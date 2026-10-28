# Groq Console `tool_use_failed`: offline reassessment of terminal second turns

**28 October 2026; no inference or Groq API access.** The account owner reports
seeing **four HTTP 400 entries dated 27 October 2026** for
`openai/gpt-oss-120b`, each classified by the Groq Console as
`tool_use_failed` and showing **512 completion tokens**. Other same-model
requests, including tool continuations, succeeded. This is **owner-supplied
Console evidence**, not a screenshot, export, error-response body or locally
verified provider request ID. We did not access the Console or obtain per-row
timestamps, timezone, project/account attribution, field definitions or
`failed_generation`. Do not substitute this evidence for the local durable
receipts or claim four exact matches.

## Correlation and its limits

Read-only local checkpoint history (no send, no credential) gives the **first
checkpoint containing each second-turn reservation**, in UTC. These are near
the attempt but are **not provider receive times**. The frozen wires match
their saved reserved SHA-256 digests and terminal HTTP-400 records as in the
[seven-continuation audit](week3-groq-http400-official-docs-offline-review.md).

| Local terminal attempt | Locally selected account | First second-turn reservation checkpoint (UTC) | Local HTTP result / configured cap |
| --- | --- | --- | --- |
| M2.0 B01 Pricing, original | Primary | 2026-10-27 19:58:13 | 400 / 512 |
| M2.0 B01 Pricing, later | Secondary | 2026-10-28 07:08:16 | 400 / 512 |
| M2.1 B01 Credit, first | Secondary | 2026-10-28 12:18:37 | 400 / 512 |
| M2.1 B01 Credit, diagnostic | Secondary | 2026-10-28 13:23:13 | 400 / 512 |

The earlier local records show two different accounts, with no confirmed
Groq **project** identifiers. Only the first local reservation is on 27
October **UTC**. The owner reported four Console rows on 27 October but did
not specify Console timezone or account/project grouping. Repository report
*dates* for the three later trials are 28 October; they are not precise send
timestamps. No per-row Console time, request ID or project was supplied, so
we cannot resolve the date difference or establish which Console entries
belong to which local attempts. **If** Console times are UTC and all four
rows belong to one project, the proposed four-row correspondence conflicts
with the saved chronology/account split. Do not silently assume a timezone
offset or that every Console 400 is one of these four. A request-body digest
is not a provider ID. All four local failures still have unknown **actual**
provider usage; the Console's “512 completion tokens” may be a *configured
ceiling*, generated usage, or another display field until the owner confirms
its label and semantics. Four identical configured limits alone do not prove
all four generations reached exactly 512 tokens.

## Wire, prompts and successful counterexamples

All four locally reconstructed second turns have one valid returned native
inspection call paired with its JSON-string tool result. They send
`tool_choice="required"`, **three** advertised functions (specialist-specific
read-only `inspect_*`, `submit_finding`, `abstain`),
`max_completion_tokens=512`, `parallel_tool_calls=false`, `temperature=0`.
No request sets `reasoning_effort`, `reasoning_format`, `include_reasoning` or
`response_format`; the provider's effective default reasoning effort and
output budget distribution are not measured. GPT-OSS reasoning and generated
function arguments share the completion budget per the
[previous compatibility review](groq-inference-compatibility-and-probe.md).
M2.0 finding arguments require an array of exact
`ref/field/value_json` citations **and** `uncertainty_reasons`; M2.1 Credit
requires exact citations but not `uncertainty_reasons`. Both offer a compact
enumerated `abstain` action. The initial inspect call is inexpensive;
composing exact claims on the second turn is harder. Credit's selected profile
is redacted but still requires matching aliased refs/fields/values.

The original Pricing prompt (historical source at
`9e70046a67d7776aff40e6604c16462134ddfd42`) says *first inspect*, cite
returned fields, choose **exactly one function per response**, and never give
a free-text final answer. Later Pricing v2 adds domain-specific constraints
but still requires one declared function. The Credit v1 system prompt
separates untrusted evidence, exact citations and abstention; its wire adds
“Choose exactly one declared function; no free-text final answer.” Neither
prompt explicitly instructs the model to inspect *again* after a completed
read. Nevertheless, `required` still forces **some** function even when it
would naturally stop or explain uncertainty. `submit_finding` or `abstain`
are the intended second-turn actions; the inspection tool remains advertised
although Credit's parser rejects a second inspection and M2.0 limits
repeated inspections. This is a possible avoidable generation burden, **not**
proof that Groq tried an unnecessary inspection or that the model attempted
prose instead of a call.

