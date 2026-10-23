"""Replay supplemental Configuration inputs in isolated PostgreSQL transactions."""

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unittest

from render_phase1c_configuration_extension import build, OUTPUT, HERE, render
from test_phase1c_evaluation_cases import TABLE_ORDER, FORBIDDEN, keys_in

try:
    import psycopg
    from psycopg import sql
    from psycopg.types.json import Jsonb
except ImportError:
    psycopg = None


class ConfigurationExtensionSources(unittest.TestCase):
    def test_versioned_source_identity_and_failure_shapes(self):
        inputs, manifest = build()
        self.assertEqual(len(inputs['cases']), 3)
        self.assertEqual(manifest['independently_reviewed_answers'], 0)
        self.assertEqual([case['case_id'] for case in inputs['cases']],
                         ['EVAL-CONFIG-001', 'EVAL-CONFIG-002', 'EVAL-CONFIG-003'])
        self.assertEqual([case['tables']['deal_lines'][0]['configuration_json']['selected_options']
                          for case in inputs['cases'][:2]], [['unsupported'], ['standard', 'alternate']])
        self.assertEqual(len({case['tables']['deal_runs'][0]['run_id'] for case in inputs['cases']}), 3)
        self.assertEqual(inputs['cases'][2]['tables']['compatibility_rules'][0]['rule_type'], 'requires_product')
        self.assertFalse(keys_in(inputs) & FORBIDDEN)
        for case in inputs['cases']:
            self.assertTrue(case['tables']['deals'][0]['deal_id'].startswith('EVALCFG-'))
            self.assertEqual(case['provider_manifest']['records'], [])


@unittest.skipUnless(psycopg is not None and os.environ.get('EVALUATION_DATABASE_URL'),
                     'Dedicated disposable PostgreSQL evaluation database required')
