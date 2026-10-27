# Isolated Groq compatibility probe — successful basic inference and local tool call

**27 October 2026.** Ali authorized only
`GROQ-CONTRACT-PROBE-85c63f16-0c5b-4c24-bea4-1d1b79adea71` for two sequential
POSTs, at most 1,536 configured completion tokens combined and 2,048 request
bytes per send. This authorization is **spent**. Both requests used the frozen
offline-built wires in [the compatibility plan](groq-inference-compatibility-and-probe.md)
and `openai/gpt-oss-120b`; no deal data, business actions, B01 replay,
campaign, fallback, retry, or account/billing changes occurred. Stage 2 ran
only after stage 1 returned a valid completion and usage. A sanitized model
metadata preflight passed. The account was the existing Free/billing-disabled
account confirmed for this probe; the probe did not alter those settings.

| Stage | HTTP observation | Request / configured cap | Validated response | Elapsed | Provider-reported tokens (prompt + completion = total) |
| --- | --- | --- | --- | --- | --- |
| Plain chat | Successful HTTP 2xx path; **exact status not retained** | 135 bytes / 512 | One `chat.completion`, nonempty content, `finish_reason=stop`, no tool call | 869 ms | 74 + 25 = 99 |
| Harmless local tool | Successful HTTP 2xx path; **exact status not retained** | 584 bytes / 1,024 | One `chat.completion`, `finish_reason=tool_calls`, exactly one valid `record_probe(status=ready)` call; **tool not executed** | 587 ms | 145 + 38 = 183 |

**Total:** exactly two POSTs, 1,536 configured completion tokens, 219 prompt
+ 63 completion = **282 reported tokens**. These are per-stage launcher
elapsed times, not a complete deal-assessment latency measurement. The
successful HTTP code itself was not persisted by the transport, so a recorded
HTTP 200 must not be claimed. Neither success establishes why the replacement
B01 decision returned HTTP 400 or what caused the first closed B01 failure.
No Fulfillment five-tool decision, structured final, proposal, fixed candidate
verification, reviewer handoff, or comparative quality outcome was exercised
by this probe.

## Audit and boundaries

The new owner-only `0700` probe directory
`/tmp/opencode/dealdesk-groq-compat-probe-reservations` contains one fsynced
`0600` consolidated journal and two distinct `0600` per-send receipts. Each
receipt matches its prepared request digest and contains `reserved` followed
by `returned`. Raw successful responses are retained only as `0600` files in
`/tmp/opencode/dealdesk-groq-compat-probe-private`, alongside the private
one-shot launcher; none is committed or reproduced here. Historical campaign
receipts were neither sent nor modified. The offline builder, compatibility
tests and approved plan were previously validated with a fresh isolated
PostgreSQL regression (219 tests, 212 passed, seven unrelated Gemma diagnostics
skipped); this **provider-only** probe ran no new PostgreSQL or CI gate.
GitHub CI for this result is unverified. There is no measured accuracy or
Fulfillment delivery outcome from these two harmless requests.

## Smallest next *separately authorized* Fulfillment contract test

Prepare **offline first** an exact `GroqHybridTransportModel.request_decision`
wire for one newly identified, eligible synthetic assessment (not either
historical B01 identity or wire), using its frozen pinned evidence pack,
authorized tool list and a fresh immutable assessment/start identity. Inspect
the wire digest, source fingerprint, bytes, five function definitions, 512
configured completion cap and permitted output parser before requesting any
hosted permission. If that offline gate passes, propose **one** bounded
decision-only POST with a fresh fsynced reservation; persist sanitized status,
usage and whether exactly one permitted action parses. **Do not execute a
selected evidence tool, request a structured final, construct a candidate,
replay B01 or run multiple cases.** If the service rejects it, save only a
safe error classification under an explicitly reviewed diagnostic plan; do
not infer the cause from HTTP status. The plain/tool probe authorization does
not cover this test or any additional hosted inference. Prioritize Week 1
Fulfillment gaps and Week 2 Configuration/Pricing work after this narrow
contract gate, not another ten-case campaign.
