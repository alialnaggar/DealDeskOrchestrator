# Offline Deal Desk release candidate — operator acceptance (29 October 2026)

**Scope:** reproducible *development* demonstration, not a production release,
approved deal, independently scored thesis evaluation, or hosted-model trial.
The [executed demonstration](dealdesk-offline-demo.md) and
[structured trace](dealdesk-offline-demo.json) are projections of the same
[nine-case offline evaluation](week4-offline-development.json); the projection
verifies the evaluation's stable hash before writing anything. Models are
scripted offline doubles. Exact Phase 1C pin:
`90c0bc8e285ee69262c7db826b786096a77ad004`.

## Operator command (repository root on Oracle Ubuntu)

Prerequisites: an already-running **disposable** local PostgreSQL test cluster
using `/tmp/opencode`, a clean separate exact pinned Phase 1C checkout and the
repository's locked backend virtual environment. This script does not install,
restart or reconfigure PostgreSQL. For the current Oracle test environment:

```sh
mkdir -p /tmp/opencode/dealdesk-offline-release-candidate
export PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests
/tmp/opencode/dealdesk-test-venv/bin/python phase-2-implementation/backend/tests/run_week4_disposable.py \
  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --json /tmp/opencode/dealdesk-offline-release-candidate/week4.json \
  --markdown /tmp/opencode/dealdesk-offline-release-candidate/week4.md
```

Each invocation creates a **new** pair of disposable `recovery_*_m20` business
and `recovery_*_m20_checkpoint` databases on that cluster. The output directory
also receives `dealdesk-offline-demo.json` and `dealdesk-offline-demo.md`. The
CLI checks the socket, cluster data directory, clean Phase 1C pin, PostgreSQL
bin/lib paths and distinct output paths; it will not connect to a provider or
write deals into existing business databases. It does not drop its new test
databases. The external test cluster and pinned checkout must already exist.

## Expected acceptance checks

1. The demo's B01 original has six fixed results and **six distinct AI
   execution slots** (five evidence-checked citations; Fulfillment completes
   with an abstention). Its fixed review is `needs_revision`, the route is
   withheld and the final reviewer action explicitly requires human review.
2. B05 rejects a fabricated Credit reference, Policy abstains; N03 skips
   Fulfillment because evidence is inadequate, while Policy records an error.
   No rejected/skipped finding is counted as a valid AI contribution.
3. A separate B01 assessment proposes a scripted binding two-slice alternative.
   Its original and candidate use the same sealed bundle/source digest but
   different assessment IDs. All six **fixed** candidate responsibilities
   recheck; supply is `supply_supported_unreserved`, business remains
   `needs_revision`, customer acceptance is `pending`. No reservation,
   delivery promise or approval occurs. This is *not* six-AI candidate work.
4. Inspect the trace and returned evidence references in JSON. Structural
   metrics are in `week4.json`: nine original deals, 54 fixed mappings, 54
   scripted AI execution slots (46 completed, four errors, three skips, one
   abstained execution), 40 validated claims, five fixed discovered splits and
   four no-split controls. Two independently provisioned DB cohorts reproduced
   the stable Week 4 hash
   `75036c5ccf36d77970c43342f3fe467ac386aefcafe9ea7b84e60c525e46c41b`;
   timing and random database names are excluded. A second run on one thread
   is an idempotency check, not a new independent case.
5. CI was intentionally skipped to avoid billable Actions. Fresh local tests:
   **26 focused passed** (`/tmp/opencode/dealdesk-rc-focused.log`) and
   **328 full seven-database tests passed**, with seven unrelated Gemma skips
   (`/tmp/opencode/dealdesk-rc-regression.log`). No Groq calls or activation
   were made.

## Release decision and non-claims

**Accept for local offline operator demonstration only.** This is evidence of
source-bound orchestration, fixed-rule authority, checkpoint/restart behavior,
bounded permissioned tools and rejection containment under scripted inputs;
the existing integration tests separately cover interruption, no-replay,
budget and candidate correction. It is not a measurement of real LLM quality,
accuracy, usefulness or comparative advantage. The 36 provisional Phase 1C
packets still have **0/36 independently accepted answers**; developer-authored
model-double findings are never treated as ground truth. The fixture family
shares a product class, policy and region, and the Credit/Policy/Route source
views remain limited for nonempty AR/payment and role cases. There is no
combined six-AI candidate continuation or reviewer UI.

**Next gates, kept separate:** source-first nonempty Credit/Policy/Route cases
and candidate-subject AI isolation; independent review/acceptance of case
answers, then blinded semantic evaluation against identical deterministic-only
baselines. Real Groq validation additionally requires the separately documented
owner approval, free-tier/billing and credential checks, fresh exclusive test
identity, reviewed activation/manifest and a strictly bounded hosted trial.
The typed-final gate stays dormant; previous hosted HTTP 400s do not establish
compatibility or reliability. Never replay spent sends or infer approval from
this acceptance report.
