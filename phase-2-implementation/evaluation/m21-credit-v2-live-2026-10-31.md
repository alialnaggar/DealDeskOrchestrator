# M2.1 Credit v2: two fresh real-Groq original assessments

**31 October 2026. Development observations, not formal evaluation.**
After the local `groq_daily_limit` expired, two fresh six-stage synthetic
assessments used the existing free-tier coordinator, separate disposable
PostgreSQL business/checkpoint databases, the pinned Phase 1C fixture and the
committed `credit-observation-v2` prompt. No terminal assessment was replayed,
no paid API was used and no model saw candidate-subject M2.1 evidence.

| Fresh case | Six AI contributions | Credit exact returned observations | Candidate fixed verdict |
| --- | --- | --- | --- |
| B01 `GROQ-DEV-fb11524ad4b94e52913e259a19115079` | Six validated | `credit_profile:M18-C-B01`: `credit_status=Active`, `credit_limit=1000000.00`, `fixed_commitments_fresh=true`, `risk_rating=Low`, `unbilled_committed_amount=0.00` | Fixed checked; supply `supply_supported_unreserved`; deal `needs_revision` |
| B05 `GROQ-DEV-2c20a480783d40329afbc21e74e7a45c` | Six validated | `credit_profile:M18-C-B05`: same five exact fields, plus `last_review_date=2026-08-20` | Fixed checked; supply `unknown_or_unavailable`; deal `needs_revision` |

Both original reviews still say `needs_revision`. Both candidate Routes remain
withheld; customer acceptance is pending. `Active` is an observed credit
profile status, **not** credit approval, a cleared blocker or authorization
to upgrade a candidate. Both Credit model outputs passed exact-ref, field,
type and value validation after one authorized original-subject inspection.
These two cases provide **first real-model evidence** that Credit v2 can
produce valid observations without forcing a finding. They do not establish
that the revised prompt *caused* the improvement: model variability and two
small, synthetic profiles remain alternative explanations. Abstention must
remain available for incomplete or uncertain evidence.

Fulfillment's successful final requests were 9,883 bytes (B01) and 9,888
bytes (B05), both with strict-schema SHA-256
`4d9077a08f5b1129a83ca05b434a84b9eae1dfa22440332fa4ceb674ca0977f6`.
Neither produced HTTP 400. The earlier HTTP 400 receipts have no bounded
final-request metadata or usable safe provider category, so there is still
**no failed-versus-successful final comparison** and no evidenced root cause.
No validator, strict schema, tool-to-final transition or deterministic rule
was changed for these trials. Further identical retries are unlikely to
resolve this without a fresh failed receipt; no more hosted calls were made.

## Separate outcome counts across 11 fresh B01/B05 assessments

| Outcome | Count |
| --- | ---: |
| Complete six-stage workflows | 6 |
| Complete workflows with six validated AI contributions | 2 |
| Credit contract-valid `model_uncertainty` abstentions | 5 (one followed by Routing failure) |
| Fulfillment provider HTTP 400 | 3 |
| Routing provider HTTP 429 | 1 |
| Local daily-limit stop before Fulfillment decision send | 1 |
| Observed local structured-output or evidence-validation failures | 0 |
| Fixed-checked candidate / no candidate | 7 / 4 |
| Complete workflow without candidate | 0 |

These are observed outcomes, not measured accuracy or an independently
accepted answer-key comparison. Before hosted sends, 44 focused tests ran
(42 passed, 2 skipped); a fresh-checkpoint PostgreSQL/LangGraph regression
afterward ran **94 tests (92 passed, 2 skipped)**. Phase 1C still owns the
unreleased data/answer set. Its handoff should clarify completeness semantics
for empty selected Credit AR/payment sets; do not invent evidence or alter
the frozen Phase 1C pin. The next reliability milestone is a fresh, safely
diagnosed Fulfillment failure if one occurs, broader diverse cases including
genuine no-candidate completions, and formal evaluation only after the
approved Phase 1C release and explicit dataset handoff.
