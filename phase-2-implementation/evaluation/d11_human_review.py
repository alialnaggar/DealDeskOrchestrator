"""Private source-first human pilot: prepare, check, freeze, verify, then unlock.

No command accepts a reference answer or establishes human independence.
Only source documents and blank forms are copied into the blind workspace.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil

import d9_review_prep as d9
import d10_private_dossier_check as d10

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESTRICTED_AI_DIR = Path("/tmp/opencode/d10_private_pilot_2026-11-09")
BLANK = HERE / "supervisor-demo-d9-pilot-blank.json"
BLANK_SHA256 = "9dbbac09aab44009b16ebd157c023d4c909c2a72233f9fd7a7f171ea6d568fce"
IDS = tuple(f"EVAL-PREP-{n:03d}" for n in d9.PILOT)
ROLES = d10.SPECIALISTS
CODES = {"no_issue_identified", "issue_identified", "evidence_needed", "human_review_required", "not_applicable"}
GATES = {"blocked", "needs_revision", "needs_evidence", "needs_commitment", "approval_required"}
DOCUMENTS = {"packet", "provider", "scope"}


def refuse(message):
    raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(value):
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if t.tzinfo is None or t.utcoffset() is None:
            raise ValueError("timezone missing")
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("reviewed_at requires an ISO-8601 timezone-aware date") from exc


def text(value):
    return isinstance(value, str) and bool(value.strip())


def private_new(path):
    path = path.absolute()
    if (path.resolve().is_relative_to(REPO) or path.resolve().is_relative_to(RESTRICTED_AI_DIR)
            or path.is_relative_to(REPO) or path.is_relative_to(RESTRICTED_AI_DIR)):
        refuse("Private output must be outside Git/development trees")
    if path.exists() or path.is_symlink():
        refuse("Output already exists; never overwrite or mix first passes")
    if not path.parent.is_dir() or path.parent.is_symlink():
        refuse("Create an authorized private parent directory first")
    if path.parent.stat().st_mode & 0o077:
        refuse("Private parent must not be readable by group/others")
    path.mkdir(mode=0o700)
    return path


def private_existing(path):
    path = path.absolute()
    if (path.resolve().is_relative_to(REPO) or path.resolve().is_relative_to(RESTRICTED_AI_DIR)
            or not path.is_dir() or path.is_symlink() or path.stat().st_mode & 0o077):
        refuse("Review workspace must be a private directory outside Git")


def write_new(path, value):
    data = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b"\n"
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def blank_case(row, scope_sha):
    return {
        "case_id": row["case_id"], "packet_sha256": row["packet_sha256"],
        "provider_file_sha256": row["provider_file_sha256"],
        "credit_scope_sha256": scope_sha,
        "review_state": "blank",
        "credit_scope": {"use": None, "rationale": None, "citations": []},
        "findings": {role: {"code": None, "rationale": None, "calculations": None,
                            "uncertainty": None, "citations": [], "rule_ids": []} for role in ROLES},
        "overall": {"status": None, "gate": None, "rationale": None, "calculations": None,
                    "uncertainty": None, "human_actions": [], "citations": [], "rule_ids": [],
                    "conditional_interpretations": [], "methodology_question": None},
    }


def template(index, scope_pins):
    rows = {r["case_id"]: r for r in index["cases"]}
    return {"schema_version": 1, "status": "human_first_pass_private_not_accepted",
            "index_sha256": d9.d8.PIN,
            "reviewer": {"identity": None, "role": None, "reviewed_at": None,
                         "source_first_attestation": False, "prior_ai_answer_exposure": None,
                         "ai_assistance_used": None, "assistance_details": None,
                         "independence_limitations": None},
            "cases": [blank_case(rows[cid], scope_pins[cid]["scope_sha256"]) for cid in IDS]}


def checked_sources(root, packets=None):
    index, pins, state, _ = d9.load_sources(root, packets)
    if packets is not None and any(not state[cid].startswith("verified:") for cid in IDS):
        refuse("Pilot sources are missing/unverified")
    if sha(BLANK) != BLANK_SHA256:
        refuse("D9 blinded blank workspace changed")
    pilot = json.loads(BLANK.read_text())
    if [c["case_id"] for c in pilot["cases"]] != list(IDS) or any(
            c["review_status"] != "pending" or c["reviewer"] is not None for c in pilot["cases"]):
        refuse("D9 workspace is not blank")
    scopes = {r["case_id"]: r for r in json.loads((root / "phase-1c-data/evaluation/credit-evidence-v3/credit_scope_v3.json").read_text())["cases"]}
    return index, pins, scopes


def prepare(root, packets, destination):
    index, pins, scopes = checked_sources(root, packets)
    # No AI dossier or answer-shaped input is read by this code path.
    destination = private_new(destination)
    source = destination / "sources"
    source.mkdir(mode=0o700)
    for cid in IDS:
        target = source / cid
        target.mkdir(mode=0o700)
        for name in (f"{cid}.json", f"{cid}-provider.json"):
            with open(packets / name, "rb") as stream:
                fd = os.open(target / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, "wb") as out:
                    shutil.copyfileobj(stream, out)
        write_new(target / "credit_scope.json", scopes[cid])
    # Recheck copied bytes and each scope row without relying on the original files.
    rows = {r["case_id"]: r for r in index["cases"]}
    digest = d9.d8.load_contract(root)[4]
    for cid in IDS:
        target = source / cid
        packet = json.loads((target / f"{cid}.json").read_text())
        if (packet.get("sha256") != rows[cid]["packet_sha256"] or
                digest(packet["payload"]) != rows[cid]["packet_sha256"] or
                sha(target / f"{cid}-provider.json") != rows[cid]["provider_file_sha256"] or
                digest(json.loads((target / "credit_scope.json").read_text())) != pins[cid]["scope_sha256"]):
            refuse("Copied source changed")
        for file in target.iterdir():
            if any(marker in file.read_text().lower() for marker in d9.FORBIDDEN_BLIND_MARKERS):
                refuse("Blinded source contains model/answer marker; stop delivery")
    write_new(destination / "first_pass.json", template(index, pins))
    return {"blank_cases": 6, "verified_source_pairs": 6, "status": "private_blank_first_pass_only"}


def refs(value, documents, *, required=True):
    if not isinstance(value, list) or (required and not value):
        refuse("Citations missing")
    for ref in value:
        if not isinstance(ref, dict) or set(ref) != {"document", "pointer"} or ref["document"] not in DOCUMENTS:
            refuse("Malformed citation")
        pointer = ref["pointer"]
        permitted = ((ref["document"] == "packet" and pointer.startswith(("/source_rows/", "/run_context/", "/business_contract/")))
                     or (ref["document"] == "provider" and (pointer == "/records" or pointer.startswith("/records/")))
                     or (ref["document"] == "scope" and pointer.startswith(("/credit_evidence_scope/", "/customer_id", "/case_id", "/as_of_at", "/base_packet_sha256", "/base_provider_file_sha256"))))
        if not permitted:
            refuse("Citation outside pinned source facts")
        try:
            d10.follow(documents[ref["document"]], pointer)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError("Citation does not resolve") from exc


def rules(value, known):
    if not isinstance(value, list) or not value or len(value) != len(set(value)) or any(x not in known for x in value):
        refuse("Missing, duplicate or unknown rule identifier")


def validate(form, root, workspace, *, require_complete=False):
    private_existing(workspace)
    index, pins, scopes = checked_sources(root)
    blank = template(index, pins)
    if not isinstance(form, dict) or set(form) != set(blank) or any(form[k] != blank[k] for k in ("schema_version", "status", "index_sha256")):
        refuse("Form schema/status differs; cannot claim accepted/reviewed")
    cases = form["cases"]
    if not isinstance(cases, list) or len(cases) != 6 or [c.get("case_id") for c in cases if isinstance(c, dict)] != list(IDS):
        refuse("Missing, duplicate or reordered case IDs")
    reviewer = form["reviewer"]
    if not isinstance(reviewer, dict) or set(reviewer) != set(blank["reviewer"]):
        refuse("Reviewer metadata fields differ")
    completed = sum(c.get("review_state") == "draft_complete" for c in cases)
    if require_complete or completed:
        for field in ("identity", "role", "assistance_details", "independence_limitations"):
            if not text(reviewer[field]):
                refuse("Reviewer identity, role and assistance/independence disclosures required")
        stamp(reviewer["reviewed_at"])
        if (reviewer["source_first_attestation"] is not True or
                type(reviewer["prior_ai_answer_exposure"]) is not bool or
                type(reviewer["ai_assistance_used"]) is not bool):
            refuse("Explicit source-first attestation and prior-exposure/assistance disclosures required")
    rows = {r["case_id"]: r for r in index["cases"]}
    for case, empty in zip(cases, blank["cases"]):
        cid = case["case_id"]
        if not isinstance(case, dict) or set(case) != set(empty) or any(case[k] != empty[k] for k in ("case_id", "packet_sha256", "provider_file_sha256", "credit_scope_sha256")):
            refuse("Case schema or pinned source hashes differ")
        folder = workspace / "sources" / cid
        packet = json.loads((folder / f"{cid}.json").read_text())
        provider_file = folder / f"{cid}-provider.json"
        scope = json.loads((folder / "credit_scope.json").read_text())
        digest = d9.d8.load_contract(root)[4]
        if (packet["sha256"] != rows[cid]["packet_sha256"] or digest(packet["payload"]) != rows[cid]["packet_sha256"] or
                sha(provider_file) != rows[cid]["provider_file_sha256"] or digest(scope) != pins[cid]["scope_sha256"] or
                any(scope[k] != packet["payload"][k] for k in ("case_id",)) or
                scope["customer_id"] != packet["payload"]["source_rows"]["deal"]["customer_id"] or
                scope["as_of_at"] != packet["payload"]["run_context"]["as_of_at"] or
                scope["base_packet_sha256"] != case["packet_sha256"] or
                scope["base_provider_file_sha256"] != case["provider_file_sha256"]):
            refuse("Copied source or Credit scope identity/hash differs")
        if case["review_state"] == "blank":
            if case != empty or require_complete:
                refuse("Blank case changed or incomplete first pass")
            continue
        if case["review_state"] != "draft_complete":
            refuse("Only draft_complete is permitted; no acceptance transition")
        documents = {"packet": packet["payload"], "provider": json.loads(provider_file.read_text()), "scope": scope}
        known = {r.get("pricing_rule_id", r.get("policy_rule_id", r.get("approval_rule_id")))
                 for group in packet["payload"]["source_rows"]["rules"].values() for r in group}
        credit = case["credit_scope"]
        if (not isinstance(credit, dict) or set(credit) != set(empty["credit_scope"]) or
                credit["use"] not in ("conditional", "not_adopted", "unresolved") or not text(credit["rationale"])):
            refuse("Credit completeness position must be explicit and conditional")
        refs(credit["citations"], documents)
        if not any(r["document"] == "scope" and r["pointer"].startswith("/credit_evidence_scope/") for r in credit["citations"]):
            refuse("Credit scope must cite the separate v3 declaration")
        findings = case["findings"]
        if not isinstance(findings, dict) or set(findings) != set(ROLES):
            refuse("Six specialist findings required")
        for role, finding in findings.items():
            if (not isinstance(finding, dict) or set(finding) != set(empty["findings"][role]) or
                    finding["code"] not in CODES or any(not text(finding[k]) for k in ("rationale", "calculations", "uncertainty"))):
                refuse("Finding/code/calculation/rationale/uncertainty incomplete")
            refs(finding["citations"], documents)
            rules(finding["rule_ids"], known)
        overall = case["overall"]
        if (not isinstance(overall, dict) or set(overall) != set(empty["overall"]) or
                overall["status"] not in ("proposed", "deferred") or
                (overall["gate"] not in GATES if overall["status"] == "proposed" else overall["gate"] is not None) or
                any(not text(overall[k]) for k in ("rationale", "calculations", "uncertainty", "methodology_question")) or
                not isinstance(overall["human_actions"], list) or not overall["human_actions"] or
                any(not text(x) for x in overall["human_actions"])):
            refuse("Overall gate/deferral, rationale, uncertainty, method question and actions required")
        refs(overall["citations"], documents)
        rules(overall["rule_ids"], known)
        routes = overall["conditional_interpretations"]
        if not isinstance(routes, list) or (cid == "EVAL-PREP-020" and len(routes) < 2):
            refuse("020 requires at least two explicit conditional interpretations")
        if cid == "EVAL-PREP-020" and len({r.get("assumption") for r in routes if isinstance(r, dict)}) < 2:
            refuse("020 alternatives must have distinct assumptions")
        for route in routes:
            if (not isinstance(route, dict) or set(route) != {"assumption", "gate", "rationale", "citations"} or
                    route["gate"] not in GATES | {None} or not text(route["assumption"]) or not text(route["rationale"])):
                refuse("Invalid conditional route")
            refs(route["citations"], documents)
    if require_complete and completed != 6:
        refuse("All six genuine first-pass decisions must be complete before freezing")
    return {"complete_drafts_not_accepted": completed, "remaining": 6 - completed,
            "reviewer_independence_certified": False, "accepted": 0}


def freeze(form_path, workspace, root, outdir, reviewer_name):
    # Validate before mkdir/write; impossible for the command to freeze blank data.
    if form_path.absolute().is_relative_to(REPO) or form_path.is_symlink():
        refuse("Filled review must stay outside Git")
    form = json.loads(form_path.read_text())
    result = validate(form, root, workspace, require_complete=True)
    if reviewer_name != form["reviewer"]["identity"] or not text(reviewer_name):
        refuse("Reviewer identity acknowledgement differs; not identity authentication")
    out = private_new(outdir)
    original = out / "first_pass.json"
    fd = os.open(original, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(form_path.read_bytes())
    receipt = {"status": "frozen_first_pass_not_accepted", "source_sha256": sha(original),
               "reviewer_identity_claim": reviewer_name, "reviewed_at": form["reviewer"]["reviewed_at"],
               "frozen_at": datetime.now(timezone.utc).isoformat(), "source_root_index_sha256": d9.d8.PIN,
               "case_ids": list(IDS), "independence_certified": False, "accepted": 0}
    write_new(out / "receipt.json", receipt)
    return result | {"frozen_sha256": receipt["source_sha256"], "status": receipt["status"]}


def verify_freeze(out, root, workspace):
    private_existing(out)
    receipt = json.loads((out / "receipt.json").read_text())
    form_path = out / "first_pass.json"
    if (set(receipt) != {"status", "source_sha256", "reviewer_identity_claim", "reviewed_at", "frozen_at",
                        "source_root_index_sha256", "case_ids", "independence_certified", "accepted"} or
            receipt["status"] != "frozen_first_pass_not_accepted" or receipt["independence_certified"] is not False or
            receipt["accepted"] != 0 or receipt["case_ids"] != list(IDS) or
            receipt["source_root_index_sha256"] != d9.d8.PIN or sha(form_path) != receipt["source_sha256"]):
        refuse("Frozen first pass changed or receipt invalid")
    form = json.loads(form_path.read_text())
    if receipt["reviewer_identity_claim"] != form["reviewer"]["identity"] or receipt["reviewed_at"] != form["reviewer"]["reviewed_at"]:
        refuse("Frozen reviewer metadata differs")
    validate(form, root, workspace, require_complete=True)
    return receipt


def unlock(out, root, workspace, dossier, manifest_path, destination, reviewer_name, packets, *, owner_release=False):
    # Check freeze FIRST; no dossier bytes read on an incomplete or modified freeze.
    receipt = verify_freeze(out, root, workspace)
    if owner_release is not True:
        refuse("Owner must explicitly release restricted AI draft after verifying the genuine human first pass")
    if reviewer_name != receipt["reviewer_identity_claim"]:
        refuse("Only the claimed first-pass reviewer can request unlock; identity is not cryptographically authenticated")
    if dossier.absolute().is_relative_to(REPO) or dossier.is_symlink():
        refuse("Restricted AI dossier must stay outside Git")
    manifest = json.loads(manifest_path.read_text())
    d10.validate(dossier, manifest, root, packets)
    target = private_new(destination)
    fd = os.open(target / "d10_ai_proposals.md", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with open(dossier, "rb") as incoming, os.fdopen(fd, "wb") as stream:
        shutil.copyfileobj(incoming, stream)
    if sha(target / "d10_ai_proposals.md") != manifest["private_dossier_sha256"]:
        refuse("Copied restricted AI dossier changed")
    comparison = {"status": "comparison_blank_not_adjudicated", "frozen_first_pass_sha256": receipt["source_sha256"],
                  "ai_dossier_sha256": manifest["private_dossier_sha256"], "reviewer_identity_claim": reviewer_name,
                  "cases": [{"case_id": cid, "agreements": [], "disagreements": [], "corrections": [],
                             "open_questions": [], "proposed_adjudication": None} for cid in IDS],
                  "acceptances_created": 0}
    write_new(target / "comparison_blank.json", comparison)
    return {"status": comparison["status"], "cases": 6, "acceptances_created": 0}


def check_comparison(comparison, out, root, workspace, manifest):
    receipt = verify_freeze(out, root, workspace)
    if (not isinstance(comparison, dict) or
            set(comparison) != {"status", "frozen_first_pass_sha256", "ai_dossier_sha256",
                                "reviewer_identity_claim", "cases", "acceptances_created"} or
            comparison["status"] not in ("comparison_blank_not_adjudicated", "comparison_proposed_not_accepted") or
            comparison["frozen_first_pass_sha256"] != receipt["source_sha256"] or
            comparison["ai_dossier_sha256"] != manifest["private_dossier_sha256"] or
            comparison["reviewer_identity_claim"] != receipt["reviewer_identity_claim"] or
            comparison["acceptances_created"] != 0):
        refuse("Comparison cannot alter frozen provenance or claim acceptance")
    cases = comparison["cases"]
    if not isinstance(cases, list) or len(cases) != 6 or [x.get("case_id") for x in cases if isinstance(x, dict)] != list(IDS):
        refuse("Comparison cases missing/duplicated")
    for case in cases:
        if set(case) != {"case_id", "agreements", "disagreements", "corrections", "open_questions", "proposed_adjudication"}:
            refuse("Comparison fields differ")
        for field in ("agreements", "disagreements", "corrections", "open_questions"):
            if not isinstance(case[field], list) or any(not text(x) for x in case[field]):
                refuse("Comparison notes must be nonempty text; preserve first pass separately")
        proposed = case["proposed_adjudication"]
        if proposed is not None and (not isinstance(proposed, dict) or set(proposed) != {"rationale", "open_authority_question"} or
                                     any(not text(proposed[k]) for k in proposed)):
            refuse("Adjudication is only a reasoned proposal, not an acceptance")
    return {"comparison_status": comparison["status"], "frozen_first_pass_verified": True, "accepted": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("prepare", "check", "freeze", "verify-freeze", "unlock", "check-comparison"):
        s = sub.add_parser(cmd)
        s.add_argument("--review-root", type=Path, required=True)
        if cmd == "prepare":
            s.add_argument("--packet-directory", type=Path, required=True)
            s.add_argument("--destination", type=Path, required=True)
        else:
            s.add_argument("--workspace", type=Path, required=True)
            if cmd in ("check", "freeze"):
                s.add_argument("--form", type=Path, required=True)
            if cmd in ("freeze", "verify-freeze", "unlock", "check-comparison"):
                s.add_argument("--freeze-dir", type=Path, required=True)
            if cmd in ("freeze", "unlock"):
                s.add_argument("--reviewer-name", required=True)
            if cmd == "unlock":
                s.add_argument("--dossier", type=Path, required=True)
                s.add_argument("--manifest", type=Path, required=True)
                s.add_argument("--packet-directory", type=Path, required=True)
                s.add_argument("--destination", type=Path, required=True)
                s.add_argument("--owner-release-after-human-freeze", action="store_true")
            if cmd == "check-comparison":
                s.add_argument("--comparison", type=Path, required=True)
                s.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.review_root, args.packet_directory, args.destination)
        elif args.command == "check":
            result = validate(json.loads(args.form.read_text()), args.review_root, args.workspace)
        elif args.command == "freeze":
            result = freeze(args.form, args.workspace, args.review_root, args.freeze_dir, args.reviewer_name)
        elif args.command == "verify-freeze":
            result = {"status": verify_freeze(args.freeze_dir, args.review_root, args.workspace)["status"], "accepted": 0}
        elif args.command == "unlock":
            result = unlock(args.freeze_dir, args.review_root, args.workspace, args.dossier, args.manifest,
                            args.destination, args.reviewer_name, args.packet_directory,
                            owner_release=args.owner_release_after_human_freeze)
        else:
            result = check_comparison(json.loads(args.comparison.read_text()), args.freeze_dir, args.review_root,
                                      args.workspace, json.loads(args.manifest.read_text()))
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        parser.exit(2, f"D11 review refused: {exc}\n")


if __name__ == "__main__":
    main()
