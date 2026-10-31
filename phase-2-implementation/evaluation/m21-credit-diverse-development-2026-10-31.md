# M2.1 isolated Credit evidence development — 31 October 2026

**Later disposition:** Ali discontinued Gemma and removed its uncommitted
tests; the [subsequent complete fresh-PostgreSQL local suite](m21-gemma-retirement-credit-diagnostics-2026-10-31.md)
passes 331/331 with no skips. The failures/skips below describe only the
earlier test environment, not the current suite.

**Development observations, not accepted-answer evaluation.** The pinned
Phase 1C checkout remains `90c0bc8e285ee69262c7db826b786096a77ad004`.
Three additional `M21CD-*` cases exist only in separately provisioned local
PostgreSQL databases, after the original nine M18 disposable cases. Neither
the 36 evaluation deals nor supplemental controls, Phase 1C files or dataset
pin were edited. Fixture row counts prove only a closed-world *synthetic*
assertion, not completeness of an external ledger.

| Case | Frozen original-source evidence | Fixed result | Fresh real-Groq Credit v2 |
| --- | --- | --- | --- |
| CR01 | Active profile, 100.00 original AR, 40.00 payment, 60.00 outstanding; fresh commitments | `calculated`, exposure 9160.00 | Inspected all three exact original refs; terminal response rejected (`terminal_semantics_or_evidence`). No validated claim. Assessment `GROQ-DEV-1737030252c24469935ca877f734c333`. |
| CR02 | Review/High profile, commitments dated 1 August against 1 September assessment; **no selected AR or payments** | `unknown`, stale commitments, exposure 9300.00, `PO-BASE-CREDIT-REVIEW` | Completed, cited only five exact original profile fields including `fixed_commitments_fresh=false`; no AR/payment or clearance claims. Assessment `GROQ-DEV-a4f60f71bae441eca153cc287a1e586c`. |
| CR03 | On-Hold/High profile, overdue 1200.00 original AR, 300.00 payment, 900.00 outstanding | `infeasible`, exposure 10100.00; `PO-BASE-CREDIT-ON-HOLD`, `PO-BASE-CREDIT-CAP`, `PO-BASE-OVERDUE-AR` | First response rejected as invalid action arguments (`action_arguments`), **before inspection**. No validated claim. Assessment `GROQ-DEV-135935f951984a7fade7850ce134b99e`. |

CR02's completed result is a valid *observation of incomplete evidence*, **not
an abstention or a resolved credit assessment**. Its fixed `unknown` result
remains authoritative. A valid `insufficient_evidence` abstention for that
empty-pool pattern is demonstrated by an offline typed-terminal mock only.
CR01/CR03 calculations
and record joins were checked against the pinned reader before sends; the
Credit model did not establish either transactional reasoning pattern as a
validated finding. No original/candidate data was merged, no candidate was
created, no deal was approved and no terminal/uncertain action was replayed.
All hosted cases used the standing free-tier coordinator, fresh business and
checkpoint databases, a credit-only two-POST maximum, exact case/subject
allowlists, private owner receipts, alias redaction and the existing strict
typed terminal verifier. The rejected cases are **failures**, not abstentions.

## Checks and limits

- Fresh-PostgreSQL source tests verified selected customer and original refs,
  original-minus-payment arithmetic, fixed exposure, freshness, status and
  rule IDs. Missing payments, changed freshness and mismatched AR fail the
  preflight. The CR02 absence is explicitly a fixture assertion; it does not
  mean zero external exposure. Redaction kept invoice/customer/payment IDs
  out of the model view, and mocked guarded Credit-only continuation preserved
  fixed results and rejected replay.
- Focused tests: **109 run, 107 passed, 2 skipped**. Non-Gemma full regression
  against independently fresh baseline/E2E business and checkpoint pairs:
  **328 run, 293 passed, 35 skipped**. One mixed-database run and two runs
  using previously occupied checkpoints failed as expected under identity
  guards; they were not counted as passing. A raw full discovery also reported
  two failures in unrelated uncommitted Gemma tests, left untouched. CI was
  not verified in this local run.
- No Fulfillment was called, so these trials neither reproduced nor explain
  its earlier HTTP 400. The CR01/CR03 Credit failures are locally categorized
  response-validation failures, not HTTP 400. There is no evidence to attribute
  either to a provider transport cause.
- M2.1 reliability is **not established** for receivable/payment reasoning or
  profile-plus-transaction interpretation. Investigate safe error categories
  and prompting with new fresh cases only if a meaningful diagnostic plan is
  available; retain hard evidence validation, legitimate abstention and
  no-replay guards. Formal accuracy requires accepted independent answers and
  the separate Phase 1C release/handoff. The N01 six-stage no-candidate result
  remains the distinct prior milestone.
