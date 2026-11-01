"""No-network prospective hosted-readiness negative controls."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from dealdesk_phase2.graph_state import SPECIALISTS
from dealdesk_phase2.m22_enablement import OfflineCampaign, _start_path
from dealdesk_phase2.m22_hosted_readiness import (
    CONTRACTS, inspect_prospective_case, run_hosted_prospective)
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_m22_registry import case


class HostedReadinessNoSend(TestCase):
    def setUp(self):
        temp = TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.case = {**case(0), "contract_versions": CONTRACTS}
        self.adapter = SimpleNamespace(validate_pinned_context=Mock())
        self.campaign = OfflineCampaign.freeze(self.root, campaign_id="offline-preview",
            phase2_sha="f" * 40, cases=[self.case, {**case(1),
                "contract_versions": CONTRACTS}], adapter=self.adapter)
        self.state = {"specialist_results": {n: {"specialist": n} for n in SPECIALISTS}}
        self.context = SimpleNamespace(**{k: self.case[k] for k in (
            "assessment_id", "original_deal_id", "source_input_digest",
            "bundle_sha256", "data_snapshot_ref")}, phase1c_run_id=self.case[
            "phase1c_run_id"], as_of_at=SimpleNamespace(isoformat=lambda: self.case["as_of_at"]))
        self.pin = SimpleNamespace(context=self.context)

    def inspect(self, case_id="C0", state=None):
        with patch("dealdesk_phase2.m22_hosted_readiness.pinned_from_state",
                   return_value=self.pin), patch(
                   "dealdesk_phase2.m22_hosted_readiness.validate_result"):
            return inspect_prospective_case(self.campaign, case_id,
                state=state if state is not None else self.state)

    def test_explicit_authority_missing_even_with_callback_or_credentials(self):
        self.campaign.preflight("C0", status="eligible")
        self.assertEqual(self.inspect()["hosted_execution"],
                         "blocked_pending_independent_authority")
        sent = Mock()
        for kwargs in ({}, {"authorized": True, "send": sent},
                       {"api_key": "gsk_fake_not_a_credential", "send": sent}):
            with self.assertRaises(EvidenceMismatch):
                run_hosted_prospective(self.campaign, "C0", **kwargs)
        sent.assert_not_called()
        self.adapter.validate_pinned_context.assert_called()

    def test_missing_ineligible_wrong_case_source_version_or_start_rejected(self):
        sent = Mock()
        with self.assertRaises(FileNotFoundError):
            self.inspect()
        self.campaign.preflight("C0", status="eligible")
        self.campaign.preflight("C1", status="ineligible", reason="not_eligible")
        with self.assertRaises(EvidenceMismatch):
            self.inspect("C1")
        with self.assertRaises(EvidenceMismatch):
            self.inspect("unknown")
        self.context.bundle_sha256 = "wrong"
        with self.assertRaises(EvidenceMismatch):
            self.inspect()
        self.context.bundle_sha256 = self.case["bundle_sha256"]
        self.assertEqual(self.inspect()["case_id"], "C0")
        _start_path(self.root, "C0").write_text("uncertain")
        with self.assertRaises(EvidenceMismatch):
            self.inspect()
        with self.assertRaises(EvidenceMismatch):
            run_hosted_prospective(self.campaign, "C0", send=sent)
        sent.assert_not_called()

    def test_changed_manifest_and_wrong_contracts_fail_before_source_reader(self):
        self.campaign.preflight("C0", status="eligible")
        path = self.root / "campaign.json"
        old = path.read_bytes()
        try:
            path.write_bytes(old.replace(b'"C0"', b'"C9"'))
            with self.assertRaises(EvidenceMismatch):
                self.inspect()
        finally:
            path.write_bytes(old)
        self.campaign.digest = "0" * 64
        with self.assertRaises(EvidenceMismatch):
            self.inspect()
        other = self.root / "wrong-model"
        other.mkdir(mode=0o700)
        self.campaign = OfflineCampaign.freeze(other, campaign_id="wrong-model",
            phase2_sha="f" * 40, cases=[{**self.case, "contract_versions": {
                **CONTRACTS, "model": "different"}}], adapter=self.adapter)
        self.campaign.preflight("C0", status="eligible")
        with self.assertRaises(EvidenceMismatch):
            self.inspect()
        self.adapter.validate_pinned_context.side_effect = EvidenceMismatch("source changed")
        with self.assertRaises(EvidenceMismatch):
            self.inspect()
