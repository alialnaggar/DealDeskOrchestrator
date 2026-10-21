"""Compare the imported V1 catalogue with its pinned synthetic source drafts.

Run against a CSV exported inside the same PostgreSQL transaction that loaded
the 156-row catalogue. This proves import/source agreement, not market value.
"""

import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

import yaml

from render_phase1c_sellable_catalogue import product_rows
from validate_phase1c_variant_cost_pilot import evaluate_build_cost_draft


HERE = Path(__file__).resolve().parent
FIELDS = ("product_id", "catalog_version", "list_price", "standard_cost",
          "billing_model", "unit_of_measure", "fulfillment_mode", "is_sellable",
          "attributes_json")


def _money(value):
    if isinstance(value, bool):
        raise ValueError("boolean money")
    amount = Decimal(str(value))
    if not amount.is_finite():
        raise ValueError("nonfinite money")
    return amount


def _attributes(value):
    return json.loads(value) if isinstance(value, str) else value


def expected_rows(portfolio, costs, config, contract):
    cost_gate = evaluate_build_cost_draft(portfolio, costs, config)
    if cost_gate["errors"] or cost_gate["checked_products"] != 18 or cost_gate["checked_boms"] != 24:
        raise ValueError("buildable source cost/BOM reconciliation failed")
    products = {p["product_id"]: p for p in portfolio["products"]}
    if len(products) != 156 or len(costs["component_standard_costs_eur"]) != 36:
        raise ValueError("V1 catalogue source cardinality differs")
    expected = {}
    for row in product_rows(portfolio, costs, config, contract):
        pid, _, version, _, _, _, attrs, price, cost, billing, unit, sellable, mode, _ = row
        expected[pid] = (version, _money(price), _money(cost), billing, unit,
                         mode, sellable, attrs)
    for draft in costs["products"]:
        pid = draft["product_id"]
        expected[pid] = (portfolio["catalog_version"], _money(draft["product_list_price_eur"]),
                         _money(draft["product_standard_cost_eur"]), "one_time", "device",
                         "make_to_order", True, products[pid]["attributes_json"])
    for pid, cost in costs["component_standard_costs_eur"].items():
        expected[pid] = (portfolio["catalog_version"], Decimal(0), _money(cost),
                         "not_applicable", "component_unit", "component", False,
                         products[pid]["attributes_json"])
    if len(expected) != 156 or set(expected) != set(products):
        raise ValueError("V1 source rows are missing or duplicated")
    return expected, cost_gate


def audit(imported, portfolio, costs, config, contract):
    expected, cost_gate = expected_rows(portfolio, costs, config, contract)
    if len(imported) != 156 or any(set(row) != set(FIELDS) for row in imported):
        raise ValueError("imported V1 row count or fields differ")
    ids = [row["product_id"] for row in imported]
    if len(set(ids)) != 156 or set(ids) != set(expected):
        raise ValueError("imported V1 identities differ from source")
    for row in imported:
        pid = row["product_id"]
        try:
            actual = (row["catalog_version"], _money(row["list_price"]),
                      _money(row["standard_cost"]), row["billing_model"],
                      row["unit_of_measure"], row["fulfillment_mode"],
                      row["is_sellable"].lower() in {"true", "t"},
                      _attributes(row["attributes_json"]))
        except (InvalidOperation, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{pid}: malformed imported value") from exc
        if row["is_sellable"].lower() not in {"true", "false", "t", "f"} or actual != expected[pid]:
            raise ValueError(f"{pid}: imported catalogue differs from source")
    return {
        "basis": "synthetic_source_to_import_reconciliation_not_market_evidence",
        "v1_rows_reconciled": 156, "generated_sellable_reconciled": 102,
        "buildable_reconciled": cost_gate["checked_products"],
        "active_bom_rollups_checked": cost_gate["checked_boms"],
        "components_reconciled": 36,
        "market_comparability_verified": False,
        "accepted_evaluation_answers": 0,
        "ready_for_generation": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imported_csv", type=Path)
    args = parser.parse_args()
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    with args.imported_csv.open(newline="") as handle:
        imported = list(csv.DictReader(handle))
    print(json.dumps(audit(imported, portfolio, costs, config, contract), indent=2))


if __name__ == "__main__":
    main()
