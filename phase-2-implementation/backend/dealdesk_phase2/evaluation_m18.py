"""M1.8 evaluation capture and pinned deterministic comparison.

Source cases and reviewer answers are deliberately absent from this module.
Capture is model-blind and records observations; adjudication is a separate,
post-run human-review operation. No business logic is reimplemented here.
"""

import importlib
from pathlib import Path

from .phase1c_adapter import EvidenceMismatch


CAPTURE_VERSION = "m1.8-observation-v1"


def pinned_baseline(adapter, connection_factory, pinned):
    """Use exactly the separately pinned Phase 1C discovery and full verifier."""
    pool = adapter.validate_pinned_context(pinned)
    module = importlib.import_module("phase1c_partial_discovery")
    implementation = (adapter.checkout / "phase-1c-data" / "implementation").resolve()
    if not Path(module.__file__).resolve().is_relative_to(implementation):
        raise EvidenceMismatch("Discovery module was not loaded from the pinned checkout")
    candidate, reason = module.discover_partial_delivery(pool)
    result = {"version": "m1.8-pinned-baseline-v1",
              "run_id": str(pinned.context.phase1c_run_id),
              "deal_id": pinned.context.original_deal_id,
              "bundle_sha256": pinned.context.bundle_sha256,
              "source_input_digest": pinned.context.source_input_digest,
              "discovered": candidate is not None, "reason": reason,
              "candidate": None, "verification": None}
    if candidate is None:
        return result
    checked, decision = adapter.verify_candidate(connection_factory, pinned, candidate)
    trace = checked["candidate_trace"]
    result["candidate"] = {"candidate_id": candidate.candidate_id,
        "slices": [{"line_id": s.line_id, "quantity": str(s.quantity),
                    "delivery_date": s.arrival_date.isoformat(),
                    "evidence_ids": list(s.evidence_ids)} for s in candidate.delivery_slices],
        "evidence_ids": list(candidate.evidence_ids)}
    result["verification"] = {"supply_status": trace["assessment"]["status"],
        "business_status": decision["status"],
        "source_input_digest": trace["source_input_digest"]}
    return result


def capture_trial(case_id: str, state: dict, baseline: dict, *, provider: str,
                  model: str, prompt_version: str) -> dict:
    """Record a trial without loading a reviewer answer or scoring semantics.

    Caller must pass a completed graph checkpoint, not a model-supplied state.
    The two digests and IDs prevent accidentally comparing unlike evidence.
    """
    context = state.get("context", {})
    if (state.get("assessment_id") != context.get("assessment_id")
            or state.get("phase1c_run_id") != context.get("phase1c_run_id")
            or state.get("phase1c_run_id") != baseline.get("run_id")
            or context.get("original_deal_id") != baseline.get("deal_id")
            or context.get("bundle_sha256") != baseline.get("bundle_sha256")
            or context.get("source_input_digest") != baseline.get("source_input_digest")):
        raise EvidenceMismatch("Trial and baseline identities or evidence differ")
    if not state.get("reviewer_package"):
        raise ValueError("Reviewer handoff has not completed")
    ai = state.get("ai_fulfillment_result") or {}
    contribution = ai.get("contribution") or {}
    records = list(state.get("candidate_records", {}).values())
    attempts = state.get("model_attempt_ledger", [])
    completed = [x for x in attempts if x.get("status") == "completed"]
    ledger = state.get("tool_access_ledger", [])
    return {"version": CAPTURE_VERSION, "case_id": case_id,
        "assessment_id": state["assessment_id"], "phase1c_run_id": state["phase1c_run_id"],
        "original_deal_id": context["original_deal_id"],
        "bundle_sha256": context["bundle_sha256"],
        "source_input_digest": context["source_input_digest"],
        "provider": provider, "model": model, "prompt_version": prompt_version,
        "ai_execution": ai.get("execution", "not_run"),
        "contribution_kind": contribution.get("kind"),
        "candidate_status": state.get("candidate_status", "not_started"),
        "candidates": [{"candidate_id": x["candidate_id"], "status": x["status"],
            "proposed_slices": x["proposed_slices"],
            "supply_status": x.get("fixed_supply_status"),
            "business_status": x.get("fixed_business_status"),
            "error": x.get("error")} for x in records],
        "baseline": baseline,
        "raw_rejected_claims": state.get("ai_claim_audit", []),
        "reviewer_package": state["reviewer_package"],
        "tool_calls": sum(bool(x.get("counted")) for x in ledger),
        "tool_access": [{"tool": x.get("tool"), "status": x.get("status"),
                         "returned_refs": x.get("returned_refs", [])} for x in ledger],
        "model_attempts": [{"provider": x.get("provider"), "model": x.get("model"),
            "status": x.get("status"), "usage": x.get("usage"),
            "latency_ms": x.get("latency_ms"), "error_code": x.get("error_code")}
            for x in completed]}


def structural_flags(observation: dict) -> dict:
    """Mechanical signals only; business correctness requires blind review."""
    review = observation["reviewer_package"]
    candidates = observation["candidates"]
    baseline = observation["baseline"]
    verified = [x for x in candidates if x["status"] == "fixed_checked"
                and x["supply_status"] == "supply_supported_unreserved"]
    comparable = (verified[0]["proposed_slices"] if verified else None)
    base = baseline.get("candidate")
    baseline_slices = base["slices"] if base else None
    same_schedule = (comparable is not None and baseline_slices is not None and
                     [(s["quantity"], s["delivery_date"]) for s in comparable] ==
                     [(s["quantity"], s["delivery_date"]) for s in baseline_slices])
    return {"fixed_supported_candidate": bool(verified),
            "baseline_discovered": baseline["discovered"],
            "same_schedule_as_baseline": same_schedule,
            "distinct_value_not_established": True,
            "raw_rejection_count": len(observation["raw_rejected_claims"]),
            "reviewer_candidate_count": len(review.get("candidates", [])),
            "requires_semantic_review": True}


def adjudicate(observation: dict, answer: dict, *, reviewer_id: str) -> dict:
    """Never label developer-authored expectations as accepted ground truth."""
    if answer.get("case_id") != observation["case_id"] or not reviewer_id:
        raise ValueError("Answer identity and reviewer are required")
    if (answer.get("bundle_sha256") != observation["bundle_sha256"]
            or answer.get("source_input_digest") != observation["source_input_digest"]):
        raise EvidenceMismatch("Reviewer answer is not for this evidence")
    status = answer.get("review_status")
    if status not in ("developer_provisional", "human_accepted"):
        raise ValueError("Answer must carry explicit review status")
    if status == "human_accepted" and not answer.get("acceptance_record"):
        raise ValueError("Human acceptance record required")
    return {"case_id": observation["case_id"], "reviewer_id": reviewer_id,
            "answer_status": status, "structural": structural_flags(observation),
            "business_correctness": "requires_reviewer_judgment",
            "critical_failure": "requires_reviewer_judgment"}
