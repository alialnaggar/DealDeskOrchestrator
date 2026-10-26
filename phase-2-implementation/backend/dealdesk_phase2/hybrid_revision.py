"""Allowlisted hybrid revision feedback. Never manufactures a candidate.

One caller-approved, separately reserved model submission may use this small
generic feedback. The existing iterative correction path is untouched.
"""

from .fulfillment_correction import TOTAL_ERROR
from .hybrid_contracts import (HybridContractError, canonical_quantity,
                               prove_source_slices, strict_binding)
from .phase1c_adapter import EvidenceMismatch


REVISION_VERSION = "hybrid-revision-v1"


def feedback_for(raw: object, input, ledger: list[dict], *, failure: Exception,
                 already_revised: bool = False) -> dict | None:
    """Return safe feedback only when another independent error is ruled out.

    Missing binding refs, dates and quantities are deliberately NOT on D4's
    first required-field allowlist. No missing answer, proposed sum or new
    evidence enters the feedback.
    """
    if (already_revised or not isinstance(raw, dict) or raw.get("line_id") != input.line_id
            or not input.allow_partial_delivery or not isinstance(raw.get("delivery_slices"), list)
            or len(raw["delivery_slices"]) != 2):
        return None
    slices = raw["delivery_slices"]
    if any(not isinstance(sl, dict) or set(sl) != {
            "quantity", "delivery_date", "source_refs"} for sl in slices):
        return None
    missing_tradeoff = "tradeoff_code" not in raw and set(raw) == {
        "line_id", "delivery_slices"}
    if missing_tradeoff:
        if not isinstance(failure, (ValueError, HybridContractError)):
            return None
        if any(not canonical_quantity(sl["quantity"]) for sl in slices):
            return None
        try:
            prove_source_slices(raw, input, ledger)
        except (ValueError, EvidenceMismatch):
            return None
        return _feedback("required_field_missing", ["payload.tradeoff_code"],
                         "Submit a complete new proposal with the required contract fields.")
    if (isinstance(failure, HybridContractError)
            and failure.code.startswith("quantity_noncanonical:")):
        index = int(failure.code.rsplit(":", 1)[1])
        if (index not in (0, 1) or "tradeoff_code" not in raw
                or any(not canonical_quantity(sl["quantity"]) for pos, sl in
                       enumerate(slices) if pos != index)):
            return None
        # Check unchanged source/date bindings; never substitute a quantity,
        # even temporarily, to classify this failure.
        try:
            prove_source_slices(raw, input, ledger)
        except (ValueError, EvidenceMismatch):
            return None
        return _feedback("quantity_format", [f"payload.delivery_slices[{index}].quantity"],
                         "Quantity text must be a positive canonical ASCII whole-unit string.")
    if (type(failure) is ValueError and str(failure) == TOTAL_ERROR):
        try:
            strict_binding(raw, input, ledger)
            # The pinned verifier rejects totals before dated-slice analysis.
            # Only allow this feedback when unchanged source/date bindings pass
            # the conservative diagnostic; otherwise withhold revision.
            prove_source_slices(raw, input, ledger)
        except (ValueError, EvidenceMismatch):
            return None
        return _feedback("quantity_sum_mismatch", ["payload.delivery_slices"],
                         "The deterministic verifier rejected the proposal's total quantity.")
    return None


def _feedback(code: str, paths: list[str], explanation: str) -> dict:
    return {"version": REVISION_VERSION, "constraint_code": code,
            "field_paths": paths, "constraint_explanation": explanation,
            "instruction": "Submit one new complete unverified proposal or abstain; no tools."}
