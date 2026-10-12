"""Check conflict source rows against the PostgreSQL reader and compiled policy."""

import json
import os
from pathlib import Path
import re
import unittest

import yaml

from render_phase1c_conflict_pilot import build, CASE_MAP
from validate_phase1c_generated_rows import audit_dependency_coverage, load_rows

try:
    import psycopg
except ImportError:
    psycopg = None

if psycopg is not None:
    from phase1c_reader import read_run, load_provider_evidence
    from phase1c_deal_decision import assemble_deal_decision

HERE = Path(__file__).resolve().parent


class ConflictRenderTests(unittest.TestCase):
    def test_deterministic_and_no_oracle_in_submissions(self):
        args = (json.loads((HERE / "phase1c_portfolio_draft.json").read_text()),
                json.loads((HERE / "phase1c_build_cost_draft.json").read_text()),
                yaml.safe_load((HERE / "calibration_config.yaml").read_text()),
                yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text()))
        sql = build(*args)
        self.assertEqual(sql, (HERE / "phase1c_conflict_pilot.sql").read_text())
        self.assertEqual(sql.count("INSERT INTO deals "), len(CASE_MAP))
        self.assertEqual(sql.count("INSERT INTO deal_runs "), len(CASE_MAP))
        self.assertNotIn("target_bucket", sql)
        locations = set(re.findall(r"'(WH-EU-[A-Z]+)'", sql))
        self.assertTrue(locations)
        self.assertLessEqual(locations, set(args[3]["controlled_vocabularies"]["location_codes"]))
        self.assertIn("'WH-EU-WEST', 'Europe/Amsterdam'", sql)


@unittest.skipUnless(psycopg is not None and os.environ.get("DATABASE_URL"),
                     "PostgreSQL integration requires psycopg and DATABASE_URL")
class ConflictReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg.connect(os.environ["DATABASE_URL"])
        cls.conn.execute("SET search_path TO deal_desk, public")
        try:
            for name in ("phase1c_buildable_master.sql", "phase1c_sellable_catalogue.sql",
                         "phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql"):
                content = (HERE / name).read_text()
                for statement in re.findall(r"^(?:INSERT INTO|UPDATE deals SET) .*?;", content,
                                            re.M | re.S):
                    cls.conn.execute(statement)
        except Exception:
            cls.conn.rollback()
            cls.conn.close()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.conn.rollback()
        cls.conn.close()

    def read(self, case):
        index = CASE_MAP[case]
        return read_run(self.conn, f"00000000-0000-4000-8000-{260000 + index:012d}",
                        digital_evidence_resolver=load_provider_evidence(
                            HERE / "phase1c_conflict_provider_manifest.json"),
                        cost_parameters={"workforce_cost_eur_per_hour": 30,
                                         "overhead_fraction": "0.1"},
                        commercial_rule_mode="compiled")

    def test_operational_conflicts_remain_bounded(self):
        expected = {
            "STOCK-ALLOCATED": "infeasible", "STOCK-STALE": "unknown",
            "SUPPLY-OFFER-ONLY": "conditional", "SUPPLY-CANCELLED": "infeasible",
            "DIGITAL-NO-PROOF": "binding_candidate", "DIGITAL-EXPIRED": "binding_candidate",
            "SERVICE-OUTSIDE": "infeasible",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                bundle = self.read(case)
                fact = bundle["facts"]["lines"][0]
                actual = (fact["digital"]["status"] if case.startswith("DIGITAL") else
                          fact["service"]["status"] if case.startswith("SERVICE") else
                          fact["fulfillment_status"])
                self.assertEqual(actual, status)
        self.assertEqual(assemble_deal_decision(self.read("SUPPLY-OFFER-ONLY"))["status"],
                         "needs_evidence")
        for case in ("DIGITAL-NO-PROOF", "DIGITAL-EXPIRED"):
            fact = self.read(case)["facts"]["lines"][0]["digital"]
            self.assertFalse(fact["pools"][0]["full_term_verified"])
            self.assertEqual(assemble_deal_decision(self.read(case))["status"], "needs_evidence")

    def test_commercial_conflicts_keep_source_attribution(self):
        for case, expected_area in (("CREDIT-LIMIT", "credit"),
                                    ("PRICE-FLOOR", "pricing"),
                                    ("POLICY-CLAUSE", "policy")):
            with self.subTest(case=case):
                bundle = self.read(case)
                self.assertEqual(bundle["facts"]["lines"][0]["fulfillment_status"],
                                 "confirmed_by_date")
                decision = assemble_deal_decision(bundle)
                self.assertTrue(any(hit["area"] == expected_area
                                    for hit in decision["commercial_rule_hits"]))
                self.assertNotEqual(decision["status"], "approved")

    def test_build_conflicts_do_not_infer_unrepresented_capacity(self):
        substitute = self.read("BUILD-SUBSTITUTE")
        line = substitute["facts"]["lines"][0]
        self.assertEqual(line["fulfillment_status"], "feasible_uncommitted")
        plan = substitute["facts"]["supply"]["assembly_by_bom"]["BOM-001"]
        self.assertEqual(plan["substitution_groups"][0]["selected_component_product_id"],
                         "COMP-NETWORK_AND_POWER-002")
        self.assertIn("CONFLICT-INBOUND-16", plan["candidate_evidence_ids"])
        for case, reason in (("BUILD-CAPACITY-STALE", "production_capacity_evidence_missing_or_stale"),
                             ("BUILD-HORIZON", "confirmed_component_supply_after_capacity_horizon")):
            with self.subTest(case=case):
                bundle = self.read(case)
                fact = bundle["facts"]["lines"][0]
                self.assertEqual(fact["fulfillment_status"], "unknown")
                self.assertEqual(fact["production_unknown_reason"], reason)
                self.assertEqual(assemble_deal_decision(bundle)["status"], "needs_evidence")

    def test_isolated_required_product_pass_and_conflict_reach_deal_gate(self):
        """Exercise a real reader rule without changing shared pilot outcomes."""
        source = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-004"
        target = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005"
        self.conn.execute("SAVEPOINT dependency_trial")
        try:
            self.conn.execute("""INSERT INTO deal_desk.compatibility_rules
                (compatibility_rule_id,catalog_version,rule_name,rule_type,scope_type,
                 source_product_id,target_product_id,condition_json,severity,message,priority)
                VALUES ('TRIAL-REQUIRES-ADDON','CATALOGUE_2026_V1',
                'Synthetic product dependency','requires_product','whole_deal',%s,%s,
                '{"operator":"present"}','blocker','Add-on required',1)""", (source, target))
            for index, include_target in ((21, False), (22, True)):
                deal_id = f"DEP-TRIAL-{index}"
                run_id = f"00000000-0000-4000-8000-{270000 + index:012d}"
                self.conn.execute("""INSERT INTO deal_desk.deals
                    (deal_id,customer_id,salesperson_id,deal_name,submitted_at,currency_code,
                     catalog_version,policy_set_code,requested_delivery_date,
                     destination_country_code,destination_region,shipping_service_code,
                     terms_json,deal_status,dataset_type)
                    VALUES (%s,'CONFLICT-CUST-06','SALES-001','Dependency trial',
                    '2026-09-01 10:00+00','EUR','CATALOGUE_2026_V1','BASELINE_2026',
                    '2026-09-10','DE','DE-NW','standard',
                    '{"payment_terms_days":30,"contract_clause_codes":["standard"],"allow_partial_delivery":false}',
                    'Draft','generated_test')""", (deal_id,))
                for number, product in enumerate((source, target) if include_target else (source,), 1):
                    self.conn.execute("""INSERT INTO deal_desk.deal_lines
                        (deal_line_id,deal_id,line_number,product_id,quantity,
                         quoted_unit_price,configuration_json)
                        SELECT %s,%s,%s,product_id,1,list_price,'{}'
                        FROM deal_desk.products WHERE product_id=%s""",
                        (f"DEP-LINE-{index}-{number}", deal_id, number, product))
                self.conn.execute("UPDATE deal_desk.deals SET deal_status='Submitted' WHERE deal_id=%s",
                                  (deal_id,))
                self.conn.execute("""INSERT INTO deal_desk.deal_runs
                    (run_id,deal_id,original_policy_set_code,applied_policy_set_code,
                     catalog_version_used,as_of_at,data_snapshot_ref,input_snapshot_json,
                     config_hash,run_status,started_at)
                    VALUES (%s,%s,'BASELINE_2026','BASELINE_2026','CATALOGUE_2026_V1',
                    '2026-09-01 12:00+00','DEP-TRIAL-SNAPSHOT','{}',
                    'dependency-trial','queued','2026-09-01 12:00+00')""", (run_id, deal_id))
                bundle = read_run(self.conn, run_id, commercial_rule_mode="compiled")
                finding = next(f for f in bundle["facts"]["compatibility"]
                               if f["compatibility_rule_id"] == "TRIAL-REQUIRES-ADDON")
                decision = assemble_deal_decision(bundle)
                self.assertEqual(finding["status"], "pass" if include_target else "fail")
                matching_blocks = [b for b in decision["blocks"]
                                   if b.get("rule_id") == "TRIAL-REQUIRES-ADDON"]
                self.assertEqual(bool(matching_blocks), not include_target)
                self.assertEqual(decision["status"] == "blocked", not include_target)
            coverage = audit_dependency_coverage(load_rows(self.conn))
            self.assertGreaterEqual(coverage["finding_counts"]["pass"], 1)
            self.assertGreaterEqual(coverage["finding_counts"]["fail"], 2)
            self.assertFalse(coverage["coverage_gap"])
        finally:
            self.conn.execute("ROLLBACK TO SAVEPOINT dependency_trial")
            self.conn.execute("RELEASE SAVEPOINT dependency_trial")


if __name__ == "__main__":
    unittest.main()
