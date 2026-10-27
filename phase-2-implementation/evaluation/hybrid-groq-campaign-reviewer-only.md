# Adaptive-hybrid Groq campaign — reviewer-only authorization manifest

**Status:** prepared offline, not authorized for inference. This document and
`hybrid-groq-campaign-identities.json` are NEVER model input. Source-first
expectations below are developer/supervisor-reviewed for synthetic cases,
provisional for reference R03, and **not** externally accepted ground truth.
Approval of the exact campaign includes acceptance of R03 as a *provisional*
semantic review control; independent evaluation acceptance remains separate.

| Order | Case | Reviewer-only evidence and outcome | Hosted requests |
|---|---|---|---:|
| 1 | B01 | 10 due Sep 4, eight stock Sep 4 and two confirmed inbound Sep 8; fixed-supported split, `needs_revision` and customer acceptance pending. Historical hybrid failure remains a separate assessment. | <=3 |
| 2 | B02 | 14 due Sep 4, six stock Sep 4 and eight inbound Sep 8; fixed-supported, unreserved. | <=3 |
| 3 | B03 | 15 due Sep 7, four stock Sep 7 and 11 inbound Sep 10; fixed-supported, unreserved. | <=3 |
| 4 | B04 | 9 due Sep 8, three stock Sep 8 and six inbound Sep 11; fixed-supported, unreserved. | <=3 |
| 5 | B05 | 18 due Sep 4, 11 stock Sep 4 and seven inbound Sep 11; fixed-supported, unreserved; beware prior overcount behavior. | <=3 |
| 6 | N01 | Ten due Sep 4; customer **forbids partial**. Eligible original shortage investigation, but no binding two-slice candidate is allowed. Finding or abstention may be appropriate. | <=3 |
| 7 | R03 | Pinned original `offer_without_supplier_commitment`: 20 requested by Sep 10; uncommitted supplier offer, no binding inbound and partial forbidden; `conditional` / `needs_evidence`. Scoped cited conditional finding or reasoned abstention; never promote offer, assert universal absence, or promise delivery. M1.5 source-first sheet awaits independent acceptance; historical R03 Groq responses contained scoped-absence semantic errors. | <=3 |
| 8–10 | N02, N03, N04 | Fixed-only controls (cancelled inbound; stale stock; bounded pool with no binding source). Ineligible to hybrid; no model calls, no claim of universal absence. | **0** |

Source basis: [M1.8 dated supervisor decisions](m1.8-developer-review-decisions.md),
[M1.5 source-first reference sheet](m1.5-answer-sheet.md), the exact separate
Phase 1C pin `90c0bc8e285ee69262c7db826b786096a77ad004`, and the frozen
10-case run/bundle/source identities in the JSON manifest. Compare returned
references and dated slice support with the pinned verifier and perform later
human semantic review; never infer accuracy from these fixed schedules alone.

## Budget and ownership proposed for **one approval**

Seven eligible assessments sequentially, three fixed-only controls last.
`openai/gpt-oss-120b` on the owner's existing Free Groq account, with no
billing change. **At most 21 total inference requests**, maximum three per
eligible case: two native-function decisions at 512 configured completion
tokens each and a structured final at 1,024; no D4 revision, fallback,
retry, parallel requests or new provider. **14,336 configured output-token
ceiling across seven cases** and **8,192 serialized UTF-8 request bytes per
request** (at most 172,032 request-body bytes across 21 requests). The
configured ceiling is not actual billable usage. Count reported prompt and
completion tokens cumulatively; stop after a case if the **60,000 reported
total-token threshold** is exceeded. Because prompt token count is reported
*after* a send, that threshold is an observed stop gate, not a hard input-token
or financial ceiling; the last case could cross it. Unknown/missing usage
stops immediately. B01's two-request 3,537-token observation is not a
forecast of this campaign's cost or model behavior. Verify Free-tier quota,
billing-off status and current account conditions with Ali before any POST.

Campaign scope digest: `8dbaac541012a21c76b71e5a77af53c43dac2aa357417098a374bc7ae79ba8bd`. Approval must cite this
digest and the ten ordered cases; it is an identity check, **not** a secret.
No approval is inferred from possessing the credential or running metadata
preflight. Do not set `authorized=True` or launch the transport until owner
approval has been explicitly recorded. The earlier B01 approval does not
authorize this campaign.

## Preparation and execution protocol (no hosted call in preparation)

