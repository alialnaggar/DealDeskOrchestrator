# Thesis Literature Extraction — Structured Article Extraction

## Purpose

This document contains the structured extraction of the five papers provided for the Bachelor’s thesis **Deal Desk Orchestrator (Multi-Agent System)**.

The extraction follows the thesis workflow:

1. Article identification and verification
2. Structured article extraction
3. Cross-paper comparison
4. Synthesis and research-gap development

### Important extraction rule

The content below is based on the supplied paper files. Where a point is an interpretation for thesis relevance rather than a statement explicitly made by the authors, it is labelled **Thesis interpretation**. No final thesis requirement, agent set, architecture, or research gap should be treated as established solely from these papers.

---

# Paper 1 — Multi-Agent Collaboration via Evolving Orchestration

## 1. Bibliographic / Verification Information

| Field | Extraction |
|---|---|
| Title | **Multi-Agent Collaboration via Evolving Orchestration** |
| Authors | Yufan Dang, Chen Qian, Xueheng Luo, Jingru Fan, Zihao Xie, Ruijie Shi, Weize Chen, Cheng Yang, Xiaoyin Che, Ye Tian, Xuantang Xiong, Lei Han, Zhiyuan Liu, Maosong Sun |
| Venue | **NeurIPS 2025**, 39th Conference on Neural Information Processing Systems |
| Year | 2025 |
| DOI | 10.52202/085713-5502 |
| Code | GitHub repository identified in the paper: `OpenBMB/ChatDev/tree/puppeteer` |
| Research type | Empirical research / system proposal |
| Peer-reviewed status | Conference paper at NeurIPS 2025; the supplied manuscript identifies it as a NeurIPS paper |
| Main research area | LLM-based multi-agent systems; dynamic orchestration; centralized coordination; reinforcement learning |
| Primary relevance to thesis | **Very high** for orchestration architecture and dynamic agent selection |

## 2. Problem

The paper starts from the observation that LLMs are increasingly used for complex reasoning and that multiple specialized agents can improve problem solving. However, many existing multi-agent systems rely on **static organizational structures**.

The authors identify several problems:

- Static agent topologies may not adapt when task complexity changes.
- Increasing the number of agents can create coordination overhead.
- Agents may perform redundant reasoning.
- Predefined chains, trees, or graphs do not necessarily represent the best collaboration structure for every task.
- Agent selection and coordination can become a scalability bottleneck.

The central problem is therefore not simply how to create multiple capable agents, but **how to dynamically decide which agents should participate and in what sequence as the task evolves**.

## 3. Objective / Research Question

The paper proposes a **puppeteer-style paradigm** in which a centralized orchestrator dynamically controls specialized agents.

The central idea is:

> A learned centralized policy observes the evolving task state and selects which agent should act next.

The orchestrator is trained through reinforcement learning so that the organization of the multi-agent system itself can improve over time.

### Core objective

Develop a multi-agent orchestration mechanism that:

- dynamically selects agents;
- adapts collaboration to task state;
- reduces unnecessary coordination;
- works with heterogeneous or homogeneous agent models;
- improves performance without requiring a manually designed topology for every task.

## 4. Context

The context is broad LLM reasoning rather than a specific enterprise domain.

The paper evaluates tasks including:

- mathematical reasoning;
- knowledge-intensive reasoning;
- general benchmarks;
- tool-augmented tasks;
- embodied / interactive environments.

This means the architecture is presented as a **general orchestration mechanism**, not as a Deal Desk-specific architecture.

## 5. Conceptual Foundation

The paper models a multi-agent system as a directed graph:

- nodes = agents;
- edges = dependency or information flow;
- source = task input;
- sink = unified task output.

The authors connect this representation to graph-of-thought style reasoning.

The important conceptual move is that the graph is not treated as permanently fixed. The orchestration policy can effectively construct a task-specific collaboration structure during execution.

---

## 6. Proposed Solution

### 6.1 Centralized Puppeteer

The central component is the **Puppeteer**, a centralized orchestrator.

Instead of each agent independently deciding whom to communicate with, the Puppeteer:

1. observes the current global task state;
2. considers the available agents;
3. selects an agent;
4. activates that agent;
5. incorporates the resulting state;
6. selects the next agent.

This separates:

- **agent behavior** — what an individual specialist does;
- **orchestration** — which specialist should act next.

This separation is highly relevant to the Deal Desk Orchestrator concept.

### 6.2 Serialized Orchestration

The paper addresses the enormous number of possible graph structures by **serializing** the collaborative reasoning process.

Rather than explicitly searching the entire graph topology space, the orchestrator unfolds the collaboration into a sequence.

Conceptually:

`Task → Agent A → Agent B → Agent C → Agent B → Agent D → Final Output`

The authors emphasize that this sequential execution can later be interpreted as a directed graph of dependencies.

This is important because it provides a practical way to control a potentially complex multi-agent topology.

### 6.3 Sequential Decision Process

The orchestrator is formalized as a policy:

`π(agent | current state, task specification)`

At each time step:

- current state is observed;
- one agent is selected;
- the selected agent performs reasoning/tool use;
- the global state is updated;
- another agent may be selected.

This creates a dynamic control loop.

---

## 7. Agent Responsibilities

The paper contains both tool-use agents and reasoning agents.

### Tool-use agents

| Agent | Main responsibility |
|---|---|
| ArxivAgent | Search academic papers |
| WebsiteAgent | Access websites |
| PythonAgent | Execute Python |
| PlannerAgent | Planning-related reasoning |
| ReasoningAgent | General reasoning |
| CriticAgent | Critique solutions |
| ReflectAgent | Reflection |
| QuestionAgent | Generate questions |
| SummarizerAgent | Summarization |
| ConcluderAgent | Produce conclusions |
| ModifierAgent | Modify/refine outputs |

The exact implementation separates actions into:

### Tool-use actions

- `read_file`
- `search_arxiv`
- `search_bing`
- `access_website`
- `run_python`

### Reasoning patterns

- reasoning
- critique
- reflect
- question
- summarize
- conclude
- modify
- planning

### Thesis interpretation

This demonstrates a useful distinction for the thesis:

**specialized agents do not necessarily have to correspond to business departments.**

A multi-agent system can contain:

- domain agents;
- reasoning agents;
- validation agents;
- tool-use agents;
- orchestration agents.

This should inform, but not determine, the eventual Deal Desk architecture.

---

## 8. Coordination Mechanism

The central coordination mechanism is **centralized dynamic orchestration**.

The Puppeteer decides:

> Who should act next?

Rather than requiring every agent to maintain a complete understanding of all other agents.

The architecture therefore reduces the responsibility of individual agents for global coordination.

### Key property

Agent selection is **state-dependent**.

The same agent does not necessarily act at every step.

Example conceptual flow:

`Task → Planner → Pricing-like specialist → Critic → Inventory-like specialist → Critic → Conclusion`

The actual paper does not use these Deal Desk roles; this example is a **thesis interpretation**.

---

## 9. Communication

Communication is primarily mediated through the evolving global/task state.

The orchestrator selects the next agent and the agent receives relevant state/context.

The system is therefore different from a pure peer-to-peer conversation where agents independently select communication partners.

---

## 10. Tools / External Systems

The implementation contains tool-use capabilities including:

- web search;
- academic search;
- website access;
- Python execution;
- file reading.

The paper therefore demonstrates that orchestration can control not only pure reasoning agents but also agents capable of interacting with external tools.

### Thesis relevance

This is particularly relevant for a Deal Desk system because a commercial workflow will likely require access to:

- CRM;
- CPQ;
- ERP;
- pricing databases;
- inventory systems;
- credit information;
- approval services.

