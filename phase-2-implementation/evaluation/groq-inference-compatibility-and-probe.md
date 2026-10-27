# Groq inference compatibility — offline finding and small probe proposal

**Post-probe update:** Ali separately authorized the isolated two-stage probe;
both stages passed. See the [sanitized result](groq-contract-probe-result.md).
That authorization is spent; the original B01 rejection remains unexplained.

**27 October 2026; no hosted inference authorized by this document.** The
historical B01 and replacement B01 assessment identities, pending sends,
receipts, checkpoints and journals remain closed. The replacement's
[`http_400` result](hybrid-groq-replacement-stopped-result.md) proves HTTP
rejection, **not** which parameter caused it. The frozen B01 decision wire
was 4,807 bytes (SHA-256
`f70a779b30d2b2727cc733e13ff25f58b341580296ea743d5575e6e0b54da77f`)
with a 512 configured completion cap, five authorized local function tools,
`tool_choice=required`, `parallel_tool_calls=false`, `temperature=0`, and
system/user text messages. Its final strict-JSON turn was never sent.

## Official documented contract versus saved wire

| Area | Documented support and offline comparison | Remaining unknown |
| --- | --- | --- |
| Model/chat messages | [Model list](https://console.groq.com/docs/models) lists `openai/gpt-oss-120b`; [chat create](https://console.groq.com/docs/api-reference#chat-create) accepts a model and role/content message array. B01 uses system/user text, no `messages[].name`, `n`, logprobs or other [unsupported OpenAI fields](https://console.groq.com/docs/openai). Authenticated model-metadata GET succeeded before both campaigns. | GET is not evidence that a chat POST was valid or billed. |
| Local tools / selection | [Local tool calling](https://console.groq.com/docs/tool-use/local-tool-calling) includes GPT-OSS 120B. Chat create documents `tools`, `tool_choice` and `parallel_tool_calls` (`required` is an allowed choice; false disables parallel calls). B01's decision uses function definitions with named JSON-object parameters; no proposal tool before binding-path inspection. | The service's validation of these *particular* five function schemas was not observed. |
| Reasoning and completion cap | [Reasoning](https://console.groq.com/docs/reasoning) supports GPT-OSS 120B with `reasoning_effort=low/medium/high` (medium default). `reasoning_format=raw` explicitly combined with tools/JSON produces 400, but B01 did **not** set raw; the docs say the format switches to parsed with tools. [Chat create](https://console.groq.com/docs/api-reference#chat-create) accepts `max_completion_tokens`; its limit includes visible and reasoning tokens. Model listing gives a maximum completion capacity but **no documented minimum of 1,024 or other value**. B01's 512 is a valid positive integer below the listed maximum. | Medium reasoning can exhaust 512 before a usable tool call; no documentation proves that a 512 cap produces HTTP 400 on this model. Neither the failed response body nor usage was saved. |
| Temperature | [OpenAI compatibility](https://console.groq.com/docs/openai) says `temperature=0` is converted to `1e-8`; [chat create](https://console.groq.com/docs/api-reference#chat-create) permits 0–2. | A model-specific runtime rejection cannot be excluded from HTTP status alone, but zero is not a documented unsupported field. |
| Structured final | [Structured outputs](https://console.groq.com/docs/structured-outputs) lists GPT-OSS 120B for `json_schema`, `strict:true`; all object properties must be required with `additionalProperties:false`. Offline recursion verifies that the existing final schema satisfies these structural requirements. Decision and final are separate turns: B01 had tools but no response format; final would have a strict schema but no tools. | No hosted final request occurred; acceptance and semantic quality remain untested. |

**Conclusion:** No particular field is demonstrably incompatible with the
official contract. The two stopped B01 attempts used the same serialized wire
under different authorized identities; the replacement returned HTTP 400,
while the first attempt's exact error classification was not saved. A
systematic request-level incompatibility is plausible, not established.
Changing the production adapter, business contract, model or 512 cap by guess
would create a third untested wire and obscure diagnosis. None is changed in
this milestone. Offline request-shape tests now protect the documented fields
and strict-schema structure; a separate *offline-only* builder prepares minimal
provider-contract probes.

**Offline gate:** focused contract/provider tests passed; a new isolated
PostgreSQL 16 cluster with independently loaded pinned synthetic/reference
fixtures, compiled rules and a separate checkpoint database ran the complete
backend suite: **219 tests, 212 passed, seven unrelated historical Gemma
diagnostics skipped**. Neither the pinned mocked hybrid tests nor the new
probe tests were skipped. GitHub CI is **unverified**, not claimed passed.
No provider call, credential lookup, Phase 1C modification or ordinary-agent
activation occurred during this investigation.

## One small, separately authorized diagnostic (not a ten-case campaign)

Proposed isolated ID:
`GROQ-CONTRACT-PROBE-85c63f16-0c5b-4c24-bea4-1d1b79adea71`.
No business deal, Phase 1C row, evidence, reviewer answer, graph assessment,
candidate or approval tool is in either model input. Two **distinct** requests
at most, sequentially, with the second allowed only after a valid first
inference response and reported usage:

1. **Plain chat control:** `Reply OK.`, model GPT-OSS 120B,
   `reasoning_effort=low`, `max_completion_tokens=512`, no tools or schema.
   Exact offline wire: **135 bytes**, SHA-256
   `4a34f6d4011cb32785b9ae8f413cc7df91a82ada0556a48184f58954740902a9`.
   Stop on any HTTP/transport/protocol error, missing usage or malformed
   completion; never resend.
2. **One local-tool call**, only if stage 1 succeeds: ask for `record_probe`
   with `status=ready`, `tool_choice=required`, `parallel_tool_calls=false`,
   `reasoning_effort=low`, `reasoning_format=parsed`, and
   `max_completion_tokens=1024`. This tool performs no action and cannot
   access deal data. Exact wire: **584 bytes**, SHA-256
   `0adbe00090d135587f771cff1ce4162c2a20f7b6158176323dd9d87ebe23442b`.
   Require exactly one valid function call and reported usage; stop otherwise.

**Maximum proposed scope:** **two attempted POSTs**, **1,536 configured
completion tokens total**, **2,048 serialized request bytes per send**
(both actual prepared wires are smaller); no retry, fallback, concurrent
worker, revised body or third request. The configured limits do not bound
input tokens or guarantee provider usage. Fresh owner-only `0700` receipt
directory, distinct fsynced `0600` per-stage reservations, sanitized status,
raw successful outputs only in owner-only test artifacts, timing/usage when
available, no secret or raw error body in reports. Failed or interrupted
stage is permanently uncertain and cannot be resent. The private launcher
must check exact probe ID, wire digests, credential ownership/format, current
Free-tier/billing-off confirmation and model-metadata access, and stop if
identity, wire, quota, permission or account gate changes. GitHub CI status
must be stated honestly. **No launcher is activated by this offline builder,
no credential is read, and no provider POST is made in preparation.**

Groq's [error documentation](https://console.groq.com/docs/errors) describes
an `error.type` field alongside an error `message`. If a later failure needs
better classification, an opt-in probe-only reader could cap the error body
to a small fixed size, transiently parse JSON, retain **only exact allowlisted
`error.type` values**, then discard the body and never log the message,
headers, URL or arbitrary strings. Even `invalid_request_error` would not
identify the rejected field; this security change is **proposed, not
implemented**, and is not needed to attempt the two staged control wires.
Never re-read or reinterpret the preserved historical error bodies (none
were saved). A successful probe establishes basic inference/tool compatibility,
not a hosted deal assessment; then return to critical Week 1 Fulfillment gaps
and Week 2 Configuration/Pricing AI rather than staging another ten-case run.
