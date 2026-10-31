"""Isolated development cases: reader selection, fixed arithmetic and uncertainty."""

import os
import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
import unittest
from unittest.mock import patch

import psycopg
from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.m21_redaction import model_view
from dealdesk_phase2.m21_specialists import _project
from dealdesk_phase2.m21_specialists import VERSION, PROMPT_VERSION, TOOLS
from dealdesk_phase2.m21_specialists import run_m21_evaluation
from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m21_groq_contract import GroqM21Model
from dealdesk_phase2.typed_final_contract import VERSION as FINAL_VERSION
from run_groq_development import _m21_campaign
from m18_case_setup import install_disposable_cases
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from m21_credit_case_setup import CASES, ids, install_credit_cases, verify_credit_case


@unittest.skipUnless(os.getenv("M21_CREDIT_DATABASE_URL") and os.getenv(
    "DEALDESK_PHASE1C_CHECKOUT"), "separately provisioned disposable PostgreSQL required")
class CreditCasePostgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = os.environ["M21_CREDIT_DATABASE_URL"]
        with psycopg.connect(db) as conn:
            baseline = conn.execute("SELECT count(*) FROM deal_desk.deals WHERE "
                "deal_id LIKE 'M18-D-%'").fetchone()[0]
            if baseline == 0:
                install_disposable_cases(conn)
            elif baseline != 9:
                raise ValueError("isolated Credit database has incomplete M18 baseline")
        with psycopg.connect(db) as conn:
            count = conn.execute("SELECT count(*) FROM deal_desk.deals WHERE "
                "deal_id LIKE 'M21CD-D-%'").fetchone()[0]
            if count == 0:
                install_credit_cases(conn)
            elif count != 3:
                raise ValueError("isolated Credit database has incomplete Credit fixtures")

    def test_selected_sources_and_fixed_results(self):
        db = os.environ["M21_CREDIT_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(db)
        with connect() as conn:
            before = conn.execute("SELECT deal_id, customer_id FROM deal_desk.deals "
                "WHERE deal_id LIKE 'M18-D-%' ORDER BY deal_id").fetchall()
            self.assertEqual(len(before), 9)
            self.assertEqual(conn.execute("SELECT count(*) FROM deal_desk.deals "
                "WHERE deal_id LIKE 'M21CD-D-%'").fetchone()[0], 3)
        expected = {
            "CR01": ("calculated", True, Decimal("9160.00"), Decimal("60.00"),
                     Decimal("40.00"), "Partially Paid", ()),
            "CR02": ("unknown", False, Decimal("9300.00"), None, None, None,
                     ("PO-BASE-CREDIT-REVIEW",)),
            "CR03": ("infeasible", True, Decimal("10100.00"), Decimal("900.00"),
                     Decimal("300.00"), "Overdue", ("PO-BASE-CREDIT-ON-HOLD",
                         "PO-BASE-CREDIT-CAP", "PO-BASE-OVERDUE-AR")),
        }
        for case in CASES:
            with self.subTest(case=case.case_id):
                ref = ids(case.case_id)
                graph = build_original_graph(adapter, connect, InMemorySaver())
                assessment = "TEST-M21CD-" + uuid4().hex
                state = graph.invoke(initial_state(assessment, case.run_id),
                    {"configurable": {"thread_id": assessment}})
                pinned = pinned_from_state(state)
                pool = adapter.validate_pinned_context(pinned)
                fixed = state["specialist_results"]["credit"]
                verify_credit_case(pool, fixed, case.case_id)
                altered = deepcopy(pool)
                if case.case_id == "CR01":
                    altered["payments"] = []
                elif case.case_id == "CR02":
                    altered["credit"]["commitments_as_of_at"] = pinned.context.as_of_at
                    altered_fixed = deepcopy(fixed)
                    altered_fixed["payload"]["commitments_fresh"] = True
                else:
                    altered["receivables"][0]["outstanding_amount"] += Decimal("1.00")
                with self.assertRaises(ValueError):
                    verify_credit_case(altered,
                        altered_fixed if case.case_id == "CR02" else fixed,
                        case.case_id)
                finding, fresh, exposure, outstanding, paid, status, hits = expected[case.case_id]
                self.assertEqual(fixed["finding"], finding)
                self.assertEqual(fixed["payload"]["commitments_fresh"], fresh)
                self.assertEqual(fixed["payload"]["credit_exposure"], exposure)
                self.assertEqual(tuple(r["rule_id"] for r in fixed["payload"]["rule_hits"]), hits)
                self.assertEqual(len(pool["receivables"]), int(outstanding is not None))
                self.assertEqual(len(pool["payments"]), int(paid is not None))
                self.assertEqual(pool["deal"]["customer_id"], ref["C"])
                records = _project(pool, state, pinned.context, "credit")
                self.assertEqual([r["ref"] for r in records], ["credit_profile:" + ref["C"]] +
                    (["receivable:" + ref["AR"], "payment:" + ref["PAY"]] if paid is not None else []))
                if paid is not None:
                    with connect() as conn:
                        original, ar_outstanding = conn.execute("SELECT original_amount, "
                            "outstanding_amount FROM deal_desk.accounts_receivable "
                            "WHERE receivable_id=%s", (ref["AR"],)).fetchone()
                        recorded_paid = conn.execute("SELECT paid_amount FROM "
                            "deal_desk.payment_history WHERE payment_id=%s",
                            (ref["PAY"],)).fetchone()[0]
                    self.assertEqual((ar_outstanding, recorded_paid), (outstanding, paid))
                    self.assertEqual(original - recorded_paid, ar_outstanding)
                    self.assertEqual(records[1]["fields"]["status"], status)
                identity = {"version": VERSION, "prompt_version": PROMPT_VERSION,
                    "assessment_id": assessment,
                    "phase1c_run_id": str(case.run_id), "subject_id": ref["D"],
                    "bundle_sha256": pinned.context.bundle_sha256,
                    "source_input_digest": pinned.context.source_input_digest,
                    "specialist": "credit", "permitted_tool": TOOLS["credit"],
                    "fixed_execution": fixed["execution"], "fixed_finding": fixed["finding"],
                    "customer_id": ref["C"], "data_snapshot_ref": pinned.context.data_snapshot_ref,
                    "as_of_at": pinned.context.as_of_at.isoformat()}
                observation = {"version": VERSION, "tool": TOOLS["credit"],
                    "execution": "completed", "records": records,
                    "returned_refs": [r["ref"] for r in records]}
                _, redacted, mapping = model_view(identity, (observation,))
                self.assertEqual(set(mapping.values()), set(observation["returned_refs"]))
                self.assertNotIn(ref["AR"], str(redacted))
                self.assertNotIn(ref["PAY"], str(redacted))
                if paid is not None:
                    self.assertEqual(redacted[0]["records"][1]["invoice_match_key"],
                        redacted[0]["records"][2]["invoice_match_key"])
                    self.assertNotIn("invoice_match_key", redacted[0]["records"][1]["fields"])
                if case.case_id == "CR02":
                    self.assertFalse(records[0]["fields"]["fixed_commitments_fresh"])
                    self.assertEqual(len(records), 1)
        with connect() as conn:
            after = conn.execute("SELECT deal_id, customer_id FROM deal_desk.deals "
                "WHERE deal_id LIKE 'M18-D-%' ORDER BY deal_id").fetchall()
            self.assertEqual(before, after)
            self.assertEqual(conn.execute("SELECT count(*) FROM deal_desk.deals "
                "WHERE deal_id LIKE 'M21CD-D-%'").fetchone()[0], 3)

    def test_credit_only_mock_send_and_no_replay(self):
        """Production gate and redaction, mocked HTTP; no provider access."""
        db = os.environ["M21_CREDIT_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        parts = psycopg.conninfo.conninfo_to_dict(db)
        name = "m21cd_checkpoint_" + uuid4().hex[:16]
        admin = psycopg.conninfo.make_conninfo(**{**parts, "dbname": "postgres"})
        checkpoint = psycopg.conninfo.make_conninfo(**{**parts, "dbname": name})
        with psycopg.connect(admin, autocommit=True) as conn:
            conn.execute("CREATE DATABASE " + name)
        try:
            with thesis_checkpointer(checkpoint) as saver:
                # Hosted identity requires one exclusive business/checkpoint pair
                # per case; exercise CR01 here, never reuse either DB for sends.
                for case in CASES[:1]:
                    with self.subTest(case=case.case_id), TemporaryDirectory(
                            dir="/tmp/opencode") as directory:
                        root = Path(directory)
                        root.chmod(0o700)
                        owner = root / "owner"
                        owner.mkdir(mode=0o700)
                        graph = build_original_graph(adapter,
                            lambda: psycopg.connect(db), saver)
                        assessment = "M21CD-MOCK-" + uuid4().hex
                        config = {"configurable": {"thread_id": assessment}}
                        before = graph.invoke(initial_state(assessment, case.run_id), config)
                        sent = []
                        def fake_post(url, key, header, body, **kwargs):
                            sent.append(body)
                            public = json.loads(body["messages"][1]["content"])
                            self.assertNotIn("M21CD-AR-", _canonical(body))
                            self.assertNotIn("M21CD-PAY-", _canonical(body))
                            if len(sent) == 2:
                                self.assertNotIn("tools", body)
                            if len(sent) == 1:
                                self.assertEqual(public["input"]["specialist"], "credit")
                                return {"usage": {"prompt_tokens": 200,
                                    "completion_tokens": 20}, "choices": [{
                                    "finish_reason": "tool_calls", "message": {
                                        "content": None, "tool_calls": [{"id":
                                        "call_m21cd_offline_0001", "type": "function",
                                        "function": {"name": TOOLS["credit"],
                                        "arguments": _canonical({"subject_id": public[
                                            "input"]["subject_id"]})}}]}}]}
                            records = public["observations"][0]["records"]
                            if case.case_id == "CR02":
                                payload = {"version": FINAL_VERSION, "kind": "abstain",
                                    "claims": [], "uncertainty_reasons": [],
                                    "reason_code": "insufficient_evidence"}
                            else:
                                chosen = records[1]
                                payload = {"version": FINAL_VERSION, "kind": "finding",
                                    "claims": [{"ref": chosen["ref"], "field":
                                        "outstanding_amount", "value_json": json.dumps(
                                        chosen["fields"]["outstanding_amount"])}],
                                    "uncertainty_reasons": [], "reason_code": "none"}
                            return {"usage": {"prompt_tokens": 400,
                                "completion_tokens": 80}, "choices": [{
                                "finish_reason": "stop", "message": {
                                    "content": json.dumps(payload)}}]}
                        with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                                "dealdesk_phase2.m21_groq_contract._post",
                                side_effect=fake_post) as sender:
                            digest, state = _m21_campaign(graph, config, adapter,
                                case_id=case.case_id, owner=owner, root=root,
                                key="gsk_offline_test_placeholder_123456789",
                                credit_only=True)
                            self.assertEqual(sender.call_count, 2)
                            result = state["m21_ai_results"]["credit"]
                            self.assertEqual(result["execution"],
                                "abstained" if case.case_id == "CR02" else "completed")
                            self.assertEqual(state["specialist_results"],
                                before["specialist_results"])
                            self.assertEqual(state["candidate_status"], "not_started")
                            self.assertFalse(state.get("m21_review"))
                            if case.case_id != "CR02":
                                self.assertEqual(result["validated_claims"][0]["ref"],
                                    "receivable:" + ids(case.case_id)["AR"])
                            with patch.dict(os.environ, {"GROQ_SECONDARY_API_KEY":
                                    "gsk_offline_test_placeholder_123456789"}):
                                again = run_m21_evaluation(graph, config, adapter,
                                    {key: GroqM21Model(key) for key in TOOLS},
                                    manifest=json.loads((root / "manifest.json").read_text()),
                                    approved_manifest_sha256=digest, authorized=True,
                                    owner_dir=owner, free_tier_billing_disabled=True,
                                    development_selection=("credit",))
                            self.assertEqual(again["m21_ai_results"], state["m21_ai_results"])
                            self.assertEqual(sender.call_count, 2)
        finally:
            with psycopg.connect(admin, autocommit=True) as conn:
                conn.execute("DROP DATABASE " + name)
