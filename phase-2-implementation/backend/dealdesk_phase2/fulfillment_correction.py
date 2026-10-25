"""Narrow, audit-only classification of a rejected V3 binding hypothesis.

Only the pinned Phase 1C verifier decides whether any delivery is supportable.
The temporary quantity projection below is used to identify a format mistake;
it is never submitted as a corrected model proposal or shown to reviewers.
"""

from copy import deepcopy
from decimal import Decimal, InvalidOperation

from .candidate_contract import construct_candidate, validate_from_graph
from .phase1c_adapter import EvidenceMismatch


CORRECTION_VERSION = "fulfillment-correction-v1"
# Verified at Phase 1C 90c0bc8e285ee69262c7db826b786096a77ad004,
# phase1c_candidate.review_partial_delivery. Unknown/changed errors are terminal.
TOTAL_ERROR = "Delivery slices must account for every original unit and line"


def _format_only(raw, input, graph, config):
    if (not isinstance(raw, dict) or set(raw) != {"schema_version", "kind", "payload"}
            or raw.get("schema_version") != "3" or raw.get("kind") != "binding_proposal"):
        return None
    payload = raw["payload"]
    if not isinstance(payload, dict) or set(payload) != {"line_id", "delivery_slices", "tradeoff_code"}:
        return None
    slices = payload["delivery_slices"]
    if not isinstance(slices, list) or len(slices) != 2:
        return None
    projection = deepcopy(payload)
    bad = []
    for index, item in enumerate(slices):
        if not isinstance(item, dict) or not isinstance(item.get("quantity"), str):
            return None
        text = item["quantity"]
        if text.isascii() and text.isdecimal() and int(text) > 0:
            continue
        # Only a positive, integral ASCII decimal *format* is eligible. Do not
        # round fractions, coerce JSON numbers or accept signed/Unicode digits.
        head, separator, fractional = text.partition(".")
        if (not separator or not head.isascii() or not head.isdecimal()
                or int(head) <= 0 or not fractional or set(fractional) != {"0"}):
            return None
        projection["delivery_slices"][index]["quantity"] = head
        bad.append(index)
    if not bad:
        return None
    # A different structural, identity or source-access error is not a
    # correctable formatting failure, even when a quantity also looks wrong.
    try:
        validate_from_graph(projection, input, graph, config)
    except (ValueError, EvidenceMismatch, TypeError, KeyError):
        return None
    return {"code": "quantity_format", "field_paths": [
        f"payload.delivery_slices[{index}].quantity" for index in bad]}


def classify(raw, input, graph, config, adapter, connection_factory, *, validation_error=None):
    """Return safe correction metadata or None; never certify a candidate."""
    if validation_error is not None:
        if (type(validation_error) is not ValueError
                or str(validation_error) != "Binding slice requires a positive whole quantity"):
            return None
        return _format_only(raw, input, graph, config)
    if (not isinstance(raw, dict) or raw.get("schema_version") != "3"
            or raw.get("kind") != "binding_proposal"):
        return None
    # The caller has already validated the untrusted contribution in full.
    from .graph_state import pinned_from_state
    pinned = pinned_from_state(graph.get_state(config).values)
    adapter.validate_pinned_context(pinned)
    proposal = validate_from_graph(raw["payload"], input, graph, config)
    candidate, _ = construct_candidate(adapter, pinned, proposal)
    try:
        adapter.verify_candidate(connection_factory, pinned, candidate)
    except ValueError as exc:
        if type(exc) is not ValueError or str(exc) != TOTAL_ERROR:
            return None
        try:
            original = Decimal(input.requested_quantity)
            quantities = [int(item["quantity"]) for item in proposal["delivery_slices"]]
        except (InvalidOperation, ValueError, TypeError, KeyError):
            return None
        if not original.is_finite() or sum(quantities) == original:
            return None
        return {"code": "quantity_sum_mismatch", "field_paths": [
            "payload.delivery_slices"], "requested_quantity": str(original),
            "proposed_total": str(sum(quantities))}
    return None


def feedback(failure: dict, input, returned_refs: list[str], remaining_turns: int) -> dict:
    """No raw exception, source rows, answer key or suggested replacement slice."""
    explanation = ("Binding quantities must be positive whole-unit ASCII digit strings; "
                   "decimal-formatted text is not accepted." if failure["code"] == "quantity_format"
                   else "Delivery slice quantities must sum to the original requested quantity; "
                        "the fixed verifier rejected the first proposal's total.")
    return {"version": CORRECTION_VERSION, "failed_stage": (
        "proposal_shape" if failure["code"] == "quantity_format" else "fixed_candidate_check"),
        "constraint_code": failure["code"], "field_paths": failure["field_paths"],
        "constraint_explanation": explanation,
        "requested_quantity": failure.get("requested_quantity"),
        "proposed_total": failure.get("proposed_total"),
        "permitted_returned_refs": sorted(set(returned_refs))[:25],
        "remaining_model_turns": remaining_turns,
        "instruction": "Submit a new unverified V3 binding proposal or abstain; no source, date, or quantity is supplied as a correction."}
