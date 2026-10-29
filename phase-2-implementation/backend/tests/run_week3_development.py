"""Development-only pinned PostgreSQL runner; never loads answer drafts.

Run after the repository's disposable CI-style Phase 1C schema/fixture setup.
Requires an existing isolated M20 business and checkpoint database. It creates
only new checkpoint threads and writes local JSON/Markdown reports, not deals.
"""

import argparse
import json
import os
from pathlib import Path

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.fulfillment_agent import OfflineModelDouble
from dealdesk_phase2.orchestrator import build_original_graph
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from dealdesk_phase2.week3_development import VERSION, capture_original_development
from dealdesk_phase2.week3_offline import run_week3_offline
from m18_case_setup import CASES
from test_week3_offline import models

import psycopg


SCENARIOS = (("B01", False), ("B05", True), ("N03", False))


def disposable_pair(identities: list[tuple[str, str]]) -> bool:
    """CLI safety guard; a name alone is not proof of production freshness."""
    if len(identities) != 2:
        return False
    (business, business_dir), (checkpoint, checkpoint_dir) = identities
    return (business.startswith("recovery_") and business.endswith("_m20")
        and checkpoint == business + "_checkpoint"
        and all(Path(directory).resolve().is_relative_to("/tmp/opencode")
                for directory in (business_dir, checkpoint_dir)))


def run_development(connect, checkpoint_url: str, adapter) -> dict:
    """Three distinct disposable source cases, not independent answer labels."""
    observations = []
    with connect() as conn:
        present = {r[0] for r in conn.execute(
            "SELECT deal_id FROM deal_desk.deals WHERE deal_id IN "
            "('M18-D-B01','M18-D-B05','M18-D-N03')")}
    if present != {"M18-D-B01", "M18-D-B05", "M18-D-N03"}:
        raise ValueError("Disposable Phase 2 M1.8 fixture not loaded; do not auto-write deals")
    for label, adverse in SCENARIOS:
        case = next(x for x in CASES if x.case_id == label)
        assessment = f"DEV-W3-{VERSION}-{label}-{'adverse' if adverse else 'nominal'}"
        config = {"configurable": {"thread_id": assessment}}
        fulfillment = OfflineModelDouble(({"type": "contribution", "value": {
            "kind": "abstention", "payload": {"reason": "No supportable suggestion",
                "uncertainty_reasons": ["No binding evidence"]}}},))
        m20, m21 = models(adverse=adverse)
        with thesis_checkpointer(checkpoint_url) as saver:
            graph = build_original_graph(adapter, connect, saver)
            state = run_week3_offline(graph, config, adapter, fulfillment, m20, m21,
                assessment_id=assessment, run_id=case.run_id)
            observations.append(capture_original_development(state, adapter))
    return {"version": VERSION, "cohort": "development_only_pinned_synthetic",
        "independent_answers_accepted": 0, "provider_requests": 0,
        "scenarios": observations,
        "summary": {"scenarios": len(observations), "fixed_results": sum(len(
            x["deterministic_baseline"]["specialists"]) for x in observations),
            "completed_ai_results": sum(v["execution"] == "completed"
                for x in observations for v in x["offline_ai"].values()),
            "skipped_ai_results": sum(v["execution"] == "skipped"
                for x in observations for v in x["offline_ai"].values()),
            "abstained_ai_results": sum(v["execution"] == "abstained"
                for x in observations for v in x["offline_ai"].values()),
            "fulfillment_contribution_abstentions": sum(x["offline_ai"]["fulfillment"].get(
                "contribution_kind") == "abstention" for x in observations),
            "error_ai_results": sum(v["execution"] == "error"
                for x in observations for v in x["offline_ai"].values()),
            "accepted_answer_accuracy": None,
            "hosted_model_reliability": "not_measured"}}


