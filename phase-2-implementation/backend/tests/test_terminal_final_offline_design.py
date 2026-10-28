"""Offline proposal tests: no provider, credential, runtime or live request."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from dealdesk_phase2.hybrid_send_reservation import (attempt_path, claim_and_call,
    verify_receipt)
from dealdesk_phase2.m21_redaction import model_view
from dealdesk_phase2.m21_specialists import TOOLS, VERSION as M21_VERSION
from dealdesk_phase2.m20_specialists import VERSION as M20_VERSION
from terminal_final_offline_design import (VERSION, TerminalContractError,
    MAX_REQUEST_BYTES, draft_request, parse_final, schema)


def fixture(specialist):
    identity = {"assessment_id": "offline-only", "phase1c_run_id": "offline-run",
                "bundle_sha256": "a" * 64,
                "source_input_digest": "b" * 64, "subject_id": "M18-D-B01",
                "specialist": specialist}
    if specialist in ("configuration", "pricing"):
        tool = "inspect_" + specialist + "_line"
        input = {**identity, "version": M20_VERSION, "permitted_tool": tool}
        ref, field, value = (("product:SYN-P1", "is_sellable", True)
            if specialist == "configuration" else
            ("pricing_line:SYN-L1", "fixed_margin_pct", "21.000"))
        observation = {"tool": tool, "execution": "completed",
            "records": [{"ref": ref, "fields": {field: value}}],
            "returned_refs": [ref]}
    else:
        input = {**identity, "version": M21_VERSION, "prompt_version": "m21-original-system-v1",
            "as_of_at": "2026-09-01T12:00:00+00:00",
            "fixed_execution": "completed", "fixed_finding": "calculated",
            "customer_id": "SYN-C1", "data_snapshot_ref": "SYN-SNAPSHOT",
            "permitted_tool": TOOLS[specialist]}
        kind = {"credit": "credit_profile", "policy": "policy_rule",
                "approval_routing": "fixed_route"}[specialist]
        field, value = {"credit": ("credit_status", "review"),
            "policy": ("severity", "block"),
            "approval_routing": ("route_withheld", True)}[specialist]
        ref = kind + ":SYN-1"
        observation = {"version": M21_VERSION, "tool": TOOLS[specialist],
            "execution": "completed", "records": [{"ref": ref, "fields": {field: value}}],
            "returned_refs": [ref]}
    return input, (observation,), identity, ref, field, value


def response(payload, *, reason="stop", tokens=300):
    return {"choices": [{"finish_reason": reason, "message": {
        "content": json.dumps(payload, sort_keys=True), "tool_calls": None}}],
        "usage": {"prompt_tokens": 180, "completion_tokens": tokens}}


def finding(ref, field, value):
    return {"version": VERSION, "kind": "finding", "claims": [{"ref": ref,
        "field": field, "value_json": json.dumps(value)}], "reason_code": "none",
        "uncertainty_reasons": []}


def checked(raw, input, observations, identity, **overrides):
    return parse_final(raw, input=input, observations=observations,
        completed_ledger=overrides.get("ledger", observations),
        expected_identity=identity,
        checkpoint_identity=overrides.get("checkpoint", identity))


class TerminalFinalOffline(unittest.TestCase):
    def test_schema_and_separate_no_tools_request(self):
        shape = schema()
        for node in (shape, shape["properties"]["claims"]["items"]):
            self.assertEqual(set(node["properties"]), set(node["required"]))
            self.assertIs(node["additionalProperties"], False)
        for specialist in ("configuration", "pricing", "credit", "policy", "approval_routing"):
            with self.subTest(specialist=specialist):
                input, observations, _, ref, _, _ = fixture(specialist)
                wire = draft_request(input, observations, observations)
                self.assertLessEqual(len(json.dumps(wire).encode()), MAX_REQUEST_BYTES)
                self.assertNotIn("tools", wire)
                self.assertNotIn("tool_choice", wire)
                self.assertEqual(wire["response_format"]["json_schema"]["strict"], True)
                self.assertEqual([x["role"] for x in wire["messages"]], ["system", "user"])
                text = wire["messages"][1]["content"]
                if specialist not in ("configuration", "pricing"):
                    self.assertNotIn(ref, text)
                    self.assertNotIn(input["customer_id"], text)
                self.assertNotIn("tool_calls", text)

    def test_exact_finding_uses_existing_domain_validator(self):
        for specialist in ("configuration", "pricing", "credit", "policy", "approval_routing"):
            with self.subTest(specialist=specialist):
                input, observations, identity, ref, field, value = fixture(specialist)
                visible_ref = (ref if specialist in ("configuration", "pricing") else next(iter(
                    model_view(input, observations)[2])))
                action = checked(response(finding(visible_ref, field, value)),
                                 input, observations, identity)
                self.assertEqual(action["kind"], "finding")
                self.assertEqual(action["claims"], [{"ref": ref, "field": field,
                                                     "value": value}])

    def test_abstention_has_no_implicit_finding(self):
        input, observations, identity, *_ = fixture("credit")
        for reason in ("insufficient_evidence", "model_uncertainty",
                       "unsupported_capability"):
            payload = {"version": VERSION, "kind": "abstain", "claims": [],
                "uncertainty_reasons": [], "reason_code": reason}
            self.assertEqual(checked(response(payload), input, observations, identity),
                             {"kind": "abstain", "reason_code": reason})
            payload["claims"] = [{"ref": "forged", "field": "x", "value_json": "true"}]
            with self.assertRaises(TerminalContractError):
                checked(response(payload), input, observations, identity)

    def test_malformed_fabricated_and_coerced_claims_fail_closed(self):
        for specialist in ("pricing", "credit"):
            input, observations, identity, ref, field, value = fixture(specialist)
            visible_ref = (ref if specialist == "pricing" else next(iter(
                model_view(input, observations)[2])))
            good = finding(visible_ref, field, value)
            variants = []
            for key, bad in (("version", "wrong"), ("reason_code", "model_uncertainty")):
                payload = deepcopy(good); payload[key] = bad; variants.append(payload)
            for key, bad in (("ref", "forged:ref"), ("field", "unknown"),
                             ("value_json", json.dumps("wrong")),
                             ("value_json", "{not json"),
                             ("value_json", json.dumps(True))):
                payload = deepcopy(good); payload["claims"][0][key] = bad
                variants.append(payload)
            for key, bad in (("extra", "ignored"), ("claims", [])):
                payload = deepcopy(good); payload[key] = bad; variants.append(payload)
            for payload in variants:
                with self.subTest(specialist=specialist, payload=payload):
                    with self.assertRaises(TerminalContractError):
                        checked(response(payload), input, observations, identity)
            if specialist == "credit":
                payload = deepcopy(good); payload["uncertainty_reasons"] = ["unsupported"]
                with self.assertRaises(TerminalContractError):
                    checked(response(payload), input, observations, identity)

    def test_identity_ledger_and_interrupted_response_rejected(self):
        input, observations, identity, ref, field, value = fixture("pricing")
        good = response(finding(ref, field, value))
        for kw in ({"checkpoint": {**identity, "bundle_sha256": "c" * 64}},
                   {"ledger": ()}, {"ledger": (deepcopy({**observations[0],
                        "returned_refs": []}),)}):
            with self.assertRaises(TerminalContractError):
                checked(good, input, observations, identity, **kw)
        for bad in (response(finding(ref, field, value), reason="length"),
                    response(finding(ref, field, value), tokens=1025),
                    {"choices": [{"finish_reason": "stop", "message": {
                        "content": '{"version":', "tool_calls": None}}],
                     "usage": {"prompt_tokens": 180, "completion_tokens": 200}}):
            with self.assertRaises(TerminalContractError):
                checked(bad, input, observations, identity)
        no_usage = deepcopy(good); no_usage.pop("usage")
        with self.assertRaises(TerminalContractError):
            checked(no_usage, input, observations, identity)
        unsolicited_call = deepcopy(good)
        unsolicited_call["choices"][0]["message"]["tool_calls"] = [{"id": "bad"}]
        with self.assertRaises(TerminalContractError):
            checked(unsolicited_call, input, observations, identity)
        oversized = deepcopy(observations)
        oversized[0]["records"][0]["fields"]["unexpected"] = "x" * MAX_REQUEST_BYTES
        with self.assertRaises(TerminalContractError):
            draft_request(input, oversized, oversized)

    def test_existing_durable_receipt_is_terminal_on_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); directory.chmod(0o700)
            args = dict(assessment_id="offline-final-only", start_digest="a" * 64,
                        stage="final", ordinal=0, request_digest="b" * 64)
            sent = []
            def interrupted():
                sent.append(1)
                raise TimeoutError("not a retry authorization")
            with self.assertRaises(TimeoutError):
                claim_and_call(directory, **args, send=interrupted)
            path = attempt_path(directory, **{k: args[k] for k in (
                "assessment_id", "start_digest", "stage", "ordinal")})
            self.assertFalse(verify_receipt(path, **{k: args[k] for k in (
                "start_digest", "stage", "ordinal", "request_digest")}))
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **args, send=lambda: sent.append(2))
            self.assertEqual(sent, [1])
            self.assertNotIn("not a retry authorization", path.read_text())

    def test_success_receipt_also_cannot_be_replayed(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp); directory.chmod(0o700)
            args = dict(assessment_id="offline-final-returned", start_digest="a" * 64,
                        stage="final", ordinal=0, request_digest="b" * 64)
            calls = []
            self.assertEqual(claim_and_call(directory, **args,
                send=lambda: calls.append("first") or {"choices": []}), {"choices": []})
            path = attempt_path(directory, **{k: args[k] for k in (
                "assessment_id", "start_digest", "stage", "ordinal")})
            self.assertTrue(verify_receipt(path, **{k: args[k] for k in (
                "start_digest", "stage", "ordinal", "request_digest")}))
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **args, send=lambda: calls.append("second"))
            self.assertEqual(calls, ["first"])


if __name__ == "__main__":
    unittest.main()
