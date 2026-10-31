# Provisional v3 case-level technical review handoff — 30 October 2026

Codex technical synthesis, not independent human adjudication. The 36 v2 packet/provider hashes were rechecked against the pinned index from the last passing PostgreSQL export. Each original v3 input is its unchanged v2 packet/provider pair plus the separately bound fictional Credit scope. The existing source-first aids for [001–012](v2_batch_001_012_review.md), [013–024](v2_batch_013_024_review.md), and [025–036](v2_batch_025_036_review.md) give individual source pointers and six-responsibility prompts; the [Credit table](../credit-evidence-v3/credit_case_technical_review_v3.md) gives individual v3 Credit arithmetic. These are proposed review materials, not accepted labels.

| Cases | Source distinction | Tentative gate | Discrepancy or question |
| --- | --- | --- | --- |
| 001–002 | fresh stock | approval_required | check dispatch and routine route |
| 003–004 | fully allocated stock | needs_revision | distinguish revision from missing replenishment evidence |
| 005–006 | 49/61-hour-old stock | needs_evidence | refresh before asserting shortage |
| 007–008 | confirmed inbound and lane | approval_required | separate offer does not bind supply |
| 009–010 | offer only | needs_commitment | draft mentions a cancelled receipt absent from source |
| 011–012 | cancelled PO plus separate offer | needs_commitment | exclude cancelled receipt, require new commitment |
| 013–014 | fresh materials, unbooked workshop | needs_commitment | do not call capacity a booked slot |
| 015–016 | alternate component receipt | needs_commitment | verify BOM choice and later workshop |
| 017–018 | 51/52-hour-old capacity | needs_evidence | refresh capacity |
| 019 | late October PO plus earlier offer | needs_commitment proposed | maximum-lead earlier route needs supplier/workshop/dispatch commitments |
| 020 | late October PO plus earlier offer | needs_commitment proposed | Ali selected modal route only; six findings unaccepted |
| 021–022 | binding digital pool and matching full-term proof | approval_required | verify activation and anniversary |
| 023–024 | binding pool without separate proof | needs_evidence | reference alone does not prove coverage |
| 025–026 | provider proof ends before anniversary | needs_evidence | valid_until is not full term |
| 027–028 | regional eligibility true, no slot | needs_commitment | coverage is not appointment |
| 029–030 | regional eligibility false | needs_revision | Configuration versus Availability attribution |
| 031–032 | credit exposure >15% exception cap | blocked | no executable route |
| 033–034 | hard margin-floor failure | blocked | discount escalation does not waive block |
| 035–036 | legal_review clause | approval_required | check Regional Manager and Legal order |

For each of the 36 cases, an accountable reviewer must inspect its exact packet and v3 Credit scope first, then write Configuration, Pricing, Availability, Credit, Policy, Approval and overall findings with source IDs, rule IDs, arithmetic, human actions and unknowns. Only afterward compare the preserved model/author drafts. Their Credit rationales all asserted a complete snapshot before v2 had a declaration; the new v3 fictional scope needs explicit source binding, not retrospective rewriting of those drafts. Conditional supply, stale observations and provider gaps cannot be cleared by favorable Credit facts. Current blocked deals 031–034 have no executable approval route. Case 020's modal-route choice does not accept its six findings.

Supplemental [039](configuration_extension_scope_review.md) remains a separate Configuration dependency case requiring its own field-scope and six-finding review. Credit control 040 has one overdue invoice with EUR 700 outstanding after EUR 300 paid; 041 explicitly declares incomplete evidence, which the current reader does not yet enforce. Both require clean PostgreSQL replay, packet hashes and separate adjudication. All source-first technical recommendations are **hold pending a complete six-finding human disposition**. Accepted original 0/36, 039 0/1, Credit controls 0/2; ready_for_generation=false. Phase 2's pin remains unchanged.