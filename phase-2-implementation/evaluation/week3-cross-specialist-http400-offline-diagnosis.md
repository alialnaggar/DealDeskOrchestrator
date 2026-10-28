# Week 2 Pricing and Week 3 Credit second-turn HTTP 400 — cross-specialist offline diagnosis

**28 October 2026; no provider request.** The three B01 HTTP 400 continuations
are terminal: original M2.0 Pricing, secondary-account M2.0 Pricing and
secondary-account M2.1 Credit. No checkpoint, request or receipt was replayed.
This is a *read-only* comparison of the actual frozen PostgreSQL checkpoints,
completed authorized tool ledgers and existing returned-call descriptors.
The older Pricing wire was rebuilt using the exact `m20_groq.py` source from
its historical commit `9e70046a67d7776aff40e6604c16462134ddfd42`;
the newer Pricing, Credit and accepted B05 Fulfillment wires used their
corresponding current contracts. Applying today's strengthened M2.0 prompt
to the first historical attempt produces **different hashes** and cannot be
substituted for its old request. In every comparison below the appropriate
builder's compact UTF-8 serialization equals the `_post` transport encoding,
and the first/second-turn SHA-256 matches its original pre-send reservation.
No raw body, customer identifier, credential or returned model text is
published here.

## What the saved requests and receipts establish

| Case / account / specialist | First turn (accepted), bytes | Second turn, bytes and result | Matched native continuation? |
| --- | ---: | --- | --- |
| M2.0 B01 first account, Configuration | 2,596 | 3,339; accepted | Yes; ID 39 characters |
| M2.0 B01 first account, Pricing | 2,573 | 3,377; **HTTP 400** | Yes; ID 39 characters |
| M2.0 B01 second account, Configuration | 3,006 | 3,749; accepted | Yes; ID 39 characters |
| M2.0 B01 second account, Pricing | 2,964 | 3,768; **HTTP 400** | Yes; ID 39 characters |
| M2.1 B01 second account, Credit | 2,910 | 3,814; **HTTP 400** | Yes; ID 39 characters, **redacted** result |
| Corrected M2.0 B05, Fulfillment | 4,810 | 7,252; **accepted** | Yes; ID 39 characters |

The first turns use `system → user`; every second turn above uses
`system → user → assistant(tool_calls) → tool(tool_call_id)`. The assistant
has `content: null`, exactly one function call, and the *same provider-issued*
ID in the assistant call and tool result. Each tool-result message has a
`name` equal to that specialist's inspection function; its `content` is a
JSON **string** of exactly the completed permission-ledger result (M2.1's
allowlisted aliased projection rather than the internal Credit record).
The first user message does **not** duplicate the completed tool result.
For all six second turns, the top-level fields are exactly `model`,
`temperature`, `max_completion_tokens`, `parallel_tool_calls`,
`tool_choice`, `tools`, `messages`; model is `openai/gpt-oss-120b`,
temperature is `0`, completion ceiling is `512`, parallel calls are `false`,
and tool choice is `required`. No `response_format` is mixed with tools.
All bodies are below the approved 8,192-byte limit. These are **local byte
and receipt facts**, not proof of server-side schema validation.

The **M2.0** request advertises its specialist's own `inspect_*_line`,
`submit_finding`, `abstain`. Both inspect functions accept one required
`line_id`; both submission schemas require `claims` and
`uncertainty_reasons` with the same structure. Configuration's accepted
continuation returns selected product evidence; Pricing's rejected one
returns selected price/list/cost and fixed-discount/margin evidence. The
**M2.1 Credit** request advertises `inspect_customer_credit_evidence`
(one required aliased `subject_id`), `submit_finding` (required `claims`, no
`uncertainty_reasons`) and `abstain`. Its rejected continuation carries one
allowlisted credit-profile record, not the raw customer ID. All listed
inspection and submission schemas have `additionalProperties: false`.
The successful **Fulfillment** continuation exposes a different, larger
inspector/proposal tool set and distinct task input; its paired four-role
conversation still shows the same model/512/required/false/0 controls, a
named tool result and no response format. It is a structural counterexample,
not a matched domain experiment.

The first Pricing case has a distinct earlier trusted system prompt, whereas
the second Pricing case used `m20-config-pricing-system-v2`; both failed on
the pricing second turn. Credit used `m21-original-system-v1`, an aliased
subject and a different submission schema, yet also failed at the same
*stage*. This recurrence is **consistent with a domain/returned-evidence or
forced-tool-generation interaction**, not evidence that one shared fixed
schema field or named tool message caused it. Neither the failed generation
nor its error detail was retained, so this is correlation, **not a diagnosed
cause**.

## Local Groq contract review and hypotheses

