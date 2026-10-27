"""Opt-in M2.0 Configuration and Pricing investigations.

Fixed original/candidate checks remain authoritative. This module offers no
SQL, substitutions, repricing, approval or free-text claims. Hosted transport
is separately gated in m20_groq; the default entrypoint remains offline-only.
The short LangGraph continuation checkpoints each AI result in the original
graph without altering its six deterministic results or comparator.
"""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from time import monotonic
from typing import Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from .fulfillment_tools import _json
from .graph_state import pinned_from_state
from .hybrid_pack import _canonical
from .hybrid_send_reservation import exclusive_owner
from .live_models import ProviderError
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import complete, entries, reserve
from .tool_permissions import AuthorizationDenied, TrustedToolScope


VERSION = "m20-ai-investigation-v1"
MAX_TURNS = 3
MAX_INSPECTIONS = 2
MAX_RECORDS = 25
MAX_MODEL_INPUT_BYTES = 4096
MAX_MODEL_OUTPUT_BYTES = 8192
MAX_OBSERVATION_BYTES = 16384
TOOLS = {"configuration": "inspect_configuration_line",
         "pricing": "inspect_pricing_line"}
_HOSTED_CAPABILITY = object()
HOSTED_REPORTED_TOKEN_STOP = 24000


class M20Model(Protocol):
    provider: str
    model: str
    offline_only: bool

    def next_action(self, input: "M20Input", observations: tuple[dict, ...]) -> dict: ...


class M20Input(TypedDict):
    version: str
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    specialist: Literal["configuration", "pricing"]
    line_ids: list[str]
    fixed_execution: str
    fixed_finding: str
    permitted_tool: str
    max_inspections: int


class M20Claim(TypedDict):
    ref: str
    field: str
    value: str | int | bool | None


class M20AIResult(TypedDict):
    version: str
    producer_type: Literal["AI"]
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    specialist: Literal["configuration", "pricing"]
    execution: Literal["completed", "skipped", "abstained", "error"]
    reason: str | None
    validated_claims: list[M20Claim]
    uncertainty_reasons: list[str]
    provider: str
    model: str
    prompt_version: str
    model_turns: int
    tool_calls: int


class M20State(TypedDict, total=False):
    current: str


def _identity(context, specialist):
    return {"assessment_id": context.assessment_id,
            "phase1c_run_id": str(context.phase1c_run_id),
            "subject_id": context.original_deal_id,
            "bundle_sha256": context.bundle_sha256,
            "source_input_digest": context.source_input_digest,
            "specialist": specialist}


def _source_records(pool, state, specialist, line_id):
    """Only selected Phase 1C facts and scoped fixed findings; no recomputation."""
    line = next((row for row in pool["lines"] if row["deal_line_id"] == line_id), None)
    if line is None:
        raise AuthorizationDenied("Line outside sealed original")
    if specialist == "configuration":
        product = {k: _json(line[k]) for k in ("product_id", "catalog_version", "is_active",
            "is_sellable", "fulfillment_mode", "configuration_json", "attributes_json")}
        records = [{"ref": "product:" + str(line["product_id"]), "fields": product}]
        fixed = state["specialist_results"]["configuration"]["payload"]
        for row in fixed["compatibility"]:
            source = next((rule for rule in pool["compatibility"] if rule[
                "compatibility_rule_id"] == row["compatibility_rule_id"]), None)
            if source and source.get("source_product_id") in (None, line["product_id"]):
                records.append({"ref": "compatibility_rule:" + str(row["compatibility_rule_id"]),
                    "fields": {"rule_id": str(row["compatibility_rule_id"]), "status": row["status"],
                               "severity": row["severity"], "rule_type": source["rule_type"]}})
        for bom in pool["bom"]:
            if bom["finished_product_id"] == line["product_id"] and bom[
                    "configuration_signature_json"] == line["configuration_json"]:
                records.append({"ref": "bom:" + str(bom["bom_id"]),
                    "fields": {"bom_id": str(bom["bom_id"]),
                               "finished_product_id": line["product_id"],
                               "status": bom["status"]}})
    else:
        fact = next(x for x in pool["facts"]["lines"] if x["line_id"] == line_id)
        fields = {k: _json(line[k]) for k in ("product_id", "quoted_unit_price",
                                                  "list_price", "standard_cost", "quantity")}
        fields.update({"line_id": line_id, "currency_code": pool["deal"]["currency_code"],
                       "fixed_discount_pct": _json(fact["discount_pct"]),
                       "fixed_margin_pct": _json(fact["margin_pct"])})
        records = [{"ref": "pricing_line:" + line_id, "fields": fields}]
        for hit in state["specialist_results"]["pricing"]["payload"]["rule_hits"]:
            if len(pool["lines"]) != 1 and hit.get("line_id") != line_id:
                continue  # A deal-level hit cannot be attributed to an arbitrary line.
            rule_id = hit.get("rule_id")
            rule = next((row for row in pool["rules"]["pricing_rules"] if row[
                "pricing_rule_id"] == rule_id), None)
            if rule is not None:
                records.append({"ref": "pricing_rule:" + str(rule_id),
                    "fields": {"rule_id": str(rule_id), "rule_type": rule["rule_type"],
                               "severity": hit["severity"]}})
    if len(records) > MAX_RECORDS or len(_canonical(records).encode()) > MAX_OBSERVATION_BYTES:
        raise EvidenceMismatch("M2.0 source projection exceeds record ceiling")
    return records


