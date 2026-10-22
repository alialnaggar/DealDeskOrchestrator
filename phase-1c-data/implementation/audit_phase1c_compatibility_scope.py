"""Inventory compatibility rule families in pinned source inputs, not answers."""

import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
RULE = re.compile(
    r"^INSERT INTO compatibility_rules \([^)]*\) VALUES "
    r"\('([^']+)', '([^']+)', '[^']+', '([^']+)', '([^']+)', "
    r"'([^']+)', (?:'([^']+)', )?'(\{[^']+\})', '([^']+)'",
)
FIXTURES = ("phase1c_vertical_pilot.sql", "phase1c_conflict_pilot.sql",
            "phase1c_dependency_pilot.sql")


def audit(sql_texts, evaluation):
    development = []
    for filename, source in sql_texts.items():
        for line in source.splitlines():
            if not line.startswith("INSERT INTO compatibility_rules "):
                continue
            match = RULE.match(line)
            if not match:
                raise ValueError(f"unparsed compatibility rule in {filename}")
            rule_id, version, rule_type, scope, product, target, condition, severity = match.groups()
            development.append({"rule_id": rule_id, "catalog_version": version,
                                "rule_type": rule_type, "scope_type": scope,
                                "source_product_id": product, "target_product_id": target,
                                "condition_json": json.loads(condition), "severity": severity})
    service = "SELL-PROFESSIONAL_AND_IMPLEMENTATION_SERVICES"
    expected = {
        "PILOT-SERVICE-COVERAGE": ("CATALOGUE_2026_V1", "installation_eligibility",
                                   "line", service + "-001", None,
                                   {"country_code": "DE", "eligible": True, "region": "DE-NW"}, "blocker"),
        "CONFLICT-SERVICE-OUTSIDE": ("CATALOGUE_2026_V1", "installation_eligibility",
                                     "line", service + "-002", None,
                                     {"country_code": "DE", "eligible": False, "region": "DE-NW"}, "blocker"),
        "V2-REQUIRES-ADDON": ("CATALOGUE_2026_V2", "requires_product", "whole_deal",
                              "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-004-V2",
                              "SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-005-V2",
                              {"operator": "present"}, "blocker"),
    }
    actual = {x["rule_id"]: tuple(x[key] for key in (
        "catalog_version", "rule_type", "scope_type", "source_product_id",
        "target_product_id", "condition_json", "severity")) for x in development}
    if len(development) != len(expected) or actual != expected:
        raise ValueError("development compatibility scope differs from pinned V1/V2 rules")
    cases = evaluation["cases"]
    if len(cases) != 36 or len({c["case_id"] for c in cases}) != 36:
        raise ValueError("expected 36 distinct evaluation input cases")
    evaluation_rows = [
        {"case_id": case["case_id"], "rule_id": row["compatibility_rule_id"],
         "catalog_version": row["catalog_version"], "rule_type": row["rule_type"]}
        for case in cases for row in case["tables"].get("compatibility_rules", [])
    ]
    expected_cases = {f"EVAL-PREP-{n:03d}" for n in range(27, 31)}
    if (len(evaluation_rows) != 4 or
            {x["case_id"] for x in evaluation_rows} != expected_cases or
            any(x["catalog_version"] != "CATALOGUE_2026_V1" or
                x["rule_type"] != "installation_eligibility" for x in evaluation_rows)):
        raise ValueError("evaluation compatibility scope differs from four regional service inputs")
    for case in cases:
        if case["case_id"] not in expected_cases:
            continue
        number = int(case["case_id"].split("-")[-1])
        rule = case["tables"]["compatibility_rules"][0]
        deal = case["tables"]["deals"][0]
        region, eligible = ("DE-NW", True) if number < 29 else ("DE-BY", False)
        if (rule["compatibility_rule_id"] != f"EVAL36-{number:03d}-SERVICE-COVERAGE" or
                rule["scope_type"] != "line" or rule["severity"] != "blocker" or
                rule["source_product_id"] != service + "-001" or
                rule["condition_json"] != {"country_code": "DE", "region": region,
                                           "eligible": eligible} or
                (deal["destination_country_code"], deal["destination_region"]) != ("DE", region) or
                rule["source_product_id"] not in {line["product_id"] for line in
                                                  case["tables"]["deal_lines"]}):
            raise ValueError(f"evaluation regional source semantics differ in {case['case_id']}")
    return {"basis": "pinned_source_rows_only_no_answer_labels",
            "development_rules": sorted(development, key=lambda x: x["rule_id"]),
            "evaluation_rule_rows": sorted(evaluation_rows, key=lambda x: x["case_id"]),
            "v1_development_rule_families": ["installation_eligibility"],
            "v2_dependency_isolated": True,
            "generic_families_in_evaluation": False,
            "accepted_evaluation_answers": 0,
            "ready_for_generation": False}


def main():
    sql_texts = {name: (HERE / name).read_text() for name in FIXTURES}
    evaluation = json.loads((HERE.parent / "evaluation/provisional_cases.json").read_text())
    print(json.dumps(audit(sql_texts, evaluation), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
