# Version-2 substantive verification sheet — awaiting human review

**36 source-arithmetic checks completed; 0/36 answers accepted.** This is primary-author/model-assisted verification after reading the delivered model draft. It is not another blind review, independent expert validation, a scored answer key or a release approval. The original model draft and both input versions remain unchanged.

Source commit: `5cfddf7d77a56f0880a59618a967344642fb5eb5`; v2 definition digest `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`. Reviewed model file SHA-256: `9cdffe708cf4fab3ddc022132e60a4aaf2c1f036cc832c01691673203657bc72`. Expanded source-arithmetic report SHA-256: `87f71a574805e0f8ef97c5323d58eb6ec569a67dd6650063d6dd6e6387ee24d3` (the previous narrower report digest `0063379e...` remains its dated checkpoint). The report is reproduced from fresh PostgreSQL exports in CI, outside system-visible input artifacts.

The [audit](../../implementation/audit_phase1c_evaluation_contract.py) verifies all 72 packet/provider hashes before deriving money, exposure, source ages and bounded conditional offer/operation schedules. It reads source packets only: no model answers, authoring archetypes, reader/decision engine, baseline outcomes or expected gates. The review sheet then compares those facts with the separately saved model draft. Six unit checks cover time boundaries, identity/tampering, full billed digital quantity and multi-line exposure, weekends/declared holidays, and missing separate-day operation evidence. These are fact/arithmetic checks, not a second business-decision engine or a proof of all 216 findings.

## Proposed corrections to the delivered draft

The approved G1 contract concerns the submitted quantity/date/region. No submitted field binds cases019/020 to a selected purchase order or sourcing route. A late confirmed route does not by itself prove that the customer request must change when a viable earlier alternative exists. This follows the already approved contract; no new freshness/cost/schema rule is proposed.

| Cases | Delivered wording | Primary-author proposal, still unaccepted |
| --- | --- | --- |
| 019 | needs_revision, with Sales Director for the late confirmed route | Propose needs_commitment for the earlier matching compute offer plus production/dispatch commitments. Its maximum lead illustration reaches the existing Sep10 request. Retain the October route's missing later capacity as a separate rejected/unevidenced alternative; do not make it the only route. |
| 020 | needs_revision, with Sales Director for the late confirmed route | Propose needs_commitment for a **specific conditional** earlier receipt no later than Sep7 and Sep7/8 operations, giving indicative Sep10 arrival before the Sep11 request. Supplier/workshop/dispatch humans must commit this route. The maximum-lead Sep9 receipt lacks a later test observation under the conservative schedule; that alternative needs evidence. Adjudicate whether the overall gate may use the documented feasible modal alternative or must await stronger lead-time evidence; do not assert that all routes are late. |
| 019–020 Policy/Approval | A submitted-date revision is required and Sales Director is applicable because the confirmed route is late | For the conditional timely replacement, retain the customer's quantity/date and present ordinary Regional_Manager routing only as provisional information after commitments are resolved (unless other explicit rules trigger). Sales Director applies to a proposed **later customer date**, under R1, rather than being mandatory solely because one alternative PO is late. No approval or commitment is granted. |
| 031–032 Approval | Regional_Manager described as applicable while credit hard-blocked | Exact replacement: “Current executable approval route: none. Credit exposure exceeds the 15% hard cap; no ordinary sales or Finance-exception route may waive it. After an allowed corrected submission clears the hard block, perform a fresh assessment before deriving a route.” Retain the blocked gate and source-specific Credit/Policy findings. |
| 033–034 Approval | Sales_Director described as applicable while margin hard-blocked | Exact replacement: “Current executable approval route: none. Category margin shortfall exceeds the two-point exception limit; ordinary discount escalation cannot waive that prohibition. After an allowed corrected submission clears the hard block, perform a fresh assessment before deriving a route.” Retain the blocked gate and source-specific Pricing/Policy findings. |

These proposals replace the route-only reasoning and hard-block routing language, not the underlying source facts. They have not been applied to the original draft or counted as independently accepted answers. No comparison with the deterministic implementation is used as a correctness test. A separate author-assisted review view is reconstructed from the small [`v2_author_amendments.json`](v2_author_amendments.json) file. Its six amended cases carry model_assisted primary-author provenance; the other30 retain original model provenance. The amendments bind the exact original review-file hash and current input-index/case hashes. Invalid references, altered sources and acceptance claims fail. CI preserves the derived review and its zero-acceptance validation as a reviewer-only artifact; the original is never overwritten.

