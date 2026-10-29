# First Pricing B05 typed-final trial — owner decision packet

**29 October 2026 · preparation only; NO-GO for a send today.** On branch
`phase2-agent-implementation` at `51249f2b7a07d2cf0ed557d1b313d48e7f935a2a`,
`HOSTED_ACTIVATION` is `False`. This packet creates neither an authorization
nor a live manifest, receipt, database, request or trial approval. The existing
[B05 v2 proposal](pricing-b05-typed-final-v2.json) is intentionally invalid
for execution; do not edit it into an approval. The separate Credit proposal
is not part of this trial. Preserve unrelated Gemma work.

## What is verified, and what is not

- Offline checks of the proposal against current runtime constants: exact
  version/key shape and `m1.2-v1` permissions; pinned Phase 1C
  `90c0bc8e285ee69262c7db826b786096a77ad004`; model
  `openai/gpt-oss-120b`; Pricing inspection prompt SHA-256
  `df4479e5d69af05790a20ae9ddb8983d0ab70a1a051ba51dd2aa7dab45fa6e5d`,
  Configuration prompt
  `d775c7546e2abc7c06e76f5cebb13dca4a892969c3b8e301198e1a97cc4fc74f`,
  final prompt
  `b225765db2f3004e37909711a669e284931e4b7ff387781a8ddfdb00a283bba7`,
  and strict required/closed schema
  `6aee636903e89ec78d0008b494c42e705478fd7299dd3c0e39e7ea6304f785fe`.
  The *canonical SHA-256 of the unfilled, non-authorizing proposal* is
  `8d16cecedd7d296acb9f68c94c15b6e201618e7b949589a905d3fe145d9f4319`;
  **this is not the future manifest hash**. The existing offline contract
  test rejects this proposal both at the validator and disabled production
  entry. `sha256(_canonical(manifest).encode()).hexdigest()` is the *future*
  exact-manifest hash, computable only when the fresh real identities exist.
- Four POSTs **maximum**: Configuration native tool turns `512 + 512`,
  Pricing one inspection turn `512`, separate no-tools strict-schema final
  `1,024`: **2,560 configured completion tokens** total. Pricing alone is
  two POSTs / 1,536 configured completion tokens. Each serialized request
  is capped at 8,192 bytes, response at 16,384; reported prompt tokens are
  checked against 4,096 per returned POST. The 24,000 reported-token stop
  applies *after* responses, not as a pre-send cost guarantee. No retries,
  metadata requests, fallback, replay, second case or Credit invocation.
- Deployment code selects **`GROQ_SECONDARY_API_KEY`**, not `GROQ_API_KEY`.
  The older `.github/workflows/phase2-m18-live.yml` selects the latter and
  cannot verify the typed-final credential. Neither variable was present in
  the inspection process. The ignored `backend/.env` exists and had current
  user ownership/mode `0600`; its content was not examined. File metadata
  cannot establish whether the secondary key is installed, which account it
  belongs to, its validity, or its billing state. Do not print or hash a key.
  Ali has **stated** that the intended Groq account is free-tier with paid
  billing disabled; this does not verify the *selected deployed key*.
