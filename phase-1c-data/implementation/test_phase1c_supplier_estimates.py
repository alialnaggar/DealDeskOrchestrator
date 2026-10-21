"""The historical modal-only source must never gain an invented dated route."""

from copy import deepcopy
from datetime import datetime, date, timezone
import unittest

from phase1c_supplier_estimates import estimate_supplier_offer


class SupplierEstimateTests(unittest.TestCase):
    def setUp(self):
        self.as_of = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
        self.offer = {
            "supplier_item_id": "O-1", "supplier_id": "S-1",
            "order_calendar_json": {"working_weekdays": [1, 2, 3, 4, 5],
                                    "holiday_dates": [], "time_zone": "Europe/Berlin"},
            "lead_days_min": 0, "lead_days_mode": 2, "lead_days_max": 3,
        }

    def test_complete_offer_remains_uncommitted(self):
        result = estimate_supplier_offer(self.offer, self.as_of)
        self.assertEqual((result["earliest"], result["mode"], result["latest"]),
                         (date(2026, 9, 1), date(2026, 9, 3), date(2026, 9, 4)))
        self.assertFalse(result["binding"])

    def test_calendar_alone_cannot_complete_historical_modal_offer(self):
        for missing in ("lead_days_min", "lead_days_max"):
            with self.subTest(missing=missing):
                offer = deepcopy(self.offer)
                del offer[missing]
                self.assertIsNone(estimate_supplier_offer(offer, self.as_of))

    def test_invalid_leads_fail_closed(self):
        for leads in ((3, 2, 4), (0, True, 3), (-1, 2, 3), (0, 2, "3")):
            with self.subTest(leads=leads):
                offer = deepcopy(self.offer)
                offer.update(zip(("lead_days_min", "lead_days_mode", "lead_days_max"), leads))
                self.assertIsNone(estimate_supplier_offer(offer, self.as_of))

    def test_invalid_calendar_fails_closed(self):
        for change in ({"time_zone": "No/Such_Zone"}, {"working_weekdays": []},
                       {"working_weekdays": [1, 1, 2]}, {"working_weekdays": [True, 2]},
                       {"holiday_dates": ["2026-09-02"]}):
            with self.subTest(change=change):
                offer = deepcopy(self.offer)
                offer["order_calendar_json"].update(change)
                self.assertIsNone(estimate_supplier_offer(offer, self.as_of))


if __name__ == "__main__":
    unittest.main()
