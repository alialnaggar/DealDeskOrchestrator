# Week 3 consolidated hosted validation — proposal, **not authorized**

## 28 October offline preparation audit — still **not ready to send**

The [non-executable proposed manifest](week3-hosted-validation-proposal.json)
now records source-reviewed B01/B05/N03 original identities, Groq
`openai/gpt-oss-120b`, explicit **secondary** credential selection, prompt
`m21-original-system-v1`, dormant native-tool wire
`m21-groq-native-tools-v1`, three separate specialist tool scopes, and the
limits below. Local frozen Phase 1C read verified all three bundle/source
digests, as-of timestamps and snapshot refs.
The proposal's canonical sorted-key compact-JSON SHA-256 is
`f3b71a75cd835234382f4e40af95a410679ab3278c9b5c463b3073b3bf11b291`;
this checksum identifies an **unapproved draft**, not a send authorization.
B01 and B05 each have the fixed
`PO-BASE-DELIVERY-LATE` approval-required hit; N03 has **no fixed Policy hit**.
All three have a **withheld route, zero exposed roles**, and no selected AR or
payment rows. None tests over-limit Credit, a hard Policy block, a nonempty
AR/payment history or a role-visible fixed route. These are case coverage
gaps, not evidence that those conditions do not occur.

The [provider-independent allowlist and opaque reference view](../backend/dealdesk_phase2/m21_redaction.py)
now omits customer/deal/receivable/payment raw IDs, invoice numbers,
commitment evidence IDs and snapshot refs from proposed model messages; it
keeps internal exact evidence in the private checkpoint and maps model-visible
aliases back to returned references only after a strict wire parse. The
[dormant Groq request/response contract](../backend/dealdesk_phase2/m21_groq_contract.py)
uses the existing model ID/native function-call conventions, explicit trusted
system prompt, paired assistant/tool messages, bounded JSON, single call,
no structured-output-with-tools, and exact-value parsing. Its simulated
HTTP 400 uses the **existing** sanitized `_post` transport. Neither module
contains a credential lookup, metadata request or executable hosted sender.
Opaque SHA-256 aliases reduce casual ID exposure; they are **not** a
cryptographic anonymization guarantee, especially for small identifier spaces.
Only synthetic source-verified records are proposed; a real-customer/data-use
review would need separate authorization and stronger privacy controls.

**Remaining hard gates before a bounded hosted trial:** a reviewed, exact
Groq M2.1 adapter wired to the authorized LangGraph M2.1 stage; durable
exclusive owner directory and pre-send byte-hash reservation with completed
ledger exchange matching; terminal stop on HTTP/timeout/invalid output and
aggregate campaign token/request accounting; manifest-hash/credential/account
preflight and restart/no-replay tests for the *actual hosted path*; offline
end-to-end wire double and private CI. The current M2.1 runner explicitly
rejects Groq adapters. No one can approve or launch inference using this
proposal. Week 2 Pricing remains independently blocked.

**Recommended authorization sequence:** first complete and test those hard
gates offline; revalidate the proposed case digests in a fresh disposable
source; obtain Ali's confirmation of the selected secondary account's Free
tier and disabled billing, plus approval of a **new canonical manifest hash**,
account, model, case(s) and budgets. Begin with B01 only, then ask separately
whether to proceed to B05/N03; do not infer approval from this draft's
three-case maximum. No metadata GET or inference POST was performed here.

**28 October 2026.** This is a source-first review plan for the three distinct
Credit, Policy and Approval Routing AI investigations, not an executable
manifest, approved account charge or permission to call Groq. The current
M2.1 implementation is **offline-only** and has no executable hosted Week 3
adapter; its versioned prompts are not yet sent to a provider. The separate
[Week 2 Pricing blocker](week2-closure-audit.md) remains open: neither
terminal B01 Pricing request is eligible for replay. Week 3 cannot be used
to bypass or close that gate.

## Proposed cases and authority

