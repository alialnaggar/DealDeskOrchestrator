"""Author 36 provisional source-only cases; no expected findings or scores.

Each case is loaded alone with the shared fictional catalogue and policy.
Operational records are constructed here, never copied from pilot or historical
submissions. The separate authoring map is reviewer material, not agent input.
"""

import argparse
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import yaml

from render_phase1c_sellable_catalogue import product_rows

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE.parent / "evaluation"
SOURCE_FILES = ("phase1c_scenario_matrix.yaml", "phase1c_portfolio_draft.json",
                "phase1c_build_cost_draft.json", "calibration_config.yaml",
                "phase1c_data_contract.yaml", "phase1c_buildable_master.sql",
                "phase1c_sellable_catalogue.sql", "render_phase1c_evaluation_cases.py",
                "render_phase1c_sellable_catalogue.py")
CATALOG = "CATALOGUE_2026_V1"
POLICY = "BASELINE_2026"
PRODUCTS = {
    "stocked_finished": "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001",
    "supplier_finished": "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-006",
    "make_to_order": "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009",
    "digital_activation": "SELL-CLOUD_SERVICES_AND_SUBSCRIPTIONS-001",
    "scheduled_service": "SELL-PROFESSIONAL_AND_IMPLEMENTATION_SERVICES-001",
}
COMPONENTS = ("COMP-COMPUTE-001", "COMP-STORAGE-001",
              "COMP-NETWORK_AND_POWER-001", "COMP-CHASSIS_AND_OTHER-001",
              "COMP-NETWORK_AND_POWER-002")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def render(value):
    return json.dumps(value, sort_keys=True, indent=2, default=str) + "\n"


