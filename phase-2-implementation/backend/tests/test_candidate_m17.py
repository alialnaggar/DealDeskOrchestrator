"""Binding proposal guards and pinned Phase 1C candidate integration."""

from datetime import date
import os
from pathlib import Path
import unittest
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver

from dealdesk_phase2.candidate_contract import validate_binding_proposal
from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.fulfillment_agent import FulfillmentInputV1, OfflineModelDouble
from dealdesk_phase2.investigation_graph import (run_original_investigate_and_review,
                                                   run_original_then_investigate)
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter

try:
    import psycopg
except ImportError:
    psycopg = None


RUN = UUID("00000000-0000-4000-8000-000000017771")
DEAL = "D-m17-binding-test"
LINE = "L-m17-binding-test"
STOCK = "INV-stock_then_confirmed_receipt-P"
INBOUND = "IN-stock_then_confirmed_receipt"
REQUIRED = bool(psycopg and os.getenv("DATABASE_URL") and os.getenv("CHECKPOINT_DATABASE_URL")
                and os.getenv("DEALDESK_PHASE1C_CHECKOUT"))


def proposal(*, later="2026-09-08", source=INBOUND, early="8"):
    return {"line_id": LINE, "delivery_slices": [
        {"quantity": early, "delivery_date": "2026-09-04", "source_refs": ["inventory:" + STOCK]},
        {"quantity": "2", "delivery_date": later, "source_refs": ["inbound_supply:" + source]}],
        "tradeoff_code": "partial_delivery_requires_customer_acceptance"}


def tool():
    return {"type": "tool", "tool": "inspect_fulfillment_paths", "arguments": {"line_id": LINE}}


def contribution(value=None):
    return {"type": "contribution", "value": {"schema_version": "3",
        "kind": "binding_proposal", "payload": proposal() if value is None else value}}


def fake_input():
    return FulfillmentInputV1("A-M17", str(RUN), DEAL, "bundle", "source", LINE, "P", "10", "8",
                              "2026-09-04", "DE", "Berlin", True, "late_alternative",
                              ("inspect_fulfillment_paths",), 11)


def ledger(*, evidence="eligible_binding", refs=None):
    refs = refs if refs is not None else ["inventory:" + STOCK, "inbound_supply:" + INBOUND]
    return [{"tool": "inspect_fulfillment_paths", "status": "completed",
             "args": {"line_id": LINE}, "returned_refs": refs,
             "identity": {"assessment_id": "A-M17", "phase1c_run_id": str(RUN),
                          "subject_id": DEAL, "bundle_sha256": "bundle",
                          "source_input_digest": "source", "specialist": "fulfillment"},
             "result": {"execution": "completed", "evidence": evidence,
                        "more_in_sealed_pool": False,
                        "findings": {"binding_options": [{"stock_id": STOCK,
                                                         "supply_ids": [INBOUND]}]}}}]


