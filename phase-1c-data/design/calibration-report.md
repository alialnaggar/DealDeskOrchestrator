> **Status note (11 October 2026):** This is the calibration research record. Its dated implementation counts are historical. See `../README.md` and `../implementation/phase1c_release_review.md` for current readiness.

# Deal Desk Orchestrator — Phase 1C Calibration Report

**Student:** Ali Alnaggar  
**Thesis:** Deal Desk Orchestrator (Multi-Agent System)  
**Created:** 23 September 2026  
**Last updated:** 25 September 2026  
**Status:** Core calibration streams completed — Olist, enterprise product taxonomy/list price, Microsoft wholesale-credit/supply, and price/cost cross-checks are documented. Final rule thresholds and generator freeze remain.

---

## 1. Purpose

This report records the external evidence used to configure the synthetic data generator. It prevents “calibrated” from becoming a vague claim: every adopted parameter must show its source, filters, observed statistic, transformation, final generator value and limitation.

The report distinguishes:

- **Observed commercial data**, which may support statistical shapes after relevance checks.
- **Real product catalogues**, which support taxonomy, attributes and price sampling.
- **Official fictional sample databases**, which support schema and logical relationships but not claims about market averages.
- **Purposeful experimental design**, used when public evidence is unavailable or when evaluation coverage matters more than population representation.

No external row will become a row in the thesis database.

---

## 2. Approved source hierarchy

| Priority | Source type | Examples | Permitted role |
|---:|---|---|---|
| 1 | Real product/catalogue evidence | Open Icecat; official provider and manufacturer catalogues | Categories, subcategories, product attributes, naming patterns and sampled list-price bands |
| 2 | Observed commercial transactions | Olist | Distribution shapes for delivery, popularity and selected order characteristics after relevance checks |
| 3 | Official fictional business samples | Microsoft WideWorldImporters and AdventureWorks | Table relationships, credit/payment fields, inventory flows and pricing calculations |
| 4 | Secondary public datasets | DataCo | Cross-check delivery timing only after provenance/data-quality review |
| 5 | Explicit thesis assumptions | Policy thresholds, approval authority, compatibility rules, customer coverage design | Necessary confidential/governance data, clearly labelled synthetic |

Superstore and Northwind are no longer primary calibration sources. They may be used only as weak sanity/schema checks.

---

## 3. Olist source and access note

Canonical source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

