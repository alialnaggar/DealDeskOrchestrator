# Evaluation contract decisions for Ali — pending, 14 October 2026

**Recommendation: approve the bounded evaluation-contract proposal below for a versioned second review. This is not a calibration freeze, schema change or acceptance of the 36 answers.** No proposal in this document has been adopted. The first-pass source pin and model draft remain intact. Accepted independent answers: **0/36**.

## Evidence and method

Source of truth: `alialnaggar/DealDeskOrchestrator`, branch `phase1c-candidate-contract`, inspected at `75459dcbca883c8ed91da04ce295244277999dc6`; PR #1 was draft with no comments/reviews and both PostgreSQL workflows passed. Input definitions remain pinned at SHA-256 `5b3168a6871ebb2cfdcaa0c594c9ff6e34ab300708661146c22a994f85a09977`; canonical packet index digest `07f85eeee8902619446c1c49a678987b867e4bfc82930d0c88e499948b560527`.

The new [source audit](../../implementation/audit_phase1c_evaluation_contract.py) verifies all 72 packet/provider hashes before calculating ages and comparing offer costs only with the same product's submitted-line or BOM standard cost. It does not import the reader/decision engine, read authoring intentions or model answers, or produce expected gates. It reports explicit JSON pointers for every observation. Three tests cover the inclusive time boundary/future timestamps, component identity versus finished-product cost, incomplete indexes and source/provider tampering. The full report is a CI artifact, not another checked-in copy of the inputs.

Reproduce from the implementation directory after obtaining/exporting the pinned source packets:

```sh
python -m unittest -v test_phase1c_evaluation_contract
python audit_phase1c_evaluation_contract.py --packet-directory /tmp/phase1c_evaluation_packets --index ../evaluation/provisional_packet_index.json > /tmp/phase1c_evaluation_contract_audit.json
```

The default 24-hour comparison is explicitly an observation of the current implementation, **not an independently approved business rule**. For the current inputs, the report SHA-256 is `dedd1c3dd5f3afe602d843c61e2c5d5d756d0afe7a71b8495c6b4ca0c97e016d`. CI repeats the audit byte-for-byte against a fresh PostgreSQL export. This is source/audit reproducibility, not evidence that a model answer is correct. Review findings and author implementation inspection remain separate.

## 1. Declare the evidence-age contract

| Cases | Source and age at assessment | Current first-pass issue |
| --- | --- | --- |
| 005 / 006 | Inventory: 49 / 61 hours | Model flagged freshness uncertainty but no business limit was supplied. |
| 017 / 018 | All 16 production-capacity observations per case: 51 / 52 hours | Model failed to qualify these old observations. |
| Other 32 | Audited inventory, capacity, digital and credit snapshots are within 24 hours | This alone establishes neither sufficient quantity nor a commitment. |

**Proposed decision F1:** publish an explicit fictional evidence contract: inventory, production capacity, digital-capacity observations and credit commitments must be at or before the assessment timestamp and no more than 24 elapsed hours old (24 hours is included). Future or older observations do not establish current availability/exposure. Request refreshed evidence rather than interpreting missing/stale evidence as proof of impossibility. Independently supplied provider proof must be at or before assessment and no more than seven elapsed days old, with matching identity/quantity/term and valid binding dates. These proposed numbers document the existing reader conventions (`phase1c_reader.py::_fresh`, `_digital_proof`), not an externally validated SLA.

For digital term coverage, explicitly require `covers_from <= requested_activation_date` and `covers_until >= activation_date + contract_months`, with calendar-month addition clamped to the last day for shorter months. This conservatively requires coverage through the anniversary date; it is a simulation convention, not a legal contract interpretation.

If Ali prefers other limits or a different end-date convention, record the exact values before changing any input, implementation or answer. Any adoption requires a versioned system-visible contract included in future source fingerprints and a new reviewer pass; retain the original pass as evidence of the missing contract.

## 2. Remove the arbitrary evaluation-offer cost and declare costing precedence

| Cases | Same-product offer / standard cost (EUR) | Difference (EUR) |
| --- | --- | --- |
| 007–012 | 47.50 / 2,386.20, finished product | -2,338.70 |
| 015–016 | 47.50 / 50.00, network component | -2.50 |
| 019–020 | 47.50 / 240.00, compute component | -192.50 |

`render_phase1c_evaluation_cases.py::build.offer` hardcodes 47.50 for every offered SKU. This is an authoring placeholder, not a sourced bargain. The audit matches product identity before comparing costs; a component offer must never be compared to the finished desktop's cost. Equal product IDs do not independently establish equal tax, unit or loaded-cost bases.

