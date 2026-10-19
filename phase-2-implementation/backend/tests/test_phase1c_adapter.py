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
        cls.connect = staticmethod(lambda: psycopg.connect(os.environ["DATABASE_URL"]))
        with cls.connect() as conn:
            exists = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals WHERE deal_id=%s)",
                                  ("D-stock_then_confirmed_receipt",)).fetchone()[0]
        if not exists:
            raise RuntimeError("Load pinned Phase 1C reference rows before adapter tests")

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
        with self.connect() as conn:
            jsonb_bytes = conn.execute("SELECT pg_column_size(%s::jsonb)",
                                       (pinned.serialized,)).fetchone()[0]
        print(f"M1.0 sealed binding fixture: {pinned.size_bytes} UTF-8 bytes; "
              f"{jsonb_bytes} PostgreSQL jsonb expression bytes (not checkpoint storage)")
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

    def test_changed_selected_source_stops_candidate_reread(self):
        pinned = self.adapter.read_original(self.connect, RUN_STOCK, "A-STOCK")
        candidate_identity = SimpleNamespace(parent_run_id=RUN_STOCK,
                                             parent_deal_id=pinned.context.original_deal_id)
        source_id = "INV-stock_then_confirmed_receipt-P"
        with self.connect() as conn:
            original_quantity = conn.execute(
                "SELECT quantity_on_hand FROM deal_desk.inventory WHERE inventory_id=%s",
                (source_id,)).fetchone()[0]
            conn.execute("UPDATE deal_desk.inventory SET quantity_on_hand=%s WHERE inventory_id=%s",
                         (original_quantity + 1, source_id))
        try:
            with self.assertRaisesRegex(EvidenceMismatch, "selected evidence changed"):
                self.adapter.verify_candidate(self.connect, pinned, candidate_identity)
        finally:
            with self.connect() as conn:
                conn.execute("UPDATE deal_desk.inventory SET quantity_on_hand=%s WHERE inventory_id=%s",
                             (original_quantity, source_id))

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
