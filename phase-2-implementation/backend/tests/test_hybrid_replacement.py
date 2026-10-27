"""Replacement authorization is distinct; all provider behavior is mocked."""

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from dealdesk_phase2.hybrid_campaign import (
    CASE_ORDER, CaseLocalFailure, CampaignStop, HOSTED_BUDGET,
    campaign_digest, replacement_digest, run_campaign)
from dealdesk_phase2.hybrid_campaign_execution import (
    _attest_case_local, execute_authorized_campaign, load_identities,
    report_saved_campaign)
from dealdesk_phase2.hybrid_send_reservation import attempt_path, claim_and_call
from dealdesk_phase2.live_models import ProviderError
from test_hybrid_campaign import eligible, control
from test_hybrid_provider import wire_call, wire_final
from m18_case_setup import install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


MANIFEST = (Path(__file__).resolve().parents[2] / "evaluation" /
            "hybrid-groq-replacement-identities.json")


class ReplacementPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.identities = load_identities(MANIFEST, replacement=True)
        self.assessments = {case: row["assessment_id"] for case, row in self.identities.items()}

    def test_frozen_identity_source_and_legacy_campaign_are_separate(self):
        old = load_identities(Path(__file__).resolve().parents[2] / "evaluation" /
                              "hybrid-groq-campaign-identities.json")
        self.assertNotEqual(campaign_digest(), replacement_digest())
        self.assertEqual(set(self.identities), set(CASE_ORDER))
        self.assertEqual(len(set(self.assessments.values())), 10)
        for case in CASE_ORDER:
            for key in old[case]:
                self.assertEqual(self.identities[case][key], old[case][key])
            self.assertNotIn("source_reviewed_answer", str(self.identities[case]))
        with self.assertRaisesRegex(CampaignStop, "campaign_not_authorized"):
            run_campaign(self.directory, authorized=True, approved_digest=campaign_digest(),
                execute_case=lambda *_: self.fail("old identity invoked"), assess_control=control,
                replacement=True, assessments=self.assessments)
        self.assertFalse(list(self.directory.iterdir()))

    def test_one_attested_timeout_reserves_full_budget_then_completes_other_cases(self):
        calls = []
        def run(case, left, output):
            calls.append((case, left, output))
            if case == "B01":
                raise CaseLocalFailure(case, self.assessments[case], "transport_timeout")
            result = eligible(case, candidate="not_started" if case in ("N01", "R03")
                              else "fixed_checked")
            return result.__class__(**{**result.__dict__,
                                       "assessment_id": self.assessments[case]})
        def skip(case):
            result = control(case)
            return result.__class__(**{**result.__dict__,
                                       "assessment_id": self.assessments[case]})
        result = run_campaign(self.directory, authorized=True,
            approved_digest=replacement_digest(), execute_case=run,
            assess_control=skip, replacement=True, assessments=self.assessments)
        self.assertEqual([x[0] for x in calls], list(CASE_ORDER[:7]))
        self.assertEqual(result["cases"], 9)
        self.assertEqual(result["case_local_failures"], 1)
        self.assertEqual(result["requests"], 21)
        self.assertEqual(result["reserved_request_slots"], 21)
        self.assertEqual(result["minimum_attempted_requests"], 19)
        self.assertEqual(result["output_ceilings"], 14336)
        audit, = self.directory.glob("hybrid-campaign-*.audit.jsonl")
        events = [json.loads(x) for x in audit.read_text().splitlines()]
        self.assertEqual(events[2]["event"], "case_failed")
        self.assertEqual(events[2]["reported_usage"], "incomplete")
        self.assertEqual(events[-1]["event"], "campaign_completed")
        with self.assertRaisesRegex(CampaignStop, "campaign_already_started"):
            run_campaign(self.directory, authorized=True,
                approved_digest=replacement_digest(), execute_case=run,
                assess_control=skip, replacement=True, assessments=self.assessments)

    def test_second_local_failure_and_http_rejection_stop_globally(self):
        for mode in ("second", "http"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(dir="/tmp/opencode") as tmp:
                called = []
                def run(case, *_):
                    called.append(case)
                    if mode == "http" and case == "B01":
                        raise ProviderError("http_429")
                    raise CaseLocalFailure(case, self.assessments[case], "transport_timeout")
                with self.assertRaises((CampaignStop, ProviderError)):
                    run_campaign(Path(tmp), authorized=True, approved_digest=replacement_digest(),
                        execute_case=run, assess_control=control, replacement=True,
                        assessments=self.assessments)
                self.assertEqual(called, ["B01", "B02"] if mode == "second" else ["B01"])
                audit, = Path(tmp).glob("hybrid-campaign-*.audit.jsonl")
                events = [json.loads(x) for x in audit.read_text().splitlines()]
                self.assertEqual(events[-1]["event"], "campaign_stopped")

    def test_wrong_assessment_and_unapproved_manifest_fail_closed(self):
        with self.assertRaisesRegex(CampaignStop, "replacement_assessments_invalid"):
            run_campaign(self.directory, authorized=True, approved_digest=replacement_digest(),
                execute_case=lambda *_: self.fail("called"), assess_control=control,
                replacement=True, assessments={})
        with self.assertRaisesRegex(CampaignStop, "campaign_identity_manifest_changed"):
            load_identities(Path(__file__).resolve().parents[2] / "evaluation" /
                            "hybrid-groq-campaign-identities.json", replacement=True)

    def test_case_local_requires_matching_durable_failed_marker_not_reserved_only(self):
        row = self.identities["B01"]
        start, request = "a" * 64, "b" * 64
        with self.assertRaises(ProviderError):
            claim_and_call(self.directory, assessment_id=row["assessment_id"],
                start_digest=start, stage="decision", ordinal=0,
                request_digest=request,
                send=lambda: (_ for _ in ()).throw(ProviderError("transport_timeout")))
        state = {"assessment_id": row["assessment_id"], "phase1c_run_id": row["run_id"],
            "context": {"assessment_id": row["assessment_id"],
                "bundle_sha256": row["bundle_sha256"],
                "source_input_digest": row["source_input_digest"]},
            "candidate_status": "not_started", "candidate_records": {},
            "specialist_results": {x: {} for x in (
                "configuration", "pricing", "fulfillment", "credit", "policy",
                "approval_routing")},
            "hybrid_execution": {"assessment_id": row["assessment_id"],
                "hosted_budget": HOSTED_BUDGET, "start_sha256": start, "attempts": [],
                "pending": {"stage": "decision", "ordinal": 0,
                            "request_sha256": request}}}
        graph = SimpleNamespace(get_state=lambda config: SimpleNamespace(values=state))
        self.assertEqual(_attest_case_local(graph, {}, self.directory, row,
                                            "transport_timeout"), (0, 0))
        path = attempt_path(self.directory, assessment_id=row["assessment_id"],
                            start_digest=start, stage="decision", ordinal=0)
        reserved = path.read_text().splitlines()[0]
        path.write_text(reserved + "\n")
        with self.assertRaisesRegex(CampaignStop, "case_local_attestation_failed"):
            _attest_case_local(graph, {}, self.directory, row, "transport_timeout")
        with self.assertRaises(FileExistsError):
            claim_and_call(self.directory, assessment_id=row["assessment_id"],
                start_digest=start, stage="decision", ordinal=0,
                request_digest=request, send=lambda: self.fail("replayed"))


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "DATABASE_URL", "REFERENCE_DATABASE_URL", "CHECKPOINT_DATABASE_URL",
    "DEALDESK_PHASE1C_CHECKOUT")), "Pinned PostgreSQL fixtures required")
