"""PostgreSQL-only proof of persisted deterministic execution output."""

import json
import os
from copy import deepcopy
from pathlib import Path
from uuid import UUID
import unittest

import yaml

from phase1c_development_runtime import execute_development_run, _known_evidence
from phase1c_reader import read_run
from phase1c_deal_decision import assemble_deal_decision
from validate_phase1c_runtime_outputs import validate_execution_rows


HERE = Path(__file__).resolve().parent
CONTRACT = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
SOURCE_RUN = UUID("00000000-0000-4000-8000-000000010001")
TEST_RUN = UUID("a85b1c01-0000-4000-8000-000000000001")


@unittest.skipUnless(os.environ.get("DATABASE_URL"), "PostgreSQL integration requires DATABASE_URL")
class DevelopmentRuntimeTests(unittest.TestCase):
    def setUp(self):
        import psycopg
        from psycopg.rows import dict_row
        self.conn = psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
        self.conn.execute("SET search_path TO deal_desk, public")
        self.conn.execute("""INSERT INTO deal_desk.deal_runs
            (run_id, deal_id, original_policy_set_code, applied_policy_set_code,
             catalog_version_used, as_of_at, data_snapshot_ref, input_snapshot_json,
             config_hash, run_status, started_at)
            SELECT %s, deal_id, original_policy_set_code, applied_policy_set_code,
                   catalog_version_used, as_of_at, data_snapshot_ref, input_snapshot_json,
                   config_hash, 'running', as_of_at + interval '1 second'
            FROM deal_desk.deal_runs WHERE run_id = %s""", (TEST_RUN, SOURCE_RUN))
        self.assertEqual(self.conn.execute("SELECT count(*) FROM deal_desk.deal_runs WHERE run_id = %s", (TEST_RUN,)).fetchone()["count"], 1)

    def tearDown(self):
        self.conn.rollback()
        self.conn.close()

    def test_actual_reader_decision_and_seven_persisted_envelopes(self):
        result = execute_development_run(self.conn, TEST_RUN, CONTRACT)
        self.assertEqual(result["rows"], 7)
        self.assertEqual(result["engine"], "deterministic_development")
        stored = self.conn.execute("""SELECT run_id, agent_name, attempt_number, status,
            input_snapshot_json, output_json, deal_id, applied_policy_set_code,
            catalog_version_used, model_name FROM deal_desk.agent_execution_log
            WHERE run_id = %s ORDER BY execution_id""", (TEST_RUN,)).fetchall()
        self.assertEqual([x["agent_name"] for x in stored],
                         ["Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval", "Orchestrator"])
        bundle = read_run(self.conn, TEST_RUN, commercial_rule_mode="compiled")
        decision = assemble_deal_decision(bundle)
        report = validate_execution_rows(stored, CONTRACT,
                                         known_evidence=_known_evidence(bundle))
        self.assertEqual(report["errors"], [])
        invented = deepcopy(stored)
        invented[2]["output_json"]["findings"][0]["evidence_refs"].append("INVENTED-SUPPLY-ID")
        self.assertTrue(any("unknown evidence INVENTED-SUPPLY-ID" in error for error in
                            validate_execution_rows(invented, CONTRACT,
                                                    known_evidence=_known_evidence(bundle))["errors"]))
        self.assertEqual({x["input_snapshot_json"]["config_hash"] for x in stored},
                         {bundle["run"]["config_hash"]})
        self.assertTrue(all(x["deal_id"] == bundle["deal"]["deal_id"] and
                            x["applied_policy_set_code"] == bundle["run"]["applied_policy_set_code"] and
                            x["catalog_version_used"] == bundle["run"]["catalog_version_used"] and
                            x["model_name"] is None for x in stored))
        self.assertEqual(self.conn.execute("SELECT run_status FROM deal_desk.deal_runs WHERE run_id = %s", (TEST_RUN,)).fetchone()["run_status"], "completed")
        if os.environ.get("PHASE1C_RUNTIME_REPORT"):
            Path(os.environ["PHASE1C_RUNTIME_REPORT"]).write_text(json.dumps({
                "run_id": str(TEST_RUN), "source_run_id": str(SOURCE_RUN),
                "engine": result["engine"], "decision_status": result["decision_status"],
                "stored_agents": [x["agent_name"] for x in stored],
                "typed_validation_errors": report["errors"], "run_status": "completed",
                "model_execution_claimed": False, "accepted_evaluation_answers": 0,
                "transaction_committed": False}, indent=2) + "\n")
        with self.assertRaisesRegex(ValueError, "queued/running"):
            execute_development_run(self.conn, TEST_RUN, CONTRACT)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM deal_desk.agent_execution_log WHERE run_id = %s", (TEST_RUN,)).fetchone()["count"], 7)

    def test_invalid_contract_fails_before_any_write(self):
        bad = {**CONTRACT, "controlled_vocabularies": {**CONTRACT["controlled_vocabularies"], "agent_names": []}}
        with self.assertRaisesRegex(ValueError, "Invalid runtime output"):
            execute_development_run(self.conn, TEST_RUN, bad)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM deal_desk.agent_execution_log WHERE run_id = %s", (TEST_RUN,)).fetchone()["count"], 0)
        self.assertEqual(self.conn.execute("SELECT run_status FROM deal_desk.deal_runs WHERE run_id = %s", (TEST_RUN,)).fetchone()["run_status"], "running")


if __name__ == "__main__":
    unittest.main()
