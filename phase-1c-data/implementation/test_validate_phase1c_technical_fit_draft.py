"""Check that every fictional BOM candidate fails closed on incompatible facts."""

from copy import deepcopy
import json
import unittest

from validate_phase1c_technical_fit_draft import HERE, validate


class FullSyntheticFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
        cls.draft = json.loads((HERE / "phase1c_technical_fit_draft.json").read_text())

    def test_all_current_boms_and_substitutes_are_covered(self):
        result = validate(self.portfolio, self.draft)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["checked_component_specs"], 36)
        self.assertEqual(result["checked_boms"], 24)
        self.assertEqual(result["checked_alternatives"], 25)
        self.assertEqual(len(result["alternatives"]["BOM-001"]), 2)
        self.assertTrue(result["synthetic_fit_check_passed"])
        self.assertFalse(result["ready_for_generation"])

    def test_shared_drive_interface_mismatch_affects_each_using_bom(self):
        draft = deepcopy(self.draft)
        draft["component_specs"]["COMP-STORAGE-007"]["host_interface"] = "SATA"
        errors = validate(self.portfolio, draft)["errors"]
        self.assertTrue(any("BOM-019" in error and "storage interface mismatch" in error
                            for error in errors))
        self.assertTrue(any("BOM-024" in error and "storage interface mismatch" in error
                            for error in errors))

    def test_substitute_power_failure_cannot_hide_behind_preferred_kit(self):
        draft = deepcopy(self.draft)
        draft["component_specs"]["COMP-NETWORK_AND_POWER-002"]["psu_output_watts"] = 100
        result = validate(self.portfolio, draft)
        self.assertTrue(result["alternatives"]["BOM-001"][0]["fit"])
        self.assertFalse(result["alternatives"]["BOM-001"][1]["fit"])
        self.assertTrue(any("BOM-001" in error and "power supply" in error
                            for error in result["errors"]))

    def test_slots_cooling_and_platform_are_real_constraints(self):
        draft = deepcopy(self.draft)
        draft["component_specs"]["COMP-CHASSIS_AND_OTHER-002"]["drive_slots"] = 1
        draft["component_specs"]["COMP-CHASSIS_AND_OTHER-005"]["cooling_capacity_watts"] = 100
        portfolio = deepcopy(self.portfolio)
        component = next(p for p in portfolio["products"] if p["product_id"] == "COMP-COMPUTE-004")
        component["attributes_json"]["supported_platforms"] = ["workstation"]
        errors = validate(portfolio, draft)["errors"]
        self.assertTrue(any("insufficient drive slots" in error for error in errors))
        self.assertTrue(any("enclosure cooling" in error for error in errors))
        self.assertTrue(any("does not declare platform server" in error for error in errors))

    def test_missing_spec_or_synthetic_basis_is_rejected(self):
        draft = deepcopy(self.draft)
        draft["component_specs"].pop("COMP-STORAGE-003")
        draft["basis"] = "manufacturer_certified"
        errors = validate(self.portfolio, draft)["errors"]
        self.assertTrue(any("synthetic basis" in error for error in errors))
        self.assertTrue(any("cover exactly all components" in error for error in errors))

    def test_nonfinite_power_cannot_pass(self):
        draft = deepcopy(self.draft)
        draft["component_specs"]["COMP-COMPUTE-001"]["rated_watts"] = float("nan")
        self.assertTrue(any("rated_watts must be positive" in error
                            for error in validate(self.portfolio, draft)["errors"]))

    def test_catalogue_and_companion_specs_must_match(self):
        portfolio = deepcopy(self.portfolio)
        component = next(p for p in portfolio["products"] if p["product_id"] == "COMP-STORAGE-001")
        component["attributes_json"]["host_interface"] = "SATA"
        self.assertTrue(any("catalogue attributes differ" in error
                            for error in validate(portfolio, self.draft)["errors"]))


if __name__ == "__main__":
    unittest.main()
