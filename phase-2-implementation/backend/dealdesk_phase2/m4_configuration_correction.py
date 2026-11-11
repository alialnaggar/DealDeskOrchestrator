"""Offline-only, one-shot Configuration correction over an original PG checkpoint.

An explicit caller-held rejected final is required: the live M2.0 transport does
NOT retain it, and cannot invoke this function. No network or hosted capability.
"""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

from .evidence_bundle import seal
from .fixed_specialists import domain_result
from .graph_state import pinned_from_state, validate_result
from .hybrid_pack import _canonical
from .hybrid_send_reservation import (attempt_path, claim_and_call, exclusive_owner,
                                       verify_receipt)
from .hybrid_contracts import HybridContractError
from .m20_specialists import _identity, _source_records, TOOLS, VERSION as M20_VERSION
from .m4_configuration_diagnostic import diagnose_boolean_text
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import entries
from .typed_final_contract import InvalidTerminal, decode

VERSION = "m4-configuration-correction-offline-v1"
STAGE = "configuration_correction"
BUDGET_VERSION = "m4-configuration-separate-budget-v1"


class ScriptedConfigurationCorrection:
    """Only permitted sender; a response is a model-authored terminal string."""

    offline_only = True
    provider = "offline_double"

    def __init__(self, model: str, response):
        self.model = model
        self.response = response
        self.calls = 0

    def finish(self, request):
        self.calls += 1
        return self.response(deepcopy(request)) if callable(self.response) else deepcopy(self.response)


def _digest(value):
    return sha256(_canonical(value).encode()).hexdigest()


def _checked_context(graph, config, adapter, owner_dir):
    snapshot = graph.get_state(config)
    state = snapshot.values
    if (snapshot.next or state.get("stop_reason") or state.get("m20_hosted_owner")
            or state.get("typed_final_hosted_start") or any(x.get("specialist") ==
                "configuration" for x in state.get("m20_model_attempts", []))
            or not isinstance(owner_dir, Path) or not owner_dir.is_absolute()):
        raise EvidenceMismatch("m4_configuration_offline_scope_required")
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    fixed = state["specialist_results"]["configuration"]
    validate_result(fixed, state, "configuration")
    if fixed["execution"] != "completed":
        raise EvidenceMismatch("m4_configuration_fixed_unavailable")
    decision = adapter.fixed_original_decision(pinned)
    raw, digest, _ = seal(decision)
    recomputed = domain_result("configuration", pinned, decision, state["assessment_id"], {})
    if (digest != state["fixed_decision_sha256"] or raw != state["fixed_decision"]
            or fixed != recomputed):
        raise EvidenceMismatch("m4_configuration_fixed_changed")
    if owner_dir.is_symlink() or owner_dir.stat().st_mode & 0o077:
        raise EvidenceMismatch("m4_configuration_owner_invalid")
    return state, pinned, pool


def _observation(graph, config, state, pinned, pool, line_id):
    ctx = pinned.context
    if line_id not in {str(x["deal_line_id"]) for x in pool["lines"]}:
        raise EvidenceMismatch("m4_configuration_line_outside_source")
    ledger = entries(graph, config, ctx.assessment_id, ctx.bundle_sha256)
    call_id = sha256(f"{M20_VERSION}:{ctx.assessment_id}:configuration:0".encode()).hexdigest()
    selected = [x for x in ledger if x.get("call_id") == call_id]
    identity = _identity(ctx, "configuration")
    if (len(selected) != 2 or [x.get("status") for x in selected] !=
            ["reserved", "completed"] or any(x.get("identity", {}).get(k) != v
            for x in selected for k, v in identity.items()) or any(x.get("tool") !=
            TOOLS["configuration"] or x.get("args") != {"line_id": line_id}
            for x in selected)):
        raise EvidenceMismatch("m4_configuration_inspection_ledger_changed")
    expected = _source_records(pool, state, "configuration", line_id)
    result = selected[1].get("result")
    if (result != {"version": M20_VERSION, "tool": TOOLS["configuration"],
            "execution": "completed", "records": expected,
            "returned_refs": [x["ref"] for x in expected]}):
        raise EvidenceMismatch("m4_configuration_inspection_result_changed")
    return (result,)


