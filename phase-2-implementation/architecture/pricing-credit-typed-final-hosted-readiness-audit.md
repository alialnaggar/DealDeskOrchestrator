# Dormant typed-final hosted gate — security/readiness audit

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
