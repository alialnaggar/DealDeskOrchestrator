"""No provider access: deliberately disconnected error classifier and receipts."""

import io
import json
from pathlib import Path
import tempfile
import unittest

from dealdesk_phase2.groq_error_diagnostic import MAX_ERROR_BYTES, classify_error
from dealdesk_phase2.hybrid_send_reservation import (
    attempt_path, claim_and_call, verify_receipt,
)
from dealdesk_phase2.live_models import ProviderError


class DiagnosticSafety(unittest.TestCase):
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
