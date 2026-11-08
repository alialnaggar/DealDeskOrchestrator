"""Authenticated HTTP integration with genuinely executed offline LangGraph stages."""

import os
from pathlib import Path
from time import monotonic, sleep
import unittest
from unittest.mock import patch
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient
import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from dealdesk_phase2.assessment_api import create_app, create_app_from_env
from dealdesk_phase2 import assessment_service
from dealdesk_phase2.assessment_service import AssessmentService
from dealdesk_phase2.checkpoint import thesis_checkpointer
from m18_case_setup import install_disposable_cases
from m21_integrated_credit_setup import install_integrated_credit


class StartupGuards(unittest.TestCase):
    def test_reject_unmatched_database_pair_before_connection(self):
        with patch.dict(os.environ, {
                "DEALDESK_DEMO_TOKEN": "x"*40,
                "DEALDESK_DEMO_OWNER": "operator",
                "DEALDESK_DEMO_BUSINESS_DSN": "host=/tmp/opencode dbname=shared_database",
                "DEALDESK_DEMO_CHECKPOINT_DSN": "host=/tmp/opencode dbname=other_database",
                "DEALDESK_PHASE1C_CHECKOUT": "/tmp/opencode/dealdesk-phase1c-pinned"}):
            with self.assertRaisesRegex(ValueError, "matching demo fixture"):
                create_app_from_env()


