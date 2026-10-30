# Phase 1C accountable answer adjudication handoff — 30 October 2026

**Reviewer-only preparation; no accepted labels.** Original 36: 0/36; supplemental Configuration 039: 0/1; Credit controls 040–041: 0/2. The [fresh isolated PostgreSQL report](phase1c_postgres_verification_2026-10-30.md) verifies source import, reader selection, packet hashes and mutations. It does not establish expected six-specialist answers or reviewer independence. The [216-recommendation matrix](v3_six_responsibility_technical_matrix.md) is model-assisted, uses authored archetype navigation and has unadjudicated rule/action wording. Never place this handoff or completed answers in agent-visible inputs.

## Packet set and review order

| Cohort | Frozen facts for initial review | Candidate status |
| --- | --- | --- |
| Original 001–036 | Each exact v2 packet and separate provider file in `provisional_packet_index.json`, plus its *matching* `credit-evidence-v3/credit_scope_v3.json` row and `index.json` hash. The v3 Credit declaration is a fictional complete-zero population, not a real-world balance certificate. | 36 distinct provisional v3 inputs; all findings pending. Do not treat historical or 100 development outcomes as labels. |
| Configuration 039 | Separate `configuration-extension/v1/packet_index.json`, exported packet/provider and approved business contract. 037–038 are typed preflight diagnostics, outside the six-specialist denominator. | One supplemental candidate, separate from 36. The field's V2 dependency scope is technically dispositioned; the answer is not. |
| Credit 040–041 | `credit-evidence-v3/control_cases_v1.json`, source `index.json`, `control_packet_index_v1.json`, exported packet/provider and the trusted `classify_selected_packet` state. | Two separate controls, not added to original 36. 040 is complete/nonempty with EUR 700 overdue; 041 is incomplete/unknown with null overdue, despite empty selected rows. Neither is cleared or accepted. |

For **each** candidate, first verify its packet payload/self/index hash, provider-file hash, customer, deal, run, cutoff, catalogue and source-scope identity. For an original case also bind the v3 Credit row; the existing v2 review validator alone cannot establish that added source fact. Read the approved synthetic business contract and the *source rows before any proposed answer*. Record six separate findings (Configuration, Pricing, Availability, Credit, Policy, Approval), exact source and rule pointers, arithmetic, dated evidence, counterevidence, unknowns, human actions and the overall precedence gate. A hard blocker can coexist with subordinate evidence findings; a potential human route does not grant approval, reserve supply or promise delivery.

Then compare the source-first record to the [matrix](v3_six_responsibility_technical_matrix.json), [three batch aids](v2_batch_001_012_review.md), [039 draft](../configuration-extension/v1/reviews/model_assisted_039_draft.json), preserved original v2 model draft and author-assisted amendments. Log every agreement, disagreement and correction with provenance. For 020, Ali's conditional modal-route interpretation is a reviewed *business assumption* only; verify all six findings and the maximum-lead countercase. For 039, check missing add-on, quote-only scope, the other five specialists and blocked precedence separately. For 040, reconcile invoice/payment dates and EUR 700 outstanding. For 041, evaluate the appropriate Credit evidence-needed finding and actions from the trusted incomplete state; empty rows cannot establish zero exposure.

## Accountability and intake

A qualified human reviewer or supervisor must be named. Record their identity, expertise or role, timezone-aware review time, method, what packet/source version they examined, and whether they are the case author or used model assistance. If Ali reviews his own case, label it author review; do not call it independent validation. The reviewer may reject, request source changes, or propose a corrected answer. Any source change requires a *new input version and hashes* before adjudication; preserve v2, v3, draft and previous review records.

The existing `phase1c_evaluation_review.py` form and `phase1c_evaluation_acceptance.py` intake enforce six findings, resolvable pinned v2 source pointers, human provenance, a subsequent explicit disposition and assistance disclosure. They are **structural checks only** and do not attest independence or correctness. Because original v3 adds a separate Credit scope, the final intake must bind that scope and its hash in a versioned reviewer-only record before any v3 acceptance count changes. The supplemental 039 and 040–041 require their own separate intake records and source pins; do not reuse or silently enlarge the original 36-case intake. No completed form or acceptance is supplied by this handoff.

## Review queue and concrete dispute points

| Cases | First source question for the accountable reviewer |
| --- | --- |
| 001–012 | Fresh, allocated or stale stock versus confirmed/cancelled receipts and uncommitted offers; correct 009–010 draft wording about a cancelled receipt absent from those sources. |
| 013–020 | BOM substitution and distinct workshop steps; stale capacity; uncommitted earlier offer versus late PO. In 020, test the selected modal route and unsupported maximum-lead route separately. |
| 021–026 | Billed instance-month units versus concurrent capacity, matching provider proof and full anniversary coverage. |
| 027–030 | Regional service eligibility versus an actual booked slot; distinguish Configuration and Availability attribution for ineligible regions. |
| 031–036 | Credit cap, hard margin floor, legal-review clause and executable versus merely possible approval routes. |
| 039 | Exact V2 whole-deal required-product blocker; subordinate pricing, stock, credit and policy facts without inventing facts for the omitted add-on. |
| 040–041 | Nonempty overdue AR/payment reconciliation versus explicitly unknown invoice population; test that completeness comes from trusted pinned metadata, not empty selected rows. |

Acceptance remains pending until the reviewer signs case-level findings and dispositions, a separate check validates the source/scope bindings, disagreements are resolved, and the final release gates below pass.
