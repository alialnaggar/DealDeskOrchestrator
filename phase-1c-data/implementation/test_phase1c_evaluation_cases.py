"""Check provisional author inputs without creating or scoring answer labels."""

from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import unittest

from render_phase1c_evaluation_cases import build_from_files, render, OUTPUT_DIR, HERE

try:
    import psycopg
    from psycopg import sql
    from psycopg.types.json import Jsonb
except ImportError:
    psycopg = None

FORBIDDEN = {"expected_decision", "expected_findings", "target_bucket", "historical_decision",
             "decision_reason", "approved_by_roles_json", "archetype_id", "score", "candidate_trace",
             "facts", "specialists", "observed_decision_status"}
TABLE_ORDER = ("customers", "customer_credit_profiles", "suppliers", "supplier_items",
               "purchase_orders", "inbound_supply", "inventory", "production_capacity",
               "digital_capacity", "shipping_lanes", "compatibility_rules", "deals", "deal_lines", "deal_runs")


def keys_in(value):
    if isinstance(value, dict):
        return set(value).union(*(keys_in(x) for x in value.values()))
    if isinstance(value, list):
        return set().union(*(keys_in(x) for x in value))
    return set()


class EvaluationAuthoringTests(unittest.TestCase):
    def test_reproducible_separate_36_source_cases(self):
        inputs, manifest = build_from_files()
        self.assertEqual(len(inputs["cases"]), 36)
        self.assertEqual(manifest["independently_reviewed_answers"], 0)
        self.assertEqual(sorted(Counter(x["archetype_id"] for x in manifest["cases"]).values()),
                         [2] * 18)
        self.assertEqual(len({x["case_id"] for x in inputs["cases"]}), 36)
        self.assertFalse(keys_in(inputs) & FORBIDDEN)
        self.assertTrue(all(not any(name.startswith(p) for p in ("phase1c_vertical", "phase1c_conflict", "phase1c_stress", "phase1c_historical"))
                            for name in manifest["source_sha256"]))
        for name, value in (("provisional_cases.json", inputs), ("provisional_authoring_manifest.json", manifest)):
            self.assertEqual((OUTPUT_DIR / name).read_text(), render(value))
        self.assertEqual(hashlib.sha256(render(inputs).encode()).hexdigest(), manifest["inputs_sha256"])
        pinned = json.loads((OUTPUT_DIR / "provisional_packet_index.json").read_text())
        self.assertEqual(pinned["input_case_count"], 36)
        self.assertEqual(pinned["independently_reviewed_answers"], 0)
        self.assertEqual(pinned["source_definition_sha256"], manifest["inputs_sha256"])
        self.assertEqual([row["case_id"] for row in pinned["cases"]],
                         [row["case_id"] for row in inputs["cases"]])
        self.assertFalse(keys_in(pinned) & FORBIDDEN)
        identities = set()
        for case in inputs["cases"]:
            self.assertEqual(set(case["tables"]) - set(TABLE_ORDER), set())
            deal = case["tables"]["deals"][0]
            self.assertEqual(deal["dataset_type"], "evaluation")
            self.assertNotIn(deal["deal_id"], identities)
            identities.add(deal["deal_id"])
            run = case["tables"]["deal_runs"][0]
            self.assertGreaterEqual(datetime.fromisoformat(run["as_of_at"]),
                                    datetime.fromisoformat(deal["submitted_at"]))
            self.assertEqual(run["deal_id"], deal["deal_id"])
            self.assertEqual(case["provider_manifest"]["schema_version"], 1)


@unittest.skipUnless(psycopg is not None and os.environ.get("EVALUATION_DATABASE_URL"),
                     "Dedicated disposable PostgreSQL database required")
