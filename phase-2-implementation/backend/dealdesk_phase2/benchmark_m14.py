"""Explicit opt-in, sequential live trials on the two actual pinned references.

Repeated trials estimate stability, not independent business-case accuracy.
Requires a pinned Phase 1C checkout and isolated existing PostgreSQL test DBs.
No API call is made without --live and the corresponding environment key.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from time import sleep
from uuid import UUID, uuid4

import psycopg

from .checkpoint import thesis_checkpointer
from .live_models import GEMINI_MODEL, GROQ_MODEL, PROMPT_VERSION, LiveInvestigationModel
from .orchestrator import build_original_graph
from .investigation_graph import run_original_then_investigate
from .phase1c_adapter import Phase1CAdapter


BINDING_RUN = UUID("00000000-0000-4000-8000-000000010001")
OFFER_RUN = UUID("00000000-0000-4000-8000-000000030001")


def _trial(provider, case, trial, saver, adapter, factory):
    assessment = "M14-" + str(uuid4())
    graph = build_original_graph(adapter, factory, saver)
    config = {"configurable": {"thread_id": assessment}}
    model = LiveInvestigationModel(provider, graph, config, pace_seconds=12)
    run = BINDING_RUN if case == "binding" else OFFER_RUN
    started = datetime.now(timezone.utc)
    state = run_original_then_investigate(graph, config, adapter, model,
                                          assessment_id=assessment, run_id=run)
    ai = state["ai_fulfillment_result"]
    contribution = ai.get("contribution") or {}
    model_records = [x for x in state.get("model_attempt_ledger", [])
                     if x["status"] in ("completed", "error")]
    return {"case_id": f"pinned-{case}-repeat-{trial:02}",
            "source_kind": "actual_pinned_reference_repeated_trial",
            "assessment_id": assessment, "phase1c_run_id": str(run),
            "source_fingerprint": state["context"]["source_input_digest"],
            "bundle_sha256": state["context"]["bundle_sha256"],
            "provider": provider, "requested_model": GROQ_MODEL if provider == "groq" else GEMINI_MODEL,
            "prompt_version": PROMPT_VERSION, "temperature": 0,
            "decision_output_cap": 1024, "final_output_cap": 2048,
            "response_models": list(dict.fromkeys(x.get("response_model") for x in model_records)),
            "timestamp_utc": started.isoformat(),
            "elapsed_ms": round((datetime.now(timezone.utc) - started).total_seconds() * 1000),
            "execution": ai["execution"], "contribution_kind": contribution.get("kind"),
            "verification": contribution.get("verification"), "error": ai.get("error"),
            "citations": (contribution.get("payload") or {}).get("citations", []),
            "tool_calls": sum(bool(x.get("counted")) for x in state.get("tool_access_ledger", [])),
            "model_requests": len(model_records),
            "input_tokens": sum(x.get("usage", {}).get("input_tokens") or 0 for x in model_records),
            "output_tokens": sum(x.get("usage", {}).get("output_tokens") or 0 for x in model_records),
            "thinking_tokens": sum(x.get("usage", {}).get("thinking_tokens") or 0 for x in model_records),
            "http_or_parse_errors": [x.get("error_code") for x in model_records
                                     if x["status"] == "error"],
            "fixed_review_status": state["review_status"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly permit live API calls")
    parser.add_argument("--provider", choices=("groq", "gemini"), required=True)
    parser.add_argument("--offer-repeats", type=int, default=10)
    parser.add_argument("--binding-repeats", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error("Live requests require --live; routine CI never invokes this module")
    if "results" not in args.output.parts:
        parser.error("Place local output inside an ignored results/ directory")
    if not (0 <= args.offer_repeats <= 10 and 0 <= args.binding_repeats <= 2):
        parser.error("Approved trial caps: up to ten offer and two binding repetitions")
    key = "GROQ_API_KEY" if args.provider == "groq" else "GEMINI_API_KEY"
    if not os.environ.get(key):
        parser.error(f"{key} must be set securely in the process environment")
    required = ("DATABASE_URL", "CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")
    if any(not os.environ.get(x) for x in required):
        parser.error("Pinned checkout and isolated PostgreSQL configuration are required")
    adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
    records = []
    with thesis_checkpointer(os.environ["CHECKPOINT_DATABASE_URL"]) as saver:
        for case, count in (("binding", args.binding_repeats), ("offer", args.offer_repeats)):
            for index in range(1, count + 1):
                record = _trial(args.provider, case, index, saver, adapter,
                                lambda: psycopg.connect(os.environ["DATABASE_URL"]))
                records.append(record)
                # Only sanitized measurements and public fixture identities are printed.
                print(json.dumps(record, sort_keys=True), flush=True)
                if any(code == "http_429" for code in record["http_or_parse_errors"]):
                    print("Quota response; stopped without substituting another model", flush=True)
                    break
                sleep(20)
            if records and "http_429" in records[-1]["http_or_parse_errors"]:
                break
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
