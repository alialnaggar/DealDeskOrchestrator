# Version-2 model review record — provisional, 14 October 2026

## Approval and source pin

Ali approved evaluation-contract decisions F1, C1/C2, G1, S1 and R1 on 14 October 2026 at 19:04:52 UTC with “approve contnue”. Approval covers the versioned input conventions, ten offer-cost corrections and renewed source-based model review. It does not accept answers, freeze calibration or change the schema.

- Source/export commit: `6902d3879842fe77f476a2f0823ffb0956cdec4e`.
- Verified producing [push run 38623137916](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38623137916); [PR run 38623147899](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38623147899) also passed.
- Input artifact: `phase1c-provisional-evaluation-inputs`, ID `11922344930`, archive digest `sha256:c2911f8e157bc03fe0b48dbd20c66e14135e45437157407e25485df0e5057623`.
- Version-2 definition SHA-256: `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`.
- Business-contract canonical SHA-256: `6e6990f014e061acd61039bdc128af753fc0116d4c1e7d60dafcdfb2108f7971`.
- Index exact-byte SHA-256: `d67a146c2d73265f622d8928f93338b7e66f054f7a01e235ad8ad99470157c46`.
- Canonical parsed index SHA-256: `7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc`.
- Source-audit report SHA-256 from fresh CI: `0063379e1ec17412b4f27e6e0b0006d2ba6152a19be43e16d44b3b47e30fef96`.

The primary agent compared the downloaded artifact index to the tracked GitHub pin and verified all 36 payload hashes and 36 provider exact-byte hashes before handing sources to the reviewer. Both workflows reproduce the original v1 inputs separately and validate its unchanged first-pass draft against that version. V1 and v2 are versions of the same 36 cases, not independent new cohorts or 72 samples.

## Version change and methodological boundary

V2 declares the approved fictional evidence-age, costing, gate, service and routing conventions within each system-visible packet. Its ten supplier offer prices match declared same-product standard costs. Master costs/prices, quotes, provider records, historical/pilot/100-case sources and calibration thresholds are unchanged. Contract/exporter/generator hashes change the per-run configuration fingerprint. Source rows/rule arrays are normalized by canonical JSON for v2 hashing; no selected facts are added or removed.

An initial replay identified incidental BOM row-order variation after archived-source loading. Exact equality failed, diagnostic packets were preserved, and a row-permutation test plus v2-only normalization resolved the cause. The current fresh PostgreSQL runs pass; v1 export ordering and original evidence pointers remain intact. No assertion was weakened to tolerate mismatches.

The second pass is a post-clarification review: business conventions were drafted after inspecting ambiguities in the first model pass and current implementation, then explicitly approved by Ali. This influence on dataset design is disclosed, rather than treating implementation agreement as independent correctness. No baseline agreement or agent accuracy is reported. All source packets remain fictional; no external supplier/provider verification or real-world service-level claim follows.

## Review visibility and protocol

A new model agent was initiated without parent conversation history, distinct from the first reviewer context. Only the verified v2 packet index, 36 packets, 36 provider files, blank bound review template and format validator were supplied. The approved business contract is embedded in the facts. The reviewer was instructed not to consult v1 drafts, authoring intent, source generator, reader/decision implementation, tests, diagnostic outcomes, web/GitHub or other workspace files, and not to delegate further.

This is an instruction-only boundary, not an OS access-control sandbox. The inherited session model configuration does not establish a different family/provider; exact backend identity and sampling were not independently controlled or verified. Saved hashes identify the actual outputs; identical future model wording is not guaranteed. All six responsibilities require case-specific reasoning, arithmetic, resolvable references, human actions and disclosed uncertainties. The controlled source snapshots are complete within their fictional scope; empty AR/payments mean no such history, not a favorable payment record. Separate provider evidence is a simulated channel, never a real confirmation.

The exact supplied reviewer instruction is preserved below. Structural checks establish completeness and source binding, not correctness, reviewer authentication or expert independence. The primary author must record any later observations separately and must not silently amend the delivered draft to match system outcomes.

## Acceptance boundary

**0/36 independently accepted answers.** Model drafting and source binding do not accept labels. The six field marks, two calibration reviews and `ready_for_generation=false` remain. These reviewer files stay outside system-visible input artifacts and any future system prompt/tools. Human verification must record who accepted each case, when, against which source/contract version, and why before scoring.

## Saved outputs and source-only self-check

- `model_review_v2_draft.json`: SHA-256 `9cdffe708cf4fab3ddc022132e60a4aaf2c1f036cc832c01691673203657bc72`.
- `model_review_v2_assembly.py.txt`: SHA-256 `f7b72632fe82763874f884a32fe6bcc9cf15487c0240fda59ea49fda25efbd93`.
- `model_review_v2_selfcheck.py.txt`: SHA-256 `e5e2f36d4be104f5cf1fcc0238dc72b9f055d8e02e15b8939dc074d6fb46fd6d`.
- `model_review_v2_selfcheck.patch`: SHA-256 `53954e5730cdcdf66395f8bc434300662849a60758e974c72d46ce4784f205fe`.
- Original first assembly: SHA-256 `f1327f8b69dc2380601ac534c4299ce68c9dd7a057acac7ce8aa62cf4ff44514`.

