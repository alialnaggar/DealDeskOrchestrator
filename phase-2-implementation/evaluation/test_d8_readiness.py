"""Synthetic-only D8 contract tests; never use held-out answers or hosted models."""

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

import d8_readiness as d8


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Same independently maintained Phase 1C intake code as the CLI.
        cls.review = Path(os.environ.get("DEALDESK_PHASE1C_REVIEW_CHECKOUT",
                    "/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c"))
        if not cls.review.is_dir():
            raise unittest.SkipTest("Separate Phase 1C review checkout unavailable")
        d8.load_contract(cls.review)
        from phase1c_evaluation_review import build_review_workspace, digest, validate_review_workspace
        from phase1c_evaluation_acceptance import bind_source_review, empty_intake, validate_intake
        cls.workspace = staticmethod(build_review_workspace)
        cls.digest = staticmethod(digest)
        cls.validate_workspace = staticmethod(validate_review_workspace)
        cls.bind = staticmethod(bind_source_review)
        cls.empty = staticmethod(empty_intake)
        cls.validate_intake = staticmethod(validate_intake)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="d8-synthetic-", dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.cid = "SYNTHETIC-ONLY-001"
        payload = {"source_rows": {"deal": {"synthetic": True}}, "business_contract": {}, "run_context": {}}
        raw = json.dumps({"sha256": self.digest(payload), "payload": payload})
        provider = b'{"records":[]}'
        (self.folder / (self.cid + ".json")).write_text(raw)
        (self.folder / (self.cid + "-provider.json")).write_bytes(provider)
        self.index = {"cases": [{"case_id": self.cid, "packet_sha256": self.digest(payload),
                                  "provider_file_sha256": hashlib.sha256(provider).hexdigest()}]}
        self.workspace_obj = self.workspace(self.index)
        self.intake = self.empty(self.index)

    def reviewed(self):
        row = self.workspace_obj["cases"][0]
        row["review_status"] = "draft_complete"
        row["reviewer"] = {"identity": "Synthetic reviewer", "method": "human",
                            "reviewed_at": "2026-11-09T12:00:00Z", "independence_statement": "test only"}
        for role in d8.ROLES:
            row["findings"][role] = {"finding": "issue_identified" if role == "Credit" else "no_issue_identified",
                                     "evidence_refs": [{"document": "packet", "pointer": "/source_rows/deal"}],
                                     "rationale": "Synthetic source only"}
        row["overall"] = {"decision_status": "blocked", "human_actions": ["Human review"],
                           "unresolved_questions": [], "rationale": "Synthetic Credit blocker"}
        self.review_bytes = json.dumps(self.workspace_obj).encode()
        self.intake = self.bind(self.index, self.review_bytes, self.folder)
        self.assertEqual(self.validate_intake(self.intake, self.index, review_bytes=self.review_bytes,
                                              packet_directory=self.folder)["errors"], [])

    def accepted(self):
        self.reviewed()
        prior = copy.deepcopy(self.intake)
        row = self.intake["cases"][0]
        row.update(disposition="accepted", reason="Synthetic test", draft_comparison_and_assistance="Synthetic only",
                   adjudicator={"identity": "Synthetic adjudicator", "method": "human",
                                "decided_at": "2026-11-09T13:00:00Z", "source_first_attestation": "test only"})
        self.assertEqual(self.validate_intake(self.intake, self.index, review_bytes=self.review_bytes,
                                              packet_directory=self.folder)["errors"], [])
        return prior

    def test_empty_has_no_accuracy_and_missing_cases_rejected(self):
        result = d8.report(self.index, self.workspace_obj, self.intake,
                           self.validate_intake(self.intake, self.index))
        self.assertEqual(result["review"]["accepted"], 0)
        self.assertIsNone(result["metrics"]["specialist_agreement"])
        prospective = {"mode": "genuine_ai", "model_version": "synthetic-test-only",
                       "prompt_contract": "synthetic-test-only", "dataset_index_sha256": d8.PIN,
                       "phase2_commit": "synthetic-test-only", "campaign_id": "synthetic-test-only",
                       "cases": [{"case_id": self.cid, "status": "completed"}]}
        self.assertIsNone(d8.report(self.index, self.workspace_obj, self.intake,
                                    self.validate_intake(self.intake, self.index), prospective)
                          ["metrics"]["business_gate_agreement"])
        bad = copy.deepcopy(self.workspace_obj)
        bad["cases"].append(bad["cases"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            d8.report(self.index, bad, self.intake, self.validate_intake(self.intake, self.index))

    def test_source_refs_finding_metadata_and_stale_hash_fail_closed(self):
        self.reviewed()
        row = self.workspace_obj["cases"][0]
        for mutate in (lambda: row["findings"]["Credit"].update(finding="invented"),
                       lambda: row["findings"]["Credit"].update(evidence_refs=[]),
                       lambda: row["reviewer"].update(reviewed_at="yesterday"),
                       lambda: row.update(packet_sha256="0" * 64)):
            original = copy.deepcopy(row)
            mutate()
            self.assertTrue(self.validate_workspace(self.workspace_obj, self.index,
                                                    packet_directory=self.folder)["errors"])
            self.workspace_obj["cases"][0] = row = original

    def test_acceptance_requires_reviewed_predecessor(self):
        previous = self.accepted()
        d8.check_transition(self.intake, previous, self.index)
        with self.assertRaisesRegex(ValueError, "prior"):
            d8.check_transition(self.intake, None, self.index)
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            d8.check_transition(self.intake, self.empty(self.index), self.index)
        previous["cases"][0]["source_review_case_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "source review changed"):
            d8.check_transition(self.intake, previous, self.index)

    def test_run_is_provenance_bound_and_offline_mode_never_scores(self):
        self.accepted()
        row = {"case_id": self.cid, "status": "completed", "findings": {
            role: self.workspace_obj["cases"][0]["findings"][role]["finding"] for role in d8.ROLES},
            "overall": "blocked"}
        run = {"mode": "offline_scripted", "model_version": "synthetic-double",
               "prompt_contract": "synthetic-only", "dataset_index_sha256": d8.PIN,
               "phase2_commit": "synthetic-not-a-commit", "campaign_id": "synthetic-only", "cases": [row]}
        valid = self.validate_intake(self.intake, self.index, review_bytes=self.review_bytes,
                                     packet_directory=self.folder)
        self.assertIsNone(d8.report(self.index, self.workspace_obj, self.intake, valid, run)["metrics"]["specialist_agreement"])
        run["dataset_index_sha256"] = "stale"
        with self.assertRaisesRegex(ValueError, "dataset pin"):
            d8.report(self.index, self.workspace_obj, self.intake, valid, run)
        run["dataset_index_sha256"] = d8.PIN
        run["mode"] = "genuine_ai"  # purely synthetic unit test, NOT a measured model run
        scored = d8.report(self.index, self.workspace_obj, self.intake, valid, run)
        self.assertEqual(scored["metrics"]["business_gate_agreement"]["scored"], 1)
        run["cases"].append(row)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            d8.report(self.index, self.workspace_obj, self.intake, valid, run)

    def test_prompt_leak_guard(self):
        prompts = self.folder / "prompts"
        prompts.mkdir()
        (prompts / "system.py").write_text("source = 'SYNTHETIC-ONLY-001'")
        d8.check_prompt_boundary([prompts], self.index, [])
        real_ids = {"cases": [{"case_id": "EVAL-PREP-001"}]}
        (prompts / "system.py").write_text("source = 'EVAL-PREP-001'")
        with self.assertRaisesRegex(ValueError, "model-visible"):
            d8.check_prompt_boundary([prompts], real_ids, [])
        (prompts / "system.py").write_text("safe")
        with self.assertRaisesRegex(ValueError, "answer file"):
            d8.check_prompt_boundary([prompts], real_ids, [prompts / "system.py"])


if __name__ == "__main__":
    unittest.main()
