"""Fresh, rollback-only PostgreSQL replay of separate Credit controls 040–041."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

from test_phase1c_evaluation_cases import TABLE_ORDER

try:
    import psycopg
    from psycopg import sql
    from psycopg.types.json import Jsonb
except ImportError:
    psycopg = None

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent / "evaluation"


@unittest.skipUnless(psycopg is not None and os.environ.get("EVALUATION_DATABASE_URL"),
                     "Dedicated empty PostgreSQL database required")
class CreditControlDatabaseTests(unittest.TestCase):
    def test_isolated_reader_replay_and_fail_closed_projection(self):
        from credit_evidence_gate import (CONTROL, INDEX, classify_selected_packet,
                                          canonical)
        from phase1c_reader import read_run, load_provider_evidence
        from phase1c_evaluation_input import (prepare_heldout_review_input,
                                               review_source_digest, verify_review_input)
        from validate_phase1c_generated_rows import load_rows, validate_rows
        import yaml

        source_bytes, index_bytes = CONTROL.read_bytes(), INDEX.read_bytes()
        packet_index_bytes = (EVAL / "credit-evidence-v3/control_packet_index_v1.json").read_bytes()
        source, index = json.loads(source_bytes), json.loads(index_bytes)
        self.assertEqual(sha256(source_bytes).hexdigest(), index["control_source_sha256"])
        base = json.loads((EVAL / "provisional_packet_index.json").read_text())
        self.assertEqual(base["source_definition_sha256"], source["base_v2_source_definition_sha256"])
        contract = json.loads((EVAL / "provisional_cases.json").read_text())["business_contract"]
        development = json.loads((HERE / "phase1c_development_source_exclusions.json").read_text())
        historical = json.loads((HERE / "phase1c_historical_source_exclusions.json").read_text())
        row_contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        output = Path(os.environ.get("PHASE1C_CREDIT_PACKETS", tempfile.mkdtemp(prefix="phase1c-credit-")))
        output.mkdir(parents=True, exist_ok=True)
        with psycopg.connect(os.environ["EVALUATION_DATABASE_URL"]) as conn:
            conn.execute("SET search_path TO deal_desk, public")
            self.assertEqual(conn.execute("SELECT count(*) FROM deals").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT count(*) FROM agent_execution_log").fetchone()[0], 0)
            for name in ("phase1c_buildable_master.sql", "phase1c_sellable_catalogue.sql"):
                for statement in re.findall(r"^INSERT INTO .*?;", (HERE / name).read_text(), re.M | re.S):
                    conn.execute(statement)
            for case, pin in zip(source["cases"], index["controls"]):
                cid = case["case_id"]
                with self.subTest(case=cid), conn.transaction(force_rollback=True):
                    self.assertEqual(pin["case_id"], cid)
                    self.assertEqual(pin["source_sha256"], sha256(canonical(case).encode()).hexdigest())
                    for table in (*TABLE_ORDER, "accounts_receivable", "payment_history"):
                        for row in case["tables"].get(table, []):
                            if table == "deal_runs":
                                conn.execute("UPDATE deals SET deal_status='Submitted' WHERE deal_id=%s", (row["deal_id"],))
                            conn.execute(sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                                sql.Identifier(table), sql.SQL(",").join(map(sql.Identifier, row)),
                                sql.SQL(",").join(sql.Placeholder() for _ in row)),
                                [Jsonb(value) if isinstance(value, (dict, list)) else value for value in row.values()])
                    conn.execute("SET CONSTRAINTS ALL IMMEDIATE")
                    self.assertEqual(validate_rows(load_rows(conn), row_contract)["errors"], [])
                    provider_bytes = (json.dumps(case["provider_manifest"], sort_keys=True, indent=2) + "\n").encode()
                    with tempfile.TemporaryDirectory() as temp:
                        provider_path = Path(temp) / "provider.json"
                        provider_path.write_bytes(provider_bytes)
                        resolver = load_provider_evidence(provider_path)
                        def prepare():
                            bundle = read_run(conn, case["tables"]["deal_runs"][0]["run_id"],
                                              commercial_rule_mode="compiled", digital_evidence_resolver=resolver)
                            packet = prepare_heldout_review_input(
                                bundle, case_id=cid, development_manifest=development,
                                historical_manifest=historical, business_contract=contract)
                            verify_review_input(packet, expected_case_id=cid,
                                                expected_source_digest=review_source_digest(bundle, contract),
                                                expected_business_contract=contract)
                            return packet
                        packet = prepare()
                        self.assertEqual(packet, prepare())
                    state = classify_selected_packet(source_bytes, index_bytes, cid, packet,
                                                     provider_bytes=provider_bytes,
                                                     packet_index_bytes=packet_index_bytes)
                    self.assertTrue(state["selection_verified"])
                    self.assertFalse(state["credit_clearance_allowed"])
                    selected = packet["payload"]["source_rows"]
                    self.assertEqual(len(selected["receivables"]), 1 if cid.endswith("040") else 0)
                    self.assertEqual(len(selected["payments"]), 1 if cid.endswith("040") else 0)
                    if cid.endswith("040"):
                        self.assertEqual(state["overdue_ar_eur"], "700.00")
                        self.assertEqual(selected["receivables"][0]["outstanding_amount"], "700.00")
                        self.assertEqual(selected["payments"][0]["paid_amount"], "300.00")
                    else:
                        self.assertEqual(state["source_evidence_state"], "unknown_incomplete")
                        self.assertIsNone(state["overdue_ar_eur"])
                    (output / (cid + ".json")).write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n")
                    (output / (cid + "-provider.json")).write_bytes(provider_bytes)
                    for mutation in ("seal", "rows", "identity", "provider"):
                        changed = deepcopy(packet)
                        proof = provider_bytes
                        if mutation == "seal":
                            changed["sha256"] = "0" * 64
                        elif mutation == "rows":
                            changed["payload"]["source_rows"]["receivables"] = [] if cid.endswith("040") else [
                                {"customer_id": case["tables"]["customers"][0]["customer_id"]}]
                            changed["sha256"] = sha256(json.dumps(changed["payload"], sort_keys=True,
                                                            separators=(",", ":")).encode()).hexdigest()
                        elif mutation == "identity":
                            changed["payload"]["run_context"]["data_snapshot_ref"] = "SWAPPED"
                        else:
                            proof = b'{"records":[{"spoofed":true}],"schema_version":1}'
                        with self.assertRaises(ValueError):
                            classify_selected_packet(source_bytes, index_bytes, cid, changed,
                                                     provider_bytes=proof, packet_index_bytes=packet_index_bytes)
                    if cid.endswith("040"):
                        with conn.transaction(force_rollback=True):
                            conn.execute("UPDATE accounts_receivable SET outstanding_amount=650 WHERE customer_id=%s",
                                         (case["tables"]["customers"][0]["customer_id"],))
                            altered = read_run(conn, case["tables"]["deal_runs"][0]["run_id"],
                                               commercial_rule_mode="compiled", digital_evidence_resolver=resolver)
                            mutated = prepare_heldout_review_input(
                                altered, case_id=cid, development_manifest=development,
                                historical_manifest=historical, business_contract=contract)
                            with self.assertRaises(ValueError):
                                classify_selected_packet(source_bytes, index_bytes, cid, mutated,
                                                         provider_bytes=provider_bytes,
                                                         packet_index_bytes=packet_index_bytes)
                    with self.assertRaises(ValueError):
                        classify_selected_packet(source_bytes, index_bytes, cid, packet,
                                                 provider_bytes=provider_bytes,
                                                 packet_index_bytes=packet_index_bytes.replace(
                                                     b"postgresql_replayed", b"unverified_replayed"))
                    self.assertEqual(conn.execute("SELECT count(*) FROM agent_execution_log").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT count(*) FROM deals").fetchone()[0], 0)
            conn.rollback()


if __name__ == "__main__":
    unittest.main()
