"""Blinded second-model input, structural review and exception queue.

No model API call and no acceptance decision. Supply freshly exported packet
directories; source hashes are checked against repository indexes.
"""
import argparse
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
ROLES = ("Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval")
FINDINGS = {"no_issue_identified", "issue_identified", "evidence_needed",
            "human_review_required", "not_applicable", "abstain"}
GATES = {"blocked", "needs_revision", "needs_evidence", "needs_commitment",
         "approval_required", "abstain"}
HIGH_RISK = {20, 29, 30, 31, 32, 33, 34, 39, 40, 41}
FORBIDDEN_BLIND_KEYS = {"archetype_id", "technical_review", "technical_recommendation",
                        "overall_technical_gate_proposal", "expected_decision",
                        "expected_findings", "reviewer_oracle_draft", "author_amendments",
                        "review_status", "accepted_answer", "score"}


def read(path):
    return json.loads(Path(path).read_bytes())


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(obj):
    return sha256(canonical(obj).encode()).hexdigest()


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def manifest():
    original = read(ROOT / "provisional_packet_index.json")
    v3 = read(ROOT / "credit-evidence-v3/index.json")
    scope = read(ROOT / "credit-evidence-v3/credit_scope_v3.json")
    config = read(ROOT / "configuration-extension/v1/packet_index.json")
    controls = read(ROOT / "credit-evidence-v3/control_packet_index_v1.json")
    if (digest(original) != "7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc"
            or config["source_definition_sha256"] != "2e3a4dc2bf25e1df4b1d79f93b73ba98b79adfb5b71de983c1c659192eaf9d7e"
            or config["cases"][2]["packet_sha256"] != "83f65e17b9bfddee6bd32f76742678f3bf60c8e4ffea94d2d3d6479f717b2b99"
            or [x["packet_sha256"] for x in controls["cases"]] != [
                "f9bde65c883535ae1ee9f9abd2915870c9d809fae880c7a700cb9e97d0ecae25",
                "367e0755d1775b5cdd0b63a5db1bcb5b1664cc63da31e9d632ab321698126f9b"]
            or controls["accepted_answers"] != 0
            or v3["accepted_original_answers"] != 0 or v3["accepted_control_answers"] != 0
            or len(original["cases"]) != len(v3["cases"]) != len(scope["cases"]) != 36
            or [x["case_id"] for x in config["cases"]] !=
            ["EVAL-PREP-037", "EVAL-PREP-038", "EVAL-PREP-039"]
            or [x["case_id"] for x in controls["cases"]] !=
            ["EVAL-PREP-040", "EVAL-PREP-041"]):
        raise ValueError("Source cohort identity differs")
    rows = []
    for p, pin, s in zip(original["cases"], v3["cases"], scope["cases"]):
        if (p["case_id"] != pin["case_id"] or p["case_id"] != s["case_id"]
                or p["packet_sha256"] != pin["base_packet_sha256"]
                or p["provider_file_sha256"] != s["base_provider_file_sha256"]
                or digest(s) != pin["scope_sha256"]):
            raise ValueError("v3 source binding differs")
        rows.append(dict(cohort="original_v3", **p, scope_sha256=pin["scope_sha256"]))
    rows.append(dict(cohort="supplemental_configuration", **config["cases"][2]))
    rows.extend(dict(cohort="supplemental_credit", **p) for p in controls["cases"])
    return {"schema_version": 1, "status": "blind_source_manifest_no_answers",
            "accepted_original_answers": 0, "accepted_supplemental_answers": 0,
            "original_index_sha256": digest(original),
            "v3_scope_file_sha256": sha256((ROOT / "credit-evidence-v3/credit_scope_v3.json").read_bytes()).hexdigest(),
            "configuration_index_sha256": digest(config),
            "credit_control_index_sha256": digest(controls),
            "cases": rows}


