# Phase 1C evaluation authoring boundary — 12 October 2026

## Provisional 36-case input authoring — 14 October 2026

The repository now contains reproducible source definitions for **36 provisional evaluation inputs**, two per planned archetype. [Source definitions](provisional_cases.json) contain submitted rows and separately supplied synthetic provider records. The [authoring manifest](provisional_authoring_manifest.json) maps the scenario intent and records source hashes and pending reviews; it is reviewer material and must stay outside the system under test. There are **0 independently reviewed expected answers** and no released evaluation results.

`../implementation/render_phase1c_evaluation_cases.py` constructs new customers, submissions, inventory, offers, PO/receipts, workshop observations, digital pools/proofs, service rules and lanes without copying development or historical deal rows. The five selected sellable SKUs, V1 catalogue/BOM assumptions, canonical location/region codes and compiled baseline policy are shared context. The author knows the development archetypes; distinct IDs and isolated loading do not establish statistical or semantic independence.

CI uses a separate disposable database and loads each case alone with the shared masters. It validates typed rows, reads the case twice, compares source-only packets, checks both pinned exclusion registries and rejects cross-case operational ID reuse. It exports input packets and provider records separately from authoring metadata. It does not assemble, score or publish expected deal decisions. A separate reviewer must inspect complete facts and record answers outside these inputs before baseline or agent evaluation. Calibration, six field marks, two calibration reviews and `ready_for_generation=false` remain open.

## Service-region source correction — 14 October 2026

Author source inspection found that `EVAL-PREP-029` and `EVAL-PREP-030` had only an eligible DE-NW rule while submitting DE-BY. The reader's exact-region lookup therefore had no matching record: missing coverage is unknown, not an explicit denial. The source definitions now state `country_code=DE`, `region=DE-BY`, `eligible=false` for those two cases. A source-condition test requires an explicit matching rule for all four service cases. This repairs authoring intent before independent answer review; it is not a reviewed answer key.

The regenerated source-definition SHA-256 is `5b3168a6871ebb2cfdcaa0c594c9ff6e34ab300708661146c22a994f85a09977`. All 36 packet hashes and blank review bindings are regenerated because the generator-source fingerprint is part of each run's context; the substantive region condition changes are confined to those two cases. The earlier `7dff...` definition/index is superseded. CI must reproduce the current packet index from a fresh database. No historical/pilot/generated-regression input, schema, calibration value or reviewed answer changed (0/36).

## Pinned packet index and review procedure — 14 October 2026

The initial [PostgreSQL authoring run](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38586442975) produced 36 replay-equal input packets and separate provider files. The current [pinned index](provisional_packet_index.json), including the correction above, stores each payload hash and provider-file hash and the source-definition SHA-256 `5b3168a6871ebb2cfdcaa0c594c9ff6e34ab300708661146c22a994f85a09977`. A fresh CI database must reproduce the index exactly. This pins input content; it does not freeze calibration or certify answers.

| File or artifact | Role |
| --- | --- |
| `provisional_cases.json` | Reproducible submitted rows and case-owned operational/provider source definitions |
| `provisional_authoring_manifest.json` | Reviewer-only intent, shared context, source hashes and pending reviews |
| `provisional_packet_index.json` | Expected source/provider hashes for the 36 prepared packets |
| CI artifact `phase1c-provisional-evaluation-inputs` | 36 source-only reader packets, 36 provider files and the packet index; no archetype map, findings or scores |

For independent review:

1. Rebuild from the tracked definitions or obtain the named artifact from the producing run. Compare its index with the tracked index before reviewing the corresponding case/provider files.
2. Inspect the submission and complete selected facts, dates, units, costs, credit context, policy rules and evidence records. The authoring map states intent; it is not an expected answer and may be wrong.
3. Record a reviewer identity, date, relationship to the case author, and findings for configuration, pricing, fulfillment, credit, policy and routing. Cite exact source IDs and rule references, explain uncertainty and unmet customer constraints, and state what still needs human review. Correct or reject a case if its full facts fail its stated purpose.
4. Store findings separately from the source inputs. Keep that file outside the future system's prompt, tools and outputs. Another authoring run or diagnostic result cannot be presented as an independent review.
5. Review all 36 cases and resolve disagreements before running and scoring the rule-only baseline and agents on the same pinned inputs. Count reviewed answers only after recorded review; the present count is **0/36**.

These cases assume their supplied source set is complete within the fictional snapshot. Empty receivable and payment sets represent a declared no-invoice/no-payment-history context, not proof that a real company's financial source is complete. All ordinary credit profiles are fresh; credit-limit cases have separate headroom conditions. Only five sellable SKUs and two quantity/quote patterns are represented. Shared catalogue, BOM, policy and canonical location context and implementation-informed authoring remain explicit limitations.

## Blank review workspace — 14 October 2026

[`provisional_review_template.json`](provisional_review_template.json) has one empty form per pinned case. It contains no archetype labels or prefilled findings. Each form binds the input/provider hashes and asks for reviewer provenance, findings and rationale for all six responsibilities, source references, an overall proposed gate status, human actions and unresolved questions.

Copy the template to a **reviewer-only working file**, outside the system input folder. Leave `review_status=pending` until a full draft is written; then use `draft_complete`. Record identity, method (`human`, `model` or `model_assisted`), a timezone-aware date and an honest independence statement. First write findings from the source packets without consulting the authoring intent or deterministic diagnostics. Compare scenario intent afterwards to review coverage.

References identify an exact location in a pinned source document, for example:

```json
{"document":"packet","pointer":"/source_rows/inventory/0/quantity_on_hand"}
```

Use `document=provider` for the separately supplied provider file, with a pointer under `/records`. A reference to an empty collection can support a stated absence; the reviewer must explain its meaning and the fictional completeness assumption. A resolving pointer proves that the cited fact exists, not that the conclusion follows from it.

From `implementation/`:

```bash
python phase1c_evaluation_review.py --check-template
python phase1c_evaluation_review.py --review-file /path/to/reviewer-work.json --packet-directory /path/to/downloaded-packets
```

The checker binds the workspace to the tracked index, requires all six findings and human actions for complete drafts, checks packet/provider hashes, and resolves references. It rejects invented references, changed sources, missing provenance, an `approved` system outcome and attempts to claim accepted/independently reviewed answers. **A complete draft still reports 0 independently reviewed answers.** Substantive correctness, reviewer independence and final acceptance require a separate recorded review; this tool cannot certify them. No baseline or agent score is run here.

## Earlier development examples and checkpoints


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

The PostgreSQL export is now pinned as [`phase1c_historical_source_exclusions.json`](../implementation/phase1c_historical_source_exclusions.json), sealed with `bc16d4e3c86b36bd0392889909296dbc970330d5b067dfab0d12b6d8481ee544`. `prepare_heldout_review_input` requires it together with the 154-run development registry and rejects run/deal/selected operational ID reuse from either cohort. The 400 historical reads selected 844 inventory, 1,372 inbound, 24,294 production-capacity and 1,870 digital-capacity IDs (unique within each type). These are identity counts, not independent evidence instances. The database preparation example still shares customer, policy, PO and lane context, so it is not counted among the 36. Independent review remains 0/36.
