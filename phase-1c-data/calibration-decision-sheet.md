# Phase 1C calibration decision sheet

**Scope selected by Ali on 12 October 2026: A, bounded synthetic model. Calibration and dataset remain provisional.**

## Where the data stands

The 24-table schema, 14 reference cases, reader, 36-deal development pilot,
80 synthetic customers and 400 historical submissions have passing PostgreSQL
checks. Dated operational sources replay at all 400 cutoffs. The diagnostic
deal decisions are not labels. The proposed 100-test set, separate 36-case
evaluation set and real agent execution outputs have not been released.

The 156-product catalogue has 120 sellable products and 36 components.
Eighteen sellable items are make-to-order with 24 offered BOMs. All 36 component rows now carry declared synthetic interface, form-factor,
power and cooling attributes. The catalogue-wide draft checker covers all
24 BOMs and 25 possible component selections. This establishes internal
synthetic fit for the current draft, not manufacturer-certified compatibility.

Prices and costs are also draft simulation inputs. The example workstation
has a €1,050 list price and €715 standard cost, yielding 31.90% catalogue
margin. Across all 18 make-to-order product drafts, this is the only margin
above its category's proposed p90 value (28% for this category); the other
17 are below their respective category p90 values. **A p90 is a target for a
category distribution, not a per-product ceiling.** This comparison alone
does not require changing the workstation price or cost, and 18 buildable
products are not the full 120-product sellable distribution. Its two selected
BOMs roll up to €683.33 and €705.33, within the shared-cost tolerance. These
arithmetic checks establish neither market prices nor purchasing costs. The
historical decision distribution is design-induced and provisional.

## Two choices to review

| Choice | A: bounded synthetic model (selected for the thesis scope) | B: sourced product model |
| --- | --- | --- |
| Components and fit | Define fictional, internally consistent kit specifications for all 24 BOMs. Check interface, slots, power and relevant thermal constraints. Explicitly state that these are synthetic assumptions, not manufacturer-certified configurations. | Identify comparable real product and component configurations, document dates and sources, then transform them to fictional rows with verified fit rules. |
| Prices and costs | Keep values as declared synthetic experimental parameters. Treat the workstation's 31.90% margin as one draft observation above the proposed category p90 of 28%, not an automatic failure. Check the full category distribution after generation, then adjust a *proposed* parameter only if the distribution or cost basis warrants it. Never claim a market margin. | Find dated like-for-like prices with matching currency, unit and tax basis. Costs still need a clearly synthetic procurement assumption unless supportable evidence exists. |
| Trade-off | Reproducible and suitable for testing agent decision correctness under stated assumptions; no claim that it mirrors a real provider's catalogue or margins. | Stronger external realism, substantially more sourcing and cross-part verification work before data freeze. |

**Decision rationale:** A. The thesis tests whether governed agents use available
facts and constraints correctly. A consistent synthetic company with explicit
assumptions supports that evaluation. It should still include genuinely
challenging and independently checked conflicts.

## What follows after the choice

1. Record Option A as selected; retain the review marks until their evidence
   and runtime mapping are checked.
2. Maintain the 36 catalogue component specifications and 24-BOM checker as
   one pinned, versioned synthetic assumption set.
3. Calculate achieved price, cost and margin distributions from all generated
   category rows. Review the workstation's cost and price basis in that context;
   keep values provisional until the check passes.
4. Recheck supplier calendars and compatibility rules; leave actual
   `agent_execution_log.output_json` open until real runs produce it.
5. Generate the 100 test submissions and author the 36 evaluation variants
   and their expected findings independently, outside agent-visible inputs.
   Only then rerun a fresh database import, provenance and repeat-seed checks.

No threshold or dataset label is frozen by this sheet. The current field
ledger still has six open marks and `ready_for_generation=false`.

## Quantified pre-integration audit — 12 October 2026

Before the Option A specification update, the portfolio and cost draft enumerated 156 products,
including 36 components, 18 make-to-order sellable products and 24 active
BOMs. Each component carries a platform and role but no interface,
form-factor, power or thermal specification; therefore none of the 24 BOMs
has enough detailed part attributes here to claim validated physical fit.
The separate five-part demonstration is still only an illustration.

The 18 draft buildable product prices/costs yield exactly one catalogue
margin above its proposed **category p90**: workstation
`SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009` at 31.90% against 28%.
That is a comparison with a provisional percentile target, not a breach of
a hard rule. It cannot establish the achieved percentile for all 120
sellable products or external price realism. No values or readiness marks
were changed by this audit.

