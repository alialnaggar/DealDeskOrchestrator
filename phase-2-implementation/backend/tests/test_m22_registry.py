"""Offline campaign freeze and negative denominator controls; no model calls."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dealdesk_phase2.m22_registry import (register_campaign, record_preflight,
    reconcile_campaign)
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch


def case(i):
    return {"case_id": f"C{i}", "assessment_id": f"A{i}",
            "original_deal_id": f"D{i}", "phase1c_run_id": f"R{i}",
            "cohort": "fault_injection", "case_family": "offline",
            "source_input_digest": "a" * 64, "bundle_sha256": "b" * 64,
            "as_of_at": "2026-11-01T00:00:00+00:00", "data_snapshot_ref": "snapshot",
            "contract_versions": {"capture": "m22-checkpoint-observation-v1",
                                  "model": "offline", "prompt": "test-v1"}}


def observed(i, kind):
    attempts = [] if kind == "no_send" else [{"specialist": "credit", "family": "m21",
        "status": "reserved", "error_code": None}]
    if kind in ("rejected", "complete"):
        attempts.append({"specialist": "credit", "family": "m21", "status": "returned",
                         "error_code": "invalid_terminal" if kind == "rejected" else None})
    return {**{k: case(i)[k] for k in ("assessment_id", "original_deal_id",
             "phase1c_run_id", "source_input_digest", "bundle_sha256",
             "as_of_at", "data_snapshot_ref")},
        "version": "m22-checkpoint-observation-v1",
        "phase1c_pin": "90c0bc8e285ee69262c7db826b786096a77ad004",
        "attempts": attempts, "evaluation_status": "completed" if kind == "complete"
        else "stopped_or_incomplete", "failure_stage": "credit" if kind == "rejected" else None,
        "ai_original": {"credit": {"execution": "error" if kind == "rejected" else
            "completed" if kind == "complete" else "skipped",
            "reason": "invalid_terminal" if kind == "rejected" else None}}}


class CampaignRegistryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.rows = [case(i) for i in range(7)]
        self.digest = register_campaign(self.root, campaign_id="offline-WP2",
            phase2_sha="f" * 40, cases=self.rows)

    def test_counts_include_early_stops_and_returned_rejection(self):
        record_preflight(self.root, case_id="C1", status="source_preflight_failed",
                         reason="source_unavailable")
        record_preflight(self.root, case_id="C2", status="ineligible",
                         reason="declared_exclusion")
        for i in range(3, 7):
            record_preflight(self.root, case_id=f"C{i}", status="eligible")
        states = {"C3": {"stop_reason": "local_quota"}, "C4": object(),
                  "C5": object(), "C6": object()}
        observations = iter(observed(i, kind) for i, kind in ((3, "no_send"),
             (4, "reserved"), (5, "rejected"), (6, "complete")))
        with patch("dealdesk_phase2.m22_registry.capture_m22",
                   side_effect=lambda *a, **kw: next(observations)):
            report = reconcile_campaign(self.root, None,
                                        expected_manifest_sha256=self.digest, checkpoints=states)
        self.assertEqual([r["status"] for r in report["cases"]], [
            "scheduled_unobserved", "source_preflight_failed", "ineligible",
            "no_send_stopped", "reserved_unreturned", "attempted_incomplete", "completed"])
        self.assertEqual({k: report["counts"][k] for k in ("scheduled", "eligible",
            "started_eligible", "attempted_cases", "provider_send_reservations",
            "returned_responses", "validated_specialist_outputs", "completed")},
            dict(zip(("scheduled", "eligible", "started_eligible", "attempted_cases",
            "provider_send_reservations", "returned_responses",
            "validated_specialist_outputs", "completed"), (7, 4, 4, 3, 3, 2, 1, 1))))
        self.assertEqual(report["cases"][5]["failure_category"],
                         {"credit": "invalid_terminal"})
        self.assertTrue(report["cases"][4]["uncertain_delivery"])
        self.assertEqual(report["cases"][0]["receipt_verification"], "not_checked")
        self.assertEqual([report["counts"][name] for name in (
            "preflight_rejected", "no_send_stopped", "reserved_unreturned_cases",
            "returned_rejected_cases", "failed_or_incomplete")], [2, 1, 1, 1, 6])
        self.assertEqual(report["by_cohort"]["fault_injection"]["scheduled"], 7)

    def test_freeze_identity_and_preflight_fail_closed(self):
        with self.assertRaises(FileExistsError):
            register_campaign(self.root, campaign_id="offline-WP2",
                phase2_sha="f" * 40, cases=self.rows[:-1])
        with self.assertRaises(EvidenceMismatch):
            record_preflight(self.root, case_id="other", status="eligible")
        record_preflight(self.root, case_id="C0", status="source_preflight_failed",
                         reason="source_unavailable")
        with self.assertRaises(FileExistsError):
            record_preflight(self.root, case_id="C0", status="eligible")
        with self.assertRaises(EvidenceMismatch):
            reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                               checkpoints={"C0": {}})
        with self.assertRaises(EvidenceMismatch):
            reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                               checkpoints={"not_scheduled": {}})
        preflight = next(self.root.glob("*.preflight.json"))
        original_preflight = preflight.read_bytes()
        try:
            tampered = json.loads(original_preflight)
            tampered["status"] = "eligible"
            preflight.write_text(json.dumps(tampered))
            with self.assertRaises(EvidenceMismatch):
                reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                                   checkpoints={})
        finally:
            preflight.write_bytes(original_preflight)
        path = self.root / "campaign.json"
        saved = path.read_bytes()
        try:
            changed = json.loads(saved)
            changed["cases"].pop()
            path.write_text(json.dumps(changed))
            with self.assertRaises(EvidenceMismatch):
                reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                                   checkpoints={})
        finally:
            path.write_bytes(saved)

    def test_checkpoint_and_receipt_disagreement_fail_closed(self):
        record_preflight(self.root, case_id="C0", status="eligible")
        with patch("dealdesk_phase2.m22_registry.capture_m22", return_value={
                **observed(0, "complete"), "original_deal_id": "wrong"}):
            with self.assertRaises(EvidenceMismatch):
                reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                                   checkpoints={"C0": {}})
        with patch("dealdesk_phase2.m22_registry.capture_m22",
                   return_value=observed(0, "complete")), patch(
                   "dealdesk_phase2.m22_registry.reconcile_receipts",
                   return_value={"assessment_id": "wrong", "bundle_sha256": "b" * 64}):
            with self.assertRaises(EvidenceMismatch):
                reconcile_campaign(self.root, None, expected_manifest_sha256=self.digest,
                                   checkpoints={"C0": {}},
                                   receipt_root=self.root)


if __name__ == "__main__":
    unittest.main()
