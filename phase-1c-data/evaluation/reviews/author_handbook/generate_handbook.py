#!/usr/bin/env python3
"""Rebuild a provisional author handbook and register seed from pinned Phase 1C packets.

No answer acceptance is performed. The index hashes the packet payload as compact
sorted JSON; provider files are hashed as stored bytes. All 36 must validate.
"""
from __future__ import annotations
import hashlib, json, pathlib, re
from datetime import datetime
from decimal import Decimal

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
COMMIT = 'c80460492def9b32771089997bfccff7c4732288'
P = ROOT / 'v2_packets'
E = ROOT / 'repo/phase-1c-data/evaluation'
INDEX = json.loads((P/'packet_index.json').read_text())
MATRIX = json.loads((E/'reviews/v3_six_responsibility_technical_matrix.json').read_text())
SCOPE = json.loads((ROOT/'credit-evidence-v3/credit_scope_v3.json').read_text())
RESP = ['Configuration','Pricing','Availability','Credit','Policy','Approval']
POINTER = {'Configuration':'/source_rows/compatibility','Pricing':'/source_rows/rules/pricing_rules','Availability':'/source_rows/inventory','Credit':'/source_rows/credit','Policy':'/source_rows/rules/policy_rules','Approval':'/source_rows/rules/approval_rules'}

def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def money(x): return f'{x:,.2f}'
def esc(x): return str(x).replace('|','\\|').replace('\n','; ')
def val(x):
    if isinstance(x,(dict,list)): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return 'null' if x is None else str(x)
def label(x): return x.replace('_',' ')
def field(k,v):
    rendered=esc(val(v))
    # xurl allows breaks at punctuation in long IDs and serialized JSON values.
    if len(rendered)>44 and '|' not in rendered: rendered=r'\path{'+rendered+'}'
    return f'{label(k)}={rendered}'
def rowid(r):
    for k in ('inventory_id','inbound_supply_id','offer_id','capacity_id','digital_capacity_id','compatibility_rule_id','shipping_lane_id','requirement_id','bom_id','bom_line_id','id'):
        if k in r: return f'{k}={r[k]}'
    return ', '.join(f'{k}={v}' for k,v in r.items() if k.endswith('_id') or k.endswith('_code'))[:100] or '(row position)'
def factlines(obj,path,limit=None):
    if obj is None: return [f'- **Verified source fact** `{path}`: null (no selected record).']
    if isinstance(obj,list):
        if not obj:return [f'- **Verified source fact** `{path}`: empty selected set. This alone never proves source-wide completeness.']
        lines=[]
        for i,r in enumerate(obj):
            if not isinstance(r,dict): lines.append(f'- **Verified source fact** `{path}/{i}`: {esc(val(r))}.');continue
            fields='; '.join(field(k,v) for k,v in r.items() if k not in ('attributes_json','configuration_json'))
            lines.append(f'- **Verified source fact** `{path}/{i}` ({esc(rowid(r))}): {fields}.')
        return lines
    return [f'- **Verified source fact** `{path}`: '+ '; '.join(field(k,v) for k,v in obj.items())+'.']
def ptrget(packet, scope, ptr, provider):
    if ptr.startswith('scope:/'): cur={'credit_evidence_scope':scope['credit_evidence_scope']}; p=ptr[7:]
    elif ptr.startswith('packet:/'): cur=packet; p=ptr[8:]
    elif ptr.startswith('provider:/'): cur=provider; p=ptr[10:]
    else: return None
    try:
        for key in p.split('/'):
            if key: cur=cur[int(key)] if isinstance(cur,list) else cur[key]
        return cur
    except (KeyError,IndexError,TypeError,ValueError): return None
def age_hours(cutoff, observation):
    a=datetime.fromisoformat(cutoff.replace('Z','+00:00'))
    b=datetime.fromisoformat(observation.replace('Z','+00:00'))
    return (a-b).total_seconds()/3600
