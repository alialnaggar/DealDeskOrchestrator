"""Dormant Week 3 Groq native-tool wire; no credential or HTTP access.

A future separately authorized runner must own request reservations, ledger
pairing, account gates and terminal no-replay before calling shared _post.
"""

import json

from .hybrid_pack import _canonical
from .live_models import GROQ_MODEL
from .m21_prompts import PROMPT_VERSION, system_instruction
from .m21_redaction import model_view
from .m21_specialists import TOOLS, VERSION


WIRE_VERSION = "m21-groq-native-tools-v1"
MAX_REQUEST_BYTES = 8192
MAX_COMPLETION_TOKENS = 512


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
        calls = message["tool_calls"]
        if (message.get("content") not in (None, "") or type(calls) is not list
                or len(calls) != 1):
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
    raise ValueError("m21_groq_invalid_response") from None
