# **Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems** 

Sreemaee Akshathala<sup>∗</sup> Bassam Adnan<sup>∗</sup> Software Engineering Research Software Engineering Research Center Center IIIT Hyderabad IIIT Hyderabad Hyderabad, Telangana, India Hyderabad, Telangana, India sreemaee.akshathala@research.iiit.ac.in bassam.adnan@research.iiit.ac.in 

Mahisha Ramesh Software Engineering Research Center IIIT Hyderabad Hyderabad, Telangana, India mahisha.ramesh@research.iiit.ac.in 

Karthik Vaidhyanathan Basil Muhammed Software Engineering Research MontyCloud Center Bangalore, Karnataka, India IIIT Hyderabad, India basil@montycloud.com Hyderabad, Telangana, India karthik.vaidhyanathan@iiit.ac.in 

Kannan Parthasarathy MontyCloud Bangalore, Karnataka, India kannan@montycloud.com 

## **Abstract** 

reveal behavioral deviations overlooked by conventional metrics, demonstrating its effectiveness in capturing runtime uncertainties. 

Recent advances in agentic AI have shifted the focus from standalone Large Language Models (LLMs) to integrated systems that combine LLMs with tools, memory, and other agents to perform complex tasks. These multi-agent architectures enable coordinated reasoning, planning, and execution across diverse domains, allowing agents to collaboratively automate complex workflows. Despite these advances, evaluation and assessment of LLM agents and the multi-agent systems they constitute remain a fundamental challenge. Although various approaches have been proposed in the software engineering literature for evaluating conventional software components, existing methods for AI-based systems often overlook the non-deterministic nature of models. This non-determinism introduces behavioral uncertainty during execution, yet existing evaluations rely on binary task-completion metrics that fail to capture it. Evaluating agentic systems therefore requires examining additional dimensions, including the agent’s ability to invoke tools, ingest and retrieve memory, collaborate with other agents, and interact effectively with its environment. 

## **Keywords** 

Agentic AI, Assessment, Evaluation, AI-enabled systems, Software Engineering, CloudOps 

### **ACM Reference Format:** 

Sreemaee Akshathala, Bassam Adnan, Mahisha Ramesh, Karthik Vaidhyanathan, Basil Muhammed, and Kannan Parthasarathy. 2026. Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems. In _International Workshop on Agentic Engineering (AGENT ’26), April 12–18, 2026, Rio de Janeiro, Brazil._ ACM, New York, NY, USA, 9 pages. https://doi.org/10.1145/3786167.3788414 

## **1 Introduction** 



<!-- Start of picture text -->
Agent<br>LLM<br>Accuracy InstructionFollowing AlignmentSafety & Cost & Time<br>Tools Memory<br>Evaluationof Tool Interactionwith Tool Retrieval Storage<br>Environment<br>Workflows Configurability Guardrails<br>Evaluation<br>Static Dynamic<br>Metric Agent-as-a LLM-as-a<br>Analysis Judge Judge<br><!-- End of picture text -->

These challenges emerged during our ongoing industry collaboration with MontyCloud Inc., an industrial partner in the domain of Autonomous CloudOps, when we deployed an agentic system in production. These limitations surfaced during deployment, highlighting practical gaps in the current evaluation methods and the need for a systematic assessment of agent behavior beyond task outcomes. Informed by these observations and established definitions of agentic systems, we propose an end-to-end Agent Assessment Framework with four evaluation pillars encompassing LLMs, Memory, Tools, and Environment. We validate the framework on a representative Autonomous CloudOps use case, where experiments 

∗These authors contributed equally to this work. 

This work is licensed under a Creative Commons Attribution 4.0 International License. _AGENT ’26, Rio de Janeiro, Brazil_ 

**Figure 1: Agent Assessment Framework Overview** 

© 2026 Copyright held by the owner/author(s). ACM ISBN 979-8-4007-2399-5/26/04 

The evolution of LLMs over the last few years has shifted the AI system design from independent and isolated model deployment to 

https://doi.org/10.1145/3786167.3788414 

9 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Akshathala, Adnan, et al. 

**Table 1: Uncertainties and Evaluation Metrics** 

|**Source**|**Uncertainty**|**Description**|**Evaluation Metrics**|
|---|---|---|---|
|**LLM**|Instruction<br>Following|Agent adherence to policy constraints|Instruction adherence score; Sequence correctness;<br>Test case coverage;Judge scores|
||Safety &<br>Alignment|Generated actions’ compliance with safety policies and<br>intended objectives|Safety violation count; Policy compliance rate; Judge<br>scores|
|**Memory**|Storage|Correctness and efficiency of memory updates and prop-<br>agation|Update correctness rate; Update latency; Duplicate<br>entrycount|
||Retrieval|Accuracy and completeness of retrieved information<br>from memorysystems|Precision; Recall; F1-score; BLEU-1; ROUGE; Retrieval<br>latency; Coverage ratio|
||Tool Selection|Correct identification of appropriate tool forgiven task|Classification accuracy; Tool selection;Judge scores|
|**Tools**|Parameter<br>Mapping|Semantic and contextual accuracy of tool parameters|Parameter accuracy; Semantic correctness score;<br>Judge scores|
||Tool<br>Sequencing|Correct execution order respecting dependencies and<br>workflows|Sequence correctness score; Phase completion ratio;<br>Diagnostic-before-action adherence|
||Error<br>Interpretation|Agent understanding and response to tool execution<br>errors|Recovery success rate; Corrective action accuracy;<br>Judge scores|
|**Environment**|Resource<br>Limitations|Environment limitations like resource fluctuations, con-<br>straint changes & action authorization|Guardrail violation count; Blocked action attempts;<br>Authorization failures;Judge scores|



agentic system architectures that integrate reasoning, planning, and tool use [14]. While multi-agent systems have a well-established foundation[22], modern agentic systems extend these principles through memory mechanisms and environment interaction. This enables its application across diverse domains such as software engineering, customer service, and autonomous operations. This evolution requires the evaluation mechanisms to shift from modelcentric metrics to system-level assessments. The integration of multiple components introduces significant evaluation challenges that conventional assessment methodologies do not address. The primary challenge in evaluating agentic systems stems from the inherent uncertainty [21] introduced by non-deterministic AI models. Agentic systems exhibit variability in execution paths, tool selection, and memory retrieval patterns, causing uncertainty to propagate through the system, affecting the correctness of tool invocations, the consistency of memory operations, and the reliability of multi-agent interactions. 

