import unittest
from copy import deepcopy
from unittest.mock import patch
import json
from argparse import Namespace
import tempfile
from workflow import (manifest, blank, validate_response, deterministic_discrepancies,
                      assert_blind_sources)
from run_free_batch import verify_zero_pricing, prompt, run


class WorkflowTests(unittest.TestCase):
    def test_manifest_and_blind_forms(self):
        rows = manifest()['cases']
        self.assertEqual([x['case_id'] for x in rows],
                         [f'EVAL-PREP-{n:03d}' for n in range(1, 37)] +
                         ['EVAL-PREP-039', 'EVAL-PREP-040', 'EVAL-PREP-041'])
        self.assertEqual(len({x['packet_sha256'] for x in rows}), 39)
        self.assertTrue(all(blank(x)['status'] == 'pending_second_model_review'
                            and all(v['finding'] is None for v in blank(x)['findings'].values())
                            for x in rows))

    def test_pending_is_not_completed(self):
        row = manifest()['cases'][0]
        self.assertTrue(validate_response(blank(row), row, {}))
        altered = deepcopy(blank(row))
        altered['status'] = 'second_model_draft_not_accepted'
        self.assertTrue(validate_response(altered, row, {}))

    def test_arithmetic_is_source_derived(self):
        docs = {'packet': {'source_rows': {'lines': [{'quantity': 2, 'quoted_unit_price': '10.00'}],
                            'credit': {'unbilled_committed_amount': '3.00'}}},
                'credit_scope': {'credit_evidence_scope': {'completeness': 'declared_complete_zero'}}}
        row = manifest()['cases'][0]
        response = blank(row)
        for metric, value in [('quote_total_eur', '20.00'), ('credit_exposure_eur', '23.00')]:
            response['findings']['Pricing' if metric == 'quote_total_eur' else 'Credit']['calculations'].append(
                {'metric': metric, 'value_eur': value, 'formula': 'source arithmetic',
                 'evidence_refs': [{'document': 'packet', 'pointer': '/source_rows/lines/0'}]})
        self.assertEqual(deterministic_discrepancies(response, docs), [])
        response['findings']['Credit']['calculations'][0]['value_eur'] = '0.00'
        self.assertTrue(deterministic_discrepancies(response, docs))

    def test_blind_boundary_refuses_answer_metadata_but_keeps_catalogue_fact(self):
        row = manifest()['cases'][0]
        docs = {'packet': {'source_rows': {'lines': [{'attributes_json':
                    {'archetype_code': 'WORKSTATION'}}]}},
                'provider': {}, 'credit_scope': {'credit_evidence_scope':
                    {'completeness': 'declared_complete_zero'}}}
        assert_blind_sources(row, docs)
        docs['packet']['source_rows']['archetype_id'] = 'STOCK-READY'
        with self.assertRaisesRegex(ValueError, 'metadata'):
            assert_blind_sources(row, docs)

    def test_calculation_and_overall_citations_must_resolve(self):
        row = manifest()['cases'][0]
        docs = {'packet': {'source_rows': {'lines': [{'quantity': 2}]}},
                'provider': {}, 'credit_scope': {'credit_evidence_scope':
                    {'completeness': 'declared_complete_zero'}}}
        response = blank(row)
        ref = {'document': 'packet', 'pointer': '/source_rows/lines/0/quantity'}
        for item in response['findings'].values():
            item.update(finding='no_issue_identified', rationale='Observed source fact',
                        evidence_refs=[ref])
        for role in ('Pricing', 'Credit'):
            response['findings'][role]['calculations'] = [{
                'metric': 'illustrative', 'value_eur': '2.00',
                'formula': 'cited source', 'evidence_refs': [ref]}]
        response['overall'].update(gate='approval_required', rationale='Pending human review',
                                   evidence_refs=[ref])
        response['reviewer'] = dict(model_id='opencode/example-free',
                                    reviewed_at='2026-10-30T17:00:00Z',
                                    source_first_attestation='attached sources only',
                                    assistance_disclosure='AI, not human')
        response['status'] = 'second_model_draft_not_accepted'
        self.assertEqual(validate_response(response, row, docs), [])
        wrong = {'document': 'packet', 'pointer': '/source_rows/lines/99'}
        response['findings']['Pricing']['calculations'][0]['evidence_refs'] = [wrong]
        response['overall']['evidence_refs'] = [wrong]
        self.assertIn('Pricing: calculation citation does not resolve',
                      validate_response(response, row, docs))
        self.assertIn('Overall citation does not resolve',
                      validate_response(response, row, docs))

    def test_free_runner_rejects_changed_price_and_keeps_blind_prompt(self):
        model = {'id': 'beam-free', 'providerID': 'opencode',
                 'cost': [{'input': 0, 'output': 0, 'cache': {'read': 0, 'write': 0}}]}
        class Result:
            @property
            def stdout(self):
                return json.dumps({'data': [model]}).encode()
        with patch('run_free_batch.subprocess.run', return_value=Result()):
            verify_zero_pricing('opencode/beam-free')
            model['cost'][0]['output'] = 1
            with self.assertRaisesRegex(ValueError, 'zero-priced'):
                verify_zero_pricing('opencode/beam-free')
        instruction = prompt('opencode/beam-free', '2026-10-30T17:00:00Z')
        self.assertIn('No tools, web, outside files, prior answers', instruction)
        self.assertNotIn('STOCK-READY', instruction)

    def test_prior_uncertain_sends_never_auto_replay_in_new_attempt_directory(self):
        with tempfile.TemporaryDirectory() as temp, patch('run_free_batch.verify_zero_pricing'), \
                patch('run_free_batch.subprocess.run') as send:
            options = Namespace(model='opencode/beam-free', original_packets=temp,
                                configuration_packets=temp, credit_packets=temp,
                                packages=temp, attempts=temp+'/attempts', responses=temp+'/responses',
                                case_id=['EVAL-PREP-002'], acknowledge_previous_send=None,
                                max_cases=1, timeout_seconds=10)
            run(options)
            send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
