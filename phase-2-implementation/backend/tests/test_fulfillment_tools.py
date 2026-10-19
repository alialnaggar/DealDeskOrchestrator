"""M1.2 sealed-source projections, permission and checkpoint budget gates."""

import copy
from datetime import date, datetime, timezone
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from uuid import UUID

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph

from dealdesk_phase2.contracts import RunContextV1
from dealdesk_phase2.evidence_bundle import seal
from dealdesk_phase2.fulfillment_tools import FulfillmentTools
from dealdesk_phase2.graph_state import context_to_record, pinned_from_state
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from dealdesk_phase2.tool_ledger import was_returned
from dealdesk_phase2.tool_permissions import (FORWARD_DAYS, MAX_CALLS, MAX_RECORDS,
                                              TrustedToolScope)

try:
    import psycopg
except ImportError:
    psycopg = None


RUN = UUID("00000000-0000-4000-8000-000000010001")
OFFER = UUID("00000000-0000-4000-8000-000000030001")
CATEGORIES = frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane"))
READY = all((psycopg, os.getenv("DATABASE_URL"), os.getenv("CHECKPOINT_DATABASE_URL"),
             os.getenv("DEALDESK_PHASE1C_CHECKOUT")))


class _FakeGraph:
    def __init__(self, state):
        self.state = copy.deepcopy(state)

    def get_state(self, _config):
        return SimpleNamespace(values=copy.deepcopy(self.state), next=())

    def update_state(self, _config, values, *, as_node):
        assert as_node == "finish"
        self.state.update(copy.deepcopy(values))


class _FakeAdapter:
    def validate_pinned_context(self, pinned):
        return pinned.decode()


def _offline():
    when = datetime(2026, 9, 1, tzinfo=timezone.utc)
    bundle = {"run": {"run_id": RUN}, "deal": {"deal_id": "D1", "customer_id": "C1",
              "requested_delivery_date": date(2026, 9, 4)},
              "lines": [{"deal_line_id": "L1", "product_id": "P1",
                         "fulfillment_mode": "supplier_finished"}],
              "inventory": [{"inventory_id": "S1", "product_id": "P1", "location_id": "W1",
                             "quantity_on_hand": 12, "quantity_allocated": 0,
                             "snapshot_at": when}],
              "inbound_supply": [],
              "supplier_offers": [{"supplier_item_id": "O1", "supplier_id": "SUP1",
                                   "product_id": "P1", "lead_days_mode": 8,
                                   "order_calendar_json": {}}],
              "shipping_lanes": [{"lane_id": "LANE1", "origin_location_id": "W1",
                                  "destination_country_code": "EG", "destination_region": "Cairo"}],
              "facts": {"lines": [{"line_id": "L1", "fulfillment_status": "conditional",
                                    "shipping_options": [{"stock_id": "S1", "supply_ids": [],
                                                          "quantity": 12, "location": "W1",
                                                          "dispatch": date(2026, 9, 2),
                                                          "arrival": date(2026, 9, 4)}],
                                    "quantity_by_requested_date": __import__("decimal").Decimal("12")}],
                        "supply": {"stock": {"P1": [{"id": "S1", "location": "W1",
                                                      "free": 12, "fresh": True}]},
                                   "binding_receipts": {"P1": []}}}}
    raw, digest, _ = seal(bundle)
    context = RunContextV1("offline", RUN, "D1", "D1", when, "snap", "cat", "policy",
                           "config", "0" * 64, digest)
    state = {"state_version": "m1.1-original-v1", "assessment_id": "offline",
             "phase1c_run_id": str(RUN), "subject_kind": "original",
             "context": context_to_record(context), "sealed_bundle": raw,
             "tool_access_ledger": [], "review_status": "incomplete"}
    graph = _FakeGraph(state)
    scope = TrustedToolScope(context, "fulfillment", "D1", "C1", frozenset(("L1",)),
                             CATEGORIES)
    return graph, scope, bundle


