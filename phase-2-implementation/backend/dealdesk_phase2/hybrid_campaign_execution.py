"""Dormant hosted campaign binding; never called by ordinary assessments.

Identity manifest contains no reviewer schedule or answer and is never passed
into Groq requests. The only transport is the existing individually reserved
hybrid evaluation, after all read-only case checks and an explicit campaign gate.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import stat
from uuid import UUID, uuid4

import psycopg
from langgraph.checkpoint.memory import InMemorySaver

from .checkpoint import thesis_checkpointer
from .fulfillment_agent import eligible_line
from .graph_state import pinned_from_state
from .hybrid_campaign import (CASE_ORDER, CONTROLS, ELIGIBLE, IDENTITIES_SHA256,
                              CONTAINED_MODEL_ERRORS,
                              CampaignStop, CaseReceipt, campaign_digest, run_campaign)
from .hybrid_evaluation import capture_hybrid, summarize_hybrid
from .hybrid_offline import HOSTED_BUDGET, run_hybrid_evaluation
from .hybrid_pack import _canonical
from .hybrid_provider import GroqHybridTransportModel
from .orchestrator import build_original_graph, initial_state
from .phase1c_adapter import Phase1CAdapter


def load_identities(path: Path) -> dict:
    """Reviewer-only exact source identities; never embed answers in agent input."""
    raw = path.read_bytes()
    if len(raw) > 8192:
        raise CampaignStop("campaign_identity_manifest_oversize")
    data = json.loads(raw)
    if (sha256(_canonical(data).encode()).hexdigest() != IDENTITIES_SHA256
            or set(data) != {"version", "case_order", "cases"}
            or data["version"] != "hybrid-groq-campaign-identities-v1"
            or tuple(data["case_order"]) != CASE_ORDER
            or set(data["cases"]) != set(CASE_ORDER)):
        raise CampaignStop("campaign_identity_manifest_changed")
    for item in data["cases"].values():
        if (set(item) != {"run_id", "bundle_sha256", "source_input_digest"}
                or len(item["bundle_sha256"]) != 64
                or len(item["source_input_digest"]) != 64):
            raise CampaignStop("campaign_identity_manifest_invalid")
        UUID(item["run_id"])
    return data["cases"]


def inspect_sources(adapter, connect_for_case, identities):
    """Read-only original six-check gate over every case before the first send."""
    for case_id in CASE_ORDER:
        connect = connect_for_case(case_id)
        original = build_original_graph(adapter, connect, InMemorySaver())
        identifier = "HYBRID-CAMPAIGN-PREFLIGHT-" + case_id
        row = identities[case_id]
        run_id = UUID(row["run_id"])
        pinned = adapter.read_original(connect, run_id, identifier)
        if (pinned.context.bundle_sha256 != row["bundle_sha256"]
                or pinned.context.source_input_digest != row["source_input_digest"]):
            raise CampaignStop("source_identity_changed:" + case_id)
        config = {"configurable": {"thread_id": identifier}}
        state = original.invoke(initial_state(identifier, run_id), config)
        if (len(state.get("specialist_results", {})) != 6
                or state.get("stop_reason") is not None):
            raise CampaignStop("original_fixed_check_incomplete:" + case_id)
        selected, reason = eligible_line(state, adapter.validate_pinned_context(
            pinned_from_state(state)))
        if (case_id in ELIGIBLE and (selected is None or reason != "eligible")
                or case_id in CONTROLS and selected is not None):
            raise CampaignStop("eligibility_changed:" + case_id)


def _check_databases(fixture: str, reference: str, checkpoint: str):
    """Reference and synthetic selections must remain isolated and checkpoint fresh."""
    names = []
    for dsn in (fixture, reference):
        with psycopg.connect(dsn, options="-c default_transaction_read_only=on") as conn:
            name = conn.execute("SELECT current_database()").fetchone()[0]
            if not name.startswith("dealdesk_hybrid_campaign_"):
                raise CampaignStop("fixture_database_not_disposable")
            names.append(name)
    with psycopg.connect(checkpoint, options="-c default_transaction_read_only=on") as conn:
        checkpoint_name = conn.execute("SELECT current_database()").fetchone()[0]
        if (not checkpoint_name.startswith("dealdesk_hybrid_campaign_")
                or len({*names, checkpoint_name}) != 3):
            raise CampaignStop("checkpoint_database_not_isolated")
        existing = conn.execute("SELECT to_regclass('public.checkpoints')").fetchone()[0]
        if existing and conn.execute("SELECT count(*) FROM public.checkpoints").fetchone()[0]:
            raise CampaignStop("checkpoint_database_not_fresh")


def execute_authorized_campaign(*, authorized: bool, approved_digest: str,
                                identities_path: Path, pinned_checkout: Path,
                                fixture_database: str, reference_database: str,
                                checkpoint_database: str,
                                reservation_directory: Path) -> dict:
    """Call only after explicit approval of the exact case set and manifest digest.

    Do not use a historical B01 checkpoint or receipts. The caller must run the
    sanitized metadata GET and confirm account free tier/quota and human consent
    before calling; this function deliberately does not read credentials or
    make an unapproved metadata request itself. All sends use Groq's existing
    three-request per-case reserved boundary and no-retry policy.
    """
    if authorized is not True or approved_digest != campaign_digest():
        raise CampaignStop("campaign_not_authorized")
    if not os.environ.get("GROQ_API_KEY"):
        raise CampaignStop("credential_unavailable")
    identities = load_identities(identities_path)
    _check_databases(fixture_database, reference_database, checkpoint_database)
    adapter = Phase1CAdapter(pinned_checkout)
    def connect_for_case(case_id):
        dsn = reference_database if case_id == "R03" else fixture_database
        return lambda: psycopg.connect(dsn)

    inspect_sources(adapter, connect_for_case, identities)
    if HOSTED_BUDGET["revision_enabled"] is not False:
        raise CampaignStop("hosted_revision_not_disabled")

    with thesis_checkpointer(checkpoint_database) as saver:
        def execute_case(case_id, remaining_requests, remaining_output):
            # The campaign coordinator reserves this case on disk before entry.
            if (remaining_requests < HOSTED_BUDGET["max_requests"]
                    or remaining_output < HOSTED_BUDGET["max_output_tokens"]):
                raise CampaignStop("aggregate_budget_exhausted")
            assessment = "HYBRID-CAMPAIGN-" + case_id + "-" + str(uuid4())
            model = GroqHybridTransportModel()
            config = {"configurable": {"thread_id": assessment}}
            connect = connect_for_case(case_id)
            graph = build_original_graph(adapter, connect, saver)
            state = run_hybrid_evaluation(graph, config, adapter, connect, model,
                assessment_id=assessment, run_id=UUID(identities[case_id]["run_id"]),
                reservation_dir=reservation_directory, authorized=True)
            observed = capture_hybrid(state)
            if (observed["bundle_sha256"] != identities[case_id]["bundle_sha256"]
                    or observed["source_input_digest"] != identities[case_id][
                        "source_input_digest"] or observed["pending_send"]):
                raise CampaignStop("campaign_checkpoint_source_changed")
            # The sealed checkpoint holds raw attempts; journal keeps only the
            # bounded, model-blind projection. Never claim semantic correctness.
            stages = observed["attempt_stages"]
            output = sum(item["max_completion_tokens"] for item in state[
                "hybrid_execution"]["attempts"])
            if (len(stages) > remaining_requests or output > remaining_output):
                raise CampaignStop("aggregate_budget_exhausted")
            citations = observed["raw_citation_access"] or {}
            critical = (observed["candidate_status"] == "fixed_checked"
                and not observed["fixed_checked_candidate"]
                or case_id in ("N01", "R03") and bool(state.get("candidate_records"))
                or state["reviewer_package"].get("reviewer_action") !=
                    "Human review required; no approval, reservation or delivery promise")
            contained_error = observed["ai_error"] if (
                observed["ai_error"] in CONTAINED_MODEL_ERRORS
                and observed["audit_rejection_count"] > 0
                and state["reviewer_package"].get("audit_rejection_count", 0) >=
                    observed["audit_rejection_count"]
                and not state["candidate_records"]
                and state.get("review_status") == observed["original_review_status"]
                ) else None
            return CaseReceipt(case_id, assessment, len(stages), output,
                observed["tokens"]["prompt"] if observed["tokens"] else None,
                observed["tokens"]["completion"] if observed["tokens"] else None,
                observed["candidate_status"], observed["ai_execution"],
                observed["contribution_kind"], critical,
                citations.get("returned"), citations.get("submitted"),
                observed["latency_ms"], tuple(observed["audit_rejection_codes"]),
                contained_error)

        def assess_control(case_id):
            assessment = "HYBRID-CAMPAIGN-CONTROL-" + case_id + "-" + str(uuid4())
            config = {"configurable": {"thread_id": assessment}}
            graph = build_original_graph(adapter, connect_for_case(case_id), saver)
            state = graph.invoke(initial_state(assessment, UUID(identities[
                case_id]["run_id"])), config)
            selected, _ = eligible_line(state, adapter.validate_pinned_context(
                pinned_from_state(state)))
            if (selected is not None or state.get("candidate_records")
                    or state["context"]["bundle_sha256"] != identities[case_id]["bundle_sha256"]
                    or state["context"]["source_input_digest"] != identities[case_id][
                        "source_input_digest"]):
                raise CampaignStop("control_eligibility_or_source_changed")
            return CaseReceipt(case_id, assessment, 0, 0, None, None,
                               "not_started", "skipped", None)

        return run_campaign(reservation_directory, authorized=authorized,
            approved_digest=approved_digest, execute_case=execute_case,
            assess_control=assess_control)


def report_saved_campaign(*, journal_path: Path, checkpoint_database: str,
                          identities_path: Path, pinned_checkout: Path, fixture_database: str,
                          reference_database: str) -> dict:
    """Read-only reporting from saved checkpoints; never sends a model request."""
    st = journal_path.lstat()
    if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid()
            or stat.S_IMODE(st.st_mode) != 0o600 or st.st_nlink != 1
            or st.st_size > 65536):
        raise CampaignStop("campaign_report_journal_invalid")
    events = [json.loads(line) for line in journal_path.read_text().splitlines()]
    if (not events or events[0].get("event") != "start"
            or events[0].get("digest") != campaign_digest()):
        raise CampaignStop("campaign_report_identity_changed")
    complete = [item for item in events if item.get("event") == "case_completed"]
    if [item.get("case_id") for item in complete] != list(CASE_ORDER[:len(complete)]):
        raise CampaignStop("campaign_report_order_changed")
    identities = load_identities(identities_path)
    adapter = Phase1CAdapter(pinned_checkout)
    observations = []
    with thesis_checkpointer(checkpoint_database) as saver:
        for item in complete:
            case_id = item["case_id"]
            if case_id in CONTROLS:
                continue
            dsn = reference_database if case_id == "R03" else fixture_database
            graph = build_original_graph(adapter, lambda: psycopg.connect(dsn), saver)
            config = {"configurable": {"thread_id": item["assessment_id"]}}
            observed = capture_hybrid(graph.get_state(config).values)
            if (observed["attempted_model_requests"] != item["attempted_requests"]
                    or observed["ai_execution"] != item["ai_execution"]
                    or observed["candidate_status"] != item["candidate_status"]
                    or observed["bundle_sha256"] != identities[case_id]["bundle_sha256"]
                    or observed["source_input_digest"] != identities[case_id][
                        "source_input_digest"]):
                raise CampaignStop("campaign_report_checkpoint_changed")
            observations.append({"case_id": case_id, **observed})
    reserved_eligible = sum(item.get("event") == "case_reserved" and
                            item.get("case_id") in ELIGIBLE for item in events)
    return {"version": "hybrid-campaign-report-v1", "digest": campaign_digest(),
        "complete": events[-1].get("event") == "campaign_completed",
        "started_eligible_cases": reserved_eligible,
        "unreconciled_started_eligible_cases": reserved_eligible - len(observations),
        "stopped_case": (events[-1].get("case_id")
                         if events[-1].get("event") == "campaign_stopped" else None),
        "control_cases_checked": sum(item["case_id"] in CONTROLS for item in complete),
        "eligible": observations, "aggregate": summarize_hybrid(observations),
        "semantic_review": "not_scored_without_source_first_human_review"}
