"""Structural audit of a PROPOSED authorization, never a permission to send.

No trust anchor, issuer authentication, signature or revocation distribution is
approved. This module intentionally has no signing or verifying implementation.
Do not import it in a sender or treat zero structural errors as authorization.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal, TypedDict

from .graph_state import SPECIALISTS
from .m22_hosted_readiness import PROMPT_PLAN, PROMPT_PLAN_SHA256
from .m22_registry import _case, _digest
from .phase1c_adapter import PHASE1C_COMMIT

VERSION = "m22-campaign-authorization-proposal-v1"


class StageGrantV1(TypedDict):
    specialist: str
    model_id: str
    prompt_version: str
    prompt_sha256: str
    wire_version: str
    schema_sha256: str | None
    stage_manifest_sha256: str
    max_requests_per_case: int
    max_requests_total: int
    max_completion_tokens_per_request: int


class CampaignAuthorizationProposalV1(TypedDict):
    version: Literal["m22-campaign-authorization-proposal-v1"]
    approval_id: str
    campaign_id: str
    campaign_manifest_sha256: str
    case_set_sha256: str
    phase1c_commit: str
    phase2_commit: str
    cohorts: list[str]
    stages: list[StageGrantV1]
    max_requests_total: int
    max_requests_per_case: int
    max_completion_tokens_total: int
    max_provider_spend_usd: str
    billing_disabled_required: bool
    window_start: str
    window_end: str
    issued_at: str
    expires_at: str
    operator_subject_id: str
    approver_subject_id: str
    issuer_key_id: str
    checkpoint_namespace: str
    revocation_feed_id: str
    signature_b64: str


def _sha(value):
    return type(value) is str and len(value) == 64 and all(c in
        "0123456789abcdef" for c in value)


def _time(value):
    try:
        result = datetime.fromisoformat(value)
        return result if result.tzinfo and result.utcoffset() is not None else None
    except (TypeError, ValueError):
        return None


def audit_proposal(proposal: object, manifest: object, *,
                   expected_manifest_sha256: str, expected_issuer_key_id: str,
                   now: datetime, revoked_ids: frozenset[str] = frozenset()) -> dict:
    """Report structural mismatches; ALWAYS blocked regardless of inputs.

    expected_issuer_key_id, now and revoked_ids are untrusted test inputs here.
    A real approval would require an independent trust anchor and authenticated,
    current revocation proof that the operator cannot rewrite.
    """
    errors = set()
    if (type(proposal) is not dict or set(proposal) != set(
            CampaignAuthorizationProposalV1.__annotations__) or
            proposal.get("version") != VERSION):
        return {"version": VERSION, "authorization_status": "blocked",
                "errors": ["invalid_contract", "independent_verification_unavailable"]}
    if type(manifest) is not dict:
        manifest = {}
    try:
        digest_matches = _digest({k: v for k, v in manifest.items() if k != "sha256"}) == (
            expected_manifest_sha256)
    except (TypeError, ValueError):
        digest_matches = False
    if (manifest.get("sha256") !=
            expected_manifest_sha256 or not _sha(expected_manifest_sha256) or
            not digest_matches):
        errors.add("manifest_unverified")
        cases = []
    else:
        cases = manifest.get("cases")
        try:
            if type(cases) is not list or not cases:
                raise ValueError()
            for c in cases:
                _case(c)
        except (TypeError, ValueError, KeyError):
            errors.add("case_membership_invalid")
            cases = []
    if (proposal["campaign_manifest_sha256"] != expected_manifest_sha256 or
            proposal["campaign_id"] != manifest.get("campaign_id") or
            proposal["phase1c_commit"] != PHASE1C_COMMIT or
            proposal["phase1c_commit"] != manifest.get("phase1c_pin") or
            proposal["phase2_commit"] != manifest.get("phase2_sha")):
        errors.add("campaign_binding_changed")
    if (not _sha(proposal["case_set_sha256"]) or
            proposal["case_set_sha256"] != _digest(cases) or
            type(proposal["cohorts"]) is not list or
            any(type(c) is not str for c in proposal["cohorts"]) or
            sorted(proposal["cohorts"]) != sorted({c.get("cohort") for c in cases}) or
            len({c.get("case_id") for c in cases}) != len(cases) or
            len({c.get("assessment_id") for c in cases}) != len(cases)):
        errors.add("case_membership_changed")
    if (type(proposal["issuer_key_id"]) is not str or
            proposal["issuer_key_id"] != expected_issuer_key_id or
            not proposal["issuer_key_id"] or
            type(proposal["operator_subject_id"]) is not str or
            not proposal["operator_subject_id"] or
            type(proposal["approver_subject_id"]) is not str or
            not proposal["approver_subject_id"] or
            proposal["operator_subject_id"] == proposal["approver_subject_id"] or
            any(type(proposal[k]) is not str or not proposal[k] for k in (
                "approval_id", "checkpoint_namespace", "revocation_feed_id",
                "signature_b64"))):
        errors.add("issuer_or_separation_invalid")
    stages = proposal["stages"]
    if (type(stages) is not list or len(stages) != len(SPECIALISTS) or
            any(type(s) is not dict or set(s) != set(StageGrantV1.__annotations__)
                for s in stages) or
            any(type(s["specialist"]) is not str for s in stages) or
            tuple(s["specialist"] for s in stages) != tuple(SPECIALISTS)):
        errors.add("six_stage_scope_incomplete")
        stages = []
    for stage in stages:
        if (any(type(stage[k]) is not str or not stage[k] for k in (
                "model_id", "prompt_version", "wire_version")) or
                stage["prompt_version"] != PROMPT_PLAN.get(stage["specialist"]) or
                not all(_sha(stage[k]) for k in (
                    "prompt_sha256", "stage_manifest_sha256")) or
                (stage["schema_sha256"] is not None and not _sha(stage["schema_sha256"])) or
                (stage["specialist"] == "pricing" and not _sha(stage["schema_sha256"]))):
            errors.add("stage_identity_invalid")
        if (any(type(stage[k]) is not int or stage[k] <= 0 for k in (
                "max_requests_per_case", "max_requests_total",
                "max_completion_tokens_per_request")) or
                type(proposal["max_requests_per_case"]) is not int or
                stage["max_requests_per_case"] > proposal["max_requests_per_case"]):
            errors.add("request_budget_invalid")
        for c in cases:
            versions = c.get("contract_versions")
            if (type(versions) is not dict or
                    versions.get("model") != stage["model_id"] or
                    versions.get("prompt") != PROMPT_PLAN_SHA256 or
                    versions.get("capture") != "m22-checkpoint-observation-v1"):
                errors.add("case_model_or_contract_changed")
    if (any(type(proposal[k]) is not int or proposal[k] <= 0 for k in (
            "max_requests_total", "max_requests_per_case",
            "max_completion_tokens_total")) or
            stages and (proposal["max_requests_total"] > sum(
                s["max_requests_total"] for s in stages if type(s.get("max_requests_total")) is int)
                or proposal["max_requests_per_case"] > sum(
                s["max_requests_per_case"] for s in stages if type(s.get("max_requests_per_case")) is int))):
        errors.add("campaign_budget_invalid")
    try:
        amount = Decimal(proposal["max_provider_spend_usd"])
        if (type(proposal["max_provider_spend_usd"]) is not str or
                not amount.is_finite() or amount != 0 or
                proposal["billing_disabled_required"] is not True):
            errors.add("spending_not_disabled")
    except (InvalidOperation, TypeError, ValueError):
        errors.add("spending_not_disabled")
    start, end, issued, expires = (_time(proposal[k]) for k in (
        "window_start", "window_end", "issued_at", "expires_at"))
    if (not all((start, end, issued, expires)) or
            type(now) is not datetime or now.tzinfo is None or
            now.utcoffset() is None):
        errors.add("window_invalid")
    elif not (issued <= start < end <= expires and start <= now < end):
        errors.add("expired_or_out_of_window")
    if type(proposal["approval_id"]) is str and proposal["approval_id"] in revoked_ids:
        errors.add("revoked")
    errors.add("independent_verification_unavailable")
    return {"version": VERSION, "authorization_status": "blocked",
            "errors": sorted(errors)}
