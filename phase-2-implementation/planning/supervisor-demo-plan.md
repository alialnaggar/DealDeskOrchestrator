# Supervisor demonstration — feasibility and execution plan

**Status:** Planning baseline, not implemented. **Branch:** `feature/supervisor-live-demo` (branched from Phase 2 at `4de1e762f3bb6405f13b71bb28ec00a8115c7e25`). **Purpose:** demonstrate the richest genuinely supported end-to-end deal without modifying formal held-out evaluation cases.

## Evidence-backed scenario selection

**Provisional flagship: RC01/B01 development overlay.** The 31 October M2.1 integrated Credit report records one authorized Groq hosted run `GROQ-DEV-a0108d5c19b34178b612c2a2213a1b97` with six AI stages completed, one Fulfillment `fixed_checked` candidate, six candidate-subject fixed results, original-subject Credit AR/payment evidence, Policy/Routing continuation, and original review `needs_revision`. Candidate requires human acceptance; fixed supply is not a reservation. This is one historical development result, not a reproducibility estimate, formal accuracy, or successful approval. See `phase-2-implementation/evaluation/m21-integrated-credit-exit-gate-2026-10-31.md` and `phase-2-implementation/architecture/m21-original-after-candidate.md`.

**Important boundary:** The candidate is Fulfillment-specific; six specialist AI investigations are on the original subject, while the candidate gets six deterministic checks. Do not describe this as six candidate-specific AI reassessments. A prior B01 offline release demo uses scripted model doubles and a separate candidate thread; never present it as a live LLM run.

## Work packages (no hosted sends or paid calls authorized by this plan)

- [ ] D0: Audit actual RC01/B01 input, specialist results, candidate fields, runner entrypoint, source pins, model budgets and receipts; compare other development cases for richer supported outcomes. Select a scenario with exact evidence and record limitations.
- [ ] D1: Run offline preflight on disposable PostgreSQL only; establish one reproducible original → six specialists → optional Fulfillment candidate → six fixed candidate checks → human review path. Test no-candidate, abstention and fail-closed behavior.
- [ ] D2: Define minimal read-only/run-scoped Python API for fresh authorized assessments, statuses, sanitized trace and final review; no approval, reservation, mutation of source records or replay of uncertain attempts.
- [ ] D3: Build minimal Next.js presentation: deal intake/details, original evidence, six specialist statuses, findings/citations, candidate comparison, deterministic recheck, human handoff, trace with matching assessment ID.
- [ ] D4: Prepare OpenCode walkthrough of actual LangGraph graph, contracts, specialist tool boundaries, verifier, checkpoint/receipt behavior and logs; show backend and Next.js from the same assessment.
- [ ] D5: After separate provider authorization, run one *fresh* development-only hosted assessment with explicit budget, safe receipt, no replay and captured failure handling. Never reuse the 36 held-out answer keys.
- [ ] D6: Prepare a truthful offline model-double fallback, operator runbook and demonstration script. Label offline versus hosted output visibly.
- [ ] D7: Write a supervisor methodology draft, grounded in the existing literature review and `phase-1a-literature-review/review/Chapter-3-Synthetic-Data-Methodology-Draft.md`. Check overarching research-method terminology before adopting Design Science Research; cover research design, architecture, data provenance, implementation, independent answer review, prospective evaluation, baseline, limitations and work remaining.

## Definition of done

A supervisor can watch a **fresh, traceable** execution and inspect the same assessment in Next.js and OpenCode. It shows six original-subject specialist stages, real evidence-backed outputs or truthful abstentions/failures, optional supported Fulfillment candidate, all six fixed candidate checks, original/candidate differences and human-only review. The demo must not claim model superiority, approval, reservation, fully resolved candidate, or formal measured accuracy. A recorded prior run may be shown only as explicitly historical evidence, never as live execution.

## Integration and change control

