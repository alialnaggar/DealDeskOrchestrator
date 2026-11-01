"""Read-only prospective hosted preflight. There is deliberately NO sender here.

The existing Groq development CLI is not an authorized prospective campaign.
No authenticated campaign approval boundary exists in the pinned application;
do not turn a Boolean, callback, credential or owner-writable file into one.
"""

import os

from .graph_state import SPECIALISTS, pinned_from_state, validate_result
from .groq_typed_final import PROMPT_VERSION as TYPED_PROMPT
from .live_models import GROQ_MODEL, PROMPT_VERSION as FULFILLMENT_PROMPT
from .m20_groq import PROMPT_VERSION as M20_PROMPT
from .m21_prompts import PROMPT_VERSION as M21_PROMPT
from .m22_registry import _digest
from .m22_enablement import _start_path
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT

VERSION = "m22-hosted-readiness-no-send-v1"
PROMPT_PLAN = {
    "configuration": M20_PROMPT,
    "pricing": TYPED_PROMPT,
    "fulfillment": FULFILLMENT_PROMPT,
    "credit": M21_PROMPT,
    "policy": M21_PROMPT,
    "approval_routing": M21_PROMPT,
}
PROMPT_PLAN_SHA256 = _digest(PROMPT_PLAN)
CONTRACTS = {"capture": "m22-checkpoint-observation-v1",
             "model": GROQ_MODEL, "prompt": PROMPT_PLAN_SHA256}


def inspect_prospective_case(campaign, case_id, *, state):
    """Validate the existing frozen registry/preflight without creating a send.

    A returned plan is a diagnostic, NOT a capability to invoke any sender.
    Precise per-request system prompts, their hashes and budgets must also be
    bound by an independently approved multi-stage campaign manifest before a
    real hosted entrypoint can exist. No such authority is presently available.
    """
    case = campaign._eligible(case_id)
    if os.path.lexists(_start_path(campaign.root, case_id)):
        raise EvidenceMismatch("Prospective assessment already started or uncertain")
    pinned = pinned_from_state(state)
    campaign.adapter.validate_pinned_context(pinned)
    context = pinned.context
    expected = {"assessment_id": context.assessment_id,
        "original_deal_id": context.original_deal_id,
        "phase1c_run_id": str(context.phase1c_run_id),
        "source_input_digest": context.source_input_digest,
        "bundle_sha256": context.bundle_sha256,
        "as_of_at": context.as_of_at.isoformat(),
        "data_snapshot_ref": context.data_snapshot_ref}
    if (type(state.get("specialist_results")) is not dict or
            set(state["specialist_results"]) != set(SPECIALISTS) or
            state.get("model_attempt_ledger") or state.get("m20_model_attempts") or
            state.get("typed_final_attempts") or state.get("m21_model_attempts") or
            any(case.get(k) != v for k, v in expected.items()) or
            case["contract_versions"] != CONTRACTS):
        raise EvidenceMismatch("Prospective hosted case or version differs")
    for name in SPECIALISTS:
        validate_result(state["specialist_results"][name], state, name)
    return {"version": VERSION, "case_id": case_id,
        "assessment_id": case["assessment_id"],
        "campaign_sha256": campaign.digest, "phase1c_pin": PHASE1C_COMMIT,
        "prompt_plan_sha256": PROMPT_PLAN_SHA256,
        "hosted_execution": "blocked_pending_independent_authority"}


def run_hosted_prospective(*args, **kwargs):
    """Never calls a callback: no trusted campaign authorizer exists today."""
    raise EvidenceMismatch("Prospective hosted authorization boundary unavailable")
