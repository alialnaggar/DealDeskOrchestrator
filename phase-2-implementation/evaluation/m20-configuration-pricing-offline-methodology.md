# M2.0 — Configuration/Pricing AI offline implementation and acceptance

**27 October 2026; opt-in mock-model milestone, not a live-model quality result.**
The Phase 1C source pin remains
`90c0bc8e285ee69262c7db826b786096a77ad004`. The existing original
LangGraph, iterative Fulfillment comparator, six deterministic responsibility
results, approval routing and exact candidate verifier remain authoritative.
No new business calculation, substitution, repricing, reservation, approval or
hosted provider request is implemented by M2.0.

## Business example and Week 1 gate

For synthetic B05, the original asks for **18 units by 4 September**;
pin-selected early stock supports an earlier dated slice, while binding
inbound supports a later one. An offline Groq-wire double first submitted
an **11+18 overcount**. The trusted pinned verifier rejected the total and
the bounded Fulfillment correction flow issued only safe constraint feedback.
The mock then submitted **11+7** with the exact *returned* inventory and
inbound references. A permissioned `inspect_fulfillment_paths` call and its
checkpointed ledger bind the cited sources; Phase 1C independently checked
the candidate and all six deterministic responsibilities, including Routing.
The reviewer comparison retained the immutable original, the first rejection,
`supply_supported_unreserved` for the isolated candidate, and pending
customer/human acceptance. This is a scripted **integration demonstration**,
not a Groq-generated success or evidence of candidate quality. The first
version of this new test used a date that was not in the returned path;
revision eligibility correctly failed. The test was corrected to the actual
returned early option without changing the business rule or model adapter.

Other existing offline/Pg tests cover malformed whole-unit quantities,
forged citations, conditional supplier offers remaining unverified, provider
errors, separate Credit/Policy blockers and restart across a completed tool
or candidate boundary. This milestone adds a single combined corrected-final
and M2.0 reviewer-path test; it does **not** perform a live Groq tool
execution, final structured response, candidate proposal or correction.

## M2.0 contract and control flow

`m20_specialists.py` provides a **provider-independent `M20Model` protocol**
and version `m20-ai-investigation-v1`. `run_m20_offline` requires marked
offline model doubles and an already-completed original fixed assessment.
Its small typed LangGraph runs Configuration AI, then Pricing AI, then a
safe reviewer handoff. The original LangGraph and six deterministic slots are
not rewritten. Pricing AI skips if *fixed* Configuration is not valid or
fixed Pricing did not run; Configuration AI itself may abstain/error without
falsifying the fixed result. The opt-in continuation holds its own
`m20_ai_results`, append-only `m20_model_attempts` and `m20_review` checkpoint
fields. For a completed original without a prior reviewer package, the
existing original-only package builder now supplies a human handoff; otherwise
the only reviewer-package addition is `m20_ai`:
validated observed fields, status, fixed review status and withheld route;
no model prose or approval decision. A resumed completed run does not call a
model or charge tools again; a reserved model call interrupted before a
recorded response is terminal rather than replayed.

Each specialist has **one separately named read-only inspection tool**
registered in the existing default-deny `TrustedToolScope`, with a
line/assessment/customer/subject/source-fingerprint identity. A tool reads
only the sealed, validated Phase 1C pool, not SQL. Configuration can inspect
the selected line's product/configuration and applicable fixed compatibility
rule/BOM observations. Pricing can inspect the selected quoted/list/cost
fields, the *already calculated* Phase 1C discount/margin facts and scoped
fixed pricing-rule hits. Multi-line pricing hits without an exact line
attribution are not presented as line-specific. The checkpointed M1.2 tool
ledger records reservations, permitted refs and returned records. Limits:
three model turns per specialist, at most two inspections, the shared
12-call ledger, at most 25 records/16,384 observation bytes, 4,096 input bytes,
8,192 output bytes, and at most six claims. These are engineering ceilings,
**not** business thresholds.

The model can request an authorized inspection, submit a typed finding, or
abstain with one of three reason codes. Findings are **exact typed
observations** (`ref`, `field`, `value`), not free-form economic conclusions.
Each is accepted only if its category, ref, field, type and value match an
actually returned scoped ledger record; a forged ref, swapped domain, wrong
price, overlong/malformed action, unavailable source or wrong identity is an
AI error with zero validated claims. Model uncertainty text is private audit
data and never placed in the review projection. Neither AI result can assert
configuration validity, margin clearance, credit sufficiency, policy waiver
or approval. A compatible Configuration substitute or Pricing price revision
would require separately approved fixed candidate interfaces.

## Test matrix and interpretation

| Offline scenario | Asserted boundary |
| --- | --- |
| B05 recoverable shortage; genuine returned stock/inbound; mocked overcount then corrected final | First proposal rejected; exact bound correction fixed-checks one candidate with all six mappings; reviewer keeps original and pending human acceptance. |
| B05 Configuration and Pricing positive findings | Distinct model decisions and tool receipts, exact product sellability and Phase 1C margin fact citations; six fixed originals, review status and candidate result unchanged. |
| N01 abstention and independent Pricing | Configuration AI abstains; fixed Configuration still controls eligibility; Pricing may inspect under its own scope. |
| Pinned offer-only reference | Fulfillment remains **conditional**; Configuration/Pricing observations cannot promote supply or create a candidate. |
| B02 forged product, B04 cross-domain/wrong-line tool | AI error or denial; reviewer receives no forged claim, Pricing fixed results do not change. |
| Disposable B03 non-sellable product | Phase 1C fixed Configuration marks infeasible; Pricing AI is skipped, not treated as calculated by a model. |
| PostgreSQL restart and process interruption | Completed results do not rerun model/tools; an uncertain reserved model turn is terminal, never resent. |

**Evidence level:** Source-first synthetic and pinned reference fixtures,
scripted mock-model outputs, local isolated PostgreSQL. No independent
evaluation accuracy, provider-model superiority, latency or cost claim.
The post-contract-edit local full regression on fresh business/checkpoint
databases completed **225 tests: 218 passed, seven unrelated Gemma skips**;
the CI workflow provisions separate M2.0 fixtures and must be checked after
the push before claiming a remote CI pass. A first full attempt reused a
checkpoint and correctly failed its restart-identity check; no production
fix was needed. CI does not run hosted inference.
Further hosted inference requires a separate exact-case/limits authorization;
the accepted B06 decision-only authorization is spent. A candidate including
conditional supplier supply remains unverified under the pinned Phase 1C
interface. Before Week 3: review M2.0 claim/tool security, complete its CI
gate, choose whether to activate a bounded hosted Configuration/Pricing model
adapter under a separately approved evaluation, and define Credit/Policy/
Routing scoped contracts and accepted source-first cases. No paid API or
Phase 1C pin upgrade is implicit.
