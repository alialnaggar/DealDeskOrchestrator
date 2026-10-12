> **Status note (11 October 2026):** This is a working plan with dated checkpoints. Its 7 October opening counts are historical; see `../README.md` and `phase1c_release_review.md` for the latest six open field marks, two calibration reviews, and provisional 400-run diagnostics.

# Phase 1C — path to usable synthetic data

**Working plan, 7 October 2026.** The current PostgreSQL reader and decision
tests cover the 24-table design and all 24 proposed build variants, but there
is no generated operational dataset. `ready_for_generation` is still false:
four calibration review items and 22 field-level review marks remain open.
All portfolio identities, prices, costs and operating quantities are
synthetic drafts. This plan keeps that distinction visible through delivery.

## Outcome and scope

The deliverable is a reproducible, versioned synthetic dataset that the six
agents and Orchestrator can read in PostgreSQL, plus a separate hidden
evaluation set with independently authored expected findings. Its initial
targets are 156 products (120 sellable and 36 components), 18 buildable
products with 24 offered BOMs, 80 customers, 400 historical deals and 100
generated test deals. The evaluation-case count is chosen from a scenario
matrix before the final run, not guessed from the 100 test deals. The existing
seed is `22495`. Targets and tolerance decisions remain provisional until
the freeze described below.

"Ready for use" means a clean rebuild from the pinned configuration and
seed, a database import, passing integrity and reader checks, an achieved
distribution report against explicit tolerances, evidence provenance, and
separated evaluation answer keys. It does not mean live supplier commitments,
real customers, or completed six-agent execution. `agent_execution_log` and
other genuine runtime output are written by actual test/agent runs, rather
than fabricated as source facts to fill a table.

## Critical path

| Stage | Work and artifact | Exit check |
| --- | --- | --- |
| 1. Freeze a **pilot contract** | Pin current schema, field ledger, config, seed and data provenance in a run manifest. Write an explicit scenario matrix for stocked, supplier-finished, assembled, digital and service lines; include confirmed, conditional, unknown, revision and policy/credit cases. Define evaluation count and per-scenario minimums. Keep unresolved values tagged `provisional`. | Every generated field has a rule or an explicit open decision; scenario matrix covers each fulfillment path and each material decision state. |
| 2. Build one vertical slice | Implement one deterministic Python generator with separate modules for masters, operational facts, customer history, submissions and evidence. In dependency order: products/BOMs/compatibility and offers; POs/inbound, stock, capacity, digital and shipping evidence; customers, as-of AR and commitments; immutable deals/runs. Load roughly 10–20 varied pilot deals into disposable PostgreSQL, with all five fulfillment paths represented. | Clean import; PK/FK, types, uniqueness and allocation constraints pass; existing readers and deal gate produce evidence-backed outcomes on the pilot. Re-running the same seed produces identical rows and manifest hashes. |
| 3. Calibrate and close evidence **while stage 2 runs** | Source representative component archetypes and comparable dated price configurations, then check cross-kit interfaces, quantities, slots, power and material thermal limits for all 24 BOMs. Reconcile the €1,050 workstation / 31.90% draft margin against the proposed 28% p90. Verify the Olist mirror against its canonical source or exclude its derived rates. Decide how leads beyond the 30-day represented capacity horizon are labeled. Review the 36-component/156-product mix now that structural BOM coverage has passed. Resolve the 22 field marks with tests and evidence, or document bounded synthetic assumptions. | Four calibration items and 22 field marks are dispositioned; no unverified public-derived rate is represented as an enterprise statistic; every offered BOM has a checked compatibility basis and every commercial band has a comparable unit/date/tax basis or an explicitly synthetic label. User reviews the compact decision sheet before final freeze. |
| 4. Stress the pilot and freeze | Generate a larger mixed pilot (about 30–50 deals). Check as-of chronology, stale/absent proof, cancelled or allocated supply, shared material and capacity contention, cost rollups, credit exposure, and decision labels. Produce distribution diagnostics for deal lines, categories, popularity, modes, dates, credit, supply and outcomes. Correct rules or targets, then freeze config, scenario matrix, tolerances and source manifest. | No leakage of expected decisions into input rows; independent answer-key authoring; all material negative cases fail as intended; achieved pilot metrics are within documented pilot tolerances or an approved explicit exception. Both generation validators change to ready only after their real gates pass. |
| 5. Generate and release | Run the frozen generator with seed `22495` for the 80/400/100 targets and the frozen evaluation matrix. Import into a fresh PostgreSQL database, run schema/contract, calibration, relationship, evidence, chronology, replay and distribution checks in CI, then package the data, SQL/load instructions, manifest, checksums and validation report. Keep hidden evaluation inputs and keys outside agent-visible data. | Fresh import and repeat run agree by checksum; all blocking checks pass; achieved distributions and any documented deviations are in the report; agents can read the data and produce real run logs. Tag the dataset version and freeze its configuration. |

