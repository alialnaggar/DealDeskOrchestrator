# Stopped B01 Pricing HTTP 400 — offline structural diagnosis

**27 October 2026.** The B01 assessment and its fourth attempted Groq POST
are permanently stopped. This diagnosis reads the existing private PostgreSQL
checkpoint **locally**; it does not send anything, print provider responses,
expose credentials, or interpret an unread error body. The [sanitized run
result](m20-configuration-pricing-hosted-result.md) identifies the four
attempts, three returned usage reports and fixed-review containment.

The Configuration and Pricing second-turn bodies were independently rebuilt
from each specialist's exact checkpointed input, returned native call
descriptor and **completed** permission-ledger result, using the same
`request_body` serializer. Each rebuilt SHA-256 matched its pre-send
`m20_model_attempts` reservation. No model text, line values or private body
was copied into this document.

| Checked property | Configuration follow-up (accepted) | Pricing follow-up (HTTP 400) |
| --- | --- | --- |
| UTF-8 canonical body | 3,339 bytes | 3,377 bytes |
| Model / token setting | `openai/gpt-oss-120b` / 512 | Same |
| Top-level fields | `model`, `temperature`, `max_completion_tokens`, `parallel_tool_calls`, `tool_choice`, `tools`, `messages` | Same |
| Tool names | Own `inspect_configuration_line`, `submit_finding`, `abstain` | Own `inspect_pricing_line`, `submit_finding`, `abstain` |
| Tool schema / control | Domain-specific line ID; shared final/abstain schemas; `tool_choice=required`, `parallel_tool_calls=false` | Same, except own inspection name |
| Role sequence | system → user → assistant → tool | Same |
| Assistant call / tool result | `content=null`, one function call, native 39-character ID paired with `tool_call_id`, same function name, valid original line ID; tool content equals completed ledger result | Same checks pass |
| Request reservation | Rebuilt request hash equals reserved hash | Same |

The Pricing tool result contains the selected pricing-line fields rather than
Configuration's selected product fields, as authorized. That data and the
inspect function name are the meaningful differences; an HTTP 400 alone
does not establish which difference mattered. Groq's error body was **not
read**, and there is no provider contract rejection detail. Neither the
paired-message implementation, IDs, serialization nor budget can currently
be identified as the demonstrated root cause. Classify as **unresolved
provider rejection**; do not change the adapter or claim that Groq rejects
Pricing's schema based on this one response.

Offline regression adds both specialists' shared wire-shape/ID checks and a
mocked four-turn Configuration-success/Pricing-HTTP400 flow: the original
fixed results and human review remain intact, Pricing contributes no validated
finding, and reopening the PostgreSQL checkpoint causes **zero replay sends**.
Further diagnosis must use safe local fixtures or separately authorized
provider-contract documentation/probes. A fresh hosted assessment and budget
would require Ali's new explicit authorization; B01 may not be resumed.

## 28 October 2026 — second-account recurrence and byte-level review

The separately authenticated [Week 2 B01 assessment](week2-secondary-b01-hosted-result.md)
again returned Configuration's inspection/finding and Pricing's inspection,
then stopped on the **fourth POST**, Pricing's second turn, HTTP 400. Both B01
assessment identities have a terminal reserved Pricing follow-up; neither
checkpoint, owner receipt nor reserved request may be retried, resumed or
replaced in place. This review performed **no provider request**.

Read-only reconstruction from the newer checkpoint used its exact
`m20_model_attempts` returned call descriptor, completed scoped tool ledger,
sealed Phase 1C pool, original fixed findings and `request_body`.
`live_models._post` actually sends `_json(body).encode("utf-8")` via
`urllib.request.Request`. For each follow-up, these bytes equalled
`_canonical(body).encode("utf-8")` **byte for byte**; their lengths and SHA-256
equalled the pre-send reservation and the published request size/hash.
No credential, raw provider return or business input was copied to Git.

