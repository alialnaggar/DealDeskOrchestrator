# Approved B01 Configuration/Pricing hosted validation — stopped at Pricing

**27 October 2026.** Ali approved exactly one assessment,
`M20-HOSTED-SPECIALISTS-B01-f9530345-979c-41ba-b6c6-9ec426059696`,
at Phase 2 commit `9e70046a67d7776aff40e6604c16462134ddfd42`,
manifest canonical SHA-256
`5ee0d6c308b9ff0bb64cd439fd7dc1b755ca22a886cfaad3e0977e963f0c91af`.
Ali confirmed Groq Free with billing disabled. The approved budget was six
sequential POSTs, at most 512 configured completion tokens and 8,192
serialized bytes each, and a 24,000 reported-total-token **post-send** stop.
This authorization has been used; do not retry or resume the assessment.

## Pre-send gates and isolated source

The source pin was `90c0bc8e285ee69262c7db826b786096a77ad004`.
The first offline trial populated only the B01 fixture, which **failed** the
approved bundle/source-fingerprint comparison; no model access or inference
occurred. A second, new isolated business database was populated with the
same complete nine B/N disposable fixture cases used in the source-first
proposal; its B01 bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`
and source digest
`64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`
matched. All six original fixed findings, no candidate, empty fresh
PostgreSQL checkpoint, owner-only empty reservation directory, credential
ownership/mode/shape, exact manifest/commit/budget, fresh local regression
(**237 tests, seven skips**), and authenticated model metadata GET passed.
The GET established access, not billing or inference success. Private CI
remains **unverified**, not passed.

## Real hosted attempts (Groq `openai/gpt-oss-120b`)

| Sequential POST | Specialist and transport | Request bytes | Reported prompt + completion | Recorded model latency |
| --- | --- | ---: | ---: | ---: |
| 1 | Configuration: HTTP response, native `inspect_configuration_line` | 2,596 | 581 + 56 = 637 | 702 ms |
| 2 | Configuration: HTTP response, paired assistant/tool follow-up, `submit_finding` | 3,339 | 712 + 309 = 1,021 | 1,267 ms |
| 3 | Pricing: HTTP response, native `inspect_pricing_line` | 2,573 | 584 + 58 = 642 | 707 ms |
| 4 | Pricing: **HTTP 400** on paired assistant/tool follow-up; terminal stop | 3,377 | **Unknown: no response usage** | **Not recorded** |

Exactly **four** sequential sends were attempted, all under the size limit;
each configured 512 completion tokens (**2,048** configured in total).
Only three returned measurable usage: **1,877 prompt + 423 completion =
2,300 reported tokens**. Known returned model-call latency was **2,676 ms**
combined; it is not total assessment wall time or a latency measurement for
the fourth attempted call. The fourth request was reserved before sending
and has no returned response/usage. It was **not retried**. No provider cost
was reported; Free/billing-disabled status is Ali's confirmation, not a
measured invoice. The sanitized transport code is `provider_http_400`;
the rejected provider body was not read or published, so the precise rejection
reason is **unknown**.

## Evidence, authority and outcome by specialist

- **Configuration:** One model-selected, authorized, completed read of
  `product:M18-P-B01`; the model's five validated exact field observations
  were `catalog_version=CATALOGUE_2026_V1`,
  `fulfillment_mode=stocked_finished`, `is_active=true`,
  `is_sellable=true`, and `product_id=M18-P-B01`. These are cited observations,
  **not** an AI decision that the deal is valid. The pinned fixed Configuration
  finding remains `confirmed`. Two returned model turns; known reported
  usage **1,293 prompt + 365 completion = 1,658 tokens**, 1,969 ms of
  recorded model-call latency.
- **Pricing:** One model-selected, authorized, completed read of
  `pricing_line:M18-L-B01` returned selected quoted/list/cost fields and
  **Phase 1C-computed** discount/margin. The model made **no validated
  Pricing finding or abstention**: the second Pricing request was rejected
  with HTTP 400 and the investigation stopped. The pinned fixed Pricing
  finding remains `calculated`; no AI recalculation, clearance or repricing
  occurred. One returned turn (642 reported tokens, 707 ms); a second
  attempted turn has unknown usage and latency.

The other original fixed results also remain unchanged: Fulfillment
`needs_revision`, Credit `calculated`, Policy
`evaluated_with_interface_limits`, and Approval Routing `withheld`.
The original review remains `needs_revision`; `candidate_status=not_started`,
no candidate was created, and the reviewer package contains a **stopped AI
investigation** with human review required. Nothing was approved, waived,
reserved, booked, repriced or promised. No candidate deterministic rerun
occurred (none was submitted). Configuration's successful wire does **not**
prove Pricing's tool-result wire is accepted by Groq; neither one-case result
demonstrates model accuracy.

## Containment and next gate

Private raw returns, owner-only attempt markers, the stopped summary and
runner remain outside Git in
`/tmp/opencode/dealdesk-m20-specialists-b01-private/` (`0700` directory,
`0600` files). The separate PostgreSQL checkpoint remains in the isolated
`dealdesk_m20_specialists_b01_frozen_checkpoint` database; the durable
single-worker owner is `/tmp/opencode/dealdesk-m20-specialists-b01-owner/`.
Do not replay any of the four sends or reuse this assessment identity.
Investigating the Pricing HTTP 400 must be **offline-first** with the sealed
request shape/authorized tool facts; any proposed new hosted test requires a
new source-first identity, bounded budget and explicit approval. Week 3
Credit, Policy and Routing remain planning-only with no tools or hosted
authorization under this campaign.
