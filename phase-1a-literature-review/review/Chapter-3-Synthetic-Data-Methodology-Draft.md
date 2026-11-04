# Chapter 3 — Synthetic Data Methodology

**Working thesis chapter — 4 November 2026.** This chapter documents the implemented Phase 1C method, not a finalized dataset release or measured AI accuracy. Source of truth: `phase1c-candidate-contract` (Phase 1C) and the approved Phase 2 roadmap. Figure callouts are **specifications for figures to insert into the formatted thesis document**, not claims that figures already exist.

## 3.1 Research setting and methodological objective

The Deal Desk Orchestrator addresses enterprise sales proposals that require coordinated assessment of product configuration, pricing and discounting, availability/production/fulfillment, customer credit and risk, policy compliance, and approval routing. These are not independent classification problems: a configuration change may alter component demand and price, while a feasible delivery alternative can still violate a credit constraint or require human approval. Accordingly, the research requires a relational business environment in which the same deal is assessed against consistent, traceable evidence across all six responsibilities.

The **unit of analysis** is a submitted deal, potentially containing several deal lines. A distinct assessment run (`deal_run`) fixes the assessment cutoff (`as_of_at`), applicable catalogue and policy context, and data-snapshot reference. The distinction matters because the submitted request must not be silently rewritten when new evidence appears or an alternative is proposed. The dataset is designed to enable reproducible deterministic assessment and later comparison with bounded AI-specialist findings; it is **not** an independently observed sample of enterprise transactions.

**Figure 3.1 — Business evidence and decision boundary (to insert).** Show a submitted deal feeding a versioned, cutoff-aware evidence reader; draw separate inputs for catalogue/BOM, pricing/policy, inventory/inbound/capacity, credit/AR, and provider/service evidence. The reader feeds six deterministic responsibility findings and a human-review gate. Draw AI specialists alongside the fixed findings, with dashed explanatory/proposal arrows, not authority to approve. *Interpretation:* the separation prevents a salesperson's assertion or an AI suggestion from being treated as authoritative business proof.

## 3.2 Synthetic-data design and provenance

A fictional enterprise technology provider was modeled because the study requires mutually consistent customer, product, credit, stock, supplier, production and policy records. The construction approach combines **seeded generation**, **declared business constraints**, and **deliberately designed positive, negative and boundary cases**. It does not claim that the generated distributions reproduce any named company's operational frequencies.

Three provenance classes are maintained. First, documented public reference anchors inform the plausibility of selected product families, attributes and broad price ranges; they do not supply private costs, supplier commitments or actual sales transactions. Second, configuration files declare fictional experimental assumptions such as counts, allocation patterns, commercial thresholds, capacities, observation schedules and sensitivity profiles. Third, SQL/JSON/YAML generators produce the synthetic master, transactional and operational records. The baseline, lenient and strict commercial profiles are **sensitivity settings**, not empirically established industry policies. Calibration decisions about detailed component fit and comparable price/cost basis remain provisional and must be recorded as such.

The base generation seed is **22495**, with documented offsets for individual renderers (including customer allocation using `seed + 801` and historical inputs using `seed + 400`). The versioned code, configuration, generated manifests and SHA-256 digests support repeatability. A matching digest verifies artifact identity, **not** realism, independence or correctness.

**Figure 3.2 — Generation and provenance pipeline (to insert).** Public reference anchors and explicit fictional assumptions feed calibration/configuration; these feed catalogue/customer generation and, separately, historical transactions and dated evidence; the resulting relational fixtures enter PostgreSQL and validation. Mark provenance categories on arrows. *Interpretation:* public references inform selected parameters but are not represented as direct enterprise observations.

## 3.3 Relational model and master data

The implemented PostgreSQL schema contains **24 tables**, governed by typed data contracts and column rules. These organize product and component definitions, customers, deal submissions and lines, business rules, operational source records and assessment/execution-related records. Foreign keys, typed structured fields and effective-date constraints protect the relationships used by the reader. The chapter deliberately describes **logical groups** rather than inventing a complete table-by-table mapping; the final entity-relationship figure should be generated from `phase-1c-data/implementation/schema.sql`.