**Decision recorded:** Ali selected A. The full generated category price/cost
distribution still needs review before calibration freeze.

## Option A implementation draft — 12 October 2026

Ali selected the bounded fictional specification and price/cost model. The
selection defines the evidence claim: internal consistency under declared
synthetic assumptions, not manufacturer-certified fit or observed market
margins. `implementation/phase1c_technical_fit_draft.json` explicitly lists
interface, form-factor, slot, power and cooling assumptions for all 36
components. `validate_phase1c_technical_fit_draft.py` checks all 24 active
BOMs and 25 possible selected component sets, including both candidates in
BOM-001. Failure cases cover mismatched shared interfaces, inadequate power,
slots and cooling, and a component declared for the wrong platform. The old
one-BOM pilot remains a narrow rule example.

The detailed assumptions have now been copied into the 36 draft component
catalogue attributes and allowed by the JSON contract. The fit checker rejects
any difference between those rows and the pinned companion file. The reader
can select these product attributes; the current candidate alternative runtime
does not yet use them to propose substitutions. The readiness audit reports
24 internally checked BOMs while retaining the price-comparability, sourcing,
independent-answer and actual-agent gates. Field-level review marks and
`ready_for_generation=false` remain until their full evidence review. No
threshold, list price, standard cost or schema changed.

## Provisional full-catalogue distribution audit — 12 October 2026

`implementation/audit_phase1c_price_distribution.py` reproduces the 120
sellable rows from the checked-in portfolio, 18 buildable cost drafts and the
same deterministic generator used for the other 102 rows. It uses linear
interpolation on the sorted rows for empirical p10, p50 and p90; percentages
below are rounded to two decimals. The checker rejects incomplete or
duplicate buildable costs and invalid price/cost values. Its CI artifact is a
diagnostic, not a market-calibration certificate.

| Category | Rows (generated / buildable) | Achieved margin p90 | Proposed margin p90 |
| --- | ---: | ---: | ---: |
| Cloud subscriptions | 12 (12 / 0) | 38.00% | 55.00% |
| Cybersecurity | 12 (12 / 0) | 32.00% | 48.00% |
| End-user workplace | 18 (16 / 2) | 18.18% | 28.00% |
| Enterprise software | 18 (18 / 0) | 45.00% | 65.00% |
| Support and warranty | 10 (10 / 0) | 42.00% | 60.00% |
| Networking | 16 (16 / 0) | 21.00% | 32.00% |
| Implementation services | 12 (12 / 0) | 48.00% | 65.00% |
| Servers and compute | 12 (2 / 10) | 16.07% | 25.00% |
| Storage and protection | 10 (4 / 6) | 19.01% | 28.00% |

All 102 generated rows are within 0.01 percentage point of their category's
proposed p50 margin because their costs are set directly from that p50. This
is an algorithmic concentration, not a finding about the market. The one
individual row above a proposed p90 remains workstation
`SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009` (31.90%); the achieved
workplace p90 is still 18.18%. An individual row can exceed a distribution
percentile without violating a hard rule. The report also groups price
percentiles by category, billing model and unit, so device prices are not
pooled with annual licences or monthly capacity. Even rows sharing those
fields may describe different product capabilities; these are not sourced
like-for-like comparables.

**Exact calibration decision for review before a freeze:** retain the fixed
p50 synthetic cost ratio as an explicit simplification, or specify a bounded,
seeded variation that produces a reviewed category margin spread. Either
choice must preserve each product's cost basis, BOM rollup and deterministic
replay, and must be tested on the same 120 rows. Separately review the
workstation cost/price assumption and the units, dates and tax basis of price
examples. This audit changes no prices, costs, thresholds, schema, field
marks or `ready_for_generation=false` status.

## Bounded margin spread sensitivity experiment — 12 October 2026

The read-only `implementation/experiment_phase1c_margin_spread.py` compares
the current catalogue with a **proposal**, leaving the SQL fixtures and
calibration YAML untouched. Within each category, it orders the 102 generated
product IDs by a SHA-256 digest of the configured seed and ID. It assigns a
margin within the existing proposed p10/p50/p90 band by linear interpolation
of rank, capped at p10 and p90, then recalculates synthetic cost from the
unchanged list price. The 18 buildable products keep their explicit BOM-based
draft costs. The JSON report includes the source-input digest and every
generated product's current and proposed cost, list margin and 10% discount
status. A changed seed changes the provisional draw as well as assignments.

