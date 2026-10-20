"""M1.6 semantic claim boundary and fixed fallback regressions."""
import unittest
from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.investigation_graph import run_original_then_investigate
from dealdesk_phase2.live_models import _canonical_final, FINAL_SCHEMA
from dealdesk_phase2.orchestrator import build_original_graph
from test_investigation_graph import InvestigationAdapter, _tool, RUN


def claim(kind, **changes):
    value = {"type": kind, "line_id": "L1", "source_ref": "", "field": "",
             "value": "", "scope": "", "gap_code": "", "idea_code": "",
             "delivery_slices": []}
    value.update(changes)
    return value


def output(*claims, kind="finding_without_proposal", notes=None):
    return {"type": "contribution", "value": {"schema_version": "2", "kind": kind,
            "payload": {"line_id": "L1", "claims": list(claims),
                        "notes": notes or {"finding": "Untrusted free text"}}}}


class ClaimContractTests(unittest.TestCase):
    def setUp(self):
        self.adapter = InvestigationAdapter()
        self.graph = build_original_graph(self.adapter, None, InMemorySaver())
        self.config = {"configurable": {"thread_id": self.id()}}

    def run_with(self, *actions):
        return run_original_then_investigate(
            self.graph, self.config, self.adapter, OfflineModelDouble(tuple(actions)),
            assessment_id=self.id(), run_id=RUN)

    def test_dated_offer_rejected_original_preserved_and_explicitly_downgraded(self):
        dated = claim("candidate_idea", source_ref="supplier_offer:O1",
                      idea_code="ask_supplier_for_later_option",
                      delivery_slices=[{"quantity": "8", "delivery_date": "2026-09-17",
                                        "commitment_claim": "conditional"}])
        state = self.run_with(_tool(), output(
            claim("source_observation", source_ref="supplier_offer:O1",
                  field="lead_days_mode", value="10"),
            claim("conditional_possibility", source_ref="supplier_offer:O1",
                  value="supplier_confirmation_required"), dated, kind="proposal"))
        ai = state["ai_fulfillment_result"]
        self.assertEqual(ai["execution"], "completed")
        contribution = ai["contribution"]
        self.assertEqual(contribution["kind"], "finding_without_proposal")
        self.assertEqual(contribution["model_contribution_kind"], "proposal")
        self.assertIsNone(contribution["verification"])
        self.assertEqual(contribution["validation_disposition"], "downgraded")
        self.assertEqual(state["ai_claim_audit"][0]["original_claim"], dated)
        self.assertEqual(state["ai_claim_audit"][0]["reason"], "candidate_date_unverified")
        self.assertTrue(any(x["status"] == "directly_observed" for x in
                            contribution["payload"]["validated_claims"]))
        self.assertTrue(any(x["status"] == "conditional_uncommitted" for x in
                            contribution["payload"]["validated_claims"]))
        self.assertTrue(any(x["status"] == "downgraded_nonactionable" for x in
                            contribution["payload"]["validated_claims"]))
        self.assertNotIn("2026-09-17", str(contribution["payload"]["review_summary"]))
        self.assertNotIn("Untrusted free text", str(contribution["payload"]["review_summary"]))
        self.assertEqual(state["review_status"], "needs_revision")
        self.assertEqual(self.adapter.decisions, 1)
        self.assertNotIn("candidate", state)
        self.assertEqual(self.run_with(_tool(), output(dated))["ai_claim_audit"],
                         state["ai_claim_audit"])

    def test_unsupported_stock_and_false_fixed_finding_are_rejected(self):
        state = self.run_with(_tool(), output(
            claim("source_observation", source_ref="inventory:S1",
                  field="quantity_on_hand", value="20"),
            claim("fixed_finding_reference", field="quantity_by_requested_date", value="20"),
            claim("fixed_finding_reference", field="quantity_by_requested_date", value="12")))
        self.assertEqual([x["reason"] for x in state["ai_claim_audit"]],
                         ["source_value_mismatch", "fixed_finding_mismatch"])
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["payload"]
                         ["review_summary"], ["Phase 1C fixed quantity_by_requested_date: 12."])
        self.assertEqual(state["specialist_results"]["fulfillment"]["execution"], "completed")

    def test_forged_citation_and_identity_mismatch_stop_entire_contribution(self):
        for bad, error in (
            (claim("source_observation", source_ref="inventory:NOT_RETURNED",
                   field="quantity_on_hand", value="12"), "unsupported_citation"),
            (claim("candidate_idea", source_ref="supplier_offer:O1", line_id="WRONG",
                   idea_code="ask_supplier_for_later_option"), "identity_mismatch")):
            with self.subTest(error=error):
                self.setUp()
                state = self.run_with(_tool(), output(bad))
                self.assertEqual(state["ai_fulfillment_result"]["error"], error)
                self.assertIsNone(state["ai_fulfillment_result"]["contribution"])
                self.assertEqual(state["ai_claim_audit"][0]["original_content"]
                                 ["payload"]["claims"], [bad])
                self.assertEqual(state["review_status"], "needs_revision")

    def test_offer_validity_cannot_support_arrival_observation(self):
        state = self.run_with(_tool(), output(
            claim("source_observation", source_ref="supplier_offer:O1",
                  field="arrival_date", value="2026-09-17"),
            claim("conditional_possibility", source_ref="supplier_offer:O1",
                  value="supplier_confirmation_required")))
        self.assertEqual(state["ai_claim_audit"][0]["reason"], "source_field_not_exposed")
        self.assertEqual(len(state["ai_fulfillment_result"]["contribution"]["payload"]
                             ["review_summary"]), 1)

    def test_bounded_absence_does_not_infer_global_supply(self):
        state = self.run_with(_tool(), output(
            claim("evidence_gap", scope="global", gap_code="no_eligible_evidence_in_selected_pool"),
            claim("evidence_gap", scope="returned_records",
                  gap_code="no_eligible_evidence_in_selected_pool")))
        self.assertEqual([x["reason"] for x in state["ai_claim_audit"]],
                         ["absence_scope_must_be_returned_records",
                          "selected_pool_absence_not_established"])
        self.assertEqual(state["ai_fulfillment_result"]["contribution"]["kind"], "abstention")

    def test_live_final_schema_maps_only_typed_claims_to_review_path(self):
        raw = {key: ([] if key in ("claims", "delivery_slices", "citations", "tradeoffs",
                                  "assumptions", "unmet_requirements", "uncertainty_reasons")
                     else "finding_without_proposal" if key == "kind"
                     else "L1" if key == "line_id" else "")
               for key in FINAL_SCHEMA["required"]}
        raw["claims"] = [claim("fixed_finding_reference",
                               field="fulfillment_status", value="late_alternative")]
        value = _canonical_final(raw)["value"]
        self.assertEqual(value["schema_version"], "2")
        self.assertEqual(value["payload"]["claims"], raw["claims"])


if __name__ == "__main__":
    unittest.main()
