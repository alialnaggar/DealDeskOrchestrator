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

from .hybrid_contracts import HybridContractError


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
                    or set(events[1]) != {"event", "returned_at_utc"}
                    or events[1]["event"] != "returned"
                    or not isinstance(events[1]["returned_at_utc"], str))):
            raise HybridContractError("send_receipt_invalid")
        return len(events) == 2
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
        result = send()
        _append(fd, {"event": "returned", "returned_at_utc":
                     datetime.now(timezone.utc).isoformat()})
        return result
    finally:
        os.close(fd)
