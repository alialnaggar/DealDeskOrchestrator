# Week 2 closure audit — 27 October 2026

**Verdict: PARTIAL, not complete.** There is no single separately named
"Week 2 definition of done" in the roadmap: this audit interprets Week 2 as
the approved correction → M2.0 Configuration/Pricing sequence and the
blueprint's shared instruction/integration gates. This is an evidence audit of the
`phase2-agent-implementation` branch, not an authorization for a new hosted
run. The [roadmap](../planning/implementation-roadmap.md),
[blueprint](../planning/master-implementation-blueprint.md#3-specialist-responsibilities-and-dependencies),
and [P2-INSTR/P2-CORR decisions](../planning/decision-log.md#p2-instr--shared-specialist-instruction-hierarchy-22-october-2026)
describe the intended Week 2 sequence. Later proposals in those documents
are not evidence of implemented, validated production capabilities. This
matrix treats a fixed Phase 1C result and an AI specialist as different
things. **Pass** means the scoped offline implementation is demonstrated;
**partial** means a specifically required acceptance gate or integration is
not demonstrated; **missing** means the capability itself does not exist.

| Week 2 criterion | Status | Evidence and exact remaining gap |
| --- | --- | --- |
| Preserve Phase 1C authority, Configuration first, Pricing dependent, original unchanged | **Pass (offline)** | [M2.0 LangGraph/typed results](../backend/dealdesk_phase2/m20_specialists.py), [original-only/failure tests](../backend/tests/test_m20_specialists.py), [fixed source mapping](../backend/dealdesk_phase2/fixed_specialists.py). No M2.0 substitute, repricing or candidate modification. |
| Configuration evidence reasoning with scoped reads and grounded citations | **Pass (narrow)** | [M2.0 tool projection and exact claims](../backend/dealdesk_phase2/m20_specialists.py), [permission registry](../backend/dealdesk_phase2/tool_permissions.py), [mock wire tests](../backend/tests/test_m20_groq.py); [B01 hosted result](m20-configuration-pricing-hosted-result.md#evidence-authority-and-outcome-by-specialist) reports five exact returned observations. Sellability is not a full configuration approval. |
| Pricing evidence reasoning and fixed margin authority | **Partial** | Same M2.0 typed/tool/claim tests and mocked successful two-turn sequence, but [B01 Pricing follow-up](m20-configuration-pricing-hosted-result.md#real-hosted-attempts-groq-openaigpt-oss-120b) failed HTTP 400: no validated **live** Pricing finding. [Offline diagnosis](m20-pricing-http400-offline-diagnosis.md) cannot classify cause. No speculative adapter repair. |
| Trusted domain-specific instructions, data/authority hierarchy, versioned prompts and tools | **Partial** | [M2.0 trusted Configuration/Pricing system instruction](../backend/dealdesk_phase2/m20_groq.py) is now domain-specific and versioned separately from its wire/contract; [prompt isolation and version tests](../backend/tests/test_m20_groq.py) are offline. However, the older [iterative Fulfillment decision/final/correction wire](../backend/dealdesk_phase2/live_models.py) places its detailed `_prompt` guidance in user text, not the approved trusted system layer; [hybrid Fulfillment wire](../backend/dealdesk_phase2/hybrid_provider.py) has trusted system instructions but not one common six-specialist template. Do not silently alter previously validated hosted wire semantics. |
| Bounded Fulfillment correction, original rejection preservation, same model, fixed recheck and safe feedback | **Pass (offline only)** | [classifier and safe feedback](../backend/dealdesk_phase2/fulfillment_correction.py), [hybrid continuation](../backend/dealdesk_phase2/hybrid_offline.py), [candidate audit](../backend/dealdesk_phase2/candidate_graph.py), [classifier tests](../backend/tests/test_fulfillment_correction.py), [offline M2.0 B05 overcount → 11+7 example](m20-configuration-pricing-offline-methodology.md#business-example-and-week-1-gate). Hosted [hybrid revision is explicitly disabled](../backend/dealdesk_phase2/hybrid_provider.py); no measured live correction improvement. |
| Correction of Configuration/Pricing proposals | **Not in this narrow slice** | [M2.0 contract](m20-configuration-pricing-offline-methodology.md) permits only original-subject inspections, exact findings and abstentions; it creates **no** Configuration substitute or Pricing reprice proposal. The [approved P2-CORR policy](../planning/decision-log.md) applies to eligible rejected proposals, not arbitrary wrong/unsupported observations. Adding proposal/correction paths requires source-compatible fixed verification and separate design review; it is not an offline bug fix. |
| Fulfillment integration alongside M2.0 specialists | **Partial** | [M2.0 offline method](m20-configuration-pricing-offline-methodology.md) exercises an existing corrected Fulfillment candidate and the separate Configuration/Pricing continuation with fixed checks. M2.0 is **post-original/original-only**, not a single hosted six-specialist graph or candidate-subject M2.0 investigation. [Blueprint](../planning/master-implementation-blueprint.md) keeps broader candidate/specialist integration incremental. |
| Failure containment, stop/restart, tool and model budgets, human-only routing | **Pass (offline)** | [M2.0 hosted gate and reservation](../backend/dealdesk_phase2/m20_specialists.py), [paired-wire HTTP-400/no-replay tests](../backend/tests/test_m20_groq.py), [stopped B01 review](m20-configuration-pricing-hosted-result.md#containment-and-next-gate). B01 original remains `needs_revision`, candidate `not_started`, routing withheld. |
| Independent accuracy, end-to-end live Configuration **and** Pricing acceptance | **Missing** | Only Configuration has a successful hosted observation; Pricing has no successful live finding. No accepted independent answer set, comparative accuracy result or six-agent hosted run exists. A fresh separately authorized bounded trial is needed to close **live Pricing completion**, but one successful synthetic trial would still not prove accuracy or production readiness. See [proposal](week2-closure-hosted-proposal.md). |
| Latest full regression and CI | **Partial** | Fresh local PostgreSQL full discovery completed **245 tests, seven skips, no failures** on seven new isolated databases with pinned Phase 1C source and compiled fixture rules. This discovery includes preserved untracked Gemma tests, which are **not** staged for this change. GitHub Actions for this increment remains unverified; historical CI links cannot substitute for it. |

## Actual runtime prompt inventory

| Model-facing path and execution | Construction, version and controls | Tested boundary / outstanding gap |
| --- | --- | --- |
| [Fulfillment hybrid](../backend/dealdesk_phase2/hybrid_provider.py) `OfflineGroqWireDouble.decision_request` / `final_request`; opt-in [Groq transport](../backend/dealdesk_phase2/hybrid_provider.py) | System role contains `WIRE_VERSION=hybrid-groq-wire-v1`; decision includes authorized function selection, returned-only evidence, supplier-offer warning and binding-path prerequisite; final system requires structured JSON, canonical units, no approvals or delivery promises. User role contains structured input, returned observations, intent and optional bounded correction feedback. Hosted revision intent/final are disabled. | [Hybrid wire tests](../backend/tests/test_hybrid_provider.py), [offline continuation tests](../backend/tests/test_hybrid_offline.py); wire version is not a shared six-specialist prompt-template version. |
| [Fulfillment iterative](../backend/dealdesk_phase2/live_models.py) `_prompt`, `LiveInvestigationModel.next_action` / `revise`; opt-in [runner](../backend/dealdesk_phase2/live_m18.py) | `_prompt` uses `PROMPT_VERSION=m16-fulfillment-claims-v1`, optionally a binding suffix. It instructs evidence-only citations, conditional supplier limitations, binding quantities/dates, findings/abstention and fixed verification. Detailed guidance is placed in **user** text; system messages are short tool/JSON/revision directives. Correction user text includes rejected output and safe feedback. | [Prompt and mapping tests](../backend/tests/test_live_models.py), [evaluation prompt tests](../backend/tests/test_evaluation_m15.py), [correction tests](../backend/tests/test_fulfillment_correction.py). Approved hierarchy not fully implemented here; changing it changes historic live wire and needs isolated review/validation. |
| [Configuration + Pricing](../backend/dealdesk_phase2/m20_groq.py) `system_instruction` / `request_body`; separately gated [continuation](../backend/dealdesk_phase2/m20_specialists.py) | Common non-overridable system constraints plus distinct domain sections, `PROMPT_VERSION=m20-config-pricing-system-v2`, wire `m20-groq-native-tools-v1`, contract `m20-ai-investigation-v1`; line/run input and returned observations stay in user/tool roles. Each uses only its named `inspect_*_line`, `submit_finding` with exact JSON-serialized values, or `abstain` (`insufficient_evidence`, `model_uncertainty`, `unsupported_capability`). Fixed checks, not AI, own validity/margin/approval. | [System isolation, schema, serialization, attempt-version and no-replay tests](../backend/tests/test_m20_groq.py), [claim/permission tests](../backend/tests/test_m20_specialists.py). New version is **not** the B01 deployed prompt, which was the older generic instruction. Fresh hosted use requires new approval. |
| [Credit, Policy, Routing offline doubles](../backend/dealdesk_phase2/m21_specialists.py) | Typed input and `prompt_version=m21-original-evidence-v1` tag plus three scoped reads and exact returned scalar claims; **no actual model-facing system message or hosted adapter exists**. | [Offline tests](../backend/tests/test_m21_specialists.py). Do not call this a runtime system prompt or a Week 2 live validation. |

## Gemma disposition

There are **no tracked Gemma Python modules, tests, imports or Gemma CI steps**
in the active backend/workflows; tracked runtime paths use the opt-in Groq
adapters or offline doubles. The Gemma modules, tests and provider notes in
the current working tree are **untracked**, and two tracked documents have
uncommitted Gemma edits. These are other work and remain untouched. The
[Gemma decision/history](../planning/decision-log.md#p2-gemma--development-only-gemma-4-exception-24-october-2026)
records one bounded failed development trial, not an active default; the
[historical result](gemma4-bounded-live-validation.md) is useful evidence.
**Recommendation:** Retain committed decision history and sanitized results;
after Ali explicitly confirms the untracked experiment is obsolete and no
other session is using it, inventory each file and agree a deletion or
archival commit removing only unused experimental runtime/config/tests. Do
not remove now, silently reinterpret the historical Gemma approval, or infer
that the planned paid OpenAI production API is already funded or integrated.
