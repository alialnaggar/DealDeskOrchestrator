# M2.2 six-responsibility integration and evaluation — scope and pretest design

**1 November 2026; planning increment only.** Source: Phase 2 `phase2-agent-implementation`
at `db128809a707ce986b665f182b9c575fe6b31ee8`; Phase 1C runtime pin remains
`90c0bc8e285ee69262c7db826b786096a77ad004`. No hosted send, scored
evaluation, new dataset adoption, runtime code or paid service is authorized
by this document. M2.1 [conditional implementation closure](../evaluation/m21-integrated-credit-exit-gate-2026-10-31.md#m21-completion-review--conditional-development-closure-31-october-2026)
and all its deferred risks remain intact. Draft PR #1 is not merged.

## Original milestone criterion and boundaries

The [master blueprint M2.2 row](master-implementation-blueprint.md#8-remaining-implementation-roadmap-and-gates)
requires reconciliation of all six outcomes with LangGraph, bounded failure/
retry and a reviewable trace; evaluation of sequential latency, whether
parallelism is necessary, and matched baseline comparisons. Its exit evidence
is end-to-end PostgreSQL restart, identity, audit, negative controls, human
review fidelity and an **accepted source-first answer set**. Parallel execution,
a Phase 1C pin upgrade and production deployment are **not** implicit. The
[evaluation tiers](master-implementation-blueprint.md#7-evaluation-and-research-claims)
distinguish mock contracts, disposable-PostgreSQL behavior and independently
reviewed model accuracy. The [M2.1 handoff](../evaluation/m21-integrated-credit-exit-gate-2026-10-31.md#m21-completion-review--conditional-development-closure-31-october-2026)
names the open reliability risks, not new M2.1 requirements. The specific
measures below operationalize these approved gates; they are *proposed
methodology*, not retrospectively applied thresholds or results.

### Runtime inventory and gap classification

All six **fixed** slots are projections of the pinned Phase 1C aggregate
decision (`orchestrator.py`, `fixed_specialists.py`, `graph_state.py`). They are
not six separately authored fixed engines. Original pinned source identity
(`phase1c_adapter.py`, `evidence_bundle.py`), sequential LangGraph checkpoints
(`checkpoint.py`), restricted tools (`tool_permissions.py`, `tool_ledger.py`),
typed model results, attempt receipts (`hybrid_send_reservation.py`) and a
free-tier rate coordinator (`groq_dev_rate.py`) already exist. The original-only
offline composition (`week3_offline.py`) does **not** accept hosted models or
binding proposals; hosted integrated development is separately opt-in and
guarded (`typed_final_hosted.py`, `m21_specialists.py`,
`backend/tests/run_groq_development.py`). Do not substitute either for a
general production workflow or create a second ungoverned sender.

| Specialist in prerequisite order | Current bounded AI and fixed boundary | M2.2 status / remaining limit |
| --- | --- | --- |
| 1. Configuration Validation | `m20_specialists.py`/`typed_final_hosted.py`: original product inspection, exact scalar citations; fixed Configuration precedes dependent work. | **Implemented** on pinned development sources; hosted terminal rejections remain an availability risk. No general AI substitution/compatibility correction. |
| 2. Pricing and Discounting | Scoped original pricing line inspection and typed findings; fixed Phase 1C owns value, discount and margin. | **Implemented** as explanation; no general AI repricing or discount authorization. |
| 3. Availability, Production and Fulfillment | `fulfillment_agent.py`, `investigation_graph.py`, `hybrid_offline.py`: bounded supply/path tools and one binding two-slice proposal or finding/abstention; `candidate_graph.py` calls Phase 1C fixed verifier. | **Partially implemented** against the broader production/conditional/substitute target: binding stocked-finished slice only; historical HTTP 400 unknown. Candidate gets six **fixed**, not six candidate-subject AI, checks. |
| 4. Credit and Risk | `m21_specialists.py` original-only same-customer selected profile/AR/payment and fixed freshness; cited observations distinct from fixed exposure/credit status. | **Implemented** for scoped original; incomplete UC02 hosted finding, not abstention. Empty selected AR is not a complete ledger. No AI credit clearance or candidate-subject Credit. |
| 5. Policy and Compliance | Only selected fixed-hit policy rules and returned rule rows; unresolved prerequisites stay unresolved, Credit blocker does not erase Policy. | **Implemented** for scoped original; per-rule prerequisite declarations absent from pinned reader, so global pass and inferred non-hit rules are **missing by source contract**. |
| 6. Approval Routing and Escalation | Only fixed-returned roles/order and route-withheld fact; Routing follows exact-subject fixed reconciliation. | **Implemented** for scoped original; withheld roles cannot be invented. Fixed candidate Routing reruns; candidate-subject AI Routing and human approval workflow are **not implemented**. |

Cross-cutting **implemented**: immutable original, at most one verified binding
candidate, all six fixed candidate reruns, exact source/subject identity,
reviewer package retaining unmet date and customer acceptance, read-only tools,
strict validation, bounded posts/tool calls, no-unsafe-replay and human-only
approval. **Partial**: unified offline-and-hosted evaluation capture across
all six stages, with paired denominator-safe reports, latency/resource
accounting, case-level reviewer fidelity and statistically interpretable
availability. **Missing**: independently accepted broad reference answers,
released Credit-completeness semantics in the pinned reader, formally matched
baseline study and production readiness. These are M2.2/data dependencies;
do not rebrand them as already working or silently broaden the M2.1 agents.

Example: for B01 ten units with eight available now and two on a binding
later inbound, Fulfillment may suggest an 8+2 schedule. The pinned reader and
fixed verifier decide supported-*unreserved* supply and rerun all six fixed
candidate responsibilities; the original review and candidate comparison stay
separate. AI findings from Credit/Policy/Routing on the **original** cannot
clear the candidate or grant approval. The customer must accept the revised
date and humans must decide. RC01 was a synthetic Groq development
demonstration, not an independently accepted answer or measured model gain.

## Predeclared evaluation protocol — freeze before any trial

1. **Registry and separation.** Record immutable case ID, source cohort
   (`pinned_development`, `phase1c_100_diagnostic`, `phase1c_36_held_out`,
   `supplemental_control`, `fault_injection`), Phase 1C/Phase 2 SHAs,
   source/packet/bundle hashes, run ID, as-of cutoff, policy/catalogue versions,
   case family, original/candidate eligibility, model/prompt/schema versions,
   configured limits and analysis version. Register *all* scheduled cases and
   attempts before viewing model results, including expected skip and stop
   rules. The 100 diagnostic submissions, B01/HC03/UC02 overlays, repeated
   clones and failure injections are **never** independent held-out 36 cases.
   One case repeated with a fresh assessment identity gives additional runtime
   attempts, **not** another distinct source case.
2. **Answer and leakage boundary.** Source-first independent reviewer records
   expected six domain findings, allowable uncertainty/abstention, unacceptable
   claims, candidate constraints, customer action and route on frozen source
   pointers; adjudicate disagreements and version acceptance. Model prompts,
   tools, logs it can read, development fixtures and model selection never
   contain the reviewer answers, drafts, baseline decision or held-out case
   intent. A primary-author draft or fixed output alone is not independent
   ground truth. Freeze cases/answers/metrics before held-out inference;
   tuning on a held-out case moves it to development and requires a new cohort.
3. **Execution tiers.** First run scripted offline doubles, fault injections
   and fresh isolated PostgreSQL on the existing pin. Then independently
   accept case answers and adopt a compatible released Phase 1C version under
   the separate gate below. Only after a reviewed, quota-bounded free-tier
   Groq protocol may a new hosted evaluation tranche run. Older M2.1 hosted
   receipts are retrospective diagnostics only and cannot be pooled with a
   predeclared tranche. No paid API or implicit hosted retry.
4. **Matched baseline.** On each identical frozen case run the pinned fixed
   original and, *only if eligible*, its existing deterministic
   `discover_partial_delivery`/fixed recheck comparator. Apply the same
   candidate feasibility and customer-action rubric. AI copying a baseline
   option is not an incremental discovery. No single-agent advantage claim
   without an independently controlled single-agent comparator.

### Outcome accounting (report per case and by cohort, never only successes)

| Measure | Numerator / denominator and reporting rule |
| --- | --- |
| Coverage and end-to-end completion | Register `scheduled`, `source_preflight_failed`, `ineligible`, `eligible`, `attempted`, `completed`, `abstained`, `skipped`, `error`, `stopped` and `unknown_send` by stage and case. Full six-AI completion / all **started eligible assessments**, plus conditional completion / assessments eligible to reach each stage. An expected prerequisite skip is not a provider failure or a validated contribution. A failure upstream still counts in end-to-end denominator; report six fixed slots separately from six AI stages. |
| Grounding and authorization | Accepted exact returned ref/field/value claims / all parseable submitted claims, and rejected/fabricated or wrong-subject claims / same denominator; report unparseable finals and zero-claim abstentions separately, never as zero-error validated findings. Unauthorized/wrong tool calls / all proposed tool calls; completed tool reads / reserved reads. Report raw rejected errors *and* unsafe claims surviving in the reviewer package. A reference existing elsewhere but not returned is invalid. |
| Fixed rules and candidate support | Fixed-checked candidates / all *proposed* candidates; fixed-rejected, unsupported, unknown and no-proposal as distinct categories. Critical violations of fixed authority or customer constraint surviving to review / all attempted assessments, also list raw model violations rejected before review. Report original and candidate statuses independently, with exact six fixed reruns and exact candidate Routing. |
| Abstention/uncertainty and safety | Validated abstentions / completed reachable specialist finals; categorize model uncertainty, genuine bounded evidence gap, technical error and skipped prerequisite separately. **Appropriateness** of finding versus abstention / independently accepted *eligible labelled* specialist cases only; unknown/incomplete Credit must not imply zero exposure. Unauthorized clearance, waiver, delivery promise or approval reaching review / all attempted assessments, with every case listed; no inferred roles on withheld routing. |
| Accuracy and human review | Per-specialist correct/partially correct/incorrect/not-assessable / accepted independently reviewed **reachable** cases for that specialist; report skipped and failed cases alongside coverage, not silently remove them. End-to-end correct final package, blockers, route, candidate/customer actions / all accepted **scheduled** cases, with failures counted as not completed and separately scored for safe containment. Compare paired fixed baseline on same case, report case-level discordance and reviewer disagreements. **No accuracy fraction until acceptance.** |
| Provider reliability, recovery and resources | Each fresh started send has one terminal category: returned-valid, returned-invalid/semantic, HTTP 400, HTTP 429, other HTTP, timeout/network, local rate stop before send, reserved/uncertain, or other. Report counts / all reserved attempts and / eligible assessments; local pre-send stop is **not** HTTP 400. Checkpoint resume/no duplicate calls and same fixed/subject state / all injected recovery boundaries, with any mismatch listed. Report wall-clock per attempted assessment (including wait), provider and graph/checkpoint times only when recorded, p50/p95 only when sample permits, per-stage and total tokens reported versus missing, configured completion ceilings separately, and observed cost or `unknown` (free-tier nominal charge is not measured cost). Do not impute missing usage, exclude failed latency, or infer population success from small N. |

For each report include the complete registry, denominator and missing-data
counts, case-family clustering, reason for every exclusion, model/fixture/answer
version, observation window, CI/local test status and uncertainty limits.
Predeclare any precision intervals and sample size before interpreting them;
do not manufacture pass-rate targets. Critical surviving safety failure blocks
a safety claim regardless of average completion. A controlled restart is one
attempt with a recovery event, not two independent trials. Preserve only
allowlisted provider diagnostics and private receipt references; no credentials
or raw provider error text in reports.

## Phase 1C dependency and versioned Credit adoption

The Phase 2 pin supports B01/N01 and the exact synthetic RC01/HC03/UC02
source-checked overlays for **engineering** tests; it cannot make broad held-out
Credit completeness claims. On the separate `origin/phase1c-candidate-contract`
draft observed at `239123753435f03221eb38b93adb9a7d45c36348`, the
`phase-1c-data/current-status.md` handoff still says **0/36** independently
accepted original answers, supplemental Configuration 039 **0/1**, Credit
controls 040/041 **0/2**, and `ready_for_generation=false`. Its
`evaluation/credit-evidence-v3/README.md` describes a **provisional** overlay
bound to unchanged v2 packet hashes: per-case fictional complete-zero AR/payment
scope for 36, nonempty overdue/partial-payment 040, explicitly incomplete
041. The existing nonhistorical reader may sum zero selected AR for 041 and
does **not** consume the scope overlay. Source-only/evaluation-only projection
is not a released runtime API; 040/041 cannot be scored as accepted cases.

Adoption sequence, **not executed here**:

1. Phase 1C independently accepts and versions source-first answers and the
   intended Credit semantics, validates 040/041 with clean PostgreSQL reader
   replay and completes its own release gate. Its owner specifies whether a
   trusted, dated, original-customer/run-bound completeness field is in the
   reader/API or an explicitly versioned projection. Empty rows alone never
   imply complete-zero; reject absent, inconsistent, changed, future or
   model-supplied scope rather than falling back to a favorable status.
2. Phase 2 performs a **read-only compatibility audit** of proposed exact
   Phase 1C SHA against the current pin in separate disposable checkouts/DBs:
   reader signatures and selected records, credit scope and as-of semantics,
   sealed-bundle serialization and hashes, tool projections/claim binding,
   all six fixed results, candidate verification, policy/routing visibility,
   checkpoint/replay and reviewer package. Treat a new scope field or bundle
   digest as a new version/assessment, never silently replay an old run or
   make old evidence complete. Record both SHAs, schema and fixture hashes,
   source differences, failing cases and changed expected conclusions.
3. Obtain explicit approval for any Phase 1C pin, data/API, business-rule or
   material infrastructure change; update the pinned adapter, lock/CI and
   fixtures in a separate reviewed increment. Run negative tests for 040
   nonempty, 041 unknown/incomplete, tampered/missing scope, wrong subject,
   stale commitments and originally empty v2 selected pools. Preserve 36
   original inputs/index and separately version supplemental controls and
   the 100 diagnostic exclusion registry. Reopen answer review if source
   meaning changes. No hidden answer may be passed to any model.

Until then: use the old pin for engineering and report Credit unknown where
source completeness is unsupported. Formal 36-case accuracy or comparative
claims wait for compatible accepted answers and an explicitly adopted version.
The 100-case development diagnostics are for distribution/debugging only,
not an evaluation denominator or source of labels.

## Integration tests and ordered work packages

| Order / existing component to reuse | Increment and missing work; tests / acceptance | Dependency |
| --- | --- | --- |
| **WP1 — inventory and offline matrix**: `backend/tests/test_typed_final_hosted.py`, `test_m21_*`, `test_candidate_m17.py`, `test_week3_*`, `week3_offline.py`, development overlay setup | Map existing tests to each stage and failure category; add only *uncovered* end-to-end original/candidate and no-candidate assertions. Include fixed infeasible/unknown, accepted finding/abstention, fabricated/wrong-subject citation, invalid tool args, malformed final, missing Policy prerequisite, withheld/unauthorized route and unsupported candidate overridden by fixed verifier. Assert no approval or customer acceptance. **Done:** traceable coverage matrix, missing cases have failing-then-passing focused tests on fresh isolated PostgreSQL, unchanged pin and full offline regression. | Existing pin; no accepted answers or hosted calls required. |
| **WP2 — paired capture/recovery**: `week3_development.py`, `hybrid_evaluation.py`, checkpoint, receipts, `groq_dev_rate.py` | Identify missing per-stage completion/latency/usage fields and create a **read-only, versioned evaluation projection** (not a new transport) if needed. Fault-inject HTTP 400/429, local quota before send, interrupted reserved sends, restart after final, tampered receipt, changed evidence and cross-subject leakage. **Done:** registry/counts agree with stored identity-bound checkpoints; terminal/uncertain sends are never repeated; output includes stopped cases and missing measurements, no model-visible answers. | WP1; scoped implementation review before changing trusted runtime interfaces. |
| **WP3 — six-specialist evidence-gap reporting (proposed extension)** | [Design a bounded verified-versus-suggested gap contract](../architecture/m22-evidence-gap-and-reassessment-design-2026-11-01.md) for all six, with exact source identity/field when available, unknown/interface-limit handling and human reviewer visibility; no invented Credit completeness, Policy prerequisites or Routing roles. **Required Week 4 deliverable is reviewed design;** working gap projection requires separately agreed typed contract, offline tests and implementation capacity. | Resume/finish WP2 first; source-owner and business-rule review for any expanded field semantics. |
| **WP4 — versioned evidence revision and safe reassessment (proposed extension)** | Design authorized evidence intake, immutable V1/V2 source and assessment lineage, full fresh fixed/AI rerun, old checkpoint/receipt retention, no stale result carryover or V1 uncertain-send replay, customer/human control. **Required Week 4 deliverable is reviewed design;** a working supported-source V2 path is stretch only, not presumed feasible on the pinned reader. | WP2; WP3 gap semantics; separately approved source-ingestion/versioning and security boundary before runtime work. |
| **WP5 — final integration and evaluation readiness (original M2.2 gate remains mandatory)** | Reconcile WP1–4 design/implementation status with PostgreSQL restart, identity/audit, negative controls, human-review fidelity, sequential latency/parallelism decision, same-source fixed baseline and independently accepted source-first answers. Report missing measurements/cases, no post-hoc accuracy. **Do not claim M2.2 complete merely because WP3/4 designs exist.** | WP2 and any implemented WP3/4 changes; Phase 1C release/acceptance and separately gated hosted work where required. |

**Implementation update (WP2, 1 November 2026):** The [WP1 matrix](../evaluation/m22-wp1-offline-integration-coverage-2026-11-01.md) and [WP2 capture audit](../evaluation/m22-wp2-capture-audit-2026-11-01.md) establish read-only checkpoint projection for completed six-stage and terminal/uncertain runs. The projection does not claim that unverified receipts were verified or that aggregate latency and cost were measured. WP2's independent receipt-to-checkpoint reconciliation and full failure taxonomy remain open; finish those bounded offline checks before declaring WP2 closed. The *former* WP3 Phase 1C compatibility track remains separately dependent on a released Phase 1C proposal. The following original planning note is retained as historical scope, not current status.

**Week 4 extension reconciliation (proposed, 1 November 2026):** Ali approved **planning** for six-specialist gap reporting and controlled evidence-revision/reassessment; this is extra scope, **not** an original four-week delivery commitment or a relaxation of M2.2. The earlier table called Phase 1C read-only compatibility “WP3”, answer acceptance/registry “WP4” and bounded hosted analysis “WP5”. The new Week 4 WP3/WP4 labels above refer **only** to gap/reassessment work. Those original three obligations move to explicit **separate dependencies within or preceding WP5**, not out of scope: (i) exact-SHA Phase 1C release compatibility audit and separate pin-approval gate under [Phase 1C dependency](#phase-1c-dependency-and-versioned-credit-adoption); (ii) independently accepted, predeclared source-first reviewer answers, exclusions, blind rubric and matched fixed baseline under [evaluation protocol](#predeclared-evaluation-protocol--freeze-before-any-trial); (iii) separately authorized, quota-bounded hosted tranche if justified, with stopped attempts/latency/usage and safety denominators. Until the first two are available, WP5 may document *readiness and blockers* but cannot declare formal M2.2 accuracy/evaluation complete. Do not run a hosted campaign for this design increment. [Contract and V1/V2 feasibility](../architecture/m22-evidence-gap-and-reassessment-design-2026-11-01.md) are proposals requiring detailed review before any write path. After documentation, **resume WP2** before WP3 runtime work; the prior sentence about WP3 being the Phase 1C compatibility audit is historical terminology, not the new sequence.

**WP2 follow-up status:** [Receipt-bound offline results and remaining registry gap](../evaluation/m22-wp2-capture-audit-2026-11-01.md#wp2-bounded-offline-receipt-follow-up-after-week-4-extension-plan) cover the receipt-bearing six-stage paths and their uncertain/tampered controls. Checkpoint-only capture still reports receipts as `not_checked`; the optional reconciler checks only known, bounded owner directories and labels other transports unavailable. No predeclared scheduled-case registry exists in current state to count preflight failures or prove scheduled/attempted agreement. **WP2 not closed; WP3 runtime deferred.** Finish a model-blind, identity-bound offline registry/recovery denominator review and documented coverage limits before any WP3 implementation.

**WP2 closure update (supersedes earlier open notes):** [Pre-execution scheduled-case registry, exact counts and offline failure audit](../evaluation/m22-wp2-capture-audit-2026-11-01.md#wp2-scheduled-registry-and-closure-review-offline) satisfy the WP2 offline acceptance gate. Manifest freeze and case preflight markers are prospective, not retroactive for earlier M2.1 campaigns. WP2 is closed **for offline engineering only**; provider reliability, full sequential latency and accepted-answer/baseline comparison await separately approved WP5 work. WP3 evidence-gap reporting is the next implementation package, without authorization to silently change source completeness or the Phase 1C pin.

**WP3 implementation update (supersedes design-only proposal status):** [Versioned six-specialist evidence-gap audit](../evaluation/m22-wp3-evidence-gap-coverage-2026-11-01.md) adds an optional, read-only reviewer-package projection from the existing validated checkpoint and pinned fixed results. It separates verified narrow diagnostics, Credit/Policy/Routing interface limits and original-only AI suggestions, and isolates fixed-checked candidates. No historical checkpoint/schema, Phase 1C reader, business rule, source acceptance or reviewer approval authority changed. WP4 new evidence intake/reassessment remains separately gated and unimplemented; WP5 formal evaluation remains open.

**WP4 source/authorization design gate:** [Owner matrix, proposed typed intake and immutable V1→V2 lineage](../architecture/m22-wp4-source-ownership-and-reassessment-gate-2026-11-01.md) show that the pinned adapter has no trusted source writer, durable all-category version, authenticated owner attestation or human role integration. No safe V2 execution/ingress can be implemented under existing approvals. This is an implementation-ready **design and blocker**, not a new acceptance or a retreat from the original M2.2 evaluation gate; require explicit Phase 1C/owner/security decisions before any source writer or reassessment runtime. WP5 evaluation readiness may proceed independently where its other gates allow; no unapproved hosted/paid calls.

**Historical 1 November planning note (superseded by the WP1/WP2 updates above): Immediate next work package: WP1 offline test-coverage inventory**, not a new
hosted run. This first document is the M2.2 scope/evaluation design; it is not
WP1 implementation. M2.2 completion requires the original blueprint gate's
end-to-end identity/restart/audit/negative-control and human review fidelity,
measured sequential latency and matched baseline, plus accepted source-first
answers for a clearly labelled formal cohort. Unavailable accepted answers
keep the **formal-evaluation gate open**, regardless of a good development
demo. The historical Configuration terminal rejections, Fulfillment HTTP 400,
rate/429 interruptions, unobserved hosted UC02 abstention, unmeasured provider
reliability and unknown accuracy remain an explicit risk register throughout;
do not assert their causes or silently waive them.
