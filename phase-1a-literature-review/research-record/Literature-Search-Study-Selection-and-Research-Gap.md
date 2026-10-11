# Deal Desk Orchestrator — Phase 1A: Literature Review (LR)

**Student:** Ali Alnaggar
**Thesis:** Deal Desk Orchestrator (Multi-Agent System)
**Created:** 19 September 2026, after the supervisor ("doctor") meeting
**Archive update:** 11 October 2026. All 15 detailed-synthesis source texts are now filed under `../papers/`; this research record retains the historical selection and extraction decisions.
**Status:** This file is Track A only (Literature Review). Agent design is the Phase 1B record (to be integrated later), data strategy is the Phase 1C record (to be integrated later), and administrative context is the thesis administration record (to be integrated later). Full business-paper extraction detail lives in `Business-Process-Governance-and-Evaluation-Study-Notes.md`; this file holds the summary and gap-tracking view.

---

## Goal of this track

Build the Literature Review (LR). To build it, we go through **4 steps, in this order**:

1. **Problem papers** — papers that talk about the actual problem (complex B2B deals needing coordination across CRM, CPQ, ERP, pricing, inventory, credit, approvals).
2. **Solution attempt papers** — papers where people already tried to solve this or a similar problem, focused on *how*.
3. **Gaps** — from steps 1 and 2, what's still missing.
4. **Contribution (mine)** — based on the gap, what Ali's thesis specifically adds.

### Rules that apply to all 4 steps

- Papers must be **real, verified, peer-reviewed, academic** papers only.
- **Foundation papers must address the Deal Desk / B2B deal-coordination problem OR multi-agent orchestration specifically** — either angle qualifies. General MAS/AI-agent papers with no connection to either angle are not foundation papers — kept as background reading only.
- **Publication year: 2020 or later**, unless used purely as classic MAS theory (flag explicitly as "foundational theory, not evidence").

### Search strategy — purposive, and stated as such

**Decision (20 Sept 2026): the original 187-paper candidate pool is retired and will not be worked through.** The review uses a **purposive (targeted) search strategy** across two defined domains — orchestration and business-process automation — selecting the strongest peer-reviewed source per sub-topic rather than screening an exhaustive corpus.

This is a legitimate and common LR method for a bachelor's thesis and must simply be **declared in the methodology section**, in roughly these words:

> This review employs a purposive search strategy across two domains — LLM multi-agent orchestration and enterprise business-process automation — selecting peer-reviewed sources by relevance to each Deal Desk decision pillar, rather than an exhaustive systematic screening. Claims of literature absence are therefore stated as "no peer-reviewed work was identified that…" rather than as proof of non-existence.

Phrasing every absence claim that way keeps the gap statement honest without requiring exhaustive coverage. **Do not write "no work exists" anywhere in the thesis — write "no peer-reviewed work was identified."**

### Source rule — verifying peer review independently

Journal claiming peer review is not enough on its own. Checklist: (1) Scopus/Web of Science indexing, (2) known publisher reputation (IEEE, ACM, Elsevier, Springer/Nature, Taylor & Francis, Sage, Wiley, MDPI — check the specific journal, INFORMS), (3) check predatory-journal watchlists, (4) real named editorial board, (5) turnaround time (weeks = red flag, 3+ months = normal), (6) reject preprint servers outright (SSRN, arXiv, ResearchGate, TechRxiv) regardless of polish, (7) for conferences: real recurring event, legitimate proceedings publisher.

**Added rule (8) — check the paper's own front matter for contamination.** A mismatched ethics statement, funding declaration or dataset reference means the manuscript was assembled from a template and not proofread. See the rejected-sources table below for a live example.

**Added rule (9) — check the reference-format block, not the title layout, for author order.** Two-column PDFs routinely scramble author order when converted. This has already caused one error in this review (O1) and one near-miss (B7).

---

## STATUS AT A GLANCE — answering "where are we right now"

| Question | Answer |
|---|---|
| Orchestration papers found and read? | **Yes — 5/5 done.** O1–O5, full text, bibliographically verified. |
| Business, governance, and evaluation evidence ready? | **Yes.** The current LR uses nine full-text business, governance, and evaluation papers: B1, B3, B4, B6, B7, B9, B10, B11, and B12. B8 is retained only at publisher-abstract level. |
| Current evidence pool | **Fifteen full-text peer-reviewed studies plus two abstract-level sources.** The full-text pool consists of O1 to O5, B1, B3, B4, B6, B7, B9 to B12, and C047. B8 and C007 are used only at official publisher-abstract level. |
| Anything still blocked? | **No source blocks the LR.** B2 and B5 remain abstract-only and are excluded from detailed claims. KG-BDI is excluded because its full text could not be obtained. |
| Is the gap statement done? | **Yes, and it is now defensible** — provided every absence claim is phrased as "no peer-reviewed work was identified" (see search-strategy note above). |
| Is the LR drafted? | **Yes.** Introduction, Methodology, three Results groups, Discussion, and References are complete in a clean submission-ready draft. |
| What remains before submission? | Supervisor feedback, any resulting revisions, and the university plagiarism check. The reference audit, source-ID synchronization, language pass, formatting check, and B1/B3 evidence verification are complete. |

**Bottom line:** the LR is structurally complete and no longer depends on B2. B2 may be added later only if its full text becomes available and contributes evidence that is not already covered. It is not required to finalize the present LR.

---

