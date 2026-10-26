"""Opt-in hybrid LangGraph; original graph owns durable business checkpoints.

This offline entrypoint never accepts a provider transport. Outbound ownership
and checkpoints are separate from the unchanged iterative comparator.
"""

from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import TypedDict
from uuid import UUID

from langgraph.graph import END, START, StateGraph

from .candidate_contract import construct_candidate
from .fulfillment_agent import runtime_envelope, validate_contribution
from .fulfillment_tools import FulfillmentTools
from .graph_state import pinned_from_state
from .hybrid_contracts import (HybridContractError, decision, final, strict_binding,
                               verified_source_slices)
from .hybrid_pack import _canonical, prepare_pack
from .hybrid_revision import feedback_for
from .hybrid_send_reservation import (attempt_path, claim_and_call, exclusive_owner,
                                      verify_receipt)
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import entries
from .tool_permissions import MAX_CALLS, TrustedToolScope


RUN_VERSION = "hybrid-offline-run-v1"
MAX_DECISIONS = 6
HOSTED_BUDGET = {"version": "groq-smoke-budget-v1", "max_requests": 3,
                 "max_request_bytes": 8192, "max_output_tokens": 2048,
                 "max_decision_tokens": 512, "max_final_tokens": 1024,
                 "revision_enabled": False}
_CATEGORIES = frozenset(("inventory", "inbound_supply", "supplier_offer", "shipping_lane"))


def _save(graph, config, record):
    graph.update_state(config, {"hybrid_execution": record}, as_node="finish")


def _bounded(raw):
    try:
        size = len(_canonical(raw).encode())
    except (TypeError, ValueError, OverflowError):
        raise HybridContractError("raw_response_invalid") from None
    if size > 16384:
        raise HybridContractError("raw_response_oversize")
    return raw


def _send(graph, config, directory, record, stage, ordinal, request, callback):
    prior = [x for x in record["attempts"] if x["stage"] == stage and x["ordinal"] == ordinal]
    if record.get("hosted_budget") is not None:
        budget = record["hosted_budget"]
        if budget != HOSTED_BUDGET or stage not in ("decision", "final"):
            raise HybridContractError("hosted_budget_identity_invalid")
        if (stage == "decision" and ordinal not in (0, 1)
                or stage == "final" and ordinal not in (0, 1)):
            raise HybridContractError("hosted_request_budget_exhausted")
        if (not isinstance(request, dict) or request.get("model") != record["model"]
                or type(request.get("max_completion_tokens")) is not int
                or request["max_completion_tokens"] != budget[
                    "max_decision_tokens" if stage == "decision" else "max_final_tokens"]
                or len(_canonical(request).encode()) > budget["max_request_bytes"]):
            raise HybridContractError("hosted_wire_budget_exceeded")
        previous = record["attempts"]
        if not prior and (len(previous) >= budget["max_requests"]
                or sum(x["max_completion_tokens"] for x in previous) + request[
                    "max_completion_tokens"] > budget["max_output_tokens"]):
            raise HybridContractError("hosted_request_budget_exhausted")
    digest = sha256(_canonical(request).encode()).hexdigest()
    path = attempt_path(directory, assessment_id=record["assessment_id"],
                        start_digest=record["start_sha256"], stage=stage, ordinal=ordinal)
    returned = False
    if path.exists() or path.is_symlink():
        returned = verify_receipt(path, start_digest=record["start_sha256"], stage=stage,
                                  ordinal=ordinal, request_digest=digest)
    if prior:
        if (len(prior) != 1 or prior[0]["request_sha256"] != digest
                or not returned):
            raise EvidenceMismatch("Saved hybrid model result identity differs")
        if record.get("hosted_budget") is not None:
            _verify_hosted_usage(prior[0]["raw"], request)
        return prior[0]["raw"], record
    if record.get("pending") not in (None, {"stage": stage, "ordinal": ordinal,
                                          "request_sha256": digest}):
        raise EvidenceMismatch("Hybrid pending request identity differs")
    if path.exists() or path.is_symlink():
        raise HybridContractError("hybrid_send_outcome_uncertain")
    record = {**record, "pending": {"stage": stage, "ordinal": ordinal,
                                      "request_sha256": digest}}
    _save(graph, config, record)
    raw = claim_and_call(directory, assessment_id=record["assessment_id"],
                         start_digest=record["start_sha256"], stage=stage,
                         ordinal=ordinal, request_digest=digest,
                         send=lambda: _bounded(callback()))
    record = {**record, "pending": None, "attempts": [*record["attempts"],
              {"stage": stage, "ordinal": ordinal, "request_sha256": digest, "raw": raw,
               "max_completion_tokens": request["max_completion_tokens"] if record.get(
                   "hosted_budget") is not None else None}]}
    _save(graph, config, record)
    if record.get("hosted_budget") is not None:
        _verify_hosted_usage(raw, request)
    return raw, record


