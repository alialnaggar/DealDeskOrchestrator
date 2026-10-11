# Business-Side Paper Extraction — B1–B12

Companion to `Multi-Agent-Orchestration-Paper-Analysis.md` (orchestration side). Same extraction discipline: anything that is an interpretation for thesis relevance rather than an authors' claim is labelled **Thesis interpretation**.

## Template change

Three fields added to the original template, because the original was built for orchestration papers and has no slot for what matters most here:

- **Business constraint enforcement** — how deterministic rules were imposed on the LLM.
- **Observed failure modes** — distinct from Limitations. Limitations are what the authors concede; failure modes are what the system actually did wrong.
- **Business domain & data realism** — which process, which data, how close to a real enterprise setting.

Two fields are marked **N/A** for B4, B5 and B7: *Architecture* and *Agent responsibilities*. Those are review papers with no system of their own.

## Source access status

| Paper | Access | Extraction depth |
|---|---|---|
| B1 | Open access (MDPI) | **Full text** — verified including section numbers |
| B3 | Full text supplied by user | **Full text** — verified including all tables |
| B4 | Full text supplied by user | **Full text** — verified up to Section 5 (research gaps) |
| B6 | Author preprint full text | **Full text** — verified, cite journal version |
| **B7** | **Open access (CC BY 4.0, ACM)** | **Full text** — verified, all sections 1–6 |
| **B8** | Springer publisher page | **Official abstract only**; complete chapter not obtained |
| **B9** | Accepted author manuscript | **Full text** — verified |
| **B10** | Complete nine-page author version (arXiv); official ACM DOI verified | **Full text** — verified against the complete paper |
| **B11** | Open access, Springer Nature | **Full text** — verified |
| **B12** | Full text supplied by user, SAGE | **Full text** — verified |
| B2 | Paywalled (Springer) | Abstract-level — marked ⚠ — optional, not blocking |
| B5 | Paywalled (Springer) | Abstract-level — marked ⚠ — **superseded in part by B7**, see note |

B2 remains desirable for its unique ERP multi-agent segregation-of-duties angle, but it is not blocking. B1, B7, B9, B11, and B12 provide sufficient governance and conventional-process evidence for the current LR. Do not infer B2's architecture, mechanism, or results from the abstract:
- B2: https://link.springer.com/chapter/10.1007/978-3-032-15632-7_7
- B5 (lower priority now — B7 covers the evaluation argument from a stronger venue): https://link.springer.com/chapter/10.1007/978-981-92-2014-4_26

## Rejected sources — recorded so the decision is not revisited

| Source | Reason for rejection |
|---|---|
| MASCA: LLM-based Multi-Agent System for Credit Assessment (arXiv:2507.22758) | Preprint, no peer-reviewed version located. Excluded under the review's no-preprint rule. |
| Srivastav, *Multi-Agent Artificial Intelligence for Autonomous Enterprise Automation* (SSRN, posted 17 Jul 2026) | Preprint **and** quality-disqualified — see note below. **Do not cite.** |
| Febryanto et al., *Knowledge Graph-Grounded BDI Architecture for LLM-Based Multi-Agent Orchestration in Enterprise Workflow Automation* (IEEE ICSMech 2026; DOI 10.1109/ICSMech69390.2026.11647167) | **Screened but not retained.** The complete paper could not be obtained after two independent access searches. Metadata/abstract snippets are insufficient for architecture, governance or result claims; no pool ID assigned. |

**On the Srivastav SSRN paper.** Rejected on four independent grounds, any one of which is sufficient:

1. **Contaminated front matter.** Its Ethics Approval statement reads: *"All data used in this research were obtained from publicly available datasets (BUSI – Breast Ultrasound Images Dataset)."* The paper is a literature review of enterprise automation and contains no ultrasound data. The statement is template text carried over from an unrelated manuscript and never removed.
2. **Preprint-based evidence chain.** Its own Section 2.2 lists SSRN, Authorea and "AGPH Books" among its data sources. Two are preprint repositories and one is a vanity publisher, so its synthesised claims rest on non-peer-reviewed material. Citing it would import exactly the evidence class this review excludes, one layer down.
3. **No PRISMA, no screening counts.** It calls itself a systematic literature review but reports no funnel, no screened total and no included total. Compare B4 (182 → 120 → 51 → 60).
4. **Citation pattern.** Every in-text citation is a 2025 single-surname source. It discusses the Contract Net Protocol, FIPA ACL, JADE, Paxos, Raft and BDI architectures — all of which have canonical originating papers — and cites none of them.

**Thesis interpretation.** Transparency flagging does not repair this. A flagged citation still tells an examiner that the author read the source and judged it usable; the ultrasound line makes that judgment indefensible and casts doubt on every other source in the bibliography. Excluded outright.

---

# B1 — Governed Agentic Process Automation: A Floor-Safety Guarantee for Compliance-Critical LLM Routing

> **Verification completed 24 September 2026:** the approval-subset count, aggregate accuracy, mandatory-escalation recall, and stability values were checked directly against Tables 7, 10, and 11 of the complete paper.

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Massimo Pacella, Gabriele Papadia, Vincenzo Giliberti |
| Venue | *Algorithms* 19(8), 627 — MDPI |
| Year | 2026 |
| DOI | 10.3390/a19080627 |
| Peer review | Peer-reviewed journal article, open access |
| Research type | Architecture proposal + empirical evaluation |
| Main area | Agentic process automation; LLM governance; compliance routing |
| Thesis relevance | **Very high** — approval enforcement |

## 2. Problem and objectives

The problem is precise and directly transferable. An LLM in an agentic workflow may **recognise elevated risk in its own written rationale and still fail to select the mandatory human-approval route**. The authors call this *silent under-escalation*: the policy violation leaves no trace until an audit.

The stated gap is between **agent capability** (what an LLM can do) and **agent governability** (whether its decisions stay inside organisational constraints).

Objectives: bound LLM autonomy while preserving discretion where appropriate; formalise a floor-safety property; demonstrate empirically that the mechanism prevents missed escalations; and show that governance must be **architectural rather than prompt-level**.

## 3. Architecture

Five layers (Section 3.3):

| Layer | Function |
|---|---|
| Intake | Schema validation, mandatory field checks, completeness logging |
| Cognitive | The only layer where the LLM acts; produces **proposals only**, never executes |
| Control | Executes a fixed `mainWorkflow`; sequences actions per governed decisions |
| Execution | Deterministic atomic actions (account creation, group assignment, mailbox setup) |
| Governance | Applies guardrails, provides deterministic fallback, maintains append-only audit log |

The structural move worth copying: **the LLM proposes, the architecture disposes.** The cognitive layer cannot execute anything.

## 4. Agent responsibilities

Not a multi-agent system in the ChatDev/CAMEL sense. A single LLM decision point wrapped in deterministic machinery, plus a `DataAgent` for natural-language artifacts.

**Thesis interpretation.** This is a useful corrective. The paper demonstrates that the hard part of an enterprise workflow may not be dividing work across agents at all, but constraining whatever agent exists. The Deal Desk should not assume more agents equals more safety.

## 5. Coordination and communication

The Decision Wrapper (Algorithm 1), four sequential stages:

1. **Input validation** — schema check, completeness logging
2. **Bounded LLM choice** — restricted to a closed option set; validates route, confidence score, rationale
3. **Policy guardrail** — override mode (forces the policy route) or floor mode (enforces a minimum)
4. **Deterministic fallback** — triggers if LLM output is invalid, malformed, out-of-vocabulary or incomplete

## 6. Business constraint enforcement ★

The core contribution. Formal decision tuple ⟨E, O, π, D, ϕ⟩ (Section 3.1):

- **E** — schema-valid case space
- **O** — closed, **ordered** set of admissible options, ordered by conservativeness
- **π** — LLM policy (partial function; may return an invalid marker ⊥)
- **D** — deterministic fallback (total function, always valid)
- **ϕ** — guardrail specification, mode μ ∈ {none, override, floor}

Governing logic (Eq. 2): invalid LLM output → fallback D(e); override mode → forced policy route; floor mode → **max(π(e), r_floor(e))**, the more conservative of the two; no guardrail → accept the LLM output.

**Floor-safety property (Eq. 3):** `g(e) ⪰ r_floor(e)` — for every schema-valid case the executed route is never less conservative than the policy minimum. Guaranteed **by architecture, not by model behaviour**.

Concrete instance: option set {standard ≺ enhanced ≺ human_approval_required}; the floor forces `human_approval_required` when high data access combines with managerial seniority or contractor engagement.

**Thesis interpretation.** Ordering the option set by conservativeness is what makes "take the maximum" meaningful. A Deal Desk would need the same: discount tiers, credit-risk bands and approval levels each ordered so that a floor can be defined.

## 7. Tools / system interaction

Execution layer performs deterministic provisioning actions. No CRM, CPQ or ERP integration. Append-only audit log at the governance layer.

## 8. Business domain & data realism ★

Employee onboarding — a genuine regulated HR process with real compliance obligations. 166 structured profiles with explicit human-in-the-loop ground truth, 43 of them requiring mandatory approval.

Structured data only; no free-text fields. Realistic as a compliance-routing process, but the authors are explicit that free-text exposure (and therefore prompt injection) was out of scope.

## 9. Methodology

Three configurations: deterministic baseline (no LLM); ungoverned LLM (no guardrails, policies or fallback); governed LLM with floor guardrail.

Two local models: **Qwen2.5** and **llama3.1**.

Three routing decisions in the process: work mode (override mode), role profile (unguarded), compliance level (floor mode — the focus).

Metrics: HITL recall, HITL precision, overall accuracy, inter-run stability, baseline–LLM agreement, guardrail activation frequency, fallback usage.

## 10. Evaluation and reported results

Sensitive cases, n = 43 mandatory escalations:

| Configuration | Recall | Precision |
|---|---|---|
| Deterministic baseline | 1.0 | 1.0 |
| Ungoverned Qwen2.5 | **0.0** | N/A |
| Ungoverned llama3.1 | 1.0 | 0.81 |
| Governed Qwen2.5 (floor) | **1.0** | 1.0 |
| Governed llama3.1 (floor) | 1.0 | 0.84 |

**The accuracy paradox.** Ungoverned Qwen2.5 scored **0.74 overall accuracy across all 166 profiles while achieving 0.0 recall on the safety-critical subset.**

Inter-run stability (Qwen2.5, compliance decision): ungoverned **0.73** → governed **1.0**.

Within-run natural experiment, same ungoverned run: the guarded decision (work mode, override) reached **1.00 agreement / 1.00 stability**, while the unguarded compliance decision reached **0.11 agreement** with major drift.

Guardrail activation: floor triggered on all 43 compliance-critical cases for Qwen2.5.

## 11. Findings

1. An LLM can articulate risk in its rationale and still route below the mandated level.
2. Architectural governance restores full recall without sacrificing precision.
3. Aggregate accuracy is an unsafe metric for compliance-critical decisions.
4. Guardrails stabilise decisions across runs, not only correct them.
5. Two models failed in **opposite directions** — neither behaviour is a property of "LLMs" but of a particular model.
6. Governance must sit in the architecture; prompt-level instruction was insufficient.

