"""Offline-only Configuration correction: fresh PG checkpoint + durable mock receipt."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from dealdesk_phase2.hybrid_send_reservation import attempt_path
from dealdesk_phase2.m20_specialists import _inspect
from dealdesk_phase2.m4_configuration_correction import (
    BUDGET_VERSION, ScriptedConfigurationCorrection, run_configuration_correction_offline)
from dealdesk_phase2.m4_configuration_original_capture import (
    STAGE as ORIGINAL_STAGE, ScriptedOriginalFinal, capture_original_final_offline)
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh isolated PostgreSQL business and checkpoint databases required")
class ConfigurationCorrectionPostgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["M20_DATABASE_URL"]))
        with cls.connect() as conn:
            if not conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]:
                install_disposable_cases(conn)

    def setUp(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        self.saver_context = thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"])
        self.saver = self.saver_context.__enter__()
        self.graph = build_original_graph(self.adapter, self.connect, self.saver)
        self.tmp = TemporaryDirectory(prefix="m4-config-", dir="/tmp/opencode")
        self.owner = Path(self.tmp.name)
        self.owner.chmod(0o700)
        self.config = {"configurable": {"thread_id": "M4-CONFIG-" + uuid4().hex}}
        case = next(x for x in CASES if x.case_id == "B05")
        self.before = self.graph.invoke(initial_state(self.config["configurable"]["thread_id"],
                                                    case.run_id), self.config)
        self.assertEqual(self.before["specialist_results"]["configuration"]["execution"], "completed")
        line_id = "M18-L-B05"
        self.observation = _inspect(self.graph, self.config, self.adapter,
                                    "configuration", line_id, 0)
        product = next(x for x in self.observation["records"] if x["ref"].startswith("product:"))
        field = "is_sellable"
        self.raw = {"version": "terminal-final-v1", "kind": "finding", "claims": [{
            "ref": product["ref"], "field": field,
            "value_json": json.dumps(str(product["fields"][field]).lower())}],
            "uncertainty_reasons": [], "reason_code": "none"}
        self.corrected = {**self.raw, "claims": [{**self.raw["claims"][0],
            "value_json": json.dumps(product["fields"][field])}]}
        self.model = ScriptedConfigurationCorrection("m4-mock-v1", json.dumps(self.corrected))
        self.kw = {"rejected_content": json.dumps(self.raw), "line_id": line_id,
            "budget": {"version": BUDGET_VERSION, "maximum_correction_posts": 1,
                       "maximum_configured_completion_tokens": 512},
            "owner_dir": self.owner, "opt_in": True}

    def tearDown(self):
        self.tmp.cleanup()
        self.saver_context.__exit__(None, None, None)

    def run_correction(self, model=None, graph=None, **overrides):
        return run_configuration_correction_offline(graph or self.graph, self.config,
            self.adapter, model or self.model, **{**self.kw, **overrides})

    def reopen(self):
        return build_original_graph(self.adapter, self.connect, self.saver)

    def test_invalid_to_valid_retention_fixed_verification_and_restart(self):
        result = self.run_correction()
        self.assertEqual(result["validation"], "valid")
        self.assertEqual(result["validated_action"]["claims"][0]["value"],
            json.loads(self.corrected["claims"][0]["value_json"]))
        self.assertIsNone(result["usage"])
        self.assertIsNone(result["cost_usd"])
        self.assertGreaterEqual(result["elapsed_ms"], 0)
        state = self.graph.get_state(self.config).values
        protocol = state["m4_configuration_correction"]["protocol"]
        self.assertEqual(protocol["original"]["content"], self.kw["rejected_content"])
        self.assertEqual(protocol["original"]["validation_category"], "claim_binding")
        self.assertEqual(protocol["original"]["returned_field"], {
            "ref": self.raw["claims"][0]["ref"], "field": "is_sellable"})
        self.assertNotEqual(result["attempt_id"], protocol["original"]["attempt_id"])
        self.assertEqual(state["specialist_results"], self.before["specialist_results"])
        self.assertEqual(state["review_status"], self.before["review_status"])
        self.assertEqual(self.run_correction(graph=self.reopen()), result)
        self.assertEqual(self.model.calls, 1)

    def test_invalid_to_invalid_and_forged_corrected_citation(self):
        self.model.response = json.dumps(self.raw)
        result = self.run_correction()
        self.assertEqual(result["validation"], "invalid")
        self.assertIsNone(result["validated_action"])
        self.assertEqual(self.run_correction(graph=self.reopen()), result)
        self.model.response = json.dumps(self.corrected)
        self.assertEqual(self.run_correction(graph=self.reopen()), result)
        self.assertEqual(self.model.calls, 1)  # no second correction

    def test_forged_corrected_reference_never_becomes_valid(self):
        self.model.response = json.dumps({**self.corrected,
            "claims": [{**self.corrected["claims"][0], "ref": "product:FORGED"}]})
        result = self.run_correction()
        self.assertEqual(result["validation"], "invalid")
        self.assertIsNone(result["validated_action"])

    def test_ineligible_original_source_and_explicit_budget(self):
        for change in ({"budget": {**self.kw["budget"], "maximum_correction_posts": 0}},
                       {"budget": {**self.kw["budget"], "maximum_correction_posts": 2}},
                       {"opt_in": False}, {"line_id": "M18-L-B01"}):
            with self.subTest(change=change), self.assertRaises((ValueError, EvidenceMismatch)):
                self.run_correction(**change)
        forged = {**self.raw, "claims": [{**self.raw["claims"][0], "ref": "product:FORGED"}]}
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(rejected_content=json.dumps(forged))
        self.assertEqual(self.model.calls, 0)

    def test_transport_failure_and_uncertain_send_are_terminal(self):
        self.model.response = lambda _: (_ for _ in ()).throw(TimeoutError("offline failure"))
        with self.assertRaises(TimeoutError):
            self.run_correction()
        self.assertEqual([x["status"] for x in self.graph.get_state(self.config).values[
            "m4_configuration_correction"]["attempts"]], ["reserved", "uncertain"])
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(graph=self.reopen())
        self.assertEqual(self.graph.get_state(self.config).values[
            "m4_configuration_correction"]["attempts"][1]["status"], "uncertain")
        self.assertEqual(self.model.calls, 1)

    def test_missing_or_reserved_only_receipt_does_not_prove_return(self):
        self.run_correction()
        saved = self.graph.get_state(self.config).values["m4_configuration_correction"]
        path = attempt_path(self.owner, assessment_id=self.config["configurable"]["thread_id"],
            start_digest=saved["start_sha256"], stage="configuration_correction", ordinal=0)
        content = path.read_bytes()
        path.unlink()
        with self.assertRaises((EvidenceMismatch, FileNotFoundError)):
            self.run_correction(graph=self.reopen())
        path.write_bytes(content.splitlines(keepends=True)[0])
        path.chmod(0o600)
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(graph=self.reopen())
        self.assertEqual(self.model.calls, 1)

    def test_identity_response_and_checkpoint_tampering_fail_closed(self):
        result = self.run_correction()
        for changes in ({"rejected_content": json.dumps({**self.raw,
                "claims": [{**self.raw["claims"][0], "value_json": '"false"'}]})},
                {"model": ScriptedConfigurationCorrection("different-model", "")},
                {"budget": {**self.kw["budget"], "maximum_configured_completion_tokens": 1024}}):
            with self.subTest(changes=changes), self.assertRaises((ValueError, EvidenceMismatch)):
                model = changes.get("model", self.model)
                self.run_correction(model=model, **{k:v for k,v in changes.items() if k != "model"})
        saved = self.graph.get_state(self.config).values["m4_configuration_correction"]
        altered = {**saved, "attempts": [saved["attempts"][0],
            {**saved["attempts"][1], "original_attempt_id": "forged"}]}
        self.graph.update_state(self.config, {"m4_configuration_correction": altered}, as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(graph=self.reopen())
        self.assertEqual(result["validation"], "valid")
        self.assertEqual(self.model.calls, 1)

    def test_rewritten_response_even_with_updated_checkpoint_digest_fails_receipt(self):
        from hashlib import sha256
        self.run_correction()
        saved = self.graph.get_state(self.config).values["m4_configuration_correction"]
        forged = json.dumps({**self.corrected, "claims": [
            {**self.corrected["claims"][0], "field": "is_active", "value_json": "false"}]})
        altered = {**saved, "attempts": [saved["attempts"][0], {
            **saved["attempts"][1], "content": forged,
            "response_sha256": sha256(forged.encode()).hexdigest()}]}
        self.graph.update_state(self.config, {"m4_configuration_correction": altered}, as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(graph=self.reopen())
        self.assertEqual(self.model.calls, 1)

    def test_returned_receipt_without_checkpointed_response_is_uncertain(self):
        self.run_correction()
        saved = self.graph.get_state(self.config).values["m4_configuration_correction"]
        self.graph.update_state(self.config, {"m4_configuration_correction": {
            **saved, "attempts": saved["attempts"][:1]}}, as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(graph=self.reopen())
        self.assertEqual(self.model.calls, 1)

    def test_source_ledger_mismatch_and_untrusted_sender_stop_before_send(self):
        from dealdesk_phase2.tool_ledger import entries
        state = self.graph.get_state(self.config).values
        ledger = entries(self.graph, self.config, state["assessment_id"],
                         state["context"]["bundle_sha256"])
        ledger[-1]["result"]["records"][0]["fields"]["is_sellable"] = "forged"
        self.graph.update_state(self.config, {"tool_access_ledger": ledger}, as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction()
        self.assertEqual(self.model.calls, 0)

    def capture_original(self, response=None):
        original = ScriptedOriginalFinal(self.model.model, json.dumps(self.raw)
            if response is None else response)
        saved = capture_original_final_offline(self.graph, self.config, self.adapter,
            original, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        return original, saved

    def test_returned_original_digest_receipt_binds_one_correction_and_restart(self):
        original, saved = self.capture_original()
        self.assertEqual(saved["status"], "returned")
        self.assertEqual(saved["content"], self.kw["rejected_content"])
        result = self.run_correction(original_capture_start=saved["start_sha256"])
        self.assertEqual(result["validation"], "valid")
        self.assertEqual(self.run_correction(graph=self.reopen(),
            original_capture_start=saved["start_sha256"]), result)
        again = capture_original_final_offline(self.reopen(), self.config, self.adapter,
            original, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        self.assertEqual(again, saved)
        self.assertEqual(original.calls, 1)
        self.assertEqual(self.model.calls, 1)
        state = self.graph.get_state(self.config).values
        self.assertEqual(state["specialist_results"], self.before["specialist_results"])
        self.assertEqual(state["review_status"], self.before["review_status"])

    def test_captured_original_cannot_be_substituted_or_skipped(self):
        original, saved = self.capture_original()
        for change in ({}, {"original_capture_start": "0" * 64},
                       {"original_capture_start": saved["start_sha256"],
                        "rejected_content": json.dumps(self.corrected)}):
            with self.subTest(change=change), self.assertRaises(EvidenceMismatch):
                self.run_correction(**change)
        self.assertEqual(self.model.calls, 0)
        self.assertEqual(original.calls, 1)

    def test_original_missing_receipt_or_lost_checkpoint_is_not_replayable(self):
        original, saved = self.capture_original()
        path = attempt_path(self.owner, assessment_id=self.config["configurable"]["thread_id"],
            start_digest=saved["start_sha256"], stage=ORIGINAL_STAGE, ordinal=0)
        content = path.read_bytes()
        path.unlink()
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(original_capture_start=saved["start_sha256"])
        path.write_bytes(content.splitlines(keepends=True)[0])
        path.chmod(0o600)
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(original_capture_start=saved["start_sha256"])
        path.write_bytes(content)
        state = self.graph.get_state(self.config).values
        self.graph.update_state(self.config, {"m4_configuration_original_capture": {
            **state["m4_configuration_original_capture"], "content": None,
            "status": "reserved", "response_sha256": None}}, as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            capture_original_final_offline(self.reopen(), self.config, self.adapter,
                original, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        self.assertEqual(original.calls, 1)
        self.assertEqual(self.model.calls, 0)

    def test_failed_original_is_terminal_without_correction(self):
        failed = ScriptedOriginalFinal(self.model.model,
            lambda _: (_ for _ in ()).throw(TimeoutError("mock only")))
        with self.assertRaises(TimeoutError):
            capture_original_final_offline(self.graph, self.config, self.adapter,
                failed, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        with self.assertRaises(EvidenceMismatch):
            capture_original_final_offline(self.reopen(), self.config, self.adapter,
                failed, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        self.assertEqual(failed.calls, 1)
        self.assertEqual(self.model.calls, 0)

    def test_valid_original_is_returned_but_not_correction_eligible(self):
        original = ScriptedOriginalFinal(self.model.model, json.dumps(self.corrected))
        with self.assertRaisesRegex(EvidenceMismatch, "not_rejected"):
            capture_original_final_offline(self.graph, self.config, self.adapter,
                original, line_id=self.kw["line_id"], owner_dir=self.owner, opt_in=True)
        saved = self.graph.get_state(self.config).values["m4_configuration_original_capture"]
        self.assertEqual(saved["status"], "returned")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(original_capture_start=saved["start_sha256"])
        self.assertEqual(original.calls, 1)
        self.assertEqual(self.model.calls, 0)

    def test_original_checkpoint_content_and_digest_cannot_replace_receipt(self):
        from hashlib import sha256
        _, saved = self.capture_original()
        forged = json.dumps({**self.raw, "claims": [{**self.raw["claims"][0],
            "value_json": '"false"'}]})
        self.graph.update_state(self.config, {"m4_configuration_original_capture": {
            **saved, "content": forged, "response_sha256": sha256(forged.encode()).hexdigest()}},
            as_node="finish")
        with self.assertRaises(EvidenceMismatch):
            self.run_correction(rejected_content=forged,
                original_capture_start=saved["start_sha256"])
        self.assertEqual(self.model.calls, 0)


if __name__ == "__main__":
    unittest.main()
