# Pricing/Credit typed-final hosted infrastructure — dormant

**28 October 2026. Infrastructure implementation only.** This extends the
[approved design](pricing-credit-typed-final-implementation-design.md) and
[offline implementation](pricing-credit-typed-final-offline-implementation.md).
The `HOSTED_ACTIVATION = False` gate in `typed_final_hosted.py` prevents all
production sends regardless of a caller's boolean, manifest or credential.
No owner approval was created outside disposable test fixtures. No Groq API,
metadata endpoint, live inference or paid model was contacted.

## Boundary and compatibility

The new `pricing-credit-typed-hosted-manifest-v1` gate checks one fresh pinned
case, exact manifest SHA-256, owner-only `0700` directory and preexisting
`0600` exact approval file, explicit account and free-tier/billing-disabled
confirmation, a single selected specialist, immutable run/source/snapshot,
permission/wire/prompt/schema versions, actual business/checkpoint database
names, and an exclusive OS owner lock. Existing M2.0/M2.1 manifests and
approval files are structurally incompatible. Credit is a standalone targeted
inspection; fixed Pricing is still a prerequisite. Pricing runs **unchanged
Configuration native wire and its original validators** first under the new
manifest's separate `typed_configuration` receipt stage, then the distinct
Pricing inspection stage and no-tools typed final. Configuration is not
migrated to typed final. Fulfillment, Policy and Routing keep their defaults.

Inspection reuses the old domain serializers and evidence projection but adds
a distinct `pricing-credit-hosted-inspection-v1` wire and versioned instruction
to the new request; **the existing Configuration wire is unchanged**.
Inspection permits only the scoped read-only tool or abstention; a native
terminal finding is unavailable on this new wire. Pricing's preflight plan
allows one or two reads; Credit permits one. The final is a **new** system/user
request with `response_format.type=json_schema`, `strict=true`, all fields
required and `additionalProperties=false` on each object. Its name and schema
SHA are pinned in the manifest. It has **no tools, `tool_choice`, tool-role
messages, streaming or raw reasoning format**. This matches the compatibility
conditions quoted in the repo's approved design from Groq's Structured Outputs
and tool-use documentation; it is not a provider acceptance result. A schema
change, mixed tools+strict schema, invalid response, HTTP 400 or timeout fails
closed without best-effort JSON or a native-tool fallback.

Per POST: maximum 8,192 serialized request bytes; reported prompt 4,096
tokens, response 16,384 bytes, inspection completion 512 or final completion
1,024 tokens, and final content 8,192 bytes. Pricing plan 1 requires up to
**2 Configuration + 1 Pricing inspection + 1 final = 4 POSTs/2,560
configured completion tokens**; plan 2 uses **5 POSTs/3,072**. Credit targeted
uses **2 POSTs/1,536**. The separately calculated full M2.1 bound for Credit
plus unchanged Policy/Routing is **6 POSTs/3,584 configured tokens**; that
broader campaign is **not executable** by this targeted gate. All reported
total tokens stop at 24,000 *after a successful response*; failed sends have
unknown usage and no pre-send cost guarantee. The manifest must use exactly
the calculated target budget, with Configuration's actual returned receipts
counted before Pricing can send. No paid fallback or automatic retry exists.

An append-only PostgreSQL reservation and `0600` receipt (scoped by stage,
ordinal, request digest and protocol/manifest identity) precede every send.
Returned Configuration receipts are checked against the original native
request, source ledger and existing claim validator. Pricing/Credit receipts
and source ledger are rechecked after restart; a failed, reserved-only,
returned-but-unparsed, damaged or identity-swapped send never permits replay.
Only bounded sanitized codes/usage and validated citations enter state or
review. The offline graph remains callable with an exact scripted double;
an assessment selected for hosted cannot revert to that double.

## Test-only exception and limits

`MockTypedTransport` explicitly bypasses **only** the hard activation switch
for ephemeral synthetic PostgreSQL tests and has no HTTP client or credential
access. It still requires the exact new manifest and temporary permissioned
approval fixture; `_post` is patched to fail if called. This is not a live
approval record. The production branch reads a credential and could call
the provider only after a separately approved code change enabling the
hard-disabled gate and supplying an externally authored matching approval.
The original default paths, existing hosted authorizations and historical
terminal identities remain unchanged.

The targeted gate does not run Policy/Routing or establish accuracy versus
the legacy path. It does not prove Groq will accept this exact schema, model
or request. No current Groq capability or free-tier metadata was queried.
Before activation, perform an independent security and architecture review,
check private CI, verify current provider documentation and owner account
terms/quotas without inferring them from tests, and obtain Ali's separate
approval to enable this new gate for fresh cases. Activation is a distinct
reviewed commit changing `HOSTED_ACTIVATION`; it is **not** accomplished by
changing a manifest or environment variable.

## Proposed first hosted acceptance — NOT AUTHORIZED

Propose one **new synthetic B05 Pricing** assessment with preflight
`inspection_plan=1`, exact pinned Phase 1C commit, `openai/gpt-oss-120b`,
unchanged Configuration native inspection, Pricing inspection and one strict
final. Proposed maximum **4 POSTs**, **8,192 request bytes per POST**,
**4,096 reported prompt tokens per successful POST**, **512/512/512/1,024
configured completion tokens**, **2,560 configured completion tokens total**,
**24,000 reported-token post-send stop**, 16,384 response bytes per POST and
zero retry/fallback. Use `GROQ_SECONDARY_API_KEY` only for a single owner-
identified account whose actual ID and **free-tier/billing-disabled** status
Ali separately confirms. The test-only account ID must not be used. Create
fresh isolated business/checkpoint databases and fresh assessment/owner
directory, never a historical stopped assessment.

After that fresh case is pinned, generate the **exact canonical manifest**
with its new assessment/run, bundle SHA, source digest, as-of and snapshot,
owner directory, database identities, model, account ID, schema and exact
ceilings. Present its immutable
`SHA256(_canonical(manifest).encode())` to Ali for explicit one-case approval.
The actual hash and account ID **cannot be supplied or preapproved now**:
neither a new assessment nor a selected account/manifest exists. Only Ali's
separate activation decision followed by a separate authorization for this
exact case, account/billing state, manifest SHA, retention and budget can
permit an externally created owner-only approval artifact and a first send.
No metadata GET, broad matrix, trial retry or provider fallback is included.
