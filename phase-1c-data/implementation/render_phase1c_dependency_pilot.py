"""Reproducible, isolated dependency pair for the synthetic pilot.

This fixture is loaded inside a savepoint. The current rule language applies
to every deal containing its source SKU, so it must not enter the shared
catalogue/pilot or historical baseline without a reviewed scope decision.
"""

import hashlib
import json
from pathlib import Path

from render_phase1c_vertical_pilot import insert, quote

HERE = Path(__file__).resolve().parent
SOURCE = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-004"
TARGET = "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005"
RULE_ID = "TRIAL-REQUIRES-ADDON"
CASES = ((21, False), (22, True))


def build(portfolio):
    products = {row["product_id"]: row for row in portfolio["products"]}
    if any(products.get(product, {}).get("fulfillment_mode") != "stocked_finished"
           for product in (SOURCE, TARGET)):
        raise ValueError("dependency fixture product scope changed")
    if any(product in (SOURCE, TARGET) for product in
           ("SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001",
            "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-006")):
        raise ValueError("fixture overlaps primary pilot paths")
    rows = ["-- Isolated generated dependency cases; never import into shared baseline.\n",
            "SET search_path TO deal_desk, public;\n"]
    rows.append(insert("compatibility_rules", dict(
        compatibility_rule_id=RULE_ID, catalog_version="CATALOGUE_2026_V1",
        rule_name="Synthetic product dependency", rule_type="requires_product",
        scope_type="whole_deal", source_product_id=SOURCE, target_product_id=TARGET,
        condition_json={"operator": "present"}, severity="blocker",
        message="Add-on required", priority=1)))
    for index, include_target in CASES:
        deal = f"DEP-TRIAL-{index}"
        rows.append(insert("deals", dict(
            deal_id=deal, customer_id="CONFLICT-CUST-06", salesperson_id="SALES-001",
            deal_name="Dependency coverage input", submitted_at="2026-09-01T10:00:00Z",
            catalog_version="CATALOGUE_2026_V1", policy_set_code="BASELINE_2026",
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
                        f"SELECT {quote(f'DEP-LINE-{index}-{number}')}, {quote(deal)}, "
                        f"{number}, product_id, 1, list_price, '{{}}' "
                        f"FROM products WHERE product_id={quote(product)};\n")
        rows.append(f"UPDATE deals SET deal_status='Submitted' WHERE deal_id={quote(deal)};\n")
        rows.append(insert("deal_runs", dict(
            run_id=f"00000000-0000-4000-8000-{270000 + index:012d}",
            deal_id=deal, original_policy_set_code="BASELINE_2026",
            applied_policy_set_code="BASELINE_2026",
            catalog_version_used="CATALOGUE_2026_V1",
            as_of_at="2026-09-01T12:00:00Z",
            data_snapshot_ref="DEP-TRIAL-SNAPSHOT", input_snapshot_json={},
            config_hash="dependency-trial", run_status="queued",
            started_at="2026-09-01T12:00:00Z")))
    return "".join(rows)


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    print(hashlib.sha256(build(portfolio).encode()).hexdigest())
