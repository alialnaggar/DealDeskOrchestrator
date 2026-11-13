"""Experimental Qwen wire/safety checks: offline only, no credential or sender."""

from unittest import TestCase
from unittest.mock import Mock, patch

from dealdesk_phase2.groq_dev_rate import _limits, send_with_limit
from dealdesk_phase2.groq_contract_probe import request_for_stage
from dealdesk_phase2.groq_typed_final import checked_schema
from dealdesk_phase2.hybrid_campaign import MODEL, campaign_digest
from dealdesk_phase2.hybrid_provider import GroqHybridTransportModel
from dealdesk_phase2.live_models import GROQ_MODEL
from dealdesk_phase2.m22_groq_comparison import BASELINE_MODEL
from dealdesk_phase2.m22_hosted_readiness import CONTRACTS, run_hosted_prospective
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from dealdesk_phase2.typed_final_contract import InvalidTerminal, schema


class QwenCompatibility(TestCase):
    def test_model_and_existing_frozen_contracts_are_bound(self):
        self.assertEqual(GROQ_MODEL, "qwen/qwen3.8-27b")
        self.assertEqual(MODEL, GROQ_MODEL)
        self.assertEqual(CONTRACTS["model"], GROQ_MODEL)
        self.assertEqual(BASELINE_MODEL, "openai/gpt-oss-120b")
        self.assertNotEqual(campaign_digest(), "")

    def test_tool_and_strict_final_are_separate_under_existing_caps(self):
        model = GroqHybridTransportModel()
        tool = model.request_decision({"line_id": "L1"}, ())
        final = model.request_final({"kind": "abstain"}, {"line_id": "L1"}, ())
        self.assertEqual(tool["model"], final["model"])
        self.assertEqual(tool["model"], GROQ_MODEL)
        self.assertNotIn("response_format", tool)
        self.assertEqual(tool["tool_choice"], "required")
        self.assertFalse(tool["parallel_tool_calls"])
        self.assertNotIn("tools", final)
        self.assertTrue(final["response_format"]["json_schema"]["strict"])
        self.assertNotIn("reasoning_format", tool)
        self.assertNotIn("reasoning_format", final)
        self.assertEqual(request_for_stage("tool")["model"], GROQ_MODEL)
        self.assertEqual(checked_schema(schema()), schema())
        with self.assertRaises(InvalidTerminal):
            checked_schema({"type": "object", "additionalProperties": True})

    def test_wrong_model_and_unapproved_prospective_sender_never_call_back(self):
        sender = Mock()
        body = {"model": BASELINE_MODEL, "max_completion_tokens": 1024,
                "messages": [{"role": "user", "content": "offline"}]}
        with self.assertRaisesRegex(ValueError, "rate_scope_invalid"):
            send_with_limit(body, "offline_key", sender)
        with self.assertRaises(EvidenceMismatch):
            run_hosted_prospective(authorized=True, send=sender)
        sender.assert_not_called()

    def test_free_base_limits_and_request_over_budget_fail_before_send(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual({k: _limits()[k] for k in ("RPM", "RPD", "TPM", "TPD")},
                             {"RPM": 30, "RPD": 1000, "TPM": 8000, "TPD": 200000})
        sender = Mock()
        from dealdesk_phase2.live_models import ProviderError
        with self.assertRaisesRegex(ProviderError, "groq_request_exceeds_rate_budget"):
            send_with_limit({"model": GROQ_MODEL, "max_completion_tokens": 8000,
                             "messages": [{"role": "user", "content": "offline"}]},
                            "offline_key", sender)
        sender.assert_not_called()