All 36 cases are structurally complete (216 responsibility findings), with zero errors and zero accepted answers in reviewer and primary format checks. Proposed draft gates are 8 approval_required, 6 needs_revision, 8 needs_evidence, 10 needs_commitment and 4 blocked. This distribution is not an expected answer key or accuracy measurement.

The retained assembly helper and self-check helper are audit text outside the runtime, not maintained oracle generators. The first-to-final patch records the source-only amendments (including refreshed timestamps); reversing it against the final JSON reconstructs the original assembly byte-for-byte. Temporary paths/checkpoints mentioned in the verbatim notes are not separately committed. Numeric work is retained in the arithmetic appendix below. No primary feedback was supplied before final drafting.

## Primary author's post-delivery observations — no accepted corrections

The primary agent independently reran source-bound format validation (36 complete, zero errors, zero accepted answers), confirmed all source/provider bindings and spot-checked Decimal arithmetic for credit and margin cases. Cases031/032 exposure is EUR4,818.80/EUR8,495.20 against EUR1,000; cases033/034 gross margin is 0.9898622800%, about 7.01014 points below the 8% floor and outside the explicit two-point exception. These checks validate only the stated arithmetic, not every proposed conclusion or source attribution.

The renewed model explicitly identifies 51/52-hour capacity observations in017/018 as insufficient under the approved 24-hour rule. It also distinguishes scheduled-service ineligibility from a booked slot, uses the declared quote-cost basis and preserves the boundary against approval/reservation/delivery promises. These are source-grounded observations, not a claim of overall accuracy.

Two substantive issues remain for adjudication:

| Cases | Source/review issue | Verification needed before acceptance |
| --- | --- | --- |
| 019–020 | The draft assigns needs_revision to a currently confirmed October sourcing route, but retains earlier active procurement offers and possible September production. The submitted deal does not explicitly choose a particular PO/route. No post-October-receipt capacity is supplied. | Decide which feasible alternative controls the submitted-deal gate under G1, distinguishing a missing commitment from a required quantity/date/region change. Do not infer that every route is impossible or force the answer to match the author's archetype or the deterministic implementation. Verify full operation/dispatch dates and whether the scenario actually isolates a horizon conflict. |
| 031–034 | The model correctly retains hard blocks, but its Approval prose lists Regional_Manager/Sales_Director as applicable routes with instructions to resolve the block first. | Clarify that any such role is hypothetical for a later valid proposal or a review of corrective action; it must not be presented as a currently executable approval route that can waive the hard cap. Check exact responsibility attribution and human actions. |

The model's scrap and conservative separate-day scheduling assumptions are also disclosed in its notes. Upward integer storage rounding (4.04/8.08 to5/9) still fits these stock rows, but exact intraday completion is not established. Shared five-SKU context, limited variation, author-known archetypes and model-family uncertainty continue to limit evidence claims.

No primary observation changes the saved model draft, input pin, gate count or independent acceptance count. Cases with no unresolved question in the model file are still unaccepted; an empty question list is not proof of correctness. The next gate is substantive case-level verification, beginning with route selection and hard-block routing, followed by recorded human acceptance before scoring. Six field marks and two calibration reviews remain separately open.

## Review table — model proposals only, not accepted answers

