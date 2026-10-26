"""Provider-independent hybrid wire contract and offline Groq serialization.

No HTTP client, credential lookup or runtime activation in this module. The
existing iterative Groq adapter and its READY behavior are left untouched.
"""

from copy import deepcopy
from typing import Protocol
import json

from .hybrid_contracts import ACTION_VERSION, HybridContractError, decision, final
from .live_models import CLAIM_SCHEMA, GROQ_MODEL, TOOL_PARAMETERS


WIRE_VERSION = "hybrid-groq-wire-v1"


class HybridWireAdapter(Protocol):
    provider: str
    model: str

    def decision_request(self, input: dict, observations: tuple[dict, ...]) -> dict: ...
    def final_request(self, intent: dict, input: dict, observations: tuple[dict, ...],
                      feedback: dict | None = None) -> dict: ...
    def parse_decision(self, response: dict, line_id: str,
                       tools: tuple[str, ...]) -> dict: ...
    def parse_final(self, response: dict, intent: dict) -> dict: ...


def _message(response):
    try:
        if not isinstance(response, dict) or len(response["choices"]) != 1:
            raise ValueError()
        choice = response["choices"][0]
        if choice.get("finish_reason") not in ("tool_calls", "stop"):
            raise ValueError()
        message = choice["message"]
        if not isinstance(message, dict):
            raise ValueError()
        return message, choice["finish_reason"]
    except (KeyError, TypeError, ValueError, IndexError):
        raise HybridContractError("invalid_groq_response") from None


def _json_payload(message):
    try:
        content = message["content"]
        if not isinstance(content, str) or len(content.encode()) > 16384:
            raise ValueError()
        return json.loads(content)
    except (KeyError, TypeError, ValueError):
        raise HybridContractError("invalid_groq_json") from None


def _schema(kind):
    if kind == "submit_proposal":
        payload = {"type": "object", "properties": {
            "line_id": {"type": "string"}, "tradeoff_code": {"type": "string"},
            "delivery_slices": {"type": "array", "items": {"type": "object",
                "properties": {"quantity": {"type": "string"},
                    "delivery_date": {"type": "string"}, "source_refs": {
                        "type": "array", "items": {"type": "string"}}},
                "required": ["quantity", "delivery_date", "source_refs"],
                "additionalProperties": False}}},
            "required": ["line_id", "tradeoff_code", "delivery_slices"],
            "additionalProperties": False}
    elif kind == "submit_finding":
        # Claim semantics are enforced by the shared M1.6 validator, not JSON schema.
        payload = {"type": "object", "properties": {"line_id": {"type": "string"},
            "claims": {"type": "array", "items": deepcopy(CLAIM_SCHEMA)},
            "uncertainty_reasons": {"type": "array", "items": {"type": "string"}}},
            "required": ["line_id", "claims", "uncertainty_reasons"],
            "additionalProperties": False}
    else:
        payload = {"type": "object", "properties": {
            "reason_code": {"type": "string"}, "scope": {"type": "string"},
            "missing_evidence": {"type": "array", "items": {"type": "string"}}},
            "required": ["reason_code", "scope", "missing_evidence"],
            "additionalProperties": False}
    return {"type": "object", "properties": {
        "version": {"type": "string", "enum": [ACTION_VERSION]},
        "kind": {"type": "string", "enum": [kind]}, "payload": payload},
        "required": ["version", "kind", "payload"], "additionalProperties": False}