def _verify_hosted_usage(raw, request):
    usage = raw.get("usage") if isinstance(raw, dict) else None
    if (not isinstance(usage, dict) or type(usage.get("completion_tokens")) is not int
            or usage["completion_tokens"] < 0
            or usage["completion_tokens"] > request["max_completion_tokens"]):
        raise HybridContractError("hosted_usage_unverifiable")


def _inspect(graph, config, adapter, input, action, ordinal, start):
    pinned = pinned_from_state(graph.get_state(config).values)
    pool = adapter.validate_pinned_context(pinned)
    if (pinned.context.assessment_id != input.assessment_id
            or pinned.context.bundle_sha256 != input.bundle_sha256
            or pinned.context.source_input_digest != input.source_input_digest):
        raise EvidenceMismatch("Hybrid tool context changed")
    scope = TrustedToolScope(pinned.context, "fulfillment", input.subject_id,
                             pool["deal"]["customer_id"], frozenset((input.line_id,)),
                             _CATEGORIES)
    args = dict(action["arguments"])
    if "horizon" in args:
        args["horizon"] = date.fromisoformat(args["horizon"])
    call_id = sha256(f"{start}:model_inspect:{ordinal}".encode()).hexdigest()
    result = getattr(FulfillmentTools(graph, config, adapter, scope), action["tool_name"])(
        call_id=call_id, **args)
    if result.get("execution") != "completed":
        raise HybridContractError("inspection_" + str(result.get("execution")))
    return result


def _contribution(graph, config, adapter, factory, input, submission):
    kind, payload = submission["kind"], submission["payload"]
    if kind == "submit_proposal":
        proposal = strict_binding(payload, input, entries(
            graph, config, input.assessment_id, input.bundle_sha256))
        pinned = pinned_from_state(graph.get_state(config).values)
        candidate, _ = construct_candidate(adapter, pinned, proposal)
        checked, _ = adapter.verify_candidate(factory, pinned, candidate)
        verified_source_slices(proposal, checked)
        return {"schema_version": "3", "kind": "binding_proposal", "payload": proposal,
                "verification": "unverified", "review_summary_status": "fixed_verification_pending"}
    if kind == "submit_finding":
        if (set(payload) != {"line_id", "claims", "uncertainty_reasons"}
                or payload["line_id"] != input.line_id
                or not isinstance(payload["uncertainty_reasons"], list)):
            raise HybridContractError("invalid_finding")
        return validate_contribution({"schema_version": "2", "kind": "finding_without_proposal",
                                      "payload": {"line_id": input.line_id,
                                                  "claims": payload["claims"], "notes": {}}},
                                     input, graph, config)
    if kind == "abstain":
        if (set(payload) != {"reason_code", "scope", "missing_evidence"}
                or payload["scope"] != input.line_id
                or payload["reason_code"] not in ("insufficient_evidence", "unsupported_capability",
                                                   "authorization_limit", "model_uncertainty")
                or not isinstance(payload["missing_evidence"], list)
                or len(payload["missing_evidence"]) > 10
                or any(not isinstance(x, str) or len(x) > 128 for x in payload[
                    "missing_evidence"])):
            raise HybridContractError("invalid_abstention")
        return {"schema_version": "2", "kind": "abstention", "verification": None,
                "payload": {"line_id": input.line_id, "validated_claims": [],
                            "review_summary": []}, "model_contribution_kind": "abstention",
                "validation_disposition": "no_validated_claims"}
    raise HybridContractError("invalid_submission")


