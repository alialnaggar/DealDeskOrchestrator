"""Sanitized, read-only Groq model-access gate; never prints response or key.

This is a metadata check, not inference authorization. Call only after the
owner supplies a valid free-tier credential; do not retry a known-invalid key.
"""

from dataclasses import dataclass
import json
import os
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .live_models import GROQ_MODEL


MODEL_URL = "https://api.groq.com/openai/v1/models"
MAX_METADATA_BYTES = 1048576


@dataclass(frozen=True)
class ModelAccess:
    category: str
    http_status: int | None = None
    model_accessible: bool | None = None

    @property
    def ready(self) -> bool:
        return self.category == "available" and self.model_accessible is True


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def credential_shape(key: str | None) -> str:
    """Local syntax diagnosis only; never proves that Groq accepts this key."""
    if not key:
        return "credential_unavailable"
    try:
        raw = key.encode("ascii")
    except UnicodeError:
        return "credential_invalid_format"
    if (not 8 <= len(raw) <= 511 or any(c < 33 or c > 126 for c in raw)
            or not raw.startswith(b"gsk_") or raw.count(b"gsk_") != 1
            or len(raw) % 2 == 0 and raw[:len(raw)//2] == raw[len(raw)//2:]):
        return "credential_invalid_format"
    return "credential_shape_ok"


def _status(code: int) -> str:
    return {401: "authentication_failed", 403: "authorization_denied",
            404: "metadata_endpoint_missing", 429: "rate_limited"}.get(code, "http_error")


def check_model_access(key: str | None, *, opener=None) -> ModelAccess:
    """One bounded GET; no redirects, retries, provider-body logging or inference."""
    shape = credential_shape(key)
    if shape != "credential_shape_ok":
        return ModelAccess(shape)
    request = Request(MODEL_URL, headers={"Authorization": "Bearer " + key,
        "User-Agent": "DealDeskOrchestrator-B01-preflight/1"}, method="GET")
    client = opener if opener is not None else build_opener(_NoRedirect())
    try:
        with client.open(request, timeout=20) as response:
            status = response.status
            if status != 200:
                return ModelAccess(_status(status), status)
            data = response.read(MAX_METADATA_BYTES + 1)
    except HTTPError as exc:
        code = exc.code
        exc.close()  # Do not read or retain headers, response text, or error body.
        return ModelAccess(_status(code), code)
    except (socket.timeout, TimeoutError):
        return ModelAccess("transport_timeout")
    except ssl.SSLError:
        return ModelAccess("transport_tls_failure")
    except URLError as exc:
        reason = exc.reason
        if isinstance(reason, socket.gaierror):
            return ModelAccess("transport_dns_failure")
        if isinstance(reason, ssl.SSLError):
            return ModelAccess("transport_tls_failure")
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return ModelAccess("transport_timeout")
        return ModelAccess("transport_failure")
    except (OSError, ValueError):
        return ModelAccess("transport_failure")
    if len(data) > MAX_METADATA_BYTES:
        return ModelAccess("metadata_too_large", 200)
    try:
        payload = json.loads(data)
        models = payload["data"]
        if not isinstance(models, list) or any(
                not isinstance(item, dict) or not isinstance(item.get("id"), str)
                for item in models):
            raise ValueError()
        available = GROQ_MODEL in {item["id"] for item in models}
    except (ValueError, KeyError, TypeError, UnicodeError):
        return ModelAccess("invalid_metadata", 200)
    return ModelAccess("available" if available else "model_unavailable", 200, available)


def main() -> int:
    result = check_model_access(os.environ.get("GROQ_API_KEY"))
    print("groq_preflight=" + result.category + " http_status=" + (
        str(result.http_status) if result.http_status is not None else "unknown") +
        " model_accessible=" + (str(result.model_accessible).lower()
                               if result.model_accessible is not None else "unknown"))
    return 0 if result.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
