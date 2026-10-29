"""Week 3 Groq native-tool contract; sends only via separately gated M2.1."""

import json
import os
from hashlib import sha256

from .hybrid_pack import _canonical
from .live_models import GROQ_MODEL, ProviderError, _post
from .m21_prompts import PROMPT_VERSION, system_instruction
from .m21_redaction import model_view
from .m21_specialists import TOOLS, VERSION
from .tool_response_diagnostic import ToolResponseError, rejected_category


WIRE_VERSION = "m21-groq-native-tools-v1"
MAX_REQUEST_BYTES = 8192
MAX_COMPLETION_TOKENS = 512
MAX_RESPONSE_BYTES = 16384
MAX_PROMPT_TOKENS = 4096


def request_body(input: dict, observations: tuple[dict, ...], *, exchanges=()):
    """Prepare a redacted, paired wire body; caller never supplies raw tool text."""
    if input.get("prompt_version") != PROMPT_VERSION or len(exchanges) != len(observations):
        raise ValueError("m21_groq_prompt_or_exchange_identity")
    public, visible, _ = model_view(input, observations)
    specialist = input["specialist"]
    inspect = TOOLS[specialist]
    tools = [{"type": "function", "function": {"name": inspect,
        "description": "Inspect only the scoped, pinned original evidence.",
        "parameters": {"type": "object", "properties": {
            "subject_id": {"type": "string"}}, "required": ["subject_id"],
            "additionalProperties": False}}},
        {"type": "function", "function": {"name": "submit_finding",
        "description": "Cite only exact fields of returned evidence. Never approve or waive.",
        "parameters": {"type": "object", "properties": {"claims": {"type": "array",
            "items": {"type": "object", "properties": {
                "ref": {"type": "string"}, "field": {"type": "string"},
                "value_json": {"type": "string"}},
                "required": ["ref", "field", "value_json"], "additionalProperties": False}}},
            "required": ["claims"], "additionalProperties": False}}},
        {"type": "function", "function": {"name": "abstain",
        "description": "Abstain if the exact evidence is insufficient.",
        "parameters": {"type": "object", "properties": {"reason_code": {"type": "string",
            "enum": ["insufficient_evidence", "model_uncertainty", "unsupported_capability"]}},
            "required": ["reason_code"], "additionalProperties": False}}}]
    messages = [{"role": "system", "content": system_instruction(specialist) +
        " Choose exactly one declared function; no free-text final answer. " + WIRE_VERSION +
        " " + VERSION}, {"role": "user", "content": _canonical({"input": public,
                                                                   "observations": ()})}]
    for call, observation in zip(exchanges, visible):
        try:
            call_id, name, arguments = call["id"], call["name"], call["arguments"]
            if (set(call) != {"id", "name", "arguments"} or type(call_id) is not str
                    or not 0 < len(call_id) <= 128 or name != inspect
                    or type(arguments) is not str or len(arguments.encode()) > 1024
                    or json.loads(arguments) != {"subject_id": public["subject_id"]}):
                raise ValueError()
        except (TypeError, ValueError, KeyError, UnicodeError):
            raise ValueError("m21_groq_invalid_exchange") from None
        messages.extend([{"role": "assistant", "content": None, "tool_calls": [{
            "id": call_id, "type": "function", "function": {"name": name,
                "arguments": arguments}}]}, {"role": "tool", "tool_call_id": call_id,
            "name": name, "content": _canonical(observation)}])
    body = {"model": GROQ_MODEL, "temperature": 0,
            "max_completion_tokens": MAX_COMPLETION_TOKENS,
            "parallel_tool_calls": False, "tool_choice": "required", "tools": tools,
            "messages": messages}
    if len(_canonical(body).encode()) > MAX_REQUEST_BYTES:
        raise ValueError("m21_groq_request_oversize")
    return body