## Verified papers — Orchestration side (5 papers) — COMPLETE

Deep-extracted and bibliographically verified 20 September 2026.

### O1 — Multi-Agent Collaboration via Evolving Orchestration

| | |
|---|---|
| Authors | Yufan Dang, Chen Qian, Xueheng Luo, Jingru Fan, Zihao Xie, Ruijie Shi, Weize Chen, Cheng Yang, Xiaoyin Che, Ye Tian, Xuantang Xiong, Lei Han, Zhiyuan Liu, Maosong Sun |
| Cite as | **Dang et al. (2025)** |
| Venue | NeurIPS 2025 (Advances in Neural Information Processing Systems 38) |
| Preprint | arXiv:2505.19591 |
| DOI | 10.52202/085713-5502 |
| Peer review | Peer-reviewed conference proceedings |
| Relevance | Orchestration architecture (evolving/learned orchestration vs. static workflow) |

### O2 — ChatDev

| | |
|---|---|
| Venue | ACL 2024 |
| DOI | 10.18653/v1/2024.acl-long.810 |
| Pages | 15174–15186 |
| Peer review | Peer-reviewed conference proceedings |
| Relevance | Static multi-agent workflow baseline |
| Caveat | Shares authors with O1 (same Tsinghua/OpenBMB group); the "Puppeteer" learned-orchestration variant lives inside the ChatDev repo itself. **O1 and O2 are not independent evidence** — their contrast is one research line's own evolution, not two groups converging. State it that way when cited together. |

### O3 — CAMEL

| | |
|---|---|
| Venue | NeurIPS 2023 (Advances in Neural Information Processing Systems 36) |
| Pages | 51991–52008 |
| Preprint | arXiv:2303.17760 |
| Peer review | Peer-reviewed conference proceedings |
| Relevance | Foundational multi-agent role-play/communication architecture |

### O4 — Symbolic Guidance for LLM Agents in Distributed Multiagent Coordination

| | |
|---|---|
| Authors | Benjamin Rachmut, Ning Zhang, Yevgeniy Vorobeychik, William Yeoh |
| Venue | AAMAS 2026 |
| DOI | 10.65109/KEVK7310 |
| Peer review | Peer-reviewed **3-page extended abstract** |
| Relevance | Carries the load-bearing claim "business rules should not simply be delegated to unrestricted LLM reasoning" |
| Caveat | Compressed evidence: one heuristic (MIS), three synthetic graph domains, no enterprise setting. Pair with B1, which demonstrates the same principle in a real business process with real numbers. |

### O5 — LLM-Based Multi-Agent Orchestration survey

| | |
|---|---|
| Authors | Zhu, Liu, Yu & Zhang |
| Venue | *Future Internet* 18(6), 326 |
| Year | 2026 |
| DOI | 10.3390/fi18060326 |
| Peer review | Peer-reviewed, open-access review article |
| Relevance | **States directly that no widely adopted benchmark exists for multi-agent orchestration quality.** Named gap from a peer-reviewed source — basis for the thesis's dual evaluation framing (business correctness AND orchestration behaviour). |

---

## Verified papers — Business, governance, and evaluation side

### B1 — Governed Agentic Process Automation ✅ FULL TEXT DONE

| | |
|---|---|
| Authors | Massimo Pacella, Gabriele Papadia, Vincenzo Giliberti |
| Venue | *Algorithms* 19(8), 627 — MDPI |
| Year | 2026 |
| DOI | 10.3390/a19080627 |
| Peer review | Peer-reviewed, open access |
| Deal Desk pillar | **Approval** |
| Key finding | Five-layer architecture (Intake→Cognitive→Control→Execution→Governance); LLM proposes, never executes. Formal floor-safety property: `g(e) ⪰ r_floor(e)`. On 166 employee-onboarding profiles, 43 requiring mandatory approval: ungoverned Qwen2.5 missed **all 43 (recall 0.0)** while showing 0.74 *overall* accuracy — the accuracy paradox. With the floor guardrail active: **recall 1.0**, precision 1.0. |
| Why it matters | Direct, peer-reviewed proof an unguarded LLM will silently skip required approvals. Pairs with O4 (principle on synthetic graphs) and now with B7, which states the same risk as a general principle at a top-tier venue. |

### B2 — Multi-agent Collaboration for BPA in ERP Systems ⚠ ABSTRACT-ONLY — excluded from detailed LR evidence

| | |
|---|---|
| Authors | Jonas Schnepf, Matthias Schwarz, Bernd Scheuermann, Simon Anderer |
| Venue | IJCCI 2025 — *Communications in Computer and Information Science*, vol. 2827, Springer |
| Year | 2026, pp. 118–138 |
| DOI | 10.1007/978-3-032-15632-7_7 |
| Peer review | Peer-reviewed conference proceedings |
| Deal Desk pillar | General process / audit |
| What we know (abstract only) | Multi-agent LLM automation of procure-to-pay in a real ERP. Applies **segregation of duties** — a control-based justification (not a capability argument) for splitting a workflow across separate agents. |
| Current handling | The full PDF could not be obtained. No metrics, architecture details, or SoD mechanism are used in the LR. The source remains tracked as a relevant near-miss, but it is not a blocker. |
| Fallback used | B7 §5.1 supports permission-aware RBAC, while B1 supports separation of model proposals from controlled execution. The LR does not claim that these fully reproduce B2's possible task-distribution mechanism. |

### B3 — BPLLM framework ✅ FULL TEXT DONE

