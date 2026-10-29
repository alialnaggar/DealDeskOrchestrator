# B05 Pricing restricted deployment preflight — NOT authorized

**29 October 2026; branch `phase2-agent-implementation`.** Supersedes the
*environment* in [the earlier trust-cluster exercise](pricing-b05-fresh-preflight-2026-10-29.md),
not its test conclusions. No runtime authorization file, Groq request,
activation or billed CI. The owner has already confirmed that all Groq keys,
including the selected secondary key, belong to the intended free-tier setup;
do not ask again for billing confirmation. The owner's private-CI gap exception
applies **only to one bounded synthetic B05 experiment**, not a CI pass.

## Account field: exact remaining owner-only value

`typed_final_hosted._validate_manifest` requires `account_id` to be a
**nonempty string of at most 100 characters**; it binds that literal into the
manifest's canonical SHA-256, checkpoint owner state, and private approval
record. The code does **not** derive it from a key; it cannot verify Groq
ownership from the string. Neither the authorized process account/organization
configuration field nor the ignored backend `.env` supplied an account ID;
the archived proposals and deployment artifacts have no actual account ID.
No credential contents or hashes were published or sent. Ali needs to provide
the **nonsecret exact Groq organization/account identifier for the intended
account**, for the v2 JSON field `account_id`. Do not substitute a key name,
masked key, synthetic test ID or a billing statement. This is a field-value
request, **not** a repeated plan/billing review. Without it there can be no
exact final manifest digest, even with all other fields pinned.

## Isolated restricted B05 (private local test installation)

The existing PostgreSQL 16.15 binaries were used in a **new** directory
`/tmp/opencode/dealdesk-b05-scram-9c9794347b09` (mode `0700`), with new data
and socket directories (`0700`), local `scram-sha-256` password authentication
and `listen_addresses=''` (no TCP listener). No existing/shared cluster HBA,
service, VM or system dependency was changed. The one-time operator script and
private redacted creation and independent verification records are:

```
/tmp/opencode/dealdesk-b05-secure-create.py
/tmp/opencode/dealdesk-b05-scram-9c9794347b09/provisioning-evidence.json
/tmp/opencode/dealdesk-b05-scram-9c9794347b09/independent-verification.json
/tmp/opencode/dealdesk-b05-scram-9c9794347b09/b05-proposal-not-authorized.json
```

All private JSON, inventory and password-file modes are `0600`; no password,
credential hash or connection string is in Git. The creation transcript
(operator-script SHA-256
`9a836b24403134933a1302a39a8364c3ad209ce71a380b1965c6fc9a9f8cf277`,
creation-record SHA-256
`c9be9344f16bd3c74e165648a2df45ad208fcd0d8c8f0c90c0ad94a216f4d8cd`)
shows the successful *new* database creation, independently confirmed by
`pg_database` names/OIDs; the DB-clock observation was
`2026-10-29 10:59:21 UTC` (OIDs alone do not establish creation time).

| New database | OID | DB owner |
| --- | ---: | --- |
| `b05_business_2230473070` | 16385 | `b05_bootstrap_53c9a22f` |
| `b05_checkpoint_c43d6b2467` | 16386 | `b05_bootstrap_53c9a22f` |

The bootstrap superuser role is **NOLOGIN** after provisioning; its bootstrap
password was not retained. `b05_runner_ecd55360` is LOGIN but not SUPERUSER,
CREATEDB, CREATEROLE or REPLICATION. It has CONNECT only to these two DBs,
not `postgres`, `template0` or `template1`. Actual attempts to connect to
`postgres` and `template1` with the runner password were denied. An explicitly
incorrect password was rejected by SCRAM. The runner gets business schema
USAGE, SELECT on pinned source tables and EXECUTE on compiled rule functions,
no business UPDATE/DDL and a read-only default transaction. It receives
checkpoint SELECT/INSERT/UPDATE/DELETE and the exact runtime checkpoint lock,
but **no CREATE on the checkpoint schema**. Negative UPDATE/DDL and ALTER ROLE
attempts were rejected. The graph, pinned evidence reread and gate's exact
`_checkpoint_send_lock` ran under that restricted login.