| Case | Proposed gate | First proposed human action | Unresolved questions |
| --- | --- | --- | ---: |
| EVAL-PREP-001 | approval_required | Warehouse and Sales must confirm allocation and dispatch through the human order process after required review. | 0 |
| EVAL-PREP-002 | approval_required | Warehouse and Sales must confirm allocation and dispatch through the human order process after required review. | 0 |
| EVAL-PREP-003 | needs_revision | Sales and supply owner must propose a revised quantity/date or obtain a new supported supply source, then obtain customer acceptance. | 1 |
| EVAL-PREP-004 | needs_revision | Sales and supply owner must propose a revised quantity/date or obtain a new supported supply source, then obtain customer acceptance. | 1 |
| EVAL-PREP-005 | needs_evidence | Inventory owner must refresh SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001 at WH-EU-CENTRAL and recheck net stock plus dispatch. | 1 |
| EVAL-PREP-006 | needs_evidence | Inventory owner must refresh SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001 at WH-EU-CENTRAL and recheck net stock plus dispatch. | 1 |
| EVAL-PREP-007 | approval_required | Supply owner must track confirmed EVAL36-007-PO, verify receipt and allocate the requested 2 units through the order process. | 0 |
| EVAL-PREP-008 | approval_required | Supply owner must track confirmed EVAL36-008-PO, verify receipt and allocate the requested 4 units through the order process. | 0 |
| EVAL-PREP-009 | needs_commitment | Procurement must obtain a new binding supplier/PO confirmation for 2 units, arrival and warehouse dispatch; do not reuse a cancelled receipt. | 1 |
| EVAL-PREP-010 | needs_commitment | Procurement must obtain a new binding supplier/PO confirmation for 4 units, arrival and warehouse dispatch; do not reuse a cancelled receipt. | 1 |
| EVAL-PREP-011 | needs_commitment | Procurement must obtain a new binding supplier/PO confirmation for 2 units, arrival and warehouse dispatch; do not reuse a cancelled receipt. | 1 |
| EVAL-PREP-012 | needs_commitment | Procurement must obtain a new binding supplier/PO confirmation for 4 units, arrival and warehouse dispatch; do not reuse a cancelled receipt. | 1 |
| EVAL-PREP-013 | needs_commitment | Workshop must commit 1.5 hours each for sequenced assembly/test after component availability and warehouse must confirm dispatch; confirm alternate network selection where used. | 1 |
| EVAL-PREP-014 | needs_commitment | Workshop must commit 2.5 hours each for sequenced assembly/test after component availability and warehouse must confirm dispatch; confirm alternate network selection where used. | 1 |
| EVAL-PREP-015 | needs_commitment | Workshop must commit 1.5 hours each for sequenced assembly/test after component availability and warehouse must confirm dispatch; confirm alternate network selection where used. | 1 |
| EVAL-PREP-016 | needs_commitment | Workshop must commit 2.5 hours each for sequenced assembly/test after component availability and warehouse must confirm dispatch; confirm alternate network selection where used. | 1 |
| EVAL-PREP-017 | needs_evidence | Workshop must refresh all required dated assembly/test capacity and then verify operation sequence and lane timing. | 1 |
| EVAL-PREP-018 | needs_evidence | Workshop must refresh all required dated assembly/test capacity and then verify operation sequence and lane timing. | 1 |
| EVAL-PREP-019 | needs_revision | Sales Director and customer must review any later physical date proposal; requested date requires revision on the confirmed route. | 3 |
| EVAL-PREP-020 | needs_revision | Sales Director and customer must review any later physical date proposal; requested date requires revision on the confirmed route. | 3 |
| EVAL-PREP-021 | approval_required | Activation owner and Regional Manager must review the supported simulated term and execute the human activation process; no allocation or activation promise is made. | 0 |
| EVAL-PREP-022 | approval_required | Activation owner and Regional Manager must review the supported simulated term and execute the human activation process; no allocation or activation promise is made. | 0 |
| EVAL-PREP-023 | needs_evidence | Provider evidence owner must supply matching current simulated proof for identity, net units, binding dates, validity and entire anniversary term. | 1 |
| EVAL-PREP-024 | needs_evidence | Provider evidence owner must supply matching current simulated proof for identity, net units, binding dates, validity and entire anniversary term. | 1 |
| EVAL-PREP-025 | needs_evidence | Provider evidence owner must obtain full-term coverage through 2027-09-03, or Sales must submit an explicitly changed term; current proof is insufficient. | 1 |
| EVAL-PREP-026 | needs_evidence | Provider evidence owner must obtain full-term coverage through 2027-09-04, or Sales must submit an explicitly changed term; current proof is insufficient. | 1 |
| EVAL-PREP-027 | needs_commitment | Service scheduling owner must confirm staffing and book 2 packages in DE-NW for the customer-accepted date. | 1 |
| EVAL-PREP-028 | needs_commitment | Service scheduling owner must confirm staffing and book 4 packages in DE-NW for the customer-accepted date. | 1 |
| EVAL-PREP-029 | needs_revision | Sales and service owner must propose a covered destination or different supported service and obtain customer acceptance before rerun. | 1 |
| EVAL-PREP-030 | needs_revision | Sales and service owner must propose a covered destination or different supported service and obtain customer acceptance before rerun. | 1 |
| EVAL-PREP-031 | blocked | Finance and Sales must reduce exposure or establish a revised authorized limit and submit a new compliant review; no approval of current exposure. | 0 |
| EVAL-PREP-032 | blocked | Finance and Sales must reduce exposure or establish a revised authorized limit and submit a new compliant review; no approval of current exposure. | 0 |
| EVAL-PREP-033 | blocked | Sales must submit a compliant price and rerun margin/policy review; do not route the prohibited price as approvable. | 0 |
| EVAL-PREP-034 | blocked | Sales must submit a compliant price and rerun margin/policy review; do not route the prohibited price as approvable. | 0 |
| EVAL-PREP-035 | approval_required | Warehouse and Sales must confirm allocation and dispatch through the human order process after required review. | 0 |
| EVAL-PREP-036 | approval_required | Warehouse and Sales must confirm allocation and dispatch through the human order process after required review. | 0 |

## Reviewer self-check corrections (verbatim JSON)

