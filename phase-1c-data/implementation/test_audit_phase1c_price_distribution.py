"""Check the full provisional distribution and fail on incomplete pricing."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

import yaml

from audit_phase1c_price_distribution import audit


HERE = Path(__file__).resolve().parent


class PriceDistributionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
        cls.config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())

    def test_full_fixture_is_counted_without_promoting_the_gate(self):
        report = audit(self.portfolio, self.costs, self.config, self.contract)
        self.assertEqual((report["sellable_count"], report["generated_count"],
                          report["buildable_draft_count"]), (120, 102, 18))
        self.assertEqual(len(report["categories"]), 9)
        self.assertEqual(sum(row["count"] for row in report["categories"]), 120)
        self.assertEqual(sum(row["generated_at_proposed_p50"]
                             for row in report["categories"]), 102)
        self.assertEqual([pid for row in report["categories"]
                          for pid in row["above_proposed_p90"]],
                         ["SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009"])
        self.assertFalse(report["price_comparability_verified"])
        self.assertFalse(report["ready_for_generation"])

    def test_a_changed_buildable_price_changes_the_measured_margin(self):
        altered = deepcopy(self.costs)
        altered["products"][0]["product_list_price_eur"] = 990
        report = audit(self.portfolio, altered, self.config, self.contract)
        self.assertFalse(any(row["above_proposed_p90"] for row in report["categories"]))

    def test_missing_or_duplicate_buildable_cost_fails(self):
        altered = deepcopy(self.costs)
        altered["products"].pop()
        with self.assertRaisesRegex(ValueError, "18 distinct"):
            audit(self.portfolio, altered, self.config, self.contract)
        altered = deepcopy(self.costs)
        altered["products"][1]["product_id"] = altered["products"][0]["product_id"]
        with self.assertRaisesRegex(ValueError, "18 distinct"):
            audit(self.portfolio, altered, self.config, self.contract)

    def test_incomparable_units_have_separate_price_groups(self):
        report = audit(self.portfolio, self.costs, self.config, self.contract)
        cloud = [r for r in report["price_groups"]
                 if r["category"] == "cloud_services_and_subscriptions"]
        self.assertGreater(len({row["unit_of_measure"] for row in cloud}), 1)


if __name__ == "__main__":
    unittest.main()
