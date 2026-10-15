"""Report source facts for contract adjudication; never derive evaluation labels."""
import argparse
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo


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


def quote_credit_arithmetic(rows):
    """Full submitted commercial quantity, never concurrent digital demand."""
    lines, revenue, profit, listed = [], Decimal(0), Decimal(0), Decimal(0)
    for i, row in enumerate(rows['lines']):
        qty, price, cost, list_price = map(Decimal, (row['quantity'], row['quoted_unit_price'], row['standard_cost'], row['list_price']))
        if min(qty, price, list_price) <= 0:
            raise ValueError('Positive quantity, quoted price and list price required')
        amount = qty * price
        margin = (price - cost) * 100 / price
        floors = [(j, r) for j, r in enumerate(rows['rules']['pricing_rules'])
                  if r['rule_type'] == 'category_margin_floor' and r['scope_value'] == row['category']]
        if len(floors) != 1:
            raise ValueError('One declared category floor required')
        j, floor = floors[0]
        lines.append({'pointer': f'/source_rows/lines/{i}', 'quantity': str(qty),
                      'revenue_eur': str(amount), 'standard_cost_total_eur': str(qty * cost),
                      'discount_pct': str((list_price - price) * 100 / list_price),
                      'margin_pct': str(margin), 'category_floor_pct': str(floor['condition_json']['margin_pct_lt']),
                      'floor_shortfall_points': str(Decimal(floor['condition_json']['margin_pct_lt']) - margin),
                      'floor_pointer': f'/source_rows/rules/pricing_rules/{j}'})
        revenue += amount; profit += qty * (price - cost); listed += qty * list_price
    commitments = Decimal(rows['credit']['unbilled_committed_amount'])
    ar = sum((Decimal(row['outstanding_amount']) for row in rows['receivables']), Decimal(0))
    limit = Decimal(rows['credit']['credit_limit'])
    if limit <= 0 or revenue <= 0:
        raise ValueError('Positive limit and revenue required')
    exposure = revenue + commitments + ar
    return {'lines': lines, 'deal_revenue_eur': str(revenue), 'deal_margin_pct': str(profit * 100 / revenue),
            'deal_discount_pct': str((listed - revenue) * 100 / listed),
            'unbilled_commitments_eur': str(commitments), 'receivables_eur': str(ar),
            'exposure_eur': str(exposure), 'credit_limit_eur': str(limit),
            'credit_excess_pct': str(max(Decimal(0), (exposure / limit - 1) * 100)),
            'qualification': 'Arithmetic over supplied snapshot; no approval, label or freshness acceptance.'}


def advance_workdays(day, count, weekdays, holidays=()):
    if not weekdays or any(type(d) is not int or not 1 <= d <= 7 for d in weekdays) or type(count) is not int or count < 0:
        raise ValueError('Invalid working-day calendar or lead')
    holidays = set(holidays)
    while count:
        day += timedelta(days=1)
        if day.isoweekday() in weekdays and day.isoformat() not in holidays:
            count -= 1
    return day


