"""A read-only candidate assessment over actual PostgreSQL reference sources."""

from copy import deepcopy
from datetime import date
import json
import os
from pathlib import Path
import tempfile
import unittest
from uuid import UUID

from phase1c_candidate import Candidate, DeliverySlice, FieldChange, verify_run_correlation, compare_for_human
from phase1c_candidate_trace import (build_trace_record, export_trace_once,
                                     verify_exported_trace, replay_exported_trace)
from phase1c_candidate_batch import compare_candidate_set
from phase1c_partial_discovery import discover_partial_delivery, discover_and_recheck
from phase1c_evaluation_input import (prepare_review_input, verify_review_input,
    prepare_heldout_review_input)
from score_phase1c_reader_trial import score

try:
    import psycopg
except ImportError:
    psycopg = None


@unittest.skipUnless(psycopg is not None and os.environ.get("DATABASE_URL"),
                     "PostgreSQL integration requires DATABASE_URL")
class CandidateReaderTests(unittest.TestCase):
    def setUp(self):
        from test_phase1c_reader import load_fixture_rows
        self.conn = psycopg.connect(os.environ["DATABASE_URL"])
        # The reference fixture is loaded by an earlier CI step. Allow this
        # test to run alone in a fresh disposable database as well.
        exists = self.conn.execute(
            "SELECT EXISTS(SELECT 1 FROM deal_desk.deals WHERE deal_id=%s)",
            ("D-stock_then_confirmed_receipt",)).fetchone()[0]
        self.conn.rollback()
        if not exists:
            load_fixture_rows()
        self.conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        self.conn.execute("SET LOCAL search_path TO deal_desk, public")
        self.conn.execute("""INSERT INTO deal_desk.deals
            (deal_id,customer_id,salesperson_id,deal_name,submitted_at,currency_code,
             catalog_version,policy_set_code,requested_delivery_date,destination_country_code,
             destination_region,shipping_service_code,terms_json,deal_status,dataset_type)
            VALUES ('D-candidate-shortage','C-stock_then_confirmed_receipt','SALES-FIXTURE',
            'Candidate shortage trial','2026-09-01 09:00+00','EUR','CATALOGUE_2026_V1',
            'BASELINE_2026','2026-09-04','DE','Berlin','standard',
            '{"allow_partial_delivery":true,"contract_clause_codes":["standard"],"payment_terms_days":30}',
            'Draft','generated_test')""")
        self.conn.execute("""INSERT INTO deal_desk.deal_lines
            (deal_line_id,deal_id,line_number,product_id,quantity,quoted_unit_price,configuration_json)
            VALUES ('L-candidate-shortage','D-candidate-shortage',1,
            'stock_then_confirmed_receipt-P',10,900,'{}')""")
        self.conn.execute("UPDATE deal_desk.deals SET deal_status='Submitted' WHERE deal_id='D-candidate-shortage'")
        self.run_id = UUID("00000000-0000-4000-8000-000000019991")
        self.conn.execute("""INSERT INTO deal_desk.deal_runs
            (run_id,deal_id,original_policy_set_code,applied_policy_set_code,catalog_version_used,
             as_of_at,data_snapshot_ref,input_snapshot_json,config_hash,run_status,started_at)
            VALUES (%s,'D-candidate-shortage','BASELINE_2026','BASELINE_2026',
            'CATALOGUE_2026_V1','2026-09-01 12:00+00','FIXTURE-stock_then_confirmed_receipt',
            '{"deal_id":"D-candidate-shortage"}','FIXTURE-CONFIG','queued','2026-09-01 12:00+00')""",
            (self.run_id,))

    def tearDown(self):
        self.conn.rollback()
        self.conn.close()

    def candidate(self, *, second_date=date(2026, 9, 8), second_evidence=None,
                  candidate_id="C-READ-1"):
        from datetime import datetime, timezone
        stock = "INV-stock_then_confirmed_receipt-P"
        receipt = "IN-stock_then_confirmed_receipt"
        return Candidate(
            candidate_id=candidate_id, parent_deal_id="D-candidate-shortage",
            parent_run_id=self.run_id, proposal_kind="partial_delivery",
            changes=(FieldChange(None, "proposed_delivery_slices",
                                 (("L-candidate-shortage", 10, date(2026, 9, 4)),),
                                 (("L-candidate-shortage", 8, date(2026, 9, 4)),
                                  ("L-candidate-shortage", 2, second_date))),),
            customer_constraints=("10 units", "original_requested_delivery_date", "partial allowed"),
            unmet_constraints=("original_requested_delivery_date",),
            delivery_slices=(
                DeliverySlice("L-candidate-shortage", 8, date(2026, 9, 4), (stock,), "confirmed"),
                DeliverySlice("L-candidate-shortage", 2, second_date,
                              (second_evidence or receipt,), "confirmed")),
            evidence_ids=(stock, second_evidence or receipt),
            as_of_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            catalog_version="CATALOGUE_2026_V1", policy_set_code="BASELINE_2026",
            data_snapshot_ref="FIXTURE-stock_then_confirmed_receipt",
            assumptions=("Customer acceptance of later two units is pending",),
            tradeoff="Eight units by request; two later with dated binding supply, pending customer acceptance.")

    def test_actual_reader_sources_recheck_and_original_immutable(self):
        from phase1c_reader import read_run
        from phase1c_deal_decision import assemble_deal_decision
        before = self.conn.execute(
            "SELECT requested_delivery_date,terms_json FROM deal_desk.deals WHERE deal_id='D-candidate-shortage'"
        ).fetchone()
        original = read_run(self.conn, self.run_id, commercial_rule_mode="compiled")
        candidate = self.candidate()
        checked = read_run(self.conn, self.run_id, commercial_rule_mode="compiled", candidate=candidate)
        verify_run_correlation(candidate, original, checked)
        baseline = assemble_deal_decision(original)
        result = assemble_deal_decision(checked)
        self.assertEqual(baseline["status"], "needs_revision")
        self.assertEqual(result["status"], "needs_revision")
        self.assertEqual(result["candidate_trace"]["assessment"]["status"], "supply_supported_unreserved")
        self.assertEqual(result["candidate_trace"]["rerun_specialists"],
                         ["Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval"])
        self.assertEqual(result["specialists"]["availability"][0]["original_requested_date"], date(2026, 9, 4))
        self.assertEqual([x["cumulative_quantity"] for x in
                          result["specialists"]["availability"][0]["candidate_slices"]], [8, 10])
        self.assertEqual(result["required_approvals"], [])
        self.assertEqual(result["customer_constraints_unmet"], ["original_requested_delivery_date"])
        comparison = compare_for_human(candidate, original, checked)
        self.assertEqual(comparison["original_requested_date"], date(2026, 9, 4))
        self.assertEqual(comparison["proposed"]["availability"][0]["candidate_slices"][-1]["arrival_date"],
                         date(2026, 9, 8))
        self.assertIn("customer acceptance", comparison["human_action"])
        self.assertTrue(comparison["verified_supply_option"])
        self.assertEqual(self.conn.execute(
            "SELECT requested_delivery_date,terms_json FROM deal_desk.deals WHERE deal_id='D-candidate-shortage'"
        ).fetchone(), before)
        self.assertEqual(self.conn.execute(
            "SELECT count(*) FROM deal_desk.agent_execution_log WHERE run_id=%s", (self.run_id,)
        ).fetchone()[0], 0)
        tampered = deepcopy(checked)
        tampered["inventory"][0]["quantity_on_hand"] = 999
        with self.assertRaisesRegex(ValueError, "Reader-used"):
            verify_run_correlation(candidate, original, tampered)

        with tempfile.TemporaryDirectory() as temp:
            record = build_trace_record(candidate, original, checked)
            self.assertEqual(record["payload"]["actual_source_ids"],
                             ["IN-stock_then_confirmed_receipt", "INV-stock_then_confirmed_receipt-P"])
            self.assertEqual(record["payload"]["original_requested_date"], "2026-09-04")
            path = export_trace_once(temp, record)
            self.assertEqual(verify_exported_trace(path, candidate, original, checked), record["sha256"])
            self.assertEqual(replay_exported_trace(
                self.conn, path, candidate, reader_kwargs={"commercial_rule_mode": "compiled"}),
                record["sha256"])
            self.conn.execute("UPDATE deal_desk.inventory SET quantity_on_hand=quantity_on_hand+1 "
                              "WHERE inventory_id='INV-stock_then_confirmed_receipt-P'")
            with self.assertRaisesRegex(ValueError, "differs from replayed"):
                replay_exported_trace(self.conn, path, candidate,
                                      reader_kwargs={"commercial_rule_mode": "compiled"})
            self.conn.execute("UPDATE deal_desk.inventory SET quantity_on_hand=quantity_on_hand-1 "
                              "WHERE inventory_id='INV-stock_then_confirmed_receipt-P'")
            with self.assertRaises(FileExistsError):
                export_trace_once(temp, record)
            altered = json.loads(Path(path).read_text())
            altered["payload"]["candidate_decision"]["status"] = "approval_required"
            Path(path).write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "content changed"):
                verify_exported_trace(path, candidate, original, checked)
            # Recomputing a self-hash does not prove provenance: fresh replay
            # must still reject a forged decision.
            from hashlib import sha256
            from phase1c_candidate_trace import _canonical
            altered["sha256"] = sha256(_canonical(altered["payload"]).encode()).hexdigest()
            Path(path).write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "differs from replayed"):
                verify_exported_trace(path, candidate, original, checked)

    def test_discovery_uses_reader_facts_and_full_recheck(self):
        from phase1c_reader import read_run
        original = read_run(self.conn, self.run_id, commercial_rule_mode="compiled")
        candidate, reason = discover_partial_delivery(original)
        self.assertIn("full recheck", reason)
        self.assertEqual(candidate.changes[0].before,
                         (("L-candidate-shortage", 10, date(2026, 9, 4)),))
        self.assertEqual([(s.quantity, s.arrival_date, s.evidence_ids)
                          for s in candidate.delivery_slices], [
            (8, date(2026, 9, 4), ("INV-stock_then_confirmed_receipt-P",)),
            (2, date(2026, 9, 8), ("IN-stock_then_confirmed_receipt",))])
        result = discover_and_recheck(self.conn, self.run_id,
                                      reader_kwargs={"commercial_rule_mode": "compiled"})
        self.assertEqual(result["status"], "review_option")
        self.assertIsNone(result["selected_candidate_id"])
        self.assertEqual(result["comparison"]["validated_supply_option_ids"],
                         [candidate.candidate_id])
        record = result["comparison"]["candidate_records"][0]
        self.assertEqual(record["payload"]["human_comparison"]["original_requested_date"],
                         "2026-09-04")
        self.assertEqual(record["payload"]["actual_source_ids"],
                         ["IN-stock_then_confirmed_receipt", "INV-stock_then_confirmed_receipt-P"])
        self.conn.execute("UPDATE deal_desk.inventory SET quantity_on_hand=quantity_on_hand+1 "
                          "WHERE inventory_id='INV-stock_then_confirmed_receipt-P'")
        changed = discover_and_recheck(self.conn, self.run_id,
                                       reader_kwargs={"commercial_rule_mode": "compiled"})
        self.assertEqual(changed["status"], "review_option")
        self.assertEqual([s.quantity for s in changed["candidate"].delivery_slices], [9, 1])
        self.assertNotEqual(changed["candidate"].candidate_id, candidate.candidate_id)

    def test_discovery_fails_closed_when_permission_or_supply_missing(self):
        from phase1c_reader import read_run
        original = read_run(self.conn, self.run_id, commercial_rule_mode="compiled")
        forbidden = deepcopy(original)
        forbidden["deal"]["terms_json"]["allow_partial_delivery"] = False
        self.assertIsNone(discover_partial_delivery(forbidden)[0])
        no_receipt = deepcopy(original)
        no_receipt["facts"]["lines"][0]["shipping_options"] = [
            o for o in no_receipt["facts"]["lines"][0]["shipping_options"]
            if not o["supply_ids"]]
        self.assertIsNone(discover_partial_delivery(no_receipt)[0])
        # A real reader re-read must also refuse a formerly supported proposal
        # when the confirmed receipt is withdrawn before the snapshot cutoff.
        self.conn.execute("UPDATE deal_desk.inbound_supply SET status='Cancelled' "
                          "WHERE supply_id='IN-stock_then_confirmed_receipt'")
        result = discover_and_recheck(self.conn, self.run_id,
                                      reader_kwargs={"commercial_rule_mode": "compiled"})
        self.assertEqual(result["status"], "no_proposal")
        self.assertIn("binding full supply", result["reason"])

    def test_distinct_input_only_evaluation_preparation(self):
        from phase1c_reader import read_run
        from phase1c_candidate import reader_input_digest
        self.conn.execute("""INSERT INTO deal_desk.products
            (product_id,product_code,catalog_version,product_name,category,product_type,
             attributes_json,list_price,standard_cost,billing_model,unit_of_measure,
             is_active,is_sellable,fulfillment_mode,stock_uom)
            SELECT 'eval_prep_stock-P','EVAL-PREP-STOCK',catalog_version,
                   'Independent review preparation',category,product_type,attributes_json,
                   list_price,standard_cost,billing_model,unit_of_measure,is_active,
                   is_sellable,fulfillment_mode,stock_uom
            FROM deal_desk.products WHERE product_id='stock_then_confirmed_receipt-P'""")
        self.conn.execute("""INSERT INTO deal_desk.inventory
            (inventory_id,product_id,location_id,quantity_on_hand,quantity_allocated,snapshot_at)
            SELECT 'INV-EVAL-PREP-1','eval_prep_stock-P',location_id,5,0,snapshot_at
            FROM deal_desk.inventory WHERE inventory_id='INV-stock_then_confirmed_receipt-P'""")
        self.conn.execute("""INSERT INTO deal_desk.inbound_supply
            (supply_id,purchase_order_id,product_id,location_id,quantity,quantity_allocated,
             expected_date,confirmed_at,status,reference_number,evidence_ref,valid_until)
            SELECT 'IN-EVAL-PREP-1',purchase_order_id,'eval_prep_stock-P',location_id,
                   7,0,expected_date,confirmed_at,status,'REF-EVAL-PREP-1',
                   evidence_ref,valid_until FROM deal_desk.inbound_supply
            WHERE supply_id='IN-stock_then_confirmed_receipt'""")
        self.conn.execute("""INSERT INTO deal_desk.deals
            (deal_id,customer_id,salesperson_id,deal_name,submitted_at,currency_code,
             catalog_version,policy_set_code,requested_delivery_date,destination_country_code,
             destination_region,shipping_service_code,terms_json,deal_status,dataset_type)
            VALUES ('D-eval-prep-1','C-stock_then_confirmed_receipt','SALES-FIXTURE',
            'Separate input review case','2026-09-01 09:00+00','EUR','CATALOGUE_2026_V1',
            'BASELINE_2026','2026-09-03','DE','Berlin','standard',
            '{"allow_partial_delivery":true,"contract_clause_codes":["standard"],"payment_terms_days":30}',
            'Draft','generated_test')""")
        self.conn.execute("""INSERT INTO deal_desk.deal_lines
            (deal_line_id,deal_id,line_number,product_id,quantity,quoted_unit_price,configuration_json)
            VALUES ('L-eval-prep-1','D-eval-prep-1',1,'eval_prep_stock-P',11,900,'{}')""")
        self.conn.execute("UPDATE deal_desk.deals SET deal_status='Submitted' WHERE deal_id='D-eval-prep-1'")
        review_run = UUID("00000000-0000-4000-8000-000000019992")
        self.conn.execute("""INSERT INTO deal_desk.deal_runs
            (run_id,deal_id,original_policy_set_code,applied_policy_set_code,catalog_version_used,
             as_of_at,data_snapshot_ref,input_snapshot_json,config_hash,run_status,started_at)
            VALUES (%s,'D-eval-prep-1','BASELINE_2026','BASELINE_2026',
            'CATALOGUE_2026_V1','2026-09-01 12:00+00','EVAL-PREP-SNAPSHOT-1',
            '{"deal_id":"D-eval-prep-1"}','EVAL-PREP-CONFIG','queued','2026-09-01 12:00+00')""",
            (review_run,))
        bundle = read_run(self.conn, review_run, commercial_rule_mode="compiled")
        packet = prepare_review_input(bundle, case_id="EVAL-PREP-1",
            excluded_deal_ids=("D-candidate-shortage", "D-stock_then_confirmed_receipt"),
            excluded_source_ids=("INV-stock_then_confirmed_receipt-P",
                                 "IN-stock_then_confirmed_receipt"))
        pinned_registry = json.loads(
            (Path(__file__).resolve().parent /
             "phase1c_development_source_exclusions.json").read_text())
        heldout_preparation = prepare_heldout_review_input(
            bundle, case_id="EVAL-PREP-1", development_manifest=pinned_registry)
        self.assertEqual(heldout_preparation, packet)
        self.assertTrue(verify_review_input(packet, expected_case_id="EVAL-PREP-1",
                                            expected_source_digest=reader_input_digest(bundle)))
        self.assertNotIn("facts", packet["payload"])
        self.assertNotIn("candidate_trace", packet["payload"])
        self.assertEqual(packet["payload"]["source_rows"]["deal"]["requested_delivery_date"],
                         "2026-09-03")
        forged = deepcopy(packet)
        forged["payload"]["source_rows"]["inventory"][0]["quantity_on_hand"] = "500"
        with self.assertRaisesRegex(ValueError, "seal differs"):
            verify_review_input(forged, expected_case_id="EVAL-PREP-1",
                                expected_source_digest=reader_input_digest(bundle))
        with self.assertRaisesRegex(ValueError, "reuses development"):
            prepare_review_input(bundle, case_id="EVAL-PREP-1",
                                 excluded_source_ids=("INV-EVAL-PREP-1",))

    def test_unavailable_date_or_false_source_cannot_pass(self):
        from phase1c_reader import read_run
        earlier = self.candidate(second_date=date(2026, 9, 4))
        with self.assertRaisesRegex(ValueError, "later slice"):
            read_run(self.conn, self.run_id, commercial_rule_mode="compiled", candidate=earlier)
        fake_source = self.candidate(second_evidence="NOT-A-SOURCE")
        with self.assertRaisesRegex(ValueError, "selected binding evidence"):
            read_run(self.conn, self.run_id, commercial_rule_mode="compiled", candidate=fake_source)
        unavailable = self.candidate(second_date=date(2026, 9, 5))
        checked = read_run(self.conn, self.run_id, commercial_rule_mode="compiled", candidate=unavailable)
        self.assertEqual(checked["candidate_trace"]["assessment"]["status"], "unknown_or_unavailable")
        original = read_run(self.conn, self.run_id, commercial_rule_mode="compiled")
        comparison = compare_for_human(unavailable, original, checked)
        self.assertFalse(comparison["verified_supply_option"])
        self.assertIn("no validated delivery option", comparison["human_action"])
        self.assertEqual(compare_for_human(unavailable, original, checked)["proposed"]["status"],
                         "needs_revision")
        record = build_trace_record(unavailable, original, checked)
        self.assertFalse(record["payload"]["human_comparison"]["verified_supply_option"])
        self.assertEqual(record["payload"]["actual_source_ids"], [])

    def test_two_options_share_sources_but_keep_separate_traces(self):
        supported = self.candidate()
        unsupported = self.candidate(second_date=date(2026, 9, 5), candidate_id="C-READ-2")
        package = compare_candidate_set(self.conn, self.run_id, [supported, unsupported],
                                        reader_kwargs={"commercial_rule_mode": "compiled"})
        oracle = json.loads((Path(__file__).resolve().parent.parent / "evaluation" /
                             "reader_trial_oracle_draft.json").read_text())
        diagnostic = score(package, oracle)
        self.assertTrue(diagnostic["all_checks_match_draft"])
        self.assertEqual(diagnostic["original_rule_only_status"], "needs_revision")
        self.assertEqual(diagnostic["independently_reviewed_cases"], 0)
        self.assertEqual((diagnostic["false_supported_options"],
                          diagnostic["missed_supported_options"]), (0, 0))
        forged = deepcopy(package)
        forged["candidate_records"][0]["payload"]["human_comparison"]["verified_supply_option"] = False
        from hashlib import sha256
        from phase1c_candidate_trace import _canonical
        forged["candidate_records"][0]["sha256"] = sha256(
            _canonical(forged["candidate_records"][0]["payload"]).encode()).hexdigest()
        self.assertTrue(score(forged, oracle)["candidate_results"][0]["missed_supported_option"])
        forged = deepcopy(package)
        forged["candidate_records"][0]["payload"]["actual_source_ids"] = []
        with self.assertRaisesRegex(ValueError, "content digest"):
            score(forged, oracle)
        forged["candidate_records"][0]["sha256"] = sha256(
            _canonical(forged["candidate_records"][0]["payload"]).encode()).hexdigest()
        self.assertFalse(score(forged, oracle)["all_checks_match_draft"])
        self.assertEqual(package["validated_supply_option_ids"], ["C-READ-1"])
        self.assertIsNone(package["selected_candidate_id"])
        a, b = package["candidate_records"]
        self.assertEqual(a["payload"]["source_input_digest"], b["payload"]["source_input_digest"])
        self.assertNotEqual(a["payload"]["candidate_input_digest"], b["payload"]["candidate_input_digest"])
        self.assertNotEqual(a["sha256"], b["sha256"])
        self.assertFalse(b["payload"]["human_comparison"]["verified_supply_option"])
        with tempfile.TemporaryDirectory() as temp:
            first = export_trace_once(temp, a)
            second = export_trace_once(temp, b)
            self.assertNotEqual(first, second)
            self.assertEqual(json.loads(first.read_text())["sha256"], a["sha256"])
            self.assertEqual(json.loads(second.read_text())["sha256"], b["sha256"])
            for path, candidate, record in ((first, supported, a), (second, unsupported, b)):
                self.assertEqual(replay_exported_trace(
                    self.conn, path, candidate, reader_kwargs={"commercial_rule_mode": "compiled"}),
                    record["sha256"])
            with self.assertRaisesRegex(ValueError, "differs from replayed"):
                replay_exported_trace(self.conn, first, unsupported,
                                      reader_kwargs={"commercial_rule_mode": "compiled"})
        with self.assertRaisesRegex(ValueError, "distinct"):
            compare_candidate_set(self.conn, self.run_id, [supported, supported])
        with self.assertRaisesRegex(ValueError, "one or two"):
            compare_candidate_set(self.conn, self.run_id, [supported, unsupported,
                                                        self.candidate(candidate_id="C-READ-3")])
        with self.assertRaisesRegex(ValueError, "Duplicate proposals"):
            compare_candidate_set(self.conn, self.run_id,
                                  [supported, self.candidate(candidate_id="C-READ-4")])


if __name__ == "__main__":
    unittest.main()
