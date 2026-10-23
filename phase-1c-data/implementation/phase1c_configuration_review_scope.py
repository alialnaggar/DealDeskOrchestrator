"""Fail-closed review scope for the supplemental Configuration inputs.

Only 039 is a candidate for six-responsibility review. The two rejected input
shapes are preflight diagnostics, not specialist answer cases. No findings or
accepted answers are produced here.
"""

import argparse
import hashlib
import json
from pathlib import Path

from phase1c_evaluation_review import build_review_workspace, digest, render, validate_review_workspace

ROOT = Path(__file__).resolve().parent.parent / 'evaluation/configuration-extension/v1'
SOURCE_SHA = '2e3a4dc2bf25e1df4b1d79f93b73ba98b79adfb5b71de983c1c659192eaf9d7e'
BASE_SHA = '1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc'
CONTRACT_SHA = '6e6990f014e061acd61039bdc128af753fc0116d4c1e7d60dafcdfb2108f7971'
PINS = {
    'EVAL-PREP-037': '3508dd584b0b41eeca18f18f806587bb7f00bc7cc05e428574533eceb4187d70',
    'EVAL-PREP-038': '8a27506a538f7c99340c8fef54ebace37fbfc38c69b135f585cc4de76bb37231',
    'EVAL-PREP-039': '83f65e17b9bfddee6bd32f76742678f3bf60c8e4ffea94d2d3d6479f717b2b99',
}
EMPTY_PROVIDER_SHA = '6f217c34d69b2ef93c2124ae6e08a565626e33da0d258b782934b99fb56efcf8'
DIAGNOSTICS = ('EVAL-PREP-037', 'EVAL-PREP-038')
ELIGIBLE = 'EVAL-PREP-039'


def audit(index, packet_directory):
    """Verify all three source pins before constructing a one-case blank form."""
    if (not isinstance(index, dict) or index.get('schema_version') != 1
            or index.get('extension_id') != 'configuration-v1'
            or index.get('source_definition_sha256') != SOURCE_SHA
            or index.get('base_source_definition_sha256') != BASE_SHA
            or index.get('business_contract_sha256') != CONTRACT_SHA
            or index.get('input_case_count') != 3
            or index.get('independently_reviewed_answers') != 0
            or len(index.get('cases', [])) != 3):
        raise ValueError('Supplemental source index differs from pinned extension')
    rows = index['cases']
    if (not all(isinstance(row, dict) and set(row) ==
                {'case_id', 'packet_sha256', 'provider_file_sha256'} for row in rows)
            or [row['case_id'] for row in rows] != [*DIAGNOSTICS, ELIGIBLE]
            or any(row['packet_sha256'] != PINS[row['case_id']]
                   or row['provider_file_sha256'] != EMPTY_PROVIDER_SHA for row in rows)):
        raise ValueError('Supplemental case identities, order or source pins differ')
    folder = Path(packet_directory)
    for row in rows:
        cid = row['case_id']
        packet = json.loads((folder / f'{cid}.json').read_bytes())
        provider_bytes = (folder / f'{cid}-provider.json').read_bytes()
        if (packet.get('sha256') != row['packet_sha256']
                or digest(packet['payload']) != row['packet_sha256']
                or hashlib.sha256(provider_bytes).hexdigest() != row['provider_file_sha256']):
            raise ValueError(f'{cid}: exported source packet or provider differs')
    candidate_index = {
        'schema_version': 1, 'review_scope': 'configuration-v1-six-responsibility-candidate',
        'parent_input_index_sha256': digest(index),
        'cases': [rows[2]],
    }
    template = build_review_workspace(candidate_index)
    validation = validate_review_workspace(template, candidate_index)
    if validation != {'errors': [], 'pending_cases': 1, 'complete_draft_cases': 0,
                       'independently_reviewed_answers': 0}:
        raise ValueError('Blank one-case reviewer boundary differs')
    report = {
        'parent_input_index_sha256': digest(index),
        'diagnostic_preflight_only': list(DIAGNOSTICS),
        'six_responsibility_review_candidate': [ELIGIBLE],
        'verified_packet_provider_pairs': 3,
        'candidate_index_sha256': digest(candidate_index),
        'pending_candidate_reviews': 1,
        'accepted_answers': 0,
        'ready_for_generation': False,
    }
    return report, candidate_index, template


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=ROOT / 'packet_index.json')
    parser.add_argument('--packet-directory', type=Path, required=True)
    parser.add_argument('--candidate-index-output', type=Path)
    parser.add_argument('--blank-review-output', type=Path)
    args = parser.parse_args()
    report, candidate, template = audit(json.loads(args.index.read_text()), args.packet_directory)
    if args.candidate_index_output:
        args.candidate_index_output.write_text(render(candidate))
    if args.blank_review_output:
        args.blank_review_output.write_text(render(template))
    print(render(report), end='')


if __name__ == '__main__':
    main()
