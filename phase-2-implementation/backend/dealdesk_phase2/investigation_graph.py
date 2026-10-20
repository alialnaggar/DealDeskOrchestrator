"""M1.3 conditional LangGraph investigation after the fixed original graph.

The original graph/checkpoint is authoritative. This short-lived private
LangGraph controls the offline model/tool sequence; M1.2 persists every tool
reservation and returned source in the original PostgreSQL checkpoint.
"""

from datetime import date
from hashlib import sha256
from typing import TypedDict
from uuid import UUID

from langgraph.graph import START, END, StateGraph

from .fulfillment_agent import (InvestigationModel, eligible_line, restricted_input,
                                runtime_envelope, validate_contribution)
from .graph_state import pinned_from_state
from .fulfillment_tools import FulfillmentTools
from .phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from .tool_ledger import entries
from .tool_permissions import MAX_CALLS, TrustedToolScope


SOURCE_CATEGORIES = frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane"))


class PrivateInvestigationState(TypedDict, total=False):
    status: str
    reason: str | None
    input: object
    observations: list[dict]
    action: dict
    outcome: dict
    claim_audit: list[dict]


def _tool_call(tools: FulfillmentTools, name: str, call_id: str, args: dict) -> dict:
    if not isinstance(args, dict) or set(args) - {"line_id", "horizon", "source_category", "source_id"}:
        raise ValueError("Malformed tool arguments")
    if not isinstance(args.get("line_id"), str):
        raise ValueError("Line ID required")
    if name in ("inspect_line_supply", "inspect_fulfillment_paths"):
        if set(args) - {"line_id", "horizon"}:
            raise ValueError("Unexpected tool parameter")
        horizon = args.get("horizon")
        if horizon is not None:
            if not isinstance(horizon, str):
                raise ValueError("Horizon must be an ISO date")
            horizon = date.fromisoformat(horizon)
        return getattr(tools, name)(call_id=call_id, line_id=args["line_id"], horizon=horizon)
    if name == "inspect_evidence_record" and set(args) == {"line_id", "source_category", "source_id"}:
        if not all(isinstance(args[key], str) for key in args):
            raise ValueError("Source key fields must be strings")
        return tools.inspect_evidence_record(call_id=call_id, **args)
    raise ValueError("Tool is not authorized or arguments are malformed")


