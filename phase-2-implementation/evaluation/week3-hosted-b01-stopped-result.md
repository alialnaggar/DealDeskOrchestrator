# Week 3 B01 first authorized hosted trial — Credit follow-up HTTP 400, stopped

**28 October 2026.** Ali explicitly authorized exactly the
[single-B01 manifest](week3-hosted-b01-authorization-candidate.json), canonical
sorted-key compact-JSON SHA-256
`6b4597c3c6969c12b419300952d77a24d7d579d9fcd72693b07df1b0824553aa`,
assessment `M21-WEEK3-B01-ae75c274-dd93-43b4-a6d8-8ba8681bab5f`, Groq
`openai/gpt-oss-120b` and the **existing secondary** local credential only.
Ali reconfirmed that the selected account is Free-tier with paid billing
disabled. No metadata GET, billing change, primary-key fallback, Pricing
experiment, other case, retry or second hosted campaign occurred.

## Pre-send identity and authority checks

Branch `phase2-agent-implementation` at `d89259cf8b3164d56154e1b936ba875f15b55b92`
matched origin; the unrelated uncommitted Gemma work was untouched. The
manifest hash, B01/run/assessment identity, three specialist tool scopes,
prompt/permission/wire versions, model, one-read ceiling and six-POST,
two-per-specialist, 512-completion-token, 8,192-byte and 24,000-reported-
token post-send ceilings matched the gate. The pinned Phase 1C checkout
`90c0bc8e285ee69262c7db826b786096a77ad004` had no tracked
implementation changes, and regenerated compiled rules matched the loaded
SQL byte-for-byte (SHA-256
`c7f9e658ff37dc86ff99cf4befcc8896eb0421d28e60a2bc68fc5e3241aac767`).
The ignored owner-only local `.env` contained a shape-valid secondary key
distinct from the primary; no key value or key-derived fingerprint is
published here.

Both named PostgreSQL databases and the owner directory were verified
**absent**, then created fresh: business
`dealdesk_w3_b01_ae75c274_fixture`, checkpoint
`dealdesk_w3_b01_ae75c274_checkpoint`, owner
`/tmp/opencode/dealdesk-w3-b01-ae75c274-owner` (`0700`). Actual business
and checkpoint connections returned their declared `current_database()`;
the business graph's connection factory was read-only. The fresh checkpoint
had no assessment. The business database loaded the pinned schema, reference
fixtures, complete nine-case synthetic fixture and pinned compiled rules.
The newly checkpointed original returned the approved sealed bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`,
source digest
`64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`,
cutoff `2026-09-01T12:00:00+00:00` and snapshot `M18-SNAPSHOT-B01`.
Six fixed findings and `needs_revision` original review matched the approved
preflight; there was no candidate, M2.1 attempt, M2.1 result, tool ledger
or owner receipt. **Only after every check passed**, a new private
`m21-approved-manifest.json` was created in the owner directory, owned by
the runner, mode `0600`, binding that exact hash, assessment, secondary-key
selection and disabled-billing attestation. It was not added to Git.

The previously stopped **M2.0** B01 Pricing assessments are distinct
identities and databases; neither was opened for a send or replayed. The
[Week 2 Pricing HTTP 400](m20-pricing-http400-offline-diagnosis.md) remains
an independent unresolved blocker.

## Actual bounded attempts and evidence

| Sequential POST | Specialist / response | Serialized request size | Request SHA-256 | Receipt |
| --- | --- | ---: | --- | --- |
| 1 | Credit native `inspect_customer_credit_evidence` tool call returned; authorized read of one selected credit-profile record completed. | **2,910 bytes** | `52277d55441d0be6be41da127f94e931d76f306a38c394375f69ac1c9e9deb11` | Durable `reserved` → `returned` |
| 2 | Credit second-turn request after its selected tool result: **HTTP 400**. No accepted model finding or abstention. Provider error body was not logged or classified further. | **3,814 bytes** | `24a848dc8bb4f5126701045645ac505258e1b104cebc08df75ca60b15c0ab19f` | Durable `reserved` → `failed`, sanitized `http_400` |

**Total: 2/6 POSTs**, both Credit; **zero** Policy and Routing POSTs. Each
serialized request hash was recomputed offline from the frozen checkpoint
and matches its reservation; both reconstituted model-visible requests were
under 8,192 bytes and excluded the raw deal/customer, snapshot and
commitment identifiers. The first response reported **668 prompt + 159
completion = 827 tokens**. The returned attempt's checkpoint records
**836 ms**; the terminal error receipt records **1,530 ms** of local send
time. Usage for the failed POST, any consumed provider quota and actual cost
are **unknown**, not zero. No token stop was
reached on the recorded return; the failed request cannot be retried.

Credit's only accepted **model action** was to request its scoped inspection.
The access ledger completed exactly one authorized selected credit-profile
read; it returned one verifiable ref. The model's second-turn error means
**zero validated AI claims**, no AI credit clearance and no evidence-backed
Credit finding. Credit's stored AI execution is `error`, reason
`provider_http_400`; Policy and Routing were not reached. The reviewer
projection is `m21_ai: stopped`, empty claims. The original fixed results
remain Configuration `confirmed`, Pricing `calculated`, Fulfillment
`needs_revision`, Credit `calculated`, Policy
`evaluated_with_interface_limits`, Approval Routing `withheld`. The original
review remains `needs_revision`; the candidate remains `not_started`. No
approval, waiver, reservation, production booking or delivery promise was
made.

Read-only post-run checkpoint inspection found exactly **two reserved model
attempts, one returned marker, one completed tool ledger entry and two
matching one-use receipts**. The HTTP 400 receipt is terminal; the second
request and assessment identity must **never** be replayed. No other
specialist ran after the failure. The private approval/owner/receipt files
and checkpoint remain outside Git. This demonstrates **preflight binding,
redaction, a real authorized Credit evidence read and safe error
containment**, but **not** a complete three-specialist hosted Week 3
assessment or model reasoning success. The cause of Credit's second-turn
HTTP 400 is unproven; any diagnosis should begin offline, and any future
hosted attempt needs a new reviewed contract, manifest, fresh identity and
separate authorization. No accuracy comparison is supported.

The last fresh pre-trial seven-database offline backend regression ran
**271 tests: 264 passed, seven unrelated historical Gemma skips**. Private
CI status and any provider billing record were not checked during the
trial; no claim of measured free usage or accepted accuracy is made.

**Offline follow-up:** The
[cross-specialist wire comparison](week3-cross-specialist-http400-offline-diagnosis.md)
reconstructed this Credit continuation alongside both terminal Pricing
continuations and accepted Configuration/Fulfillment controls. The provider
cause remains unclassified; this Credit assessment remains terminal.
