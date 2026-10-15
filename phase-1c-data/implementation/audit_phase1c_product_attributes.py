"""Check all V1 product attributes under the bounded fictional catalogue scope."""

from collections import Counter
from pathlib import Path
import json

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
        if mode != "component" and attrs.get("category") is None:
            errors.append(f"{pid}: sellable category missing")
        errors.extend(f"{pid}: {error}" for error in
                      validate_payload("product_attributes", attrs, contract, mode=mode))
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
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
