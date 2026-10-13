# Phase 1C — synthetic data and implementation

**Status: provisional, 11 October 2026.** This directory is the project copy of
`alialnaggar/dealdeskdata` branch `phase1c-reader-draft` at commit
`8bb6117ba24a4e8e0b7d20a70aca670f0edbb08a`. The implementation files
retain their original relative paths. The migration passed the private PostgreSQL workflow; edit this repository
for all new Phase 1C work. The old repository is a historical portfolio copy.

## How to navigate these files — 12 October 2026

The implementation folder has 175 tracked files. These are grouped by job, not 175 independent features:

| Start here | What it does | Keep for release? |
| --- | --- | --- |
| `schema.sql`, `calibration_config.yaml`, `phase1c_data_contract.yaml`, `phase1c_scenario_matrix.yaml` | Define tables, synthetic assumptions and coverage targets | Yes; review before freeze |
| `phase1c_reader.py`, `phase1c_deal_decision.py`, policy/compatibility helpers | Read dated evidence and compute deterministic findings | Yes |
| `render_*.py`, `phase1c_*source*.json`, `phase1c_*inputs*.sql`, portfolio/customer files | Generate and hold provisional synthetic masters, deals and dated evidence; the numbered files are manageable shards of one dataset | Yes until a reproducible release package replaces drafts |
| `validate_*.py`, `audit_*.py`, `test_*.py`, `phase1c_*fixtures.sql` | Check row relationships, distribution, evidence and regressions | Yes as quality gates; fixtures are development cases, not evaluation labels |
| `phase1c_candidate*.py`, `phase1c_partial_discovery.py`, `phase1c_evaluation_input.py`, `../evaluation/` | Bounded option and evaluation preparation experiments | Keep separately identifiable; these are not final generated data or six live agents |
| `phase1c_release_review.md`, `phase1c_data_readiness_plan.md`, `../calibration-decision-sheet.md` | Current evidence, work order and decisions awaiting review | Yes as provenance; their dated sections are a history, not separate current plans |

**Current finish line for finalized Phase 1C data:** the 80 customer masters and
400 historical submissions exist as provisional synthetic inputs, and a
36-deal pilot passes. Next (1) resolve six field marks and two calibration
reviews with evidence or explicit bounded synthetic assumptions; (2) freeze
the config, source manifest and tolerances after pilot diagnostics; (3)
generate and validate the unfinished 100 test deals and a separate 36-case
evaluation input set with independently reviewed answers; (4) rebuild from
the pinned seed into clean PostgreSQL twice, compare checksums and pass all
integrity, chronology, source and distribution checks before tagging a
dataset release. The 400 diagnostic decisions are not labels. No evaluation
case has an independently reviewed answer (0/36). The generation readiness
flag is false.

Candidate discovery and evaluation packet preparation are useful for the
later system, but should not displace the data gates above. Keep Phase 1A
literature and Phase 1B target agent architecture in their own directories.

## What exists

- PostgreSQL Schema V2: 24 tables. `implementation/schema.sql` is the DDL.
- Fourteen reference scenarios: `implementation/phase1c_row_fixtures.sql`,
  smoke checks and reader/decision tests.
- A deterministic read and decision layer with as-of evidence selection.
- A 36-deal development pilot, 80 customer masters, and 400 historical
  submissions with 1,200 lines, plus dated stock, inbound, capacity,
  digital-provider, shipping, credit and receivables sources.
- The 400 historical outcomes are **provisional diagnostics**. They are not
  expected answers or training labels. Runtime specialist logs are not fabricated.

## First reader-backed candidate experiment — 11 October 2026

`implementation/phase1c_candidate.py` defines a typed proposal whose original
customer requested date stays in the submitted deal. Its separate delivery
slices state proposed quantities and dates. `read_run(..., candidate=...)`
uses the same frozen source selection as the original run, checks cumulative
slice quantities against dated binding stock/receipt options at one location,
and fingerprints the deal, lines, rules and selected evidence it actually
used. `verify_run_correlation` compares those source inputs and the
candidate assessment, without requiring a different deal ID.
`compare_for_human` assembles original and candidate deterministic decisions.
The PostgreSQL test uses a 10-unit shortage: eight units supported by the
original date and two supported later by a confirmed receipt. It checks that
the submitted date and rows remain unchanged, the candidate's original-date
constraint stays unmet, and normal approval routing remains withheld pending
customer acceptance. No source is reserved and no agent log is fabricated.

