"""Versioned, source-only credit evidence scope for the pinned v2 cases.

This does not change the 36 PostgreSQL source rows or accept reviewer answers.
The overlay plus the v2 packet form a provisional v3 input; a database replay
and reviewer adjudication are required before it is released.
"""

from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_SHA = "1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc"
BASE_INDEX_SHA = "7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc"
ARCHETYPES = (
    "STOCK-READY", "STOCK-ALLOCATED", "STOCK-STALE",
    "SUPPLY-CONFIRMED", "SUPPLY-OFFER-ONLY", "SUPPLY-CANCELLED",
    "BUILD-READY", "BUILD-SUBSTITUTE", "BUILD-CAPACITY-STALE",
    "BUILD-HORIZON", "DIGITAL-PROVED", "DIGITAL-NO-PROOF",
    "DIGITAL-EXPIRED", "SERVICE-COVERED", "SERVICE-OUTSIDE",
    "CREDIT-LIMIT", "PRICE-FLOOR", "POLICY-CLAUSE",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def render(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def build(base, authoring, index, intent, *, raw_base, raw_index):
    if (sha256(raw_base).hexdigest() != BASE_SHA or
            digest(json.loads(raw_index)) != BASE_INDEX_SHA):
        raise ValueError("Pinned v2 source or index bytes differ")
    if (base.get("evaluation_input_version") != 2 or
            index.get("source_definition_sha256") != BASE_SHA or
            index.get("input_case_count") != 36 or
            authoring.get("authored_input_cases") != 36):
        raise ValueError("Base evaluation identity differs")
    cases = base["cases"]
    reviews = authoring["cases"]
    pins = index["cases"]
    if len(cases) != 36 or len(reviews) != 36 or len(pins) != 36:
        raise ValueError("Expected 36 source/review/index rows")
    if (intent.get("status") != "technical_case_intent_review_not_accepted_answers" or
            intent.get("source_definition_sha256") != BASE_SHA or
            len(intent.get("cases", [])) != 36):
        raise ValueError("Individual credit source review missing")
    overlay = []
    for n, (case, review, pin) in enumerate(zip(cases, reviews, pins), 1):
        expected_id = f"EVAL-PREP-{n:03d}"
        if (case["case_id"] != expected_id or review["case_id"] != expected_id or
                pin["case_id"] != expected_id or
                review["archetype_id"] != ARCHETYPES[(n - 1) // 2] or
                review["variant"] != (n - 1) % 2 + 1):
            raise ValueError(f"{expected_id}: source/authoring/index identity differs")
        tables = case["tables"]
        if (len(tables.get("customer_credit_profiles", [])) != 1 or
                len(tables.get("customers", [])) != 1 or
                len(tables.get("deals", [])) != 1 or
                len(tables.get("deal_runs", [])) != 1 or
                len(tables.get("deal_lines", [])) != 1 or
                tables.get("accounts_receivable") or tables.get("payment_history")):
            raise ValueError(f"{expected_id}: unexpected credit or deal source rows")
        customer = tables["customers"][0]
        credit = tables["customer_credit_profiles"][0]
        deal = tables["deals"][0]
        run = tables["deal_runs"][0]
        line = tables["deal_lines"][0]
        entry = intent["cases"][n - 1]
        quote = Decimal(str(line["quantity"])) * Decimal(str(line["quoted_unit_price"]))
        if (entry["case_id"] != expected_id or
                entry["archetype_id"] != review["archetype_id"] or
                entry["customer_id"] != customer["customer_id"] or
                entry["as_of_at"] != run["as_of_at"] or
                entry["quote_total_eur"] != f"{quote:.2f}" or
                entry["credit_limit_eur"] != f"{Decimal(str(credit['credit_limit'])):.2f}" or
                entry["unbilled_commitments_eur"] !=
                f"{Decimal(str(credit['unbilled_committed_amount'])):.2f}" or
                entry["authored_receivables"] != 0 or
                entry["authored_payments"] != 0 or
                entry["intended_credit_scope"] !=
                "fictional_complete_zero_ar_and_payment_events" or
                not entry.get("technical_basis") or not entry.get("review_provenance")):
            raise ValueError(f"{expected_id}: individual credit source review differs")
        if (len({customer["customer_id"], credit["customer_id"], deal["customer_id"]}) != 1 or
                deal["deal_id"] != run["deal_id"] or
                deal["dataset_type"] != "evaluation" or
                run["data_snapshot_ref"] != f"EVAL36-{n:03d}-SOURCES" or
                credit["credit_status"] != "Active" or
                customer["account_status"] != "Active" or
                credit["commitment_evidence_ref"] != f"EVAL36-{n:03d}-CREDIT"):
            raise ValueError(f"{expected_id}: credit customer or source scope differs")
        as_of = datetime.fromisoformat(run["as_of_at"])
        observed = datetime.fromisoformat(credit["commitments_as_of_at"])
        if not 0 <= (as_of - observed).total_seconds() <= 24 * 3600:
            raise ValueError(f"{expected_id}: credit commitment timestamp not fresh")
        if (n in (31, 32)) != (review["archetype_id"] == "CREDIT-LIMIT"):
            raise ValueError("Credit-limit archetype selection differs")
        if (credit["credit_limit"] == 1000) != (n in (31, 32)):
            raise ValueError(f"{expected_id}: credit-limit source differs")
        overlay.append({
            "case_id": expected_id,
            "base_packet_sha256": pin["packet_sha256"],
            "base_provider_file_sha256": pin["provider_file_sha256"],
            "customer_id": customer["customer_id"],
            "deal_id": deal["deal_id"],
            "run_id": run["run_id"],
            "data_snapshot_ref": run["data_snapshot_ref"],
            "as_of_at": run["as_of_at"],
            "commitment_evidence_ref": credit["commitment_evidence_ref"],
            "archetype_id": review["archetype_id"],
            "credit_evidence_scope": {
                "source_class": "fictional_isolated_case_fixture",
                "customer_invoice_population": "complete_for_this_synthetic_customer_at_cutoff",
                "selected_receivables_count": 0,
                "selected_payment_events_count": 0,
                "completeness": "declared_complete_zero",
                "external_financial_verification": False,
            },
            "technical_review": "case_source_identity_cutoff_and_empty_rows_checked; not independent human adjudication",
            "intent_review_sha256": digest(entry),
        })
    base_case = cases[0]
    controls = []
    for number, completeness in ((40, "declared_complete_nonempty"), (41, "explicitly_incomplete_unknown")):
        cid = f"EVAL-PREP-{number:03d}"
        copied = deepcopy(base_case)
        replacement = f"EVALCREDIT-{number:03d}"
        # Replace only the case-specific prefix. Shared product and policy IDs remain stable.
        serialized = json.dumps(copied)
        copied = json.loads(serialized.replace("EVAL36-001", replacement))
        copied["case_id"] = cid
        copied["tables"]["deals"][0]["deal_name"] = f"Synthetic credit evidence control {number}"
        copied["tables"]["deal_runs"][0]["run_id"] = f"00000000-0000-4000-8000-{360000 + number:012d}"
        copied["tables"]["deal_runs"][0]["data_snapshot_ref"] = replacement + "-SOURCES"
        if number == 40:
            copied["tables"]["accounts_receivable"] = [{
                "receivable_id": replacement + "-AR-1",
                "customer_id": replacement + "-CUSTOMER",
                "invoice_number": replacement + "-INV-1",
                "invoice_date": "2026-08-01",
                "due_date": "2026-08-20",
                "original_amount": "1000.00",
                "outstanding_amount": "700.00",
                "status": "Overdue",
                "as_of_date": "2026-09-01",
            }]
            copied["tables"]["payment_history"] = [{
                "payment_id": replacement + "-PAY-1",
                "customer_id": replacement + "-CUSTOMER",
                "invoice_number": replacement + "-INV-1",
                "invoice_date": "2026-08-01",
                "due_date": "2026-08-20",
                "paid_date": "2026-08-15",
                "invoice_amount": "1000.00",
                "paid_amount": "300.00",
            }]
        scope = {
            "source_class": "fictional_isolated_credit_control",
            "customer_invoice_population": ("complete_for_this_synthetic_customer_at_cutoff"
                                            if number == 40 else "not_established"),
            "selected_receivables_count": len(copied["tables"].get("accounts_receivable", [])),
            "selected_payment_events_count": len(copied["tables"].get("payment_history", [])),
            "completeness": completeness,
            "external_financial_verification": False,
        }
        controls.append({
            "case_id": cid, "derived_from": "EVAL-PREP-001",
            "tables": copied["tables"],
            "provider_manifest": copied["provider_manifest"],
            "credit_evidence_scope": scope,
            "technical_review": "source_only_control_pending_postgresql_replay_and_six_findings",
        })
    overlay_doc = {
        "schema_version": 1, "evaluation_input_version": 3,
        "status": "provisional_source_scope_not_accepted_answers",
        "base_v2_source_definition_sha256": BASE_SHA,
        "base_v2_index_sha256": BASE_INDEX_SHA,
        "case_intent_review_sha256": sha256(render(intent).encode()).hexdigest(),
        "cases": overlay,
    }
    control_doc = {
        "schema_version": 1, "extension_id": "credit-evidence-controls-v1",
        "status": "provisional_source_cases_pending_postgresql_replay_and_review",
        "base_v2_source_definition_sha256": BASE_SHA,
        "cases": controls,
    }
    result_index = {
        "schema_version": 1, "evaluation_input_version": 3,
        "status": "provisional_overlay_index_not_released_answers",
        "base_v2_index_sha256": BASE_INDEX_SHA,
        "original_case_count": 36, "supplemental_control_count": 2,
        "accepted_original_answers": 0, "accepted_control_answers": 0,
        "credit_scope_sha256": sha256(render(overlay_doc).encode()).hexdigest(),
        "control_source_sha256": sha256(render(control_doc).encode()).hexdigest(),
        "cases": [{"case_id": r["case_id"], "scope_sha256": digest(r),
                   "base_packet_sha256": r["base_packet_sha256"]} for r in overlay],
        "controls": [{"case_id": r["case_id"], "source_sha256": digest(r)}
                     for r in controls],
    }
    return overlay_doc, control_doc, result_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    base_path = HERE / "provisional_cases.json"
    index_path = HERE / "provisional_packet_index.json"
    base = json.loads(base_path.read_text())
    authoring = json.loads((HERE / "provisional_authoring_manifest.json").read_text())
    intent = json.loads((HERE / "credit_intent_review_v3.json").read_text())
    index = json.loads(index_path.read_text())
    values = build(base, authoring, index, intent,
                   raw_base=base_path.read_bytes(), raw_index=index_path.read_bytes())
    output = HERE / "credit-evidence-v3"
    if not args.check:
        output.mkdir(exist_ok=True)
    for name, value in zip(("credit_scope_v3.json", "control_cases_v1.json", "index.json"), values):
        path = output / name
        if args.check:
            if path.read_text() != render(value):
                raise SystemExit(f"{path.name} differs from pinned source-only generation")
        else:
            path.write_text(render(value))
    print("36 scoped original cases; 2 unaccepted supplemental controls")


if __name__ == "__main__":
    main()
