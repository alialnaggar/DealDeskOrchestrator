"""Fail-closed classification of pinned synthetic Credit control source evidence.

The v3 sidecar is a trusted fixture artifact, not a salesperson or model claim.
This source gate does not certify that PostgreSQL selected the authored rows:
the separate fresh database replay and packet-index binding remain required.
"""

from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROL = HERE / "credit-evidence-v3" / "control_cases_v1.json"
INDEX = HERE / "credit-evidence-v3" / "index.json"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def classify(source_bytes, index_bytes, case_id):
    """Return an evidence state; never equate an empty selected set with zero.

    The caller must load both files from a trusted, pinned checkout. A mismatch
    or an unsupported declaration raises rather than granting clearance.
    """
    source = json.loads(source_bytes)
    index = json.loads(index_bytes)
    if (sha256(source_bytes).hexdigest() != index.get("control_source_sha256")
            or source.get("status") !=
            "provisional_source_cases_pending_postgresql_replay_and_review"
            or index.get("status") !=
            "provisional_overlay_index_not_released_answers"
            or index.get("supplemental_control_count") != 2
            or index.get("accepted_control_answers") != 0):
        raise ValueError("Credit control source/index identity differs")
    cases = source["cases"]
    pins = index["controls"]
    if ([c["case_id"] for c in cases] != ["EVAL-PREP-040", "EVAL-PREP-041"]
            or [p["case_id"] for p in pins] != ["EVAL-PREP-040", "EVAL-PREP-041"]
            or any(digest(c) != p["source_sha256"] for c, p in zip(cases, pins))):
        raise ValueError("Credit control case identity or hash differs")
    if case_id not in ("EVAL-PREP-040", "EVAL-PREP-041"):
        raise ValueError("Unknown Credit control")
    case = next(c for c in cases if c["case_id"] == case_id)
    scope = case["credit_evidence_scope"]
    tables = case["tables"]
    run, deal, customer, profile = (tables["deal_runs"][0], tables["deals"][0],
                                     tables["customers"][0],
                                     tables["customer_credit_profiles"][0])
    receivables = tables.get("accounts_receivable", [])
    payments = tables.get("payment_history", [])
    if (case["derived_from"] != "EVAL-PREP-001"
            or run["run_id"] != f"00000000-0000-4000-8000-0000003600{case_id[-2:]}"
            or run["deal_id"] != deal["deal_id"]
            or run["data_snapshot_ref"] != f"EVALCREDIT-{case_id[-3:]}-SOURCES"
            or len({customer["customer_id"], deal["customer_id"],
                    profile["customer_id"]}) != 1
            or any(r["customer_id"] != customer["customer_id"]
                   for r in receivables + payments)
            or scope["selected_receivables_count"] != len(receivables)
            or scope["selected_payment_events_count"] != len(payments)
            or scope["source_class"] != "fictional_isolated_credit_control"
            or scope["external_financial_verification"] is not False):
        raise ValueError("Credit scope/source facts disagree")
    if case_id == "EVAL-PREP-040":
        if (scope["completeness"] != "declared_complete_nonempty"
                or scope["customer_invoice_population"] !=
                "complete_for_this_synthetic_customer_at_cutoff"
                or len(receivables) != 1 or len(payments) != 1):
            raise ValueError("Nonempty control declaration differs")
        ar, pay = receivables[0], payments[0]
        from decimal import Decimal
        if (ar["invoice_number"] != pay["invoice_number"]
                or ar["as_of_date"] != run["as_of_at"][:10]
                or pay["paid_date"] > run["as_of_at"][:10]
                or ar["due_date"] >= run["as_of_at"][:10]
                or Decimal(ar["original_amount"]) - Decimal(pay["paid_amount"])
                != Decimal(ar["outstanding_amount"])
                or ar["status"] != "Overdue"):
            raise ValueError("Nonempty control accounting/cutoff differs")
        return {"case_id": case_id, "source_evidence_state": "declared_complete_nonempty",
                "receivables": 1, "payments": 1, "overdue_ar_eur": "700.00",
                "selection_verified": False, "credit_clearance_allowed": False}
    if (scope["completeness"] != "explicitly_incomplete_unknown"
            or scope["customer_invoice_population"] != "not_established"
            or receivables or payments):
        raise ValueError("Incomplete control declaration differs")
    return {"case_id": case_id, "source_evidence_state": "unknown_incomplete",
            "receivables": 0, "payments": 0, "overdue_ar_eur": None,
            "selection_verified": False, "credit_clearance_allowed": False}


if __name__ == "__main__":
    for control_id in ("EVAL-PREP-040", "EVAL-PREP-041"):
        print(canonical(classify(CONTROL.read_bytes(), INDEX.read_bytes(), control_id)))