def source_pointer(documents, ref):
    if not isinstance(ref, dict) or set(ref) != {"document", "pointer"}:
        raise ValueError("Malformed source citation")
    document, pointer = ref["document"], ref["pointer"]
    if document not in documents or not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("Citation outside source documents")
    if document == "packet" and not pointer.startswith(("/source_rows/", "/run_context/", "/business_contract/")):
        raise ValueError("Citation outside packet source facts")
    value = documents[document]
    for token in pointer[1:].split("/"):
        if "~" in token:
            if any(token[i] == "~" and (i + 1 >= len(token) or token[i+1] not in "01")
                   for i in range(len(token))):
                raise ValueError("Invalid pointer escape")
            token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def load_case(row, dirs):
    cid = row["case_id"]
    folder = dirs[row["cohort"]]
    packet = read(folder / (cid + ".json"))
    provider_bytes = (folder / (cid + "-provider.json")).read_bytes()
    if (packet["sha256"] != row["packet_sha256"]
            or digest(packet["payload"]) != row["packet_sha256"]
            or sha256(provider_bytes).hexdigest() != row["provider_file_sha256"]
            or packet["payload"]["case_id"] != cid):
        raise ValueError(cid + ": source packet/provider hash differs")
    docs = {"packet": packet["payload"], "provider": json.loads(provider_bytes)}
    if row["cohort"] == "original_v3":
        scope = read(ROOT / "credit-evidence-v3/credit_scope_v3.json")
        s = next(x for x in scope["cases"] if x["case_id"] == cid)
        if digest(s) != row["scope_sha256"]:
            raise ValueError(cid + ": credit scope hash differs")
        docs["credit_scope"] = {k: s[k] for k in
            ("case_id", "customer_id", "run_id", "as_of_at",
             "base_packet_sha256", "credit_evidence_scope")}
    elif row["cohort"] == "supplemental_credit":
        source = read(ROOT / "credit-evidence-v3/control_cases_v1.json")
        index = read(ROOT / "credit-evidence-v3/index.json")
        if sha256((ROOT / "credit-evidence-v3/control_cases_v1.json").read_bytes()).hexdigest() != index["control_source_sha256"]:
            raise ValueError("Credit control source differs")
        docs["credit_scope"] = next(x for x in source["cases"] if x["case_id"] == cid)["credit_evidence_scope"]
    return docs


def assert_blind_sources(row, docs):
    """Prevent reviewer metadata/answers entering the second model's source view.

    A product attributes_json.archetype_code is a pinned catalogue attribute,
    not the case author's scenario archetype_id; it must not be removed from a
    hash-bound PostgreSQL packet merely to hide that legitimate source fact.
    """
    if set(docs) != ({"packet", "provider"} if row["cohort"] == "supplemental_configuration"
                     else {"packet", "provider", "credit_scope"}):
        raise ValueError("Blind package contains unexpected documents")
    def inspect(value):
        if isinstance(value, dict):
            if FORBIDDEN_BLIND_KEYS.intersection(value):
                raise ValueError("Answer or authoring metadata in blind package")
            for item in value.values(): inspect(item)
        elif isinstance(value, list):
            for item in value: inspect(item)
    inspect(docs)


def blank(row):
    return {"case_id": row["case_id"], "cohort": row["cohort"],
            "packet_sha256": row["packet_sha256"],
            "provider_file_sha256": row["provider_file_sha256"],
            "scope_sha256": row.get("scope_sha256"),
            "reviewer": {"model_id": None, "reviewed_at": None,
                         "source_first_attestation": None, "assistance_disclosure": None},
            "findings": {role: {"finding": None, "rationale": None,
                                "evidence_refs": [], "calculations": [],
                                "uncertainties": [], "abstention_reason": None}
                         for role in ROLES},
            "overall": {"gate": None, "rationale": None, "evidence_refs": [],
                        "human_actions": [], "uncertainties": [], "abstention_reason": None},
            "status": "pending_second_model_review"}