Current research on agentic AI systems concentrates primarily on design patterns and architectural frameworks[10], with limited attention to systematic assessment methodologies. This gap became evident when we tested an agentic system in a CloudOps production environment at Montycloud<sup>1</sup> . While the agents completed the tasks, deviations from expected policies or validation flows remained undetected by existing assessment methods as they surfaced only during runtime execution rather than in static validation phases. Based on these production-level insights, we designed a comprehensive assessment framework for evaluating agentic AI systems across the four identified pillars: LLM, Memory, Tools, and Environment. These pillars were derived based on the fundamental definition of an agent, an entity equipped with a reasoning component (LLM), memory, and tools for interaction with its environment[6, 16]. Based on existing research in self-adaptive systems [11, 24], we also recognize the environment as a source of uncertainty which influences agent behavior. The framework integrates static, dynamic, and 

judge evaluation modes to capture behavioral failures beyond task success rates. Table 1 provides an overview of the pillar-specific uncertainties and corresponding evaluation metrics that form the foundation of our assessment methodology. 

We validate the assessment framework through experimental evaluation on MOYA, a multi-agent framework previously developed [19]. With insights from Montycloud, we designed three productionmotivated CloudOps scenarios of varying complexity, representing real operational challenges encountered in enterprise-level cloud management. Results demonstrate that while baseline metrics report task completion, our framework-specific assessments reveal substantial behavioral failures across all pillars, particularly in tool orchestration and memory retrieval. 

The rest of the paper is organised as follows: Section 2 motivates the need for assessment through Autonomous CloudOps examples, Section 3 introduces the framework architecture across all four pillars and the evaluation components. Section 4 details experimental setup and results, while sections 5, 6, and 7 discuss implications for researchers and practitioners, related work, and future work. Our experiments and results are available on GitHub<sup>2</sup> . 

## **2 Motivation** 

CloudOps manages and optimizes cloud infrastructure through automated workflows. Organizations navigating increasingly complex cloud environments require autonomous systems capable of executing diverse operational tasks at scale. CloudOps platforms like _MontyCloud Inc._<sup>3</sup> leverage AI agents to automate cloud management tasks, including resource provisioning, compliance enforcement, and incident response [19]. These systems demonstrate the growing reliance on autonomous decision-making in operational workflows. Conventional evaluation frameworks largely focus on task outcomes and operational efficiency, overlooking behavioral failures which emerge at runtime. Agents might appear to perform 

> 2https://github.com/sa4s-serc/asf 

> 1https://montycloud.com/ 

> 3https://montycloud.com/ 

10 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems 

well while violating policies, making uninformed decisions, or skipping verification checks. Evaluating behavioral reliability requires verifying whether agents consult policies before acting, perform diagnostic checks, retrieve relevant context, invoke tools with correct parameters, and respect guardrails that prevent unauthorized operations. 

Due to the nature of agentic systems, the uncertainties extend beyond the performance of the model and span multiple sources, as shown in Table 1. These pillars capture an agent’s reasoning, memory, tool use [6], and include the environment as a source of operational uncertainty [11, 24]. The _LLM pillar_ introduces failures in instruction following and safety alignment. The _Memory pillar_ presents challenges in storage consistency and retrieval accuracy. The _Tools pillar_ exhibits failures in Tool selection, parameter mapping, and execution sequencing. The _Environment pillar_ represents the operational context in which agents are assessed, defined through structured workflows, guardrails for safe operation, and configurability for reproducible evaluation, assuming sufficient observability for monitoring and analysis. These limitations motivate a multi-layered evaluation strategy that examines agent behavior across complementary dimensions, including static, dynamic, and qualitative analyses, to enable assessment of behavioral reliability. The following subsections detail the framework components and evaluation strategies for each pillar. 

## **3 Agent Assessment Framework** 

Figures 1 and 2 illustrate the proposed framework for evaluating agentic AI systems across four pillars, namely, _LLM, Memory, Tools, and Environment_ . The framework performs three layers of analysis: (i) _Static Analysis_ , which validates agent behaviors against predefined ground-truth specifications; (ii) _Dynamic Execution_ , which monitors runtime behaviors to detect deviations and policy violations; and (iii) _Judge-based Evaluation_ , which qualitatively assesses reasoning, safety, and alignment through LLM or Agent-as-a-Judge protocols. Together, these layers establish a comprehensive process for assessing both deterministic correctness and behavioral reliability in agentic systems. 

The framework follows a modular structure where each pillar defines its own evaluation metrics and assessment focus. Results from the static and dynamic assessments are combined to measure behavioral correctness and reliability, while qualitative evaluations are used to assess reasoning and alignment. This structure allows the framework to provide both granular and system-level insights into agent performance across diverse operational contexts. 

**Test Case Generation:** To ensure consistency across all pillars, the framework includes a _test case generator_ component that defines controlled scenarios for evaluation. Each test case specifies context, expected behaviors, and success criteria derived from ground-truth specifications. These cases are tailored to each pillar’s objectives. For example, for the _LLM_ pillar, they test instruction following and safety alignment; for _Memory_ , retrieval accuracy and context retention; for _Tools_ , proper selection and parameter mapping; and for the _Environment_ , workflow execution and guardrail compliance. The generated test cases are used throughout static validation, dynamic monitoring, and judge-based evaluation to ensure systematic and reproducible assessment across all dimensions of agent performance. 

## **3.1 Memory** 

A fundamental limitation of the agent’s backbone LLM is its context length and its effective utilization. This is mitigated by providing the agent with a memory mechanism [27] that allows the agent to store and retrieve memories. Current state-of-the art approaches rely on extracting relations between entities and store them in a graph or vector-based storage engines [5]. Our Static analysis for the pillar computes precision, recall, F1-score, and BLEU-1 against gold-standard labels, followed by Judge evaluation. 

