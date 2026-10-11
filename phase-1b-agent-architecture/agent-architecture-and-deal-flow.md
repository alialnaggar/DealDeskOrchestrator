# Deal Desk Orchestrator — Phase 1B: Agent Architecture (Rethought)

**Student:** Ali Alnaggar
**Thesis:** Deal Desk Orchestrator (Multi-Agent System)
**Created:** 20 September 2026
**Design status (11 October 2026):** Consolidated six-specialist architecture with expanded pre-order production and fulfillment feasibility. This is the Phase 1B design baseline, not a claim that the six-agent system has been implemented. Phase 1C specifies a 24-table Schema V2; its SQL schema, smoke checks, 14 reference row fixtures and deterministic decision-gate checks have passed in GitHub Actions. Full specialist-agent/orchestrator execution, complete generated operational data and independent evaluation remain separate implementation work.

---

## 0. How we got here (context for later)

The graduation-project proposal sheet (July 2026) listed 12 agentic AI topics for ERP/CPQ/CRM. Several of Ali's colleagues are working on some of these topics individually:

- Topic 6 — Inventory Management Agent
- Topic 7 — CPQ Configuration Assistant
- Topic 8 — Lead Qualification & Routing Agent
- Topic 11 — Quote & Contract Compliance Checker
- Topic 12 — Deal Desk Orchestrator (Ali's own official thesis)

The plan was NOT to just copy-paste 4 of these agents into the Deal Desk. Instead, we asked: **what does a real Deal Desk actually do, end to end?**, listed out the real steps, and only then matched agents to those steps — pulling in colleague ideas where they genuinely fit, customizing them, and adding new agents where nothing existing fit.

**Topic 8 (Lead Qualification) was explicitly dropped.** It belongs to an earlier stage of the pipeline (before a deal even exists), not the Deal Desk approval stage. Including it would blur thesis scope.

The auto-purchase-order half of Topic 6 (Inventory) was also dropped — that's supply-chain replenishment, not deal approval. Only the pre-order delivery-feasibility half was kept, later expanded to components, procurement feasibility, production capacity and fulfillment.

---

## 1. The business process this sits inside: Quote-to-Cash (Q2C)

Q2C is the umbrella process. RevOps is just the name for the department/function that owns the whole thing — it is not a separate concept.

```
Lead comes in
   ↓
Qualify the lead                 ← Topic 8 (dropped — wrong zone)
   ↓
Configure the product            ← Topic 7 (kept, customized)
   ↓
Price the deal                   ← new agent
   ↓
Check supply/production/fulfillment ← Topic 6 (adapted)
   ↓
Check customer credit risk       ← new agent
   ↓
Check compliance/policy          ← Topic 11 (kept, customized)
   ↓
Get approval                     ← new agent (routing)
   ↓
Order → Invoice → Payment        ← Topic 9 (not in scope)
   ↓
After the sale: track happiness  ← Topic 3 (not in scope)
```

**The Deal Desk thesis owns the middle zone only**: from "product gets configured" through "deal gets an approval route." Everything before (lead qualification) and everything after (order fulfillment, invoicing, churn tracking) is explicitly out of scope.

---

## 2. What a real Deal Desk actually does (the job description we designed agents from)

1. Triage — is this deal actually non-standard? Does it even need Deal Desk review?
2. Check the config — is what the rep built a valid, sellable combination?
3. Analyze price & margin — how deep is the discount, what margin is left, is it within policy?
4. Structure the deal — payment terms, contract length, bundling
5. Check we can deliver — stock, reservations, supplier supply, BOM/components, production capacity, schedules and shipping
6. Check they'll pay — credit limit, payment history, exposure
7. Check policy & contract terms — non-standard clauses, legal/finance risk
8. Look for precedent — "have we approved something like this before?"
9. Route for approval — who signs off, in what order, depending on discount depth and deal size
10. Assemble the package — one clean document with everything plus the reasoning trail

Every agent below maps to one or more of these real steps.

---

## 3. Agent architecture: six specialists, one orchestrator and shared tools

**Status (26 September 2026): design specification; implementation and data generation are not yet complete.** This section incorporates the expanded fulfillment decision. The six specialists keep independent inputs, outputs and evaluation, particularly Credit & Risk versus Policy & Compliance. Rules govern hard constraints; agent reasoning can gather evidence, explain outcomes and propose bounded alternatives. A human handles decisions beyond delegated authority.

### 3.1 Orchestrator — coordination throughout

- **Purpose:** Accept a deal, maintain shared state, schedule eligible specialists, detect missing or contradictory evidence, handle bounded retries, and assemble an approval-ready package with an audit trail. It does not calculate domain results or choose approvers.
- **Inputs/tools:** Submitted deal and typed agent results; workflow state, validation, logging and retry controls.
- **Decision logic:** Enforce prerequisites and gates; start independent checks concurrently; compare outputs against shared deal identity, prices and rule versions; re-run only when missing/stale evidence can be recovered; escalate unresolved conflicts, failed tools or exhausted retries. Do not silently overwrite a specialist's result.
- **Outputs/exceptions:** Status, consolidated findings, unresolved issues, approval route or stop/escalation, full provenance (agent inputs, evidence, outputs, errors, retries, overrides and times).
- **Evaluation:** Completion and correct stopping, dependency/order correctness, conflict detection and disposition, trace integrity, state consistency, retry loops, latency and tool/LLM calls. Evaluate orchestration separately from each specialist's accuracy.

### 3.2 Agent 1 — Configuration Validator

- **Origin/purpose:** Topic 7 (CPQ), narrowed to whether the submitted products and selected options form valid, sellable configurations. Validate each actual bundle/assembly; unrelated quote lines need not be mutually compatible.
- **Inputs/tools:** Customer and product IDs, line quantities and configuration choices; product catalogue, compatibility rules, required attributes, lifecycle/sellability and BOM definitions where relevant.
- **Decision logic:** Check IDs, quantities, required choices, product availability for sale, constraints among selected options and applicable BOM. Hard incompatibilities require correction or a technically verified alternative; a commercial approval cannot make an impossible assembly valid.
- **Outputs/exceptions:** Normalized deal and per-line pass/fail/issues with rule evidence; missing facts or ambiguous catalogue versions stop or escalate rather than becoming invented defaults.
- **Evaluation:** Invalid configuration detection, false rejection of valid combinations, exact issue attribution, evidence correctness and downstream gate behavior.

### 3.3 Agent 2 — Pricing & Margin

- **Purpose:** Establish a verified deal value and commercial economics for subsequent credit, policy and routing checks.
- **Inputs/tools:** Validated lines, quantities, proposed unit prices/discounts and terms; list prices, costs, pricing rules and applicable policy set.
- **Decision logic:** Calculate extended prices, discount depth, cost and margins deterministically with explicit currency/rounding rules; distinguish an ordinary price or margin result from a policy exception, which Agent 5 independently classifies. Agent reasoning may explain or propose a permitted repricing.
- **Outputs/exceptions:** Per-line and deal totals, discount and margin, rule references, flags and proposed bounded alternatives; missing/ambiguous price or cost data stops the calculation or escalates.
- **Evaluation:** Numerical correctness, margin-floor detection, rule selection, evidence and correct deal value supplied downstream.

### 3.4 Agent 3 — Availability, Production & Fulfillment

- **Origin/purpose:** Topic 6 (Inventory), expanded to answer whether each proposed quantity can realistically be delivered by the requested date. This is **pre-order feasibility**; the agent does not autonomously purchase, manufacture or ship.
- **Inputs/tools:** Validated lines, quantities, delivery location/date and configuration/BOM; inventory by location, reservations, confirmed inbound finished goods, supplier lead times and purchase commitments, components and their reservations, production resources and workforce/equipment capacity, existing jobs and schedules, working calendars, assembly durations and shipping lead times.
- **Decision logic:** Compute available-to-promise finished goods after reservations; for shortfalls, test confirmed inbound supply, feasible procurement or BOM component coverage plus time-phased capacity and scheduling. Include transit. Treat hypothetical procurement and unscheduled production as conditional options, never confirmed supply. Check cross-deal commitments to avoid double counting.
- **Outputs/exceptions:** Feasible and infeasible quantities, earliest supportable delivery date, limiting resources/components, confidence or commitment status, partial delivery or technically valid substitution options, evidence and any required escalation. Missing or contradictory stock, BOM, supplier or capacity facts are explicit unknowns, not a delivery promise.
- **Evaluation:** Feasibility and date accuracy, critical-shortage recall, reservation/capacity correctness, confirmed-versus-hypothetical distinction, partial-delivery quality and evidence traceability.

### 3.5 Agent 4 — Credit & Risk

- **Purpose:** Assess the specific customer's financial exposure and payment behavior **independently** of organizational policy compliance.
- **Inputs/tools:** Verified deal value, customer ID and payment terms; credit profile and limit, current receivables/overdue amounts, open exposure and payment history.
- **Decision logic:** Compute post-deal exposure with consistent treatment of committed open deals and receivables; compare against credit limit and relevant payment-risk indicators. Report facts and risk, leaving companywide contract/policy classification to Agent 5.
- **Outputs/exceptions:** Exposure, limit headroom, payment-history evidence, OK/caution/exceeded result and explanation; stale or missing records trigger an unknown/escalation result, never an assumed pass.
- **Evaluation:** Exposure arithmetic, at-risk detection, false passes, customer matching, stale-data handling and evidence attribution.

### 3.6 Agent 5 — Policy & Compliance

- **Origin/purpose:** Topic 11 (Quote & Contract Compliance), expanded to deal-level formal policy and terms. It remains separate from Credit & Risk so failures can be attributed and tested by domain.
- **Inputs/tools:** Validated deal and Pricing result, including verified discount/margin and terms; effective policy set, restrictions, contract/payment-term rules and authorized exception criteria. It may consume independent credit/fulfillment findings only where an explicit policy rule requires them; that dependency must be declared before scheduling.
- **Decision logic:** Evaluate applicable thresholds and mandatory conditions deterministically; interpret non-standard wording only within bounded rules. Distinguish violation, permitted exception requiring approval, and insufficient evidence. A credit pass never cancels a policy violation, nor vice versa.
- **Outputs/exceptions:** Rule-by-rule pass/violation/unknown with severity, evidence, required correction or exception and escalation; conflicting rule versions or missing clauses must be resolved or escalated.
- **Evaluation:** Violation detection and severity, critical-condition recall, correct exception classification, false passes and rule provenance.

### 3.7 Agent 6 — Approval Routing

- **Purpose:** Determine required approval **roles and order** from the completed specialist findings; distinct from the Orchestrator, which manages execution.
- **Inputs/tools:** Agents 1–5's validated findings, exceptions, deal size and effective approval rules/hierarchy; all unresolved issues supplied explicitly.
- **Decision logic:** Select all applicable mandatory roles and sequencing under the approval matrix. Multiple exceptions can require multiple approvers; routing does not itself grant approval or erase a failed gate. Unresolved prerequisites route to clarification/escalation rather than normal sign-off.
- **Outputs/exceptions:** Required roles, sequence, matched rule IDs, rationale, open blockers and escalation status; unknown or conflicting authority rules stop automatic routing.
- **Evaluation:** Correct roles/order, missed mandatory approvers, unnecessary approvals, correct escalation and rationale traceability.

### 3.8 Shared tools and the optional Deal History lookup

Inventory, BOM, supplier, capacity, calendar, pricing, credit and policy queries are **controlled tools** for their relevant specialists, not automatic extra agents. The optional Deal History/Precedent lookup can return similar historical approvals to Pricing, Policy or Routing. Historical decisions give context, not permission to override current rules. Its construction is a stretch goal; it is not required for the six-agent core.

---

## 4. Execution flow and dependencies

### 4.1 Incoming deal and data contract

The submitted deal carries an identity and customer/salesperson IDs, submission time, currency and applicable catalogue/policy versions; product or service lines with quantities, proposed unit prices, selected options and bundle/fulfillment groups; payment and contract terms; destination, shipping service, requested physical arrival date, partial-delivery permission and any digital activation date or installation request; and customer requirements, special conditions, salesperson justification/comments and references to supporting evidence. The effective BOM, component quantities, required licenses/services and line dependencies are selected or validated against the catalogue rather than trusted as free-form salesperson assertions.

Phase 1C Section 3.1 and the `deals`/`deal_lines` field specifications are the detailed input contract. Discounts, deal totals and margins are derived from quoted prices and rules rather than independently trusted fields. Payment method and deal type are deferred unless a defined decision or evaluation rule needs them. Installation is an eligibility check, not an installer-capacity scheduler. Missing required inputs fail validation; missing optional evidence yields an explicit unknown or conditional result when it affects a check. A correction creates a linked new submission rather than silently changing submitted facts.

```text
Deal input (customer, configured lines, quantities, prices/discounts,
            payment/contract terms, delivery destination and requested date)
    ↓
1. Configuration Validator → invalid/unknown: correct or escalate
    ↓ valid normalized deal
2. Pricing & Margin → verified deal value and economics
    ↓
3. Availability, Production & Fulfillment ┐
4. Credit & Risk                           ├→ Orchestrator reconciles findings
5. Policy & Compliance                     ┘     ↓
                                         6. Approval Routing
                                                ↓
                           Approval-ready package, or stop/escalation
```

Agents 3–5 can run in parallel once their actual prerequisites are met: Credit requires verified deal value; Policy requires Pricing's output; Availability requires a valid configuration and BOM. If an explicit policy rule depends on credit or fulfillment, that portion must wait for the relevant result; never pretend such checks are independent. The Orchestrator records each agent's inputs, tools, outputs, errors and retries. It flags contradictions and missing evidence rather than silently selecting a winner. Routing runs after the findings are resolved or explicitly marked for escalation. Evaluate concurrent versus sequential latency on equivalent cases.

---

## 5. Orchestrator vs. Approval Routing — the key distinction (worth restating clearly, since this was the trickiest part to pin down)

| | Orchestrator | Approval Routing |
|---|---|---|
| Job | Manages the *work* | Decides *who has authority* |
| Talks to other agents? | Yes — calls them, re-triggers them, resolves their conflicts | No — only receives the finished facts |
| Has domain expertise? | No | Yes (approval-authority rules) |
| Analogy | The nurse coordinating your hospital visit | The rule that says "this needs a senior surgeon's signature" |
| Example decision | "Credit came back empty — ask Config for the right customer ID and re-run Credit" | "35% discount + €400k deal + credit exception → needs Sales VP AND Finance Director, in that order" |

**Simple test:** if the question is *"what happens next / who does the work / these two answers clash, fix it"* → that's the Orchestrator. If the question is *"who has the authority to approve this"* → that's Approval Routing.

---

## 6. Agent summary

| Component | Core decision | Prerequisite |
|---|---|---|
| Orchestrator | What runs next; how are errors and conflicts handled? | Runs throughout |
| 1. Configuration Validator | Is the requested configuration valid? | Submitted deal |
| 2. Pricing & Margin | What are verified price, discount, margin and value? | Valid configuration |
| 3. Availability, Production & Fulfillment | How much can be delivered and when? | Valid configuration and supply/production evidence |
| 4. Credit & Risk | What is post-deal exposure and payment risk? | Verified value and customer records |
| 5. Policy & Compliance | Which rules or contract conditions are breached? | Verified prices and applicable policy; explicit extra dependencies if required |
| 6. Approval Routing | Which roles must approve, in what order? | All findings and unresolved exceptions |
| Optional precedent tool | What happened in comparable historical deals? | No decision authority |

---

## 7. What's explicitly NOT in scope (to avoid scope creep later)

- Lead Qualification / lead scoring (Topic 8) — earlier pipeline stage, not Deal Desk
- Auto-generating purchase requisitions (half of Topic 6) — supply-chain replenishment, not deal approval
- Order-to-Cash automation (Topic 9), invoicing, payment collection — post-approval, out of scope
- Churn/sentiment tracking (Topic 3) — post-sale, out of scope
- Full CRM, CPQ, or ERP platform build — the core operates on synthetic data; optional later sandbox adapters do not require rebuilding those systems
- **"Chat with your ERP Database" (Topic 1)** — not a Deal Desk decision-making agent, so it does not join the core pipeline. Documented as a **future/Phase 2 extension**: a natural-language query layer on top of the finished deal history + audit trail (e.g. "show me all deals blocked on credit this month," "why was deal #4521 escalated to the VP?"). Build the core 6 agents first; add this later if time allows.

---

## 8. Product ambition & phased roadmap

Ali's goal for this project is not just a thesis-grade prototype — the long-term intent is to build this toward an actual production-quality product, while still respecting that a Bachelor's thesis timeline realistically only gets partway there. The roadmap, agreed:

**MVP → Polished Prototype → (beyond-thesis) Production**

(No separate Proof-of-Concept phase — go straight to MVP since the architecture and agent design are already worked out in this file, not just an unproven idea.)

- **MVP:** All 6 agents + Orchestrator working end-to-end on internally consistent synthetic data, basic working UI, running locally. Goal: prove the flow works, including the parallel block and conflict resolution.
- **Polished Prototype:** A stable PostgreSQL-backed prototype with a proper UI and a complete evaluated core. CRM/ERP sandbox adapters are optional extensions only after the core experiment is complete.
- **Production (beyond-thesis, stated as design intent only):** Real auth, monitoring, security hardening, live users. Realistically outside a Bachelor's timeline — the thesis should frame this honestly as "designed with production concerns in mind (structured outputs, audit trails, error handling), demonstrated as a polished prototype," not claim a shipped live product.

---

## 9. Final decision-authority and evaluation framework

The literature review supports governance according to the risk and rule type. Evaluate each agent separately so errors can be attributed to Configuration, Pricing, Fulfillment, Credit, Policy or Routing, as well as to Orchestration.

- **Deterministic or rule-validated decisions:** configuration validity, price and margin calculations, margin floors, credit-limit checks, mandatory policy conditions and approval thresholds.
- **Bounded agent reasoning:** evidence gathering, explanation, technically verified substitution proposals, supply/production alternatives, exception interpretation and deal-package assembly.
- **Human escalation:** missing evidence, unresolved contradictions, exceptional terms and any requested action outside the system's delegated authority.

The evaluation will separate final-output correctness from orchestration correctness. Planned dimensions are:

- final deal-package correctness and completeness;
- business-rule compliance and critical-subset recall;
- approval-routing and escalation correctness;
- trace integrity, state consistency and evidence provenance;
- unauthorized-action, stale-state, retry-loop and unresolved-conflict counts;
- latency, LLM/tool calls and cost.

If time permits, the same cases will be run through a single-generalist baseline. This is a validity check motivated by evidence that collaboration is not universally beneficial, not an experiment designed to prove that the multi-agent system must win.

Still open are the exact numeric policy thresholds, allowed enumerations, conflict-injection rates, and whether Deal History remains a documented stretch tool.

---

## 10. Toolkit — what to learn and what to build with

Picked to fit the actual architecture above (parallel branches, a gate, conflict resolution, structured data, real CRM/ERP integration, and a genuinely production-minded UI) — not picked for popularity.

### 10.1 Python (the language)

Already known at a basic level. What matters specifically for this project:
- **`asyncio` (async/await)** — Availability/Production/Fulfillment, Credit, and Policy run in parallel for real (Section 4). This is the actual mechanism that makes that true concurrency, not just written-to-look-parallel code.
- **Pydantic** — defines the exact shape of the data passed between agents (e.g. what a "validated deal object" looks like). Directly supports the design rule that agents shouldn't invent facts — structured data should carry them.
- **Type hints** — keeps multi-agent code from turning into a debugging nightmare as the graph grows.

### 10.2 Agent framework: LangGraph (not CrewAI)

**Why LangGraph:** the whole flow in Section 4 is a graph — a gate, a sequential step, a parallel branch, a merge point, conflict handling, a final step. LangGraph makes you draw that exact graph; nodes and edges are first-class, not a workaround. It also has real production features: **checkpointing** (save/resume a deal mid-flow if something crashes) and **persistence** (deal state survives a restart), both of which matter given the production ambition in Section 8.

**Why not CrewAI:** CrewAI is easier to start with (just define "roles"), but it hides the exact control needed here — stopping early on an invalid config, running three agents at once, catching when two agents disagree, re-running a failed agent. That level of control is exactly what CrewAI abstracts away. LangGraph does not.

Learn specifically:
- Nodes and edges (each agent = a node)
- Parallel branching (the Step 3/4/5 block)
- Conditional edges (the Orchestrator's "if invalid, stop" gate; "if conflict, flag exception" logic)
- State schema (where Pydantic plugs in)
- Checkpointing/persistence (for the production-minded angle)

### 10.3 Data & tools layer

- **PostgreSQL from the start** stores deal data, pricing rules, credit records, supply/production facts, deal history and execution logs. Phase 1C specifies a 24-table Schema V2 for the expanded pre-order fulfillment scope. The schema, smoke checks, 14 reference row fixtures and deterministic decision-gate checks have passed in GitHub Actions; full generated operational data and six-agent execution remain unfinished.
- **REST API basics** — both Salesforce and Odoo are reached over REST APIs.
- **OAuth basics** — Salesforce (and most real CRMs) require OAuth to access their API; need at least the simple token flow.

### 10.4 Backend & frontend (production-minded UI, not a throwaway demo)

- **FastAPI** — serves the LangGraph agents as an API layer.
- **Next.js (React) + Tailwind CSS** — the chosen demo-day UI for a polished deal submission form, findings, approval dashboard and audit history. FastAPI remains the business API; Next.js does not duplicate the agent or rule engine.
- **Streamlit** — kept only as an internal dev tool for fast testing of agent outputs while building. Not the final UI. Build the Next.js UI only once backend logic is stable — don't build both at the same time.

### 10.5 LLM strategy: free development, paid OpenAI for the deployed version

- **During development:** Prefer a suitable openly licensed model run locally through Ollama or another local runtime. Limited free Hugging Face hosted inference credits or provider promotions can support small experiments; they are not assumed sufficient for the full evaluation. Grok/xAI is an alternative only when actual API credits or budget are available, not a guaranteed free API.
- **Provider-neutral interface:** Keep model calls behind one Python adapter with typed input/output contracts. Record provider, model/version, prompt version, tool calls, latency and cost per run. Business calculations, feasibility checks, policy thresholds and mandatory approval rules remain deterministic regardless of model.
- **For the final deployed prototype and any later production use:** Switch the adapter to a paid OpenAI API model if comparative tests show it meets the required quality and budget. Rerun the same evaluation cases after switching models; report results by provider/model rather than attributing local-model results to the final model. OpenAI API spend is a separate budget from AWS hosting.
- **Agentic role:** Specialists may use an LLM to select relevant evidence queries, interpret unusual text, explain findings and propose bounded alternatives. The orchestrator and deterministic tools validate all proposed actions; a model cannot override hard constraints. A rule-only baseline helps measure whether LLM reasoning improves decisions.

### 10.6 Cloud: AWS

Picked now so the code isn't written against "generic Python" and then rewired later, even though AWS itself isn't touched until later implementation phases.
- Develop locally first; deploy closer to the demonstration if the account is eligible for AWS new-customer credits and the available balance covers the selected services. Credits and the Free plan have time and usage limits; check account eligibility and costs before provisioning.
- Later path: RDS can host PostgreSQL, an eligible compute service can run the FastAPI/LangGraph backend, and S3 can store exported reports. The exact compute service remains a deployment decision, not a prerequisite for the core experiment.
- Chosen over GCP/Azure mainly for industry recognition/resume value — no strong technical reason to prefer it otherwise

### 10.7 Optional CRM/ERP integration (after evaluated core)

- **CRM → Salesforce Developer Edition** (free forever, real API, well documented, industry-standard)
- **ERP → Odoo Community Edition** (free, self-hosted, real Inventory + Accounting modules — exactly what Availability and Credit agents need, real REST API, larger community than the ERPNext alternative that was also considered — chosen for the bigger community/faster troubleshooting and stronger name recognition in the thesis write-up, despite Ali having more prior hands-on experience with ERPNext)

### 10.8 Learning order (practical sequence)

1. Python: `asyncio`, Pydantic, type hints
2. LangGraph: nodes, parallel branches, conditional edges, state, checkpointing
3. PostgreSQL + basic REST/OAuth
4. FastAPI (backend API layer)
5. Provider-neutral LLM adapter; local/free development model, then a measured OpenAI API switch for the final deployed version
6. Next.js + Tailwind (frontend) — after backend logic is stable
7. AWS basics and deployment costs — later implementation phases
8. Optional Salesforce Developer Edition + Odoo Community Edition — after the evaluated core works

---

## 11. Documentation practice during implementation

**Rule: document everything as it's built, not retroactively at the end.** This isn't optional polish — a thesis needs to show the process, not just the finished result, and trying to reconstruct decisions/reasoning after the fact loses detail and looks thin in the write-up.

What to document, as it happens, for each agent/component as it's built:
- Design decisions and why they were made (including any change from what's written in this file — update this file too when that happens)
- Problems hit and how they were solved (integration quirks, framework limitations, bugs that shaped the design)
- What was tried and abandoned, and why (negative results are still results, and are useful for the thesis's discussion/limitations section)
- Prompts, schemas, and configuration used for each agent, versioned as they evolve
- Test cases and evaluation results as they're run, not just a final summary

Suggested lightweight approach: a running dev log (dated entries) alongside the code, plus keeping this project's files (Phase 1A/1B, and future phase files) updated as decisions change — rather than one big write-up attempted after implementation is "done." This running log is also what the evaluation chapter and the thesis defense will draw on.

---

## 12. Security — deferred, placed at the end near CRM/ERP + Chat-with-ERP integration

Security work is intentionally **not** part of the MVP or early build. It's scoped in for later, deliberately grouped with the two other integration-heavy pieces it naturally belongs with:

- Optional real CRM/ERP integration (Section 10.7 — Salesforce Developer Edition + Odoo Community Edition)
- The "Chat with your ERP Database" future extension (Section 7)

**Why grouped there:** security concerns only become concrete once the system is actually talking to real external systems and real (even if sandboxed) data — OAuth token handling, credential storage, access control on what a natural-language query agent is allowed to touch, audit logging on real integrations. Bolting security controls onto fake/sample local data earlier doesn't teach much and would slow down proving the core agent logic works.

**What "security" means here, roughly (to flesh out once this phase starts):**
- Proper OAuth/credential handling for the Salesforce and Odoo integrations (not hardcoded secrets)
- Access control / permission-respecting behavior, especially for the Chat-with-ERP natural-language query layer (a query agent must not be able to see or return data the requesting user isn't allowed to see)
- Basic audit logging on real integration calls, building on the audit trail the Orchestrator already maintains internally (Section 3.1)

This stays a placeholder for now — full detail to be defined if Section 10.7 integration work starts.

---

## 13. Relationship to other files in this project

- `00-Deal-Desk-Orchestrator-Master-Progress.md` is the authoritative project-level status.
- `03-Deal-Desk-Orchestrator-Phase1A.md` contains the completed literature-review tracking and evidence base.
- `02-Deal-Desk-Orchestrator-Phase1C.md` defines the 24-table PostgreSQL Schema V2, the incoming-deal field contract and the synthetic-data strategy for expanded production and fulfillment. Schema and reference checks have passed; full generated data and independent agent evaluation remain pending.
- `07-Literature-Review-Submission-Draft.md` contains the concise university-aligned literature review that justifies the governance and evaluation choices above.