class BindingContractTests(unittest.TestCase):
    def test_authorized_binding_path_is_only_an_unverified_proposal(self):
        result = validate_binding_proposal(proposal(), fake_input(), ledger())
        self.assertEqual(result["verification"], "unverified")
        self.assertEqual([s["quantity"] for s in result["delivery_slices"]], ["8", "2"])

    def test_offer_or_unseen_source_cannot_be_labeled_binding(self):
        for bad in (proposal(source="not-returned"),
                    {**proposal(), "delivery_slices": [proposal()["delivery_slices"][0],
                      {"quantity": "2", "delivery_date": "2026-09-08",
                       "source_refs": ["supplier_offer:O1"]}]}):
            with self.subTest(bad=bad), self.assertRaisesRegex(EvidenceMismatch, "not returned"):
                validate_binding_proposal(bad, fake_input(), ledger())
        with self.assertRaises(ValueError):
            validate_binding_proposal(proposal(), fake_input(), ledger(evidence="unsupported_capability"))

    def test_identity_permission_quantity_and_date_fail_closed(self):
        with self.assertRaises(EvidenceMismatch):
            validate_binding_proposal(proposal(), fake_input(),
                                      [{**ledger()[0], "identity": {**ledger()[0]["identity"],
                                                                    "subject_id": "OTHER"}}])
        with self.assertRaises(ValueError):
            validate_binding_proposal(proposal(),
                fake_input().__class__(**{**vars(fake_input()), "allow_partial_delivery": False}), ledger())
        for bad in (proposal(early="0"), proposal(early="8.5"), proposal(later="2026-02-30")):
            with self.assertRaises(ValueError):
                validate_binding_proposal(bad, fake_input(), ledger())

    def test_conditional_offer_failure_preserves_original_and_raw_audit(self):
        from test_investigation_graph import InvestigationAdapter, RUN as SYNTHETIC_RUN

        adapter = InvestigationAdapter()
        saver = InMemorySaver()
        graph = build_original_graph(adapter, None, saver)
        config = {"configurable": {"thread_id": "M17-conditional-offer"}}
        synthetic = {"line_id": "L1", "tradeoff_code":
                     "partial_delivery_requires_customer_acceptance",
                     "delivery_slices": [{"quantity": "12", "delivery_date": "2026-09-04",
                                          "source_refs": ["inventory:S1"]},
                                         {"quantity": "8", "delivery_date": "2026-09-17",
                                          "source_refs": ["supplier_offer:O1"]}]}
        model = OfflineModelDouble((
            {"type": "tool", "tool": "inspect_fulfillment_paths", "arguments": {"line_id": "L1"}},
            contribution(synthetic)))
        state = run_original_investigate_and_review(graph, config, adapter, model,
            assessment_id="M17-conditional-offer", run_id=SYNTHETIC_RUN)
        self.assertEqual(state["ai_fulfillment_result"]["execution"], "error")
        self.assertEqual(state["review_status"], "needs_revision")
        self.assertEqual(state["candidate_records"], {})
        self.assertEqual(state["reviewer_package"]["candidates"], [])
        self.assertEqual(state["ai_claim_audit"][-1]["original_content"]["payload"], synthetic)

    def test_reviewer_labels_validated_offer_inquiry_as_nonactionable(self):
        from test_investigation_graph import InvestigationAdapter, RUN as SYNTHETIC_RUN
        from test_claim_validation_m16 import claim, output, _tool

        adapter = InvestigationAdapter()
        graph = build_original_graph(adapter, None, InMemorySaver())
        config = {"configurable": {"thread_id": "M17-review-offer-inquiry"}}
        dated = claim("candidate_idea", source_ref="supplier_offer:O1",
                      idea_code="ask_supplier_for_later_option",
                      delivery_slices=[{"quantity": "8", "delivery_date": "2026-09-17",
                                        "commitment_claim": "conditional"}])
        state = run_original_investigate_and_review(graph, config, adapter,
            OfflineModelDouble((_tool(), output(dated, kind="proposal"))),
            assessment_id="M17-review-offer-inquiry", run_id=SYNTHETIC_RUN)
        review = state["reviewer_package"]
        self.assertEqual(review["candidates"], [])
        self.assertEqual(review["unverified_planning_ideas"][0]["status"],
                         "downgraded_nonactionable")
        self.assertEqual(review["audit_rejection_count"], len(state["ai_claim_audit"]))
        self.assertNotIn("2026-09-17", str(review))
        self.assertEqual(state["ai_claim_audit"][0]["original_claim"], dated)


