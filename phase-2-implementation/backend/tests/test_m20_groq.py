"""No-network native Groq tool wire and explicitly gated hosted checkpoint tests."""

import io
import json
import os
from pathlib import Path
import tempfile
from hashlib import sha256
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from uuid import uuid4

from dealdesk_phase2.m20_groq import (GroqM20Model, WIRE_VERSION, PROMPT_VERSION,
                                        MAX_REQUEST_BYTES, parse_response, request_body,
                                        system_instruction)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m20_specialists import build_m20_graph, run_m20_evaluation
from dealdesk_phase2.live_models import GROQ_MODEL, ProviderError, _json, _post
from dealdesk_phase2.tool_response_diagnostic import ToolResponseError
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


def tool_response(name, arguments, *, usage=None, call_id="call_offline_test"):
    return {"choices": [{"finish_reason": "tool_calls", "message": {
        "content": None, "tool_calls": [{"id": call_id, "type": "function", "function": {
            "name": name, "arguments": json.dumps(arguments)}}]}}],
        "usage": usage or {"prompt_tokens": 300, "completion_tokens": 60}}


class GroqM20Wire(unittest.TestCase):
    def setUp(self):
        self.input = {"specialist": "configuration", "permitted_tool":
                      "inspect_configuration_line", "line_ids": ["L1"]}

    def test_native_tool_only_bounded_request_and_typed_exact_values(self):
        body = request_body(self.input, ())
        self.assertEqual(body["model"], GROQ_MODEL)
        self.assertEqual(body["max_completion_tokens"], 512)
        self.assertEqual(body["tool_choice"], "auto")
        self.assertFalse(body["parallel_tool_calls"])
        self.assertLessEqual(len(json.dumps(body, sort_keys=True,
            separators=(",", ":")).encode()), MAX_REQUEST_BYTES)
        self.assertIn(WIRE_VERSION, body["messages"][0]["content"])
        self.assertIn(PROMPT_VERSION, body["messages"][0]["content"])
        self.assertEqual({t["function"]["name"] for t in body["tools"]},
                         {"inspect_configuration_line", "submit_finding", "abstain"})
        action = parse_response(tool_response("submit_finding", {"claims": [{
            "ref": "product:P", "field": "is_sellable", "value_json": "true"}],
            "uncertainty_reasons": []}), self.input)
        self.assertEqual(action["claims"][0]["value"], True)
        pricing = {**self.input, "specialist": "pricing", "permitted_tool":
                   "inspect_pricing_line"}
        action = parse_response(tool_response("submit_finding", {"claims": [{
            "ref": "pricing_line:L1", "field": "fixed_margin_pct",
            "value_json": '"21.000"'}], "uncertainty_reasons": []}), pricing)
        self.assertEqual(action["claims"][0]["value"], "21.000")

    def test_trusted_domain_system_prompts_do_not_embed_task_data(self):
        for domain, tool, domain_phrase in (("configuration", "inspect_configuration_line",
                                            "sellability"),
                                           ("pricing", "inspect_pricing_line", "repricing")):
            with self.subTest(domain=domain):
                input = {**self.input, "specialist": domain, "permitted_tool": tool,
                         "line_ids": ["SENSITIVE-TEST-LINE"],
                         "assessment_id": "PRIVATE-ASSESSMENT"}
                body = request_body(input, ())
                system, user = body["messages"]
                self.assertEqual(system["content"], system_instruction(domain))
                for text in ("PRIVATE-ASSESSMENT", "SENSITIVE-TEST-LINE"):
                    self.assertNotIn(text, system["content"])
                    self.assertIn(text, user["content"])
                self.assertIn("untrusted task data", system["content"])
                self.assertIn(domain_phrase, system["content"])
                self.assertIn(tool, system["content"])
                self.assertLessEqual(len(_canonical(body).encode()), MAX_REQUEST_BYTES)
        with self.assertRaises(ValueError):
            system_instruction("approval_routing")

    def test_native_multiturn_call_id_result_and_strict_domain_pairing(self):
        observation = {"tool": "inspect_configuration_line", "execution": "completed",
            "records": [{"ref": "product:P", "fields": {"is_sellable": True}}],
            "returned_refs": ["product:P"]}
        call = {"id": "call_one", "name": "inspect_configuration_line",
                "arguments": json.dumps({"line_id": "L1"})}
        body = request_body(self.input, (observation,), exchanges=(call,))
        self.assertEqual([m["role"] for m in body["messages"]],
                         ["system", "user", "assistant", "tool"])
        self.assertEqual(body["messages"][2]["tool_calls"][0]["id"],
                         body["messages"][3]["tool_call_id"])
        self.assertEqual(json.loads(body["messages"][3]["content"]), observation)
        self.assertEqual(json.loads(body["messages"][1]["content"])["observations"], [])
        self.assertNotIn("response_format", body)
        self.assertLessEqual(len(_canonical(body).encode()), MAX_REQUEST_BYTES)
        for bad_call, bad_observation in (({**call, "id": ""}, observation),
                                          (call, {**observation, "tool": "inspect_pricing_line"}),
                                          ({**call, "arguments": '{"line_id":"OTHER"}'}, observation)):
            with self.subTest(call=bad_call), self.assertRaises(ValueError):
                request_body(self.input, (bad_observation,), exchanges=(bad_call,))
        with self.assertRaises(ValueError):
            request_body(self.input, (observation,))

    def test_pricing_and_configuration_followups_have_identical_contract_shape(self):
        shapes = []
        for specialist in ("configuration", "pricing"):
            name = "inspect_" + specialist + "_line"
            observation = {"tool": name, "execution": "completed", "records": [{
                "ref": "product:P" if specialist == "configuration" else "pricing_line:L1",
                "fields": {"is_sellable": True} if specialist == "configuration" else {
                    "fixed_margin_pct": "22.22222222222222222222222222"}}],
                "returned_refs": ["product:P" if specialist == "configuration" else
                                  "pricing_line:L1"]}
            input = {**self.input, "specialist": specialist, "permitted_tool": name}
            call = {"id": "call_native_123", "name": name,
                    "arguments": json.dumps({"line_id": "L1"})}
            body = request_body(input, (observation,), exchanges=(call,))
            self.assertLessEqual(len(_canonical(body).encode()), MAX_REQUEST_BYTES)
            messages = body["messages"]
            self.assertEqual(messages[-2]["tool_calls"][0]["id"],
                             messages[-1]["tool_call_id"])
            self.assertEqual(json.loads(messages[-1]["content"]), observation)
            self.assertEqual(body["max_completion_tokens"], 512)
            self.assertEqual(body["tool_choice"], "auto" if specialist ==
                             "configuration" else "required")
            self.assertIs(body["parallel_tool_calls"], False)
            if specialist == "configuration":
                self.assertEqual(body["reasoning_format"], "parsed")
            else:
                self.assertNotIn("reasoning_format", body)
            shapes.append((sorted(k for k in body if k != "reasoning_format"),
                [m["role"] for m in messages],
                [t["function"]["name"] for t in body["tools"]][1:]))
        self.assertEqual(shapes[0], shapes[1])

    def test_actual_http_serialization_of_both_followups_without_network(self):
        """Inspect the bytes passed to urllib, not just the typed message list."""
        for specialist in ("configuration", "pricing"):
            with self.subTest(specialist=specialist):
                name = "inspect_" + specialist + "_line"
                input = {**self.input, "specialist": specialist, "permitted_tool": name}
                observation = {"tool": name, "execution": "completed", "records": [{
                    "ref": "product:P" if specialist == "configuration" else "pricing_line:L1",
                    "fields": {"label": "café", "is_sellable": True}}],
                    "returned_refs": ["product:P" if specialist == "configuration" else
                                      "pricing_line:L1"]}
                call = {"id": "call_offline_39_chars_00000000000000000", "name": name,
                        "arguments": '{"line_id":"L1"}'}
                body = request_body(input, (observation,), exchanges=(call,))
                captured = []

                class OfflineOpener:
                    def open(self, request, timeout):
                        captured.append((request, timeout))
                        return io.BytesIO(json.dumps(tool_response("submit_finding", {
                            "claims": [], "uncertainty_reasons": []})).encode())

                with patch("dealdesk_phase2.live_models.build_opener",
                           return_value=OfflineOpener()) as opener:
                    response = _post("https://api.groq.com/openai/v1/chat/completions",
                                     "Bearer offline-test", "Authorization", body,
                                     classify_transport=True, reject_redirects=True)
                self.assertEqual(len(response["choices"]), 1)
                self.assertEqual(opener.call_count, 1)
                request, timeout = captured[0]
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(request.get_header("Content-type"), "application/json")
                self.assertEqual(request.get_header("Authorization"), "Bearer offline-test")
                self.assertEqual(timeout, 30)
                self.assertEqual(request.data, _json(body).encode("utf-8"))
                self.assertEqual(request.data, _canonical(body).encode("utf-8"))
                wire = json.loads(request.data)
                self.assertEqual([m["role"] for m in wire["messages"]],
                                 ["system", "user", "assistant", "tool"])
                self.assertEqual(wire["messages"][2]["tool_calls"][0]["id"],
                                 wire["messages"][3]["tool_call_id"])
                self.assertEqual(json.loads(wire["messages"][3]["content"]), observation)
                self.assertEqual(wire["messages"][3]["name"], name)
                self.assertEqual(wire["max_completion_tokens"], 512)
                self.assertEqual(wire["tool_choice"], "auto" if specialist ==
                                 "configuration" else "required")
                self.assertFalse(wire["parallel_tool_calls"])
                self.assertNotIn("response_format", wire)
                self.assertLessEqual(len(request.data), MAX_REQUEST_BYTES)

    def test_pricing_second_turn_http_error_is_sanitized_at_real_transport(self):
        """A mocked HTTP 400 proves containment, not why Groq rejected a body."""
        input = {**self.input, "specialist": "pricing",
                 "permitted_tool": "inspect_pricing_line"}
        observation = {"tool": "inspect_pricing_line", "execution": "completed",
                       "records": [{"ref": "pricing_line:L1", "fields": {
                           "fixed_margin_pct": "21.000"}}],
                       "returned_refs": ["pricing_line:L1"]}
        call = {"id": "call_offline_pricing", "name": "inspect_pricing_line",
                "arguments": '{"line_id":"L1"}'}
        body = request_body(input, (observation,), exchanges=(call,))

        class UnreadableBody(io.BytesIO):
            def read(self, *args, **kwargs):
                raise AssertionError("Provider error body must never be read")

        class OfflineOpener:
            attempts = 0
            wire = None

            def open(self, request, timeout):
                self.attempts += 1
                self.wire = request.data
                raise HTTPError(request.full_url, 400, "offline provider rejection", {},
                                UnreadableBody(b"private provider details"))

        opener = OfflineOpener()
        with patch("dealdesk_phase2.live_models.build_opener", return_value=opener):
            with self.assertRaises(ProviderError) as caught:
                _post("https://api.groq.com/openai/v1/chat/completions",
                      "Bearer offline-test", "Authorization", body,
                      classify_transport=True, reject_redirects=True)
        self.assertEqual(caught.exception.code, "http_400")
        self.assertEqual(opener.attempts, 1)
        self.assertEqual(opener.wire, _json(body).encode("utf-8"))

    def test_fail_closed_on_malformed_parallel_wrong_domain_and_prose(self):
        valid = tool_response("inspect_configuration_line", {"line_id": "L1"})
        for response in ({**valid, "choices": [{**valid["choices"][0],
                              "finish_reason": "stop"}]},
                         tool_response("inspect_pricing_line", {"line_id": "L1"}),
                         tool_response("submit_finding", {"claims": [{
                             "ref": "product:P", "field": "is_sellable",
                             "value_json": "invalid"}], "uncertainty_reasons": []}),
                         {**valid, "choices": [valid["choices"][0]] * 2},
                         {**valid, "choices": [{**valid["choices"][0], "message": {
                             **valid["choices"][0]["message"], "content": "approved"}}]}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                parse_response(response, self.input)
        with self.assertRaises(ValueError):
            request_body({**self.input, "permitted_tool": "inspect_pricing_line"}, ())

    def test_rejected_native_response_categories_are_bounded_and_content_free(self):
        valid = tool_response("inspect_configuration_line", {"line_id": "L1"})
        choice = valid["choices"][0]
        message = choice["message"]
        call = message["tool_calls"][0]
        variations = (
            ({"choices": []}, "envelope"),
            ({**valid, "choices": [{**choice, "finish_reason": "length"}]}, "finish_reason"),
            ({**valid, "choices": [{**choice, "message": {**message,
                "content": "PRIVATE-provider-answer"}}]}, "message_content"),
            ({**valid, "choices": [{**choice, "message": {**message,
                "tool_calls": [call, call]}}]}, "tool_count"),
            ({**valid, "choices": [{**choice, "message": {**message,
                "tool_calls": [{**call, "id": ""}]}}]}, "tool_metadata"),
            (tool_response("inspect_pricing_line", {"line_id": "L1"}), "unsupported_tool"),
            ({**valid, "choices": [{**choice, "message": {**message, "tool_calls": [{
                **call, "function": {**call["function"], "arguments": "{private"}}]}}]},
                "arguments_json"),
            (tool_response("inspect_configuration_line", {"subject_id": "PRIVATE"}),
                "action_arguments"),
        )
        for response, category in variations:
            with self.subTest(category=category):
                with self.assertRaises(ToolResponseError) as caught:
                    parse_response(response, self.input)
                self.assertEqual(caught.exception.category, category)
                self.assertNotIn("PRIVATE", str(caught.exception))
        self.assertEqual(parse_response(valid, self.input)["kind"], "inspect")

    def test_mocked_transport_requires_usage_and_bounds_provider_response(self):
        model = GroqM20Model("configuration")
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                "dealdesk_phase2.m20_groq._post", return_value=tool_response(
                    "inspect_configuration_line", {"line_id": "L1"}, usage={
                        "prompt_tokens": 4097, "completion_tokens": 20})) as send:
            with self.assertRaisesRegex(ProviderError, "hosted_usage_unverifiable"):
                model.next_action(self.input, ())
            self.assertEqual(send.call_count, 1)
            self.assertFalse(model.last_usage)
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                "dealdesk_phase2.m20_groq._post", return_value=tool_response(
                    "inspect_configuration_line", {"line_id": "L1"}, usage={
                        "prompt_tokens": 100, "completion_tokens": 513})):
            with self.assertRaisesRegex(ProviderError, "hosted_usage_unverifiable"):
                model.next_action(self.input, ())
        with patch("dealdesk_phase2.m20_groq._post", side_effect=AssertionError("network")):
            with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(
                    ProviderError, "missing_credential"):
                model.next_action(self.input, ())

    def test_offline_graph_cannot_adopt_hosted_transport(self):
        with self.assertRaises(ValueError):
            build_m20_graph(None, {}, None, {name: GroqM20Model(name) for name in (
                "configuration", "pricing")})
        with self.assertRaisesRegex(ValueError, "reported token gate reached"):
            run_m20_evaluation(None, {}, None, {name: GroqM20Model(name) for name in (
                "configuration", "pricing")}, authorized=True, prior_reported_tokens=24000)


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Isolated M2.0 PostgreSQL business and checkpoint databases required")
class HostedWirePostgres(unittest.TestCase):
    def test_second_configuration_response_shape_is_audit_bounded_and_terminal(self):
        """Fresh offline B05: a returned but truncated tool turn cannot reach Pricing."""
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(os.environ["M20_DATABASE_URL"])
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(x for x in CASES if x.case_id == "B05")
        config = {"configurable": {"thread_id": "M20-SHAPE-" + uuid4().hex}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, thesis_checkpointer(
                os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            original = graph.invoke(initial_state(config["configurable"]["thread_id"],
                                                   case.run_id), config)
            sends = []
            def fake_post(url, key, header, body, **kwargs):
                sends.append(body)
                if len(sends) == 1:
                    return tool_response("inspect_configuration_line", {
                        "line_id": case.ids()["L"]}, call_id="call_shape")
                self.assertEqual([m["role"] for m in body["messages"]],
                                 ["system", "user", "assistant", "tool"])
                response = tool_response("submit_finding", {"claims": [],
                    "uncertainty_reasons": []})
                response["choices"][0]["finish_reason"] = "length"
                return response
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=fake_post) as sender:
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                        for name in ("configuration", "pricing")}, authorized=True,
                        reservation_dir=Path(directory))
                self.assertEqual(sender.call_count, 2)
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                        for name in ("configuration", "pricing")}, authorized=True,
                        reservation_dir=Path(directory))
                self.assertEqual(sender.call_count, 2)
            state = graph.get_state(config).values
            self.assertEqual(state["specialist_results"], original["specialist_results"])
            self.assertEqual(state["m20_ai_results"]["configuration"]["model_output_category"],
                             "finish_reason")
            self.assertNotIn("pricing", state["m20_ai_results"])
            self.assertEqual([x["status"] for x in state["m20_model_attempts"]],
                             ["reserved", "returned", "reserved"])

    def test_pricing_second_turn_http_400_stops_and_never_replays(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        database = os.environ["M20_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(x for x in CASES if x.case_id == "B01")
        config = {"configurable": {"thread_id": "M20-PRICING-400-NEW-OFFLINE-ID"}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                original = graph.invoke(initial_state(config["configurable"]["thread_id"],
                                                      case.run_id), config)
                sent = []
                def fake_post(url, key, header, body, **kwargs):
                    sent.append(body)
                    domain = json.loads(body["messages"][1]["content"])["input"]["specialist"]
                    if len(body["messages"]) == 2:
                        return tool_response("inspect_" + domain + "_line",
                            {"line_id": case.ids()["L"]}, call_id="call_" + domain)
                    self.assertEqual([m["role"] for m in body["messages"]],
                                     ["system", "user", "assistant", "tool"])
                    self.assertEqual(body["messages"][2]["tool_calls"][0]["id"],
                                     body["messages"][3]["tool_call_id"])
                    if domain == "pricing":
                        raise ProviderError("http_400")
                    row = json.loads(body["messages"][3]["content"])["records"][0]
                    return tool_response("submit_finding", {"claims": [{
                        "ref": row["ref"], "field": "is_sellable",
                        "value_json": json.dumps(row["fields"]["is_sellable"])}],
                        "uncertainty_reasons": []})
                with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                        "dealdesk_phase2.m20_groq._post", side_effect=fake_post) as sender:
                    with self.assertRaises(EvidenceMismatch):
                        run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                            for name in ("configuration", "pricing")}, authorized=True,
                            reservation_dir=Path(directory))
                    self.assertEqual(sender.call_count, 4)
                state = graph.get_state(config).values
                self.assertEqual(state["specialist_results"], original["specialist_results"])
                self.assertEqual(state["candidate_status"], "not_started")
                self.assertEqual(state["m20_ai_results"]["configuration"]["execution"], "completed")
                self.assertEqual(state["m20_ai_results"]["pricing"]["reason"], "provider_http_400")
                self.assertIsNone(state.get("m20_review"))
                self.assertEqual(state["reviewer_package"]["m20_ai"]["execution"], "stopped")
                self.assertEqual([x["status"] for x in state["m20_model_attempts"][-3:]],
                                 ["reserved", "returned", "reserved"])
                self.assertLessEqual(max(len(_canonical(body).encode()) for body in sent),
                                     MAX_REQUEST_BYTES)
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                        "dealdesk_phase2.m20_groq._post", side_effect=AssertionError(
                            "forbidden replay")) as sender:
                    with self.assertRaises(EvidenceMismatch):
                        run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                            for name in ("configuration", "pricing")}, authorized=True,
                            reservation_dir=Path(directory))
                    sender.assert_not_called()

    def test_second_turn_http_400_stops_without_pricing_or_restart_send(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        database = os.environ["M20_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(x for x in CASES if x.case_id == "B01")
        config = {"configurable": {"thread_id": "M20-WIRE-HTTP400-B01-OFFLINE"}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                original = graph.invoke(initial_state(config["configurable"]["thread_id"],
                                                      case.run_id), config)
                requests = []
                def fake_post(url, key, header, body, **kwargs):
                    requests.append(body)
                    if len(requests) == 1:
                        return tool_response("inspect_configuration_line", {"line_id": case.ids()["L"]},
                                             call_id="call_configuration")
                    self.assertEqual([x["role"] for x in body["messages"]],
                                     ["system", "user", "assistant", "tool"])
                    raise ProviderError("http_400")
                with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                        "dealdesk_phase2.m20_groq._post", side_effect=fake_post) as sender:
                    with self.assertRaises(EvidenceMismatch):
                        run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                            for name in ("configuration", "pricing")}, authorized=True,
                            reservation_dir=Path(directory))
                    self.assertEqual(sender.call_count, 2)
                state = graph.get_state(config).values
                self.assertEqual(state["specialist_results"], original["specialist_results"])
                self.assertEqual(state["m20_ai_results"]["configuration"]["reason"],
                                 "provider_http_400")
                self.assertNotIn("pricing", state["m20_ai_results"])
                self.assertEqual(state["reviewer_package"]["m20_ai"]["execution"], "stopped")
                self.assertEqual(len([x for x in state["m20_model_attempts"] if x[
                    "status"] == "reserved"]), 2)
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                        "dealdesk_phase2.m20_groq._post", side_effect=AssertionError(
                            "no replay")) as sender:
                    with self.assertRaises(EvidenceMismatch):
                        run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                            for name in ("configuration", "pricing")}, authorized=True,
                            reservation_dir=Path(directory))
                    sender.assert_not_called()

    def test_missing_information_abstention_keeps_fixed_results_and_handoff(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        database = os.environ["M20_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(x for x in CASES if x.case_id == "B01")
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, thesis_checkpointer(
                os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            config = {"configurable": {"thread_id": "M20-WIRE-ABSTAIN-B01-OFFLINE"}}
            original = graph.invoke(initial_state(config["configurable"]["thread_id"], case.run_id),
                                    config)
            sends = []
            def fake_post(url, key, header, body, **kwargs):
                sends.append(body)
                domain = json.loads(body["messages"][1]["content"])["input"]["specialist"]
                if len(body["messages"]) == 2:
                    return tool_response("inspect_" + domain + "_line", {"line_id": case.ids()["L"]},
                                         call_id="call_" + domain)
                self.assertEqual(body["messages"][2]["tool_calls"][0]["id"],
                                 body["messages"][3]["tool_call_id"])
                return tool_response("abstain", {"reason_code": "insufficient_evidence"})
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=fake_post):
                state = run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                    for name in ("configuration", "pricing")}, authorized=True,
                    reservation_dir=Path(directory))
            self.assertEqual(len(sends), 4)
            self.assertEqual(state["specialist_results"], original["specialist_results"])
            self.assertEqual(state["candidate_status"], "not_started")
            for domain in ("configuration", "pricing"):
                self.assertEqual(state["m20_ai_results"][domain]["execution"], "abstained")
                self.assertEqual(state["m20_review"]["specialists"][domain]["validated_claims"], [])
            self.assertEqual(state["reviewer_package"]["m20_ai"], state["m20_review"])

    def test_missing_provider_tool_id_stops_before_followup_or_pricing(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        database = os.environ["M20_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(x for x in CASES if x.case_id == "B01")
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory, thesis_checkpointer(
                os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            config = {"configurable": {"thread_id": "M20-WIRE-NO-ID-B01-OFFLINE"}}
            graph.invoke(initial_state(config["configurable"]["thread_id"], case.run_id), config)
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", return_value=tool_response(
                        "inspect_configuration_line", {"line_id": case.ids()["L"]},
                        call_id="")) as sender:
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, {name: GroqM20Model(name)
                        for name in ("configuration", "pricing")}, authorized=True,
                        reservation_dir=Path(directory))
                sender.assert_called_once()
            self.assertEqual(graph.get_state(config).values["m20_ai_results"][
                "configuration"]["execution"], "error")
            self.assertNotIn("pricing", graph.get_state(config).values["m20_ai_results"])

    def test_explicit_gate_real_tool_mocked_transport_restart_and_bad_claim_stop(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        directory = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(directory.cleanup)
        receipt_dir = Path(directory.name)
        database = os.environ["M20_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)
        case = next(item for item in CASES if item.case_id == "B05")
        def models():
            return {name: GroqM20Model(name) for name in ("configuration", "pricing")}
        with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            assessment = "M20-GROQ-WIRE-OFFLINE-B05-" + uuid4().hex
            config = {"configurable": {"thread_id": assessment}}
            original = graph.invoke(initial_state(assessment, case.run_id), config)
            with patch("dealdesk_phase2.live_models._post", side_effect=AssertionError(
                    "closed gate sent a request")) as sender:
                with self.assertRaises(ValueError):
                    run_m20_evaluation(graph, config, adapter, models(),
                                       reservation_dir=receipt_dir)
                sender.assert_not_called()

            requests = []
            def fake_post(url, key, header, body, **kwargs):
                requests.append(body)
                input = json.loads(body["messages"][1]["content"])
                specialist = input["input"]["specialist"]
                if len(body["messages"]) == 2:
                    return tool_response("inspect_" + specialist + "_line", {
                        "line_id": input["input"]["line_ids"][0]},
                        call_id="call_" + specialist)
                self.assertEqual([m["role"] for m in body["messages"]],
                                 ["system", "user", "assistant", "tool"])
                self.assertEqual(body["messages"][2]["tool_calls"][0]["id"],
                                 body["messages"][3]["tool_call_id"])
                row = json.loads(body["messages"][-1]["content"])["records"][0]
                field = "is_sellable" if specialist == "configuration" else "fixed_margin_pct"
                return tool_response("submit_finding", {"claims": [{"ref": row["ref"],
                    "field": field, "value_json": json.dumps(row["fields"][field])}],
                    "uncertainty_reasons": []})
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=fake_post):
                state = run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                           reservation_dir=receipt_dir)
            self.assertEqual(len(requests), 4)
            self.assertLessEqual(max(len(_canonical(request).encode()) for request in requests),
                                 MAX_REQUEST_BYTES)
            self.assertEqual(state["specialist_results"], original["specialist_results"])
            self.assertEqual(state["candidate_status"], "not_started")
            self.assertEqual(state["m20_hosted_base_tokens"], 0)
            self.assertEqual({item["prompt_version"] for item in state["m20_model_attempts"]},
                             {PROMPT_VERSION})
            self.assertEqual([state["m20_ai_results"][name]["execution"] for name in (
                "configuration", "pricing")], ["completed", "completed"])
            self.assertEqual({entry["status"] for entry in state["m20_model_attempts"]},
                             {"reserved", "returned"})
            self.assertEqual([entry["request_sha256"] for entry in state[
                "m20_model_attempts"] if entry["status"] == "reserved"],
                [sha256(_canonical(body).encode()).hexdigest() for body in requests])
            self.assertEqual(len([entry for entry in state["tool_access_ledger"] if entry[
                "status"] == "completed"]), 2)
            self.assertEqual(state["m20_review"]["specialists"]["pricing"][
                "validated_claims"], state["m20_ai_results"]["pricing"]["validated_claims"])
            self.assertEqual(state["reviewer_package"]["m20_ai"], state["m20_review"])
            self.assertEqual(state["reviewer_package"]["reviewer_action"],
                             "Human review required; no approval, reservation or delivery promise")
        with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=AssertionError("replayed send")):
                replay = run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                            reservation_dir=receipt_dir)
            self.assertEqual(replay["m20_ai_results"], state["m20_ai_results"])
            with tempfile.TemporaryDirectory(dir="/tmp/opencode") as moved_dir, patch.dict(
                    os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=AssertionError("changed owner send")):
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                       reservation_dir=Path(moved_dir))

            assessment = "M20-GROQ-WIRE-ADVERSE-B05-" + uuid4().hex
            config = {"configurable": {"thread_id": assessment}}
            graph.invoke(initial_state(assessment, case.run_id), config)
            def bad_post(url, key, header, body, **kwargs):
                input = json.loads(body["messages"][1]["content"])
                if len(body["messages"]) == 2:
                    return tool_response("inspect_configuration_line", {"line_id": case.ids()["L"]})
                return tool_response("submit_finding", {"claims": [{"ref": "product:FORGED",
                    "field": "is_sellable", "value_json": "true"}],
                    "uncertainty_reasons": []})
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=bad_post) as sender:
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                       reservation_dir=receipt_dir)
                self.assertEqual(sender.call_count, 2)  # Pricing never sends
                with self.assertRaises(EvidenceMismatch):
                    run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                       reservation_dir=receipt_dir)
                self.assertEqual(sender.call_count, 2)
            failed = graph.get_state(config).values
            self.assertEqual(failed["m20_ai_results"]["configuration"]["execution"], "error")
            self.assertNotIn("pricing", failed["m20_ai_results"])
            self.assertEqual(failed["m20_ai_results"]["configuration"]["validated_claims"], [])
            self.assertEqual(failed["reviewer_package"]["m20_ai"]["execution"], "stopped")
            self.assertEqual(failed["reviewer_package"]["m20_ai"]["validated_claims"], [])
            self.assertEqual(failed["reviewer_package"]["reviewer_action"],
                             "Human review required; no approval, reservation or delivery promise")
