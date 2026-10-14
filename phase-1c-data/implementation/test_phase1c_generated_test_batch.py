"""Reproduce and read the provisional 100-deal generated-test batch."""

from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import unittest

import yaml

from render_phase1c_generated_test_batch import (SOURCE_FILES, build,
    eligible_customers, render_digital_manifest)
from validate_phase1c_scenario_matrix import generated_case_plan

try:
    import psycopg
except ImportError:
    psycopg = None

if psycopg is not None:
    from phase1c_reader import read_run, load_provider_evidence
    from phase1c_deal_decision import assemble_deal_decision
    from validate_phase1c_generated_rows import load_rows, validate_rows

HERE = Path(__file__).resolve().parent
FILES = ("phase1c_buildable_master.sql", "phase1c_sellable_catalogue.sql",
         "phase1c_customer_master.sql",
         "phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql",
         "phase1c_stress_pilot.sql", "phase1c_dependency_pilot.sql",
         "phase1c_generated_test_batch.sql")


class GeneratedBatchRenderTests(unittest.TestCase):
    def test_source_only_reproducibility(self):
        matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
        hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                  for name in SOURCE_FILES}
        sql, report = build(matrix, hashes, (HERE / "phase1c_customer_master.sql").read_text())
        self.assertEqual(sql, (HERE / "phase1c_generated_test_batch.sql").read_text())
        provider_manifest = render_digital_manifest(
            (HERE / "phase1c_vertical_provider_manifest.json").read_text(),
            (HERE / "phase1c_conflict_provider_manifest.json").read_text())
        report["provider_manifest_sha256"] = hashlib.sha256(
            provider_manifest.encode()).hexdigest()
        self.assertEqual(provider_manifest,
                         (HERE / "phase1c_generated_provider_manifest.json").read_text())
        self.assertEqual(report, json.loads(
            (HERE / "phase1c_generated_test_batch_report.json").read_text()))
        self.assertEqual(len(generated_case_plan(matrix)), 100)
        self.assertEqual((report["v1_deals"], report["v2_dependency_deals"],
                          report["line_count"], report["source_template_count"]),
                         (98, 2, 101, 20))
        self.assertEqual((report["eligible_customer_count"], report["customer_reassignment_count"]),
                         (37, 63))
        self.assertEqual(report["dated_stock_variant_count"], 5)
        self.assertEqual(report["dated_component_stock_variant_count"], 5)
        self.assertEqual(report["dated_confirmed_supply_variant_count"], 5)
        self.assertEqual(report["dated_digital_variant_count"], 4)
        self.assertEqual(len(set(eligible_customers((HERE / "phase1c_customer_master.sql").read_text()))), 37)
        self.assertNotIn("target_bucket", sql)
        self.assertNotIn("historical_decision", sql)
        self.assertNotIn("expected_decision", sql)


@unittest.skipUnless(psycopg is not None and os.environ.get("DATABASE_URL"),
                     "PostgreSQL integration requires psycopg and DATABASE_URL")
