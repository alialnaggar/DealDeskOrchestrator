# Phase 2 implementation roadmap — planning baseline

**Status:** Workshop 3 (W3.1–W3.8) closed at architectural-direction level; M1 integration and evidence decisions approved 19 October 2026. M1.0 is implemented; Ali authorized bounded M1.1 original-only LangGraph implementation on 19 October 2026. This roadmap is not evidence of coded AI agents. Follow the [decision log](decision-log.md), [Workshop 1 baseline](../architecture/workshop-1-architecture-baseline.md) and [M1 technical specification](../architecture/m1-contract-and-integration-spec.md).

| Order | Milestone / planning work | Dependency and exit evidence |
| --- | --- | --- |
| 0 | Repository audit | Completed as a read-only planning baseline. Phase 2 branch and draft Phase 1C PR diverge; distinguish verified code from design. |
| 1 | Workshop 1: end-to-end flow, D1 AI contribution, D2 contracts, D3 Orchestrator | Provisionally approved and recorded. LangGraph selected; Configuration first, Fulfillment first AI-intensive; exact interfaces remain open. |
| 2 | Workshop 2: LangGraph run/state and frozen-evidence mechanism | Decide exact typed state, node/edge and subject transitions; compare same-transaction, sealed bundle/reconstruction and persistence options against Phase 1C reader. Specify failure/replay tests. Do not add checkpoint infrastructure by assumption. |
| 3 | Workshop 3: specialist/tool and candidate contracts | Closed at direction level (W3.1–W3.8). Six domain payloads, permission registry, Fulfillment investigation and fixed verification boundary approved; typed mappings remain subject to M1 tests. |
| 4 | Focused M1 Contract and Integration Review | Two pinned checkouts and sealed reader bundle/checkpoint replay approved. [M1 spec](../architecture/m1-contract-and-integration-spec.md) pins Phase 1C at `90c0bc8e285ee69262c7db826b786096a77ad004`; exact adapter, replay, tool and candidate acceptance gates precede implementation. Broader model/evaluation operations can be settled when needed. |
| 5 | Master blueprint sections and independent review | Link authoritative Phase 1B/1C rules, write detailed sections in stages, check contradictions and unresolved assumptions, then publish reviewed plan. A narrow milestone may begin when its own contracts/tests are approved; the entire long blueprint need not be finished first. |
| 6 | M1: narrow LangGraph end-to-end assessment | M1.0 pinned dual-checkout reader/replay is complete. M1.1 original-only LangGraph and PostgreSQL restart were separately authorized; six distinct results map one pinned Phase 1C fixed decision. Later separately approved tasks add bounded AI tools and fixed candidate checks. Mixed 12+8 conditional verification remains a Phase 1C compatibility gate. |
| 7 | Incremental specialist capabilities | Add Configuration correction/substitution, Pricing proposals, Credit evidence analysis, Policy corrective options, Routing explanations and wider Fulfillment modes. Keep separate domains and fixed-rule authority. |
| 8 | General candidate orchestration and evaluation | Prove safe selective reruns by fingerprints and dependencies, consider parallel nodes by measurement, finalize persistence/resumption if needed, and compare with rule-only baseline only after independent expected answers are accepted. |

## M1 prerequisite checklist

- [M1 technical specification](../architecture/m1-contract-and-integration-spec.md) reviewed; first coding task scope separately approved. LangGraph remains selected from M1.
- Dual-checkout setup asserts Phase 1C draft commit `90c0bc8e285ee69262c7db826b786096a77ad004`; narrow adapter maps real deal, reader, compiled rule, candidate and evidence interfaces; no silent PR merge or module copy.
- Stable small development fixture; sealed canonical reader bundle, source/run identity and digest replay demonstrated, with checkpoint size/overhead measured.
- Binding candidate full six-check recheck and no-alternative path tested; conditional 12+8 remains unverified until a compatible Phase 1C fixed verifier is available.
- Configurable candidate/retry/time/tool budgets, failures and stopping tests specified.
- Model-provider access, costs and mock behavior settled before paid calls.
- Separate thesis test environment verified without touching Odoo/n8n.
- No evaluation answer drafts exposed to agents.

## Progress and change control

Record each later milestone with commit/PR, fixture, test and CI evidence, known limitations and one business example. W1–W3 are approved directions; exact contracts and compatibility need M1 acceptance tests. The first coding task is a separate approval gate. Material technology changes follow TG1 in the decision log; no replacement or expansion is accepted silently. Phase 1C data completion can progress in parallel; its draft PR stays separate.

**31 October 2026 provider change:** Ali permanently discontinued Gemma. The Gemma-only development adapter, tests, trial outputs and migration direction are removed; older dated references below are historical test reports, not a future provider gate. Continue Groq free-tier development under its existing guards; the intended OpenAI production option remains separately governed and unfunded. M2.1 Credit reliability is still incomplete: [CR01/CR02/CR03 development report](../evaluation/m21-credit-diverse-development-2026-10-31.md) distinguishes one validated stale-profile observation from failed reconciled-AR and held-profile/transaction model attempts. Do not present either failure as an abstention or a successful six-stage workflow.