def availability_steps(src,ctx,provider,lines):
    cutoff=ctx['as_of_at']; qty=Decimal(str(lines[0]['quantity'])); result=[]
    for i,r in enumerate(src['inventory']):
        free=Decimal(r['quantity_on_hand'])-Decimal(r['quantity_allocated']); age=age_hours(cutoff,r['snapshot_at'])
        result.append(f'Inventory `/source_rows/inventory/{i}`: {r["quantity_on_hand"]} on hand − {r["quantity_allocated"]} allocated = {free} free units of `{r["product_id"]}`; observation age {age:.2f} h, '+('within' if 0<=age<=24 else 'outside')+' the inclusive 24 h freshness window. '+('Compare with '+str(qty)+' submitted units if this is the finished product.' if r['product_id']==lines[0]['product_id'] else 'For a component, multiply BOM units per finished product by submitted quantity and compare with free stock.'))
    for i,r in enumerate(src['inbound_supply']):
        free=Decimal(r['quantity'])-Decimal(r['quantity_allocated'])
        result.append(f'Inbound `/source_rows/inbound_supply/{i}`: {r["quantity"]} − {r["quantity_allocated"]} = {free} unallocated units; status `{r["status"]}`, PO `{r["po_status"]}`, expected {r["expected_date"]}. Compare receipt with requested date and downstream work/shipping; a dated PO is not received stock.')
    for i,r in enumerate(src['supplier_offers']):
        result.append(f'Offer `/source_rows/supplier_offers/{i}`: minimum/mode/maximum {r["lead_days_min"]}/{r["lead_days_mode"]}/{r["lead_days_max"]} supplier workdays, minimum order {r["minimum_order_qty"]}, multiple {r["order_multiple"]}, validity {r["valid_from"]}–{r["valid_to"]}. This is an uncommitted route; apply its stated calendar and then production/dispatch rather than treating the modal lead as a guarantee.')
    if src['bom_lines']:
        for i,r in enumerate(src['bom_lines']):
            needed=qty*Decimal(r['required_quantity_per_output'])*(Decimal(1)+Decimal(r.get('scrap_pct','0'))/100)
            result.append(f'BOM `/source_rows/bom_lines/{i}`: {qty} finished × {r["required_quantity_per_output"]} per unit × (1 + {r.get("scrap_pct","0")}% scrap) = {needed} units of `{r["component_product_id"]}`; mandatory={r["is_mandatory"]}, substitute group={r.get("substitute_group_code")}. Compare only compatible selected rows and dated supply.')
    if src['requirements']:
        for i,r in enumerate(src['requirements']):
            hours=qty*Decimal(r['hours_per_unit'])+Decimal(r['setup_hours'])
            result.append(f'Operation `/source_rows/requirements/{i}`: {qty} × {r["hours_per_unit"]} h + {r["setup_hours"]} setup h = {hours} h for `{r["capability_code"]}`; compare separate dated resource slots, sequence and freshness. This arithmetic does not book a slot.')
    if src['production_capacity']:
        capabilities=sorted({r['capability_code'] for r in src['production_capacity']})
        for cap in capabilities:
            arr=[r for r in src['production_capacity'] if r['capability_code']==cap]
            dates=[]
            for r in arr:
                free=Decimal(r['available_capacity_hours'])-Decimal(r['allocated_capacity_hours'])
                age=age_hours(cutoff,r['snapshot_at'])
                dates.append(f'{r["capacity_date"]}: {free} h ({"fresh" if 0<=age<=24 else "stale/future"})')
            result.append(f'Capacity `{cap}` `/source_rows/production_capacity`: '+', '.join(dates)+'. Hours across resource types must meet their respective operation, not be indiscriminately summed.')
    for i,r in enumerate(src['digital_capacity']):
        free=Decimal(r['capacity_total'])-Decimal(r['quantity_allocated']); age=age_hours(cutoff,r['snapshot_at'])
        result.append(f'Digital pool `/source_rows/digital_capacity/{i}`: {r["capacity_total"]} total − {r["quantity_allocated"]} allocated = {free} free `{r["capacity_unit"]}`; snapshot age {age:.2f} h ({"fresh" if 0<=age<=24 else "stale/future"}); status `{r["commitment_status"]}`. For a 12-month `instance_month` line, {qty}/12 = {qty/12} simultaneous instances; check the full provider term.')
    for i,r in enumerate(provider['records']):
        result.append(f'Provider `/records/{i}`: '+', '.join(f'{k}={v}' for k,v in r.items() if k in ('verified_at','valid_until','covers_from','covers_until','quantity','term_code','status','provider_id','product_id'))+'. Check matching identity/quantity and anniversary coverage; a later validity date does not extend the coverage end.')
    for i,r in enumerate(src['compatibility']):
        result.append(f'Compatibility `/source_rows/compatibility/{i}`: `{r["rule_type"]}` condition {val(r["condition_json"])} for `{r["source_product_id"]}`; exact region/eligibility is a rule result, not evidence of a booked service slot.')
    for i,r in enumerate(src['shipping_lanes']):
        result.append(f'Lane `/source_rows/shipping_lanes/{i}`: {r["transit_workdays"]} transit workday(s), {r["cutoff_local_time"]} local cutoff, dispatch weekdays {val(r["dispatch_weekdays_json"])} in {r["origin_time_zone"]}. An actual dispatch and customer delivery remain unconfirmed.')
    return result or ['No positive availability record is selected; assess missing evidence and source scope rather than infer impossibility.']
def price_rule_steps(src,lines):
    out=[]
    for i,l in enumerate(lines):
        quote=Decimal(str(l['quantity']))*Decimal(l['quoted_unit_price'])
        cost=Decimal(str(l['quantity']))*Decimal(l['standard_cost'])
        listval=Decimal(str(l['quantity']))*Decimal(l['list_price'])
        margin=(quote-cost)*100/quote if quote else Decimal(0)
        discount=(listval-quote)*100/listval if listval else Decimal(0)
        rule=next((r for r in src['rules']['pricing_rules'] if r['rule_type']=='category_margin_floor' and r['scope_value']==l['category']),None)
        if rule:
            floor=Decimal(str(rule['condition_json']['margin_pct_lt']))
            diff=floor-margin
            out.append(f'Line {i+1}: €{money(quote)} quote − €{money(cost)} standard cost = €{money(quote-cost)} gross profit; / €{money(quote)} × 100 = {margin:.6f}% margin. Rule `{rule["pricing_rule_id"]}` floor {floor}%, shortfall {max(diff,Decimal(0)):.6f} percentage points. '+('More than two points below floor is a hard block.' if diff>2 else 'Within the floor or two-point exception band; inspect any separate exception predicate.'))
        out.append(f'Line {i+1}: (€{money(listval)} list − €{money(quote)} quote) / €{money(listval)} list × 100 = {discount:.6f}% discount. >10% Director flag={discount>10}; >20% VP flag={discount>20}; >35% hard cap={discount>35}.')
    return out

