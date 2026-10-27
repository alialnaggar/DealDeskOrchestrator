"""Model-blind checkpoint capture: quality is not inferred from parseability."""

from copy import deepcopy
from unittest import TestCase

from dealdesk_phase2.hybrid_evaluation import capture_hybrid, summarize_hybrid
from dealdesk_phase2.hybrid_offline import RUN_VERSION
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch


def checkpoint():
    context = {"assessment_id": "A", "phase1c_run_id": "R", "original_deal_id": "D",
               "bundle_sha256": "B", "source_input_digest": "S"}
    result = {"execution": "error", "error": "hybrid_rejected:invalid_binding_shape",
              "contribution": None}
    return {"assessment_id": "A", "phase1c_run_id": "R", "context": context,
        "hybrid_investigation_start": {**context, "subject_id": "D", "start_sha256": "X"},
        "hybrid_evidence_pack": {"start_sha256": "X", "pack_sha256": "P"},
        "hybrid_execution": {"version": RUN_VERSION, "phase": "terminal",
            "assessment_id": "A", "start_sha256": "X", "pack_sha256": "P",
            "pending": None, "result": result, "rejections": [
                {"code": "invalid_binding_shape", "raw": "PRIVATE"}],
            "attempts": [{"stage": "decision", "latency_ms": 1557,
                          "raw": {"usage": {"prompt_tokens": 1173,
                                            "completion_tokens": 483}}},
                         {"stage": "final", "latency_ms": 1986,
                          "raw": {"choices": [{"message": {"content":
                              '{"payload":{"delivery_slices":[{"source_refs":["M18-INV"]}]}}'}}],
                                  "usage": {"prompt_tokens": 1130,
                                            "completion_tokens": 751}}}]},
        "ai_fulfillment_result": result, "review_status": "needs_revision",
        "candidate_status": "not_started", "candidate_records": {},
        "specialist_results": {k: {} for k in ("configuration", "pricing", "fulfillment",
            "credit", "policy", "approval_routing")},
        "tool_access_ledger": [{"status": "completed", "counted": False,
                                "returned_refs": ["inventory:M18-INV"]}],
        "reviewer_package": {"assessment_id": "A", "bundle_sha256": "B",
                             "candidates": []}}


class HybridEvaluationTests(TestCase):
    def test_b01_failure_kept_in_denominator_and_raw_never_projected(self):
        state = checkpoint()
        baseline = {"run_id": "R", "deal_id": "D", "bundle_sha256": "B",
                    "source_input_digest": "S", "discovered": True}
        observed = capture_hybrid(state, baseline=baseline)
        self.assertEqual(observed["attempt_stages"], ["decision", "final"])
        self.assertEqual(observed["tokens"], {"prompt": 2303, "completion": 1234})
        self.assertEqual(observed["latency_ms"], 3543)
        self.assertEqual(observed["raw_citation_access"]["returned"], 0)
        self.assertFalse(observed["fixed_checked_candidate"])
        self.assertNotIn("PRIVATE", str(observed))
        summary = summarize_hybrid([observed])
        self.assertEqual((summary["attempted_cases"], summary["errors"],
                          summary["fixed_checked_candidates"]), (1, 1, 0))
        self.assertEqual(summary["raw_citation_access"]["submitted"], 1)
        self.assertEqual(summary["business_quality"],
                         "not_scored_without_independent_review")

    def test_identity_and_incomplete_handoff_fail_closed(self):
        for field, value in (("phase1c_run_id", "DIFFERENT"),
                             ("reviewer_package", {}),
                             ("ai_fulfillment_result", {"execution": "completed"})):
            with self.subTest(field=field):
                changed = deepcopy(checkpoint())
                changed[field] = value
                with self.assertRaises(EvidenceMismatch):
                    capture_hybrid(changed)
        with self.assertRaises(EvidenceMismatch):
            capture_hybrid(checkpoint(), baseline={"run_id": "wrong"})

    def test_missing_usage_is_unknown_and_zero_cases_have_no_false_rate(self):
        changed = checkpoint()
        del changed["hybrid_execution"]["attempts"][0]["raw"]["usage"]
        observed = capture_hybrid(changed)
        self.assertIsNone(observed["tokens"])
        self.assertEqual(summarize_hybrid([observed])["token_usage_observed_cases"], 0)
        self.assertEqual(summarize_hybrid([])["attempted_cases"], 0)
        with self.assertRaises(ValueError):
            summarize_hybrid([{"version": "unknown"}])
