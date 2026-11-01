"""Read-only, versioned evidence-gap reviewer projection over pinned checkpoints.

No new business prerequisite or source completeness is inferred by this module.
Historical reviewer packages and AI output contracts remain untouched.
"""

from copy import deepcopy
from typing import Literal, TypedDict

from .graph_state import SPECIALISTS, pinned_from_state
from .m22_capture import capture_m22
from .phase1c_adapter import EvidenceMismatch

VERSION = "m22-evidence-gap-v1"
REVIEW_VERSION = "m22-evidence-review-v1"
REASONS = {"missing", "incomplete", "stale", "conflicting", "unavailable",
           "conditional_unconfirmed", "prerequisite_unmet"}
ACTIONS = {"request_evidence", "verify_source", "investigate", "seek_source_contract"}
IMPACTS = {"configuration_uncertain", "cost_uncertain", "delivery_uncertain",
           "credit_uncertain", "policy_scope_unknown", "routing_withheld",
           "dependent_check_unavailable"}
IMPACT_TEXT = {
    "configuration_uncertain": "Configuration compatibility needs source review.",
    "cost_uncertain": "Conflicting cost evidence limits the pricing conclusion.",
    "delivery_uncertain": "Delivery evidence does not establish a confirmed commitment.",
    "credit_uncertain": "Credit exposure or commitment scope cannot be cleared from this evidence.",
    "policy_scope_unknown": "Per-rule prerequisite coverage is not exposed by this interface.",
    "routing_withheld": "Required roles cannot be inferred while routing is withheld.",
    "dependent_check_unavailable": "This specialist lacks a completed prerequisite or fixed result."}
ACTION_TEXT = {
    "request_evidence": "Ask the source owner for updated, dated evidence.",
    "verify_source": "Have an authorized reviewer verify the cited source or diagnostic.",
    "investigate": "Have a human reviewer investigate the upstream stop; do not approve.",
    "seek_source_contract": "Ask the source owner whether a trusted completeness interface exists."}


class EvidenceGapV1(TypedDict):
    version: str
    assessment_id: str
    phase1c_run_id: str
    subject_kind: Literal["original", "candidate"]
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    as_of_at: str
    specialist: str
    requirement_id: str
    field_path: str | None
    line_id: str | None
    rule_id: str | None
    source_ref: str | None
    scope: Literal["fixed_result", "selected_reader_pool", "returned_tool_records",
                   "interface_unavailable"]
    reason_code: str
    basis: Literal["fixed_result", "returned_record", "interface_limit", "model_suggestion"]
    verification: Literal["verified", "interface_limit", "suggested_unverified"]
    impact_code: str
    impact_text: str
    next_action_code: str
    next_action_text: str
    resolution_status: Literal["unresolved"]


def _gap(ctx, name, subject, requirement, field, reason, impact, action, *,
         line=None, rule=None, source=None, scope="fixed_result", basis="fixed_result",
         verification="verified") -> EvidenceGapV1:
    gap: EvidenceGapV1 = {"version": VERSION, "assessment_id": ctx.assessment_id,
        "phase1c_run_id": str(ctx.phase1c_run_id), "subject_kind": subject[0],
        "subject_id": subject[1], "bundle_sha256": ctx.bundle_sha256,
        "source_input_digest": ctx.source_input_digest, "as_of_at": ctx.as_of_at.isoformat(),
        "specialist": name, "requirement_id": requirement, "field_path": field,
        "line_id": line, "rule_id": rule, "source_ref": source, "scope": scope,
        "reason_code": reason, "basis": basis, "verification": verification,
        "impact_code": impact, "impact_text": IMPACT_TEXT[impact],
        "next_action_code": action, "next_action_text": ACTION_TEXT[action],
        "resolution_status": "unresolved"}
    if (name not in SPECIALISTS or reason not in REASONS or impact not in IMPACTS or
            action not in ACTIONS or not requirement or
            (verification == "verified" and basis != "fixed_result") or
            (verification == "interface_limit" and (basis != "interface_limit" or
             scope != "interface_unavailable" or source is not None)) or
            (verification == "suggested_unverified" and basis != "model_suggestion")):
        raise EvidenceMismatch("M2.2 evidence-gap provenance invalid")
    return gap


