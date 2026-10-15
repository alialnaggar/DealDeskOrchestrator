# Phase 1C catalogue calibration review card — 15 October 2026

**Decision requested:** settle the two open V1 catalogue calibration reviews for the bounded fictional Option A selected by Ali on 12 October. This card is a proposal, not an approval or a calibration freeze. The approved F1, C1/C2, G1, S1 and R1 evaluation conventions are unaffected.

## Source pins and tested facts

- Branch `phase1c-candidate-contract`, draft [PR #1](https://github.com/alialnaggar/DealDeskOrchestrator/pull/1); [passing PostgreSQL run 38678607112](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38678607112) at `1bfb848de4dabb7003bd0fa4a36af7d4b3359bb6`. The run's `phase1c_price_distribution.json`, `phase1c_margin_spread_experiment.json` and 36 `EVAL-PREP-*.json` input packets supplied the comparisons below. The margin experiment's source input digest is `03e99abb2db78c9b6c345807552fc785935124c73fb293b38cd14d86f5bffc51`; seed `22495`.
- V1 has **156 products: 120 sellable plus 36 components**. Eighteen sellable products are make-to-order, with 24 active BOMs and 25 possible component selections. Two cloned V2 sellable rows exist only for a dependency-rule pilot; they do not enter the V1 120-row margin audit.
- All 102 generated sellable rows have costs targeting their category's proposed p50 margin. The nine achieved category p90 margins are below the nine proposed p90 targets. The workstation `SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009` lists at €1,050, costs €715 and has 31.90% catalogue margin, above its provisional category p90 of 28%. That percentile is not an individual hard cap. Its selected BOM rollups are €683.33 and €705.33 within the declared tolerance.
- The read-only seeded spread changes costs of the 102 generated rows only. List prices, the 18 buildable costs and the three policy profiles stay fixed. At a hypothetical **10% discount** under `BASELINE_2026`, the current catalogue has 12 positive below-floor lines and zero nonpositive lines; the experiment has 39 positive below-floor and two nonpositive lines. **31 product status identities change.** These are single-line arithmetic diagnostics, not observed deal gates or agent answers.

## Decision 1: component/product mix

**Proposed decision:** retain the 36/156 V1 fictional mix and its pinned synthetic technical-fit assumptions for the first thesis data release. Record the 120 sellable/36 component denominator and exclude the two V2 dependency copies from distribution claims. This is sufficient for internally reproducible fictional scenarios; it does not establish manufacturer-certified fit or a representative market mix.

**Alternative:** redesign the V1 component and sellable mix. That changes catalogue identities/relationships and requires a new version, all affected BOM/compatibility and generator checks, historical/development/evaluation impact assessment and PostgreSQL replay. There is no source evidence in this review that calls for a particular replacement mix.

## Decision 2: generated price/cost basis

**Proposed decision:** retain fixed category-p50 synthetic cost ratios for the 102 generated V1 sellable products as an explicitly disclosed first-release simplification. Keep the 18 buildable draft costs, including the workstation, with their separate BOM basis. Do not call these market-comparable prices or sourced procurement costs. The narrow achieved margin distributions remain a declared limitation; review source units, dates and tax basis as synthetic fixture definitions during the product-field mark disposition.

**Alternative:** adopt a **reviewed** bounded seeded cost spread. The current experiment is an option to inspect, not an adopted fixture. Review each category shape and all three profiles first, pin seed and cost algorithm, revise the cost basis, version the master catalogue and manifests, then replay the 400 historical diagnostics and 100 provisional development regressions. The 36 evaluation inputs must be checked and versioned; do not silently alter v2 or transplant its draft answers. A different seed or spread may have different results. This experiment still derives cost from target margins rather than purchase evidence.

### Exact v2 evaluation impact of this experiment

The 36 exported v2 packets each have one submitted line, covering five distinct product IDs. The cost in every affected v2 line matches the current V1 cost in the spread report. **Four generated products cover 28 cases whose line cost would change** under this particular seeded experiment. The other eight cases, 013–020, use the unchanged make-to-order workstation. The following are cost references, not accepted findings or projected overall decisions:

| Cases | Product suffix within `SELL-…` | Current → experimental unit cost | Scope |
| --- | --- | ---: | --- |
| 001–006, 031–036 | `END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-001` | €1,656.40 → €1,719.53 | 12 cases |
| 007–012 | `END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-006` | €2,386.20 → €2,363.47 | 6 cases |
| 013–020 | `END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-009` | €715.00 → €715.00 | 8 cases, buildable |
| 021–026 | `CLOUD_SERVICES_AND_SUBSCRIPTIONS-001` | €440.20 → €546.70 | 6 cases |
| 027–030 | `PROFESSIONAL_AND_IMPLEMENTATION_SERVICES-001` | €11,367.20 → €7,651.00 | 4 cases |

For example, using **each packet's actual quoted unit price** and only replacing that line cost, case 001's arithmetic quoted margin moves from 15.46% to 12.24%; case 021 from 36.08% to 20.62%; cases 033/034 from 0.99% to **−2.78%**. Cases 033/034 are already hard-blocked under the existing draft review; this hypothetical extra margin fact does not supply an executable approval route. No six-responsibility gate has been recomputed or accepted from this substitution. Any adoption needs new source packets and fresh substantive review under the approved contract.

## Recorded choice and follow-through

| Review | Proposed choice | Status |
| --- | --- | --- |
| V1 mix | Retain bounded fictional 36 components / 156 products | **Awaiting Ali's explicit decision** |
| Generated cost distribution | Retain fixed-p50 first-release simplification | **Awaiting Ali's explicit decision** |

After a choice, record its rationale in the calibration configuration and decision sheet; then review the five source-data field marks against that choice. If either alternative changes shared facts, version and replay the affected inputs before case-answer review. The six field marks, two calibration reviews, **0/36 accepted answers**, `ready_for_generation=false` and draft PR status remain unchanged at this proposal stage. The case-020 route decision is separate and still open.
