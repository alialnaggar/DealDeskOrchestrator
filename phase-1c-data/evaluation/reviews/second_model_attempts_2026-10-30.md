# Blinded second-model attempt log and author-priority sheet — 30 October 2026

**No accepted answers; no valid second-model draft.** Verified remote Phase 1C
head before execution: `baa244248d1aa1a9cd1618887363f58e007ab56b`.
The separate clean Phase 1C worktree was fast-forwarded to that head; the
Phase 2 `fe250fd132a149bef7ccebad0148147cf60f6c29` checkout and its
uncommitted Gemma work were untouched. PR #1 is not changed.

## Reproducible source and leakage checks

`workflow.py prepare` read the 4b4b1c7-era fresh PostgreSQL packet directories
under `/tmp/opencode/phase1c_{original,configuration,credit}_packets`. Each of
the **39** materialized source/provider/scope hash bindings matched its
repository pin; the source packages contained only `sources.json` and
`blank_response.json`. A second materialization produced byte-for-byte
identical 79 files (39 source packages, 39 blank forms, one manifest). The
recursive structural audit found no answer keys, author `archetype_id`, draft,
technical recommendation, accepted outcome or model-assisted result in any
source package. The source product attribute `archetype_code=WORKSTATION` is
a legitimate pinned catalogue field, not an evaluation archetype hint. No
sealed source bytes were rewritten. The original 36, supplemental 039 and
Credit 040–041 remain separate; 037–038 are preflight diagnostics.

Commands, from `phase-1c-data/evaluation/second_model_review`:

```sh
python -m unittest -v test_workflow
python workflow.py prepare --original-packets /tmp/opencode/phase1c_original_packets --configuration-packets /tmp/opencode/phase1c_configuration_packets --credit-packets /tmp/opencode/phase1c_credit_packets --output /tmp/opencode/phase1c_blind_verified_20261030
python workflow.py compare --original-packets /tmp/opencode/phase1c_original_packets --configuration-packets /tmp/opencode/phase1c_configuration_packets --credit-packets /tmp/opencode/phase1c_credit_packets --responses /tmp/opencode/phase1c_second_model_attempts_20261030/responses --output /tmp/opencode/phase1c_second_model_attempts_20261030/exception_queue.json
```

The seven-test structural suite passes, including an injected author-archetype
leak, invalid citations, arithmetic, changed model pricing and no automatic
replay of a previous uncertain send. The comparator
currently queues **39/39** (one invalid response, 38 missing), not 39
substantive disagreements. There is no basis yet for an agreement rate or
business-correctness claim. `ready_for_generation=false`.

## Model attempts, identity, cost and provenance

Local OpenCode v2.0.31 advertised the OpenCode-hosted models below with
input/output/cache pricing all zero. Each call used a **separate standalone
session from the single-case blind folder**, attaching only that case's
`sources.json` and `blank_response.json`. Prompts required the six-role JSON
contract, source citations, uncertainty, explicit model disclosure and no
prior answers. Inference variant was `default`; no sampling temperature/seed
was pinned by the CLI, so outputs are not deterministic reproductions. Model
responses are AI-only and not independent human review. The pilot prompt
snapshots below are the exact attached user messages saved from their OpenCode
sessions; raw JSONL and stderr remain at
`/tmp/opencode/phase1c_second_model_attempts_20261030/` on this VM.

| Case | OpenCode model/version | Session | Attached prompt SHA-256 | Raw event SHA-256 | Outcome |
| --- | --- | --- | --- | --- | --- |
| 001 | `opencode/beam-free` | `ses_e721f0fecffews0rogOLse5fQB` | `1c9ba8f4b32e77739aaf2856f460dc45d35af617356ae48409e51053ac6c72c3` | `668633f4876b04724b140ab2445d28a6bee9e8e1bf8dc62826e194d3c8bd8887` | Completed at cost 0; JSON parsed, but all six finding labels were outside contract and citations used strings rather than `{document,pointer}` objects. **Invalid, pending.** |
| 002 | `opencode/deepseek-v4.1-flash-free` | `ses_e721de846ffek31QxT01dVhBzA` | `90bb89bc034b6aae9bed460e46a3ea3a3ffbef00376e969f8b8ea1a3ccf1329c` | `cfd6eeba4945b292814f018194d160cb055a5185f57e37d7bd85bcf80efb37e2` | Sent, then socket closed unexpectedly; no draft. **Uncertain send, no automatic retry.** |
| 003 | `opencode/glm-5.3-flash-free` | `ses_e721af206ffemn7Z7VlqBMKPJr` | `0a5a1c6c1a8b901fd42e9f2ea53fedfda98641f09b0b4a93fc35017b346b011a` | `ead673c5ffdf93d3ca43788ff2040244fe462f747780c824fd3489fac3bbc34c` | Sent, then socket closed unexpectedly; no draft. **Uncertain send, no automatic retry.** |
| 004 | `opencode/nemotron-3.5-lightning-free` | `ses_e72184b88ffeSVKfq8L7e6qJzc` | `a51586ad77d0ccb8ebabef7eca9d8f2d212513bf2d48fbcc7154b861aea9e456` | `bd05c62c34fdbb854e99f85f6bfe8d8fc6488f27ac1240f3fefea8f04433d23c` | Called a tool despite the no-tools instruction (tool input referenced only its two blind files), then HTTP 429 `FreeUsageLimitError`. No complete response; **pending, no automatic retry**. |

