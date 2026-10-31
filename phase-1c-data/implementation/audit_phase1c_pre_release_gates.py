"""Read-only Phase 1C release-gate inventory from versioned repository facts.

This inventory reports documented bounded dispositions separately from the
remaining answer, runtime and final-audit gates. It cannot release data or
certify the substantive correctness of a reviewer judgment.
"""

import argparse
import json
from pathlib import Path

import yaml

from phase1c_evaluation_acceptance import check_v2_index
from phase1c_evaluation_review import digest, render
from phase1c_configuration_review_scope import (BASE_SHA, CONTRACT_SHA, DIAGNOSTICS,
                                                 ELIGIBLE, EMPTY_PROVIDER_SHA, PINS,
                                                 SOURCE_SHA)

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
FIELDS = (
    ('products', 'attributes_json'),
    ('products', 'list_price'),
    ('products', 'standard_cost'),
    ('suppliers', 'order_calendar_json'),
    ('compatibility_rules', 'condition_json'),
    ('agent_execution_log', 'output_json'),
)
CALIBRATION_MARKERS = (
    '**Mix evidence review: resolved for the synthetic V1 catalogue**',
    '**Fixed-p50 calibration evidence review: resolved for internal synthetic arithmetic only**',
)
SUPPLEMENTAL_SCOPE_MARKER = 'bounded supplemental 039 V2 dependency field disposition on 30 October 2026'


def audit(rules, calibration_text, development, v2, extension):
    """Reject source drift; report substantive gates as pending, never inferred passed."""
    check_v2_index(v2)
    if (not isinstance(development, dict) or not isinstance(development.get('payload'), dict)
            or digest(development['payload']) != development.get('sha256')):
        raise ValueError('Development exclusion registry hash differs')
    dev = development['payload']
    ids = dev.get('deal_ids')
    expected = {f'GEN-TEST-{n:03d}' for n in range(1, 101)}
    if (dev.get('status') != 'development_reader_selected_sources_not_evaluation_answers'
            or dev.get('deal_count') != 152 or not isinstance(ids, list)
            or len(ids) != 152 or len(set(ids)) != 152
            or {cid for cid in ids if cid.startswith('GEN-TEST-')} != expected):
        raise ValueError('100-case diagnostic registry differs')
    if (not isinstance(extension, dict) or extension.get('schema_version') != 1
            or extension.get('extension_id') != 'configuration-v1'
            or extension.get('source_definition_sha256') != SOURCE_SHA
            or extension.get('base_source_definition_sha256') != BASE_SHA
            or extension.get('business_contract_sha256') != CONTRACT_SHA
            or extension.get('input_case_count') != 3
            or extension.get('independently_reviewed_answers') != 0):
        raise ValueError('Configuration extension version or answer boundary differs')
    rows = extension.get('cases')
    if (not isinstance(rows, list) or len(rows) != 3
            or [row.get('case_id') for row in rows] != [*DIAGNOSTICS, ELIGIBLE]
            or any(set(row) != {'case_id', 'packet_sha256', 'provider_file_sha256'}
                   or row['packet_sha256'] != PINS[row['case_id']]
                   or row['provider_file_sha256'] != EMPTY_PROVIDER_SHA for row in rows)):
        raise ValueError('Configuration extension case pins differ')
    documented, pending = [], []
    for table, column in FIELDS:
        field = rules['tables'][table][column]
        name = f'{table}.{column}'
        if field.get('resolved_by') and field.get('review_before_generation'):
            raise ValueError(f'{name}: contradictory field disposition')
        if field.get('resolved_by'):
            documented.append(name)
        elif field.get('review_before_generation'):
            pending.append(name)
        else:
            raise ValueError(f'{name}: missing explicit field review status')
    if documented != [f'{t}.{c}' for t, c in FIELDS[:5]] or pending != ['agent_execution_log.output_json']:
        raise ValueError('Bounded field review scope differs; inspect before updating gate')
    if SUPPLEMENTAL_SCOPE_MARKER not in rules['tables']['compatibility_rules']['condition_json']['resolved_by']:
        raise ValueError('Supplemental 039 technical field disposition is missing')
    if not all(marker in calibration_text for marker in CALIBRATION_MARKERS):
        raise ValueError('Calibration evidence disposition text differs')
    return {
        'schema_version': 1,
        'status': 'pre_release_inventory_not_a_release_decision',
        'development_diagnostics': {'registered_cases': 100, 'accepted_answers': 0,
                                    'exclusion_registry_sha256': development['sha256']},
        'field_reviews': {'bounded_dispositions': documented, 'pending': pending,
                          'supplemental_v2_dependency_scope':
                          'bounded_field_disposition_039_answer_review_pending'},
        'calibration_evidence_reviews': {'documented_bounded_dispositions': 2,
                                         'external_market_validity_claimed': False},
        'evaluation': {'original_input_count': 36,
                       'source_index_independently_reviewed_answers': 0,
                       'accepted_answer_intake': 'not_supplied_to_this_audit',
                       'input_index_sha256': digest(v2),
                       'case_020_six_findings': 'pending',
                       'supplemental_review_candidate': [ELIGIBLE],
                       'supplemental_accepted_answers': 0,
                       'preflight_diagnostics': list(DIAGNOSTICS)},
        'final_clean_rebuild_and_release_audit': 'pending',
        'ready_for_generation': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-current', action='store_true')
    args = parser.parse_args()
    report = audit(
        yaml.safe_load((HERE / 'phase1c_column_rules.yaml').read_text()),
        (PHASE / 'calibration-decision-sheet.md').read_text(),
        json.loads((HERE / 'phase1c_development_source_exclusions.json').read_text()),
        json.loads((PHASE / 'evaluation/provisional_packet_index.json').read_text()),
        json.loads((PHASE / 'evaluation/configuration-extension/v1/packet_index.json').read_text()),
    )
    if args.check_current and (report['ready_for_generation'] is not False
                               or report['evaluation']['source_index_independently_reviewed_answers'] != 0
                               or report['field_reviews']['pending'] != ['agent_execution_log.output_json']):
        raise ValueError('Current provisional gate differs')
    print(render(report), end='')


if __name__ == '__main__':
    main()
