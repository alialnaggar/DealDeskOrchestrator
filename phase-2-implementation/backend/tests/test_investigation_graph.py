"""Offline and pinned-PostgreSQL M1.3 Fulfillment investigation contracts."""

from datetime import date, datetime, time, timezone
from decimal import Decimal
import os
from pathlib import Path
import unittest
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.contracts import RunContextV1
from dealdesk_phase2.evidence_bundle import seal
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.investigation_graph import run_original_then_investigate
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import PinnedBundleV1, Phase1CAdapter
from test_original_graph import FixedAdapterDouble, RUN, AT

try:
    import psycopg
except ImportError:
    psycopg = None


def _bundle():
    return {"run": {"run_id": RUN},
            "deal": {"deal_id": "D-20", "customer_id": "C-20",
                     "requested_delivery_date": date(2026, 9, 4),
                     "destination_country_code": "DE", "destination_region": "Berlin",
                     "terms_json": {"allow_partial_delivery": True}},
            "lines": [{"deal_line_id": "L1", "product_id": "P1",
                       "fulfillment_mode": "supplier_finished", "quantity": Decimal(20)}],
            "inventory": [{"inventory_id": "S1", "product_id": "P1", "location_id": "W1",
                           "quantity_on_hand": Decimal(12), "quantity_allocated": Decimal(0),
                           "snapshot_at": AT}],
            "inbound_supply": [],
            "supplier_offers": [{"supplier_item_id": "O1", "supplier_id": "SUP",
                                 "product_id": "P1", "lead_days_min": 8,
                                 "lead_days_mode": 10, "lead_days_max": 12,
                                 "order_calendar_json": {}}],
            "shipping_lanes": [{"lane_id": "LANE", "origin_location_id": "W1",
                                "destination_country_code": "DE", "destination_region": "Berlin",
                                "cutoff_local_time": time(15)}],
            "facts": {"lines": [{"line_id": "L1", "fulfillment_status": "late_alternative",
                                  "shipping_options": [{"stock_id": "S1", "supply_ids": [],
                                                        "location": "W1", "quantity": Decimal(12),
                                                        "dispatch": date(2026, 9, 3),
                                                        "arrival": date(2026, 9, 4)}],
                                  "quantity_by_requested_date": Decimal(12)}],
                      "supply": {"stock": {"P1": [{"id": "S1", "location": "W1",
                                                    "free": Decimal(12), "fresh": True}]},
                                 "binding_receipts": {"P1": []}}}}


class InvestigationAdapter(FixedAdapterDouble):
    def read_original(self, connection_factory, run_id, assessment_id):
        raw, digest, size = seal(_bundle())
        context = RunContextV1(assessment_id, RUN, "D-20", "D-20", AT, "snapshot-1",
                               "catalog-1", "BASELINE_2026", "config-1", "0" * 64, digest)
        return PinnedBundleV1(context, raw, size)


def _proposal(citations=None):
    return {"type": "contribution", "value": {"kind": "proposal", "payload": {
        "line_id": "L1", "delivery_slices": [
            {"quantity": "12", "delivery_date": "2026-09-04", "commitment_claim": "unknown"},
            {"quantity": "8", "delivery_date": "2026-09-17", "commitment_claim": "conditional"}],
        "citations": citations if citations is not None else ["inventory:S1", "supplier_offer:O1"],
        "tradeoffs": ["Eight may arrive later"], "assumptions": ["Supplier confirmation needed"],
        "unmet_requirements": ["Eight units not supported by requested date"],
        "uncertainty_reasons": ["Offer is uncommitted"]}}}


def _tool(line="L1"):
    return {"type": "tool", "tool": "inspect_line_supply", "arguments": {"line_id": line}}


def _finding(citations):
    return {"type": "contribution", "value": {"kind": "finding_without_proposal",
            "payload": {"line_id": "L1", "finding": "Later supply is conditional",
                        "citations": citations, "uncertainty_reasons": ["Supplier confirmation absent"]}}}


