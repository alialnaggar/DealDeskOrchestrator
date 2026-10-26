"""Offline-only hybrid handoff, intent boundary, crash and owner races."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.hybrid_contracts import ACTION_VERSION, HybridContractError
from dealdesk_phase2.hybrid_offline import run_hybrid_offline
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_investigation_graph import InvestigationAdapter, RUN


class Scripted:
    provider = "offline_double"
    offline_only = True
    model = "offline-script-v1"

    def __init__(self, actions, response, revision=None):
        self.actions, self.response, self.revision = actions, response, revision
        self.decisions = 0
        self.finals = 0

    def decide(self, input, observations):
        self.decisions += 1
        return self.actions[self.decisions - 1]

    def submit(self, intent, input, observations):
        self.finals += 1
        return self.response

    def revision_intent(self, feedback, input, observations):
        return {"version": ACTION_VERSION, "kind": "submit_proposal",
                "submission_kind": "binding_partial_delivery"}

    def revise(self, intent, feedback, input, observations):
        return self.revision


def intent(kind="abstain"):
    return {"version": ACTION_VERSION, "kind": kind}


def abstain(line="L1"):
    return {"version": ACTION_VERSION, "kind": "abstain", "payload": {
        "scope": line, "reason_code": "model_uncertainty", "missing_evidence": []}}


class OfflineHybridTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.adapter = InvestigationAdapter()
        self.graph = build_original_graph(self.adapter, None, InMemorySaver())
        self.assessment_id = self.id()
        self.config = {"configurable": {"thread_id": self.assessment_id}}
        self.graph.invoke(initial_state(self.assessment_id, RUN), self.config)

    def run_model(self, model):
        return run_hybrid_offline(self.graph, self.config, self.adapter, None, model,
            assessment_id=self.assessment_id, run_id=RUN, reservation_dir=self.dir)

    def test_explicit_intent_final_and_original_only_review(self):
        model = Scripted([intent()], abstain())
        state = self.run_model(model)
        self.assertEqual((model.decisions, model.finals), (1, 1))
        self.assertEqual(state["investigation_status"], "completed")
        self.assertEqual(state["candidate_status"], "not_started")
        self.assertEqual(state["reviewer_package"]["candidates"], [])
        self.assertEqual(len(state["specialist_results"]), 6)
        self.assertEqual(sum(bool(x.get("counted")) for x in state["tool_access_ledger"]), 1)
        self.assertEqual([x["stage"] for x in state["hybrid_execution"]["attempts"]],
                         ["decision", "final"])
        self.assertEqual(self.run_model(model)["reviewer_package"], state["reviewer_package"])
        self.assertEqual((model.decisions, model.finals), (1, 1))

    def test_model_directed_inspection_and_mismatched_final_rejected(self):
        actions = [{"version": ACTION_VERSION, "kind": "inspect",
                    "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": "L1"},
                    "purpose_code": "check_dated_path"}, intent()]
        model = Scripted(actions, {**abstain(), "kind": "submit_finding"})
        state = self.run_model(model)
        self.assertEqual(state["investigation_status"], "error")
        self.assertEqual([x["stage"] for x in state["hybrid_execution"]["attempts"]],
                         ["decision", "decision", "final"])
        self.assertEqual(sum(bool(x.get("counted")) for x in state["tool_access_ledger"]), 2)
        self.assertEqual(state["candidate_records"], {})
        self.assertEqual(state["reviewer_package"]["candidates"], [])

    def test_interrupted_send_cannot_repeat_even_with_new_model(self):
        class Crashing(Scripted):
            def decide(self, input, observations):
                raise KeyboardInterrupt("unknown send state")

        with self.assertRaises(KeyboardInterrupt):
            self.run_model(Crashing([], abstain()))
        with self.assertRaisesRegex(HybridContractError, "hybrid_send_outcome_uncertain"):
            self.run_model(Scripted([intent()], abstain()))
        state = self.graph.get_state(self.config).values
        self.assertEqual(state["hybrid_execution"]["pending"]["stage"], "decision")
        self.assertEqual(state["investigation_status"], "not_started")

    def test_owner_claim_is_exclusive_across_competing_callers(self):
        entered, release = threading.Event(), threading.Event()

        class Blocking(Scripted):
            def decide(self, input, observations):
                entered.set()
                if not release.wait(5):
                    raise TimeoutError("test timed out")
                return intent()

        model = Blocking([intent()], abstain())
        with ThreadPoolExecutor(max_workers=2) as workers:
            first = workers.submit(self.run_model, model)
            self.assertTrue(entered.wait(5))
            with self.assertRaises((HybridContractError, FileExistsError)):
                self.run_model(Scripted([intent()], abstain()))
            release.set()
            self.assertEqual(first.result(timeout=5)["investigation_status"], "completed")
        self.assertEqual(model.decisions, 0)  # overridden method, only first thread sent

    def test_sender_not_exposed_as_offline_model(self):
        model = Scripted([intent()], abstain())
        model.provider = "groq"
        with self.assertRaisesRegex(HybridContractError, "offline_double_required"):
            self.run_model(model)
        self.assertNotIn("hybrid_investigation_start", self.graph.get_state(self.config).values)

    def test_completed_decision_and_final_resume_without_resend(self):
        import dealdesk_phase2.hybrid_offline as hybrid
        model = Scripted([intent()], abstain())
        actual = hybrid.decision
        tripped = False

        def interrupt_decision(*args, **kwargs):
            nonlocal tripped
            if not tripped:
                tripped = True
                raise KeyboardInterrupt("after saved decision")
            return actual(*args, **kwargs)

        with patch.object(hybrid, "decision", side_effect=interrupt_decision):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        state = self.graph.get_state(self.config).values
        self.assertEqual(state["hybrid_execution"]["attempts"][0]["stage"], "decision")
        self.assertEqual(self.run_model(model)["investigation_status"], "completed")
        self.assertEqual((model.decisions, model.finals), (1, 1))

        # Another assessment: final response saved but final parsing interrupted.
        self.setUp()
        second = Scripted([intent()], abstain())
        actual_final = hybrid.final
        tripped = False

        def interrupt_final(*args, **kwargs):
            nonlocal tripped
            if not tripped:
                tripped = True
                raise KeyboardInterrupt("after saved final")
            return actual_final(*args, **kwargs)

        with patch.object(hybrid, "final", side_effect=interrupt_final):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(second)
        self.assertEqual([x["stage"] for x in self.graph.get_state(self.config).values[
            "hybrid_execution"]["attempts"]], ["decision", "final"])
        self.assertEqual(self.run_model(second)["investigation_status"], "completed")
        self.assertEqual((second.decisions, second.finals), (1, 1))

    def test_saved_raw_with_reserved_only_receipt_cannot_replay(self):
        import json
        from dealdesk_phase2.hybrid_send_reservation import attempt_path
        import dealdesk_phase2.hybrid_offline as hybrid

        model = Scripted([intent()], abstain())
        with patch.object(hybrid, "decision", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        record = self.graph.get_state(self.config).values["hybrid_execution"]
        self.assertEqual(len(record["attempts"]), 1)
        path = attempt_path(self.dir, assessment_id=self.assessment_id,
                            start_digest=record["start_sha256"], stage="decision", ordinal=0)
        path.write_text(json.dumps(json.loads(path.read_text().splitlines()[0])) + "\n")
        with self.assertRaisesRegex(EvidenceMismatch, "Saved hybrid model result identity differs"):
            self.run_model(model)
        self.assertEqual((model.decisions, model.finals), (1, 0))

    def test_completed_tool_replay_does_not_repeat_read(self):
        import dealdesk_phase2.hybrid_offline as hybrid
        action = {"version": ACTION_VERSION, "kind": "inspect",
                  "tool_name": "inspect_fulfillment_paths", "arguments": {"line_id": "L1"},
                  "purpose_code": "check_dated_path"}
        model = Scripted([action, intent()], abstain())
        actual = hybrid._save
        interrupted = False

        def interrupt_after_tool(graph, config, record):
            nonlocal interrupted
            if (record.get("phase") == "decision" and record.get("decision_count") == 1
                    and not interrupted):
                interrupted = True
                raise KeyboardInterrupt("tool completed, observation not checkpointed")
            return actual(graph, config, record)

        with patch.object(hybrid, "_save", side_effect=interrupt_after_tool):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        state = self.graph.get_state(self.config).values
        self.assertEqual(sum(bool(x.get("counted")) for x in state["tool_access_ledger"]), 2)
        self.assertEqual(self.run_model(model)["investigation_status"], "completed")
        self.assertEqual(sum(bool(x.get("counted")) for x in self.graph.get_state(
            self.config).values["tool_access_ledger"]), 2)
        self.assertEqual((model.decisions, model.finals), (2, 1))

    def test_pending_without_claim_resumes_but_claim_without_saved_raw_is_uncertain(self):
        import dealdesk_phase2.hybrid_offline as hybrid
        model = Scripted([intent()], abstain())
        original = hybrid.claim_and_call
        tripped = False

        def interrupt_before_claim(*args, **kwargs):
            nonlocal tripped
            if not tripped and kwargs.get("stage") == "decision":
                tripped = True
                raise KeyboardInterrupt("no filesystem claim, provably unsent")
            return original(*args, **kwargs)

        with patch.object(hybrid, "claim_and_call", side_effect=interrupt_before_claim):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        self.assertEqual(model.decisions, 0)
        self.assertEqual(self.run_model(model)["investigation_status"], "completed")
        self.assertEqual(model.decisions, 1)

    def test_result_returned_but_checkpoint_failed_is_not_resent(self):
        import dealdesk_phase2.hybrid_offline as hybrid
        model = Scripted([intent()], abstain())
        actual = hybrid._save

        def interrupt_after_response(graph, config, record):
            if record.get("attempts") and not record.get("pending"):
                raise KeyboardInterrupt("model responded, checkpoint not durable")
            return actual(graph, config, record)

        with patch.object(hybrid, "_save", side_effect=interrupt_after_response):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        with self.assertRaisesRegex(HybridContractError, "hybrid_send_outcome_uncertain"):
            self.run_model(model)
        self.assertEqual((model.decisions, model.finals), (1, 0))

    def test_handoff_restart_uses_saved_result_only(self):
        model = Scripted([intent()], abstain())
        # Stop after the result is saved as handoff, before original AI update.
        original_update = self.graph.update_state
        tripped = False

        def interrupt_handoff(config, values, **kwargs):
            nonlocal tripped
            if "ai_fulfillment_result" in values and not tripped:
                tripped = True
                raise KeyboardInterrupt("handoff interrupted")
            return original_update(config, values, **kwargs)

        with patch.object(self.graph, "update_state", side_effect=interrupt_handoff):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        self.assertEqual(self.graph.get_state(self.config).values[
            "hybrid_execution"]["phase"], "handoff")
        self.assertEqual(self.run_model(model)["investigation_status"], "completed")
        self.assertEqual((model.decisions, model.finals), (1, 1))

    def test_recovery_requires_same_reservation_directory(self):
        model = Scripted([intent()], abstain())
        import dealdesk_phase2.hybrid_offline as hybrid
        with patch.object(hybrid, "decision", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as other:
            with self.assertRaisesRegex(Exception, "Hybrid restart identity differs"):
                run_hybrid_offline(self.graph, self.config, self.adapter, None, model,
                    assessment_id=self.assessment_id, run_id=RUN,
                    reservation_dir=Path(other))
        self.assertEqual(model.decisions, 1)

    def test_terminal_replay_rejects_changed_pack_without_new_send(self):
        model = Scripted([intent()], abstain())
        self.run_model(model)
        pack = self.graph.get_state(self.config).values["hybrid_evidence_pack"]
        self.graph.update_state(self.config, {"hybrid_evidence_pack": {
            **pack, "model_input": {**pack["model_input"], "requested_quantity": "999"}}},
            as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_model(model)
        self.assertEqual((model.decisions, model.finals), (1, 1))

    def test_crash_before_start_resumes_if_no_send_or_prefetch_was_reserved(self):
        model = Scripted([intent()], abstain())
        with patch("dealdesk_phase2.hybrid_offline.prepare_pack", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_model(model)
        state = run_hybrid_offline(self.graph, self.config, self.adapter, None, model,
                assessment_id=self.assessment_id, run_id=RUN, reservation_dir=self.dir,
                policy_version="different-policy")
        self.assertEqual(state["investigation_status"], "completed")
        self.assertEqual((model.decisions, model.finals), (1, 1))


if __name__ == "__main__":
    unittest.main()