packets={}; sources={}; controls=[]
for entry in INDEX['cases']:
    case=entry['case_id']; assert re.fullmatch(r'EVAL-PREP-\d{3}',case)
    blob=json.loads((P/(case+'.json')).read_text()); payload=blob['payload']
    assert digest(canonical(payload))==entry['packet_sha256'] and blob.get('sha256',entry['packet_sha256'])==entry['packet_sha256']
    assert digest((P/(case+'-provider.json')).read_bytes())==entry['provider_file_sha256']
    assert payload['case_id']==case
    packets[case]=payload; sources[case]=entry
assert list(packets)==[f'EVAL-PREP-{i:03d}' for i in range(1,37)]
assert [c['case_id'] for c in MATRIX['cases']]==list(packets)
assert [c['case_id'] for c in SCOPE['cases']]==list(packets)
assert MATRIX['accepted_answers']==0 and len(MATRIX['cases'])*len(RESP)==216
assert digest(canonical(INDEX))==MATRIX['base_v2_index_sha256']==SCOPE['base_v2_index_sha256']
for m,s in zip(MATRIX['cases'],SCOPE['cases']):
    case=m['case_id']; entry=sources[case]; p=packets[case]
    provider=json.loads((P/(case+'-provider.json')).read_text())
    assert s['base_packet_sha256']==m['v2_packet_sha256']==entry['packet_sha256']
    assert s['base_provider_file_sha256']==m['v2_provider_file_sha256']==entry['provider_file_sha256']
    assert digest(canonical(s))==m['v3_scope_sha256'], case
    assert set(m['six_responsibilities'])==set(RESP)
    assert s['credit_evidence_scope']['completeness']=='declared_complete_zero'
    assert not p['source_rows']['receivables'] and not p['source_rows']['payments']
    for name,r in m['six_responsibilities'].items():
        for pointer in r['source_pointers']:
            assert ptrget(p,s,pointer,provider) is not None, (case,name,pointer)

parts=[]
def add(s=''): parts.append(s+'\n')
add('---\ntitle: "Deal Desk Orchestrator | Author Adjudication Handbook"\nsubtitle: "36 original evaluation cases · source-bound provisional review"\nauthor: "Prepared for Ali Alnaggar"\ndate: "31 October 2026"\ngeometry: margin=22mm\nfontsize: 10pt\ncolorlinks: true\nheader-includes:\n  - \\usepackage{xurl}\n  - \\usepackage{ragged2e}\n  - \\RaggedRight\n---')
add('# Reading guide and status')
add('**All proposed findings in this handbook are pending author adjudication. Accepted original answers: 0/36.** This is an AI-assisted working reference, not an independently validated answer key. It uses the pinned v2 packet payload and separate provider bytes, the v3 fictional Credit scope overlay, and the v3 six-responsibility technical matrix. GitHub branch `phase1c-candidate-contract`, source commit `'+COMMIT+'`. PR #1 remains draft and `ready_for_generation=false`. The 100 development diagnostics, historical outcomes, supplemental 039 and controls 040–041 are not counted among the 36.')
add('**Evidence labels used throughout:** **Verified source fact** = copied from the hash-checked packet or scope; **Deterministic calculation** = recomputed from stated values and approved synthetic conventions; **AI-assisted technical recommendation** = the preserved matrix proposal, to challenge; **Business assumption/ambiguity** = a convention or unresolved judgment; **Final author decision** = only an explicit entry by Ali in the register with rationale and timestamp. A blank field means pending, never approval.')
add('The packet hash is SHA-256 of the canonical compact sorted `payload` JSON, while the provider hash is SHA-256 of the exact provider-file bytes. A file byte hash for the pretty-printed packet is different. Source pointers such as `packet:/source_rows/inventory/0` address the packet payload. The v3 Credit declaration is a distinct overlay; it does not rewrite v2 or the archived drafts.')
add('## Navigation')
add('Part I explains the project and rules. Part II contains a complete separate dossier for every original case, with exact pointers and a decision space. Part III compares difficult cases. Part IV gives the review and release procedure. The spreadsheet holds the editable author decisions. Read each packet-based fact before the model-assisted recommendation.')
add('# Part I — Project, method and rule reference')
add('## Business problem and research purpose')
add('A salesperson submits a structured business-to-business quote spanning product configuration, price, supply or service feasibility, customer credit, policy and approvals. A conventional handoff among teams can produce inconsistent judgments or premature promises. The thesis tests whether a governed orchestration of six specialist responsibilities can produce evidence-linked, bounded recommendations and human actions. Evaluation must assess the submitted original deal, preserve negative and missing evidence, and separate specialist correctness from the overall gate. The synthetic dataset is fictional and versioned; it is not a customer, supplier or market validity study. The system may recommend a revision or human route; it cannot approve a deal, reserve stock, commit a supplier or promise delivery. [Root README; Phase 1B architecture; Phase 1C README at source commit.]')
add('## Workflow and ownership')
add('The run pins the deal, catalogue, policy set and `as_of_at` timestamp. A read-only evidence reader selects rows valid for that run. Configuration checks sellability, version and explicit product or regional compatibility. Pricing recomputes the submitted quote from each full line quantity and catalogue standard cost, then tests discounts and category margin floors. Availability/Production/Fulfillment checks current stock, inbound supply, supplier alternatives, bill of materials (BOM), dated production slots, provider proof, regional service coverage and shipping. Credit computes exposure from receivables, payments, unbilled commitments and the quote, but must distinguish empty selected rows from a complete snapshot. Policy applies explicit hard blocks and escalation predicates. Approval composes an applicable human route only after blockers and preconditions are exposed. The orchestrator retains subordinate findings and chooses the highest-precedence gate. Source facts and calculations are deterministic; AI reasoning interprets evidence, proposes alternatives and explains uncertainty under these boundaries. [Phase 1B architecture; v2 packet `/business_contract`; matrix.]')
add('## Gate vocabulary and uncertainty')
for k,v in packets['EVAL-PREP-001']['business_contract']['gates'].items():
    add(f'- **{k}**: {esc(val(v))}.')
