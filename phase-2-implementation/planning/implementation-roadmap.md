# Phase 2 implementation roadmap — planning baseline

**Status:** Workshop 1 directions D1–D3 provisionally approved 18 October 2026; detailed specifications, integration and implementation gates remain open. This roadmap is not evidence that milestones have been coded. Follow [decision log](decision-log.md) and [Workshop 1 architecture](../architecture/workshop-1-architecture-baseline.md).

| Order | Milestone / planning work | Dependency and exit evidence |
| --- | --- | --- |
| 0 | Repository audit | Completed as a read-only planning baseline. Phase 2 branch and draft Phase 1C PR diverge; distinguish verified code from design. |
| 1 | Workshop 1: end-to-end flow, D1 AI contribution, D2 contracts, D3 Orchestrator | Provisionally approved and recorded. LangGraph selected; Configuration first, Fulfillment first AI-intensive; exact interfaces remain open. |
| 2 | Workshop 2: LangGraph run/state and frozen-evidence mechanism | Decide exact typed state, node/edge and subject transitions; compare same-transaction, sealed bundle/reconstruction and persistence options against Phase 1C reader. Specify failure/replay tests. Do not add checkpoint infrastructure by assumption. |
| 3 | Workshop 3: specialist/tool and candidate contracts | Pin real Phase 1C interfaces; define six payloads, permission lists, Fulfillment investigation, proposal/abstention, verifier and candidate lineage. Draft failure taxonomy and exact acceptance criteria. |
| 4 | Workshop 4: evaluation and operational design | Hidden-answer isolation, rule-only comparison, metrics, model-provider/cost choices, retries/budgets, checkpointing, VM isolation and later parallelism criteria. Secure explicit approval for any material new technology or cost. |
| 5 | Master blueprint sections and independent review | Link authoritative Phase 1B/1C rules, write detailed sections in stages, check contradictions and unresolved assumptions, then publish reviewed plan. A narrow milestone may begin when its own contracts/tests are approved; the entire long blueprint need not be finished first. |
| 6 | M1: narrow LangGraph end-to-end assessment | On an explicit compatible integration checkout, Configuration first; prerequisite fixed checks; Fulfillment AI investigates the 20-unit shortage; candidate or abstention; fixed proposal verification; all six deterministic responsibilities rerun for the candidate; exact Routing recomputed; human comparison and trace. Offline mock-model tests and PostgreSQL integration/CI required. No code starts from this roadmap alone. |
| 7 | Incremental specialist capabilities | Add Configuration correction/substitution, Pricing proposals, Credit evidence analysis, Policy corrective options, Routing explanations and wider Fulfillment modes. Keep separate domains and fixed-rule authority. |
| 8 | General candidate orchestration and evaluation | Prove safe selective reruns by fingerprints and dependencies, consider parallel nodes by measurement, finalize persistence/resumption if needed, and compare with rule-only baseline only after independent expected answers are accepted. |

## M1 prerequisite checklist

- Exact LangGraph state/node/edge spec and tool permissions reviewed.
- Actual Phase 1C submitted-deal, reader, compiled-rule, candidate and evidence interfaces pinned and compatible; no silent PR merge.
- Stable small development fixture and source/run identity mechanism.
- Candidate verification and no-alternative path specified, including conditional versus confirmed.
- Configurable candidate/retry/time/tool budgets, failures and stopping tests specified.
- Model-provider access, costs and mock behavior settled before paid calls.
- Separate thesis test environment verified without touching Odoo/n8n.
- No evaluation answer drafts exposed to agents.

## Progress and change control

Record each later milestone with commit/PR, fixture, test and CI evidence, known limitations and one business example. D1–D3 remain provisional until detailed contracts and compatibility tests are reviewed. Material technology changes follow TG1 in the decision log; no replacement or expansion is accepted silently. Phase 1C data completion can progress in parallel; its draft PR stays separate.
