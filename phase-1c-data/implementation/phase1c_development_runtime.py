"""Persist one real deterministic development replay, never an AI-agent claim.

The caller owns the transaction. A failed call must be rolled back by the caller;
the integration test uses a disposable transaction and never commits its rows.
"""

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from psycopg.types.json import Jsonb

from phase1c_deal_decision import assemble_deal_decision
from phase1c_reader import read_run
from validate_phase1c_runtime_outputs import validate_execution_rows


AGENTS = ("Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval")


def _json(value):
    return json.loads(json.dumps(value, default=lambda v: v.isoformat()
                           if isinstance(v, (date, datetime)) else str(v)
                           if isinstance(v, (Decimal, UUID)) else _unsupported(v)))


def _unsupported(value):
    raise TypeError(f"Non-JSON runtime value: {type(value).__name__}")


def _known_evidence(bundle):
    """IDs exposed by selected reader source rows, independent of output claims."""
    ids = {str(bundle["deal"]["deal_id"]), str(bundle["customer"]["customer_id"])}
    ids.update(str(line["deal_line_id"]) for line in bundle["lines"])
    ids.update(str(row["bom_id"]) for row in bundle["bom"])
    ids.update(str(row["compatibility_rule_id"]) for row in bundle["compatibility"])
    for table, key in (("inventory", "inventory_id"), ("inbound_supply", "supply_id"),
                       ("production_capacity", "capacity_id"),
                       ("digital_capacity", "digital_capacity_id")):
        ids.update(str(row[key]) for row in bundle[table])
    ids.update(str(row["purchase_order_id"]) for row in bundle["inbound_supply"]
               if row.get("purchase_order_id"))
    for table, key in (("pricing_rules", "pricing_rule_id"),
                       ("policy_rules", "policy_rule_id"),
                       ("approval_rules", "approval_rule_id")):
        ids.update(str(row[key]) for row in bundle["rules"][table])
    return ids


def _finding(code, message, refs, severity="info"):
    return {"code": code, "severity": severity, "message": message,
            "evidence_refs": sorted(set(map(str, refs)))}


def _outputs(bundle, decision):
    specialists = decision["specialists"]
    deal_id = bundle["deal"]["deal_id"]
    rows = {}
    configs = specialists["configuration"]
    rows["Configuration"] = {"status": "blocked" if any(x["status"] != "valid" for x in configs) else "supported",
        "findings": [_finding("CONFIG-" + x["status"].upper(), ", ".join(x["codes"]) or "Configured line checked",
                              [x["line_id"], *x["bom_ids"]], "blocker" if x["status"] != "valid" else "info") for x in configs]}
    pricing = specialists["pricing"]
    rows["Pricing"] = {"status": "unknown" if pricing["cost_evidence_gaps"] else "conditional",
        "findings": [_finding("PRICING-REVIEW", "Compiled pricing findings; human review remains required",
                              [deal_id, *(h["rule_id"] for h in pricing["rule_hits"])], "warning")]}
    availability = specialists["availability"]
    rows["Availability"] = {"status": "unknown" if any(x["status"] == "unknown" for x in availability) else
                            "infeasible" if any(x["status"] == "infeasible" for x in availability) else
                            "conditional" if any(x["status"] != "confirmed_by_date" for x in availability) else "supported",
        "findings": [_finding("SUPPLY-" + x["status"].upper(), "Reader fulfillment state: " + x["status"],
                              [x["line_id"], *x["source_ids"]], "warning" if x["status"] != "confirmed_by_date" else "info") for x in availability]}
    credit = specialists["credit"]
    rows["Credit"] = {"status": "conditional" if credit["commitments_fresh"] else "unknown",
        "findings": [_finding("CREDIT-REVIEW", "Compiled credit findings; human review remains required",
                              [bundle["customer"]["customer_id"], *(h["rule_id"] for h in credit["rule_hits"])], "warning")]}
    policy = specialists["policy"]
    rows["Policy"] = {"status": "blocked" if policy["hard_blocks"] else "conditional",
        "findings": [_finding("POLICY-BLOCK" if policy["hard_blocks"] else "POLICY-REVIEW",
                              "Compiled policy gate: " + ("hard block" if policy["hard_blocks"] else "review"),
                              [deal_id, *(h["rule_id"] for h in policy["rule_hits"])],
                              "blocker" if policy["hard_blocks"] else "warning")]}
    route = specialists["approval_routing"]
    rows["Approval"] = {"status": "blocked" if decision["status"] == "blocked" else "conditional" if not route["route_withheld"] else "unknown",
        "findings": [_finding("ROUTE-WITHHELD" if route["route_withheld"] else "ROUTE-REVIEW",
                              "Route withheld" if route["route_withheld"] else "Review roles identified; no approval recorded",
                              [deal_id], "warning")]}
    rows["Orchestrator"] = {"status": {"blocked": "blocked", "needs_revision": "infeasible",
        "needs_evidence": "unknown", "needs_commitment": "conditional",
        "approval_required": "conditional"}[decision["status"]],
        "findings": [_finding("GATE-" + decision["status"].upper(),
                              "Deterministic gate: " + decision["status"] + "; no approval or reservation recorded",
                              [deal_id], "blocker" if decision["status"] == "blocked" else "warning")]}
    return {name: {"agent_name": name, **content, "engine": "deterministic_development"}
            for name, content in rows.items()}


