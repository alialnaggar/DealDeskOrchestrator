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


def operational_source_ids(bundle):
    """IDs of dated operational rows actually selected by this reader run."""
    return {table: {str(row[column]) for row in bundle[table]}
            for table, column in OPERATIONAL_SOURCE_ID_COLUMNS.items()}


def build_development_exclusion_manifest(bundles):
    """Seal all selected development IDs; no decisions or answer fields enter."""
    ids = {table: set() for table in OPERATIONAL_SOURCE_ID_COLUMNS}
    runs = set()
    deals = set()
    for bundle in bundles:
        run_id = str(bundle["run"]["run_id"])
        deal_id = str(bundle["deal"]["deal_id"])
        if run_id in runs:
            raise ValueError("Duplicate development run in exclusion manifest")
        runs.add(run_id)
        deals.add(deal_id)
        for table, selected in operational_source_ids(bundle).items():
            ids[table].update(selected)
    if not runs:
        raise ValueError("Development exclusion manifest is empty")
    payload = {
        "schema_version": 1,
        "status": "development_reader_selected_sources_not_evaluation_answers",
        "run_count": len(runs),
        "deal_count": len(deals),
        "run_ids": sorted(runs),
        "deal_ids": sorted(deals),
        "source_ids_by_table": {table: sorted(values) for table, values in ids.items()},
    }
    return {"payload": payload, "sha256": sha256(_canonical(payload).encode()).hexdigest()}


def build_historical_exclusion_manifest(bundles):
    """Seal the 400 dated historical reads without their diagnostic decisions."""
    manifest = build_development_exclusion_manifest(bundles)
    manifest["payload"]["status"] = "historical_reader_selected_sources_not_evaluation_answers"
    manifest["sha256"] = sha256(_canonical(manifest["payload"]).encode()).hexdigest()
    return manifest


def excluded_ids_from_manifest(manifest, *, expected_run_count, expected_deal_count=None,
                               expected_status="development_reader_selected_sources_not_evaluation_answers"):
    """Verify a pinned development registry before passing IDs to preparation."""
    payload = manifest.get("payload")
    if (not isinstance(payload, dict)
            or set(payload) != {"schema_version", "status", "run_count",
                                "deal_count", "run_ids", "deal_ids",
                                "source_ids_by_table"}
            or payload["schema_version"] != 1
            or payload["status"] != expected_status
            or payload["run_count"] != expected_run_count
            or not isinstance(payload["deal_count"], int)
            or not 0 < payload["deal_count"] <= expected_run_count
            or (expected_deal_count is not None and
                payload["deal_count"] != expected_deal_count)
            or not isinstance(payload["run_ids"], list)
            or any(not isinstance(value, str) or not value for value in payload["run_ids"])
            or payload["run_ids"] != sorted(set(payload["run_ids"]))
            or len(payload["run_ids"]) != expected_run_count
            or not isinstance(payload["deal_ids"], list)
            or any(not isinstance(value, str) or not value for value in payload["deal_ids"])
            or payload["deal_ids"] != sorted(set(payload["deal_ids"]))
            or len(payload["deal_ids"]) != payload["deal_count"]
            or not isinstance(payload["source_ids_by_table"], dict)
            or set(payload["source_ids_by_table"]) != set(OPERATIONAL_SOURCE_ID_COLUMNS)
            or manifest.get("sha256") != sha256(_canonical(payload).encode()).hexdigest()):
        raise ValueError("Development exclusion manifest identity or seal differs")
    for values in payload["source_ids_by_table"].values():
        if (not isinstance(values, list) or
                any(not isinstance(value, str) or not value for value in values) or
                values != sorted(set(values))):
            raise ValueError("Development exclusion manifest source IDs are invalid")
    return {value for values in payload["source_ids_by_table"].values() for value in values}


def prepare_review_input(bundle, *, case_id, excluded_deal_ids=(), excluded_source_ids=()):
    """Copy selected source rows only, and seal them for later reviewer comparison."""
    if not case_id.startswith("EVAL-PREP-"):
        raise ValueError("Evaluation preparation needs a distinct case ID")
    if bundle.get("candidate_trace") or bundle["deal"]["deal_id"] in excluded_deal_ids:
        raise ValueError("Candidate output or development submission cannot enter review input")
    source_ids = set().union(*operational_source_ids(bundle).values())
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


def prepare_heldout_review_input(bundle, *, case_id, development_manifest,
                                 historical_manifest):
    """Require both pinned source registries for a future held-out input."""
    if not isinstance(development_manifest, dict) or not isinstance(historical_manifest, dict):
        raise ValueError("Held-out preparation requires development and historical exclusion manifests")
    excluded_sources = excluded_ids_from_manifest(
        development_manifest, expected_run_count=154, expected_deal_count=152)
    payload = development_manifest["payload"]
    historical_sources = excluded_ids_from_manifest(
        historical_manifest, expected_run_count=400, expected_deal_count=400,
        expected_status="historical_reader_selected_sources_not_evaluation_answers")
    historical = historical_manifest["payload"]
    run_id = str(bundle["run"]["run_id"])
    if run_id in payload["run_ids"]:
        raise ValueError("Review run reuses a development run")
    if run_id in historical["run_ids"]:
        raise ValueError("Review run reuses a historical run")
    return prepare_review_input(
        bundle, case_id=case_id,
        excluded_deal_ids=set(payload["deal_ids"]) | set(historical["deal_ids"]),
        excluded_source_ids=excluded_sources | historical_sources)


def verify_review_input(packet, *, expected_case_id, expected_source_digest):
    if (packet.get("payload", {}).get("case_id") != expected_case_id or
            packet["payload"].get("source_input_digest") != expected_source_digest or
            set(packet["payload"]) != {"case_id", "run_context", "source_rows",
                                       "source_input_digest"} or
            set(packet["payload"]["source_rows"]) != set(INPUT_TABLES) or
            packet.get("sha256") != sha256(_canonical(packet["payload"]).encode()).hexdigest()):
        raise ValueError("Review input identity, source set or seal differs")
    return True

