# Version-2 evaluation review handoff — 15 October 2026

**Status: 36 provisional inputs; 36 model drafts; 0/36 accepted answers.** This is a queue for substantive review, not an answer key. Original model drafts, the six-case primary-author amendment, the blank reviewer workspace, and source-only audits have different provenance. A row in this document does not assign a gate or approve a deal.

## Pinned materials and order of use

1. Use the v2 [packet index](../provisional_packet_index.json) with source-definition SHA-256 `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`, the 36 source packets and 36 separate provider files from the [passing PostgreSQL run](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38672706316). Verify each packet/provider hash before reviewing.
2. Read the approved [fictional business contract](../../implementation/phase1c_evaluation_business_contract.json) embedded in every v2 packet. Use only the case's frozen source rows and provider file to write initial findings for Configuration, Pricing, Availability, Credit, Policy and Approval, plus overall human actions. The [blank template](../provisional_review_template.json) and [validator](../../implementation/phase1c_evaluation_review.py) check shape, provenance, source identity and citations; they do not certify a correct answer.
3. After the initial source review, compare it with the [original v2 model draft](model_review_v2_draft.json), [author-assisted amendment](v2_author_amendments.json), [verification sheet](v2_verification_sheet.md) and source-only CI audit. Record disagreements and correction reasons. The amended view is reconstructed separately; neither draft is an independent oracle.
4. An accountable reviewer must record identity, method, date, source hashes, reasoning for all six responsibilities, and whether model/primary-author assistance was used. Accept or reject each case explicitly in a separate reviewer-only record. Keep accepted material outside agent-visible inputs. **Do not score** the rule-only baseline or agents until cases have accepted expected findings.

## Review queue

Every pair below contains two distinct quantities under the same source-condition family. The prompt is a verification task, not an expected answer. Arithmetic, evidence ages and cited source IDs can be checked in the [source-only contract audit](../../implementation/audit_phase1c_evaluation_contract.py) and its CI artifact. The source audit does not decide gates.

| Cases | Source facts to verify before case-level judgment |
| --- | --- |
| 001–002 | Net stock, allocation, requested date, lane and human dispatch handoff. |
| 003–004 | Allocated stock versus free quantity; whether the submitted quantity/date has any other support. |
| 005–006 | Inventory observations 49/61 hours old against the approved 24-hour window; distinguish unknown current stock from proven shortage. |
| 007–008 | Confirmed same-product inbound receipt, unallocated quantity, requested date and lane; avoid treating expected receipt as delivery already completed. |
| 009–010 | Offer-only supply with no inbound receipt; distinguish an uncommitted procurement alternative from binding supply. |
| 011–012 | Cancelled inbound receipt alongside an active offer; do not count the cancelled receipt as binding supply. Inspect lead/calendar and missing new commitment. |
| 013–014 | Component quantities, BOM fit, separate assembly/test operations, capacity hours and dispatch assumptions. |
| 015–016 | Confirmed component receipt alongside an active same-product offer; check component cost identity, dated receipt and operation sequence. |
| 017–018 | Production observations 51/52 hours old; request current capacity evidence rather than borrowing stale hours. |
| 019–020 | Competing October confirmed receipt and earlier uncommitted offer. Review the [route decision brief](case_020_route_adjudication.md): 019 has a timely illustrated maximum-lead schedule; 020 has a timely modal schedule but no later test observation for its maximum lead. The whole-deal gate and route-dependent roles need explicit adjudication. |
| 021–022 | Digital provider identity/configuration, concurrent units versus full billed quantity, fresh verification and coverage through the 12-month anniversary. |
| 023–024 | Digital capacity snapshot exists but the separate provider proof collection is empty; determine what can be supported without proof. |
| 025–026 | Provider proof is present and freshly verified, but `covers_until=2026-12-31` precedes the Sep 2027 anniversary. Do not confuse proof validity with full service coverage. |
| 027–028 | Exact eligible DE-NW scheduled-service region; no booked slot follows from eligibility. `installation_requested=false` does not remove the service line's region requirement. |
| 029–030 | Exact `eligible=false` DE-BY record; check changed region/service choices and customer acceptance separately. |
| 031–032 | Exposure relative to credit limit and 15% hard cap. The current hard-blocked submission has no executable ordinary/Finance exception approval route; a corrected submission needs a fresh six-responsibility review. |
| 033–034 | Submitted margin against 8% category floor and two-point exception band. No executable approval route while the hard prohibition remains; do not confuse discount escalation with a margin waiver. |
| 035–036 | Financial and policy escalation conditions on otherwise ordinary stock submissions; verify the exact applicable human roles and order. |

The source-only audit currently reports exact arithmetic for all 36 cases, provider verification ages for four records, digital provider field/term comparisons and four exact service-region matches. It has SHA-256 `4c8f2e5bdbff985025e0b7898593f229975c76a1cf926952844c24e77d1abd25` on the last passing source version; its additional reports do not change any packet or model draft. Later CI runs should verify the matching digest before a reviewer relies on this pin.

## Boundary and next decision

