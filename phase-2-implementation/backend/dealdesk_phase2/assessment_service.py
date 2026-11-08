"""Explicitly offline, scripted synthetic assessment; no hosted transport imports."""

from pathlib import Path
from uuid import UUID

import psycopg

from .assessment_store import AssessmentStore, Conflict
from .candidate_graph import original_only_package
from .checkpoint import thesis_checkpointer
from .demo_fixture_contract import verify_demo_fixture
from .fulfillment_agent import OfflineModelDouble
from .graph_state import SPECIALISTS, pinned_from_state
from .investigation_graph import run_original_investigate_and_review
from .m20_specialists import run_m20_offline
from .m21_specialists import checked_candidate_context, run_m21_offline
from .orchestrator import build_original_graph, initial_state
from .phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from .recommendation_review import project_source_grounded_review


SCENARIOS = {
    "B01/RC01": (UUID("00000000-0000-4000-8000-000000018001"), "M18-D-B01"),
    "N01/UC02": (UUID("00000000-0000-4000-8000-000000018101"), "M18-D-N01"),
}


class _OfflineSourceModel:
    """Deterministic inspection/citation script; source values come from tool returns."""
    provider = "offline_double"
    model = "demo-source-script-v1"
    offline_only = True

    def __init__(self, specialist):
        self.specialist = specialist

    def next_action(self, input, observations):
        if not observations:
            if self.specialist in ("configuration", "pricing"):
                return {"kind": "inspect", "tool": input["permitted_tool"],
                        "line_id": input["line_ids"][0]}
            return {"kind": "inspect", "tool": input["permitted_tool"],
                    "subject_id": input["subject_id"]}
        rows = observations[0]["records"]
        if self.specialist == "credit" and not rows:
            return {"kind": "abstain", "reason_code": "insufficient_evidence"}
        field = {"configuration": "is_sellable", "pricing": "fixed_margin_pct",
                 "credit": "credit_status", "policy": "rule_id",
                 "approval_routing": "route_withheld"}[self.specialist]
        row = next((row for row in rows if field in row["fields"]), None)
        if row is None:
            return ({"kind": "abstain", "reason_code": "insufficient_evidence"} if
                self.specialist not in ("configuration", "pricing") else
                {"kind": "abstain", "reason_code": "insufficient_evidence",
                 "uncertainty_reasons": []})
        result = {"kind": "finding", "claims": [{"ref": row["ref"], "field": field,
            "value": row["fields"][field]}]}
        if self.specialist in ("configuration", "pricing"):
            result["uncertainty_reasons"] = []
        return result


def _fulfillment(scenario):
    if scenario == "B01/RC01":
        return OfflineModelDouble((
            {"type": "tool", "tool": "inspect_fulfillment_paths",
             "arguments": {"line_id": "M18-L-B01"}},
            {"type": "contribution", "value": {"schema_version": "3",
             "kind": "binding_proposal", "payload": {
                "line_id": "M18-L-B01", "tradeoff_code":
                    "partial_delivery_requires_customer_acceptance",
                "delivery_slices": [
                    {"quantity": "8", "delivery_date": "2026-09-03",
                     "source_refs": ["inventory:M18-INV-B01"]},
                    {"quantity": "2", "delivery_date": "2026-09-08",
                     "source_refs": ["inbound_supply:M18-IN-B01",
                                     "inventory:M18-INV-B01"]}]}}}))
    return OfflineModelDouble(({"type": "contribution", "value": {
        "kind": "abstention", "payload": {"reason": "No verified partial option",
            "uncertainty_reasons": ["Customer terms prohibit partial delivery"]}}},))


