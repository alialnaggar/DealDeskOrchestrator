"""Offline-only returned-original capture for the M4 Configuration mock path.

No Groq sender, hosted manifest, credential or budget is accepted. The separate
response-digest receipt proves only this scripted invocation, NOT a real Groq
original final. An uncertain original can never be sent again under its ID.
"""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from .hybrid_contracts import HybridContractError
from .hybrid_pack import _canonical
from .hybrid_send_reservation import (attempt_path, claim_and_call,
                                      exclusive_owner, verify_receipt)
from .m20_specialists import _identity, TOOLS, VERSION as M20_VERSION
from .m4_configuration_correction import _checked_context, _observation
from .phase1c_adapter import EvidenceMismatch
from .typed_final_contract import InvalidTerminal, decode

VERSION = "m4-configuration-original-offline-v1"
STAGE = "configuration_original_offline"


def _digest(value):
    return sha256(_canonical(value).encode()).hexdigest()


class ScriptedOriginalFinal:
    offline_only = True
    provider = "offline_double"

    def __init__(self, model, response):
        self.model = model
        self.response = response
        self.calls = 0

    def finish(self, request):
        self.calls += 1
        return self.response(deepcopy(request)) if callable(self.response) else deepcopy(self.response)


def _scope(graph, config, adapter, owner_dir, line_id, model):
    state, pinned, pool = _checked_context(graph, config, adapter, owner_dir)
    observation = _observation(graph, config, state, pinned, pool, line_id)
    ctx = pinned.context
    identity = _identity(ctx, "configuration")
    input = {**identity, "version": M20_VERSION,
        "line_ids": [str(row["deal_line_id"]) for row in pool["lines"]],
        "fixed_execution": state["specialist_results"]["configuration"]["execution"],
        "fixed_finding": state["specialist_results"]["configuration"]["finding"],
        "permitted_tool": TOOLS["configuration"], "max_inspections": 2}
    protocol = {"version": VERSION, "identity": identity, "model": model,
        "line_id": line_id, "observation_sha256": _digest(observation),
        "fixed_sha256": _digest(state["specialist_results"]["configuration"]),
        "owner_directory": str(owner_dir), "owner_device": owner_dir.stat().st_dev,
        "owner_inode": owner_dir.stat().st_ino}
    return state, ctx, observation, input, protocol


def checked_original_capture(graph, config, adapter, *, owner_dir, line_id,
                             model, rejected_content, start_digest):
    """Read-only validation under caller's exclusive owner lock; no model call."""
    state, ctx, observation, input, protocol = _scope(
        graph, config, adapter, owner_dir, line_id, model)
    if (type(rejected_content) is not str or type(start_digest) is not str
            or start_digest != _digest(protocol)):
        raise EvidenceMismatch("m4_original_capture_scope_changed")
    saved = state.get("m4_configuration_original_capture")
    request_digest = _digest({"version": VERSION, "protocol": protocol})
    if (type(saved) is not dict or set(saved) != {"protocol", "start_sha256",
            "request_sha256", "status", "content", "response_sha256"}
            or saved["protocol"] != protocol or saved["start_sha256"] != start_digest
            or saved["request_sha256"] != request_digest or saved["status"] != "returned"
            or saved["content"] != rejected_content or
            saved["response_sha256"] != sha256(rejected_content.encode()).hexdigest()):
        raise EvidenceMismatch("m4_original_capture_unverified")
    try:
        if not verify_receipt(attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                start_digest=start_digest, stage=STAGE, ordinal=0),
                start_digest=start_digest, stage=STAGE, ordinal=0,
                request_digest=request_digest, response_digest=saved["response_sha256"]):
            raise EvidenceMismatch("m4_original_capture_uncertain")
    except (FileNotFoundError, HybridContractError) as exc:
        raise EvidenceMismatch("m4_original_capture_receipt_changed") from exc
    try:
        decode(rejected_content, specialist="configuration", input=input,
               observations=observation)
    except InvalidTerminal:
        return saved["response_sha256"]
    raise EvidenceMismatch("m4_original_capture_not_rejected")


def capture_original_final_offline(graph, config, adapter, model, *,
                                   line_id, owner_dir, opt_in=False):
    """One scripted original response; a reserved/failed original is terminal."""
    if (opt_in is not True or type(model) is not ScriptedOriginalFinal or
            model.offline_only is not True or model.provider != "offline_double" or
            type(model.model) is not str or not model.model or
            type(line_id) is not str or not isinstance(owner_dir, Path)):
        raise ValueError("m4_original_offline_double_required")
    state, ctx, _, _, protocol = _scope(graph, config, adapter, owner_dir,
                                       line_id, model.model)
    with exclusive_owner(owner_dir, ctx.assessment_id):
        state, ctx, _, _, protocol = _scope(graph, config, adapter, owner_dir,
                                           line_id, model.model)
        start_digest = _digest(protocol)
        request_digest = _digest({"version": VERSION, "protocol": protocol})
        path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                            start_digest=start_digest, stage=STAGE, ordinal=0)
        saved = state.get("m4_configuration_original_capture")
        if saved is not None:
            if type(saved) is not dict or saved.get("status") != "returned":
                raise EvidenceMismatch("m4_original_capture_uncertain_no_replay")
            checked_original_capture(graph, config, adapter, owner_dir=owner_dir,
                line_id=line_id, model=model.model, rejected_content=saved.get("content"),
                start_digest=start_digest)
            return deepcopy(saved)
        if path.exists():
            raise EvidenceMismatch("m4_original_capture_orphan_receipt")
        reserved = {"protocol": protocol, "start_sha256": start_digest,
            "request_sha256": request_digest, "status": "reserved",
            "content": None, "response_sha256": None}
        graph.update_state(config, {"m4_configuration_original_capture": reserved},
                           as_node="finish")
        response = claim_and_call(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=start_digest, stage=STAGE, ordinal=0,
            request_digest=request_digest,
            send=lambda: model.finish({"version": VERSION, "protocol": protocol}),
            bind_response=True)
        returned = {**reserved, "status": "returned", "content": response,
            "response_sha256": sha256(response.encode()).hexdigest()}
        graph.update_state(config, {"m4_configuration_original_capture": returned},
                           as_node="finish")
        checked_original_capture(graph, config, adapter, owner_dir=owner_dir,
            line_id=line_id, model=model.model, rejected_content=response,
            start_digest=start_digest)
        return deepcopy(returned)
