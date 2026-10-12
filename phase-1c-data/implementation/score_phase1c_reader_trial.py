"""Score a database-backed development trial against a separate provisional draft.

This does not create held-out labels or certify an independent reviewer.
The candidate reader and rule-only original must run before this scorer sees
the reviewer-only draft; the draft is never an input to candidate generation.
"""

from hashlib import sha256

from phase1c_candidate_trace import _canonical


def score(package, oracle):
    if (oracle.get("status") != "provisional_author_draft_pending_independent_review"
            or oracle.get("review_status") != "pending_independent_review"
            or oracle.get("reviewer") is not None
            or oracle.get("independently_reviewed_cases") != 0):
        raise ValueError("reader trial oracle is only a pending development draft")
    expected = oracle["candidates"]
    if len(expected) != 2 or len({x["candidate_id"] for x in expected}) != 2:
        raise ValueError("reader trial requires two distinct authored expectations")
    records = package["candidate_records"]
    if len(records) != 2 or len({r["payload"]["candidate"]["candidate_id"] for r in records}) != 2:
        raise ValueError("reader trial requires two distinct candidate records")
    if any(sha256(_canonical(r["payload"]).encode()).hexdigest() != r["sha256"]
           for r in records):
        raise ValueError("candidate trace content digest differs")
    actual_by_id = {r["payload"]["candidate"]["candidate_id"]: r["payload"] for r in records}
    if set(actual_by_id) != {x["candidate_id"] for x in expected}:
        raise ValueError("candidate IDs differ from the frozen development draft")
    if package["selected_candidate_id"] is not None:
        raise ValueError("a candidate was selected without human authority")
    if any(p["source_input_digest"] != package["source_input_digest"] for p in actual_by_id.values()):
        raise ValueError("candidates do not share the same reader-used facts")

    items = []
    for item in expected:
        cid = item["candidate_id"]
        payload = actual_by_id[cid]
        comparison = payload["human_comparison"]
        actual_supply = comparison["verified_supply_option"]
        expected_supply = item["supply_supported"]
        actual_date = comparison["proposed"]["availability"][0]["candidate_slices"][-1]["arrival_date"]
        checks = {
            "original_rule_only_status": payload["original_decision"]["status"] == oracle["original_decision_status"],
            "original_customer_date": payload["original_requested_date"] == oracle["original_requested_date"],
            "proposed_later_date": actual_date == item["proposed_later_date"],
            "candidate_decision_status": payload["candidate_decision"]["status"] == item["candidate_decision_status"],
            "supply_assessment": actual_supply == expected_supply,
            "source_evidence": payload["actual_source_ids"] == item["actual_source_ids"],
            "customer_constraints": payload["candidate_decision"]["customer_constraints_unmet"]
                                    == item["unmet_customer_constraints"],
            "human_action": item["human_action_contains"] in comparison["human_action"],
            "full_rerun": payload["rerun_specialists"] == oracle["rerun_specialists"],
            "read_only": payload["side_effects"] == "read_only_no_stock_or_approval_write",
        }
        items.append({
            "candidate_id": cid, "checks": checks, "all_checks_match_draft": all(checks.values()),
            "false_supported_option": actual_supply and not expected_supply,
            "missed_supported_option": expected_supply and not actual_supply,
        })
    expected_valid = sorted(x["candidate_id"] for x in expected if x["supply_supported"])
    listed_valid = sorted(package["validated_supply_option_ids"])
    return {
        "case_id": oracle["case_id"], "status": "development_diagnostic_not_independent_label",
        "original_rule_only_status": records[0]["payload"]["original_decision"]["status"],
        "candidate_results": items,
        "validated_option_list_matches_draft": listed_valid == expected_valid,
        "all_checks_match_draft": all(x["all_checks_match_draft"] for x in items)
                                  and listed_valid == expected_valid,
        "false_supported_options": sum(x["false_supported_option"] for x in items),
        "missed_supported_options": sum(x["missed_supported_option"] for x in items),
        "independently_reviewed_cases": 0,
    }
