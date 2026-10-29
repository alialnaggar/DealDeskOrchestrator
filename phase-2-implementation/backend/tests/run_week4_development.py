"""Offline Week 4 engineering cohort; requires preloaded disposable PostgreSQL.

No answer sheet, provider or candidate baseline is sent to a model. The
baseline and scripted candidate are assessed on separate checkpoint threads.
"""

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
from time import perf_counter_ns

import psycopg

from dealdesk_phase2.candidate_contract import CANDIDATE_VERSION
from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.evaluation_m18 import pinned_baseline
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.graph_state import SPECIALISTS, STATE_VERSION, pinned_from_state
from dealdesk_phase2.investigation_graph import run_original_investigate_and_review
from dealdesk_phase2.m20_specialists import VERSION as M20_VERSION
from dealdesk_phase2.m21_specialists import VERSION as M21_VERSION
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT, EvidenceMismatch, Phase1CAdapter
from dealdesk_phase2.week3_development import capture_original_development
from dealdesk_phase2.week3_offline import run_week3_offline
from m18_case_setup import CASES
from run_week3_development import disposable_pair
from test_week3_offline import models


VERSION = "week4-offline-development-v1"
SCENARIOS = tuple((case.case_id, case.case_id == "B05") for case in CASES)


def _candidate_actions(case):
    """Predeclared B01 script, not derived from discovery or reviewer answers."""
    ids = case.ids()
    return ({"type": "tool", "tool": "inspect_fulfillment_paths",
             "arguments": {"line_id": ids["L"]}},
            {"type": "contribution", "value": {"schema_version": "3",
             "kind": "binding_proposal", "payload": {"line_id": ids["L"],
             "delivery_slices": [
                 {"quantity": "8", "delivery_date": "2026-09-04",
                  "source_refs": ["inventory:" + ids["INV"]]},
                 {"quantity": "2", "delivery_date": "2026-09-08",
                  "source_refs": ["inbound_supply:" + ids["IN"]]}],
             "tradeoff_code": "partial_delivery_requires_customer_acceptance"}}})


def _candidate_record(state, baseline, adapter):
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    if (ctx.original_deal_id != baseline["deal_id"]
            or str(ctx.phase1c_run_id) != baseline["run_id"]
            or ctx.bundle_sha256 != baseline["bundle_sha256"]
            or ctx.source_input_digest != baseline["source_input_digest"]
            or state.get("candidate_status") != "fixed_checked"
            or state.get("stop_reason") or len(state.get("candidate_records", {})) != 1):
        raise EvidenceMismatch("Week 4 candidate and deterministic baseline diverged")
    candidate = next(iter(state["candidate_records"].values()))
    original = state["specialist_results"]
    if (set(original) != set(SPECIALISTS)
            or set(candidate["specialist_results"]) != set(SPECIALISTS)
            or candidate["parent_run_id"] != baseline["run_id"]
            or candidate["parent_deal_id"] != baseline["deal_id"]
            or candidate["source_input_digest"] != ctx.source_input_digest
            or candidate["bundle_sha256"] != ctx.bundle_sha256
            or any(x["subject_id"] != candidate["candidate_id"] or
                   x["producer_type"] != "deterministic"
                   for x in candidate["specialist_results"].values())
            or any(x["subject_id"] != baseline["deal_id"] for x in original.values())
            or state["reviewer_package"].get("candidates", [{}])[0].get(
                "candidate_id") != candidate["candidate_id"]):
        raise EvidenceMismatch("Week 4 candidate subject or reviewer handoff changed")
    refs = {ref for event in state.get("tool_access_ledger", [])
            if event["status"] == "completed" and event["tool"] == "inspect_fulfillment_paths"
            and event["identity"]["assessment_id"] == ctx.assessment_id
            and event["identity"]["bundle_sha256"] == ctx.bundle_sha256
            for ref in event["returned_refs"]}
    cited = {ref for part in candidate["proposed_slices"] for ref in part["source_refs"]}
    if not cited or not cited <= refs:
        raise EvidenceMismatch("Week 4 candidate cites a source not returned by a tool")
    review = state["reviewer_package"]["candidates"][0]
    return {"assessment_id": ctx.assessment_id, "case_id": baseline["deal_id"],
        "bundle_sha256": ctx.bundle_sha256, "source_input_digest": ctx.source_input_digest,
        "proposal_contract": CANDIDATE_VERSION, "proposal_kind": "binding_proposal",
        "proposal_source": "predeclared_offline_script_not_model_reasoning",
        "candidate_id": candidate["candidate_id"], "candidate_status": candidate["status"],
        "fixed_supply_status": candidate["fixed_supply_status"],
        "fixed_business_status": candidate["fixed_business_status"],
        "fixed_rechecks": {k: {"execution": v["execution"], "finding": v["finding"]}
            for k, v in candidate["specialist_results"].items()},
        "citations_returned": True, "returned_source_count": len(refs),
        "customer_acceptance": review["customer_acceptance"],
        "human_approval": "not_granted_by_system",
        "same_schedule_as_fixed_discovery": [(s["quantity"], s["delivery_date"])
            for s in candidate["proposed_slices"]] == [(s["quantity"], s["delivery_date"])
            for s in baseline["candidate"]["slices"]] if baseline["candidate"] else None,
        "baseline_discovered": baseline["discovered"],
        "baseline_fixed_supply_status": (baseline["verification"] or {}).get("supply_status")}


