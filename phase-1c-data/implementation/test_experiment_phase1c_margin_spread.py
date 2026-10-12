"""Bound the read-only price sensitivity experiment and its provenance."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

import yaml

from experiment_phase1c_margin_spread import experiment, proposed_margin


HERE = Path(__file__).resolve().parent


class MarginSpreadExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
        cls.config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())

    def test_replay_and_no_input_mutation(self):
        source = deepcopy(self.costs)
        first = experiment(self.portfolio, self.costs, self.config, self.contract)
        self.assertEqual(first, experiment(self.portfolio, self.costs, self.config, self.contract))
        self.assertEqual(self.costs, source)
        self.assertEqual((first["generated_costs_recalculated"],
                          first["buildable_costs_unchanged"]), (102, 18))
        self.assertEqual(len(first["product_deltas"]), 102)
        self.assertEqual(len(first["input_digest"]), 64)
        self.assertTrue(first["prices_unchanged"])
        self.assertFalse(first["calibration_frozen"])
        self.assertFalse(first["ready_for_generation"])

    def test_bounded_spread_changes_floor_sensitivity_without_bom_repricing(self):
        result = experiment(self.portfolio, self.costs, self.config, self.contract)
        rows = result["categories"]
        self.assertEqual(sum(x["ten_pct_discount_below_floor_current"] for x in rows), 12)
        self.assertEqual(sum(x["ten_pct_discount_below_floor_experiment"] for x in rows), 41)
        self.assertEqual(sum(x["ten_pct_discount_nonpositive_current"] for x in rows), 0)
        self.assertEqual(sum(x["ten_pct_discount_nonpositive_experiment"] for x in rows), 2)
        self.assertEqual(sum(len(x["status_transitions"]) for x in rows), 31)
        self.assertEqual({x["source"] for row in rows for x in row["status_transitions"]},
                         {"generated"})
        for row in result["product_deltas"]:
            targets = self.config["commercial_supply"]["standard_cost"][
                "target_list_margin_percent_by_category"][row["category"]]
            self.assertGreaterEqual(float(row["experimental_list_margin_pct"]), targets["p10"] - .01)
            self.assertLessEqual(float(row["experimental_list_margin_pct"]), targets["p90"] + .01)

    def test_seed_changes_the_provisional_draw_and_is_traceable(self):
        altered = deepcopy(self.config)
        altered["random_seed"] += 1
        original = experiment(self.portfolio, self.costs, self.config, self.contract)
        changed = experiment(self.portfolio, self.costs, altered, self.contract)
        self.assertNotEqual(original["input_digest"], changed["input_digest"])
        self.assertNotEqual(original["product_deltas"], changed["product_deltas"])
        self.assertNotEqual([x["list_price_eur"] for x in original["product_deltas"]],
                            [x["list_price_eur"] for x in changed["product_deltas"]])

    def test_three_policy_profiles_show_identity_changes_hidden_by_totals(self):
        scenarios = experiment(self.portfolio, self.costs, self.config,
                               self.contract)["profile_scenarios"]
        self.assertEqual(len(scenarios), 9)
        for row in scenarios:
            self.assertEqual(sum(row["current"].values()), 120)
            self.assertEqual(sum(row["experiment"].values()), 120)
            self.assertEqual(len(row["changed_product_ids"]), row["changed_line_statuses"])
        baseline = next(row for row in scenarios if row["profile"] == "BASELINE_2026"
                        and row["quote_discount_pct"] == 10)
        strict = next(row for row in scenarios if row["profile"] == "STRICT_EXPERIMENT"
                      and row["quote_discount_pct"] == 10)
        self.assertEqual((baseline["current"]["below_floor"],
                          baseline["experiment"]["below_floor"],
                          baseline["experiment"]["nonpositive"],
                          baseline["changed_line_statuses"]), (12, 39, 2, 31))
        self.assertEqual((strict["current"]["below_floor"],
                          strict["experiment"]["below_floor"],
                          strict["experiment"]["nonpositive"],
                          strict["changed_line_statuses"]), (55, 54, 2, 39))

    def test_invalid_or_incomplete_proposal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid bounded margin band"):
            proposed_margin(0, 10, {"p10": 20, "p50": 10, "p90": 30})
        altered = deepcopy(self.costs)
        altered["products"].pop()
        with self.assertRaisesRegex(ValueError, "unpriced buildable product"):
            experiment(self.portfolio, altered, self.config, self.contract)


if __name__ == "__main__":
    unittest.main()