class GeneratedBatchDatabaseTests(unittest.TestCase):
    def test_import_reader_decision_and_row_coverage(self):
        matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
        contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            conn.execute("SET search_path TO deal_desk, public")
            try:
                before = {table: {row[next(iter(row))] for row in records}
                          for table, records in load_rows(conn).items()}
                for name in FILES:
                    for statement in re.findall(r"^(?:INSERT INTO|UPDATE deals SET) .*?;",
                                                (HERE / name).read_text(), re.M | re.S):
                        conn.execute(statement)
                rows = {table: [row for row in records
                                if row[next(iter(row))] not in before[table]]
                        for table, records in load_rows(conn).items()}
                result = validate_rows(rows, contract)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["counts"]["deals"], 138)
                self.assertEqual(result["counts"]["deal_lines"], 169)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["pass"], 2)
                self.assertEqual(result["dependency_coverage"]["finding_counts"]["fail"], 2)
                self.assertEqual(result["supplier_calendar_coverage"]["offers_missing_calendar"], [])
                statuses, modes, customers = Counter(), Counter(), Counter()
                fulfillment, availability_sources = Counter(), Counter()
                by_archetype_status = defaultdict(Counter)
                by_archetype_fulfillment = defaultdict(Counter)
                by_archetype_customers = defaultdict(set)
                by_archetype_sources = defaultdict(set)
                baseline = assemble_deal_decision(read_run(
                    conn, "00000000-0000-4000-8000-000000260001",
                    commercial_rule_mode="compiled"))
                self.assertIn("PILOT-STOCK-005", {
                    source for finding in baseline["specialists"]["availability"]
                    for source in finding["source_ids"]})
                build_baseline = assemble_deal_decision(read_run(
                    conn, "00000000-0000-4000-8000-000000260003",
                    commercial_rule_mode="compiled"))
                self.assertIn("PILOT-STOCK-002", {
                    source for finding in build_baseline["specialists"]["availability"]
                    for source in finding["source_ids"]})
                supplier_baseline_bundle = read_run(
                    conn, "00000000-0000-4000-8000-000000260002",
                    commercial_rule_mode="compiled")
                self.assertFalse(any(row["supply_id"].startswith("GEN-INBOUND-")
                                     for row in supplier_baseline_bundle["inbound_supply"]))
                supplier_baseline = assemble_deal_decision(supplier_baseline_bundle)
                self.assertIn("PILOT-INBOUND-001", {
                    source for finding in supplier_baseline["specialists"]["availability"]
                    for source in finding["source_ids"]})
                stress_bundle = read_run(
                    conn, "00000000-0000-4000-8000-000000270001",
                    commercial_rule_mode="compiled")
                self.assertFalse(any(row["supply_id"].startswith("GEN-INBOUND-")
                                     for row in stress_bundle["inbound_supply"]))
                digital_baseline_bundle = read_run(
                    conn, "00000000-0000-4000-8000-000000260004",
                    commercial_rule_mode="compiled")
                self.assertEqual([p["digital_capacity_id"]
                                  for p in digital_baseline_bundle["digital_capacity"]],
                                 ["PILOT-POOL-001"])
                digital_baseline = assemble_deal_decision(digital_baseline_bundle)
                self.assertIn("PILOT-POOL-001", {
                    source for finding in digital_baseline["specialists"]["availability"]
                    for source in finding["source_ids"]})
                digital_stress_bundle = read_run(
                    conn, "00000000-0000-4000-8000-000000270003",
                    commercial_rule_mode="compiled")
                self.assertFalse(any(p["digital_capacity_id"].startswith("GEN-DIGITAL-POOL-")
                                     for p in digital_stress_bundle["digital_capacity"]))
                provider_resolver = load_provider_evidence(
                    HERE / "phase1c_generated_provider_manifest.json")
                eligible = set(eligible_customers((HERE / "phase1c_customer_master.sql").read_text()))
                stocked_variant = 0
                build_variant = 0
                supply_variant = 0
                digital_variant = 0
                case_observations = []
                for index, slot in enumerate(generated_case_plan(matrix), 1):
                    run_id = f"00000000-0000-4000-8000-{310000 + index:012d}"
                    bundle = read_run(conn, run_id, commercial_rule_mode="compiled",
                                      digital_evidence_resolver=provider_resolver)
                    self.assertEqual(bundle["deal"]["deal_id"], slot["case_id"])
                    self.assertEqual(bundle["run"]["catalog_version_used"], slot["catalog_version"])
                    decision = assemble_deal_decision(bundle)
                    self.assertNotEqual(decision["status"], "approved")
                    statuses[decision["status"]] += 1
                    customers[bundle["deal"]["customer_id"]] += 1
                    archetype = slot["archetype_id"]
                    by_archetype_status[archetype][decision["status"]] += 1
                    by_archetype_customers[archetype].add(bundle["deal"]["customer_id"])
                    if bundle["deal"]["customer_id"] in eligible:
                        profile = conn.execute(
                            "SELECT credit_status, risk_rating, commitments_as_of_at "
                            "FROM customer_credit_profiles WHERE customer_id=%s",
                            (bundle["deal"]["customer_id"],)).fetchone()
                        self.assertEqual(profile[0], "Active")
                        self.assertIn(profile[1], ("Low", "Medium"))
                        self.assertLessEqual(profile[2], bundle["run"]["as_of_at"])
                    if slot["archetype_id"] == "CREDIT-LIMIT":
                        self.assertNotIn(bundle["deal"]["customer_id"], eligible)
                    modes.update(line["fulfillment_mode"] for line in bundle["lines"])
                    fulfillment_for_case = [fact["fulfillment_status"] for fact in bundle["facts"]["lines"]
                                            if "fulfillment_status" in fact]
                    fulfillment.update(fulfillment_for_case)
                    by_archetype_fulfillment[archetype].update(fulfillment_for_case)
                    sources_for_case = {source
                        for finding in decision["specialists"]["availability"]
                        for source in finding["source_ids"]}
                    availability_sources.update(source
                        for finding in decision["specialists"]["availability"]
                        for source in finding["source_ids"])
                    by_archetype_sources[archetype].update(sources_for_case)
                    case_observations.append({
                        "case_id": slot["case_id"],
                        "archetype_id": archetype,
                        "catalog_version": slot["catalog_version"],
                        "run_as_of_at": bundle["run"]["as_of_at"].isoformat(),
                        "customer_id": bundle["deal"]["customer_id"],
                        "line_modes": [line["fulfillment_mode"] for line in bundle["lines"]],
                        "observed_decision_status": decision["status"],
                        "observed_fulfillment_statuses": fulfillment_for_case,
                        "availability_finding_source_ids": sorted(sources_for_case),
                        "reader_visible_raw_source_ids": {
                            "inventory": sorted(row["inventory_id"] for row in bundle["inventory"]),
                            "inbound_supply": sorted(row["supply_id"] for row in bundle["inbound_supply"]),
                            "digital_capacity": sorted(row["digital_capacity_id"]
                                                       for row in bundle["digital_capacity"]),
                        },
                        "digital_facts": [
                            {"status": digital["status"],
                             "full_term_verified": any(pool["full_term_verified"]
                                                       for pool in digital.get("pools", []))}
                            for fact in bundle["facts"]["lines"]
                            for digital in [fact.get("digital")] if digital is not None
                        ],
                        "service_facts": [
                            {"status": service["status"],
                             "coverage": service["coverage"],
                             "coverage_rule_ids": service["coverage_rule_ids"],
                             "requested_date": (service["requested_date"].isoformat()
                                                if service["requested_date"] else None),
                             "slot_committed": service["slot_committed"]}
                            for fact in bundle["facts"]["lines"]
                            for service in [fact.get("service")] if service is not None
                        ],
                        "service_coverage_rule_ids": sorted({
                            source for fact in bundle["facts"]["lines"]
                            for source in fact.get("service", {}).get("coverage_rule_ids", [])
                        }),
                        "applicable_compatibility_rules": sorted(
                            [{"rule_id": finding["compatibility_rule_id"],
                              "observed_status": finding["status"]}
                             for finding in bundle["facts"]["compatibility"]
                             if finding["status"] in ("pass", "fail")],
                            key=lambda row: row["rule_id"]),
                        "independent_review": "pending",
                    })
                    if slot["archetype_id"] == "STOCK-READY":
                        sources = {source for finding in decision["specialists"]["availability"]
                                   for source in finding["source_ids"]}
                        expected = ("PILOT-STOCK-005" if stocked_variant == 0
                                    else f"GEN-STOCK-{stocked_variant:03d}")
                        self.assertIn(expected, sources)
                        self.assertEqual((bundle["run"]["as_of_at"].hour,
                                          bundle["run"]["as_of_at"].minute),
                                         (12, 10 * stocked_variant))
                        stocked_variant += 1
                    if slot["archetype_id"] == "BUILD-READY":
                        sources = {source for finding in decision["specialists"]["availability"]
                                   for source in finding["source_ids"]}
                        expected = ("PILOT-STOCK-002" if build_variant == 0
                                    else f"GEN-BUILD-STOCK-{build_variant:03d}")
                        self.assertIn(expected, sources)
                        self.assertEqual((bundle["run"]["as_of_at"].hour,
                                          bundle["run"]["as_of_at"].minute),
                                         (12, 10 * build_variant))
                        build_variant += 1
                    if archetype == "SUPPLY-CONFIRMED":
                        expected = ("PILOT-INBOUND-001" if supply_variant == 0
                                    else f"GEN-INBOUND-{supply_variant:03d}")
                        self.assertIn(expected, sources_for_case)
                        self.assertEqual(bundle["lines"][0]["quantity"],
                                         1 if supply_variant == 0 else supply_variant + 2)
                        self.assertEqual((bundle["run"]["as_of_at"].hour,
                                          bundle["run"]["as_of_at"].minute),
                                         (12, 0) if supply_variant == 0
                                         else (14, 10 * supply_variant))
                        if supply_variant:
                            receipt = next(row for row in bundle["inbound_supply"]
                                           if row["supply_id"] == expected)
                            self.assertLessEqual(receipt["confirmed_at"],
                                                 bundle["run"]["as_of_at"])
                            self.assertFalse(any(
                                row["supply_id"] == f"GEN-INBOUND-{later:03d}"
                                for row in bundle["inbound_supply"]
                                for later in range(supply_variant + 1, 6)))
                        supply_variant += 1
                    if archetype == "DIGITAL-PROVED":
                        expected = ("PILOT-POOL-001" if digital_variant == 0
                                    else f"GEN-DIGITAL-POOL-{digital_variant:03d}")
                        self.assertIn(expected, sources_for_case)
                        self.assertEqual((bundle["run"]["as_of_at"].hour,
                                          bundle["run"]["as_of_at"].minute),
                                         (12, 0) if digital_variant == 0
                                         else (14, 10 * digital_variant))
                        selected = bundle["digital_capacity"]
                        self.assertEqual([p["digital_capacity_id"] for p in selected], [expected])
                        self.assertTrue(bundle["facts"]["lines"][0]["digital"]["pools"][0]["full_term_verified"])
                        self.assertEqual(bundle["facts"]["lines"][0]["digital"]["status"],
                                         "confirmed_by_date")
                        if digital_variant:
                            self.assertEqual(selected[0]["capacity_total"], 10 + digital_variant)
                            self.assertLessEqual(selected[0]["snapshot_at"],
                                                 bundle["run"]["as_of_at"])
                        digital_variant += 1
                    if archetype in ("DIGITAL-NO-PROOF", "DIGITAL-EXPIRED"):
                        self.assertFalse(any(
                            pool["full_term_verified"]
                            for fact in bundle["facts"]["lines"]
                            for pool in fact.get("digital", {}).get("pools", [])))
                    if index in (99, 100):
                        finding = next(f for f in bundle["facts"]["compatibility"]
                                       if f["compatibility_rule_id"] == "V2-REQUIRES-ADDON")
                        self.assertEqual(finding["status"], "pass" if index == 99 else "fail")
                        self.assertEqual(any(b.get("rule_id") == "V2-REQUIRES-ADDON"
                                             for b in decision["blocks"]), index == 100)
                self.assertEqual(supply_variant, 6)
                self.assertEqual(digital_variant, 5)
                self.assertTrue({f"GEN-INBOUND-{n:03d}" for n in range(1, 6)}
                                <= set(availability_sources))
                self.assertTrue({f"GEN-DIGITAL-POOL-{n:03d}" for n in range(1, 5)}
                                <= set(availability_sources))
                self.assertEqual(len(case_observations), 100)
                self.assertEqual(len({case["case_id"] for case in case_observations}), 100)
                self.assertEqual({source for case in case_observations
                                  for source in case["availability_finding_source_ids"]},
                                 set(availability_sources))
                source_case_reuse = Counter(
                    source for case in case_observations
                    for source in case["availability_finding_source_ids"])
                service_facts = [service for case in case_observations
                                 for service in case["service_facts"]]
                source_gap_cases = [case["case_id"] for case in case_observations
                                    if not case["availability_finding_source_ids"]]
                reused_source_case_count = sum(
                    any(source_case_reuse[source] > 1
                        for source in case["availability_finding_source_ids"])
                    for case in case_observations)
                case_review = {
                    "status": "development_observations_for_independent_review",
                    "independent_answers_reviewed": 0,
                    "distribution_review": {
                        "customer_count": len(customers),
                        "line_mode_counts": dict(sorted(modes.items())),
                        "observed_decision_status_counts": dict(sorted(statuses.items())),
                        "distinct_availability_source_ids": len(source_case_reuse),
                        "source_ids_used_in_one_case": sum(n == 1 for n in source_case_reuse.values()),
                        "cases_with_reused_attributed_source": reused_source_case_count,
                        "source_template_count": 20,
                    },
                    "availability_source_id_case_reuse": dict(sorted(source_case_reuse.items())),
                    "cases_without_attributed_availability_source_ids": source_gap_cases,
                    "service_review_summary": {
                        "service_line_count": len(service_facts),
                        "coverage_counts": dict(sorted(Counter(
                            service["coverage"] for service in service_facts).items())),
                        "slot_committed_count": sum(service["slot_committed"]
                                                    for service in service_facts),
                    },
                    "cases": case_observations,
                    "limitations": [
                        "observed_decisions_are_not_expected_answers",
                        "reader_visible_raw_rows_are_not_necessarily_binding_or_used_in_findings",
                        "source_reuse_does_not_prove_independence",
                    ],
                }
                self.assertEqual(case_review["service_review_summary"]["service_line_count"], 11)
                self.assertEqual(case_review["service_review_summary"]["slot_committed_count"], 0)
                diagnostic = {
                    "status": "development_diagnostic_not_answer_key",
                    "deal_count": sum(statuses.values()),
                    "decision_status_counts": dict(sorted(statuses.items())),
                    "line_mode_counts": dict(sorted(modes.items())),
                    "fulfillment_status_counts": dict(sorted(fulfillment.items())),
                    "distinct_customer_count": len(customers),
                    "distinct_availability_source_ids": len(availability_sources),
                    "top_availability_source_reuse": [
                        {"source_id": source, "finding_attributions": count}
                        for source, count in sorted(availability_sources.items(),
                                                    key=lambda item: (-item[1], item[0]))[:10]],
                    "source_template_count": 20,
                    "archetype_distribution": {
                        archetype: {
                            "deals": sum(counts.values()),
                            "decision_status_counts": dict(sorted(counts.items())),
                            "fulfillment_status_counts": dict(sorted(by_archetype_fulfillment[archetype].items())),
                            "distinct_customer_count": len(by_archetype_customers[archetype]),
                            "distinct_availability_source_ids": len(by_archetype_sources[archetype]),
                        }
                        for archetype, counts in sorted(by_archetype_status.items())},
                    "archetypes_with_one_observed_decision_status": sorted(
                        archetype for archetype, counts in by_archetype_status.items()
                        if len(counts) == 1),
                    "limitations": ["source_states_reused_across_submissions",
                                    "no_independent_answers_or_evaluation_cases",
                                    "observed_statuses_are_not_expected_answers"],
                }
                self.assertEqual(diagnostic["deal_count"], 100)
                self.assertEqual(sum(modes.values()), 101)
                self.assertGreaterEqual(len(statuses), 2)
                self.assertGreaterEqual(len(customers), 50)
                self.assertEqual(stocked_variant, 6)
                self.assertEqual(build_variant, 6)
                self.assertEqual(set(by_archetype_status),
                                 {case["id"] for case in matrix["archetypes"]} |
                                 {"DEPENDENCY-PASS", "DEPENDENCY-CONFLICT"})
                self.assertEqual(sum(sum(counts.values()) for counts in by_archetype_status.values()), 100)
                self.assertEqual(sum(sum(counts.values()) for counts in by_archetype_fulfillment.values()),
                                 sum(fulfillment.values()))
                self.assertTrue({f"GEN-STOCK-{i:03d}" for i in range(1, 6)}
                                <= set(availability_sources))
                self.assertTrue({f"GEN-BUILD-STOCK-{i:03d}" for i in range(1, 6)}
                                <= set(availability_sources))
                if os.environ.get("PHASE1C_CASE_REVIEW"):
                    Path(os.environ["PHASE1C_CASE_REVIEW"]).write_text(
                        json.dumps(case_review, indent=2, sort_keys=True) + "\n")
                    print("Case review summary: " + json.dumps({
                        "cases": len(case_observations),
                        "cases_without_attributed_availability_ids": len(source_gap_cases),
                        "service": case_review["service_review_summary"],
                        "distribution": case_review["distribution_review"],
                        "most_reused_source_ids": sorted(
                            source_case_reuse.items(), key=lambda item: (-item[1], item[0]))[:5],
                    }, sort_keys=True))
                if os.environ.get("PHASE1C_BATCH_DIAGNOSTIC"):
                    Path(os.environ["PHASE1C_BATCH_DIAGNOSTIC"]).write_text(
                        json.dumps(diagnostic, indent=2, sort_keys=True) + "\n")
            finally:
                conn.rollback()


if __name__ == "__main__":
    unittest.main()

