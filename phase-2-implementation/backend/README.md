# M1.0 — Pinned reader and replay boundary

**M2.0 offline continuation:** See the
[Configuration/Pricing methodology and limitations](../evaluation/m20-configuration-pricing-offline-methodology.md)
for the opt-in post-original LangGraph, separate read-only tools, corrected
mock Fulfillment candidate, fixed checks and reviewer handoff. The pinned
Phase 1C source and human-only approval boundary remain unchanged. The
[CI workflow](../../.github/workflows/phase2-m1-contracts.yml) provisions
separate disposable M2.0 business/checkpoint databases so its tests do not
silently skip; no hosted model is invoked by the test suite.

**M2.0 hosted results (historical approvals spent):** The
[completed B05 Fulfillment result](../evaluation/m20-groq-wire-continuation-hosted-result.md)
passed fixed candidate verification but did not approve, reserve or promise
delivery. The later [B01 Configuration/Pricing result](../evaluation/m20-configuration-pricing-hosted-result.md)
accepted Configuration's native two-turn investigation; Pricing's native
inspection returned but its paired follow-up stopped at HTTP 400. The
[offline structural diagnosis](../evaluation/m20-pricing-http400-offline-diagnosis.md)
found no demonstrated transport root cause. Both assessment identities are
spent. `m20_groq.py` remains an opt-in native-tool adapter, not authorization
for new inference or automatic retry. Offline tests mock all provider calls.

**M2.1 original-only offline extension:**
[`m21_specialists.py`](dealdesk_phase2/m21_specialists.py) defines three
separate typed Credit, Policy and Routing observations, one read-only
same-subject/pinned projection per specialist and scripted-model LangGraph
continuation. The existing fixed Phase 1C results retain business authority.
The [scope, adversarial cases and gaps](../evaluation/m21-credit-policy-routing-offline-methodology.md)
are documented; no M2.1 hosted or candidate investigation exists. For the
full suite, follow the same two-checkout CI setup below and supply distinct
`M20_DATABASE_URL` and `M20_CHECKPOINT_DATABASE_URL` disposable databases:
M2.1 tests reuse these isolated fixture connections, without sending inference.

**B05 second-turn wire diagnostic:** The authorized hosted attempt stopped
after one successful native inspection and a second-request HTTP 400. The
[offline diagnosis and new, unauthorized continuation proposal](../evaluation/m20-groq-second-turn-offline-diagnostic.md)
document the missing assistant-call/tool-result pairing in the saved second
request and the corrected hosted decision wire. The old B05 reservation
must never be replayed; the new wire has passed mocked-HTTP pinned PostgreSQL
tests, **not** a new Groq inference call.

**Status:** Implemented and tested against Phase 1C commit
`90c0bc8e285ee69262c7db826b786096a77ad004`. This is a read-only
integration foundation, not a LangGraph graph or an AI specialist.

## Two-checkout setup

Check out this repository's `phase2-agent-implementation` branch and a second
copy at the exact Phase 1C commit in separate directories. Set
`DEALDESK_PHASE1C_CHECKOUT` to the absolute path of the pinned second checkout,
`PYTHONPATH` to this `backend` directory, and `DATABASE_URL`/standard `PG*`
variables for an **isolated disposable thesis test database**. Use the existing
Phase 1C CI dependencies (`psycopg[binary]>=3.2,<4`, `PyYAML>=6,<7`) and
PostgreSQL client. The [M1 CI workflow](../../.github/workflows/phase2-m1-contracts.yml)
is the executable setup reference: it asserts the checkout SHA, applies the
pinned schema, loads the actual 14 reference rows, compiles the pinned rule
profiles, and runs `python -m unittest discover -s
phase-2-implementation/backend/tests -p 'test_*.py' -v`.

The adapter rejects a different commit or changes to tracked Phase 1C
implementation files. Generated Python caches are ignored. It imports the
pinned modules from the separate checkout; no Phase 1C source is copied here.
Each reader call is in a `REPEATABLE READ READ ONLY` transaction. The adapter
does not call Phase 1C's writing development runtime or commit business data.

