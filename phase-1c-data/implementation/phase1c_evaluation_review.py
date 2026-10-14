"""Prepare and check reviewer-only drafts; never certify independent answers.

Completed draft findings still need substantive independent review and recorded
acceptance. Hash/pointer checks establish source identity, not answer correctness
or reviewer independence. This file never reads the authoring archetype map.
"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent / "evaluation"
RESPONSIBILITIES = ("Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval")
FINDINGS = {"no_issue_identified", "issue_identified", "evidence_needed",
            "human_review_required", "not_applicable"}
DECISIONS = {"blocked", "needs_revision", "needs_evidence", "needs_commitment", "approval_required"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def render(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_review_workspace(index):
    """Bind empty forms to pinned inputs without consulting any outcomes."""
    return {
        "schema_version": 1, "status": "review_workspace_not_released_answers",
        "answer_key_agent_visible": False, "independently_reviewed_answers": 0,
        "input_index_sha256": digest(index),
        "cases": [{
            "case_id": row["case_id"], "packet_sha256": row["packet_sha256"],
            "provider_file_sha256": row["provider_file_sha256"], "review_status": "pending",
            "reviewer": None,
            "findings": {role: {"finding": None, "evidence_refs": [], "rationale": None}
                         for role in RESPONSIBILITIES},
            "overall": {"decision_status": None, "human_actions": [],
                        "unresolved_questions": [], "rationale": None},
        } for row in index["cases"]],
    }


def resolve_pointer(document, pointer):
    """Resolve a strict JSON pointer; no external paths or executable content."""
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("JSON pointer must start with /")
    current = document
    for raw in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw):
            raise ValueError("Invalid JSON pointer escape")
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                raise ValueError("Invalid array index")
            try:
                current = current[int(part)]
            except IndexError as exc:
                raise ValueError("JSON pointer does not resolve") from exc
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise ValueError("JSON pointer does not resolve")
    return current


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _texts(value, *, nonempty=False):
    return isinstance(value, list) and (bool(value) or not nonempty) and all(_text(x) for x in value)


def validate_review_workspace(workspace, index, *, packet_directory=None):
    errors, pending, complete = [], 0, 0
    template = build_review_workspace(index)
    if not isinstance(workspace, dict) or set(workspace) != set(template):
        return {"errors": ["Review workspace fields differ"], "pending_cases": 0,
                "complete_draft_cases": 0, "independently_reviewed_answers": 0}
    for field in ("schema_version", "status", "answer_key_agent_visible",
                  "independently_reviewed_answers", "input_index_sha256"):
        if type(workspace[field]) is not type(template[field]) or workspace[field] != template[field]:
            errors.append(f"Workspace {field} differs; drafts cannot certify independent review")
    cases = workspace["cases"]
    if not isinstance(cases, list) or len(cases) != len(template["cases"]):
        errors.append("Review case count differs from pinned index")
        cases = cases if isinstance(cases, list) else []
    indexed = {row["case_id"]: row for row in template["cases"]}
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != set(template["cases"][0]):
            errors.append("Review case fields differ")
            continue
        cid = case["case_id"]
        if not isinstance(cid, str) or cid not in indexed or cid in seen:
            errors.append("Unknown or duplicate review case ID")
            continue
        seen.add(cid)
        blank = indexed[cid]
        before = len(errors)
        for field in ("packet_sha256", "provider_file_sha256"):
            if case[field] != blank[field]:
                errors.append(f"{cid}: pinned source hash differs")
        if case["review_status"] == "pending":
            pending += 1
            if case != blank:
                errors.append(f"{cid}: pending form contains findings or reviewer claims")
            continue
        if case["review_status"] != "draft_complete":
            errors.append(f"{cid}: only pending or draft_complete is accepted; review acceptance is separate")
            continue
        reviewer = case["reviewer"]
        if (not isinstance(reviewer, dict)
                or set(reviewer) != {"identity", "method", "reviewed_at", "independence_statement"}
                or not _text(reviewer.get("identity"))
                or reviewer.get("method") not in ("human", "model", "model_assisted")
                or not _text(reviewer.get("independence_statement"))):
            errors.append(f"{cid}: reviewer provenance is incomplete")
        try:
            stamp = datetime.fromisoformat(reviewer["reviewed_at"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("Timezone required")
        except (TypeError, KeyError, AttributeError, ValueError):
            errors.append(f"{cid}: dated reviewer provenance requires a timezone")
        sources = {}
        if packet_directory is None:
            errors.append(f"{cid}: completed drafts require the pinned packet/provider files")
        else:
            folder = Path(packet_directory)
            try:
                packet = json.loads((folder / (cid + ".json")).read_text())
                provider_bytes = (folder / (cid + "-provider.json")).read_bytes()
                if (packet.get("sha256") != blank["packet_sha256"]
                        or digest(packet["payload"]) != blank["packet_sha256"]
                        or hashlib.sha256(provider_bytes).hexdigest() != blank["provider_file_sha256"]):
                    raise ValueError("Pinned source hash differs")
                sources = {"packet": packet["payload"], "provider": json.loads(provider_bytes)}
            except (OSError, ValueError, KeyError, TypeError):
                errors.append(f"{cid}: source files missing, malformed or changed")
        findings = case["findings"]
        if not isinstance(findings, dict) or set(findings) != set(RESPONSIBILITIES):
            errors.append(f"{cid}: all six responsibility findings are required")
            findings = {}
        for role, finding in findings.items():
            if (not isinstance(finding, dict)
                    or set(finding) != {"finding", "evidence_refs", "rationale"}
                    or not isinstance(finding.get("finding"), str)
                    or finding.get("finding") not in FINDINGS
                    or not _text(finding.get("rationale"))):
                errors.append(f"{cid}/{role}: finding and rationale are required")
                continue
            refs = finding["evidence_refs"]
            if not isinstance(refs, list) or not refs:
                errors.append(f"{cid}/{role}: at least one source reference is required")
                continue
            for ref in refs:
                if (not isinstance(ref, dict) or set(ref) != {"document", "pointer"}
                        or ref.get("document") not in ("packet", "provider")
                        or not isinstance(ref.get("pointer"), str)):
                    errors.append(f"{cid}/{role}: malformed source reference")
                    continue
                pointer = ref["pointer"]
                permitted = ((ref["document"] == "packet" and
                              (pointer.startswith("/source_rows/") or pointer.startswith("/run_context/") or pointer.startswith("/business_contract/")))
                             or (ref["document"] == "provider" and
                                 (pointer == "/records" or pointer.startswith("/records/"))))
                try:
                    if not permitted or ref["document"] not in sources:
                        raise ValueError("Reference is outside source facts")
                    resolve_pointer(sources[ref["document"]], pointer)
                except ValueError:
                    errors.append(f"{cid}/{role}: source reference does not resolve in pinned facts")
        overall = case["overall"]
        if (not isinstance(overall, dict) or set(overall) != set(blank["overall"])
                or not isinstance(overall.get("decision_status"), str)
                or overall.get("decision_status") not in DECISIONS
                or not _texts(overall.get("human_actions"), nonempty=True)
                or not _texts(overall.get("unresolved_questions"))
                or not _text(overall.get("rationale"))):
            errors.append(f"{cid}: overall finding, rationale and human actions are required; approval is not an output")
        if len(errors) == before:
            complete += 1
    if seen != set(indexed):
        errors.append("Review case identities differ from pinned index")
    return {"errors": errors, "pending_cases": pending, "complete_draft_cases": complete,
            "independently_reviewed_answers": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write-template", action="store_true")
    action.add_argument("--check-template", action="store_true")
    action.add_argument("--review-file", type=Path)
    parser.add_argument("--packet-directory", type=Path)
    parser.add_argument("--index", type=Path, default=EVALUATION / "provisional_packet_index.json")
    args = parser.parse_args()
    index = json.loads(args.index.read_text())
    template_path = EVALUATION / "provisional_review_template.json"
    expected = render(build_review_workspace(index))
    if args.write_template:
        template_path.write_text(expected)
    if args.check_template and template_path.read_text() != expected:
        raise SystemExit("Review template differs from pinned input index")
    workspace = json.loads(args.review_file.read_text() if args.review_file else expected)
    report = validate_review_workspace(workspace, index, packet_directory=args.packet_directory)
    print(render(report), end="")
    raise SystemExit(bool(report["errors"]))


if __name__ == "__main__":
    main()
