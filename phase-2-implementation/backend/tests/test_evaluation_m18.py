"""M1.8 engineering tests, not evidence of live model business accuracy."""

import os
from pathlib import Path
import unittest

from dealdesk_phase2.evaluation_m18 import (adjudicate, capture_trial,
                                             pinned_baseline, structural_flags)
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None

DB_READY = bool(psycopg and os.getenv("DATABASE_URL") and
                os.getenv("DEALDESK_PHASE1C_CHECKOUT"))


def observation():
    baseline = {"run_id": "R", "deal_id": "D", "bundle_sha256": "H",
        "source_input_digest": "S", "discovered": True,
        "candidate": {"slices": [{"quantity": "8", "delivery_date": "2026-09-04"},
                                  {"quantity": "2", "delivery_date": "2026-09-08"}]}}
    state = {"assessment_id": "A", "phase1c_run_id": "R",
        "context": {"assessment_id": "A", "phase1c_run_id": "R",
                    "original_deal_id": "D", "bundle_sha256": "H",
                    "source_input_digest": "S"},
        "reviewer_package": {"candidates": [], "original": {"deal_id": "D"}},
        "ai_fulfillment_result": {"execution": "completed", "contribution": {"kind": "abstention"}},
        "ai_claim_audit": [{"original_claim": "unsupported", "reason": "not_returned"}],
        "tool_access_ledger": [{"counted": True, "tool": "inspect_fulfillment_paths",
                                "status": "completed", "returned_refs": ["inventory:X"]}]}
    return state, baseline


class CaptureTests(unittest.TestCase):
    def test_cases_distinct_and_separately_classified(self):
        self.assertEqual((sum(x.case_id.startswith("B") for x in CASES),
                          sum(x.case_id.startswith("N") for x in CASES)), (5, 4))
        self.assertEqual(len({x.run_id for x in CASES}), len(CASES))
        self.assertEqual(len({x.ids()["P"] for x in CASES}), len(CASES))
        self.assertGreaterEqual(len({(x.quantity, x.requested_date, x.stock_total,
                                     x.inbound_date, x.partial_allowed) for x in CASES}), 7)

    def test_capture_is_model_blind_and_requires_matching_evidence(self):
        state, baseline = observation()
        captured = capture_trial("B01", state, baseline,
                                 provider="offline_double", model="scripted",
                                 prompt_version="none")
        self.assertEqual(captured["tool_calls"], 1)
        self.assertEqual(captured["raw_rejected_claims"], state["ai_claim_audit"])
        self.assertNotIn("answer", str(captured).lower())
        self.assertTrue(structural_flags(captured)["requires_semantic_review"])
        with self.assertRaises(EvidenceMismatch):
            capture_trial("B01", state, {**baseline, "bundle_sha256": "wrong"},
                          provider="offline_double", model="scripted", prompt_version="none")
        with self.assertRaises(ValueError):
            capture_trial("B01", {**state, "reviewer_package": {}}, baseline,
                          provider="offline_double", model="scripted", prompt_version="none")

    def test_scoring_never_infers_quality_or_acceptance_from_json(self):
        state, baseline = observation()
        captured = capture_trial("B01", state, baseline, provider="offline_double",
                                 model="scripted", prompt_version="none")
        answer = {"case_id": "B01", "bundle_sha256": "H", "source_input_digest": "S",
                  "review_status": "developer_provisional"}
        scored = adjudicate(captured, answer, reviewer_id="engineering")
        self.assertEqual(scored["business_correctness"], "requires_reviewer_judgment")
        self.assertEqual(scored["answer_status"], "developer_provisional")
        with self.assertRaises(ValueError):
            adjudicate(captured, {**answer, "review_status": "human_accepted"},
                       reviewer_id="engineering")
        with self.assertRaises(EvidenceMismatch):
            adjudicate(captured, {**answer, "source_input_digest": "wrong"},
                       reviewer_id="engineering")

    def test_structural_comparison_cannot_claim_added_value(self):
        state, baseline = observation()
        state["candidate_records"] = {"C": {"candidate_id": "C", "status": "fixed_checked",
            "fixed_supply_status": "supply_supported_unreserved", "fixed_business_status": "needs_revision",
            "proposed_slices": [{"quantity": "8", "delivery_date": "2026-09-04"},
                                {"quantity": "2", "delivery_date": "2026-09-08"}]}}
        captured = capture_trial("B01", state, baseline, provider="offline_double",
                                 model="scripted", prompt_version="none")
        flags = structural_flags(captured)
        self.assertTrue(flags["same_schedule_as_baseline"])
        self.assertTrue(flags["distinct_value_not_established"])
        self.assertFalse(flags["requires_semantic_review"] is False)