class OfflineToolTests(unittest.TestCase):
    def test_mixed_path_is_unsupported_while_stock_is_visible(self):
        graph, scope, _ = _offline()
        tools = FulfillmentTools(graph, {}, _FakeAdapter(), scope)
        stock = tools.inspect_line_supply(call_id="one", line_id="L1")
        self.assertEqual(stock["evidence"], "eligible_binding")
        self.assertEqual({r["category"] for r in stock["records"]},
                         {"inventory", "supplier_offer", "shipping_lane"})
        paths = tools.inspect_fulfillment_paths(call_id="two", line_id="L1")
        self.assertEqual(paths["evidence"], "unsupported_capability")
        self.assertEqual(paths["findings"]["quantity_by_requested_date"], "12")
        self.assertFalse(paths["findings"]["confirmed_mixed_path"])
        self.assertFalse(paths["findings"]["conditional_estimates"])
        self.assertTrue(was_returned(graph, {}, "offline", scope.context.bundle_sha256,
                                     "supplier_offer", "O1", "L1"))
        detail = tools.inspect_evidence_record(call_id="three", line_id="L1",
                                               source_category="supplier_offer", source_id="O1")
        self.assertEqual(detail["evidence"], "insufficient_or_conditional")

    def test_unseen_reference_denied_and_never_citable(self):
        graph, scope, _ = _offline()
        tools = FulfillmentTools(graph, {}, _FakeAdapter(), scope)
        unseen = tools.inspect_evidence_record(call_id="unseen", line_id="L1",
                                               source_category="inventory", source_id="S1")
        self.assertEqual(unseen["execution"], "authorization_denied")
        self.assertEqual(unseen["returned_refs"], [])
        self.assertFalse(was_returned(graph, {}, "offline", scope.context.bundle_sha256,
                                      "inventory", "S1", "L1"))
        self.assertEqual(graph.state["tool_access_ledger"][0]["status"], "reserved")
        self.assertEqual(graph.state["tool_access_ledger"][1]["status"], "completed")

    def test_wrong_customer_specialist_source_and_subject_denied(self):
        for change in ({"customer_id": "OTHER"}, {"specialist": "credit"},
                       {"subject_id": "OTHER"},
                       {"source_categories": frozenset(("inventory",))}):
            with self.subTest(change=change):
                graph, scope, _ = _offline()
                from dataclasses import replace
                other = replace(scope, **change)
                result = FulfillmentTools(graph, {}, _FakeAdapter(), other).inspect_line_supply(
                    call_id="denied", line_id="L1")
                self.assertEqual(result["execution"], "authorization_denied")
                self.assertEqual(result["returned_refs"], [])
        graph, scope, _ = _offline()
        wrong_context = RunContextV1("other", RUN, "D1", "D1", scope.context.as_of_at,
                                     "snap", "cat", "policy", "config", "0" * 64,
                                     scope.context.bundle_sha256)
        from dataclasses import replace
        denied = FulfillmentTools(graph, {}, _FakeAdapter(), replace(scope, context=wrong_context))
        self.assertEqual(denied.inspect_line_supply(call_id="wrong-context", line_id="L1")
                         ["execution"], "authorization_denied")

    def test_interrupted_call_consumes_budget_without_citable_source(self):
        from dealdesk_phase2.tool_ledger import reserve

        graph, scope, _ = _offline()
        context = scope.context
        reserve(graph, {}, "offline", scope.context.bundle_sha256, "interrupted",
                "inspect_line_supply", {"line_id": "L1", "horizon": None},
                {"assessment_id": "offline", "phase1c_run_id": str(context.phase1c_run_id),
                 "subject_id": "D1", "customer_id": "C1", "bundle_sha256": context.bundle_sha256,
                 "source_input_digest": context.source_input_digest, "specialist": "fulfillment",
                 "permission_version": scope.permission_version,
                 "allowed_lines": ["L1"], "allowed_sources": sorted(CATEGORIES)})
        restarted = _FakeGraph(graph.state)
        result = FulfillmentTools(restarted, {}, _FakeAdapter(), scope).inspect_line_supply(
            call_id="interrupted", line_id="L1")
        self.assertEqual(result["execution"], "technical_failure")
        self.assertFalse(was_returned(restarted, {}, "offline", scope.context.bundle_sha256,
                                      "inventory", "S1", "L1"))
        self.assertEqual(len([x for x in restarted.state["tool_access_ledger"] if x["counted"]]), 1)

    def test_corrupt_seal_stops_without_refresh_and_malformed_source_is_failure(self):
        graph, scope, _ = _offline()
        graph.state["sealed_bundle"] += " "
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            FulfillmentTools(graph, {}, _FakeAdapter(), scope).inspect_line_supply(
                call_id="bad-digest", line_id="L1")
        graph, scope, pool = _offline()
        del pool["inventory"][0]["inventory_id"]
        raw, digest, _ = seal(pool)
        graph.state["sealed_bundle"] = raw
        context = RunContextV1("offline", RUN, "D1", "D1", scope.context.as_of_at,
                               "snap", "cat", "policy", "config", "0" * 64, digest)
        graph.state["context"] = context_to_record(context)
        from dataclasses import replace
        scope = replace(scope, context=context)
        result = FulfillmentTools(graph, {}, _FakeAdapter(), scope).inspect_line_supply(
            call_id="malformed", line_id="L1")
        self.assertEqual(result["execution"], "technical_failure")
        self.assertEqual(result["returned_refs"], [])

    def test_scope_horizon_and_idempotent_budget_survive_restart(self):
        graph, scope, _ = _offline()
        tools = FulfillmentTools(graph, {}, _FakeAdapter(), scope)
        self.assertEqual(tools.inspect_line_supply(call_id="wrong", line_id="OTHER")
                         ["execution"], "authorization_denied")
        too_far = date(2026, 9, 4).toordinal() + FORWARD_DAYS + 1
        self.assertEqual(tools.inspect_line_supply(call_id="far", line_id="L1",
                         horizon=date.fromordinal(too_far))["execution"], "authorization_denied")
        for index in range(MAX_CALLS - 2):
            tools.inspect_line_supply(call_id=f"call-{index}", line_id="L1")
        restarted = _FakeGraph(graph.state)
        restored = FulfillmentTools(restarted, {}, _FakeAdapter(), scope)
        self.assertEqual(restored.inspect_line_supply(call_id="new", line_id="L1")
                         ["execution"], "budget_exhausted")
        self.assertEqual(restored.inspect_line_supply(call_id="call-0", line_id="L1")
                         ["execution"], "completed")
        with self.assertRaises(EvidenceMismatch):
            restored.inspect_fulfillment_paths(call_id="call-0", line_id="L1")
        self.assertEqual(len([x for x in restarted.state["tool_access_ledger"] if x["counted"]]),
                         MAX_CALLS)

    def test_old_evidence_visible_and_record_cap_reports_discovery_limit(self):
        graph, scope, pool = _offline()
        pool["inventory"][0]["snapshot_at"] = datetime(2026, 8, 1, tzinfo=timezone.utc)
        for i in range(MAX_RECORDS + 1):
            pool["supplier_offers"].append(dict(pool["supplier_offers"][0],
                                                supplier_item_id=f"EXTRA-{i}"))
        raw, digest, _ = seal(pool)
        context = RunContextV1("offline", RUN, "D1", "D1", scope.context.as_of_at,
                               "snap", "cat", "policy", "config", "0" * 64, digest)
        graph.state["sealed_bundle"] = raw
        graph.state["context"] = context_to_record(context)
        graph.state["tool_access_ledger"] = []
        scope = TrustedToolScope(context, "fulfillment", "D1", "C1", frozenset(("L1",)),
                                 CATEGORIES)
        result = FulfillmentTools(graph, {}, _FakeAdapter(), scope).inspect_line_supply(
            call_id="cap", line_id="L1")
        self.assertEqual(result["evidence"], "discovery_limit")
        self.assertEqual(len(result["records"]), MAX_RECORDS)
        self.assertTrue(result["more_in_sealed_pool"])
        # Historical stock provenance is included despite the forward horizon.
        self.assertIn("inventory:S1", result["returned_refs"])

    def test_no_selected_evidence_is_explicitly_bounded(self):
        graph, scope, pool = _offline()
        pool["inventory"] = []
        pool["supplier_offers"] = []
        pool["shipping_lanes"] = []
        pool["facts"]["supply"]["stock"]["P1"] = []
        pool["facts"]["lines"][0]["shipping_options"] = []
        raw, digest, _ = seal(pool)
        graph.state["sealed_bundle"] = raw
        context = RunContextV1("offline", RUN, "D1", "D1", scope.context.as_of_at,
                               "snap", "cat", "policy", "config", "0" * 64, digest)
        graph.state["context"] = context_to_record(context)
        scope = TrustedToolScope(context, "fulfillment", "D1", "C1", frozenset(("L1",)),
                                 CATEGORIES)
        result = FulfillmentTools(graph, {}, _FakeAdapter(), scope).inspect_line_supply(
            call_id="none", line_id="L1")
        self.assertEqual(result["evidence"], "no_eligible_evidence")
        self.assertIn("selected reader pool", result["gaps"][0])

    def test_real_langgraph_checkpoint_update_preserves_budget(self):
        from dealdesk_phase2.graph_state import AssessmentStateV1

        fake, scope, _ = _offline()
        builder = StateGraph(AssessmentStateV1)
        builder.add_node("finish", lambda state: {})
        builder.add_edge(START, "finish")
        builder.add_edge("finish", END)
        saver = InMemorySaver()
        graph = builder.compile(checkpointer=saver)
        config = {"configurable": {"thread_id": "offline"}}
        graph.invoke(fake.state, config)
        session = FulfillmentTools(graph, config, _FakeAdapter(), scope)
        result = session.inspect_line_supply(call_id="a", line_id="L1")
        self.assertEqual(result["execution"], "completed")
        self.assertEqual(graph.get_state(config).next, ())
        self.assertEqual(len(graph.get_state(config).values["tool_access_ledger"]), 2)
        self.assertEqual(FulfillmentTools(graph, config, _FakeAdapter(), scope)
                         .inspect_line_supply(call_id="a", line_id="L1"), result)