def _fixed_gaps(ctx, subject, results, pool):
    gaps = {name: [] for name in SPECIALISTS}
    for name in SPECIALISTS:
        row = results[name]
        payload = row.get("payload")
        if row["execution"] != "completed":
            if row["execution"] == "skipped":
                gaps[name].append(_gap(ctx, name, subject, "fixed_prerequisite", "prerequisite",
                    "prerequisite_unmet", "dependent_check_unavailable", "investigate"))
            else:
                gaps[name].append(_gap(ctx, name, subject, "fixed_result_unavailable", None,
                    "unavailable", "dependent_check_unavailable", "investigate",
                    scope="interface_unavailable", basis="interface_limit",
                    verification="interface_limit"))
            continue
        if name == "configuration":
            for item in payload["compatibility"]:
                if item.get("status") == "unknown":
                    rule = str(item["compatibility_rule_id"])
                    gaps[name].append(_gap(ctx, name, subject,
                        "compatibility_rule_unknown", "compatibility.status", "unavailable",
                        "configuration_uncertain", "verify_source", rule=rule,
                        line=item.get("line_id")))
        elif name == "pricing":
            for diagnostic in payload["cost_evidence_gaps"]:
                if type(diagnostic) is not str or not diagnostic.startswith(
                        "assembly_cost_disagreement:"):
                    raise EvidenceMismatch("M2.2 unknown pricing evidence diagnostic")
                gaps[name].append(_gap(ctx, name, subject, "assembly_cost_disagreement",
                    "cost_rollup.within_5_pct", "conflicting", "cost_uncertain",
                    "verify_source"))
        elif name == "fulfillment":
            for line in payload:
                status = line["status"]
                if status in ("unknown", "pending_production_check", "conditional",
                              "feasible_uncommitted"):
                    gaps[name].append(_gap(ctx, name, subject,
                        "fulfillment_" + status, "availability.status",
                        "conditional_unconfirmed" if status in (
                            "conditional", "feasible_uncommitted") else
                        "incomplete" if status == "pending_production_check" else "unavailable",
                        "delivery_uncertain", "verify_source", line=line["line_id"]))
                if line.get("installation") == "unknown":
                    gaps[name].append(_gap(ctx, name, subject,
                        "installation_eligibility_missing", "availability.installation",
                        "unavailable", "delivery_uncertain", "verify_source",
                        line=line["line_id"]))
        elif name == "credit":
            if payload["commitments_fresh"] is False:
                credit = pool.get("credit") if subject[0] == "original" else None
                customer = pool.get("deal", {}).get("customer_id")
                if credit is not None and (credit.get("customer_id") != customer or
                        credit.get("commitments_as_of_at") > ctx.as_of_at):
                    raise EvidenceMismatch("M2.2 stale Credit source identity differs")
                gaps[name].append(_gap(ctx, name, subject, "credit_commitments_fresh",
                    "commitments_as_of_at", "stale", "credit_uncertain", "request_evidence",
                    source="credit_profile:" + str(customer) if credit is not None else None,
                    scope="selected_reader_pool" if credit is not None else "fixed_result"))
            gaps[name].append(_gap(ctx, name, subject, "credit_ledger_completeness",
                None, "unavailable", "credit_uncertain", "seek_source_contract",
                scope="interface_unavailable", basis="interface_limit",
                verification="interface_limit"))
        elif name == "policy" and payload["per_rule_prerequisites_available"] is False:
            gaps[name].append(_gap(ctx, name, subject, "per_rule_prerequisites",
                None, "unavailable", "policy_scope_unknown", "seek_source_contract",
                scope="interface_unavailable", basis="interface_limit",
                verification="interface_limit"))
        elif name == "approval_routing" and payload["route_withheld"] is True:
            gaps[name].append(_gap(ctx, name, subject, "route_roles_withheld",
                "required_roles", "unavailable", "routing_withheld", "investigate",
                scope="interface_unavailable", basis="interface_limit",
                verification="interface_limit"))
    return gaps


