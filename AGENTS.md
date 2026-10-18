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

## AI coding model selection and cost policy (October–November 2026)
This section governs **development assistants working on this repository**, not the six specialist agents' production model choices. Model availability, limits and quality can change; these are provisional assignments, not benchmark-backed superiority claims.

- **October 2026:** Prefer authenticated subscription-based Codex for architecture decisions, typed contracts, implementing specialist agents and LangGraph coordination, complex debugging, integration, critical business-rule review, and final correctness checks. Do not assume ChatGPT subscription authentication is equivalent to OpenAI API credits.
- **November 2026 (planned):** If the user activates a Claude plan with Claude Code access, use Claude Code as the primary paid assistant for comparable complex tasks. Prefer Sonnet for routine substantial coding and Opus, when available and justified, for especially difficult architecture/review. Verify the actual subscription, usage limits, supported authentication path and model access before relying on it. Claude API usage is distinct from a Claude subscription.
- **Free OpenCode models:** Try GLM-5.3-Flash for narrow Python helpers, routine coding, simple bug fixes, tests and UI edits; DeepSeek V4.1 Flash for SQL and debugging alternatives; Nemotron 3 Ultra for repository comprehension, architectural critique and independent reviews. Big Pickle is a fallback for low-risk tasks. These are initial hypotheses to validate on repository-specific tasks, not guaranteed quality rankings. Free labels do not imply unlimited usage.
- **Task routing:** Use a free model first for bounded, reversible, low-risk changes; escalate to the paid assistant when cross-file reasoning, complex orchestration, uncertain contracts, repeated test failures or critical correctness is involved. Use an independent second-model review for changes involving configuration validity, margin, delivery commitments, credit, policy, approval routing, orchestration state or evaluation. Reviewers must not see hidden evaluation answer keys.
- **Quality gates:** No model's confidence substitutes for deterministic rules, fixtures, unit/integration tests, and CI. Require human review before materially changing approved architecture, thresholds, credit/policy rules or scope. Never let a model autonomously authorize deals, delivery commitments, financial actions or approvals.
- **Spending:** Prefer authenticated subscription coding tools where explicitly supported; do not add API keys, enable metered billing, switch to paid API providers, or trigger unexpected usage charges without explicit user approval. Record provider/model/version and approximate cost/usage where available; keep offline/mock-model tests viable.
- **Workflow and isolation:** GitHub remains the source of truth. Work on the Phase 2 branch or a dedicated feature branch/PR; inspect status before edits, run tests, summarize diffs and obtain approval for risky changes. Never touch the ongoing Phase 1C draft PR without authorization. Before changing assistants/months, commit and push agreed work, update README/progress/decisions, and leave a concise handoff describing open tasks, test status, contracts and blockers.
- **Oracle VM / Discord Kimaki:** The VM clone is a working copy, not authoritative storage. Keep work within the DealDeskOrchestrator project and its authorized test environment. Do not inspect or modify unrelated host directories, credentials, Docker containers, networks, volumes, or services (including existing Odoo and n8n). Do not restart, upgrade or reconfigure the VM or install system-wide dependencies without explicit approval. Discord bot commands are potentially powerful: restrict access to trusted users, avoid posting secrets, and request approval for destructive commands, pushes and deployments.

## Phase 2 planning authority and session synchronization
Before beginning substantial Phase 2 work, read `phase-2-implementation/README.md` for the agreed blueprint process, workspace roles, dependency boundaries, change control and first audit task. That document is a planning framework, **not** an approved completed technical blueprint. Do not create large specifications or implement broad agent features until the repository audit and necessary design decisions are reviewed.

At the start of a coding session, check the repository path, current branch and `git status --short --branch`; run `git fetch origin`, inspect tracking-branch divergence and use `git pull --ff-only` only when the working tree is clean and the branch can fast-forward safely. Preserve uncommitted work and unpushed commits; never auto-reset, force-push or discard conflicting changes. Before pushing, fetch/reconcile new remote commits, inspect the diff and test results, and request user approval. Report the commit SHA and remaining work. Git synchronization does not update database state, dependencies or services.

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