The paper does not implement those enterprise systems. The connection is therefore a **thesis interpretation**, not a reported experiment.

---

## 11. Methodology

The paper uses empirical evaluation.

The Puppeteer is trained through online reinforcement learning.

The authors compare:

- baseline models;
- existing agent workflow approaches;
- Puppeteer;
- Puppeteer-Mono.

Two broad configurations are considered:

### Puppeteer-Mono

Agents are driven by the same model.

### Puppeteer

Agents can be driven by a diverse set of models.

This allows the authors to test whether centralized orchestration works with both homogeneous and heterogeneous agent populations.

---

## 12. Evaluation

The paper evaluates performance on multiple benchmark datasets, including:

- GSM-Hard;
- MMLU-Pro;
- SRDD;
- Commonsense / reasoning benchmarks.

The manuscript reports initialized versus evolved performance.

The reported results show improvements after orchestration policy evolution.

For example, in the reported Mimas setting:

- Puppeteer average: **0.6273 initialized → 0.6324 evolved**
- Puppeteer-Mono Llama-3.1-8B: **0.5068 → 0.6147**

In the reported Titan setting:

- Puppeteer average: **0.6893 → 0.7731**
- Puppeteer-Mono Llama-3.1-405B: **0.6671 → 0.7453**

The paper argues that the learned centralized orchestrator can coordinate both heterogeneous and same-model agents.

### Important interpretation

These results establish evidence for the **orchestration mechanism under the evaluated benchmark conditions**.

They do not establish that centralized orchestration is universally optimal for enterprise workflows.

---

## 13. Efficiency

The paper explicitly examines performance versus computational cost.

The authors argue that dynamic orchestration can avoid unnecessary agent execution.

The learned system tends toward more compact reasoning structures.

The appendix includes token-cost analysis and performance-cost trade-offs.

### Thesis relevance

For the Deal Desk implementation, this suggests that an orchestrator should not simply call every specialist for every deal.

Instead, it could potentially:

- call only relevant specialists;
- stop when sufficient evidence exists;
- request re-validation only when necessary;
- avoid redundant checks.

This is a **design implication**, not a requirement established by the paper.

---

## 14. Emergent Organization

One of the paper's important findings is that the learned organizational topology can evolve.

The authors observe more compact and cyclic reasoning structures emerging during orchestration.

This is significant because the collaboration structure is not necessarily a fixed chain.

A system can learn patterns such as:

`A → B → C → B → D`

rather than always:

`A → B → C → D`

This provides an important conceptual basis for dynamic re-checking.

For a Deal Desk example, a thesis implementation could theoretically have:

`Pricing → Credit → Pricing → Approval`

when the credit result changes the pricing conditions.

Again, this is a **thesis interpretation**.

---

## 15. Findings

### Main findings

1. A centralized learned orchestrator can dynamically select agents.
2. Dynamic selection can outperform static or manually structured collaboration under the evaluated settings.
3. The approach works with both homogeneous and heterogeneous agent configurations.
4. Evolved orchestration can improve average benchmark performance.
5. More compact/cyclic organizational structures emerge during learning.
6. Tool-use and reasoning agents can be combined under the same orchestration mechanism.
7. Orchestration can be optimized jointly with performance and token efficiency.

---

## 16. Limitations

The authors explicitly identify several limitations:

### Coarse rewards

The Puppeteer currently uses relatively coarse rewards based on:

- final output;
- token usage.

The authors suggest that step-level correctness could provide better optimization signals.

### Fixed agent/tool set

The framework assumes a fixed collection of agents and tools.

The authors identify dynamic modification of agents/tools as future work.

### Mis-coordination

The system can occasionally exhibit:

- mis-coordination;
- deceptive agreement.

This means orchestration does not automatically guarantee reliable coordination.

### Computational complexity

Training the orchestrator is computationally expensive.

The paper reports use of:

- NVIDIA A800 GPUs;
- multiple GPUs;
- online training interleaved with inference.

---

## 17. Enterprise Relevance

### Direct evidence

The paper provides a general mechanism for:

- dynamic agent selection;
- centralized orchestration;
- tool use;
- adaptive collaboration.

### Not directly demonstrated

The paper does **not** demonstrate:

- CRM integration;
- CPQ integration;
- ERP integration;
- B2B quoting;
- pricing approval;
- credit approval;
- commercial deal management.

### Thesis interpretation

The paper can therefore support the **orchestration layer** of the Deal Desk Orchestrator, rather than serving as direct evidence for the business-domain design.

---

## 18. Deal Desk Relevance

Potential mappings:

| Paper concept | Potential Deal Desk interpretation |
|---|---|
| Puppeteer | Deal Desk Orchestrator |
| Specialized agents | Pricing / Inventory / Credit / Approval specialists |
| Dynamic agent selection | Invoke only relevant deal specialists |
| Global state | Current deal context |
| Tool-use agents | CRM/CPQ/ERP/API integration |
| Critic | Validation/review mechanism |
| Reflection | Re-check after a failed or uncertain validation |
| Serialized orchestration | Executable deal-processing workflow |
| Learned topology | Future adaptive orchestration |

These mappings are **proposed thesis interpretations**, not claims that the paper evaluated Deal Desk systems.

---

## 19. Potential Gap Evidence

The paper leaves open several areas relevant to this thesis:

- fixed agent/tool set;
- coarse-grained reward signals;
- limited domain-specific enterprise validation;
- need for more reliable coordination;
- need to dynamically adapt agent/tool composition.

A potential thesis contribution could therefore investigate a **structured enterprise workflow in which specialized agents interact with business systems under an explicit orchestrator**.

This should be confirmed against the remaining literature before becoming the formal research gap.

---

## 20. Evidence Locations

| Topic | Location in paper |
|---|---|
| Centralized Puppeteer | Section 2.1 |
| Serialized orchestration | Section 2.1 |
| Dynamic policy | Section 2.1 |
| Benchmark evaluation | Section 3 |
| Agent configuration | Appendix B.1 |
| Tool-use agents | Appendix B.1 |
| Reasoning agents | Appendix B.1 |
| Computational resources | Appendix C |
| Limitations | Appendix D |
| Token-cost analysis | Appendix A.1 |
| Emergent behavior | Appendix A.3 |

---

# Paper 2 — ChatDev: Communicative Agents for Software Development

## 1. Bibliographic / Verification Information

| Field | Extraction |
|---|---|
| Title | **ChatDev: Communicative Agents for Software Development** |
| Authors | Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, Maosong Sun |
| Venue | Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL 2024), Volume 1: Long Papers |
| Year | 2024 |
| Pages | 15174–15186 |
| Research type | Empirical system paper |
| Peer-reviewed status | ACL conference long paper |
| Main research area | LLM multi-agent collaboration; role specialization; communication; software development |
| Primary thesis relevance | **Very high** for specialized agent roles, staged workflows, communication and validation |

## 2. Problem

Software development is complex and requires different roles:

- architecture/design;
- programming;
- reviewing;
- testing.

Previous deep-learning approaches often optimize individual stages independently, resulting in fragmented development processes.

The paper asks whether LLM agents with specialized roles can cooperate through language to perform an end-to-end development process.

---

## 3. Objective

ChatDev aims to provide a unified multi-agent framework in which specialized LLM agents cooperate through communication.

The two key mechanisms are:

1. **Chat Chain**
2. **Communicative Dehallucination**

The goal is to transform software development into a structured sequence of agent interactions.

---

## 4. Context

The application domain is software development.

This is useful for the thesis because it is an example of a complex business-like process decomposed into specialized roles.

However, the domain differs from commercial deal processing.

---

# 5. Proposed Architecture

## 5.1 Role-based agents

