"""No provider access: bounded opt-in transport classification and receipts."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from dealdesk_phase2.groq_error_diagnostic import MAX_ERROR_BYTES, classify_error
from dealdesk_phase2.hybrid_send_reservation import (
    attempt_path, claim_and_call, verify_receipt,
)
from dealdesk_phase2.live_models import ProviderError, _json, _post


class DiagnosticSafety(unittest.TestCase):
    def _transport(self, payload, *, enabled=True, status=400, headers=None,
                   success=False):
        body = {"messages": [{"role": "user", "content": "offline"}],
                "model": "openai/gpt-oss-120b"}
        seen = []

        class Opener:
            def open(self, request, timeout):
                seen.append(request.data)
                if success:
                    return io.BytesIO(b'{"choices":[],"usage":{}}')
                raise HTTPError(request.full_url, status, "private provider text",
                                headers or {}, payload)

        with patch("dealdesk_phase2.live_models.build_opener", return_value=Opener()):
            try:
                value = _post("https://api.groq.com/openai/v1/chat/completions",
                    "Bearer offline-secret", "Authorization", body,
                    classify_transport=True, reject_redirects=True,
                    capture_http_error=enabled)
            except ProviderError as error:
                value = error
        self.assertEqual(seen, [_json(body).encode()])
        return value

    def test_shared_transport_recognized_400_and_terminal_receipt(self):
        private = "customer-SECRET bearer-SECRET"
        raw = json.dumps({"error": {"type": "invalid_request_error",
            "code": "tool_use_failed", "param": "messages[3].tool_call_id",
            "message": private}}).encode()

        class Bounded(io.BytesIO):
            def read(self, size=-1):
                self_size = size
                if self_size != MAX_ERROR_BYTES + 1:
                    raise AssertionError("unbounded read")
                return super().read(size)

        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as base:
            directory = Path(base)
            directory.chmod(0o700)
            kwargs = dict(assessment_id="new-offline", start_digest="a" * 64,
                          stage="decision", ordinal=1, request_digest="b" * 64)
            path = attempt_path(directory, **{key: kwargs[key] for key in (
                "assessment_id", "start_digest", "stage", "ordinal")})
            calls = []

            def send():
                calls.append(True)
                raise self._transport(Bounded(raw), headers={
                    "x-request-id": "12345678-1234-1234-1234-123456789abc"})

            with self.assertRaises(ProviderError) as caught:
                claim_and_call(directory, **kwargs, send=send)
            self.assertEqual(caught.exception.code, "http_400")
            self.assertEqual(str(caught.exception), "http_400")
            receipt = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row["event"] for row in receipt], ["reserved", "failed"])
            self.assertEqual(receipt[1]["code"], "http_400")
            self.assertGreaterEqual(receipt[1]["elapsed_ms"], 0)
            self.assertEqual(receipt[0]["request_sha256"], "b" * 64)
            self.assertEqual(receipt[1]["diagnostic"], {
                "type": "invalid_request_error", "code": "tool_use_failed",
                "param": "messages[3].tool_call_id",
                "request_id": "12345678-1234-1234-1234-123456789abc"})
            self.assertNotIn(private, path.read_text())
            self.assertFalse(verify_receipt(path, start_digest="a" * 64,
                stage="decision", ordinal=1, request_digest="b" * 64))
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **kwargs, send=send)
            self.assertEqual(len(calls), 1)

    def test_unknown_malformed_oversize_timeout_preserve_http_status(self):
        class TimeoutStream:
            def read(self, size):
                raise TimeoutError("customer-SECRET")
            def close(self):
                pass

        for payload in (io.BytesIO(b'not json'), io.BytesIO(b'[]'),
                        io.BytesIO(b' ' * (MAX_ERROR_BYTES + 1)), TimeoutStream(),
                        io.BytesIO(json.dumps({"error": {"type": "customer-SECRET",
                            "code": "customer-SECRET", "param": "customer-SECRET"}}).encode())):
            with self.subTest(payload=type(payload).__name__):
                error = self._transport(payload, headers={"x-request-id": "customer-SECRET"})
                self.assertIsInstance(error, ProviderError)
                self.assertEqual(error.code, "http_400")
                self.assertEqual(error.diagnostic, {})
        self.assertEqual(self._transport(io.BytesIO(b'{}'), status=503).code, "http_503")

    def test_success_does_not_read_diagnostic_or_change_wire(self):
        self.assertEqual(self._transport(None, success=True), {"choices": [], "usage": {}})
        class NoRead(io.BytesIO):
            def read(self, *args, **kwargs):
                raise AssertionError("error must remain unread when capture is disabled")
        error = self._transport(NoRead(b'private'), enabled=False)
        self.assertEqual(error.code, "http_400")
        self.assertIsNone(error.diagnostic)

    def test_crash_only_reservation_and_tampered_diagnostic_cannot_replay(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as base:
            directory = Path(base)
            directory.chmod(0o700)
            kwargs = dict(assessment_id="crashed-offline", start_digest="c" * 64,
                          stage="decision", ordinal=0, request_digest="d" * 64)
            path = attempt_path(directory, **{k: kwargs[k] for k in (
                "assessment_id", "start_digest", "stage", "ordinal")})
            reserved = {"event": "reserved", "stage": "decision", "ordinal": 0,
                        "start_sha256": "c" * 64, "request_sha256": "d" * 64,
                        "reserved_at_utc": "2026-10-28T00:00:00+00:00"}
            path.write_text(json.dumps(reserved) + "\n")
            path.chmod(0o600)
            self.assertFalse(verify_receipt(path, start_digest="c" * 64,
                             stage="decision", ordinal=0, request_digest="d" * 64))
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **kwargs, send=lambda: self.fail("replayed"))
            tampered = {"event": "failed", "code": "http_400", "elapsed_ms": 1,
                        "diagnostic": {"type": "customer-SECRET"}}
            with path.open("a") as f:
                f.write(json.dumps(tampered) + "\n")
            from dealdesk_phase2.hybrid_contracts import HybridContractError
            with self.assertRaises(HybridContractError):
                verify_receipt(path, start_digest="c" * 64, stage="decision",
                               ordinal=0, request_digest="d" * 64)
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **kwargs, send=lambda: self.fail("replayed"))

    def test_recognized_values_only_and_bounded_read(self):
        class Checked(io.BytesIO):
            def read(self, size=-1):
                self_size = size
                if self_size != MAX_ERROR_BYTES + 1:
                    raise AssertionError("unbounded read")
                return super().read(size)

        private = "customer-SECRET bearer-SECRET"
        raw = json.dumps({"error": {"type": "invalid_request_error",
            "code": "tool_use_failed", "param": "messages[3].tool_call_id",
            "message": private}, "extra": private}).encode()
        result = classify_error(Checked(raw), {
            "x-request-id": "12345678-1234-1234-1234-123456789abc",
            "authorization": private})
        self.assertEqual(result, {"type": "invalid_request_error",
            "code": "tool_use_failed", "param": "messages[3].tool_call_id",
            "request_id": "12345678-1234-1234-1234-123456789abc"})
        self.assertNotIn(private, repr(result))

    def test_unknown_values_never_echo_and_header_must_be_uuid(self):
        private = "customer-SECRET"
        raw = json.dumps({"error": {"type": private, "code": private,
             "param": private, "message": private}}).encode()
        result = classify_error(io.BytesIO(raw), {"x-request-id": private})
        self.assertEqual(result, {"type": "unknown", "code": "unknown",
                                  "param": "unknown", "request_id": None})

    def test_malformed_oversized_and_timeout_fail_closed(self):
        class TimeoutStream:
            def read(self, size):
                raise TimeoutError("customer-SECRET")

        for stream in (io.BytesIO(b"not json"), io.BytesIO(b"[]"),
                       io.BytesIO(b'{"error": "bad"}'),
                       io.BytesIO(b" " * (MAX_ERROR_BYTES + 1)), TimeoutStream()):
            with self.subTest(stream=type(stream).__name__):
                result = classify_error(stream, {"x-request-id":
                    "12345678-1234-1234-1234-123456789abc"})
                self.assertEqual(result, {"type": "unknown", "code": "unknown",
                                          "param": "unknown", "request_id": None})

    def test_failed_send_receipt_stays_terminal_and_contains_no_diagnostic(self):
        with tempfile.TemporaryDirectory(dir="/tmp/opencode") as base:
            directory = Path(base)
            directory.chmod(0o700)
            digest = "a" * 64
            request = "b" * 64
            path = attempt_path(directory, assessment_id="offline-only",
                                start_digest=digest, stage="decision", ordinal=1)
            calls = []

            def send():
                calls.append(1)
                diagnostic = classify_error(io.BytesIO(json.dumps({"error": {
                    "type": "invalid_request_error", "code": "tool_use_failed",
                    "message": "customer-SECRET"}}).encode()))
                self.assertEqual(diagnostic["code"], "tool_use_failed")
                raise ProviderError("http_400")

            kwargs = dict(assessment_id="offline-only", start_digest=digest,
                          stage="decision", ordinal=1, request_digest=request,
                          send=send)
            with self.assertRaises(ProviderError):
                claim_and_call(directory, **kwargs)
            self.assertFalse(verify_receipt(path, start_digest=digest,
                             stage="decision", ordinal=1, request_digest=request))
            self.assertEqual([json.loads(line)["event"] for line in
                              path.read_text().splitlines()], ["reserved", "failed"])
            self.assertNotIn("SECRET", path.read_text())
            self.assertNotIn("tool_use_failed", path.read_text())
            with self.assertRaises(FileExistsError):
                claim_and_call(directory, **kwargs)
            self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
