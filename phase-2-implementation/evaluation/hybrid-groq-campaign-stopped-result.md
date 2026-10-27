# Authorized representative Groq campaign — stopped on first B01 send

**27 October 2026; frozen digest** `8dbaac541012a21c76b71e5a77af53c43dac2aa357417098a374bc7ae79ba8bd`;
**branch** `phase2-agent-implementation` at `cd313be82e20f28a308a37391ccd17238a78591b`;
**Phase 1C pin** `90c0bc8e285ee69262c7db826b786096a77ad004`.
Ali approved one ten-case campaign on an existing Free Groq account with billing
disabled. No billing change, fallback, retry or ordinary-hybrid activation was
made. This is a **stopped** campaign, not a representative quality evaluation.

## Execution and preservation

All ten frozen source identities and seven eligible/three fixed-only statuses
passed a read-only original-graph preflight before inference. Synthetic B/N
cases used one fresh disposable PostgreSQL fixture, R03 used a separately
loaded pinned-reference fixture (mixing synthetic rows changes its source
fingerprint), and a third fresh database held checkpoints. The pinned compiled
rules matched the earlier exact compilation. The owner-only credential passed
a fresh sanitized authenticated model-metadata GET, HTTP 200. The repository
checkout and pin matched the approved SHAs. The reservation directory was
new, owner-only `0700`, on the single VM filesystem; execution used one worker.
The fresh local regression used as the approved gate passed **207 tests:
200 passed, seven historical Gemma diagnostics skipped**. GitHub CI was not
observed or claimed to pass.

The single campaign invocation stopped at B01 with a sanitized `ProviderError`
raised during its **first decision-send boundary**. The journal records
`start`, `case_reserved B01`, and `campaign_stopped B01 / ProviderError`.
The exact per-send receipt is `0600`, contains a `reserved` marker timestamped
`2026-10-27T08:26:06.698495+00:00`, and has **no `returned` marker**. The
checkpoint records `pending` decision ordinal 0, zero completed model
attempts and zero rejection entries. The provider error subtype was not saved
by the private runner; **HTTP status, transport cause, response body,
provider-token consumption, API cost and send latency are unknown**. Do not
infer zero provider usage from zero completed responses. A read-only
reconstruction of the frozen first wire matched the pending request SHA-256:
4,807 serialized bytes, `max_completion_tokens=512`, authorized inspection,
finding and abstention functions, and no premature binding-proposal function.
The wire was not resent. There were **at most one attempted inference POST**,
zero completed model responses and zero subsequent campaign calls; none of the
other nine cases was run, including the three fixed-only controls.

| Ordered case | Hosted status | Tools / AI / deterministic candidate result | Usage and latency |
|---|---|---|---|
| B01 | Started; first decision reserved; stopped on `ProviderError` | One completed counted prefetch returned three scoped refs. No model decision, proposal, citations, candidate verification or reviewer package; original six fixed mappings `needs_revision`. | 1 reserved send, 512 configured completion tokens; actual prompt/completion tokens and latency **unknown**. |
| B02 | Not started after safety stop | No case-specific hosted tool, AI or candidate check. Original source/eligibility checked in preflight only. | 0 campaign sends; not scored. |
| B03 | Not started after safety stop | Same as B02. | 0; not scored. |
| B04 | Not started after safety stop | Same as B02. | 0; not scored. |
| B05 | Not started after safety stop | Same as B02. | 0; not scored. |
| N01 | Not started after safety stop | Same as B02; no hosted abstention observation. | 0; not scored. |
| R03 | Not started after safety stop | Provisional conditional-source expectation retained outside model inputs; no hosted output. | 0; not scored. |
| N02 | Fixed-only control not executed after safety stop | Fixed-gate exclusion confirmed in preflight; no campaign assessment or model call. | 0; not scored. |
| N03 | Fixed-only control not executed after safety stop | Same as N02; stale-stock exclusion preflight only. | 0; not scored. |
| N04 | Fixed-only control not executed after safety stop | Same as N02; bounded-pool exclusion preflight only. | 0; not scored. |

**Campaign totals:** one case reserved, zero terminal case observations, one
unreconciled model send, at most one attempted POST of 21 authorized, zero
recorded model responses and zero verified hosted candidates. The reserved
request had a configured completion ceiling of 512 (campaign ceiling 14,336);
**reported prompt, completion and total tokens are unavailable**, not zero.
No hosted citation accuracy, abstention quality, end-to-end latency, or
aggregate candidate-quality rate can be computed. Offline mocked candidates
do not change these hosted denominators.

For B01 the customer requested ten by 4 September. The original pinned six
fixed responsibility mappings remain intact with `needs_revision`. One counted
authorized line-supply prefetch completed and exposed three returned refs
(inventory, confirmed inbound and shipping lane). AI submitted no usable
decision, proposed no schedule and cited nothing; no candidate was constructed,
no candidate fixed verification ran, and no reviewer package was generated.
The campaign report records **one started eligible case, zero reconciled
terminal cases, one unreconciled send and an incomplete campaign**. There is
no hosted candidate-quality, citation-accuracy or abstention denominator that
can support a quality rate; mocked offline outcomes must not be reported as
hosted successes. R03's source-first expected outcome remains provisional.

## Artifacts, boundaries and next decision

Private local artifacts, not model inputs or repository data:

- The owner-only `0600` campaign journal and send receipt under
  `/tmp/opencode/dealdesk-hybrid-campaign-live-reservations`.
- The PostgreSQL 16 test cluster in
  `/tmp/opencode/dealdesk-hybrid-campaign-hosted-pgdata`, with three separate
  `dealdesk_hybrid_campaign_live_*` databases, including the durable B01
  checkpoint and tool ledger. No raw model response exists for this send.
- Read-only sanitized aggregate projection at
  `/tmp/opencode/dealdesk-hybrid-campaign-private/stopped-campaign-report.json`.
  The private launcher in that owner-only directory printed only sanitized
  stop/report status, not the key or provider response body.
- An owner-only (`0600`) PostgreSQL custom-format backup of the checkpoint DB
  at `/tmp/opencode/dealdesk-hybrid-campaign-private/live-checkpoint.pgcustom`.
  The dedicated test PostgreSQL process was then stopped cleanly; its `0700`
  on-disk cluster and databases were not deleted.

The reserved-only send is permanently uncertain and **must not be retried**
under this campaign identity. The authorization covered this one sequential
campaign, not another attempt or a substitute case order. A future attempt
requires a new approval, fresh identities/checkpoints/receipts and an explicit
decision on sanitized error-code telemetry so an HTTP versus transport cause
can be distinguished without exposing provider error bodies. Any change to
budget, account plan, pinned Phase 1C authority or business rules requires its
own governance gate. The unchanged iterative comparator remains untouched.
