"""D9 read-only pinned-source check plus synthetic/blank-form negative tests."""

import copy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import d9_review_prep as d9
import d8_readiness as d8


class ReviewPrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get("DEALDESK_PHASE1C_REVIEW_CHECKOUT",
                        "/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c"))
        if not root.exists():
            raise unittest.SkipTest("Separate Phase 1C review checkout unavailable")
        cls.index, cls.scope, cls.state, cls.workspace = d9.load_sources(root)
        cls.gates = {name: "decision_pending" for name in d9.GATES}
        _, _, _, cls.check_workspace, _ = d8.load_contract(root)
        cls.check_workspace = staticmethod(cls.check_workspace)

    def test_36_cases_index_is_only_source_references_and_blank_pilot(self):
        self.assertEqual(len(self.index["cases"]), 36)
        self.assertEqual(len(self.scope), 36)
        pilot = d9.blank_pilot(self.index, self.workspace)
        self.assertEqual([x["case_id"] for x in pilot["cases"]],
                         [f"EVAL-PREP-{n:03d}" for n in d9.PILOT])
        self.assertEqual(d9.check_pilot(pilot, self.index, self.workspace, None, self.state,
                                        self.gates, self.check_workspace)["missing_pilot_decisions"], 6)
        for case in pilot["cases"]:
            self.assertEqual(case["review_status"], "pending")
            self.assertIsNone(case["reviewer"])
            self.assertTrue(all(x["finding"] is None for x in case["findings"].values()))
        text = d9.render_index(self.index, self.scope, self.state, source_version="synthetic-index-test",
                               retrieval="source-only test")
        self.assertEqual(text.count("| `EVAL-PREP-"), 36)
        self.assertNotIn("model_review_v2_draft", text)
        self.assertNotIn("gate_for_review", text)

    def test_missing_export_prevents_draft(self):
        pilot = d9.blank_pilot(self.index, self.workspace)
        pilot["cases"][0]["review_status"] = "draft_complete"
        with self.assertRaisesRegex(ValueError, "verified packet"):
            d9.check_pilot(pilot, self.index, self.workspace, None, self.state, self.gates,
                           self.check_workspace)

    def test_rejects_missing_case_stale_hash_and_fake_acceptance(self):
        for field, value, message in (("cases", [], "missing"),
                                      ("status", "accepted", "acceptance")):
            pilot = d9.blank_pilot(self.index, self.workspace)
            pilot[field] = value
            with self.assertRaisesRegex(ValueError, message):
                d9.check_pilot(pilot, self.index, self.workspace, None, self.state,
                               self.gates, self.check_workspace)
        pilot = d9.blank_pilot(self.index, self.workspace)
        pilot["cases"][0]["packet_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pin"):
            d9.check_pilot(pilot, self.index, self.workspace, None, self.state,
                           self.gates, self.check_workspace)

    def test_unresolved_gates_cannot_be_claimed_approved(self):
        gates = copy.deepcopy(self.gates)
        gates["credit_v3_scope_and_intake"] = "approved"
        with self.assertRaisesRegex(ValueError, "Methodology gate"):
            d9.check_pilot(d9.blank_pilot(self.index, self.workspace), self.index,
                               self.workspace, None, self.state, gates, self.check_workspace)

    def test_blind_material_rejects_draft_decision_marker(self):
        pilot = d9.blank_pilot(self.index, self.workspace)
        pilot["cases"][0]["overall"]["rationale"] = "case_020_business_choice.json"
        with self.assertRaisesRegex(ValueError, "Draft/model-assisted"):
            d9.check_pilot(pilot, self.index, self.workspace, None, self.state,
                           self.gates, self.check_workspace)

    def test_actual_export_hashes_read_only_when_available(self):
        packets = Path(os.environ.get("DEALDESK_PHASE1C_ORIGINAL_PACKETS",
                                   "/tmp/opencode/phase1c_original_packets"))
        if not packets.exists():
            raise unittest.SkipTest("Local Phase 1C exported source packets unavailable")
        root = Path(os.environ.get("DEALDESK_PHASE1C_REVIEW_CHECKOUT",
                        "/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c"))
        _, _, state, _ = d9.load_sources(root, packets)
        self.assertEqual(sum(x.startswith("verified:") for x in state.values()), 36)

    def test_changed_credit_scope_pin_fails_closed(self):
        root = Path(os.environ.get("DEALDESK_PHASE1C_REVIEW_CHECKOUT",
                        "/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c"))
        with patch.object(d9, "SCOPE_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "Credit v3 source pin"):
                d9.load_sources(root)


if __name__ == "__main__":
    unittest.main()
