"""Check all V1 product attributes under the bounded fictional catalogue scope."""

from collections import Counter
from pathlib import Path
import json
import re

import yaml

from validate_phase1c_data_contract import validate_payload
from validate_phase1c_technical_fit_draft import validate as validate_fit


HERE = Path(__file__).resolve().parent
MODES = {
    "stocked_finished": "physical",
    "supplier_finished": "physical",
    "make_to_order": "physical",
    "digital_activation": "digital_activation",
    "scheduled_service": "scheduled_service",
    "component": "component",
}

V2_CLONE = re.compile(
    r"INSERT INTO products \(([^)]+)\) SELECT '([^']+)', product_code, "
    r"'([^']+)', product_name, category, product_type, attributes_json, "
    r"list_price, standard_cost, billing_model, unit_of_measure, is_active, "
    r"is_sellable, fulfillment_mode, stock_uom FROM products WHERE "
    r"product_id='([^']+)' AND catalog_version='([^']+)';"
)
V2_COLUMNS = ("product_id, product_code, catalog_version, product_name, category, "
              "product_type, attributes_json, list_price, standard_cost, billing_model, "
              "unit_of_measure, is_active, is_sellable, fulfillment_mode, stock_uom")


def audit_v2_attribute_clones(sql):
    """Require the isolated V2 dependency pair to inherit V1 attributes verbatim."""
    rows = [line for line in sql.splitlines() if line.startswith("INSERT INTO products ")]
    expected = {f"SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-{n:03d}"
                for n in (4, 5)}
    matched = set()
    for row in rows:
        match = V2_CLONE.fullmatch(row)
        if not match:
            raise ValueError("V2 product clone no longer preserves the V1 attributes and columns")
        columns, target, version, source, source_version = match.groups()
        if (columns != V2_COLUMNS or source not in expected or source in matched or
                target != source + "-V2" or version != "CATALOGUE_2026_V2" or
                source_version != "CATALOGUE_2026_V1"):
            raise ValueError("V2 dependency clone identity or source scope differs")
        matched.add(source)
    if matched != expected:
        raise ValueError("V2 dependency must clone exactly two V1 product attribute rows")
    return len(matched)


def audit(portfolio, contract, fit_draft):
    errors = []
    rows = portfolio.get("products", [])
    ids = [row["product_id"] for row in rows]
    counts = Counter(row["fulfillment_mode"] for row in rows)
    if len(rows) != 156 or len(set(ids)) != 156:
        errors.append("V1 must have 156 distinct product IDs")
    if counts["component"] != 36 or sum(counts.values()) - counts["component"] != 120:
        errors.append("V1 must have 36 components and 120 sellable rows")
    for row in rows:
        pid = row["product_id"]
        mode = MODES.get(row["fulfillment_mode"])
        if mode is None:
            errors.append(f"{pid}: unrecognized fulfillment mode")
            continue
        if row["catalog_version"] != portfolio["catalog_version"]:
            errors.append(f"{pid}: catalogue version differs")
        if row["is_sellable"] != (mode != "component"):
            errors.append(f"{pid}: sellability differs from component scope")
        attrs = row["attributes_json"]
        if mode != "component" and isinstance(attrs, dict) and attrs.get("category") is None:
            errors.append(f"{pid}: sellable category missing")
        errors.extend(f"{pid}: {error}" for error in
                      validate_payload("product_attributes", attrs, contract, mode=mode))
    if errors:
        return {
            "basis": "declared_synthetic_attributes_not_manufacturer_certification",
            "product_rows": len(rows), "mode_counts": dict(sorted(counts.items())),
            "checked_component_specs": 0, "checked_boms": 0,
            "checked_alternatives": 0, "errors": errors,
            "ready_for_generation": False,
        }
    fit = validate_fit(portfolio, fit_draft)
    errors.extend(f"synthetic fit: {error}" for error in fit["errors"])
    if fit.get("checked_component_specs") != 36 or fit.get("checked_boms") != 24 or fit.get("checked_alternatives") != 25:
        errors.append("synthetic fit coverage must be 36 components, 24 BOMs and 25 selections")
    return {
        "basis": "declared_synthetic_attributes_not_manufacturer_certification",
        "product_rows": len(rows),
        "mode_counts": dict(sorted(counts.items())),
        "checked_component_specs": fit.get("checked_component_specs", 0),
        "checked_boms": fit.get("checked_boms", 0),
        "checked_alternatives": fit.get("checked_alternatives", 0),
        "errors": errors,
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    fit_draft = json.loads((HERE / "phase1c_technical_fit_draft.json").read_text())
    result = audit(portfolio, contract, fit_draft)
    result["v2_attribute_clones"] = audit_v2_attribute_clones(
        (HERE / "phase1c_dependency_pilot.sql").read_text())
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
