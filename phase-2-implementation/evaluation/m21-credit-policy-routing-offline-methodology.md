# M2.1 original-only Credit, Policy and Routing — offline method and limits

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
