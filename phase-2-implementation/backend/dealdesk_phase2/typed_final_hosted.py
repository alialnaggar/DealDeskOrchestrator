"""Dormant, separately gated hosted infrastructure for typed Pricing/Credit."""

from contextlib import contextmanager
import json
import os
from hashlib import sha256
from pathlib import Path

from .graph_state import pinned_from_state
from .groq_preflight import credential_shape
from .groq_typed_final import (WIRE_VERSION, PROMPT_VERSION, SCHEMA_NAME,
                               FINAL_SYSTEM_INSTRUCTION,
                               schema, request_sha256)
from .hybrid_pack import _canonical
from .hybrid_send_reservation import (attempt_path, claim_and_call,
                                       exclusive_owner, verify_receipt)
from .live_models import GROQ_MODEL, ProviderError
from .m20_groq import (GroqM20Model, WIRE_VERSION as CONFIG_WIRE,
                       PROMPT_VERSION as CONFIG_PROMPT, parse_response as config_parse,
                       request_body as config_request,
                       system_instruction as config_instruction)
from .m20_specialists import (_one as run_configuration,
                              _identity as config_identity,
                              _validate_claims as config_validate_claims,
                              VERSION as CONFIG_VERSION, MAX_INSPECTIONS,
                              TOOLS as CONFIG_TOOLS)
from .m21_groq_contract import WIRE_VERSION as CREDIT_WIRE
from .m21_prompts import system_instruction as credit_instruction
from .m21_specialists import VERSION as CREDIT_VERSION
from .phase1c_adapter import PHASE1C_COMMIT, EvidenceMismatch
from .tool_permissions import PERMISSION_VERSION
from .tool_ledger import entries
from .typed_final_offline import (_HOSTED_CAPABILITY, HOSTED_PROTOCOL_VERSION,
    run_typed_final_offline)


MANIFEST_VERSION = "pricing-credit-typed-hosted-manifest-v2"
INSPECTION_WIRE_VERSION = "pricing-credit-hosted-inspection-v1"
INSPECTION_PROMPT_VERSION = "pricing-credit-hosted-inspection-system-v1"
INSPECTION_PROMPT_SUFFIX = (" " + INSPECTION_PROMPT_VERSION + " " +
    INSPECTION_WIRE_VERSION + " Only inspect scoped evidence or abstain; "
    "a finding requires a separate no-tools final request.")
APPROVAL_NAME = "typed-final-approved-manifest.json"
HOSTED_ACTIVATION = False  # Changing this requires Ali's separate activation approval.
MAX_REPORTED_TOKENS = 24000
SCHEMA_SHA256 = sha256(_canonical(schema()).encode()).hexdigest()


def inspection_instruction(specialist):
    if specialist == "pricing":
        return config_instruction("pricing") + INSPECTION_PROMPT_SUFFIX
    if specialist == "credit":
        return (credit_instruction("credit") +
            " Choose exactly one declared function; no free-text final answer. " +
            CREDIT_WIRE + " " + CREDIT_VERSION + INSPECTION_PROMPT_SUFFIX)
    raise ValueError("typed_hosted_unknown_inspection")


MANIFEST_KEYS = frozenset(("version", "status", "phase1c_pin", "specialist",
    "inspection_plan", "case", "account_id", "billing_state", "provider", "model",
    "credential_env_selection", "permission_version", "inspection_wire_version",
    "inspection_prompt_version", "inspection_prompt_sha256",
    "configuration_wire_version", "configuration_prompt_version",
    "configuration_prompt_sha256", "wire_version", "prompt_version",
    "final_prompt_sha256", "schema_name", "schema_sha256", "budgets",
    "execution_context"))
CASE_KEYS = frozenset(("case_id", "assessment_id", "run_id", "subject_id",
    "bundle_sha256", "source_input_digest", "as_of_at", "data_snapshot_ref"))
BUDGET_KEYS = frozenset(("maximum_posts_per_case", "maximum_posts_per_specialist",
    "maximum_configured_completion_per_case", "maximum_configured_completion_per_specialist",
    "maximum_serialized_request_bytes_per_post", "maximum_response_bytes_per_post",
    "maximum_prompt_tokens_per_returned_post", "maximum_final_content_bytes",
    "maximum_inspection_completion_tokens", "maximum_final_completion_tokens",
    "reported_total_token_post_send_stop"))