The provisional V1 catalogue comprises **156 products: 120 sellable and 36 components**. Sellable offerings cover five fulfillment modes: stocked finished goods, supplier-sourced finished goods, make-to-order items, digital activation, and scheduled services. Make-to-order offerings depend on declared bills of materials (BOMs) and configuration rules. Structural validation of a BOM is not equivalent to manufacturer-certified technical compatibility; the detailed sourcing/fit of some variants remains a documented limitation. The project also uses two scoped V2 copies for dependency-rule regression, not as additional V1 market comparables.

The customer master comprises **80 fictional customers**. Customer segment, industry, country, risk/status and terms follow configured category counts and seeded allocation; credit limits use a bounded triangular draw. These are controlled experimental distributions. They should not be described as observed market statistics.

**Figure 3.3 — Relational entity-relationship diagram (to insert).** Derive the diagram from the actual 24-table schema. For readability, show a main diagram of deals, lines, customers, products, BOMs, runs and source evidence; put a full-schema diagram in an appendix. *Interpretation:* the primary key/foreign-key links establish which evidence can be joined to a particular deal and run.

## 3.4 Historical transaction and operational evidence construction

The historical input renderer generated **400 synthetic deal submissions containing 1,200 lines**, preceding the designated 1 September 2026 evaluation date. It uses exact line-count quotas, weighted product allocation and customer cycling. At input generation, these are submissions, not already accepted decisions. Separate renderers then construct dated evidence and queued baseline assessment runs at recorded cutoffs. The observed historical deterministic decisions are development diagnostics, not independently accepted answer labels.

Operational evidence is deliberately represented outside the salesperson submission. Inventory observations specify dated stock and allocations; supplier records distinguish offers, confirmed purchase orders, inbound receipts, delays and cancellations; workshop sources specify components and finite represented capacity; digital-provider sources include pool availability and separate full-term proof; credit sources include commitments, receivables and payment context; shipping and service sources express lanes or eligibility. These channels are **independently generated within the simulation**, not real supplier or provider attestations.

The provisional historical operational source includes **daily dated stock for 48 products**, **38 standard shipping lanes**, and **54 supplier/component offer SKUs** across the 400 assessment cutoffs. Other source classes use their own schedules and validity rules. A feasible production path does not book a workshop slot; a shipping option does not reserve delivery; service-region eligibility does not book an appointment.

**Figure 3.4 — Example evidence packet (to insert).** Draw one fictional submitted deal with a requested date and quantity, then link it to separate inventory, supplier, workshop, credit, policy and shipping/provider records. Label each record with source ID, observation/validity time and status. *Interpretation:* the evidence graph illustrates why a deal-supplied reference alone cannot establish a binding commitment. All displayed numbers should be labeled illustrative unless copied and checked against a pinned repository case.

## 3.5 Temporal validity: freshness, expiry and historical replay

The evidence reader selects facts visible at the assessment cutoff (`as_of_at`); a later observation cannot retroactively support an earlier deal. It also distinguishes **observation freshness** from **commitment validity** and from **product lifecycle**. For instance, a workstation does not expire after two days, but a two-day-old inventory observation may be insufficient to confirm the stock currently unallocated, because intervening transactions can change available quantity. This is a configured fictional operational control, **not** a universal technology-industry expiry rule.

The implementation includes a **two-day stock-observation freshness boundary** exercised by negative-stock regression cases. For the historical source, daily dated stock observations were generated for 48 products, providing more frequent observations than that boundary in the modeled coverage. This does **not** mean that every product and every assessment is guaranteed fresh: some cases deliberately provide stale or missing records to test whether the system preserves uncertainty. The diagnostic batch includes four deliberately stale-stock variations whose observations exceed the two-day limit, and allocated-stock variants in which on-hand stock equals allocated stock, leaving zero free quantity.