class AssessmentService:
    def __init__(self, business_dsn, checkpoint_dsn, phase1c_checkout: Path):
        self.business_dsn = business_dsn
        self.checkpoint_dsn = checkpoint_dsn
        self.adapter = Phase1CAdapter(phase1c_checkout)
        self.store = AssessmentStore(checkpoint_dsn)

    def _connect_business(self):
        # The API holds no write-capable business connection, including during
        # Phase 1C candidate verification and review-time source rechecks.
        return psycopg.connect(self.business_dsn,
                               options="-c default_transaction_read_only=on")

    def create(self, owner, key, scenario, schedule):
        if scenario not in SCENARIOS:
            raise ValueError("Unsupported synthetic scenario")
        run_id, deal_id = SCENARIOS[scenario]
        assessment_id, fresh = self.store.create(owner, key, scenario, run_id, deal_id)
        if fresh:
            try:
                schedule(assessment_id)
            except Exception:
                self.store.mark_unscheduled(assessment_id)
                raise
        return assessment_id, fresh

    def _graph(self, saver):
        return build_original_graph(self.adapter, self._connect_business, saver)

    def run(self, assessment_id):
        if not self.store.claim(assessment_id):
            return
        try:
            row = self.store.get_ownerless_for_worker(assessment_id)
            scenario = row["scenario"]
            if scenario not in SCENARIOS or row["run_id"] != SCENARIOS[scenario][0]:
                raise EvidenceMismatch("Worker scenario identity differs")
            config = {"configurable": {"thread_id": assessment_id}}
            with thesis_checkpointer(self.checkpoint_dsn) as saver:
                graph = self._graph(saver)
                if graph.get_state(config).values:
                    raise EvidenceMismatch("Fresh assessment checkpoint already exists")
                state = graph.invoke(initial_state(assessment_id, row["run_id"]), config)
                pinned = pinned_from_state(state)
                pool = self.adapter.validate_pinned_context(pinned)
                if (pinned.context.original_deal_id != row["source_deal_id"] or
                        state.get("stop_reason")):
                    raise EvidenceMismatch("Synthetic source preflight failed")
                verify_demo_fixture(pool, state["specialist_results"]["credit"], scenario)
                self.store.record(assessment_id, "preflight_ok", "original", source=(
                    pinned.context.bundle_sha256, pinned.context.source_input_digest))
                self.store.record(assessment_id, "checkpoint", "original")
                for name in SPECIALISTS:
                    if state["specialist_results"][name]["execution"] != "completed":
                        raise EvidenceMismatch("Fixed specialist incomplete")
                    self.store.record(assessment_id, "fixed_completed", name)
                m20 = {name: _OfflineSourceModel(name) for name in ("configuration", "pricing")}
                state = run_m20_offline(graph, config, self.adapter, m20)
                self.store.record(assessment_id, "checkpoint", "pricing")
                for name in m20:
                    if state["m20_ai_results"][name]["execution"] not in ("completed", "abstained"):
                        raise EvidenceMismatch("Offline original specialist failed")
                    self.store.record(assessment_id, "ai_completed", name)
                state = run_original_investigate_and_review(graph, config, self.adapter,
                    _fulfillment(scenario), assessment_id=assessment_id, run_id=row["run_id"])
                self.store.record(assessment_id, "checkpoint", "fulfillment")
                if state["ai_fulfillment_result"]["execution"] not in ("completed", "abstained"):
                    raise EvidenceMismatch("Offline fulfillment failed")
                self.store.record(assessment_id, "ai_completed", "fulfillment")
                if state["candidate_status"] == "fixed_checked":
                    self.store.record(assessment_id, "checkpoint", "candidate")
                m21 = {name: _OfflineSourceModel(name) for name in (
                    "credit", "policy", "approval_routing")}
                state = run_m21_offline(graph, config, self.adapter, m21,
                    candidate_context=(checked_candidate_context(state) if
                        state["candidate_status"] == "fixed_checked" else None))
                if state["candidate_status"] == "not_started":
                    # Offline original-only handoff may retain the pre-investigation
                    # package summary; refresh only from the same stored state.
                    package = original_only_package(state)
                    package["m21_ai"] = state["reviewer_package"]["m21_ai"]
                    graph.update_state(config, {"reviewer_package": package}, as_node="finish")
                    state = graph.get_state(config).values
                self.store.record(assessment_id, "checkpoint", "approval_routing")
                for name in m21:
                    if state["m21_ai_results"][name]["execution"] not in ("completed", "abstained"):
                        raise EvidenceMismatch("Offline original specialist failed")
                    self.store.record(assessment_id, "ai_completed", name)
                snapshot = graph.get_state(config)
                project_source_grounded_review(snapshot.values, self.adapter,
                    checkpoint_pending=bool(snapshot.next))
                self.store.record(assessment_id, "review_ready", "review", status="completed")
        except Exception:
            # No replay on worker exceptions. No exception details or raw evidence in events.
            try:
                self.store.record(assessment_id, "stopped", status="stopped")
            except EvidenceMismatch:
                pass  # A restarted process may already have marked this run uncertain.
            raise

    def review(self, owner, assessment_id):
        row = self.store.get(owner, assessment_id)
        if row["status"] != "completed" or not row["bundle_sha256"]:
            raise Conflict("Review not available")
        config = {"configurable": {"thread_id": assessment_id}}
        with thesis_checkpointer(self.checkpoint_dsn) as saver:
            graph = self._graph(saver)
            snapshot = graph.get_state(config)
            if not snapshot.values or snapshot.next:
                raise EvidenceMismatch("Completed review checkpoint missing or pending")
            pinned = pinned_from_state(snapshot.values)
            if (pinned.context.assessment_id != assessment_id or
                    pinned.context.phase1c_run_id != row["run_id"] or
                    pinned.context.original_deal_id != row["source_deal_id"] or
                    pinned.context.bundle_sha256 != row["bundle_sha256"] or
                    pinned.context.source_input_digest != row["source_input_digest"]):
                raise EvidenceMismatch("Registry and checkpoint identity differ")
            fresh = self.adapter.read_original(self._connect_business, row["run_id"], assessment_id)
            if (fresh.context.bundle_sha256 != pinned.context.bundle_sha256 or
                    fresh.context.source_input_digest != pinned.context.source_input_digest):
                raise EvidenceMismatch("Business evidence changed since pin")
            verify_demo_fixture(self.adapter.validate_pinned_context(pinned),
                snapshot.values["specialist_results"]["credit"], row["scenario"])
            return project_source_grounded_review(snapshot.values, self.adapter,
                checkpoint_pending=bool(snapshot.next))
