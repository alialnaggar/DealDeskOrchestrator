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

**Design decision (11 October 2026):** A submitted deal is predominantly structured. The aim is an evidence-backed recommendation for *human* approval, not autonomous approval or a delivery promise. Specialists may investigate failed checks and propose bounded alternatives; deterministic tools validate each proposal. These are target capabilities, **not claims that six LLM specialists or alternative search have been implemented**. The Phase 1C reader and decision gate are a tested rule-based foundation; full specialist and Orchestrator execution remain open.

A specialist is a separately attributable business responsibility with typed inputs and outputs. Use ordinary code for fixed rules. Invoke a model only for a measurable task such as selecting relevant evidence, developing a constrained option, or explaining a nontrivial conflict. Do not manufacture agent activity to meet an agent count. Credit and Policy remain independent. Every result includes deal/run and candidate identity, data-as-of time, catalogue/policy versions, evidence IDs, rule IDs, status (pass, fail, conditional or unknown), and a short business explanation. Reasoning summaries are not private chain-of-thought.

### 3.1 Orchestrator — coordination, not domain authority

- **Purpose:** Accept an immutable submitted deal, maintain shared run state, order eligible checks, coordinate bounded candidate revisions, compare specialist findings, and assemble the human review package. It neither computes a domain result nor chooses approval roles.
- **Inputs/tools:** Typed deal and candidate records; specialist outputs; workflow state, data snapshot, validation, logging and retry controls. It can request a fresh authorized read, but cannot silently switch evidence snapshots inside an already frozen run.
- **Initial flow:** Validate the deal's shape; run Configuration, then Pricing; run Fulfillment, Credit and Policy as their declared dependencies permit. A rule that explicitly needs another specialist's finding waits for it. Reconcile identities, values, versions, evidence times and contradictory statuses before Routing.
- **Alternative flow:** When a specialist reports a recoverable issue, invite a bounded proposal, retain the original unchanged, check candidate field changes against the customer's stated constraints, create a separately identified candidate, and rerun Configuration and Pricing plus all affected downstream checks. Route only the completed, internally consistent candidate. Candidates are simulated, not accepted quotes or stock reservations. A customer's acceptance or correction becomes a linked new submission, never a hidden mutation.
- **Limits:** Limit candidate count, search depth, tool calls and retries; deduplicate equivalent proposals. A hard incompatibility, unsupported commitment, stale critical evidence, unknown authority, or exhausted budget remains a blocker/escalation. Never turn a hypothetical supply path into a promise or choose a winner by overriding a specialist.
- **Output/evaluation:** Original-versus-candidate comparison, evidence and assumptions, rerun dependency trace, unresolved blockers, reviewable status and audit trail. Test correct stopping, changed-field invalidation, state/version consistency, conflicts, duplicate/loop prevention, latency, cost and tool/model calls.

### 3.2 Agent 1 — Configuration Validator

- **Purpose/input:** Check product IDs, quantities, chosen options and true configured groups against catalogue version, sellability, compatibility rules and effective BOM (bill of materials: components required for an assembly). Unrelated lines are not automatically incompatible.
- **Deterministic boundary:** Reject missing choices, invalid bundles, unavailable-for-sale products and hard incompatibilities. An approver cannot waive a technically impossible configuration. Installation eligibility and dependencies follow the catalogue rules; this is not an installer scheduling service.
- **Added capability:** If the submitted choice fails, search the *offered* catalogue for an option or product satisfying the same explicit customer/site requirements. Show what changes (feature, licence, component, group, quantity) and which requirement may no longer be met. A substitute is a proposal, not a valid line until the entire configured group and BOM are rechecked.
- **Output/evaluation:** Normalized lines, exact failing rule and evidence, verified candidate or a clear no-option/unknown result. Test invalid detection, false rejection, group completeness, customer-constraint preservation and quality of proposed alternatives. A missing catalogue version or unproven technical fit stops the candidate.

### 3.3 Agent 2 — Pricing & Margin

