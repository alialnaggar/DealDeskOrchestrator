# Thesis To-Do List — Deal Desk Orchestrator

**Updated:** 4 November 2026 · **Status:** project-wide non-roadmap checklist. See separate dated roadmaps for milestone targets.

This is the **single front-door checklist** for remaining thesis work. It complements rather than replaces the authoritative phase-specific blueprints, decision logs, evaluation records, and actual test/CI evidence. Dates are targets. Check a task only after verifying its deliverable and recording the supporting commit or review evidence. Do not infer completion from a drafted plan.

**Priority:** P0 = blocks final evaluation/thesis; P1 = needed for quality and submission; P2 = optional and explicitly scope-controlled.

## Current verified baseline

- Phase 1A literature review: formatted Report 1 DOCX exists at [Phase 1A review](phase-1a-literature-review/review/Deal-Desk-Orchestrator-Literature-Review-Report-1.docx); combined three-chapter working DOCX generated locally, but not yet published to GitHub; reference audit remains pending.
- Phase 1C: 24-table schema, generated masters/history, reference fixtures, 100 diagnostic submissions, 36-deal development pilot, and 36 provisional held-out **inputs** exist; **0/36 independently accepted answers** at last verified checkpoint. Formal Phase 1C release is pending.
- Phase 2: M2.1 conditional engineering closure; substantial M2.2 offline integration, but **original M2.2 evaluation exit OPEN**. No measured final AI accuracy/superiority claim.
- Writing: [Chapter 3 synthetic-data methodology draft](phase-1a-literature-review/review/Chapter-3-Synthetic-Data-Methodology-Draft.md) created 4 November and integrated into a locally generated combined DOCX. **The combined binary file has not been committed to GitHub**; diagrams and final thesis checks remain pending.
- The [approved M3–M9 roadmap](roadmaps/phase2-m3-m9-roadmap.md) is maintained separately from this checklist.

## Current cross-phase triggers

- **Once Phase 1C cases are independently accepted:** update the methodology release status, then enable formal held-out scoring preparation.
- **Once a frozen hosted campaign has actually run and been scored:** write results, discussion, performance figures and conclusions.
- **Once the original LR DOCX is integrated with Chapter 3:** review formatting, headings, references and figure placements.
- **Once architecture and implementation scope is frozen:** finalize their thesis chapters and diagrams.
- **Before submission:** supervisor review, citation audit, final export and verification.

## Thesis document and writing tracker

### A. Source document and integration — P1

- [x] Draft Chapter 3 synthetic-data methodology as a source-grounded Markdown working chapter.
- [x] **Integrate Chapter 3 into the uploaded formatted Report 1 DOCX** and render-check a local combined working file (4 November 2026). The generated DOCX is available as a conversation artifact, **not yet committed to GitHub**. Figure specifications are placeholders, not inserted diagrams.
- [ ] **Publish the verified combined Word file** as `Updated Thesis with Data Methodology.docx` under `phase-1a-literature-review/review/` on `main` using a binary-capable upload method; retain the original.
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
- [ ] **Trigger: Phase 1C release candidate available.** Audit exact counts, source schedules, configuration seeds, generated manifests and table relationships against the final release.
- [ ] Explain calibration/provenance and which values are fictional assumptions rather than real enterprise facts.
- [ ] Include source-first independent answer review protocol; update only with genuinely accepted cases.
- [ ] Insert figures and explanatory paragraphs; verify figure labels, source citations and consistency with actual schema.
- [ ] **Trigger: Phase 1C release audit completed.** Update provisional status and limitations using actual release evidence.

### D. Architecture and implementation chapters — P1

- [ ] **Trigger: architecture and scope frozen.** Write architecture chapter: six specialists, LangGraph orchestrator, immutable original, pinned reader, evidence boundary, deterministic verifier, candidate, human routing.
- [ ] **Trigger: core implementation and regression evidence available.** Write implementation chapter: interfaces, state/checkpointing, tools/permissions, provider abstraction, budgets, replay prevention, typed finals, audit, error handling.
- [ ] Distinguish target design from implemented functionality and from deferred features; tie assertions to tests/commits.
- [ ] Provide one end-to-end worked example and explain its evidence and final review package.
- [ ] Explain ethical/governance constraints, privacy and why AI cannot approve/waive/commit.
- [ ] Describe deployment/demo environment only after it is actually verified.