@unittest.skipUnless(all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh disposable M2.0 business and pinned Phase 1C required")
class OfflineAssessmentAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parts = conninfo_to_dict(os.environ["M20_DATABASE_URL"])
        if not (parts["host"] == "/tmp/opencode" or
                os.environ.get("GITHUB_ACTIONS") == "true" and
                parts["host"] == "localhost" and
                parts["dbname"] == "deal_desk_m20_ai"):
            raise ValueError("Fresh disposable local or CI fixture required")
        cls.admin = make_conninfo(**{**parts, "dbname": "postgres"})
        cls.business_name = "api_business_" + uuid4().hex[:12]
        cls.check_name = "api_checkpoint_" + uuid4().hex[:12]
        with psycopg.connect(cls.admin, autocommit=True) as db:
            db.execute(sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(
                sql.Identifier(cls.business_name), sql.Identifier(parts["dbname"])))
            db.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(cls.check_name)))
        cls.business = make_conninfo(**{**parts, "dbname": cls.business_name})
        cls.checkpoint = make_conninfo(**{**parts, "dbname": cls.check_name})
        with psycopg.connect(cls.business) as db:
            present = db.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id='M18-D-B01'").fetchone()[0]
        if not present:
            with psycopg.connect(cls.business) as db:
                install_disposable_cases(db)
        for case, variant in (("B01", "RC01"), ("N01", "UC02")):
            with psycopg.connect(cls.business) as db:
                install_integrated_credit(db, case_id=case, variant=variant)
        with psycopg.connect(cls.checkpoint) as db:
            db.execute((Path(__file__).parents[1] / "migrations" /
                "001_demo_assessment_registry.sql").read_text())
        cls.service = AssessmentService(cls.business, cls.checkpoint,
            Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        cls.alice = "a" * 40
        cls.bob = "b" * 40
        cls.app = create_app(cls.service, {cls.alice: "alice", cls.bob: "bob"})
        cls.client_context = TestClient(cls.app, base_url="http://127.0.0.1:8765")
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        with psycopg.connect(cls.admin, autocommit=True) as db:
            for name in (cls.check_name, cls.business_name):
                db.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(name)))

    def headers(self, token=None, key=None):
        return {"Authorization": "Bearer " + (token or self.alice),
                "Idempotency-Key": key or "key-" + uuid4().hex}

    def create(self, scenario):
        response = self.client.post("/demo/assessments", json={"scenario": scenario},
                                    headers=self.headers())
        self.assertEqual(response.status_code, 202, response.text)
        self.assertTrue(response.json()["created"])
        self.assertEqual(response.json()["status"], "accepted")
        return response.json()["assessment_id"]

    def completed(self, assessment_id, token=None):
        deadline = monotonic() + 45
        while monotonic() < deadline:
            response = self.client.get("/demo/assessments/" + assessment_id,
                headers=self.headers(token))
            self.assertEqual(response.status_code, 200)
            if response.json()["status"] != "running" and response.json()["status"] != "accepted":
                return response.json()
            sleep(.1)
        self.fail("Offline assessment did not finish")

    def test_authentication_idempotency_and_owner_boundary(self):
        self.assertEqual(self.client.get("/demo/assessments/" + "a" * 32).status_code, 401)
        for suffix in ("/events", "/review"):
            self.assertEqual(self.client.get("/demo/assessments/" + "a"*32 + suffix
                ).status_code, 401)
        self.assertEqual(self.client.post("/demo/assessments", json={"scenario": "B01/RC01"},
            headers={"Idempotency-Key": "key-12345678"}).status_code, 401)
        key = "key-" + uuid4().hex
        headers = self.headers(key=key)
        first = self.client.post("/demo/assessments", json={"scenario": "N01/UC02"},
            headers=headers)
        self.assertEqual(first.status_code, 202, first.text)
        ident = first.json()["assessment_id"]
        second = self.client.post("/demo/assessments", json={"scenario": "N01/UC02"},
            headers=headers)
        self.assertEqual(second.json()["assessment_id"], ident)
        self.assertFalse(second.json()["created"])
        self.assertEqual(self.client.post("/demo/assessments", json={"scenario": "B01/RC01"},
            headers=headers).status_code, 409)
        for suffix in ("", "/events", "/review"):
            self.assertEqual(self.client.get("/demo/assessments/" + ident + suffix,
                headers=self.headers(self.bob)).status_code, 404)
        self.assertEqual(self.completed(ident)["status"], "completed")

    def test_simultaneous_same_key_is_single_run_and_owner_scoped(self):
        key = "same-" + uuid4().hex
        def submit(token, scenario="N01/UC02"):
            return self.client.post("/demo/assessments", json={"scenario": scenario},
                                    headers=self.headers(token, key))
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: submit(self.alice), range(12)))
        self.assertEqual([r.status_code for r in results], [202] * 12)
        ids = {r.json()["assessment_id"] for r in results}
        self.assertEqual(len(ids), 1)
        self.assertEqual(sum(r.json()["created"] for r in results), 1)
        ident = ids.pop()
        self.assertEqual(self.completed(ident)["status"], "completed")
        with ThreadPoolExecutor(max_workers=4) as pool:
            conflicts = list(pool.map(lambda _: submit(self.alice, "B01/RC01"), range(4)))
        self.assertEqual([r.status_code for r in conflicts], [409] * 4)
        other = submit(self.bob)
        self.assertEqual(other.status_code, 202)
        self.assertNotEqual(other.json()["assessment_id"], ident)
        self.assertEqual(self.completed(other.json()["assessment_id"], self.bob)["status"], "completed")
        self.assertEqual(self.client.get(f"/demo/assessments/{ident}",
                         headers=self.headers(self.bob)).status_code, 404)
        with self.service.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM dealdesk_demo.assessments "
                "WHERE idempotency_key=%s", (key,)).fetchone()["count"], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM dealdesk_demo.assessment_events "
                "WHERE assessment_id=%s AND kind='accepted'", (ident,)).fetchone()["count"], 1)

    def test_invalid_identifiers_host_queries_and_database_outage_are_sanitized(self):
        bad_host = self.client.get("/demo/assessments/"+"a"*32,
            headers={**self.headers(), "Host": "evil.invalid"})
        self.assertEqual(bad_host.status_code, 400)
        self.assertEqual(bad_host.headers["cache-control"], "no-store")
        for bad in ("NOT-HEX", "f"*33, "..%2Fprivate", "' OR 1=1 --"):
            response = self.client.get("/demo/assessments/" + bad,
                headers=self.headers())
            self.assertEqual(response.status_code, 404, response.text)
        for after in ("-1", "not-an-integer", "9223372036854775808"):
            response = self.client.get("/demo/assessments/" + "f"*32 +
                "/events?after=" + after, headers=self.headers())
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post("/demo/assessments", json={"scenario": "N01/UC02"},
            headers=self.headers(key="invalid key")).status_code, 422)
        private = "password=DO-NOT-LEAK"
        with patch.object(self.service.store, "connect",
                side_effect=psycopg.OperationalError(private)):
            for path in ("/demo/assessments/"+"f"*32, "/demo/assessments"):
                response = (self.client.get(path, headers=self.headers()) if
                    path.endswith("f"*32) else self.client.post(path,
                    json={"scenario": "N01/UC02"}, headers=self.headers()))
                self.assertEqual(response.status_code, 503)
                self.assertNotIn(private, response.text)
                self.assertEqual(response.headers["cache-control"], "no-store")
        ident = self.create("N01/UC02")
        self.assertEqual(self.completed(ident)["status"], "completed")

    def test_allowlist_request_limits_and_actual_rc01_progress(self):
        with self.service._connect_business() as db:
            self.assertEqual(db.execute("SHOW transaction_read_only").fetchone()[0], "on")
        for body in ({"scenario": "B05/RC01"}, {"scenario": "B01/RC01", "dsn": "other"}):
            self.assertEqual(self.client.post("/demo/assessments", json=body,
                headers=self.headers()).status_code, 422)
        rejected = self.client.post("/demo/assessments", json={"scenario": "B01/RC01",
            "provider_key": "PRIVATE-NOT-TO-ECHO"}, headers=self.headers())
        self.assertEqual(rejected.status_code, 422)
        self.assertNotIn("PRIVATE-NOT-TO-ECHO", rejected.text)
        self.assertEqual(self.client.post("/demo/assessments", content="x"*1024,
            headers=self.headers()).status_code, 413)
        with patch("dealdesk_phase2.live_models._post", side_effect=AssertionError("hosted")), patch(
                "dealdesk_phase2.m21_groq_contract._post", side_effect=AssertionError("hosted")):
            ident = self.create("B01/RC01")
            status = self.completed(ident)
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["mode"], "offline_scripted")
        self.assertNotIn("customer_id", str(status))
        events = self.client.get(f"/demo/assessments/{ident}/events",
            headers=self.headers()).json()["events"]
        self.assertEqual([e["sequence"] for e in events], list(range(1, len(events)+1)))
        self.assertEqual(events[0]["kind"], "accepted")
        self.assertEqual(events[-1]["kind"], "review_ready")
        self.assertEqual(sum(e["kind"] == "fixed_completed" for e in events), 6)
        self.assertEqual(sum(e["kind"] == "ai_completed" for e in events), 6)
        self.assertIn("candidate", [e["stage"] for e in events if e["kind"] == "checkpoint"])
        self.assertTrue(all("occurred_at" in e and set(e) == {
            "assessment_id", "sequence", "occurred_at", "kind", "stage"} for e in events))
        later = self.client.get(f"/demo/assessments/{ident}/events?after=10",
            headers=self.headers()).json()["events"]
        self.assertEqual(later[0]["sequence"], 11)
        review = self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers())
        self.assertEqual(review.status_code, 200, review.text)
        result = review.json()
        self.assertEqual([(s["quantity"], s["delivery_date"]) for s in
            result["candidate_comparison"]["proposed_slices"]],
            [(8, "2026-09-03"), (2, "2026-09-08")])
        self.assertEqual(result["candidate_comparison"]["fixed_supply_status"],
                         "supply_supported_unreserved")
        self.assertEqual(result["candidate_comparison"]["customer_acceptance"], "pending")
        self.assertEqual(result["candidate"]["business_status"], "needs_revision")
        self.assertIsNone(result["candidate"]["required_roles"])
        self.assertEqual(result["authorization"], "human_only_not_granted")
        for private in ("M21IC-INVOICE", "fixed_decision", "provider_receipt", "raw_model"):
            self.assertNotIn(private, review.text)
        with self.service.store.connect() as db:
            db.execute("UPDATE dealdesk_demo.assessments SET source_input_digest=%s WHERE assessment_id=%s",
                       ("forged", ident))
        self.assertEqual(self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers()).status_code, 409)

    def test_no_candidate_uncertain_restart_and_no_replay(self):
        ident = self.create("N01/UC02")
        self.assertEqual(self.completed(ident)["status"], "completed")
        response = self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsNone(response.json()["candidate_comparison"])
        self.assertTrue(any(r["verification"] == "suggested_unverified" for r in
            response.json()["recommendations"]))
        with thesis_checkpointer(self.service.checkpoint_dsn) as saver:
            graph = self.service._graph(saver)
            self.assertEqual(graph.get_state({"configurable": {"thread_id": ident}}).values[
                "assessment_id"], ident)
        lost, _ = self.service.create("alice", "key-"+uuid4().hex, "B01/RC01", lambda _:None)
        self.assertTrue(self.service.store.claim(lost))
        self.service.store.mark_interrupted()
        self.assertEqual(self.service.store.get("alice", lost)["status"], "uncertain")
        self.service.run(lost)
        self.assertEqual(self.service.store.get("alice", lost)["status"], "uncertain")
        self.assertEqual(self.client.get(f"/demo/assessments/{lost}/review",
            headers=self.headers()).status_code, 409)
        with self.service.store.connect() as db:
            with self.assertRaises(psycopg.Error):
                db.execute("DELETE FROM dealdesk_demo.assessment_events WHERE assessment_id=%s",
                           (lost,))

    def test_checkpoint_tampering_missing_state_and_stale_evidence(self):
        ident = self.create("N01/UC02")
        self.assertEqual(self.completed(ident)["status"], "completed")
        with psycopg.connect(self.business) as db:
            db.execute("UPDATE deal_desk.customer_credit_profiles SET credit_status='Active' "
                       "WHERE customer_id='M18-C-N01'")
        try:
            self.assertEqual(self.client.get(f"/demo/assessments/{ident}/review",
                headers=self.headers()).status_code, 409)
        finally:
            with psycopg.connect(self.business) as db:
                db.execute("UPDATE deal_desk.customer_credit_profiles SET credit_status='Review' "
                           "WHERE customer_id='M18-C-N01'")
        self.assertEqual(self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers()).status_code, 200)
        with thesis_checkpointer(self.service.checkpoint_dsn) as saver:
            graph = self.service._graph(saver)
            config = {"configurable": {"thread_id": ident}}
            context = dict(graph.get_state(config).values["context"])
            context["assessment_id"] = "forged"
            graph.update_state(config, {"context": context}, as_node="finish")
        self.assertEqual(self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers()).status_code, 409)
        self.assertEqual(self.client.get("/demo/assessments/" + "f"*32,
            headers=self.headers()).status_code, 404)
        missing, _ = self.service.create("alice", "key-" + uuid4().hex,
            "B01/RC01", lambda _: None)
        with self.service.store.connect() as db:
            db.execute("""UPDATE dealdesk_demo.assessments SET status='completed',
                bundle_sha256=%s,source_input_digest=%s WHERE assessment_id=%s""",
                ("0"*64, "0"*64, missing))
        self.assertEqual(self.client.get(f"/demo/assessments/{missing}/review",
            headers=self.headers()).status_code, 409)
        for suffix in ("", "/events"):
            self.assertEqual(self.client.get(f"/demo/assessments/{missing}" + suffix,
                headers=self.headers()).status_code, 409)

    def test_reserved_send_crash_is_uncertain_and_never_replayed(self):
        ident, _ = self.service.create("alice", "key-" + uuid4().hex,
            "N01/UC02", lambda _: None)
        original = assessment_service._OfflineSourceModel.next_action

        def interrupted(model, input, observations):
            if model.specialist == "credit":
                raise KeyboardInterrupt("synthetic process interruption")
            return original(model, input, observations)

        with patch.object(assessment_service._OfflineSourceModel, "next_action", interrupted):
            with self.assertRaises(KeyboardInterrupt):
                self.service.run(ident)
        with thesis_checkpointer(self.service.checkpoint_dsn) as saver:
            graph = self.service._graph(saver)
            state = graph.get_state({"configurable": {"thread_id": ident}}).values
            self.assertEqual(state["m21_model_attempts"][0]["status"], "reserved")
        self.service.store.mark_interrupted()
        self.assertEqual(self.service.store.get("alice", ident)["status"], "uncertain")
        self.service.run(ident)
        with thesis_checkpointer(self.service.checkpoint_dsn) as saver:
            graph = self.service._graph(saver)
            self.assertEqual(len(graph.get_state({"configurable": {
                "thread_id": ident}}).values["m21_model_attempts"]), 1)
        self.assertEqual(self.client.get(f"/demo/assessments/{ident}/review",
            headers=self.headers()).status_code, 409)
