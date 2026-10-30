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

## Second pass and author decision

After freezing all raw initial responses, compare them with the existing model-assisted matrix and source arithmetic:

```sh
python workflow.py compare --original-packets /tmp/opencode/phase1c_original_packets --configuration-packets /tmp/opencode/phase1c_configuration_packets --credit-packets /tmp/opencode/phase1c_credit_packets --responses /private/responses --output /private/exception_queue.json
```

The comparison validates case identity, packet/provider/scope pins, six fields, source citations, provenance, quote and original complete-zero Credit arithmetic. It classifies disagreement, missing response, invalid/unsupported citation, calculation mismatch or omission, abstention and uncertainty; 020, 029–030 and the supplements are high-priority. Agreements are not acceptance. Numeric checks are bounded to explicitly implemented formulas; other claims still need author inspection. The queue must be reviewed alongside **all 39** responses, including apparently agreeing cases, to guard against correlated model errors.

`author_decision_template.json` keeps every row pending. After Ali personally reviews each source, initial response, exceptions and proposed recommendations, he can record `author_accepted`, `author_rejected` or `revision_requested` with identity `Ali Alnaggar`, timezone-aware date, rationale, resolved ambiguities, exact second-model response hash and assistance disclosure. `workflow.py validate-decisions --decisions ... --responses ... --output ...` checks shape and pins only; it cannot verify that Ali actually made a judgment or that the answer is correct. Do not call this independent expert validation or feed it into the existing human-source-first intake unchanged. The [versioned methodology decision](methodology_decision.md) records Ali's approved direction and its thesis limitation; no case decisions have been supplied.
