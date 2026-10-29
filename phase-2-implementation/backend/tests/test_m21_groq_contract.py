"""Offline-only Week 3 redaction and native-tool protocol tests; no network."""

import json
import io
import unittest
from copy import deepcopy
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.live_models import GROQ_MODEL, ProviderError, _post
from dealdesk_phase2.m21_groq_contract import parse_response, request_body
from dealdesk_phase2.m21_prompts import PROMPT_VERSION
from dealdesk_phase2.m21_redaction import model_view
from dealdesk_phase2.m21_specialists import _claims, TOOLS, VERSION
from dealdesk_phase2.tool_response_diagnostic import ToolResponseError


def tool_response(name, arguments, *, call_id="call_w3_synthetic"):
    return {"choices": [{"finish_reason": "tool_calls", "message": {"content": None,
        "tool_calls": [{"id": call_id, "type": "function", "function": {"name": name,
            "arguments": json.dumps(arguments)}}]}}]}


class M21GroqWire(unittest.TestCase):
    def setUp(self):
        self.input = {"version": VERSION, "prompt_version": PROMPT_VERSION,
            "assessment_id": "W3-SYNTHETIC", "phase1c_run_id": "synthetic-run",
            "subject_id": "D-SENSITIVE", "customer_id": "C-SENSITIVE",
            "bundle_sha256": "0" * 64, "source_input_digest": "1" * 64,
            "as_of_at": "2026-09-01T00:00:00+00:00", "policy_set_code": "PRIVATE",
            "data_snapshot_ref": "SENSITIVE-SNAPSHOT", "specialist": "credit",
            "fixed_execution": "completed", "fixed_finding": "needs_revision",
            "permitted_tool": TOOLS["credit"]}
        self.observation = {"version": VERSION, "tool": TOOLS["credit"],
            "execution": "completed", "records": [
                {"ref": "credit_profile:C-SENSITIVE", "fields": {
                    "credit_limit": "100.00", "commitment_evidence_ref": "PRIVATE-COMMITMENT",
                    "credit_status": "Active", "fixed_commitments_fresh": False}},
                {"ref": "receivable:R-PRIVATE", "fields": {"invoice_number": "PRIVATE-INVOICE",
                    "outstanding_amount": "20.00", "status": "Open"}},
                {"ref": "payment:P-PRIVATE", "fields": {"invoice_number": "PRIVATE-INVOICE",
                    "paid_amount": "5.00"}}],
            "returned_refs": ["credit_profile:C-SENSITIVE", "receivable:R-PRIVATE",
                              "payment:P-PRIVATE"]}

    def test_credit_transport_redacts_ids_and_sensitive_fields_and_links_call(self):
        public, visible, refs = model_view(self.input, (self.observation,))
        for private in ("D-SENSITIVE", "C-SENSITIVE", "PRIVATE-COMMITMENT",
                        "PRIVATE-INVOICE", "R-PRIVATE", "P-PRIVATE", "SENSITIVE-SNAPSHOT"):
            self.assertNotIn(private, _canonical([public, visible]))
        self.assertEqual(len(refs), 3)
        self.assertEqual(set(visible[0]["returned_refs"]), set(refs))
        body = request_body(self.input, ())
        self.assertEqual(body["model"], GROQ_MODEL)
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertEqual(body["messages"][1]["role"], "user")
        self.assertFalse(body["parallel_tool_calls"])
        self.assertNotIn("response_format", body)
        inspect = parse_response(tool_response(TOOLS["credit"], {
            "subject_id": public["subject_id"]}), self.input, ())
        self.assertEqual(inspect, {"kind": "inspect", "tool": TOOLS["credit"],
                                   "subject_id": "D-SENSITIVE"})
        exchange = {"id": "call_w3_synthetic", "name": TOOLS["credit"],
                    "arguments": json.dumps({"subject_id": public["subject_id"]})}
        continuation = request_body(self.input, (self.observation,), exchanges=(exchange,))
        self.assertEqual(continuation["messages"][2]["tool_calls"][0]["id"],
                         continuation["messages"][3]["tool_call_id"])
        self.assertEqual(json.loads(continuation["messages"][3]["content"]), visible[0])
        for private in ("D-SENSITIVE", "C-SENSITIVE", "PRIVATE-COMMITMENT",
                        "PRIVATE-INVOICE", "R-PRIVATE", "P-PRIVATE", "SENSITIVE-SNAPSHOT"):
            self.assertNotIn(private, _canonical(continuation))
        ref = visible[0]["records"][0]["ref"]
        finding = parse_response(tool_response("submit_finding", {"claims": [{
            "ref": ref, "field": "fixed_commitments_fresh", "value_json": "false"}]}),
            self.input, (self.observation,))
        self.assertEqual(_claims(finding, (self.observation,)), finding["claims"])
        self.assertEqual(finding["claims"][0]["value"], False)

    def test_fabricated_fields_refs_values_and_malformed_or_abstained_response(self):
        _, visible, _ = model_view(self.input, (self.observation,))
        ref = visible[0]["records"][0]["ref"]
        cases = [("credit_profile:FORGED", "credit_status", '"Active"'),
                 (ref, "commitment_evidence_ref", '"PRIVATE-COMMITMENT"'),
                 (ref, "fixed_commitments_fresh", "0"),
                 (ref, "credit_limit", '"999.00"'),
                 (ref, "approved", "true")]
        for bad_ref, field, value in cases:
            with self.subTest(field=field, ref=bad_ref), self.assertRaises(ValueError):
                parse_response(tool_response("submit_finding", {"claims": [{
                    "ref": bad_ref, "field": field, "value_json": value}]}),
                    self.input, (self.observation,))
        for result in ({"choices": []}, tool_response("approve", {"approved": True}),
                       tool_response("submit_finding", {"claims": []}),
                       tool_response(TOOLS["credit"], {"subject_id": "OTHER"})):
            with self.assertRaises(ValueError):
                parse_response(result, self.input, (self.observation,))
        self.assertEqual(parse_response(tool_response("abstain", {
            "reason_code": "model_uncertainty"}), self.input, (self.observation,)),
            {"kind": "abstain", "reason_code": "model_uncertainty"})
        with self.assertRaises(ValueError):
            request_body(self.input, (self.observation,))
        extra = deepcopy(self.observation)
        extra["records"][0]["fields"]["customer_name"] = "PRIVATE-NAME"
        with self.assertRaises(ValueError):
            model_view(self.input, (extra,))

    def test_shared_rejection_categories_do_not_expose_redacted_credit_evidence(self):
        for response, expected in ((tool_response("approve", {"approved": True}),
                                    "unsupported_tool"),
                                   (tool_response("submit_finding", {"claims": []}),
                                    "action_arguments"),
                                   ({"choices": []}, "envelope")):
            with self.subTest(category=expected), self.assertRaises(
                    ToolResponseError) as caught:
                parse_response(response, self.input, (self.observation,))
            self.assertEqual(caught.exception.category, expected)
            self.assertNotIn("PRIVATE", str(caught.exception))

    def test_policy_routing_keep_only_returned_fixed_refs(self):
        for name, record in (("policy", {"ref": "policy_rule:PO-1", "fields": {
                "rule_id": "PO-1", "required_action": "approval_required"}}),
                             ("approval_routing", {"ref": "fixed_route:D-SENSITIVE",
                "fields": {"route_withheld": True,
                           "roles_available_from_fixed_interface": False}})):
            with self.subTest(name=name):
                input = {**self.input, "specialist": name, "permitted_tool": TOOLS[name]}
                obs = {"version": VERSION, "tool": TOOLS[name], "execution": "completed",
                       "records": [record], "returned_refs": [record["ref"]]}
                _, visible, _ = model_view(input, (obs,))
                ref = visible[0]["records"][0]["ref"]
                field, value = next(iter(record["fields"].items()))
                action = parse_response(tool_response("submit_finding", {"claims": [{
                    "ref": ref, "field": field, "value_json": _canonical(value)}]}), input,
                    (obs,))
                self.assertEqual(_claims(action, (obs,)), action["claims"])
                self.assertNotIn("D-SENSITIVE", _canonical(request_body(input, (obs,),
                    exchanges=({"id": "call_w3_synthetic", "name": TOOLS[name],
                                "arguments": json.dumps({"subject_id": model_view(input, ())[0][
                                    "subject_id"]})},))))
                if name == "policy":
                    injected = deepcopy(obs)
                    injected["records"][0]["fields"]["scope_value"] = "C-SENSITIVE"
                    with self.assertRaises(ValueError):
                        model_view(input, (injected,))

    def test_shared_transport_error_is_sanitized_without_network_or_body_read(self):
        body = request_body(self.input, ())

        class Unreadable(io.BytesIO):
            def read(self, *args, **kwargs):
                raise AssertionError("private provider body read")

        class OfflineOpener:
            calls = 0
            wire = None

            def open(self, request, timeout):
                self.calls += 1
                self.wire = request.data
                raise HTTPError(request.full_url, 400, "redacted", {},
                                Unreadable(b"private provider details"))

        offline = OfflineOpener()
        with patch("dealdesk_phase2.live_models.build_opener", return_value=offline):
            with self.assertRaises(ProviderError) as caught:
                _post("https://api.groq.com/openai/v1/chat/completions",
                      "Bearer offline-placeholder", "Authorization", body,
                      classify_transport=True, reject_redirects=True)
        self.assertEqual(caught.exception.code, "http_400")
        self.assertEqual(offline.calls, 1)
        self.assertNotIn(b"C-SENSITIVE", offline.wire)
        self.assertNotIn(b"PRIVATE-INVOICE", offline.wire)

        class TimedOutOpener:
            calls = 0

            def open(self, request, timeout):
                self.calls += 1
                raise URLError(TimeoutError("private transport details"))

        timeout_opener = TimedOutOpener()
        with patch("dealdesk_phase2.live_models.build_opener", return_value=timeout_opener):
            with self.assertRaises(ProviderError) as caught:
                _post("https://api.groq.com/openai/v1/chat/completions",
                      "Bearer offline-placeholder", "Authorization", body,
                      classify_transport=True, reject_redirects=True)
        self.assertEqual(caught.exception.code, "transport_timeout")
        self.assertEqual(timeout_opener.calls, 1)