| | |
|---|---|
| Authors | Mario Luca Bernardi, Angelo Casciani, Marta Cimitile, Andrea Marrella |
| Venue | *Journal of Intelligent Information Systems* 62 — Springer |
| Year | 2024 |
| DOI | 10.1007/s10844-024-00898-1 |
| Peer review | Peer-reviewed journal article |
| Deal Desk pillar | Process knowledge representation |
| Key finding | RAG + fine-tuning + BPMN-specific chunking. Best result: 92.31% accuracy (fine-tuned Llama 3.1 8B, int4, single process). **Critical finding: adding a second process to the knowledge base reduced accuracy (92.31% → ~82%), worse when the two processes shared similar vocabulary** (Food Delivery + E-commerce, both delivery-style, ~80%) than when dissimilar (Food Delivery + Reimbursement, ~82–85%). |
| Why it matters | A concrete warning that multi-process knowledge can create interference. It motivates testing scoped retrieval and specialist boundaries, but does not prove that specialist agents are universally more accurate. Retrieval configuration, vocabulary overlap, context load, and evaluation design are alternative explanations. |

### B4 — Interpretable LLMs for credit risk ✅ FULL TEXT DONE (through Section 5)

| | |
|---|---|
| Authors | Muhammed Golec, Maha Alabduljalil |
| Venue | *Expert Systems with Applications* 306 — Elsevier |
| Year | 2026 |
| DOI | 10.1016/j.eswa.2025.130941 |
| Peer review | Peer-reviewed journal article |
| Deal Desk pillar | **Credit** |
| Key finding | PRISMA review, 60 papers (2020–2025). Only **3/60** use causal/counterfactual interpretability (rest post-hoc, e.g. SHAP). Only **9/60** report robustness tests. Only **7/60** report efficiency (cost/latency/energy) at all. Explicitly calls for "evaluation frameworks beyond accuracy"; ties future work to Basel Accords / EU AI Act. |
| Why it matters | Directly citable stated research gaps in the paper's own words. One of four independent sources converging on "accuracy alone is an unsafe evaluation metric." Also the methodological model for how a proper PRISMA funnel is reported (182→120→51→60) — useful when writing up our own, more modest, purposive method. |

### B5 — Toward Reliable Evaluation of LLM-Based Financial Multi-agent Systems ⚠ ABSTRACT-ONLY — no longer blocking

| | |
|---|---|
| Authors | Phat Nguyen, Thang Pham |
| Venue | PAKDD 2026 — *Lecture Notes in Computer Science*, Springer |
| Year | 2026, pp. 324–336 |
| DOI | 10.1007/978-981-92-2014-4_26 |
| Peer review | Peer-reviewed conference proceedings |
| Deal Desk pillar | Evaluation / coordination (finance-specific) |
| What we know (abstract only) | Four-dimensional taxonomy over 12 financial multi-agent systems. **Coordination Primacy Hypothesis**: coordination-protocol design may drive decision quality more than model scaling (authors flag it as an unverified, falsifiable hypothesis — keep that hedge in every citation). **Coordination Breakeven Spread**: cost-aware metric. Five evaluation failures documented, not yet enumerated. |
| Status change | **Downgraded from "highest priority" to optional.** B7 now carries the evaluation argument from ACM SIGKDD (stronger venue, open access). B5 would still add the five named failures and CBS, but nothing load-bearing depends on it. |

### B6 — Agentic LLMs in the supply chain ✅ FULL TEXT DONE

| | |
|---|---|
| Authors | Valeria Jannelli, Stefan Schöpf, Matthias Bickel, Torbjørn H. Netland, Alexandra Brintrup |
| Venue | *International Journal of Production Research* — Taylor & Francis |
| Year | 2025, advance online publication |
| DOI | 10.1080/00207543.2025.2604311 (journal version of arXiv:2411.10184 — **cite the journal DOI**) |
| Peer review | Peer-reviewed journal article |
| Deal Desk pillar | **Inventory** |
| Key finding | Echelon agents negotiate inventory/delivery consensus; tool outputs (linear regression, EOQ) bound the negotiation range. Best cost result via negotiation+tools; information-sharing alone gave the single biggest cost improvement (92.8%). Performance "can vary non-monotonically with model size." Failure modes: agent stubbornness (downstream agents dominate, upstream become "suggestible"); tool misuse without communication actively worsened the bullwhip effect. |
| Why it matters | Independent domain showing bigger model ≠ better. Agent stubbornness is a concrete, transferable failure mode for Deal Desk agent negotiation (e.g. Pricing vs Credit). |

### B7 — Evaluation and Benchmarking of LLM Agents: A Survey ✅ FULL TEXT DONE — NEW

