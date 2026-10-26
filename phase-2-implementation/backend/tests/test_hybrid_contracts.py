"""Offline-only provider-independent hybrid action and binding checks."""

import unittest

from dealdesk_phase2.hybrid_contracts import (ACTION_VERSION, HybridContractError,
                                              decision, final, strict_binding,
                                              verified_source_slices)
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from test_candidate_m17 import fake_input, ledger, proposal


class HybridContractTests(unittest.TestCase):
    def decide(self, raw):
        return decision(raw, line_id=fake_input().line_id,
                        permitted_tools=fake_input().permitted_tools)

    def test_explicit_inspect_and_submission_intents_only(self):
        action = {"version": ACTION_VERSION, "kind": "inspect",
                  "tool_name": "inspect_fulfillment_paths", "arguments": {
                      "line_id": fake_input().line_id}, "purpose_code": "check_dated_path"}
        self.assertEqual(self.decide(action), action)
        for kind in ("submit_finding", "abstain"):
            intent = self.decide({"version": ACTION_VERSION, "kind": kind})
            self.assertEqual(final({"version": ACTION_VERSION, "kind": kind,
                                    "payload": {}}, intent)["kind"], kind)
        self.assertEqual(self.decide({"version": ACTION_VERSION,
                                      "kind": "submit_proposal",
                                      "submission_kind": "binding_partial_delivery"})["kind"],
                         "submit_proposal")

    def test_no_ready_missing_intent_or_wrong_final(self):
        for raw in ("READY", {}, {"version": ACTION_VERSION, "kind": "ready"},
                    {"version": ACTION_VERSION, "kind": "inspect", "tool_name":
                     "inspect_fulfillment_paths", "arguments": {"line_id": "OTHER"},
                     "purpose_code": "check_dated_path"},
                    {"version": ACTION_VERSION, "kind": "submit_finding", "payload": {}}):
            with self.subTest(raw=raw), self.assertRaises(HybridContractError):
                self.decide(raw)
        intent = self.decide({"version": ACTION_VERSION, "kind": "submit_finding"})
        for raw in ({"version": ACTION_VERSION, "kind": "abstain", "payload": {}},
                    {"version": ACTION_VERSION, "kind": "submit_finding", "payload": {},
                     "tool_name": "inspect_line_supply"}):
            with self.assertRaises(HybridContractError):
                final(raw, intent)

    def test_canonical_quantities_no_silent_repairs(self):
        events = ledger()
        for entry in events:
            entry["result"]["findings"]["binding_options"] = [
                {"stock_id": "INV-m17-binding-test", "supply_ids": [],
                 "arrival": "2026-09-04"},
                {"stock_id": None, "supply_ids": ["IN-m17-binding-test"],
                 "arrival": "2026-09-08"}]
        # Use actual fixture source IDs rather than assumed literals.
        events[0]["result"]["findings"]["binding_options"][0]["stock_id"] = (
            events[0]["returned_refs"][0].split(":", 1)[1])
        events[0]["result"]["findings"]["binding_options"][1]["supply_ids"] = [
            events[0]["returned_refs"][1].split(":", 1)[1]]
        raw = proposal()
        self.assertEqual(strict_binding(raw, fake_input(), events)["verification"], "unverified")
        for value in ("08", "00", "8.000", "８", "8.5", 8, "-8", "0"):
            with self.subTest(value=value), self.assertRaisesRegex(
                    HybridContractError, "quantity_noncanonical"):
                strict_binding(proposal(early=value), fake_input(), events)

    def test_returned_id_does_not_prove_date_slice_binding(self):
        events = ledger()
        ref_stock, ref_inbound = events[0]["returned_refs"]
        events[0]["result"]["findings"]["binding_options"] = [
            {"stock_id": ref_stock.split(":", 1)[1], "supply_ids": [],
             "arrival": "2026-09-04"},
            {"stock_id": None, "supply_ids": [ref_inbound.split(":", 1)[1]],
             "arrival": "2026-09-08"}]
        bad = proposal()
        bad["delivery_slices"][0]["source_refs"] = [ref_inbound]
        self.assertEqual(strict_binding(bad, fake_input(), events)["verification"], "unverified")
        # A returned ID or even a visible option is not dated support; the
        # pinned verifier's slice trace must be checked after construction.
        trace = {"candidate_trace": {"assessment": {
            "status": "supply_supported_unreserved", "slices": [
                {"line_id": fake_input().line_id, "quantity": 8,
                 "arrival_date": "2026-09-04", "source_ids": [ref_stock.split(":", 1)[1]]},
                {"line_id": fake_input().line_id, "quantity": 2,
                 "arrival_date": "2026-09-08", "source_ids": [ref_inbound.split(":", 1)[1]]}]}}}
        verified_source_slices(proposal(), trace)
        with self.assertRaisesRegex(EvidenceMismatch, "fixed_source_to_slice_unproven"):
            verified_source_slices(bad, trace)
        self.assertEqual(strict_binding(proposal(), fake_input(), ledger())["verification"],
                         "unverified")  # access-valid, NOT source-to-slice verified
        with self.assertRaises(ValueError):
            strict_binding(proposal(), fake_input(), ledger(evidence="unsupported_capability"))


if __name__ == "__main__":
    unittest.main()
