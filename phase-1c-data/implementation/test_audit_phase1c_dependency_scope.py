"""Pin the effect of a catalogue-wide dependency on existing submissions."""

import unittest

from audit_phase1c_dependency_scope import audit


class DependencyScopeTests(unittest.TestCase):
    def test_existing_submissions_that_would_gain_a_block(self):
        report = audit()
        self.assertEqual((report["historical_deals"], report["pilot_deals"]), (400, 36))
        self.assertEqual(report["source_without_target"]["historical"],
                         ["HIST-DEAL-0060", "HIST-DEAL-0121", "HIST-DEAL-0123",
                          "HIST-DEAL-0133", "HIST-DEAL-0239"])
        self.assertEqual(report["source_without_target"]["pilot"], ["CONFLICT-DEAL-13"])
        self.assertEqual(report["existing_safe_requires_pairs"], 0)
        self.assertEqual(report["source_with_target"],
                         {"historical": [], "pilot": []})


if __name__ == "__main__":
    unittest.main()
