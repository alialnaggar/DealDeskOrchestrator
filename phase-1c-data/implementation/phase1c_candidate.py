"""Typed, side-effect-free proposal and audit boundary for the first alternative trial.

This module does not turn a proposal into a submitted deal or a checked result.
The existing reader reads deal_lines, not candidate changes in a run snapshot.
"""

from dataclasses import dataclass
from datetime import datetime, date
from hashlib import sha256
import json
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
    "terms_json.contract_clause_codes", "proposed_delivery_slices",
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
        if (self.field in {"requested_delivery_date", "proposed_delivery_slices", "terms_json.allow_partial_delivery",
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
            if len(self.changes) != 1 or self.changes[0].field != "proposed_delivery_slices":
                raise ValueError("Partial delivery must preserve the submitted requested date")
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
    original_schedule = tuple(sorted((line_id, quantity, requested_date)
                                     for line_id, quantity in original_quantities.items()))
    proposed_schedule = tuple((s.line_id, s.quantity, s.arrival_date) for s in candidate.delivery_slices)
    if candidate.changes[0].before != original_schedule or candidate.changes[0].after != proposed_schedule:
        raise ValueError("Schedule diff must match the original request and exact proposed slices")
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


INPUT_TABLES = ("deal", "lines", "customer", "credit", "receivables", "payments", "rules",
                "compatibility", "bom", "bom_lines", "requirements", "inventory", "inbound_supply",
                "supplier_offers", "production_capacity", "digital_capacity", "shipping_lanes",
                "cost_parameters")


def reader_input_digest(bundle: dict, candidate: Candidate | None = None) -> str:
    """Fingerprint the source facts selected by the reader, not a caller's claimed run ID."""
    payload = {key: bundle[key] for key in INPUT_TABLES}
    payload["run_context"] = {key: bundle["run"][key] for key in
                              ("run_id", "deal_id", "as_of_at", "catalog_version_used",
                               "applied_policy_set_code", "data_snapshot_ref", "config_hash")}
    if candidate is not None:
        payload["candidate"] = {"id": candidate.candidate_id,
                                "slices": [(s.line_id, s.quantity, s.arrival_date.isoformat(),
                                            s.evidence_ids, s.commitment) for s in candidate.delivery_slices]}
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return sha256(encoded.encode()).hexdigest()


def assess_reader_slices(candidate: Candidate, bundle: dict) -> dict:
    """Compare cumulative slice demand with dated binding options at one location.

    Offers, separate locations and unbooked production never become confirmations.
    The initial experiment is limited to one stocked/supplier-finished line.
    """
    run, deal, lines = bundle["run"], bundle["deal"], bundle["lines"]
    if str(run["run_id"]) != str(candidate.parent_run_id) or deal["deal_id"] != candidate.parent_deal_id:
        raise ValueError("Candidate parent run/deal mismatch")
    for field, expected in (("as_of_at", candidate.as_of_at),
                            ("catalog_version_used", candidate.catalog_version),
                            ("applied_policy_set_code", candidate.policy_set_code),
                            ("data_snapshot_ref", candidate.data_snapshot_ref)):
        if run[field] != expected:
            raise ValueError(f"Candidate differs from frozen reader context: {field}")
    if candidate.proposal_kind != "partial_delivery" or len(lines) != 1 or lines[0]["fulfillment_mode"] not in {"stocked_finished", "supplier_finished"}:
        raise ValueError("First reader experiment supports one stocked or supplier-finished line")
    line = lines[0]
    requested = deal["requested_delivery_date"]
    review_partial_delivery(candidate, original_quantities={line["deal_line_id"]: line["quantity"]},
                            requested_date=requested,
                            partial_allowed=deal["terms_json"].get("allow_partial_delivery") is True,
                            indivisible_groups=(frozenset({line["deal_line_id"]}),) if line["fulfillment_group_code"] else ())
    if any(s.arrival_date <= requested for s in candidate.delivery_slices) is False:
        raise ValueError("Candidate must offer some units by the original requested date")
    options = bundle["facts"]["lines"][0].get("shipping_options", [])
    ordered = sorted(candidate.delivery_slices, key=lambda s: s.arrival_date)
    locations = sorted({o["location"] for o in options})
    for location in locations:
        cumulative = 0
        findings = []
        for item in ordered:
            cumulative += item.quantity
            eligible = [o for o in options if o["location"] == location and
                        o["arrival"] <= item.arrival_date and o["quantity"] >= cumulative]
            if not eligible:
                break
            option = min(eligible, key=lambda o: (o["arrival"], len(o["supply_ids"])))
            actual_ids = set(option["supply_ids"])
            if option.get("stock_id"):
                actual_ids.add(option["stock_id"])
            if set(item.evidence_ids) - actual_ids or item.commitment != "confirmed":
                raise ValueError("Proposed source claim differs from selected binding evidence")
            findings.append({"line_id": item.line_id, "quantity": item.quantity,
                             "arrival_date": item.arrival_date, "cumulative_quantity": cumulative,
                             "source_ids": sorted(actual_ids), "source_status": "binding_unreserved"})
        if len(findings) == len(ordered):
            return {"status": "supply_supported_unreserved", "location": location,
                    "original_requested_date": requested, "slices": findings}
    return {"status": "unknown_or_unavailable", "location": None,
            "original_requested_date": requested, "slices": [],
            "reason": "No single location has enough dated binding supply for every slice"}


def verify_run_correlation(candidate: Candidate, original_bundle: dict, candidate_bundle: dict) -> None:
    """Verify the exact source inputs the reader used for a candidate assessment."""
    trace = candidate_bundle.get("candidate_trace")
    if not trace or trace.get("candidate_id") != candidate.candidate_id:
        raise ValueError("Candidate trace identity missing")
    if (original_bundle["run"] != candidate_bundle["run"] or
            original_bundle["deal"] != candidate_bundle["deal"] or
            original_bundle["lines"] != candidate_bundle["lines"]):
        raise ValueError("Original submitted facts changed")
    if trace.get("original_requested_date") != original_bundle["deal"]["requested_delivery_date"]:
        raise ValueError("Original customer date was overwritten")
    actual_original = reader_input_digest(original_bundle)
    actual_source = reader_input_digest(candidate_bundle)
    actual_candidate = reader_input_digest(candidate_bundle, candidate)
    if (actual_original != actual_source or trace.get("source_input_digest") != actual_source or
            trace.get("candidate_input_digest") != actual_candidate):
        raise ValueError("Reader-used source facts or candidate slices differ from trace")
    if trace.get("assessment") != assess_reader_slices(candidate, candidate_bundle):
        raise ValueError("Candidate assessment differs from reader-used evidence")


def compare_for_human(candidate: Candidate, original_bundle: dict, candidate_bundle: dict) -> dict:
    """Read-only original-versus-option package after both deterministic checks."""
    from phase1c_deal_decision import assemble_deal_decision

    verify_run_correlation(candidate, original_bundle, candidate_bundle)
    original = assemble_deal_decision(original_bundle)
    proposal = assemble_deal_decision(candidate_bundle)
    if proposal.get("candidate_trace", {}).get("candidate_id") != candidate.candidate_id:
        raise ValueError("Decision output is not tied to the reader-checked candidate")
    return {
        "candidate_id": candidate.candidate_id,
        "parent_deal_id": candidate.parent_deal_id,
        "parent_run_id": str(candidate.parent_run_id),
        "original_requested_date": original_bundle["deal"]["requested_delivery_date"],
        "original": {"status": original["status"], "availability": original["specialists"]["availability"],
                     "revision_reasons": original["revision_reasons"]},
        "proposed": {"status": proposal["status"], "availability": proposal["specialists"]["availability"],
                     "revision_reasons": proposal["revision_reasons"],
                     "evidence_gaps": proposal["evidence_gaps"]},
        "reader_input_digest": proposal["candidate_trace"]["candidate_input_digest"],
        "customer_constraints_unmet": candidate.unmet_constraints,
        "assumptions": candidate.assumptions,
        "tradeoff": candidate.tradeoff,
        "human_action": "Seek customer acceptance and prescribed internal review; no approval or delivery promise",
    }
