# Supplier calendar field review — 15 October 2026

**Field:** `suppliers.order_calendar_json`. **Disposition:** open. The [data contract](phase1c_data_contract.yaml) specifies ISO working weekdays, an empty holiday list and an IANA time zone. The imported-row validator `validate_phase1c_generated_rows.py` already applies that contract to every loaded `suppliers` row and rejects offers whose referenced supplier lacks a typed calendar. The development pilot has at least one such linked offer, verified in PostgreSQL. These are synthetic supplier assumptions, not actual availability or a purchase commitment.

## Historical source gap

The pinned `phase1c_historical_offer_source.json` has SHA-256 `7e6052d02e84d6185621a8749daa29d6dd198ec5d2749e5aa8bbb8bbba600e78` in `phase1c_historical_operational_index.json`. It contains **162 synthetic offers** for 54 products over three quarterly windows, using **ten supplier IDs**, across the 400 registered historical cutoffs. Each offer has a modal lead value, validity dates and a verification instant. The source has **zero typed calendars and zero complete minimum/mode/maximum lead triplets**. There is no pinned historical supplier-calendar registry to join to these IDs.

The reader only emits a dated `supplier_offer_estimates` route when an offer carries a usable supplier calendar and the full lead bounds. It does not invent a date from modal days. The offer may still indicate a conditional procurement possibility, but it is **not a binding receipt, verified calendar schedule or delivery promise**. No historical decision label is inferred from this audit.

`audit_phase1c_historical_supplier_calendars.py` verifies the source against the pinned index and reports those coverage counts. Three focused tests pass: the present source has no dated estimate fields, tampering is rejected, and a calendar by itself still cannot supply missing lead bounds. CI preserves a separate source-only JSON artifact. The development, historical and evaluation cohorts remain distinct.

## Required closure work

1. If historical dated offer alternatives are in scope, define ten **fictional, versioned supplier calendars** with source owner, zone, weekdays and the declared no-holiday convention; add valid min/mode/max lead bounds to offers. Do not use a current supplier row to backfill an earlier cutoff.
2. Version and regenerate the historical operational source, index and all affected cutoff snapshots. Verify as-of visibility, active/valid offer filtering, supplier identity, calendar/lead arithmetic and distinct receipt versus uncommitted-offer status. Replay the 400 historical diagnostics and compare the resulting source IDs and decisions; do not turn those observations into labels.
3. If historical offer dates are deliberately outside this release, explicitly restrict the field-mark claim to the imported development/evaluation rows and retain the absence of historical dated routes as a documented limit. Review the final generated-test and evaluation offer links before a `resolved_by` entry.

No fixture, source hash, schema, threshold, calibration choice or answer was changed in this review. The field mark and the two calibration evidence reviews remain open; all six field marks open; accepted evaluation answers **0/36**; `ready_for_generation=false`; PR #1 draft.

## Evaluation source join check — 21 October 2026

The separate pinned **v2 evaluation input** contains 36 local synthetic supplier rows with typed calendars and ten active, locally joined supplier offers in cases 007–012, 015–016 and 019–020. Each of those offers has a nonnegative ordered min/mode/max lead triplet and a validity window containing its run cutoff. `audit_phase1c_evaluation_supplier_calendars.py` reports only these source joins; five focused tests reject a missing supplier, invalid calendar, inverted lead range or expired offer. CI preserves the source-only report without answer material.

This check does not establish an accepted route or adjudicate case 020's modal-versus-maximum-lead issue. The **162 historical modal-only offers remain without dated estimates**, and the 100-case development batch reuses pilot offer states rather than providing independent supplier-calendar evidence. The field mark remains open pending a deliberate historical scope disposition and final imported-row/reader review. No evaluation input, source hash or answer changed; accepted answers remain **0/36** and `ready_for_generation=false`.


## Incomplete-offer reader boundary — 21 October 2026

The reader now emits a nonbinding supplier date range only when a local calendar has a valid IANA zone, unique ISO workdays and the declared empty holiday list, and when all three lead values are nonnegative, typed integers in min/mode/max order. Missing or malformed dated evidence leaves the offer as an undated conditional possibility; it cannot be completed from a current supplier calendar. The source-only historical audit still pins the original 162 offers, and a separate test passes a hypothetical calendar to each modal-only offer to verify that a calendar alone does not produce dates. The 36 evaluation source rows and ten matched offers are untouched; the existing database reference test checks the complete-calendar path and its nonbinding status.

This is a defensive reader correction, not a historical calendar registry or a decision on whether dated historical routes belong in the first release. The supplier field mark, all other field marks and two calibration evidence reviews remain open. Evaluation answers stay at 0/36; `ready_for_generation=false`; case 020 is not adjudicated.
