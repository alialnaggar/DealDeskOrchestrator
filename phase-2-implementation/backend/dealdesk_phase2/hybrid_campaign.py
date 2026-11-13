"""Offline-safe coordinator for one separately authorized sequential Groq campaign.

No provider, credential, business database or model input is opened here. The
caller supplies audited per-case execution after explicit owner authorization.
The journal's reserved event is fsynced before a case begins; interrupted cases
never advance automatically, even if an underlying HTTP result is unknown.
"""

from dataclasses import dataclass
from hashlib import sha256
import fcntl
import json
import os
from pathlib import Path
import stat

from .hybrid_offline import HOSTED_BUDGET
from .hybrid_contracts import HybridContractError
from .hybrid_pack import _canonical
from .hybrid_send_reservation import sanitized_failure_code
from .live_models import GROQ_MODEL, ProviderError


CAMPAIGN_VERSION = "hybrid-groq-campaign-v1"
MODEL = GROQ_MODEL
ELIGIBLE = ("B01", "B02", "B03", "B04", "B05", "N01", "R03")
CONTROLS = ("N02", "N03", "N04")
CASE_ORDER = ELIGIBLE + CONTROLS
MAX_REQUESTS = len(ELIGIBLE) * HOSTED_BUDGET["max_requests"]  # 21
MAX_OUTPUT_CEILINGS = len(ELIGIBLE) * HOSTED_BUDGET["max_output_tokens"]  # 14,336
MAX_REPORTED_TOTAL_TOKENS = 60000  # observed usage stop threshold, not a billing ceiling
IDENTITIES_SHA256 = "a2dd38337c5d4a446c83143caacd2c8decef64d5ddd49191818df2145d0018ce"
REPLACEMENT_VERSION = "hybrid-groq-replacement-v1"
REPLACEMENT_IDENTITIES_SHA256 = "a1a431778efd694055e4d7f04b5f5d7bfb150f76dcd15579b2720179ad62653d"
CASE_LOCAL_CODES = frozenset(("transport_timeout", "transport_connection_lost",
                              "transport_protocol_failure", "invalid_provider_json",
                              "provider_response_oversize"))
MAX_CASE_LOCAL_FAILURES = 1
CONTAINED_MODEL_ERRORS = frozenset(("hybrid_rejected:invalid_binding_shape",
                                    "hybrid_rejected:binding_paths_required"))


def campaign_digest():
    """Digest of approved scope, not a secret or an authorization by itself."""
    return sha256(_canonical({"version": CAMPAIGN_VERSION, "model": MODEL,
        "eligible": ELIGIBLE, "controls": CONTROLS, "per_case_budget": HOSTED_BUDGET,
        "identities_sha256": IDENTITIES_SHA256,
        "contained_errors": sorted(CONTAINED_MODEL_ERRORS),
        "contained_failure_stop_count": 2,
        "max_requests": MAX_REQUESTS, "max_output_ceilings": MAX_OUTPUT_CEILINGS,
        "max_reported_total_tokens": MAX_REPORTED_TOTAL_TOKENS}).encode()).hexdigest()


def replacement_digest():
    """Distinct authorization; the historical campaign digest never changes."""
    return sha256(_canonical({"version": REPLACEMENT_VERSION, "model": MODEL,
        "eligible": ELIGIBLE, "controls": CONTROLS, "per_case_budget": HOSTED_BUDGET,
        "identities_sha256": REPLACEMENT_IDENTITIES_SHA256,
        "contained_errors": sorted(CONTAINED_MODEL_ERRORS),
        "contained_failure_stop_count": 2, "case_local_codes": sorted(CASE_LOCAL_CODES),
        "max_case_local_failures": MAX_CASE_LOCAL_FAILURES,
        "failed_case_reservation": "full_per_case_budget",
        "max_requests": MAX_REQUESTS, "max_output_ceilings": MAX_OUTPUT_CEILINGS,
        "max_reported_total_tokens": MAX_REPORTED_TOTAL_TOKENS}).encode()).hexdigest()


class CampaignStop(RuntimeError):
    """A safety or identity gate prevents advancing to any further case."""


