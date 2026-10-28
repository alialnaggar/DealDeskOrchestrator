# Pricing/Credit typed final — detailed opt-in implementation design (not activation)

**28 October 2026. Design authorized; implementation and hosting are not.**
Branch `phase2-agent-implementation`. This refines the
[offline architecture review](second-turn-typed-final-offline-review.md) and
[test-only prototype](../backend/tests/terminal_final_offline_design.py).
Groq Console `tool_use_failed` is owner-supplied and not matched row-by-row
to four local receipts. No claim is made that this design fixes their cause.
Existing `m20_groq.py`, `m21_groq_contract.py`, LangGraph runners, manifests,
receipts and terminal historical identities stay unchanged by this document.

## 1. Scope, immutable authority and state sequence

The **default** remains the existing three-tool `required` model path. A
separately versioned opt-in applies only to *Pricing* (M2.0) or *Credit*
(M2.1), selected before any attempt for a **new** assessment. It cannot be
enabled on an existing checkpoint or retrofitted to a failed request. The
original deal, frozen as-of cut-off, transaction snapshot, source fingerprint,
six deterministic findings, approval route and source-bound evidence remain
unchanged; AI findings are observations, never price/credit clearance or human
approval. Configuration runs first under its old wire; Policy, Routing and
Fulfillment keep their own old implementations. No automatic switch after a
provider failure or unknown response.

```text
new source-pinned original + fixed result
  → select default or opt-in protocol in preflight (immutable per specialist)
  → inspection decision: same scoped native read-only function and fixed
    permission/ledger reservation (Pricing may inspect at most twice;
    Credit exactly once for a finding)
  → checkpoint returned provider call, usage and completed tool receipt
  → select no-tools final stage only after verifying exact completed ledger,
    frozen run identity, aliases and any permitted second Pricing inspection
  → build a separate system+user request (not a tool-call continuation),
    freeze digest and checkpoint final reservation BEFORE owner-only send receipt
  → one bounded `strict: true` JSON-schema final, `finish_reason=stop`
  → local schema + branch + evidence verification → finding / abstention / error
  → existing AI result and human-review projection; fixed results unchanged
```

Pricing's optional second inspection remains a native tool decision using
its existing permissions and up-to-three-turn ceiling; after **one or two**
completed inspections its terminal is a separate no-tools final. Credit's
model may abstain on the first decision, as today; a finding requires its
single completed inspection, followed by the no-tools terminal. If an
inspection errors or no permitted read completes, never generate a finding.
Changing Pricing to one inspection or forcing a final when evidence is
insufficient would be a *separate* scope decision, not implied here.

## 2. Provider-independent typed contracts and verification

Define a versioned `TerminalFinalV1` independent of Groq transport:

```text
{version: "terminal-final-v1",
 kind: "finding" | "abstain",
 claims: [{ref: str, field: str, value_json: str}],
 uncertainty_reasons: [str],
 reason_code: "none" | "insufficient_evidence" |
              "model_uncertainty" | "unsupported_capability"}
```

All top-level fields required (one shared simple schema); each claim has
exactly three required fields. `finding`: `reason_code=none`, 1–6 claims,
Pricing retains at most five bounded (128-character) uncertainty reasons,
Credit requires zero. `abstain`: empty claims and uncertainty list, one of
the three existing reason codes. An unknown, incomplete, unsupported,
length-truncated or malformed response, provider rejection or lost receipt
is **error**, not model abstention. A no-tool final does **not** request a
read; the inspection remains a separate permissioned call.

For Pricing reuse the scoped `inspect_pricing_line` ledger result and
`m20_specialists._validate_claims`; a `value_json` must decode to the exact
returned primitive with no coercion, using existing Pricing `pricing_line:`/
`pricing_rule:` prefixes. For Credit reuse `m21_redaction.model_view` and
`m21_specialists._claims`: model sees only the existing per-bundle opaque
aliases, allowlisted selected fields and as-of context; validate visible
alias/field/value before mapping back to the **same** ledger's original ref.
Never expose raw customer, invoice, payment match or commitment IDs and
never let a model-supplied identity replace the pinned one. Confirm each
observation corresponds to a completed authorized receipt for the same
assessment, original subject, specialist, permission version, bundle SHA,
source-input digest and tool; compare exactly with the checked ledger, not
only by ref. Unrecognized, duplicate or swapped aliases fail closed. Keep
six-claim and size limits and existing fixed prerequisites. Final output
returns the existing `{kind: finding, claims, uncertainty_reasons}` (Pricing),
`{kind: finding, claims}` (Credit), or `{kind: abstain, reason_code}` action;
the current downstream reviewer sees **validated claims only**.

