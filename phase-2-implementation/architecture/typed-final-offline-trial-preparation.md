# Typed-final Pricing/Credit — offline activation and trial preparation

**29 October 2026 · proposal only, not authorization.** Current security and
owner decision record: [readiness audit](pricing-credit-typed-final-hosted-readiness-audit.md#final-owner-decision-sheet-29-october-2026).
`HOSTED_ACTIVATION = False`; no live approval file or provider request was
created. The separate [Pricing B05](trial-proposals/pricing-b05-typed-final-v2.json)
and [Credit limit](trial-proposals/credit-limit-typed-final-v2.json) JSON files
have an intentionally invalid runtime status and null identities. They cannot
be submitted to the gate. Do **not** fill them in place or reinterpret a
proposal's hash as an approval. Credit is not scheduled.

## A. Activation change to review later — DO NOT APPLY NOW

The smallest prospective code change is a **separate, reviewed commit** in
`backend/dealdesk_phase2/typed_final_hosted.py`, changing only
`HOSTED_ACTIVATION = False` to `HOSTED_ACTIVATION = True`. The flag is a Python
constant, not an environment toggle. No other configuration, default agent,
legacy M2.0/M2.1/hybrid transport, specialist contract, graph edge, business
rule or credential selection should change in that commit. Approval must cover
the specific diff and deployment process after owner account/billing,
provider-document and privilege checks. Keep the flag false until then; a
code review proposal is not permission to create an approval record.

Rollback for a **future, separately authorized activation**: stop scheduling
new assessments; disable the gate in a separate reviewed commit restoring
`HOSTED_ACTIVATION = False`, and deploy the disabled version before any new
invocation. Coordinate in-flight activity instead of assuming a running
process picks up source changes. The owner should revoke unused private
one-case approval artifacts under an explicit authorized procedure and
preserve all spent attempt/checkpoint/receipt records for audit. An interrupted
or uncertain send is never retried, even after rollback. Do not switch to the
legacy hosted path or a different account as a fallback. Rollback changes are
not executed by this plan.

## B. Fresh isolated case provisioning — owner-controlled, not done here

The existing [Phase 2 CI workflow](../../.github/workflows/phase2-m1-contracts.yml)
and `backend/tests/m18_case_setup.py` already give a repeatable pinned schema,
reference-row, compiled-rule and disposable B05 fixture recipe; the isolated
seven-database regression demonstrates the test setup. They do **not** prove
freshness or isolation of a future *owner's* trial DB. No new database-writing
helper is justified by this offline planning task: it would require new
administrator access and could accidentally touch a shared DB. Instead,
require the following independently recorded creation-and-verification
sequence before a separate trial-authorization request:

1. Identify a dedicated PostgreSQL cluster and approved operator/role; record
   cluster identity and a redacted, dated transcript of **successful fresh
   CREATE DATABASE** operations for distinct business and checkpoint DBs.
   Never reuse a database, and never run the CI fixture loader against a
   production/shared DB. Restrict access to the trial roles; record owners,
   grants, names and database OIDs. `pg_database` OIDs prove identity, not age.
2. In a separate clean checkout, verify `git rev-parse HEAD` equals pinned
   Phase 1C `90c0bc8e285ee69262c7db826b786096a77ad004` and verify no
   tracked changes to the Phase 1C implementation. Record the pinned schema,
   rule-profile and fixture-source SHA-256 digests and the actual synthetic
   B05 loader provenance. Use the existing CI setup as a *recipe*, not as
   evidence that a future trial was provisioned.
3. Under the owner's authority, load the B05 synthetic fixture into the new
   business DB and create **one new** original-only B05 assessment with
   `subject_id=M18-D-B05`. Capture run ID, assessment/thread ID, business and
   checkpoint DB names/OIDs, source fingerprint, sealed bundle digest,
   as-of/snapshot reference and original fixed results from that exact
   checkpoint. Read the data through the pinned adapter; do not mutate
   business records during the hosted attempt. Prefer a restricted read-only
   business-DB role for the runner. The case is not fresh merely because its
   name is new.
4. Record a read-only preflight of checkpoint `checkpoints`,
   `checkpoint_writes` and `checkpoint_blobs` showing no foreign thread. Review
   **all** history for the selected thread: no older terminal protocol,
   previous Pricing/Credit attempt or returned-but-unparsed reservation.
   Verify the private owner directory is newly created, owned by the runner,
   mode `0700`, and has no prior receipt or approval file. Record evidence in
   a private, redacted owner-controlled location, not Git or chat. The
   production gate rechecks names/OIDs/history, but the owner's creation
   transcript supplies independent freshness evidence.
5. Only after the activation decision and all recorded identities exist,
   prepare a **new** exact v2 manifest with the real pinned case/account and
   canonical SHA-256. Present those *non-secret* identifiers, budgets and
   the hash for a **separate** one-case authorization. Owner-approved private
   approval JSON may be created only after that authorization, not as part of
   provisioning or this template review. No metadata GET or inference is
   required for these offline steps.

Abort on a mismatched pin, fixture digest, DB identity, manifest, earlier
receipt, foreign thread, incorrect subject, unresolved privileges or evidence
mutation. The existing offline tests exercise mismatched OIDs, cleared
attempt history, shared checkpoint database, pre-/post-lock mutation,
concurrent SQL writes and restart no-replay; do not claim they establish an
actual trial DB's creation date or account status.

## C. Boundaries and template validation

Pricing proposes **one new B05** with `inspection_plan=1` and model
`openai/gpt-oss-120b`: two unchanged Configuration native POSTs, one Pricing
inspection POST and one separate strict-schema no-tools final POST. Maximum
**4 POSTs / 2,560 configured completion tokens**, respectively
512 + 512 + 512 + 1,024. Per request 8,192 serialized bytes; per response
16,384 bytes; reported prompt ceiling 4,096 tokens per returned POST. The
24,000 reported-token stop is post-return, not a hard pre-send spend cap.
Credit's separate, **unscheduled** `CREDIT-LIMIT` proposal has one inspection
and one final POST (2 / 1,536 configured completion tokens), contingent on
its own fresh pinned case and separate review; it is not bundled with B05.
Neither proposal can be promoted by editing a status field alone. Both lack
account, billing attestation, assessment, run, evidence, DB and owner identity,
and neither includes a live approval file. `test_typed_final_proposals.py`
compares their version/shape, hashes and budgets to the runtime constants and
proves rejection by the current manifest validator and disabled entry. Full
mocked PostgreSQL tests cover Configuration prerequisites, bounded findings,
abstentions, failure/no-replay, manifest rejection and legacy-path isolation.
No fallback, retry or replay after uncertain sends.

## D. Owner-only checks before proposing activation

- Ali personally verifies the selected key's **masked** identifier and its
  Groq account in the provider console. Record a dated private attestation of
  account ID, free-tier status, **billing disabled**, key association, limits,
  relevant terms and whether paid overage/payment is possible. Do not send a
  key, credential hash, billing screenshot with secrets, or console token to
  the coding agent or Git. If the console does not establish both free tier
  and billing disabled, stop; a boolean in a manifest is not proof.
- Independently review the actual deployment account, Python/plugin trust,
  file permissions, OS ownership, DB grants and owner-only directory. The
  checkpoint write guard is limited to DML while the send transaction holds
  its table locks. Confirm the current official Groq model/tool/strict-schema
  documentation without making an API or metadata request; documentary wire
  compatibility is **not** acceptance of the exact trial request.
- Decide explicitly whether the local fresh PostgreSQL regression is enough
  to accept the **private-CI evidence gap for one synthetic trial**, or
  separately authorize CI. `[skip ci]` commits do not prove GitHub Actions
  passed. Then request the distinct activation-diff approval; after fresh
  provisioning, request the distinct exact-manifest B05 trial approval.
