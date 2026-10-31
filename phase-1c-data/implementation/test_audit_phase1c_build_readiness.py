"""Check that readiness findings respond to real changes in draft inputs."""

from copy import deepcopy
import json
import unittest

import yaml

from audit_phase1c_build_readiness import HERE, audit


class ReadinessAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
        cls.fit_draft = json.loads((HERE / "phase1c_technical_fit_draft.json").read_text())
        cls.config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())

    def test_current_draft_keeps_evidence_gate_open(self):
        result = audit(self.portfolio, self.costs, self.config, self.fit_draft)
        self.assertEqual(result["component_specifications_missing"], {})
        self.assertEqual(result["boms_awaiting_detailed_compatibility"], [])
        self.assertEqual(result["synthetic_fit_checked_boms"], 24)
        self.assertFalse(result["component_sourcing_verified"])
        self.assertEqual(len(result["margin_outliers_above_proposed_p90"]), 1)
        self.assertFalse(result["ready_for_full_generation"])

    def test_margin_change_removes_only_the_outlier(self):
        costs = deepcopy(self.costs)
        costs["products"][0]["product_standard_cost_eur"] = 770
        result = audit(self.portfolio, costs, self.config, self.fit_draft)
        self.assertEqual(result["margin_outliers_above_proposed_p90"], [])
        self.assertEqual(result["boms_awaiting_detailed_compatibility"], [])
        self.assertFalse(result["price_comparability_verified"])

    def test_part_specification_updates_affected_bom_set(self):
        portfolio = deepcopy(self.portfolio)
        component = next(p for p in portfolio["products"] if p["product_id"] == "COMP-STORAGE-001")
        component["attributes_json"]["host_interface"] = "SATA"
        result = audit(portfolio, self.costs, self.config, self.fit_draft)
        self.assertEqual(len(result["boms_awaiting_detailed_compatibility"]), 24)
        self.assertTrue(any("catalogue attributes differ" in error
                            for error in result["synthetic_fit_errors"]))
        self.assertFalse(result["ready_for_full_generation"])


if __name__ == "__main__":
    unittest.main()