ChatDev assigns different roles to agents.

The implementation described in the evaluation uses:

- CEO;
- CTO;
- programmer;
- reviewer;
- tester.

The agents are divided across **five subtasks and three phases**.

The roles are encoded in system prompts.

This means the system relies on both:

- agent specialization;
- process structure.

---

## 5.2 Chat Chain

The **Chat Chain** decomposes software development into phases and subtasks.

Instead of sending the entire problem to every agent, each phase has a specific responsibility.

This produces a structured process:

`Requirement → Design → Coding → Review → Testing → Final Software`

The exact internal phases contain role-specific communication.

### Key principle

Agents do not all communicate with everyone at all times.

Communication follows a predefined process.

This provides:

- predictability;
- context control;
- specialization;
- reduced unnecessary context.

---

## 5.3 Memory

ChatDev explicitly separates memory into:

### Short-term memory

Contains dialogue inside the current phase.

### Long-term memory

Carries the solution from previous phases into subsequent phases.

Instead of passing the complete conversation history forward, the framework transmits relevant completed solutions.

This reduces context overload.

### Thesis relevance

This is directly relevant to the Deal Desk Orchestrator because a deal may pass through several validation stages.

Instead of giving every agent the entire history, the orchestrator could maintain:

- global deal state;
- phase-specific context;
- validated outputs from previous agents.

This is a **design implication**.

---

# 6. Communicative Dehallucination

A major contribution is a communication mechanism designed to reduce coding hallucinations.

The basic problem:

`Instruction → Answer`

can be insufficient when the instruction is vague.

ChatDev therefore allows the assistant agent to ask for clarification or request a more precise modification before producing a final response.

This introduces more granular communication.

### Conceptual process

`Instruction → Clarification → Specific requirement → Solution → Refinement`

The mechanism is especially useful for:

- ambiguous requirements;
- incomplete code;
- incorrect implementation;
- missing dependencies;
- inconsistent outputs.

---

# 7. Agent Responsibilities

| Role | Responsibility |
|---|---|
| CEO | Overall task / project direction |
| CTO | Technical architecture and technical decisions |
| Programmer | Implementation |
| Reviewer | Review and identify issues |
| Tester | Validate functionality |

The important point is not the exact roles themselves, but the principle of **specialized responsibility**.

### Thesis interpretation

For Deal Desk, this raises the question:

> Which commercial decisions are sufficiently distinct that they deserve specialized agents?

That question should be answered from the literature plus the actual thesis scope, not copied from ChatDev.

---

# 8. Coordination

ChatDev uses **structured sequential coordination**.

The process is largely predetermined:

- phases;
- roles;
- communication structure;
- termination conditions.

This is different from Paper 1.

### Comparison

| ChatDev | Puppeteer |
|---|---|
| Mostly predefined workflow | Dynamically learned workflow |
| Static role structure | Dynamic agent selection |
| Human-designed phases | Learned orchestration policy |
| Communication protocol predefined | Orchestrator selects next agent |
| Strong process predictability | Stronger adaptability |

This contrast is important for the thesis architecture decision.

---

# 9. Tools / System Interaction

ChatDev integrates Python 3.11.4 for feedback during the evaluation.

The paper is primarily about language-based software generation rather than enterprise API integration.

It does not demonstrate CRM, CPQ or ERP integration.

---

# 10. Methodology

The authors construct a **Software Requirement Description Dataset (SRDD)**.

It contains:

- 1,200 software task prompts;
- 5 main categories;
- 40 subcategories;
- 30 tasks per subcategory.

Categories include:

- Education;
- Work;
- Life;
- Game;
- Creation.

The authors compare ChatDev with:

- GPT-Engineer;
- MetaGPT.

---

# 11. Evaluation Metrics

ChatDev uses four primary metrics:

### Completeness

Whether generated software is complete rather than containing placeholders.

### Executability

Whether the generated software can compile and run.

### Consistency

How closely generated software aligns with the original requirements.

### Quality

Product of the three dimensions:

`Quality = Completeness × Executability × Consistency`

---

# 12. Evaluation Results

Reported average results:

| Method | Completeness | Executability | Consistency | Quality |
|---|---:|---:|---:|---:|
| GPT-Engineer | 0.5022 | 0.3583 | 0.7887 | 0.1419 |
| MetaGPT | 0.4834 | 0.4145 | 0.7601 | 0.1523 |
| ChatDev | **0.5600** | **0.8800** | **0.8021** | **0.3953** |

The paper also performs pairwise evaluation using GPT-4 and human evaluators.

Reported ChatDev win rates include:

- GPT-Engineer: 77.08% GPT-4 evaluation;
- GPT-Engineer: 90.16% human evaluation;
- MetaGPT: 57.08% GPT-4 evaluation;
- MetaGPT: 88.00% human evaluation.

These are the paper's reported evaluation results and should not be generalized beyond its benchmark setting.

---

# 13. Ablation Findings

The ablation study removes:

- phases;
- communicative dehallucination;
- role prompts.

Important observations:

- code completion improves completeness;
- testing is important for executability;
- removing communicative dehallucination reduces performance;
- removing role definitions produces a particularly large degradation.

This provides empirical evidence that **agent specialization and workflow stages are not merely decorative prompt labels**; they can affect system performance.

---

# 14. Communication Analysis

The paper examines communication across:

- natural language;
- programming language.

The authors argue that natural language is useful for requirements and design, while programming-language communication is useful for debugging and implementation.

This demonstrates that different stages may benefit from different communication representations.

---

# 15. Findings

1. Complex tasks benefit from decomposition.
2. Specialized roles can improve cooperation.
3. Structured multi-phase workflows provide process control.
4. Communication itself can be used as a mechanism for iterative refinement.
5. Testing and review provide important validation stages.
6. Role prompts materially influence agent behavior.
7. Multi-agent systems can produce larger and more feature-rich software, but at higher token/time cost.

---

# 16. Limitations

The authors caution that:

- agent capabilities can be overestimated;
- vague requirements produce weak implementations;
- current systems are better suited to prototypes than complex real-world applications;
- general software evaluation is difficult;
- multi-agent systems consume more tokens and time;
- future systems should reduce interaction cost.

These limitations are highly relevant to an enterprise thesis.

---

# 17. Enterprise Relevance

The paper demonstrates a general pattern applicable to business workflows:

`Complex task → specialized roles → staged coordination → review → validation → final result`

This is one of the strongest conceptual connections to the Deal Desk thesis.

However, the paper does not demonstrate commercial deal processing.

---

# 18. Deal Desk Relevance

Potential mapping:

| ChatDev concept | Deal Desk interpretation |
|---|---|
| CEO / coordinator | Deal Desk Orchestrator |
| Specialized roles | Business-specialist agents |
| Chat Chain | Deal processing workflow |
| Reviewer | Deal validation agent |
| Tester | Policy / consistency validation |
| Long-term memory | Persisted validated deal state |
| Communicative dehallucination | Clarification / exception handling |
| Phase termination | Validation gate |

These are thesis interpretations.

---

# 19. Potential Research-Gap Evidence

ChatDev provides strong evidence for specialized role-based agents and staged workflows, but:

- its workflow is primarily static;
- it does not focus on enterprise commercial operations;
- it does not model pricing, inventory, credit and approvals;
- it does not evaluate cross-system enterprise coordination;
- its validation mechanisms are software-development-specific.

Therefore, it can support the thesis motivation for **specialized agents + structured orchestration**, while leaving the commercial enterprise setting open.

---

# 20. Evidence Locations

