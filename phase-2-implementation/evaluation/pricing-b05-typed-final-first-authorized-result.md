# First authorized B05 Pricing typed-final trial — stopped at Configuration

**29 October 2026; one synthetic assessment only.** Ali approved the exact
manifest SHA-256
`530cfc1d87cde830b3376284e9f0a05dd6a0e167b9e5c7bc27def85c2a42b0e3`,
the single reviewed `HOSTED_ACTIVATION=False` → `True` diff, Groq organization
`org_01m5d82zneee6b2vzsz8d2014b`, and at most **four POSTs / 2,560
configured completion tokens**, without retry/replay/fallback. The earlier
private-CI evidence gap was explicitly accepted for this one case; CI did
**not** pass. No other hosted assessment or metadata request was made.

The frozen B05 original `TYPED-B05-SCRAM-8ba93fddd647` used pinned Phase 1C
`90c0bc8e285ee69262c7db826b786096a77ad004`, business database
`b05_business_2230473070` (OID 16385) and its exclusive checkpoint database
`b05_checkpoint_c43d6b2467` (OID 16386). Pre-send source reread, manifest,
permission/prompt/schema/budget hashes and exclusive checkpoint history
matched the approved identities. The restricted PostgreSQL runner, existing
Graph and exact hosted entry were used. A private, owner-only `0600`
`typed-final-approved-manifest.json` was created as authorized and is **not**
in Git. The owner-only directory and spent receipts are retained as audit
evidence; the single-invocation marker prevents rerunning this assessment.

## What actually happened

1. Configuration, Pricing's required preceding investigation, sent its first
   native-tool POST (`max_completion_tokens=512`). The returned and
   checkpointed response requested one allowed
   `inspect_configuration_line` read, returning the synthetic evidence ref
   `product:M18-P-B05`. This is **Configuration** evidence, not a Pricing
   price/margin observation. First returned usage: 642 prompt tokens and
   84 completion tokens; its validated-claim list remained empty because
   the investigation had not reached a final finding.
2. Configuration's second native-tool POST (`max_completion_tokens=512`) has
   a durable **reserved → returned** receipt: the HTTPS send returned a
   response. The model/tool action was **not** accepted by the local
   Configuration parser. The checkpoint contains its reservation but **no
   returned-and-validated checkpoint attempt**. The bounded AI result is
   `execution=error`, `reason=invalid_model_or_tool_output`, with zero
   validated claims. Its returned usage/content are not preserved; the
   specific schema/tool-call discrepancy cannot be established after the
   fact without inventing facts or logging a raw provider body. This is
   **not** evidence of a transport failure or an HTTP 400.
3. The runtime stopped before Pricing: **zero Pricing inspection POSTs,
   zero strict-schema final POSTs, zero typed-final attempts/findings**.
   Fixed original status remains `needs_revision`, human review only.

**Measured boundary:** **two Configuration POSTs returned**, each configured
for at most 512 completion tokens: **1,024 configured completion tokens**
associated with the two attempted sends, below the approved 4/2,560 cap.
Only the first response has checkpointed usage (642/84); do not claim actual
token consumption, cost or response content for the second. Receipt-returned
does not make a parse-invalid reservation replayable. There was **no retry**.

## Interpretation, stop/rollback and next work

**Did real Groq Pricing work? No.** Groq produced a Configuration tool
inspection, but its second Configuration result failed local validation and
Pricing was never invoked. **Did typed-final fix the earlier
`tool_use_failed`? Not demonstrated:** this run reached neither Pricing
inspection nor its no-tools strict-schema final. It did not observe the
earlier HTTP 400 on the second Configuration POST; it instead observed a
different, locally rejected response. Do not generalize one case to model
quality or claim an AI Pricing recommendation. Deterministic fixed results
and the human-approval boundary were unchanged.

As soon as the error was observed, the approved flag was restored to
`HOSTED_ACTIVATION = False`; the trial process exited. The private approval,
both returned receipts and the terminal checkpoint reservation were retained
for audit. A second invocation, continuation, legacy path or fallback on
this assessment is **prohibited**, despite the returned receipt.

Before considering another **separately authorized fresh case**, inspect
the offline Configuration parser/request contract and design a *bounded,
redacted* failure-category diagnostic for a future authorized response if
needed; do not reconstruct unseen provider content or loosen evidence
validation. Re-evaluate Configuration eligibility and the exact second-turn
wire using offline fixtures/mocks. Any new hosted experiment, architecture
change or additional POST budget needs its own owner review and authorization.

## Evidence and verification

- Private sanitized result (mode `0600`):
  `/tmp/opencode/dealdesk-b05-scram-9c9794347b09/trial-sanitized-result.json`,
  SHA-256 `a34e31b5774695b9bab38deefa4fe3879e07515c253cd8f9d46602c91dc28259`.
  One-shot runner SHA-256:
  `3a4e8831b7992effde4884b55cae80c6329aa9328affec6d269e2318d91bbb72`.
  Neither artifact contains a credential or raw provider response.
- After rollback, read-only checkpoint inspection confirmed Configuration
  attempts `(0,reserved)`, `(0,returned,inspect)`, `(1,reserved)`;
  `typed_final_attempts=[]` and `typed_final_results={}`. Private receipts
  for both Configuration ordinals contain `reserved` and `returned`; no
  Pricing/typed-final send receipt exists. The only completed tool evidence
  ref is `product:M18-P-B05`.
- Focused **eight** offline proposal/typed-contract/dormant-gate tests passed
  after rollback (`/tmp/opencode/dealdesk-b05-scram-9c9794347b09/post-trial-offline-tests.log`).
  No billable CI or full fresh PostgreSQL regression was dispatched for this
  trial. No accuracy or hosted typed-final success claim is warranted.

**Offline follow-up (29 October):** Native-tool parser failures now emit only
fixed structural categories for *future* attempts; this cannot reconstruct
B05's unretained second response. Fresh disposable PostgreSQL fixtures passed
41 relevant Configuration/Pricing/Credit/Policy/Routing and typed-final mocked
tests, including a complete Configuration → Pricing path and a terminal
malformed-second-turn case. Groq inference remained disabled and was not sent.
