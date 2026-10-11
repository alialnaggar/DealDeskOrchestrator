# Phase 1C calibration decision sheet

**Prepared 11 October 2026. Status: review proposal, not a frozen dataset.**

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
margin, above the proposed category p90 margin of 28%. Its two selected BOMs
roll up to €683.33 and €705.33, within the shared-cost tolerance. Those
arithmetic checks do not establish a comparable market price or purchasing
cost. The historical decision distribution is design-induced and provisional.

## Two choices to review

| Choice | A: bounded synthetic model (recommended for this thesis scope) | B: sourced product model |
| --- | --- | --- |
| Components and fit | Define fictional, internally consistent kit specifications for all 24 BOMs. Check interface, slots, power and relevant thermal constraints. Explicitly state that these are synthetic assumptions, not manufacturer-certified configurations. | Identify comparable real product and component configurations, document dates and sources, then transform them to fictional rows with verified fit rules. |
| Prices and costs | Keep values as declared synthetic experimental parameters. Resolve the workstation's 31.90% versus 28% mismatch by changing a *proposed* parameter or marking it as a documented exception; regenerate dependent rows and rerun distribution tests. Never claim a market margin. | Find dated like-for-like prices with matching currency, unit and tax basis. Costs still need a clearly synthetic procurement assumption unless supportable evidence exists. |
| Trade-off | Reproducible and suitable for testing agent decision correctness under stated assumptions; no claim that it mirrors a real provider's catalogue or margins. | Stronger external realism, substantially more sourcing and cross-part verification work before data freeze. |

**Recommendation:** A. The thesis tests whether governed agents use available
facts and constraints correctly. A consistent synthetic company with explicit
assumptions supports that evaluation. It should still include genuinely
challenging and independently checked conflicts.

## What follows after the choice

1. Record the selected scope and revise the two calibration review entries.
2. Extend the component specifications and fit checker from one illustrative
   BOM to all 24, or source the chosen real comparables.
3. Reconcile the workstation outlier and calculate achieved price, cost and
   margin distributions from generated rows. Keep current values provisional
   until the check passes.
4. Recheck supplier calendars and compatibility rules; leave actual
   `agent_execution_log.output_json` open until real runs produce it.
5. Generate the 100 test submissions and author the 36 evaluation variants
   and their expected findings independently, outside agent-visible inputs.
   Only then rerun a fresh database import, provenance and repeat-seed checks.

No threshold or dataset label is frozen by this sheet. The current field
ledger still has six open marks and `ready_for_generation=false`.
