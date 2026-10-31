"""Review fictional component fit for every offered BOM and substitute.

The specs are declared assumptions in a companion draft. Passing these
checks does not certify real hardware or make the dataset ready to generate.
"""

from itertools import product
from pathlib import Path
import json
import math


HERE = Path(__file__).resolve().parent
FIELDS = {
    "compute_kit": {"storage_host_interface", "network_slot_interface",
                    "board_form_factor", "rated_watts"},
    "storage_drive": {"host_interface", "form_factor", "rated_watts"},
    "network_power_kit": {"network_interface", "psu_output_watts", "rated_watts"},
    "enclosure_kit": {"supported_board_form_factors", "supported_drive_form_factors",
                      "drive_slots", "power_budget_watts", "cooling_capacity_watts"},
}
NUMBERS = {"rated_watts", "psu_output_watts", "drive_slots",
           "power_budget_watts", "cooling_capacity_watts"}
BASIS = "declared_synthetic_engineering_assumptions_not_manufacturer_certification"


def validate(portfolio, draft):
    errors = []
    products = {p["product_id"]: p for p in portfolio["products"]}
    components = {pid: p for pid, p in products.items()
                  if p["fulfillment_mode"] == "component"}
    specs = draft.get("component_specs")
    if draft.get("basis") != BASIS or not draft.get("spec_version"):
        errors.append("fit draft needs explicit synthetic basis and version")
    if draft.get("catalog_version") != portfolio["catalog_version"]:
        errors.append("fit draft catalogue version differs")
    if not isinstance(specs, dict) or set(specs) != set(components):
        return {"errors": errors + ["specifications must cover exactly all components"],
                "checked_boms": 0, "checked_alternatives": 0,
                "ready_for_generation": False}
    for cid, component in components.items():
        role = component["attributes_json"].get("component_role")
        spec = specs[cid]
        if role not in FIELDS or not isinstance(spec, dict) or set(spec) != FIELDS[role]:
            errors.append(f"{cid}: incomplete {role} specification")
            continue
        for field, value in spec.items():
            if field in NUMBERS and (type(value) not in (int, float) or
                                     not math.isfinite(value) or value <= 0):
                errors.append(f"{cid}: {field} must be positive")
            elif field not in NUMBERS and isinstance(value, list):
                if not value or any(not isinstance(x, str) or not x for x in value):
                    errors.append(f"{cid}: {field} needs named values")
            elif field not in NUMBERS and (not isinstance(value, str) or not value):
                errors.append(f"{cid}: {field} must be named")
    if errors:
        return {"errors": errors, "checked_boms": 0, "checked_alternatives": 0,
                "ready_for_generation": False}
    for cid, spec in specs.items():
        attrs = components[cid]["attributes_json"]
        if any(attrs.get(field) != value for field, value in spec.items()):
            errors.append(f"{cid}: catalogue attributes differ from pinned fit draft")

    lines_by_bom = {}
    for line in portfolio["bom_lines"]:
        lines_by_bom.setdefault(line["bom_id"], []).append(line)
    results = {}
    for header in portfolio["bom_headers"]:
        if header["status"] != "active":
            continue
        bid = header["bom_id"]
        if header["output_quantity"] != 1:
            errors.append(f"{bid}: this draft checks one output unit at a time")
            continue
        finished = products[header["finished_product_id"]]
        platform = finished["attributes_json"]["build_platform"]
        fixed, groups = [], {}
        for line in lines_by_bom.get(bid, []):
            cid = line["component_product_id"]
            if cid not in components:
                errors.append(f"{bid}: unknown component {cid}")
                continue
            if platform not in components[cid]["attributes_json"]["supported_platforms"]:
                errors.append(f"{bid}: {cid} does not declare platform {platform}")
            if line["substitute_group_code"] is None:
                fixed.append(line)
            else:
                groups.setdefault(line["substitute_group_code"], []).append(line)
        if not fixed and not groups:
            errors.append(f"{bid}: no component lines")
            continue
        choices = [groups[key] for key in sorted(groups)]
        count = 1
        for options in choices:
            count *= len(options)
        if count > 16:
            errors.append(f"{bid}: substitute search exceeds bounded draft")
            continue
        alternatives = []
        for selected in product(*choices):
            chosen = fixed + list(selected)
            by_role = {}
            for row in chosen:
                cid = row["component_product_id"]
                if cid not in components:
                    continue
                role = components[cid]["attributes_json"]["component_role"]
                by_role.setdefault(role, []).append(row)
            candidate_ids = sorted(row["component_product_id"] for row in chosen)
            problems = []
            if set(by_role) != set(FIELDS) or any(len(by_role.get(role, [])) != 1 for role in FIELDS):
                problems.append("one component line per required role is needed")
            else:
                def part(role):
                    row = by_role[role][0]
                    return row, specs[row["component_product_id"]]

                compute_row, compute = part("compute_kit")
                storage_row, storage = part("storage_drive")
                network_row, network = part("network_power_kit")
                enclosure_row, enclosure = part("enclosure_kit")
                quantities = [row["required_quantity_per_output"] for row in chosen]
                if any(type(q) is not int or q < 1 for q in quantities):
                    problems.append("component quantities must be positive whole units")
                else:
                    if storage["host_interface"] != compute["storage_host_interface"]:
                        problems.append("storage interface mismatch")
                    if network["network_interface"] != compute["network_slot_interface"]:
                        problems.append("network interface mismatch")
                    if compute["board_form_factor"] not in enclosure["supported_board_form_factors"]:
                        problems.append("board does not fit enclosure")
                    if storage["form_factor"] not in enclosure["supported_drive_form_factors"]:
                        problems.append("drive does not fit enclosure")
                    if storage_row["required_quantity_per_output"] > enclosure["drive_slots"]:
                        problems.append("insufficient drive slots")
                    demand = (compute_row["required_quantity_per_output"] * compute["rated_watts"] +
                              storage_row["required_quantity_per_output"] * storage["rated_watts"] +
                              network_row["required_quantity_per_output"] * network["rated_watts"])
                    if demand > network["psu_output_watts"]:
                        problems.append("power supply below calculated load")
                    if demand > enclosure["power_budget_watts"]:
                        problems.append("enclosure power budget below calculated load")
                    if demand > enclosure["cooling_capacity_watts"]:
                        problems.append("enclosure cooling below calculated load")
            errors.extend(f"{bid} {','.join(candidate_ids)}: {message}" for message in problems)
            alternatives.append({"component_ids": candidate_ids, "fit": not problems})
        results[bid] = alternatives
    return {"errors": errors, "checked_component_specs": len(specs),
            "checked_boms": len(results),
            "checked_alternatives": sum(map(len, results.values())),
            "alternatives": results, "synthetic_fit_check_passed": not errors,
            "ready_for_generation": False}


if __name__ == "__main__":
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    draft = json.loads((HERE / "phase1c_technical_fit_draft.json").read_text())
    result = validate(portfolio, draft)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
