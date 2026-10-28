# Week 2 B01 secondary Groq credential — offline preparation only

**Later result:** A separately supplied second key passed exactly one
[metadata GET](week2-secondary-metadata-access-result.md), but the owner has
not confirmed Free-tier/billing-disabled status for that second account, so
no inference POST was made. The statements below describe the *earlier*
offline preparation, not the current credential availability.

**28 October 2026; no secondary key received, no provider call.** The
repository was synchronized at `4d8ccdd44aff3462d69aa5bebad5bf6a9804f433`
on `phase2-agent-implementation`. The host reported `tarekvnic`, user
`ubuntu`, kernel `6.17.0-1018-oracle` (aarch64), and working repository
`/home/ubuntu/coding-agent/projects/DealDeskOrchestrator`. Both the checkout
and ignored backend `.env` reside on the same read-write root ext4 filesystem
(`/dev/sda1`), not a temporary overlay. This is expected to persist across
OpenCode sessions on the same VM; the filesystem check cannot establish
off-VM backup or future VM lifetime.

The [historical B05 result](m20-groq-wire-continuation-hosted-result.md)
and [Configuration/Pricing B01 result](m20-configuration-pricing-hosted-result.md)
document successful Groq metadata/authentication checks and successful
requests, but **do not include a credential fingerprint or source path**.
The tracked runtime read `GROQ_API_KEY` from its process environment. Neither
result proves which physical key or account was used; the local `.env` was
created later for the failed [Week 2 401 metadata preflight](week2-closure-hosted-authentication-result.md).
Neither earlier hosted assessment was replayed or changed.

The existing primary `.env` line remains unchanged, owner-only (`0600`), and
Git-ignored. No second credential value has been supplied in this session:
`GROQ_SECONDARY_API_KEY` is not yet stored. The [opt-in launcher](../backend/dealdesk_phase2/local_env.py)
now supports explicit `--credential secondary` selection, passing *only*
that selected value to the existing child runner as `GROQ_API_KEY`. Missing
or malformed secondary values fail before launching; there is no automatic
rotation, primary fallback, provider change, or model/business-rule change.
Four focused launcher tests and the full fresh isolated PostgreSQL regression
passed **253 tests, seven skips**; no paid or hosted model call occurred.

The [approved Week 2 manifest](week2-closure-hosted-proposal.json) still has
canonical SHA-256
`5bbf5e79f7fe6d77014d4f40f4f66c446b029b6e54bbcc0e5353b82b58a14143`.
The previously initialized B01 checkpoint contains only the fixed original:
**zero model attempts, zero AI findings, no hosted owner, zero owner receipts**.
This does not qualify its already-used business/checkpoint databases as
*fresh* for another preflight. After the secondary key is provided securely,
one metadata GET must pass first; only then use new isolated databases and
an empty owner directory, reconfirm the exact source/fixed findings, and
invoke the original sequential capped experiment if its authorization and
all gates still hold. No secondary metadata request or inference POST has
occurred in this preparation step. Pricing remains without a validated
hosted finding or justified abstention; Week 2 is still partial.

The separate historical OpenACP `provider.quota` error concerns the coding
assistant backend, **not Groq**. The current coding session is functioning;
no quota reset, account allowance or permanent resolution was verified.
