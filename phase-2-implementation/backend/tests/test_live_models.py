"""No-network M1.4 adapter, secret, replay and failure tests."""

import json
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.live_models import (LiveInvestigationModel, ProviderError, _post,
                                         _canonical_final, _prompt, BINDING_PROMPT_SUFFIX,
                                         BINDING_FINAL_SCHEMA, FINAL_SCHEMA)
from dealdesk_phase2.investigation_graph import run_original_then_investigate
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from test_investigation_graph import InvestigationAdapter, RUN


def final(line="L1", citations=("supplier_offer:O1",)):
    return {"kind": "finding_without_proposal", "line_id": line,
            "delivery_slices": [], "citations": list(citations), "tradeoffs": [],
            "assumptions": [], "unmet_requirements": [],
            "uncertainty_reasons": ["Supplier confirmation absent"],
            "finding": "Supplier offer is conditional", "reason": ""}


class LiveModelTests(TestCase):
    def test_opt_in_binding_schema_maps_to_v3_without_network(self):
        raw = {**final(), "kind": "binding_proposal", "tradeoff_code":
               "partial_delivery_requires_customer_acceptance",
               "delivery_slices": [{"quantity": "8", "delivery_date": "2026-09-04",
                                    "source_refs": ["inventory:STOCK"]},
                                   {"quantity": "2", "delivery_date": "2026-09-08",
                                    "source_refs": ["inbound_supply:IN"]}], "claims": []}
        mapped = _canonical_final(raw)
        self.assertEqual(mapped["value"]["schema_version"], "3")
        self.assertEqual(mapped["value"]["payload"]["delivery_slices"][1]["quantity"], "2")
        self.assertEqual(BINDING_FINAL_SCHEMA["properties"]["kind"]["enum"][-1],
                         "binding_proposal")
        self.assertNotIn("binding_proposal", FINAL_SCHEMA["properties"]["kind"]["enum"])

    def test_m19_binding_guidance_preserves_raw_quantities_for_strict_validation(self):
        from test_candidate_m17 import fake_input

        prompt = _prompt(fake_input(), (), enable_binding_proposals=True)
        self.assertIn(BINDING_PROMPT_SUFFIX, prompt)
        self.assertIn("never '8.000', '8.0', 8", prompt)
        self.assertIn("source-to-slice support", prompt)
        self.assertNotIn(BINDING_PROMPT_SUFFIX, _prompt(fake_input(), ()))
        quantity_schema = BINDING_FINAL_SCHEMA["properties"]["delivery_slices"]["items"]["properties"]["quantity"]
        self.assertEqual(quantity_schema["type"], "string")
        self.assertIn("Never '8.000'", quantity_schema["description"])
        # The adapter must not repair the model's raw output behind the audit's back.
        raw = {**final(), "kind": "binding_proposal", "tradeoff_code":
               "partial_delivery_requires_customer_acceptance",
               "delivery_slices": [{"quantity": "8.000", "delivery_date": "2026-09-04",
                                    "source_refs": ["inventory:STOCK"]},
                                   {"quantity": "2", "delivery_date": "2026-09-08",
                                    "source_refs": ["inbound_supply:IN"]}], "claims": []}
        mapped = _canonical_final(raw)
        self.assertEqual(mapped["value"]["payload"]["delivery_slices"][0]["quantity"], "8.000")

    def test_live_request_uses_descriptive_api_client_identity(self):
        from io import BytesIO

        class Response:
            def __enter__(self): return BytesIO(b'{}')
            def __exit__(self, *args): return False

        with patch("dealdesk_phase2.live_models.urlopen", return_value=Response()) as request:
            self.assertEqual(_post("https://api.groq.com/openai/v1/chat/completions",
                                   "Bearer test-secret", "Authorization", {"model": "test"}), {})
        sent = request.call_args.args[0]
        self.assertEqual(sent.get_header("User-agent"), "DealDeskOrchestrator-thesis-M1.4/1.0")
        self.assertEqual(sent.get_header("Authorization"), "Bearer test-secret")

    def setUp(self):
        self.adapter = InvestigationAdapter()
        self.saver = InMemorySaver()
        self.graph = build_original_graph(self.adapter, None, self.saver)
        self.config = {"configurable": {"thread_id": self.id()}}

    def run_model(self, provider, responses):
        model = LiveInvestigationModel(provider, self.graph, self.config)
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret", "GEMINI_API_KEY": "test-secret"}), \
             patch("dealdesk_phase2.live_models._post", side_effect=responses) as request:
            result = run_original_then_investigate(self.graph, self.config, self.adapter,
                model, assessment_id=self.id(), run_id=RUN)
        return result, request

    def test_groq_tool_then_strict_final_and_checkpointed_attempts(self):
        tool = {"model": "openai/gpt-oss-120b", "usage": {"prompt_tokens": 50,
                "completion_tokens": 15}, "choices": [{"message": {"tool_calls": [{
                    "function": {"name": "inspect_line_supply",
                                 "arguments": json.dumps({"line_id": "L1"})}}]}}]}
        ready = {"model": "openai/gpt-oss-120b", "usage": {},
                 "choices": [{"message": {"content": "READY"}}]}
        ending = {"model": "openai/gpt-oss-120b", "usage": {},
                  "choices": [{"message": {"content": json.dumps(final())}}]}
        state, request = self.run_model("groq", [tool, ready, ending])
        self.assertEqual(request.call_count, 3)
        self.assertEqual(state["ai_fulfillment_result"]["execution"], "completed")
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["kind"],
                         "finding_without_proposal")
        ledger = state["model_attempt_ledger"]
        self.assertEqual(len([x for x in ledger if x["status"] == "completed"]), 3)
        self.assertEqual(ledger[1]["usage"]["input_tokens"], 50)
        self.assertNotIn("test-secret", str(ledger))
        self.assertEqual(state["specialist_results"]["fulfillment"]["execution"], "completed")

    def test_gemini_function_call_then_structured_final(self):
        tool = {"modelVersion": "gemini-3.8-flash", "usageMetadata": {
                "promptTokenCount": 31, "candidatesTokenCount": 8},
                "candidates": [{"content": {"parts": [{"functionCall": {
                    "name": "inspect_line_supply", "args": {"line_id": "L1"}}}]}}]}
        ready = {"candidates": [{"content": {"parts": [{"text": "READY"}]}}]}
        ending = {"candidates": [{"content": {"parts": [
                  {"text": json.dumps(final())}]}}]}
        state, request = self.run_model("gemini", [tool, ready, ending])
        self.assertEqual(state["ai_fulfillment_result"]["execution"], "completed")
        self.assertEqual(request.call_count, 3)
        self.assertEqual(sum(bool(x["counted"]) for x in state["tool_access_ledger"]), 1)
        schema = request.call_args_list[-1].args[3]["generationConfig"]["responseSchema"]
        self.assertNotIn("additionalProperties", json.dumps(schema))
        self.assertEqual(set(schema["required"]), set(schema["properties"]))

    def test_unsupported_citation_and_fabricated_confirmation_are_rejected(self):
        ready = {"choices": [{"message": {"content": "READY"}}]}
        ending = {"choices": [{"message": {"content": json.dumps(final(
                  citations=("supplier_offer:unseen",)))}}]}
        result, _ = self.run_model("groq", [ready, ending])
        self.assertEqual(result["ai_fulfillment_result"]["error"], "unsupported_citation")
        self.assertEqual(result["review_status"], "needs_revision")
        self.setUp()
        falsified = final()
        falsified["kind"] = "proposal"
        falsified["delivery_slices"] = [{"quantity": "20", "delivery_date": "2026-09-04",
                                         "commitment_claim": "confirmed"}]
        result, _ = self.run_model("groq", [ready, {"choices": [{"message": {
            "content": json.dumps(falsified)}}]}])
        self.assertEqual(result["ai_fulfillment_result"]["error"], "malformed_contribution")

    def test_quota_and_missing_key_keep_fixed_result(self):
        result, _ = self.run_model("groq", [ProviderError("http_429")])
        self.assertEqual(result["ai_fulfillment_result"]["execution"], "error")
        self.assertEqual(result["model_attempt_ledger"][-1]["error_code"], "http_429")
        self.assertEqual(result["specialist_results"]["fulfillment"]["execution"], "completed")
        self.setUp()
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = run_original_then_investigate(self.graph, self.config, self.adapter,
                LiveInvestigationModel("groq", self.graph, self.config),
                assessment_id=self.id(), run_id=RUN)
        self.assertEqual(result["ai_fulfillment_result"]["execution"], "error")
        self.assertNotIn("model_attempt_ledger", result)

    def test_completed_model_decision_replays_without_second_network_call(self):
        first = {"choices": [{"message": {"tool_calls": [{"function": {
            "name": "inspect_line_supply", "arguments": '{"line_id":"L1"}'}}]}}]}
        class InterruptAfterFirst:
            def __init__(self, wrapped): self.wrapped = wrapped
            def next_action(self, input, observations):
                action = self.wrapped.next_action(input, observations)
                if not observations: raise KeyboardInterrupt("after response checkpoint")
                return action
        model = LiveInvestigationModel("groq", self.graph, self.config)
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
             patch("dealdesk_phase2.live_models._post", return_value=first) as request:
            with self.assertRaises(KeyboardInterrupt):
                run_original_then_investigate(self.graph, self.config, self.adapter,
                    InterruptAfterFirst(model), assessment_id=self.id(), run_id=RUN)
            self.assertEqual(request.call_count, 1)
        restarted = build_original_graph(self.adapter, None, self.saver)
        model = LiveInvestigationModel("groq", restarted, self.config)
        ready = {"choices": [{"message": {"content": "READY"}}]}
        ending = {"choices": [{"message": {"content": json.dumps(final())}}]}
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
             patch("dealdesk_phase2.live_models._post", side_effect=[ready, ending]) as request:
            result = run_original_then_investigate(restarted, self.config, self.adapter,
                model, assessment_id=self.id(), run_id=RUN)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(self.adapter.decisions, 1)
        self.assertEqual(result["ai_fulfillment_result"]["execution"], "completed")

    def test_interrupted_reservation_does_not_auto_repeat(self):
        model = LiveInvestigationModel("groq", self.graph, self.config)
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
             patch("dealdesk_phase2.live_models._post", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                run_original_then_investigate(self.graph, self.config, self.adapter,
                    model, assessment_id=self.id(), run_id=RUN)
        restarted = build_original_graph(self.adapter, None, self.saver)
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
             patch("dealdesk_phase2.live_models._post") as request:
            result = run_original_then_investigate(restarted, self.config, self.adapter,
                LiveInvestigationModel("groq", restarted, self.config),
                assessment_id=self.id(), run_id=RUN)
        self.assertEqual(request.call_count, 0)
        self.assertEqual(result["ai_fulfillment_result"]["execution"], "error")
        self.assertEqual(result["model_attempt_ledger"][-1]["status"], "reserved")


@__import__("unittest").skipUnless(all(os.environ.get(k) for k in
    ("DATABASE_URL", "CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Needs exact pinned Phase 1C and disposable PostgreSQL")
class PinnedLiveReplayTests(TestCase):
    def test_reopened_postgres_saver_replays_model_decision(self):
        import psycopg
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        config = {"configurable": {"thread_id": "M14-pg-attempt-restart"}}
        run = UUID("00000000-0000-4000-8000-000000030001")
        assessment = "M14-pg-attempt-restart"
        line = "L-offer_without_supplier_commitment-1"
        tool_response = {"model": "openai/gpt-oss-120b", "choices": [{"message": {
            "tool_calls": [{"function": {"name": "inspect_line_supply",
                                          "arguments": json.dumps({"line_id": line})}}]}}]}

        class AfterCompletedDecision:
            def __init__(self, delegate): self.delegate = delegate
            def next_action(self, input, observations):
                action = self.delegate.next_action(input, observations)
                if not observations:
                    raise KeyboardInterrupt("process stopped after recorded model output")
                return action

        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter,
                lambda: psycopg.connect(os.environ["DATABASE_URL"]), saver)
            with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
                 patch("dealdesk_phase2.live_models._post", return_value=tool_response):
                with self.assertRaises(KeyboardInterrupt):
                    run_original_then_investigate(graph, config, adapter,
                        AfterCompletedDecision(LiveInvestigationModel("groq", graph, config)),
                        assessment_id=assessment, run_id=run)
            self.assertEqual(len([x for x in graph.get_state(config).values["model_attempt_ledger"]
                                  if x["status"] == "completed"]), 1)

        ready = {"choices": [{"message": {"content": "READY"}}]}
        ending = {"choices": [{"message": {"content": json.dumps(final(
            line=line, citations=("supplier_offer:OFFER-offer_without_supplier_commitment",)))}}]}
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter,
                lambda: psycopg.connect(os.environ["DATABASE_URL"]), saver)
            with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}), \
                 patch("dealdesk_phase2.live_models._post", side_effect=[ready, ending]) as request:
                result = run_original_then_investigate(graph, config, adapter,
                    LiveInvestigationModel("groq", graph, config),
                    assessment_id=assessment, run_id=run)
            self.assertEqual(request.call_count, 2)
            self.assertEqual(result["ai_fulfillment_result"]["execution"], "completed")
            self.assertEqual(result["specialist_results"]["fulfillment"]["finding"], "conditional")
            self.assertEqual(sum(bool(x["counted"]) for x in result["tool_access_ledger"]), 1)