## 12. Observed failure modes ★

**Ungoverned Qwen2.5 — silent under-escalation.** Identified elevated risk in its generated rationale, then selected `standard` or `enhanced` instead of `human_approval_required`. All 43 mandatory escalations missed; invisible until audit.

**Ungoverned llama3.1 — over-escalation.** Full recall but unnecessary escalations, precision 0.81.

**Thesis interpretation.** The opposite-direction failures are the more useful result. A deal-approval system faces both risks. Any Deal Desk evaluation must report precision and recall separately per decision, never a single accuracy figure.

## 13. Limitations

The guarantee is **local**, assuming validated structured inputs and a trusted policy knowledge base.

Explicitly out of scope: input corruption or poisoning; policy errors; extraction failures upstream; prompt injection in free-text fields; downstream tool misuse; end-to-end workflow correctness; global system safety.

Empirical: single process; two-model proof of concept; structured data only; dataset-specific.

Architectural: assumes downstream execution is correct; does not prevent over-reliance; requires explicitly formalised policy rules.

## 14. Enterprise relevance

Strong and direct. An industrially grounded process evaluated with partner-validated synthetic profiles, a formal safety property, an audit log, and quantified consequences of removing governance.

## 15. Deal Desk relevance

| B1 concept | Deal Desk mapping |
|---|---|
| Ordered option set O | Discount tiers / credit bands / approval levels, ordered by conservativeness |
| Policy floor r_floor | Minimum approval level for a given deal risk profile |
| Override mode | Rules with no LLM discretion at all (hard price floor) |
| Floor mode | Rules where the LLM may be more cautious but never less |
| Deterministic fallback D | Safe routing when an agent fails or returns malformed output |
| Cognitive layer proposes only | Agents recommend; the orchestrator executes |
| Append-only audit log | Deal decision audit trail |

All **thesis interpretations**.

## 16. Evidence locations

| Topic | Section |
|---|---|
| Problem formulation & literature gap | 2.6 |
| Decision space & ordering | 3.1.1 |
| Policies & guardrail modes | 3.1.2 |
| Governed decision function | 3.1.3 |
| Floor-safety property | 3.1.4 |
| Threat model & scope | 3.1.5 |
| Case study: onboarding | 3.2 |
| Architecture overview | 3.3 |
| Decision wrapper algorithm | 3.3.1 |
| Experimental results | 4 |
| Failure modes | 4 and 5 |
| Auditability & automation bias | 5 |
| Limitations & future work | 5 and 6 |

## 17. Potential gap evidence

Single process, two models, structured input only, local guarantee. A Deal Desk spanning **several** governed decisions with interacting floors is outside anything demonstrated here.

---

# B6 — Agentic LLMs in the supply chain: towards autonomous multi-agent consensus-seeking

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Valeria Jannelli, Stefan Schöpf, Matthias Bickel, Torbjørn H. Netland, Alexandra Brintrup |
| Venue | *International Journal of Production Research* — Taylor & Francis |
| Year | 2025, advance online publication |
| DOI | 10.1080/00207543.2025.2604311 |
| Peer review | Peer-reviewed journal article |
| Preprint | arXiv:2411.10184 — **cite the journal DOI** |
| Research type | Framework + simulation case study |
| Thesis relevance | **High** — inventory, and coordination-design evidence |

## 2. Problem and objectives

Supply chain coordination requires agreement on **inventory levels and delivery times**. Poor consensus produces the **bullwhip effect**. Existing automated coordination has high entry barriers that lock out SMEs, limited capability and poor adaptability.

## 3. Architecture

LLM agents at different supply chain echelons (Section 4). Modular framework integrating **perception, memory and execution**.

Each agent: perceives local state (inventory, backlog, orders, downstream demand) → holds memory of the previous **10 observations** → makes a tentative independent decision → communicates with immediate neighbours (upstream only, §4.2) → executes a final action.

## 4. Agent responsibilities

Agents are **homogeneous by role, differentiated by position**. No planner/critic/executor split.

**Thesis interpretation.** A second architectural pattern distinct from every orchestration paper: specialisation by *position in a process* rather than by *function*. B2's segregation-of-duties argument favours function; this paper shows position-based is viable.

## 5. Coordination and communication ★

Five frameworks of increasing sophistication (§4.2.1):

1. **Standalone** — no communication
2. **Information sharing** — agents enrich decisions with neighbour data
3. **Standalone + tools** — computational outputs embedded in prompts
4. **Information sharing + tools** — combined
5. **Negotiation + tools** — tool outputs become **upper and lower bounds for a negotiation range**, iterating up to 3 rounds

## 6. Business constraint enforcement ★

Softer than B1. Constraints enter as **negotiation bounds derived from tools** (linear regression for costs, EOQ for order quantity), not as a hard guarantee.

**Thesis interpretation.** B1 and B6 sit at two points on the constraint spectrum — hard architectural floor versus soft tool-derived bounds. The Deal Desk will likely need both.

## 7. Tools / system interaction

Linear regression (cost estimation) and EOQ (order quantity). Simulation environment, not a live ERP. Code open-sourced.

## 8. Business domain & data realism ★

Three-echelon sequential supply chain, lead time 2 steps, max order 100 units, customer demand from a **Merton Jump Diffusion** process (0–20 units/period), 52 periods, temperature 0.1.

## 9. Methodology

Two objectives: global cost minimisation and bullwhip reduction (coefficient of variation < 1). Baselines — weak: (S,s) = (100,60) restocking; strong: pure tool execution. Models: **Gemini Flash** and **Gemini Pro**.

## 10. Evaluation and reported results

**Cost minimisation (Gemini Flash), relative improvements:**

- Standalone + tool: **63.5%** reduction vs standalone
- Information sharing: **92.8%** reduction vs standalone
- Information sharing + tool: **67.9%** reduction
- Negotiation + tool: **50.7%** reduction vs information sharing + tool
- Best absolute: **12,790** cumulative cost (negotiation + tool)

**Bullwhip (CV < 1 to pass):**

| Framework | Flash | Pro |
|---|---|---|
| Standalone | pass | fail |
| Standalone + EOQ tool | fail | fail |
| Information sharing | pass | pass |
| Info sharing + EOQ tool | pass | pass |
| Negotiation + EOQ tool | pass (0.507) | pass (0.258) |

Negotiation gave a **66.2%** bullwhip reduction over information-sharing-with-tool for Gemini Pro. Performance **"can vary non-monotonically with model size"** (§6.1.2).

## 11. Findings

1. Communication alone produced the largest cost improvement — **92.8%**.
2. Negotiation gave the best absolute cost and bullwhip control.
3. A tool without communication **made bullwhip worse**.
4. Bigger model ≠ better.
5. Tool outputs work well as negotiation bounds.
6. Agents reach near-human-level consensus at scale.

**Thesis interpretation.** Finding 4 corroborates SGT's non-monotonic result and B5's Coordination Primacy Hypothesis. This does not rebut C007. Instead, the combined evidence establishes a boundary condition: collaboration can help under suitable coordination and task structure, but a capable single agent may outperform a multi-agent system when coordination adds unnecessary overhead.

## 12. Observed failure modes ★

1. **Tool misuse** — EOQ tool without communication worsened bullwhip.
2. **Agent stubbornness** — downstream agents dominated; upstream agents became *"suggestible."*
3. **Format errors** — malformed outputs (§5.2).
4. **Model inconsistency** — larger models not reliably better.
5. **Total disagreement** — negotiations sometimes failed to converge (Appendix E1).

**Thesis interpretation.** Agent stubbornness is the most transferable failure — an independent argument for B1-style hard floors over B6-style negotiation on anything risk-bearing.

## 13. Limitations

Unstable across foundation models; heavy prompt optimisation needed; human oversight still required; scalability O(n)/O(m·n); **memory restricted to current step**; tested only on 3-echelon chains; explicitly *"still far from autonomous LLM-powered supply chains."*

## 14. Enterprise relevance

Real operations-management problem with standard metrics. The memory limitation is directly relevant: a deal moving through stages needs persistent state, which this framework lacks and ChatDev's long-term memory provides.

## 15. Deal Desk relevance

| B6 concept | Deal Desk mapping |
|---|---|
| Echelon agents | Stage-based rather than function-based agents |
| Information sharing | Agents see each other's findings before deciding |
| Tool-bounded negotiation | LLM negotiates within calculated limits |
| Bullwhip effect | Amplified error propagating through a deal |
| Agent stubbornness | One specialist dominating another |
| Memory of last 10 observations | Deal state window |

All **thesis interpretations**.

## 16. Evidence locations

| Topic | Section |
|---|---|
| Architecture | 4 |
| Modular perception/memory/execution | 4.2 |
| Five consensus frameworks | 4.2.1 |
| Case study setup | 5, Table F1 |
| Format errors | 5.2 |
| Results | 6, Tables D1–D2 |
| Non-monotonic model size | 6.1.2 |
| Coordination failures | 6.2.1, Appendix E |
| Bullwhip results | 6.2.2 |
| Limitations | 7.1, 8 |

## 17. Potential gap evidence

No persistent cross-step memory; only 3 echelons; homogeneous agents; simulation only; soft bounds; human oversight still required.

---

# B3 — Conversing with business process-aware large language models: the BPLLM framework

> **Verification completed 24 September 2026:** Table 4 confirms 92.31% for Food Delivery alone, 84.62% for Food Delivery with Reimbursement, and 80.53% for Food Delivery with E-commerce under int4 fine-tuning. The authors associate the larger decline with similarities in activity names, but this remains study-specific rather than a universal causal law.

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Mario Luca Bernardi, Angelo Casciani, Marta Cimitile, Andrea Marrella |
| Venue | *Journal of Intelligent Information Systems* 62 — Springer |
| Year | 2024 (received 18 Mar, accepted 29 Sep, published online 4 Oct) |
| DOI | 10.1007/s10844-024-00898-1 |
| Peer review | Peer-reviewed journal article |
| Research type | Framework + empirical evaluation |
| Thesis relevance | **Medium-high** — process knowledge representation, and a rare case with negative results reported |

## 2. Problem and objectives

Process-aware Decision Support Systems (DSSs) assist workers during process execution, but the authors state plainly that **empirical validation of LLMs for process-aware decision support is scarce in the literature** — this is itself a small, explicit gap statement worth citing directly.

BPLLM couples **Retrieval-Augmented Generation with fine-tuning** to enrich process-specific knowledge, plus a **process-aware chunking** approach.

Four research questions drive the whole evaluation:
- **RQ1** — does RAG improve end-to-end performance over a base LLM?
- **RQ2** — what is the influence of chunking and prompting?
- **RQ3** — how does process representation format (natural text vs BPMN) and embedding model choice affect performance?
- **RQ4** — what is the effect of fine-tuning, and does knowledge-base size (number of processes) affect performance?

