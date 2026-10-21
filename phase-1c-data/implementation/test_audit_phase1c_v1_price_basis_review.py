"""Keep the V1 accounting proposal distinct from pinned source facts."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

import yaml

from audit_phase1c_v1_price_basis_review import audit


HERE = Path(__file__).resolve().parent


class V1PriceBasisReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
        cls.config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        cls.review = json.loads((HERE / "phase1c_v1_price_basis_review.json").read_text())
        cls.historical_sql = "\n".join(
            (HERE / f"phase1c_historical_inputs_{n:02d}.sql").read_text()
            for n in range(1, 9))

    def run_audit(self, **changes):
        args = dict(portfolio=self.portfolio, costs=self.costs, config=self.config,
                    contract=self.contract, review=self.review,
                    historical_sql=self.historical_sql)
        args.update(changes)
        return audit(**args)

    def test_full_ledger_keeps_its_review_boundary(self):
        result = self.run_audit()
        self.assertEqual(len(result["rows"]), 156)
        self.assertEqual(result["source_class_counts"], {
            "buildable_bom_draft": 18, "component_draft": 36,
            "seeded_category_draw_and_fixed_p50": 102})
        self.assertEqual(result["sellable_unit_mismatches"], 36)
        self.assertEqual(result["sku_observation_dates_recorded"], 0)
        self.assertEqual(result["historical_submission_dates"]["count"], 400)
        self.assertEqual(result["historical_submission_dates"]
                         ["before_catalogue_research_calibration_date"], 400)
        self.assertEqual(result["accepted_evaluation_answers"], 0)
        self.assertFalse(result["ready_for_generation"])

    def test_currency_or_status_cannot_silently_be_promoted(self):
        review = deepcopy(self.review)
        review["currency"] = "USD"
        with self.assertRaisesRegex(ValueError, "scope, currency"):
            self.run_audit(review=review)
        review = deepcopy(self.review)
        review["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "provisional status"):
            self.run_audit(review=review)

    def test_new_sku_provenance_requires_ledger_revision(self):
        portfolio = deepcopy(self.portfolio)
        portfolio["products"][0]["price_observation_date"] = "2026-09-24"
        with self.assertRaisesRegex(ValueError, "provenance has changed"):
            self.run_audit(portfolio=portfolio)

    def test_incomplete_historical_date_census_fails(self):
        changed = self.historical_sql.replace("'HIST-DEAL-0001'", "'OTHER-0001'", 1)
        with self.assertRaisesRegex(ValueError, "historical submission date coverage"):
            self.run_audit(historical_sql=changed)


if __name__ == "__main__":
    unittest.main()
