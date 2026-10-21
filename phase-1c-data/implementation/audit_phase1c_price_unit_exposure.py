"""Count source-input exposure to catalogue category-default unit mismatches.

This is an impact inventory, not a price conversion, decision score or answer key.
The pinned SQL and evaluation definitions remain unchanged.
"""

from collections import Counter, defaultdict
import json
from pathlib import Path
import re

import yaml

from audit_phase1c_price_distribution import audit as price_audit


HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent / "evaluation" / "provisional_cases.json"
LITERAL_LINE = re.compile(
    r"^INSERT INTO deal_lines .*? VALUES \('[^']+', '([^']+)', '\d+', '([^']+)'",
    re.MULTILINE,
)
BATCH_LINE = re.compile(
    r"^INSERT INTO deal_lines .*?'(GEN-TEST-\d+)',line_number,product_id.*?"
    r"FROM deal_lines WHERE deal_id='([^']+)'", re.MULTILINE,
)
V2_LINE = re.compile(
    r"^INSERT INTO deal_lines .*? SELECT '[^']+', '(DEP-V2-DEAL-\d+)', .*?"
    r"WHERE product_id='([^']+)'", re.MULTILINE,
)


def literal_lines(text):
    return [(deal, product) for deal, product in LITERAL_LINE.findall(text)]


def count_exposure(lines, mismatched_ids):
    all_deals = {deal for deal, _ in lines}
    affected = [(deal, product) for deal, product in lines if product in mismatched_ids]
    return {
        "deals": len(all_deals), "lines": len(lines),
        "affected_deals": len({deal for deal, _ in affected}),
        "affected_lines": len(affected),
        "affected_product_ids": sorted({product for _, product in affected}),
        "affected_lines_by_category": dict(sorted(Counter(
            mismatched_ids[product] for _, product in affected).items())),
    }


def audit(portfolio, costs, config, contract, historical_sql, batch_sql,
          pilot_sql, dependency_sql, evaluation):
    price_report = price_audit(portfolio, costs, config, contract)
    mismatched = {row["product_id"]: row["category"]
                  for row in price_report["category_default_unit_mismatches"]}
    if len(mismatched) != 36:
        raise ValueError("expected 36 distinct unit-mismatched V1 products")
    history = literal_lines(historical_sql)
    if len(history) != 1200 or len({deal for deal, _ in history}) != 400:
        raise ValueError("historical source line/deal coverage drift")
    templates = defaultdict(list)
    for deal, product in literal_lines(pilot_sql):
        templates[deal].append(product)
    for deal, product in V2_LINE.findall(dependency_sql):
        templates[deal].append(product)
    development = []
    batch_refs = BATCH_LINE.findall(batch_sql)
    if len(batch_refs) != 100 or len({deal for deal, _ in batch_refs}) != 100:
        raise ValueError("development source references drift")
    for deal, source in batch_refs:
        if not templates[source]:
            raise ValueError(f"{deal}: missing development source {source}")
        development.extend((deal, product) for product in templates[source])
    cases = evaluation["cases"]
    if len(cases) != 36 or len({case["case_id"] for case in cases}) != 36:
        raise ValueError("evaluation source case coverage drift")
    evaluated = [(case["case_id"], line["product_id"])
                 for case in cases for line in case["tables"]["deal_lines"]]
    if any(product not in {p["product_id"] for p in portfolio["products"]}
           for _, product in history + evaluated):
        raise ValueError("historical/evaluation line references unknown V1 product")
    return {
        "basis": "source_only_unit_impact_not_answers_or_price_comparables",
        "v1_sellable_products": price_report["sellable_count"],
        "mismatched_product_ids": sorted(mismatched),
        "historical": count_exposure(history, mismatched),
        "development_regression": count_exposure(development, mismatched),
        "evaluation_v2_inputs": count_exposure(evaluated, mismatched),
        "accepted_evaluation_answers": 0,
        "ready_for_generation": False,
    }


def main():
    portfolio = json.loads((HERE / "phase1c_portfolio_draft.json").read_text())
    costs = json.loads((HERE / "phase1c_build_cost_draft.json").read_text())
    config = yaml.safe_load((HERE / "calibration_config.yaml").read_text())
    contract = yaml.safe_load((HERE / "phase1c_data_contract.yaml").read_text())
    history = "\n".join((HERE / f"phase1c_historical_inputs_{n:02d}.sql").read_text()
                        for n in range(1, 9))
    pilots = "\n".join((HERE / name).read_text() for name in
                       ("phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql"))
    report = audit(portfolio, costs, config, contract, history,
                   (HERE / "phase1c_generated_test_batch.sql").read_text(), pilots,
                   (HERE / "phase1c_dependency_pilot.sql").read_text(),
                   json.loads(EVALUATION.read_text()))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