@unittest.skipUnless(READY, "Requires pinned Phase 1C fixtures and disposable PostgreSQL")
class PinnedPostgresToolTests(unittest.TestCase):
    def _make(self, run, assessment):
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        saver = thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"])
        checkpointer = saver.__enter__()
        graph = build_original_graph(adapter,
                                     lambda: psycopg.connect(os.environ["DATABASE_URL"]),
                                     checkpointer)
        config = {"configurable": {"thread_id": assessment}}
        state = graph.invoke(initial_state(assessment, run), config)
        pinned = pinned_from_state(state)
        pool = adapter.validate_pinned_context(pinned)
        scope = TrustedToolScope(pinned.context, "fulfillment", pinned.context.original_deal_id,
                                 pool["deal"]["customer_id"],
                                 frozenset(x["deal_line_id"] for x in pool["lines"]), CATEGORIES)
        return saver, graph, config, adapter, pool, scope

    def test_actual_binding_and_conditional_pinned_references(self):
        for label, run in (("binding", RUN), ("offer", OFFER)):
            with self.subTest(label=label):
                saver, graph, config, adapter, pool, scope = self._make(run, "M12-" + label)
                try:
                    line = pool["lines"][0]["deal_line_id"]
                    tools = FulfillmentTools(graph, config, adapter, scope)
                    supply = tools.inspect_line_supply(call_id="stock", line_id=line)
                    paths = tools.inspect_fulfillment_paths(call_id="paths", line_id=line)
                    self.assertEqual(supply["execution"], "completed")
                    self.assertEqual(paths["execution"], "completed")
                    if label == "binding":
                        self.assertEqual(paths["findings"]["quantity_by_requested_date"], "10")
                        self.assertTrue(any(x["category"] == "inbound_supply"
                                            for x in supply["records"]))
                        self.assertTrue(paths["findings"]["binding_options"])
                    else:
                        self.assertEqual(paths["evidence"], "insufficient_or_conditional")
                        self.assertFalse(paths["findings"]["binding_options"])
                        self.assertFalse(pool["facts"]["supply"]["binding_receipts"]
                                         [pool["lines"][0]["product_id"]])
                finally:
                    saver.__exit__(None, None, None)

    def test_postgres_restart_keeps_consumed_calls_and_citation_ledger(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        assessment = "M12-restart"
        saver, graph, config, adapter, pool, scope = self._make(RUN, assessment)
        line = pool["lines"][0]["deal_line_id"]
        try:
            tools = FulfillmentTools(graph, config, adapter, scope)
            first = tools.inspect_line_supply(call_id="first", line_id=line)
            source = first["records"][0]
            for i in range(5):
                tools.inspect_line_supply(call_id=f"before-{i}", line_id=line)
        finally:
            saver.__exit__(None, None, None)
        with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as reopened:
            restored = build_original_graph(adapter,
                                            lambda: psycopg.connect(os.environ["DATABASE_URL"]),
                                            reopened)
            session = FulfillmentTools(restored, config, adapter, scope)
            self.assertTrue(was_returned(restored, config, assessment,
                                         scope.context.bundle_sha256,
                                         source["category"], source["id"], line))
            self.assertEqual(session.inspect_line_supply(call_id="first", line_id=line), first)
            for i in range(MAX_CALLS - 6):
                session.inspect_line_supply(call_id=f"after-{i}", line_id=line)
            self.assertEqual(session.inspect_line_supply(call_id="excess", line_id=line)
                             ["execution"], "budget_exhausted")
            self.assertEqual(len([x for x in restored.get_state(config).values["tool_access_ledger"]
                                  if x["counted"]]), MAX_CALLS)


if __name__ == "__main__":
    unittest.main()
