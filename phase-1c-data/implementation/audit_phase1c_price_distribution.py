"""Measure the provisional 120-product catalogue without freezing calibration.

The 102 generated prices use a synthetic draw and a fixed category p50 margin.
The other 18 prices and costs are explicit buildable draft assumptions. These
statistics describe that fixture, not observed comparable market prices.
"""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json

import yaml

from render_phase1c_sellable_catalogue import product_rows


HERE = Path(__file__).resolve().parent
CENT = Decimal("0.01")


def number(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("price and cost must be finite")
    return result


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot summarize an empty group")
    position = (len(ordered) - 1) * Decimal(str(fraction))
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def rounded(value):
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def audit(portfolio, costs, config, contract):
    catalogue = {p["product_id"]: p for p in portfolio["products"] if p["is_sellable"]}
    buildable = {p["product_id"]: p for p in costs["products"]}
    if len(catalogue) != 120 or len(buildable) != 18 or not set(buildable) <= set(catalogue):
        raise ValueError("expected 120 sellable products and 18 distinct buildable costs")
    components = {p["product_id"] for p in portfolio["products"]
                  if p["fulfillment_mode"] == "component" and not p["is_sellable"]}
    component_costs = costs["component_standard_costs_eur"]
    if len(components) != 36 or set(component_costs) != components:
        raise ValueError("component costs must cover exactly 36 catalogue components")
    for pid, value in component_costs.items():
        if number(value) <= 0:
            raise ValueError(f"{pid}: component cost must be positive")
    generated = product_rows(portfolio, costs, config, contract)
    records = []
    reconciled_generated_costs = 0
    for row in generated:
        pid, _, _, _, category, _, _, price, cost, billing, unit, _, mode, _ = row
        p50 = number(config["commercial_supply"]["standard_cost"]
                     ["target_list_margin_percent_by_category"][category]["p50"])
        expected = (number(price) * (1 - p50 / 100)).quantize(CENT, rounding=ROUND_HALF_UP)
        if number(cost) != expected:
            raise ValueError(f"{pid}: generated cost does not reconcile to fixed category p50")
        reconciled_generated_costs += 1
        records.append((pid, category, mode, billing, unit, number(price), number(cost), "generated"))
    for pid, draft in buildable.items():
        product = catalogue[pid]
        if product["fulfillment_mode"] != "make_to_order":
            raise ValueError(f"{pid}: build cost does not describe a make-to-order product")
        records.append((pid, product["attributes_json"]["category"], "make_to_order",
                        "one_time", "device", number(draft["product_list_price_eur"]),
                        number(draft["product_standard_cost_eur"]), "buildable_draft"))
    if len(records) != 120 or {r[0] for r in records} != set(catalogue):
        raise ValueError("the priced records must cover the sellable catalogue exactly once")

    by_category = defaultdict(list)
    price_groups = defaultdict(list)
    outside_anchor_span = []
    mismatched_category_units = []
    anchor_span_checked_count = 0
    for pid, category, mode, billing, unit, price, cost, source in records:
        if price <= 0 or cost < 0 or cost > price:
            raise ValueError(f"{pid}: invalid price/cost")
        margin = (price - cost) / price * 100
        by_category[category].append((pid, margin, source))
        price_groups[(category, billing, unit)].append(price)
        category_config = config["product_catalogue"]["categories"][category]
        declared_unit = category_config["default_unit_of_measure"]
        if unit != declared_unit:
            mismatched_category_units.append({
                "product_id": pid, "source": source, "category": category,
                "product_unit": unit, "category_default_unit": declared_unit,
            })
            continue
        anchor_span_checked_count += 1
        anchor = category_config["price_eur"]
        if price < number(anchor["p10"]) or price > number(anchor["p90"]):
            outside_anchor_span.append({"product_id": pid, "source": source,
                                        "category": category, "price_eur": rounded(price)})
    targets = config["commercial_supply"]["standard_cost"]["target_list_margin_percent_by_category"]
    categories = []
    for category in sorted(by_category):
        rows = by_category[category]
        margins = [r[1] for r in rows]
        target = targets[category]
        p50 = number(target["p50"])
        p90 = number(target["p90"])
        categories.append({
            "category": category, "count": len(rows),
            "generated_count": sum(r[2] == "generated" for r in rows),
            "buildable_draft_count": sum(r[2] == "buildable_draft" for r in rows),
            "margin_pct_p10": rounded(percentile(margins, "0.1")),
            "margin_pct_p50": rounded(percentile(margins, "0.5")),
            "margin_pct_p90": rounded(percentile(margins, "0.9")),
            "proposed_margin_p50_pct": rounded(p50),
            "proposed_margin_p90_pct": rounded(p90),
            "generated_at_proposed_p50": sum(r[2] == "generated" and
                                             abs(r[1] - p50) < Decimal("0.01")
                                             for r in rows),
            "above_proposed_p90": sorted(r[0] for r in rows if r[1] > p90),
        })
    groups = [
        {"category": category, "billing_model": billing, "unit_of_measure": unit,
         "count": len(prices), "price_eur_p10": rounded(percentile(prices, "0.1")),
         "price_eur_p50": rounded(percentile(prices, "0.5")),
         "price_eur_p90": rounded(percentile(prices, "0.9"))}
        for (category, billing, unit), prices in sorted(price_groups.items())
    ]
    return {
        "basis": "provisional_synthetic_fixture_not_market_comparables",
        "sellable_count": len(records), "generated_count": len(generated),
        "buildable_draft_count": len(buildable), "categories": categories,
        "price_groups": groups, "component_costs_checked": len(component_costs),
        "generated_fixed_p50_costs_reconciled": reconciled_generated_costs,
        "category_default_unit_match_count": anchor_span_checked_count,
        "category_default_unit_mismatches": sorted(mismatched_category_units,
                                                     key=lambda row: row["product_id"]),
        "outside_synthetic_p10_p90_anchor_span": outside_anchor_span,
        "anchor_span_is_hard_price_limit": False,
        "price_comparability_verified": False,
        "calibration_frozen": False, "ready_for_generation": False,
    }


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    print(json.dumps(audit(portfolio, costs, config, contract), indent=2))


