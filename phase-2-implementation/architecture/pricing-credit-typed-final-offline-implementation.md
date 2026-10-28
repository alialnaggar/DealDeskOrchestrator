# Pricing/Credit typed final — default-off offline implementation

**28 October 2026.** Ali approved implementation of the
[detailed design](pricing-credit-typed-final-implementation-design.md), not
activation, provider inference, new approval records or a hosted trial.
This increment implements and exercises the **offline** LangGraph contract;
`run_typed_final_offline` accepts only an exact `ScriptedTypedFinal` double,
requires `opt_in=True` and a private owner directory, and is unreachable
through existing hosted M2.0/M2.1 model/manifest gates. Nothing routes the
default hosted or offline specialist graphs to it. Existing terminal attempts
remain terminal and unmodified.

## Implemented boundary

- `typed_final_contract.py`: versioned all-required schema, explicit finding
  and abstention branches, strict JSON parser; existing Pricing and Credit
  claim validators, plus Credit's existing opaque alias projection, decide
  whether source refs and values match authorized returns.
- `groq_typed_final.py`: **serialization only** for a distinct two-message
  no-tools strict-schema request; 8,192 serialized request bytes, 1,024
  configured final completion tokens, 16,384 response bytes, 8,192 content
  bytes and 4,096 reported prompt tokens. Unsupported schema changes stop
  locally. No credential access, HTTP client or sender was added.
- `typed_final_offline.py`: explicit preflight `inspection_plan=1|2` for
  Pricing or `1` for Credit; read-only tool permissions and ledger from the
  existing specialists, LangGraph nodes and conditional edges, exact checked
  evidence, checkpointed protocol/POST reservations, owner-exclusive receipts,
  request digests, no replay on uncertain sends, and an additive reviewer
  projection. Inspections use 512 configured completion tokens each and
  disclose only the scoped tools plus an abstention option, **not** the old
  native terminal function. A failed send cannot fall back. The Config
  prerequisite is an unchanged M2.0 run; the Pricing component is at most
  three POSTs / 2,048 configured completion tokens, and the preflight checks
  its two-turn Configuration contribution against five POSTs / 3,072 total.
  Credit's component is at most two POSTs / 1,536. Successful returns stop
  on reported prompt/response/usage errors; a failed transport has unknown
  usage, never a claimed zero cost.
- `graph_state.py` has additive typed fields. The existing default graphs,
  Phase 1C pin, rules, other four specialists, manifests, legacy wire and
  historical assessment records were not migrated.

## Scenario and verification

On disposable synthetic B05, Configuration's existing AI inspection occurs
first. The offline Pricing double asks to inspect the original line once (or
twice when explicitly preplanned), then cites its returned `fixed_margin_pct`
in a separate no-tools typed finding. Fixed Pricing calculated that field;
the AI neither recalculates margin nor approves the deal. Credit's simulated
finding uses only the redacted alias and is mapped back to a returned Credit
record by the fixed validator. Fabricated refs, wrong values, incomplete JSON,
transport interruption, altered protocol/receipt, budget corruption and
restart attempts fail closed. A final abstention has no validated claims.
The original six fixed findings are unchanged; reviewer additions explicitly
say AI observations only and human approval remains required.

## Deviations and remaining gates

The approved design allowed Pricing to choose whether to inspect again. Here
the one- or two-inspection plan is **frozen before the first send** to enforce
the three-POST ceiling. A later hosted review must decide whether to keep
this explicit plan or add an independently budgeted decision node. Native
inspection requests are built from the legacy serializers, then remove
`submit_finding`; only scoped inspection or abstention is permitted. This
intentional restriction is part of the **new** wire; no existing wire changes.

This is **not** an activated or complete hosted execution path: no hosted
transport, new hosted exact-manifest approval gate, account/cost authorization
or live Groq/schema-compatibility trial exists. Existing M2.0/M2.1 hosted
manifests cannot select it. Reported campaign-wide token accounting is not
implemented for a mixed hosted run; only the offline component and configured
Configuration ceilings are checked. Provider-side strict-schema support is
unverified for this exact request. Before any activation, review and implement
the distinct hosted manifest gate, bind the full investigation/cost accounting
and owner approvals, perform security review and private CI checks, then obtain
Ali's **separate activation approval** for fresh assessments. A subsequent
single narrowly bounded synthetic hosted attempt needs its **own** approval
for exact case/manifest hash, source pin, free-tier billing state, account,
POST/token limits, failure handling and sanitized retention **before a send**.
Neither approval is implied by these offline tests.

No claim about model accuracy, Groq 400 resolution or comparative performance
is possible without an accepted answer key and separately authorized trials.
