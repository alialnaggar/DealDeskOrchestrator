import unittest
from copy import deepcopy
from unittest.mock import patch
import json
from argparse import Namespace
import tempfile
from pathlib import Path
from workflow import (manifest, blank, validate_response, deterministic_discrepancies,
                      assert_blind_sources)
from run_free_batch import verify_zero_pricing, prompt, run


class WorkflowTests(unittest.TestCase):
    def test_source_neutral_example_is_not_an_evaluation_answer(self):
        fixture = json.loads((Path(__file__).parent / 'source_neutral_example.json').read_text())
        self.assertEqual(fixture['status'], 'illustrative_contract_fixture_not_evaluation_source_or_answer')
        self.assertEqual(fixture['row']['case_id'], 'EXAMPLE-ONLY')
        self.assertNotIn('EVAL-PREP-', json.dumps(fixture))
        self.assertEqual(validate_response(fixture['response'], fixture['row'], fixture['documents']), [])
        self.assertEqual(deterministic_discrepancies(fixture['response'], fixture['documents']), [])

    def test_nonfinite_amounts_wrong_metric_role_and_false_abstentions_fail(self):
        fixture = json.loads((Path(__file__).parent / 'source_neutral_example.json').read_text())
        row, docs, original = fixture['row'], fixture['documents'], fixture['response']
        for bad in ('NaN', 'Infinity', '1e2', '0.001', 20.0):
            response = deepcopy(original)
            response['findings']['Pricing']['calculations'][0]['value_eur'] = bad
            self.assertTrue(any('finite decimal EUR' in e
                                for e in validate_response(response, row, docs)))
        response = deepcopy(original)
        response['findings']['Approval']['calculations'] = [deepcopy(
            original['findings']['Pricing']['calculations'][0])]
        self.assertTrue(any('required metric belongs to Pricing' in e
                            for e in validate_response(response, row, docs)))
        response = deepcopy(original)
        response['findings']['Credit']['abstention_reason'] = 'false abstention'
        self.assertTrue(any('only allowed for abstain' in e
                            for e in validate_response(response, row, docs)))
        response = deepcopy(original)
        response['overall']['human_actions'] = []
        self.assertTrue(any('Overall gate/actions/rationale incomplete' in e
                            for e in validate_response(response, row, docs)))

    def test_unknown_credit_abstention_is_explicit_and_cited(self):
        fixture = json.loads((Path(__file__).parent / 'source_neutral_example.json').read_text())
        row, docs, response = fixture['row'], fixture['documents'], fixture['response']
        docs['credit_scope']['credit_evidence_scope']['completeness'] = 'explicitly_incomplete_unknown'
        credit = response['findings']['Credit']
        credit['finding'] = 'abstain'
        credit['abstention_reason'] = 'The invoice population is not established.'
        credit['calculations'] = []
        self.assertEqual(validate_response(response, row, docs), [])
        self.assertEqual(deterministic_discrepancies(response, docs), [])
        credit['calculations'] = [{'metric': 'overdue_ar_eur', 'value_eur': '0.00',
                                    'formula': 'empty list', 'evidence_refs': credit['evidence_refs']}]
        self.assertTrue(any('incomplete population' in e
                            for e in deterministic_discrepancies(response, docs)))

    def test_source_neutral_nonempty_invoice_needs_payment_and_scope_citations(self):
        fixture = json.loads((Path(__file__).parent / 'source_neutral_example.json').read_text())
        docs, response = fixture['documents'], fixture['response']
        docs['credit_scope']['credit_evidence_scope']['completeness'] = 'declared_complete_nonempty'
        docs['packet']['source_rows']['receivables'] = [
            {'original_amount': '100.00', 'outstanding_amount': '80.00', 'status': 'Overdue'}]
        docs['packet']['source_rows']['payments'] = [{'paid_amount': '20.00'}]
        credit = response['findings']['Credit']['calculations'][0]
        credit.update(metric='overdue_ar_eur', value_eur='80.00',
                      formula='EUR 100.00 original less EUR 20.00 paid', evidence_refs=[
                          {'document': 'packet', 'pointer': '/source_rows/receivables/0'},
                          {'document': 'packet', 'pointer': '/source_rows/payments/0'},
                          {'document': 'credit_scope', 'pointer': '/credit_evidence_scope/completeness'}])
        self.assertEqual(deterministic_discrepancies(response, docs), [])
        credit['evidence_refs'].pop(1)
        self.assertTrue(any('invoice/payment source citations missing' in e
                            for e in deterministic_discrepancies(response, docs)))

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
        lines = {'document': 'packet', 'pointer': '/source_rows/lines/0'}
        commitment = {'document': 'packet', 'pointer': '/source_rows/credit/unbilled_committed_amount'}
        scope = {'document': 'credit_scope', 'pointer': '/credit_evidence_scope/completeness'}
        for metric, value in [('quote_total_eur', '20.00'), ('credit_exposure_eur', '23.00')]:
            response['findings']['Pricing' if metric == 'quote_total_eur' else 'Credit']['calculations'].append(
                {'metric': metric, 'value_eur': value, 'formula': 'source arithmetic',
                 'evidence_refs': [lines] if metric == 'quote_total_eur' else [lines, commitment, scope]})
        self.assertEqual(deterministic_discrepancies(response, docs), [])
        response['findings']['Credit']['calculations'][0]['value_eur'] = '0.00'
        self.assertTrue(deterministic_discrepancies(response, docs))

    def test_required_arithmetic_needs_relevant_references_and_no_duplicate(self):
        docs = {'packet': {'source_rows': {'lines': [
                    {'quantity': 2, 'quoted_unit_price': '10.00'},
                    {'quantity': 1, 'quoted_unit_price': '5.00'}],
                    'credit': {'unbilled_committed_amount': '3.00'}}},
                'credit_scope': {'credit_evidence_scope': {'completeness': 'declared_complete_zero'}}}
        response = blank(manifest()['cases'][0])
        calculation = {'metric': 'quote_total_eur', 'value_eur': '25.00',
                       'formula': '2*10+1*5', 'evidence_refs': [
                           {'document': 'packet', 'pointer': '/source_rows/lines/0'}]}
        response['findings']['Pricing']['calculations'] = [calculation, deepcopy(calculation)]
        response['findings']['Credit']['finding'] = 'abstain'
        issues = deterministic_discrepancies(response, docs)
        self.assertTrue(any('duplicate' in issue for issue in issues))
        self.assertTrue(any('line 1 source citation missing' in issue for issue in issues))

    def test_unknown_credit_population_cannot_be_numeric_clearance(self):
        docs = {'packet': {'source_rows': {'lines': [{'quantity': 2, 'quoted_unit_price': '10.00'}],
                            'credit': {'unbilled_committed_amount': '3.00'}}},
                'credit_scope': {'completeness': 'explicitly_incomplete_unknown'}}
        response = blank(manifest()['cases'][0])
        response['findings']['Pricing']['finding'] = 'abstain'
        response['findings']['Credit']['finding'] = 'abstain'
        response['findings']['Credit']['calculations'].append({
            'metric': 'credit_exposure_eur', 'value_eur': '0.00', 'formula': 'empty rows',
            'evidence_refs': [{'document': 'credit_scope', 'pointer': '/completeness'}]})
        self.assertTrue(any('incomplete population' in issue
                            for issue in deterministic_discrepancies(response, docs)))

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
                                   evidence_refs=[ref], human_actions=['Obtain human review.'])
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
                                case_id=['EVAL-PREP-002'],
                                max_cases=1, timeout_seconds=10)
            run(options)
            send.assert_not_called()

    def test_batch_requires_a_valid_fresh_pilot_first(self):
        with tempfile.TemporaryDirectory() as temp, patch('run_free_batch.verify_zero_pricing'), \
                patch('run_free_batch.subprocess.run') as send:
            options = Namespace(model='opencode/beam-free', original_packets=temp,
                                configuration_packets=temp, credit_packets=temp,
                                packages=temp, attempts=temp+'/attempts', responses=temp+'/responses',
                                case_id=['EVAL-PREP-005'], max_cases=3, timeout_seconds=10)
            with self.assertRaisesRegex(ValueError, 'First validate one new-case pilot'):
                run(options)
            send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