class HybridStep(TypedDict, total=False):
    phase: str


def build_hybrid_graph(original, config, adapter, factory, model, directory, pack, input):
    """Explicit conditional graph. Every transition is mirrored in the original checkpoint."""
    builder = StateGraph(HybridStep)

    def current():
        record = original.get_state(config).values["hybrid_execution"]
        if (record["start_sha256"] != pack["start_sha256"]
                or record["pack_sha256"] != pack["pack_sha256"]):
            raise EvidenceMismatch("Hybrid frozen pack differs at graph transition")
        return record

    def transition(record, phase, **updates):
        record = {**record, **updates, "phase": phase}
        _save(original, config, record)
        return {"phase": phase}

    def fail(record, exc, raw=None):
        if raw is not None:
            record = {**record, "rejections": [*record["rejections"], {
                "ordinal": len(record["rejections"]) + 1, "raw": raw,
                "reason": type(exc).__name__, "code": getattr(exc, "code", None)}]}
        result = runtime_envelope(input, execution="error", error=(
            "hybrid_rejected:" + getattr(exc, "code", type(exc).__name__)))
        return transition(record, "handoff", result=result)

    def gate(_):
        return {"phase": current()["phase"]}

    def decide(_):
        record = current()
        ordinal = record["decision_count"]
        if record.get("hosted_budget") is not None and ordinal >= 2:
            return fail(record, HybridContractError("hosted_request_budget_exhausted"))
        if ordinal >= MAX_DECISIONS:
            return fail(record, HybridContractError("model_turn_budget_exhausted"))
        request = {"pack_sha256": pack["pack_sha256"], "observations": record[
            "observations"], "ordinal": ordinal, "policy_version": record["policy_version"]}
        if hasattr(model, "wire_adapter"):
            request = model.request_decision(pack["model_input"], tuple(record["observations"]))
        raw, record = _send(original, config, directory, record, "decision", ordinal,
                            request, lambda: model.decide(pack["model_input"],
                                                          tuple(record["observations"])))
        try:
            parsed = (model.wire_adapter.parse_decision(raw, input.line_id, input.permitted_tools)
                      if hasattr(model, "wire_adapter") else raw)
            action = decision(parsed, line_id=input.line_id, permitted_tools=input.permitted_tools)
        except ValueError as exc:
            return fail(record, exc, raw)
        return transition(record, "inspection" if action["kind"] == "inspect" else "final",
                          action=action, decision_count=ordinal + 1,
                          intent=action if action["kind"] != "inspect" else None)

    def inspect(_):
        record = current()
        if record.get("hosted_budget") is not None and record["decision_count"] >= 2:
            return fail(record, HybridContractError("hosted_inspection_budget_exhausted"))
        try:
            if sum(bool(x.get("counted")) for x in entries(original, config,
                    input.assessment_id, input.bundle_sha256)) >= MAX_CALLS:
                raise HybridContractError("tool_budget_exhausted")
            observation = _inspect(original, config, adapter, input, record["action"],
                                   record["decision_count"] - 1, pack["start_sha256"])
        except (ValueError, EvidenceMismatch) as exc:
            return fail(record, exc)
        return transition(record, "decision", observations=[*record["observations"], observation])

    def submit(_):
        record = current()
        action = record["intent"]
        ordinal = record["decision_count"] - 1
        request = {"pack_sha256": pack["pack_sha256"], "intent": action,
                   "observations_sha256": sha256(_canonical(record[
                       "observations"]).encode()).hexdigest(),
                   "ordinal": ordinal, "policy_version": record["policy_version"]}
        if hasattr(model, "wire_adapter"):
            request = model.request_final(action, pack["model_input"],
                                          tuple(record["observations"]))
        raw, record = _send(original, config, directory, record, "final", ordinal,
                            request, lambda: model.submit(action, pack["model_input"],
                                                          tuple(record["observations"])))
        try:
            parsed = (model.wire_adapter.parse_final(raw, action)
                      if hasattr(model, "wire_adapter") else raw)
            submission = final(parsed, action)
        except ValueError as exc:
            return fail(record, exc, raw)
        return transition(record, "validate", submission=submission)

    def validate(_):
        record = current()
        submission = record["submission"]
        try:
            contribution = _contribution(original, config, adapter, factory, input, submission)
        except (ValueError, EvidenceMismatch) as exc:
            raw = next(x["raw"] for x in reversed(record["attempts"]) if x["stage"] == "final")
            rejection = {"ordinal": 1, "raw": raw, "reason": type(exc).__name__,
                         "code": getattr(exc, "code", None)}
            record = {**record, "rejections": [rejection]}
            _save(original, config, record)
            feedback = (feedback_for(submission["payload"], input, entries(original, config,
                input.assessment_id, input.bundle_sha256), failure=exc)
                if submission["kind"] == "submit_proposal" and record["decision_count"] < MAX_DECISIONS
                and record.get("hosted_budget") is None
                else None)
            if feedback is None:
                return fail(record, exc)
            return transition(record, "revision_intent", feedback=feedback)
        return accepted(record, contribution)

    def accepted(record, contribution):
        audit = contribution.pop("claim_audit", None)
        if audit:
            fresh = original.get_state(config).values
            rejected = [{"original_claim": item["original_claim"], "reason": item["reason"],
                         "claim_index": item["claim_index"], "assessment_id": input.assessment_id,
                         "bundle_sha256": input.bundle_sha256}
                        for item in audit.get("rejected_claims", [])]
            if audit.get("raw_model_notes"):
                rejected.append({"raw_model_notes": audit["raw_model_notes"],
                                 "reason": "audit_only_model_notes",
                                 "assessment_id": input.assessment_id,
                                 "bundle_sha256": input.bundle_sha256})
            existing = fresh.get("ai_claim_audit", [])
            original.update_state(config, {"ai_claim_audit": [
                *existing, *(item for item in rejected if item not in existing)]},
                as_node="finish")
        result = runtime_envelope(input, execution="completed", contribution=contribution)
        return transition(record, "handoff", result=result)

    def revision_intent(_):
        record = current()
        feedback = record["feedback"]
        request = {"pack_sha256": pack["pack_sha256"], "feedback": feedback,
                   "policy_version": record["policy_version"], "allowed": [
                       "submit_proposal", "abstain"]}
        if hasattr(model, "wire_adapter"):
            request = model.request_revision_intent(feedback, pack["model_input"],
                                                     tuple(record["observations"]))
        raw, record = _send(original, config, directory, record, "revision_intent", 0,
            request, lambda: model.revision_intent(feedback, pack["model_input"],
                                                   tuple(record["observations"])))
        try:
            parsed = (model.wire_adapter.parse_decision(raw, input.line_id, ())
                      if hasattr(model, "wire_adapter") else raw)
            action = decision(parsed, line_id=input.line_id, permitted_tools=())
            if action["kind"] not in ("submit_proposal", "abstain"):
                raise HybridContractError("invalid_revision_intent")
        except ValueError as exc:
            return fail(record, exc, raw)
        return transition(record, "revision", revision_intent=action)

    def revise(_):
        record = current()
        feedback = record["feedback"]
        request = {"pack_sha256": pack["pack_sha256"], "feedback": feedback,
                   "intent": record["revision_intent"],
                   "observations_sha256": sha256(_canonical(record[
                       "observations"]).encode()).hexdigest(),
                   "policy_version": record["policy_version"]}
        if hasattr(model, "wire_adapter"):
            request = model.request_revision(record["revision_intent"], feedback,
                                             pack["model_input"], tuple(record["observations"]))
        raw, record = _send(original, config, directory, record, "revision", 0,
            request, lambda: model.revise(record["revision_intent"], feedback, pack["model_input"],
                                          tuple(record["observations"])))
        try:
            parsed = (model.wire_adapter.parse_final(raw, record["revision_intent"])
                      if hasattr(model, "wire_adapter") else raw)
            submission = final(parsed, record["revision_intent"])
            contribution = _contribution(original, config, adapter, factory, input, submission)
        except (ValueError, EvidenceMismatch) as exc:
            return fail(record, exc, raw)
        return accepted(record, contribution)

    def handoff(_):
        record = current()
        result = record["result"]
        fresh = original.get_state(config).values
        existing = fresh.get("ai_fulfillment_result")
        if existing is None:
            original.update_state(config, {"ai_fulfillment_result": result,
                "investigation_status": result["execution"],
                "trace": [*fresh["trace"], "fulfillment_hybrid:" + result["execution"]]},
                as_node="finish")
        elif existing != result:
            raise EvidenceMismatch("Hybrid handoff result differs from original checkpoint")
        snapshot = original.get_state(config)
        if snapshot.next:
            original.invoke(None, config)
        if original.get_state(config).next:
            raise HybridContractError("candidate_checkpoint_not_complete")
        fresh = original.get_state(config).values
        if not fresh.get("reviewer_package"):
            if result["execution"] == "completed" and result["contribution"][
                    "kind"] == "binding_proposal":
                raise EvidenceMismatch("Hybrid candidate reviewer path was not completed")
            from .candidate_graph import original_only_package
            original.update_state(config, {"reviewer_package": original_only_package(fresh)},
                                  as_node="finish")
        return transition(record, "terminal")

    nodes = {"gate": gate, "decision": decide, "inspection": inspect, "final": submit,
             "validate": validate, "revision_intent": revision_intent,
             "revision": revise, "handoff": handoff}
    for name, node in nodes.items():
        builder.add_node(name, node)
    builder.add_edge(START, "gate")
    routes = {"decision": "decision", "inspection": "inspection", "final": "final",
              "validate": "validate", "revision_intent": "revision_intent",
              "revision": "revision", "handoff": "handoff",
              "terminal": END}
    for name in nodes:
        builder.add_conditional_edges(name, lambda state: state["phase"], routes)
    return builder.compile()


