"""Export and replay a candidate decision trace without writing database rows.

The sidecar is a prototype: exclusive creation prevents accidental overwrite,
and replay detects changed content or reader facts. It is not access-controlled
immutable storage or a substitute for an approved production audit design.
"""

from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import UUID

from phase1c_candidate import compare_for_human


TRACE_VERSION = 1
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")


def _encode(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    raise TypeError(f"Unsupported trace value: {type(value).__name__}")


def _canonical(value):
    return json.dumps(value, default=_encode, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def build_trace_record(candidate, original_bundle, checked_bundle):
    """Build an evidence-linked, deterministic record from a fresh reader replay."""
    from phase1c_deal_decision import assemble_deal_decision
    comparison = compare_for_human(candidate, original_bundle, checked_bundle)
    original = assemble_deal_decision(original_bundle)
    proposed = assemble_deal_decision(checked_bundle)
    trace = checked_bundle["candidate_trace"]
    actual_sources = sorted({source
                             for part in trace["assessment"]["slices"]
                             for source in part["source_ids"]})
    payload = {
        "trace_version": TRACE_VERSION,
        "candidate": asdict(candidate),
        "original_requested_date": original_bundle["deal"]["requested_delivery_date"],
        "parent_run_id": str(candidate.parent_run_id),
        "parent_deal_id": candidate.parent_deal_id,
        "source_input_digest": trace["source_input_digest"],
        "candidate_input_digest": trace["candidate_input_digest"],
        "reader_assessment": trace["assessment"],
        "actual_source_ids": actual_sources,
        "rerun_specialists": trace["rerun_specialists"],
        "original_decision": original,
        "candidate_decision": proposed,
        "human_comparison": comparison,
        "side_effects": "read_only_no_stock_or_approval_write",
    }
    # Round-trip normalizes dates, UUIDs, Decimals and tuple fields to JSON.
    payload = json.loads(_canonical(payload))
    return {"payload": payload, "sha256": sha256(_canonical(payload).encode()).hexdigest()}


def export_trace_once(directory, record):
    """Exclusively create one UTF-8 sidecar; an existing candidate is never replaced."""
    candidate_id = record["payload"]["candidate"]["candidate_id"]
    if not SAFE_ID.fullmatch(candidate_id):
        raise ValueError("Unsafe candidate ID for trace filename")
    if record["sha256"] != sha256(_canonical(record["payload"]).encode()).hexdigest():
        raise ValueError("Record digest does not match payload")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{candidate_id}.json"
    data = _canonical(record) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    return path


def verify_exported_trace(path, candidate, original_bundle, checked_bundle):
    """Compare the saved record with the supplied reader bundles."""
    with Path(path).open(encoding="utf-8") as source:
        saved = json.load(source)
    if not isinstance(saved, dict) or set(saved) != {"payload", "sha256"}:
        raise ValueError("Malformed candidate trace")
    if saved["sha256"] != sha256(_canonical(saved["payload"]).encode()).hexdigest():
        raise ValueError("Saved candidate trace content changed")
    expected = build_trace_record(candidate, original_bundle, checked_bundle)
    if saved != expected:
        raise ValueError("Saved trace differs from replayed reader evidence or decision")
    return saved["sha256"]


def replay_exported_trace(conn, path, candidate, *, reader_kwargs=None):
    """Re-read the parent and candidate before verifying a saved sidecar."""
    from phase1c_candidate import verify_run_correlation
    from phase1c_reader import read_run

    options = dict(reader_kwargs or {})
    if "candidate" in options:
        raise ValueError("Reader options cannot replace the trace candidate")
    original = read_run(conn, candidate.parent_run_id, **options)
    checked = read_run(conn, candidate.parent_run_id, candidate=candidate, **options)
    verify_run_correlation(candidate, original, checked)
    return verify_exported_trace(path, candidate, original, checked)