The canonical Kaggle page is public, but direct raw download required a Kaggle sign-in in the available environment. The first profiling pass therefore used the public mirror [Ganesh7699/Brazilian-E-Commerce-OList](https://github.com/Ganesh7699/Brazilian-E-Commerce-OList), repository commit `932d49a1197e27589c41ede0ad3e6b39666b30dd`. This is **provisional** until the files are checksum-verified against a canonical Kaggle download. Row counts and schemas match the widely documented Olist structure, but this does not replace checksum verification.

### 3.1 Files profiled

| File | Rows | Columns relevant to calibration |
|---|---:|---|
| `olist_orders_dataset.csv` | 99,441 | Status, purchase timestamp, delivered date, estimated delivery date |
| `olist_order_items_dataset.csv` | 112,650 | Order, line sequence, product, price, freight |
| `olist_customers_dataset.csv` | 99,441 | Customer ID and unique-customer ID |
| `olist_order_payments_dataset.csv` | 103,886 | Payment sequence, type, installments and value |
| `olist_products_dataset.csv` | 32,951 | Category and physical/logistical attributes |

Recorded SHA-256 values for this profiling pass:

| File | SHA-256 |
|---|---|
| `olist_orders_dataset.csv` | `8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf` |
| `olist_order_items_dataset.csv` | `0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279` |
| `olist_customers_dataset.csv` | `983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2` |
| `olist_order_payments_dataset.csv` | `4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0` |
| `olist_products_dataset.csv` | `3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc` |

### 3.2 Profiling filters

- Line/order statistics used rows with `price > 0` and `freight_value >= 0`.
- Delivery statistics used orders with status `delivered` and non-null purchase, delivered and estimated timestamps.
- Actual and estimated durations had to be between 0 and 180 days.
- This left 96,456 clean delivered orders from 96,470 delivered orders with the required dates.

---

## 4. Olist profiling results

### 4.1 Order structure

| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean | Maximum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Item rows per order | 1 | 1 | 1 | 1 | 1 | 2 | 1.14 | 21 |
| Distinct products per order | 1 | 1 | 1 | 1 | 1 | 1 | 1.04 | 8 |

**Decision:** reject direct transfer. A B2B technology deal commonly combines hardware, licences, services and support. The thesis generator will use a deliberately broader bundle distribution:

| Lines per deal | Target share |
|---:|---:|
| 1 | 15% |
| 2 | 25% |
| 3 | 25% |
| 4 | 18% |
| 5 | 10% |
| 6–8 | 7% |

This gives approximately three lines per deal while preserving both simple and complex deals. It is an explicit B2B transformation, not an Olist statistic.

### 4.2 Customer purchase frequency

- Unique customers: 96,096.
- Average orders per unique customer: 1.035.
- Customers with more than one order: 3.12%.
- Maximum observed orders for one customer: 17.

**Decision:** reject direct transfer. Olist's marketplace/customer pattern cannot support customer-specific credit history or Deal History precedents. The thesis retains 80 customers and 400 historical deals as purposeful repeated-measures design. Deal frequency will be weighted toward larger and strategic accounts rather than copied from Olist.

### 4.3 Product popularity

| Product group | Share of all item occurrences |
|---|---:|
| Top 10% of products | 53.78% |
| Top 20% of products | 67.13% |
| Top 50% of products | 85.38% |

Product occurrence count had median 1, P90 6, P95 11 and maximum 527.

**Decision:** accept the qualitative long-tail shape, not the exact product counts. For the 120-product thesis catalogue, the target is:

- Top 20% core products: approximately 60–70% of historical deal-line occurrences.
- Middle 50% regular products: approximately 25–35%.
- Bottom 30% niche products: approximately 5–10%.
- Every product must appear at least three times so no catalogue record is untestable.

### 4.4 Delivery timing

| Metric (days) | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| Actual purchase-to-delivery | 4.16 | 6.77 | 10.22 | 15.72 | 23.09 | 29.26 | 12.53 |
| Estimated purchase-to-delivery | 13.05 | 18.33 | 23.23 | 28.41 | 34.29 | 38.42 | 23.74 |

- Late-delivery rate: 8.10%.
- Among late deliveries, lateness was P50 5.80 days, P90 21.00 days and P95 28.93 days.

**Decision:** accept the distribution shape as a starting point only. Physical enterprise-technology products will use category-specific lead-time bands. Locally stocked workplace/network products may use shorter bands; servers, storage and configured infrastructure may use longer bands. A baseline 8–12% delivery exception rate is defensible for generated history, while evaluation cases deliberately include shortages and delayed inbound supply.

### 4.5 Price and order value

Olist price and order-value percentiles were calculated for data-quality understanding, but they are **not adopted** because they are in Brazilian reais and represent consumer-marketplace product categories. Enterprise-technology price bands will instead be sampled from current official/provider catalogues and recorded with observation date, currency and conversion method.

---

## 5. Provisional generator decisions supported by the first pass

| Parameter | Provisional decision | Evidence status |
|---|---|---|
| Historical lines per deal | Distribution in Section 4.1; mean approximately 3 | Purposeful B2B transformation; Olist explicitly rejected for direct transfer |
| Product-demand concentration | Top 20% products receive 60–70% of lines | Supported by Olist long-tail shape |
| Minimum product coverage | At least 3 historical occurrences per product | Experimental coverage requirement |
| Baseline physical delivery exception rate | 8–12% | Anchored to Olist's 8.10%, subject to enterprise-category adjustment |
| Customer repeat activity | Approximately 5 deals/customer on average, uneven by segment | Purposeful design; Olist explicitly rejected |
| Product/customer/deal counts | 120 / 80 / 400 | Approved experimental scale from Phase 1C |

These values remain provisional until the other calibration streams are completed.

---

## 6. Calibration work after the first pass

The WideWorldImporters and AdventureWorks checks listed in the original plan are completed in Sections 10–13. A DataCo cross-check is no longer required for the MVP: Olist already supplies an observed delivery baseline, while Microsoft samples validate replenishment logic. Adding a weaker-provenance source would not justify another generator parameter.

The remaining work listed at the end of this initial profiling pass was later expanded by the 24-table design and the pre-generation gates in Section 14. Use Section 14 and the current YAML validators for present readiness; this early list is historical, not a complete current checklist.

---

## 7. Reproducibility notes

The final calibration package must preserve:

- Source URL and access date.
- Licence/usage restriction.
- File name, row count and checksum where available.
- Filters and cleaning rules.
- Profiling code and random seed.
- Observed statistics.
- Adopted values and transformation rationale.
- Rejected statistics and reason for rejection.

This ensures that external data informs the generator without becoming untraceable or being presented as more representative than it is.

---

## 8. Enterprise product taxonomy calibration

### 8.1 Evidence used and interpretation

The taxonomy was checked on 24 September 2026 against:

- [SHI](https://www.shi.com/), which explicitly combines hardware/software procurement, licensing advisory, data-centre integration and IT services.
- [Insight](https://www.insight.com/en_US/home.html), which identifies its offer as computer hardware, software, cloud solutions and IT services.
- [CDW's category map](https://www.cdw.com/content/cdw/en/terms-conditions/site-map.html), which exposes detailed endpoint, server, storage, networking, security and software subcategories.
- [Dell](https://www.dell.com/en-us/shop), [Cisco](https://www.cisco.com/site/us/en/products/networking/index.html) and [HPE](https://www.hpe.com/asia_pac/en/products.html) portfolios for workplace, compute, storage, switching, routing, wireless and infrastructure archetypes.
- [Microsoft business and cloud catalogues](https://www.microsoft.com/en-us/microsoft-365/microsoft-365-business) for user-based subscriptions, cloud desktops and enterprise licensing patterns.
- [Icecat product taxonomy](https://icecat.com/product-taxonomy/) for the principle that product types should carry feature groups and specifications rather than forcing all products into one fixed attribute set.

These sources validate the types of products and the attributes used to distinguish them. Their raw catalogue proportions are not copied because reseller sites contain many duplicate vendor models, accessories and regional SKUs that are unnecessary for the thesis experiment.

### 8.2 Approved 120-product allocation

| Category | Approved subcategories and counts | Why this shape is useful |
|---|---|---|
| End-user computing and digital workplace (18) | Business laptops 5; desktops/mini PCs 3; workstations 2; monitors 3; collaboration devices 3; docks/peripherals 2 | Provides high-volume common items plus workstation and collaboration variants for bundle and compatibility checks. |
| Servers and compute infrastructure (12) | Rack 4; tower 3; edge/compact 2; GPU/accelerated 3 | Covers entry, data-centre, edge and high-performance configurations without modelling every chassis option. |
| Storage and data protection (10) | Arrays 3; NAS/file 2; backup appliances 3; enterprise drives 2 | Creates capacity, interface and protection-tier differences while keeping a contained family set. |
| Networking and connectivity (16) | Switches 5; routers/SD-WAN 3; wireless access points 3; controllers/management 2; optics/transceivers 3 | Networking needs the widest compatibility surface: port speeds, PoE, management platform, uplinks and optics. |
| Cybersecurity (12) | Firewalls/appliances 3; endpoint/XDR 3; identity/access 2; email/cloud security 2; SIEM/vulnerability 2 | Mixes device, user and protected-asset licensing so Pricing and Policy must interpret different commercial units. |
| Cloud services and subscriptions (12) | IaaS compute 3; storage/backup 2; managed database/application platform 2; virtual desktop 2; DRaaS 3 | Represents usage, instance, user and protected-capacity services rather than treating cloud as one generic SKU. |
| Enterprise software and licensing (18) | Productivity/collaboration 4; CRM/ERP 4; data/BI/analytics 3; backup/virtualization 3; ITSM/endpoint management 2; developer/database tools 2 | Software receives broad coverage because editions, modules, user bands and licence terms drive many commercial rules. |
| Professional and implementation services (12) | Assessment 2; architecture/design 2; deployment/integration 3; migration/modernization 3; training/adoption 2 | Enables mixed product-service deals and required-service compatibility rules. |
| Managed support and warranty (10) | Warranty extension 2; premium vendor support 3; managed infrastructure/network 3; managed security/cloud operations 2 | Provides attachable coverage tiers, response times and contract terms without creating a full service-management catalogue. |
| **Total** | **44 subcategories; 120 products** | |

### 8.3 Attribute design

Attributes are stored in `products.attributes_json`. Common keys are `subcategory`, `family`, `tier`, `term_months`, and `price_unit`; physical products also carry `stocked = true/false`. Important category keys are:

| Category | Required differentiating attributes |
|---|---|
| Workplace | Form factor, processor tier, RAM, storage, display size/resolution, operating system, dock/connector type |
| Servers | Chassis/form factor, socket/CPU tier, RAM capacity, drive bays, GPU capability, power-supply redundancy |
| Storage | Usable capacity, media type, protocol/interface, controller redundancy, throughput tier, rack units |
| Networking | Device role, port count, port speed, PoE budget, uplink type, management platform, licence requirement |
| Cybersecurity | Deployment type, protected users/devices, throughput or user band, security tier, subscription term, required appliance/platform |
| Cloud | Service family, region class, vCPU/RAM or capacity tier, billing unit, service tier, term/commitment |
| Software | Software family, edition, licence metric, user/device/core band, term, deployment model, required base product |
| Professional services | Service scope, complexity tier, included days/hours, delivery mode, prerequisite product/category |
| Support/warranty | Coverage type, response target, coverage window, term, covered product family, managed/not-managed flag |

The product schema now includes `unit_of_measure` explicitly. Example values are `device`, `user_year`, `device_year`, `instance_month`, `protected_tb_month`, `service_package`, and `coverage_year`. This prevents a line quantity of 100 from being interpreted inconsistently across devices, licences and months.

### 8.4 Brand-neutral naming and codes

Generated names remain fictional and follow four templates:

- Hardware: `[Family] [Form/Tier] [Capacity or Performance]`, for example `Aster Pro 14 U5-16-512`.
- Infrastructure: `[Family] [Role/Form] [Scale]`, for example `Vertex Rack R2-256` or `NexusEdge Switch 48P-PoE`.
- Software/cloud: `[Capability] [Edition] [Billing Unit/Term]`, for example `Orbit CRM Enterprise User-Year`.
- Services/support: `[Outcome] [Scope] [Tier/Term]`, for example `Cloud Migration Medium Package` or `Infrastructure Care 24x7 One-Year`.

Codes use `CATEGORY-SUBCATEGORY-NNN`, such as `EUC-LAP-001`, `NET-SWI-003`, and `SVC-MIG-002`. Real product names are evidence for naming structure only and will not appear as generated rows.

## 9. List-price calibration

### 9.1 Public anchor samples

Public catalogue pricing is incomplete because enterprise configurations are frequently quote-based. The calibration therefore uses visible prices as anchors, not as a statistically representative market sample.

| Area | Public anchor observed | Use in calibration |
|---|---|---|
| Workplace | Dell 14 Plus base configuration: USD 1,109.99 | Anchors the centre of the business-laptop range. |
| Storage | Dell PowerVault ME5224: USD 20,298.99 base price | Anchors upper-mid infrastructure storage. |
| Networking | Ubiquiti Dream Router: EUR 185 before VAT; Cisco Meraki MS150 48-port switch: USD 8,586 | Demonstrates the wide device range from branch gateway to enterprise managed switching. |
| Cybersecurity | Box KeySafe: USD 378.99; WatchGuard three-year suite: USD 1,511.99; Fortinet points licence: USD 9,017 sale / USD 10,000 MSRP | Anchors low, mid and high subscription/licence values. |
| Software | Microsoft 365 business plans: approximately USD 5.40–14 per user/month; Microsoft 365 E7: USD 99 per user/month | Anchors user-based annualized software licensing. |
| Cloud/virtual desktop | Windows 365 examples: USD 36 and USD 56 per user/month | Anchors recurring cloud-desktop offers; other cloud services remain usage/configuration based. |
| Deployment services | Dell PowerEdge deployment add-ons: approximately USD 367–1,762 | Provides a public lower-bound anchor; complete consulting/migration packages are intentionally higher and synthetic. |
| Support | HPE Foundation Care example at SHI: approximately USD 765 | Anchors entry support while premium and managed coverage scales higher. |

USD anchors are normalized using the documented ECB reference of EUR 1 = USD 1.1377 from 24 July 2026. The exchange rate is a fixed calibration input, not a live runtime dependency.

### 9.2 Adopted generator list-price bands

These are **generator parameters**, not claimed market percentiles. `P10/P50/P90` names describe target distribution anchors within the synthetic catalogue.

| Category | Price basis | P10 EUR | P50 EUR | P90 EUR |
|---|---|---:|---:|---:|
| End-user computing/workplace | One device | 180 | 1,050 | 3,500 |
| Servers/compute | One configured server | 3,000 | 12,000 | 45,000 |
| Storage/data protection | One device/appliance | 1,200 | 9,000 | 28,000 |
| Networking/connectivity | One device | 180 | 1,800 | 8,500 |
| Cybersecurity | One appliance or annual licence unit | 300 | 2,500 | 12,000 |
| Cloud services | One monthly service unit | 25 | 250 | 1,500 |
| Enterprise software | One annual licence unit | 75 | 750 | 6,000 |
| Professional services | One fixed service package | 1,500 | 8,000 | 25,000 |
| Managed support/warranty | One annual coverage unit | 300 | 2,200 | 10,000 |

Generation will use subcategory-specific triangular or log-normal draws around these anchors, not a single category-wide uniform distribution. Values will be rounded to commercially readable amounts. `standard_cost` is generated from the category margin anchors approved in Section 11.

### 9.3 Limitations and decision

- Visible catalogue prices are snapshots and may be promotional, regional or base configurations.
- Many enterprise servers, cloud services and managed offerings require a quote.
- Subscription values depend on licence metric and term, so comparisons are valid only when `unit_of_measure` is explicit.
- The adopted bands are deliberately broad enough to create low-, medium- and high-value deals for agent testing, while remaining anchored to visible examples.

**Decision:** accept the taxonomy, attribute templates, naming patterns, price units and synthetic list-price anchors for generator design. The price/cost calibration in Section 11 completes the corresponding `standard_cost` rule.

---

## 10. Microsoft sample-database profiling

### 10.1 Provenance and interpretation boundary

The official Microsoft `sql-server-samples` repository was profiled at commit `beaab06ef72831089ca80e5355d65e661fd19b26`. The selected source files, their SHA-256 checksums, the reproducible script, and the calculated output are recorded in `profile_microsoft_samples.py` and `calibration_results_microsoft_samples.json`.

WideWorldImporters is a fictional wholesale company sample, and AdventureWorks is a fictional bicycle-manufacturer sample. They are valid evidence for **how** credit, AR, inventory, purchase orders, standard cost, price and discounts relate. They are not evidence for real enterprise-technology market averages. Every transferred numeric parameter below is therefore either a deliberately transformed assumption or an external sanity check—not a relabelled sample statistic.

### 10.2 WideWorldImporters results

The source separates customer `CreditLimit`, `PaymentDays`, `IsOnCreditHold` and `StandardDiscountPercentage`. Customer transactions separately retain `OutstandingBalance` and finalization information. This validates the project’s separation of `customer_credit_profiles`, `accounts_receivable` and `payment_history`.

The sample payment-day generator gives 30 days a theoretical 37.5% share, 45 days 25%, and 60, 90 and 180 days 12.5% each. Its generated credit limits run only from 1,100 to 4,000 monetary units. Both distributions are illustrative and unsuitable for direct transfer. The useful finding is that payment terms are discrete contractual choices and should remain separate from credit capacity.

For supply, 219 seed stock items have lead times concentrated at 12 and 14 days, with observed seed values of 2, 7, 12, 14 and 20 days. The 219 stock-holding seeds have quantity-on-hand median 22, target-stock median 40, 18.26% below reorder level, and 2.74% at zero stock. More importantly, the replenishment procedure:

1. computes effective stock from on-hand, open demand and stock already on order;
2. triggers when effective stock falls below the reorder level;
3. orders toward a target stock level in valid pack sizes;
4. assigns an expected date using lead time; and
5. increases on-hand stock when the purchase order is received.

This directly supports current `inventory` plus multiple future `inbound_supply` rows. Reorder level and target stock are useful generator concepts but do not need extra database columns because the Availability Agent only needs the point-in-time stock and dated inbound receipts.

### 10.3 AdventureWorks results

Of 504 product rows, 304 have positive list price and standard cost. For those rows, list-price gross margin has P10 36.36%, median 45.24%, P90 62.60%, and mean 46.28%. These are bicycle-sample values and are rejected as direct margin targets.

Across 121,317 sales-order lines, quantity has median 1, P90 5 and P95 7. Discounts are zero on 97.29% of lines. Positive discounts use discrete values from 2% to 40%, with a 5% median among discounted lines. The zero-discount share is rejected because a deal-desk experiment requires meaningful negotiated and exception cases; the discrete band structure is retained.

The `ProductVendor` rows show lead-time P10 15 days, median 17, P90 25 and P95 45. This supports using longer replenishment bands for configured servers/storage than for locally stocked workplace items, while remaining illustrative.

---

## 11. Standard cost, margin and discount decisions

Public 2025 full-year results provide an external portfolio-level check: CDW reported a 21.7% gross margin and Insight reported 21.4%. These are blended company results, not product-level cost rates. The generator therefore uses different category list-margin anchors, then validates that the generated historical portfolio produces a **realized revenue-weighted gross margin of 19–25% after discounts**.

| Category | List-margin P10 | P50 | P90 |
|---|---:|---:|---:|
| End-user computing/workplace | 10% | 18% | 28% |
| Servers/compute | 9% | 16% | 25% |
| Storage/data protection | 10% | 19% | 28% |
| Networking/connectivity | 12% | 21% | 32% |
| Cybersecurity | 18% | 32% | 48% |
| Cloud services | 22% | 38% | 55% |
| Enterprise software | 25% | 45% | 65% |
| Professional services | 30% | 48% | 65% |
| Managed support/warranty | 25% | 42% | 60% |

`standard_cost = list_price × (1 - target_list_margin)` and is rounded to two decimals. It is generated before and independently of the deal’s quoted discount. The generator must never silently reduce cost or repair a low-margin quote; a below-floor result is precisely what Pricing and Policy must detect.

Historical requested discounts use the following target shares: zero 15%; up to 5% 35%; 5–10% 25%; 10–15% 15%; 15–20% 7%; 20–30% 2.5%; and 30–40% 0.5%. Draws are conditioned on segment, category, unit, quantity and pricing rules. This creates realistic routine quotes while guaranteeing a small population of senior exceptions. Hand-built evaluation deals remain separate and may deliberately exceed the historical mix.

---

## 12. Credit, AR and payment-history decisions

The adopted values are purposeful synthetic business assumptions because public customer-level credit data is confidential and the WWI numbers are generated.

| Segment | Credit-limit triangular range (EUR) | Paid-history rows/customer | Open AR rows/customer |
|---|---:|---:|---:|
| SMB | 20k / 75k / 200k | 8 / 12 / 16 | 0 / 2 / 4 |
| Mid-Market | 100k / 300k / 750k | 12 / 18 / 24 | 1 / 3 / 6 |
| Enterprise | 400k / 1.2m / 3m | 18 / 27 / 36 | 2 / 5 / 10 |

The three values are minimum/mode/maximum. Strategic accounts receive a 1.25 multiplier, capped at EUR 4m. Across 80 customers, exact risk counts are 44 Low, 28 Medium and 8 High; credit statuses are 72 Active, 5 Review and 3 On-Hold. Payment terms are not uniform: aggregate exact counts are 8 at 15 days, 36 at 30, 20 at 45, 13 at 60 and 3 at 90, with longer terms concentrated in larger accounts.

Payment history covers 24 months. Low-risk customers target 80% early/on-time, 17% 1–10 days late and 3% 11–45 days late; Medium targets 60/30/10 across early/on-time, 1–15 late and 16–60 late; High targets 35/40/25 across early/on-time, 1–20 late and 21–90 late. These are probabilistic relationships, not circular labels. A “strong” payment history is derived only when on-time share is at least 80%, average delay is no more than five days and serious lateness is no more than 5%.

Open AR targets 18–28% overdue invoices. About 10% of customers should already fall in an exceeded-exposure band, so Credit sees both normal and cautionary cases. The required evaluation case—post-deal exposure above the limit despite strong history—is hand built rather than left to chance.

---

## 13. Inventory and inbound-supply decisions

No additional database table is required. `inventory` remains the current product/location snapshot, while each future receipt is a separate `inbound_supply` row. Two location codes (`WH-EU-CENTRAL`, `WH-EU-WEST`) are sufficient; a warehouse master would not improve an agent decision in this MVP.

Stocked items target 55% healthy, 25% tight, 15% below-reorder and 5% zero-available states. This is close to WWI’s illustrative 18.26% below-reorder and 2.74% zero-stock observations but intentionally increases zero-availability coverage. Reservations use 0–45% of on-hand stock. Target-stock ranges are 20–120 units for core products, 5–50 for regular products and 1–15 for niche products.

Confirmed inbound supply accounts for 70% of inbound rows; Planned 20%, Delayed 8% and Cancelled 2%. Only Confirmed supply arriving on or before the requested delivery date counts as fulfillable. Replenished products receive one to three dated rows, and at least 20% receive multiple receipts so cumulative date/quantity reasoning is tested.

Physical lead-time triangular bands are 2/7/14 days for workplace, 14/28/45 for servers, 10/21/45 for storage, and 3/10/21 for networking and security appliances. Digital subscriptions and fixed service packages use a documented `fulfillment_lead_days` product attribute. Workforce-capacity scheduling is explicitly outside the MVP; adding a service-resource table would exceed the agent’s current decision scope.

The full machine-readable decisions are in `commercial_supply_calibration.yaml`.

---

## 14. Phase 1C pre-generation addendum — 4 October 2026

Sections 1–13 record the earlier profiling pass and its decisions at that time. The current 24-table design adds component BOMs, capability/day production capacity, shipping, digital pools and installation eligibility. The earlier statement that workforce-capacity scheduling is outside the MVP has been superseded **for aggregate production capability/day checks**; individual employee schedules remain out of scope. The consolidated `calibration_config.yaml` is authoritative over older calibration YAMLs if values differ.

`Phase1C-calibration-contract.md` now maps each parameter family to observed, transformed, structural or synthetic evidence; specifies relationships and generator order; and defines row, distribution, decision and leakage checks. Olist's 67.13% product concentration and 8.10% late-delivery rate are source-profile observations. Only the product-popularity shape has a transformed target in this fictional B2B system; actual lateness cannot be measured from the present schema. These are not enterprise benchmarks. Microsoft samples are fictional and support relationships and calculations, not empirical operating rates. Operational hours, stock, supplier lead, credit and test-conflict numbers are assumptions to test as a coherent scenario.

The draft branch's `validate_phase1c_calibration.py` currently finds no configured arithmetic errors, but it deliberately returns `ready_for_generation: false`. Four reviews remain: carry the conservative 30-calendar-day horizon behavior into generated rows for possible 30-workday supplier leads; prove the proposed 36-component/156-product targets through BOM coverage; verify Olist mirror checksums against the canonical download; and check catalogue price dates, units and comparability. The historical lines-per-deal distribution and its tolerance are executable; achieved-statistic tolerances for other distributions still need settings before freeze. A future generator must produce rows, independently recompute facts and findings, and report achieved distributions; this configuration check is not evidence that a full dataset exists or is realistic.

For digital confirmation, the trusted synthetic evidence manifest must include `provider_id` and `quantity_allocated` along with exact product, configuration, region, term, unit, capacity, binding status and full-term dates. A mismatched provider cannot confirm a candidate pool. These manifest records are independently controlled test data, not live attestations.

**Field-level correction (4 October 2026):** The new Phase1C-column-calibration-rules.md covers all 266 schema columns and records 22 open pre-generation definitions. The earlier proposed 8–12% late-delivery band is **not a valid actual-outcome target** for this schema: Olist measures actual-versus-estimated consumer delivery, while these 24 tables have no actual delivery event/date. Only requested-date feasibility can be derived from the available stock, inbound, production and shipping facts. The 1–8 historical lines/deal sampling weights and pilot tolerances are now explicit in the consolidated config; they are synthetic B2B design settings.

**Structured contract addendum (4 October 2026):** phase1c_data_contract.yaml fixes the initial synthetic countries/regions, installation coverage, locations/time zones, weekday-only calendar semantics, customer industry/country shares, and typed JSON boundaries for terms, configurations, requirements, evidence references, compatibility rules, provider proof and agent outputs. Its validator passed in [Actions run 37224407758](https://github.com/alialnaggar/dealdeskdata/actions/runs/37224407758), alongside the schema and 14 reference cases. These definitions make values judgeable during generation; they do not turn synthetic numbers into observed industry statistics or replace row-level pilot validation.

**Calendar validation increment:** Supplier calendar and shipping weekday payloads have per-row shape checks. They reject invalid ISO numbers, duplicates, holidays in the deliberately holiday-free Phase 1C model, missing/extra supplier fields and invalid time zones. [Actions run 37224836805](https://github.com/alialnaggar/dealdeskdata/actions/runs/37224836805) passed them alongside the PostgreSQL/reference checks. Generator integration, workday lead arithmetic and origin-local dispatch checks remain open; the main generation gate remains closed.

**Connected pilot preflight:** The draft eight-row synthetic slice in `Phase1C-pilot-preflight-report.md` checks row shape, selected payload contracts, stock and geography relationships, supplier workday lead, origin-local lane date, and generated-test answer isolation. Its 30-workday maximum offer reaches 13 November 2026, beyond the 3 November 30-calendar-day horizon, so it is reported unknown/conditional. The lane's 5 October dispatch and 7 October arrival are candidates only. This tests mechanics and selected relationships; it does not establish price/stock distributions, BOM coverage or full-data realism.

[GitHub Actions run 37225949947](https://github.com/alialnaggar/dealdeskdata/actions/runs/37225949947) passed the connected pilot SQL constraints and existing 14 reference/reader/decision gates at draft commit `5d3392b`. Full generation remains blocked by the 22 ledger review definitions and independent distribution checks.

**Assembly pilot increment:** `Phase1C-assembly-pilot-report.md` documents one configured build with two mandatory components, one active effective BOM and two dated capability operations. The independent row preflight and SQL reader agree on a feasible uncommitted candidate and a €428.47 illustrative cost rollup within 5% of the synthetic standard cost. [Branch run 37226908922](https://github.com/alialnaggar/dealdeskdata/actions/runs/37226908922) and [PR run 37226911993](https://github.com/alialnaggar/dealdeskdata/actions/runs/37226911993) passed. The 1% scrap calculation yields fractional theoretical `component_unit` demand. One BOM does not validate the proposed 24–36 variants, 36 component SKUs or realized capacity/cost distributions.

**Component-unit calibration rule:** Initial component inventory and allocations are whole units. Theoretical scrap-adjusted demand aggregates across selected builds before rounding up once per component for the physical stock check; cost uses unrounded expected consumption. The compute example needs seven stock units for 6.060606… theoretical demand. Fractional component inventory is rejected by row preflight, even though general SQL NUMERIC(14,3) permits it. [PR run 37228116477](https://github.com/alialnaggar/dealdeskdata/actions/runs/37228116477) passed the revised reader, preflight, contract and 14 reference cases at draft commit `95161f0`. Generator and shared-component portfolio tests remain open; the 22 field reviews are not closed by this single example.

**Two-configuration relationship check:** The connected PostgreSQL extension uses two BOMs for one SKU and one shared compute component. Exact configuration matching yields distinct 3- and 2-unit builds; combined scrap-adjusted demand rounds to 11 whole component units. A configuration-free finished inventory row cannot support either variant. [Branch run 37229591464](https://github.com/alialnaggar/dealdeskdata/actions/runs/37229591464) and [PR run 37229595705](https://github.com/alialnaggar/dealdeskdata/actions/runs/37229595705) passed, including the existing 14 scenarios and decision gates. This is a relationship boundary test, not proof of 18 SKU/24–36 BOM coverage or achieved component/capacity distributions.

**Substitute-group selection increment:** `phase1c_bom_selection.py` defines the generator/reader rule for alternatives within one BOM: choose one candidate per group, prefer sufficient selectable whole units from fresh stock or confirmed unexpired inbound at active production locations, then use lowest priority and component ID as deterministic tie-breaks. If no option covers the rounded requirement, retain the deterministic choice and expose the group shortfall; do not double-count alternatives. Pure tests cover stocked, inbound-supported and shortage paths. The rule is now declared in both YAML contracts, but no full generated BOM set exists yet and the overall calibration review items plus column-level generator checks remain open.

**Capacity-window classification (5 October 2026):** The reader keeps a 30-calendar-day capacity window. If required component stock and confirmed receipts through the last represented capacity date are insufficient, but a confirmed receipt is expected afterward, production is reported as `unknown` with reason `confirmed_component_supply_after_capacity_horizon`. Missing, stale or incomplete fresh capacity evidence is also `unknown`, not zero capacity. It does not count supplier offers as commitments or claim later capacity. Eight focused tests cover late/on-window receipts, location matching, stale stock, resource coverage and status classification. [Actions run 37294322176](https://github.com/alialnaggar/dealdeskdata/actions/runs/37294322176) passed those checks together with all 14 reader and deal-decision cases. The generator must preserve this rule, and overall calibration remains unfrozen.

**BOM proposal arithmetic (5 October 2026):** `validate_phase1c_calibration.py` now checks that the component-family counts sum to the proposed component total, proposed overall product rows reconcile, the BOM variant range covers the make-to-order SKU count, and component units, scrap and sharing/substitute proportions stay in valid ranges. These are consistency checks only: they do not prove that generated product configurations have complete BOM coverage. Product totals remain proposals and generation remains blocked.

## Calibration arithmetic gate — 5 October 2026

The executable pre-generation checker now validates the proposed BOM portfolio’s internal arithmetic: family totals and total product rows, shape and order of the BOM variant bounds, coverage of proposed make-to-order products, component-unit and scrap triplets, a scrap ceiling below 100%, and shared-component/substitute-group shares within 0–1. Focused tests deliberately corrupt the proposal and confirm the checker rejects it. This is a consistency check, not evidence that each offered configuration maps to an effective BOM or that generated distributions match the proposal.

GitHub Actions [run 37295322480](https://github.com/alialnaggar/dealdeskdata/actions/runs/37295322480) passed the PostgreSQL schema/fixture checks, all 14 reference reader scenarios, calibration and column-coverage validation, policy compilation, and the commercial and deal-decision gates. Local pure tests at that point: 63 passed; 21 database tests were skipped because this workspace lacks PostgreSQL and `psycopg`. `ready_for_generation` remains false.

## Portfolio coverage preflight — 6 October 2026

`validate_phase1c_bom_portfolio.py` now accepts an explicitly prepared portfolio snapshot and checks that every listed make-to-order configuration maps to exactly one active BOM on the selected as-of date. It also checks catalogue-version consistency, proposed sellable/component/family counts, same-version non-sellable component references, per-component quantities/scrap, BOM overlap, substitute-group limits and component reuse, and requires active production steps for every effective BOM. The checker does not enumerate option combinations or fabricate portfolio rows.

Eight pure tests use a small fictional portfolio created only in test code. They cover successful explicit coverage, a missing BOM, overlapping versus historical non-overlapping versions, an invalid component/scrap value, component reuse, substitute bounds, and projection-field drift. GitHub Actions [run 37434768059](https://github.com/alialnaggar/dealdeskdata/actions/runs/37434768059) passed all 20 workflow steps, including PostgreSQL validation and all 14 reader scenarios. Local `unittest discover`: 71 pass and 21 database-dependent tests skip without PostgreSQL/`psycopg`. No production portfolio has been supplied to the checker, so the 18-SKU and 24–36-BOM proposal is not yet proven and calibration remains unfrozen.

## Portfolio draft and cost decision — 6 October 2026

The user approved a small local configuration/test workshop and chose one list price and one conservative standard cost per product for the six paired technical options. Their codes are `standard` and `alternate`; alternate does not imply a premium tier. No new priced-SKU layer or pricing schema is needed for this draft. A material cost gap would require a distinct priced SKU or a later pricing-design decision.

`build_phase1c_portfolio_draft.py` now produces a synthetic structural projection of 120 sellable products and 36 components. Eighteen locally buildable SKUs (2 workstations, 10 servers, 6 storage systems) declare 24 offered configurations with 24 effective BOMs. Eighteen of 36 components are reused in at least two BOMs; one BOM contains a same-family substitute group. All 156 products have typed attribute shapes, and the checker enforces declared options, platform compatibility and BOM coverage. The precise operating mix, component identities, source prices and compatibility at interface/power level are still proposed rather than validated commercial facts. See `phase1c_portfolio_draft_review.md` on `phase1c-reader-draft`.

A single illustrative workstation cost pilot rolls two options to €688.56 and €710.78 using €30/hour and 10% overhead. One €715 standard cost covers the higher BOM and sits within the configured 5% tolerance for both; the €1,050 list price is an unverified draft category anchor. Its 31.90% catalogue margin is arithmetic, not an observed market margin. `validate_phase1c_variant_cost_pilot.py` rejects undercosted, materially divergent or incomplete inputs. Cost inputs for the other 17 buildable SKUs remain open. The portfolio validator still returns `ready_for_full_generation: false`; four calibration review items and 22 field reviews remain open, as do achieved distribution and independent evidence checks.

Draft implementation: [`b0d99a9`](https://github.com/alialnaggar/dealdeskdata/commit/b0d99a962261b3bd0c156c1a4045b74f0e0b8e87) on `phase1c-reader-draft`. Local `unittest discover`: 106 tests run, 21 PostgreSQL-dependent tests skipped; the [branch CI run](https://github.com/alialnaggar/dealdeskdata/actions/runs/37454718795) verifies database cases separately.

## All-build cost feasibility — 6 October 2026

The draft branch now contains `phase1c_build_cost_draft.json` and a batch check that reuses the single-product cost rule. It covers all 36 proposed component costs and all 18 buildable products with their 24 effective BOMs. All paired standard/alternate costs fit one conservative product standard cost within the configured 5% tolerance; the checker requires exact product and component coverage and retains `ready_for_full_generation: false`. The previously documented €715/€1,050 workstation pilot remains unchanged. Local `unittest discover`: 108 run, with 21 PostgreSQL-dependent tests skipped. Implementation commit: [`026468c`](https://github.com/alialnaggar/dealdeskdata/commit/026468c317732f09075aa8503240f2edb779689a).

The additional numbers are deliberately constructed synthetic arithmetic inputs. Most component costs use platform/family bases, and prices follow the resulting cost and proposed category p50 margin. This check is not independent market-price calibration or component compatibility proof. Representative database master rows, sourcing/price evidence and the four calibration plus 22 field reviews remain open before full generation. See the `Phase1C-portfolio-draft-review.md` file for the full boundary.

## Representative database master rows — 6 October 2026

`render_phase1c_master_slice.py` now maps a proposed workstation, rack server and storage array plus their referenced components into the actual PostgreSQL product, BOM and production-requirement columns. The five offered BOMs are checked for component platform support, selected substitute treatment and cost rollups against each finished product's one standard cost. `phase1c_master_slice.sql` applies the sample within a transaction and rolls back. A regeneration check prevents drift from the structural and synthetic cost JSON. [Push CI](https://github.com/alialnaggar/dealdeskdata/actions/runs/37456273773) and [PR CI](https://github.com/alialnaggar/dealdeskdata/actions/runs/37456279688) passed with PostgreSQL 18 at draft commit [`f11023f`](https://github.com/alialnaggar/dealdeskdata/commit/f11023f38c5eedb23bf9fd2f2d0f9f2527f7e9a5).

This proves a representative schema/relationship slice, not all 156 products or the full supplier/inventory/deal evidence graph. Inputs remain synthetic, including the workstation pilot margin mismatch (31.90% against the proposed category p90 of 28%). Full generation stays gated by price/source review, component compatibility, independent evidence, four calibration decisions and 22 field decisions.