**Storage:** Evaluates how effectively the agent structures, updates, and manages stored information such as events, conversations, and contextual data to ensure efficient and accurate memory retrieval. This evaluation focuses on whether these memory operations are performed correctly and efficiently, ensuring that obsolete information is replaced rather than duplicated. Additionally, this component measures update latency, i.e., how long it takes for new information to propagate through the memory hierarchy and become visible to all agents. For example, in CloudOps practice, this may be observed when outdated configuration details of the same resource are retained, leading to multiple conflicting entries for the same resource. 

**Retrieval:** Evaluates how accurately and efficiently the agent recalls relevant information from memory systems such as graph or vector-based stores, conversation history, or external knowledge sources. This component measures recall accuracy, which reflects how well the retrieved information aligns with the intended query. The evaluation spans four key retrieval types—Single-hop, Multihop, Temporal Reasoning, and Open-Domain. Single-hop tests the recall of facts from a single point of context; Multi-hop assesses retrieval across multiple interconnected memory instances; Temporal Reasoning examines the agent’s chronological understanding of events; and Open-Domain retrieval evaluates how effectively the agent combines conversational memory with external knowledge bases such as vector databases or cloud documentation. Effective retrieval ensures that the agent can synthesize context from multiple sources to provide consistent, contextually grounded responses. In CloudOps, this may involve retrieving recent system configuration updates and aligning WAFR<sup>4</sup> workload details with cloud best-practice guidelines to support informed operational decisions. 

## **3.2 Tools** 

Tools enable agents to act within real or simulated environments, defining their operational competence. Within an agentic framework, they may be internal functions or external components defined through protocols like the Model Context Protocol (MCP) [7]. Evaluating both the tool quality and the agent’s ability to use tools correctly is therefore essential, as failures often stem from ambiguous descriptions, incorrect parameter mappings, or inadequate error messages. 

_Quantitative Validation:_ Based on the trajectory of an agent, the tool usage can be extracted and compared to golden labels as part of the Static analysis. This can be categorized into: 

**Tool Classification Accuracy:** Measures if the correct tool is identified for a given task based on the problem description and available tool catalog. A misclassification or wrong sequencing may 

4https://techreformers.com/solutions/wafr/ 

11 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Akshathala, Adnan, et al. 



<!-- Start of picture text -->
Storage Retrieval<br>Memory<br>Test Case Graph memory Node update/ Execute Test  Compare Calculate<br>Generation initialisation new node Queries Metrics<br>Tools and Parameters  Execution<br>Validation<br>Success Compare with<br>golden output<br>Tools<br>Mapping Classification  Accuracy environmentExecute in Failure Check Error Msg Is it descriptive?LLM interpretable? Performance Reliability<br>a| ee Safety and AlignmentSafety and Alignment<br>Safe and Judge Evaluation<br>Aligned Validate and compare<br>with golden standards<br>LLM<br>Instruction<br>Following environmentExecute in Failed Safety Flag Violation, Log Safety breach  Agent asJudge LLM asJudge<br>Workflows Validation<br>Passed<br>guardrails Verify Correctness<br>Environment Check outcomes<br>End-to-endworkflows Logging expected tools,Compare withparameters Guardrailsviolated Flag ViolationUnauthorized action Configurability<br><!-- End of picture text -->

**Figure 2: Detailed view of Agent Assessment Framework** 

lead to invoking an incorrect or unrelated tool, compromising task reliability. In a CloudOps setting, the agent might select the Audit tool instead of the Monitoring tool due to incorrect classification. **Parameter Accuracy:** Verifies that the parameters passed to a tool are semantically and contextually accurate. For instance, in CloudOps, an agent may attempt to scale a compute instance using a region name instead of an instance ID, leading to incorrect API calls or failed actions. 

_Qualitative Validation:_ To assess how tools behave during real or simulated execution and how effectively the agent responds to runtime conditions. Tools are executed within a sandboxed environment that replicates operational conditions to verify whether they complete successfully. 

**Error Message Evaluation:** When a tool call fails, the returned error should be interpretable and descriptive enough for the LLM to understand the cause and guide corrective actions. For instance, instead of having "Operation Failed" when the agent fails to delete an EC2 instance due invalid authorization, the error message should be descriptive, for example: "Insufficient IAM permissions for deleting EC2 instance". This in turn reduces repetitive, invalid attempts. **Performance:** Compares functionally equivalent tools or endpoints based on latency, cost, and consistency. In CloudOps, an agent may choose between invoking an API through a US-West or US-East server. Evaluating both paths under varying workloads helps determine the optimal route for cost-performance trade-offs. **Reliability:** Tracks error frequency and recovery behavior to assess whether tools execute consistently and recover gracefully from partial failures. Modular tools tend to be more reliable since they 

isolate faults, support independent validation and fault recovery. In contrast, monolithic tool definitions combining multiple operations introduce multiple points of failure[25]. In CloudOps, this can manifest as API calls intermittently failing or returning inconsistent responses. 

## **3.3 LLM** 

An LLM is a core part of the agent, and in extension, the framework as well. It is well integrated in various layers of the system which includes classification of tools, segregation of tasks from user query, LLM as a judge for evaluation, handling errors etc. This requires this component to be tested across various aspects. Our assessment’s Static analysis verifies the presence of required keywords in memory queries prior to action execution. As depicted in Fig. 2, the rest of the assessment of the LLM pillar can be broadly categorized into the following components: 

**Instruction Following** : Evaluates how accurately the LLM adheres to predefined instructions and rule-based workflows. This includes compliance with the system prompt and task-specific instructions, such as parsing execution logs, analyzing tool invocation sequences and memory queries, and verifying alignment with the expected flow and policy constraints. The evaluation is performed using the proposed metrics - through static comparison of expected versus actual behavior, LLM-as-a-judge assessments of logs to detect attempted actions, and dynamic test case generation designed to measure the agent’s ability to follow instructions under varying conditions. In the CloudOps context, this may occur when an agent attempts to delete an EC2 instance despite restricted permissions, or bypasses mandatory steps in a workflow. 