add('A finding `no_issue_identified` means the cited check did not establish a problem; it is not global clearance. `requires_adjudication` flags an unresolved attribution or rule interpretation. `human_review_required` identifies a route request, not granted approval. `needs_evidence` means the available evidence cannot establish a current fact, whereas `needs_revision` means the original submitted quantity/date/region cannot be supported and a changed proposal is needed. `needs_commitment` is a feasible but uncommitted conditional route. `blocked` is a hard prohibition; other favorable findings remain visible but do not authorize the deal. Abstention should name the missing fact and the check it prevents. No missing record should be silently read as a favorable result.')
add('An alternative is not the submitted deal. A substituted component, shifted date, reduced quantity, altered service or destination requires a revised proposal and renewed checks; customer acceptance may also be required. A conditional source route is explicitly hypothetical until actual commitments are obtained. [v2 `/business_contract/gates` and `/business_contract/routing`.]')
add('## Synthetic source model and selection')
add('The Phase 1C relational build contains 24 PostgreSQL tables, including deals and lines, customers, catalogue and product facts, compatibility, inventory, inbound supply, supplier offers, BOM and components, production capacity, digital capacity and provider proof, shipping lanes, receivables and payments, credit commitments and pricing, policy and approval rules. Each isolated evaluation packet captures the selected rows under `/source_rows`; `/run_context` records the policy set, catalogue, cutoff, snapshot, deal and run identity. The separate provider file contains proof records. Selection is scoped by product, customer, region, validity and cutoff; a later observation must not retroactively justify an earlier run. Fresh PostgreSQL replay, selected rows and hash checks were documented on 30 October, not rerun for this handbook. [PostgreSQL verification report.]')
add('The v3 overlay declares a *fictional complete-zero* AR/payment population for each individually reviewed original case, bound to the unchanged v2 packet and customer/cutoff. This is a constructed scenario fact, not evidence of real-world solvency or payment history. Empty rows without this explicit scope remain unknown: control 041 demonstrates that distinction, while control 040 has a nonempty overdue receivable with a partial payment. AR means accounts receivable, i.e. unpaid customer invoices. [Credit v3 README and `credit_scope_v3.json`.]')
add('## Versioned business conventions and thresholds')
contract=packets['EVAL-PREP-001']['business_contract']
for key in ['costing','digital_term','evidence_age','service_scope','routing']:
    add('### '+label(key).title())
    for k,v in contract[key].items(): add(f'- `{k}`: {esc(val(v))}. [packet `/business_contract/{key}/{k}`]')
add('**Pricing calculations:** quote = sum(quantity × quoted unit price); list = sum(quantity × catalogue list price); cost = sum(quantity × versioned standard cost); discount percent = 100 × (list − quote)/list; gross margin percent = 100 × (quote − cost)/quote. The category floor compares line margin in percentage points, not a currency amount. A floor shortfall above two points is a blocker; a positive-margin shortfall of at most two points invokes a human exception. Discount above 10% invokes Sales Director, above 20% Sales VP, and above 35% is a hard block. A nonpositive margin is a hard block. These comparisons are strict where the rule says `_gt` or `_lt`. [packet `/source_rows/rules/pricing_rules` and `/source_rows/rules/policy_rules`.]')
add('**Credit calculations:** exposure = unpaid selected receivables net of applicable selected payments + unbilled committed amount + full submitted quote, under the complete v3 synthetic scope. Exceeding the credit limit by at most 15% is a Finance exception; more than 15% is a hard block. An On-Hold credit status and inactive customer account block; Review status, positive overdue AR, or payment terms above 45 and at most 90 days require Finance review. Terms above 90 days block. Preserve exact rule conditions and allowed-value predicates below. [packet `/source_rows/rules/policy_rules`; v3 scope.]')
add('**Availability:** 24 elapsed hours inclusive for inventory, production, digital capacity and credit commitments; seven elapsed days inclusive for matching provider verification. Stale, future or absent observation does not prove impossibility; seek refreshed evidence. Free stock subtracts allocations. An offer is not received or reserved stock. Production requires components and dated operation hours; shipping requires a valid lane and cutoffs. Digital proof must match identity, quantity, term and covering dates; `valid_until` does not extend `covers_until`. Regional `installation_eligibility` covers service regions but is not a booked slot. [packet `/business_contract/evidence_age`, `/business_contract/digital_term`, `/business_contract/service_scope`.]')
add('**Approval:** routine Regional Manager; higher Sales roles only when the explicit discount, value or supported-but-late proposal conditions trigger. Finance and Legal roles require their own predicates. A blocked submitted deal has no executable approval route; discount escalation cannot waive a hard floor or credit cap. A proposed later date invokes at least Sales Director review and customer acceptance, followed by renewed specialist checks. [packet `/source_rows/rules/approval_rules`; `/business_contract/routing`.]')
add('### Exact active rule catalogue (source facts)')
rules=packets['EVAL-PREP-001']['source_rows']['rules']
for typ in ['pricing_rules','policy_rules','approval_rules']:
    add('#### '+label(typ).title())
    add('| Rule ID | Scope / condition | Action, role or threshold |\n|---|---|---|')
    for i,r in enumerate(rules[typ]):
        rid=r.get('pricing_rule_id') or r.get('policy_rule_id') or r.get('approval_rule_id')
        action=r.get('action_json') or {k:r.get(k) for k in ('severity','required_action','required_role','approval_sequence','is_mandatory') if k in r}
        add('| `'+rid+'` | '+esc(val({'scope_type':r.get('scope_type'),'scope_value':r.get('scope_value'),'condition':r.get('condition_json')}))+' | '+esc(val(action))+' |')
    add(f'Source: every case packet `/source_rows/rules/{typ}`; review each case for exact active applicability. These are synthetic policy conventions, not universal business law.')