The checkpoint schema was initialized by the bootstrap role *before* its
login was disabled. `thesis_checkpointer()` always calls `saver.setup()`, which
attempts `CREATE TABLE IF NOT EXISTS` even after installation, and fails for a
no-DDL runner. **For this already-initialized restricted cluster**, use the
existing `PostgresSaver.from_conn_string(checkpoint_dsn)` context directly
with `LANGGRAPH_STRICT_MSGPACK=true`; do not call `.setup()` as the runner or
grant CREATE to make it pass. This is an operator connection choice, not a
graph, schema, AI contract or runtime authority change. The
[offline rechecker](../../backend/tests/verify_b05_restricted_preflight.py)
uses precisely that pattern; it does not send or write an approval record.

The separate Phase 1C checkout is exactly
`90c0bc8e285ee69262c7db826b786096a77ad004`, with no tracked changes.
Pinned schema SHA-256:
`637a8d78ef8ec15e912c02209ccac2ab04623aa37c44595eeed9df33d36bca0f`;
compiled rules SHA-256:
`c7f9e658ff37dc86ff99cf4befcc8896eb0421d28e60a2bc68fc5e3241aac767`;
synthetic B05 fixture SHA-256:
`d1ffab448fb114aa9e2b5442f77c745ada03b4503380d37ee9985ae675f0ceee`.
Only B05 of the nine M1.8 deals was loaded, with the pinned reference data.

**Fresh original assessment:** `TYPED-B05-SCRAM-8ba93fddd647`, subject
`M18-D-B05`, run `00000000-0000-4000-8000-000000018005`, as-of
`2026-09-01T12:00:00+00:00`, snapshot `M18-SNAPSHOT-B05`.
Sealed bundle SHA-256:
`a80b5b99f5d09ca2568010f8c26867413f4049097173e72ff229661e7a830df9`;
source-input digest:
`7859cec62db30f44f2777a90158cef6bd8d75fe57e7373595642959313e93b39`;
fixed-decision SHA-256:
`a94d2cf8629e7694dfcf73ab5b3b12fd0eb4793c0a14e678fb1c6b93c43ac356`.
Fixed original status: **`needs_revision`**, not approved. The 11 graph
history states and 11/42/22 checkpoint/write/blob rows belong exclusively
to this assessment; no past M2.0/M2.1/typed-final attempts, returned sends,
foreign threads or receipts. Source reread matches the original checkpoint.
`/tmp/opencode/dealdesk-b05-scram-9c9794347b09/owner` is mode `0700`, empty
and owned by the process user. No AI proposal was generated here; only fixed
rules assessed the deal.

## Offline recheck, manifest and boundaries

From the repository root (no provider credential needed):

```sh
PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests \
  /tmp/opencode/dealdesk-test-venv/bin/python \
  phase-2-implementation/backend/tests/verify_b05_restricted_preflight.py \
  --inventory /tmp/opencode/dealdesk-b05-scram-9c9794347b09/provisioning-evidence.json
```

The separate private B05 v2 proposal has actual assessment, DB names/OIDs
and owner path, but **deliberately** retains
`status=proposal_not_authorized_not_executable`, `account_id=null` and
`billing_state=null`. Its canonical SHA-256 is
`376c79b01eb95db2b243246d535008fcf8af9b1dcd88284ddcd41c2c0b64b15a`;
**this is not an executable manifest hash**. Its prompt/schema/permission
constants, four POSTs / 2,560 configured completion tokens and case identity
were rechecked offline. The runtime rejects the persisted proposal; an
in-memory synthetic account/status substitution (never stored) passed its
structural validator against the real restricted checkpoint; the private
approval file is absent and the activation constant is still `False`.
Seven focused gate/contract tests passed; private CI remains **unverified by
owner exception**, not passed. No retry/fallback or provider request.

This test proves *database-role* isolation and working checkpoint DML/lock,
not protection against a compromised process or its OS user (which owns the
private data directory), nor against direct authorized DML to checkpoint
tables outside a send lock. These are the existing documented trust/atomicity
limits; a runner needs checkpoint writes for LangGraph. Restrict the actual
deployment's OS/Python/plugin access, preserve the dedicated cluster and
operator evidence, and recheck identities/history immediately before any
authorized send. A change of deployment/role/DB requires fresh provisioning
and a new manifest/hash. Do not call the trial executable yet.

## Owner decision after the missing field is supplied