| Topic | Location |
|---|---|
| ChatDev architecture | Section 3 |
| Chat Chain | Section 3.1 |
| Memory | Section 3.1 |
| Communicative Dehallucination | Section 3.2 |
| Evaluation setup | Section 4 |
| Metrics | Section 4 |
| Ablation | Section 4.2 |
| Communication analysis | Section 4.3 |
| Limitations | Section 6 |

---

# Paper 3 — CAMEL: Communicative Agents for “Mind” Exploration of Large Language Model Society

## 1. Bibliographic / Verification Information

| Field | Extraction |
|---|---|
| Title | **CAMEL: Communicative Agents for “Mind” Exploration of Large Language Model Society** |
| Authors | Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, Bernard Ghanem |
| Venue | NeurIPS 2023 |
| Year | 2023 |
| Research type | Framework + empirical evaluation |
| Peer-reviewed status | NeurIPS conference paper as identified in supplied manuscript |
| Main research area | Communicative agents; role-playing; autonomous cooperation |
| Primary thesis relevance | **High** for role assignment, agent-to-agent communication, task planning/execution |

---

# 2. Problem

CAMEL begins from a simple problem:

LLMs can solve complex tasks, but they often require humans to repeatedly guide the conversation.

The authors ask whether human intervention can be reduced by allowing agents to autonomously communicate with each other.

The central challenge is therefore:

> How can multiple LLM agents cooperate autonomously while maintaining their assigned roles and progressing toward a common task?

---

# 3. Objective

CAMEL proposes a role-playing framework in which:

- an AI user acts as planner/instructor;
- an AI assistant acts as executor;
- both share a common task;
- agents communicate through multiple turns;
- human involvement is minimized.

---

# 4. Role-Playing Framework

The framework starts with:

1. human idea;
2. selected roles;
3. task specification;
4. role assignment;
5. autonomous conversation;
6. task completion.

Example from the paper:

**Idea:** develop a stock-trading bot.

Potential roles:

- Python Programmer;
- Stock Trader.

A task-specifier agent converts the vague idea into a more concrete task.

---

# 5. Agent Responsibilities

| Agent | Responsibility |
|---|---|
| Task Specifier | Convert preliminary idea into concrete task |
| AI User | Planner / instructor |
| AI Assistant | Executor / solution provider |
| Critic | Evaluate/select proposals or provide feedback |

This is an important early example of separating **planning** from **execution**.

---

# 6. Task Specification

The task-specifier agent is introduced because a non-expert human may have only a vague idea.

The agent turns:

`Idea → Specific executable task`

This is relevant to enterprise systems because business users often express objectives at a high level.

### Thesis interpretation

A Deal Desk user might specify:

> “Process this customer deal.”

An orchestration layer could theoretically translate that into structured subtasks.

However, the thesis should not assume this component is required unless supported by the final requirements.

---

# 7. Agent Communication

CAMEL uses an instruction-following loop.

At each time step:

1. AI User generates an instruction;
2. AI Assistant receives it;
3. Assistant produces a solution;
4. conversation state is updated;
5. User produces the next instruction.

The authors formalize the evolving message set.

This creates an iterative planning/execution process.

---

# 8. Critic-in-the-Loop

CAMEL also introduces a critic capable of:

- selecting proposals;
- providing feedback;
- supporting tree-search-like task solving.

The critic can be an AI agent or a human.

This is relevant to the thesis because it demonstrates that an orchestrated system can include a **validation / critique role in addition to domain specialists**.

---

# 9. Inception Prompting

The framework uses three major prompts:

1. Task Specifier Prompt;
2. Assistant System Prompt;
3. User System Prompt.

These prompts establish:

- roles;
- task;
- communication rules;
- termination conditions;
- constraints.

A central design concern is preventing unwanted behavior such as role flipping.

---

# 10. Observed Coordination Problems

CAMEL reports several challenges.

### Role flipping

Agents can switch their intended roles.

### Repetition

The assistant may simply repeat the user's instructions.

### Flake replies

An agent may promise to do something without actually doing it.

### Infinite loops

Agents can repeatedly communicate without advancing the task.

These are important because they show that **multi-agent communication does not automatically imply effective coordination**.

---

# 11. Termination Conditions

The framework uses explicit termination conditions:

- user does not instruct for three rounds;
- assistant instructs the user, indicating role reversal;
- `<CAMEL_TASK_DONE>` token;
- token limit;
- maximum of 40 messages.

This is directly relevant to orchestration design.

A production workflow needs explicit rules for:

- success;
- failure;
- timeout;
- repeated communication;
- escalation.

---

# 12. Experimental Setup

For the AI Society experiments, the paper generated:

- 50 assistant roles;
- 50 user roles;
- 10 tasks per role combination;
- 25,000 conversations.

It also created:

- CAMEL AI Society;
- CAMEL Code;
- CAMEL Math;
- CAMEL Science.

---

# 13. Evaluation

CAMEL evaluates agent solutions against single-shot GPT-3.5 solutions.

### Human evaluation

453 responses were collected for AI Society.

Reported results:

- CAMEL: 76.3% wins;
- GPT-3.5: 10.4%;
- Draw: 13.3%.

### GPT-4 evaluation

AI Society:

- CAMEL: 73%;
- GPT-3.5: 23%;
- Draw: 4%.

Code:

- CAMEL: 76%;
- GPT-3.5: 24%;
- Draw: 0%.

These results concern the paper's experimental setup and should not be treated as general proof that multi-agent systems always outperform single-agent systems.

---

# 14. Fine-Tuning / Knowledge Experiment

The paper also fine-tunes LLaMA-7B progressively on:

- AI Society;
- Code;
- Math;
- Science.

The authors evaluate the resulting model on multiple domains.

The paper reports improvements as datasets are added.

---

# 15. HumanEval

The CAMEL-7B model reports:

| Model | HumanEval pass@1 | HumanEval pass@100 | HumanEval+ pass@1 | HumanEval+ pass@100 |
|---|---:|---:|---:|---:|
| GPT-3.5-turbo | 69.4 | 94.0 | 61.7 | 89.8 |
| LLaMA-7B | 10.5 | 36.5 | — | — |
| Vicuna-7B | 11.0 | 42.9 | 9.9 | 34.7 |
| CAMEL-7B | 14.0 | 57.9 | 12.2 | 50.0 |

The result supports the paper's claim that the generated multi-domain datasets can improve the fine-tuned model's coding performance relative to the other open models tested.

---

# 16. Findings

1. Role-playing can enable autonomous multi-agent cooperation.
2. Separating planner and executor roles provides a structured interaction mechanism.
3. Task specification can reduce the burden on human users.
4. Critics can provide additional control.
5. Prompt-based role constraints are important.
6. Explicit termination rules are necessary.
7. Autonomous agents can still exhibit loops, role reversal and unproductive communication.

---

# 17. Limitations / Weaknesses Relevant to Thesis

The framework is primarily:

- prompt-driven;
- conversational;
- two-agent in its central formulation.

It does not directly solve:

- enterprise integration;
- deterministic business rules;
- transactional workflows;
- commercial approvals;
- enterprise data consistency.

The paper's evaluation also relies heavily on model-based judging and generated datasets, which should be considered when using it as evidence.

---

# 18. Enterprise Relevance

CAMEL provides useful design primitives:

- role assignment;
- planner/executor separation;
- task specification;
- critic;
- termination;
- autonomous communication.

These are transferable architectural concepts.

---

# 19. Deal Desk Relevance

Potential mapping:

| CAMEL concept | Deal Desk interpretation |
|---|---|
| Task Specifier | Convert business request into structured deal task |
| AI User / Planner | Orchestration/planning layer |
| AI Assistant / Executor | Specialist agent |
| Critic | Validation/review |
| Inception Prompting | Agent role and protocol definition |
| Message history | Deal execution context |
| Termination token | Deal completion state |

