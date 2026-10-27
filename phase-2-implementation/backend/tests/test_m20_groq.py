"""No-network native Groq tool wire and explicitly gated hosted checkpoint tests."""

import json
import os
from pathlib import Path
import tempfile
from hashlib import sha256
import unittest
from unittest.mock import patch

from dealdesk_phase2.m20_groq import (GroqM20Model, WIRE_VERSION, MAX_REQUEST_BYTES,
                                       parse_response, request_body)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m20_specialists import build_m20_graph, run_m20_evaluation
from dealdesk_phase2.live_models import ProviderError
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


def tool_response(name, arguments, *, usage=None):
    return {"choices": [{"finish_reason": "tool_calls", "message": {
        "content": None, "tool_calls": [{"type": "function", "function": {
            "name": name, "arguments": json.dumps(arguments)}}]}}],
        "usage": usage or {"prompt_tokens": 300, "completion_tokens": 60}}


class GroqM20Wire(unittest.TestCase):
    def setUp(self):
        self.input = {"specialist": "configuration", "permitted_tool":
                      "inspect_configuration_line", "line_ids": ["L1"]}

    def test_native_tool_only_bounded_request_and_typed_exact_values(self):
        body = request_body(self.input, ())
        self.assertEqual(body["model"], "openai/gpt-oss-120b")
        self.assertEqual(body["max_completion_tokens"], 512)
        self.assertEqual(body["tool_choice"], "required")
        self.assertFalse(body["parallel_tool_calls"])
        self.assertLessEqual(len(json.dumps(body, sort_keys=True,
            separators=(",", ":")).encode()), MAX_REQUEST_BYTES)
        self.assertIn(WIRE_VERSION, body["messages"][0]["content"])
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
            assessment = "M20-GROQ-WIRE-OFFLINE-B05"
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
                observations = input["observations"]
                if not observations:
                    return tool_response("inspect_" + specialist + "_line", {
                        "line_id": input["input"]["line_ids"][0]})
                row = observations[0]["records"][0]
                field = "is_sellable" if specialist == "configuration" else "fixed_margin_pct"
                return tool_response("submit_finding", {"claims": [{"ref": row["ref"],
                    "field": field, "value_json": json.dumps(row["fields"][field])}],
                    "uncertainty_reasons": []})
            with patch.dict(os.environ, {"GROQ_API_KEY": "gsk_" + "x" * 47}), patch(
                    "dealdesk_phase2.m20_groq._post", side_effect=fake_post):
                state = run_m20_evaluation(graph, config, adapter, models(), authorized=True,
                                           reservation_dir=receipt_dir)
            self.assertEqual(len(requests), 4)
            self.assertEqual(state["specialist_results"], original["specialist_results"])
            self.assertEqual(state["candidate_status"], "not_started")
            self.assertEqual(state["m20_hosted_base_tokens"], 0)
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

            assessment = "M20-GROQ-WIRE-ADVERSE-B05"
            config = {"configurable": {"thread_id": assessment}}
            graph.invoke(initial_state(assessment, case.run_id), config)
            def bad_post(url, key, header, body, **kwargs):
                input = json.loads(body["messages"][1]["content"])
                if not input["observations"]:
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
