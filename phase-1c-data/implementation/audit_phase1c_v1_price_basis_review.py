"""Produce a source-only V1 price/cost provenance ledger for field review.

The selected fictional convention is recorded separately from pinned source inputs.
"""

from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import re

import yaml

from audit_phase1c_catalogue_import import expected_rows
from audit_phase1c_price_distribution import audit as price_audit


HERE = Path(__file__).resolve().parent


HISTORICAL_DEAL = re.compile(
    r"^INSERT INTO deals .*? VALUES \('(HIST-DEAL-\d+)', '[^']+', '[^']+', "
    r"'[^']+', '([^']+)'", re.MULTILINE)


def audit(portfolio, costs, config, contract, review, historical_sql):
    version = portfolio["catalog_version"]
    if (review["catalog_version"] != version or review["currency"] != config["currency"]
            or review["status"] != "approved_bounded_synthetic_v1_convention_not_calibration_release"
            or review["decision"] != "Ali selected bounded synthetic V1 convention on 22 October 2026; this does not approve market comparability, historical price validity or evaluation answers."
            or review["quote_arithmetic_basis"] != "Fictional tax-exclusive list price and standard cost per stored product unit; no freight or tax adjustment is included in catalogue margin arithmetic."
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
    historical = HISTORICAL_DEAL.findall(historical_sql)
    if len(historical) != 400 or len({deal for deal, _ in historical}) != 400:
        raise ValueError("historical submission date coverage differs")
    dates = [datetime.fromisoformat(submitted).date() for _, submitted in historical]
    calibrated = date.fromisoformat(str(config["product_catalogue"]["metadata"]["calibrated_on"]))
    return {
        "basis": "source_only_bounded_synthetic_v1_convention_not_market_calibration",
        "review_status": review["status"], "catalog_version": version,
        "currency": review["currency"], "catalogue_calibrated_on": str(
            config["product_catalogue"]["metadata"]["calibrated_on"]),
        "fx_reference_date": str(config["product_catalogue"]["metadata"]
                                 ["usd_normalization"]["reference_date"]),
        "portfolio_as_of_at": portfolio["as_of_at"],
        "historical_submission_dates": {
            "count": len(dates), "earliest": min(dates).isoformat(),
            "latest": max(dates).isoformat(),
            "before_catalogue_research_calibration_date": sum(d < calibrated for d in dates),
        },
        "source_class_counts": dict(sorted(counts.items())),
        "sellable_unit_mismatches": len(mismatched),
        "sku_observation_dates_recorded": 0,
        "sku_price_effective_intervals_recorded": 0,
        "tax_basis_for_v1": "approved_fictional_tax_exclusive_per_stored_unit",
        "rows": rows, "accepted_evaluation_answers": 0,
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    review = json.loads((HERE / "phase1c_v1_price_basis_review.json").read_text())
    historical_sql = "\n".join((HERE / f"phase1c_historical_inputs_{n:02d}.sql").read_text()
                               for n in range(1, 9))
    print(json.dumps(audit(portfolio, costs, config, contract, review, historical_sql), indent=2))