add('## Evidence and review discipline')
add('Read `packet:/...` as an exact JSON pointer into the pinned packet payload; `scope:/credit_evidence_scope` is the v3 declaration. A zero-row selection only says nothing was selected. Compare source timestamps with `run_context/as_of_at`; identify the scope and any missing or contradictory record. Distinguish an explicit `eligible=false` from missing eligibility, an expired provider coverage period from absent provider proof, and a hard block from a human escalation. An AI recommendation needs its cited source and the relevant deterministic rule before the author can accept it. If a rule is undefined, record an unresolved assumption rather than inventing a threshold.')
add('Ali is the sole accountable author. AI generated the technical matrix and this presentation; the separate second-model review was contemplated but is not a completed independent expert label. Author adjudication can generate transparent thesis labels, with source binding, corrections, disclosed assistance and an audit trail. It cannot claim independent human validation. Any formally mandated second-model or external review gate must be changed explicitly with academic approval if applicable. [second-model methodology decision; release checklist.]')

add('# Part II — 36 original case dossiers')
register=[]
for m,s in zip(MATRIX['cases'],SCOPE['cases']):
    case=m['case_id']; n=case[-3:]; p=packets[case]; src=p['source_rows']; ctx=p['run_context']; deal=src['deal']; lines=src['lines']; credit=src['credit']; customer=src['customer']; entry=sources[case]
    quote=sum(Decimal(str(l['quantity']))*Decimal(l['quoted_unit_price']) for l in lines)
    list_total=sum(Decimal(str(l['quantity']))*Decimal(l['list_price']) for l in lines)
    cost=sum(Decimal(str(l['quantity']))*Decimal(l['standard_cost']) for l in lines)
    disc=(list_total-quote)*100/list_total if list_total else None
    margin=(quote-cost)*100/quote if quote else None
    commitments=Decimal(credit['unbilled_committed_amount']); exposure=quote+commitments
    limit=Decimal(credit['credit_limit']); over=(exposure-limit)*100/limit if limit else None
    assert not src['receivables'] and not src['payments']
    add('\\newpage\n## Case '+n+' — '+m['archetype'].replace('-',' ').title())
    add('**A. Identity and purpose.** `'+case+'`; v2 unchanged input, v3 Credit scope. **Documented scenario archetype:** `'+m['archetype']+'` in the matrix and scope; the behavior inferred from that name must be checked against the rows below. This case tests how the six checks combine around the source distinction; paired quantities are not interchangeable. **Proposed whole-deal gate:** `'+m['overall_technical_gate_proposal']+'` (AI-assisted, pending).')
    add('**B. Submitted original deal.** '+esc(customer['customer_name'])+' (`'+customer['customer_id']+'`), account '+esc(customer['account_status'])+', segment '+esc(customer.get('size_segment'))+', country/region '+esc(customer.get('country_code'))+'/'+esc(customer.get('region'))+'. Deal `'+deal['deal_id']+'`, submitted '+deal['submitted_at']+', requested delivery '+esc(deal.get('requested_delivery_date'))+', destination '+esc(deal.get('destination_country_code'))+'/'+esc(deal.get('destination_region'))+', currency '+deal['currency_code']+', shipping `'+esc(deal.get('shipping_service_code'))+'`, terms '+esc(val(deal['terms_json']))+'. Cutoff '+ctx['as_of_at']+'.')
    for i,l in enumerate(lines):
        add('- **Submitted line '+str(i+1)+'** `/source_rows/lines/'+str(i)+'`: ID `'+l['deal_line_id']+'`; product `'+l['product_code']+'`; mode `'+esc(l['fulfillment_mode'])+'`; '+str(l['quantity'])+' '+esc(l.get('unit_of_measure'))+'. Unit list €'+esc(l['list_price'])+', quote €'+esc(l['quoted_unit_price'])+', standard cost €'+esc(l['standard_cost'])+'. Configuration '+esc(val(l.get('configuration_json')))+'; activation '+esc(l.get('requested_activation_date'))+'; installation requested '+str(l.get('installation_requested'))+'.')
    add('**Deterministic calculation:** list €'+money(list_total)+'; quote €'+money(quote)+'; catalogue standard cost €'+money(cost)+'; discount '+f'{disc:.6f}'+'%; quoted gross margin '+f'{margin:.6f}'+'%. Credit: quote €'+money(quote)+' + unbilled commitments €'+money(commitments)+' + declared complete-zero AR €0 = €'+money(exposure)+'; limit €'+money(limit)+'; '+('over limit '+f'{over:.6f}'+'%' if over>0 else 'headroom €'+money(limit-exposure))+'. Read the source rows and floor predicates before accepting any threshold finding. [packet `/source_rows/lines`, `/source_rows/credit`, `/source_rows/rules`; v3 scope.]')
    add('**C. Pinned source evidence.** The rows below are the selected source at this exact cutoff. Identifiers and row pointers are given; a selected empty list is distinguished from a complete population declaration. A source row can contain extra fields in the packet, but every decision-relevant field is presented or cited.')
    for key in ['customer','credit','inventory','inbound_supply','supplier_offers','bom','bom_lines','requirements','production_capacity','digital_capacity','compatibility','shipping_lanes','receivables','payments']:
        if key in ('customer','credit'): continue
        add('**'+label(key).title()+':**')
        for line in factlines(src[key],'/source_rows/'+key):add(line)
    add('- **Verified source fact** `scope:/credit_evidence_scope`: '+esc(val(s['credit_evidence_scope']))+'. The empty AR and payment selections are complete only under this separate fictional case-scope declaration.')
    pf=json.loads((P/(case+'-provider.json')).read_text());add('**Separate provider record:**')
    for line in factlines(pf['records'],'provider:/records'):add(line)
    add('**D. Six specialist assessments.** Each recommendation and basis below is the existing AI-assisted technical matrix at this commit. The row cites the exact source fields to inspect; the calculations above are independently recomputed from packet values, not acceptance of the matrix.')
    for resp in RESP:
        r=m['six_responsibilities'][resp]
        add('### '+resp)
        add('**Responsibility:** '+{'Configuration':'Check the submitted line, version, sellability and exact compatibility/dependency predicates.','Pricing':'Check full-quantity quote, discount, standard-cost margin, category floor and escalation or hard cap.','Availability':'Check stock or supply, dated production or digital proof, service coverage, shipping and original date.','Credit':'Check scoped AR/payment completeness, commitments, quote exposure, limit, status and terms.','Policy':'Apply independently triggered policy predicates; avoid counting one evidence problem as a second independent prohibition.','Approval':'Compose a provisional human route after blockers, revisions, evidence and commitments; never grant approval.'}[resp])
        add('**AI-assisted technical recommendation:** `'+r['technical_recommendation']+'`. '+r['source_basis'])
        add('**Citations and inspection:** '+', '.join('`'+x+'`' for x in r['source_pointers'])+'.')
        if resp=='Pricing':
            add('**Deterministic calculation:** quote €'+money(quote)+'; discount '+f'{disc:.6f}'+'%; margin '+f'{margin:.6f}'+'%. A discount escalation cannot cure a hard floor shortfall. [packet `/source_rows/lines`, `/source_rows/rules/pricing_rules`.]')
            for step in price_rule_steps(src,lines):add('- '+step)
        if resp=='Credit': add('**Deterministic calculation:** €'+money(quote)+' + €'+money(commitments)+' + €0 scoped receivables = €'+money(exposure)+' against €'+money(limit)+'. '+('Over-limit '+f'{over:.6f}'+'%; compare 15% exception ceiling.' if over>0 else 'Within limit; do not infer real-world payment history.')+' [packet `/source_rows/credit`, `/source_rows/receivables`, `/source_rows/payments`; v3 scope.]')
        if resp=='Availability':
            add('**Deterministic source walkthrough (not a commitment):**')
            for step in availability_steps(src,ctx,pf,lines): add('- '+step)
        if resp in ('Availability','Configuration'):
            add('**Review counterargument / uncertainty:** inspect the selected row states, dates and exact rule scope above; absence of a selected alternative is not a universal impossibility claim. A feasible hypothetical alternative is uncommitted and may need customer acceptance if it changes the original deal.')
        elif resp=='Approval':add('**Review action:** state the exact applicable roles and whether the current route is executable; a `blocked` gate means no executable approval of this submission.')
        else:add('**Review action:** identify exact triggered rule ID and its consequence; mark any non-triggered or unsupported narrative claim for correction.')
        add('**Author decision required:** accept, correct, reject or unresolved for this responsibility; record the finding, action, rationale and cited packet pointer in the register. This proposal is not fully accepted by source-binding alone.')
    add('**E. Overall gate and actions.** AI-assisted proposal `'+m['overall_technical_gate_proposal']+'`. Apply the v2 precedence blocked → needs_revision → needs_evidence → needs_commitment → approval_required, retaining subordinate findings. Verify whether each lower finding is an independent blocker, a warning, or a conditional human action. A changed date, quantity, destination, component or terms requires a new proposal, renewed checks and any necessary customer acceptance. No route here is a reservation, delivery promise or approval.')
    question=('Confirm the selected conditional modal route, its uncommitted Sep 10 arrival, unsupported maximum-lead route and exact six findings.' if n=='020' else 'Decide whether regional `eligible=false` is a Configuration incompatibility and/or an Availability service-coverage finding without double-counting it.' if n in ('029','030') else 'Confirm the six source-backed findings, exact rule IDs, gate precedence and human actions; correct any unsupported claim.')
    add('**F. Author adjudication.** Priority question: '+question+' **Provisional recommendation:** challenge the six matrix findings against the cited rows; accept the gate only if the original deal satisfies its stated meaning. **Alternative:** correct a responsibility or gate with source-based rationale, or leave unresolved if a policy/business convention is missing. **Decision space (to enter in Excel):** Configuration [ ]; Pricing [ ]; Availability [ ]; Credit [ ]; Policy [ ]; Approval [ ]; Overall [ ]; case status accept/correct/reject/unresolved [ ]; author identity [ ]; timestamp [ ]; source citations [ ]; rationale [ ]; AI-assistance disclosure [ ]. Blank means no decision.')
    add('**G. Traceability and limits.** v2 packet payload SHA-256 `'+entry['packet_sha256']+'`; provider-file byte SHA-256 `'+entry['provider_file_sha256']+'`; v3 scope SHA-256 `'+m['v3_scope_sha256']+'`; v2 source definition SHA-256 `'+SCOPE['base_v2_source_definition_sha256']+'`; technical matrix JSON `phase-1c-data/evaluation/reviews/v3_six_responsibility_technical_matrix.json`, `cases['+str(int(n)-1)+']`, six-responsibility entries. No case acceptance is implied by hash validation, PostgreSQL replay or technical recommendation.')
    register.append({'case_id':case,'archetype':m['archetype'],'proposed_gate':m['overall_technical_gate_proposal'],'packet_sha':entry['packet_sha256'],'provider_sha':entry['provider_file_sha256'],'scope_sha':m['v3_scope_sha256'],'quote':str(quote),'exposure':str(exposure),'priority':'high' if n in ('020','029','030','031','032','033','034') else 'standard','question':question,'recommendations':{r:m['six_responsibilities'][r]['technical_recommendation'] for r in RESP}})

