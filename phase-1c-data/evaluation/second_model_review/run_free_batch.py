"""Checkpointed, no-retry OpenCode free-model blind-review batch runner.

Never runs a paid model. An interrupted/uncertain send remains pending and is
never automatically retried. Only structurally and arithmetically valid drafts
are admitted to responses; raw invocation evidence is always retained.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from workflow import (assert_blind_sources, blank, deterministic_discrepancies,
                      load_case, manifest, validate_response, write)

# Verify zero pricing in the local /api/model catalogue before each campaign.
# This allowlist is a safety ceiling, not a claim of remaining free quota.
FREE_MODELS = {"opencode/beam-free", "opencode/flint-40b-free",
               "opencode/nemotron-3.5-super-vl-free", "opencode/nemotron-3.5-lightning-free",
               "opencode/mimo-v2.6-flash-free", "opencode/deepseek-v4.1-flash-free",
               "opencode/glm-5.3-flash-free"}
PREVIOUS_ATTEMPTS = {"EVAL-PREP-001", "EVAL-PREP-002", "EVAL-PREP-003", "EVAL-PREP-004"}


def verify_zero_pricing(model):
    """Refuse to send if the local OpenCode model catalogue no longer says free."""
    response = subprocess.run(["opencode", "api", "get", "/api/model"],
                              capture_output=True, timeout=20, check=True)
    found = [m for m in json.loads(response.stdout)["data"]
             if m.get("providerID", "") + "/" + m.get("id", "") == model]
    if (len(found) != 1 or not found[0].get("cost") or
            any(c.get("input") != 0 or c.get("output") != 0 or
                any(c.get("cache", {}).get(k) != 0 for k in ("read", "write"))
                for c in found[0]["cost"])):
        raise ValueError("Model is not confirmed zero-priced in local catalogue")


def prompt(model, timestamp):
    return ("Blinded AI-only, source-first six-responsibility technical review. "
            "Use ONLY attached sources.json and blank_response.json. No tools, web, "
            "outside files, prior answers or recommendations. Return exactly ONE JSON "
            "object, no markdown, using the precise blank_response.json keys and nested "
            "keys. status=second_model_draft_not_accepted. "
            f"reviewer.model_id={model}; reviewer.reviewed_at={timestamp}; "
            "reviewer.source_first_attestation=Only supplied blinded case sources; "
            "reviewer.assistance_disclosure=AI-only source-first technical review, "
            "not independent human expert validation. "
            "For each of Configuration, Pricing, Availability, Credit, Policy, Approval: "
            "finding MUST be one of no_issue_identified, issue_identified, evidence_needed, "
            "human_review_required, not_applicable, abstain (no other label); nonempty "
            "rationale; evidence_refs must be OBJECTS {document,pointer} citing EXISTING "
            "facts in sources.json.documents. packet pointers start /source_rows/, "
            "/run_context/ or /business_contract/; credit_scope pointers start /credit_evidence_scope/ "
            "for originals and /completeness for controls. Include calculations arrays "
            "of {metric,value_eur,formula,evidence_refs}, uncertainties arrays, and null "
            "abstention_reason unless abstaining. Pricing: quote_total_eur calculation or "
            "explicit abstention. For declared complete-zero Credit: credit_exposure_eur "
            "calculation or abstention. For complete nonempty Credit: overdue_ar_eur "
            "calculation or abstention. For incomplete credit evidence: no asserted numeric "
            "credit exposure or overdue balance. Overall gate MUST be one of blocked, "
            "needs_revision, needs_evidence, needs_commitment, approval_required, abstain; "
            "give rationale, evidence_refs, human_actions, uncertainties and null "
            "abstention_reason unless abstaining. No approval, reservation, payment-history "
            "or delivery promise from missing facts. No evaluation answer is accepted.")


def run(args):
    if args.model not in FREE_MODELS:
        raise ValueError("Only explicitly allowlisted zero-priced models are permitted")
    verify_zero_pricing(args.model)
    rows = manifest()["cases"]
    dirs = {"original_v3": Path(args.original_packets),
            "supplemental_configuration": Path(args.configuration_packets),
            "supplemental_credit": Path(args.credit_packets)}
    packages, attempts, responses = map(Path, (args.packages, args.attempts, args.responses))
    attempts.mkdir(parents=True, exist_ok=True)
    responses.mkdir(parents=True, exist_ok=True)
    chosen = set(args.case_id or [r["case_id"] for r in rows])
    if chosen - {r["case_id"] for r in rows}:
        raise ValueError("Unknown case ID")
    acknowledgments = set(args.acknowledge_previous_send or [])
    if acknowledgments - PREVIOUS_ATTEMPTS or acknowledgments - chosen:
        raise ValueError("Acknowledge only selected, documented prior sends")
    count = 0
    for row in rows:
        cid = row["case_id"]
        if (cid not in chosen or (cid in PREVIOUS_ATTEMPTS and cid not in acknowledgments)
                or (attempts / (cid + ".json")).exists() or
                (responses / (cid + ".json")).exists()):
            continue  # Never automatically retry an ambiguous or rejected send.
        if count >= args.max_cases:
            break
        docs = load_case(row, dirs)
        assert_blind_sources(row, docs)
        folder = packages / cid
        if (json.loads((folder / "sources.json").read_bytes()) !=
                {"source_pins": row, "documents": docs} or
                json.loads((folder / "blank_response.json").read_bytes()) != blank(row)):
            raise ValueError(cid + ": materialized blind package differs")
        now = datetime.now(timezone.utc).isoformat()
        text = prompt(args.model, now)
        record = {"case_id": cid, "model_id": args.model, "invocation": "opencode run --standalone",
                  "prompt": text, "prompt_sha256": sha256(text.encode()).hexdigest(),
                  "started_at": now, "state": "send_started_uncertain_until_result",
                  "source_pins": row, "tool_use_permitted": False,
                  "operator": "automated local runner; no human adjudication"}
        checkpoint = attempts / (cid + ".json")
        write(checkpoint, record)  # Before network send; no automatic retries.
        command = ["opencode", "run", "--standalone", "--model", args.model,
                   "--format", "json", "--title", "Phase1C blinded " + cid,
                   "--file", "sources.json", "--file", "blank_response.json", text]
        try:
            result = subprocess.run(command, cwd=folder, capture_output=True,
                                    timeout=args.timeout_seconds, check=False)
            (attempts / (cid + ".jsonl")).write_bytes(result.stdout)
            (attempts / (cid + ".stderr")).write_bytes(result.stderr)
            record.update(exit_code=result.returncode,
                          raw_sha256=sha256(result.stdout).hexdigest(),
                          completed_at=datetime.now(timezone.utc).isoformat())
            events = [json.loads(line) for line in result.stdout.splitlines()]
            if result.returncode or any(e.get("type") in ("error", "tool_use") for e in events):
                record["state"] = "failed_or_tool_use_pending_manual_review"
            else:
                chunks = [e["part"]["text"] for e in events if e.get("type") == "text"]
                response = json.loads("".join(chunks))
                errors = validate_response(response, row, docs)
                if not errors:
                    errors = deterministic_discrepancies(response, docs)
                record["validation_errors"] = errors
                if errors:
                    record["state"] = "invalid_draft_pending"
                else:
                    record["state"] = "valid_ai_draft_not_accepted"
                    write(responses / (cid + ".json"), response)
        except (subprocess.TimeoutExpired, OSError, ValueError, KeyError, TypeError) as error:
            record["state"] = "uncertain_or_invalid_pending_no_retry"
            record["error_type"] = type(error).__name__
            if isinstance(error, subprocess.TimeoutExpired):
                (attempts / (cid + ".partial_stdout")).write_bytes(error.stdout or b"")
                (attempts / (cid + ".partial_stderr")).write_bytes(error.stderr or b"")
        write(checkpoint, record)
        count += 1
        print(cid, record["state"], flush=True)
        if record["state"] in ("failed_or_tool_use_pending_manual_review", "uncertain_or_invalid_pending_no_retry"):
            break  # Rate-limit/transport/timeout may affect all subsequent calls.


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--original-packets", required=True)
    p.add_argument("--configuration-packets", required=True)
    p.add_argument("--credit-packets", required=True)
    p.add_argument("--packages", required=True)
    p.add_argument("--attempts", required=True)
    p.add_argument("--responses", required=True)
    p.add_argument("--case-id", action="append", help="May be repeated; omit for remaining cases")
    p.add_argument("--acknowledge-previous-send", action="append",
                   help="Explicitly authorize a new attempt after inspecting that case's raw pilot evidence")
    p.add_argument("--max-cases", type=int, default=3)
    p.add_argument("--timeout-seconds", type=int, default=180)
    a = p.parse_args()
    if not 1 <= a.max_cases <= 5 or not 10 <= a.timeout_seconds <= 600:
        p.error("Bound batches to 1–5 cases and timeouts to 10–600 seconds")
    run(a)
