# Phase 1C — What followed the agent-to-table design

**29 September 2026.** This is a decision record for the work after defining the deal input, six agent responsibilities, 24 justified tables, and candidate calibration sources. It distinguishes a public observation, a fictional sample structure, an experimental choice, a passed design check, and an implemented database.

## 1. Turn table names into an exact field and relationship contract

**Action.** The `24-table-field-and-provenance-spec-DRAFT.md` identifies columns, data types, keys, controlled values, nullable facts, derived values, field origins and joins. A deal has a header and line items. Product configuration stays on each line; product catalogues and BOMs decide technical requirements. Customer identity, credit, invoices and payments remain separate. A run freezes the input/configuration/data context and an execution log records each agent attempt.

**Reason.** Table names alone cannot tell the generator whether a receipt is allocated, a product is a component, a digital entitlement is concurrent or a quoted date is physical delivery. Those distinctions affect agent answers. We kept aggregate `quantity_allocated` and capacity hours instead of inventing reservation owners or individual jobs; we omitted payment method and deal type where no agent decision used them.

**Status (29 September 2026 update).** Design contract written and compared structurally with SQL. The 24-table DDL, connected smoke test and 14-case row fixture subsequently passed in the user's local PostgreSQL 18.6 test database. Repository/agent decision tests remain pending.

## 2. Choose source-grounded and explicitly synthetic values

| Provenance | Used for | Not used for |
|---|---|---|
| Open Icecat and official manufacturer/provider catalogues | Product families, attributes, option patterns and sampled visible price bands, translated into brand-neutral synthetic SKUs | Importing the original product rows, private cost or governance policy |
| ECB dated reference FX | Converting sampled USD list-price anchors to provisional EUR bands | Live exchange rates or cross-currency deal processing |
| Olist observed data | Selected order-frequency, item-count and delivery-time *shapes*, transformed for the fictional B2B context | Consumer BRL prices, consumer payment behaviour, or a claim that its frequencies are B2B norms |
| Official fictional Microsoft sample databases (WideWorldImporters, AdventureWorks) and ERPNext documentation | Example customer/invoice/supplier/PO/BOM relationships and workflow structure | Empirical factory hours, supplier quantities, credit policies or approval levels |
| Public integrator financial reports (CDW/Insight) | Broad, blended portfolio gross-margin plausibility check | Deriving an individual product cost, category margin floor or approval threshold |
| `SYN` fictional-company experiment choices | Product/customer counts, BOM/component quantities, production hours/capacity, allocations, evidence freshness, credit limits, commercial policies, role thresholds and conflict quotas | Claims of measured industry rates |

**Method.** For a measured anchor, record the source, extraction/date, transformation and limitation in the calibration report. For an unobservable operating fact, state `SYN`, a usable range or quota and a reason tied to an agent decision. Generate related facts jointly, not as isolated random columns. Example: 18 make-to-order sellable SKUs and 36 nonsellable components are coverage choices; 24–36 proposed BOM variants must resolve to valid configurations and produce costs consistent with product price/margin bands. Day-level production hours are intended to create both feasible and capacity-constrained cases, not to model a real factory.

**Status.** Earlier catalogue/commercial calibration is recorded. Expanded operational ranges remain proposed and need row-level checks and sensitivity analysis. No external source establishes a 24-hour stock freshness threshold, 18 assembled products or a 15:00 dispatch cutoff as an industry norm.

## 3. Define three commercial profiles

**Action.** `calibration_config.yaml` defines `BASELINE_2026`, `LENIENT_EXPERIMENT`, and `STRICT_EXPERIMENT`. The same submitted deal, list prices, standard costs, credit limits and supply snapshot are held fixed. Only the applied commercial policy set changes in distinct `deal_runs` records. Historical decisions use baseline.

| Policy example | Strict | Baseline | Lenient |
|---|---:|---:|---:|
| Routine discount maximum | 5% | 10% | 15% |
| Hard discount cap | 25% | 35% | 40% |
| Standard payment term maximum | 30 days | 45 days | 60 days |
| Absolute payment term cap | 60 days | 90 days | 90 days |
| Over-credit-limit exception ceiling for Finance review | 5% | 15% | 25% |
| Sales Director review above deal value | €50,000 | €100,000 | €200,000 |

Category-specific margin floors and Sales VP deal-value thresholds also differ by profile. Values exactly equal to an `above` threshold stay in the lower band. A nonpositive margin, prohibited clause or invalid technical configuration remains a hard block; a commercial approver cannot waive physical impossibility.