Again, these are **thesis interpretations**.

---

# 20. Potential Gap Evidence

CAMEL leaves open the question of how role-based LLM agents can operate reliably inside **structured enterprise processes with external systems and deterministic constraints**.

That distinction is particularly relevant to a Deal Desk system.

---

# 21. Evidence Locations

| Topic | Location |
|---|---|
| Role-playing framework | Section 3.1 |
| Task specification | Section 3.1 |
| Planner/executor roles | Section 3.1 |
| Critic | Section 3.1 |
| Inception prompting | Section 3.2 |
| Coordination problems | Section 4.1 |
| Termination | Section 4.1 |
| Agent evaluation | Section 5.1 |
| Human/GPT-4 evaluation | Section 5.1 |
| HumanEval | Section 5.3 |

---

# Paper 4 — Symbolic Guidance for LLM Agents in Distributed Multiagent Coordination

## 1. Bibliographic / Verification Information

| Field | Extraction |
|---|---|
| Title | **Symbolic Guidance for LLM Agents in Distributed Multiagent Coordination: Extended Abstract** |
| Authors | Ben Rachmut, Ning Zhang, Yevgeniy Vorobeychik, William Yeoh |
| Venue | AAMAS 2026, Extended Abstracts |
| Conference | 25th International Conference on Autonomous Agents and Multiagent Systems |
| Date | May 25–29, 2026 |
| Pages | 3356–3358 |
| DOI | 10.65109/KEVK7310 |
| Research type | Empirical extended abstract |
| Main area | Distributed coordination; adjustable autonomy; symbolic guidance |
| Primary thesis relevance | **High** for reliability, autonomy control, and coordination constraints |

---

# 2. Problem

LLM agents can reason flexibly, but distributed coordination can become unreliable when agents have too much unrestricted autonomy.

Classical symbolic distributed algorithms offer stronger structure and formal guarantees, but they can be too rigid for underspecified natural-language tasks.

The paper therefore investigates a middle ground:

> How much algorithmic structure should be provided to an LLM agent?

---

# 3. Objective

The paper introduces the:

## Symbolic Guidance Taxonomy (SGT)

SGT characterizes a spectrum between:

- maximum autonomy;
- partial symbolic guidance;
- complete algorithmic prescription.

The purpose is to understand how autonomy level affects distributed coordination.

---

# 4. SGT Concept

The paper defines a guidance strategy as:

`G(S, E; A) → I`

where:

- `A` = symbolic algorithm;
- `S` = which algorithmic components are exposed;
- `E` = representation/encoding;
- `I` = guidance supplied to the agent.

The important insight is that autonomy is not simply:

`autonomous vs non-autonomous`.

It is a spectrum.

---

# 5. Autonomy Spectrum

### Level 1 — Unguided

Agent receives no symbolic algorithmic guidance.

Maximum autonomy.

### Level 2 — Function Description

Agent receives partial information describing algorithmic functions.

### Level 3 — Function Pseudocode

Agent receives pseudocode for particular functions.

### Level 4 — Main Pseudocode

Agent receives more of the algorithm's structure.

### Level 5 — Full Pseudocode

Agent receives a highly prescriptive algorithm.

Minimum autonomy.

---

# 6. Main Finding

The relationship between autonomy and coordination performance is **non-monotonic**.

The paper reports that intermediate autonomy levels generally perform better than:

- fully unguided agents;
- fully prescribed agents.

In particular, function-level guidance is identified as a robust configuration.

This is important for the thesis because an enterprise orchestrator may need to balance:

- LLM flexibility;
- deterministic business rules.

---

# 7. Experimental Domains

The authors use three graph-based coordination domains:

- graph coloring;
- matching;
- vertex cover.

They test:

- local variants;
- global variants.

The experiments use the Maximal Independent Set (MIS) heuristic as the underlying symbolic algorithm.

---

# 8. Evaluation Metric

Coordination quality is evaluated using:

`ln(1 + SSE)`

where SSE measures deviations from feasibility or optimality.

Lower values are better.

The experiments compare the different symbolic guidance levels.

---

# 9. Reported Results

For example, in the reported Gemini-2.5 Flash experiments:

### Local coordination

| Guidance | Coloring | Matching | Vertex Cover |
|---|---:|---:|---:|
| AgentsNet | 1.99 | 1.03 | 2.74 |
| Function-Description | 0.55 | 0.78 | 2.21 |
| Function-Pseudocode | 0.34 | 0.80 | 3.03 |
| Main-Pseudocode | 1.05 | 1.85 | 2.34 |
| Full-Pseudocode | 0.76 | 2.61 | 3.48 |

### Global coordination

| Guidance | Coloring | Matching | Vertex Cover |
|---|---:|---:|---:|
| AgentsNet | 2.35 | 1.24 | 2.90 |
| Function-Description | 1.92 | 1.11 | 2.35 |
| Function-Pseudocode | 1.56 | 1.01 | 3.29 |
| Main-Pseudocode | 2.49 | 1.37 | 2.83 |
| Full-Pseudocode | 1.89 | 1.85 | 3.68 |

The exact best configuration varies by problem, but the paper's general conclusion is that **intermediate symbolic guidance is often more effective than either extreme**.

---

# 10. Findings

1. Full LLM autonomy can produce inconsistent coordination.
2. Complete symbolic prescription can be too rigid.
3. Partial symbolic guidance can provide a useful middle ground.
4. The amount of guidance should depend on the coordination problem.
5. Adjustable autonomy is therefore a meaningful architectural design dimension.

---

# 11. Enterprise Relevance

This paper is particularly relevant to a thesis where agents must operate under business rules.

Enterprise processes contain many deterministic constraints:

- price floors;
- credit limits;
- inventory constraints;
- approval thresholds;
- compliance policies.

A fully free-form LLM should not necessarily decide these constraints.

### Thesis interpretation

A strong architecture could separate:

**LLM reasoning**
from
**deterministic business rules**

while giving the LLM enough structured guidance to coordinate effectively.

This is a potential architectural principle, not a final thesis requirement.

---

# 12. Deal Desk Relevance

A Deal Desk system is a natural candidate for adjustable autonomy.

Potential examples:

| Deal Desk component | Possible autonomy |
|---|---|
| Pricing policy check | Highly constrained |
| Inventory lookup | Tool/API constrained |
| Credit assessment | Rule + data constrained |
| Approval routing | Policy constrained |
| Exception explanation | More LLM-flexible |
| Negotiation reasoning | Potentially more flexible |
| Orchestration | Structured but adaptive |

The exact allocation should be determined after the remaining literature and thesis requirements are finalized.

---

# 13. Limitations

The paper is an **extended abstract**, so the empirical detail is considerably narrower than a full-length research article.

The experiments focus on graph coordination rather than enterprise workflows.

Therefore:

- no CRM;
- no CPQ;
- no ERP;
- no B2B deals;
- no commercial approvals.

Its value to the thesis is primarily conceptual and methodological.

---

# 14. Potential Gap Evidence

The paper provides evidence for a general problem:

> LLM agents need an appropriate degree of autonomy.

What remains open in an enterprise context is how to operationalize that principle across different business agents and workflows.

This could be relevant when deciding which parts of the Deal Desk process should be:

- LLM-driven;
- rule-driven;
- tool-driven;
- orchestrator-controlled.

---

# 15. Evidence Locations

| Topic | Location |
|---|---|
| Problem motivation | Section 1 |
| SGT definition | Section 2 |
| Autonomy spectrum | Section 2 / Figure 1 |
| Experimental setup | Section 3 |
| Results | Table 1 |
| Conclusions | Section 4 |

