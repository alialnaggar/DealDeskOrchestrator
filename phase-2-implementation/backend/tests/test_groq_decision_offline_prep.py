"""Wire-contract checks are offline and never trigger any provider transport."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from dealdesk_phase2.hybrid_contracts import HybridContractError
from dealdesk_phase2.hybrid_provider import GroqHybridTransportModel
from groq_decision_offline_prep import (_strict_wire, write_private, EXPECTED_TOOLS,
                                        MAX_REQUEST_BYTES)


class OfflineDecisionPrepTests(unittest.TestCase):
    def setUp(self):
        self.model = GroqHybridTransportModel()
        self.line = "M18-L-B06"
        self.input = SimpleNamespace(line_id=self.line, permitted_tools=(
            "inspect_line_supply", "inspect_fulfillment_paths", "inspect_evidence_record"))
        self.pack = {"model_input": {"line_id": self.line, "requested_quantity": "12",
            "requested_delivery_date": "2026-09-05", "quantity_by_requested_date": "6",
            "fixed_fulfillment_status": "late_alternative", "allow_partial_delivery": True,
            "destination_country_code": "DE", "destination_region": "Berlin"},
                     "observation": {"tool": "inspect_line_supply", "execution": "completed",
                                     "findings": {"line_id": self.line}}}
        self.body = self.model.request_decision(self.pack["model_input"],
                                                (self.pack["observation"],))

    def test_exact_production_shape_and_private_output_are_offline(self):
        with patch("dealdesk_phase2.live_models._post", side_effect=AssertionError(
                "hosted send forbidden")) as sender:
            raw = _strict_wire(self.body, self.input, self.pack)
            self.assertLess(len(raw), MAX_REQUEST_BYTES)
            self.assertEqual([x["function"]["name"] for x in self.body["tools"]],
                             list(EXPECTED_TOOLS))
            self.assertNotIn("submit_proposal", raw.decode())
            self.assertEqual(json.loads(raw)["messages"][1]["role"], "user")
            with tempfile.TemporaryDirectory(dir="/tmp/opencode") as tmp:
                from hashlib import sha256
                from os import stat
                from stat import S_IMODE
                identity = {"request_bytes": len(raw),
                            "request_sha256": sha256(raw).hexdigest()}
                write_private(Path(tmp), identity, raw)
                self.assertEqual((Path(tmp) / "decision-request.json").read_bytes(), raw + b"\n")
                self.assertEqual(S_IMODE(stat(Path(tmp) / "identity.json").st_mode), 0o600)
                with self.assertRaises(HybridContractError):
                    write_private(Path(tmp), identity, raw)
            sender.assert_not_called()

    def test_mutation_wrong_source_schema_or_token_cap_fails_closed(self):
        import copy
        for change in (lambda b: b.update(max_completion_tokens=1024),
                       lambda b: b.update(tool_choice="auto"),
                       lambda b: b["tools"].pop(),
                       lambda b: b["tools"][0]["function"]["parameters"].update(
                           additionalProperties=True),
                       lambda b: b["messages"][1].update(content='{"input":{},"observations":[]}'),
                       lambda b: b.update(response_format={"type": "json_object"})):
            with self.subTest(change=change):
                body = copy.deepcopy(self.body)
                change(body)
                with self.assertRaises(HybridContractError):
                    _strict_wire(body, self.input, self.pack)

    def test_production_parser_accepts_one_scoped_action_rejects_other_line(self):
        response = {"choices": [{"finish_reason": "tool_calls", "message": {
            "content": None, "tool_calls": [{"type": "function", "function": {
                "name": "inspect_fulfillment_paths", "arguments": json.dumps({
                    "line_id": self.line, "purpose_code": "check_dated_path"})}}]}}]}
        result = self.model.wire_adapter.parse_decision(response, self.line,
                                                         self.input.permitted_tools)
        self.assertEqual(result["tool_name"], "inspect_fulfillment_paths")
        response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = json.dumps({
            "line_id": "M18-L-B01", "purpose_code": "check_dated_path"})
        with self.assertRaisesRegex(HybridContractError, "unauthorized_inspection"):
            self.model.wire_adapter.parse_decision(response, self.line,
                                                    self.input.permitted_tools)


if __name__ == "__main__":
    unittest.main()