- **Purpose/input:** Use valid configured lines, quantity, quoted unit prices, currency/term, effective list prices, costs and pricing rules to establish full-term value, discount and margin.
- **Deterministic boundary:** Calculation, unit/currency/rounding conventions, margin floors and permitted prices are executed by tools. Policy separately decides whether a commercial exception is approvable. The model never supplies a number as the source of truth.
- **Added capability:** Offer a small set of permitted repricing options for an original or substituted line (for example, price that restores a margin floor), with the verified changes to total, discount, margin and customer-facing terms. Never silently change a quote; if price evidence or a compatible comparison is missing, mark the option unknown.
- **Output/evaluation:** Verified arithmetic, applied rule and evidence IDs, candidate price deltas and explanatory tradeoffs. Test numeric and unit correctness, floor detection, candidate legality and correct downstream value passed to Credit, Policy and Routing. Price changes require those downstream checks again.

### 3.4 Agent 3 — Availability, Production & Fulfillment

- **Purpose/input:** Assess pre-order feasibility for physical goods, configured builds, digital activation and installation eligibility, using validated groups/BOM, destination/date, dated stock and allocations, confirmed inbound, supplier offers, component supply, capability/day workforce and equipment hours, digital proof and shipping lanes.
- **Deterministic boundary:** Calculate free stock, component demand, net capacity and supportable dates; distinguish available, confirmed, feasible-but-uncommitted, conditional, unknown and infeasible. Day-level capacity is not a factory booking. An offer or unconfirmed build is not a delivery commitment. Do not purchase, schedule, reserve or ship.
- **Added capability:** When the requested date/quantity is unsupported, develop a limited set of options: a later supportable date, partial quantities/dates only if the customer permits them and groups stay intact, or a candidate substitute to be verified by Configuration. Describe the bottleneck, evidence time, assumptions and which option requires supplier or human confirmation. Digital activation is evidence-bound; installation remains eligibility only, not an appointment.
- **Output/evaluation:** Per-line/group feasibility, earliest supportable dates within the represented horizon, bottleneck and commitment class, plus candidate options and explicit unknowns. Test feasibility arithmetic, no double counting across commitments, conditional-versus-confirmed distinction, partial/group legality and candidate usefulness. No represented future capacity means unknown, not an invented date.

### 3.5 Agent 4 — Credit & Risk

- **Purpose/input:** Assess this customer's exposure and payment behavior independently of Policy, using verified full-term deal value, terms, credit profile, dated receivables, unbilled commitments and payment history.
- **Deterministic boundary:** Calculate post-deal exposure and limit headroom without counting the proposed quote or receivables twice; show stale/missing inputs as unknown, never pass. An explanation or good payment history cannot waive an exceeded limit.
- **Added capability:** Attribute the concern to the specific exposure or payment evidence; when an authorized fresher source is available, request a new controlled read and rerun. Compare how a *verified* lower-value candidate changes exposure, without proposing an unauthorized credit-limit change or declaring approval.
- **Output/evaluation:** OK/caution/exceeded/unknown, amount and dated evidence, what needs refreshing, candidate delta and remaining blocker. Test arithmetic, customer identity, freshness, no double count, false passes and accurate candidate comparisons. A requested payment-term change also triggers Policy.

### 3.6 Agent 5 — Policy & Compliance

- **Purpose/input:** Independently apply effective policy rules to validated terms and Pricing findings; consume Credit or Fulfillment only where a specific policy condition declares that dependency.
- **Deterministic boundary:** Mandatory clauses, thresholds, permitted exception classes and hard blocks are rule-checked. A credit pass cannot cancel a policy violation. Interpretation of unusual wording is optional and bounded; structured clause codes, not free-text comments, are the primary input.
- **Added capability:** Produce a rule-by-rule explanation and classify a problem as correctable, a configured exception needing human approval, or insufficient evidence. Suggest a *permitted* terms/price correction where possible, which must be represented as a candidate and rerun through affected specialists. A salesperson justification is not proof of a waiver.
- **Output/evaluation:** Rule IDs, pass/violation/unknown and severity, evidence, requested correction or exception role, and reason a candidate does or does not clear a rule. Test critical-condition recall, false passes, exception classification, version selection and evidence trace. Conflicting or missing effective rules block normal routing.

### 3.7 Agent 6 — Approval Routing

- **Purpose/input:** From a fully checked original or candidate, read all independent findings and the effective approval matrix; choose required *roles and order*, distinct from the Orchestrator's execution management.
- **Deterministic boundary:** Combine all applicable mandatory roles, sequencing, thresholds and unresolved blockers. Routing cannot grant approval, waive a hard failure, or turn a conditional option into a confirmed deal.
- **Added capability:** Explain why each human role is involved, what exactly the person is being asked to review, and which blockers prevent ordinary sign-off. If the chosen candidate differs from the original, compute the route from its final verified value and findings, not cached original results.
- **Output/evaluation:** Ordered roles and matched rule IDs or an explicit stop/clarification path, with a concise review brief. Test missing/unnecessary approvers, order, escalation, candidate-specific rerouting and rationale. An unknown authority rule stops automatic routing.

