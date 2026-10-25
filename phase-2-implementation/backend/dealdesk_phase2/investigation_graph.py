"""M1.3 conditional LangGraph investigation after the fixed original graph.

The original graph/checkpoint is authoritative. This short-lived private
LangGraph controls the offline model/tool sequence; M1.2 persists every tool
reservation and returned source in the original PostgreSQL checkpoint.
"""

from datetime import date
from hashlib import sha256
import json
from typing import TypedDict
from uuid import UUID

from langgraph.graph import START, END, StateGraph

from .fulfillment_agent import (InvestigationModel, eligible_line, restricted_input,
                                 runtime_envelope, validate_contribution)
from .fulfillment_correction import CORRECTION_VERSION, classify, feedback
from .graph_state import pinned_from_state
from .fulfillment_tools import FulfillmentTools
from .phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from .tool_ledger import entries
from .tool_permissions import MAX_CALLS, TrustedToolScope
from .live_models import MAX_MODEL_TURNS


SOURCE_CATEGORIES = frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane"))


class PrivateInvestigationState(TypedDict, total=False):
    status: str
    reason: str | None
    input: object
    observations: list[dict]
    action: dict
    outcome: dict
    claim_audit: list[dict]
    model_turns: int
    raw_contribution: dict


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
            if state.get("model_turns", 0) >= MAX_MODEL_TURNS:
                return {"status": "error", "reason": "model_turn_budget_exhausted"}
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
            return {"action": action, "model_turns": state.get("model_turns", 0) + 1,
                    "status": "tool_pending" if action["type"] == "tool"
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
                    "raw_contribution": state["action"]["value"],
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
                    "raw_contribution": state["action"].get("value"),
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


def _correction_input(graph, config, adapter, state):
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    selected, reason = eligible_line(state, pool)
    if selected is None:
        raise EvidenceMismatch("Correction eligibility changed: " + reason)
    used = sum(bool(x.get("counted")) for x in state.get("tool_access_ledger", []))
    return restricted_input(pinned.context, pool, selected, MAX_CALLS - used)


def _correction_identity(input, model):
    return {"assessment_id": input.assessment_id, "phase1c_run_id": input.phase1c_run_id,
            "subject_id": input.subject_id, "line_id": input.line_id,
            "bundle_sha256": input.bundle_sha256,
            "source_input_digest": input.source_input_digest,
            "provider": getattr(model, "provider", "offline_double"),
            "model": getattr(model, "model", type(model).__name__)}


def _correction_observations(state, input):
    observations, refs = [], []
    for event in state.get("tool_access_ledger", []):
        if event.get("status") != "completed":
            continue
        identity = event.get("identity", {})
        if (identity.get("assessment_id") != input.assessment_id
                or identity.get("phase1c_run_id") != input.phase1c_run_id
                or identity.get("subject_id") != input.subject_id
                or identity.get("bundle_sha256") != input.bundle_sha256
                or identity.get("source_input_digest") != input.source_input_digest
                or identity.get("specialist") != "fulfillment"):
            raise EvidenceMismatch("Correction tool observation identity differs")
        if event.get("args", {}).get("line_id") != input.line_id:
            continue
        observations.append(event["result"])
        refs.extend(event.get("returned_refs", []))
    return tuple(observations), refs


def _checkpoint(graph, config, correction, **updates):
    graph.update_state(config, {"fulfillment_correction": correction, **updates}, as_node="finish")


def _correct(graph, config, adapter, connection_factory, model, first):
    """Resume a single revision. A reserved but unsaved response is uncertain/terminal."""
    state = graph.get_state(config).values
    correction = state["fulfillment_correction"]
    input = _correction_input(graph, config, adapter, state)
    if correction["identity"] != _correction_identity(input, model):
        raise EvidenceMismatch("Correction restart model or source identity changed")
    if correction["status"] == "reserved":
        # The provider may have received the request. Never send it again.
        correction = {**correction, "status": "uncertain_terminal"}
        _checkpoint(graph, config, correction)
        return runtime_envelope(input, execution="error", error="correction_outcome_uncertain")
    if correction["status"] == "eligible":
        remaining = MAX_MODEL_TURNS - correction["attempts"][0]["model_turns"]
        if remaining < 1 or correction["feedback"]["remaining_model_turns"] != remaining:
            raise EvidenceMismatch("Correction turn budget differs from checkpoint")
        identity = correction["identity"]
        revision_id = sha256((identity["assessment_id"] + ":" + identity["bundle_sha256"] +
                              ":" + identity["provider"] + ":" + identity["model"] +
                              ":correction-v1:final").encode()).hexdigest()
        correction = {**correction, "status": "reserved", "attempts": [
            *correction["attempts"], {"ordinal": 2, "status": "reserved",
                                       "attempt_id": revision_id}]}
        _checkpoint(graph, config, correction)
        # Same sealed pool; no new tool calls. Only completed first-attempt
        # observations in the original checkpoint are passed to the model.
        state = graph.get_state(config).values
        observations, _ = _correction_observations(state, input)
        try:
            action = model.revise(input, observations, correction["feedback"], first["raw"])
            if (not isinstance(action, dict) or set(action) != {"type", "value"}
                    or action["type"] != "contribution"):
                raise ValueError("Revision must be a contribution, never a tool call")
            if len(json.dumps(action["value"]).encode("utf-8")) > 16384:
                raise ValueError("Revision exceeds bounded raw audit")
            correction = {**correction, "status": "response_saved", "attempts": [
                correction["attempts"][0], {**correction["attempts"][1],
                                              "status": "response_saved", "raw": action["value"]}]}
            _checkpoint(graph, config, correction)
        except Exception as exc:
            correction = {**correction, "status": "terminal", "attempts": [
                correction["attempts"][0], {**correction["attempts"][1],
                                              "status": "error", "error_type": type(exc).__name__}]}
            _checkpoint(graph, config, correction)
            return runtime_envelope(input, execution="error", error="revision_failed")
    raw = correction["attempts"][1]["raw"]
    try:
        revised = validate_contribution(raw, input, graph, config)
        if revised.get("schema_version") != "3" or revised.get("kind") != "binding_proposal":
            raise ValueError("Revision did not contain a V3 binding proposal")
        correction = {**correction, "status": "completed", "attempts": [
            correction["attempts"][0], {**correction["attempts"][1],
                                        "status": "validated_unverified"}]}
        _checkpoint(graph, config, correction)
        return runtime_envelope(input, execution="completed", contribution=revised)
    except Exception as exc:
        correction = {**correction, "status": "terminal", "attempts": [
            correction["attempts"][0], {**correction["attempts"][1],
                                        "status": "rejected", "error_type": type(exc).__name__}]}
        _checkpoint(graph, config, correction)
        return runtime_envelope(input, execution="error", error="revised_contribution_rejected")


def run_original_then_investigate(original_graph, config: dict, adapter: Phase1CAdapter,
                                   model: InvestigationModel, *, assessment_id: str,
                                   run_id: UUID, connection_factory=None) -> dict:
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
    correction = state.get("fulfillment_correction") or {}
    if correction:
        first = correction["attempts"][0]
        result = first["result"]
    else:
        private = build_investigation_graph(original_graph, config, adapter, model)
        private_result = private.invoke({"status": "pending", "observations": [],
                                         "model_turns": 0},
                                        {"recursion_limit": 2 * MAX_CALLS + 7})
        result = private_result["outcome"]
        raw = private_result.get("raw_contribution")
        audit = private_result.get("claim_audit", [])
        # A bounded output is needed for durable raw-attempt audit. Oversize or
        # unserializable model material is not eligible for correction.
        try:
            bounded = raw is not None and len(json.dumps(raw).encode()) <= 16384
        except (TypeError, ValueError):
            bounded = False
        if bounded and result["execution"] in ("completed", "error"):
            first = {"ordinal": 1, "status": result["execution"], "raw": raw,
                     "result": result, "model_turns": private_result.get("model_turns", 0)}
            correction = {"version": CORRECTION_VERSION, "status": "classifying",
                          "identity": _correction_identity(
                              _correction_input(original_graph, config, adapter,
                                                original_graph.get_state(config).values), model),
                          "attempts": [first]}
            _checkpoint(original_graph, config, correction,
                        ai_claim_audit=[*original_graph.get_state(config).values.get(
                            "ai_claim_audit", []), *audit])
        else:
            # No retry: keep existing result and audit, with no unbounded raw copy.
            fresh = original_graph.get_state(config).values
            original_graph.update_state(config, {"ai_claim_audit": [
                *fresh.get("ai_claim_audit", []), *audit]}, as_node="finish")
    if correction and correction["status"] == "classifying":
        first = correction["attempts"][0]
        input = _correction_input(original_graph, config, adapter,
                                  original_graph.get_state(config).values)
        failure = None
        if (connection_factory is not None and first["model_turns"] < MAX_MODEL_TURNS
                and hasattr(model, "revise") and getattr(model, "revision", True) is not None
                and input.allow_partial_delivery):
            raw = first["raw"]
            if first["result"]["execution"] == "error" and first["result"].get(
                    "error") == "malformed_contribution":
                try:
                    validate_contribution(raw, input, original_graph, config)
                except ValueError as exc:
                    failure = classify(raw, input, original_graph, config, adapter,
                                       connection_factory, validation_error=exc)
            elif first["result"]["execution"] == "completed" and first[
                    "result"].get("contribution", {}).get("kind") == "binding_proposal":
                try:
                    failure = classify(raw, input, original_graph, config, adapter,
                                       connection_factory)
                except (EvidenceMismatch, ValueError, TypeError, KeyError):
                    pass  # Unknown pinned verifier failure is terminal.
        if failure:
            _, refs = _correction_observations(original_graph.get_state(config).values, input)
            correction = {**correction, "status": "eligible", "failure": failure,
                          "feedback": feedback(failure, input, refs,
                                               MAX_MODEL_TURNS - first["model_turns"]),
                          "attempts": [{**first, "status": "rejected"}]}
        else:
            correction = {**correction, "status": "terminal"}
        _checkpoint(original_graph, config, correction)
    if correction and correction["status"] in ("eligible", "reserved", "response_saved"):
        result = _correct(original_graph, config, adapter, connection_factory,
                          model, correction["attempts"][0])
    elif correction and correction["status"] in ("uncertain_terminal", "completed"):
        # Completed revision can be replayed from its saved response without a
        # second remote call if finalization was interrupted.
        if correction["status"] == "completed":
            input = _correction_input(original_graph, config, adapter,
                                      original_graph.get_state(config).values)
            revised = validate_contribution(correction["attempts"][1]["raw"], input,
                                            original_graph, config)
            result = runtime_envelope(input, execution="completed", contribution=revised)
        else:
            input = _correction_input(original_graph, config, adapter,
                                      original_graph.get_state(config).values)
            result = runtime_envelope(input, execution="error", error="correction_outcome_uncertain")
    elif correction and correction["status"] == "terminal" and len(correction["attempts"]) > 1:
        input = _correction_input(original_graph, config, adapter,
                                  original_graph.get_state(config).values)
        result = runtime_envelope(input, execution="error", error="revision_failed")
    fresh = original_graph.get_state(config).values
    if (fresh.get("assessment_id") != assessment_id or
            fresh.get("context", {}).get("bundle_sha256") !=
            state.get("context", {}).get("bundle_sha256")):
        raise EvidenceMismatch("Original assessment changed during investigation")
    original_graph.update_state(config, {"ai_fulfillment_result": result,
                                          "investigation_status": result["execution"],
                                         "trace": [*fresh["trace"],
                                                   "fulfillment_ai:" + result["execution"]]},
                                as_node="finish")
    return original_graph.get_state(config).values


def run_original_investigate_and_review(original_graph, config: dict, adapter: Phase1CAdapter,
                                        model: InvestigationModel, *, assessment_id: str,
                                        run_id: UUID) -> dict:
    """Resume a checkpointed binding candidate after the bounded AI investigation."""
    state = run_original_then_investigate(original_graph, config, adapter, model,
                                           assessment_id=assessment_id, run_id=run_id,
                                           connection_factory=getattr(original_graph,
                                                                      "phase2_connection_factory", None))
    snapshot = original_graph.get_state(config)
    if snapshot.next:
        original_graph.invoke(None, config)
    state = original_graph.get_state(config).values
    if (state.get("assessment_id") != assessment_id or state.get("phase1c_run_id") != str(run_id)):
        raise EvidenceMismatch("Reviewer handoff restart identity differs")
    if not state.get("reviewer_package") and not original_graph.get_state(config).next:
        from .candidate_graph import original_only_package

        original_graph.update_state(config, {"reviewer_package": original_only_package(state)},
                                    as_node="finish")
        state = original_graph.get_state(config).values
    return state
