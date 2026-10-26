"""Opt-in sealed Fulfillment pack; offline-only until exclusive ownership exists.

The sole prefetch runs through the existing permissioned, counted tool facade.
An interrupted reservation stays terminal; it never triggers a second tool read.
"""

from dataclasses import asdict
from hashlib import sha256
import json

from .fulfillment_agent import FulfillmentInputV1, eligible_line, restricted_input
from .fulfillment_tools import FulfillmentTools
from .graph_state import pinned_from_state
from .hybrid_contracts import PACK_VERSION, HybridContractError
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT
from .tool_ledger import entries
from .tool_permissions import (MAX_CALLS, MAX_RECORDS, FORWARD_DAYS,
                               PERMISSION_VERSION, TrustedToolScope)


START_VERSION = "hybrid-investigation-start-v1"
_CATEGORIES = frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane"))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def prepare_pack(graph, config: dict, adapter, *, provider: str, model: str,
                 policy_version: str) -> tuple[dict, object]:
    """Freeze the original input, then perform exactly one counted supply read.

    No sender is exposed here. Caller must still implement durable exclusive
    model-send ownership before using any of this on a live hybrid assessment.
    """
    if not all(isinstance(x, str) and x and len(x) <= 128 for x in (
            provider, model, policy_version)):
        raise HybridContractError("invalid_hybrid_policy")
    state = graph.get_state(config).values
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    selected, reason = eligible_line(state, pool)
    if selected is None:
        raise HybridContractError("ineligible:" + reason)
    context = pinned.context
    used = sum(bool(x.get("counted")) for x in entries(
        graph, config, context.assessment_id, context.bundle_sha256))
    input = restricted_input(context, pool, selected, MAX_CALLS - used)
    existing = state.get("hybrid_investigation_start")
    if existing is not None:
        if (not isinstance(existing, dict) or existing.get("version") != START_VERSION
                or existing.get("phase1c_commit") != PHASE1C_COMMIT
                or existing.get("start_sha256") != sha256(_canonical({
                    key: val for key, val in existing.items() if key != "start_sha256"
                }).encode()).hexdigest()
                or any(existing.get(k) != v for k, v in {
                    "assessment_id": context.assessment_id,
                    "phase1c_run_id": str(context.phase1c_run_id),
                    "subject_id": context.original_deal_id,
                    "bundle_sha256": context.bundle_sha256,
                    "source_input_digest": context.source_input_digest,
                    "as_of_at": context.as_of_at.isoformat(),
                    "data_snapshot_ref": context.data_snapshot_ref,
                    "catalog_version": context.catalog_version,
                    "policy_set_code": context.policy_set_code,
                    "config_hash": context.config_hash,
                    "fixed_decision_sha256": state.get("fixed_decision_sha256"),
                    "permission_version": PERMISSION_VERSION,
                    "line_id": input.line_id, "provider": provider, "model": model,
                    "policy_version": policy_version, "pack_version": PACK_VERSION}.items())):
            raise EvidenceMismatch("Hybrid investigation start identity differs")
        fields = existing["restricted_input"]
        input = FulfillmentInputV1(**{
            **fields, "permitted_tools": tuple(fields["permitted_tools"])})
        if state.get("hybrid_evidence_pack") is not None:
            pack = state["hybrid_evidence_pack"]
            call_id = sha256((existing["start_sha256"] +
                              ":trusted_prefetch:inspect_line_supply").encode()).hexdigest()
            completed = [event for event in entries(
                graph, config, context.assessment_id, context.bundle_sha256)
                if event.get("call_id") == call_id and event.get("status") == "completed"]
            if (not isinstance(pack, dict) or pack.get("version") != PACK_VERSION
                    or pack.get("start_sha256") != existing["start_sha256"]
                    or pack.get("tool_call_id") != call_id or len(completed) != 1
                    or completed[0].get("result") != pack.get("observation")
                    or pack.get("pack_sha256") != sha256(_canonical({
                        k: v for k, v in pack.items() if k != "pack_sha256"
                    }).encode()).hexdigest()):
                raise EvidenceMismatch("Hybrid pack or completed tool provenance differs")
            return pack, input
        start_digest = existing["start_sha256"]
    else:
        if used >= MAX_CALLS:
            raise HybridContractError("tool_budget_exhausted")
        start = {"version": START_VERSION, "phase1c_commit": PHASE1C_COMMIT,
             "assessment_id": input.assessment_id, "phase1c_run_id": input.phase1c_run_id,
             "subject_id": input.subject_id, "bundle_sha256": input.bundle_sha256,
             "source_input_digest": input.source_input_digest,
             "as_of_at": context.as_of_at.isoformat(),
             "data_snapshot_ref": context.data_snapshot_ref,
             "catalog_version": context.catalog_version,
             "policy_set_code": context.policy_set_code,
             "config_hash": context.config_hash,
             "fixed_decision_sha256": state.get("fixed_decision_sha256"),
             "permission_version": PERMISSION_VERSION,
             "line_id": input.line_id, "restricted_input": asdict(input),
             "tool_calls_at_start": used, "provider": provider, "model": model,
             "policy_version": policy_version, "pack_version": PACK_VERSION}
        start_digest = sha256(_canonical(start).encode()).hexdigest()
        graph.update_state(config, {"hybrid_investigation_start": {
            **start, "start_sha256": start_digest}}, as_node="finish")
    scope = TrustedToolScope(context, "fulfillment", input.subject_id,
                             pool["deal"]["customer_id"], frozenset((input.line_id,)),
                             _CATEGORIES)
    call_id = sha256((start_digest + ":trusted_prefetch:inspect_line_supply").encode()).hexdigest()
    prior = [event for event in entries(graph, config, input.assessment_id,
             input.bundle_sha256) if event.get("call_id") == call_id]
    if prior:
        if [event.get("status") for event in prior] == ["reserved"]:
            raise HybridContractError("prefetch_outcome_uncertain")
        if [event.get("status") for event in prior] != ["reserved", "completed"]:
            raise EvidenceMismatch("Hybrid prefetch ledger differs")
        result = prior[1]["result"]
    else:
        result = FulfillmentTools(graph, config, adapter, scope).inspect_line_supply(
            call_id=call_id, line_id=input.line_id)
    if result.get("execution") != "completed":
        raise HybridContractError("prefetch_" + str(result.get("execution")))
    latest = entries(graph, config, input.assessment_id, input.bundle_sha256)
    events = [x for x in latest if x.get("call_id") == call_id and x.get("status") == "completed"]
    if (len(events) != 1 or events[0].get("returned_refs") != result.get("returned_refs")
            or not any(x.get("call_id") == call_id and x.get("status") == "reserved"
                       and x.get("counted") for x in latest)):
        raise EvidenceMismatch("Hybrid prefetch missing durable counted completion")
    exposed = {"line_id": input.line_id, "requested_quantity": input.requested_quantity,
               "requested_delivery_date": input.requested_delivery_date,
               "quantity_by_requested_date": input.quantity_by_requested_date,
               "fixed_fulfillment_status": input.fixed_fulfillment_status,
               "allow_partial_delivery": input.allow_partial_delivery,
               "destination_country_code": input.destination_country_code,
               "destination_region": input.destination_region}
    pack = {"version": PACK_VERSION, "start_sha256": start_digest,
            "origin": "trusted_prefetch", "tool_call_id": call_id,
            "model_input": exposed, "observation": result,
            "coverage": {"scope": "selected_reader_pool_only", "line_id": input.line_id,
                         "forward_days": FORWARD_DAYS, "record_limit": MAX_RECORDS,
                         "more_in_sealed_pool": result.get("more_in_sealed_pool"),
                         "evidence": result.get("evidence"), "gaps": result.get("gaps", [])}}
    pack["pack_sha256"] = sha256(_canonical(pack).encode()).hexdigest()
    graph.update_state(config, {"hybrid_evidence_pack": pack}, as_node="finish")
    return pack, input
