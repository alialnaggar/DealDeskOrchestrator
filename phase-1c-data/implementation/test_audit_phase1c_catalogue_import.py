"""Reject imported price, cost and identity drift from the source catalogue."""

from copy import deepcopy
from decimal import Decimal
from unittest.mock import patch
import unittest

from audit_phase1c_catalogue_import import audit


class CatalogueImportTests(unittest.TestCase):
    def setUp(self):
        self.rows = []
        self.expected = {}
        for n in range(156):
            pid = f"P-{n:03d}"
            attrs = {"category": "synthetic"}
            self.rows.append({
                "product_id": pid, "catalog_version": "CATALOGUE_2026_V1",
                "list_price": "100.00", "standard_cost": "70.00",
                "billing_model": "one_time", "unit_of_measure": "device",
                "fulfillment_mode": "stocked_finished", "is_sellable": "t",
                "attributes_json": '{"category":"synthetic"}',
            })
            self.expected[pid] = ("CATALOGUE_2026_V1", Decimal(100), Decimal(70),
                                  "one_time", "device", "stocked_finished", True, attrs)
        self.source = patch("audit_phase1c_catalogue_import.expected_rows",
                            return_value=(self.expected, {"checked_products": 18,
                                                          "checked_boms": 24}))
        self.source.start()
        self.addCleanup(self.source.stop)

    def check(self, rows):
        return audit(rows, None, None, None, None)

    def test_exact_import_with_postgresql_boolean_format(self):
        self.assertEqual(self.check(self.rows)["v1_rows_reconciled"], 156)

    def test_changed_cost_or_attribute_is_rejected(self):
        for field, value in (("standard_cost", "71"), ("attributes_json", "{}")):
            with self.subTest(field=field):
                rows = deepcopy(self.rows)
                rows[0][field] = value
                with self.assertRaisesRegex(ValueError, "differs from source"):
                    self.check(rows)

    def test_missing_or_repeated_identity_is_rejected(self):
        rows = deepcopy(self.rows)
        rows[1]["product_id"] = rows[0]["product_id"]
        with self.assertRaisesRegex(ValueError, "identities differ"):
            self.check(rows)
        with self.assertRaisesRegex(ValueError, "row count"):
            self.check(self.rows[:-1])


if __name__ == "__main__":
    unittest.main()
