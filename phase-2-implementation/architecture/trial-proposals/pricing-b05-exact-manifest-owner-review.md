# First B05 Pricing typed-final — exact owner review, NOT authorization

**29 October 2026 · branch `phase2-agent-implementation`.** Ali supplied
`org_01m5d82zneee6b2vzsz8d2014b` as the exact Groq Organization ID; this
message provided **identity only**, not activation or permission to send.
The owner previously confirmed the intended free-tier setup and accepted the
unverified private-CI gap for **one** bounded synthetic experiment only; CI
has **not** passed. No Groq/metadata request, hosted inference, approval file
or activation was made. Unrelated Gemma work and Phase 1C source are untouched.

## Immutable owner-review manifest hash

**Exact would-be runtime manifest SHA-256** (UTF-8 bytes from the established
`sha256(_canonical(manifest).encode()).hexdigest()`):

```text
530cfc1d87cde830b3376284e9f0a05dd6a0e167b9e5c7bc27def85c2a42b0e3
```

Reproduce the **review calculation offline** from the committed,
non-executable [fully identified proposal](pricing-b05-scram-final-review-proposal.json):

```python
import json
from hashlib import sha256
from pathlib import Path
from dealdesk_phase2.hybrid_pack import _canonical

proposal = json.loads(Path(
    'phase-2-implementation/architecture/trial-proposals/'
    'pricing-b05-scram-final-review-proposal.json').read_text())
assert proposal['status'] == 'proposal_not_authorized_not_executable'
would_be_runtime_manifest = {**proposal, 'status': 'authorized_one_case'}
print(sha256(_canonical(would_be_runtime_manifest).encode()).hexdigest())
```

The file **committed to Git is not an authorized manifest**; its own canonical
hash is `16feccc8c0e499d8015399f1404bf101bd04ce08a2f0d133ed0710d877012b1a`
and cannot be used as a runtime approval digest. The would-be runtime JSON
exists only as a mode-`0600` owner-review copy **outside** the empty runtime
owner directory at
`/tmp/opencode/dealdesk-b05-scram-9c9794347b09/would-be-authorized-b05-review-only.json`.
Its `status=authorized_one_case` is the exact *future* byte value needed to
calculate the owner's review hash, **not** an authorization or approval record.
The runtime's private `typed-final-approved-manifest.json` does not exist.

## Exact identities and checks (no reprovisioning)

| Binding | Reviewed value |
| --- | --- |
| Specialist, plan | Pricing; one inspection |
| Provider/model/key selection | `groq`; `openai/gpt-oss-120b`; `GROQ_SECONDARY_API_KEY` |
| Owner-supplied account ID | `org_01m5d82zneee6b2vzsz8d2014b` |
| Phase 1C checkout | `90c0bc8e285ee69262c7db826b786096a77ad004` |
| Subject / assessment | `M18-D-B05` / `TYPED-B05-SCRAM-8ba93fddd647` |
| Phase 1C run / snapshot | `00000000-0000-4000-8000-000000018005` / `M18-SNAPSHOT-B05` |
| As-of cutoff | `2026-09-01T12:00:00+00:00` |
| Sealed bundle SHA-256 | `a80b5b99f5d09ca2568010f8c26867413f4049097173e72ff229661e7a830df9` |
| Source input digest | `7859cec62db30f44f2777a90158cef6bd8d75fe57e7373595642959313e93b39` |
| Restricted business DB / OID | `b05_business_2230473070` / `16385` |
| Exclusive checkpoint DB / OID | `b05_checkpoint_c43d6b2467` / `16386` |
| Empty private owner directory | `/tmp/opencode/dealdesk-b05-scram-9c9794347b09/owner` |
| Original fixed result | `needs_revision` (not approval) |

The [restricted preflight](pricing-b05-restricted-preflight-2026-10-29.md)
records independent CREATE DATABASE evidence and non-superuser SCRAM role
privileges. This follow-up used its existing original assessment: the pinned
Phase 1C adapter reread matched the checkpoint; `typed_final_hosted`'s **exact
runtime `_validate_manifest`**, database-name/OID/exclusive-thread and
all-history validators passed against the *in-memory* would-be manifest.
All 11 history states belong to this assessment, contain no prior hosted
Pricing/Credit/typed-final attempts, and the owner directory remains empty.
The approval-file check correctly rejected the missing file. No send path
was invoked. Exact permission version is `m1.2-v1`; Configuration, inspection
and final prompt hashes plus schema SHA-256 match the runtime (checked by the
offline proposal test). These facts identify a candidate for **owner review**;
they do not confer approval, guarantee provider acceptance or freeze future
business/OS changes. Recheck state, access and receipts immediately before
any separately authorized send; a changed identity requires a **new** hash
and owner decision.

## Bound and proposed activation — neither applied nor authorized

The runtime's exact `budgets('pricing', 1)` is **four POSTs and 2,560
configured completion tokens**, inclusive of two Configuration native turns
(512 + 512), one Pricing inspection (512), and one separate strict-schema
no-tools final (1,024). Maximum 8,192 serialized request bytes, 16,384
response bytes and 4,096 *reported* prompt tokens per returned POST;
24,000 reported total tokens is a **post-return** stop, not a pre-send cost
guarantee. No retries, replay, fallback, extra case, Credit trial, metadata
request or paid OpenAI API.

**Only proposed, one-line activation diff** in
`phase-2-implementation/backend/dealdesk_phase2/typed_final_hosted.py`:

```diff
-HOSTED_ACTIVATION = False  # Changing this requires Ali's separate activation approval.
+HOSTED_ACTIVATION = True  # Changing this requires Ali's separate activation approval.
```

The flag remains `False`. **Next explicit owner action:** review and approve
this exact activation diff **and separately** authorize the precise one-case
B05 Pricing manifest hash shown above, selected account, DB/assessment and
four-POST budget. Until those decisions, do not deploy the diff, create the
private approval record, or call the hosted entry. Following authorization,
any HTTP 400/429, uncertainty, invalid usage/citation, mutated evidence or
interruption ends this assessment: no retry or fallback. Rollback stops
scheduling, coordinates in-flight activity, deploys a separately reviewed
restoration to `False`, and preserves every spent receipt/checkpoint for audit.
