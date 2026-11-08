"""Read-only, source-bound V0/V1 human-review projection; never an approval API."""

from datetime import date
from decimal import Decimal
import re
from typing import Literal, TypedDict

from .candidate_contract import construct_candidate
from .candidate_graph import _proposal
from .evidence_bundle import unseal
from .graph_state import SPECIALISTS, pinned_from_state
from .m22_capture import capture_m22
from .m22_evidence_gaps import project_gap_review
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT


VERSION = "source-grounded-review-v1"
_CODE = re.compile(r"[a-z][a-z0-9_:-]{0,100}\Z")
_REFERENCE = re.compile(r"[A-Za-z][A-Za-z0-9_]*:[A-Za-z0-9_.-]{1,100}\Z")


class FindingV1(TypedDict):
    fixed_execution: str
    fixed_finding: str
    fixed_rule_ids: list[str]
    ai_original_execution: str | None
    ai_original_citations: list[dict[str, str]]
    evidence_gaps: list["GapV1"]


class GapV1(TypedDict):
    requirement_id: str
    reason_code: str
    verification: str
    impact_code: str
    next_action_code: str


class LineV1(TypedDict):
    line_id: str
    quantity: int


class SliceV1(TypedDict):
    quantity: int
    delivery_date: str
    source_refs: list[str]


class BlockV1(TypedDict, total=False):
    code: str
    line_id: str | None
    rule_id: str
    specialist: str


class ReasonV1(TypedDict):
    code: str
    line_id: str | None


class ApprovalRequirementV1(TypedDict):
    rule_id: str
    severity: str


class HumanRoleV1(TypedDict):
    rule_id: str
    role: str
    sequence: int


class AvailabilityV1(TypedDict):
    line_id: str
    status: str
    requested_quantity: int
    quantity_by_requested_date: str
    earliest_full_date: str | None


class SubjectV1(TypedDict):
    subject_kind: Literal["original", "candidate"]
    subject_id: str
    business_status: str
    specialists: dict[str, FindingV1]
    requested_delivery_date: str
    lines: list[LineV1]
    availability: list[AvailabilityV1]
    blockers: list[BlockV1]
    revision_reasons: list[ReasonV1]
    evidence_gaps: list[str]
    uncommitted_paths: list[str]
    approval_requirements: list[ApprovalRequirementV1]
    routing_roles_status: str
    required_roles: list[HumanRoleV1] | None


class CandidateComparisonV1(TypedDict):
    parent_subject_id: str
    candidate_id: str
    candidate_input_digest: str
    changed_field: Literal["proposed_delivery_slices"]
    original_line_id: str
    original_quantity: int
    original_requested_date: str
    proposed_slices: list[SliceV1]
    fixed_supply_status: str
    reservation_status: Literal["not_reserved"]
    customer_acceptance: Literal["pending"]
    unmet_customer_constraints: list[str]
    addressed_original_reasons: list[str]
    remaining_revision_reasons: list[str]


class RecommendationV1(TypedDict):
    specialist: str
    action_code: str
    verification: Literal["deterministic", "suggested_unverified"]
    subject_id: str
    source_refs: list[str]
    rule_ids: list[str]
    remaining_customer_constraints: list[str]


class SourceGroundedReviewV1(TypedDict):
    version: str
    assessment_id: str
    phase1c_pin: str
    phase1c_run_id: str
    bundle_sha256: str
    source_input_digest: str
    original: SubjectV1
    candidate: SubjectV1 | None
    candidate_comparison: CandidateComparisonV1 | None
    recommendations: list[RecommendationV1]
    reviewer_action: str
    permitted_next_actions: list[str]
    authorization: Literal["human_only_not_granted"]


def _codes(items, *, line_ids):
    if type(items) is not list:
        raise EvidenceMismatch("Review decision codes missing")
    result = []
    for item in items:
        if (type(item) is not dict or type(item.get("code")) is not str
                or not _CODE.fullmatch(item["code"]) or
                item.get("line_id") not in (None, *line_ids)):
            raise EvidenceMismatch("Review decision reason not source-bound")
        result.append({"code": item["code"], "line_id": item.get("line_id")})
    return result


