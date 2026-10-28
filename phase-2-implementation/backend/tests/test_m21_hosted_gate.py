"""No-network Groq M2.1 manifest/owner/checkpoint integration."""

import json
import os
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from uuid import uuid4

from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.live_models import ProviderError
from dealdesk_phase2.m21_groq_contract import GroqM21Model
from dealdesk_phase2.m21_specialists import run_m21_evaluation, TOOLS
from dealdesk_phase2.hybrid_send_reservation import attempt_path
from dealdesk_phase2.hybrid_contracts import HybridContractError
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


def response(name, args, *, usage=None):
    return {"usage": usage or {"prompt_tokens": 200, "completion_tokens": 20},
        "choices": [{"finish_reason": "tool_calls", "message": {"content": None,
            "tool_calls": [{"id": "call_offline_m21_00001", "type": "function",
                "function": {"name": name, "arguments": _canonical(args)}}]}}]}


def models():
    return {name: GroqM21Model(name) for name in TOOLS}


def manifest(name, case):
    proposed = json.loads(Path("phase-2-implementation/evaluation/"
        "week3-hosted-validation-proposal.json").read_text())
    proposed.update(status="authorized_one_case", maximum_posts_total=6)
    proposed["cases"] = [{**next(x for x in proposed["cases"] if x["case_id"] == case),
                           "assessment_id": name}]
    return proposed


def digest(data):
    return sha256(_canonical(data).encode()).hexdigest()