class OfflineInvestigationTests(unittest.TestCase):
    def setUp(self):
        self.adapter = InvestigationAdapter()
        self.saver = InMemorySaver()
        self.graph = build_original_graph(self.adapter, None, self.saver)
        self.config = {"configurable": {"thread_id": self.id()}}

    def run_with(self, *actions):
        return run_original_then_investigate(self.graph, self.config, self.adapter,
            OfflineModelDouble(tuple(actions)), assessment_id=self.id(), run_id=RUN)

    def test_proposal_is_cited_and_unverified_without_changing_fixed_assessment(self):
        state = self.run_with(_tool(), _proposal())
        self.assertEqual(self.adapter.decisions, 1)
        self.assertEqual(len(state["specialist_results"]), 6)
        self.assertEqual(state["review_status"], "needs_revision")
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["verification"], "unverified")
        self.assertEqual(state["ai_fulfillment_result"]["producer_type"], "AI")
        self.assertEqual(state["ai_fulfillment_result"]["subject_id"], "D-20")
        self.assertNotIn("candidate", state)
        self.assertEqual(len([e for e in state["tool_access_ledger"] if e["counted"]]), 1)
        self.assertEqual(self.run_with(_tool(), _proposal())["trace"], state["trace"])

    def test_finding_and_abstention_are_distinct(self):
        finding = self.run_with(_tool(), _finding(["supplier_offer:O1"]))
        self.assertEqual(finding["ai_fulfillment_result"]["contribution"]["kind"],
                         "finding_without_proposal")
        self.assertEqual(finding["ai_fulfillment_result"]["execution"], "completed")
        self.setUp()
        abstained = self.run_with({"type": "contribution", "value": {"kind": "abstention",
            "payload": {"reason": "No supportable suggestion", "uncertainty_reasons": ["Missing commitment"]}}})
        self.assertEqual(abstained["ai_fulfillment_result"]["contribution"]["kind"], "abstention")
        self.assertEqual(abstained["specialist_results"]["fulfillment"]["finding"], "needs_revision")

    def test_malformed_model_and_unseen_citation_fail_separately(self):
        malformed = self.run_with({"type": "contribution", "value": {"kind": "proposal"}})
        self.assertEqual(malformed["ai_fulfillment_result"]["error"], "malformed_contribution")
        self.assertEqual(malformed["review_status"], "needs_revision")
        self.setUp()
        unsupported = self.run_with(_tool(), _proposal(["inventory:NEVER_RETURNED"]))
        self.assertEqual(unsupported["ai_fulfillment_result"]["error"], "unsupported_citation")
        self.assertEqual(unsupported["specialist_results"]["fulfillment"]["execution"], "completed")
        self.setUp()
        falsely_confirmed = _proposal()
        falsely_confirmed["value"]["payload"]["delivery_slices"][1]["commitment_claim"] = "confirmed"
        rejected = self.run_with(_tool(), falsely_confirmed)
        self.assertEqual(rejected["ai_fulfillment_result"]["error"], "malformed_contribution")

    def test_unauthorized_tool_and_model_timeout_preserve_fixed_results(self):
        denied = self.run_with(_tool("OTHER"), _proposal())
        self.assertEqual(denied["ai_fulfillment_result"]["error"], "tool:authorization_denied")
        self.assertEqual(denied["tool_access_ledger"][-1]["returned_refs"], [])
        self.setUp()

        class TimedOut:
            def next_action(self, input, observations):
                raise TimeoutError("offline model timeout")

        failed = run_original_then_investigate(self.graph, self.config, self.adapter, TimedOut(),
                                                assessment_id=self.id(), run_id=RUN)
        self.assertEqual(failed["ai_fulfillment_result"]["error"], "model_output:TimeoutError")
        self.assertEqual(failed["review_status"], "needs_revision")

    def test_tool_execution_error_and_exhausted_budget_are_not_business_results(self):
        class BrokenEvidence(InvestigationAdapter):
            def read_original(self, connection_factory, run_id, assessment_id):
                from dataclasses import replace

                pinned = super().read_original(connection_factory, run_id, assessment_id)
                bundle = pinned.decode()
                del bundle["inventory"][0]["inventory_id"]
                raw, digest, size = seal(bundle)
                return PinnedBundleV1(replace(pinned.context, bundle_sha256=digest), raw, size)

        adapter = BrokenEvidence()
        graph = build_original_graph(adapter, None, InMemorySaver())
        config = {"configurable": {"thread_id": "tool-failure"}}
        failed = run_original_then_investigate(graph, config, adapter,
            OfflineModelDouble((_tool(),)), assessment_id="tool-failure", run_id=RUN)
        self.assertEqual(failed["ai_fulfillment_result"]["error"], "tool:technical_failure")
        self.assertEqual(failed["review_status"], "needs_revision")
        # Reserve all calls before starting a new investigation. No model
        # action should run, and no fresh allowance appears on restart.
        fixed = self.graph.invoke(initial_state(self.id(), RUN), self.config)
        from dealdesk_phase2.tool_ledger import reserve

        context = fixed["context"]
        identity = {"assessment_id": self.id(), "bundle_sha256": context["bundle_sha256"]}
        for index in range(12):
            reserve(self.graph, self.config, self.id(), context["bundle_sha256"],
                    f"pre-spent-{index}", "inspect_line_supply", {"line_id": "L1"}, identity)
        exhausted = run_original_then_investigate(self.graph, self.config, self.adapter,
            OfflineModelDouble(tuple()), assessment_id=self.id(), run_id=RUN)
        self.assertEqual(exhausted["ai_fulfillment_result"]["error"], "budget_exhausted")
        self.assertEqual(exhausted["review_status"], "needs_revision")

    def test_configuration_or_no_shortage_skips_but_policy_block_does_not(self):
        for adapter, reason in ((InvestigationAdapter(config_valid=False, status="blocked"),
                                 "configuration_not_valid"),
                                (InvestigationAdapter(fulfillment="confirmed_by_date",
                                                      status="approval_required"),
                                 "no_single_supported_recoverable_shortage")):
            with self.subTest(reason=reason):
                saver = InMemorySaver()
                graph = build_original_graph(adapter, None, saver)
                config = {"configurable": {"thread_id": reason}}
                result = run_original_then_investigate(graph, config, adapter,
                    OfflineModelDouble(tuple()), assessment_id=reason, run_id=RUN)
                self.assertEqual(result["ai_fulfillment_result"],
                                 {"execution": "skipped", "reason": reason})
        blocked = InvestigationAdapter(status="blocked")
        graph = build_original_graph(blocked, None, InMemorySaver())
        result = run_original_then_investigate(graph, {"configurable": {"thread_id": "policy"}},
            blocked, OfflineModelDouble((_tool(), _finding(["supplier_offer:O1"]))),
            assessment_id="policy", run_id=RUN)
        self.assertEqual(result["ai_fulfillment_result"]["execution"], "completed")
        self.assertEqual(result["review_status"], "blocked")

    def test_interruption_replays_tool_without_resetting_budget(self):
        class InterruptOnce:
            def __init__(self):
                self.interrupted = False

            def next_action(self, input, observations):
                if not observations:
                    return _tool()
                if not self.interrupted:
                    self.interrupted = True
                    raise KeyboardInterrupt("simulated process exit after tool checkpoint")
                return _finding(["inventory:S1"])

        model = InterruptOnce()
        with self.assertRaises(KeyboardInterrupt):
            run_original_then_investigate(self.graph, self.config, self.adapter, model,
                                           assessment_id=self.id(), run_id=RUN)
        before = self.graph.get_state(self.config).values
        self.assertEqual(sum(bool(e["counted"]) for e in before["tool_access_ledger"]), 1)
        self.assertNotIn("ai_fulfillment_result", before)
        restarted_graph = build_original_graph(self.adapter, None, self.saver)
        after = run_original_then_investigate(restarted_graph, self.config, self.adapter, model,
                                               assessment_id=self.id(), run_id=RUN)
        self.assertEqual(after["ai_fulfillment_result"]["execution"], "completed")
        self.assertEqual(sum(bool(e["counted"]) for e in after["tool_access_ledger"]), 1)
        self.assertEqual(self.adapter.decisions, 1)