---

# Paper 5 — LLM-Based Multi-Agent Orchestration: A Survey of Frameworks, Communication Protocols, and Emerging Patterns

## 1. Bibliographic / Verification Information

| Field | Extraction |
|---|---|
| Title | **LLM-Based Multi-Agent Orchestration: A Survey of Frameworks, Communication Protocols, and Emerging Patterns** |
| Authors | Yiwen Zhu, Lihe Liu, Jiaqian Yu, Di Zhang |
| Venue | Future Internet |
| Year | 2026 |
| Volume / Issue / Article | 18(6), 326 |
| DOI | 10.3390/fi18060326 |
| Received | 29 April 2026 |
| Revised | 3 June 2026 |
| Accepted | 8 June 2026 |
| Published | 15 June 2026 |
| Research type | Review / survey |
| Literature cutoff | March 2026 |
| Main area | LLM agents; multi-agent orchestration; frameworks; protocols; evaluation |
| Primary thesis relevance | **Extremely high** as a synthesis source for orchestration architecture |

---

# 2. Purpose

The survey addresses the growing difficulty of composing multiple LLM agents into reliable systems.

It focuses specifically on:

- orchestration;
- coordination topology;
- adaptivity;
- frameworks;
- communication protocols;
- production considerations;
- evaluation;
- open challenges.

The survey is particularly useful for positioning the Deal Desk Orchestrator within the broader LLM-agent literature.

---

# 3. Survey Methodology

The survey covers literature from:

**2023 through early 2026**

with a cutoff of:

**March 2026**.

A major methodological contribution is the explicit **evidence hierarchy** used when discussing deployment claims.

The survey distinguishes:

- peer-reviewed research;
- independent measurements;
- government/evaluator measurements;
- vendor-reported results.

This distinction is important for the thesis literature review because vendor performance claims should not automatically be treated as equivalent to independent empirical evidence.

---

# 4. Core Taxonomy

The survey proposes:

## Three topology types

1. Centralized
2. Decentralized
3. Hierarchical

and one cross-cutting adaptivity dimension:

- static;
- dynamic/adaptive.

This creates a conceptual **3 × 2 grid**.

---

# 5. Centralized Topology

A central supervisor/orchestrator controls agent interactions.

Conceptually:

`Supervisor → Agent A`
`Supervisor → Agent B`
`Supervisor → Agent C`

The supervisor can:

- assign tasks;
- monitor state;
- route work;
- aggregate results.

### Advantages discussed

- clear control;
- easier coordination;
- centralized state;
- easier policy enforcement.

### Potential limitations

- central bottleneck;
- single point of failure;
- scalability concerns;
- orchestrator quality becomes critical.

### Thesis relevance

This is directly aligned with the term **Deal Desk Orchestrator**.

---

# 6. Decentralized Topology

Agents communicate peer-to-peer.

There is no single permanent controller.

Potential benefits:

- distributed decision-making;
- reduced central bottleneck;
- potentially more robust local coordination.

Potential drawbacks:

- harder global coordination;
- communication overhead;
- more difficult state consistency;
- harder governance.

For an undergraduate thesis implementation, this architecture may be more complex than necessary, but that is an engineering consideration rather than a literature conclusion.

---

# 7. Hierarchical Topology

Hierarchical systems combine multiple coordination layers.

Example:

`Global Supervisor`
→ `Commercial Coordinator`
→ `Specialist Agents`

This can potentially separate:

- high-level planning;
- domain-level coordination;
- individual execution.

This topology is particularly relevant if the Deal Desk Orchestrator eventually needs multiple levels of decision-making.

---

# 8. Adaptivity Dimension

The survey treats adaptivity as a separate dimension.

### Static

Roles/topology are fixed.

### Dynamic/adaptive

The system can alter:

- routing;
- team composition;
- topology;
- execution strategy.

This connects directly to the Puppeteer paper.

---

# 9. Self-Evolving Systems

The survey identifies self-evolving coordination as an emerging area.

Examples include systems that learn:

- which agents should collaborate;
- which agents are useful;
- how communication should be routed;
- when to stop;
- how to optimize cost.

The survey identifies generalization as an unresolved issue.

A topology learned on one task type may not automatically generalize to another.

---

# 10. Framework Comparison

The survey discusses frameworks including:

- LangGraph;
- CrewAI;
- AutoGen / Microsoft Agent Framework;
- OpenAI Agents SDK;
- MetaGPT;
- DSPy.

The frameworks differ in:

- state management;
- topology;
- task routing;
- cost;
- failure recovery;
- design philosophy.

### Thesis relevance

The thesis implementation should eventually choose a framework based on actual requirements rather than popularity.

---

# 11. Communication Protocols

The survey distinguishes multiple protocol layers.

## MCP

**Model Context Protocol**

Primarily addresses agent-to-tool interaction.

Conceptually:

`Agent ↔ Tool`

Examples:

- databases;
- APIs;
- external services.

## A2A

**Agent-to-Agent protocol**

Addresses communication between independent agents.

Conceptually:

`Agent ↔ Agent`

## ANP

**Agent Network Protocol**

Addresses discovery and decentralized agent networking.

### Important conceptual distinction

MCP and A2A are not necessarily competing protocols.

The survey frames them as complementary layers:

`Agent ↔ Tool` = MCP

`Agent ↔ Agent` = A2A

This is highly relevant to an enterprise multi-agent system.

---

# 12. Production Design Considerations

The survey identifies several major implementation dimensions.

## 12.1 State Management

Long-horizon tasks create significant state-management problems.

The system needs to preserve:

- task state;
- agent outputs;
- tool results;
- intermediate artifacts;
- decisions.

## 12.2 Task Planning and Decomposition

Complex tasks need to be broken into manageable subtasks.

This connects directly to:

- ChatDev;
- CAMEL;
- Puppeteer.

## 12.3 Error Handling and Recovery

Multi-agent systems must handle:

- failed agents;
- incorrect outputs;
- tool failures;
- inconsistent responses;
- coordination failures.

## 12.4 Scalability

Adding agents can increase:

- latency;
- token cost;
- communication;
- coordination complexity.

Therefore, “more agents” does not automatically mean “better”.

## 12.5 Security and Trust

Enterprise agents introduce issues involving:

- permissions;
- authentication;
- tool access;
- data leakage;
- trust boundaries.

This is especially important for CRM/ERP/CPQ integration.

---

# 13. Evaluation Gap

One of the survey's strongest conclusions is that there is **no widely adopted benchmark specifically designed for multi-agent orchestration quality**.

Existing benchmarks often evaluate the final task outcome rather than the quality of collaboration.

The survey identifies missing dimensions such as:

- communication efficiency;
- redundant versus useful messages;
- scalability with agent count;
- cost per task;
- robustness;
- emergent behavior;
- coordination quality.

---

# 14. Six Evaluation Dimensions

The survey proposes a six-dimension framework for multi-agent coordination evaluation.

The dimensions include concepts such as:

- task success;
- coordination efficiency;
- scalability;
- cost;
- robustness;
- emergent behavior.

The important thesis implication is that simply reporting:

> “The final answer was correct”

may be insufficient to evaluate an orchestration system.

A thesis implementation can potentially evaluate both:

1. **business-task correctness**
2. **orchestration behavior**

---

# 15. Benchmark Evidence

The survey discusses benchmarks including:

- HumanEval;
- SWE-bench;
- GAIA;
- WebArena;
- OSWorld;
- AgentBench;
- τ-bench.

Examples reported in the survey demonstrate substantial differences between:

- one-shot success;
- sustained multi-step success;
- human performance;
- agent performance.

The survey emphasizes that benchmark subset and evaluation date matter when comparing results.

