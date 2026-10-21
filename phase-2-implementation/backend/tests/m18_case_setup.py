"""Phase 2-only disposable PostgreSQL cases; never imported by the agent.

Every case has its own customer, product, location, shipping lane, stock,
purchase order, inbound source, deal, line and run. CI's database is disposable.
The declared expectations live in a separate reviewer-only document.
"""

from dataclasses import dataclass
import json
from uuid import UUID


@dataclass(frozen=True)
class SourceCase:
    case_id: str
    quantity: int
    requested_date: str
    stock_total: int
    stock_allocated: int
    inbound_total: int
    inbound_allocated: int
    inbound_date: str
    transit_days: int
    partial_allowed: bool = True
    inbound_status: str = "Confirmed"
    stock_snapshot: str = "2026-09-01 10:00+00"

    @property
    def run_id(self) -> UUID:
        suffix = (18000 if self.case_id.startswith("B") else 18100) + int(self.case_id[-2:])
        return UUID(f"00000000-0000-4000-8000-{suffix:012d}")

    def ids(self) -> dict[str, str]:
        return {kind: f"M18-{kind}-{self.case_id}" for kind in
                ("C", "P", "S", "PO", "IN", "INV", "LANE", "D", "L", "WH")}


# Meaningful variations: allocation, requested date, confirmed inbound date,
# quantity and shipping transit. B01 is the 8+2 reference-source shape; the
# other cases have distinct evidence rows. Ali's 2026-10-21 developer-side
# acceptance is recorded separately from these model-blind synthetic inputs.
CASES = (
    SourceCase("B01", 10, "2026-09-04", 20, 12, 5, 2, "2026-09-03", 2),
    SourceCase("B02", 14, "2026-09-04", 9, 3, 12, 2, "2026-09-04", 1),
    SourceCase("B03", 15, "2026-09-07", 16, 12, 20, 4, "2026-09-07", 2),
    SourceCase("B04", 9, "2026-09-08", 15, 12, 12, 4, "2026-09-08", 2),
    SourceCase("B05", 18, "2026-09-04", 20, 9, 15, 5, "2026-09-09", 1),
    SourceCase("N01", 10, "2026-09-04", 20, 12, 5, 2, "2026-09-03", 2,
               partial_allowed=False),
    SourceCase("N02", 10, "2026-09-04", 20, 12, 5, 2, "2026-09-03", 2,
               inbound_status="Cancelled"),
    SourceCase("N03", 10, "2026-09-04", 20, 12, 0, 0, "2026-09-03", 2,
               stock_snapshot="2026-08-28 10:00+00"),
    SourceCase("N04", 10, "2026-09-04", 0, 0, 0, 0, "2026-09-03", 2),
)