12 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems 

**Safety and Alignment:** Evaluates whether the agent’s generated actions or code are safe, compliant, and aligned with intended objectives. This is especially crucial when agents can execute or modify code and interact with live environments. The evaluation framework operates in two phases: static analysis, to detect potential risks before execution, and dynamic analysis, involving Judge Evaluation to assess runtime behavior. This includes validating outputs against safety policies, flagging violations, and logging breaches for traceability. In the CloudOps context, this may involve scenarios where the agent’s generated deployment commands contain unsafe operations such as modifying production configurations or bypassing approval checks. 

**LLM-as-Judge** LLM-as-Judge [8] evaluates task completion, safety, reasoning quality, memory usage, and policy correctness using structured prompts. The judge receives execution logs and produces scored assessments with justifications, capturing qualitative aspects beyond deterministic metrics. 

**Agent-as-Judge** Recent advancement in agent communication protocols[13] enables agent capability discovery via the _Agent Card_<sup>5</sup> which can be provided to an auditor agent that designs capability tests from the card. The auditor identifies capabilities, issues test instructions, and verifies execution through environment inspection tools that check tool logs, memory queries, and state changes [28]. 

## **3.4 Environment** 

The environment in which an agent operates can be either simulated or real-world. Although real-world environments may offer more representative conditions, their variability often reduces reproducibility. To perform the following evaluations, the framework assumes that the environment provides observability mechanisms to enable effective monitoring and analysis of the agent’s internal states, decisions, and interactions during execution. Modules such as telemetry, tracing, logging, and control-flow visibility collectively support continuous monitoring and facilitate root cause analysis (RCA) during fault conditions. Telemetry modules [6] evaluate agents at runtime by capturing traces and metadata across multiple spans throughout the execution lifecycle, thereby improving explainability by making the system’s decision-making process interpretable. Monitoring helps identify changes within the environment during workflow execution, especially in CloudOps settings, where fluctuations can significantly impact operational costs. Strands Agents<sup>6</sup> apply observability principles at the agent level, whereas cloud platforms such as _CloudTrail_ provide system-wide monitoring and operational auditing. The agent’s behavior is then evaluated within this structured setup, which enables controlled execution, supports repeatable experimentation, and allows verification of agent fidelity under different operational conditions. The desired characteristics of this environment include: 

**Workflows:** The environment contains predefined workflows or test cases that enable systematic assessment [1]. These workflows can be defined in consultation with domain experts or system stakeholders to ensure they represent realistic operational scenarios and 

> 5https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/ 

6https://strandsagents.com/latest/documentation/docs/user-guide/observabilityevaluation/observability/ 

policy constraints. They can vary in complexity from simple singletool invocations to multi-step chains involving interdependent tools and varied solution paths. The evaluation examines whether the agent preserves intended execution order, passes intermediate results correctly, and handles failures or unexpected responses properly throughout the workflow. In CloudOps, test cases might include scenarios of EC2 deployment with networking configuration or S3 bucket setup with access policies, where the evaluation verifies the agent selects the correct AWS APIs and provides accurate parameters in the expected order. 

**Configurability:** The environment provides mechanisms to configure, manage, and reset evaluation settings with minimal effort. When running multiple test cases, it should allow resetting to a known state without requiring a complete restart. Users can define upper and lower bounds for parameters such as resource allocation and cost limits, and evaluate the agent’s performance under varied workloads and fault injection scenarios [1, 4]. This capability enables fine-grained experimentation and reproducibility, allowing the agent to be tested under diverse constraints and configurations. In CloudOps, this involves resetting environments to a baseline or intermediate state between tests, injecting faults, and setting cost or resource limits to enable systematic evaluation without manual cleanup in the console. 

**Guardrails and Security:** The environment enforces operational boundaries and access controls that define the limits within which the agent operates. These ensure that the agents or tools perform only permitted actions and prevent it from executing operations that could cause unintended or harmful outcomes. This involves the enforcement of predefined permissions and policies that govern the agent’s behavior and interactions within the system. In CloudOps, an agent’s attempt to invoke a tool for deleting an existing EC2 instance must be disallowed unless explicit authorization or approval is granted, typically enforced through IAM policies. Such restrictions should be deterministically implemented, either through logical constraints within the agent or system-level mechanisms like role-based access control. Defining these guardrails enables systematic detection and analysis of agent rule or policy violations, which can be monitored using open-source solutions such as Arize Guards [6]. 

## **4 Experimentation and Results** 

We evaluate our assessment framework through experimentation on an autonomous CloudOps system built using MOYA [19]. Our goal is to validate the framework’s ability to surface behavioral failures across pillars using MOYA. Building on our motivation in Section 2, we address two primary objectives: effectiveness in capturing assessment dimensions across all four pillars, and efficiency in terms of cost and time. We investigate the following research questions: 

- **RQ1: How effective is the proposed framework in capturing agent assessment dimensions compared to baseline evaluations?** We compare our four-pillar framework against a baseline evaluation that captures only task completion and tool usage ratios, measuring the framework’s ability to surface failures overlooked by conventional approaches. 

13 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Akshathala, Adnan, et al. 

- **RQ2: What are the failure patterns across assessment pillars?** We analyze the distribution and frequency of failures across the pillars to characterize the types of agent failures. 

- **RQ3: What is the efficiency of the framework in terms of cost and time?** We quantify the computational overhead through scenario execution costs, token consumption, and evaluation time for both runtime execution and judge-based assessment protocols. 

## **4.1 Experimental Setup** 

For the experimental setup, we extended MOYA to incorporate memory mechanisms using the default settings of Mem0 [5] as the Memory pillar. Based on prior findings on the rule-following capabilities of different LLMs [17, 23], we selected the GPT-4o model as the agent reasoning engine, with a temperature of 0.7, chosen after several trial runs to balance predictability and creativity in agent responses. The LLM serves as the core decision-making component, interpreting tasks, selecting tools, and generating responses based on retrieved context. We use ChromaDB for storing embeddings generated via text-embedding-3-small model. To ensure realism, we generated synthetic data reflecting production CloudOps conditions we encountered at MontyCloud, including system logs, and organizational policies, using Sonnet 4.5 due to its ranking on LM Arena<sup>7</sup> . These were exposed to the agents as callable tools, enabling them to retrieve and process information about simulated cloud resources and operational rules. We defined three workflows of varying complexity representing real-world CloudOps scenarios: 