Other evidence types have distinct schedules and rules. A historical credit-source cadence mismatch initially made many observations stale under a 24-hour credit rule; the provisional source was adjusted to a daily schedule with 85% capture, yielding both fresh and stale views. The supplier pipeline was represented with weekly observations and separately configured confirmation validity; digital-provider proof must cover the specified quantity and full quoted term. A component receipt beyond the represented workshop-capacity horizon does not establish a later production slot.

**Figure 3.5 — Temporal evidence timeline (to insert).** Draw a deal cutoff at Thursday 12:00, a valid inventory observation within the configured window, an older stale observation, and a future observation. Use separate bars for a supplier offer's validity and a digital provider's coverage period. *Interpretation:* freshness governs whether an observation can support a present claim; expiry/coverage governs whether a documented commitment applies. Neither is the physical product's expiry date.

## 3.6 Development fixtures and diagnostic regression design

The methodology uses different cohorts for different engineering questions; their counts should not be added into a single independent sample size.

**Fourteen isolated reference scenarios** are focused fixtures for data contracts, reader behavior and selected fixed business rules. A narrow example is a stock record whose allocated quantity exhausts on-hand inventory: the rule must not report those units as free. Their purpose resembles unit-level regression, not model evaluation.

The **100-submission diagnostic batch** is a broader stress/regression cohort, constructed by varying **20 development templates** with bounded changes to quotes, customers and selected operational evidence. It contains **101 lines** and **55 distinct customers**. The scenario matrix uses the 18 V1 archetypes plus scoped V2 dependency pass/conflict cases; controlled variations exercise stock, supply, production, digital proof and commercial constraints. The provisional deterministic gate distribution was **23 approval_required, 12 blocked, 11 needs_commitment, 37 needs_evidence, and 17 needs_revision**. These are **observed outputs**, not independently reviewed correct answers or approvals. Reused templates and source states mean the 100 submissions cannot be described as 100 independent operating situations.

Reference fixtures test specific behaviors; diagnostic submissions test whether those behaviors remain consistent across controlled variants and interactions. Neither is the final held-out performance dataset.

## 3.7 Separate held-out evaluation construction

The evaluation design declares **18 business archetypes**, each with **two variants**, for **36 provisional evaluation inputs**. They cover three stock cases (ready, allocated, stale), three supplier cases (confirmed, offer-only, cancelled), four build cases (ready, substitute, stale capacity, beyond horizon), three digital cases (proved, missing proof, expired proof), two service cases (covered, outside), and three cross-cutting commercial cases (credit limit, price floor, policy clause).

The renderer `render_phase1c_evaluation_cases.py` constructs new deal, run, customer/credit and case-owned operational identities directly from the declared V1 synthetic context, **without reading development or historical submissions or their operational ledgers**. It uses controlled variant quantities and quote multipliers, and separate source evidence. The same five selected sellable SKUs, catalogue/BOM assumptions, policy and canonical location codes remain shared context. Cases are loaded one at a time in disposable PostgreSQL contexts, and development/historical exclusion registries check selected operational source IDs. Two identical source-only reader exports and a pinned packet index test reproducibility and isolation.

The evaluation cohort is methodologically different from the development pilot because it is reserved for later **prospective scoring against separately reviewed expected answers**. The authoring manifest is reviewer-only; agent-visible inputs must not contain scenario labels or answer keys. Independent reviewers must inspect each case's six domain findings, source citations, uncertainty and human-review requirements. At the documented checkpoint, **36 inputs were authored but 0/36 answer sets were independently accepted**. Distinct IDs and new operational rows do not prove statistical or semantic independence: the same author knew the archetypes and only five sellable SKUs were used.

**Figure 3.6 — Dataset-cohort separation (to insert).** Draw shared fictional catalogue/policy at the top, then separate branches for isolated reference fixtures, 400 historical inputs, 100 diagnostic variants, 36 connected development-pilot deals and 36 separately authored held-out cases. Only the held-out branch leads to independent source-first answer review and final AI/baseline scoring. *Interpretation:* shared business context is not the same as copying operational evidence or accepted labels.

## 3.8 Deterministic verification and bounded candidate support