Case 020's modal-route proposal remains a **primary-author/model-assisted proposal**, not accepted merely because work continued. Ali's explicit choice on whether this specific conditional route is enough for a proposed `needs_commitment` gate would settle one business interpretation for review; it would not accept the six findings automatically. The other 35 cases also require substantive case-level verification. Six field marks, two catalogue calibration reviews and `ready_for_generation=false` remain open. PR #1 stays draft.

## Input replay gate — 22 October 2026

The current v2 source definitions and pinned packet index are unchanged. `test_phase1c_evaluation_cases.py` now prepares all 36 case packets, 36 separate provider files and the index twice through separate PostgreSQL connections on the clean, dedicated evaluation database, rolling back every case and each import. It verifies the pinned source-definition and per-case hashes in each pass, checks the 73 output filenames, and compares all file bytes across passes. Both passes require no development/historical or cross-case operational rows, no committed deal rows after export, and no answer-bearing keys. This is a reproducibility gate for the **existing v2 input version**; it neither creates a v3 nor rebinds the preserved original/author-assisted drafts.

After the full PostgreSQL CI pass, v2 can be treated as the pinned input version for the current bounded synthetic scope. If any source fact or approved business convention changes, create a new version and redo the hashes and case review. The separate reviewer answer workspace remains blank with **0/36 accepted**; case 020 is unresolved and the final data release remains blocked by independent findings and runtime evidence.

## Case 020 business interpretation — 22 October 2026

Ali selected the conditional modal route as sufficient for a **proposed** `needs_commitment` gate, with explicit supplier, workshop and dispatch commitments still required. The maximum-lead route lacks the later test observation and stays unsupported for the requested date. The [hash-bound reviewer-only record](case_020_business_choice.json) and [adjudication brief](case_020_route_adjudication.md) hold the exact limits. This resolves the business interpretation to apply during review; it does not accept a six-responsibility case answer, change v2 inputs, or authorize an executable approval route. Review all 36 cases source-first; accepted answers remain **0/36**.

## First 12-case review aid — 22 October 2026

The [source-first 001–012 review aid](v2_batch_001_012_review.md) checks each pinned packet/provider pair, commercial arithmetic, supply state and indicative route, then separately identifies three saved-draft wording issues for reviewer adjudication. It is Codex model-assisted analysis, not an independently accepted answer key. Keep the blank workspace and source packets first in the review order; accepted answers remain **0/36**.

## Second 12-case review aid — 22 October 2026

The [source-first 013–024 review aid](v2_batch_013_024_review.md) checks buildable component/operation evidence, stale workshop observations, the competing 019/020 routes and separate digital provider proof before comparing preserved drafts. Case 020's selected modal interpretation remains a reviewer-only business choice, not an accepted answer. This is Codex model-assisted review material; source packets and the blank workspace precede it in the reviewer workflow. **0/36 accepted**.

## Third 12-case review aid — 22 October 2026

The [source-first 025–036 review aid](v2_batch_025_036_review.md) checks full digital term evidence, exact scheduled-service region and missing booking, credit/margin hard blocks, and Legal routing before comparing original and author-assisted drafts. Together with the [001–012](v2_batch_001_012_review.md) and [013–024](v2_batch_013_024_review.md) aids, all 36 cases now have a Codex model-assisted source-first handoff. They are **not accepted answer keys**: accountable six-responsibility case dispositions remain 0/36, and `ready_for_generation=false`.

## Human disposition intake — 22 October 2026

The [reviewer-only intake checker](../../implementation/phase1c_evaluation_acceptance.py) now makes step 6's acceptance boundary executable without creating answer labels. CI validates its empty form: **36 pending, zero recorded acceptances**. Its focused tests reject changed input/case/source-review hashes, model or model-assisted source drafts, invented review claims, missing packet/provider files, incomplete adjudicator provenance, and attempts to promote `ready_for_generation` or agent visibility. A valid structural record still reports `independence_or_correctness_certified=false`: a program cannot verify a person's identity, independence or substantive reasoning.

An accountable reviewer starts with the source packets and [blank workspace](../provisional_review_template.json), records all six findings and a source-first human review, and only afterwards compares model/author-assisted material. Keep completed files in a reviewer-only location **outside agent-visible inputs**. From `implementation/`, after that source review is complete:

```sh
python phase1c_evaluation_review.py --review-file /private/reviewer-work.json --packet-directory /private/pinned-packets
python phase1c_evaluation_acceptance.py --bind-review /private/dispositions.json --review-file /private/reviewer-work.json --packet-directory /private/pinned-packets
```

The binding command records exact source-review file and completed-case hashes as `reviewed_pending_disposition`; it accepts **nothing**. The human adjudicator then changes a reviewed case to `accepted` or `rejected`, supplies `adjudicator` (`identity`, `method=human`, timezone-aware `decided_at`, `source_first_attestation`), case `reason`, and `draft_comparison_and_assistance`, then checks it:

```sh
python phase1c_evaluation_acceptance.py --intake /private/dispositions.json --review-file /private/reviewer-work.json --packet-directory /private/pinned-packets
```

The report counts **recorded attestations only**. It never certifies business correctness or independent expertise and cannot turn existing model/author drafts into human source-first reviews. A source or reviewer file change invalidates its hash binding. Do not score an agent or alter the release flag based on structural counts. The current reviewer workspace is blank; **0/36 accepted**, `ready_for_generation=false`, PR #1 draft.
