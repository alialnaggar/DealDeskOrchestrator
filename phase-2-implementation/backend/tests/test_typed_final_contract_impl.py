"""Offline-only unit gates for new Pricing/Credit terminal contracts."""

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from dealdesk_phase2.groq_typed_final import (MAX_COMPLETION_TOKENS,
    FinalResponseError, configuration_final_body, parse_configuration_final,
    request_body, request_sha256, parse_response, DEVELOPMENT_FINAL_INSTRUCTION,
    CREDIT_DEVELOPMENT_FINAL_INSTRUCTION)
from dealdesk_phase2.typed_final_contract import InvalidTerminal, VERSION, decode, schema
from dealdesk_phase2.m21_redaction import model_view
from test_terminal_final_offline_design import fixture, finding, response


def final_payload(ref, field, value):
    return {**finding(ref, field, value), "version": VERSION}


class TypedFinalContractImpl(unittest.TestCase):
    def test_credit_prompt_invites_exact_observation_not_credit_clearance(self):
        input, rows, _, ref, field, value = fixture("credit")
        body = request_body(input, rows, completed_ledger=rows,
            final_instruction=CREDIT_DEVELOPMENT_FINAL_INSTRUCTION)
        instruction = body["messages"][0]["content"]
        self.assertIn("credit-observation-v3", instruction)
        self.assertIn("not as clearance", instruction)
        self.assertIn("evidence is uncertain, abstain", instruction)
        self.assertNotIn("Pricing:", instruction)
        self.assertNotIn(ref, instruction)
        pricing_input, pricing_rows, *_ = fixture("pricing")
        with self.assertRaises(InvalidTerminal):
            request_body(pricing_input, pricing_rows, completed_ledger=pricing_rows,
                final_instruction=CREDIT_DEVELOPMENT_FINAL_INSTRUCTION)
        alias = next(iter(model_view(input, rows)[2]))
        self.assertEqual(parse_response(response(final_payload(alias, field, value)),
            input=input, observations=rows, development=True)["kind"], "finding")
        abstain = {"version": VERSION, "kind": "abstain", "claims": [],
            "uncertainty_reasons": [], "reason_code": "model_uncertainty"}
        self.assertEqual(parse_response(response(abstain), input=input,
            observations=rows, development=True)["kind"], "abstain")
        with self.assertRaises(InvalidTerminal):
            parse_response(response(final_payload(alias, field, "fabricated")),
                input=input, observations=rows, development=True)

    def test_development_caps_and_diagnostic_categories_fail_closed(self):
        from dealdesk_phase2.typed_final_hosted import budgets
        input, rows, _, ref, field, value = fixture("pricing")
        wire = request_body(input, rows, completed_ledger=rows,
            final_instruction=DEVELOPMENT_FINAL_INSTRUCTION)
        self.assertEqual(wire["max_completion_tokens"], 2048)
        self.assertEqual(budgets("pricing", 1, development=True)[
            "maximum_configured_completion_per_case"], 4096)
        self.assertEqual(budgets("pricing", 1)[
            "maximum_configured_completion_per_case"], 2560)
        valid = response(final_payload(ref, field, value), tokens=1500)
        self.assertEqual(parse_response(valid, input=input, observations=rows,
            development=True)["kind"], "finding")
        with self.assertRaises(FinalResponseError):
            parse_response(valid, input=input, observations=rows)
        for payload, category in (({**final_payload(ref, field, value),
                "claims": []}, "finding_claim_count"),
                ({**final_payload(ref, field, value), "reason_code":
                    "model_uncertainty"}, "finding_reason"),
                ({**final_payload(ref, field, value), "kind": "abstain",
                    "reason_code": "model_uncertainty"}, "abstention_semantics")):
            with self.subTest(category=category), self.assertRaises(
                    FinalResponseError) as caught:
                parse_response(response(payload), input=input, observations=rows,
                    development=True)
            self.assertEqual(caught.exception.category, category)
        config_input = {"specialist": "configuration", "permitted_tool":
            "inspect_configuration_line"}
        config_row = ({"tool": "inspect_configuration_line", "execution": "completed",
            "records": [{"ref": "product:P", "fields": {"is_sellable": True}}],
            "returned_refs": ["product:P"]},)
        self.assertEqual(configuration_final_body(config_input, config_row)[
            "max_completion_tokens"], 1024)
        bad = response(final_payload("product:FAKE", "is_sellable", True))
        with self.assertRaises(FinalResponseError) as caught:
            parse_configuration_final(bad, config_input, config_row)
        self.assertEqual(caught.exception.category, "claim_binding")

    def test_configuration_development_final_is_no_tools_and_exact_evidence_only(self):
        input = {"specialist": "configuration", "permitted_tool":
            "inspect_configuration_line", "line_ids": ["L1"]}
        observation = ({"tool": "inspect_configuration_line", "execution": "completed",
            "returned_refs": ["product:P"], "records": [{"ref": "product:P",
                "fields": {"is_sellable": True}}]},)
        body = configuration_final_body(input, observation)
        self.assertNotIn("tools", body)
        self.assertTrue(body["response_format"]["json_schema"]["strict"])
        claim = final_payload("product:P", "is_sellable", True)
        self.assertEqual(parse_configuration_final(response(claim), input, observation)[
            "claims"], [{"ref": "product:P", "field": "is_sellable", "value": True}])
        with self.assertRaises(FinalResponseError):
            parse_configuration_final(response(final_payload("product:FORGED",
                "is_sellable", True)), input, observation)
        with self.assertRaises(InvalidTerminal):
            configuration_final_body(input, ())

    def test_rejected_final_carries_only_bounded_category(self):
        input, rows, _, ref, field, value = fixture("pricing")
        valid = response(final_payload(ref, field, value))
        cases = (({**valid, "choices": []}, "envelope"),
                 (response(final_payload(ref, field, value), reason="length"),
                  "finish_reason"),
                 ({**valid, "usage": None}, "usage"),
                 ({**valid, "choices": [{"finish_reason": "stop", "message": {
                     "content": "PRIVATE {", "tool_calls": None}}]}, "content_json"),
                 (response({"private": "PRIVATE"}), "schema_shape"),
                 (response(final_payload("forged:PRIVATE", field, value)),
                  "claim_binding"))
        for item, category in cases:
            with self.subTest(category=category), self.assertRaises(
                    FinalResponseError) as caught:
                parse_response(item, input=input, observations=rows)
            self.assertEqual(caught.exception.category, category)
            self.assertNotIn("PRIVATE", str(caught.exception))

    def test_new_wire_no_tools_and_redacted_credit(self):
        for specialist in ("pricing", "credit"):
            with self.subTest(specialist=specialist):
                input, rows, _, ref, field, value = fixture(specialist)
                body = request_body(input, rows, completed_ledger=rows)
                self.assertNotIn("tools", body)
                self.assertNotIn("tool_choice", body)
                self.assertEqual(body["max_completion_tokens"], 1024)
                self.assertTrue(body["response_format"]["json_schema"]["strict"])
                self.assertEqual(len(request_sha256(body)), 64)
                self.assertEqual([m["role"] for m in body["messages"]], ["system", "user"])
                if specialist == "credit":
                    self.assertNotIn(ref, body["messages"][1]["content"])
                    self.assertNotIn(input["customer_id"], body["messages"][1]["content"])
                alias = ref if specialist == "pricing" else next(iter(model_view(input, rows)[2]))
                action = parse_response(response(final_payload(alias, field, value)),
                    input=input, observations=rows)
                self.assertEqual(action["claims"], [{"ref": ref, "field": field,
                                                       "value": value}])
                with self.assertRaises(InvalidTerminal):
                    request_body(input, rows, completed_ledger=())

    def test_pricing_two_inspections_and_abstention(self):
        input, rows, _, ref, field, value = fixture("pricing")
        body = request_body(input, (rows[0], deepcopy(rows[0])),
                            completed_ledger=(rows[0], deepcopy(rows[0])))
        self.assertEqual(body["max_completion_tokens"], MAX_COMPLETION_TOKENS)
        abstain = {"version": VERSION, "kind": "abstain", "claims": [],
                   "uncertainty_reasons": [], "reason_code": "model_uncertainty"}
        self.assertEqual(decode(json.dumps(abstain), specialist="pricing", input=input,
                                observations=rows), {"kind": "abstain",
                                                      "reason_code": "model_uncertainty"})

    def test_unsupported_schema_and_request_size_before_send(self):
        input, rows, *_ = fixture("pricing")
        with patch("dealdesk_phase2.groq_typed_final.schema", return_value={
                "type": "object", "properties": {}, "required": [],
                "additionalProperties": False}):
            with self.assertRaisesRegex(InvalidTerminal, "unsupported_final_schema"):
                request_body(input, rows, completed_ledger=rows)
        oversized = deepcopy(rows)
        oversized[0]["records"][0]["fields"]["long_value"] = "x" * 9000
        with self.assertRaisesRegex(InvalidTerminal, "final_request_oversize"):
            request_body(input, oversized, completed_ledger=oversized)

    def test_all_fields_required_and_invalid_outputs_fail_closed(self):
        shape = schema()
        self.assertEqual(set(shape["required"]), set(shape["properties"]))
        self.assertFalse(shape["additionalProperties"])
        self.assertFalse(shape["properties"]["claims"]["items"]["additionalProperties"])
        for specialist in ("pricing", "credit"):
            input, rows, _, ref, field, value = fixture(specialist)
            alias = ref if specialist == "pricing" else next(iter(model_view(input, rows)[2]))
            base = final_payload(alias, field, value)
            for change in (lambda x: x["claims"][0].update(ref="fabricated"),
                           lambda x: x["claims"][0].update(value_json='"wrong"'),
                           lambda x: x.update(reason_code="model_uncertainty"),
                           lambda x: x.update(claims=[])):
                wrong = deepcopy(base); change(wrong)
                with self.subTest(specialist=specialist, wrong=wrong):
                    with self.assertRaises(InvalidTerminal):
                        parse_response(response(wrong), input=input, observations=rows)
            for content in ('{"version":', '{"version":"terminal-final-v1",'
                            '"version":"terminal-final-v1"}'):
                with self.assertRaises(InvalidTerminal):
                    decode(content, specialist=specialist, input=input, observations=rows)
            with self.assertRaises(InvalidTerminal):
                decode(json.dumps(base)[:-1] + ',"kind":"finding"}',
                    specialist=specialist, input=input, observations=rows)
            bad = response(base, reason="length")
            with self.assertRaises(InvalidTerminal):
                parse_response(bad, input=input, observations=rows)
            bad = response(base, tokens=MAX_COMPLETION_TOKENS + 1)
            with self.assertRaises(InvalidTerminal):
                parse_response(bad, input=input, observations=rows)
            bad = response(base); bad.pop("usage")
            with self.assertRaises(InvalidTerminal):
                parse_response(bad, input=input, observations=rows)


if __name__ == "__main__":
    unittest.main()
