"""Check reviewer intake cannot promote source-free or model drafts."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from phase1c_evaluation_review import build_review_workspace, digest, render, EVALUATION, RESPONSIBILITIES
from phase1c_evaluation_acceptance import (empty_intake, bind_source_review,
                                           check_v2_index, validate_intake)


class AcceptanceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        payload = {"case_id": "EVAL-PREP-TEST", "source_rows": {"deal": {"deal_id": "D-TEST"}},
                   "run_context": {"as_of_at": "2026-09-01T12:00:00+00:00"}}
        packet = {"payload": payload, "sha256": digest(payload)}
        provider = render({"schema_version": 1, "records": []})
        self.index = {"schema_version": 1, "cases": [{
            "case_id": payload["case_id"], "packet_sha256": packet["sha256"],
            "provider_file_sha256": hashlib.sha256(provider.encode()).hexdigest()}]}
        (self.folder / "EVAL-PREP-TEST.json").write_text(render(packet))
        (self.folder / "EVAL-PREP-TEST-provider.json").write_text(provider)
        self.blank = empty_intake(self.index)

    def review(self, method="human"):
        workspace = build_review_workspace(self.index)
        case = workspace["cases"][0]
        case["review_status"] = "draft_complete"
        case["reviewer"] = {"identity": "REVIEWER-TEST", "method": method,
                            "reviewed_at": "2026-10-22T09:00:00+02:00",
                            "independence_statement": "Fixture only; no real review or business answer."}
        for role in RESPONSIBILITIES:
            case["findings"][role] = {"finding": "evidence_needed",
                "evidence_refs": [{"document": "packet", "pointer": "/source_rows/deal/deal_id"}],
                "rationale": "Synthetic structural fixture, not a business conclusion."}
        case["overall"] = {"decision_status": "needs_evidence",
            "human_actions": ["Review this fixture."], "unresolved_questions": [],
            "rationale": "Only checks structure."}
        return workspace

    def intake(self, workspace=None, disposition="accepted"):
        workspace = workspace or self.review()
        data = render(workspace).encode()
        intake = deepcopy(self.blank)
        intake["source_review_file_sha256"] = hashlib.sha256(data).hexdigest()
        row = intake["cases"][0]
        row["disposition"] = disposition
        row["source_review_case_sha256"] = digest(workspace["cases"][0])
        row["adjudicator"] = {"identity": "HUMAN-TEST", "method": "human",
            "decided_at": "2026-10-22T10:00:00+02:00",
            "source_first_attestation": "Test-only assertion; not a real independent review."}
        row["reason"] = "A fixture disposition with no actual business acceptance."
        row["draft_comparison_and_assistance"] = "No external draft was consulted in this fixture."
        return intake, data

    def check(self, intake, data=None):
        return validate_intake(intake, self.index, review_bytes=data, packet_directory=self.folder)

    def test_real_index_builds_36_pending_without_answers(self):
        index_path = EVALUATION / "provisional_packet_index.json"
        if not index_path.exists():
            index_path = Path(__file__).resolve().parent / "provisional_packet_index.json"
        index = json.loads(index_path.read_text())
        check_v2_index(index)
        report = validate_intake(empty_intake(index), index)
        self.assertEqual(report, {"errors": [], "pending_cases": 36,
            "reviewed_pending_cases": 0,
            "recorded_acceptances": 0, "recorded_rejections": 0,
            "independence_or_correctness_certified": False})

    def test_intake_cli_index_pin_rejects_coherent_unapproved_version(self):
        index_path = EVALUATION / "provisional_packet_index.json"
        if not index_path.exists():
            index_path = Path(__file__).resolve().parent / "provisional_packet_index.json"
        index = json.loads(index_path.read_text())
        check_v2_index(index)
        changed = deepcopy(index)
        changed["cases"][0]["packet_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "differs from pinned v2"):
            check_v2_index(changed)
        changed = deepcopy(index)
        changed["source_definition_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "differs from pinned v2"):
            check_v2_index(changed)

    def test_binding_human_review_is_pending_not_acceptance(self):
        data = render(self.review()).encode()
        intake = bind_source_review(self.index, data, self.folder)
        report = self.check(intake, data)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["reviewed_pending_cases"], 1)
        self.assertEqual(report["recorded_acceptances"], 0)
        self.assertFalse(report["independence_or_correctness_certified"])
        changed = deepcopy(intake)
        changed["cases"][0]["reason"] = "Premature decision"
        self.assertTrue(self.check(changed, data)["errors"])
        with self.assertRaises(ValueError):
            bind_source_review(self.index, render(self.review("model")).encode(), self.folder)

    def test_structural_human_record_never_certifies_correctness(self):
        intake, data = self.intake()
        report = self.check(intake, data)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["recorded_acceptances"], 1)
        self.assertFalse(report["independence_or_correctness_certified"])
        rejected, data = self.intake(disposition="rejected")
        self.assertEqual(self.check(rejected, data)["recorded_rejections"], 1)

    def test_model_and_model_assisted_drafts_cannot_be_recorded_as_accepted(self):
        for method in ("model", "model_assisted"):
            with self.subTest(method=method):
                intake, data = self.intake(self.review(method))
                report = self.check(intake, data)
                self.assertTrue(report["errors"])
                self.assertEqual(report["recorded_acceptances"], 0)

    def test_pins_and_full_source_files_required(self):
        intake, data = self.intake()
        self.assertTrue(self.check(intake)["errors"])
        self.assertTrue(self.check(intake, data + b" ")["errors"])
        changed = deepcopy(intake); changed["cases"][0]["packet_sha256"] = "other"
        self.assertTrue(self.check(changed, data)["errors"])
        changed = deepcopy(intake); changed["cases"][0]["source_review_case_sha256"] = "other"
        self.assertTrue(self.check(changed, data)["errors"])
        (self.folder / "EVAL-PREP-TEST-provider.json").write_text('{"records":[{"changed":true}]}')
        self.assertTrue(self.check(intake, data)["errors"])

    def test_pending_and_release_claims_fail(self):
        for field, value in (("answer_key_agent_visible", True),
                             ("ready_for_generation", True), ("status", "released")):
            with self.subTest(field=field):
                changed = deepcopy(self.blank); changed[field] = value
                self.assertTrue(self.check(changed)["errors"])
        changed = deepcopy(self.blank); changed["cases"][0]["reason"] = "Hidden answer"
        self.assertTrue(self.check(changed)["errors"])
        changed = deepcopy(self.blank); changed["cases"][0]["disposition"] = "accepted"
        self.assertTrue(self.check(changed)["errors"])

    def test_adjudication_provenance_and_order_required(self):
        intake, data = self.intake()
        variants = []
        change = deepcopy(intake); change["cases"][0]["adjudicator"]["method"] = "model"; variants.append(change)
        change = deepcopy(intake); change["cases"][0]["adjudicator"]["decided_at"] = "2026-10-22T08:00:00+02:00"; variants.append(change)
        change = deepcopy(intake); change["cases"][0]["adjudicator"]["decided_at"] = "2026-10-22T10:00:00"; variants.append(change)
        change = deepcopy(intake); change["cases"][0]["draft_comparison_and_assistance"] = ""; variants.append(change)
        for change in variants:
            self.assertTrue(self.check(change, data)["errors"])


if __name__ == "__main__":
    unittest.main()
