"""Bounded opt-in HTTP error classifier; never returns arbitrary provider text.

Never log, store or return a provider body, message, arbitrary header or URL.
The hosted transport may use this only after a one-use reservation.
"""

import json
import re


MAX_ERROR_BYTES = 1024
TYPES = frozenset({"invalid_request_error", "api_error"})
CODES = frozenset({"invalid_request_error", "tool_use_failed", "json_validate_failed"})
PARAMS = frozenset({"messages", "tools", "tool_choice", "max_completion_tokens",
                    "messages[2].tool_calls", "messages[3].tool_call_id"})
REQUEST_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")


def _allowed(value, choices):
    return value if type(value) is str and value in choices else "unknown"


def safe_fields(diagnostic):
    """Fields eligible for a failed receipt; reject unrecognized input shape."""
    if type(diagnostic) is not dict or set(diagnostic) != {
            "type", "code", "param", "request_id"}:
        return {}
    fields = {name: diagnostic[name] for name, choices in (
        ("type", TYPES), ("code", CODES), ("param", PARAMS))
        if type(diagnostic[name]) is str and diagnostic[name] in choices}
    identifier = diagnostic["request_id"]
    if type(identifier) is str and REQUEST_ID.fullmatch(identifier):
        fields["request_id"] = identifier
    return fields


def classify_error(stream, headers=None):
    """Return only fixed allowlisted categories from a bounded mockable stream.

    Caller owns and closes the response. Read/parse failure leaves no partial
    provider data in the result, and this function never changes send status.
    """
    result = {"type": "unknown", "code": "unknown", "param": "unknown",
              "request_id": None}
    try:
        raw = stream.read(MAX_ERROR_BYTES + 1)
        if type(raw) is not bytes or len(raw) > MAX_ERROR_BYTES:
            return result
        value = json.loads(raw)
        if type(value) is not dict or type(value.get("error")) is not dict:
            return result
        error = value["error"]
        result["type"] = _allowed(error.get("type"), TYPES)
        result["code"] = _allowed(error.get("code"), CODES)
        result["param"] = _allowed(error.get("param"), PARAMS)
        # Only the documented header name is considered; never persist any
        # other header. Restrict IDs to canonical lowercase UUIDs.
        identifier = headers.get("x-request-id") if headers is not None else None
        if type(identifier) is str and REQUEST_ID.fullmatch(identifier):
            result["request_id"] = identifier
    except (OSError, TimeoutError, ValueError, UnicodeError, TypeError, AttributeError):
        return {"type": "unknown", "code": "unknown", "param": "unknown",
                "request_id": None}
    return result
