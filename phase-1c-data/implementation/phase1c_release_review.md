# Phase 1C release review — provisional decisions

**10 October 2026.** This is the compact review sheet for the generation freeze. The 36-deal development pilot passes PostgreSQL, and 80 customer masters and 400 historical inputs/runs have been generated. Historical labels, completed specialist executions, and the final independent evaluation release remain open. `ready_for_generation` remains false.

[PostgreSQL Actions run 37821625969](https://github.com/alialnaggar/dealdeskdata/actions/runs/37821625969) passed the typed-row, manifest, provider-reader, and full decision workflow after aligning the reader with the new evidence record shape. The local suite has 165 tests, with 35 database cases exercised in CI rather than locally.

## Decisions already bounded by executable evidence

| Decision | Current rule and evidence | Limit |
| --- | --- | --- |
| Product popularity | The top-fifth 60–70% historical line share is an explicit **synthetic coverage target**, not an Olist-derived enterprise statistic. Config and field basis reject a silent observed-source claim. | Check achieved share and per-product minimum on the 400 generated historical deals. |
| Capacity horizon | A confirmed component receipt beyond represented capacity dates yields `unknown`, with no invented later production slot. BUILD-HORIZON and stale-capacity cases pass in PostgreSQL. | A longer lead is not a longer capacity forecast. |
| Offered configurations | The draft's 18 make-to-order products and 24 offered BOM variants have exact signatures and one effective BOM per offered configuration. | Detailed sourced part fit remains open for 23 BOMs; structural coverage does not prove hardware compatibility. |
| Digital and shipping evidence | The pilot checks an independent full-term provider manifest, missing/partial proof, and dated Central/West shipping. | Provider and lane records are synthetic; no real commitment is claimed. |
| Ledger types and locations | The field checker now distinguishes 18 `TIMESTAMPTZ` fields from the one `TIME` field. Pilot source locations are restricted to the configured Central and West sites with matching origin time zones. | The full generator must obey the same mapping. |

## Remaining decisions before generation

| Gate | Field marks | Required closure |
| --- | --- | --- |
| Product fit, price and cost | `products.attributes_json`, `products.list_price`, `products.standard_cost` | Sourced comparable configurations and dated EUR price/unit/tax basis; check cross-kit interfaces, thermal and power limits for the remaining 23 BOMs; reconcile the €1,050 workstation and proposed margin band. Otherwise retain clearly synthetic price and fit assumptions with explicit limits. |
| Distribution | `customers.industry`, `customers.country_code`, `deal_lines.product_id` | Generate 80 customers and 400 historical deals, then measure country/industry, top-fifth product share, at-least-three occurrences per SKU, line-count bins and configured tolerances. The 36-deal case-designed pilot is not that sample. |
| Source evidence and replay | `customer_credit_profiles.commitment_evidence_ref`, `accounts_receivable.as_of_date`, `inbound_supply.evidence_ref`, `deals.evidence_refs_json`, `deal_runs.data_snapshot_ref` | The manifest validator checks typed provider records, full-term binding coverage, reference resolution, SHA-256 snapshot entries and as-of ordering. The pilot is pinned as `PILOT-OPERATIONS-SNAPSHOT`. Historical reader runs now require a complete frozen credit/AR manifest matching the run cutoff; generate and validate those manifests plus independent no-PO inbound proof before closing this gate. |
| Row and relationship checks | `suppliers.order_calendar_json`, `compatibility_rules.condition_json` | Execute typed row checks on all generated rows, dependency and installation predicates, and supplier lead/dispatch calendars. The pilot validator now closes the location, requirements, and per-mode line-configuration checks on 36 deals / 65 lines; dependency coverage remains open. |
| Runtime output | `agent_execution_log.output_json` | `validate_phase1c_runtime_outputs.py` now checks unique attempts, outcome-free inputs, typed output envelopes, agent identity and manifest evidence IDs. Populate and validate actual specialist runs; never fabricate execution logs as source data. |

The two remaining calibration-level review items are the provisional **36 components / 156 products** mix (structural BOM coverage exists, detailed sourcing/fit does not) and comparable **catalogue price dates, currencies, units and tax bases**. The ledger now has **six field marks** open after evidence-backed disposition of eight marks. No final threshold, source claim, distribution tolerance or release target is frozen by this sheet.

## Immediate build order

Historical operational replay now fails closed without a complete dated
manifest. This prevents later stock, supplier, capacity, digital or undated
shipping lane rows from leaking into a past run. No-PO confirmed receipts
require matching supplier evidence. The 400 queued runs therefore still need
their actual operational source ledger before baseline decisions can be
derived; the field marks remain open.

The provisional operational source has daily dated stock for 48 products,
38 standard lanes, 54 supplier/component offer SKUs, independently proved
inbound receipts, a dated workshop plan and synthetic digital provider pools
across all 400 cutoffs. They are hash pinned. Workshop feasibility does not
book a slot. Measure source distributions before deriving historical outcome
labels.

1. Generate independent credit, no-PO inbound and historical AR manifests; replay historical rows at their frozen as-of times and validate actual runtime output envelopes.
2. Finish product fit and comparable price/cost evidence, or explicitly label any unresolved values as bounded synthetic assumptions for thesis scope.
3. The provisional 80-customer master and 400 chronological historical input deals / 1,200 lines are generated. Their configured line bins and product share are exact. A separate synthetic source ledger resolves 400 SHA-pinned dated credit/AR views, and 400 queued baseline runs link to them. Generate and connect operational snapshots, derive documented baseline decisions and measure source provenance before constructing the 100 generated tests.
4. Author the 36 evaluation variants and expected findings independently, keep them outside agent-visible inputs, then run fresh import, repeat-seed checksum and decision gates. Only then freeze the dataset version.

## Dated workshop capacity increment — 9 October 2026

A separate hash-pinned synthetic workshop plan resolves 180 resource/day rows
per historical cutoff: 30 represented days across assembly, configuration and
test, each with equipment and workforce. Daily observations are within 24 hours
of each run cutoff; weekends have zero available hours. Existing allocations
and downtime follow provisional ranges. The resolver rejects missing days and
source digest changes; selection rejects future snapshots. This supports a
**feasible, uncommitted** build path, not a booked production slot. Capacity
beyond the window remains unknown. Baseline decisions, 14 field marks and two
calibration reviews remain open.

## Dated digital provider increment — 9 October 2026

A synthetic independent pool ledger now covers 36 of 41 digital SKUs in the
five configured countries, with daily as-of observations and six-day proof
refreshes. Across 5,580 pool epochs, the configured binding/provisional/unknown
mix is exactly 70/20/10%. Binding rows have separately hash-pinned provider
proof for the exact product, configuration, region, 12-month term, unit,
capacity and allocation; the proof states a full-term coverage interval.
Missing, changed or future proof fails closed. This is **synthetic test
evidence**, not a real provider promise. The five SKUs without exact pool
coverage remain unknown. The provisional protected-TB pool totals use the
instance range pending calibration review. The source resolves at all 400
historical cutoffs; generated historical decisions and actual agent execution
still have not been run.

## Historical baseline diagnostic — 9 October 2026

The disposable PostgreSQL pass read all 400 queued runs with compiled baseline
policy and frozen credit, operational and provider evidence. It wrote a
separate provisional diagnostic artifact and rolled back the imported rows;
no expected outcome or agent execution was written to deal inputs.

The first pass exposed a source-cadence mismatch: monthly commitment
observations made 386 of 400 credit views stale under the existing 24-hour
freshness rule. A provisional independent daily observation schedule at 85%
capture now yields 329 fresh and 71 stale views. The agreed calibration file
and threshold were not changed. Service coverage rules for 22 products now
cover DE, NL and BE with one explicit excluded region in each; FR and AT
remain unknown, and no service slot is claimed. Missing service coverage
fell from 184 to 52 line findings.

[PostgreSQL diagnostic run 37956989726](https://github.com/alialnaggar/dealdeskdata/actions/runs/37956989726)
passed all 400 reads. Its provisional gate distribution is 6
`approval_required`, 30 `needs_commitment`, 129 `needs_evidence`, 211
`needs_revision` and 24 `blocked`. Evidence-gap counts include 71 stale
credit commitments, 438 missing delivery findings, 185 missing digital
confirmations and 52 missing service coverage findings. These are overlapping
line/run findings, not exclusive deal counts. Delivery gaps need a per-mode
review before any historical labels are materialized or used for training.
The 14 field marks and two calibration reviews remain open.

## Historical workshop alignment — 10 October 2026

The provisional source now locates all 36 component SKUs at the configured
Central workshop. Finished stock continues to use the configured locations.
The reader also reports an unschedulable build as `infeasible` or `unknown`
according to its production classification, rather than leaving a
`pending_production_check` fulfillment status after the check has run.

[PostgreSQL run 38022399576](https://github.com/alialnaggar/dealdeskdata/actions/runs/38022399576)
passed the full workflow. All 220 historical make-to-order lines have matching,
selected BOMs; 200 now have feasible but uncommitted builds and 20 are
infeasible without replenishment. The 400-deal provisional gate mix is 6
`approval_required`, 24 `blocked`, 69 `needs_commitment`, 212
`needs_evidence` and 89 `needs_revision`. Evidence-gap findings are 71 stale
credit commitments, 238 missing delivery findings, 185 missing digital
confirmations and 52 missing service coverage findings. These findings can
overlap within a deal. The 20 material shortfalls and the remaining evidence
gaps require review before any labels or execution logs are authored.

## Dated inbound source increment — 8 October 2026

The independent provisional inbound ledger now has 441 supplier/component receipts across 63 products and seven monthly observation dates. Its Confirmed/Planned/Delayed/Cancelled mix follows the configured 70/20/8/2% target within 0.5 percentage points. Four SHA-256-pinned shards and a matching 400-cutoff index supply dated PO headers or independent supplier proofs for confirmed no-PO receipts. The historical resolver validates all 400 views; expired confirmations remain historical records but are not binding. Historical labels, actual execution logs, detailed product fit and comparable prices remain pending. The 14 field marks and two calibration reviews stay open.

## Remaining gap classification — 10 October 2026

[PostgreSQL run 38024615223](https://github.com/alialnaggar/dealdeskdata/actions/runs/38024615223)
passed the full workflow with a per-mode diagnostic and a corrected digital
gate. Of 185 previously reported digital confirmation gaps, 108 have fresh,
full-term provider proof and enough capacity but cannot meet the requested
activation date. They now receive a date revision; the other 77 have no
matching pool and remain evidence gaps. The provisional 400-deal mix is 6
`approval_required`, 24 `blocked`, 69 `needs_commitment`, 142
`needs_evidence`, and 159 `needs_revision`.

The 238 delivery evidence findings comprise 213 supplier-finished, 20
make-to-order, and five stocked-finished lines. Supplier-finished lines
include 168 conditional offers and 45 infeasible supply findings; an offer
is not a binding receipt. The remaining evidence findings are 71 stale
credit commitments, 77 digital pool gaps, and 52 service coverage gaps.
These counts overlap across deals and do not establish final labels.

## Weekly provisional inbound pipeline — 10 October 2026

The original monthly inbound observation schedule left 205 of 213
supplier-finished lines without a binding receipt even though confirmed
receipt history was visible: nine-day confirmations expired before many
deal cutoffs. The configured evidence recheck cadence is seven days. The
provisional independent source now records a fresh supplier pipeline each
week, with 1,764 separately evidenced events for 63 SKUs, while preserving
the configured 70/20/8/2% status mix and nine-day validity. It does not
extend old confirmations or use deal outcomes to create receipts.

[PostgreSQL run 38042504618](https://github.com/alialnaggar/dealdeskdata/actions/runs/38042504618)
passed. Of 257 supplier-finished lines, 159 are confirmed by the requested
date, 29 have a late alternative, 60 have conditional offers, and nine are
infeasible. Total missing delivery findings across physical lines fell from
238 to 82. The provisional 400-deal gate mix is 11 `approval_required`,
24 `blocked`, 102 `needs_commitment`, 124 `needs_evidence`, and 139
`needs_revision`. The weekly pipeline cadence and outcome mix remain
subject to calibration review; no historical label is frozen.

## Field-ledger disposition — 10 October 2026

Seven of the 14 previous `review_before_generation` marks now have a
`resolved_by` entry in `phase1c_column_rules.yaml`: customer industry and
country quotas; independent credit commitment evidence; frozen nonfuture
AR replay; no-PO inbound supplier proof; achieved historical product
popularity; and complete SHA-pinned run snapshots. The column checker still
covers all 266 columns in 24 tables and deliberately reports
`ready_for_generation=false` with seven open marks.

The remaining marks are `products.attributes_json`, `products.list_price`,
`products.standard_cost`, `suppliers.order_calendar_json`,
`compatibility_rules.condition_json`, `deals.evidence_refs_json`, and
`agent_execution_log.output_json`. The first three and the two calibration
reviews need an explicit synthetic-scope or sourced-fit/price decision;
actual agent outputs must come from execution, never generated as source
rows. The independent 100-test and 36-case evaluation release still needs
construction and its own answer-key review.

## Deal document scope — 10 October 2026

The typed deal reference validator now rejects a trusted customer document
unless its independent record names the same deal. A matching, timely
document passes; missing, future, altered or cross-deal references fail.
Historical deals have empty reference arrays and make no document-proof
claim. `deals.evidence_refs_json` now has a `resolved_by` entry, leaving
six open field marks: product attributes, list price, standard cost,
supplier calendars, compatibility predicates and actual agent output.
Supplier calendar and receipt/offer linkage are not inferred where the
schema has no specific supplier-item reference on an inbound receipt.

The compatibility evaluator now checks `requires_product` and
`excludes_product` within each declared line or configured group. A target
product in another group no longer satisfies a same-group dependency. The
regression covers both separated and shared groups. The field mark remains
open for full generated-rule coverage and product-fit evidence.


## Expanded agent capability note — 11 October 2026

The revised [Phase 1B architecture](../../phase-1b-agent-architecture/agent-architecture-and-deal-flow.md) specifies bounded, evidence-backed alternatives and a cross-specialist recheck loop. The [Phase 1C data strategy](../design/data-strategy.md#19-structured-input-recommendation-extension--11-october-2026-target-design) maps the required facts and open trace decision. This is a **design addition**, not a completed six-agent runtime or a change to this release's calibration/field marks. The core structured input is largely sufficient; candidate identity, auditable reruns, product-fit/price evidence and independent alternative-quality cases remain open.

First retain the 24-table schema and specify a typed candidate record. Test one shortage → allowed partial delivery or substitute → full affected-check rerun example with immutable submitted facts and no order, stock-reservation or human-approval side effect. Use its trace to decide whether separate correlated runs suffice or a small schema migration is justified. Expand independent scenarios and close existing fit/price reviews before describing AI-generated options as verified. Historical diagnostic outcomes do not supply an independent answer key for this experiment.

## Candidate contract checkpoint — 11 October 2026

The first implementation increment is `phase1c_candidate.py` with four
contract tests in `test_phase1c_candidate.py`. A typed proposal records
parent identity, exact changes, constraints, dated source references, frozen
versions/snapshot, delivery slices, assumptions and the business tradeoff.
The shortage example accounts for all 20 requested units (12 dated-stock
units on time and eight later conditional-offer units). It rejects missing
partial permission, lost units, a split indivisible group and reuse of the
unchanged parent deal as a purported candidate run. This is a synthetic
**proposal-shape and correlation test**, not a supplier proof, actual
specialist execution, independent evaluation case or full affected-check
rerun. The PostgreSQL workflow includes the contract test.

**Evidence for the persistence decision:** `deal_runs` references a stored
`deal_id`; `read_run` selects the submitted `agent_visible_deals` and
`deal_lines` by that ID and does not apply changed fields from
`input_snapshot_json`. The original reader could only recheck the stored submission. The new
run-scoped candidate path now assesses separate delivery slices while keeping
the submitted date unchanged; its in-memory trace is still not persisted. A new
`deals` row with `supersedes_deal_id` would represent a new submitted
revision, which the proposal is not. The run-log uniqueness key also treats
attempts as retries. No schema or calibration changes are made here.

**Decision to review before a schema change:** allow an explicitly typed,
run-scoped candidate input and per-line delivery slices in the reader and
its frozen run context, or add the smallest persisted candidate identity and
schedule relation needed to audit that input. Either path must demonstrate
that Configuration, Pricing, Availability, Credit, Policy and Approval all
recompute for the *same* candidate and evidence snapshot, with the original
submission untouched. Until then, `full_reader_recheck` is blocked. Next
build the reader-backed experiment and human comparison after that input
representation is reviewed; add a no-safe-option case and independent
answer review. Six field marks, two calibration reviews, 100 generated tests
and 36 independent evaluation variants remain open. `ready_for_generation`
remains false.

## Reader-backed candidate experiment — 11 October 2026

The draft PR now preserves `deals.requested_delivery_date` as the customer's
original date. `Candidate.changes` describes only the separate proposed
delivery slices, with each quantity and date; it cannot rewrite that date.
The read-only `read_run(..., candidate=...)` path reselects the same frozen
PostgreSQL evidence and recomputes the deterministic decision package. The
first supported scope is one stocked or supplier-finished physical line with
partial delivery permitted. It checks cumulative supply by each slice date
at one location, counts only fresh stock and binding receipts, and compares
the proposal's cited IDs to actual selected IDs. Offers and unbooked builds
cannot become confirmed delivery. The customer-date difference remains an
unmet constraint and keeps ordinary routing withheld pending acceptance.

Correlation now uses the same parent deal/run plus a SHA-256 fingerprint of
the reader-selected deal, lines, customer/credit, rules and operational source
rows, frozen context and proposed slices. `verify_run_correlation` recomputes
that fingerprint and the slice assessment; a changed source row or fabricated
finding fails. It no longer requires a different deal ID. A human comparison
contains the original and candidate deterministic statuses, actual source IDs,
dates, open customer constraint, assumptions and tradeoff. It makes no approval
or delivery commitment. The PostgreSQL test inserts an isolated submission
inside a rolled-back transaction: ten requested units by 4 September, eight
from dated stock by that date and two from a confirmed receipt by 8 September.
The 24-table schema and calibration remain unchanged.

**Limits and next gate:** this run-scoped candidate trace is returned in memory,
not persisted as an agent execution or auditable candidate record. Only a
partial-delivery scenario is reader-backed; substitute, repricing, multiple
lines/groups, conditional offers and no-safe-option cases need their own
source-backed tests. It is a deterministic six-responsibility recheck, not
six AI agents. Before a schema migration, decide whether an append-only trace
artifact tied to the existing run/candidate digest is sufficient for the
thesis audit, or whether persisted candidate identity/schedule fields are
necessary. No generation field mark or calibration review closes from this
example. `ready_for_generation` remains false.

## Safe refusal and source selection — 11 October 2026

The reader-backed experiment now tests a **no validated option** case: the
second slice is requested before the dated receipt could arrive. The human
comparison says to request evidence or stop; it does not present that
schedule as a verified option. Any later slice must explicitly retain the
unmet `original_requested_delivery_date` customer constraint. The source
selector examines eligible single-location paths before rejecting an evidence
ID, so a valid West path is not lost because Central has a different source.
A cited unknown ID still fails closed. These tests do not add independent
answer labels or a general candidate search algorithm; the generation gate
and six field marks/two calibration reviews remain open.

## Candidate trace export and replay — 11 October 2026

`phase1c_candidate_trace.py` can serialize the reader-backed original and
candidate decisions, customer request, proposed slices, source IDs, frozen
versions/snapshot, specialist results and human comparison into a canonical
JSON record. It writes a candidate-named sidecar with exclusive creation, so
normal reruns cannot silently overwrite it. The record includes a SHA-256
content digest. A verifier recomputes the digest **and** rebuilds the record
from a fresh reader replay: changing a status fails even if someone recomputes
the file's own hash. The PostgreSQL integration test exports to a temporary
directory, verifies replay, rejects duplicate creation, and tests both forms
of tampering. No candidate or agent log is written to the 24-table database.

**Audit decision evidence:** a run ID plus candidate ID, frozen source-input
digest and exact slice payload can correlate the first option and its six
specialist decision results without another deal ID. This sidecar is an
engineering prototype, not an immutable, access-controlled production audit
trail: a filesystem administrator could replace both the file and its source
inputs, and there is no retention, signing or multi-writer coordination. It
supports continuing the first experiment without a schema change. Before
claiming durable governance, choose a controlled append-only artifact store
with independent retained hashes and permissions, or review a small schema
migration. The wider multi-candidate lifecycle and actual agent execution
remain to be tested. Six field marks, two calibration reviews and the
independent evaluation release remain open; `ready_for_generation=false`.

## Two-candidate isolation trial — 11 October 2026

`phase1c_candidate_batch.py` adds a bounded, read-only comparison of at most
two candidates against one parent run. It re-reads each candidate, verifies
that both used the identical frozen source-input digest, and produces separate
candidate trace records and human comparisons. Duplicate IDs, identical
proposals under different IDs, mixed parent runs and a third candidate fail
before an unbounded search can start. It never selects a candidate itself.
The PostgreSQL regression compares one supported 8-now/2-later plan with a
second plan whose later slice predates the binding receipt; only the first is
listed as having a verified supply option. Each has its own trace filename
and digest. This tests correlation and safe refusal for two alternatives,
not candidate generation, agent execution, customer acceptance or durable
audit storage. The schema, six field marks, two calibration reviews and
`ready_for_generation=false` are unchanged.

## Reader-backed sidecar replay — 11 October 2026

The sidecar verifier now has an explicit `replay_exported_trace` entry point:
it reads the original and candidate from PostgreSQL again and compares the
saved record to that fresh result. The regression replays each of two separate
candidate files, rejects a swapped candidate, and changes a dated inventory quantity after export to prove that a different reader-used fact invalidates the
saved trace. The lower-level verifier still accepts caller-supplied bundles
and does not itself fetch facts. This strengthens the prototype correlation
claim without making the local sidecar immutable or closing the audit storage
decision. No schema, calibration, generation-readiness or independent answer
review status changes.

## Calibration review evidence clarification — 12 October 2026

A review of the current 156-product portfolio, 24 BOMs and 18-product build
cost draft found no detailed interface/form-factor/power/thermal attributes
on any of the 36 components. Structural BOM coverage and rollup arithmetic
therefore do not validate physical fit. Exactly one of the 18 draft buildable
product margins exceeds its proposed category p90 value: workstation
`SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009` is 31.90% against 28%.
A category p90 is a distribution target, not a hard ceiling for each SKU;
this one comparison cannot justify an automatic price or cost rewrite. The
full 120-product generated distribution and comparable unit/date/tax basis
remain to be checked. See `../calibration-decision-sheet.md` for the exact
bounded-synthetic versus sourced-comparable choice. This is a read-only
review; no calibration, schema or readiness status has changed.

## Bounded synthetic fit scope selected — 12 October 2026

Ali selected Option A in `../calibration-decision-sheet.md`: fictional but
internally checked product/component specifications and declared synthetic
prices and costs. The new companion fit draft enumerates all 36 components;
its checker covers 24 active BOMs and 25 possible component sets, including
the substitute in BOM-001. It checks interfaces, board/drive form factors,
drive slots, platform, power and cooling and rejects deliberately incompatible
variants. This is an internal synthetic fit check, not manufacturer-certified
compatibility. The detailed specs are still a companion draft rather than
runtime catalogue attributes. Product-attribute and compatibility field marks,
price/cost evidence review, independent answer keys and generation readiness
remain open. No price, cost, threshold or schema was changed.

## Catalogue fit integration — 12 October 2026

The 36 fictional component specifications have now been copied from the
versioned companion draft into the draft catalogue's `attributes_json` rows.
The component JSON contract permits these fields, and the 24-BOM checker
requires the catalogue and companion facts to match exactly. The readiness
audit now distinguishes 24 internally checked synthetic BOMs from external
sourcing and price comparability. A changed catalogue interface, slot, power,
cooling or platform claim fails the fit check; the reader can select the same
catalogue attributes for future specialist use. This does not implement a
substitute-proposing agent or certify real hardware. The six field marks,
price/cost distribution review, independent answer keys and
`ready_for_generation=false` remain open. No database schema, threshold,
list price or cost changed.

## Full provisional price-distribution audit — 12 October 2026

The reproducible audit now measures all 120 sellable catalogue rows: 102
deterministically generated fixture rows and 18 explicit buildable drafts.
All 102 generated margins are effectively pinned to their category p50;
the achieved category p90 margins are therefore below the proposed p90
targets in all nine categories. This is a property of the generator, not
evidence that those targets or market prices are correct. One workstation
individual margin remains 31.90% above its proposed category p90 of 28%,
while the workplace distribution's achieved p90 is 18.18%. Price summaries
are separated by billing model and unit, and remain provisional even within
a unit because capabilities, dates and tax basis have not been matched.
`audit_phase1c_price_distribution.py` and its CI artifact make the
measurement repeatable; see `../calibration-decision-sheet.md` for the
exact fixed-p50-versus-bounded-variation decision to review. No commercial
number, threshold, schema or readiness flag was changed.

## Bounded margin spread sensitivity — 12 October 2026

A read-only experiment assigns the 102 generated products a reproducible
margin inside each category's proposed p10/p50/p90 band, using seeded product
ranks. It keeps list prices and all 18 buildable costs unchanged and reports
each generated product's experimental cost alongside its original. With a
hypothetical 10% quote discount, 12 current rows versus 41 experimental rows
are below the BASELINE_2026 category floor; two experimental workstation rows
have nonpositive quoted margin. Thirty-one product statuses change. This
checks sensitivity of line arithmetic only, not a full deal or specialist
rerun. The result is explicitly provisional: neither a new calibrated cost
basis nor a sourced comparable. The exact decision and caveats are in
`../calibration-decision-sheet.md`. Tests and a CI JSON artifact pin the
experiment. The catalogue, policy thresholds, schema, field marks and
`ready_for_generation=false` remain unchanged.

## Three-profile margin sensitivity — 12 October 2026

The read-only spread report now evaluates 0%, 10% and 20% quoted discounts
under lenient, baseline and strict category floors, preserving each changed
product ID. At strict 10%, the count below floor changes from 55 to 56, while
39 individual product statuses change. At baseline 10%, the count changes
from 12 to 41, including two nonpositive proposed lines. This remains
line-margin arithmetic, not a full deal decision: discount approvals,
exception windows and other specialist checks were not rerun. See the
nine-case table and exact adoption decision in
`../calibration-decision-sheet.md`. No calibration, catalogue, schema or
readiness flag changed.

## Evaluation authoring development examples — 12 October 2026

`../evaluation/` now holds two illustrative partial-delivery cases with
submission facts and dated evidence in `development_inputs.json`. A
separate `reviewer_oracle_draft.json` contains author-written expected
findings. The first has binding support for two later units; the second has
only an offer and should withhold a validated option. A new validator and
four tests check input shape, dates, quantities, evidence references,
answer-field leakage and premature review claims. These are **development
examples only**: no independent reviewer has accepted the draft answers,
the files are not access-controlled from one another, and the examples
lack the full cross-specialist database facts. The count of independently
reviewed cases remains **0 of 36**; the 100 generated tests remain
unfinished. The evaluator must later use distinct frozen full cases,
load only agent-facing facts into the system, and score against separately
reviewed answers and the rule-only baseline. No readiness, schema or
calibration status changes.

## Reader-backed development evaluation scorer — 12 October 2026

The existing PostgreSQL shortage regression now runs its rule-only original
decision and two separately rechecked candidate options **before** loading a
provisional reviewer-only draft. A small scorer compares the actual source
IDs, original customer date, later slice dates, decision statuses, six
deterministic reruns, human actions and no automatic selection against that
draft. It reports false supported options, missed supported options and
per-field mismatches. A tampered trace digest is rejected; rehashed false
support or omitted evidence fails the provisional comparison. This is a
development diagnostic over an existing reference fixture. The oracle has
not been reviewed independently, no agent produced either proposal and no
new held-out case or full specialist outcome label is claimed. See
`../evaluation/README.md`. Independently reviewed evaluation cases remain
**0/36** and the 100 generated tests are unfinished. Schema, calibration,
readiness and the draft PR status remain unchanged.

## Reader-fact partial-delivery discovery — 12 October 2026

`phase1c_partial_discovery.py` now derives one partial-delivery candidate from the reader's selected shipping options for a single ungrouped finished-product line. The reference shortage yields eight units by the unchanged 4 September customer date and two by the binding 8 September receipt, followed by a fresh PostgreSQL reader pass, all six deterministic checks, and a human comparison with no automatic selection. Tests cover permission and missing supply; the database test withdraws the confirmed receipt and expects no proposal. The source trace still records what the reader used, with no separate deal ID or schema migration. This is a bounded development fixture, with no independent outcome label, reservation, customer acceptance, substitute search or AI specialist implementation. Field marks, calibration review, 100 generated tests, held-out 36 answers (0 independently reviewed) and `ready_for_generation=false` remain open.

## Separate evaluation input preparation — 12 October 2026

A PostgreSQL test now creates a distinct synthetic product, inventory, inbound receipt, submission and run, then seals only reader-selected source rows into an input-only review packet. The packet omits derived findings and candidate outputs; overlap with named development IDs and content tampering fail. Shared customer, lane and versioned rules are stated explicitly. The fixture rolls back, so there is no durable held-out set, independent reviewer answer or agent evaluation result. **0/36** answers independently reviewed; 100 generated tests and readiness gates remain open. See `../evaluation/README.md`.

## Dependency coverage gate made measurable — 12 October 2026

`validate_phase1c_generated_rows.py` now runs the existing compatibility evaluator on each imported deal's source lines and reports configured non-installation rules, applicable deal-rule checks, and pass/fail/not-applicable counts. Its development example has no such rules and therefore reports a coverage gap; a paired test proves an applicable `requires_product` rule reports a failure and a non-applicable rule does not count as coverage. The currently inspected pilot SQL contains installation coverage rules but no populated `requires_product`, `excludes_product` or attribute rule. This instrument is not evidence that dependency coverage is complete. `compatibility_rules.condition_json` retains its review mark; no calibration, schema, data or readiness flag changed.

## Isolated dependency decision trial — 12 October 2026

An integration test constructs two temporary submitted deals over the existing pilot catalogue and dated stock: one includes a required add-on and one omits it. A typed `requires_product` blocker must pass for the first and produce an attributed configuration block for the second after a full PostgreSQL reader and deterministic deal decision. The row coverage audit sees both results. The test rolls back its rule and deals, preserving all pilot and historical outcomes. This proves the rule path, not generated-set coverage; `compatibility_rules.condition_json` remains open until the reproducible generator includes deliberate dependency cases. No schema, calibration or readiness flag changed.

## Reproducible dependency pair — 12 October 2026

`implementation/render_phase1c_dependency_pilot.py` deterministically creates two submitted synthetic inputs using the current catalogue: one includes a required add-on, and the other omits it. The PostgreSQL regression loads the generated SQL inside a savepoint, reads both runs, checks the full deterministic decision and attributed Configuration block, measures pass/fail coverage from imported rows, and verifies that rolling back restores an existing pilot decision and removes the rule. CI prints a digest of the generated SQL. The selected source SKU already appears in an existing conflict case, so this catalogue-wide rule must not be imported into the shared 36-deal or historical baseline. This is permanent, reproducible **development coverage**, not yet a released dependency distribution. The `compatibility_rules.condition_json` field review mark remains open for safely scoped generated data; schema, calibration, 400 historical outcomes, 36 pilot outcomes and `ready_for_generation=false` are unchanged.