- **Cost Optimization (S1):** A Cost Optimization Agent must reduce AWS infrastructure costs by 30% by identifying and terminating underutilized EC2 instances while adhering to organization policies on non-production prioritization, environment verification, and approvals. Tests whether the agent balances cost reduction goals with operational safety constraints. 

- **Security Incident Response (S2):** A Security Remediation Agent must remediate publicly accessible S3 bucket containing sensitive data exposed for 5 days. The agent must assess exposure scope, check compliance requirements, enable logging before policy changes, and apply remediation while maintaining authorized service access. 

- **Multi-Agent Root Cause Analysis (RCA) (S3):** Diagnose 60% response time degradation in payment service caused by network misconfiguration 5 minutes prior. Requires coordination between Performance, Security, and RCA agents to identify root cause through temporal correlation. Tests whether the system identifies configuration issues versus treating symptoms through costly scaling. 

Each scenario was executed three times independently, with results averaged to ensure reliability and account for non-deterministic LLM behavior. Ground truth for evaluation was established through domain expert consultation with MontyCloud engineers, defining expected behaviors, required tool sequences, and memory retrieval patterns for each scenario. These specifications were codified as evaluation contracts used by both static analysis and judge-based 

> 7https://lmarena.ai/leaderboard 

protocols. We use API keys to run these experiments and report the token consumption and response time. 

## **4.2 Results** 

We evaluate our assessment framework through three research questions. Table 2 defines the metrics used across all evaluations, the trajectory and baseline evaluations are available on GitHub<sup>8</sup> . We report the results for each scenario across the agents used. **Table 2: Overview of the metrics computed through deterministic log analysis: tool sequences matched against phasespecific requirements, memory retrieval compared to golden labels (P/R/F1), and LLM adherence verified through policy lookup patterns in execution traces.** 

|**Category**|**Metric**|**Definition**|
|---|---|---|
|LLM|Policy Adherence|Look up policy guidance before<br>acting.|
||Dependency<br>Inquiry|Retrieving dependency context<br>before acting.|
|Tools|Tool usage|Ratio of tools invoked vs. required<br>tool list.|
||Tool sequence|Runs respecting<br>diagnostic-before-action order.|
||Expected<br>tool<br>calls|Mandatory tools invoked with<br>requiredparameters.|
|Memory|Memory<br>cover-<br>age|Required memory lookups issued<br>(Precision, Recall, F1).|
|Eit|Task completion|Runs meetingdeclared objective.|
|nvronmen|Production<br>guardrail|Flags for environment protection<br>violations.|



_4.2.1_ **RQ1: How effective is the proposed framework in capturing agent assessment dimensions compared to baseline evaluation?** We compare our framework’s pillar-specific assessment (labeled F in Table 3) against a baseline evaluation (labeled B) that captures only task completion and tool usage ratio, representing conventional agent evaluation approaches. We also evaluate two judge-based protocols: Agent-as-Judge and LLM-as-Judge. 

For Agent-as-Judge evaluation, an auditor agent reads each worker agent’s card to dynamically design role-specific capability tests, instructs the worker to demonstrate capabilities, then verifies execution through environment checks. LLM-as-Judge provides holistic assessment across task completion, safety, and memory dimensions using structured prompts (Table 5). Prior research has shown strong correlation between LLM-as-Judge assessments and human evaluation [8], validating this approach for scalable agent evaluation where manual annotation is challenging. 

Baseline evaluation reports identical metrics across both approaches (e.g., S2: 100% task completion, 0.97 tool usage ratio). However, framework-specific metrics reveal underlying execution issues: S1 achieved perfect tool sequencing (100%) but only 33% policy adherence, indicating actions proceeded without consulting safety guidelines. Memory performance varied significantly, with S2 showing particularly low recall (13.1%) and F1 score (18.1%), 

> 8https://github.com/sa4s-serc/asf 

14 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems 

**Table 3: Baseline (B) vs. Framework (F) metrics across all scenarios (S1–S3)** 

||**S**|**1**|**S**|**2**|**S**|**3**|
|---|---|---|---|---|---|---|
|**Metric**|**B**|**F**|**B**|**F**|**B**|**F**|
|Task completion (%)|0|0|100|100|33|33|
|Tool usage (ratio)|0.80|0.80|0.97|0.97|0.62|0.62|
|Tool sequence (%)|–|100|–|33|–|53|
|Expected calls (%)|–|100|–|67|–|62|
|Policy Adherence (%)|–|33|–|100|–|0|
|Dependency Inquiry (%)|–|100|–|0|–|67|
|Memory precision (P) (%)|–|33.7|–|30.0|–|75.56|
|Memory recall (R) (%)|–|37.9|–|13.1|–|50.67|
|Memory F1 (%)|–|31.1|–|18.1|–|51.32|



while S3 achieved 51.32% memory F1. Tool sequence correctness ranged from 33% (S2) to 100% (S1). 

**Table 4: Memory mechanisms (for S3):** 

|**Mechanism**|**P**|**R**|**Expected(gold)**|
|---|---|---|---|
|Single-hop|63.3|61.1|Retrieve one key fact such as baseline response<br>times, subnet, or Security Group (SG) configu-<br>ration.|
|Multi-hop|100.0|26.5|Link_change_and_topology_to confirm DB access<br>from appsubnet onport 5432.|
|Temporal|100.0|29.8|Correlate symptom onset with SG change tim-<br>ing (within 5–10 minutes)to infer causality.|



Table 4 decomposes memory retrieval performance across three mechanisms for S3. Single-hop retrieval achieved balanced precision (63.3%) and recall (61.1%), while multi-hop and temporal reasoning showed perfect precision (100%) but substantially lower recall (26.5% and 29.8% respectively), indicating the agent retrieved accurate information when querying but failed to retrieve all relevant memories. 

