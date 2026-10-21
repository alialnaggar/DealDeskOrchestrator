"""One explicitly opted-in M1.8 live trial; no reviewer answers enter the model.

Run in a disposable PostgreSQL job with the exact separate Phase 1C checkout.
This CLI never loops over trials, retries failures, or invokes a paid fallback.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from time import monotonic
from urllib.request import Request, urlopen
from uuid import uuid4

import psycopg

from .checkpoint import thesis_checkpointer
from .evaluation_m18 import capture_trial, pinned_baseline, structural_flags
from .investigation_graph import run_original_investigate_and_review
from .live_models import GROQ_MODEL, PROMPT_VERSION, LiveInvestigationModel
from .orchestrator import build_original_graph
from .phase1c_adapter import Phase1CAdapter


# Source identities observed in the previous clean pinned PostgreSQL run.
# These are input-integrity checks, not model-visible reviewer answers.
SOURCES = {
    "B01": ("720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526",
            "64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4"),
    "B05": ("be3a5bae596cecb0a0bf7faaf05ed06755652db1f4f7f771826a70a49ca37008",
            "3af874a55010ef7d84134d673c2e800aa984596cb6a2d5a5935395aef60f30cd"),
}


def model_available(key: str) -> bool:
    # The ID is checked before a generation call. Never log response headers,
    # provider error bodies, credential-bearing requests or a token.
    request = Request("https://api.groq.com/openai/v1/models",
                      headers={"Authorization": "Bearer " + key,
                               "User-Agent": "DealDeskOrchestrator-M18/1"})
    with urlopen(request, timeout=20) as response:
        return GROQ_MODEL in {item.get("id") for item in json.load(response).get("data", [])}


def run_one(case_id: str, trial: int, output: Path) -> dict:
    if case_id not in SOURCES or trial not in (1, 2):
        raise ValueError("Only B01/B05, repetitions 1/2 are authorized")
    if "results" not in output.parts:
        raise ValueError("Results must be placed under an ignored results/ directory")
    if os.getenv("M14_FREE_TIER_CONFIRMED") != "true":
        raise RuntimeError("Free-tier owner attestation is missing")
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("Groq credential is unavailable")
    required = ("DATABASE_URL", "CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")
    if any(not os.getenv(name) for name in required):
        raise RuntimeError("Pinned checkout and both disposable databases are required")

    # Source-first review material is never imported. This module only imports
    # synthetic rows and their case identifiers from the test fixture module.
    from m18_case_setup import CASES, install_disposable_cases
    case = next(c for c in CASES if c.case_id == case_id)
    factory = lambda: psycopg.connect(os.environ["DATABASE_URL"])
    adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
    install_disposable_cases(factory())
    assessment = "M18-LIVE-" + str(uuid4())
    pinned = adapter.read_original(factory, case.run_id, assessment)
    if (pinned.context.bundle_sha256, pinned.context.source_input_digest) != SOURCES[case_id]:
        raise RuntimeError("Sealed source identities changed; no model call permitted")
    baseline = pinned_baseline(adapter, factory, pinned)
    if not (baseline["discovered"] and
            baseline["verification"]["supply_status"] == "supply_supported_unreserved"):
        raise RuntimeError("Pinned deterministic baseline changed; no model call permitted")
    if not model_available(key):
        raise RuntimeError("Selected Groq model ID is unavailable; no generation call permitted")
    started = datetime.now(timezone.utc)
    before = monotonic()
    with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
        graph = build_original_graph(adapter, factory, saver)
        config = {"configurable": {"thread_id": assessment}}
        model = LiveInvestigationModel("groq", graph, config,
                                       pace_seconds=12, enable_binding_proposals=True)
        state = run_original_investigate_and_review(
            graph, config, adapter, model, assessment_id=assessment, run_id=case.run_id)
        # Capture the committed checkpoint rather than transient graph return.
        state = graph.get_state(config).values
    observation = capture_trial(case_id, state, baseline,
                                provider="groq", model=GROQ_MODEL,
                                prompt_version=PROMPT_VERSION + "-m17-binding-optin")
    observation["trial"] = trial
    observation["started_at_utc"] = started.isoformat()
    observation["elapsed_ms"] = round((monotonic() - before) * 1000)
    observation["configuration"] = {
        "temperature": 0, "decision_output_cap": 1024, "final_output_cap": 2048,
        "tool_call_cap": 12, "source_record_cap": 25, "sequential": True,
        "phase1c_commit": "90c0bc8e285ee69262c7db826b786096a77ad004",
    }
    observation["mechanical_flags"] = structural_flags(observation)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(observation, indent=2, sort_keys=True, default=str) + "\n")
    # A small sanitized line for Actions; the detailed synthetic-case record is
    # a short-retention artifact, never a raw HTTP request/response log.
    print(json.dumps({"case_id": case_id, "trial": trial,
                      "assessment_id": assessment, "ai_execution": observation["ai_execution"],
                      "candidate_status": observation["candidate_status"],
                      "candidate_count": len(observation["candidates"]),
                      "tool_calls": observation["tool_calls"],
                      "model_attempts": len(observation["model_attempts"]),
                      "elapsed_ms": observation["elapsed_ms"]}, sort_keys=True))
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--case-id", choices=tuple(SOURCES), required=True)
    parser.add_argument("--trial", type=int, choices=(1, 2), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("Live generation requires an explicit --live switch")
    run_one(args.case_id, args.trial, args.output)


if __name__ == "__main__":
    main()