class GroqHybridAdapter:
    provider = "groq"
    model = GROQ_MODEL
    wire_version = WIRE_VERSION

    def decision_request(self, input, observations):
        tools = []
        for name in input["permitted_tools"]:
            parameters = deepcopy(TOOL_PARAMETERS[name])
            parameters["properties"]["purpose_code"] = {"type": "string", "enum": [
                "check_dated_path", "inspect_source", "check_line_supply"]}
            parameters["required"].append("purpose_code")
            parameters["additionalProperties"] = False
            tools.append({"type": "function", "function": {"name": name,
                "description": "Read scoped pinned evidence only", "parameters": parameters}})
        for name in ("submit_proposal", "submit_finding", "abstain"):
            parameters = {"type": "object", "properties": {}, "required": [],
                          "additionalProperties": False}
            if name == "submit_proposal":
                parameters = {"type": "object", "properties": {"submission_kind": {
                    "type": "string", "enum": ["binding_partial_delivery"]}},
                    "required": ["submission_kind"], "additionalProperties": False}
            tools.append({"type": "function", "function": {"name": name,
                "description": "Record explicit submission intent; final is separate",
                "parameters": parameters}})
        return {"model": self.model, "temperature": 0, "max_completion_tokens": 1024,
            "parallel_tool_calls": False, "tool_choice": "required", "tools": tools,
            "messages": [{"role": "system", "content":
                WIRE_VERSION + ". Choose exactly one authorized function. Never return READY. "
                "Only returned records may be cited; supplier offers are not confirmed. "
                "A submit call is intent only; it carries no proposed answer."},
                {"role": "user", "content": json.dumps({"input": input,
                    "observations": observations}, sort_keys=True, default=list)}]}

    def final_request(self, intent, input, observations, feedback=None):
        if intent.get("kind") not in ("submit_proposal", "submit_finding", "abstain"):
            raise HybridContractError("invalid_submission_intent")
        if feedback is not None and intent["kind"] != "submit_proposal":
            raise HybridContractError("invalid_revision_intent")
        return {"model": self.model, "temperature": 0, "max_completion_tokens": 2048,
            "messages": [{"role": "system", "content": WIRE_VERSION +
                ". Return only the structured final for the saved intent. No tools, "
                "no approval, stock reservation or delivery promise. Proposals must use "
                "canonical whole-unit ASCII quantities; Phase 1C alone verifies supply."},
                {"role": "user", "content": json.dumps({"input": input,
                    "observations": observations, "intent": intent,
                    "feedback": feedback}, sort_keys=True, default=list)}],
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "hybrid_fulfillment_final_v1", "strict": True,
                "schema": _schema(intent["kind"])}}}

    def parse_decision(self, response, line_id, tools):
        message, reason = _message(response)
        calls = message.get("tool_calls")
        if (reason != "tool_calls" or not isinstance(calls, list) or len(calls) != 1
                or message.get("content") not in (None, "")):
            raise HybridContractError("invalid_groq_action")
        try:
            name = calls[0]["function"]["name"]
            args = json.loads(calls[0]["function"]["arguments"])
            if not isinstance(args, dict):
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise HybridContractError("invalid_groq_action") from None
        if name in ("submit_proposal", "submit_finding", "abstain"):
            action = {"version": ACTION_VERSION, "kind": name, **args}
        else:
            action = {"version": ACTION_VERSION, "kind": "inspect", "tool_name": name,
                      "arguments": {k: v for k, v in args.items() if k != "purpose_code"},
                      "purpose_code": args.get("purpose_code")}
        return decision(action, line_id=line_id, permitted_tools=tools)

    def parse_final(self, response, intent):
        message, reason = _message(response)
        if reason != "stop" or message.get("tool_calls"):
            raise HybridContractError("invalid_groq_final")
        return final(_json_payload(message), intent)


class OfflineGroqWireDouble:
    """Adapter exercised end-to-end with supplied response fixtures, never HTTP."""
    provider = "offline_double"
    offline_only = True
    model = "groq-wire-double-v1"

    def __init__(self, responses, adapter=None):
        self.responses = list(responses)
        self.adapter = adapter or GroqHybridAdapter()
        self.wire_adapter = self.adapter
        self.requests = []

    def _take(self, body):
        self.requests.append(body)
        if not self.responses:
            raise HybridContractError("offline_wire_exhausted")
        return self.responses.pop(0)

    def request_decision(self, input, observations):
        return self.adapter.decision_request({**input, "permitted_tools": (
            "inspect_line_supply", "inspect_fulfillment_paths", "inspect_evidence_record")},
            observations)

    def decide(self, input, observations):
        return self._take(self.request_decision(input, observations))

    def request_final(self, intent, input, observations):
        return self.adapter.final_request(intent, input, observations)

    def submit(self, intent, input, observations):
        return self._take(self.request_final(intent, input, observations))

    def request_revision_intent(self, feedback, input, observations):
        body = self.adapter.decision_request({**input, "permitted_tools": ()}, observations)
        body["tools"] = [x for x in body["tools"] if x["function"]["name"] in (
            "submit_proposal", "abstain")]
        body["messages"][0]["content"] += " Revision intent: submit a new full proposal or abstain; no inspections."
        return body

    def revision_intent(self, feedback, input, observations):
        return self._take(self.request_revision_intent(feedback, input, observations))

    def request_revision(self, intent, feedback, input, observations):
        return self.adapter.final_request(intent, input, observations, feedback)

    def revise(self, intent, feedback, input, observations):
        return self._take(self.request_revision(intent, feedback, input, observations))


class GroqHybridTransportModel(OfflineGroqWireDouble):
    """Dormant real transport; the default offline runner refuses this model.

    No retry, fallback or credential lookup until the separately authorized
    evaluation entrypoint calls a stage after its durable send reservation.
    """
    provider = "groq"
    offline_only = False
    model = GROQ_MODEL

    def __init__(self, adapter=None):
        super().__init__([], adapter)
        self.model = self.adapter.model

    # Only the separately gated hosted smoke uses these smaller ceilings.
    def request_decision(self, input, observations):
        body = super().request_decision(input, observations)
        body["max_completion_tokens"] = 512
        return body

    def request_final(self, intent, input, observations):
        body = super().request_final(intent, input, observations)
        body["max_completion_tokens"] = 1024
        return body

    def request_revision_intent(self, feedback, input, observations):
        raise HybridContractError("hosted_revision_disabled")

    def request_revision(self, intent, feedback, input, observations):
        raise HybridContractError("hosted_revision_disabled")

    def _take(self, body):
        import os
        from .live_models import _post, ProviderError

        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise ProviderError("missing_credential")
        self.requests.append(body)
        return _post("https://api.groq.com/openai/v1/chat/completions",
                     "Bearer " + key, "Authorization", body,
                     timeout_seconds=30, classify_transport=True)
