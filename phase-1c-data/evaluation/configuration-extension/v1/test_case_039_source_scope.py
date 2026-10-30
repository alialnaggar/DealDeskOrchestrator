"""Pinned supplemental 039 source-only compatibility scope check."""

from hashlib import sha256
from pathlib import Path
import json
import unittest

HERE = Path(__file__).resolve().parent


class Case039SourceScopeTests(unittest.TestCase):
    def test_pinned_v2_dependency_and_absent_target(self):
        raw = (HERE / "source_cases.json").read_bytes()
        index = json.loads((HERE / "packet_index.json").read_bytes())
        self.assertEqual(sha256(raw).hexdigest(), index["source_definition_sha256"])
        source = json.loads(raw)
        self.assertEqual(source["base_source_definition_sha256"],
                         index["base_source_definition_sha256"])
        self.assertEqual([c["case_id"] for c in source["cases"]],
                         ["EVAL-PREP-037", "EVAL-PREP-038", "EVAL-PREP-039"])
        case = source["cases"][2]
        run = case["tables"]["deal_runs"][0]
        rule, = case["tables"]["compatibility_rules"]
        lines = case["tables"]["deal_lines"]
        self.assertEqual(run["catalog_version_used"], "CATALOGUE_2026_V2")
        self.assertEqual(rule["catalog_version"], run["catalog_version_used"])
        self.assertEqual(rule["rule_type"], "requires_product")
        self.assertEqual(rule["scope_type"], "whole_deal")
        self.assertEqual(rule["severity"], "blocker")
        self.assertEqual(rule["condition_json"], {"operator": "present"})
        self.assertEqual([line["product_id"] for line in lines],
                         [rule["source_product_id"]])
        self.assertNotIn(rule["target_product_id"],
                         {line["product_id"] for line in lines})
        self.assertEqual(case["provider_manifest"]["records"], [])
        self.assertEqual(index["independently_reviewed_answers"], 0)
        self.assertEqual(index["cases"][2]["packet_sha256"],
                         "83f65e17b9bfddee6bd32f76742678f3bf60c8e4ffea94d2d3d6479f717b2b99")


if __name__ == "__main__":
    unittest.main()
