"""Default-off LangGraph Pricing/Credit typed-final execution foundation.

The existing hosted M2.0/M2.1 gates do not import this module. Public calls
accept only the scripted double; a separate dormant gate holds the private
capability for hosted transport. No key, HTTP client or activation lives here.
"""

from hashlib import sha256
import os
from pathlib import Path
from contextlib import nullcontext
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from .graph_state import pinned_from_state
from .groq_typed_final import (PROMPT_VERSION, WIRE_VERSION, DEVELOPMENT_FINAL_INSTRUCTION,
                                FinalResponseError, parse_response,
                                request_body, request_sha256)
from .hybrid_pack import _canonical
from .hybrid_send_reservation import (attempt_path, claim_and_call,
                                       exclusive_owner, verify_receipt)
from .live_models import ProviderError
from .m20_groq import parse_response as m20_parse, request_body as m20_wire
from .m20_specialists import (_identity as m20_identity, _inspect as m20_inspect,
                              _validate_claims, TOOLS as M20_TOOLS, VERSION as M20_VERSION)
from .m21_groq_contract import parse_response as m21_parse, request_body as m21_wire
from .m21_prompts import PROMPT_VERSION as M21_PROMPT
from .m21_specialists import (_identity as m21_identity, _inspect as m21_inspect,
                              _claims, TOOLS as M21_TOOLS, VERSION as M21_VERSION)
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import entries
from .tool_permissions import PERMISSION_VERSION
from .tool_response_diagnostic import ToolResponseError
from .typed_final_contract import InvalidTerminal, VERSION as FINAL_VERSION


PROTOCOL_VERSION = "pricing-credit-optin-offline-v1"
HOSTED_PROTOCOL_VERSION = "pricing-credit-optin-hosted-v1"
_HOSTED_CAPABILITY = object()
MAX_POSTS = {"pricing": 3, "credit": 2}
MAX_CONFIGURED_COMPLETION = {"pricing": 2048, "credit": 1536}
MAX_REPORTED_TOKENS = 24000


class _Flow(TypedDict):
    current: str


class ScriptedTypedFinal:
    """Exact offline double: never transports or loads a provider credential."""

    offline_only = True

    def __init__(self, decisions, final):
        self.decisions = list(decisions)
        self.final_response = final
        self.requests = []

    def decide(self, body):
        self.requests.append(body)
        if not self.decisions:
            raise InvalidTerminal("offline_inspection_exhausted")
        result = self.decisions.pop(0)
        return result(body) if callable(result) else result

    def finish(self, body):
        self.requests.append(body)
        if self.final_response is None:
            raise InvalidTerminal("offline_final_interrupted")
        return self.final_response(body) if callable(self.final_response) else self.final_response


