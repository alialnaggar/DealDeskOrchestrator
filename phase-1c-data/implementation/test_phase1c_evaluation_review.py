"""Exercise source tampering, false review claims and incomplete review drafts.

The one-case draft below is a validator fixture, not an expected business answer.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from phase1c_evaluation_review import (build_review_workspace, digest, render,
                                      resolve_pointer, validate_review_workspace,
                                      RESPONSIBILITIES, EVALUATION, apply_review_amendments)


class ReviewWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        payload = {"case_id": "EVAL-PREP-TEST", "source_rows": {"deal": {"deal_id": "D-TEST"}},
                   "run_context": {"as_of_at": "2026-09-01T12:00:00+00:00"}}
        self.packet = {"payload": payload, "sha256": digest(payload)}
        provider = render({"schema_version": 1, "records": [{"evidence_ref": "PROOF-TEST"}]})
        self.index = {"schema_version": 1, "input_case_count": 1, "independently_reviewed_answers": 0,
                      "source_definition_sha256": "source-fixture",
                      "cases": [{"case_id": "EVAL-PREP-TEST", "packet_sha256": self.packet["sha256"],
                                 "provider_file_sha256": hashlib.sha256(provider.encode()).hexdigest()}]}
        (self.folder / "EVAL-PREP-TEST.json").write_text(render(self.packet))
        (self.folder / "EVAL-PREP-TEST-provider.json").write_text(provider)
        self.blank = build_review_workspace(self.index)

    def draft(self):
        draft = deepcopy(self.blank)
        case = draft["cases"][0]
        case["review_status"] = "draft_complete"
        case["reviewer"] = {"identity": "VALIDATOR-TEST-FIXTURE", "method": "model",
                            "reviewed_at": "2026-10-14T12:00:00+00:00",
                            "independence_statement": "Structural validator fixture; no substantive independent review."}
        for role in RESPONSIBILITIES:
            case["findings"][role] = {
                "finding": "evidence_needed", "rationale": "Validator fixture only, no business answer is asserted.",
                "evidence_refs": [{"document": "packet", "pointer": "/source_rows/deal/deal_id"},
                                  {"document": "provider", "pointer": "/records/0/evidence_ref"}]}
        case["overall"] = {"decision_status": "needs_evidence", "human_actions": ["Review the actual complete case."],
                           "unresolved_questions": [], "rationale": "Validator fixture only."}
        return draft

    def check(self, workspace):
        return validate_review_workspace(workspace, self.index, packet_directory=self.folder)

    def test_pending_and_structurally_complete_are_not_independent_answers(self):
        self.assertEqual(self.check(self.blank), {"errors": [], "pending_cases": 1,
            "complete_draft_cases": 0, "independently_reviewed_answers": 0})
        self.assertEqual(self.check(self.draft()), {"errors": [], "pending_cases": 0,
            "complete_draft_cases": 1, "independently_reviewed_answers": 0})

    def test_template_matches_all_36_pinned_identities_with_no_prefilled_answers(self):
        index = json.loads((EVALUATION / "provisional_packet_index.json").read_text())
        template = build_review_workspace(index)
        self.assertEqual((EVALUATION / "provisional_review_template.json").read_text(), render(template))
        report = validate_review_workspace(template, index)
        self.assertEqual(report, {"errors": [], "pending_cases": 36,
                                  "complete_draft_cases": 0, "independently_reviewed_answers": 0})

    def test_cannot_claim_review_acceptance_or_agent_visibility(self):
        for field, value in (("independently_reviewed_answers", 1), ("answer_key_agent_visible", True),
                             ("status", "released_answers")):
            with self.subTest(field=field):
                changed = self.draft()
                changed[field] = value
                self.assertTrue(self.check(changed)["errors"])
        changed = self.draft()
        changed["cases"][0]["review_status"] = "independently_reviewed"
        self.assertTrue(self.check(changed)["errors"])

    def test_wrong_sources_and_changed_self_seal_fail_pinned_hash(self):
        for field in ("packet_sha256", "provider_file_sha256"):
            changed = self.draft()
            changed["cases"][0][field] = "wrong"
            report = self.check(changed)
            self.assertTrue(report["errors"])
            self.assertEqual(report["complete_draft_cases"], 0)
        altered = deepcopy(self.packet)
        altered["payload"]["source_rows"]["deal"]["deal_id"] = "FORGED"
        altered["sha256"] = digest(altered["payload"])
        (self.folder / "EVAL-PREP-TEST.json").write_text(render(altered))
        self.assertTrue(self.check(self.draft())["errors"])

    def test_changed_provider_or_missing_packet_fail(self):
        (self.folder / "EVAL-PREP-TEST-provider.json").write_text('{"records":[]}')
        self.assertTrue(self.check(self.draft())["errors"])
        (self.folder / "EVAL-PREP-TEST.json").unlink()
        self.assertTrue(self.check(self.draft())["errors"])

    def test_invented_or_out_of_scope_references_fail(self):
        for pointer in ("/source_rows/inventory/999", "/case_id", "/source_rows/deal/~2bad",
                        "https://example.invalid/evidence", "/source_rows/deal/deal_id/0"):
            with self.subTest(pointer=pointer):
                changed = self.draft()
                changed["cases"][0]["findings"]["Configuration"]["evidence_refs"] = [
                    {"document": "packet", "pointer": pointer}]
                self.assertTrue(self.check(changed)["errors"])

    def test_missing_responsibility_provenance_rationale_and_automatic_approval_fail(self):
        changes = []
        d = self.draft(); del d["cases"][0]["findings"]["Credit"]; changes.append(d)
        d = self.draft(); d["cases"][0]["reviewer"] = None; changes.append(d)
        d = self.draft(); d["cases"][0]["reviewer"]["reviewed_at"] = "2026-10-14T12:00:00"; changes.append(d)
        d = self.draft(); d["cases"][0]["findings"]["Policy"]["rationale"] = ""; changes.append(d)
        d = self.draft(); d["cases"][0]["overall"]["decision_status"] = "approved"; changes.append(d)
        d = self.draft(); d["cases"][0]["findings"]["Policy"]["finding"] = []; changes.append(d)
        d = self.draft(); d["cases"][0]["overall"]["decision_status"] = []; changes.append(d)
        for changed in changes:
            self.assertTrue(self.check(changed)["errors"])

    def test_pending_cannot_hide_a_draft_and_complete_draft_needs_source_files(self):
        changed = deepcopy(self.blank)
        changed["cases"][0]["findings"]["Pricing"]["rationale"] = "Hidden draft."
        self.assertTrue(self.check(changed)["errors"])
        self.assertTrue(validate_review_workspace(self.draft(), self.index)["errors"])

    def test_case_identity_and_count_are_bound_to_index(self):
        for cases in ([], self.blank["cases"] * 2):
            changed = deepcopy(self.blank)
            changed["cases"] = cases
            self.assertTrue(self.check(changed)["errors"])
        changed = deepcopy(self.blank)
        changed["cases"][0]["case_id"] = "EVAL-PREP-OTHER"
        self.assertTrue(self.check(changed)["errors"])

    def test_business_contract_references_are_hash_bound(self):
        self.packet["payload"]["business_contract"] = {"costing": {"currency": "EUR"}}
        self.packet["sha256"] = digest(self.packet["payload"])
        self.index["cases"][0]["packet_sha256"] = self.packet["sha256"]
        self.blank = build_review_workspace(self.index)
        (self.folder / "EVAL-PREP-TEST.json").write_text(render(self.packet))
        draft = self.draft()
        draft["cases"][0]["findings"]["Pricing"]["evidence_refs"].append(
            {"document": "packet", "pointer": "/business_contract/costing/currency"})
        self.assertEqual(self.check(draft)["errors"], [])
        self.packet["payload"]["business_contract"]["costing"]["currency"] = "USD"
        self.packet["sha256"] = digest(self.packet["payload"])
        (self.folder / "EVAL-PREP-TEST.json").write_text(render(self.packet))
        self.assertTrue(self.check(draft)["errors"])

    def amendments(self):
        draft = self.draft()
        finding = deepcopy(draft["cases"][0]["findings"]["Approval"])
        finding["rationale"] = "Author-assisted fixture correction; not an accepted business answer."
        return {"schema_version":1,"status":"author_assisted_amendments_not_accepted_answers",
                "source_review_sha256":"original-bytes-sha","input_index_sha256":digest(self.index),
                "reviewer":dict(draft["cases"][0]["reviewer"],method="model_assisted"),
                "cases":[{"case_id":"EVAL-PREP-TEST","packet_sha256":draft["cases"][0]["packet_sha256"],
                          "provider_file_sha256":draft["cases"][0]["provider_file_sha256"],
                          "findings":{"Approval":finding}}]}

    def amend(self, changes):
        return apply_review_amendments(self.draft(),self.index,changes,source_review_sha256="original-bytes-sha")

    def test_author_assisted_view_preserves_original_and_zero_acceptance(self):
        original = self.draft()
        before = deepcopy(original)
        derived = apply_review_amendments(original,self.index,self.amendments(),source_review_sha256="original-bytes-sha")
        self.assertEqual(original,before)
        self.assertEqual(derived["cases"][0]["reviewer"]["method"],"model_assisted")
        self.assertEqual(self.check(derived)["errors"],[])
        self.assertEqual(derived["independently_reviewed_answers"],0)
        self.assertFalse(derived["answer_key_agent_visible"])

    def test_amendments_fail_changed_provenance_or_case_source(self):
        for key in ("source_review_sha256","input_index_sha256"):
            change=self.amendments();change[key]="different"
            with self.assertRaises(ValueError): self.amend(change)
        for key in ("packet_sha256","provider_file_sha256","case_id"):
            change=self.amendments();change["cases"][0][key]="different"
            with self.assertRaises(ValueError): self.amend(change)
        change=self.amendments();change["cases"]*=2
        with self.assertRaises(ValueError): self.amend(change)

    def test_amendments_cannot_accept_answers_or_hide_invalid_findings(self):
        for field in ("independently_reviewed_answers","answer_key_agent_visible"):
            change=self.amendments();change[field]=36
            with self.assertRaises(ValueError): self.amend(change)
        change=self.amendments();change["cases"][0]["review_status"]="accepted"
        with self.assertRaises(ValueError): self.amend(change)
        change=self.amendments();change["reviewer"]["method"]="human"
        with self.assertRaises(ValueError): self.amend(change)
        change=self.amendments();change["cases"][0]["findings"]["Approval"]["evidence_refs"]=[{"document":"packet","pointer":"/business_contract/invented"}]
        self.assertTrue(self.check(self.amend(change))["errors"])

    def test_v2_derived_hard_blocks_do_not_route_current_submission(self):
        """Check the tracked amendment view, while leaving the model draft intact."""
        review_dir = EVALUATION / "reviews"
        source_path = review_dir / "model_review_v2_draft.json"
        original = json.loads(source_path.read_text())
        before = deepcopy(original)
        index = json.loads((EVALUATION / "provisional_packet_index.json").read_text())
        amendments = json.loads((review_dir / "v2_author_amendments.json").read_text())
        derived = apply_review_amendments(
            original, index, amendments,
            source_review_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest())
        self.assertEqual(original, before)
        self.assertEqual(derived["independently_reviewed_answers"], 0)
        self.assertFalse(derived["answer_key_agent_visible"])
        for number in range(31, 35):
            case_id = f"EVAL-PREP-{number:03d}"
            case = next(c for c in derived["cases"] if c["case_id"] == case_id)
            self.assertEqual(case["overall"]["decision_status"], "blocked")
            actions = case["overall"]["human_actions"]
            self.assertTrue(any("No executable approval route" in action for action in actions))
            self.assertFalse(any("Submit the supported or revised proposal to" in action
                                 for action in actions))
            self.assertEqual(case["reviewer"]["method"], "model_assisted")

    def test_json_pointer_escapes_and_array_indices(self):
        self.assertEqual(resolve_pointer({"a/b~c": [7]}, "/a~1b~0c/0"), 7)
        for bad in ("/a/-1", "/a/00", "/a/1"):
            with self.assertRaises(ValueError):
                resolve_pointer({"a": [7]}, bad)


if __name__ == "__main__":
    unittest.main()