READY = all((psycopg, os.getenv("DATABASE_URL"), os.getenv("CHECKPOINT_DATABASE_URL"),
             os.getenv("DEALDESK_PHASE1C_CHECKOUT")))


@unittest.skipUnless(READY, "Needs pinned Phase 1C and disposable PostgreSQL")
class PinnedInvestigationTests(unittest.TestCase):
    def test_binding_deal_skips_offer_deal_investigates_without_split_claim(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter,
                lambda: psycopg.connect(os.environ["DATABASE_URL"]), saver)
            binding = run_original_then_investigate(
                graph, {"configurable": {"thread_id": "M13-binding"}}, adapter,
                OfflineModelDouble(tuple()), assessment_id="M13-binding", run_id=RUN)
            self.assertEqual(binding["ai_fulfillment_result"]["execution"], "skipped")
            offer_run = UUID("00000000-0000-4000-8000-000000030001")
            offer_id = "OFFER-offer_without_supplier_commitment"
            offer_line = "L-offer_without_supplier_commitment-1"
            model = OfflineModelDouble((
                _tool(offer_line), {"type": "contribution", "value": {
                    "kind": "finding_without_proposal", "payload": {
                        "line_id": offer_line, "finding": "Supplier offer needs confirmation",
                        "citations": ["supplier_offer:" + offer_id],
                        "uncertainty_reasons": ["No binding receipt"]}}}))
            offer = run_original_then_investigate(
                graph, {"configurable": {"thread_id": "M13-offer"}}, adapter, model,
                assessment_id="M13-offer", run_id=offer_run)
            self.assertEqual(offer["ai_fulfillment_result"]["execution"], "completed")
            self.assertEqual(offer["ai_fulfillment_result"]["contribution"]["kind"],
                             "finding_without_proposal")
            self.assertEqual(offer["specialist_results"]["fulfillment"]["finding"], "conditional")
            self.assertEqual(sum(bool(e["counted"]) for e in offer["tool_access_ledger"]), 1)

    def test_postgres_restart_replays_sealed_tool_result_without_new_call(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        offer_run = UUID("00000000-0000-4000-8000-000000030001")
        line_id = "L-offer_without_supplier_commitment-1"
        assessment = "M13-offer-restart"
        config = {"configurable": {"thread_id": assessment}}

        class Interrupted:
            def __init__(self):
                self.once = False

            def next_action(self, input, observations):
                if not observations:
                    return _tool(line_id)
                if not self.once:
                    self.once = True
                    raise KeyboardInterrupt("simulated process stop")
                return _finding(["supplier_offer:OFFER-offer_without_supplier_commitment"])

        model = Interrupted()
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter,
                lambda: psycopg.connect(os.environ["DATABASE_URL"]), saver)
            with self.assertRaises(KeyboardInterrupt):
                run_original_then_investigate(graph, config, adapter, model,
                                              assessment_id=assessment, run_id=offer_run)
            before = graph.get_state(config).values
            self.assertEqual(sum(bool(e["counted"]) for e in before["tool_access_ledger"]), 1)
            self.assertNotIn("ai_fulfillment_result", before)
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            restarted = build_original_graph(adapter,
                lambda: psycopg.connect(os.environ["DATABASE_URL"]), saver)
            after = run_original_then_investigate(restarted, config, adapter, model,
                                                  assessment_id=assessment, run_id=offer_run)
            self.assertEqual(after["ai_fulfillment_result"]["execution"], "completed")
            self.assertEqual(after["context"], before["context"])
            self.assertEqual(after["specialist_results"], before["specialist_results"])
            self.assertEqual(sum(bool(e["counted"]) for e in after["tool_access_ledger"]), 1)
            self.assertEqual(after["trace"].count("configuration:completed"), 1)


if __name__ == "__main__":
    unittest.main()
