"""Check source sealing and that modal-only offers do not imply dates."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from datetime import datetime, timezone

from phase1c_supplier_estimates import estimate_supplier_offer

import yaml

from audit_phase1c_historical_supplier_calendars import SOURCE, audit


HERE = Path(__file__).resolve().parent


class HistoricalCalendarCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (HERE / SOURCE).read_bytes()
        cls.index = json.loads((HERE / "phase1c_historical_operational_index.json").read_text())
        cls.contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())

    def test_pinned_modal_only_source_has_no_dated_offer_estimate(self):
        result = audit(self.raw, self.index, self.contract)
        self.assertEqual((result["historical_cutoffs"], result["offers"], result["supplier_ids"]),
                         (400, 162, 10))
        self.assertEqual((result["offers_with_typed_calendar"],
                          result["offers_with_complete_min_mode_max"],
                          result["offers_supporting_dated_estimate_fields"]), (0, 0, 0))
        self.assertTrue(result["calendar_review_open"])

    def test_all_historical_modal_offers_stay_undated_even_with_a_calendar(self):
        source = json.loads(self.raw)
        as_of = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
        for offer in source["offers"]:
            with self.subTest(offer=offer["supplier_item_id"]):
                hypothetical = dict(offer, order_calendar_json={
                    "working_weekdays": [1, 2, 3, 4, 5],
                    "holiday_dates": [], "time_zone": "Europe/Berlin",
                })
                self.assertIsNone(estimate_supplier_offer(hypothetical, as_of))

    def test_tampered_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "pinned index"):
            audit(self.raw + b" ", self.index, self.contract)

    def test_calendar_alone_does_not_supply_missing_lead_bounds(self):
        source = json.loads(self.raw)
        source["offers"][0]["order_calendar_json"] = {
            "working_weekdays": [1, 2, 3, 4, 5], "holiday_dates": [],
            "time_zone": "Europe/Amsterdam",
        }
        raw = json.dumps(source, sort_keys=True).encode()
        index = deepcopy(self.index)
        index["source_sha256"][SOURCE] = hashlib.sha256(raw).hexdigest()
        result = audit(raw, index, self.contract)
        self.assertEqual(result["offers_with_typed_calendar"], 1)
        self.assertEqual(result["offers_supporting_dated_estimate_fields"], 0)


if __name__ == "__main__":
    unittest.main()
