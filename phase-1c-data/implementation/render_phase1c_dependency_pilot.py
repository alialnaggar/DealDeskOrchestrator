"""Render a small V2 catalogue slice with two dependency submissions.

V1's 156 product rows, 36 development deals and 400 historical inputs remain
unchanged. The V2 rows reuse the fictional specifications and prices of two
V1 stocked products, with new immutable IDs and a version-scoped rule.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL_PATH = HERE / "phase1c_dependency_pilot.sql"
BASE_SOURCE = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-004"
BASE_TARGET = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005"
SOURCE = BASE_SOURCE + "-V2"
TARGET = BASE_TARGET + "-V2"
CATALOG = "CATALOGUE_2026_V2"
RULE_ID = "V2-REQUIRES-ADDON"
CASES = ((21, False), (22, True))
PRODUCT_COLUMNS = ("product_id", "product_code", "catalog_version", "product_name",
                   "category", "product_type", "attributes_json", "list_price",
                   "standard_cost", "billing_model", "unit_of_measure", "is_active",
                   "is_sellable", "fulfillment_mode", "stock_uom")


def quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return "'" + str(value).replace("'", "''") + "'"


def insert(table, record):
    return (f"INSERT INTO {table} ({', '.join(record)}) VALUES ("
            + ", ".join(quote(value) for value in record.values()) + ");\n")


def build():
    rows = ["-- V2 dependency slice; import after the 36-deal pilot. No answer keys.\n",
            "SET search_path TO deal_desk, public;\n"]
    for base, clone in ((BASE_SOURCE, SOURCE), (BASE_TARGET, TARGET)):
        selected = [quote(clone), "product_code", quote(CATALOG),
                    *PRODUCT_COLUMNS[3:]]
        rows.append(f"INSERT INTO products ({', '.join(PRODUCT_COLUMNS)}) "
                    f"SELECT {', '.join(selected)} FROM products "
                    f"WHERE product_id={quote(base)} AND catalog_version='CATALOGUE_2026_V1';\n")
    rows.append(insert("compatibility_rules", dict(
        compatibility_rule_id=RULE_ID, catalog_version=CATALOG,
        rule_name="Synthetic V2 product dependency", rule_type="requires_product",
        scope_type="whole_deal", source_product_id=SOURCE, target_product_id=TARGET,
        condition_json={"operator": "present"}, severity="blocker",
        message="Add-on required", priority=1)))
    for number, product in enumerate((SOURCE, TARGET), 1):
        rows.append(insert("inventory", dict(
            inventory_id=f"DEP-V2-STOCK-{number}", product_id=product,
            location_id="WH-EU-CENTRAL", quantity_on_hand=2, quantity_allocated=0,
            snapshot_at="2026-09-01T09:00:00Z")))
    for index, include_target in CASES:
        deal = f"DEP-V2-DEAL-{index}"
        rows.append(insert("deals", dict(
            deal_id=deal, customer_id="CONFLICT-CUST-06", salesperson_id="SALES-001",
            deal_name="Versioned dependency input",
            submitted_at="2026-09-01T10:00:00Z",
            catalog_version=CATALOG, policy_set_code="BASELINE_2026",
            requested_delivery_date="2026-09-10",
            destination_country_code="DE", destination_region="DE-NW",
            shipping_service_code="standard",
            terms_json={"payment_terms_days": 30, "contract_clause_codes": ["standard"],
                        "allow_partial_delivery": False},
            deal_status="Draft", dataset_type="generated_test")))
        for number, product in enumerate((SOURCE, TARGET) if include_target else (SOURCE,), 1):
            rows.append("INSERT INTO deal_lines "
                        "(deal_line_id,deal_id,line_number,product_id,quantity,"
                        "quoted_unit_price,configuration_json) "
                        f"SELECT {quote(f'DEP-V2-LINE-{index}-{number}')}, {quote(deal)}, "
                        f"{number}, product_id, 1, list_price, '{{}}' "
                        f"FROM products WHERE product_id={quote(product)};\n")
        rows.append(f"UPDATE deals SET deal_status='Submitted' WHERE deal_id={quote(deal)};\n")
        rows.append(insert("deal_runs", dict(
            run_id=f"00000000-0000-4000-8000-{270000 + index:012d}",
            deal_id=deal, original_policy_set_code="BASELINE_2026",
            applied_policy_set_code="BASELINE_2026", catalog_version_used=CATALOG,
            as_of_at="2026-09-01T12:00:00Z",
            data_snapshot_ref="DEP-V2-SNAPSHOT", input_snapshot_json={},
            config_hash="dependency-v2-pilot", run_status="queued",
            started_at="2026-09-01T12:00:00Z")))
    return "".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sql = build()
    if args.check:
        if SQL_PATH.read_text() != sql:
            raise SystemExit("V2 dependency pilot differs from generator")
    else:
        SQL_PATH.write_text(sql)
    print(hashlib.sha256(sql.encode()).hexdigest())


if __name__ == "__main__":
    main()
