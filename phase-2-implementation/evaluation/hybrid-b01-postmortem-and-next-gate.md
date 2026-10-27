# Adaptive hybrid B01 postmortem and bounded next evaluation gate (27 October 2026)

## Saved observation, not a rerun

On synthetic B01 a customer asked for ten units by 4 September 2026. The
source-reviewed schedule, kept outside model input, has eight fresh stock units
deliverable 4 September and two confirmed inbound units deliverable 8 September;
even a fixed-supported split still requires customer acceptance and human review.
Groq `openai/gpt-oss-120b` used the counted authorized line-supply prefetch but
chose `submit_proposal` rather than inspecting binding paths. The final request
proposed eight plus two both on 4 September, used unprefixed IDs and used
`binding_partial_delivery` where the required tradeoff code is
`partial_delivery_requires_customer_acceptance`. It failed `invalid_binding_shape`
before candidate construction. Original six fixed findings stayed
`needs_revision`; zero candidates, zero validated AI summaries, human approval
not granted. The checkpoint contains the raw rejection; previously the reviewer
package projected zero rejections. Two requests took 1,557 and 1,986 ms HTTP
time; reported 2,303 prompt and 1,234 completion tokens. No third request.

## Offline engineering changes

Proposal intent is absent from the decision wire until a completed, untruncated
`eligible_binding` path observation for the exact line; the graph independently
rejects a premature intent before a final request. This is an *inspection*
prerequisite, not verification that any schedule works. Final schema and prompt
spell out the canonical tradeoff code and `category:id` citations without
including a source-reviewed candidate answer. Only the pinned reader can
verify dated quantity and exact source-to-slice support. The original six
specialist mappings and isolated candidate rerun remain unchanged. Reviewer
projection now shows rejection count and codes without raw model output.
Model sends retain request bytes, measured local elapsed time, token metadata
when supplied, and append-only reservations; interrupted sends remain
non-retryable rather than silently repeated. D4 offline revision remains
limited to one fresh model response with feedback after recoverable local
rejection; the prior rejected output stays in the private checkpoint. Hosted
smoke budget still disables revision. No ordinary-assessment activation,
business-rule change, Phase 1C pin change or hosted inference occurred in this
increment.

`hybrid_evaluation.capture_hybrid` is read-only and model-blind. It requires a
terminal matching checkpoint and all six original mappings; optional reviewer
baseline is matched on sealed identity and is never passed to the model. Count
attempted cases including errors. Record fixed-supported six-mapping candidates,
abstentions, rejection codes, model/tool counts, returned-reference syntax
coverage, available request elapsed times and reported token totals. Returned
IDs alone do **not** establish citation accuracy: per-slice support needs the
pinned verifier and semantic quality needs independent source-first human
review. Missing usage/latency is unknown, not zero; no accuracy or superiority
is claimed. The unchanged iterative comparator remains separate.

Fresh isolated local PostgreSQL 16 fixture and separate checkpoint databases,
loaded from the pinned schema/reference rows and compiled 105 commercial rules,
ran the complete backend suite: **198 tests, 191 passed, seven optional
saved-checkpoint diagnostics skipped**. Log:
`/tmp/opencode/dealdesk-hybrid-final-suite.log` (local, not a repository
artifact). Mocked hosted B01 used three reserved requests and produced the
fixed-supported two-slice candidate with six candidate mappings, returned
source references and pending customer acceptance. Offline D4 tests exercised
one corrected proposal and one abstention; adverse B05/N01 produced no
candidate, and N02 stopped at the fixed eligibility gate. Other coverage
includes invalid binding, wrong slice citation, crash/restart and request
budgets. These tests do not measure hosted multi-case task quality. GitHub
Actions for this increment has not yet been observed.

## Next representative hosted gate (proposal, **not authorization**)

After independent review of fixture source identities and the offline report,
request case-specific approval for one pass of five source-reviewed eligible
binding cases B01–B05 and the eligible adverse N01, **at most six assessments**,
with a ceiling of **three requests per assessment, 18 total**, no retry or
revision, and each decision/final cap of 512/1,024 completion tokens under
the existing 2,048-token per-assessment sum cap. These are *maxima*, not a
promise that each case can reach a final; count denied, failed and uncertain
sends. Worst-case requested output ceilings sum to 12,288 tokens across six
cases; prompt tokens, latency and provider cost are not known in advance. The
observed B01 3,537 total tokens is descriptive only, not a price forecast.
Use unique assessment/receipt identities and fresh separate PostgreSQL
business/checkpoint databases at the exact pin. Prepare reviewer expectations
source-first, outside wire input and tools, before transmission. Measure
rejection rates, verified candidates, abstentions, evidence and token budget,
dated citation support and human semantic ratings alongside the unchanged
iterative comparator on independently authorized cases. Add conditional,
stale, truncated and fixed-gate excluded controls **offline**; do not count an
ineligible case as a hosted agent failure. Stop the entire hosted batch on
identity mismatch, unexpected cost/billing, repeated wire failures or an
unexplained safety violation. Obtain new explicit owner approval for the exact
case set, call ceiling, provider account and cost conditions before any POST.
