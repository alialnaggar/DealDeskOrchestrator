"""First shortage proposal: validate its shape and expose the current rerun gap."""

from dataclasses import replace
from datetime import date, datetime, timezone
from uuid import UUID
import unittest

from phase1c_candidate import Candidate, DeliverySlice, FieldChange, review_partial_delivery, assess_reader_slices, CHECKS


RUN = UUID("00000000-0000-4000-8000-000000000001")
AS_OF = datetime(2026, 9, 1, tzinfo=timezone.utc)


def shortage_candidate():
    return Candidate(
        candidate_id="C-SHORT-1", parent_deal_id="D-SHORT", parent_run_id=RUN,
        proposal_kind="partial_delivery",
        changes=(FieldChange(None, "proposed_delivery_slices",
                             (("L1", 20, date(2026, 9, 4)),),
                             (("L1", 12, date(2026, 9, 4)),
                              ("L1", 8, date(2026, 9, 11)))),),
        customer_constraints=("20 units", "partial allowed", "original_requested_delivery_date"),
        unmet_constraints=("original_requested_delivery_date",),
        delivery_slices=(DeliverySlice("L1", 12, date(2026, 9, 4), ("STOCK-12",), "confirmed"),
                         DeliverySlice("L1", 8, date(2026, 9, 11), ("OFFER-8",), "conditional")),
        evidence_ids=("STOCK-12", "OFFER-8"), as_of_at=AS_OF,
        catalog_version="CATALOGUE_2026_V1", policy_set_code="BASELINE_2026",
        data_snapshot_ref="SNAP-1", assumptions=("Eight later units require supplier confirmation",),
        tradeoff="12 on time; 8 later only if the supplier confirms. Customer must accept the split.",
    )


class CandidateContractTests(unittest.TestCase):
    def test_shortage_partial_is_a_proposal_not_a_verified_decision(self):
        candidate = shortage_candidate()
        trace = review_partial_delivery(candidate, original_quantities={"L1": 20},
                                        requested_date=date(2026, 9, 4), partial_allowed=True)
        self.assertEqual(trace["required_reruns"], list(CHECKS))
        self.assertEqual(trace["full_reader_recheck"], "blocked_by_candidate_input_contract")
        self.assertEqual(candidate.delivery_slices[1].commitment, "conditional")
        self.assertIn("original_requested_delivery_date", candidate.unmet_constraints)

    def test_permission_quantity_and_group_are_hard_boundaries(self):
        candidate = shortage_candidate()
        with self.assertRaisesRegex(ValueError, "permitted"):
            review_partial_delivery(candidate, original_quantities={"L1": 20},
                                    requested_date=date(2026, 9, 4), partial_allowed=False)
        with self.assertRaisesRegex(ValueError, "every original unit"):
            review_partial_delivery(candidate, original_quantities={"L1": 21},
                                    requested_date=date(2026, 9, 4), partial_allowed=True)
        with self.assertRaisesRegex(ValueError, "group"):
            review_partial_delivery(candidate, original_quantities={"L1": 20},
                                    requested_date=date(2026, 9, 4), partial_allowed=True,
                                    indivisible_groups=(frozenset({"L1"}),))

    def test_candidate_identity_and_evidence_cannot_be_implicit(self):
        candidate = shortage_candidate()
        with self.assertRaisesRegex(ValueError, "unique"):
            replace(candidate, changes=candidate.changes * 2)
        with self.assertRaisesRegex(ValueError, "assumption"):
            replace(candidate, assumptions=())
        with self.assertRaisesRegex(ValueError, "context"):
            replace(candidate, data_snapshot_ref="")
        with self.assertRaisesRegex(ValueError, "unmet original"):
            review_partial_delivery(replace(candidate, unmet_constraints=()),
                                    original_quantities={"L1": 20},
                                    requested_date=date(2026, 9, 4), partial_allowed=True)

    def test_original_date_is_distinct_from_candidate_schedule(self):
        candidate = shortage_candidate()
        self.assertEqual(candidate.changes[0].before[0][2], date(2026, 9, 4))
        self.assertEqual(candidate.delivery_slices[-1].arrival_date, date(2026, 9, 11))
        with self.assertRaisesRegex(ValueError, "preserve"):
            replace(candidate, changes=(FieldChange(None, "requested_delivery_date",
                                                     date(2026, 9, 4), date(2026, 9, 11)),))

    def test_reader_selects_location_matching_actual_cited_sources(self):
        candidate = shortage_candidate()
        candidate = replace(candidate, evidence_ids=("W-STOCK", "W-RECEIPT"),
                            delivery_slices=(
                                replace(candidate.delivery_slices[0], evidence_ids=("W-STOCK",)),
                                replace(candidate.delivery_slices[1], evidence_ids=("W-RECEIPT",),
                                        commitment="confirmed")))
        bundle = {
            "run": {"run_id": RUN, "as_of_at": AS_OF,
                    "catalog_version_used": candidate.catalog_version,
                    "applied_policy_set_code": candidate.policy_set_code,
                    "data_snapshot_ref": candidate.data_snapshot_ref},
            "deal": {"deal_id": candidate.parent_deal_id,
                     "requested_delivery_date": date(2026, 9, 4),
                     "terms_json": {"allow_partial_delivery": True}},
            "lines": [{"deal_line_id": "L1", "quantity": 20,
                       "fulfillment_mode": "stocked_finished", "fulfillment_group_code": None}],
            "facts": {"lines": [{"shipping_options": [
                {"location": "Central", "arrival": date(2026, 9, 4),
                 "quantity": 12, "stock_id": "C-STOCK", "supply_ids": []},
                {"location": "Central", "arrival": date(2026, 9, 11),
                 "quantity": 20, "stock_id": "C-STOCK", "supply_ids": ["C-RECEIPT"]},
                {"location": "West", "arrival": date(2026, 9, 4),
                 "quantity": 12, "stock_id": "W-STOCK", "supply_ids": []},
                {"location": "West", "arrival": date(2026, 9, 11),
                 "quantity": 20, "stock_id": "W-STOCK", "supply_ids": ["W-RECEIPT"]},
            ]}]},
        }
        self.assertEqual(assess_reader_slices(candidate, bundle)["location"], "West")


if __name__ == "__main__":
    unittest.main()