def offer_operation_projections(payload, comparison_hours):
    """Bounded one-line, unit-output, separate-day schedule illustrations.

    Other material/configuration and actual cutoff/commitments require review.
    This never selects an overall gate, calls the reader or fabricates a booking.
    """
    rows, as_of = payload['source_rows'], payload['run_context']['as_of_at']
    projections = []
    if len(rows['lines']) != 1:
        return [{'qualification': 'Multi-line projection unsupported; review manually.'}]
    line = rows['lines'][0]
    boms = [b for b in rows['bom'] if b['finished_product_id'] == line['product_id']
            and b['configuration_signature_json'] == line['configuration_json'] and b['status'] == 'active']
    for i, offer in enumerate(rows['supplier_offers']):
        if line['fulfillment_mode'] == 'make_to_order':
            if len(boms) != 1 or Decimal(boms[0]['output_quantity']) != 1:
                projections.append({'offer_pointer': f'/source_rows/supplier_offers/{i}',
                                    'qualification': 'Unique unit-output BOM required; review manually.'})
                continue
            bom = boms[0]
            if not any(b['bom_id'] == bom['bom_id'] and b['component_product_id'] == offer['product_id'] for b in rows['bom_lines']):
                continue
            requirements = sorted((r for r in rows['requirements'] if r['bom_id'] == bom['bom_id'] and r['status'] == 'active'), key=lambda r:r['operation_seq'])
        elif offer['product_id'] == line['product_id'] and line['fulfillment_mode'] == 'supplier_finished':
            requirements = []
        else:
            continue
        cal = offer['order_calendar_json']
        order_day = stamp(as_of).astimezone(ZoneInfo(cal['time_zone'])).date()
        if not offer['is_active'] or not (date.fromisoformat(offer['valid_from']) <= order_day <= date.fromisoformat(offer['valid_to'])):
            projections.append({'offer_pointer': f'/source_rows/supplier_offers/{i}',
                                'hypothetical_order_date': order_day.isoformat(),
                                'qualification': 'Inactive or out-of-validity offer cannot support a conditional schedule.'})
            continue
        lanes = [(j, lane) for j, lane in enumerate(rows['shipping_lanes']) if lane['is_active']
                 and lane['destination_country_code'] == rows['deal']['destination_country_code']
                 and lane['destination_region'] == rows['deal']['destination_region']
                 and lane['shipping_service_code'] == rows['deal']['shipping_service_code']]
        for label in ('min', 'mode', 'max'):
            receipt = advance_workdays(order_day, offer[f'lead_days_{label}'], cal['working_weekdays'], cal['holiday_dates'])
            for j, lane in lanes:
                operations, ready, missing = [], receipt, None
                for req in requirements:
                    qty = Decimal(line['quantity'])
                    batches = (qty / Decimal(req['batch_size'])).to_integral_value(rounding=ROUND_CEILING)
                    hours = qty * Decimal(req['hours_per_unit']) + batches * Decimal(req['setup_hours'])
                    candidates = [(k, c) for k, c in enumerate(rows['production_capacity'])
                                  if c['location_id'] == lane['origin_location_id'] and c['capability_code'] == req['capability_code']
                                  and c['resource_type'] == req['resource_type'] and c['status'] == 'active'
                                  and date.fromisoformat(c['capacity_date']) >= ready
                                  and (not operations or c['capacity_date'] > operations[-1]['date'])
                                  and age_observation(c['snapshot_at'], as_of, comparison_hours)['within_comparison_window']
                                  and Decimal(c['available_capacity_hours']) - Decimal(c['allocated_capacity_hours']) >= hours]
                    if not candidates:
                        missing = req['capability_code']
                        break
                    k, capacity = min(candidates, key=lambda pair:(pair[1]['capacity_date'], pair[1]['capacity_id']))
                    ready = date.fromisoformat(capacity['capacity_date'])
                    operations.append({'capability': req['capability_code'], 'date': ready.isoformat(),
                                       'hours_required': str(hours), 'capacity_pointer': f'/source_rows/production_capacity/{k}'})
                arrival = None
                if missing is None:
                    if not lane['dispatch_weekdays_json']:
                        raise ValueError('Dispatch calendar required')
                    while ready.isoweekday() not in lane['dispatch_weekdays_json']:
                        ready += timedelta(days=1)
                    arrival = advance_workdays(ready, lane['transit_workdays'], [1, 2, 3, 4, 5]).isoformat()
                projections.append({'offer_pointer': f'/source_rows/supplier_offers/{i}',
                                    'lane_pointer': f'/source_rows/shipping_lanes/{j}', 'lead_assumption': label,
                                    'hypothetical_order_date': order_day.isoformat(), 'component_or_product_receipt': receipt.isoformat(),
                                    'operations': operations, 'missing_operation_observation': missing,
                                    'indicative_arrival': arrival,
                                    'requested_date': rows['deal']['requested_delivery_date'],
                                    'qualification': 'Uncommitted projection; separate-day operations, weekday transit, same-day dispatch requires cutoff confirmation. Remaining materials/configuration and actual commitments are not certified.'})
    return projections


def audit_case(payload, comparison_hours):
    contract = payload.get('business_contract')
    if contract is not None and Decimal(contract['evidence_age']['snapshot_max_elapsed_hours']) != comparison_hours:
        raise ValueError('Comparison window differs from the declared business contract')
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
            'lines': lines, 'service_rules': service_rules,
            'quote_credit_arithmetic': quote_credit_arithmetic(rows),
            'conditional_offer_projections': offer_operation_projections(payload, comparison_hours)}


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
        if 'business_contract_sha256' in index and digest(packet['payload'].get('business_contract')) != index['business_contract_sha256']:
            raise ValueError(f'{cid}: declared business contract hash differs')
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
