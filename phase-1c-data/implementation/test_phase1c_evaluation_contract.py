"""Audit arithmetic, product matching and fail-closed input identity."""
from decimal import Decimal
from datetime import date
import json
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from audit_phase1c_evaluation_contract import age_observation, audit_case, audit_inputs, digest, quote_credit_arithmetic, advance_workdays, offer_operation_projections


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
                     'credit': {'commitments_as_of_at': '2026-09-02T11:00:00+00:00', 'credit_limit':'10000', 'unbilled_committed_amount':'0'},
                     'receivables': [], 'bom': [],
                     'rules': {'pricing_rules':[{'rule_type':'category_margin_floor','scope_value':'fixture','condition_json':{'margin_pct_lt':8}}]},
                     'lines': [{'product_id': 'finished', 'standard_cost': '715',
                                'fulfillment_mode': 'make_to_order', 'installation_requested': False,
                                'quantity':'1', 'quoted_unit_price':'1000', 'list_price':'1050', 'category':'fixture', 'configuration_json':{}}],
                     'bom_lines': [{'component_product_id': 'component', 'standard_cost': '50'}],
                     'supplier_offers': [{'product_id': 'component', 'unit_cost': '47.50', 'currency_code': 'EUR'}],
                     'compatibility': [], 'cost_parameters': None}}
        offer = audit_case(payload, Decimal(24))['offers'][0]
        self.assertEqual(len(offer['matching_standard_costs']), 1)
        self.assertEqual(offer['matching_standard_costs'][0]['offer_minus_standard_cost'], '-2.50')
        self.assertIn('/bom_lines/', offer['matching_standard_costs'][0]['pointer'])
        payload['business_contract'] = {'evidence_age': {'snapshot_max_elapsed_hours': 24}}
        with self.assertRaisesRegex(ValueError, 'declared business contract'):
            audit_case(payload, Decimal(48))

    def test_full_billed_quantity_and_multiline_credit_arithmetic(self):
        rows = {'lines': [
            {'quantity':'24','quoted_unit_price':'80','standard_cost':'50','list_price':'100',
             'category':'fixture','configuration_json':{'units_per_period':2}},
            {'quantity':'2','quoted_unit_price':'100','standard_cost':'60','list_price':'120','category':'fixture'}],
            'credit':{'credit_limit':'1000','unbilled_committed_amount':'100'},
            'receivables':[{'outstanding_amount':'50'}],
            'rules':{'pricing_rules':[{'rule_type':'category_margin_floor','scope_value':'fixture','condition_json':{'margin_pct_lt':8}}]}}
        report = quote_credit_arithmetic(rows)
        self.assertEqual(Decimal(report['deal_revenue_eur']), Decimal('2120'))
        self.assertEqual(Decimal(report['exposure_eur']), Decimal('2270'))
        self.assertEqual(Decimal(report['credit_excess_pct']), Decimal('127'))
        self.assertEqual(Decimal(report['deal_margin_pct']), Decimal(800) * 100 / Decimal(2120))

    def test_workday_projection_respects_weekend_and_declared_holiday(self):
        self.assertEqual(advance_workdays(date(2026,9,4),1,[1,2,3,4,5],['2026-09-07']),date(2026,9,8))
        with self.assertRaises(ValueError):
            advance_workdays(date(2026,9,4),1,[])

    def test_missing_separate_day_operation_does_not_invent_arrival(self):
        payload = {'run_context':{'as_of_at':'2026-09-01T12:00:00+00:00'},'source_rows':{
            'deal':{'destination_country_code':'DE','destination_region':'NW','shipping_service_code':'standard','requested_delivery_date':'2026-09-09'},
            'lines':[{'product_id':'finished','fulfillment_mode':'make_to_order','configuration_json':{},'quantity':'2'}],
            'bom':[{'bom_id':'B','finished_product_id':'finished','configuration_signature_json':{},'status':'active','output_quantity':'1'}],
            'bom_lines':[{'bom_id':'B','component_product_id':'component'}],
            'supplier_offers':[{'product_id':'component','lead_days_min':4,'lead_days_mode':4,'lead_days_max':4,
                'is_active':True,'valid_from':'2026-08-01','valid_to':'2026-09-30',
                'order_calendar_json':{'time_zone':'Europe/Amsterdam','working_weekdays':[1,2,3,4,5],'holiday_dates':[]}}],
            'shipping_lanes':[{'is_active':True,'destination_country_code':'DE','destination_region':'NW','shipping_service_code':'standard','origin_location_id':'W','dispatch_weekdays_json':[1,2,3,4,5],'transit_workdays':1}],
            'requirements':[{'bom_id':'B','status':'active','operation_seq':n,'capability_code':code,'resource_type':code,'batch_size':4,'hours_per_unit':'0.5','setup_hours':'0.5'} for n,code in [(1,'assembly'),(2,'test')]],
            'production_capacity':[{'capacity_id':code,'capacity_date':'2026-09-07','capability_code':code,'resource_type':code,'location_id':'W','status':'active','snapshot_at':'2026-09-01T11:00:00+00:00','available_capacity_hours':'8','allocated_capacity_hours':'0'} for code in ['assembly','test']]}}
        result = offer_operation_projections(payload, Decimal(24))
        self.assertTrue(all(r['missing_operation_observation']=='test' and r['indicative_arrival'] is None for r in result))
        slot=dict(payload['source_rows']['production_capacity'][1],capacity_id='later-test',capacity_date='2026-09-08')
        payload['source_rows']['production_capacity'].append(slot)
        result=offer_operation_projections(payload, Decimal(24))
        self.assertTrue(all(r['indicative_arrival']=='2026-09-09' for r in result))
        offer=payload['source_rows']['supplier_offers'][0]
        offer['is_active']=False
        self.assertNotIn('indicative_arrival', offer_operation_projections(payload, Decimal(24))[0])
        offer['is_active']=True
        offer['valid_to']='2026-08-31'
        self.assertNotIn('indicative_arrival', offer_operation_projections(payload, Decimal(24))[0])

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
            payload = {'case_id':'EVAL-PREP-001','business_contract':{'contract_id':'unexpected'}}
            (directory/'EVAL-PREP-001.json').write_text(json.dumps({'payload':payload,'sha256':digest(payload)}))
            index['cases'][0]['packet_sha256'] = digest(payload)
            index['cases'][0]['provider_file_sha256'] = hashlib.sha256(b'{}').hexdigest()
            index['business_contract_sha256'] = 'different-contract'
            with self.assertRaisesRegex(ValueError, 'business contract hash'):
                audit_inputs(index,directory)



if __name__ == '__main__':
    unittest.main()