Use a disposable database and the pinned Phase 1C checkout
`90c0bc8e285ee69262c7db826b786096a77ad004`. Proposed reference fixtures
are **B01** (ten-unit original; fixed delivery Policy hit and withheld route),
**B05** (dated split supply, fixed delivery approval hit and withheld route),
and **N03** (withheld route under a distinct adverse original). Before any
approval, independently re-read each fixture's sealed source, selected
credit/AR/payment rows, exact fixed hit IDs, fixed route and current
source/bundle digests; reject or replace a case if its actual evidence does
not exercise the claimed condition. Choose a separate source-verified
over-limit/stale-credit or hard-block case if one is required for that
behavior. Do **not** fabricate a blocked route's missing roles or claim a
populated fixed route test without an independently confirmed fixture.

Keep source-first expected findings and reviewer answers outside all model
messages. Evaluate each specialist separately against selected evidence and
the fixed result: exact citations, justified abstentions, unsupported claims,
wrong-subject/tool requests, withheld-route interpretation and preserved
human authority. Compare with the deterministic-only original, report all
started attempts and separate offline/mock results from hosted observations;
no accuracy claim is currently supported.

## Explicit gates to prepare for human approval

| Gate | Proposed boundary, **not permission** |
| --- | --- |
| Provider/model | Propose Groq Free `openai/gpt-oss-120b` as the already observed development model; check current model availability, tool support and service limits at authorization time. No paid fallback. |
| Credential | Propose explicit selection of the existing **secondary** local `GROQ_SECONDARY_API_KEY` for a fresh, separate child process, leaving primary untouched. This is not a claim that another key fixes Pricing. Obtain owner confirmation of Free tier/billing disabled and approval of this exact credential selection; never print/stage either value. |
| Per-case sends | At most **six sequential POSTs** for Credit, Policy and Routing combined (up to two per specialist); one authorized inspection per specialist; no parallel requests, automatic retries or reused terminal identities. If a case needs Configuration/Pricing/Fulfillment hosted inference, prepare a **separately budgeted and approved** manifest instead of silently adding those POSTs. Fixed original and independent offline prerequisites can be reused only when source-identical and explicitly approved. |
| Total campaign | At most three approved source-verified cases, **18 Week 3 POSTs total** (six per case). Proposed at most 512 configured completion tokens and 8,192 serialized request bytes per POST, plus a 24,000 reported-total-token post-send stop per campaign; verify prompt/schema actually fits before authorization, and lower limits when possible. No metered charge without explicit approval. |
| Preflight | Review a new narrowly scoped hosted adapter, trusted prompts, tool/result wire, exact claim schema and customer/AR/payment-field redaction for PII and prompt injection; complete offline protocol and PostgreSQL tests plus CI. Freeze a **new** assessment ID, case/run ID, sealed bundle digest, source-input digest, as-of cutoff, snapshot and source fingerprint in a canonical manifest with its SHA-256. Confirm empty isolated checkpoint and owner-only receipt directory, credential ownership/permissions and account/billing status. Require explicit Ali approval of the exact manifest hash, credential, model and budget **before** any send. |
| Stop | Terminal on any failed/unknown/timeout POST, malformed response, unavailable fixed prerequisite, source/manifest drift, insufficient credential/account preflight, incorrect tool scope, exhausted request/tool/token budget or withheld role inference. Reserve request identity durably before send; never resend an uncertain request, including after restart. Record only sanitized status, bounded field-level error category if separately approved, timing and available usage; no raw error body, customer PII, credentials or headers in Git. Stop the case/campaign on the first unclassified provider 400 rather than guessing a wire fix. |

Before converting this proposal into an executable manifest, decide whether
the first hosted test should isolate **only** Credit/Policy/Routing with fixed
original and offline prerequisite results, and independently verify that the
required evidence and hosted prompt transport are safe. A Week 3 result does
not establish a successful hosted Pricing turn; that requires a **new,
separately authorized** Week 2 validation after the rejection is classified.
