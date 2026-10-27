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
