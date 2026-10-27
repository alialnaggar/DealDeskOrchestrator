# Replacement Groq campaign — authorization proposal (no hosted POST yet)

**Prepared 27 October 2026.** Historical digest
`8dbaac541012a21c76b71e5a77af53c43dac2aa357417098a374bc7ae79ba8bd`
and its reserved-only B01 attempt are permanently out of scope; no replay,
resume or alteration. The new proposed authorization digest is
**`0c3b9af2e7ca5d2f673397df0604acb1b1c5e5757845755d29f6935298e52082`**.
This digest identifies the new manifest, model, case order, budgets and
case-local failure policy; it is not a credential or approval by itself.

## Exact scope for a separate approval

**Ordered cases:** `B01`, `B02`, `B03`, `B04`, `B05`, `N01`, `R03`, `N02`, `N03`,
`N04`. Seven eligible cases; the last three are fixed-only controls and make
zero model calls. Model: Groq `openai/gpt-oss-120b` on Ali's existing Free-tier
account with billing disabled; no account or plan change. **At most 21
sequential inference requests**, **14,336 configured completion tokens total**
and **8,192 UTF-8 serialized request bytes per send**. Per eligible case:
at most two 512-completion-token decision sends and one 1,024-token final;
at most 2,048 configured completion tokens. No retry, D4 revision, fallback,
parallel worker, added case or ordinary-assessment activation. Completion
limits include reasoning output and may constrain visible actions; actual
quality is unmeasured. This proposal retains the smaller original ceilings
rather than implying their adequacy.

Fresh exact assessment IDs and each Phase 1C `run_id`, frozen bundle hash and
source-input digest are pinned in
[`hybrid-groq-replacement-identities.json`](hybrid-groq-replacement-identities.json),
canonical SHA-256
`a1a431778efd694055e4d7f04b5f5d7bfb150f76dcd15579b2720179ad62653d`.
All ten source identities match the source hashes inspected in the historical
offline preflight; each assessment ID is newly named `HYBRID-REPLACEMENT-*`
and is different from the historical B01 ID. The actual replacement must
repeat a read-only ten-case source and six-fixed-check preflight before any
inference. R03's source-first expected outcome remains provisional; reviewer
expectations are **not** in this manifest, prompts or tool evidence.

## Safety policy and accounting

The historical v1 campaign keeps its global-stop policy. Only this newly
identified replacement v1 may **skip at most one failed eligible case** when
its exact frozen assessment/checkpoint identity, six original fixed mappings,
no candidate, pending decision/final send, and a matching fsynced `failed`
receipt prove an allowlisted local transport timeout, lost connection,
protocol interruption, malformed JSON or oversized response. A reserved-only
receipt, unrecognized error or mismatched checkpoint **stops globally**.
The failed request is permanently non-replayable even if the provider may have
processed it. The campaign never treats it as a model success, abstention or
verified candidate. It reserves the **entire 3-request/2,048-completion-token
case allocation** against the 21/14,336 maxima regardless of how many sends
actually occurred; completed prior sends in the failed case contribute their
known usage. The legacy `requests` result field is budget slots charged, **not
POSTs actually observed**; replacement results and read-only reports also
state `reserved_request_slots` and `minimum_attempted_requests`. A newly
reserved but globally stopped case remains an outstanding reservation, with
unknown send count, and is charged its full case allowance in reporting.
An attested failed case is accounted separately from an outstanding case.
Actual usage for the failed send is **unknown, not zero**.

HTTP rejection (including 400/401/403/429/5xx), missing usage on a completed
send, a second case-local failure, changed identity/source/pin/credential,
invalid receipt or audit, hard budget or permission failure, unsafe candidate,
failed deterministic verification, unsupported reviewer handoff or any
unexpected failure **stops the campaign**. Preserve the existing stop after
two contained model validation errors. The cumulative **60,000 reported
total-token threshold** is checked after cases, including any known prior
usage on a failed case; it is **not** a hard input-token ceiling and cannot
reconstruct unknown usage on a failed POST. This unknown-usage caveat is
part of the proposed authorization, not a claim of zero cost. Any local
failure may make later quality denominators smaller even if all other cases
finish.

**Engineering decision:** The historical global-stop policy is safer when
failure provenance is missing (as in the first B01 campaign), so it remains
unchanged for v1. For this separately authorized run, stopping every unrelated
case on one *attested* local transport interruption loses the whole sample
without making that failed request any safer. Continuing after any provider
error was rejected: HTTP rejection can signal credentials, quota or schema;
missing usage or a changed source defeats the safety gate. The narrow one-case
exception above preserves no-replay and the hard configured ceilings while
disclosing the unavoidable unknown prompt usage; the second failure stops as
a potential systemic issue. This is a campaign policy decision, not an AI or
fixed-business-rule change.

## Execution prerequisites and outcome

Before any POST: explicit approval of the **new digest and this policy**;
confirmation that the Groq plan remains Free with billing disabled; a
sanitized authenticated metadata GET for model access; passing fresh local
PostgreSQL regression, CI status disclosed accurately, and three new separate
disposable PostgreSQL databases (synthetic, reference-only R03, checkpoint).
Require a new empty `0700` owner-only reservation directory on a durable
single-host filesystem and one worker, with no historical journal/receipt or
checkpoint reuse. The dormant entrypoint requires `replacement=True`, the
new manifest, and `authorized=True` with this exact digest; the old digest
cannot authorize it. Run all cases sequentially without asking again between
them unless a documented global stop fires. Preserve raw successful model
outputs and usage in checkpoint, tool ledger and reviewer handoff, and save
sanitized failures in per-send receipt plus case journal. Read-only reporting
separates completed cases, one incomplete local case, reserved budgets and
unobserved tokens; independently review semantic quality later. No AI output
approves deals or promises delivery. The unchanged iterative comparator and
Phase 1C fixed-rule authority remain untouched.

**Offline acceptance:** A new isolated PostgreSQL fixture and checkpoint
rehearsal mocked a B01 transport timeout, attested its non-replayable failed
receipt, continued to B02–N04 without resending B01, checked four fixed
binding candidates with all six rerun mappings, two abstentions and three
fixed-only controls, and reconstructed a read-only incomplete-case report.
This is *not* a hosted success count. The final fresh isolated PostgreSQL 16
full backend suite ran **217 tests: 210 passed, seven unrelated historical
Gemma diagnostics skipped**; the pinned mocked replacement, original
campaign, no-replay and reporting tests were not skipped. An independent
read-only safety review identified the reserved-versus-observed accounting
gap, now covered by separate fields and an outstanding-reservation test.
GitHub CI remains **unverified**, not passed. No inference call was used here.
