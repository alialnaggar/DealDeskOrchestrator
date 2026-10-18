# Phase 2 architectural decision log

This log records decisions for the Phase 2 implementation blueprint. It does not override the approved Phase 1B business architecture or Phase 1C data and deterministic rules. A provisional approval establishes direction; interface and acceptance details still require workshop review.

## D1 — First AI contribution: bounded Fulfillment alternative

- **Status:** Provisionally approved by Ali, 18 October 2026. D2 (contracts and permissions) and D3 (Orchestrator lifecycle) remain under review. No agent implementation is authorized by this entry.
- **Decision:** The first AI-assisted milestone focuses on the Fulfillment specialist proposing and explaining a bounded alternative to an original deal, followed by deterministic verification. Start with the narrow 20-unit partial-delivery scenario, while designing contracts to accommodate broader fulfillment scenarios later. The specialist may return **no suitable alternative** if evidence is insufficient or customer constraints cannot be met.
- **AI contribution:** Consider verified options, explicit customer constraints, tradeoffs, uncertainty and whether any suitable alternative exists. The model must do more than restate a candidate already discovered by Phase 1C. Its proposal is an unverified hypothesis until fixed tools check it. The system preserves the original deal and distinguishes confirmed, conditional, unknown and infeasible outcomes.
- **Authority:** Deterministic Python tools remain authoritative for quantities, availability, dates, business rules and candidate validity. AI cannot approve a deal, waive rules, reserve stock, book production, promise delivery or convert conditional supply into confirmed supply. A human reviews the result and decides whether to pursue a revision.
- **Rationale:** A constrained alternative demonstrates specialist proposal work, evidence use and governed rechecking while keeping the first implementation small enough to test and explain. Whether it improves on deterministic discovery is an evaluation hypothesis, not a result.
- **Alternatives considered:** (1) Explanation of fixed results only: simplest integration, but does not adequately demonstrate substantive specialist contribution. It can remain a fallback when no safe candidate exists. (2) Six AI specialists and general candidate search immediately: covers the target design sooner but depends on too many unsettled interfaces and failure paths. (3) Model-proposed split without fixed recheck: rejected because unsupported dates, quantities or commitments could reach human review.
- **Phase 1C dependencies:** Pin a compatible structured deal input, dated evidence reader, fixed decision/rule interface, frozen run and selected-source identity, trusted development fixture, and typed candidate/recheck interface. The partial-delivery candidate, reader-backed correlation and trace on draft PR #1 (`phase1c-candidate-contract`, audited at `90c0bc8e285ee69262c7db826b786096a77ad004`) are **development experiments**, not a released general contract. The Phase 2 branch (`phase2-agent-implementation`, audited at `c8ded2e5b9ec9e615280464aa0660f4a3eed8249`) has diverged; reuse requires an explicit, tested integration approach. Do not modify Phase 1C or merge PR #1 by implication. Full performance claims wait for independently accepted evaluation answers (0/36 at audit).
- **Implementation impact:** D2 must specify minimal agent-visible facts, permitted reads/tools, proposal and abstention outputs, citations, uncertainty and fixed-validation rejection. D3 must specify candidate identity, reruns, stopping, comparison and human handoff. Start with one narrow scenario; broaden only with tests and compatible Phase 1C interfaces.
- **References:** `phase-1b-agent-architecture/agent-architecture-and-deal-flow.md`; `phase-2-implementation/README.md`; draft PR #1's `phase-1c-data/implementation/phase1c_candidate.py`, `phase1c_partial_discovery.py`, `phase1c_reader.py`, `phase1c_deal_decision.py` and `phase-1c-data/current-status.md`.

## Pending workshop decisions

| ID | Subject | Status |
| --- | --- | --- |
| D2 | Agent input/output contracts and tool permissions | Proposed during Workshop 1; not approved |
| D3 | Orchestrator lifecycle, state, failures and candidate reruns | Not yet reviewed |