---

# 16. Long-Horizon Evaluation

The survey identifies a major problem with terminal pass/fail metrics.

If a long task fails after 95% of its work, a binary success metric may treat it the same as a task that failed immediately.

The survey therefore points toward:

- partial credit;
- intermediate progress;
- cost telemetry;
- cross-session resumption fidelity.

This is potentially relevant to Deal Desk workflows where a deal may pass through many validation stages.

---

# 17. Open Challenge — Protocol Interoperability

MCP, A2A and ANP currently have different assumptions about:

- sessions;
- authentication;
- trust boundaries;
- discovery.

The survey argues that standardized bridging remains incomplete.

This matters for enterprise environments where:

- internal tools;
- external agents;
- SaaS systems;
- APIs

may all need to interact.

---

# 18. Open Challenge — Self-Organizing MAS

The survey identifies research into systems that automatically optimize:

- agent composition;
- topology;
- routing;
- communication.

Examples include learned topologies and agent-selection methods.

The open question is whether such learned coordination generalizes reliably to new tasks.

---

# 19. Open Challenge — Cost

Multi-agent systems can multiply LLM calls.

The survey identifies approaches including:

- token-budget management;
- communication compression;
- model routing;
- caching;
- trajectory reduction;
- structured messages.

This is highly relevant to a thesis implementation because a system that calls every specialist on every deal may become unnecessarily expensive.

---

# 20. Open Challenge — Trust, Safety and Alignment

The survey emphasizes that individually aligned agents can still produce undesirable collective behavior.

Enterprise systems add additional concerns:

- permissions;
- sensitive data;
- tool access;
- organizational boundaries;
- policy compliance.

This means orchestration should include governance and validation, not just routing.

---

# 21. Open Challenge — Long-Horizon Coordination

The survey highlights that long-horizon tasks require:

- persistent state;
- reliable planning;
- error recovery;
- intermediate validation;
- resumption.

This is particularly relevant to commercial processes where a deal may move through multiple steps and may require human approval before continuing.

---

# 22. Open Challenge — Generalization of Learned Orchestration

A learned topology may work well on one benchmark but fail on a different task type.

Therefore:

> Dynamic orchestration must be evaluated for generalization, not only benchmark performance.

This is directly relevant to a Deal Desk system because commercial deals can vary significantly.

---

# 23. Enterprise Relevance

This survey provides the strongest high-level evidence for viewing the thesis as a **multi-agent orchestration problem**, not simply an LLM chatbot.

A Deal Desk Orchestrator potentially contains:

- orchestration topology;
- specialized agents;
- tool integrations;
- state management;
- routing;
- validation;
- error recovery;
- security;
- cost control.

---

# 24. Deal Desk Relevance

The survey supports several potential architectural dimensions:

| Survey dimension | Deal Desk application |
|---|---|
| Centralized topology | Deal Desk Orchestrator |
| Hierarchical topology | Orchestrator → domain coordinator → specialists |
| Dynamic routing | Invoke relevant deal agents |
| State management | Persistent deal context |
| Task decomposition | Break complex deal into checks |
| Error handling | Retry/escalate failed validations |
| MCP | Connect agents to enterprise tools |
| A2A | Agent-to-agent communication |
| Cost optimization | Avoid unnecessary LLM calls |
| Security | Control CRM/ERP/financial access |
| Evaluation | Measure both deal correctness and orchestration |

These are architectural hypotheses, not final requirements.

---

# 25. Potential Research-Gap Evidence

The survey identifies several open areas:

1. orchestration evaluation;
2. adaptive/self-organizing systems;
3. long-horizon coordination;
4. cost optimization;
5. protocol interoperability;
6. trust and security;
7. generalization of learned coordination.

However, the survey is broad.

It does not specifically answer:

> How should a multi-agent orchestration architecture support complex B2B deal processing across enterprise commercial systems?

That domain-specific question remains open in the supplied evidence.

---

# 26. Evidence Locations

| Topic | Location |
|---|---|
| Survey methodology | Section 3 |
| Centralized/decentralized/hierarchical taxonomy | Section 4 |
| Adaptivity | Section 4.2 |
| Frameworks | Section 5 |
| MCP | Section 6.1 |
| A2A | Section 6.2 |
| Protocol complementarity | Section 6.3 |
| State management | Section 7.1 |
| Planning | Section 7.2 |
| Error handling | Section 7.3 |
| Scalability | Section 7.4 |
| Security | Section 7.5 |
| Evaluation | Section 8 |
| Applications | Section 9 |
| Open challenges | Section 10 |
| Conclusions | Section 11 |
| Extraction details | Appendix A |

---

# Cross-Paper Synthesis

## 1. Architecture Comparison

| Paper | Main architecture | Coordination | Adaptivity | Specialized agents | Tool use |
|---|---|---|---|---|---|
| Puppeteer | Centralized | Learned centralized selection | High | Yes | Yes |
| ChatDev | Structured staged workflow | Predefined | Low/medium | Yes | Limited |
| CAMEL | Role-playing | Conversational planner/executor | Medium | Yes | Not central |
| SGT | Distributed coordination | Symbolic guidance | Autonomy spectrum | Yes | Not central |
| Survey | Centralized/decentralized/hierarchical taxonomy | Multiple | Explicit dimension | Yes | MCP/A2A focus |

---

# 2. What the Papers Collectively Say About Agents

Across the papers, an agent can represent different kinds of responsibility.

### Domain-specialist agent

Examples:

- programmer;
- reviewer;
- tester;
- stock trader.

### Reasoning agent

Examples:

- planner;
- critic;
- reasoner;
- reflector;
- summarizer.

### Tool-use agent

Examples:

- web search;
- Python;
- file access;
- website access.

### Orchestration agent

Responsible for:

- deciding which agent should act;
- sequencing work;
- managing state;
- coordinating specialists.

### Important conclusion for the thesis

The term **“agent” should not automatically mean a business department**.

The literature supports several layers of agent responsibility.

---

# 3. Coordination Mechanism Comparison

## Static workflow

Strongly represented by ChatDev.

Advantages:

- predictable;
- easy to implement;
- easy to explain;
- easier to test.

Disadvantages:

- less adaptive;
- may invoke unnecessary agents;
- may struggle with unusual cases.

## Conversational coordination

Strongly represented by CAMEL.

Advantages:

- flexible;
- agents can iteratively clarify;
- natural interaction.

Disadvantages:

- loops;
- role confusion;
- communication overhead.

## Learned dynamic orchestration

Strongly represented by Puppeteer.

Advantages:

- adaptive;
- potentially more efficient;
- can learn task-specific routing.

Disadvantages:

- training complexity;
- reliability issues;
- fixed agent/tool assumptions;
- difficult enterprise validation.

## Symbolically guided autonomy

Strongly represented by SGT.

Advantages:

- combines structure and flexibility;
- useful for constrained processes.

Disadvantages:

- correct level of guidance is problem-dependent.

---

# 4. Communication Comparison

| Paper | Main communication pattern |
|---|---|
| Puppeteer | Orchestrator-mediated state/context |
| ChatDev | Structured role-to-role communication |
| CAMEL | Planner → executor conversational loop |
| SGT | Distributed coordination under symbolic guidance |
| Survey | Agent-to-agent and agent-to-tool protocol layers |

---

# 5. Validation / Reliability

A major cross-paper pattern is that **coordination alone is not enough**.

Reliability mechanisms include:

- ChatDev: reviewer + tester + communicative dehallucination;
- CAMEL: critic + explicit termination conditions;
- Puppeteer: reward-based optimization + critic/reasoning agents;
- SGT: symbolic guidance;
- Survey: error handling, recovery, security and evaluation.