add('\\newpage\n# Part III — Cross-case decision support')
add('| Cases | Differentiating source | Provisional gate | Critical review |\n|---|---|---|---|')
for a,b in [(1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16),(17,18),(19,20),(21,22),(23,24),(25,26),(27,28),(29,30),(31,32),(33,34),(35,36)]:
    rr=register[a-1];add(f'| {a:03d}–{b:03d} | {rr["archetype"]}; quantities and dates differ | `{rr["proposed_gate"]}` | Compare both packets individually, not one copied answer. |')
add('## Case 020 — conditional delivery and route')
add('**Verified source fact:** four workstations due 11 September; zero compute stock; a confirmed seven-unit compute PO arrives 2 October and cannot substantiate the requested date. A matching active offer quotes 2/4/6 supplier workdays at €240 per compute unit; it is not a receipt or commitment. Assembly and test need 2.5 hours each for four units, with separate available weekday slots; the lane needs two weekdays and a 16:00 cutoff. [020 packet `/source_rows/inventory`, `/inbound_supply/0`, `/supplier_offers/0`, `/production_capacity`, `/shipping_lanes/0`.]')
add('**Deterministic projections, conditional:** minimum receipt 3 September → assembly 3rd/test 4th → indicative arrival 8th. Modal receipt 7th → assembly 7th/test 8th → indicative arrival 10th. Maximum receipt 9th → assembly 9th but no 10th test observation → arrival unknown. Intraday receipt, workshop booking, component allocations and dispatch are not certified. [case 020 route adjudication record.]')
add('**Author’s earlier bounded business choice:** the timely modal route supports proposing `needs_commitment` for the original date, conditional on supplier lead/order, workshop slots and dispatch/transit confirmation, followed by renewed six checks. This is not acceptance of any of the six findings. Competing conservative treatments are `needs_evidence` for the missing later test slot or `needs_revision` if the October PO becomes the selected route; a later date requires Sales Director and customer acceptance. Your decision in this handbook should confirm or correct the full case and retain the unsupported maximum route.')
add('## 029–030 — regional rule and ownership')
add('**Verified source fact:** `installation_eligibility` row for the submitted service and DE-BY says `eligible=false`; `installation_requested=false` does not remove the scheduled-service line’s regional requirement. No booked service slot exists. [029–030 packets `/source_rows/compatibility/0`, `/source_rows/deal`, `/source_rows/lines/0`.]')
add('**Competing attribution:** Configuration can name an explicit line/service compatibility failure; Availability can name the same geographic service coverage failure and missing slot. A defensible answer may record both specialist perspectives with one underlying cause, or assign the primary explicit rule to Configuration and Availability as downstream feasibility. Do not manufacture two independent hard prohibitions. Proposed `needs_revision` changes destination or offered service and needs customer acceptance, then a slot and renewed checks. State the responsibility boundary in both cases consistently. [v2 batch 025–036 review; S1 service-scope contract.]')
add('## Other high-risk comparisons')
add('- **005–006 and 017–018:** stale inventory or production observation is insufficient evidence of current feasibility, not proof of no supply. The 24-hour boundary is inclusive; check the exact cutoff and observation time.')
add('- **021–026:** billed instance-months are not concurrent instances: 24 over 12 months = two, 48 = four. Match pool and provider proof identity, count and full activation-to-anniversary term. In 025–026, a later `valid_until` does not cure `covers_until=2026-12-31`.')
add('- **031–032:** a €1,000 credit limit is exceeded far beyond the 15% Finance exception ceiling. Existing ordinary or Finance escalation cannot approve a prohibited original submission. The complete-zero declaration is synthetic only.')
add('- **033–034:** unit quote €1,672.96, cost €1,656.40 gives 0.989862% margin, 7.010138 points below the 8% floor. The >10% discount escalation is subordinate to the hard floor block.')
add('- **035–036:** `legal_review` clause invokes Legal plus routine sales review. It is neither prohibited nor already approved. Verify role order and avoid adding Finance without its predicate.')
add('- **All cases:** v3 complete-zero AR/payment scope is declared, not derived from empty rows. The credit commitment timestamp must be fresh. Unknown completeness in supplemental 041 must withhold numeric clearance; nonempty 040 tests overdue AR and partial payment. These controls are not original-case answer labels.')
add('# Part IV — Author review and release process')
add('## Suggested review order')
add('Begin with the seven high-priority cases 020, 029–030, 031–034. Then examine each paired archetype in order: 001–018, 019 and 021–028, 035–036. A paired archetype helps compare quantity/date changes but requires two separate six-finding decisions. Use the `Case Decisions` sheet for one row per original case and `Six Findings` for detailed per-responsibility correction. Batch size 6–12 straightforward cases is practical only after the high-risk interpretations are resolved; no batch action creates acceptance automatically.')
add('## Consolidated provisional matrix')
add('| Case | Archetype | Proposed gate | Configuration | Pricing | Availability | Credit | Policy | Approval |\n|---|---|---|---|---|---|---|---|---|')
for r in register:add('| '+r['case_id'][-3:]+' | '+r['archetype']+' | `'+r['proposed_gate']+'` | '+' | '.join('`'+r['recommendations'][x]+'`' for x in RESP)+' |')
add('## Case acceptance checklist')
add('1. Verify the case ID, v2 packet and provider hashes and v3 scope identity against the manifest. 2. Read the submitted deal and selected rows at the pinned cutoff, including negative and missing evidence. 3. Recalculate quote, list, discount, margin, cost, Credit exposure and any dated feasibility projection. 4. For each of six responsibilities, write the finding, exact rule ID where applicable, source pointer, uncertainty and action. 5. Apply gate precedence without erasing subordinate issues; distinguish the original submission from a conditional revised proposal. 6. Record accept/correct/reject/unresolved for each finding and the overall gate, the final author action, identity, time, rationale, and AI-assistance disclosure. 7. If corrected, preserve the proposal and place the new wording and citation in separate decision fields. 8. Keep any unresolved business convention explicit and do not count the case as accepted. 9. Export a structured reviewer-only answer record, run structural and source-binding validation, and manually approve its substantive content; automated agreement cannot do that.')
add('## After all 36 author decisions')
add('Confirm that each case has seven substantive decisions, six source-backed findings, required actions, author identity/time and disclosure. Close exceptions and case 020/029–030 consistency; preserve corrected text and prior drafts. Record the methodology change from mandatory second-model corroboration explicitly and obtain any required academic approval rather than silently relaxing an earlier release gate. Finish genuine specialist runtime-output field evidence, clean rebuild and source/hash audit, final release review, then update readiness and Phase 2 pin only through an explicit compatibility handoff. PR #1 remains draft and `ready_for_generation=false` until those actual release gates pass. No independent expert validation is claimed.')
add('## Source manifest and reproducibility')
add('The companion `source_manifest.json` records full GitHub commit, index, source-definition and each case packet/provider/scope hash. The 72 packet/provider export files are **workflow artifact bytes**, not tracked individual GitHub files; the index is tracked as `phase-1c-data/evaluation/provisional_packet_index.json`. The reproducibility bundle includes the verified exports, matrix and scope. The script `generate_handbook.py` validates all 36 payload and provider hashes, 216 matrix entries, v3 binding and every matrix pointer before writing this Markdown and the register seed. It does not rerun PostgreSQL and does not adjudicate business correctness. To regenerate from the bundle directory: `python3 generate_handbook.py`; then `pandoc outputs/Author_Adjudication_Handbook.md --pdf-engine=xelatex -o outputs/Author_Adjudication_Handbook.pdf`. Build the workbook with the bundled `build_register.mjs` using the Codex primary runtime artifact tool. A changed source commit or index requires a new manifest and review.')