- Public Groq documentation read without API authentication: [model card](https://console.groq.com/docs/model/openai/gpt-oss-120b)
  lists tool use and JSON Schema Mode; [structured outputs](https://console.groq.com/docs/structured-outputs)
  lists `openai/gpt-oss-120b` for `strict: true`, requires all object fields
  and `additionalProperties: false`, and says tool use/streaming cannot be
  combined with structured outputs. [Local tool calling](https://console.groq.com/docs/tool-use/local-tool-calling)
  documents function calls, `tool_choice: required` and local execution.
  The inspection wire uses required local tools; the **separate** final wire
  sends no tools and uses `response_format.json_schema.strict: true`. Groq's
  general examples sometimes suggest retries; this trial **forbids them**.
  [Public rate limits](https://console.groq.com/docs/rate-limits) are
  organization-level summaries, not this organization's current limits;
  owner must read their private console. Public examples do not prove the
  actual server will accept our exact schema or second turn; previous hosted
  HTTP 400s remain unresolved for this wire.

## Exact activation diff for review — **DO NOT APPLY**

Only after the owner's separate activation decision, in a *separate reviewed
commit/deployment* (path relative to repository root):

```diff
diff --git a/phase-2-implementation/backend/dealdesk_phase2/typed_final_hosted.py b/phase-2-implementation/backend/dealdesk_phase2/typed_final_hosted.py
--- a/phase-2-implementation/backend/dealdesk_phase2/typed_final_hosted.py
+++ b/phase-2-implementation/backend/dealdesk_phase2/typed_final_hosted.py
@@
-HOSTED_ACTIVATION = False  # Changing this requires Ali's separate activation approval.
+HOSTED_ACTIVATION = True  # Changing this requires Ali's separate activation approval.
```

Activating that code is **not** authorization for any assessment or POST; the
owner must separately approve the exact manifest and private approval record.
No alternate environment toggle, model, business rule or legacy path changes.

## Fresh B05 identity and exact proposed manifest — NOT YET INSTANTIABLE

Follow the existing [non-executing provisioning procedure](../typed-final-offline-trial-preparation.md#b-fresh-isolated-case-provisioning--owner-controlled-not-done-here).
Before any one-case authorization, owner/operator must privately retain a
redacted, dated transcript of *successful new* CREATE DATABASE operations
on an approved isolated cluster (distinct business and checkpoint DBs), DB
names/OIDs, owners/grants and read-only business access for the runner.
Names/OIDs alone do not prove creation date. Verify a **separate clean**
Phase 1C checkout at the exact commit above, with schema, rule-profile and
fixture-source SHA-256s; load only the synthetic B05 fixture using the pinned
CI/`backend/tests/m18_case_setup.py` recipe into the newly created business
DB. Preserve its loader and fixed-rule provenance; never run this against a
shared DB. Capture a *new original-only* `M18-D-B05` assessment and run ID,
sealed bundle digest, source fingerprint, as-of cutoff and snapshot reference
from its real checkpoint. Independently record first-use checkpoint table
evidence (`checkpoints`, `checkpoint_writes`, `checkpoint_blobs`) with only
that thread and all its history free of previous Pricing/Credit/terminal
attempts, foreign threads or receipts. Check private new owner directory
ownership, mode `0700`, runner OS/DB privileges and lack of approval/receipts.
Place redacted evidence in a private owner-controlled location, not Git/chat.

For a **new private proposal**, use the unchanged B05 v2 JSON *shape* and
constants. Replace null `case` fields with **exact** checkpoint values
(`assessment_id`, `run_id`, `bundle_sha256`, `source_input_digest`, `as_of_at`,
`data_snapshot_ref`); null `account_id` with the owner-verified Groq account
identifier; null `billing_state` with the runtime-required literal
`owner_asserts_free_tier_billing_disabled` **only after** account/key checks;
and null `execution_context` values with the independently recorded fresh
business/checkpoint database names and positive OIDs and absolute owner
directory. Keep `fresh_databases_required: true`, `specialist: pricing`,
`inspection_plan: 1`, `case_id: B05`, `subject_id: M18-D-B05`, and all prompt,
schema, model, permission and budget fields unchanged. For review, compute
the canonical hash of that **fully populated** proposal and compare it to
the pinned checkpoint and current code. Do not set `status` to
`authorized_one_case`, create `typed-final-approved-manifest.json`, or invoke
`run_typed_final_hosted` until the owner has authorized that *exact* case,
account, hash and four-POST budget. A runtime-accepted status or billing string
is not independent proof of authorization or billing.

## Separate decisions, shortest later execution and stop procedure

1. **Owner-only readiness attestation:** Ali matches the *masked identifier*
   of the deployed `GROQ_SECONDARY_API_KEY` to the intended Groq organization
   in their console, confirms that organization's currently free plan,
   billing disabled, actual quota, and absence of paid overage; independently
   reviews OS/Python/plugin trust, private owner directory and DB grants.
   Record this privately without secret/key hash. If unavailable: NO-GO.
2. **CI evidence exception:** decide explicitly whether the fresh local
   PostgreSQL tests suffice **for one synthetic case** despite private CI not
   being verified. If not, seek separate approval to run/check CI; do not
   represent `[skip ci]` as CI success.
3. **Activation:** after readiness and CI decision, Ali reviews/approves the
   *one-line diff above* and its deployment separately. Operator applies
   only that reviewed change, runs offline tests and verifies the deployed
   process picked up the enabled code; no sends just because the gate is on.
4. **Exact case authorization:** owner/operator first provisions and verifies
   the fresh DBs and one checkpoint as above, then reviews the *new* exact
   populated manifest/hash and separately authorizes **one B05 Pricing**
   assessment, four POSTs / 2,560 configured completion tokens. Only then
   create the owner-only approval record by the existing runtime contract,
   select the verified secondary credential in the authorized process, and
   invoke the existing gated `run_typed_final_hosted` once with that exact
   original graph, pinned adapter, manifest/hash, `specialist="pricing"`,
   absolute owner directory, `authorized=True` and
   `owner_billing_attested=True`. No blanket permission or unattended queue.
5. **Inspect without replay:** capture redacted stage receipts, reservations,
   checkpoints, returned usage, cited source IDs, original fixed results and
   final reviewer action; reconcile sends to at most four. On HTTP 400/429,
   timeout, unconfirmed/uncertain send, rejected citation, invalid usage,
   changed evidence or any quota/budget discrepancy: stop this assessment.
   Preserve receipts/checkpoint history, do **not** retry/resume/fallback or
   reinterpret a spent send as free. Do not grant human approval or delivery
   commitments. For a later trial obtain a new case and authorization.
   To roll back an approved activation, stop scheduling, coordinate in-flight
   activity, deploy a separately reviewed restoration to `False` and verify
   running processes use it; revoke unused owner approval under authorized
   procedure, never delete spent audit artifacts. No rollback is performed now.