def prepare(args):
    man = manifest()
    out = Path(args.output)
    # Never put freshly prepared facts alongside old model responses or
    # silently overwrite a previous frozen package.
    out.mkdir(parents=True, exist_ok=False)
    dirs = {"original_v3": Path(args.original_packets),
            "supplemental_configuration": Path(args.configuration_packets),
            "supplemental_credit": Path(args.credit_packets)}
    for row in man["cases"]:
        docs = load_case(row, dirs)
        assert_blind_sources(row, docs)
        case_dir = out / row["case_id"]
        case_dir.mkdir(exist_ok=True)
        write(case_dir / "sources.json", {"source_pins": row, "documents": docs})
        write(case_dir / "blank_response.json", blank(row))
    write(out / "manifest.json", man)
    print("39 blinded source packages prepared; no recommendation or answer files included")


def validate_response(response, row, docs):
    errors = []
    if (not isinstance(response, dict) or set(response) != set(blank(row))
            or any(response.get(k) != blank(row)[k] for k in
                   ("case_id", "cohort", "packet_sha256", "provider_file_sha256", "scope_sha256"))
            or response.get("status") != "second_model_draft_not_accepted"):
        return ["Review shape, status or source identity differs"]
    provenance = response["reviewer"]
    if (not isinstance(provenance, dict) or set(provenance) != set(blank(row)["reviewer"])
            or not all(isinstance(provenance.get(k), str) and provenance[k].strip()
                       for k in provenance)):
        errors.append("Second-model provenance/assistance disclosure incomplete")
    else:
        try:
            if datetime.fromisoformat(provenance["reviewed_at"].replace("Z", "+00:00")).tzinfo is None:
                raise ValueError()
        except ValueError:
            errors.append("Review timestamp needs timezone")
    findings = response.get("findings")
    if not isinstance(findings, dict) or set(findings) != set(ROLES):
        return errors + ["Six findings required"]
    for role, item in findings.items():
        if not isinstance(item, dict) or set(item) != set(blank(row)["findings"][role]):
            errors.append(role + ": fields differ")
            continue
        if item["finding"] not in FINDINGS or not isinstance(item["rationale"], str) or not item["rationale"].strip():
            errors.append(role + ": finding/rationale missing")
        if not isinstance(item["evidence_refs"], list) or not item["evidence_refs"]:
            errors.append(role + ": source citations missing")
        else:
            for ref in item["evidence_refs"]:
                try: source_pointer(docs, ref)
                except (ValueError, KeyError, IndexError, TypeError): errors.append(role + ": citation does not resolve")
        if (not isinstance(item["calculations"], list) or
                not isinstance(item["uncertainties"], list) or
                not all(isinstance(u, str) for u in item["uncertainties"])):
            errors.append(role + ": calculations/uncertainties must be lists")
        elif any(not isinstance(c, dict) or set(c) != {"metric", "value_eur", "formula", "evidence_refs"}
                 or not all(isinstance(c.get(k), str) and c[k].strip() for k in ("metric", "formula"))
                 or not isinstance(c.get("evidence_refs"), list) or not c["evidence_refs"]
                 for c in item["calculations"]):
            errors.append(role + ": calculation record incomplete")
        else:
            for calc in item["calculations"]:
                for ref in calc["evidence_refs"]:
                    try: source_pointer(docs, ref)
                    except (ValueError, KeyError, IndexError, TypeError):
                        errors.append(role + ": calculation citation does not resolve")
        if role in ("Pricing", "Credit") and not item["calculations"] and item["finding"] != "abstain":
            errors.append(role + ": calculation or abstention required")
        if item["finding"] == "abstain" and not item["abstention_reason"]:
            errors.append(role + ": abstention reason required")
    overall = response.get("overall")
    if (not isinstance(overall, dict) or set(overall) != set(blank(row)["overall"])
            or overall["gate"] not in GATES
            or not isinstance(overall["rationale"], str) or not overall["rationale"].strip()
            or not isinstance(overall["human_actions"], list)
            or not isinstance(overall["uncertainties"], list)
            or not isinstance(overall["evidence_refs"], list)
            or not all(isinstance(u, str) for u in overall["uncertainties"])):
        errors.append("Overall gate/actions/rationale incomplete")
    elif overall["gate"] == "abstain" and not overall["abstention_reason"]:
        errors.append("Overall abstention reason required")
    if isinstance(overall, dict) and isinstance(overall.get("evidence_refs"), list):
        for ref in overall["evidence_refs"]:
            try: source_pointer(docs, ref)
            except (ValueError, KeyError, IndexError, TypeError):
                errors.append("Overall citation does not resolve")
    return errors


