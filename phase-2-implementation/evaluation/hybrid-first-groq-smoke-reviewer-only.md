# First hosted hybrid smoke — reviewer-only manifest (not a model input)

**Status (27 October): the replacement credential passed authenticated metadata
preflight; B01 alone was attempted and stopped after two hosted inference
requests with no verified candidate.** Earlier rejected-key 401 was a separate
preflight with zero inference requests. Do not load
this file, any linked answer sheet, deterministic discovery output or baseline
schedule into the model input, system prompt, tool results or Groq request.
The model receives only the restricted pinned input, counted prefetch and
authorized tool observations from `hybrid_pack.py` / `hybrid_offline.py`.
Use a fresh disposable fixture/checkpoint database; never alter Phase 1C or
the unchanged iterative comparator. Do not relabel earlier iterative Groq
trials as hybrid evidence. Model text is not authority for business outcomes.

| Order | Case and provenance | Source-first reviewer expectation (not model-visible) | Hosted gate |
| --- | --- | --- | --- |
| 1 | B01, synthetic source case in `backend/tests/m18_case_setup.py`; developer/supervisor accepted 2026-10-21 in `m1.8-developer-review-decisions.md`; sealed bundle `720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`, source digest `64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4` | Original `needs_revision`; 8 on Sep 4 from stock + 2 on Sep 8 from confirmed inbound is fixed-supported but not reserved or customer-accepted. Sep 3 option can support the Sep 4 slice; do not insist dates match options exactly. No invented citation, confirmed supplier offer, approval or delivery promise. | Eligible; **first and only requested hosted smoke**. |
| 2 | R03, real pinned `offer_without_supplier_commitment`, run suffix `030001`; M1.5 source-first sheet, **separate human acceptance still open**; bundle `057951350658013a82a35463e28ccc734079c988931b7bebc93ab00d0ce64699`, source digest `dda896a00658a83df25d4807ecec439657be3ae11c1f8bb6e86d613fbb1738db` (from M1.6 source record) | Fixed `conditional` / `needs_evidence`. Supplier estimate is uncommitted, no binding receipt; customer forbids partial. Accept scoped cited conditional finding or reasoned abstention; no confirmed delivery or verified split. This is a source-first expectation, not M1.8 developer acceptance or independent ground truth. | Eligible; **not authorized by approval of B01 alone**. Requires explicit R03 expectation acceptance and a second hosted authorization. |
| 3 | N02, synthetic developer/supervisor accepted; bundle `44cdcc1416fae86cd8c2b853288567170edc2ca78afe7eb8f15cae3f2c4a5a3c`, source `630aa7b2a2fc0d8a8eea7afdcb4ffe31c7bd142cbc4e7392e39f51813a2c49fd` | Cancelled inbound cannot support a binding later slice; no fixed verified candidate. | Fixed gate skip: **zero** hybrid/model requests. |
| 4 | N03, synthetic developer/supervisor accepted; bundle `a176ad55e465ea91c66ed5d10d814ee694368f96ee4268ea0021aaff465a8148`, source `6f9918c9e5192a22eb254980dd603a9d842969fdde04039eea8a8bbbbc575a06` | Stale stock: original `unknown` / `needs_evidence`; no assertion of zero physical inventory. | Fixed gate skip: **zero** hybrid/model requests. |
| 5 | N04, synthetic developer/supervisor accepted; bundle `f73cc52513fb8c3959d6811924b336228a97500ba68a410f6b65679b4e2b43ec`, source `975bbcef1650d3918001a0d0b0fe1d6b8b001ba40563dad84a487c7c28d547d8` | No selected binding source in bounded pool; no universal supply-absence claim. | Fixed gate skip: **zero** hybrid/model requests. |

The N cases are adverse **fixed-gate controls**, not tests of hosted reasoning.
Use a read-only original-graph eligibility check first; do **not** invoke the
hybrid runner on skipped cases (its entrypoint assumes an eligible case).
Record exact fresh source identity before scoring. Divergent bundle/digest or
original status stops the exercise; never copy these labels into Groq messages.
Keep pinned discovery/verify outputs and the iterative baseline in a separate
reviewer-only artifact, not the model-visible `model_input` or observations.

## Proposed B01 smoke limits and order