| Actual-wire property | New Configuration accepted | New Pricing HTTP 400 | Historical B05 Fulfillment accepted |
| --- | --- | --- | --- |
| Body bytes | 3,749; checkpoint hash matched | 3,768; checkpoint hash matched | 7,252 reported for the successful decision continuation; a separate wire/campaign |
| Top-level parameters | `model`, `temperature=0`, `max_completion_tokens=512`, `parallel_tool_calls=false`, `tool_choice=required`, `tools`, `messages` | Exactly the same keys/values | Decision continuation also used model, temperature, token ceiling, tool definitions, required tool choice, sequential tool calls and messages; not an identical domain schema |
| Roles | system → user → assistant → tool | Same | Same four-role continuation, per [B05 report](m20-groq-wire-continuation-hosted-result.md) |
| Tool-call linkage | One provider-issued 39-character ID; assistant `tool_calls[].id` equals tool `tool_call_id`; JSON arguments match original line | Same | Native assistant/tool pairing accepted |
| Tool result message | String-encoded JSON of completed, authorized product record; includes `name` | String-encoded JSON of completed, authorized pricing-line record; includes `name` | Historical adapter also included tool `name` |
| Available tools | `inspect_configuration_line`, `submit_finding`, `abstain` | `inspect_pricing_line`, `submit_finding`, `abstain` | Different Fulfillment tools/parameters |
| Other differences | Configuration system instruction, specialist/fixed finding and selected product fields | Pricing instruction, specialist/fixed finding and selected quoted/list/cost/margin fields | Different task/response schema and prompt; not a controlled counterfactual |
| Structured output | **No** `response_format` on either B01 tool-use turn | **No** `response_format` | Structured final was a separate request, not its successful tool-use continuation |

The newer request's provider-issued call IDs, paired tool-result content,
model, controls, sizes and actual bytes pass local structural checks; the
earlier B01's checkpoint reconstruction above
also matched its reservation hashes (3,339/3,377 follow-up bytes). Those
checks are **not** a Groq server validator. The test
`test_actual_http_serialization_of_both_followups_without_network` now
intercepts the real `_post`/`urllib` serialization with synthetic inputs;
`test_pricing_second_turn_http_error_is_sanitized_at_real_transport` simulates
one HTTP 400 and proves one attempt plus unread provider error body. The
pre-existing PostgreSQL no-replay test checks terminal containment. The
focused wire class passed **9 tests**; a fresh seven-database isolated
PostgreSQL regression passed **255 tests, seven skips**. Private CI remains
unverified. An offline mock can reproduce **our stop behavior**, not the
server's rejection.

Groq documentation checked on 28 October 2026:

- [OpenAI compatibility](https://console.groq.com/docs/openai) says
  `messages[].name` is unsupported and could produce HTTP 400; its separate
  [local-tool examples](https://console.groq.com/docs/tool-use/local-tool-calling)
  **include** a tool-result `name`. Both B01 Configuration continuations and
  the B05 Fulfillment continuation with this field were accepted. This is a
  documented inconsistency and a candidate for a *future* controlled test,
  **not** proof that `name` caused Pricing's rejection. Do not remove it from
  active wire solely on this evidence or rewrite historical request hashes.
- [Local tool calling](https://console.groq.com/docs/tool-use/local-tool-calling)
  requires a matching `tool_call_id` and says `tool_choice=required` can
  return 400 if the model does not call a tool. Both follow-ups supplied tools
  and a correct ID; the actual generated decision on the rejected turn is
  unknown. An inference-time tool-choice failure remains a hypothesis.
- [API reference](https://console.groq.com/docs/api-reference#chat-create-request-body)
  supports `max_completion_tokens`, `parallel_tool_calls` and `tool_choice`;
  [model listing](https://console.groq.com/docs/models) lists a 65,536-token
  completion maximum for `openai/gpt-oss-120b`, well above the approved 512.
  No supported-parameter or numeric-limit violation was established. The
  [tool-use table](https://console.groq.com/docs/tool-use/overview) lists this
  model as supporting local tools, but not parallel calls, consistent with
  our `parallel_tool_calls=false`.
- [Structured outputs](https://console.groq.com/docs/structured-outputs)
  disallows tool use combined with structured outputs; **neither** B01
  continuation supplied `response_format`. B05's separate structured final
  therefore does not explain the Pricing failure.

**Conclusion: recurring provider rejection, cause unclassified.** No proven
Pricing-specific serialization defect or provider fix was found; no live
adapter, prompt, provider-independent contract, fixed rule or budget was
changed. The smallest next diagnostic is first to ask the account owner to
retrieve any *existing* Groq-side rejection category/field for the stopped
request (without another send), if such a record is available. If not, a
**new, separately approved and budgeted source-first assessment** may capture
only bounded/sanitized error `type`, `code` and `param` (and a safe request
identifier if available) from a *new* failed response under owner-only
retention; never publish its raw body, headers, credentials or echoed input.
Such a diagnostic needs a reviewed redaction contract and must not resend
either terminal request, silently retry, change tool choice or enlarge limits.
Even a successful future diagnostic is not a validated hosted Pricing finding;
a separately authorized new assessment is required to establish that gate.
