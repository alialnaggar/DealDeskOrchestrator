"""Six-case D13 candidate-only adapter; never writes a disposition or accepted answer.

The Phase 1C 36-case intake and its source-first human requirements are untouched.
Inputs must be trusted pinned source exports, never agent-provided scope claims.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import d11_human_review as d11

CONTRACT = Path(__file__).with_name("d13_pilot_composite_contract.json")
INDEX = "phase-1c-data/evaluation/provisional_packet_index.json"
BUSINESS = "phase-1c-data/implementation/phase1c_evaluation_business_contract.json"
OVERLAY_INDEX = "phase-1c-data/evaluation/credit-evidence-v3/index.json"
OVERLAY_SCOPE = "phase-1c-data/evaluation/credit-evidence-v3/credit_scope_v3.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def contract():
    value = json.loads(CONTRACT.read_text())
    require(value["schema_version"] == 1 and value["status"] == "technical_candidate_only_no_adoption_or_acceptance"
            and value["pilot_case_ids"] == list(d11.IDS), "Unsupported pilot contract")
    return value


def trusted_sources(root):
    """Verify entire v2 index and entire overlay before selecting six rows."""
    spec = contract()
    index = json.loads((root / INDEX).read_text())
    business = json.loads((root / BUSINESS).read_text())
    overlay = json.loads((root / OVERLAY_INDEX).read_text())
    scope = json.loads((root / OVERLAY_SCOPE).read_text())
    scope_bytes = (root / OVERLAY_SCOPE).read_bytes()
    require(digest(index) == spec["base_v2_index_sha256"] and
            index["source_definition_sha256"] == spec["base_v2_source_definition_sha256"] and
            digest(business) == spec["base_v2_business_contract_sha256"] and
            digest(overlay) == spec["overlay_index_sha256"] and
            hashlib.sha256(scope_bytes).hexdigest() == spec["overlay_scope_sha256"] and
            overlay["base_v2_index_sha256"] == digest(index) and
            overlay["credit_scope_sha256"] == hashlib.sha256(scope_bytes).hexdigest() and
            scope["base_v2_index_sha256"] == digest(index) and
            scope["base_v2_source_definition_sha256"] == spec["base_v2_source_definition_sha256"],
            "Trusted v2/overlay/contract pin differs")
    rows = {x["case_id"]: x for x in index["cases"]}
    overlay_rows = {x["case_id"]: x for x in overlay["cases"]}
    scope_rows = {x["case_id"]: x for x in scope["cases"]}
    require(len(rows) == 36 and len(overlay_rows) == len(scope_rows) == 36 and
            len(index["cases"]) == len(overlay["cases"]) == len(scope["cases"]) == 36,
            "Duplicate or missing source identity")
    return spec, business, rows, overlay_rows, scope_rows


def amount(value):
    try:
        number = Decimal(value)
    except (TypeError, InvalidOperation) as exc:
        raise ValueError("Invalid money amount") from exc
    require(number.is_finite(), "Nonfinite money amount")
    return number


def instant(value):
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("Missing or invalid source timestamp") from exc
    require(stamp.tzinfo is not None and stamp.utcoffset() is not None, "Source timestamp must have offset")
    return stamp


def classify_credit(packet, scope, business):
    """Source semantics only, not an adopted business disposition."""
    rows = packet["source_rows"]
    credit = rows["credit"]
    run = packet["run_context"]
    cutoff = instant(run["as_of_at"])
    observed = instant(credit["commitments_as_of_at"])
    age = (cutoff - observed).total_seconds()
    require(0 <= age <= business["evidence_age"]["snapshot_max_elapsed_hours"] * 3600,
            "Missing, future or stale credit commitment observation")
    require(credit["customer_id"] == rows["deal"]["customer_id"] and
            credit["commitment_evidence_ref"] == scope["commitment_evidence_ref"] and
            credit["credit_status"] == "Active", "Credit identity/status differs")
    quote = sum((amount(line["quoted_unit_price"]) * amount(line["quantity"])
                 for line in rows["lines"]), Decimal("0"))
    known = quote + amount(credit["unbilled_committed_amount"])
    require(quote >= 0 and amount(credit["unbilled_committed_amount"]) >= 0 and
            amount(credit["credit_limit"]) > 0, "Invalid known exposure/limit")
    cap = [r for r in rows["rules"]["policy_rules"] if r["policy_rule_id"] == "PO-BASE-CREDIT-CAP"]
    require(len(cap) == 1 and cap[0]["is_active"] is True and
            cap[0]["condition_json"] == {"credit_over_limit_pct_gt": 15} and
            cap[0]["required_action"] == "reject" and cap[0]["severity"] == "blocker" and
            cap[0]["policy_set_code"] == run["applied_policy_set_code"], "Credit hard-cap rule differs")
    declaration = scope["credit_evidence_scope"]
    complete = (declaration.get("completeness") == "declared_complete_zero" and
                declaration.get("customer_invoice_population") == "complete_for_this_synthetic_customer_at_cutoff" and
                declaration.get("source_class") == "fictional_isolated_case_fixture" and
                declaration.get("external_financial_verification") is False and
                declaration.get("selected_receivables_count") == 0 and
                declaration.get("selected_payment_events_count") == 0 and
                rows["receivables"] == [] and rows["payments"] == [])
    return {"evidence_state": "complete_synthetic_zero" if complete else "unknown_incomplete",
            "synthetic_ar_zero_supported": complete, "known_positive_exposure_eur": str(known),
            "credit_limit_eur": str(amount(credit["credit_limit"])),
            "known_exceeds_hard_cap": known > amount(credit["credit_limit"]) * Decimal("1.15"),
            "hard_cap_adjudication_without_completeness": "not_authorized",
            "credit_clearance_allowed": False}


def validate_composite(root, workspace):
    """Bind six unchanged v2 source pairs to six trusted scope rows; no adoption."""
    spec, business, rows, overlays, scopes = trusted_sources(root)
    d11.private_existing(workspace)
    results = {}
    for cid in spec["pilot_case_ids"]:
        folder = workspace / "sources" / cid
        packet = json.loads((folder / f"{cid}.json").read_text())
        provider_bytes = (folder / f"{cid}-provider.json").read_bytes()
        local_scope = json.loads((folder / "credit_scope.json").read_text())
        row, overlay, scope = rows[cid], overlays[cid], scopes[cid]
        payload = packet["payload"]
        require(payload["case_id"] == cid and packet["sha256"] == digest(payload) == row["packet_sha256"] == overlay["base_packet_sha256"] == scope["base_packet_sha256"] and
                hashlib.sha256(provider_bytes).hexdigest() == row["provider_file_sha256"] == scope["base_provider_file_sha256"] and
                digest(scope) == overlay["scope_sha256"] == digest(local_scope),
                f"{cid}: packet/provider/scope hash mismatch")
        ctx, deal = payload["run_context"], payload["source_rows"]["deal"]
        require(scope["case_id"] == cid and scope["customer_id"] == deal["customer_id"] and
                scope["deal_id"] == ctx["deal_id"] == deal["deal_id"] and
                scope["run_id"] == ctx["run_id"] and
                scope["as_of_at"] == ctx["as_of_at"] and
                scope["data_snapshot_ref"] == ctx["data_snapshot_ref"],
                f"{cid}: scope identity/cutoff mismatch")
        credit = classify_credit(payload, scope, business)
        require(credit["evidence_state"] == "complete_synthetic_zero", f"{cid}: incomplete Credit evidence")
        results[cid] = {"packet_sha256": row["packet_sha256"],
                        "provider_file_sha256": row["provider_file_sha256"],
                        "scope_sha256": overlay["scope_sha256"], "credit": credit}
    return {"contract_sha256": digest(spec), "input_index_sha256": digest(json.loads((root / INDEX).read_text())),
            "cases": results}


def candidate(form_bytes, root, workspace):
    """Create a PRIVATE in-memory candidate, never a legacy intake or acceptance."""
    composite = validate_composite(root, workspace)
    form = json.loads(form_bytes)
    require(form.get("schema_version") == 3, "D11 v3 required for mixed-method candidate")
    d11.validate(form, root, workspace, require_complete=True)
    reviewer = form["reviewer"]
    require(reviewer["identity"] == "Ali Alnaggar" and reviewer["role"] == "Thesis author" and
            reviewer["reviewed_at"] is None and reviewer["source_first_attestation"] is False and
            reviewer["prior_ai_answer_exposure"] is None and reviewer["ai_assistance_used"] is True,
            "Mixed author-assisted provenance differs")
    try:
        day = date.fromisoformat(reviewer["review_date"])
        zone = ZoneInfo(reviewer["review_timezone"])
    except (TypeError, ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError("Date-only review requires valid date and IANA timezone") from exc
    require(day.isoformat() == reviewer["review_date"] and zone.key == reviewer["review_timezone"],
            "Noncanonical date-only provenance")
    result = []
    for row in form["cases"]:
        cid = row["case_id"]
        source = composite["cases"][cid]
        require(all(row[k] == source[k] for k in ("packet_sha256", "provider_file_sha256")) and
                row["credit_scope_sha256"] == source["scope_sha256"] and
                row["credit_scope"]["use"] == "conditional", f"{cid}: Credit adoption/pins differ")
        provenance = form["case_review_provenance"][cid]
        require(provenance["ai_assistance_used"] is True and
                (cid == d11.IDS[0] or provenance["source_first_attestation"] is False),
                f"{cid}: summary-based review must not claim source-first")
        result.append({"case_id": cid, "d11_case_sha256": digest(row),
                       "review_method": "source_first_ai_assisted_author" if provenance["source_first_attestation"] else "summary_based_ai_assisted_author",
                       "prior_ai_answer_exposure": provenance["prior_ai_answer_exposure"],
                       "source_pins": {k: source[k] for k in ("packet_sha256", "provider_file_sha256", "scope_sha256")},
                       "draft": row, "case_review_provenance": provenance})
    all_ids = [x["case_id"] for x in json.loads((root / INDEX).read_text())["cases"]]
    return {"schema_version": 1, "status": "six_case_candidate_only_not_authorized_for_acceptance",
            "academic_acceptance_policy": "pending", "accepted_reference_answers": 0,
            "ready_for_generation": False, "independent_human_review_certified": False,
            "legacy_intake_unchanged": True, "input_index_sha256": composite["input_index_sha256"],
            "composite_contract_sha256": composite["contract_sha256"],
            "d11_file_sha256": hashlib.sha256(form_bytes).hexdigest(),
            "review_date": reviewer["review_date"], "review_timezone": reviewer["review_timezone"],
            "reviewed_at": None, "pilot_cases": result,
            "other_cases_pending": [x for x in all_ids if x not in composite["cases"]]}


def write_private_candidate(form_bytes, root, workspace, destination):
    """Optional output: only a new owner-only file outside Git, never an intake."""
    value = candidate(form_bytes, root, workspace)
    parent = destination.parent
    d11.private_existing(parent)
    require(not destination.is_symlink() and not destination.exists() and
            not destination.resolve().is_relative_to(d11.REPO.resolve()) and
            value["status"] == "six_case_candidate_only_not_authorized_for_acceptance" and
            value["accepted_reference_answers"] == 0 and value["academic_acceptance_policy"] == "pending",
            "Only a new private, nonaccepted candidate may be written")
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")
