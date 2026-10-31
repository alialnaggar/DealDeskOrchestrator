"""Ensure preflight diagnostics cannot be counted as specialist review cases."""

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from phase1c_configuration_review_scope import ROOT, audit


class ReviewScopeTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((ROOT / 'packet_index.json').read_text())

    def test_changed_index_and_preflight_promotion_fail_closed(self):
        for change in ('source', 'promotion', 'hash', 'answer'):
            with self.subTest(change=change):
                index = deepcopy(self.index)
                if change == 'source':
                    index['source_definition_sha256'] = '0' * 64
                elif change == 'promotion':
                    index['cases'][1], index['cases'][2] = index['cases'][2], index['cases'][1]
                elif change == 'hash':
                    index['cases'][2]['packet_sha256'] = '0' * 64
                else:
                    index['independently_reviewed_answers'] = 1
                with self.assertRaises(ValueError):
                    audit(index, Path('/not-read-before-index-validation'))

    def test_verified_packets_yield_only_blank_039_candidate(self):
        packet_dir = os.environ.get('PHASE1C_CONFIGURATION_PACKETS')
        if not packet_dir:
            self.skipTest('Exported PostgreSQL packets required')
        report, candidate, template = audit(self.index, Path(packet_dir))
        self.assertEqual(report['diagnostic_preflight_only'], ['EVAL-PREP-037', 'EVAL-PREP-038'])
        self.assertEqual(report['six_responsibility_review_candidate'], ['EVAL-PREP-039'])
        self.assertEqual(report['accepted_answers'], 0)
        self.assertFalse(report['ready_for_generation'])
        self.assertEqual([row['case_id'] for row in candidate['cases']], ['EVAL-PREP-039'])
        self.assertEqual(template['independently_reviewed_answers'], 0)
        self.assertEqual(template['cases'][0]['review_status'], 'pending')
        self.assertTrue(all(value['finding'] is None for value in
                            template['cases'][0]['findings'].values()))
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp)
            for cid in ('EVAL-PREP-037', 'EVAL-PREP-038', 'EVAL-PREP-039'):
                for suffix in ('', '-provider'):
                    filename = f'{cid}{suffix}.json'
                    (changed / filename).write_bytes((Path(packet_dir) / filename).read_bytes())
            target = changed / 'EVAL-PREP-037-provider.json'
            target.write_bytes(target.read_bytes() + b' ')
            with self.assertRaises(ValueError):
                audit(self.index, changed)


if __name__ == '__main__':
    unittest.main()