```json
[
  {
    "case_id": "EVAL-PREP-019",
    "fields": [
      "findings.Availability.rationale",
      "overall.rationale",
      "overall.unresolved_questions"
    ],
    "correction": "Added exact earlier-offer receipt/operation/transit dates; clarified revision gate attaches to currently confirmed route and retained alternative ambiguity. Case 020 latest separate-day test lacks supplied Sep 10 capacity. No gate was changed."
  },
  {
    "case_id": "EVAL-PREP-020",
    "fields": [
      "findings.Availability.rationale",
      "overall.rationale",
      "overall.unresolved_questions"
    ],
    "correction": "Added exact earlier-offer receipt/operation/transit dates; clarified revision gate attaches to currently confirmed route and retained alternative ambiguity. Case 020 latest separate-day test lacks supplied Sep 10 capacity. No gate was changed."
  },
  {
    "case_id": "EVAL-PREP-033",
    "fields": [
      "findings.Pricing.rationale"
    ],
    "correction": "Replaced generic hard margin/discount wording with the actual margin-shortfall prohibition; explicitly distinguished discount escalation from hard cap. No calculation or gate changed."
  },
  {
    "case_id": "EVAL-PREP-034",
    "fields": [
      "findings.Pricing.rationale"
    ],
    "correction": "Replaced generic hard margin/discount wording with the actual margin-shortfall prohibition; explicitly distinguished discount escalation from hard cap. No calculation or gate changed."
  },
  {
    "case_id": "EVAL-PREP-031",
    "fields": [
      "findings.Credit.rationale"
    ],
    "correction": "Added exact excess arithmetic and EUR1150 exposure exception ceiling; no finding or gate changed."
  },
  {
    "case_id": "EVAL-PREP-032",
    "fields": [
      "findings.Credit.rationale"
    ],
    "correction": "Added exact excess arithmetic and EUR1150 exposure exception ceiling; no finding or gate changed."
  }
]

```

## Reviewer notes (verbatim)

# Version 2 source-only model review notes

This is a model draft review of 36 synthetic cases, with six responsibility findings per case (216 total). It is not human verification, an accepted answer key, or established cross-model independence. All cases are `draft_complete`, reviewer method is `model`, and `independently_reviewed_answers=0`, `answer_key_agent_visible=false`, and `review_workspace_not_released_answers` remain unchanged. Confidence and format/hash success establish no acceptance.

## Method and consulted inputs

I am OpenAI Codex reviewer agent `/root/v2_source_reviewer`, newly initiated without primary conversation history, using the inherited same-session model configuration. I have not independently verified a different model family. I followed an instruction visibility boundary, not an OS-enforced sandbox.

Authorized source files consulted were exactly `/tmp/dealdesk_v2_review_inputs/packet_index.json`, `review_template.json`, `review_format.py`, all 36 `EVAL-PREP-001.json` through `EVAL-PREP-036.json`, and all 36 corresponding `EVAL-PREP-NNN-provider.json` files. Each packet was parsed in full, with facts, business contract and raw rules inspected through direct reads and compact source summaries. Identical raw rule sets across all packets were checked programmatically, not inferred from case numbers. The filenames are identifiers, not archetype labels or decision templates. My own assembly and output drafts were consulted for source-only self-check.

Before substantive review, I verified each canonical packet payload SHA-256 against the index and wrapper digest, and each separate provider file exact-byte SHA-256 against the index. All 72 checks passed. After assembly/self-check I repeated all 72 checks, plus supplied-format validation against the pinned input directory. The validation report records 36 complete cases, 216 findings, zero errors and zero independently reviewed answers. Pointers resolve to actual packet facts or provider records. Hashes and pointer checks establish source identity and structural completeness, not answer correctness.

I did not consult prior reviews, authoring maps, generators, reader/decision implementations, expected outcomes, test/diagnostic outcomes, GitHub/web, or tools' private history. I did not call the system under evaluation, spawn/delegate, obtain primary author observations, approve a deal, reserve capacity/supply or promise delivery. Progress messages supplied counts and process disclosures only; no expectations were requested.

`assemble_drafts.py` is my arithmetic and narrative assembly helper, not an oracle, expected-answer generator or system implementation. `arithmetic_ledger.json` retains per-case decimal computations. `source_only_selfcheck.py` records the substantive source-only clarifications and completion checks. Scripts have been adjusted to disable further bytecode writes.

## Arithmetic and source observations

Each packet has a single submitted line. Revenue is quoted unit price × full submitted quantity; quote cost is versioned submitted catalogue standard_cost × quantity. Thus line and deal discount/margin coincide for these cases. The approved cost basis is tax-exclusive EUR, with no added freight/tax. Workstation standard cost is the approved loaded EUR715.00. Null cost_parameters permits no independent labour/overhead reconstruction or reconciled BOM rollup. Supplier offer costs support procurement, not a replacement quote-margin cost basis.

Digital instance_month quantity is the entire commercial quantity: 2×12=24 or 4×12=48. Pool demand is only 2 or 4 concurrent instances. Coverage must extend from activation to its 12-month anniversary: Sep3,2026–Sep3,2027 or Sep4,2026–Sep4,2027. Matching controlled manifests ending Sep6,2027 satisfy this; manifests ending Dec31,2026 do not. valid_until Sep10,2027 does not replace coverage end. Empty provider collections do not verify a local binding flag. These manifests are simulated evidence, not real-provider/live-service verification.

