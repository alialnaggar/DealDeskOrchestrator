# Phase 2 — Planning and implementation operating plan

**Status:** Agreed planning approach, not the completed technical blueprint. **Branch:** `phase2-agent-implementation`. **Source of truth:** this GitHub repository. Do not treat proposed file names, technology decisions or milestones as already implemented.

## Purpose
Build a comprehensive **Deal Desk Orchestrator — Phase 2 Master Implementation Blueprint**, potentially 50–80 pages if warranted by substance, before broad agent implementation. It must explain *what to build, why, interfaces, invariants, tests, acceptance criteria and forbidden behavior*. Do not generate a long one-shot document filled with assumptions. Develop sections iteratively from verified repository sources and user-approved decisions; keep it change-controlled, not frozen. Begin narrow implementation when interfaces and first milestone are sufficiently specified, rather than waiting for every document or Phase 1C dataset to finish.

## Responsibility and workspace map
| Workspace | Responsibility |
| --- | --- |
| ChatGPT | Planning, architecture workshops, learning, reviewing decisions, preparing blueprint sections |
| GitHub | Authoritative blueprint, agent specifications, source code, tests, decisions, progress, pull requests and CI |
| Oracle VM | Working repository clone, implementation, local tests, tooling; not authoritative until changes are pushed |
| Discord + Kimaki + OpenCode | Current remote conversational interface to coding agents on the VM; optional, not mandatory forever |
| Codex / Claude Code / free OpenCode models | Coding assistants operating on checked-out repository, subject to `AGENTS.md` instructions |

Do not confuse GitHub (versioned storage/review) with the interface used to instruct a coding agent. Keep Odoo and n8n infrastructure separate from thesis work. Audit VM Python, dependency, PostgreSQL, testing, capacity and model authentication readiness before changing infrastructure.

## Master blueprint content
**Part I — Foundations and boundaries:** thesis objectives/RQs, relevant Phase 1A findings, approved Phase 1B decisions, actual Phase 1C readiness, functional/nonfunctional requirements, scope, assumptions, success criteria.

**Part II — Technical architecture:** Python backend and project layout, component interfaces, LangGraph suitability decision, shared orchestration state, dependency and rerun logic, model/provider abstraction, PostgreSQL reader integration, Next.js UI, deployment boundaries.

**Part III — Six specialist specifications:** Configuration Validator; Pricing & Margin; Availability/Production/Fulfillment; Credit & Risk; Policy & Compliance; Approval Routing. For each: responsibilities, required inputs and typed outputs, evidence and tool access, deterministic versus LLM responsibilities, dependencies, proposals and prohibitions, failures, examples and tests. Include orchestrator specification separately.

**Part IV — Data and integration:** Phase 1C schema/reader/rules, dated evidence and frozen snapshots, immutable submitted deals, typed candidate variants, data validation and missing facts, stable/provisional interfaces, hidden evaluation-answer isolation.

**Part V — Governance, safety and evaluation:** no autonomous approval/waivers/reservations/delivery promises; deterministic hard-rule checks, evidence/rule IDs, audit logs, model/tool permissions, safe failure modes, reproducible evaluation, held-out answer keys, rule-only baseline, correctness, latency and cost.

**Part VI — Executable roadmap:** milestone dependencies, tasks and file targets, tests, acceptance gates, definition of done, CI, assistant/model routing, risks, fallback plans, handoff and completion checklist.

Include diagrams, state transitions, example deal traces, sample typed/JSON contracts, failure cases and test matrices where they add clarity. Avoid duplicating authoritative business rules: link to the governing Phase 1B/1C documents and version decisions.

## Document organization (proposal, subject to repository audit)
- `phase-2-implementation/master-implementation-blueprint.md` — authoritative comprehensive plan
- `phase-2-implementation/architecture/` — focused technical design, orchestration and contracts
- `phase-2-implementation/specifications/` — six agent specifications
- `phase-2-implementation/planning/implementation-roadmap.md`
- `phase-2-implementation/planning/task-backlog.md`
- `phase-2-implementation/planning/progress-tracker.md`
- `phase-2-implementation/planning/decision-log.md`
- `phase-2-implementation/evaluation/evaluation-plan.md`

