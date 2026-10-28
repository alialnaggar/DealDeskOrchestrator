"""M2.1 original-only Credit/Policy/Routing evidence investigations.

Only pinned evidence and six fixed results decide business outcomes. The
default path is offline; a distinct exact-manifest and owner gate may use
Groq for synthetic original-only observations. No candidate edit, credit
computation, policy engine or approval operation is available here.
"""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from time import monotonic
from typing import Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from .fulfillment_tools import _json
from .graph_state import pinned_from_state
from .hybrid_pack import _canonical
from .hybrid_send_reservation import attempt_path, exclusive_owner, verify_receipt
from .live_models import GROQ_MODEL, ProviderError
from .m21_prompts import PROMPT_VERSION
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import complete, entries, reserve
from .tool_permissions import AuthorizationDenied, PERMISSION_VERSION, TrustedToolScope


VERSION = "m21-original-evidence-v1"
TOOLS = {"credit": "inspect_customer_credit_evidence",
         "policy": "inspect_fixed_policy_hits",
         "approval_routing": "inspect_fixed_route"}
MAX_RECORDS = 25
MAX_OBSERVATION_BYTES = 16384
MAX_ACTION_BYTES = 8192
_HOSTED_CAPABILITY = object()
HOSTED_REPORTED_TOKEN_STOP = 24000


class M21Model(Protocol):
    provider: str
    model: str
    offline_only: bool

    def next_action(self, input: "M21Input", observations: tuple[dict, ...]) -> dict: ...


class M21Input(TypedDict):
    version: str
    prompt_version: str
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    customer_id: str
    policy_set_code: str
    data_snapshot_ref: str
    as_of_at: str
    specialist: Literal["credit", "policy", "approval_routing"]
    fixed_execution: str
    fixed_finding: str
    permitted_tool: str


class M21Claim(TypedDict):
    ref: str
    field: str
    value: str | int | bool | None


class M21Result(TypedDict):
    version: str
    producer_type: Literal["AI"]
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    specialist: Literal["credit", "policy", "approval_routing"]
    execution: Literal["completed", "abstained", "skipped", "error"]
    reason: str | None
    validated_claims: list[M21Claim]
    model: str
    provider: str
    prompt_version: str
    model_turns: int
    tool_calls: int


class M21State(TypedDict, total=False):
    current: str


def _identity(context, specialist):
    return {"assessment_id": context.assessment_id,
            "phase1c_run_id": str(context.phase1c_run_id),
            "subject_id": context.original_deal_id,
            "bundle_sha256": context.bundle_sha256,
            "source_input_digest": context.source_input_digest,
            "specialist": specialist}


