'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { z } from 'zod';
import { DealInput, type DealInputDTO } from '@/lib/intake-contract';
import { csrf, json } from './client';

type TextKey='customerId'|'dealId'|'productId'|'lineId'|'quantity'|'requestedDeliveryDate'|'quotedUnitPrice'|'discountPercent'|'currencyCode'|'paymentTermsDays'|'destinationCountryCode'|'destinationRegion'|'shippingServiceCode'|'additionalRequirements'|'configuration';
const initial:Record<TextKey,string>={ customerId:'',dealId:'',productId:'',lineId:'',quantity:'',requestedDeliveryDate:'',quotedUnitPrice:'',discountPercent:'',currencyCode:'EUR',paymentTermsDays:'30',destinationCountryCode:'DE',destinationRegion:'Berlin',shippingServiceCode:'standard',additionalRequirements:'',configuration:'{}' };
const fields:{key:TextKey;label:string;type?:string;required?:boolean;help?:string}[]=[
  {key:'customerId',label:'Customer ID',required:true},{key:'dealId',label:'Deal ID',required:true},
  {key:'productId',label:'Product ID',required:true},{key:'lineId',label:'Deal line ID',required:true},
  {key:'quantity',label:'Quantity (units)',type:'number',required:true},{key:'requestedDeliveryDate',label:'Requested delivery date',type:'date',required:true},
  {key:'quotedUnitPrice',label:'Proposed unit price (€)',type:'number',required:true},{key:'discountPercent',label:'Proposed discount (%)',type:'number',help:'Optional. The supported fixtures specify no separate discount; entering one makes this request unsupported.'},
  {key:'currencyCode',label:'Currency code',required:true},{key:'paymentTermsDays',label:'Payment terms (days)',type:'number',required:true},
  {key:'destinationCountryCode',label:'Destination country code',required:true},{key:'destinationRegion',label:'Destination region',required:true},
  {key:'shippingServiceCode',label:'Shipping service',required:true},
];
const names:Record<TextKey,string>=Object.fromEntries([...fields.map(f=>[f.key,f.label]),['configuration','Configuration options'],['additionalRequirements','Additional customer requirements']]) as Record<TextKey,string>;
const matchResponse=z.discriminatedUnion('matched',[
  z.object({matched:z.literal(false)}).strict(),
  z.object({matched:z.literal(true),scenario:z.enum(['rc01','uc02']),receipt:z.string().min(1).max(250)}).strict(),
]);