| | |
|---|---|
| Authors | Mahmoud Mohammadi, Yipeng Li, Jane Lo, Wendy Yip — all **SAP Labs** |
| Cite as | **Mohammadi et al. (2025)** — ⚠ use the ACM Reference Format order (Mohammadi, Li, Lo, Yip), **not** the scrambled two-column title-block order |
| Venue | **KDD '25 — Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining, V.2**, Toronto, 3–7 Aug 2025, pp. 6129–6139 |
| DOI | 10.1145/3711896.3736570 |
| Licence | **CC BY 4.0 — open access, no paywall** |
| Peer review | Peer-reviewed conference proceedings. **ACM SIGKDD is CORE A\*** — the strongest venue on the business side of this review. |
| Deal Desk pillar | **Evaluation** (primary), **General process / audit** (secondary, via RBAC) |
| Key content | Two-dimensional taxonomy — *Evaluation Objectives* (behavior, capabilities, reliability, safety) × *Evaluation Process* (interaction mode, data, metrics computation, tooling, contexts). Section 5 is four **enterprise-specific challenges**: RBAC, reliability guarantees, long-horizon interaction, and policy/compliance adherence — which explicitly names *"approval workflows"* as an enterprise policy constraint. Supplies named multi-agent metrics: Collaborative Efficiency, Information Sharing Effectiveness, Adaptive Role Switching. Supplies **pass^k** as the strict consistency metric and **Task Completion Under Constraints** as the compliance metric. |
| The quotable sentence | *"Without explicit modeling of these constraints during evaluation, agents deemed 'correct' in traditional benchmarks may still fail in production due to policy violations or compliance risks."* (§5.4) |
| Why it matters | Three things at once: **(1)** it is the peer-reviewed, top-tier statement of the accuracy-paradox *principle* that B1 demonstrates *empirically*; **(2)** it gives the thesis a ready-made evaluation framework and named metrics instead of inventing them — which becomes RQ7; **(3)** its RBAC section partially covers what B2 was wanted for, from authors who build ERP software for a living. |
| Weakness to note | No PRISMA protocol or screening counts (weaker method than B4); 11 pages, so each sub-topic is brief; all four authors from one company, so "enterprise" reflects one vendor's view. Cite it as an expert-organised taxonomy, not a systematic review. |

### B8 — A Step Towards Cognitive Automation ⚠ PUBLISHER ABSTRACT ONLY

| | |
|---|---|
| Authors | Sascha Kaltenpoth, Alexander Skolik, Oliver Müller, Daniel Beverungen |
| Venue | BPM 2025, Lecture Notes in Computer Science, volume 16044, pp. 308–324 |
| DOI | 10.1007/978-3-032-02867-9_19 |
| Evidence role | Structured process-rule grounding |
| Access status | The complete chapter is subscription-only and was not obtained. Official Springer metadata confirms the peer-reviewed BPM 2025 paper, author order, page range, and abstract. |
| Safe LR use | The publisher abstract reports evaluation on 118 real-world process instances from a power-grid provider and a reduction in process failures from 16% to 1% when structured process rules were used. No detailed architecture, additional dataset, or procedural claims are permitted without the complete chapter. |

### B9 — Adding Decision Management to Robotic Process Automation ✅ FULL TEXT USED

| | |
|---|---|
| Authors | Maximilian Völker, Simon Siegert, Mathias Weske |
| Venue | BPM 2021 Blockchain and Robotic Process Automation Forum, LNBIP 428 |
| DOI | 10.1007/978-3-030-85867-4_3 |
| Evidence role | External decision management and DMN |
| LR use | Provides an architectural precedent for separating workflow automation from maintainable, versioned business-decision logic. It is RPA rather than LLM evidence and is not presented as proof of LLM performance. |

### B10 — Beyond Task Completion ✅ FULL TEXT VERIFIED

| | |
|---|---|
| Authors | Sreemaee Akshathala, Bassam Adnan, Mahisha Ramesh, Karthik Vaidhyanathan, Basil Muhammed, Kannan Parthasarathy |
| Venue | International Workshop on Agentic Engineering, AGENT '26, ACM, 2026, pp. 9–17 |
| DOI | 10.1145/3786167.3788414 |
| Evidence role | Trace-level agent assessment |
| Verified LR use | The complete nine-page paper verifies four assessment pillars, three production-motivated CloudOps scenarios, three independent runs per scenario, and static, dynamic, and judge-based evaluation. Table 3 reports 33% task completion and 0% policy adherence for the multi-agent S3 scenario, while Table 6 reports trace-level failures across the LLM, tools, memory, and environment pillars. |

### B11 — Solutions and Minimal Conflict Search for Product Configuration ✅ FULL TEXT VERIFIED

| | |
|---|---|
| Authors | Sebastian Velten, Christopher Hamkins |
| Venue | *Constraints*, 30, 35–61 |
| Year | 2025 |
| DOI | 10.1007/s10601-025-09381-2 |
| Evidence role | Conventional deterministic product configuration and conflict resolution |
| Verified LR use | The paper models product configuration with constraint programming and evaluates solution, conflict-detection, and resolution performance using real interaction cases. The configurator produces quotation information and transfers configuration outputs, including order-specific bills of materials, to ERP. It establishes a non-agentic baseline for enforceable configuration rules, explainable conflicts, and real-time decision support. |
| Limitation | One industrial product-configuration setting. It does not study LLMs, multi-agent coordination, credit, or approval routing. |

### B12 — Implementing Configure, Price, Quote in the Supply Chain ✅ FULL TEXT VERIFIED

| | |
|---|---|
| Authors | Ariane Blumentritt, Joachim Ehrenthal, Benjamin Haueter, Nadine Hitz, Muhammad Sufian |
| Venue | *Journal of Information Technology Teaching Cases*, 13(2), 246–254 |
| Year | 2023 |
| DOI | 10.1177/20438869221139596 |
| Evidence role | Conventional B2B CRM, CPQ, and ERP process baseline |
| Verified LR use | The case follows lead management, opportunity management, configuration, pricing, quotation, purchase order, and factory-order initiation. It documents spreadsheet errors, dependence on product-management expertise, and integration of CPQ with CRM and ERP. After implementation, rules and prices could be updated centrally, but approximately 30% of special requests still required manual action. |
| Limitation | A single teaching case without a controlled experiment or agentic-AI evaluation. It supports process description and implementation limitations, not causal performance claims. |

