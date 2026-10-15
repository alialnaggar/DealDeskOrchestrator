"""Report calendar/lead coverage in the pinned historical offer source.

This is a diagnostic. Missing calendar data cannot establish a dated offer
route and must not be filled from a current supplier or generic weekdays.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path

import yaml

from validate_phase1c_data_contract import validate_payload


HERE = Path(__file__).resolve().parent
SOURCE = "phase1c_historical_offer_source.json"


def audit(raw, index, contract):
    digest = hashlib.sha256(raw).hexdigest()
    if index.get("source_sha256", {}).get(SOURCE) != digest:
        raise ValueError("historical offer source differs from pinned index")
    source = json.loads(raw)
    if source.get("schema_version") != 1 or source.get("provenance") != "synthetic_provisional_supplier_offers":
        raise ValueError("historical offer source identity differs")
    offers = source.get("offers")
    if not isinstance(offers, list) or len(offers) != 162:
        raise ValueError("historical offer cohort count differs")
    if len(index.get("snapshots", [])) != 400:
        raise ValueError("historical cutoff registry count differs")
    ids = [offer["supplier_item_id"] for offer in offers]
    if len(ids) != len(set(ids)):
        raise ValueError("historical offer IDs must be distinct")
    suppliers = Counter(offer["supplier_id"] for offer in offers)
    typed = 0
    complete_leads = 0
    dated = 0
    for offer in offers:
        calendar = offer.get("order_calendar_json")
        valid = calendar is not None and not validate_payload("supplier_calendar", calendar, contract)
        if valid:
            typed += 1
        leads = all(type(offer.get(key)) is int and offer[key] >= 0
                    for key in ("lead_days_min", "lead_days_mode", "lead_days_max"))
        if leads and offer["lead_days_min"] <= offer["lead_days_mode"] <= offer["lead_days_max"]:
            complete_leads += 1
            if valid:
                dated += 1
    return {
        "basis": "pinned_source_only_historical_offer_coverage_not_decision_labels",
        "source_sha256": digest,
        "historical_cutoffs": len(index["snapshots"]),
        "offers": len(offers),
        "supplier_ids": len(suppliers),
        "offers_with_typed_calendar": typed,
        "offers_with_complete_min_mode_max": complete_leads,
        "offers_supporting_dated_estimate_fields": dated,
        "calendar_review_open": dated != len(offers),
        "ready_for_generation": False,
    }


if __name__ == "__main__":
    raw = (HERE / SOURCE).read_bytes()
    index = json.loads((HERE / "phase1c_historical_operational_index.json").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    print(json.dumps(audit(raw, index, contract), indent=2))