CONTEXT_KEYS = frozenset(("fixture_database", "checkpoint_database",
    "fixture_database_oid", "checkpoint_database_oid", "owner_directory",
    "fresh_databases_required"))


def budgets(specialist, inspection_plan):
    """Exact component and mixed ceilings, not a pre-send spending guarantee."""
    if specialist not in ("pricing", "credit") or inspection_plan not in (
            (1, 2) if specialist == "pricing" else (1,)):
        raise ValueError("typed_hosted_invalid_plan")
    component = inspection_plan * 512 + 1024
    return {"maximum_posts_per_case": (2 + inspection_plan + 1 if specialist ==
        "pricing" else 2), "maximum_posts_per_specialist": inspection_plan + 1,
        "maximum_configured_completion_per_case": (1024 + component if specialist ==
        "pricing" else component),
        "maximum_configured_completion_per_specialist": component,
        "maximum_serialized_request_bytes_per_post": 8192,
        "maximum_response_bytes_per_post": 16384,
        "maximum_prompt_tokens_per_returned_post": 4096,
        "maximum_final_content_bytes": 8192,
        "maximum_inspection_completion_tokens": 512,
        "maximum_final_completion_tokens": 1024,
        "reported_total_token_post_send_stop": MAX_REPORTED_TOKENS}


def full_m21_budget():
    """Non-executable planning bound: Credit + unchanged Policy/Routing."""
    return {"posts": 6, "configured_completion_tokens": 3584,
            "reported_post_send_stop": MAX_REPORTED_TOKENS}


def _validate_manifest(manifest, digest, specialist, owner, pinned, config):
    if (type(manifest) is not dict or set(manifest) != MANIFEST_KEYS or
            type(digest) is not str or len(digest) != 64 or
            sha256(_canonical(manifest).encode()).hexdigest() != digest or
            manifest["version"] != MANIFEST_VERSION or
            manifest["status"] != "authorized_one_case" or
            manifest["specialist"] != specialist or
            type(manifest["inspection_plan"]) is not int or
            manifest["budgets"] != budgets(specialist, manifest["inspection_plan"]) or
            set(manifest["budgets"]) != BUDGET_KEYS or
            manifest["phase1c_pin"] != PHASE1C_COMMIT or
            manifest["provider"] != "groq" or manifest["model"] != GROQ_MODEL or
            manifest["permission_version"] != PERMISSION_VERSION or
            manifest["credential_env_selection"] != "GROQ_SECONDARY_API_KEY" or
            manifest["billing_state"] != "owner_asserts_free_tier_billing_disabled" or
            type(manifest["account_id"]) is not str or not manifest["account_id"] or
            len(manifest["account_id"]) > 100 or
            manifest["inspection_wire_version"] != INSPECTION_WIRE_VERSION or
            manifest["inspection_prompt_version"] != INSPECTION_PROMPT_VERSION or
            manifest["inspection_prompt_sha256"] != sha256(inspection_instruction(
                specialist).encode()).hexdigest() or
            manifest["configuration_wire_version"] != CONFIG_WIRE or
            manifest["configuration_prompt_version"] != CONFIG_PROMPT or
            manifest["configuration_prompt_sha256"] != sha256(config_instruction(
                "configuration").encode()).hexdigest() or
            manifest["wire_version"] != WIRE_VERSION or
            manifest["prompt_version"] != PROMPT_VERSION or
            manifest["final_prompt_sha256"] != sha256(
                FINAL_SYSTEM_INSTRUCTION.encode()).hexdigest() or
            manifest["schema_name"] != SCHEMA_NAME or
            manifest["schema_sha256"] != SCHEMA_SHA256 or
            type(manifest["case"]) is not dict or set(manifest["case"]) != CASE_KEYS or
            type(manifest["execution_context"]) is not dict or
            set(manifest["execution_context"]) != CONTEXT_KEYS):
        raise ValueError("typed_hosted_manifest_or_approval_hash_mismatch")
    case, ctx = manifest["case"], pinned.context
    if (case != {"case_id": case["case_id"], "assessment_id": ctx.assessment_id,
            "run_id": str(ctx.phase1c_run_id), "subject_id": ctx.original_deal_id,
            "bundle_sha256": ctx.bundle_sha256,
            "source_input_digest": ctx.source_input_digest,
            "as_of_at": ctx.as_of_at.isoformat(),
            "data_snapshot_ref": ctx.data_snapshot_ref} or
            case["case_id"] not in ("B01", "B05", "N03", "CREDIT-LIMIT") or
            case["subject_id"] != {"B01": "M18-D-B01", "B05": "M18-D-B05",
                "N03": "M18-D-N03", "CREDIT-LIMIT": "CONFLICT-DEAL-13"}[
                    case["case_id"]] or
            config.get("configurable", {}).get("thread_id") != ctx.assessment_id):
        raise EvidenceMismatch("typed_hosted_case_identity_changed")
    execution = manifest["execution_context"]
    if (execution["fresh_databases_required"] is not True or
            type(execution["fixture_database"]) is not str or
            type(execution["checkpoint_database"]) is not str or
            not execution["fixture_database"] or not execution["checkpoint_database"] or
            execution["fixture_database"] == execution["checkpoint_database"] or
            any(type(execution[k]) is not int or execution[k] <= 0 for k in (
                "fixture_database_oid", "checkpoint_database_oid")) or
            execution["owner_directory"] != str(owner) or
            str(owner.resolve(strict=True)) != str(owner) or
            owner.is_symlink()):
        raise EvidenceMismatch("typed_hosted_owner_or_databases_changed")


