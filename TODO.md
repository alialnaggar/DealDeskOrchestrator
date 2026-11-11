# Thesis To-Do List — Deal Desk Orchestrator

**Updated:** 4 November 2026 · **Status:** working project-wide execution tracker · **Submission:** 5 January 2027 · **Defense:** 18–29 January 2027 (university schedule to reconfirm).

This is the **single front-door checklist** for remaining thesis work. It complements rather than replaces the authoritative phase-specific blueprints, decision logs, evaluation records, and actual test/CI evidence. Dates are targets. Check a task only after verifying its deliverable and recording the supporting commit or review evidence. Do not infer completion from a drafted plan.

**Priority:** P0 = blocks final evaluation/thesis; P1 = needed for quality and submission; P2 = optional and explicitly scope-controlled.

## Current verified baseline

- Phase 1A literature review: formatted Report 1 DOCX exists at [Phase 1A review](phase-1a-literature-review/review/Deal-Desk-Orchestrator-Literature-Review-Report-1.docx); final thesis integration and reference audit are pending.
- Phase 1C: 24-table schema, generated masters/history, reference fixtures, 100 diagnostic submissions, 36-deal development pilot, and 36 provisional held-out **inputs** exist; **0/36 independently accepted answers** at last verified checkpoint. Formal Phase 1C release is pending.
- Phase 2: M2.1 conditional engineering closure; substantial M2.2 offline integration, but **original M2.2 evaluation exit OPEN**. No measured final AI accuracy/superiority claim.
- Writing: [Chapter 3 synthetic-data methodology draft](phase-1a-literature-review/review/Chapter-3-Synthetic-Data-Methodology-Draft.md) created 4 November. It is **not yet integrated into the formatted Report 1 DOCX**.
- Existing [approved M3–M9 roadmap](#milestone-execution) moved here from the root README; historical [Phase 2 roadmap](phase-2-implementation/planning/implementation-roadmap.md) remains authoritative for its own historical milestones.

## Quick priority board

| Priority | Workstream | Immediate next deliverable | Target |
| --- | --- | --- | --- |
| P0 | Phase 1C independent answers | Source-first review and acceptance for 36 held-out cases | 15 Nov |
| P0 | Phase 1C release | Field/calibration decisions, frozen source and reproducibility audit | 15 Nov |
| P0 | M2.2 evaluation readiness | Prospective runner, scorer, denominators, timing, matched baseline | 15 Nov |
| P0 | Core engineering | Governed single correction turn and full six-stage negative/regression checks | 18 Nov |
| P0 | Model and formal evaluation | Approved paid model pilot, freeze, independent held-out campaign | 12 Dec |
| P1 | Thesis writing | Integrate LR + data methodology; architecture, implementation and methods drafts | Nov |
| P1 | Figures and references | Source-derived diagrams, captions, citation audit | Nov–Dec |
| P1 | Results and final submission | Evaluation results, limitations, supervisor review, formatting | 5 Jan |
| P1 | Defense | Presentation, demonstration, Q&A rehearsal | Jan |
| P2 | Enhancements | Only explicitly approved improvements before scope freeze | 22 Nov |

## Thesis document and writing tracker

### A. Source document and integration — P1

- [x] Draft Chapter 3 synthetic-data methodology as a source-grounded Markdown working chapter.
- [ ] **Integrate Chapter 3 into the existing formatted Report 1 DOCX**, preserve its exact heading styles, title/front matter, page numbers, citation format and existing LR text. **Blocked in this environment:** the private GitHub binary DOCX is visible but the GitHub connector cannot download its bytes; obtain a direct DOCX upload or a supported binary transfer. Do **not** claim the Word document is already updated.
- [ ] Save the combined Word file as **Updated Thesis with Data Methodology.docx** under `phase-1a-literature-review/review/` (or an approved final thesis location) after genuine integration; retain the original.
- [ ] Confirm thesis chapter numbering against the actual Report 1 headings before finalizing Chapter 3 numbering.
- [ ] Verify university thesis formatting/submission requirements and supervisor expectations; do not assume Report 1 format alone is final-thesis compliant.
- [ ] Update document revision history and source commit used for each chapter.

### B. Literature review and research framing — P1

- [ ] Audit every citation and claim in the existing LR against its cited paper; resolve missing references and placeholders.
- [ ] Check research gap, research questions, hypotheses/objectives and contribution wording against the final implemented scope.
- [ ] Remove duplicated background between LR, system architecture and methodology.
- [ ] Confirm consistent terminology: six fixed responsibilities, bounded specialists, deterministic authority, candidate, evidence, abstention, human review.
- [ ] Complete bibliography in the thesis's actual citation style.

### C. Data methodology — P1 (current draft exists)

- [x] Explain evidence freshness correctly: observations can be stale; technology products do not expire because of an observation rule.
- [x] Separate 14 reference fixtures, 400 historical submissions, 100 diagnostics, 36 connected development-pilot deals and 36 held-out evaluation cases.
- [ ] Audit exact counts, source schedules, configuration seeds, generated manifests and table relationships against the final Phase 1C release.
- [ ] Explain calibration/provenance and which values are fictional assumptions rather than real enterprise facts.
- [ ] Include source-first independent answer review protocol; update only with genuinely accepted cases.
- [ ] Insert figures and explanatory paragraphs; verify figure labels, source citations and consistency with actual schema.
- [ ] Update provisional status and limitations after the Phase 1C release audit.

### D. Architecture and implementation chapters — P1

- [ ] Write architecture chapter: six specialists, LangGraph orchestrator, immutable original, pinned reader, evidence boundary, deterministic verifier, candidate, human routing.
- [ ] Write implementation chapter: interfaces, state/checkpointing, tools/permissions, provider abstraction, budgets, replay prevention, typed finals, audit, error handling.
- [ ] Distinguish target design from implemented functionality and from deferred features; tie assertions to tests/commits.
- [ ] Provide one end-to-end worked example and explain its evidence and final review package.
- [ ] Explain ethical/governance constraints, privacy and why AI cannot approve/waive/commit.
- [ ] Describe deployment/demo environment only after it is actually verified.

### E. Experiment, results, discussion — P0/P1

- [ ] Write prospective evaluation protocol before hosted execution: case eligibility, source pin, prompt/model versions, baseline, denominators, scoring, statistical limitations.
- [ ] After independent authorization and actual execution, report specialist and end-to-end correctness, supported claims, abstentions, reliability, time, tokens and costs.
- [ ] Analyze failures and negative results without overstating performance.
- [ ] Write discussion, threats to validity, ethics, future work and conclusion grounded in measurements.
- [ ] Prepare abstract and executive summary **after** results are established.

### F. Figures, tables and visual evidence — P1

- [ ] **F1** Deal Desk data/decision authority diagram — original deal → pinned evidence → six fixed checks and bounded AI → human.
- [ ] **F2** Synthetic-data provenance/generation pipeline — public anchors versus assumptions, seeds, masters, history, dated evidence, validation.
- [ ] **F3** ERD derived directly from the 24-table `schema.sql`; simplified main figure plus full appendix.
- [ ] **F4** One illustrative deal and linked operational source packet, with timestamp/source IDs and clearly labeled invented example values.
- [ ] **F5** Evidence freshness and validity timeline; observation-age threshold versus commitment validity versus future data.
- [ ] **F6** Cohort separation and evaluation answer-key isolation (14/400/100/36 pilot/36 held-out).
- [ ] **F7** Original/candidate deterministic recheck and human decision boundary.
- [ ] **F8** Validation ladder from structural checks to independent formal evaluation.
- [ ] Architecture: LangGraph state/sequence diagram, six-specialist dependencies, tool/evidence permission boundary, checkpoint and uncertain-send failure path.
- [ ] Evaluation: study flow, outcome/error taxonomy, paired baseline comparison and actual results charts (only after scoring).
- [ ] Add captions, cross-references, legends, accessible labels and an explanation immediately after each substantive figure; avoid decorative or redundant graphics.

## Milestone execution

### M3 — Data and evaluation readiness (4–15 Nov) — P0

- [ ] Review all 36 held-out cases **source-first**, record six findings and overall gate per case, resolve disagreements and accept answers with accountable reviewer evidence.
- [ ] Resolve Phase 1C field-review marks, calibration decisions and source-provenance questions; freeze release inputs and conduct fresh double-build/hash/chronology/decision comparison.
- [ ] Confirm Phase 2 reader compatibility with accepted Phase 1C pin; approve changes explicitly, including any Credit v3 / controls 040–041 scope.
- [ ] Finish prospective campaign membership, preflight, authorization, start and receipt reconciliation, including preflight/no-send and uncertain-send denominators.
- [ ] Offline-test independent scorer, missing-aware timing/usage and matched deterministic baseline eligibility.
- **11 Nov engineering evidence (not M3 closure):** [IR2 offline evaluation-readiness report](phase-2-implementation/evaluation/m22-ir2-offline-evaluation-readiness-2026-11-11.md) documents mock-tested registry/unknown-start accounting, measured-only timing and post-run six-domain reviewer-label interface on the pinned source. External *independent* answer acceptance, authenticator, trust root/hosted authorization and actual comparison remain open; keep the M3 checkboxes unchecked.
- **Exit evidence:** accepted answer register, release audit, compatible pin decision, offline evaluation readiness report.

### M4 — Core engineering closure (9–18 Nov) — P0

- [ ] Implement at most one separately checkpointed correction turn after a **fully returned, deterministically invalid and safely correctable** specialist final; new identity/receipt/budget and sanitized reason.
- [ ] Never correct/replay on uncertain sends, transport/timeout failures, source or subject mismatch, permission/budget stop; preserve original and fixed authority.
- [ ] Test invalid→valid, invalid→invalid, restart, tampering, identity, budgets and all six specialist stages.
- [ ] Investigate Configuration validation, Fulfillment HTTP 400, HTTP 429/quota failures without replaying historical attempts.
- **11 Nov bounded implementation (M4 still open):** [Fulfillment correction safety and six-stage eligibility audit](phase-2-implementation/evaluation/m4-single-correction-engineering-2026-11-11.md) adds distinct source-bound correction IDs, restart tamper checks, elapsed measurement and strict shared no-send policy for the five unsupported stages. Full fresh PostgreSQL **365/365**; no new hosted correction capability. The three M4 checkboxes above remain open pending separately budgeted, receipt-bound safe paths for other specialists.
- **Exit evidence:** code/commit, negative tests, fresh PostgreSQL suite, documented remaining limitations.

### M5 — Enhancement review and scope freeze (16–22 Nov) — P1

- [ ] Review six specialist capabilities, orchestrator, evidence coverage, reviewer UX and candidate support.
- [ ] Classify enhancements **implement / defer / reject** with research value, safety, effort and measurability.
- [ ] Do not silently expand to WP4 source-writing/V2; obtain separate security/source-owner approval.
- [ ] Freeze optional functionality by **22 Nov**; record later change control.
- **11 Nov early M5 increment (not M5 closure):** [Six-specialist capability matrix and offline Credit fixed-exposure evidence](phase-2-implementation/evaluation/m5-specialist-capability-and-credit-2026-11-11.md). An offline Credit model may cite the already verified fixed amount alongside dated evidence; the hosted view, fixed decision and candidate scope are unchanged. Focused fresh PostgreSQL **17/17**, full fresh PostgreSQL **380/380**. Enhancement register, independent evaluation and feature freeze remain open.
- **Exit evidence:** approved enhancement register and feature-freeze decision.

### Supervisor feedback — Pydantic v2 contract standardization (P1; optional)

- [ ] Adopt **Pydantic v2 selectively** for six specialist input/output contracts, orchestrator-to-specialist typed interfaces, and structured LLM response schemas, subject to a compatibility and regression review.
- [ ] Inventory existing dataclass, JSON Schema and custom-validation boundaries; plan incremental migration that preserves provider-independent contracts, strict rejection behavior and backward compatibility.
- [ ] Retain deterministic evidence verification, permission/authorization checks, business-rule validation and approval authority outside Pydantic schema validation.
- [ ] Add equivalence/negative regression tests for accepted and rejected payloads, including malformed, extra-field and identity-mismatch cases; record the decision and implementation evidence before checking complete.
- **Source:** supervisor recommendation discussed 8 Nov 2026; optional, not mandated. **Scheduling:** evaluate within M5 enhancement review; implement only if compatible with P0 evaluation milestones and scope freeze. No existing validation is assumed migrated.

### M6 — Paid OpenAI model integration (20–29 Nov) — P0

- [ ] Choose exact paid OpenAI API model, cost ceiling and adapter; keep provider-independent contracts and deterministic authority.
- [ ] Test six specialist development cases, typed finals, tool boundaries, abstention and failure behavior **without exposing held-out answers**.
- [ ] Freeze prompt/model/contract/source/budgets and approve prospective hosted pilot separately.
- **Exit evidence:** adapter tests, provider configuration record, pilot receipts and explicit authorization.

### M7 — Formal evaluation (30 Nov–12 Dec) — P0

- [ ] Predeclare frozen cohort, accepted answers, model, source, scorer, correction policy, baseline and metrics before hosted execution.
- [ ] Run independently authorized prospective held-out experiment; preserve no-send, uncertain-send and completion denominators.
- [ ] Score six specialists and end-to-end workflow against accepted answers; measure unsupported claims, abstention, reliability, latency, usage and cost.
- [ ] Compare only supported same-case/same-source deterministic baseline capabilities; document all negative findings and limitations.
- [ ] Determine whether the **original M2.2 formal evaluation exit** is met; do not close it from offline tests alone.
- **Exit evidence:** immutable campaign manifest/receipts, scored report, limitations, signed-off milestone gate.

### M8 — Final system and demonstration (8–18 Dec) — P1

- [ ] Prepare stable release candidate, tag evaluated code and reproducible setup/operator instructions.
- [ ] Demonstrate six-specialist assessment, source citations, abstention/gaps, bounded candidate recheck, human routing, checkpoints and safe failure.
- [ ] Run fresh regression and document known limitations.
- [ ] Avoid unapproved scope creep into enterprise UI/ERP deployment.
- **Exit evidence:** tagged RC, demo script, setup guide, fresh test/audit report.

### M9 — Thesis submission and defense (parallel through 5 Jan; defense Jan) — P0/P1

- [ ] Finish and integrate all chapters and appendix material into a single thesis document.
- [ ] Insert verified figures/tables, citations, results and limitations; perform terminology and plagiarism/quotation checks.
- [ ] Obtain supervisor review; resolve comments; complete formatting and export checks.
- [ ] Submit thesis by **5 January 2027** (confirm official university instructions).
- [ ] Prepare defense presentation, demo backup and Q&A; rehearse for January defense window.
- **Exit evidence:** submitted thesis and presentation package.

## Critical path and coordination

**Accepted Phase 1C answers + compatible source pin → prospective campaign/scorer and authorization → paid-model pilot → frozen formal evaluation → analyzed thesis results → final submission.**

M3/M4 overlap; writing and figures run in parallel. If an external approval or API constraint delays evaluation, prioritize evidence integrity over optional features. No roadmap entry authorizes paid calls, source mutation, autonomous business approvals or rewriting the original deal.

## Weekly operating check

For each active task, log **owner · priority · status (not started/in progress/blocked/verified complete) · due date · last verified commit/CI/review · blocker · next action**. Revisit the P0 critical path weekly and after major source changes. Keep the technical phase-specific trackers in their existing locations; this file is the **cross-phase and thesis-writing master checklist**.

## Source navigation

- [Root project overview](README.md)
- [Phase 1A literature review](phase-1a-literature-review/README.md)
- [Current Chapter 3 methodology draft](phase-1a-literature-review/review/Chapter-3-Synthetic-Data-Methodology-Draft.md)
- [Phase 1C data and release review](phase-1c-data/README.md)
- [Phase 2 master blueprint](phase-2-implementation/planning/master-implementation-blueprint.md)
- [Phase 2 historical implementation roadmap](phase-2-implementation/planning/implementation-roadmap.md)
- [M2.2 evaluation readiness and exit gate](phase-2-implementation/evaluation/m22-wp5-evaluation-readiness-and-exit-gate-2026-11-01.md)
