# Phase 2 — Planning and implementation operating plan

**Status:** Workshops 1–3 and M1 integration decisions approved at their recorded levels; bounded M1.0–M1.9 implementation completed. The [living master blueprint](planning/master-implementation-blueprint.md) consolidates the approved design, measured implementation and future gates. Five AI specialist capabilities, frontend and deployment remain unfinished. **Branch:** `phase2-agent-implementation`. **Source of truth:** this GitHub repository. Distinguish completed milestones from proposed later work.

## Purpose
Build a comprehensive **Deal Desk Orchestrator — Phase 2 Master Implementation Blueprint**, potentially 50–80 pages if warranted by substance, before broad agent implementation. It must explain *what to build, why, interfaces, invariants, tests, acceptance criteria and forbidden behavior*. Do not generate a long one-shot document filled with assumptions. Develop sections iteratively from verified repository sources and user-approved decisions; keep it change-controlled, not frozen. Begin narrow implementation when interfaces and first milestone are sufficiently specified, rather than waiting for every document or Phase 1C dataset to finish.

## Responsibility and workspace map
| Workspace | Responsibility |
| --- | --- |
| ChatGPT | Planning, architecture workshops, learning, reviewing decisions, preparing blueprint sections |
| GitHub | Authoritative blueprint, agent specifications, source code, tests, decisions, progress, pull requests and CI |
| Oracle VM | Working repository clone, implementation, local tests, tooling; not authoritative until changes are pushed |
| Discord + Kimaki + OpenCode 2 | Proposed remote coding interface; [VM handoff](development/oracle-vm-discord-handoff.md) is a plan, not a deployed/verified service |
| Codex / Claude Code / free OpenCode models | Coding assistants operating on checked-out repository, subject to `AGENTS.md` instructions |

Do not confuse GitHub (versioned storage/review) with the interface used to instruct a coding agent. Keep Odoo and n8n infrastructure separate from thesis work. Audit VM Python, dependency, PostgreSQL, testing, capacity and model authentication readiness before changing infrastructure.

## Master blueprint content
**Part I — Foundations and boundaries:** thesis objectives/RQs, relevant Phase 1A findings, approved Phase 1B decisions, actual Phase 1C readiness, functional/nonfunctional requirements, scope, assumptions, success criteria.

**Part II — Technical architecture:** Python backend and project layout, component interfaces, LangGraph implementation design (framework selected in D3), shared orchestration state, dependency and rerun logic, model/provider abstraction, PostgreSQL reader integration, Next.js UI, deployment boundaries.

**Part III — Six specialist specifications:** Configuration Validator; Pricing & Margin; Availability/Production/Fulfillment; Credit & Risk; Policy & Compliance; Approval Routing. For each: responsibilities, required inputs and typed outputs, evidence and tool access, deterministic versus LLM responsibilities, dependencies, proposals and prohibitions, failures, examples and tests. Include orchestrator specification separately.

**Part IV — Data and integration:** Phase 1C schema/reader/rules, dated evidence and frozen snapshots, immutable submitted deals, typed candidate variants, data validation and missing facts, stable/provisional interfaces, hidden evaluation-answer isolation.

**Part V — Governance, safety and evaluation:** no autonomous approval/waivers/reservations/delivery promises; deterministic hard-rule checks, evidence/rule IDs, audit logs, model/tool permissions, safe failure modes, reproducible evaluation, held-out answer keys, rule-only baseline, correctness, latency and cost.

**Part VI — Executable roadmap:** milestone dependencies, tasks and file targets, tests, acceptance gates, definition of done, CI, assistant/model routing, risks, fallback plans, handoff and completion checklist.

Include diagrams, state transitions, example deal traces, sample typed/JSON contracts, failure cases and test matrices where they add clarity. Avoid duplicating authoritative business rules: link to the governing Phase 1B/1C documents and version decisions.

## Document organization (proposal, subject to repository audit)
- [`planning/master-implementation-blueprint.md`](planning/master-implementation-blueprint.md) — living implementation map with actual-versus-target status
- `phase-2-implementation/architecture/` — focused technical design, orchestration and contracts; [Workshop 1 baseline](architecture/workshop-1-architecture-baseline.md)
- `phase-2-implementation/specifications/` — six agent specifications
- [implementation roadmap](planning/implementation-roadmap.md)
- `phase-2-implementation/planning/task-backlog.md`
- `phase-2-implementation/planning/progress-tracker.md`
- [decision log](planning/decision-log.md)
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

## Workshop 1 result and technology governance

