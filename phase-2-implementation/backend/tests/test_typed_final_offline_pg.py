"""No-network opt-in graph and durable PostgreSQL restart safety."""

import json
import os
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4

from dealdesk_phase2.m20_specialists import _one as config_one
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from dealdesk_phase2.live_models import ProviderError
from dealdesk_phase2.typed_final_contract import InvalidTerminal, VERSION
from dealdesk_phase2.typed_final_offline import (ScriptedTypedFinal,
    run_typed_final_offline, PROTOCOL_VERSION)
from m18_case_setup import CASES, install_disposable_cases
from test_m20_groq import tool_response
from test_m20_specialists import Scripted, inspect, product_finding

try:
    import psycopg
except ImportError:
    psycopg = None


def terminal(body, *, invalid=None):
    payload = json.loads(body["messages"][1]["content"])
    row = payload["observations"][0]["records"][0]
    field = ("fixed_margin_pct" if payload["input"]["specialist"] == "pricing"
             else "credit_status")
    result = {"version": VERSION, "kind": "finding", "claims": [{
        "ref": row["ref"], "field": field,
        "value_json": json.dumps(row["fields"][field])}],
        "reason_code": "none", "uncertainty_reasons": []}
    if invalid == "ref":
        result["claims"][0]["ref"] = "invented:ref"
    elif invalid == "value":
        result["claims"][0]["value_json"] = '"not-the-value"'
    elif invalid == "json":
        return {"choices": [{"finish_reason": "stop", "message": {
            "content": '{"version":', "tool_calls": None}}],
            "usage": {"prompt_tokens": 200, "completion_tokens": 40}}
    elif invalid == "abstain":
        result = {"version": VERSION, "kind": "abstain", "claims": [],
            "reason_code": "model_uncertainty", "uncertainty_reasons": []}
    return {"choices": [{"finish_reason": "stop", "message": {
        "content": json.dumps(result), "tool_calls": None}}],
        "usage": {"prompt_tokens": 200, "completion_tokens": 40}}


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh isolated M2.0 business and checkpoint databases required")
class TypedFinalPostgres(unittest.TestCase):
    def test_default_is_off(self):
        with self.assertRaisesRegex(ValueError, "typed_final_offline_opt_in_required"):
            run_typed_final_offline(None, {}, None, ScriptedTypedFinal([], None),
                specialist="pricing", owner_dir=Path("/tmp/opencode"))

    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["M20_DATABASE_URL"]))
        with cls.connect() as conn:
            if not conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]:
                install_disposable_cases(conn)

    def run_case(self, *, specialist="pricing", plan=1, invalid=None,
                 interrupt=False, change=None):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        case = next(x for x in CASES if x.case_id == "B05")
        identifier = "TYPED-OFFLINE-" + uuid4().hex
        config = {"configurable": {"thread_id": identifier}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as path:
            owner = Path(path)
            owner.chmod(0o700)
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                baseline = graph.invoke(initial_state(identifier, case.run_id), config)
                self.assertIsNone(baseline.get("stop_reason"), baseline.get("trace"))
                self.assertEqual(len(baseline.get("specialist_results", {})), 6)
                if specialist == "pricing":
                    config_one(graph, config, self.adapter, "configuration",
                        Scripted([inspect, product_finding]))
                # Credit's inspected subject is the original, not the assessment ID.
                def inspected(body):
                    if invalid == "inspect_transport":
                        raise ProviderError("transport_timeout")
                    public = json.loads(body["messages"][1]["content"])["input"]
                    return tool_response(body["tools"][0]["function"]["name"],
                        {"line_id": case.ids()["L"]} if specialist == "pricing" else
                        {"subject_id": public["subject_id"]},
                        call_id="typed_call_" + str(len(model.requests)))
                def finish(body):
                    if invalid == "transport":
                        raise ProviderError("transport_timeout")
                    return terminal(body, invalid=invalid)
                model = ScriptedTypedFinal([inspected] * plan,
                    None if interrupt else finish)
                args = dict(specialist=specialist, inspection_plan=plan,
                            owner_dir=owner, opt_in=True)
                failed = invalid in ("ref", "value", "json", "transport",
                                      "inspect_transport") or interrupt
                if failed:
                    with self.assertRaises((InvalidTerminal, ProviderError)):
                        run_typed_final_offline(graph, config, self.adapter, model, **args)
                    result = graph.get_state(config).values["typed_final_results"][specialist]
                    self.assertEqual(result["execution"], "error")
                    self.assertEqual(result["reason"], "transport_failure" if invalid in (
                        "transport", "inspect_transport") else "malformed_output")
                else:
                    result = run_typed_final_offline(graph, config, self.adapter, model, **args)
                    self.assertEqual(result["execution"], "abstained" if invalid ==
                        "abstain" else "completed")
                    self.assertEqual(result["protocol_version"], PROTOCOL_VERSION)
                    self.assertEqual(len(model.requests), plan + 1)
                    self.assertNotIn("tools", model.requests[-1])
                    self.assertEqual(graph.get_state(config).values["specialist_results"],
                                     baseline["specialist_results"])
                    self.assertEqual(graph.get_state(config).values["reviewer_package"][
                        "typed_final_ai"]["validated_claims"], result["validated_claims"])
                    if specialist == "pricing":
                        self.assertEqual(graph.get_state(config).values[
                            "m20_ai_results"]["configuration"]["model_turns"], 2)
                if change:
                    graph.update_state(config, change(graph.get_state(config).values),
                                       as_node="finish")
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                resume = ScriptedTypedFinal([], lambda _: self.fail("unexpected second send"))
                if failed or change:
                    with self.assertRaises((EvidenceMismatch, InvalidTerminal)):
                        run_typed_final_offline(graph, config, self.adapter, resume, **args)
                else:
                    self.assertEqual(run_typed_final_offline(graph, config, self.adapter,
                        resume, **args)["execution"], "abstained" if invalid ==
                        "abstain" else "completed")
                self.assertEqual(resume.requests, [])

    def test_pricing_one_and_two_inspections(self):
        for plan in (1, 2):
            with self.subTest(plan=plan):
                self.run_case(plan=plan)

    def test_credit_alias_and_abstain(self):
        self.run_case(specialist="credit")
        self.run_case(specialist="credit", invalid="abstain")

    def test_malformed_fabricated_mismatch_and_interruption_no_replay(self):
        for invalid in ("ref", "value", "json"):
            with self.subTest(invalid=invalid):
                self.run_case(invalid=invalid)
        self.run_case(interrupt=True)
        self.run_case(invalid="transport")
        self.run_case(invalid="inspect_transport")

    def test_checkpoint_tampering_and_budget(self):
        self.run_case(change=lambda state: {"typed_final_protocol": {
            **state["typed_final_protocol"], "inspection_plan": 2}})
        self.run_case(change=lambda state: {"typed_final_attempts": [
            *state["typed_final_attempts"], {
                **state["typed_final_attempts"][0], "status": "reserved"}]})
        self.run_case(change=lambda state: {"typed_final_attempts": [
            *state["typed_final_attempts"], *[{
                **state["typed_final_attempts"][0], "ordinal": n,
                "status": "reserved"} for n in (1, 2, 3)]]})
        self.run_case(change=lambda state: {"tool_access_ledger": [
            *state["tool_access_ledger"][:-1], {
                **state["tool_access_ledger"][-1], "identity": {
                    **state["tool_access_ledger"][-1]["identity"],
                    "permission_version": "forged"}}]})


if __name__ == "__main__":
    unittest.main()
