"""Post-run, model-blind comparison; never imported by specialist senders.

An independent reviewer must accept the separate source-first answer file.
Agreement here means only exact declared labels, not semantic superiority.
"""

import json
from .graph_state import SPECIALISTS
from .m22_registry import _digest
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT

VERSION = "m22-source-first-offline-score-v1"
HUMAN = "Human review required; no approval, reservation or delivery promise"


def score_campaign(registry, observations, baselines, answers):
    """Fail closed before reading any per-case result on unapproved answer sets."""
    if (type(registry) is not dict or type(observations) is not dict or
            type(baselines) is not dict or type(answers) is not dict or
            registry.get("phase1c_pin") != PHASE1C_COMMIT or
            answers.get("version") != "m22-source-first-answers-v1" or
            answers.get("status") != "independent_accepted" or
            answers.get("phase1c_pin") != PHASE1C_COMMIT or
            answers.get("manifest_sha256") != registry.get("manifest_sha256") or
            type(answers.get("acceptance")) is not dict or
            not all(answers["acceptance"].get(k) for k in (
                "reviewer_id", "accepted_at", "independent_source_check",
                "answer_sha256")) or
            answers["acceptance"].get("independent_source_check") is not True or
            type(answers.get("cases")) is not dict or
            answers["acceptance"]["answer_sha256"] != _digest(answers["cases"])):
        raise EvidenceMismatch("Independent source-first answer acceptance unavailable")
    rows = registry.get("cases")
    if (type(rows) is not list or not rows or
            set(answers["cases"]) != {r["case_id"] for r in rows} or
            set(observations) - set(answers["cases"]) or
            set(baselines) - set(answers["cases"])):
        raise EvidenceMismatch("Answer/campaign membership differs")
    result = []
    for row in rows:
        cid = row["case_id"]
        answer = answers["cases"][cid]
        if (type(answer) is not dict or
                any(answer.get(k) != row.get(k) for k in (
                    "assessment_id", "original_deal_id", "phase1c_run_id",
                    "bundle_sha256", "source_input_digest")) or
                any(type(answer.get(k)) is not str or not answer[k] for k in (
                    "bundle_sha256", "source_input_digest", "phase1c_run_id")) or
                type(answer.get("fixed_findings")) is not dict or
                set(answer["fixed_findings"]) != set(SPECIALISTS) or
                type(answer.get("acceptable_ai_execution")) is not dict or
                set(answer["acceptable_ai_execution"]) != set(SPECIALISTS) or
                any(type(v) is not list or not v or set(v) - {
                    "completed", "abstained", "skipped"} for v in
                    answer["acceptable_ai_execution"].values()) or
                answer.get("expected_review_status") not in (
                    "approval_required", "blocked", "needs_revision", "unknown") or
                answer.get("candidate_allowed") not in ("yes", "no", "unknown") or
                answer.get("candidate_comparison") not in (
                    "eligible", "excluded", "unsupported")):
            raise EvidenceMismatch("Six-domain accepted answer contract differs")
        obs = observations.get(cid)
        if obs is None:
            result.append({"case_id": cid, "cohort": row["cohort"],
                "status": "missing_observation", "specialists": None,
                "end_to_end": "not_assessable", "baseline": "not_compared"})
            continue
        if row.get("preflight") != "eligible" or row.get("status") in (
                "scheduled_unobserved", "eligible_not_executed", "ineligible",
                "source_preflight_failed"):
            raise EvidenceMismatch("Observation supplied for unstarted or excluded case")
        if (type(obs) is not dict or obs.get("version") != "m22-checkpoint-observation-v1" or
                any(obs.get(k) != answer.get(k) for k in (
                "assessment_id", "original_deal_id", "bundle_sha256")) or
                any(obs.get(k) != answer.get(k) for k in (
                    "phase1c_run_id", "source_input_digest")) or
                type(obs.get("fixed_original")) is not dict or
                type(obs.get("ai_original")) is not dict or
                set(obs["fixed_original"]) != set(SPECIALISTS) or
                set(obs["ai_original"]) != set(SPECIALISTS)):
            raise EvidenceMismatch("Observation differs from accepted source")
        specialist = {}
        for name in SPECIALISTS:
            fixed = obs["fixed_original"][name]
            ai = obs["ai_original"][name]
            specialist[name] = {"fixed_agreement": fixed.get("finding") ==
                answer["fixed_findings"][name],
                "ai_execution": ai.get("execution") if type(ai) is dict else None,
                "ai_execution_agreement": (ai.get("execution") in answer[
                    "acceptable_ai_execution"][name] if type(ai) is dict else None),
                "semantic_judgment": "requires_independent_case_adjudication"}
        review = obs.get("review", {})
        human = type(review) is dict and review.get("action") == HUMAN and (
            obs.get("candidate_id") is None or review.get("customer_acceptance") == "pending")
        review_agreement = type(review) is dict and review.get("status") == answer[
            "expected_review_status"]
        candidate_agreement = (None if answer["candidate_allowed"] == "unknown" else
            (obs.get("candidate_id") is not None) == (answer["candidate_allowed"] == "yes"))
        # Label agreement is not a human decision or proof of semantic value.
        end_to_end = ("not_assessable" if candidate_agreement is None or
            any(item["ai_execution_agreement"] is None for item in specialist.values())
            else "label_agreement" if human and review_agreement and candidate_agreement and
            all(item["fixed_agreement"] and item["ai_execution_agreement"] for item in
                specialist.values()) else "label_disagreement")
        baseline = baselines.get(cid)
        eligibility = answer["candidate_comparison"]
        if eligibility != "eligible":
            comparison = eligibility
        elif baseline is None:
            comparison = "missing_baseline"
        elif (type(baseline) is not dict or
                baseline.get("version") != "m1.8-pinned-baseline-v1" or
                any((baseline.get(k) != obs.get(v))
                 for k,v in (("run_id", "phase1c_run_id"), ("deal_id", "original_deal_id"),
                             ("bundle_sha256", "bundle_sha256"),
                             ("source_input_digest", "source_input_digest")))):
            raise EvidenceMismatch("Baseline and AI source/case mismatch")
        else:
            comparison = ("matched_candidate" if baseline.get("candidate") and
                obs.get("candidate_id") else "matched_no_candidate" if not baseline.get(
                "candidate") and not obs.get("candidate_id") else "different_candidate_presence")
        result.append({"case_id": cid, "cohort": row["cohort"],
            "status": row["status"], "specialists": specialist,
            "human_review_boundary": human,
            "review_status_agreement": review_agreement,
            "candidate_presence_agreement": candidate_agreement,
            "end_to_end": end_to_end,
            "baseline": comparison})
    by_cohort = {cohort: {
        "scheduled": sum(r["cohort"] == cohort for r in result),
        "missing_observations": sum(r["cohort"] == cohort and
            r["status"] == "missing_observation" for r in result),
        "unsupported_comparisons": sum(r["cohort"] == cohort and
            r["baseline"] == "unsupported" for r in result)}
        for cohort in sorted({r["cohort"] for r in result})}
    return {"version": VERSION, "campaign_id": registry["campaign_id"],
        "answer_version": answers["version"], "manifest_sha256": registry["manifest_sha256"],
        "synthetic_fixture": answers.get("synthetic_fixture") is True,
        "formal_accuracy": None, "cases": result,
        "denominators": registry["counts"],
        "by_cohort": by_cohort,
        "missing_observations": sum(r["status"] == "missing_observation" for r in result),
        "unsupported_comparisons": sum(r["baseline"] == "unsupported" for r in result)}


def reports(result):
    """Return machine-readable JSON and safe, compact human-readable Markdown."""
    if result.get("version") != VERSION:
        raise EvidenceMismatch("Scoring report version differs")
    text = ["# M2.2 source-first comparison (post-run)", "",
        f"Campaign: `{result['campaign_id']}`", "Formal accuracy: unavailable",
        f"Scheduled: {result['denominators']['scheduled']}",
        f"Missing observations: {result['missing_observations']}",
        f"Unsupported baseline comparisons: {result['unsupported_comparisons']}", "",
        "| Case | Cohort | Outcome | Baseline |", "| --- | --- | --- | --- |"]
    for row in result["cases"]:
        # All display strings are allowlisted or escape Markdown delimiters.
        safe = [str(row[k]).replace("|", "\\|").replace("\n", " ")
                for k in ("case_id", "cohort", "end_to_end", "baseline")]
        text.append("| " + " | ".join(safe) + " |")
    return json.dumps(result, sort_keys=True, indent=2) + "\n", "\n".join(text) + "\n"