def summarize(scenarios, candidate):
    """Count observed structures only; reject duplicates and partial records."""
    if (len({x["case_id"] for x in scenarios}) != len(scenarios)
            or len({x["assessment_id"] for x in scenarios}) != len(scenarios)
            or len({x["bundle_sha256"] for x in scenarios}) != len(scenarios)):
        raise EvidenceMismatch("Week 4 cases or frozen bundles duplicated")
    if any(set(x["offline_ai"]) != set(SPECIALISTS) or
           set(x["deterministic_baseline"]["specialists"]) != set(SPECIALISTS)
           or x["candidate_status"] != "not_started" for x in scenarios):
        raise EvidenceMismatch("Week 4 original cohort is incomplete or includes candidate")
    ai = Counter(v["execution"] for x in scenarios for v in x["offline_ai"].values())
    fixed = Counter(v["execution"] for x in scenarios
                    for v in x["deterministic_baseline"]["specialists"].values())
    contribution = Counter(x["offline_ai"]["fulfillment"].get("contribution_kind")
                           for x in scenarios)
    attempts = Counter(row["status"] for x in scenarios
                       for group in x["attempts"].values() for row in group)
    baseline = Counter(x["fixed_discovery"]["discovered"] for x in scenarios)
    if (candidate["case_id"] not in {x["case_id"] for x in scenarios}
            or candidate["fixed_supply_status"] != candidate["baseline_fixed_supply_status"]):
        raise EvidenceMismatch("Week 4 candidate has no matching fixed discovery")
    return {"original_cases": len(scenarios), "deterministic_mappings": dict(sorted(fixed.items())),
        "offline_ai_execution": dict(sorted(ai.items())),
        "fulfillment_contribution_kinds": {str(k): v for k, v in sorted(
            contribution.items(), key=lambda pair: str(pair[0]))},
        "validated_claims": sum(len(v["validated_claims"]) for x in scenarios
                                for v in x["offline_ai"].values()),
        "results_with_validated_claims": sum(bool(v["validated_claims"])
            for x in scenarios for v in x["offline_ai"].values()),
        "tool_reserved": sum(e["status"] == "reserved" for x in scenarios for e in x["tool_trace"]),
        "tool_completed": sum(e["status"] == "completed" for x in scenarios for e in x["tool_trace"]),
        "model_attempt_record_statuses": dict(sorted(attempts.items())),
        "model_turns_recorded_for_five_specialists": sum(v.get("model_turns") or 0
            for x in scenarios for name, v in x["offline_ai"].items() if name != "fulfillment"),
        "tool_budget_exhausted_events": sum(e["status"] == "budget_exhausted"
            for x in scenarios for e in x["tool_trace"]),
        "fixed_discovery": {"discovered": baseline[True], "not_discovered": baseline[False]},
        "candidate_fixed_checked": int(candidate["candidate_status"] == "fixed_checked"),
        "candidate_fixed_rechecks": len(candidate["fixed_rechecks"]),
        "candidate_source_returned": candidate["citations_returned"],
        "accepted_answer_accuracy": None, "model_reasoning_quality": "not_measured",
        "hosted_reliability": "not_measured"}


