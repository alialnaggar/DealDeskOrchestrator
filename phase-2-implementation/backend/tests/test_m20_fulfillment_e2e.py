"""Offline Fulfillment revision, fixed candidate and M2.0 AI on one pinned run."""

import os
from pathlib import Path
import tempfile
import unittest

from dealdesk_phase2.hybrid_offline import run_hybrid_offline
from dealdesk_phase2.hybrid_provider import OfflineGroqWireDouble
from dealdesk_phase2.m20_specialists import run_m20_offline
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases
from test_hybrid_provider import wire_call, wire_final
from test_m20_specialists import Scripted, inspect, product_finding, pricing_finding

try:
    import psycopg
except ImportError:
    psycopg = None


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_E2E_DATABASE_URL", "M20_E2E_CHECKPOINT_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh pinned Fulfillment/M2.0 integration databases required")
class FullOfflineIntegration(unittest.TestCase):
    def test_corrected_hybrid_final_evidence_fixed_candidate_then_separate_m20_ai(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        case = next(x for x in CASES if x.case_id == "B05")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connection = lambda: psycopg.connect(os.environ["M20_E2E_DATABASE_URL"])
        with connection() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        def final(second):
            return wire_final("submit_proposal", {"line_id": ids["L"],
                "tradeoff_code": "partial_delivery_requires_customer_acceptance",
                "delivery_slices": [
                    {"quantity": "11", "delivery_date": "2026-09-02",
                     "source_refs": ["inventory:" + ids["INV"]]},
                    {"quantity": second, "delivery_date": "2026-09-11",
                     "source_refs": ["inbound_supply:" + ids["IN"]]}]})
        responses = [wire_call("inspect_fulfillment_paths", {"line_id": ids["L"],
                        "purpose_code": "check_dated_path"}),
                     wire_call("submit_proposal", {"submission_kind": "binding_partial_delivery"}),
                     final("18"),  # rejected model overcount; never a published candidate
                     wire_call("submit_proposal", {"submission_kind": "binding_partial_delivery"}),
                     final("7")]
        model = OfflineGroqWireDouble(responses)
        assessment = "M20-HYBRID-B05-CORRECTION-OFFLINE-V2"
        config = {"configurable": {"thread_id": assessment}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["M20_E2E_CHECKPOINT_URL"]) as saver:
                graph = build_original_graph(adapter, connection, saver)
                state = run_hybrid_offline(graph, config, adapter, connection, model,
                    assessment_id=assessment, run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(state["candidate_status"], "fixed_checked")
                self.assertEqual(state["hybrid_execution"]["feedback"]["constraint_code"],
                                 "quantity_sum_mismatch")
                self.assertEqual([item["stage"] for item in state["hybrid_execution"]["attempts"]],
                                 ["decision", "decision", "final", "revision_intent", "revision"])
                self.assertEqual(state["hybrid_execution"]["rejections"][0]["raw"], final("18"))
                self.assertEqual(len(state["candidate_records"]), 1)
                checked = next(iter(state["candidate_records"].values()))
                self.assertEqual(checked["fixed_supply_status"], "supply_supported_unreserved")
                self.assertEqual(len(checked["specialist_results"]), 6)
                self.assertEqual(state["reviewer_package"]["candidates"][0][
                    "customer_acceptance"], "pending")
                self.assertEqual(state["reviewer_package"]["candidates"][0][
                    "verification_outcome"], "binding_supply_supported_unreserved")
                original_fixed = state["specialist_results"]
                original_review = state["reviewer_package"]
                configuration = Scripted([inspect, product_finding])
                pricing = Scripted([inspect, pricing_finding])
                state = run_m20_offline(graph, config, adapter, {
                    "configuration": configuration, "pricing": pricing})
                self.assertEqual(state["specialist_results"], original_fixed)
                self.assertEqual({k: v for k, v in state["reviewer_package"].items()
                                  if k != "m20_ai"}, original_review)
                self.assertEqual(state["reviewer_package"]["m20_ai"], state["m20_review"])
                self.assertEqual([state["m20_ai_results"][name]["execution"] for name in (
                    "configuration", "pricing")], ["completed", "completed"])
                self.assertEqual(len(state["candidate_records"]), 1)
            with thesis_checkpointer(os.environ["M20_E2E_CHECKPOINT_URL"]) as saver:
                graph = build_original_graph(adapter, connection, saver)
                replay = run_m20_offline(graph, config, adapter, {
                    "configuration": configuration, "pricing": pricing})
                self.assertEqual((configuration.calls, pricing.calls), (2, 2))
                self.assertEqual(replay["candidate_records"], state["candidate_records"])
                self.assertEqual(replay["m20_ai_results"], state["m20_ai_results"])
