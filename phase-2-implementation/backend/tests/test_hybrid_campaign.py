"""Campaign-level gates; scripted callbacks cannot contact a model provider."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dealdesk_phase2.hybrid_campaign import (
    CASE_ORDER, CONTROLS, ELIGIBLE, MAX_OUTPUT_CEILINGS, MAX_REQUESTS,
    CampaignStop, CaseReceipt, campaign_digest, run_campaign)
from dealdesk_phase2.hybrid_campaign_execution import (execute_authorized_campaign,
    load_identities)


IDENTITIES = (Path(__file__).resolve().parents[2] / "evaluation" /
              "hybrid-groq-campaign-identities.json")


def eligible(case, *, requests=3, usage=True, candidate="fixed_checked"):
    return CaseReceipt(case, "HYBRID-CAMPAIGN-" + case, requests,
        2048 if requests == 3 else (512 if requests == 1 else 1024),
        1400 if usage else None, 400 if usage else None, candidate,
        "completed", "binding_proposal" if candidate == "fixed_checked" else "abstention")


def control(case):
    return CaseReceipt(case, "HYBRID-CAMPAIGN-" + case, 0, 0, None, None,
                       "not_started", "skipped", None)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.calls = []

    def events(self):
        path, = self.dir.glob("hybrid-campaign-*.audit.jsonl")
        return [json.loads(line) for line in path.read_text().splitlines()]

    def test_closed_gate_never_invokes_callbacks_or_creates_journal(self):
        for authorized, digest in ((False, campaign_digest()), (True, "wrong")):
            with self.assertRaisesRegex(CampaignStop, "campaign_not_authorized"):
                run_campaign(self.dir, authorized=authorized, approved_digest=digest,
                    execute_case=lambda *args: self.fail("model callback invoked"),
                    assess_control=lambda *args: self.fail("control callback invoked"))
        self.assertEqual(list(self.dir.iterdir()), [])

        with patch("dealdesk_phase2.hybrid_campaign_execution.psycopg.connect",
                   side_effect=AssertionError("database opened")), patch(
                       "dealdesk_phase2.live_models._post",
                       side_effect=AssertionError("hosted request")):
            with self.assertRaisesRegex(CampaignStop, "campaign_not_authorized"):
                execute_authorized_campaign(authorized=False,
                    approved_digest=campaign_digest(), identities_path=IDENTITIES,
                    pinned_checkout=Path("/not-read"), fixture_database="not-opened",
                    reference_database="not-opened", checkpoint_database="not-opened",
                    reservation_directory=self.dir)

    def test_manifest_is_frozen_and_contains_no_reviewer_answer(self):
        identities = load_identities(IDENTITIES)
        self.assertEqual(set(identities), set(CASE_ORDER))
        self.assertNotIn("delivery_slices", str(identities))
        changed = self.dir / "tampered.json"
        changed.write_text(IDENTITIES.read_text().replace('"B01"', '"X01"', 1))
        with self.assertRaisesRegex(CampaignStop, "identity_manifest_changed"):
            load_identities(changed)

    def test_one_pass_order_and_global_budget_are_fsynced(self):
        def run(case, left, remaining):
            self.calls.append((case, left, remaining))
            return eligible(case, candidate="not_started" if case in ("N01", "R03")
                            else "fixed_checked")

        def skipped(case):
            self.calls.append((case, "fixed_gate"))
            return control(case)

        result = run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                              execute_case=run, assess_control=skipped)
        self.assertEqual(tuple(x[0] for x in self.calls), CASE_ORDER)
        self.assertEqual((result["requests"], result["output_ceilings"]),
                         (MAX_REQUESTS, MAX_OUTPUT_CEILINGS))
        self.assertEqual(len(ELIGIBLE), 7)
        self.assertEqual(len(CONTROLS), 3)
        events = self.events()
        self.assertEqual([x["event"] for x in events].count("case_reserved"), 10)
        self.assertEqual(events[-1]["event"], "campaign_completed")
        self.assertNotIn("source_reviewed_answer", str(events))
        with self.assertRaisesRegex(CampaignStop, "campaign_already_started"):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=run, assess_control=skipped)
        self.assertEqual(len(self.calls), 10)

    def test_uncertain_send_and_errors_stop_all_later_cases(self):
        def uncertain(case, left, remaining):
            self.calls.append(case)
            raise TimeoutError("uncertain")

        with self.assertRaises(TimeoutError):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=uncertain, assess_control=control)
        self.assertEqual(self.calls, ["B01"])
        self.assertEqual([x["event"] for x in self.events()],
            ["start", "case_reserved", "campaign_stopped"])
        with self.assertRaisesRegex(CampaignStop, "campaign_already_started"):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=uncertain, assess_control=control)

    def test_missing_usage_and_unsafe_adverse_candidate_stop(self):
        for result, code in ((eligible("B01", usage=False), "usage_unverifiable"),
                             (eligible("B01", requests=4), "case_receipt_invalid"),
                             (CaseReceipt("B01", "id", 2, 1024, 100, 50,
                                          "fixed_rejected", "error", None),
                              "case_safety_outcome")):
            with self.subTest(code=code), tempfile.TemporaryDirectory(
                    dir="/tmp/opencode") as tmp:
                with self.assertRaisesRegex(CampaignStop, code):
                    run_campaign(Path(tmp), authorized=True, approved_digest=campaign_digest(),
                        execute_case=lambda *args: result, assess_control=control)

    def test_adverse_and_control_must_not_produce_candidates_or_requests(self):
        def run(case, left, remaining):
            self.calls.append(case)
            if case == "N01":
                return eligible(case)  # unsafe binding candidate
            return eligible(case)

        with self.assertRaisesRegex(CampaignStop, "case_safety_outcome"):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=run, assess_control=control)
        self.assertEqual(self.calls, ["B01", "B02", "B03", "B04", "B05", "N01"])

    def test_token_threshold_blocks_next_case(self):
        def run(case, left, remaining):
            self.calls.append(case)
            return CaseReceipt(case, case, 1, 512, 10000, 300,
                               "not_started", "completed", "abstention")

        with self.assertRaisesRegex(CampaignStop, "reported_token_threshold_exceeded"):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=run, assess_control=control)
        self.assertEqual(len(self.calls), 6)

    def test_one_contained_model_failure_continues_second_stops(self):
        def run(case, left, remaining):
            self.calls.append(case)
            if case in ("B01", "B03"):
                return CaseReceipt(case, case, 2, 1536, 900, 300,
                    "not_started", "error", None,
                    rejection_codes=("invalid_binding_shape",),
                    contained_error="hybrid_rejected:invalid_binding_shape")
            return eligible(case)

        with self.assertRaisesRegex(CampaignStop, "repeated_contained_model_failures"):
            run_campaign(self.dir, authorized=True, approved_digest=campaign_digest(),
                execute_case=run, assess_control=control)
        self.assertEqual(self.calls, ["B01", "B02", "B03"])
        self.assertEqual(self.events()[-1]["code"], "repeated_contained_model_failures")
