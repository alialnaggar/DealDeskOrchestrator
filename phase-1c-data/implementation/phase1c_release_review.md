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

## Dependency rule release decision — 12 October 2026

`audit_phase1c_dependency_scope.py` scans the eight deterministic history shards and three pilot inputs (400 + 36 deals, 1,265 lines). If the isolated source-004 → target-005 `requires_product` rule entered `CATALOGUE_2026_V1`, it would add a Configuration block to historical deals 0060, 0121, 0123, 0133 and 0239 and existing pilot `CONFLICT-DEAL-13`. None of those six contains target-005. An exhaustive intersection over all 120 sellable products finds **zero** alternative source/target pairs for which every pre-existing source deal already contains the target. A global V1 dependency would therefore alter at least one prior submission. This is an input-scope finding, not a claim that six full decision statuses have been rerun under the hypothetical rule.

**Exact proposed decision before changing the released data:** retain the 156-row `CATALOGUE_2026_V1` and its 400 historical / 36 pilot results; add an explicitly versioned `CATALOGUE_2026_V2` dependency test slice with two cloned sellable product rows (new immutable IDs, same synthetic specs), the scoped rule and deliberate pass/conflict submissions. That yields 158 product rows across both versions while preserving the 156-product V1 distribution. The generator, JSON contract, source manifest and tests would have to accept and label both versions, and V2 needs dated stock or an explicit unknown fulfillment result. This uses existing version columns and no schema migration. It does change the catalogue-mix assumption and is **proposed, not adopted**; show the V2 rows and exact output impact for review before integration. Importing the rule globally into V1 or making behavior depend on `dataset_type` is not adopted. The `compatibility_rules.condition_json` mark remains open, with no calibration freeze or readiness change.

## Versioned dependency pilot extension — 13 October 2026

Ali continued with the proposed V2 slice. `render_phase1c_dependency_pilot.py` now pins two V2 clones of stocked V1 products, a V2-only `requires_product` rule, dated V2 inventory and two submitted V2 inputs (required add-on present/absent). The generator writes `phase1c_dependency_pilot.sql`; the pilot snapshot manifest hashes it and the data contract lists exactly the two V2 product IDs, two V2 deal IDs and rule. The typed row validator rejects unlisted versions and mixed-version lines. CI imports the V2 extension after the existing 36 deals and checks 158 product rows across versions, 38 development deals, one applicable dependency pass and one fail. The reader/full deterministic decision test checks the attributed Configuration block and a V1 comparison. The base V1 catalogue still has 156 rows and the 400 historical input deals are unchanged; the 36 existing pilot cases retain their outcomes. This is generated **pilot** coverage, not the 100-test release or independent evaluation. The `compatibility_rules.condition_json` field mark remains open until the final generated set and scope manifest are reviewed. No 24-table schema, prices, costs, thresholds or generation-readiness flag were frozen.

## Supplier calendar offer evidence — 13 October 2026

The row checker now links each imported supplier offer to its supplier's typed calendar and reports offer coverage; the PostgreSQL CI gate requires no missing calendar on the current development rows. For a supplier-finished line without a shipping option, the reader can calculate an **indicative, nonbinding** min/mode/max workday window from the selected offer and the supplier's local weekdays. It records the offer and supplier IDs, leaves an absent or untyped calendar without an estimated date, and does not turn the offer into a confirmed receipt or a delivery promise. A PostgreSQL reference test checks a four-day supplier week across a weekend, the unchanged conditional status and lack of binding supply. Confirmed inbound continues to rely on its own dated evidence.

This covers the connected development offer path. The 400 historical operational snapshots contain offer lead-day evidence without a supplier calendar link, so their dates are not inferred. The final 100 generated cases and source-specific offer/receipt review are still needed before resolving the `suppliers.order_calendar_json` field mark. Six field marks, two calibration reviews and `ready_for_generation=false` remain open; no schema or calibration values changed.

## Provisional 100-case allocation — 13 October 2026

