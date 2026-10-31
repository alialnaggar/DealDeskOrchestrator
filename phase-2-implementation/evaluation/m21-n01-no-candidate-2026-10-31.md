# M2.1 no-candidate development assessment — N01

**31 October 2026.** The existing pinned Phase 2-only disposable N01 fixture
has a fixed `late_alternative` Fulfillment shortage and explicitly
`allow_partial_delivery=false`. N02/N04 are fixed-infeasible and N03 has
unknown/stale supply, so they do not exercise the same eligible six-stage
Fulfillment investigation. N01 was narrowly added to the existing standing
free-tier development case/subject allowlists; model, tool permissions,
business rules, Phase 1C pin, manifest identity and budgets are unchanged.

A fresh synthetic assessment `GROQ-DEV-301c8dfe9fc545deb911b75d4b779d7a`
used separate disposable business/checkpoint PostgreSQL databases. All six
real Groq AI contributions completed and passed validation. Fulfillment read
the pinned inventory, inbound and lane/path evidence and returned a bounded
**finding without a binding proposal**. No candidate record was created.
Credit read only the N01 original profile and cited six exact returned fields
(`credit_status=Active`, `credit_limit=1000000.00`, fixed commitments freshness,
`risk_rating=Low`, unbilled commitments and the as-of timestamp). This is an
observation, not approval or credit clearance. The original fixed result still
`needs_revision`; Routing remains withheld, human review remains required and
no customer delivery promise was made.

The successful Fulfillment final was 9,884 bytes with strict-schema SHA-256
`4d9077a08f5b1129a83ca05b434a84b9eae1dfa22440332fa4ceb674ca0977f6`.
**No HTTP 400 occurred.** Earlier 400s have neither comparable failed-request
metadata nor a usable allowlisted provider category, so their cause remains
unknown. One new no-candidate run demonstrates a governed path; it does not
establish a general no-candidate completion rate.

## Outcome counts across 12 fresh B01/B05/N01 assessments

| Separately measured outcome | Count |
| --- | ---: |
| Complete six-stage workflows | 7 |
| Workflows with six validated AI contributions | 3 |
| Contract-valid Credit `model_uncertainty` abstentions | 5 (one in a later Routing failure) |
| Fulfillment provider HTTP 400 | 3 |
| Routing provider HTTP 429 | 1 |
| Local daily limit before Fulfillment decision send | 1 |
| Observed local structured-output or evidence-validation failure | 0 |
| Fixed-checked candidate / no candidate | 7 / 5 |
| Complete workflow with no candidate | 1 |

The Credit evidence is **not diverse in the hosted cases**: all nine M18
source cases clone the same profile and have no selected receivable or payment
rows. The existing pinned `CREDIT-LIMIT` conflict pilot contains one selected
receivable, zero payments and fixed Credit infeasibility; it is not provisioned
by the current six-stage disposable runner. Offline v2 tests exercise an
aliased profile plus receivable/payment, verify exact AR citation, and permit
`insufficient_evidence` abstention for a completed but empty returned pool,
while rejecting an invented AR claim. These are *scripted contract tests*,
not real-model evidence that Credit v2 reasons correctly over a hold or AR.
A narrow, separately reviewed fixture/adapter is needed for a diverse hosted
Credit trial; never mutate the Phase 1C pin or infer that empty AR proves
zero exposure. Independently accepted answer keys and formal accuracy claims
await Phase 1C release/handoff.

Before the hosted assessment, the fresh-checkpoint PostgreSQL suite ran
**106 tests (104 passed, 2 skipped)** including a six-stage mocked N01
no-candidate continuation. No terminal/uncertain sends were replayed. The
final offline regression after the additional Credit pattern test is recorded
here: **107 tests (105 passed, 2 skipped)** on a fresh PostgreSQL checkpoint.
Private CI status was not verified from this environment. Further identical
hosted attempts were stopped as low diagnostic value.