**Table 5: LLM-as-Judge results across scenarios (%)** 

|**Scenario**|**Completion**|**Safety**|**Memory**|**Reasoning**|**Overall**|
|---|---|---|---|---|---|
|S1|60|85|75|70|72|
|S2|90|85|70|80|85|
|S3|100|100|100|100|100|



LLM-as-Judge assessment (Table 5) assigns overall scores of 72% (S1), 85% (S2), and 100% (S3). Completion scores increased from 60% (S1) to 100% (S3), while safety scores remained consistently high (85-100%). Memory usage scores ranged from 70% (S2) to 100% (S3), and reasoning scores improved from 70% (S1) to 100% (S3). The completion score in S1 is reported as 60% since the agent expected user input before proceeding to take an action, which is why its completion rate is reported as 0% in Table 3. Agent-asJudge dynamically determined test counts based on each agent’s capabilities, conducting 31 tests total across five agents: 6 tests each for Cost and Security agents in S1-S2, and for S3, 9 tests for Performance Agent, 4 for Security Agent, and 6 for RCA Agent. Failures are detailed in Table 6. 

_4.2.2_ **RQ2: What are the failure patterns across assessment pillars?** We analyze failure patterns by tracking average failures 

per pillar across scenarios to identify which assessment dimensions would be missed without pillar-specific evaluation. Table 6 reports the average number of failures observed in each pillar, with example failure modes illustrating the types of issues captured. 

**Table 6: Pillar ablation with Agent-as-Judge findings. Average failures per run (3 runs/scenario).** 

|**Pillar**|**S1**|**S2**|**S3**|**Example Failure**|
|---|---|---|---|---|
|LLM|1.67|1.33|1.00|Skipped company policy checks be-<br>fore acting (2/3 runs in S1; 0% depen-<br>dencychecks in S2).|
|Tools|1.00|2.33|7.67|Missed compliance verification (S2);<br>incomplete diagnostic phases (S3: 2/5<br>completed).|
|Memory|0.67|2.33|3.67|Low recall (13% in S2); failed to link<br>changes to symptoms (S3: 26% to 30%<br>recall).|
|Environment|0.00|0.00|2.00|Production state modified despite<br>protection rules(S3 only).|



Tool orchestration failures escalate with scenario complexity (S1: 1.00 to S3: 7.67), driven by incomplete diagnostic workflows. Agent-as-Judge verification revealed S3 coordination gaps: Performance Agent missed configuration lookups (9/10 tests), Security Agent skipped policy consultation (4/5 tests). Memory failures show precision-recall imbalance. S3 multi-hop retrieval achieved 100% precision but only 26.5% recall, retrieving accurate facts while missing context needed to connect configuration changes to symptoms. LLM pillar failures stem from policy adherence gaps; agents skipped policy checks in 67% of S1 runs before terminating instances. 

_4.2.3_ **RQ3: What is the efficiency of the framework in terms of cost and time?** We measure the computational overhead introduced by our framework through scenario execution costs, token consumption, and evaluation time. Figure 3 shows the distribution of these metrics across three runs per scenario, while Figure 4 compares the overhead introduced by LLM-as-Judge and Agent-asJudge evaluation protocols. 



<!-- Start of picture text -->
Input Tokens Output Tokens<br>30000<br>2500<br>25000<br>2000<br>20000<br>1500<br>15000<br>1000<br>10000 500<br>S1 S2 S3 S1 S2 S3<br>Response Time Cost<br>450 0.10<br>400 0.09<br>350 0.08<br>300 0.07<br>250 0.06<br>200 0.05<br>150 0.04<br>100 0.03<br>0.02<br>S1 S2 S3 S1 S2 S3<br>Number of Tokens Number of Tokens<br>Time (s) Cost (USD)<br><!-- End of picture text -->

**Figure 3: Distribution of input tokens, output tokens, response time, and cost across scenarios** 

Average scenario execution required $0.0621 per run, consuming 19,644 input tokens and 1,301 output tokens over an average execution time of 183.5 seconds. Costs scaled with scenario complexity 

15 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Akshathala, Adnan, et al. 

from S1 ($0.0405, 160.3s) to S3 ($0.0818, 203.5s). Fig. 3 reveals variability in S1 input tokens (7,784–19,335) and S3 response time (72– 454s), indicating scenario-dependent resource utilization patterns. 



<!-- Start of picture text -->
(a) Evaluation Cost (b) Evaluation Time<br>1000<br>1.0 $0.9572 913.4s<br>800<br>0.8<br>600<br>0.6<br>0.4 400<br>0.2 200 183.5s<br>0.0 $0.0621 $0.0593 0 14.7s<br>Scenario LLM-as-Judge Agent-as-Judge Scenario LLM-as-Judge Agent-as-Judge<br>Execution Execution<br>Cost (USD)<br>Time (seconds)<br><!-- End of picture text -->

**Figure 4: Evaluation overhead comparison showing (a) cost and (b) time for LLM-as-Judge and Agent-as-Judge protocols.** LLM-as-Judge added minimal overhead ($0.0593 total across all scenarios, 14.7 seconds), consuming 18,602 input tokens and 1,277 output tokens. In contrast, Agent-as-Judge incurred higher costs ($0.9572 total, 913.4 seconds) with 289,006 input tokens and 23,472 output tokens. The cost difference reflects the depth of assessment. S3 accounted for the majority of Agent-as-Judge cost ($0.6110, 632.1s) due to multi-agent coordination requiring extensive verification cycles. Agent-as-Judge incurs 16× higher cost and 62× longer execution time due to extensive capability testing. 

## **5 Discussions** 

