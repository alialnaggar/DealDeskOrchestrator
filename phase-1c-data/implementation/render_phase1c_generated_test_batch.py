"""Render provisional 100 source-only generated-test submissions from pinned pilot sources.

The batch varies quotes but intentionally reuses 18 V1 and two V2 development
source states. It is an import/reader coverage increment, not the final
independent source distribution or evaluation oracle.
"""

import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

import yaml

from validate_phase1c_scenario_matrix import generated_case_plan

HERE = Path(__file__).resolve().parent
SQL_PATH = HERE / "phase1c_generated_test_batch.sql"
REPORT_PATH = HERE / "phase1c_generated_test_batch_report.json"
V1_TEMPLATES = {
    "STOCK-READY": 1, "SUPPLY-CONFIRMED": 2, "BUILD-READY": 3,
    "DIGITAL-PROVED": 4, "SERVICE-COVERED": 5,
    "STOCK-ALLOCATED": 6, "STOCK-STALE": 7,
    "SUPPLY-OFFER-ONLY": 8, "SUPPLY-CANCELLED": 9,
    "DIGITAL-NO-PROOF": 10, "DIGITAL-EXPIRED": 11,
    "SERVICE-OUTSIDE": 12, "CREDIT-LIMIT": 13,
    "PRICE-FLOOR": 14, "POLICY-CLAUSE": 15,
    "BUILD-SUBSTITUTE": 16, "BUILD-CAPACITY-STALE": 17,
    "BUILD-HORIZON": 18,
}
V2_TEMPLATES = {"DEPENDENCY-PASS": "DEP-V2-DEAL-22",
                "DEPENDENCY-CONFLICT": "DEP-V2-DEAL-21"}
MULTIPLIERS = (Decimal("1.00"), Decimal("0.98"), Decimal("0.96"),
               Decimal("0.94"), Decimal("0.92"), Decimal("0.90"))
SOURCE_FILES = ("phase1c_scenario_matrix.yaml", "phase1c_vertical_pilot.sql",
                "phase1c_conflict_pilot.sql", "phase1c_dependency_pilot.sql",
                "phase1c_customer_master.sql")