**Reason.** Public companies do not publish a complete compatible set of discount, credit, policy and approval rules. These values are *synthetic experimental controls* chosen to yield meaningful baseline decisions and a monotonic lenient/strict contrast. They must be reviewed for internal consistency and useful boundary coverage. Public portfolio financial results only sanity-check overall generated margins, not these thresholds.

**Status.** Profiles and allowed values are specified in YAML; rules have not been compiled into loaded database rows or executed by agents.

## 4. Deliberately construct test coverage

**Action.** The generator plan allocates exactly 100 `generated_test` deals into 18 mutually exclusive *primary* cases under baseline: 30 clean, and 70 spread across discount/margin, credit/payment, configuration, stock/components/PO, equipment/workforce, digital, installation, shipping, stale evidence and multi-flag cases. Specific overlay counts add partial delivery, shared components, downtime and other combinations without adding more deals.

**Clean means** every required selected option, commercial rule, account check and requested fulfillment condition is satisfied by valid evidence under baseline. It may still receive the normal Regional Manager route. Clean does not mean a human approval has been granted, and the 30% quota is not a measured rate of real-world clean deals.

**Reason.** Unconstrained random generation could produce almost no rare but thesis-critical failures. A single-fault case isolates which specialist should detect a problem; multi-flag cases test coordination. After generating a requested case, an independent rule oracle must verify its *actual* primary and secondary findings. Lenient/strict findings are recomputed rather than copying baseline labels. Historical deals follow their separate baseline distributions, and independently authored evaluation fixtures remain hidden from agents.

**Status.** Quotas sum to 100 and the classification contract is specified; the 100 deals themselves have not been generated.

## 5. Dry-run decision logic with hand-authored examples

**Action.** Fourteen examples in `phase1c_reference_fixtures.yaml` pass `validate_phase1c_reference_fixtures.py`. They cover stock/allocated inbound, BOM materials and capacity hours, supplier offers, digital entitlements, shipping cutoffs, installation eligibility, stale evidence, credit exposure, policy replay, cost roll-up and shared components.

**Example.** Stock 20 on hand − 12 allocated = 8 free now. A confirmed receipt of 5 − 2 allocated = 3 potentially free later. For a request of 10, the correct finding can be 8 now plus 2 later *only when* the receipt is binding, timely and can ship to arrive by the customer's date. It cannot call all 10 immediately available. This is a controlled arithmetic/evidence example, not ten inserted database records.

**Reason.** These examples catch contradictions in our own rules before the generator can replicate them hundreds of times. They do not establish agent accuracy: the executable design oracle, SQL, generator and final independently authored evaluation set are different layers.

**Status.** All 14 design-level checks pass. Row-level fixtures and agent repository outputs have not been tested.

## 6. Translate the field contract into PostgreSQL DDL

**Action.** `schema.sql` drafts all 24 tables with primary and foreign keys, checks, selected indexes, a restricted deal-input view and targeted triggers. `validate_schema_contract.py` checks 24 documented table/column sets, FK target table names, 21 controlled vocabularies against the YAML, and the 100-case total.

**Reason.** Database constraints should reject impossible local states such as negative or over-allocated stock, wrong product modes, mismatched catalogue versions, an overlapping active BOM, a confirmed receipt lacking evidence, or an edited submitted deal. SQL is a safeguard under the agent layer, while configuration and repository validation must still handle JSON schemas and multi-row business logic.

**Status.** Static checks pass. There is **no executed PostgreSQL schema or operational row set yet**. A text check does not prove that DDL parses or that triggers behave correctly.

## 7. Keep an explicit implementation gate

**Next checks, in order:** (a) apply SQL in disposable PostgreSQL 15+ and test representative accepted/rejected inserts; (b) load small coherent row-level fixtures for the 14 examples and exercise repository joins, dates, evidence, allocation and policy results; (c) validate JSON contracts, BOM coverage/ambiguous signatures, historical point-in-time financial facts and effective snapshots; (d) finalize the independent evaluation coverage matrix without exposing expected answers to agents; (e) generate and validate the historical and test rows, then implement specialists.

**Why this matters.** A valid-looking table can still produce the wrong answer when two receipts are double-counted, a latest snapshot is stale, a licence quantity covers a contract term rather than simultaneous seats, or shipping transit is omitted. `schema-validation-notes.md` lists the remaining database and repository checks.

See `Phase1C-schema-visualization.md` for a readable overview and detailed relationship views. The diagrams show actual foreign keys separately from business-code/time joins.