Our collaboration with MontyCloud provided continuous feedback from production-scale deployments, allowing us to validate the practicality and efficiency of the proposed framework under real operational conditions. The comparison from the baseline (RQ1) shows that conventional approaches miss critical behavioral issues. For instance, S1 achieved perfect tool sequencing but only 33% policy adherence, taking actions without consulting safety guidelines-a failure baseline metrics cannot detect. S2 showed low memory recall (13.1%) despite task completion. Judge-based protocols revealed additional failures: the Remediation Agent skipped verification steps in 20% of tests, while LLM-as-Judge gave S1 only 72% overall. Further, in multi-agent scenario (S3) Judge methods help identify the error propagating through agents. This demonstrates that assessment frameworks must explicitly check instruction following, policy adherence, and memory usage beyond final outcomes. The pillar ablation study (RQ2) reveals where assessment effort should focus. Tool orchestration had the highest failure rate in complex scenarios, primarily from skipping diagnostic steps. Memory failures increased with scenario complexity, while Environment violations appeared only in multi-agent scenarios where production states changed despite guardrails. These patterns indicate that tool sequencing and memory management need particular attention in the multi-agent scenarios. The efficiency analysis (RQ3) shows practical feasibility with average execution cost of $0.0621. LLM-as-Judge added minimal overhead ($0.0593, 14.7s), while Agent-as-Judge incurred higher costs ($0.9572, 913.4s). This suggests LLM-as-Judge for continuous monitoring and Agent-as-Judge for pre-deployment audits. 

**Implications for Researchers:** While existing approaches [9] focus on model-centric metrics, there is a need for assessment of behavioral uncertainness across system components. Our results 

show the agents violating policies and missing important context across the scenarios evaluated in RQ1. This reveals research directions for handling the high tool orchestration failure rate in multi-agent scenarios indicates the need for better coordination mechanisms and formal verification methods that enforce diagnosis before taking an action. The precision-recall gap in memory presents the need for balancing accuracy with completeness, agents retrieve correct information but miss decision relevant context. The cost tradeoff discussed in RQ3 between the judge-based protocols motivates a research direction for dynamically adaptive evaluation strategies to select the assessment depth based on risk levels. Further, our scenarios required manual specification of expected behaviors while generating test cases, automated test case generation from agent capabilities presents a promising direction. Extending our framework to other agentic paradigms such as code generation or multi modal agents will validate and identify domain-specific evaluation requirements. 

**Implications for Practitioners:** Existing methods evaluate primarily on final outcomes [26] , which which may explain the low translation from a prototype to production conversion rates, due to which these failures surface which are otherwise invisible to standard metrics. Our results show that agents exhibit these failures, in S3 skipped policy checks, while S1 could not resolve the issue, it terminated while asking for permission to terminate the instances. This highlights the need for evaluations to perform behavior-based testing apart from outcome-based testing. Developers should implement pillar-specific checks for instruction following, policy adherence and implement defensive guardrails at the environment layer (IAM policies, control policies). For evaluation, using LLM and Agent based judges while highlight such behavioral aspects at runtime. Implanting telemetry by capturing tool call invocations, memory retrieval and storage, policy checks will set the foundation for prompt refinements and root cause analysis when agents fail. 

## **5.1 Threats to Validity** 

**External Validity.** CloudOps was chosen as the evaluation domain for this work as a representative setting to demonstrate the broader applicability of the proposed multi-agent framework. However, the proposed framework, interaction patterns, and evaluation methodology are not CloudOps-specific by design. The evaluated scenarios may not capture challenges in creative or long-horizon tasks. However, they span varying levels of complexity informed by our experience with CloudOps. 

**Internal Validity.** Uniform temperature (0.7) and model selection (GPT-4o) may not capture all behavior distributions. Ground truth contracts defined by the us may not reflect all valid solution paths. Judge-based evaluation may introduce LLM evaluation biases. **Construct Validity.** Memory assessment excludes retrieval efficiency. The textual simulation limits evaluation of some performance characteristics such as resource utilization. Environment checks do not measure observability or recovery mechanisms. 

## **6 Related Work** 

Research on agentic systems highlights the ongoing challenges across the domains of memory, task-following, safety, evaluation, and multi-agent coordination. In the memory domain, Maharana et al. [15] show that LLMs struggle to track long conversations, while RAG-based approaches improve access to information there, Hu et 

16 

AGENT ’26, April 12–18, 2026, Rio de Janeiro, Brazil 

Beyond Task Completion: An Assessment Framework for Evaluating Agentic AI Systems 

al. [12] highlight its limitations. Overall, these findings suggest that a combination of approaches is needed to handle the evaluation of memory mechanism. For instruction-following, Qi et al. [20] show the importance of assessment to capture performance on complex instructions involving multiple constraints, especially when tools or conditions are involved. Dong et al. [6] and Andriushchenko et al. [2] focus on improving transparency, multi-agent coordination, and the robustness against harmful instructions. These studies emphasize the need for evaluation frameworks that balance reasoning, execution, safety, and monitoring. Further, research on self-adaptive and multi-agent systems by Nascimento et al. [18] demonstrate the inconsistencies in memory and decision-making remain. The study “Why Do Multi-Agent LLM Systems Fail?” [3] by Cemri et al. analyzes MAS failures by identifying gaps in specifications, alignment, and verification. Despite these advances, most evaluations focus on model accuracy or individual components, leaving runtime uncertainties, tool use, multi-agent coordination, and interactions with dynamic environments underexplored. To the best of our knowledge, there does not exist unified evaluation system of an agentic system. To address these limitations, we propose an Agent Assessment framework that evaluates agentic systems across four pillars: LLMs, Memory, Tools, and Environment, and highlight the failures which surface using CloudOps scenarios to capture overall agent behavior. 

## **7 Conclusions and Future Work** 

In this work, we present the first steps towards an assessment framework for evaluating agentic AI systems across four pillars. Through an industrial case of autonomous cloudOps, we demonstrate the effectiveness and efficiency of our framework. Future research directions include, but are not limited to: i) applying to diverse domains beyond CloudOps; ii) Integration with self-adaptive abilities to support continuous improvement of the agentic system; and iii) leveraging agent-as-judge to discover failure modes and assessment automation. 

