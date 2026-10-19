"""Sequential LangGraph foundation for the original deterministic assessment."""

from uuid import UUID

from langgraph.graph import END, START, StateGraph

from .evidence_bundle import seal, unseal
from .fixed_specialists import domain_result
from .graph_state import (AssessmentStateV1, STATE_VERSION, SPECIALISTS,
                          context_to_record, pinned_from_state, validate_result)
from .phase1c_adapter import EvidenceMismatch, Phase1CAdapter


def initial_state(assessment_id: str, run_id: UUID) -> AssessmentStateV1:
    if not assessment_id:
        raise ValueError("Assessment ID required")
    return {"state_version": STATE_VERSION, "assessment_id": assessment_id,
            "phase1c_run_id": str(run_id), "subject_kind": "original",
            "specialist_results": {}, "trace": [], "stop_reason": None,
            "review_status": "pending"}


def _decision(state: AssessmentStateV1) -> dict:
    pinned = pinned_from_state(state)
    decision = unseal(state["fixed_decision"], state["fixed_decision_sha256"])
    if (str(decision["run_id"]) != str(pinned.context.phase1c_run_id)
            or str(decision["deal_id"]) != pinned.context.original_deal_id
            or decision["as_of_at"] != pinned.context.as_of_at
            or decision["policy_set_code"] != pinned.context.policy_set_code
            or decision["catalog_version"] != pinned.context.catalog_version):
        raise EvidenceMismatch("Fixed decision identity differs from sealed evidence")
    return decision


def build_original_graph(adapter: Phase1CAdapter, connection_factory, checkpointer,
                         *, interrupt_after=()):
    """Build one synchronous, original-only graph; no business write operations."""
    builder = StateGraph(AssessmentStateV1)

    def pin_evidence(state):
        if (state.get("state_version") != STATE_VERSION or state.get("subject_kind") != "original"
                or state.get("specialist_results") or state.get("sealed_bundle")):
            raise EvidenceMismatch("Invalid original assessment start")
        try:
            pinned = adapter.read_original(connection_factory, UUID(state["phase1c_run_id"]),
                                           state["assessment_id"])
        except Exception as exc:
            return {"stop_reason": "evidence_read:" + type(exc).__name__,
                    "review_status": "incomplete",
                    "trace": ["evidence_read_failed:" + type(exc).__name__]}
        return {"context": context_to_record(pinned.context), "sealed_bundle": pinned.serialized,
                "trace": ["evidence_pinned"]}

    def specialist(name):
        def run(state):
            try:
                pinned = pinned_from_state(state)
                adapter.validate_pinned_context(pinned)
                updates = {}
                if name == "configuration":
                    decision = adapter.fixed_original_decision(pinned)
                    raw, digest, _ = seal(decision)
                    updates = {"fixed_decision": raw, "fixed_decision_sha256": digest}
                else:
                    decision = _decision(state)
                prior = state["specialist_results"]
                result = domain_result(name, pinned, decision, state["assessment_id"], prior)
                validate_result(result, state, name)
                updates["specialist_results"] = {**prior, name: result}
                updates["trace"] = [*state["trace"], name + ":" + result["execution"]]
                return updates
            except Exception as exc:
                reason = name + ":" + type(exc).__name__
                return {"stop_reason": reason, "review_status": "incomplete",
                        "trace": [*state["trace"], reason]}
        return run

    def reconcile(state):
        adapter.validate_pinned_context(pinned_from_state(state))
        decision = _decision(state)
        results = state["specialist_results"]
        if any(key not in results for key in SPECIALISTS[:-1]):
            raise ValueError("Required specialist result missing")
        status = decision["status"]
        if any(result["execution"] != "completed" for result in results.values()):
            status = "incomplete"
        return {"review_status": status, "trace": [*state["trace"], "reconciled"]}

    def routing(state):
        pinned = pinned_from_state(state)
        adapter.validate_pinned_context(pinned)
        decision = _decision(state)
        prior = state["specialist_results"]
        result = domain_result("approval_routing", pinned, decision, state["assessment_id"], prior)
        if state["review_status"] != "approval_required":
            result["payload"]["route_withheld"] = True
            result["payload"]["roles_available_from_fixed_interface"] = False
            result["finding"] = "withheld"
        validate_result(result, state, "approval_routing")
        return {"specialist_results": {**prior, "approval_routing": result},
                "trace": [*state["trace"], "approval_routing:" + result["execution"]]}

    def finish(state):
        return {"trace": [*state["trace"],
                          "assessment_stopped" if state.get("stop_reason") else "review_prepared"]}

    def next_or_stop(state):
        return "finish" if state.get("stop_reason") else "continue"

    builder.add_node("pin_evidence", pin_evidence)
    for name in SPECIALISTS[:-1]:
        builder.add_node(name, specialist(name))
    builder.add_node("reconcile", reconcile)
    builder.add_node("approval_routing", routing)
    builder.add_node("finish", finish)
    builder.add_edge(START, "pin_evidence")
    names = ("pin_evidence", *SPECIALISTS[:-1], "reconcile", "approval_routing", "finish")
    for left, right in zip(names, names[1:]):
        if left == "finish":
            continue
        builder.add_conditional_edges(left, next_or_stop,
                                      {"finish": "finish", "continue": right})
    builder.add_edge("finish", END)
    return builder.compile(checkpointer=checkpointer, interrupt_after=list(interrupt_after))