## Evidence and measured size

`RunContextV1` pins run/deal, as-of time, snapshot, catalogue, policy, config
and source identities. `seal` encodes the bounded reader bundle into canonical
typed JSON; it handles tuple dictionary keys, dates, timezone-aware datetimes,
time, Decimal and UUID without lossy string fallback. The SHA-256 detects a
changed serialized bundle. A candidate reread first checks the original
selected source and run context in one new read-only transaction, then uses
Phase 1C's correlation check for the candidate in that same transaction.
Digest or identity mismatch stops that verification.

Passing [CI run 39244070977](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39244070977)
ran eight tests against the pinned Phase 1C checkout and disposable PostgreSQL
18 service. It measured:

| Actual Phase 1C reference case | Canonical UTF-8 bundle | Other storage observation |
| --- | ---: | ---: |
| Binding stock plus confirmed inbound (`stock_then_confirmed_receipt`) | 38,717 bytes | 59,228 bytes from `pg_column_size` of the JSONB expression |
| Conditional supplier offer (`offer_without_supplier_commitment`) | 37,814 bytes | Not measured as JSONB |

The JSONB expression is a size proxy, **not** a LangGraph checkpoint row or a
measured restart/latency result. No LangGraph checkpointing has been implemented
or benchmarked. The source mutation test changed one row only in disposable CI
fixture setup, observed the adapter reject the reread, then restored the row.
It did not change Phase 1C source code.

## Current limits

- The actual reference binding case has ten requested units, with eight free
  stock and a confirmed receipt; it is not the illustrative 20-unit proposal.
- A separate actual reference case has a supplier offer with no binding
  receipt and stays conditional. The 12+8 mixed conditional candidate remains
  an unverified planning idea until Phase 1C supplies a compatible fixed
  verifier.
- The sealed bundle is currently a typed JSON value prepared for later
  checkpoint state. No LangGraph nodes, tool adapters, access ledger, model
  calls, checkpoint write/read or restart test exist in M1.0.
- Tool source-pool coverage for all three approved Fulfillment operations is
  a subsequent Fulfillment milestone gate. An absent record in this bounded pool must later be reported
  as a discovery limitation, not as proof that no relevant supply exists.
- Full candidate rerun and human comparison remain later milestone work.

## M1.1 original assessment graph

M1.1 adds a sequential LangGraph graph in `dealdesk_phase2/orchestrator.py`.
Configuration is the first specialist result. The pinned Phase 1C
`assemble_deal_decision` runs **once** there; subsequent nodes map its
existing domain findings into six distinct, versioned results. This does not
claim six independently callable Phase 1C engines. Configuration prerequisites
can skip dependent Pricing, Fulfillment and Credit mappings; independent
Policy findings remain visible. A business blocker is not a technical failure.
Approval Routing identifies human review requirements; it grants no approval.

The graph state contains original submission identity, the M1.0 sealed bundle
and source fingerprint, result slots, trace and review status. Each node
revalidates pinned source identity. `requirements-m1.1.txt` lists approved
direct pins and `requirements-m1.1.lock` captures the Python 3.12 resolution.
LangGraph depends on Pydantic and LangSmith packages transitively; M1.1
neither defines Pydantic specialist schemas nor calls a hosted service.

CI uses a second disposable PostgreSQL database, `deal_desk_m1_checkpoint`,
for checkpoints. A test pauses after Configuration in a separate process,
opens a new saver and graph, and resumes at Pricing without rerunning
Configuration. The final code [M1.1 CI run
39255592023](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39255592023)
passed 16 tests, including all eight M1.0 tests. For its completed restart
thread, `pg_column_size` reported 8,614 bytes for the latest checkpoint
JSONB field and 65 bytes for its metadata. The shared tables' total
relation-plus-index sizes, after several test threads and multiple
checkpoints, were 344,064 bytes (`checkpoints`), 98,304 bytes
(`checkpoint_blobs`) and 188,416 bytes (`checkpoint_writes`).
These shared table sizes include PostgreSQL page/index overhead and are
**not** bytes per assessment. The sealed binding bundle was 38,717 UTF-8
bytes. This establishes recovery between nodes, not recovery midway through
a node; neither latency nor VM performance has been benchmarked.

