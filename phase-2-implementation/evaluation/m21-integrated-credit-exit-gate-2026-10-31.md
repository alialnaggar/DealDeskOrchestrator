# M2.1 integrated Credit development and exit gate — 31 October 2026

## Guarded Configuration probe and fresh UC02 continuation — 31 October 2026

**Exit recommendation: C — keep M2.1 open.** This section supersedes only the
*next-step status* in the dated sections below; their original receipts, test
counts and conclusions at the time are retained. No terminal or uncertain
assessment was replayed. Hosted testing stopped after the following two fresh
assessments; neither is a reliability sample or proof that Configuration v4
caused an improvement.

The development-only `configuration_probe` uses the existing typed-final
Configuration inspection, strict final parser/evidence validator, original
source boundary, checkpoint, private manifest/receipt, rate coordinator and
no-replay guard. The manifest binds N01/UC02, a fresh assessment, the pinned
Phase 1C source and prompt hashes, `standing_configuration_probe` and an
explicit probe flag. It allows **at most two POSTs** and **1,536 configured
completion tokens**, returns before Pricing and is rejected by the normal
Pricing and production-disabled routes. The UC02 overlay was preflighted
against the disposable source: stale commitments, no selected AR/payment,
fixed Credit `unknown` and original review `needs_revision`. It did not alter
the Phase 1C pin, original submitted deal, evaluation cases, fixed rules or
validator. Offline fake sends exercised a valid finding and abstention,
rejected float and invented citation, an uncertain send, manifest/budget and
CLI scope rejection, checkpoint restart without another send, and absence of
downstream specialist invocation. No paid model or alternative LLM transport
was introduced.

| Fresh assessment, not a replay | Observed outcome |
| --- | --- |
| Configuration-only N01/UC02 `GROQ-DEV-3aaa3e576c1d440495cd683e545448ca` (checkpoint `groq_dev_checkpoint_6ed96c1e6db44f88`) | Configuration inspected only `product:M18-P-N01` and returned a **completed, validated finding** with five exact product claims: `catalog_version`, `fulfillment_mode`, `is_active`, `is_sellable`, `product_id`. Receipt shows two reserved/returned sends. No Pricing, Fulfillment, Credit, Policy or Routing AI, no candidate; fixed Credit remained `unknown`, review `needs_revision`. |
| Integrated N01/UC02 `GROQ-DEV-7d9898ab709c4727920a17d8b814b905` (checkpoint `groq_dev_checkpoint_b0586b8b99f44ea9`) | All six AI stages completed **without a candidate**. Credit inspected only original `credit_profile:M18-C-N01` and returned a **validated finding**, citing `credit_status=Review`, `credit_limit=5000.00`, `fixed_commitments_fresh=false`, `risk_rating=High` and `unbilled_committed_amount=300.00`. No selected AR/payment evidence was returned, so no zero-balance or clearance claim was warranted. Fixed Credit remained `unknown`, review `needs_revision`; original-only review was present. |

**Business example and authority:** the N01 deal's Review customer has stale
commitments and no selected transaction rows in this synthetic UC02 source.
AI reported the returned profile facts; fixed rules still could not determine
Credit, and neither a candidate nor a deal approval, waiver or delivery promise
followed. Offline UC02 can validly abstain; the hosted Credit finding here is
**not an abstention**. The complete discoverable Phase 2 suite passed on five
newly isolated business and three newly isolated checkpoint PostgreSQL
databases: **340 run, 340 passed, 0 failed, 0 skipped**. CI is a separate gate.

**Remaining exit gates:** the historical HC03 Configuration terminal rejection
and intermittent Fulfillment HTTP 400 still lack a demonstrated cause. These
two fresh runs did not reproduce either failure, but cannot establish runtime
repeatability. Hosted incomplete-evidence Credit *finding* is demonstrated;
hosted incomplete-evidence **abstention** is not. Independently accepted
evaluation answers and predeclared comparisons are still required before
accuracy or production-readiness claims. Preserve original/candidate isolation,
fixed verification, private receipts, no unsafe replay and human approval.

## UC02 scalar-only Configuration contract review — 31 October 2026

**Exit recommendation: C — keep M2.1 open.** The dated hosted results below
remain unchanged. The UC02 `claim_value_type` label shows only that at least
one decoded model claim had an unsupported JSON type. It does **not** retain
which claim, field, type or value was emitted; it does not explain the earlier
HC03 terminal rejection. No assessment was replayed.

**Confirmed interface ambiguity:** the terminal wire schema declares
`value_json` a string containing JSON, but deliberately cannot encode the
decoded claim's business-allowed type. The provider-independent semantic
validator accepts only exact returned strings, integers, booleans or null,
not floats, arrays or objects. The v3 Configuration instruction said “12 for
a number,” which could reasonably imply a JSON float; the actual B01/N01
inspection exposes `configuration_json` and `attributes_json` objects as
context although whole-object citations cannot pass the validator. This is
a real instruction/source mismatch, **not proof** that the UC02 model cited
one of those fields or that the earlier HC03 error had the same cause.

The Configuration-only terminal instruction is now
`groq-configuration-terminal-system-v4-scalar-only`: it names the four
permitted decoded types, excludes float/array/object values and whole
configuration/attributes objects, keeps exact `value_json` quoting and a
legitimate abstention. It is versioned and manifest-hashed automatically;
the generic terminal schema, fixed rules, evidence-binding and strict
acceptance validator are unchanged. The sanitized rejection classifier is
now `typed-final-rejection-v3`, distinguishing only `float`, `array` or
`object` **type categories** on rejected claims. It stores no path, raw
field/value, provider body or free-form prompt and cannot reclassify earlier
receipts. Tests cover bool/string/int/null acceptance, float/array/object
rejection, B01/N01 exact refs and no invented or cross-subject claims.

