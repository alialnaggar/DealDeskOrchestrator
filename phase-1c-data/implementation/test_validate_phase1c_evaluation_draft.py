"""Keep development examples separate from unreviewed oracle drafts."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

import yaml

from validate_phase1c_evaluation_draft import validate


HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent / "evaluation"


class EvaluationAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads((EVALUATION / "development_inputs.json").read_text())
        cls.oracle = json.loads((EVALUATION / "reviewer_oracle_draft.json").read_text())
        cls.matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())

    def test_development_cases_validate_but_review_count_stays_zero(self):
        self.assertEqual(validate(self.inputs, self.oracle, self.matrix), [])
        self.assertEqual(self.oracle["independently_reviewed_cases"], 0)
        self.assertEqual(len(self.inputs["cases"]), 2)
        self.assertEqual(self.matrix["evaluation"]["target_cases"], 36)
        self.assertEqual(self.inputs["cases"][0]["requested_delivery_date"], "2026-09-04")
        self.assertEqual(self.inputs["cases"][0]["candidate_slices"][1]["arrival_date"], "2026-09-08")

    def test_expected_outcome_or_review_claim_cannot_enter_agent_input(self):
        inputs = deepcopy(self.inputs)
        inputs["cases"][0]["candidate_slices"][0]["expected"] = "approved"
        self.assertTrue(any("answer fields" in x for x in validate(inputs, self.oracle, self.matrix)))
        oracle = deepcopy(self.oracle)
        oracle["cases"][0]["review_status"] = "independently_reviewed"
        self.assertTrue(any("cannot claim independent review" in x
                            for x in validate(self.inputs, oracle, self.matrix)))

    def test_unsupported_or_reused_evidence_cannot_pass_as_a_well_formed_case(self):
        inputs = deepcopy(self.inputs)
        inputs["cases"][0]["candidate_slices"][1]["evidence_ids"] = ["NOT-A-SOURCE"]
        self.assertTrue(any("evidence reference" in x for x in validate(inputs, self.oracle, self.matrix)))
        inputs = deepcopy(self.inputs)
        inputs["cases"][0]["candidate_slices"][1]["evidence_ids"] = ["DEV-INV-8-A"]
        self.assertTrue(any("reused across slices" in x for x in validate(inputs, self.oracle, self.matrix)))
        inputs = deepcopy(self.inputs)
        inputs["cases"][0]["source_evidence"][1]["available_date"] = "2026-09-09"
        self.assertTrue(any("cannot cover cited slice" in x for x in validate(inputs, self.oracle, self.matrix)))

    def test_oracle_references_must_identify_frozen_facts(self):
        oracle = deepcopy(self.oracle)
        oracle["cases"][0]["expected"]["supporting_evidence_ids"] = ["NOT-A-SOURCE"]
        self.assertTrue(any("oracle cites unknown" in x
                            for x in validate(self.inputs, oracle, self.matrix)))

    def test_malformed_source_fails_closed_without_exception(self):
        inputs = deepcopy(self.inputs)
        inputs["cases"][0]["source_evidence"][1]["quantity"] = "two"
        self.assertTrue(any("invalid source fact" in x
                            for x in validate(inputs, self.oracle, self.matrix)))
        inputs = deepcopy(self.inputs)
        inputs["cases"][1]["source_evidence"][1]["binding"] = True
        self.assertTrue(any("commitment kind" in x
                            for x in validate(inputs, self.oracle, self.matrix)))


if __name__ == "__main__":
    unittest.main()
