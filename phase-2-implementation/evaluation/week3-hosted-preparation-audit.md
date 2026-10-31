# Week 3 hosted preparation audit — no hosted calls

## Later 28 October gated execution increment — still no provider call

The separately gated [M2.1 hosted entrypoint](../backend/dealdesk_phase2/m21_specialists.py)
now accepts **only one exact synthetic original per approved manifest hash**.
It refuses the published proposal status, a different model, secondary-key
selection, prompt/wire version, source fingerprint, as-of cutoff, snapshot,
owner inode or changed credential fingerprint. Each specialist still has one
authorized selected read, at most two turns, and no authority over fixed
calculations or approvals. `_post` is reused behind the same exclusive-owner
and durable `claim_and_call` audit primitive as the earlier transport; the
checkpoint records a request digest before the file receipt and network
invocation. A crash after reservation, HTTP 400, timeout, malformed response,
over-token response, tampered source, forged citation or exhausted budget
stops the assessment without any further specialist send. The first completed
inspection can be reconstructed from its saved descriptor and completed
permission ledger on restart without repeating it; a reservation without a
validated returned attempt is terminal. Only the explicit `authorized_one_case`
manifest status *plus a pre-existing private owner approval record binding
the hash/assessment and Free/no-billing gate* can unlock a send; the checked-in
proposed manifest cannot. Unknown receipts from other campaigns fail closed;
returned receipts must match the saved request hashes before a resumed send.
A crash after a returned terminal action but before final result checkpointing
is attributed `unrecorded_terminal_exchange`, not a bad model finding; the
response is unrecoverable and never resent. The exact
secondary key is never logged or sent to any metadata endpoint in this task.
On terminal hosted error, the original fixed reviewer package gains only a
sanitized `m21_ai: stopped` marker with empty claims; it never suggests an
approval or masks fixed results. A final post-marker fresh seven-DB regression
again passed **270 tests, seven unrelated Gemma skips, no failures**.

**Source-first conflict pilot survey:** an isolated database loaded the pinned
catalogue, vertical/conflict SQL and compiled rules without changing the
Phase 1C pin. `CREDIT-LIMIT` run `...260013` has one selected receivable,
zero payments, fixed Credit `infeasible` with `PO-BASE-CREDIT-CAP`, and a
withheld route. `POLICY-CLAUSE` run `...260015` has an approval-required legal
hit and a visible two-role route (`Regional_Manager`, `Legal_Compliance`).
Both passed actual selected-projection and redacted two-turn request-size
checks (all under 8,192 bytes). A separate in-memory-checkpoint,
mock-`_post` gated execution sent **six simulated POSTs** for each:
`CREDIT-LIMIT` produced completed Credit, a justified no-hit Policy
abstention and completed withheld Routing; `POLICY-CLAUSE` produced three
completed AI observations with the two fixed route roles retained. Both
preserved their exact original fixed results and created no candidate.
These are scripted model actions, not Groq outcomes. `PRICE-FLOOR` run `...260014` has discount-
and margin-related hard Policy hits, but repeats a discount-cap hit ID;
M2.1's duplicate-ref fail-closed policy projection prevents its hosted use
until a reviewed scoped-hit contract resolves that collision. No loaded
generated-test conflict case yielded a selected payment. A small separately
approved, dated synthetic payment row tied to an existing invoice in the
Phase 1C development fixture would be the narrowest data addition for that
coverage; do **not** change the pinned production data by implication.

**Offline results:** No-network focused mock Groq/checkpoint tests cover six
sequential tool-call continuations, source/redaction, exact-value claims,
restart after a completed inspection, malformed/forged model responses,
HTTP/timeout, pre-reservation crash, reserved crash, tampered manifest,
credential drift, per-turn limits and post-send campaign token stop.
The final post-review fresh **seven-database** PostgreSQL backend discovery ran **270
tests: 263 passed, seven skipped, zero failures**. All seven skips are the
same unrelated historical Gemma-checkpoint tests listed below; private CI
remains unverified. Mock success does not establish that Groq will accept
the request or that the model will reason correctly. The B01-only
[proposal and source coverage table](week3-hosted-validation-proposal.md)
must be reviewed by Ali before a separately authorized hosted assessment.
The unresolved Week 2 Pricing HTTP 400 remains independently terminal.

