"""Versioned original state with isolated fixed and M1.3 AI results."""

from datetime import datetime
from typing import Literal, TypedDict
from uuid import UUID

from .contracts import RunContextV1
from .evidence_bundle import unseal
from .phase1c_adapter import EvidenceMismatch, PinnedBundleV1


STATE_VERSION = "m1.1-original-v1"
SPECIALISTS = ("configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing")


class SpecialistResultV1(TypedDict):
    version: str
    specialist: str
    producer_type: Literal["deterministic"]
    assessment_id: str
    subject_id: str
    bundle_sha256: str
    execution: Literal["completed", "skipped", "error"]
    finding: str
    prerequisite: str
    payload: object
    error: str | None


class AssessmentStateV1(TypedDict, total=False):
    state_version: str
    assessment_id: str
    phase1c_run_id: str
    subject_kind: str
    context: dict
    sealed_bundle: str
    fixed_decision: str
    fixed_decision_sha256: str
    specialist_results: dict[str, SpecialistResultV1]
    trace: list[str]
    stop_reason: str | None
    review_status: str
    # M1.2 additive field; older M1.1 checkpoints treat absence as no calls.
    tool_access_ledger: list[dict]
    # M1.3 additive result; the six fixed specialist slots remain authoritative.
    ai_fulfillment_result: dict
    investigation_status: str
    # M1.4: sequential, checkpointed reservations and sanitized outcomes.
    model_attempt_ledger: list[dict]
    # M1.6 raw rejected claims and validation errors; never reviewer-facing prose.
    ai_claim_audit: list[dict]
    # M1.7 additive candidate slot, isolated from original fixed results.
    candidate_state_version: str
    candidate_records: dict[str, dict]
    candidate_status: str
    reviewer_package: dict
    # Additive, original-subject correction attempt and reservation audit.
    fulfillment_correction: dict
    # Opt-in adaptive hybrid state. Existing iterative nodes ignore these keys.
    hybrid_investigation_start: dict
    hybrid_evidence_pack: dict
    hybrid_execution: dict


def context_to_record(context: RunContextV1) -> dict:
    return {**vars(context), "phase1c_run_id": str(context.phase1c_run_id),
            "as_of_at": context.as_of_at.isoformat()}


def context_from_record(record: dict) -> RunContextV1:
    return RunContextV1(**{**record, "phase1c_run_id": UUID(record["phase1c_run_id"]),
                           "as_of_at": datetime.fromisoformat(record["as_of_at"])})


def pinned_from_state(state: AssessmentStateV1) -> PinnedBundleV1:
    if (state.get("state_version") != STATE_VERSION or state.get("subject_kind") != "original"
            or state.get("assessment_id") != state.get("context", {}).get("assessment_id")
            or state.get("phase1c_run_id") != state.get("context", {}).get("phase1c_run_id")):
        raise EvidenceMismatch("Graph state identity or version differs")
    context = context_from_record(state["context"])
    raw = state["sealed_bundle"]
    bundle = unseal(raw, context.bundle_sha256)
    if (str(bundle["run"]["run_id"]) != str(context.phase1c_run_id)
            or str(bundle["deal"]["deal_id"]) != context.original_deal_id):
        raise EvidenceMismatch("Sealed evidence run or deal differs")
    return PinnedBundleV1(context, raw, len(raw.encode("utf-8")))


def validate_result(result: SpecialistResultV1, state: AssessmentStateV1,
                    expected: str, *, subject_id: str | None = None) -> None:
    pinned = pinned_from_state(state)
    if (result.get("version") != "1" or result.get("specialist") != expected
            or result.get("producer_type") != "deterministic"
            or result.get("assessment_id") != state["assessment_id"]
            or result.get("subject_id") != (subject_id or pinned.context.original_deal_id)
            or result.get("bundle_sha256") != pinned.context.bundle_sha256
            or result.get("execution") not in ("completed", "skipped", "error")):
        raise EvidenceMismatch("Specialist result identity, producer or contract differs")
    if result["execution"] == "completed" and result.get("error") is not None:
        raise ValueError("Completed result cannot have an execution error")
    if result["execution"] == "error" and not result.get("error"):
        raise ValueError("Execution error must carry a reason")
