"""Groq wire serialization is offline, strict, and separate from iterative."""

import json
import unittest
from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.hybrid_contracts import ACTION_VERSION, HybridContractError
from dealdesk_phase2.hybrid_provider import (GroqHybridAdapter, OfflineGroqWireDouble,
                                            GroqHybridTransportModel)
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from test_investigation_graph import InvestigationAdapter, RUN


def wire_call(name, args):
    return {"choices": [{"finish_reason": "tool_calls", "message": {"content": None,
        "tool_calls": [{"type": "function", "function": {"name": name,
                          "arguments": json.dumps(args)}}]}}]}


def wire_final(kind, payload):
    return {"choices": [{"finish_reason": "stop", "message": {
        "content": json.dumps({"version": ACTION_VERSION, "kind": kind,
                               "payload": payload})}}]}


class WireTests(unittest.TestCase):
    def setUp(self):
        self.adapter = GroqHybridAdapter()
        self.tools = ("inspect_line_supply", "inspect_fulfillment_paths",
                      "inspect_evidence_record")
        self.input = {"line_id": "L1", "permitted_tools": self.tools}

    def test_explicit_native_intent_and_no_ready_transition(self):
        body = self.adapter.decision_request(self.input, ())
        self.assertEqual(body["tool_choice"], "required")
        self.assertFalse(body["parallel_tool_calls"])
        self.assertNotIn("READY", body["messages"][0]["content"].replace("Never return READY", ""))
        for invalid in ({"choices": [{"finish_reason": "stop", "message": {"content": "READY"}}]},
                        {"choices": [{"finish_reason": "tool_calls", "message": {
                            "tool_calls": wire_call("abstain", {})["choices"][0]["message"][
                                "tool_calls"] * 2}}]}):
            with self.assertRaises(HybridContractError):
                self.adapter.parse_decision(invalid, "L1", self.tools)
        intent = self.adapter.parse_decision(wire_call("submit_proposal", {
            "submission_kind": "binding_partial_delivery"}), "L1", self.tools)
        self.assertEqual(intent["kind"], "submit_proposal")
        request = self.adapter.final_request(intent, self.input, ())
        self.assertNotIn("tools", request)
        self.assertTrue(request["response_format"]["json_schema"]["strict"])

    def test_wrong_kind_extra_calls_and_invalid_json_rejected(self):
        intent = {"version": ACTION_VERSION, "kind": "abstain"}
        for response in (wire_final("submit_finding", {}),
                         wire_call("inspect_line_supply", {"line_id": "L1"}),
                         {"choices": [{"finish_reason": "stop", "message": {
                             "content": "not-json"}}]}):
            with self.assertRaises(HybridContractError):
                self.adapter.parse_final(response, intent)
        with self.assertRaises(HybridContractError):
            self.adapter.parse_decision(wire_call("inspect_fulfillment_paths", {
                "line_id": "other", "purpose_code": "check_dated_path"}), "L1", self.tools)

    def test_wire_double_enters_offline_graph_no_transport(self):
        from dealdesk_phase2.hybrid_offline import run_hybrid_offline
        import tempfile
        from pathlib import Path
        import uuid

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            original = build_original_graph(InvestigationAdapter(), None, InMemorySaver())
            assessment = "WIRE-OFFLINE-" + str(uuid.uuid4())
            config = {"configurable": {"thread_id": assessment}}
            original.invoke(initial_state(assessment, RUN), config)
            double = OfflineGroqWireDouble([wire_call("abstain", {}), wire_final("abstain", {
                "reason_code": "model_uncertainty", "scope": "L1", "missing_evidence": []})])
            state = run_hybrid_offline(original, config, InvestigationAdapter(), None, double,
                assessment_id=assessment, run_id=RUN, reservation_dir=Path(directory))
            self.assertEqual(state["investigation_status"], "completed")
            self.assertEqual(len(double.requests), 2)
            self.assertEqual(state["reviewer_package"]["candidates"], [])
            self.assertEqual(state["hybrid_execution"]["attempts"][0]["raw"],
                             wire_call("abstain", {}))
            self.assertNotIn("tools", double.requests[1])

    def test_evaluation_gate_blocks_transport_before_any_checkpoint_or_network(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation

        model = GroqHybridTransportModel()
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            graph = build_original_graph(InvestigationAdapter(), None, InMemorySaver())
            config = {"configurable": {"thread_id": "GROQ-HYBRID-GATE-OFF"}}
            with patch("dealdesk_phase2.live_models._post", side_effect=AssertionError(
                    "No hosted request allowed")) as sender:
                with self.assertRaisesRegex(HybridContractError,
                                            "hosted_evaluation_not_authorized"):
                    run_hybrid_evaluation(graph, config, InvestigationAdapter(), None, model,
                        assessment_id="GROQ-HYBRID-GATE-OFF", run_id=RUN,
                        reservation_dir=Path(directory))
                sender.assert_not_called()
            self.assertFalse(graph.get_state(config).values)

    def test_groq_transport_body_uses_existing_post_only_when_mocked(self):
        model = GroqHybridTransportModel()
        response = wire_call("abstain", {})
        with patch.dict("os.environ", {"GROQ_API_KEY": "offline-test-key"}), patch(
                "dealdesk_phase2.live_models._post", return_value=response) as mocked:
            self.assertEqual(model.decide({"line_id": "L1"}, ()), response)
        self.assertEqual(mocked.call_count, 1)
        self.assertEqual(mocked.call_args.args[3], model.requests[0])

    def test_hosted_hard_cap_stops_second_inspection_before_third_send(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation, HOSTED_BUDGET
        import uuid

        assessment = "SMOKE-OFFLINE-" + str(uuid.uuid4())
        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        config = {"configurable": {"thread_id": assessment}}
        model = GroqHybridTransportModel()
        inspection = wire_call("inspect_fulfillment_paths", {"line_id": "L1",
            "purpose_code": "check_dated_path"})
        inspection["usage"] = {"completion_tokens": 100, "prompt_tokens": 300}
        responses = iter((inspection, inspection))
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, patch.object(
                model, "_take", side_effect=lambda body: next(responses)) as sender:
            state = run_hybrid_evaluation(graph, config, adapter, None, model,
                assessment_id=assessment, run_id=RUN, reservation_dir=Path(directory),
                authorized=True)
            self.assertEqual(sender.call_count, 2)
            self.assertEqual(state["investigation_status"], "error")
            self.assertEqual(state["hybrid_execution"]["hosted_budget"], HOSTED_BUDGET)
            self.assertEqual(len(state["hybrid_execution"]["attempts"]), 2)
            self.assertEqual(state["reviewer_package"]["candidates"], [])

    def test_hosted_request_bytes_checked_before_receipt_and_send(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation

        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        model = GroqHybridTransportModel()
        original = model.request_decision

        def oversized(input, observations):
            body = original(input, observations)
            body["messages"][0]["content"] += "x" * 8192
            return body

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, patch.object(
                model, "request_decision", side_effect=oversized), patch.object(
                    model, "_take", side_effect=AssertionError("must not send")) as sender:
            with self.assertRaisesRegex(HybridContractError, "hosted_wire_budget_exceeded"):
                run_hybrid_evaluation(graph, {"configurable": {"thread_id":
                    "SMOKE-OVERSIZE"}}, adapter, None, model,
                    assessment_id="SMOKE-OVERSIZE", run_id=RUN,
                    reservation_dir=Path(directory), authorized=True)
            sender.assert_not_called()
            self.assertEqual(list(Path(directory).glob("*.hybrid.audit.jsonl"))[-1].stat().st_size, 0)

    def test_hosted_smoke_has_two_decision_and_one_final_token_ceilings(self):
        model = GroqHybridTransportModel()
        self.assertEqual(model.request_decision({"line_id": "L1"}, ())[
            "max_completion_tokens"], 512)
        self.assertEqual(model.request_final({"kind": "abstain"}, {"line_id": "L1"}, ())[
            "max_completion_tokens"], 1024)
        with self.assertRaisesRegex(HybridContractError, "hosted_revision_disabled"):
            model.request_revision_intent({}, {"line_id": "L1"}, ())


if __name__ == "__main__":
    unittest.main()
