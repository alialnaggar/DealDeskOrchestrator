"""Focused source-classification checks for the evaluation coverage audit."""

from copy import deepcopy
import unittest

from audit_phase1c_evaluation_configuration_coverage import case_facts


class ConfigurationCoverageTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'case_id': 'EVAL-PREP-001', 'source_rows': {
            'lines': [{'product_id': 'P', 'catalog_version': 'V1', 'fulfillment_mode': 'make_to_order',
                       'is_active': True, 'is_sellable': True,
                       'configuration_json': {'selected_options': ['standard']},
                       'attributes_json': {'offered_options': ['standard']}}],
            'bom': [{'finished_product_id': 'P', 'catalog_version': 'V1', 'status': 'active',
                     'configuration_signature_json': {'selected_options': ['standard']}}],
            'compatibility': []}}

    def test_matching_bom_and_option_are_source_facts(self):
        facts = case_facts(self.payload)['lines'][0]
        self.assertEqual(facts['active_matching_bom_pointers'], ['/source_rows/bom/0'])
        self.assertTrue(facts['selected_options_declared'])
        altered = deepcopy(self.payload)
        altered['source_rows']['lines'][0]['configuration_json']['selected_options'] = ['unsupported']
        mismatch = case_facts(altered)['lines'][0]
        self.assertEqual(mismatch['active_matching_bom_pointers'], [])
        self.assertFalse(mismatch['selected_options_declared'])

    def test_regional_denial_remains_separate_from_product_activity(self):
        altered = deepcopy(self.payload)
        altered['source_rows']['compatibility'] = [{
            'rule_type': 'installation_eligibility', 'is_active': True,
            'condition_json': {'eligible': False}}]
        facts = case_facts(altered)
        self.assertTrue(facts['lines'][0]['active_sellable'])
        self.assertEqual(facts['compatibility_rules'][0]['eligible'], False)


if __name__ == '__main__':
    unittest.main()
