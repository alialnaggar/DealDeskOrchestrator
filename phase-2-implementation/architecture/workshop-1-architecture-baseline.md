# Workshop 1 architecture baseline — D1, D2 and D3

**Status:** Architectural direction provisionally approved by Ali on 18 October 2026. This is a readable bridge to detailed specifications, not a completed master blueprint or implementation authorization. The [decision log](../planning/decision-log.md) records rationale, alternatives, dependencies and approval status. Approved Phase 1B domain design and Phase 1C data/rules retain precedence in their scopes.

## Business example and authority

A salesperson submits 20 configured units requested by Friday and permits partial delivery. Configuration validates first. Fixed evidence may establish 12 supportable by Friday and a potential later eight that is conditional on supplier confirmation. Fulfillment is the first AI-intensive specialist: it may investigate authorized facts, propose a split with unmet date/tradeoffs, or abstain. The candidate remains unverified until fixed Python checks the exact schedule and all applicable rules. A human receives a comparison; the system does not promise delivery or approve a deal.

No AI or Orchestrator may approve, waive policy, reserve stock, book capacity, purchase supplies, promise delivery or alter the original submitted deal. Confirmed, conditional, unknown and infeasible must remain distinct. A structurally valid candidate is not automatically feasible, committed or approved.

## Selected architecture

- **Framework:** LangGraph from M1 for nodes, conditional edges, typed shared state and bounded candidate recheck loop. Begin sequentially, with a small understandable graph. Business calculations and rules remain ordinary Python services called by graph nodes. Specialists expose typed contracts independent of graph internals.
- **Specialists:** Six separately attributable responsibilities: Configuration, Pricing, Fulfillment, Credit, Policy and Approval Routing. Configuration starts the real flow; Fulfillment gains the first substantial AI proposal capability. Other AI capabilities arrive incrementally. Credit and Policy remain separate.
- **Contracts:** Common versioned run/evidence/provenance/result/error envelope plus domain-specific inputs and payloads. Agent tools are named, authorized and read-only, permitting bounded investigation without unrestricted SQL, arbitrary code or credentials. AI claims/proposals, fixed verification and workflow-control transitions are separate records. AI may abstain; no uncalibrated numeric confidence.
- **State:** Original run/deal identity and immutable input reference; as-of time, snapshot context, source fingerprint and catalogue/policy/rule versions; current original/candidate subject; per-subject outputs and verification; dependencies; candidate lineage/diffs; trace; model/tool calls; budgets/retries; errors/conflicts/stops; final package status. Specialists return outputs; the Orchestrator validates and updates state.
- **Evidence:** As-of cutoff, transaction snapshot and source fingerprint have different meanings. Define and test a mechanism that gives nodes and candidate reruns the same selected facts or reconstructs them exactly. A refresh creates a separately identified assessment context.
- **Order:** Configuration precedes dependent checks. Pricing needs validated commercial context; Fulfillment needs valid configuration and dated facts; Credit needs verified value; Policy waits only for prerequisites of applicable rules; Routing follows complete reconciled findings. Run M1 sequentially; evaluate parallelism later with measured correctness, latency and traceability.
- **Candidate path:** An AI proposal begins unverified with its own ID, parent, exact changes, assumptions, evidence and trace. Fixed validation checks it. M1 reruns all six deterministic responsibilities for the first checked candidate; Routing recomputes for the exact subject. Selective reuse later requires equal input fingerprints, evidence versions and proven dependencies. Neither candidate nor its findings overwrites the original.
- **Failure path:** Classify business violation, evidence gap/staleness, conditional/unknown, abstention, malformed model output, invented reference, rejected proposal, transient tool/model error, identity/version conflict, contradictory findings and exhausted budget. Fail closed, retain the original fixed result if AI fails, retry only eligible transient idempotent work, withhold ordinary executable routing on unresolved required findings, and record the stop.
- **M1 budgets (provisional engineering defaults):** Two distinct proposals, one candidate revision level and one retry of eligible transient model/tool failure. Specify configurable time and tool-call budgets. No unbounded graph loop.
- **Human output:** Original findings, candidates and verification outcomes, differences, unmet constraints, evidence/time/freshness and commitment status, roles/order where applicable, risks/conflicts, stop reason and provenance. A person decides whether to pursue a linked revision through a separately authorized process.

## Scope of the first milestone versus complete design

M1 must start with Configuration validation and then respect each downstream prerequisite. Its first substantive model task is Fulfillment shortage investigation for the narrow 20-unit partial-delivery fixture, with deterministic candidate verification and full six-responsibility recheck. The full architecture also supports later Configuration substitutions, Pricing revisions, Credit evidence analysis, Policy corrections, Routing explanation, bounded multi-candidate comparisons and orchestrated reruns. It does not require six model calls for every deal or treat deterministic responsibility summaries as live AI specialists.

## Phase 1C dependency boundary

The newer typed partial-delivery candidate, reader-backed correlation, trace, dated reader, compiled decisions and deterministic runtime proof are on draft PR #1 (`phase1c-candidate-contract`), audited at `90c0bc8e285ee69262c7db826b786096a77ad004`. The Phase 2 branch diverged. These experiments can inform contracts but are not a released general candidate API. Before integration, pin actual input/reader/rule/candidate signatures, trusted fixtures and a reproducible combined test strategy. Do not modify Phase 1C or merge its draft PR by implication. The 36 evaluation cases still had zero accepted independent answers at audit; no improvement claim is established.

## Detailed design still open

**Provider disposition (31 October 2026):** Gemma is permanently discontinued and has no active adapter or planned comparison. This does not change the LangGraph/fixed-rule architecture, the guarded Groq development runtime or the separately approved future OpenAI production direction; paid API use remains unauthorized.

1. Exact LangGraph version, state type, node contracts, edges and execution topology.
2. Transaction/snapshot consistency or exact reconstruction across graph nodes, plus source fingerprints.
3. Checkpointing/persistence and resumption; no additional infrastructure is implied.
4. Candidate state transitions, lineage and verification statuses.
5. Selective invalidation and reusable-result fingerprints.
6. Exact error taxonomy, timeout/tool-call budgets, retry policy and final package schema.
7. Model-provider choice and metered cost authorization; offline mock-model tests.
8. Phase 1C compatibility and full workflow acceptance tests.
9. Evidence-based decision on parallel execution.

Before any material technology change, follow [TG1 in the decision log](../planning/decision-log.md): explain alternatives and impacts, then obtain Ali's explicit approval. LangGraph is selected; a custom Python state machine is not its replacement.
