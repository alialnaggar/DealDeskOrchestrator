"""Actual pinned Phase 1C path-shape proof; no model or provider request."""

import os
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.fulfillment_tools import FulfillmentTools
from dealdesk_phase2.hybrid_contracts import strict_binding, verified_source_slices
from dealdesk_phase2.hybrid_pack import prepare_pack
from dealdesk_phase2.hybrid_offline import run_hybrid_offline
from dealdesk_phase2.hybrid_evaluation import capture_hybrid, summarize_hybrid
from dealdesk_phase2.hybrid_contracts import ACTION_VERSION
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter, EvidenceMismatch
from dealdesk_phase2.tool_ledger import entries
from dealdesk_phase2.tool_permissions import TrustedToolScope
from m18_case_setup import CASES

try:
    import psycopg
except ImportError:
    psycopg = None


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "DATABASE_URL", "CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Pinned PostgreSQL fixture and checkpoint required")
class PinnedHybridEvidenceTests(unittest.TestCase):
    def test_adverse_case_abstention_and_fixed_gate_exclusion(self):
        from test_hybrid_offline import Scripted
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(os.environ["DATABASE_URL"])
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                for name in ("B05", "N01"):
                    case = next(x for x in CASES if x.case_id == name)
                    assessment = "HYBRID-ADVERSE-" + name
                    line = case.ids()["L"]
                    model = Scripted([{"version": ACTION_VERSION, "kind": "inspect",
                        "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": line},
                        "purpose_code": "check_dated_path"},
                        {"version": ACTION_VERSION, "kind": "abstain"}],
                        {"version": ACTION_VERSION, "kind": "abstain", "payload": {
                            "reason_code": "model_uncertainty", "scope": line,
                            "missing_evidence": []}})
                    config = {"configurable": {"thread_id": assessment}}
                    state = run_hybrid_offline(graph, config, adapter, connect, model,
                        assessment_id=assessment, run_id=case.run_id,
                        reservation_dir=Path(directory))
                    self.assertEqual(state["candidate_records"], {})
                    self.assertEqual(state["candidate_status"], "not_started")
                    self.assertEqual(state["reviewer_package"]["ai_contribution"], "abstention")
                    self.assertEqual(capture_hybrid(state)["contribution_kind"], "abstention")
                    self.assertEqual(capture_hybrid(graph.get_state(config).values),
                                     capture_hybrid(state))
                excluded = next(x for x in CASES if x.case_id == "N02")
                assessment = "HYBRID-EXCLUDED-N02"
                config = {"configurable": {"thread_id": assessment}}
                graph.invoke(initial_state(assessment, excluded.run_id), config)
                with self.assertRaisesRegex(ValueError, "ineligible"):
                    run_hybrid_offline(graph, config, adapter, connect,
                        Scripted([], {}), assessment_id=assessment, run_id=excluded.run_id,
                        reservation_dir=Path(directory))
                self.assertNotIn("hybrid_execution", graph.get_state(config).values)

    def test_mocked_hosted_b01_budget_receipts_raw_and_reviewer_handoff(self):
        from test_hybrid_provider import wire_call, wire_final
        from dealdesk_phase2.hybrid_offline import run_hybrid_evaluation
        from dealdesk_phase2.hybrid_provider import GroqHybridTransportModel
        from dealdesk_phase2.hybrid_send_reservation import attempt_path, verify_receipt

        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(os.environ["DATABASE_URL"])
        responses = [wire_call("inspect_fulfillment_paths", {"line_id": ids["L"],
                     "purpose_code": "check_dated_path"}),
                     wire_call("submit_proposal", {"submission_kind": "binding_partial_delivery"}),
                     wire_final("submit_proposal", {"line_id": ids["L"],
                         "tradeoff_code": "partial_delivery_requires_customer_acceptance",
                         "delivery_slices": [
                             {"quantity": "8", "delivery_date": "2026-09-04",
                              "source_refs": ["inventory:" + ids["INV"]]},
                             {"quantity": "2", "delivery_date": "2026-09-08",
                              "source_refs": ["inbound_supply:" + ids["IN"]]}]})]
        for response, count in zip(responses, (72, 45, 140)):
            response["usage"] = {"completion_tokens": count, "prompt_tokens": 300}
        model = GroqHybridTransportModel()
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                assessment = "HYBRID-B01-HOSTED-TRANSPORT-MOCK"
                config = {"configurable": {"thread_id": assessment}}
                with patch.dict(os.environ, {"GROQ_API_KEY": "offline-test-only"}), patch(
                        "dealdesk_phase2.live_models._post", side_effect=responses) as transport:
                    state = run_hybrid_evaluation(graph, config, adapter, connect, model,
                        assessment_id=assessment, run_id=case.run_id,
                        reservation_dir=Path(directory), authorized=True)
                    self.assertEqual(transport.call_count, 3)
                record = state["hybrid_execution"]
                self.assertEqual(record["phase"], "terminal")
                self.assertEqual(state["candidate_status"], "fixed_checked")
                self.assertEqual(len(next(iter(state["candidate_records"].values()))[
                    "specialist_results"]), 6)
                self.assertEqual(state["reviewer_package"]["candidates"][0][
                    "customer_acceptance"], "pending")
                self.assertEqual([x["raw"] for x in record["attempts"]], responses)
                self.assertEqual([x["max_completion_tokens"] for x in record[
                    "attempts"]], [512, 512, 1024])
                for item in record["attempts"]:
                    receipt = attempt_path(Path(directory), assessment_id=assessment,
                        start_digest=record["start_sha256"], stage=item["stage"],
                        ordinal=item["ordinal"])
                    verify_receipt(receipt, start_digest=record["start_sha256"],
                        stage=item["stage"], ordinal=item["ordinal"],
                        request_digest=item["request_sha256"])
                self.assertEqual(len(model.requests), 3)
                self.assertLessEqual(max(len(json.dumps(body,
                    sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
                    for body in model.requests), 8192)
                captured = capture_hybrid(state)
                self.assertTrue(captured["fixed_checked_candidate"])
                self.assertEqual(captured["raw_citation_access"]["returned"], 2)
                self.assertEqual(captured["tokens"], {"prompt": 900, "completion": 257})
                self.assertEqual(captured["model_selected_evidence_tools"], 1)
                self.assertEqual(summarize_hybrid([captured])["attempted_cases"], 1)
                reread = graph.get_state(config).values
                self.assertEqual(capture_hybrid(reread), captured)
                with self.assertRaises(EvidenceMismatch):
                    capture_hybrid(reread, baseline={"run_id": "wrong"})

    def test_groq_wire_double_b01_full_handoff_without_hosted_call(self):
        from test_hybrid_provider import wire_call, wire_final
        from dealdesk_phase2.hybrid_provider import OfflineGroqWireDouble
        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        final_response = wire_final("submit_proposal", {"line_id": ids["L"],
            "tradeoff_code": "partial_delivery_requires_customer_acceptance",
            "delivery_slices": [{"quantity": "8", "delivery_date": "2026-09-04",
                "source_refs": ["inventory:" + ids["INV"]]},
                {"quantity": "2", "delivery_date": "2026-09-08",
                 "source_refs": ["inbound_supply:" + ids["IN"]]}]})
        double = OfflineGroqWireDouble([
            wire_call("inspect_fulfillment_paths", {"line_id": ids["L"],
                  "purpose_code": "check_dated_path"}),
            wire_call("submit_proposal", {"submission_kind": "binding_partial_delivery"}),
            final_response])
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                assessment = "HYBRID-B01-GROQ-WIRE-OFFLINE"
                state = run_hybrid_offline(graph, {"configurable": {"thread_id": assessment}},
                    adapter, connect, double, assessment_id=assessment, run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(state["candidate_status"], "fixed_checked")
                self.assertEqual(len(state["reviewer_package"]["candidates"]), 1)
                self.assertEqual(len(double.requests), 3)
                self.assertNotIn("tools", double.requests[-1])
                self.assertEqual(state["hybrid_execution"]["attempts"][-1]["raw"],
                                 final_response)

    def test_candidate_graph_interruption_resumes_without_model_retransmit(self):
        from test_hybrid_offline import Scripted
        from dealdesk_phase2.hybrid_contracts import HybridContractError
        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        model = Scripted([{"version": ACTION_VERSION, "kind": "inspect",
            "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": ids["L"]},
            "purpose_code": "check_dated_path"},
            {"version": ACTION_VERSION, "kind": "submit_proposal",
             "submission_kind": "binding_partial_delivery"}],
            {"version": ACTION_VERSION, "kind": "submit_proposal", "payload": {
                "line_id": ids["L"],
                "tradeoff_code": "partial_delivery_requires_customer_acceptance",
                "delivery_slices": [
                    {"quantity": "8", "delivery_date": "2026-09-04",
                     "source_refs": ["inventory:" + ids["INV"]]},
                    {"quantity": "2", "delivery_date": "2026-09-08",
                     "source_refs": ["inbound_supply:" + ids["IN"]]}]}})
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver,
                                             interrupt_after=("candidate_verify",))
                assessment = "HYBRID-B01-CANDIDATE-RESTART"
                config = {"configurable": {"thread_id": assessment}}

                def run():
                    return run_hybrid_offline(graph, config, adapter, connect, model,
                        assessment_id=assessment, run_id=case.run_id,
                        reservation_dir=Path(directory))

                with self.assertRaisesRegex(HybridContractError, "candidate_checkpoint_not_complete"):
                    run()
                self.assertEqual(graph.get_state(config).values["hybrid_execution"]["phase"],
                                 "handoff")
                state = run()
                self.assertEqual(state["candidate_status"], "fixed_checked")
                self.assertEqual(len(next(iter(state["candidate_records"].values()))[
                    "specialist_results"]), 6)
                self.assertEqual((model.decisions, model.finals), (2, 1))

    def test_d4_new_model_proposal_revalidated_by_pinned_and_reviewer(self):
        from test_hybrid_offline import Scripted
        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        inspect = {"version": ACTION_VERSION, "kind": "inspect",
                   "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": ids["L"]},
                   "purpose_code": "check_dated_path"}
        intent = {"version": ACTION_VERSION, "kind": "submit_proposal",
                  "submission_kind": "binding_partial_delivery"}
        missing_field = {"version": ACTION_VERSION, "kind": "submit_proposal", "payload": {
            "line_id": ids["L"], "delivery_slices": [
                {"quantity": "8", "delivery_date": "2026-09-03",
                 "source_refs": ["inventory:" + ids["INV"]]},
                {"quantity": "2", "delivery_date": "2026-09-08",
                 "source_refs": ["inbound_supply:" + ids["IN"]]}]}}
        corrected = {"version": ACTION_VERSION, "kind": "submit_proposal", "payload": {
            **missing_field["payload"],
            "tradeoff_code": "partial_delivery_requires_customer_acceptance",
            "delivery_slices": [
                {**missing_field["payload"]["delivery_slices"][0],
                 "delivery_date": "2026-09-04"},
                missing_field["payload"]["delivery_slices"][1]]}}
        model = Scripted([inspect, intent], missing_field, revision=corrected)
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                state = run_hybrid_offline(graph, {"configurable": {"thread_id":
                    "HYBRID-B01-D4-NEW-PROPOSAL"}}, adapter, connect, model,
                    assessment_id="HYBRID-B01-D4-NEW-PROPOSAL", run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(state["hybrid_execution"]["feedback"]["constraint_code"],
                                 "required_field_missing")
                self.assertEqual(state["hybrid_execution"]["attempts"][-1]["raw"], corrected)
                self.assertEqual(state["candidate_status"], "fixed_checked")
                self.assertEqual(len(next(iter(state["candidate_records"].values()))[
                    "specialist_results"]), 6)
                self.assertEqual(state["reviewer_package"]["candidates"][0][
                    "customer_acceptance"], "pending")

    def test_d4_model_authored_abstention_and_unsupported_binding_exclusion(self):
        from test_hybrid_offline import Scripted
        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        inspect = {"version": ACTION_VERSION, "kind": "inspect",
                   "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": ids["L"]},
                   "purpose_code": "check_dated_path"}
        intent = {"version": ACTION_VERSION, "kind": "submit_proposal",
                  "submission_kind": "binding_partial_delivery"}
        stock, inbound = "inventory:" + ids["INV"], "inbound_supply:" + ids["IN"]
        raw = {"version": ACTION_VERSION, "kind": "submit_proposal", "payload": {
            "line_id": ids["L"], "tradeoff_code": "partial_delivery_requires_customer_acceptance",
            "delivery_slices": [{"quantity": "08", "delivery_date": "2026-09-03",
                                 "source_refs": [stock]},
                                {"quantity": "2", "delivery_date": "2026-09-08",
                                 "source_refs": [inbound]}]}}

        class RevisionModel(Scripted):
            def revision_intent(self, feedback, input, observations):
                self.feedback = feedback
                return {"version": ACTION_VERSION, "kind": "abstain"}

            def revise(self, intent, feedback, input, observations):
                self.revisions = getattr(self, "revisions", 0) + 1
                return {"version": ACTION_VERSION, "kind": "abstain", "payload": {
                    "reason_code": "model_uncertainty", "scope": ids["L"],
                    "missing_evidence": []}}

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                model = RevisionModel([inspect, intent], raw)
                state = run_hybrid_offline(graph, {"configurable": {"thread_id":
                    "HYBRID-B01-D4-ABSTAIN"}}, adapter, connect, model,
                    assessment_id="HYBRID-B01-D4-ABSTAIN", run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(model.feedback["constraint_code"], "quantity_format")
                self.assertEqual(model.revisions, 1)
                self.assertEqual(state["candidate_records"], {})
                self.assertEqual(state["ai_fulfillment_result"]["contribution"]["kind"],
                                 "abstention")
                self.assertEqual(state["hybrid_execution"]["rejections"][0]["raw"], raw)
                self.assertEqual([x["stage"] for x in state["hybrid_execution"]["attempts"]],
                                 ["decision", "decision", "final", "revision_intent", "revision"])

                bad = {**raw, "payload": {**raw["payload"], "delivery_slices": [
                    {**raw["payload"]["delivery_slices"][0], "source_refs": [inbound]},
                    raw["payload"]["delivery_slices"][1]]}}
                blocked = RevisionModel([inspect, intent], bad)
                state = run_hybrid_offline(graph, {"configurable": {"thread_id":
                    "HYBRID-B01-D4-BAD-BINDING"}}, adapter, connect, blocked,
                    assessment_id="HYBRID-B01-D4-BAD-BINDING", run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(state["investigation_status"], "error")
                self.assertEqual(state["candidate_records"], {})
                self.assertEqual(len(state["hybrid_execution"]["attempts"]), 3)
                self.assertFalse(hasattr(blocked, "feedback"))

    def test_offline_model_selected_b01_candidate_and_six_specialist_review(self):
        from test_hybrid_offline import Scripted
        case = next(x for x in CASES if x.case_id == "B01")
        ids = case.ids()
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        action = {"version": ACTION_VERSION, "kind": "inspect",
                  "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": ids["L"]},
                  "purpose_code": "check_dated_path"}
        intent = {"version": ACTION_VERSION, "kind": "submit_proposal",
                  "submission_kind": "binding_partial_delivery"}
        raw = {"version": ACTION_VERSION, "kind": "submit_proposal", "payload": {
            "line_id": ids["L"], "tradeoff_code": "partial_delivery_requires_customer_acceptance",
            "delivery_slices": [{"quantity": "8", "delivery_date": "2026-09-04",
                                 "source_refs": ["inventory:" + ids["INV"]]},
                                {"quantity": "2", "delivery_date": "2026-09-08",
                                 "source_refs": ["inbound_supply:" + ids["IN"]]}]}}
        model = Scripted([action, intent], raw)
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as directory:
            with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(adapter, connect, saver)
                assessment_id = "HYBRID-PINNED-B01-OFFLINE"
                config = {"configurable": {"thread_id": assessment_id}}
                state = run_hybrid_offline(graph, config, adapter, connect, model,
                    assessment_id=assessment_id, run_id=case.run_id,
                    reservation_dir=Path(directory))
                self.assertEqual(state["investigation_status"], "completed")
                self.assertEqual(state["candidate_status"], "fixed_checked")
                record = next(iter(state["candidate_records"].values()))
                self.assertEqual(record["fixed_supply_status"], "supply_supported_unreserved")
                self.assertEqual(len(record["specialist_results"]), 6)
                self.assertEqual(len(state["specialist_results"]), 6)
                review = state["reviewer_package"]
                self.assertEqual(review["candidates"][0]["verification_outcome"],
                                 "binding_supply_supported_unreserved")
                self.assertEqual(review["candidates"][0]["customer_acceptance"], "pending")
                self.assertEqual([x["stage"] for x in state["hybrid_execution"]["attempts"]],
                                 ["decision", "decision", "final"])
                self.assertEqual(sum(bool(x.get("counted")) for x in state[
                    "tool_access_ledger"]), 2)
                self.assertEqual(model.finals, 1)
                captured = capture_hybrid(state)
                self.assertTrue(captured["fixed_checked_candidate"])
                self.assertEqual(captured["attempt_stages"], ["decision", "decision", "final"])
                self.assertIsNone(captured["tokens"])
                self.assertEqual(captured["raw_citation_access"], None)

    def test_model_selected_path_required_and_pinned_option_cites_exact_slice(self):
        case = next(x for x in CASES if x.case_id == "B01")
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))

        def connect():
            return psycopg.connect(os.environ["DATABASE_URL"])

        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(adapter, connect, saver)
            assessment_id = "HYBRID-PINNED-B01"
            config = {"configurable": {"thread_id": assessment_id}}
            graph.invoke(initial_state(assessment_id, case.run_id), config)
            pack, input = prepare_pack(graph, config, adapter, provider="offline_double",
                                       model="scripted", policy_version="hybrid-offline-v1")
            self.assertNotIn("binding_options", str(pack))
            ids = case.ids()
            raw = {"line_id": ids["L"], "tradeoff_code":
                "partial_delivery_requires_customer_acceptance", "delivery_slices": [
                    {"quantity": "8", "delivery_date": "2026-09-04",
                     "source_refs": ["inventory:" + ids["INV"]]},
                    {"quantity": "2", "delivery_date": "2026-09-08",
                     "source_refs": ["inbound_supply:" + ids["IN"]]}]}
            before = entries(graph, config, input.assessment_id, input.bundle_sha256)
            with self.assertRaises(ValueError):
                strict_binding(raw, input, before)  # no model-selected dated path
            from dealdesk_phase2.graph_state import pinned_from_state
            pinned = pinned_from_state(graph.get_state(config).values)
            pool = adapter.validate_pinned_context(pinned)
            scope = TrustedToolScope(pinned.context, "fulfillment", input.subject_id,
                pool["deal"]["customer_id"], frozenset((input.line_id,)),
                frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane")))
            path = FulfillmentTools(graph, config, adapter, scope).inspect_fulfillment_paths(
                call_id="hybrid-b01-model-selected-path", line_id=input.line_id)
            self.assertEqual(path["evidence"], "eligible_binding")
            from dealdesk_phase2.candidate_contract import construct_candidate
            trusted = strict_binding(raw, input, entries(
                graph, config, input.assessment_id, input.bundle_sha256))
            self.assertEqual(trusted["verification"], "unverified")
            candidate, _ = construct_candidate(adapter, pinned, trusted)
            checked, decision = adapter.verify_candidate(connect, pinned, candidate)
            self.assertEqual(decision["status"], "needs_revision")
            verified_source_slices(raw, checked)
            wrong = {**raw, "delivery_slices": [
                {**raw["delivery_slices"][0], "source_refs": ["inbound_supply:" + ids["IN"]]},
                raw["delivery_slices"][1]]}
            wrong_trusted = strict_binding(wrong, input, entries(
                graph, config, input.assessment_id, input.bundle_sha256))
            wrong_candidate, _ = construct_candidate(adapter, pinned, wrong_trusted)
            with self.assertRaises(ValueError):
                adapter.verify_candidate(connect, pinned, wrong_candidate)
            with self.assertRaisesRegex(EvidenceMismatch, "fixed_source_to_slice_unproven"):
                verified_source_slices(wrong, checked)
            state = graph.get_state(config).values
            self.assertEqual(state["candidate_status"], "not_started")
            self.assertEqual(state["review_status"], "needs_revision")
            self.assertEqual(sum(bool(x.get("counted")) for x in state["tool_access_ledger"]), 2)
