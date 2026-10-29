"""Fixed, non-content-bearing categories for rejected native-tool responses.

This never accepts a response or records provider text. The domain parser
remains the sole authority for turning a response into an action.
"""

import json


CATEGORIES = frozenset({"envelope", "finish_reason", "message_content",
    "tool_count", "tool_metadata", "unsupported_tool", "arguments_json",
    "action_arguments"})


class ToolResponseError(ValueError):
    def __init__(self, category):
        if category not in CATEGORIES:
            raise ValueError("invalid_tool_response_category")
        self.category = category
        super().__init__("invalid_native_tool_response")


def rejected_category(response, allowed_tools):
    """Classify only the rejected *shape*; never include field values or text."""
    if (type(response) is not dict or type(response.get("choices")) is not list
            or len(response["choices"]) != 1 or
            type(response["choices"][0]) is not dict):
        return "envelope"
    choice = response["choices"][0]
    if choice.get("finish_reason") != "tool_calls":
        return "finish_reason"
    message = choice.get("message")
    if type(message) is not dict:
        return "envelope"
    if message.get("content") not in (None, ""):
        return "message_content"
    calls = message.get("tool_calls")
    if type(calls) is not list or len(calls) != 1:
        return "tool_count"
    call = calls[0]
    if (type(call) is not dict or call.get("type") != "function"
            or type(call.get("id")) is not str or not 0 < len(call["id"]) <= 128
            or type(call.get("function")) is not dict):
        return "tool_metadata"
    function = call["function"]
    if type(function.get("name")) is not str or function["name"] not in allowed_tools:
        return "unsupported_tool"
    arguments = function.get("arguments")
    if type(arguments) is not str or len(arguments.encode()) > 4096:
        return "arguments_json"
    try:
        if type(json.loads(arguments)) is not dict:
            return "arguments_json"
    except (ValueError, UnicodeError):
        return "arguments_json"
    return "action_arguments"
