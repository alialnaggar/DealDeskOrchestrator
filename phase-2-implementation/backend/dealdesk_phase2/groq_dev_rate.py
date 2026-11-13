"""Groq development-only, cross-process send pacing. Never retries a POST.

No API key, request body, response body or arbitrary header is persisted. A
reservation is charged before sending; uncertain requests retain their budget.
The caller's checkpoint/receipt remains the authority for no-replay.
"""

from contextlib import contextmanager
from hashlib import sha256
import fcntl
import json
import os
from pathlib import Path
import re
from time import sleep, time


_DIR = Path("/tmp/opencode/dealdesk-groq-rate")
_DURATION = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s)?\Z")
_LIMIT_HEADERS = ("x-ratelimit-limit-requests", "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens")
_RESET_HEADERS = ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens")


def _duration(raw):
    if not isinstance(raw, str) or len(raw) > 32:
        return None
    match = _DURATION.fullmatch(raw)
    if not match or all(x is None for x in match.groups()):
        return None
    value = float(match[1] or 0) * 3600 + float(match[2] or 0) * 60 + float(match[3] or 0)
    return value if 0 <= value <= 86400 else None


def rate_headers(headers):
    """Only Groq's documented numeric limits/resets; never error text/headers."""
    result = {}
    if headers is None:
        return result
    for name in _LIMIT_HEADERS:
        value = headers.get(name)
        if isinstance(value, str) and value.isascii() and value.isdecimal() and len(value) <= 10:
            result[name] = int(value)
    for name in _RESET_HEADERS:
        value = _duration(headers.get(name))
        if value is not None:
            result[name] = value
    raw = headers.get("retry-after")
    if isinstance(raw, str) and re.fullmatch(r"\d{1,5}(?:\.\d{1,2})?", raw):
        result["retry-after"] = min(float(raw), 86400)
    return result


def _limits():
    # Published FREE base limits; actual org-specific lower headers win.
    defaults = {"RPM": 30, "RPD": 1000, "TPM": 8000, "TPD": 200000,
                "ITPM": 0, "OTPM": 0}
    result = {}
    for name, default in defaults.items():
        raw = os.environ.get("DEALDESK_GROQ_" + name)
        if raw is None:
            result[name] = default
        elif not raw.isascii() or not raw.isdecimal() or len(raw) > 9 or int(raw) < 0:
            raise ValueError("groq_development_invalid_rate_limit")
        else:
            result[name] = int(raw)
    if any(result[k] == 0 for k in ("RPM", "RPD", "TPM", "TPD")):
        raise ValueError("groq_development_invalid_rate_limit")
    return result


@contextmanager
def _locked(path):
    _DIR.mkdir(mode=0o700, exist_ok=True)
    st = _DIR.stat()
    if _DIR.is_symlink() or st.st_uid != os.geteuid() or st.st_mode & 0o077:
        raise ValueError("groq_development_rate_directory_unsafe")
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        st = os.fstat(fd)
        if st.st_uid != os.geteuid() or st.st_nlink != 1 or st.st_mode & 0o077:
            raise ValueError("groq_development_rate_file_unsafe")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield fd
    finally:
        os.close(fd)


def _load(fd):
    size = os.fstat(fd).st_size
    if size == 0:
        return {"version": 1, "events": [], "blocked_until": 0,
                "daily_until": 0, "provider": {}}
    if size > 1048576:
        raise ValueError("groq_development_rate_state_invalid")
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        state = json.loads(os.read(fd, size))
        if (type(state) is not dict or set(state) != {"version", "events", "blocked_until",
                "daily_until", "provider"} or state["version"] != 1 or
                type(state["events"]) is not list or len(state["events"]) > 2000 or
                any(type(e) is not dict or set(e) != {"at", "input", "output"} or
                    any(type(e[k]) not in (int, float) or e[k] < 0 for k in e)
                    for e in state["events"]) or type(state["provider"]) is not dict or
                any(type(state[k]) not in (int, float) or state[k] < 0
                    for k in ("blocked_until", "daily_until"))):
            raise ValueError()
        return state
    except (OSError, ValueError, TypeError, UnicodeError):
        raise ValueError("groq_development_rate_state_invalid") from None


def _save(fd, state):
    data = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
    if len(data) > 1048576:
        raise ValueError("groq_development_rate_state_full")
    os.lseek(fd, 0, os.SEEK_SET)
    os.write(fd, data)
    os.ftruncate(fd, len(data))
    os.fsync(fd)