def _inspect(original, config, adapter, specialist, line_id, ordinal):
    state = original.get_state(config).values
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    context = pinned.context
    scope = TrustedToolScope(context, specialist, context.original_deal_id,
        pool["deal"]["customer_id"], frozenset(str(x["deal_line_id"]) for x in pool["lines"]),
        frozenset())
    tool = TOOLS[specialist]
    args = {"line_id": line_id}
    identity = {**_identity(context, specialist), "customer_id": pool["deal"]["customer_id"],
                "permission_version": scope.permission_version,
                "allowed_lines": sorted(scope.line_ids), "allowed_sources": []}
    call_id = sha256(f"{VERSION}:{context.assessment_id}:{specialist}:{ordinal}".encode()).hexdigest()
    try:
        scope.check(tool=tool, context=context, subject_id=context.original_deal_id,
                    customer_id=pool["deal"]["customer_id"], line_id=line_id)
        allowed = True
    except AuthorizationDenied:
        allowed = False
    event, prior = reserve(original, config, context.assessment_id,
                           context.bundle_sha256, call_id, tool, args, identity)
    if event == "budget_exhausted":
        raise EvidenceMismatch("M2.0 shared tool-call ceiling reached")
    if prior is not None:
        if prior["status"] == "completed":
            return prior["result"]
        raise EvidenceMismatch("M2.0 tool result uncertain; never rerun")
    if not allowed:
        result = {"version": VERSION, "tool": tool, "execution": "authorization_denied",
                  "records": [], "returned_refs": []}
    else:
        records = _source_records(pool, state, specialist, line_id)
        result = {"version": VERSION, "tool": tool, "execution": "completed",
                  "records": records, "returned_refs": [r["ref"] for r in records]}
    complete(original, config, context.assessment_id, context.bundle_sha256, call_id, result)
    return result


def _validate_claims(action, observations, specialist):
    if (set(action) != {"kind", "claims", "uncertainty_reasons"}
            or not isinstance(action["claims"], list) or not 1 <= len(action["claims"]) <= 6
            or not isinstance(action["uncertainty_reasons"], list)
            or len(action["uncertainty_reasons"]) > 5
            or any(type(x) is not str or len(x) > 128 for x in action["uncertainty_reasons"])):
        raise ValueError("m20_invalid_finding")
    exposed = {row["ref"]: row["fields"] for observation in observations
               if observation["execution"] == "completed" for row in observation["records"]
               if row["ref"] in observation["returned_refs"]}
    prefix = ("product:", "compatibility_rule:", "bom:") if specialist == "configuration" else (
        "pricing_line:", "pricing_rule:")
    claims = []
    for claim in action["claims"]:
        if (not isinstance(claim, dict) or set(claim) != {"ref", "field", "value"}
                or type(claim["ref"]) is not str or not claim["ref"].startswith(prefix)
                or type(claim["field"]) is not str or claim["field"] not in exposed.get(claim["ref"], {})
                or type(claim["value"]) not in (str, int, bool, type(None))
                or type(claim["value"]) is not type(exposed[claim["ref"]][claim["field"]])
                or claim["value"] != exposed[claim["ref"]][claim["field"]]):
            raise ValueError("m20_unsupported_claim")
        claims.append(dict(claim))
    return claims


