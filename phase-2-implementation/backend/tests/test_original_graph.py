"""Offline graph contract tests with a small fixed-decision double."""

from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import unittest
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.contracts import RunContextV1
from dealdesk_phase2.evidence_bundle import seal
from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import PinnedBundleV1


RUN = UUID("00000000-0000-4000-8000-000000010001")
AT = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)


class FixedAdapterDouble:
    def __init__(self, *, config_valid=True, status="needs_revision", fulfillment="late_alternative"):
        self.config_valid = config_valid
        self.status = status
        self.fulfillment = fulfillment
        self.decisions = 0

    def read_original(self, connection_factory, run_id, assessment_id):
        raw, digest, size = seal({"run": {"run_id": RUN},
                                  "deal": {"deal_id": "D-20"}})
        context = RunContextV1(assessment_id, RUN, "D-20", "D-20", AT, "snapshot-1",
                               "catalog-1", "BASELINE_2026", "config-1", "0" * 64, digest)
        return PinnedBundleV1(context, raw, size)

    def fixed_original_decision(self, pinned):
        pinned.decode()
        self.decisions += 1
        return {"run_id": RUN, "deal_id": "D-20", "as_of_at": AT,
                "policy_set_code": "BASELINE_2026", "catalog_version": "catalog-1",
                "status": self.status,
                "specialists": {
                    "configuration": [{"line_id": "L1", "status": "valid" if self.config_valid else "invalid",
                                       "codes": [] if self.config_valid else ["configuration_invalid"]}],
                    "compatibility": [],
                    "pricing": {"deal_margin_pct": 15, "deal_discount_pct": 0,
                                "cost_evidence_gaps": [], "rule_hits": []},
                    "availability": [{"line_id": "L1", "status": self.fulfillment,
                                      "requested_quantity": 20, "quantity_by_requested_date": 12,
                                      "source_ids": ["S1"]}],
                    "credit": {"credit_exposure": 5, "credit_over_limit_pct": 0,
                               "rule_hits": [], "commitments_fresh": True},
                    "policy": {"rule_hits": [], "hard_blocks": ["credit_hold"] if self.status == "blocked" else []},
                    "approval_routing": {"required_roles": ["Regional_Manager"]
                                         if self.status == "approval_required" else [],
                                         "route_withheld": self.status != "approval_required"}}}

    def validate_pinned_context(self, pinned):
        return pinned.decode()


class OriginalGraphTests(unittest.TestCase):
    def run_graph(self, adapter):
        graph = build_original_graph(adapter, None, InMemorySaver())
        return graph.invoke(initial_state("A-20", RUN),
                            {"configurable": {"thread_id": "A-20"}})

    def test_sequential_results_are_six_distinct_mappings_of_one_decision(self):
        adapter = FixedAdapterDouble()
        state = self.run_graph(adapter)
        self.assertEqual(adapter.decisions, 1)
        self.assertEqual(list(state["specialist_results"]), [
            "configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"])
        self.assertEqual(state["specialist_results"]["fulfillment"]["finding"], "needs_revision")
        self.assertEqual(state["specialist_results"]["credit"]["execution"], "completed")
        self.assertEqual(state["specialist_results"]["approval_routing"]["finding"], "withheld")
        self.assertEqual(state["review_status"], "needs_revision")
        self.assertEqual(pinned_from_state(state).decode()["deal"]["deal_id"], "D-20")

    def test_configuration_failure_skips_dependent_work_but_policy_still_runs(self):
        state = self.run_graph(FixedAdapterDouble(config_valid=False, status="blocked"))
        results = state["specialist_results"]
        self.assertEqual(results["configuration"]["finding"], "infeasible")
        for name in ("pricing", "fulfillment", "credit"):
            self.assertEqual(results[name]["execution"], "skipped")
        self.assertEqual(results["policy"]["execution"], "completed")
        self.assertEqual(results["approval_routing"]["finding"], "withheld")
        self.assertEqual(state["review_status"], "incomplete")

    def test_policy_block_does_not_suppress_credit_or_fulfillment(self):
        state = self.run_graph(FixedAdapterDouble(status="blocked"))
        self.assertEqual(state["specialist_results"]["credit"]["execution"], "completed")
        self.assertEqual(state["specialist_results"]["fulfillment"]["execution"], "completed")
        self.assertEqual(state["specialist_results"]["policy"]["finding"], "infeasible")
        self.assertEqual(state["specialist_results"]["approval_routing"]["payload"]["required_roles"], [])
        self.assertFalse(state["specialist_results"]["approval_routing"]["payload"][
            "roles_available_from_fixed_interface"])

    def test_confirmed_business_route_is_still_only_human_review(self):
        state = self.run_graph(FixedAdapterDouble(status="approval_required",
                                                  fulfillment="confirmed_by_date"))
        routing = state["specialist_results"]["approval_routing"]
        self.assertEqual(routing["finding"], "approval_required")
        self.assertEqual(routing["payload"]["required_roles"], ["Regional_Manager"])
        self.assertNotIn("approved", state["review_status"])

    def test_tampered_bundle_rejected_before_next_node(self):
        adapter = FixedAdapterDouble()
        saver = InMemorySaver()
        graph = build_original_graph(adapter, None, saver, interrupt_after=("configuration",))
        config = {"configurable": {"thread_id": "A-20"}}
        graph.invoke(initial_state("A-20", RUN), config)
        state = graph.get_state(config).values
        self.assertEqual(adapter.decisions, 1)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            pinned_from_state({**state, "sealed_bundle": state["sealed_bundle"] + " "})


if __name__ == "__main__":
    unittest.main()
