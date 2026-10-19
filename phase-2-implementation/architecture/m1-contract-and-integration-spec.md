# M1 contract and integration specification — review baseline

**Status:** Approved architectural decisions for Phase 1C integration and M1 evidence replay by Ali, 19 October 2026. M1.0 was separately authorized and implemented; later coding tasks require separate approval. Detailed contracts below are the approved review baseline; Phase 1C-dependent mappings and engineering defaults require the acceptance gates before promotion. This elaborates W1–W3 without replacing Phase 1B business rules or Phase 1C fixed-rule ownership.

**Phase 2 branch:** `phase2-agent-implementation`. **Pinned Phase 1C draft source:** `phase1c-candidate-contract` commit `90c0bc8e285ee69262c7db826b786096a77ad004` (draft PR #1). Do not float the integration to a branch name in tests or CI. Changes to this pin require review and retesting. The draft PR remains separate and unmerged.

## Purpose and scope

The first implementation starts with Configuration validation, records an original deterministic six-responsibility assessment (including explicit unable-to-complete results), then invites Fulfillment AI only for an eligible recoverable shortage. For a customer requesting 20 units by Friday with partial delivery permitted, dated fixed evidence may support 12 by Friday and a possible later eight subject to supplier confirmation. AI may investigate and suggest a split, explain the tradeoff, return a finding without proposal, or abstain. Python verifies each proposal. The original submission is immutable; each candidate is separately identified and compared for human review. No component approves a business deal, reserves stock, books production or promises delivery.

The conditional eight units are an **unverified planning idea** with the pinned Phase 1C interface. Full deterministic verification of a mixed binding/conditional schedule is a Phase 1C compatibility dependency. Do not label a conditional proposal as a verified candidate or claim that M1's full candidate acceptance gate passed. A supported binding-supply fixture can exercise the full candidate-recheck path separately.

## Decision M1-I — Two pinned checkouts

Phase 2 code lives on its own branch or feature branch. During local integration and CI, check out the same private repository twice: Phase 2 at the reviewed commit and Phase 1C at the exact SHA above, in separate directories. Document the two paths and load only the pinned `phase-1c-data/implementation` Python modules through a narrow, explicit import path in the test/process configuration. Assert the source commit before tests. Do not copy modules or merge draft PR #1 into Phase 2. Do not import Phase 1C's development runtime as an agent: `execute_development_run` writes logs and its deterministic summaries do not implement live specialists.

The adapter calls the read-only `read_run(conn, run_id, commercial_rule_mode="compiled", ...)`, `assemble_deal_decision(bundle)`, and candidate functions `review_partial_delivery`, `reader_input_digest`, `verify_run_correlation`, `assess_reader_slices` and `compare_for_human` only where their tested preconditions hold. Pin exact signatures and selected keys in adapter contract tests. `compare_candidate_set` is an optional bounded test aid, not an approval engine. The Phase 1C reader currently supports one stocked/supplier-finished line for its reader-backed candidate experiment and binding supply at a single location; a conditional offer is not confirmed supply. Phase 1C owns any extension to fixed conditional candidate classification. A later accepted integration/packaging choice requires explicit review.

**Alternatives considered:** immediate merge/copy (prematurely accepts draft code); duplicate Phase 2 rules (inconsistent authority); pinned separate checkouts (selected for isolation and reproducibility). This is an import arrangement, not a new library or service.

## Decision M1-E — Sealed evidence bundle and checked rereads

At run creation, call `read_run` once inside a PostgreSQL `REPEATABLE READ READ ONLY` transaction. Pin the Phase 1C run ID, original deal ID, business `as_of_at`, `data_snapshot_ref`, catalogue and policy versions, configuration hash, Phase 1C commit and `reader_input_digest(bundle)`. Serialize the bounded selected bundle into canonical UTF-8 JSON, with explicit reversible tags for `Decimal`, `date`, timezone-aware `datetime` and `UUID`; sorted keys, stable array order and compact separators. Reject unsupported values, ambiguous types and a failed round trip. Hash the canonical bytes using SHA-256. Store the versioned sealed representation and hashes in the PostgreSQL-backed LangGraph checkpoint state for M1; credentials and hidden evaluation answers are excluded. Decode a fresh read-only view for each node/tool; do not mutate the sealed bytes.

The initial model view is a restricted projection. M1's three authorized Fulfillment operations reveal bounded subsets of the sealed reader-selected pool and log actual returned record IDs, versions/fingerprints, source category and tool-call identity. Thus records can be discovered later without changing the pinned source pool. A record absent from that bounded pool produces an explicit `discovery_limit`/unsupported-source result; it is **not** proof that no relevant real supply exists. Test all three tools against the sealed pool, including a selected stock source, conditional offer and a missing out-of-pool record.

Before Phase 1C candidate assessment, begin a new read-only repeatable-read transaction. First reread the original, compare run context and `reader_input_digest` to the sealed source. Only if equal, read the candidate within that **same transaction**. Then use Phase 1C's correlation check and compare candidate source identity/digest to the original. A mismatch stops affected verification and records an identity/evidence error; it never silently refreshes the context. A genuinely refreshed fact requires a new identified assessment context. A snapshot reference alone is not an MVCC snapshot across transactions.

Measure canonical bundle bytes and PostgreSQL checkpoint write/read size and latency in M1 tests. The bounded checkpoint bundle is the initial approved arrangement. If size or overhead becomes impractical, propose an immutable bundle stored separately in the **same** PostgreSQL thesis database with only reference/hash in graph state; document measurement, alternatives, retention/security and change rationale before changing storage. No other database, queue or object store is authorized.

**Alternatives considered:** one long transaction across model calls (fragile across waits/restart); as-of-only rereads (can change row versions); sealed bundle plus checked rereads (selected). The existing Phase 1C fingerprint covers reader-selected inputs; canonical sealing additionally protects the serialized working pool.

## M1 typed boundary, version 1

Use existing Python `dataclass`/`TypedDict`/`Literal` facilities and explicit JSON encoding. The names and enumerations below are M1 contract targets; adapter field mapping must be proven against the pinned Phase 1C code. The LangGraph state is authoritative for workflow control, while specialists receive a restricted projection and return typed results, never arbitrary state mutation.

| Type | Required fields (logical types) | Owner |
| --- | --- | --- |
| `RunContextV1` | `contract_version: "1"`, `assessment_id: str`, `phase1c_run_id: UUID`, `original_deal_id: str`, `submission_ref: str`, `as_of_at: datetime`, `data_snapshot_ref: str`, `catalog_version: str`, `policy_set_code: str`, `config_hash: str`, `phase1c_commit: str`, `source_input_digest: str`, `bundle_sha256: str` | Orchestrator |
| `SubjectRefV1` | `kind: original|candidate`, `subject_id: str`, `parent_subject_id: str|null`, `change_digest: str|null` | Orchestrator |
| `SpecialistResultV1[T]` | `version: "1"`, context/subject references, `specialist: Configuration|Pricing|Fulfillment|Credit|Policy|ApprovalRouting`, `producer: deterministic|AI`, `attempt: int`, `execution: completed|failed|skipped`, `contribution: finding|proposal|abstention|none`, `payload: T|null`, cited source/rule references, uncertainty reasons, typed error/reference and trace IDs | Trusted runtime assigns identity/producer/attempt; specialist supplies only bounded domain content |
| `FixedVerificationV1` | candidate/subject identity, `shape: valid|rejected|unknown`, `evidence: binding|conditional|unknown|infeasible|unsupported`, rule findings, source digest, whole-subject assessment status, reasons and trace | Fixed Python |
| `WorkflowDecisionV1` | evaluated prerequisites, accepted/quarantined result, next node, retry/proposal/tool counters, stopping reason and final review status | Orchestrator |
| `AssessmentStateV1` | run context, sealed bundle/reference, original and candidate subject map, per-subject specialist/fixed results, candidate lineage and statuses, access ledger, budgets, errors/conflicts, execution trace and final-package reference | LangGraph Orchestrator |

Use string encoding for money/precise decimals and ISO 8601 date/time in checkpoint JSON, with explicit validated decoding. A successful invocation does not imply a favorable business result or a transition. An unauthorized tool call, AI abstention, business unknown, conditional finding and technical failure remain distinct. The full reader bundle stays outside model inputs and specialist envelopes. Record source IDs and rule IDs by reference rather than duplicating graph state.

### Specialist domain payloads and execution gates

| Responsibility | Required input to execute | M1 payload |
| --- | --- | --- |
| Configuration | Structured subject, pinned catalogue/configuration context | Per-line/group status, normalized references, compatibility/BOM failures and missing facts; executes first |
| Pricing | Relevant validated configuration and effective commercial inputs | Fixed full-term value, discounts/margins, pricing rules and gaps; no model arithmetic |
| Fulfillment fixed | Valid configuration, exact request and dated selected supply | Quantity/date/source status, bottleneck, commitment class and uncertainty |
| Credit | Verified exact-subject commercial value/terms and same-customer dated credit facts | Exposure/headroom, freshness, risk and source/rule findings |
| Policy | Effective policy and each rule's actual prerequisites | Evaluated rule IDs/severity, evidence, unresolved applicable rules and reason; independent rules still evaluate |
| Approval Routing | Reconciled exact-subject findings, with explicit unresolved status | Required human roles/order/rule IDs **when fixed evidence establishes them**, plus independent ordinary-routing eligibility and withholding reasons |

A failed or conditional finding is a business result, not automatically an execution barrier for another independent responsibility. The current Phase 1C `assemble_deal_decision` attributes six deterministic domains, but `evaluate_compiled_policy` may return no required-role list when blocked. Phase 2 must not infer mandatory roles from model prose or duplicate approval rules: mark roles unresolved where the fixed interface cannot establish them and retain the withheld route. Supplying fixed role attribution under blockers is a Phase 1C compatibility gate for the stronger W3.8 behavior. Rule-by-rule dependency detail likewise requires mapping or compatible fixed exposure; do not invent a pass for an unexposed rule.

### Fulfillment AI and tools

`FulfillmentInputV1` contains context/subject references, one validated line and group, quantity/date/destination, structured customer partial-delivery and mandatory constraints, original fixed shortage and relevant references, permitted named tools/scopes and remaining budget. It contains no credentials or unrelated domain bundle.

`FulfillmentContributionV1` is exactly one of: `proposal` (line/slice change claims, observed evidence refs, unmet requirements, assumptions, uncertainty and tradeoff); `abstention` (reason and scope of investigation); `finding_without_proposal` (cited bottleneck/limitation and reason no candidate was recommended). Technical failure is the separate envelope execution path. The model cannot assert verification, create authoritative candidate identity or upgrade conditional supply.

The Phase 2 adapter exposes exactly `inspect_line_supply`, `inspect_fulfillment_paths` and `inspect_evidence_record` to this specialist. The trusted Orchestrator assigns identity. A versioned Python permission registry checks tool name and run/deal/subject/candidate/customer/line/source/version and bounded argument scope on every invocation. Each tool returns typed records/references or one of `no_eligible_evidence`, `insufficient_or_conditional`, `unsupported_capability`, `discovery_limit`, `authorization_denied`, `technical_failure`. The path tool delegates fixed calculations to Phase 1C; if mixed binding/conditional path derivation is unavailable it reports unsupported capability. An access ledger records records **actually returned**, and only those records in the pinned context may support AI citations. Candidate verification is a separate Orchestrator-controlled fixed step.

## LangGraph execution and candidate lifecycle

Sequential M1 graph nodes: create/pin run; Configuration and result gate; eligible Pricing; fixed Fulfillment; eligible Credit; applicable Policy; original Routing/withheld-result computation; reconcile and record complete/explicitly incomplete original fixed assessment; Fulfillment AI eligibility gate and bounded investigation; AI output validation; fixed candidate verification; full six fixed responsibility recheck for an assessable candidate; exact-subject Routing; final comparison/human package. Separate validation after each specialist checks version, identities, producer, output shape, references, authorization ledger, dependencies and business gates. Independent findings remain available even if another domain is blocked.

Investigation eligibility requires a valid relevant configuration, a fixed potentially recoverable shortage, required customer constraints and tool/evidence context. A distinct Credit or Policy blocker alone does not disqualify investigation; only an explicit testable rule establishing no useful human-review contribution may do so. All blockers remain visible and withhold inappropriate ordinary routing.

Candidate states: `proposed_unverified` -> `shape_rejected|source_unverifiable|eligible_for_fixed_assessment` -> `fixed_assessment_complete|fixed_assessment_incomplete` -> human comparison. Candidate ID, parent, exact diff, version and per-subject results are Orchestrator owned. Binding-supported supply is still unreserved and awaits customer/human action. A conditional 12+8 suggestion remains `source_unverifiable` under the pinned Phase 1C verifier and may be shown only as an unverified planning idea. Approval Routing is recomputed for the exact candidate when its required fixed checks are complete.

Failure classes: domain rule violation, unknown/missing/stale evidence, conditional finding, AI abstention, malformed output, invented/unseen citation, authorization denial, rejected candidate, unsupported capability, transient model/tool failure, identity/version/digest mismatch, contradictory findings and exhausted budgets. Do not retry rule violations. Only idempotent transient failures may retry once. Provisional configurable M1 ceilings: two distinct proposals, one revision level, one eligible transient retry; time and call ceilings must be set and tested before enabling a live model. A checkpoint resume retains budgets and avoids duplicate candidate IDs. Missing evidence or a failed call never becomes a favorable result.

## Acceptance gates

1. **Pin/import:** two-checkout setup reproducibly asserts Phase 1C SHA and adapter signature/field mappings; no PR merge, source copy or use of development runtime as an agent.
2. **Sealing/replay:** canonical encode/decode preserves dates, decimals and IDs; hashes/digests survive checkpoint restart. Test bundle size/write/read overhead. A changed reader input or subject/version mismatch stops affected verification. No long-lived transaction crosses model calls.
3. **Investigation pool:** all three tools can inspect appropriate sealed M1 records; out-of-pool access reports discovery limitation; wrong customer/line/version and records not actually returned cannot be cited.
4. **Original flow:** Configuration executes first; valid dependencies proceed; failed/conditional findings do not suppress independent checks; Policy marks unavailable rules unresolved; roles are reported only when fixed support exists and ordinary routing is withheld for unresolved required findings.
5. **AI outcomes:** offline mock covers proposal, finding without proposal, abstention, malformed output, timeout, authorization denial and unsupported fixed capability. Retain original fixed assessment.
6. **Candidate:** original immutable; unique identity/lineage; quantity, group, partial permission, source and date checks; full six deterministic recheck and exact Routing on a supported binding candidate; conditional 12+8 remains unverified until a compatible Phase 1C interface is accepted and tested.
7. **Restart/safety/package:** restart after Configuration and during investigation retains identities, budgets, access ledger and findings; duplicate suggestions deduplicated; human package shows original/candidate differences, unmet Friday date, conditional supplier status, source provenance, independent blockers, known human roles, withheld routing and stop reasons. No autonomous business action.
8. **Evaluation boundary:** offline tests use development fixtures and mock model; hidden independently reviewed answer keys stay inaccessible. Comparative improvement remains an untested hypothesis.

## Implementation sequence and integration gates

1. Approve a small first coding task limited to dual-checkout reproducibility, Phase 1C read-only adapter, `RunContextV1` and canonical sealing/fingerprint tests. No graph/model/tool implementation in that task.
2. Verify isolated thesis PostgreSQL and LangGraph/checkpointer compatibility, then implement typed state and sequential original fixed graph with restart tests.
3. Add versioned permission registry, sealed-pool tools, access ledger and offline mock Fulfillment AI with bounded proposals.
4. Add candidate state/verification, current binding-supported full six deterministic rerun and human comparison.
5. Integrate a **compatible Phase 1C** mixed conditional candidate verifier after separate Phase 1C ownership/review; test the illustrative 12+8 path. Until then, show it only as an unverified idea.
6. Evaluate model choice, live access/cost, broader specialist AI, selective reruns and parallelism in later approved tasks. PostgreSQL checkpointing is selected from M1; no Redis, new database, external authorization service or paid model is implied.

Each task records commit, test/CI evidence and limitations. Coding, dependency installation, infrastructure changes, Phase 1C edits and PR merge require their own authorization as applicable.

## M1.0 implementation evidence — 19 October 2026

The [M1.0 backend note](../backend/README.md) identifies implementation files, exact two-checkout setup, observed sealed-bundle sizes and limitations. [CI run 39244070977](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39244070977) passed eight tests with pinned Phase 1C and disposable PostgreSQL 18. Binding stock/confirmed-inbound and conditional supplier-offer reference fixtures remained distinct. A changed selected inventory row caused candidate reread rejection in a disposable test and was restored afterward. M1.0 prepares a sealed bundle but has **not** stored it through a LangGraph checkpointer, measured checkpoint overhead, tested resume, or implemented the three Fulfillment tools. Those gates remain open; the conditional 12+8 candidate cannot be promoted to verified.
