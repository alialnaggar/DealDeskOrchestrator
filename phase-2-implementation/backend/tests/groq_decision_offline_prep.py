"""Offline-only fresh synthetic decision wire; never calls a provider.

Run against a *new* disposable PostgreSQL business DB with pinned Phase 1C
fixtures/rules and a distinct empty checkpoint DB. No campaign or B01 API.
"""

from hashlib import sha256
from copy import deepcopy
import json
import os
from pathlib import Path
import stat

import psycopg

from dealdesk_phase2.checkpoint import thesis_checkpointer
from dealdesk_phase2.fulfillment_agent import eligible_line
from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.hybrid_contracts import HybridContractError
from dealdesk_phase2.hybrid_pack import _canonical, prepare_pack
from dealdesk_phase2.hybrid_provider import GroqHybridTransportModel
from dealdesk_phase2.live_models import TOOL_PARAMETERS, _json
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter, PHASE1C_COMMIT
from m18_case_setup import SourceCase, install_disposable_cases


CASE = SourceCase("B06", 12, "2026-09-05", 12, 6, 11, 2, "2026-09-09", 1)
ASSESSMENT = "GROQ-DECISION-B06-9a480223-3fd5-4f85-97eb-0ad390f842b1"
POLICY = "hybrid-groq-evaluation-v1"
MAX_REQUEST_BYTES = 8192
EXPECTED_TOOLS = ("inspect_line_supply", "inspect_fulfillment_paths",
                  "inspect_evidence_record", "submit_finding", "abstain")
EXPOSED_FIELDS = frozenset(("line_id", "requested_quantity", "requested_delivery_date",
                            "quantity_by_requested_date", "fixed_fulfillment_status",
                            "allow_partial_delivery", "destination_country_code",
                            "destination_region"))


def _strict_wire(body, input, pack):
    """Check actual production serialization, not a reimplemented request."""
    if (set(body) != {"model", "temperature", "max_completion_tokens", "tools",
                      "tool_choice", "parallel_tool_calls", "messages"}
            or body["model"] != "openai/gpt-oss-120b" or body["temperature"] != 0
            or body["max_completion_tokens"] != 512
            or body["tool_choice"] != "required" or body["parallel_tool_calls"] is not False
            or [x["function"]["name"] for x in body["tools"]] != list(EXPECTED_TOOLS)
            or len(body["messages"]) != 2
            or [x["role"] for x in body["messages"]] != ["system", "user"]
            or any(set(x) != {"role", "content"} or not isinstance(x["content"], str)
                   for x in body["messages"])):
        raise HybridContractError("decision_wire_unexpected")
    for tool in body["tools"]:
        if set(tool) != {"type", "function"} or tool["type"] != "function":
            raise HybridContractError("decision_tool_unexpected")
        function = tool["function"]
        if (set(function) != {"name", "description", "parameters"}
                or not isinstance(function["description"], str)):
            raise HybridContractError("decision_tool_unexpected")
        schema = function["parameters"]
        if (set(schema) != {"type", "properties", "required", "additionalProperties"}
                or schema["type"] != "object" or schema["additionalProperties"] is not False
                or len(schema["required"]) != len(set(schema["required"]))
                or not set(schema["required"]).issubset(schema["properties"])):
            raise HybridContractError("decision_tool_schema_unexpected")
        if function["name"] in input.permitted_tools:
            expected = deepcopy(TOOL_PARAMETERS[function["name"]])
            expected["properties"]["purpose_code"] = {"type": "string", "enum": [
                "check_dated_path", "inspect_source", "check_line_supply"]}
            expected["required"].append("purpose_code")
            expected["additionalProperties"] = False
            if ("purpose_code" not in schema["required"]
                    or schema != expected):
                raise HybridContractError("decision_tool_schema_unexpected")
        elif schema["properties"] or schema["required"]:
            raise HybridContractError("decision_tool_schema_unexpected")
    data = json.loads(body["messages"][1]["content"])
    if (set(pack["model_input"]) != EXPOSED_FIELDS
            or pack["observation"].get("tool") != "inspect_line_supply"
            or pack["observation"].get("execution") != "completed"):
        raise HybridContractError("decision_source_unexpected")
    expected_input = {**pack["model_input"], "permitted_tools": list(input.permitted_tools)}
    if (set(data) != {"input", "observations"} or data["input"] != expected_input
            or data["observations"] != [pack["observation"]]
            or data["input"]["line_id"] != input.line_id
            or any(x in body for x in ("response_format", "reasoning_format", "reasoning_effort"))):
        raise HybridContractError("decision_source_unexpected")
    raw = _canonical(body).encode("utf-8")
    if any(marker in raw for marker in (b"source_reviewed_answer", b"expected_answer",
                                       b"M18-L-B01", b"M18-D-B01", b"GROQ_API_KEY")):
        raise HybridContractError("decision_source_unexpected")
    if len(raw) > MAX_REQUEST_BYTES or raw != _json(body).encode("utf-8"):
        raise HybridContractError("decision_wire_oversize")
    return raw


