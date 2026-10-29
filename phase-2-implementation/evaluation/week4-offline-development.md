# Week 4 offline development evaluation

Nine distinct pinned synthetic deals, five binding-source shapes and four negative controls. 0/36 independently accepted evaluation answers; no semantic accuracy or real-model quality measured.

| Deal | Fixed original | Discovery (fixed) | Fulfillment AI execution / contribution | Other offline AI exceptions |
| --- | --- | --- | --- | --- |
| M18-D-B01 | needs_revision | True | completed / abstention | none |
| M18-D-B02 | needs_revision | True | completed / abstention | none |
| M18-D-B03 | needs_revision | True | completed / abstention | none |
| M18-D-B04 | needs_revision | True | completed / abstention | none |
| M18-D-B05 | needs_revision | True | completed / abstention | credit:error, policy:abstained |
| M18-D-N01 | needs_revision | False | completed / abstention | none |
| M18-D-N02 | needs_revision | False | skipped / None | policy:error |
| M18-D-N03 | needs_evidence | False | skipped / None | policy:error |
| M18-D-N04 | needs_revision | False | skipped / None | policy:error |

**Structural diagnostics:** {"accepted_answer_accuracy": null, "candidate_fixed_checked": 1, "candidate_fixed_rechecks": 6, "candidate_source_returned": true, "deterministic_mappings": {"completed": 54}, "fixed_discovery": {"discovered": 5, "not_discovered": 4}, "fulfillment_contribution_kinds": {"None": 3, "abstention": 6}, "hosted_reliability": "not_measured", "model_attempt_record_statuses": {"reserved": 89, "returned": 86}, "model_reasoning_quality": "not_measured", "model_turns_recorded_for_five_specialists": 89, "offline_ai_execution": {"abstained": 1, "completed": 46, "error": 4, "skipped": 3}, "original_cases": 9, "results_with_validated_claims": 40, "tool_budget_exhausted_events": 0, "tool_completed": 44, "tool_reserved": 44, "validated_claims": 40}

A separate B01 checkpoint runs a predeclared scripted two-slice Fulfillment hypothesis. The pinned verifier rechecks all six deterministic responsibilities; supply: `supply_supported_unreserved`, business: `needs_revision`, customer acceptance: `pending`. Matching the fixed discovery is **not** added AI value. No candidate is created in the nine original-only investigations.

Counts describe contracts, source visibility and fault containment, not model accuracy or business correctness against independent answers. Reserved and returned attempt records are ledger transitions, not unique provider sends or retries. This run exercises replay; interruption/no-replay and budget-exhaustion are tested separately, not measured here. Duration includes DB/checkpoint and is nonreproducible (fresh versus resume). No tokens or API cost exist offline. Execution `completed` may contain an abstention contribution; `error` is not a validated finding. N01 disallows partial delivery, N02 cancels inbound, N03 has stale stock evidence and N04 lacks supply. N01 can still enter Fulfillment investigation but cannot produce a permitted partial candidate. Conditional supplier offers are exercised by existing separate fault tests, not this cohort. The fixture cohort shares one product class, policy and region.

Stable projection SHA-256: `75036c5ccf36d77970c43342f3fe467ac386aefcafe9ea7b84e60c525e46c41b` (excludes timing only). Re-running on the same threads tests idempotence, not another independent case.

## Run

With the locked backend virtual environment, already-running local `/tmp/opencode` disposable PostgreSQL test cluster and clean exact pinned Phase 1C checkout, set `PYTHONPATH` to the Phase 2 backend and tests and run this single command (adjust the local PostgreSQL bin/lib paths if necessary):

```sh
python phase-2-implementation/backend/tests/run_week4_disposable.py \
  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --json /tmp/opencode/week4.json --markdown /tmp/opencode/week4.md
```

The command creates two **new** disposable databases, loads the pinned schema, reference rows, compiled rules and synthetic fixtures, then runs the offline cohort. It does not drop databases or install services. For an already preloaded paired recovery cohort, use `run_week4_development.py` with `--json` and `--markdown` instead. No provider credentials, answer sheets, live inference, activation, business reservation, approval or CI invocation are used.
