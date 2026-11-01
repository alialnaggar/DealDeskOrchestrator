"""No model calls: exact fixed/interface boundaries and proposed-gap negatives."""

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
import unittest

from dealdesk_phase2.graph_state import SPECIALISTS
from dealdesk_phase2.m22_evidence_gaps import _fixed_gaps, _suggestions
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch


def context():
    return SimpleNamespace(assessment_id="A", phase1c_run_id="R",
        original_deal_id="D", bundle_sha256="a" * 64, source_input_digest="b" * 64,
        as_of_at=datetime(2026, 9, 1, tzinfo=timezone.utc))


def rows():
    payloads = {
        "configuration": {"compatibility": [], "lines": [{"line_id": "L1", "status": "valid"}]},
        "pricing": {"cost_evidence_gaps": [], "rule_hits": []},
        "fulfillment": [{"line_id": "L1", "status": "confirmed_by_date"}],
        "credit": {"commitments_fresh": True, "rule_hits": []},
        "policy": {"per_rule_prerequisites_available": False, "rule_hits": []},
        "approval_routing": {"route_withheld": False, "required_roles": []}}
    return {name: {"execution": "completed", "finding": "calculated", "payload": payload}
            for name, payload in payloads.items()}


def pool(*, receivables=None):
    return {"deal": {"customer_id": "C"},
            "credit": {"customer_id": "C", "commitments_as_of_at": datetime(
                2026, 8, 1, tzinfo=timezone.utc)},
            "receivables": [] if receivables is None else receivables, "payments": []}


class EvidenceGapContractTests(unittest.TestCase):
    def test_six_specialists_complete_finding_and_explicit_zero(self):
        found = _fixed_gaps(context(), ("original", "D"), rows(), pool(
            receivables=[{"outstanding_amount": 0}]))
        self.assertEqual(set(found), set(SPECIALISTS))
        self.assertEqual(found["configuration"], [])
        self.assertEqual(found["pricing"], [])
        self.assertEqual(found["fulfillment"], [])
        self.assertEqual(found["credit"][0]["verification"], "interface_limit")
        self.assertEqual(found["policy"][0]["verification"], "interface_limit")
        self.assertEqual(found["approval_routing"], [])
        self.assertEqual(found["credit"], _fixed_gaps(context(), ("original", "D"),
            rows(), pool())["credit"], "one zero-valued row is not complete-zero scope")

    def test_dated_stale_incomplete_conflict_and_candidate_separation(self):
        fixed = rows()
        fixed["configuration"]["payload"]["compatibility"] = [{
            "status": "unknown", "compatibility_rule_id": "RULE1"}]
        fixed["pricing"]["payload"]["cost_evidence_gaps"] = [
            "assembly_cost_disagreement:BOM1"]
        fixed["fulfillment"]["payload"] = [
            {"line_id": "L1", "status": "pending_production_check"},
            {"line_id": "L2", "status": "conditional"},
            {"line_id": "L3", "status": "feasible_uncommitted"},
            {"line_id": "L4", "status": "confirmed_by_date", "installation": "unknown"}]
        fixed["credit"]["payload"]["commitments_fresh"] = False
        fixed["approval_routing"]["payload"]["route_withheld"] = True
        original = _fixed_gaps(context(), ("original", "D"), fixed, pool())
        self.assertEqual([original[n][0]["reason_code"] for n in (
            "configuration", "pricing", "fulfillment", "credit", "policy",
            "approval_routing")], ["unavailable", "conflicting", "incomplete",
                                 "stale", "unavailable", "unavailable"])
        self.assertEqual(original["credit"][0]["source_ref"], "credit_profile:C")
        self.assertEqual(original["credit"][0]["scope"], "selected_reader_pool")
        self.assertEqual(original["fulfillment"][1]["reason_code"],
                         "conditional_unconfirmed")
        self.assertEqual(original["fulfillment"][2]["reason_code"],
                         "conditional_unconfirmed")
        self.assertEqual(original["fulfillment"][3]["requirement_id"],
                         "installation_eligibility_missing")
        self.assertEqual(original["configuration"][0]["rule_id"], "RULE1")
        candidate = _fixed_gaps(context(), ("candidate", "ALT"), fixed, pool())
        self.assertTrue(all(g["subject_id"] == "ALT" for group in candidate.values()
                            for g in group))
        self.assertEqual(candidate["credit"][0]["source_ref"], None)
        self.assertEqual(original["credit"][0]["subject_id"], "D")
        fixed["credit"]["execution"] = "skipped"
        skipped = _fixed_gaps(context(), ("original", "D"), fixed, pool())
        self.assertEqual([g["reason_code"] for g in skipped["credit"]],
                         ["prerequisite_unmet"])
        fixed["credit"]["execution"] = "error"
        errored = _fixed_gaps(context(), ("original", "D"), fixed, pool())
        self.assertEqual(errored["credit"][0]["verification"], "interface_limit")
        self.assertEqual(errored["credit"][0]["requirement_id"],
                         "fixed_result_unavailable")

    def test_abstention_does_not_erase_verified_gap_or_promote_suggestion(self):
        fixed = rows()
        fixed["credit"]["payload"]["commitments_fresh"] = False
        gaps = _fixed_gaps(context(), ("original", "D"), fixed, pool())
        state = {"m21_ai_results": {"credit": {"execution": "abstained"}},
            "tool_access_ledger": [{"status": "completed",
                "identity": {"specialist": "credit"},
                "result": {"records": [{"ref": "credit_profile:C", "fields": {}}]},
                "returned_refs": ["credit_profile:C"]}]}
        proposed = _suggestions(context(), state, gaps, [{"specialist": "credit",
            "requirement_id": "credit_commitments_fresh", "source_ref": "credit_profile:C"}])
        self.assertEqual(proposed[0]["verification"], "suggested_unverified")
        self.assertEqual(gaps["credit"][0]["verification"], "verified")
        self.assertEqual(proposed[0]["resolution_status"], "unresolved")
        for malformed in (
            {"specialist": "credit", "requirement_id": "invented_document", "source_ref": None},
            {"specialist": "credit", "requirement_id": "credit_commitments_fresh",
             "source_ref": "credit_profile:other"},
            {"specialist": "credit", "requirement_id": "credit_ledger_completeness",
             "source_ref": "credit_profile:C"},
            {"specialist": "approval_routing", "requirement_id": "credit_commitments_fresh",
             "source_ref": None},
            {"specialist": "credit", "requirement_id": "credit_commitments_fresh",
             "source_ref": None, "verified": True}):
            with self.subTest(malformed=malformed), self.assertRaises(EvidenceMismatch):
                _suggestions(context(), state, gaps, [malformed])
        wrong = deepcopy(pool())
        wrong["credit"]["customer_id"] = "other"
        with self.assertRaises(EvidenceMismatch):
            _fixed_gaps(context(), ("original", "D"), fixed, wrong)


if __name__ == "__main__":
    unittest.main()
