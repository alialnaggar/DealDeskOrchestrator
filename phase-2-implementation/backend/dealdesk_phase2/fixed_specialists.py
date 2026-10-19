"""Map one authoritative Phase 1C decision; never recalculate its business rules."""

from .graph_state import SpecialistResultV1
from .phase1c_adapter import PinnedBundleV1


def domain_result(name: str, pinned: PinnedBundleV1, decision: dict | None,
                  assessment_id: str, prior: dict[str, SpecialistResultV1]) -> SpecialistResultV1:
    execution, finding, prerequisite, payload, error = "completed", "unknown", "met", None, None
    if decision is None:
        execution, prerequisite = "skipped", "fixed_decision_unavailable"
    elif name == "configuration":
        payload = {"lines": decision["specialists"]["configuration"],
                   "compatibility": decision["specialists"]["compatibility"]}
        invalid = any(line["status"] != "valid" for line in payload["lines"])
        invalid |= any(item.get("severity") == "blocker" and
                       item.get("status") in ("fail", "unsupported")
                       for item in payload["compatibility"])
        uncertain = any(item.get("status") == "unknown" for item in payload["compatibility"])
        finding = "infeasible" if invalid else "unknown" if uncertain else "confirmed"
    elif name in ("pricing", "fulfillment") and prior["configuration"]["finding"] != "confirmed":
        execution, prerequisite = "skipped", "configuration_not_valid"
    elif name == "credit" and (prior["pricing"]["execution"] != "completed"
                               or prior["pricing"]["finding"] == "unknown"):
        execution, prerequisite = "skipped", "verified_commercial_values_unavailable"
    elif name == "approval_routing":
        required = ("configuration", "pricing", "fulfillment", "credit", "policy")
        payload = dict(decision["specialists"]["approval_routing"])
        payload["roles_available_from_fixed_interface"] = not payload["route_withheld"]
        if any(prior[key]["execution"] != "completed" for key in required):
            payload["route_withheld"] = True
            payload["roles_available_from_fixed_interface"] = False
        finding = "approval_required" if not payload["route_withheld"] else "withheld"
    elif name == "pricing":
        payload = decision["specialists"]["pricing"]
        finding = ("infeasible" if any(h.get("severity") == "blocker" for h in payload["rule_hits"])
                   else "unknown" if payload["cost_evidence_gaps"] else "calculated")
    elif name == "fulfillment":
        payload = decision["specialists"]["availability"]
        statuses = {line["status"] for line in payload}
        if statuses <= {"confirmed_by_date"}:
            finding = "confirmed"
        elif "infeasible" in statuses:
            finding = "infeasible"
        elif statuses & {"conditional", "feasible_uncommitted"}:
            finding = "conditional"
        else:
            finding = "unknown" if statuses & {"unknown", "pending_production_check"} else "needs_revision"
    elif name == "credit":
        payload = decision["specialists"]["credit"]
        finding = ("infeasible" if any(h.get("severity") == "blocker" for h in payload["rule_hits"])
                   else "unknown" if not payload["commitments_fresh"] else "calculated")
    elif name == "policy":
        payload = decision["specialists"]["policy"]
        # Fixed Phase 1C rule hits remain authoritative. Its aggregate interface
        # does not expose a per-rule prerequisite API.
        payload = {**payload, "per_rule_prerequisites_available": False}
        finding = "infeasible" if payload["hard_blocks"] else "evaluated_with_interface_limits"
    else:
        raise ValueError(f"Unknown specialist: {name}")
    return {"version": "1", "specialist": name, "producer_type": "deterministic",
            "assessment_id": assessment_id, "subject_id": pinned.context.original_deal_id,
            "bundle_sha256": pinned.context.bundle_sha256, "execution": execution,
            "finding": finding, "prerequisite": prerequisite, "payload": payload, "error": error}
