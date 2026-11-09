"""Read-only Phase 1C reviewer-intake gate and conservative evaluation report.

Never imports the demo runner, calls a provider, writes answers or creates a register.
Run from a separately checked-out Phase 1C review tree; never from prompt/tool code.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

PIN = "7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc"
ROLES = ("Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval")
FINDINGS = {"no_issue_identified", "issue_identified", "evidence_needed",
            "human_review_required", "not_applicable"}
GATES = {"blocked", "needs_revision", "needs_evidence", "needs_commitment", "approval_required"}
ROOT = Path(__file__).resolve().parents[1]


def load_contract(review_root):
    """Load the authoritative Phase 1C source-review + intake validators, not a copy."""
    impl = review_root / "phase-1c-data" / "implementation"
    if not (impl / "phase1c_evaluation_acceptance.py").is_file():
        raise ValueError("Phase 1C review checkout lacks the authoritative intake validator")
    sys.dont_write_bytecode = True  # never create artefacts inside a source/review checkout
    sys.path.insert(0, str(impl))
    from phase1c_evaluation_acceptance import (check_v2_index, empty_intake, validate_intake)
    from phase1c_evaluation_review import validate_review_workspace, digest
    return check_v2_index, empty_intake, validate_intake, validate_review_workspace, digest


def check_transition(current, previous, index):
    """Acceptance needs a preserved, source-bound reviewed predecessor; no auto-promotion."""
    expected = {row["case_id"] for row in index["cases"]}
    if previous is None:
        if any(row.get("disposition") != "pending" for row in current["cases"]):
            raise ValueError("Non-pending intake requires a prior validated intake snapshot")
        return
    before = {row["case_id"]: row for row in previous["cases"]}
    after = {row["case_id"]: row for row in current["cases"]}
    if set(before) != expected or set(after) != expected:
        raise ValueError("Prior/current case membership differs")
    allowed = {"pending": {"pending", "reviewed_pending_disposition"},
               "reviewed_pending_disposition": {"reviewed_pending_disposition", "accepted", "rejected"},
               "accepted": {"accepted"}, "rejected": {"rejected"}}
    for cid in expected:
        old, new = before[cid], after[cid]
        if new["disposition"] not in allowed.get(old["disposition"], set()):
            raise ValueError(f"{cid}: unauthorized disposition transition")
        if old["disposition"] in ("accepted", "rejected") and old != new:
            raise ValueError(f"{cid}: terminal decision changed; version a new review instead")
        if old["disposition"] == "reviewed_pending_disposition" and new["disposition"] in ("accepted", "rejected"):
            if old["source_review_case_sha256"] != new["source_review_case_sha256"]:
                raise ValueError(f"{cid}: source review changed during disposition")


def check_prompt_boundary(paths, index, private_files):
    """Conservative local leakage scan, not proof about remote prompts or earlier sends."""
    ids = {row["case_id"] for row in index["cases"]}
    ids_pattern = re.compile(r"\bEVAL-PREP-0(?:0[1-9]|[12][0-9]|3[0-6])\b")
    for root in paths:
        if not root.is_dir():
            raise ValueError(f"Prompt/model search directory absent: {root}")
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".json", ".md", ".ts", ".tsx"}:
                continue
            if any(parent in {"node_modules", ".git", "__pycache__"} for parent in path.parts):
                continue
            if any(path.resolve() == private.resolve() for private in private_files if private):
                raise ValueError("Reviewer answer file located in model-visible directory")
            text = path.read_text(errors="replace")
            if any(match.group() in ids for match in ids_pattern.finditer(text)):
                raise ValueError(f"Held-out case ID present in model-visible tree: {path}")


def _unique(rows, expected, label):
    if not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get("case_id"), str) for row in rows):
        raise ValueError(f"{label}: invalid rows")
    ids = [row["case_id"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError(f"{label}: duplicate, missing or unexpected case IDs")


def _validated_intake(value, index, review_bytes, packets, validate_intake):
    result = validate_intake(value, index, review_bytes=review_bytes, packet_directory=packets)
    if result["errors"]:
        raise ValueError("Phase 1C intake invalid: " + "; ".join(result["errors"]))
    return result


def report(index, workspace, intake, intake_report, run=None):
    """Aggregate only scored accepted cases from genuinely measured runs; no example scores."""
    expected = {row["case_id"] for row in index["cases"]}
    _unique(intake["cases"], expected, "intake")
    _unique(workspace["cases"], expected, "workspace")
    accepted = {row["case_id"] for row in intake["cases"] if row["disposition"] == "accepted"}
    if len(accepted) != intake_report["recorded_acceptances"]:
        raise ValueError("Acceptance count differs from authoritative intake validator")
    counts = Counter(row["disposition"] for row in intake["cases"])
    result = {"schema_version": 1, "reference_status": "structurally_validated_not_independence_certified",
              "dataset_version": {"phase1c_index_sha256": PIN, "case_count": len(expected)},
              "review": {"accepted": len(accepted), "reviewed_pending": counts["reviewed_pending_disposition"],
                         "pending": counts["pending"], "rejected": counts["rejected"],
                         "excluded_from_scoring": len(expected) - len(accepted)},
              "run": None, "metrics": {"specialist_agreement": None, "business_gate_agreement": None,
                        "coverage": None, "false_clearance": None, "citation_validity": None,
                        "deterministic_verification_correctness": None, "workflow_completion": None,
                        "latency": None, "tokens": None, "cost": None},
              "unavailable": ["independent-review certification", "specialist accuracy",
                              "business-gate accuracy", "semantic citation correctness",
                              "deterministic verification correctness", "measured runtime/resource usage"]}
    if run is None:
        return result
    required = {"mode", "model_version", "prompt_contract", "dataset_index_sha256",
                "phase2_commit", "campaign_id", "cases"}
    if not isinstance(run, dict) or set(run) != required or any(not isinstance(run[k], str) or not run[k].strip() for k in required - {"cases"}):
        raise ValueError("Run provenance incomplete")
    if run["dataset_index_sha256"] != PIN or run["mode"] not in ("genuine_ai", "offline_scripted"):
        raise ValueError("Wrong dataset pin or unsupported execution mode")
    _unique(run["cases"], expected, "run")
    if any(row.get("status") not in {"completed", "abstained", "failed", "skipped"} for row in run["cases"]):
        raise ValueError("Unknown workflow status")
    result["run"] = {key: run[key] for key in required - {"cases"}}
    by_run = {row["case_id"]: row for row in run["cases"]}
    result["run"]["status_counts"] = dict(sorted(Counter(row["status"] for row in run["cases"]).items()))
    if not accepted or run["mode"] == "offline_scripted":
        result["run"]["scoring"] = "unavailable: no accepted references or offline scripted mode"
        return result
    refs = {row["case_id"]: row for row in workspace["cases"]}
    for cid in accepted:
        if refs[cid]["review_status"] != "draft_complete":
            raise ValueError(f"{cid}: accepted source review missing")
    agreements = {}
    for role in ROLES:
        numerator = denominator = 0
        for cid in accepted:
            case = by_run[cid]
            if case["status"] != "completed":
                continue
            findings = case.get("findings")
            if not isinstance(findings, dict) or set(findings) != set(ROLES) or any(x not in FINDINGS for x in findings.values()):
                raise ValueError(f"{cid}: incomplete/invalid specialist findings")
            denominator += 1
            numerator += findings[role] == refs[cid]["findings"][role]["finding"]
        agreements[role] = {"matching": numerator, "scored": denominator, "rate": numerator / denominator if denominator else None}
    completed = {cid for cid in accepted if by_run[cid]["status"] == "completed"}
    gates = [cid for cid in completed if by_run[cid].get("overall") in GATES]
    if len(gates) != len(completed):
        raise ValueError("Completed run lacks a valid overall gate")
    same = sum(by_run[cid]["overall"] == refs[cid]["overall"]["decision_status"] for cid in gates)
    blockers = [cid for cid in gates if refs[cid]["overall"]["decision_status"] == "blocked"]
    false = sum(by_run[cid]["overall"] == "approval_required" for cid in blockers)
    result["metrics"].update({
        "specialist_agreement": agreements,
        "business_gate_agreement": {"matching": same, "scored": len(gates), "rate": same / len(gates) if gates else None},
        "coverage": {"completed": len(completed), "accepted": len(accepted), "scheduled": len(expected)},
        "false_clearance": {"count": false, "reference_blocked_completed": len(blockers),
                            "rate": false / len(blockers) if blockers else None},
        "workflow_completion": {"completed": sum(r["status"] == "completed" for r in run["cases"]),
                                "scheduled": len(expected), "failures": sum(r["status"] == "failed" for r in run["cases"]),
                                "abstentions": sum(r["status"] == "abstained" for r in run["cases"])}})
    result["unavailable"] = [x for x in result["unavailable"] if x not in ("specialist accuracy", "business-gate accuracy")]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", required=True, type=Path, help="separate Phase 1C checkout with authoritative intake code")
    parser.add_argument("--intake", type=Path, help="reviewer-only existing Phase 1C disposition file; omit to inspect blank authoritative intake")
    parser.add_argument("--prior-intake", type=Path, help="previous preserved disposition file, required for any transition")
    parser.add_argument("--review-file", type=Path, help="source-first review bytes required for any non-pending disposition")
    parser.add_argument("--packet-directory", type=Path, help="exported SHA-bound packet/provider pair directory for reviewed cases")
    parser.add_argument("--run", type=Path, help="separate prospective run record (never a historical demo trace)")
    parser.add_argument("--prompt-root", type=Path, action="append", default=[], help="model-visible source directory to scan for held-out IDs")
    args = parser.parse_args()
    try:
        review_root = args.review_root.resolve(strict=True)
        commit = subprocess.check_output(["git", "-C", str(review_root), "rev-parse", "HEAD"], text=True).strip()
        check_index, empty, validate, validate_workspace, digest = load_contract(review_root)
        index = json.loads((review_root / "phase-1c-data/evaluation/provisional_packet_index.json").read_text())
        check_index(index)
        if digest(index) != PIN or index.get("independently_reviewed_answers") != 0:
            raise ValueError("Unrecognized evaluation index or index claims accepted answers")
        workspace_path = args.review_file or review_root / "phase-1c-data/evaluation/provisional_review_template.json"
        workspace_bytes = workspace_path.read_bytes()
        workspace = json.loads(workspace_bytes)
        workspace_report = validate_workspace(workspace, index, packet_directory=args.packet_directory)
        if workspace_report["errors"]:
            raise ValueError("Source-first workspace invalid: " + "; ".join(workspace_report["errors"]))
        intake = json.loads(args.intake.read_text()) if args.intake else empty(index)
        prior = json.loads(args.prior_intake.read_text()) if args.prior_intake else None
        intake_report = _validated_intake(intake, index, workspace_bytes if args.review_file else None,
                                          args.packet_directory, validate)
        if prior is not None:
            _validated_intake(prior, index, workspace_bytes if args.review_file else None,
                              args.packet_directory, validate)
        check_transition(intake, prior, index)
        roots = args.prompt_root or [ROOT / "backend/dealdesk_phase2", ROOT / "frontend/app", ROOT / "frontend/lib"]
        check_prompt_boundary(roots, index, [args.intake, args.prior_intake, args.review_file])
        output = report(index, workspace, intake, intake_report, json.loads(args.run.read_text()) if args.run else None)
        output["dataset_version"]["review_checkout_commit"] = commit
        output["review"]["source_first_complete_drafts"] = workspace_report["complete_draft_cases"]
        print(json.dumps(output, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"D8 validation refused: {exc}\n")


if __name__ == "__main__":
    main()
