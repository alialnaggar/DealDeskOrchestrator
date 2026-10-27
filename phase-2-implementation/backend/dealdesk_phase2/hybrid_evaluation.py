"""Read-only, model-blind hybrid observation capture and aggregate denominators.

Never load source-reviewed answers or the rule-only baseline into a model.
Capture only completed checkpoints after the run, and keep reviewer judgments
separate from mechanical fixed checks. Raw model responses stay in checkpoints.
"""

import json
from hashlib import sha256

from .hybrid_offline import RUN_VERSION
from .phase1c_adapter import EvidenceMismatch


VERSION = "hybrid-observation-v1"


def _raw_references(attempts):
    """Audit-only bounded extraction; a returned ID is not per-slice support."""
    refs = []
    for attempt in attempts:
        if attempt.get("stage") not in ("final", "revision"):
            continue
        try:
            content = attempt["raw"]["choices"][0]["message"]["content"]
            if not isinstance(content, str) or len(content.encode()) > 16384:
                return None
            payload = json.loads(content)["payload"]
            if not isinstance(payload, dict):
                return None
            slices = payload.get("delivery_slices", [])
            if not isinstance(slices, list) or len(slices) > 2:
                return None
            for item in slices:
                if not isinstance(item, dict) or not isinstance(item.get("source_refs"), list):
                    return None
                if len(item["source_refs"]) > 25 or any(
                        not isinstance(ref, str) or len(ref) > 256
                        for ref in item["source_refs"]):
                    return None
                refs.extend(item["source_refs"])
        except (KeyError, IndexError, TypeError, ValueError):
            return None
    return refs


def capture_hybrid(state: dict, *, baseline: dict | None = None) -> dict:
    """Capture one attempted eligible case; no raw response or answer in output."""
    context, run = state.get("context", {}), state.get("hybrid_execution", {})
    pack, start = state.get("hybrid_evidence_pack", {}), state.get(
        "hybrid_investigation_start", {})
    if (not isinstance(context, dict) or not isinstance(run, dict)
            or not isinstance(pack, dict) or not isinstance(start, dict)
            or run.get("version") != RUN_VERSION or run.get("phase") != "terminal"
            or state.get("assessment_id") != context.get("assessment_id")
            or run.get("assessment_id") != context.get("assessment_id")
            or run.get("pack_sha256") != pack.get("pack_sha256")
            or run.get("start_sha256") != start.get("start_sha256")
            or pack.get("start_sha256") != start.get("start_sha256")
            or any(start.get(k) != context.get(k) for k in (
                "assessment_id", "phase1c_run_id", "bundle_sha256", "source_input_digest"))
            or start.get("subject_id") != context.get("original_deal_id")
            or state.get("phase1c_run_id") != context.get("phase1c_run_id")
            or state.get("reviewer_package", {}).get("assessment_id") != state.get(
                "assessment_id") or state.get("reviewer_package", {}).get(
                "bundle_sha256") != context.get("bundle_sha256")
            or state.get("ai_fulfillment_result") != run.get("result")):
        raise EvidenceMismatch("Hybrid observation checkpoint identity or handoff differs")
    if baseline is not None and (baseline.get("run_id") != state["phase1c_run_id"]
            or baseline.get("deal_id") != context.get("original_deal_id")
            or baseline.get("bundle_sha256") != context.get("bundle_sha256")
            or baseline.get("source_input_digest") != context.get("source_input_digest")):
        raise EvidenceMismatch("Reviewer-only baseline uses different sealed evidence")
    results = state.get("specialist_results", {})
    if set(results) != {"configuration", "pricing", "fulfillment", "credit", "policy",
                        "approval_routing"}:
        raise EvidenceMismatch("Original six responsibility mappings are incomplete")
    ledger = state.get("tool_access_ledger", [])
    completed = [item for item in ledger if item.get("status") == "completed"]
    prefetch_id = sha256((run["start_sha256"] +
        ":trusted_prefetch:inspect_line_supply").encode()).hexdigest()
    returned = {ref for item in completed for ref in item.get("returned_refs", [])}
    attempts = run.get("attempts", [])
    refs = _raw_references(attempts)
    ai = state.get("ai_fulfillment_result", {})
    candidate = list(state.get("candidate_records", {}).values())
    if len(candidate) > 1:
        raise EvidenceMismatch("Hybrid evaluation has multiple candidate records")
    checked = bool(candidate and candidate[0].get("status") == "fixed_checked"
                   and candidate[0].get("fixed_supply_status") == "supply_supported_unreserved"
                   and set(candidate[0].get("specialist_results", {})) == set(results)
                   and state.get("candidate_status") == "fixed_checked")
    usage = [item.get("raw", {}).get("usage") for item in attempts]
    measurable = all(isinstance(item, dict) and all(
        type(item.get(key)) is int and item[key] >= 0
        for key in ("prompt_tokens", "completion_tokens")) for item in usage)
    return {"version": VERSION, "assessment_id": state["assessment_id"],
        "phase1c_run_id": state["phase1c_run_id"],
        "bundle_sha256": context["bundle_sha256"],
        "source_input_digest": context["source_input_digest"],
        "original_review_status": state.get("review_status"),
        "ai_execution": ai.get("execution"), "ai_error": ai.get("error"),
        "contribution_kind": (ai.get("contribution") or {}).get("kind"),
        "attempted_model_requests": len(attempts),
        "attempt_stages": [item.get("stage") for item in attempts],
        "pending_send": run.get("pending") is not None,
        "counted_evidence_tools": sum(bool(x.get("counted")) for x in ledger),
        "completed_evidence_tools": len(completed),
        "model_selected_evidence_tools": sum(bool(x.get("counted")) for x in ledger
            if x.get("call_id") != prefetch_id),
        "raw_citation_access": {"submitted": len(refs),
            "returned": sum(ref in returned for ref in refs),
            "per_slice_support": "requires_pinned_verifier"}
            if refs is not None else None,
        "fixed_checked_candidate": checked,
        "candidate_status": state.get("candidate_status"),
        "candidate_supply_status": candidate[0].get("fixed_supply_status") if candidate else None,
        "reviewer_candidate_count": len(state["reviewer_package"].get("candidates", [])),
        "audit_rejection_count": len(run.get("rejections", [])),
        "audit_rejection_codes": [item.get("code") or item.get("reason", "unknown")
                                  for item in run.get("rejections", [])],
        "latency_ms": sum(item["latency_ms"] for item in attempts)
            if all(type(item.get("latency_ms")) is int for item in attempts) else None,
        "tokens": ({"prompt": sum(item["prompt_tokens"] for item in usage),
                    "completion": sum(item["completion_tokens"] for item in usage)}
                   if measurable else None),
        "baseline_discovered": baseline.get("discovered") if baseline else None,
        "business_quality": "requires_separate_source_first_human_review",
        "human_approval": "not_granted_by_system"}


