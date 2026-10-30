# Blinded second-model review — source-first, author-accountable

Status: preparation only. **No AI review has run and no answer has been accepted.** Original 36, Configuration 039 and Credit controls 040–041 have distinct source pins in `source_manifest.json` and blank forms in `blank_responses.json`. Cases 037–038 remain preflight diagnostics. The original v2 inputs/drafts and v3 scopes remain untouched.

## Blind first pass

On the verification VM, supply the *fresh exported* packet/provider directories recorded in `../reviews/phase1c_postgres_verification_2026-10-30.md` and run:

```sh
python workflow.py prepare --original-packets /tmp/opencode/phase1c_original_packets --configuration-packets /tmp/opencode/phase1c_configuration_packets --credit-packets /tmp/opencode/phase1c_credit_packets --output /private/blind_review
```

The script refuses any packet/provider or v3 scope hash mismatch and creates 39 per-case folders containing only `sources.json` and `blank_response.json`. Give the second model **only that case folder and this contract**. Never give it `reviews/v3_six_responsibility_technical_matrix.json`, model drafts, author amendments, review aids, prior gate proposals or historical/development outcomes before its initial response is frozen. Keep the model's raw response bytes and model/version, prompt, settings, date, operator and invocation log. No paid API call is authorized by this preparation.

**Second-model instruction:** Review only the supplied source packet, separate provider manifest, trusted Credit scope (if present), and embedded business contract. First establish source identities and cutoff. Write one JSON response using `blank_response.json` keys with `status=second_model_draft_not_accepted`. For Configuration, Pricing, Availability, Credit, Policy and Approval, give a finding from `no_issue_identified`, `issue_identified`, `evidence_needed`, `human_review_required`, `not_applicable`, `abstain`; a reason; resolvable `{document,pointer}` citations to `packet`, `provider` or `credit_scope`; calculations as `{metric,value_eur,formula,evidence_refs}`; uncertainties; and an abstention reason when applicable. At least quote arithmetic (`quote_total_eur`) and, for the original complete-zero cases, `credit_exposure_eur` must be calculated or explicitly abstained from. Give an overall gate from `blocked`, `needs_revision`, `needs_evidence`, `needs_commitment`, `approval_required`, `abstain`, with precedence reasoning, human actions and unresolved questions. A possible review route is never an approval, reservation or delivery promise. Do not infer a complete-zero balance from empty rows without trusted scope. If source facts are missing, abstain or request evidence. Disclose model identity, timestamp and any assistance or outside information. Do not claim to be an independent human expert.

The source-first AI output is **independent of the prior answer drafts only in its blinded initial context**. It is still AI-assisted technical review, not independent human expert validation; the author owns final decisions and must disclose authorship and model assistance.

## Offline contract example (not a blind-package attachment)

[`source_neutral_example.json`](source_neutral_example.json) is a tiny
**EXAMPLE-ONLY**, non-evaluation source, blank-form identity and illustrative
six-role JSON response. Its EUR 20 quote and EUR 23 bounded fictional Credit
exposure are deliberately unrelated to any evaluation case. Unit tests run
both the structural validator and the narrow source arithmetic against it.
It teaches `{ "document": "packet", "pointer": "/source_rows/lines/0" }`
object citations and decimal-string EUR calculations, not a case conclusion.
Additional *synthetic-only* unit examples distinguish an overdue EUR 100
invoice with EUR 20 paid/EUR 80 outstanding (both AR and payment references
required) from an incomplete invoice population, which cannot assert zero
exposure even with empty selected rows. Neither uses a real evaluation ID,
source hash or answer.
**Never attach the example or this README to a blinded case request.** The
model receives only its exact case source and blank form; no existing answer,
matrix or technical recommendation appears in the prompt or package.

## Bounded zero-priced runner and current execution status

