"""Explicit fresh-case Groq free-tier development CLI (never imported by CI).

Run with --cluster-dsn on the isolated /tmp/opencode PostgreSQL test cluster.
One invocation provisions a new business DB and a dedicated checkpoint DB,
pins a synthetic case, writes its private manifest audit, and sends at most
the manifest's request budget. No retry or fallback on any uncertain send.
"""

import argparse
import json
import os
from pathlib import Path
import tempfile
from hashlib import sha256
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.groq_development import build_manifest, record_manifest
from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.groq_error_diagnostic import safe_fields
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.investigation_graph import run_original_investigate_and_review
from dealdesk_phase2.local_env import with_local_groq_key
from dealdesk_phase2.live_models import LiveInvestigationModel, GROQ_MODEL
from dealdesk_phase2.m21_groq_contract import GroqM21Model
from dealdesk_phase2.m21_specialists import TOOLS as M21_TOOLS, run_m21_evaluation
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from dealdesk_phase2.typed_final_hosted import DEV_ENABLE_ENV, run_groq_development
from dealdesk_phase2.typed_final_hosted import _database_identity
from m18_case_setup import CASES
from run_week4_disposable import provision_and_run, require_disposable_cluster


def _m21_campaign(graph, config, adapter, *, case_id, owner, root, key,
                  policy_routing_only=False, typed_credit=False,
                  manifest_path=None):
    """Full campaign or isolated Policy → Routing development investigation."""
    template = (Path(__file__).resolve().parents[2] / "evaluation" /
        "week3-hosted-validation-proposal.json")
    manifest = json.loads(template.read_text())
    pinned = pinned_from_state(graph.get_state(config).values)
    adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    with graph.phase2_connection_factory() as connection:
        business_name, business_oid = connection.execute(
            "SELECT current_database(), oid FROM pg_database WHERE datname=current_database()"
            ).fetchone()
    checkpoint_row = graph.checkpointer.conn.execute(
        "SELECT current_database(), oid FROM pg_database WHERE datname=current_database()"
        ).fetchone()
    manifest.update(status="standing_development" if (policy_routing_only or
        typed_credit) else
        "authorized_one_case", version="m21-policy-route-standing-dev-v1" if
        policy_routing_only else "m21-credit-terminal-standing-dev-v1" if
        typed_credit else manifest["version"],
        **({"order": ["policy", "approval_routing"],
            "allowed_tools": {name: M21_TOOLS[name] for name in (
                "policy", "approval_routing")}, "maximum_posts_total": 4,
            "maximum_posts_per_case": 4} if policy_routing_only else
           {"maximum_posts_total": 6,
            **({"maximum_completion_tokens_per_post": 1024} if typed_credit else {})}),
        cases=[{"case_id": case_id, "assessment_id": ctx.assessment_id,
            "run_id": str(ctx.phase1c_run_id), "bundle_sha256": ctx.bundle_sha256,
            "source_input_digest": ctx.source_input_digest,
            "as_of_at": ctx.as_of_at.isoformat(),
            "data_snapshot_ref": ctx.data_snapshot_ref}],
        execution_context={"fixture_database": business_name,
            "checkpoint_database": checkpoint_row["current_database"],
            "owner_directory": str(owner), "fresh_databases_required": True})
    _database_identity(graph, {"execution_context": {
        **manifest["execution_context"], "fixture_database_oid": business_oid,
        "checkpoint_database_oid": checkpoint_row["oid"]},
        "case": {"assessment_id": ctx.assessment_id}}, exclusive=True)
    digest = sha256(_canonical(manifest).encode()).hexdigest()
    for path, value in ((manifest_path or root / "manifest.json", manifest),
                        (owner / "m21-approved-manifest.json", {
                            "assessment_id": ctx.assessment_id,
                            "approved_manifest_sha256": digest,
                            "credential_env_selection": "GROQ_SECONDARY_API_KEY",
                            "billing_disabled_confirmed": True})):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as output:
            output.write(_canonical(value) + "\n")
            output.flush()
            os.fsync(output.fileno())
    os.environ["GROQ_SECONDARY_API_KEY"] = key
    try:
        state = run_m21_evaluation(graph, config, adapter,
            {name: GroqM21Model(name) for name in M21_TOOLS}, manifest=manifest,
            approved_manifest_sha256=digest, authorized=True, owner_dir=owner,
            free_tier_billing_disabled=True,
            development_selection=("policy", "approval_routing") if
                policy_routing_only else tuple(M21_TOOLS) if typed_credit else None)
    finally:
        os.environ.pop("GROQ_SECONDARY_API_KEY", None)
    return digest, state


