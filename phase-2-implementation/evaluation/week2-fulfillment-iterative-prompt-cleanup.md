# Week 2 offline Fulfillment iterative prompt hierarchy — 27 October 2026

The opt-in [iterative Groq wire](../backend/dealdesk_phase2/live_models.py)
previously put the detailed Fulfillment instructions and selected evidence
into the same **user** message, with only a short system sentence. It now
assembles the former evidence-only citation, conditional-offer, binding-path,
whole-unit quantity, uncertainty/abstention and human-only authority guidance
in a trusted system instruction, with separate stage rules for decision,
schema-constrained final and correction. The decision system instruction
also names only the trusted input's allowlisted local read tools; an unknown
name fails before model access. The user message holds selected task input,
returned observations, a prior **rejected** model output and bounded trusted
validation feedback as data, not permission to override the system role.
No tool permission, rule, source pin, candidate verifier, schema or model
budget was changed. The original `_prompt` full-prompt helper stays available
for historical offline diagnostics, but active Groq sends use `_task_data`
under `_system_instruction`.

`m16-fulfillment-claims-v2-system` plus the unchanged binding-mode suffix
identifies the **new** prompt; old hosted M1.6–M1.9 measurements keep their
original v1 prompt identity. The PostgreSQL attempt ledger now stores that
prompt version separately from its canonical request SHA-256. A restarted
attempt requires both to match, or fails closed; no completed request is
silently upgraded to this new prompt. Versioned output/candidate contracts
and hybrid wire versions are unchanged. No new hosted run is authorized.

The existing [hybrid Groq adapter](../backend/dealdesk_phase2/hybrid_provider.py)
also records its unchanged trusted text under the independent audit label
`hybrid-fulfillment-system-v1`, rather than reusing
`hybrid-groq-wire-v1` as a prompt version. Its checkpoint verifies the
label on restart; legacy terminal checkpoints without this label remain
readable but cannot resume a new send. No system/user text or provider
request was changed.

**B05 example:** A proposed 11+18 split of 18 units is a rejected model
contribution, not a changed deal. Correction feedback reports the trusted
quantity-sum constraint; an offline mocked correction can return 11+7 with
the original stock/inbound source refs. The pinned verifier (in the existing
offline B05 integration tests) decides whether that candidate is supported.
The new protocol tests keep the full binding guidance in system, the rejected
text/feedback in user data, the correction response schema unchanged, and
the selected original fixed findings unchanged. A PostgreSQL restart of the
mocked B05 correction reuses its completed ledger response with **zero new
provider sends**. This demonstrates protocol containment and replay only,
not that a model will resist every adversarial instruction or produce B05
correctly in a new live trial.

The fresh seven-database full PostgreSQL discovery passed **249 tests,
seven skips**, including the preserved untracked Gemma experiment tests.
GitHub Actions for this increment is still **unverified**. No Gemma files or
unrelated uncommitted document edits were changed or deleted.

See the [closure matrix](week2-closure-audit.md) and the [proposed fresh
Pricing validation](week2-closure-hosted-proposal.md); neither provides
authorization for Groq or other hosted inference.