### Documented absence — no peer-reviewed CPQ + LLM-agent literature identified

The review now includes two peer-reviewed studies of conventional CPQ and product configuration, B11 and B12. However, the targeted search did not identify a peer-reviewed study integrating LLM agents with governed CPQ, pricing, credit, inventory, policy, and approval routing. Framing for the LR:

> Agentic CPQ is actively marketed by vendors, but those claims are vendor-reported and lack independent peer-reviewed evaluation.

Supported by O5's own evidence hierarchy (peer-reviewed vs. vendor-reported) — turns an absence into a documented observation, not an argument from silence.

---

## Rejected sources — recorded so the decision is not revisited

| Source | Reason |
|---|---|
| MASCA: LLM-based Multi-Agent System for Credit Assessment (arXiv:2507.22758) | Preprint; no peer-reviewed version located. Excluded under the no-preprint rule. |
| **Srivastav, *Multi-Agent Artificial Intelligence for Autonomous Enterprise Automation*** (SSRN, posted 17 Jul 2026, 45pp) | **Preprint AND quality-disqualified. Do not cite.** See below. |

**Why the Srivastav paper was rejected** (considered as a possible B2 substitute on 20 Sept and declined). Four independent grounds, any one sufficient:

1. **Contaminated front matter.** Its Ethics Approval statement reads: *"All data used in this research were obtained from publicly available datasets (BUSI – Breast Ultrasound Images Dataset)."* The paper is a literature review of enterprise automation containing no ultrasound data. Template text from an unrelated manuscript, never removed.
2. **Preprint-based evidence chain.** Its own §2.2 lists SSRN, Authorea and "AGPH Books" among its sources — two preprint repositories and a vanity publisher. Citing it imports non-peer-reviewed evidence one layer down.
3. **No PRISMA, no screening counts.** Calls itself a systematic review; reports no funnel, no screened total, no included total.
4. **Citation pattern.** Every in-text citation is a 2025 single-surname source. It discusses Contract Net Protocol, FIPA ACL, JADE, Paxos, Raft and BDI architectures — all with canonical originating papers — and cites none of them.

**Note on transparency flagging.** Flagging a weak source does not neutralise it: a flagged citation still tells the examiner the author read it and judged it usable. The ultrasound line makes that judgment indefensible and would cast doubt on the rest of the bibliography. Rejection, not flagging, is the correct handling here.

---

## Convergent findings across the whole pool (the strongest material in the LR)

### Finding 1 — bigger/more capable is not monotonically better (4 independent sources)

- **O4/SGT** (graph coordination): intermediate symbolic guidance beats both full autonomy and full prescription.
- **B6** (supply chain): performance "can vary non-monotonically with model size"; information-sharing alone beat information-sharing-plus-tools on cost.
- **B5** (finance, hypothesis not yet confirmed): coordination design may outweigh model scaling.
- **B3** (process QA): the best result in the paper (92.31%, single-process fine-tuning) beat several larger multi-process and RAG-only configurations.

Plus **B1**: two different models (Qwen2.5, llama3.1) failed in *opposite* directions — under-escalation vs. over-escalation — so the failure is model-specific, not a general LLM property.

**C007 is treated as a boundary condition, not rebutted.** Collaboration may help where work genuinely requires distributed information, role separation, negotiation, or permission boundaries, but it may add overhead when a capable single agent already performs well. This justifies an optional single-generalist comparison rather than an expected claim that the multi-agent system must win.

### Finding 2 — accuracy alone is an unsafe evaluation metric (4 sources, now including a top-tier statement of principle)

