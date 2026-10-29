# Credit and Fulfillment Groq reliability follow-up

**29 October 2026; bounded synthetic observations, not an accuracy claim.**
The earlier [six-case sample](m21-groq-final-reliability-2026-10-29.md)
is retained unchanged. Two additional fresh assessments used the free-tier
Groq coordinator; neither was replayed. No paid OpenAI request was made.

| Measure across eight fresh B01/B05 cases | Count |
| --- | ---: |
| Complete six-stage workflow executions | 4 |
| Six validated AI contributions | 0 |
| Credit inspected evidence and contract-validly abstained (`model_uncertainty`) | 5 (one in a later-stopped workflow) |
| Fulfillment provider HTTP 400, no candidate | 3 |
| Provider HTTP 429 at original Approval Routing, candidate kept separate | 1 |
| Locally rejected structured output / evidence validation | 0 observed |
| Fixed-checked candidates | 5 (four complete workflows, one later-stopped) |
| No candidate | 3 (all stopped at Fulfillment) |
| Complete workflow without candidate | 0 observed |

New B01 `GROQ-DEV-6e1fae6b892b467397261b95daf02e03` completed all
six original AI stages with five findings and a Credit abstention. New B05
`GROQ-DEV-ab1d81b4dcb74e09a1992a1e4ed5db4c` completed Configuration,
Pricing, Fulfillment, Credit (abstained) and Policy, but stopped on Routing
HTTP 429. The coordinator set a cooldown; **no further sends were made**.
Both candidates were fixed checked with separate exact-candidate rules; neither
was reserved, approved or customer-accepted. They still need revision and
human review. Original-only AI never upgrades the candidate.

## Credit investigation

The B01 profile returned a dated commitments reference, `credit_status=Active`,
`risk_rating=Low` and `fixed_commitments_fresh=true`. These are citeable
observations, not a credit-clearance conclusion. The model used its inspected
evidence and returned a valid `model_uncertainty` abstention, not a rejected
claim or missing data error. The original development final instruction
described exact scalar quoting but illustrated a finding only for Pricing.
We tested a versioned example that explicitly permits an exact-copy Credit
status observation while forbidding implied clearance, and leaves abstention
available. The two fresh hosted attempts still abstained. This is **no
demonstrated improvement**; no provider reasoning trace is saved, so the
specific reason for abstaining remains unproven. The final committed prompt
isolates that example to Credit rather than adding Credit text to Pricing;
that final isolation passed offline contract tests but has not itself had a
new hosted trial due to the 429 cooldown. Validators and credit rules were
not relaxed.

## Fulfillment investigation

The new B01 and B05 Fulfillment finals succeeded with identical strict-schema
SHA-256 `4d9077a08f5b1129a83ca05b434a84b9eae1dfa22440332fa4ceb674ca0977f6`.
B05's final was 9,888 serialized bytes (same as a preceding successful B05).
No new Fulfillment HTTP 400 occurred, so there is still **no failed request
with bounded byte count and schema hash** to compare. Earlier failures have
only HTTP status and no usable allowlisted diagnostic; neither schema
compatibility checks nor successful identical-schema requests prove the
cause. The strict schema, tool-to-final transition, provider adapter,
deterministic validations and no-replay controls remain unchanged. Do not
attribute 400s to schema or model generation without a safe provider category.

Before hosted sends, a fresh-checkpoint PostgreSQL/LangGraph suite ran
**93 tests: 91 passed, 2 skipped**. Focused final-contract tests additionally
passed after isolating the Credit guidance. Next: wait for normal quota,
compare a *new* failed final's bounded metadata if it occurs, and test the
isolated Credit prompt on fresh cases. Never resume terminal attempts.
