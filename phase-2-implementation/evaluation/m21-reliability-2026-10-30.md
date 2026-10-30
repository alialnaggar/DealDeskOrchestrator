# M2.1 reliability continuation — 30 October 2026

**Development-only sample; not formal evaluation.** The eight fresh B01/B05
assessments in [the earlier follow-up](m21-credit-and-fulfillment-reliability-followup.md)
are retained unchanged. One additional fresh B01 assessment
`GROQ-DEV-213b41bb2dbb4dcf810032fdce9c3697` reached Configuration and
Pricing, then stopped **before the Fulfillment decision send** at the Groq
coordinator's `groq_daily_limit`. Its Fulfillment receipt is an error at phase
`decision` with 5,071 serialized request bytes and **no final schema hash**.
This is not HTTP 400, not a Fulfillment strict-schema failure and not a Credit
abstention. No candidate or M2.1 continuation was created. Do not replay it.
The coordinator then reported an approximately 15-hour daily block; no further
hosted sends were made.

| Distinct outcome across nine fresh original B01/B05 assessments | Count |
| --- | ---: |
| Completed six-stage workflow | 4 |
| Six validated AI contributions | 0 |
| Credit inspected evidence and contract-validly abstained (`model_uncertainty`) | 5, including one later Routing failure |
| Fulfillment provider HTTP 400 | 3 |
| Routing provider HTTP 429 | 1 |
| Local Groq coordinator daily limit before Fulfillment decision send | 1 |
| Observed local structured-output / evidence-validation failure | 0 |
| Fixed-checked candidate | 5 (4 completed workflows; 1 later Routing failure) |
| No candidate | 4 (3 HTTP 400; 1 local daily limit) |
| Completed workflow without candidate | 0 |

## Credit and wire findings

The committed Credit `credit-observation-v1` final had not been reached on the
new run. Inspecting the exact instruction found that v1 appended Credit guidance
to a shared final containing **Pricing-specific instructions** on which fields
to cite and when to abstain. That is a plausible source of prompt ambiguity,
not a demonstrated cause of the five valid Credit abstentions. A distinct
`credit-observation-v2` instruction now provides only Credit-specific exact
alias/field/value guidance, protects against confusing an observed status with
credit clearance, and retains abstention for uncertain evidence. The shared
Pricing instruction and all schema/claim/fixed-rule validators are unchanged.
V2 is **offline tested only**; no improvement claim is made until fresh hosted
cases run after normal quota restoration.

The existing B01 selected credit projection exposed an `Active` credit status,
`Low` risk rating, fixed freshness and a dated commitments reference; its
model-visible projection redacts the customer and commitment identifiers. The
recorded abstentions are contract-valid, not local output failures. A profile
field being citeable does not itself prove that the underlying credit evidence
is sufficient for a clearance decision. The pinned B01 tool result contained
only a profile, without receivable or payment rows. **Phase 1C handoff
question:** when expanding synthetic cases, document whether empty selected
receivable/payment sets mean an explicitly complete zero-record snapshot or
an unknown/incomplete source. This is not a claim that incomplete evidence
caused the model's abstentions and does not authorize inventing records or
changing credit thresholds.

No new Fulfillment final HTTP 400 carrying the bounded metadata exists. The
previous successful final requests used the same strict-schema hash; their
similar byte counts do not establish the cause of the older failures. The
runner now reports allowlisted Fulfillment error code, phase, request byte
count and hex schema hash separately, never arbitrary provider text. These
fields are **diagnostics**, not validation relaxations. The local quota stop
shows why a stopped campaign must not automatically be classified as a
provider HTTP failure.

Offline regressions use fresh PostgreSQL checkpoints and mock models; formal
comparison against independent expected answers still waits for an approved
Phase 1C release and explicit handoff. The Phase 1C pin is unchanged. No
hidden answer keys were exposed to any agent or model.

The final focused offline PostgreSQL/LangGraph suite ran **94 tests: 92 passed,
2 skipped**, including candidate/no-candidate continuation, tamper checks,
no-replay and strict typed-final tests. GitHub Actions status was not verified
locally (`gh` is unavailable); the local suite is not a CI result.
