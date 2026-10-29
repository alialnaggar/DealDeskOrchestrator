# B05 typed-final offline preflight: isolated fixture, NOT an executable trial

**29 October 2026.** Branch `phase2-agent-implementation`, starting at
`665f52d3cd691eb688aa05a595ce949b260ad6be`. This is a synthetic
offline provisioning exercise on the existing local `/tmp/opencode` **test**
PostgreSQL cluster, not approval of that cluster for hosted sending. No
activation, hosted approval file, Groq API request, runtime authorization
record or change to pinned Phase 1C/Gemma work occurred. The
[decision packet](pricing-b05-first-owner-decision-packet.md) supplies the
unchanged *unapplied* one-line activation diff and rollback procedure.

## Owner statements and exception (narrow scope)

Ali confirms **all** Groq API keys, including `GROQ_SECONDARY_API_KEY`, belong
to the intended free-tier setup; paid OpenAI API is reserved for later
production use, **not** this experiment. Do not request the same plan/billing
confirmation again. Ali also accepts the **unverified private-CI evidence gap
for this single bounded synthetic B05 experiment only**. This does not turn
`[skip ci]` into a CI pass, authorize other hosted experiments, enable the
gate or authorize a send. The nonsecret exact Groq **account identifier**
needed in the current manifest contract has not been provided; no substitute
identifier was invented.

## Independently checked local creation and source identity

The private operator evidence is in `/tmp/opencode/dealdesk-b05-trial-prep/`:
`provision.py` (one-time provisioning transcript), `creation-evidence.json`,
`independent-verification.json`, and `b05-proposal-not-authorized.json`.
The two JSON records are mode `0600`. On a separate database connection,
`pg_database` returned the following new names and OIDs, matching the
successful `CREATE DATABASE` transcript (OIDs alone do **not** date creation):

| Dedicated local test DB | OID | Owner |
| --- | ---: | --- |
| `b05_8970df6bd44d4b17_business` | 151614 | `ubuntu` |
| `b05_8970df6bd44d4b17_checkpoint` | 151615 | `ubuntu` |

Independent verification at DB-clock `2026-10-29 10:51:46 UTC` recorded
creation-record SHA-256
`9e6d82b14f5ddcf9e21b0749576283b2f510a9b32c5a25702c0a68995a742391`
and operator-script SHA-256
`07f9edac2ad3771578bf9ad3470905b1c04fa3ab7ddcdeca0c27f7b3100a391c`.
The separate Phase 1C checkout HEAD was exactly
`90c0bc8e285ee69262c7db826b786096a77ad004`; its tracked implementation
was clean (generated untracked `__pycache__` only). Schema SHA-256:
`637a8d78ef8ec15e912c02209ccac2ab04623aa37c44595eeed9df33d36bca0f`;
rule compiler SHA-256:
`1fc921e002a38fba66c3572dd1470ff876db031aa88c5d0dd8cf8886c2f1856a`;
compiled rule SQL SHA-256:
`c7f9e658ff37dc86ff99cf4befcc8896eb0421d28e60a2bc68fc5e3241aac767`;
Phase 1C fixture loader SHA-256:
`21c3997d68e288df0407a5827f4d31f809aee837a16d4fc1adc64418a33791e4`;
Phase 2 synthetic B05 fixture SHA-256:
`d1ffab448fb114aa9e2b5442f77c745ada03b4503380d37ee9985ae675f0ceee`.
Only the synthetic `M18-D-B05` M1.8 deal was loaded (alongside pinned
reference rows). No production deal/database was touched.