class M21AuthorizedStatusManifest(unittest.TestCase):
    def test_credit_diagnostic_candidate_is_non_authorizing_and_two_posts(self):
        candidate = json.loads(Path("phase-2-implementation/evaluation/"
            "week3-credit-http400-diagnostic-candidate.json").read_text())
        self.assertEqual(digest(candidate),
            "592110acd76a914f56b55f7d23d8fa78819c95015a4444512aada50d47c3c8e9")
        self.assertEqual(candidate["status"], "authorization_candidate")
        self.assertEqual(candidate["order"], ["credit"])
        self.assertEqual(candidate["maximum_posts_total"], 2)
        self.assertEqual(candidate["maximum_completion_tokens_per_post"], 512)
        self.assertEqual(candidate["maximum_serialized_request_bytes_per_post"], 8192)

    def test_checked_in_authorized_status_is_not_an_approval_record(self):
        candidate = json.loads(Path("phase-2-implementation/evaluation/"
            "week3-hosted-b01-authorization-candidate.json").read_text())
        self.assertEqual(digest(candidate),
            "6b4597c3c6969c12b419300952d77a24d7d579d9fcd72693b07df1b0824553aa")
        self.assertEqual(candidate["status"], "authorized_one_case")
        self.assertEqual(len(candidate["cases"]), 1)
        self.assertEqual(candidate["maximum_posts_total"], 6)
        self.assertEqual(candidate["maximum_completion_tokens_per_post"], 512)
        self.assertEqual(candidate["maximum_serialized_request_bytes_per_post"], 8192)
        self.assertEqual(candidate["reported_total_token_post_send_stop"], 24000)
        self.assertEqual(candidate["execution_context"]["fresh_databases_required"], True)


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh isolated PostgreSQL source and checkpoint databases required")
class M21HostedGatePostgres(unittest.TestCase):
    def test_credit_diagnostic_only_two_sends_then_terminal_restart(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        bodies = []

        def send(url, key, header, body, **kwargs):
            bodies.append(body)
            self.assertTrue(kwargs["capture_http_error"])
            self.assertEqual(body["model"], "openai/gpt-oss-120b")
            self.assertLessEqual(len(_canonical(body).encode()), 8192)
            if len(bodies) == 1:
                public = json.loads(body["messages"][1]["content"])["input"]
                return response(TOOLS["credit"], {"subject_id": public["subject_id"]})
            return response("abstain", {"reason_code": "model_uncertainty"})

        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post", side_effect=send):
            owner = Path(directory)
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, before, data = self.original(saver)
                data.update(version="m21-credit-http400-diagnostic-v1",
                    status="authorization_candidate", order=["credit"],
                    allowed_tools={"credit": TOOLS["credit"]},
                    maximum_posts_total=2, maximum_posts_per_case=2)
                # Disposable test-only authorization fixture, NOT the candidate owner.
                state = self.gated(graph, config, data, owner)
                self.assertEqual(len(bodies), 2)
                self.assertEqual(set(state["m21_ai_results"]), {"credit"})
                self.assertNotIn("m21_review", state)
                self.assertNotIn("m21_ai", state.get("reviewer_package") or {})
                self.assertEqual(state["specialist_results"], before["specialist_results"])
                self.assertEqual(len([x for x in state["m21_model_attempts"] if
                                      x["status"] == "reserved"]), 2)
            with thesis_checkpointer(self.checkpoint) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                self.gated(graph, config, data, owner)
                self.assertEqual(len(bodies), 2)

    def setUp(self):
        self.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        self.connect = lambda: psycopg.connect(os.environ["M20_DATABASE_URL"])
        self.checkpoint = os.environ["M20_CHECKPOINT_DATABASE_URL"]
        with self.connect() as conn:
            if conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0] == 0:
                install_disposable_cases(conn)

    def original(self, saver, case="B01"):
        selected = next(x for x in CASES if x.case_id == case)
        name = "W3-GATED-" + str(uuid4())
        config = {"configurable": {"thread_id": name}}
        graph = build_original_graph(self.adapter, self.connect, saver)
        before = graph.invoke(initial_state(name, selected.run_id), config)
        return graph, config, before, manifest(name, case)

    def gated(self, graph, config, data, directory, *, active=True, account=True,
              approved=None, selected_models=None):
        data["execution_context"] = {"fixture_database": "dealdesk_test_fixture",
            "checkpoint_database": "dealdesk_test_checkpoint",
            "owner_directory": str(directory), "fresh_databases_required": True}
        approval = directory / "m21-approved-manifest.json"
        if not approval.exists():
            record = {"assessment_id": config["configurable"]["thread_id"],
                "approved_manifest_sha256": digest(data),
                "credential_env_selection": "GROQ_SECONDARY_API_KEY",
                "billing_disabled_confirmed": True}
            fd = os.open(approval, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(fd, _canonical(record).encode())
                os.fsync(fd)
            finally:
                os.close(fd)
        return run_m21_evaluation(graph, config, self.adapter,
            selected_models or models(), manifest=data,
            approved_manifest_sha256=approved if approved is not None else digest(data),
            authorized=active, free_tier_billing_disabled=account,
            owner_dir=directory)

    def test_valid_six_posts_original_only_redacted_and_reopen_without_replay(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        bodies = []

        def send(url, key, header, body, **kwargs):
            bodies.append(body)
            self.assertTrue(key.startswith("Bearer gsk_"))
            self.assertFalse(kwargs["capture_http_error"])
            for secret in ("M18-C-B01", "M18-D-B01", "M18-SNAPSHOT-B01"):
                self.assertNotIn(secret, _canonical(body))
            if body["messages"][-1]["role"] == "user":
                public = json.loads(body["messages"][1]["content"])["input"]
                return response(body["tools"][0]["function"]["name"],
                                {"subject_id": public["subject_id"]})
            observation = json.loads(body["messages"][-1]["content"])
            row = observation["records"][0]
            field, value = next(iter(row["fields"].items()))
            return response("submit_finding", {"claims": [{"ref": row["ref"],
                "field": field, "value_json": _canonical(value)}]})

        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post", side_effect=send):
            owner = Path(directory)
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, before, data = self.original(saver)
                state = self.gated(graph, config, data, owner)
                self.assertEqual(len(bodies), 6)
                self.assertEqual(state["specialist_results"], before["specialist_results"])
                self.assertEqual(state["candidate_status"], "not_started")
                self.assertEqual({x["execution"] for x in state["m21_ai_results"].values()},
                                 {"completed"})
                self.assertEqual(len([x for x in state["m21_model_attempts"] if
                                      x["status"] == "reserved"]), 6)
                self.assertEqual(len([x for x in state["tool_access_ledger"] if
                                      x["status"] == "completed"]), 3)
                self.assertEqual(state["reviewer_package"]["m21_ai"], state["m21_review"])
            with thesis_checkpointer(self.checkpoint) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                restarted = self.gated(graph, config, data, owner)
                self.assertEqual(restarted["m21_ai_results"], state["m21_ai_results"])
                self.assertEqual(len(bodies), 6)
                with patch.dict(os.environ, {"GROQ_SECONDARY_API_KEY":
                        "gsk_changed_offline_test_placeholder_9999"}):
                    with self.assertRaises(EvidenceMismatch):
                        self.gated(graph, config, data, owner)
                self.assertEqual(len(bodies), 6)
                receipt = attempt_path(owner, assessment_id=config["configurable"]["thread_id"],
                    start_digest=digest(data), stage="decision", ordinal=0)
                receipt.write_text("tampered\n")  # test-owned disposable owner only
                with self.assertRaises(HybridContractError):
                    self.gated(graph, config, data, owner)
                self.assertEqual(len(bodies), 6)

    def test_manifest_or_account_tampering_fails_before_any_post(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post") as send:
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, _, data = self.original(saver)
                data["execution_context"] = {"fixture_database": "dealdesk_test_fixture",
                    "checkpoint_database": "dealdesk_test_checkpoint",
                    "owner_directory": str(Path(directory)), "fresh_databases_required": True}
                with self.assertRaises(EvidenceMismatch):
                    run_m21_evaluation(graph, config, self.adapter, models(), manifest=data,
                        approved_manifest_sha256=digest(data), authorized=True,
                        free_tier_billing_disabled=True, owner_dir=Path(directory))
                for change in (lambda x: x.update(maximum_posts_total=18),
                               lambda x: x.update(credential_env_selection="GROQ_API_KEY"),
                               lambda x: x.update(model="wrong"),
                               lambda x: x.update(maximum_posts_total=6.0),
                               lambda x: x.update(cases=[7]),
                               lambda x: x["cases"][0].update(bundle_sha256="0" * 64)):
                    bad = json.loads(json.dumps(data))
                    change(bad)
                    with self.assertRaises((ValueError, EvidenceMismatch)):
                        self.gated(graph, config, bad, Path(directory))
                with self.assertRaises(ValueError):
                    self.gated(graph, config, data, Path(directory), active=False)
                with self.assertRaises(ValueError):
                    self.gated(graph, config, data, Path(directory), account=False)
                with self.assertRaises(ValueError):
                    self.gated(graph, config, data, Path(directory), approved="0" * 64)
                with TemporaryDirectory() as other_directory:
                    with self.assertRaises(ValueError):
                        run_m21_evaluation(graph, config, self.adapter, models(),
                            manifest=data, approved_manifest_sha256=digest(data),
                            authorized=True, free_tier_billing_disabled=True,
                            owner_dir=Path(other_directory))
                not_fresh = json.loads(json.dumps(data))
                not_fresh["execution_context"]["fresh_databases_required"] = False
                with self.assertRaises(ValueError):
                    run_m21_evaluation(graph, config, self.adapter, models(),
                        manifest=not_fresh, approved_manifest_sha256=digest(not_fresh),
                        authorized=True, free_tier_billing_disabled=True,
                        owner_dir=Path(directory))
                send.assert_not_called()
                self.assertNotIn("m21_hosted_owner", graph.get_state(config).values)

    def test_provider_error_and_reserved_crash_terminal_after_restart(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        for outcome in (ProviderError("http_400"), ProviderError("transport_timeout"),
                        KeyboardInterrupt("offline crash")):
            with (self.subTest(outcome=type(outcome).__name__),
                  TemporaryDirectory() as directory,
                  patch.dict(os.environ, {"GROQ_SECONDARY_API_KEY":
                      "gsk_offline_test_placeholder_123456789"})):
                calls = []

                def failed(*args, **kwargs):
                    calls.append(1)
                    raise outcome

                with thesis_checkpointer(self.checkpoint) as saver, patch(
                        "dealdesk_phase2.m21_groq_contract._post", side_effect=failed):
                    graph, config, before, data = self.original(saver)
                    with self.assertRaises((EvidenceMismatch, KeyboardInterrupt)):
                        self.gated(graph, config, data, Path(directory))
                    self.assertEqual(calls, [1])
                    self.assertEqual(graph.get_state(config).values["m21_model_attempts"][0][
                        "status"], "reserved")
                with thesis_checkpointer(self.checkpoint) as saver, patch(
                        "dealdesk_phase2.m21_groq_contract._post", side_effect=failed):
                    graph = build_original_graph(self.adapter, self.connect, saver)
                    with self.assertRaises(EvidenceMismatch):
                        self.gated(graph, config, data, Path(directory))
                    self.assertEqual(calls, [1])
                    self.assertEqual(graph.get_state(config).values["specialist_results"],
                                     before["specialist_results"])

    def test_completed_first_inspection_survives_restart_without_repeat_send(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        calls = []

        def send(url, key, header, body, **kwargs):
            calls.append(body)
            if body["messages"][-1]["role"] == "user":
                public = json.loads(body["messages"][1]["content"])["input"]
                return response(body["tools"][0]["function"]["name"], {
                    "subject_id": public["subject_id"]})
            observation = json.loads(body["messages"][-1]["content"])
            row = observation["records"][0]
            field, value = next(iter(row["fields"].items()))
            return response("submit_finding", {"claims": [{"ref": row["ref"],
                "field": field, "value_json": _canonical(value)}]})

        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post", side_effect=send):
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, before, data = self.original(saver)
                selected = models()
                original_prepare = selected["credit"].prepare_request

                def crash_before_second(input, observations):
                    if observations:
                        raise KeyboardInterrupt("offline pre-reservation crash")
                    return original_prepare(input, observations)

                selected["credit"].prepare_request = crash_before_second
                with self.assertRaises(KeyboardInterrupt):
                    self.gated(graph, config, data, Path(directory), selected_models=selected)
                snapshot = graph.get_state(config).values
                self.assertEqual(len(calls), 1)
                self.assertEqual([x["status"] for x in snapshot["m21_model_attempts"]],
                                 ["reserved", "returned"])
                self.assertEqual(len([e for e in snapshot["tool_access_ledger"] if e[
                    "status"] == "completed"]), 1)
            with thesis_checkpointer(self.checkpoint) as saver:
                graph = build_original_graph(self.adapter, self.connect, saver)
                state = self.gated(graph, config, data, Path(directory))
                self.assertEqual(len(calls), 6)  # no duplicate first inspection
                self.assertEqual(len(state["m21_ai_results"]), 3)
                self.assertEqual(state["specialist_results"], before["specialist_results"])

    def test_fabricated_claim_and_budget_overrun_stop_without_next_specialist(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        for adverse in ("forged", "token_over_limit", "malformed"):
            with (self.subTest(adverse=adverse), TemporaryDirectory() as directory,
                  patch.dict(os.environ, {"GROQ_SECONDARY_API_KEY":
                      "gsk_offline_test_placeholder_123456789"})):
                calls = []

                def send(url, key, header, body, **kwargs):
                    calls.append(body)
                    if body["messages"][-1]["role"] == "user":
                        public = json.loads(body["messages"][1]["content"])["input"]
                        return response(body["tools"][0]["function"]["name"], {
                            "subject_id": public["subject_id"]})
                    if adverse == "forged":
                        return response("submit_finding", {"claims": [{
                            "ref": "credit_profile:FORGED", "field": "credit_limit",
                            "value_json": '"100"'}]})
                    if adverse == "token_over_limit":
                        return response("abstain", {"reason_code": "model_uncertainty"},
                            usage={"prompt_tokens": 4097, "completion_tokens": 512})
                    return {"choices": [], "usage": {"prompt_tokens": 1,
                                                       "completion_tokens": 1}}

                with thesis_checkpointer(self.checkpoint) as saver, patch(
                        "dealdesk_phase2.m21_groq_contract._post", side_effect=send):
                    graph, config, before, data = self.original(saver)
                    with self.assertRaises(EvidenceMismatch):
                        self.gated(graph, config, data, Path(directory))
                    state = graph.get_state(config).values
                    self.assertEqual(len(calls), 2)
                    self.assertEqual(state["m21_ai_results"]["credit"]["execution"], "error")
                    self.assertEqual(state["reviewer_package"]["m21_ai"]["execution"], "stopped")
                    self.assertEqual(state["reviewer_package"]["m21_ai"]["validated_claims"], [])
                    self.assertNotIn("policy", state["m21_ai_results"])
                    self.assertEqual(state["specialist_results"], before["specialist_results"])

    def test_post_send_campaign_token_stop_is_terminal(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        calls = []

        def send(url, key, header, body, **kwargs):
            calls.append(body)
            usage = {"prompt_tokens": 4096, "completion_tokens": 512}
            if body["messages"][-1]["role"] == "user":
                public = json.loads(body["messages"][1]["content"])["input"]
                return response(body["tools"][0]["function"]["name"], {
                    "subject_id": public["subject_id"]}, usage=usage)
            observation = json.loads(body["messages"][-1]["content"])
            row = observation["records"][0]
            field, value = next(iter(row["fields"].items()))
            return response("submit_finding", {"claims": [{"ref": row["ref"],
                "field": field, "value_json": _canonical(value)}]}, usage=usage)

        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post", side_effect=send):
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, before, data = self.original(saver)
                with self.assertRaises(EvidenceMismatch):
                    self.gated(graph, config, data, Path(directory))
                self.assertEqual(len(calls), 6)
                state = graph.get_state(config).values
                self.assertEqual(state["m21_ai_results"]["approval_routing"]["execution"],
                                 "error")
                self.assertEqual(state["specialist_results"], before["specialist_results"])

    def test_unknown_owner_artifact_blocks_a_different_campaign(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        with TemporaryDirectory() as directory, patch.dict(os.environ, {
            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                "dealdesk_phase2.m21_groq_contract._post") as send:
            with thesis_checkpointer(self.checkpoint) as saver:
                graph, config, _, data = self.original(saver)
                (Path(directory) / "foreign-receipt.hybrid.audit.jsonl").write_text("foreign")
                with self.assertRaises(EvidenceMismatch):
                    self.gated(graph, config, data, Path(directory))
                send.assert_not_called()
