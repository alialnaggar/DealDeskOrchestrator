"""Dormant hosted gate exercised only by fake transports and synthetic approval fixtures."""

import json
import os
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.groq_typed_final import (WIRE_VERSION, PROMPT_VERSION, SCHEMA_NAME,
                                               FINAL_SYSTEM_INSTRUCTION)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.live_models import GROQ_MODEL, ProviderError
from dealdesk_phase2.m20_groq import (WIRE_VERSION as CONFIG_WIRE,
    PROMPT_VERSION as CONFIG_PROMPT, system_instruction as config_instruction)
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT, Phase1CAdapter
from dealdesk_phase2.tool_permissions import PERMISSION_VERSION
from dealdesk_phase2.typed_final_contract import VERSION
from dealdesk_phase2.typed_final_hosted import (APPROVAL_NAME, HOSTED_ACTIVATION,
    INSPECTION_WIRE_VERSION, INSPECTION_PROMPT_VERSION, MANIFEST_VERSION,
    SCHEMA_SHA256, MockTypedTransport, budgets, inspection_instruction,
    full_m21_budget, run_typed_final_hosted)
from m18_case_setup import CASES, install_disposable_cases
from test_m20_groq import tool_response

try:
    import psycopg
except ImportError:
    psycopg = None


def response(body, wrong=None):
    if "tools" in body:
        domain = json.loads(body["messages"][1]["content"])["input"]["specialist"]
        if domain == "configuration" and len(body["messages"]) > 2:
            record = json.loads(body["messages"][3]["content"])["records"][0]
            return tool_response("submit_finding", {"claims": [{"ref": record["ref"],
                "field": "is_sellable", "value_json": json.dumps(record[
                    "fields"]["is_sellable"])}], "uncertainty_reasons": []})
        args = ({"subject_id": json.loads(body["messages"][1]["content"])[
            "input"]["subject_id"]} if domain == "credit" else
            {"line_id": "M18-L-B05"})
        return tool_response(body["tools"][0]["function"]["name"], args,
                             call_id="test_" + domain + str(len(body["messages"])))
    task = json.loads(body["messages"][1]["content"])
    row = task["observations"][0]["records"][0]
    field = "fixed_margin_pct" if task["input"]["specialist"] == "pricing" else "credit_status"
    payload = {"version": VERSION, "kind": "finding", "claims": [{"ref": row[
        "ref"], "field": field, "value_json": json.dumps(row["fields"][field])}],
        "uncertainty_reasons": [], "reason_code": "none"}
    if wrong == "citation":
        payload["claims"][0]["ref"] = "invented:ref"
    if wrong == "abstain":
        payload.update(kind="abstain", claims=[], reason_code="model_uncertainty")
    if wrong == "malformed":
        text = '{"version":'
    else:
        text = json.dumps(payload)
    return {"choices": [{"finish_reason": "length" if wrong == "length" else "stop",
        "message": {"content": text,
        "tool_calls": None}}], "usage": {"prompt_tokens": 200, "completion_tokens": 50}}


def manifest(state, specialist, owner, business_database, checkpoint_database, plan=1):
    context = state["context"]
    return {"version": MANIFEST_VERSION, "status": "authorized_one_case",
        "phase1c_pin": PHASE1C_COMMIT, "specialist": specialist,
        "inspection_plan": plan, "account_id": "synthetic-test-account",
        "billing_state": "free_tier_billing_disabled", "provider": "groq",
        "model": GROQ_MODEL, "credential_env_selection": "GROQ_SECONDARY_API_KEY",
        "permission_version": PERMISSION_VERSION,
        "inspection_wire_version": INSPECTION_WIRE_VERSION,
        "inspection_prompt_version": INSPECTION_PROMPT_VERSION,
        "inspection_prompt_sha256": sha256(inspection_instruction(specialist).encode(
            )).hexdigest(),
        "configuration_wire_version": CONFIG_WIRE,
        "configuration_prompt_version": CONFIG_PROMPT,
        "configuration_prompt_sha256": sha256(config_instruction("configuration").encode(
            )).hexdigest(),
        "wire_version": WIRE_VERSION, "prompt_version": PROMPT_VERSION,
        "final_prompt_sha256": sha256(FINAL_SYSTEM_INSTRUCTION.encode()).hexdigest(),
        "schema_name": SCHEMA_NAME, "schema_sha256": SCHEMA_SHA256,
        "budgets": budgets(specialist, plan),
        "case": {"case_id": "B05", "assessment_id": context["assessment_id"],
            "run_id": context["phase1c_run_id"], "subject_id": context[
                "original_deal_id"], "bundle_sha256": context["bundle_sha256"],
            "source_input_digest": context["source_input_digest"],
            "as_of_at": context["as_of_at"],
            "data_snapshot_ref": context["data_snapshot_ref"]},
        "execution_context": {"fixture_database": business_database,
            "checkpoint_database": checkpoint_database,
            "owner_directory": str(owner), "fresh_databases_required": True}}


