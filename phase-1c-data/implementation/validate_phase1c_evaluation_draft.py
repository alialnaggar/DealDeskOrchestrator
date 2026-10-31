"""Check the two evaluation-authoring examples without certifying their answers.

The input file is the only agent-facing example. A separately stored oracle
draft requires independent human review before it can become an evaluation
label. Structural checks here do not compute expected findings.
"""

from datetime import date, datetime, timezone
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent / "evaluation"
INPUT_FIELDS = {
    "case_id", "archetype_id", "as_of_at", "catalog_version", "policy_set_code",
    "requested_quantity", "requested_delivery_date", "allow_partial_delivery",
    "candidate_slices", "source_evidence",
}
SLICE_FIELDS = {"quantity", "arrival_date", "evidence_ids"}
SOURCE_FIELDS = {"evidence_id", "kind", "as_of_at", "quantity", "available_date", "binding"}
ORACLE_FIELDS = {"case_id", "review_status", "reviewer", "expected", "authoring_rationale"}
EXPECTED_FIELDS = {
    "original_shortfall_units_at_requested_date", "candidate_supply_supported",
    "unmet_customer_constraints", "human_action", "supporting_evidence_ids",
}
FORBIDDEN_INPUT_KEYS = {
    "expected", "oracle", "answer_key", "ground_truth", "target_bucket",
    "decision", "label", "authoring_rationale", "review_status",
}


