"""Compatibility report boundaries; live values are measured on CI PostgreSQL."""

import unittest
from unittest.mock import patch

from dealdesk_phase2.compat_m19 import _shape, compare, PIN


class CompatibilityContractTests(unittest.TestCase):
    def test_nested_reader_shape_retains_types_and_field_names(self):
        self.assertEqual(_shape({"run": {"run_id": "R"}, "rows": [{"quantity": 8}]}),
                         {"rows": [{"quantity": "int"}], "run": {"run_id": "str"}})
        self.assertEqual(_shape({"rows": []}), {"rows": []})

    @patch("dealdesk_phase2.compat_m19.subprocess.check_output", return_value="wrong-sha\n")
    def test_diagnostic_refuses_to_compare_an_unpinned_checkout(self, _):
        with self.assertRaisesRegex(ValueError, "approved Phase 1C SHA"):
            compare("/tmp/pinned", "/tmp/development")

    def test_pin_is_an_exact_commit_not_a_moving_branch(self):
        self.assertEqual(PIN, "90c0bc8e285ee69262c7db826b786096a77ad004")


if __name__ == "__main__":
    unittest.main()