export function ManualIntake() {
  const router=useRouter();
  const [form,setForm]=useState(initial); const [partial,setPartial]=useState(true);
  const [errors,setErrors]=useState<Record<string,string>>({});const [step,setStep]=useState<'enter'|'review'|'unsupported'>('enter');
  const [confirmed,setConfirmed]=useState<DealInputDTO|null>(null); const [busy,setBusy]=useState(false);const [message,setMessage]=useState('');const [token,setToken]=useState('');
  useEffect(()=>{void csrf().then(r=>setToken(r.authenticated?r.csrf:'')).catch(()=>setMessage('Demo session unavailable. Refresh the page before confirming.'));},[]);
  function update(key:TextKey,value:string) { setForm(f=>({...f,[key]:value}));setErrors(e=>({...e,[key]:''})); }
  function validate() {
    const issues:Record<string,string>={};let configuration:Record<string,unknown>={};
    try { const value=JSON.parse(form.configuration);if(!value || typeof value!=='object' || Array.isArray(value)) throw Error();configuration=value; }
    catch { issues.configuration='Enter configuration options as a JSON object, such as {}.'; }
    for(const key of ['quantity','quotedUnitPrice','paymentTermsDays'] as const) if(!form[key].trim()) issues[key]=`${names[key]} is required.`;
    for(const key of ['customerId','dealId','productId','lineId','requestedDeliveryDate'] as const) if(!form[key].trim()) issues[key]=`${names[key]} is required.`;
    const result=DealInput.safeParse({
      ...form,configuration,quantity:form.quantity.trim()?Number(form.quantity):NaN,
      quotedUnitPrice:form.quotedUnitPrice.trim()?Number(form.quotedUnitPrice):NaN,
      paymentTermsDays:form.paymentTermsDays.trim()?Number(form.paymentTermsDays):NaN,
      discountPercent:form.discountPercent.trim()?Number(form.discountPercent):null,
      allowPartialDelivery:partial,catalogVersion:'CATALOGUE_2026_V1',policySetCode:'BASELINE_2026',contractClauseCodes:['standard'],
    });
    if(!result.success) for(const issue of result.error.issues) { const key=String(issue.path[0]);issues[key] ||= issue.message; }
    setErrors(issues);
    return Object.keys(issues).length ? null : result.data!;
  }
  async function confirm() {
    if(!confirmed || !token || busy) return;
    setBusy(true);setMessage('');
    try {
      const result=await json('/api/intake/match',matchResponse,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':token},body:JSON.stringify(confirmed)});
      if(result.matched) router.push(`/scenarios/${result.scenario}?intake=${encodeURIComponent(result.receipt)}`);
      else setStep('unsupported');
    } catch {setMessage('Validation is unavailable or your session expired. No assessment was started. Refresh and try again.'); }
    finally {setBusy(false);}
  }
  return <main id="main-content" className="workspace intake-page"><div className="back"><Link href="/">← Back to homepage</Link> / MANUAL DEAL INTAKE</div><div className="workspace-hero"><div><span className="eyebrow">COMMERCIAL REQUEST · SYNTHETIC DEMO ONLY</span><h1>Start a Deal Assessment</h1><p>Enter and review a single-line deal. This is not an open-ended assessment of new customers; only exact supported synthetic fixture inputs may run the existing workflow.</p></div></div>
    <ol className="intake-steps"><li className={step==='enter'?'active':''}>01 · Enter Deal Details</li><li className={step==='review'?'active':''}>02 · Review &amp; Confirm</li><li className={step==='unsupported'?'active':''}>03 · Validate Supported Assessment</li></ol>
    {step==='enter' && <form className="panel intake-form" noValidate onSubmit={e=>{e.preventDefault();const value=validate();if(value){setConfirmed(value);setMessage('');setStep('review');}}}><span className="eyebrow">STEP 01 / USER-ENTERED INFORMATION</span><h2>Enter Deal Details</h2><p>Use synthetic identifiers only—do not enter real customer information. Specialists retrieve inventory, credit and policy evidence from their pinned source; you do not supply or certify those records.</p><div className="intake-fields">{fields.map(field=><div className="intake-field" key={field.key}><label htmlFor={field.key}>{field.label}{field.required && ' *'}</label><input id={field.key} value={form[field.key]} onChange={e=>update(field.key,e.target.value)} type={field.type||'text'} required={field.required} min={field.type==='number'?'0':undefined} step={field.key==='quantity'||field.key==='paymentTermsDays'?'1':field.type==='number'?'0.01':undefined} aria-invalid={!!errors[field.key]} aria-describedby={errors[field.key]?`${field.key}-error`:undefined}/>{field.help && <small>{field.help}</small>}{errors[field.key] && <small id={`${field.key}-error`} role="alert">{errors[field.key]}</small>}</div>)}</div>
      <div className="intake-fields"><div className="intake-field"><label htmlFor="configuration">Configuration options *</label><textarea id="configuration" value={form.configuration} onChange={e=>update('configuration',e.target.value)} rows={3} aria-invalid={!!errors.configuration}/><small>For a product without selected options, use {'{}'}. Other options must be a JSON object.</small>{errors.configuration && <small role="alert">{errors.configuration}</small>}</div><div className="intake-field"><label htmlFor="additionalRequirements">Additional customer requirements</label><textarea id="additionalRequirements" value={form.additionalRequirements} onChange={e=>update('additionalRequirements',e.target.value)} maxLength={500} rows={3}/><small>Optional; new requirements cannot be assessed by the two pinned demonstrations.</small>{errors.additionalRequirements && <small role="alert">{errors.additionalRequirements}</small>}</div></div>
      <label className="intake-checkbox"><input type="checkbox" checked={partial} onChange={e=>setPartial(e.target.checked)}/> Customer permits partial delivery</label>
      <p className="intake-context"><strong>Demo source context (not user-entered):</strong> baseline 2026 policy, 2026 V1 catalog and standard contract clause. Changing these would require a different assessment and is not supported here. One product line only; no uploaded documents or private credit details.</p>
      <button type="submit" className="run-button">Review Deal Details →</button></form>}
    {step==='review' && confirmed && <section className="panel intake-review"><span className="eyebrow">STEP 02 / NOT YET VERIFIED OR STORED</span><h2>Review &amp; Confirm</h2><p>This is the commercial request you entered—not information verified by Deal Desk. Confirming compares it to a supported fixture; it does not persist a new deal or grant approval.</p><dl className="intake-record">{fields.map(field=><div key={field.key}><dt>{field.label}</dt><dd>{form[field.key] || 'Not specified'}</dd></div>)}<div><dt>Configuration options</dt><dd>{form.configuration}</dd></div><div><dt>Partial delivery permitted</dt><dd>{partial?'Yes':'No'}</dd></div><div><dt>Additional requirements</dt><dd>{form.additionalRequirements || 'None entered'}</dd></div><div><dt>Fixed demo context</dt><dd>BASELINE_2026 · CATALOGUE_2026_V1 · standard clause</dd></div></dl><div className="intake-actions"><button type="button" onClick={()=>{setStep('enter');setConfirmed(null);}}>← Edit entries</button><button type="button" className="run-button" disabled={!token||busy} onClick={()=>void confirm()}>{busy?'Checking supported fixture…':'Confirm & Check Support →'}</button></div>{message && <p role="alert" className="error">{message}</p>}</section>}
    {step==='unsupported' && <section className="panel intake-review" role="status"><span className="eyebrow">STEP 03 / NO ASSESSMENT STARTED</span><h2>Deal input not supported</h2><p>This deal cannot currently be assessed in this demonstration. Your entry was <strong>not recorded or persisted</strong>, and no scripted assessment was launched. A changed price, discount, configuration, customer requirement, date or other assessment input cannot be substituted with fixture data.</p><div className="intake-actions"><button type="button" onClick={()=>setStep('review')}>← Review entries</button><button type="button" onClick={()=>{setStep('enter');setConfirmed(null);}}>Edit entries</button><Link href="/#scenarios">Explore supported scenarios</Link></div></section>}
  </main>;
}
