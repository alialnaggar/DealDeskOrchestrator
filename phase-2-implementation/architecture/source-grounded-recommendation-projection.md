# Source-grounded recommendation and comparison projection

**Contract:** `source-grounded-review-v1`, `dealdesk_phase2.recommendation_review.project_source_grounded_review(state, adapter, checkpoint_pending=False)`. Read-only Python function over **one existing completed six-stage assessment**; it is neither an API, persisted reviewer decision, model call nor candidate composer. Source pin remains `90c0bc8e285ee69262c7db826b786096a77ad004`. No Phase 1C source or business rule changes.

## Integration and authority

The caller uses an authorized assessment's PostgreSQL LangGraph checkpoint (`graph.get_state({"configurable": {"thread_id": assessment_id}})`). Check `snapshot.next` before invoking; pass `checkpoint_pending=bool(snapshot.next)` so an interrupted run fails closed. Pass the exact pinned `Phase1CAdapter`; do **not** pass a model-generated dictionary or accept a client-supplied assessment ID without authorization. `capture_m22` validates six fixed slots, original/candidate subjects, verified model citations, attempts and reviewer package. The projection additionally reassembles the original fixed decision from the sealed bundle, rechecks the Fulfillment binding proposal against returned authorized tool sources, reconstructs candidate identity/field changes, compares fixed candidate trace slices to cited proposal slices, and uses `project_gap_review` for separately labeled evidence/interface limitations. A reserved-only/failed/incomplete stage cannot become a review. Checkpoint/receipt reconciliation and access control still belong to the future server API; this function does not assert receipt verification, fresh DB re-verification or hosted model reliability.

Typed `SourceGroundedReviewV1` returns immutable identities and hashes; separate `SubjectV1` for original V0 and optional candidate V1, with six fixed findings and allowlisted fixed rule IDs each. `ai_original_execution` and allowlisted `{ref,field}` citations appear **only** under V0; V1 has six *deterministic* results and no candidate AI claims. The original requested date and line quantities remain unchanged; `candidate_comparison.changed_field` is only `proposed_delivery_slices`, with exact proposed quantities/dates/source refs, original shortage, candidate supply status, unreserved status, pending customer acceptance, mitigated original reason and remaining revision reason. Approval-required *policy hit* IDs are separate from the `required_roles` field; withheld Routing sets roles to **null**, never `[]`/no roles. Each evidence gap has a coded requirement/reason, `verification` and next-action code; selected-ledger incompleteness is not confirmed-zero credit. All recommendations have specialist, action code, verification type (`deterministic` or `suggested_unverified`), subject and cited refs/rules. Action codes request **human** review/acceptance/evidence, not approval, reservation or a customer commitment. The only authorized delivery state in the DTO is `human_only_not_granted`.

Example **sanitized excerpt** from scripted RC01/B01 assertions (illustrative ID/hash omitted, not a historical hosted assessment or complete schema):

```json
{
  "version": "source-grounded-review-v1",
  "original": {
    "subject_kind": "original", "subject_id": "M18-D-B01",
    "business_status": "needs_revision", "requested_delivery_date": "2026-09-04",
    "lines": [{"line_id": "M18-L-B01", "quantity": 10}],
    "availability": [{"line_id": "M18-L-B01", "status": "late_alternative",
      "requested_quantity": 10, "quantity_by_requested_date": "8.000",
      "earliest_full_date": "2026-09-08"}],
    "revision_reasons": [{"line_id": "M18-L-B01", "code": "requested_date_not_supported"}],
    "approval_requirements": [{"rule_id": "PO-BASE-DELIVERY-LATE", "severity": "approval_required"}],
    "routing_roles_status": "unavailable_while_route_withheld", "required_roles": null
  },
  "candidate": {"subject_kind": "candidate", "business_status": "needs_revision",
    "specialists": {"fulfillment": {"fixed_finding": "needs_revision",
      "ai_original_execution": null}}},
  "candidate_comparison": {
    "changed_field": "proposed_delivery_slices",
    "proposed_slices": [
      {"quantity": 8, "delivery_date": "2026-09-03", "source_refs": ["inventory:M18-INV-B01"]},
      {"quantity": 2, "delivery_date": "2026-09-08", "source_refs": ["inbound_supply:M18-IN-B01", "inventory:M18-INV-B01"]}
    ],
    "fixed_supply_status": "supply_supported_unreserved",
    "reservation_status": "not_reserved", "customer_acceptance": "pending",
    "unmet_customer_constraints": ["original_requested_delivery_date"],
    "remaining_revision_reasons": ["partial_delivery_requires_customer_acceptance"]
  },
  "authorization": "human_only_not_granted"
}
```

The actual DTO additionally carries assessment/run/bundle/source identities, full six-domain fixed/AI status and gap codes, proposal/lineage IDs, recommendation actions and human handoff. Neither `supply_supported_unreserved` nor six-slot Fulfillment `needs_revision` overrides the other: the former verifies available supply for an *unreserved* revised schedule; the latter and overall `needs_revision` retain unmet customer terms. RC01 Configuration, Pricing and Credit return `no_fixed_blocker_in_selected_evidence`, not approval or a complete financial ledger claim. Policy retains its late-delivery approval-required rule, and Routing withholds roles.

**No-candidate:** `candidate`/`candidate_comparison` are null, with original findings and any unresolved evidence gaps still visible. An unsupported requested date yields an explicitly `suggested_unverified` Fulfillment recommendation to investigate an alternative with a human, not a fabricated proposal. **Failure:** missing, malformed, mismatched, cross-subject or incomplete records raise `EvidenceMismatch` (or the existing strict validator error); no partial/provisional review is returned. Neither model text nor provider receipts, raw sealed bundles, private credit amounts/receivable IDs, rejected claims, authentication material or raw unrestricted policy payloads are serialized. The caller must still apply authentication, field-level permissions and receipt reconciliation before exposing the DTO through a future Python API. The UI must label scripted offline versus hosted execution using a separately trusted run registry; this DTO does not infer it. V0→V1→V2, source-writing/acceptance, candidate-specific AI reassessment and stock reservation remain **unimplemented**.

## Offline checks

The local pinned Phase 1C checkout, existing `/tmp/opencode` PostgreSQL cluster and locked backend venv were used without hosted requests. Focused `python -m unittest -v test_recommendation_review test_m21_hosted_gate.M21HostedGatePostgres.test_integrated_credit_reconciled_candidate_offline test_m21_hosted_gate.M21HostedGatePostgres.test_integrated_credit_held_no_candidate_offline test_m21_hosted_gate.M21HostedGatePostgres.test_integrated_credit_incomplete_no_candidate_offline` with `PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests`, `DEALDESK_PHASE1C_CHECKOUT=/tmp/opencode/dealdesk-phase1c-pinned` and separate `M20_DATABASE_URL` / `M20_CHECKPOINT_DATABASE_URL` passed **6/6 in 72.055 s** on the final projection code. It checks true RC01 source quantities/dates and Policy IDs, HC03 blocker/not-zero handling, UC02 abstention, missing/forged refs, source/digest/cross-subject tampering, reserved checkpoint status and restart-stable output. The full discoverable suite passed **364/364 in 308.707 s**, provisioned on eight **fresh disposable** databases using the CI-equivalent Phase 1C schema/reference/compiled rules and `python -m unittest discover -s phase-2-implementation/backend/tests -p 'test_*.py' -v`. No Phase 1C files, held-out inputs, answer keys, business rules or validator semantics were changed.
