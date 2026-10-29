"""Sample release projection verifies actual captured graph/evaluation outputs."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from offline_release_demo import markdown, project
from run_week4_disposable import provision_and_run


EVALUATION = Path(__file__).resolve().parents[2] / "evaluation"


class ReleaseProjection(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((EVALUATION / "week4-offline-development.json").read_text())

    def test_sample_corresponds_to_captured_original_and_isolated_candidate(self):
        actual = project(self.source)
        committed = json.loads((EVALUATION / "dealdesk-offline-demo.json").read_text())
        self.assertEqual(actual, committed)
        self.assertEqual(len(actual["scenarios"]), 3)
        self.assertEqual(actual["evaluation_stable_sha256"],
                         self.source["stable_result_sha256"])
        b01, b05, n03 = actual["scenarios"]
        self.assertEqual(len(b01["fixed_specialists"]), 6)
        self.assertEqual(len(b01["offline_ai"]), 6)
        self.assertEqual(sum(bool(r["validated_claims"]) for r in b01[
            "offline_ai"].values()), 5)
        self.assertEqual(b01["offline_ai"]["fulfillment"]["contribution_kind"],
                         "abstention")
        self.assertEqual(b05["offline_ai"]["credit"]["validated_claims"], [])
        self.assertEqual(n03["offline_ai"]["fulfillment"]["execution"], "skipped")
        candidate = actual["separate_fulfillment_candidate"]
        self.assertNotEqual(candidate["assessment_id"], b01["assessment_id"])
        self.assertEqual(candidate["bundle_sha256"], b01["bundle_sha256"])
        self.assertEqual(candidate["human_approval"], "not_granted_by_system")
        self.assertEqual(set(candidate["fixed_rechecks"]), set(b01["offline_ai"]))
        self.assertEqual(markdown(actual), (EVALUATION /
            "dealdesk-offline-demo.md").read_text())

    def test_tampering_cannot_be_published_as_offline_acceptance(self):
        altered = deepcopy(self.source)
        altered["scenarios"][0]["offline_ai"]["credit"]["validated_claims"] = [
            {"ref": "credit_profile:INVENTED", "field": "credit_status"}]
        with self.assertRaises(EvidenceMismatch):
            project(altered)
        altered = deepcopy(self.source)
        altered["isolated_candidate"]["human_approval"] = "approved"
        with self.assertRaises(EvidenceMismatch):
            project(altered)
        altered = deepcopy(self.source)
        altered["scenarios"][0]["reviewer_action"] = "AI approved"
        with self.assertRaises(EvidenceMismatch):
            project(altered)
        altered = deepcopy(self.source)
        altered["stable_result_sha256"] = "0" * 64
        with self.assertRaises(EvidenceMismatch):
            project(altered)

    def test_colliding_output_paths_rejected_before_any_database_connection(self):
        output = Path("/tmp/opencode/release-overlap.json")
        with self.assertRaisesRegex(ValueError, "four distinct paths"):
            provision_and_run("invalid connection string", Path("unused"),
                              output, output, Path("unused"), Path("unused"))


if __name__ == "__main__":
    unittest.main()
