"""Check source-only reach of incompatible category-default price units."""

import json
from pathlib import Path
import unittest

import yaml

from audit_phase1c_price_unit_exposure import audit, count_exposure, literal_lines


HERE = Path(__file__).resolve().parent


class PriceUnitExposureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
        cls.config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        cls.history = "\n".join((HERE / f"phase1c_historical_inputs_{n:02d}.sql").read_text()
                                for n in range(1, 9))
        cls.batch = (HERE / "phase1c_generated_test_batch.sql").read_text()
        cls.pilots = "\n".join((HERE / name).read_text() for name in
                               ("phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql"))
        cls.dependency = (HERE / "phase1c_dependency_pilot.sql").read_text()
        cls.evaluation = json.loads((HERE.parent / "evaluation" / "provisional_cases.json").read_text())

    def run_audit(self, **overrides):
        args = {"portfolio": self.portfolio, "costs": self.costs,
                "config": self.config, "contract": self.contract,
                "historical_sql": self.history, "batch_sql": self.batch,
                "pilot_sql": self.pilots, "dependency_sql": self.dependency,
                "evaluation": self.evaluation}
        args.update(overrides)
        return audit(**args)

    def test_full_source_impact_without_promoting_answers(self):
        report = self.run_audit()
        self.assertEqual(len(report["mismatched_product_ids"]), 36)
        self.assertEqual((report["historical"]["deals"], report["historical"]["lines"],
                          report["historical"]["affected_deals"],
                          report["historical"]["affected_lines"]), (400, 1200, 235, 328))
        self.assertEqual((report["development_regression"]["deals"],
                          report["development_regression"]["lines"],
                          report["development_regression"]["affected_deals"]),
                         (100, 101, 16))
        self.assertEqual((report["evaluation_v2_inputs"]["deals"],
                          report["evaluation_v2_inputs"]["affected_deals"]), (36, 6))
        self.assertEqual(report["accepted_evaluation_answers"], 0)
        self.assertFalse(report["ready_for_generation"])

    def test_missing_development_template_fails(self):
        changed = self.batch.replace("FROM deal_lines WHERE deal_id='PILOT-DEAL-01'",
                                     "FROM deal_lines WHERE deal_id='MISSING-TEMPLATE'", 1)
        with self.assertRaisesRegex(ValueError, "missing development source"):
            self.run_audit(batch_sql=changed)

    def test_line_parser_and_affected_deals_are_distinct(self):
        lines = literal_lines("INSERT INTO deal_lines (x) VALUES ('L1', 'D1', '1', 'P1');\n"
                              "INSERT INTO deal_lines (x) VALUES ('L2', 'D1', '2', 'P1');\n"
                              "INSERT INTO deal_lines (x) VALUES ('L3', 'D2', '1', 'P2');\n")
        self.assertEqual(count_exposure(lines, {"P1": "category"})["affected_deals"], 1)
        self.assertEqual(count_exposure(lines, {"P1": "category"})["affected_lines"], 2)


if __name__ == "__main__":
    unittest.main()