def build_investigation_graph(original_graph, config: dict, adapter: Phase1CAdapter,
                              model: InvestigationModel):
    """Private, bounded sequence; durable identity/ledger lives in original graph."""
    builder = StateGraph(PrivateInvestigationState)

    def gate(state):
        original = original_graph.get_state(config).values
        try:
            pinned = pinned_from_state(original)
            pool = adapter.validate_pinned_context(pinned)
            selected, reason = eligible_line(original, pool)
            if selected is None:
                return {"status": "skipped", "reason": reason}
            ledger = entries(original_graph, config, pinned.context.assessment_id,
                             pinned.context.bundle_sha256)
            used = sum(bool(x.get("counted")) for x in ledger)
            input = restricted_input(pinned.context, pool, selected, MAX_CALLS - used)
            if used >= MAX_CALLS:
                return {"status": "error", "reason": "budget_exhausted", "input": input}
            return {"status": "eligible", "input": input, "observations": []}
        except Exception as exc:
            return {"status": "error", "reason": "evidence_identity:" + type(exc).__name__}

    def decide(state):
        try:
            action = model.next_action(state["input"], tuple(state["observations"]))
            if not isinstance(action, dict) or action.get("type") not in ("tool", "contribution"):
                raise ValueError("Malformed model action")
            if action["type"] == "tool":
                if len(state["observations"]) >= MAX_CALLS:
                    return {"status": "error", "reason": "budget_exhausted"}
                if (set(action) != {"type", "tool", "arguments"}
                        or action["tool"] not in state["input"].permitted_tools
                        or not isinstance(action["arguments"], dict)):
                    raise ValueError("Unauthorized or malformed model tool request")
            elif set(action) != {"type", "value"}:
                raise ValueError("Malformed contribution action")
            return {"action": action, "status": "tool_pending" if action["type"] == "tool"
                    else "contribution_pending"}
        except Exception as exc:
            return {"status": "error", "reason": "model_output:" + type(exc).__name__}

    def tool(state):
        input = state["input"]
        try:
            pinned = pinned_from_state(original_graph.get_state(config).values)
            pool = adapter.validate_pinned_context(pinned)
            if (input.assessment_id != pinned.context.assessment_id or
                    input.bundle_sha256 != pinned.context.bundle_sha256 or
                    input.subject_id != pinned.context.original_deal_id or
                    input.source_input_digest != pinned.context.source_input_digest):
                raise EvidenceMismatch("Investigation input changed context")
            scope = TrustedToolScope(pinned.context, "fulfillment", input.subject_id,
                                     pool["deal"]["customer_id"], frozenset((input.line_id,)),
                                     SOURCE_CATEGORIES)
            facade = FulfillmentTools(original_graph, config, adapter, scope)
            action = state["action"]
            call_id = sha256(f"{input.assessment_id}:fulfillment:{len(state['observations'])}"
                             .encode("utf-8")).hexdigest()
            result = _tool_call(facade, action["tool"], call_id, action["arguments"])
            if result["execution"] != "completed":
                return {"status": "error", "reason": "tool:" + result["execution"],
                        "observations": [*state["observations"], result]}
            return {"status": "eligible", "observations": [*state["observations"], result]}
        except Exception as exc:
            return {"status": "error", "reason": "tool:" + type(exc).__name__}

    def finalize(state):
        if state["status"] == "skipped":
            return {"outcome": {"execution": "skipped", "reason": state["reason"]}}
        input = state.get("input")
        if input is None:
            return {"outcome": {"execution": "error", "error": state.get("reason")}}
        if state["status"] == "error":
            return {"outcome": runtime_envelope(input, execution="error", error=state["reason"])}
        try:
            contribution = validate_contribution(state["action"]["value"], input,
                                                 original_graph, config)
            audit = contribution.pop("claim_audit", {})
            return {"outcome": runtime_envelope(input, execution="completed",
                                                 contribution=contribution),
                    "claim_audit": [{"original_claim": item["original_claim"],
                                     "reason": item["reason"],
                                     "claim_index": item["claim_index"],
                                     "assessment_id": input.assessment_id,
                                     "bundle_sha256": input.bundle_sha256}
                                    for item in audit.get("rejected_claims", [])]
                                   + ([{"raw_model_notes": audit["raw_model_notes"],
                                        "reason": "audit_only_model_notes",
                                        "assessment_id": input.assessment_id,
                                        "bundle_sha256": input.bundle_sha256}]
                                      if audit.get("raw_model_notes") else [])}
        except Exception as exc:
            reason = ("unsupported_citation" if isinstance(exc, EvidenceMismatch)
                      and "not returned" in str(exc) else
                      "identity_mismatch" if isinstance(exc, EvidenceMismatch)
                      else "malformed_contribution")
            # The source content is retained only in the checkpointed audit,
            # never in the reviewer-facing business contribution.
            return {"outcome": runtime_envelope(input, execution="error", error=reason),
                    "claim_audit": [{"original_content": state["action"].get("value"),
                                     "reason": reason, "detail": str(exc),
                                     "assessment_id": input.assessment_id,
                                     "bundle_sha256": input.bundle_sha256}]}

    def from_gate(state):
        return "decide" if state["status"] == "eligible" else "finalize"

    def from_decide(state):
        return "tool" if state["status"] == "tool_pending" else "finalize"

    def after_tool(state):
        return "decide" if state["status"] == "eligible" else "finalize"

    builder.add_node("eligibility", gate)
    builder.add_node("model_decision", decide)
    builder.add_node("authorized_tool", tool)
    builder.add_node("validate_contribution", finalize)
    builder.add_edge(START, "eligibility")
    builder.add_conditional_edges("eligibility", from_gate,
                                  {"decide": "model_decision", "finalize": "validate_contribution"})
    builder.add_conditional_edges("model_decision", from_decide,
                                  {"tool": "authorized_tool", "finalize": "validate_contribution"})
    builder.add_conditional_edges("authorized_tool", after_tool,
                                  {"decide": "model_decision", "finalize": "validate_contribution"})
    builder.add_edge("validate_contribution", END)
    return builder.compile()


def run_original_then_investigate(original_graph, config: dict, adapter: Phase1CAdapter,
                                  model: InvestigationModel, *, assessment_id: str,
                                  run_id: UUID) -> dict:
    """Complete fixed graph once, then conditionally run the private graph.

    A crash before the final update leaves fixed findings intact. On restart,
    the private graph replays from its gate; M1.2 call IDs/results and budget
    are already checkpointed in the original state.
    """
    snapshot = original_graph.get_state(config)
    if not snapshot.values:
        from .orchestrator import initial_state
        original_graph.invoke(initial_state(assessment_id, run_id), config)
    elif snapshot.next:
        original_graph.invoke(None, config)
    state = original_graph.get_state(config).values
    if (state.get("assessment_id") != assessment_id or
            state.get("phase1c_run_id") != str(run_id)):
        raise EvidenceMismatch("Restart assessment identity differs")
    if state.get("investigation_status") in ("completed", "skipped", "error"):
        return state
    private = build_investigation_graph(original_graph, config, adapter, model)
    private_result = private.invoke({"status": "pending", "observations": []},
                                    {"recursion_limit": 2 * MAX_CALLS + 7})
    result = private_result["outcome"]
    fresh = original_graph.get_state(config).values
    if (fresh.get("assessment_id") != assessment_id or
            fresh.get("context", {}).get("bundle_sha256") !=
            state.get("context", {}).get("bundle_sha256")):
        raise EvidenceMismatch("Original assessment changed during investigation")
    original_graph.update_state(config, {"ai_fulfillment_result": result,
                                         "ai_claim_audit": [*fresh.get("ai_claim_audit", []),
                                                            *private_result.get("claim_audit", [])],
                                         "investigation_status": result["execution"],
                                         "trace": [*fresh["trace"],
                                                   "fulfillment_ai:" + result["execution"]]},
                                as_node="finish")
    return original_graph.get_state(config).values
