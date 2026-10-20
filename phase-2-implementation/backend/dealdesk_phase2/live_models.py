"""Opt-in Groq/Gemini REST adapters for the M1.3 investigation protocol.

Only model-selected local function calls cross into M1.2's trusted adapter.
No provider has database access. Both use a separate structured final turn.
"""

from dataclasses import asdict
from hashlib import sha256
import json
import os
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import model_attempts


GROQ_MODEL = "openai/gpt-oss-120b"
GEMINI_MODEL = "gemini-3.8-flash"
MAX_OUTPUT_TOKENS = 2048
MAX_PROMPT_BYTES = 20000
MAX_MODEL_TURNS = 6


class ProviderError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _post(url: str, key: str, header: str, body: dict) -> dict:
    payload = _json(body).encode("utf-8")
    if len(payload) > MAX_PROMPT_BYTES:
        raise ProviderError("request_too_large")
    request = Request(url, payload, {"Content-Type": "application/json", header: key}, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        # Error bodies can echo request content and must not enter logs/checkpoints.
        raise ProviderError("http_" + str(exc.code)) from None
    except (URLError, TimeoutError, OSError):
        raise ProviderError("transport_failure") from None
    except (ValueError, TypeError):
        raise ProviderError("invalid_provider_json") from None


TOOL_PARAMETERS = {
    "inspect_line_supply": {"type": "object", "properties": {"line_id": {"type": "string"},
        "horizon": {"type": "string"}}, "required": ["line_id"]},
    "inspect_fulfillment_paths": {"type": "object", "properties": {"line_id": {"type": "string"},
        "horizon": {"type": "string"}}, "required": ["line_id"]},
    "inspect_evidence_record": {"type": "object", "properties": {"line_id": {"type": "string"},
        "source_category": {"type": "string"}, "source_id": {"type": "string"}},
        "required": ["line_id", "source_category", "source_id"]},
}

FINAL_SCHEMA = {"type": "object", "properties": {
    "kind": {"type": "string", "enum": ["proposal", "finding_without_proposal", "abstention"]},
    "line_id": {"type": "string"},
    "delivery_slices": {"type": "array", "items": {"type": "object", "properties": {
        "quantity": {"type": "string"}, "delivery_date": {"type": "string"},
        "commitment_claim": {"type": "string", "enum": ["conditional", "unknown"]}},
        "required": ["quantity", "delivery_date", "commitment_claim"], "additionalProperties": False}},
    "citations": {"type": "array", "items": {"type": "string"}},
    "tradeoffs": {"type": "array", "items": {"type": "string"}},
    "assumptions": {"type": "array", "items": {"type": "string"}},
    "unmet_requirements": {"type": "array", "items": {"type": "string"}},
    "uncertainty_reasons": {"type": "array", "items": {"type": "string"}},
    "finding": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["kind", "line_id", "delivery_slices", "citations", "tradeoffs",
                 "assumptions", "unmet_requirements", "uncertainty_reasons", "finding", "reason"],
    "additionalProperties": False}


def _canonical_final(raw):
    if not isinstance(raw, dict) or set(raw) != set(FINAL_SCHEMA["required"]):
        raise ProviderError("malformed_final")
    kind = raw["kind"]
    if kind == "proposal":
        fields = ("line_id", "delivery_slices", "citations", "tradeoffs", "assumptions",
                  "unmet_requirements", "uncertainty_reasons")
    elif kind == "finding_without_proposal":
        fields = ("line_id", "finding", "citations", "uncertainty_reasons")
    elif kind == "abstention":
        fields = ("reason", "uncertainty_reasons")
    else:
        raise ProviderError("malformed_final")
    return {"type": "contribution", "value": {"kind": kind,
            "payload": {field: raw[field] for field in fields}}}


def _prompt(input, observations):
    safe = {key: value for key, value in asdict(input).items()
            if key not in ("assessment_id", "phase1c_run_id", "subject_id",
                           "bundle_sha256", "source_input_digest")}
    return ("You investigate a fulfillment shortage. Only tool responses are citable; "
            "their returned_refs are source-category:source-id. Supplier offers are conditional, "
            "never confirmed. An empty bounded pool does not prove no supply exists. "
            "Never approve, reserve or promise. You may abstain or report a finding. "
            "First choose one authorized local tool when useful; if ready for final output, "
            "say READY. For a final proposal, use only conditional/unknown slices, and "
            "never claim it was fixed-rule verified. Input and observations: " +
            _json({"input": safe, "observations": observations}))


class LiveInvestigationModel:
    def __init__(self, provider: str, graph, config, *, pace_seconds: float = 0):
        if provider not in ("groq", "gemini"):
            raise ValueError("Unknown benchmark provider")
        self.provider = provider
        self.model = GROQ_MODEL if provider == "groq" else GEMINI_MODEL
        self.graph, self.config = graph, config
        self.pace_seconds = pace_seconds
        self._last_sent = None

    def _request(self, input, step: int, phase: str, body: dict):
        key_name = "GROQ_API_KEY" if self.provider == "groq" else "GEMINI_API_KEY"
        key = os.environ.get(key_name)
        if not key:
            raise ProviderError("missing_credential")
        url = ("https://api.groq.com/openai/v1/chat/completions" if self.provider == "groq"
               else "https://generativelanguage.googleapis.com/v1beta/models/"
                    + self.model + ":generateContent")
        header = "Authorization" if self.provider == "groq" else "x-goog-api-key"
        auth = "Bearer " + key if self.provider == "groq" else key
        digest = sha256(_json(body).encode()).hexdigest()
        attempt_id = sha256(f"{input.assessment_id}:{input.bundle_sha256}:"
                            f"{self.provider}:{self.model}:{step}:{phase}".encode()).hexdigest()
        prior = model_attempts.reserve(self.graph, self.config, input, attempt_id,
                                       self.provider, self.model, digest)
        if prior:
            return prior["action"]
        start = monotonic()
        try:
            if self._last_sent is not None and self.pace_seconds:
                sleep(max(0, self.pace_seconds - (monotonic() - self._last_sent)))
            self._last_sent = monotonic()
            response = _post(url, auth, header, body)
            action, usage, response_model = self._parse(response, phase)
            model_attempts.complete(self.graph, self.config, input, attempt_id,
                                    status="completed", action=action, usage=usage,
                                    response_model=response_model,
                                    latency_ms=round((monotonic() - start) * 1000))
            return action
        except Exception as exc:
            code = exc.code if isinstance(exc, ProviderError) else "invalid_provider_response"
            model_attempts.complete(self.graph, self.config, input, attempt_id,
                                    status="error", action=None, usage={}, error_code=code,
                                    response_model=None,
                                    latency_ms=round((monotonic() - start) * 1000))
            raise ProviderError(code) from None

    def next_action(self, input, observations):
        step = len(observations)
        if step >= MAX_MODEL_TURNS:
            raise ProviderError("model_turn_budget_exhausted")
        prompt = _prompt(input, observations)
        if self.provider == "groq":
            tools = [{"type": "function", "function": {"name": name,
                      "description": "Read only pinned Fulfillment evidence",
                      "parameters": TOOL_PARAMETERS[name]}}
                     for name in input.permitted_tools]
            decision = {"model": self.model, "temperature": 0, "max_completion_tokens": 1024,
                        "parallel_tool_calls": False, "tool_choice": "auto", "tools": tools,
                        "messages": [{"role": "system", "content": "Choose at most one local tool or say READY."},
                                     {"role": "user", "content": prompt}]}
        else:
            declarations = [{"name": name, "description": "Read only pinned Fulfillment evidence",
                             "parameters": TOOL_PARAMETERS[name]}
                            for name in input.permitted_tools]
            decision = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "tools": [{"functionDeclarations": declarations}],
                        "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}},
                        "generationConfig": {"temperature": 0, "maxOutputTokens": 1024}}
        first = self._request(input, step, "decision", decision)
        if first["type"] == "tool":
            return first
        final_prompt = prompt + "\nReturn the final JSON under the specified schema now; no tool call."
        if self.provider == "groq":
            final = {"model": self.model, "temperature": 0,
                     "max_completion_tokens": MAX_OUTPUT_TOKENS,
                     "messages": [{"role": "system", "content": "Output the evidence-limited JSON assessment."},
                                  {"role": "user", "content": final_prompt}],
                     "response_format": {"type": "json_schema", "json_schema": {
                         "name": "fulfillment_contribution", "strict": True, "schema": FINAL_SCHEMA}}}
        else:
            final = {"contents": [{"role": "user", "parts": [{"text": final_prompt}]}],
                     "generationConfig": {"temperature": 0,
                         "maxOutputTokens": MAX_OUTPUT_TOKENS,
                         "responseMimeType": "application/json", "responseSchema": FINAL_SCHEMA}}
        return self._request(input, step, "final", final)

    def _parse(self, response: dict, phase: str):
        if self.provider == "groq":
            choice = response["choices"][0]["message"]
            calls = choice.get("tool_calls") or []
            if phase == "decision" and calls:
                if len(calls) != 1:
                    raise ProviderError("multiple_tool_calls")
                function = calls[0]["function"]
                action = {"type": "tool", "tool": function["name"],
                          "arguments": json.loads(function["arguments"])}
            elif phase == "decision":
                action = {"type": "ready"}
            else:
                action = _canonical_final(json.loads(choice["content"]))
            usage = response.get("usage") or {}
            return action, {"input_tokens": usage.get("prompt_tokens"),
                            "output_tokens": usage.get("completion_tokens")}, response.get("model")
        candidate = response["candidates"][0]
        parts = candidate["content"]["parts"]
        calls = [p["functionCall"] for p in parts if "functionCall" in p]
        if phase == "decision" and calls:
            if len(calls) != 1:
                raise ProviderError("multiple_tool_calls")
            action = {"type": "tool", "tool": calls[0]["name"],
                      "arguments": calls[0].get("args", {})}
        elif phase == "decision":
            action = {"type": "ready"}
        else:
            action = _canonical_final(json.loads("".join(p.get("text", "") for p in parts)))
        usage = response.get("usageMetadata") or {}
        return action, {"input_tokens": usage.get("promptTokenCount"),
                        "output_tokens": usage.get("candidatesTokenCount"),
                        "total_tokens": usage.get("totalTokenCount")}, response.get("modelVersion")
