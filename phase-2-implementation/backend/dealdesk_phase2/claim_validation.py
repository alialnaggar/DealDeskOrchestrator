"""M1.6 evidence-scoped AI claims. Phase 1C retains all business-rule authority.

This module checks equality to *returned* tool records or sealed fixed findings.
It never derives stock availability, supplier arrival dates, or candidate validity.
"""
from typing import Literal, TypedDict

from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import entries, was_returned


CLAIM_TYPES = frozenset((
    "source_observation", "fixed_finding_reference", "conditional_possibility",
    "evidence_gap", "candidate_idea",
))
SOURCE_FIELDS = {
    "supplier_offer": frozenset(("supplier_id", "lead_days_min", "lead_days_mode",
                                  "lead_days_max", "valid_from", "valid_to")),
    "inventory": frozenset(("quantity_on_hand", "quantity_allocated", "snapshot_at",
                            "location_id")),
    "inbound_supply": frozenset(("quantity", "quantity_allocated", "expected_date",
                                 "status", "confirmed_at", "valid_until")),
    "shipping_lane": frozenset(("transit_workdays", "cutoff_local_time",
                                "dispatch_weekdays_json")),
}
COMMON = frozenset(("type", "line_id", "source_ref", "field", "value", "scope",
                    "gap_code", "idea_code", "delivery_slices"))
MAX_CLAIMS = 8


class FulfillmentClaimV2(TypedDict):
    type: Literal["source_observation", "fixed_finding_reference",
                  "conditional_possibility", "evidence_gap", "candidate_idea"]
    line_id: str
    source_ref: str
    field: str
    value: str
    scope: str
    gap_code: str
    idea_code: str
    delivery_slices: list[dict]


class ClaimAssessmentV2(TypedDict):
    accepted_claims: list[dict]
    rejected_claims: list[dict]
    review_summary: list[str]
    disposition: str
    raw_model_notes: dict


def _visible_records(graph, config, input):
    ledger = entries(graph, config, input.assessment_id, input.bundle_sha256)
    visible = []
    for event in ledger:
        identity = event.get("identity", {})
        if event.get("status") != "completed" or event.get("args", {}).get("line_id") != input.line_id:
            continue
        if (identity.get("phase1c_run_id") != input.phase1c_run_id
                or identity.get("subject_id") != input.subject_id
                or identity.get("source_input_digest") != input.source_input_digest
                or identity.get("specialist") != "fulfillment"):
            raise EvidenceMismatch("Tool ledger identity differs from Fulfillment input")
        result = event["result"]
        for record in result.get("records", []):
            visible.append((record, result))
    return visible, ledger


def _record_for(ref, input, graph, config, visible):
    if not isinstance(ref, str) or ":" not in ref:
        raise EvidenceMismatch("Claim source reference is malformed")
    category, source_id = ref.split(":", 1)
    if not was_returned(graph, config, input.assessment_id, input.bundle_sha256,
                        category, source_id, input.line_id):
        raise EvidenceMismatch("Claim cites a record not returned by authorized tools")
    for record, _ in visible:
        if record["category"] == category and str(record["id"]) == source_id:
            return record
    raise EvidenceMismatch("Returned source record has no matching ledger body")


def _line_results(ledger, line_id):
    return [item["result"] for item in ledger if item.get("status") == "completed"
            and item.get("args", {}).get("line_id") == line_id
            and item.get("result", {}).get("execution") == "completed"]


