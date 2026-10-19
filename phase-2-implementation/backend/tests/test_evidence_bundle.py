"""Offline contract checks; no model, database or new dependency required."""

from dataclasses import replace
from datetime import date, datetime, time, timezone
from decimal import Decimal
import json
import unittest
from uuid import UUID

from dealdesk_phase2.contracts import RunContextV1
from dealdesk_phase2.evidence_bundle import seal, unseal
from dealdesk_phase2.phase1c_adapter import PinnedBundleV1


class EvidenceBundleTests(unittest.TestCase):
    def sample(self):
        return {
            "run": {"run_id": UUID("00000000-0000-4000-8000-000000010001"),
                    "as_of_at": datetime(2026, 9, 1, 12, tzinfo=timezone.utc)},
            "facts": {"required_hours": {("assembly", "workforce"): Decimal("5.00")},
                      "arrival": date(2026, 9, 4), "cutoff": time(15, 30),
                      "values": (None, True, 0, "évidence", ["str", "x"])}
        }

    def test_round_trip_is_canonical_and_preserves_types(self):
        original = self.sample()
        raw, digest, size = seal(original)
        restored = unseal(raw, digest)
        self.assertEqual(restored, original)
        self.assertIsInstance(next(iter(restored["facts"]["required_hours"])), tuple)
        self.assertEqual(str(restored["facts"]["required_hours"][("assembly", "workforce")]), "5.00")
        self.assertEqual(size, len(raw.encode("utf-8")))
        self.assertEqual(seal({"facts": original["facts"], "run": original["run"]}),
                         (raw, digest, size))
        restored["facts"]["arrival"] = date(2026, 9, 5)
        self.assertEqual(unseal(raw, digest), original)

    def test_tampering_and_noncanonical_encoding_fail(self):
        raw, digest, _ = seal(self.sample())
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            unseal(raw.replace("évidence", "invented"), digest)
        alternate = json.dumps(json.loads(raw), indent=2, ensure_ascii=False)
        from hashlib import sha256
        with self.assertRaisesRegex(ValueError, "Noncanonical"):
            unseal(alternate, sha256(alternate.encode()).hexdigest())

    def test_unsupported_or_ambiguous_types_fail(self):
        for value in (1.2, {1, 2}, object(), datetime(2026, 9, 1), Decimal("NaN")):
            with self.subTest(value=repr(value)), self.assertRaises(TypeError):
                seal({"bad": value})

    def test_context_and_pinned_payload_identity(self):
        raw, digest, size = seal(self.sample())
        context = RunContextV1(
            assessment_id="A-1", phase1c_run_id=UUID("00000000-0000-4000-8000-000000010001"),
            original_deal_id="D-1", submission_ref="D-1",
            as_of_at=datetime(2026, 9, 1, 12, tzinfo=timezone.utc),
            data_snapshot_ref="FIXTURE-1", catalog_version="CAT-1", policy_set_code="POL-1",
            config_hash="CONFIG", source_input_digest="a" * 64, bundle_sha256=digest)
        pinned = PinnedBundleV1(context, raw, size)
        self.assertEqual(pinned.decode(), self.sample())
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            replace(pinned, context=replace(context, bundle_sha256="0" * 64)).decode()
        with self.assertRaisesRegex(ValueError, "timezone aware"):
            replace(context, as_of_at=datetime(2026, 9, 1))


if __name__ == "__main__":
    unittest.main()
