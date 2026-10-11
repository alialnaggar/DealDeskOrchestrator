"""First shortage proposal: validate its shape and expose the current rerun gap."""

from dataclasses import replace
from datetime import date, datetime, timezone
from uuid import UUID
import unittest

from phase1c_candidate import Candidate, DeliverySlice, FieldChange, review_partial_delivery, verify_run_correlation, CHECKS


RUN = UUID("00000000-0000-4000-8000-000000000001")
AS_OF = datetime(2026, 9, 1, tzinfo=timezone.utc)


def shortage_candidate():
    return Candidate(
        candidate_id="C-SHORT-1", parent_deal_id="D-SHORT", parent_run_id=RUN,
        proposal_kind="partial_delivery",
        changes=(FieldChange(None, "requested_delivery_date", date(2026, 9, 4), date(2026, 9, 11)),),
        customer_constraints=("20 units", "partial allowed", "delivery target 4 September"),
        unmet_constraints=("delivery target 4 September",),
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
        self.assertIn("delivery target 4 September", candidate.unmet_constraints)

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

    def test_separate_run_on_same_parent_deal_cannot_verify_candidate(self):
        candidate = shortage_candidate()
        parent = {"run_id": RUN, "deal_id": candidate.parent_deal_id}
        proposed = {"run_id": UUID("00000000-0000-4000-8000-000000000002"),
                    "deal_id": candidate.parent_deal_id, "as_of_at": AS_OF,
                    "catalog_version_used": candidate.catalog_version,
                    "applied_policy_set_code": candidate.policy_set_code,
                    "data_snapshot_ref": candidate.data_snapshot_ref,
                    "input_snapshot_json": {"candidate_id": candidate.candidate_id}}
        with self.assertRaisesRegex(ValueError, "unchanged parent"):
            verify_run_correlation(candidate, parent, proposed)
        proposed["deal_id"] = "D-OTHER"
        verify_run_correlation(candidate, parent, proposed)  # Correlation only, not proof of a full rerun.
        proposed["data_snapshot_ref"] = "SNAP-NEW"
        with self.assertRaisesRegex(ValueError, "frozen context"):
            verify_run_correlation(candidate, parent, proposed)


if __name__ == "__main__":
    unittest.main()
