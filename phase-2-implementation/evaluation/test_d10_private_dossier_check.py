"""D10 private read-only validation; never put draft answers in this tree."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import d10_private_dossier_check as d10

HERE = Path(__file__).parent
MANIFEST = HERE / "supervisor-demo-d10-private-manifest-2026-11-09.json"
DOSSIER = Path("/tmp/opencode/d10_private_pilot_2026-11-09/dossier.md")
ROOT = Path("/home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c")
PACKETS = Path("/tmp/opencode/phase1c_original_packets")


class PrivateDossierTests(unittest.TestCase):
    def test_pointer_resolution_is_strict(self):
        obj = {"a/b": [{"~x": 3}], "empty": []}
        self.assertEqual(d10.follow(obj, "/a~1b/0/~0x"), 3)
        self.assertEqual(d10.follow(obj, "/empty"), [])
        for pointer in ("a", "/a~2b", "/a~1b/1", "/empty/0", "/a~1b/-1"):
            with self.assertRaises((KeyError, IndexError, ValueError)):
                d10.follow(obj, pointer)

    @unittest.skipUnless(DOSSIER.is_file() and ROOT.is_dir() and PACKETS.is_dir(),
                         "Private evidence unavailable; only synthetic test runs")
    def test_private_dossier_and_manifest_are_source_bound(self):
        manifest = json.loads(MANIFEST.read_text())
        result = d10.validate(DOSSIER, manifest, ROOT, PACKETS)
        self.assertEqual(result["cases"], 6)
        self.assertEqual(result["source_export_pairs_verified"], 6)
        self.assertEqual(result["acceptances_created"], 0)
        self.assertGreaterEqual(result["citation_pointers_resolved"], 36)
        self.assertGreaterEqual(result["rule_identifiers_resolved"], 6)
        for key, value in (("accepted_cases", 1), ("status", "accepted")):
            changed = copy.deepcopy(manifest)
            changed[key] = value
            with self.assertRaisesRegex(ValueError, "manifest status"):
                d10.validate(DOSSIER, changed, ROOT, PACKETS)
        changed = copy.deepcopy(manifest)
        changed["sources"]["EVAL-PREP-001"]["packet_payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source pin differs"):
            d10.validate(DOSSIER, changed, ROOT, PACKETS)
        changed = copy.deepcopy(manifest)
        changed["private_dossier_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dossier digest"):
            d10.validate(DOSSIER, changed, ROOT, PACKETS)

    @unittest.skipUnless(DOSSIER.is_file() and ROOT.is_dir() and PACKETS.is_dir(),
                         "Private evidence unavailable; only synthetic test runs")
    def test_bad_private_citation_fails_without_exposing_answers(self):
        # Temp private copy is outside Git and is deleted automatically.
        text = DOSSIER.read_text().replace("packet:/source_rows/lines/0",
                                            "packet:/source_rows/lines/999", 1)
        with tempfile.TemporaryDirectory(prefix="d10-citation-", dir="/tmp/opencode") as tmp:
            path = Path(tmp) / "dossier.md"
            path.write_text(text)
            changed = json.loads(MANIFEST.read_text())
            import hashlib
            changed["private_dossier_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "unresolved packet citation"):
                d10.validate(path, changed, ROOT, PACKETS)


if __name__ == "__main__":
    unittest.main()