Credit exposure includes full submitted revenue, all unbilled commitments and snapshot AR. Empty receivable/payment collections mean no AR or payments within this complete snapshot, not a favorable payment history. Cases031/032 yield exposure EUR4818.80/EUR8495.20 against EUR1000.00: excess 381.88%/749.52%, beyond the 15% cap (EUR1150 exposure ceiling). Cases033/034 have price EUR1672.96 and cost EUR1656.40: unit profit EUR16.56, margin 16.56/1672.96×100 = 0.989862%, 7.010138 points below the 8% floor. Their 17.180198% discount routes to Sales Director, but the actual prohibition is margin shortfall, not the >35% discount cap. Ordinary escalation cannot waive either hard cap. Legal review is additional only for the explicitly declared legal_review clause.

Inventory is net of allocations. Future/missing/older-than-24-hour observations cannot establish current supply/capacity. Stale stock and production observations are missing current evidence, not proof of perpetual impossibility. Cancelled inbound quantities do not count as binding supply, while valid active matching offers remain conditional procurement alternatives.

For workstation quantity2/4, declared proportional storage scrap gives 2×2×1.01=4.04 / 4×2×1.01=8.08 storage units. Assembly and test each require quantity×0.5 + ceil(quantity/4)×0.5 =1.5 /2.5 hours. Network group rows are substitutes ranked 0/1, not additive network requirements. Confirmed alternate-network inbound can support the same BOM group despite fully allocated primary network stock. Supplied production capacity has daily resolution. I used conservative separate-day assembly/test schedules to demonstrate feasibility without inventing intraday timing. Those illustrative schedules are not reservations.

The October compute receipts in019/020 are later than requested delivery; component arrival is not finished-product delivery. Capacity ends Sep9, so there is no supplied production evidence after the October receipt. No exact October completion or delivery is asserted. Earlier matching offers are retained separately: case019 max lead allows Sep8 assembly/Sep9 test and conditional Sep10 arrival; case020 modal receipt permits Sep7 assembly/Sep8 test and conditional Sep10 arrival, but max Sep9 receipt would require a Sep10 test slot under the conservative schedule, outside the supplied capacity horizon. Supply, workshop and shipping humans must commit the complete replacement route.

For scheduled services, the approved contract applies regional eligibility even when installation_requested=false. Eligible coverage establishes no booked slot. Ineligible scope requires a changed service or destination proposal, with booking still outstanding afterward. The approved explicit service interpretation governs the raw compatibility rule's blocker severity.

## Limitations and remaining ambiguity

All findings use the fictional declared business conventions; no unstated vendor, market or legal facts were imported. Calendar calculations use declared Monday-Friday calendars and empty supplier holiday lists, with origin time zones and listed shipping cutoff. Physical dates are indicative because receipt time, intraday operation completion and dispatch acceptance are not supplied. Production/activation/service humans must confirm execution.

The approved gates call a feasible conditional alternative needs_commitment. I apply that to valid uncommitted supplier offers, feasible unbooked workstation production, and eligible unbooked services. This is an interpretation requiring subsequent substantive independent review; the validator does not adjudicate it.

For019/020, the draft needs_revision gate is attached to the currently confirmed late October sourcing route, with subordinate needs_evidence for post-receipt capacity and needs_commitment for possible earlier replacement procurement retained. Whether a newly committed replacement sourcing proposal should supersede that route and receive another gate remains explicitly unresolved. The model does not claim all alternative routes impossible. At least Sales Director reviews a changed late physical date proposal; no additional Finance or Legal roles are invented without their own triggers.

Scrap quantities are evaluated proportionally because no integer-rounding convention is supplied. Rounding these demands upward to5/9 still fits the listed stock and does not change the reviewed supply finding. Separate-day operations are conservative demonstrations, not assertions that the business prohibits same-day ordered operations. Exact earliest same-day completion would require unavailable intraday evidence.

## Retained assembly and correction disclosures

The first complete draft is retained as `model_review_v2_draft_first_assembly.json`; its original assembly helper is retained as `assemble_drafts_first_assembly.py`. No first assembly was silently overwritten or deleted. Source-only self-check clarifications, before any primary author observations, are in `selfcheck_corrections.json`:019/020 add exact replacement-offer schedules and route/gate ambiguity;033/034 identify the specific margin-shortfall prohibition and distinguish ordinary discount routing;031/032 add exact excess/15%-ceiling arithmetic. No finding classifications or overall gates were changed. Reviewer timestamps were refreshed across all cases at final assembly. The final report includes hashes of both assembled draft versions.

One unsuccessful pre-assembly script run raised a local NameError because a make-to-order-only variable appeared before its mode guard. It produced no complete draft. I reordered the condition, reran assembly, and then validated the complete result.

Boundary deviation: importing the explicitly allowed `review_format.py` with Python's default import behavior incidentally created `/tmp/dealdesk_v2_review_inputs/__pycache__`. This is a write outside the instruction's output-only directory, so strict write-boundary compliance cannot be claimed. No pinned source JSON or format source was modified. I disclosed this to the primary agent and changed current helpers to disable bytecode writes; I left cleanup to the primary agent rather than perform another mutation in the input directory. The allowed input boundary remained an instruction restriction, never verified enforced isolation.