The original-only LangGraph assessment/thread is
`TYPED-B05-OFFLINE-PREP-8970df6bd44d4b17`, Phase 1C run
`00000000-0000-4000-8000-000000018005`, subject `M18-D-B05`, as-of
`2026-09-01T12:00:00+00:00`, snapshot `M18-SNAPSHOT-B05`. The fresh pinned
bundle SHA-256 is
`a80b5b99f5d09ca2568010f8c26867413f4049097173e72ff229661e7a830df9`;
source-input digest is
`7859cec62db30f44f2777a90158cef6bd8d75fe57e7373595642959313e93b39`;
fixed-decision SHA-256 is
`a94d2cf8629e7694dfcf73ab5b3b12fd0eb4793c0a14e678fb1c6b93c43ac356`.
The fixed original status is `needs_revision`, not approval. A fresh
read-only source reread matched the checkpoint's pinned context. This work
proposed **no AI finding**; deterministic rules alone produced the status.

Before the graph, all three checkpoint tables were empty. After completion,
`checkpoints`/`checkpoint_writes`/`checkpoint_blobs` held **11/42/22** rows,
respectively, and no foreign thread. All 11 graph-history states belonged to
this assessment; no prior M2.0/M2.1/typed-final hosted attempt or owner start
was found in that history. The private owner directory is
`/tmp/opencode/dealdesk-b05-trial-prep/owner_8970df6bd44d4b17`, owned by
the process user, mode `0700` and empty (no receipt or approval record).

## Manifest and runtime-contract verification, without authorizing

`b05-proposal-not-authorized.json` has the v2 template's **actual case,
database/OID and owner-directory fields filled**, but deliberately retains
`status: proposal_not_authorized_not_executable`, `account_id: null`, and
`billing_state: null`. Its canonical SHA-256 is
`e9cc5e27517092c26ad56451ebc4c3d546d25ea11f0c76f973d4e71aa9090dc2`.
**This is not an executable manifest hash.** The runtime validator rejects
that persisted proposal. An *in-memory synthetic* account/status substitution
(not stored or used for sending) passed the exact runtime manifest validator
against the real checkpoint, DB identities and owner directory. The recorded
Pricing, Configuration and final prompt hashes, schema hash, `m1.2-v1`
permissions and budget were checked again against current code; the gate
remains `HOSTED_ACTIVATION = False`. Seven focused offline contract/gate tests
passed. No private CI was run; no paid API calls occurred.

The proposed limit remains **one B05 Pricing case, at most four POSTs / 2,560
configured completion tokens**: Configuration 512 + 512, Pricing inspection
512, separate strict-schema no-tools final 1,024. No retry, replay, fallback,
metadata request, Credit case or production OpenAI API use. Even after an
approval, a 24,000 reported-token stop is post-return, not a pre-send cap.

## Genuine blockers before a final executable manifest or activation

1. The exact **nonsecret Groq account ID** is absent. The owner-confirmed
   key/plan association is accepted; this is solely the still-missing value
   for the manifest's required `account_id`. A populated executable manifest
   and its exact canonical hash cannot be truthfully calculated without it.
   Do not use a synthetic label as the actual account ID.
2. This disposable test cluster uses local **`trust` authentication** and
   the DB owner/runner role `ubuntu` is a **superuser**. Merely naming a fresh
   DB or checking the owner directory does not provide the restricted business
   reader and checkpoint writer boundary required by the decision packet.
   Do not enable the gate against this cluster or reuse this manifest for a
   hosted send. Reconfiguring the cluster/host or moving to an approved
   restricted deployment requires a separate, authorized environment review;
   no server authentication, service or system settings were changed here.
   A different approved cluster requires new DB/assessment identities and a
   **new** manifest hash. This is not a reason to weaken any runtime checks.

Once an appropriately isolated deployment and exact account ID exist, take
fresh creation/privilege evidence and reassess the case's source and complete
checkpoint/receipt history. Construct the **new** v2 manifest with those
verified identities; compute `sha256(_canonical(manifest).encode()).hexdigest()`
and seek **one explicit owner decision approving the reviewed activation diff
AND the exact one-case manifest/hash and four-POST budget**. Until then this
is a NO-GO, despite the scoped CI exception. After authorization, activation
and approval-file creation are distinct operator actions; stop on any
uncertain send, preserve the audit trail and restore the flag to `False` in a
separately reviewed rollback deployment without replaying spent attempts.
