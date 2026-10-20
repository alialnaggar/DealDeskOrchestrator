"""Explicit, bounded M1.4 provider connectivity probes; never prints credentials."""

import argparse
from datetime import datetime, timezone
import json
import os
import re
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GROQ_MODEL = "openai/gpt-oss-120b"
GEMINI_MODEL = "gemini-3.8-flash"
GROQ_ROOT = "https://api.groq.com/openai/v1"
GEMINI_ROOT = "https://generativelanguage.googleapis.com/v1beta"
MAX_RESPONSE_BYTES = 8192


def _safe_message(value, key):
    if not isinstance(value, str):
        return None
    value = value.replace(key, "[REDACTED]")
    value = re.sub(r"(?i)bearer\s+\S+|AIza[\w-]+|gsk_[\w-]+", "[REDACTED]", value)
    value = re.sub(r"[\x00-\x1f\x7f]", " ", value)
    return value[:400]


def _safe_header(value):
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", value) else None


def _error_details(raw, key):
    try:
        body = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        body = None
    if not isinstance(body, dict) or not isinstance(body.get("error"), dict):
        return {"body_kind": "non_json_or_no_error", "message": _safe_message(raw.decode("utf-8", "replace"), key)}
    error = body["error"]
    return {"body_kind": "json_error", "code": error.get("code") if isinstance(error.get("code"), int) else _safe_header(error.get("code")),
            "type": _safe_header(error.get("type")), "status": _safe_header(error.get("status")),
            "message": _safe_message(error.get("message"), key)}


def _request(provider, phase, method, url, key, body=None, *, max_attempts=1):
    header = "Authorization" if provider == "groq" else "x-goog-api-key"
    auth = "Bearer " + key if provider == "groq" else key
    payload = json.dumps(body, separators=(",", ":")).encode() if body is not None else None
    if payload is not None and len(payload) > 2048:
        raise ValueError("Diagnostic request exceeded 2 KB")
    attempts = []
    for attempt in range(max_attempts):
        if attempt:
            sleep(4 * attempt)
        request = Request(url, data=payload, headers={header: auth, "Content-Type": "application/json",
                          "User-Agent": "DealDeskOrchestrator-thesis-M1.4/1.0"}, method=method)
        start = monotonic()
        entry = {"provider": provider, "phase": phase, "attempt": attempt + 1,
                 "timestamp_utc": datetime.now(timezone.utc).isoformat()}
        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                headers = response.headers
                entry["status"] = response.status
            if len(raw) > MAX_RESPONSE_BYTES:
                entry["result"] = "response_too_large"
            else:
                try:
                    data = json.loads(raw)
                except (ValueError, UnicodeDecodeError):
                    data = None
                entry["result"] = _interpret(provider, phase, data)
        except HTTPError as exc:
            headers = exc.headers
            raw = exc.read(MAX_RESPONSE_BYTES)
            entry["status"] = exc.code
            entry["error"] = _error_details(raw, key)
        except (URLError, TimeoutError, OSError):
            headers = {}
            entry["status"] = None
            entry["error"] = {"body_kind": "transport_failure"}
        entry["latency_ms"] = round((monotonic() - start) * 1000)
        entry["request_ids"] = {name: value for name in
            ("x-request-id", "x-groq-request-id", "x-goog-request-id", "x-cloud-trace-context")
            if (value := _safe_header(headers.get(name)))}
        attempts.append(entry)
        # Only a transient 503 is retried; 403 and all other errors stop.
        if entry["status"] != 503:
            break
    return attempts


