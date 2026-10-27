# Proposed single hosted-validation milestone — **not authorization**

**27 October 2026.** Baseline `69a4c5852308382c77ed98315d2e8dfd66d25405`.
The earlier B06 one-decision Groq approval is spent. This proposal prepares
exactly **one Fulfillment assessment and one sequential Configuration/Pricing
assessment** on the existing Groq Free account, not an accuracy study or a
production launch. No inference, token-count or authenticated metadata call
was made in preparing this proposal. Obtain Ali's explicit approval of the
exact identities/budget **and** confirmation that the current account is
Free/billing-disabled before any inference POST.

## Source-first cases, held outside all model requests

The [identity manifest](m20-hosted-validation-identities.json) contains the
new assessment IDs, Phase 1C run UUIDs, frozen bundle and selected-source
digests.
The canonical JSON SHA-256 of that reviewer-only manifest is
`b014decf8c0bb9daaa55e8bc40682145567f1b98430cce4c46657c45ccefdb9f`.
Prepare fresh, separate disposable synthetic-business and
PostgreSQL-checkpoint databases with the pinned Phase 1C schema, 14 reference
rows, compiled rules and M1.8 B/N cases. The manifest is **reviewer-only**;
the model sees only the bounded input and authorized tool returns. Independently
re-seal each source and compare all four identities before either send. Any
mismatch requires new source-first review and new approval, not hash editing.
The separate pinned Phase 1C checkout remains exactly
`90c0bc8e285ee69262c7db826b786096a77ad004`.

1. **B05 Fulfillment, first:** 18 stocked units requested by 4 September;
   the selected inventory can support an early slice of 11, and confirmed
   inbound supports the later seven. This is a *reviewer expectation*, not
   prompt content or a supplied proposal. Use the existing gated
   `GroqHybridTransportModel` and `run_hybrid_evaluation`, not the offline
   double or historical B05 result. A fresh `0700` durable receipt directory
   and empty checkpoint are required. Model-selected bounded tools must return
   exact dated options; the model may submit a structured binding proposal,
   scoped finding or justified abstention. The pinned verifier alone decides
   candidate supply and six rerun findings. A supported option remains
   **unreserved**, needs customer acceptance and human review; an overcount,
   wrong source/date or conditional offer cannot become confirmed supply.
   Hosted same-specialist correction remains **disabled**, despite the
   separately passing offline corrected B05 integration.
2. **B01 Configuration then Pricing, second:** ten units, one stocked product.
   Actual sealed Configuration inspection returns `product:M18-P-B01` with
   `is_active=true`, `is_sellable=true`, catalogue
   `CATALOGUE_2026_V1` and empty configured attributes. Actual Pricing
   inspection returns `pricing_line:M18-L-B01`, EUR 900.00 quoted,
   EUR 1000.00 list, EUR 700.00 cost, and **Phase 1C-computed** discount
   `10` and margin `22.22222222222222222222222222` percent. These
   observations do **not** authorize AI to recalculate, clear a margin, alter
   the price or approve. Fixed Configuration is `confirmed`, fixed Pricing
   is `calculated`, original review is `needs_revision`, and Routing is
   withheld. Hosted AI may investigate via its *own* one-line tool, return
   exact typed cited observations or abstain. An original-only human-review
   package is created if Fulfillment has not produced one.

Both cases were resealed read-only against the local fresh source fixture;
the expected bundles/digests matched the manifest. B05/B01 share a product
class and pricing pattern, so they are **not diverse test cases**. Separate
offline controls include N01 (partial delivery forbidden), the pinned
offer-only conditional case, invalid sellability, forged pricing/product
references, wrong tool/line, missing usage and interrupted checkpoints.
None of those controls consumes a hosted request under this proposal.

## Provider compatibility, exact ceilings and stop conditions

