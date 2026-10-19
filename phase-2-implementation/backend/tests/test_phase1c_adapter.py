"""Integration with the pinned, separately checked-out Phase 1C reference data."""

from dataclasses import replace
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from uuid import UUID

from dealdesk_phase2.contracts import PHASE1C_COMMIT
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter, PinnedBundleV1

try:
    import psycopg
except ImportError:
    psycopg = None


PINNED_PATH = os.environ.get("DEALDESK_PHASE1C_CHECKOUT")
RUN_STOCK = UUID("00000000-0000-4000-8000-000000010001")
RUN_OFFER = UUID("00000000-0000-4000-8000-000000030001")


@unittest.skipUnless(psycopg and os.environ.get("DATABASE_URL") and PINNED_PATH,
                     "Requires pinned Phase 1C checkout and disposable PostgreSQL fixture DB")
class Phase1CAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(PINNED_PATH))
        from test_phase1c_reader import load_fixture_rows
        load_fixture_rows()  # Actual 14-case Phase 1C reference rows; no answer keys.
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["DATABASE_URL"]))

    def test_pin_and_binding_reference_evidence_is_read_only(self):
        self.assertEqual(PHASE1C_COMMIT, self.adapter._context(
            self.adapter.read_original(self.connect, RUN_STOCK, "A-STOCK").decode(),
            "A-STOCK").context.phase1c_commit)
        with self.connect() as conn:
            before = conn.execute("SELECT run_status FROM deal_desk.deal_runs WHERE run_id=%s",
                                  (RUN_STOCK,)).fetchone()
        pinned = self.adapter.read_original(self.connect, RUN_STOCK, "A-STOCK")
        bundle = pinned.decode()
        line = bundle["facts"]["lines"][0]
        product = "stock_then_confirmed_receipt-P"
        self.assertEqual(bundle["facts"]["supply"]["stock"][product][0]["free"], 8)
        self.assertEqual(bundle["facts"]["supply"]["binding_receipts"][product][0]["free"], 3)
        self.assertEqual(line["fulfillment_status"], "confirmed_by_date")
        self.assertEqual(self.adapter.fixed_original_decision(pinned)["run_id"], RUN_STOCK)
        self.assertGreater(pinned.size_bytes, 0)
        print(f"M1.0 sealed binding fixture: {pinned.size_bytes} UTF-8 bytes")
        with self.connect() as conn:
            after = conn.execute("SELECT run_status FROM deal_desk.deal_runs WHERE run_id=%s",
                                 (RUN_STOCK,)).fetchone()
        self.assertEqual(before, after)

    def test_conditional_offer_is_not_binding_receipt(self):
        pinned = self.adapter.read_original(self.connect, RUN_OFFER, "A-OFFER")
        bundle = pinned.decode()
        product = "offer_without_supplier_commitment-P"
        self.assertEqual(bundle["facts"]["supply"]["binding_receipts"][product], [])
        self.assertEqual(bundle["facts"]["lines"][0]["fulfillment_status"], "conditional")
        self.assertTrue(bundle["supplier_offers"])
        print(f"M1.0 sealed conditional fixture: {pinned.size_bytes} UTF-8 bytes")

    def test_run_and_source_identity_fail_closed(self):
        pinned = self.adapter.read_original(self.connect, RUN_STOCK, "A-STOCK")
        with self.assertRaises(EvidenceMismatch):
            self.adapter.verify_candidate(self.connect, pinned, SimpleNamespace(
                parent_run_id=RUN_OFFER, parent_deal_id=pinned.context.original_deal_id))
        fake = replace(pinned, context=replace(pinned.context, source_input_digest="0" * 64))
        with self.assertRaises(EvidenceMismatch):
            self.adapter.verify_candidate(self.connect, fake, SimpleNamespace(
                parent_run_id=RUN_STOCK, parent_deal_id=pinned.context.original_deal_id))
        other = self.adapter.read_original(self.connect, RUN_OFFER, "A-OFFER")
        mixed = PinnedBundleV1(pinned.context, other.serialized, other.size_bytes)
        with self.assertRaises(ValueError):
            mixed.decode()


if __name__ == "__main__":
    unittest.main()
