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
