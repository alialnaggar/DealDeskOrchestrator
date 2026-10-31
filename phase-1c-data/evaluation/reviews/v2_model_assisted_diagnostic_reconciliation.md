# V2 model-assisted diagnostic reconciliation — 22 October 2026

**Use:** bounded qualitative engineering diagnostics from the pinned v2 inputs. This is Codex analysis, not an independent or accepted answer key. Ali chose to use this analysis for development rather than personally adjudicate 36 cases in chat. That choice does not attest to six-responsibility correctness, change the separate reviewer workspace, or authorize accuracy scoring. **Accepted answers: 0/36; `ready_for_generation=false`.**

The source-definition SHA-256 is `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`; canonical index SHA-256 is `7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc`. The [001–012](v2_batch_001_012_review.md), [013–024](v2_batch_013_024_review.md) and [025–036](v2_batch_025_036_review.md) source-first aids checked packet/provider hashes, source arithmetic, dates and route conditions before comparing the [preserved model draft](model_review_v2_draft.json) and [separate author-assisted amendments](v2_author_amendments.json). Agreement between these related analyses is not independent corroboration. No source, provider file, index, draft, amendment or hash is changed by this reconciliation.

## Corrected diagnostic view

The [separate Codex correction layer](v2_codex_diagnostic_corrections.json) amends 22 draft cases (003–006, 009–018, 023–030) after the six [author-assisted amendments](v2_author_amendments.json). It removes the nonexistent cancelled receipt from 009–010, puts source repair and rerun before any later approval route in conditional/evidence/revision cases, and specifies the selected material plan in 013–014. These two layers are disjoint, bind the same original draft SHA-256, and are applied only to a reviewer-side diagnostic copy. Eight cases retain their original model draft. The CI combined-view check validates all 36 packet/provider pins and records **0 independently reviewed answers**; its artifact is diagnostic and cannot serve as an answer key.

## Provisional pattern for diagnostics only

Each row covers two distinct input cases, not two independent adjudications. The gate column is a proposal to inspect during development, never an expected label for an accuracy calculation.

| Cases | Source distinction to preserve | Provisional gate |
| --- | --- | --- |
| 001–002 | Fresh free stock and a dated active shipping lane; allocation and dispatch remain human actions. | `approval_required` |
| 003–004 | All observed stock allocated; no dated inbound or offer; partial permission adds no supply. | `needs_revision` |
| 005–006 | Inventory observation 49/61 hours old against the 24-hour convention. | `needs_evidence` |
| 007–008 | Timely confirmed same-product receipt; a separate active offer is uncommitted. | `approval_required` |
| 009–010 | Active offer only, no inbound receipt; estimated dates require new commitments. | `needs_commitment` |
| 011–012 | Cancelled receipt/PO plus a separate active conditional offer; cancelled units do not count. | `needs_commitment` |
| 013–014 | Component stock and dated workshop hours permit an illustrative build; no slot is booked. | `needs_commitment` |
| 015–016 | Confirmed alternate component receipt plus uncommitted offer; assembly, test and dispatch remain conditional. | `needs_commitment` |
| 017–018 | Workshop observations 51/52 hours old; no current capacity proof. | `needs_evidence` |
| 019–020 | Late confirmed PO coexists with earlier active component offer; only a specified conditional route can preserve the requested date. | `needs_commitment` proposed for that route; see limits below |
| 021–022 | Fresh matching binding digital proof, concurrent capacity and full 12-month term declaration. | `approval_required` |
| 023–024 | Pool exists but separate provider proof collection is empty. | `needs_evidence` |
| 025–026 | Recent proof ends in Dec 2026, before the Sep 2027 term anniversary. | `needs_evidence` |
| 027–028 | Exact eligible region but no booked service appointment. | `needs_commitment` |
| 029–030 | Exact region explicitly ineligible; a changed service/destination needs customer acceptance. | `needs_revision` |
| 031–032 | Credit exposure exceeds the hard exception cap despite available stock. | `blocked` |
| 033–034 | Margin shortfall exceeds the two-point exception band; discount escalation cannot waive it. | `blocked` |
| 035–036 | `legal_review` clause calls for ordered human Sales and Legal review. | `approval_required` |

## Disagreements and restrictions before any reference use

1. The original draft routes 019–020 through the late October PO and proposes `needs_revision`. The separate amendment proposes an earlier conditional offer route. Case 019 has a timely **maximum-lead illustration**; for 020 Ali selected only a timely **modal** interpretation for a proposed `needs_commitment` gate. Case 020 lacks a later test observation for the maximum lead. Neither offer is a binding receipt, workshop reservation or delivery promise.
2. The original 009–010 actions mention a cancelled receipt, but those packets have **no inbound receipt**. The warning applies to 011–012. Do not reuse that erroneous action text as a diagnostic expectation.
3. The original 031–034 actions name a Sales approval route for a currently hard-blocked submission. The separate amendment withholds any executable route until a corrected submission passes a fresh six-responsibility check. Keep the original draft unmodified for provenance.
4. In 003–006, 009–012, 013–020 and 023–030, a named future reviewer is conditional on resolving the current supply, evidence, date or service issue. An Approval or Policy finding must not merely copy the overall gate without its own applicable rule and action.
5. Configuration attribution in 029–030 and Policy attribution across the conditional cases remain judgment questions. For 001, the pinned packet has an active sellable stocked SKU, no specified options and no compatibility rows. A configuration concern raised in discussion has no identified source conflict yet; do not promote the model's `no_issue_identified` finding into an accepted conclusion or assert manufacturer fit.
6. Keep quantities and dates exact: digital 24/48 billed `instance_month` units are two/four concurrent instances; regional eligibility is not a service booking; historical modal-only offers have no established dated route. All delivery dates from uncommitted offers and workshop illustrations remain conditional.

## Permitted next use

Use the three detailed aids and this index to investigate discrepancies, exercise development-only checks and design a later reviewer task. Record any comparison with deterministic or agent output as a **qualitative diagnostic with model-assisted provenance**, not a count of correct cases or an accuracy percentage. The 400 historical and 100 generated cases remain diagnostics too. If thesis scoring is desired, obtain separately adjudicated case findings for the exact scored subset, document reviewer assistance, and keep those answers outside agent-visible inputs. The Phase 1C full release still requires the runtime-output field evidence and final audit; PR #1 remains draft.
