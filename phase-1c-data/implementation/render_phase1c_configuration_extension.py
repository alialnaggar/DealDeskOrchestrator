"""Versioned supplemental Configuration inputs; no expected findings or scores.

These two cases deliberately derive from v2 build cases 013/014. They are a
separate technical-coverage extension, not independent samples or a rewrite
of the pinned 36-case evaluation set.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from render_phase1c_evaluation_cases import build_from_files, canonical, render


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parent / 'evaluation' / 'configuration-extension' / 'v1'
BASE_SHA = '1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc'


def remap(value, old, new):
    if isinstance(value, dict):
        return {key: remap(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [remap(item, old, new) for item in value]
    return value.replace(old, new) if isinstance(value, str) else value


def build():
    base, base_manifest = build_from_files()
    if base_manifest['inputs_sha256'] != BASE_SHA or hashlib.sha256(render(base).encode()).hexdigest() != BASE_SHA:
        raise ValueError('Pinned v2 source definitions changed; review extension lineage')
    source_digest = hashlib.sha256(canonical({
        'base_sha256': BASE_SHA,
        'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contract_sha256': hashlib.sha256(canonical(base['business_contract']).encode()).hexdigest(),
    }).encode()).hexdigest()
    cases, intent = [], []
    for number, base_number, selected_options, purpose in (
        (1, 13, ['unsupported'], 'option_not_offered'),
        (2, 14, ['standard', 'alternate'], 'offered_combination_without_selected_bom'),
    ):
        source = next(case for case in base['cases'] if case['case_id'] == f'EVAL-PREP-{base_number:03d}')
        case = remap(deepcopy(source), f'EVAL36-{base_number:03d}', f'EVALCFG-{number:03d}')
        case['case_id'] = f'EVAL-CONFIG-{number:03d}'
        tables = case['tables']
        line = tables['deal_lines'][0]
        line['configuration_json'] = {'selected_options': selected_options}
        tables['deals'][0]['deal_name'] = f'Synthetic configuration extension {number:03d}'
        run = tables['deal_runs'][0]
        run['run_id'] = f'00000000-0000-4000-8000-{370000 + number:012d}'
        run['config_hash'] = source_digest
        cases.append(case)
        intent.append({'case_id': case['case_id'], 'derived_from': source['case_id'],
                       'source_condition': purpose, 'source_review': 'pending',
                       'independent_answer_review': 'pending'})
    inputs = {'schema_version': 1, 'extension_id': 'configuration-v1',
              'base_evaluation_input_version': 2, 'base_source_definition_sha256': BASE_SHA,
              'business_contract': base['business_contract'], 'cases': cases}
    manifest = {'schema_version': 1, 'status': 'supplemental_source_inputs_not_answers',
                'extension_id': 'configuration-v1', 'base_source_definition_sha256': BASE_SHA,
                'inputs_sha256': hashlib.sha256(render(inputs).encode()).hexdigest(),
                'generator_fingerprint_sha256': source_digest, 'authored_input_cases': len(cases),
                'independently_reviewed_answers': 0, 'cases': intent,
                'limitations': ['Derived from existing v2 build cases; no statistical independence claim',
                                'Only two selected-option failures; not full Configuration breadth']}
    return inputs, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    inputs, manifest = build()
    for name, value in (('source_cases.json', inputs), ('authoring_manifest.json', manifest)):
        path = OUTPUT / name
        if args.check:
            if path.read_text() != render(value):
                raise SystemExit(f'{path} differs from reproducible sources')
        else:
            OUTPUT.mkdir(parents=True, exist_ok=True)
            path.write_text(render(value))
    print('Two supplemental Configuration inputs; 0 independently reviewed answers')


if __name__ == '__main__':
    main()
