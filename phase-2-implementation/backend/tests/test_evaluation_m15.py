"""M1.5 source-first cases: real references, synthetic offline bundles, faults.

These are distinct cohorts. The synthetic adapter has scripted fixed findings:
it exercises Phase 2 boundaries and is not independent Phase 1C ground truth.
"""
import copy
from dataclasses import replace
from pathlib import Path
import os
import unittest
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.evidence_bundle import seal
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.investigation_graph import run_original_then_investigate
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter, PinnedBundleV1
from test_investigation_graph import InvestigationAdapter, _bundle, _proposal, _tool, RUN

try:
    import psycopg
except ImportError:
    psycopg = None


ANSWER_SHEET = Path(__file__).resolve().parents[2] / "evaluation" / "m1.5-answer-sheet.md"
OFFER_RUN = UUID("00000000-0000-4000-8000-000000030001")


def _action(kind, payload):
    return {"type": "contribution", "value": {"kind": kind, "payload": payload}}


def _completed_calls(state):
    return [event for event in state["tool_access_ledger"] if event["status"] == "completed"]


class SyntheticScenarioAdapter(InvestigationAdapter):
    """Change only the sealed source pool, leaving the scripted fixed double explicit."""

    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.source = copy.deepcopy(source)

    def read_original(self, connection_factory, run_id, assessment_id):
        original = super().read_original(connection_factory, run_id, assessment_id)
        raw, digest, size = seal(self.source)
        return PinnedBundleV1(replace(original.context, bundle_sha256=digest), raw, size)


class SourceFirstSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(ANSWER_SHEET.is_file())
        self.assertIn("S20", ANSWER_SHEET.read_text())

    def assess(self, source, actions, *, fixed_status="late_alternative"):
        adapter = SyntheticScenarioAdapter(source, fulfillment=fixed_status)
        saver = InMemorySaver()
        graph = build_original_graph(adapter, None, saver)
        config = {"configurable": {"thread_id": self.id()}}
        state = run_original_then_investigate(
            graph, config, adapter, OfflineModelDouble(tuple(actions)),
            assessment_id=self.id(), run_id=RUN)
        return state, adapter

    def test_s20_mixed_stock_offer_is_unverified_even_after_three_tools(self):
        source = _bundle()
        inspect_paths = {"type": "tool", "tool": "inspect_fulfillment_paths",
                         "arguments": {"line_id": "L1"}}
        inspect_offer = {"type": "tool", "tool": "inspect_evidence_record",
                         "arguments": {"line_id": "L1", "source_category": "supplier_offer",
                                       "source_id": "O1"}}
        state, adapter = self.assess(source, (_tool(), inspect_paths, inspect_offer, _proposal()))
        calls = _completed_calls(state)
        self.assertEqual([x["tool"] for x in calls],
                         ["inspect_line_supply", "inspect_fulfillment_paths", "inspect_evidence_record"])
        self.assertEqual(calls[1]["result"]["evidence"], "unsupported_capability")
        self.assertEqual(calls[2]["result"]["evidence"], "insufficient_or_conditional")
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["verification"], "unverified")
        self.assertEqual(state["review_status"], "needs_revision")
        self.assertNotIn("candidate", state)
        self.assertEqual(adapter.decisions, 1)

    def test_s21_customer_forbids_split_and_fixed_result_survives(self):
        source = _bundle()
        source["deal"]["terms_json"]["allow_partial_delivery"] = False
        state, _ = self.assess(source, (_tool(), _proposal()))
        self.assertEqual(state["ai_fulfillment_result"]["error"], "malformed_contribution")
        self.assertEqual(state["specialist_results"]["fulfillment"]["execution"], "completed")
        self.assertEqual(state["review_status"], "needs_revision")

    def test_s22_empty_selected_pool_never_proves_global_infeasibility(self):
        source = _bundle()
        source["inventory"] = []
        source["supplier_offers"] = []
        source["shipping_lanes"] = []
        source["facts"]["supply"]["stock"]["P1"] = []
        source["facts"]["lines"][0]["shipping_options"] = []
        abstain = _action("abstention", {
            "reason": "No relevant records in the bounded selected pool",
            "uncertainty_reasons": ["Unseen supply cannot be ruled out"]})
        state, _ = self.assess(source, (_tool(), abstain), fixed_status="conditional")
        self.assertEqual(_completed_calls(state)[0]["result"]["evidence"], "no_eligible_evidence")
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["kind"], "abstention")
        self.assertEqual(state["specialist_results"]["fulfillment"]["finding"], "conditional")

    def test_s23_competing_uncommitted_offers_remain_uncertain(self):
        source = _bundle()
        second = copy.deepcopy(source["supplier_offers"][0])
        second.update(supplier_item_id="O2", supplier_id="SUP2",
                      lead_days_min=25, lead_days_mode=30, lead_days_max=35)
        source["supplier_offers"].append(second)
        finding = _action("finding_without_proposal", {
            "line_id": "L1",
            "finding": "Two uncommitted lead estimates require review",
            "citations": ["supplier_offer:O1", "supplier_offer:O2"],
            "uncertainty_reasons": ["Neither supplier offer is a confirmed receipt"]})
        state, _ = self.assess(source, (_tool(), finding))
        exposed = _completed_calls(state)[0]["returned_refs"]
        self.assertIn("supplier_offer:O1", exposed)
        self.assertIn("supplier_offer:O2", exposed)
        self.assertEqual(state["ai_fulfillment_result"]["execution"], "completed")
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["kind"],
                         "finding_without_proposal")
        self.assertEqual(state["review_status"], "needs_revision")

    def test_f06_uncited_or_blank_finding_is_rejected_with_fixed_fallback(self):
        for finding, citations in (("Eight units are confirmed", []),
                                   ("   ", ["supplier_offer:O1"])):
            with self.subTest(finding=finding):
                output = _action("finding_without_proposal", {
                    "line_id": "L1", "finding": finding,
                    "citations": citations, "uncertainty_reasons": ["Offer uncommitted"]})
                state, _ = self.assess(_bundle(), (_tool(), output))
                self.assertEqual(state["ai_fulfillment_result"]["error"],
                                 "malformed_contribution")
                self.assertEqual(state["specialist_results"]["fulfillment"]["execution"],
                                 "completed")
                self.assertEqual(state["review_status"], "needs_revision")


@unittest.skipUnless(psycopg is not None and os.getenv("DATABASE_URL")
                     and os.getenv("DEALDESK_PHASE1C_CHECKOUT"),
                     "Requires pinned Phase 1C reference rows and PostgreSQL")
class PinnedRealReferenceTests(unittest.TestCase):
    def test_r01_r03_r07_r10_r14_source_first_fixed_expectations(self):
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cases = ((1, "confirmed_by_date"), (3, "conditional"),
                 (7, "late_alternative"), (10, "unknown"), (14, "infeasible"))
        for number, expected in cases:
            with self.subTest(reference=number):
                run = UUID(f"00000000-0000-4000-8000-000000{number:02d}0001")
                pinned = adapter.read_original(
                    lambda: psycopg.connect(os.environ["DATABASE_URL"]),
                    run, f"M15-reference-{number}")
                pool = adapter.validate_pinned_context(pinned)
                self.assertEqual(pool["facts"]["lines"][0]["fulfillment_status"], expected)
                self.assertEqual(str(pinned.context.phase1c_run_id), str(run))
                self.assertEqual(pinned.context.original_deal_id, pool["deal"]["deal_id"])
                self.assertEqual(len(pinned.context.bundle_sha256), 64)
        self.assertIn("not independently accepted", ANSWER_SHEET.read_text().lower())


if __name__ == "__main__":
    unittest.main()