No independently reviewed answer is released by these drafts. Remaining substantive acceptance must be performed and recorded outside this model drafting step.

## Reviewer arithmetic ledger (draft computations, verbatim)

```json
[
  {
    "case_id": "EVAL-PREP-001",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "approval_required",
    "exposure_eur": "4043.80",
    "gross_profit_eur": "606.00",
    "list_total_eur": "4040.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "3918.80"
  },
  {
    "case_id": "EVAL-PREP-002",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "approval_required",
    "exposure_eur": "7845.20",
    "gross_profit_eur": "969.60",
    "list_total_eur": "8080.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "7595.20"
  },
  {
    "case_id": "EVAL-PREP-003",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "4293.80",
    "gross_profit_eur": "606.00",
    "list_total_eur": "4040.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "3918.80"
  },
  {
    "case_id": "EVAL-PREP-004",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "8095.20",
    "gross_profit_eur": "969.60",
    "list_total_eur": "8080.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "7595.20"
  },
  {
    "case_id": "EVAL-PREP-005",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "4543.80",
    "gross_profit_eur": "606.00",
    "list_total_eur": "4040.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "3918.80"
  },
  {
    "case_id": "EVAL-PREP-006",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "8345.20",
    "gross_profit_eur": "969.60",
    "list_total_eur": "8080.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "7595.20"
  },
  {
    "case_id": "EVAL-PREP-007",
    "catalogue_cost_eur": "4772.40",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "approval_required",
    "exposure_eur": "6520.40",
    "gross_profit_eur": "873.00",
    "list_total_eur": "5820.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "5645.40"
  },
  {
    "case_id": "EVAL-PREP-008",
    "catalogue_cost_eur": "9544.80",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "approval_required",
    "exposure_eur": "11941.60",
    "gross_profit_eur": "1396.80",
    "list_total_eur": "11640.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "10941.60"
  },
  {
    "case_id": "EVAL-PREP-009",
    "catalogue_cost_eur": "4772.40",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "6770.40",
    "gross_profit_eur": "873.00",
    "list_total_eur": "5820.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "5645.40"
  },
  {
    "case_id": "EVAL-PREP-010",
    "catalogue_cost_eur": "9544.80",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "12191.60",
    "gross_profit_eur": "1396.80",
    "list_total_eur": "11640.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "10941.60"
  },
  {
    "case_id": "EVAL-PREP-011",
    "catalogue_cost_eur": "4772.40",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "7020.40",
    "gross_profit_eur": "873.00",
    "list_total_eur": "5820.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "5645.40"
  },
  {
    "case_id": "EVAL-PREP-012",
    "catalogue_cost_eur": "9544.80",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "12441.60",
    "gross_profit_eur": "1396.80",
    "list_total_eur": "11640.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "10941.60"
  },
  {
    "case_id": "EVAL-PREP-013",
    "catalogue_cost_eur": "1430.00",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "3662.00",
    "gross_profit_eur": "607.00",
    "list_total_eur": "2100.00",
    "margin_pct": "29.79872361315660284732449681",
    "over_limit_pct": "0",
    "revenue_eur": "2037.00"
  },
  {
    "case_id": "EVAL-PREP-014",
    "catalogue_cost_eur": "2860.00",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "5698.00",
    "gross_profit_eur": "1088.00",
    "list_total_eur": "4200.00",
    "margin_pct": "27.55825734549138804457953394",
    "over_limit_pct": "0",
    "revenue_eur": "3948.00"
  },
  {
    "case_id": "EVAL-PREP-015",
    "catalogue_cost_eur": "1430.00",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "3912.00",
    "gross_profit_eur": "607.00",
    "list_total_eur": "2100.00",
    "margin_pct": "29.79872361315660284732449681",
    "over_limit_pct": "0",
    "revenue_eur": "2037.00"
  },
  {
    "case_id": "EVAL-PREP-016",
    "catalogue_cost_eur": "2860.00",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "5948.00",
    "gross_profit_eur": "1088.00",
    "list_total_eur": "4200.00",
    "margin_pct": "27.55825734549138804457953394",
    "over_limit_pct": "0",
    "revenue_eur": "3948.00"
  },
  {
    "case_id": "EVAL-PREP-017",
    "catalogue_cost_eur": "1430.00",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "4162.00",
    "gross_profit_eur": "607.00",
    "list_total_eur": "2100.00",
    "margin_pct": "29.79872361315660284732449681",
    "over_limit_pct": "0",
    "revenue_eur": "2037.00"
  },
  {
    "case_id": "EVAL-PREP-018",
    "catalogue_cost_eur": "2860.00",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "6198.00",
    "gross_profit_eur": "1088.00",
    "list_total_eur": "4200.00",
    "margin_pct": "27.55825734549138804457953394",
    "over_limit_pct": "0",
    "revenue_eur": "3948.00"
  },
  {
    "case_id": "EVAL-PREP-019",
    "catalogue_cost_eur": "1430.00",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "4412.00",
    "gross_profit_eur": "607.00",
    "list_total_eur": "2100.00",
    "margin_pct": "29.79872361315660284732449681",
    "over_limit_pct": "0",
    "revenue_eur": "2037.00"
  },
  {
    "case_id": "EVAL-PREP-020",
    "catalogue_cost_eur": "2860.00",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "6448.00",
    "gross_profit_eur": "1088.00",
    "list_total_eur": "4200.00",
    "margin_pct": "27.55825734549138804457953394",
    "over_limit_pct": "0",
    "revenue_eur": "3948.00"
  },
  {
    "case_id": "EVAL-PREP-021",
    "catalogue_cost_eur": "10564.80",
    "category_floor_pct": "20",
    "discount_pct": "3.00",
    "draft_gate": "approval_required",
    "exposure_eur": "19153.80",
    "gross_profit_eur": "5964.00",
    "list_total_eur": "17040.00",
    "margin_pct": "36.08247422680412371134020619",
    "over_limit_pct": "0",
    "revenue_eur": "16528.80"
  },
  {
    "case_id": "EVAL-PREP-022",
    "catalogue_cost_eur": "21129.60",
    "category_floor_pct": "20",
    "discount_pct": "6.00",
    "draft_gate": "approval_required",
    "exposure_eur": "34785.20",
    "gross_profit_eur": "10905.60",
    "list_total_eur": "34080.00",
    "margin_pct": "34.04255319148936170212765957",
    "over_limit_pct": "0",
    "revenue_eur": "32035.20"
  },
  {
    "case_id": "EVAL-PREP-023",
    "catalogue_cost_eur": "10564.80",
    "category_floor_pct": "20",
    "discount_pct": "3.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "19403.80",
    "gross_profit_eur": "5964.00",
    "list_total_eur": "17040.00",
    "margin_pct": "36.08247422680412371134020619",
    "over_limit_pct": "0",
    "revenue_eur": "16528.80"
  },
  {
    "case_id": "EVAL-PREP-024",
    "catalogue_cost_eur": "21129.60",
    "category_floor_pct": "20",
    "discount_pct": "6.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "35035.20",
    "gross_profit_eur": "10905.60",
    "list_total_eur": "34080.00",
    "margin_pct": "34.04255319148936170212765957",
    "over_limit_pct": "0",
    "revenue_eur": "32035.20"
  },
  {
    "case_id": "EVAL-PREP-025",
    "catalogue_cost_eur": "10564.80",
    "category_floor_pct": "20",
    "discount_pct": "3.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "19653.80",
    "gross_profit_eur": "5964.00",
    "list_total_eur": "17040.00",
    "margin_pct": "36.08247422680412371134020619",
    "over_limit_pct": "0",
    "revenue_eur": "16528.80"
  },
  {
    "case_id": "EVAL-PREP-026",
    "catalogue_cost_eur": "21129.60",
    "category_floor_pct": "20",
    "discount_pct": "6.00",
    "draft_gate": "needs_evidence",
    "exposure_eur": "35285.20",
    "gross_profit_eur": "10905.60",
    "list_total_eur": "34080.00",
    "margin_pct": "34.04255319148936170212765957",
    "over_limit_pct": "0",
    "revenue_eur": "32035.20"
  },
  {
    "case_id": "EVAL-PREP-027",
    "catalogue_cost_eur": "22734.40",
    "category_floor_pct": "25",
    "discount_pct": "3.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "45783.40",
    "gross_profit_eur": "19674.00",
    "list_total_eur": "43720.00",
    "margin_pct": "46.39175257731958762886597938",
    "over_limit_pct": "0",
    "revenue_eur": "42408.40"
  },
  {
    "case_id": "EVAL-PREP-028",
    "catalogue_cost_eur": "45468.80",
    "category_floor_pct": "25",
    "discount_pct": "6.00",
    "draft_gate": "needs_commitment",
    "exposure_eur": "85693.60",
    "gross_profit_eur": "36724.80",
    "list_total_eur": "87440.00",
    "margin_pct": "44.68085106382978723404255319",
    "over_limit_pct": "0",
    "revenue_eur": "82193.60"
  },
  {
    "case_id": "EVAL-PREP-029",
    "catalogue_cost_eur": "22734.40",
    "category_floor_pct": "25",
    "discount_pct": "3.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "46033.40",
    "gross_profit_eur": "19674.00",
    "list_total_eur": "43720.00",
    "margin_pct": "46.39175257731958762886597938",
    "over_limit_pct": "0",
    "revenue_eur": "42408.40"
  },
  {
    "case_id": "EVAL-PREP-030",
    "catalogue_cost_eur": "45468.80",
    "category_floor_pct": "25",
    "discount_pct": "6.00",
    "draft_gate": "needs_revision",
    "exposure_eur": "85943.60",
    "gross_profit_eur": "36724.80",
    "list_total_eur": "87440.00",
    "margin_pct": "44.68085106382978723404255319",
    "over_limit_pct": "0",
    "revenue_eur": "82193.60"
  },
  {
    "case_id": "EVAL-PREP-031",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "blocked",
    "exposure_eur": "4818.80",
    "gross_profit_eur": "606.00",
    "list_total_eur": "4040.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "381.8800",
    "revenue_eur": "3918.80"
  },
  {
    "case_id": "EVAL-PREP-032",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "blocked",
    "exposure_eur": "8495.20",
    "gross_profit_eur": "969.60",
    "list_total_eur": "8080.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "749.5200",
    "revenue_eur": "7595.20"
  },
  {
    "case_id": "EVAL-PREP-033",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "17.18019801980198019801980198",
    "draft_gate": "blocked",
    "exposure_eur": "7470.92",
    "gross_profit_eur": "33.12",
    "list_total_eur": "4040.00",
    "margin_pct": "0.9898622800306044376434583015",
    "over_limit_pct": "0",
    "revenue_eur": "3345.92"
  },
  {
    "case_id": "EVAL-PREP-034",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "17.18019801980198019801980198",
    "draft_gate": "blocked",
    "exposure_eur": "10941.84",
    "gross_profit_eur": "66.24",
    "list_total_eur": "8080.00",
    "margin_pct": "0.9898622800306044376434583015",
    "over_limit_pct": "0",
    "revenue_eur": "6691.84"
  },
  {
    "case_id": "EVAL-PREP-035",
    "catalogue_cost_eur": "3312.80",
    "category_floor_pct": "8",
    "discount_pct": "3.00",
    "draft_gate": "approval_required",
    "exposure_eur": "8293.80",
    "gross_profit_eur": "606.00",
    "list_total_eur": "4040.00",
    "margin_pct": "15.46391752577319587628865979",
    "over_limit_pct": "0",
    "revenue_eur": "3918.80"
  },
  {
    "case_id": "EVAL-PREP-036",
    "catalogue_cost_eur": "6625.60",
    "category_floor_pct": "8",
    "discount_pct": "6.00",
    "draft_gate": "approval_required",
    "exposure_eur": "12095.20",
    "gross_profit_eur": "969.60",
    "list_total_eur": "8080.00",
    "margin_pct": "12.76595744680851063829787234",
    "over_limit_pct": "0",
    "revenue_eur": "7595.20"
  }
]

```

