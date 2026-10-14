# Phase 1C evaluation authoring boundary — 12 October 2026

The [scenario matrix](../implementation/phase1c_scenario_matrix.yaml) plans
36 evaluation variants across 18 archetypes. **None is independently
reviewed yet.** The two files here are development examples for building
that process, not held-out cases or released answer labels.

| File | Intended reader | Contents |
| --- | --- | --- |
| `development_inputs.json` | Future candidate system and reviewer | Frozen illustrative submission, proposed slices and dated source facts; no answer fields |
| `reviewer_oracle_draft.json` | Independent reviewer only | Provisional author-written findings, evidence references and rationale; review status pending |

Both examples ask for ten units on 4 September 2026 and permit partial
delivery. Eight units have free inventory on that date. In the supported
example, two later units have a confirmed receipt dated 8 September. In the
refusal example, those two units have only an offer. The customer has not
accepted a later date in either example. The draft answer calls the first
proposal supply-supported but still pending customer review, and the second
unvalidated. A different reviewer must inspect the frozen facts and correct
or accept those findings before they become evaluation answers.

`../implementation/validate_phase1c_evaluation_draft.py` checks shape,
version, evidence references, non-reuse of sources, quantity conservation,
dated facts, original-date preservation and absence of answer fields from
the input. It does **not** derive or certify the expected findings. CI tests
failure cases for leakage, false references and premature review claims.
The files share a private repository; separate paths and a flag do not
provide access control. A future evaluation harness must load only the
input file for the system under test and keep the reviewed oracle out of
its prompt, tools and outputs.

These examples omit a full product catalogue, location/route, prices,
credit, policy and approval evidence. They cannot be executed as complete
deals or counted among the 36 held-out cases. Next: create frozen, distinct
database-backed evaluation cases; have a separate reviewer record findings
from those facts before running the agents; then compare the same cases
against the rule-only baseline and score specialist errors, trace integrity,
useful alternatives and safe refusal. Do not use the 400 historical
diagnostic outcomes as labels.

## Database-backed development scoring trial

`reader_trial_oracle_draft.json` is a separate, **unreviewed** reference for
the existing PostgreSQL shortage regression. The test first reads the
original deal and independently rechecks two proposed delivery dates, then
loads this draft and calls `score_phase1c_reader_trial.py`. The scorer
compares the rule-only original status, original customer date, selected
source IDs, proposed dates, six rerun responsibilities, unmet constraints,
human action, and whether each option has validated supply. It also rejects
an unauthorized selection and altered trace content. A supported 8-now /
2-on-8-September option and an unsupported 8-now / 2-on-5-September option
both keep the original requested date of 4 September. The latter is
unsupported because its proposed date precedes the confirmed receipt.

This trial reuses a **development regression fixture**. Its expected
findings were authored from that fixture and are pending independent review;
it is not hidden, not a newly generated evaluation row, and not one of the
36 held-out cases. A trace hash detects changes to the scorer input, while
the separate reader-backed replay test checks the underlying database
facts. Neither provides an access-controlled independent oracle. The
reported count of independently reviewed cases remains **0/36**.

## Separate database input preparation — 12 October 2026

`implementation/phase1c_evaluation_input.py` prepares a source-only packet from a separate PostgreSQL submission and operational source IDs. The integration fixture uses a distinct product, inventory, receipt, deal and run, with 11 requested units on 3 September; it shares versioned policy, shipping lane and customer master context. The packet contains the selected reader input rows and a SHA-256 seal, with no reader-derived findings, proposed option, score or reviewer answer. The preparation check rejects overlap with named development deal and source IDs, and detects tampering. The case is rolled back after the test: no durable frozen evaluation release or independently reviewed answer exists yet. It is **not counted among the 36**. A separate reviewer still needs a frozen complete case and an isolated answer key before any agent run or baseline scoring. Readiness and calibration remain unchanged.

## Operational source ID isolation for evaluation preparation — 14 October 2026