## Evidence for the two competing-route cases

Assumption: a hypothetical Sep1 order on the supplied Monday–Friday supplier calendar; operations on separate days using current active capacity and exact capability/resource/location matching; completion-day dispatch must be confirmed before the 16:00 cutoff; transit counted on weekdays. These are illustrative **uncommitted** schedules. Component arrival times, intraday completion, all other material/configuration checks and actual booking are not certified by the helper.

| Case | Lead assumption | Compute receipt | Assembly | Test | Indicative arrival | What remains |
| --- | --- | --- | --- | --- | --- | --- |
| EVAL-PREP-019 | min | 2026-09-02 | 2026-09-02 | 2026-09-03 | 2026-09-04 | Supplier, workshop and cutoff/dispatch commitments. |
| EVAL-PREP-019 | mode | 2026-09-04 | 2026-09-04 | 2026-09-07 | 2026-09-08 | Supplier, workshop and cutoff/dispatch commitments. |
| EVAL-PREP-019 | max | 2026-09-08 | 2026-09-08 | 2026-09-09 | 2026-09-10 | Supplier, workshop and cutoff/dispatch commitments. |
| EVAL-PREP-020 | min | 2026-09-03 | 2026-09-03 | 2026-09-04 | 2026-09-08 | Supplier, workshop and cutoff/dispatch commitments. |
| EVAL-PREP-020 | mode | 2026-09-07 | 2026-09-07 | 2026-09-08 | 2026-09-10 | Supplier, workshop and cutoff/dispatch commitments. |
| EVAL-PREP-020 | max | 2026-09-09 | 2026-09-09 | not evidenced | not established | Missing test observation; do not invent future capacity. |

For019, two outputs require1.5 hours per assembly/test operation; supplied daily net hours are7. For020, four outputs require2.5 hours per operation; net hours are8. Other raw materials are present in the supplied inventory (proportional storage demand4.04/8.08, chassis/network2/4); they still require source/freshness/configuration verification and allocation. The confirmed compute receipts are Oct1/Oct2, while the supplied capacity ends Sep9. No October finished-product completion or delivery follows.

Source pointers: `/source_rows/supplier_offers/0`, `/source_rows/inbound_supply/0`, `/source_rows/requirements`, `/source_rows/production_capacity`, `/source_rows/shipping_lanes/0`, `/source_rows/lines/0` and `/business_contract/gates`. The audit reports exact capacity-row pointers for each illustrated operation, so reviewers do not rely on positional guesses.

## All 36 cases: recomputed commercial arithmetic

“Model gate” below is quoted from the unaccepted delivered draft. The table supplies arithmetic for review; it does not certify configuration, policy, role mapping, capacity/term proof, or the gate itself. Full submitted line quantity is used for money, including all24/48 billed instance-months in digital cases, rather than2/4 concurrent instances.

