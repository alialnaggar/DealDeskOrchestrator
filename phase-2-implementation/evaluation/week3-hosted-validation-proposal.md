# Week 3 consolidated hosted validation — proposal, **not authorized**

## 28 October offline execution gate — proposed B01 authorization unit

The [final proposed manifest](week3-hosted-validation-proposal.json) is a
**single B01 assessment**, not the earlier three-case 18-POST campaign.
Canonical sorted-key compact-JSON SHA-256:
`a3043ee6ff916eb3d6b9afc3d9c1142ce0218dad5838a0187d1b1bdf75b9f8ca`.
It is **not authorized or executable as published**. The gated runner
requires an explicit `authorized_one_case` status, matching separately
approved hash, Free/billing-disabled confirmation, pinned original source,
owner-only directory, and the exact existing **secondary** key selection.
Changing status creates a **new hash**, which Ali must approve before any
send. A separate pre-existing **0600 owner-only**
`m21-approved-manifest.json` must bind the hash, assessment ID, selected
secondary credential and disabled-billing confirmation; the runner never
creates this record. The caller's `authorized=True` flag alone cannot
activate a send. No API call, including metadata, was made. B05, N03 and the additional
source-verified conflict cases need their **own separate manifest and
authorization**, not an inferred extension of the B01 budget.

The [gated M2.1 LangGraph entrypoint](../backend/dealdesk_phase2/m21_specialists.py)
now reuses the shared Groq `_post` transport, native-tool contract and
exclusive owner/`claim_and_call` durable receipt primitive. Six total POSTs
maximum per **one-case campaign**, two per specialist, one authorized read
per specialist, 512 completion tokens and 8,192 request bytes per POST,
4,096 reported prompt tokens per POST and a 24,000 **reported** aggregate
post-send token stop. Token accounting cannot retroactively prevent the POST
which crosses the threshold; it stops the case before another request and
marks the specialist error. Any transport, schema, source, budget, tool,
credential or response error is terminal; a reserved uncertain attempt is
never replayed. A completed first inspection may resume from its checkpoint
and completed access ledger; the tool-call descriptor and request digest are
checked before the second send. The checkpoint binds the manifest hash,
owner directory/inode and local SHA-256 credential fingerprint (never its
value); runtime rejects a different key, model, prompt, source or owner.
The manifest also freezes the M2.1 contract and permission versions, each
specialist's named read-only tool and the single-inspection ceiling.
Changing the key mid-assessment is terminal by design; its high-entropy
secret-derived fingerprint stays in the private checkpoint, so backup access
must be restricted. This is a trusted single-operator process boundary,
not a security sandbox against arbitrary Python with access to the key.
The published proposal status deliberately fails the hosted gate.

**Case coverage from sealed pinned Phase 1C reads, not expected-answer keys:**

| Existing source case | Verified selected evidence and fixed behavior | Current trial status |
| --- | --- | --- |
| B01 | Run `00000000-0000-4000-8000-000000018001`; bundle `720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`; source `64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`; fixed delivery approval-required hit, route withheld, no AR/payment rows. | Proposed **first** one-case manifest; no live validation yet. |
| B05 / N03 | Previously verified digests in the [preparation audit](week3-hosted-preparation-audit.md); B05 has a delivery approval-required hit, N03 no fixed Policy hit. Both routes withheld, no AR/payments. | Distinct follow-up manifests only, not included in B01 approval. |
| `CREDIT-LIMIT` | Pinned conflict pilot run `00000000-0000-4000-8000-000000260013`; bundle `f2ff063e6b1cf3fa6f09dd093606c825f0bcb35bd60089e69cf646f71fb3bd90`; source `ba2dad6061f746554dc4c8f133b229a23166478a8de1b8f7d782da1421211633`; **one selected AR**, zero payments, fixed Credit `infeasible` with `PO-BASE-CREDIT-CAP` blocker; routing withheld. | Existing synthetic source verifies Credit-limit/AR behavior; requires its own manifest, account review and approval. |
| `POLICY-CLAUSE` | Pinned conflict pilot run `00000000-0000-4000-8000-000000260015`; bundle `a07ec65e4f8e3d098ae44426d3072957db9d00513c50e28507517dea6308409d`; source `4196f6a83f02bba65617a81e6449ee152a9b544514a29ca73467299a3c1884b4`; legal-review approval-required Policy hit, **route visible** with `Regional_Manager` and `Legal_Compliance` in fixed sequence. | Existing synthetic source verifies visible-role explanation, not an AI approval; separate manifest. |
| `PRICE-FLOOR` | Pinned conflict pilot run `00000000-0000-4000-8000-000000260014`; fixed hard Policy hits include discount cap and margin shortfall. The discount-cap rule ID repeats across hits. | **Not hosted-eligible**: current M2.1 policy projection rejects duplicate refs rather than flatten hit scope. Needs a narrow, reviewed scoped-hit-reference design and tests; no rule change or invented finding. |

