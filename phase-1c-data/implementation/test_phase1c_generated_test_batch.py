"""Reproduce and read the provisional 100-deal generated-test batch."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import unittest

import yaml

from render_phase1c_generated_test_batch import SOURCE_FILES, build, eligible_customers
from validate_phase1c_scenario_matrix import generated_case_plan

try:
    import psycopg
except ImportError:
    psycopg = None

if psycopg is not None:
    from phase1c_reader import read_run
    from phase1c_deal_decision import assemble_deal_decision
    from validate_phase1c_generated_rows import load_rows, validate_rows

HERE = Path(__file__).resolve().parent
FILES = ("phase1c_buildable_master.sql", "phase1c_sellable_catalogue.sql",
         "phase1c_customer_master.sql",
         "phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql",
         "phase1c_stress_pilot.sql", "phase1c_dependency_pilot.sql",
         "phase1c_generated_test_batch.sql")


class GeneratedBatchRenderTests(unittest.TestCase):
    def test_source_only_reproducibility(self):
        matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
        hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in SOURCE_FILES}
        sql, report = build(matrix, hashes, (HERE / "phase1c_customer_master.sql").read_text())
        self.assertEqual(sql, (HERE / "phase1c_generated_test_batch.sql").read_text())
        self.assertEqual(report, json.loads(
            (HERE / "phase1c_generated_test_batch_report.json").read_text()))
        self.assertEqual(len(generated_case_plan(matrix)), 100)
        self.assertEqual((report["v1_deals"], report["v2_dependency_deals"],
                          report["line_count"], report["source_template_count"]),
                         (98, 2, 101, 20))
        self.assertEqual((report["eligible_customer_count"], report["customer_reassignment_count"]),
                         (37, 63))
        self.assertEqual(len(set(eligible_customers((HERE / "phase1c_customer_master.sql").read_text()))), 37)
        self.assertNotIn("target_bucket", sql)
        self.assertNotIn("historical_decision", sql)
        self.assertNotIn("expected_decision", sql)


@unittest.skipUnless(psycopg is not None and os.environ.get("DATABASE_URL"),
                     "PostgreSQL integration requires psycopg and DATABASE_URL")
class GeneratedBatchDatabaseTests(unittest.TestCase):
    def test_import_reader_decision_and_row_coverage(self):
        matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
        contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            conn.execute("SET search_path TO deal_desk, public")
            try:
                before = {table: {row[next(iter(row))] for row in records}
                          for table, records in load_rows(conn).items()}
                for name in FILES:
                    for statement in re.findall(r"^(?:INSERT INTO|UPDATE deals SET) .*?;",
                                                (HERE / name).read_text(), re.M | re.S):
                        conn.execute(statement)
                rows = {table: [row for row in records
                                if row[next(iter(row))] not in before[table]]
                        for table, records in load_rows(conn).items()}
                result = validate_rows(rows, contract)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["counts"]["deals"], 138)
                self.assertEqual(result["counts"]["deal_lines"], 169)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["pass"], 2)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["fail"], 2)
                self.assertEqual(result["supplier_calendar_coverage"]["offers_missing_calendar"], [])
                statuses, modes, customers = Counter(), Counter(), Counter()
                fulfillment, availability_sources = Counter(), Counter()
                eligible = set(eligible_customers((HERE / "phase1c_customer_master.sql").read_text()))
                for index, slot in enumerate(generated_case_plan(matrix), 1):
                    run_id = f"00000000-0000-4000-8000-{310000 + index:012d}"
                    bundle = read_run(conn, run_id, commercial_rule_mode="compiled")
                    self.assertEqual(bundle["deal"]["deal_id"], slot["case_id"])
                    self.assertEqual(bundle["run"]["catalog_version_used"], slot["catalog_version"])
                    decision = assemble_deal_decision(bundle)
                    self.assertNotEqual(decision["status"], "approved")
                    statuses[decision["status"]] += 1
                    customers[bundle["deal"]["customer_id"]] += 1
                    if bundle["deal"]["customer_id"] in eligible:
                        profile = conn.execute(
                            "SELECT credit_status, risk_rating, commitments_as_of_at "
                            "FROM customer_credit_profiles WHERE customer_id=%s",
                            (bundle["deal"]["customer_id"],)).fetchone()
                        self.assertEqual(profile[0], "Active")
                        self.assertIn(profile[1], ("Low", "Medium"))
                        self.assertLessEqual(profile[2], bundle["run"]["as_of_at"])
                    if slot["archetype_id"] == "CREDIT-LIMIT":
                        self.assertNotIn(bundle["deal"]["customer_id"], eligible)
                    modes.update(line["fulfillment_mode"] for line in bundle["lines"])
                    fulfillment.update(fact["fulfillment_status"] for fact in bundle["facts"]["lines"]
                                       if "fulfillment_status" in fact)
                    availability_sources.update(source
                        for finding in decision["specialists"]["availability"]
                        for source in finding["source_ids"])
                    if index in (99, 100):
                        finding = next(f for f in bundle["facts"]["compatibility"]
                                       if f["compatibility_rule_id"] == "V2-REQUIRES-ADDON")
                        self.assertEqual(finding["status"], "pass" if index == 99 else "fail")
                        self.assertEqual(any(b.get("rule_id") == "V2-REQUIRES-ADDON"
                                             for b in decision["blocks"]), index == 100)
                diagnostic = {
                    "status": "development_diagnostic_not_answer_key",
                    "deal_count": sum(statuses.values()),
                    "decision_status_counts": dict(sorted(statuses.items())),
                    "line_mode_counts": dict(sorted(modes.items())),
                    "fulfillment_status_counts": dict(sorted(fulfillment.items())),
                    "distinct_customer_count": len(customers),
                    "distinct_availability_source_ids": len(availability_sources),
                    "top_availability_source_reuse": [
                        {"source_id": source, "finding_attributions": count}
                        for source, count in sorted(availability_sources.items(),
                                                    key=lambda item: (-item[1], item[0]))[:10]],
                    "source_template_count": 20,
                    "limitations": ["source_states_reused_across_submissions",
                                    "no_independent_answers_or_evaluation_cases"],
                }
                self.assertEqual(diagnostic["deal_count"], 100)
                self.assertEqual(sum(modes.values()), 101)
                self.assertGreaterEqual(len(statuses), 2)
                self.assertGreaterEqual(len(customers), 50)
                if os.environ.get("PHASE1C_BATCH_DIAGNOSTIC"):
                    Path(os.environ["PHASE1C_BATCH_DIAGNOSTIC"]).write_text(
                        json.dumps(diagnostic, indent=2, sort_keys=True) + "\n")
            finally:
                conn.rollback()


if __name__ == "__main__":
    unittest.main()
