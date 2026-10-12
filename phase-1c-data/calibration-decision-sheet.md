# Phase 1C calibration decision sheet

**Scope selected by Ali on 12 October 2026: A, bounded synthetic model. Calibration and dataset remain provisional.**

## Where the data stands

The 24-table schema, 14 reference cases, reader, 36-deal development pilot,
80 synthetic customers and 400 historical submissions have passing PostgreSQL
checks. Dated operational sources replay at all 400 cutoffs. The diagnostic
deal decisions are not labels. The proposed 100-test set, separate 36-case
evaluation set and real agent execution outputs have not been released.

The 156-product catalogue has 120 sellable products and 36 components.
Eighteen sellable items are make-to-order with 24 offered BOMs. All 36
component rows declare a platform and role, but **none has detailed interface,
form-factor or power attributes** in the catalogue. A separate five-part,
one-BOM synthetic fit example tests two substitute kits; it is a rule
demonstration, not sourced product compatibility. The other 23 BOMs lack
that detailed check.

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

1. Record the selected scope and revise the two calibration review entries.
2. Extend the component specifications and fit checker from one illustrative
   BOM to all 24, or source the chosen real comparables.
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

## Quantified draft audit — 12 October 2026

The repository's current portfolio and cost draft enumerate 156 products,
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

**Decision needed before calibration freeze:** choose the bounded fictional
component and pricing model (A) or the sourced comparable model (B) in the
table above. Under either choice, check fit for all 24 BOMs and assess the
full generated category distributions; the audit does not settle that choice.

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

The detailed assumptions are currently a **companion review draft**. They are
not yet part of the catalogue rows selected by the runtime reader, and
passing a fit check does not close product-attribute/compatibility field marks
or `ready_for_generation`. Next map reviewed specification fields into the
catalogue and rule contracts, check the price/cost distribution for all
sellable rows, and independently review evaluation answers. No calibration
threshold, list price, standard cost or schema was changed by this step.