def run_hybrid_offline(graph, config, adapter, factory, model, *, assessment_id: str,
                       run_id: UUID, reservation_dir: Path,
                       policy_version: str = "hybrid-offline-v1") -> dict:
    """Run only a marked local double; all transport-based calls remain disabled."""
    if (getattr(model, "provider", None) != "offline_double"
            or getattr(model, "offline_only", False) is not True):
        raise HybridContractError("offline_double_required")
    return _run_hybrid(graph, config, adapter, factory, model,
        assessment_id=assessment_id, run_id=run_id, reservation_dir=reservation_dir,
        policy_version=policy_version)


def run_hybrid_evaluation(graph, config, adapter, factory, model, *,
                          assessment_id: str, run_id: UUID, reservation_dir: Path,
                          authorized: bool = False,
                          policy_version: str = "hybrid-groq-evaluation-v1") -> dict:
    """Dormant until separate hosted-evaluation authorization is explicitly passed.

    Not selected by the ordinary iterative entrypoint. No credentials are
    resolved or requests sent when the gate is closed.
    """
    from .hybrid_provider import GroqHybridTransportModel
    if authorized is not True or not isinstance(model, GroqHybridTransportModel):
        raise HybridContractError("hosted_evaluation_not_authorized")
    return _run_hybrid(graph, config, adapter, factory, model,
        assessment_id=assessment_id, run_id=run_id, reservation_dir=reservation_dir,
        policy_version=policy_version)


