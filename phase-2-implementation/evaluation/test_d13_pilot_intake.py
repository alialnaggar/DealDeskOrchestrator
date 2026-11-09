"""Synthetic structural fixtures only; never author findings or reference answers."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import d11_human_review as d11
import d13_pilot_intake as pilot
from test_d11_human_review import ROOT, PACKETS, WorkflowTests


@unittest.skipUnless(ROOT.is_dir() and PACKETS.is_dir(), "Pinned private source-only exports unavailable")
class CandidateOnlyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d13-synthetic-", dir="/tmp/opencode")
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name) / "blind"
        d11.prepare(ROOT, PACKETS, self.workspace)
        self.blank = json.loads((self.workspace / "first_pass.json").read_text())
        self.form = WorkflowTests.synthetic_complete(self)
        self.form["schema_version"] = 3
        self.form["reviewer"].update(identity="Ali Alnaggar", role="Thesis author", reviewed_at=None,
                                     review_date="2026-11-09", review_timezone="Africa/Cairo",
                                     ai_assistance_used=True, prior_ai_answer_exposure=None,
                                     source_first_attestation=False,
                                     assistance_details="SYNTHETIC fixture, no genuine author confirmation",
                                     independence_limitations="SYNTHETIC fixture, no actual review")
        self.form["case_review_provenance"] = {}
        for i, row in enumerate(self.form["cases"]):
            row["credit_scope"]["use"] = "conditional"
            self.form["case_review_provenance"][row["case_id"]] = {
                "source_first_attestation": i == 0,
                "prior_ai_answer_exposure": False if i == 0 else None,
                "ai_assistance_used": True, "method": "SYNTHETIC fixture, no genuine review"}

    def build(self, form=None):
        return pilot.candidate(json.dumps(form or self.form).encode(), ROOT, self.workspace)

    def test_six_case_composite_candidate_only_and_legacy_is_unchanged(self):
        result = self.build()
        self.assertEqual(result["status"], "six_case_candidate_only_not_authorized_for_acceptance")
        self.assertEqual((result["accepted_reference_answers"], len(result["pilot_cases"]),
                          len(result["other_cases_pending"])), (0, 6, 30))
        self.assertEqual([x["review_method"] for x in result["pilot_cases"]],
                         ["source_first_ai_assisted_author"] + ["summary_based_ai_assisted_author"] * 5)
        self.assertIsNone(result["reviewed_at"])
        self.assertFalse(result["ready_for_generation"])
        self.assertTrue(all(pilot.validate_composite(ROOT, self.workspace)["cases"][x["case_id"]]
                            ["credit"]["evidence_state"] == "complete_synthetic_zero" for x in result["pilot_cases"]))
        # Legacy source-first/precise-time validation is not changed by this adapter.
        legacy = WorkflowTests.synthetic_complete(self)
        self.assertEqual(d11.validate(legacy, ROOT, self.workspace, require_complete=True)["accepted"], 0)

    def test_packet_provider_scope_hash_and_identity_mismatch(self):
        cid = d11.IDS[0]
        folder = self.workspace / "sources" / cid
        for file, replacement in ((folder / f"{cid}.json", "{}"),
                                  (folder / f"{cid}-provider.json", "{}"),
                                  (folder / "credit_scope.json", "{}")):
            original = file.read_bytes()
            try:
                file.write_text(replacement)
                with self.subTest(file=file.name), self.assertRaises((ValueError, KeyError)):
                    self.build()
            finally:
                file.write_bytes(original)
        scope = json.loads((folder / "credit_scope.json").read_text())
        scope["customer_id"] = "OTHER"
        (folder / "credit_scope.json").write_text(json.dumps(scope))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.build()

    def test_empty_rows_are_not_completeness_or_hard_cap_adjudication(self):
        cid = d11.IDS[-1]
        folder = self.workspace / "sources" / cid
        packet = json.loads((folder / f"{cid}.json").read_text())["payload"]
        spec, business, _, _, scopes = pilot.trusted_sources(ROOT)
        self.assertEqual(spec["schema_version"], 1)
        incomplete = copy.deepcopy(scopes[cid])
        incomplete["credit_evidence_scope"]["completeness"] = "unknown_incomplete"
        result = pilot.classify_credit(packet, incomplete, business)
        self.assertEqual(result["evidence_state"], "unknown_incomplete")
        self.assertTrue(result["known_exceeds_hard_cap"])
        self.assertFalse(result["credit_clearance_allowed"])
        self.assertEqual(result["hard_cap_adjudication_without_completeness"], "not_authorized")
        self.form["cases"][0]["credit_scope"]["use"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "Credit adoption/pins"):
            self.build()

    def test_freshness_and_rule_binding_in_source_classifier(self):
        cid = d11.IDS[-1]
        packet = json.loads((self.workspace / "sources" / cid / f"{cid}.json").read_text())["payload"]
        _, business, _, _, scopes = pilot.trusted_sources(ROOT)
        for change in (lambda x: x["source_rows"]["credit"].update(
                           commitments_as_of_at="2026-08-29 00:00:00+00:00"),
                       lambda x: x["source_rows"]["credit"].update(
                           commitments_as_of_at="2026-09-02 00:00:00+00:00"),
                       lambda x: next(r for r in x["source_rows"]["rules"]["policy_rules"]
                           if r["policy_rule_id"] == "PO-BASE-CREDIT-CAP")["condition_json"].update(
                               credit_over_limit_pct_gt=20)):
            bad = copy.deepcopy(packet)
            change(bad)
            with self.subTest(change=change), self.assertRaises(ValueError):
                pilot.classify_credit(bad, scopes[cid], business)

    def test_date_only_mixed_methods_and_unauthorized_acceptance(self):
        for change in (lambda x: x["reviewer"].update(reviewed_at="2026-11-09T12:00:00+02:00"),
                       lambda x: x["reviewer"].update(review_timezone="Invalid/Zone"),
                       lambda x: x["case_review_provenance"][d11.IDS[1]].update(source_first_attestation=True),
                       lambda x: x["cases"][0].update(review_state="accepted")):
            bad = copy.deepcopy(self.form)
            change(bad)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.build(bad)
        with self.assertRaises(ValueError):
            pilot.write_private_candidate(json.dumps(self.form).encode(), ROOT, self.workspace,
                                          Path(__file__).with_name("synthetic-answer.json"))
        self.assertFalse(Path(__file__).with_name("synthetic-answer.json").exists())


if __name__ == "__main__":
    unittest.main()