class EvaluationDatabaseTests(unittest.TestCase):
    def test_reader_packets_reproduce_without_development_or_cross_case_sources(self):
        from phase1c_reader import read_run, load_provider_evidence
        from phase1c_evaluation_input import (prepare_heldout_review_input,
                                              operational_source_ids, verify_review_input)
        from phase1c_candidate import reader_input_digest
        from validate_phase1c_generated_rows import load_rows, validate_rows
        import yaml

        inputs, authoring = build_from_files()
        development = json.loads((HERE / "phase1c_development_source_exclusions.json").read_text())
        historical = json.loads((HERE / "phase1c_historical_source_exclusions.json").read_text())
        output = Path(os.environ["PHASE1C_EVALUATION_PACKETS"]) if os.environ.get("PHASE1C_EVALUATION_PACKETS") else None
        if output:
            output.mkdir(parents=True, exist_ok=True)
        index, selected_across_cases = [], set()
        with psycopg.connect(os.environ["EVALUATION_DATABASE_URL"]) as conn:
            try:
                conn.execute("SET search_path TO deal_desk, public")
                self.assertEqual(conn.execute("SELECT count(*) FROM deals").fetchone()[0], 0)
                self.assertEqual(conn.execute("SELECT count(*) FROM inventory").fetchone()[0], 0)
                for name in ("phase1c_buildable_master.sql", "phase1c_sellable_catalogue.sql"):
                    for statement in re.findall(r"^INSERT INTO .*?;", (HERE / name).read_text(), re.M | re.S):
                        conn.execute(statement)
                self.assertEqual(conn.execute("SELECT count(*) FROM products").fetchone()[0], 156)
                self.assertEqual(conn.execute("SELECT count(*) FROM pricing_rules").fetchone()[0], 33)
                for case in inputs["cases"]:
                    with self.subTest(case_id=case["case_id"]), conn.transaction(force_rollback=True):
                        tables = case["tables"]
                        for table in TABLE_ORDER:
                            for row in tables.get(table, []):
                                if table == "deal_runs":
                                    conn.execute("UPDATE deals SET deal_status='Submitted' WHERE deal_id=%s",
                                                 (row["deal_id"],))
                                statement = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                                    sql.Identifier(table),
                                    sql.SQL(",").join(map(sql.Identifier, row)),
                                    sql.SQL(",").join(sql.Placeholder() for _ in row))
                                conn.execute(statement, [Jsonb(v) if isinstance(v, (dict, list)) else v for v in row.values()])
                        conn.execute("SET CONSTRAINTS ALL IMMEDIATE")
                        validation = validate_rows(load_rows(conn), yaml.safe_load(
                            (HERE / "phase1c_data_contract.yaml").read_text()))
                        self.assertEqual(validation["errors"], [])
                        self.assertEqual(conn.execute("SELECT count(*) FROM deals").fetchone()[0], 1)
                        proof_path = output / (case["case_id"] + "-provider.json") if output else None
                        # The independent simulated provider channel is supplied
                        # separately; it is never a salesperson assertion.
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp:
                            provider = Path(temp) / "provider.json"
                            provider.write_text(render(case["provider_manifest"]))
                            resolver = load_provider_evidence(provider)
                            run_id = tables["deal_runs"][0]["run_id"]
                            bundle = read_run(conn, run_id, commercial_rule_mode="compiled",
                                              digital_evidence_resolver=resolver)
                            packet = prepare_heldout_review_input(
                                bundle, case_id=case["case_id"], development_manifest=development,
                                historical_manifest=historical)
                            repeated = prepare_heldout_review_input(
                                read_run(conn, run_id, commercial_rule_mode="compiled", digital_evidence_resolver=resolver),
                                case_id=case["case_id"], development_manifest=development,
                                historical_manifest=historical)
                        self.assertEqual(packet, repeated)
                        self.assertTrue(verify_review_input(packet, expected_case_id=case["case_id"],
                                                           expected_source_digest=reader_input_digest(bundle)))
                        self.assertFalse(keys_in(packet) & FORBIDDEN)
                        selected = operational_source_ids(bundle)
                        expected_ids = {
                            "inventory": {r["inventory_id"] for r in tables.get("inventory", [])},
                            "inbound_supply": {r["supply_id"] for r in tables.get("inbound_supply", [])},
                            "production_capacity": {r["capacity_id"] for r in tables.get("production_capacity", [])},
                            "digital_capacity": {r["digital_capacity_id"] for r in tables.get("digital_capacity", [])},
                        }
                        self.assertEqual(selected, expected_ids)
                        all_selected = set().union(*selected.values())
                        self.assertFalse(all_selected & selected_across_cases)
                        selected_across_cases.update(all_selected)
                        self.assertEqual(conn.execute("SELECT count(*) FROM agent_execution_log").fetchone()[0], 0)
                        proof_text = render(case["provider_manifest"])
                        index.append({"case_id": case["case_id"], "packet_sha256": packet["sha256"],
                                      "provider_file_sha256": hashlib.sha256(proof_text.encode()).hexdigest()})
                        if output:
                            (output / (case["case_id"] + ".json")).write_text(render(packet))
                            proof_path.write_text(proof_text)
                self.assertEqual(conn.execute("SELECT count(*) FROM deals").fetchone()[0], 0)
            finally:
                conn.rollback()
        self.assertEqual(len(index), 36)
        packet_index = {"schema_version": 1, "input_case_count": 36, "independently_reviewed_answers": 0,
                        "source_definition_sha256": authoring["inputs_sha256"],
                        "cases": index}
        self.assertEqual(packet_index, json.loads(
            (OUTPUT_DIR / "provisional_packet_index.json").read_text()))
        if output:
            (output / "packet_index.json").write_text(render(packet_index))
        print("Evaluation input preparation: 36 reproducible packets; 0 independently reviewed answers")


if __name__ == "__main__":
    unittest.main()