Known fixed-interface limits remain: blocked cases do not expose the full
set of otherwise required approval roles, and Phase 1C does not provide
rule-level Policy prerequisite evaluation. M1.1 has no AI investigation,
alternative candidates, live models, UI or VM deployment.

## M1.2 bounded Fulfillment investigation (original-only)

`fulfillment_tools.py` exposes `inspect_line_supply`,
`inspect_fulfillment_paths` and `inspect_evidence_record` over M1.0's sealed
reader bundle. It performs no business SQL or writes. `tool_permissions.py`
has six versioned specialist allowlists; only Fulfillment's three operations
are enabled. Its trusted scope pins run/deal/customer/line/source/subject and
the original context. The response contains a separate execution result,
evidence/capability status, source records actually returned, and explicit
gaps. A 30-day forward horizon after the requested date does not discard
older stock snapshots or inbound provenance needed to assess freshness.

`tool_ledger.py` reserves each attempt in the existing LangGraph PostgreSQL
checkpoint *before* execution and appends a completion event. Twelve calls
per original investigation include denied attempts; each response exposes at
most 25 source records. Replay of a completed call ID returns its checkpointed
response without consuming another call. An interrupted reservation consumes
its call but supplies no citable evidence. Reusing a call ID with different
arguments fails closed. Only IDs actually returned by completed, authorized
calls within the pinned context can be cited or inspected in detail. The
investigation adapter currently attaches to a completed original graph; it
does not insert an AI node or candidate transition. It permits one sequential
caller; parallel callers require a separate atomic reservation design.

The actual pinned binding reference requests ten units and has eight fresh
stock plus a confirmed inbound receipt; the separate offer reference is
conditional. A mixed binding-plus-offer path is an explicit unsupported
Phase 1C capability, even where existing shipping options are visible. A
missing source is bounded absence from the sealed reader pool, never proof
that no supply exists elsewhere. M1.2 neither verifies candidate delivery
slices nor treats an indicative supplier offer as a commitment.

Run the existing locked Python 3.12 test command and two-checkout CI workflow
above. The M1.2 tests cover source identity, returned-ID citations, restart
budgets, authorization, horizon, response truncation and the real Phase 1C
binding/offer fixtures. [Final implementation CI run
39267937168](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39267937168)
passed all 29 offline and PostgreSQL tests, preserving the 16 M1.0/M1.1
tests. The real selected-stock/confirmed-inbound and separate conditional-offer
fixtures exercised all three tools; a synthetic sealed-pool contract test
exercised the unsupported mixed binding/offer path. PostgreSQL restart kept
the returned-source citation ledger and all 12 consumed call reservations.

**Limits:** There is no general Phase 1C mixed-supply path or conditional
candidate verifier. The tools do not discover sources outside the reader's
sealed selection, or confirm stock reservation, supplier commitment or human
approval. Ledger reservation is sequential: parallel tool invocations require
an atomic update design before concurrency is enabled. The run demonstrates
checkpoint recovery between calls; a call interrupted after reservation is
conservatively consumed, and no response from it becomes citable.

## M1.3 Fulfillment specialist interface and offline investigation

`fulfillment_agent.py` defines a restricted, typed original-line input,
untrusted tool requests, and three contribution forms: proposal, finding
without proposal and abstention. `investigation_graph.py` contains a small
conditional LangGraph: eligibility, offline model decision, one authorized
tool call at a time, and output validation. It starts only after the original
Configuration-first six-result graph completes. The original graph checkpoint
remains the authoritative state; a short-lived private investigation graph
controls the model/tool sequence. It uses M1.2's original PostgreSQL ledger
for call reservations and returned-record citations, then stores the trusted
AI envelope in a separate `ai_fulfillment_result` slot. It never overwrites
the fixed Fulfillment result or creates a candidate.