Stages 2 and 3 overlap. A provisional pilot is useful for engineering without
turning the draft numbers into final calibration. Stage 5 waits for the stage
3/4 freeze, because changing price, fit or evidence rules afterward would
make the released rows and answer keys inconsistent.

## Work queue and decisions

The implementation work is the generator, provenance manifest, independent
scenario/answer-key builder, PostgreSQL loader, validation report and CI
gate. The review package should contain only the material choices: component
archetype/fit basis, comparable price and cost bands (including the
workstation outlier), treatment of the unverified Olist metric, horizon
labeling, and any target/tolerance revisions. Existing approvals already
settled the synthetic strategy, local workshop model and same-price paired
technical alternatives; these are not being reopened.

At each stage, record the command, seed, commit, row counts, achieved metrics,
failed checks and remaining blockers in this file or a linked run report.
Treat a pilot as **development usable** after stage 2. Treat the dataset as
**evaluation usable** only after stage 5. The evidence review can proceed
in parallel with pilot engineering.

## Progress — 7 October 2026

Stage 1's provisional coverage contract is now executable. The matrix has 18
scenario archetypes across all five fulfillment modes and credit, pricing and
policy conflicts. It specifies one case per archetype for an 18-deal pilot and
two independently reviewed variants per archetype for a 36-case evaluation
target. `validate_phase1c_scenario_matrix.py` checks the seed and baseline
against calibration, coverage, counts, and answer-key isolation. Its manifest
pins hashes of the schema, calibration, field and JSON contracts, portfolio,
cost draft and matrix. These are targets, not generated rows or validated
outcomes. Stage 2's vertical data generator remains the next implementation
step; the four calibration and 22 field reviews remain open.

The first stage 2 master-data increment is `render_phase1c_sellable_catalogue.py`.
It renders 102 additional sellable products from the draft portfolio and
joins the existing 18 buildable products and 36 components in one disposable
PostgreSQL check. Every sellable fulfillment mode is present. Category price
draws use the configured p10/p50/p90 anchors and p50 synthetic cost margins;
these values are provisional and will be regenerated after sourcing review.
This is catalogue coverage, **not** the 18-deal pilot or operational data.
Next: independently generate supplier, stock, capacity, digital, shipping and
credit evidence, then the 18 scenario deals/runs on the 1 September 2026
configuration as-of date and read their results.

The catalogue integration exposed a digital reader mismatch before any pilot
deal was generated: monthly quantities and whole product attributes had been
assumed for every provider pool. The reader now derives concurrent demand for
monthly or annual billable units and compares only the declared digital
configuration identity (edition, tier and features). The provisional
catalogue uses pool-compatible `instance_month`, `protected_tb_month` and
`licence_year` units. Existing monthly reference checks and focused annual
unit tests pass; a connected rich-attribute digital row is still required
in the operational pilot.

## Progress — 8 October 2026

The reader and gate now treat `scheduled_service` as a bounded coverage check:
an explicit eligible region with a future requested date is conditional and
the service slot remains uncommitted; an ineligible region needs revision and
missing coverage needs evidence. There is no service-worker calendar or booked
appointment table, so the pilot must never claim a confirmed service slot.
The `SERVICE-COVERED` matrix bucket was corrected to
`conditional_uncommitted`.

`render_phase1c_vertical_pilot.py` now renders five source-connected
generated-test deals at the configured 1 September as-of date. The five
paths use catalogue rows, confirmed supplier inbound, fresh stock, dated
workshop capacity, a trusted digital provider manifest, explicit service
coverage, shipping and customer credit. It emits source evidence before the
deals and omits expected decisions from submitted rows. The output is a
disposable pilot fixture, not the intended 18-deal varied pilot or the full
dataset. PostgreSQL reader verification is the next gate, followed by the
13 remaining scenario archetypes and distribution checks.