The test-only prototype demonstrates this projection for one inspection,
including five specialist fixture shapes; it is **not** production code. Its
helper takes trusted caller-supplied `completed_ledger` and does not fetch
checkpoint/tool receipts, implement Pricing's second inspection, or enforce
the full typed runtime version/budget/owner contract. These are required
implementation tasks, not already-satisfied acceptance criteria.

## 3. Wire specification and compatibility boundary

Provider-neutral service owns `TerminalFinalV1`, validated observations,
source binding and result taxonomy; a replaceable provider adapter owns
serialization/response parsing. Give the opt-in adapter a **new** wire and
prompt version distinct from `m20-groq-native-tools-v1` and
`m21-groq-native-tools-v1`. Do not reuse `terminal-final-offline-v1` as a
live contract without a reviewed version change. Pricing decision stage
retains current native inspection wire where valid; Credit decision stage
retains current aliased inspection projection. The Groq **final** request:

```json
{"model":"openai/gpt-oss-120b","temperature":0,
 "max_completion_tokens":1024,
 "messages":[{"role":"system","content":"<new versioned terminal-only instruction>"},
             {"role":"user","content":"<canonical pinned input + exactly returned selected evidence>"}],
 "response_format":{"type":"json_schema","json_schema":{
   "name":"pricing_credit_terminal_v1","strict":true,
   "schema":"<versioned all-required, additionalProperties:false schema>"}}}
```

This is a **new two-message request**, not replay of the assistant/tool
conversation. No `tools`, `tool_choice`, tool-role messages, `parallel_tool_calls`,
`stream` or `reasoning_format=raw`; never put structured output and tools in
the same request. Pin prompt bytes, canonical encoding, schema name/hash,
model ID, provider version where available, and serialized request SHA before
reserving. Do not include hidden evaluation answers, rule-result authorizations
or unredacted Credit records. Local `finish_reason=stop`, exactly one choice,
one bounded JSON `message.content`, zero `tool_calls`, recognized usage and
explicit schema/semantic checks are mandatory. Treat refusal/content filter,
`length`, malformed JSON, extra fields, bool/int confusion and incorrect
cross-field combinations as errors; no response text is an approval.