The negative path now withholds a proposed schedule whose later slice lacks\ndated binding supply, and the human comparison says no validated option exists.\nThe original customer date must appear among unmet constraints.\n\n`implementation/phase1c_candidate_trace.py` now exports an exclusive-create
JSON sidecar. `replay_exported_trace` reads PostgreSQL again before comparing the saved record, so a changed source fact or swapped candidate fails verification. It can correlate the
candidate and six deterministic results without another deal ID. The file is
a prototype, not durable immutable audit storage; see the release review.

`implementation/phase1c_candidate_batch.py` now compares two independently
checked options on the same frozen source view, with separate IDs and trace
records and no automatic selection. One deliberately unsupported schedule
remains unverified. See the release review for limits.

This is a **bounded, deterministic, reader-backed partial-delivery recheck**,
not the six-agent runtime, substitute search, persisted candidate audit or
independent alternative-quality evaluation. The separate typed contract
tests remain in CI. See the [release review](implementation/phase1c_release_review.md#reader-backed-candidate-experiment--11-october-2026).

## Still open

**Expanded Phase 1B design:** The structured input and 24-table schema cover the core deal facts, but candidate identity, validated proposal outputs, source quality and complete alternatives have not been implemented or independently evaluated. Keep the schema for a first shortage → permitted partial delivery or substitute → full recheck experiment, with a typed candidate record and explicit trace. Then decide whether separate runs can auditably correlate candidates or a small schema migration is needed. Expand the scenario set and close product-fit and comparable price/cost reviews; additional rows alone do not resolve those gaps. See [data strategy Section 19](design/data-strategy.md#19-structured-input-recommendation-extension--11-october-2026-target-design) and the [Phase 1B design](../phase-1b-agent-architecture/agent-architecture-and-deal-flow.md).


The six field marks cover product attributes, list price, standard cost,
supplier calendars, compatibility predicates and actual agent output.

Ali selected the bounded synthetic calibration scope on 12 October 2026.
The companion fit draft now covers all 36 components and checks the 24 active
BOMs (25 component selections). The declared specifications are now in the draft component catalogue
attributes and checked against the pinned companion file. Internal synthetic
fit passes, while field-level review and price/cost evidence remain open.
The [calibration decision sheet](calibration-decision-sheet.md) now quantifies
all 24 BOMs' missing detailed fit attributes and the draft buildable margins;
its p90 comparison is a distribution target, not a per-product hard limit.
The 100 generated tests and separate 36-case evaluation set with independently
reviewed expected findings remain to be completed. `ready_for_generation`
remains false. See `calibration-decision-sheet.md` for the selected scope
and `implementation/phase1c_release_review.md` for the dated
evidence and `implementation/phase1c_data_readiness_plan.md` for the work order.

The full provisional price audit now covers all 120 sellable products.
The 102 generated non-buildable costs derive almost exactly from the proposed
category p50 margin, so the nine achieved p90 margins sit below their proposed
p90 targets. This is a generator property, not market evidence. The
[decision sheet](calibration-decision-sheet.md) records the exact choice to
review before calibration freeze; neither price comparability nor generation
readiness is closed.

A read-only bounded margin experiment now compares the current fixed-p50
costs with a seeded synthetic spread for the 102 generated catalogue rows.
At a hypothetical 10% discount, 12 current rows and 41 experimental rows
would fall below their baseline category floor; two experimental rows have
nonpositive margin. This is line arithmetic, not a full deal result. The
[decision sheet](calibration-decision-sheet.md) records the evidence and
the choice to review before any calibration freeze. The catalogue and
generation readiness are unchanged.

The bounded margin report now compares all three configured policy profiles
at 0%, 10% and 20% discounts. Under strict rules at 10%, 39 individual
product statuses change despite a below-floor total of 55 versus 56. See
the [decision sheet](calibration-decision-sheet.md) for the nine-case
arithmetic table and the still-open adoption decision. This is not a
complete specialist rerun.

[Evaluation authoring examples](evaluation/README.md) now show the boundary
between system-visible facts and provisional reviewer findings for one
supported and one unsupported partial-delivery proposal. They are
development examples, not held-out labels: **0 of 36** evaluation cases
have independently reviewed answers, and the 100 generated tests remain
unfinished.

The [evaluation development pack](evaluation/README.md) now includes a
PostgreSQL-backed scoring trial: it checks the original rule-only deal and
two reader-backed candidate traces against a separate, provisional draft.
The trial reuses a regression fixture and has no independently accepted
answer. It does not increase the **0/36** reviewed evaluation count.

## Document precedence

`design/data-strategy.md` records the thesis methodology and earlier decisions.
Its dated status passages are historical. The implementation, executable
contracts, and release review above determine current technical status.
The Drive copies are reference history after this migration. Phase 1A and
Phase 1B remain in their own top-level directories.

## Reproduce

The repository workflow `.github/workflows/phase1c-postgres.yml` runs the
PostgreSQL checks from `phase-1c-data/implementation`. Do not promote pilot
diagnostics to labels without the independent calibration and evaluation gate.

## Bounded proposal discovery from reader facts — 12 October 2026

`implementation/phase1c_partial_discovery.py` forms one deterministic partial-delivery proposal for a single ungrouped finished-product line when the customer permits partial delivery. It uses the reader-selected shipping options, keeps the customer's requested date in the submitted record, and requires a distinct dated binding source for the later quantity at the same location. It then re-reads the run and requires the existing six-check candidate comparison to support the option. Missing permission, no complete later supply or changed source facts yield no review option. No stock is reserved and customer acceptance remains pending. This is a development capability, not a live proposing agent or a held-out evaluation result; generation readiness, calibration and schema are unchanged.

The separate evaluation-input preparation trial is documented in [evaluation/README.md](evaluation/README.md). It proves a distinct database case can be packaged without derived findings, but has no durable frozen case or independent answer. The reviewed count remains **0/36**; generation readiness remains false.

The row validator now reports whether a configured product-dependency or attribute rule actually applies to a generated deal, with pass/fail/not-applicable counts. This exposes a remaining compatibility coverage gap without promoting draft data to ready. See the release review.

A temporary PostgreSQL dependency trial now verifies a required add-on passes when present and blocks when missing; it does not add permanent generated cases or close the compatibility review mark. See the release review.

## Reproducible dependency pair — 12 October 2026

`implementation/render_phase1c_dependency_pilot.py` deterministically creates two submitted synthetic inputs using the current catalogue: one includes a required add-on, and the other omits it. The PostgreSQL regression loads the generated SQL inside a savepoint, reads both runs, checks the full deterministic decision and attributed Configuration block, measures pass/fail coverage from imported rows, and verifies that rolling back restores an existing pilot decision and removes the rule. CI prints a digest of the generated SQL. The selected source SKU already appears in an existing conflict case, so this catalogue-wide rule must not be imported into the shared 36-deal or historical baseline. This is permanent, reproducible **development coverage**, not yet a released dependency distribution. The `compatibility_rules.condition_json` field review mark remains open for safely scoped generated data; schema, calibration, 400 historical outcomes, 36 pilot outcomes and `ready_for_generation=false` are unchanged.

## Dependency release scope audit — 12 October 2026

A repeatable audit of the checked-in 400 historical and 36 pilot submissions found that the trial `requires_product` rule would add a Configuration block to five historical deals and one pilot deal. Across all 120 sellable products, no source/target pair is present together in every existing deal containing the source, so merely choosing another pair cannot preserve the current baseline. CI saves the exact affected IDs. The isolated pair remains development coverage; see the release review for the versioned-catalogue decision before importing any dependency rule. Six field marks, two calibration reviews and `ready_for_generation=false` remain unchanged.

## Versioned dependency pilot extension — 13 October 2026

Ali continued with the proposed V2 slice. `render_phase1c_dependency_pilot.py` now pins two V2 clones of stocked V1 products, a V2-only `requires_product` rule, dated V2 inventory and two submitted V2 inputs (required add-on present/absent). The generator writes `phase1c_dependency_pilot.sql`; the pilot snapshot manifest hashes it and the data contract lists exactly the two V2 product IDs, two V2 deal IDs and rule. The typed row validator rejects unlisted versions and mixed-version lines. CI imports the V2 extension after the existing 36 deals and checks 158 product rows across versions, 38 development deals, one applicable dependency pass and one fail. The reader/full deterministic decision test checks the attributed Configuration block and a V1 comparison. The base V1 catalogue still has 156 rows and the 400 historical input deals are unchanged; the 36 existing pilot cases retain their outcomes. This is generated **pilot** coverage, not the 100-test release or independent evaluation. The `compatibility_rules.condition_json` field mark remains open until the final generated set and scope manifest are reviewed. No 24-table schema, prices, costs, thresholds or generation-readiness flag were frozen.

## Supplier calendar offer evidence — 13 October 2026

The row checker now links each imported supplier offer to its supplier's typed calendar and reports offer coverage; the PostgreSQL CI gate requires no missing calendar on the current development rows. For a supplier-finished line without a shipping option, the reader can calculate an **indicative, nonbinding** min/mode/max workday window from the selected offer and the supplier's local weekdays. It records the offer and supplier IDs, leaves an absent or untyped calendar without an estimated date, and does not turn the offer into a confirmed receipt or a delivery promise. A PostgreSQL reference test checks a four-day supplier week across a weekend, the unchanged conditional status and lack of binding supply. Confirmed inbound continues to rely on its own dated evidence.

This covers the connected development offer path. The 400 historical operational snapshots contain offer lead-day evidence without a supplier calendar link, so their dates are not inferred. The final 100 generated cases and source-specific offer/receipt review are still needed before resolving the `suppliers.order_calendar_json` field mark. Six field marks, two calibration reviews and `ready_for_generation=false` remain open; no schema or calibration values changed.

## Provisional 100-case allocation — 13 October 2026

The existing scenario matrix now allocates the separate generated-test target without reusing the 36-deal development pilot or the held-out evaluation IDs: five slots for each of 18 archetypes (90), eight extra edge-case slots, and two V2 dependency pass/conflict slots (100 total). The matrix validator checks the count, unique `GEN-TEST-` IDs, declared archetypes, V2 scope and source-only plan shape; its pinned pilot manifest records the changed matrix hash. The allocation now renders 100 distinct provisional submitted deal rows and 101 lines with pinned source hashes and a repeatable SQL digest. It uses 18 V1 and two V2 development source states; each V1 archetype varies the quoted price across bounded deterministic steps. CI imports the batch in a rollback-only PostgreSQL transaction, validates all 138 development deals and 169 lines together, reads each of the 100 runs, checks full deterministic decisions, and verifies the two V2 dependency findings. This is an import and rule-coverage batch, **not a release-quality 100-case distribution**: customers and operational evidence are reused, achieved category and outcome distributions remain to be reviewed, and no independent answer key or held-out evaluation case is created. Next diversify and date source evidence, measure distributions, and review calibration before any freeze. Six field marks, two calibration reviews and `ready_for_generation=false` remain open.

## Measured 100-case development diagnostic — 13 October 2026

The PostgreSQL workflow now saves `phase1c-generated-test-diagnostic` after reading all 100 provisional submissions with compiled policy rows. Aggregate deterministic gate counts are **18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision**. These are observed development decisions, never independent expected answers or approvals. The 101 lines cover 36 stocked, 21 make-to-order, 17 supplier-finished, 16 digital and 11 service modes. Only 18 customer IDs and 20 development source templates support the batch; Availability findings cite 28 distinct source IDs, with some reused across many cases. This proves import and rule-path breadth but exposes limited customer and operational diversity. Next generate independent dated source states and customer variation, rerun the same aggregate audit, and review achieved distributions before release. The separate 36 evaluation answers remain 0 independently reviewed; six field marks, two calibration reviews and `ready_for_generation=false` remain open.

## Customer variation in the provisional batch — 13 October 2026

The 100-case generator now uses the pinned 80-customer synthetic master as a source. It chooses 37 active profiles with Low/Medium risk and more than €150,000 of headroom after recorded commitments, and assigns them across 63 ordinary repeated variants. Each archetype's first reference submission and all credit-limit cases retain their original customer. Three early-run archetypes also retain their original customer because their 05:00/07:00 evidence cutoff precedes the master’s 09:00 credit snapshot. The deal's requested shipping destination remains its submitted destination, which can differ from the buyer's registered country. The master is imported before the pilot inside the PostgreSQL batch transaction, and its file hash is part of the reproducibility report. The PostgreSQL diagnostic measured 55 distinct customers, up from 18; aggregate decision counts stayed 18 approval_required, 12 blocked, 11 needs_commitment, 42 needs_evidence and 17 needs_revision. This varies customer credit context, not the reused 20 operational source states or independent evaluation answers. Field and calibration reviews remain open.

## Dated stock variation in generated tests — 13 October 2026

Five repeated STOCK-READY submissions now have separate synthetic inventory observations at 12:05, 12:15, 12:25, 12:35 and 12:45 UTC and run cutoffs five minutes later. The original pilot reads at 12:00 and keeps its original stock row; the existing stress-pilot observation is at 13:00, outside these variant cutoffs. The PostgreSQL reader/full-decision regression attributes each generated case to its own selected inventory ID and the pilot to its prior ID. The aggregate diagnostic rose from 28 to 33 distinct attributed Availability source IDs, with 55 customer IDs and the same five aggregate decision counts. This adds five dated observations for one archetype, not an independent operational distribution across the 100 cases. The field and calibration reviews, independent evaluation answers and generation gate remain open.
