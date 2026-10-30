# Credit source-first technical review — provisional v3

> Codex technical review, 30 October 2026. Proposed Credit findings only; no independent human adjudication, accepted answer, or whole-deal gate. The source is pinned v2 plus the explicit fictional v3 Credit scope. No model draft was used to calculate the table.

All rows have one matching active customer and active credit profile, a commitment observation 85 minutes (odd cases) or 95 minutes (even cases) before the run, 30-day submitted terms, zero authored AR/payment records, and a complete-zero *fictional v3* scope declaration. The 24-hour freshness rule applies to commitments. The v3 scope says the fictional customer invoice population is complete at the cutoff; it does not prove external zero balance or favorable payment behavior. Exposure below is the full quoted line plus stated unbilled commitments and EUR 0 selected AR. Baseline credit exception cap is 15% over limit; >15% is a hard block. The distinct source IDs and exact cutoff for each row are in `../credit_intent_review_v3.json` and `credit_scope_v3.json`.

| Case | Scenario | Quote € | Commitments € | Exposure € | Limit € | Proposed Credit disposition |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 001 | STOCK-READY | 3918.80 | 125.00 | 4043.80 | 260000.00 | No credit-limit issue on declared facts |
| 002 | STOCK-READY | 7595.20 | 250.00 | 7845.20 | 270000.00 | No credit-limit issue on declared facts |
| 003 | STOCK-ALLOCATED | 3918.80 | 375.00 | 4293.80 | 280000.00 | No credit-limit issue on declared facts |
| 004 | STOCK-ALLOCATED | 7595.20 | 500.00 | 8095.20 | 290000.00 | No credit-limit issue on declared facts |
| 005 | STOCK-STALE | 3918.80 | 625.00 | 4543.80 | 300000.00 | No credit-limit issue on declared facts |
| 006 | STOCK-STALE | 7595.20 | 750.00 | 8345.20 | 310000.00 | No credit-limit issue on declared facts |
| 007 | SUPPLY-CONFIRMED | 5645.40 | 875.00 | 6520.40 | 320000.00 | No credit-limit issue on declared facts |
| 008 | SUPPLY-CONFIRMED | 10941.60 | 1000.00 | 11941.60 | 330000.00 | No credit-limit issue on declared facts |
| 009 | SUPPLY-OFFER-ONLY | 5645.40 | 1125.00 | 6770.40 | 340000.00 | No credit-limit issue on declared facts |
| 010 | SUPPLY-OFFER-ONLY | 10941.60 | 1250.00 | 12191.60 | 350000.00 | No credit-limit issue on declared facts |
| 011 | SUPPLY-CANCELLED | 5645.40 | 1375.00 | 7020.40 | 360000.00 | No credit-limit issue on declared facts |
| 012 | SUPPLY-CANCELLED | 10941.60 | 1500.00 | 12441.60 | 370000.00 | No credit-limit issue on declared facts |
| 013 | BUILD-READY | 2037.00 | 1625.00 | 3662.00 | 380000.00 | No credit-limit issue on declared facts |
| 014 | BUILD-READY | 3948.00 | 1750.00 | 5698.00 | 390000.00 | No credit-limit issue on declared facts |
| 015 | BUILD-SUBSTITUTE | 2037.00 | 1875.00 | 3912.00 | 400000.00 | No credit-limit issue on declared facts |
| 016 | BUILD-SUBSTITUTE | 3948.00 | 2000.00 | 5948.00 | 410000.00 | No credit-limit issue on declared facts |
| 017 | BUILD-CAPACITY-STALE | 2037.00 | 2125.00 | 4162.00 | 420000.00 | No credit-limit issue on declared facts |
| 018 | BUILD-CAPACITY-STALE | 3948.00 | 2250.00 | 6198.00 | 430000.00 | No credit-limit issue on declared facts |
| 019 | BUILD-HORIZON | 2037.00 | 2375.00 | 4412.00 | 440000.00 | No credit-limit issue on declared facts |
| 020 | BUILD-HORIZON | 3948.00 | 2500.00 | 6448.00 | 450000.00 | No credit-limit issue on declared facts |
| 021 | DIGITAL-PROVED | 16528.80 | 2625.00 | 19153.80 | 460000.00 | No credit-limit issue on declared facts |
| 022 | DIGITAL-PROVED | 32035.20 | 2750.00 | 34785.20 | 470000.00 | No credit-limit issue on declared facts |
| 023 | DIGITAL-NO-PROOF | 16528.80 | 2875.00 | 19403.80 | 480000.00 | No credit-limit issue on declared facts |
| 024 | DIGITAL-NO-PROOF | 32035.20 | 3000.00 | 35035.20 | 490000.00 | No credit-limit issue on declared facts |
| 025 | DIGITAL-EXPIRED | 16528.80 | 3125.00 | 19653.80 | 500000.00 | No credit-limit issue on declared facts |
| 026 | DIGITAL-EXPIRED | 32035.20 | 3250.00 | 35285.20 | 510000.00 | No credit-limit issue on declared facts |
| 027 | SERVICE-COVERED | 42408.40 | 3375.00 | 45783.40 | 520000.00 | No credit-limit issue on declared facts |
| 028 | SERVICE-COVERED | 82193.60 | 3500.00 | 85693.60 | 530000.00 | No credit-limit issue on declared facts |
| 029 | SERVICE-OUTSIDE | 42408.40 | 3625.00 | 46033.40 | 540000.00 | No credit-limit issue on declared facts |
| 030 | SERVICE-OUTSIDE | 82193.60 | 3750.00 | 85943.60 | 550000.00 | No credit-limit issue on declared facts |
| 031 | CREDIT-LIMIT | 3918.80 | 900.00 | 4818.80 | 1000.00 | Hard credit cap (>15%; 381.88% over) |
| 032 | CREDIT-LIMIT | 7595.20 | 900.00 | 8495.20 | 1000.00 | Hard credit cap (>15%; 749.52% over) |
| 033 | PRICE-FLOOR | 3345.92 | 4125.00 | 7470.92 | 580000.00 | No credit-limit issue on declared facts |
| 034 | PRICE-FLOOR | 6691.84 | 4250.00 | 10941.84 | 590000.00 | No credit-limit issue on declared facts |
| 035 | POLICY-CLAUSE | 3918.80 | 4375.00 | 8293.80 | 600000.00 | No credit-limit issue on declared facts |
| 036 | POLICY-CLAUSE | 7595.20 | 4500.00 | 12095.20 | 610000.00 | No credit-limit issue on declared facts |