def _project(pool, state, context, specialist):
    """Selected, already pinned rows only; never infer a missing rule or role."""
    fixed = state["specialist_results"][specialist]["payload"]
    customer = pool["deal"]["customer_id"]
    if specialist == "credit":
        profile = pool["credit"]
        if (profile["customer_id"] != customer or
                profile["commitments_as_of_at"] > context.as_of_at):
            raise EvidenceMismatch("M2.1 credit customer or as-of mismatch")
        fields = ("credit_limit", "unbilled_committed_amount", "commitments_as_of_at",
                  "commitment_evidence_ref", "credit_status", "risk_rating",
                  "last_review_date", "next_review_date")
        records = [{"ref": "credit_profile:" + customer,
            "fields": {**_json({k: profile[k] for k in fields}),
                       "fixed_commitments_fresh": fixed["commitments_fresh"]}}]
        for row in pool["receivables"]:
            if row["customer_id"] != customer or row["as_of_date"] > context.as_of_at.date():
                raise EvidenceMismatch("M2.1 receivable customer or date mismatch")
            records.append({"ref": "receivable:" + str(row["receivable_id"]),
                "fields": _json({k: row[k] for k in ("invoice_number", "as_of_date",
                    "due_date", "outstanding_amount", "status")})})
        for row in pool["payments"]:
            if row["customer_id"] != customer or row["paid_date"] > context.as_of_at.date():
                raise EvidenceMismatch("M2.1 payment customer or date mismatch")
            records.append({"ref": "payment:" + str(row["payment_id"]),
                "fields": _json({k: row[k] for k in ("invoice_number", "paid_date",
                    "paid_amount", "due_date")})})
    elif specialist == "policy":
        if fixed["per_rule_prerequisites_available"] is not False:
            raise EvidenceMismatch("M2.1 policy prerequisite interface changed")
        selected = {r["policy_rule_id"]: r for r in pool["rules"]["policy_rules"]}
        records = []
        for hit in fixed["rule_hits"]:
            rule = selected.get(hit["rule_id"])
            if (rule is None or rule["policy_set_code"] != context.policy_set_code
                    or rule["severity"] != hit["severity"]):
                raise EvidenceMismatch("M2.1 fixed policy hit not in selected rules")
            records.append({"ref": "policy_rule:" + str(hit["rule_id"]),
                "fields": _json({"rule_id": hit["rule_id"],
                    "policy_area": rule["policy_area"], "severity": hit["severity"],
                    "required_action": rule["required_action"], "scope": hit["scope"],
                    "scope_type": rule["scope_type"],
                    "scope_value": rule["scope_value"]})})
    elif specialist == "approval_routing":
        withheld = fixed["route_withheld"]
        if withheld is not True and withheld is not False:
            raise EvidenceMismatch("M2.1 invalid fixed route status")
        if withheld and (fixed["roles_available_from_fixed_interface"] is not False
                        or fixed["required_roles"]):
            raise EvidenceMismatch("M2.1 withheld route cannot expose roles")
        if not withheld and fixed["roles_available_from_fixed_interface"] is not True:
            raise EvidenceMismatch("M2.1 route roles unavailable from fixed interface")
        records = [{"ref": "fixed_route:" + context.original_deal_id,
            "fields": {"route_withheld": withheld,
                       "roles_available_from_fixed_interface": fixed[
                           "roles_available_from_fixed_interface"]}}]
        if not withheld:
            selected = {r["approval_rule_id"]: r for r in pool["rules"]["approval_rules"]}
            for role in fixed["required_roles"]:
                rule = selected.get(role["rule_id"])
                if (rule is None or rule["policy_set_code"] != context.policy_set_code
                        or role["role"] != rule["required_role"]
                        or role["sequence"] != rule["approval_sequence"]):
                    raise EvidenceMismatch("M2.1 fixed route role not in selected rules")
                records.append({"ref": "fixed_role:" + str(role["rule_id"]),
                    "fields": _json({"rule_id": role["rule_id"], "role": role["role"],
                                     "sequence": role["sequence"]})})
    else:
        raise AuthorizationDenied("M2.1 specialist outside scope")
    if len(records) > MAX_RECORDS or len(_canonical(records).encode()) > MAX_OBSERVATION_BYTES:
        raise EvidenceMismatch("M2.1 evidence projection exceeds limits")
    if len({row["ref"] for row in records}) != len(records):
        raise EvidenceMismatch("M2.1 duplicate evidence reference")
    return records


def _inspect(original, config, adapter, specialist):
    state = original.get_state(config).values
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    context = pinned.context
    customer = pool["deal"]["customer_id"]
    scope = TrustedToolScope(context, specialist, context.original_deal_id,
                             customer, frozenset(), frozenset())
    tool = TOOLS[specialist]
    scope.check(tool=tool, context=context, subject_id=context.original_deal_id,
                customer_id=customer)
    identity = {**_identity(context, specialist), "customer_id": customer,
                "permission_version": scope.permission_version,
                "allowed_lines": [], "allowed_sources": []}
    args = {"subject_id": context.original_deal_id}
    call_id = sha256(f"{VERSION}:{context.assessment_id}:{specialist}:0".encode()).hexdigest()
    event, prior = reserve(original, config, context.assessment_id,
                            context.bundle_sha256, call_id, tool, args, identity)
    if event == "budget_exhausted":
        raise EvidenceMismatch("M2.1 shared tool budget exhausted")
    if prior is not None:
        if prior["status"] == "completed":
            return prior["result"]
        raise EvidenceMismatch("M2.1 uncertain tool receipt; never replay")
    records = _project(pool, state, context, specialist)
    result = {"version": VERSION, "tool": tool, "execution": "completed",
              "records": records, "returned_refs": [r["ref"] for r in records]}
    complete(original, config, context.assessment_id, context.bundle_sha256, call_id, result)
    return result


