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
                or Decimal(ar["original_amount"]) != Decimal("1000.00")
                or Decimal(pay["invoice_amount"]) != Decimal("1000.00")
                or Decimal(pay["paid_amount"]) != Decimal("300.00")
                or Decimal(ar["outstanding_amount"]) != Decimal("700.00")
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


def classify_selected_packet(source_bytes, index_bytes, case_id, packet, *, provider_bytes,
                             packet_index_bytes):
    """Bind a freshly exported reader packet to the pinned control and source scope.

    Only a trusted caller may supply the source/index and a packet exported from
    PostgreSQL. This versioned projection does not change the v2 packet or reader.
    """
    state = classify(source_bytes, index_bytes, case_id)
    packet_index = json.loads(packet_index_bytes)
    if (packet_index.get("schema_version") != 1 or
            packet_index.get("status") != "postgresql_replayed_control_inputs_not_accepted_answers" or
            packet_index.get("accepted_answers") != 0 or
            packet_index.get("credit_source_index_sha256") != sha256(index_bytes).hexdigest() or
            packet_index.get("control_source_sha256") != sha256(source_bytes).hexdigest() or
            [r.get("case_id") for r in packet_index.get("cases", [])] !=
            ["EVAL-PREP-040", "EVAL-PREP-041"]):
        raise ValueError("Credit packet index source binding differs")
    pin = next(r for r in packet_index["cases"] if r["case_id"] == case_id)
    if (pin.get("packet_sha256") != packet.get("sha256") or
            pin.get("provider_file_sha256") != sha256(provider_bytes).hexdigest()):
        raise ValueError("Credit packet/provider pin differs")
    source = json.loads(source_bytes)
    case = next(c for c in source["cases"] if c["case_id"] == case_id)
    payload = packet.get("payload", {})
    from phase1c_evaluation_input import verify_review_input
    from decimal import Decimal
    rows = payload.get("source_rows", {})
    context = payload.get("run_context", {})
    if (not isinstance(provider_bytes, bytes) or
            json.loads(provider_bytes) != case["provider_manifest"] or
            context.get("run_id") != case["tables"]["deal_runs"][0]["run_id"] or
            context.get("deal_id") != case["tables"]["deals"][0]["deal_id"] or
            context.get("data_snapshot_ref") != case["tables"]["deal_runs"][0]["data_snapshot_ref"] or
            context.get("as_of_at") != case["tables"]["deal_runs"][0]["as_of_at"].replace("T", " ") or
            rows.get("customer", {}).get("customer_id") != case["tables"]["customers"][0]["customer_id"] or
            rows.get("deal", {}).get("customer_id") != rows["customer"]["customer_id"] or
            rows.get("credit", {}).get("customer_id") != rows["customer"]["customer_id"]):
        raise ValueError("Credit packet source identity differs")
    for key, table in (("receivables", "accounts_receivable"), ("payments", "payment_history")):
        selected = rows.get(key)
        expected = case["tables"].get(table, [])
        if not isinstance(selected, list) or len(selected) != len(expected):
            raise ValueError("Credit selected-row count differs")
        for authored in expected:
            matches = [item for item in selected if all(
                str(item.get(field)) == str(value) or
                (isinstance(value, str) and value.replace("T", " ") == str(item.get(field))) or
                (field in {"original_amount", "outstanding_amount", "invoice_amount", "paid_amount"}
                 and item.get(field) is not None and Decimal(str(item[field])) == Decimal(str(value)))
                for field, value in authored.items())]
            if len(matches) != 1:
                raise ValueError("Credit selected rows differ from authored source")
    # Recompute the packet seal and verify its complete source-row shape. The
    # caller must additionally compare its digest to the freshly read bundle.
    verify_review_input(packet, expected_case_id=case_id,
                        expected_source_digest=payload.get("source_input_digest"),
                        expected_business_contract=payload.get("business_contract"))
    return {**state, "selection_verified": True,
            # 040 has an overdue balance; 041 has unknown completeness.
            "credit_clearance_allowed": False, "packet_sha256": packet["sha256"],
            "provider_file_sha256": sha256(provider_bytes).hexdigest()}


if __name__ == "__main__":
    for control_id in ("EVAL-PREP-040", "EVAL-PREP-041"):
        print(canonical(classify(CONTROL.read_bytes(), INDEX.read_bytes(), control_id)))
