# Authorized Credit-only B01 HTTP 400 diagnostic — terminal unknown category

**28 October 2026. Single hosted trial completed and stopped.** Ali explicitly
approved [this exact manifest](week3-credit-http400-diagnostic-candidate.json),
compact sorted-key JSON SHA-256
`592110acd76a914f56b55f7d23d8fa78819c95015a4444512aada50d47c3c8e9`,
assessment `M21-DIAG-B01-31b981ed-d364-422c-91ea-9a5a2c6c661b`, the
existing **secondary** Groq account confirmed Free-tier with paid billing
disabled, `openai/gpt-oss-120b`, and only the bounded, allowlisted HTTP error
capture for this trial. There were no metadata checks, other cases,
specialists, retry, primary-credential fallback or later hosted trial.

## Pre-send source, isolation and authorization

Branch `phase2-agent-implementation` at
`6942dbde7620889b2fba75d114251445fc97ae56` matched origin;
unrelated local Gemma work was left alone. The manifest SHA-256, single Credit
tool scope, two-POST ceiling, 512 completion tokens and 8,192 serialized
request bytes per POST, 24,000 reported-total-token post-send stop, prompt,
wire and permission versions were checked. The pinned Phase 1C checkout was
clean at `90c0bc8e285ee69262c7db826b786096a77ad004`. Regenerated compiled
rules matched the previously reviewed SQL byte-for-byte (SHA-256
`c7f9e658ff37dc86ff99cf4befcc8896eb0421d28e60a2bc68fc5e3241aac767`).
Only the pre-existing owner-only secondary credential was selected and its
local shape/difference from the primary verified; no key was printed or
committed.

The fresh fixture and checkpoint databases and owner directory were checked
absent, then created as declared by the manifest. Each actual database
connection returned its distinct declared database name. The business reader
used a read-only connection. The pinned schema, reference rows, full nine-case
synthetic fixture and compiled rules produced B01's approved sealed bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`
and source-input digest
`64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`.
The new checkpointed original had **all six** deterministic findings and an
entire fixed decision identical to the previous source-identical B01
assessment: Configuration `confirmed`, Pricing `calculated`, Fulfillment
`needs_revision`, Credit `calculated`, Policy
`evaluated_with_interface_limits`, Approval Routing `withheld`; original
review `needs_revision`, candidate `not_started`. Before send there were zero
M2.1 attempts, model results, tool entries or hosted owner state. The first
serialized request was checked for redaction, scoped tools, model and budget.
**Only after these preflight checks passed** was the private `0700` owner
directory given a `0600` approval record binding the exact manifest hash,
assessment, secondary selector and disabled-billing attestation. The record,
credential and checkpoint were not added to Git.

## Observed two-turn trial

| Sequential inference POST | Canonical bytes / SHA-256 | Result / durable receipt |
| --- | --- | --- |
| 1 — Credit inspection | 2,909 / `acad9266fa5a45aa3154925453cf15b49f1de7c5773ee7af56cf6e3d0188702a` | Native `inspect_customer_credit_evidence` call returned; `reserved → returned`. One authorized selected credit-profile read completed and returned one evidence reference. Provider-reported usage: **669 prompt + 122 completion = 791 tokens**. |
| 2 — Credit continuation | 3,813 / `c533f4ee91afc7940d377c1eb47d6704cc37e6254bdafb7c49f7bd3b161dd2ec` | **HTTP 400; stopped.** Receipt `reserved → failed`, original `http_400`, local elapsed time **1,412 ms**. **No recognized allowlisted error type, code, parameter or UUID request ID** was retained (`diagnostic` absent). |

The two rebuilt post-run canonical wires matched their pre-send request
digests and remained below 8,192 bytes. Exactly **2/2 POSTs** were reserved;
one returned a model tool call, one failed. Usage/cost for the failed POST
are **unknown**, not zero. Successful inspection is not a Credit finding:
there were **zero validated AI claims and zero abstentions**. Credit's AI
execution is `error` with `provider_http_400`; no Policy, Routing, Pricing or
other specialist model ran. The narrow diagnostic cannot issue a complete
three-specialist AI review or a deal approval.

## Read-only terminal verification and inference limit

The checkpoint has two reserved M2.1 attempts, one returned marker, one
completed authorized tool entry, and Credit as its only AI result. Both
owner-only receipts match their checkpointed request digests; the first
verifies returned and the second verifies terminal failed. The owner
directory contains only its expected approval file, owner lock and two
receipts, all owner-only. The original source identity, complete fixed
decision and six findings are unchanged; candidate remains `not_started`
and routing remains withheld. The failed assessment and **both** request
identities must **never** be replayed.

The safe classifier's empty diagnostic is **not proof** that Groq returned
no error explanation: its body may have been oversized, malformed, timed out,
contained unrecognized categories or a non-UUID identifier. The original
`http_400` is the only retained provider classification. This outcome does
not establish whether the rejection arose from the request contract,
forced-tool generation, trusted prompt or selected evidence. No follow-up
hosted trial is authorized. An account-owner manual Console lookup remains
conditional on actual request-level visibility; do not infer a request ID or
expose raw bodies.

The last pre-trial fresh seven-database offline backend regression passed
**281 tests: 274 passed, seven unrelated Gemma skips**. This hosted trial
did not change backend code or business rules; private CI status for this
result remains unverified.