Single VM process, exactly one worker, one assessment at a time, persistent
`/tmp/opencode/dealdesk-hybrid-smoke-reservations` (`ubuntu`, mode `0700`, local
ext4 `/dev/sda1`). Its receipts and PostgreSQL checkpoints must survive
restart; do not remove the directory or reuse an assessment ID after an
uncertain attempt. Cross-process `flock`, fsync and 0700/0600 are covered by
offline tests on this local filesystem, **not** by a multi-VM/shared-storage
deployment test. No multi-worker configuration has been established. Confirm
the intended process/container can access the *same path/inode and checkpoint
database* immediately before any approved request; otherwise stop. No current
Deal Desk service worker or deployment file was identified; OpenCode workers
are not Deal Desk workers.

Hosted-only frozen policy `groq-smoke-budget-v1`: maximum **3 sequential
requests per eligible case**, each serialized body **<=8,192 bytes**; at most
two native-function decisions (each `max_completion_tokens=512`) and one
strict-schema final (`max_completion_tokens=1,024`), or **2,048 configured
output tokens total**. One optional inspection may follow decision 1; a
second inspection ends this case without a third decision. No D4 revision,
automatic retry, concurrent send, fallback, or cross-case aggregate run is
permitted. The budget and directory identity are checkpoint-frozen, and the
send boundary checks each body **before** durable reservation. B01 offline
request sizes with the prior larger ceilings were 4,901 / 6,671 / 5,521
bytes; changed source/observations may exceed 8 KiB and must then stop, not
raise the cap. Groq account quota, price and actual token use are unknown
until a separately authorized hosted call; obtain quota/permission and any
cost approval separately, without changing billing here.

**Before each send:** verify source/pack and checkpoint identity, receipt
directory, budget, serialized request, selected tool scope and completed
prefetch ledger. The exclusive attempt file records start/request digests and
fsyncs the reserved marker and directory before calling Groq. After a
response the raw bounded JSON (including usage if provided) is checkpointed
before parsing; receipt contains no key or raw response. A receipt with no
saved raw means uncertain send and no retransmission; a saved raw can replay
only against its matching receipt/request. Missing or over-ceiling Groq usage
stops the case after capturing raw. Inspect checkpointed raw decision/final,
tool-call count/arguments, parse/finish reason, returned_refs and audit-only
rejections; validate citations against returned ledger, not just source pool;
for binding proposals use pinned Phase 1C candidate construction and verifier
before isolated six-specialist reviewer handoff. Unreviewed prose remains
unreviewed; human customer acceptance and approval remain pending.

**Global stop:** stop immediately on HTTP/rate/quota/transport error, timeout,
incomplete/invalid response, token or byte cap, uncertain receipt, source or
directory mismatch, unauthorized tool/citation, conditional source promoted
to binding, unsupported date/quantity, changed original/fixed result,
automated approval, absent raw audit/reviewer package, or any critical safety
claim. Do not move to R03 or control cases after a safety failure. A safe
abstention or scoped finding is a valid *contract* outcome, not proof of
business quality. Stop after B01 for human raw-output review; no implicit
approval for R03 or paired comparison.

## Wire readiness boundary

The adapter sends `openai/gpt-oss-120b` to Groq chat completions. Native local
functions with `tool_choice=required` and `parallel_tool_calls=false` select
one scoped inspection or explicit submission intent. A separate request has
no tools and a strict JSON schema for the saved intent. One tool call only,
matching final kind, returned citation checks, and invalid/multiple/truncated
responses fail closed. Groq documentation describes these features for this
model (structured outputs and local tool calling); tests with scripted wire
JSON are **not** evidence of this account's live behavior. The very first
authorized B01 request must stop on API parameter/schema rejection or model
response mismatch; no silent schema downgrade.

**Credential gate:** The process requires `GROQ_API_KEY`, not a coding-model
subscription or a Gemini key. The private VM launcher loads it from a 0600
owner-controlled local file into the child process only. The rejected file
was reset during the 26–27 October handoff; do not retry that key. For a
**different valid key** already owned by Ali, the one owner action is to run
`python3 /tmp/opencode/dealdesk-hybrid-b01-smoke-prep/supply_existing_groq_key.py`
in a trusted interactive VM terminal and enter it at the hidden prompt.
Never send the key in chat, a command-line argument or a repository file.
The runner first uses `groq_preflight.check_model_access`: one sanitized,
bounded, no-redirect metadata GET. 401, 403, 404, 429, model absence and
transport/JSON failures stop with no inference; there is no retry or fallback.
After successful metadata access, reconfirm the disposable B01 source hashes,
empty checkpoint/receipt directory, single-worker ownership, account free
tier/quota and the above three-request ceiling before the one approved B01
assessment. Offline original eligibility and fixture hash checks were
reconfirmed after credential reset; **no live inference has been performed**.