No paid endpoint was called or authorized. The confirmed shared free-tier
quota stop makes further unattended sends inappropriate. The fastest safe
route when quota becomes available is one fresh-case free-model pilot through
`run_free_batch.py`, with its live zero-price check, pre-send checkpoint,
raw-log retention, citation/arithmetic validation and stop-on-error behavior;
only then use batches of up to three. Cases 002–004 require manual inspection
and an explicit new-attempt decision because sends/tool use occurred. If free
quota cannot reliably finish 39 reviews, ask Ali for explicit paid-model
budget/provider authorization rather than silently spending or substituting
the same invalid model. Do not treat an error as a first-pass completion.

## Short author-decision agenda (questions, **not** adjudications)

The automated exception queue is currently dominated by absent reviews. Keep
the case-level [author decision register](../second_model_review/author_decision_template.json)
entirely pending; first collect valid, provenance-bound model drafts. Then
prioritize these *source-bound* business choices while inspecting both model
and source, without converting any suggested gate to an accepted answer:

1. **020 — conditional delivery interpretation.** Four workstation units are
   requested by 11 September; the confirmed receipt is 2 October, while the
   earlier `EVAL36-020-OFFER` has lead min/mode/max **2/4/6 days** and
   workshop steps need separately dated capacity. Should a feasible *modal*
   conditional route count as `needs_commitment` under G1 even though the
   maximum-lead route lacks the required test slot, or should date/evidence
   uncertainty change the gate? State precisely which dates, steps and
   customer commitments would be necessary. Sources: packet
   `/source_rows/deal/requested_delivery_date`, `/source_rows/inbound_supply`,
   `/source_rows/supplier_offers`, `/source_rows/production_capacity`.
2. **029–030 — regional attribution.** Each submitted DE-BY service has an
   exact active `installation_eligibility` rule with `eligible=false` for
   DE-BY. Decide how an explicitly ineligible region is attributed across
   Configuration versus Availability and whether a changed region/service
   requires a new proposal. Do not infer an appointment or treat missing
   coverage as denial. Sources: packet `/source_rows/compatibility` and
   `/source_rows/deal/destination_region`.
3. **039 — V2 product dependency.** Verify the required add-on is absent, the
   whole-deal blocker scope is exact, and subordinate pricing, stock, Credit,
   Policy and Approval findings survive a proposed blocker. Its model-assisted
   draft is **not** an answer. Sources: supplemental packet `/source_rows/compatibility`
   and `/source_rows/lines`.
4. **040–041 — distinguish nonempty debt from unknown population.** 040 has
   €1,000 invoiced, €300 paid and €700 overdue in an explicitly complete
   fictional population. 041 has no selected rows **and explicitly incomplete
   scope**. Decide required evidence and human actions separately, without
   declaring clearance from a zero row count. Sources: control packets
   `/source_rows/receivables`, `/source_rows/payments` and trusted
   `credit_scope`.
5. **Other 33 originals:** group apparently matching outputs for bounded
   source-first inspection, including stale observations (005–006, 017–018),
   digital proof/term (021–026), credit cap (031–032), price floor (033–034)
   and legal clause (035–036). Agreement alone never accepts a case; keep
   the original 36 separate from 039 and 040–041.

Ali's case-level interpretation, source-first rationale and explicit
author-accountable disposition are still required. This workflow cannot
establish independent human expert validation; any change in academic
requirements must be decided by the appropriate academic authority.