[PostgreSQL Actions run 37770210410](https://github.com/alialnaggar/dealdeskdata/actions/runs/37770210410)
passed the full workflow, including the five generated deal reads and the
service coverage negative cases. The stock and confirmed inbound paths reach
dated delivery; the selected BOM reaches an uncommitted build path; the
separate provider proof confirms the digital term; and explicit service
coverage remains conditional until a slot is committed. The matrix's other
13 conflict cases are still designs, not generated rows.

## Eighteen-case source conflict pilot — 8 October 2026

`render_phase1c_conflict_pilot.py` adds 13 source-connected cases to the five
mode baselines, one for every archetype in the provisional matrix. Each case
has a separate generated-test submission and immutable run; the case-to-run
map stays in test code, outside submitted rows. The examples cover allocated
and stale stock, an uncommitted supplier offer, cancelled inbound, an
alternate BOM kit, stale capacity, a component ETA beyond the represented
capacity window, absent and partial-term digital proof, out-of-region service,
and credit, price and contract-clause exceptions. The partial-term provider
record is stored separately from the deal; a reference string alone never
confirms digital capacity.

[PostgreSQL Actions run 37771255791](https://github.com/alialnaggar/dealdeskdata/actions/runs/37771255791)
passed the full schema/load/reader/compiled-policy workflow with the five
baselines and 13 conflicts. This establishes an **18-deal development pilot**,
not a calibrated distribution or independent evaluation answer key. The
supplier-offer-only case is conditional operationally, but its final gate
needs evidence because a dated delivery commitment is absent. This makes
the matrix's `unknown` target a gate/evidence bucket, not a claim that no
offer exists. No outcome labels are in the agent-visible SQL.

Next: build the seeded 30–50-deal mixed stress pilot with shared capacity and
inventory contention, as-of replay, a provenance manifest and achieved
distribution report. In parallel, disposition the four calibration reviews
and 22 field marks; only then freeze tolerances, independently author the
36-case evaluation oracle, and generate the 80/400/100 release targets.

## Seeded 36-deal stress increment — 8 October 2026

`render_phase1c_stress_pilot.py` adds 18 seeded mixed deals and 47 lines to
the 18-archetype pilot. The added deals have eight two-line, nine three-line
and one four-line submissions; line mode counts are 11 stocked, nine
supplier-finished, nine make-to-order, ten digital and eight scheduled service.
`phase1c_stress_pilot_report.json` records seed `22531`, these achieved input
counts and SHA-256 of the rendered SQL. The added records use later source
snapshots, so the reader can replay earlier baseline decisions at their
original as-of timestamp. At least two runs cite the same stock source,
exposing the current read-only model's cross-deal reservation limit; the
intra-run build quantity cases also exercise capacity shortfall.

[PostgreSQL Actions run 37772292678](https://github.com/alialnaggar/dealdeskdata/actions/runs/37772292678)
passed the 36-deal SQL import, deterministic rendering, reader/gate checks,
as-of isolation and prior workflow. This is a development stress increment,
**not** an achieved calibrated business distribution. The input diagnostic is
versioned beside the generated SQL. A separate database audit now records
aggregate reader decisions and source hashes in a CI artifact: 36 deals,
65 total lines (mean 1.81), with nine `approval_required`, two `blocked`,
12 `needs_commitment`, nine `needs_evidence` and four `needs_revision`.
Five distinct stock evidence IDs appear in more than one read-only run.
[The measured report from run 37772681168](https://github.com/alialnaggar/dealdeskdata/actions/runs/37772681168)
also captures line mode/category counts, as-of counts and SHA-256 of five SQL
inputs plus configuration, matrix and provider manifest. The diagnostic
is separate from deal inputs and expires with GitHub's CI artifact retention;
the code reproduces it from a fresh database. These pilot frequencies are
design-induced and must not be presented as target business rates.

Next: compare pilot metrics with explicit tolerances, resolve the four calibration
and 22 field reviews, and only then freeze the release generator and hidden
independent evaluation cases. Cross-deal allocation needs an explicit
reservation or replay rule before claims of portfolio-wide availability.

## Calibration and field-gate triage — 8 October 2026

The field coverage checker had parsed `TIMESTAMPTZ` as `TIME`; the corrected
parser and ledger now distinguish 18 timestamp-with-zone columns from the
single shipping cutoff `TIME`. The conflict pilot also exposed two invented
workshop locations outside the controlled two-site vocabulary and a West
origin time-zone mismatch. The fixtures now use only Central/West and the
configured Berlin/Amsterdam zones. [PostgreSQL run 37774188041](https://github.com/alialnaggar/dealdeskdata/actions/runs/37774188041)
passed the corrected 36-deal load and reader checks.

Five field review marks with direct executable pilot evidence have been
closed: offered BOM signature coverage, late-component/supplier-offer
classification, stale and horizon-limited capacity, independent digital
full-term proof, and origin-local shipping. The typed generated-row validator
also closes the location mapping, deal requirement, and per-mode line
configuration marks. The explicit horizon rule is
`unknown_no_inferred_production_date`. Product-popularity shape is a declared
synthetic target; no unverified Olist mirror rate is claimed as an enterprise
statistic. [PostgreSQL run 37774640395](https://github.com/alialnaggar/dealdeskdata/actions/runs/37774640395)
passed the updated calibration and 266-column checks. Both generation gates
remain false: **two calibration reviews and 14 field marks** remain. The
[release review sheet](https://drive.google.com/file/d/15w7ayUuyfYJn-cvTLKTgbEnw18Y_RDtf/view)
lists their evidence and closure order. The two calibration choices are the
provisional 36-component/156-product mix and comparable catalogue price
basis; neither is frozen by the pilot.

The validator checks configured locations and origin time zones, supplier
calendars, country/region predicates, requirement keys and types,
evidence-reference metadata, active sellable lines, per-mode configuration,
full-term digital units, and exact active make-to-order BOM signatures. Pure
negative tests cover unknown locations, zone drift, unoffered options,
unresolved or future evidence, expected-decision leakage, bad installation
predicates, and incorrect recurring quantities. The disposable PostgreSQL
workflow passed all 156 products, 36 deals and 65 lines with zero typed-row
errors. Evidence manifest resolution, compatibility dependency coverage,
historical as-of replay, runtime output contracts, distribution calibration,
product fit, and comparable price basis remain open.

`validate_phase1c_evidence_manifests.py` adds the next manifest boundary:
provider records must carry typed evidence metadata and full-term dates;
binding capacity must cover the evaluation as-of; deal references must match
the independent record; and replay snapshots can be verified by SHA-256 and
as-of time. The current vertical and conflict provider manifests pass this
contract. Credit, no-PO inbound and historical AR manifests still need to be
generated and connected before those field marks can close.

`phase1c_pilot_snapshot_manifest.json` now pins the pilot schema, six SQL
inputs, contracts, calibration/scenario configuration, and provider manifests
under `PILOT-OPERATIONS-SNAPSHOT`. Its SHA-256 entries and 1 September 2026
as-of timestamp pass the validator. This makes the development pilot
reproducible; the full historical dataset still needs separate frozen credit,
AR, inbound and snapshot manifests.

`validate_phase1c_runtime_outputs.py` also checks the execution-log boundary:
unique attempts, valid agent/status pairs, outcome-free input snapshots,
typed output envelopes, matching agent identities, and evidence IDs that exist
in the independent manifest. The current dataset has no populated execution
log, so this validator is a gate for the later runtime sample rather than a
release closure.

[PostgreSQL Actions run 37821625969](https://github.com/alialnaggar/dealdeskdata/actions/runs/37821625969)
passed the complete pilot after the provider reader and its reference fixture
were aligned with typed metadata and full-term confirmation dates. The local
suite reports 165 tests, with 35 PostgreSQL-dependent cases run in CI.

The next reader increment requires a complete frozen credit/AR manifest for
historical deals. It matches the run snapshot ID, customer and as-of time;
rejects future invoices/payments and unmatched commitment evidence; and uses
the manifest's historical account status in the policy gate. Nonhistorical
pilot reads retain their existing database path. This is a fail-closed
contract, not generated historical evidence; the credit/AR field marks remain
open until manifests and actual historical rows exist.

The deterministic `render_phase1c_customer_master.py` now emits 80 synthetic
customer and credit rows plus a matching commitment ledger. It allocates the
configured segment, industry, country, risk, status and payment-term counts
exactly, marks three On-Hold customers with synthetic adverse signals, and
uses the configured 1 September as-of time. `test_phase1c_customer_master.py`
checks reproducibility and PostgreSQL constraints/distributions in CI. This
is provisional generated input, not independently sourced historical credit
or AR evidence; no historical deal or field mark is closed by it.

`render_phase1c_historical_inputs.py` now emits eight chronological SQL shards
with **400 provisional historical submission headers and 1,200 sellable lines**.
The configured line-count bins are exact (50/87/135/80/40/6/1/1), mean is
3.0, every one of 120 sellable products appears at least four times, and the
top 24 account for 768 lines (64%). All 80 customers appear. The generator
records no historical decisions, specialist runs, or source evidence; each
header remains an unlabelled Submitted row. PostgreSQL loading and measured
distribution are checked in CI. This is the input skeleton for the frozen
operational/credit/AR snapshot work, not a usable historical training set.

`render_phase1c_historical_credit.py` generates a separate synthetic dated
credit and AR source ledger for the 80 customers, with 400 registered as-of
cutoffs. Eight customer source shards are SHA-256 pinned by the index. The
resolver constructs each complete credit/AR view using only commitment events,
invoices and payments known by that cutoff; all 400 views pass the historical
reader's fail-closed credit validator. The September 1 open-invoice overdue
share is within the configured 18–28% band, and paid/open invoice counts use
the segment bands. These are synthetic dated source records, with no derived
historical decision or full operational snapshot yet. Do not use the current
customer credit/AR tables as historical truth.

`render_phase1c_historical_runs.py` now links the 400 submitted deals to
those registered cutoffs as **queued** baseline runs, with an input/config
hash and no outcome or agent output. The PostgreSQL gate loads the run rows
and reads early, middle and late samples through `read_run` with the dated
resolver. Operational availability, supplier, capacity, digital and shipping
evidence are still missing for these cutoffs; queued reads must not be treated
as completed or correct business decisions.

Historical reads now also require a complete **operational** snapshot resolver.
This closes a replay leak: current inventory, supplier, capacity and digital
tables, plus undated shipping lanes, cannot silently provide facts for an
earlier run. The validator rejects future stock, inbound, PO confirmations,
offers, capacity, digital observations and unverified/future shipping lanes;
confirmed no-PO inbound needs a matching independent supplier proof. A test
with explicitly empty complete evidence remains unknown, while a missing
resolver fails closed. This is a safeguard, not a generated operational
source; actual dated operational snapshots remain to be built.

The first operational source slice now provides **daily aggregate stock for
12 stocked sellables and 36 components**, plus 38 dated standard shipping
lanes and rolling 90-day offers covering 32/36 components and 22/27
supplier-finished SKUs. It is generated independently of submitted deal
choices, SHA-256 pinned, and resolves across all 400 registered cutoffs with
stock at most 24 hours old. Reader integration samples early, middle and
late queued runs. This provisional source has no inbound receipts, production
slots or digital commitments, so those paths must stay conditional/unknown;
it is not the complete release operational distribution.

The next operational slice adds 441 independently generated dated inbound receipt events for 63 products across seven months, with exact-cutoff PO header or supplier proof validation and SHA-256 source digests. All 400 historical operational views now include the relevant dated receipt rows. The reader only counts unexpired confirmed receipts as binding. No historical outcome or execution log is claimed.

## Historical baseline diagnostic checkpoint — 10 October 2026

The independent source now also includes dated workshop capacity, full-term
digital provider evidence and bounded service eligibility. A disposable
PostgreSQL pass reads all 400 queued runs with compiled policy, then rolls
back the imported rows. Its separate diagnostic is provisional and excluded
from agent inputs and independent evaluation. Daily observed credit evidence
and workshop co-located component stock corrected two source mismatches.
The final [PostgreSQL run 38022399576](https://github.com/alialnaggar/dealdeskdata/actions/runs/38022399576)
passes: 200 of 220 make-to-order lines have feasible uncommitted builds;
20 need replenishment. The remaining evidence-gap findings are 71 stale
credit commitments, 238 missing delivery findings, 185 missing digital
confirmations and 52 missing service coverage findings. These overlap.

Next: inspect the remaining gaps by fulfillment mode and source state,
calibrate the 14 open field marks and two review items, then author the
independent answer key and execution evidence. Do not promote these
diagnostic decisions into historical labels or training data yet.

The subsequent per-mode diagnostic found 213 of 238 missing delivery
findings on supplier-finished lines, 20 on make-to-order, and five on
stocked-finished. Of 185 digital findings, 108 had verified capacity and
full-term proof but missed the requested activation date. The gate now
routes those to a date revision; 77 lines without a matching pool remain
evidence gaps. [PostgreSQL run 38024615223](https://github.com/alialnaggar/dealdeskdata/actions/runs/38024615223)
passes with a provisional decision mix of 6 approval routes, 24 blocks,
69 commitments, 142 evidence needs, and 159 revisions. The next source
review should concentrate on supplier receipt/offer coverage and distinguish
intentional unavailable stock from accidental source gaps before calibration.

The supplier review found that 205 of 213 supplier-finished lines lacking
binding delivery had confirmed receipt history whose nine-day proof had
expired. A provisional weekly inbound pipeline now matches the configured
seven-day evidence recheck cadence: 1,764 independently evidenced events
cover 63 SKUs, preserving the configured status proportions. The full
[PostgreSQL run 38042504618](https://github.com/alialnaggar/dealdeskdata/actions/runs/38042504618)
passes. Supplier-finished findings are 159 confirmed by date, 29 late
alternatives, 60 conditional offers and nine infeasible; all-mode missing
delivery findings fell from 238 to 82. This is a source cadence adjustment,
not an outcome target or training label. Review cadence and achieved mix
alongside the remaining field marks before final freeze.

## Field-ledger checkpoint — 10 October 2026

Seven previously open marks now cite the exact passing distribution and
historical replay checks in `phase1c_column_rules.yaml`: customer industry
and country, credit commitment evidence, frozen AR, no-PO inbound proof,
historical product popularity and run snapshot isolation. Seven marks stay
open for product attributes/price/cost, supplier calendars, compatibility
predicates, deal document references and actual agent output. The 24-table,
266-column coverage check passes, while `ready_for_generation` remains false.
The independent 100-test set and 36 evaluation variants are still a separate
generation and review stage; the 400-deal diagnostic cannot act as their
answer key.

The deal document validator now requires a trusted customer-document record
to be issued before submission and scoped to the same deal; a cross-deal
reference fails. The field ledger cites the positive and negative row tests
for this mark. Six marks remain open, and the historical inputs' empty
document lists do not imply that a document was verified.

The compatibility predicate evaluator now honors the declared configured
group for required/excluded product checks. A dependency in another group
cannot satisfy the source group's rule. Full generated compatibility-rule
coverage and detailed product fit remain open.


## Agent-recommendation extension checkpoint — 11 October 2026

Phase 1B now describes evidence-backed options across specialists and Orchestrator coordination. This is a **target behavior**, separate from the current generation/release gates and from the dated checkpoints above. The core structured submission fields are largely sufficient for the first experiment. Keep the 24-table schema; define a typed candidate record with candidate ID, parent deal, exact field changes, evidence/as-of, catalogue/policy/snapshot versions, customer constraints, commitment class, checked specialist results and tradeoff. It is not an implemented runtime type yet.

Run one shortage → allowed partial delivery or offered substitute → complete affected-check rerun → human comparison case. Assert the submitted deal remains immutable; the proposal has no booking or approval side effects; conditional supply stays conditional; group and customer constraints hold; price, fulfillment, credit, policy and routing findings belong to the same candidate; and rerun traces remain auditable. Test separate correlated runs before deciding if a small candidate-identity schema migration is needed. Expand the independent scenario matrix with valid alternatives and safe refusals, then finish the existing product-fit and dated comparable-price/cost evidence reviews. **More generated rows alone cannot establish candidate validity.** Do not mark `ready_for_generation` true or count this design note as an executed agent test.

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

The read-only `phase1c_evaluation_input.py` path and PostgreSQL integration test seal source-only rows for a distinct temporary case; the fixture is rolled back and has no answer key. This checks the packaging boundary before producing frozen cases. It does not count toward 36 independently reviewed evaluation cases, change the 100 generated-test target, or close calibration, field marks or generation readiness. Next: persist a complete frozen case from a reproducible build, isolate reviewer answers, obtain independent review, then score against the same rule-only baseline and candidate system.

## Compatibility dependency coverage check — 12 October 2026

The existing generated-row validator now reports actual non-installation rule application, including no-rule and no-applicable-rule gaps. This makes the `compatibility_rules.condition_json` gate measurable while leaving it open. Next add deliberate dependency pass and conflict rows to the synthetic pilot and verify both the row validator and deterministic deal decision before marking coverage complete. No new dataset label, schema or calibration freeze is implied.
