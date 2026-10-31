import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const base = new URL('./outputs/', import.meta.url).pathname;
const data = JSON.parse(await fs.readFile(`${base}/register_seed.json`, 'utf8'));
const wb = Workbook.create();
const summary = wb.worksheets.add('Instructions');
const cases = wb.worksheets.add('Case Decisions');
const findings = wb.worksheets.add('Six Findings');
for (const sh of [summary,cases,findings]) sh.showGridLines = false;

summary.getRange('A1:B13').values = [
  ['AUTHOR ADJUDICATION · ORIGINAL 36','PENDING — 0/36 accepted'],
  ['Source commit',data.commit],
  ['Scope','Original cases 001–036 only; supplements 039–041 excluded'],
  ['Evidence','Read each case dossier and its hash-bound packet before deciding'],
  ['Yellow cells','Author inputs; blank means no decision'],
  ['Six Findings','One row per case and specialist; enter status, corrected wording, evidence and rationale'],
  ['Case Decisions','One case-level row; enter six dispositions and overall decision'],
  ['Allowed disposition','Accept / Correct / Reject / Unresolved'],
  ['No automatic acceptance','AI proposals and source checks are not author decisions'],
  ['Timestamp','Enter an ISO date-time with timezone, e.g. 2026-10-31T14:00:00+02:00'],
  ['Disclosure','Describe AI assistance and any source-first check done personally'],
  ['Release','Keep ready_for_generation=false and draft PR until all release gates pass'],
  ['Method limitation','Author adjudication is not independent human expert validation'],
];
summary.getRange('A1:B1').format.fill = '#15324D';
summary.getRange('A1:B1').format.font.color = '#FFFFFF';
summary.getRange('A1:B1').format.font.bold = true;
summary.getRange('A:A').format.columnWidth = 27;
summary.getRange('B:B').format.columnWidth = 100;
summary.getRange('A2:A13').format.font.bold = true;
summary.getRange('A1:B13').format.rowHeight = 26;

const caseHeaders=['Case ID','Scenario','Priority','Packet SHA-256','Provider SHA-256','Credit scope SHA-256','Quote EUR','Provisional gate (AI)','Decision: Configuration','Decision: Pricing','Decision: Availability','Decision: Credit','Decision: Policy','Decision: Approval','Decision: overall gate','Final overall gate / action','Case status','Author identity','Decision timestamp ISO 8601','Rationale and cross-specialist reasoning','Evidence references','Uncertainty / required further evidence','AI-assistance disclosure','Corrections / alternative proposal','Author sign-off'];
cases.getRangeByIndexes(0,0,1,caseHeaders.length).values=[caseHeaders];
const caseRows=data.cases.map(c=>[c.case_id,c.archetype,c.priority,c.packet_sha,c.provider_sha,c.scope_sha,Number(c.quote),c.proposed_gate,...Array(17).fill('')]);
cases.getRangeByIndexes(1,0,caseRows.length,caseHeaders.length).values=caseRows;
cases.getRange('A1:Y1').format.fill='#15324D';cases.getRange('A1:Y1').format.font.color='#FFFFFF';cases.getRange('A1:Y1').format.font.bold=true;
cases.getRange('A:A').format.columnWidth=21;cases.getRange('B:B').format.columnWidth=23;cases.getRange('C:C').format.columnWidth=12;
cases.getRange('D:F').format.columnWidth=20;cases.getRange('G:H').format.columnWidth=22;cases.getRange('I:O').format.columnWidth=21;
cases.getRange('P:Y').format.columnWidth=30;cases.getRange('I2:Y37').format.fill='#FFF2CE';
cases.getRange('G2:G37').setNumberFormat('#,##0.00');cases.getRange('A1:Y37').format.rowHeight=28;
cases.freezePanes.freezeRows(1);
for(const col of ['I','J','K','L','M','N','O','Q']) cases.getRange(`${col}2:${col}37`).dataValidation={rule:{type:'list',values:col==='O'?['blocked','needs_revision','needs_evidence','needs_commitment','approval_required','unresolved']:['Accept','Correct','Reject','Unresolved']}};
cases.tables.add('A1:Y37',true,'OriginalCaseDecisions');

const findingHeaders=['Case ID','Responsibility','AI recommendation — pending','Author disposition','Final finding / corrected wording','Required action / blocker','Evidence pointer(s)','Rule ID / calculation checked','Uncertainty / abstention','Rationale / counterargument','Author identity','Decision timestamp ISO 8601','AI-assistance disclosure','Packet SHA-256'];
findings.getRangeByIndexes(0,0,1,findingHeaders.length).values=[findingHeaders];
const findingRows=[];
for(const c of data.cases) for(const responsibility of data.responsibilities) findingRows.push([c.case_id,responsibility,c.recommendations[responsibility],...Array(10).fill(''),c.packet_sha]);
findings.getRangeByIndexes(1,0,findingRows.length,findingHeaders.length).values=findingRows;
findings.getRange('A1:N1').format.fill='#15324D';findings.getRange('A1:N1').format.font.color='#FFFFFF';findings.getRange('A1:N1').format.font.bold=true;
findings.getRange('A:B').format.columnWidth=21;findings.getRange('C:C').format.columnWidth=26;findings.getRange('D:M').format.columnWidth=31;findings.getRange('N:N').format.columnWidth=21;
findings.getRange('D2:M217').format.fill='#FFF2CE';findings.getRange('A1:N217').format.rowHeight=27;
findings.getRange('D2:D217').dataValidation={rule:{type:'list',values:['Accept','Correct','Reject','Unresolved']}};
findings.freezePanes.freezeRows(1);
findings.tables.add('A1:N217',true,'SixResponsibilityDecisions');

await wb.recalculate();
const inspection=await wb.inspect({kind:'sheet',include:'id,name',maxChars:1000});
console.log(JSON.stringify(inspection).slice(0,1000));
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(`${base}/Author_Adjudication_Decision_Register.xlsx`);
console.log('Exported original cases',caseRows.length,'specialist rows',findingRows.length);
