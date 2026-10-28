"""Durable, exclusive hybrid send primitive; NOT wired into any live runtime.

The caller must checkpoint the immutable investigation and exact request digest
before using this primitive. A reserved-but-unfinished file is permanently
uncertain: no sender is invoked by another process for that attempt identity.
"""

from datetime import datetime, timezone
from contextlib import contextmanager
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
from time import monotonic

from .hybrid_contracts import HybridContractError
from .live_models import ProviderError
from .groq_error_diagnostic import safe_fields


def sanitized_failure_code(exc: BaseException) -> str:
    """Allow only fixed provider categories; never persist exception text."""
    if isinstance(exc, ProviderError):
        code = exc.code
        if (type(code) is str and (code in {
                "transport_timeout", "transport_connection_lost",
                "transport_connection_failure", "transport_network_error",
                "transport_protocol_failure", "transport_failure",
                "invalid_provider_json", "invalid_provider_response",
                "provider_response_oversize", "provider_http_unknown",
                "invalid_request_timeout", "request_too_large", "missing_credential"}
                or len(code) == 8 and code.startswith("http_")
                and code[5:].isdigit() and 100 <= int(code[5:]) <= 599)):
            return code
        return "provider_failure_unknown"
    return "send_failure_unknown"


def _valid_failure(event):
    if (set(event) not in ({"event", "code", "elapsed_ms"},
                           {"event", "code", "elapsed_ms", "diagnostic"})
            or event["event"] != "failed"
            or type(event["elapsed_ms"]) is not int or event["elapsed_ms"] < 0):
        return False
    if type(event["code"]) is not str:
        return False
    if "diagnostic" in event and (not event["code"].startswith("http_")
            or type(event["diagnostic"]) is not dict or not event["diagnostic"]
            or safe_fields({**{"type": "unknown", "code": "unknown",
                "param": "unknown", "request_id": None}, **event["diagnostic"]})
                != event["diagnostic"]):
        return False
    code = event["code"]
    return (type(code) is str and
            (sanitized_failure_code(ProviderError(code)) == code
             or code == "send_failure_unknown"))


@contextmanager
def exclusive_owner(directory: Path, assessment_id: str):
    """Cross-process mutex for one assessment's sequential checkpoint/tool writes.

    The file is permanent; a crashed process releases only its OS lock. The
    next owner must inspect checkpoints and send receipts before doing work.
    """
    path = attempt_path(directory, assessment_id=assessment_id,
                        start_digest="0" * 64, stage="owner", ordinal=0)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise HybridContractError("hybrid_owner_busy") from None
        if os.fstat(fd).st_nlink != 1 or os.fstat(fd).st_mode & 0o077:
            raise HybridContractError("hybrid_owner_file_invalid")
        dfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        yield
    finally:
        os.close(fd)


def _append(fd: int, value: dict):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    while data:
        written = os.write(fd, data)
        if written <= 0:
            raise OSError("Cannot persist hybrid attempt")
        data = data[written:]
    os.fsync(fd)


def attempt_path(directory: Path, *, assessment_id: str, start_digest: str,
                 stage: str, ordinal: int) -> Path:
    if (not isinstance(directory, Path) or not directory.is_dir() or directory.is_symlink()
            or directory.stat().st_uid != os.geteuid() or directory.stat().st_mode & 0o077
            or not isinstance(assessment_id, str) or not assessment_id
            or len(assessment_id) > 128 or not isinstance(start_digest, str)
            or len(start_digest) != 64 or any(c not in "0123456789abcdef" for c in start_digest)
            or stage not in ("owner", "decision", "final", "revision_intent", "revision")
            or type(ordinal) is not int or ordinal < 0 or ordinal > 6):
        raise HybridContractError("invalid_send_reservation_scope")
    identity = f"{assessment_id}:{start_digest}:{stage}:{ordinal}"
    return directory / (sha256(identity.encode()).hexdigest() + ".hybrid.audit.jsonl")


def verify_receipt(path: Path, *, start_digest: str, stage: str,
                   ordinal: int, request_digest: str) -> bool:
    """Verify a receipt; return whether the send reached its returned marker.

    A reserved-only receipt is valid proof of an uncertain attempt, never
    evidence of a completed response that can be replayed.
    """
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        stat = os.fstat(fd)
        if (stat.st_nlink != 1 or stat.st_uid != os.geteuid()
                or stat.st_mode & 0o077 or stat.st_size > 4096
                or stat.st_size == 0):
            raise HybridContractError("send_receipt_invalid")
        with os.fdopen(os.dup(fd), "r", encoding="utf-8") as stream:
            events = [json.loads(line) for line in stream]
        if (len(events) not in (1, 2) or not isinstance(events[0], dict)
                or set(events[0]) != {"event", "stage", "ordinal", "start_sha256",
                                       "request_sha256", "reserved_at_utc"}
                or events[0]["event"] != "reserved" or events[0]["stage"] != stage
                or type(events[0]["ordinal"]) is not int or events[0]["ordinal"] != ordinal
                or events[0]["start_sha256"] != start_digest
                or events[0]["request_sha256"] != request_digest
                or not isinstance(events[0]["reserved_at_utc"], str)
                 or len(events) == 2 and (not isinstance(events[1], dict)
                     or not ((set(events[1]) == {"event", "returned_at_utc"}
                              and events[1]["event"] == "returned"
                              and isinstance(events[1]["returned_at_utc"], str))
                             or _valid_failure(events[1])))):
            raise HybridContractError("send_receipt_invalid")
        return len(events) == 2 and events[1]["event"] == "returned"
    except (UnicodeError, ValueError, TypeError):
        raise HybridContractError("send_receipt_invalid") from None
    finally:
        os.close(fd)


def claim_and_call(directory: Path, *, assessment_id: str, start_digest: str,
                   stage: str, ordinal: int, request_digest: str, send):
    """One sender invocation maximum per identity, even on crash/error/race.

    Returns the in-memory response only; no raw provider response or key is
    written to the audit. The caller owns bounded parse/checkpoint persistence.
    """
    if (not isinstance(request_digest, str) or len(request_digest) != 64
            or any(c not in "0123456789abcdef" for c in request_digest)
            or not callable(send)):
        raise HybridContractError("invalid_send_request")
    path = attempt_path(directory, assessment_id=assessment_id,
                        start_digest=start_digest, stage=stage, ordinal=ordinal)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_APPEND |
                 os.O_NOFOLLOW, 0o600)
    try:
        _append(fd, {"event": "reserved", "stage": stage, "ordinal": ordinal,
                     "start_sha256": start_digest, "request_sha256": request_digest,
                     "reserved_at_utc": datetime.now(timezone.utc).isoformat()})
        dfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        # No exception handler with a retry. A transport error or an unexpected
        # crash leaves a terminal reservation, not permission to send again.
        started = monotonic()
        try:
            result = send()
        except BaseException as exc:
            failure = {"event": "failed", "code": sanitized_failure_code(exc),
                       "elapsed_ms": max(0, round((monotonic() - started) * 1000))}
            if isinstance(exc, ProviderError) and failure["code"].startswith("http_"):
                fields = safe_fields(exc.diagnostic)
                if fields:
                    failure["diagnostic"] = fields
            _append(fd, failure)
            raise
        _append(fd, {"event": "returned", "returned_at_utc":
                     datetime.now(timezone.utc).isoformat()})
        return result
    finally:
        os.close(fd)
