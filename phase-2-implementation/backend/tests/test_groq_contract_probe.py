"""Offline documented request-shape checks; these tests never contact Groq."""

import unittest

from dealdesk_phase2.groq_contract_probe import (
    GROQ_MODEL, MAX_CONFIGURED_COMPLETION_TOKENS, MAX_REQUEST_BYTES,
    PROBE_ID, request_for_stage)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.hybrid_provider import GroqHybridTransportModel


class GroqContractProbeTests(unittest.TestCase):
    def test_two_isolated_offline_wires_are_small_and_do_not_carry_business_data(self):
        plain, tool = request_for_stage("plain"), request_for_stage("tool")
        self.assertEqual(PROBE_ID, "GROQ-CONTRACT-PROBE-85c63f16-0c5b-4c24-bea4-1d1b79adea71")
        self.assertEqual((plain["model"], tool["model"]), (GROQ_MODEL, GROQ_MODEL))
        self.assertEqual(plain["max_completion_tokens"] + tool["max_completion_tokens"],
                         MAX_CONFIGURED_COMPLETION_TOKENS)
        self.assertNotIn("tools", plain)
        self.assertEqual(tool["tool_choice"], "required")
        self.assertIs(tool["parallel_tool_calls"], False)
        self.assertEqual(tool["reasoning_format"], "parsed")
        self.assertEqual(tool["reasoning_effort"], "low")
        self.assertEqual(tool["tools"][0]["function"]["parameters"]["required"], ["status"])
        self.assertLessEqual(max(len(_canonical(body).encode()) for body in (plain, tool)),
                             MAX_REQUEST_BYTES)
        for body in (plain, tool):
            self.assertNotIn("source_reviewed_answer", str(body))
            self.assertNotIn("assessment_id", str(body))
            self.assertNotIn("GROQ_API_KEY", str(body))
        plain["messages"].append({"role": "tool", "content": "tamper"})
        self.assertEqual(request_for_stage("plain")["messages"],
                         [{"role": "user", "content": "Reply OK."}])
        with self.assertRaisesRegex(ValueError, "unknown_probe_stage"):
            request_for_stage("final")

    def test_existing_hosted_decision_and_final_use_documented_chat_fields(self):
        model = GroqHybridTransportModel()
        decision = model.request_decision({"line_id": "L1"}, ())
        self.assertEqual(set(decision), {"model", "temperature", "max_completion_tokens",
            "parallel_tool_calls", "tool_choice", "tools", "messages"})
        self.assertEqual(decision["max_completion_tokens"], 512)
        self.assertEqual(decision["tool_choice"], "required")
        self.assertIs(decision["parallel_tool_calls"], False)
        self.assertNotIn("reasoning_format", decision)  # no incompatible explicit raw
        self.assertNotIn("response_format", decision)  # tools and schema are separate turns
        self.assertEqual([x["role"] for x in decision["messages"]], ["system", "user"])
        self.assertTrue(all(isinstance(x["content"], str) for x in decision["messages"]))
        for item in decision["tools"]:
            self.assertEqual(item["type"], "function")
            schema = item["function"]["parameters"]
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])
            if item["function"]["name"] in ("submit_finding", "abstain"):
                self.assertEqual(set(schema["required"]), set(schema["properties"]))

        def strict_objects(schema):
            if schema.get("type") == "object":
                self.assertIs(schema.get("additionalProperties"), False)
                self.assertEqual(set(schema["properties"]), set(schema["required"]))
                for child in schema["properties"].values():
                    strict_objects(child)
            if schema.get("type") == "array":
                strict_objects(schema["items"])

        paths = ({"tool": "inspect_fulfillment_paths", "execution": "completed",
            "evidence": "eligible_binding", "more_in_sealed_pool": False,
            "findings": {"line_id": "L1", "binding_options": [{"arrival": "2026-09-03"}]}},)
        for kind in ("abstain", "submit_finding", "submit_proposal"):
            with self.subTest(kind=kind):
                final = model.request_final({"kind": kind}, {"line_id": "L1"},
                                             paths if kind == "submit_proposal" else ())
                self.assertEqual(set(final), {"model", "temperature", "max_completion_tokens",
                                              "messages", "response_format"})
                self.assertEqual(final["max_completion_tokens"], 1024)
                self.assertEqual(final["response_format"]["type"], "json_schema")
                spec = final["response_format"]["json_schema"]
                self.assertTrue(spec["strict"])
                strict_objects(spec["schema"])
                self.assertLessEqual(len(_canonical(final).encode()), 8192)
        self.assertLessEqual(len(_canonical(decision).encode()), 8192)


if __name__ == "__main__":
    unittest.main()