The accepted Configuration continuations use the same model, 512 cap,
required choice, named tool result and M2.0 final-action schema; one returned
309 completion tokens (first-account run), so none is a universal wire defect.
The accepted B05 Fulfillment decision continuation used the same 512 ceiling
and consumed **494** completion tokens—near the ceiling, but not a failed
Pricing/Credit sample. B05's **separate structured final** consumed **1,017**
under a **1,024** configured ceiling; that demonstrates this model can produce
a longer accepted response with a different final schema/budget, **not** that
increasing Pricing/Credit's cap will fix `tool_use_failed`. No accepted
same-specialist, same-evidence, higher-budget comparison exists. The
documented `messages[].name` compatibility warning still conflicts with
Groq's own local-tool examples and the accepted continuations; it is now
less explanatory than a tool-generation problem, not disproved in every
context.

## Interpretation and classifier boundary

The owner-supplied category is **consistent with Groq failing to produce an
acceptable model-generated tool call/arguments** when a tool is required,
possibly compounded by a 512-token ceiling, default reasoning, exact-value
claim schema and domain evidence. Groq's
[local-tool documentation](https://console.groq.com/docs/tool-use/local-tool-calling)
allows a 400 when `required` yields no tool call; its documented invalid
generation may include `failed_generation` in an error. The Console label
does **not** show whether these particular failures were no-call, malformed
arguments, truncated generation, tool-name mismatch or another provider
path. The local requests are syntactically paired and some same-control
continuations were accepted: a categorical invalid request-wire claim is
not justified. The leading **mechanism** is generation/tool-choice
interaction, not a proven root cause or a demonstrated token-exhaustion
threshold.

The existing opt-in classifier already allowlists **`error.code =
tool_use_failed`**. If the diagnostic trial's failed response was a complete
JSON object of at most 1,024 bytes with nested `error.code` exactly this
string, it should have been retained. The Console's normalized label does
**not** establish that the HTTP body used that shape or field: a long
`failed_generation` or free-form message could make the complete JSON exceed
1,024 bytes; a partial read, timeout, different code/type location or
unknown shape would also leave no category. The code ignores
`failed_generation` by design and never saves raw provider output; **ignoring
that field alone would not suppress a short otherwise parseable
`error.code`**. Do not infer what the unavailable diagnostic body contained,
backfill old receipts or loosen retention based on the Console label.

## Smallest next steps; generic matrix paused

1. **No new send:** Ask the owner, if safe, for the Console's timezone,
account/project per row, UTC time (or offset), and whether “512 completion
tokens” means configured limit or actual generated usage; seek only a safe
error category/field path or a support interpretation of
`tool_use_failed`, **not** `failed_generation`, prompts, customer evidence,
keys or raw response text. This may resolve the correlation and distinguish
budget exhaustion from other model-generation failures without an inference.
2. **Offline design only if needed:** Compare a second-turn-only alternative
that keeps a native **typed** `submit_finding`/`abstain` action but removes the
now-ineligible inspector; alternatively evaluate `auto` with strict local
validation: prose/no tool call must become an **abstention or AI error**, never
an accepted finding. Keep role/citation/evidence permission checks and
deterministic authority. Mock tests should cover both valid tool calls and
no-call/malformed output, budget edges and terminal no-replay. Altering tool
choice or advertised tools changes the request contract and requires review.
3. Consider a separately justified modestly larger completion ceiling or
less complex final-action schema **only after** safer metadata/support or
offline sizing suggests the relevant failure mode. A larger ceiling changes
cost/quotas and cannot retroactively reveal failed usage; schema reductions
must not weaken exact evidence binding. Do not enable `reasoning_format=raw`
with tools. None is implemented or approved here.

Any later hosted validation needs an exact source-first manifest, fresh
identity, explicit owner approval and billing/budget confirmation, durable
reservation and terminal no-replay; **no new hosted trial is authorized**.
The previously prepared [generic synthetic matrix](groq-http400-minimal-synthetic-diagnostic-plan.md)
is **paused**, not an active proposal. No six-agent rule, wire, classifier,
approval route, original deal or terminal attempt was changed. Focused
offline mocked diagnostic/transport and M2.0/M2.1 wire tests passed **31/31**.
No new PostgreSQL regression is required for documentation-only changes;
private CI has not been verified for this update.
