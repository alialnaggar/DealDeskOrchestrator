"""Reproduce and read the provisional 100-deal generated-test batch."""

import hashlib
import json
import os
from pathlib import Path
import re
import unittest

import yaml

from render_phase1c_generated_test_batch import SOURCE_FILES, build
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
         "phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql",
         "phase1c_stress_pilot.sql", "phase1c_dependency_pilot.sql",
         "phase1c_generated_test_batch.sql")


class GeneratedBatchRenderTests(unittest.TestCase):
    def test_source_only_reproducibility(self):
        matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
        hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in SOURCE_FILES}
        sql, report = build(matrix, hashes)
        self.assertEqual(sql, (HERE / "phase1c_generated_test_batch.sql").read_text())
        self.assertEqual(report, json.loads(
            (HERE / "phase1c_generated_test_batch_report.json").read_text()))
        self.assertEqual(len(generated_case_plan(matrix)), 100)
        self.assertEqual((report["v1_deals"], report["v2_dependency_deals"],
                          report["line_count"], report["source_template_count"]),
                         (98, 2, 101, 20))
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
                for name in FILES:
                    for statement in re.findall(r"^(?:INSERT INTO|UPDATE deals SET) .*?;",
                                                (HERE / name).read_text(), re.M | re.S):
                        conn.execute(statement)
                rows = load_rows(conn)
                result = validate_rows(rows, contract)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["counts"]["deals"], 138)
                self.assertEqual(result["counts"]["deal_lines"], 166)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["pass"], 2)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["fail"], 2)
                self.assertEqual(result["supplier_calendar_coverage"]["offers_missing_calendar"], [])
                for index, slot in enumerate(generated_case_plan(matrix), 1):
                    run_id = f"00000000-0000-4000-8000-{310000 + index:012d}"
                    bundle = read_run(conn, run_id, commercial_rule_mode="compiled")
                    self.assertEqual(bundle["deal"]["deal_id"], slot["case_id"])
                    self.assertEqual(bundle["run"]["catalog_version_used"], slot["catalog_version"])
                    decision = assemble_deal_decision(bundle)
                    self.assertNotEqual(decision["status"], "approved")
                    if index in (99, 100):
                        finding = next(f for f in bundle["facts"]["compatibility"]
                                       if f["compatibility_rule_id"] == "V2-REQUIRES-ADDON")
                        self.assertEqual(finding["status"], "pass" if index == 99 else "fail")
                        self.assertEqual(any(b.get("rule_id") == "V2-REQUIRES-ADDON"
                                             for b in decision["blocks"]), index == 100)
            finally:
                conn.rollback()


if __name__ == "__main__":
    unittest.main()