| Case | Quote EUR | Margin % | Exposure EUR | Model gate | Verification focus |
| --- | ---: | ---: | ---: | --- | --- |
| EVAL-PREP-001 | 3918.80 | 15.463918 | 4043.80 | approval_required | Source/rule findings and human actions |
| EVAL-PREP-002 | 7595.20 | 12.765957 | 7845.20 | approval_required | Source/rule findings and human actions |
| EVAL-PREP-003 | 3918.80 | 15.463918 | 4293.80 | needs_revision | Source/rule findings and human actions |
| EVAL-PREP-004 | 7595.20 | 12.765957 | 8095.20 | needs_revision | Source/rule findings and human actions |
| EVAL-PREP-005 | 3918.80 | 15.463918 | 4543.80 | needs_evidence | Old evidence is not current availability |
| EVAL-PREP-006 | 7595.20 | 12.765957 | 8345.20 | needs_evidence | Old evidence is not current availability |
| EVAL-PREP-007 | 5645.40 | 15.463918 | 6520.40 | approval_required | Source/rule findings and human actions |
| EVAL-PREP-008 | 10941.60 | 12.765957 | 11941.60 | approval_required | Source/rule findings and human actions |
| EVAL-PREP-009 | 5645.40 | 15.463918 | 6770.40 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-010 | 10941.60 | 12.765957 | 12191.60 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-011 | 5645.40 | 15.463918 | 7020.40 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-012 | 10941.60 | 12.765957 | 12441.60 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-013 | 2037.00 | 29.798724 | 3662.00 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-014 | 3948.00 | 27.558257 | 5698.00 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-015 | 2037.00 | 29.798724 | 3912.00 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-016 | 3948.00 | 27.558257 | 5948.00 | needs_commitment | Source/rule findings and human actions |
| EVAL-PREP-017 | 2037.00 | 29.798724 | 4162.00 | needs_evidence | Old evidence is not current availability |
| EVAL-PREP-018 | 3948.00 | 27.558257 | 6198.00 | needs_evidence | Old evidence is not current availability |
| EVAL-PREP-019 | 2037.00 | 29.798724 | 4412.00 | needs_revision | Competing route/gate adjudication above |
| EVAL-PREP-020 | 3948.00 | 27.558257 | 6448.00 | needs_revision | Competing route/gate adjudication above |
| EVAL-PREP-021 | 16528.80 | 36.082474 | 19153.80 | approval_required | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-022 | 32035.20 | 34.042553 | 34785.20 | approval_required | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-023 | 16528.80 | 36.082474 | 19403.80 | needs_evidence | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-024 | 32035.20 | 34.042553 | 35035.20 | needs_evidence | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-025 | 16528.80 | 36.082474 | 19653.80 | needs_evidence | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-026 | 32035.20 | 34.042553 | 35285.20 | needs_evidence | Billed quantity vs concurrent demand; full provider term |
| EVAL-PREP-027 | 42408.40 | 46.391753 | 45783.40 | needs_commitment | Regional service scope vs actual booking |
| EVAL-PREP-028 | 82193.60 | 44.680851 | 85693.60 | needs_commitment | Regional service scope vs actual booking |
| EVAL-PREP-029 | 42408.40 | 46.391753 | 46033.40 | needs_revision | Regional service scope vs actual booking |
| EVAL-PREP-030 | 82193.60 | 44.680851 | 85943.60 | needs_revision | Regional service scope vs actual booking |
| EVAL-PREP-031 | 3918.80 | 15.463918 | 4818.80 | blocked | Credit hard cap; no executable approval route |
| EVAL-PREP-032 | 7595.20 | 12.765957 | 8495.20 | blocked | Credit hard cap; no executable approval route |
| EVAL-PREP-033 | 3345.92 | 0.989862 | 7470.92 | blocked | Margin hard block; no executable approval route |
| EVAL-PREP-034 | 6691.84 | 0.989862 | 10941.84 | blocked | Margin hard block; no executable approval route |
| EVAL-PREP-035 | 3918.80 | 15.463918 | 8293.80 | approval_required | Source/rule findings and human actions |
| EVAL-PREP-036 | 7595.20 | 12.765957 | 12095.20 | approval_required | Source/rule findings and human actions |

Cases031/032: EUR4,818.80/EUR8,495.20 exposure against EUR1,000, or381.88%/749.52% excess. The15% exception ceiling would be EUR1,150; ordinary routing does not bypass it. Cases033/034: unit price EUR1,672.96 minus cost EUR1,656.40 equals EUR16.56 profit, or0.989862% margin; shortfall below the8% floor is7.010138 points, beyond the two-point exception. Discount escalation remains a separate finding, not authority to waive the margin prohibition.

## Reconstruct the separate author-assisted review view

From the implementation directory, after obtaining the pinned source packets:

```sh
python phase1c_evaluation_review.py --review-file ../evaluation/reviews/model_review_v2_draft.json --packet-directory /tmp/phase1c_evaluation_packets --amendments ../evaluation/reviews/v2_author_amendments.json --write-amended-review /tmp/phase1c_v2_author_assisted_review.json
```

This generates an unaccepted draft for review, not an independently verified answer file. The proposed six corrections above are applied only in this derived view; the source packets and original review remain intact.

## Human verification and acceptance still required

