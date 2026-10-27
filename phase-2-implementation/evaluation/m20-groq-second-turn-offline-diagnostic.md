# Groq B05 second-turn HTTP 400 — offline wire correction and new proposal

**27 October 2026. No new hosted inference.** The stopped two-request B05
assessment in [the saved result](m20-approved-hosted-validation-stopped-result.md)
remains permanently reserved. B01 was never started. Owner-only raw response,
receipts and checkpoint were inspected locally; neither their content nor any
credential is included in this repository. The pinned Phase 1C authority and
the separate Configuration/Pricing hosted contract were not changed.

## Evidence and diagnosis

The first live B05 decision was **4,810 bytes**, returned an assistant
`inspect_fulfillment_paths` native function call with a nonempty provider
`id`, and the trusted tool returned two evidence references. The second
checkpointed request was **6,887 bytes** and its recomputed canonical SHA-256
matched the failed reservation. It contained only `system → user` messages,
flattening the new observation into the user text, without the previous
assistant `tool_calls` message or a `tool` result paired by `tool_call_id`.
Groq returned HTTP 400 before producing a response; its error body was
intentionally not read, so the **exact provider-side rejection reason is
unknown**. The successful first request excludes a general lack of model
access or universally invalid tool definitions as explanations for that
request. It does not prove the second failed solely because of message shape.

Groq's [local tool calling contract](https://console.groq.com/docs/tool-use/local-tool-calling)
and [tool-use overview](https://console.groq.com/docs/tool-use/overview)
show a continuation as `system/user → assistant(tool_calls with id) →
tool(tool_call_id matching id, name, content)`. Missing this pair in the
saved follow-up is a **proven protocol defect**, and the strongest actionable
root-cause candidate; provider-specific validation of `tool_choice=required`
could independently yield 400 if the model does not choose a function.
Neither alternative can be confirmed without a separately authorized POST.

The saved second-turn metadata used the same chat endpoint, model
`openai/gpt-oss-120b`, temperature zero, one forced native tool call,
`parallel_tool_calls=false`, and 512 configured completion tokens; there
was **no** `response_format`. These fields are covered by Groq's
[chat API reference](https://console.groq.com/docs/api-reference#chat-create).
The first request used the same settings and succeeded. The later final
request (never sent live) has **no tools** and a separate strict JSON-schema
response format, consistent with Groq's
[structured output limitation](https://console.groq.com/docs/structured-outputs)
against mixing tool use and structured output in one request; exact final
schema acceptance remains unproven. `live_models._post` sends the canonical
UTF-8 JSON after checking size, and the durable send path hashes the same
serialization; the first request's recomputed digest still matches its
returned checkpoint after this correction.

## Narrow correction, safety and tests

Only a *hosted follow-up decision after a completed inspection* now carries
the original assistant call and authorized tool result in order. It validates
the checkpointed action, tool name, completed ledger result, one original
provider call ID and matching result before reserving the send. The initial
user message retains only the initial prefetched observation so the tool
result is not duplicated there. No raw provider reasoning is forwarded.
The old failed identity is not reusable: the corrected second-turn body is
**7,252 bytes** on the saved local source (below 8,192), with a new digest;
the old reservation and original checkpoint are untouched. Missing IDs or
altered results stop before a second reservation. The decision request
still has `tool_choice=required` and no structured output; final requests
remain separate. This is a wire-contract repair, not a change to business
rules, agent roles, evidence scope, provider, budget or retries.

Mocked HTTP on a fresh pinned B05 fixture exercised two native decisions,
the separate structured final, tool-result ID pairing, cited fixed candidate
verification, six candidate specialist rechecks, customer acceptance pending
and human review. Another fresh assessment simulated HTTP 400 on the second
decision and confirmed the pending checkpoint, failed receipt and **no send
after restart**. Malformed/missing tool IDs and mismatched tool result/name
stop before transmission. Historical campaign mocks were updated to supply
realistic call IDs rather than silently weakening the production check.
The final fresh PostgreSQL suite used seven newly initialized disposable
databases: **233 tests, 226 passed, seven unrelated Gemma skips**, log
`/tmp/opencode/dealdesk-m20-wire-fix-v3-full-regression.log`. These are
offline checks; GitHub CI is not represented as green.

## Proposed minimal new hosted test — **not authorized; do not execute**

Only the new B05 assessment in
[`m20-groq-wire-continuation-proposal.json`](m20-groq-wire-continuation-proposal.json):
`M20-WIRE-CONTINUATION-B05-6c63a9e3-fec9-4d97-8c80-2cb1c9dcf476`.
Canonical manifest SHA-256:
`9fcd2fd14fde3ba00b497f404ea3716dc88ca79f58a635c9d39ee762517f7822`.
Use the **same pinned synthetic source**, freshly sealed/verified for this
identity, and a fresh isolated checkpoint and owner-only receipt directory.
At most **three sequential Groq POSTs** (two decisions at 512 configured
completion tokens each, one structured final at 1,024: **2,048 configured
output tokens total**), each no more than **8,192 serialized bytes**; stop
on **8,000 reported total tokens** after each returned response. This
reported-token gate is not a hard input-token or financial ceiling. No retry,
fallback, second case, historical replay or hosted correction. Stop on any
source/pin/receipt/credential/model-access mismatch, HTTP error, unknown
send, missing usage, invalid ID/ledger/citation, failed fixed verification
or budget violation. Preserve private artifacts and require human review;
a valid abstention is recorded, not a candidate success. Before any POST,
Ali must confirm Free/billing-disabled status again, approve this **new**
identity/digest/budget, and accept CI status if unverified. Successful
transport would validate the wire only for this case; it would not establish
accuracy or authorize ordinary hybrid execution. Week 3 planning remains
separate and does not delay resolving this Groq execution blocker.