def _blocks(items, *, line_ids):
    if type(items) is not list:
        raise EvidenceMismatch("Review fixed blockers missing")
    result = []
    for item in items:
        if type(item) is not dict:
            raise EvidenceMismatch("Review fixed blocker malformed")
        if "rule_id" in item:
            rule = item["rule_id"]
            if (type(rule) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", rule)
                    or item.get("area") not in ("configuration", "pricing", "credit", "policy")
                    or item.get("severity") != "blocker"
                    or item.get("scope") not in ("deal", *line_ids)):
                raise EvidenceMismatch("Review fixed rule blocker differs")
            result.append({"code": "fixed_rule_blocker", "rule_id": rule,
                           "specialist": item["area"]})
        else:
            code = item.get("code")
            if (type(code) is not str or not _CODE.fullmatch(code) or
                    item.get("line_id") not in (None, *line_ids)):
                raise EvidenceMismatch("Review fixed blocker differs")
            result.append({"code": code, "line_id": item.get("line_id")})
    return result


def _subject(kind, subject_id, decision, fixed, gaps, pool, ai=None):
    deal, lines = pool["deal"], pool["lines"]
    if (type(decision) is not dict or decision.get("deal_id") != deal["deal_id"]
            or type(decision.get("status")) is not str or
            type(deal.get("requested_delivery_date")) is not date or
            type(lines) is not list or not lines or
            any(type(row.get("quantity")) is not int or row["quantity"] <= 0
                or type(row.get("deal_line_id")) is not str for row in lines)):
        raise EvidenceMismatch("Review subject source shape differs")
    line_ids = {line["deal_line_id"] for line in lines}
    availability = decision["specialists"]["availability"]
    if (type(availability) is not list or len(availability) != len(lines) or
            {row.get("line_id") for row in availability} != line_ids or
            any(type(row.get("requested_quantity")) is not int or
                type(row.get("quantity_by_requested_date")) not in (Decimal, int) or
                type(row.get("status")) is not str or
                row.get("earliest_full_date") is not None and
                type(row["earliest_full_date"]) is not date for row in availability)):
        raise EvidenceMismatch("Review fixed availability differs from original lines")
    specialists = {}
    for name in SPECIALISTS:
        row = fixed[name]
        observation = ai[name] if ai is not None else None
        raw_rule_ids = ([hit["rule_id"] for hit in decision["specialists"][name][
            "rule_hits"]] if name in ("pricing", "credit", "policy") else
            [hit["compatibility_rule_id"] for hit in decision["specialists"][
                "compatibility"]] if name == "configuration" else [])
        if any(type(rule) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", rule)
               for rule in raw_rule_ids):
            raise EvidenceMismatch("Review fixed specialist rule reference invalid")
        citations = []
        if observation is not None:
            for claim in observation["validated_claims"]:
                # Credit refs can disclose customer/invoice/payment identities.
                # They remain server-side for a separately authorized drilldown.
                if name != "credit":
                    if not _REFERENCE.fullmatch(claim["ref"]):
                        raise EvidenceMismatch("Review citation reference malformed")
                    citations.append({"ref": claim["ref"], "field": claim["field"]})
        specialists[name] = {"fixed_execution": row["execution"],
            "fixed_finding": row["finding"],
            "fixed_rule_ids": raw_rule_ids,
            "ai_original_execution": observation["execution"] if observation else None,
            "ai_original_citations": citations,
            "evidence_gaps": [{key: gap[key] for key in (
                "requirement_id", "reason_code", "verification", "impact_code",
                "next_action_code")} for gap in gaps[name]]}
    hits = decision["specialists"]["policy"]["rule_hits"]
    if type(hits) is not list or any(type(hit.get("rule_id")) is not str or
            not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", hit["rule_id"]) for hit in hits):
        raise EvidenceMismatch("Review policy rule IDs invalid")
    routing = fixed["approval_routing"]["payload"]
    if (type(routing) is not dict or type(routing.get("route_withheld")) is not bool
            or type(routing.get("roles_available_from_fixed_interface")) is not bool):
        raise EvidenceMismatch("Review fixed routing state invalid")
    roles = None
    if routing["roles_available_from_fixed_interface"]:
        if routing["route_withheld"] or type(routing.get("required_roles")) is not list:
            raise EvidenceMismatch("Review fixed routing roles unavailable")
        roles = []
        for role in routing["required_roles"]:
            if (type(role) is not dict or type(role.get("rule_id")) is not str or
                    type(role.get("role")) is not str or
                    not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", role["rule_id"]) or
                    not re.fullmatch(r"[A-Za-z0-9_ .-]{1,100}", role["role"]) or
                    type(role.get("sequence")) is not int):
                raise EvidenceMismatch("Review fixed routing role invalid")
            roles.append({"rule_id": role["rule_id"], "role": role["role"],
                          "sequence": role["sequence"]})
    elif not routing["route_withheld"]:
        raise EvidenceMismatch("Review route cannot expose unknown roles")
    # Never return unrestricted fixed payloads or customer/credit ledger rows.
    return {"subject_kind": kind, "subject_id": subject_id,
        "business_status": decision["status"], "specialists": specialists,
        "requested_delivery_date": deal["requested_delivery_date"].isoformat(),
        "lines": [{"line_id": row["deal_line_id"], "quantity": row["quantity"]}
                  for row in lines],
        "availability": [{"line_id": row["line_id"], "status": row["status"],
            "requested_quantity": row["requested_quantity"],
            "quantity_by_requested_date": str(row["quantity_by_requested_date"]),
            "earliest_full_date": (row["earliest_full_date"].isoformat()
                if row.get("earliest_full_date") is not None else None)}
            for row in availability],
        "blockers": _blocks(decision["blocks"], line_ids=line_ids),
        "revision_reasons": _codes(decision["revision_reasons"], line_ids=line_ids),
        "evidence_gaps": [gap["reason_code"] for group in gaps.values() for gap in group],
        "uncommitted_paths": ["uncommitted_path_requires_review"] * len(
            decision["uncommitted_paths"]),
        "approval_requirements": [{"rule_id": hit["rule_id"],
            "severity": hit["severity"]} for hit in hits if hit["severity"] ==
                "approval_required"],
        "routing_roles_status": ("available_from_fixed_interface" if roles is not None
            else "unavailable_while_route_withheld"), "required_roles": roles}


def project_source_grounded_review(state: dict, adapter, *, checkpoint_pending=False) -> SourceGroundedReviewV1:
    """Project one completed checkpoint, with no DB writes, send or acceptance."""
    observation = capture_m22(state, adapter, checkpoint_pending=checkpoint_pending)
    if observation["evaluation_status"] != "completed" or any(
            row is None or row["execution"] not in ("completed", "abstained")
            for row in observation["ai_original"].values()):
        raise EvidenceMismatch("Review requires completed six-stage assessment")
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    original_decision = unseal(state["fixed_decision"], state["fixed_decision_sha256"])
    if original_decision != adapter.fixed_original_decision(pinned):
        raise EvidenceMismatch("Review original fixed decision differs from pinned source")
    gaps = project_gap_review(state, adapter)
    if gaps["ai_gap_suggestions"]:
        raise EvidenceMismatch("Review does not accept externally supplied gap suggestions")
    original_gaps = {name: gaps["original"]["specialists"][name]["evidence_gaps"]
        for name in SPECIALISTS}
    original = _subject("original", ctx.original_deal_id, original_decision,
        state["specialist_results"], original_gaps, pool, observation["ai_original"])
    candidate, comparison = None, None
    recommendations: list[RecommendationV1] = []
    if observation["candidate_id"] is not None:
        _, proposal = _proposal(state, adapter)  # Recheck returned binding-source citations.
        reconstructed, expected = construct_candidate(adapter, pinned, proposal)
        record = state["candidate_records"][observation["candidate_id"]]
        if any(record.get(key) != expected[key] for key in (
                "candidate_id", "parent_deal_id", "parent_candidate_id", "parent_run_id",
                "line_id", "proposed_slices", "original_requested_date", "source_input_digest",
                "bundle_sha256")) or reconstructed.candidate_id != observation["candidate_id"]:
            raise EvidenceMismatch("Review candidate lineage or field changes differ")
        candidate_decision = unseal(record["fixed_decision"], record["fixed_decision_sha256"])
        trace = candidate_decision["candidate_trace"]
        slices = trace.get("assessment", {}).get("slices")
        if type(slices) is not list or len(slices) != len(proposal["delivery_slices"]):
            raise EvidenceMismatch("Review candidate checked slices missing")
        cumulative = 0
        for checked, proposed in zip(slices, proposal["delivery_slices"]):
            cumulative += int(proposed["quantity"])
            if (checked.get("line_id") != proposal["line_id"] or
                    checked.get("quantity") != int(proposed["quantity"]) or
                    checked.get("arrival_date") != date.fromisoformat(proposed["delivery_date"]) or
                    checked.get("cumulative_quantity") != cumulative or
                    checked.get("source_status") != "binding_unreserved" or
                    sorted(checked.get("source_ids", [])) != sorted(
                        ref.split(":", 1)[1] for ref in proposed["source_refs"])):
                raise EvidenceMismatch("Review candidate fixed slices differ from cited proposal")
        if (trace.get("source_input_digest") != ctx.source_input_digest or
                trace.get("candidate_input_digest") != record["candidate_input_digest"] or
                trace.get("original_requested_date") != pool["deal"]["requested_delivery_date"] or
                trace.get("assessment", {}).get("status") != record["fixed_supply_status"] or
                gaps["candidates"][0]["candidate_id"] != record["candidate_id"]):
            raise EvidenceMismatch("Review candidate verifier source differs")
        candidate_gaps = {name: gaps["candidates"][0]["specialists"][name]["evidence_gaps"]
            for name in SPECIALISTS}
        candidate = _subject("candidate", record["candidate_id"], candidate_decision,
            record["specialist_results"], candidate_gaps, pool)
        cited = sorted({ref for item in proposal["delivery_slices"] for ref in item["source_refs"]})
        if (record["fixed_supply_status"] != "supply_supported_unreserved" or
                record["fixed_business_status"] != candidate["business_status"] or
                state["reviewer_package"]["candidates"][0]["customer_acceptance"] != "pending" or
                type(candidate_decision.get("customer_constraints_unmet")) is not list or
                "original_requested_delivery_date" not in candidate_decision[
                    "customer_constraints_unmet"]):
            raise EvidenceMismatch("Review candidate cannot be offered as supported")
        comparison = {"parent_subject_id": ctx.original_deal_id,
            "candidate_id": record["candidate_id"],
            "candidate_input_digest": record["candidate_input_digest"],
            "changed_field": "proposed_delivery_slices",
            "original_line_id": record["line_id"],
            "original_quantity": next(row["quantity"] for row in pool["lines"] if row[
                "deal_line_id"] == record["line_id"]),
            "original_requested_date": record["original_requested_date"],
            "proposed_slices": [{"quantity": int(item["quantity"]),
                "delivery_date": item["delivery_date"], "source_refs": list(item["source_refs"])}
                for item in proposal["delivery_slices"]],
            "fixed_supply_status": record["fixed_supply_status"],
            "reservation_status": "not_reserved",
            "customer_acceptance": "pending",
            "unmet_customer_constraints": list(candidate_decision["customer_constraints_unmet"]),
            "addressed_original_reasons": [row["code"] for row in original[
                "revision_reasons"] if row["code"] == "requested_date_not_supported" and
                any(item["code"] == "partial_delivery_requires_customer_acceptance"
                    for item in candidate["revision_reasons"])],
            "remaining_revision_reasons": [row["code"] for row in candidate["revision_reasons"]]}
        recommendations.append({"specialist": "fulfillment",
            "action_code": "present_supported_partial_option_for_customer_review",
            "verification": "deterministic", "subject_id": record["candidate_id"],
            "source_refs": cited, "rule_ids": [],
            "remaining_customer_constraints": list(candidate_decision["customer_constraints_unmet"])})
    elif any(reason["code"] == "requested_date_not_supported" for reason in
             original["revision_reasons"]):
        recommendations.append({"specialist": "fulfillment",
            "action_code": "investigate_delivery_alternative_with_human",
            "verification": "suggested_unverified", "subject_id": ctx.original_deal_id,
            "source_refs": [], "rule_ids": [],
            "remaining_customer_constraints": ["original_requested_delivery_date"]})
    for name in SPECIALISTS:
        finding = original["specialists"][name]
        if finding["fixed_execution"] != "completed":
            raise EvidenceMismatch("Review fixed specialist incomplete")
        if finding["evidence_gaps"]:
            recommendations.append({"specialist": name, "action_code": "review_evidence_gap",
                "verification": "suggested_unverified", "subject_id": ctx.original_deal_id,
                "source_refs": [], "rule_ids": [], "remaining_customer_constraints": []})
    for blocker in original["blockers"]:
        if blocker["code"] == "fixed_rule_blocker":
            recommendations.append({"specialist": blocker["specialist"],
                "action_code": "refer_fixed_blocker_to_human",
                "verification": "deterministic", "subject_id": ctx.original_deal_id,
                "source_refs": [], "rule_ids": [blocker["rule_id"]],
                "remaining_customer_constraints": []})
    for name, expected_finding in (("configuration", "confirmed"),
                                   ("pricing", "calculated"), ("credit", "calculated")):
        if (original["specialists"][name]["fixed_finding"] == expected_finding and
                not any(block.get("specialist") == name for block in original["blockers"])):
            recommendations.append({"specialist": name,
                "action_code": "no_fixed_blocker_in_selected_evidence",
                "verification": "deterministic", "subject_id": ctx.original_deal_id,
                "source_refs": [], "rule_ids": [],
                "remaining_customer_constraints": []})
    for hit in original_decision["specialists"]["policy"]["rule_hits"]:
        if hit["severity"] == "approval_required":
            recommendations.append({"specialist": "policy",
                "action_code": "retain_late_delivery_policy_review" if hit["rule_id"] ==
                    "PO-BASE-DELIVERY-LATE" else "retain_policy_review",
                "verification": "deterministic", "subject_id": ctx.original_deal_id,
                "source_refs": [], "rule_ids": [hit["rule_id"]],
                "remaining_customer_constraints": []})
    if original["specialists"]["approval_routing"]["fixed_finding"] == "withheld":
        recommendations.append({"specialist": "approval_routing",
            "action_code": "route_withheld_until_revised_submission",
            "verification": "deterministic", "subject_id": ctx.original_deal_id,
            "source_refs": [], "rule_ids": [], "remaining_customer_constraints": []})
    return {"version": VERSION, "assessment_id": ctx.assessment_id,
        "phase1c_pin": PHASE1C_COMMIT, "phase1c_run_id": str(ctx.phase1c_run_id),
        "bundle_sha256": ctx.bundle_sha256, "source_input_digest": ctx.source_input_digest,
        "original": original, "candidate": candidate,
        "candidate_comparison": comparison, "recommendations": recommendations,
        "reviewer_action": state["reviewer_package"]["reviewer_action"],
        "permitted_next_actions": (["seek_customer_acceptance", "request_human_review"]
            if candidate else ["request_human_review", "request_evidence_if_needed"]),
        "authorization": "human_only_not_granted"}
