# M1.0 — Pinned reader and replay boundary

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

## M1.4 opt-in Groq/Gemini comparison

`live_models.py` implements two narrowly scoped standard-library HTTP adapters
behind the M1.3 `InvestigationModel` protocol. Groq uses
`openai/gpt-oss-120b`; Gemini uses `gemini-3.8-flash`. Each requests at most
one local tool at a time and uses a separate structured final request. Runtime
validation, authorized M1.2 execution and original/fixed results remain
unchanged. `model_attempts.py` records a sanitized reservation and completion
in the existing PostgreSQL checkpoint. Completed requests replay without a
second provider call; an interrupted reservation stops safely. No API key,
raw provider response or raw request body is checkpointed.

The [M1.4 benchmark protocol](benchmarks/m1.4-method.md) describes the
two actual pinned cases, repeated-trial limitation, quotas, metrics, opt-in
runner and critical failures. Routine CI uses patched HTTP responses only;
it never reads credentials or makes live API calls. [Live smoke results](benchmarks/m1.4-live-smoke-results.md) now record two
failed eligible requests per provider: Groq HTTP 403 and Gemini HTTP 503.
The original fixed results remain intact. No successful inference, paired
benchmark or provider-quality conclusion has been measured.