def _approval(owner, manifest, digest):
    path = owner / APPROVAL_NAME
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            stat = os.fstat(fd)
            if (stat.st_uid != os.geteuid() or stat.st_mode & 0o077 or
                    stat.st_nlink != 1 or not 0 < stat.st_size <= 2048):
                raise ValueError()
            with os.fdopen(os.dup(fd), encoding="utf-8") as stream:
                data = json.load(stream)
        finally:
            os.close(fd)
    except (ValueError, OSError, TypeError, UnicodeError):
        raise EvidenceMismatch("typed_hosted_approval_unavailable") from None
    if data != {"version": MANIFEST_VERSION, "assessment_id": manifest["case"][
            "assessment_id"], "approved_manifest_sha256": digest,
            "credential_env_selection": "GROQ_SECONDARY_API_KEY",
            "account_id": manifest["account_id"], "owner_billing_attested": True,
            "typed_final_opt_in_confirmed": True}:
        raise EvidenceMismatch("typed_hosted_approval_mismatch")


class HostedTypedTransport:
    _typed_hosted_transport = True

    def __init__(self, send, inspection_prompt_sha256, final_prompt_sha256):
        self._send = send
        self.expected_head = None
        self._inspection_prompt_sha256 = inspection_prompt_sha256
        self._final_prompt_sha256 = final_prompt_sha256

    def decide(self, body):
        if ("response_format" in body or body.get("tool_choice") != "required"
                or len(_canonical(body).encode()) > 8192 or
                sha256(body.get("messages", [{}])[0].get("content", "").encode(
                    )).hexdigest() != self._inspection_prompt_sha256 or
                INSPECTION_WIRE_VERSION not in body.get("messages", [{}])[0].get(
                    "content", "") or
                {x["function"]["name"] for x in body.get("tools", [])} not in (
                    {"inspect_pricing_line", "abstain"},
                    {"inspect_customer_credit_evidence", "abstain"})):
            raise ValueError("typed_hosted_inspection_wire_invalid")
        return self._send(body, self.expected_head)

    def finish(self, body):
        if (body.get("response_format", {}).get("json_schema", {}).get("strict") is not True
                or body["response_format"]["json_schema"].get("name") != SCHEMA_NAME
                or sha256(body.get("messages", [{}])[0].get("content", "").encode(
                    )).hexdigest() != self._final_prompt_sha256
                or any(k in body for k in ("tools", "tool_choice", "parallel_tool_calls",
                    "stream", "reasoning_format")) or len(body.get("messages", [])) != 2
                or len(_canonical(body).encode()) > 8192):
            raise ValueError("typed_hosted_final_wire_invalid")
        return self._send(body, self.expected_head)