**Hosted gate:** the current guarded development CLI has no
Configuration-only specialist mode. The general typed-final development
gate accepts Pricing (which sends Configuration **and** Pricing), while the
M2.0 gate requires both Configuration and Pricing models. Sending through
either is not the requested one-case Configuration-only diagnostic; adding
a new hosted capability solely to force a trial would expand the trusted
authorization/manifest surface. Accordingly **no new hosted Configuration
probe or integrated UC02 assessment was sent**. A targeted new assessment
must wait for a separately tested, bounded Configuration-only guard or an
equally narrow predeclared diagnostic. Previous RC01/HC03 integrated success
does not prove the v4 prompt improves Configuration runtime reliability;
hosted incomplete-evidence Credit abstention remains **not demonstrated**.
Historical intermittent Fulfillment HTTP 400 and independent accepted
Phase 1C answers remain open. The **complete discoverable Phase 2 suite**
passed on five newly isolated business and three newly isolated checkpoint
PostgreSQL databases: **338 run, 338 passed, 0 failed, 0 skipped**. This is
local testing; GitHub Actions status was not verified here.

## Configuration diagnostic and fresh integrated follow-up — 31 October 2026

**Current disposition remains C: keep M2.1 open.** The original exit table
below is a dated snapshot of the *first* HC03 attempt; the fresh outcomes
here do not retroactively change its receipt or reveal its exact error.

- **Historical HC03 receipt:** the inspection returned exactly
  `product:M18-P-N01`; the fixed Configuration finding was `confirmed`.
  The terminal HTTP exchange had a reserved attempt and an allowlisted
  `terminal_semantics_or_evidence` rejection, with no validated final.
  RC01 Configuration succeeded on the same prompt, tool and product field
  types with a different original-subject ref. The old category covers
  multiple possible malformed/evidence cases, so no particular raw response,
  prompt failure, model intent or provider defect can be inferred.
- **Confirmed *diagnostic* gap, not a proven prompt cause:** the parser's strict
  allowed types and evidence checks were sound, but distinct parseable errors
  all received the catch-all category. The versioned
  `typed-final-rejection-v2` classifier now labels only rejected schema
  versions, duplicated claim pairs, unsupported JSON claim value types and
  malformed finding uncertainty arrays. It stores only a category, not a
  provider body, evidence value or unrestricted prompt. The terminal schema,
  Configuration prompt v3 and acceptance validators did **not** change.
  B01/N01 offline tests bind to their actual pinned product refs and check
  true/false booleans, invented and cross-subject citations, valid abstention,
  malformed terminal output and a returned JSON configuration object that is
  **not** an allowable scalar claim. This object is one plausible source of a
  future type mistake, **not** evidence of what any historical model emitted.
- **Offline final run:** complete Phase 2 local discovery on five fresh
  isolated business and three fresh checkpoint databases: **338 run, 338
  passed, 0 failed, 0 skipped**. This includes three earlier integrated
  synthetic overlay cases and two new focused Configuration contract tests.
  No paid model call. CI must be checked separately.

| Fresh assessment, never a replay | Exact observed result |
| --- | --- |
| HC03/N01 `GROQ-DEV-6e932d797d90493fb84eefbf8b41dddb` | All six AI stages **completed** without a candidate. Configuration cited exact original product values; Fulfillment completed without proposing a fixed candidate. Credit inspected exact original profile/AR/payment and validated `credit_status=On-Hold`, `credit_limit=1500.00`, `fixed_commitments_fresh=true`, AR `outstanding_amount=900.00` and payment `paid_amount=300.00`. Fixed Credit remained `infeasible`, review `blocked`, and the original-only review was present. No hold was waived, credit cleared or deal approved. |
| UC02/N01 `GROQ-DEV-70aacc939c0c4ab79e3352303fe88237` | Pinned source preflight established stale commitments, no selected AR/payment, fixed Credit `unknown`, review `needs_revision`. Configuration inspected `product:M18-P-N01` but its terminal response failed the new safe `claim_value_type` category; no downstream Pricing, Fulfillment, Credit, Policy or Routing AI ran, no candidate was created and no final was replayed. This category proves at least one parsed claim value was outside the strict primitive types; it does **not** identify the value, its field or the old HC03 error. |

**Gate assessment by dimension:** the hosted held/overdue **no-candidate**
path is now demonstrated once; the RC01 fixed-checked candidate path remains
demonstrated once. Hosted **incomplete-evidence Credit uncertainty or
abstention is still not demonstrated** because UC02 stopped upstream. Offline
UC02 did validly abstain, which is not a negative Credit outcome. One
successful HC03 and one different Configuration failure on the same N01
product evidence show runtime variability, not statistical reliability.
Neither fresh run reproduced Fulfillment HTTP 400; its historical intermittent
failure remains unresolved. Fixed-rule, original/candidate, read-only tool,
private receipt, no-replay and human approval boundaries remained intact.
Formal accuracy still needs independently accepted Phase 1C answers.

**Stop rule applied:** no further N01/UC02 hosted send without a specific
source-supported Configuration fix or diagnostic method. A next iteration may
review a *versioned* scalar-only guidance change and an offline exercise of
its prompt hash, while keeping valid abstention and the strict parser; do not
assert that JSON objects caused UC02 or alter the acceptance validator to
make the model pass. Only then consider one new UC02 integrated attempt.

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
