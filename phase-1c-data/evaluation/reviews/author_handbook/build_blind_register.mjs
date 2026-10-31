import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const base=new URL('./outputs/',import.meta.url).pathname;
const data=JSON.parse(await fs.readFile(`${base}/blind_register_seed.json`,'utf8'));
const wb=Workbook.create(), help=wb.worksheets.add('Read First'), cases=wb.worksheets.add('Initial Case Decisions'), findings=wb.worksheets.add('Initial Six Findings'), supp=wb.worksheets.add('Supplemental Separate');
for(const s of [help,cases,findings,supp])s.showGridLines=false;
help.getRange('A1:B12').values=[
 ['BLINDED FIRST PASS','No model recommendations or proposed gates in this workbook'],
 ['Source commit',data.commit],
 ['Sequence','Read Blinded Source-First Handbook; decide; freeze; only then open technical reference'],
 ['Original cohort','36 cases 001–036; one row per case, six detailed findings per case'],
 ['Supplemental cohort','039, 040, 041 on a separate sheet; not included in 36'],
 ['Decision','Write your own finding and gate, cited rule/pointer, uncertainty and action'],
 ['Status','Initial status is your own draft; it is not formal answer acceptance'],
 ['Batches','Freeze a complete subset with the command in the methodology note'],
 ['Freeze','Export a canonical JSON snapshot and SHA-256 before opening technical material'],
 ['Yellow cells','Editable author decisions; all blank at delivery'],
 ['Identity and time','Use your name and timezone-aware ISO timestamp'],
 ['AI disclosure','State source compilation assistance; no prior recommendations viewed'],
];
const ch=['Case ID','Packet SHA-256','Provider SHA-256','Credit scope SHA-256','Quote EUR (source arithmetic)','Configuration finding','Pricing finding','Availability finding','Credit finding','Policy finding','Approval finding','Overall gate','Original-deal actions','Alternative / customer acceptance','Evidence pointer(s)','Rule IDs and calculations','Uncertainty / abstention','Rationale','Author identity','Initial decision timestamp ISO','AI-assistance disclosure','Initial status (draft/unresolved)'];
cases.getRangeByIndexes(0,0,1,ch.length).values=[ch];
cases.getRangeByIndexes(1,0,36,ch.length).values=data.cases.map(c=>[c.case_id,c.packet_sha,c.provider_sha,c.scope_sha,Number(c.quote),...Array(17).fill('')]);
cases.getRange('A1:V1').format.fill='#16364E';cases.getRange('A1:V1').format.font.color='#FFFFFF';cases.getRange('A1:V1').format.font.bold=true;
cases.getRange('A:A').format.columnWidth=22;cases.getRange('B:D').format.columnWidth=20;cases.getRange('E:E').format.columnWidth=18;cases.getRange('F:V').format.columnWidth=29;
cases.getRange('F2:V37').format.fill='#FFF3D6';cases.getRange('A1:V37').format.rowHeight=28;cases.getRange('E2:E37').setNumberFormat('#,##0.00');cases.freezePanes.freezeRows(1);
cases.getRange('L2:L37').dataValidation={rule:{type:'list',values:['blocked','needs_revision','needs_evidence','needs_commitment','approval_required','unresolved']}};
cases.getRange('V2:V37').dataValidation={rule:{type:'list',values:['Draft','Unresolved']}};
cases.tables.add('A1:V37',true,'BlindOriginalCases');
const fh=['Case ID','Responsibility','Initial finding code','Initial finding narrative','Source pointer(s)','Rule / calculation','Action or blocker','Uncertainty or abstention','Counterargument','Author identity','Decision timestamp ISO','AI-assistance disclosure'];
findings.getRangeByIndexes(0,0,1,fh.length).values=[fh];
const fr=[];for(const c of data.cases)for(const resp of data.responsibilities)fr.push([c.case_id,resp,...Array(10).fill('')]);
findings.getRangeByIndexes(1,0,216,fh.length).values=fr;
findings.getRange('A1:L1').format.fill='#16364E';findings.getRange('A1:L1').format.font.color='#FFFFFF';findings.getRange('A1:L1').format.font.bold=true;
findings.getRange('A:B').format.columnWidth=22;findings.getRange('C:L').format.columnWidth=31;findings.getRange('C2:L217').format.fill='#FFF3D6';findings.getRange('A1:L217').format.rowHeight=28;findings.freezePanes.freezeRows(1);
findings.getRange('C2:C217').dataValidation={rule:{type:'list',values:['no_issue_identified','needs_evidence','needs_commitment','needs_revision','blocked','human_review_required','requires_adjudication','abstain','other']}};
findings.tables.add('A1:L217',true,'BlindSixFindings');
supp.getRange('A1:F4').values=[['Case ID','Cohort','Source extension','Initial findings','Overall gate','Author notes'],['EVAL-PREP-039','Configuration supplement','configuration-extension/v1','','',''],['EVAL-PREP-040','Credit nonempty control','credit-evidence-v3/control_cases_v1','','',''],['EVAL-PREP-041','Credit incomplete control','credit-evidence-v3/control_cases_v1','','','']];
supp.getRange('A1:F1').format.fill='#16364E';supp.getRange('A1:F1').format.font.color='#FFFFFF';supp.getRange('A1:F1').format.font.bold=true;supp.getRange('A:F').format.columnWidth=30;supp.getRange('D2:F4').format.fill='#FFF3D6';
help.getRange('A1:B1').format.fill='#16364E';help.getRange('A1:B1').format.font.color='#FFFFFF';help.getRange('A1:B1').format.font.bold=true;help.getRange('A:A').format.columnWidth=25;help.getRange('B:B').format.columnWidth=95;help.getRange('A2:A12').format.font.bold=true;help.getRange('A1:B12').format.rowHeight=28;
await wb.recalculate();const out=await SpreadsheetFile.exportXlsx(wb);await out.save(`${base}/Blinded_Initial_Decision_Register.xlsx`);console.log('Blinded register: 36 case rows, 216 specialist rows, 3 separate supplements');