def _wait(state, limits, now, estimated_input, estimated_output):
    from .live_models import ProviderError
    events = state["events"] = [e for e in state["events"] if e["at"] > now - 86400]
    if state["daily_until"] > now:
        raise ProviderError("groq_daily_limit")
    provider = state["provider"]
    limits = dict(limits)
    if type(provider.get("requests_limit")) is int and provider["requests_limit"] > 0:
        limits["RPD"] = min(limits["RPD"], provider["requests_limit"])
    if type(provider.get("tokens_limit")) is int and provider["tokens_limit"] > 0:
        limits["TPM"] = min(limits["TPM"], provider["tokens_limit"])
    recent = [e for e in events if e["at"] > now - 60]
    if len(events) >= limits["RPD"] or sum(e["input"] + e["output"] for e in events) + (
            estimated_input + estimated_output) > limits["TPD"]:
        state["daily_until"] = min(e["at"] for e in events) + 86400
        raise ProviderError("groq_daily_limit")
    waits = [max(0, state["blocked_until"] - now)]
    for name, observed, expected in (
            ("RPM", len(recent), 1),
            ("TPM", sum(e["input"] + e["output"] for e in recent),
             estimated_input + estimated_output),
            ("ITPM", sum(e["input"] for e in recent), estimated_input),
            ("OTPM", sum(e["output"] for e in recent), estimated_output)):
        if limits[name] and observed + expected > limits[name]:
            if expected > limits[name]:
                raise ProviderError("groq_request_exceeds_rate_budget")
            waits.append(min(e["at"] for e in recent) + 60 - now)
    if provider.get("tokens_until", 0) <= now:
        provider.pop("remaining_tokens", None)
    if provider.get("requests_until", 0) <= now:
        provider.pop("remaining_requests", None)
    if provider.get("remaining_requests") == 0:
        reset = provider.get("requests_until", 0)
        if reset > now:
            state["daily_until"] = reset
            raise ProviderError("groq_daily_limit")
    if provider.get("remaining_tokens") is not None and provider.get(
            "remaining_tokens") < estimated_input + estimated_output:
        waits.append(max(0, provider.get("tokens_until", 0) - now))
    return max(waits)


def _observe(state, headers, status, now):
    data = headers or {}  # already allowlisted by the private send hook
    provider = state["provider"]
    for name, dest, reset in (("requests", "remaining_requests", "requests_until"),
                              ("tokens", "remaining_tokens", "tokens_until")):
        limit = data.get("x-ratelimit-limit-" + name)
        remain = data.get("x-ratelimit-remaining-" + name)
        duration = data.get("x-ratelimit-reset-" + name)
        if limit is not None and remain is not None and duration is not None:
            provider[dest] = min(limit, remain)
            provider[reset] = now + duration
            provider[name + "_limit"] = limit
    if status == 429:
        # Without a trusted reset/retry window, an unknown 429 cannot justify
        # another fresh assessment after only one minute. Charge the uncertain
        # send and conservatively stop new sends for a day.
        reset = data.get("x-ratelimit-reset-tokens") or data.get(
            "x-ratelimit-reset-requests")
        state["blocked_until"] = max(state["blocked_until"], now + max(60,
            data.get("retry-after", reset if reset is not None else 86400)))
        if reset is None and "retry-after" not in data:
            state["daily_until"] = max(state["daily_until"], now + 86400)
        if provider.get("remaining_requests") == 0 and provider.get("requests_until", 0) > now:
            state["daily_until"] = provider["requests_until"]
        if provider.get("remaining_tokens") == 0 and provider.get("tokens_until", 0) > now:
            state["blocked_until"] = max(state["blocked_until"], provider["tokens_until"])


def send_with_limit(body, key, send):
    """One Groq send under a credential+model lock; never replay on failure."""
    from .live_models import GROQ_MODEL, ProviderError, _json
    if not callable(send) or body.get("model") != GROQ_MODEL:
        raise ValueError("groq_development_rate_scope_invalid")
    limits = _limits()
    estimate_input = (len(_json(body).encode()) + 2) // 3
    estimate_output = body.get("max_completion_tokens")
    if (type(estimate_output) is not int or estimate_output < 1 or
            estimate_input + estimate_output > limits["TPM"] or
            estimate_input + estimate_output > limits["TPD"]):
        raise ProviderError("groq_request_exceeds_rate_budget")
    account = os.environ.get("DEALDESK_GROQ_ACCOUNT_ID")
    if account is not None and (not re.fullmatch(r"org_[a-zA-Z0-9]{8,100}", account)):
        raise ValueError("groq_development_rate_account_invalid")
    scope = account if account is not None else sha256(key.encode()).hexdigest()
    path = _DIR / (sha256((scope + ":" + body["model"]).encode(
        )).hexdigest() + ".json")
    while True:
        with _locked(path) as fd:
            state = _load(fd)
            now = time()
            try:
                wait = _wait(state, limits, now, estimate_input, estimate_output)
            except ProviderError:
                _save(fd, state)
                raise
            if wait > 0:
                _save(fd, state)
            else:
                event = {"at": now, "input": estimate_input, "output": estimate_output}
                state["events"].append(event)
                _save(fd, state)  # durable charge before the network call
                observed = {}
                def headers(status, values):
                    observed["status"] = status
                    observed["headers"] = rate_headers(values)
                try:
                    response = send(headers)
                except BaseException:
                    _observe(state, observed.get("headers"), observed.get("status"), time())
                    _save(fd, state)
                    raise
                usage = response.get("usage", {}) if type(response) is dict else {}
                if (type(usage) is dict and type(usage.get("prompt_tokens")) is int and
                        type(usage.get("completion_tokens")) is int and
                        0 <= usage["prompt_tokens"] <= 100000 and
                        0 <= usage["completion_tokens"] <= estimate_output):
                    event["input"] = usage["prompt_tokens"]
                    event["output"] = usage["completion_tokens"]
                _observe(state, observed.get("headers"), 200, time())
                if state["provider"].get("remaining_tokens") is not None:
                    state["provider"]["remaining_tokens"] = max(0,
                        state["provider"]["remaining_tokens"])
                _save(fd, state)
                return response
        sleep(min(wait, 60))