The existing scenario matrix now allocates the separate generated-test target without reusing the 36-deal development pilot or the held-out evaluation IDs: five slots for each of 18 archetypes (90), eight extra edge-case slots, and two V2 dependency pass/conflict slots (100 total). The matrix validator checks the count, unique `GEN-TEST-` IDs, declared archetypes, V2 scope and source-only plan shape; its pinned pilot manifest records the changed matrix hash. The allocation now renders 100 distinct provisional submitted deal rows and 101 lines with pinned source hashes and a repeatable SQL digest. It uses 18 V1 and two V2 development source states; each V1 archetype varies the quoted price across bounded deterministic steps. CI imports the batch in a rollback-only PostgreSQL transaction, validates all 138 development deals and 169 lines together, reads each of the 100 runs, checks full deterministic decisions, and verifies the two V2 dependency findings. This is an import and rule-coverage batch, **not a release-quality 100-case distribution**: customers and operational evidence are reused, achieved category and outcome distributions remain to be reviewed, and no independent answer key or held-out evaluation case is created. Next diversify and date source evidence, measure distributions, and review calibration before any freeze. Six field marks, two calibration reviews and `ready_for_generation=false` remain open.

## Measured 100-case development diagnostic — 13 October 2026

The PostgreSQL workflow now saves `phase1c-generated-test-diagnostic` after reading all 100 provisional submissions with compiled policy rows. Aggregate deterministic gate counts are **18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision**. These are observed development decisions, never independent expected answers or approvals. The 101 lines cover 36 stocked, 21 make-to-order, 17 supplier-finished, 16 digital and 11 service modes. Only 18 customer IDs and 20 development source templates support the batch; Availability findings cite 28 distinct source IDs, with some reused across many cases. This proves import and rule-path breadth but exposes limited customer and operational diversity. Next generate independent dated source states and customer variation, rerun the same aggregate audit, and review achieved distributions before release. The separate 36 evaluation answers remain 0 independently reviewed; six field marks, two calibration reviews and `ready_for_generation=false` remain open.

## Customer source variation in generated tests — 13 October 2026

The deterministic 100-case renderer now hashes and selects from the existing 80-customer synthetic master. The selected 37 profiles are Active, Low/Medium risk, and have more than €150,000 credit-limit headroom after dated unbilled commitments. It rotates 63 non-reference, non-credit-limit V1 variants through them; original reference, credit-limit and three early-run customer contexts, all 36 pilot submissions and 400 historical inputs remain intact. The PostgreSQL batch loads the customer master in its rollback-only transaction and reads the 100 deals through the full deterministic gate. Buyer country and requested shipping destination can differ. This is a bounded development variation; the operational snapshots still reuse 20 source states and it creates no oracle labels. The passing PostgreSQL push workflow measured 55 distinct customers versus 18 before this change. Aggregate decision counts remained 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision; this does not prove every individual finding was unchanged. The 28 distinct attributed Availability source IDs did not increase. The achieved distribution needs review before the test set can be released. Six field marks, two calibration reviews, 0/36 independently reviewed evaluation answers and `ready_for_generation=false` remain.

## Bounded dated inventory observations — 13 October 2026

The generated-test renderer now appends five distinct inventory observations for the STOCK-READY product and location, with quantities 3, 4, 2, 5 and 3 at 12:05–12:45 UTC. Their five run cutoffs are 12:10–12:50. A first PostgreSQL trial exposed the existing stress-pilot row at 13:00: a generated 13:00 run selected it, so the cutoffs were corrected to remain earlier. The passing rollback-only regression now checks all five selected inventory IDs, the original pilot's unchanged 12:00 source, the row validator and the full deterministic decision. The push PostgreSQL workflow passed for the corrected commit. The measured diagnostic has 33 distinct attributed Availability source IDs (previously 28), 55 distinct customers and unchanged aggregate decision counts: 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence, 17 needs_revision. No case-level answer key is inferred from those counts. The 20 source deal templates and nearly all other operational observations are reused; this is a bounded development slice, not the final 100-case distribution. No V1 rule, historical input, 36-pilot outcome, schema or calibration value was changed. Six field marks, two calibration reviews, 0/36 independently reviewed answers and `ready_for_generation=false` remain.

## Dated make-to-order component stock — 13 October 2026

The 100-case renderer adds five later compute-component inventory observations for repeated BUILD-READY cases, with quantities 2, 3, 2, 4 and 2. The selected timestamps (12:05–12:45 UTC) and run cutoffs (12:10–12:50) preserve the original pilot's 12:00 read and precede the existing 13:00 stress observation for that component. The rollback-only PostgreSQL regression verifies each generated build cites its own inventory ID in Availability findings, checks its full deterministic decision and confirms the original build still cites PILOT-STOCK-002. The corrected code's push workflow passed. The aggregate diagnostic moved from 33 to 38 distinct Availability source IDs; customer count remains 55 and aggregate statuses remain 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision. These counts cannot establish case-by-case agreement or an independent answer key. The 20 source deal templates and other fulfillment evidence remain largely reused. The historical inputs, 36-deal development pilot, V1 catalogue, schema and calibration values were not edited. Six field review marks, two calibration reviews, 0/36 independently reviewed evaluation answers and `ready_for_generation=false` remain.