## 3. Architecture

Three-phase pipeline (Fig. 2), built on **LangChain**:

1. **RAG Knowledge Augmentation (offline)** — chunking → embedding → storing in a vector index
2. **LLM Fine-tuning (offline)** — supervised fine-tuning on a BP-specific dataset
3. **RAG Querying (online)** — retrieval → answering

**Chunking (§4.1.1).** Two families tested: fixed-size and recursive chunking for a natural-language DFG description, and the same two plus a custom **BPMN-specific chunking** technique that parses BPMN XML tags directly (splitting on `<task>`, `<exclusiveGateway>`, `<sendTask>` etc.) so chunks stay semantically self-contained rather than being cut arbitrarily.

**Embedding (§4.1.2).** Best performer overall: `all-MiniLM-L6-v2`. Vector store: **qDrant**, cosine similarity, gRPC.

**Fine-tuning (§4.2).** PEFT via HuggingFace AutoTrain Advanced, fine-tuning **Llama 3.1 8B** in a supervised fashion on process-specific question/binary-answer pairs distinguishing *structural* information (presence of activities/events/gateways) from *behavioral* information (sequence flows between them).

## 4. Agent responsibilities

Not a multi-agent system — a single LLM pipeline. No agent decomposition.

**Thesis interpretation.** A useful negative case for the thesis's "what counts as an agent" discussion (raised also by B1): sophisticated process-aware behaviour does not require multiple agents. It can come entirely from how one model is grounded and fine-tuned.

## 5. Coordination and communication

N/A — single-model pipeline, no inter-agent communication.

## 6. Business constraint enforcement

None. This system answers factual yes/no questions about a process model; it does not enforce or route decisions. Distinguishes it from B1 sharply — this is a **knowledge-grounding** paper, not a **governance** paper.

## 7. Tools / system interaction

Considered two process representations: **natural-language DFG** and **BPMN** (industry-standard notation, OMG). Evaluated on three real process types: **Food Delivery**, **E-commerce**, **Reimbursement** (an expense-approval process with a threshold-based approval gate — directly relevant to Deal Desk approval logic).

## 8. Business domain & data realism ★

Three plausible, if simplified, business processes. The Reimbursement process specifically models an **approval threshold**: below a threshold amount, auto-approved; above it, a manager evaluates it. This is architecturally close to what a Deal Desk discount-approval gate would need, though the paper evaluates only whether the LLM can *describe* the model correctly — not whether it enforces the threshold in execution.

## 9. Methodology

Oracle-based evaluation: the oracle holds the question and expected binary answer, compares it to the LLM's response, and computes accuracy as percent correct. Both structural checks (activity presence) and behavioral checks (sequence-flow presence) tested, including deliberately false activities/flows not in the model, to test for hallucination as well as recall.

## 10. Evaluation and reported results — all four RQs, full numbers

**RQ1 — RAG vs pure LLM** (Table 1, Llama 2 13B, Food Delivery):

| Methodology | Representation | Accuracy |
|---|---|---|
| Pure LLM | None | 42.78% |
| RAG | Natural Text | **65.48%** |
| RAG | BPMN | 60.57% |

A pure LLM with no retrieval scored barely above chance. The authors explicitly note **hallucination**: the pure LLM claimed familiarity with activities it had no knowledge of.

**RQ2 — chunking and prompting** (Table 2, Llama 2 13B):

Natural text: no-chunking, fixed and recursive chunking all land close together (~55–67%), because the process description is small enough to fit near-whole in one chunk anyway.

BPMN: chunking strategy matters far more, because the BPMN file is larger:

| Chunking | Prompt | Accuracy |
|---|---|---|
| No chunking | Not refined | 60.57% |
| No chunking | Refined | 64.86% |
| Fixed | Refined | 73.53% |
| Recursive | Refined | 73.53% |
| **BPMN-specific** | Refined | **76.47%** |

Refined prompts beat unrefined prompts in every single row. BPMN-specific chunking is the best chunking strategy for the BPMN representation.

Model comparison at the best chunking configuration (BPMN-specific, refined prompt):

| Model | Accuracy |
|---|---|
| Llama 2 13B | 76.47% |
| Llama 2 7B | 68.47% |
| Llama 3 8B Instruct | 89.78% |
| **Llama 3.1 8B Instruct** | **90.38%** |
| Mistral 7B Instruct v0.2 | 88.85% |
| Mistral 7B Instruct v0.3 | 90.18% |
| Mixtral 8x7B Instruct | 79.81% |

The authors explicitly tested for an **inverse scaling** effect (does a smaller model sometimes beat a larger one?) by trying Llama 2 7B — it did not outperform 13B here, so inverse scaling did not hold in this instance, though the authors raise it as a real possibility worth testing per task.

**RQ3 — representation format and embedding model** (Table 3):

| Representation | Embedding model | Accuracy |
|---|---|---|
| Natural Text | all-MiniLM-L6-v2 | 87.50% |
| Natural Text | paraphrase-xlm-r-multilingual-v1 | 85.58% |
| Natural Text | bert-finetuned-bpmn | 87.88% |
| BPMN | all-MiniLM-L6-v2 | **90.38%** |
| BPMN | paraphrase-xlm-r-multilingual-v1 | 90.20% |
| BPMN | bert-finetuned-bpmn | 69.23% |

Note the reversal: a BPMN-specific fine-tuned embedding model (`bert-finetuned-bpmn`) is *best* for natural text but *worst* for BPMN. Embedding-model choice is not transferable across representation formats — it must be matched to the input type.

**RQ4 — fine-tuning and knowledge-base scaling** (Table 4):

| Process(es) | Fine-tuned | Quantization | Accuracy |
|---|---|---|---|
| Food Delivery | Yes | int4 | **92.31%** |
| Food Delivery | Yes | int8 | 90.58% |
| Food Delivery + Reimbursement | No | — | 82.16% |
| Food Delivery + Reimbursement | Yes | int4 | 84.62% |
| Food Delivery + Reimbursement | Yes | int8 | 81.87% |
| Food Delivery + E-commerce | No | — | 80.26% |
| Food Delivery + E-commerce | Yes | int4 | 80.53% |

Fine-tuning on a single process (92.31%) beats the best RAG-only configuration (90.38%) — a real, if modest, gain. **int4 quantization outperformed int8** — cheaper and more accurate.

**Critical finding for the thesis: adding a second process to the knowledge base *hurt* accuracy** (92.31% → 82–85%), and the drop was **worse when the two processes had similar activity names** (Food Delivery + E-commerce, both delivery-style processes, ~80%) than when they were dissimilar (Food Delivery + Reimbursement, ~82–85%). The LLM confused near-synonymous activity names across processes ("Select Rider" vs "Select Courier").

## 11. Findings

1. RAG substantially outperforms a pure LLM and reduces hallucination (42.78% → 65.48%).
2. Domain-specific chunking (BPMN-specific) materially outperforms generic chunking (76.47% vs ~65–68%).
3. Prompt refinement improves accuracy in every configuration tested.
4. Embedding-model choice must match the representation format — no universal best embedding model.
5. Fine-tuning on a single process gives the best result overall (92.31%), beating RAG alone.
6. **Scaling the knowledge base to multiple processes reduces accuracy**, especially when processes share similar vocabulary.
7. int4 quantization is both cheaper and more accurate than int8 here.

**Thesis interpretation.** Finding 6 is an important risk signal for the thesis. A Deal Desk generalist would combine pricing, credit and approval policies that share terms such as discount, threshold, approval and limit. B3 motivates testing whether scoped retrieval and specialist boundaries reduce this interference, but it does not prove that multiple agents are universally superior. Retrieval configuration, context load, vocabulary overlap and evaluation design are plausible alternative explanations.

## 12. Observed failure modes ★

**Hallucination under no retrieval.** The pure LLM claimed knowledge of activities absent from the process model (RQ1).

**Cross-process confusion.** When two processes shared similar activity names, the LLM's answers degraded measurably — a concrete instance of knowledge interference (RQ4).

**Embedding mismatch.** Using a BPMN-tuned embedding model on natural-text input (or vice versa) sharply hurt accuracy (69.23% vs a possible ~88%) — evidence that a mismatched retrieval component silently damages system quality rather than failing loudly.

## 13. Limitations

The paper's own stated limitations are not exhaustively listed in the introduction, but the study design reveals them directly: single-domain evaluation (three processes only, all business-workflow examples, none enterprise-scale); binary yes/no question format only, not open-ended reasoning about the process; oracle-based accuracy only, no live deployment or user study reported in the main results discussed here; and the explicit finding that knowledge-base scaling degrades performance is presented as a result rather than resolved.

## 14. Enterprise relevance

Directly useful. The Reimbursement process is architecturally an approval-threshold gate, close to what the Deal Desk needs. The paper demonstrates concretely how an agent is grounded in the *actual* text of an organisation's process definitions rather than reasoning generically — the missing piece behind B1's "trusted policy knowledge base" assumption, which B1 itself does not explain how to build.

## 15. Deal Desk relevance

| B3 concept | Deal Desk mapping |
|---|---|
| BPMN-specific chunking | Parsing the actual approval-workflow definition, not a plain-text summary |
| Process-aware RAG | How a Deal Desk agent is grounded in the real discount/credit/approval policy documents |
| Fine-tuning on one process | Specialised, single-domain agent knowledge |
| Knowledge-base scaling degradation | Direct evidence *against* one generalist agent holding all deal knowledge |
| Reimbursement threshold gate | Structural analogue of a discount/deal approval threshold |
| int4 outperforming int8 | Small, efficient models can be the right choice per agent — relevant to the orchestration literature's cost concerns |

All **thesis interpretations** except the numeric results themselves.

## 16. Evidence locations

| Topic | Section |
|---|---|
| Research questions | 1 |
| Related work / stated literature gap | 2 |
| BPMN background | 3.1 |
| RAG / fine-tuning background | 3.2 |
| Architecture (3-phase pipeline) | 4 |
| Chunking, incl. BPMN-specific technique | 4.1.1 |
| Embedding | 4.1.2 |
| Vector storage | 4.1.3 |
| Fine-tuning | 4.2 |
| RAG querying | 4.3 |
| Process models used | 5.1 |
| RQ1 results (Table 1) | 5, RQ1 |
| RQ2 results (Table 2) | 5, RQ2 |
| RQ3 results (Table 3) | 5, RQ3 |
| RQ4 results (Table 4) | 5, RQ4 |

## 17. Potential gap evidence

No enterprise-scale knowledge base tested (only 2–3 processes at once, and performance already degraded at 2). No live execution or enforcement — this system answers questions about a process, it does not run one. No multi-agent structure — a natural next step the paper does not take, which the thesis can.

---