class CaseLocalFailure(RuntimeError):
    """Raised only after verifying the exact failed send receipt and checkpoint."""
    def __init__(self, case_id: str, assessment_id: str, code: str,
                 known_tokens: int = 0, completed_requests: int = 0):
        self.case_id, self.assessment_id, self.code = case_id, assessment_id, code
        self.known_tokens, self.completed_requests = known_tokens, completed_requests
        super().__init__("case_local_failure")


def _stop_code(exc):
    if isinstance(exc, ProviderError):
        return sanitized_failure_code(exc)
    if isinstance(exc, HybridContractError) and str(exc) in {
            "invalid_groq_response", "invalid_groq_json", "invalid_groq_action",
            "invalid_groq_final", "raw_response_invalid", "raw_response_oversize"}:
        return str(exc)
    if isinstance(exc, CampaignStop):
        code = str(exc)
        if code in {"case_receipt_invalid", "control_model_invocation_or_gate_changed",
                    "case_safety_outcome", "usage_unverifiable",
                    "assessment_identity_reused", "reported_token_threshold_exceeded",
                    "repeated_contained_model_failures", "aggregate_budget_exhausted",
                    "campaign_checkpoint_source_changed", "control_eligibility_or_source_changed",
                    "case_local_failure_invalid", "repeated_case_local_failures"}:
            return code
        return "campaign_stop_unknown"
    return (type(exc).__name__ if type(exc) in (TimeoutError, KeyboardInterrupt)
            else "execution_failure_unknown")


def _private_directory(directory):
    if (not isinstance(directory, Path) or directory.is_symlink()
            or not directory.is_dir() or directory.stat().st_uid != os.geteuid()
            or stat.S_IMODE(directory.stat().st_mode) != 0o700):
        raise CampaignStop("campaign_directory_not_private")


def _append(fd, value):
    data = (_canonical(value) + "\n").encode()
    while data:
        written = os.write(fd, data)
        if written < 1:
            raise CampaignStop("journal_write_failed")
        data = data[written:]
    os.fsync(fd)


@dataclass(frozen=True)
class CaseReceipt:
    case_id: str
    assessment_id: str
    attempted_requests: int
    output_ceilings: int
    prompt_tokens: int | None
    completion_tokens: int | None
    candidate_status: str
    ai_execution: str
    contribution_kind: str | None
    critical_failure: bool = False
    citation_returned: int | None = None
    citation_submitted: int | None = None
    latency_ms: int | None = None
    rejection_codes: tuple[str, ...] = ()
    contained_error: str | None = None


def _validate_receipt(case_id, result, remaining_requests, remaining_output):
    if (not isinstance(result, CaseReceipt) or result.case_id != case_id
            or not isinstance(result.assessment_id, str) or not result.assessment_id
            or type(result.attempted_requests) is not int
            or not 0 <= result.attempted_requests <= min(
                HOSTED_BUDGET["max_requests"], remaining_requests)
            or type(result.output_ceilings) is not int
            or not 0 <= result.output_ceilings <= min(
                HOSTED_BUDGET["max_output_tokens"], remaining_output)
            or not isinstance(result.candidate_status, str)
            or not isinstance(result.ai_execution, str)
            or type(result.critical_failure) is not bool
            or any(type(x) is not int or x < 0 for x in (
                result.citation_returned, result.citation_submitted, result.latency_ms)
                if x is not None)
            or not isinstance(result.rejection_codes, tuple)
            or any(not isinstance(x, str) or len(x) > 64 or not x.replace("_", "").isalnum()
                   for x in result.rejection_codes)):
        raise CampaignStop("case_receipt_invalid")
    if case_id in CONTROLS:
        if (result.attempted_requests or result.output_ceilings
                or result.ai_execution != "skipped" or result.candidate_status != "not_started"):
            raise CampaignStop("control_model_invocation_or_gate_changed")
    else:
        contained = (result.ai_execution == "error"
            and result.contained_error in CONTAINED_MODEL_ERRORS
            and result.candidate_status == "not_started"
            and result.contribution_kind is None and bool(result.rejection_codes))
        if (result.attempted_requests < 1 or result.ai_execution not in ("completed", "error")
                or result.critical_failure or result.ai_execution == "error" and not contained
                or result.ai_execution == "completed" and result.contained_error is not None
                or result.candidate_status not in ("fixed_checked", "not_started")
                or result.ai_execution == "completed" and result.contribution_kind not in (
                    "binding_proposal", "finding_without_proposal", "abstention")
                or result.candidate_status == "fixed_checked"
                    and result.contribution_kind != "binding_proposal"
                or result.contribution_kind == "binding_proposal"
                    and result.candidate_status != "fixed_checked"
                or case_id in ("N01", "R03") and (
                    result.candidate_status != "not_started"
                    or result.contribution_kind == "binding_proposal")):
            raise CampaignStop("case_safety_outcome")
        if (result.prompt_tokens is None or result.completion_tokens is None
                or type(result.prompt_tokens) is not int or result.prompt_tokens < 0
                or type(result.completion_tokens) is not int or result.completion_tokens < 0
                or result.completion_tokens > result.output_ceilings):
            raise CampaignStop("usage_unverifiable")