def _claims(action, observations):
    if (set(action) != {"kind", "claims"} or action["kind"] != "finding"
            or type(action["claims"]) is not list
            or not 1 <= len(action["claims"]) <= 6):
        raise ValueError("M2.1 invalid finding contract")
    exposed = {row["ref"]: row["fields"] for observation in observations
               for row in observation["records"] if observation["execution"] == "completed"
               and row["ref"] in observation["returned_refs"]}
    validated = []
    for claim in action["claims"]:
        if (type(claim) is not dict or set(claim) != {"ref", "field", "value"}
                or type(claim["ref"]) is not str or type(claim["field"]) is not str
                or claim["field"] not in exposed.get(claim["ref"], {})
                or type(claim["value"]) not in (str, int, bool, type(None))
                or type(claim["value"]) is not type(exposed[claim["ref"]][claim["field"]])
                or claim["value"] != exposed[claim["ref"]][claim["field"]]):
            raise ValueError("M2.1 unsupported evidence claim")
        validated.append(dict(claim))
    return validated


def _one(original, config, adapter, specialist, model, *, hosted=False):
    state = original.get_state(config).values
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    context = pinned.context
    identity = _identity(context, specialist)
    previous = state.get("m21_ai_results", {})
    if specialist in previous:
        if any(previous[specialist].get(k) != v for k, v in identity.items()) or (
                previous[specialist].get("model") != model.model or
                previous[specialist].get("provider") != model.provider or
                previous[specialist].get("version") != VERSION or
                previous[specialist].get("prompt_version") not in (
                    (PROMPT_VERSION,) if hosted else (PROMPT_VERSION, VERSION))):
            raise EvidenceMismatch("M2.1 completed AI identity changed")
        if hosted and previous[specialist]["execution"] == "error":
            raise EvidenceMismatch("M2.1 hosted error terminal; no further sends")
        return
    fixed = state["specialist_results"]
    unavailable = (fixed[specialist]["execution"] != "completed" or
        specialist == "credit" and fixed["pricing"]["execution"] != "completed" or
        specialist == "approval_routing" and any(fixed[key]["execution"] != "completed"
            for key in ("configuration", "pricing", "fulfillment", "credit", "policy")))
    status, reason, claims, turns, observations = "skipped", "fixed_prerequisite_unavailable", [], 0, []
    if not unavailable:
        input = {**identity, "version": VERSION, "prompt_version": PROMPT_VERSION,
            "customer_id": pool["deal"]["customer_id"],
            "policy_set_code": context.policy_set_code,
            "data_snapshot_ref": context.data_snapshot_ref,
            "as_of_at": context.as_of_at.isoformat(), "fixed_execution": fixed[specialist]["execution"],
            "fixed_finding": fixed[specialist]["finding"], "permitted_tool": TOOLS[specialist]}
        if len(_canonical(input).encode()) > 4096:
            raise EvidenceMismatch("M2.1 input exceeds limit")
        status, reason = "error", "model_or_tool_failure"
        try:
            for ordinal in range(2):
                attempts = original.get_state(config).values.get("m21_model_attempts", [])
                marker = {**identity, "version": VERSION, "ordinal": ordinal,
                          "model": model.model, "provider": model.provider,
                          "prompt_version": PROMPT_VERSION}
                # Old offline checkpoints used VERSION as their prompt label.
                # A label upgrade must never cause an uncertain send to replay.
                prior = [item for item in attempts if all(item.get(k) == v for k, v in identity.items())
                         and item.get("ordinal") == ordinal and item.get("status") == "reserved"]
                returned = [item for item in attempts if all(item.get(k) == v for k, v in identity.items())
                            and item.get("ordinal") == ordinal and item.get("status") == "returned"]
                if prior and (not hosted or len(prior) != 1 or len(returned) != 1
                        or prior[0].get("request_sha256") != returned[0].get("request_sha256")):
                    raise EvidenceMismatch("M2.1 uncertain model attempt; never resend")
                if returned:
                    if not hosted or len(prior) != 1 or ordinal != 0 or len(returned) != 1 or returned[0].get(
                            "action_kind") != "inspect" or returned[0].get("prompt_version") != PROMPT_VERSION:
                        raise EvidenceMismatch("M2.1 unrecorded terminal exchange; never replay")
                    completed = [e["result"] for e in entries(original, config,
                        context.assessment_id, context.bundle_sha256) if e["status"] == "completed"
                        and e["tool"] == TOOLS[specialist] and e["identity"].get(
                            "specialist") == specialist and e["identity"].get(
                            "source_input_digest") == context.source_input_digest]
                    if (len(completed) != 1 or not returned[0].get("tool_call")
                            or returned[0].get("model") != model.model
                            or returned[0].get("request_sha256") is None):
                        raise EvidenceMismatch("M2.1 incomplete returned inspection; never replay")
                    observations.append(completed[0])
                    continue
                if hosted:
                    if len([x for x in attempts if x.get("status") == "reserved"]) >= 6:
                        raise EvidenceMismatch("M2.1 case/campaign POST ceiling")
                    used = sum(x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"]
                        for x in attempts if x.get("status") == "returned" and x.get("usage"))
                    if used >= HOSTED_REPORTED_TOKEN_STOP:
                        raise EvidenceMismatch("M2.1 reported token stop")
                    completed = [e["result"] for e in entries(original, config,
                        context.assessment_id, context.bundle_sha256) if e["status"] == "completed"
                        and e["tool"] == TOOLS[specialist] and e["identity"].get(
                            "specialist") == specialist and e["identity"].get(
                            "source_input_digest") == context.source_input_digest]
                    calls = [x["tool_call"] for x in attempts if x.get("specialist") == specialist
                        and x.get("status") == "returned" and x.get("action_kind") == "inspect"
                        and "tool_call" in x]
                    if len(calls) != len(observations) or any(o not in completed for o in observations):
                        raise EvidenceMismatch("M2.1 hosted completed ledger differs")
                    model.previous_calls = tuple(calls)
                    body = model.prepare_request(input, tuple(observations))
                    request_digest = sha256(_canonical(body).encode()).hexdigest()
                    model.pending_request_digest = request_digest
                    model._attempt_ordinal = tuple(TOOLS).index(specialist) * 2 + ordinal
                    marker["request_sha256"] = request_digest
                original.update_state(config, {"m21_model_attempts": [*attempts,
                    {**marker, "status": "reserved"}]}, as_node="finish")
                started = monotonic()
                turns += 1
                action = model.next_action(deepcopy(input), deepcopy(tuple(observations)))
                if type(action) is not dict or len(_canonical(action).encode()) > MAX_ACTION_BYTES:
                    raise ValueError("M2.1 malformed or oversized action")
                attempts = original.get_state(config).values["m21_model_attempts"]
                original.update_state(config, {"m21_model_attempts": [*attempts,
                    {**marker, "status": "returned", "action_kind": action.get("kind") if
                        action.get("kind") in ("inspect", "finding", "abstain") else "invalid",
                     "elapsed_ms": max(0, round((monotonic() - started) * 1000)),
                      "cost_usd": None, "usage": dict(model.last_usage) if hosted and
                      model.last_usage is not None else None,
                      **({"tool_call": dict(model.last_tool_call)} if hosted and
                          model.last_tool_call is not None else {})}]}, as_node="finish")
                if hosted and (model.last_usage is None or sum(
                    x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"]
                    for x in original.get_state(config).values["m21_model_attempts"]
                    if x.get("status") == "returned" and x.get("usage")) >= HOSTED_REPORTED_TOKEN_STOP):
                    raise EvidenceMismatch("M2.1 reported token stop")
                if action.get("kind") == "inspect":
                    if (set(action) != {"kind", "tool", "subject_id"} or ordinal != 0
                            or action["tool"] != TOOLS[specialist]
                            or action["subject_id"] != context.original_deal_id):
                        raise ValueError("M2.1 inspection identity or budget invalid")
                    observations.append(_inspect(original, config, adapter, specialist))
                elif action.get("kind") == "finding":
                    if not observations:
                        raise ValueError("M2.1 finding without authorized inspection")
                    completed = [e["result"] for e in entries(original, config,
                        context.assessment_id, context.bundle_sha256) if e["status"] == "completed"
                        and e["tool"] == TOOLS[specialist]
                        and e["identity"].get("source_input_digest") == context.source_input_digest
                        and e["identity"].get("subject_id") == context.original_deal_id]
                    if any(observation not in completed for observation in observations):
                        raise EvidenceMismatch("M2.1 evidence ledger changed")
                    claims = _claims(action, observations)
                    status, reason = "completed", None
                    break
                elif action.get("kind") == "abstain":
                    if (set(action) != {"kind", "reason_code"} or action["reason_code"] not in
                            ("insufficient_evidence", "model_uncertainty", "unsupported_capability")):
                        raise ValueError("M2.1 invalid abstention")
                    status, reason = "abstained", action["reason_code"]
                    break
                else:
                    raise ValueError("M2.1 unsupported model action")
            else:
                status, reason = "abstained", "model_turn_budget_exhausted"
        except ProviderError as exc:
            status, reason = "error", "provider_" + exc.code
        except EvidenceMismatch as exc:
            status, reason = "error", ("unrecorded_terminal_exchange" if str(exc).startswith(
                ("M2.1 unrecorded terminal", "M2.1 incomplete returned inspection"))
                else "evidence_identity_or_budget")
        except (ValueError, TypeError, KeyError, AuthorizationDenied):
            status, reason = "error", "invalid_model_or_evidence"
        except Exception:
            status, reason = "error", "model_or_tool_failure"
    latest = original.get_state(config).values
    result = {**identity, "version": VERSION, "producer_type": "AI",
        "execution": status, "reason": reason, "validated_claims": claims,
        "model": model.model, "provider": model.provider, "prompt_version": PROMPT_VERSION,
        "model_turns": turns, "tool_calls": len(observations)}
    original.update_state(config, {"m21_ai_results": {**latest.get("m21_ai_results", {}),
        specialist: result}, "trace": [*latest["trace"], "m21_" + specialist + ":" + status]},
        as_node="finish")
    if hosted and status == "error":
        from .candidate_graph import original_only_package
        fresh = original.get_state(config).values
        package = fresh.get("reviewer_package") or original_only_package(fresh)
        if "m21_ai" not in package:
            original.update_state(config, {"reviewer_package": {**package, "m21_ai": {
                "version": VERSION, "execution": "stopped", "specialist": specialist,
                "reason": reason, "validated_claims": [],
                "authority": "Fixed original; human review only"}}}, as_node="finish")
        raise EvidenceMismatch("M2.1 hosted investigation terminal; fixed original retained")


