"""M1.8 engineering tests, not evidence of live model business accuracy."""

import os
from pathlib import Path
import unittest

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.evaluation_m18 import (adjudicate, capture_trial,
                                             pinned_baseline, structural_flags)
from dealdesk_phase2.live_m18 import SOURCES, run_one
from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.candidate_contract import CANDIDATE_VERSION, TRADEOFF, construct_candidate
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.investigation_graph import run_original_investigate_and_review
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None

DB_READY = bool(psycopg and os.getenv("DATABASE_URL") and
                os.getenv("DEALDESK_PHASE1C_CHECKOUT"))


def observation():
    baseline = {"run_id": "R", "deal_id": "D", "bundle_sha256": "H",
        "source_input_digest": "S", "discovered": True,
        "candidate": {"slices": [{"quantity": "8", "delivery_date": "2026-09-04"},
                                  {"quantity": "2", "delivery_date": "2026-09-08"}]}}
    state = {"assessment_id": "A", "phase1c_run_id": "R",
        "context": {"assessment_id": "A", "phase1c_run_id": "R",
                    "original_deal_id": "D", "bundle_sha256": "H",
                    "source_input_digest": "S"},
        "reviewer_package": {"candidates": [], "original": {"deal_id": "D"}},
        "ai_fulfillment_result": {"execution": "completed", "contribution": {"kind": "abstention"}},
        "ai_claim_audit": [{"original_claim": "unsupported", "reason": "not_returned"}],
        "tool_access_ledger": [{"counted": True, "tool": "inspect_fulfillment_paths",
                                "status": "completed", "returned_refs": ["inventory:X"]}]}
    return state, baseline


