"""Focused source/identity and control-boundary checks; no answer labels."""

from copy import deepcopy
import json
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path
import unittest

from build_credit_v3 import build

HERE = Path(__file__).resolve().parent


class CreditV3SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_base = (HERE / "provisional_cases.json").read_bytes()
        cls.raw_index = (HERE / "provisional_packet_index.json").read_bytes()
        cls.base = json.loads(cls.raw_base)
        cls.authoring = json.loads((HERE / "provisional_authoring_manifest.json").read_text())
        cls.intent = json.loads((HERE / "credit_intent_review_v3.json").read_text())
        cls.index = json.loads(cls.raw_index)

    def generate(self, base=None, authoring=None, index=None, intent=None,
                 raw_base=None, raw_index=None):
        return build(base if base is not None else self.base,
                     authoring if authoring is not None else self.authoring,
                     index if index is not None else self.index,
                     intent if intent is not None else self.intent,
                     raw_base=raw_base if raw_base is not None else self.raw_base,
                     raw_index=raw_index if raw_index is not None else self.raw_index)

    def test_36_case_scopes_and_two_distinct_controls(self):
        scoped, controls, index = self.generate()
        self.assertEqual(len(scoped["cases"]), 36)
        self.assertEqual([x["case_id"] for x in controls["cases"]],
                         ["EVAL-PREP-040", "EVAL-PREP-041"])
        self.assertEqual({x["case_id"] for x in scoped["cases"]} &
                         {x["case_id"] for x in controls["cases"]}, set())
        self.assertTrue(all(x["credit_evidence_scope"]["completeness"] ==
                            "declared_complete_zero" for x in scoped["cases"]))
        self.assertEqual(index["accepted_original_answers"], 0)
        self.assertEqual(index["accepted_control_answers"], 0)
        self.assertEqual(scoped["cases"][0]["as_of_at"], "2026-09-01 12:01:00+00:00")
        nonempty, incomplete = controls["cases"]
        self.assertEqual(nonempty["credit_evidence_scope"]["completeness"],
                         "declared_complete_nonempty")
        self.assertEqual(incomplete["credit_evidence_scope"]["completeness"],
                         "explicitly_incomplete_unknown")
        self.assertEqual(len(nonempty["tables"]["accounts_receivable"]), 1)
        self.assertEqual(len(nonempty["tables"]["payment_history"]), 1)
        self.assertEqual(len(incomplete["tables"].get("accounts_receivable", [])), 0)
        self.assertEqual(len(incomplete["tables"].get("payment_history", [])), 0)
        for control in controls["cases"]:
            case_id = control["case_id"]
            self.assertEqual(control["tables"]["deals"][0]["customer_id"],
                             control["tables"]["customer_credit_profiles"][0]["customer_id"])
            self.assertEqual(control["tables"]["deals"][0]["deal_id"],
                             control["tables"]["deal_runs"][0]["deal_id"])
            self.assertEqual(control["tables"]["deal_runs"][0]["data_snapshot_ref"],
                             "EVALCREDIT-" + case_id[-3:] + "-SOURCES")
        self.assertEqual(nonempty["tables"]["accounts_receivable"][0]["outstanding_amount"],
                         "700.00")
        self.assertEqual(nonempty["tables"]["payment_history"][0]["paid_amount"], "300.00")

    def test_pinned_input_or_index_mutation_fails(self):
        with self.assertRaisesRegex(ValueError, "Pinned v2 source"):
            self.generate(raw_base=self.raw_base + b" ")
        altered = deepcopy(self.index)
        altered["source_definition_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Pinned v2 source"):
            self.generate(raw_index=json.dumps(altered).encode())

    def test_case_level_credit_mutations_fail(self):
        mutations = [
            ("accounts_receivable", [{"invoice_number": "unexpected"}]),
            ("payment_history", [{"payment_id": "unexpected"}]),
        ]
        for table, rows in mutations:
            with self.subTest(table=table):
                changed = deepcopy(self.base)
                changed["cases"][17]["tables"][table] = rows
                with self.assertRaisesRegex(ValueError, "unexpected credit"):
                    self.generate(base=changed)
        changed = deepcopy(self.base)
        changed["cases"][30]["tables"]["customer_credit_profiles"][0]["credit_limit"] = 2000
        with self.assertRaisesRegex(ValueError, "individual credit source review"):
            self.generate(base=changed)
        changed = deepcopy(self.base)
        changed["cases"][19]["tables"]["customer_credit_profiles"][0]["commitments_as_of_at"] = (
            "2026-08-29T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "not fresh"):
            self.generate(base=changed)

    def test_authoring_identity_or_case_order_mutation_fails(self):
        changed = deepcopy(self.authoring)
        changed["cases"][0]["archetype_id"] = "CREDIT-LIMIT"
        with self.assertRaisesRegex(ValueError, "source/authoring/index identity"):
            self.generate(authoring=changed)
        changed = deepcopy(self.index)
        changed["cases"][0]["case_id"] = "EVAL-PREP-036"
        with self.assertRaisesRegex(ValueError, "source/authoring/index identity"):
            self.generate(index=changed)

    def test_individual_review_missing_or_wrong_fails(self):
        changed = deepcopy(self.intent)
        changed["cases"][19]["quote_total_eur"] = "0.00"
        with self.assertRaisesRegex(ValueError, "individual credit source review"):
            self.generate(intent=changed)
        changed = deepcopy(self.intent)
        changed["cases"].pop()
        with self.assertRaisesRegex(ValueError, "Individual credit source review missing"):
            self.generate(intent=changed)

    def test_nonempty_control_invoice_payment_reconcile_and_unknown_is_distinct(self):
        _, controls, _ = self.generate()
        nonempty, unknown = controls["cases"]
        ar = nonempty["tables"]["accounts_receivable"][0]
        payment = nonempty["tables"]["payment_history"][0]
        self.assertEqual(ar["customer_id"], payment["customer_id"])
        self.assertEqual(ar["invoice_number"], payment["invoice_number"])
        self.assertEqual(Decimal(ar["original_amount"]),
                         Decimal(payment["paid_amount"]) + Decimal(ar["outstanding_amount"]))
        cutoff = datetime.fromisoformat(nonempty["tables"]["deal_runs"][0]["as_of_at"]).date()
        self.assertLess(date.fromisoformat(ar["due_date"]), cutoff)
        self.assertLessEqual(date.fromisoformat(payment["paid_date"]), cutoff)
        self.assertEqual(ar["status"], "Overdue")
        self.assertEqual(unknown["credit_evidence_scope"]["customer_invoice_population"],
                         "not_established")
        self.assertNotEqual(nonempty["tables"]["deals"][0]["customer_id"],
                            unknown["tables"]["deals"][0]["customer_id"])


if __name__ == "__main__":
    unittest.main()