def build_m21_graph(original, config, adapter, models, *, _capability=None,
                    diagnostic_credit_only=False):
    """Sequential LangGraph post-original continuation; offline doubles only."""
    hosted = _capability is _HOSTED_CAPABILITY
    if _capability is not None and not hosted:
        raise ValueError("M2.1 private hosted capability only")
    if diagnostic_credit_only and not hosted:
        raise ValueError("M2.1 credit diagnostic needs hosted capability")
    if set(models) != set(TOOLS):
        raise ValueError("M2.1 three specialist models required")
    if hosted:
        from .m21_groq_contract import GroqM21Model
        if any(type(models[name]) is not GroqM21Model or models[name].specialist != name
               for name in TOOLS):
            raise ValueError("M2.1 exact scoped Groq adapters required")
    elif any(getattr(model, "provider", None) != "offline_double"
            or getattr(model, "offline_only", None) is not True
            or not isinstance(getattr(model, "model", None), str) for model in models.values()):
        raise ValueError("M2.1 offline, three specialist models required")
    builder = StateGraph(M21State)
    for name in TOOLS:
        def node(_, name=name):
            _one(original, config, adapter, name, models[name], hosted=hosted)
            return {"current": name}
        builder.add_node(name, node)
    def handoff(_):
        state = original.get_state(config).values
        pinned = pinned_from_state(state)
        adapter.validate_pinned_context(pinned)
        results = state.get("m21_ai_results", {})
        if set(results) != set(TOOLS):
            raise EvidenceMismatch("M2.1 incomplete AI contributions")
        review = {"version": VERSION, "assessment_id": pinned.context.assessment_id,
            "subject_id": pinned.context.original_deal_id,
            "source_input_digest": pinned.context.source_input_digest,
            "fixed_review_status": state["review_status"],
            "fixed_route_withheld": state["specialist_results"]["approval_routing"][
                "payload"]["route_withheld"],
            "authority": "AI observations only; fixed results and human approval govern",
            "specialists": {name: {"execution": result["execution"], "reason": result["reason"],
                "validated_claims": result["validated_claims"]} for name, result in results.items()}}
        if state.get("m21_review") not in (None, review):
            raise EvidenceMismatch("M2.1 review projection changed")
        if state.get("reviewer_package") is not None and "m21_ai" in state["reviewer_package"]:
            if state["reviewer_package"]["m21_ai"] != review:
                raise EvidenceMismatch("M2.1 reviewer package changed")
        if state.get("m21_review") is None:
            from .candidate_graph import original_only_package
            package = state.get("reviewer_package") or original_only_package(state)
            original.update_state(config, {"m21_review": review,
                "reviewer_package": {**package, "m21_ai": review}}, as_node="finish")
        return {"current": "handoff"}
    builder.add_node("handoff", handoff)
    builder.add_edge(START, "credit")
    if diagnostic_credit_only:
        # Never project an incomplete three-specialist AI reviewer package.
        builder.add_edge("credit", END)
    else:
        builder.add_edge("credit", "policy")
        builder.add_edge("policy", "approval_routing")
        builder.add_edge("approval_routing", "handoff")
        builder.add_edge("handoff", END)
    return builder.compile()