def deterministic_discrepancies(response, docs):
    """Check a small, explicit arithmetic set; no inferred business label."""
    rows = docs["packet"]["source_rows"]
    quote = sum(Decimal(str(x["quantity"])) * Decimal(str(x["quoted_unit_price"]))
                for x in rows["lines"])
    expected = {"quote_total_eur": quote}
    scope = docs.get("credit_scope", {})
    scope = scope.get("credit_evidence_scope", scope)
    if scope.get("completeness") == "declared_complete_zero":
        expected["credit_exposure_eur"] = quote + Decimal(str(rows["credit"]["unbilled_committed_amount"]))
    if scope.get("completeness") == "declared_complete_nonempty":
        expected["overdue_ar_eur"] = sum(Decimal(str(x["outstanding_amount"]))
                                          for x in rows["receivables"] if x["status"] == "Overdue")
    issues = []
    seen = set()
    for role in ROLES:
        for calc in response["findings"][role]["calculations"]:
            if scope.get("completeness") == "explicitly_incomplete_unknown" and calc["metric"] in (
                    "credit_exposure_eur", "overdue_ar_eur"):
                issues.append(role + ": incomplete population cannot assert numeric " + calc["metric"])
            if calc["metric"] not in expected:
                continue
            seen.add(calc["metric"])
            try:
                actual = Decimal(str(calc["value_eur"]))
                if actual != expected[calc["metric"]]:
                    issues.append(f"{role}/{calc['metric']}: {actual} differs from source arithmetic {expected[calc['metric']]}")
            except (ValueError, TypeError):
                issues.append(f"{role}/{calc['metric']}: nonnumeric value")
            for ref in calc["evidence_refs"]:
                try: source_pointer(docs, ref)
                except (ValueError, KeyError, IndexError, TypeError): issues.append(role + ": calculation citation does not resolve")
    for metric in expected.keys() - seen:
        role = "Credit" if metric in ("credit_exposure_eur", "overdue_ar_eur") else "Pricing"
        if response["findings"][role]["finding"] != "abstain":
            issues.append(metric + ": deterministic calculation missing")
    return issues


def compare(args):
    man = manifest()
    dirs = {"original_v3": Path(args.original_packets),
            "supplemental_configuration": Path(args.configuration_packets),
            "supplemental_credit": Path(args.credit_packets)}
    matrix = read(ROOT / "reviews/v3_six_responsibility_technical_matrix.json")
    proposals = {x["case_id"]: x for x in matrix["cases"]}
    queue = []
    for row in man["cases"]:
        cid = row["case_id"]
        docs = load_case(row, dirs)
        path = Path(args.responses) / (cid + ".json")
        if not path.exists():
            queue.append({"case_id": cid, "priority": "high" if int(cid[-3:]) in HIGH_RISK else "normal",
                          "classes": ["missing_second_model_review"]})
            continue
        try:
            response = read(path)
        except (ValueError, UnicodeError):
            queue.append({"case_id": cid, "priority": "high",
                          "classes": ["invalid_or_unsupported_review"],
                          "details": ["Response is not valid JSON; raw output remains pending"]})
            continue
        errors = validate_response(response, row, docs)
        classes = ["invalid_or_unsupported_review"] if errors else []
        details = errors[:]
        if not errors and cid in proposals:
            prior = proposals[cid]
            for role in ROLES:
                a = response["findings"][role]["finding"]
                b = prior["six_responsibilities"][role]["technical_recommendation"]
                if a != b:
                    classes.append("disagreement")
                    details.append(role + ": second=" + a + ", technical=" + b)
            if response["overall"]["gate"] != prior["overall_technical_gate_proposal"]:
                classes.append("gate_disagreement")
        if not errors:
            arithmetic = deterministic_discrepancies(response, docs)
            if arithmetic:
                classes.append("deterministic_mismatch_or_missing_calculation")
                details.extend(arithmetic)
        if not errors:
            for role in ROLES:
                if response["findings"][role]["finding"] == "abstain":
                    classes.append("abstention")
                if response["findings"][role]["uncertainties"]:
                    classes.append("uncertainty")
            if cid in ("EVAL-PREP-020", "EVAL-PREP-029", "EVAL-PREP-030"):
                classes.append("business_attribution_or_route_review")
            if cid in ("EVAL-PREP-039", "EVAL-PREP-040", "EVAL-PREP-041"):
                classes.append("supplemental_source_decision")
        if classes:
            queue.append({"case_id": cid, "priority": "high" if int(cid[-3:]) in HIGH_RISK or errors else "normal",
                          "classes": sorted(set(classes)), "details": details})
    result = {"status": "automated_exception_triage_not_human_acceptance",
              "recorded_acceptances": 0,
              "cases_compared": len(man["cases"]),
              "exceptions": sorted(queue, key=lambda x: (x["priority"] != "high", x["case_id"]))}
    write(args.output, result)
    print(len(queue), "cases queued; no acceptance inferred")


