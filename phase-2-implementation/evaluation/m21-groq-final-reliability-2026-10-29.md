# Groq six-stage reliability investigation — 29 October 2026

**Scope:** six fresh B01/B05 original assessments under the approved Option A
runner: four previously recorded in [candidate continuation](m21-original-after-candidate-live.md)
and two new cases here. This is a small convenience sample, not an accuracy or
provider reliability estimate. No terminal assessment was replayed.

| Outcome (assessment-level, mutually scoped) | Observed / 6 |
| --- | ---: |
| All six stages executed (including valid abstention) | 3 |
| All six AI contributions validated as findings/proposals | 0 |
| Credit legitimate *contract-valid* `model_uncertainty` abstention after evidence inspection | 3 |
| Provider Fulfillment HTTP 400, no later AI stages | 3 |
| Locally rejected structured output or evidence validation | 0 observed |
| Fixed-checked Fulfillment candidate, original-only M2.1 continuation | 3 |
| No candidate because Fulfillment stopped at HTTP 400 | 3 |
| Completed six-stage workflow without candidate | 0 observed |

New B01 `GROQ-DEV-d887f5e9e35a46febaf2aaa0f72d3a93` and B05
`GROQ-DEV-efd18fd5b9de47769b41fdd1eb115eda` both completed the six
original-subject stages: Configuration, Pricing, Fulfillment, Policy and Routing
validated; Credit abstained with `model_uncertainty`. Both have distinct
fixed-checked candidate records, `supply_supported_unreserved` but
`needs_revision`, withheld Routing and pending customer acceptance. The
original remains `needs_revision`. Neither candidate is approved or reserved.

## Wire and evidence findings

- Fulfillment's decision request offers permitted tools; after the completed
  `inspect_fulfillment_paths` read, the final request is a *new* two-message
  system/user request **without tools**. It uses `response_format=json_schema`,
  `strict=true` and `openai/gpt-oss-120b`. Unlike M2.1's terminal request, it
  does not carry prior assistant/tool messages. The exact binding schema is
  closed at every object depth and all properties are required. [Groq's
  documentation](https://console.groq.com/docs/structured-outputs) lists
  this model as supporting strict mode. These facts do **not** establish the
  cause of the intermittent 400; successful finals use the same schema.
- The new successful final receipts record the same strict-schema SHA-256
  `4d9077a08f5b1129a83ca05b434a84b9eae1dfa22440332fa4ceb674ca0977f6`
  with request lengths 9,883 (B01) and 9,888 (B05) bytes. Earlier failing
  receipts predate the bounded wire metadata, so their request sizes and
  schema hashes cannot be recovered from saved receipts. No earlier HTTP 400
  yielded an allowlisted provider category. Status alone cannot distinguish
  malformed request, constrained decoding or another provider-side cause.
  New attempts persist only phase, byte length and schema hash alongside the
  existing request digest, never prompts, raw error text or credentials.
- B01's returned credit profile exposed exact fields including
  `credit_status=Active`, `risk_rating=Low` and
  `fixed_commitments_fresh=true` with a dated commitments reference. Its
  model returned a valid abstain tool call, not an invalid claim or local
  rejection. The new B01/B05 runs likewise inspected a profile and abstained.
  Citeable fields existed, but checkpointed receipts cannot reveal why the
  model did not select one; a cautious abstention remains legitimate. A
  bounded, versioned Credit-specific prompt experiment against fresh cases
  could test whether this is avoidable, without forcing a finding or changing
  credit rules. Do not count abstentions as six validated findings.

**Offline gates:** 85 focused tests run, 83 passed and 2 skipped on a fresh PostgreSQL checkpoint
before hosted sends, plus replay and final-receipt checks after the metadata
change. Tests assert strict-schema object constraints, tool-to-final request
shape, bounded error metadata, old-checkpoint replay and tamper/no-replay
continuation. Remaining blocker: safely obtaining an actual provider error
category on a *fresh* failed final; previous responses have no usable one.
