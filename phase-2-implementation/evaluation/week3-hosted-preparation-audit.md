# Week 3 hosted preparation audit — no hosted calls

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

## Exact seven skipped tests in fresh full local discovery

All skips are from **unrelated uncommitted Gemma** tests whose read-only
historical synthetic checkpoints were not supplied to this fresh isolated
suite. They do not represent an untested M2.1 or Week 4 test *in this suite*,
but the missing historical Gemma checkpoint validation remains a separate
Gemma migration coverage gap; it is not evidence that Week 4 candidate
integration, cross-model evaluation, role-visible routing or nonempty AR
history are covered.

| Test (module/class/method) | Exact `unittest` skip reason |
| --- | --- |
| `test_gemma_late_diagnostic.SavedLateDecisionDiagnostics.test_all_saved_late_wires_match_and_tampering_fails_without_http` | `Requires existing synthetic read-only checkpoint databases; no model access` |
| `test_gemma_late_diagnostic.SavedLateDecisionDiagnostics.test_isolated_v5_preparation_never_writes_or_sends` | `Requires existing synthetic read-only checkpoint databases; no model access` |
| `test_gemma_one_shot.IsolatedOneShotSafety.test_audit_sync_failure_and_unknown_send_failure_are_terminal` | `Existing read-only synthetic checkpoint required; never live HTTP` |
| `test_gemma_one_shot.IsolatedOneShotSafety.test_crash_after_send_or_reservation_never_retransmits` | `Existing read-only synthetic checkpoint required; never live HTTP` |
| `test_gemma_one_shot.IsolatedOneShotSafety.test_http_timeout_and_token_exhaustion_remain_terminal` | `Existing read-only synthetic checkpoint required; never live HTTP` |
| `test_gemma_one_shot.IsolatedOneShotSafety.test_tamper_and_wrong_destination_fail_before_audit_or_send` | `Existing read-only synthetic checkpoint required; never live HTTP` |
| `test_gemma_one_shot.IsolatedOneShotSafety.test_valid_ready_single_exact_wire_and_sealed_original_unchanged` | `Existing read-only synthetic checkpoint required; never live HTTP` |

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