def _run_hybrid(graph, config, adapter, factory, model, *, assessment_id: str,
                run_id: UUID, reservation_dir: Path, policy_version: str) -> dict:
    with exclusive_owner(reservation_dir, assessment_id):
        reservation_identity = {"path": str(reservation_dir.resolve(strict=True)),
                                "device": reservation_dir.stat().st_dev,
                                "inode": reservation_dir.stat().st_ino}
        snapshot = graph.get_state(config)
        if not snapshot.values:
            from .orchestrator import initial_state
            graph.invoke(initial_state(assessment_id, run_id), config)
        elif snapshot.next:
            if snapshot.values.get("hybrid_execution", {}).get("phase") != "handoff":
                raise HybridContractError("hybrid_original_graph_incomplete")
        state = graph.get_state(config).values
        if (state.get("assessment_id") != assessment_id
                or state.get("phase1c_run_id") != str(run_id) or state.get("stop_reason")):
            raise EvidenceMismatch("Hybrid original assessment identity differs")
        record = state.get("hybrid_execution")
        if record and (record.get("version") != RUN_VERSION
                       or record.get("assessment_id") != assessment_id
                       or record.get("model") != model.model
                       or record.get("reservation_directory") != reservation_identity
                       or record.get("policy_version") != policy_version
                       or record.get("hosted_budget") != (HOSTED_BUDGET if model.provider == "groq" else None)):
            raise EvidenceMismatch("Hybrid restart identity differs")
        if record and record["phase"] == "terminal":
            saved_pack, _ = prepare_pack(graph, config, adapter, provider=model.provider,
                                         model=model.model, policy_version=policy_version)
            if (record["start_sha256"] != saved_pack["start_sha256"]
                    or record["pack_sha256"] != saved_pack["pack_sha256"]
                    or state.get("ai_fulfillment_result") != record.get("result")
                    or not state.get("reviewer_package")):
                raise EvidenceMismatch("Hybrid terminal checkpoint identity differs")
            return state
        if snapshot.next and record and record["phase"] == "handoff":
            # Candidate execution is internal to the unchanged original graph.
            # Finish it before tool-ledger/pack replay validation; no model send.
            for _ in range(12):
                if not graph.get_state(config).next:
                    break
                graph.invoke(None, config)
            if graph.get_state(config).next:
                raise HybridContractError("candidate_checkpoint_not_complete")
            state = graph.get_state(config).values
        if state.get("investigation_status") != "not_started" and not record:
            raise EvidenceMismatch("Hybrid cannot adopt an iterative investigation")
        pack, input = prepare_pack(graph, config, adapter, provider=model.provider,
                                   model=model.model, policy_version=policy_version)
        if not record:
            record = {"version": RUN_VERSION, "assessment_id": assessment_id,
                      "start_sha256": pack["start_sha256"], "pack_sha256": pack["pack_sha256"],
                      "model": model.model, "policy_version": policy_version, "phase": "decision",
                      "reservation_directory": reservation_identity,
                      **({"hosted_budget": dict(HOSTED_BUDGET)} if model.provider == "groq" else {}),
                      "decision_count": 0, "attempts": [], "rejections": [],
                      "observations": [pack["observation"]], "intent": None, "pending": None}
            _save(graph, config, record)
        private = build_hybrid_graph(graph, config, adapter, factory, model,
                                     reservation_dir, pack, input)
        private.invoke({"phase": record["phase"]}, {"recursion_limit": 2 * MAX_DECISIONS + 16})
        return graph.get_state(config).values
