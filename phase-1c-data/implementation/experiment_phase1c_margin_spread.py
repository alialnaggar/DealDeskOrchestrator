"""Compare a bounded synthetic cost spread with the unchanged catalogue fixture.

This read-only experiment never emits SQL and does not change the price
generator, buildable BOM costs, calibration or policy configuration.
"""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from pathlib import Path
import json

import yaml

from audit_phase1c_price_distribution import number, percentile, rounded
from render_phase1c_sellable_catalogue import product_rows


HERE = Path(__file__).resolve().parent
CENT = Decimal("0.01")


def proposed_margin(rank, count, target):
    """Assign seeded ranks to the declared p10/p50/p90 band, with no tails."""
    u = (Decimal(rank) + Decimal("0.5")) / Decimal(count)
    low, mid, high = (number(target[key]) for key in ("p10", "p50", "p90"))
    if not 0 < low <= mid <= high < 100:
        raise ValueError("invalid bounded margin band")
    if u <= Decimal("0.1"):
        return low
    if u <= Decimal("0.5"):
        return low + (mid - low) * (u - Decimal("0.1")) / Decimal("0.4")
    if u < Decimal("0.9"):
        return mid + (high - mid) * (u - Decimal("0.5")) / Decimal("0.4")
    return high


def floor_status(price, cost, floor, discount=Decimal("0.10")):
    quote = price * (1 - discount)
    margin = (quote - cost) / quote * 100
    return "nonpositive" if margin <= 0 else "below_floor" if margin < floor else "at_or_above_floor"


def experiment(portfolio, costs, config, contract):
    generated = product_rows(portfolio, costs, config, contract)
    by_category = defaultdict(list)
    for row in generated:
        by_category[row[4]].append(row)
    buildable = {p["product_id"]: p for p in costs["products"]}
    sellable = {p["product_id"]: p for p in portfolio["products"] if p["is_sellable"]}
    if (len(generated) != 102 or len(buildable) != 18 or len(sellable) != 120 or
            (set(buildable) | {row[0] for row in generated}) != set(sellable)):
        raise ValueError("expected complete 102 + 18 sellable catalogue")
    targets = config["commercial_supply"]["standard_cost"]["target_list_margin_percent_by_category"]
    floors = config["governance"]["profiles"]["BASELINE_2026"]["pricing"]["category_margin_floor_pct"]
    seed = config["random_seed"]
    records = {}
    for category, rows in by_category.items():
        ordered = sorted(rows, key=lambda row: (
            sha256(f"{seed}:{row[0]}".encode()).hexdigest(), row[0]))
        for rank, row in enumerate(ordered):
            pid, price, original_cost = row[0], number(row[7]), number(row[8])
            margin = proposed_margin(rank, len(rows), targets[category])
            alternative_cost = (price * (1 - margin / 100)).quantize(CENT, rounding=ROUND_HALF_UP)
            if not 0 <= alternative_cost <= price:
                raise ValueError(f"{pid}: invalid experimental cost")
            records[pid] = (category, price, original_cost, alternative_cost, "generated")
    for pid, draft in buildable.items():
        product = sellable[pid]
        if product["fulfillment_mode"] != "make_to_order" or pid in records:
            raise ValueError(f"{pid}: invalid buildable cost")
        records[pid] = (product["attributes_json"]["category"],
                        number(draft["product_list_price_eur"]),
                        number(draft["product_standard_cost_eur"]),
                        number(draft["product_standard_cost_eur"]), "buildable")
    if len(records) != 120:
        raise ValueError("expected exactly 120 priced sellable products")
    categories = []
    product_deltas = []
    for category in sorted(targets):
        selected = [(pid, *values) for pid, values in records.items() if values[0] == category]
        if len(selected) != config["product_catalogue"]["categories"][category]["count"]:
            raise ValueError(f"{category}: incomplete category")
        floor = number(floors[category])
        original_margins = [(price - old) / price * 100
                            for _, _, price, old, new, source in selected]
        alternative_margins = [(price - new) / price * 100
                               for _, _, price, old, new, source in selected]
        original_below = set()
        experimental_below = set()
        original_nonpositive = set()
        experimental_nonpositive = set()
        transitions = []
        for pid, _, price, old, new, source in selected:
            before, after = floor_status(price, old, floor), floor_status(price, new, floor)
            if source == "generated":
                product_deltas.append({
                    "product_id": pid, "category": category,
                    "list_price_eur": rounded(price),
                    "current_cost_eur": rounded(old),
                    "experimental_cost_eur": rounded(new),
                    "current_list_margin_pct": rounded((price - old) / price * 100),
                    "experimental_list_margin_pct": rounded((price - new) / price * 100),
                    "ten_pct_discount_current": before,
                    "ten_pct_discount_experiment": after,
                })
            if before != "at_or_above_floor":
                original_below.add(pid)
            if after != "at_or_above_floor":
                experimental_below.add(pid)
            if before == "nonpositive":
                original_nonpositive.add(pid)
            if after == "nonpositive":
                experimental_nonpositive.add(pid)
            if before != after:
                transitions.append({"product_id": pid, "source": source,
                                    "current": before, "experiment": after})
        categories.append({
            "category": category, "count": len(selected),
            "generated_count": sum(row[-1] == "generated" for row in selected),
            "current_margin_p10_pct": rounded(percentile(original_margins, "0.1")),
            "current_margin_p50_pct": rounded(percentile(original_margins, "0.5")),
            "current_margin_p90_pct": rounded(percentile(original_margins, "0.9")),
            "experimental_margin_p10_pct": rounded(percentile(alternative_margins, "0.1")),
            "experimental_margin_p50_pct": rounded(percentile(alternative_margins, "0.5")),
            "experimental_margin_p90_pct": rounded(percentile(alternative_margins, "0.9")),
            "baseline_floor_pct": rounded(floor),
            "ten_pct_discount_below_floor_current": len(original_below),
            "ten_pct_discount_below_floor_experiment": len(experimental_below),
            "ten_pct_discount_nonpositive_current": len(original_nonpositive),
            "ten_pct_discount_nonpositive_experiment": len(experimental_nonpositive),
            "status_transitions": sorted(transitions, key=lambda row: row["product_id"]),
        })
    return {
        "basis": "read_only_synthetic_sensitivity_experiment",
        "seed": seed, "quote_discount_pct": 10,
        "input_digest": sha256(json.dumps({
            "portfolio": portfolio, "costs": costs, "config": config,
            "contract": contract,
        }, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest(),
        "generated_costs_recalculated": 102, "buildable_costs_unchanged": 18,
        "prices_unchanged": True, "categories": categories,
        "product_deltas": sorted(product_deltas, key=lambda row: row["product_id"]),
        "interpretation": "single-line arithmetic at a fixed 10% discount; not a full deal decision",
        "calibration_frozen": False, "price_comparability_verified": False,
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    print(json.dumps(experiment(portfolio, costs, config, contract), indent=2))
