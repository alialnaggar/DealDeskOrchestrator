# Week 3 B01 authorized-status candidate — preparation only, **not approved**

The [one-case manifest](week3-hosted-b01-authorization-candidate.json) is
deliberately marked `authorized_one_case` so its **exact bytes and canonical
hash** can be reviewed. This status is **not Ali's approval**. No private
`m21-approved-manifest.json` exists for this assessment, and no inference POST,
model metadata GET, provider account query or billing change was made during
preparation. Do not treat this document as a command to send.

**Canonical SHA-256:**
`6b4597c3c6969c12b419300952d77a24d7d579d9fcd72693b07df1b0824553aa`
of sorted-key compact UTF-8 JSON (`dealdesk_phase2.hybrid_pack._canonical`).
Changing *any* field requires a new hash and separate owner approval.

## Frozen trial identity and proposed local execution context

| Item | Exact selection |
| --- | --- |
| Case / submitted deal | Synthetic B01; original `M18-D-B01`; no candidate |
| New assessment / checkpoint thread | `M21-WEEK3-B01-ae75c274-dd93-43b4-a6d8-8ba8681bab5f` |
| Phase 1C checkout / run | `90c0bc8e285ee69262c7db826b786096a77ad004`; `00000000-0000-4000-8000-000000018001` |
| Pinned source | Bundle `720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`; input `64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`; cutoff `2026-09-01T12:00:00+00:00`; snapshot `M18-SNAPSHOT-B01` |
| Fresh, **not yet created** business DB | `dealdesk_w3_b01_ae75c274_fixture` |
| Fresh, **not yet created** checkpoint DB | `dealdesk_w3_b01_ae75c274_checkpoint` |
| Private, **not yet created** owner directory | `/tmp/opencode/dealdesk-w3-b01-ae75c274-owner` (`0700`, owned by runner) |
| Provider / credential | Groq `openai/gpt-oss-120b`; **only** existing local `GROQ_SECONDARY_API_KEY`, never print or stage either key |
| Versions | `m21-original-system-v1` prompt; `m21-groq-native-tools-v1` wire; `m21-original-evidence-v1` evidence contract; `m1.2-v1` permission contract |
| Sequence / limits | Credit → Policy → Approval Routing; one scoped read and two sequential POSTs each; six POSTs total; 512 completion tokens, 4,096 reported prompt tokens and 8,192 serialized request bytes per POST; 24,000 **reported total tokens post-send stop**, not a guaranteed pre-send token cap |

Ali's [28 October secondary-account confirmation](week2-secondary-b01-hosted-result.md)
attested **Free-tier with paid billing disabled** for the second Groq account.
This is the previously confirmed status, **not** a current authenticated
account inspection or proof that it remains unchanged. Immediately before
any future send, Ali must affirm that the *same selected secondary account*
still has Free-tier access and billing disabled and approve the exact hash,
one-case maximum and any quota/cost implications. Do not try a metadata call
as a substitute, enable billing, fall back to the primary key, or infer a
successful model response from prior access.

## Source-only preflight and no-replay separation

A newly created **separate disposable preflight database** loaded the pinned
Phase 1C schema, reference fixtures, the complete nine-case synthetic M1.8
set and compiled rules. In-memory-only original assessment
`M21-B01-SOURCE-ONLY-AUDIT-ae75c274` (not the candidate thread) returned
the exact bundle/input/cutoff/snapshot above. Fixed results: Configuration
`confirmed`, Pricing `calculated`, Fulfillment `needs_revision`, Credit
`calculated`, Policy `evaluated_with_interface_limits`, Approval Routing
`withheld`; original candidate status `not_started`. Offline redacted first/
second-turn sizes were respectively Credit **2,894/3,756**, Policy
**2,849/3,616** and Routing **2,798/3,412** canonical bytes. These
are scripted tool-observation sizes, not provider token counts or a promise
about the actual hosted second-turn wire. No model was invoked.

