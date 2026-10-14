"""Audit arithmetic, product matching and fail-closed input identity."""
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from audit_phase1c_evaluation_contract import age_observation, audit_case, audit_inputs, digest


class ContractAuditTests(unittest.TestCase):
    def test_time_boundary_and_future_observation(self):
        now = '2026-09-02T12:00:00+00:00'
        self.assertTrue(age_observation('2026-09-01T12:00:00+00:00', now, Decimal(24))['within_comparison_window'])
        self.assertFalse(age_observation('2026-09-01T11:59:59+00:00', now, Decimal(24))['within_comparison_window'])
        self.assertTrue(age_observation('2026-09-02T13:00:00+00:00', now, Decimal(24))['future_dated'])
        with self.assertRaises(ValueError):
            age_observation('2026-09-02T12:00:00', now, Decimal(24))

    def test_component_offer_does_not_use_finished_cost(self):
        payload = {'case_id': 'example', 'run_context': {'as_of_at': '2026-09-02T12:00:00+00:00'},
                   'source_rows': {'inventory': [], 'production_capacity': [], 'digital_capacity': [],
                     'credit': {'commitments_as_of_at': '2026-09-02T11:00:00+00:00'},
                     'lines': [{'product_id': 'finished', 'standard_cost': '715',
                                'fulfillment_mode': 'make_to_order', 'installation_requested': False}],
                     'bom_lines': [{'component_product_id': 'component', 'standard_cost': '50'}],
                     'supplier_offers': [{'product_id': 'component', 'unit_cost': '47.50', 'currency_code': 'EUR'}],
                     'compatibility': [], 'cost_parameters': None}}
        offer = audit_case(payload, Decimal(24))['offers'][0]
        self.assertEqual(len(offer['matching_standard_costs']), 1)
        self.assertEqual(offer['matching_standard_costs'][0]['offer_minus_standard_cost'], '-2.50')
        self.assertIn('/bom_lines/', offer['matching_standard_costs'][0]['pointer'])

    def test_index_completeness_and_tampered_source(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'exactly'):
                audit_inputs({'cases': []}, directory)
            index = {'cases': [{'case_id': f'EVAL-PREP-{i:03}', 'packet_sha256': digest({}),
                                'provider_file_sha256': 'wrong'} for i in range(1, 37)]}
            (directory / 'EVAL-PREP-001.json').write_text(json.dumps({'payload': {'tampered': True}, 'sha256': digest({})}))
            (directory / 'EVAL-PREP-001-provider.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'packet hash'):
                audit_inputs(index, directory)
            (directory / 'EVAL-PREP-001.json').write_text(json.dumps({'payload': {}, 'sha256': digest({})}))
            with self.assertRaisesRegex(ValueError, 'provider hash'):
                audit_inputs(index, directory)


if __name__ == '__main__':
    unittest.main()