def _interpret(provider, phase, data):
    if not isinstance(data, dict):
        return "invalid_json_shape"
    if phase == "metadata":
        ids = ({data.get("id")} | {x.get("id") for x in data.get("data", []) if isinstance(x, dict)}) if provider == "groq" else {data.get("name")}
        expected = GROQ_MODEL if provider == "groq" else "models/" + GEMINI_MODEL
        return "model_present" if expected in ids else "model_absent"
    if provider == "groq":
        choices = data.get("choices") or []
        return "text_present" if choices and isinstance(choices[0].get("message", {}).get("content"), str) else "no_text"
    candidates = data.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    if phase == "tool":
        return "expected_tool_call" if any(p.get("functionCall", {}).get("name") == "inspect_line_supply" for p in parts) else "no_expected_tool_call"
    if phase == "structured":
        try:
            parsed = json.loads("".join(p.get("text", "") for p in parts))
        except ValueError:
            return "invalid_structured_json"
        return "valid_structured_json" if parsed == {"status": "ok"} else "unexpected_structured_value"
    return "text_present" if any(isinstance(p.get("text"), str) and p["text"] for p in parts) else "no_text"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--provider", choices=("all", "gemini"), default="all")
    parser.add_argument("--require-success", action="store_true",
                        help="Exit nonzero unless all selected capability probes succeed")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    keys = {provider: os.environ.get(env) for provider, env in
            (("groq", "GROQ_API_KEY"), ("gemini", "GEMINI_API_KEY"))}
    if not all(keys.values()):
        parser.error("Both provider secrets must be present")
    records = []
    groq_key, gemini_key = keys["groq"], keys["gemini"]
    if args.provider == "all":
        records += _request("groq", "metadata", "GET", GROQ_ROOT + "/models/" + GROQ_MODEL, groq_key)
        records += _request("groq", "generation", "POST", GROQ_ROOT + "/chat/completions", groq_key,
                            {"model": GROQ_MODEL, "messages": [{"role": "user", "content": "Reply OK."}],
                             "temperature": 0, "max_completion_tokens": 32})
    records += _request("gemini", "metadata", "GET", GEMINI_ROOT + "/models/" + GEMINI_MODEL, gemini_key)
    endpoint = GEMINI_ROOT + "/models/" + GEMINI_MODEL + ":generateContent"
    base = {"contents": [{"parts": [{"text": "Reply OK."}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 128}}
    records += _request("gemini", "generation", "POST", endpoint, gemini_key, base, max_attempts=2)
    if any(r["status"] == 429 for r in records):
        _finish(records, args.output, args.require_success)
        return
    sleep(15)
    structured = {"contents": [{"parts": [{"text": "Return a JSON object with status ok."}]}],
                  "generationConfig": {"temperature": 0, "maxOutputTokens": 128,
                      "responseMimeType": "application/json",
                      "responseSchema": {"type": "object", "properties": {"status": {"type": "string", "enum": ["ok"]}},
                                         "required": ["status"]}}}
    records += _request("gemini", "structured", "POST", endpoint, gemini_key, structured, max_attempts=2)
    if any(r["status"] == 429 for r in records):
        _finish(records, args.output, args.require_success)
        return
    sleep(15)
    tool = {"contents": [{"parts": [{"text": "Call inspect_line_supply for line_id smoke-line."}]}],
            "tools": [{"functionDeclarations": [{"name": "inspect_line_supply", "description": "Read a test line",
                "parameters": {"type": "object", "properties": {"line_id": {"type": "string"}}, "required": ["line_id"]}}]}],
            "toolConfig": {"functionCallingConfig": {"mode": "ANY"}},
            "generationConfig": {"temperature": 0, "maxOutputTokens": 128}}
    records += _request("gemini", "tool", "POST", endpoint, gemini_key, tool, max_attempts=2)
    # The tool declaration is only a connectivity probe. No local business tool is executed.
    _finish(records, args.output, args.require_success)


def _finish(records, output, require_success):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)
    for entry in records:
        print(json.dumps(entry, sort_keys=True), flush=True)
    if require_success:
        expected = {"metadata": "model_present", "generation": "text_present",
                    "structured": "valid_structured_json", "tool": "expected_tool_call"}
        selected = {r["phase"]: r for r in records if r["provider"] == "gemini"}
        if any(selected.get(phase, {}).get("result") != result or
               selected[phase].get("status") != 200 for phase, result in expected.items()):
            raise SystemExit("Gemini capability probes did not pass; eligible smoke gated")


if __name__ == "__main__":
    main()