The [decision log](planning/decision-log.md) records D1 (bounded Fulfillment AI proposal), D2 (versioned specialist contracts and restricted tools), D3 (LangGraph Orchestrator, Configuration-first execution, frozen run and candidate isolation) as **provisionally approved**. [Workshop 1 architecture](architecture/workshop-1-architecture-baseline.md) separates the complete target design from the narrow first milestone. LangGraph is the selected orchestration framework from M1; ordinary Python owns fixed business logic. M1.1 implemented sequential original-assessment nodes and PostgreSQL checkpointing. Candidate transitions and concurrency remain later work. Do not substitute a custom Python state machine for LangGraph.

Before changing, replacing, removing or materially expanding an agreed technology, framework, library, database, model provider, development tool or infrastructure component, present the current agreement, proposal, need, alternatives, architecture/implementation/cost/learning implications and recommendation; obtain Ali's explicit approval. Normal details within approved tools need no repeated approval unless they materially alter architecture or create meaningful cost/security implications. LangGraph does not itself authorize other infrastructure or paid APIs. Record approved changes in the decision log.

## Immediate next action

M1.9 Groq-only contract repair and 16-case Phase 1C compatibility comparison are completed; the [final full CI](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39803289084) passed 85 tests without skips after Gemini active code/workflows were removed. Review the [master blueprint](planning/master-implementation-blueprint.md) and [VM/Discord setup plan](development/oracle-vm-discord-handoff.md). The VM and Discord are not deployed by this documentation. M2.0 Configuration and Pricing AI requires a separate implementation approval. Historical M1.3–M1.8 decisions and experiments remain in the roadmap and linked reports.

## Workshop 2 result — LangGraph implementation design direction

[Workshop 2 technical specification](architecture/workshop-2-langgraph-state-evidence-and-transitions.md) and the [decision log](planning/decision-log.md) record W2.1–W2.4: typed authoritative assessment state with isolated specialist contracts; version-pinned evidence and controlled discovery; PostgreSQL-backed LangGraph checkpoints; and rule-controlled transitions with post-specialist validation, bounded candidate loops and safe human handoff. M1.0 now seals a pinned reader bundle and M1.1 checkpoints the original assessment in a disposable PostgreSQL database. Candidate transitions, tool signatures and conditional Phase 1C verification remain open.

Workshop 3 subsequently inspected the pinned Phase 1C interfaces and recorded its specialist contracts. Consult the actual M1 tests for implemented coverage.

## Workshop 3 and focused M1 review

W3.1–W3.8 are approved directions in the [decision log](planning/decision-log.md); Workshop 3 is closed at that level. The broad Workshop 4 is replaced by the focused [M1 contract and integration specification](architecture/m1-contract-and-integration-spec.md). Ali approved two pinned checkouts and a sealed, versioned reader bundle with checked candidate rereads on 19 October 2026. The exact Phase 1C pin, alternatives, compatibility gaps, acceptance tests and implementation sequence are recorded there. A conditional 12+8 candidate cannot be called verified under the pinned Phase 1C interface. Subsequent separate approvals authorized bounded M1.0–M1.3 coding; no Phase 1C merge/edit, paid model or VM change was authorized.

## Implemented M1 boundaries and current handoff

- [Living master blueprint](planning/master-implementation-blueprint.md): six responsibilities, LangGraph lifecycle, fixed/AI authority, candidate/review contracts, evaluation tiers, Next.js plan and remaining approval gates.
- [Backend evidence](backend/README.md): read-only exact Phase 1C pin, sealed bundle, six **deterministic responsibility mappings from one aggregate decision**, PostgreSQL restart, three Fulfillment tools, typed claims and narrow binding candidate verification. Only Fulfillment has live AI reasoning; do not call the other five AI agents implemented.
- [M1.4 historical Groq/Gemini experiment](backend/benchmarks/m1.4-gated-smoke-results.md) remains for reproducibility. Gemini is **discontinued** as an active development LLM; Groq `openai/gpt-oss-120b` is the provisional runtime provider, not a proven quality winner.
- [M1.8 pilot](evaluation/m1.8-measured-results.md) recorded four malformed candidate outputs. [M1.9 results](evaluation/m1.9-contract-and-output-results.md) document the Groq-only prompt repair, read-only two-checkout compatibility measurement, 89-test PostgreSQL CI and two more live trials: one abstention, one incorrect 11+18 candidate rejected by the pinned verifier. There is no demonstrated AI discovery improvement over the fixed baseline.
- [Roadmap](planning/implementation-roadmap.md) records M2.0 Configuration/Pricing and M2.1 Credit/Policy/Routing as **proposed, unapproved implementation**. The conditional 20-unit 12+8 supplier-offer path is not binding verified.
- [Oracle VM, OpenCode 2, Kimaki/Discord guide](development/oracle-vm-discord-handoff.md) is prepared for review. No VM/Discord deployment or M2.0 coding follows from it automatically.

Continue with a focused user approval of the VM setup and the later M2.0 scope, while keeping the Phase 1C pin and human approval boundaries intact.
