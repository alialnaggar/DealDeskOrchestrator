"""Groq wire serialization is offline, strict, and separate from iterative."""

import json
import http.client
from io import BytesIO
from urllib.error import URLError
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.hybrid_contracts import ACTION_VERSION, HybridContractError
from dealdesk_phase2.hybrid_provider import (GroqHybridAdapter, OfflineGroqWireDouble,
                                             GroqHybridTransportModel, PROMPT_VERSION,
                                             WIRE_VERSION)
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from test_investigation_graph import InvestigationAdapter, RUN


def wire_call(name, args, *, call_id=None):
    return {"choices": [{"finish_reason": "tool_calls", "message": {"content": None,
        "tool_calls": [{**({"id": call_id} if call_id is not None else {}),
                        "type": "function", "function": {"name": name,
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
        self.assertEqual(self.adapter.prompt_version, PROMPT_VERSION)
        self.assertNotEqual(PROMPT_VERSION, WIRE_VERSION)
        self.assertEqual(OfflineGroqWireDouble([]).prompt_version, PROMPT_VERSION)
        self.assertEqual(body["tool_choice"], "required")
        self.assertFalse(body["parallel_tool_calls"])
        self.assertNotIn("submit_proposal", [x["function"]["name"] for x in body["tools"]])
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
        with self.assertRaisesRegex(HybridContractError, "binding_paths_required"):
            self.adapter.final_request(intent, self.input, ())
        observations = ({"tool": "inspect_fulfillment_paths", "execution": "completed",
            "evidence": "eligible_binding", "more_in_sealed_pool": False,
            "findings": {"line_id": "L1", "binding_options": [{"arrival": "2026-09-03"}]}},)
        body = self.adapter.decision_request(self.input, observations)
        self.assertIn("submit_proposal", [x["function"]["name"] for x in body["tools"]])
        request = self.adapter.final_request(intent, self.input, observations)
        self.assertNotIn("tools", request)
        self.assertTrue(request["response_format"]["json_schema"]["strict"])
        self.assertEqual(request["response_format"]["json_schema"]["schema"][
            "properties"]["payload"]["properties"]["tradeoff_code"]["enum"],
            ["partial_delivery_requires_customer_acceptance"])
        self.assertIn("inventory:<id>", request["response_format"]["json_schema"][
            "schema"]["properties"]["payload"]["properties"]["delivery_slices"][
                "items"]["properties"]["source_refs"]["items"]["description"])

    def test_incomplete_or_wrong_line_paths_do_not_enable_proposal(self):
        for status, more, line, options in (("eligible_binding", True, "L1", [{}]),
                                            ("eligible_binding", False, "L2", [{}]),
                                            ("unsupported_capability", False, "L1", [{}]),
                                            ("stale_evidence", False, "L1", [{}]),
                                            ("conditional", False, "L1", [{}]),
                                            ("eligible_binding", False, "L1", [])):
            with self.subTest(status=status, more=more, line=line, options=options):
                observed = ({"tool": "inspect_fulfillment_paths", "execution": "completed",
                    "evidence": status, "more_in_sealed_pool": more,
                    "findings": {"line_id": line, "binding_options": options}},)
                body = self.adapter.decision_request(self.input, observed)
                self.assertNotIn("submit_proposal", [x["function"]["name"]
                                  for x in body["tools"]])

    def test_observed_early_submission_stops_before_structured_final(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_offline

        graph = build_original_graph(InvestigationAdapter(), None, InMemorySaver())
        config = {"configurable": {"thread_id": "HYBRID-EARLY-SUBMISSION"}}
        double = OfflineGroqWireDouble([wire_call("submit_proposal", {
            "submission_kind": "binding_partial_delivery"})])
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            state = run_hybrid_offline(graph, config, InvestigationAdapter(), None, double,
                assessment_id="HYBRID-EARLY-SUBMISSION", run_id=RUN,
                reservation_dir=Path(directory))
        self.assertEqual([x["stage"] for x in state["hybrid_execution"]["attempts"]],
                         ["decision"])
        self.assertEqual(state["investigation_status"], "error")
        self.assertEqual(state["candidate_status"], "not_started")
        self.assertEqual(state["hybrid_execution"]["rejections"][0]["code"],
                         "binding_paths_required")
        self.assertEqual(state["reviewer_package"]["audit_rejection_count"], 1)
        self.assertEqual(state["reviewer_package"]["hybrid_audit"]["rejection_codes"],
                         ["binding_paths_required"])
        self.assertNotIn("raw", str(state["reviewer_package"]["hybrid_audit"]))

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

    def test_native_followup_pairs_original_call_id_with_authorized_result(self):
        observation = {"tool": "inspect_fulfillment_paths", "execution": "completed",
                       "returned_refs": ["inventory:synthetic"], "findings": {"line_id": "L1"}}
        call = wire_call("inspect_fulfillment_paths", {"line_id": "L1",
            "purpose_code": "check_dated_path"}, call_id="call_offline_1")["choices"][0][
            "message"]["tool_calls"][0]
        body = GroqHybridTransportModel().request_decision({"line_id": "L1"},
            ({"tool": "inspect_line_supply", "execution": "completed"}, observation),
            prior_call=call, tool_result=observation)
        messages = body["messages"]
        self.assertEqual([message["role"] for message in messages],
                         ["system", "user", "assistant", "tool"])
        self.assertEqual(messages[2]["tool_calls"][0]["id"], messages[3]["tool_call_id"])
        self.assertEqual(messages[3]["name"], "inspect_fulfillment_paths")
        self.assertEqual(json.loads(messages[3]["content"]), observation)
        self.assertEqual(len(json.loads(messages[1]["content"])["observations"]), 1)
        self.assertNotIn("response_format", body)
        self.assertFalse(body["parallel_tool_calls"])
        for bad_call, bad_result in (({**call, "id": ""}, observation),
                                     (call, {**observation, "tool": "inspect_evidence_record"}),
                                     ({**call, "type": "other"}, observation)):
            with self.subTest(call=bad_call, result=bad_result), self.assertRaises(
                    HybridContractError):
                GroqHybridTransportModel().request_decision({"line_id": "L1"},
                    ({"tool": "inspect_line_supply"}, observation),
                    prior_call=bad_call, tool_result=bad_result)

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

    def test_reserved_wire_is_sent_without_rebuilding_or_changing_digest(self):
        from hashlib import sha256
        from dealdesk_phase2.hybrid_pack import _canonical
        from dealdesk_phase2.hybrid_offline import run_hybrid_offline
        import tempfile
        from pathlib import Path

        assessment = "HYBRID-ONE-BUILD-OFFLINE"
        graph = build_original_graph(InvestigationAdapter(), None, InMemorySaver())
        config = {"configurable": {"thread_id": assessment}}
        double = OfflineGroqWireDouble([wire_call("abstain", {}), wire_final("abstain", {
            "reason_code": "model_uncertainty", "scope": "L1", "missing_evidence": []})])
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, patch.object(
                double, "request_decision", wraps=double.request_decision) as decision_build, patch.object(
                double, "request_final", wraps=double.request_final) as final_build:
            state = run_hybrid_offline(graph, config, InvestigationAdapter(), None, double,
                assessment_id=assessment, run_id=RUN, reservation_dir=Path(directory))
        self.assertEqual((decision_build.call_count, final_build.call_count), (1, 1))
        self.assertEqual([sha256(_canonical(body).encode()).hexdigest()
                          for body in double.requests],
                         [attempt["request_sha256"] for attempt in state["hybrid_execution"][
                             "attempts"]])

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

    def test_hosted_http_statuses_are_sanitized_and_never_read_error_body(self):
        from unittest.mock import Mock
        from dealdesk_phase2.live_models import ProviderError

        for status in (401, 403, 404, 429):
            with self.subTest(status=status):
                body = Mock()
                body.read.side_effect = AssertionError("no provider error body")
                error = HTTPError("https://example.invalid", status, "private error",
                                  {"Authorization": "private"}, body)
                with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_" + "x" * 48}), patch(
                        "dealdesk_phase2.live_models.build_opener") as opener:
                    opener.return_value.open.side_effect = error
                    with self.assertRaisesRegex(ProviderError, "http_" + str(status)):
                        GroqHybridTransportModel().decide({"line_id": "L1"}, ())
                opener.assert_called_once()
                post = opener.return_value.open
                post.assert_called_once()
                self.assertEqual(post.call_args.args[0].get_header("Authorization"),
                                 "Bearer gsk_" + "x" * 48)
                body.read.assert_not_called()

    def test_hosted_fault_categories_and_partial_response_are_sanitized(self):
        from dealdesk_phase2.live_models import _post, ProviderError
        key = "private-token"
        for failure, code in ((URLError(TimeoutError(key)), "transport_timeout"),
                              (ConnectionResetError(key), "transport_connection_lost"),
                              (URLError(ConnectionRefusedError(key)), "transport_connection_failure"),
                              (http.client.IncompleteRead(b'{"private":', 12),
                               "transport_protocol_failure")):
            with self.subTest(code=code), patch("dealdesk_phase2.live_models.build_opener") as opener:
                opener.return_value.open.side_effect = failure
                with self.assertRaises(ProviderError) as caught:
                    _post("https://api.groq.com/openai/v1/chat/completions", key,
                          "Authorization", {}, classify_transport=True, reject_redirects=True)
                self.assertEqual(str(caught.exception), code)
                self.assertNotIn(key, str(caught.exception))

        class Response:
            def __init__(self, data): self.data = BytesIO(data)
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size): return self.data.read(size)

        for data, code in ((b'{"choices":', "invalid_provider_json"),
                           (b'null', "invalid_provider_response"),
                           (b'x' * 16385, "provider_response_oversize")):
            with self.subTest(code=code), patch("dealdesk_phase2.live_models.build_opener") as opener:
                opener.return_value.open.return_value = Response(data)
                with self.assertRaises(ProviderError) as caught:
                    _post("https://api.groq.com/openai/v1/chat/completions", key,
                          "Authorization", {}, classify_transport=True, reject_redirects=True)
                self.assertEqual(str(caught.exception), code)

    def test_hybrid_transport_rejects_redirect_instead_of_forwarding_key(self):
        from dealdesk_phase2.live_models import ProviderError
        from unittest.mock import Mock

        body = Mock()
        redirect = HTTPError("https://api.groq.com/openai/v1/chat/completions", 302,
                             "redirect", {"Location": "https://example.invalid"}, body)
        with patch.dict("os.environ", {"GROQ_API_KEY": "gsk_" + "x" * 48}), patch(
                "dealdesk_phase2.live_models.build_opener") as opener:
            opener.return_value.open.side_effect = redirect
            with self.assertRaisesRegex(ProviderError, "http_302"):
                GroqHybridTransportModel().decide({"line_id": "L1"}, ())
        self.assertEqual(opener.return_value.open.call_count, 1)
        body.read.assert_not_called()

    def test_hosted_401_reserves_one_attempt_and_never_retries(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation
        from dealdesk_phase2.live_models import ProviderError

        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        config = {"configurable": {"thread_id": "HYBRID-HTTP-401-OFFLINE"}}
        model = GroqHybridTransportModel()
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, patch.object(
                model, "_take", side_effect=ProviderError("http_401")) as sender:
            with self.assertRaisesRegex(ProviderError, "http_401"):
                run_hybrid_evaluation(graph, config, adapter, None, model,
                    assessment_id="HYBRID-HTTP-401-OFFLINE", run_id=RUN,
                    reservation_dir=Path(directory), authorized=True)
            self.assertEqual(sender.call_count, 1)
            with self.assertRaisesRegex(HybridContractError, "hybrid_send_outcome_uncertain"):
                run_hybrid_evaluation(graph, config, adapter, None, model,
                    assessment_id="HYBRID-HTTP-401-OFFLINE", run_id=RUN,
                    reservation_dir=Path(directory), authorized=True)
            self.assertEqual(sender.call_count, 1)

    def test_hosted_usage_missing_or_over_cap_stops_after_saved_raw(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation

        for raw in (wire_call("abstain", {}),
                    {**wire_call("abstain", {}), "usage": {"completion_tokens": 513}}):
            with self.subTest(usage=raw.get("usage")), tempfile.TemporaryDirectory(
                    dir="/tmp/opencode") as directory:
                adapter = InvestigationAdapter()
                graph = build_original_graph(adapter, None, InMemorySaver())
                config = {"configurable": {"thread_id": "HYBRID-USAGE-" + str(len(raw))}}
                model = GroqHybridTransportModel()
                with patch.object(model, "_take", return_value=raw) as sender:
                    with self.assertRaisesRegex(HybridContractError, "hosted_usage_unverifiable"):
                        run_hybrid_evaluation(graph, config, adapter, None, model,
                            assessment_id=config["configurable"]["thread_id"], run_id=RUN,
                            reservation_dir=Path(directory), authorized=True)
                    self.assertEqual(sender.call_count, 1)
                    self.assertEqual(graph.get_state(config).values[
                        "hybrid_execution"]["attempts"][0]["raw"], raw)
                    with self.assertRaisesRegex(HybridContractError, "hosted_usage_unverifiable"):
                        run_hybrid_evaluation(graph, config, adapter, None, model,
                            assessment_id=config["configurable"]["thread_id"], run_id=RUN,
                            reservation_dir=Path(directory), authorized=True)
                    sender.assert_called_once()

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
            "purpose_code": "check_dated_path"}, call_id="call_offline_first")
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

    def test_hosted_missing_tool_call_id_stops_before_second_reservation(self):
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation
        import tempfile
        from pathlib import Path

        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        model = GroqHybridTransportModel()
        first = wire_call("inspect_fulfillment_paths", {"line_id": "L1",
            "purpose_code": "check_dated_path"})
        first["usage"] = {"prompt_tokens": 300, "completion_tokens": 100}
        assessment = "HYBRID-MISSING-TOOL-ID-OFFLINE"
        config = {"configurable": {"thread_id": assessment}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, patch.object(
                model, "_take", side_effect=[first, AssertionError("second send")]) as sender:
            with self.assertRaisesRegex(HybridContractError, "invalid_groq_tool_exchange"):
                run_hybrid_evaluation(graph, config, adapter, None, model,
                    assessment_id=assessment, run_id=RUN,
                    reservation_dir=Path(directory), authorized=True)
            sender.assert_called_once()
            record = graph.get_state(config).values["hybrid_execution"]
            self.assertEqual(len(record["attempts"]), 1)
            self.assertIsNone(record["pending"])
            self.assertEqual(len(list(Path(directory).glob("*.hybrid.audit.jsonl"))), 2)

    def test_hosted_request_bytes_checked_before_receipt_and_send(self):
        import tempfile
        from pathlib import Path
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation

        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        model = GroqHybridTransportModel()
        original = model.request_decision

        def oversized(input, observations, **kwargs):
            body = original(input, observations, **kwargs)
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