Create only needed files after auditing existing locations. Define precedence: approved Phase 1B domain design and Phase 1C data/rules remain authoritative for their scopes; Phase 2 blueprint governs implementation choices consistent with them; task specs must not silently override higher-level decisions. Record proposed changes and seek review for material conflicts.

## Six-stage blueprint-to-code workflow
1. **Repository audit:** verify branch/PR/CI; inspect current Phase 1A, Phase 1B, Phase 1C and existing Phase 2 code; classify each relevant component as approved, implemented, provisional or missing. Report reusable modules, Phase 1C blockers, first viable end-to-end slice and unresolved decisions. No invented status.
2. **Architecture workshops:** settle remaining design choices with the user: agent contracts, orchestration state, tool interfaces, candidates/reruns, model abstraction, security, errors, tests and deployment.
3. **Write blueprint in sections:** use evidence from GitHub and approved decisions; include diagrams, contracts, examples and acceptance gates. Label unverified assumptions and unresolved questions.
4. **Independent review:** inspect contradictions, scope creep, gaps, complexity, data contract compatibility and alignment with thesis research/evaluation.
5. **Publish approved plan:** commit the master and supporting specifications to Phase 2 branch/PR; link them from `AGENTS.md` and this README.
6. **Milestone-based implementation:** assign bounded tasks to coding assistants; each task names specification, inputs, expected changes, tests, prohibited changes and completion criteria. Start with one narrow genuine AI-assisted assessment, then expand.

## Phase 1C dependency policy
Do **not** wait for the complete synthetic dataset or independently accepted evaluation answers to draft agent specifications or begin isolated coding. Before substantive integration, verify stable **deal input contract, dated evidence reader, deterministic rule interfaces, candidate proposal contract and trusted small fixtures**. Mark unfinished interfaces provisional and use narrowly scoped adapters/mocks. Phase 1C owns generation, schema, evidence quality, fixed business rules and independent answer preparation; Phase 2 consumes them for agents, orchestration and system evaluation. Never duplicate Phase 1C or silently merge its unfinished draft branch. Full integration and defensible performance claims require the final compatible data and independently verified evaluations.

## Everyday development and Git synchronization
At session start, the coding agent verifies repository/branch, runs `git status --short --branch` and `git fetch origin`, checks ahead/behind/divergence, and fast-forward pulls **only when safe** (clean working tree, appropriate tracking branch and no divergence). If there are local changes or divergence, preserve everything and report a reconciliation plan; never reset, force-push or discard work. Read `AGENTS.md`, current milestone, shared contracts and relevant specification before editing. GitHub edits made by ChatGPT or a person do not automatically appear on the VM; VM edits do not appear on GitHub until committed and pushed. Avoid simultaneous edits to the same branch by multiple assistants.

For each milestone: implement only approved scope; run relevant tests; summarize files, diff, results, assumptions and blockers; request approval before push or destructive operations; commit and push to approved branch; report SHA and CI. For substantial work prefer a feature branch and PR. Syncing Git does **not** sync installed packages, DB state, environment variables or services; manage those separately with reproducible instructions.

## Learning, progress and change control
Maintain roadmap (order/dependencies), progress tracker (status with commit/test evidence), decision log (options/rationale/approval/status) and a concise teaching explanation for each milestone. Explain with one example deal: business problem, evidence, AI action, fixed-rule verification, tests and remaining work. Keep the user able to defend the implementation independently. When implementation contradicts the blueprint, document the conflict, decide explicitly and version the blueprint rather than silently deviating.

## Immediate next action
**Stage 1: full Phase 2 readiness audit.** Verify current GitHub branch and existing code; read authoritative Phase 1B and latest Phase 1C contracts; identify ready/provisional interfaces, reusable implementation, open questions, first end-to-end slice, and VM readiness checks. Present the audit and decision list **before** drafting the full blueprint or making broad implementation changes.