## Discrepancies and limits

- All 36 preserved v2 model Credit rationales call the empty collections a “complete snapshot,” while v2 alone does not contain that declaration. The v3 scope explicitly makes a *fictional* complete-zero claim for these case identities after individual source review. Retain the v2 drafts unchanged; compare only after a fresh v3 source-first review.
- Cases 031–032 exceed the 15% baseline exception cap even when selected AR is zero. A complete-zero declaration does not remove their hard credit issue. Other proposed no-issue rows rely on the new fictional completeness scope and require reevaluation if that scope or source facts change.
- Case 040 proposes a separate nonempty control: one €1,000 invoice, €300 payment and €700 overdue outstanding. Its provisional full-quote exposure is €4,743.80 (including €125 commitments and €700 AR). Rule selection, Policy and Routing findings require PostgreSQL replay and source-first review.
- Case 041 declares incomplete AR/payment evidence despite empty selected rows. The existing nonhistorical reader still adds zero to its arithmetic; it cannot yet turn this metadata into an evidence-gap finding. Do not score this control or call it a Credit clearance until the trusted projection and deterministic gate are verified.
- This table is a **Credit-only technical proposal**. Configuration, Pricing, Availability, Policy, Approval and overall human actions for every case still need source-first adjudication. Case 020's modal-route choice and 039's Configuration dependency remain distinct.

## Reviewer work

For each case, verify the v2 packet and provider hashes, match its v3 scope to the same customer/run/cutoff, inspect the selected credit profile and AR/payment rows, recalculate exposure and baseline rule, and record whether the proposed finding holds. Then review other five responsibilities and the exact human route. Compare preserved model/author drafts only afterward and disclose that assistance. Record accountable adjudicator, method, date, disagreements and source hashes in the separate reviewer-only intake. Accepted original answers remain **0/36**; controls **0/2** and Configuration 039 **0/1**.