def prepare(*, fixture_dsn, checkpoint_dsn, checkout: Path):
    """Create just B06 in isolated fixtures; checkpoint one real fixed assessment."""
    if checkout.resolve().name != "dealdesk-phase1c-pinned":
        raise HybridContractError("phase1c_checkout_unexpected")
    with psycopg.connect(fixture_dsn, options="-c default_transaction_read_only=on") as conn:
        name = conn.execute("SELECT current_database()").fetchone()[0]
        count = conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]
    with psycopg.connect(checkpoint_dsn, options="-c default_transaction_read_only=on") as conn:
        checkpoint_name = conn.execute("SELECT current_database()").fetchone()[0]
        existing = conn.execute("SELECT to_regclass('public.checkpoints')").fetchone()[0]
        checkpoints = conn.execute("SELECT count(*) FROM public.checkpoints").fetchone()[0] if existing else 0
    if (not name.startswith("dealdesk_groq_decision_offline_")
            or not checkpoint_name.startswith("dealdesk_groq_decision_offline_")
            or checkpoint_name == name or count or checkpoints):
        raise HybridContractError("decision_databases_not_fresh")
    adapter = Phase1CAdapter(checkout)
    connect = lambda: psycopg.connect(fixture_dsn)
    with connect() as conn:
        install_disposable_cases(conn, (CASE,))
    model = GroqHybridTransportModel()
    with thesis_checkpointer(checkpoint_dsn) as saver:
        graph = build_original_graph(adapter, connect, saver)
        config = {"configurable": {"thread_id": ASSESSMENT}}
        state = graph.invoke(initial_state(ASSESSMENT, CASE.run_id), config)
        pinned = pinned_from_state(state)
        pool = adapter.validate_pinned_context(pinned)
        selected, reason = eligible_line(state, pool)
        if (reason != "eligible" or selected is None
                or len(state["specialist_results"]) != 6
                or state["stop_reason"] is not None
                or state["candidate_status"] != "not_started"
                or pinned.context.assessment_id != ASSESSMENT
                or pinned.context.phase1c_run_id != CASE.run_id
                or pool["deal"]["deal_id"] != CASE.ids()["D"]):
            raise HybridContractError("decision_original_not_eligible")
        pack, input = prepare_pack(graph, config, adapter, provider=model.provider,
                                   model=model.model, policy_version=POLICY)
        body = model.request_decision(pack["model_input"], (pack["observation"],))
        raw = _strict_wire(body, input, pack)
        if (input.assessment_id != ASSESSMENT or input.bundle_sha256 != pinned.context.bundle_sha256
                or input.source_input_digest != pinned.context.source_input_digest
                or pack["observation"]["tool"] != "inspect_line_supply"
                or graph.get_state(config).values.get("hybrid_execution") is not None):
            raise HybridContractError("decision_pack_identity_unexpected")
        identity = {"assessment_id": ASSESSMENT, "phase1c_run_id": str(CASE.run_id),
                    "phase1c_commit": PHASE1C_COMMIT,
                    "bundle_sha256": input.bundle_sha256,
                    "source_input_digest": input.source_input_digest,
                    "start_sha256": pack["start_sha256"], "pack_sha256": pack["pack_sha256"],
                    "request_sha256": sha256(raw).hexdigest(), "request_bytes": len(raw),
                    "configured_completion_tokens": 512, "maximum_request_bytes": MAX_REQUEST_BYTES,
                    "tool_names": list(EXPECTED_TOOLS), "decision_only": True}
        return identity, raw


def write_private(directory: Path, identity: dict, raw: bytes):
    """Exclusive owner-only files; never store the wire in the repository."""
    if (not directory.is_dir() or directory.is_symlink()
            or directory.stat().st_uid != os.geteuid()
            or stat.S_IMODE(directory.stat().st_mode) != 0o700
            or any(directory.iterdir()) or len(raw) != identity["request_bytes"]
            or sha256(raw).hexdigest() != identity["request_sha256"]):
        raise HybridContractError("decision_private_directory_invalid")
    for name, data in (("decision-request.json", raw + b"\n"),
                       ("identity.json", (_canonical(identity) + "\n").encode())):
        fd = os.open(directory / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    identity, raw = prepare(fixture_dsn=os.environ["DATABASE_URL"],
                            checkpoint_dsn=os.environ["CHECKPOINT_DATABASE_URL"],
                            checkout=Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
    write_private(Path(os.environ["DECISION_PRIVATE_DIR"]), identity, raw)
    print(_canonical(identity))  # identifiers/digests only; never print wire or provider output
