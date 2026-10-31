# Supplemental 039 — compatibility field scope and technical recommendation

Status: **source-first technical review only**. Original 36-case acceptance remains 0/36; supplemental 039 remains 0/1. Reviewer provenance: model-assisted preparation with source inspection, 30 October 2026. This is neither a qualified independent reviewer decision nor an accepted answer.

## Pinned input and isolated scope

The separate configuration extension index pins case 039 packet SHA-256 `83f65e17b9bfddee6bd32f76742678f3bf60c8e4ffea94d2d3d6479f717b2b99`, provider file SHA-256 `6f217c34d69b2ef93c2124ae6e08a565626e33da0d258b782934b99fb56efcf8`, and source definition SHA-256 `2e3a4dc2bf25e1df4b1d79f93b73ba98b79adfb5b71de983c1c659192eaf9d7e`. Its base v2 source definition is `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`. The indexed packet and provider must be rechecked against a fresh import before accepting a finding.

| Source fact | Source location and consequence |
| --- | --- |
| Run uses `CATALOGUE_2026_V2`, cutoff 2026-09-01 12:01 UTC, snapshot `EVALCFG-003-SOURCES` | `source_cases.json`, 039 `deal_runs[0]`; V2 rules must be selected only for this run. |
| One submitted line, product `SELL-END_USER_COMPUTING_AND_DIGITAL_WORKPLACE-004-V2`, quantity 2 | 039 `deal_lines[0]`; the target add-on is absent from the submitted line set. |
| One V2, active-on-version `requires_product` rule, `whole_deal`, `blocker`, source 004-V2 and target 005-V2, `present` | 039 `compatibility_rules[0]`; proposed Configuration finding is an unmet dependency and a human revision action to include the target add-on or revise the proposal. |
| Provider manifest has zero records | 039 `provider_manifest.records`; no external provider proof is inferred. |

The V1 regional service rules in original cases 027–030 and the isolated V2 development pair 099–100 have distinct scopes. Case 039 is a separately versioned **evaluation** of the generic V2 dependency family. Its presence supports a bounded field disposition for V2 `requires_product` only after selected reader and negative/missing-evidence replay. It does not establish coverage for `excludes_product`, `attribute_constraint`, or `required_deal_field`, and it must not change V1 historical submissions or the Phase 2 pin.

## Review recommendation and open checks

Proposed Configuration finding: `issue_identified` for the absent required product, with a `blocked` overall gate under the approved synthetic business contract, retaining other specialist findings and human actions. The rule's blocker severity is a source fact; the selected rule, evaluator output, catalog identity, all six responsibilities and overall precedence still require fresh PostgreSQL replay and accountable case-level review. No answer is accepted by this note.

Before the field mark is closed: import the 039 fixture in a fresh isolated database; verify selected rule ID, type, version, source and target IDs, missing target, evaluated Configuration finding and packet/provider SHA-256; check omission gives unknown rather than a fabricated failure; inspect other five specialist source facts and actions. Record a separate field-scope disposition that names the V2 family and excludes untested families. Do not generalize the result to all compatibility rule types.
