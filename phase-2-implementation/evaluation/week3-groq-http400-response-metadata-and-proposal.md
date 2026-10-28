# Groq second-turn HTTP 400: saved metadata and next diagnostic (unapproved)

**28 October 2026. Offline only.** Follow-up to the
[cross-specialist byte comparison](week3-cross-specialist-http400-offline-diagnosis.md).
The first-account Pricing, second-account Pricing and secondary-account Credit
assessments are **terminal**. No Groq inference, metadata query, new approval
record or historical send occurred in this review. The local owner directories
and exact assessment checkpoint threads were inspected read-only; raw private
model responses, evidence, credentials and approval files are not reproduced.

## What exists already

| Historical rejection | Local evidence | Could it identify a Groq request? |
| --- | --- | --- |
| First-account M2.0 Pricing, `M20-HOSTED-SPECIALISTS-B01-f9530345-979c-41ba-b6c6-9ec426059696` | Checkpoint: four reserved, three returned; failed Pricing ordinal 1 reservation includes local request SHA-256. The owner directory's audit file is an empty owner lock, **not** a per-POST receipt. | No saved provider request ID, response header, error category or provider body. |
| Secondary-account M2.0 Pricing, `M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7` | Checkpoint: four reserved, three returned; failed Pricing ordinal 1 has the local request digest. The owner audit file is likewise an empty lock. | No saved provider request ID, response header or error detail. |
| Secondary-account M2.1 Credit, `M21-WEEK3-B01-ae75c274-dd93-43b4-a6d8-8ba8681bab5f` | Checkpoint: two reserved, one returned; one completed credit inspection. Separate owner-only receipts show `reserved → returned` and `reserved → failed` with `http_400` and local elapsed milliseconds. | No saved provider request ID, response header or provider error detail. |

`request_sha256` is **our digest of the outgoing canonical body**, not a Groq
request identifier; the returned tool-call `id` links the model's function call
to its tool result and is **also not** an HTTP request ID. The historical
`_post` intentionally does not read the HTTP error body or copy response
headers; provider response IDs in successful model payloads, if any, do not
identify the failed HTTP requests. Existing records prove local reservation,
hash/shape and HTTP 400, **not the provider rejection reason**. The first
account's credentials are not interchangeable with the secondary account's.

### Optional manual Console check by Ali (no new inference)

Using the account that made **each** POST (first account for the first Pricing
attempt; secondary account for the other Pricing and Credit attempts), Ali can
look in the Groq Console **if** that account exposes historical request or
error activity. Filter by 27–28 October 2026, `openai/gpt-oss-120b`, HTTP
400/error status, and the approximate sequence (Pricing: fourth of four,
after Configuration's two successes; Credit: second of two, after one credit
inspection). Prefer a narrow Console time window using the locally retained
receipt timestamps where available; these are *client* times, not guaranteed
server times. Check whether the Console actually provides per-request status,
request IDs, an error category/code/parameter, or only aggregate usage. If it
offers a safe request ID/category/field name, Ali can provide just those and
account/approximate time (no raw request/response, evidence, prompt, key or
customer data). Do **not** open/export potentially sensitive request or error
bodies merely to debug this issue. If the Console has no request-level detail,
or the record cannot be matched uniquely, record **unavailable/ambiguous**;
do not attribute a Console event to a stopped assessment by date alone. We
have not verified that Groq Console offers these views or retains errors.

## Disabled offline diagnostic design

`backend/dealdesk_phase2/groq_error_diagnostic.py` is a **disconnected**
pure classifier, not an enabled HTTP handler or a runnable trial. It requests
at most 1,025 bytes from an error stream and rejects any body larger than
1,024 bytes. Only a parsed JSON `error` object can yield the fixed enumerated
`type` (`invalid_request_error`, `api_error`), `code`
(`invalid_request_error`, `tool_use_failed`, `json_validate_failed`) and
`param` (`messages`, `tools`, `tool_choice`, `max_completion_tokens`,
`messages[2].tool_calls`, `messages[3].tool_call_id`). All other values,
malformed/oversized responses and read timeouts become `unknown`; nothing
reflects provider `message`, unfamiliar `param`, body or headers. An optional
`x-request-id` is retained **only** when it is an exact lowercase canonical
UUID; other provider formats become `None`. This deliberately sacrifices some
potential matches to avoid retaining arbitrary server-supplied text; a future
ID grammar or enum expansion requires review. The test-only helper never
stores a body, never creates a receipt and cannot send. No historic data can
be recovered retroactively from it.