Phase 1C includes a cutoff-aware reader and deterministic decision layer. It provides fixed, auditable findings that AI specialists may explain or use when proposing alternatives; the model does not replace fixed verification. A bounded candidate mechanism preserves the original deal and represents a proposed alternative separately. The same frozen source context is reread, the candidate's supported quantities/dates are checked, and the six fixed responsibility outcomes are recomputed for the candidate subject. Original unmet requirements, such as the requested delivery date, remain visible; a human must accept any change.

This mechanism is part of the **data and verification foundation**, rather than proof that the Phase 2 AI agents have independently solved the candidate or that an alternative has been reserved or approved. Its scope is deliberately limited and should not be generalized to arbitrary candidate search.

**Figure 3.7 — Original-versus-candidate verification (to insert).** Show an original request, an optional AI-proposed alternative, a common pinned source reader, fixed original/candidate checks and a human comparison. Use a two-slice delivery illustration (eight now, two later) only as a clearly labeled example. *Interpretation:* a candidate may improve a constraint without satisfying the original date or authorizing delivery.

## 3.9 Connected development pilot and validation

The **36-deal connected development pilot**, containing **65 deal lines**, exercises interactions across five fulfillment modes and business conflicts. Unlike the held-out 36 evaluation cases, it was available for implementation, debugging and repeated adjustment; its deterministic observations therefore constitute **development/integration evidence**, not independent final evaluation. Placing it here reflects its role as a validation instrument after the model, sources and scenario-generation method have been explained.

Validation includes PostgreSQL type and relationship checks, typed JSON/field contracts, effective dates, source references, temporal selection, deterministic decision regression, scenario-specific negative controls, and reproducibility of generated source packets. Disposable or rollback-only database runs reduce cross-test contamination. For held-out authoring, the project also checks source identity exclusions and per-case packet replay. These tests support specific structural and procedural claims, but cannot by themselves establish the realism of fictional records or the correctness of independently unreviewed answers.

**Figure 3.8 — Validation ladder (to insert).** Show schema/contract validation → isolated reference checks → historical as-of replay → 100 diagnostic regressions → connected development pilot → separate held-out source construction → independent answer review (pending) → formal AI/baseline evaluation (future). *Interpretation:* engineering regression and scientific performance evaluation are separate evidence levels.

## 3.10 Readiness, limitations and implications for evaluation

At the documented checkpoint, the 24-table schema, V1 masters, historical inputs and evidence, reference fixtures, 100 diagnostics, connected development pilot and provisional 36 held-out inputs existed. **Phase 1C was not formally released.** The source records still identify outstanding field-owner and calibration decisions, source-provenance/distribution review, 36 independent answer acceptances, and final fresh regeneration/replay/release checks. Actual specialist execution logs must arise from genuine execution, not fabricated synthetic source rows.

Threats to validity include fictional commercial assumptions, incomplete detailed product fit/price calibration, deliberately narrow archetype and SKU coverage, author familiarity with scenario families, diagnostic source reuse, synthetic rather than real supplier/provider commitments, and incomplete independent adjudication. The method supports controlled, reproducible research **within its stated fictional environment**. It does not yet support claims of measured AI accuracy, superiority to the deterministic baseline, general enterprise representativeness or production readiness.

### Source and reproducibility record

The principal implementation sources are:

- `phase-1c-data/design/synthetic-data-methodology.md`
- `phase-1c-data/design/calibration-rationale.md` and `calibration-report.md`
- `phase-1c-data/implementation/schema.sql`
- `phase-1c-data/implementation/calibration_config.yaml`
- `phase-1c-data/implementation/phase1c_data_contract.yaml`
- `phase-1c-data/implementation/phase1c_scenario_matrix.yaml`
- `phase-1c-data/evaluation/provisional_cases.json`
- `phase-1c-data/evaluation/provisional_authoring_manifest.json`
- `phase-1c-data/implementation/phase1c_release_review.md`

**Before thesis submission:** Replace the provisional checkpoint with the approved release commit and dates; insert source-verified figures and numbered captions; add the project's formal citation style and bibliography entries; verify all achieved distributions and final review dispositions. No figure or acceptance result should be presented as completed until actually produced and checked.
