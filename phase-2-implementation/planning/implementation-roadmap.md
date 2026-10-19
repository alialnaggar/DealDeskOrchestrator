# Phase 2 implementation roadmap — planning baseline

**Status:** Workshop 3 (W3.1–W3.8) closed at architectural-direction level; M1 integration and evidence decisions approved 19 October 2026. M1.0 is implemented; Ali authorized bounded M1.1 original-only LangGraph implementation on 19 October 2026. This roadmap is not evidence of coded AI agents. Follow the [decision log](decision-log.md), [Workshop 1 baseline](../architecture/workshop-1-architecture-baseline.md) and [M1 technical specification](../architecture/m1-contract-and-integration-spec.md).

| Order | Milestone / planning work | Dependency and exit evidence |
| --- | --- | --- |
| 0 | Repository audit | Completed as a read-only planning baseline. Phase 2 branch and draft Phase 1C PR diverge; distinguish verified code from design. |
| 1 | Workshop 1: end-to-end flow, D1 AI contribution, D2 contracts, D3 Orchestrator | Provisionally approved and recorded. LangGraph selected; Configuration first, Fulfillment first AI-intensive; exact interfaces remain open. |
| 2 | Workshop 2: LangGraph run/state and frozen-evidence mechanism | Decide exact typed state, node/edge and subject transitions; compare same-transaction, sealed bundle/reconstruction and persistence options against Phase 1C reader. Specify failure/replay tests. Do not add checkpoint infrastructure by assumption. |
| 3 | Workshop 3: specialist/tool and candidate contracts | Closed at direction level (W3.1–W3.8). Six domain payloads, permission registry, Fulfillment investigation and fixed verification boundary approved; typed mappings remain subject to M1 tests. |
| 4 | Focused M1 Contract and Integration Review | Two pinned checkouts and sealed reader bundle/checkpoint replay approved. [M1 spec](../architecture/m1-contract-and-integration-spec.md) pins Phase 1C at `90c0bc8e285ee69262c7db826b786096a77ad004`; exact adapter, replay, tool and candidate acceptance gates precede implementation. Broader model/evaluation operations can be settled when needed. |
| 5 | Master blueprint sections and independent review | Link authoritative Phase 1B/1C rules, write detailed sections in stages, check contradictions and unresolved assumptions, then publish reviewed plan. A narrow milestone may begin when its own contracts/tests are approved; the entire long blueprint need not be finished first. |
| 6 | M1: narrow LangGraph end-to-end assessment | M1.0 pinned dual-checkout reader/replay is complete. M1.1 original-only LangGraph and PostgreSQL restart were separately authorized; six distinct results map one pinned Phase 1C fixed decision. Later separately approved tasks add bounded AI tools and fixed candidate checks. Mixed 12+8 conditional verification remains a Phase 1C compatibility gate. |
| 7 | Incremental specialist capabilities | Add Configuration correction/substitution, Pricing proposals, Credit evidence analysis, Policy corrective options, Routing explanations and wider Fulfillment modes. Keep separate domains and fixed-rule authority. |
| 8 | General candidate orchestration and evaluation | Prove safe selective reruns by fingerprints and dependencies, consider parallel nodes by measurement, finalize persistence/resumption if needed, and compare with rule-only baseline only after independent expected answers are accepted. |

## M1 prerequisite checklist

- [M1 technical specification](../architecture/m1-contract-and-integration-spec.md) reviewed; first coding task scope separately approved. LangGraph remains selected from M1.
- Dual-checkout setup asserts Phase 1C draft commit `90c0bc8e285ee69262c7db826b786096a77ad004`; narrow adapter maps real deal, reader, compiled rule, candidate and evidence interfaces; no silent PR merge or module copy.
- Stable small development fixture; sealed canonical reader bundle, source/run identity and digest replay demonstrated, with checkpoint size/overhead measured.
- Binding candidate full six-check recheck and no-alternative path tested; conditional 12+8 remains unverified until a compatible Phase 1C fixed verifier is available.
- Configurable candidate/retry/time/tool budgets, failures and stopping tests specified.
- Model-provider access, costs and mock behavior settled before paid calls.
- Separate thesis test environment verified without touching Odoo/n8n.
- No evaluation answer drafts exposed to agents.

## Progress and change control

Record each later milestone with commit/PR, fixture, test and CI evidence, known limitations and one business example. W1–W3 are approved directions; exact contracts and compatibility need M1 acceptance tests. The first coding task is a separate approval gate. Material technology changes follow TG1 in the decision log; no replacement or expansion is accepted silently. Phase 1C data completion can progress in parallel; its draft PR stays separate.

## M1.0 implementation checkpoint — 19 October 2026

**Implemented:** [Pinned reader and replay boundary](../backend/README.md) in `phase-2-implementation/backend`, plus [two-checkout CI](../../.github/workflows/phase2-m1-contracts.yml). The Phase 1C source pin is `90c0bc8e285ee69262c7db826b786096a77ad004`; no PR merge/copy or Phase 1C code change. The adapter uses read-only repeatable-read transactions; typed context, canonical reversible bundle, SHA-256 and source rerun validation are in place. [CI run 39244070977](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39244070977) passed eight offline/PostgreSQL tests. Bundle measurements: binding reference 38,717 UTF-8 bytes (59,228-byte PostgreSQL JSONB expression proxy); conditional reference 37,814 UTF-8 bytes. These are **not** LangGraph checkpoint or restart measurements.

**Limitations:** Actual pinned binding fixture is ten units, while the 20-unit 12+8 conditional example remains illustrative and unverified. No LangGraph node/checkpoint storage, Fulfillment tool, access ledger, model, full candidate rerun or VM setup exists yet. Candidate correlation's accepted-path integration and the three sealed-pool tool coverage tests remain next gates. The current Phase 1C role list may be unavailable under a blocked route, and conditional candidate verification remains Phase 1C-owned.

**M1.1 authorized and in progress:** Sequential original-only LangGraph,
versioned state holding the M1.0 sealed bundle, Configuration-first result,
six fixed responsibility mappings and explicit prerequisites. Use a separate
disposable PostgreSQL checkpoint database in CI; prove resumption from a
node boundary and measure actual storage. The pinned Phase 1C aggregate
decision is assembled once, not six new rule engines. Model, candidate,
frontend, VM and Phase 1C changes remain outside this milestone.

The initial [M1.1 PostgreSQL CI
run](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39255258148)
passed 15 tests and proved a cross-process node-boundary resume. The backend
README records measured checkpoint fields and shared table sizes. A follow-up
CI run validates the explicit technical-failure stop path and pinned
Python 3.12 workflow before M1.1 is marked complete.