def _six_campaign(graph, config, adapter, *, case_id, account_id, root, key, run_id):
    """Sequential original-checkpoint LangGraph continuations, stopping on any error."""
    typed_owner = root / "typed-owner"
    typed_owner.mkdir(mode=0o700)
    manifest, digest = build_manifest(graph, config, adapter, case_id=case_id,
        specialist="pricing", plan=1, account_id=account_id, owner_dir=typed_owner)
    path = root / "typed-manifest.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write(_canonical(manifest) + "\n")
        output.flush()
        os.fsync(output.fileno())
    record_manifest(typed_owner, manifest, digest)
    os.environ["GROQ_SECONDARY_API_KEY"] = key
    try:
        run_groq_development(graph, config, adapter, manifest=manifest,
            manifest_sha256=digest, specialist="pricing", owner_dir=typed_owner)
    finally:
        os.environ.pop("GROQ_SECONDARY_API_KEY", None)
    state = graph.get_state(config).values
    if (state.get("m20_ai_results", {}).get("configuration", {}).get("execution") !=
            "completed" or state.get("typed_final_results", {}).get("pricing", {}).get(
            "execution") != "completed"):
        return "configuration_or_pricing_incomplete"
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    fulfillment_manifest = {"version": "groq-fulfillment-standing-dev-v1",
        "status": "standing_development", "provider": "groq", "model": GROQ_MODEL,
        "assessment_id": pinned.context.assessment_id, "case_id": case_id,
        "bundle_sha256": pinned.context.bundle_sha256,
        "source_input_digest": pinned.context.source_input_digest,
        "decision_completion_tokens": 2048, "maximum_final_completion_tokens": 2048}
    fd = os.open(root / "fulfillment-manifest.json", os.O_WRONLY | os.O_CREAT |
                 os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write(_canonical(fulfillment_manifest) + "\n")
        output.flush()
        os.fsync(output.fileno())
    os.environ["GROQ_API_KEY"] = key
    try:
        model = LiveInvestigationModel(graph, config, pace_seconds=12,
            enable_binding_proposals=True, decision_completion_tokens=2048)
        run_original_investigate_and_review(graph, config, adapter, model,
            assessment_id=pinned.context.assessment_id, run_id=run_id)
    finally:
        os.environ.pop("GROQ_API_KEY", None)
    state = graph.get_state(config).values
    if (state.get("ai_fulfillment_result", {}).get("execution") != "completed" or
            state.get("candidate_status") != "not_started"):
        return "fulfillment_incomplete_or_candidate_requires_separate_review"
    owner = root / "owner"
    owner.mkdir(mode=0o700)
    _m21_campaign(graph, config, adapter, case_id=case_id, owner=owner,
        root=root, key=key, typed_credit=True,
        manifest_path=root / "m21-manifest.json")
    return "six_stages_completed"


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cluster-dsn", required=True)
    cli.add_argument("--phase1c", type=Path, required=True)
    cli.add_argument("--pg-bin", type=Path, required=True)
    cli.add_argument("--pg-lib", type=Path, required=True)
    cli.add_argument("--account-id", required=True)
    cli.add_argument("--specialist", choices=("pricing", "credit", "fulfillment",
                                          "m21_campaign", "policy_routing",
                                          "full_typed_credit", "six_campaign"),
                     default="pricing")
    cli.add_argument("--case", choices=("B01", "B05", "N03"), default="B05")
    args = cli.parse_args()
    if os.environ.get(DEV_ENABLE_ENV) != "1":
        raise ValueError("groq_development_opt_in_required")
    if args.specialist == "credit" and args.case != "B05":
        raise ValueError("groq_development_credit_case_not_prepared")
    if args.specialist in ("fulfillment", "six_campaign") and args.case not in (
            "B01", "B05"):
        raise ValueError("groq_development_fulfillment_case_not_prepared")
    require_disposable_cluster(args.cluster_dsn)
    # Credential preflight happens before provisioning and is never logged.
    key = with_local_groq_key({}, credential="secondary")["GROQ_API_KEY"]
    root = Path(tempfile.mkdtemp(prefix="dealdesk-groq-dev-", dir="/tmp/opencode"))
    root.chmod(0o700)
    result = {"assessment": None, "specialist": args.specialist, "case": args.case,
              "invoked": False, "error_class": None}
    try:
        fixture = provision_and_run(args.cluster_dsn, args.phase1c,
            root / "fixture.json", root / "fixture.md", args.pg_bin, args.pg_lib,
            root / "demo.json", root / "demo.md")["disposable_setup"]
        admin = conninfo_to_dict(args.cluster_dsn)
        checkpoint_name = "groq_dev_checkpoint_" + uuid4().hex[:16]
        with psycopg.connect(args.cluster_dsn, autocommit=True) as connection:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(checkpoint_name)))
        params = {k: v for k, v in admin.items() if k != "dbname"}
        business_dsn = make_conninfo(**params, dbname=fixture["business_database"])
        checkpoint_dsn = make_conninfo(**params, dbname=checkpoint_name)
        owner = root / "owner"
        owner.mkdir(mode=0o700)
        case = next(x for x in CASES if x.case_id == args.case)
        assessment = "GROQ-DEV-" + uuid4().hex
        result["assessment"] = assessment
        result["business_database"] = fixture["business_database"]
        result["checkpoint_database"] = checkpoint_name
        config = {"configurable": {"thread_id": assessment}}
        adapter = Phase1CAdapter(args.phase1c.resolve())
        os.environ["LANGGRAPH_STRICT_MSGPACK"] = "true"
        with thesis_checkpointer(checkpoint_dsn) as saver:
            graph = build_original_graph(adapter, lambda: psycopg.connect(business_dsn), saver)
            original = graph.invoke(initial_state(assessment, case.run_id), config)
            if args.specialist == "six_campaign":
                result["invoked"] = True
                result["fixed_review_status"] = original["review_status"]
                try:
                    result["campaign_status"] = _six_campaign(graph, config, adapter,
                        case_id=args.case, account_id=args.account_id, root=root,
                        key=key, run_id=case.run_id)
                except Exception as exc:
                    result["error_class"] = type(exc).__name__
                    result["campaign_status"] = "terminal_failure"
                finally:
                    key = None
                state = graph.get_state(config).values
                result["six_specialists"] = {
                    "configuration": state.get("m20_ai_results", {}).get("configuration", {}).get("execution"),
                    "pricing": state.get("typed_final_results", {}).get("pricing", {}).get("execution"),
                    "fulfillment": state.get("ai_fulfillment_result", {}).get("execution"),
                    **{name: state.get("m21_ai_results", {}).get(name, {}).get("execution")
                       for name in M21_TOOLS}}
                result["stage_errors"] = {name: {k: row.get(k) for k in (
                    "reason", "model_output_category")} for name, row in (
                    ("configuration", state.get("m20_ai_results", {}).get("configuration", {})),
                    ("pricing", state.get("typed_final_results", {}).get("pricing", {})),
                    *((name, state.get("m21_ai_results", {}).get(name, {}))
                      for name in M21_TOOLS)) if row.get("execution") == "error"}
                result["candidate_status"] = state.get("candidate_status")
                result["m21_review_present"] = bool(state.get("m21_review"))
                result["completed_evidence_refs"] = [row.get("returned_refs", [])
                    for row in state.get("tool_access_ledger", []) if row.get("status") == "completed"]
            elif args.specialist == "fulfillment":
                pinned = pinned_from_state(original)
                adapter.validate_pinned_context(pinned)
                manifest = {"version": "groq-fulfillment-standing-dev-v1",
                    "status": "standing_development", "provider": "groq", "model": GROQ_MODEL,
                    "assessment_id": assessment, "case_id": args.case,
                    "bundle_sha256": pinned.context.bundle_sha256,
                    "source_input_digest": pinned.context.source_input_digest,
                    "business_database": fixture["business_database"],
                    "checkpoint_database": checkpoint_name,
                    "completion_cap_per_decision": 1024, "completion_cap_per_final": 2048,
                    "maximum_model_turns": 6}
                digest = sha256(_canonical(manifest).encode()).hexdigest()
                manifest_fd = os.open(root / "manifest.json", os.O_WRONLY | os.O_CREAT |
                    os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(manifest_fd, "w") as output:
                    output.write(_canonical(manifest) + "\n")
                    output.flush()
                    os.fsync(output.fileno())
                result["manifest_sha256"] = digest
                result["fixed_review_status"] = original["review_status"]
                os.environ["GROQ_API_KEY"] = key
                result["invoked"] = True
                try:
                    model = LiveInvestigationModel(graph, config, pace_seconds=12,
                                                   enable_binding_proposals=True)
                    run_original_investigate_and_review(graph, config, adapter, model,
                        assessment_id=assessment, run_id=case.run_id)
                except Exception as exc:
                    result["error_class"] = type(exc).__name__
                finally:
                    os.environ.pop("GROQ_API_KEY", None)
                    key = None
                state = graph.get_state(config).values
                contribution = state.get("ai_fulfillment_result") or {}
                result["fulfillment"] = {"execution": contribution.get("execution"),
                    "error_category": (contribution.get("error") if
                        contribution.get("error") in ("model_turn_budget_exhausted",
                            "budget_exhausted", "malformed_contribution",
                            "revision_failed", "correction_outcome_uncertain") else
                        "other" if contribution.get("error") else None),
                    "contribution_kind": (contribution.get("contribution", {}).get("kind")
                        if contribution.get("contribution", {}).get("kind") in (
                            "abstention", "finding_without_proposal", "binding_proposal")
                        else None),
                    "tool_calls": len([row for row in state.get("tool_access_ledger", [])
                                       if row.get("status") == "completed"]),
                    "candidate_status": state.get("candidate_status"),
                    "model_attempts": [{k: row.get(k) for k in ("status", "error_code",
                        "usage", "prompt_version")} for row in state.get(
                            "model_attempt_ledger", [])]}
                result["completed_evidence_refs"] = [row.get("returned_refs", [])
                    for row in state.get("tool_access_ledger", [])
                    if row.get("status") == "completed"]
            elif args.specialist in ("m21_campaign", "policy_routing",
                                     "full_typed_credit"):
                result["invoked"] = True
                result["fixed_review_status"] = original["review_status"]
                try:
                    digest, state = _m21_campaign(graph, config, adapter,
                        case_id=args.case, owner=owner,
                        root=root, key=key,
                        policy_routing_only=args.specialist == "policy_routing",
                        typed_credit=args.specialist == "full_typed_credit")
                    result["manifest_sha256"] = digest
                except Exception as exc:
                    result["error_class"] = type(exc).__name__
                    state = graph.get_state(config).values
                finally:
                    key = None
                result["m21_results"] = {name: {k: row.get(k) for k in (
                    "execution", "reason", "model_output_category", "validated_claims",
                    "tool_calls")} for name, row in state.get("m21_ai_results", {}).items()}
                result["m21_attempts"] = [{k: row.get(k) for k in (
                    "specialist", "ordinal", "status", "action_kind", "usage")}
                    for row in state.get("m21_model_attempts", [])]
                result["completed_evidence_refs"] = [row.get("returned_refs", [])
                    for row in state.get("tool_access_ledger", [])
                    if row.get("status") == "completed"]
            else:
                manifest, digest = build_manifest(graph, config, adapter, case_id=args.case,
                    specialist=args.specialist, plan=1, account_id=args.account_id,
                    owner_dir=owner)
                manifest_fd = os.open(root / "manifest.json", os.O_WRONLY | os.O_CREAT |
                    os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(manifest_fd, "w") as output:
                    output.write(_canonical(manifest) + "\n")
                    output.flush()
                    os.fsync(output.fileno())
                record_manifest(owner, manifest, digest)
                result["manifest_sha256"] = digest
                result["fixed_review_status"] = original["review_status"]
                # The key only enters the child process for the explicitly gated send.
                os.environ.pop("GROQ_API_KEY", None)
                os.environ["GROQ_SECONDARY_API_KEY"] = key
                result["invoked"] = True
                try:
                    run_groq_development(graph, config, adapter, manifest=manifest,
                        manifest_sha256=digest, specialist=args.specialist, owner_dir=owner)
                except Exception as exc:
                    result["error_class"] = type(exc).__name__
                finally:
                    os.environ.pop("GROQ_SECONDARY_API_KEY", None)
                    key = None
                state = graph.get_state(config).values
                result["configuration"] = {k: state.get("m20_ai_results", {}).get(
                    "configuration", {}).get(k) for k in ("execution", "reason",
                        "model_output_category", "validated_claims", "tool_calls")}
                result["typed_final"] = {k: state.get("typed_final_results", {}).get(
                    args.specialist, {}).get(k) for k in ("execution", "reason",
                        "model_output_category", "validated_claims", "tool_calls")}
                result["configuration_attempts"] = [{k: row.get(k) for k in (
                    "ordinal", "status", "action_kind", "usage")}
                    for row in state.get("m20_model_attempts", [])]
                result["typed_attempts"] = [{k: row.get(k) for k in (
                    "stage", "ordinal", "status", "action_kind", "usage")}
                    for row in state.get("typed_final_attempts", [])]
                result["completed_evidence_refs"] = [row.get("returned_refs", [])
                    for row in state.get("tool_access_ledger", []) if row.get("status") == "completed"]
                result["failed_receipts"] = []
                for receipt in owner.glob("*.hybrid.audit.jsonl"):
                    if receipt.stat().st_size > 4096:
                        continue
                    for line in receipt.read_text().splitlines():
                        event = json.loads(line)
                        if event.get("event") == "failed":
                            result["failed_receipts"].append({"stage": event.get("stage"),
                                "code": event.get("code") if event.get("code") in (
                                    "http_400", "http_429", "http_403", "http_401") else
                                    "other_failure", "diagnostic": safe_fields({
                                    **{"type": "unknown", "code": "unknown",
                                       "param": "unknown", "request_id": None},
                                    **(event.get("diagnostic") or {})})})
    except Exception as exc:
        result["error_class"] = type(exc).__name__
    finally:
        os.environ.pop("GROQ_SECONDARY_API_KEY", None)
        report = root / "sanitized-result.json"
        fd = os.open(report, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as output:
            output.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
            output.flush()
            os.fsync(output.fileno())
        print(json.dumps({"private_directory": str(root), **result}, sort_keys=True))
    return 0 if result["invoked"] and result["error_class"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
