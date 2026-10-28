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

## Bounded diagnostic integration, still unapproved for hosted use

`backend/dealdesk_phase2/groq_error_diagnostic.py` is a pure classifier.
The shared `_post` transport now accepts an **opt-in** `capture_http_error`
flag; **only** the exact separately approved M2.1 Credit-diagnostic manifest
enables it in the hosted model. Ordinary M2.1, M2.0 and all other callers
retain the original default (error bodies unread). The
classifier is reached **only** after an HTTP error, not for 2xx responses.
It requests
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
ID grammar or enum expansion requires review. No historic data can be
recovered retroactively from it.

The error response is closed; `_post` raises the **original `http_400`** even
if parsing fails or times out. Only recognized fields (omit `unknown`) can
be appended to the existing failed receipt as a schema-validated optional
`diagnostic` object, after a durable one-use reservation. Earlier receipts
without it remain valid; the `code`, `elapsed_ms` and original request hash
are unchanged. There is no second file, raw provider message, URL, credential
or tool evidence in the receipt. Failed receipts and crash-only reservations
still cannot be sent again. The classifier cannot authorize another POST or
business action. Ali must separately approve **this** capture/retention
contract before a new hosted send.

## Smallest proposed hosted discriminator — authorization candidate, not approved

The checked-in [exact non-secret candidate manifest](week3-credit-http400-diagnostic-candidate.json)
has compact sorted-key JSON SHA-256
`592110acd76a914f56b55f7d23d8fa78819c95015a4444512aada50d47c3c8e9`.
Its `authorization_candidate` status alone is **not approval**: the hosted
runner also requires explicit authorization, Free/billing-disabled
confirmation, exact manifest digest, an owner-supplied private approval record
with the same digest/assessment/secondary selection, and source/checkpoint
identity checks. Proposed **new** identity (not present in historical checkpoints):
`M21-DIAG-B01-31b981ed-d364-422c-91ea-9a5a2c6c661b`.
Synthetic B01 only; fresh fixture database
`dealdesk_diag_b01_31b981ed_fixture`, checkpoint
`dealdesk_diag_b01_31b981ed_checkpoint`, and owner directory
`/tmp/opencode/dealdesk-diag-b01-31b981ed-owner` were checked **absent**
offline; none was created. A future authorized operator must independently
recheck absence, create owner-only `0700` storage and confirm actual business
and checkpoint connections return the **declared distinct database names**
before either send. The runner checks the checkpointed pinned bundle/source
digest against the manifest, but the caller must verify actual database
connection targets and Phase 1C source before any approval record or POST.
Use pinned Phase 1C commit
`90c0bc8e285ee69262c7db826b786096a77ad004`, the existing synthetic B01
source bundle/digest and unchanged fixed original and credit-specific M2.1
redaction, prompt, tool names/schema and native continuation wire. Keep the
**same** Groq model `openai/gpt-oss-120b` and **existing secondary** local
credential selected by `GROQ_SECONDARY_API_KEY`; never fall back to primary.
No other specialist, case or request is proposed. The separate Credit-only
LangGraph edge ends after Credit and deliberately does **not** present an
incomplete Credit result as a full Policy/Routing review; the existing
three-specialist route is unchanged.

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

**Approval required before execution:** Ali reviews/accepts the capture
fields, optional failed-receipt schema and tests, then explicitly approves
**exactly the manifest hash above** and confirms the selected secondary
Groq account is Free-tier with paid billing disabled. Before any private
approval record is created or either POST is sent, the operator must recheck
source pin, full synthetic fixture, fixed original six findings, sealed bundle,
source-input digest, clean checkout/diff, fresh databases/checkpoint/owner,
actual database connections, credential ownership and shape, and exact
two-send budget. Only an explicitly authorized operator may then write the
owner-only private approval record that binds the manifest SHA-256, assessment
ID, credential selection and billing attestation. No such record was created
here; historical approvals cannot be reused. Any metadata preflight or other
network access would require separate inclusion in Ali's authorization.

Offline validation: **35/35 focused tests** passed on a fresh isolated
PostgreSQL fixture/checkpoint pair before the final crash-only receipt test
was added. The final **fresh seven-database backend regression ran 281 tests:
274 passed, seven unrelated Gemma skips**. These
exercise mocked HTTP errors, bounded reads, receipt integrity, historical
gate behavior and a Credit-only two-send/restart test; no provider calls or
historical receipts. The B01 synthetic original is ten stocked-finished units:
the authorized credit inspection would read one selected dated credit profile;
AI would have the option to return a finding or abstain, but fixed credit and
the original withheld routing govern. A 400 yields no AI finding and stops.
No deterministic business rule was changed. Private GitHub CI for this
increment remains unverified.
