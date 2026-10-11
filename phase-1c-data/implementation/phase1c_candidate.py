"""Typed, side-effect-free proposal and audit boundary for the first alternative trial.

This module does not turn a proposal into a submitted deal or a checked result.
The existing reader reads deal_lines, not candidate changes in a run snapshot.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Literal
from uuid import UUID


Specialist = Literal["Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval"]
CHECKS: tuple[Specialist, ...] = (
    "Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval"
)
CHANGE_FIELDS = {
    "product_id", "quantity", "quoted_unit_price", "configuration_json",
    "fulfillment_group_code", "requested_delivery_date", "requested_activation_date",
    "terms_json.allow_partial_delivery", "terms_json.payment_terms_days",
    "terms_json.contract_clause_codes",
}


@dataclass(frozen=True)
class FieldChange:
    line_id: str | None
    field: str
    before: object
    after: object

    def __post_init__(self):
        if self.field not in CHANGE_FIELDS or self.before == self.after:
            raise ValueError("Change must name a supported field with a different value")
        if (self.field in {"requested_delivery_date", "terms_json.allow_partial_delivery",
                           "terms_json.payment_terms_days", "terms_json.contract_clause_codes"}) == (self.line_id is not None):
            raise ValueError("Deal fields have no line_id; line fields require one")


@dataclass(frozen=True)
class DeliverySlice:
    line_id: str
    quantity: int
    arrival_date: date
    evidence_ids: tuple[str, ...]
    commitment: Literal["confirmed", "conditional", "unknown"]


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    parent_deal_id: str
    parent_run_id: UUID
    proposal_kind: Literal["partial_delivery", "substitute"]
    changes: tuple[FieldChange, ...]
    customer_constraints: tuple[str, ...]
    unmet_constraints: tuple[str, ...]
    delivery_slices: tuple[DeliverySlice, ...]
    evidence_ids: tuple[str, ...]
    as_of_at: datetime
    catalog_version: str
    policy_set_code: str
    data_snapshot_ref: str
    assumptions: tuple[str, ...]
    tradeoff: str

    def __post_init__(self):
        if not self.candidate_id or not self.parent_deal_id or not self.tradeoff:
            raise ValueError("Candidate identity, parent and tradeoff are required")
        if not self.changes or len({(c.line_id, c.field) for c in self.changes}) != len(self.changes):
            raise ValueError("Candidate requires unique, explicit field changes")
        if self.as_of_at.tzinfo is None or not all((self.catalog_version, self.policy_set_code, self.data_snapshot_ref)):
            raise ValueError("Candidate needs a dated and versioned evidence context")
        if set(self.unmet_constraints) - set(self.customer_constraints):
            raise ValueError("Unmet constraints must identify submitted customer constraints")
        if not self.evidence_ids or any(not ref for ref in self.evidence_ids):
            raise ValueError("Candidate needs named evidence")
        if self.proposal_kind == "partial_delivery":
            if not self.delivery_slices or len(self.delivery_slices) < 2:
                raise ValueError("Partial delivery needs at least two dated slices")
            if any(s.quantity <= 0 or not s.line_id or not s.evidence_ids for s in self.delivery_slices):
                raise ValueError("Each slice needs positive quantity and evidence")
            if any(s.arrival_date < self.as_of_at.date() or
                   set(s.evidence_ids) - set(self.evidence_ids) for s in self.delivery_slices):
                raise ValueError("Slice date and evidence must agree with candidate context")
            if any(s.commitment != "confirmed" for s in self.delivery_slices) and not self.assumptions:
                raise ValueError("Uncommitted delivery must expose an assumption")
        elif not any(c.field == "product_id" for c in self.changes):
            raise ValueError("Substitute must change a product")


def review_partial_delivery(candidate: Candidate, *, original_quantities: dict[str, int],
                            requested_date: date, partial_allowed: bool,
                            indivisible_groups: tuple[frozenset[str], ...] = ()) -> dict:
    """Check proposal shape only; source selection and commercial reruns remain open."""
    if candidate.proposal_kind != "partial_delivery" or not partial_allowed:
        raise ValueError("Customer has not permitted this partial delivery")
    by_line: dict[str, int] = {}
    for item in candidate.delivery_slices:
        by_line[item.line_id] = by_line.get(item.line_id, 0) + item.quantity
    if by_line != original_quantities:
        raise ValueError("Delivery slices must account for every original unit and line")
    for group in indivisible_groups:
        dates = {item.arrival_date for item in candidate.delivery_slices if item.line_id in group}
        if len(dates) > 1:
            raise ValueError("Indivisible configuration group split across dates")
    if not any(item.arrival_date > requested_date for item in candidate.delivery_slices):
        raise ValueError("Shortage alternative needs an explicitly later slice")
    return {
        "candidate_id": candidate.candidate_id,
        "parent_run_id": str(candidate.parent_run_id),
        "required_reruns": list(CHECKS),
        "proposal_check": "shape_valid_only",
        "full_reader_recheck": "blocked_by_candidate_input_contract",
        "human_comparison": "original versus proposed dates, quantities, evidence and commitment status",
    }


def verify_run_correlation(candidate: Candidate, original_run: dict, proposed_run: dict) -> None:
    """Reject a purported candidate run which still reads the original deal."""
    if str(original_run["run_id"]) != str(candidate.parent_run_id):
        raise ValueError("Parent run identity mismatch")
    if str(proposed_run["run_id"]) == str(candidate.parent_run_id):
        raise ValueError("Candidate cannot reuse the parent run")
    if proposed_run["deal_id"] == candidate.parent_deal_id:
        raise ValueError("A run on the unchanged parent deal cannot verify changed fields")
    for field, value in (("as_of_at", candidate.as_of_at),
                         ("catalog_version_used", candidate.catalog_version),
                         ("applied_policy_set_code", candidate.policy_set_code),
                         ("data_snapshot_ref", candidate.data_snapshot_ref)):
        if proposed_run[field] != value:
            raise ValueError(f"Candidate run differs in frozen context: {field}")
    if proposed_run.get("input_snapshot_json", {}).get("candidate_id") != candidate.candidate_id:
        raise ValueError("Candidate-to-run link missing")