### E. Experiment, results, discussion — P0/P1

- [ ] Write prospective evaluation protocol before hosted execution: case eligibility, source pin, prompt/model versions, baseline, denominators, scoring, statistical limitations.
- [ ] **Trigger: independently authorized hosted evaluation completed and scored.** Report specialist and end-to-end correctness, supported claims, abstentions, reliability, time, tokens and costs.
- [ ] Analyze failures and negative results without overstating performance.
- [ ] Write discussion, threats to validity, ethics, future work and conclusion grounded in measurements.
- [ ] **Trigger: results and discussion finalized.** Prepare abstract and executive summary.

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

## Final thesis submission and defense — P0/P1

- [ ] **Trigger: all substantive chapters drafted.** Assemble the complete thesis, appendices, table of contents, figure/table lists, glossary if needed, and reproducibility references.
- [ ] **Trigger: diagrams and results finalized.** Check every cross-reference, caption, figure numbering, table numbering and claim against its source or measured evidence.
- [ ] **Trigger: complete draft ready.** Obtain supervisor review and resolve feedback with a documented revision log.
- [ ] **Trigger: supervisor feedback resolved.** Perform citation/bibliography audit, formatting, proofreading, pagination and DOCX/PDF export inspection.
- [ ] **Before official submission deadline.** Verify university submission requirements and submit the final artifact; retain submission confirmation.
- [ ] **Trigger: evaluation/demo release candidate stable.** Prepare defense slides, demonstration script, screenshots/video fallback and likely examiner questions.
- [ ] **Before defense.** Rehearse presentation timing and technical questions; verify demo environment and offline backup.

## Roadmaps (separate dated plans)

- **[Phase 2 M3–M9 roadmap](roadmaps/phase2-m3-m9-roadmap.md)** — dated milestones, implementation and evaluation gates, exit evidence.
- [Historical Phase 2 implementation roadmap](phase-2-implementation/planning/implementation-roadmap.md) — original technical planning record.
- [Phase 1C data release review](phase-1c-data/implementation/phase1c_release_review.md) — source-specific readiness and release gates; add a dedicated dated roadmap only if needed.

**Separation rule:** This TODO file contains cross-phase actionable tasks, including writing and diagrams. Dates and milestone sequencing belong in roadmaps. Tasks without a meaningful deadline should instead specify their **trigger/dependency**.

## Critical path and coordination

**Accepted Phase 1C answers + compatible source pin → prospective campaign/scorer and authorization → paid-model pilot → frozen formal evaluation → analyzed thesis results → final submission.**

M3/M4 overlap; writing and figures run in parallel. If an external approval or API constraint delays evaluation, prioritize evidence integrity over optional features. No roadmap entry authorizes paid calls, source mutation, autonomous business approvals or rewriting the original deal.

## Operating check

For each active task, log **owner · priority · status (not started/in progress/blocked/verified complete) · due date · last verified commit/CI/review · blocker · next action**. Review tasks when their prerequisites change and at project checkpoints; use dated roadmaps for scheduling. Keep the technical phase-specific trackers in their existing locations; this file is the **cross-phase and thesis-writing master checklist**.

## Source navigation

- [Root project overview](README.md)
- [Phase 1A literature review](phase-1a-literature-review/README.md)
- [Current Chapter 3 methodology draft](phase-1a-literature-review/review/Chapter-3-Synthetic-Data-Methodology-Draft.md)
- [Phase 1C data and release review](phase-1c-data/README.md)
- [Phase 2 master blueprint](phase-2-implementation/planning/master-implementation-blueprint.md)
- [Phase 2 historical implementation roadmap](phase-2-implementation/planning/implementation-roadmap.md)
- [M2.2 evaluation readiness and exit gate](phase-2-implementation/evaluation/m22-wp5-evaluation-readiness-and-exit-gate-2026-11-01.md)