1. Create **three fresh separate disposable PostgreSQL databases** on the
   authorized thesis test instance: synthetic B/N fixture, reference-only
   R03 fixture, and checkpoint. Load identical pinned schema, pinned reference
   rows and compiled rules into both fixture databases; add the nine M1.8
   synthetic cases **only** to the B/N database. A combined fixture changes
   R03's selected-source fingerprint and must fail the frozen manifest check.
   Neither DB is an operational deal database.
2. Verify exact Phase 1C checkout and manifest hash, all ten source identities,
   six original fixed mappings and expected seven eligible/three fixed-gate
   excluded cases in read-only preflight **before the first send**. A future
   source change needs a newly reviewed manifest and new campaign approval,
   not an updated hash in the existing run. Validate empty checkpoint, fresh
   `0700` owner-only reservation directory on a durable single-host filesystem,
   one worker, same directory inode and DB for every case. Never reuse B01's
   previous receipts or checkpoint. Check CI where access is available; require
   a passing fresh local pinned mocked campaign and full regression regardless,
   credential file shape/ownership, and one sanitized authenticated model
   metadata GET. GET is not inference, billing or account-tier verification.
3. Once authorized, invoke dormant
   `hybrid_campaign_execution.execute_authorized_campaign` through the
   owner-only private credential launcher. The campaign journal (0600) fsyncs
   each case reservation before execution, and each model send uses its own
   fsynced receipt plus PostgreSQL raw-response checkpoint. The process runs
   one case at a time; original six findings, tools, candidate checks and
   reviewer handoff remain isolated by assessment. Do not copy reviewer
   expectations, discovery baseline or identity manifest into a model request.
4. If complete or stopped, use **read-only** `report_saved_campaign` to
   reconstruct seven eligible observations (or a partial report with separate
   unreconciled starts) from checkpoint and journal. Preserve raw responses
   only in private checkpoints, not public reports. Include request/body cap,
   token, latency, tool, citation, fixed-candidate and abstention denominators;
   record human source-first semantic judgment separately. Compare the
   unchanged historical iterative arm only with matched source identities,
   not as a newly authorized hosted comparator.

**Global stop immediately:** changed source/pin/config/run identity; mutable
or reused database/receipt/inode; failed permission, tool or budget gate;
provider HTTP/429/timeout/unknown send; missing usage; unauthorized citation
or evidence access; conditional offer treated as binding; unsupported dated
quantity, fabricated approval/reservation/promise; changed original six
findings; incomplete reviewer handoff; any unresolved audit or safety concern.
A single contained, checkpointed `invalid_binding_shape` or premature
`binding_paths_required` may be measured and the next case attempted if the
original, reviewer package and source identity remain intact. **A second
contained contract failure stops the campaign**, as do all other error codes.
Do not rerun an uncertain case. A safe abstention is a result, not a failure.

**Skipped diagnostic classification:** The seven skips in the 198-test prior
regression were two read-only historical Gemma saved-wire tests and five
historical Gemma one-shot diagnostic tests requiring those saved checkpoints;
none exercises hybrid campaign safety. The new pinned ten-case mock campaign,
restart/receipt tests and PostgreSQL hybrid tests are **mandatory** for this
hosted gate; a skip or failure among them blocks inference.

**Preparation evidence (27 October):** A fresh PostgreSQL 16 synthetic fixture,
separately loaded pinned-reference fixture and separate checkpoint database,
all under `/tmp/opencode`, passed the complete backend regression: **207 tests,
200 passed, seven historical Gemma diagnostics skipped**;
`/tmp/opencode/dealdesk-hybrid-campaign-validated-suite.log`. The ten-case
scripted HTTP double made **19** sequential mock requests, constructed five
fixed-supported B candidates with six rerun mappings each, abstained for
N01/R03, and performed zero hosted calls for three fixed controls. It verified
read-only checkpoint reporting and original source fingerprints. This is
**not** a 5/5 hosted success rate. The actual frozen campaign permits up to 21
requests; the mock happened to use fewer. Authenticated metadata GET returned
HTTP 200 for the intended Groq model with the owner-only key, but did not
verify current Free-tier limits or account billing. GitHub Actions status was
not readable here (`gh` unavailable; unauthenticated private Actions API 404).
If it remains inaccessible before inference, disclose that uncertainty and
proceed only if Ali's single campaign authorization explicitly accepts the
CI-unobserved risk alongside the fresh local regression; never claim CI passed.