def parse_response(response: dict, input: dict, observations: tuple[dict, ...]):
    """Map opaque aliases to exact returned refs; M2.1 _claims remains final authority."""
    public, visible, ref_map = model_view(input, observations)
    try:
        if (type(response) is not dict or type(response["choices"]) is not list
                or len(response["choices"]) != 1 or response["choices"][0]["finish_reason"] != "tool_calls"):
            raise ValueError()
        message = response["choices"][0]["message"]
        if type(message) is not dict:
            raise ValueError()
        calls = message["tool_calls"]
        if (message.get("content") not in (None, "") or type(calls) is not list
                or len(calls) != 1 or type(calls[0]) is not dict):
            raise ValueError()
        call = calls[0]
        if (call["type"] != "function" or type(call["id"]) is not str
                or not 0 < len(call["id"]) <= 128
                or type(call["function"]["arguments"]) is not str
                or len(call["function"]["arguments"].encode()) > 4096):
            raise ValueError()
        name = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        if type(args) is not dict:
            raise ValueError()
        if name == TOOLS[input["specialist"]] and args == {"subject_id": public["subject_id"]}:
            if observations:
                raise ValueError()
            return {"kind": "inspect", "tool": name, "subject_id": input["subject_id"]}
        if name == "abstain" and set(args) == {"reason_code"} and args["reason_code"] in (
                "insufficient_evidence", "model_uncertainty", "unsupported_capability"):
            return {"kind": "abstain", **args}
        if name == "submit_finding" and set(args) == {"claims"} and observations:
            if type(args["claims"]) is not list or not 1 <= len(args["claims"]) <= 6:
                raise ValueError()
            exposed = {row["ref"]: row["fields"] for observation in visible
                       for row in observation["records"] if row["ref"] in observation["returned_refs"]}
            claims = []
            for claim in args["claims"]:
                if (type(claim) is not dict or set(claim) != {"ref", "field", "value_json"}
                        or type(claim["ref"]) is not str or claim["ref"] not in ref_map
                        or type(claim["field"]) is not str or claim["field"] not in exposed[claim["ref"]]
                        or type(claim["value_json"]) is not str
                        or len(claim["value_json"].encode()) > 1024):
                    raise ValueError()
                value = json.loads(claim["value_json"])
                if (type(value) is not type(exposed[claim["ref"]][claim["field"]])
                        or value != exposed[claim["ref"]][claim["field"]]):
                    raise ValueError()
                claims.append({"ref": ref_map[claim["ref"]], "field": claim["field"],
                               "value": value})
            return {"kind": "finding", "claims": claims}
    except (KeyError, IndexError, TypeError, ValueError, UnicodeError):
        pass
    raise ToolResponseError(rejected_category(response, {TOOLS[input["specialist"]],
        "submit_finding", "abstain"})) from None


class GroqM21Model:
    """Bounded transport behind the M2.1 manifest/owner/reservation gate.

    The runner sets the exact request hash and exclusive owner before calling
    next_action; instantiating the adapter alone confers no send capability.
    """

    provider = "groq"
    model = GROQ_MODEL
    offline_only = False
    prompt_version = PROMPT_VERSION
    wire_version = WIRE_VERSION

    def __init__(self, specialist):
        if specialist not in TOOLS:
            raise ValueError("m21_groq_invalid_specialist")
        self.specialist = specialist
        self.previous_calls = ()
        self.pending_request_digest = None
        self.last_tool_call = None
        self.last_usage = None
        self._send_capability = None
        self._owner_directory = None
        self._assessment_id = None
        self._manifest_hash = None
        self._attempt_ordinal = None
        self._credential_sha256 = None
        self._capture_http_error = False

    def prepare_request(self, input, observations):
        if input["specialist"] != self.specialist:
            raise ValueError("m21_groq_wrong_specialist")
        return request_body(input, observations, exchanges=self.previous_calls)

    def next_action(self, input, observations):
        # No direct adapter call may bypass the checkpointed M2.1 runner.
        from .m21_specialists import _HOSTED_CAPABILITY
        if (self._send_capability is not _HOSTED_CAPABILITY or
                self._owner_directory is None or self._assessment_id != input["assessment_id"]
                or self._attempt_ordinal is None or self._manifest_hash is None
                or self._credential_sha256 is None):
            raise ProviderError("missing_hosted_authorization")
        body = self.prepare_request(input, observations)
        digest = sha256(_canonical(body).encode()).hexdigest()
        if self.pending_request_digest != digest:
            raise ProviderError("hosted_request_identity_changed")
        from .hybrid_send_reservation import claim_and_call
        key = os.environ.get("GROQ_SECONDARY_API_KEY")
        if not key or sha256(key.encode()).hexdigest() != self._credential_sha256:
            raise ProviderError("missing_credential")
        self.last_usage = None
        self.last_tool_call = None
        response = claim_and_call(self._owner_directory, assessment_id=self._assessment_id,
            start_digest=self._manifest_hash, stage="decision", ordinal=self._attempt_ordinal,
            request_digest=digest, send=lambda: _post(
                "https://api.groq.com/openai/v1/chat/completions", "Bearer " + key,
                "Authorization", body, timeout_seconds=30,
                classify_transport=True, reject_redirects=True,
                capture_http_error=self._capture_http_error))
        if len(_canonical(response).encode()) > MAX_RESPONSE_BYTES:
            raise ProviderError("provider_response_oversize")
        usage = response.get("usage")
        if (type(usage) is not dict or any(type(usage.get(k)) is not int or usage[k] < 0
                for k in ("prompt_tokens", "completion_tokens"))
                or usage["prompt_tokens"] > MAX_PROMPT_TOKENS
                or usage["completion_tokens"] > MAX_COMPLETION_TOKENS):
            raise ProviderError("hosted_usage_unverifiable")
        self.last_usage = {k: usage[k] for k in ("prompt_tokens", "completion_tokens")}
        action = parse_response(response, input, observations)
        if action["kind"] == "inspect":
            call = response["choices"][0]["message"]["tool_calls"][0]
            self.last_tool_call = {"id": call["id"], "name": call["function"]["name"],
                "arguments": call["function"]["arguments"]}
        return action