### 3.8 Shared tools and optional Deal History

Catalogue, BOM, inventory, supplier, capacity, shipping, digital, pricing, credit and policy reads are controlled tools, not more agents. Optional Deal History may show comparable *historical* decisions for context; it is not a permission source, an evaluation answer key, or required for the core.

### 3.9 Candidate and recommendation contract

Every alternative is a **proposal** linked to its immutable original. Define one typed candidate record with `candidate_id`, `parent_deal_id`, exact changed fields, customer constraints preserved or violated, evidence IDs and as-of time, catalogue/policy/snapshot versions, assumptions, commitment status, deterministic verification, each affected specialist's finding and a human-readable tradeoff. The candidate record is a contract proposal, not a new table or an implemented runtime object. Candidate search is limited and side-effect free. Do not assert an option is feasible when any mandatory check is missing or unknown. The package compares the submitted deal, valid checked options, conditional options, rejected options and outstanding human decisions without conflating their statuses.

A customer/salesperson choosing an option must submit a linked revision and run the checks on that submission. An approver's action is a separate human event beyond a routing recommendation. No candidate proposal edits submitted facts, raises a credit limit, changes a policy, allocates stock, books production, or creates an ERP order.

## 4. Execution flow and dependencies

### 4.1 Incoming deal and data contract

The submitted deal carries identity, customer/salesperson IDs, submission time, currency and effective catalogue/policy versions; configured lines with quantities and quoted unit prices; payment/contract terms; destination, requested physical arrival date, partial-delivery permission, any digital activation date and installation request; structured customer/site requirements, justification and evidence references. Salesperson comments are supplementary, **not a required source of requirements**. Phase 1C's `deals`/`deal_lines` definitions specify the fields. Effective BOM quantities and licence dependencies are checked against the catalogue, not trusted from a comment. Discount, total and margin are derived. A submitted deal is immutable.

### 4.2 Initial assessment and bounded alternative loop

1. Configuration validates the submitted deal. Invalid configuration stops the *original* from normal routing, but a technically checked correction candidate may be explored.
2. Pricing calculates the economics of valid configured lines. Fulfillment, Credit and Policy run when their actual prerequisites are satisfied; explicitly dependent policy rules wait.
3. The Orchestrator reconciles identity, evidence time, versions and independent findings. Hard blocks, missing evidence and conflicts cannot be hidden by a favorable result from another domain.
4. When useful and permitted, specialists propose a small bounded candidate set. The Orchestrator records changed fields and invalidates affected outputs: product/options/group changes rerun Configuration, Pricing, Fulfillment and any dependent Credit/Policy; price or quantity changes rerun Pricing and affected Fulfillment/Credit/Policy; delivery/date/partial changes rerun Fulfillment and dependent Policy; terms change Credit/Policy as applicable. Routing is always recomputed after final findings. These are conservative dependency rules; never reuse a stale result merely to save calls.
5. Each checked candidate is classified as verified, conditional, unknown or rejected, with its own trace. Routing uses completed findings for the exact candidate and may output an escalation path when ordinary approval is unavailable. The Orchestrator assembles the comparison and hands decisions to humans.

Agent 3–5 parallel execution applies only when their declared inputs are ready; reruns need not restart unrelated checks if their inputs and evidence versions remain identical. Bound candidate count, loops and retries. If no safe candidate survives, the output is a correction request, evidence request, or blocked/escalated package rather than a fabricated approval-ready deal. Compare the agent-assisted run with a rule-only baseline and separately evaluate alternative quality and orchestration.

### 4.3 Illustrative structured deal

A customer requests 20 configured workstations by Friday at a quoted unit price. The reader shows 12 supportable by that date and the rest later. Fulfillment may propose a partial delivery only if the input permits it and indivisible groups remain intact, or a substitute from the offered catalogue. Configuration validates the substitute and BOM; Pricing recalculates its full-term value and margin; Fulfillment checks its dated supply; Credit and Policy recheck the changed value/terms; Routing recomputes roles. The package shows what is confirmed versus conditional and requests customer choice and human approval; it does not promise, reserve, or submit an ERP order.

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