Provider/model: existing Groq `openai/gpt-oss-120b`; no fallback, new
provider, key export, billing change, retry or parallel send. The B06 live
decision confirmed **one native tool choice** on Groq; neither the B05
structured final nor the new Configuration/Pricing tool schema has yet been
accepted by Groq. The new `m20_groq.py` adapter uses one native tool call
per turn with `tool_choice=required`, `parallel_tool_calls=false`, two
domain-specific read-only inspect names and a common `submit_finding`/
`abstain` action. A `value_json` string is parsed into a typed JSON value,
then the original exact-type/value validator checks it against returned
checkpointed records; there is **no implicit numeric normalization**.
Offline mock HTTP tests prove serialization/checkpoint attribution, not provider acceptance.
The new M2.0 hosted path is **evaluation-ready at the offline-contract level**:
it rejects missing authorization/credentials, requires exact scoped Groq
adapters, checkpoints request SHA-256 before transmission, enforces a
single-host owner lock with directory identity and never resends an uncertain
turn. A forged Configuration claim yields an original-only reviewer handoff
and stops before Pricing. No production hosted assessment has used this path.
Groq's [local tool-calling documentation](https://console.groq.com/docs/tool-use/overview)
lists `openai/gpt-oss-120b` as tool-capable but not parallel-tool-capable;
its [structured-output guide](https://console.groq.com/docs/structured-outputs)
lists strict JSON for the model and explicitly says tool use cannot be
combined with structured outputs in one request. The existing Fulfillment
wire correctly separates native decision calls from its strict structured
final; M2.0 uses native tool calls throughout. These are documented API
capabilities, **not** live acceptance evidence for the exact new payloads.

| Assessment | Maximum sends | Per-send configured completion ceiling | Maximum configured output ceiling |
| --- | ---: | --- | ---: |
| B05 Fulfillment | 3 | 512 for each of two decisions; 1024 for one strict-schema final | 2048 |
| B01 Configuration, then Pricing | 6 (3 turns each) | 512 for each native-tool decision | 3072 |
| **Aggregate** | **9** | 8192 UTF-8 request-body bytes each | **5120** |

At most two read-only inspections per M2.0 specialist, six exact claims per
finding, 25 records per inspection, shared 12-counted-call ceiling; hybrid
prefetch is a counted call. M2.0 checks actual provider-reported prompt tokens
at **4096 per returned request** and completion tokens at 512; unknown/missing
usage is terminal. The Fulfillment hosted adapter verifies reported completion
counts but does not impose a pre-send prompt-token ceiling. **Measured**
aggregate prompt+completion usage must be reviewed after B05 and each B01
turn, stopping at 24,000 reported tokens; this is a *post-send stop*, not
a hard bound on input tokens, charges or unknown sends. Serialized request
body and configured output ceilings are pre-send gates. Provider cost is
unknown until account status and actual usage are verified; expected Free-tier
API charge is **$0 only if Ali re-confirms billing remains disabled**. Any
unexpected charge or quota change stops the milestone.

**Stop globally** on missing free-tier confirmation, CI/local gate failure,
source/pin/manifest mismatch, nonfresh checkpoint or used receipt, unexpected
model/tool response, HTTP 400/401/403/429/5xx, network timeout or unknown
send outcome, missing/oversized usage, permission denial, forged/unreturned
citation, incorrect binding quantity/date, conditional offer promoted to
confirmed, rewritten original fixed result, missing human-review package or
any approval/delivery/reservation promise. Do **not** retry a failed or
uncertain turn, reuse an assessment ID, or let a Configuration failure trigger
Pricing. A safe model abstention is a recorded outcome, not a success claim.
Manual source-first human semantic review follows the complete run; never
expose answer sheets or reviewer drafts to the model.

## Before/after evidence and Week 3 gate

Before any POST: verify pin and manifest digest, fresh business/checkpoint
DBs, source fingerprints, six original fixed findings, B05 eligibility and
B01 Configuration/Pricing prerequisites; use one owner-only `0700` durable
directory for the M2.0 single-worker mutex and a separate owner-only
directory for Fulfillment. M2.0 checkpoints a model-attempt reservation
**before** every send and will not replay an uncertain turn; unlike
Fulfillment it does **not** maintain a per-send fsynced disk receipt.
Thus a returned-but-not-checkpointed response is classified uncertain,
never treated as a successful observation. Run full fresh offline PostgreSQL
regression and inspect the branch's GitHub Actions. A sanitized authenticated
Groq model-metadata GET may be used **after** owner consent; it establishes
model access, **not** current quota or billing. Require explicit acceptance
if private CI status remains unavailable. Record raw responses only in
owner-only checkpoint/receipt storage, never in the repository. After each
send record request SHA-256, model/prompt version, counted tool receipts,
returned refs, sanitized errors, timing, actual usage/cost if known, source
and fixed-result digests, candidate verification and reviewer containment.
Report **attempted** requests and all failures, including abstention and
stopped paths; do not claim a live assessment succeeded merely because an HTTP
request returned. A fresh approval must name both case IDs and manifest digest
with the **9-request/5120-output-token** maximum. Until then leave hosted
entrypoints uninvoked.

**Preparation gate:** the final local regression used seven newly created
disposable business/checkpoint databases and completed **230 tests: 223
passed, seven unrelated saved-Gemma diagnostic skips**; log:
`/tmp/opencode/dealdesk-m20-hosted-preparation-release.log`. The new
mocked-Groq test exercised both specialists through their actual pinned
PostgreSQL evidence projections, normal handoff, rejection and restart, with
zero HTTP calls. The last accessible GitHub Actions status is **unknown** in
this environment (`gh` unavailable; private unauthenticated API 404). The
CI workflow provisions the M2.0 fixture DBs and runs test discovery on push,
but a green CI run is **not** asserted here. Review its result (or explicitly
accept CI-unobserved risk) before authorizing hosted use.
