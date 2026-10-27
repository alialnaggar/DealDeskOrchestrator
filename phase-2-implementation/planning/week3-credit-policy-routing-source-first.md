# Week 3 source-first contract preparation — no agent implementation

**27 October 2026; planning only.** The current hosted-validation milestone
remains the priority. Credit, Policy and Approval Routing are **three separate
fixed responsibility mappings**, not yet three AI agents or callable Phase 1C
engines. [Fixed mapping](../backend/dealdesk_phase2/fixed_specialists.py)
derives them from one pinned Phase 1C aggregate decision; no new thresholds,
exposure formula, exception or approval authority is proposed here.

| Responsibility | Actual pinned interface/observation | Next scoped AI contract to design, not run |
| --- | --- | --- |
| Credit & Risk | The fixed Credit mapping needs Pricing to have completed; B05 returns `commitments_fresh=true`, EUR 16,200.00 exposure, zero over-limit percentage and no rule hits. There is no independent permissioned Credit inspection tool. | Separate input with exact customer/run/as-of/source identity, bounded read-only selected credit/AR evidence, typed evidence-gap/observation claims; fixed service alone recalculates exposure/limit. Test stale, missing, over-limit and wrong-customer facts before granting any tool. No credit-limit change. |
| Policy & Compliance | B05 returns no hard block and a `PO-BASE-DELIVERY-LATE` `approval_required` rule hit for its original line. Phase 1C does **not** expose a per-rule prerequisite API; independent Policy mappings stay visible if Configuration fails. | Cite only selected applicable rules and fixed hit IDs/scope; abstain when prerequisites cannot be determined rather than infer a pass or waiver. Test hard block, unknown, independent Credit blocker and mismatched rule IDs. No policy mutation. |
| Approval Routing | B05 and N03 both have withheld routing: `required_roles=[]` and `roles_available_from_fixed_interface=false`. These empty roles **do not prove nobody needs to review**. Routing follows exact fully checked original/candidate after all required findings. | AI may explain only fixed returned roles and unresolved blockers; it cannot add reviewers, infer missing blocked-route roles, remove a required role or grant approval. Gate on exact subject/candidate digest and withheld status; test conditional, policy block and candidate recheck before any hosted trial. |

**Evidence to inspect before design approval:** pinned Phase 1C reader fields,
dated commitment/AR inputs and freshness; selected applicable policy/approval
rule rows with scope and severity; Phase 1C `decision["specialists"]` output
and six-result mapping; whether blocked-route roles can be obtained without
inventing them. Use a fresh, isolated PostgreSQL fixture and source-first
expected behavior kept out of agent inputs. Compare a suitable over-limit,
hard-block and approval-required reference/development case after checking
its actual pinned source identity. Do not port incomplete Phase 1C drafts,
infer new business thresholds or open hosted Week 3 sends under the M2.0
authorization. A separate typed-contract review, offline adverse tests and
owner authorization follow the bounded three-specialist hosted validation.

## Next design slice after M2.0: proposed contracts, not tool grants

The pinned reader at `90c0bc8e285ee69262c7db826b786096a77ad004`
selects a same-customer `customer_credit_profiles` row, most recent eligible
`accounts_receivable` per invoice, and dated `payment_history` events for
synthetic runs. Historical runs require a separate frozen credit/AR manifest;
mixing a current customer row into a past run is forbidden. It also selects
active pricing/policy/approval rules by **the run's applied policy set**.
Phase 2's existing permission map assigns **no named tools** to Credit,
Policy or Routing. The following are interface candidates for a later typed
contract review, not permissions to query arbitrary tables or execute them:

| Agent input and proposed scoped read | Sufficient evidence before a model claim | Fixed handoff, dependencies and adverse fixtures |
| --- | --- | --- |
| **Credit & Risk:** versioned original/candidate subject, customer and run IDs, as-of/snapshot/source fingerprints, verified Pricing value, fixed Credit hit IDs; candidate `inspect_customer_credit_evidence(customer_id)` may return only the sealed profile (`credit_limit`, `unbilled_committed_amount`, `commitments_as_of_at`, `commitment_evidence_ref`, review dates/status) and the selected same-customer AR/payment rows with dated refs. | Exact customer match, manifest/source identity and as-of ordering, nonmissing commitment evidence and fixed freshness disposition. A missing/stale profile, uncertain payment matching or wrong-customer ref yields evidence gap/abstention, **not** a computed clearance. The model may cite returned facts, never calculate exposure or change a limit. | Pricing must complete before Credit. Existing fixed Credit mapping owns exposure, over-limit percentage, `rule_hits` and freshness. Recheck Credit on an exact checked changed-price candidate, then dependent Policy/Routing. Test stale/absent credit, stale AR, wrong customer, unknown credit and a fixed blocker without creating a new threshold. |
| **Policy & Compliance:** same frozen subject plus exact fixed Credit/Fulfillment/Pricing findings, policy-set code and fixed policy hit IDs/scope. Candidate `inspect_applicable_policy_rules(rule_ids)` may return only selected active pinned rule rows (severity, required action, condition, scope) and exact matching fixed hit metadata. | Rule ID and policy-set match, correct line/whole-deal scope, required prerequisite results available. The aggregate Phase 1C decision **does not expose a per-rule prerequisite API**, so the agent must not infer that every rule passed or turn a missing hit into a waiver. Record unknown prerequisites and escalate. | Remains separate from Credit: one favorable result cannot erase the other's blocker. Fixed rule engine owns applicability, hard blocks and exception-required status. Test a hard blocker, delivery approval hit, missing rule, wrong policy set and unavailable Credit prerequisite; never grant an exception. |
| **Approval Routing:** exact fully checked original or candidate ID/input digest, all five prior fixed results, fixed route-withheld flag and fixed returned roles. Candidate `inspect_fixed_route(subject_digest)` may expose only the sealed fixed route and selected active approval-rule IDs **when the fixed interface supplies them**. | All required specialist results for that exact subject complete and reconciled; if `route_withheld=true`, empty `required_roles` is **not** a role-free approval. No inferred role, sequence, signed approval or blocked-route reconstruction from rule rows. | Routing is last and recomputed for the exact checked candidate. Fixed Phase 1C chooses roles and order; AI may only explain verified roles/blockers. Test withheld original B01/B05, over-limit/Policy blocker, switched candidate digest and missing predecessor. A genuinely populated fixed role route needs a separately source-reviewed fixture before hosted evaluation. |

Proposed typed outputs are small: `execution` (`completed`, `abstained`,
`skipped`, `error`); subject/run/fingerprint/model/prompt identity; bounded
`{ref, field, exact_value}` observations; `rule_id` only if an applicable
fixed hit and selected rule are both present; missing-evidence/uncertainty
codes; and a **separate** immutable fixed result. Candidate alternatives
for credit limits, policy waivers or approval roles are not in scope. Before
coding, review each projection and tool budget against selected pinned rows
and agree on safe redaction of customer/receivable fields; implement with
mocked models and fresh PostgreSQL fixtures first. The current M2.0 B01
hosted campaign cannot authorize Week 3 tools or inference.