class _ConfigurationModel(GroqM20Model):
    """Existing Configuration wire and validators; new receipt namespace only."""
    def __init__(self, send, owner, assessment_id, digest, pre_send):
        super().__init__("configuration")
        self._send = send
        self._owner = owner
        self._assessment = assessment_id
        self._digest = digest
        self._pre_send = pre_send

    def next_action(self, input, observations):
        body = self.prepare_request(input, observations)
        ordinal = len(observations)
        request_digest = request_sha256(body)
        if (ordinal not in (0, 1) or request_digest != self.pending_request_digest
                or len(_canonical(body).encode()) > 8192):
            raise ValueError("typed_hosted_config_wire_changed")
        self.last_usage = None
        self.last_tool_call = None
        expected_head = self._pre_send()
        response = claim_and_call(self._owner, assessment_id=self._assessment,
            start_digest=self._digest, stage="typed_configuration", ordinal=ordinal,
            request_digest=request_digest, send=lambda: self._send(body, expected_head))
        if type(response) is not dict or len(_canonical(response).encode()) > 16384:
            raise ProviderError("provider_response_oversize")
        usage = response.get("usage")
        if (type(usage) is not dict or any(type(usage.get(k)) is not int or usage[k] < 0
                for k in ("prompt_tokens", "completion_tokens")) or
                usage["prompt_tokens"] > 4096 or usage["completion_tokens"] > 512):
            raise ProviderError("hosted_usage_unverifiable")
        self.last_usage = {k: usage[k] for k in ("prompt_tokens", "completion_tokens")}
        action = config_parse(response, input)
        if action["kind"] == "inspect":
            call = response["choices"][0]["message"]["tool_calls"][0]
            if (type(call.get("id")) is not str or not 0 < len(call["id"]) <= 128
                    or call.get("type") != "function"):
                raise ValueError("typed_hosted_config_call_invalid")
            self.last_tool_call = {"id": call["id"], "name": call["function"]["name"],
                                   "arguments": call["function"]["arguments"]}
        return action


