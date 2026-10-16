# Deal Desk Orchestrator — AI coding agent instructions

## Source of truth and scope
This private repository `alialnaggar/DealDeskOrchestrator` is the only source of truth. Inspect the current branch, PRs, relevant GitHub Actions, root README, Phase 1B architecture, and current Phase 1C interfaces before making changes. Do not use old ChatGPT attachments, Google Drive copies, or `alialnaggar/dealdeskdata` as current authority.

Phase 1A is literature review; Phase 1B is approved architecture; Phase 1C is synthetic data, evidence reader, and deterministic rules. Phase 2 is **implementation of the working AI agent system**. Do not restart Phase 1C generation or calibration in Phase 2.

## Product behavior
A salesperson submits a structured deal. The Orchestrator coordinates six specialist responsibilities:
1. Configuration Validator
2. Pricing & Margin
3. Availability, Production & Fulfillment
4. Credit & Risk
5. Policy & Compliance
6. Approval Routing

Specialists use authorized, dated evidence and deterministic verification tools to explain findings and, where appropriate, propose bounded alternatives. The Orchestrator manages prerequisites, run identity, disagreements, affected-check reruns, stopping conditions, and the final review package.

**Authority boundary:** AI may recommend; it cannot approve deals, waive policy, reserve stock, book production, promise delivery, or treat conditional supplier offers as confirmed supply. Hard calculations and rules belong to deterministic tools. Cite evidence and rule IDs; distinguish confirmed, conditional, unknown, and infeasible. Preserve original submitted deals and trace candidate changes.

## Implementation approach
- Work on a dedicated Phase 2 branch/PR; do not modify the ongoing Phase 1C draft PR or silently merge its unfinished contracts.
- First inventory existing Phase 1C implementations to avoid rebranding deterministic checks as AI agents.
- Establish typed agent input/output contracts, tool permissions, shared orchestrator state, evidence references, run identity, and failure handling.
- Implement one genuinely AI-assisted end-to-end deal assessment, then add specialist reasoning, bounded alternatives, verification, and affected-check reruns incrementally.
- Reuse existing PostgreSQL schema, evidence reader, and deterministic rules. Use stable fixtures or a narrow adapter when Phase 1C contracts remain unfinished; document dependencies instead of inventing production data.
- Prefer Python for backend and PostgreSQL for persistence. Evaluate LangGraph against the actual workflow before adoption. Keep the LLM provider replaceable, support low-cost/free development models where practical, and make tests run without paid model calls. Use Next.js for the eventual UI.
- Keep Credit and Policy separate. Recompute Approval Routing on the exact fully checked original/candidate.
- Do not expose independent evaluation answers or reviewer drafts to agents.

## Quality and traceability
Write unit/integration tests with deterministic mock-model behavior; run relevant checks and inspect CI. Record model and prompt versions, evidence IDs, rule references, tool calls, retries, errors, reruns, timing and cost where available. Never claim measured accuracy or superiority before accepted evaluation answers and actual comparative experiments.

Keep implementation, tests, setup instructions, architectural decisions and progress notes committed. Ask for user review only when materially changing approved architecture, business rules, or thesis scope; routine implementation can proceed.

## Reporting
For each meaningful increment explain, concisely, with one example deal: (1) business scenario, (2) evidence read, (3) what AI proposed, (4) what fixed rules verified, (5) what tests demonstrated, and (6) remaining work. Define unfamiliar terms. On 'continue', inspect the latest repository state and pick the next unfinished Phase 2 task.

## Read first
- `README.md`
- `phase-1b-agent-architecture/README.md`
- `phase-1b-agent-architecture/agent-architecture-and-deal-flow.md`
- `phase-1c-data/README.md`
- `phase-1c-data/implementation/phase1c_release_review.md`
- `phase-1c-data/phase1c_data_readiness_plan.md` (if present)
- `phase-1c-data/calibration-decision-sheet.md` (if present)

When files or paths differ, locate the current equivalents in the repository rather than assuming they exist.
