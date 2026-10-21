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
    original = adapter.fixed_original_decision(pinned)
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
              "original": {"business_status": original["status"],
                           "fulfillment": [{"line_id": x["line_id"],
                                            "status": x["status"],
                                            "requested_quantity": str(x["requested_quantity"]),
                                            "quantity_by_requested_date": str(x["quantity_by_requested_date"])}
                                           for x in original["specialists"]["availability"]]},
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
    if state["reviewer_package"].get("original", {}).get("deal_id") != context["original_deal_id"]:
        raise EvidenceMismatch("Reviewer package original deal differs")
    ai = state.get("ai_fulfillment_result") or {}
    contribution = ai.get("contribution") or {}
    records = list(state.get("candidate_records", {}).values())
    attempts = state.get("model_attempt_ledger", [])
    # The checkpoint ledger has a reservation and (possibly) a terminal row
    # for the same attempt. Keep failures and interrupted reservations too.
    latest_attempts = {}
    for item in attempts:
        latest_attempts[item["attempt_id"]] = item
    ledger = state.get("tool_access_ledger", [])
    return {"version": CAPTURE_VERSION, "case_id": case_id,
        "assessment_id": state["assessment_id"], "phase1c_run_id": state["phase1c_run_id"],
        "original_deal_id": context["original_deal_id"],
        "bundle_sha256": context["bundle_sha256"],
        "source_input_digest": context["source_input_digest"],
        "provider": provider, "model": model, "prompt_version": prompt_version,
        "ai_execution": ai.get("execution", "not_run"),
        "contribution_kind": contribution.get("kind"),
        "validated_contribution": contribution,
        "ai_error": ai.get("error"),
        "original_review_status": state.get("review_status"),
        "stop_reason": state.get("stop_reason"),
        "trace": list(state.get("trace", [])),
        "candidate_status": state.get("candidate_status", "not_started"),
        "candidates": [{"candidate_id": x["candidate_id"], "status": x["status"],
            "proposed_slices": x["proposed_slices"],
            "supply_status": x.get("fixed_supply_status"),
            "business_status": x.get("fixed_business_status"),
            "error": x.get("error")} for x in records],
        "baseline": baseline,
        "raw_rejected_claims": state.get("ai_claim_audit", []),
        "reviewer_package": state["reviewer_package"],
        "reviewer_semantic_error_status": "requires_human_review",
        "tool_calls": sum(bool(x.get("counted")) for x in ledger),
        "tool_access": [{"tool": x.get("tool"), "status": x.get("status"),
                         "arguments": x.get("args"),
                         "evidence_status": x.get("result", {}).get("evidence"),
                         "returned_refs": x.get("returned_refs", []),
                         "identity": x.get("identity")} for x in ledger],
        "model_attempts": [{"attempt_id": x.get("attempt_id"),
            "provider": x.get("provider"), "model": x.get("model"),
            "status": x.get("status"), "usage": x.get("usage"),
            "latency_ms": x.get("latency_ms"), "error_code": x.get("error_code"),
            "response_model": x.get("response_model"),
            "prompt_digest": x.get("prompt_digest"),
            "started_at": x.get("started_at"), "finished_at": x.get("finished_at")}
            for x in latest_attempts.values()]}


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
    cited = {ref for candidate in candidates for sl in candidate["proposed_slices"]
             for ref in sl.get("source_refs", [])}
    returned = {ref for item in observation["tool_access"]
                if item["status"] == "completed" for ref in item["returned_refs"]}
    return {"fixed_supported_candidate": bool(verified),
            "baseline_discovered": baseline["discovered"],
            "same_schedule_as_baseline": same_schedule,
            "distinct_value_not_established": True,
            "raw_rejection_count": len(observation["raw_rejected_claims"]),
            "candidate_citations_returned": cited <= returned,
            "reviewer_candidate_count": len(review.get("candidates", [])),
            "requires_semantic_review": True}


def adjudicate(observation: dict, answer: dict, *, reviewer_id: str,
               judgment: dict | None = None) -> dict:
    """Never label developer-authored expectations as accepted ground truth."""
    if answer.get("case_id") != observation["case_id"] or not reviewer_id:
        raise ValueError("Answer identity and reviewer are required")
    if (answer.get("bundle_sha256") != observation["bundle_sha256"]
            or answer.get("source_input_digest") != observation["source_input_digest"]):
        raise EvidenceMismatch("Reviewer answer is not for this evidence")
    status = answer.get("review_status")
    if status not in ("developer_provisional", "developer_supervisor_accepted",
                      "independent_accepted"):
        raise ValueError("Answer must carry explicit review status")
    record = answer.get("acceptance_record")
    if status != "developer_provisional" and (not isinstance(record, dict)
                                                or not record.get("reviewer_id")
                                                or not record.get("reviewed_at")
                                                or not record.get("source_check")
                                                or record.get("reviewer_id") != reviewer_id):
        raise ValueError("Human acceptance record required")
    if status == "independent_accepted" and not record.get(
            "independent_of_case_author_and_model_output"):
        raise ValueError("Independent review attestation required")
    if judgment is not None:
        if status == "developer_provisional":
            raise ValueError("A provisional answer cannot support a rated trial")
        if set(judgment) != {"business_correctness", "usefulness_vs_baseline",
                             "raw_critical_failures", "surviving_critical_failures", "rationale"}:
            raise ValueError("Trial judgment fields differ")
        if (judgment["business_correctness"] not in ("correct", "incorrect", "uncertain")
                or judgment["usefulness_vs_baseline"] not in
                ("improved", "equivalent", "worse", "not_applicable", "uncertain")
                or not isinstance(judgment["rationale"], str) or not judgment["rationale"].strip()
                or any(not isinstance(judgment[key], list) or
                       any(not isinstance(code, str) or not code.strip() for code in judgment[key])
                       for key in ("raw_critical_failures", "surviving_critical_failures"))):
            raise ValueError("Trial judgment must be explicit and evidence-explained")
    return {"case_id": observation["case_id"], "reviewer_id": reviewer_id,
            "answer_status": status, "structural": structural_flags(observation),
            "business_correctness": (judgment["business_correctness"] if judgment
                                     else "requires_reviewer_judgment"),
            "usefulness_vs_baseline": (judgment["usefulness_vs_baseline"] if judgment
                                       else "requires_reviewer_judgment"),
            "raw_critical_failures": (judgment["raw_critical_failures"] if judgment
                                      else "requires_reviewer_judgment"),
            "surviving_critical_failures": (judgment["surviving_critical_failures"] if judgment
                                            else "requires_reviewer_judgment"),
            "rationale": judgment["rationale"] if judgment else None}
