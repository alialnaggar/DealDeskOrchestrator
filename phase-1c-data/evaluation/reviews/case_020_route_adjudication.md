# Case 020 — route and gate adjudication (15 October 2026)

**Decision pending; accepted evaluation answers remain 0/36.** This is a primary-author review of source facts and competing drafts, not an independent answer. It does not modify the v2 inputs, original model draft, author-assisted amendment, approved F1/C1/C2/G1/S1/R1 contract, or any calibration value.

## Source pin and reproducible check

- Branch head reviewed: `4d75a95ae007be784dc6b3b2c7a52d42c5a6a882`; v2 source-definition SHA-256: `1b7e0dffb3eaae8ee7c7e4bcd82aba0d55da11321198ce8c54e1581fae6740cc`.
- Case 020 packet SHA-256: `6edee7da614ce168e3422a3f1d013da26769f97e8378cacb107f0a55b036957b`; provider bytes SHA-256: `6f217c34d69b2ef93c2124ae6e08a565626e33da0d258b782934b99fb56efcf8`.
- Rechecked both hashes against the pinned index in PR workflow `38644128074`'s `phase1c-provisional-evaluation-inputs` artifact. Its separate source audit has 36 cases, 72 verified source/provider hashes and zero accepted answers. The case's min/mode/max projections below matched the audit artifact. These checks establish input identity and arithmetic, not a correct gate.

## Facts that matter

The customer submitted four workstations for **11 September 2026**; no submitted field selects a PO. Compute stock is zero. A confirmed PO has seven unallocated compute units arriving **2 October**, with no supplied post-receipt production capacity; it cannot establish a finished workstation delivery by the requested date. The active matching compute offer is for EUR 240 per unit, permits an order of four, and quotes **2/4/6 supplier workdays**. An order on 1 September is hypothetical; the offer is neither a receipt nor a reservation. The supplied assembly and test operations each need 2.5 hours for four units; dated weekday slots through 9 September show eight available hours each. The active lane has two weekday transit days and a 16:00 local dispatch cutoff. Sources: `/source_rows/deal`, `/source_rows/lines/0`, `/source_rows/inventory`, `/source_rows/inbound_supply/0`, `/source_rows/supplier_offers/0`, `/source_rows/requirements`, `/source_rows/production_capacity`, `/source_rows/shipping_lanes/0`.

| Offer lead | Indicative compute receipt | Assembly / test evidence | Indicative arrival | Limitation |
| --- | --- | --- | --- | --- |
| Minimum | Sep 3 | Sep 3 / Sep 4 | Sep 8 | All steps uncommitted. |
| Modal | Sep 7 | Sep 7 / Sep 8 | Sep 10 | Timely only if supplier, workshop and dispatch commit this specific route. |
| Maximum | Sep 9 | Sep 9 / no Sep 10 test observation | Unknown | Do not invent later capacity or a delivery date. |

The projection assumes the component is usable for assembly on its receipt day, operations occur on separate days, and completion meets the dispatch cutoff. Intraday arrival and completion times, other component allocation and actual booking are not certified. The approved G1 contract defines `needs_revision` when the submitted quantity/date/region cannot be supported as submitted, `needs_evidence` for missing adequate current facts, and `needs_commitment` for a feasible conditional alternative. It does not explicitly say whether one feasible modal route can determine the whole-deal gate while the maximum-lead route lacks a test slot. R1 makes Sales Director relevant to a **later customer date proposal**, rather than every deal containing a late PO.

## Exact choice for substantive review

**Proposed decision:** Treat the Sep 7 receipt → Sep 7 assembly → Sep 8 test → conditional Sep 10 arrival as a *specific feasible but uncommitted* route preserving the submitted quantity and date. Record `needs_commitment` as the proposed whole-deal gate, with supplier/workshop/dispatch commitments and a fresh six-responsibility check before any executable approval route. Keep the maximum-lead and October routes visibly unsupported for the original date. The routine Regional_Manager path is provisional information only. This is the author-assisted proposal and has **not** been accepted as an independent answer.

| Alternative | Gate treatment | Consequence |
| --- | --- | --- |
| Require support across the entire 2–6 day offer window | `needs_evidence` for the missing later test slot, or `needs_revision` if the chosen route is the October PO | More conservative; rejects the modal route as sufficient for the overall gate until a binding lead and schedule are obtained. If a later customer date is proposed, R1 adds Sales Director review. |
| Use the specific timely modal route subject to commitments (proposed) | `needs_commitment` | Preserves the customer's date as a conditional possibility, but cannot promise it. The maximum-lead path and intraday/dispatch uncertainty must remain explicit. |
| Assign a gate only after a selected sourcing route is bound to the submission | Defer the whole-deal gate pending route selection | Would add a new route-selection convention or input; version and review that choice before changing evaluation facts or implementation. |

**Review request:** Is the documented modal conditional route enough for case 020's proposed `needs_commitment` gate, or should the gate wait for a committed lead and dated Sep 10 test/dispatch evidence? Also verify the six responsibility findings and human actions before accepting a case answer. This is a case-level adjudication under the approved conventions, not a request to reapprove F1/C1/C2/G1/S1/R1.

Until then, retain the original v2 model draft and hash-bound author-assisted view separately; do not score a rule baseline or agents against either. The 100 regression cases and historical diagnostics remain development data. Six field marks, two calibration reviews and `ready_for_generation=false` remain open.
