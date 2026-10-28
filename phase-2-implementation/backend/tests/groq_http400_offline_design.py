"""Mock-only design fixtures. No transport, credentials, runtime hook or approval.

Provider tool-call IDs in these fixtures are fabricated for offline assertions;
any future hosted continuation MUST use the actual first-turn returned call.
This proposed retention parser is NOT connected to the production classifier.
"""

import json
from io import BytesIO

from dealdesk_phase2.groq_error_diagnostic import REQUEST_ID, safe_fields


PROPOSED_ERROR_BYTES = 4096
INSPECT = "inspect_synthetic_record"
SUBMIT = "submit_synthetic_result"
CALL_ID = "call_offline_fixture_only"
NEUTRAL = {"record_key": "SYN-1", "signal": "amber"}
DOMAIN_LIKE = {"record_key": "SYN-1", "margin_band": "review",
               "credit_band": "review"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def synthetic_body(*, continuation=False, named=True, complex_schema=False,
                   domain_like=False, tool_choice="required"):
    """One-factor-at-a-time mock wire; never contains business/evaluation rows."""
    if tool_choice not in ("required", "auto"):
        raise ValueError("unapproved_mock_tool_choice")
    inspect = {"type": "object", "properties": {"record_key": {"type": "string",
        "enum": ["SYN-1"]}}, "required": ["record_key"], "additionalProperties": False}
    submit = {"type": "object", "properties": {"result": {"type": "string"}},
              "required": ["result"], "additionalProperties": False}
    if complex_schema:
        submit = {"type": "object", "properties": {"result": {"type": "string"},
            "checks": {"type": "array", "items": {"type": "object",
                "properties": {"kind": {"type": "string", "enum": ["signal", "gap"]},
                               "observed": {"type": "boolean"}},
                "required": ["kind", "observed"], "additionalProperties": False}}},
            "required": ["result", "checks"], "additionalProperties": False}
    tools = [{"type": "function", "function": {"name": name,
        "description": description, "parameters": parameters}} for name, description, parameters in (
        (INSPECT, "Read one fictional record", inspect),
        (SUBMIT, "Report a fictional signal", submit))]
    messages = [{"role": "system", "content": "Use fictional tools only; never approve anything."},
                {"role": "user", "content": "Inspect SYN-1, then report its signal using a tool."}]
    if continuation:
        call = {"id": CALL_ID, "type": "function", "function": {"name": INSPECT,
                "arguments": canonical({"record_key": "SYN-1"})}}
        result = {"role": "tool", "tool_call_id": CALL_ID,
                  "content": canonical(DOMAIN_LIKE if domain_like else NEUTRAL)}
        if named:
            result["name"] = INSPECT
        messages.extend([{"role": "assistant", "content": None,
                          "tool_calls": [call]}, result])
    return {"model": "openai/gpt-oss-120b", "messages": messages, "tools": tools,
            "tool_choice": tool_choice, "temperature": 0,
            "max_completion_tokens": 512, "parallel_tool_calls": False}


def proposed_error_projection(stream, headers=None):
    """Mock-only 4096+1 byte draft, with fixed LOCAL outcomes and no body output.

    Caller owns the stream. Proposed headers are only examined for an exact
    UUID x-request-id; no claim that Groq supplies it on failures.
    """
    identifier = headers.get("x-request-id") if type(headers) is dict else None
    safe_id = (identifier if type(identifier) is str and REQUEST_ID.fullmatch(identifier)
               else None)
    diagnostic = {"request_id": safe_id} if safe_id else {}
    data = bytearray()
    try:
        while len(data) <= PROPOSED_ERROR_BYTES:
            piece = stream.read(PROPOSED_ERROR_BYTES + 1 - len(data))
            if type(piece) is not bytes:
                return {"local_state": "malformed", "diagnostic": diagnostic}
            if not piece:
                break
            data.extend(piece)
        if len(data) > PROPOSED_ERROR_BYTES:
            return {"local_state": "oversize", "diagnostic": diagnostic}
        value = json.loads(data)
        if type(value) is not dict or type(value.get("error")) is not dict:
            return {"local_state": "malformed", "diagnostic": diagnostic}
        error = value["error"]
        allowed = safe_fields({"type": error.get("type"), "code": error.get("code"),
                               "param": error.get("param"), "request_id": safe_id})
        diagnostic.update(allowed)
        provider_category = any(key in allowed for key in ("type", "code", "param"))
        return {"local_state": "parsed_allowlisted" if provider_category else
                "parsed_unrecognized", "diagnostic": diagnostic}
    except (TimeoutError, OSError):
        return {"local_state": "read_timeout", "diagnostic": diagnostic}
    except (ValueError, UnicodeError, TypeError):
        return {"local_state": "malformed", "diagnostic": diagnostic}


def mocked_error_bytes(*, message_size=0, error_type="invalid_request_error"):
    """Synthetic-only response generator, never a provider response."""
    return BytesIO(canonical({"error": {"type": error_type,
        "message": "x" * message_size}}).encode())