def install_disposable_cases(connection):
    """Write only to CI's disposable business database, never to Phase 1C files.

    Copy master attributes from the pinned reference row, with a distinct
    product/customer/source identity for every case. The exact fixed reader
    and business rules later decide all outcomes; no rule is encoded here.
    """
    with connection:
        # The pinned schema's operational triggers use unqualified table names.
        # Scope this only to the disposable fixture-write transaction.
        connection.execute("SET LOCAL search_path TO deal_desk, public")
        found = connection.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]
        if found:
            raise RuntimeError("M1.8 case database is not fresh; refusing duplicate or mixed sources")
        for case in CASES:
            ids = case.ids()
            connection.execute("""INSERT INTO deal_desk.customers
                (customer_id, customer_code, customer_name, size_segment, strategic_account,
                 industry, country_code, region, customer_since, account_status)
                SELECT %s, %s, %s, size_segment, strategic_account, industry, country_code,
                       region, customer_since, account_status
                FROM deal_desk.customers WHERE customer_id='C-stock_then_confirmed_receipt'""",
                (ids["C"], ids["C"], "Disposable " + case.case_id))
            connection.execute("""INSERT INTO deal_desk.customer_credit_profiles
                (customer_id, credit_limit, unbilled_committed_amount, commitments_as_of_at,
                 commitment_evidence_ref, risk_rating, credit_status,
                 default_payment_terms_days, last_review_date, next_review_date)
                SELECT %s, credit_limit, unbilled_committed_amount, commitments_as_of_at,
                       %s, risk_rating, credit_status, default_payment_terms_days,
                       last_review_date, next_review_date
                FROM deal_desk.customer_credit_profiles
                WHERE customer_id='C-stock_then_confirmed_receipt'""",
                (ids["C"], "M18-COMMIT-" + case.case_id))
            connection.execute("""INSERT INTO deal_desk.products
                (product_id, product_code, catalog_version, product_name, category,
                 product_type, attributes_json, list_price, standard_cost, billing_model,
                 unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom)
                SELECT %s, %s, catalog_version, %s, category, product_type,
                       attributes_json, list_price, standard_cost, billing_model,
                       unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom
                FROM deal_desk.products WHERE product_id='stock_then_confirmed_receipt-P'""",
                (ids["P"], ids["P"], "Disposable " + case.case_id))
            connection.execute("""INSERT INTO deal_desk.shipping_lanes
                (lane_id, origin_location_id, origin_time_zone, destination_country_code,
                 destination_region, shipping_service_code, transit_workdays,
                 dispatch_weekdays_json, cutoff_local_time, is_active)
                SELECT %s, %s, origin_time_zone, destination_country_code,
                       destination_region, shipping_service_code, %s,
                       dispatch_weekdays_json, cutoff_local_time, is_active
                FROM deal_desk.shipping_lanes WHERE lane_id='LANE-stock_then_confirmed_receipt'""",
                (ids["LANE"], ids["WH"], case.transit_days))
            if case.stock_total:
                connection.execute("""INSERT INTO deal_desk.inventory
                    (inventory_id, product_id, location_id, quantity_on_hand,
                     quantity_allocated, snapshot_at) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (ids["INV"], ids["P"], ids["WH"], case.stock_total,
                     case.stock_allocated, case.stock_snapshot))
            if case.inbound_total:
                connection.execute("""INSERT INTO deal_desk.purchase_orders
                    (purchase_order_id, supplier_id, reference_number, ordered_at,
                     confirmed_at, status, destination_location_id)
                    SELECT %s, supplier_id, %s, ordered_at, confirmed_at,
                           %s, %s FROM deal_desk.purchase_orders
                    WHERE purchase_order_id='PO-stock_then_confirmed_receipt'""",
                    (ids["PO"], ids["PO"], case.inbound_status, ids["WH"]))
                connection.execute("""INSERT INTO deal_desk.inbound_supply
                    (supply_id, purchase_order_id, product_id, location_id, quantity,
                     quantity_allocated, expected_date, confirmed_at, status,
                     reference_number, evidence_ref, valid_until)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (ids["IN"], ids["PO"], ids["P"], ids["WH"], case.inbound_total,
                     case.inbound_allocated, case.inbound_date,
                     "2026-08-31 10:00+00" if case.inbound_status == "Confirmed" else None,
                     case.inbound_status, ids["IN"], "M18-BIND-" + case.case_id,
                     "2026-09-30 00:00+00" if case.inbound_status == "Confirmed" else None))
            connection.execute("""INSERT INTO deal_desk.deals
                (deal_id, customer_id, salesperson_id, deal_name, submitted_at,
                 currency_code, catalog_version, policy_set_code, requested_delivery_date,
                 destination_country_code, destination_region, shipping_service_code,
                 terms_json, deal_status, dataset_type)
                VALUES (%s,%s,'M18-EVAL','M1.8 provisional case','2026-09-01 09:00+00',
                'EUR','CATALOGUE_2026_V1','BASELINE_2026',%s,'DE','Berlin','standard',
                %s,'Draft','generated_test')""",
                (ids["D"], ids["C"], case.requested_date,
                 json.dumps({"allow_partial_delivery": case.partial_allowed,
                     "contract_clause_codes": ["standard"], "payment_terms_days": 30})))
            connection.execute("""INSERT INTO deal_desk.deal_lines
                (deal_line_id,deal_id,line_number,product_id,quantity,quoted_unit_price,
                 configuration_json) VALUES (%s,%s,1,%s,%s,900,'{}')""",
                (ids["L"], ids["D"], ids["P"], case.quantity))
            connection.execute("UPDATE deal_desk.deals SET deal_status='Submitted' WHERE deal_id=%s",
                               (ids["D"],))
            connection.execute("""INSERT INTO deal_desk.deal_runs
                (run_id,deal_id,original_policy_set_code,applied_policy_set_code,
                 catalog_version_used,as_of_at,data_snapshot_ref,input_snapshot_json,
                 config_hash,run_status,started_at)
                VALUES (%s,%s,'BASELINE_2026','BASELINE_2026','CATALOGUE_2026_V1',
                '2026-09-01 12:00+00',%s,%s,'M18-CONFIG','queued','2026-09-01 12:00+00')""",
                (case.run_id, ids["D"], "M18-SNAPSHOT-" + case.case_id,
                 json.dumps({"deal_id": ids["D"], "case_id": case.case_id})))