# B4 — Interpretable LLMs for credit risk: A systematic review and taxonomy

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Muhammed Golec (Boğaziçi University), Maha Alabduljalil (Kuwait University) |
| Venue | *Expert Systems With Applications* 306, article 130941 — Elsevier |
| Year | 2026 (received 10 Jun 2025, accepted 20 Dec 2025, online 24 Dec 2025) |
| DOI | 10.1016/j.eswa.2025.130941 |
| Peer review | Peer-reviewed journal article |
| Research type | PRISMA systematic review + taxonomy |
| Thesis relevance | **Medium-high** — credit domain grounding, and directly citable research gaps |

## 2. Problem and objectives

The authors state plainly: **no LLM-specific, interpretability-focused taxonomy of credit risk research exists.** Prior surveys fall into three clusters, all insufficient for the thesis's purpose:

- **Domain-general finance/LLM overviews** — describe LLMs in finance broadly, but not credit-specific and shallow on interpretability.
- **Financial-NLP/FinLLM surveys** — financial-NLP-focused, not credit-focused.
- **Credit risk/ML surveys** — credit-focused, but pre-LLM: traditional ML/statistical methods only, no transformer-based architectures.

The paper's stated contribution: a four-pillar taxonomy (model architecture, data modality, interpretability mechanism, application domain) that is simultaneously credit-specific, LLM-specific, and interpretability-focused — no prior survey is all three at once (their own comparison Table 1 makes this explicit against ~19 named prior surveys).

## 3–4. Architecture / agent responsibilities

**N/A — review paper**, no system of its own.

## 9. Methodology — full PRISMA protocol

Databases searched: **IEEE Xplore, Elsevier, ACM Digital Library, SpringerLink, Scopus, arXiv**, 2020–2025. Explicit exclusions: finance-focused repositories like SSRN and NBER were *not* searched (acknowledged limitation), and foundational pre-LLM work like FinBERT (2019) was excluded from inclusion by design.

Five keyword search strings used (Table 2), covering: LLM/credit-scoring terms; LLM + explainability + financial NLP; credit risk + multimodal/unstructured/behavioral data; LLM + evaluation/benchmark; fairness/bias/hallucination/reproducibility + LLM/credit risk.

**PRISMA funnel:** 182 papers found → 120 after dedup and relevance filtering → 51 after full inclusion criteria → **60 final papers** after snowball sampling.

Inclusion criteria: (i) peer-reviewed or preprint, (ii) LLM/transformer-based, (iii) credit-risk-task focused, (iv) full text in English.

Exclusions at eligibility stage: not credit risk (n=28), not LLM (n=21), no interpretability (n=6), no full text (n=4).

Quality/bias assessment: a binary Yes/No checklist across dataset transparency, reproducibility, interpretability mechanism, neutrality, robustness testing, publication type — applied to all 60 papers.

## 10. Taxonomy — four RQs

- **RQ1 (model architectures)** — encoder-only (RoBERTa, DistilBERT, FinBERT), decoder-only, hybrid, domain-specific FinLLMs, parameter-efficient LLMs.
- **RQ2 (data modalities)** — structured tabular vs unstructured text vs multimodal.
- **RQ3 (interpretability mechanisms)** — post-hoc methods (SHAP, attention maps), chain-of-thought prompting, natural-language justification, causal/counterfactual reasoning.
- **RQ4 (application domains)** — retail credit scoring, SME credit scoring, and related financial scenarios.

## 11. Findings — quantified gaps, not just described

This is the section that matters most for the thesis. The authors quantify how thin the evidence base actually is:

- Only **9 of 60 studies** report robustness tests (adversarial/stress testing).
- Only **12 of 60** include a fairness/bias check.
- Only **7 of 60** report efficiency metrics (latency, cost, energy).
- Only **3 of 60** use causal or counterfactual reasoning techniques — nearly all interpretability in the field is post-hoc (SHAP-style), not causal.
- Most studies use small datasets, limiting external validity; several lack standardized train/test splits.

## 12. Observed failure modes ★

**Interpretability is post-hoc, not causal.** The literature overwhelmingly explains model decisions after the fact rather than reasoning transparently, which the authors say makes it "difficult to understand the true decision-making mechanism" in credit scenarios.

**Bias against protected characteristics.** The literature reports LLM bias by race, gender and age in credit-relevant outputs.

**Hallucination risk specific to credit.** LLMs can produce false information that is "very close to the truth" — a distinctly dangerous failure mode for a domain where a wrong but plausible-sounding number or justification can pass unnoticed.

**Efficiency is essentially unmeasured.** Only 7/60 papers report runtime/cost data at all, meaning most published credit-LLM systems have no evidence of whether they are practically deployable.

## 13. Limitations

Explicitly acknowledged by the authors: SSRN/NBER excluded from search (may under-represent working papers); benchmark fragmentation makes cross-study comparison difficult (no standardized dataset splits across most of the 60 studies); most studies too small-scale for strong external validity claims.

## 14. Enterprise relevance

Directly maps onto the Deal Desk's credit-agent requirement. The regulatory framing matters specifically: the authors tie future work to **Basel Accords and the EU AI Act**, i.e. explainability in credit is not a nice-to-have but a compliance requirement in regulated markets — reinforcing B1's point that some Deal Desk decisions need hard, auditable justification, not just a plausible-sounding one.

## 15. Deal Desk relevance

| B4 concept | Deal Desk mapping |
|---|---|
| Post-hoc vs causal interpretability | The credit agent's justification must be auditable, not just plausible |
| Bias findings | A Deal Desk credit agent needs bias/fairness checking before deployment, not just accuracy |
| Efficiency measurement gap (7/60) | Latency and cost of a credit-check agent should be measured explicitly, not assumed |
| Regulatory alignment (Basel, EU AI Act) | The credit agent may face real compliance obligations, giving a concrete external reason for B1-style hard constraints on this specific agent |

All **thesis interpretations**.

## 16. Evidence locations

| Topic | Section |
|---|---|
| Stated literature gap & survey comparison (Table 1) | 2, 2.4 |
| PRISMA protocol & search strings (Table 2) | 3.1 |
| Quality/bias assessment | 3.2 |
| Research questions | 3.3 |
| Taxonomy — model architectures (RQ1) | 4.1 |
| Full list of 60 papers (Table 3) | 4 |
| Research gaps — methodological (RQ5) | 5.1 |
| Research gaps — application-oriented | 5.2 |
| Future directions | 5.3 |

## 17. Potential gap evidence ★ — the paper's own stated research gaps (RQ5), directly citable

**Methodological gaps:**
- **Interpretability gap** — near-total reliance on post-hoc methods; causal/counterfactual reasoning used in only 3/60 studies.
- **Reproducibility and robustness gap** — only 9/60 report robustness testing; small datasets dominate; inconsistent train/test splitting across the field.
- **Bias, fairness and hallucination risk** — documented but under-addressed; few frameworks specifically target fairness or hallucination reduction in credit.
- **Efficiency/scaling gap** — only 7/60 report runtime, cost or energy metrics at all.
- **Evaluation benchmark fragmentation** — no standard benchmark exists across studies, making comparison difficult.

**Application-oriented gap:**
- **Behavioral/external signal integration** — repayment-pattern and sentiment signals remain theoretically promising but rarely integrated in practice.

**Future directions the authors name explicitly:** low-cost/edge-ready credit models; behavioral and sentiment-driven credit signals; domain-specific personalisation across sectors/regions; evaluation frameworks beyond raw accuracy (fairness audits, hallucination stress tests); regulatory alignment with Basel and the EU AI Act.

**Thesis interpretation.** The efficiency gap (7/60) and the evaluation-beyond-accuracy call are the two points that connect most directly to the orchestration side of the review (Zhu et al.) and to B1's accuracy-paradox finding. Now reinforced by B7 from a top-tier venue.

---

# B7 — Evaluation and Benchmarking of LLM Agents: A Survey

> **Final-draft verification flag:** recheck the exact wording and section locations for RBAC, approval workflows, policy/compliance constraints and the quoted “deemed correct” sentence in the ACM PDF before final submission.