## **References** 

   - [12] Yuanzhe Hu, Yu Wang, and Julian McAuley. 2025. Evaluating memory in llm agents via incremental multi-turn interactions. _arXiv preprint arXiv:2507.05257_ (2025). 

   - [13] Yedidel Louck, Ariel Stulman, and Amit Dvir. 2025. Improving Google A2A Protocol: Protecting Sensitive Data and Mitigating Unintended Harms in MultiAgent Systems. arXiv:2505.12490 [cs.CR] https://arxiv.org/abs/2505.12490 

   - [14] Qinghua Lu, Liming Zhu, Xiwei Xu, Zhenchang Xing, and Jon Whittle. 2024. Toward Responsible AI in the Era of Generative AI: A Reference Architecture for Designing Foundation Model-Based Systems. _IEEE Software_ PP (11 2024), 1–7. doi:10.1109/MS.2024.3406333 

   - [15] Adyasha Maharana, Dong-Ho Lee, et al. 2024. Evaluating very long-term conversational memory of llm agents. _arXiv preprint arXiv:2402.17753_ (2024). 

   - [16] Dany Moshkovich and Sergey Zeltyn. 2025. Taming Uncertainty via Automation: Observing, Analyzing, and Optimizing Agentic AI Systems. arXiv:2507.11277 [cs.AI] https://arxiv.org/abs/2507.11277 

   - [17] Rudra Murthy et al. 2025. KCIF: Knowledge-Conditioned Instruction Following. arXiv:2410.12972 [cs.CL] https://arxiv.org/abs/2410.12972 

   - [18] Nascimento et al. 2023. Self-adaptive large language model (llm)-based multiagent systems. In _2023 IEEE International Conference on Autonomic Computing and SelfOrganizing Systems Companion (ACSOS-C)_ . IEEE, 104–109. 

   - [19] Kannan Parthasarathy, Karthik Vaidhyanathan, et al. 2025. Engineering LLM Powered Multi-Agent Framework for Autonomous CloudOps. In _IEEE/ACM 4th International Conference on AI Engineering – Software Engineering for AI (CAIN)_ . 201–211. doi:10.1109/CAIN66642.2025.00031 

   - [20] Yunjia Qi, Hao Peng, et al. 2025. Agentif: Benchmarking instruction following of large language models in agentic scenarios. _arXiv preprint arXiv:2505.16944_ (2025). 

   - [21] Claudia Raibulet, Ilias Gerostathopoulos, and Osman Abdelmukaram. 2026. SURE! A Catalog of Uncertainties and RELAXed Requirements for Self-adaptive Systems. In _Software Architecture_ . Springer Nature Switzerland, Cham, 214–223. 

   - [22] Yoav Shoham and Kevin Leyton-Brown. 2008. _Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations_ . Cambridge University Press, USA. 

   - [23] Wangtao Sun et al. 2024. Beyond Instruction Following: Evaluating Inferential Rule Following of Large Language Models. arXiv:2407.08440 [cs.CL] https: //arxiv.org/abs/2407.08440 

   - [24] Danny Weyns. 2018. Engineering self-adaptive software systems–an organized tour. In _2018 ieee 3rd international workshops on foundations and applications of self* systems (fas* w)_ . IEEE, 1–2. 

   - [25] Yu Yuan et al. 2024. Do LLMs Overcome Shortcut Learning? An Evaluation of Shortcut Challenges in Large Language Models. In _Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing_ . Association for Computational Linguistics, Miami, Florida, USA, 12188–12200. doi:10.18653/v1/ 2024.emnlp-main.679 

   - [26] Shaokun Zhang et al. 2025. Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems. arXiv:2505.00212 [cs.MA] https://arxiv.org/abs/2505.00212 

   - [27] Zeyu Zhang, Xiaohe Bo, et al. 2024. A Survey on the Memory Mechanism of Large Language Model based Agents. arXiv:2404.13501 [cs.AI] https://arxiv.org/ abs/2404.13501 

   - [28] Mingchen Zhuge et al. 2024. Agent-as-a-Judge: Evaluate Agents with Agents. arXiv:2410.10934 [cs.AI] https://arxiv.org/abs/2410.10934 

- [1] Pierre Andrews, Amine Benhalloum, et al. 2025. ARE: Scaling Up Agent Environments and Evaluations. arXiv:2509.17158 [cs.AI] https://arxiv.org/abs/2509.17158 

- [2] Maksym Andriushchenko, Alexandra Souly, et al. 2024. Agentharm: A benchmark for measuring harmfulness of llm agents. _arXiv preprint arXiv:2410.09024_ (2024). 

- [3] Mert Cemri, Melissa Z Pan, Shuyi Yang, et al. 2025. Why do multi-agent llm systems fail? _arXiv preprint arXiv:2503.13657_ (2025). 

- [4] Yinfang Chen et al. 2025. AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds. arXiv:2501.06706 [cs.AI] https://arxiv.org/ abs/2501.06706 

- [5] Prateek Chhikara, Dev Khant, et al. 2025. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory. arXiv:2504.19413 [cs.CL] https: //arxiv.org/abs/2504.19413 

- [6] Liming Dong et al. 2024. AgentOps: Enabling Observability of LLM Agents. arXiv:2411.05285 [cs.AI] https://arxiv.org/abs/2411.05285 

- [7] Shiqing Fan, Xichen Ding, et al. 2025. MCPToolBench++: A Large Scale AI Agent Model Context Protocol MCP Tool Use Benchmark. arXiv:2508.07575 [cs.AI] https://arxiv.org/abs/2508.07575 

- [8] Jiawei Gu, Xuhui Jiang, et al. 2025. A Survey on LLM-as-a-Judge. arXiv:2411.15594 [cs.CL] https://arxiv.org/abs/2411.15594 

- [9] Mohammed Mehedi Hasan, Hao Li, et al. 2025. An Empirical Study of Testing Practices in Open Source AI Agent Frameworks and Agentic Applications. arXiv:2509.19185 [cs.SE] https://arxiv.org/abs/2509.19185 

- [10] Ahmed E. Hassan et al. 2025. Agentic Software Engineering: Foundational Pillars and a Research Roadmap. 

- [11] Sara M Hezavehi et al. 2021. Uncertainty in self-adaptive systems: A research community perspective. _ACM Transactions on Autonomous and Adaptive Systems (TAAS)_ 15, 4 (2021), 1–36. 

17 