All demo-specific changes remain on this feature branch until reviewed. Phase 1C stays separate; no cherry-pick/merge of unfinished Phase 1C draft without an explicit compatibility decision. Prefer existing backend/frontend conventions; inspect Next.js feasibility and required API design before implementation. Do not authorize Groq/OpenAI sends by merely merging or running the demo. M3/M4/M6/M7 critical-path work remains authoritative in root `TODO.md`. Pydantic v2 is a separate optional P1 migration, not a prerequisite for this demo.

## Tool ownership and collaboration protocol (approved 8 November 2026)

- **ChatGPT — project control, D0 scenario decision, architecture/review, academic methodology (D7), demo narrative, acceptance gates.** Verify repository evidence before recommending changes; do not equate documentation with runtime success.
- **Codex — sole primary implementation owner for D1–D3 and implementation aspects of D5–D6:** inspect/reproduce backend, write narrowly scoped API and Next.js code, run isolated tests, produce exact commands/commit SHAs/results and reviewable PR. Do not start hosted calls without separate authorization.
- **OpenCode — technical presentation and inspection (D4):** browse the actual LangGraph graph, contracts, evidence tools, deterministic verifier and checkpoints; inspect sanitized traces from the same assessment ID as Next.js. OpenCode is not itself an execution observability service. Read-only during Codex ownership; any future edits require explicit handoff.
- **GitHub — single authoritative source:** all work on `feature/supervisor-live-demo` until reviewed. One writer at a time; Codex must sync and check working tree before editing. No simultaneous modifications by OpenCode/ChatGPT/Codex to the same files. Review commits and test evidence rather than trusting assistant summaries.
- **Sequence:** ChatGPT D0 decision → Codex D1 offline reproducibility → review gate → Codex D2/D3 minimal API/Next.js → OpenCode D4 walkthrough → separately authorized D5 fresh hosted run → D6 rehearsal; ChatGPT drafts D7 methodology in parallel.
- **Change boundaries:** reuse existing LangGraph and Phase 1C pin; no production approvals, reservations, unsafe source mutation, held-out answers or unapproved paid/provider calls. Separate any generally reusable fix for review before merging into the main Phase 2 branch.

## D0 scenario acceptance matrix (preliminary)

| Requirement | RC01/B01 observed evidence | Next verification |
| --- | --- | --- |
| Six original-subject hosted specialist stages | One 31 October completed development run | Inspect exact per-stage returned findings, citations and receipts |
| Fulfillment candidate | One `fixed_checked` candidate | Inspect candidate values and whether proposal is intelligible to supervisor |
| Six candidate checks | Six deterministic checks, **not** six candidate AI reruns | Verify statuses, changed fields and source IDs |
| Credit evidence | Original AR/payment claims with exact linkage | Confirm visible business explanation and privacy-safe projection |
| Business result | Original `needs_revision`; candidate requires acceptance | Do not label candidate approved, resolved or production-ready |
| Repeatable fresh run | **Not established** | Offline disposable-DB rehearsal; later separately authorized hosted attempt |
| Presentation UI | **Not established** | Minimal Next.js + API feasibility, source-backed trace projection |

**D0 decision rule:** RC01/B01 remains provisional until exact case data and complete output shape are inspected; prefer an existing richer development case only if it is actually supported by source, safe to run and covers at least the same boundaries. Avoid constructing a new held-out-like case solely to force a green outcome.


## Future enhancement explicitly excluded from minimum demo

The user requested that the long-term architecture remember **several specialist recommendations and incremental V0→V1→V2 candidates**. The master blueprint and implementation roadmap now track this as an **M5 decision gate**, not implemented functionality. The supervisor demo remains six original-subject AI investigations plus at most one Fulfillment binding candidate with six fixed candidate checks; no candidate-specific AI loop or automatic multi-specialist proposal composer is currently available. Do not inflate the demo's scope or falsely describe the current candidate as a composite multi-agent negotiated offer.
