"""Source-only supplier-calendar join for the pinned 36-case v2 input cohort.

This checks an offer's calendar and lead evidence, not its deliverability,
commitment status, expected answer, or the separate historical cohort.
"""

from datetime import date
import json
from pathlib import Path

import yaml

from validate_phase1c_data_contract import validate_payload


HERE = Path(__file__).resolve().parent
CASES = HERE.parent / "evaluation" / "provisional_cases.json"


def audit(source, contract):
    if source.get("evaluation_input_version") != 2 or len(source.get("cases", [])) != 36:
        raise ValueError("expected the 36 pinned v2 source cases")
    seen = set()
    offer_cases = []
    offer_ids = set()
    supplier_count = 0
    for case in source["cases"]:
        case_id = case["case_id"]
        if case_id in seen:
            raise ValueError(f"duplicate case {case_id}")
        seen.add(case_id)
        tables = case["tables"]
        suppliers = {row["supplier_id"]: row for row in tables.get("suppliers", [])}
        if len(suppliers) != len(tables.get("suppliers", [])):
            raise ValueError(f"{case_id}: duplicate supplier")
        supplier_count += len(suppliers)
        for row in suppliers.values():
            errors = validate_payload("supplier_calendar", row["order_calendar_json"], contract)
            if errors:
                raise ValueError(f"{case_id}: invalid calendar for {row['supplier_id']}: {errors}")
        offers = tables.get("supplier_items", [])
        if offers:
            offer_cases.append(case_id)
        as_of = date.fromisoformat(tables["deal_runs"][0]["as_of_at"][:10])
        for offer in offers:
            item_id = offer["supplier_item_id"]
            if item_id in offer_ids:
                raise ValueError(f"duplicate offer {item_id}")
            offer_ids.add(item_id)
            supplier = suppliers.get(offer["supplier_id"])
            if supplier is None or supplier["status"] != "active":
                raise ValueError(f"{case_id}: {item_id} lacks an active local supplier")
            leads = [offer.get(f"lead_days_{part}") for part in ("min", "mode", "max")]
            if any(type(value) is not int or value < 0 for value in leads) or leads != sorted(leads):
                raise ValueError(f"{case_id}: {item_id} has incomplete or unordered leads")
            if not offer["is_active"] or not (
                date.fromisoformat(offer["valid_from"]) <= as_of <=
                date.fromisoformat(offer["valid_to"])
            ):
                raise ValueError(f"{case_id}: {item_id} not active at run cutoff")
    return {
        "basis": "v2_source_only_calendar_and_lead_joins_not_answer_labels",
        "evaluation_input_version": 2,
        "cases": len(seen),
        "supplier_rows_with_typed_calendars": supplier_count,
        "linked_offer_count": len(offer_ids),
        "linked_offer_case_ids": offer_cases,
        "historical_dated_offer_coverage": "not_assessed_here",
        "independently_reviewed_answers": 0,
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    source = json.loads(CASES.read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    print(json.dumps(audit(source, contract), indent=2, sort_keys=True))
