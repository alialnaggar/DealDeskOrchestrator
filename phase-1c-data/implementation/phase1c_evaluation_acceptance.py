"""Reviewer-only disposition intake, not an independent-answer certificate.

The tracked source index and a source-first human review bind each disposition.
Structural checks cannot prove a person's identity, independence, reasoning or
business correctness. Never place completed intake or reviewer answers in an
agent-visible packet directory or publish a score from this report alone.
"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

from phase1c_evaluation_review import (EVALUATION, digest, render,
                                       validate_review_workspace)


def empty_intake(index):
    """Create a blank, hash-bound register without reading answer drafts."""
    return {
        "schema_version": 1,
        "status": "reviewer_only_intake_not_released_answers",
        "answer_key_agent_visible": False,
        "ready_for_generation": False,
        "input_index_sha256": digest(index),
        "source_review_file_sha256": None,
        "cases": [{
            "case_id": row["case_id"],
            "packet_sha256": row["packet_sha256"],
            "provider_file_sha256": row["provider_file_sha256"],
            "disposition": "pending",
            "source_review_case_sha256": None,
            "adjudicator": None,
            "reason": None,
            "draft_comparison_and_assistance": None,
        } for row in index["cases"]],
    }


def bind_source_review(index, review_bytes, packet_directory):
    """Bind completed human drafts for later disposition; accept none."""
    workspace = json.loads(review_bytes)
    report = validate_review_workspace(workspace, index, packet_directory=packet_directory)
    if report["errors"]:
        raise ValueError("Source review invalid: " + "; ".join(report["errors"]))
    intake = empty_intake(index)
    by_id = {case["case_id"]: case for case in workspace["cases"]}
    found = 0
    for row in intake["cases"]:
        case = by_id[row["case_id"]]
        if case["review_status"] == "draft_complete":
            if case["reviewer"]["method"] != "human":
                raise ValueError(f"{row['case_id']}: source-first review must be human")
            row["disposition"] = "reviewed_pending_disposition"
            row["source_review_case_sha256"] = digest(case)
            found += 1
    if not found:
        raise ValueError("No completed human case review to bind")
    intake["source_review_file_sha256"] = hashlib.sha256(review_bytes).hexdigest()
    return intake


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _dated(value):
    if not _text(value):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp if stamp.tzinfo is not None else None
    except ValueError:
        return None


def validate_intake(intake, index, *, review_bytes=None, packet_directory=None):
    """Check identity, human provenance and a complete source-bound draft.

    `recorded_acceptances` is an attested-form count, never a correctness or
    independent-review certification. The release count stays a human gate.
    """
    blank = empty_intake(index)
    errors = []
    report = {"errors": errors, "pending_cases": 0, "reviewed_pending_cases": 0,
              "recorded_acceptances": 0, "recorded_rejections": 0,
              "independence_or_correctness_certified": False}
    if not isinstance(intake, dict) or set(intake) != set(blank):
        errors.append("Intake fields differ")
        return report
    for field in ("schema_version", "status", "answer_key_agent_visible",
                  "ready_for_generation", "input_index_sha256"):
        if type(intake[field]) is not type(blank[field]) or intake[field] != blank[field]:
            errors.append(f"Intake {field} differs")
    rows = intake["cases"]
    if not isinstance(rows, list) or len(rows) != len(blank["cases"]):
        errors.append("Case count differs from pinned index")
        rows = rows if isinstance(rows, list) else []
    expected = {row["case_id"]: row for row in blank["cases"]}
    seen = set()
    active = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(blank["cases"][0]):
            errors.append("Case fields differ")
            continue
        cid = row["case_id"]
        if not isinstance(cid, str) or cid not in expected or cid in seen:
            errors.append("Unknown or duplicate case identity")
            continue
        seen.add(cid)
        if any(row[k] != expected[cid][k] for k in ("packet_sha256", "provider_file_sha256")):
            errors.append(f"{cid}: source pin differs")
        if row["disposition"] == "pending":
            report["pending_cases"] += 1
            if row != expected[cid]:
                errors.append(f"{cid}: pending record contains a decision or provenance")
        elif row["disposition"] in ("reviewed_pending_disposition", "accepted", "rejected"):
            active.append(row)
        else:
            errors.append(f"{cid}: unsupported disposition")
    if seen != set(expected):
        errors.append("Case identities differ from pinned index")
    if not active:
        if intake["source_review_file_sha256"] is not None:
            errors.append("Pending register must not claim a reviewed file")
        return report

    if not isinstance(review_bytes, bytes) or not packet_directory:
        errors.append("Recorded dispositions require exact source-review bytes and pinned packet files")
        return report
    if hashlib.sha256(review_bytes).hexdigest() != intake["source_review_file_sha256"]:
        errors.append("Source-review file bytes do not match intake pin")
        return report
    try:
        workspace = json.loads(review_bytes)
    except (UnicodeDecodeError, ValueError):
        errors.append("Source-review file is invalid JSON")
        return report
    source_report = validate_review_workspace(workspace, index, packet_directory=packet_directory)
    if source_report["errors"]:
        errors.extend(f"Source review: {error}" for error in source_report["errors"])
        return report
    by_id = {case["case_id"]: case for case in workspace["cases"]}
    for row in active:
        cid = row["case_id"]
        case = by_id[cid]
        if case["review_status"] != "draft_complete" or row["source_review_case_sha256"] != digest(case):
            errors.append(f"{cid}: completed source-first case or its digest differs")
            continue
        reviewer = case["reviewer"]
        adjudicator = row["adjudicator"]
        if reviewer["method"] != "human":
            errors.append(f"{cid}: model or model-assisted draft cannot be accepted as a source-first human review")
        if row["disposition"] == "reviewed_pending_disposition":
            if adjudicator is not None or row["reason"] is not None or row["draft_comparison_and_assistance"] is not None:
                errors.append(f"{cid}: reviewed but undispositioned case contains a decision")
            if not any(error.startswith(f"{cid}:") for error in errors):
                report["reviewed_pending_cases"] += 1
            continue
        if (not isinstance(adjudicator, dict)
                or set(adjudicator) != {"identity", "method", "decided_at", "source_first_attestation"}
                or not _text(adjudicator.get("identity"))
                or adjudicator.get("method") != "human"
                or not _text(adjudicator.get("source_first_attestation"))):
            errors.append(f"{cid}: accountable human adjudicator provenance is incomplete")
        else:
            decided = _dated(adjudicator["decided_at"])
            reviewed = _dated(reviewer["reviewed_at"])
            if decided is None or reviewed is None or decided < reviewed:
                errors.append(f"{cid}: disposition must follow timezone-aware source review")
        if not _text(row["reason"]) or not _text(row["draft_comparison_and_assistance"]):
            errors.append(f"{cid}: case reasoning and model/author assistance disclosure required")
        if not any(error.startswith(f"{cid}:") for error in errors):
            key = "recorded_acceptances" if row["disposition"] == "accepted" else "recorded_rejections"
            report[key] += 1
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-empty", action="store_true")
    action.add_argument("--write-empty", type=Path)
    action.add_argument("--bind-review", type=Path)
    action.add_argument("--intake", type=Path)
    parser.add_argument("--index", type=Path, default=EVALUATION / "provisional_packet_index.json")
    parser.add_argument("--review-file", type=Path)
    parser.add_argument("--packet-directory", type=Path)
    args = parser.parse_args()
    index = json.loads(args.index.read_text())
    review_bytes = args.review_file.read_bytes() if args.review_file else None
    if args.write_empty:
        args.write_empty.write_text(render(empty_intake(index)))
    if args.bind_review:
        if review_bytes is None or args.packet_directory is None:
            parser.error("--bind-review requires --review-file and --packet-directory")
        intake = bind_source_review(index, review_bytes, args.packet_directory)
    else:
        intake = json.loads(args.intake.read_text()) if args.intake else empty_intake(index)
    report = validate_intake(intake, index, review_bytes=review_bytes,
                             packet_directory=args.packet_directory)
    if args.check_empty and (report["pending_cases"] != 36 or report["recorded_acceptances"] != 0):
        report["errors"].append("Expected 36 blank cases and no acceptance")
    if args.bind_review and not report["errors"]:
        args.bind_review.write_text(render(intake))
    print(render(report), end="")
    raise SystemExit(bool(report["errors"]))


if __name__ == "__main__":
    main()