**Independent second-model review:** An attempted free Nemotron review was
unavailable; a read-only DeepSeek review identified self-certified approval,
cross-campaign directory, receipt integrity/error-attribution and manifest
numeric-type gaps addressed in the code/tests above. Residual limitations:
an importable Python capability sentinel is not a sandbox against arbitrary
same-process code; key rotation intentionally terminates an assessment;
private checkpoint backups contain a high-entropy secret-derived SHA-256
fingerprint; a terminal response lost between the returned-attempt checkpoint
and its final AI result cannot be safely reconstructed and is never resent.
These are not hosted validation results.

**28 October 2026.** Branch `phase2-agent-implementation` at starting commit
`faadfb946a0cedc351356fc89a3bc1122f2187fb`; the source of truth is this
repository. The already-uncommitted Gemma work and both ignored local Groq
credentials were left unchanged. No inference, metadata check or old B01
Pricing request was sent. CI for this increment has not been observed.

## Responsibility and evidence boundary

The Week 3 original-only LangGraph continues to use the pinned Phase 1C
aggregate for all six fixed findings. M2.1's internal selected credit, policy
and route projections are authorization-checked against exact original,
customer, source digest and cutoff; one read-only tool per specialist is
bounded by the shared ledger. A model's only accepted finding is an exact
typed scalar from a completed returned ref; fabricated refs, invented roles,
non-hit policy rules, malformed actions and boolean/number coercion are
rejected. No AI credit clearance, waiver, approval, business mutation or
candidate-subject tool exists.

New `m21_redaction.py` prepares a **provider-independent synthetic-only**
allowlisted view without invoice numbers, raw customer/receivable/payment
identifiers or commitment evidence IDs. Internal evidence and checkpoint
still retain exact selected refs. New dormant `m21_groq_contract.py` reuses
the agreed Groq model/native tool schema and the already-tested shared
`live_models._post` transport in mocked transport tests; it does **not** make
a hosted request. It validates one function call, exact redacted citations,
abstention and native call/result linkage. This is a wire contract, **not an
integrated live adapter**: provider errors/usage and durable pre-send request
identity have not yet been wired through M2.1's hosted path. The offline
M2.1 runner remains default-deny for any hosted model. Prompts stay trusted
system text; redacted evidence is user/tool data. A legacy reserved offline
turn remains no-replay after the prompt-version upgrade.

For synthetic B01's ten-unit original, the fixed Policy delivery hit is
approval-required and the route is withheld. An offline model can cite only
the returned fixed rule or route status; the fixed Credit decision, Policy
application and route remain intact. A forged Credit claim is contained as
AI error, and a separate Policy abstention does not change the fixed review.
The wire-double tests also reject a guessed customer/ref/amount, sensitive
unreturned fields, malformed functions, false/zero coercion and unexpected
extra source columns; a mocked HTTP 400 remains sanitized without reading
the provider's error body. They do not establish actual hosted model quality.

## Historical seven skips — superseded 31 October 2026

The seven skips in the **dated run below** belonged to the now-discontinued,
uncommitted Gemma diagnostic. Their modules and saved trial artifacts have
been removed with Ali's authorization. They are not current-suite skips;
this historical count does not establish Week 4 candidate integration,
cross-model evaluation, role-visible routing or nonempty AR coverage.

**Local checks:** Four focused no-network Week 3 redaction/Groq-wire tests
passed. Full `unittest discover -v` against **seven newly created isolated
PostgreSQL databases**, pinned Phase 1C source and compiled fixture rules:
**263 tests, 256 passed, seven skipped, zero failures**. The seven skip
names/reasons above come from that verbose run. No private GitHub CI status
was verified. The [proposed source-verified identities and budgets](week3-hosted-validation-proposal.md)
still require a separate executable hosted gate and Ali's explicit approval.

## Week 4 and Week 2 limits

Week 4 still needs separately scoped candidate-subject Credit/Policy/Routing
evidence and fully checked candidate reruns; independent accepted evaluation
answers and controlled hosted experiments; a real, source-reviewed populated
AR/payment and role-visible route case; and human-only reviewer UI/approval.
The two terminal B01 Pricing HTTP 400 attempts remain an unresolved **Week 2**
blocker; the [offline wire review](m20-pricing-http400-offline-diagnosis.md)
did not prove cause and neither request may be replayed. Week 3 original-only
evidence or mock transport success cannot close Week 2.