def report(data: dict) -> str:
    rows = ["# Six-specialist offline development baseline", "",
        "Pinned synthetic cases only; **0 independently accepted answer labels**. "
        "Scripted model actions are engineering probes, not evidence of real-model quality.",
        "No Groq request, hosted activation, business write or deal approval.", "",
        "| Case | Fixed review | AI executions (Fulfillment / Configuration / Pricing / Credit / Policy / Routing) | Candidate |",
        "| --- | --- | --- | --- |"]
    order = ("fulfillment", "configuration", "pricing", "credit", "policy",
             "approval_routing")
    for case in data["scenarios"]:
        ai = case["offline_ai"]
        rows.append("| " + case["case_id"] + " | " + case["deterministic_baseline"][
            "review_status"] + " | " + " / ".join(ai[n]["execution"] for n in order)
            + " | " + case["candidate_status"] + " |")
    return "\n".join(rows + ["",
        "## What was exercised", "",
        "- B01: one pinned original with six fixed mappings; the six eligible "
        "offline AI paths include a Fulfillment **abstention contribution** "
        "(its execution status is `completed`, not a model-supplied proposal). "
        "The fixed route is withheld; no customer commitment or approval occurs.",
        "- B05: an invented Credit reference is rejected (zero validated Credit "
        "claims), Policy abstains, and the other domains' original fixed "
        "results remain intact. The Credit error is recorded by outcome code; "
        "the attempted raw claim is not reproduced in this sanitized report. "
        "The attempted AI finding is not ground truth.",
        "- N03: stale source evidence prevents Fulfillment investigation; an "
        "empty Policy projection makes the scripted citation fail. Neither "
        "the skipped nor failed specialist is reported as an AI finding.", "",
        "The companion JSON contains frozen source/run/bundle identities, six "
        "deterministic mappings of **one** Phase 1C decision, five validated "
        "AI-investigation results plus Fulfillment, bounded citation references, "
        "tool/attempt trace, abstentions and failures. Model-double actions "
        "and their outcomes are developer-authored; fixed-rule consistency is "
        "checked against the pinned decision, not independent human answers.", "",
        "## Reproduce and interpret", "",
        "Follow `.github/workflows/phase2-m1-contracts.yml` to provision "
        "**disposable** seven-DB PostgreSQL fixtures and a clean separate "
        "Phase 1C checkout at `90c0bc8e285ee69262c7db826b786096a77ad004`. "
        "Install the locked backend dependencies, load the pinned schema, "
        "reference rows, compiled rules and M1.8 synthetic cases in the "
        "disposable M20 business DB using `install_disposable_cases`. The CLI "
        "requires matching `recovery_*_m20` / `_m20_checkpoint` databases in "
        "a local `/tmp/opencode` test cluster and refuses arbitrary DBs. "
        "Export only `DEALDESK_PHASE1C_CHECKOUT`, "
        "`M20_DATABASE_URL`, `M20_CHECKPOINT_DATABASE_URL` and `PYTHONPATH` "
        "for the backend and tests; the runner refuses missing cases and never "
        "loads a fixture into an existing business DB. Run:", "",
        "```sh", "python phase-2-implementation/backend/tests/run_week3_development.py \\",
        "  --json phase-2-implementation/evaluation/week3-six-specialist-development.json \\",
        "  --markdown phase-2-implementation/evaluation/week3-six-specialist-development.md",
        "```", "",
        "Only the original-only six-AI composition is measured here. The "
        "existing M1.7/M1.8 Fulfillment candidate tests separately exercise "
        "a scripted binding proposal and full **six deterministic** candidate "
        "recheck; they are not a six-AI candidate continuation. No accepted "
        "answers are exposed to models. The 36 provisional Phase 1C packets "
        "have 0/36 independently accepted labels; no accuracy, improvement, "
        "model reliability, CI pass or hosted compatibility is inferred.", ""])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    for key in ("M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL",
                "DEALDESK_PHASE1C_CHECKOUT"):
        if not os.getenv(key):
            parser.error(f"{key} is required (disposable PostgreSQL only)")
    adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
    connect = lambda: psycopg.connect(os.environ["M20_DATABASE_URL"])
    # CLI is intentionally narrower than the CI/test helper: never create a
    # thread in an arbitrary owner, shared, or production PostgreSQL service.
    identities = []
    for key in ("M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL"):
        with psycopg.connect(os.environ[key]) as db:
            name, directory = db.execute(
                "SELECT current_database(), current_setting('data_directory')").fetchone()
        identities.append((name, directory))
    if not disposable_pair(identities):
        parser.error("CLI requires paired disposable recovery_* DBs on /tmp/opencode")
    result = run_development(connect, os.environ["M20_CHECKPOINT_DATABASE_URL"], adapter)
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(report(result))


if __name__ == "__main__":
    main()
