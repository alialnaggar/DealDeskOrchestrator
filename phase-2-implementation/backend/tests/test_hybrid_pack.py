"""No-network opt-in prefetch and checkpoint tests with the existing facade."""

import unittest
from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.hybrid_contracts import HybridContractError
from dealdesk_phase2.hybrid_pack import prepare_pack
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_investigation_graph import InvestigationAdapter, RUN


class HybridPackTests(unittest.TestCase):
    def setUp(self):
        self.adapter = InvestigationAdapter()
        self.graph = build_original_graph(self.adapter, None, InMemorySaver())
        self.config = {"configurable": {"thread_id": self.id()}}
        self.graph.invoke(initial_state(self.id(), RUN), self.config)

    def pack(self, *, policy="hybrid-test-v1"):
        return prepare_pack(self.graph, self.config, self.adapter,
                            provider="offline_double", model="scripted", policy_version=policy)

    def test_one_counted_prefetch_with_no_answer_or_baseline_and_replay(self):
        result, input = self.pack()
        state = self.graph.get_state(self.config).values
        self.assertEqual(result["origin"], "trusted_prefetch")
        self.assertEqual(result["observation"]["tool"], "inspect_line_supply")
        self.assertEqual(result["model_input"]["line_id"], input.line_id)
        self.assertEqual(result["observation"]["returned_refs"], [
            "inventory:S1", "shipping_lane:LANE", "supplier_offer:O1"])
        self.assertFalse(any(x in str(result) for x in (
            "baseline", "discover_partial_delivery", "binding_options",
            "expected_answer", "candidate_slices")))
        events = state["tool_access_ledger"]
        self.assertEqual([x["status"] for x in events], ["reserved", "completed"])
        self.assertEqual(sum(bool(x.get("counted")) for x in events), 1)
        self.assertEqual(result["coverage"]["scope"], "selected_reader_pool_only")
        self.assertFalse(result["coverage"]["more_in_sealed_pool"])
        with patch("dealdesk_phase2.hybrid_pack.FulfillmentTools", side_effect=AssertionError(
                "replay must use saved pack")):
            again, frozen_input = self.pack()
        self.assertEqual(again, result)
        self.assertEqual(frozen_input, input)
        with self.assertRaises(EvidenceMismatch):
            self.pack(policy="changed-policy")

    def test_start_without_tool_reservation_may_resume_once(self):
        with patch("dealdesk_phase2.hybrid_pack.FulfillmentTools", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.pack()
        self.assertEqual(self.graph.get_state(self.config).values["tool_access_ledger"], [])
        pack, _ = self.pack()
        self.assertEqual(pack["observation"]["execution"], "completed")
        self.assertEqual(sum(bool(x.get("counted")) for x in self.graph.get_state(
            self.config).values["tool_access_ledger"]), 1)

    def test_completed_prefetch_rebuilds_pack_without_second_tool_read(self):
        import dealdesk_phase2.hybrid_pack as hybrid
        original = self.graph.update_state

        def interrupt(config, values, **kwargs):
            if "hybrid_evidence_pack" in values:
                raise KeyboardInterrupt("tool result saved, pack not yet saved")
            return original(config, values, **kwargs)

        with patch.object(self.graph, "update_state", side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.pack()
        with patch.object(hybrid, "FulfillmentTools", side_effect=AssertionError(
                "completed prefetch must not be reread")):
            pack, _ = self.pack()
        self.assertEqual(pack["observation"]["execution"], "completed")

    def test_reserved_prefetch_without_completed_result_is_terminal(self):
        from dealdesk_phase2.fulfillment_tools import FulfillmentTools
        original = FulfillmentTools.inspect_line_supply

        def crash_after_reserve(tools, **kwargs):
            with patch("dealdesk_phase2.fulfillment_tools.complete", side_effect=KeyboardInterrupt):
                return original(tools, **kwargs)

        with patch.object(FulfillmentTools, "inspect_line_supply", crash_after_reserve):
            with self.assertRaises(KeyboardInterrupt):
                self.pack()
        with self.assertRaisesRegex(HybridContractError, "prefetch_outcome_uncertain"):
            self.pack()

    def test_tampered_pack_or_frozen_policy_fails_without_new_read(self):
        pack, _ = self.pack()
        self.graph.update_state(self.config, {"hybrid_evidence_pack": {
            **pack, "model_input": {**pack["model_input"], "requested_quantity": "999"}}},
            as_node="finish")
        with patch("dealdesk_phase2.hybrid_pack.FulfillmentTools", side_effect=AssertionError(
                "tamper must not cause reexecution")), self.assertRaises(EvidenceMismatch):
            self.pack()


if __name__ == "__main__":
    unittest.main()
