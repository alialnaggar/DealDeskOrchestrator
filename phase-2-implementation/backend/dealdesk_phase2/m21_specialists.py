"""M2.1 original-only, offline Credit/Policy/Routing evidence investigations.

Only the pinned reader and six fixed results decide business outcomes. No
hosted model, candidate edit, credit computation, policy engine or approval
operation is available through this module.
"""

from copy import deepcopy
from hashlib import sha256
from time import monotonic
from typing import Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from .fulfillment_tools import _json
from .graph_state import pinned_from_state
from .hybrid_pack import _canonical
from .m21_prompts import PROMPT_VERSION
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import complete, entries, reserve
from .tool_permissions import AuthorizationDenied, TrustedToolScope


VERSION = "m21-original-evidence-v1"
TOOLS = {"credit": "inspect_customer_credit_evidence",
         "policy": "inspect_fixed_policy_hits",
         "approval_routing": "inspect_fixed_route"}
MAX_RECORDS = 25
MAX_OBSERVATION_BYTES = 16384
MAX_ACTION_BYTES = 8192


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


def _one(original, config, adapter, specialist, model):
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
                previous[specialist].get("prompt_version") not in (PROMPT_VERSION, VERSION)):
            raise EvidenceMismatch("M2.1 completed AI identity changed")
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
                if any(all(item.get(k) == v for k, v in identity.items())
                       and item.get("ordinal") == ordinal for item in attempts):
                    raise EvidenceMismatch("M2.1 uncertain model attempt; never resend")
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
                     "cost_usd": None}]}, as_node="finish")
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
        except (ValueError, TypeError, KeyError, AuthorizationDenied, EvidenceMismatch):
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


def build_m21_graph(original, config, adapter, models):
    """Sequential LangGraph post-original continuation; offline doubles only."""
    if (set(models) != set(TOOLS) or any(getattr(model, "provider", None) != "offline_double"
            or getattr(model, "offline_only", None) is not True
            or not isinstance(getattr(model, "model", None), str) for model in models.values())):
        raise ValueError("M2.1 offline, three specialist models required")
    builder = StateGraph(M21State)
    for name in TOOLS:
        def node(_, name=name):
            _one(original, config, adapter, name, models[name])
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
    builder.add_edge("credit", "policy")
    builder.add_edge("policy", "approval_routing")
    builder.add_edge("approval_routing", "handoff")
    builder.add_edge("handoff", END)
    return builder.compile()


def run_m21_offline(original, config, adapter, models):
    snapshot = original.get_state(config)
    state = snapshot.values
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    if (snapshot.next or state.get("stop_reason") or state.get("candidate_status") != "not_started"
            or set(state.get("specialist_results", {})) != {
                "configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"}):
        raise EvidenceMismatch("M2.1 needs completed fixed original, no candidate")
    build_m21_graph(original, config, adapter, models).invoke({"current": "start"})
    return original.get_state(config).values