class PinnedReplacementTests(unittest.TestCase):
    def test_timeout_on_first_b01_send_then_remaining_cases_are_mocked_and_reported(self):
        connection = lambda: psycopg.connect(os.environ["DATABASE_URL"])
        with connection() as conn:
            exists = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals "
                "WHERE deal_id='M18-D-B01')").fetchone()[0]
        if not exists:
            install_disposable_cases(connection())
        schedules = {"B02": ("6", "2026-09-04", "8", "2026-09-08"),
                     "B03": ("4", "2026-09-07", "11", "2026-09-10"),
                     "B04": ("3", "2026-09-08", "6", "2026-09-11"),
                     "B05": ("11", "2026-09-04", "7", "2026-09-11")}
        sent = []
        def fake_post(url, token, header, body, **kwargs):
            self.assertLessEqual(len(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                             ensure_ascii=False).encode()), 8192)
            self.assertNotIn("source_reviewed_answer", str(body))
            data = json.loads(body["messages"][1]["content"])
            line = data["input"]["line_id"]
            case = next((x for x in ("B01", "B02", "B03", "B04", "B05", "N01", "R03")
                         if line.endswith(x)), None)
            sent.append(case)
            if case == "B01":
                raise ProviderError("transport_timeout")
            if "tools" in body:
                if case in schedules:
                    response = (wire_call("inspect_fulfillment_paths", {"line_id": line,
                        "purpose_code": "check_dated_path"}, call_id="call_mock_" + case)
                        if len(body["messages"]) == 2
                        else wire_call("submit_proposal", {
                            "submission_kind": "binding_partial_delivery"}))
                else:
                    response = wire_call("abstain", {})
            elif case in schedules:
                first, first_date, second, second_date = schedules[case]
                response = wire_final("submit_proposal", {"line_id": line,
                    "tradeoff_code": "partial_delivery_requires_customer_acceptance",
                    "delivery_slices": [{"quantity": first, "delivery_date": first_date,
                        "source_refs": ["inventory:M18-INV-" + case]},
                        {"quantity": second, "delivery_date": second_date,
                         "source_refs": ["inbound_supply:M18-IN-" + case]}]})
            else:
                response = wire_final("abstain", {"reason_code": "model_uncertainty",
                    "scope": line, "missing_evidence": []})
            response["usage"] = {"prompt_tokens": 300, "completion_tokens": 75}
            return response

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as tmp:
            with patch.dict(os.environ, {"GROQ_API_KEY": "offline-mock-only"}), patch(
                 "dealdesk_phase2.hybrid_campaign_execution._check_databases"), patch(
                 "dealdesk_phase2.live_models._post", side_effect=fake_post) as post:
                result = execute_authorized_campaign(authorized=True,
                    approved_digest=replacement_digest(), identities_path=MANIFEST,
                    pinned_checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]),
                    fixture_database=os.environ["DATABASE_URL"],
                    reference_database=os.environ["REFERENCE_DATABASE_URL"],
                    checkpoint_database=os.environ["CHECKPOINT_DATABASE_URL"],
                    reservation_directory=Path(tmp), replacement=True)
            self.assertEqual(result["cases"], 9)
            self.assertEqual(result["case_local_failures"], 1)
            self.assertEqual(post.call_count, 17)
            self.assertEqual(result["minimum_attempted_requests"], 17)
            self.assertEqual(result["reserved_request_slots"], 19)
            self.assertEqual(sent[0], "B01")
            self.assertEqual(sent.count("B01"), 1)
            self.assertEqual(sent.count("N02"), 0)
            audit, = Path(tmp).glob("hybrid-campaign-*.audit.jsonl")
            report = report_saved_campaign(journal_path=audit,
                checkpoint_database=os.environ["CHECKPOINT_DATABASE_URL"],
                identities_path=MANIFEST,
                pinned_checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]),
                fixture_database=os.environ["DATABASE_URL"],
                reference_database=os.environ["REFERENCE_DATABASE_URL"], replacement=True)
            self.assertTrue(report["complete"])
            self.assertEqual(report["reserved_request_slots"], 19)
            self.assertEqual(report["minimum_attempted_requests"], 17)
            self.assertEqual(report["unreconciled_started_eligible_cases"], 0)
            self.assertEqual(report["aggregate"]["fixed_checked_candidates"], 4)
            self.assertEqual(report["aggregate"]["abstentions"], 2)
            self.assertEqual(report["case_local_failures"][0]["code"], "transport_timeout")
            self.assertEqual(report["control_cases_checked"], 3)

            stopped = Path(tmp) / "stopped-report-only.audit.jsonl"
            stopped.write_text("\n".join(json.dumps(x) for x in (
                {"event": "start", "digest": replacement_digest()},
                {"event": "case_reserved", "case_id": "B01"},
                {"event": "campaign_stopped", "case_id": "B01", "code": "TimeoutError"}
                )) + "\n")
            stopped.chmod(0o600)
            outstanding = report_saved_campaign(journal_path=stopped,
                checkpoint_database=os.environ["CHECKPOINT_DATABASE_URL"],
                identities_path=MANIFEST,
                pinned_checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]),
                fixture_database=os.environ["DATABASE_URL"],
                reference_database=os.environ["REFERENCE_DATABASE_URL"], replacement=True)
            self.assertEqual(outstanding["outstanding_case_reservation"], "B01")
            self.assertEqual(outstanding["reserved_request_slots"], 3)
            self.assertEqual(outstanding["minimum_attempted_requests"], 0)
            self.assertFalse(outstanding["complete"])
