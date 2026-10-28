# Week 3 consolidated hosted validation — proposal, **not authorized**

**28 October 2026.** This is a source-first review plan for the three distinct
Credit, Policy and Approval Routing AI investigations, not an executable
manifest, approved account charge or permission to call Groq. The current
M2.1 implementation is **offline-only** and has no hosted Week 3 adapter;
its versioned prompts are not yet sent to a provider. The separate
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
