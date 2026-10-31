"""Opt-in synthetic Credit overlays on existing B01/N01 disposable sources.

Never apply to Phase 1C or shared CI databases. The caller must provision an
exclusive fresh business/checkpoint pair and run this before pinning evidence.
"""

from decimal import Decimal


VARIANTS = {"RC01": "B01", "HC03": "N01", "UC02": "N01"}


def install_integrated_credit(connection, *, case_id, variant):
    if VARIANTS.get(variant) != case_id:
        raise ValueError("integrated_credit_variant_not_allowed")
    customer = "M18-C-" + case_id
    with connection:
        connection.execute("SET LOCAL search_path TO deal_desk, public")
        if (connection.execute("SELECT count(*) FROM deals WHERE deal_id=%s AND "
                "customer_id=%s AND dataset_type='generated_test'",
                ("M18-D-" + case_id, customer)).fetchone()[0] != 1 or
                connection.execute("SELECT count(*) FROM accounts_receivable "
                    "WHERE customer_id=%s", (customer,)).fetchone()[0] or
                connection.execute("SELECT count(*) FROM payment_history "
                    "WHERE customer_id=%s", (customer,)).fetchone()[0]):
            raise ValueError("integrated_credit_source_not_exclusive_baseline")
        limit, committed, dated, risk, status = {
            "RC01": (Decimal("10000.00"), Decimal("100.00"),
                     "2026-09-01 10:00+00", "Low", "Active"),
            "HC03": (Decimal("1500.00"), Decimal("200.00"),
                     "2026-09-01 10:00+00", "High", "On-Hold"),
            "UC02": (Decimal("5000.00"), Decimal("300.00"),
                     "2026-08-01 10:00+00", "High", "Review")}[variant]
        if connection.execute("UPDATE customer_credit_profiles SET credit_limit=%s, "
                "unbilled_committed_amount=%s, commitments_as_of_at=%s, "
                "risk_rating=%s, credit_status=%s WHERE customer_id=%s",
                (limit, committed, dated, risk, status, customer)).rowcount != 1:
            raise ValueError("integrated_credit_missing_profile")
        if variant == "UC02":
            return
        original, outstanding, paid, ar_status, due = (
            (Decimal("100.00"), Decimal("60.00"), Decimal("40.00"),
             "Partially Paid", "2026-09-15") if variant == "RC01" else
            (Decimal("1200.00"), Decimal("900.00"), Decimal("300.00"),
             "Overdue", "2026-08-15"))
        invoice = "M21IC-INVOICE-" + variant
        connection.execute("""INSERT INTO accounts_receivable
            (receivable_id,customer_id,invoice_number,invoice_date,due_date,
             original_amount,outstanding_amount,status,as_of_date)
            VALUES (%s,%s,%s,'2026-08-01',%s,%s,%s,%s,'2026-09-01')""",
            ("M21IC-AR-" + variant, customer, invoice, due, original,
             outstanding, ar_status))
        connection.execute("""INSERT INTO payment_history
            (payment_id,customer_id,invoice_number,invoice_date,due_date,
             paid_date,invoice_amount,paid_amount)
             VALUES (%s,%s,%s,'2026-08-01',%s,'2026-08-20',%s,%s)""",
            ("M21IC-PAY-" + variant, customer, invoice, due, original, paid))


def verify_integrated_credit(pool, fixed, *, case_id, variant):
    if VARIANTS.get(variant) != case_id:
        raise ValueError("integrated_credit_variant_not_allowed")
    profile = pool["credit"]
    ar, payments = pool["receivables"], pool["payments"]
    expected = {
        "RC01": (True, "calculated", Decimal("9160.00"), "Active",
                 Decimal("100.00"), Decimal("60.00"), Decimal("40.00")),
        "HC03": (True, "infeasible", Decimal("10100.00"), "On-Hold",
                 Decimal("1200.00"), Decimal("900.00"), Decimal("300.00")),
        "UC02": (False, "unknown", Decimal("9300.00"), "Review",
                 None, None, None),
    }[variant]
    fresh, finding, exposure, status, original, outstanding, paid = expected
    if (pool["deal"]["deal_id"] != "M18-D-" + case_id or
            profile["customer_id"] != "M18-C-" + case_id or
            profile["credit_status"] != status or
            fixed["execution"] != "completed" or fixed["finding"] != finding or
            fixed["payload"]["commitments_fresh"] is not fresh or
            fixed["payload"]["credit_exposure"] != exposure or
            len(ar) != int(original is not None) or
            len(payments) != int(original is not None)):
        raise ValueError("integrated_credit_fixed_or_source_mismatch")
    if original is None:
        return
    invoice = "M21IC-INVOICE-" + variant
    if (ar[0]["customer_id"] != profile["customer_id"] or
            ar[0]["receivable_id"] != "M21IC-AR-" + variant or
            ar[0]["invoice_number"] != invoice or
            ar[0]["original_amount"] != original or
            ar[0]["outstanding_amount"] != outstanding or
            payments[0]["customer_id"] != profile["customer_id"] or
            payments[0]["payment_id"] != "M21IC-PAY-" + variant or
            payments[0]["invoice_number"] != invoice or
            payments[0]["invoice_amount"] != original or
            payments[0]["paid_amount"] != paid or original - paid != outstanding):
        raise ValueError("integrated_credit_reconciliation_mismatch")