The narrow gate requires a valid Configuration finding, completed original
fixed Fulfillment result, a requested date, exactly one supported finished
physical line with a recoverable `late_alternative` or `conditional` shortage,
and fixed requested-date quantity below requested quantity. A separate Credit
or Policy blocker does not suppress this investigation; it remains in the
original findings and routing disposition. Multiple eligible lines and other
fulfillment modes are explicitly skipped pending broader contracts. Partial
delivery permission is passed to the model; a split suggestion when permission
is false fails the AI output guard, without treating the suggestion as a
verified candidate.

Runtime code assigns specialist/producer/run/subject/source identity. Model
content can request only the three named M1.2 tools and may cite only source
IDs actually returned to this line by completed authorized calls. A proposal
has status `unverified`, even if its dates and quantities are syntactically
valid. The model cannot mark a proposal slice confirmed; fixed Phase 1C
verification, which M1.3 does not invoke, owns business validity and source
commitments. AI abstention, a finding without a proposal, malformed output,
unsupported citation, tool failure and budget exhaustion are separate states.
An AI failure leaves the full fixed original assessment intact.

The offline `OfflineModelDouble` is a deterministic script with no provider
connection. If the process stops after a tool completes, rerunning the private
graph reuses its stable call ID and saved M1.2 tool result; it does not spend
another call or recalculate the six fixed domains. A reservation interrupted
mid-call stays consumed and yields no citation. This restart design is tested
against the disposable PostgreSQL checkpointer and pinned Phase 1C offer
fixture. A later live provider needs separately approved integration and
durable model-attempt records before non-deterministic replays are enabled.

The actual pinned stock-plus-confirmed-receipt reference has no requested-date
shortage and skips AI. The offer-only reference permits investigation but
forbids partial delivery: the offline double reports a cited finding without
proposing a split. The synthetic 20-unit 12+8 proposal test is explicitly
unverified; the pinned Phase 1C interface cannot verify its mixed path.

## Historical M1.4 comparison; active Groq-only runtime

**Local credential loading for opt-in, authorized development:** The root
`.gitignore` already excludes nested `.env` files. Keep the current checkout's
`phase-2-implementation/backend/.env` owner-only (`0600`) and containing just
`GROQ_API_KEY=<value>`. The existing opt-in test runner reads `GROQ_API_KEY`
from its process environment; no hosted runner auto-loads credentials in
routine CI. From the project root, launch an *existing* command through the
strict standard-library loader:

```sh
PYTHONPATH=phase-2-implementation/backend python -m dealdesk_phase2.local_env -- python -c 'import os; from dealdesk_phase2.groq_preflight import credential_shape; print(credential_shape(os.environ.get("GROQ_API_KEY")))'
```

This loader reads only the key, checks file ownership/mode and shape, and
passes it to its child without printing it. A successful local shape check is
not proof of Groq access: the [authorized Week 2 metadata gate](../evaluation/week2-closure-hosted-authentication-result.md)
returned HTTP 401 before any inference POST. Do not run any hosted campaign
without its separate assessment approval, fresh source preflight and budget.

For a **separately provided** second-account credential, retain the original
`GROQ_API_KEY` line unchanged and add `GROQ_SECONDARY_API_KEY` as a second
line in the same `0600`, Git-ignored file. To select it for **one** already
authorized command, use
`python -m dealdesk_phase2.local_env --credential secondary -- <existing-command>`
with this backend on `PYTHONPATH`. The child sees only the selected value as
`GROQ_API_KEY`; it never tries the other key automatically. An absent or
malformed secondary value fails before launching the command. No key-switching
or provider fallback is built into model requests.