**Proposed decision C1:** in the second evaluation input version, replace those ten arbitrary offer values with each same-product declared standard cost: 2,386.20 in 007–012, 50.00 in 015–016, and 240.00 in 019–020. Explicitly declare EUR per catalogue unit, fictional tax-exclusive values, without an additional freight/tax adjustment in these cases. Leave all master prices/costs, quotes, policy thresholds, historical/pilot/100-case data and calibration parameters unchanged. This removes an incidental distraction rather than testing procurement discounts; future discount scenarios would need deliberate, justified authoring.

**Proposed decision C2:** quote-margin arithmetic uses the submitted line's versioned catalogue standard cost. An offered procurement price supports an uncommitted purchase alternative and does not silently replace the commercial margin cost. The workstation EUR 715 standard cost is a declared synthetic loaded-cost input. A null `cost_parameters` means the packet does not support an independently reconstructed labour/overhead rollup; do not invent one or claim a reconciled BOM cost. If BOM reconciliation is to be scored, supply its separate complete cost assumptions and review them first. This is a proposed evaluation accounting convention, not evidence that the existing catalogue is market-calibrated.

## 3. Publish gate and service/routing meanings before a second review

The author inspected current implementation **after** saving the model's first pass. Its behavior is evidence about a business-contract gap, not an oracle to copy into labels:

- `phase1c_reader.py` uses regional `installation_eligibility` records for `scheduled_service` even when `installation_requested=false`. `phase1c_compatibility.py` excludes that rule type from ordinary product dependencies. `phase1c_deal_decision.py` treats unsupported service coverage/date as a revision, separately from an ineligible requested installation.
- `phase1c_deal_decision.py` gives hard blocks precedence, then required revision, then missing evidence, then uncommitted supply/service, then an approval route. This hierarchy was not declared in the source packets.
- `phase1c_policy_decision.py` routes a supported-but-late physical alternative to at least Sales Director, while the submitted requested date still requires revision. A delivery-late trigger alone does not justify inventing a Finance Director requirement.

**Proposed decision G1:** make these business meanings explicit for all future inputs: `blocked` means a hard prohibition/invalid configuration; `needs_revision` means the submitted quantity/date/region cannot be supported as submitted and requires a changed proposal; `needs_evidence` means the assessment lacks adequate current facts; `needs_commitment` means a feasible conditional alternative still needs a supplier/provider/production/service commitment; `approval_required` means the applicable human route can be presented, never approval granted. Apply precedence in that order while retaining all subordinate findings and human actions. A missing supply option and a feasible uncommitted option must remain distinguishable. Review the allocated-stock and cancelled-receipt cases individually; these definitions do not assign their answers automatically.

**Proposed decision S1:** retain the existing regional eligibility record type for this bounded prototype and explicitly document its two uses: requested installation eligibility and scheduled-service regional coverage. An eligible service region does not establish a booked slot; an ineligible region requires a changed service/destination proposal. `installation_requested=false` removes an additional installation request, not the service line's regional requirement. No schema rename is proposed. Ali may instead choose a future separate predicate, but it must be designed and reviewed before adoption.

**Proposed decision R1:** disclose the current fictional escalation convention: supported-but-late physical fulfillment requires at least Sales Director review of any proposed date change, with higher roles/additional Finance or Legal roles only when their own explicit rules trigger. Human/customer acceptance and source commitments remain separate. No gate or route promises delivery.

## Adoption sequence and remaining gates

Ali can approve F1, C1/C2, G1, S1 and R1 together for the bounded second review, or specify exceptions. A generic continue is not recorded as acceptance of these substantive decisions. After explicit decisions:

1. Add the approved business contract to system-visible inputs and source hashing; update the evaluation offer generator if C1 is approved. Preserve the current index, inputs/provenance and first-pass answers.
2. Regenerate a versioned 36-case input set, verify all hashes and affected source differences, and rerun all cohort/reproducibility/reader checks.
3. Obtain a renewed source-based review with the declared business contract. Record any implementation-informed reviewer exposure; do not call the primary author's revised labels independent. Keep any fresh reviewer from earlier model answers/author expected gates during drafting.
4. Record substantive human verification and case-level acceptance before scoring. The current 36 drafts remain unaccepted, including apparently straightforward cases; no answer is accepted by this proposal or by CI.

This does not close the six field marks or two calibration reviews. The separate fixed-p50 versus spread and V1 product-mix decisions remain on the [calibration sheet](../../calibration-decision-sheet.md). The 24-table schema remains unchanged and `ready_for_generation=false`. The review protocol and caveats remain in [the model review record](model_review_record.md).