def run_m21_offline(original, config, adapter, models):
    _validate_m21_start(original, config, adapter)
    build_m21_graph(original, config, adapter, models).invoke({"current": "start"})
    return original.get_state(config).values


def _validate_m21_start(original, config, adapter):
    snapshot = original.get_state(config)
    state = snapshot.values
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    if (snapshot.next or state.get("stop_reason") or state.get("candidate_status") != "not_started"
            or set(state.get("specialist_results", {})) != {
                "configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"}):
        raise EvidenceMismatch("M2.1 needs completed fixed original, no candidate")
    return pinned


def run_m21_evaluation(original, config, adapter, models, *, manifest: dict,
                       approved_manifest_sha256: str, authorized: bool = False,
                       owner_dir: Path | None = None, free_tier_billing_disabled: bool = False):
    """One synthetic original per explicit approved manifest; no multi-case campaign.

    Proposal manifests cannot call the provider. The caller supplies an exact
    approved digest and account/billing confirmation for a *new* one-case
    manifest, plus an empty owner-only directory and original checkpoint.
    """
    if authorized is not True or free_tier_billing_disabled is not True:
        raise ValueError("M2.1 explicit hosted/account authorization required")
    from .groq_preflight import credential_shape
    from .m21_groq_contract import GroqM21Model, PROMPT_VERSION, WIRE_VERSION
    from .phase1c_adapter import PHASE1C_COMMIT
    diagnostic_credit_only = (type(manifest) is dict and
        manifest.get("version") == "m21-credit-http400-diagnostic-v1")
    if (type(manifest) is not dict or type(approved_manifest_sha256) is not str
            or sha256(_canonical(manifest).encode()).hexdigest() != approved_manifest_sha256
            or manifest.get("status") != ("authorization_candidate" if
                diagnostic_credit_only else "authorized_one_case")
            or manifest.get("version") != ("m21-credit-http400-diagnostic-v1" if
                diagnostic_credit_only else "m21-week3-proposal-v1")
            or manifest.get("phase1c_pin") != PHASE1C_COMMIT
            or manifest.get("model") != GROQ_MODEL or manifest.get("provider") != "groq"
            or manifest.get("credential_env_selection") != "GROQ_SECONDARY_API_KEY"
            or manifest.get("prompt_version") != PROMPT_VERSION
            or manifest.get("wire_version") != WIRE_VERSION
            or manifest.get("m21_contract_version") != VERSION
            or manifest.get("permission_version") != PERMISSION_VERSION
            or manifest.get("allowed_tools") != ({"credit": TOOLS["credit"]} if
                diagnostic_credit_only else TOOLS)
            or manifest.get("maximum_inspections_per_specialist") != 1
            or manifest.get("order") != (["credit"] if diagnostic_credit_only else list(TOOLS))
            or type(manifest.get("maximum_posts_per_specialist")) is not int
            or manifest["maximum_posts_per_specialist"] != 2
            or any(type(manifest.get(k)) is not int or manifest[k] != v for k, v in {
                "maximum_posts_per_case": 2 if diagnostic_credit_only else 6,
                "maximum_posts_total": 2 if diagnostic_credit_only else 6,
                "maximum_completion_tokens_per_post": 512,
                "maximum_serialized_request_bytes_per_post": 8192,
                "reported_total_token_post_send_stop": HOSTED_REPORTED_TOKEN_STOP,
                "maximum_inspections_per_specialist": 1}.items())
            or type(manifest.get("cases")) is not list or len(manifest["cases"]) != 1
            or type(manifest["cases"][0]) is not dict
            or set(manifest["cases"][0]) != {"case_id", "assessment_id", "run_id",
                "bundle_sha256", "source_input_digest", "as_of_at", "data_snapshot_ref"}
            or manifest["cases"][0]["case_id"] not in (
                "B01", "B05", "N03", "CREDIT-LIMIT", "POLICY-CLAUSE")
            or type(manifest.get("execution_context")) is not dict
            or set(manifest["execution_context"]) != {"fixture_database",
                "checkpoint_database", "owner_directory", "fresh_databases_required"}
            or manifest["execution_context"]["fresh_databases_required"] is not True
            or any(type(manifest["execution_context"][key]) is not str
                or not manifest["execution_context"][key]
                for key in ("fixture_database", "checkpoint_database", "owner_directory"))
            or not Path(manifest["execution_context"]["owner_directory"]).is_absolute()
            or os.path.normpath(manifest["execution_context"]["owner_directory"])
                != manifest["execution_context"]["owner_directory"]
            or manifest["execution_context"]["fixture_database"] == manifest[
                "execution_context"]["checkpoint_database"]
            or set(manifest) != {"version", "status", "phase1c_pin", "model", "provider",
                "credential_env_selection", "prompt_version", "wire_version", "order",
                "m21_contract_version", "permission_version", "allowed_tools",
                "maximum_inspections_per_specialist",
                "maximum_posts_per_specialist", "maximum_posts_per_case",
                "maximum_posts_total", "maximum_completion_tokens_per_post",
                "maximum_serialized_request_bytes_per_post", "reported_total_token_post_send_stop",
                "cases", "execution_context"}):
        raise ValueError("M2.1 hosted manifest or approved hash mismatch")
    if (set(models) != set(TOOLS) or any(type(models[name]) is not GroqM21Model
            or models[name].specialist != name for name in TOOLS)):
        raise ValueError("M2.1 exact scoped Groq models required")
    # Do not call a metadata endpoint; validate only local shape and owner.
    credential = os.environ.get("GROQ_SECONDARY_API_KEY")
    if credential_shape(credential) != "credential_shape_ok":
        raise ValueError("M2.1 secondary credential unavailable")
    pinned = _validate_m21_start(original, config, adapter)
    case = manifest["cases"][0]
    ctx = pinned.context
    if (ctx.assessment_id != case["assessment_id"]
            or str(ctx.phase1c_run_id) != case["run_id"]
            or ctx.bundle_sha256 != case["bundle_sha256"]
            or ctx.source_input_digest != case["source_input_digest"]
            or ctx.as_of_at.isoformat() != case["as_of_at"]
            or ctx.data_snapshot_ref != case["data_snapshot_ref"]
            or config.get("configurable", {}).get("thread_id") != ctx.assessment_id
            or pinned.context.original_deal_id != {
                "B01": "M18-D-B01", "B05": "M18-D-B05", "N03": "M18-D-N03",
                "CREDIT-LIMIT": "CONFLICT-DEAL-13",
                "POLICY-CLAUSE": "CONFLICT-DEAL-15"}[case["case_id"]]):
        raise EvidenceMismatch("M2.1 hosted pinned source/manifest identity changed")
    if (not isinstance(owner_dir, Path) or not owner_dir.is_absolute()
            or owner_dir.is_symlink() or str(owner_dir) != manifest[
                "execution_context"]["owner_directory"]
            or str(owner_dir.resolve(strict=True)) != manifest[
                "execution_context"]["owner_directory"]):
        raise ValueError("M2.1 durable owner directory required")
    with exclusive_owner(owner_dir, ctx.assessment_id):
        # Approval is an owner-supplied, private durable artifact, NOT derived
        # from caller's boolean/hash or created by this runner. A proposal
        # cannot be converted to authorization by passing `authorized=True`.
        approval_path = owner_dir / "m21-approved-manifest.json"
        try:
            fd = os.open(approval_path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                st = os.fstat(fd)
                if (st.st_uid != os.geteuid() or st.st_nlink != 1 or st.st_mode & 0o077
                        or st.st_size > 2048 or st.st_size == 0):
                    raise ValueError("M2.1 invalid owner approval file")
                with os.fdopen(os.dup(fd), "r", encoding="utf-8") as stream:
                    approval = json.load(stream)
            finally:
                os.close(fd)
        except (OSError, UnicodeError, ValueError, TypeError):
            raise EvidenceMismatch("M2.1 owner approval record unavailable") from None
        if (type(approval) is not dict or approval != {
                "assessment_id": ctx.assessment_id,
                "approved_manifest_sha256": approved_manifest_sha256,
                "credential_env_selection": "GROQ_SECONDARY_API_KEY",
                "billing_disabled_confirmed": True}):
            raise EvidenceMismatch("M2.1 owner approval identity mismatch")
        owner = {"manifest_sha256": approved_manifest_sha256,
            "path": str(owner_dir.resolve(strict=True)), "device": owner_dir.stat().st_dev,
            "inode": owner_dir.stat().st_ino, "credential_env_selection": "GROQ_SECONDARY_API_KEY",
            "credential_sha256": sha256(credential.encode()).hexdigest()}
        fresh = original.get_state(config).values
        if (fresh.get("m21_hosted_owner") not in (None, owner)
                or fresh.get("m21_hosted_owner") is None and (fresh.get("m21_model_attempts")
                    or fresh.get("m21_ai_results"))
                or any(x.get("provider") != "groq" or diagnostic_credit_only and
                    x.get("specialist") != "credit" for x in fresh.get("m21_model_attempts", []))
                or any(x.get("provider") != "groq" for x in fresh.get("m21_ai_results", {}).values())
                or any(x.get("execution") == "error" for x in fresh.get(
                    "m21_ai_results", {}).values())):
            raise EvidenceMismatch("M2.1 hosted owner, attempts or terminal state changed")
        if fresh.get("m21_hosted_owner") is None:
            original.update_state(config, {"m21_hosted_owner": owner}, as_node="finish")
        receipts = fresh.get("m21_model_attempts", [])
        allowed_paths = {approval_path.name, attempt_path(owner_dir,
            assessment_id=ctx.assessment_id, start_digest="0" * 64, stage="owner",
            ordinal=0).name}
        allowed_paths.update(attempt_path(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=approved_manifest_sha256, stage="decision",
            ordinal=tuple(TOOLS).index(x["specialist"]) * 2 + x["ordinal"]).name
            for x in receipts if x.get("status") == "reserved" and x.get("specialist") in TOOLS
            and type(x.get("ordinal")) is int and x["ordinal"] in (0, 1))
        if any(entry.name not in allowed_paths for entry in owner_dir.iterdir()):
            raise EvidenceMismatch("M2.1 owner directory contains unknown campaign receipt")
        if len([x for x in receipts if x.get("status") == "reserved"]) > (
                2 if diagnostic_credit_only else 6):
            raise EvidenceMismatch("M2.1 hosted campaign reservation ceiling changed")
        for item in receipts:
            if item.get("status") != "returned":
                continue
            reserved = [x for x in receipts if x.get("status") == "reserved"
                and x.get("specialist") == item.get("specialist")
                and x.get("ordinal") == item.get("ordinal")
                and x.get("request_sha256") == item.get("request_sha256")]
            if (len(reserved) != 1 or item.get("specialist") not in TOOLS
                    or item.get("ordinal") not in (0, 1)
                    or type(item.get("usage")) is not dict
                    or any(type(item["usage"].get(k)) is not int or item["usage"][k] < 0
                           for k in ("prompt_tokens", "completion_tokens"))):
                raise EvidenceMismatch("M2.1 hosted returned attempt provenance changed")
            path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                start_digest=approved_manifest_sha256, stage="decision",
                ordinal=tuple(TOOLS).index(item["specialist"]) * 2 + item["ordinal"])
            try:
                valid = verify_receipt(path, start_digest=approved_manifest_sha256,
                    stage="decision", ordinal=tuple(TOOLS).index(item["specialist"]) * 2 +
                    item["ordinal"], request_digest=item["request_sha256"])
            except OSError:
                raise EvidenceMismatch("M2.1 hosted receipt unavailable") from None
            if not valid:
                raise EvidenceMismatch("M2.1 hosted returned receipt missing")
        try:
            for model in models.values():
                model._send_capability = _HOSTED_CAPABILITY
                model._owner_directory = owner_dir
                model._assessment_id = ctx.assessment_id
                model._manifest_hash = approved_manifest_sha256
                model._credential_sha256 = owner["credential_sha256"]
                model._capture_http_error = diagnostic_credit_only
            build_m21_graph(original, config, adapter, models,
                _capability=_HOSTED_CAPABILITY,
                diagnostic_credit_only=diagnostic_credit_only).invoke({"current": "start"})
        finally:
            for model in models.values():
                model._send_capability = None
                model._owner_directory = None
                model._capture_http_error = False
                model._assessment_id = None
                model._manifest_hash = None
                model._credential_sha256 = None
                model._attempt_ordinal = None
                model.pending_request_digest = None
    return original.get_state(config).values