def _one(original, config, adapter, specialist, model, *, hosted=False):
    state = original.get_state(config).values
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    context = pinned.context
    identity = _identity(context, specialist)
    fixed = state["specialist_results"]
    previous = state.get("m20_ai_results", {})
    if specialist in previous:
        if ({k: previous[specialist].get(k) for k in identity} != identity
                or previous[specialist].get("model") != model.model
                or previous[specialist].get("provider") != model.provider
                or previous[specialist].get("prompt_version") != VERSION
                or previous[specialist].get("version") != VERSION):
            raise EvidenceMismatch("M2.0 completed AI identity changed")
        if hosted and previous[specialist]["execution"] == "error":
            raise EvidenceMismatch("M2.0 hosted error cannot resume sends")
        return
    if (specialist == "pricing" and "configuration" not in previous):
        raise EvidenceMismatch("M2.0 Configuration AI prerequisite missing")
    if (specialist == "pricing" and (fixed["configuration"]["finding"] != "confirmed"
            or fixed["pricing"]["execution"] != "completed")):
        result = {**identity, "version": VERSION, "producer_type": "AI", "execution": "skipped",
                  "reason": "configuration_or_fixed_pricing_unavailable", "validated_claims": [],
                  "uncertainty_reasons": [], "model": model.model, "provider": model.provider,
                  "prompt_version": VERSION, "model_turns": 0,
                  "tool_calls": 0}
        original.update_state(config, {"m20_ai_results": {**previous, specialist: result}},
                              as_node="finish")
        return
    if fixed[specialist]["execution"] != "completed":
        result = {**identity, "version": VERSION, "producer_type": "AI", "execution": "skipped",
                  "reason": "fixed_specialist_unavailable", "validated_claims": [],
                  "uncertainty_reasons": [], "model": model.model, "provider": model.provider,
                  "prompt_version": VERSION, "model_turns": 0,
                  "tool_calls": 0}
        original.update_state(config, {"m20_ai_results": {**previous, specialist: result}},
                              as_node="finish")
        return
    input = {**identity, "version": VERSION, "line_ids": [str(x["deal_line_id"]) for x in pool["lines"]],
             "fixed_execution": fixed[specialist]["execution"],
             "fixed_finding": fixed[specialist]["finding"],
             "permitted_tool": TOOLS[specialist], "max_inspections": MAX_INSPECTIONS}
    if len(_canonical(input).encode()) > MAX_MODEL_INPUT_BYTES:
        raise EvidenceMismatch("M2.0 model input exceeds ceiling")
    observations = []
    status, reason, claims, uncertainty = "error", "model_failure", [], []
    turns = 0
    try:
        for ordinal in range(MAX_TURNS):
            attempts = list(original.get_state(config).values.get("m20_model_attempts", []))
            if hosted and len([item for item in attempts if item["status"] == "reserved"]) >= 6:
                raise EvidenceMismatch("M2.0 hosted aggregate request budget exhausted")
            if hosted and original.get_state(config).values["m20_hosted_base_tokens"] + sum(
                    item["usage"]["prompt_tokens"] + item["usage"]["completion_tokens"]
                    for item in attempts if item["status"] == "returned") >= HOSTED_REPORTED_TOKEN_STOP:
                raise EvidenceMismatch("M2.0 hosted reported token stop reached")
            request_digest = None
            if hosted:
                completed = [event["result"] for event in entries(original, config,
                    context.assessment_id, context.bundle_sha256) if event.get("status") == "completed"
                    and event.get("identity", {}).get("specialist") == specialist
                    and event.get("identity", {}).get("source_input_digest") == context.source_input_digest
                    and event.get("identity", {}).get("subject_id") == context.original_deal_id
                    and event.get("tool") == TOOLS[specialist]]
                prior_calls = [item["tool_call"] for item in attempts
                    if item.get("specialist") == specialist and item["status"] == "returned"
                    and item.get("action_kind") == "inspect" and "tool_call" in item]
                if (len(prior_calls) != len(observations) or any(observation not in completed
                        for observation in observations)):
                    raise EvidenceMismatch("M2.0 hosted tool exchange differs from completed ledger")
                model.previous_calls = tuple(prior_calls)
                request = model.prepare_request(input, tuple(observations))
                request_digest = sha256(_canonical(request).encode()).hexdigest()
                model.pending_request_digest = request_digest
            marker = {**identity, "version": VERSION, "ordinal": ordinal, "model": model.model,
                      "provider": model.provider, "prompt_version": VERSION,
                      **({"request_sha256": request_digest} if hosted else {})}
            if any(all(item.get(k) == v for k, v in marker.items()) for item in attempts):
                raise EvidenceMismatch("M2.0 prior model attempt uncertain; never resend")
            original.update_state(config, {"m20_model_attempts": [*attempts,
                {**marker, "status": "reserved"}]}, as_node="finish")
            turns += 1
            started = monotonic()
            action = model.next_action(deepcopy(input), deepcopy(tuple(observations)))
            if len(_canonical(action).encode()) > MAX_MODEL_OUTPUT_BYTES:
                raise ValueError("m20_model_output_oversize")
            # Only bounded, primitive audit metadata survives. Model text is not published.
            attempts = list(original.get_state(config).values["m20_model_attempts"])
            original.update_state(config, {"m20_model_attempts": [*attempts,
                {**marker, "status": "returned", "action_kind": action.get("kind") if isinstance(
                    action, dict) and action.get("kind") in ("inspect", "finding", "abstain") else "invalid",
                     "elapsed_ms": max(0, round((monotonic() - started) * 1000)),
                     "cost_usd": None,
                     **({"tool_call": dict(model.last_tool_call)} if hosted and
                        model.last_tool_call is not None else {}),
                     "usage": dict(model.last_usage) if hosted else None}]},
                as_node="finish")
            if hosted and original.get_state(config).values["m20_hosted_base_tokens"] + sum(
                    item["usage"]["prompt_tokens"] + item["usage"]["completion_tokens"]
                    for item in original.get_state(config).values["m20_model_attempts"]
                    if item["status"] == "returned") >= HOSTED_REPORTED_TOKEN_STOP:
                raise EvidenceMismatch("M2.0 hosted reported token stop reached")
            if not isinstance(action, dict):
                raise ValueError("m20_malformed_action")
            if action.get("kind") == "inspect":
                if (set(action) != {"kind", "tool", "line_id"}
                        or action["tool"] != TOOLS[specialist]
                        or type(action["line_id"]) is not str
                        or len(observations) >= MAX_INSPECTIONS):
                    raise ValueError("m20_invalid_inspection")
                result = _inspect(original, config, adapter, specialist, action["line_id"],
                                  len(observations))
                if result["execution"] != "completed":
                    raise ValueError("m20_inspection_denied")
                observations.append(result)
            elif action["kind"] == "finding":
                completed = [event["result"] for event in entries(original, config,
                    context.assessment_id, context.bundle_sha256) if event.get("status") == "completed"
                    and event.get("identity", {}).get("specialist") == specialist
                    and event.get("identity", {}).get("source_input_digest") == context.source_input_digest
                    and event.get("identity", {}).get("subject_id") == context.original_deal_id
                    and event.get("tool") == TOOLS[specialist]]
                if len(completed) < len(observations) or any(observation not in completed
                        for observation in observations):
                    raise EvidenceMismatch("M2.0 returned evidence ledger differs")
                claims = _validate_claims(action, observations, specialist)
                uncertainty = list(action["uncertainty_reasons"])
                status, reason = "completed", None
                break
            elif action["kind"] == "abstain":
                if set(action) != {"kind", "reason_code"} or action["reason_code"] not in (
                        "insufficient_evidence", "model_uncertainty", "unsupported_capability"):
                    raise ValueError("m20_invalid_abstention")
                status, reason = "abstained", action["reason_code"]
                break
            else:
                raise ValueError("m20_malformed_action")
        else:
            reason = "model_turn_budget_exhausted"
    except (ValueError, EvidenceMismatch, TypeError, KeyError) as exc:
        status, reason = "error", ("evidence_identity" if isinstance(exc, EvidenceMismatch)
                                    else "invalid_model_or_tool_output")
    except ProviderError as exc:
        status, reason = "error", "provider_" + exc.code
    except Exception:
        status, reason = "error", "model_or_tool_failure"
    latest = original.get_state(config).values
    result = {**identity, "version": VERSION, "producer_type": "AI", "execution": status,
              "reason": reason, "validated_claims": claims, "uncertainty_reasons": uncertainty,
              "model": model.model, "provider": model.provider, "prompt_version": VERSION,
              "model_turns": turns, "tool_calls": len(observations)}
    original.update_state(config, {"m20_ai_results": {**latest.get("m20_ai_results", {}),
                            specialist: result}, "trace": [*latest["trace"],
                            "m20_" + specialist + ":" + status]}, as_node="finish")
    if hosted and status == "error":
        # Do not send Pricing after an uncertain, malformed or denied hosted turn.
        from .candidate_graph import original_only_package
        fresh = original.get_state(config).values
        package = fresh.get("reviewer_package") or original_only_package(fresh)
        if "m20_ai" not in package:
            original.update_state(config, {"reviewer_package": {**package,
                "m20_ai": {
                    "version": VERSION, "execution": "stopped",
                    "specialist": specialist, "reason": reason,
                    "validated_claims": [], "authority": "Fixed original; human review only"}}},
                as_node="finish")
        raise EvidenceMismatch("M2.0 hosted investigation stopped; fixed review retained")


