#!/usr/bin/env python3
"""Build a source-first author packet without labels, archetypes or AI recommendations.

Imports the pinned hash validator from generate_handbook.py. This script exposes
only source rows, approved rules, arithmetic and neutral decision prompts.
"""
import json, pathlib
from decimal import Decimal
import generate_handbook as g

O=g.OUT
sections=[]
def add(s=''):sections.append(s+'\n')
add('---\ntitle: "Deal Desk Orchestrator | Blinded Source-First Author Review"\nsubtitle: "Original cases 001–036; initial decisions only"\nauthor: "Prepared for Ali Alnaggar"\ndate: "31 October 2026"\ngeometry: margin=22mm\nfontsize: 10pt\nheader-includes:\n  - \\usepackage{xurl}\n  - \\usepackage{ragged2e}\n  - \\RaggedRight\n---')
add('# Read this before adjudicating')
add('**This is the initial source-first view. No prior model answers, technical recommendation matrix, scenario archetypes, proposed findings, proposed gates, or accepted labels appear here.** The companion technical handbook must remain closed until initial decisions are frozen. Every case decision is blank. The six responsibilities, exact source facts, business conventions and deterministic computations appear below; they may naturally reveal a rule consequence, but no prior answer proposal is shown. The original 36 cases are distinct from supplemental 039–041.')
add('Source basis: GitHub `alialnaggar/DealDeskOrchestrator`, source commit `'+g.COMMIT+'`, v2 packet/provider hashes and v3 fictional Credit scope. The generator checks 36 packet hashes, 36 provider-byte hashes, 36 v3 scope hashes and source pointer integrity; these checks establish identity, not correctness. PostgreSQL replay is documented separately and was not rerun for this packet.')
add('**Method:** Read each case, apply the actual rules, write six independent findings and an overall gate in the blank register, cite evidence, state uncertainty and actions, then freeze a timestamped hash of the completed first-pass workbook. Only after that open the technical recommendation reference, compare and record a separate final author decision. Do not call this independent external expert validation. The current release checklist still requires a second-model pass; changing that gate remains a pending documented methodological decision.')
add('# Part I — Source-first reference')
add('A salesperson submits a structured deal. Configuration checks version, sellability and exact compatibility rules; Pricing checks full-quantity quote, discount, standard cost and margin floor; Availability checks dated stock, offers, production, provider coverage, service eligibility and transit; Credit checks exposure and source completeness; Policy applies explicit hard blocks or escalations; Approval identifies a possible human route. The orchestrator retains subordinate findings, then applies gate precedence. No specialist approves, reserves or promises delivery.')
add('The gate order in the approved v2 synthetic contract is `blocked` → `needs_revision` → `needs_evidence` → `needs_commitment` → `approval_required`. A blocked submission has a hard prohibition. Revision changes the original quantity, date or region; evidence means current adequate facts are missing; commitment means a specific feasible but unbooked route; approval required means only that a human route can be presented. None is approval granted. Abstain on a claim when evidence is incomplete and state the missing fact. A proposed alternative must be distinguished from the submitted original and may need customer acceptance and a new six-check run.')
add('**Commercial arithmetic:** quote = sum(quantity × quoted unit price); list = sum(quantity × list price); cost = sum(quantity × versioned catalogue standard cost); discount = (list − quote)/list × 100; gross margin = (quote − cost)/quote × 100. Compare each line with its category floor, strict discount escalation thresholds and hard caps. Supplier offer cost is not a substitute for quote-margin standard cost. Fictional EUR values are tax-exclusive.')
add('**Credit arithmetic:** quoted amount + unbilled commitments + unpaid receivables net of applied payments. The original v2 packet selects no AR/payment rows; the versioned v3 case scope explicitly declares a fictional complete-zero population per customer/cutoff after individual source-intent review. Without such a declaration, zero selected rows do not prove completeness. The 040/041 controls separately test nonempty and unknown evidence. A complete synthetic declaration is not external verification or favorable payment history.')
add('**Time and scope:** Inventory, production capacity, digital capacity and credit commitments require observations no older than 24 elapsed hours, inclusive, and not future-dated. Provider verification is within seven elapsed days and must match identity, quantity, binding term and coverage through the contract anniversary. Supplier offers are not committed supply; a regional eligibility rule is not an appointment. For submitted alternatives, retain maximum-lead and missing-slot uncertainty. Follow the calendar, cutoff and valid dates in each row.')
contract=g.packets['EVAL-PREP-001']['business_contract']
for key in ['gates','costing','digital_term','evidence_age','service_scope','routing']:
    add('## '+g.label(key).title())
    for k,v in contract[key].items():add('- `'+k+'`: '+g.esc(g.val(v))+f'. [packet `/business_contract/{key}/{k}`]')
