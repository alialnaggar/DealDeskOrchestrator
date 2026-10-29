"""Source-checked engineering observations, never independent answer labels.

The existing Week 3 LangGraph performs all execution. This module only reads
its completed original checkpoint and emits a bounded development record.
No reference answers or reviewer drafts are imported or sent to a model.
"""

from .evidence_bundle import unseal
from .fixed_specialists import domain_result
from .graph_state import SPECIALISTS, pinned_from_state, validate_result
from .m20_specialists import TOOLS as M20_TOOLS
from .m21_specialists import TOOLS as M21_TOOLS
from .phase1c_adapter import PHASE1C_COMMIT, EvidenceMismatch


VERSION = "week3-six-specialist-development-v1"


def capture_original_development(state: dict, adapter) -> dict:
    """Separate fixed authority from mock AI observations, failing closed."""
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    fixed = state.get("specialist_results", {})
    m20, m21 = state.get("m20_ai_results", {}), state.get("m21_ai_results", {})
    fulfillment = state.get("ai_fulfillment_result", {})
    review = state.get("reviewer_package", {})
    if (state.get("stop_reason") or set(fixed) != set(SPECIALISTS)
            or set(m20) != set(M20_TOOLS) or set(m21) != set(M21_TOOLS)
            or not fulfillment or state.get("candidate_status") != "not_started"
            or state.get("typed_final_hosted_start") or state.get("m20_hosted_owner")
            or state.get("m21_hosted_owner") or state.get("typed_final_protocol")
            or any(review.get(k) is None for k in ("m20_ai", "m21_ai"))
            or review["m20_ai"] != state.get("m20_review")
            or review["m21_ai"] != state.get("m21_review")
            or review.get("assessment_id") != ctx.assessment_id
            or review.get("bundle_sha256") != ctx.bundle_sha256):
        raise EvidenceMismatch("Week 3 development needs completed original-only offline handoff")
    decision = unseal(state["fixed_decision"], state["fixed_decision_sha256"])
    if decision.get("deal_id") != ctx.original_deal_id or str(decision.get(
            "run_id")) != str(ctx.phase1c_run_id):
        raise EvidenceMismatch("Week 3 development fixed decision identity changed")
    reconstructed = {}
    for name in SPECIALISTS:
        validate_result(fixed[name], state, name)
        expected = domain_result(name, pinned, decision, ctx.assessment_id, reconstructed)
        if name == "approval_routing" and state["review_status"] != "approval_required":
            expected["payload"]["route_withheld"] = True
            expected["payload"]["roles_available_from_fixed_interface"] = False
            expected["finding"] = "withheld"
        if fixed[name] != expected:
            raise EvidenceMismatch("Week 3 fixed result differs from pinned decision mapping")
        reconstructed[name] = expected
    original = review.get("original", {})
    if (original.get("deal_id") != ctx.original_deal_id
            or original.get("run_id") != str(ctx.phase1c_run_id)
            or original.get("review_status") != state["review_status"]
            or original.get("specialists") != {name: {
                "execution": fixed[name]["execution"], "finding": fixed[name]["finding"]}
                for name in SPECIALISTS}
            or review.get("candidates") != []
            or review.get("candidate_workflow_status") != "not_started"
            or review.get("reviewer_action") != (
                "Human review required; no approval, reservation or delivery promise")):
        raise EvidenceMismatch("Week 3 reviewer handoff differs from fixed original")
    ledger = state.get("tool_access_ledger", [])
    if not isinstance(ledger, list):
        raise EvidenceMismatch("Week 3 development tool ledger changed")
    refs = {name: set() for name in SPECIALISTS}
    exposed = {name: {} for name in SPECIALISTS}
    events = []
    for item in ledger:
        identity = item.get("identity", {})
        name = identity.get("specialist")
        if (name not in refs or identity.get("assessment_id") != ctx.assessment_id
                or identity.get("phase1c_run_id") != str(ctx.phase1c_run_id)
                or identity.get("subject_id") != ctx.original_deal_id
                or identity.get("bundle_sha256") != ctx.bundle_sha256
                or identity.get("source_input_digest") != ctx.source_input_digest
                or item.get("status") not in ("reserved", "completed", "budget_exhausted")):
            raise EvidenceMismatch("Week 3 development tool identity changed")
        if item["status"] == "completed":
            refs[name].update(item.get("returned_refs", []))
            for row in item.get("result", {}).get("records", []):
                if row.get("ref") in refs[name]:
                    exposed[name][row["ref"]] = row.get("fields", {})
        events.append({"specialist": name, "tool": item["tool"],
            "status": item["status"], "counted": item.get("counted") is True,
            "returned_refs": list(item.get("returned_refs", []))})

    ai = {}
    for name, result in {**m20, **m21}.items():
        if (result.get("specialist") != name or result.get("producer_type") != "AI"
                or result.get("provider") != "offline_double"
                or result.get("assessment_id") != ctx.assessment_id
                or result.get("phase1c_run_id") != str(ctx.phase1c_run_id)
                or result.get("subject_id") != ctx.original_deal_id
                or result.get("bundle_sha256") != ctx.bundle_sha256
                or result.get("source_input_digest") != ctx.source_input_digest
                or result.get("execution") not in (
                    "completed", "skipped", "abstained", "error")):
            raise EvidenceMismatch("Week 3 development AI result identity changed")
        claims = result.get("validated_claims", [])
        if (not isinstance(claims, list) or result["execution"] != "completed" and claims
                or any(not isinstance(claim, dict) or claim.get("ref") not in refs[name]
                    or not isinstance(claim.get("field"), str)
                    or claim["field"] not in exposed[name].get(claim["ref"], {})
                    or type(claim.get("value")) is not type(exposed[name][claim["ref"]][
                        claim["field"]]) or claim["value"] != exposed[name][claim["ref"]][
                        claim["field"]] for claim in claims)):
            raise EvidenceMismatch("Week 3 development unsupported AI claim")
        ai[name] = {"execution": result["execution"], "reason": result.get("reason"),
            "validated_claims": [{"ref": c["ref"], "field": c["field"]} for c in claims],
            "model_turns": result.get("model_turns"), "tool_calls": result.get("tool_calls"),
            "provider": result.get("provider"), "model": result.get("model"),
            "prompt_version": result.get("prompt_version"), "contract_version": result.get("version")}
    if (fulfillment.get("provider") not in (None, "offline_double")
            or fulfillment.get("execution") not in ("skipped", "completed", "error")
            or fulfillment.get("execution") != "skipped" and (
                fulfillment.get("assessment_id") != ctx.assessment_id
                or fulfillment.get("phase1c_run_id") != str(ctx.phase1c_run_id)
                or fulfillment.get("subject_id") != ctx.original_deal_id
                or fulfillment.get("bundle_sha256") != ctx.bundle_sha256)
            or fulfillment.get("execution") == "skipped" and (
                fulfillment.get("assessment_id") not in (None, ctx.assessment_id)
                or fulfillment.get("bundle_sha256") not in (None, ctx.bundle_sha256))):
        raise EvidenceMismatch("Week 3 development fulfillment identity changed")
    ai["fulfillment"] = {"execution": fulfillment["execution"],
        "reason": fulfillment.get("reason") or fulfillment.get("error"),
        "contribution_kind": (fulfillment.get("contribution") or {}).get("kind"),
        "validated_claims": [], "model_turns": None, "tool_calls": None}
    return {"version": VERSION, "case_id": ctx.original_deal_id,
        "assessment_id": ctx.assessment_id, "phase1c_pin": PHASE1C_COMMIT,
        "phase1c_run_id": str(ctx.phase1c_run_id), "bundle_sha256": ctx.bundle_sha256,
        "source_input_digest": ctx.source_input_digest,
        "as_of_at": ctx.as_of_at.isoformat(), "data_snapshot_ref": ctx.data_snapshot_ref,
        "fixed_decision_sha256": state["fixed_decision_sha256"],
        "deterministic_baseline": {"decision_status": decision["status"],
            "review_status": state["review_status"], "specialists": {
                name: {"execution": fixed[name]["execution"],
                    "finding": fixed[name]["finding"],
                    "prerequisite": fixed[name]["prerequisite"]} for name in SPECIALISTS}},
        "offline_ai": ai, "tool_trace": events,
        "attempts": {"m20": [{"specialist": x.get("specialist"),
            "ordinal": x.get("ordinal"), "status": x.get("status")}
            for x in state.get("m20_model_attempts", [])],
            "m21": [{"specialist": x.get("specialist"),
                "ordinal": x.get("ordinal"), "status": x.get("status")}
                for x in state.get("m21_model_attempts", [])]},
        "trace": list(state.get("trace", [])),
        "fulfillment_claim_audit_records": len(state.get("ai_claim_audit", [])),
        "candidate_status": state["candidate_status"],
        "reviewer_action": review["reviewer_action"],
        "human_approval": "not_granted_by_system",
        "ground_truth": "none_accepted_development_diagnostic_only",
        "hosted_model_quality": "not_measured_offline_doubles"}