def _checked_configuration(original, config, adapter, owner, manifest_digest, assessment_id):
    state = original.get_state(config).values
    pinned = pinned_from_state(state)
    ctx = pinned.context
    expected_identity = config_identity(ctx, "configuration")
    attempts = state.get("m20_model_attempts", [])
    if (len(attempts) > 4 or len([x for x in attempts if x.get("status") == "reserved"]) > 2
            or any(x.get("specialist") != "configuration" or x.get("provider") != "groq"
                   or x.get("prompt_version") != CONFIG_PROMPT or
                   x.get("version") != CONFIG_VERSION or x.get("ordinal") not in (0, 1)
                   or x.get("status") not in ("reserved", "returned") or
                   any(x.get(k) != v for k, v in expected_identity.items())
                   for x in attempts)):
        raise EvidenceMismatch("typed_hosted_configuration_attempts_changed")
    reserved = [x for x in attempts if x["status"] == "reserved"]
    returned = [x for x in attempts if x["status"] == "returned"]
    if len(reserved) != len(returned) or len({x["ordinal"] for x in reserved}) != len(
            reserved) or sorted(x["ordinal"] for x in reserved) != list(range(len(reserved))):
        raise EvidenceMismatch("typed_hosted_configuration_uncertain")
    for reservation in reserved:
        matches = [x for x in returned if x["ordinal"] == reservation["ordinal"]]
        if (len(matches) != 1 or matches[0].get("request_sha256") != reservation.get(
                "request_sha256") or type(matches[0].get("usage")) is not dict or
                any(type(matches[0]["usage"].get(k)) is not int or
                    matches[0]["usage"][k] < 0 for k in ("prompt_tokens", "completion_tokens"))
                or matches[0]["usage"]["prompt_tokens"] > 4096 or
                matches[0]["usage"]["completion_tokens"] > 512 or
                not verify_receipt(attempt_path(owner, assessment_id=assessment_id,
                    start_digest=manifest_digest, stage="typed_configuration",
                    ordinal=reservation["ordinal"]), start_digest=manifest_digest,
                    stage="typed_configuration", ordinal=reservation["ordinal"],
                    request_digest=reservation["request_sha256"])):
            raise EvidenceMismatch("typed_hosted_configuration_receipt_changed")
    if returned:
        pool = adapter.validate_pinned_context(pinned)
        input = {**config_identity(ctx, "configuration"), "version": CONFIG_VERSION,
            "line_ids": [str(x["deal_line_id"]) for x in pool["lines"]],
            "fixed_execution": state["specialist_results"]["configuration"]["execution"],
            "fixed_finding": state["specialist_results"]["configuration"]["finding"],
            "permitted_tool": CONFIG_TOOLS["configuration"],
            "max_inspections": MAX_INSPECTIONS}
        ledger = entries(original, config, assessment_id, ctx.bundle_sha256)
        completed_events = [e for e in ledger if e.get("status") == "completed"
            and e.get("tool") == CONFIG_TOOLS["configuration"] and
            e.get("identity", {}).get("specialist") == "configuration" and
            e.get("identity", {}).get("source_input_digest") == ctx.source_input_digest]
        observations = [e["result"] for e in completed_events]
        inspections = [x for x in returned if x.get("action_kind") == "inspect"]
        if (len(observations) != len(inspections) or len(inspections) > 1
                or any(e.get("execution") != "completed" for e in observations)):
            raise EvidenceMismatch("typed_hosted_configuration_ledger_changed")
        identity = {**config_identity(ctx, "configuration"),
            "customer_id": pool["deal"]["customer_id"],
            "permission_version": PERMISSION_VERSION,
            "allowed_lines": sorted(input["line_ids"]), "allowed_sources": []}
        for event in completed_events:
            ordinal = completed_events.index(event)
            expected_id = sha256(f"{CONFIG_VERSION}:{ctx.assessment_id}:configuration:"
                f"{ordinal}".encode()).hexdigest()
            related = [e for e in ledger if e.get("call_id") == expected_id]
            if (event.get("call_id") != expected_id or len(related) != 2
                    or related[0].get("status") != "reserved" or related[1] != event
                    or related[0].get("identity") != identity or event.get(
                        "identity") != identity or event.get("args") != related[0].get(
                        "args") or event.get("args", {}).get("line_id") not in input[
                        "line_ids"] or event.get("result", {}).get("tool") != CONFIG_TOOLS[
                        "configuration"] or event.get("returned_refs") != event[
                        "result"].get("returned_refs")):
                raise EvidenceMismatch("typed_hosted_configuration_source_tampered")
        for ordinal in range(len(returned)):
            before = tuple(observations[:ordinal])
            calls = tuple(x["tool_call"] for x in inspections[:ordinal])
            expected = request_sha256(config_request(input, before, exchanges=calls))
            if returned[ordinal].get("request_sha256") != expected:
                raise EvidenceMismatch("typed_hosted_configuration_request_changed")
        result = state.get("m20_ai_results", {}).get("configuration")
        if result and result.get("execution") == "completed":
            config_validate_claims({"kind": "finding", "claims": result[
                "validated_claims"], "uncertainty_reasons": result[
                "uncertainty_reasons"]}, tuple(observations), "configuration")
    return reserved, returned


def _database_identity(original, manifest, *, exclusive):
    execution = manifest["execution_context"]
    with original.phase2_connection_factory() as conn:
        business_db, business_oid = conn.execute(
            "SELECT current_database(), oid FROM pg_database WHERE datname = current_database()"
        ).fetchone()
    checkpoint = original.checkpointer.conn
    checkpoint_row = checkpoint.execute(
        "SELECT current_database(), oid FROM pg_database WHERE datname = current_database()"
    ).fetchone()
    checkpoint_db, checkpoint_oid = checkpoint_row["current_database"], checkpoint_row["oid"]
    if (business_db != execution["fixture_database"] or
            checkpoint_db != execution["checkpoint_database"] or
            business_oid != execution["fixture_database_oid"] or
            checkpoint_oid != execution["checkpoint_database_oid"] or
            business_db == checkpoint_db and business_oid == checkpoint_oid):
        raise EvidenceMismatch("typed_hosted_database_identity_changed")
    if exclusive:
        # A new dedicated checkpoint DB contains only the current assessment.
        # Checkpoint history, not merely the latest state, prevents cleared
        # historical attempts from being relabeled as a new investigation.
        for table in ("checkpoints", "checkpoint_writes", "checkpoint_blobs"):
            foreign = checkpoint.execute("SELECT 1 FROM " + table +
                " WHERE thread_id IS DISTINCT FROM %s LIMIT 1",
                (manifest["case"]["assessment_id"],)).fetchone()
            if foreign:
                raise EvidenceMismatch("typed_hosted_checkpoint_database_reused")