## Archetype-level achieved coverage — 13 October 2026

The existing `phase1c-generated-test-diagnostic` artifact now groups reader/full-decision observations for all 20 declared archetypes, without adding agent-visible answer keys. For each group it records deal count, observed decision and line fulfillment status counts, distinct customers and distinct source IDs attributed in Availability findings. PostgreSQL validates that all 100 cases and all 20 groups are accounted for; push and PR checks passed. All 18 repeated V1 groups (five or six deals each) show exactly one observed final status per group; the two V2 dependency groups are singletons. This does not establish case-level correctness and does not mean varied statuses are mandatory within a deliberately defined archetype. It does show how strongly the repeated inputs preserve their template outcome. The six SUPPLY-CONFIRMED submissions cite one Availability finding source ID and six customer IDs; DIGITAL-PROVED, DIGITAL-NO-PROOF, DIGITAL-EXPIRED and SERVICE-COVERED likewise cite one finding source ID per group. Zero attributed Availability IDs on several infeasible/unknown groups must not be read as an absence of all raw evidence. Next inspect and diversify dated supplier, digital and service evidence and review the individual findings before release. Six field marks, two calibration reviews, 0/36 independently reviewed evaluation answers and `ready_for_generation=false` remain.

## Dated generated-test supplier receipt slice — 13 October 2026

The reproducible 100-case renderer now adds five synthetic, dated confirmed purchase orders and inbound receipts for repeated SUPPLY-CONFIRMED cases. The original 12:00 supplier pilot and 14:00 stress runs cannot see the 14:05–14:45 confirmations; the five generated runs at 14:10–14:50 need successively more receipt quantity (three through seven requested units, counting the original two-unit receipt). The PostgreSQL push workflow checked source-only reproduction, row contract, reader visibility and Availability attribution, and each complete deterministic decision. Its diagnostic reports six distinct Availability source IDs for the six SUPPLY-CONFIRMED submissions (previously one) and 43 across the batch (previously 38). The 55-customer count and aggregate status counts remain 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision. This is measured development behavior, not case-level correctness or an independent answer key. The new evidence references are deliberately synthetic placeholders and still need source-specific field review; they are not independent supplier proof or delivery commitments. The 20 deal source templates, 400 historical inputs, 36 pilot submissions, schema and calibration values were not edited. Six field review marks, two calibration reviews, 0/36 independently reviewed evaluation answers and `ready_for_generation=false` remain. Next inspect individual source and finding variety in digital and service cases, then complete field/calibration review and a separate held-out evaluation set before a release decision.

## Dated digital capacity slice — 13 October 2026

The reproducible 100-case renderer now appends four provider-capacity observations for repeated DIGITAL-PROVED cases, with distinct IDs, capacity totals of 11–14 and timestamps after the existing 14:00 stress cutoff. The reference case retains its 12:00 source. The PostgreSQL reader and full deterministic decision test checks all five selected IDs, the old pilot and stress visibility boundaries, and that provider references alone do not validate full-term proof. The source-only render and row validation checks passed. Availability findings now cite five distinct IDs within DIGITAL-PROVED (previously one), and 47 across the batch (previously 43); all five digital cases still report needs_evidence. The 55 customer IDs and aggregate statuses remain 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision. These are observed development decisions, not independent labels or activation promises. The synthetic provider references need source-specific validation; service coverage remains a common regional rule without a committed slot. Continue case-level source and finding review, especially service evidence, while completing field marks, calibration reviews and the separate 36-case evaluation. The schema and calibration values were not changed; six field marks, two reviews, 0/36 answers and `ready_for_generation=false` remain.

## Case-level generated-test review output — 13 October 2026

