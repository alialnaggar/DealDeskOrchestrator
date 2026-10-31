"""Bounded comparison of separate candidates over one frozen reader context."""

from dataclasses import asdict
import json

from phase1c_candidate import reader_input_digest, verify_run_correlation
from phase1c_candidate_trace import build_trace_record


MAX_CANDIDATES = 2  # First experiment, not an open-ended search loop.


def compare_candidate_set(conn, run_id, candidates, *, reader_kwargs=None):
    """Re-read each option independently; never choose or approve one automatically.

    The caller should use one REPEATABLE READ READ ONLY transaction against
    frozen evidence. The test fixture inserts its submission in a transaction
    first, then performs these reads without any additional database writes.
    """
    from phase1c_reader import read_run

    candidates = tuple(candidates)
    if not 1 <= len(candidates) <= MAX_CANDIDATES:
        raise ValueError("First experiment allows one or two candidates")
    if len({c.candidate_id for c in candidates}) != len(candidates):
        raise ValueError("Candidate IDs must be distinct")
    if any(str(c.parent_run_id) != str(run_id) for c in candidates):
        raise ValueError("Every candidate must refer to the same parent run")
    signatures = [json.dumps({"changes": asdict(c)["changes"],
                              "slices": asdict(c)["delivery_slices"]},
                             sort_keys=True, default=str) for c in candidates]
    if len(set(signatures)) != len(signatures):
        raise ValueError("Duplicate proposals must not be disguised as different candidates")
    options = dict(reader_kwargs or {})
    if "candidate" in options:
        raise ValueError("Reader options cannot supply another candidate")
    original = read_run(conn, run_id, **options)
    source_digest = reader_input_digest(original)
    records = []
    for candidate in candidates:
        checked = read_run(conn, run_id, candidate=candidate, **options)
        verify_run_correlation(candidate, original, checked)
        if checked["candidate_trace"]["source_input_digest"] != source_digest:
            raise ValueError("Candidates used different source snapshots")
        record = build_trace_record(candidate, original, checked)
        records.append(record)
    if len({r["payload"]["candidate_input_digest"] for r in records}) != len(records):
        raise ValueError("Candidate input fingerprints collided")
    return {
        "parent_run_id": str(run_id),
        "source_input_digest": source_digest,
        "candidate_records": records,
        "validated_supply_option_ids": [
            r["payload"]["candidate"]["candidate_id"] for r in records
            if r["payload"]["human_comparison"]["verified_supply_option"]],
        "selected_candidate_id": None,
        "note": "Human comparison only; customer acceptance and prescribed review remain open.",
    }