For both conflict runs, frozen cutoff is `2026-09-01T12:00:00+00:00`,
snapshot `CONFLICT-SNAPSHOT`. The pinned conflict SQL was loaded **only**
into a disposable PostgreSQL database alongside the pinned catalogue,
vertical pilot and compiled rules; no production pin or source data was
modified. Full field/role projections and redacted first/second-turn sizes
were checked locally (under 8,192 bytes). No current generated-test conflict
run supplies a selected payment; the pinned historical credit source files
are not equivalent to a source-verified original M2.1 run. To cover a
payment event, propose **one synthetic, dated payment row tied to an existing
conflict invoice in an isolated Phase 1C development fixture**, with a new
source/bundle digest and independent fixed-check review; obtain approval
before changing the pinned data. Do not silently port historical sources.

The [mocked gated-path methodology and remaining gaps](week3-hosted-preparation-audit.md)
distinguishes offline integration from an actual provider response. Before
seeking authorization, obtain Ali's account Free-tier/billing-disabled
confirmation for the selected secondary key, review current model/tool
availability and data-use terms **without performing a metadata call under
this task**, verify isolated B01 source and empty owner/checkpoint, run CI,
and approve the *new authorized-status* manifest hash and one-case budget.
First POST failure, invalid usage or missing safe evidence ends that case;
do not retry or move to the next case implicitly. Pricing remains a separate
Week 2 second-turn HTTP 400 blocker; neither old B01 attempt can be replayed.

## Historical 28 October preparation audit — pre-gate state

The superseded, unapproved three-case draft recorded B01/B05/N03 original identities, Groq
`openai/gpt-oss-120b`, explicit **secondary** credential selection, prompt
`m21-original-system-v1`, dormant native-tool wire
`m21-groq-native-tools-v1`, three separate specialist tool scopes, and the
limits below. Local frozen Phase 1C read verified all three bundle/source
digests, as-of timestamps and snapshot refs.
The proposal's canonical sorted-key compact-JSON SHA-256 is
`f3b71a75cd835234382f4e40af95a410679ab3278c9b5c463b3073b3bf11b291`;
this checksum identifies a **superseded unapproved draft**, not a send authorization.
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
[then-dormant Groq request/response contract](../backend/dealdesk_phase2/m21_groq_contract.py)
uses the existing model ID/native function-call conventions, explicit trusted
system prompt, paired assistant/tool messages, bounded JSON, single call,
no structured-output-with-tools, and exact-value parsing. Its simulated
HTTP 400 used the **existing** sanitized `_post` transport. At that point
neither module contained an executable hosted sender.
Opaque SHA-256 aliases reduce casual ID exposure; they are **not** a
cryptographic anonymization guarantee, especially for small identifier spaces.
Only synthetic source-verified records are proposed; a real-customer/data-use
review would need separate authorization and stronger privacy controls.

**Historical gaps before the new gate above:** a reviewed, exact
Groq M2.1 adapter wired to the authorized LangGraph M2.1 stage; durable
exclusive owner directory and pre-send byte-hash reservation with completed
ledger exchange matching; terminal stop on HTTP/timeout/invalid output and
aggregate campaign token/request accounting; manifest-hash/credential/account
preflight and restart/no-replay tests for the *actual hosted path*; offline
end-to-end wire double and private CI. The offline M2.1 entrypoint still
rejects Groq adapters; only the new one-case manifest gate above may send
after separate authorization. Week 2 Pricing remains independently blocked.

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
M2.1 implementation **was offline-only at that checkpoint** and its versioned
prompts had not been sent to a provider. The separate
[Week 2 Pricing blocker](week2-closure-audit.md) remains open: neither
terminal B01 Pricing request is eligible for replay. Week 3 cannot be used
to bypass or close that gate.

## Historical proposed cases and authority (superseded)

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

## Historical three-case budget (superseded; not authorizable)

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