def build_m20_graph(original, config, adapter, models, *, _capability=None):
    """Configuration then Pricing AI; offline unless given the private hosted gate."""
    if set(models) != set(TOOLS):
        raise ValueError("M2.0 two specialist models required")
    hosted = _capability is _HOSTED_CAPABILITY
    if _capability is not None and not hosted:
        raise ValueError("M2.0 hosted capability not available")
    if hosted:
        from .m20_groq import GroqM20Model
        if any(type(models[name]) is not GroqM20Model or models[name].specialist != name
               for name in TOOLS):
            raise ValueError("M2.0 hosted models must be exact scoped Groq adapters")
    elif any(getattr(m, "provider", None) != "offline_double"
            or getattr(m, "offline_only", False) is not True or not isinstance(
                getattr(m, "model", None), str) for m in models.values()):
        raise ValueError("M2.0 offline models required")
    builder = StateGraph(M20State)
    def node(name):
        def run(_):
            _one(original, config, adapter, name, models[name], hosted=hosted)
            return {"current": name}
        return run
    for name in TOOLS:
        builder.add_node(name, node(name))
    def handoff(_):
        state = original.get_state(config).values
        pinned = pinned_from_state(state)
        adapter.validate_pinned_context(pinned)
        results = state.get("m20_ai_results", {})
        if set(results) != set(TOOLS):
            raise EvidenceMismatch("M2.0 missing specialist contribution")
        review = {"version": VERSION, "assessment_id": pinned.context.assessment_id,
            "subject_id": pinned.context.original_deal_id,
            "source_input_digest": pinned.context.source_input_digest,
            "fixed_review_status": state["review_status"],
            "fixed_route_withheld": state["specialist_results"]["approval_routing"][
                "payload"]["route_withheld"],
            "authority": "AI observations only; original fixed findings and human approval govern",
            "specialists": {name: {"execution": results[name]["execution"],
                "reason": results[name]["reason"],
                "validated_claims": results[name]["validated_claims"]} for name in TOOLS}}
        if state.get("m20_review") not in (None, review):
            raise EvidenceMismatch("M2.0 reviewer projection changed")
        if state.get("reviewer_package") is not None and "m20_ai" in state[
                "reviewer_package"] and state["reviewer_package"]["m20_ai"] != review:
            raise EvidenceMismatch("M2.0 reviewer package differs from validated claims")
        if state.get("m20_review") is None:
            from .candidate_graph import original_only_package
            package = state.get("reviewer_package") or original_only_package(state)
            if "m20_ai" in package:
                raise EvidenceMismatch("M2.0 reviewer output already exists")
            update = {"m20_review": review,
                      "reviewer_package": {**package, "m20_ai": review}}
            original.update_state(config, update, as_node="finish")
        return {"current": "handoff"}
    builder.add_node("handoff", handoff)
    builder.add_edge(START, "configuration")
    builder.add_edge("configuration", "pricing")
    builder.add_edge("pricing", "handoff")
    builder.add_edge("handoff", END)
    return builder.compile()