No model calls, pricing checks or quota polls are scheduled. **Do not invoke
the runner until existing free-tier quota is demonstrably available again**
and the work is resumed. `run_free_batch.py` requires an explicitly
allowlisted free model **and**
verifies its live OpenCode catalogue input/output/cache pricing is zero before
sending. It attaches only the per-case source and blank form from the isolated
directory, checkpoints *before* each send, stores the exact prompt, timestamps,
raw JSONL and stderr outside the source packages, and never automatically
retries a case with any attempt record. Default: **one fresh case** and a
180-second per-call timeout. A batch of two or three first requires a valid,
checkpointed fresh-case pilot from the **same model**, with all six labels,
resolvable citations, and bounded required arithmetic; stop on any invalid
output, provider error, tool use or uncertain transport. Structurally/arithmetic-invalid responses remain
pending in the attempt log, not in the valid-response folder. Ali must
explicitly authorize any new attempt for 002–004 after inspecting the frozen
raw evidence; the current runner cannot make such an attempt. Do not relabel
a retry as a first blind pass.

After free quota and runtime availability are confirmed, from this folder:

```sh
python run_free_batch.py --model opencode/flint-40b-free \
  --original-packets /tmp/opencode/phase1c_original_packets \
  --configuration-packets /tmp/opencode/phase1c_configuration_packets \
  --credit-packets /tmp/opencode/phase1c_credit_packets \
  --packages /tmp/opencode/phase1c_blind_verified_20261030 \
  --attempts /private/phase1c-attempts --responses /private/phase1c-valid-responses \
  --max-cases 1
```

The example model is **unproven** for this contract: run one new-case pilot,
inspect valid citations and calculations, then increase to `--max-cases 3`
only if its outputs pass. **Paid API usage is not authorized**; do not switch
providers, bypass limits or retry failed free models to finish this campaign.
The runner unconditionally excludes the four earlier pilot IDs (001–004),
even if a new attempts folder is used. **No override is provided.** Cases
002–004 require explicit authorization from Ali before any further attempt;
if granted, the recorded attempt policy must be versioned rather than bypassed
with a CLI switch. The first default fresh-case pilot is 005.

The **30 October 2026** free-tier pilots were not a successful adjudication:
001 returned a parseable but structurally invalid draft, 002 and 003 ended
with transport errors after sending, and 004 attempted a tool call then hit
HTTP 429 `FreeUsageLimitError`. No valid six-responsibility review resulted;
the attempts are **0 valid, 1 invalid (001), 3 uncertain/incomplete
(002–004), and 35 never attempted**. The comparator's 38 "missing" entries
include the three uncertain attempts; do not report them as never sent.
The first-pass responses must not be treated as accepted findings. Raw logs,
attached-prompt snapshots and comparison queue remain only in the VM's
`/tmp/opencode/phase1c_second_model_attempts_20261030/`. See the [attempt
provenance and author-priority sheet](../reviews/second_model_attempts_2026-10-30.md).

The product catalogue field `attributes_json.archetype_code` in some source
packets is a hash-bound **product attribute**, not an author case archetype or
technical recommendation. It is retained rather than editing sealed facts.
The package auditor rejects `archetype_id`, findings and authoring metadata;
case-level reviewer-only archetype mappings remain excluded.

## Second pass and author decision

After freezing all raw initial responses, compare them with the existing model-assisted matrix and source arithmetic:

```sh
python workflow.py compare --original-packets /tmp/opencode/phase1c_original_packets --configuration-packets /tmp/opencode/phase1c_configuration_packets --credit-packets /tmp/opencode/phase1c_credit_packets --responses /private/responses --output /private/exception_queue.json
```

The comparison validates case identity, packet/provider/scope pins, six fields, source citations, provenance, quote and original complete-zero Credit arithmetic. It classifies disagreement, missing response, invalid/unsupported citation, calculation mismatch or omission, abstention and uncertainty; 020, 029–030 and the supplements are high-priority. Agreements are not acceptance. Numeric checks are bounded to explicitly implemented formulas; other claims still need author inspection. The queue must be reviewed alongside **all 39** responses, including apparently agreeing cases, to guard against correlated model errors.

`author_decision_template.json` keeps every row pending. After Ali personally reviews each source, initial response, exceptions and proposed recommendations, he can record `author_accepted`, `author_rejected` or `revision_requested` with identity `Ali Alnaggar`, timezone-aware date, rationale, resolved ambiguities, exact second-model response hash and assistance disclosure. `workflow.py validate-decisions --decisions ... --responses ... --output ...` checks shape and pins only; it cannot verify that Ali actually made a judgment or that the answer is correct. Do not call this independent expert validation or feed it into the existing human-source-first intake unchanged. The [versioned methodology decision](methodology_decision.md) records Ali's approved direction and its thesis limitation; no case decisions have been supplied.