def execute_development_run(conn, run_id, contract):
    """Write six responsibility summaries and a gate for a queued/running run.

    The frozen run must already exist. This function owns no commit and provides
    no retry or booking side effect. A second execution fails before writing.
    """
    started_at = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("SELECT run_id, run_status FROM deal_desk.deal_runs WHERE run_id = %s FOR UPDATE", (run_id,))
        row = cur.fetchone()
        status = row["run_status"] if isinstance(row, dict) else row[1] if row else None
        if status not in ("queued", "running"):
            raise ValueError("Run must exist in queued/running state")
        cur.execute("SELECT count(*) FROM deal_desk.agent_execution_log WHERE run_id = %s", (run_id,))
        count = cur.fetchone()
        if (count["count"] if isinstance(count, dict) else count[0]):
            raise ValueError("Run already has execution attempts; retry needs a separate design")
    bundle = read_run(conn, run_id, commercial_rule_mode="compiled")
    decision = assemble_deal_decision(bundle)
    run = bundle["run"]
    if str(run["run_id"]) != str(run_id) or decision["deal_id"] != run["deal_id"]:
        raise ValueError("Reader and run identity differ")
    snapshot = {"run_id": str(run_id), "deal_id": run["deal_id"],
                "as_of_at": run["as_of_at"].isoformat(), "data_snapshot_ref": run["data_snapshot_ref"],
                "config_hash": run["config_hash"], "policy_set_code": run["applied_policy_set_code"],
                "catalog_version": run["catalog_version_used"]}
    outputs = _outputs(bundle, decision)
    rows = [{"run_id": str(run_id), "agent_name": name, "attempt_number": 1,
             "status": "Success", "input_snapshot_json": snapshot, "output_json": outputs[name]}
            for name in (*AGENTS, "Orchestrator")]
    report = validate_execution_rows(rows, contract, known_evidence=_known_evidence(bundle))
    if report["errors"]:
        raise ValueError("Invalid runtime output: " + "; ".join(report["errors"]))
    completed_at = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute("UPDATE deal_desk.deal_runs SET run_status = 'running' WHERE run_id = %s", (run_id,))
        for item in rows:
            cur.execute("""INSERT INTO deal_desk.agent_execution_log
                (run_id, deal_id, agent_name, attempt_number, started_at, completed_at,
                 status, input_snapshot_json, output_json,
                 applied_policy_set_code, catalog_version_used)
                VALUES (%s,%s,%s,1,%s,%s,'Success',%s,%s,%s,%s)""",
                (run_id, run["deal_id"], item["agent_name"], started_at, completed_at,
                 Jsonb(snapshot), Jsonb(_json(item["output_json"])),
                 run["applied_policy_set_code"], run["catalog_version_used"]))
        cur.execute("UPDATE deal_desk.deal_runs SET run_status = 'completed', completed_at = clock_timestamp() WHERE run_id = %s", (run_id,))
    return {"run_id": str(run_id), "decision_status": decision["status"], "rows": len(rows),
            "engine": "deterministic_development", "accepted_evaluation_answers": 0}
