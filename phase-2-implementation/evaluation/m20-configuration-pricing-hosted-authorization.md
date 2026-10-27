# B01 Configuration/Pricing hosted validation — proposal, **not authorized**

**27 October 2026.** This is the one consolidated **new B01-only** proposal.
The earlier [B05 hosted result](m20-groq-wire-continuation-hosted-result.md)
is complete; earlier B01 identities and B05 approvals do not authorize this
campaign. Reviewer-only [identity/budget manifest](m20-configuration-pricing-hosted-proposal.json)
has canonical JSON SHA-256
`5ee0d6c308b9ff0bb64cd439fd7dc1b755ca22a886cfaad3e0977e963f0c91af`
(the SHA-256 of `_canonical(json.loads(file))`, UTF-8). Do not amend the
manifest after approval; any changed identity, evidence or budget needs a
new source-first review and approval. **No inference POST was made in preparing
this proposal.**

## Exact case, evidence and expected boundary

One fresh assessment, `M20-HOSTED-SPECIALISTS-B01-f9530345-979c-41ba-b6c6-9ec426059696`,
against pinned Phase 1C checkout `90c0bc8e285ee69262c7db826b786096a77ad004`,
run `00000000-0000-4000-8000-000000018001`, frozen bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`,
source-input digest `64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`.
The **reviewer-only** source-first fixture is ten units of one stocked product:
the authorized Configuration inspection exposes `product:M18-P-B01`
(active/sellable, catalogue/version and selected configuration fields);
Pricing exposes `pricing_line:M18-L-B01` (EUR 900 quoted, EUR 1,000 list,
EUR 700 standard cost, plus **Phase 1C-computed** discount 10% and margin
22.22222222222222222222222222%). Do not put these answers, a reviewer draft,
or this manifest in the model prompt. The model gets a bounded identity/line
input and only its own selected tool returns; Configuration investigates
first, then Pricing. Neither changes a submitted deal or proposes a price.

Pinned original fixed findings, independently preflighted on B01: Configuration
`confirmed`, Pricing `calculated`, Fulfillment `needs_revision`, Credit
`calculated`, Policy `evaluated_with_interface_limits`, Routing `withheld`.
The original review remains **needs_revision**, with routing withheld even
if both AI investigators cite valid facts. No candidate is created by this
campaign; candidate verification is **not** demonstrated by the B01 AI
investigation. Any later candidate requires its own exact-source six-check
deterministic rerun and routing before human review. The completed B05
Fulfillment campaign already demonstrated that separate path, not a B01
candidate approval.

## Exact hosted budget and gates

Use only the existing Groq Free/billing-disabled account and
`openai/gpt-oss-120b`; no alternative provider, billing change, paid API,
parallel requests, retries or automatic replay. At most **six sequential
inference POSTs** total (up to three native-tool turns each for Configuration
then Pricing); each configures **512 maximum completion tokens** for a
**3,072 configured-output-token aggregate ceiling**. Each serialized UTF-8
request body must be **at most 8,192 bytes** before send. Per returned POST,
provider-reported prompt tokens must be at most 4,096, completion tokens at
most 512, and the response at most 16,384 serialized bytes. Missing or
implausible usage stops the run. After **each** returned POST, stop before
another send if cumulative reported prompt + completion tokens, including
any supplied prior reported usage, reach **24,000**. This is a **post-send
stop**, not a guaranteed bound on actual token usage, charges or unknown
in-flight sends. Cost is unknown until measured; do not assume that a
subscription pays for API use.

Before any POST, Ali must explicitly approve this exact manifest digest,
identity and budget, reconfirm account Free/billing-disabled status, and
acknowledge private CI status if it remains unobservable. Recheck current
branch/commit and full fresh local PostgreSQL regression; verify the exact
pin, sealed source/bundle fingerprints, all six original fixed findings and
M2.0 prerequisites. Use **fresh separate isolated business and checkpoint
databases**, a fresh `0700` owner-only durable directory with exclusive
single-worker ownership, empty hosted checkpoint/attempt history for this
assessment, and no prior reservation. Verify credential ownership/mode/shape
without exposing it. Optionally check model availability via authenticated
metadata GET (not an inference request); its success cannot prove billing or
quota. Check request SHA-256 in the checkpoint before every send. The hosted
wire retains native assistant `tool_calls` IDs paired with completed
read-only ledger results, and never transmits SQL or a reviewer answer.

Stop without sending Pricing if Configuration has an error, forged citation,
wrong line/tool, permission denial, unknown send outcome or unusable result.
Stop all further sends on source/identity mismatch, malformed or oversized
messages, HTTP failure (including 400/401/403/429/5xx), timeout, unexpected
quota/charge, missing usage, altered fixed findings, unsafe approval/delivery
claim or missing human-review containment. No historical failed request,
reservation or uncertain result may be replayed. A justified `abstain`
is recorded as an **abstention**, not invented evidence or a success. Keep
private responses, receipts and credentials outside Git in owner-only
storage; publish only sanitized attempts, source IDs, cited refs, errors,
timings, reported usage and the fixed-review outcome.

## Acceptance / remaining gaps

Success requires real Groq to accept the exact native multi-turn wire, select
authorized per-specialist line inspection, return strictly structured and
exactly supported typed observations (or a justified safe abstention), and
complete an original-only human-review handoff **without** altering the
pinned fixed findings or implying an approval. Record each attempted request,
not just successful responses; manually compare claims to returned fields
and reviewer-only source expectations. Offline mocked HTTP and checkpoint
tests demonstrate protocol/containment, **not** Groq acceptance or model
accuracy. No broad accuracy comparison or independent evaluation label is
claimed. Week 3 Credit/Policy/Routing tools and inference are outside this
authorization.

**Offline gate:** full fresh isolated PostgreSQL suite, 237 tests, seven
skips, passed 27 October 2026; the mocked HTTP 400 and no-replay controls
are included. Branch GitHub Actions status is **unverified** here (`gh` is
unavailable and unauthenticated private Actions API returns 404). This
proposal is not consent to send inference.
