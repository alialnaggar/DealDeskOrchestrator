# Compatibility-condition field review — 15 October 2026

**Field:** `compatibility_rules.condition_json`. **Disposition:** open. The JSON contract lists five rule types: `requires_product`, `excludes_product`, `attribute_constraint`, `required_deal_field` and `installation_eligibility`. The imported-row validator checks the condition shape, rule type and V2 extension identity. The reader selects active rules by the run's catalogue version; the generic predicate evaluator handles the first four families, while installation/service region is checked through its separate reader path.

## Actual imported coverage

| Cohort | Current rules | Tested behavior and limit |
| --- | --- | --- |
| V1 development fixtures | `PILOT-SERVICE-COVERAGE` (eligible DE-NW) and `CONFLICT-SERVICE-OUTSIDE` (ineligible DE-NW), both `installation_eligibility` | Typed country/region/boolean checks, reader and PostgreSQL service cases. Coverage means region eligibility, not a dated appointment or crew booking. |
| V2 isolated dependency pilot | `V2-REQUIRES-ADDON`, `requires_product`, source and target are two cloned V2 sellable rows | The generated-test pair proves one pass and one Configuration failure, with version isolation and rollback. This rule is not imported globally into V1: prior impact audit found five historical and one development-pilot V1 conflicts if imposed there. |
| Generic evaluator tests | `requires_product`, `excludes_product`, `attribute_constraint`, `required_deal_field` | Unit tests cover pass/fail, configured groups, attribute/field reads and unsupported operator. These tests do not amount to a released distribution of generated rows for every rule family. |

The condition validator now also rejects malformed dotted attribute/deal-field paths, a non-boolean `exists.expected` and an empty/non-list `in.expected`. The focused local contract suite passed **13 tests**, including the new valid and invalid predicate cases. The CI PostgreSQL workflow runs that suite plus the imported-row validator and isolated V2 pass/fail regression. Existing valid fixture conditions and the 24-table schema are unchanged.

## Remaining evidence before closing the mark

1. Check the final generated-test/evaluation compatibility rows and selected reader findings per rule family; record which families are only unit-tested and why. Keep reviewer answer files separate.
2. For the bounded first release, decide whether V1 intentionally has only regional service rules and whether generic dependencies remain V2-only development coverage. No implicit global V1 dependency can be introduced because it changes earlier submissions.
3. Check negative/missing evidence and exact effective catalogue version in the final input replay. Region eligibility must not be called a confirmed installation slot. Record a `resolved_by` entry only for the actually supported scope.

No input packet, answer, field mark, policy threshold, calibration value or source cohort was changed by this validation tightening. Six field marks and two calibration evidence reviews remain open; accepted answers **0/36**; `ready_for_generation=false`; PR #1 draft.

## Pinned source-family inventory — 21 October 2026

`audit_phase1c_compatibility_scope.py` checks the actual V1 pilot SQL, isolated V2 dependency SQL and 36 v2 evaluation source definitions, without loading answer drafts. It finds two V1 `installation_eligibility` development rules, one V2-only `requires_product` rule, and four V1 `installation_eligibility` evaluation rows in cases 027–030. The evaluation inputs contain no `excludes_product`, `attribute_constraint` or `required_deal_field` rule row. Three focused local tests pass, including mutations that would move the dependency into V1 or change an evaluation rule family. The audit is wired into PostgreSQL CI with a source-scope artifact. Both full workflows passed at `ff468ec`: [push 39541377422](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39541377422) and [PR 39541381815](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39541381815).

This inventory protects the existing bounded scope and makes its coverage limit explicit. It does not validate every business meaning or accept expected findings. The compatibility mark remains open for final scope disposition and reader/source review.

## Generated development replay exposure — 21 October 2026

The 100-case batch copies the eligible V1 service template `PILOT-DEAL-05` into cases 014, 032, 050, 068 and 086; it copies the ineligible V1 service template `CONFLICT-DEAL-12` into cases 015, 033, 051, 069, 087 and 097. The batch has 89 other cases without service facts, including the V2 dependency pair 099–100. This is template exposure, not 11 independent service labels.

`test_phase1c_generated_test_batch.py` now checks the source template mapping and, on PostgreSQL replay, each selected service coverage rule ID, region and observed eligible/conditional versus ineligible/infeasible service fact. It also rejects service-fact leakage into other cases, requires no committed service slot, and confines applicable generic compatibility findings to the V2 dependency pair. The existing case-review artifact remains explicitly diagnostic with zero independently reviewed answers. These checks protect version and negative-case selection, not the business adjudication of an accepted outcome.

The field mark remains **open**: bounded V1/V2 release scope and evaluation reader findings still require explicit field review. None of the six field marks or two calibration evidence reviews is dispositioned here; accepted evaluation answers remain **0/36** and `ready_for_generation=false`.

## Evaluation reader-selection guard — 21 October 2026

The dedicated fresh-PostgreSQL, rollback-per-case evaluation export now checks the **selected** V2 reader view against the unchanged v2 source definitions. Cases 027–030 must each select exactly their own active V1 regional service rule, with matching version, service product, country/region, coverage rule ID and eligible/ineligible source boolean. The reader's service fact must report the corresponding regional coverage and no committed slot. With the rule omitted, the same reader helper must return `unknown`, not infer ineligibility. The other 32 cases must have no service facts or selected compatibility rule rows; all 36 have no generic compatibility finding. These are source/selection invariants, not accepted six-responsibility findings or whole-deal decisions. The pinned packets, index, source hashes, reviewer drafts and blank answer workspace are unchanged.

This protects the present narrow evaluation distribution. It does not settle whether the first release should explicitly exclude generic V1 dependencies and the three unit-only predicate families, or establish appointment capacity. Leave the compatibility field mark open until that bounded scope receives an explicit disposition; 0/36 answers accepted and `ready_for_generation=false`.

## Scoped first-release disposition — 22 October 2026

**Resolved for the actual imported rule families.** V1 development and v2 evaluation inputs use only regional `installation_eligibility` conditions. The V2 `requires_product` dependency is an isolated development pair with one observed pass and one fail, never a global V1 rule. `excludes_product`, `attribute_constraint` and `required_deal_field` remain validator/unit coverage only and are **outside generated first-release rule-family claims**. The strengthened source audit checks exact rule identities, source and target products, scope, blocker severity and condition values in the development fixtures. It also verifies the four evaluation rule IDs, source product, matching destination, eligible 027–028 and ineligible 029–030, and catches source mutations. The PostgreSQL generated-batch and evaluation tests check selected reader facts, missing-rule `unknown`, version isolation and absence of committed slots. See `audit_phase1c_compatibility_scope.py`, `test_audit_phase1c_compatibility_scope.py`, `test_phase1c_generated_test_batch.py` and `test_phase1c_evaluation_cases.py`.

This supports a `resolved_by` field-ledger entry only for that bounded scope. Reopen if V1 dependencies or other generic predicates enter generated/evaluation inputs, or if rule source facts change. Regional eligibility never establishes appointment capacity or an installation date. No source input, hash, answer or rule row changed. Four field marks and two calibration evidence reviews remain open, evaluation answers are **0/36**, case 020 is unresolved, `ready_for_generation=false`, and PR #1 remains draft.
