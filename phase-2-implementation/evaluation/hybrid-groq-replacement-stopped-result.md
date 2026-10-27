# Replacement hosted Groq campaign — stopped on B01 HTTP 400

**27 October 2026.** Approved replacement digest
`0c3b9af2e7ca5d2f673397df0604acb1b1c5e5757845755d29f6935298e52082`;
branch `phase2-agent-implementation` at
`5dd4d604481259bab43af764ab819ac24d3f5dd0`;
Phase 1C pin `90c0bc8e285ee69262c7db826b786096a77ad004`.
Ali confirmed the existing Groq Free tier and billing-off status and approved
one sequential ten-case replacement. The account plan, pin, rules and ordinary
hybrid activation were not changed. **This campaign stopped on its first
eligible case; it is not a hosted quality comparison.**

## Gate and incident

The branch and remote matched, the manifest/digest and all ten fresh assessment
IDs matched their frozen values, and all ten exact source hashes matched the
previous reviewed source manifest. A new PostgreSQL 16 cluster held separately
loaded synthetic, reference-only R03 and empty checkpoint databases; the
source preflight produced seven eligible and three fixed-only classifications
with all six original responsibility mappings present. Pinned compiled rules
matched their previous SQL byte-for-byte. The owner-only, previously empty
reservation directory was `0700` on the local durable filesystem. The private
credential passed the owner/permission/format checks. A sanitized authenticated
**model-metadata GET** confirmed access before the first POST; it did not prove
that the POST schema would be accepted. A new isolated PostgreSQL regression
passed **217 tests: 210 passed and seven unrelated Gemma diagnostics skipped**.
GitHub CI was **not verified**.

One replacement B01 decision POST reached the hosted HTTP error boundary:
**HTTP 400**, recorded as sanitized `http_400` in both the fsynced `0600`
per-send receipt (`reserved` followed by `failed`) and the one-shot campaign
journal (`start`, `case_reserved B01`, `campaign_stopped B01`). The failed
marker recorded **1,498 ms** for the attempted send; this is not full case
latency. There is no returned marker, completed model response, saved provider
error body, reported token usage or provider billing observation. The request
was **4,807 bytes** (under 8,192) with a 512 configured completion cap; its
reconstructed SHA-256 matches the saved pending request. Because the source,
prompt and observations are the same, the request-byte digest equals the
historical B01 wire digest, but this was a **new, approved assessment ID,
start identity, checkpoint and receipt**, not a replay of the historical
attempt. Neither B01 attempt may be resent. HTTP 400 establishes an HTTP
rejection but **not the rejected field or the historical B01 failure cause**:
the error body was deliberately not recorded, and the 512 cap, tool schema
or account conditions are hypotheses, not established root causes.

This is an **HTTP rejection**, not one of the approved attested local
transport/response failure codes. The replacement therefore stopped
campaign-wide; the one-time continuation allowance was **not used**. The
checkpoint retains pending decision ordinal zero, zero completed model
responses, the original six fixed findings (`needs_revision`), and one counted
line-supply prefetch with three returned references. There is no AI decision,
candidate, fixed-checked alternative, citation, abstention or reviewer package.

| Case(s) | Hosted outcome | Observed inference and quality |
| --- | --- | --- |
| B01 | Fresh assessment started; HTTP 400 on first decision; permanently non-replayable. | One attempted POST, no completed response or reported tokens; no AI proposal or candidate quality to score. Original fixed result `needs_revision`; prefetch returned three references. |
| B02–B05, N01, R03 | Not started after global stop. | Zero sends and no hosted citations, abstentions or candidates. R03 expectation remains provisional and separate from model inputs. |
| N02–N04 | Fixed-only classifications confirmed in preflight; campaign controls not run. | Zero model sends; not scored as hosted controls. |

**Budget versus observation:** the stopped-case projection conservatively
reserves **3 of 21 request slots** and **2,048 of 14,336 configured
completion tokens** for B01, though exactly **one POST was attempted** with
only a 512-token configured cap and **zero responses completed**. Actual
prompt/completion/total tokens and cost for that send are **unknown**, not
zero. The generic read-only projection's `minimum_attempted_requests=0`
counts only terminal case observations and cannot inspect this outstanding
case; the fsynced receipt independently establishes **one** attempted send.
No aggregate hosted candidate-quality, citation-support or abstention rate is
defined for this stopped campaign. Offline mocked candidates are not hosted
observations. The 60,000 *reported*-total-token threshold was not measurable
for this failed case; it is not a hard input-token limit.

## Preserved private artifacts and next gate

- Owner-only `0600` campaign journal and B01 send receipt under
  `/tmp/opencode/dealdesk-hybrid-replacement-live-reservations`. The empty
  owner mutex file is separate and unchanged.
- Owner-only `0600` read-only sanitized projection and three PostgreSQL
  custom-format backups (synthetic, reference, checkpoint) under
  `/tmp/opencode/dealdesk-hybrid-replacement-live-private`.
- Dedicated `0700` PostgreSQL cluster at
  `/tmp/opencode/dealdesk-hybrid-replacement-live-pgdata`, stopped cleanly,
  **not deleted**. Its preserved checkpoint contains the fixed original,
  evidence pack and tool ledger; no raw model output exists from this send.

No second POST, later-case assessment, fallback, billing change or new model
provider was attempted. The exact approved replacement campaign is spent and
stopped: **do not restart it or route around the HTTP 400 under this
authorization**. Offline diagnosis of the request against current Groq
requirements can inform a newly scoped proposal; any corrected wire, larger
completion budget, new identities or further hosted request requires separate
review and authorization. Do not claim this campaign completed or that its
HTTP 400 explains the first campaign's unsaved `ProviderError` subtype.
