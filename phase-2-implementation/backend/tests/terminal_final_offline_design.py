"""Offline-only typed terminal design; NEVER imported by a hosted runner.

This deliberately makes a separate no-tools final request, not a Groq native
tool continuation. Durable send reservations belong to the existing runner.
"""

import json

from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m20_specialists import (TOOLS as M20_TOOLS, VERSION as M20_VERSION,
    _validate_claims)
from dealdesk_phase2.m21_redaction import model_view
from dealdesk_phase2.m21_specialists import TOOLS, VERSION as M21_VERSION, _claims


VERSION = "terminal-final-offline-v1"
REASONS = ("insufficient_evidence", "model_uncertainty", "unsupported_capability")
MAX_RESPONSE_BYTES = 16384
MAX_REQUEST_BYTES = 8192  # hypothetical cap; never widens active permissions
MAX_COMPLETION_TOKENS = 1024  # proposal only, not an authorized hosted budget
IDENTITY_KEYS = frozenset(("assessment_id", "phase1c_run_id", "subject_id",
                           "bundle_sha256", "source_input_digest", "specialist"))


class TerminalContractError(ValueError):
    pass


def schema():
    """Strict-mode compatible shape; cross-field semantics are checked locally."""
    return {"type": "object", "properties": {
        "version": {"type": "string", "enum": [VERSION]},
        "kind": {"type": "string", "enum": ["finding", "abstain"]},
        "claims": {"type": "array", "items": {"type": "object", "properties": {
            "ref": {"type": "string"}, "field": {"type": "string"},
            "value_json": {"type": "string"}},
            "required": ["ref", "field", "value_json"], "additionalProperties": False}},
        "uncertainty_reasons": {"type": "array", "items": {"type": "string"}},
        "reason_code": {"type": "string", "enum": ["none", *REASONS]}},
        "required": ["version", "kind", "claims", "uncertainty_reasons", "reason_code"],
        "additionalProperties": False}


def _verified_view(input, observations, completed_ledger):
    """Require exact completed tool result and frozen identity before projection."""
    if (type(input) is not dict or type(observations) is not tuple or len(observations) != 1
            or type(completed_ledger) is not tuple or observations != completed_ledger
            or any(type(x) is not dict or x.get("execution") != "completed"
                   for x in observations)):
        raise TerminalContractError("unverified_inspection")
    specialist = input.get("specialist")
    if specialist in TOOLS:
        if (input.get("version") != M21_VERSION or
                input.get("permitted_tool") != TOOLS[specialist] or
                observations[0].get("tool") != TOOLS[specialist]):
            raise TerminalContractError("wrong_m21_scope")
        try:
            public, visible, ref_map = model_view(input, observations)
        except (KeyError, TypeError, ValueError) as exc:
            raise TerminalContractError("unverified_projection") from None
        return public, visible, ref_map
    if (specialist not in M20_TOOLS or input.get("version") != M20_VERSION
            or input.get("permitted_tool") != M20_TOOLS[specialist]
            or observations[0].get("tool") != M20_TOOLS[specialist]):
        raise TerminalContractError("wrong_m20_scope")
    # M2.0's existing trusted selected-evidence projection is used as-is.
    return input, observations, None


def draft_request(input, observations, completed_ledger):
    public, visible, _ = _verified_view(input, observations, completed_ledger)
    body = {"model": "openai/gpt-oss-120b", "temperature": 0,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "messages": [{"role": "system", "content":
            "Return one typed evidence finding or abstain. Cite only inspected values. "
            "Never approve, waive, recalculate, reserve, or promise delivery. "
            "For finding use reason_code=none and one to six claims; for abstain "
            "return no claims and a reason_code. Use empty uncertainty_reasons "
            "for Credit, Policy and Routing. No tools are available."},
            {"role": "user", "content": _canonical({"input": public,
                "observations": visible})}],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": VERSION.replace("-", "_"), "strict": True, "schema": schema()}}}
    if len(_canonical(body).encode()) > MAX_REQUEST_BYTES:
        raise TerminalContractError("final_request_oversize")
    return body


def parse_final(response, *, input, observations, completed_ledger,
                expected_identity, checkpoint_identity):
    """Return a validated existing action; never trust a model-echoed identity."""
    if (type(expected_identity) is not dict or type(checkpoint_identity) is not dict
            or not IDENTITY_KEYS.issubset(expected_identity)
            or checkpoint_identity != expected_identity
            or any(input.get(k) != value for k, value in expected_identity.items())):
        raise TerminalContractError("source_or_checkpoint_identity")
    _, visible, ref_map = _verified_view(input, observations, completed_ledger)
    try:
        if type(response) is not dict or len(response["choices"]) != 1:
            raise ValueError()
        choice = response["choices"][0]
        message = choice["message"]
        usage = response["usage"]
        if (choice["finish_reason"] != "stop" or type(message) is not dict
                or message.get("tool_calls") or type(message.get("content")) is not str
                or len(message["content"].encode()) > MAX_RESPONSE_BYTES
                or type(usage) is not dict or type(usage.get("completion_tokens")) is not int
                or type(usage.get("prompt_tokens")) is not int
                or usage["prompt_tokens"] < 0
                or not 0 <= usage["completion_tokens"] <= MAX_COMPLETION_TOKENS):
            raise ValueError()
        raw = json.loads(message["content"])
        if (type(raw) is not dict or set(raw) != set(schema()["required"])
                or raw["version"] != VERSION or raw["kind"] not in ("finding", "abstain")
                or type(raw["claims"]) is not list or type(raw["uncertainty_reasons"]) is not list
                or raw["reason_code"] not in ("none", *REASONS)):
            raise ValueError()
        if raw["kind"] == "abstain":
            if raw["claims"] or raw["uncertainty_reasons"] or raw["reason_code"] == "none":
                raise ValueError()
            return {"kind": "abstain", "reason_code": raw["reason_code"]}
        if raw["reason_code"] != "none" or not 1 <= len(raw["claims"]) <= 6:
            raise ValueError()
        claims = []
        for claim in raw["claims"]:
            if (type(claim) is not dict or set(claim) != {"ref", "field", "value_json"}
                    or any(type(x) is not str for x in claim.values())
                    or len(claim["value_json"].encode()) > 1024):
                raise ValueError()
            value = json.loads(claim["value_json"])
            if type(value) not in (str, int, bool, type(None)):
                raise ValueError()
            claims.append({"ref": claim["ref"], "field": claim["field"], "value": value})
        if input["specialist"] in TOOLS:
            if raw["uncertainty_reasons"]:
                raise ValueError()
            exposed = {row["ref"]: row["fields"] for obs in visible for row in obs["records"]
                       if row["ref"] in obs["returned_refs"]}
            for claim in claims:
                if (claim["ref"] not in ref_map or claim["field"] not in exposed.get(
                        claim["ref"], {}) or type(claim["value"]) is not type(
                        exposed[claim["ref"]][claim["field"]]) or
                        claim["value"] != exposed[claim["ref"]][claim["field"]]):
                    raise ValueError()
                claim["ref"] = ref_map[claim["ref"]]
            _claims({"kind": "finding", "claims": claims}, observations)
            return {"kind": "finding", "claims": claims}
        action = {"kind": "finding", "claims": claims,
                  "uncertainty_reasons": raw["uncertainty_reasons"]}
        _validate_claims(action, observations, input["specialist"])
        return action
    except (KeyError, TypeError, ValueError, IndexError, UnicodeError):
        raise TerminalContractError("invalid_terminal_response") from None
