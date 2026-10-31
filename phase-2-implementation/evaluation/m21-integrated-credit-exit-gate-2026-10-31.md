# M2.1 integrated Credit development and exit gate — 31 October 2026

**Recommendation: C — keep M2.1 open.** This is a bounded synthetic development
assessment, not an accuracy study or approval of a production runtime.
Phase 1C remains pinned to `90c0bc8e285ee69262c7db826b786096a77ad004`;
neither its 36 evaluation cases nor supplemental controls were changed.

## Minimal integrated coverage and source boundary

The existing B01 source supports a fixed-checked Fulfillment candidate; N01
forbids partial delivery and supports a no-candidate path. Existing isolated
CR01/CR02/CR03 are N01 clones and cannot by themselves test a candidate.
Three opt-in **development-only overlays** on separate fresh disposable B01/N01
business databases are the smallest distinct integrated source shapes here:

| Variant | Base | Credit source and fixed preflight | Integrated question |
| --- | --- | --- | --- |
| RC01 | B01 | Active/fresh profile; 100.00 AR original, 40.00 paid, 60.00 outstanding; fixed `calculated`, exposure 9160.00 | Candidate full six-check re-evaluation followed by original-subject transactional Credit investigation. |
| HC03 | N01 | On-Hold/fresh profile; overdue 1200.00 AR original, 300.00 paid, 900.00 outstanding; fixed `infeasible`, exposure 10100.00 | No-candidate six-specialist path with a held/overdue customer. |
| UC02 | N01 | Review/stale commitments; no selected AR/payment in this synthetic source; fixed `unknown`, exposure 9300.00 | No-candidate six-specialist path accepting uncertainty or abstention without inventing a zero balance. |

The runner accepts only the exact case/variant combinations with
`--specialist six_campaign --credit-variant ...`. It rejects any preexisting
AR/payment for the selected customer, checks the pinned reader and fixed
Credit calculation **before** any hosted request, verifies exact customer,
invoice and amount linkage, writes a private exclusive variant/digest receipt,
and retains fresh business/checkpoint assessment identity and no-replay gates.
These overlays alter synthetic external credit evidence in the *disposable*
database, not the original submitted deal or the pinned Phase 1C checkout.

## Offline and hosted outcomes

The full discoverable local Phase 2 regression on five **fresh** isolated
business databases and three fresh checkpoint databases passed: **336 run,
336 passed, 0 failed, 0 skipped**. Three added integrated offline model-double
tests passed: RC01 candidate, HC03 no candidate, UC02 valid Credit abstention.
The campaign uses the actual LangGraph nodes, pinned source and fixed
candidate verifier, checked candidate/original subject isolation, strict
model-wire/claim parsing, durable receipts and terminal no-replay test. Offline
abstention is recorded as `abstained`, not a failed finding. Tampered invoice
joins/customer identity fail source preflight. This is local verification;
GitHub Actions status is separate and not verified here.

Two **fresh** authorized free-tier Groq integrated assessments were attempted:

| Assessment | Observed outcome | Boundary |
| --- | --- | --- |
| `GROQ-DEV-a0108d5c19b34178b612c2a2213a1b97` RC01/B01 | All six AI stages completed; Fulfillment produced one `fixed_checked` candidate; the candidate has six fixed results on its own subject. Original Credit inspected profile/AR/payment and validated six original-only claims including AR `outstanding_amount=60.00` and payment `paid_amount=40.00`. Policy and Routing completed; original review `needs_revision`. | Candidate needs human acceptance; fixed supply is not a reservation, and model did not compute authoritative exposure or clear credit. No candidate evidence became an original Credit claim. |
| `GROQ-DEV-e32c6dbfb0e049a8b3850d39f63c0c08` HC03/N01 | Fixed original Credit was `infeasible` and review `blocked`. Configuration's first inspected product ref, then its terminal response failed strict semantic/evidence validation (`terminal_semantics_or_evidence`). Campaign stopped with `terminal_failure`; no Pricing, Fulfillment, Credit, Policy or Routing AI was invoked; no candidate. | This does **not** demonstrate hosted On-Hold/overdue Credit or a hosted no-candidate six-stage result in the new variant. Raw provider response was intentionally not retained; the exact Configuration cause is unknown. No terminal replay. |

No UC02 hosted attempt followed: the preceding N01-based campaign stopped
before Credit on a Configuration validation error. Repeating its upstream
Configuration path without a narrower diagnostic would add little evidence
about Credit abstention. **Hosted incomplete-evidence abstention has not been
demonstrated.** Earlier isolated CR02 returned a *finding* citing incomplete
profile evidence, not an abstention; the integrated UC02 mock did abstain.
Previously reported B01/B05/N01 hosted completions remain separate prior
milestones, not new reruns in this campaign.

## Exit gate

| Dimension | Evidence and status |
| --- | --- |
| Functional coverage | Six-stage hosted RC01 with a fixed-checked candidate and original-subject transactional Credit: **demonstrated once**. Prior hosted N01 no-candidate workflow exists; held/overdue integrated N01 and live incomplete-evidence abstention: **not demonstrated**. |
| Runtime reliability | A successful integrated RC01 and a pre-Credit HC03 terminal error are not a stability sample. No statistical reliability or comparative superiority established. |
| Offline contracts | All three integrated source shapes, candidate/no-candidate, exact AR/payment citations, abstention, fixed-rule isolation and no-replay: **tested, 336/336 full suite**. |
| Provider failures | HC03 Configuration semantic/evidence failure, exact raw cause unknown. Historical Fulfillment final HTTP 400 **remains unresolved**; neither new assessment produced one. Existing bounded phase, serialized bytes, schema hash and allowlisted provider diagnostic are already recorded. RC01's successful Fulfillment final was 9,883 bytes with schema SHA-256 `4d9077a08f5b1129a83ca05b434a84b9eae1dfa22440332fa4ceb674ca0977f6`; similarity to failed requests does **not** prove a cause. No new unsafe request metadata or error-body logging is justified. |
| Governance/deterministic safety | Fresh identities and private manifests; no replay of uncertain or terminal sends, no paid API, no candidate/customer approval, source rows and candidate subjects isolated. Fixed Credit and Phase 1C verifier retain all financial/delivery authority. |
| Formal evaluation | Independent accepted Phase 1C answers and repeated predeclared case comparisons are still missing; development successes cannot serve as measured accuracy. |

**Concrete next gate:** investigate HC03 Configuration's safe rejection class
offline for a reproducible contract ambiguity, rather than retrying its
terminal assessment. Then run *fresh* integrated held/overdue and UC02
incomplete-evidence assessments only if upstream validity makes Credit
reachable; preserve abstention as a legitimate result. Diagnose Fulfillment
HTTP 400 only with bounded offline comparisons or a fresh legitimate failure,
without inferring its cause from request size/hash or replaying old sends.
Review CI separately; seek accepted evaluation answers before a formal thesis
quality or production-readiness decision.