[Official Groq Structured Outputs](https://console.groq.com/docs/structured-outputs)
lists `openai/gpt-oss-120b` for `strict:true`, requires every field and
`additionalProperties:false`, and says Structured Outputs does **not**
support tool use/streaming. Groq's local-tool guide permits independent
native inspection and documents `required` tool-generation 400. The old
Fulfillment accepted a **different** no-tools strict final under a 1,024
ceiling; this is not proof that Pricing/Credit's schema or two-message
projection will work. Strict schema controls **syntax**, not evidence truth;
constrained decoding may replace `tool_use_failed` with schema/length/semantic
errors. Best-effort JSON is not a silent fallback; the native terminal-tool
default stays available only for *new* preselected runs. No current Groq
capability check, request or metadata lookup is authorized here.

## 4. Checkpoint and no-replay migration

Add **new, opt-in-only** versioned state/attempt metadata; do not reinterpret
old attempt ordinals or modify completed originals. Before the first model
turn, bind assessment/run/original-subject, pinned evidence bundle and source
fingerprint, as-of/snapshot, specialist, protocol selection, model, schema,
prompt/wire/permission versions and owner manifest hash. Enforce one
immutable selection per specialist across restarts; old checkpoints lacking
the opt-in version always continue on their old path or remain terminal.

At each stage, persist an append-only `reserved` attempt with distinct
`inspect_decision` versus `typed_final` identity, ordinal and canonical
request digest **before** the provider call. Extend the existing
`hybrid_send_reservation.claim_and_call` / `verify_receipt` primitives only
with a reviewed, new stage label and owner-path allowlist (today's allowed
labels are `decision`, `final`, etc.; M2.1 currently hard-codes `decision`
and two ordinals). Do **not** make new final receipts collide with M2.0,
M2.1 or Fulfillment paths; an alternative is a distinct bound stage/ordinal
namespace, approved before code. Enforce `0700` owner directory, `0600`
receipt/approval modes and OS-exclusive owner lock. After response, store
sanitized returned/error metadata and usage, never arbitrary provider body
or error text in receipts or review. Validate the checked tool-result ledger
on resume and re-project alias mapping from the sealed source; no stored
model-provided ref map may become authority. The M2.1 gate's exact
model-type, manifest keys, campaign totals, owner directory allowlist,
ordinal→stage mapping and final receipt checks must be **versioned**, not
relaxed globally; M2.0 currently has checkpoint reservations and owner lock
but needs explicit per-POST durable receipt integration for this path.

On restart: a completed inspection with verified returned receipt and
completed tool ledger may advance **once** to an unreserved final after
rebuilding the exact versioned request; a final `reserved` with no verified
returned-and-validated checkpoint is terminal **uncertain**. A `failed`,
reserved-only, returned-but-unparsed, parse-invalid or digest-mismatched
receipt never licenses another send, another protocol, or fallback within the
same assessment. Audit file/checkpoint write ordering and process-crash
windows explicitly; avoid treating `returned` receipt alone as a verified
finding. Historical four Pricing/Credit attempts are terminal, immutable,
not migration inputs. New cases require fresh assessment, checkpoint and
owner directory.

## 5. Independent, proposed budgets (NOT current authorization)

| Ceiling | Existing relevant contract | Proposed opt-in limit and rationale |
| --- | --- | --- |
| Pricing stages | M2.0: ≤2 inspections, ≤3 turns; global ≤6 reserved sends. | Up to **2 native inspection decisions + 1 typed final = 3 sequential POSTs**; preserve second read and old three-turn limit. No retries/fallback. |
| Credit stages | M2.1: 1 inspection, 2 turns; case ≤6 sends (or spent diagnostic ≤2). | **1 inspection decision + 1 typed final = 2 POSTs**. A first-turn native abstention ends without a final. Other specialists untouched. |
| Per-POST serialized JSON | Existing M2.0/M2.1 wire ≤8,192 bytes. | **8,192 bytes including schema and escaped observation**, checked before reservation; fail closed if selected evidence cannot fit, never truncate citations. |
| Per-POST prompt/response | Existing returned prompt ≤4,096 tokens; provider response ≤16,384 bytes, action ≤8,192. | Retain **4,096 reported prompt-token post-send validation** and **16,384 response/8,192 action bytes**; token counts on failed POSTs are unknown, so this is *not* a guaranteed pre-send prompt cap. |
| Configured completion | Existing 512 per native decision/final. | Inspection remains **512**. Typed final proposes **1,024** for 1–6 exact claims plus strict envelope, informed only by B05's different accepted 1,024-budget structured final. Does **not** establish 512 caused the 400s or 1,024 resolves them. No automatic upshift. |
| Configured aggregate | Existing M2.0 aggregate ≤6 × 512 = 3,072; existing M2.1 six × 512 = 3,072. | Pricing-only **≤2,048** (512+512+1,024), Credit-only **≤1,536** (512+1,024). Existing Configuration two-turn 1,024 + Pricing max 2,048 = **3,072 over ≤5 POSTs**. In the full M2.1 order, Credit 1,536 + Policy 1,024 + Routing 1,024 = **3,584 over ≤6 POSTs**; this **raises** M2.1's configured total by 512 and requires approval. |
| Reported investigation stop | Existing `HOSTED_REPORTED_TOKEN_STOP=24,000` is checked after returns, not a hard cost cap. | Retain **24,000 reported total-token post-send stop**, fail closed on missing/unverifiable usage. With six M2.1 POSTs each later reporting 4,096 prompt tokens, a theoretical reported total could be **28,160** (24,576+3,584) before the final post-send check. This is a bound *conditional on all successful responses passing reported per-POST validation*, not a pre-send spending guarantee; choose a stricter campaign budget and stop earlier if a hard cost ceiling is needed. |

The Pricing-only 2,048 figure is a **component** ceiling, not an executable
hosted M2.0 campaign: that graph requires completed Configuration AI before
Pricing. A new case under the existing graph must budget its unchanged
Configuration sends too (up to **five POSTs/3,072 configured completion
tokens** total); do not bypass its prerequisite. An initial Credit-targeted
case can use a new, explicitly scoped Credit-only gate if implemented and
approved, with the fixed Pricing prerequisite still checked. Do not
automatically enable a full six-specialist campaign. All request/count
caps are engineering safety limits, not financial/policy thresholds. The
future approval must specify provider account, cost policy, token budgets,
error capture limits and no metadata calls unless separately authorized.

## 6. Implementation map, offline tests and staged approvals

**Only after implementation approval:** create a provider-independent
terminal/result schema and parser with deterministic validation; write a
Groq-specific **new** adapter/prompt; add opt-in graph conditional routing
and immutable state/receipt stage markers; version M2.0/M2.1 manifest gates
without accepting old authorizations for new wire. Keep old adapters and
their wire hashes/test fixtures unchanged; no rules, Phase 1C pin or
database framework change. Prefer a named adapter/capability rather than
switching `GroqM20Model` / `GroqM21Model` behavior by a mutable flag after
start. Do not select fallback on exception. Review security/cost/learning
impacts before adding new dependencies; none is proposed now.

**Offline acceptance tests:** schema shape and two-message no-tools wire;
byte/digest and budget checks; Pricing one/two inspections, Credit alias
redaction, cross-domain default denial, exact scalar types/refs and
abstention taxonomy; invalid/multiple/length/refusal/JSON/fabricated/duplicate
claims, missing usage, oversize, failed tool and partial source evidence;
false/tampered authorizations, wrong provider or prompt/schema version;
`reserve→returned→validated` success and crash at *every* checkpoint/file
boundary; reserved-only/failed/returned-but-unparsed must never replay or
fallback; old wire/receipt/manifest and completed/terminal checkpoint
compatibility. Run isolated PostgreSQL integration for original+ledger+
checkpoint/restart/reviewer and a **fresh seven-database backend regression**
with deterministic mock model; inspect private CI before any activation.
No paid model call is needed for this gate. Existing prototype's **38/38**
focused tests cover only test-only one-inspection fixtures and receipt
primitives; they do not satisfy the future graph/Pg acceptance tests.

**Future hosted acceptance (not approved):** preflight one fresh pinned
synthetic case, exact new manifest SHA, private owner-only approval and
single selected Free-tier/billing-disabled account; one **targeted** Pricing
or Credit specialist, plus any mandatory unchanged Configuration prerequisite,
with explicit per-specialist inspection/final ceilings; no retries, metadata
GET or credential fallback. Stop at any invalid native call, failed
permissioned read, 400, unexpected usage, malformed final or uncertain
reservation; inspect only allowlisted sanitized outcomes. Ali must approve
**each** new manifest/identity after reviewing offline results and budget.
No historical attempt may be reused. A real result would test feasibility,
not establish model superiority, accuracy or business approval.

**Evaluation plan:** record per attempt provider/model/schema/prompt/version,
configured budget and reported prompt/completion tokens (unknown on failed
responses), time, status, receipt, requested tool, abstention reason,
validated-claim count, exact returned source refs and fixed-rule IDs without
publishing sensitive text. Define *schema validity* as one stop-response
passing envelope + branch checks; *evidence accuracy* as exact matches to
scoped ledger and separately reviewed independent answers (not model
confidence); *abstention rate* among eligible assessed cases, separating
first-turn abstentions and final abstentions; *failure rate* by transport,
schema, semantic validation, permission, budget and restart; and usage per
completed/attempted assessment with unknown failed usage explicitly unknown.
Compare against the old terminal-tool path only on **new**, comparable
source-pinned, consented cases with matched provider/version and budgets
reported separately; old terminal assessments cannot be replayed as controls.
No measured accuracy or lower 400 rate is claimed before independent accepted
answers and actual comparative runs.

**Decision gates:** (A) Ali approves or revises this *detailed design* and
its material wire/budget/receipt-stage changes **before production code**;
record that approval in `planning/decision-log.md`. (B) After offline/Pg/CI
review, Ali separately approves **opt-in activation** on fresh assessments,
not existing terminal ones. (C) Ali separately authorizes **each hosted
trial**, its source and case, account/billing state, manifest hash, budgets,
retention and private approval artifact, before any send. This document
constitutes none of (A)–(C); the current permission covers design only.
