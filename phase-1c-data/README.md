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