| Diagnostic at a 10% quoted discount | Current fixture | Bounded experiment |
| --- | ---: | ---: |
| Sellable products | 120 | 120 |
| Generated products with recalculated cost | 0 | 102 |
| Buildable draft costs changed | 0 | 0 |
| Products below the BASELINE_2026 category margin floor | 12 | 41 |
| Products with nonpositive quoted margin | 0 | 2 |

Thirty-one product statuses change: 28 cross from at/above the floor to
positive below-floor margin, two cross to nonpositive margin, and one moves
from below-floor to at/above-floor margin. The current 12 below-floor products are all
servers. The experimental counts by category are cloud 3, cybersecurity 3,
workplace 7, enterprise software 4, support 2, networking 7,
implementation services 2, servers 11 and storage 2. The experiment expands
the achieved margin spread in most categories; the server category remains
largely fixed because ten of its twelve products are buildable and unchanged.
This is a **single-line arithmetic sensitivity check**. A positive below-floor line might be blocked or sent for an authorized
exception review under the full rules; the two nonpositive lines would meet
the baseline hard-block margin condition. This is not an agent decision or a
validated deal outcome.

**Decision for Ali before any calibration freeze:** whether to adopt a
reviewed bounded synthetic spread for the 102 generated products or retain
the fixed-p50 simplification. If adopted, review category shape, the effect
on each baseline/lenient/strict policy profile and the independent evaluation
cases before regenerating prices/costs and manifests. The proposed spread
still derives cost from a target margin rather than sourced procurement
evidence; it does not establish like-for-like commercial realism. The
workstation outlier, six field marks, two calibration reviews,
`ready_for_generation=false` and the independent answer gate remain open.

## Policy-profile sensitivity follow-up — 12 October 2026

The same read-only report now computes line-margin states for every sellable
product under the three configured policy profiles and 0%, 10% and 20% quote
discounts. The table counts lines below their category floor, **including**
nonpositive margin. Parentheses show nonpositive lines, which are a hard-block
margin condition in the profiles. Exact changed product IDs are in the
versioned CI report.

| Profile | Discount | Current below floor (nonpositive) | Proposed below floor (nonpositive) | Product statuses changed |
| --- | ---: | ---: | ---: | ---: |
| Lenient | 0% | 0 (0) | 0 (0) | 0 |
| Lenient | 10% | 0 (0) | 18 (2) | 18 |
| Lenient | 20% | 55 (39) | 65 (38) | 42 |
| Baseline | 0% | 0 (0) | 0 (0) | 0 |
| Baseline | 10% | 12 (0) | 41 (2) | 31 |
| Baseline | 20% | 55 (39) | 72 (38) | 46 |
| Strict | 0% | 0 (0) | 12 (0) | 12 |
| Strict | 10% | 55 (0) | 56 (2) | 39 |
| Strict | 20% | 79 (39) | 84 (38) | 50 |

At strict 10%, almost equal totals hide 39 changed product identities.
This supports retaining per-case findings in independent evaluation rather
than using an aggregate count as the answer key. The quote is an unrounded
arithmetic percentage of list price; discount approvals, exception windows,
deal totals, and other specialists are **not** simulated by this report.
Neither these observations nor the p10/p50/p90 targets authorize a
calibration freeze. The adoption decision above remains open.

## Versioned dependency pilot count — 13 October 2026

The 156-row V1 catalogue and its 120 sellable/36 component mix remain the calibration baseline. A separate generated_test V2 pilot extension clones two of its sellable fictional products with new versioned IDs to test a dependency rule without changing V1 submissions. The database holds 158 product rows when this extension is imported, but the category price and margin audit still measures the 120 V1 sellable products. The extra V2 rows are copies for rule coverage, not new market comparables or approval to freeze the two calibration reviews. `ready_for_generation=false`.


## 14 October 2026 — exact open calibration decisions

| Review | Evidence | Proposed choice for Ali |
| --- | --- | --- |
| Component/product mix | V1 has 156 products: 120 sellable and 36 components. The generated dependency pilot adds two V2 copies solely for rule coverage. | Accept the bounded fictional 36/156 V1 mix for Option A after field review of component fit; do not count V2 copies as market samples. |
| Price and cost basis | The 102 generated sellable costs target category p50. A read-only seeded spread changes 31 baseline 10%-discount product states and produces two nonpositive margins; source units, dates, tax basis and the €1,050 workstation need review. | Retain fixed p50 as a disclosed regression-data simplification for this first release, or choose the reviewed bounded spread and recheck all profile/deal effects before adoption. Neither choice claims market-comparable prices. |

These are proposals for review, not approvals. No cost, threshold, schema or release flag changes here; both calibration reviews and `ready_for_generation=false` remain open.