markdown='\n'.join(parts)
# Use LaTeX's breakable path representation for long JSON pointers in the PDF.
# The Markdown remains a readable, fully editable regeneration source.
markdown=re.sub(r'`((?:packet|provider|scope):/[^`\s]+)`',lambda m:r'\path{'+m.group(1)+'}',markdown)
(OUT/'Author_Adjudication_Handbook.md').write_text(markdown)
(OUT/'register_seed.json').write_text(json.dumps({'commit':COMMIT,'cases':register,'responsibilities':RESP},indent=2))
manifest={'repository':'alialnaggar/DealDeskOrchestrator','branch':'phase1c-candidate-contract','commit':COMMIT,'original_cases':36,'specialist_proposals':216,'acceptance_count':0,'input_version':2,'credit_overlay_version':3,'packet_index_payload_sha256':digest(canonical(INDEX)),'source_definition_sha256':SCOPE['base_v2_source_definition_sha256'],'matrix_file_sha256':digest((E/'reviews/v3_six_responsibility_technical_matrix.json').read_bytes()),'scope_file_sha256':digest((ROOT/'credit-evidence-v3/credit_scope_v3.json').read_bytes()),'source_files':{'packet_index':'phase-1c-data/evaluation/provisional_packet_index.json','packet_provider_exports':'v2_packets/ in reproducibility bundle (verified PostgreSQL workflow artifact, not individually tracked in GitHub)','technical_matrix':'phase-1c-data/evaluation/reviews/v3_six_responsibility_technical_matrix.json','credit_scope':'phase-1c-data/evaluation/credit-evidence-v3/credit_scope_v3.json','postgres_report':'phase-1c-data/evaluation/reviews/phase1c_postgres_verification_2026-10-30.md'},'cases':[{**x,'scope_sha256':m['v3_scope_sha256']} for x,m in zip(INDEX['cases'],MATRIX['cases'])]}
(OUT/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
print('Validated 36 cases, 72 indexed source hashes, 216 matrix pointers groups, and scope binds.')
print('Handbook characters',len(markdown),'case records',len(register))
