"""D4 feedback is a code/path only, not a corrected business answer."""

import unittest

from dealdesk_phase2.fulfillment_correction import TOTAL_ERROR
from dealdesk_phase2.hybrid_contracts import HybridContractError, strict_binding
from dealdesk_phase2.hybrid_revision import feedback_for
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_candidate_m17 import fake_input, ledger, proposal


def dated_ledger():
    events = ledger()
    refs = events[0]["returned_refs"]
    events[0]["result"]["findings"]["binding_options"] = [
        {"stock_id": refs[0].split(":", 1)[1], "supply_ids": [],
         "arrival": "2026-09-04"},
        {"stock_id": None, "supply_ids": [refs[1].split(":", 1)[1]],
         "arrival": "2026-09-08"}]
    return events


class RevisionTests(unittest.TestCase):
    def test_format_and_required_field_feedback_never_supply_a_replacement(self):
        events = dated_ledger()
        raw = proposal(early="08")
        with self.assertRaises(HybridContractError) as caught:
            strict_binding(raw, fake_input(), events)
        feedback = feedback_for(raw, fake_input(), events, failure=caught.exception)
        self.assertEqual(feedback["constraint_code"], "quantity_format")
        self.assertEqual(feedback["field_paths"], ["payload.delivery_slices[0].quantity"])
        self.assertFalse(any(x in str(feedback) for x in ("08", "2026-09-04", "inventory:",
                                                      "requested_quantity", "proposed_total")))
        missing = proposal()
        missing.pop("tradeoff_code")
        self.assertEqual(feedback_for(missing, fake_input(), events,
            failure=HybridContractError("invalid_binding_shape"))["constraint_code"],
            "required_field_missing")
        missing["delivery_slices"][0]["quantity"] = "08"
        self.assertIsNone(feedback_for(missing, fake_input(), events,
            failure=HybridContractError("invalid_binding_shape")))
        both = proposal(early="08")
        both["delivery_slices"][1]["quantity"] = "02"
        self.assertIsNone(feedback_for(both, fake_input(), events,
            failure=HybridContractError("quantity_noncanonical:0")))
        self.assertIsNone(feedback_for(raw, fake_input(), events,
                                       failure=caught.exception, already_revised=True))

    def test_total_mismatch_is_not_a_suggested_sum(self):
        feedback = feedback_for(proposal(), fake_input(), dated_ledger(),
                                failure=ValueError(TOTAL_ERROR))
        self.assertEqual(feedback["constraint_code"], "quantity_sum_mismatch")
        self.assertNotIn("10", str(feedback))
        self.assertNotIn("proposed_total", str(feedback))

    def test_bad_binding_conditional_and_unknown_verifier_are_terminal(self):
        events = dated_ledger()
        bad = proposal(early="08")
        bad["delivery_slices"][0]["source_refs"] = events[0]["returned_refs"][1:]
        self.assertIsNone(feedback_for(bad, fake_input(), events,
                                      failure=HybridContractError("quantity_noncanonical:0")))
        wrong_total = proposal()
        wrong_total["delivery_slices"][0]["source_refs"] = events[0]["returned_refs"][1:]
        self.assertIsNone(feedback_for(wrong_total, fake_input(), events,
                                      failure=ValueError(TOTAL_ERROR)))
        for failure in (EvidenceMismatch("unsupported binding"),
                        ValueError("unknown verifier error")):
            self.assertIsNone(feedback_for(proposal(), fake_input(), events, failure=failure))
        self.assertIsNone(feedback_for(proposal(), fake_input(),
                                      ledger(evidence="unsupported_capability"),
                                      failure=ValueError(TOTAL_ERROR)))


if __name__ == "__main__":
    unittest.main()