## Exact reviewer instruction

```text
You are a newly initiated model reviewer, authorized by Ali to draft findings from the version-2 synthetic Deal Desk evaluation facts. You have no parent conversation context. This is a model draft review, not human verification, cross-model independence or an accepted answer key.

Visibility boundary: read ONLY files inside /tmp/dealdesk_v2_review_inputs. That folder contains the pinned packet_index.json, 36 EVAL-PREP-NNN.json source packets, their 36 separate -provider.json records, review_template.json and review_format.py. The approved fictional business contract is embedded in each packet. Do not read any other filesystem locations, prior reviews, authoring maps, generators, reader/decision implementation, tests/diagnostic outcomes, GitHub/web or other tools' private history. Do not call the system under evaluation or spawn/delegate to other agents. You may execute your own arithmetic/scripts over these allowed files and import the allowed format module. This is an instruction-only restriction; do not claim an OS-enforced sandbox or a verified different model family.

Write ONLY under /tmp/dealdesk_v2_review_output. First verify all 36 packet payload hashes and 36 provider exact-byte hashes against the supplied index. Read the facts/business contract/raw rules, then reason independently for every case, with findings for Configuration, Pricing, Availability, Credit, Policy and Approval. Do not substitute aggregate counts or author case-number templates for reasoning. Supply substantive case-specific rationales, exact arithmetic when relevant, actual source pointers, human actions and unresolved questions. Interpret the declared fictional company and rules consistently, without importing unstated market/vendor/business facts. Supplied source sets are complete fictional snapshots: empty receivable/payment collections mean none within this snapshot, not an assumed favorable payment history. Separate synthetic provider records are controlled simulated evidence, not real-world verification; matching identities, quantities, dates, term and declared proof rules matter. Do not approve a deal, reserve supply/capacity or promise delivery.

Use review_template.json as the schema and review_format.py to validate. Permitted evidence pointers include /source_rows/... and /run_context/... and /business_contract/... in packet, and /records... in provider. All 36 cases should be draft_complete, with reviewer method=model and truthful identity, timezone-aware reviewed_at and independence_statement. Keep independently_reviewed_answers=0, answer_key_agent_visible=false and the review-workspace unreleased status. None of these drafts are accepted independent answers.

Deliver:
1. model_review_v2_draft.json: all 36 substantive drafts (216 responsibility findings).
2. reviewer_notes.md: exact method/allowed files consulted, limitations/remaining ambiguity, arithmetic/cross-case observations and self-check disclosures. Distinguish instruction boundary from enforced isolation and same-session model configuration from cross-model independence. Do not claim confidence establishes acceptance.
3. validation_report.json and source_hash_verification.json from the allowed inputs.
If you amend a fully assembled draft during source-only self-check, retain the earlier assembly and describe precise corrections; never silently rewrite after receiving primary author observations. Repeat hash/format checks at completion. Keep any own arithmetic/assembly helper in the output directory for audit, explicitly not an oracle or system implementation. You may report progress to the primary agent at meaningful checkpoints but do not request or consult expected answers.
```
