# Provisional 100-case source review — 15 October 2026

**Scope:** development rule-regression submissions only. Source is the [passing PostgreSQL run 38682251976](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/38682251976) per-case `phase1c-generated-case-review` and aggregate `phase1c-generated-test-diagnostic` artifacts. These are observations from the reader and deterministic gate, **not expected answers or an independent evaluation sample**. The separate 36 v2 evaluation inputs and their reviewer-only drafts remain outside this set.

## Achieved diagnostic distribution

| Measure | Observed |
| --- | ---: |
| Submitted cases / lines | 100 / 101 |
| Archetypes / source templates | 20 / 20 |
| Distinct customers | 55 |
| Distinct attributed Availability source IDs | 47 |
| Attributed IDs used in just one case | 19 |
| Cases citing at least one reused attributed ID | 67 |
| Cases with no attributed Availability ID | 22 |
| Service lines: eligible / ineligible / booked slot | 11: 5 / 6 / 0 |
| Observed overall statuses | 23 `approval_required`, 12 `blocked`, 11 `needs_commitment`, 37 `needs_evidence`, 17 `needs_revision` |

The 101 lines comprise 36 stocked, 21 make-to-order, 17 supplier-finished, 16 digital and 11 scheduled service. All 20 archetypes have only one observed overall status within each group. This reflects bounded source templates and repeatable rule paths; it does not establish case-level correctness or a statistically varied real-world workload.

## Review of the 22 no-attribution cases

An empty `availability_finding_source_ids` list does **not** mean the reader saw no relevant source. The per-case report shows:

| Archetype | Cases | Reader-visible raw evidence | Why an attributed binding Availability ID may be absent |
| --- | ---: | --- | --- |
| `STOCK-ALLOCATED` | 6 | An inventory observation in every case, including five dated generated variants | Fully allocated stock contributes no free supply. |
| `STOCK-STALE` | 5 | An inventory observation in every case, including four dated generated variants | The observation is too old to establish current stock. |
| `SUPPLY-CANCELLED` | 5 | A cancelled inbound record in every case, with the same `CONFLICT-INBOUND-09` reused | Cancelled receipt is not binding supply. |
| `SUPPLY-OFFER-ONLY` | 6 | Supplier offers are reader-visible; the report previously omitted their IDs from its raw-source section | An offer is an uncommitted procurement possibility, not a confirmed receipt. |

The per-case artifact now lists `supplier_offers` IDs in `reader_visible_raw_source_ids`, and the database test checks that all six offer-only variants show an offer while their Availability finding source set remains empty. The test validates diagnostic visibility and the source boundary; it does not accept a deal decision.

## Disposition and next review

Retain this batch as a **provisional engineering regression** for deterministic reader, source selection and rule-path changes. The 22 cases have intelligible source reasons; no fabricated receipt, stock or provider proof should be added simply to reduce that count. The reused cancelled receipt, service coverage without slots, 20 templates and 67/100 reused-source cases limit breadth. Review individual deal inputs and findings before release; if broader operational diversity is a target, add dated independent synthetic states deliberately and rerun the entire batch and source exclusion registry. Keep any expected reviewer findings separate from observed statuses.

No historical diagnostic becomes a label, and no baseline or agent accuracy is scored here. Six field marks, two calibration evidence reviews and `ready_for_generation=false` remain open; 36 evaluation answers remain 0/36 accepted; PR #1 draft.