def _history_identity(original, config, manifest, digest):
    for item in original.get_state_history(config):
        state = item.values
        if (state and state.get("assessment_id") != manifest["case"]["assessment_id"] or
                any(state.get(key) for key in ("hybrid_investigation_start",
                    "m20_hosted_owner", "m21_hosted_owner", "m21_model_attempts",
                    "m21_ai_results", "m20_review", "m21_review")) or
                any(row.get("specialist") == "pricing" for row in state.get(
                    "m20_model_attempts", [])) or state.get("m20_ai_results", {}).get(
                    "pricing") or any(state.get(key) for key in (
                    "typed_final_results", "typed_final_attempts", "typed_final_protocol"))
                and not state.get("typed_final_hosted_start") or
                state.get("typed_final_hosted_start", {}).get("manifest_sha256") not in (
                    None, digest)):
            raise EvidenceMismatch("typed_hosted_assessment_history_reused")


@contextmanager
def _checkpoint_send_lock(original):
    """Block every checkpoint DML writer during final validation and send.

    Use a distinct connection: LangGraph's saver commits its reservation before
    entering here. The production checkpoint database is dedicated to this case.
    A mere advisory lock would not constrain an ordinary saver or SQL writer.
    """
    import psycopg
    with psycopg.connect(original.checkpointer.conn.info.dsn) as guard:
        with guard.transaction():
            # An uncooperative writer must not stall a guarded send forever.
            guard.execute("SET LOCAL lock_timeout = '2000ms'")
            try:
                guard.execute("LOCK TABLE public.checkpoints, public.checkpoint_writes, "
                              "public.checkpoint_blobs IN SHARE ROW EXCLUSIVE MODE")
            except psycopg.errors.LockNotAvailable:
                raise EvidenceMismatch("typed_hosted_checkpoint_lock_unavailable") from None
            yield