class CaptureTests(unittest.TestCase):
    def test_cases_distinct_and_separately_classified(self):
        self.assertEqual((sum(x.case_id.startswith("B") for x in CASES),
                          sum(x.case_id.startswith("N") for x in CASES)), (5, 4))
        self.assertEqual(len({x.run_id for x in CASES}), len(CASES))
        self.assertEqual(len({x.ids()["P"] for x in CASES}), len(CASES))
        self.assertGreaterEqual(len({(x.quantity, x.requested_date, x.stock_total,
                                     x.inbound_date, x.partial_allowed) for x in CASES}), 7)

    def test_capture_is_model_blind_and_requires_matching_evidence(self):
        state, baseline = observation()
        captured = capture_trial("B01", state, baseline,
                                 provider="offline_double", model="scripted",
                                 prompt_version="none")
        self.assertEqual(captured["tool_calls"], 1)
        self.assertEqual(captured["raw_rejected_claims"], state["ai_claim_audit"])
        self.assertEqual(captured["reviewer_semantic_error_status"], "requires_human_review")
        self.assertNotIn("answer", str(captured).lower())
        self.assertTrue(structural_flags(captured)["requires_semantic_review"])
        self.assertIsNone(structural_flags(captured)["candidate_citations_returned"])
        self.assertEqual(captured["validated_contribution"]["kind"], "abstention")
        with self.assertRaises(EvidenceMismatch):
            capture_trial("B01", state, {**baseline, "bundle_sha256": "wrong"},
                          provider="offline_double", model="scripted", prompt_version="none")
        with self.assertRaises(ValueError):
            capture_trial("B01", {**state, "reviewer_package": {}}, baseline,
                          provider="offline_double", model="scripted", prompt_version="none")
        with self.assertRaises(EvidenceMismatch):
            capture_trial("B01", {**state, "reviewer_package": {"original": {"deal_id": "OTHER"}}},
                          baseline, provider="offline_double", model="scripted",
                          prompt_version="none")

    def test_capture_retains_failed_model_and_candidate_rejection(self):
        state, baseline = observation()
        state["ai_fulfillment_result"] = {"execution": "error", "error": "malformed_contribution"}
        state["candidate_records"] = {"C": {"candidate_id": "C", "status": "fixed_rejected",
            "proposed_slices": [], "error": "ValueError"}}
        state["model_attempt_ledger"] = [
            {"attempt_id": "one", "status": "reserved", "provider": "groq", "model": "m"},
            {"attempt_id": "one", "status": "error", "provider": "groq", "model": "m",
             "error_code": "timeout", "latency_ms": 1200, "usage": {}}]
        captured = capture_trial("B01", state, baseline, provider="offline_double",
                                 model="scripted", prompt_version="none")
        self.assertEqual(captured["ai_error"], "malformed_contribution")
        self.assertEqual(captured["candidates"][0]["status"], "fixed_rejected")
        self.assertEqual(captured["model_attempts"][0]["error_code"], "timeout")
        self.assertFalse(structural_flags(captured)["fixed_supported_candidate"])

    def test_scoring_never_infers_quality_or_acceptance_from_json(self):
        state, baseline = observation()
        captured = capture_trial("B01", state, baseline, provider="offline_double",
                                 model="scripted", prompt_version="none")
        answer = {"case_id": "B01", "bundle_sha256": "H", "source_input_digest": "S",
                  "review_status": "developer_provisional"}
        scored = adjudicate(captured, answer, reviewer_id="engineering")
        self.assertEqual(scored["business_correctness"], "requires_reviewer_judgment")
        self.assertEqual(scored["answer_status"], "developer_provisional")
        with self.assertRaises(ValueError):
            adjudicate(captured, {**answer, "review_status": "developer_supervisor_accepted"},
                       reviewer_id="engineering")
        accepted = adjudicate(captured, {**answer,
            "review_status": "developer_supervisor_accepted",
            "acceptance_record": {"reviewer_id": "test_reviewer", "reviewed_at": "TEST-DATE",
                                  "source_check": "synthetic test metadata"}},
            reviewer_id="test_reviewer")
        self.assertEqual(accepted["answer_status"], "developer_supervisor_accepted")
        with self.assertRaises(ValueError):
            adjudicate(captured, answer, reviewer_id="engineering", judgment={})
        trial = adjudicate(captured, {**answer,
            "review_status": "developer_supervisor_accepted",
            "acceptance_record": {"reviewer_id": "test_reviewer", "reviewed_at": "TEST-DATE",
                                  "source_check": "synthetic test metadata"}},
            reviewer_id="test_reviewer", judgment={
                "business_correctness": "uncertain", "usefulness_vs_baseline": "equivalent",
                "raw_critical_failures": ["unsupported_claim"],
                "surviving_critical_failures": [],
                "rationale": "Synthetic judgment example; no model-quality observation"})
        self.assertEqual(trial["raw_critical_failures"], ["unsupported_claim"])
        self.assertEqual(trial["surviving_critical_failures"], [])
        with self.assertRaises(ValueError):
            adjudicate(captured, {**answer, "review_status": "independent_accepted",
                "acceptance_record": {"reviewer_id": "test_reviewer", "reviewed_at": "TEST-DATE",
                                      "source_check": "synthetic test metadata"}},
                reviewer_id="test_reviewer")
        with self.assertRaises(EvidenceMismatch):
            adjudicate(captured, {**answer, "source_input_digest": "wrong"},
                       reviewer_id="engineering")

    def test_structural_comparison_cannot_claim_added_value(self):
        state, baseline = observation()
        state["candidate_records"] = {"C": {"candidate_id": "C", "status": "fixed_checked",
            "fixed_supply_status": "supply_supported_unreserved", "fixed_business_status": "needs_revision",
            "proposed_slices": [{"quantity": "8", "delivery_date": "2026-09-04"},
                                {"quantity": "2", "delivery_date": "2026-09-08"}]}}
        captured = capture_trial("B01", state, baseline, provider="offline_double",
                                 model="scripted", prompt_version="none")
        flags = structural_flags(captured)
        self.assertTrue(flags["same_schedule_as_baseline"])
        self.assertTrue(flags["distinct_value_not_established"])
        self.assertFalse(flags["requires_semantic_review"] is False)

    def test_live_pilot_rejects_unauthorized_cases_and_trial_counts_before_network(self):
        self.assertEqual(set(SOURCES), {"B01", "B05"})
        for case_id, trial in (("B02", 1), ("B01", 3), ("N01", 1)):
            with self.subTest(case_id=case_id, trial=trial), self.assertRaises(ValueError):
                run_one(case_id, trial, Path("benchmarks/results/unused.json"))