**31 October 2026 Credit follow-up:** [Fresh CR01-like and CR03-like Credit-only runs](../evaluation/m21-credit-diverse-development-2026-10-31.md#fresh-credit-only-reliability-follow-up--31-october-2026) now validate exact original-subject AR/payment and On-Hold citations under versioned inspection/terminal instructions and a non-citable opaque invoice match key. The full local fresh-isolated-PostgreSQL regression passes **333/333, 0 failed, 0 skipped**. This does not establish the causes of the earlier failures, model-derived reconciliation, credit clearance, hosted abstention or six-specialist reliability; Fulfillment HTTP 400 remains unresolved. Check CI and independent accepted evaluation answers before broader claims.

**M2.1 integrated exit assessment, 31 October 2026:** [Three source-checked synthetic integrated variants](../evaluation/m21-integrated-credit-exit-gate-2026-10-31.md) passed the complete fresh PostgreSQL regression (**336/336, 0 failed, 0 skipped**) and offline candidate/no-candidate/valid Credit-abstention continuations. Fresh RC01 completed all six hosted stages with a fixed-checked candidate and validated original AR/payment claims; fresh HC03 stopped at Configuration terminal evidence/semantics validation before Credit. Hosted incomplete-evidence abstention remains untested; Fulfillment HTTP 400 is still unresolved. **Recommendation C: keep M2.1 open** pending a justified Configuration diagnostic, fresh held/overdue and incomplete-evidence integrated results, and independent accepted evaluation answers. Prior B01/B05/N01 successes are not rerun counts or formal reliability statistics.

**Configuration diagnostic and integrated follow-up, 31 October 2026:** [Updated exit assessment](../evaluation/m21-integrated-credit-exit-gate-2026-10-31.md#configuration-diagnostic-and-fresh-integrated-follow-up--31-october-2026) records a **338/338** full fresh-database local suite, safe versioned rejection categories without validator changes, a new six-stage HC03 no-candidate hosted completion with validated held/overdue Credit evidence, and a new UC02 Configuration terminal `claim_value_type` stop **before Credit**. The earlier HC03 error remains unexplained; no hosted incomplete-evidence abstention, repeatability or formal accuracy is claimed. Keep **M2.1 open (C)**; stop UC02 hosted attempts until an evidence-based upstream change is offline checked. Historical Fulfillment HTTP 400 remains on the reliability register.

**UC02 Configuration scalar review, 31 October 2026:** [Current contract and hosted-gate finding](../evaluation/m21-integrated-credit-exit-gate-2026-10-31.md#uc02-scalar-only-configuration-contract-review--31-october-2026) identifies the v3 prompt's ambiguous “number” example and returned non-citable JSON objects against an unchanged string/int/bool/null semantic validator. Configuration-only v4 guidance and v3 content-free rejected-type labels pass the **full fresh PostgreSQL suite (338/338, 0 failed, 0 skipped)**. Existing guarded development routes are not Configuration-only; no new hosted send or UC02 replay was made. **M2.1 stays open (C)** until a separately tested bounded Configuration-only diagnostic is available and an appropriately gated fresh UC02 reaches Credit; Fulfillment HTTP 400 and formal accepted-answer evaluation remain independent open items.

## M1.0 implementation checkpoint — 19 October 2026

**Implemented:** [Pinned reader and replay boundary](../backend/README.md) in `phase-2-implementation/backend`, plus [two-checkout CI](../../.github/workflows/phase2-m1-contracts.yml). The Phase 1C source pin is `90c0bc8e285ee69262c7db826b786096a77ad004`; no PR merge/copy or Phase 1C code change. The adapter uses read-only repeatable-read transactions; typed context, canonical reversible bundle, SHA-256 and source rerun validation are in place. [CI run 39244070977](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39244070977) passed eight offline/PostgreSQL tests. Bundle measurements: binding reference 38,717 UTF-8 bytes (59,228-byte PostgreSQL JSONB expression proxy); conditional reference 37,814 UTF-8 bytes. These are **not** LangGraph checkpoint or restart measurements.

**Limitations:** Actual pinned binding fixture is ten units, while the 20-unit 12+8 conditional example remains illustrative and unverified. No LangGraph node/checkpoint storage, Fulfillment tool, access ledger, model, full candidate rerun or VM setup exists yet. Candidate correlation's accepted-path integration and the three sealed-pool tool coverage tests remain next gates. The current Phase 1C role list may be unavailable under a blocked route, and conditional candidate verification remains Phase 1C-owned.

**M1.1 implemented and tested:** Sequential original-only LangGraph,
versioned state holding the M1.0 sealed bundle, Configuration-first result,
six fixed responsibility mappings and explicit prerequisites. Use a separate
disposable PostgreSQL checkpoint database in CI; prove resumption from a
node boundary and measure actual storage. The pinned Phase 1C aggregate
decision is assembled once, not six new rule engines. Model, candidate,
frontend, VM and Phase 1C changes remain outside this milestone.

The [M1.1 PostgreSQL CI
run](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39255592023)
passed 16 tests and proved a cross-process node-boundary resume, safe
technical-failure stop and pinned Python 3.12 environment. The backend
README records measured checkpoint fields and shared table sizes.
Conditional mixed-supply candidates, exact blocked-route approval roles
and rule-by-rule Policy prerequisites remain Phase 1C integration gates.

## M1.2 implementation checkpoint

The bounded, read-only Fulfillment investigation adapter adds three approved
operations over the existing sealed Phase 1C pool, a default-deny six-role
permission registry and an append-only, PostgreSQL-checkpointed access ledger.
The 25-record response, 12-call investigation and 30-day forward horizon are
engineering limits, not business rules. Historical selected provenance remains
visible. A resumed investigation retains spent calls and returned-source
citations. The original graph and Phase 1C pin remain unchanged in function;
no AI or candidate node is added. Record the final passing CI run and fixture
coverage here before describing M1.2 as complete.

**M1.2 verified:** [GitHub Actions run
39267937168](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39267937168)
passed 29 tests, including all 16 existing tests, actual pinned Phase 1C
stock/inbound and offer tool projections, source-detail access, authorization,
line-scoped citations, budget retention and PostgreSQL checkpoint restart.
The mixed 12+8 delivery path is still unsupported by the pinned fixed
interface and is not a verified candidate.

**Next proposed bounded gate:** offline mock Fulfillment contribution over these
three tools, with typed proposal/finding/abstention and explicit eligibility;
keep candidate verification separate and conditional 12+8 unverified until
the Phase 1C fixed interface supports it. Request separate approval first.

## M1.3 implementation checkpoint

Ali separately approved the typed Fulfillment input/output, conditional
post-original LangGraph investigation, offline model double and pinned restart
tests. The original six deterministic findings and PostgreSQL checkpoint stay
authoritative. A private temporary investigation graph runs an eligibility
gate and bounded tool/model turns; each tool call is recorded in M1.2's
original checkpoint ledger. Valid model contributions, abstention and AI
errors occupy a separate original-subject AI result slot. Proposals have no
candidate ID and remain unverified. The pinned binding fixture skips AI; the
offer-only fixture supports a cited finding, not a confirmed 12+8 delivery.
[CI run 39271579933](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39271579933) passed **38 tests** in the disposable PostgreSQL and exact two-checkout environment, preserving the prior 29. Tests cover typed proposal/finding/abstention, citation rejection, malformed output, model/tool failures, exhausted budget, independent Policy blocker, actual pinned binding/offer fixtures and restarted PostgreSQL checkpoint replay of a completed tool call without a second ledger charge. The first run exposed a test fixture's wrong pinned line ID; the follow-up commit corrected it and passed. The offline model double supplies scripted responses; no live LLM inference or candidate verification was measured.

**Next approval gate:** review live-model options, developer/provider cost,
security and repeatability, then choose a provider before adding network
calls. Candidate verification and any Phase 1C conditional verifier are
separate later work; no live model, frontend or VM change is implied by M1.3.

## M1.4 bounded two-provider benchmark — 20 October 2026

Ali approved comparing GroqCloud and Gemini free-tier APIs, without selecting
a permanent provider or enabling paid billing. The [opt-in benchmark protocol](../backend/benchmarks/m1.4-method.md) records model IDs, caps, distinct actual
pinned references versus repeated trials, critical failures, privacy and
measurement limits. Standard-library adapters, checkpointed model-attempt
reservations, fake-provider tests and the explicit runner are implemented in
`backend`. [CI run 39475593959](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39475593959)
passed **45 offline and PostgreSQL tests**, retaining all 38 M1.3 tests.

**Live smoke attempted:** [run 39479573713](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39479573713) and [diagnostic run 39480124609](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39480124609) verified nonempty secret variables and exact Phase 1C pin. The [sanitized results](../backend/benchmarks/m1.4-live-smoke-results.md) show Groq HTTP 403 for both the model list and eligible generation; Gemini model metadata HTTP 200 but eligible generation HTTP 503 twice. No eligible response or paired trial completed; no accuracy, tool-use, token or quality winner can be measured. The original fixed result survived each AI failure. The pinned actual fixtures supply one eligible
conditional-offer case and one binding-supply skip; ten repetitions of the
offer case cannot substitute for independently reviewed diverse cases. Repeat a minimal eligible smoke only after diagnosing access or service recovery; the paired trials remain gated on both successful outputs. No primary provider is selected.
The separate M1.4 workflow runs only from a deliberate
`phase2-m14-live-run` branch push after the owner securely configures both
GitHub Actions secrets and confirms free-tier status through the repository
variable. It never runs from ordinary Phase 2 pushes.

**M1.4 diagnostic follow-up:** [Connectivity evidence](../backend/benchmarks/m1.4-connectivity-diagnostic.md) identified Groq's default-client error 1010 and a working descriptive User-Agent. Gemini generated no successful response; separate structured and tool probes encountered an unsupported schema field, timeouts and HTTP 503. The schema projection was corrected locally and is covered by offline tests, but a live structured result has not been observed. No provider-quality ranking or permanent selection is justified.

**Gated live smoke:** [Run 39486356862](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39486356862) completed one Groq offer investigation with three authorized tools and one accepted citation; Gemini generation succeeded on one retry, but structured and tool probes did not pass, so its eligible smoke was skipped. See [measurements](../backend/benchmarks/m1.4-gated-smoke-results.md). [Offline CI 39486340288](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39486340288) passed 49 tests. Groq is viable as a provisional development provider for this one fixture; neither a permanent provider nor a reasoning-quality winner has been selected.

## M1.5 Fulfillment evaluation and hardening — 20 October 2026

Approved development provider: Groq `openai/gpt-oss-120b`, provisional only; keep Gemini for future comparison without troubleshooting it in M1.5. The [source-first answer sheet](../evaluation/m1.5-answer-sheet.md) separates real pinned references, synthetic offline bundles and fault injection; the [implementation and measured results](../backend/benchmarks/m1.5-results.md) record two bounded, repeated eligible Groq trials and semantic review. Fixed Phase 1C results remain authoritative. The two live outputs had valid tool citations but unqualified absence wording, which fails strict semantic scope review; the revised `m15` prompt and finding citation requirement have offline coverage only. Do not report a diverse-case accuracy score or a permanent provider selection. That M1.5-era approval gate was subsequently satisfied for bounded M1.6 claim validation; the conditional candidate verification dependency remains open.

## M1.6 Fulfillment semantic grounding — 21 October 2026

Ali approved five evidence-scoped claim types, fixed validation, explicit reject/downgrade records and raw-versus-reviewer failure tracking. [Claim contract](../architecture/m1.6-claim-contract.md) specifies the boundary; [measured results](../evaluation/m1.6-results.md) separate pinned real live behavior from synthetic offline faults. [CI run 39494608405](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39494608405) passed **63 tests**, including PostgreSQL restart and rejection-audit persistence. One opt-in [Groq run 39535533200](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39535533200) rejected a broad absence claim, retained it in audit, and rendered only an exact returned source observation; original Phase 1C `needs_evidence` remained. This is containment on one eligible pinned case, not a broad accuracy result or proof of a supportable alternative.

**Next gate:** Ali's separate approval before M1.7 or another specialist. Phase 1C must supply a compatible deterministic conditional-candidate verifier before mixed binding/offer proposals can be accepted as structurally verified. Broader source-first independently reviewed cases are needed to assess semantic performance.

## M1.7 candidate verification and reviewer handoff readiness audit — 21 October 2026

[Readiness audit and proposed implementation gate](../architecture/m1.7-candidate-verification-readiness-audit.md) inspected Phase 2 at `e1b8f920e484adf3e93d3d9bac158aae293af1a9` and the separate Phase 1C checkout pinned at `90c0bc8e285ee69262c7db826b786096a77ad004`. The existing Phase 2 adapter can call the narrow pinned Phase 1C binding partial-delivery verifier, but the original-only LangGraph state has no candidate lifecycle or reviewer handoff. The illustrative 20-unit 12+8 conditional supplier-offer split remains unverified; a binding 8+2 transaction-local test represents a different positive integration path. The proposed binding-only candidate scope, structured AI proposal and reviewer package require Ali's explicit approval before coding. Phase 1C's conditional/mixed-path verifier and blocked-route role extraction remain separately owned dependencies. No M1.7 implementation or Phase 1C pin change is authorized by this audit.

## M1.7 binding-only implementation checkpoint — 21 October 2026

Ali approved Option A from the [readiness audit](../architecture/m1.7-candidate-verification-readiness-audit.md): a versioned AI binding proposal, Phase 1C fixed candidate verification, isolated candidate-subject full six-result mapping, PostgreSQL resume and [typed reviewer handoff methodology](../evaluation/m1.7-binding-candidate-methodology.md). The conditional supplier-offer 12+8 example stays unverified; M1.6 planning ideas remain nonactionable. Record actual passing CI and storage evidence after the bounded implementation runs. No Phase 1C pin or business-rule changes; no live provider trial is implied by routine CI.

**Completed stabilization:** The resumed `finish` transition formerly rescheduled candidate construction, and candidate Approval Routing lacked an edge to the reviewer node. Both graph-control defects were corrected without changing Phase 1C. The [final PostgreSQL CI validation](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39585013020) at `6dba64f2b45624b5775a1e8b33093d62b4f1cc9b` passed all 72 tests, including interrupted candidate restart and reviewer labeling of a nonactionable conditional inquiry; one completed candidate checkpoint JSONB field measured 9,967 bytes. The original Phase 1C finding and deal are preserved; no live AI quality claim follows. The [methodology](../evaluation/m1.7-binding-candidate-methodology.md) records scope, actual measures and limitations. M1.7's binding-only implementation is complete; any next milestone requires separate approval.

## M1.8 candidate evaluation and ground-truth readiness audit — 21 October 2026

The [audit](../evaluation/m1.8-candidate-evaluation-readiness-audit.md) established that M1.7's scripted binding proposal and pinned PostgreSQL verifier demonstrate a narrow integration, not live AI candidate quality. Ali subsequently approved M1.8 evaluation infrastructure. The [protocol](../evaluation/m1.8-evaluation-protocol.md), [case-review sheet](../evaluation/m1.8-case-review-sheet.md), disposable source generator and baseline/capture harness now cover five distinct provisional eligible binding cases and four separately reported safety controls. They use Phase 1C `90c0bc8e285ee69262c7db826b786096a77ad004` in a separate checkout. The [first green PostgreSQL run 39590252565](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39590252565) passed 78 tests without skips, observing five binding two-slice baseline candidates with `supply_supported_unreserved` and aggregate `needs_revision`, and four no-proposal controls. [Subsequent run 39661859652](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39661859652) passed 80 tests including scripted graph capture and candidate interruption/restart stability. These tests are engineering checks, not model accuracy or independent case acceptance.

The [final M1.8 code validation](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39662789074) at `17ebe53e78dd7159d24f885bea47fa1fd4341db2` passed **81 offline/PostgreSQL tests without skips**. Original-versus-candidate capture, baseline equivalence, raw rejection versus reviewer package, source identity and candidate restart/replay are covered. No live candidate quality is measured.

**M1.8 bounded pilot completed 21 October 2026:** Ali accepted all nine [source-first case expectations](../evaluation/m1.8-developer-review-decisions.md) as `developer_supervisor_accepted`, with unchanged pinned source identities; this is not external independent ground truth. The approved [four sequential live Groq trials](../evaluation/m1.8-measured-results.md) used B01 and B05 twice each. All four returned malformed decimal-formatted binding quantities and were rejected before candidate construction; original assessments and human review boundaries held, with no rejected claim surviving in the reviewer package. No live candidate passed the fixed verifier and no realized discovery improvement was demonstrated. A separate exploratory fixed diagnostic found earlier normalized dates structurally supported, but that is not a model success. The [post-pilot PostgreSQL CI 39666810812](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39666810812) passed 83 tests without skips. M1.8 is complete **as a bounded pilot and documented negative result**, not as evidence of general candidate quality. A second independent reviewer would strengthen the thesis answer set. Fixing the live binding output contract and evaluating valid candidates is a recommended next milestone requiring Ali's approval. The conditional 20-unit 12+8 illustration remains outside the binding verifier; no multi-agent superiority is established.

## Cross-branch integration audit — 22 October 2026 (planning only)

The [live Phase 1C/Phase 2 audit](../architecture/cross-branch-integration-audit-2026-10-22.md) compares Phase 1C `c664cd1d08e6969366eaa0c52985dac919e97bbe` with Phase 2 `476d2e71567585e6407561ee10b43597887e77e5` before this documentation update. Phase 2 still pins the separate Phase 1C checkout at `90c0bc8e285ee69262c7db826b786096a77ad004`. Phase 1C's new seven-row deterministic development log does not replace Phase 2 LangGraph orchestration or represent six AI specialists. Its 36 v2 evaluation inputs have zero independently accepted answers; the Phase 2 four-trial live candidate pilot verified no AI candidate.

**M1.9 completed 22 October 2026:** The [contract and output results](../evaluation/m1.9-contract-and-output-results.md) and [compact 16-case comparison](../evaluation/m1.9-compatibility-summary.json) document the approved prompt-only V3 repair, read-only comparison of pinned Phase 1C `90c0bc8e285ee69262c7db826b786096a77ad004` with development snapshot `963d217991afa78c8273386f83a13e7de3b87cc2`, and two bounded free-tier Groq attempts. The final [PostgreSQL CI 39770918068](https://github.com/alialnaggar/DealDeskOrchestrator/actions/runs/39770918068) passed 89 tests without skips. Fixed six-domain values matched on 16 measured originals and two binding candidates, but three reference reader bundles gained an empty field; a pin upgrade requires a new evidence context and separate approval. B01 abstained after an incorrect raw interpretation and B05 emitted correctly formatted yet overcounted 11+18 for 18 units. The fixed verifier rejected B05 and reviewer output remained safe. **Zero of two live M1.9 attempts produced a supported candidate; no discovery improvement is established.** The four earlier M1.8 malformed attempts remain documented.

**Proposed, unapproved next order:** M2.0 narrow Configuration and Pricing AI investigations under authoritative fixed checks; M2.1 separate Credit, Policy and Approval Routing assistance with an end-to-end six-responsibility evaluation. These milestones, a Phase 1C pin upgrade, conditional/substitution/reprice verification and runtime-log write integration each require explicit approval before implementation. The conditional 20-unit 12+8 offer is still not a binding verified candidate.

## Post-M1.9 blueprint and coding-environment handoff — 22 October 2026

Ali discontinued Gemini as an active development provider (TG2). The [Groq-only adapter and backend note](../backend/README.md) remove executable Gemini integration and obsolete paired live workflows; M1.4 measurements remain historical and are not reinterpreted. The [master implementation blueprint](master-implementation-blueprint.md) consolidates six-specialist architecture, actual M1.0–M1.9 implementation, Phase 1C authority, safety, evaluation and proposed remaining milestones. The [Oracle VM/Discord handoff](../development/oracle-vm-discord-handoff.md) is an actionable **plan only**; host packages, authentication, Discord and services are not yet configured or verified by this repository work.

**Next approval sequence:** (1) review the preflight and VM account/GitHub/Discord isolation plan, then authorize any actual setup; (2) separately approve a bounded M2.0 Configuration and Pricing AI contract and implementation, beginning with exact pinned source/tool availability; (3) separately review M2.1 Credit, Policy and Approval Routing. Do not change the Phase 1C pin, invoke its writing runtime, add conditional/substitution/repricing verification, run live Groq trials or deploy infrastructure by implication. Continue routine offline/PostgreSQL CI and retain source-first human evaluation gates.

## Approved post-blueprint sequence — 22 October 2026 (documentation decision, no deployment)

**Step 1 — Documentation completed in this update.** The [master blueprint](master-implementation-blueprint.md) and [decision log](decision-log.md) now record: Groq `openai/gpt-oss-120b` as provisional free development runtime; the **paid OpenAI API** as the future production runtime after development/evaluation and a separately funded/configured integration; provider-independent trusted contracts; permanent Gemini discontinuation with preserved M1.4 evidence; a shared specialist instruction hierarchy; one eligible same-specialist correction attempt within existing budgets; and observed/hypothesized/unknown failure plus reviewer containment measurement. No OpenAI adapter or correction loop is implemented by the documentation.

**Step 2 — Next task: Oracle VM + OpenCode/Codex + Kimaki/Discord setup.** Follow the [existing handoff guide](../development/oracle-vm-discord-handoff.md), beginning with read-only VM checks, isolation from Odoo/n8n and a reviewed setup action. Kimaki runs OpenCode 2 sessions; it does not control the standalone Codex IDE extension. Subscription coding-agent authentication is separate from the paid OpenAI business runtime API. This documentation update does not install, authenticate, deploy or run a bot.

**Step 3 — First coding task in the new environment: bounded Fulfillment correction prototype.** Use M1.8 malformed whole-unit strings and M1.9 B05 overcount as eligible-failure regressions, B01 abstention and forged evidence/identity mismatch as ineligible controls. Preserve original and revised contributions and fixed outcomes, return only safe structured feedback, count one maximum correction in existing model/tool budgets, revalidate from scratch, test PostgreSQL interruption/restart and reviewer containment. No silent normalization or extra live trials. Review exact contract/graph changes before enabling.

**Step 4 — M2.0 Configuration and Pricing AI.** Implement domain-scoped evidence tools and typed reasoning under Phase 1C fixed authority and shared instruction/validation/correction/audit; keep Configuration first and no substitute or repricing commitment without a separate fixed interface and approval.

**Step 5 — M2.1 Credit, Policy and Approval Routing AI**, then six-responsibility end-to-end evaluation and later Next.js reviewer UI, each with its own contracts, accepted source-first cases and separate scope/technology approval. Keep Credit and Policy distinct, unresolved blockers visible and human approval exclusive.

The Phase 1C production pin remains exactly `90c0bc8e285ee69262c7db826b786096a77ad004`; its draft PR #1, rules and writing development runtime are outside this work. An approved sequence is not permission to change the VM, make paid OpenAI API calls, write agent code or begin M2.0 in this documentation task.

## M2.0 stopped Pricing investigation and first M2.1 offline slice — 27 October 2026

**28 October 2026 unresolved Week 2 gate (deferred while implementing Week 3):**
Two distinct, permanently stopped [first B01](../evaluation/m20-configuration-pricing-hosted-result.md)
and [second-account B01](../evaluation/week2-secondary-b01-hosted-result.md)
hosted assessments completed Configuration but received HTTP 400 on Pricing's
second turn. The [offline byte-level wire diagnosis](../evaluation/m20-pricing-http400-offline-diagnosis.md)
matched serialized request sizes/hashes and call/result linkage; it did not
establish a cause or justify a speculative adapter change. **Week 2 is not
closed.** Pricing still needs a separately authorized, source-first hosted
validation under a *new* assessment identity; neither terminal request may
be replayed. Week 3 offline work does not substitute for that gate.

**28 October 2026 Week 3 offline increment:** The
[M2.1 methodology update](../evaluation/m21-credit-policy-routing-offline-methodology.md#28-october-week-3-integration-update--offline-only)
documents versioned trusted Credit/Policy/Routing instructions and a
LangGraph original-only composition of the existing Fulfillment, M2.0 and
M2.1 investigations. Six fixed responsibilities and six separate AI
investigation results are integrated offline, not hosted. A fresh seven-DB
PostgreSQL run passed 259 tests (seven skips). The
[consolidated hosted proposal](../evaluation/week3-hosted-validation-proposal.md)
is not authorization; a hosted adapter, customer-field redaction review,
source-verified cases, human approval and the separate Pricing gate remain.

**Later Week 3 hosted preparation, no sends:** The
[readiness and seven-skip audit](../evaluation/week3-hosted-preparation-audit.md)
records a provider-independent synthetic-only redacted view and dormant Groq
native-tool contract, plus a fresh 263-test local PostgreSQL run (seven
unrelated Gemma checkpoint skips). The
[non-executable proposed manifest](../evaluation/week3-hosted-validation-proposal.json)
has B01/B05/N03 source identities and explicit secondary-key selection;
**not ready to send** until a durable exclusive hosted M2.1 gate, budgeted
attempt tracking, hosted error/no-replay tests, CI and explicit Ali approval.

**Subsequent Week 3 offline hosted-gate increment:** The
[gated runner and source-first audit](../evaluation/week3-hosted-preparation-audit.md#later-28-october-gated-execution-increment--still-no-provider-call)
now use one-case manifests, the existing exclusive send owner/receipt and
shared Groq transport. A final post-review fresh seven-DB run passed 270 tests with seven
unrelated historical Gemma skips. The updated
[single-B01 proposal](../evaluation/week3-hosted-validation-proposal.json)
has a **six-POST total**, remains `proposal_not_authorized_not_executable`,
and needs new-status hash approval, account/cost confirmation and CI before
any hosted call. Pinned conflict cases separately verify an AR/credit blocker
and visible two-role route; the hard-block duplicate-hit projection and
payment coverage gaps remain. Week 2 Pricing is still unresolved.

The [Week 2 closure matrix](../evaluation/week2-closure-audit.md) distinguishes
completed offline behavior from the unresolved hosted Pricing acceptance and
broader Phase 2 integration. An [offline iterative Fulfillment prompt-hierarchy
cleanup](../evaluation/week2-fulfillment-iterative-prompt-cleanup.md) moves
trusted instructions into the system role without changing the approved
business/tool contracts. The fresh B01 [hosted proposal](../evaluation/week2-closure-hosted-proposal.md)
remains **unauthorized**: no new inference is implied by this roadmap entry.

Ali approved one fresh B01 Configuration/Pricing Groq assessment at
`9e70046`. The [sanitized result](../evaluation/m20-configuration-pricing-hosted-result.md)
records Configuration's one authorized inspection and five exact observations;
Pricing inspected its authorized line but Groq returned HTTP 400 on the
paired second turn, and the assessment stopped without replay. The
[offline wire diagnosis](../evaluation/m20-pricing-http400-offline-diagnosis.md)
reconstructed both reserved second-turn request hashes, native call-ID
pairing, schemas and limits; **no precise provider rejection cause is known**.
No transport fix or new hosted attempt is justified without more evidence.

The [M2.1 original-only offline method](../evaluation/m21-credit-policy-routing-offline-methodology.md)
implements scoped Credit, Policy and Approval Routing evidence investigations
and deterministic-result isolation with scripted doubles and PostgreSQL
restart. Credit/Policy/Route are separate AI results, not another fixed rule
engine. Only fixed-hit Policy rules and fixed-returned Routing roles can be
cited; withheld roles and rule-by-rule prerequisites are unavailable. No
candidate-subject or hosted M2.1 execution is enabled. Continue with a
source-reviewed nonempty AR/payment fixture, rule/prerequisite and role
visibility boundaries, typed candidate isolation, then integrated six-agent
offline cases before considering any hosted Week 3 proposal. Private CI
status must be reported as unverified unless actually observed.

Fresh local Phase 1C-pinned PostgreSQL regression for this increment passed
**244 tests (seven skips)** across seven isolated databases. This is not a
measured multi-specialist accuracy result; GitHub Actions status is unverified.

## Current short path from typed-final preparation (29 October 2026)

The [offline activation/trial preparation](../architecture/typed-final-offline-trial-preparation.md)
and [readiness decision sheet](../architecture/pricing-credit-typed-final-hosted-readiness-audit.md#final-owner-decision-sheet-29-october-2026)
supersede older *pre-remediation* gate advice above; historical stopped cases
remain spent. The typed-final Pricing/Credit gate is dormant. Offline templates
are invalid as authorizations; no new inference follows from their existence.

1. **Owner gate, not new speculative implementation:** confirm actual free-tier
   account/key/billing-disabled status, deployment privilege boundary and
   current provider wire documentation. Decide explicitly whether to accept
   local-only regression without private CI for **one** synthetic trial. Then
   review the separate minimal activation diff; no automatic activation.
2. **Only after distinct approvals:** owner provisions a fresh pinned B05
   case with independently evidenced DB creation, identity and exclusivity;
   review the exact manifest hash and separately authorize at most four POSTs
   / 2,560 configured completion tokens. Stop at the first uncertain send;
   no retry/fallback. Credit's proposal is **unscheduled** and requires its
   own fresh case and later authorization. Hosted compatibility and quality
   remain unproven until measured.
3. **Keep the thesis moving offline meanwhile:** close the source-first
   Credit/Policy/Routing visibility and payment/AR fixture gaps; integrate all
   six distinct AI observations with the existing six deterministic checks
   and human-only Approval Routing; test original and candidate isolation,
   prerequisite skips, disagreements, bounded alternatives, reruns and
   PostgreSQL restart. Prepare independent accepted evaluation cases and
   compare to deterministic-only baselines before any accuracy claim. The
   Phase 1C pin, supplier-offer constraints and human approval boundary stay
   unchanged. Evaluate the reviewer UI only after the six-agent backend is
   coherently exercised. Further architecture, cost or hosted scope changes
   need separate owner approval.

## Weeks 1–4 evidence checkpoint — six-specialist offline development (29 October 2026)

| Plan period | Verified working boundary | Still open |
| --- | --- | --- |
| Week 1, pinned foundation | Exact Phase 1C `90c0bc8e285ee69262c7db826b786096a77ad004` reader, sealed context, six **deterministic mappings of one** fixed decision, original PostgreSQL LangGraph/checkpoint and restart. | Broader Phase 1C release/calibration and a pin upgrade are separate decisions. |
| Week 2, bounded agents | Permissioned Fulfillment AI investigation, scripted proposal/abstention, and a separate candidate path that fully rechecks six **fixed** responsibilities. Configuration and Pricing have independent scoped offline AI investigations; hosted Pricing remains stopped by prior 400s. | Typed-final hosted acceptance, substitution/repricing and combined six-AI candidate continuation are not demonstrated. Never replay a spent hosted attempt. |
| Week 3, specialist integration | The existing `week3_offline.py` LangGraph composes original/Fulfillment → Configuration/Pricing → Credit/Policy/Routing → original-only reviewer handoff. Five bounded evidence-reading offline AI specialists plus Fulfillment retain separate results and preserve fixed authority. | Credit/Policy/Route source coverage (nonempty AR/payment roles), candidate-subject AI isolation and all-specialist hosted operation remain incomplete. |
| Week 4, evaluation | New [three-case development baseline](../evaluation/week3-six-specialist-development.md) and [machine-readable trace](../evaluation/week3-six-specialist-development.json) exercise B01 nominal, B05 fabricated Credit/Policy abstention, N03 insufficient evidence. Distinct disposable DB reruns yield byte-identical observations; 0 accepted independent answers, no provider requests. | The pinned 36 provisional packets have **0/36 accepted** answers. Independent evaluation/scoring, comparative controlled cases, real-model reliability and reviewer UI are not complete. |

**Next minimal offline increment:** extend source-first nonempty Credit/Policy/
Routing cases and original/candidate-subject isolation tests without changing
Phase 1C rules; secure independent answer acceptance before quality scoring.
Then seek separately scoped hosted validation (if still needed) and UI review.
The Week 3 development runner demonstrates orchestration and safety boundaries
with scripted actions, **not** AI model quality or a finished Week 4 thesis.
Fresh disposable PostgreSQL verification for this increment: **14 focused
tests passed** and **320 full-suite tests passed, seven unrelated Gemma skips**
(`/tmp/opencode/dealdesk-six-specialist-focused.log` and
`/tmp/opencode/dealdesk-six-specialist-regression.log`). Private GitHub CI
was not run.

## Week 4 follow-on — reproducible broader offline cohort (29 October 2026)

[Week 4 development runner](../backend/tests/run_week4_development.py) and
[fresh-disposable one-command setup](../backend/tests/run_week4_disposable.py)
exercise all nine Phase 2 M1.8 synthetic source cases B01–B05/N01–N04, not
the provisional 36-answer set. The [sample JSON](../evaluation/week4-offline-development.json)
and [report](../evaluation/week4-offline-development.md) keep 54 original
fixed mappings apart from 54 offline AI execution slots (scripted, not measured
model reasoning); five source-derived fixed binding splits, four no-split
controls, failure/abstention/skips and a separately checkpointed B01 scripted
binding proposal with six fixed candidate rechecks. Original assessment and
candidate share the exact pinned evidence identity but never share a checkpoint
thread. Candidate fixed supply is supported **unreserved**, the aggregate
remains `needs_revision` and customer acceptance is pending; its schedule
matches deterministic-only discovery, so no added AI value is established.
Structural metrics, tool/model ledger transitions and optional wall-clock
diagnostics make no semantic accuracy claim. Two independent fresh cohorts
produced the same stable structural SHA-256; timing and unique database names
are deliberately excluded from that digest. This does **not** change the
pinned handoff's **0/36 accepted** answers; hosted inference remains disabled.
Fresh seven-DB full regression: 325 tests passed with seven unrelated Gemma
skips (`/tmp/opencode/dealdesk-week4-regression.log`); private CI not run.
Remaining Week 4: broader source families and nonempty Credit/Policy/Route
evidence, source-first independent answer acceptance, semantic/blinded human
comparison, and separately authorized hosted validation if pursued.

## Offline release-candidate operator handoff (29 October 2026)

The existing [fresh-disposable Week 4 command](../backend/tests/run_week4_disposable.py)
now emits a verified, read-only [operator demonstration](../evaluation/dealdesk-offline-demo.md)
and [structured projection](../evaluation/dealdesk-offline-demo.json) beside its
evaluation files, with one B01 complete original LangGraph handoff, B05/N03
fault/skip controls and the separate B01 fixed-checked binding candidate.
The [acceptance checklist and Oracle command](../evaluation/offline-release-candidate-acceptance.md)
are the offline release-candidate entrypoint; no new business or agent runtime
capability was added. Graph reviewer identity, six fixed mappings, AI evidence
and human-only action are checked before projection. Offline doubles and
deterministic-only discovery remain separately attributable. The structural
evaluation digest was reproduced in a new isolated PostgreSQL cohort after
generating the sample artifacts. Remaining Week 1–4 work is unchanged:
independent answers (0/36), richer source families, real-model and hosted
compatibility under **separate approval**, and eventual reviewer UI.

## First authorized typed-final B05 Pricing trial — stopped (29 October 2026)

The owner separately approved the exact one-line activation and one-case
manifest/budget. A single restricted, Phase 1C-pinned B05 invocation sent
**two Configuration prerequisite POSTs**, both with returned receipts, for
**1,024 configured completion tokens**. The first completed one allowed
product inspection; the second response was rejected as invalid model/tool
output before checkpointing a returned action. No Pricing inspection or
typed-schema final was sent, so [this trial result](../evaluation/pricing-b05-typed-final-first-authorized-result.md)
**does not establish** that the typed-final approach fixes the previous
`tool_use_failed` HTTP 400. The second send's receipt returned successfully,
but its unparsed checkpoint reservation is terminal and must never be replayed.
Fixed review stayed `needs_revision`; the gate was immediately restored to
`HOSTED_ACTIVATION=False`, with private receipts retained. Eight focused
offline tests passed after rollback; private CI remains unverified under the
owner's one-case exception. Next: source-bound offline diagnosis of the
Configuration second-turn wire/response category; any new hosted case needs
fresh identity, budget and separate authorization. No broader hosted
success or measured model-quality claim follows from this single stop.
