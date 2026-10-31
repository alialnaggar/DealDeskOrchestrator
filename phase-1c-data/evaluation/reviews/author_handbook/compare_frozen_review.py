#!/usr/bin/env python3
"""Compare frozen author first pass to preserved technical proposals.

This is an exception triage aid, not a semantic verifier or acceptance tool.
"""
import argparse, hashlib, json, pathlib
ap=argparse.ArgumentParser();ap.add_argument('--snapshot',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
root=pathlib.Path(__file__).parent;path=pathlib.Path(args.snapshot);raw=path.read_bytes();got=hashlib.sha256(raw).hexdigest();sidecar=path.with_suffix(path.suffix+'.sha256')
if not sidecar.exists() or sidecar.read_text().split()[0]!=got:raise SystemExit('Frozen snapshot hash mismatch or missing sidecar')
snap=json.loads(raw);matrix=json.loads((root/'repo/phase-1c-data/evaluation/reviews/v3_six_responsibility_technical_matrix.json').read_text());reference={c['case_id']:c for c in matrix['cases']}
if snap['stage']!='author_initial_blinded_source_first' or snap['accepted_answers']!=0:raise SystemExit('Unexpected snapshot stage')
queue=[]
for item in snap['cases']:
    c=item['case'];cid=c['Case ID'];r=reference[cid]
    if c['Packet SHA-256']!=r['v2_packet_sha256'] or c['Provider SHA-256']!=r['v2_provider_file_sha256'] or c['Credit scope SHA-256']!=r['v3_scope_sha256']:raise SystemExit(cid+' source pin mismatch')
    findings=[]
    for f in item['six_findings']:
        resp=f['Responsibility'];proposal=r['six_responsibilities'][resp]['technical_recommendation'];initial=f['Initial finding code']
        kinds=[]
        if initial!=proposal:kinds.append('code_disagreement')
        if initial in ('abstain','other','requires_adjudication') or 'unknown' in str(f['Uncertainty or abstention']).lower():kinds.append('uncertainty_or_abstention')
        # Literal pointer presence is syntactic only; it cannot establish claim support.
        if not any(t in str(f['Source pointer(s)']) for t in ('packet:/','provider:/','scope:/')):kinds.append('missing_structured_evidence_pointer')
        findings.append({'responsibility':resp,'initial_code':initial,'technical_code':proposal,'flags':kinds,'manual_source_claim_check_required':True})
    gate=c['Overall gate'];gate_disagree=gate!=r['overall_technical_gate_proposal'];risk=cid[-3:] in ('020','029','030','031','032','033','034')
    flags=[x for x in ['high_risk_business_case' if risk else '', 'overall_gate_disagreement' if gate_disagree else ''] if x]
    if any(f['flags'] for f in findings):flags.append('specialist_exception')
    queue.append({'case_id':cid,'priority':0 if risk or gate_disagree else 1 if flags else 2,'flags':flags,'initial_gate':gate,'technical_gate':r['overall_technical_gate_proposal'],'findings':findings,'first_pass_rationale':c['Rationale'],'accepted':False})
queue.sort(key=lambda x:(x['priority'],x['case_id']))
out={'snapshot_sha256':got,'technical_matrix_sha256':hashlib.sha256((root/'repo/phase-1c-data/evaluation/reviews/v3_six_responsibility_technical_matrix.json').read_bytes()).hexdigest(),'accepted_answers':0,'classification_scope':'literal codes, pointer presence and declared uncertainty only; narrative source support needs author review','cases':queue}
target=pathlib.Path(args.output)
with target.open('x') as f:json.dump(out,f,indent=2)
print('Compared',len(queue),'cases; flagged',sum(bool(x['flags']) for x in queue),'for review. No label accepted.')