def keys_recursively(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from keys_recursively(child)
    elif isinstance(value, list):
        for child in value:
            yield from keys_recursively(child)


def iso_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def utc_instant(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed) else None
    except (AttributeError, TypeError, ValueError):
        return None


def validate(inputs, oracle, matrix):
    errors = []
    if inputs.get("schema_version") != 1 or inputs.get("status") != "development_examples_not_held_out":
        errors.append("inputs must remain versioned development examples")
    if oracle.get("schema_version") != 1 or (
        oracle.get("status") != "provisional_author_draft_pending_independent_review"
        or oracle.get("answer_key_agent_visible") is not False
        or oracle.get("independently_reviewed_cases") != 0
    ):
        errors.append("oracle draft cannot claim independent review or agent visibility")
    input_cases, oracle_cases = inputs.get("cases"), oracle.get("cases")
    if not isinstance(input_cases, list) or not isinstance(oracle_cases, list):
        return errors + ["both files need case lists"]
    if len(input_cases) != 2 or len(oracle_cases) != 2:
        errors.append("this first development sample contains exactly two cases")
    known_archetypes = {a["id"] for a in matrix["archetypes"]}
    seen_inputs, seen_oracles = set(), set()
    for i, case in enumerate(input_cases):
        if not isinstance(case, dict):
            errors.append(f"inputs[{i}]: object required")
            continue
        cid = case.get("case_id")
        if set(case) != INPUT_FIELDS or FORBIDDEN_INPUT_KEYS.intersection(keys_recursively(case)):
            errors.append(f"{cid}: agent-facing input contains unexpected or answer fields")
        if not isinstance(cid, str) or not cid.startswith("DEV-") or cid in seen_inputs:
            errors.append(f"inputs[{i}]: unique development case ID required")
        seen_inputs.add(cid)
        if case.get("archetype_id") not in known_archetypes:
            errors.append(f"{cid}: unknown archetype")
        if case.get("catalog_version") != matrix["catalog_version"] or (
            case.get("policy_set_code") != matrix["policy_set_code"]
        ):
            errors.append(f"{cid}: catalogue or policy differs from matrix")
        as_of = utc_instant(case.get("as_of_at"))
        requested_date = iso_date(case.get("requested_delivery_date"))
        if as_of is None or requested_date is None or requested_date < as_of.date():
            errors.append(f"{cid}: invalid as-of or requested date")
        quantity = case.get("requested_quantity")
        slices = case.get("candidate_slices")
        sources = case.get("source_evidence")
        if type(quantity) is not int or quantity <= 0 or case.get("allow_partial_delivery") is not True:
            errors.append(f"{cid}: positive quantity and partial-delivery permission required")
        if not isinstance(slices, list) or not slices or not isinstance(sources, list) or not sources:
            errors.append(f"{cid}: slices and source facts required")
            continue
        source_ids = set()
        source_by_id = {}
        for source in sources:
            if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
                errors.append(f"{cid}: malformed source fact")
                continue
            sid = source["evidence_id"]
            if not isinstance(sid, str) or not sid or sid in source_ids:
                errors.append(f"{cid}: duplicate or invalid evidence ID")
                continue
            source_ids.add(sid)
            source_by_id[sid] = source
            if source["kind"] not in {"free_inventory", "confirmed_receipt", "supplier_offer"} or (
                type(source["quantity"]) is not int or source["quantity"] <= 0
                or type(source["binding"]) is not bool
                or utc_instant(source["as_of_at"]) is None
                or iso_date(source["available_date"]) is None
            ):
                errors.append(f"{cid}: invalid source fact")
            elif as_of and utc_instant(source["as_of_at"]) > as_of:
                errors.append(f"{cid}: future evidence cannot be known at evaluation time")
            if (source["kind"] == "supplier_offer" and source["binding"] is not False) or (
                source["kind"] in {"free_inventory", "confirmed_receipt"} and source["binding"] is not True
            ):
                errors.append(f"{cid}: source commitment kind and binding flag conflict")
        total = 0
        cited = set()
        for row in slices:
            if not isinstance(row, dict) or set(row) != SLICE_FIELDS:
                errors.append(f"{cid}: malformed delivery slice")
                continue
            qty, ids = row["quantity"], row["evidence_ids"]
            if type(qty) is not int or qty <= 0 or iso_date(row["arrival_date"]) is None or (
                not isinstance(ids, list) or not ids or
                any(not isinstance(x, str) or x not in source_ids for x in ids)
            ):
                errors.append(f"{cid}: invalid slice quantity, date or evidence reference")
            else:
                total += qty
                arrival = iso_date(row["arrival_date"])
                for sid in ids:
                    if sid in cited:
                        errors.append(f"{cid}: source evidence reused across slices")
                    cited.add(sid)
                    source = source_by_id[sid]
                    available = iso_date(source.get("available_date"))
                    source_qty = source.get("quantity")
                    if (available is not None and available > arrival) or (
                        type(source_qty) is not int or source_qty < qty
                    ):
                        errors.append(f"{cid}: source cannot cover cited slice date or quantity")
        if total != quantity:
            errors.append(f"{cid}: proposed quantities must sum to the submitted quantity")
    for i, case in enumerate(oracle_cases):
        if not isinstance(case, dict):
            errors.append(f"oracle[{i}]: object required")
            continue
        cid = case.get("case_id")
        if set(case) != ORACLE_FIELDS or not isinstance(case.get("expected"), dict) or (
            set(case["expected"]) != EXPECTED_FIELDS
        ):
            errors.append(f"{cid}: incomplete reviewer draft")
            continue
        if cid in seen_oracles:
            errors.append(f"{cid}: duplicate oracle case")
        seen_oracles.add(cid)
        if case.get("review_status") != "pending_independent_review" or case.get("reviewer") is not None:
            errors.append(f"{cid}: draft cannot claim independent review")
        expected = case["expected"]
        if type(expected["original_shortfall_units_at_requested_date"]) is not int or (
            expected["original_shortfall_units_at_requested_date"] < 0
            or type(expected["candidate_supply_supported"]) is not bool
            or not isinstance(expected["unmet_customer_constraints"], list)
            or any(not isinstance(x, str) or not x for x in expected["unmet_customer_constraints"])
            or not isinstance(case.get("authoring_rationale"), str)
            or not case["authoring_rationale"]
            or expected["human_action"] not in {
                "seek_customer_acceptance_and_prescribed_review",
                "request_binding_supply_or_revise_no_validated_option",
            }
        ):
            errors.append(f"{cid}: invalid draft finding shape")
        input_case = next((x for x in input_cases if isinstance(x, dict) and x.get("case_id") == cid), None)
        if input_case:
            evidence = {x.get("evidence_id") for x in (input_case.get("source_evidence") or [])
                        if isinstance(x, dict)}
            refs = expected["supporting_evidence_ids"]
            if (not isinstance(refs, list) or not refs or
                    any(not isinstance(x, str) for x in refs) or
                    set(refs) - evidence):
                errors.append(f"{cid}: oracle cites unknown source facts")
    if seen_inputs != seen_oracles:
        errors.append("input and oracle case IDs differ")
    return errors


if __name__ == "__main__":
    import yaml
    inputs = json.loads((EVALUATION / "development_inputs.json").read_text())
    oracle = json.loads((EVALUATION / "reviewer_oracle_draft.json").read_text())
    matrix = yaml.safe_load((HERE / "phase1c_scenario_matrix.yaml").read_text())
    errors = validate(inputs, oracle, matrix)
    print(json.dumps({"errors": errors, "development_examples": len(inputs["cases"]),
                      "independently_reviewed": 0, "evaluation_target": 36}, indent=2))
    raise SystemExit(bool(errors))
