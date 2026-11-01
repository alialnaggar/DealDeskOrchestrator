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
from dealdesk_phase2.m21_specialists import (checked_candidate_context,
    run_m21_evaluation, TOOLS)
from dealdesk_phase2.hybrid_send_reservation import attempt_path
from dealdesk_phase2.hybrid_contracts import HybridContractError
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from m18_case_setup import CASES, install_disposable_cases
from m21_integrated_credit_setup import (install_integrated_credit,
    verify_integrated_credit)

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
    def test_fulfillment_campaign_error_summary_is_bounded_and_distinguishes_local_quota(self):
        from run_groq_development import _fulfillment_error_summary
        for code, phase, expected in (("groq_daily_limit", "decision", None),
                                      ("http_400", "final", "a" * 64)):
            receipt = {"status": "error", "error_code": code,
                "request_metadata": {"phase": phase, "bytes": 9888,
                    "strict_schema_sha256": expected, "private": "SECRET"},
                "provider_diagnostic": {"message": "SECRET"}}
            result = _fulfillment_error_summary({"model_attempt_ledger": [receipt]})
            self.assertEqual(result["error_code"], code)
            self.assertEqual(result["phase"], phase)
            self.assertEqual(result["strict_schema_sha256"], expected)
            self.assertEqual(result["request_bytes"], 9888)
            self.assertNotIn("SECRET", str(result))
        self.assertEqual(_fulfillment_error_summary({"model_attempt_ledger": [{
            "status": "error", "error_code": "SECRET", "request_metadata": {
                "phase": "SECRET", "bytes": True,
                "strict_schema_sha256": "z" * 64}}]}),
            {"error_code": "other", "phase": None, "request_bytes": None,
             "strict_schema_sha256": None})

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
    def test_configuration_b01_n01_actual_product_refs_and_terminal_boundaries(self):
        """Real pinned source and checkpoint, mocked terminal; never hosted."""
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        from dealdesk_phase2.graph_state import pinned_from_state
        from dealdesk_phase2.m20_specialists import _source_records, TOOLS as M20_TOOLS
        from dealdesk_phase2.groq_typed_final import (FinalResponseError,
            parse_configuration_final)
        from dealdesk_phase2.typed_final_contract import VERSION as FINAL_VERSION
        with thesis_checkpointer(self.checkpoint) as saver:
            for case_id in ("B01", "N01"):
                with self.subTest(case_id=case_id):
                    selected = next(c for c in CASES if c.case_id == case_id)
                    name = "DEV-CONFIG-" + uuid4().hex
                    config = {"configurable": {"thread_id": name}}
                    graph = build_original_graph(self.adapter, self.connect, saver)
                    state = graph.invoke(initial_state(name, selected.run_id), config)
                    pool = self.adapter.validate_pinned_context(pinned_from_state(state))
                    records = _source_records(pool, state, "configuration",
                        selected.ids()["L"])
                    self.assertEqual([r["ref"] for r in records], ["product:" +
                        selected.ids()["P"]])
                    obs = ({"tool": M20_TOOLS["configuration"], "execution": "completed",
                        "records": records, "returned_refs": [r["ref"] for r in records]},)
                    input = {"specialist": "configuration", "permitted_tool":
                        M20_TOOLS["configuration"], "line_ids": [selected.ids()["L"]]}
                    def reply(ref, field, value):
                        return {"choices": [{"finish_reason": "stop", "message": {
                            "content": json.dumps({"version": FINAL_VERSION,
                                "kind": "finding", "claims": [{"ref": ref,
                                    "field": field, "value_json": json.dumps(value)}],
                                "reason_code": "none", "uncertainty_reasons": []})}}],
                            "usage": {"prompt_tokens": 500, "completion_tokens": 70}}
                    ref = records[0]["ref"]
                    self.assertEqual(parse_configuration_final(reply(ref,
                        "is_sellable", True), input, obs)["claims"][0]["ref"], ref)
                    for other in ("B01", "N01"):
                        if other != case_id:
                            with self.assertRaises(FinalResponseError) as caught:
                                parse_configuration_final(reply("product:M18-P-" +
                                    other, "is_sellable", True), input, obs)
                            self.assertEqual(caught.exception.category, "claim_binding")
                    with self.assertRaises(FinalResponseError):
                        parse_configuration_final(reply(ref, "is_sellable", False),
                            input, obs)
                    # The returned configuration object is inspectable context,
                    # not a citable terminal scalar. Never relax the validator.
                    self.assertIsInstance(records[0]["fields"]["configuration_json"],
                        dict)
                    with self.assertRaises(FinalResponseError) as caught:
                        parse_configuration_final(reply(ref, "configuration_json",
                            records[0]["fields"]["configuration_json"]), input, obs)
                    self.assertEqual(caught.exception.category, "claim_value_type_object")

    def test_full_six_development_graph_continuations_offline(self):
        self._six_campaign_offline()

    def test_full_six_original_ai_with_fixed_checked_candidate_offline(self):
        self._six_campaign_offline(binding=True)

    def test_n01_six_original_ai_without_candidate_after_forbidden_partial_offline(self):
        self._six_campaign_offline(case_id="N01")

    def test_integrated_credit_reconciled_candidate_offline(self):
        self._integrated_six_offline("B01", "RC01", binding=True)

    def test_integrated_credit_held_no_candidate_offline(self):
        self._integrated_six_offline("N01", "HC03")

    def test_integrated_credit_incomplete_no_candidate_offline(self):
        self._integrated_six_offline("N01", "UC02")

    def _integrated_six_offline(self, case_id, variant, *, binding=False):
        from dealdesk_phase2.graph_state import pinned_from_state
        from psycopg import sql
        from copy import deepcopy
        parts = psycopg.conninfo.conninfo_to_dict(os.environ["M20_DATABASE_URL"])
        admin = psycopg.conninfo.make_conninfo(**{**parts, "dbname": "postgres"})
        name = "m21_integrated_" + uuid4().hex[:16]
        with psycopg.connect(admin, autocommit=True) as db:
            db.execute(sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(
                sql.Identifier(name), sql.Identifier(parts["dbname"])))
        original_connect = self.connect
        target = psycopg.conninfo.make_conninfo(**{**parts, "dbname": name})
        try:
            self.connect = lambda: psycopg.connect(target)
            with self.connect() as db:
                install_integrated_credit(db, case_id=case_id, variant=variant)
            from dealdesk_phase2.checkpoint import thesis_checkpointer
            checkpoint_name = "m21_preflight_" + uuid4().hex[:16]
            checkpoint = psycopg.conninfo.make_conninfo(**{**parts,
                "dbname": checkpoint_name})
            with psycopg.connect(admin, autocommit=True) as db:
                db.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(checkpoint_name)))
            try:
                with thesis_checkpointer(checkpoint) as saver:
                    selected = next(c for c in CASES if c.case_id == case_id)
                    assessment = "DEV-PREFLIGHT-" + uuid4().hex
                    graph = build_original_graph(self.adapter, self.connect, saver)
                    before = graph.invoke(initial_state(assessment, selected.run_id),
                        {"configurable": {"thread_id": assessment}})
                    pool = self.adapter.validate_pinned_context(pinned_from_state(before))
                    fixed = before["specialist_results"]["credit"]
                    verify_integrated_credit(pool, fixed, case_id=case_id, variant=variant)
                    corrupted = deepcopy(pool)
                    if variant == "UC02":
                        corrupted["credit"]["customer_id"] = "other"
                    else:
                        corrupted["payments"][0]["invoice_number"] = "other"
                    with self.assertRaises(ValueError):
                        verify_integrated_credit(corrupted, fixed, case_id=case_id,
                            variant=variant)
                self._six_campaign_offline(binding=binding, case_id=case_id,
                    credit_variant=variant)
            finally:
                with psycopg.connect(admin, autocommit=True) as db:
                    db.execute(sql.SQL("DROP DATABASE {}").format(
                        sql.Identifier(checkpoint_name)))
        finally:
            self.connect = original_connect
            with psycopg.connect(admin, autocommit=True) as db:
                db.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(name)))

    def _six_campaign_offline(self, *, binding=False, case_id="B01", credit_variant=None):
        """Fresh PostgreSQL checkpoint; all six model transports are offline doubles."""
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        from dealdesk_phase2.typed_final_contract import VERSION as FINAL_VERSION
        from run_groq_development import _six_campaign
        name = "dev_six_" + uuid4().hex[:16]
        parts = psycopg.conninfo.conninfo_to_dict(self.checkpoint)
        admin = psycopg.conninfo.make_conninfo(**{**parts, "dbname": "postgres"})
        dedicated = psycopg.conninfo.make_conninfo(**{**parts, "dbname": name})
        with psycopg.connect(admin, autocommit=True) as db:
            db.execute("CREATE DATABASE " + name)
        try:
            with TemporaryDirectory(dir="/tmp/opencode") as directory:
                root = Path(directory)
                root.chmod(0o700)
                (root / "owner").mkdir(mode=0o700)  # same setup as the real CLI
                with thesis_checkpointer(dedicated) as saver:
                    if case_id == "N01":
                        run_id = next(x.run_id for x in CASES if x.case_id == case_id)
                        config = {"configurable": {"thread_id": "DEV-N01-" + uuid4().hex}}
                        graph = build_original_graph(self.adapter, self.connect, saver)
                        before = graph.invoke(initial_state(config["configurable"][
                            "thread_id"], run_id), config)
                    else:
                        graph, config, before, _ = self.original(saver, case_id)
                    if case_id == "N01":
                        from dealdesk_phase2.graph_state import pinned_from_state
                        from dealdesk_phase2.fulfillment_agent import eligible_line
                        pool = self.adapter.validate_pinned_context(pinned_from_state(before))
                        self.assertIs(pool["deal"]["terms_json"]["allow_partial_delivery"], False)
                        self.assertEqual(eligible_line(before, pool)[1], "eligible")
                    calls = []
                    model_visibility = []
                    def fake_post(url, key, header, body, **kwargs):
                        calls.append(body)
                        if body.get("response_format", {}).get("json_schema", {}).get(
                                "name") == "fulfillment_contribution":
                            task = json.loads(body["messages"][1]["content"].split(
                                "Input and observations: ", 1)[1])
                            return {"choices": [{"finish_reason": "stop", "message": {
                                "content": json.dumps({"kind": ("binding_proposal" if binding else
                                    "abstention"), "line_id": task[
                                    "input"]["line_id"], "delivery_slices": [], "citations": [],
                                    "tradeoffs": [], "assumptions": [], "unmet_requirements": [],
                                    "uncertainty_reasons": [], "finding": "", "reason":
                                    "insufficient evidence", "claims": [],
                                    "tradeoff_code": ("partial_delivery_requires_customer_acceptance"
                                        if binding else "none"), **({"delivery_slices": [
                                        {"quantity": "8", "delivery_date": "2026-09-03",
                                         "source_refs": ["inventory:M18-INV-B01"]},
                                        {"quantity": "2", "delivery_date": "2026-09-08",
                                         "source_refs": ["inbound_supply:M18-IN-B01",
                                                         "inventory:M18-INV-B01"]}]}
                                        if binding else {})})}}], "model": "openai/gpt-oss-120b",
                                "usage": {"prompt_tokens": 100, "completion_tokens": 40}}
                        if "Input and observations: " in body["messages"][1]["content"]:
                            return {"choices": [{"finish_reason": "stop", "message": {
                                "content": "READY"}}], "model": "openai/gpt-oss-120b",
                                "usage": {"prompt_tokens": 100, "completion_tokens": 15}}
                        public = json.loads(body["messages"][1]["content"])["input"]
                        domain = public["specialist"]
                        if binding and domain in TOOLS:
                            model_visibility.append((domain, public.get("subject_id"),
                                "M17-" in _canonical(body)))
                        if "response_format" not in body:
                            if domain in TOOLS and len(body["messages"]) > 2:
                                record = json.loads(body["messages"][3]["content"])[
                                    "records"][0]
                                field, value = next(iter(record["fields"].items()))
                                return response("submit_finding", {"claims": [{
                                    "ref": record["ref"], "field": field,
                                    "value_json": json.dumps(value)}]})
                            name = (TOOLS[domain] if domain in TOOLS else
                                "inspect_" + domain + "_line")
                            args = ({"subject_id": public["subject_id"]} if domain in TOOLS
                                else {"line_id": public["line_ids"][0]})
                            return response(name, args)
                        observation = json.loads(body["messages"][1]["content"])[
                            "observations"][0]
                        if domain == "credit" and credit_variant == "UC02":
                            return {"choices": [{"finish_reason": "stop", "message": {
                                "content": json.dumps({"version": FINAL_VERSION,
                                    "kind": "abstain", "claims": [],
                                    "reason_code": "insufficient_evidence",
                                    "uncertainty_reasons": []})}}],
                                "usage": {"prompt_tokens": 200, "completion_tokens": 60}}
                        if domain == "credit" and credit_variant in ("RC01", "HC03"):
                            fields = (("credit_profile", "credit_status"),
                                ("receivable", "outstanding_amount"),
                                ("payment", "paid_amount"))
                            selected = [next(r for r in observation["records"] if
                                r["ref"].startswith(kind + ":")) for kind, _ in fields]
                            self.assertEqual(selected[1]["invoice_match_key"],
                                selected[2]["invoice_match_key"])
                            self.assertNotIn("M21IC-INVOICE", _canonical(body))
                            claims = [{"ref": r["ref"], "field": field,
                                "value_json": json.dumps(r["fields"][field])} for
                                r, (_, field) in zip(selected, fields)]
                            return {"choices": [{"finish_reason": "stop", "message": {
                                "content": json.dumps({"version": FINAL_VERSION,
                                    "kind": "finding", "claims": claims,
                                    "reason_code": "none", "uncertainty_reasons": []})}}],
                                "usage": {"prompt_tokens": 200, "completion_tokens": 60}}
                        field = {"configuration": "is_sellable", "pricing":
                            "fixed_margin_pct", "credit": "credit_status"}[domain]
                        record = next(row for row in observation["records"] if
                            field in row["fields"])
                        return {"choices": [{"finish_reason": "stop", "message": {
                            "content": json.dumps({"version": FINAL_VERSION,
                                "kind": "finding", "claims": [{"ref": record["ref"],
                                "field": field, "value_json": json.dumps(record[
                                    "fields"][field])}], "reason_code": "none",
                                "uncertainty_reasons": []})}}],
                            "usage": {"prompt_tokens": 200, "completion_tokens": 60}}
                    run_id = next(x.run_id for x in CASES if x.case_id == case_id)
                    with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                            "dealdesk_phase2.live_models._post", side_effect=fake_post), patch(
                            "dealdesk_phase2.m21_groq_contract._post", side_effect=fake_post):
                        try:
                            status = _six_campaign(graph, config, self.adapter,
                                case_id=case_id, account_id="synthetic-test-account", root=root,
                                key="gsk_offline_test_placeholder_123456789", run_id=run_id)
                        except EvidenceMismatch:
                            if not binding:
                                raise
                            snapshot = graph.get_state(config).values
                            self.fail(str({"m21": {k: (v.get("execution"), v.get("reason"),
                                v.get("model_output_category")) for k,v in snapshot.get(
                                "m21_ai_results",{}).items()}, "calls": len(calls),
                                "tool_count": len(snapshot.get("tool_access_ledger", [])),
                                "visibility": model_visibility}))
                    state = graph.get_state(config).values
                    from dealdesk_phase2.m22_capture import capture_m22
                    projected = capture_m22(state, self.adapter)
                    self.assertEqual(projected["evaluation_status"], "completed")
                    self.assertEqual(set(projected["ai_original"]), set(state["specialist_results"]))
                    self.assertEqual(projected["candidate_id"] is not None, binding)
                    self.assertEqual(projected["fixed_candidate"] is not None, binding)
                    self.assertEqual(projected["receipt_verification"], "not_checked")
                    self.assertIsNone(projected["total_tokens"])
                    self.assertIsNone(projected["total_latency_ms"])
                    self.assertIsNone(projected["accuracy"])
                    self.assertEqual(capture_m22(state, self.adapter,
                        checkpoint_pending=True)["evaluation_status"], "stopped_or_incomplete")
                    self.assertTrue(projected["request_count"] >= projected["returned_count"])
                    self.assertTrue(all(row["tokens"] is None or set(row["tokens"]) == {
                        "prompt_tokens", "completion_tokens"} for row in projected["attempts"]))
                    from copy import deepcopy
                    for change in (
                            lambda x: x["context"].update(original_deal_id="wrong"),
                            lambda x: x["reviewer_package"]["original"].update(
                                review_status="approved"),
                            lambda x: x["m21_ai_results"]["policy"]["validated_claims"][0].update(
                                value="fabricated"),
                            lambda x: x["m21_model_attempts"][0].update(
                                subject_id="wrong"),
                            lambda x: x["m21_model_attempts"].append({
                                **x["m21_model_attempts"][0], "status": "returned"}),
                            lambda x: x["m21_model_attempts"].append({
                                **x["m21_model_attempts"][0], "status": "returned",
                                "ordinal": 99}),
                            lambda x: x["m21_model_attempts"].append({
                                **x["m21_model_attempts"][0], "status": "reserved"})):
                        forged = deepcopy(state)
                        change(forged)
                        with self.assertRaises((EvidenceMismatch, ValueError)):
                            capture_m22(forged, self.adapter)
                    self.assertEqual(status, "six_stages_completed", msg={
                        "fulfillment": {k: state.get("ai_fulfillment_result", {}).get(k)
                            for k in ("execution", "error")}, "calls": len(calls),
                        "attempts": [(r.get("status"), r.get("error_code")) for r in
                            state.get("model_attempt_ledger", [])]})
                    self.assertEqual(state["specialist_results"], before["specialist_results"])
                    from dealdesk_phase2.graph_state import SPECIALISTS, validate_result
                    self.assertEqual(set(state["specialist_results"]), set(SPECIALISTS))
                    for domain in SPECIALISTS:
                        validate_result(state["specialist_results"][domain], state, domain)
                    original_id = state["context"]["original_deal_id"]
                    package = state["reviewer_package"]
                    self.assertEqual(package["original"]["deal_id"], original_id)
                    self.assertEqual(package["original"]["review_status"],
                        state["review_status"])
                    self.assertEqual(package["original"]["specialists"], {name: {
                        "execution": row["execution"], "finding": row["finding"]}
                        for name, row in state["specialist_results"].items()})
                    self.assertEqual(package["m21_ai"], state["m21_review"])
                    self.assertEqual(package["m21_ai"]["fixed_review_status"],
                        state["review_status"])
                    self.assertEqual(package["m21_ai"]["fixed_route_withheld"],
                        state["specialist_results"]["approval_routing"]["payload"][
                            "route_withheld"])
                    self.assertEqual(package["m21_ai"]["subject_id"], original_id)
                    self.assertEqual(package["configuration_ai"], {key: state[
                        "m20_ai_results"]["configuration"][key] for key in (
                        "execution", "reason", "validated_claims")})
                    self.assertEqual(package["reviewer_action"],
                        "Human review required; no approval, reservation or delivery promise")
                    ai = {"configuration": state["m20_ai_results"]["configuration"],
                        "pricing": state["typed_final_results"]["pricing"],
                        **state["m21_ai_results"]}
                    self.assertEqual(set(ai) | {"fulfillment"}, set(SPECIALISTS))
                    for domain, result in ai.items():
                        with self.subTest(case=case_id, variant=credit_variant,
                                binding=binding, specialist=domain):
                            if domain != "pricing":
                                self.assertEqual(result["subject_id"], original_id)
                            else:
                                self.assertEqual(package["typed_final_ai"]["subject_id"],
                                    original_id)
                                self.assertEqual(package["typed_final_ai"][
                                    "validated_claims"], result["validated_claims"])
                            self.assertEqual(result["execution"], "abstained" if
                                domain == "credit" and credit_variant == "UC02" else
                                "completed")
                            records = {row["ref"]: row["fields"] for event in state[
                                "tool_access_ledger"] if event["status"] == "completed"
                                and event["identity"]["specialist"] == domain
                                for row in event["result"].get("records", []) if
                                "ref" in row and row["ref"] in event["returned_refs"]}
                            for claim in result["validated_claims"]:
                                self.assertIn(claim["ref"], records)
                                self.assertIn(claim["field"], records[claim["ref"]])
                                value = records[claim["ref"]][claim["field"]]
                                self.assertIs(type(claim["value"]), type(value))
                                self.assertEqual(claim["value"], value)
                    self.assertEqual(package["m21_ai"]["specialists"], {name: {
                        "execution": result["execution"], "reason": result["reason"],
                        "validated_claims": result["validated_claims"]}
                        for name, result in state["m21_ai_results"].items()})
                    self.assertEqual(state["candidate_status"],
                        "fixed_checked" if binding else "not_started")
                    if case_id == "N01":
                        self.assertEqual(state.get("candidate_records", {}), {})
                        self.assertEqual(state["reviewer_package"].get("candidates", []), [])
                        self.assertEqual(state["m21_review"]["subject_id"], "M18-D-N01")
                    if binding:
                        candidate = next(iter(state["candidate_records"].values()))
                        self.assertEqual(candidate["fixed_supply_status"],
                                         "supply_supported_unreserved")
                        self.assertEqual({v["subject_id"] for v in candidate[
                            "specialist_results"].values()}, {candidate["candidate_id"]})
                        self.assertEqual(state["reviewer_package"]["candidates"][0][
                            "customer_acceptance"], "pending")
                        self.assertFalse(state["reviewer_package"]["candidates"][0][
                            "routing"]["eligible_for_ordinary_routing"])
                    self.assertEqual(state["ai_fulfillment_result"]["execution"], "completed")
                    self.assertEqual(state["typed_final_results"]["pricing"]["execution"],
                                     "completed")
                    self.assertEqual({name: row["execution"] for name, row in
                        state["m21_ai_results"].items()}, {name: (
                            "abstained" if name == "credit" and credit_variant == "UC02"
                            else "completed") for name in TOOLS})
                    if credit_variant == "UC02":
                        self.assertEqual(state["m21_ai_results"]["credit"][
                            "validated_claims"], [])
                        self.assertEqual(state["m21_ai_results"]["credit"][
                            "reason"], "insufficient_evidence")
                    elif credit_variant:
                        self.assertEqual({c["field"] for c in state[
                            "m21_ai_results"]["credit"]["validated_claims"]},
                            {"credit_status", "outstanding_amount", "paid_amount"})
                    self.assertEqual(state["m21_review"]["assessment_id"],
                                     config["configurable"]["thread_id"])
                    self.assertEqual(state["m21_review"]["subject_id"],
                                     state["context"]["original_deal_id"])
                    self.assertEqual({v["subject_id"] for v in state[
                        "m21_ai_results"].values()}, {state["context"]["original_deal_id"]})
                    if binding:
                        self.assertEqual(state["reviewer_package"]["m21_ai"],
                                         state["m21_review"])
                        self.assertEqual({domain for domain, _, _ in model_visibility},
                                         set(TOOLS))
                        self.assertTrue(all(subject.startswith("subject:") and not visible
                            for _, subject, visible in model_visibility), msg=model_visibility)
                        self.assertEqual(len({subject for _, subject, _ in model_visibility}), 1)
                        self.assertEqual(json.loads((root / "m21-manifest.json").read_text())[
                            "candidate_context"]["candidate_id"], candidate["candidate_id"])
                        from copy import deepcopy
                        forged = deepcopy(state)
                        forged["candidate_records"][candidate["candidate_id"]][
                            "fixed_decision_sha256"] = "0" * 64
                        with self.assertRaises(EvidenceMismatch):
                            checked_candidate_context(forged)
                        forged = deepcopy(state)
                        forged["candidate_records"][candidate["candidate_id"]][
                            "specialist_results"]["credit"]["subject_id"] = "M18-D-B01"
                        with self.assertRaises(EvidenceMismatch):
                            checked_candidate_context(forged)
                        forged = deepcopy(state)
                        forged["reviewer_package"]["candidates"][0][
                            "routing"]["eligible_for_ordinary_routing"] = True
                        with self.assertRaises(EvidenceMismatch):
                            checked_candidate_context(forged)
                        forged = deepcopy(state)
                        forged["reviewer_package"]["typed_final_ai"]["subject_id"] = (
                            candidate["candidate_id"])
                        with self.assertRaises(EvidenceMismatch):
                            checked_candidate_context(forged)
                        forged = deepcopy(state)
                        forged["reviewer_package"]["configuration_ai"][
                            "validated_claims"] = []
                        with self.assertRaises(EvidenceMismatch):
                            checked_candidate_context(forged)
                        from dealdesk_phase2.m21_specialists import _validate_m21_start
                        with self.assertRaises(EvidenceMismatch):
                            _validate_m21_start(graph, config, self.adapter)
                        self.assertEqual(state["reviewer_package"]["candidates"][0][
                            "customer_acceptance"], "pending")
                    self.assertEqual(len(calls), 12)
                approved_manifest = json.loads((root / "m21-manifest.json").read_text())
                with thesis_checkpointer(dedicated) as saver:
                    restarted = build_original_graph(self.adapter, self.connect, saver)
                    with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1",
                            "GROQ_SECONDARY_API_KEY": "gsk_offline_test_placeholder_123456789"}), patch(
                            "dealdesk_phase2.m21_groq_contract._post",
                            side_effect=AssertionError("terminal assessment replayed")) as sender:
                        resumed = run_m21_evaluation(restarted, config, self.adapter,
                            models(), manifest=approved_manifest,
                            approved_manifest_sha256=digest(approved_manifest),
                            authorized=True, owner_dir=root / "owner",
                            free_tier_billing_disabled=True,
                            development_selection=tuple(TOOLS))
                    sender.assert_not_called()
                    for field in ("candidate_records", "specialist_results",
                            "m20_ai_results", "typed_final_results", "m21_ai_results",
                            "m21_model_attempts", "m21_review", "reviewer_package",
                            "tool_access_ledger"):
                        self.assertEqual(resumed[field], state[field], msg=field)
                    self.assertEqual(capture_m22(resumed, self.adapter), projected)
        finally:
            with psycopg.connect(admin, autocommit=True) as db:
                db.execute("DROP DATABASE " + name)

    def test_standing_full_typed_credit_six_sends_and_no_replay(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        from dealdesk_phase2.typed_final_contract import VERSION as FINAL_VERSION
        from run_groq_development import _m21_campaign
        name = "dev_full_m21_" + uuid4().hex[:16]
        parts = psycopg.conninfo.conninfo_to_dict(self.checkpoint)
        admin = psycopg.conninfo.make_conninfo(**{**parts, "dbname": "postgres"})
        dedicated = psycopg.conninfo.make_conninfo(**{**parts, "dbname": name})
        with psycopg.connect(admin, autocommit=True) as db:
            db.execute("CREATE DATABASE " + name)
        try:
            with TemporaryDirectory(dir="/tmp/opencode") as directory:
                root = Path(directory)
                root.chmod(0o700)
                owner = root / "owner"
                owner.mkdir(mode=0o700)
                with thesis_checkpointer(dedicated) as saver:
                    graph, config, before, _ = self.original(saver)
                    bodies = []
                    def fake_post(url, key, header, body, **kwargs):
                        bodies.append(body)
                        public = json.loads(body["messages"][1]["content"])["input"]
                        if "response_format" in body:
                            self.assertEqual(public["specialist"], "credit")
                            self.assertNotIn("tools", body)
                            visible = json.loads(body["messages"][1]["content"])[
                                "observations"]
                            claim = visible[0]["records"][0]
                            field, value = next(iter(claim["fields"].items()))
                            return {"usage": {"prompt_tokens": 400,
                                "completion_tokens": 80}, "choices": [{
                                "finish_reason": "stop", "message": {"content": json.dumps({
                                    "version": FINAL_VERSION, "kind": "finding",
                                    "claims": [{"ref": claim["ref"], "field": field,
                                        "value_json": json.dumps(value)}],
                                    "uncertainty_reasons": [], "reason_code": "none"})}}]}
                        if len(body["messages"]) == 2:
                            return response(TOOLS[public["specialist"]],
                                {"subject_id": public["subject_id"]})
                        return response("abstain", {"reason_code": "model_uncertainty"})
                    with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                            "dealdesk_phase2.m21_groq_contract._post",
                            side_effect=fake_post) as sender:
                        digest, state = _m21_campaign(graph, config, self.adapter,
                            case_id="B01", owner=owner, root=root,
                            key="gsk_offline_test_placeholder_123456789",
                            typed_credit=True)
                        self.assertEqual(sender.call_count, 6)
                        self.assertEqual(set(state["m21_ai_results"]), set(TOOLS))
                        self.assertEqual(state["m21_ai_results"]["credit"]["execution"],
                                         "completed")
                        self.assertEqual(state["specialist_results"],
                                         before["specialist_results"])
                        self.assertEqual(state["m21_review"]["assessment_id"],
                                         config["configurable"]["thread_id"])
                        with patch.dict(os.environ, {"GROQ_SECONDARY_API_KEY":
                                "gsk_offline_test_placeholder_123456789"}):
                            again = run_m21_evaluation(graph, config, self.adapter,
                                models(), manifest=json.loads((root /
                                    "manifest.json").read_text()),
                                approved_manifest_sha256=digest, authorized=True,
                                owner_dir=owner, free_tier_billing_disabled=True,
                                development_selection=tuple(TOOLS))
                        self.assertEqual(again["m21_review"], state["m21_review"])
                        self.assertEqual(sender.call_count, 6)
        finally:
            with psycopg.connect(admin, autocommit=True) as db:
                db.execute("DROP DATABASE " + name)

    def test_standing_policy_routing_without_credit_and_no_replay(self):
        """Fresh checkpoint, trusted fixture; no incomplete campaign handoff."""
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        from run_groq_development import _m21_campaign
        name = "dev_policy_route_" + uuid4().hex[:16]
        parts = psycopg.conninfo.conninfo_to_dict(self.checkpoint)
        admin = psycopg.conninfo.make_conninfo(**{**parts, "dbname": "postgres"})
        dedicated = psycopg.conninfo.make_conninfo(**{**parts, "dbname": name})
        with psycopg.connect(admin, autocommit=True) as db:
            db.execute("CREATE DATABASE " + name)
        try:
            with TemporaryDirectory(dir="/tmp/opencode") as directory:
                root = Path(directory)
                root.chmod(0o700)
                owner = root / "owner"
                owner.mkdir(mode=0o700)
                with thesis_checkpointer(dedicated) as saver:
                    graph, config, before, _ = self.original(saver)
                    bodies = []
                    def fake_post(url, key, header, body, **kwargs):
                        bodies.append(body)
                        domain = json.loads(body["messages"][1]["content"])["input"][
                            "specialist"]
                        if len(body["messages"]) == 2:
                            public = json.loads(body["messages"][1]["content"])["input"]
                            return response(TOOLS[domain], {"subject_id": public["subject_id"]})
                        return response("abstain", {"reason_code": "model_uncertainty"})
                    with patch.dict(os.environ, {"DEALDESK_GROQ_DEV_ENABLE": "1"}), patch(
                            "dealdesk_phase2.m21_groq_contract._post",
                            side_effect=fake_post) as sender:
                        digest, state = _m21_campaign(graph, config, self.adapter,
                            case_id="B01", owner=owner, root=root,
                            key="gsk_offline_test_placeholder_123456789",
                            policy_routing_only=True)
                        self.assertEqual(sender.call_count, 4)
                        self.assertEqual(set(state["m21_ai_results"]),
                                         {"policy", "approval_routing"})
                        self.assertFalse(state.get("m21_review"))
                        self.assertEqual(state["specialist_results"],
                                         before["specialist_results"])
                        with self.assertRaises((ValueError, FileExistsError)):
                            _m21_campaign(graph, config, self.adapter, case_id="B01",
                                owner=owner, root=root,
                                key="gsk_offline_test_placeholder_123456789",
                                policy_routing_only=True)
                        self.assertEqual(sender.call_count, 4)
                        self.assertEqual(len(digest), 64)
        finally:
            with psycopg.connect(admin, autocommit=True) as db:
                db.execute("DROP DATABASE " + name)

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
                    from dealdesk_phase2.m22_capture import capture_m22
                    observed = capture_m22(graph.get_state(config).values, self.adapter)
                    self.assertEqual(observed["evaluation_status"], "stopped_or_incomplete")
                    self.assertEqual(observed["ai_original"]["credit"]["execution"],
                                     "error")
                    self.assertEqual(observed["ai_original"]["credit"][
                        "validated_claims"], [])
                    self.assertEqual(observed["request_count"], 1)
                    self.assertEqual(observed["returned_count"], 0)
                    self.assertEqual(observed["receipt_verification"], "not_checked")
                    self.assertIsNone(observed["attempts"][-1]["tokens"])
                    self.assertIsNone(observed["attempts"][-1]["elapsed_ms"])

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