class ConfigurationExtensionDatabase(unittest.TestCase):
    def test_two_connection_replay_and_source_only_packets(self):
        inputs, manifest = build()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path = Path(os.environ.get('PHASE1C_CONFIGURATION_PACKETS') or first)
            second_path = Path(second)
            one = self.export(inputs, manifest, first_path)
            two = self.export(inputs, manifest, second_path)
            self.assertEqual(one, two)
            expected = {'packet_index.json'} | {
                f'EVAL-CONFIG-{i:03d}{suffix}.json' for i in (1, 2, 3) for suffix in ('', '-provider')}
            self.assertEqual({p.name for p in first_path.iterdir()}, expected)
            self.assertEqual({p.name for p in second_path.iterdir()}, expected)
            self.assertEqual({name: (first_path / name).read_bytes() for name in expected},
                             {name: (second_path / name).read_bytes() for name in expected})
            pinned = OUTPUT / 'packet_index.json'
            if pinned.exists():
                self.assertEqual(json.loads(pinned.read_text()), one)

    def export(self, inputs, manifest, output):
        from phase1c_reader import load_provider_evidence, read_run
        from phase1c_evaluation_input import (prepare_heldout_review_input, review_source_digest,
                                               verify_review_input)
        from validate_phase1c_generated_rows import load_rows, validate_rows
        import yaml

        output.mkdir(parents=True, exist_ok=True)
        development = json.loads((HERE / 'phase1c_development_source_exclusions.json').read_text())
        historical = json.loads((HERE / 'phase1c_historical_source_exclusions.json').read_text())
        contract = inputs['business_contract']
        row_contract = yaml.safe_load((HERE / 'phase1c_data_contract.yaml').read_text())
        row_contract['catalogue_extensions']['dependency_pilot'] = json.loads(
            (HERE / 'phase1c_configuration_extension_contract.json').read_text())
        index_rows = []
        with psycopg.connect(os.environ['EVALUATION_DATABASE_URL']) as conn:
            conn.execute('SET search_path TO deal_desk, public')
            self.assertEqual(conn.execute('SELECT count(*) FROM deals').fetchone()[0], 0)
            for name in ('phase1c_buildable_master.sql', 'phase1c_sellable_catalogue.sql'):
                for statement in re.findall(r'^INSERT INTO .*?;', (HERE / name).read_text(), re.M | re.S):
                    conn.execute(statement)
            for statement in re.findall(r'^INSERT INTO .*?;',
                                        (HERE / 'phase1c_configuration_extension_master.sql').read_text(), re.M | re.S):
                conn.execute(statement)
            for case in inputs['cases']:
                with self.subTest(case=case['case_id']), conn.transaction(force_rollback=True):
                    tables = case['tables']
                    for table in TABLE_ORDER:
                        for row in tables.get(table, []):
                            if table == 'deal_runs':
                                conn.execute("UPDATE deals SET deal_status='Submitted' WHERE deal_id=%s",
                                             (row['deal_id'],))
                            statement = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                                sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier, row)),
                                sql.SQL(',').join(sql.Placeholder() for _ in row))
                            conn.execute(statement, [Jsonb(v) if isinstance(v, (dict, list)) else v
                                                     for v in row.values()])
                    conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
                    errors = validate_rows(load_rows(conn), row_contract)['errors']
                    line_id = tables['deal_lines'][0]['deal_line_id']
                    if case['case_id'] in ('EVAL-CONFIG-001', 'EVAL-CONFIG-002'):
                        self.assertEqual(errors, [
                            f'deal_lines.{line_id}: make-to-order selected option must be one offered code',
                            f'deal_lines.{line_id}: selected BOM missing or ambiguous'])
                    else:
                        self.assertEqual(errors, [])
                    with tempfile.TemporaryDirectory() as temporary:
                        provider = Path(temporary) / 'provider.json'
                        provider.write_text(render(case['provider_manifest']))
                        resolver = load_provider_evidence(provider)
                        run_id = tables['deal_runs'][0]['run_id']
                        bundle = read_run(conn, run_id, commercial_rule_mode='compiled',
                                          digital_evidence_resolver=resolver)
                        packet = prepare_heldout_review_input(
                            bundle, case_id=case['case_id'], development_manifest=development,
                            historical_manifest=historical, business_contract=contract)
                        repeated = prepare_heldout_review_input(
                            read_run(conn, run_id, commercial_rule_mode='compiled',
                                     digital_evidence_resolver=resolver), case_id=case['case_id'],
                            development_manifest=development, historical_manifest=historical,
                            business_contract=contract)
                    self.assertEqual(packet, repeated)
                    self.assertTrue(verify_review_input(
                        packet, expected_case_id=case['case_id'],
                        expected_source_digest=review_source_digest(bundle, contract),
                        expected_business_contract=contract))
                    self.assertFalse(keys_in(packet) & FORBIDDEN)
                    line = packet['payload']['source_rows']['lines'][0]
                    selected = line['configuration_json'].get('selected_options', [])
                    offered = line['attributes_json'].get('offered_options', [])
                    if case['case_id'] == 'EVAL-CONFIG-001':
                        self.assertFalse(all(item in offered for item in selected))
                    elif case['case_id'] == 'EVAL-CONFIG-002':
                        self.assertTrue(all(item in offered for item in selected))
                    if case['case_id'] in ('EVAL-CONFIG-001', 'EVAL-CONFIG-002'):
                        self.assertEqual(packet['payload']['source_rows']['bom'], [])
                    else:
                        facts = bundle['facts']['compatibility']
                        self.assertEqual([(fact['compatibility_rule_id'], fact['status']) for fact in facts],
                                         [('EVALCFG-003-REQUIRES-ADDON', 'fail')])
                    self.assertEqual(conn.execute('SELECT count(*) FROM agent_execution_log').fetchone()[0], 0)
                    proof = render(case['provider_manifest'])
                    (output / (case['case_id'] + '.json')).write_text(render(packet))
                    (output / (case['case_id'] + '-provider.json')).write_text(proof)
                    index_rows.append({'case_id': case['case_id'], 'packet_sha256': packet['sha256'],
                                       'provider_file_sha256': hashlib.sha256(proof.encode()).hexdigest()})
            self.assertEqual(conn.execute('SELECT count(*) FROM deals').fetchone()[0], 0)
            conn.rollback()
        index = {'schema_version': 1, 'extension_id': 'configuration-v1',
                 'input_case_count': 3, 'independently_reviewed_answers': 0,
                 'source_definition_sha256': manifest['inputs_sha256'],
                 'base_source_definition_sha256': inputs['base_source_definition_sha256'],
                 'business_contract_sha256': hashlib.sha256(json.dumps(
                     contract, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                 'cases': index_rows}
        (output / 'packet_index.json').write_text(render(index))
        return index


if __name__ == '__main__':
    unittest.main()
