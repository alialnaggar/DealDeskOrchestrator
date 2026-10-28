"""Original-only six-responsibility offline handoff; no hosted provider path.

The authoritative original graph owns fixed results and the PostgreSQL
checkpoint. This small LangGraph composes the existing bounded investigation
graphs without copying rules, sending inference or opening a candidate route.
"""

from typing import TypedDict
from uuid import UUID

from langgraph.graph import END, START, StateGraph

from .fulfillment_agent import OfflineModelDouble
from .graph_state import SPECIALISTS, pinned_from_state
from .investigation_graph import run_original_then_investigate
from .m20_specialists import TOOLS as M20_TOOLS, run_m20_offline
from .m21_specialists import TOOLS as M21_TOOLS, run_m21_offline
from .phase1c_adapter import EvidenceMismatch


class Week3State(TypedDict, total=False):
    current: str


def build_week3_offline_graph(original, config, adapter, fulfillment_model,
                              m20_models, m21_models, *, assessment_id: str,
                              run_id: UUID):
    """Wire existing graphs in prerequisite order, with offline-only models."""
    if (type(fulfillment_model) is not OfflineModelDouble
            or set(m20_models) != set(M20_TOOLS)
            or any(getattr(m, "provider", None) != "offline_double"
                   or getattr(m, "offline_only", None) is not True for m in m20_models.values())
            or set(m21_models) != set(M21_TOOLS)
            or any(getattr(m, "provider", None) != "offline_double"
                   or getattr(m, "offline_only", None) is not True for m in m21_models.values())):
        raise ValueError("Week 3 integration accepts offline model doubles only")
    if (not isinstance(assessment_id, str) or not assessment_id
            or not isinstance(run_id, UUID)
            or config.get("configurable", {}).get("thread_id") != assessment_id):
        raise ValueError("Week 3 original assessment identity required")

    builder = StateGraph(Week3State)

    def original_and_fulfillment(_):
        state = run_original_then_investigate(original, config, adapter, fulfillment_model,
            assessment_id=assessment_id, run_id=run_id)
        if (state.get("stop_reason") or set(state.get("specialist_results", {})) != set(SPECIALISTS)
                or state.get("candidate_status") != "not_started"
                or (state.get("ai_fulfillment_result", {}).get("contribution") or {}).get(
                    "kind") == "binding_proposal"):
            raise EvidenceMismatch("Week 3 original-only scope or fixed prerequisites changed")
        return {"current": "original_and_fulfillment"}

    def configuration_pricing(_):
        run_m20_offline(original, config, adapter, m20_models)
        return {"current": "configuration_pricing"}

    def credit_policy_routing(_):
        run_m21_offline(original, config, adapter, m21_models)
        return {"current": "credit_policy_routing"}

    def handoff(_):
        state = original.get_state(config).values
        pinned = pinned_from_state(state)
        adapter.validate_pinned_context(pinned)
        if (pinned.context.assessment_id != assessment_id
                or pinned.context.phase1c_run_id != run_id
                or state.get("candidate_status") != "not_started"
                or state.get("review_status") in (None, "pending", "incomplete")
                or not state.get("ai_fulfillment_result")
                or set(state.get("m20_ai_results", {})) != set(M20_TOOLS)
                or set(state.get("m21_ai_results", {})) != set(M21_TOOLS)
                or not {"m20_ai", "m21_ai"}.issubset(state.get("reviewer_package", {}))):
            raise EvidenceMismatch("Week 3 original-only handoff incomplete")
        return {"current": "handoff"}

    for name, node in (("original_and_fulfillment", original_and_fulfillment),
                       ("configuration_pricing", configuration_pricing),
                       ("credit_policy_routing", credit_policy_routing),
                       ("handoff", handoff)):
        builder.add_node(name, node)
    builder.add_edge(START, "original_and_fulfillment")
    builder.add_edge("original_and_fulfillment", "configuration_pricing")
    builder.add_edge("configuration_pricing", "credit_policy_routing")
    builder.add_edge("credit_policy_routing", "handoff")
    builder.add_edge("handoff", END)
    return builder.compile()


def run_week3_offline(original, config, adapter, fulfillment_model, m20_models,
                      m21_models, *, assessment_id: str, run_id: UUID):
    build_week3_offline_graph(original, config, adapter, fulfillment_model,
        m20_models, m21_models, assessment_id=assessment_id, run_id=run_id).invoke(
            {"current": "start"})
    return original.get_state(config).values