**Status: full text, verified. Replaces B5 as the primary evaluation source.**

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Mahmoud Mohammadi, Yipeng Li, Jane Lo, Wendy Yip — all **SAP Labs** (Bellevue WA and Palo Alto CA) |
| Venue | *Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining, V.2* (KDD '25), Toronto, 3–7 August 2025 |
| Year | 2025 |
| Pages | 6129–6139 (11 pages) |
| DOI | 10.1145/3711896.3736570 |
| ISBN | 979-8-4007-1454-2 |
| Licence | **CC BY 4.0 — open access**, no paywall |
| Peer review | Peer-reviewed conference proceedings. **ACM SIGKDD is a top-tier venue** (CORE A*, the flagship data-mining conference). |
| Research type | Systematic survey + two-dimensional taxonomy |
| Thesis relevance | **Very high** — supplies the thesis's evaluation framework and independent enterprise-constraint evidence |

⚠ **Citation-order note.** The PDF's title block splits the author names across two columns, which makes Mohammadi and Lo appear first. The paper's own ACM Reference Format (page 1) gives the canonical order: **Mohammadi, Li, Lo, and Yip**. Cite in that order. *(Same class of error as the Dang et al. author-order problem on the orchestration side — check the reference format block, not the title layout.)*

**Why this matters for provenance.** All four authors are at SAP Labs — a major ERP vendor. The enterprise-specific claims in Section 5 come from people who build enterprise software, which is exactly the perspective the review was missing, and it is peer-reviewed rather than vendor marketing.

## 2. Problem and objectives

The authors' stated problem: evaluating LLM agents "remains a complex and underdeveloped area." Two specific deficiencies in the existing literature are named:

1. **Existing surveys are too narrow** — they "focus narrowly on LLM evaluation or cover specific agent capabilities without a holistic perspective."
2. **Enterprise requirements are largely absent** — secure data access, reliability for audit and compliance, and complex interaction patterns are "rarely addressed in the existing literature."

Their framing analogy is useful and quotable: *"LLM evaluation is like examining the performance of an engine. In contrast, agent evaluation assesses a car's performance comprehensively, as well as under various driving conditions."*

They also distinguish agent evaluation from classical software testing: software testing assumes deterministic, static behaviour; LLM agents are "inherently probabilistic and behave dynamically."

Two stated contributions: (i) the taxonomy, (ii) the enterprise-specific challenges.

## 3–4. Architecture / agent responsibilities

**N/A — survey paper**, no system of its own.

## 5. Coordination and communication

N/A as a system property. But the survey **does** treat multi-agent collaboration as an evaluation target (§3.2.4), which is the part the thesis needs — see field 10.

## 6. Business constraint enforcement ★

This is where B7 partially covers what B2 was wanted for. The paper does not propose an enforcement mechanism, but it documents the enterprise constraint classes that agents must respect and that evaluation must therefore test:

**§5.1 Role-Based Access Control (RBAC).** "Users operate with varying levels of access depending on their roles, and agents acting on their behalf must adhere to the same constraints." An agent's ability to retrieve or act "is not uniform but contextually bound to the user's permissions." Cites **IntellAgent** as a framework that embeds authentication and cross-user access denial directly into task generation.

**§5.4 Domain-specific policies and compliance.** Names the constraint types explicitly: *"approval workflows, data retention policies, usage quotas, and legal regulations like GDPR or HIPAA."* Evaluating agents here "requires more than measuring task success; it demands verification that agent behaviors align with formal policy constraints." Cites **TheAgentCompany**, which evaluates enterprise agents under structured correctness constraints requiring adherence to predefined organizational policies.

**Thesis interpretation.** RBAC is segregation of duties expressed as an access-control problem rather than a task-distribution problem. B2 (unread) argues duties should be split *across agents*; B7 argues each agent's *permissions* must be bound to the acting user's role. These are complementary, not competing. The Deal Desk arguably needs both — and B7 is the peer-reviewed, readable source for half of it.

## 7. Tools / system interaction

Covers tool use as an evaluated capability (§3.2.1) with concrete metrics: Invocation Accuracy, Tool Selection Accuracy, Retrieval Accuracy, MRR, NDCG, parameter-name F1. Notes that AST-based validation "may miss semantic errors, such as incorrect or hallucinated parameter values," and that Gorilla-style **execution-based evaluation** is the more grounded alternative.

Names evaluation tooling: DeepEval, InspectAI, Phoenix, GALILEO, OpenAI Evals; platforms Azure AI Foundry, Google Vertex AI, **LangGraph**, Amazon Bedrock.

**Thesis interpretation.** LangGraph appearing in a peer-reviewed KDD survey as an agent platform with evaluation features is a small but usable citation for the Phase1B toolkit decision, which was otherwise justified only by documentation.

## 8. Business domain & data realism ★

Not domain-specific by design — the survey spans coding, web, finance and healthcare benchmarks. The enterprise realism is concentrated in §5, which is framed as what current benchmarks *fail* to capture rather than what they do.

Finance appears repeatedly as a worked example: biased loan approvals and investment strategies (§3.4.1, citing FinCon and AutoGuide), a finance chatbot that "must not disclose confidential information" (§3.4.3).

## 9. Methodology

Survey, organised around a **two-dimensional taxonomy** (Fig. 1). Not PRISMA — no screening funnel is reported, which is a genuine methodological weakness relative to B4. Treat it as an expert-organised taxonomy rather than a systematic review in the strict sense.

## 10. Evaluation and reported results — the taxonomy

### Dimension 1 — Evaluation Objectives (*what* to evaluate)

| Category | Sub-dimension | Representative metrics |
|---|---|---|
| **Agent Behavior** (outcome-oriented) | Task completion | Success Rate, Task Goal Completion, Pass Rate, pass@k, Progress Rate |
| | Output quality | Accuracy, relevance, coherence, fluency, user satisfaction |
| | Latency & cost | Time To First Token, End-to-End Request Latency, token usage, monetary cost |
| **Agent Capabilities** (process-oriented) | Tool use | Invocation Accuracy, Tool Selection Accuracy, Retrieval Accuracy, MRR, NDCG, parameter-name F1 |
| | Planning & reasoning | Node F1 (tool selection), Edge F1 / Normalized Edit Distance (sequence), Step Success Rate |
| | Memory & context retention | Factual Recall Accuracy, Consistency Score; Memory Span and Memory Forms |
| | **Multi-agent collaboration** | **Collaborative Efficiency, Information Sharing Effectiveness, Adaptive Role Switching, Reasoning Rating** |
| **Reliability** | Consistency | pass@k, and the stricter **pass^k** |
| | Robustness | Task success under perturbation; error-handling rate under injected failures |
| **Safety & Alignment** | Fairness | Awareness Coverage, Violation Rate, Transparency |
| | Harm/toxicity/bias | Adversarial robustness, prompt-injection resistance, harmfulness |
| | Compliance & privacy | Risk Awareness, **Task Completion Under Constraints** |

### Dimension 2 — Evaluation Process (*how* to evaluate)

- **Interaction mode** — static/offline (cheaper, "more prone to error propagation and generally less accurate representations of system performance") vs dynamic/online (simulators, real interactions).
- **Evaluation data** — human-annotated, synthetic, interaction-generated; domain-specific benchmarks.
- **Metrics computation** — three methods: **code-based** (deterministic, reproducible, but "typically inflexible"), **LLM-as-a-judge** (scalable, handles subjectivity; extended to Agent-as-a-Judge), **human-in-the-loop** ("the gold standard for subjective aspects… expensive, time-consuming, and challenging to scale").
- **Evaluation tooling** — frameworks, platforms, leaderboards; **Evaluation-driven Development (EDD)** and AgentOps as continuous-evaluation patterns.
- **Evaluation contexts** — controlled sandbox → mocked API → live deployment, with an explicit realism/cost/safety trade-off.

### Reported empirical point worth citing

On consistency (§5.2): the **τ-benchmark** applies the pass^k metric in retail and airline-booking domains, and "the authors show that current agents struggle with consistency." B7 reports this as a finding of the cited work, not its own experiment — cite it as such.

## 11. Findings

1. Agent evaluation is categorically harder than LLM evaluation — agents act in dynamic environments, use tools, hold memory and collaborate, so text-quality metrics are insufficient.
2. Existing surveys lack a holistic perspective; the two-dimensional taxonomy is offered to fix that.
3. **Enterprise requirements are a distinct and under-served evaluation category** — RBAC, reliability guarantees, long-horizon behaviour, and policy/compliance adherence.
4. Task completion alone gives "limited fine-grained insight into failures."
5. Offline/static evaluation is systematically less representative than dynamic evaluation.
6. Current agents struggle with consistency under the strict pass^k measure (via τ-benchmark).
7. Four future directions: holistic frameworks, more realistic settings, automated/scalable techniques, and **time- and cost-bounded evaluation protocols**.

## 12. Observed failure modes ★

The survey names failure classes the evaluation literature has found. The single most important sentence in the paper for this thesis (§5.4):

> **"Without explicit modeling of these constraints during evaluation, agents deemed 'correct' in traditional benchmarks may still fail in production due to policy violations or compliance risks."**

This is the accuracy-paradox claim stated as a general principle, from a top-tier peer-reviewed venue — where B1 demonstrated it empirically in one process.

Other named failure modes:
- **Consistency failure** — stochastic agents succeed sometimes and fail other times on identical input; "occasional success is insufficient" for production.
- **Brittleness under perturbation** — paraphrased instructions, typos, misleading context, or a changed web page structure (WebLinX) degrade task success.
- **Poor tool-failure handling** — ToolEmu-style injected API errors and null responses cause agents to break down rather than retry, switch or explain.
- **Semantic tool errors that pass syntactic checks** — hallucinated parameter values that are valid AST-wise but wrong.
- **Performance drift over long horizons** — short-episode benchmarks cannot detect it.
- **Safety bypass via coreference** — CoSafe found advanced agents tricked by ambiguous referents.

## 13. Limitations

Stated by the authors: none explicitly, which is itself a limitation of a short survey.

**Assessed here:** no PRISMA protocol or screening counts (weaker methodology than B4); 11 pages, so coverage of each sub-topic is brief; no original experiments; taxonomy is proposed but not validated against practitioners; all four authors are from a single company, so the enterprise framing reflects one vendor's view of enterprise needs.

## 14. Enterprise relevance

**The strongest in the business set, and the closest thing the review has to a ready-made evaluation chapter.** Section 5 is four enterprise challenges — RBAC, reliability guarantees, dynamic/long-horizon interaction, and policy/compliance adherence — each with cited example frameworks. It is written by enterprise-software engineers and published in a top-tier peer-reviewed venue.

## 15. Deal Desk relevance

| B7 concept | Deal Desk mapping |
|---|---|
| Two-dimensional taxonomy | Direct skeleton for the thesis's evaluation design — what to measure × how to measure it |
| Multi-agent collaboration metrics | Gives named, citable metrics for orchestration quality: Collaborative Efficiency, Information Sharing Effectiveness, Adaptive Role Switching |
| pass^k (strict consistency) | The right metric for "does the Deal Desk route this deal the same way every time?" — B1 measured this as inter-run stability without naming it |
| RBAC (§5.1) | A sales rep's agent must not see or act on data above that rep's permission level |
| "Approval workflows" named as a policy constraint (§5.4) | Peer-reviewed confirmation that approval routing is a recognised enterprise agent-evaluation problem, not a thesis invention |
| Task Completion Under Constraints | The single most appropriate headline metric for the Deal Desk — completion *and* policy adherence together |
| Latency & cost (TTFT, token cost) | Makes the cost of multi-agent orchestration an explicit evaluated dimension |
| Static vs dynamic evaluation | Justifies evaluating the Deal Desk on live simulated deals rather than a fixed test set alone |
| Code-based vs LLM-as-judge vs human | Frames the thesis's own evaluation-method choice with a citation |
| EDD / AgentOps | Justifies building evaluation into the Deal Desk from the start |
| LangGraph named as an evaluated platform | Minor supporting citation for the Phase1B toolkit choice |

All **thesis interpretations** except the taxonomy contents and the quoted sentences.

## 16. Evidence locations

| Topic | Section |
|---|---|
| Problem statement, why agent eval ≠ LLM eval | 1 |
| Stated gap in existing surveys | 1 |
| Taxonomy overview (Fig. 1) | 2 |
| Agent behavior — task completion, output quality, latency & cost | 3.1–3.1.3 |
| Tool use metrics | 3.2.1 |
| Planning & reasoning metrics | 3.2.2 |
| Memory & context retention | 3.2.3 |
| **Multi-agent collaboration metrics** | **3.2.4** |
| Consistency (pass^k) | 3.3.1 |
| Robustness | 3.3.2 |
| Fairness / harm / compliance | 3.4.1–3.4.3 |
| Static vs dynamic evaluation | 4.1.1–4.1.2 |
| Metrics computation methods | 4.3 |
| Evaluation tooling (incl. LangGraph) | 4.4 |
| Evaluation contexts | 4.5 |
| **Enterprise challenges — RBAC** | **5.1** |
| **Reliability guarantees, τ-benchmark pass^k** | **5.2** |
| Long-horizon interaction | 5.3 |
| **Policy & compliance, "approval workflows" quote** | **5.4** |
| Future directions | 6 |
| Objectives-to-metrics mapping | Table 1 |

## 17. Potential gap evidence ★

The authors' own statements, directly citable as gap evidence:

- Enterprise-specific evaluation concerns are "often overlooked in current research" and "rarely addressed in the existing literature."
- Existing surveys "focus narrowly on LLM evaluation or cover specific agent capabilities without a holistic perspective."
- Most benchmarks "focus on short episodes or single interactions" and cannot capture "performance drift, context retention, or the cumulative effect of decisions on business outcomes."
- No evaluation framework exists that is simultaneously holistic, realistic, scalable and cost-bounded — the four future directions in §6 are named precisely because none currently is.

**Thesis interpretation.** This is the cleanest available peer-reviewed statement that *evaluating* an enterprise multi-agent system against real policy constraints is an open problem. Combined with B1's empirical demonstration, RQ5 now rests on demonstration plus top-tier acknowledgement rather than on the thesis's own assertion.

---

# B2 — Multi-agent Collaboration for Business Process Automation in ERP Systems ⚠ REQUESTED FROM AUTHOR

**Abstract-level extraction only. PDF requested from the author. B2 remains uniquely valuable for multi-agent ERP segregation of duties, but it is no longer a blocker because B1+B7+B8+B9 provide a documented fallback evidence chain.**

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Jonas Schnepf, Matthias Schwarz, Bernd Scheuermann, Simon Anderer |
| Venue | IJCCI 2025 — *Communications in Computer and Information Science*, vol. 2827, Springer |
| Year | 2026 |
| Pages | 118–138 |
| DOI | 10.1007/978-3-032-15632-7_7 |
| Peer review | Peer-reviewed conference proceedings |
| Research type | Applied case study |
| Thesis relevance | **High** — closest published process analogue |

## 2. Problem and objectives

RPA cannot handle complex business processes. Existing LLM-based systems miss the benefits of multi-agent collaboration and neglect security controls, specifically **segregation of duties**.

## 3–5. Architecture / agents / coordination ⚠

Multiple LLM agents rather than a single agent, motivated by collaboration benefits including *"divergent thinking or reasoning."* **Role definitions and interaction patterns not available from the abstract — need the PDF.**

## 6. Business constraint enforcement ★ ⚠

Segregation of duties enforced by distributing process steps across agents so no single agent performs conflicting functions (authorisation, execution, approval). **Exact mechanism not available from the abstract — need the PDF.**

**Thesis interpretation.** A control-based justification for agent boundaries, categorically different from the capability-based justification in ChatDev and CAMEL, and different again from B7's permission-based (RBAC) framing. Confirm the mechanism before building on it.

## 8. Business domain & data realism ★

**Procure-to-pay** in an ERP system: purchasing, receiving, invoicing, payment. Structurally the mirror of quote-to-cash.

## 9–13. Methodology, results, failure modes, limitations ⚠

Error-driven prompt engineering reported to achieve *"consistently reliable automation."* **No metrics, scenarios or failure analysis available from the abstract. Do not cite performance claims until verified.**

## 15. Deal Desk relevance

P2P → Q2C is the closest published structural mapping available. Segregation of duties transfers directly.

**If B2 cannot be obtained:** the segregation-of-duties argument survives in weakened form through B7 §5.1 (RBAC — permission-bound agents) and B1 (architectural separation of proposal from execution). What would be lost is the only published *task-distribution* framing of duty separation across agents, and the only P2P-in-ERP case study. Record the absence explicitly in the LR rather than papering over it.

---

# B5 — Toward Reliable Evaluation of LLM-Based Financial Multi-agent Systems ⚠ SUPERSEDED IN PART

**Abstract-level extraction only. No longer critical — B7 now carries the evaluation argument from a stronger venue (ACM SIGKDD vs. a Springer LNCS chapter) and is open access.** Still worth having for its finance-specific content and the CPH framing, but it is no longer blocking.

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Phat Nguyen, Thang Pham |
| Venue | PAKDD 2026 — *Lecture Notes in Computer Science*, Springer |
| Year | 2026 (online 14 July 2026) |
| Pages | 324–336 |
| DOI | 10.1007/978-981-92-2014-4_26 |
| Peer review | Peer-reviewed conference proceedings |
| Research type | Systematic survey + conceptual framework |
| Thesis relevance | **Medium** (downgraded from Very High — B7 covers the core argument) |

## 2. Problem and objectives

Financial multi-agent LLM systems report results that evaluation practice cannot support. The paper builds a taxonomy and names the evaluation failures that invalidate reported performance.

## 9. Methodology

Four-dimensional taxonomy — architecture, coordination, memory, tool integration — over **12 systems plus baselines**.

## 10–11. Findings

**Coordination Primacy Hypothesis (CPH)** — inter-agent coordination protocol design is a primary driver of decision quality, *"often exerting greater influence than model scaling."* Presented explicitly as a **falsifiable hypothesis pending adequate evaluation infrastructure** — keep that hedge in every citation.

**Coordination Breakeven Spread (CBS)** — a metric for whether coordination adds value **net of transaction costs**.

**Five evaluation failures** documented, including transaction-cost neglect, that can *reverse* reported returns. ⚠ Enumerate from the PDF if obtained.

## 14–15. Relevance

1. **Evaluation design.** Now one of *four* independent sources supporting RQ5 (B1, B4, B7, B5), rather than a load-bearing one.
2. **Boundary-condition dialogue.** CPH is a useful hypothesis to place beside C007, but neither should be treated as a universal rule. The thesis must test whether governance benefits justify coordination overhead in its own Deal Desk setting.

**Thesis interpretation.** Use CPH carefully — the authors call it unverified. Presenting it as established would be the exact error the paper warns against.

---

# Cross-paper synthesis

## 1. The constraint spectrum

Arranged from most to least constrained:

| Paper | Mechanism | Guarantee |
|---|---|---|
| B1 | Architectural floor, ordered option set | **Formal** — cannot be violated |
| B2 ⚠ | Segregation of duties across agents | Structural (mechanism unverified) |
| B7 | RBAC — agent permissions bound to acting user's role | Structural; documented as a requirement, not a mechanism |
| B8 | Structured process rules retrieved during execution | Empirical process-adherence improvement; not a formal guarantee |
| B9 | External DMN decision service | Deterministic rule execution; no LLM/MAS evaluation |
| SGT (orch. P4) | Symbolic guidance, 5 levels | Empirical, non-monotonic |
| B6 | Tool-derived negotiation bounds | Soft — LLM chooses inside range |
| B3 | RAG + fine-tuning grounding | None — a knowledge, not a control, mechanism |
| ChatDev (orch. P2) | Predefined phases | Process structure only |
| Puppeteer (orch. P1) | Learned policy | None — fully learned |
| CAMEL (orch. P3) | Prompt-level role constraints | Weakest — role flipping observed |

**Thesis interpretation.** This supports a **risk-sensitive governance continuum** rather than one constraint mechanism for everything: deterministic services for mandatory/high-risk decisions; bounded reasoning for evidence gathering, substitutions and exception analysis; and human escalation when authority or evidence is insufficient. B7 adds a second axis: B1 constrains what may be decided, while RBAC constrains what each agent may see and touch. Specialist boundaries are therefore justified primarily by permission scope, accountability, traceability and failure isolation—not assumed accuracy superiority.

## 2. Convergent finding — more capability is not monotonically better

Four independent papers, four domains, same shape:

- **SGT** (graph coordination): intermediate symbolic guidance beats both extremes.
- **B6** (supply chain): performance *"can vary non-monotonically with model size."*
- **B5** (finance): coordination design plausibly outweighs model scaling (CPH — hypothesis).
- **B3** (process QA): the best result in the paper (92.31%, single-process fine-tuning) beat several larger multi-process and RAG-only configurations.

Plus **B1**: two models failed in opposite directions.

This is a strong cross-paper pattern, but it does not invalidate C007. C007 remains a required boundary condition and motivates the controlled single-generalist baseline.

## 2a. Convergent finding — accuracy alone is an unsafe evaluation metric

**Supported by complementary empirical and review evidence:**

- **B1** (empirical): 0.74 aggregate accuracy concealed 0.0 recall on the safety-critical subset.
- **B4** (credit review): only 7/60 credit-risk papers report efficiency at all; authors explicitly call for "evaluation frameworks beyond accuracy."
- **B7** (KDD '25, general principle): *"agents deemed 'correct' in traditional benchmarks may still fail in production due to policy violations or compliance risks."* Also: task completion alone gives "limited fine-grained insight into failures."
- **B5 / Zhu et al.** (finance / orchestration): both name the lack of an orchestration-quality benchmark as an open problem.
- **B10** (CloudOps framework): task-completion baselines concealed policy, memory, tool-sequence and guardrail failures; the paper supplies implementable trace metrics.

**This is now the best-evidenced claim in the entire review.** B7 supplies the broad evaluation taxonomy, C047 supplies the multi-agent failure taxonomy, and B10 operationalises trace-level evaluation in an enterprise workflow. Supporting RQ2 no longer rests on the thesis's own assertion.

## 3. Failure modes worth designing against

| Failure | Source | Deal Desk risk |
|---|---|---|
| Silent under-escalation | B1 | Deal approved that required sign-off |
| Over-escalation | B1 | Automation defeated; everything escalates |
| Accuracy/task-completion paradox | B1, B4, B7, B10 | Evaluation hides critical process failures |
| Inconsistency across identical runs | B1, B7 (pass^k) | Same deal routed differently on different days |
| Agent stubbornness | B6 | Pricing dominates Credit |
| Tool misuse | B6 | Tool used without context makes it worse |
| Semantic tool errors passing syntactic checks | B7 | A valid-looking API call with a hallucinated discount value |
| Poor tool-failure handling | B7 | CRM API times out and the agent breaks instead of retrying |
| Cross-process knowledge confusion | B3 | One generalist agent given all Deal Desk policies gives worse answers |
| Embedding/representation mismatch | B3 | A grounding component tuned for the wrong input format silently degrades |
| Post-hoc-only interpretability | B4 | A credit decision looks explainable but isn't causally grounded |
| Performance drift over long horizons | B7 | Quality decays across a multi-week deal cycle, undetected |
| Permission leakage | B7 | An agent surfaces data above the acting rep's access level |
| Policy not consulted before action | B10 | A plausible output is produced without checking the applicable rule |
| Wrong or missing tool sequence | B10 | Approval is requested before configuration, credit or margin validation |
| Incomplete shared-state retrieval | B10 | A decision uses stale or missing customer/inventory context |
| Guardrail expected but state changed | B10 | An unauthorized approval or deal-state update succeeds |
| Role flipping | CAMEL | Agent abandons its assigned role |
| Mis-coordination / deceptive agreement | Puppeteer | Agents agree wrongly |
| Infinite loops | CAMEL | Deal never completes |

## 4. Architecture comparison — business papers

| Paper | Architecture | Agent basis | Coordination | Constraint |
|---|---|---|---|---|
| B1 | Five-layer, single decision point | None (wrapped LLM) | Sequential wrapper | Formal floor |
| B2 ⚠ | Multi-agent | Function (SoD) | Unverified | Duty separation |
| B3 | RAG + fine-tuning pipeline | None | N/A | None (knowledge only) |
| B6 | Echelon agents | Position | Negotiation, 3 rounds | Tool bounds |
| B7 | N/A (survey) | — | — | RBAC + policy adherence as evaluated requirements |
| B8 | Single LLM agent + process-rule database | Function/process | Rule retrieval during execution | Structured process rules |
| B9 | RPA bot + external DMN service/repository | N/A | Bot-service calls | Deterministic DMN rules |
| B10 | Four-pillar assessment framework on MOYA | CloudOps roles | Trace/judge evaluation | Policies, RBAC/guardrails as assessed controls |

## 5. What the business papers add that the orchestration papers do not

1. **Formal safety guarantees** (B1).
2. **Control-based agent boundaries** (B2), and **permission-based agent boundaries** (B7).
3. **Industrially grounded processes with explicit evaluation targets** (B1, B2, B3).
4. **Auditability as a requirement** (B1, B4, B7, B10).
5. **Cost-aware evaluation** (B4, B5, B7, B10 — TTFT, token cost, cost-bounded protocols and judge overhead).
6. **Process-specific knowledge grounding and a testable risk of cross-process interference** (B3).
7. **Complementary evaluation frameworks**: B7 supplies a broad taxonomy; B10 supplies implementable trace metrics across LLM, Memory, Tools and Environment.

## 6. Selected research questions

**Primary RQ — governed orchestration.** *How can a governed multi-agent orchestrator coordinate specialised agents to ensure business-rule compliance and decision completeness in B2B Deal Desk processing?*

**Supporting RQ1 — governance mechanisms.** *Which Deal Desk decisions require deterministic business rules, which permit bounded agent reasoning, and how do these mechanisms affect constraint compliance, escalation accuracy and latency?* Evidence base: B1, B6, B8 and B9.

**Supporting RQ2 — evaluation beyond final accuracy.** *To what extent do orchestration-level trace metrics identify Deal Desk processing failures that are not visible from final-output accuracy alone?* Evidence base: B1, B4, B7, B10 and O5, with C047 supplying the empirical multi-agent failure taxonomy.

**Optional comparison experiment.** *How does the specialised multi-agent architecture compare with a single generalist agent in decision accuracy, policy compliance, consistency, latency and cost?* This tests the architectural implication drawn from B3 and responds to C007's capability-saturation boundary condition. It is a validity check, not an expected proof that MAS is superior, and is not a dependency for completing the core thesis.

The previous seven-question candidate set is superseded by this structure. Dynamic routing remains a possible implementation experiment, while enterprise integration remains a system-design requirement rather than a separate RQ.

## 7. Preliminary research-gap formulation

> Existing peer-reviewed work provides important components for governed enterprise agents, including adaptive orchestration, symbolic guidance, rule-grounded process execution, external decision management and domain-specific automation. However, in this purposive review, **no peer-reviewed work was identified** that integrates these components into a governed multi-agent Deal Desk architecture coordinating configuration, pricing, availability, credit/risk, policy compliance and approval routing together. The remaining gap concerns the design and evaluation of a risk-sensitive orchestrator that applies deterministic control where required, bounded agent reasoning where appropriate, maintains auditable shared state, and evaluates orchestration behaviour alongside final decision correctness. B7 and B10 provide the evaluation foundation, while C047 identifies multi-agent failure categories that the trace metrics should detect.

## 8. What the papers establish vs. thesis interpretation

**Established by the papers:**
- An ungoverned LLM missed 100% of mandatory escalations in an industrially grounded onboarding evaluation using partner-validated synthetic profiles (B1).
- Aggregate accuracy can conceal complete failure on a safety-critical subset (B1).
- Agents deemed correct on traditional benchmarks can still fail in production on policy and compliance grounds (B7, stated as principle).
- Enterprise evaluation concerns — RBAC, reliability guarantees, long-horizon behaviour, policy adherence — are "rarely addressed in the existing literature" (B7).
- Current agents struggle with strict consistency (pass^k) in retail and booking domains (B7, reporting τ-benchmark).
- Agents negotiating inventory can reach near-human consensus, and can also stubbornly dominate one another (B6).
- Performance does not scale monotonically with model size (B6).
- Combining two processes in one LLM's knowledge base reduces accuracy, more so when the processes share vocabulary (B3).
- Domain/format-specific grounding (chunking, embedding choice) materially outperforms generic approaches (B3).
- Only 3/60 credit-LLM papers use causal rather than post-hoc interpretability, and only 7/60 report efficiency at all (B4).
- Coordination design may outweigh model scaling — **hypothesis, not result** (B5).

**Thesis interpretation, not established:**
- That Pricing/Inventory/Credit/Approval are the correct agent set.
- That a hybrid constraint scheme outperforms a uniform one.
- That P2P findings transfer to Q2C.
- That B7's multi-agent metrics will detect Deal-Desk-specific failures — that is RQ7, to be tested.
- That RBAC and segregation of duties are complementary rather than substitutes.
- That specialist agents are universally more accurate than one generalist agent. B3 reports a process-knowledge degradation pattern, but retrieval confusion, context overload, vocabulary overlap and evaluation design are alternative explanations. Specialisation is primarily justified here by permission scope, accountability, traceability and failure isolation, and remains empirically testable.

---

# B8 — A Step Towards Cognitive Automation: Integrating LLM Agents with Process Rules ⚠ PUBLISHER ABSTRACT ONLY

> **Access rule:** the complete Springer chapter was not obtained. Only bibliographic facts and claims stated explicitly in the official publisher abstract may be used. Earlier detailed extraction notes are withdrawn.

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Sascha Kaltenpoth, Alexander Skolik, Oliver Müller, Daniel Beverungen |
| Venue | BPM 2025 — *Business Process Management*, LNCS |
| DOI | 10.1007/978-3-032-02867-9_19 |
| Pages | 308–324 |
| Peer review | Peer-reviewed conference proceedings |
| Full text | Not obtained; subscription-only |

## 2–17. Permitted evidence and thesis relevance

The publisher abstract states that the study integrates LLM agents with process rules, evaluates 118 real-world process instances from a power-grid provider, and reports a reduction in process failures from 16% to 1%. These abstract-level statements support only the general principle that structured process rules may improve adherence. The source does not support detailed claims in this review about its internal architecture, additional datasets, rule-generation procedure, failure taxonomy, or unreported experimental conditions. It provides no direct evidence that a multi-agent design is superior or that the result transfers to Deal Desk processing.

---

# B9 — Adding Decision Management to Robotic Process Automation ✅ FULL TEXT DONE

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Maximilian Völker, Simon Siegert, Mathias Weske |
| Venue | BPM 2021 Blockchain and RPA Forum, LNBIP 428 |
| DOI | 10.1007/978-3-030-85867-4_3 |
| Pages | 23–37 |
| Peer review | Peer-reviewed conference proceedings |
| Full text | Accepted author manuscript verified |

## 2. Problem and objective

RPA platforms automate interactions but treat decisions as embedded if/else or switch logic. Complex decision logic therefore produces unreadable, hard-to-maintain automation models. The paper proposes making decisions first-class, separately managed components.

## 3–5. Architecture, responsibilities and coordination

The prototype integrates UiPath with Camunda's decision engine through DMN. The architecture separates: **(1)** the RPA bot/workflow, **(2)** the decision service, **(3)** independently modelled DMN decision tables, and **(4)** a decision-model repository. The paper evaluates embedded and external decision-service patterns and demonstrates communication between the bot, engine and repository.

## 6. Business constraint enforcement ★

DMN tables define input variables, output variables, rules and hit policies. Business decisions can therefore be reviewed, updated and executed independently of the automation workflow. This is a strong architectural precedent for separating Deal Desk business rules from agent prompts and orchestration code.

## 7–9. Tools, domain and methodology

The working prototype uses UiPath and Camunda. An illustrative shipment-cost/responsible-department decision demonstrates the approach. The evaluation is a design-and-prototype validation rather than a comparative LLM experiment; it does not report accuracy improvements comparable to B1 or B8.

## 10–12. Findings and failure modes

The main finding is architectural: externalized decision models reduce process-model complexity and allow decision logic to be managed separately. The main risks are additional modelling complexity, the need to learn DMN, synchronization/versioning between bot and decision models, and deployment/testing considerations.

## 13. Limitations

RPA rather than LLM agents; prototype/illustrative case rather than field deployment; no multi-agent collaboration; no ERP-specific evaluation; no segregation-of-duties test; limited quantitative performance evidence.

## 14–15. Enterprise and Deal Desk relevance

The paper maps cleanly to the thesis architecture: specialist agents perform domain work, while a separate deterministic service evaluates explicit, versioned decision rules. It supports the design of editable policy tables and auditable rule execution, but should not be cited as evidence that LLM or multi-agent systems perform better.

## 16. Evidence locations

| Claim | Location |
|---|---|
| Problem with embedded decision logic | §§1–3 |
| DMN integration and design | §4 |
| External decision-service architecture | §4.2 |
| UiPath/Camunda prototype | §5 |
| Limitations and design implications | §§5–6 |

## 17. Potential gap evidence

The paper separates deterministic decision management from automated execution, but the executor is an RPA bot. It does not study how several LLM agents coordinate around shared decision services, handle contradictory outputs or preserve coherent deal state—precisely the orchestration problem addressed by this thesis.

---

# B10 — Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems ✅ FULL TEXT DONE

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Sreemaee Akshathala, Bassam Adnan, Mahisha Ramesh, Karthik Vaidhyanathan, Basil Muhammed, Kannan Parthasarathy |
| Venue | AGENT 2026 — 3rd International Workshop on AI Foundation Models and Software Engineering |
| Proceedings pages | 9–17 |
| DOI | 10.1145/3786167.3788414 |
| Full-text version | Complete nine-page author version, arXiv:2512.12791v2 |
| Peer review | Peer-reviewed ACM workshop proceedings |
| Thesis relevance | **High for Supporting RQ2** — directly evaluates runtime behaviour beyond task completion |

## 2. Problem and stated gap

The paper argues that binary task-completion metrics do not capture behavioural uncertainty in agentic systems. Non-determinism changes execution paths, tool selection and memory retrieval, so a task can appear successful while the agent violates policy, skips validation or uses incomplete context. The authors derive this problem from an industry collaboration with MontyCloud and a production CloudOps deployment (Introduction and §2).

## 3. Objective and research questions

The paper proposes an end-to-end assessment framework and evaluates:

1. Whether it reveals assessment dimensions missed by task-completion/tool-usage baselines.
2. Which failure patterns occur across assessment pillars.
3. Its cost and time overhead.

These questions align closely with this thesis's distinction between final-output correctness and orchestration correctness.

## 4. Framework architecture

The framework contains four pillars:

- **LLM:** instruction following, policy adherence, safety and alignment.
- **Memory:** storage correctness, update propagation and retrieval coverage.
- **Tools:** selection, parameter mapping, ordering, expected calls, errors and recovery.
- **Environment:** workflows, configurability, observability, guardrails and authorization boundaries.

It combines three assessment modes: **static analysis** against ground truth, **dynamic runtime monitoring**, and **judge-based evaluation** using LLM-as-Judge or Agent-as-Judge (§3, Figures 1–2).

## 5. Agent roles and coordination

Evaluation uses MOYA, an existing multi-agent CloudOps framework. Three scenarios include cost-optimization and security agents, while the most complex scenario includes Performance, Remediation and root-cause-analysis agents. The paper evaluates coordination primarily through execution traces, expected tool sequences, context retrieval and state outcomes rather than proposing a new orchestration algorithm.

## 6. Business constraint enforcement ★

The Environment pillar requires deterministic operational boundaries and access controls. The paper explicitly discusses predefined permissions, policies, authorization/approval and system-level role-based access control (§3.4). Its contribution is chiefly **assessment of enforcement** rather than a new universal enforcement mechanism.

For the Deal Desk, this supports checking whether agents consulted applicable pricing/credit/approval rules and whether prohibited actions were blocked—not merely whether the final deal package looked plausible.

## 7. Shared state and memory

The Memory pillar measures whether updates are correct, non-duplicative and visible across agents, including update latency and retrieval precision/recall/F1. The authors distinguish single-hop, multi-hop, temporal and open-domain retrieval (§3.1). This provides direct methodological grounding for treating shared deal state as an evaluated governance mechanism.

## 8. Tools and observability

Tool assessment covers:

- correct tool classification;
- semantically correct parameters;
- diagnostic-before-action ordering;
- invocation of mandatory tools;
- interpretable error messages;
- recovery, latency, cost and consistency.

The environment assumes telemetry, tracing, logging and control-flow visibility for root-cause analysis (§§3.2–3.4).

## 9. Data and enterprise realism

The authors construct synthetic instances, logs and policies from production-motivated issues. The three scenarios are:

1. AWS cost optimization subject to environment verification, policy and approval constraints.
2. Security incident remediation requiring compliance checks and logging before policy changes.
3. A multi-agent performance/root-cause/remediation workflow with dependencies and rollback requirements.

This is more enterprise-realistic than a toy benchmark, but the experimental data are synthetic and the domain is CloudOps, not Deal Desk.

## 10. Experimental setup

The implementation extends MOYA with Mem0 and ChromaDB, uses GPT-4o at temperature 0.7 and text-embedding-3-small, and runs each scenario three times. Baselines measure task completion and tool-usage ratio. The proposed framework adds deterministic trace metrics plus LLM-as-Judge and Agent-as-Judge assessment (§4.1).

## 11. Results ★

Key within-paper results:

- In S1, tool sequencing was 100%, but policy adherence was only 33%.
- S2 completed the task, yet memory recall was 13.1% and memory F1 was 18.1%.
- In S3, tool-sequence correctness was 53%, expected calls 62%, policy adherence 0%, dependency inquiry 67% and memory F1 51.32%.
- Tool failures were highest in the complex multi-agent scenario; environment guardrail failures appeared only there.
- LLM-as-Judge was far cheaper and faster than Agent-as-Judge; the latter cost roughly 16 times more and took roughly 62 times longer in the reported comparison.

The correct inference is that final completion and coarse tool-usage metrics can conceal process failures. Results must not be compared numerically with other papers because the tasks, models and experimental designs differ.

## 12. Observed failure modes ★

- Acting without consulting applicable policy.
- Skipping diagnostic or verification steps.
- Missing mandatory tool calls or using an incorrect sequence.
- Incomplete memory retrieval despite correct retrieved facts.
- Missing configuration or role-mapping context.
- State changes despite expected environment guardrails.
- Error propagation across agents in the complex scenario.

## 13. Limitations

- Only three CloudOps scenarios and three runs per scenario.
- Synthetic operational data, although motivated by production issues.
- GPT-4o only; limited model diversity.
- Manual specification of expected behaviour and golden traces.
- Judge-based assessment can introduce evaluator bias.
- Agent-as-Judge has substantial cost/time overhead.
- Authors themselves call this “first steps” and recommend validation in other domains.

## 14. Enterprise relevance

B10 is stronger than a purely conceptual survey because it operationalises system-level assessment on an enterprise workflow. It complements B7: B7 supplies the general taxonomy; B10 supplies implementable trace metrics and demonstrates why task completion is insufficient.

## 15. Deal Desk mapping

| B10 metric | Deal Desk adaptation |
|---|---|
| Policy adherence | Was the correct pricing, credit or approval policy consulted before action? |
| Diagnostic-before-action sequence | Were configuration, availability, credit and margin checks performed before approval routing? |
| Expected tool calls | Were all mandatory specialist agents/rule services invoked with valid parameters? |
| Memory coverage | Was all required customer, product, inventory and prior-decision context retrieved? |
| Guardrail violation | Was an unauthorized approval, override or state update attempted? |
| State observability | Can every deal-state change be traced to evidence, actor and rule/version? |

## 16. Evidence locations

| Claim | Location |
|---|---|
| Four pillars and three assessment modes | §3, Figures 1–2, Table 1 |
| Memory metrics and propagation | §3.1 |
| Tool sequence, expected calls and recovery | §3.2 |
| Policy adherence and safety evaluation | §3.3 |
| Observability, guardrails and RBAC | §3.4 |
| Experimental setup and scenarios | §4.1 |
| Metric definitions | §4.2, Table 2 |
| Baseline vs framework results | Table 3 |
| Judge results and failure patterns | Tables 5–7 |
| Cost/time overhead | Figures 3–4 |
| Interpretation and limitations | §§5 and 7 |

## 17. Potential gap evidence

B10 shows how to inspect enterprise-agent traces, but it is a CloudOps assessment framework rather than a Deal Desk implementation. It does not coordinate configuration, pricing, availability, credit and approval decisions or evaluate completion of an approval-ready deal package. It therefore strengthens the thesis's evaluation method without closing the Deal Desk-specific integration gap.

---

# B11 — Solutions and Minimal Conflict Search for Product Configuration: A Case Study ✅ FULL TEXT DONE

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Sebastian Velten, Christopher Hamkins |
| Venue | *Constraints*, 30, 35–61 |
| Year | 2025 |
| DOI | 10.1007/s10601-025-09381-2 |
| Type | Peer-reviewed application paper and industrial case study |
| Access | Complete open-access paper verified |

## 2. Problem and objective

The paper addresses configuration of high-performance pumps and valves under technical, pricing, lead-time, availability, and business constraints. Its objectives are to find preferred feasible configurations, detect infeasibility, identify minimal conflicts, propose resolutions, and help product modelers diagnose problematic rules.

## 3–8. Architecture, decision logic, tools, and data realism

The system translates ERP product models into a constraint-programming formulation. Sales users specify customer requirements, while deterministic restriction tables, conditional assignments, and plant-availability constraints define feasible combinations. The configurator generates quotation information and, after ordering, produces the order-specific bill of materials, work plans, and routings transmitted to ERP. Google OR-Tools provides the solver implementation. This is deterministic decision support rather than LLM or multi-agent reasoning.

## 9–11. Methodology and results

The evaluation uses genuine user interactions across industrial product models. The solution study includes 2,250 cases, of which 431 were infeasible and 1,819 admitted solutions. A preprocessing study uses 24,000 cases repeated five times and reports about 10% average response-time improvement. Prepared solver objects save roughly 30% of processing time. Around 6,000 conflicting end-user cases compare the proposed MinC_BBS algorithm with modified QUICKXPLAIN; the proposed method usually completes in about 25% of the baseline time. A separate analysis uses 3,700 conflicting product-modeler cases.

## 12–13. Failure modes and limitations

The system detects inconsistent customer requirements and rule conflicts rather than agent failures. Its results depend on one company's product models, whose minimal conflicts are usually small. The underlying problems remain computationally difficult, and some cases take substantially longer. The study does not evaluate credit, approval routing, policy permissions, LLMs, or multi-agent coordination.

## 14–17. Enterprise and Deal Desk relevance

B11 establishes that configuration validity can be enforced through deterministic constraints while still producing explanations and alternative resolutions. It supports treating configuration as a high-control Deal Desk decision rather than delegating validity to unrestricted LLM reasoning. It also supplies a realistic conventional baseline linking customer requirements, quotation data, configuration rules, inventory-related availability, and ERP outputs. The thesis interpretation is that agents may gather requirements and explain alternatives, while a deterministic service retains authority over configuration validity.

---

# B12 — Implementing Configure, Price, Quote in the Supply Chain: The Case of Essemtec AG ✅ FULL TEXT DONE

## 1. Bibliographic / verification

| Field | Value |
|---|---|
| Authors | Ariane Blumentritt, Joachim Ehrenthal, Benjamin Haueter, Nadine Hitz, Muhammad Sufian |
| Venue | *Journal of Information Technology Teaching Cases*, 13(2), 246–254 |
| Year | 2023 |
| DOI | 10.1177/20438869221139596 |
| Type | Peer-reviewed teaching case |
| Access | Complete paper verified |

## 2. Problem and objective

The case explains why a B2B manufacturer replaced spreadsheet-based quotation with a CPQ system. Product complexity made configuration slow and error-prone, required repeated intervention from product management, and sometimes produced technically infeasible or underpriced offers.

## 3–8. Process, systems, coordination, and data

The documented process proceeds from CRM-supported lead management to opportunity management, configuration, quotation, purchase order, factory order, production, and quality checks. CPQ contains product rules and connects sales-facing configuration with production requirements. The implementation required integration with existing CRM and ERP systems, including customer and article master data and a bidirectional ERP-CRM interface. Coordination involved sales, product management, ICT, CRM and ERP owners, management, distributors, and the software provider.

## 9–11. Evidence and reported outcomes

The paper is a descriptive teaching case rather than a controlled experiment. It reports that CPQ reduced configuration inquiries to product management, supported real-time global changes to configurations and prices, improved quotation convenience, and reduced failure costs. It also reports that approximately 30% of cases remained special requests requiring manual action. The original six-month implementation estimate expanded to about two years because of rule complexity, interface integration, and stakeholder expectations.

## 12–13. Failure modes and limitations

The conventional process suffered from spreadsheet logic errors, outdated distributed files, incorrect configurations, missed prerequisite options, low prices caused by incomplete configurations, manual double-checking, and cross-department dependence. The evidence comes from one company and does not provide a controlled baseline, detailed quantitative performance metrics, or an agentic-AI comparison.

## 14–17. Enterprise and Deal Desk relevance

B12 provides the clearest full-text description of the non-agentic business side required by the supervisor. It connects CRM, CPQ, ERP, pricing, configuration, sales, and production while showing that conventional CPQ improves rule consistency but does not eliminate exceptions or organisational coordination. It supports positioning the thesis contribution as governed coordination across systems and decision domains, not as the invention of product rules or CPQ itself.

---

# Outstanding work

1. B2 and B5 remain optional abstract-only records. Neither blocks the LR.
2. B1 and B3 load-bearing numerical claims were verified directly on 24 September 2026. B8 must remain limited to its publisher abstract.
3. The final reference-format audit and two-way citation check were completed on 25 September 2026. Shared IDs are synchronized across Phase 1A, this extraction file, and the LR bibliography.
4. The retained full-text pool is O1 to O5, B1, B3, B4, B6, B7, B9 to B12, and C047. B8 and C007 are publisher-abstract sources.
5. KG-BDI is closed as screened but excluded unless the user later supplies the complete PDF; do not use its abstract-level architecture or result claims.
6. Only supervisor feedback and the final university plagiarism check remain before freezing the LR.
