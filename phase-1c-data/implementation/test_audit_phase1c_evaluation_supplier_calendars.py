"""Mutation checks for source-only evaluation offer joins."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

import yaml

from audit_phase1c_evaluation_supplier_calendars import CASES, HERE, audit


class EvaluationCalendarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(CASES.read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())

    def test_current_v2_offer_joins(self):
        report = audit(self.source, self.contract)
        self.assertEqual(report["cases"], 36)
        self.assertEqual(report["linked_offer_count"], 10)
        self.assertEqual(report["supplier_rows_with_typed_calendars"], 36)
        self.assertEqual(report["linked_offer_case_ids"],
                         [f"EVAL-PREP-{n:03d}" for n in
                          (7, 8, 9, 10, 11, 12, 15, 16, 19, 20)])
        self.assertEqual(report["independently_reviewed_answers"], 0)

    def test_missing_supplier_rejected(self):
        source = deepcopy(self.source)
        source["cases"][6]["tables"]["suppliers"] = []
        with self.assertRaisesRegex(ValueError, "active local supplier"):
            audit(source, self.contract)

    def test_bad_calendar_rejected(self):
        source = deepcopy(self.source)
        source["cases"][6]["tables"]["suppliers"][0]["order_calendar_json"]["working_weekdays"] = [0]
        with self.assertRaisesRegex(ValueError, "invalid calendar"):
            audit(source, self.contract)

    def test_inverted_leads_rejected(self):
        source = deepcopy(self.source)
        source["cases"][6]["tables"]["supplier_items"][0]["lead_days_max"] = 0
        with self.assertRaisesRegex(ValueError, "unordered leads"):
            audit(source, self.contract)

    def test_expired_offer_rejected(self):
        source = deepcopy(self.source)
        source["cases"][6]["tables"]["supplier_items"][0]["valid_to"] = "2026-08-31"
        with self.assertRaisesRegex(ValueError, "not active at run cutoff"):
            audit(source, self.contract)


if __name__ == "__main__":
    unittest.main()