The [exact unapplied activation diff and rollback](pricing-b05-first-owner-decision-packet.md#exact-activation-diff-for-review--do-not-apply)
remain solely `HOSTED_ACTIVATION = False` → `True`, with reviewed restoration
to `False` if later rolled back. After the nonsecret `account_id` value and
deployment trust review, populate that field and the existing owner-confirmed
free-tier literal in a **new** one-case v2 manifest, calculate the *new*
canonical SHA-256 and seek explicit owner approval of **both** the reviewed
activation and that exact B05 manifest/budget. Only following that decision
may an operator enable the gate and create the matching private approval;
neither operation is performed here. At most two Configuration native POSTs,
one Pricing inspection POST and one strict no-tools final POST; no retry,
replay, fallback, Credit case or paid OpenAI API. On any uncertain send, stop,
preserve checkpoint/receipt history and coordinate a reviewed rollback.

## Account-ID contract clarification and final offline proposal (follow-up)

The **original** [hosted infrastructure contract](../pricing-credit-typed-final-hosted-infrastructure.md#proposed-first-hosted-acceptance--not-authorized)
calls for a single owner-identified **Groq account whose actual ID** Ali
confirms, explicitly excludes the test-only account ID, and requires that
account ID in the final approved manifest. The later [v2 audit](../pricing-credit-typed-final-hosted-readiness-audit.md#remediation-after-audit-28-october-2026)
states that the gate cannot prove the key belongs to the manifest's
`account_id`. This is a **provider organization/account identity for an owner
assertion and immutable binding**, not a freely chosen application owner label.
Its runtime check is deliberately only string type, nonempty and ≤100
characters. The exact **value** must match in the manifest, private approval
JSON, checkpoint `typed_final_hosted_start` and hosted protocol binding;
the canonical manifest SHA-256 binds all manifest fields across recovery.
`run_typed_final_hosted` selects
`GROQ_SECONDARY_API_KEY` to authenticate the POST, but it never sends
`account_id` to Groq or derives it from the key. The test fixture's
`synthetic-test-account` exercises **shape/equality only**, not semantics.
Accepting an arbitrary label because it passes Python validation would
contradict the written owner-identified-account contract. Changing to an
application-defined identifier would require a separate architecture decision;
no such change is proposed.

The provider's public [Organization Settings page](https://console.groq.com/settings/organization)
labels **Organization ID** as the unique identifier (the Organization name
is explicitly non-unique); it says the ID is used in invoices/communications
and *not* needed for API calls. Ali can **sign in personally**, select the
organization associated with the secondary key using the Console's
[Organization / Projects selector](https://console.groq.com/docs/projects),
then open **Settings → Organization → General → Organization ID** and copy
*only that nonsecret ID*. Do not send the API key, a key hash, screenshot or
console session token; no metadata request is necessary. If this Console
does not display an Organization ID, report that exact UI limitation rather
than guessing from an organization name, project name or key identifier.
No organization ID was present in authorized local configuration, previous
documented deployment evidence, or the trial templates.

After the owner's already recorded free-tier/billing-disabled statement, a
**new, still non-authorizing private proposal** was prepared at
`/tmp/opencode/dealdesk-b05-scram-9c9794347b09/b05-proposal-owner-statement-not-authorized.json`
(mode `0600`). It is exactly the previous preflight proposal except
`billing_state=owner_asserts_free_tier_billing_disabled`; its *proposal-only*
canonical SHA-256 is
`a90b1d6dd9932ed25dea492034fee181e880fb74d004756ea6779f42670549b7`.
It retains `account_id=null` and
`status=proposal_not_authorized_not_executable`; it is **not** an executable
manifest or owner approval, and its hash must not be approved as one. The
original private creation/proposal records were not overwritten. All actual
DB/assessment identities, prompt and schema hashes, permissions and
**four POSTs / 2,560 configured completion tokens** remain unchanged. An
offline field-by-field comparison to the earlier proposal and seven focused
contract/gate tests passed; no Groq/metadata call or CI dispatch. Once the
actual Organization ID is supplied and identity/history remains valid, add
that exact value to a **new non-authorizing** proposal. For the owner's
decision, calculate a separately labeled **would-be runtime hash** in memory
from the *exact* final JSON bytes, including the future
`status=authorized_one_case`; do not persist that executable-status JSON,
create an approval file or use its hash to send before explicit approval of
those bytes and the activation diff. Hashing the still-non-authorizing
proposal instead would produce a **different hash**, which cannot be used as
the runtime approval digest. The one-line activation diff remains unapplied.
