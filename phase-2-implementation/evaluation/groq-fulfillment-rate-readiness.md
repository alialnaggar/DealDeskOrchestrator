# Groq development pacing and Fulfillment shared-ledger follow-up

**29 October 2026 · offline verification only.** Continues the
[six-specialist development follow-up](groq-six-specialist-development-followup.md).
The historical HTTP 429, malformed Fulfillment contribution and native HTTP
400 remain stopped assessments. No earlier reservation was replayed or
retrospectively relabeled as a successful model output.

## Changes and scope

- Fulfillment binding proposals and claim validation now ignore completed
  Configuration/Pricing tool entries when scanning the *shared original*
  checkpoint ledger. Only tools in the existing Fulfillment permission registry
  can furnish Fulfillment evidence. Any event using a Fulfillment tool with a
  mismatched Fulfillment identity still raises an identity error; cited records
  must have been returned to that specialist for the exact line and run. No
  Phase 1C business rule, source authority, quantity or date test was relaxed.
- The opt-in **Groq development-only** coordinator scopes to the Groq chat
  endpoint, bearer Authorization, `openai/gpt-oss-120b` and
  `DEALDESK_GROQ_DEV_ENABLE=1`. It uses an owner-only per-account/model file
  and an OS file lock held across each send. A bounded conservative token
  estimate and the request are charged durably before POST; after a successful
  response, validated usage replaces the estimate. Only allowlisted numeric
  rate-limit headers and reset durations are interpreted; raw headers, API
  key, request/response text and provider error body are never written to the
  coordinator file. A 429 stops the current attempt without retry. Unknown
  429 reset information blocks new sends conservatively for 24 hours; a
  known reset/retry interval is honored with at least 60 seconds of spacing.
  The assessment's checkpoint and receipt, not this shared pacing file,
  remain authoritative for no-replay and terminal status.
- The coordinator is **not** a provider quota oracle, cost guarantee or
  automatic fallback. Rates can vary by organization and time. The configured
  account ID is owner-supplied and is not cryptographically bound to the key;
  other processes outside this coordinator or different account labels do not
  share its counters. An observed HTTP 429 on a stopped assessment must not
  be retried, and no new trial should begin until the owner confirms ordinary
  quota availability. This work neither enables paid billing nor changes the
  production terminal-tool default.

## Validation and remaining output failure

Fresh seven-database PostgreSQL regression: **352 tests, 7 skipped**, including
the mocked six-specialist LangGraph sequence. Dedicated offline tests cover
Fulfillment's cross-specialist ledger filtering and forged Fulfillment
identity denial, header allowlisting without reading HTTP error text, 429
stopping behavior, minute/day budget accounting, per-organization
serialization in threads and separate processes, and an interrupted send's
durable charge. No model API was called by these tests.

The historical Fulfillment `identity_mismatch` may have been caused by the
shared-ledger bug; that is a hypothesis, not a live confirmation. The separate
`malformed_contribution` and native HTTP 400 are **genuine unresolved output/
transport failures**: no safe deterministic repair follows from their coarse
categories. The validator still rejects a wrong line, malformed payload,
unreturned citation and unsupported binding schedule. A fresh trial plus
private, bounded validator-category review is necessary to determine whether
the prompt, serializer or model output must change; do not coerce malformed
outputs into findings or normalize business quantities/dates. The previous
provider 429 is a Groq quota observation, not evidence of an OpenACP limit.

No normal provider quota reset was independently verified in this session;
therefore **no fresh real-Groq assessment was started**. The OpenACP execution
limit reported for the prior interrupted execution did not recur during this
offline work. Private CI status was not inferred from local tests.

## Bounded prompt follow-up (29 October 2026)

The retained rejected Fulfillment binding payload used `tradeoff_code="none"`,
which is valid for a finding/abstention but not for an M1.7 binding proposal.
The versioned binding prompt now explicitly distinguishes those kinds and tells
the model to abstain or give a bounded finding when permission or binding
evidence is uncertain. The strict schema and business validator are unchanged;
the validator continues to reject `"none"` on binding proposals. On the
synthetic B01 shortfall, the model may suggest a two-slice delivery only after
reading an eligible binding path; fixed rules still verify each unit, source,
date and customer constraint, and no delivery is promised. The 71-test focused
offline regression (7 skipped without all fixture environment variables)
passed, including a fresh-checkpoint PostgreSQL six-specialist LangGraph
assessment using model doubles. No real-model success is inferred from that.

Normal Groq quota availability was not independently verified: the prior 429
retained no reset headers or identifiable quota type, and the new coordinator
has no history from that attempt. Do not use a fresh assessment to probe an
uncertain daily limit or replay any prior terminal assessment. The previous
OpenACP execution-limit message is separate from the provider's HTTP 429 and
did not recur. CI could not be inspected here (`gh` unavailable).
