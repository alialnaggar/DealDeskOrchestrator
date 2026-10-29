"""Engineering metrics and separate original/candidate PostgreSQL boundaries."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases
from run_week4_development import _candidate_record, report, run, summarize
from run_week4_disposable import require_disposable_cluster

try:
    import psycopg
except ImportError:
    psycopg = None


class CalculationTests(unittest.TestCase):
    def test_disposable_cluster_guard_rejects_other_hosts_before_connection(self):
        for dsn in ("host=localhost dbname=postgres", "host=/tmp/opencode dbname=deals",
                    "dbname=postgres", "host=/var/run/postgresql dbname=postgres"):
            with self.subTest(dsn=dsn), self.assertRaises(ValueError):
                require_disposable_cluster(dsn)

    def test_sample_digest_covers_structural_result_not_nondeterministic_timing(self):
        artifact = Path(__file__).resolve().parents[2] / "evaluation" / "week4-offline-development.json"
        if not artifact.exists():
            self.skipTest("Committed sample artifact not yet generated")
        result = json.loads(artifact.read_text())
        stable = {k: v for k, v in result.items() if k not in (
            "stable_result_sha256", "timing_diagnostics", "disposable_setup")}
        encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(sha256(encoded).hexdigest(), result["stable_result_sha256"])
        self.assertEqual(result["summary"], summarize(result["scenarios"],
                                                        result["isolated_candidate"]))
        self.assertNotIn("answer_key", artifact.read_text())

    def test_counts_do_not_equate_execution_with_a_finding(self):
        def observation(name, execution, kind, discovered):
            ai = {key: {"execution": "skipped", "validated_claims": [],
                        "contribution_kind": None} for key in (
                "configuration", "pricing", "fulfillment", "credit", "policy",
                "approval_routing")}
            ai["fulfillment"].update(execution=execution, contribution_kind=kind)
            return {"case_id": name, "assessment_id": "A" + name,
                "bundle_sha256": "hash" + name, "candidate_status": "not_started",
                "offline_ai": ai, "tool_trace": [], "attempts": {"m20": [], "m21": []},
                "fixed_discovery": {"discovered": discovered},
                "deterministic_baseline": {"specialists": {
                    key: {"execution": "completed"} for key in ai}}}
        cases = [observation("B01", "completed", "abstention", True),
                 observation("N01", "skipped", None, False)]
        candidate = {"case_id": "B01", "candidate_status": "fixed_checked",
            "fixed_supply_status": "supply_supported_unreserved",
            "baseline_fixed_supply_status": "supply_supported_unreserved",
            "fixed_rechecks": {key: {} for key in cases[0]["offline_ai"]},
            "citations_returned": True}
        total = summarize(cases, candidate)
        self.assertEqual(total["fulfillment_contribution_kinds"], {
            "None": 1, "abstention": 1})
        self.assertEqual(total["offline_ai_execution"], {"completed": 1, "skipped": 11})
        self.assertEqual(total["validated_claims"], 0)
        self.assertIsNone(total["accepted_answer_accuracy"])
        for invalid in ([cases[0], deepcopy(cases[0])],
                        [{**cases[0], "candidate_status": "fixed_checked"}, cases[1]]):
            with self.assertRaises(EvidenceMismatch):
                summarize(invalid, candidate)
        with self.assertRaises(EvidenceMismatch):
            summarize(cases, {**candidate, "baseline_fixed_supply_status": "unknown"})


@unittest.skipUnless(psycopg and all(os.getenv(key) for key in (
    "DEALDESK_PHASE1C_CHECKOUT", "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL")),
    "Pinned disposable PostgreSQL required")
class PinnedWeek4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        # M20 is intentionally mutated by other fault-injection tests later
        # in full discovery; use the separately provisioned E2E business and
        # checkpoint pair when CI provides it. Never mix pairs.
        if bool(os.getenv("M20_E2E_DATABASE_URL")) != bool(os.getenv("M20_E2E_CHECKPOINT_URL")):
            raise ValueError("Week 4 requires both E2E business/checkpoint DBs or neither")
        cls.db_url = os.getenv("M20_E2E_DATABASE_URL") or os.environ["M20_DATABASE_URL"]
        cls.checkpoint_url = (os.getenv("M20_E2E_CHECKPOINT_URL") or
                              os.environ["M20_CHECKPOINT_DATABASE_URL"])
        cls.connect = staticmethod(lambda: psycopg.connect(cls.db_url))
        with cls.connect() as db:
            if db.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE "
                          "'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(db)

    def test_nine_cases_and_isolated_candidate_replay(self):
        dsn = self.checkpoint_url
        result = run(self.connect, dsn, self.adapter)
        summary = result["summary"]
        self.assertEqual(summary["original_cases"], len(CASES))
        self.assertEqual(sum(summary["deterministic_mappings"].values()), 54)
        self.assertEqual(sum(summary["offline_ai_execution"].values()), 54)
        self.assertEqual(summary["fixed_discovery"], {"discovered": 5,
                                                       "not_discovered": 4})
        self.assertEqual(summary["candidate_fixed_rechecks"], 6)
        self.assertEqual(summary["candidate_fixed_checked"], 1)
        self.assertEqual(result["provider_requests"], 0)
        self.assertIsNone(summary["accepted_answer_accuracy"])
        self.assertIn("Nine distinct pinned synthetic deals", report(result))
        self.assertEqual(len({x["bundle_sha256"] for x in result["scenarios"]}), 9)
        by_case = {x["case_id"]: x for x in result["scenarios"]}
        self.assertEqual(by_case["M18-D-B03"]["deterministic_baseline"][
            "review_status"], "needs_revision")
        self.assertEqual(by_case["M18-D-B03"]["offline_ai"]["fulfillment"][
            "execution"], "completed")
        self.assertFalse(by_case["M18-D-N01"]["fixed_discovery"]["discovered"])
        self.assertEqual(by_case["M18-D-B05"]["offline_ai"]["credit"][
            "validated_claims"], [])
        candidate = result["isolated_candidate"]
        self.assertEqual(candidate["customer_acceptance"], "pending")
        self.assertEqual(candidate["fixed_business_status"], "needs_revision")
        self.assertTrue(candidate["same_schedule_as_fixed_discovery"])
        self.assertNotEqual(candidate["assessment_id"], by_case["M18-D-B01"][
            "assessment_id"])
        self.assertEqual(candidate["bundle_sha256"], by_case["M18-D-B01"][
            "bundle_sha256"])
        repeat = run(self.connect, dsn, self.adapter)
        self.assertEqual(repeat["stable_result_sha256"], result["stable_result_sha256"])
        for key in ("timing_diagnostics", "stable_result_sha256"):
            repeat.pop(key)
            result.pop(key)
        self.assertEqual(repeat, result)

    def test_candidate_rejects_cross_subject_or_invented_citation(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        from dealdesk_phase2.orchestrator import build_original_graph
        result = run(self.connect, self.checkpoint_url, self.adapter)
        target = result["isolated_candidate"]
        with thesis_checkpointer(self.checkpoint_url) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            state = graph.get_state({"configurable": {"thread_id": target[
                "assessment_id"]}}).values
            from dealdesk_phase2.evaluation_m18 import pinned_baseline
            from dealdesk_phase2.graph_state import pinned_from_state
            baseline = pinned_baseline(self.adapter, self.connect, pinned_from_state(state))
            altered = deepcopy(state)
            candidate = next(iter(altered["candidate_records"].values()))
            candidate["specialist_results"]["credit"]["subject_id"] = "WRONG"
            with self.assertRaises(EvidenceMismatch):
                _candidate_record(altered, baseline, self.adapter)
            altered = deepcopy(state)
            candidate = next(iter(altered["candidate_records"].values()))
            candidate["proposed_slices"][0]["source_refs"] = ["inventory:INVENTED"]
            with self.assertRaises(EvidenceMismatch):
                _candidate_record(altered, baseline, self.adapter)
            with self.assertRaises(EvidenceMismatch):
                _candidate_record(state, {**baseline, "bundle_sha256": "WRONG"}, self.adapter)


if __name__ == "__main__":
    unittest.main()