def build(portfolio, costs, config, contract, matrix, source_hashes):
    if matrix["evaluation"]["target_cases"] != 36 or len(matrix["archetypes"]) != 18:
        raise ValueError("Evaluation authoring requires the 18-archetype/36-case contract")
    if matrix["evaluation"]["variants_per_archetype"] != 2:
        raise ValueError("Two variants per archetype required")
    priced = product_rows(portfolio, costs, config, contract)
    prices = {row[0]: Decimal(row[7]) for row in priced}
    standard_cost = {row[0]: Decimal(row[8]) for row in priced}
    prices.update({p["product_id"]: Decimal(str(p["product_list_price_eur"]))
                   for p in costs["products"]})
    assumptions = hashlib.sha256(canonical(source_hashes).encode()).hexdigest()
    cases, authoring = [], []
    for archetype in matrix["archetypes"]:
        kind = archetype["id"]
        mode = archetype["mode"]
        if mode == "cross_cutting":
            mode = "stocked_finished"
        product = PRODUCTS[mode]
        for variant in range(2):
            index = len(cases) + 1
            case_id = f"EVAL-PREP-{index:03d}"
            prefix = f"EVAL36-{index:03d}"
            deal, customer, supplier = prefix + "-DEAL", prefix + "-CUSTOMER", prefix + "-SUPPLIER"
            location = "WH-EU-CENTRAL"
            quantity = 2 + 2 * variant
            as_of = datetime(2026, 9, 1, 12, index, tzinfo=timezone.utc)
            snapshot = as_of - timedelta(minutes=85 + variant * 10)
            requested = date(2026, 9, 10 + variant)
            tables = {}

            def add(table, **row):
                tables.setdefault(table, []).append(row)

            add("customers", customer_id=customer, customer_code=customer,
                customer_name=f"Synthetic evaluation buyer {index:03d}",
                size_segment="SMB" if variant == 0 else "Mid-Market",
                industry="manufacturing" if variant == 0 else "professional_services",
                country_code="DE", region="DE-NW", customer_since="2024-06-01",
                account_status="Active")
            add("customer_credit_profiles", customer_id=customer,
                credit_limit=1000 if kind == "CREDIT-LIMIT" else 250000 + 10000 * index,
                unbilled_committed_amount=900 if kind == "CREDIT-LIMIT" else 125 * index,
                commitments_as_of_at=snapshot.isoformat(),
                commitment_evidence_ref=prefix + "-CREDIT", risk_rating="Low",
                credit_status="Active", default_payment_terms_days=30,
                last_review_date="2026-08-25")
            add("suppliers", supplier_id=supplier, supplier_code=supplier,
                supplier_name=f"Synthetic source owner {index:03d}", country_code="NL",
                status="active", order_calendar_json={"working_weekdays": [1, 2, 3, 4, 5],
                    "holiday_dates": [], "time_zone": "Europe/Amsterdam"})

            def stock(sku, total, allocated=0, observed=None):
                add("inventory", inventory_id=prefix + "-INV-" + sku,
                    product_id=sku, location_id=location, quantity_on_hand=total,
                    quantity_allocated=allocated, snapshot_at=(observed or snapshot).isoformat())

            def offer(sku):
                add("supplier_items", supplier_item_id=prefix + "-OFFER", supplier_id=supplier,
                    product_id=sku, supplier_sku=prefix + "-SKU", minimum_order_qty=1,
                    order_multiple=1, lead_days_min=1 + variant, lead_days_mode=3 + variant,
                    lead_days_max=5 + variant, unit_cost="47.50", currency_code="EUR",
                    valid_from="2026-08-20", valid_to="2026-09-30", is_active=True)

            def receipt(sku, amount, arrival, cancelled=False):
                confirmed = as_of - timedelta(hours=20 + variant)
                add("purchase_orders", purchase_order_id=prefix + "-PO", supplier_id=supplier,
                    reference_number=prefix + "-PO-REFERENCE",
                    ordered_at=(confirmed - timedelta(hours=7)).isoformat(),
                    confirmed_at=confirmed.isoformat(), status="Cancelled" if cancelled else "Confirmed",
                    destination_location_id=location)
                add("inbound_supply", supply_id=prefix + "-RECEIPT",
                    purchase_order_id=prefix + "-PO", product_id=sku, location_id=location,
                    quantity=amount, quantity_allocated=0, expected_date=arrival.isoformat(),
                    confirmed_at=confirmed.isoformat(), status="Cancelled" if cancelled else "Confirmed",
                    reference_number=prefix + "-RECEIPT-REFERENCE",
                    evidence_ref=prefix + "-SUPPLIER-CONFIRMATION",
                    valid_until="2026-10-10T00:00:00+00:00")

            if mode in ("stocked_finished", "supplier_finished", "make_to_order"):
                add("shipping_lanes", lane_id=prefix + "-LANE", origin_location_id=location,
                    origin_time_zone="Europe/Berlin", destination_country_code="DE",
                    destination_region="DE-NW", shipping_service_code="standard",
                    transit_workdays=1 + variant, dispatch_weekdays_json=[1, 2, 3, 4, 5],
                    cutoff_local_time="16:00:00")
            if mode == "stocked_finished":
                total = quantity + 3 + variant
                observed = as_of - timedelta(hours=49 + variant * 12) if kind == "STOCK-STALE" else snapshot
                stock(product, total, total if kind == "STOCK-ALLOCATED" else variant, observed)
            if mode == "supplier_finished":
                offer(product)
                if kind != "SUPPLY-OFFER-ONLY":
                    receipt(product, quantity + 2 + variant, date(2026, 9, 3 + variant),
                            cancelled=kind == "SUPPLY-CANCELLED")
            if mode == "make_to_order":
                for component in COMPONENTS:
                    total, allocated = quantity * (3 if component == "COMP-STORAGE-001" else 2) + 3, 0
                    if kind == "BUILD-SUBSTITUTE" and component == "COMP-NETWORK_AND_POWER-001":
                        allocated = total
                    if ((kind == "BUILD-SUBSTITUTE" and component == "COMP-NETWORK_AND_POWER-002")
                            or (kind == "BUILD-HORIZON" and component == "COMP-COMPUTE-001")):
                        total = 0
                    stock(component, total, allocated)
                if kind in ("BUILD-SUBSTITUTE", "BUILD-HORIZON"):
                    supplied = ("COMP-NETWORK_AND_POWER-002" if kind == "BUILD-SUBSTITUTE"
                                else "COMP-COMPUTE-001")
                    offer(supplied)
                    receipt(supplied, quantity + 3,
                            date(2026, 9, 3 + variant) if kind == "BUILD-SUBSTITUTE" else date(2026, 10, 1 + variant))
                for day in range(1, 9):
                    for operation, resource in (("assembly", "workforce"), ("test", "equipment")):
                        capacity_day = date(2026, 9, 1) + timedelta(days=day)
                        add("production_capacity", capacity_id=f"{prefix}-CAP-{day}-{operation}",
                            location_id=location, capability_code=operation, resource_type=resource,
                            capacity_date=capacity_day.isoformat(), time_zone="Europe/Berlin",
                            available_capacity_hours=0 if capacity_day.weekday() >= 5 else 7 + variant,
                            allocated_capacity_hours=0,
                            snapshot_at=(as_of - timedelta(hours=51 + variant)
                                if kind == "BUILD-CAPACITY-STALE" else snapshot).isoformat(),
                            status="active", evidence_ref=f"{prefix}-WORKSHOP-{day}-{operation}")

            provider_manifest = {"schema_version": 1, "records": []}
            activation = date(2026, 9, 3 + variant)
            if mode == "digital_activation":
                proof_id = prefix + "-PROVIDER-PROOF"
                add("digital_capacity", digital_capacity_id=prefix + "-POOL", product_id=product,
                    configuration_signature_json={"edition": "business"}, provider_id=supplier,
                    region_code="DE", term_code="12m", capacity_unit="instance",
                    capacity_total=quantity + 5, quantity_allocated=1,
                    activation_lead_days=1 + variant, commitment_status="binding",
                    confirmed_at=(snapshot - timedelta(hours=2)).isoformat(),
                    valid_until="2027-09-10T00:00:00+00:00", snapshot_at=snapshot.isoformat(),
                    evidence_ref=proof_id)
                if kind != "DIGITAL-NO-PROOF":
                    provider_manifest["records"].append(dict(
                        evidence_ref=proof_id, evidence_type="provider_proof",
                        source_class="synthetic_provider_manifest", issued_at=snapshot.isoformat(),
                        product_id=product, provider_id=supplier,
                        configuration_signature_json={"edition": "business"}, region_code="DE",
                        term_code="12m", capacity_unit="instance", capacity_total=quantity + 5,
                        quantity_allocated=1, commitment_status="binding", verified_at=snapshot.isoformat(),
                        confirmed_at=(snapshot - timedelta(hours=2)).isoformat(),
                        valid_until="2027-09-10T00:00:00+00:00", covers_from=activation.isoformat(),
                        covers_until="2026-12-31" if kind == "DIGITAL-EXPIRED" else "2027-09-06"))
            if mode == "scheduled_service":
                add("compatibility_rules", compatibility_rule_id=prefix + "-SERVICE-COVERAGE",
                    catalog_version=CATALOG, rule_name="Declared synthetic service region",
                    rule_type="installation_eligibility", scope_type="line", source_product_id=product,
                    condition_json={"country_code": "DE",
                                    "region": "DE-BY" if kind == "SERVICE-OUTSIDE" else "DE-NW",
                                    "eligible": kind != "SERVICE-OUTSIDE"},
                    severity="blocker", message="Synthetic regional eligibility", priority=1)
            terms = {"payment_terms_days": 30, "allow_partial_delivery": variant == 1,
                     "contract_clause_codes": ["legal_review"] if kind == "POLICY-CLAUSE" else ["standard"]}
            if mode == "digital_activation":
                terms["contract_months"] = 12
            price = ((standard_cost[product] * Decimal("1.01")) if kind == "PRICE-FLOOR"
                     else prices[product] * (Decimal("0.97") if variant == 0 else Decimal("0.94")))
            add("deals", deal_id=deal, customer_id=customer, salesperson_id="SALES-036",
                deal_name=f"Synthetic submitted quote {index:03d}",
                submitted_at=(as_of - timedelta(hours=4)).isoformat(), currency_code="EUR",
                catalog_version=CATALOG, policy_set_code=POLICY,
                requested_delivery_date=None if mode == "digital_activation" else requested.isoformat(),
                destination_country_code="DE",
                destination_region="DE-BY" if kind == "SERVICE-OUTSIDE" else "DE-NW",
                shipping_service_code="standard" if mode in ("stocked_finished", "supplier_finished", "make_to_order") else None,
                terms_json=terms, deal_status="Draft", dataset_type="evaluation")
            add("deal_lines", deal_line_id=prefix + "-LINE", deal_id=deal, line_number=1,
                product_id=product, quantity=quantity * 12 if mode == "digital_activation" else quantity,
                quoted_unit_price=str(price.quantize(Decimal("0.01"))),
                configuration_json={"selected_options": ["standard"]} if mode == "make_to_order" else
                    {"edition": "business", "units_per_period": quantity} if mode == "digital_activation" else {},
                requested_activation_date=activation.isoformat() if mode == "digital_activation" else None)
            add("deal_runs", run_id=f"00000000-0000-4000-8000-{360000 + index:012d}",
                deal_id=deal, original_policy_set_code=POLICY, applied_policy_set_code=POLICY,
                catalog_version_used=CATALOG, as_of_at=as_of.isoformat(),
                data_snapshot_ref=prefix + "-SOURCES", input_snapshot_json={"deal_id": deal},
                config_hash=assumptions, run_status="queued", started_at=as_of.isoformat())
            cases.append({"case_id": case_id, "tables": tables, "provider_manifest": provider_manifest})
            authoring.append({"case_id": case_id, "archetype_id": kind, "variant": variant + 1,
                              "source_review": "pending", "independent_answer_review": "pending"})
    inputs = {"schema_version": 1, "cases": cases}
    manifest = {"schema_version": 1, "status": "provisional_author_inputs_not_reviewed_answers",
                "source_sha256": source_hashes, "inputs_sha256": hashlib.sha256(render(inputs).encode()).hexdigest(),
                "authored_input_cases": len(cases), "independently_reviewed_answers": 0,
                "shared_context": ["V1 fictional catalogue", "BOMs and production requirements", "compiled baseline policy", "canonical location and region codes"],
                "limitations": ["case author knows development archetypes", "only five selected sellable SKUs",
                                "synthetic proof is not external verification", "no statistical independence claim"],
                "cases": authoring}
    return inputs, manifest


def build_from_files():
    read_json = lambda name: json.loads((HERE / name).read_text())
    return build(read_json("phase1c_portfolio_draft.json"), read_json("phase1c_build_cost_draft.json"),
                 yaml.safe_load((HERE / "calibration_config.yaml").read_text()),
                 yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text()),
                 yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text()),
                 {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in SOURCE_FILES})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inputs, manifest = build_from_files()
    OUTPUT_DIR.mkdir(exist_ok=True)
    for name, value in (("provisional_cases.json", inputs), ("provisional_authoring_manifest.json", manifest)):
        path = OUTPUT_DIR / name
        if args.check:
            if path.read_text() != render(value):
                raise SystemExit(f"{name} differs from reproducible authoring inputs")
        else:
            path.write_text(render(value))
    print(f"{len(inputs['cases'])} provisional input cases; 0 independently reviewed answers")


if __name__ == "__main__":
    main()
