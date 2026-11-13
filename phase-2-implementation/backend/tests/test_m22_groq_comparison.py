"""No-network paired development comparison: frozen sources, no model send."""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from dealdesk_phase2.m22_enablement import OfflineCampaign
from dealdesk_phase2.m22_groq_comparison import BASELINE_MODEL, inspect_groq_pair
from dealdesk_phase2.m22_hosted_readiness import CONTRACTS, run_hosted_prospective
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_m22_registry import case


class GroqPairNoSend(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.other = self.root / "other"
        self.other.mkdir(mode=0o700)
        self.second = CONTRACTS["model"]
        self.left_cases = [{**case(i), "cohort": "pinned_development",
            "contract_versions": {**CONTRACTS, "model": BASELINE_MODEL}} for i in range(2)]
        self.right_cases = [{**row, "assessment_id": "B" + row["assessment_id"],
            "contract_versions": {**CONTRACTS, "model": self.second}}
            for row in self.left_cases]
        self.adapter = SimpleNamespace(validate_pinned_context=Mock())
        self.left = OfflineCampaign.freeze(self.root, campaign_id="declared-first",
            phase2_sha="f" * 40, cases=self.left_cases, adapter=self.adapter)
        self.right = OfflineCampaign.freeze(self.other, campaign_id="declared-second",
            phase2_sha="f" * 40, cases=self.right_cases, adapter=self.adapter)

    def audit(self):
        return inspect_groq_pair(self.left, self.right, second_model_id=self.second)

    def test_matching_frozen_development_cases_are_separate_and_unmeasured(self):
        self.left.preflight("C0", status="ineligible", reason="test_preflight")
        self.right.preflight("C0", status="source_preflight_failed", reason="missing_source")
        result = self.audit()
        self.assertEqual(result["execution"], "no_send_read_only")
        self.assertFalse(result["provider_model_verified"])
        self.assertFalse(result["independent_campaign_authorized"])
        self.assertIsNone(result["formal_accuracy"])
        self.assertEqual([arm["declared_model"] for arm in result["arms"]],
            [BASELINE_MODEL, self.second])
        self.assertEqual([arm["phase2_sha"] for arm in result["arms"]], ["f" * 40] * 2)
        self.assertEqual([arm["cases"][0]["failure_category"] for arm in result["arms"]],
            ["test_preflight", "missing_source"])
        self.assertEqual([arm["cases"][0]["status"] for arm in result["arms"]],
            ["ineligible", "source_preflight_failed"])
        for arm in result["arms"]:
            self.assertEqual(arm["counts"]["scheduled"], 2)
            self.assertIsNone(arm["cases"][0]["wall_ms"])
            self.assertIsNone(arm["cases"][0]["reported_tokens"])
            self.assertIsNone(arm["cases"][0]["cost_usd"])
        self.adapter.validate_pinned_context.assert_not_called()
        with self.assertRaises(EvidenceMismatch):
            run_hosted_prospective(self.left, "C0", authorized=True, send=Mock())

    def test_missing_model_invalid_or_same_id_rejected(self):
        for value in (None, "", "fake model", BASELINE_MODEL, 1):
            with self.subTest(value=value), self.assertRaises(EvidenceMismatch):
                inspect_groq_pair(self.left, self.right, second_model_id=value)
        self.right.root = self.left.root
        with self.assertRaises(EvidenceMismatch):
            self.audit()

    def test_changed_case_source_order_prompt_cohort_and_membership_fail_closed(self):
        for field, value in (("source_input_digest", "changed"),
                             ("bundle_sha256", "changed"),
                             ("as_of_at", "changed"),
                             ("cohort", "phase1c_36_held_out"),
                             ("assessment_id", self.left_cases[0]["assessment_id"])):
            with self.subTest(field=field):
                other = self.root / field
                other.mkdir(mode=0o700)
                rows = deepcopy(self.right_cases)
                rows[0][field] = value
                candidate = OfflineCampaign.freeze(other, campaign_id="changed-" + field,
                    phase2_sha="f" * 40, cases=rows, adapter=self.adapter)
                with self.assertRaises(EvidenceMismatch):
                    inspect_groq_pair(self.left, candidate, second_model_id=self.second)
        for key, value in (("prompt", "changed"), ("capture", "changed"),
                           ("model", "unmatched")):
            other = self.root / ("contract-" + key)
            other.mkdir(mode=0o700)
            rows = deepcopy(self.right_cases)
            rows[0]["contract_versions"][key] = value
            candidate = OfflineCampaign.freeze(other, campaign_id="changed-" + key,
                phase2_sha="f" * 40, cases=rows, adapter=self.adapter)
            with self.subTest(key=key), self.assertRaises(EvidenceMismatch):
                inspect_groq_pair(self.left, candidate, second_model_id=self.second)
        held = self.root / "held-out"
        held.mkdir(mode=0o700)
        rows = [{**row, "cohort": "phase1c_36_held_out"} for row in self.right_cases]
        candidate = OfflineCampaign.freeze(held, campaign_id="held-out", phase2_sha="f" * 40,
            cases=rows, adapter=self.adapter)
        with self.assertRaises(EvidenceMismatch):
            inspect_groq_pair(self.left, candidate, second_model_id=self.second)
        swapped = self.root / "swapped"
        swapped.mkdir(mode=0o700)
        candidate = OfflineCampaign.freeze(swapped, campaign_id="swapped",
            phase2_sha="f" * 40, cases=list(reversed(self.right_cases)), adapter=self.adapter)
        with self.assertRaises(EvidenceMismatch):
            inspect_groq_pair(self.left, candidate, second_model_id=self.second)
        changed_sha = self.root / "changed-sha"
        changed_sha.mkdir(mode=0o700)
        candidate = OfflineCampaign.freeze(changed_sha, campaign_id="changed-sha",
            phase2_sha="e" * 40, cases=self.right_cases, adapter=self.adapter)
        compared = inspect_groq_pair(self.left, candidate, second_model_id=self.second)
        self.assertEqual([arm["phase2_sha"] for arm in compared["arms"]],
                         ["f" * 40, "e" * 40])
        self.right.digest = "0" * 64
        with self.assertRaises(EvidenceMismatch):
            self.audit()

    def test_report_integrity_is_checked_not_interpreted_as_provider_authority(self):
        report = self.right.report()
        report["cases"][0]["bundle_sha256"] = "other"
        with patch.object(self.right, "report", return_value=report):
            with self.assertRaises(EvidenceMismatch):
                self.audit()