## 9. Decision authority, staged implementation and evaluation

**Hard authority:** Fixed tools validate configuration, arithmetic, supply/capacity feasibility, credit exposure, policy thresholds and approval roles. An LLM may gather authorized evidence, propose a limited candidate or explain a finding; it cannot override any tool, invent evidence, waive a rule or approve/commit a deal. The human decides whether to revise, seek a configured exception, approve through the route or stop. A language-model-free specialist is valid when it better expresses the fixed responsibility.

**Current versus target:** Phase 1C's 24-table schema, reader, deterministic decision gate and test/pilot artifacts are foundations; they do not demonstrate the six running specialist agents, Orchestrator candidate loop, independent alternative-quality evaluation or Salesforce/Odoo adapters. Implement the rule-only baseline first, then one bounded candidate loop spanning multiple specialists, then broaden options only when evidence and tests support them. The 14 reference scenarios establish narrow contracts, not complete evaluation; 400 historical diagnostics are not independent labels. Consult Phase 1C's README and release review for dated current status.

**Evaluation by responsibility:** Measure each specialist's base-check correctness, evidence attribution, unknown handling, candidate validity and useful improvement over the original. Measure Orchestration's dependency invalidation, rerun correctness, contradictory/stale evidence handling, loop/side-effect prevention and final package consistency. Measure Routing on the exact checked candidate. Report hard-constraint violations, hallucinated/unsupported alternatives, false delivery commitments, missed approvers, unresolved conflicts, latency, cost and model/tool calls. Independently authored held-out cases must include both useful alternatives and cases where no safe option exists. Compare the final recommendation against the same-case rule-only workflow and, if feasible, a single-generalist baseline; do not presume more agents are better.

**First implementation experiment:** Keep the 24-table schema and use a typed candidate record for one shortage → permitted partial delivery or catalogue substitute → complete affected-check rerun. Verify identity and replay across candidates before choosing separate correlated runs or a small schema migration. Expand held-out scenarios, and close product fit and comparable price/cost evidence before claiming viable recommendations; adding rows alone does not fix those gaps. The core input fields are largely sufficient, while candidate tracking and supporting-data coverage require work.

**Open design choices:** Candidate search limits, ranking criteria (for example customer constraints, date and economics), approval UX, exact source-of-truth mapping for live integrations, and final independently reviewed evaluation cases must be specified before claiming these additions work. Accepted synthetic commercial thresholds do not imply operational calibration or evaluation labels are frozen.

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

- **PostgreSQL from the start** stores deal data, pricing rules, credit records, supply/production facts, deal history and execution logs. Phase 1C specifies a 24-table Schema V2 for the expanded pre-order fulfillment scope. The schema, reference checks, reader and deterministic gate have passed relevant checks; provisional 36-deal pilot and 400 historical submission/evidence artifacts now exist. The 400-case baseline is diagnostic rather than independently reviewed labels; full six-specialist execution and evaluation remain unfinished. See Phase 1C's README and release review for current status.
- **Integration basics** — Salesforce REST access and version-appropriate Odoo integration are optional adapter work; verify available models, permissions, plan and deployment before choosing an Odoo endpoint.
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

- **CRM → Salesforce Developer Edition (optional sandbox):** Map accessible customer/opportunity/quote and line records to the same typed deal contract. Verify actual objects, permissions, authentication and field availability; no AI capability depends on Salesforce being connected.
- **ERP → Odoo (optional sandbox):** Map configured product, stock, purchasing, capacity and accounting records to controlled evidence contracts where available. Odoo version, Community/self-hosted deployment versus hosted plan, installed modules and access method require verification. Odoo 19 documents JSON-2 external access with hosted-plan restrictions; older RPC endpoints have announced deprecation. Do not assume a universal REST endpoint or that an inventory record proves a delivery commitment.
- **Boundary:** Define fact ownership, external IDs, units/currency/time zone, as-of times, missing-field behavior and conflict policy. Use read-only sandbox ingestion for the thesis; no automatic order creation, reservation, credit-limit update or approval. PostgreSQL synthetic evidence stays the evaluated baseline. Salesforce REST reference: https://developer.salesforce.com/docs/platform/api-rest/guide/resources-list.html ; Odoo 19 JSON-2: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html ; RPC deprecation: https://www.odoo.com/documentation/19.0/developer/reference/external_rpc_api.html .

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