rules=g.packets['EVAL-PREP-001']['source_rows']['rules']
add('## Active synthetic business-rule catalogue')
for typ in ['pricing_rules','policy_rules','approval_rules']:
    add('### '+g.label(typ).title())
    for i,r in enumerate(rules[typ]):
        rid=r.get('pricing_rule_id') or r.get('policy_rule_id') or r.get('approval_rule_id')
        action=r.get('action_json') or {k:r[k] for k in ('severity','required_action','required_role','approval_sequence') if k in r}
        add('- `'+rid+'`: scope `'+g.val({'type':r.get('scope_type'),'value':r.get('scope_value')})+'`; condition `'+g.val(r.get('condition_json'))+'`; action/role `'+g.val(action)+'`. [packet `/source_rows/rules/'+typ+'/'+str(i)+'`]')
add('## Source pointers and decision discipline')
add('Pointers `packet:/...`, `provider:/...`, and `scope:/...` identify the selected payload, separate provider file and versioned Credit declaration. Compare timestamps with the case cutoff. An empty selected list is not inherently complete, a stale observation is not proof of impossibility, and a viable alternate route is not a commitment. Record rule ID, calculation, exact pointer, counterargument, uncertainty, required action and the consequence for the original deal. If the repository lacks a convention, mark unresolved rather than creating one. [Phase 1C evaluation contract and source-bound packet index.]')

add('# Part II — Original case source dossiers')
blind=[]
for case,p in g.packets.items():
    n=case[-3:];s=next(x for x in g.SCOPE['cases'] if x['case_id']==case);src=p['source_rows'];ctx=p['run_context'];entry=g.sources[case];lines=src['lines'];d=src['deal'];c=src['customer'];cr=src['credit'];provider=json.loads((g.P/(case+'-provider.json')).read_text())
    quote=sum(Decimal(str(x['quantity']))*Decimal(x['quoted_unit_price']) for x in lines)
    listval=sum(Decimal(str(x['quantity']))*Decimal(x['list_price']) for x in lines)
    cost=sum(Decimal(str(x['quantity']))*Decimal(x['standard_cost']) for x in lines)
    exposure=quote+Decimal(cr['unbilled_committed_amount'])
    add('\\newpage\n## Case '+n+' — initial source review')
    add('**Identity:** `'+case+'`; v2 packet; v3 Credit scope. Cutoff `'+ctx['as_of_at']+'`; snapshot `'+ctx['data_snapshot_ref']+'`; policy `'+ctx['applied_policy_set_code']+'`; catalogue `'+ctx['catalog_version_used']+'`. **No prior recommendation is shown.**')
    add('**Submitted original:** `'+d['deal_id']+'`, submitted '+d['submitted_at']+'; customer `'+c['customer_id']+'` ('+c['customer_name']+'), account '+c['account_status']+', '+str(c.get('country_code'))+'/'+str(c.get('region'))+'; requested delivery '+str(d['requested_delivery_date'])+' to '+str(d['destination_country_code'])+'/'+str(d['destination_region'])+'; shipping '+str(d['shipping_service_code'])+'; terms '+g.val(d['terms_json'])+'; currency '+d['currency_code']+'. [packet `/source_rows/deal`, `/source_rows/customer`]')
    for i,l in enumerate(lines):
        add('- **Line '+str(i+1)+'** `/source_rows/lines/'+str(i)+'`: '+l['product_code']+'; quantity '+str(l['quantity'])+' '+str(l['unit_of_measure'])+'; mode '+l['fulfillment_mode']+'; unit list €'+l['list_price']+', quoted €'+l['quoted_unit_price']+', standard cost €'+l['standard_cost']+'; configuration '+g.val(l['configuration_json'])+'; activation '+str(l['requested_activation_date'])+'; installation requested '+str(l['installation_requested'])+'.')
    add('**Recomputed, before applying policy:** list €'+g.money(listval)+'; quote €'+g.money(quote)+'; standard cost €'+g.money(cost)+'; discount '+f'{(listval-quote)*100/listval:.6f}'+'%; margin '+f'{(quote-cost)*100/quote:.6f}'+'%. Credit exposure under v3 complete-zero declaration: €'+g.money(quote)+' quote + €'+g.money(Decimal(cr['unbilled_committed_amount']))+' unbilled + €0 scoped AR = €'+g.money(exposure)+' versus €'+g.money(Decimal(cr['credit_limit']))+' limit. These are arithmetic, not a case verdict.')
    add('### Selected source evidence')
    for key in ['credit','inventory','inbound_supply','supplier_offers','bom','bom_lines','requirements','production_capacity','digital_capacity','compatibility','shipping_lanes','receivables','payments']:
        add('**'+g.label(key).title()+':**')
        for line in g.factlines(src[key],'/source_rows/'+key):add(line)
    add('**Credit scope:** `scope:/credit_evidence_scope` = '+g.val(s['credit_evidence_scope'])+'.')
    for line in g.factlines(provider['records'],'provider:/records'):add(line)
    add('### Calculation worksheet — source only')
    for line in g.price_rule_steps(src,lines):add('- '+line)
    for line in g.availability_steps(src,ctx,provider,lines):add('- '+line)
    add('### Your first-pass six-responsibility decision (complete in the blinded register)')
    for name,question in [('Configuration','What exact product/version/compatibility predicate applies to this submitted line?'),('Pricing','Which discount and floor predicates trigger on full quantity?'),('Availability','What is established for the original date, and what remains uncommitted or unknown?'),('Credit','What does the scoped exposure and status establish, with any completeness limitation?'),('Policy','Which distinct active policy rules trigger, and which issues are merely downstream of another finding?'),('Approval','What human route, if any, can be presented now, and which prerequisites prevent execution?')]:
        add('- **'+name+':** '+question+' Finding [ ]; rule/pointer [ ]; calculation [ ]; uncertainty [ ]; action [ ].')
    add('**Overall:** Gate [ ]; reason and precedence [ ]; original-deal required actions [ ]; alternative (if any) [ ]; customer acceptance or human authorization [ ]; unresolved evidence [ ]. **Author identity [ ]; date/time [ ]; assistance disclosure [ ].**')
    add('**Traceability:** packet SHA-256 `'+entry['packet_sha256']+'`; provider bytes SHA-256 `'+entry['provider_file_sha256']+'`; v3 scope SHA-256 `'+g.digest(g.canonical(s))+'`. This identity check is separate from adjudication.')
    blind.append({'case_id':case,'packet_sha':entry['packet_sha256'],'provider_sha':entry['provider_file_sha256'],'scope_sha':g.digest(g.canonical(s)),'quote':str(quote)})

