"""The opt-in provider probe must redact credentials and classify only bounded output."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from dealdesk_phase2.provider_diagnostic import _error_details, _finish, _interpret, _safe_header


class ProviderDiagnosticTests(unittest.TestCase):
    def test_redacts_key_from_json_and_plain_error(self):
        key = "gsk_private_test_key"
        result = _error_details(('{"error":{"code":"permissions_error",'
                                 '"message":"key gsk_private_test_key blocked"}}').encode(), key)
        self.assertEqual(result["code"], "permissions_error")
        self.assertNotIn(key, str(result))
        self.assertNotIn(key, str(_error_details(b"Forbidden gsk_private_test_key", key)))

    def test_rejects_unexpected_header_and_classifies_structured_result(self):
        self.assertIsNone(_safe_header("id\nAuthorization: private"))
        self.assertEqual(_interpret("gemini", "structured", {"candidates": [{"content": {
            "parts": [{"text": '{"status":"ok"}'}]}}]}), "valid_structured_json")
        self.assertEqual(_interpret("groq", "metadata", {"id": "openai/gpt-oss-120b"}), "model_present")

    def test_failed_capability_gate_saves_sanitized_records_and_stops_smoke(self):
        records = [{"provider": "gemini", "phase": "generation", "status": 503,
                    "error": {"message": "high demand"}}]
        with TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with self.assertRaises(SystemExit):
                _finish(records, str(output), True)
            self.assertIn('"status": 503', output.read_text())


if __name__ == "__main__":
    unittest.main()
