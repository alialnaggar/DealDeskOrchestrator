"""Check the source-only V1/V2 compatibility scope and detect accidental spread."""

from copy import deepcopy
import json
import unittest

from audit_phase1c_compatibility_scope import HERE, FIXTURES, audit


class CompatibilityScopeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = {name: (HERE / name).read_text() for name in FIXTURES}
        cls.evaluation = json.loads((HERE.parent / "evaluation/provisional_cases.json").read_text())

    def test_pinned_sources_have_narrow_scope(self):
        report = audit(self.sql, self.evaluation)
        self.assertEqual(len(report["development_rules"]), 3)
        self.assertEqual(len(report["evaluation_rule_rows"]), 4)
        self.assertFalse(report["generic_families_in_evaluation"])
        self.assertEqual(report["accepted_evaluation_answers"], 0)

    def test_v1_dependency_cannot_silently_enter_development(self):
        changed = dict(self.sql)
        changed["phase1c_dependency_pilot.sql"] = changed["phase1c_dependency_pilot.sql"].replace(
            "'V2-REQUIRES-ADDON', 'CATALOGUE_2026_V2'",
            "'V2-REQUIRES-ADDON', 'CATALOGUE_2026_V1'")
        with self.assertRaisesRegex(ValueError, "development compatibility scope"):
            audit(changed, self.evaluation)

    def test_evaluation_rule_family_change_is_detected(self):
        changed = deepcopy(self.evaluation)
        case = next(c for c in changed["cases"] if c["case_id"] == "EVAL-PREP-027")
        case["tables"]["compatibility_rules"][0]["rule_type"] = "requires_product"
        with self.assertRaisesRegex(ValueError, "evaluation compatibility scope"):
            audit(self.sql, changed)

    def test_development_service_region_or_dependency_target_change_is_detected(self):
        for filename, before, after in (
            ("phase1c_vertical_pilot.sql", '"eligible":true', '"eligible":false'),
            ("phase1c_dependency_pilot.sql", "WORKPLACE-005-V2", "WORKPLACE-006-V2"),
        ):
            with self.subTest(filename=filename):
                changed = dict(self.sql)
                changed[filename] = changed[filename].replace(before, after)
                with self.assertRaisesRegex(ValueError, "development compatibility scope"):
                    audit(changed, self.evaluation)

    def test_evaluation_region_or_eligibility_change_is_detected(self):
        for field, value in (("region", "DE-BY"), ("eligible", False)):
            with self.subTest(field=field):
                changed = deepcopy(self.evaluation)
                case = next(c for c in changed["cases"] if c["case_id"] == "EVAL-PREP-027")
                case["tables"]["compatibility_rules"][0]["condition_json"][field] = value
                with self.assertRaisesRegex(ValueError, "evaluation regional source semantics"):
                    audit(self.sql, changed)


if __name__ == "__main__":
    unittest.main()
