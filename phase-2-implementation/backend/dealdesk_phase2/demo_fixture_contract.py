"""Narrow synthetic-case fingerprint; not a financial rule or a verifier replacement."""

from decimal import Decimal

from .phase1c_adapter import EvidenceMismatch


def verify_demo_fixture(pool, fixed, scenario):
    if scenario not in ("B01/RC01", "N01/UC02"):
        raise EvidenceMismatch("Demo fixture not allowlisted")
    case, variant = scenario.split("/")
    profile, ar, payments = pool["credit"], pool["receivables"], pool["payments"]
    expected = ({"RC01": ("Active", "calculated", True, "9160.00", "100.00", 1),
                 "UC02": ("Review", "unknown", False, "9300.00", "300.00", 0)}[variant])
    status, finding, fresh, exposure, committed, count = expected
    if (pool["deal"].get("deal_id") != "M18-D-" + case or
            profile.get("customer_id") != "M18-C-" + case or
            profile.get("credit_status") != status or
            profile.get("unbilled_committed_amount") != Decimal(committed) or
            fixed.get("execution") != "completed" or fixed.get("finding") != finding or
            fixed["payload"].get("commitments_fresh") is not fresh or
            fixed["payload"].get("credit_exposure") != Decimal(exposure) or
            len(ar) != count or len(payments) != count):
        raise EvidenceMismatch("Synthetic source variant or fixed credit differs")
    if count and (ar[0].get("customer_id") != profile["customer_id"] or
            payments[0].get("customer_id") != profile["customer_id"] or
            ar[0].get("receivable_id") != "M21IC-AR-RC01" or
            payments[0].get("payment_id") != "M21IC-PAY-RC01" or
            ar[0].get("invoice_number") != payments[0].get("invoice_number") or
            ar[0].get("original_amount") != Decimal("100.00") or
            ar[0].get("outstanding_amount") != Decimal("60.00") or
            payments[0].get("paid_amount") != Decimal("40.00")):
        raise EvidenceMismatch("Synthetic reconciled credit fingerprint differs")
