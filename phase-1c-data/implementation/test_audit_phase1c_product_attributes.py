"""Regression checks for V1 product attribute coverage and fail-closed inputs."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

import yaml

from audit_phase1c_product_attributes import audit


HERE = Path(__file__).resolve().parent


class ProductAttributesAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        cls.fit = json.loads((HERE / "phase1c_technical_fit_draft.json").read_text())

    def test_all_v1_rows_and_boms_pass(self):
        result = audit(self.portfolio, self.contract, self.fit)
        self.assertEqual(result["errors"], [])
        self.assertEqual((result["product_rows"], result["checked_component_specs"],
                          result["checked_boms"], result["checked_alternatives"]),
                         (156, 36, 24, 25))
        self.assertFalse(result["ready_for_generation"])

    def test_explicit_buildable_unknown_attribute_rejected(self):
        draft = deepcopy(self.portfolio)
        row = next(r for r in draft["products"] if r["fulfillment_mode"] == "make_to_order")
        row["attributes_json"]["invented_key"] = True
        self.assertTrue(any("unknown keys" in e for e in audit(draft, self.contract, self.fit)["errors"]))

    def test_component_catalogue_spec_mismatch_rejected(self):
        draft = deepcopy(self.portfolio)
        row = next(r for r in draft["products"] if r["fulfillment_mode"] == "component")
        row["attributes_json"]["rated_watts"] = -1
        self.assertTrue(any("catalogue attributes differ" in e for e in audit(draft, self.contract, self.fit)["errors"]))

    def test_digital_edition_missing_rejected(self):
        draft = deepcopy(self.portfolio)
        row = next(r for r in draft["products"] if r["fulfillment_mode"] == "digital_activation")
        del row["attributes_json"]["edition"]
        self.assertTrue(any("missing mode key edition" in e for e in audit(draft, self.contract, self.fit)["errors"]))

    def test_duplicate_product_id_rejected(self):
        draft = deepcopy(self.portfolio)
        draft["products"][1]["product_id"] = draft["products"][0]["product_id"]
        self.assertTrue(any("distinct product IDs" in e for e in audit(draft, self.contract, self.fit)["errors"]))


if __name__ == "__main__":
    unittest.main()
