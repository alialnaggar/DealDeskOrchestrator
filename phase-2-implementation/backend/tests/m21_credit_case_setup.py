"""Development-only credit source variants, added after the nine-case baseline.

These are not Phase 1C rows or independent answer keys. A closed-world fixture
assertion covers only the rows this disposable database installs, not the
completeness of any external financial ledger.
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreditCase:
    case_id: str
    run_id: UUID


CASES = tuple(CreditCase("CR0" + str(i), UUID(
    f"00000000-0000-4000-8000-{28000 + i:012d}")) for i in (1, 2, 3))


def ids(case):
    if case not in {item.case_id for item in CASES}:
        raise ValueError("unknown_credit_development_case")
    return {kind: f"M21CD-{kind}-{case}" for kind in ("C", "D", "L", "AR", "PAY")}


def install_credit_cases(connection):
    """Clone only source N01 in an isolated disposable DB; never edit M18 rows."""
    with connection:
        connection.execute("SET LOCAL search_path TO deal_desk, public")
        baseline = connection.execute("SELECT count(*) FROM deal_desk.deals WHERE "
            "deal_id LIKE 'M18-D-%'").fetchone()[0]
        existing = connection.execute("SELECT count(*) FROM deal_desk.deals WHERE "
            "deal_id LIKE 'M21CD-D-%'").fetchone()[0]
        if baseline != 9 or existing:
            raise ValueError("credit cases require nine unchanged source deals")
        for case in CASES:
            ref = ids(case.case_id)
            profile = {
                "CR01": (Decimal("10000.00"), Decimal("100.00"),
                    "2026-09-01 10:00+00", "Low", "Active"),
                "CR02": (Decimal("5000.00"), Decimal("300.00"),
                    "2026-08-01 10:00+00", "High", "Review"),
                "CR03": (Decimal("1500.00"), Decimal("200.00"),
                    "2026-09-01 10:00+00", "High", "On-Hold"),
            }[case.case_id]
            connection.execute("""INSERT INTO customers
                (customer_id,customer_code,customer_name,size_segment,strategic_account,
                 industry,country_code,region,customer_since,account_status)
                SELECT %s,%s,%s,size_segment,strategic_account,industry,country_code,
                       region,customer_since,account_status FROM customers
                WHERE customer_id='M18-C-N01'""", (ref["C"], ref["C"],
                "Disposable credit " + case.case_id))
            connection.execute("""INSERT INTO customer_credit_profiles
                (customer_id,credit_limit,unbilled_committed_amount,commitments_as_of_at,
                 commitment_evidence_ref,risk_rating,credit_status,
                 default_payment_terms_days,last_review_date,next_review_date)
                SELECT %s,%s,%s,%s,%s,%s,%s,default_payment_terms_days,
                       last_review_date,next_review_date
                FROM customer_credit_profiles WHERE customer_id='M18-C-N01'""",
                (ref["C"], *profile[:3], "M21CD-COMMIT-" + case.case_id,
                    *profile[3:]))
            connection.execute("""INSERT INTO deals
                (deal_id,customer_id,salesperson_id,deal_name,submitted_at,currency_code,
                 catalog_version,policy_set_code,requested_delivery_date,
                 destination_country_code,destination_region,shipping_service_code,
                 terms_json,deal_status,dataset_type)
                SELECT %s,%s,salesperson_id,%s,submitted_at,currency_code,catalog_version,
                       policy_set_code,requested_delivery_date,destination_country_code,
                       destination_region,shipping_service_code,terms_json,'Draft',
                       'generated_test' FROM deals WHERE deal_id='M18-D-N01'""",
                (ref["D"], ref["C"], "Disposable credit " + case.case_id))
            connection.execute("""INSERT INTO deal_lines
                (deal_line_id,deal_id,line_number,product_id,quantity,quoted_unit_price,
                 configuration_json) SELECT %s,%s,line_number,product_id,quantity,
                 quoted_unit_price,configuration_json FROM deal_lines
                 WHERE deal_id='M18-D-N01'""", (ref["L"], ref["D"]))
            connection.execute("UPDATE deals SET deal_status='Submitted' WHERE deal_id=%s",
                (ref["D"],))
            connection.execute("""INSERT INTO deal_runs
                (run_id,deal_id,original_policy_set_code,applied_policy_set_code,
                 catalog_version_used,as_of_at,data_snapshot_ref,input_snapshot_json,
                 config_hash,run_status,started_at)
                SELECT %s,%s,original_policy_set_code,applied_policy_set_code,
                       catalog_version_used,as_of_at,%s,jsonb_build_object(
                       'deal_id',%s::text,'case_id',%s::text),config_hash,run_status,started_at
                FROM deal_runs WHERE deal_id='M18-D-N01'""", (case.run_id, ref["D"],
                "M21CD-SNAPSHOT-" + case.case_id, ref["D"], case.case_id))
            if case.case_id in ("CR01", "CR03"):
                original, outstanding, paid, status, due = (
                    (Decimal("100"), Decimal("60"), Decimal("40"),
                     "Partially Paid", "2026-09-15") if case.case_id == "CR01" else
                    (Decimal("1200"), Decimal("900"), Decimal("300"),
                     "Overdue", "2026-08-15"))
                invoice = "M21CD-INVOICE-" + case.case_id
                connection.execute("""INSERT INTO accounts_receivable
                    (receivable_id,customer_id,invoice_number,invoice_date,due_date,
                     original_amount,outstanding_amount,status,as_of_date)
                     VALUES (%s,%s,%s,'2026-08-01',%s,%s,%s,%s,'2026-09-01')""",
                    (ref["AR"], ref["C"], invoice, due, original, outstanding, status))
                connection.execute("""INSERT INTO payment_history
                    (payment_id,customer_id,invoice_number,invoice_date,due_date,
                     paid_date,invoice_amount,paid_amount) VALUES
                     (%s,%s,%s,'2026-08-01',%s,'2026-08-20',%s,%s)""",
                    (ref["PAY"], ref["C"], invoice, due, original, paid))


def verify_credit_case(pool, fixed, case_id):
    """Fail closed before hosted calls if the pinned reader/source shape drifts."""
    ref = ids(case_id)
    profile, ar, payments = pool["credit"], pool["receivables"], pool["payments"]
    if profile["customer_id"] != ref["C"] or pool["deal"]["deal_id"] != ref["D"]:
        raise ValueError("credit_development_subject_mismatch")
    expected = {"CR01": (True, "calculated", Decimal("9160.00"),
                         Decimal("100.00"), Decimal("60.00"), Decimal("40.00")),
                "CR02": (False, "unknown", Decimal("9300.00"),
                         None, None, None),
                "CR03": (True, "infeasible", Decimal("10100.00"),
                         Decimal("1200.00"), Decimal("900.00"), Decimal("300.00"))}
    fresh, finding, exposure, original, outstanding, paid = expected[case_id]
    if (fixed["execution"] != "completed" or fixed["finding"] != finding or
            fixed["payload"]["commitments_fresh"] is not fresh or
            fixed["payload"]["credit_exposure"] != exposure or
            len(ar) != int(original is not None) or
            len(payments) != int(original is not None)):
        raise ValueError("credit_development_fixed_or_source_mismatch")
    if original is None:
        return
    invoice = "M21CD-INVOICE-" + case_id
    if (ar[0]["customer_id"] != ref["C"] or ar[0]["receivable_id"] != ref["AR"] or
            ar[0]["invoice_number"] != invoice or
            ar[0]["original_amount"] != original or
            ar[0]["outstanding_amount"] != outstanding or
            payments[0]["customer_id"] != ref["C"] or
            payments[0]["payment_id"] != ref["PAY"] or
            payments[0]["invoice_number"] != invoice or
            payments[0]["invoice_amount"] != original or
            payments[0]["paid_amount"] != paid or original - paid != outstanding):
        raise ValueError("credit_development_reconciliation_mismatch")