def run_m20_offline(original, config, adapter, models):
    """Post-original graph continuation; never invokes a provider or a candidate."""
    _validate_m20_start(original, config, adapter)
    build_m20_graph(original, config, adapter, models).invoke({"current": "start"})
    return original.get_state(config).values


def _validate_m20_start(original, config, adapter):
    snapshot = original.get_state(config)
    state = snapshot.values
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    if (snapshot.next or state.get("stop_reason") or set(state.get("specialist_results", {})) != {
            "configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"}):
        raise EvidenceMismatch("M2.0 requires completed fixed original")


def run_m20_evaluation(original, config, adapter, models, *, authorized=False,
                       reservation_dir: Path | None = None, prior_reported_tokens: int = 0):
    """Explicit opt-in hosted gate; no credentials or network before authorization."""
    if authorized is not True:
        raise ValueError("M2.0 hosted evaluation not authorized")
    if (type(prior_reported_tokens) is not int or not 0 <= prior_reported_tokens <
            HOSTED_REPORTED_TOKEN_STOP):
        raise ValueError("M2.0 hosted reported token gate reached")
    from .m20_groq import GroqM20Model
    from .groq_preflight import credential_shape
    import os
    if (set(models) != set(TOOLS) or any(type(models[name]) is not GroqM20Model
            or models[name].specialist != name for name in TOOLS)):
        raise ValueError("M2.0 hosted evaluation requires scoped Groq models")
    if credential_shape(os.environ.get("GROQ_API_KEY")) != "credential_shape_ok":
        raise ValueError("M2.0 Groq credential unavailable")
    _validate_m20_start(original, config, adapter)
    if not isinstance(reservation_dir, Path):
        raise ValueError("M2.0 durable hosted owner directory required")
    state = original.get_state(config).values
    with exclusive_owner(reservation_dir, state["assessment_id"]):
        owner = {"path": str(reservation_dir.resolve(strict=True)),
                 "device": reservation_dir.stat().st_dev,
                 "inode": reservation_dir.stat().st_ino}
        fresh = original.get_state(config).values
        if (fresh.get("m20_hosted_owner") not in (None, owner)
                or fresh.get("m20_hosted_owner") is None and (
                    fresh.get("m20_model_attempts") or fresh.get("m20_ai_results"))
                or fresh.get("m20_hosted_base_tokens") not in (None, prior_reported_tokens)):
            raise EvidenceMismatch("M2.0 hosted owner or attempt identity changed")
        if fresh.get("m20_hosted_owner") is None:
            original.update_state(config, {"m20_hosted_owner": owner,
                                         "m20_hosted_base_tokens": prior_reported_tokens},
                                  as_node="finish")
        if any(item.get("provider") != "groq" for item in original.get_state(config).values.get(
                "m20_ai_results", {}).values()):
            raise EvidenceMismatch("M2.0 cannot switch a completed offline assessment to hosted")
        if any(item.get("provider") != "groq" for item in original.get_state(config).values.get(
                "m20_model_attempts", [])):
            raise EvidenceMismatch("M2.0 cannot adopt offline model attempts")
        build_m20_graph(original, config, adapter, models,
                        _capability=_HOSTED_CAPABILITY).invoke({"current": "start"})
    return original.get_state(config).values