def run(connect, checkpoint_url, adapter):
    expected = {case.ids()["D"] for case in CASES}
    with connect() as db:
        present = {row[0] for row in db.execute(
            "SELECT deal_id FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'")}
    if present != expected:
        raise ValueError("Week 4 requires exactly nine preloaded disposable M1.8 source deals")
    scenarios = []
    measured = []
    for label, adverse in SCENARIOS:
        case = next(c for c in CASES if c.case_id == label)
        assessment = f"DEV-W4-{VERSION}-{label}-{'adverse' if adverse else 'nominal'}"
        config = {"configurable": {"thread_id": assessment}}
        model = OfflineModelDouble(({"type": "contribution", "value": {
            "kind": "abstention", "payload": {"reason": "No supportable suggestion",
                "uncertainty_reasons": ["No binding evidence"]}}},))
        m20, m21 = models(adverse=adverse)
        start = perf_counter_ns()
        with thesis_checkpointer(checkpoint_url) as saver:
            graph = build_original_graph(adapter, connect, saver)
            state = run_week3_offline(graph, config, adapter, model, m20, m21,
                assessment_id=assessment, run_id=case.run_id)
            captured = capture_original_development(state, adapter)
        elapsed = (perf_counter_ns() - start) // 1_000_000
        pinned = adapter.read_original(connect, case.run_id, assessment)
        baseline = pinned_baseline(adapter, connect, pinned)
        if (captured["bundle_sha256"] != baseline["bundle_sha256"]
                or captured["source_input_digest"] != baseline["source_input_digest"]
                or captured["phase1c_run_id"] != baseline["run_id"]
                or captured["deterministic_baseline"]["decision_status"] != baseline[
                    "original"]["business_status"]):
            raise EvidenceMismatch("Week 4 original and discovery source identities differ")
        captured["fixed_discovery"] = {"discovered": baseline["discovered"],
            "reason": baseline["reason"],
            "fixed_supply_status": (baseline["verification"] or {}).get("supply_status"),
            "fixed_business_status": (baseline["verification"] or {}).get("business_status")}
        scenarios.append(captured)
        measured.append({"case_id": captured["case_id"], "original_wall_ms": elapsed})

    case = CASES[0]  # predeclared B01 binding alternative, separate graph/thread
    assessment = "DEV-W4-ISOLATED-CANDIDATE-B01-v1"
    config = {"configurable": {"thread_id": assessment}}
    start = perf_counter_ns()
    with thesis_checkpointer(checkpoint_url) as saver:
        graph = build_original_graph(adapter, connect, saver)
        state = run_original_investigate_and_review(graph, config, adapter,
            OfflineModelDouble(_candidate_actions(case)), assessment_id=assessment,
            run_id=case.run_id)
        baseline = pinned_baseline(adapter, connect, pinned_from_state(state))
        candidate = _candidate_record(state, baseline, adapter)
    measured.append({"case_id": candidate["case_id"], "candidate_wall_ms":
                    (perf_counter_ns() - start) // 1_000_000})
    summary = summarize(scenarios, candidate)
    fixture = Path(__file__).with_name("m18_case_setup.py")
    schema = adapter.checkout / "phase-1c-data" / "implementation" / "schema.sql"
    stable = {"version": VERSION, "phase1c_pin": PHASE1C_COMMIT,
        "contracts": {"graph_state": STATE_VERSION, "m20": M20_VERSION,
            "m21": M21_VERSION, "candidate": CANDIDATE_VERSION},
        "source_hashes": {"fixture_sha256": sha256(fixture.read_bytes()).hexdigest(),
            "schema_sha256": sha256(schema.read_bytes()).hexdigest()},
        "cohort": "development_only_scripted_offline", "independent_answers_accepted": 0,
        "provider_requests": 0, "scenarios": scenarios, "isolated_candidate": candidate,
        "summary": summary}
    blob = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return {**stable, "stable_result_sha256": sha256(blob).hexdigest(),
        "timing_diagnostics": {"units": "wall_ms", "scope": "includes DB and checkpoint; fresh or resumed, not comparable",
            "observations": measured, "tokens": None, "api_cost_usd": None}}


def report(data):
    totals = data["summary"]
    lines = ["# Week 4 offline development evaluation", "",
        "Nine distinct pinned synthetic deals, five binding-source shapes and four negative controls. "
        "0/36 independently accepted evaluation answers; no semantic accuracy or real-model quality measured.", "",
        "| Deal | Fixed original | Discovery (fixed) | Fulfillment AI execution / contribution | Other offline AI exceptions |",
        "| --- | --- | --- | --- | --- |"]
    for x in data["scenarios"]:
        exceptions = ", ".join(k + ":" + v["execution"] for k, v in x["offline_ai"].items()
            if k != "fulfillment" and v["execution"] != "completed") or "none"
        f = x["offline_ai"]["fulfillment"]
        lines.append(f"| {x['case_id']} | {x['deterministic_baseline']['review_status']} | "
                     f"{x['fixed_discovery']['discovered']} | {f['execution']} / "
                     f"{f.get('contribution_kind')} | {exceptions} |")
    return "\n".join(lines + ["", "**Structural diagnostics:** " + json.dumps(totals, sort_keys=True),
        "", "A separate B01 checkpoint runs a predeclared scripted two-slice Fulfillment "
        "hypothesis. The pinned verifier rechecks all six deterministic responsibilities; "
        f"supply: `{data['isolated_candidate']['fixed_supply_status']}`, "
        f"business: `{data['isolated_candidate']['fixed_business_status']}`, "
        f"customer acceptance: `{data['isolated_candidate']['customer_acceptance']}`. "
        "Matching the fixed discovery is **not** added AI value. No candidate is created "
        "in the nine original-only investigations.", "",
        "Counts describe contracts, source visibility and fault containment, not model "
        "accuracy or business correctness against independent answers. Reserved and "
        "returned attempt records are ledger transitions, not unique provider sends or "
        "retries. This run exercises replay; interruption/no-replay and budget-exhaustion "
        "are tested separately, not measured here. Duration includes DB/checkpoint "
        "and is nonreproducible (fresh versus resume). No tokens or API cost exist offline. "
        "Execution `completed` may contain an abstention contribution; `error` is not a "
        "validated finding. N01 disallows partial delivery, N02 cancels inbound, N03 "
        "has stale stock evidence and N04 lacks supply. N01 can still enter Fulfillment "
        "investigation but cannot produce a permitted partial candidate. Conditional "
        "supplier offers are exercised by existing separate fault tests, not this cohort. "
        "The fixture cohort shares one product class, policy and region.", "",
        f"Stable projection SHA-256: `{data['stable_result_sha256']}` (excludes timing only). "
        "Re-running on the same threads tests idempotence, not another independent case.", "",
        "## Run", "", "With the locked backend virtual environment, already-running "
        "local `/tmp/opencode` disposable PostgreSQL test cluster and clean exact pinned "
        "Phase 1C checkout, set `PYTHONPATH` to the Phase 2 backend and tests and run "
        "this single command (adjust the local PostgreSQL bin/lib paths if necessary):", "",
        "```sh", "python phase-2-implementation/backend/tests/run_week4_disposable.py \\",
        "  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \\",
        "  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \\",
        "  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \\",
        "  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \\",
        "  --json /tmp/opencode/week4.json --markdown /tmp/opencode/week4.md",
        "```", "", "The command creates two **new** disposable databases, loads the "
        "pinned schema, reference rows, compiled rules and synthetic fixtures, then runs "
        "the offline cohort. It does not drop databases or install services. "
        "For an already preloaded paired recovery cohort, use "
        "`run_week4_development.py` with `--json` and `--markdown` instead. "
        "No provider credentials, answer sheets, live inference, activation, "
        "business reservation, approval or CI invocation are used.", ""])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    for key in ("DEALDESK_PHASE1C_CHECKOUT", "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL"):
        if not os.getenv(key):
            parser.error(key + " is required")
    identities = []
    for key in ("M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL"):
        with psycopg.connect(os.environ[key]) as db:
            identities.append(db.execute("SELECT current_database(), current_setting('data_directory')").fetchone())
    if not disposable_pair(identities):
        parser.error("Only paired disposable recovery_* databases on /tmp/opencode are allowed")
    adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
    result = run(lambda: psycopg.connect(os.environ["M20_DATABASE_URL"]),
                 os.environ["M20_CHECKPOINT_DATABASE_URL"], adapter)
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(report(result))


if __name__ == "__main__":
    main()