def decision_template():
    return {"schema_version": 1, "status": "author_decisions_reviewer_only",
            "independent_human_expert_validation": False,
            "ready_for_generation": False,
            "cases": [{"case_id": row["case_id"], "cohort": row["cohort"],
                       "packet_sha256": row["packet_sha256"],
                       "second_model_response_sha256": None,
                       "decision": "pending", "author_identity": None,
                       "decided_at": None, "rationale": None,
                       "assistance_disclosure": None, "resolved_ambiguities": []}
                      for row in manifest()["cases"]]}


def validate_decisions(args):
    current, baseline = read(args.decisions), decision_template()
    errors = []
    if (not isinstance(current, dict) or set(current) != set(baseline)
            or any(current[k] != baseline[k] for k in baseline if k != "cases")
            or not isinstance(current["cases"], list)
            or len(current["cases"]) != 39):
        errors.append("Decision register shape or release boundary differs")
    else:
        for row, blank_row in zip(current["cases"], baseline["cases"]):
            if (not isinstance(row, dict) or set(row) != set(blank_row)
                    or any(row[k] != blank_row[k] for k in
                           ("case_id", "cohort", "packet_sha256"))):
                errors.append("Case identity or source pin differs")
                continue
            if row["decision"] == "pending":
                if row != blank_row: errors.append(row["case_id"] + ": pending row contains decision data")
                continue
            if row["decision"] not in ("author_accepted", "author_rejected", "revision_requested"):
                errors.append(row["case_id"] + ": invalid decision")
                continue
            if (not all(isinstance(row[k], str) and row[k].strip() for k in
                        ("second_model_response_sha256", "author_identity", "decided_at",
                         "rationale", "assistance_disclosure"))
                    or row["author_identity"] != "Ali Alnaggar"):
                errors.append(row["case_id"] + ": author provenance or rationale missing")
            try:
                if datetime.fromisoformat(row["decided_at"].replace("Z", "+00:00")).tzinfo is None:
                    raise ValueError()
            except (ValueError, AttributeError):
                errors.append(row["case_id"] + ": timezone-aware date required")
            response_path = Path(args.responses) / (row["case_id"] + ".json")
            if not response_path.exists() or sha256(response_path.read_bytes()).hexdigest() != row["second_model_response_sha256"]:
                errors.append(row["case_id"] + ": second-model response bytes differ")
    write(args.output, {"status": "structural_author_decision_check_not_independent_validation",
                        "errors": errors, "human_judgment_verified_by_automation": False})
    if errors: raise ValueError("; ".join(errors))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("manifest", "prepare", "compare", "decision-template", "validate-decisions"))
    p.add_argument("--original-packets")
    p.add_argument("--configuration-packets")
    p.add_argument("--credit-packets")
    p.add_argument("--responses")
    p.add_argument("--decisions")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    if a.action == "manifest": write(a.output, manifest())
    elif a.action == "prepare": prepare(a)
    elif a.action == "compare": compare(a)
    elif a.action == "decision-template": write(a.output, decision_template())
    else: validate_decisions(a)


if __name__ == "__main__":
    main()
