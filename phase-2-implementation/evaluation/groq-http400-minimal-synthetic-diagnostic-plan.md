# Minimal synthetic Groq second-turn diagnostic — offline-only design

**PAUSED after owner-supplied Console evidence.** Four Console HTTP 400 entries
are labeled `tool_use_failed`; the [offline reassessment](week3-groq-console-tool-use-failed-reassessment.md)
prioritizes per-row account/time/token semantics and provider support over
this generic matrix. Nothing here authorizes a trial or matrix progression.

**28 October 2026; no hosted access authorized.** This is a *proposal*, not
an executable campaign or approval record. The [four-failure official-docs
review](week3-groq-http400-official-docs-offline-review.md) found correctly
paired second turns in two terminal Pricing and two terminal Credit attempts,
versus accepted Configuration twice and Fulfillment once. All seven used
`tool_choice=required`, named tool-result messages and the same model/512-token
cap. `name` and `required` are **not universal failure conditions**; a
request-dependent interaction with the prompt, tool definitions, evidence or
Groq generation/validation remains unresolved. The old paired receipts and
assessments must never be reopened for sends.

## Synthetic two-turn control, no deal or answer-key data

`backend/tests/groq_http400_offline_design.py` builds **in-memory mock wire
dicts only**. No endpoint, credentials, runtime hook or live sender exists.
The first request uses `system → user`, model `openai/gpt-oss-120b`,
`temperature=0`, `parallel_tool_calls=false`, `max_completion_tokens=512`,
`tool_choice=required`, and two local function definitions:
`inspect_synthetic_record(record_key="SYN-1")` and
`submit_synthetic_result(result=string)`. The fictional observation is only
`{"record_key":"SYN-1","signal":"amber"}`. It contains no deal lines,
customer IDs, protected evidence, fixed findings or evaluation answers.
Both schemas are small JSON objects, with required properties and
`additionalProperties=false`.

For mock continuation tests the fixture inserts a **clearly fake** tool-call
ID and a JSON-string tool result to test the exact
`system → user → assistant(tool_calls) → tool(tool_call_id)` structure.
**A future real second turn must instead use the actual accepted first-turn
provider call and matching ID. Never submit the fake test call ID.** A real
future trial must stop if its first response lacks one valid permitted call or
usage, or if the local inspection cannot complete; no artificial assistant
history may be fabricated to force a second POST. A 2xx response to
`tool_choice=auto` that contains prose instead of a tool call is informative
about HTTP acceptance, **not** a validated specialist finding.

## Conditional decision matrix — one changed factor per comparison

| Stage (at most two sequential POSTs **per separately authorized fresh identity**) | Paired comparison | Information gained; next decision |
| --- | --- | --- |
| **0 — before any inference** | Ask Ali to inspect existing account Console history if it offers safe request-level errors, or ask Groq support whether an error can be located by account/time/model without sharing private prompts or keys. | If a specific provider category/field is safely available, review it first. A local request-body SHA-256 is **not** a Groq request ID. Stop without hosted testing if this resolves the question or safe lookup is unavailable and the cost/risk is not worthwhile. |
| **A — synthetic baseline, only if separately approved** | Named result, **simple** schema, neutral observation, `required`. Two turns only if first native tool call succeeds. | If A returns 400, the problem can occur without Pricing/Credit evidence or a complex schema; inspect allowlisted category. If A succeeds, the generic message structure/name/required combination works under a third minimal context; do **not** claim historical causes ruled out. |
| **B — only if A's continuation fails and more information is approved** | Identical A request except **omit `name` from the tool-result message**. | If B succeeds, the contradictory Groq `messages[].name` documentation is a **context-dependent suspect**, not a proved cause of historical failures (accepted controls used `name`). If B also fails, name is not sufficient to explain A; consider `tool_choice` comparison E or support, not a bulk matrix. |
| **C — only if A succeeds and further isolation is approved** | Identical A except **replace only the submission function's simple parameters** with a small nested required array/object schema. Keep name, neutral content, `required` and all other wire fields. | If only C fails, inspect schema/tool-generation interaction; complex schema is a suspect, not proof of an invalid historic schema. If C succeeds, compare D only if still justified. |
| **D — only if C succeeds and further isolation is approved** | Identical C except change **only the fictional tool-result content** to `{"record_key":"SYN-1","margin_band":"review","credit_band":"review"}`. No real business evidence or amounts. | If D alone fails, domain-like language/content interacting with generation is a suspect. If D succeeds, the synthetic contrast did not reproduce Pricing/Credit failures; stop and prefer provider-side help over increasingly realistic data. |
| **E — optional only after an otherwise identical failed continuation, separate approval** | Rebuild **that same failed synthetic scenario** with only second-turn `tool_choice` changed from `required` to `auto`; keep first turn identical and use its own returned call ID. | If the `auto` continuation is accepted while `required` fails, this supports a *forced tool-generation* mechanism consistent with Groq's guide, but cannot identify the historical prompt/schema trigger. If both fail, pursue provider-side evidence. Do **not** silently switch production tool choice or treat prose as a finding. |

