# Phase 2 Implementation and Evaluation Roadmap — M3–M9

**Approved planning baseline:** 4 November 2026. **Branch for implementation:** `phase2-agent-implementation`. **Purpose:** dated milestones and exit gates; do not treat targets as verified completion.

## Milestone execution

### M3 — Data and evaluation readiness (4–15 Nov) — P0

- [ ] Review all 36 held-out cases **source-first**, record six findings and overall gate per case, resolve disagreements and accept answers with accountable reviewer evidence.
- [ ] Resolve Phase 1C field-review marks, calibration decisions and source-provenance questions; freeze release inputs and conduct fresh double-build/hash/chronology/decision comparison.
- [ ] Confirm Phase 2 reader compatibility with accepted Phase 1C pin; approve changes explicitly, including any Credit v3 / controls 040–041 scope.
- [ ] Finish prospective campaign membership, preflight, authorization, start and receipt reconciliation, including preflight/no-send and uncertain-send denominators.
- [ ] Offline-test independent scorer, missing-aware timing/usage and matched deterministic baseline eligibility.
- **Exit evidence:** accepted answer register, release audit, compatible pin decision, offline evaluation readiness report.

### M4 — Core engineering closure (9–18 Nov) — P0

- [ ] Implement at most one separately checkpointed correction turn after a **fully returned, deterministically invalid and safely correctable** specialist final; new identity/receipt/budget and sanitized reason.
- [ ] Never correct/replay on uncertain sends, transport/timeout failures, source or subject mismatch, permission/budget stop; preserve original and fixed authority.
- [ ] Test invalid→valid, invalid→invalid, restart, tampering, identity, budgets and all six specialist stages.
- [ ] Investigate Configuration validation, Fulfillment HTTP 400, HTTP 429/quota failures without replaying historical attempts.
- **Exit evidence:** code/commit, negative tests, fresh PostgreSQL suite, documented remaining limitations.

### M5 — Enhancement review and scope freeze (16–22 Nov) — P1

- [ ] Review six specialist capabilities, orchestrator, evidence coverage, reviewer UX and candidate support.
- [ ] Classify enhancements **implement / defer / reject** with research value, safety, effort and measurability.
- [ ] Do not silently expand to WP4 source-writing/V2; obtain separate security/source-owner approval.
- [ ] Freeze optional functionality by **22 Nov**; record later change control.
- **Exit evidence:** approved enhancement register and feature-freeze decision.

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


## Dependencies

Accepted Phase 1C answers and compatible source pin → prospective campaign and scorer → approved hosted model pilot → frozen evaluation → measured results. The writing and thesis deliverables are tracked separately in [TODO.md](../TODO.md).
