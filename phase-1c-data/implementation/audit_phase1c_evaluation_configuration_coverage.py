"""Inventory pinned v2 configuration source coverage without assigning answers."""

import argparse
import hashlib
import json
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def case_facts(payload):
    rows = payload['source_rows']
    line_facts = []
    for i, line in enumerate(rows['lines']):
        matching_boms = [j for j, bom in enumerate(rows['bom'])
                         if bom['finished_product_id'] == line['product_id']
                         and bom['catalog_version'] == line['catalog_version']
                         and bom['configuration_signature_json'] == line['configuration_json']
                         and bom['status'] == 'active']
        selected = line['configuration_json'].get('selected_options', [])
        offered = line['attributes_json'].get('offered_options', [])
        line_facts.append({
            'pointer': f'/source_rows/lines/{i}',
            'product_id': line['product_id'],
            'fulfillment_mode': line['fulfillment_mode'],
            'active_sellable': line['is_active'] and line['is_sellable'],
            'configuration_nonempty': bool(line['configuration_json']),
            'selected_options': selected,
            'selected_options_declared': all(option in offered for option in selected),
            'active_matching_bom_pointers': [f'/source_rows/bom/{j}' for j in matching_boms],
        })
    rules = [{'pointer': f'/source_rows/compatibility/{i}',
              'rule_type': rule['rule_type'], 'is_active': rule['is_active'],
              'eligible': rule['condition_json'].get('eligible')}
             for i, rule in enumerate(rows['compatibility'])]
    return {'case_id': payload['case_id'], 'lines': line_facts, 'compatibility_rules': rules}


def audit(index, directory):
    expected = {f'EVAL-PREP-{i:03d}' for i in range(1, 37)}
    ids = [row['case_id'] for row in index['cases']]
    if len(ids) != 36 or set(ids) != expected:
        raise ValueError('Expected 36 distinct v2 cases')
    cases = []
    for item in index['cases']:
        cid = item['case_id']
        packet = json.loads((directory / f'{cid}.json').read_bytes())
        provider = (directory / f'{cid}-provider.json').read_bytes()
        if packet['sha256'] != item['packet_sha256'] or digest(packet['payload']) != item['packet_sha256']:
            raise ValueError(f'{cid}: packet hash differs')
        if hashlib.sha256(provider).hexdigest() != item['provider_file_sha256']:
            raise ValueError(f'{cid}: provider hash differs')
        if packet['payload']['case_id'] != cid:
            raise ValueError(f'{cid}: case identity differs')
        if digest(packet['payload']['business_contract']) != index['business_contract_sha256']:
            raise ValueError(f'{cid}: business contract differs')
        cases.append(case_facts(packet['payload']))
    lines = [line for case in cases for line in case['lines']]
    rules = [rule for case in cases for rule in case['compatibility_rules'] if rule['is_active']]
    def ids_for(predicate):
        return [case['case_id'] for case in cases if predicate(case)]
    return {
        'schema_version': 1, 'status': 'source_coverage_not_expected_answers',
        'input_index_sha256': digest(index), 'verified_packet_provider_hashes': 72,
        'case_count': len(cases), 'line_count': len(lines),
        'single_line_cases': ids_for(lambda case: len(case['lines']) == 1),
        'inactive_or_unsellable_cases': ids_for(lambda case: any(not line['active_sellable'] for line in case['lines'])),
        'nonempty_configuration_cases': ids_for(lambda case: any(line['configuration_nonempty'] for line in case['lines'])),
        'undeclared_selected_option_cases': ids_for(lambda case: any(not line['selected_options_declared'] for line in case['lines'])),
        'make_to_order_without_matching_bom_cases': ids_for(lambda case: any(
            line['fulfillment_mode'] == 'make_to_order' and not line['active_matching_bom_pointers']
            for line in case['lines'])),
        'active_compatibility_rule_types': sorted({rule['rule_type'] for rule in rules}),
        'explicit_ineligible_region_cases': ids_for(lambda case: any(
            rule['rule_type'] == 'installation_eligibility' and rule['eligible'] is False
            for rule in case['compatibility_rules'] if rule['is_active'])),
        'cases': cases,
        'qualification': ('Source presence and declared matching only. BOM component fit, product capability, '
                          'regional attribution and six-responsibility correctness require separate judgment. '
                          'Zero observed invalid examples does not prove that the Configuration specialist works.'),
        'independently_reviewed_answers': 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True, type=Path)
    parser.add_argument('--packet-directory', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.index.read_text()), args.packet_directory), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
