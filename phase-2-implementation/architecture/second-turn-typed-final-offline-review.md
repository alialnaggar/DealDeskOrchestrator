# Second-turn typed final — offline contract review, not a runtime decision

**Later design-authorized refinement:** The [Pricing/Credit opt-in implementation
design](pricing-credit-typed-final-implementation-design.md) specifies staged
wire, budgets, checkpoints and approval gates. It does not activate a sender.

**28 October 2026. Proposed design only.** The current Groq
`tool_use_failed` observation is owner-supplied; four exact historical
Console-to-checkpoint matches and the provider's failed generations remain
unverified. The [reassessment](../evaluation/week3-groq-console-tool-use-failed-reassessment.md)
pauses the generic synthetic matrix. This review does not authorize a
provider send, change an existing terminal assessment or adopt a new wire.

## Which operations actually need a function

| Responsibility | Actual read/write boundary | Current model terminal representation | Implication |
| --- | --- | --- | --- |
| Configuration | `inspect_configuration_line` is an authorized, ledgered read of sealed product/rule evidence; fixed Configuration decides validity. | M2.0 `submit_finding` with exact observations or `abstain`, both generated as native functions. | Finding/abstention have **no external side effect** and could be a locally validated typed final; the existing hosted Configuration continuation already succeeded. |
| Pricing | `inspect_pricing_line` reads selected quoted/list/cost and fixed discount/margin facts. Fixed Pricing owns calculations. | Same M2.0 final functions; two second-turn 400s. | Terminal output need not be a function; never turn a model value into a new price or margin. |
| Fulfillment | Scoped stock/path/evidence reads must remain ledgered; proposed partial delivery needs exact fixed rerun of all six candidate checks and Routing, not a model commitment. | Hybrid decision functions request scoped reads or submission **intent**. A separate no-tools `strict: true` structured final carries proposal/finding/abstention, then deterministic candidate validation. | A precedent for a two-stage contract, **not** evidence the M2.0/M2.1 final schema is supported or better. Keep its current intent/proposal/correction behavior. |
| Credit | `inspect_customer_credit_evidence` reads redacted dated profile/AR/payment projection; aliases map only within one frozen bundle. Fixed Credit owns exposure/hold/headroom. | M2.1 native `submit_finding`/`abstain`; two second-turn 400s. | Terminal output can be separate, but alias mapping, exact returned-value checks and withholding remain mandatory. |
| Policy | `inspect_fixed_policy_hits` returns selected policy hits and rules; missing hits/prerequisites never imply a pass. | M2.1 native finding/abstention. | A typed final could carry observations only; cannot waive or infer compliance. No hosted Policy result yet. |
| Approval Routing | `inspect_fixed_route` reads the *fixed* route/role availability; human signs. | M2.1 native finding/abstention. | A typed final could report checked observations, not add/remove roles or authorize. No hosted Routing result yet. |

The first inspection is a genuine permissioned tool operation. A later
finding or abstention **only terminates a model investigation**: it is not a
stock reservation, database write, approval or independent rule check.
For example, B01's original ten-unit stocked deal could yield one scoped
Credit-profile observation: the mock terminal could cite the exact returned
credit-status scalar or abstain; the pinned fixed Credit still computes its
finding and fixed Routing remains withheld. This prototype did **not** ask
Groq to assess B01 or change its historical result.
Current M2.0 allows up to two inspections/three turns, whereas hosted M2.1
allows one inspection/two turns; an exact final-stage contract would need
explicit transition rules and must not silently remove M2.0's valid second
inspection route. A failed inspection or missing permitted evidence is not a
license to fabricate a final finding.

## Provider-independent terminal result v1 (offline prototype)

`backend/tests/terminal_final_offline_design.py` is **test-only**. After a
completed, identity-checked inspection, the orchestrator checkpoints the
original's assessment/run/subject, frozen bundle/source-input digests,
specialist, model/prompt/wire version, selected evidence and verified tool
ledger. It constructs a **separate, no-tools** final request from the exact
completed ledger result. In M2.1, use `model_view` for opaque subject/record
aliases; never publish raw Credit/customer/AR identifiers. In M2.0, preserve
the already-scoped selected observation. The model emits only:

```json
{"version":"terminal-final-offline-v1","kind":"finding",
 "claims":[{"ref":"<returned ref or alias>","field":"<returned field>",
            "value_json":"<exact JSON scalar>"}],
 "uncertainty_reasons":[],"reason_code":"none"}
```

All five keys are present for both variants. `abstain` requires **zero**
claims/uncertainty reasons and one of `insufficient_evidence`,
`model_uncertainty`, `unsupported_capability`; `finding` requires 1–6 claims
and `reason_code=none`. M2.1 requires empty uncertainty reasons; M2.0 keeps
its existing bounded uncertainty list. Strict schema constrains shape;
Python **still** checks branch invariants, scalar type, exact value, returned
ref/alias, specialist scope, source/ledger identity and approved evidence
using existing `_validate_claims` (M2.0) or alias reversal plus `_claims`
(M2.1). The resulting *action* is the already-typed finding/abstention; the
model cannot echo an identity into authority. `stop` with one bounded JSON
content, no tool calls and counted usage is required. Incomplete/length or
malformed responses, denial, incorrect refs, uncertain reservation or
provider errors become terminal **AI errors**, never inferred abstentions,
accepted findings, retries or a fixed-rule override. A known model
abstention is distinct from such errors.
The mock builder rejects a final request above 8,192 serialized bytes; real
source and permission checks would still be owned by the trusted runner.

