# M2.1 original-only Credit, Policy and Routing — offline method and limits

**Later hosted-preparation audit (28 October, no hosted calls):**
The [source-verified case/skip/test audit](week3-hosted-preparation-audit.md)
adds a provider-independent redacted synthetic-only evidence view, a dormant
Groq native-tool wire/strict response contract and mocked transport/error
tests. **The M2.1 runner still rejects hosted models** until a separately
reviewed durable owner/manifest/credential gate and end-to-end hosted-path
tests exist. Latest fresh local regression: **263 tests, seven unrelated
Gemma checkpoint skips**; no CI claim or inference result is implied.

## 28 October Week 3 integration update — offline only

The original-only [Week 3 LangGraph composition](../backend/dealdesk_phase2/week3_offline.py)
now runs the existing fixed original and bounded Fulfillment investigation,
then Configuration/Pricing and separate Credit, Policy and Routing
investigations. It uses the existing PostgreSQL checkpoint, tool ledger,
permission scopes and per-model reserved attempts; it introduces **no**
candidate verification, database write tool, hosted adapter or approval
authority. The composition refuses hosted model objects and binding proposals
and gates its final handoff on six fixed results, all five non-Fulfillment AI
results and the original-only reviewer package. Each underlying stage
rechecks the same pinned run/source identity on restart. The outer ephemeral
graph is re-entered from the start after a process stop; completed inner
stages are not resent or recharged. An interrupted reserved Credit turn is
marked an AI error on restart without calling that model again, while later
Policy/Routing investigations may still report separate observations.

Three [static versioned trusted instructions](../backend/dealdesk_phase2/m21_prompts.py)
state domain/authority boundaries. Their offline envelope places all task
inputs and returned observations in a separate user role. Prompt version
`m21-original-system-v1` is recorded in each M2.1 input, model attempt and
result, and is checked on restart. Existing offline results bearing the
earlier `m21-original-evidence-v1` prompt label remain readable; a previously
reserved turn is recognized by pinned assessment/specialist/ordinal regardless
of its old prompt label, so a prompt-version upgrade cannot replay it. **There
is no hosted Week 3 adapter that
actually sends these prompts yet**; the offline doubles consume typed inputs,
not prompt text. Future provider integration requires a separate security and
redaction review. Existing M2.1 selected-source tools, typed exact-value
claims, evidence checks and abstention/error logic were retained rather than
rewritten. Policy cannot infer a pass from absent hits or unknown per-rule
prerequisites; withheld Routing cannot infer empty approval roles.

For synthetic B01, the fixed original still needs revision and Routing is
withheld. An offline model double observes the dated, same-customer Credit
profile, the selected fixed Policy delivery-rule hit and the fixed withheld
route; the other doubles inspect Configuration and Pricing, while Fulfillment
abstains. Fixed Phase 1C alone computes credit/margin and applies policy and
routing. A second B01 offline scenario supplies a forged Credit ref and a
Policy abstention: the AI Credit claim is rejected, Policy abstains, Routing
continues, and none changes the original or opens a candidate.

Focused Week 3/M2.1 tests passed with disposable PostgreSQL and prompt
role-separation checks. Seven **new** isolated PostgreSQL databases with the
pinned Phase 1C source, synthetic fixtures and compiled rules ran the full
backend suite: **259 tests, seven skips, no failures**. This includes
checkpoint reopening without repeated model/tool calls, interrupted Credit
reservation/no replay, adverse evidence and default-deny hosted-object
rejection. The existing earlier **244-test** count below remains a historical
M2.1-only checkpoint. Unrelated Gemma tests are part of local discovery but
their worktree files are not in this increment; private GitHub CI remains
unverified. These scripted outputs do not measure hosted reasoning quality,
latency, costs or correctness against accepted independent answers.

The [separate consolidated hosted proposal](week3-hosted-validation-proposal.md)
is **not authorization** to send anything. Pricing's two terminal second-turn
HTTP 400 attempts remain an [unresolved Week 2 blocker](week2-closure-audit.md).