def run_typed_final_offline(original, config, adapter, model, *, specialist,
                            inspection_plan=1, owner_dir=None, opt_in=False,
                            _capability=None, _hosted_binding=None,
                            _owner_locked=False, _pre_send=None, _final_instruction=None):
    """Run a separate default-off graph over an original PG checkpoint.

    `inspection_plan=2` is an explicit preflight selection for Pricing, never
    decided by the provider after the first inspection. The default graph is
    unchanged; a future hosted migration requires a distinct reviewed gate.
    """
    hosted = (_capability is _HOSTED_CAPABILITY and type(_hosted_binding) is dict
              and _owner_locked is True)
    if hosted:
        from .typed_final_hosted import HostedTypedTransport
    if (opt_in is not True or (not hosted and (type(model) is not ScriptedTypedFinal
            or _capability is not None or _hosted_binding is not None or _owner_locked
            or _pre_send is not None))
            or hosted and not callable(_pre_send)
            or (not hosted and _final_instruction is not None)
            or (hosted and _final_instruction is not None and (
                _final_instruction != DEVELOPMENT_FINAL_INSTRUCTION or
                _hosted_binding.get("development") is not True))
            or (hosted and _hosted_binding.get("development") is True and
                _final_instruction != DEVELOPMENT_FINAL_INSTRUCTION)
            or hosted and type(model) is not HostedTypedTransport
            or specialist not in MAX_POSTS
            or type(inspection_plan) is not int
            or inspection_plan not in ((1, 2) if specialist == "pricing" else (1,))
            or not isinstance(owner_dir, Path) or not owner_dir.is_absolute()):
        raise ValueError("typed_final_offline_opt_in_required")
    snapshot = original.get_state(config)
    state = snapshot.values
    if not hosted and state.get("typed_final_hosted_start"):
        raise EvidenceMismatch("typed_final_hosted_selection_cannot_fallback")
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    fixed = state["specialist_results"]
    if (snapshot.next or state.get("stop_reason")
            or set(fixed) != {"configuration", "pricing", "fulfillment", "credit",
                                  "policy", "approval_routing"}
            or fixed[specialist]["execution"] != "completed"
            or specialist == "pricing" and (fixed["configuration"]["finding"] != "confirmed"
                or "configuration" not in state.get("m20_ai_results", {}))
            or specialist == "credit" and fixed["pricing"]["execution"] != "completed"
            or specialist == "pricing" and (state.get("m20_ai_results", {}).get("pricing")
                or any(x.get("specialist") == "pricing" for x in state.get("m20_model_attempts", [])))
            or specialist == "credit" and (state.get("m21_ai_results", {}).get("credit")
                or any(x.get("specialist") == "credit" for x in state.get("m21_model_attempts", [])))):
        raise EvidenceMismatch("typed_final_existing_or_ineligible_investigation")
    if specialist == "pricing":
        input = {**m20_identity(ctx, specialist), "version": M20_VERSION,
            "line_ids": [str(x["deal_line_id"]) for x in pool["lines"]],
            "fixed_execution": fixed[specialist]["execution"],
            "fixed_finding": fixed[specialist]["finding"],
            "permitted_tool": M20_TOOLS[specialist], "max_inspections": 2}
    else:
        input = {**m21_identity(ctx, specialist), "version": M21_VERSION,
            "prompt_version": M21_PROMPT, "customer_id": pool["deal"]["customer_id"],
            "policy_set_code": ctx.policy_set_code,
            "data_snapshot_ref": ctx.data_snapshot_ref, "as_of_at": ctx.as_of_at.isoformat(),
            "fixed_execution": fixed[specialist]["execution"],
            "fixed_finding": fixed[specialist]["finding"],
            "permitted_tool": M21_TOOLS[specialist]}
    # Existing Configuration is an immutable prerequisite, including its two
    # already-budgeted offline model turns. Do not silently make Pricing standalone.
    configuration_turns = 0
    configuration_digest = None
    development_pricing = (hosted and specialist == "pricing" and
        _hosted_binding.get("development") is True)
    final_cap = 2048 if development_pricing else 1024
    component_cap = inspection_plan * 512 + final_cap
    if specialist == "pricing":
        config_result = state["m20_ai_results"]["configuration"]
        configuration_digest = sha256(_canonical(config_result).encode()).hexdigest()
        configuration_turns = config_result.get("model_turns")
        if (type(configuration_turns) is not int or not 0 <= configuration_turns <= 2 or
                config_result.get("execution") not in ("completed", "abstained") or
                configuration_turns + inspection_plan + 1 > 5 or
                (512 if configuration_turns >= 1 else 0) +
                (1024 if development_pricing and configuration_turns == 2 else
                 512 if configuration_turns == 2 else 0) + component_cap > (
                    4608 if development_pricing else 3072)):
            raise EvidenceMismatch("typed_final_configuration_budget")
    if (owner_dir.is_symlink() or owner_dir.stat().st_mode & 0o077 or
            owner_dir.stat().st_uid != os.geteuid()):
        raise EvidenceMismatch("typed_final_owner_invalid")
    protocol_version = HOSTED_PROTOCOL_VERSION if hosted else PROTOCOL_VERSION
    protocol = {"version": protocol_version, "specialist": specialist,
        "inspection_plan": inspection_plan, "input_sha256": sha256(_canonical(input).encode()).hexdigest(),
        "assessment_id": ctx.assessment_id, "phase1c_run_id": str(ctx.phase1c_run_id),
        "subject_id": ctx.original_deal_id, "bundle_sha256": ctx.bundle_sha256,
        "source_input_digest": ctx.source_input_digest,
        "as_of_at": ctx.as_of_at.isoformat(), "data_snapshot_ref": ctx.data_snapshot_ref,
        "wire_version": WIRE_VERSION, "prompt_version": PROMPT_VERSION,
        "final_version": FINAL_VERSION, "permission_version": PERMISSION_VERSION,
        "owner_directory": str(owner_dir),
        "owner_device": owner_dir.stat().st_dev, "owner_inode": owner_dir.stat().st_ino,
        "configuration_turns": configuration_turns,
        "configuration_result_sha256": configuration_digest,
        "hosted_binding": _hosted_binding if hosted else None}
    start_digest = sha256(_canonical(protocol).encode()).hexdigest()
    if (state.get("typed_final_protocol") not in (None, protocol)
            or state.get("typed_final_protocol") is None and
                (state.get("typed_final_attempts") or state.get("typed_final_results"))
            or state.get("typed_final_protocol") is not None and
                not isinstance(state.get("typed_final_attempts"), list)):
        raise EvidenceMismatch("typed_final_protocol_changed")

    def attempts():
        return original.get_state(config).values.get("typed_final_attempts", [])

    def scoped_ledger():
        ledger = entries(original, config, ctx.assessment_id, ctx.bundle_sha256)
        scoped = [e for e in ledger if e.get("identity", {}).get("specialist") == specialist
            and e.get("tool") == input["permitted_tool"]]
        if any(e.get("status") == "reserved" and not any(x.get("status") == "completed"
                and x.get("call_id") == e.get("call_id") for x in scoped) for e in scoped):
            raise EvidenceMismatch("typed_final_uncertain_tool_reservation")
        selected = [e for e in ledger if e.get("status") == "completed" and
            e.get("identity", {}).get("specialist") == specialist and
            e.get("identity", {}).get("source_input_digest") == ctx.source_input_digest and
            e.get("identity", {}).get("subject_id") == ctx.original_deal_id and
            e.get("tool") == input["permitted_tool"]]
        if len(selected) > inspection_plan or len({e["call_id"] for e in selected}) != len(selected):
            raise EvidenceMismatch("typed_final_ledger_count")
        for ordinal, event in enumerate(selected):
            expected = sha256(f"{M20_VERSION if specialist == 'pricing' else M21_VERSION}:"
                f"{ctx.assessment_id}:{specialist}:{ordinal}".encode()).hexdigest()
            reservations = [e for e in ledger if e.get("call_id") == expected]
            identity = event.get("identity", {})
            expected_identity = {**(m20_identity(ctx, specialist) if specialist == "pricing"
                else m21_identity(ctx, specialist)), "customer_id": pool["deal"]["customer_id"],
                "permission_version": PERMISSION_VERSION,
                "allowed_lines": sorted(str(x["deal_line_id"]) for x in pool["lines"])
                    if specialist == "pricing" else [], "allowed_sources": []}
            expected_args = ({"line_id": event.get("args", {}).get("line_id")}
                if specialist == "pricing" else {"subject_id": ctx.original_deal_id})
            if (event["call_id"] != expected or len(reservations) != 2 or
                    reservations[0].get("status") != "reserved" or
                    reservations[1] != event or
                    reservations[0].get("identity") != expected_identity or
                    identity != expected_identity or
                    event.get("args") != expected_args or
                    specialist == "pricing" and expected_args["line_id"] not in
                        input["line_ids"] or
                    reservations[0].get("args") != expected_args or
                    event.get("result", {}).get("execution") != "completed" or
                    event["result"].get("tool") != input["permitted_tool"] or
                    event.get("returned_refs") != event["result"].get("returned_refs") or
                    event["result"].get("returned_refs") != [r["ref"] for r in
                        event["result"].get("records", [])]):
                raise EvidenceMismatch("typed_final_ledger_identity")
        return tuple(e["result"] for e in selected)

    def checked_attempts():
        if (owner_dir.is_symlink() or owner_dir.stat().st_dev != protocol["owner_device"]
                or owner_dir.stat().st_ino != protocol["owner_inode"]):
            raise EvidenceMismatch("typed_final_owner_changed")
        rows = attempts()
        reserved = [x for x in rows if x.get("status") == "reserved"]
        if (len(reserved) > MAX_POSTS[specialist] or len(rows) > 2 * MAX_POSTS[specialist]
                or sum(512 if x.get("stage") == "typed_inspection" else final_cap
                    for x in reserved) > component_cap):
            raise EvidenceMismatch("typed_final_budget_corrupted")
        for x in rows:
            if (x.get("protocol_version") != protocol_version or
                    x.get("specialist") != specialist or
                    x.get("stage") not in ("typed_inspection", "typed_final") or
                    x.get("ordinal") not in ((0, 1) if x.get("stage") ==
                    "typed_inspection" and inspection_plan == 2 else (0,)) or
                    x.get("status") not in ("reserved", "returned")):
                raise EvidenceMismatch("typed_final_attempt_corrupted")
        if len({(x["stage"], x["ordinal"]) for x in reserved}) != len(reserved):
            raise EvidenceMismatch("typed_final_duplicate_reservation")
        for row in rows:
            if row["status"] == "returned" and not any(x["status"] == "reserved"
                    and x["stage"] == row["stage"] and x["ordinal"] == row["ordinal"]
                    and x["request_sha256"] == row["request_sha256"] for x in rows):
                raise EvidenceMismatch("typed_final_unreserved_return")
            if row["status"] == "returned" and (type(row.get("usage")) is not dict
                    or any(type(row["usage"].get(k)) is not int or
                        row["usage"][k] < 0 for k in ("prompt_tokens", "completion_tokens"))
                    or row["usage"]["prompt_tokens"] > 4096 or
                    row["usage"]["completion_tokens"] > (512 if row["stage"] ==
                        "typed_inspection" else final_cap)):
                raise EvidenceMismatch("typed_final_reported_usage_corrupted")
        if hosted and (len(reserved) + _hosted_binding["prior_posts"] > _hosted_binding[
                "maximum_posts_per_case"] or sum(512 if x["stage"] == "typed_inspection"
                else final_cap for x in reserved) + _hosted_binding[
                "prior_configured_completion"] > _hosted_binding[
                "maximum_configured_completion_per_case"]):
            raise EvidenceMismatch("typed_final_mixed_budget_corrupted")
        return rows

    def checked_attempt(stage, ordinal, body, send):
        checked_attempts()
        digest = request_sha256(body)
        prior = [x for x in attempts() if x["stage"] == stage and x["ordinal"] == ordinal]
        path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=start_digest, stage=stage, ordinal=ordinal)
        if prior:
            if (len(prior) != 2 or prior[0]["status"] != "reserved"
                    or prior[1]["status"] != "returned" or
                    any(x["request_sha256"] != digest for x in prior)
                    or not verify_receipt(path, start_digest=start_digest, stage=stage,
                        ordinal=ordinal, request_digest=digest)):
                raise EvidenceMismatch("typed_final_uncertain_attempt_no_replay")
            return prior[1], True
        reserved_count = len([x for x in attempts() if x["status"] == "reserved"])
        if reserved_count >= MAX_POSTS[specialist]:
            raise EvidenceMismatch("typed_final_post_budget")
        if hosted and (_hosted_binding["prior_posts"] + reserved_count + 1 >
                _hosted_binding["maximum_posts_per_case"]):
            raise EvidenceMismatch("typed_final_mixed_post_budget")
        reported = sum(x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"]
            for x in attempts() if x["status"] == "returned")
        if reported + (_hosted_binding["prior_reported_tokens"] if hosted else 0) >= (
                MAX_REPORTED_TOKENS):
            raise EvidenceMismatch("typed_final_reported_token_stop")
        configured = sum(512 if x["stage"] == "typed_inspection" else final_cap
            for x in attempts() if x["status"] == "reserved")
        if configured + (512 if stage == "typed_inspection" else final_cap) > (
                component_cap):
            raise EvidenceMismatch("typed_final_completion_budget")
        if hosted and (_hosted_binding["prior_configured_completion"] + configured +
                (512 if stage == "typed_inspection" else final_cap) >
                _hosted_binding["maximum_configured_completion_per_case"]):
            raise EvidenceMismatch("typed_final_mixed_completion_budget")
        marker = {"stage": stage, "ordinal": ordinal, "request_sha256": digest,
                  "specialist": specialist, "protocol_version": protocol_version}
        if hosted:
            before_reservation = _pre_send()
        original.update_state(config, {"typed_final_attempts": [*attempts(),
            {**marker, "status": "reserved"}]}, as_node="finish")
        if hosted:
            reserved_snapshot = original.get_state(config)
            if (reserved_snapshot.parent_config is None or
                    reserved_snapshot.parent_config.get("configurable", {}).get(
                        "checkpoint_id") != before_reservation):
                raise EvidenceMismatch("typed_hosted_reservation_parent_changed")
            model.expected_head = reserved_snapshot.config["configurable"]["checkpoint_id"]
        response = claim_and_call(owner_dir, assessment_id=ctx.assessment_id,
            start_digest=start_digest, stage=stage, ordinal=ordinal,
            request_digest=digest, send=lambda: send(body))
        return (marker, response), False

    def record(stage, ordinal, marker, action, usage, call=None):
        returned = {**marker, "status": "returned", "action_kind": action["kind"],
                    "usage": {key: usage[key] for key in ("prompt_tokens", "completion_tokens")},
                    **({"tool_call": call} if call is not None else {})}
        original.update_state(config, {"typed_final_attempts": [*attempts(), returned]},
                              as_node="finish")

    def publish(result):
        fresh = original.get_state(config).values
        review = {"version": protocol_version, "specialist": specialist,
            "assessment_id": ctx.assessment_id, "subject_id": ctx.original_deal_id,
            "source_input_digest": ctx.source_input_digest,
            "execution": result["execution"], "reason": result["reason"],
            "validated_claims": result["validated_claims"],
            "authority": "AI observations only; deterministic checks and human approval govern"}
        if fresh.get("reviewer_package", {}).get("typed_final_ai") not in (None, review):
            raise EvidenceMismatch("typed_final_reviewer_projection_changed")
        original.update_state(config, {"typed_final_results": {
            **fresh.get("typed_final_results", {}), specialist: result},
            "reviewer_package": {**fresh.get("reviewer_package", {}), "typed_final_ai": review}},
            as_node="finish")

    def inspection_body(observations, exchanges):
        body = (m20_wire(input, observations, exchanges=exchanges)
                if specialist == "pricing" else m21_wire(input, observations,
                    exchanges=exchanges))
        body["tools"] = [x for x in body["tools"] if x["function"]["name"] in (
            input["permitted_tool"], "abstain")]
        if hosted:
            from .typed_final_hosted import INSPECTION_PROMPT_SUFFIX
            body["messages"][0]["content"] += INSPECTION_PROMPT_SUFFIX
        if len(_canonical(body).encode()) > 8192:
            raise InvalidTerminal("inspection_request_oversize")
        return body

    def node_inspect(ordinal):
        def node(_):
            checked_attempts()
            results = original.get_state(config).values.get("typed_final_results", {})
            if specialist in results:
                if results[specialist].get("execution") == "error":
                    raise EvidenceMismatch("typed_final_error_terminal_no_replay")
                # A completed outcome is terminal only with a verified checkpointed
                # send; never trust an injected result to skip evidence verification.
                if not any(x["status"] == "returned" and x["stage"] == "typed_final"
                        for x in attempts()) and not any(x["status"] == "returned" and
                        x["action_kind"] == "abstain" for x in attempts()):
                    raise EvidenceMismatch("typed_final_result_without_attempt")
                for row in attempts():
                    path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                        start_digest=start_digest, stage=row["stage"], ordinal=row["ordinal"])
                    if not verify_receipt(path, start_digest=start_digest, stage=row["stage"],
                            ordinal=row["ordinal"], request_digest=row["request_sha256"]):
                        raise EvidenceMismatch("typed_final_result_receipt_uncertain")
                result = results[specialist]
                if (result.get("protocol_version") != protocol_version or
                        result.get("execution") not in ("completed", "abstained") or
                        type(result.get("validated_claims")) is not list):
                    raise EvidenceMismatch("typed_final_result_corrupted")
                if result["execution"] == "completed":
                    observed = scoped_ledger()
                    if len(observed) != inspection_plan:
                        raise EvidenceMismatch("typed_final_result_ledger_changed")
                    action = {"kind": "finding", "claims": result["validated_claims"]}
                    if specialist == "pricing":
                        _validate_claims({**action, "uncertainty_reasons": result.get(
                            "uncertainty_reasons", [])}, observed, specialist)
                    else:
                        _claims(action, observed)
                review = original.get_state(config).values["reviewer_package"].get(
                    "typed_final_ai")
                if (type(review) is not dict or review.get("version") != protocol_version
                        or review.get("assessment_id") != ctx.assessment_id
                        or review.get("specialist") != specialist
                        or review.get("execution") != result["execution"]
                        or review.get("validated_claims") != result["validated_claims"]
                        or review.get("source_input_digest") != ctx.source_input_digest):
                    raise EvidenceMismatch("typed_final_reviewer_projection_missing")
                return {"current": "stop"}
            observed = scoped_ledger()
            existing = [x for x in attempts() if x["stage"] == "typed_inspection"
                        and x["ordinal"] == ordinal]
            if existing:
                path = attempt_path(owner_dir, assessment_id=ctx.assessment_id,
                    start_digest=start_digest, stage="typed_inspection", ordinal=ordinal)
                if (len(existing) != 2 or existing[0]["status"] != "reserved"
                        or existing[1]["status"] != "returned" or
                        existing[1].get("action_kind") != "inspect" or
                        existing[1].get("protocol_version") != protocol_version or
                        existing[1].get("usage", {}).get("prompt_tokens", 4097) > 4096 or
                        existing[1].get("usage", {}).get("completion_tokens", 513) > 512 or
                        existing[1]["request_sha256"] != existing[0]["request_sha256"] or
                        not verify_receipt(path, start_digest=start_digest,
                            stage="typed_inspection", ordinal=ordinal,
                            request_digest=existing[0]["request_sha256"]) or
                        len(observed) < ordinal + 1):
                    raise EvidenceMismatch("typed_final_uncertain_inspection_no_replay")
                prior = [x for x in attempts() if x["stage"] == "typed_inspection" and
                         x["ordinal"] < ordinal and x["status"] == "returned"]
                if len(prior) != ordinal or any("tool_call" not in x for x in prior):
                    raise EvidenceMismatch("typed_final_inspection_chain")
                before = observed[:ordinal]
                body = inspection_body(before, tuple(x["tool_call"] for x in prior))
                if existing[0]["request_sha256"] != request_sha256(body):
                    raise EvidenceMismatch("typed_final_inspection_request_changed")
                return {"current": "continue"}
            if len(observed) != ordinal:
                raise EvidenceMismatch("typed_final_inspection_ledger_mismatch")
            prior = [x for x in attempts() if x["stage"] == "typed_inspection" and
                     x["ordinal"] < ordinal and x["status"] == "returned"]
            if len(prior) != ordinal or any("tool_call" not in x for x in prior):
                if ordinal:
                    raise EvidenceMismatch("typed_final_inspection_receipt_missing")
            exchanges = tuple(x["tool_call"] for x in prior)
            body = inspection_body(observed, exchanges)
            prior_entry, reused = checked_attempt("typed_inspection", ordinal, body,
                                                  model.decide)
            if reused:
                raise EvidenceMismatch("typed_final_unexpected_inspection_reuse")
            marker, response = prior_entry
            if type(response) is not dict or len(_canonical(response).encode()) > 16384:
                raise InvalidTerminal("inspection_response_oversize")
            usage = response.get("usage") if type(response) is dict else None
            if (type(usage) is not dict or any(type(usage.get(k)) is not int or
                    usage[k] < 0 for k in ("prompt_tokens", "completion_tokens")) or
                    usage["prompt_tokens"] > 4096 or usage["completion_tokens"] > 512):
                raise InvalidTerminal("invalid_inspection_usage")
            action = (m20_parse(response, input) if specialist == "pricing" else
                      m21_parse(response, input, observed))
            if action["kind"] == "abstain":
                if action.get("reason_code") not in (
                        "insufficient_evidence", "model_uncertainty", "unsupported_capability"):
                    raise InvalidTerminal("invalid_inspection_abstention")
                record("typed_inspection", ordinal, marker, action, usage)
                publish({
                    "execution": "abstained", "reason": action["reason_code"],
                    "validated_claims": [], "protocol_version": protocol_version,
                    "producer_type": "AI", "provider": "groq" if hosted else "offline_double"})
                return {"current": "stop"}
            if (action["kind"] != "inspect" or ordinal >= inspection_plan
                    or specialist == "pricing" and action["line_id"] not in input["line_ids"]):
                raise InvalidTerminal("invalid_inspection_action")
            call = response["choices"][0]["message"]["tool_calls"][0]
            if (type(call.get("id")) is not str or not 0 < len(call["id"]) <= 128 or
                    call.get("type") != "function" or
                    type(call.get("function", {}).get("arguments")) is not str):
                raise InvalidTerminal("invalid_inspection_call")
            descriptor = {"id": call["id"], "name": call["function"]["name"],
                          "arguments": call["function"]["arguments"]}
            record("typed_inspection", ordinal, marker, action, usage, descriptor)
            if specialist == "pricing":
                inspected = m20_inspect(original, config, adapter, specialist,
                                        action["line_id"], ordinal)
            else:
                inspected = m21_inspect(original, config, adapter, specialist)
            if (inspected.get("execution") != "completed" or
                    len(scoped_ledger()) != ordinal + 1):
                raise InvalidTerminal("inspection_not_completed")
            return {"current": "continue"}
        return node

    def node_final(_):
        results = original.get_state(config).values.get("typed_final_results", {})
        if specialist in results:
            return {"current": "stop"}
        observations = scoped_ledger()
        if len(observations) != inspection_plan:
            raise EvidenceMismatch("typed_final_missing_evidence")
        body = request_body(input, observations, completed_ledger=observations,
            **({"final_instruction": _final_instruction} if _final_instruction else {}))
        prior_entry, reused = checked_attempt("typed_final", 0, body, model.finish)
        if reused:
            raise EvidenceMismatch("typed_final_returned_without_validated_checkpoint")
        marker, response = prior_entry
        action = parse_response(response, input=input, observations=observations,
            development=development_pricing)
        usage = response["usage"]
        configured = sum(512 if x["stage"] == "typed_inspection" else final_cap
            for x in attempts() if x["status"] == "reserved")
        if configured > component_cap:
            raise EvidenceMismatch("typed_final_completion_budget")
        record("typed_final", 0, marker, action, usage)
        publish({
            "execution": "completed" if action["kind"] == "finding" else "abstained",
            "reason": None if action["kind"] == "finding" else action["reason_code"],
            "validated_claims": action.get("claims", []),
            "uncertainty_reasons": action.get("uncertainty_reasons", []),
            "protocol_version": protocol_version, "producer_type": "AI",
            "provider": "groq" if hosted else "offline_double"})
        return {"current": "done"}

    # LangGraph coordinates the opted-in specialist's fixed inspection plan.
    graph = StateGraph(_Flow)
    graph.add_node("inspect_0", node_inspect(0))
    if inspection_plan == 2:
        graph.add_node("inspect_1", node_inspect(1))
    graph.add_node("typed_final", node_final)
    graph.add_edge(START, "inspect_0")
    graph.add_conditional_edges("inspect_0", lambda s: s["current"],
        {"stop": END, "continue": "inspect_1" if inspection_plan == 2 else "typed_final"})
    if inspection_plan == 2:
        graph.add_conditional_edges("inspect_1", lambda s: s["current"],
                                    {"stop": END, "continue": "typed_final"})
    graph.add_edge("typed_final", END)
    with (nullcontext() if hosted else exclusive_owner(owner_dir, ctx.assessment_id)):
        if original.get_state(config).values.get("typed_final_protocol") is None:
            original.update_state(config, {"typed_final_protocol": protocol,
                "typed_final_attempts": [], "typed_final_results": {}}, as_node="finish")
        try:
            graph.compile().invoke({"current": "start"})
        except (InvalidTerminal, ValueError, ProviderError, EvidenceMismatch, OSError) as exc:
            # Store only a fixed category, not provider/model error text. A returned
            # but unparsed send and any uncertain receipt stay permanently terminal.
            if original.get_state(config).values.get("typed_final_results", {}).get(
                    specialist, {}).get("execution") != "completed":
                code = ("unsupported_schema" if isinstance(exc, InvalidTerminal) and
                    str(exc) == "unsupported_final_schema" else
                    "transport_failure" if isinstance(exc, ProviderError) else
                    "malformed_output" if isinstance(exc, (InvalidTerminal, ValueError)) else
                    "checkpoint_or_evidence_failure")
                current = original.get_state(config).values.get("typed_final_results", {})
                if specialist not in current:
                    original.update_state(config, {"typed_final_results": {
                        **current, specialist: {"execution": "error", "reason": code,
                            "validated_claims": [], "protocol_version": protocol_version,
                            "producer_type": "AI", "provider": "groq" if hosted else
                            "offline_double",
                            **({"model_output_category": exc.category} if hosted and
                               isinstance(exc, (FinalResponseError, ToolResponseError))
                               else {})}}},
                        as_node="finish")
            # No fallback, retry, or model-derived abstention.
            raise
    return original.get_state(config).values["typed_final_results"][specialist]
