"""Produce a source-only V1 price/cost provenance ledger for field review.

The separate review convention is proposed, never injected into source inputs.
"""

from collections import Counter
import json
from pathlib import Path

import yaml

from audit_phase1c_catalogue_import import expected_rows
from audit_phase1c_price_distribution import audit as price_audit


HERE = Path(__file__).resolve().parent


def audit(portfolio, costs, config, contract, review):
    version = portfolio["catalog_version"]
    if (review["catalog_version"] != version or review["currency"] != config["currency"]
            or review["status"] != "proposed_synthetic_convention_for_review_not_calibration_freeze"
            or review["ready_for_generation"] is not False):
        raise ValueError("review scope, currency or provisional status differs")
    expected, _ = expected_rows(portfolio, costs, config, contract)
    provenance_keys = {"price_observed_at", "price_observation_date",
                       "price_effective_from", "price_effective_until",
                       "list_price_tax_basis", "standard_cost_tax_basis"}
    source_records = portfolio["products"] + costs["products"]
    if any(provenance_keys & (set(row) | set(row.get("attributes_json", {})))
           for row in source_records):
        raise ValueError("SKU price provenance has changed; review the zero-coverage claims")
    price_report = price_audit(portfolio, costs, config, contract)
    mismatched = {row["product_id"] for row in
                  price_report["category_default_unit_mismatches"]}
    generated = {pid for pid, row in expected.items()
                 if row[5] not in ("make_to_order", "component")}
    buildable = {p["product_id"] for p in costs["products"]}
    categories = config["product_catalogue"]["categories"]
    rows = []
    for pid, (catalogue, price, cost, billing, unit, mode, sellable, attrs) in sorted(expected.items()):
        category = attrs.get("category") if sellable else None
        if catalogue != version or (sellable and category not in categories):
            raise ValueError(f"{pid}: version or category mismatch")
        if sellable and (price <= 0 or cost < 0 or cost > price):
            raise ValueError(f"{pid}: invalid sellable commercial value")
        if not sellable and (price != 0 or cost <= 0 or unit != "component_unit"):
            raise ValueError(f"{pid}: invalid component commercial value")
        origin = ("component_draft" if mode == "component" else
                  "buildable_bom_draft" if pid in buildable else "seeded_category_draw_and_fixed_p50")
        rows.append({"product_id": pid, "mode": mode, "category": category,
                     "currency": review["currency"], "unit_of_measure": unit,
                     "billing_model": billing, "list_price_eur": str(price),
                     "standard_cost_eur": str(cost), "source_class": origin,
                     "category_default_unit_matches": pid not in mismatched if sellable else None,
                     "external_like_for_like_price_verified": False,
                     "per_sku_observation_date_recorded": False,
                     "per_sku_effective_interval_recorded": False})
    counts = Counter(row["source_class"] for row in rows)
    if len(rows) != 156 or len(generated) != 102 or counts != {
            "component_draft": 36, "buildable_bom_draft": 18,
            "seeded_category_draw_and_fixed_p50": 102}:
        raise ValueError("source classification coverage differs")
    return {
        "basis": "source_only_review_ledger_not_a_released_price_contract",
        "review_status": review["status"], "catalog_version": version,
        "currency": review["currency"], "catalogue_calibrated_on": str(
            config["product_catalogue"]["metadata"]["calibrated_on"]),
        "fx_reference_date": str(config["product_catalogue"]["metadata"]
                                 ["usd_normalization"]["reference_date"]),
        "portfolio_as_of_at": portfolio["as_of_at"],
        "source_class_counts": dict(sorted(counts.items())),
        "sellable_unit_mismatches": len(mismatched),
        "sku_observation_dates_recorded": 0,
        "sku_price_effective_intervals_recorded": 0,
        "tax_basis_for_v1": "proposed_synthetic_tax_exclusive_not_yet_dispositioned",
        "rows": rows, "accepted_evaluation_answers": 0,
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    review = json.loads((HERE / "phase1c_v1_price_basis_review.json").read_text())
    print(json.dumps(audit(portfolio, costs, config, contract, review), indent=2))