The source-only packet preparation rejects development deal IDs and now checks inventory, confirmed inbound, production capacity and digital-capacity row IDs against the caller-supplied exclusion set. A source-only test covers all four modes; the database integration fixture remains a rollback-only example, not one of the 36. The caller must build a complete exclusion set from development sources and must separately review dates, provenance and semantic similarity. Shared catalogue, policy, lane and customer context may remain, so distinct IDs alone do not establish independent cases. No answer was reviewed, frozen or exposed to an agent.


## Development source exclusion registry — 14 October 2026

The generated-batch PostgreSQL test now also reads 16 reference runs and 38 connected pilot/dependency runs alongside the 100 generated runs, collects **reader-selected raw row IDs** for inventory, inbound supply, production capacity and digital capacity, and uploads `phase1c-development-source-exclusions`. The JSON payload states the run/deal count, sorted IDs by table and a SHA-256 seal. `excluded_ids_from_manifest(..., expected_run_count=154, expected_deal_count=152)` validates it before the IDs are supplied to `prepare_review_input`. The test rejects duplicate runs and checks the 152 distinct deals and seal tampering; all four source types must have at least one selected ID.

This registry is generated inside a rolled-back development database, contains no decision labels or evaluation answers, and should be pinned to the producing CI run. It excludes the 400 historical reads and does not police catalogue, customer, shared policy, supplier-offer, lane or service-rule context. Distinct IDs do not establish independent source creation or prevent near-duplicate cases. A future 36-case authoring job must use this registry, inspect those additional overlaps and dates, and obtain independent expected findings. The count remains 0/36 reviewed.

The measured PR artifact contains 49 inventory, 12 inbound, 14 production-capacity and 10 digital-capacity IDs. The same sealed JSON is versioned as [`phase1c_development_source_exclusions.json`](../implementation/phase1c_development_source_exclusions.json); the PostgreSQL test compares a new render with it exactly. A changed source set therefore fails CI until the registry and its implications are reviewed together. The registry covers the 154 development reads, not the historical 400.


## Identity-pinned evaluation preparation — 14 October 2026

The versioned development exclusion registry now includes all **154 run IDs and 152 deal IDs**, in addition to the 85 selected operational row IDs (49 inventory, 12 inbound, 14 production and 10 digital). Its new SHA-256 seal is checked against a fresh PostgreSQL render. `prepare_heldout_review_input` requires this verified registry, rejects a reused run/deal or selected operational source ID, and produces the same input-only packet as the general development preparation path. Source-only tests cover missing/tampered registries and each rejection; the existing separate rollback-only PostgreSQL example exercises the mandatory path. That example shares permitted customer, policy and lane context and remains a **development preparation example, not one of the 36**. The registry does not exclude the 400 historical sources, copied facts with new IDs, shared supplier/PO or service evidence, or answers. Those checks and independent reviewer findings remain future gates (0/36 reviewed).


## Reader-selected capacity scope — 14 October 2026

The first mandatory-registry run found that the separate stocked-only database example still carried development production-capacity rows. The reader had selected all current workshop capacity globally, even though no line required a build. It now selects production capacity only when at least one line is `make_to_order`, in both current and historical read paths. The stocked-only input packet has an empty capacity list; its held-out preparation check passes against the pinned registry. PostgreSQL checks for reader, candidate replay, 36-pilot, 400 historical and the 100 generated decisions passed. The generated distribution remains 23/12/11/37/17 for approval_required/blocked/needs_commitment/needs_evidence/needs_revision, and the sealed 154-run registry is unchanged. This repairs an irrelevant-input leak; the example still shares other context and is not an independently reviewed evaluation case.

## Historical source identity inventory — 14 October 2026

The historical audit now emits `phase1c-historical-source-exclusions`, a sealed source-only registry from 400 dated reader runs. The baseline decision diagnostic remains a different artifact. The registry has not yet been pinned or required by `prepare_heldout_review_input`; until then, a case can pass the 154-run development exclusion yet reuse a historical run or source. Even both identity checks cannot establish independence from copied facts or shared customer, policy, lane, supplier and service context. No case has been counted or reviewed (0/36).