add('\\newpage\n# Part III — Supplemental source appendix (separate cohort)')
add('Cases 039, 040 and 041 are separate supplements; they are not counted in the 36 original decisions. Cases 037–038 are preflight diagnostics. No supplemental expected answer is accepted here.')
for f,ids in [(g.ROOT/'repo/phase-1c-data/evaluation/configuration-extension/v1/source_cases.json',['EVAL-PREP-039']),(g.ROOT/'credit-evidence-v3/control_cases_v1.json',['EVAL-PREP-040','EVAL-PREP-041'])]:
    x=json.loads(f.read_text())
    for c in x['cases']:
        if c['case_id'] not in ids:continue
        add('## Supplemental '+c['case_id'][-3:]+' — source facts, no proposed answer')
        add('Source extension `'+x['extension_id']+'`; source-definition hash `'+x['base_v2_source_definition_sha256']+'`.' if 'base_v2_source_definition_sha256' in x else 'Source extension `'+x['extension_id']+'`; source-definition hash `'+x['base_source_definition_sha256']+'`.')
        if 'credit_evidence_scope' in c:add('Credit completeness declaration: '+g.val(c['credit_evidence_scope'])+'.')
        for table,rows in c['tables'].items():
            if not rows:continue
            add('**'+g.label(table).title()+'**')
            for line in g.factlines(rows,'/tables/'+table):add(line)
        add('First-pass specialist findings and overall gate: [ ]; evidence and uncertainty: [ ]; author decision and rationale: [ ]. Supplemental review belongs in a distinct intake, never in the 36-row original register.')
add('# Part IV — Freeze and compare')
add('Complete the blinded register with six findings, gate, actions, evidence, rationale, identity and timestamp. Run the freeze validator to emit a canonical first-pass JSON snapshot and SHA-256; keep that snapshot immutable. Only then open the separate technical handbook/matrix. In a second register version, compare each responsibility and gate, log agreement/disagreement, correct or leave unresolved with reasons, and sign your final author decision. A model agreement never makes a label accepted. Current release gates remain open until a documented methodology criterion and all source, runtime and final audit requirements pass.')
import re
md='\n'.join(sections)
md=re.sub(r'`((?:packet|provider|scope):/[^`\s]+)`',lambda m:r'\path{'+m.group(1)+'}',md)
(O/'Blinded_Source_First_Handbook.md').write_text(md)
(O/'blind_register_seed.json').write_text(json.dumps({'commit':g.COMMIT,'cases':blind,'responsibilities':g.RESP},indent=2))
assert len(blind)==36
assert 'AI-assisted technical recommendation' not in md and 'proposed whole-deal gate' not in md.lower()
print('Blinded dossiers',len(blind),'characters',len(md))
