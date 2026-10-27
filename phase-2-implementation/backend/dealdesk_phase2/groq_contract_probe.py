"""Offline-only Groq chat request fixtures for a separately approved probe.

No credential, transport, assessment graph, business evidence or runtime entrypoint.
The two wires test basic inference before a required local function call.
"""

from copy import deepcopy

from .live_models import GROQ_MODEL


PROBE_VERSION = "groq-contract-probe-v1"
PROBE_ID = "GROQ-CONTRACT-PROBE-85c63f16-0c5b-4c24-bea4-1d1b79adea71"
MAX_REQUEST_BYTES = 2048
MAX_CONFIGURED_COMPLETION_TOKENS = 1536


_PLAIN = {
    "model": GROQ_MODEL,
    "messages": [{"role": "user", "content": "Reply OK."}],
    "max_completion_tokens": 512,
    "reasoning_effort": "low",
}
_TOOL = {
    "model": GROQ_MODEL,
    "messages": [
        {"role": "system", "content": "Call record_probe exactly once with status ready."},
        {"role": "user", "content": "Run the harmless compatibility probe."},
    ],
    "max_completion_tokens": 1024,
    "reasoning_effort": "low",
    "reasoning_format": "parsed",
    "parallel_tool_calls": False,
    "tool_choice": "required",
    "tools": [{"type": "function", "function": {
        "name": "record_probe", "description": "Return a harmless probe marker only.",
        "parameters": {"type": "object", "properties": {
            "status": {"type": "string", "enum": ["ready"]}},
            "required": ["status"], "additionalProperties": False}}}],
}


def request_for_stage(stage: str) -> dict:
    """Construct a fresh offline wire, never send or look up credentials."""
    if stage == "plain":
        return deepcopy(_PLAIN)
    if stage == "tool":
        return deepcopy(_TOOL)
    raise ValueError("unknown_probe_stage")
