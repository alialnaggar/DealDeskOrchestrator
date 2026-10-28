# Week 2 B01 second-account Configuration → Pricing — terminal Pricing HTTP 400

**28 October 2026.** Ali confirmed that the *second* Groq account is Free-tier
with paid billing disabled and authorized the previously approved B01-only
assessment `M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7`.
Its [unchanged canonical manifest](week2-closure-hosted-proposal.json) has
SHA-256 `5bbf5e79f7fe6d77014d4f40f4f66c446b029b6e54bbcc0e5353b82b58a14143`.
The previously [successful secondary-key metadata check](week2-secondary-metadata-access-result.md)
was **not repeated**. The explicit child launcher used only the secondary key
as `GROQ_API_KEY`; the primary `.env` value remained unchanged. Both values
are local, Git-ignored, owner-only and excluded from this report.

## Pre-send gates and business scenario

At `b456e5386e5e5b7de85c0e277534771423e859c4`, branch and remote
matched; tracked M2.0 transport/continuation code had not changed from the
reviewed implementation. Phase 1C remained pinned at
`90c0bc8e285ee69262c7db826b786096a77ad004`. The earlier B01 checkpoints
and owner directories had **zero inference attempts or receipts**; none was
reused for inference. A first freshly isolated preflight checkpointed the
six fixed results but stopped **before any POST** on an offline harness error:
the harness looked for `run_id` rather than the typed
`RunContextV1.phase1c_run_id`. Read-only inspection verified the actual
run UUID matched. That fixed-only context remains untouched. A further new
isolated business/checkpoint pair and empty `0700` owner/private directories
were created; no prior hosted original or request was replayed.

The complete nine-case synthetic fixture and pinned compiled rules produced
B01's approved sealed bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`
and source-input digest
`64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`.
The synthetic submitted deal is ten units of stocked finished product
`M18-P-B01`; the immutable original is `M18-D-B01`. The fixed original
matched all six baselines: Configuration `confirmed`, Pricing `calculated`,
Fulfillment `needs_revision`, Credit `calculated`, Policy
`evaluated_with_interface_limits`, Approval Routing `withheld`. Original
review `needs_revision`, candidate `not_started`, and withheld routing were
reconfirmed immediately before POST and remained unchanged afterwards.

## Bounded hosted observation

The approved `m20-config-pricing-system-v2` and `openai/gpt-oss-120b` ran
sequentially, Configuration before Pricing. Each request was checked against
the 8,192-byte limit, a 512-token completion ceiling and the aggregate
six-POST/3,072-configured-completion-token limit; the 24,000 reported-total-
token **post-send stop** was not reached. There were **no retries**.

| Sequential POST | Role / outcome | Canonical request bytes | Request SHA-256 |
| --- | --- | ---: | --- |
| 1 | Configuration inspection returned | 3,006 | `c1d1f41e372b04b7ee2a99b89f12f8aa2a16f829cdf101d0bb83c1c7dc0b6646` |
| 2 | Configuration finding returned | 3,749 | `e2e3bba24406a7dc8ea1a2bc25264f42fe149d9b0d28c09b1e43baea767037ab` |
| 3 | Pricing inspection returned | 2,964 | `ccf8ff864e73fd3fd07e488a232e59a20897975a404da51264efbe97454665bf` |
| 4 | Pricing follow-up **HTTP 400; stopped** | 3,768 | `f93c5bbc0c4e46cbbc648c01ef28a8b0d2203622d537231e25cd90cc25eb12f1` |

Configuration completed one authorized read and returned **four exact
validated product claims**: `is_active=true`, `is_sellable=true`,
`fulfillment_mode=stocked_finished` and
`catalog_version=CATALOGUE_2026_V1`, all cited to `product:M18-P-B01`.
Those observations are **not** a model approval or a full configuration
validity determination; the fixed Configuration result remains authoritative.
Pricing completed one permitted inspection, then the fourth POST returned
`provider_http_400`. The provider error body was not logged or published.
The cause is **unclassified**; model access and successful earlier POSTs do
not prove what Groq rejected. Pricing produced **neither a validated hosted
finding nor a justified abstention**. The reviewer AI projection is `stopped`
with no Pricing claims; fixed Pricing/margin remains `calculated` and fixed
routing stays withheld. No candidate was created and no deal was approved.

Four attempts are durably marked `reserved`; three have `returned` markers.
The last Pricing reservation is **terminal/uncertain**, not an invitation to
resume or replay this identity. The isolated checkpoint and owner-only audit
directory remain private; the old B05 and B01 hosted records were not touched.

| Sanitized measure | Observed |
| --- | ---: |
| Inference POSTs | **4 / 6 maximum** |
| Configured completion tokens | **2,048 / 3,072 maximum** |
| Reported tokens on three returned responses | **2,119 prompt + 533 completion = 2,652 total** |
| Returned-response latency | **2,461 ms sum, three responses only** |
| Fourth response usage / latency; cost | Not reported / not measured; cost unavailable |
| Fixed original, candidate, human approval | Unchanged; none; none |

A fresh post-run isolated PostgreSQL regression passed **253 tests, seven
skips**. This demonstrates offline containment and contracts, not a live
Pricing success or independent accuracy. GitHub Actions for this increment
was not verified. **Week 2 remains partial**; do not re-send the stopped
assessment or attempt a new provider-contract experiment without a separately
reviewed scope, new source-first identity and authorization. Week 3
Credit/Policy/Routing inference remains outside this run.