def eligible_customers(customer_sql):
    """Select dated, active credit contexts with room for ordinary pilot quotes."""
    rows = re.findall(
        r"INSERT INTO customer_credit_profiles .*?VALUES \('(SYN-CUST-\d+)', '([^']+)', '([^']+)', '[^']+', '[^']+', '([^']+)', '([^']+)'",
        customer_sql)
    if len(rows) != 80:
        raise ValueError("customer master must contain 80 credit profiles")
    selected = [customer for customer, limit, committed, risk, status in rows
                if status == "Active" and risk in ("Low", "Medium")
                and Decimal(limit) - Decimal(committed) > Decimal("150000")]
    if len(selected) != 37:
        raise ValueError("eligible customer pool drift")
    return selected


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def build(matrix, source_hashes, customer_sql):
    plan = generated_case_plan(matrix)
    if len(plan) != 100 or set(V1_TEMPLATES) != {c["id"] for c in matrix["archetypes"]}:
        raise ValueError("100-case source mapping differs from reviewed archetypes")
    out = ["-- Provisional source-only 100-deal batch; load after V1 pilot and V2 dependency slice.\n",
           "-- Reuses development operational states; no expected decisions or answer keys.\n",
           "SET search_path TO deal_desk, public;\n"]
    variants = Counter()
    templates = Counter()
    customers = eligible_customers(customer_sql)
    reassigned = 0
    for index, slot in enumerate(plan, 1):
        archetype, deal = slot["archetype_id"], slot["case_id"]
        if archetype in V1_TEMPLATES:
            number = V1_TEMPLATES[archetype]
            template = (f"PILOT-DEAL-{number:02d}" if number <= 5 else
                        f"CONFLICT-DEAL-{number:02d}")
        else:
            template = V2_TEMPLATES[archetype]
        templates[template] += 1
        variant = variants[archetype]
        variants[archetype] += 1
        multiplier = MULTIPLIERS[min(variant, len(MULTIPLIERS) - 1)]
        qdeal, qtemplate = quote(deal), quote(template)
        # Preserve the first reference variant and the credit-limit archetype.
        # Different billing countries may ship to the unchanged requested destination.
        customer_expr = "customer_id"
        if archetype in V1_TEMPLATES and archetype != "CREDIT-LIMIT" and variant:
            customer_expr = quote(customers[reassigned % len(customers)])
            reassigned += 1
        out.append(
            "INSERT INTO deals (deal_id,supersedes_deal_id,customer_id,salesperson_id,"
            "deal_name,submitted_at,currency_code,catalog_version,policy_set_code,"
            "requested_delivery_date,destination_country_code,destination_region,"
            "shipping_service_code,terms_json,exception_justification,requirements_json,"
            "evidence_refs_json,salesperson_comments,deal_status,dataset_type) "
            f"SELECT {qdeal},NULL,{customer_expr},salesperson_id,"
            f"{quote('Synthetic generated quote ' + f'{index:03d}')},submitted_at,"
            "currency_code,catalog_version,policy_set_code,requested_delivery_date,"
            "destination_country_code,destination_region,shipping_service_code,"
            "terms_json,exception_justification,requirements_json,evidence_refs_json,"
            f"salesperson_comments,'Draft','generated_test' FROM deals WHERE deal_id={qtemplate};\n")
        out.append(
            "INSERT INTO deal_lines (deal_line_id,deal_id,line_number,product_id,quantity,"
            "quoted_unit_price,configuration_json,fulfillment_group_code,"
            "requested_activation_date,installation_requested) "
            f"SELECT {quote(deal + '-LINE-')} || line_number,{qdeal},line_number,product_id,"
            f"quantity,ROUND(quoted_unit_price * {multiplier},2),configuration_json,"
            "fulfillment_group_code,requested_activation_date,installation_requested "
            f"FROM deal_lines WHERE deal_id={qtemplate};\n")
        out.append(f"UPDATE deals SET deal_status='Submitted' WHERE deal_id={qdeal};\n")
        out.append(
            "INSERT INTO deal_runs (run_id,deal_id,original_policy_set_code,"
            "applied_policy_set_code,catalog_version_used,as_of_at,data_snapshot_ref,"
            "input_snapshot_json,config_hash,run_status,started_at) "
            f"SELECT {quote(f'00000000-0000-4000-8000-{310000 + index:012d}')}::uuid,"
            f"{qdeal},original_policy_set_code,applied_policy_set_code,"
            "catalog_version_used,as_of_at,data_snapshot_ref,input_snapshot_json,"
            "'provisional-100-batch','queued',started_at "
            f"FROM deal_runs WHERE deal_id={qtemplate};\n")
    out.append("DO $batch$ BEGIN "
               "IF (SELECT count(*) FROM deals WHERE deal_id LIKE 'GEN-TEST-%') <> 100 "
               "OR (SELECT count(*) FROM deal_lines WHERE deal_id LIKE 'GEN-TEST-%') <> 101 "
               "THEN RAISE EXCEPTION 'Generated-test batch incomplete'; END IF; "
               "END $batch$;\n")
    sql = "".join(out)
    report = {
        "status": "provisional_source_reuse",
        "generated_deals": len(plan),
        "v1_deals": sum(p["catalog_version"] == matrix["catalog_version"] for p in plan),
        "v2_dependency_deals": len(plan) - sum(p["catalog_version"] == matrix["catalog_version"] for p in plan),
        "source_template_count": len(templates),
        "eligible_customer_count": len(customers),
        "customer_reassignment_count": reassigned,
        "source_reuse_limit": "18_V1_and_2_V2_development_states;_not_independent_source_distribution",
        "line_count": 101,
        "source_sha256": source_hashes,
        "sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
    }
    return sql, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
              for name in SOURCE_FILES}
    sql, report = build(matrix, hashes, (HERE / "phase1c_customer_master.sql").read_text())
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if SQL_PATH.read_text() != sql or REPORT_PATH.read_text() != rendered:
            raise SystemExit("generated-test batch differs from source generator")
    else:
        SQL_PATH.write_text(sql)
        REPORT_PATH.write_text(rendered)
    print(f"{report['generated_deals']} provisional deals; hash {report['sql_sha256']}")


if __name__ == "__main__":
    main()
