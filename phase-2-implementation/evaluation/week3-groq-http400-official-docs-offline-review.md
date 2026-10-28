# Four terminal Groq second-turn HTTP 400s — current-docs and offline review

**Later evidence:** The owner reports four Groq Console `tool_use_failed`
HTTP 400 entries; see the [new offline reassessment](week3-groq-console-tool-use-failed-reassessment.md)
for qualified account/date correlation and the generation hypothesis. This
historical audit's “unclassified” statements refer to **local receipts**;
the Console report does not add a provider category to those receipts.

**28 October 2026; documentation-only network lookup.** This review fetched
public official Groq **documentation pages**, not Groq API/model metadata, and
read existing private checkpoints locally. No inference, new assessment,
approval record, request replay, credential read or provider response body
was involved. The earlier three-case [byte comparison](week3-cross-specialist-http400-offline-diagnosis.md)
and [fourth terminal Credit result](week3-credit-http400-diagnostic-result.md)
remain authoritative for what was observed.

## Sources actually consulted

- [Groq GPT-OSS 120B model page](https://console.groq.com/docs/model/openai/gpt-oss-120b): tool use supported; context 131,072, max completion 65,536.
- [Tool-use overview](https://console.groq.com/docs/tool-use/overview) and [local tool-calling guide](https://console.groq.com/docs/tool-use/local-tool-calling): assistant `tool_calls`, provider-issued call ID, result message with matching `tool_call_id` and string `content`; example includes a result-message `name`. `tool_choice=required` **can yield HTTP 400 if no tool call is generated**; it is not a guarantee of a valid tool call. The model supports local tools but not parallel tool use.
- [Chat completion API reference](https://console.groq.com/docs/api-reference#chat-create): `model`, `messages`, `tools`, `tool_choice`, `parallel_tool_calls`, `temperature`, `max_completion_tokens` are documented. Up to 128 functions, 512 below model output maximum. Published successful response example has `x_groq.id` in `req_...` format; that does **not** document a failed-response header or provide a failed request ID.
- [OpenAI compatibility](https://console.groq.com/docs/openai): explicitly lists `messages[].name` as unsupported and says its presence produces HTTP 400; also states `temperature=0` is converted to `1e-8`.
- [Reasoning](https://console.groq.com/docs/reasoning): GPT-OSS supports reasoning; explicit `reasoning_format=raw` with tools may fail, but our request has **no** `reasoning_format` or `include_reasoning`.
- [Structured outputs](https://console.groq.com/docs/structured-outputs): `response_format` structured output cannot be combined with tool use; our requests have **no** `response_format`. Strict structured-output schema constraints are not evidence of a defect in these function parameters.
- [API error codes and responses](https://console.groq.com/docs/errors): the documented JSON example is `{"error":{"message":"…","type":"invalid_request_error"}}`. `message` is free-form and potentially sensitive; `error.code`, `error.param` and `x-request-id` on error responses are **not guaranteed by this page**. Its generic description of 400 as an invalid request does not disprove the tool guide's model-generated no-tool 400 case. The page mentions a Console logs view but does not guarantee per-request error detail is visible there.

These are documentation statements retrieved for this review, not evidence
of the server's internal handling of any one failed POST. The compatibility
page and the official local-tool examples **conflict** about `messages[].name`:
both are documented; neither can be silently privileged over accepted
historical continuations.

## Locally rebuilt and hash-checked serialized continuations

The first M2.0 attempt was rebuilt with the **historical** wire source at
`9e70046a67d7776aff40e6604c16462134ddfd42`, not today's changed prompt.
Each other builder used its saved-matching contract. The sealed input, returned
assistant call and completed permission-ledger result were read from the
corresponding checkpoint; each compact UTF-8 body hash was compared with its
pre-send reserved digest. No model-visible content is copied below.

| Continuation (first turn returned for every case) | Second turn | Hash matched? | Result |
| --- | ---: | --- | --- |
| First-account Configuration B01 | 3,339 bytes | Yes | Accepted |
| First-account Pricing B01 | 3,377 bytes | Yes | **400, terminal** |
| Secondary-account Configuration B01 | 3,749 bytes | Yes | Accepted |
| Secondary-account Pricing B01 | 3,768 bytes | Yes | **400, terminal** |
| Secondary-account Credit B01, Week 3 | 3,814 bytes | Yes | **400, terminal** |
| Secondary-account Credit B01, approved diagnostic | 3,813 bytes | Yes | **400, terminal** |
| Corrected Fulfillment B05 | 7,252 bytes | Yes | Accepted |

For all seven, the sequence is `system → user → assistant(tool_calls) →
tool(tool_call_id)`. The assistant `content` is null, one function call is
present, the ID matches its tool-result message, the tool-result `name` equals
that function and result `content` is a JSON **string**. Every request uses
`openai/gpt-oss-120b`, `tool_choice=required`, `parallel_tool_calls=false`,
`max_completion_tokens=512`, `temperature=0`, function tools with object
parameters and `additionalProperties=false`; none sends `response_format`.
Pricing and Configuration advertise the same three-function *shape* with
different inspection names and source evidence; Credit's inspection parameter
is aliased `subject_id` and its selected evidence is a redacted credit profile.
All four failures fit under the local 8,192-byte request ceiling. Byte/hash
matching proves what we prepared for `_post`, **not** that Groq accepted its
semantics. The three accepted controls refute a *universal* rejection of the
four-role pairing, `name`, `required`, zero temperature or 512-token cap;
they do not rule out a request-dependent interaction or provider inconsistency.

### Documented mismatch versus possible causes

The compatibility page's literal `messages[].name` restriction **does**
describe a field on our tool-result messages, so it is a **documented
compatibility warning**. But the same provider's local-tool examples include
that exact field, and all three accepted continuations sent it. These facts
do **not** establish an independently verified current protocol defect or a
cause of the four selective 400s. Removing it now would modify the active
wire based on contradictory evidence. No missing assistant/tool pair,
unmatched call ID, non-string tool-result content, unsupported top-level
parameter, unsupported model, explicit raw reasoning format or combined
structured-output/tool mode was found. Neither the specific function schemas
nor prompts/evidence were controlled counterfactuals: **forced-tool
generation**, a request-dependent provider validation rule, function choice
or argument generation under the particular Pricing/Credit evidence, and
unobserved provider errors remain unresolved. The 512-token cap may matter
for reasoning/tool generation but is supported and also succeeded elsewhere;
no measured causal link exists.

## Why the approved diagnostic kept only `http_400`

Current `groq_error_diagnostic.py` asks the error stream for **at most 1,025
bytes once**, rejects any read longer than **1,024**, and `json.loads` parses
the *entire* bounded response. A short read/truncated JSON, non-UTF-8, read
timeout, non-object root, missing/non-object `error`, or a valid JSON body
over 1,024 bytes leads to no provider fields. A long free-form `message`
could cause the last case even when `error.type` is valid. The classifier
retains only the enumerated `error.type` (`invalid_request_error` or
`api_error`), narrow `error.code` and `error.param` enums; unlisted valid
provider values are dropped. It accepts only `x-request-id` **if** the JSON
parsed and the header value is an exact lowercase UUID; the docs do not
promise this header, and their successful `x_groq.id` example uses `req_...`,
which would **not** pass our UUID rule. It never reads or retains arbitrary
message/header text. In-memory synthetic examples verified that the
documented short `error.type=invalid_request_error` **would** be retained,
while a longer message causing oversize or unknown fields/`req_...` would
not. The failed diagnostic receipt has **no** allowlisted provider fields;
it does **not** tell us which loss path occurred, body length, whether any
header existed, or what Groq said. The original `http_400`, timing, digest
and terminal no-replay receipt remain intact.

A future *separately reviewed* diagnostic contract could allow a larger
fixed read ceiling (e.g. 4 KiB, plus one overflow-detection byte) or record
only fixed local states such as `oversize`, `malformed`, `read_timeout`,
`parsed_unrecognized` **without** retaining raw text. It could inspect
*only* explicitly allowlisted response header names and accept a strictly
validated, documented ID grammar, if Groq publishes one. Never save
arbitrary `error.message`, headers, body fragments, raw evidence or keys;
keep the HTTP status and no-replay failure authoritative. Increasing the
read limit, altering ID formats, or persisting new diagnostic states is a
**new retention/security contract**, not authorized by the spent 1,025-byte
trial approval; review/test it offline and obtain Ali's explicit approval
before any future send. A single unbounded read or logging body to diagnose
this case is not acceptable.

**Safest next information source:** Ali can check existing account Console
history *manually* for a safe category/field or ask Groq support whether a
rejection can be located by account, approximate time and model **without
sharing prompts, customer evidence, credentials or raw responses**. Console
request-level availability is unverified. No saved provider HTTP request ID
exists, and our SHA-256 body digest is not one. If this produces nothing,
further controlled synthetic experiments would need **new explicit
authorization, a fresh identity, offline-tested capture and source-first
preflight**; none is approved or launched here. All four historical attempts
and their receipts remain terminal. No request-wire or deterministic-rule
code change is justified by this audit.

Focused offline mocked wire/classifier tests passed **21/21**. Because no
implementation changed, no new PostgreSQL regression was run; the previous
fresh seven-database backend regression remains **281 tests, seven unrelated
Gemma skips**. Private CI for this documentation-only increment is unverified.
