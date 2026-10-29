# Dormant typed-final hosted gate — security/readiness audit

**Current decision:** see [final owner decision sheet](#final-owner-decision-sheet-29-october-2026).
The dated v1 findings below are historical; do not interpret them as current
implementation defects after the subsequent remediation and serialization.

**28 October 2026 · branch `phase2-agent-implementation` · audited commit
`98c0ae6bc5e9d7e55971a2948b4fbd082b267a73`.** Read-only audit of
implementation and documentary Groq compatibility; no Groq request, account
metadata query, approval artifact, activation or CI dispatch. The working tree
also contains unrelated Gemma work, which was not changed.

## Decision: NO-GO for activation approval yet

The default production entry rejects a caller with `authorized=True` while
`HOSTED_ACTIVATION=False`; no normal graph imports the hosted entry point.
Nevertheless, this is **not an unconditional process-wide no-network proof**:
`run_typed_final_hosted(..., _mock_transport=MockTypedTransport(...))` permits
the entire hosted flow while the flag is false. `MockTypedTransport` accepts
caller-supplied callables; those callables can perform side effects, including
network calls, outside this module. The private-looking `_HOSTED_CAPABILITY`
is an importable Python object and the lower-level runner accepts it together
with a constructible `HostedTypedTransport`; underscore naming is not an
authorization boundary. Tests patch `_post` and use synthetic responders, but
that proves only those test invocations did not reach this HTTP sender. **Do
not enable the production flag or create a live approval yet.**

### What is verified in code

- The new exact-key manifest version, canonical SHA-256, status, fixed provider
  and model, permission version, named schema and SHA-256, prompt/wire versions
  and computed prompt hashes are checked. A separate exact approval JSON has
  owner UID, restrictive mode, no symlink and exact manifest digest/account
  fields; the directory is owner-only and locked. Old M2.0/M2.1 manifests and
  approval files cannot satisfy this new shape. These are *self-consistency*
  checks against current code, not independent owner authorization or an
  independent pinned prompt artifact.
- The production branch reads only `GROQ_SECONDARY_API_KEY`, checks credential
  shape, binds its SHA-256 into checkpoint state and sends to the fixed HTTPS
  chat-completions endpoint without redirects. A manifest `account_id`, caller
  `billing_disabled=True`, and approval `billing_disabled_confirmed=True` are
  **assertions**: none independently verifies which account owns the key or
  its current free-tier/billing status. No fallback key is read here.
- New PostgreSQL attempts are checkpointed as `reserved` before the durable
  owner-only receipt and send; receipt creation uses exclusive creation, file
  and directory sync. A reserved-only, failed, unparsed or inconsistent send
  cannot be replayed as a new attempt under the same identity. On restart the
  request digest, returned marker, evidence ledger and result are checked;
  Configuration uses a distinct `typed_configuration` receipt namespace. A
  crash between checkpoint reservation and file creation fails closed. No
  automatic retry or legacy terminal-tool fallback is present.
- For Pricing, the gate rejects any preexisting Pricing attempt/result and
  runs Configuration in the same pinned assessment before Pricing; returned
  Configuration attempts must match their own receipt, native request and
  scoped ledger. Credit has a fixed Pricing prerequisite but its targeted
  gate does not run Configuration AI. A previously failed Pricing attempt is
  not an eligible new hosted Pricing case.
- Pre-send count/configured-token limits are enforced for the selected
  specialist and, for Pricing, the Configuration+Pricing mixed run. Pricing
  plan 1 is at most **4 POSTs / 2,560 configured completion tokens**;
  plan 2, **5 / 3,072**; Credit targeted, **2 / 1,536**. The six-POST M2.1
  figure is planning only, not executable here. Response bytes and reported
  per-POST prompt/completion tokens are checked *after* return; the 24,000
  reported-token stop is not a hard pre-send spend cap, and failed sends may
  have unknown usage. Tests cover mock findings, abstentions, errors, one/two
  Pricing inspections, tampered receipts/identities, restart and no-replay.

### Blockers to correct and review before seeking activation

1. **Test bypass / trust boundary (high):** make the mock-only path unavailable
   to the installed production entry point (e.g. separate test-only injection
   at the runner/composition layer, with a production gate that cannot accept
   arbitrary sender objects). Prevent direct lower-level capability invocation
   from being mistaken for an authorization guarantee. Add a negative test
   proving no caller-supplied mock/callback can cause a send with activation
   off; document the process/OS trust assumption. Do not solve this by merely
   renaming the mock parameter or setting a different environment flag.
2. **Checkpoint timing (high):** manifest, pinned evidence and snapshot.next/
   stop checks run *before* `exclusive_owner`. Under the lock, the code checks
   selected result/attempt fields and database names but does not revalidate
   the full pinned state, manifest case or stop condition before Configuration
   or Pricing sends. Re-read and validate the complete checkpoint and adapter
   context under the lock, then ensure all other writers to this assessment
   use the same lock or equivalent serialized transaction. Test mutation in
   the pre-lock window and a concurrent writer; a second read alone is not a
   solution if other writers ignore the lock.
3. **Freshness and owner assertions (high/governance):** a boolean
   `fresh_databases_required` and database *names* do not establish fresh or
   isolated databases; allowlisted case ID and an unoccupied attempt list do
   not independently prove fresh assessment creation. Account/billing flags
   do not prove the actual key/account billing state. Specify an owner-verified
   fresh-db/case provisioning and account/credential attestation procedure,
   then bind/verify it as appropriate without querying Groq as part of this
   audit. Do not represent the current flags as verification.
4. **Receipt/restart and budget acceptance gaps (review):** extend offline
   crash-window/concurrent-writer tests around every checkpoint/file boundary;
   test manipulated returned usage and aggregate limits after restart, plus
   the exact four-POST B05 schedule and no fifth send. Review that all
   Configuration error/abstention paths fail closed and that there is no
   cross-protocol entry point for a previously selected assessment. The
   current 311-test regression (7 skipped) was reported for the implementation
   commit, not rerun in fresh PostgreSQL as part of this audit.
5. **Provider and CI evidence:** confirm current Groq strict-output/model/tool
   contract and exact schema through owner-reviewed provider documentation;
   provider acceptance is untested. Verify the existing private CI run for
   this commit via a read-only authorized GitHub channel and inspect failure/
   skip details. The local environment has no `gh` executable or discovered
   GitHub credential variable; `git fetch` confirms branch synchronization,
   **not CI status**. Do not dispatch a workflow to check it.

## Wire assessment (documentary only)

Inspection is a distinct, permissioned `tool_choice=required` request exposing
only the specialist inspection tool and `abstain`; Configuration retains its
older native wire. The final serializer constructs a separate two-message
system/user request, `response_format.type=json_schema`, strict schema with
all required fields and `additionalProperties=false`, no tools, tool-role
history, `tool_choice`, streaming or reasoning format, and a 1,024 configured
completion limit. The final result parser requires one stop response, bounded
usage/content and existing evidence/claim checks. This is consistent with the
**documentation cited in the approved design**, not proof of current provider
support or exact Groq acceptance. The first HTTP 400 must stop the case, not
trigger a fallback.

## Owner checklist — proposed first trial, **not approved**

- [ ] Review and approve fixes for blockers, focused/fresh-PostgreSQL tests,
      read-only private CI evidence and the **separate** activation diff. The
      minimal current code switch would change `HOSTED_ACTIVATION = False` to
      `True` in `typed_final_hosted.py`; **do not make that change alone**.
- [ ] Select one real account and confirm the actual secondary credential's
      account identity, free-tier status, billing disabled and any request/
      spending conditions by an owner-controlled process; no credential in
      manifest, approval, chat, Git or logs.
- [ ] Provision fresh isolated fixture and checkpoint databases and a fresh
      synthetic **B05 Pricing** assessment with frozen source fingerprint,
      snapshot, as-of, run, original and `inspection_plan=1`; create a fresh
      private owner directory only under a separately authorized procedure.
- [ ] Review the **exact canonical manifest and its immutable SHA-256 after**
      those identities and account are known; separately authorize only that
      one case, model `openai/gpt-oss-120b`, schema/prompt/permission versions,
      account and approved credential selection. No hash exists today.
- [ ] Approve at most **2 Configuration native POSTs + 1 Pricing inspection
      POST + 1 no-tools strict final POST = 4 POSTs / 2,560 configured
      completion tokens**, max 8,192 request bytes and 16,384 response bytes
      per POST, post-return reported-token checks, no retries, no fallback,
      no metadata GET and no subsequent campaign authorization. Stop on any
      400, timeout, invalid schema, failed inspection or uncertain receipt.

**Recommendation:** NO-GO to request activation approval today. Request owner
review of the proposed corrections first; after corrections and independent
verification, request activation approval and later *separate* approval of an
exact fresh-case manifest. This audit neither activates the gate nor grants
permission for a trial.

## Remediation after audit (28 October 2026)

**Implementation authorized, activation and hosted trial not authorized.**
The preceding sections describe the *audited v1 commit* and remain historical;
the following supersedes their implementation findings for the remediated
v2 gate. `HOSTED_ACTIVATION` remains `False`.

1. **Gate and mock isolation:** `run_typed_final_hosted` no longer accepts a
   mock or arbitrary sender argument. It checks activation/authorization/owner
   attestation before importing `_post` or reading a key. The synthetic sender
   is in `backend/tests/typed_final_hosted_harness.py`, which invokes an
   internal composition layer with a synthetic callable; mocked tests patch
   the live HTTP sender to assert it is never used. The internal Python layer
   remains importable by trusted in-process code; this is *not* a sandbox for
   arbitrary local Python/plugins. An adversarial caller with code execution
   in the same process can use other networking APIs, irrespective of this
   gate. Restrict deployment access accordingly.
2. **Post-lock checks:** under the OS owner lock, re-read the full checkpoint
   (including checkpoint ID), revalidate its sealed evidence, case manifest,
   stop/next state, private approval, database identity and checkpoint history.
   Reject any difference from the pre-lock snapshot before even writing the
   hosted selection. Before each new Configuration/typed reservation, recheck
   pinned state, fixed results, database identity and stop condition; existing
   attempt/ledger/budget checks still gate sends. A writer that ignores the
   lock can still race *after* a recheck: enforce shared lock discipline or a
   serialized transaction across all assessment writers before production.
3. **Freshness:** v2 binds actual PostgreSQL database OIDs as well as names;
   production requires the dedicated checkpoint database to contain no thread
   other than the selected assessment in checkpoint, writes or blobs. Every
   available checkpoint state for that thread is scanned for older terminal
   or conflicting protocol attempts, even if the latest state was cleared.
   Existing owner receipts are checked against a closed allowlist before
   recording the new hosted start. These are independent negative checks for
   reuse, **not** proof that the business database was newly created. A
   PostgreSQL database OID proves identity, not creation time; owner-controlled
   fresh database provisioning and access isolation remain required. The test
   harness permits a shared checkpoint database to run many synthetic cases;
   the production entry does not.
4. **Billing:** v2 requires `billing_state=owner_asserts_free_tier_billing_disabled`,
   `owner_billing_attested=True` and a private approval with that same owner
   attestation. These are statements by the owner, not provider verification.
   The gate verifies selected credential shape and binds its hash on restart;
   it cannot prove the key belongs to `account_id` or that the actual account
   currently has billing disabled. Ali must check the provider console/account
   and key identity through an approved manual channel *before* any activation
   or exact-manifest trial; do not infer state from string literals.
5. **Offline regression:** a fresh seven-database PostgreSQL run passed
   **314 tests, 7 skipped**. Focused hosted/offline/contract checks passed
   **16 tests**. Cases include mock B05 Configuration→Pricing findings and
   fixed-margin citation verification, Credit findings/abstention, one/two
   inspections, four-POST cap and restart no-replay; default terminal-tool
   paths retain their legacy tests. Adversarial tests cover injected transport
   rejection before credential access, pre-lock stop/fixed/ledger/sealed-bundle
   mutation, mutation after lock, tampered returned usage, cleared attempt
   history, database OID change, reused receipt, foreign checkpoint thread,
   interrupted sends, timeout and HTTP 400. No hosted inference or new CI
   workflow was run. Private CI status is **unverified**: no local `gh` client
   or discovered GitHub credential variable was available; `git fetch` cannot
   establish Actions status.

**Revised recommendation:** **conditional NO-GO for requesting activation
approval** until independent review confirms the shared-writer lock/transaction
discipline, owner evidences fresh business database and actual key/account
billing status, and private CI and current provider wire documentation are
reviewed. After those checks, Ali may separately consider a reviewed activation
diff; an actual first trial additionally requires a fresh B05 assessment,
actual account and exact v2 manifest hash, separate approval, at most **four
POSTs / 2,560 configured completion tokens**, and no retry/fallback. No such
manifest or live approval exists from this remediation.

### Interrupted-work recovery verification (29 October 2026)

The checkout at `projects/DealDeskOrchestrator` was verified on
`phase2-agent-implementation`, with `origin` pointing to the private
`alialnaggar/DealDeskOrchestrator` repository. Fetch and remote-head inspection
found both local and remote at `61bfc002962266f6ae2b89fb79688a0f65addec8`
before this remediation commit. The old regression log showed 314 tests and
seven skips, but an additional uncommitted pre-send ledger guard postdated that
log; the old result therefore did not verify the final worktree.

A new run provisioned seven distinct disposable PostgreSQL databases under the
isolated test server, pinned Phase 1C checkout
`90c0bc8e285ee69262c7db826b786096a77ad004`, installed the pinned schema
and reference rows into the four business fixtures, and compiled/applied the
pinned rules. The command was
`python -m unittest discover -s phase-2-implementation/backend/tests -p 'test_*.py' -v`
using the existing test virtualenv with distinct `DATABASE_URL`,
`CHECKPOINT_DATABASE_URL`, `REFERENCE_DATABASE_URL`, `M20_DATABASE_URL`,
`M20_CHECKPOINT_DATABASE_URL`, `M20_E2E_DATABASE_URL` and
`M20_E2E_CHECKPOINT_URL`. The complete run log is
`/tmp/opencode/dealdesk-recovery-regression.log`: **314 tests in 118.060 s,
OK (skipped=7)**. All seven skips belong to unrelated, untracked Gemma
read-only-checkpoint diagnostics; none is a hosted Pricing/Credit skip. Two
initial setup attempts lacked the locally packaged `psql` executable/library;
they stopped before running tests. No provider request or CI dispatch occurred.
The recovery commit carries `[skip ci]` because a normal push of backend
changes triggers the branch's GitHub Actions workflow; this offline-only
authorization does not permit a billable CI run. Consequently private CI
for the remediation commit remains unverified, not implicitly passed.

The last pre-send guard checks that the permissioned tool ledger retains its
pre-lock prefix and that subsequent entries belong to the selected assessment
and allowed specialist. Adversarial offline tests cover pre-lock ledger
replacement, post-lock fixed-state mutation, historical attempts and receipt
reuse. These do **not** establish atomicity against arbitrary writers that
ignore the owner lock. Separate confirmation of shared-writer serialization,
fresh business-database provisioning, provider/account billing state, current
wire compatibility and private CI remains outstanding. **NO-GO to request
activation approval** on this evidence alone; implementation completion does
not authorize activation or a manifest-specific inference trial.

### Shared-writer serialization review (29 October 2026)

**Writer inventory.** The original `orchestrator.py` LangGraph nodes write
sealed evidence, fixed results, assessment identity and stop state through the
PostgreSQL saver. Candidate/investigation continuations (`candidate_graph.py`,
`investigation_graph.py`, `hybrid_pack.py`, `hybrid_offline.py`) and the M2.0/M2.1
specialist continuations (`m20_specialists.py`, `m21_specialists.py`) can write
review/results, model-attempt and tool ledgers via `graph.update_state`.
`tool_ledger.py` and `model_attempts.py` append/reserialize reservations and
completions. `typed_final_hosted.py` selects the hosted protocol, writes its
Configuration base budget and invokes M2.0 Configuration; `typed_final_offline.py`
writes typed protocol, attempts, result and reviewer projection. Historical
Gemma modules and tests remain separate and uncommitted. The immutable original
business fixture is read through `phase1c_adapter.py`; fixture provisioning or
any direct SQL write to the business DB requires separate access control.

The typed-final hosted entry acquires its assessment owner-file lock; the
offline typed-final continuation uses its own lock when not called by the
hosted entry. Legacy hybrid/M2.0/M2.1 hosted paths use their respective
owner directories and do **not** share this new gate's lock. The
ordinary graph, candidate, tool-ledger and model-ledger writers do not acquire
it. The saver uses individual PostgreSQL transactions for checkpoints, not a
transaction spanning validation, reservation and network send; PostgreSQL
row-level locks on a prior checkpoint cannot prevent insertion of a new head.
The `claim_and_call` receipt writer uses an exclusive, fsynced file creation,
not a database lock; other local filesystem actors with owner privileges can
still alter receipts or private approval files. Direct SQL or checkpoint
clients with write privileges can bypass every application file lock.

**Observed race and correction.** Previously a writer could change the
checkpoint after the last post-lock read and before the send reservation; a
second writer could also change it between that reservation and the sender.
The new gate commits its checkpoint attempt reservation first, then opens a
separate PostgreSQL transaction on the dedicated checkpoint database and
acquires `SHARE ROW EXCLUSIVE` locks on `public.checkpoints`,
`public.checkpoint_writes` and `public.checkpoint_blobs`. These locks block
ordinary LangGraph and direct SQL checkpoint DML, including inserts of new
heads. Under the lock the gate revalidates pinned/fixed state, ledger and
database identity and compares the current checkpoint ID to the ID immediately
after its own reservation. Typed-final reservations also verify that their
parent checkpoint ID matches the pre-reservation validation. The locks remain
held through the receipt-backed send and are released after the sender
returns or fails. Lock acquisition has a two-second timeout: contention fails
closed with a terminal reservation, never a silent retry. Configuration uses
its existing reservation and validates
the head after that reservation, before send. A writer that commits before
the lock changes the head or validated state and prevents the send; one that
tries to commit during the send waits for the lock. Failed/uncertain receipts
and reserved attempts remain terminal, without replay or automatic fallback.
The table lock is limited to the **dedicated checkpoint database** required by
the production manifest, not a global lock or a change to legacy hosted paths.

**Adversarial results.** Synthetic, offline Configuration/Pricing and Credit
tests inject a concurrent stop after reservation but before `claim_and_call`'s
sender: no request is sent, and the Credit case remains terminal on restart.
Direct SQL on a second connection attempting `UPDATE public.checkpoints` during
each synthetic sender fails with PostgreSQL `lock_not_available` under a
400-ms lock timeout; normal bounded requests still finish. Focused hosted,
offline and contract checks: **18 passed**. A writer holding the checkpoint
table's write lock for over two seconds also causes a failed, unreplayable
reservation with no send. A fresh seven-database PostgreSQL
suite using the pinned Phase 1C source and the existing test virtualenv ran
`python -m unittest discover -s phase-2-implementation/backend/tests -p 'test_*.py' -v`:
**316 tests in 126.499 s, OK (7 skipped)**; all seven skips are unrelated
untracked Gemma diagnostics. The complete local logs are
`/tmp/opencode/dealdesk-serialization-focused.log` and
`/tmp/opencode/dealdesk-serialization-regression.log`. No live provider call,
metadata request or CI dispatch was made.

**Limits and decision.** This is a PostgreSQL checkpoint-DML serialization
guarantee only while the guard transaction is alive; it does not make direct
writers cooperative outside the send interval, prevent privileged actors from
altering the business database or owner directory, prove database creation
time, or independently verify account billing. Crash after a durable receipt
does not grant another attempt. A writer changing state after the lock is
released can invalidate the final review; subsequent restart/acceptance must
still validate checkpoints and receipts, and deployment must restrict writers
to the dedicated database. Private CI and actual provider acceptance remain
unverified. **NO-GO for requesting activation approval** pending owner-verified
fresh provisioning/account terms, current provider-wire review, independent
deployment/security review of database and owner-directory privileges, and
authorized private CI evidence. No activation or trial is approved here.

## Final owner decision sheet (29 October 2026)

**Basis and scope.** Branch `phase2-agent-implementation`, reviewed at
`a5add41930420c27e4522eb3f173e3e65bb77187`. The gate is still disabled;
the production entry has no mock transport, rechecks pinned state after the
owner lock, and serializes final validation/send against ordinary checkpoint
writers. The fresh seven-database offline regression passed **316 tests with
seven unrelated Gemma skips**; the hosted-focused suite passed **18**. These
are local results, not GitHub Actions results or provider acceptance. No new
code blocker was found in this read-only review. Do not reopen the corrected
issues absent a reproducible contradiction.

| Classification | Open evidence or decision | Acceptance boundary |
| --- | --- | --- |
| **Mandatory before enabling the gate** | Ali independently identifies the exact selected Groq account and credential, verifies its current free-tier status **and billing-disabled state** and applicable quota/terms, and approves the reviewed **activation diff** separately. Confirm the production process is trusted (no untrusted Python/plugins), owner-directory permissions and checkpoint/business-DB roles are restricted; review current official provider wire documentation for the selected model, tool request, strict no-tools schema and limits. | Record dated owner attestation and reviewer sign-off, without keys or approval JSON. If free-tier/billing-disabled status cannot be independently confirmed or the deployment trust boundary cannot be enforced: **NO-GO**. Another cost-control arrangement would need separate governance review; documentation compatibility is not actual acceptance. |
| **Mandatory before authorizing a specific trial** | Owner independently provisions fresh isolated synthetic B05 business/checkpoint DBs and a fresh assessment; records DB names/OIDs, role isolation, Phase 1C pin, source fingerprint/bundle digest, run/as-of/snapshot, empty prior attempts/receipts and exclusive checkpoint history. Prepare a new owner-only directory and a *proposed* exact v2 manifest hash, then obtain a separate one-case/budget/account approval before any approval file or send. | No historical failed assessment or reused checkpoint DB. Verify first checkpoint belongs only to that assessment, no foreign thread in checkpoints/writes/blobs, no previous incompatible history, and manifest matches the actual pinned state. Names, OIDs and a manifest boolean are identity/negative-reuse checks, **not** proof of creation time. |
| **Verifiable only during/after first trial** | Whether Groq accepts this exact model/inspection request and strict final schema, returns well-formed output/usage, and avoids the earlier second-turn 400. Measure actual sent POSTs, latency, usage and citations against the exact receipt/checkpoint history. | On 400, timeout, invalid response, budget/evidence error or uncertain send: stop that assessment, no retry, replay or fallback; do not infer success from offline wire checks. A successful trial does not establish population-level accuracy. |
| **Documented residual risk / explicit owner exception** | Private CI for the remediation commits is unverified: pushes carried `[skip ci]` to avoid a potentially billable workflow. The fresh isolated PostgreSQL run and adversarial tests give substantial **local** evidence for one narrowly controlled synthetic experiment, but not independent CI or deployment validation. Failed sends may have unknown provider usage; the 24,000 reported-token stop acts **after** returned responses. Privileged local/DB actors, business-DB changes and changes after a send lock is released remain outside its atomic checkpoint guarantee. | Ali may explicitly accept the CI-evidence gap for a single bounded trial after all other mandatory gates; do not claim CI passed. If independent CI is required by owner policy, seek separate approval to run/check it before activation. Restrict privilege and retain abort/no-replay rules. |

**Independent provisioning evidence (not yet collected).** A trusted operator
should record a dated, redacted creation/provisioning transcript or inventory
for both newly created databases, their OIDs and roles/ACLs, plus separate
first-use attestation of the checkpoint tables and assessment ID. Verify the
business fixture came from the separate checkout at
`90c0bc8e285ee69262c7db826b786096a77ad004`, and record schema/rule and
synthetic fixture provenance. Before any send, independently compare the run
ID, subject `M18-D-B05`, sealed bundle SHA-256, source input digest, as-of and
snapshot reference to the checkpoint and proposed manifest. Check that the
business fixture is access-isolated/read-only for the sending role and that
checkpoint history has no foreign assessment, terminal prior attempts or
receipts. The gate's database OID/history checks supplement but cannot replace
these records; PostgreSQL does not supply reliable DB creation time. Do not
publish connection strings, private approval data, or customer information.

**Credential check without disclosure (not yet performed).** Ali signs in
personally to the provider's account/billing and API-key consoles over an
owner-controlled channel, matches the selected key's masked identifier to
the intended account, checks plan/quota, billing status and whether payment or
automatic paid overages are enabled, then records the date, account identifier,
masked key identifier, relevant settings and any spending limits privately.
If the console cannot establish *free tier with billing disabled*, stop and
obtain clarification or a separately reviewed change to the gate's policy;
the manifest string `owner_asserts_free_tier_billing_disabled` is not proof.
Never show a key, credential hash, console secret, or screenshot with sensitive
fields in Git, logs or chat. No API or metadata request is needed for this
manual verification.

**Exact proposed first trial — NOT AUTHORIZED.** One new synthetic **B05
Pricing** assessment, `inspection_plan=1`, model `openai/gpt-oss-120b`:
**two Configuration native POSTs + one Pricing inspection POST + one separate
no-tools strict-schema final POST = at most four POSTs**, configured completion
limits **512 + 512 + 512 + 1,024 = 2,560 tokens**. Maximum serialized request
8,192 bytes and response 16,384 bytes per POST; reported prompt-token ceiling
4,096 on each returned POST and a 24,000 reported-token **post-return** stop.
No metadata GET, retry, fallback, Credit campaign, replay or second case.
No real account, assessment, approval record or immutable manifest hash has
been selected here.

**Recommendation: conditional NO-GO now.** There is no identified need for
another dormant-gate code change before *requesting* activation approval, but
owner account/billing attestation, deployment privilege review and current
wire-document review have not been evidenced. After those, Ali can decide
whether to accept the documented CI gap and separately approve a reviewed
activation change. Even an activation approval is **not** permission to create
a live approval artifact or send: fresh provisioning, exact-manifest review
and a separate one-case trial authorization are subsequent decisions.
