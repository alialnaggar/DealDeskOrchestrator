"""Source identity and incomplete-evidence fail-closed checks (no database)."""

from copy import deepcopy
from pathlib import Path
import json
import unittest

from credit_evidence_gate import CONTROL, INDEX, canonical, classify, digest


class CreditEvidenceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(CONTROL.read_bytes())
        cls.index = json.loads(INDEX.read_bytes())

    def check_modified(self, source, index):
        index["control_source_sha256"] = __import__("hashlib").sha256(
            (json.dumps(source, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode()
        ).hexdigest()
        index["controls"] = [{"case_id": c["case_id"], "source_sha256": digest(c)}
                             for c in source["cases"]]
        raw = (json.dumps(source, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode()
        return classify(raw, json.dumps(index).encode(), "EVAL-PREP-041")

    def test_distinct_states_are_not_clearance(self):
        forty = classify(CONTROL.read_bytes(), INDEX.read_bytes(), "EVAL-PREP-040")
        forty_one = classify(CONTROL.read_bytes(), INDEX.read_bytes(), "EVAL-PREP-041")
        self.assertEqual(forty["source_evidence_state"], "declared_complete_nonempty")
        self.assertEqual(forty["overdue_ar_eur"], "700.00")
        self.assertEqual(forty_one["source_evidence_state"], "unknown_incomplete")
        self.assertIsNone(forty_one["overdue_ar_eur"])
        self.assertFalse(forty["credit_clearance_allowed"])
        self.assertFalse(forty_one["credit_clearance_allowed"])
        self.assertFalse(forty_one["selection_verified"])

    def test_mutated_source_without_index_fails(self):
        raw = CONTROL.read_bytes().replace(b"explicitly_incomplete_unknown",
                                           b"declared_complete_zero")
        with self.assertRaises(ValueError):
            classify(raw, INDEX.read_bytes(), "EVAL-PREP-041")

    def test_even_rehashed_incomplete_to_complete_fails(self):
        source, index = deepcopy(self.source), deepcopy(self.index)
        source["cases"][1]["credit_evidence_scope"]["completeness"] = "declared_complete_zero"
        with self.assertRaises(ValueError):
            self.check_modified(source, index)

    def test_stray_receivable_or_wrong_customer_fails(self):
        source, index = deepcopy(self.source), deepcopy(self.index)
        source["cases"][1]["tables"]["accounts_receivable"] = [
            {**source["cases"][0]["tables"]["accounts_receivable"][0],
             "customer_id": "OTHER"}]
        source["cases"][1]["credit_evidence_scope"]["selected_receivables_count"] = 1
        with self.assertRaises(ValueError):
            self.check_modified(source, index)

    def test_unknown_case_fails(self):
        with self.assertRaises(ValueError):
            classify(CONTROL.read_bytes(), INDEX.read_bytes(), "EVAL-PREP-042")


if __name__ == "__main__":
    unittest.main()