def _assess_one(claim, input, graph, config, visible, ledger):
    if not isinstance(claim, dict) or set(claim) != COMMON:
        return None, "malformed_claim"
    if claim["line_id"] != input.line_id:
        raise EvidenceMismatch("Claim line identity differs")
    if claim["type"] not in CLAIM_TYPES or any(
            not isinstance(claim[key], str) for key in COMMON - {"delivery_slices"}):
        return None, "malformed_claim"
    if not isinstance(claim["delivery_slices"], list):
        return None, "malformed_claim"

    kind = claim["type"]
    ref = claim["source_ref"]
    if ref:
        source = _record_for(ref, input, graph, config, visible)
    else:
        source = None
    if kind == "source_observation":
        if not source:
            return None, "source_reference_required"
        allowed = SOURCE_FIELDS.get(source["category"], frozenset())
        field = claim["field"]
        if field not in allowed or field not in source["fields"]:
            return None, "source_field_not_exposed"
        if str(source["fields"][field]) != claim["value"]:
            return None, "source_value_mismatch"
        return {"type": kind, "line_id": input.line_id, "source_ref": ref,
                "field": field, "value": claim["value"], "status": "directly_observed"}, None

    if kind == "fixed_finding_reference":
        if ref:
            return None, "fixed_finding_must_use_pinned_input"
        actual = {"fulfillment_status": input.fixed_fulfillment_status,
                  "quantity_by_requested_date": input.quantity_by_requested_date}
        field = claim["field"]
        if field not in actual or claim["value"] != actual[field]:
            return None, "fixed_finding_mismatch"
        return {"type": kind, "line_id": input.line_id, "field": field,
                "value": actual[field], "status": "fixed_phase1c_finding"}, None

    if kind == "conditional_possibility":
        if not source or source["category"] != "supplier_offer":
            return None, "returned_supplier_offer_required"
        if claim["value"] != "supplier_confirmation_required" or claim["delivery_slices"]:
            return None, "conditional_claim_cannot_set_delivery"
        return {"type": kind, "line_id": input.line_id, "source_ref": ref,
                "condition": "supplier_confirmation_required",
                "status": "conditional_uncommitted"}, None

    if kind == "evidence_gap":
        if claim["scope"] != "returned_records":
            return None, "absence_scope_must_be_returned_records"
        results = _line_results(ledger, input.line_id)
        gap = claim["gap_code"]
        if gap == "no_eligible_evidence_in_selected_pool":
            if not any(r.get("tool") == "inspect_line_supply"
                       and r.get("evidence") == "no_eligible_evidence"
                       and not r.get("more_in_sealed_pool") for r in results):
                return None, "selected_pool_absence_not_established"
        elif gap == "supplier_confirmation_not_returned":
            if not source or source["category"] != "supplier_offer":
                return None, "returned_supplier_offer_required"
            if not any(r.get("tool") == "inspect_line_supply"
                       and r.get("evidence") == "insufficient_or_conditional"
                       and not r.get("more_in_sealed_pool") for r in results):
                return None, "confirmation_gap_not_established"
        else:
            return None, "unsupported_gap_code"
        return {"type": kind, "line_id": input.line_id, "source_ref": ref,
                "scope": "returned_records", "gap_code": gap,
                "status": "bounded_evidence_gap"}, None

    if kind == "candidate_idea":
        if claim["idea_code"] != "ask_supplier_for_later_option":
            return None, "unsupported_idea_code"
        if not source or source["category"] != "supplier_offer":
            return None, "returned_supplier_offer_required"
        if claim["delivery_slices"]:
            # The pinned Phase 1C interface cannot verify a dated mixed or
            # supplier-offer candidate. Keep original claim in rejected_claims.
            return {"type": kind, "line_id": input.line_id, "source_ref": ref,
                    "idea_code": claim["idea_code"], "status": "downgraded_nonactionable",
                    "original_dated_claim_rejected": True}, "candidate_date_unverified"
        return {"type": kind, "line_id": input.line_id, "source_ref": ref,
                "idea_code": claim["idea_code"], "status": "unverified_nonactionable"}, None
    return None, "unsupported_claim_type"


def _render(claim):
    kind = claim["type"]
    if kind == "source_observation":
        return (f"Observed in returned {claim['source_ref']}: "
                f"{claim['field']}={claim['value']}. This does not establish delivery.")
    if kind == "fixed_finding_reference":
        return f"Phase 1C fixed {claim['field']}: {claim['value']}."
    if kind == "conditional_possibility":
        return (f"Conditional possibility from {claim['source_ref']}: supplier "
                "confirmation is required; no delivery commitment is established.")
    if kind == "evidence_gap":
        return (f"Bounded evidence gap ({claim['gap_code']}) in returned records; "
                "this does not establish the absence of other supply.")
    return (f"Nonactionable, unverified planning idea from {claim['source_ref']}: "
            "ask the supplier about a later option. No date or commitment is verified."
            + (" Original dated claim was rejected." if
               claim.get("original_dated_claim_rejected") else ""))


def assess_claims(payload, input, graph, config):
    """Validate v2 without exposing raw model prose as authoritative output."""
    if not isinstance(payload, dict) or set(payload) != {"line_id", "claims", "notes"}:
        raise ValueError("Malformed typed claim payload")
    if payload["line_id"] != input.line_id:
        raise EvidenceMismatch("Typed payload line identity differs")
    claims, notes = payload["claims"], payload["notes"]
    if not isinstance(claims, list) or len(claims) > MAX_CLAIMS or not isinstance(notes, dict):
        raise ValueError("Typed claims exceed bounded contract")
    visible, ledger = _visible_records(graph, config, input)
    accepted, rejected = [], []
    for index, claim in enumerate(claims):
        valid, reason = _assess_one(claim, input, graph, config, visible, ledger)
        if reason:
            rejected.append({"claim_index": index, "original_claim": claim, "reason": reason})
        if valid:
            accepted.append(valid)
    summary = [_render(claim) for claim in accepted]
    return {"accepted_claims": accepted, "rejected_claims": rejected,
            "review_summary": summary,
            "disposition": ("downgraded" if any(c.get("status") == "downgraded_nonactionable"
                                               for c in accepted) else
                            "validated" if accepted else "no_validated_claims"),
            "raw_model_notes": notes}