def _run_assessment(original, config, adapter, *, manifest, approved_manifest_sha256,
    specialist, owner_dir, send, credential_digest, exclusive_databases):
    """Internal composition layer; only the gated entry creates a live sender.

    Tests exercise this with a synthetic sender from backend/tests, never _post.
    Python callers with arbitrary code in this process are outside this trust
    boundary; the public entry must never accept a sender injection.
    """
    if not isinstance(owner_dir, Path) or not owner_dir.is_absolute():
        raise ValueError("typed_hosted_private_owner_required")
    snapshot = original.get_state(config)
    pinned = pinned_from_state(snapshot.values)
    adapter.validate_pinned_context(pinned)
    _validate_manifest(manifest, approved_manifest_sha256, specialist, owner_dir,
                       pinned, config)
    if snapshot.next or snapshot.values.get("stop_reason"):
        raise EvidenceMismatch("typed_hosted_original_incomplete")
    ctx = pinned.context
    with exclusive_owner(owner_dir, ctx.assessment_id):
        locked = original.get_state(config)
        locked_pinned = pinned_from_state(locked.values)
        adapter.validate_pinned_context(locked_pinned)
        _validate_manifest(manifest, approved_manifest_sha256, specialist, owner_dir,
                           locked_pinned, config)
        if (locked.next or locked.values.get("stop_reason") or
                locked.values != snapshot.values or locked_pinned != pinned or
                locked.config.get("configurable", {}).get("checkpoint_id") !=
                snapshot.config.get("configurable", {}).get("checkpoint_id")):
            raise EvidenceMismatch("typed_hosted_state_changed_before_lock")
        _approval(owner_dir, manifest, approved_manifest_sha256)
        _database_identity(original, manifest, exclusive=exclusive_databases)
        _history_identity(original, config, manifest, approved_manifest_sha256)
        fixed_baseline = locked.values.get("specialist_results")
        fixed_digest = locked.values.get("fixed_decision_sha256")
        ledger_baseline = locked.values.get("tool_access_ledger", [])

        def pre_send():
            latest = original.get_state(config)
            latest_pinned = pinned_from_state(latest.values)
            adapter.validate_pinned_context(latest_pinned)
            _validate_manifest(manifest, approved_manifest_sha256, specialist,
                               owner_dir, latest_pinned, config)
            _database_identity(original, manifest, exclusive=exclusive_databases)
            ledger = latest.values.get("tool_access_ledger", [])
            if (latest.next or latest.values.get("stop_reason") or
                    latest_pinned != locked_pinned or
                    latest.values.get("specialist_results") != fixed_baseline or
                    latest.values.get("fixed_decision_sha256") != fixed_digest or
                    type(ledger) is not list or
                    ledger[:len(ledger_baseline)] != ledger_baseline or
                    any(type(event) is not dict or event.get("identity", {}).get(
                        "assessment_id") != ctx.assessment_id or
                        event.get("identity", {}).get("specialist") not in (
                            ("configuration", "pricing") if specialist == "pricing"
                            else ("credit",)) for event in ledger[len(ledger_baseline):]) or
                    latest.values.get("typed_final_hosted_start") != owner):
                raise EvidenceMismatch("typed_hosted_state_changed_before_send")
            return latest.config["configurable"]["checkpoint_id"]

        def serialized_send(body, expected_head):
            # The durable checkpoint reservation and receipt are already in
            # place. A concurrent writer between validation and this lock
            # changes the head and fails closed, without invoking the sender.
            with _checkpoint_send_lock(original):
                if pre_send() != expected_head:
                    raise EvidenceMismatch("typed_hosted_checkpoint_changed_before_send")
                return send(body)
        owner = {"version": MANIFEST_VERSION, "manifest_sha256": approved_manifest_sha256,
            "owner_path": str(owner_dir), "owner_device": owner_dir.stat().st_dev,
            "owner_inode": owner_dir.stat().st_ino, "credential_sha256": credential_digest,
            "account_id": manifest["account_id"]}
        fresh = original.get_state(config).values
        if (fresh.get("typed_final_hosted_start") not in (None, owner) or
                fresh.get("typed_final_hosted_start") is None and (
                    fresh.get("typed_final_protocol") or fresh.get("typed_final_attempts") or
                    fresh.get("typed_final_results") or fresh.get("m20_model_attempts") or
                    fresh.get("m20_ai_results") or fresh.get("m21_model_attempts") or
                    fresh.get("m21_ai_results")) or
                fresh.get("m20_ai_results", {}).get("pricing") or
                fresh.get("m21_ai_results", {}).get("credit")):
            raise EvidenceMismatch("typed_hosted_prior_protocol_or_attempt")
        refreshed = fresh
        # Closed owner-path namespace: reject extraneous receipts and links.
        allowed = {APPROVAL_NAME, attempt_path(owner_dir, assessment_id=ctx.assessment_id,
            start_digest="0" * 64, stage="owner", ordinal=0).name}
        allowed.update(attempt_path(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=approved_manifest_sha256, stage="typed_configuration", ordinal=x[
                "ordinal"]).name for x in refreshed.get("m20_model_attempts", []) if x.get(
                    "status") == "reserved" and type(x.get("ordinal")) is int and x[
                    "ordinal"] in (0, 1))
        protocol = refreshed.get("typed_final_protocol")
        if protocol:
            start = sha256(_canonical(protocol).encode()).hexdigest()
            allowed.update(attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                start_digest=start, stage=x["stage"], ordinal=x["ordinal"]).name
                for x in refreshed.get("typed_final_attempts", []) if x.get("status") ==
                "reserved" and x.get("stage") in ("typed_inspection", "typed_final")
                and type(x.get("ordinal")) is int and x["ordinal"] in (0, 1))
        if any(p.name not in allowed or p.is_symlink() for p in owner_dir.iterdir()):
            raise EvidenceMismatch("typed_hosted_owner_unknown_receipt")
        if fresh.get("typed_final_hosted_start") is None:
            original.update_state(config, {"typed_final_hosted_start": owner}, as_node="finish")
        # Re-check the active selection and pinned source after any checkpoint
        # update, before the first Configuration or typed-final reservation.
        pre_send()
        if specialist == "pricing":
            reserved, completed = _checked_configuration(original, config, adapter, owner_dir,
                approved_manifest_sha256, ctx.assessment_id)
            if not completed:
                if refreshed.get("m20_ai_results", {}).get("configuration"):
                    raise EvidenceMismatch("typed_hosted_configuration_unverified")
                original.update_state(config, {"m20_hosted_base_tokens": 0}, as_node="finish")
                run_configuration(original, config, adapter, "configuration",
                    _ConfigurationModel(serialized_send, owner_dir, ctx.assessment_id,
                                        approved_manifest_sha256, pre_send), hosted=True)
                reserved, completed = _checked_configuration(original, config, adapter, owner_dir,
                    approved_manifest_sha256, ctx.assessment_id)
            result = original.get_state(config).values.get("m20_ai_results", {}).get(
                "configuration", {})
            if (result.get("execution") not in ("completed", "abstained") or
                    result.get("model_turns") != len(completed) or
                    result.get("provider") != "groq" or not completed):
                raise EvidenceMismatch("typed_hosted_configuration_not_completed")
        else:
            if refreshed.get("m20_ai_results") or refreshed.get("m20_model_attempts"):
                raise EvidenceMismatch("typed_hosted_credit_prior_m20_attempts")
            reserved, completed = [], []
        prior_reported = sum(x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"]
            for x in completed)
        binding = {"manifest_sha256": approved_manifest_sha256,
            "credential_sha256": credential_digest, "account_id": manifest["account_id"],
            "prior_posts": len(reserved), "prior_configured_completion": len(reserved) * 512,
            "prior_reported_tokens": prior_reported,
            "maximum_posts_per_case": manifest["budgets"]["maximum_posts_per_case"],
            "maximum_configured_completion_per_case": manifest["budgets"][
                "maximum_configured_completion_per_case"]}
        if prior_reported >= MAX_REPORTED_TOKENS:
            raise EvidenceMismatch("typed_hosted_reported_budget_exhausted")
        model = HostedTypedTransport(serialized_send, manifest["inspection_prompt_sha256"],
                                     manifest["final_prompt_sha256"])
        return run_typed_final_offline(original, config, adapter, model,
            specialist=specialist, inspection_plan=manifest["inspection_plan"],
            owner_dir=owner_dir, opt_in=True, _capability=_HOSTED_CAPABILITY,
            _hosted_binding=binding, _owner_locked=True, _pre_send=pre_send)


def run_typed_final_hosted(original, config, adapter, *, manifest, approved_manifest_sha256,
    specialist, owner_dir, authorized=False, owner_billing_attested=False):
    """Production gate: no sender or injected transport when activation is off."""
    if (HOSTED_ACTIVATION is not True or authorized is not True or
            owner_billing_attested is not True):
        raise ValueError("typed_hosted_activation_or_authorization_required")
    # The test-only composition layer never imports or receives the sender.
    from .live_models import _post
    key = os.environ.get("GROQ_SECONDARY_API_KEY")
    if credential_shape(key) != "credential_shape_ok":
        raise ValueError("typed_hosted_secondary_credential_unavailable")
    def send(body):
        return _post("https://api.groq.com/openai/v1/chat/completions",
            "Bearer " + key, "Authorization", body, timeout_seconds=30,
            classify_transport=True, reject_redirects=True)
    return _run_assessment(original, config, adapter, manifest=manifest,
        approved_manifest_sha256=approved_manifest_sha256, specialist=specialist,
        owner_dir=owner_dir, send=send, credential_digest=sha256(key.encode()).hexdigest(),
        exclusive_databases=True)