CI now saves a second, per-case artifact `phase1c-generated-case-review` from the same rollback-only PostgreSQL read of the provisional 100 submissions. Every record states the case ID and archetype, run cutoff, selected customer, modes, observed deterministic status, fulfillment statuses and IDs cited in Availability findings. It separately lists reader-visible raw inventory, inbound and digital IDs, service coverage rule IDs, and applicable compatibility rule pass/fail observations. The artifact summarizes source reuse and identifies cases with no attributed Availability ID; that condition does not imply the absence of raw evidence. The integration test verifies 100 unique cases and reconciles attributed IDs with the aggregate diagnostic. The push workflow passed. These observations contain no independently reviewed expected answer; each case is explicitly pending independent review and the artifact is a development review queue, not a frozen evaluation set. Next inspect case-level evidence provenance and the service-slot gap with field reviewers, then decide what source variation and answer review are sufficient for release. Six field marks, two calibration reviews, 0/36 independently reviewed evaluation answers and `ready_for_generation=false` remain unchanged.

## Measured service commitment and no-attribution queue — 13 October 2026

The passing PostgreSQL case-review summary reports 100 cases, 22 without an Availability finding source ID, and source reuse led by `BOM-001` in 11 cases. The 22 require individual inspection of their reader-visible raw rows and finding reasons; no attributed ID alone cannot establish absent evidence or a wrong decision. Eleven scheduled-service lines divide into five regionally eligible and six ineligible; none has a committed appointment slot. The five SERVICE-COVERED generated cases continue to yield needs_commitment under the full deterministic gate. The single shared coverage rule is an eligibility rule, not a reservation, so duplicating it or asserting a synthetic booking would misstate the evidence.

**Decision retained for this development set:** leave service appointments uncommitted and eligible cases conditional. Before proposing a schema change, the field review must specify who confirms a slot; the service product, location, dated time window and resource/capacity that the commitment covers; a unique source reference, confirmation timestamp and expiry; and how a verifier can reject stale, conflicting or withdrawn proof. Then show the exact 24-table contract change, effect on the 36 pilot and 400 historical cutoffs, reader behavior, and test cases for Ali's review. No schema or calibration change is made here. The 100-case batch remains provisional, all independent case reviews pending, six field marks and two calibration reviews open, 0/36 held-out answers reviewed, and `ready_for_generation=false`.

The 22 no-attribution cases break down exactly as STOCK-ALLOCATED (6), STOCK-STALE (5), SUPPLY-CANCELLED (5) and SUPPLY-OFFER-ONLY (6). In the current deterministic assembler, physical Availability `source_ids` come from shipping options. A zero-free-stock row, stale stock, cancelled receipt or uncommitted offer can be visible to the reader yet yield no supported option and hence no attributed option ID. This is a traceability and case-review distinction, not evidence that 22 source records are absent. Inspect the raw rows and status reasons case by case; do not fabricate binding supply merely to raise the ID count. A separate reason-evidence trace can be considered after reviewing the negative cases, without changing their decisions.

## 14 October 2026 — batch release review and exact decisions proposed

The 100-case PostgreSQL packet was audited across all 100 observations using its source and status fields. It contains 100 cases/101 lines, 55 customer IDs, 20 source deal templates and 47 Availability-attributed IDs. Nineteen of those IDs occur in one case; 67 cases share at least one attributed ID with another case. The 22 cases with no shipping-option attribution are the allocated-stock, stale-stock, cancelled-supply and offer-only negative groups; their raw rows and reasons must not be mistaken for missing positive supply. All 18 repeated V1 archetypes have one observed final status within each group, so this batch supports rule regression coverage rather than an independent outcome-frequency estimate. These are observed development facts, not reviewed answers.

The generated DIGITAL-PROVED label revealed a real coverage gap: its five cases had no trusted provider resolver and were observed as needs_evidence, despite the matrix requiring full-term proof. The proposed batch renders a separate, SHA-256-pinned synthetic provider manifest from the controlled pilot proof and four later dated snapshots. The rollback-only generated-batch test supplies that manifest to the reader to validate exact pool identity, quantity, term and dates, and to reject the no-proof and expired-proof cases. The manifest is a synthetic development source outside salesperson input, not an independently verified external provider commitment. Both push and PR PostgreSQL workflows passed. All five matching cases now have full-term verified proof and move from needs_evidence to approval_required; no-proof and partial-term cases remain unverified. The observed distribution is 23 approval_required, 12 blocked, 11 needs_commitment, 37 needs_evidence and 17 needs_revision. The earlier 18/12/11/42/17 counts are the pre-proof diagnostic, not a frozen target.