def summarize_hybrid(observations: list[dict]) -> dict:
    """All attempts, including errors, remain in the denominator."""
    if any(not isinstance(item, dict) or item.get("version") != VERSION
           for item in observations):
        raise ValueError("Incompatible hybrid observation")
    durations = [item["latency_ms"] for item in observations
                 if type(item.get("latency_ms")) is int]
    citations = [item["raw_citation_access"] for item in observations
                 if item.get("raw_citation_access") is not None]
    return {"version": VERSION, "attempted_cases": len(observations),
        "fixed_checked_candidates": sum(bool(x.get("fixed_checked_candidate"))
                                        for x in observations),
        "abstentions": sum(x.get("contribution_kind") == "abstention"
                           for x in observations),
        "errors": sum(x.get("ai_execution") == "error" for x in observations),
        "model_requests": sum(x.get("attempted_model_requests", 0) for x in observations),
        "evidence_tools": sum(x.get("counted_evidence_tools", 0) for x in observations),
        "raw_citation_access": {"submitted": sum(x["submitted"] for x in citations),
                                "returned": sum(x["returned"] for x in citations),
                                "unparseable_cases": len(observations) - len(citations)},
        "latency_ms_observed_cases": len(durations),
        "latency_ms_total_observed": sum(durations),
        "token_usage_observed_cases": sum(x.get("tokens") is not None
                                           for x in observations),
        "prompt_tokens_observed": sum(x["tokens"]["prompt"] for x in observations
                                      if x.get("tokens") is not None),
        "completion_tokens_observed": sum(x["tokens"]["completion"] for x in observations
                                          if x.get("tokens") is not None),
        "baseline_discovered_cases": sum(x.get("baseline_discovered") is True
                                         for x in observations),
        "business_quality": "not_scored_without_independent_review"}
