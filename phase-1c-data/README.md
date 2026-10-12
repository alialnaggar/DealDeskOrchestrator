# Phase 1C — synthetic data and implementation

**Status: provisional, 11 October 2026.** This directory is the project copy of
`alialnaggar/dealdeskdata` branch `phase1c-reader-draft` at commit
`8bb6117ba24a4e8e0b7d20a70aca670f0edbb08a`. The implementation files
retain their original relative paths. The migration passed the private PostgreSQL workflow; edit this repository
for all new Phase 1C work. The old repository is a historical portfolio copy.

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
BOMs (25 component selections). It has not yet been integrated into runtime
catalogue attributes, and product fit and price/cost reviews remain open.
The [calibration decision sheet](calibration-decision-sheet.md) now quantifies
all 24 BOMs' missing detailed fit attributes and the draft buildable margins;
its p90 comparison is a distribution target, not a per-product hard limit.
The 100 generated tests and separate 36-case evaluation set with independently
reviewed expected findings remain to be completed. `ready_for_generation`
remains false. See `calibration-decision-sheet.md` for the selected scope
and `implementation/phase1c_release_review.md` for the dated
evidence and `implementation/phase1c_data_readiness_plan.md` for the work order.

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