For each case, verify the source dates/IDs and all six responsibilities, check calculations, review conditional alternatives and policy/routing precedence, then record the accepted finding/gate/actions or requested correction with your reasoning. Record reviewer identity, source and draft versions/hashes, date and provenance. A generic approval of business conventions or permission to continue is not recorded as independent case verification. If the reviewer uses this primary-author proposal, disclose model/author assistance; do not claim a blind independent pass.

The original reviewer form remains draft_complete and the current blank template stays blank. No accepted answer file or baseline scoring is created here. Six field marks and the two master-data calibration decisions remain separately open, and `ready_for_generation=false`. The [v2 review record](model_review_v2_record.md) and [calibration sheet](../../calibration-decision-sheet.md) retain the other boundaries.

## Hard-block action consistency correction — 14 October 2026

A cross-case wording check found that the first author-assisted amendment changed the Approval finding for 031–034 but inherited each original overall action telling the reader to submit the blocked deal to a sales approver. The separate hash-bound amendment now replaces those overall actions: **no executable approval route for the current hard-blocked submission**; correct the exposure or price, then rerun all six checks before deriving a route. Allocation and dispatch remain separate later human commitments. The source packets and original model draft are unchanged. This is a primary-author/model-assisted correction to the review view, not a blind second review or accepted answer; **0/36** remain accepted. Case 020's conditional-route adjudication and every case's substantive review are still open.

## Case 020 exact decision brief — 15 October 2026

The [source-bound route adjudication](case_020_route_adjudication.md) compares the confirmed October receipt with the minimum, modal and maximum offer schedules, lists the missing Sep 10 test and dispatch evidence, and states the precise gate alternatives and consequences. Packet/provider hashes and the source-audit projections were rechecked against the passing PR workflow artifact. This is a primary-author decision brief, not a new reviewer, accepted answer or change to the original/assisted drafts. Case 020 remains unresolved; accepted answers remain **0/36**.

## Provider verification-age source audit — 15 October 2026

The source-only audit now reports the separate provider records' `verified_at` ages under approved F1's inclusive seven-day window. Four records appear in cases 021, 022, 025 and 026, each verified about 1.42–1.58 hours before its run; 023/024 have no provider record. This is **only verification age**, not a finding that identity, capacity, binding status, dates or full contract term pass. The new report SHA-256 is `a2fc5d3956cf436144c28068e35c4367166a19e8ae37279251e1908ca13ab2d6`. Removing only the newly reported provider-age fields reproduces the previous report digest `87f71a57...`, confirming that other audited facts stayed unchanged. Seven local tests pass. All source packets and model/author-assisted drafts remain unchanged; 0/36 answers accepted.

## Digital provider source-field comparison — 15 October 2026

The source-only audit now compares each sealed provider record with the digital line and its referenced capacity row: product, declared configuration/region, concurrent units, capacity/allocation, validity at the run, and F1 calendar-month coverage. It does **not** decide the case or certify an actual service commitment. Cases 021/022 have matching declared fields and proof coverage through at least the Sep 2027 anniversary; 025/026 have otherwise matching declared fields but `covers_until=2026-12-31`, before the Sep 2027 anniversary. Cases 023/024 contain no provider proof. Eight local tests pass, including month-end clamping and mismatch examples. The new source report SHA-256 is `2dfd676b5749941514798b6bd197df1c3515c2de3e855e7e3e1db119c5576c3d`; removing only `provider_source_comparisons` reproduces the immediately previous report `a2fc5d39...`. No original model or author-assisted draft is accepted; 0/36 answers remain accepted.

## Exact service-region source comparison — 15 October 2026

The source-only audit now lists active, same-product, same-catalogue `installation_eligibility` rows matching each scheduled-service line's exact destination country and region. Cases 027/028 have explicit `eligible=true` DE-NW records; 029/030 have explicit `eligible=false` DE-BY records. All four set `installation_requested=false`, which does not remove the service line's regional coverage requirement under approved S1. An eligible region is not a booked appointment or service commitment. Nine local tests pass, including an inactive/mismatched-region check. New report SHA-256: `4c8f2e5bdbff985025e0b7898593f229975c76a1cf926952844c24e77d1abd25`; dropping only the new service comparison fields reproduces the previous report digest `2dfd676b...`. These are source facts, not accepted answers (0/36).
