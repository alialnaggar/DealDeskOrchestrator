# Six-specialist offline development baseline

Pinned synthetic cases only; **0 independently accepted answer labels**. Scripted model actions are engineering probes, not evidence of real-model quality.
No Groq request, hosted activation, business write or deal approval.

| Case | Fixed review | AI executions (Fulfillment / Configuration / Pricing / Credit / Policy / Routing) | Candidate |
| --- | --- | --- | --- |
| M18-D-B01 | needs_revision | completed / completed / completed / completed / completed / completed | not_started |
| M18-D-B05 | needs_revision | completed / completed / completed / error / abstained / completed | not_started |
| M18-D-N03 | needs_evidence | skipped / completed / completed / completed / error / completed | not_started |

## What was exercised

- B01: one pinned original with six fixed mappings; the six eligible offline AI paths include a Fulfillment **abstention contribution** (its execution status is `completed`, not a model-supplied proposal). The fixed route is withheld; no customer commitment or approval occurs.
- B05: an invented Credit reference is rejected (zero validated Credit claims), Policy abstains, and the other domains' original fixed results remain intact. The Credit error is recorded by outcome code; the attempted raw claim is not reproduced in this sanitized report. The attempted AI finding is not ground truth.
- N03: stale source evidence prevents Fulfillment investigation; an empty Policy projection makes the scripted citation fail. Neither the skipped nor failed specialist is reported as an AI finding.

The companion JSON contains frozen source/run/bundle identities, six deterministic mappings of **one** Phase 1C decision, five validated AI-investigation results plus Fulfillment, bounded citation references, tool/attempt trace, abstentions and failures. Model-double actions and their outcomes are developer-authored; fixed-rule consistency is checked against the pinned decision, not independent human answers.

## Reproduce and interpret

Follow `.github/workflows/phase2-m1-contracts.yml` to provision **disposable** seven-DB PostgreSQL fixtures and a clean separate Phase 1C checkout at `90c0bc8e285ee69262c7db826b786096a77ad004`. Install the locked backend dependencies, load the pinned schema, reference rows, compiled rules and M1.8 synthetic cases in the disposable M20 business DB using `install_disposable_cases`. The CLI requires matching `recovery_*_m20` / `_m20_checkpoint` databases in a local `/tmp/opencode` test cluster and refuses arbitrary DBs. Export only `DEALDESK_PHASE1C_CHECKOUT`, `M20_DATABASE_URL`, `M20_CHECKPOINT_DATABASE_URL` and `PYTHONPATH` for the backend and tests; the runner refuses missing cases and never loads a fixture into an existing business DB. Run:

```sh
python phase-2-implementation/backend/tests/run_week3_development.py \
  --json phase-2-implementation/evaluation/week3-six-specialist-development.json \
  --markdown phase-2-implementation/evaluation/week3-six-specialist-development.md
```

Only the original-only six-AI composition is measured here. The existing M1.7/M1.8 Fulfillment candidate tests separately exercise a scripted binding proposal and full **six deterministic** candidate recheck; they are not a six-AI candidate continuation. No accepted answers are exposed to models. The 36 provisional Phase 1C packets have 0/36 independently accepted labels; no accuracy, improvement, model reliability, CI pass or hosted compatibility is inferred.
