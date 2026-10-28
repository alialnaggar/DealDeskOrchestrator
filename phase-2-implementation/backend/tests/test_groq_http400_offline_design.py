"""Fully offline mock design checks; not authorization for provider requests."""

import io
import json
import unittest

from dealdesk_phase2.groq_error_diagnostic import classify_error, safe_fields
from groq_http400_offline_design import (CALL_ID, DOMAIN_LIKE, INSPECT, NEUTRAL,
    PROPOSED_ERROR_BYTES, canonical, mocked_error_bytes,
    proposed_error_projection, synthetic_body)


class SyntheticWireDesign(unittest.TestCase):
    def test_two_turn_native_pair_and_budget_without_business_evidence(self):
        first = synthetic_body()
        second = synthetic_body(continuation=True)
        self.assertEqual([m["role"] for m in first["messages"]], ["system", "user"])
        self.assertEqual([m["role"] for m in second["messages"]],
                         ["system", "user", "assistant", "tool"])
        self.assertEqual(first["tools"], second["tools"])
        self.assertEqual(first["messages"], second["messages"][:2])
        call = second["messages"][2]["tool_calls"][0]
        result = second["messages"][3]
        self.assertEqual(call["id"], result["tool_call_id"])
        self.assertEqual(call["id"], CALL_ID)
        self.assertEqual(call["function"]["name"], result["name"])
        self.assertEqual(result["name"], INSPECT)
        self.assertEqual(json.loads(call["function"]["arguments"]),
                         {"record_key": "SYN-1"})
        self.assertEqual(json.loads(result["content"]), NEUTRAL)
        for wire in (first, second):
            self.assertLessEqual(len(canonical(wire).encode()), 8192)
            self.assertEqual(wire["max_completion_tokens"], 512)
            self.assertFalse(wire["parallel_tool_calls"])
            self.assertNotIn("response_format", wire)
            self.assertNotIn("customer", canonical(wire).lower())
            self.assertNotIn("pricing_line", canonical(wire))

    def test_name_is_the_only_changed_field(self):
        named = synthetic_body(continuation=True)
        unnamed = synthetic_body(continuation=True, named=False)
        self.assertEqual({**unnamed["messages"][3], "name": INSPECT},
                         named["messages"][3])
        unnamed["messages"][3]["name"] = INSPECT
        self.assertEqual(named, unnamed)

    def test_schema_is_the_only_changed_field(self):
        simple = synthetic_body(continuation=True, named=False)
        complex_ = synthetic_body(continuation=True, named=False, complex_schema=True)
        self.assertEqual(simple["tools"][0], complex_["tools"][0])
        self.assertNotEqual(simple["tools"][1], complex_["tools"][1])
        complex_["tools"][1] = simple["tools"][1]
        self.assertEqual(simple, complex_)

    def test_content_is_the_only_changed_field(self):
        neutral = synthetic_body(continuation=True, named=False)
        domain = synthetic_body(continuation=True, named=False, domain_like=True)
        self.assertEqual(json.loads(domain["messages"][3]["content"]), DOMAIN_LIKE)
        domain["messages"][3]["content"] = neutral["messages"][3]["content"]
        self.assertEqual(neutral, domain)

    def test_tool_choice_is_the_only_changed_field(self):
        required = synthetic_body(continuation=True, named=False)
        auto = synthetic_body(continuation=True, named=False, tool_choice="auto")
        self.assertEqual((required["tool_choice"], auto["tool_choice"]),
                         ("required", "auto"))
        auto["tool_choice"] = "required"
        self.assertEqual(required, auto)
        with self.assertRaises(ValueError):
            synthetic_body(tool_choice="none")


class ProposedRetentionDesign(unittest.TestCase):
    def test_long_message_keeps_only_documented_type_and_local_state(self):
        raw = mocked_error_bytes(message_size=1500).getvalue()
        self.assertGreater(len(raw), 1024)
        self.assertLess(len(raw), PROPOSED_ERROR_BYTES)
        self.assertEqual(safe_fields(classify_error(io.BytesIO(raw))), {})
        result = proposed_error_projection(io.BytesIO(raw))
        self.assertEqual(result, {"local_state": "parsed_allowlisted",
                                  "diagnostic": {"type": "invalid_request_error"}})
        self.assertNotIn("message", repr(result))
        self.assertNotIn("x" * 32, repr(result))

    def test_partial_reads_are_bounded_until_end(self):
        class Chunks(io.BytesIO):
            maximum_read = 0
            def read(self, size=-1):
                self.maximum_read = max(self.maximum_read, size)
                return super().read(min(size, 17))

        stream = Chunks(mocked_error_bytes(message_size=1200).getvalue())
        result = proposed_error_projection(stream)
        self.assertEqual(result["diagnostic"], {"type": "invalid_request_error"})
        self.assertLessEqual(stream.maximum_read, PROPOSED_ERROR_BYTES + 1)

    def test_oversize_timeout_malformed_and_unknown_never_echo_provider_text(self):
        class Timeouts:
            def read(self, size):
                raise TimeoutError("private-SECRET")

        for stream, state in ((mocked_error_bytes(message_size=5000), "oversize"),
                              (Timeouts(), "read_timeout"),
                              (io.BytesIO(b"not json private-SECRET"), "malformed"),
                              (io.BytesIO(b'{"error": []}'), "malformed"),
                              (mocked_error_bytes(error_type="private-SECRET"),
                               "parsed_unrecognized")):
            with self.subTest(state=state):
                result = proposed_error_projection(stream, {
                    "x-request-id": "req_01jbd6g2qdfw2adyrt2az8hz4w",
                    "authorization": "private-SECRET"})
                self.assertEqual(result, {"local_state": state, "diagnostic": {}})
                self.assertNotIn("SECRET", repr(result))

    def test_only_exact_uuid_header_eligible_independently_of_body(self):
        uid = "12345678-1234-1234-1234-123456789abc"
        result = proposed_error_projection(mocked_error_bytes(message_size=5000),
            {"x-request-id": uid, "authorization": "private-SECRET"})
        self.assertEqual(result, {"local_state": "oversize",
                                  "diagnostic": {"request_id": uid}})
        for bad in ("req_01jbd6g2qdfw2adyrt2az8hz4w", "private-SECRET", uid.upper()):
            self.assertEqual(proposed_error_projection(mocked_error_bytes(),
                {"x-request-id": bad})["diagnostic"],
                {"type": "invalid_request_error"})

    def test_header_alone_does_not_count_as_recognized_provider_error(self):
        uid = "12345678-1234-1234-1234-123456789abc"
        result = proposed_error_projection(mocked_error_bytes(error_type="unlisted"),
                                           {"x-request-id": uid})
        self.assertEqual(result, {"local_state": "parsed_unrecognized",
                                  "diagnostic": {"request_id": uid}})


if __name__ == "__main__":
    unittest.main()