def fixture_approval(owner, data, digest):
    path = owner / APPROVAL_NAME
    path.write_text(json.dumps({"version": MANIFEST_VERSION,
        "assessment_id": data["case"]["assessment_id"],
        "approved_manifest_sha256": digest,
        "credential_env_selection": "GROQ_SECONDARY_API_KEY",
        "account_id": data["account_id"], "billing_disabled_confirmed": True,
        "typed_final_opt_in_confirmed": True}))
    path.chmod(0o600)
    return path


class GateUnit(unittest.TestCase):
    def test_default_gate_refuses_even_with_authorized_bool(self):
        self.assertIs(HOSTED_ACTIVATION, False)
        self.assertEqual(full_m21_budget(), {"posts": 6,
            "configured_completion_tokens": 3584, "reported_post_send_stop": 24000})
        self.assertEqual((budgets("pricing", 2)["maximum_posts_per_case"],
            budgets("pricing", 2)["maximum_configured_completion_per_case"]), (5, 3072))
        self.assertEqual((budgets("credit", 1)["maximum_posts_per_case"],
            budgets("credit", 1)["maximum_configured_completion_per_case"]), (2, 1536))
        with self.assertRaisesRegex(ValueError, "activation_or_authorization_required"):
            run_typed_final_hosted(None, {}, None, manifest={},
                approved_manifest_sha256="a" * 64, specialist="credit",
                owner_dir=Path("/tmp/opencode"), authorized=True,
                billing_disabled=True)


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "fresh isolated PostgreSQL business and checkpoint databases required")
class HostedMockPostgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["M20_DATABASE_URL"]))
        with cls.connect() as conn:
            if not conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]:
                install_disposable_cases(conn)

    def run_case(self, specialist="credit", plan=1, wrong=None, tamper=None):
        identifier = "TYPED-HOSTED-MOCK-" + uuid4().hex
        case = next(x for x in CASES if x.case_id == "B05")
        config = {"configurable": {"thread_id": identifier}}
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as temporary:
            owner = Path(temporary)
            owner.chmod(0o700)
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                original = graph.invoke(initial_state(identifier, case.run_id), config)
                with graph.phase2_connection_factory() as connection:
                    database = connection.info.dbname
                data = manifest(original, specialist, owner, database,
                    graph.checkpointer.conn.info.dbname, plan)
                digest = sha256(_canonical(data).encode()).hexdigest()
                approval = fixture_approval(owner, data, digest)
                args = dict(manifest=data, approved_manifest_sha256=digest,
                    specialist=specialist, owner_dir=owner, authorized=True,
                    billing_disabled=True)
                if tamper == "approval":
                    approval.write_text("{}")
                    with self.assertRaises(EvidenceMismatch):
                        run_typed_final_hosted(graph, config, self.adapter,
                            _mock_transport=MockTypedTransport([]), **args)
                    return
                if tamper in ("manifest", "schema", "budget"):
                    bad = {**data, **({"wire_version": "m20-groq-native-tools-v1"}
                        if tamper == "manifest" else {"schema_sha256": "0" * 64}
                        if tamper == "schema" else {"budgets": {
                            **data["budgets"], "maximum_posts_per_case": 1}})}
                    with self.assertRaises(ValueError):
                        run_typed_final_hosted(graph, config, self.adapter,
                            _mock_transport=MockTypedTransport([]),
                            **{**args, "manifest": bad})
                    return
                def answer(body):
                    if wrong == "transport_config" and "response_format" not in body:
                        raise ProviderError("transport_timeout")
                    if wrong == "http_400" and "response_format" in body:
                        raise ProviderError("http_400")
                    if wrong == "timeout" and "response_format" in body:
                        raise ProviderError("transport_timeout")
                    result = response(body, wrong if "response_format" in body else None)
                    if wrong == "usage" and "response_format" in body:
                        result["usage"]["prompt_tokens"] = 4097
                    return result
                transport = MockTypedTransport([answer] * (plan + (3 if specialist ==
                    "pricing" else 1)))
                with patch("dealdesk_phase2.typed_final_hosted._post",
                        side_effect=AssertionError("no HTTP even with mock")) as sender:
                    if wrong == "interrupt":
                        with patch("dealdesk_phase2.typed_final_offline.parse_response",
                                side_effect=KeyboardInterrupt("synthetic crash")), self.assertRaises(
                                KeyboardInterrupt):
                            run_typed_final_hosted(graph, config, self.adapter,
                                _mock_transport=transport, **args)
                    elif wrong in ("http_400", "timeout", "citation", "malformed",
                                   "usage", "length", "transport_config"):
                        with self.assertRaises((EvidenceMismatch, ProviderError, ValueError)):
                            run_typed_final_hosted(graph, config, self.adapter,
                                _mock_transport=transport, **args)
                    else:
                        result = run_typed_final_hosted(graph, config, self.adapter,
                            _mock_transport=transport, **args)
                        self.assertEqual(result["execution"], "abstained" if wrong ==
                            "abstain" else "completed")
                        self.assertEqual(graph.get_state(config).values[
                            "specialist_results"], original["specialist_results"])
                        state = graph.get_state(config).values
                        self.assertEqual(len([x for x in state["typed_final_attempts"]
                            if x["status"] == "reserved"]), plan + 1)
                        self.assertEqual(len([x for x in state.get("m20_model_attempts", [])
                            if x["status"] == "reserved"]), 2 if specialist ==
                            "pricing" else 0)
                    sender.assert_not_called()
                if tamper == "receipt":
                    files = [x for x in owner.iterdir() if x.name.endswith(
                        ".hybrid.audit.jsonl") and '"' not in x.name]
                    victim = next(x for x in files if '"event":"returned"' in x.read_text())
                    victim.write_text("tampered")
                if tamper == "config_identity":
                    state = graph.get_state(config).values
                    graph.update_state(config, {"m20_model_attempts": [{
                        **state["m20_model_attempts"][0], "bundle_sha256": "0" * 64},
                        *state["m20_model_attempts"][1:]]}, as_node="finish")
            with thesis_checkpointer(os.environ["M20_CHECKPOINT_DATABASE_URL"]) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                transport2 = MockTypedTransport([lambda _: self.fail("forbidden replay")])
                if wrong in ("http_400", "timeout", "citation", "malformed",
                             "usage", "length", "transport_config", "interrupt") or tamper:
                    with self.assertRaises((EvidenceMismatch, ProviderError, ValueError)):
                        run_typed_final_hosted(graph, config, self.adapter,
                            _mock_transport=transport2, **args)
                else:
                    self.assertEqual(run_typed_final_hosted(graph, config, self.adapter,
                        _mock_transport=transport2, **args)["execution"],
                        "abstained" if wrong == "abstain" else "completed")
                self.assertEqual(transport2.requests, [])

    def test_credit_findings_abstain_and_failures(self):
        for wrong in (None, "abstain", "citation", "malformed", "http_400",
                      "timeout", "interrupt", "usage", "length"):
            with self.subTest(wrong=wrong):
                self.run_case(wrong=wrong)

    def test_pricing_configuration_one_and_two_inspections(self):
        for plan in (1, 2):
            self.run_case("pricing", plan)
        self.run_case("pricing", 1, wrong="transport_config")

    def test_tamper_and_approval(self):
        self.run_case(tamper="receipt")
        self.run_case(tamper="approval")
        self.run_case(tamper="manifest")
        self.run_case(tamper="schema")
        self.run_case(tamper="budget")
        self.run_case("pricing", tamper="config_identity")


if __name__ == "__main__":
    unittest.main()