M1.4 compared the two providers experimentally. The [method](benchmarks/m1.4-method.md),
[initial failures](benchmarks/m1.4-live-smoke-results.md),
[diagnostic](benchmarks/m1.4-connectivity-diagnostic.md) and
[gated smoke](benchmarks/m1.4-gated-smoke-results.md) are preserved as historical
thesis evidence. They do not establish a quality winner. Ali subsequently
discontinued Gemini as a development LLM. The experimental Gemini adapter,
provider-selection CLI, diagnostic runner, Gemini-only offline tests, and old
paired live workflows are removed from active code. The historical reports are
not rerun or rewritten.

`live_models.py` now supports Groq `openai/gpt-oss-120b` only. Its sole
credential is `GROQ_API_KEY`; routine CI uses patched responses without any
secret or live call. `model_attempts.py` checkpoints sanitized requests and
outcomes; completed responses replay without duplicate calls, and interrupted
reservations stop safely. The M1.8/M1.9 opt-in one-trial workflow is Groq-only
and requires separate case-specific authorization before a future live run.
No permanent provider or paid billing has been selected.

## M1.5–M1.6 status

The earlier M1.4 smoke and failed access records above are historical. Groq is now the provisional development provider, after M1.5 found semantic overclaims despite valid citations. M1.6 adds `claim_validation.py`, a strict final JSON schema, checkpointed raw rejection audit, and template-rendered validated reviewer summaries. [Contract](../architecture/m1.6-claim-contract.md) and [results](../evaluation/m1.6-results.md) describe the five claim types, source limits, 63-test PostgreSQL CI and one live Groq trial. The live trial contained an unsupported absence claim but did not generate a verified alternative. The pinned Phase 1C assessment, tool budget and original deal remain authoritative.
# M1.7 binding candidate and reviewer handoff

The optional M1.7 `binding_proposal` v3 contribution cites a complete returned
`inspect_fulfillment_paths` binding projection. The trusted Orchestrator
constructs the pinned Phase 1C `Candidate`; `Phase1CAdapter.verify_candidate`
performs the read-only fixed check. Original fixed results stay separate from
candidate-specific six responsibility mappings. A typed reviewer package
shows supply support as **unreserved**, unmet customer acceptance, withheld
routing and audit rejection counts. M1.6 supplier-offer ideas remain
nonactionable. Use `run_original_investigate_and_review` for the bounded
handoff; the original-only runner remains compatible. The live adapter has
an explicit `enable_binding_proposals=True` opt-in; routine CI uses offline
model doubles. See [methodology](../evaluation/m1.7-binding-candidate-methodology.md).

## Opt-in adaptive hybrid and B01 credential gate (27 October 2026)

The separate `hybrid_offline.py` LangGraph path records one counted restricted
prefetch, explicit inspection/submit intent, strict final, bounded revision
offline, pinned Phase 1C candidate checks and an isolated human review package.
It is **not** selected for ordinary deals. The hosted evaluation entrypoint
requires explicit authorization; B01 alone is the currently requested smoke
case. See the [offline status](../architecture/adaptive-hybrid-stage2-offline-status.md)
and [reviewer-only manifest](../evaluation/hybrid-first-groq-smoke-reviewer-only.md).

`groq_preflight.py` has a sanitized one-GET metadata gate; no model or provider
account access is implied by offline tests. The previously rejected Groq key
was reset from the private smoke launcher. Ali must supply a different valid
key through the owner-only hidden prompt described in the manifest. Never
include the key, private launcher, PostgreSQL files or audit artifacts in Git.
The fresh isolated PostgreSQL fixture/checkpoint regression ran 192 tests:
185 passed, seven optional saved-checkpoint diagnostics skipped. CI is separate
from this local check and the hosted smoke. No hybrid inference has been sent.
# D3 offline assessment API

The authenticated, loopback-only FastAPI demo uses the existing PostgreSQL
checkpointer and offline LangGraph specialist continuations. For **exact pinned
dependencies, disposable synthetic fixture setup, environment variables,
startup command, authenticated request examples, event/review response contract
and security limits**, see
[`../architecture/offline-assessment-api.md`](../architecture/offline-assessment-api.md).
No hosted-model call, approval, reservation or customer acceptance is available
through this API. The UI is a separate future increment.