Only A is a candidate for first hosted authorization **after** stage 0. B/C/D/E
are mutually conditional next decisions, not a pre-approved set or full
factorial experiment. The longest justified branch is A → C → D → E (**four
independently approved identities, at most eight POSTs in total over separate
future authorizations**). Live paired trials cannot hold stochastic model
output or provider-issued tool-call IDs constant across fresh identities:
"one factor" means one *planned wire setting* changes, not identical
second-turn bytes or a causal guarantee. Save only permitted digests and
allowlisted outcomes for comparison; do not manufacture matching replies.
Stop earlier when the outcome is informative or inconclusive and support is
more useful. Each assessment stops on any first-
or second-turn error, invalid native call, budget failure, missing usage or
uncertain reservation; an error never authorizes retries or automatic
progression to the next row. No batch, fallback credential, hidden evaluation
answer, business agent or real customer evidence is included.

## Proposed revised bounded error-retention contract (NOT active)

The spent Credit diagnostic was authorized to inspect **at most 1,025**
error bytes; it retained only `http_400`. The official error example includes
free-form `error.message` and `error.type`; an otherwise valid response with
a long message can exceed the old 1,024-byte full-JSON limit. The test-only
draft parser proposes a **4,096-byte body ceiling plus one overflow-detection
byte**, reading bounded chunks until EOF, so a short socket read does not
mistakenly make JSON look truncated. If it fits, parse the entire JSON and
keep **only** previously enumerated `type`, `code`, `param` values. Never
persist or log `error.message`, raw bytes, exception text or unknown strings.
Persist at most one **fixed local status** (`oversize`, `malformed`,
`read_timeout`, `parsed_unrecognized`, `parsed_allowlisted`) and only
recognized provider values; this distinguishes loss mechanisms **without
revealing the body**. Bodies beyond 4,096 bytes still reveal no provider
fields. No parser failure may hide the original HTTP status or cause a retry.

Inspect **only** the allowlisted header `x-request-id` for an exact lowercase
UUID, independently of JSON parsing, if present. The public Groq Chat API
example includes `x_groq.id` in a successful JSON body with a `req_...`
format, **not a documented failed-response header**. Do not accept `req_...`
from arbitrary headers, persist `x_groq`, or expand any ID grammar until an
official failed-response header contract and privacy review justify it.
Unknown/header-free responses remain unclassified. Header values must never
be logged wholesale.

The offline draft and tests are *not* an approved implementation. A future
revision to the shared transport, receipt schema or retention limit would
need security review, schema-validated owner-only persistence, mocked
success/error/crash/no-replay tests, a fresh isolated PostgreSQL regression
and **Ali's explicit consent to the changed retention contract**. Existing
receipt identity, original HTTP status, request digest, elapsed time, and
terminal/no-replay controls remain immutable. Do not backfill old failures;
their response bodies were never saved.

## Authorization gate for *each* hypothetical hosted attempt

This document allocates **no** real assessment IDs or approval files.
Before any one case is sent, create a **new** synthetic assessment UUID,
new empty owner-only directory and fixture/checkpoint pair; pin source and
confirm actual database targets if using the M2.1 runner, or provide a
separately reviewed no-business-data harness. Freeze a manifest with exactly
one stage/factor, model `openai/gpt-oss-120b`, selected existing secondary
credential only, at most **two sequential POSTs**, **512 configured
completion tokens** and **8,192 serialized request bytes** per POST, one
synthetic inspection, a fixed reported-token post-send stop, no metadata
requests unless explicitly authorized, no retries or fallback. Have Ali
approve **that exact manifest hash**, confirm the chosen account is Free-tier
with paid billing disabled and separately approve any changed diagnostic
retention. Only after source/isolation/budget/credential checks may an
owner-supplied private hash-bound approval record be created. Durable
reservation precedes each send; a reserved-only, failed or uncertain receipt
never permits replay. Stop and report after each case; an approval for A is
not approval for B/C/D/E. No previous terminal identity may be reused.

Offline mock tests verify all five one-factor wire constructions, bounded
parser behavior for long messages/partial reads/oversize/timeout/malformed
data, strict headers and absence of arbitrary provider text. Focused offline
suite passed **31/31** (including existing transport and M2.0/M2.1 wire tests).
No production implementation changed, so no fresh PostgreSQL regression was
required. There was **no hosted request** from this plan.