def _suggestions(ctx, state, gaps, suggestions):
    if not isinstance(suggestions, (tuple, list)) or len(suggestions) > 12:
        raise EvidenceMismatch("M2.2 gap suggestion limit exceeded")
    returned = {name: {} for name in SPECIALISTS}
    for event in state.get("tool_access_ledger", []):
        if event["status"] == "completed":
            name = event["identity"]["specialist"]
            for record in event.get("result", {}).get("records", []):
                ref = record.get("ref") or (str(record["category"]) + ":" +
                                            str(record["id"]) if name == "fulfillment" else None)
                if ref in event.get("returned_refs", []):
                    returned[name].setdefault(ref, set()).add(event.get("args", {}).get("line_id"))
    projected = []
    for item in suggestions:
        if type(item) is not dict or set(item) != {"specialist", "requirement_id", "source_ref"}:
            raise EvidenceMismatch("M2.2 unsupported model gap suggestion")
        name, requirement, ref = (item[k] for k in ("specialist", "requirement_id", "source_ref"))
        if (type(name) is not str or name not in SPECIALISTS or
                type(requirement) is not str or
                ref is not None and type(ref) is not str):
            raise EvidenceMismatch("M2.2 gap suggestion identity invalid")
        match = next((g for g in gaps.get(name, []) if g["requirement_id"] == requirement), None)
        if (match is None or ref is not None and (ref != match["source_ref"] or
                ref not in returned[name] or
                match["line_id"] is not None and match["line_id"] not in returned[name][ref])):
            raise EvidenceMismatch("M2.2 unsupported or unreturned gap suggestion")
        projected.append(_gap(ctx, name, ("original", ctx.original_deal_id), requirement,
            match["field_path"], match["reason_code"], match["impact_code"],
            match["next_action_code"], line=match["line_id"], rule=match["rule_id"],
            source=ref, scope="returned_tool_records" if ref else "fixed_result",
            basis="model_suggestion", verification="suggested_unverified"))
    if len({(g["specialist"], g["requirement_id"], g["source_ref"]) for g in projected}) != len(projected):
        raise EvidenceMismatch("M2.2 duplicate gap suggestion")
    return projected


def project_gap_review(state, adapter, *, suggestions=()):
    """Return a new reviewer-package version; do not mutate/checkpoint old packages."""
    observation = capture_m22(state, adapter)
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    original = _fixed_gaps(ctx, ("original", ctx.original_deal_id),
                           state["specialist_results"], pool)
    candidate = None
    if observation["candidate_id"] is not None:
        candidate = _fixed_gaps(ctx, ("candidate", observation["candidate_id"]),
            state["candidate_records"][observation["candidate_id"]]["specialist_results"], pool)
    suggested = _suggestions(ctx, state, original, suggestions)
    package = deepcopy(state["reviewer_package"])
    base_version = package["version"]
    package["version"] = REVIEW_VERSION
    for name in SPECIALISTS:
        package["original"]["specialists"][name]["evidence_gaps"] = original[name]
    if candidate is not None:
        if len(package["candidates"]) != 1 or package["candidates"][0]["candidate_id"] != observation["candidate_id"]:
            raise EvidenceMismatch("M2.2 gap candidate reviewer identity differs")
        for name in SPECIALISTS:
            package["candidates"][0]["specialists"][name]["evidence_gaps"] = candidate[name]
    package["ai_gap_suggestions"] = suggested
    package["gap_contract_version"] = VERSION
    package["gap_review_base_version"] = base_version
    return package
