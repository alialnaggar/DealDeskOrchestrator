"""Source-only evaluation preparation rejects reuse across dated operational modes."""

from copy import deepcopy
import unittest

from phase1c_candidate import INPUT_TABLES, reader_input_digest
from phase1c_evaluation_input import (prepare_review_input, verify_review_input,
    build_development_exclusion_manifest, excluded_ids_from_manifest)


class EvaluationSourceIsolationTests(unittest.TestCase):
    def bundle(self, table, column, source_id):
        bundle = {key: [] for key in INPUT_TABLES}
        bundle["deal"] = {"deal_id": "EVAL-SOURCE-DEAL-1"}
        bundle["run"] = {
            "run_id": "EVAL-SOURCE-RUN-1", "deal_id": "EVAL-SOURCE-DEAL-1",
            "as_of_at": "2026-09-01T12:00:00Z",
            "catalog_version_used": "CATALOGUE_2026_V1",
            "applied_policy_set_code": "BASELINE_2026",
            "data_snapshot_ref": "EVAL-SOURCE-SNAPSHOT-1",
            "config_hash": "source-isolation-test",
        }
        bundle[table] = [{column: source_id}]
        return bundle

    def test_all_dated_operational_source_ids_are_checked(self):
        for table, column in (
            ("inventory", "inventory_id"),
            ("inbound_supply", "supply_id"),
            ("production_capacity", "capacity_id"),
            ("digital_capacity", "digital_capacity_id"),
        ):
            with self.subTest(table=table):
                bundle = self.bundle(table, column, "DEV-SOURCE-1")
                with self.assertRaisesRegex(ValueError, "reuses development"):
                    prepare_review_input(bundle, case_id="EVAL-PREP-SOURCE-1",
                                         excluded_source_ids=("DEV-SOURCE-1",))
                packet = prepare_review_input(bundle, case_id="EVAL-PREP-SOURCE-1",
                                              excluded_source_ids=("OTHER-SOURCE",))
                self.assertTrue(verify_review_input(
                    packet, expected_case_id="EVAL-PREP-SOURCE-1",
                    expected_source_digest=reader_input_digest(bundle)))
                self.assertNotIn("facts", packet["payload"])
                self.assertNotIn("candidate_trace", packet["payload"])


    def test_sealed_registry_collects_all_development_source_types(self):
        fixtures = []
        for index, (table, column) in enumerate((
            ("inventory", "inventory_id"),
            ("inbound_supply", "supply_id"),
            ("production_capacity", "capacity_id"),
            ("digital_capacity", "digital_capacity_id"),
        ), 1):
            bundle = self.bundle(table, column, f"DEV-SOURCE-{index}")
            bundle["run"]["run_id"] = f"DEV-RUN-{index}"
            bundle["deal"]["deal_id"] = f"DEV-DEAL-{index}"
            fixtures.append(bundle)
        manifest = build_development_exclusion_manifest(fixtures)
        excluded = excluded_ids_from_manifest(manifest, expected_run_count=4)
        self.assertEqual(excluded, {f"DEV-SOURCE-{n}" for n in range(1, 5)})
        self.assertEqual(manifest["payload"]["run_count"], 4)
        self.assertEqual(manifest["payload"]["run_ids"],
                         [f"DEV-RUN-{n}" for n in range(1, 5)])
        self.assertEqual(manifest["payload"]["deal_ids"],
                         [f"DEV-DEAL-{n}" for n in range(1, 5)])
        self.assertNotIn("answers", manifest["payload"])
        for bundle in fixtures:
            with self.assertRaisesRegex(ValueError, "reuses development"):
                prepare_review_input(bundle, case_id="EVAL-PREP-SOURCE-1",
                                     excluded_source_ids=excluded)
        tampered = deepcopy(manifest)
        tampered["payload"]["source_ids_by_table"]["inventory"].append("OTHER")
        with self.assertRaisesRegex(ValueError, "seal differs"):
            excluded_ids_from_manifest(tampered, expected_run_count=4)
        with self.assertRaisesRegex(ValueError, "seal differs"):
            excluded_ids_from_manifest(manifest, expected_run_count=3)
        with self.assertRaisesRegex(ValueError, "Duplicate development"):
            build_development_exclusion_manifest(fixtures + fixtures[:1])
        alternative_run = self.bundle("inventory", "inventory_id", "DEV-SOURCE-1")
        alternative_run["run"]["run_id"] = "DEV-RUN-5"
        alternative_run["deal"]["deal_id"] = "DEV-DEAL-1"
        second = build_development_exclusion_manifest(fixtures + [alternative_run])
        self.assertEqual(second["payload"]["deal_ids"],
                         [f"DEV-DEAL-{n}" for n in range(1, 5)])
        self.assertEqual((second["payload"]["run_count"], second["payload"]["deal_count"]),
                         (5, 4))
        self.assertEqual(excluded_ids_from_manifest(
            second, expected_run_count=5, expected_deal_count=4), excluded)


if __name__ == "__main__":
    unittest.main()
