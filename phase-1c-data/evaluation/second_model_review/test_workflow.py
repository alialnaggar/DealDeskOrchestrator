import unittest
from copy import deepcopy
from workflow import manifest, blank, validate_response, deterministic_discrepancies


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


if __name__ == '__main__':
    unittest.main()