| Open mark / review | Evidence in hand | Exact proposed decision before freeze |
| --- | --- | --- |
| `products.attributes_json`; component/product mix | All 36 fictional component specifications are checked across 24 offered BOMs and 25 selections. | Accept internally consistent fictional fit for the bounded Option A scope, explicitly without manufacturer certification; reviewer signs off the 36/156 mix. |
| `products.list_price`, `products.standard_cost`; price calibration | All 120 sellable rows audited. The 102 generated costs sit near category p50; the read-only spread would move 31 baseline 10%-discount line states and create two nonpositive margins. | Retain fixed-p50 costs for the first regression dataset and label the unachieved p90 spread as a synthetic simplification, unless Ali chooses the separately tested spread. Do not claim market comparability. Recheck units, dates, tax basis and the €1,050 workstation. |
| `suppliers.order_calendar_json` | Typed calendars and connected development offers pass the row gate; historical offers without calendars have no inferred delivery date. | Accept calendar-derived offer windows only as nonbinding when a typed calendar is present; keep missing historical windows unknown. Review final generated offer/receipt provenance. |
| `compatibility_rules.condition_json` | A V2-only dependency rule gives one generated pass and one conflict; a global V1 rule would alter five historical and one pilot submissions. | Keep the rule V2-only; review the final 100-case scope and attributed pass/fail before closing the mark. |
| `agent_execution_log.output_json` | No six-agent runtime has been executed; the typed validator exists. | Leave runtime output unpopulated and open. Decide explicitly whether a source-data release can be tagged separately from later agent-run evaluation; never fabricate logs. |

**Proposed 100-case scope decision:** call the set a reproducible rule-regression dataset with bounded source reuse, not an independent statistical sample or an evaluation answer key. Review its per-case raw and attributed evidence, five fulfillment modes, V2 pass/conflict and achieved statuses after the provider-proof correction. If independent operational diversity is required for this target, generate new dated source states before a freeze. The separate 36 evaluation cases remain 0/36 independently answered. None of the proposals above closes a review mark, freezes calibration or changes `ready_for_generation=false`; Ali can review them as one decision batch.


## 14 October 2026 — generated case source audit and evaluation isolation

The post-proof 100-case CI packet was grouped by archetype and source type. The five DIGITAL-PROVED reads are full-term verified and cite five distinct digital-capacity IDs; six DIGITAL-NO-PROOF and five DIGITAL-EXPIRED reads remain unverified binding candidates with one reused capacity ID per group. V2's single dependency pass and conflict have attributed pass/fail results. The 22 negative stock/supply cases with no Availability shipping-option ID still have raw stock/receipt rows where applicable. SERVICE-COVERED has five eligible regions but no committed slot. This inspection supports rule-regression coverage; it does not make repeated source states independent or supply expected answers.

Evaluation-input preparation now rejects overlap with a caller-supplied development source-ID set for inventory, inbound, production capacity and digital capacity, in addition to deal identity. The source-only test checks each mode, and CI runs it. This is an input isolation safeguard; the caller still must enumerate **all** development IDs and inspect source provenance and case similarity. It does not create any of the 36 held-out inputs or review any answer. Field marks, calibration choices and `ready_for_generation=false` remain open.


## 14 October 2026 — development source registry before held-out authoring

The PostgreSQL generated-batch check now produces a SHA-256-sealed registry of reader-selected inventory, inbound, production-capacity and digital-capacity IDs across 154 development runs on 152 deals (16 reference runs on 14 deals, 36 pilot, two V2 dependency, 100 generated). It checks the run and distinct-deal scope and nonempty coverage per source type, and CI uploads the registry. The evaluation packet helper validates its seal and count before using the union to reject source-ID overlap. This removes reliance on an ad hoc list of two physical IDs. The registry contains no answer fields and excludes historical sources and shared context; it cannot certify unique scenarios merely from IDs. Review provenance and construct 36 distinct frozen cases next. Six marks, two calibration reviews, 0/36 independent answers and `ready_for_generation=false` remain open.

The passing PR run measured **49** selected inventory IDs, **12** inbound IDs, **14** production-capacity IDs and **10** digital-capacity IDs. Its sealed JSON is now pinned in `implementation/phase1c_development_source_exclusions.json`; the rollback-only test compares each new render with that file. This is a reproducible exclusion baseline for authoring, not a release or independent oracle.