This suggests that a serious enterprise multi-agent system needs explicit validation.

---

# 6. Enterprise-System Interaction

The supplied papers vary considerably here.

| Capability | Evidence |
|---|---|
| External tools | Puppeteer |
| APIs/tools | Puppeteer / survey |
| Agent-agent communication | CAMEL / ChatDev / survey |
| Persistent state | ChatDev / survey |
| Enterprise CRM | Not demonstrated in these five papers |
| CPQ | Not demonstrated |
| ERP | Not demonstrated |
| B2B deal processing | Not demonstrated |
| Commercial pricing | Not demonstrated |
| Credit decisioning | Not demonstrated |
| Deal approval workflow | Not demonstrated |

This is important for the thesis: **the gap should not be claimed merely because no paper uses the exact words “Deal Desk.”** The stronger argument is that the supplied literature demonstrates orchestration mechanisms but does not directly validate their integration into a complex B2B commercial decision workflow.

---

# 7. Recurring Limitations Across the Papers

## Coordination reliability

Agents can:

- loop;
- repeat;
- mis-coordinate;
- agree incorrectly;
- fail to follow roles.

## Cost

Multi-agent systems generate:

- more messages;
- more LLM calls;
- more tokens;
- higher latency.

## Static versus dynamic design

Static systems are predictable but less adaptable.

Dynamic systems are flexible but harder to validate.

## Evaluation

Final task accuracy does not fully measure:

- coordination quality;
- communication efficiency;
- scalability;
- cost;
- robustness.

## State management

As tasks become longer, maintaining coherent context becomes difficult.

## Enterprise constraints

The supplied papers do not provide a complete solution for:

- authorization;
- transactional consistency;
- deterministic business rules;
- enterprise-system integration;
- auditability.

---

# 8. Final Deal Desk Architecture Context

The final Phase 1B design uses six business specialists: Configuration Validator, Pricing and Margin, Availability, Credit and Risk, Policy and Compliance, and Approval Routing. A central Orchestrator manages execution, failure handling, shared state and package assembly. Deal History remains a shared stretch tool rather than a seventh specialist agent.

The orchestration papers justify role specialization, controlled information flow, dynamic coordination and bounded autonomy. They do not by themselves establish that this exact Deal Desk agent set is optimal. The final design is derived jointly from the orchestration literature, the business-side evidence and the bounded implementation scope.

---

# 9. Final Research Questions

**Primary RQ.** How can a governed multi-agent orchestrator coordinate specialised agents to ensure business-rule compliance and decision completeness in B2B Deal Desk processing?

**Supporting RQ1.** Which Deal Desk decisions require deterministic business rules, which permit bounded agent reasoning, and how do these mechanisms affect constraint compliance, escalation accuracy, and latency?

**Supporting RQ2.** To what extent do orchestration-level trace metrics identify Deal Desk processing failures that are not visible from final-output accuracy alone?

---

# 10. Final Research Gap

> Existing peer-reviewed work provides components for adaptive orchestration, symbolic guidance, rule-grounded execution, external decision management, credit evaluation, and supply-chain coordination. However, no peer-reviewed work was identified in this purposive review that integrates these components into a governed multi-agent Deal Desk architecture coordinating configuration, pricing, availability, credit or risk, policy compliance, and approval routing together. The remaining contribution is therefore an implementation and evaluation problem: applying deterministic control where required, bounded agent reasoning where appropriate, auditable shared state, and trace-level evaluation alongside final decision correctness.

This conclusion relies on the full orchestration and business-side pool. It must be presented as a purposive-review finding, not as proof that no such work exists anywhere.

---

# 11. Most Important Takeaways for the Deal Desk Thesis

## Takeaway 1 — Orchestration is a distinct research problem

The Puppeteer paper and the survey strongly support separating:

**agent capability**
from
**agent orchestration**.

The thesis therefore should not simply build several agents and call their communication “orchestration.”

---

## Takeaway 2 — Specialized roles are supported by the literature

ChatDev and CAMEL demonstrate that role specialization can structure cooperation.

But specialization should be justified by the actual Deal Desk process.

---

## Takeaway 3 — Static and dynamic orchestration should be compared conceptually

ChatDev provides a strong example of predefined workflows.

Puppeteer provides a strong example of dynamic selection.

This gives the thesis a useful architectural design question:

> Does the Deal Desk require a predefined workflow, dynamic routing, or a hybrid?

---

## Takeaway 4 — Business rules should not simply be delegated to unrestricted LLM reasoning

SGT provides evidence that intermediate structure can improve coordination.

For a Deal Desk, this is especially relevant because:

- pricing thresholds;
- credit constraints;
- inventory constraints;
- approval rules

may require deterministic enforcement.

---

## Takeaway 5 — Validation is essential

Every paper points in some way toward the need for:

- review;
- critique;
- testing;
- guidance;
- state checking;
- error recovery.

The Deal Desk architecture should therefore explicitly consider validation rather than treating the orchestrator as only a router.

---

## Takeaway 6 — Evaluation must cover the process, not just the answer

The survey's evaluation-gap discussion is especially important.

A Deal Desk thesis could potentially measure:

### Business outcome

- correctness of deal decision;
- correct routing;
- correct approval requirement;
- correct exception detection.

### Orchestration outcome

- number of agents invoked;
- number of LLM calls;
- token usage;
- latency;
- unnecessary calls;
- successful completion;
- recovery from agent failure.

---

# Final Evidence Status

| Research Area | Evidence from these papers |
|---|---|
| Multi-agent systems | **Strong** |
| LLM-based agents | **Strong** |
| Role specialization | **Strong** |
| Agent communication | **Strong** |
| Centralized orchestration | **Strong** |
| Dynamic orchestration | **Strong** |
| Adaptive coordination | **Strong** |
| Tool use | **Strong** |
| State management | **Moderate–strong** |
| Validation / critique | **Strong** |
| Adjustable autonomy | **Moderate–strong** |
| Enterprise systems | **Limited in these five papers** |
| CRM | **Not directly demonstrated** |
| CPQ | **Not directly demonstrated** |
| ERP | **Not directly demonstrated** |
| B2B Deal Desk | **Not directly demonstrated** |
| Commercial pricing | **Not directly demonstrated** |
| Credit decisioning | **Not directly demonstrated** |
| Deal approval | **Not directly demonstrated** |
| Enterprise-grade auditability | **Not directly demonstrated** |
| Multi-agent orchestration evaluation | **Identified as an open problem** |

---

# Recommended Use in the Thesis Literature Review

These five papers should primarily support the following literature-review claims:

1. **LLM multi-agent systems can divide complex tasks among specialized agents.**
2. **Role-based communication can structure collaboration.**
3. **Predefined workflows provide structure but may limit adaptability.**
4. **Dynamic orchestration can learn which agents to activate.**
5. **Agent autonomy can be regulated through symbolic guidance.**
6. **Tool interaction and agent-agent communication represent distinct architectural concerns.**
7. **State, cost, reliability, security, and evaluation become increasingly important as multi-agent systems become more complex.**
8. **There remains a gap between general LLM multi-agent research and domain-specific enterprise commercial workflows.**

They should **not** yet be used alone to claim:

- that a specific Deal Desk agent architecture is optimal;
- that Pricing/Inventory/Credit/Approval are definitely the final agents;
- that centralized orchestration is universally superior;
- that the thesis has already established a novel research gap.

Those conclusions require the remaining literature streams and the actual thesis requirements.

---

# Source Files Used

All five saved source texts are in `../papers/multi-agent-orchestration/`. See `Paper-Source-Index.md` for the mapping from research IDs to title-based filenames.
