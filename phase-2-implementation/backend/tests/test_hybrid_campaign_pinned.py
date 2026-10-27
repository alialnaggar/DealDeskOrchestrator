"""Full ten-case campaign with a mocked HTTP boundary and pinned PostgreSQL."""

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dealdesk_phase2.hybrid_campaign import campaign_digest
from dealdesk_phase2.hybrid_campaign_execution import (execute_authorized_campaign,
    inspect_sources, load_identities, report_saved_campaign)
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases
from test_hybrid_provider import wire_call, wire_final

try:
    import psycopg
except ImportError:
    psycopg = None


IDENTITIES = (Path(__file__).resolve().parents[2] / "evaluation" /
              "hybrid-groq-campaign-identities.json")


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "DATABASE_URL", "REFERENCE_DATABASE_URL", "CHECKPOINT_DATABASE_URL",
    "DEALDESK_PHASE1C_CHECKOUT")),
    "Pinned synthetic/reference fixtures and separate checkpoint required")
class PinnedCampaignTests(unittest.TestCase):
    def test_case_set_source_preflight_and_mocked_sequential_campaign(self):
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connection = lambda: psycopg.connect(os.environ["DATABASE_URL"])
        reference = lambda: psycopg.connect(os.environ["REFERENCE_DATABASE_URL"])
        with connection() as conn:
            exists = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals "
                "WHERE deal_id='M18-D-B01')").fetchone()[0]
        if not exists:
            install_disposable_cases(connection())
        identities = load_identities(IDENTITIES)
        inspect_sources(adapter, lambda case: reference if case == "R03" else connection,
                        identities)

        # Reviewer-only schedules drive a fake provider response in this test;
        # the Groq request is produced exclusively from pinned evidence/tools.
        schedules = {
            "B01": ("8", "2026-09-04", "2", "2026-09-08"),
            "B02": ("6", "2026-09-04", "8", "2026-09-08"),
            "B03": ("4", "2026-09-07", "11", "2026-09-10"),
            "B04": ("3", "2026-09-08", "6", "2026-09-11"),
            "B05": ("11", "2026-09-04", "7", "2026-09-11"),
        }
        sent = []

        def fake_post(url, token, header_name, body, **kwargs):
            self.assertEqual(url, "https://api.groq.com/openai/v1/chat/completions")
            self.assertLessEqual(len(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                            ensure_ascii=False).encode()), 8192)
            self.assertNotIn("source_reviewed_answer", str(body))
            data = json.loads(body["messages"][1]["content"])
            line = data["input"]["line_id"]
            case = next((name for name in schedules if line.endswith(name)),
                        "N01" if line.endswith("N01") else "R03")
            sent.append(case)
            if "tools" in body:
                if case in schedules:
                    response = (wire_call("inspect_fulfillment_paths", {
                        "line_id": line, "purpose_code": "check_dated_path"},
                        call_id="call_mock_" + case)
                        if len(body["messages"]) == 2 else
                        wire_call("submit_proposal", {
                            "submission_kind": "binding_partial_delivery"}))
                else:
                    response = wire_call("abstain", {})
            elif case in schedules:
                first, first_date, second, second_date = schedules[case]
                response = wire_final("submit_proposal", {"line_id": line,
                    "tradeoff_code": "partial_delivery_requires_customer_acceptance",
                    "delivery_slices": [
                        {"quantity": first, "delivery_date": first_date,
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
                report = execute_authorized_campaign(authorized=True,
                    approved_digest=campaign_digest(), identities_path=IDENTITIES,
                    pinned_checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]),
                    fixture_database=os.environ["DATABASE_URL"],
                    reference_database=os.environ["REFERENCE_DATABASE_URL"],
                    checkpoint_database=os.environ["CHECKPOINT_DATABASE_URL"],
                    reservation_directory=Path(tmp))
            self.assertEqual(report["cases"], 10)
            self.assertEqual(report["requests"], 19)
            self.assertEqual(post.call_count, 19)
            self.assertEqual([sent.count(x) for x in schedules], [3] * 5)
            self.assertEqual(sent.count("N01"), 2)
            self.assertEqual(sent.count("R03"), 2)
            audit, = Path(tmp).glob("hybrid-campaign-*.audit.jsonl")
            events = [json.loads(row) for row in audit.read_text().splitlines()]
            self.assertEqual(events[-1]["event"], "campaign_completed")
            reported = report_saved_campaign(journal_path=audit,
                checkpoint_database=os.environ["CHECKPOINT_DATABASE_URL"],
                identities_path=IDENTITIES,
                pinned_checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]),
                fixture_database=os.environ["DATABASE_URL"],
                reference_database=os.environ["REFERENCE_DATABASE_URL"])
            self.assertTrue(reported["complete"])
            self.assertEqual(reported["started_eligible_cases"], 7)
            self.assertEqual(reported["unreconciled_started_eligible_cases"], 0)
            self.assertEqual(reported["aggregate"]["fixed_checked_candidates"], 5)
            self.assertEqual(reported["aggregate"]["abstentions"], 2)
            self.assertEqual(reported["control_cases_checked"], 3)
            self.assertEqual([x["case_id"] for x in events
                if x["event"] == "case_completed"],
                ["B01", "B02", "B03", "B04", "B05", "N01", "R03", "N02", "N03", "N04"])
