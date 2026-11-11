"""Six-stage M4 eligibility controls; no model, sender or approval capability."""

import unittest

from dealdesk_phase2.graph_state import SPECIALISTS
from dealdesk_phase2.m4_correction_policy import VERSION, disposition


class M4Policy(unittest.TestCase):
    def test_only_existing_fulfillment_repairs_have_an_executable_wire(self):
        for name in SPECIALISTS:
            for code in ("quantity_format", "quantity_sum_mismatch"):
                with self.subTest(specialist=name, code=code):
                    decision = disposition(name, code, fully_returned=True,
                                           remaining_turns=1)
                    self.assertEqual(decision["version"], VERSION)
                    self.assertEqual(decision["eligible"], name == "fulfillment")
        with self.assertRaises(ValueError):
            disposition("unknown", "quantity_format", fully_returned=True,
                        remaining_turns=1)

    def test_noncorrectable_security_transport_and_budget_stop(self):
        for code in (None, "http_400", "http_429", "transport_timeout",
                     "reserved_only", "identity_mismatch", "source_mismatch",
                     "subject_mismatch", "customer_mismatch", "permission_denied",
                     "fabricated_citation", "unsupported_source_access",
                     "business_rule_violation", "invalid_terminal_output"):
            with self.subTest(code=code):
                self.assertFalse(disposition("fulfillment", code,
                    fully_returned=True, remaining_turns=1)["eligible"])
        self.assertEqual(disposition("fulfillment", "quantity_format",
            fully_returned=False, remaining_turns=1)["reason"],
            "response_not_fully_returned")
        for remaining in (0, -1, True, None):
            with self.subTest(remaining=remaining):
                self.assertFalse(disposition("fulfillment", "quantity_format",
                    fully_returned=True, remaining_turns=remaining)["eligible"])


if __name__ == "__main__":
    unittest.main()