Before any real use, obtain explicit approval of the security/retention
contract and an adapter change that invokes it only after a fresh durable
one-use reservation, closes the error response, and records **only** the
allowlisted projection in a separately schema-validated owner-only diagnostic
record (not arbitrary `ProviderError` text). Keep `http_400` as the receipt
failure code, do not modify the receipt schema, and never retry or resume a
failed/uncertain reservation. The classifier's output alone cannot authorize
any additional POST or business action. Test and review the actual adapter
integration **offline** before Ali approves a hosted trial. The current
transport is unchanged; ordinary sends still do not read error bodies.

## Smallest proposed hosted discriminator — not executable or approved

Proposed **new** identity (not present in historical checkpoints):
`M21-DIAG-B01-31b981ed-d364-422c-91ea-9a5a2c6c661b`.
Synthetic B01 only; fresh fixture database
`dealdesk_diag_b01_31b981ed_fixture`, checkpoint
`dealdesk_diag_b01_31b981ed_checkpoint`, and owner directory
`/tmp/opencode/dealdesk-diag-b01-31b981ed-owner` must all be verified absent
before creation. Use pinned Phase 1C commit
`90c0bc8e285ee69262c7db826b786096a77ad004`, the existing synthetic B01
source bundle/digest and unchanged fixed original and credit-specific M2.1
redaction, prompt, tool names/schema and native continuation wire. Keep the
**same** Groq model `openai/gpt-oss-120b` and **existing secondary** local
credential selected by `GROQ_SECONDARY_API_KEY`; never fall back to primary.
No other specialist, case or request is proposed.

Maximum **two sequential POSTs total**, at most **512 configured completion
tokens each** (1,024 combined), **8,192 serialized request bytes each**,
one authorized credit inspection and a **24,000 reported-total-token
post-send stop** (failed-response usage remains unknown). The second POST is
eligible only after a valid, bounded first response and completed authorized
tool read, with pre-send exact digest/identity/receipt and remaining-budget
checks. Stop on any error, malformed/oversized response, timeout, ambiguous
reservation, reported-token ceiling, content/claim error, missing usage or
unrecognized tool call; no retry or extra POST. On second-turn rejection,
record only safe enumerated diagnostic fields if the future reviewed adapter
permits them; stop even if classification is `unknown`. Neither this proposal
nor a successful Credit response approves a deal or satisfies Week 3 gates.

An allowlisted **parameter/contract** error would direct a source-first
review of that specific field. A `tool_use_failed`-like category with no
parameter would favor a particular forced-tool generation/context problem,
but still **would not isolate** whether the trusted prompt, evidence content,
schema or model behavior caused it. `unknown`, no matching Console record or
a successful two-turn response remains inconclusive. A controlled
counterfactual would require another **separately authorized** fresh identity;
never alter this wire midway to chase an HTTP 400.

**Approval required before execution:** review and accept the exact
owner-only capture integration and its offline tests; freeze a new non-secret
manifest with the above identity, case, model, credential selection, source
digests, budget and SHA-256; run fresh isolation and source-first/fixed-rule
preflight; have Ali explicitly approve that *exact* manifest/hash and confirm
the selected secondary Groq account is Free-tier with paid billing disabled.
No approval record was created here, and the old trial authorizations cannot
be reused. Any metadata preflight or network access would need inclusion in
that separate authorization, not inference from this note.

Offline validation: **30/30 tests passed** (four classifier/receipt safety
tests plus 26 focused M2.0/M2.1 wire/gate tests), using a fresh isolated
PostgreSQL fixture/checkpoint pair; no provider calls. No deterministic
business rule or historical receipt was changed. CI for this increment
remains unverified.
