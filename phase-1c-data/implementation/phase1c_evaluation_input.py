"""Prepare an input-only review packet from a frozen PostgreSQL reader view.

This does not score, reveal an oracle, or certify a held-out evaluation case.
The caller must store reviewer answers separately and obtain independent review.
"""

from hashlib import sha256
import json

from phase1c_candidate import INPUT_TABLES, reader_input_digest


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


OPERATIONAL_SOURCE_ID_COLUMNS = {
    "inventory": "inventory_id",
    "inbound_supply": "supply_id",
    "production_capacity": "capacity_id",
    "digital_capacity": "digital_capacity_id",
}


def prepare_review_input(bundle, *, case_id, excluded_deal_ids=(), excluded_source_ids=()):
    """Copy selected source rows only, and seal them for later reviewer comparison."""
    if not case_id.startswith("EVAL-PREP-"):
        raise ValueError("Evaluation preparation needs a distinct case ID")
    if bundle.get("candidate_trace") or bundle["deal"]["deal_id"] in excluded_deal_ids:
        raise ValueError("Candidate output or development submission cannot enter review input")
    source_ids = {str(row[column]) for table, column in OPERATIONAL_SOURCE_ID_COLUMNS.items()
                  for row in bundle[table]}
    if source_ids & set(excluded_source_ids):
        raise ValueError("Review case reuses development operational evidence")
    source = {key: bundle[key] for key in INPUT_TABLES}
    context = {key: bundle["run"][key] for key in
               ("run_id", "deal_id", "as_of_at", "catalog_version_used",
                "applied_policy_set_code", "data_snapshot_ref", "config_hash")}
    # Round-trip to a JSON value: the returned packet shares no mutable rows
    # with the reader, and dates/decimals have a stable textual representation.
    payload = json.loads(_canonical({"case_id": case_id, "run_context": context,
                                     "source_rows": source,
                                     "source_input_digest": reader_input_digest(bundle)}))
    return {"payload": payload, "sha256": sha256(_canonical(payload).encode()).hexdigest()}


def verify_review_input(packet, *, expected_case_id, expected_source_digest):
    if (packet.get("payload", {}).get("case_id") != expected_case_id or
            packet["payload"].get("source_input_digest") != expected_source_digest or
            set(packet["payload"]) != {"case_id", "run_context", "source_rows",
                                       "source_input_digest"} or
            set(packet["payload"]["source_rows"]) != set(INPUT_TABLES) or
            packet.get("sha256") != sha256(_canonical(packet["payload"]).encode()).hexdigest()):
        raise ValueError("Review input identity, source set or seal differs")
    return True
