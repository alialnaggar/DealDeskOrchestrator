"""Reproducible development-only six-specialist checkpoint observations."""

from copy import deepcopy
import os
from pathlib import Path
import unittest
from uuid import uuid4

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from dealdesk_phase2.week3_development import capture_original_development
from dealdesk_phase2.week3_offline import run_week3_offline
from m18_case_setup import CASES, install_disposable_cases
from run_week3_development import disposable_pair, run_development, report
from test_week3_offline import models

try:
    import psycopg
except ImportError:
    psycopg = None


class RunnerSafety(unittest.TestCase):
    def test_cli_disposable_database_pair_only(self):
        good = [("recovery_123_m20", "/tmp/opencode/dealdesk-test-pgdata"),
                ("recovery_123_m20_checkpoint", "/tmp/opencode/dealdesk-test-pgdata")]
        self.assertTrue(disposable_pair(good))
        for pair in ([], [good[0], good[0]],
                     [good[0], ("shared_checkpoint", good[1][1])],
                     [(good[0][0], "/var/lib/postgresql/data"), good[1]]):
            with self.subTest(pair=pair):
                self.assertFalse(disposable_pair(pair))


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Disposable pinned PostgreSQL fixtures required")
class SixSpecialistDevelopment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["M20_DATABASE_URL"]))
        with cls.connect() as conn:
            if not conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE "
                                "'M18-D-%'").fetchone()[0]:
                install_disposable_cases(conn)

    def test_three_distinct_cases_source_bound_faults_and_replay(self):
        dsn = os.environ["M20_CHECKPOINT_DATABASE_URL"]
        result = run_development(self.connect, dsn, self.adapter)
        self.assertEqual(result["summary"]["scenarios"], 3)
        self.assertEqual(result["summary"]["fixed_results"], 18)
        self.assertEqual(result["summary"]["accepted_answer_accuracy"], None)
        self.assertEqual(result["summary"]["fulfillment_contribution_abstentions"], 2)
        self.assertEqual(result["provider_requests"], 0)
        by_id = {case["case_id"]: case for case in result["scenarios"]}
        self.assertEqual(set(by_id), {"M18-D-B01", "M18-D-B05", "M18-D-N03"})
        self.assertEqual(by_id["M18-D-B01"]["offline_ai"]["credit"]["execution"],
                         "completed")
        self.assertEqual(by_id["M18-D-B05"]["offline_ai"]["credit"]["execution"],
                         "error")
        self.assertEqual(by_id["M18-D-B05"]["offline_ai"]["credit"][
            "validated_claims"], [])
        self.assertEqual(by_id["M18-D-B05"]["offline_ai"]["policy"]["execution"],
                         "abstained")
        self.assertEqual(by_id["M18-D-N03"]["offline_ai"]["fulfillment"][
            "execution"], "skipped")
        self.assertEqual(by_id["M18-D-N03"]["offline_ai"]["policy"]["execution"],
                         "error")
        self.assertTrue(all(x["candidate_status"] == "not_started" and x[
            "human_approval"] == "not_granted_by_system" for x in result["scenarios"]))
        self.assertIn("0 independently accepted answer labels", report(result))
        # A fresh set of doubles may read already completed checkpoints but
        # may not generate another attempt, tool record or contradictory result.
        self.assertEqual(run_development(self.connect, dsn, self.adapter), result)
        with thesis_checkpointer(dsn) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            case = by_id["M18-D-B01"]
            state = graph.get_state({"configurable": {"thread_id": case[
                "assessment_id"]}}).values
            changed = deepcopy(state)
            changed["m21_ai_results"]["credit"]["validated_claims"][0]["ref"] = (
                "credit_profile:INVENTED")
            with self.assertRaises(EvidenceMismatch):
                capture_original_development(changed, self.adapter)
            changed = deepcopy(state)
            changed["m21_ai_results"]["credit"]["validated_claims"][0]["value"] = (
                "fabricated")
            with self.assertRaises(EvidenceMismatch):
                capture_original_development(changed, self.adapter)
            changed = deepcopy(state)
            changed["specialist_results"]["credit"]["finding"] = "approved"
            with self.assertRaises(EvidenceMismatch):
                capture_original_development(changed, self.adapter)
            changed = deepcopy(state)
            changed["context"]["source_input_digest"] = "0" * 64
            with self.assertRaises(EvidenceMismatch):
                capture_original_development(changed, self.adapter)
            changed = deepcopy(state)
            changed["typed_final_hosted_start"] = {"unexpected": True}
            with self.assertRaises(EvidenceMismatch):
                capture_original_development(changed, self.adapter)

    def test_real_graph_synthetic_failure_does_not_change_fixed_results(self):
        # Distinct ID keeps this fault injection separate from development
        # cohort and from the provisional 36 answer packets.
        case = next(x for x in CASES if x.case_id == "B01")
        name = "DEV-W3-FAULT-" + uuid4().hex
        config = {"configurable": {"thread_id": name}}
        fulfillment = OfflineModelDouble(({"type": "contribution", "value": {
            "kind": "abstention", "payload": {"reason": "No supportable suggestion",
                "uncertainty_reasons": ["No binding evidence"]}}},))
        m20, m21 = models(adverse=True)
        with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            state = run_week3_offline(graph, config, self.adapter, fulfillment, m20, m21,
                assessment_id=name, run_id=case.run_id)
            captured = capture_original_development(state, self.adapter)
            self.assertEqual(captured["offline_ai"]["credit"]["execution"], "error")
            self.assertEqual(captured["offline_ai"]["policy"]["execution"], "abstained")
            self.assertEqual(captured["offline_ai"]["approval_routing"]["execution"],
                             "completed")
            self.assertEqual(captured["deterministic_baseline"]["specialists"]["credit"][
                "execution"], "completed")
            self.assertNotEqual(captured["deterministic_baseline"]["review_status"],
                                "approved")


if __name__ == "__main__":
    unittest.main()