The strict-mode schema is intentionally a simple common envelope, with all
fields required and `additionalProperties=false` at every object. Cross-field
constraints stay in trusted Python rather than rely on unconfirmed JSON
Schema union/conditional support. The example above is a *schema and local
parser proposal*, not a provider-tested contract. No extra database or
framework, external SDK or provider is added.

## Groq compatibility (public documentation only)

[Groq Structured Outputs](https://console.groq.com/docs/structured-outputs)
lists `openai/gpt-oss-120b` among models supporting `response_format` with
`type=json_schema`, `strict=true`. It requires all properties and forbids
additional object properties; it claims constrained JSON-schema decoding,
but expressly states that **tool use and streaming are not supported with
Structured Outputs**. Therefore do **not** add `response_format` to the
existing second request while advertising tools or assume a historical
assistant/tool-call transcript is accepted alongside strict mode. The
proposal instead uses a fresh no-tools final request carrying only the
verified, bounded evidence projection as task data. Groq's
[local-tool guide](https://console.groq.com/docs/tool-use/local-tool-calling)
shows a follow-up after a tool result, often with more functions; it does not
prove the separate no-tools final has identical behavior. The repository's
[B05 Fulfillment result](../evaluation/m20-groq-wire-continuation-hosted-result.md)
accepted a **different** separate strict structured final with a 1,024-token
ceiling, after a native tool-intent stage. That is a narrow compatibility
precedent, **not** a Pricing/Credit benchmark or approval for this schema.

Strict decoding removes the **required native final-tool-call** obligation
from the last request. It does not guarantee *true* citations, output before
token exhaustion, correct source interpretation or provider acceptance of
this particular schema. It may exchange a `tool_use_failed` mode for a
structured-output/schema/budget failure (best-effort `strict=false` explicitly
allows malformed output/400). Doc claims of schema adherence do not replace
our semantic verifier or prove superiority. No response formatting mode is
safe to pair with tools in the same send under current docs.

## Alternatives and adoption gate

| Approach | Advantages | Costs/limits |
| --- | --- | --- |
| Keep native `submit_finding`/`abstain` (`required`) | Current M2.0/M2.1 API, tested three-function wire and permission/receipt system; successful Configuration controls. | Suspected final tool-generation failure remains; inspector advertised when it may no longer be eligible; 512 output cap unmeasured for failed generations. |
| **Separate strict typed final (preferred offline design)** | No terminal tool call; preserves exact deterministic validation; B05 demonstrates a different strict no-tools final can succeed. | New stage, prompt/response parser, context re-projection and checkpoint/wire identity; model may struggle with schema/limits, and a nominal 1,024 cap would change cost/budgets. Not approved for live use. |
| Constrained hybrid fallback | Retain native inspection and old terminals where they work; choose typed final by **preflight** case/capability/contract policy or separately reviewed migration. | Must never auto-fallback to another POST after 400, timeout, malformed/uncertain receipt or process crash; new request needs a **fresh** approved identity and budget. A free-text `auto` response is not a finding. Mixed protocols increase test, audit and learning cost. |

**Recommendation:** Design a staged Pricing/Credit-first opt-in path for a
*future* separately approved implementation, since those are the observed
stopped specialists; keep Configuration, Policy, Routing and the existing
Fulfillment hybrid unchanged until their source/budget and evidence contracts
are reviewed. The typed terminal shape can ultimately be shared, but a
uniform six-specialist cutover would conflate distinct proposal, fixed
verification and unavailable hosted results. Within the approved Python,
LangGraph, PostgreSQL and replaceable-model architecture, this is a material
**wire and completion-budget** proposal, not a new infrastructure/provider.
Trade-offs include added state/parse/test work, potentially higher Free-tier
token usage and learning a separate strict schema; keeping current native
tools costs less integration but retains the observed blockage. Seek Ali's
explicit approval before implementing any active prompt/wire/budget changes
and record the decision in the decision log only once approved.

**Integration gates if approved later:** pin stage contract/prompt/wire
version and immutable request digest before a one-use send; verify checkpoint
state, exact tool ledger, source fingerprint and owner receipt on restart;
never replay reserved/failed/uncertain attempts. Preserve original and
candidate isolation, deterministic fixed rule/routing authority and explicit
AI abstention/error distinctions. Test full isolated PostgreSQL restart,
source mismatches, limits, receipts, non-secret reviewer projection and CI
before any new hosted manifest. Each future provider trial would separately
require new assessment, exact owner-approved manifest, budget and billing
check; this document authorizes **none**.

Focused mock-only suite passed **38/38** tests (new prototype, existing Groq
classifier and M2.0/M2.1 wire checks). Prototype tests exercise five
specialist observation types, strict
shape, valid finding/abstention, fabricated/aliased refs, wrong value/type,
missing/length output, changed ledger/checkpoint, timeout and no-replay
receipt. No production implementation changed; no new database regression
is needed for this offline-only design. Private CI for this increment remains
unverified.
