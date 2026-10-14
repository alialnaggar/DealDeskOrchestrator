"""Report source facts for contract adjudication; never derive evaluation labels."""
import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def stamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Source timestamp requires a timezone')
    return parsed


def age_observation(value, as_of, comparison_hours):
    delta = stamp(as_of) - stamp(value)
    seconds = Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / Decimal(1000000)
    age = seconds / Decimal(3600)
    return {'snapshot_at': value, 'age_hours': str(age),
            'future_dated': age < 0,
            'within_comparison_window': 0 <= age <= comparison_hours}


def audit_case(payload, comparison_hours):
    rows = payload['source_rows']
    as_of = payload['run_context']['as_of_at']
    observations = []
    for collection in ('inventory', 'production_capacity', 'digital_capacity'):
        for i, row in enumerate(rows[collection]):
            observations.append({'pointer': f'/source_rows/{collection}/{i}/snapshot_at',
                                 'collection': collection,
                                 **age_observation(row['snapshot_at'], as_of, comparison_hours)})
    credit = rows['credit']
    observations.append({'pointer': '/source_rows/credit/commitments_as_of_at',
                         'collection': 'credit',
                         **age_observation(credit['commitments_as_of_at'], as_of, comparison_hours)})
    offers = []
    for i, offer in enumerate(rows['supplier_offers']):
        matches = []
        for collection, id_key in (('lines', 'product_id'), ('bom_lines', 'component_product_id')):
            for j, row in enumerate(rows[collection]):
                if row[id_key] == offer['product_id']:
                    standard = Decimal(row['standard_cost'])
                    offered = Decimal(offer['unit_cost'])
                    matches.append({'pointer': f'/source_rows/{collection}/{j}/standard_cost',
                                    'standard_cost': str(standard),
                                    'offer_minus_standard_cost': str(offered - standard)})
        offers.append({'pointer': f'/source_rows/supplier_offers/{i}',
                       'product_id': offer['product_id'], 'unit_cost': offer['unit_cost'],
                       'currency_code': offer['currency_code'], 'matching_standard_costs': matches,
                       'qualification': 'Same product identity; loaded-cost, unit and tax comparability is not established.'})
    service_rules = [{'pointer': f'/source_rows/compatibility/{i}',
                      'source_product_id': row['source_product_id'],
                      'rule_type': row['rule_type'], 'condition_json': row['condition_json']}
                     for i, row in enumerate(rows['compatibility'])
                     if row['rule_type'] == 'installation_eligibility']
    lines = [{'pointer': f'/source_rows/lines/{i}', 'product_id': row['product_id'],
              'fulfillment_mode': row['fulfillment_mode'],
              'installation_requested': row['installation_requested']}
             for i, row in enumerate(rows['lines'])]
    return {'case_id': payload['case_id'], 'as_of_at': as_of,
            'observations': observations, 'offers': offers,
            'cost_parameters_present': rows['cost_parameters'] is not None,
            'lines': lines, 'service_rules': service_rules}


def audit_inputs(index, directory, comparison_hours=Decimal(24)):
    if not comparison_hours.is_finite() or comparison_hours <= 0:
        raise ValueError('Comparison window must be positive and finite')
    ids = [row['case_id'] for row in index['cases']]
    if len(ids) != 36 or len(set(ids)) != 36 or set(ids) != {f'EVAL-PREP-{i:03}' for i in range(1, 37)}:
        raise ValueError('Expected exactly the 36 pinned cases')
    cases = []
    for row in index['cases']:
        cid = row['case_id']
        packet = json.loads((directory / f'{cid}.json').read_text())
        provider = (directory / f'{cid}-provider.json').read_bytes()
        if digest(packet['payload']) != row['packet_sha256'] or packet['sha256'] != row['packet_sha256']:
            raise ValueError(f'{cid}: packet hash differs')
        if hashlib.sha256(provider).hexdigest() != row['provider_file_sha256']:
            raise ValueError(f'{cid}: provider hash differs')
        if packet['payload']['case_id'] != cid:
            raise ValueError(f'{cid}: payload identity differs')
        cases.append(audit_case(packet['payload'], comparison_hours))
    outside = sorted({case['case_id'] for case in cases
                      if any(not item['within_comparison_window'] for item in case['observations'])})
    divergent = sorted({case['case_id'] for case in cases for offer in case['offers']
                        if any(Decimal(match['offer_minus_standard_cost']) != 0
                               for match in offer['matching_standard_costs'])})
    return {'schema_version': 1, 'status': 'contract_adjudication_facts_not_answers',
            'input_index_sha256': digest(index), 'verified_source_and_provider_hashes': 72,
            'comparison_window_hours': str(comparison_hours),
            'comparison_basis': ('Approved synthetic contract comparison; source age is not a commitment or answer.'
                                 if 'business_contract_sha256' in index else
                                 'Current reader _fresh default; observed implementation, not an approved evaluation contract.'),
            'independently_reviewed_answers': 0,
            'cases_outside_comparison_window': outside,
            'cases_with_different_offer_and_standard_cost': divergent, 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet-directory', type=Path, required=True)
    parser.add_argument('--index', type=Path, required=True)
    parser.add_argument('--comparison-hours', type=Decimal, default=Decimal(24))
    args = parser.parse_args()
    report = audit_inputs(json.loads(args.index.read_text()), args.packet_directory, args.comparison_hours)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
