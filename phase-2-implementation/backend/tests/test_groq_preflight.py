"""All metadata checks are offline doubles: no socket or real credential."""

from io import BytesIO
import socket
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

from dealdesk_phase2.groq_preflight import (GROQ_MODEL, MAX_METADATA_BYTES,
                                           check_model_access, credential_shape)


FAKE_KEY = "gsk_" + "x" * 48


class _Response:
    status = 200

    def __init__(self, body, status=200):
        self.status = status
        self.body = BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.body.close()

    def read(self, count):
        return self.body.read(count)


class MetadataGateTests(unittest.TestCase):
    def test_local_format_does_not_send_incomplete_doubled_or_altered_key(self):
        for key in (None, "", "Bearer " + FAKE_KEY, FAKE_KEY + " ",
                    FAKE_KEY + "\n", FAKE_KEY + FAKE_KEY, FAKE_KEY[:6],
                    "gsk_" + "a" * 24 + "gsk_" + "b" * 24):
            with self.subTest(kind=credential_shape(key)):
                client = Mock()
                result = check_model_access(key, opener=client)
                self.assertEqual(result.category, "credential_unavailable" if not key
                                 else "credential_invalid_format")
                client.open.assert_not_called()
        self.assertEqual(credential_shape(FAKE_KEY), "credential_shape_ok")
        # An otherwise printable truncated key cannot be proved invalid without
        # access to the owner's original: metadata authentication must decide.
        self.assertEqual(credential_shape(FAKE_KEY[:12]), "credential_shape_ok")

    def test_header_contains_one_bearer_and_the_unmodified_key(self):
        client = Mock()
        client.open.return_value = _Response(('{' + '"data":[{"id":"' + GROQ_MODEL + '"}]}').encode())
        result = check_model_access(FAKE_KEY, opener=client)
        self.assertTrue(result.ready)
        request = client.open.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer " + FAKE_KEY)
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(client.open.call_count, 1)
        self.assertNotIn(FAKE_KEY, repr(result))

    def test_http_errors_are_distinct_and_provider_bodies_are_never_read(self):
        for status, category in ((401, "authentication_failed"),
                                 (403, "authorization_denied"),
                                 (404, "metadata_endpoint_missing"),
                                 (429, "rate_limited"), (500, "http_error")):
            with self.subTest(status=status):
                body = Mock()
                body.read.side_effect = AssertionError("provider body must not be read")
                error = HTTPError("https://example.invalid/private", status,
                                  "secret error", {"Authorization": FAKE_KEY}, body)
                client = Mock()
                client.open.side_effect = error
                result = check_model_access(FAKE_KEY, opener=client)
                self.assertEqual((result.category, result.http_status), (category, status))
                self.assertFalse(result.ready)
                body.read.assert_not_called()
                self.assertNotIn(FAKE_KEY, repr(result))

    def test_missing_model_malformed_and_oversized_metadata_fail_closed(self):
        for body, category in ((b'{"data":[]}', "model_unavailable"),
                               (b'not-json', "invalid_metadata"),
                               (b'{"data":{}}', "invalid_metadata"),
                               (b'{"data":[{}]}', "invalid_metadata"),
                               (b'x' * (MAX_METADATA_BYTES + 1), "metadata_too_large")):
            with self.subTest(category=category):
                client = Mock()
                client.open.return_value = _Response(body)
                result = check_model_access(FAKE_KEY, opener=client)
                self.assertEqual(result.category, category)
                self.assertFalse(result.ready)
        client = Mock()
        client.open.return_value = _Response(b'{}', 302)
        self.assertEqual(check_model_access(FAKE_KEY, opener=client).category, "http_error")

    def test_timeout_dns_tls_and_other_transport_are_distinct(self):
        import ssl

        for error, category in ((TimeoutError(), "transport_timeout"),
                                (URLError(socket.gaierror()), "transport_dns_failure"),
                                (URLError(ssl.SSLError()), "transport_tls_failure"),
                                (URLError(OSError()), "transport_failure")):
            with self.subTest(category=category):
                client = Mock()
                client.open.side_effect = error
                self.assertEqual(check_model_access(FAKE_KEY, opener=client).category,
                                 category)


if __name__ == "__main__":
    unittest.main()