- **B1** (HR/compliance, *empirical demonstration*): 0.74 aggregate accuracy concealed 0.0 recall on the safety-critical subset.
- **B4** (credit, *quantified field survey*): only 7/60 papers report efficiency at all; explicit call for "evaluation frameworks beyond accuracy."
- **B7** (KDD '25, *stated principle*): agents "deemed 'correct' in traditional benchmarks may still fail in production due to policy violations or compliance risks"; task completion alone gives "limited fine-grained insight into failures."
- **O5 / B5** (orchestration/finance, *named missing benchmark*): both name the lack of an orchestration-quality benchmark as an open problem.

**This is now the best-evidenced claim in the entire LR** — one empirical demonstration, one quantified survey, one top-tier statement of principle, two independent acknowledgements of a missing benchmark. RQ5 no longer rests on the thesis's own assertion. B7 additionally supplies the *positive* form of the claim (what to measure instead), which becomes RQ7.

### Finding 3 — knowledge/policy overlap degrades a single generalist agent (1 source, concrete numbers)

- **B3**: combining 2 processes in one LLM's knowledge base dropped accuracy from 92.31% to ~82%, worse with overlapping vocabulary.

Direct, evidence-based argument for splitting Deal Desk agents by domain rather than one generalist agent — see RQ6. Single-source, so state it as "one study reports," not as established.

---

## Counter-evidence that must be addressed (not left out)

| ID | Paper | Venue | Status |
|---|---|---|---|
| C007 | Capable language models can outgrow the benefits of collaboration | *Nature Machine Intelligence* (2026) | Confirmed peer-reviewed. Used only at published-abstract level as a boundary condition. It supports the optional single-agent baseline. |
| C019 | More Capable, Less Cooperative? | arXiv (2026) | No verified peer-reviewed version identified. Excluded from the LR. |
| C047 | Why Do Multi-Agent LLM Systems Fail? | NeurIPS 2025, Datasets and Benchmarks Track | Confirmed peer-reviewed. Included as a core failure-taxonomy and trace-evaluation source. DOI: 10.52202/085713-4082. |

---

## Coverage check — Deal Desk pillars vs. papers

| Deal Desk pillar | Covered by | Status |
|---|---|---|
| Pricing / CPQ | B11 and B12 for the conventional process; no peer-reviewed governed LLM-agent CPQ implementation identified | ✅ Full-text business baseline plus a narrowly worded agentic gap |
| Inventory | B6 | ✅ Full text |
| Credit | B4 | ✅ Full text |
| Approval | B1 (+ O4, + B7 §5.4) | ✅ Full text |
| General process / audit | B1, B7 §5.1 RBAC, B8, B9 | ✅ Covered without relying on B2 |
| Process knowledge representation | B3 | ✅ Full text |
| Evaluation + coordination + cost | B4, B7, B10, C047, O5 | ✅ Full-text evidence, with C007 used only as an abstract-level boundary source |
| Orchestration architecture (general) | O1, O2, O3 | ✅ Full text |

---

## Final retained reference pool

### Full-text core sources, 15

| ID | Short title | Evidence role |
|---|---|---|
| O1 | Evolving Orchestration | Adaptive orchestration |
| O2 | ChatDev | Staged role-based workflow |
| O3 | CAMEL | Role-playing communication |
| O4 | Symbolic Guidance | Bounded autonomy; complete three-page extended abstract |
| O5 | LLM-Based Multi-Agent Orchestration survey | Orchestration taxonomy and benchmark gap |
| B1 | Governed Agentic Process Automation | Approval and compliance safeguards |
| B3 | BPLLM | Process-aware knowledge grounding |
| B4 | Interpretable LLMs for Credit Risk | Credit evaluation and interpretability |
| B6 | Agentic LLMs in the Supply Chain | Inventory coordination and bounded negotiation |
| B7 | Evaluation and Benchmarking of LLM Agents | Enterprise evaluation taxonomy |
| B9 | Adding Decision Management to RPA | External DMN decision services |
| B10 | Beyond Task Completion | Trace-level agent assessment |
| B11 | Solutions and Minimal Conflict Search | Deterministic product configuration |
| B12 | Implementing CPQ at Essemtec AG | CRM, CPQ, and ERP business-process baseline |
| C047 | Why Do Multi-Agent LLM Systems Fail? | Multi-agent failure taxonomy |

### Publisher-abstract sources, 2

| ID | Short title | Permitted use |
|---|---|---|
| B8 | A Step Towards Cognitive Automation | Only the process-rule result stated in the official abstract |
| C007 | Capable Language Models Can Outgrow Collaboration | Only the boundary condition and study scope stated in the published abstract |

### Excluded or optional sources

B2 and B5 remain abstract-only and are not used for detailed claims. C019 has no verified peer-reviewed version. KG-BDI is excluded because the complete paper was unavailable. The rejected Srivastav preprint remains excluded on both publication-status and quality grounds.

---

## Current draft gap statement

> Existing peer-reviewed work provides components for adaptive orchestration, symbolic guidance, rule-grounded execution, external decision management, credit evaluation, and supply-chain coordination. However, no peer-reviewed work was identified in this purposive review that integrates these components into a governed multi-agent Deal Desk architecture coordinating configuration, pricing, availability, credit or risk, policy compliance, and approval routing together. The remaining contribution is therefore an implementation and evaluation problem: applying deterministic control where required, bounded agent reasoning where appropriate, auditable shared state, and trace-level evaluation alongside final decision correctness.

**Defensibility note.** The gap statement is now sound **on the condition** that every absence claim is phrased as *"no peer-reviewed work was identified"* rather than *"no work exists"*, and that the purposive search strategy is declared in the methodology section (wording provided under Search Strategy above). With those two things in place, this statement is defensible without exhaustive corpus screening.

---

## Final research questions used in the thesis

The thesis and LR use only the following three questions. Phase 1B, Phase 1C, the evaluation plan, and the intermediate reports should use the same wording.

**Primary RQ.** How can a governed multi-agent orchestrator coordinate specialised agents to ensure business-rule compliance and decision completeness in B2B Deal Desk processing?

**Supporting RQ1.** Which Deal Desk decisions require deterministic business rules, which permit bounded agent reasoning, and how do these mechanisms affect constraint compliance, escalation accuracy, and latency?

**Supporting RQ2.** To what extent do orchestration-level trace metrics identify Deal Desk processing failures that are not visible from final-output accuracy alone?

## Archived candidate research questions, retained for design traceability

The seven earlier questions below remain in this tracking file because they show how the final questions were derived. They are **not separate thesis research questions** and should not appear as an additional RQ1 to RQ7 list in the thesis. Their useful elements are absorbed into the final three questions, implementation requirements, or evaluation objectives.

**RQ1 (orchestration).** How can a multi-agent architecture coordinate specialised agents for complex B2B deal processing?

**RQ2 (orchestration).** How can an orchestrator dynamically determine which specialised agents should participate in processing a deal?

**RQ3 (constraints, revised with B1).** Which Deal Desk decisions require formal constraint guarantees (floor/override, per B1), which permit bounded negotiation (per B6), and which can be left to learned routing — and what does each choice cost in accuracy, escalation rate and latency?

**RQ4 (enterprise integration).** How can specialised agents interact with enterprise systems/tools while preserving coherent deal state?

**RQ5 (evaluation, now well-evidenced).** How should an enterprise multi-agent Deal Desk system be evaluated beyond final-output correctness? Backed by a four-source convergent finding (B1, B4, B7, O5/B5).

**RQ6 (from B3).** Does a Deal Desk architecture with separate specialised agents per business domain (pricing, credit, inventory, approval) outperform a single generalist agent holding all policy knowledge — and does the advantage grow as more policy domains are added, mirroring the knowledge-base scaling degradation in Bernardi et al. (2024)?

**RQ7 (new, from B7).** Can the Deal Desk's orchestration quality be measured using the multi-agent collaboration metrics named in Mohammadi et al. (2025) — Collaborative Efficiency, Information Sharing Effectiveness, Adaptive Role Switching — alongside **Task Completion Under Constraints** and **pass^k**, and do those metrics detect failures that task-completion accuracy misses? **This is the strongest RQ in the set**: it turns RQ5's critique into a testable design, which is a bigger contribution than the critique alone, and it uses metrics defined in a peer-reviewed top-tier venue rather than invented for the thesis.

### How the archived questions map to the final structure

| Archived question | Current role |
|---|---|
| RQ1 and RQ2 | Absorbed into the Primary RQ and orchestrator design requirements. |
| RQ3 | Absorbed into Supporting RQ1. |
| RQ4 | Retained as an implementation requirement concerning tools and shared state, not a separate thesis RQ. |
| RQ5 and RQ7 | Combined and narrowed into Supporting RQ2. |
| RQ6 | Retained as an optional single-generalist comparison experiment, not a required RQ. |

---

## Commercial / Industry Landscape (not part of the peer-reviewed LR itself)

**These are products, not academic sources — never count as foundation papers or evidence.** Two purposes only:

**Purpose 1 — sharpen the gap argument.** These companies prove commercially that Deal Desk automation is a real, valuable problem — but none publish architecture, evaluation methodology, or metrics. That absence of open, evaluated, academically-studied architecture is itself part of the gap. Use as a short "Commercial Solutions" subsection in the LR write-up, separate from the academic Problem/Solution papers — motivation and context, not evidence.

**Purpose 2 — implementation reference during the build phase.** Agent roles, escalation triggers, "deal package"/exception-routing screen design.

### The list

**Dedicated Deal Desk Orchestrators & Management**
- **Momentum** — automates approvals/conversation tracking, syncs Salesforce/Slack/Zoom; auto-creates Slack "Deal Rooms" on risk triggers.
- **Moxo** — business service orchestration; "Deal Desk Approval Workflow" with AI agents preparing deal analyses.

**Native CRM & CPQ AI Agents**
- **Salesforce Agentforce (Deal Desk Agent)** — native to Salesforce CPQ. **Closest existing match to this thesis's concept — acknowledge explicitly with the supervisor.** Market leader doing much of this commercially inside one vendor's ecosystem.
- **DealHub AI** — full quote-to-revenue agentic platform: configuration, pricing, CLM, multi-tiered approvals.

**Specialized Sales & RevOps AI Startups**
- **Squid AI (DealFlow)** — ingests sales notes, updates CRM, structures approvals.
- **Salesbricks** — Deal Desk Agent inside Slack; auto-approves standard deals, routes exceptions.
- **Subskribe (DealDesk AI)** — conversational assistant for config checks and contract-term summarization.
- **Revolear** — listens to emails/meetings to generate deal terms, syncs across systems.

Repository reference (implementation-time): **`23f1002033/deal-desk`** on GitHub — LangGraph-based multi-agent RFP-to-proposal system, Coordinator + Pricing/Technical/Legal/Reviewer agents, discount-threshold escalation. Structurally close; study once implementation starts. (`JackJanoian/deal-desk` is unrelated — PE/M&A deal sourcing.)

### How this thesis differs

- Closed commercial products — no published architecture, no published evaluation, nothing peer-reviewed.
- Most are single-vendor/ecosystem-locked (Agentforce → Salesforce-only). This thesis is framework-agnostic, integrating across separate CRM and ERP systems (Phase1B §10.6).
- None appear to publish a clean separation between a coordination layer (Orchestrator) and an authority-decision layer (Approval Routing) as distinct, separately measurable components — a specific, defensible design contribution (Phase1B §5).
- Framing: an **evaluated, open multi-agent architecture study**, not an attempt to out-build Agentforce/DealHub. Deeper competitive comparison deliberately deferred beyond the thesis timeline.

---

## Progress log

- **20 Sept 2026** — 5 orchestration-side papers (O1–O5) deep-extracted and verified; 1 author-list error caught and corrected (O1); O1/O2 non-independence flagged. O4 was initially inaccessible from the environment and was verified later.
- **20 Sept 2026** — 6 business-side papers (B1–B6) identified and peer-review-verified; Pricing/CPQ confirmed as a documented literature absence.
- **20 Sept 2026** — Full-text extraction completed for **B1, B6**.
- **20 Sept 2026** — Full-text extraction completed for **B3, B4** — surfaced the knowledge-base scaling-degradation finding (B3) and the quantified interpretability/efficiency gaps (B4). Added RQ6. Strengthened the "accuracy alone is unsafe" convergent finding to three domains.
- **20 Sept 2026** — **B7 added and fully extracted** (Mohammadi et al., KDD '25, ACM SIGKDD, open access). Resolves the Evaluation pillar from a stronger venue than B5, partially covers B2's segregation-of-duties angle via RBAC, and supplies named multi-agent evaluation metrics. **Added candidate RQ7. B5 was downgraded from blocking to optional.** B2 was still treated as a material gap at this point, but was later excluded without blocking the LR. Author-order trap caught before it propagated (use the ACM Reference Format order).
- **20 Sept 2026** — **SSRN preprint (Srivastav) evaluated as a B2 substitute and rejected** on four grounds including contaminated front matter (an ultrasound-dataset ethics statement in an enterprise-automation review). Recorded in the rejected-sources table so the decision is not revisited. Added source-verification rules (8) and (9) as a result.
- **20 Sept 2026** — **187-paper candidate pool formally retired.** Review method restated as a *purposive search strategy*, to be declared in the methodology section; all absence claims to be phrased "no peer-reviewed work was identified." This closes the previously-open defensibility caveat without requiring exhaustive screening.
- **20 Sept 2026** — 3 counter-evidence papers (C007, C019, C047) identified. At this point only C007 was verified; C047 was subsequently verified as peer-reviewed NeurIPS evidence, while C019 remained unverified and was excluded.
- **20 Sept 2026** — Commercial/industry landscape compiled.
- **21 Sept 2026** — LR working draft completed: Introduction, Methodology, three Results groups, Discussion, and References. After the B8 evidence correction, the academic body contains approximately 3,440 words and follows the GIU Bachelor Thesis Assessment Scheme as the primary standard, with the Research Paper Writing course rubric as a structural and citation-compliance layer.
- **21 Sept 2026** — Initial source pool finalized for the working draft. This count was revised on 23 September after B8 was confirmed as subscription-only.
- **21 Sept 2026** — O1 verified as NeurIPS 2025, O4 bibliographic details corrected, O5 linked to its final journal record, and C047 verified as a peer-reviewed NeurIPS 2025 Datasets and Benchmarks paper.
- **22 Sept 2026** — Final thesis question structure locked to one Primary RQ and two Supporting RQs. The previous seven candidates remain below for design traceability but are not separate thesis questions.
- **23 Sept 2026** — B8 confirmed subscription-only. Its status was downgraded from full text to publisher-abstract level, unsupported procedural and dataset details were removed, and the source count was revised to thirteen full-text plus two abstract-level sources.
- **23 Sept 2026** — B10 complete text obtained and verified. Corrected its author names and venue to the ACM Reference Format and verified the four pillars, three scenarios, three runs per scenario, and Table 3 policy-adherence result.
- **24 Sept 2026** — B11 and B12 added from complete papers. B11 supplies the deterministic product-configuration baseline; B12 supplies the end-to-end conventional CRM, CPQ, and ERP business-process baseline requested by the supervisor. The retained pool is now fifteen full-text sources plus B8 and C007 at publisher-abstract level.
- **24 Sept 2026** — B1 and B3 evidence audit completed. B1 Tables 7, 10, and 11 confirmed the 166 profiles, 43 mandatory cases, 0.741 ungoverned accuracy, 0.000 mandatory-case recall, and 0.729 to 1.000 stability improvement. B3 Table 4 confirmed the 92.31%, 84.62%, and 80.53% process-knowledge results. B1 wording was corrected to state that the profiles were partner-validated synthetic data from an industrially grounded process.
- **25 Sept 2026** — Final LR quality pass completed. All 17 references were checked against official records, two-way citation matching was confirmed, source IDs were synchronized, Jannelli et al. was normalized to the 2025 advance-online record, the academic body was reduced to approximately 3,773 words, internal drafting notes were removed, and the clean Word version passed visual inspection.

### Still open

1. Obtain supervisor feedback on the final three-question structure, purposive methodology, gap statement, and optional single-generalist baseline.
2. Apply any supervisor-requested revisions.
3. Run the university plagiarism check on the post-feedback version.

### Immediate next action order

1. Present the submission-ready LR, three-question structure, purposive methodology, refined gap, and optional single-agent baseline to the supervisor.
2. Record and apply supervisor feedback.
3. Run the plagiarism check and freeze the post-feedback LR version.

**Current Phase 1A position:** the literature review is written, audited, synchronized, formatted, and ready for supervisor review. No additional literature expansion is required unless the supervisor requests it.

### Optional sources that are not required

- B2 full text may be added if the author supplies it, but the current LR does not depend on it.
- B5 full text may add finance-specific evaluation details, but B7 and C047 already support the evaluation argument more strongly.
- B8 full text may be reviewed later if institutional access becomes available, but the LR currently uses only claims stated in the official publisher abstract.
- KG-BDI remains excluded unless a legitimate complete paper becomes available. Abstract-level snippets must not support detailed claims.

---

## Not covered in this file

- Track B — agent architecture, execution flow, toolkit (Phase 1B, to be integrated later)
- Data strategy (Phase 1C, to be integrated later)
- Admin, supervisor, and deadline context (to be integrated later)
- Full 20+3-field paper-by-paper extraction with every table, quote and section number (`Business-Process-Governance-and-Evaluation-Study-Notes.md`)