@unittest.skipUnless(DB_READY, "Requires exact separate Phase 1C and disposable PostgreSQL")
class PinnedEvaluationCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        with cls.connect() as conn:
            existing = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals WHERE "
                                    "deal_id='D-stock_then_confirmed_receipt')").fetchone()[0]
            if not existing:
                raise RuntimeError("Pinned reference fixture missing")
        install_disposable_cases(cls.connect())

    @staticmethod
    def connect():
        return psycopg.connect(os.environ["DATABASE_URL"])

    def test_all_disposable_sources_are_isolated_and_baseline_reproducible(self):
        hashes = set()
        for case in CASES:
            with self.subTest(case=case.case_id):
                pinned = self.adapter.read_original(self.connect, case.run_id,
                                                     "M18-" + case.case_id)
                pool = self.adapter.validate_pinned_context(pinned)
                self.assertEqual(pool["deal"]["deal_id"], case.ids()["D"])
                self.assertEqual(pool["lines"][0]["product_id"], case.ids()["P"])
                self.assertNotIn(pinned.context.bundle_sha256, hashes)
                hashes.add(pinned.context.bundle_sha256)
                baseline = pinned_baseline(self.adapter, self.connect, pinned)
                self.assertEqual(baseline, pinned_baseline(self.adapter, self.connect, pinned))
                self.assertEqual(baseline["source_input_digest"], pinned.context.source_input_digest)
                if case.case_id.startswith("B"):
                    self.assertTrue(baseline["discovered"], baseline)
                    self.assertEqual(baseline["verification"]["supply_status"],
                                     "supply_supported_unreserved", baseline)
                    self.assertEqual(baseline["verification"]["business_status"],
                                     "needs_revision", baseline)
                    self.assertEqual(sum(int(s["quantity"]) for s in
                                         baseline["candidate"]["slices"]), case.quantity)
                    self.assertTrue(all(set(s["evidence_ids"]) <=
                                        {case.ids()["INV"], case.ids()["IN"]} for s in
                                        baseline["candidate"]["slices"]))
                else:
                    self.assertFalse(baseline["discovered"], baseline)
                    self.assertIsNone(baseline["verification"])

    def test_reader_unchanged_and_wrong_source_context_rejected(self):
        case = CASES[0]
        pinned = self.adapter.read_original(self.connect, case.run_id, "M18-ISOLATION")
        baseline = pinned_baseline(self.adapter, self.connect, pinned)
        self.assertEqual(baseline["deal_id"], case.ids()["D"])
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM deal_desk.agent_execution_log "
                                          "WHERE run_id=%s", (case.run_id,)).fetchone()[0], 0)
        other = self.adapter.read_original(self.connect, CASES[1].run_id, "M18-OTHER")
        with self.assertRaises(EvidenceMismatch):
            capture_trial(case.case_id, {"assessment_id": "A", "phase1c_run_id": str(case.run_id),
                "context": {"assessment_id": "A", "phase1c_run_id": str(case.run_id),
                            "original_deal_id": case.ids()["D"],
                            "bundle_sha256": other.context.bundle_sha256,
                            "source_input_digest": other.context.source_input_digest},
                "reviewer_package": {"original": {"deal_id": case.ids()["D"]}}},
                baseline, provider="offline_double", model="scripted", prompt_version="none")


if __name__ == "__main__":
    unittest.main()