def run_configuration_correction_offline(graph, config, adapter, model, *,
                                         rejected_content, line_id, budget, owner_dir,
                                         opt_in=False):
    """One explicit separate budget, one call max; restart verifies, never sends.

    A forged checkpoint is outside the trust boundary of PostgreSQL itself;
    cross-check every source identity and a *separate* write-once send receipt.
    Callers must serialize one assessment's work using the existing owner lock.
    """
    if (opt_in is not True or type(model) is not ScriptedConfigurationCorrection or
            model.provider != "offline_double" or model.offline_only is not True or
            type(model.model) is not str or not model.model or
            type(rejected_content) is not str or type(line_id) is not str or
            type(budget) is not dict or budget != {"version": BUDGET_VERSION,
                "maximum_correction_posts": 1, "maximum_configured_completion_tokens": 512}):
        raise ValueError("m4_configuration_offline_explicit_budget_and_double_required")
    state, pinned, pool = _checked_context(graph, config, adapter, owner_dir)
    ctx = pinned.context
    identity = _identity(ctx, "configuration")
    with exclusive_owner(owner_dir, ctx.assessment_id):
        state, pinned, pool = _checked_context(graph, config, adapter, owner_dir)
        observation = _observation(graph, config, state, pinned, pool, line_id)
        input = {**identity, "version": M20_VERSION,
            "line_ids": [str(x["deal_line_id"]) for x in pool["lines"]],
            "fixed_execution": state["specialist_results"]["configuration"]["execution"],
            "fixed_finding": state["specialist_results"]["configuration"]["finding"],
            "permitted_tool": TOOLS["configuration"], "max_inspections": 2}
        diagnostic = diagnose_boolean_text(rejected_content, input=input,
            observations=observation, expected_identity=identity, fully_returned=True,
            remaining_turns=budget["maximum_correction_posts"])
        if diagnostic["classification"] != "boolean_text_format_candidate":
            raise EvidenceMismatch("m4_configuration_rejection_not_proven")
        field_path = diagnostic["field_paths"][0]
        claim = json.loads(rejected_content)["claims"][int(field_path.split("[")[1].split("]")[0])]
        original_id = _digest({"version": VERSION, "identity": identity,
            "model": model.model, "rejected_sha256": diagnostic["content_sha256"],
            "line_id": line_id, "observation_sha256": _digest(observation)})
        attempt_id = _digest({"version": VERSION, "original_attempt_id": original_id,
            "stage": STAGE, "ordinal": 0, "budget": budget})
        source = {"identity": identity, "line_id": line_id,
            "observation_sha256": _digest(observation),
            "fixed_configuration_sha256": _digest(state["specialist_results"]["configuration"]),
            "model": model.model, "provider": model.provider}
        original = {"attempt_id": original_id, "content": rejected_content,
            "content_sha256": diagnostic["content_sha256"],
            "validation_category": "claim_binding",
            "classification": diagnostic["classification"], "field_path": field_path,
            "returned_field": {"ref": claim["ref"], "field": claim["field"]},
            "source": source}
        request = {"version": VERSION, "attempt_id": attempt_id,
            "original_attempt_id": original_id, "source": source,
            "rejection_code": diagnostic["classification"], "field_path": field_path,
            "configured_completion_tokens": 512}
        request_digest = _digest(request)
        protocol = {"version": VERSION, "original": original, "budget": budget,
            "attempt_id": attempt_id, "request_sha256": request_digest,
            "owner_directory": str(owner_dir), "owner_device": owner_dir.stat().st_dev,
            "owner_inode": owner_dir.stat().st_ino}
        start_digest = _digest(protocol)
        path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=start_digest, stage=STAGE, ordinal=0)
        saved = state.get("m4_configuration_correction")
        if saved is not None and (type(saved) is not dict or saved.get("protocol") != protocol
                or saved.get("start_sha256") != start_digest):
            raise EvidenceMismatch("m4_configuration_protocol_changed")
        if (owner_dir.stat().st_dev != protocol["owner_device"] or
                owner_dir.stat().st_ino != protocol["owner_inode"]):
            raise EvidenceMismatch("m4_configuration_owner_changed")
        if saved is None:
            if path.exists():
                raise EvidenceMismatch("m4_configuration_orphan_receipt")
            saved = {"protocol": protocol, "start_sha256": start_digest, "attempts": []}
            graph.update_state(config, {"m4_configuration_correction": saved}, as_node="finish")
        rows = saved.get("attempts")
        marker = {"attempt_id": attempt_id, "original_attempt_id": original_id,
            "request_sha256": request_digest, "start_sha256": start_digest,
            "stage": STAGE, "ordinal": 0, "budget_version": BUDGET_VERSION}
        if (type(rows) is not list or len(rows) > 2 or any(type(x) is not dict or
                any(x.get(k) != v for k, v in marker.items()) or x.get("status") not in
                (("reserved",) if i == 0 else ("returned", "uncertain"))
                for i, x in enumerate(rows))):
            raise EvidenceMismatch("m4_configuration_attempt_corrupted")
        if len(rows) == 2 and rows[1]["status"] == "uncertain":
            if rows[1] != {**marker, "status": "uncertain", "reason": "send_not_proven_returned"}:
                raise EvidenceMismatch("m4_configuration_uncertain_attempt_corrupted")
            raise EvidenceMismatch("m4_configuration_uncertain_send_no_replay")
        if len(rows) == 2:
            result = rows[1]
            try:
                receipt_returned = verify_receipt(path, start_digest=start_digest, stage=STAGE,
                    ordinal=0, request_digest=request_digest,
                    response_digest=result.get("response_sha256"))
            except (HybridContractError, FileNotFoundError) as exc:
                raise EvidenceMismatch("m4_configuration_return_receipt_changed") from exc
            if (not receipt_returned or
                    result.get("response_sha256") != sha256(result.get("content", "").encode()).hexdigest()
                    or result.get("usage") is not None or result.get("cost_usd") is not None
                    or type(result.get("elapsed_ms")) is not int or result["elapsed_ms"] < 0
                    or result.get("response_model") != model.model):
                raise EvidenceMismatch("m4_configuration_return_receipt_changed")
            try:
                action = decode(result["content"], specialist="configuration",
                                input=input, observations=observation)
                status = "valid" if action["kind"] == "finding" else "abstained"
            except InvalidTerminal:
                action, status = None, "invalid"
            if (result.get("validation") != status or
                    result.get("validated_action") != action):
                raise EvidenceMismatch("m4_configuration_validation_changed")
            return deepcopy(result)
        if rows or path.exists():
            # Even a returned receipt without a checkpointed response is not
            # recoverable: the in-memory response may have been lost on crash.
            if rows:
                graph.update_state(config, {"m4_configuration_correction": {
                    **saved, "attempts": [rows[0], {**marker, "status": "uncertain",
                        "reason": "send_not_proven_returned"}]}}, as_node="finish")
            raise EvidenceMismatch("m4_configuration_uncertain_send_no_replay")
        graph.update_state(config, {"m4_configuration_correction": {
            **saved, "attempts": [{**marker, "status": "reserved"}]}}, as_node="finish")
        started = monotonic()
        try:
            response = claim_and_call(owner_dir, assessment_id=ctx.assessment_id,
                start_digest=start_digest, stage=STAGE, ordinal=0,
                request_digest=request_digest, send=lambda: model.finish(request),
                bind_response=True)
        except BaseException:
            # The receipt's failed marker is NOT evidence the provider did not
            # receive a request. A process crash may leave only the reservation.
            graph.update_state(config, {"m4_configuration_correction": {
                **saved, "attempts": [{**marker, "status": "reserved"},
                    {**marker, "status": "uncertain", "reason": "send_not_proven_returned"}]}},
                as_node="finish")
            raise
        elapsed = max(0, round((monotonic() - started) * 1000))
        if type(response) is not str or len(response.encode()) > 8192:
            raise EvidenceMismatch("m4_configuration_response_unrecordable")
        try:
            action = decode(response, specialist="configuration", input=input,
                            observations=observation)
            status = "valid" if action["kind"] == "finding" else "abstained"
        except InvalidTerminal:
            action, status = None, "invalid"
        returned = {**marker, "status": "returned", "content": response,
            "response_sha256": sha256(response.encode()).hexdigest(),
            "response_model": model.model, "usage": None, "cost_usd": None,
            "elapsed_ms": elapsed, "validation": status, "validated_action": action}
        graph.update_state(config, {"m4_configuration_correction": {
            **saved, "attempts": [{**marker, "status": "reserved"}, returned]}}, as_node="finish")
        return deepcopy(returned)