@unittest.skipUnless(DB_READY, "Requires exact separate Phase 1C and disposable PostgreSQL")
class PinnedEvaluationCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        with cls.connect() as conn:
            existing = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals WHERE "
                                    "deal_id='D-stock_then_confirmed_receipt')").fetchone()[0]
            if not existing:
                raise RuntimeError("Pinned reference fixture missing")
        install_disposable_cases(cls.connect())

    @staticmethod
    def connect():
        return psycopg.connect(os.environ["DATABASE_URL"])

    def test_all_disposable_sources_are_isolated_and_baseline_reproducible(self):
        hashes = set()
        for case in CASES:
            with self.subTest(case=case.case_id):
                pinned = self.adapter.read_original(self.connect, case.run_id,
                                                     "M18-" + case.case_id)
                pool = self.adapter.validate_pinned_context(pinned)
                self.assertEqual(pool["deal"]["deal_id"], case.ids()["D"])
                self.assertEqual(pool["lines"][0]["product_id"], case.ids()["P"])
                self.assertNotIn(pinned.context.bundle_sha256, hashes)
                hashes.add(pinned.context.bundle_sha256)
                baseline = pinned_baseline(self.adapter, self.connect, pinned)
                self.assertEqual(baseline, pinned_baseline(self.adapter, self.connect, pinned))
                self.assertEqual(baseline["source_input_digest"], pinned.context.source_input_digest)
                print("M1.8 source/baseline", case.case_id,
                      "bundle_sha256=" + pinned.context.bundle_sha256,
                      "source_input_digest=" + pinned.context.source_input_digest,
                      "discovered=" + str(baseline["discovered"]),
                      "slices=" + str(baseline["candidate"]["slices"] if
                                      baseline["candidate"] else []),
                      "verification=" + str(baseline["verification"]),
                      "original=" + str(baseline["original"]),
                      "reason=" + baseline["reason"])
                if case.case_id.startswith("B"):
                    self.assertTrue(baseline["discovered"], baseline)
                    self.assertEqual(baseline["verification"]["supply_status"],
                                     "supply_supported_unreserved", baseline)
                    self.assertEqual(baseline["verification"]["business_status"],
                                     "needs_revision", baseline)
                    self.assertEqual(sum(int(s["quantity"]) for s in
                                         baseline["candidate"]["slices"]), case.quantity)
                    self.assertTrue(all(set(s["evidence_ids"]) <=
                                        {case.ids()["INV"], case.ids()["IN"]} for s in
                                        baseline["candidate"]["slices"]))
                else:
                    self.assertFalse(baseline["discovered"], baseline)
                    self.assertIsNone(baseline["verification"])

    def test_reader_unchanged_and_wrong_source_context_rejected(self):
        case = CASES[0]
        pinned = self.adapter.read_original(self.connect, case.run_id, "M18-ISOLATION")
        baseline = pinned_baseline(self.adapter, self.connect, pinned)
        self.assertEqual(baseline["deal_id"], case.ids()["D"])
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM deal_desk.agent_execution_log "
                                          "WHERE run_id=%s", (case.run_id,)).fetchone()[0], 0)
        other = self.adapter.read_original(self.connect, CASES[1].run_id, "M18-OTHER")
        with self.assertRaises(EvidenceMismatch):
            capture_trial(case.case_id, {"assessment_id": "A", "phase1c_run_id": str(case.run_id),
                "context": {"assessment_id": "A", "phase1c_run_id": str(case.run_id),
                            "original_deal_id": case.ids()["D"],
                            "bundle_sha256": other.context.bundle_sha256,
                            "source_input_digest": other.context.source_input_digest},
                "reviewer_package": {"original": {"deal_id": case.ids()["D"]}}},
                baseline, provider="offline_double", model="scripted", prompt_version="none")

    def test_exploratory_early_dates_are_assessed_by_pinned_verifier(self):
        # Post-pilot diagnostic: normalize only the rejected decimal syntax to
        # whole units. This is not a model success or an accepted AI candidate.
        for case_id, early, first, later, late in (
                ("B01", "2026-09-03", 8, 2, "2026-09-08"),
                ("B05", "2026-09-02", 11, 7, "2026-09-11")):
            with self.subTest(case=case_id):
                case = next(c for c in CASES if c.case_id == case_id)
                pinned = self.adapter.read_original(self.connect, case.run_id,
                                                    "M18-DATE-DIAGNOSTIC-" + case_id)
                proposal = {"version": CANDIDATE_VERSION, "line_id": case.ids()["L"],
                    "delivery_slices": [
                        {"quantity": str(first), "delivery_date": early,
                         "source_refs": ["inventory:" + case.ids()["INV"]]},
                        {"quantity": str(later), "delivery_date": late,
                         "source_refs": ["inbound_supply:" + case.ids()["IN"]]}],
                    "tradeoff_code": TRADEOFF, "verification": "unverified"}
                candidate, _ = construct_candidate(self.adapter, pinned, proposal)
                try:
                    checked, decision = self.adapter.verify_candidate(self.connect, pinned,
                                                                      candidate)
                except ValueError as exc:
                    print("M1.8 exploratory early date", case_id, "rejected", type(exc).__name__)
                else:
                    print("M1.8 exploratory early date", case_id,
                          "supply_status=" + checked["candidate_trace"]["assessment"]["status"],
                          "business_status=" + decision["status"])
                    self.assertEqual(checked["candidate_trace"]["source_input_digest"],
                                     pinned.context.source_input_digest)
                reread = self.adapter.read_original(self.connect, case.run_id,
                                                    "M18-DATE-RECHECK-" + case_id)
                self.assertEqual(reread.context.bundle_sha256, pinned.context.bundle_sha256)

    def test_scripted_candidate_capture_is_not_ai_quality_evidence(self):
        case = CASES[0]
        pinned = self.adapter.read_original(self.connect, case.run_id, "M18-SCRIPTED")
        baseline = pinned_baseline(self.adapter, self.connect, pinned)
        self.assertTrue(baseline["discovered"])
        slices = baseline["candidate"]["slices"]
        raw = {"line_id": case.ids()["L"], "delivery_slices": [
            {"quantity": x["quantity"], "delivery_date": x["delivery_date"],
             "source_refs": [("inventory:" if source == case.ids()["INV"] else
                              "inbound_supply:") + source for source in x["evidence_ids"]]}
            for x in slices], "tradeoff_code": "partial_delivery_requires_customer_acceptance"}
        model = OfflineModelDouble((
            {"type": "tool", "tool": "inspect_fulfillment_paths",
             "arguments": {"line_id": case.ids()["L"]}},
            {"type": "contribution", "value": {"schema_version": "3",
              "kind": "binding_proposal", "payload": raw}}))
        graph = build_original_graph(self.adapter, self.connect, InMemorySaver())
        config = {"configurable": {"thread_id": "M18-SCRIPTED-B01"}}
        state = run_original_investigate_and_review(graph, config, self.adapter, model,
            assessment_id="M18-SCRIPTED", run_id=case.run_id)
        captured = capture_trial(case.case_id, state, baseline,
            provider="offline_double", model="scripted", prompt_version="none")
        flags = structural_flags(captured)
        self.assertTrue(flags["fixed_supported_candidate"], captured)
        self.assertTrue(flags["same_schedule_as_baseline"])
        self.assertTrue(flags["candidate_citations_returned"])
        self.assertEqual(captured["reviewer_package"]["candidates"][0]["customer_acceptance"],
                         "pending")
        self.assertEqual(captured["reviewer_package"]["original"]["deal_id"], case.ids()["D"])
        self.assertEqual(run_original_investigate_and_review(graph, config, self.adapter,
            OfflineModelDouble(()), assessment_id="M18-SCRIPTED", run_id=case.run_id), state)

    @unittest.skipUnless(os.getenv("CHECKPOINT_DATABASE_URL"),
                         "Requires disposable PostgreSQL checkpoint database")
    def test_observation_is_stable_across_postgres_candidate_restart(self):
        case = CASES[0]
        pinned = self.adapter.read_original(self.connect, case.run_id, "M18-RESTART")
        baseline = pinned_baseline(self.adapter, self.connect, pinned)
        slices = baseline["candidate"]["slices"]
        proposal = {"line_id": case.ids()["L"], "delivery_slices": [
            {"quantity": x["quantity"], "delivery_date": x["delivery_date"],
             "source_refs": [("inventory:" if source == case.ids()["INV"] else
                              "inbound_supply:") + source for source in x["evidence_ids"]]}
            for x in slices], "tradeoff_code": "partial_delivery_requires_customer_acceptance"}
        model = OfflineModelDouble((
            {"type": "tool", "tool": "inspect_fulfillment_paths",
             "arguments": {"line_id": case.ids()["L"]}},
            {"type": "contribution", "value": {"schema_version": "3",
             "kind": "binding_proposal", "payload": proposal}}))
        config = {"configurable": {"thread_id": "M18-RESTART-B01"}}
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver,
                                         interrupt_after=("candidate_construct",))
            from dealdesk_phase2.investigation_graph import run_original_then_investigate
            run_original_then_investigate(graph, config, self.adapter, model,
                assessment_id="M18-RESTART", run_id=case.run_id)
            self.assertEqual(graph.get_state(config).next, ("candidate_construct",))
            graph.invoke(None, config)
            self.assertEqual(graph.get_state(config).next, ("candidate_verify",))
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            state = run_original_investigate_and_review(graph, config, self.adapter,
                OfflineModelDouble(()), assessment_id="M18-RESTART", run_id=case.run_id)
            first = capture_trial(case.case_id, state, baseline, provider="offline_double",
                                  model="scripted", prompt_version="none")
            repeated = run_original_investigate_and_review(graph, config, self.adapter,
                OfflineModelDouble(()), assessment_id="M18-RESTART", run_id=case.run_id)
            second = capture_trial(case.case_id, repeated, baseline,
                                   provider="offline_double", model="scripted", prompt_version="none")
            self.assertEqual(first, second)
            self.assertEqual(state["trace"].count("candidate_fixed_checked:supply_supported_unreserved"), 1)
            self.assertEqual(first["tool_calls"], 1)


if __name__ == "__main__":
    unittest.main()
