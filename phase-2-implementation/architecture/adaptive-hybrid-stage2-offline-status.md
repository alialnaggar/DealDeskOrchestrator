# Adaptive-hybrid Stage 2: offline handoff

Status: **opt-in, offline regression passed; no hosted hybrid evaluation authorized**.
The iterative comparator, Phase 1C pin and historical measurements are unchanged.

- `hybrid_offline.py` coordinates decisions, authorized inspections, saved submission
  intent, separately reserved final, bounded D4 revision and original/candidate
  review through conditional LangGraph nodes. The original assessment's existing
  checkpointer remains the durable state owner. Six original and six candidate
  specialist responsibilities are unchanged; human approval remains required.
- `hybrid_pack.py` freezes the investigation context, counts one authorized
  `inspect_line_supply` prefetch, and can reconstruct a pack from a completed
  durable tool event without repeating the read. An interrupted reserved tool
  without a completed result fails closed.
- `hybrid_send_reservation.py` requires **one private, persistent, shared
  reservation directory for all workers of a given assessment**. An OS file
  lock excludes competing processes while checkpoints/tools are written. Each
  outgoing attempt has an exclusive, fsynced identity/request receipt. A
  pending checkpoint without a receipt is provably unsent; a checkpointed raw
  response can be replayed after receipt validation; a receipt without saved
  raw is uncertain and is never sent again. Changing the directory on restart
  fails identity validation. The lock/receipt assumption requires a filesystem
  shared by any future concurrent workers with correct lock and fsync semantics;
  distributed workers without that guarantee are **not** approved.
- `hybrid_provider.py` keeps the provider wire protocol separate from domain
  validation. The Groq wire double tests native single-function intent and
  no-tool structured final with saved raw response. The real Groq transport
  class is dormant. `run_hybrid_offline` rejects it; the separate evaluation
  entrypoint refuses it unless explicitly authorized. No hosted request was
  made in Stage 2.
- D4 makes at most one separately reserved new intent/final and never repairs
  model content. If unchanged dated source bindings cannot be conservatively
  diagnosed before Phase 1C verification, it **withholds** a revision rather
  than approximating Phase 1C's supply rules. This can reduce revision coverage
  for valid earlier-option/later-slice cases (B01); it is not a safety success
  claim or evidence of model quality.

No ordinary assessment selects this hybrid entrypoint. Before hosted use,
obtain authorization for the proposed Groq test budget, case set and stop
rules; verify actual provider tool-choice/JSON-schema behavior and filesystem
assumptions; keep the zero-tolerance reviewer and uncertainty gates. Offline
model-double results do not establish hosted business quality.

**26 October follow-up:** receipt verification now rejects non-object events,
unexpected fields and malformed returned markers before treating a saved raw
response as replayable. Replay requires a completed returned marker, not merely
a reserved attempt; the reservation directory and receipt must belong to the
running OS user. A fresh isolated PostgreSQL regression ran 181 tests:
174 passed and seven optional saved-Gemma-checkpoint diagnostics skipped. This
is offline evidence only. The separately
gated B01 metadata GET still returns HTTP 401 with the supplied private key;
there was no hybrid inference request. Do not retry inference or substitute a
coding-agent credential. The owner must provision a valid Groq free-tier key
through the existing private local credential handoff and confirm access with
the sanitized metadata diagnostic before the B01-only smoke.

**27 October offline increment:** `groq_preflight.py` makes one read-only,
no-redirect, bounded metadata GET only when a locally well-formed credential
is available; it distinguishes 401 authentication, 403 authorization, 404
endpoint, 429 rate-limit, absent model, invalid/oversize metadata and
transport categories without logging keys, headers or response bodies. Local
structural inspection of the previous private key found one line, no whitespace
alteration or duplication and a single Bearer header at the call site; this
does not establish provider validity or rule out an otherwise plausible
truncation. The rejected smoke-only credential file was unlinked, with the
owner-controlled hidden-prompt re-entry script preserved. **Do not retry the
rejected key.** Hybrid wire requests are now built exactly once: the bytes
whose length and digest are reserved are the body passed to the transport.
Hybrid POSTs reject redirects; the iterative comparator retains its previous
transport behavior. No provider request was made during this increment.
The final fresh isolated PostgreSQL regression ran **192 tests: 185 passed,
seven optional saved-Gemma-checkpoint diagnostics skipped**, with no failures.
Offline Groq tests cover sanitized 401/403/404/429, metadata/response errors,
redirect refusal, uncertain sends, duplicate owners, one-build request digests
and exhausted/missing token usage; they are not hosted quality evidence.