Two earlier **M2.0** B01 Pricing assessments are terminal and distinct:
`M20-HOSTED-SPECIALISTS-B01-f9530345-979c-41ba-b6c6-9ec426059696`
([first stopped result](m20-configuration-pricing-hosted-result.md)) and
`M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7`
([second stopped result](week2-secondary-b01-hosted-result.md)). Their
checkpointed second-turn Pricing HTTP 400 reservations are not resumable.
This preparation neither opens nor changes those checkpoints or receipt
files; it uses a new M2.1 identity and **different** planned databases and
owner directory. The Week 2 Pricing blocker remains open.

**Before approval or send:** confirm both exact named trial databases and
owner directory were absent before creation (verified absent during this
preparation), then create **new isolated** business/checkpoint databases and
owner-only `0700` directory; never clone an old checkpoint or receipt. Load
the pinned schema, reference fixtures, full nine-case B01-compatible fixture
and pinned compiled rules into the business DB. Before constructing the
original graph, check both connection factories with PostgreSQL
`SELECT current_database()` against the manifest, that the checkpoint is
empty for this assessment, the owner directory has no receipt/approval file,
and that no old assessment ID is used. Run the six fixed specialists on the
new thread, verify source digests and fixed results again, and ensure no
candidate, model attempt or prior M2.1 result. **The current gate checks the
manifest's declared fresh-database requirement and exact owner-directory
argument, but does not introspect the graph's PostgreSQL connections or
prove the databases were freshly created. Those manual checks are mandatory
pre-send, not already demonstrated by the preflight DB above.** If any check
differs, stop and propose a new manifest/identity rather than patching the
approved hash or replaying a reservation.

## Private approval record — procedure only, **do not create yet**

After Ali explicitly approves the exact hash and reconfirms the same account
status, the authorized runner/owner may create a new **owner-only `0600`**
`m21-approved-manifest.json` inside the exact `0700` owner directory. Its
JSON content must be exactly these four fields (no secret value):

```json
{
  "assessment_id": "M21-WEEK3-B01-ae75c274-dd93-43b4-a6d8-8ba8681bab5f",
  "approved_manifest_sha256": "6b4597c3c6969c12b419300952d77a24d7d579d9fcd72693b07df1b0824553aa",
  "credential_env_selection": "GROQ_SECONDARY_API_KEY",
  "billing_disabled_confirmed": true
}
```

The runtime validates the owner-only record and the manifest hash in addition
to separate opt-in and billing-disabled flags, a single-process owner lock,
checkpointed request digests and fsynced one-use send receipts. A failed or
uncertain send is terminal; a successfully returned inspection can resume
only with its matched receipt, exact ledger and original context. The record
is **not created in Git** and must not be created until the next explicit
authorization. Before that, even the authorized-status candidate cannot
pass the gate. Verify the private directory's file modes/ownership and
absence of old receipts; keep raw provider/customer identifiers and secrets
out of published logs.

The outgoing wire exposes an aliased subject and only allowlisted, selected
evidence fields. Credit, Policy and Routing each have exactly one read-only
named tool; tool returns and subsequent messages are redacted, and claims
must match exact returned values. No model can approve or waive policy,
alter the submitted deal, override fixed rules, promise delivery or authorize
a financial action. B01 does **not** test nonempty receivables/payments,
credit-limit blocks, a hard Policy block or visible route roles; separate
source-verified cases and separate authorizations remain necessary. Private
CI and current Groq account/model access have **not** been verified here.

**Offline verification:** Focused M2.1 mocked-gate/wire tests passed
**12/12** with zero network requests. A fresh seven-database backend
PostgreSQL regression passed **271 tests: 264 passed, seven unrelated Gemma
skips, zero failures**. A read-only independent second-model review checked
the added manifest/context gate; follow-up fixes require a canonical
absolute owner path and reject malformed case entries. The review confirmed
that database freshness is a mandatory **external** pre-send verification,
not a capability the current graph gate proves. Private GitHub CI remains
unverified in this preparation environment.
