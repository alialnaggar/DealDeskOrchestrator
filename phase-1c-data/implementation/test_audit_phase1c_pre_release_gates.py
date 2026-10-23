"""Gate inventory must reject drift instead of silently treating it as ready."""

from copy import deepcopy
import unittest

from audit_phase1c_pre_release_gates import audit, CALIBRATION_MARKERS
from phase1c_evaluation_review import digest


class PreReleaseInventoryTests(unittest.TestCase):
    def setUp(self):
        from phase1c_evaluation_acceptance import PINNED_V2_SOURCE_SHA256
        from phase1c_configuration_review_scope import BASE_SHA, CONTRACT_SHA, SOURCE_SHA, PINS, EMPTY_PROVIDER_SHA
        self.rules = {'tables': {table: {} for table in
                                 ('products', 'suppliers', 'compatibility_rules', 'agent_execution_log')}}
        for name in ('attributes_json', 'list_price', 'standard_cost'):
            self.rules['tables']['products'][name] = {'resolved_by': 'bounded review'}
        self.rules['tables']['suppliers']['order_calendar_json'] = {'resolved_by': 'bounded review'}
        self.rules['tables']['compatibility_rules']['condition_json'] = {'resolved_by': 'bounded review'}
        self.rules['tables']['agent_execution_log']['output_json'] = {'review_before_generation': 'runtime needed'}
        self.calibration = '\n'.join(CALIBRATION_MARKERS)
        payload = {'status': 'development_reader_selected_sources_not_evaluation_answers',
                   'deal_count': 152, 'deal_ids': [f'GEN-TEST-{n:03d}' for n in range(1, 101)]
                   + [f'OTHER-{n:03d}' for n in range(52)]}
        self.development = {'payload': payload, 'sha256': digest(payload)}
        self.extension = {'schema_version': 1, 'extension_id': 'configuration-v1',
                          'source_definition_sha256': SOURCE_SHA,
                          'base_source_definition_sha256': BASE_SHA,
                          'business_contract_sha256': CONTRACT_SHA,
                          'input_case_count': 3, 'independently_reviewed_answers': 0,
                          'cases': [{'case_id': cid, 'packet_sha256': sha,
                                     'provider_file_sha256': EMPTY_PROVIDER_SHA}
                                    for cid, sha in PINS.items()]}

    def test_field_and_calibration_drift_fail_before_report(self):
        from unittest.mock import patch
        # The v2 index has its own exact pin check; isolate the remaining gates.
        with patch('audit_phase1c_pre_release_gates.check_v2_index'):
            base = (self.rules, self.calibration, self.development, {}, self.extension)
            self.assertFalse(audit(*base)['ready_for_generation'])
            changed = deepcopy(self.rules)
            changed['tables']['agent_execution_log']['output_json']['resolved_by'] = 'unsupported'
            with self.assertRaises(ValueError):
                audit(changed, *base[1:])
            with self.assertRaises(ValueError):
                audit(self.rules, '', *base[2:])
            changed = deepcopy(self.development)
            changed['payload']['deal_ids'].remove('GEN-TEST-100')
            with self.assertRaises(ValueError):
                audit(self.rules, self.calibration, changed, {}, self.extension)
            changed = deepcopy(self.extension)
            changed['independently_reviewed_answers'] = 1
            with self.assertRaises(ValueError):
                audit(self.rules, self.calibration, self.development, {}, changed)


if __name__ == '__main__':
    unittest.main()
