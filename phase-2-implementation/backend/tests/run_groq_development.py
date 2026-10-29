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
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.groq_development import build_manifest, record_manifest
from dealdesk_phase2.groq_error_diagnostic import safe_fields
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.local_env import with_local_groq_key
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter
from dealdesk_phase2.typed_final_hosted import DEV_ENABLE_ENV, run_groq_development
from m18_case_setup import CASES
from run_week4_disposable import provision_and_run, require_disposable_cluster


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cluster-dsn", required=True)
    cli.add_argument("--phase1c", type=Path, required=True)
    cli.add_argument("--pg-bin", type=Path, required=True)
    cli.add_argument("--pg-lib", type=Path, required=True)
    cli.add_argument("--account-id", required=True)
    cli.add_argument("--specialist", choices=("pricing", "credit"), default="pricing")
    cli.add_argument("--case", choices=("B01", "B05", "N03"), default="B05")
    args = cli.parse_args()
    if os.environ.get(DEV_ENABLE_ENV) != "1":
        raise ValueError("groq_development_opt_in_required")
    if args.specialist == "credit" and args.case != "B05":
        raise ValueError("groq_development_credit_case_not_prepared")
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
