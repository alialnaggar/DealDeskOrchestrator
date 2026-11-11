"""Prospective guard and offline-only source-first scoring controls."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from dealdesk_phase2.m22_enablement import OfflineCampaign, timing_observation, MeasuredIntervals
from dealdesk_phase2.m22_registry import _digest
from dealdesk_phase2.m22_scoring import score_campaign, reports
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from dealdesk_phase2.graph_state import SPECIALISTS
from test_m22_registry import case, observed


class ProspectiveOffline(TestCase):
    def setUp(self):
        tmp = TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.rows = [case(0), case(1), case(2)]
        self.campaign = OfflineCampaign.freeze(self.root, campaign_id="mock-campaign",
            phase2_sha="f" * 40, cases=self.rows, adapter=None)
        self.identity = {k: self.rows[0][k] for k in (
            "assessment_id", "original_deal_id", "phase1c_run_id",
            "source_input_digest", "bundle_sha256", "as_of_at",
            "data_snapshot_ref", "contract_versions")}

    def test_frozen_preflight_identity_and_durable_no_replay(self):
        calls = []
        def run():
            calls.append(1)
            raise TimeoutError("uncertain")
        with self.assertRaises(FileNotFoundError):
            self.campaign.execute_offline("C0", observed_identity=self.identity, execute=run)
        self.assertEqual(calls, [])
        self.campaign.preflight("C0", status="eligible")
        with self.assertRaises(EvidenceMismatch):
            self.campaign.execute_offline("C0", observed_identity={**self.identity,
                "bundle_sha256": "wrong"}, execute=run)
        self.assertEqual(calls, [])
        with self.assertRaises(TimeoutError):
            self.campaign.execute_offline("C0", observed_identity=self.identity, execute=run)
        self.assertEqual(calls, [1])
        restarted = OfflineCampaign(self.root, self.campaign.digest,
            self.campaign.campaign_id, self.campaign.phase2_sha, None)
        with self.assertRaises(FileExistsError):
            restarted.execute_offline("C0", observed_identity=self.identity, execute=run)
        self.assertEqual(calls, [1])
        report = restarted.report()
        self.assertEqual(report["started_without_checkpoint_unknown_send"], ["C0"])
        self.assertEqual(report["counts"]["scheduled"], 3)
        self.assertEqual(report["counts"]["attempted_cases"], 0)  # no checkpoint proof
        self.assertEqual(report["counts"]["started_eligible"], 1)
        self.assertEqual(report["counts"]["started_without_checkpoint_unknown_send"], 1)
        self.assertEqual(report["counts"]["failures_by_stage_category"],
            [("C0", "assessment", "unknown_send")])
        self.assertEqual(report["cases"][0]["status"],
            "started_without_checkpoint_unknown_send")
        self.assertTrue(report["cases"][0]["uncertain_delivery"])
        self.assertEqual(report["by_cohort"]["fault_injection"]["started_eligible"], 1)

    def test_changed_manifest_and_preflight_block_callback(self):
        self.campaign.preflight("C0", status="ineligible", reason="declared")
        with self.assertRaises(EvidenceMismatch):
            self.campaign.execute_offline("C0", observed_identity=self.identity,
                execute=lambda: self.fail("sent"))
        with self.assertRaises(EvidenceMismatch):
            self.campaign.execute_offline("C99", observed_identity=self.identity,
                execute=lambda: self.fail("sent"))
        self.campaign.preflight("C1", status="eligible")
        changed = deepcopy(self.rows[1]); changed["case_id"] = "C1"
        manifest = self.root / "campaign.json"
        content = manifest.read_bytes()
        try:
            manifest.write_text(content.decode().replace('"C1"', '"C9"'))
            with self.assertRaises(EvidenceMismatch):
                self.campaign.execute_offline("C1", observed_identity=changed,
                    execute=lambda: self.fail("sent"))
        finally:
            manifest.write_bytes(content)

    def test_reconciles_checkpoint_and_preserves_unstarted_cases(self):
        self.campaign.preflight("C0", status="eligible")
        with patch("dealdesk_phase2.m22_registry.capture_m22", return_value=observed(0,"complete")):
            self.campaign.execute_offline("C0", observed_identity=self.identity,
                execute=lambda: ({"checkpoint": "offline"}, False), clock=iter((0, 5_000_000)).__next__)
            report = self.campaign.report()
        self.assertEqual(report["counts"]["scheduled"], 3)
        self.assertEqual(report["counts"]["completed"], 1)
        self.assertEqual(report["wall_ms"]["C0"], 5)
        reopened = OfflineCampaign(self.root, self.campaign.digest,
            self.campaign.campaign_id, self.campaign.phase2_sha, None)
        with patch("dealdesk_phase2.m22_registry.capture_m22", return_value=observed(0,"complete")):
            self.assertEqual(reopened.report(checkpoints={"C0": ({"checkpoint":"offline"},
                False)})["wall_ms"]["C0"], 5)
        self.assertIsNone(report["wall_ms"]["C1"])
        self.assertEqual(report["cases"][1]["status"], "scheduled_unobserved")

    def test_missing_timings_and_usage_are_not_filled(self):
        result = timing_observation({"assessment_id":"A", "attempts":[
            {"status":"reserved", "specialist":"credit", "elapsed_ms":None,"tokens":None},
            {"status":"returned", "specialist":"credit", "elapsed_ms":17,
             "tokens":{"prompt_tokens":2,"completion_tokens":1}}]}, wall_ms=30,
             waits={"rate":4})
        self.assertIsNone(result["attempts"][0]["provider_elapsed_ms"])
        self.assertIsNone(result["attempts"][0]["provider_reported_tokens"])
        self.assertEqual(result["waits_ms"], {"rate":4})
        self.assertIsNone(result["orchestration_overhead_ms"])
        self.assertIsNone(result["total_tokens"])
        with self.assertRaises(EvidenceMismatch):
            timing_observation({"attempts": []}, stages={"credit":-1})
        spans = MeasuredIntervals()
        self.assertEqual(spans.measure("credit", lambda: "offline",
            clock=iter((0, 7_000_000)).__next__), "offline")
        self.assertEqual(spans.stages["credit"], 7)
        with self.assertRaises(EvidenceMismatch):
            spans.measure("credit", lambda: self.fail("duplicated"))


class SourceFirstScore(TestCase):
    def setUp(self):
        self.registry = {"campaign_id":"synthetic-only", "phase1c_pin":
            "90c0bc8e285ee69262c7db826b786096a77ad004",
            "manifest_sha256":"f"*64, "counts":{"scheduled":2},
            "cases":[{"case_id":"C0","cohort":"fault_injection","status":"completed",
                      "preflight":"eligible",
                      "assessment_id":"A","original_deal_id":"D","phase1c_run_id":"R",
                      "source_input_digest":"a"*64,"bundle_sha256":"b"*64},
                     {"case_id":"C1","cohort":"fault_injection","status":"scheduled_unobserved",
                      "preflight":None,
                      "assessment_id":"A1","original_deal_id":"D1","phase1c_run_id":"R",
                      "source_input_digest":"a"*64,"bundle_sha256":"b"*64}]}
        common = {"assessment_id":"A", "original_deal_id":"D", "phase1c_run_id":"R",
                  "source_input_digest":"a"*64,"bundle_sha256":"b"*64}
        self.answer = {**common, "fixed_findings":{n:"feasible" for n in SPECIALISTS},
            "acceptable_ai_execution":{n:["completed","abstained"] for n in SPECIALISTS},
            "candidate_comparison":"eligible", "candidate_allowed":"no",
            "expected_review_status":"approval_required"}
        self.answers = {"version":"m22-source-first-answers-v1",
            "status":"independent_accepted", "synthetic_fixture":True,
            "phase1c_pin":self.registry["phase1c_pin"],
            "manifest_sha256":self.registry["manifest_sha256"],
            "acceptance":{"reviewer_id":"synthetic-reviewer","accepted_at":"test-date",
                          "independent_source_check":True,"answer_sha256":None},
            "cases":{"C0":self.answer,"C1":{**self.answer,
                "assessment_id":"A1","original_deal_id":"D1",
                "candidate_comparison":"unsupported"}}}
        self.answers["acceptance"]["answer_sha256"] = _digest(self.answers["cases"])
        self.observation = {**common,"version":"m22-checkpoint-observation-v1",
            "fixed_original":{n:{"finding":"feasible"}
            for n in SPECIALISTS}, "ai_original":{n:{"execution":"abstained"}
            for n in SPECIALISTS}, "candidate_id":None,
            "review":{"action":"Human review required; no approval, reservation or delivery promise",
                      "customer_acceptance":None,"status":"approval_required"}}
        self.baseline = {"version":"m1.8-pinned-baseline-v1", "run_id":"R","deal_id":"D",
            "source_input_digest":"a"*64,"bundle_sha256":"b"*64,"candidate":None}

    def test_draft_rejected_and_case_source_must_match(self):
        for status in ("draft","developer_provisional","developer_supervisor_accepted"):
            self.answers["status"] = status
            with self.assertRaises(EvidenceMismatch):
                score_campaign(self.registry,{"C0":self.observation},
                    {"C0":self.baseline},self.answers)
        self.answers["status"] = "independent_accepted"
        with self.assertRaises(EvidenceMismatch):
            score_campaign(self.registry,{"C0":self.observation},
                {"C0":{**self.baseline,"bundle_sha256":"wrong"}},self.answers)

    def test_missing_unsupported_human_boundary_and_report(self):
        result = score_campaign(self.registry,{"C0":self.observation},
            {"C0":self.baseline},self.answers)
        self.assertIsNone(result["formal_accuracy"])
        self.assertEqual(result["missing_observations"],1)
        self.assertTrue(result["cases"][0]["human_review_boundary"])
        self.assertEqual(result["cases"][0]["end_to_end"], "label_agreement")
        self.assertEqual(result["cases"][0]["baseline"],"matched_no_candidate")
        self.assertEqual(result["cases"][1]["baseline"],"not_compared")
        json_report, markdown = reports(result)
        self.assertIn('"formal_accuracy": null',json_report)
        self.assertIn("Formal accuracy: unavailable",markdown)
        self.registry["cases"][1].update(status="completed",preflight="eligible")
        result = score_campaign(self.registry,{"C0":self.observation,"C1":{
            **self.observation,"assessment_id":"A1","original_deal_id":"D1"}},
            {"C0":self.baseline},self.answers)
        self.assertEqual(result["unsupported_comparisons"],1)
        self.assertEqual(result["by_cohort"]["fault_injection"]["unsupported_comparisons"],1)
        changed = deepcopy(self.observation);changed["candidate_id"]="candidate"
        result = score_campaign(self.registry,{"C0":changed},
            {"C0":self.baseline},self.answers)
        self.assertFalse(result["cases"][0]["human_review_boundary"])

    def test_model_blind_post_run_judgment_and_critical_controls(self):
        case_judgment = {"assessment_id":"A", "source_input_digest":"a"*64,
            "bundle_sha256":"b"*64, "specialists":{name:{"semantic":"uncertain",
                "evidence_quality":"unknown"} for name in SPECIALISTS},
            "overall":"uncertain", "raw_critical":["invented_citation"],
            "surviving_critical":[]}
        judgment = {"version":"m22-post-run-adjudication-v1",
            "status":"independent_accepted", "manifest_sha256":self.registry["manifest_sha256"],
            "answer_sha256":self.answers["acceptance"]["answer_sha256"],
            "acceptance":{"reviewer_id":"synthetic-reviewer", "model_blind":True,
                "independent_source_check":True, "cases_sha256":_digest({"C0":case_judgment})},
            "cases":{"C0":case_judgment}}
        scored = score_campaign(self.registry,{"C0":self.observation},
            {"C0":self.baseline},self.answers, judgments=judgment)
        self.assertIsNone(scored["formal_accuracy"])
        self.assertEqual(scored["adjudication_authentication"], "not_verified")
        self.assertEqual(scored["cases"][0]["post_run_adjudication"]["raw_critical"],
            ["invented_citation"])
        self.assertIsNone(scored["cases"][1]["post_run_adjudication"])
        variants = [
            {**judgment,"status":"developer_provisional"},
            {**judgment,"answer_sha256":"wrong"},
            {**judgment,"acceptance":{**judgment["acceptance"],"model_blind":False}},
            {**judgment,"cases":{"C1":case_judgment}},
        ]
        for changed in variants:
            with self.subTest(changed=changed):
                with self.assertRaises(EvidenceMismatch):
                    score_campaign(self.registry,{"C0":self.observation},
                        {"C0":self.baseline},self.answers,judgments=changed)
        altered = deepcopy(judgment)
        altered["cases"]["C0"]["surviving_critical"] = ["unauthorized_approval"]
        altered["acceptance"]["cases_sha256"] = _digest(altered["cases"])
        with self.assertRaises(EvidenceMismatch):
            score_campaign(self.registry,{"C0":self.observation},
                {"C0":self.baseline},self.answers,judgments=altered)

    def test_distinct_cohorts_and_excluded_baseline_identity(self):
        self.registry["cases"][1]["cohort"] = "phase1c_36_held_out"
        result = score_campaign(self.registry,{"C0":self.observation},
            {"C0":self.baseline},self.answers)
        self.assertEqual(result["by_cohort"]["fault_injection"]["scheduled"], 1)
        self.assertEqual(result["by_cohort"]["phase1c_36_held_out"]["scheduled"], 1)
        self.registry["cases"][1].update(status="completed",preflight="eligible")
        c1 = {**self.observation, "assessment_id":"A1", "original_deal_id":"D1"}
        with self.assertRaises(EvidenceMismatch):
            score_campaign(self.registry,{"C0":self.observation,"C1":c1},
                {"C0":self.baseline,"C1":{**self.baseline,"run_id":"wrong"}},self.answers)