def run_campaign(directory: Path, *, authorized: bool, approved_digest: str,
                 execute_case, assess_control, replacement: bool = False,
                 assessments: dict | None = None) -> dict:
    """No live transport here; callbacks must enforce pinned source and send gates.

    Historical campaigns stop on any failed case. Replacement campaigns may
    skip one attested case-local failure; neither campaign ever resumes.
    Nothing in this function turns a failed proposal into a business approval.
    """
    digest = replacement_digest() if replacement is True else campaign_digest()
    if (authorized is not True or approved_digest != digest
            or type(replacement) is not bool):
        raise CampaignStop("campaign_not_authorized")
    if replacement:
        if (not isinstance(assessments, dict) or set(assessments) != set(CASE_ORDER)
                or any(not isinstance(x, str) or not x.startswith(
                    "HYBRID-REPLACEMENT-" + case + "-") for case, x in assessments.items())
                or len(set(assessments.values())) != len(CASE_ORDER)):
            raise CampaignStop("replacement_assessments_invalid")
    elif assessments is not None:
        raise CampaignStop("campaign_not_authorized")
    if not callable(execute_case) or not callable(assess_control):
        raise CampaignStop("campaign_callbacks_missing")
    _private_directory(directory)
    path = directory / ("hybrid-campaign-" + digest + ".audit.jsonl")
    if path.exists() or path.is_symlink():
        raise CampaignStop("campaign_already_started")
    if any(directory.iterdir()):
        raise CampaignStop("campaign_directory_not_fresh")
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        raise CampaignStop("campaign_already_started") from None
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.geteuid()
                or stat.S_IMODE(st.st_mode) != 0o600):
            raise CampaignStop("campaign_journal_invalid")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise CampaignStop("campaign_owner_busy") from None
        if st.st_size:
            # No reuse, resume or second campaign behind a process crash.
            raise CampaignStop("campaign_already_started")
        _append(fd, {"event": "start", "digest": digest,
                     "cases": CASE_ORDER, "model": MODEL})
        dfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        requests, output, reported, contained_failures, case_failures = 0, 0, 0, 0, 0
        minimum_attempted = 0
        completed = []
        for case_id in CASE_ORDER:
            _append(fd, {"event": "case_reserved", "case_id": case_id})
            try:
                result = (execute_case(case_id, MAX_REQUESTS - requests,
                                       MAX_OUTPUT_CEILINGS - output)
                          if case_id in ELIGIBLE else assess_control(case_id))
                _validate_receipt(case_id, result, MAX_REQUESTS - requests,
                                  MAX_OUTPUT_CEILINGS - output)
                if replacement and result.assessment_id != assessments[case_id]:
                    raise CampaignStop("replacement_assessments_invalid")
                if result.assessment_id in {item.assessment_id for item in completed}:
                    raise CampaignStop("assessment_identity_reused")
                requests += result.attempted_requests
                minimum_attempted += result.attempted_requests
                output += result.output_ceilings
                if result.contained_error:
                    contained_failures += 1
                if case_id in ELIGIBLE:
                    reported += result.prompt_tokens + result.completion_tokens
                    if reported > MAX_REPORTED_TOTAL_TOKENS:
                        raise CampaignStop("reported_token_threshold_exceeded")
                # Exclude reviewer answers and raw model output from public summary.
                _append(fd, {"event": "case_completed", "case_id": case_id,
                    "assessment_id": result.assessment_id,
                    "attempted_requests": result.attempted_requests,
                    "output_ceilings": result.output_ceilings,
                    "reported_tokens": (result.prompt_tokens + result.completion_tokens
                                        if case_id in ELIGIBLE else None),
                    "candidate_status": result.candidate_status,
                    "ai_execution": result.ai_execution,
                    "contribution_kind": result.contribution_kind,
                    "citation_returned": result.citation_returned,
                    "citation_submitted": result.citation_submitted,
                    "latency_ms": result.latency_ms,
                    "rejection_codes": result.rejection_codes,
                    "contained_error": result.contained_error})
                completed.append(result)
                if contained_failures >= 2:
                    raise CampaignStop("repeated_contained_model_failures")
            except CaseLocalFailure as exc:
                if (not replacement or case_id not in ELIGIBLE or exc.case_id != case_id
                        or exc.assessment_id != assessments[case_id]
                        or exc.code not in CASE_LOCAL_CODES
                        or type(exc.known_tokens) is not int or exc.known_tokens < 0
                        or type(exc.completed_requests) is not int
                        or not 0 <= exc.completed_requests < HOSTED_BUDGET["max_requests"]
                        or MAX_REQUESTS - requests < HOSTED_BUDGET["max_requests"]
                        or MAX_OUTPUT_CEILINGS - output < HOSTED_BUDGET["max_output_tokens"]):
                    _append(fd, {"event": "campaign_stopped", "case_id": case_id,
                                 "code": "case_local_failure_invalid"})
                    raise CampaignStop("case_local_failure_invalid") from None
                # Unknown provider usage cannot be claimed as zero. Charge the
                # entire case allocation before starting any unrelated case.
                requests += HOSTED_BUDGET["max_requests"]
                minimum_attempted += exc.completed_requests + 1
                output += HOSTED_BUDGET["max_output_tokens"]
                reported += exc.known_tokens
                case_failures += 1
                _append(fd, {"event": "case_failed", "case_id": case_id,
                    "assessment_id": exc.assessment_id, "code": exc.code,
                    "completed_requests": exc.completed_requests,
                    "reported_tokens_known": exc.known_tokens,
                    "reserved_requests": HOSTED_BUDGET["max_requests"],
                    "reserved_output_ceilings": HOSTED_BUDGET["max_output_tokens"],
                    "reported_usage": "incomplete"})
                if reported > MAX_REPORTED_TOTAL_TOKENS:
                    _append(fd, {"event": "campaign_stopped", "case_id": case_id,
                                 "code": "reported_token_threshold_exceeded"})
                    raise CampaignStop("reported_token_threshold_exceeded") from None
                if case_failures >= MAX_CASE_LOCAL_FAILURES + 1:
                    _append(fd, {"event": "campaign_stopped", "case_id": case_id,
                                 "code": "repeated_case_local_failures"})
                    raise CampaignStop("repeated_case_local_failures") from None
                continue
            except BaseException as exc:
                _append(fd, {"event": "campaign_stopped", "case_id": case_id,
                             "code": _stop_code(exc)})
                raise
        summary = {"cases": len(completed), "requests": requests,
                   "output_ceilings": output, "reported_tokens": reported}
        _append(fd, {"event": "campaign_completed", **summary,
                     "contained_failures": contained_failures,
                     **({"case_local_failures": case_failures,
                         "reserved_request_slots": requests,
                         "minimum_attempted_requests": minimum_attempted}
                        if replacement else {})})
        return {"digest": digest, **summary,
                **({"case_local_failures": case_failures,
                    "reserved_request_slots": requests,
                    "minimum_attempted_requests": minimum_attempted}
                   if replacement else {})}
    finally:
        os.close(fd)