The repository's [28 October Pricing contract review](m20-pricing-http400-offline-diagnosis.md#28-october-2026--second-account-recurrence-and-byte-level-review)
records the then-checked [Groq local-tool calling guide](https://console.groq.com/docs/tool-use/local-tool-calling),
[OpenAI compatibility notes](https://console.groq.com/docs/openai),
[chat request reference](https://console.groq.com/docs/api-reference#chat-create),
[tool-use overview](https://console.groq.com/docs/tool-use/overview) and
[structured-output restriction](https://console.groq.com/docs/structured-outputs).
The [repository compatibility audit](groq-inference-compatibility-and-probe.md#official-documented-contract-versus-saved-wire)
also records the published GPT-OSS reasoning/temperature limits and a
later [successful basic tool probe](groq-contract-probe-result.md).
**These are previously recorded documentation observations, not a fresh
network lookup or proof that provider behavior has not changed.**

| Hypothesis | What can actually be concluded offline |
| --- | --- |
| Missing assistant/tool pair, bad call-ID linkage or string-vs-object tool result | **Rejected as a defect in these three saved failures.** Every failed body contains the correctly paired call and string content; the old *B05* unpaired follow-up was separately fixed and a new paired B05 was accepted. This does not rule out an undocumented provider validation nuance. |
| `messages[].name` is categorically unsupported | Local compatibility notes say `name` is unsupported, while the recorded local-tool example includes a tool `name`. All three failures **and** both accepted Configuration continuations and accepted Fulfillment continuation include it. It cannot explain why every continuation would fail; a context-specific effect remains unproven. **Do not remove on speculation.** |
| `tool_choice=required`, 512 completion tokens, zero temperature, `parallel_tool_calls=false`, shared API route or model is universally incompatible | **Rejected as a universal explanation** by accepted initial and second turns with the same controls. Groq's recorded guide says `required` may yield 400 when a tool is not produced; complex *particular* follow-ups could still fail at generation, but no failed output, token usage or category was captured. |
| Structured output mixed with local tools or oversized/invalid JSON transport | No `response_format`; all reconstructed JSON hashes match reserved bytes; sizes fit the ceiling. No such local protocol defect is shown. |
| Account or credential categorically unable to use the model | Both accounts returned first turns, and the secondary account returned a Configuration follow-up immediately before its Pricing failure and a Credit first turn before its Credit failure. Not a general access failure; request-dependent service failures remain possible. |
| Specific Pricing/Credit values, prompt, function schema or hidden server rule | Distinct differences between successful and failed domains; neither is isolated by a controlled counterfactual. Without a safe structured provider rejection category or service-side record, **unresolved**. |

The shared `_post` transports canonical JSON without a retry and, on HTTP
errors, records only `http_400` while deliberately **not reading** the
potentially sensitive error body. Receipts prove attempted sends and terminal
failure, not whether Groq rejected a field, failed forced tool generation or
applied some other rule. No provider-independent serialization, role/linkage,
budget or typed-schema defect in the **current saved failures** was found;
therefore **no speculative production wire, prompt, rule or budget change**
is justified. The original deals and fixed findings remain authoritative;
Credit/Policy/Routing hosted completion and Pricing's hosted finding remain
unproven. Never retry any existing terminal identity.

**Later metadata clarification:** The two M2.0 Pricing failures have durable
checkpoint reservations but no per-POST owner-directory failed receipt;
M2.1 Credit has both a checkpoint reservation and a `reserved → failed`
owner-only receipt. None has a saved Groq HTTP request ID or error category.
See [the read-only receipt inventory, conditional manual Console checks and
disabled diagnostic proposal](week3-groq-http400-response-metadata-and-proposal.md).

## Safe next diagnosis, not an authorization

First ask the account owner whether an **existing provider-side request
record** for one stopped POST contains a non-sensitive rejection category or
field path; this does not require sending or opening raw customer data. If
unavailable, propose a **separately approved**, source-first **new**
synthetic assessment with a fresh database/checkpoint/owner directory,
unchanged fixed-rule authority and at most two sequential POSTs (inspection
then follow-up only if inspection safely returns). Keep the original wire
unchanged for a controlled diagnostic. Before any such authorization, review
and offline-test an **opt-in, response-size-limited** HTTP 400 category reader:
read at most a small fixed bound (e.g. 1,024 bytes, detect overflow), parse
only a JSON object with a nested `error`, retain solely an enumerated
`error.type`, an enumerated `error.code` and a **strictly allowlisted** field
path/category for `error.param` (otherwise `unknown`). Never retain or log
`error.message`, arbitrary strings, headers, URLs, raw response body,
credential or customer input; close the error response and preserve durable
`failed` receipt/no-replay semantics. An allowlisted code like
`invalid_request_error` alone would still **not** identify the offending
field. Require separate security review, owner authorization of exact
manifest/hash/budget and account Free/billing-disabled confirmation. **No
diagnostic is authorized by this document.**

Focused M2.0/M2.1 mock-wire and PostgreSQL gate tests passed **26/26**
on a new isolated fixture/checkpoint pair. An earlier focused run against
an *already used* checkpoint produced five duplicate-thread setup errors;
it was discarded for validation and rerun on the fresh pair. No code was
changed, so a new seven-database full regression was not required; the
latest pre-trial fresh full run remains **271 tests, seven unrelated Gemma
skips**. Private CI remains unverified for this offline documentation update.
