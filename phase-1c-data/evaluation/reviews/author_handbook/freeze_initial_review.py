#!/usr/bin/env python3
"""Freeze a completed source-first author batch before exposing AI proposals.

Structural validation only. This does not accept a label or certify its truth.
Usage: python3 freeze_initial_review.py --workbook outputs/Blinded_Initial_Decision_Register.xlsx --cases 001 002 --output outputs/initial_001_002.json
"""
import argparse, datetime, hashlib, json, pathlib
from openpyxl import load_workbook

ap=argparse.ArgumentParser();ap.add_argument('--workbook',required=True);ap.add_argument('--cases',nargs='+',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
ids=[x if x.startswith('EVAL-PREP-') else 'EVAL-PREP-'+x.zfill(3) for x in args.cases]
if len(set(ids))!=len(ids) or any(x not in [f'EVAL-PREP-{i:03d}' for i in range(1,37)] for x in ids):raise SystemExit('Choose distinct original IDs 001–036 only')
wb=load_workbook(args.workbook,read_only=True,data_only=True)
cs=wb['Initial Case Decisions'];fs=wb['Initial Six Findings']
ch=[c.value for c in next(cs.rows)];fh=[c.value for c in next(fs.rows)]
def table(sheet,headers):return [dict(zip(headers,[c.value for c in row])) for row in list(sheet.rows)[1:]]
cases={r['Case ID']:r for r in table(cs,ch)};findings=table(fs,fh)
seed=json.loads((pathlib.Path(__file__).parent/'outputs/blind_register_seed.json').read_text());pins={c['case_id']:c for c in seed['cases']}
out=[]
for cid in ids:
    r=cases[cid];p=pins[cid]
    for k,v in [('Packet SHA-256',p['packet_sha']),('Provider SHA-256',p['provider_sha']),('Credit scope SHA-256',p['scope_sha'])]:
        if r[k]!=v:raise SystemExit(f'{cid}: source pin changed: {k}')
    required=['Configuration finding','Pricing finding','Availability finding','Credit finding','Policy finding','Approval finding','Overall gate','Original-deal actions','Evidence pointer(s)','Rule IDs and calculations','Uncertainty / abstention','Rationale','Author identity','Initial decision timestamp ISO','AI-assistance disclosure','Initial status (draft/unresolved)']
    for k in required:
        if r[k] is None or str(r[k]).strip()=='':raise SystemExit(f'{cid}: missing {k}')
    if r['Overall gate'] not in ['blocked','needs_revision','needs_evidence','needs_commitment','approval_required','unresolved']:raise SystemExit(f'{cid}: invalid gate')
    if r['Initial status (draft/unresolved)'] not in ['Draft','Unresolved']:raise SystemExit(f'{cid}: no acceptance in first pass')
    try:
        d=datetime.datetime.fromisoformat(str(r['Initial decision timestamp ISO']).replace('Z','+00:00'))
        if d.tzinfo is None:raise ValueError()
    except ValueError:raise SystemExit(f'{cid}: timestamp requires timezone')
    rr=[x for x in findings if x['Case ID']==cid]
    if len(rr)!=6 or {x['Responsibility'] for x in rr}!={'Configuration','Pricing','Availability','Credit','Policy','Approval'}:raise SystemExit(f'{cid}: six detailed rows required')
    for x in rr:
        for k in ['Initial finding code','Initial finding narrative','Source pointer(s)','Rule / calculation','Action or blocker','Uncertainty or abstention','Author identity','Decision timestamp ISO','AI-assistance disclosure']:
            if x[k] is None or str(x[k]).strip()=='':raise SystemExit(f'{cid}/{x["Responsibility"]}: missing {k}')
        if x['Initial finding code'] not in ['no_issue_identified','needs_evidence','needs_commitment','needs_revision','blocked','human_review_required','requires_adjudication','abstain','other']:raise SystemExit(f'{cid}/{x["Responsibility"]}: invalid code')
    out.append({'case':r,'six_findings':rr})
snapshot={'source_commit':seed['commit'],'stage':'author_initial_blinded_source_first','accepted_answers':0,'cases':out,'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'source facts and deterministic calculations before AI recommendation comparison; author decisions only'}
blob=json.dumps(snapshot,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();hashval=hashlib.sha256(blob).hexdigest();path=pathlib.Path(args.output)
with path.open('xb') as f:f.write(blob)
path.with_suffix(path.suffix+'.sha256').write_text(hashval+'  '+path.name+'\n')
print(f'Frozen {len(out)} first-pass cases; SHA-256 {hashval}. No answers accepted by this tool.')
