"""Offline Qwen Configuration tool-wire regression; no provider or replay."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from dealdesk_phase2.groq_development import CONFIG_WIRE as MANIFEST_CONFIG_WIRE
from dealdesk_phase2.groq_typed_final import configuration_final_body
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.live_models import GROQ_MODEL
from dealdesk_phase2.m20_groq import (CONFIGURATION_QWEN_WIRE_VERSION, WIRE_VERSION,
    GroqM20Model, request_body, validate_configuration_tool_wire)
from dealdesk_phase2.typed_final_hosted import CONFIG_WIRE, _ConfigurationModel


class QwenConfigurationWire(TestCase):
    def setUp(self):
        self.input = {"specialist": "configuration", "permitted_tool":
            "inspect_configuration_line", "line_ids": ["L1"]}

    def test_missing_or_raw_reasoning_from_old_shape_fails_closed(self):
        corrected = request_body(self.input, ())
        original_shape = {k: v for k, v in corrected.items() if k != "reasoning_format"}
        self.assertEqual(set(original_shape), {"model", "temperature",
            "max_completion_tokens", "parallel_tool_calls", "tool_choice", "tools",
            "messages"})
        for value in (None, "raw", "unknown"):
            with self.subTest(reasoning_format=value):
                malformed = deepcopy(original_shape)
                if value is not None:
                    malformed["reasoning_format"] = value
                with self.assertRaisesRegex(ValueError, "configuration_tool_wire_invalid"):
                    validate_configuration_tool_wire(malformed)
        mixed = deepcopy(corrected)
        mixed["response_format"] = {"type": "json_schema"}
        with self.assertRaisesRegex(ValueError, "configuration_tool_wire_invalid"):
            validate_configuration_tool_wire(mixed)
        self.assertNotEqual(sha256(_canonical(original_shape).encode()).hexdigest(),
                            sha256(_canonical(corrected).encode()).hexdigest())

    def test_corrected_tool_and_unchanged_pricing_final_budgets(self):
        tool = request_body(self.input, ())
        validate_configuration_tool_wire(tool)
        self.assertEqual(tool["model"], GROQ_MODEL)
        self.assertEqual(tool["reasoning_format"], "parsed")
        self.assertEqual(tool["tool_choice"], "required")
        self.assertIs(tool["parallel_tool_calls"], False)
        self.assertEqual(tool["max_completion_tokens"], 512)
        self.assertLessEqual(len(_canonical(tool).encode()), 8192)
        self.assertNotIn("response_format", tool)
        self.assertEqual([t["function"]["name"] for t in tool["tools"]],
            ["inspect_configuration_line", "submit_finding", "abstain"])
        self.assertEqual(CONFIG_WIRE, MANIFEST_CONFIG_WIRE)
        self.assertEqual(CONFIG_WIRE, CONFIGURATION_QWEN_WIRE_VERSION)
        self.assertEqual(GroqM20Model("configuration").wire_version, CONFIG_WIRE)
        self.assertEqual(GroqM20Model("pricing").wire_version, WIRE_VERSION)
        pricing = request_body({**self.input, "specialist": "pricing",
            "permitted_tool": "inspect_pricing_line"}, ())
        self.assertNotIn("reasoning_format", pricing)
        final = configuration_final_body(self.input, ({"tool":
            "inspect_configuration_line", "execution": "completed"},))
        self.assertNotIn("reasoning_format", final)
        self.assertNotIn("tools", final)
        self.assertTrue(final["response_format"]["json_schema"]["strict"])
        self.assertEqual(final["max_completion_tokens"], 1024)

    def test_tampered_tool_request_cannot_reserve_or_invoke_sender(self):
        send, pre_send = Mock(), Mock()
        with TemporaryDirectory(dir="/tmp/opencode") as directory:
            model = _ConfigurationModel(send, Path(directory), "fresh-assessment",
                "a" * 64, pre_send, development=True)
            for change in (lambda body: body.pop("reasoning_format"),
                           lambda body: body.update(reasoning_format="raw")):
                body = request_body(self.input, ())
                change(body)
                model.pending_request_digest = sha256(_canonical(body).encode()).hexdigest()
                with patch.object(model, "prepare_request", return_value=body):
                    with self.assertRaisesRegex(ValueError, "configuration_tool_wire_invalid"):
                        model.next_action(self.input, ())
            self.assertEqual(list(Path(directory).iterdir()), [])
        send.assert_not_called()
        pre_send.assert_not_called()
