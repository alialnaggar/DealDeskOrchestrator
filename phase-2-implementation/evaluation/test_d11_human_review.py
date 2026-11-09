"""Structural fixtures only: synthetic text is never a held-out judgment."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import d11_human_review as d11

ROOT = Path("/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c")
PACKETS = Path("/tmp/opencode/phase1c_original_packets")


@unittest.skipUnless(ROOT.is_dir() and PACKETS.is_dir(), "Private Phase 1C exports unavailable")
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d11-test-", dir="/tmp/opencode")
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        self.workspace = self.parent / "blind"
        d11.prepare(ROOT, PACKETS, self.workspace)
        self.blank = json.loads((self.workspace / "first_pass.json").read_text())

    def synthetic_complete(self):
        form = copy.deepcopy(self.blank)
        form["reviewer"].update({"identity": "SYNTHETIC FIXTURE — NOT A HUMAN", "role": "synthetic test",
                            "reviewed_at": "2026-01-01T00:00:00+00:00", "source_first_attestation": True,
                            "prior_ai_answer_exposure": False, "ai_assistance_used": False,
                            "assistance_details": "Synthetic structural test only; no real person",
                            "independence_limitations": "Not a human review, not an answer"})
        for row in form["cases"]:
            cid = row["case_id"]
            packet = json.loads((self.workspace / "sources" / cid / f"{cid}.json").read_text())["payload"]
            rule = packet["source_rows"]["rules"]["policy_rules"][0]["policy_rule_id"]
            cite = {"document": "packet", "pointer": "/source_rows/lines/0"}
            row["review_state"] = "draft_complete"
            row["credit_scope"] = {"use": "unresolved", "rationale": "Synthetic test: no scope adopted",
                                   "citations": [{"document": "scope", "pointer": "/credit_evidence_scope/completeness"}]}
            for role in d11.ROLES:
                row["findings"][role] = {"code": "evidence_needed", "rationale": "Synthetic fixture; no case judgment",
                                         "calculations": "Not a business calculation: structural test",
                                         "uncertainty": "No genuine reviewer", "citations": [cite], "rule_ids": [rule]}
            row["overall"] = {"status": "deferred", "gate": None, "rationale": "Synthetic fixture; no judgment",
                              "calculations": "Structural test only", "uncertainty": "No real reviewer",
                              "human_actions": ["Do not use as answer"], "citations": [cite], "rule_ids": [rule],
                              "conditional_interpretations": [], "methodology_question": "Synthetic only"}
            if cid == "EVAL-PREP-020":
                row["overall"]["conditional_interpretations"] = [
                    {"assumption": a, "gate": None, "rationale": "Synthetic structural alternative", "citations": [cite]}
                    for a in ("synthetic option A", "synthetic option B")]
        return form

    def test_blank_and_missing_duplicate_and_unverified_sources(self):
        self.assertEqual(d11.validate(self.blank, ROOT, self.workspace)["remaining"], 6)
        with self.assertRaisesRegex(ValueError, "disclosures"):
            d11.validate(self.blank, ROOT, self.workspace, require_complete=True)
        for change in ("missing", "duplicate"):
            form = copy.deepcopy(self.blank)
            if change == "missing":
                form["cases"].pop()
            else:
                form["cases"][1] = copy.deepcopy(form["cases"][0])
            with self.assertRaisesRegex(ValueError, "case IDs"):
                d11.validate(form, ROOT, self.workspace)
        provider = self.workspace / "sources" / d11.IDS[0] / f"{d11.IDS[0]}-provider.json"
        provider.write_text("{}")
        with self.assertRaisesRegex(ValueError, "source or Credit scope"):
            d11.validate(self.blank, ROOT, self.workspace)

    def test_incomplete_disclosure_citation_rule_scope_and_020(self):
        form = self.synthetic_complete()
        self.assertEqual(d11.validate(form, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)
        changes = [
            (lambda x: x["reviewer"].update(assistance_details=None), "disclosures"),
            (lambda x: x["reviewer"].update(prior_ai_answer_exposure=None), "disclosures"),
            (lambda x: x["cases"][0]["findings"]["Credit"].update(calculations=None), "incomplete"),
            (lambda x: x["cases"][0]["findings"]["Pricing"].update(citations=[{"document":"packet", "pointer":"/source_rows/lines/999"}]), "Citation"),
            (lambda x: x["cases"][0]["findings"]["Pricing"].update(rule_ids=["PO-BASE-NO-SUCH-RULE"]), "rule"),
            (lambda x: x["cases"][0]["credit_scope"].update(citations=[{"document":"packet", "pointer":"/source_rows/credit"}]), "Credit scope"),
            (lambda x: x["cases"][0].update(credit_scope_sha256="0" * 64), "pinned source"),
            (lambda x: x["cases"][3]["overall"].update(conditional_interpretations=[]), "020 requires"),
            (lambda x: x["cases"][0].update(review_state="accepted"), "acceptance transition"),
        ]
        for edit, reason in changes:
            changed = copy.deepcopy(form)
            edit(changed)
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                d11.validate(changed, ROOT, self.workspace, require_complete=True)

    def test_freeze_unlock_order_tamper_and_comparison_boundary(self):
        name = "SYNTHETIC FIXTURE — NOT A HUMAN"
        incomplete = self.workspace / "first_pass.json"
        freeze_dir = self.parent / "frozen"
        with self.assertRaisesRegex(ValueError, "disclosures"):
            d11.freeze(incomplete, self.workspace, ROOT, freeze_dir, name)
        self.assertFalse(freeze_dir.exists())
        with patch.object(d11.d10, "validate") as ai_check:
            with self.assertRaises((OSError, ValueError)):
                d11.unlock(freeze_dir, ROOT, self.workspace, self.parent / "ai.md",
                           self.parent / "manifest.json", self.parent / "comparison", name, PACKETS, owner_release=True)
            ai_check.assert_not_called()
        form = self.synthetic_complete()
        first_pass = self.parent / "synthetic_first_pass.json"
        first_pass.write_text(json.dumps(form))
        with self.assertRaisesRegex(ValueError, "identity acknowledgement"):
            d11.freeze(first_pass, self.workspace, ROOT, freeze_dir, "OTHER PERSON")
        d11.freeze(first_pass, self.workspace, ROOT, freeze_dir, name)
        receipt = d11.verify_freeze(freeze_dir, ROOT, self.workspace)
        self.assertEqual(receipt["accepted"], 0)
        first_pass.write_text("{}")
        self.assertEqual(d11.verify_freeze(freeze_dir, ROOT, self.workspace)["source_sha256"], receipt["source_sha256"])
        fake_dossier = self.parent / "synthetic_ai.md"
        fake_dossier.write_text("SYNTHETIC TEST ONLY - NOT AN ANSWER\n")
        manifest = {"private_dossier_sha256": hashlib.sha256(fake_dossier.read_bytes()).hexdigest()}
        fake_manifest = self.parent / "manifest.json"
        fake_manifest.write_text(json.dumps(manifest))
        with patch.object(d11.d10, "validate", return_value={}) as ai_check:
            dest = self.parent / "comparison"
            with self.assertRaisesRegex(ValueError, "Owner must"):
                d11.unlock(freeze_dir, ROOT, self.workspace, fake_dossier, fake_manifest, dest, name, PACKETS)
            d11.unlock(freeze_dir, ROOT, self.workspace, fake_dossier, fake_manifest, dest, name, PACKETS, owner_release=True)
            ai_check.assert_called_once()
            comparison = json.loads((dest / "comparison_blank.json").read_text())
            self.assertEqual(d11.check_comparison(comparison, freeze_dir, ROOT, self.workspace, manifest)["accepted"], 0)
            comparison["acceptances_created"] = 1
            with self.assertRaisesRegex(ValueError, "acceptance"):
                d11.check_comparison(comparison, freeze_dir, ROOT, self.workspace, manifest)
        (freeze_dir / "first_pass.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "changed"):
            d11.verify_freeze(freeze_dir, ROOT, self.workspace)
        with patch.object(d11.d10, "validate") as ai_check:
            with self.assertRaisesRegex(ValueError, "changed"):
                d11.unlock(freeze_dir, ROOT, self.workspace, fake_dossier, fake_manifest,
                           self.parent / "another", name, PACKETS, owner_release=True)
            ai_check.assert_not_called()

    def test_private_output_no_overwrite_or_git_write(self):
        with self.assertRaisesRegex(ValueError, "outside Git"):
            d11.private_new(d11.HERE / "forbidden")
        with self.assertRaisesRegex(ValueError, "already exists"):
            d11.private_new(self.workspace)

    def test_ruleless_configuration_and_availability_do_not_invent_ids(self):
        form = self.synthetic_complete()
        for role in ("Configuration", "Availability"):
            form["cases"][0]["findings"][role]["rule_ids"] = []
        self.assertEqual(d11.validate(form, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)
        form["cases"][0]["findings"]["Pricing"]["rule_ids"] = []
        with self.assertRaisesRegex(ValueError, "Missing, duplicate or unknown rule identifier"):
            d11.validate(form, ROOT, self.workspace, require_complete=True)

    def test_overall_gate_without_numbered_rule_needs_business_contract_citation(self):
        form = self.synthetic_complete()
        form["cases"][1]["overall"]["rule_ids"] = []
        with self.assertRaisesRegex(ValueError, "Missing, duplicate or unknown rule identifier"):
            d11.validate(form, ROOT, self.workspace, require_complete=True)
        form["cases"][1]["overall"]["citations"].append(
            {"document": "packet", "pointer": "/business_contract/gates"})
        self.assertEqual(d11.validate(form, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)

    def test_v2_date_only_and_v1_precise_time_are_distinct_and_supported(self):
        form = self.synthetic_complete()
        self.assertEqual(form["schema_version"], 2)
        form["reviewer"].update(reviewed_at=None, review_date="2026-11-09", review_timezone="Africa/Cairo")
        self.assertEqual(d11.validate(form, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)
        for changes in ({"review_date": "2026-11-31"}, {"review_timezone": "UTC+02:00"},
                        {"reviewed_at": "2026-11-09T12:00:00+02:00"}, {"review_date": None},
                        {"review_timezone": None}):
            bad = copy.deepcopy(form)
            bad["reviewer"].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                d11.validate(bad, ROOT, self.workspace, require_complete=True)
        freeze_dir = self.parent / "date_only_synthetic_freeze"
        path = self.parent / "date_only_synthetic.json"
        path.write_text(json.dumps(form))
        d11.freeze(path, self.workspace, ROOT, freeze_dir, form["reviewer"]["identity"])
        receipt = d11.verify_freeze(freeze_dir, ROOT, self.workspace)
        self.assertIsNone(receipt["reviewed_at"])
        self.assertEqual((receipt["review_date"], receipt["review_timezone"]), ("2026-11-09", "Africa/Cairo"))
        receipt["review_date"] = "2026-11-10"
        (freeze_dir / "receipt.json").write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "reviewer metadata differs"):
            d11.verify_freeze(freeze_dir, ROOT, self.workspace)
        index, pins, _ = d11.checked_sources(ROOT)
        old = copy.deepcopy(self.synthetic_complete())
        old["schema_version"] = 1
        old["reviewer"].pop("review_date")
        old["reviewer"].pop("review_timezone")
        self.assertEqual(d11.validate(old, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)
        legacy_blank = d11.template(index, pins, schema_version=1)
        self.assertEqual(d11.validate(legacy_blank, ROOT, self.workspace)["remaining"], 6)
        old_path = self.parent / "precise_legacy_synthetic.json"
        old_path.write_text(json.dumps(old))
        old_dir = self.parent / "precise_legacy_freeze"
        d11.freeze(old_path, self.workspace, ROOT, old_dir, old["reviewer"]["identity"])
        self.assertNotIn("review_date", d11.verify_freeze(old_dir, ROOT, self.workspace))

    def test_mixed_method_case_provenance_without_global_source_first_claim(self):
        form = self.synthetic_complete()
        form["schema_version"] = 3
        form["reviewer"].update(source_first_attestation=False, prior_ai_answer_exposure=None, ai_assistance_used=True,
                                reviewed_at=None, review_date="2026-11-09", review_timezone="Africa/Cairo")
        form["case_review_provenance"] = {
            case["case_id"]: {"source_first_attestation": i == 0,
                              "prior_ai_answer_exposure": False if i == 0 else None,
                              "ai_assistance_used": True, "method": "Synthetic mixed-method fixture; not human"}
            for i, case in enumerate(form["cases"])}
        self.assertEqual(d11.validate(form, ROOT, self.workspace, require_complete=True)["complete_drafts_not_accepted"], 6)
        for mutation in (lambda x: x["case_review_provenance"].pop(x["cases"][1]["case_id"]),
                         lambda x: x["case_review_provenance"][x["cases"][1]["case_id"]].update(
                             source_first_attestation=None),
                         lambda x: x["reviewer"].update(source_first_attestation=True)):
            bad = copy.deepcopy(form)
            mutation(bad)
            with self.assertRaises(ValueError):
                d11.validate(bad, ROOT, self.workspace, require_complete=True)
        path = self.parent / "mixed_method_fixture.json"
        path.write_text(json.dumps(form))
        frozen = self.parent / "mixed_method_fixture_freeze"
        d11.freeze(path, self.workspace, ROOT, frozen, form["reviewer"]["identity"])
        self.assertEqual(d11.verify_freeze(frozen, ROOT, self.workspace)["review_provenance_version"], 3)

    def test_blind_workspace_has_only_sources_and_blank_fields(self):
        files = {p.relative_to(self.workspace).as_posix() for p in self.workspace.rglob("*") if p.is_file()}
        expected = {"first_pass.json"} | {
            f"sources/{cid}/{name}" for cid in d11.IDS
            for name in (f"{cid}.json", f"{cid}-provider.json", "credit_scope.json")}
        self.assertEqual(files, expected)
        self.assertEqual(len(files), 19)
        self.assertTrue(all(row["review_state"] == "blank" for row in self.blank["cases"]))
        forbidden = ("model_review_v2_draft", "case_020_business_choice", "private_dossier_sha256",
                     "comparison_blank", "d10_ai_proposals")
        for item in self.workspace.rglob("*"):
            if item.is_file():
                self.assertFalse(any(marker in item.read_text().lower() for marker in forbidden), item)
                self.assertEqual(item.stat().st_mode & 0o077, 0)


if __name__ == "__main__":
    unittest.main()
