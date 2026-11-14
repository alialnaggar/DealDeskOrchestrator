"""Offline, sanitized reproductions of historical N01 inspection digests.

Only synthetic subject IDs, source fingerprints and committed receipt hashes are
used; no database, credential, provider response or historical send is accessed.
"""

import json
import io
from hashlib import sha256
from unittest import TestCase

from dealdesk_phase2.groq_error_diagnostic import (MAX_ERROR_BYTES, classify_error,
                                                   safe_fields)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.m20_groq import request_body
from dealdesk_phase2.m20_specialists import MAX_INSPECTIONS, VERSION


UC02 = ("d9c2bb391891a729502ed0965c9bcf54c88c8c80f974140db695fca7b4ce7f4a",
        "d45e0752fa2e784652f71115cd20371977addaf2881b4a0d6148aafd79ea51bb")
PLAIN = ("49c07a3e48660fc656f244648ead414a5d95b0cce91b15ffe5b3bf3e226bc4e5",
         "30eec02f45047467736e4378eb9b764e4fe28b0c39e5a66aa408a8a945ba2edd")
# assessment, frozen source variant, first-turn choice, reserved request SHA-256
CASES = (
    ("GROQ-DEV-ccd4a73e0d0d40f58168ce396f7dc18f", UC02, "required",
     "b8bdc1ae1ec66bd52b029ac2399da26eda32f58e6a8c0c1e3f4ddc38bd85a9cc"),
    ("GROQ-DEV-4c9bf14005b54a168d3fedbfb2fc2e90", UC02, "auto",
     "2436728e21b0be732ee2046d6696601ec37ffb2713af9bc4bc3f0eca8af551cd"),
    ("GROQ-DEV-0b6da505ecde4953b2be62b84e2df497", PLAIN, "auto",
     "b43b8a5d4c6d796089cff0ac164a423ebe51f82be58ed6ae5362c1e9595ba8e2"),
    ("GROQ-DEV-f243bb5acba44ec49f96412f45319ff3", PLAIN, "auto",
     "b1b37eb1f7f04587b4ef1554d1aee32188017b4fe7bb6f8dc69a4fdbb9ddbec4"),
    ("GROQ-DEV-925e3f37a9d24e13bb428a487ac814d5", UC02, "auto",
     "2c85331d675c6f40f0e9d6b0240183b82f507dcf68dda8fdd80ff014b51904d2"),
)


class QwenHistoricalInspectionAudit(TestCase):
    def test_400_diagnostic_classifies_only_known_codes_without_private_text(self):
        private = "SECRET customer and provider response body"
        def diagnose(error):
            return safe_fields(classify_error(io.BytesIO(json.dumps({
                "error": {**error, "message": private}}).encode())))

        self.assertEqual(diagnose({"type": "invalid_request_error",
            "code": "tool_use_failed", "param": "tool_choice"}), {
            "type": "invalid_request_error", "code": "tool_use_failed",
            "param": "tool_choice"})
        self.assertEqual(diagnose({"type": "invalid_request_error",
            "code": "new-provider-code", "param": "reasoning_format"}), {
            "type": "invalid_request_error"})
        self.assertEqual(safe_fields(classify_error(io.BytesIO(b"x" * (
            MAX_ERROR_BYTES + 1)))), {})
        self.assertNotIn(private, repr(diagnose({"type": "invalid_request_error",
            "code": "tool_use_failed", "param": "tool_choice"})))

    def test_reserved_hashes_and_exclusive_input_differences(self):
        baselines = []
        for assessment_id, (bundle, source), choice, digest in CASES:
            with self.subTest(assessment_id=assessment_id):
                body = request_body({"assessment_id": assessment_id,
                    "bundle_sha256": bundle, "source_input_digest": source,
                    "fixed_execution": "completed", "fixed_finding": "confirmed",
                    "line_ids": ["M18-L-N01"], "max_inspections": MAX_INSPECTIONS,
                    "permitted_tool": "inspect_configuration_line",
                    "phase1c_run_id": "00000000-0000-4000-8000-000000018101",
                    "specialist": "configuration", "subject_id": "M18-D-N01",
                    "version": VERSION}, ())
                if choice == "required":  # archived v1 wire, never sendable under v2
                    body["tool_choice"] = choice
                self.assertEqual(sha256(_canonical(body).encode()).hexdigest(), digest)
                self.assertEqual(len(_canonical(body).encode()),
                                 3014 if choice == "required" else 3010)
                self.assertEqual([m["role"] for m in body["messages"]],
                                 ["system", "user"])
                self.assertEqual(body["reasoning_format"], "parsed")
                self.assertEqual(body["max_completion_tokens"], 512)
                self.assertNotIn("response_format", body)
                baselines.append((sha256(body["messages"][0]["content"].encode()).hexdigest(),
                    sha256(_canonical(body["tools"]).encode()).hexdigest(),
                    json.loads(body["messages"][1]["content"])["input"],
                    {k: v for k, v in body.items() if k not in ("messages", "tool_choice")}))
        for system, tools, user, settings in baselines:
            self.assertEqual(system, "d775c7546e2abc7c06e76f5cebb13dca4a892969c3b8e301198e1a97cc4fc74f")
            self.assertEqual(tools, "5d92a0ae0b2aa6c471373218b83314de625243355999789f80a3bff4506ddfe9")
            self.assertEqual(settings, baselines[0][3])
            self.assertEqual({k: v for k, v in user.items() if k not in (
                "assessment_id", "bundle_sha256", "source_input_digest")},
                {k: v for k, v in baselines[0][2].items() if k not in (
                    "assessment_id", "bundle_sha256", "source_input_digest")})