**27 October 2026; implementation checkpoint, not hosted authorization.**
The [M2.1 module](../backend/dealdesk_phase2/m21_specialists.py) adds three
sequential **offline-only** LangGraph AI investigations *after* one completed
fixed original assessment. There is no Groq or other provider adapter, no
candidate construction, no direct SQL tool and no new rule engine. The
default-deny permission registry permits one named read-only operation per
domain for the exact original deal/customer and pinned context; tool calls
are bounded by the existing shared ledger and its 12-counted-call ceiling.
Each model gets at most two turns and one completed inspection, with a
25-record/16,384-byte evidence ceiling and exact field/type/value validation.
The typed result and checkpoint record model, prompt, source identity,
reserved/returned attempt, ledger reference, execution, abstention/error
reason and validated observations separately from all six fixed findings.

| Responsibility | Selected pinned evidence and safe model contribution | Explicit limit |
| --- | --- | --- |
| Credit & Risk | `inspect_customer_credit_evidence` exposes one same-customer sealed profile, selected as-of AR rows and selected paid-date payment rows; `fixed_commitments_fresh` is copied from the **fixed** Credit payload. Model may cite exact returned scalar fields or abstain. | Wrong customer/future source, duplicate refs or oversized pool fails closed. No exposure/headroom formula, credit-limit change, hold clearance or new freshness threshold. A stale fixed finding is never silently cleared. |
| Policy & Compliance | `inspect_fixed_policy_hits` exposes **only** hit IDs in the fixed Policy result that also match selected active policy-set rule rows; includes fixed hit severity, scoped row area/action and selected rule scope. AI may cite exact returned facts or abstain. | The pinned aggregate has **no per-rule prerequisite API**. Non-hit rules, a claimed global pass/waiver and unsupported prerequisite completion cannot be inferred from this projection. |
| Approval Routing | `inspect_fixed_route` exposes only exact original-subject `route_withheld` and the fixed interface's role-availability flag. If the fixed route is open, only its returned roles verified against selected rule IDs/roles/sequence may appear. | For B01, `route_withheld=true`; `required_roles=[]` is **not evidence of no required human approval**. AI cannot choose roles, unwithhold routing, sign an approval or reconstruct blocked-route roles. |

**Business example (B01, ten stocked units):** The offline double may request
the scoped Credit profile and cite its returned status or dated commitment
reference. It may inspect the one fixed Policy delivery-rule hit and cite
the selected rule ID/action; it may inspect the withheld fixed route and
report only that it is withheld. The fixed Pricing value/credit calculation,
Policy rule application and Approval Routing remain from the pinned Phase 1C
decision. The original still needs revision; no AI observation approves a
deal or creates a candidate. A forged credit reference, wrong customer,
future dated row, missing policy hit rule, cross-domain tool, invented role
or boolean/numeric coercion must fail or produce an AI error without changing
the original fixed results. Justified abstention is separate from success.

**Evidence and limitations:** Unit tests and fresh PostgreSQL integration
cover three independent offline doubles, returned-source matching,
independent Policy/Routing continuation after a Credit AI error, interrupted
attempt restart/no replay and original-only handoff. No live model quality or
actual independent evaluation accuracy is claimed. Candidate-subject M2.1
observations, model prompts/provider wire, selected customer-field redaction
for hosted use, evidence sufficiency on nonempty AR/payment histories, a
per-rule Policy prerequisite interface and withheld-route roles need further
source-first review. **Do not authorize hosted Week 3 inference or an
approval workflow from this offline milestone.**

**Regression gate:** On seven newly isolated PostgreSQL databases with the
exact pinned Phase 1C fixture/rules, `unittest discover` completed **244
tests, seven skips, no failures**. The separate offline Pricing follow-up
shape and four-turn HTTP-400/no-replay tests are included. Private GitHub
Actions status remains **unverified**; this local run is not CI evidence.
