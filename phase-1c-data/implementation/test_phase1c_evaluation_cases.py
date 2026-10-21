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
    def test_service_cases_have_an_explicit_condition_for_the_submitted_region(self):
        inputs, manifest = build_from_files()
        intent = {row["case_id"]: row["archetype_id"] for row in manifest["cases"]}
        checked = 0
        for case in inputs["cases"]:
            archetype = intent[case["case_id"]]
            if archetype not in ("SERVICE-COVERED", "SERVICE-OUTSIDE"):
                continue
            deal = case["tables"]["deals"][0]
            matches = [rule["condition_json"] for rule in case["tables"]["compatibility_rules"]
                       if rule["condition_json"]["country_code"] == deal["destination_country_code"]
                       and rule["condition_json"]["region"] == deal["destination_region"]]
            self.assertEqual(len(matches), 1)
            self.assertIs(matches[0]["eligible"], archetype == "SERVICE-COVERED")
            checked += 1
        self.assertEqual(checked, 4)

    def test_v2_changes_only_approved_offers_and_config_fingerprint(self):
        from copy import deepcopy
        current, manifest = build_from_files()
        archived = json.loads((OUTPUT_DIR / "archive/v1/provisional_cases.json").read_text())
        self.assertEqual(current["evaluation_input_version"], 2)
        self.assertEqual(current["business_contract"]["approval"]["decisions"], ["F1", "C1", "C2", "G1", "S1", "R1"])
        self.assertEqual(current["business_contract"]["evidence_age"]["snapshot_max_elapsed_hours"], 24)
        changed = {}
        for before, after in zip(archived["cases"], current["cases"]):
            old, new = deepcopy(before), deepcopy(after)
            old["tables"]["deal_runs"][0].pop("config_hash")
            new["tables"]["deal_runs"][0].pop("config_hash")
            for a, b in zip(old["tables"].get("supplier_items", []), new["tables"].get("supplier_items", [])):
                a_cost, b_cost = a.pop("unit_cost"), b.pop("unit_cost")
                if a_cost != b_cost:
                    changed[after["case_id"]] = b_cost
            self.assertEqual(old, new)
        expected = {f"EVAL-PREP-{i:03}": "2386.20" for i in range(7, 13)}
        expected.update({f"EVAL-PREP-{i:03}": "50.00" for i in (15, 16)})
        expected.update({f"EVAL-PREP-{i:03}": "240.00" for i in (19, 20)})
        self.assertEqual(changed, expected)
        old_manifest = json.loads((OUTPUT_DIR / "archive/v1/provisional_authoring_manifest.json").read_text())
        self.assertEqual(hashlib.sha256(render(archived).encode()).hexdigest(), old_manifest["inputs_sha256"])

    def test_contract_is_sealed_and_cannot_be_rebound(self):
        from copy import deepcopy
        from phase1c_candidate import INPUT_TABLES, reader_input_digest
        from phase1c_evaluation_input import prepare_review_input, verify_review_input, review_source_digest
        bundle = {key: [] for key in INPUT_TABLES}
        bundle["deal"] = {"deal_id": "source-fixture"}
        bundle["run"] = dict(run_id="fixture-run", deal_id="source-fixture", as_of_at="2026-09-01T12:00:00+00:00",
                             catalog_version_used="fixture", applied_policy_set_code="fixture",
                             data_snapshot_ref="fixture", config_hash="fixture")
        contract = {"contract_id": "fixture", "snapshot_hours": 24}
        legacy = prepare_review_input(bundle, case_id="EVAL-PREP-TEST")
        packet = prepare_review_input(bundle, case_id="EVAL-PREP-TEST", business_contract=contract)
        self.assertNotEqual(legacy["sha256"], packet["sha256"])
        self.assertEqual(packet["payload"]["source_rows"], legacy["payload"]["source_rows"])
        self.assertTrue(verify_review_input(packet, expected_case_id="EVAL-PREP-TEST",
                        expected_source_digest=review_source_digest(bundle, contract), expected_business_contract=contract))
        changed = deepcopy(packet)
        changed["payload"]["business_contract"]["snapshot_hours"] = 48
        changed["sha256"] = hashlib.sha256(json.dumps(changed["payload"],sort_keys=True,separators=(",", ":")).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "contract differs"):
            verify_review_input(changed, expected_case_id="EVAL-PREP-TEST",
                                expected_source_digest=review_source_digest(bundle, contract), expected_business_contract=contract)
        with self.assertRaises(ValueError):
            verify_review_input(packet, expected_case_id="EVAL-PREP-TEST", expected_source_digest=review_source_digest(bundle, contract))

    def test_v2_collection_order_does_not_change_facts_or_fingerprint(self):
        from copy import deepcopy
        from phase1c_candidate import INPUT_TABLES
        from phase1c_evaluation_input import prepare_review_input
        bundle = {key: [] for key in INPUT_TABLES}
        bundle["deal"] = {"deal_id": "source-fixture"}
        bundle["run"] = dict(run_id="fixture-run", deal_id="source-fixture", as_of_at="2026-09-01T12:00:00+00:00",
                             catalog_version_used="fixture", applied_policy_set_code="fixture",
                             data_snapshot_ref="fixture", config_hash="fixture")
        bundle["bom_lines"] = [{"bom_line_id": "B", "standard_cost": "50"},
                               {"bom_line_id": "A", "standard_cost": "180"}]
        contract = {"contract_id": "fixture"}
        first = prepare_review_input(bundle, case_id="EVAL-PREP-TEST", business_contract=contract)
        reversed_bundle = deepcopy(bundle)
        reversed_bundle["bom_lines"].reverse()
        second = prepare_review_input(reversed_bundle, case_id="EVAL-PREP-TEST", business_contract=contract)
        self.assertEqual(first, second)
        self.assertEqual(sorted(first["payload"]["source_rows"]["bom_lines"], key=lambda r:r["bom_line_id"]),
                         sorted(bundle["bom_lines"], key=lambda r:r["bom_line_id"]))
        self.assertNotEqual(prepare_review_input(bundle, case_id="EVAL-PREP-TEST")["sha256"],
                            prepare_review_input(reversed_bundle, case_id="EVAL-PREP-TEST")["sha256"])

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
        inputs, authoring = build_from_files()
        self._export(inputs, authoring, OUTPUT_DIR, inputs["business_contract"],
                     os.environ.get("PHASE1C_EVALUATION_PACKETS"))

    def test_archived_v1_packets_remain_bound_to_first_review(self):
        archive = OUTPUT_DIR / "archive" / "v1"
        self._export(json.loads((archive / "provisional_cases.json").read_text()),
                     json.loads((archive / "provisional_authoring_manifest.json").read_text()),
                     archive, None, os.environ.get("PHASE1C_EVALUATION_PACKETS_V1"))

    def _export(self, inputs, authoring, pinned_directory, business_contract, output_directory):
        from phase1c_reader import read_run, load_provider_evidence, _installation
        from phase1c_evaluation_input import (prepare_heldout_review_input,
                                              operational_source_ids, verify_review_input, review_source_digest)
        from phase1c_candidate import reader_input_digest
        from validate_phase1c_generated_rows import load_rows, validate_rows
        import yaml

        development = json.loads((HERE / "phase1c_development_source_exclusions.json").read_text())
        historical = json.loads((HERE / "phase1c_historical_source_exclusions.json").read_text())
        output = Path(output_directory) if output_directory else None
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
                            if business_contract is not None:
                                # Selected reader facts only: this is not a reviewer answer.
                                expected_rules = tables.get("compatibility_rules", [])
                                self.assertEqual(
                                    {r["compatibility_rule_id"] for r in bundle["compatibility"]},
                                    {r["compatibility_rule_id"] for r in expected_rules})
                                self.assertEqual(bundle["run"]["catalog_version_used"],
                                                 tables["deal_runs"][0]["catalog_version_used"])
                                service_facts = [fact["service"] for fact in bundle["facts"]["lines"]
                                                 if "service" in fact]
                                if case["case_id"] in {f"EVAL-PREP-{n:03d}" for n in range(27, 31)}:
                                    self.assertEqual(len(expected_rules), 1)
                                    self.assertEqual(len(service_facts), 1)
                                    rule = expected_rules[0]
                                    self.assertEqual(rule["catalog_version"], "CATALOGUE_2026_V1")
                                    self.assertEqual(rule["rule_type"], "installation_eligibility")
                                    self.assertEqual(rule["source_product_id"], bundle["lines"][0]["product_id"])
                                    self.assertEqual(rule["condition_json"]["country_code"],
                                                     bundle["deal"]["destination_country_code"])
                                    self.assertEqual(rule["condition_json"]["region"],
                                                     bundle["deal"]["destination_region"])
                                    self.assertEqual(service_facts[0]["coverage_rule_ids"],
                                                     [rule["compatibility_rule_id"]])
                                    self.assertEqual(service_facts[0]["coverage"],
                                                     "eligible" if rule["condition_json"]["eligible"]
                                                     else "ineligible")
                                    self.assertFalse(service_facts[0]["slot_committed"])
                                    self.assertEqual(_installation(bundle["lines"][0],
                                                                    bundle["deal"], []),
                                                     ("unknown", []))
                                else:
                                    self.assertEqual(expected_rules, [])
                                    self.assertEqual(service_facts, [])
                                self.assertEqual(bundle["facts"]["compatibility"], [])
                            packet = prepare_heldout_review_input(
                                bundle, case_id=case["case_id"], development_manifest=development,
                                historical_manifest=historical, business_contract=business_contract)
                            repeated = prepare_heldout_review_input(
                                read_run(conn, run_id, commercial_rule_mode="compiled", digital_evidence_resolver=resolver),
                                case_id=case["case_id"], development_manifest=development,
                                historical_manifest=historical, business_contract=business_contract)
                        self.assertEqual(packet, repeated)
                        self.assertTrue(verify_review_input(packet, expected_case_id=case["case_id"],
                                                           expected_source_digest=review_source_digest(bundle, business_contract),
                                                           expected_business_contract=business_contract))
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
        if business_contract is not None:
            packet_index.update(evaluation_input_version=2, business_contract_sha256=hashlib.sha256(
                json.dumps(business_contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
        if output:
            (output / "packet_index.json").write_text(render(packet_index))
        self.maxDiff = None
        self.assertEqual(packet_index, json.loads(
            (pinned_directory / "provisional_packet_index.json").read_text()))
        print("Evaluation input preparation: 36 reproducible packets; 0 independently reviewed answers")


if __name__ == "__main__":
    unittest.main()