@unittest.skipUnless(REQUIRED, "Requires separately pinned Phase 1C and disposable PostgreSQL DBs")
class PinnedBindingCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        with cls.connect() as conn:
            conn.execute("SET LOCAL search_path TO deal_desk, public")
            exists = conn.execute("SELECT EXISTS(SELECT 1 FROM deal_desk.deals WHERE deal_id=%s)",
                                  ("D-stock_then_confirmed_receipt",)).fetchone()[0]
            if not exists:
                raise RuntimeError("Pinned Phase 1C fixture must be loaded by CI")
            conn.execute("""INSERT INTO deal_desk.deals
                (deal_id,customer_id,salesperson_id,deal_name,submitted_at,currency_code,
                 catalog_version,policy_set_code,requested_delivery_date,destination_country_code,
                 destination_region,shipping_service_code,terms_json,deal_status,dataset_type)
                VALUES (%s,'C-stock_then_confirmed_receipt','SALES-FIXTURE','M1.7 binding test',
                '2026-09-01 09:00+00','EUR','CATALOGUE_2026_V1','BASELINE_2026',
                '2026-09-04','DE','Berlin','standard',
                '{"allow_partial_delivery":true,"contract_clause_codes":["standard"],"payment_terms_days":30}',
                'Draft','generated_test')""", (DEAL,))
            conn.execute("""INSERT INTO deal_desk.deal_lines
                (deal_line_id,deal_id,line_number,product_id,quantity,quoted_unit_price,configuration_json)
                VALUES (%s,%s,1,'stock_then_confirmed_receipt-P',10,900,'{}')""", (LINE, DEAL))
            conn.execute("UPDATE deal_desk.deals SET deal_status='Submitted' WHERE deal_id=%s", (DEAL,))
            conn.execute("""INSERT INTO deal_desk.deal_runs
                (run_id,deal_id,original_policy_set_code,applied_policy_set_code,catalog_version_used,
                 as_of_at,data_snapshot_ref,input_snapshot_json,config_hash,run_status,started_at)
                VALUES (%s,%s,'BASELINE_2026','BASELINE_2026','CATALOGUE_2026_V1',
                '2026-09-01 12:00+00','FIXTURE-stock_then_confirmed_receipt',
                '{"deal_id":"D-m17-binding-test"}','FIXTURE-CONFIG','queued','2026-09-01 12:00+00')""",
                (RUN, DEAL))

    @staticmethod
    def connect():
        return psycopg.connect(os.environ["DATABASE_URL"])

    def _candidate(self, pinned, value=None):
        from dealdesk_phase2.candidate_contract import construct_candidate

        raw = proposal() if value is None else value
        normalized = {"version": "m1.7-binding-v1", "line_id": LINE,
            "delivery_slices": raw["delivery_slices"], "tradeoff_code": raw["tradeoff_code"],
            "verification": "unverified"}
        return construct_candidate(self.adapter, pinned, normalized)[0]

    def test_positive_phase2_adapter_rechecks_binding_supply_read_only(self):
        pinned = self.adapter.read_original(self.connect, RUN, "M17-ADAPTER")
        with self.connect() as conn:
            before = conn.execute("SELECT requested_delivery_date,terms_json FROM deal_desk.deals "
                                  "WHERE deal_id=%s", (DEAL,)).fetchone()
        checked, decision = self.adapter.verify_candidate(self.connect, pinned,
                                                            self._candidate(pinned))
        self.assertEqual(checked["candidate_trace"]["assessment"]["status"],
                         "supply_supported_unreserved")
        self.assertEqual(decision["status"], "needs_revision")
        self.assertEqual(checked["deal"]["requested_delivery_date"], date(2026, 9, 4))
        with self.connect() as conn:
            after = conn.execute("SELECT requested_delivery_date,terms_json FROM deal_desk.deals "
                                 "WHERE deal_id=%s", (DEAL,)).fetchone()
            writes = conn.execute("SELECT count(*) FROM deal_desk.agent_execution_log WHERE run_id=%s",
                                  (RUN,)).fetchone()[0]
        self.assertEqual((before, writes), (after, 0))

    def test_full_graph_handoff_and_checkpoint_restart(self):
        config = {"configurable": {"thread_id": "M17-RESTART"}}
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver,
                                         interrupt_after=("candidate_construct",))
            paused = run_original_then_investigate(graph, config, self.adapter,
                OfflineModelDouble((tool(), contribution())), assessment_id="M17-RESTART", run_id=RUN)
            self.assertEqual(graph.get_state(config).next, ("candidate_construct",))
            graph.invoke(None, config)
            paused = graph.get_state(config)
            self.assertEqual(paused.next, ("candidate_verify",))
            self.assertEqual(paused.values["candidate_status"], "unverified")
            context = paused.values["context"]
            spent = sum(bool(x.get("counted")) for x in paused.values["tool_access_ledger"])
            original_results = paused.values["specialist_results"]
            claim_audit = paused.values.get("ai_claim_audit", [])
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            state = run_original_investigate_and_review(graph, config, self.adapter,
                OfflineModelDouble(()), assessment_id="M17-RESTART", run_id=RUN)
            self.assertFalse(graph.get_state(config).next)
            self.assertEqual(state["context"], context)
            self.assertEqual(state["specialist_results"], original_results)
            self.assertEqual(state.get("ai_claim_audit", []), claim_audit)
            self.assertEqual(state["trace"].count("candidate_constructed:unverified"), 1)
            self.assertEqual(sum(bool(x.get("counted")) for x in state["tool_access_ledger"]), spent)
            self.assertEqual(len(state["specialist_results"]), 6)
            candidate = next(iter(state["candidate_records"].values()))
            self.assertEqual(candidate["fixed_supply_status"], "supply_supported_unreserved")
            self.assertEqual(list(candidate["specialist_results"]), [
                "configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"])
            self.assertTrue(all(v["subject_id"] == candidate["candidate_id"] for v in
                                candidate["specialist_results"].values()))
            review = state["reviewer_package"]
            self.assertTrue(review["candidates"],
                {"candidate_status": state.get("candidate_status"),
                 "stop_reason": state.get("stop_reason"), "trace": state.get("trace"),
                 "candidate_ids": list(state.get("candidate_records", {})),
                 "ai_execution": state.get("ai_fulfillment_result", {}).get("execution")})
            self.assertEqual(review["original"]["deal_id"], DEAL)
            self.assertEqual(review["candidates"][0]["status"], "fixed_checked")
            self.assertEqual(review["candidates"][0]["verification_outcome"],
                             "binding_supply_supported_unreserved")
            self.assertEqual(review["candidates"][0]["customer_acceptance"], "pending")
            self.assertEqual({x["reference"] for x in review["candidates"][0]["returned_source_provenance"]},
                             {"inventory:" + STOCK, "inbound_supply:" + INBOUND})
            self.assertFalse(review["candidates"][0]["routing"]["eligible_for_ordinary_routing"])
            self.assertIsNone(review["candidates"][0]["routing"]["required_roles"])
            with psycopg.connect(os.environ["CHECKPOINT_DATABASE_URL"]) as conn:
                storage = conn.execute("SELECT pg_column_size(checkpoint) FROM checkpoints "
                    "WHERE thread_id=%s ORDER BY checkpoint_id DESC LIMIT 1", ("M17-RESTART",)).fetchone()[0]
            self.assertGreater(storage, 0)
            print(f"M1.7 completed candidate checkpoint JSONB field: {storage} bytes")
            repeated = run_original_investigate_and_review(graph, config, self.adapter,
                OfflineModelDouble(()), assessment_id="M17-RESTART", run_id=RUN)
            self.assertEqual(repeated, state)
            self.assertEqual(repeated["trace"].count("candidate_fixed_checked:supply_supported_unreserved"), 1)
            self.assertFalse(graph.get_state(config).next)

    def test_unavailable_later_date_keeps_candidate_unverified(self):
        pinned = self.adapter.read_original(self.connect, RUN, "M17-LATE")
        checked, decision = self.adapter.verify_candidate(self.connect, pinned,
            self._candidate(pinned, proposal(later="2026-09-05")))
        self.assertEqual(checked["candidate_trace"]["assessment"]["status"],
                         "unknown_or_unavailable")
        self.assertNotEqual(decision["status"], "approval_required")


if __name__ == "__main__":
    unittest.main()
