ETH Library 



# Agentic LLMs in the supply chain: towards autonomous multi-agent consensus-seeking 

#### **Journal Article** 

**Author(s):** Jannelli, Valeria; Schopf, Stefan; Bickel, Matthias; Netland, Torbjörn ; Brintrup, Alexandra 

**Publication date:** 2025 

**Permanent link:** <u>https://doi.org/https://doi.org/10.3929/ethz-c-000791068</u> 

**Rights / license:** <u>Creative Commons Attribution- NonCommercial-NoDerivatives 4.0 International</u> 

##### **Originally published in:** 

International Journal of Production Research, https://doi.org/10.1080/00207543.2025.2604311 

This page was generated automatically upon download from the ETH Zurich Research Collection. For more information, please consult the Terms of use. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH https://doi.org/10.1080/00207543.2025.2604311 



## **Agentic LLMs in the supply chain: towards autonomous multi-agent consensus-seeking** 

Valeria Jannelli<sup>a,b</sup> , Stefan Schöpf<sup>b,c</sup> , Matthias Bickel<sup>a</sup> , Torbjørn Netland<sup>a</sup> and Alexandra Brintrup b,c 

aDepartment of Management, Technology, and Economics, ETH Zurich, Zurich, Switzerland; bDepartment of Engineering, University of Cambridge, Cambridge, UK;<sup>c</sup> Data-Centric Engineering, The Alan Turing Institute, London, UK 

###### **ABSTRACT** 

Supply Chain Management relies on human consensus in decision-making to avoid emergent problems like the bullwhip effect. Some routine consensus processes, especially those that are timeintensive, can be automated. Previously proposed supply chain automation solutions for consensusseeking and coordination faced computational challenges, resulting in high entry barriers. Recent advances in Generative AI, particularly Large Language Model agents (LLM agents), could overcome these barriers. This paper explores how LLM agents can automate consensus-seeking in supply <u>chains. We introduce a series of novel, supply chain-specific consensus-seeking frameworks and vali-</u> datetheeffectivenessofourapproachthroughacasestudyininventorymanagement,whereagents that represent companies in a supply chain are able to balance selfish goals with systemic outcomes through conversation. Our results show that introducing LLM-based consensus-seeking frameworks reduces bullwhip effects. When equipped with appropriate tools, LLM agents can minimise bullwhip better than restocking policies and centralised demand approaches. Additionally, when LLM agents are handled within a negotiation framework, their behaviour converges to best practices in the supply chain literature on how to lessen the bullwhip effect. To provide a foundation for further advancements in LLM-based autonomous supply chain solutions, we open-source our code. 

###### **ARTICLE HISTORY** 

Received 15 November 2024 Accepted 2 December 2025 

**KEYWORDS** Multi-agent system; supply chain collaboration; LLM agent; autonomous agent; agentic workflow; Generative AI 

### **1. Introduction** 

As firms engage in trade with one another to produce their goods and services, they form interdependent networks. Researchers have formally defined Complex Adaptive Supply Networks (CASN) as networks that contain multiple interdependent firms, which observe their environment partially, interact and take goaldirected actions on behalf of the stakeholders they represent (Choi, Dooley, and Rungtusanatham 2001). These actions then lead to non-linear outcomes and dynamic patterns of cooperation and defection (Nair and ReedTsochas 2019). Some of the noteworthy emergent patterns that have been found in CASN include bullwhip effects, shortage gaming, scale-free and nested structures that impact system performance and resilience (Brintrup, Ledwoch, and Barros 2016; Brintrup, Wang, and Tiwari 2015; Sterman and Dogan 2015; Surana et al. 2005; Wycisk, McKelvey, and Hülsmann 2008). A key insight from such patterns is that firms that consider only their own behaviour in isolation from others’ perform suboptimally, whereas those seeking consensus do reach better outcomes. 

Here, _consensus-seeking_ is defined as a process that involves multiple parties interacting to reach a coordinated decision, whereby each party has different goals and may have a different understanding of the problem. However, all parties have a common interest in reaching an agreement. Within the context of Supply Chain Management (SCM), consensus-seeking is closely related to supply chain coordination and integration. It has been described as ‘collaborative working for joint planning, joint product development, mutual exchange of information and integrated information systems, cross coordination on several levels in the companies on the network, long-term cooperation and fair sharing of risks and benefits’ (Skjoett-Larsen 2000). A common example of consensus-seeking occurs in demand planning, where participants along a chain need to agree on appropriate order quantities. Failure to achieve consensus results in the bullwhip effect, where small demand changes can cause large production and inventory fluctuations upstream in the supply chain (Lee, Padmanabhan, and Whang 1997a, 1997b). To mitigate such challenges, the supply chain literature has emphasised 

> © 2025 The Author(s). Published by Informa UK Limited, trading as Taylor & Francis Group. 

> This is an Open Access article distributed under the terms of the Creative Commons Attribution-NonCommercial-NoDerivatives License (http://creativecommons.org/licenses/by-ncnd/4.0/), which permits non-commercial re-use, distribution, and reproduction in any medium, provided the original work is properly cited, and is not altered, transformed, or built upon in any way. The terms on which this article has been published allow the posting of the Accepted Manuscript in a repository by the author(s) or with their consent. 

**CONTACT** Alexandra Brintrup ab702@cam.ac.uk Institute for Manufacturing, 17 Charles Babbage Road, CB3 0FS Cambridge, United Kingdom 

2 V. JANNELLI ET AL. 



**Figure 1.** Complex consensus-seeking tasks are out of scope for current autonomous agents. LLM agents promise a new frontier, enabling complex consensus finding at scale beyond human speeds and thus unlocking significant efficiency improvements. 

coordination, integration and consensus (Marty and Ruel 2024). 

This paper focuses on a subset of supply chain consensus-seeking problems that could benefit from automated handling using AI. It is well acknowledged in the literature that decisions on delivery quantities, order frequency and capacity allocation often involve situations where end-to-end coordination would yield superior outcomes (Viswanadham 2002; Xu, Mak, Proselkov, et al. 2024). However, end-to-end coordination requires manual orchestration. While humans are able to solve complex consensus tasks, they are limited in the volume of tasks they can fulfil in a given time window, as illustrated in Figure 1. End-to-end consensus itself is a particularly difficult task that involves multiple actors over a chain of interdependencies to iteratively communicate with one another to achieve consensus. Given the high complexity of doing so at scale, individual firms are disincentivised to take part in consensus-seeking, typically reserving such efforts for high-impact decisions while neglecting a long tail of lower-priority tasks that, cumulatively, also have substantial effects on supply chain performance. 

A lack of end-to-end consensus often leads to sub-optimal outcomes, such as loss of efficiency (e.g. low utilisation of capacity Mak et al. 2023), information distortion (e.g. bullwhip effect Lee, Padmanabhan, and Whang 1997b, and shortage gaming Samuel and Mahanty 2003). Some examples of issues that arise between companies include a lack of timely information and inefficient crisis response due to ineffective communication exchange between supply chain players 

(S. L. Pan, Pan, and Leidner 2012). Ma, Pal, and Gustafsson (2019) argue that more effective consensus-seeking and coordination should be aspired to in a world with increasing supply chain disruptions; this is also explored by (Choi et al. 2023). 

Consensus and supply chain integration is a multidisciplinary area of study that cuts across social science, operations research, computer science and engineering. Researchers have proposed autonomous algorithms to handle low-level operational coordination in supply chains for over 20 years (see a review Xu, Mak, Proselkov, et al. 2024). The idea behind these proposals was that automation would alleviate manual effort, allowing system-wide solution optimality. Decisions would have become more traceable and transparent. Most of these proposals centred around intelligent software agents, which are computer programs that mimic humans and act on their behalf (Wooldridge and Jennings 1995a). They do so by perceiving their environment (e.g. ERP system data, data from digital twins, data from the web), interacting with other agents (e.g. co-optimisation with a common objective function, negotiation), using tools (e.g. other algorithms), and making decisions to achieve their given goals. 

However, as reflected by practice, these concepts did not gain traction in real-life (Hendler 2007; Marik and McFarlane 2005). Reasons for failure are numerous, but two key causes have been hypothesised. First, developing agent solutions requires expertise and structured data. Hence, barriers to entry are too high due to costs and skill shortages (Xu, Mak, and Brintrup 2021; Xu, Mak, Proselkov, et al. 2024). Agents need significant adaptation to work on new tasks or changes in the environment. Second, agents need well-defined interaction protocols and interoperability to work with other automated entities or humans across companies, turning the problem into a multi-company change management project (Marik and McFarlane 2005). Multi-agent systems were deemed practically infeasible to implement and run, especially for SMEs with resource budgets. 

_Generative AI_ refers to models capable of producing content such as natural language text, images, or video after being trained on large-scale datasets. It has seen enormous progress in recent years. Within this field, Large Language Models (LLMs) have emerged as a particularly transformative branch, enabling a wide range of applications such as conversational agents (Jackson et al. 2024) or generating computer code for supply chain simulation (Jackson, Jesus Saenz, and Ivanov 2024). 

Recent developments in LLMs have shown advanced logic and reasoning to address the two key aforementioned challenges, possibly enabling a new frontier as shown in Figure 1. A particularly promising area is the 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 3 

use of _LLM agents_ , which can be defined as computational software agents that retrieve memories, reflect, and plan using LLMs as their central reasoning component (Park et al. 2023). These agents are typically designed to operate independently or in coordination with other agents or humans to act as mediators (Dorri, Kanhere, and Jurdak 2018) or as negotiators (Mukobi et al. 2023). 

We hypothesise that these developments can significantly improve autonomous consensus-seeking and overcome the barriers that multi-agent systems have faced earlier (Xu, Mak, and Brintrup 2021). The flexibility of LLMs stems from the fact that they can engage in consensus-seeking with each other as well as with humans. This is relevant because not all companies will have LLM agents, requiring that an LLM is able to interact with humans in those companies. 

Despite promising developments, there is much work to be done before LLM agents will be commonly used in supply chain settings. While LLM agents seem promising for supply chain consensus-seeking at scale, to the best of our knowledge, no established literature explores their capabilities from a CASN perspective with sequential dependencies and partial system observability. Applying an LLM agent from a single firm’s perspective is not as difficult because a firm’s ‘agent’ would not have conflicting goals over its suppliers, and would have access to all the data over their own interactions with their suppliers. The firm agent would give a single decision at a time that is fully observable. 

We address this literature gap with a series of SCMspecific LLM agent frameworks and an accompanying case study (building upon the simulation environment of Liu et al. 2022) to demonstrate its effectiveness in a sequential supply chain inventory replenishment task. Throughout this paper, we use the term ‘framework’ to refer to a structured and modular orchestration pattern that governs how LLM agents perceive, communicate, and act in a sequential supply chain setting. Our frameworks define both the agent-level architecture (e.g. perception, memory, decision-making) and the interagent communication protocols (e.g. information sharing, negotiation), including optional tool usage. Each framework represents a specific implementation pattern for achieving consensus among agents under different assumptions about agent capabilities and the supply chain context. 

The key research questions we answer in this paper are as follows: 

- (i) Are standalone LLM agents able to outperform established heuristics in a sequential SC setting with partial observability? How is their performance moderated by enhancements such as tool use? 

- (ii) Are multiple LLM agents which share information between adjacent neighbours able to outperform established heuristics in a sequential SC setting with partial observability? How is their performance moderated by enhancements such as tool use, information sharing, and negotiation capabilities? 

This paper offers three contributions to the nascent literature on LLM agents for the supply chain: 

- (i) A modular consensus-seeking framework for LLM agents in the sequential supply chain, including the possibility for tool usage and communication between neighbouring agents. 

- (ii) An empirical case study and increased framework sophistication: our results highlight under which circumstances using tools within the framework can achieve significant performance enhancements, and in which cases it is best to prioritise sophisticated multi-agent communication over tool usage. 

- (iii) An open-source implementation of the consensusseeking framework that the supply chain research community can use and build upon, integrated into a problem-agnostic, scalable sequential supply chain simulation environment that can be extended to analyse similar topics. 

### **2. Related work** 

Automating supply chain consensus-seeking has been a longstanding challenge spanning multiple AI paradigms. This section traces the evolution from early rule-based multi-agent systems to current LLM-based approaches, examining why previous solutions faced adoption barriers and how recent advances in Generative AI may overcome them. We also identify the need for supply chain-specific benchmarking environments to evaluate these emerging technologies. 

#### **_2.1. Supply chain complexity and the evolution toward AI-Driven solutions_** 

The global supply chain ecosystem has become vulnerable and complex, characterised by multiple types of relationships and network flows. Disruptions in supply chains are becoming more frequent (Bode et al. 2011; Ivanov et al. 2023) due to increasing symptoms of climate change, pandemics, regional conflicts and geopolitical weaponisation of critical goods. Due to the increasing scale and complexity of supply chains, companies are facing difficulties in optimising supply chain processes, as traditional optimisation methods lack the ability to 

4 V. JANNELLI ET AL. 

capture the complexity and vulnerabilities of real-world supply chains (Smyth et al. 2024). 

This state of affairs calls for faster, data-driven, and more scalable supply chain consensus-seeking and coordination, which allows supply chain actors to improve their coordination and respond to frequent changes (Marty and Ruel 2024). As mentioned earlier, the use of AI to automate consensus seeking and coordination has been proposed to achieve these goals for more than two decades. However, industrial adoption had been slow, mainly due to the difficulty in implementing agent based systems with existing tools (see Xu, Mak, and Brintrup 2021; Xu, Mak, Proselkov, et al. 2024 for recent reviews). As the field of AI has seen a significant shift with the arrival of deep neural networks, and more recently Generative AI, supply chain researchers and practitioners are again increasingly looking into AI to address long-standing automation problems that involve multiple supply chain actors (Hendriksen 2023). The use of AI has thus far been confined to single organisational settings, whereas the supply chain functions as an ecosystem of multiple organisations (Dash et al. 2019; G. Wang et al. 2016). Recent advances demonstrate that generative AI assistants can enhance operational performance within single organisations. For example, Löwhagen, Schwendener, and Netland (2025) show that a RAGbased troubleshooting assistant significantly improved task performance in train commissioning by bridging skill gaps among technicians. Building on these developments, recent research has explored how synthetic data generation can address fundamental barriers to AI adoption in supply chains. Generative AI applications involving LLMs are starting to penetrate supply chain applications, for example Long et al. (2025) introduce the SCMLOps (Supply Chain Management with Machine Learning Operations) framework, demonstrating how generative models, including fine-tuned LLMs (GPT-2, LLaMA 3), GANs, and diffusion models, can generate privacy-preserving synthetic data that enables collaboration between supply chain partners without exposing proprietary information. Beyond individual organisational improvements, Generative AI is enabling new approaches to supply chain visibility and coordination. Zheng and Brintrup (2025) demonstrate how pre-trained language models combined with knowledge graphs can extract relational supply chain information with near-perfect accuracy across 27 countrylevel datasets, addressing the critical challenge of multitier visibility beyond direct trading partners. Their work shows that LLMs contain untapped supply chain knowledge that can be leveraged without fine-tuning, reducing computational barriers for practical deployment. It has long been recognised that the pursuit of supply chain 

optimisation within a single organisational boundary leads to locally optimal outcomes, and has negative consequences in the long run. Researchers pointed out that it is essential to elevate the level of AI-based tools to encompass larger supply networks (Hendriksen 2023; Olan et al. 2022). 

#### **_2.2. Agent-Based approaches in supply chain management_** 

As it has long been pointed out by CASN research (Carter, Rogers, and Choi 2015), when we move from the mindset of ‘optimisation within an organisational boundary’ to multi-organisational setting, each organisation in the supply chain must recognise the existence of conflicting goals. In a CASN, each firm itself is an ‘agent’, that acts in pursuit of own goals with partial visibility over the system. The pursuit of ‘optimisation’, therefore, becomes a pursuit of ‘consensusseeking’ (Nair, Narasimhan, and Choi 2009). Within CASN, consensus-seeking encompasses not only technical optimisation but also processual, relational, and qualitative dimensions that shape supply network dynamics (Giannoccaro, Nair, and Choi 2018; Ivanov and Dolgui 2020; Nair and Reed-Tsochas 2019; Villena, Choi, and Revilla 2021). Although the rich field of consensusseeking has multiple qualitative and quantitative dimensions, we acknowledge that effective supply chain integration requires addressing both technical and managerial aspects. Our main focus in this paper is the creation of a technical framework that serves as an enabler for firms to seek consensus within the broader CASN context. This framework contributes to CASN literature by providing technical infrastructure for adaptive, emergent supply network behaviours. While focussing on technical consensus-seeking, we recognise this as one element within broader coordination challenges, including trust-building and relationship management. The historical evolution of agent-based approaches in SCM consensus-seeking within CASN can be grouped into three major paradigms: Rule-based Multi-Agent Systems (MAS), Reinforcement Learning and Multi-Agent Reinforcement Learning (RL/MARL), and more recently LLM agents. These technical approaches represent attempts to operationalise the adaptive and emergent properties characteristic of complex supply networks. We briefly review these in the following paragraphs. 

In computer science, agents are defined as computational entities in an environment from which they perceive different parameters that are used to make decisions, take goal-directed decisions, and actuate them (Wooldridge and Jennings 1995a). A MAS is comprised of multiple interacting agents with distinct goals and 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 5 

behaviours, working together or competing in a shared environment to carry out tasks (Wooldridge, Jennings, and Kinny 2000). 

Rule-based MAS gained traction in the 2000s, owing to their ability to simulate distributed planning, procurement, and negotiation tasks in supply chains (Brintrup et al. 2011; Wooldridge and Jennings 1995b). MAS typically relied on explicitly defined roles, hand-crafted behavioural rules and structured communication templates. In cooperative settings, agents consider each other’s information and decisions, aiming for consensus and optimal coordination (Dorri, Kanhere, and Jurdak 2018). Each entity operates with limited information and must make decisions autonomously, while depending on the performance and actions of other entities in upstream and downstream tiers. These characteristics make MAS particularly suited to study sequential supply chains with multiple tiers of dependency and partial observability. In fact, a large number of multi-agent simulation studies in SCM exist. However, we note that a MAS, as opposed to a simulation, is a system that hosts computational agents that interact with and impact real life. 

#### **_2.3. Implementation challenges and Industrial adoption_** 

Supply chain automation with agents has started with eProcurement (Neef 2001). eProcurement refers to using digital tools and platforms to facilitate and conduct negotiations between buyers and suppliers within the procurement process. This can include e-auctions, e- tenders, and other online systems to facilitate price discussions, contract terms, and other aspects of supplier relationships. eProcurement has served as a motivator for designing agent-based systems to automate procurement processes, which then led to the beginning of research streams on automated negotiation (Jennings et al. 2001; Jiao, You, and Kumar 2006) and learning optimal pricing strategies in business-to-business environments (Coehoorn and Jennings 2004). Broadly, researchers investigated negotiation desiderata and application of negotiation protocols (Fatima, Kraus, and Wooldridge 2015), although much of this work remained within the broader field of autonomous agents (Xu, Mak, and Brintrup 2021; Xu, Mak, Minaricova, et al. 2024). 

Beginning in the 2000s, supply chain researchers turned their attention to supply chain coordination agent systems, focussing on the efficient division of agent roles, decision optimality, and information sharing in end-toend supply chains (Xue et al. 2005). Previous attempts tackled a diverse range of problems, such as inventory 

planning and order scheduling (Julka, Karimi, and Srinivasan 2002), collaborative production planning (Dangelmaier, Heidenreich, and Pape 2005), integration within IoT environments (López et al. 2011), automated procurement (Brintrup et al. 2011), disruption management (Behdani, Lukszo, and Srinivasan 2019) across various industrial sectors such as aerospace, logistics, recycling, construction, food and agriculture, (see Xu, Mak, Proselkov, et al. 2024 for a review). While MAS offered transparency and modularity, it struggled with adaptability. Each implementation had to be tailored to the environment, making them costly to scale and maintain. Moreover, the rigid logic of these systems made them susceptible to errors, and they were deemed inadequate under uncertainty (Leitao and Karnouskos 2015; Marik and McFarlane 2005). 

The main way of achieving consensus has been through optimisation functions, either through a global objective function (e.g.Fung and Chen 2005), often pursued through a mediator agent (e.g. A. Pan et al. 2009), a Pareto optimal solution search between conflicting objectives (e.g. Wong and Fang 2010), or ensuring that individual objectives do not conflict, by fine-tuning them a priori (e.g. Lim, Tan, and Leung 2013). A recent survey of these approaches by Xu, Mak, Proselkov, et al. (2024) argues that the field has stagnated due to low industrial adoption, which is partly due to the difficulty in creating tailored solutions, as well as interoperability and system integration issues, leading to a lack of uptake from multiple supply chain partners. Lack of trust in automation, a lack of explainability, and decision traceability are other common reasons. 

In addition to rule-based MAS, Reinforcement Learning (RL) emerged as a more flexible learning-based alternative, where agents learn to optimise their actions through trial and error in a dynamic environment. MultiAgent Reinforcement Learning (MARL) extended this to cooperative or competitive multi-agent settings (Yuan et al. 2023). While MARL achieved theoretical and empirical success in many controlled domains, such as games, it is mostly suitable for dynamic optimisation with commonly shared objectives (reward functions) across supply chain echelons (Rolf et al. 2023). RL has been found difficult to apply in consensus-seeking contexts, due to: (i) non-stationarity of models arising from concurrent policy updates, and (ii) extreme data inefficiency and cold-start challenges (Liu et al. 2022; Yang et al. 2023). 

With the advent of LLMs, new levels of automation and decision support in SCM are expected (Jackson et al. 2024). Researchers have already demonstrated promising applications such as server placement optimisation at Microsoft using LLMs (Li et al. 2023) and supply 

6 V. JANNELLI ET AL. 

chain simulation creation from natural text using LLMs (Jackson, Jesus Saenz, and Ivanov 2024). 

A recent development within the field of LLMs are agentic LLMs (Xu, Mak, Proselkov, et al. 2024). These LLM agents are able to interact with other agents or humans, use additional tools such as optimisation algorithms, query documents and databases, or search the web. Unlike previous generations of agents that required rigorously defined inputs and outputs, LLM agents are capable of learning from unstructured data, enabling them to adapt to complex environments in real-time (Li et al. 2023). Their ability to process natural language inputs and contextualise information allows them to act more autonomously (Xu, Mak, Proselkov, et al. 2024). 

There is also potential for hybrid agent approaches, integrating LLM agents with Rule-based MAS, RL and MARL. Examples of such hybrid architectures include the OptiGuide framework (Li et al. 2023), where LLMs interpret human queries into optimisation code, which is then processed by traditional solvers. The results are translated subsequently into natural language by LLMs, enabling intuitive interaction with complex supply chain optimisation tasks. Godfrey, Hunt, and Soorati (2025) present MARLIN, a framework that integrates LLMs with Multi-Agent Proximal Policy Optimisation (MAPPO). In this setup, LLMs facilitate natural language negotiations among agents, enhancing coordination and training efficiency in multi-robot navigation tasks. These, however, are just emerging and have not yet been trialled in supply chain settings. Following the OptiGuide framework, LLMs would serve as an interpretive layer that translates natural language queries into optimisation code for traditional solvers, then converts outputs back into human-understandable insights. Simultaneously, drawing from MARLIN, the system would employ dual action-generation methods: traditional reinforcement learning (MAPPO) and natural language inter-agent negotiation via LLMs, dynamically switching between them based on which is likely to produce superior plans (Godfrey, Hunt, and Soorati 2025). The architecture uses in-context learning to teach the LLM domain knowledge through prompts rather than costly fine-tuning, while the optimisation code is written in functional forms that map efficiently to human questions (Li et al. 2023). 

We posit that LLMs are particularly attractive for SMEs looking to use automation in their supply chains. By integrating tools for specialised tasks, memory and/or Retrieval Augmented Generation in LLM-based supply chain workflows, research is equipped with new strategies to orchestrate and optimise complex business decisions (BCG 2024). 

Advancements in LLM agents for supply chain management have not yet found their way into industrial applications (Xu, Mak, and Brintrup 2021). Furthermore, many systems for multi-agent communication developed in computer science research or supply chain management research are formulated as use cases, which are very context-specific and difficult to adapt to tailored situations. If communication systems were more easyto-configure, this itself may promote greater cooperation between members of real-world supply chains (Xu, Mak, and Brintrup 2021). 

Marty and Ruel (2024) find that companies tend to interact prevalently with companies both immediately upstream and immediately downstream in a supply chain, and are focussed on improving sourcing, procurement, and supplier management processes. This reflects the partial observability of supply chains. Our goal is to investigate how LLMs can be used as a viable technology to improve collaboration in an end-to-end supply chain setting, as they offer a fast, natural language-based interface that is suited for industrial control (Song et al. 2023). 

Legacy supply-chain integration hinges on structured data exchange over Enterprise Resource Planning (ERP) platforms, demanding significant investment and tightly coupled interfaces (Frohlich and Westbrook 2001). Small- and medium-sized enterprises (SMEs) often lack the digital maturity to participate, impeding end-to-end visibility (Senna et al. 2023). SMEs also struggle to invest in rigid ERP systems and justify investment without longterm commitments from buyers. Collaborative planning frameworks show that consensus on forecasts and replenishment parameters mitigates undesirable phenomena such as the bullwhip effect and shortage gaming (Dejonckheere et al. 2004; Kuncova 2002; Lee, Padmanabhan, and Whang 1997a). Yet, ERP-centric approaches rarely extend beyond tier-1 partners, and consensus formation still demands manual data wrangling, meetings, and costly middleware (Wieder et al. 2006). ERP solutions do not readily scale across the supply chain, whilst consensus seeking requires engagement between companies partnering in supply chains. Hence, there is a need for autonomous solutions, which can handle consensusbuilding for end-to-end supply chains. LLM agents offer a unique opportunity to achieve consensus faster and in a way that reflects the global objectives of the supply chain (Kudiabor 2024). This paper attempts to understand how LLM agents can help build consensus in the supply chain. 

Our framework introduces LLM-based agents as adaptive mediators to facilitate real-time negotiation among decentralised supply chain actors. Unlike traditional integration platforms that require rigid linkages, an LLM agent can interpret partners’ natural-language 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 7 

inputs, making it a more flexible and context-aware solution that bridges diverse systems without heavy integration overhead. 

#### **_2.4. Available benchmarking environments in supply chain management research_** 

While there is a large corpus of existing research on AI applications for supply chain automation involving distributed agent architectures (Liu et al. 2022; Xu, Mak, and Brintrup 2021; Yuan et al. 2023), the supply chain research community does not have a supply chainspecific LLM benchmarking environment with communication frameworks that reflect partial observability and a scalable sequential supply chain. 

The field of computer science has advanced in developing environments to study behaviours of cooperative and competitive LLM agents (Mukobi et al. 2023; Zhao et al. 2024). By drawing inspiration from LLM decisionmaking frameworks from computer science research, as well as rule-based multi-agent supply chain environments, we design a set of consensus-seeking LLM frameworks specific to supply chains that reflect partial observability and collaboration between neighbours. 

Examples of these environments include: Zhao et al. (2024), which simulates competitive agent dynamics in a marketplace setting. Though this environment illustrates an industry example with partial observability, it lacks the sequential supply chain structure with partial observability that would be useful to study inventory management challenges. Mukobi et al. (2023) focus on multi-agent collaboration in a general-sum setting, which would also be interesting for LLM-based supply chain interactions. However, a similar supply chain environment would have to include sequential dependencies, partial observability, as well as real-time decision-making and consensusseeking. There is very limited research on LLM-based decision-making in a supply chain setting, but Quan and Liu (2024) introduces LLMs to manage inventory systems by leveraging zero-shot learning capabilities to minimise costs and stockouts. Despite testing chain-of-thought reasoning for LLM agents in various supply chain scenarios, this implementation relies on standalone agents 

that do not negotiate with their neighbours to make their decisions. 

Hence, another key contribution of this paper is a consensus-seeking LLM framework that is specific to supply chains and focuses on varying types of interactions between neighbouring agents. 

### **3. Problem setting** 

We place our multi-agent consensus-seeking framework in an environment that simulates an end-to-end supply chain inventory management setting, based on the work by Liu et al. (2022). This environment has features desirable for our purposes, such as partial observability, multiple tiers of dependency, as well as a general sum setting. The focus of our implementation on the end-to-end supply chain allows us to explore and tackle longstanding challenges in SCM research, while allowing for a simple implementation of our communication framework that can be extended to a supply chain network with multiple parallel layers of echelons. 

Figure 2 shows a sequential supply chain that reflects the exchanges in order requests (‘demand’), material products (‘replenishment’), and additional insights (‘information’) that flow between the communicating agents. 

#### **_3.1. Global costs in the end-to-End supply chain_** 

The local costs of each agent are given by the sum of different cost components: inventory costs, variable ordering cost, fixed ordering cost and backlog costs (defined as the unmet demand from an agent’s downstream neighbour). The global costs of the end-to-end supply chain are given by the local costs of each agent, summed across all agents (Liu et al. 2022). Formally, 



Local objectives often drive agents to act in self-interested ways, focussing on minimising their own cost without 



<!-- Start of picture text -->
information<br>Oo demand ) demand ) demand ee0e<br>eee S|<br>GEEED o ——> |? "| —— dart<br>ieplenishment replenishment replenishment<br>Manufacturer Distributor Retailer Customer<br><!-- End of picture text -->

**Figure 2.** Problem setting: sequential supply chain with partial observability. 

8 V. JANNELLI ET AL. 

regard for the impact on other nodes of the supply chain. For example, a distributor may choose to overorder in anticipation of future demand, thereby increasing variability and inventory costs for upstream suppliers. This misalignment between selfish (local) and cooperative (global) objectives is well-documented, particularly in relation to coordination failures in decentralised systems (Lee, Padmanabhan, and Whang 1997b). Actors in a decentralised supply chain may not share local data, leading to coordination challenges in managing global demand and supply. Addressing this issue traditionally involves incentive alignment or centralised planning, which can be impractical at scale. 

#### **_3.2. The bullwhip effect in supply chains_** 

The bullwhip effect is a phenomenon of the increase in variability of orders as one moves upstream in a supply chain (Disney et al. 2005). It has been advocated that sharing information between neighbouring agents in the supply chain can mitigate the bullwhip effect (X. Wang and Disney 2016). To compute the bullwhip effect in our setting, we use a formula derived by Liu et al. (2022) and based on Fransoo and Wouters (2000), which considers the coefficient of variation of demand generated by a given echelon, i.e. the ratio between the standard deviation of demand and the mean of demand, as follows: 



where _σ(_ · _)_ is the standard deviation and _μ(_ · _)_ the mean of demand. Demand is given by the list of historical actions of agent _i_ , and _t_ is the current time interval. Therefore, a coefficient of variation of demand below 1 indicates that the bullwhip effect is negligible. 

To compute the aggregate bullwhip effect, we use Fransoo and Wouters (2000), who conclude that the aggregate bullwhip effect for a (strictly) end-to-end supply chain can be achieved by multiplying all of the coefficients of variation (i.e. the bullwhip effects) of each individual echelon. 

In order to mitigate the bullwhip effect, we implement a traditional approach to order an optimal quantity based on SCM restocking policies. The metric used to optimise for the bullwhip effect is based on the Economic Order Quantity (EOQ) measure for each agent (Kuncova 2002), motivated by a similar approach which was adopted by Jackson, Jesus Saenz, and Ivanov (2024). However, the challenge that arises is that the EOQ picked by each individual agent may not be optimal for the entire supply chain. Kuncova (2002) and Dejonckheere et al. (2004) underline that agreements on order amounts 

between neighbouring agents help mitigate the bullwhip effect. According to this insight, our implementation of consensus-seeking frameworks-based negotiation should aid in mitigating the bullwhip effect. We thus deliberately adapt the original EOQ formula as a benchmark for agents to start off with _selfish_ order quantities, and make it suitable for our environment (Liu et al. 2022), as follows: 



where Demand is derived from the mean of historical demand data from the downstream agent, Ordering Cost is the per-unit cost of ordering, and Holding Cost is the per-unit cost of holding inventory. Given that our EOQ formula is dependent on the demand coming from the neighbouring downstream agents as an input, it is not a constant variable and does not exacerbate the bullwhip effect (Disney and Towill 2003). Therefore, we use EOQ as a ‘tool’ for the agents to maximise their selfish incentives, while the consensus-seeking incentives will be dictated by the LLM prompt itself. Thus, the LLM allows agents to reach an agreement in the presence of conflicting objectives. Rather than insisting on their own EOQ, our agents will mutually agree on orders to give to each other. This creates a loop. Once consensus is reached, the agreed-upon order, in turn, dictates demand information, which then propagates through the chain. This determines the change in agents’ EOQ, meaning that they will streamline demand and supply through a consensusseeking mechanism. Hence, the EOQ in our case only acts as a starting point – to display the selfish nature of our agents – until consensus is reached. 

### **4. Methodology** 

An overview of our LLM-based consensus-seeking frameworks is shown in Figure 3. In this context, consensus-making refers to the property of the framework orchestrating and steering the agents towards agreements; whether they ultimately find consensus depends on the prompt-specific interaction between them. In particular, our frameworks include: standalone LLM agents (Figure 3(a)), information sharing between neighbouring agents (Figure 3(b)), standalone LLM agents with tools (Figure 3(c)), information sharing between neighbouring agents with tools (Figure 3(d)), and negotiation between neighbouring agents with tools (Figure 3(e)). The underlying inventory management setting for our frameworks is based on Liu et al. (2022), which we extend by integrating LLM agents. 

We utilise existing memory structures to aid the agents in storing previous local observations about the status 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 9 



<!-- Start of picture text -->
Information Agent n+1<br>Final decision stage f od<br>Agent° n+1 Agentn° Agent n+1 Agent n Agent° n+1 Agent° n<br>eS fe) )<br>Ibs 6 Se eB eS e&<br>Action" n+1 1 Obsvy),‘Action n Nei a, Neil /<br>Action nt nction n Action n+1 ‘Action n<br>(a) Standalone LLM Agents: Each (b) LLM Agents with information (c) Standalone LLM agents with<br>agent makes independent decisions sharing: Agents exchange observa- tool usage: Each agent uses an<br>based solely on its own local obser- tions with immediate neighbours be- external tool (c.g., forecasting) to<br>vations. fore making decisions. enhance its standalone decision-<br>making.<br>Information Agentn GO F—<br>— Information Agentn+1<br>Information Agentn+1 ©<br>Negotiation stage<br>Final decision stage ;<br>Agreement stage Environment<br>Agentfe) n+1 AgentQ n Agent° n+1 AgentQ n f- Tool<br>eS 6 eS & f<br>Action n+1Neil Ob:y/‘Action n ‘Action n+1Nei ay‘Action n =a) LLM Agent<br>& ces) [1 communication<br>(d) LLM Agents with information (e) LLM Agents with negotiation — Legend<br>sharing and tool usage: Agents com- around tool output: Agents ne-<br>bine tool outputs with neighbour in- gotiate with neighbours over tool-<br>formation to make better-informed based proposals to reach a mutual<br>decisions. agreement before acting.<br><!-- End of picture text -->

**Figure 3.** LLM-based consensus-seeking frameworks for the sequential supply chain. (a) Standalone LLM Agents: _Eachagentmakesindependent decisions based solely on its own local observations_ , (b) LLM Agents with information sharing: _Agents exchange observations with immediate neighbours before making decisions_ , (c) Standalone LLM agents with tool usage: _Each agent uses an external tool (e.g. forecasting) to enhance its standalone decision-making_ , (d) LLM Agents with information sharing and tool usage: _Agents combine tool outputs with neighbour information to make better-informed decisions_ , (e) LLM Agents with negotiation around tool output: _Agents negotiate with neighbours over tool-based proposals to reach a mutual agreement before acting_ and (f) Legend. 

10 V. JANNELLI ET AL. 

of the environment, namely the specific agent’s inventory state, backlog state and previous orders. Beyond this structure, we rely exclusively on context to create the memory of the agents, also as we progress to information-sharing and negotiation frameworks for decision-making. 

To support decision-making, agents are equipped with simple quantitative tools: for the cost minimisation experiments, we employ a demand forecasting tool based on linear regression, which uses the last 30 observed periods to predict the next order amount. For experiments analysing the bullwhip effect, agents are utilised with a tool for calculating the EOQ. While not globally optimal, this tool represents individual incentives and serves as a starting point for negotiation. The tools generate quantitative proposals that the LLM agents may either adopt directly or adjust through information sharing and negotiation. 

In the standalone framework, agents only have access to their local observations (e.g. current inventory, backlog, last order amount). In the information sharing and negotiation frameworks, agents share this local information and/or their tool outputs (e.g. calculated EOQ) exclusively with their immediate upstream and downstream neighbours. This design choice reflects the partial observability that characterises real-world supply chains. 

#### **_4.1. LLM-based decision-Making without communication_** 

#### **_4.1.1. Standalone LLM agents_** 

We first study standalone LLM agents. Figure 4 illustrates the decision-making process for standalone LLM agents 

that we employ for a 3-tier sequential supply chain. After perceiving the environment, the agent’s state is stored in memory, and later contextualised in a prompt for the agent, containing the following elements: 

- General description of the sequential supply chain problem setting. 

- Description of objective function: the function for cost minimisation, or the function for the coefficient of variation. 

- Agent’s observation of the environment, containing: inventory, backlog, last order, incoming/transfer orders, demand from downstream neighbour. 

- Memory: information on the previous ten observations on inventory, backlog and order amounts. 

- Final question on order amount (action) and instruction on formatting LLM output. 

The resulting output by the LLM is interpreted as the order amount or action that is executed upon the environment. The input information provided to the standalone LLM agent reflects the local view that it has of the supply chain. A detailed breakdown of the prompt components can be found in Appendix 2. 

#### **_4.1.2. Standalone LLM agents with tool usage_** 

We introduce the tool on top of the decision made by the standalone LLM agents. The output of the tool is embedded in the prompt with the necessary contextualisation, to allow the agent to benefit from more information, as illustrated in the example in Appendix 2. The wrench symbol indicates where the tool is invoked in the decision-making process. 



<!-- Start of picture text -->
\ Envi LLM<br>a, sie(eee<br>] < SSrh<br>&{| | eo= foe) Envi (] <EFLLM ee<br>; = i LLM<br>Be<br><!-- End of picture text -->

**Figure 4.** Flowchart of a standalone LLM-based decision-making process. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 11 



<!-- Start of picture text -->
ete<br>«an<br>t| —<br>[ AgentAgent o04 Environment“rercontion. [°] memoryState4 Lgim ———memConvo0 decisionFinal<br>I Communication<br>‘Agent Er <>st 9 ‘agents 0-1 —!Ce -<br>& 9 11+] perceptionEnvironment memorytate decision?Lim solo = memjonvo1 ‘Convomem 1 decisionFinal<br>—) _ Communication ¢<br>I |<br>agent+4 Environment | J Siete “im solo Ge agents 1-2 —<br>perception memory2 decision mem‘onvo2<br>I Environment |,}aState imeci> OO_— =ae ——memConvo2 decisionFinal<br>Bo perception] memoryoo) decision = ee Some Final<br>decision<br>mom<br><!-- End of picture text -->

**Figure 5.** Detailed modular framework for a 3-tier supply chain with communication between neighbours. 



<!-- Start of picture text -->
agentAgent-to-info g Agents’ . final Agent<br>fering decision summarises<br><!-- End of picture text -->

**Figure 6.** Communication framework based on information sharing between neighbouring agents (LangGraph). 

#### **_4.2. Communicating LLMAgents_** 

To enable collaboration between agents, we develop a cognitive-inspired modular framework that integrates with perception, memory and execution, as illustrated in Figure 12 in Appendix 1 and inspired by the cooperative embodied agents paper by Zhang et al. (2023). At each step of the simulation, after perceiving the environment, each agent can save to and receive information from memory. It then makes a tentative decision based on its standalone viewpoint of the supply chain, and then communicates with a neighbouring agent to seek consensus. Finally, the agent makes a decision based on all these previous steps and executes it in the environment. Figure 5 details this information flow. 

There are different orchestration frameworks for multi-agent workflows, such as LangGraph (LangChain AI 2024) or AutoGen (Wu et al. 2023). We opted for LangGraph as it offers a versatile implementation and can be easily extended to tool-calling with LangChain. To reflect the partial observability described in Marty and Ruel (2024), our framework limits communication to neighbouring agents. In particular, in our use case, each agent initiates communication with its immediate upstream neighbour. A single interaction, therefore, always involves two neighbouring agents. 

#### **_4.2.1. Communication between agents_** 

There are two types of consensus-seeking frameworks between neighbouring agents, corresponding to the stage shaped as a hexagon in Figure 5: (i) information sharing and (ii) negotiation, which both reflect the partial observability of sequential supply chains by allowing agents to only interact with their immediate neighbours. Firstly, information sharing enriches each agent with information from its upstream neighbour. We choose to implement interactions with the upstream neighbour instead of the downstream neighbour because of the need to mitigate demand amplification, which usually affects upstream echelons. 

Figure 6 shows the consensus-seeking framework based on information sharing between neighbouring agents without additional steps taken for negotiation. As we embed the outputs of our tool-calling functions directly in the prompt, the figure applies to both information sharing with tools and without tools. 

We extend this framework to include negotiation as shown in Figure 7. Negotiation allows the agents to interact and agree on an order amount by taking the output of each tool and using these values as upper and lower bounds for a negotiation range. The agents have a predefined number of iterations to negotiate before naming their definitive order amount in a final agreement stage. 

12 V. JANNELLI ET AL. 



<!-- Start of picture text -->
Agent ate,<br>responds Sey<br>,, 5 in 4 ny,Mery<br>Coan) ee AWi Agents’ final Agent Cent)<br>Sraring 7 decision summarises<br>Sm ‘<br>nagMnfoeHgs Agent<br>al initiates<br><!-- End of picture text -->

**Figure 7.** Framework for negotiation between neighbouring agents (LangGraph); for our experiments, state[num_iter] is equal to 3, meaning there are 3 loops in the interactions between neighbouring agents. 

For the experiments assessing the global costs of the supply chain, the tool output for each agent constitutes the cost-minimising amount at each echelon in the sequential supply chain. 

The consensus-seeking framework implemented with LangGraph (LangChain AI 2024) for each pair of communicating neighbours is illustrated in Figure 7. Our implementation dynamically creates nodes and edges for a sequential supply chain of any length, without requiring the user to manually define each communication exchange. 

experiments, even as we compare the performance with different language models. 

Moreover, limiting our prompts to zero-shot learning allows us to minimise the amount of changes we make between different metrics. In particular, the optimisation functions change between metrics, as well as the formulation of the question, but the formulation of the observation and description of the sequential supply chain setting remains largely unchanged, as illustrated in Appendix 2. 

#### **_4.3.2. Prompt engineering between different supply chain metrics_** 

#### **_4.3. Prompt engineering for different consensus-Seeking frameworks and different metrics_** 

In this section, we discuss the properties of the prompts that we used for different models and metrics. We underline that we undertook manual prompt engineering for our experiments. As a result, the prompts are not fully optimised and largely the same between different foundation models. We will discuss in Section 8 on limitations how model-specific optimisation can be achieved in future research. 

#### **_4.3.1. Zero-shot prompting_** 

Our benchmarking environment utilises pre-trained LLMs to tackle inventory management challenges. We use zero-shot learning to query our models, thereby requesting that the agents apply their pre-trained knowledge directly to our inventory management tasks, interpreting information that is supply chain-related based on their insights acquired from large knowledge corpora (Kojima et al. 2022). 

We exclude in-context learning from our prompts, because its performance is unstable, and subject to many factors (Dong et al. 2022). Additionally, we have opted to keep prompts as similar as possible throughout our 

Our approach is problem-agnostic, as moving from one metric to the other only requires adapting the input prompts that get passed into the consensus-seeking frameworks, without changing the implementation of the frameworks themselves and how the messages are passed between agents. In particular, the information sharing and negotiation frameworks apply to cost minimisation and bullwhip effect mitigation alike. 

#### **_4.3.3. Prompt engineering to introduce tool usage_** 

As can be observed in Appendix 2, the prompts used in our inventory management setting comprise different components. As a result, when we want an agent to make a decision based on a tool output, we have to underline the importance of this tool in the context of the prompt. The optimal prompts to achieve these results were determined experimentally and discussed in the experimental setup. 

#### **_4.4. Tools used by agents_** 

Our approach utilises two tools that can be implemented by the agents based on the metric they are optimising. 

To minimise each agent’s costs, we use a demand forecasting tool that uses linear regression to estimate the next order amount, thereby keeping orders similar to past 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 13 

**Table 1.** Summary of ablation study of LLM-based decision making with different metrics and foundation models. 

|Exp. No.|Metric|Tool|Model|Framework|
|---|---|---|---|---|
|1|Global Cost|–|–|Restocking Policy (S,s) = (100,60)|
|2|Global Cost|Demand Prediction|–|Demand Forecasting Tool|
|3|Global Cost|Demand Prediction|Gemini 1.5 Flash|Standalone LLM|
|4|Global Cost|Demand Prediction|Gemini 1.5 Flash|LLM with Info Sharing|
|5|Global Cost|Demand Prediction|Gemini 1.5 Flash|Standalone LLM+Tool|
|6|Global Cost|Demand Prediction|Gemini 1.5 Flash|Info Sharing+Tool|
|7|Global Cost|Demand Prediction|Gemini 1.5 Flash|Negotiation+Tool|
|8|Global Cost|Demand Prediction|Gemini 1.5 Pro|Standalone LLM|
|9|Global Cost|Demand Prediction|Gemini 1.5 Pro|LLM with Info Sharing|
|10|Global Cost|Demand Prediction|Gemini 1.5 Pro|Standalone LLM+Tool|
|11|Global Cost|Demand Prediction|Gemini 1.5 Pro|Info Sharing+Tool|
|12|Global Cost|Demand Prediction|Gemini 1.5 Pro|LLM Negotiation+Tool|
|13|Global Bullwhip|–|–|Restocking Policy (S,s) = (100,60)|
|14|<br>Global Bullwhip|EOQ|–|<br>EOQ tool|
|15|Global Bullwhip|–|–|Chen et al. (2000)|
|16|Global Bullwhip|EOQ|Gemini 1.5 Flash|Standalone LLM|
|17|Global Bullwhip|EOQ|Gemini 1.5 Flash|LLM with Info Sharing|
|18|Global Bullwhip|EOQ|Gemini 1.5 Flash|Standalone LLM+Tool|
|19|Global Bullwhip|EOQ|Gemini 1.5 Flash|Info Sharing+Tool|
|20|Global Bullwhip|EOQ|Gemini 1.5 Flash|Negotiation+Tool|
|21|Global Bullwhip|EOQ|Gemini 1.5 Pro|Standalone LLM|
|22|Global Bullwhip|EOQ|Gemini 1.5 Pro|LLM with Info Sharing|
|23|Global Bullwhip|EOQ|Gemini 1.5 Pro|<br>Standalone LLM+Tool|
|24|Global Bullwhip|EOQ|Gemini 1.5 Pro|Info Sharing+Tool|
|25|Global Bullwhip|EOQ|Gemini 1.5 Pro|Negotiation+Tool|



orders and avoiding spikes in demand. The tool utilises a look-back window of 30 periods to train this model on recent demand data. At the beginning of the simulation, when the dataset is insufficient, the agent defaults to the most recently observed order quantity. 

In the bullwhip effect experiments, we use an EOQbased tool as a way to showcase selfish incentives of the agents, as discussed in Section 3. This is because we are interested in studying how information sharing and negotiation frameworks can reduce the bullwhip effect in the presence of these selfish incentives. 

### **5. Experimental setup** 

We run a total of 24 experiments to compare the consensus-seeking frameworks on the two different optimisation metrics and on LLM models of different size. Experiments are detailed in Table 1. The temperature – a parameter for LLMs to control for the randomness of outputs – is set close to zero, making the outputs of our runs near-deterministic. 

Experiments are conducted with an underlying customer demand that is based on the Merton Jump Diffusion Model, as described in Liu et al. (2022). We consider an end-to-end supply chain with 3 agents, and a lead time of 2 steps, to reflect the presence of the bullwhip effect as highlighted by Chen et al. (2000) and using the measure from Fransoo and Wouters (2000) to assess whether the bullwhip effect can be mitigated with our approach. Each experiment runs for a total of 200 steps. These parameters can be set via the underlying agentic environment 

from the research by Liu et al. (2022), which we augment by building LLM agents on top of it. 

As we seek to demonstrate improvements in performance (reduction in costs or bullwhip effect) based solely on the sophistication of the consensus-seeking frameworks, the effectiveness of the tool used, and the size of the foundation model powering the agent, we define fixed parameters across all our agents and experiments. These parameters are listed in Table 2 in Appendix 6. Consequently, agents only exhibit differing behaviour based on their position in the sequential supply chain. The value 100 is set as the upper bound for orders across all agents and all experiments. This allows increasingly upstream agents to amplify demand with respect to their downstream agent, starting from the consumer demand, which fluctuates between 0 and 20 units per order. The consumer demand used for our experiments can be found in Appendix 6. 

For the LLM agents, we enforce this upper threshold with built-in code constraints and explicit prompt engineering to guarantee that the order amount selected by each agent never exceeds 100. This allows us to compare our communication frameworks and baselines in settings that reflect similar possible order quantities. 

#### **_5.1. Agent policies used as baselines for LLM agents_** 

To compare the performance of our LLM-based consensus-seeking frameworks, we establish different baselines based on existing approaches for restocking. 

14 V. JANNELLI ET AL. 

One of the most widely used approaches is the (S,s) policy (Shang 2011; Visentin et al. 2021), which we use as our weak baseline. The (S, s) restocking policy reorders to a maximum level (S) when inventory falls below a certain threshold (s). In particular, we use values of (S = 100, s = 60), which reduce the global costs. The (S,s) policy parameters S = 100 and s = 60 were chosen based on the experimental constraints and optimisation. S = 100 aligns with the maximum order limit imposed across all agents (as stated in the experimental setup), while s = 60 provides a reasonable reorder threshold that balances inventory costs with stockout risk. These parameters were experimentally validated to minimise global costs within the simulation environment’s constraints. This decision-making, based on threshold values, can lead to variability amplification up the supply chain, thereby exacerbating the bullwhip effect (Chen et al. 2000) and increasing global supply chain costs. 

On the other hand, the strong baseline for our experiments is given by the decisions of a tool-based agent: contrary to LLM agents, which embed the tool output into the LLM prompt, these baseline tool agents use the tool output directly as their final decision. When optimising for costs, we obtained a strong baseline by running the tool agent with the output of the linear regression demand forecasting tool, implemented with the previous 30 observations. Similarly, for the bullwhip effect experiments, we use the EOQ tool to represent selfish incentives, using the previous 30 observations to calculate the average demand from the downstream agent. Moreover, for the bullwhip effect experiments, we benchmark against the study of Chen et al. (2000), which uses centralised demand to calculate the order amount for agents across the entire supply chain; we use this approach as it is a well-known bullwhip effect minimisation benchmark. 

#### **_5.2. LLMs used_** 

We conduct all of our experiments with two different foundation models from the Gemini family, developed by Google DeepMind, namely Gemini Flash and Gemini Pro, to illustrate the performance of our communication frameworks with models of different parameter counts (Gemini Team 2024). Better performance by larger models has been empirically validated by numerous studies (Kaplan et al. 2020). Gemini Flash represents a smaller model optimised for fast processing at the expense of accuracy, while Gemini Pro is larger and built for more complex, nuanced tasks. 

For both models, we run our experiments with a temperature of 0.1. On one hand, this yields an almostdeterministic set of outputs; on the other hand, the small degree of randomness allows for agents to repeat queries 

which returned an incorrectly-formatted output from the LLM, and to deliver results in the correct format in subsequent iterations (Ouyang et al. 2024). 

### **6. Results & discussion** 

To illustrate the performance of our consensus-seeking communication frameworks, we conduct experiments focussing on two different metrics: global cost minimisation and global bullwhip effect minimisation. 

#### **_6.1. Global cost minimisation_** 

Figure 8 visualises the global costs achieved by each consensus-seeking framework for two foundation models, and compares the results to the two baselines achieved by the baseline agent implementations as defined in Subsection 5.1. 

#### **_6.1.1. Cost performance of gemini flash_** 

For Gemini Flash, we observe a gradual cost reduction as we introduce the demand forecasting tools, and as we introduce increasing levels of sophistication in the consensus-seeking framework. In particular, we observe: 

- 63.5% cost reduction when adding tools to the standalone agents, 

- 92.8% cost reduction when comparing information sharing agents to standalone agents, 

- 67.9% cost reduction when adding tools to information sharing agents, 

- 50.7% cost reduction when adding negotiation to agents implementing information sharing with tool usage. 

This is in line with our expectation that communication between neighbouring agents and additional information about the status of the supply chain can aid individual agents in making more informed decisions. The only framework that underperforms the weak baseline is the standalone LLM agent without tool usage. 

#### **_6.1.2. Cost performance of gemini pro_** 

For Gemini Pro, we observe that the trend in cost reduction is similar to that obtained with Gemini Flash, but there is no consistent performance improvement achieved when using a larger model, even if both models are from the same developer organisation (Google DeepMind). Existing research confirms that promptbased interactions are still brittle (Zamfirescu-Pereira et al. 2023) and that ‘performance can vary nonmonotonically with model size’ (Wei, Tay, et al. 2022). 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 

15 



<!-- Start of picture text -->
—— Strong Baseline: Heuristic Agent w/ Tool (16,645) @™ Gemini 1.5 Flash<br>— Weak Baseline: Heuristic Agent w/ (S = 100, s = 60) Policy (159,094) Gemini 1.5 Pro<br>221,532<br>172,624<br>116,508<br>80,822<br>25,947<br>15,967 16,645 13,431 15,393<br>Standalone LLM Agent Info Sharing Standalone LLM w/Tool LLM w/ Info Sharing & Tool Negotiation<br><!-- End of picture text -->

**Figure 8.** Global cumulative costs achieved by different consensus-seeking frameworks. 

L. Wang et al. (2024) also find that different prompts had variable effects across various models. Our case study optimises the prompts for the smaller model, Gemini Flash, using manual optimisation techniques. For the Gemini Pro, the prompts are identical except for the way the tool output is introduced, as can be observed in Figure 14 in Appendix 3. Prior to these prompt modifications, the performance achieved with a larger model was more unstable. Table 1 in Appendix 4 shows the performance of our consensus-seeking frameworks relative to global costs, considering a Merton Jump Diffusion (spike) demand and a prediction tool for demand forecasting. 

Finally, it is also interesting to note that, for both models used, the performance of the negotiation framework beats the hard baseline involving a tool-based restocking policy by the agent. This shows that LLM agent interactions with high degrees of orchestration can outperform even mathematical tool-driven performances. 

**_6.1.3. Effect of metric complexity on tool performance_** 

The experiments relative to the cost minimisation objective illustrate that, when a tool is highly suited for a given metric, such as our linear regression tool to predict future demand and minimise costs, the highest performance is achieved by those frameworks that give strong weight to the tool itself, without necessarily needing an elaborate consensus-seeking framework between agents. Despite this, additional orchestration on top of the tool implementation, such as with the negotiation framework, can improve tool-driven results even further. This is in line 

with existing SC research that highlights how sophisticated tools in the form of algorithms can yield optimisation of resource allocation and cost reductions (Bu 2024). 

However, demand forecasting to minimise costs is a relatively simple challenge in inventory management, defined by a formula which considers a simple sum of different costs. This is simple enough for a foundation model, which is a probabilistic machine, not a tool suited for complex calculations. For more complex metrics, such as the coefficient of variation to calculate the bullwhip effect, communication between neighbouring agents becomes the key factor in improving performance, as we illustrate in the following results. 

#### **_6.2. Global bullwhip effect minimisation_** 

We conducted a series of experiments on the bullwhip effect to study demand amplification in a setting with partial observability and LLM agents operating under selfish incentives. An in-depth overview of our experiments can be found in Table 2, illustrating the coefficients of variation that we obtained from different experiments. To benchmark the performance of our LLM-based frameworks, we designed three experimental baselines: (1) an (S,s) restocking policy, as used in previous experiments; (2) an EOQ-based setup, where agents optimise replenishment based on their individually calculated EOQ values (derived in Section 3.2), which vary as a function of local demand. Notably, under stochastic demand, the EOQ policy does not amplify the bullwhip effect (Disney and Towill 2003); and (3) a baseline grounded in the 

16 V. JANNELLI ET AL. 

**Table 2.** Global bullwhip effect for sequential SC - measured by the coefficient of variation. 

|Setup: 3 echelons, max orders = <br>|100, lead_time = 2, tool = EOQ, prev<br>|obs = 30<br>|
|---|---|---|
|Soft Baseline Agent with (S,s) = (100, 60) policy<sup>a</sup>|65.77168 (costs = 159’094)|65.77168 (costs = 159’094)|
|Hard Baseline Agent with EOQ tool<sup>a</sup>|0.79 (costs = 212’223)|0.79 (costs = 212’223)|
|Baseline Agent using Chen et al. (2000) approach –<br>Bullwhip Effect minim.|0.937 (costs = 39’276)|0.937 (costs = 39’276)|
|LLM Agent Architecture|model = gemini-1.5-pro|model = gemini-1.5-flash|
|Solo LLM Agent|4.54223 (costs = 265’092)|0.36899 (costs = 70’453)|
|Solo LLM Agent with Tool (EOQ)|24.47413 (costs = 236’053)|1.31137 (costs = 223’771)|
|LLM Agents with Information Sharing|0.76227 (costs = 56764)|0.51735 (costs = 53’706)|
|LLM Agents with Information Sharing & Tool (EOQ)|0.76486 (costs = 223’530)|0.75923 (costs = 221’888)|
|Agent negotiation with Tool (EOQ)<br>(num_iter = 3)<sup>b</sup>|0.25827 (costs = 114’980)|0.50744 (costs = 213’657)|



Note:<sup>a</sup> This agent is not powered by a foundation model. bnum_iter = 3 means that each agent pair has 3 back-and-forth passes before moving to the agreement stage. 



<!-- Start of picture text -->
Conversation “Let's have a conversation about how much to order to minimize the<br>agentStarted by downstesmintro: “) overallupper and bullwhiplower effect.bound forLet's the use negotiation the EOQs shared by each agent as<br>First My E0Q is 7; Tamwillingto negotiatehow much to order in order to}<br>{ily E0QLoopis of8; negotiationT'am willing stage:to negotiate how much to order in order fo}-——-----—--------vn| eee bathe ae 9 i<br>{minimize the bullwhip effect. >>———momen nnnnnnnnnnnnnnnnnn nnn onened<br>Srrosenrancarannoreaseseaseasascasascasaascseascaroscaseasascascrecsaceriaoos f iy demand is only 1, and | have plenty of inventory. How about |<br>pebegond Loop of negotiation stage:O_O| we settle on an order of 1? |<br>{That sounds like a good plan. An order of 1 would help minimize the |<br>| bullwhip effect. | peceeennenennnnnennennnnnnnsnnnnnnennnnnnnnnnnnnennennsnnnnennennenneennnnnny<br>“Thirdlcoocfrecctistonstacet(‘i«=i‘=‘S:*;*=‘té‘;=‘:;*é*‘:;*é«s i<br>Third Loop of negotiation stage: LN accent e cece cnnneeecececneeneeceeneneeeenennenenel<br>fOK! j<br>ba________ ED<br>H{System: “What is your final answer?” System: “What is your final answer?” Faltage: Agreementtakes place |Hi<br>|gent +1: 1 Agent n: 1 attersecbareostaionthe negotiation ||<br>|| AgentGeminipro1 Agent 0 Gemini-pro (eo)<br><!-- End of picture text -->

**Figure 9.** Negotiation for bullwhip effect – detailed example. 

analytical model of Chen et al. (2000), which quantifies the bullwhip effect under a moving average forecast and order-up-to policy. In particular, this model allows for demand centralisation by sharing the retailer’s demand with all upstream agents. 

Table 2 illustrates the results of the consensus-seeking frameworks, compared to these benchmark experiments. 

Notably, the best bullwhip effect performance was achieved with the negotiation framework. Compared to the information sharing with tool framework, negotiation yielded a 66.2% bullwhip effect reduction when using Gemini Pro, and a 33.2% reduction when using Gemini Flash. This is the result of neighbouring agents agreeing on order amounts, thereby reducing demand amplification (Kuncova 2002). This further indicates that our consensus-seeking frameworks allow overcoming selfish objectives in favour of global supply chain objectives. 

#### **_6.2.1. Detailed example of negotiation for bullwhip effect mitigation_** 

In Figures 9–11, we illustrate an example of our negotiation framework between neighbouring agents, and showcase how it allows agents to reach a compromise on their order amounts. Figures 9 and 10 illustrate first the interactions between agents 0 and 1, followed by those between 1 and 2, simulating how information would propagate upstream in a partial observability context. Agents are able to propose trade-offs and agree on them. Each agent in our framework calculates its EOQ independently for each bilateral negotiation based on local demand patterns from its specific downstream neighbour. When Agent 1 negotiates with Agent 0, it uses demand data from Agent 0. When Agent 1 subsequently negotiates with Agent 2, it uses different demand data (Agent 1’s own orders to Agent 2), resulting in a different EOQ calculation. This does not mean agents are 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 17 



<!-- Start of picture text -->
“Let's have a conversation about how much to order to minimize the<br>Conversation intro: overall bullwhip effect. Let's use the EOQs shared by each agent as<br>agentStated by ownsteam “) upper and lower bound for the negotiation<br>First Loop of negotiation. stage: My| peesE0Q  thois  buh8; Tamwillingeato negotiate9 how much to order in order to}i<br>iminimize the bullwhip effect. | pepceneecnnnncennneennennnnnnnnnnnennnnnennnnnnnnnnnnnnennnneennneennnnenennny<br>Brennan sceesooaao==i=="5 | Binge OUP EOQS are 8 and 17, how about we settle on an order of |<br>Second Loop of negotiation stage: pe HaPDE se. i<br>HERES URC IONSISIS DOCS OR PINS eae CUI IOgLCi sae<br>Third Loop of negotiation stage: | OK! |<br>| OK! i<br>T system: “What is your final answer?” ‘System: ‘What is your final answer?” Final Agreement<br>i Stage: takes place}<br>| Agent n+1: 12 Agent n: 12 atertereoetaion |<br>\Car) | AgentGemini-pro 2 AgentGemini-pro1 \ |<br><!-- End of picture text -->

**Figure 10.** Negotiation for bullwhip effect – detailed example cont. 



<!-- Start of picture text -->
por | porn<br>|2iH?;<br>JHS | OO ———— |<br>' Agent2 } + Agent? } ' AgentO }<br>| Gemini-pro } H Gemini-pro } { Gemini-pro }<br>| £0Q:17 } ' £0Q:8 } | E0Q1 |<br>i Negotiation between agents 0-1: H<br>i Result: Agreement on ordering 1 unit each. i<br>i \ Negotiation Stage<br>i Negotiation between agents 1-2: H<br>H Result: Agreement on ordering 12 units each i<br>| Agent2 Final Order: 12 Agent 1 Final Order: 8 Agent 1 Final Order:t Final Decision Stage<br><!-- End of picture text -->

**Figure 11.** Negotiation for bullwhip effect – detailed example cont. 

discarding the previous negotiation – rather, each pairwise negotiation addresses different supply relationships in the chain. The final decision stage reconciles these negotiations. Appendix 5 illustrates some further examples from our experiments of agents’ agreements and occasional disagreements in negotiation. 

From these examples, we observe that the behaviour of LLM agents is strongly influenced by previously shared information, which guides their proposals for order quantities. Moreover, both the prompt design and the structure of the interaction, i.e. number of conversational swaps before agreement (three in our experiments), establishment of a ‘final agreement’ stage, play a significant role in shaping agent responses. This structure 

facilites coordinated decision-making and contributes to attenuating the bullwhip effect. 

Our experiments reveal that if LLM Agents are not explicitly directed on which strategy should be adopted for selecting ordering amounts, they usually settle on a compromise. However they occasionally use other strategies, such as going for one extreme of the negotiation interval or disagreeing altogether. This is in line with research on LLM-based MAS and their consensusseeking strategies (Dorri, Kanhere, and Jurdak 2018). To use the same terminology from these authors, our LLM Agents in negotiation tend to be either ‘stubborn’ or ‘suggestible’. Stubborn agents tend to dominate the final decision, whereas suggestible agents tend to behave 

18 V. JANNELLI ET AL. 

more collaboratively. In the case of our specific supply chain setting, the downstream agent initiates the conversation and explains the nature of the negotiation, and subsequently tends to assume a more stubborn attitude. The upstream agent responds and, in most cases, tends to assume a more suggestible attitude. This particular behaviour is appealing for a use case that aims to minimise demand amplification, as the insights from downstream prove to benefit this optimisation, but may have to be modified in other use cases. 

#### **_6.2.2. Framework comparison for bullwhip effect performance_** 

Table 2 illustrates the performance of our consensusseeking frameworks specifically against the study by Chen et al. (2000), which utilises centralised demand from the retailer to define demand across all agents. Our results show that, starting from frameworks where neighbouring agents interact, the LLM-based agents consistently outperform the benchmark. This is a significant result, because it means that our information sharing between agents (and negotiation) with decentralised demand is able to outperform the results of (Campbell, Hoane Jr., and Hsu 2002) – which has a centralised demand setup – despite our agents’ EOQ-based selfish incentives. In the study by Campbell, Hoane Jr., and Hsu (2002) demand is not amplified by upstream communication, whereas our study looks at mitigating amplification of demand through negotiation to reach agreements in order quantities. 

Our results clearly show that introducing more sophisticated consensus-seeking frameworks (information sharing and negotiation) gradually reduces the coefficient of variation. In particular, the lowest (best) bullwhip effect measures were achieved with the negotiation framework. This result experimentally backs the research suggesting that information sharing and agreeing on order amounts mitigate the bullwhip effect (Dejonckheere et al. 2004; X. Wang and Disney 2016). 

Throughout our experiments, we observe that endto-end supply chains can operate much better compared to traditional restocking policies when adopting LLMbased settings that include coordinated communication and tool usage. Additionally, when LLM agents are handled within a negotiation framework, their behaviour converges to best practices in SC literature to lessen the bullwhip effect. 

### **7. Managerial implications and implementation** 

Reaching consensus on operational decisions across an end-to-end supply chain is time-consuming and often not possible due to the amount of manual effort involved. 

In the literature, automation of consensus-seeking in lowlevel supply chain decisions using agent-based systems has been proposed for a long time, but not adopted by industry. Previously proposed AI agents in SCM were challenging to implement for companies due to the skill set needed for their development, the complexity of finding training data and the need for all supply chain agents in a given ecosystem to match their input/output formats. In particular, SMEs cannot afford the large data science teams required to implement complex AI approaches and manage large databases. Recent advances in pre-trained LLMs offer an opportunity: the possibility to work with a fast, natural-language-based interface that has the ability to perform industrial control tasks without the need to set up interoperability across multiple supply chain information systems (Song et al. 2023). Additionally, recent advances in the applications of LLM agents for consensus-seeking prompted us to explore whether they can be used in a supply chain setting (Tessler et al. 2024). 

In this paper, we developed and provided a suite of LLM-based consensus-seeking frameworks for supply chains and tested them with a demand function simulating a spike in demand (see Appendix 17). Our experiments yield interesting managerial implications, which we report across four categories: performance, scalability, implementation, and reliability. 

#### **_7.1. Reliability and explainability_** 

Our experiments showed that neither foundation model size nor tool reliability is a guarantee to achieve high performance for global cost mitigation and global bullwhip effect mitigation. Larger models do not yet yield significant performance gains over smaller models in this setting, and each model that is plugged into our consensus-seeking frameworks requires a high engagement from a supply chain specialist or engineer to optimise the prompts and yield satisfying results. This implies that we are still far from autonomous LLM-based supply chains and decisions made to optimise real-world supply chain metrics still require a human-in-the-loop approach. In our framework, constraints are handled in two ways to prevent infeasible results: first, through explicit instructions in the prompt engineering, and second, through hard-coded backstops in the environment, such as the upper bound of 100 for order quantities. This hybrid approach ensures that even if the LLM hallucinates, the resulting action remains within feasible operational bounds. In real life, it is necessary to have someone accountable, which necessitates a human to sign off on actions and intervene if necessary. 

In addition to this, using tools is not a guarantee for success. In particular, success in tool-driven frameworks 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 19 

depends on the tool and the prompting skills of an engineer. The LLM thereby acts similarly to a human agent that needs inputs on how to work with a tool – but with the added benefit of being a scalable automated solution. 

In our experiments relating to the bullwhip effect, the tool serves as a means to simulate companies’ selfish incentives, which would arise in real-world settings, and as a means to showcase the effect of negotiation in curbing this selfish behaviour. 

#### **_7.2. Performance_** 

Experiments relating to global cost minimisation highlight that tool usage is only effective when the function behind the tool is mathematically able to tackle a certain challenge. For example, in the case of the linear regression model used for demand forecasting, this tool keeps the demand in line with previous order amounts, preventing the demand spikes that cause costs to soar. 

Another significant advantage of our consensusseeking framework is that it is problem-agnostic, as the interactions between agents offer a fixed structure, but the exact messages exchanged by agents can easily be modified by using LLM prompts. Moreover, our structure is scalable to a sequential supply chain of arbitrary length. The architecture of our agent interactions can be tailored to a specific type of framework (information sharing vs negotiation, etc.) by the user. The structure and sequence of negotiations – starting with neighbouring agents on a one-on-one basis and subsequently making decisions across the entire sequence of agents – reflect how company-to-company interactions take place in real-world supply chains (Zhu, Han, and Liu 2024). 

It is interesting to point out that the results of our experiments outperform the hard baselines (tool-based) in many cases, even if the prompts used in our experiments have not been optimised to fit a specific LLM. This result is encouraging from a managerial perspective because it shows that good results can also be achieved when prompts are engineered by a supply chain expert rather than a prompt engineering specialist. 

#### **_7.3. Scalability_** 

Many real-world supply chain consensus problems require settings where multiple agents and multiple objectives coexist. Therefore, scalability of the communication framework is an important aspect. For the sequential supply chain we modelled, where each of the _n_ agents communicates only with its immediate neighbour, the complexity is linear, or _O(n)_ , whereas the complexity in a supply chain network with _m_ layers and _n_ echelons would be _O(m_ · _n)_ . Preserving efficiency could be 

achieved in future work by using quick and safe algorithms to identify which agents have a high impact on a specific outcome and subsequently limiting communication to these high-impact agents, as proposed by Schöpf, Foster, and Brintrup (2024). Our three-tier sequential supply chain represents a foundational test case for the consensus-seeking frameworks. While real-world supply chains exhibit greater complexity – including network structures, multi-sourcing, and other features – this controlled environment allows us to rigorously validate the core mechanisms of LLM-based consensus-seeking. The demonstrated improvements in system-level outcomes (bullwhip effect reduction) in this simplified setting provide evidence for the potential of these approaches. 

#### **_7.4. Implementation_** 

Our results demonstrate not only the feasibility of deploying these agents in a supply chain setting but also the underlying implementation and structure of the agent negotiation and decision-making process with a modular approach involving tools and increased levels of sophistication. These frameworks are a necessary precursor to the eventual scalability and optimisation that will yield a concrete impact in the real world. Additionally, we underline that our open-source framework can be built upon by other researchers. As foundation models improve, as tool integration becomes more sophisticated, and as prompt engineering becomes more automated, the performance of such systems will accelerate as well. 

One of the key advantages of using LLM agents for consensus-seeking is that they do not require interoperability across the supply chain information ecosystem for applications to work effectively. In particular, some companies will move towards LLM-based decisionmaking before others, but this will not prevent them from engaging with companies that still make decisions with extant restocking approaches or hybrid solutions. Since LLM agents receive inputs in natural language and output results in a human-understandable format, they can coexist with other technologies used by other agents, be it human or AI, in the supply chain. This feature is appealing for real-world use cases and could be investigated further with our communication framework by exploring scenarios in which agents use different tools or cognitive models to make decisions about inventory management challenges. 

Moreover, as the trend towards expanding context windows (i.e.maximum input lengths) in LLMs continues, foundation models will process increasingly extensive sequences of data (Gartenberg 2024), allowing them to analyse complex supply chain scenarios. With the advent of Industry 5.0, the significance of General AI is 

20 V. JANNELLI ET AL. 

set to deepen even further (Ivanov 2023). As AI usage in supply chains becomes more widespread, integrating LLM-based consensus-seeking frameworks in existing digital twin structures will allow company-tailored information to guide the agent’s decision-making process (Jackson et al. 2024), for which real-time access to information in the whole company is essential. 

### **8. Limitations** 

As a technology with limited benchmarking environments in the supply chain management community, LLM agents are still at a very early stage in reaching their potential. 

At a fundamental level, LLMs are affected by limitations such as _hallucinations_ , which is the flaw of generating confident yet incorrect outputs (Ji et al. 2023). In the context of supply chain decision-making, hallucinations could take the form of fabricated inventory states, incorrect downstream demand signals, or unrealistic delivery lead times. This is particularly dangerous in multi-agent systems where upstream agents depend on downstream inputs to inform ordering decisions. However, tool-based agentic flows, which we use in our experiments, can constrain LLM outputs with deterministic outputs. Another fundamental downside of LLM agents is that LLMs inherit biases present in their training data (Bender et al. 2021). In supply chains, which have proved unstable in recent times, this can promote suboptimal heuristics based on historical patterns rather than current needs. A countermeasure that could be explored in future work is domain-specific fine-tuning on curated supply chain datasets to reduce the influence of irrelevant patterns from general-purpose pretraining. At the present time, there is a lack of available supply chain training data to enable training a foundation model for supply chains. This fundamental data scarcity limits the potential for developing specialised models that could better understand supply chain-specific dynamics and terminology. We also point to the risk of data breaches as a fundamental limitation of LLMs, especially concerning data-sensitive supply chain operations. If agents are externally hosted (e.g. via cloud APIs), there is a risk of data exfiltration through prompt leakage or unauthorised logging (Carlini et al. 2021). Moreover, in decentralised multi-agent settings, adversarial agents could inject misleading prompts to destabilise consensus. 

A general weakness of foundation models, independently of the rules and frameworks that surround them, is that their performance when switching between different foundation models is still unstable. This is in line with computer science literature on the topic, for example 

L. Wang et al. (2024). This limitation of our environment could easily be explored in more detail and mitigated by using frameworks for algorithmically optimising LLM prompts, such as Khattab et al. (2023). Optimising such a framework would also prove useful for making communication more intuitive to use for nonspecialists, as the efforts of prompt engineering would be reduced. A limitation of our study is the exclusive use of Gemini models, which enabled controlled comparisons across agentic framework components. However, other LLMs (e.g. GPT-4, Claude, LLaMA) may differ in reasoning and instruction-following, potentially affecting agent behaviour. Future work should assess the generalisability and robustness of our frameworks across a broader range of LLMs. 

We expect the learning curve for our communication framework to be quite steep for a non-specialist to implement and use, especially when it comes to adapting the communication framework to other supply chain challenges. 

Another intuitive enhancement to our framework would be the use of long-term conversation memory for SC agents, which would enable them to use information from downstream interactions as a way to enrich the decisions they make with upstream agents in immediately subsequent agent interactions. In the current implementation, agents’ conversation memory is limited to the current step in the simulation, while agents’ observation memory relates to the previous ten simulation steps. By allowing for long-term conversation memory, agents could use accumulated information to enrich their consensus-seeking process. A further addition to our work would be achieved by enhancing the structure of the interactions between neighbouring supply chain agents, for example, by integrating Socratic Iterative Prompt Engineering (SIPE), as proposed by Boussioux et al. (2024). Incorporating SIPE into our consensus-seeking framework could address the observed variation in consensus quality by refining agent decision logic through structured, iterative dialogue. For instance, instead of relying solely on single-pass negotiation prompts, agents could iteratively critique and improve each other’s reasoning steps, mirroring SIPE’s dialogic refinement process, and potentially achieve better alignment with global supply chain objectives. 

In terms of scalability, our implementation for a sequential supply chain has a complexity of _O(n)_ whereas fully connected communication would be _O(n_<sup>2</sup> _)_ . Our approach reflects the partial observability of supply chains by allowing agents to communicate only with their neighbours. Information sharing and negotiation frameworks are set up dynamically and can be adapted to have an arbitrary number of exchanges between agents. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 21 

Expansions of the environment to a supply chain network are theoretically possible according to Liu et al. (2022), but communication between neighbours would be more challenging. 

Relatedly, an interesting question here is the challenge of shared objectives over networks of supply chain agents crossing organisational boundaries. In particular, when self-interested organisations automate decisions using agentic workflows, will they incorporate selfish goals or network-wide consensus-seeking? Although our work has been a technical exploration that has shown the applicability of agentic technology in both selfish and cooperative scenarios, qualitative research exploring how organisations would be willing to craft consensusseeking agents remains an open and urgent question. The emerging field of ‘persuasive agents’ (Dragoni, Donadello, and Eccher 2020), and ‘mediator agent design’ (Westermann, Savelka, and Benyekhlef 2023) are worth exploring in supply chain settings, and this could be achieved by building on top of our architecture for negotiation between LLM agents. 

Finally, as mentioned in the previous section, decisions based on our communication frameworks still require a human-in-the-loop, as the outputs still are not entirely reliable and explainable. Algorithms can therefore not be held accountable for real-world use cases. 

### **9. Conclusions and future work** 

Automatically optimising supply chain operational decisions using AI has been widely explored from the point of view of a single firm. However, as CASN theory posits, major benefits can be obtained when the supply chain network is orchestrated as a whole if consensus-seeking is the goal of the orchestration process. However, the orchestration of consensus is complicated as incentives to reach consensus manually remain low due to high costs, especially among self-interested parties in a supply chain. 

Researchers have proposed agent-based automation in the past, but issues such as scalability, inflexibility, and the skillset required to develop, maintain and adopt these across end-to-end supply chains prevented widespread adoption. 

In this paper, we asserted that LLM agents offer an intuitive, scalable and interoperable solution to automated consensus-seeking across a range of supply chain challenges, and presented a series of frameworks for LLM-based consensus-seeking in the end-to-end supply chain, which were tested in a bullwhip effect setting. 

This research provides a foundational framework for LLM-based communication in supply chains, establishing proof-of-concept for autonomous multi-agent consensus-seeking in inventory management. While 

tested in a sequential three-tier setting, the modular design enables extension to more complex network structures as a key direction for future research. Whilst our framework exhibits how consensus-seeking can be automated and used to overcome unwanted emergent effects in the supply chain, we underline that establishing such an automated system is preconditioned upon collaborative will and trust. Similar to the adoption of other technical advances in managing complex relationship structures (Flynn, Huo, and Zhao 2010; Vanpoucke, Vereecke, and Muylle 2017), agentic AI also presents research opportunities for exploring relationship dynamics conducive to its practical use. We leave these important dimensions to qualitative researchers for further research. 

The key contributions of this study include the design and implementation of LLM-based consensus-seeking frameworks; a case study involving experiments across multiple foundation models, as well as an open-source implementation that the SCM community can build upon. Our consensus-seeking framework reflects important characteristics of supply chains, such as partial observability and real-time decision-making enhanced by insights from neighbouring agents (Ivanov 2024a). The negotiation framework built is scalable to a sequential supply chain of arbitrary size, which is generated automatically by having the users input the desired number of agents. Additionally, our experiments on the bullwhip effect highlight that including both selfish objectives (indicated by EOQ-based order policy in the presence of a non-constant demand) and global objectives in the agent’s prompts yields results where the global objectives prevail, in a context with information sharing and negotiation. This is interesting as it proves that LLM negotiation in a setting with decentralised demand reflects the best practices to reduce the bullwhip effect (Dejonckheere et al. 2004; Kuncova 2002). 

Additionally, compared to the costs of creating an integrated SCM ERP system of automatic negotiation, prompt engineering offers a much more intuitive approach that can be tailored to specific metrics by using the scalable architecture proposed by our approach. This is also advantageous for SMEs, which typically have fewer technical employees than large firms, as they can not afford to set up data science departments such as those in larger corporations. Future work can extend our frameworks with automatic prompt optimisation tools, such as Khattab et al. (2023). 

Further enhancements, such as self-reflection by the LLM agents (Renze and Guven 2024), could help achieve higher levels of autonomy. A further step to improve the explainability of our approach is to enhance the prompts with chain-of-thought reasoning, i.e. a series 

22 V. JANNELLI ET AL. 

of intermediate reasoning steps to help LLMs perform complex tasks (Wei, Wang, et al. 2022). Additionally, our implementation can be expanded beyond sequential supply chains to investigate how to preserve efficiency in complex supply chain networks. 

Further use cases need to be implemented on top of our framework to validate whether LLM agent behaviour can reflect the theoretical foundations of supply chain resilience and adaptation to disruptions (Ivanov 2024b). Additionally, future work can investigate LLM-based negotiation tactics that focus on multi-objective scenarios involving trade-offs between different metrics in the supply chain (e.g. costs vs emissions trade-offs), as well as explore uncooperative or malicious behaviour by agents to devise methods to discourage undesirable behaviour. 

In conclusion, this research proposes an extensive and versatile starting point for SC-specific LLM-based communication frameworks, thereby advancing towards autonomous multi-agent decision-making in inventory management settings. Our LLM-based frameworks lay the foundation for future research to investigate various use cases, including the convergence of LLM behaviour in the supply chain under realistic conditions. Furthermore, we establish an open-source baseline for the SCM community, encouraging further enhancements of the communication frameworks, such as extensions to supply chain networks with multiple dimensions, as well as multi-objective scenarios. 

### **Disclosure statement** 

No potential conflict of interest was reported by the author(s). 

### **Funding** 

This work was supported by Alan Turing Institute, Engineering and Physical Sciences Research Council [EP/W019868/1]. 

### **Notes on contributors** 

**_Valeria Jannelli_** is an alumna of ETH Zurich and a visiting MSc thesis student at the University of Cambridge’s Supply Chain AI Lab (SCAIL). Jannelli completed her Bachelor’s degree in Computer Science at ETH Zurich and her Master’s degree in Management, Technology, and Economics (MTEC) at the same institu- 



tion. She previously served as Project Manager and member of the Executive Board at ETH juniors, one of Europe’s leading student-run consultancies. At ETH juniors, she led IT projects involving natural language processing and recommendation systems. She currently works as a GenAI Engineer at a Swiss financial institution. Her research at the University 

of Cambridge focussed on the application of large language models (LLMs) and artificial intelligence to supply chain management. Her recent work introduces novel consensus-seeking frameworks using LLM-powered autonomous agents for supply chain coordination, addressing challenges in inventory management and inter-company decision-making. 

**_Stefan Schoepf_** is a PhD Candidate at the University of Cambridge, based in the Supply Chain AI Lab (SCAIL). His research focuses on machine unlearning, specifically developing methods to remove sensitive or corrupted data from already trained machine learning models. During his doctoral studies, Stefan undertook research internships at Google DeepMind and IBM Research. Prior to his PhD, he worked as an Associate at the Boston Consulting Group and completed an MSc in Management, Technology, and Economics at ETH Zürich. 

**_Matthias Bickel_** is a doctoral researcher at the Chair of Production and Operations Management at ETH Zurich, where he researches the application of AI for Knowledge Management in industrial operations. Specifically, he focuses on methods to capture the tacit knowledge of experienced operators. Prior to his doctoral studies, he gained research experience at Fraunhofer IPA and the Karlsruhe Institute of Technology (KIT), where he also obtained his M.Sc. in Industrial Engineering. 

**_Torbjørn Netland_** is Full Professor of Production and Operations Management at ETH Zurich. Switzerland. Prof. Netland is the President of the European Operations Management Association (EurOMA), a Fellow of the European Academy of Industrial Management, a Full Member of IFIP WG5.7, and a Member of the World Economic Forum’s Global Future Councils. His research spans industrial engineering and operations management, focussing on how manufacturers can achieve and sustain operational excellence. He is a co-author of the textbook Introduction to Manufacturing: An Industrial Engineering and Management Perspective (Routledge, 2022). 

**_Alexandra Brintrup_** Alexandra Brintrup is Full Professor of Digital Manufacturing at the Department of Engineering, University of Cambridge, where she leads the Supply Chain AI Lab. Prof. Brintrup is fellow of the Alan Turing Institute, Darwin College and IFAC. Her research is at the intersection of Complex Systems, AI and Supply Chain Management, focussing on emergence, resilience, vulnerability and performance. Collaborative working for joint planning, joint product development, mutual exchange of information and integrated information systems, cross coordination on several levels in the companies on the network, long-term cooperation and fair sharing of risks and benefits. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 23 

### **Data availability statement** 

The data that support the findings of this study are available from the corresponding author, Alexandra Brintrup, upon reasonable request. 

### **ORCID** 

_Alexandra Brintrup_ http://orcid.org/0000-0002-4189-2434 

### **References** 

- BCG. 2024. “Maximizing Business Insights with Retrieval Augmented Generation.” Accessed October 20, 2024. https:// www.bcgplatinion.com/insights/enhancing-enterprise-ques tion-answering-retrieval-augmented-generation. 

- Behdani, Behzad, Zofia Lukszo, and Rajagopalan Srinivasan. 2019. “Agent-Oriented Simulation Framework for Handling Disruptions in Chemical Supply Chains.” _Computers & Chemical Engineering_ 122:306–325. https://doi.org/10.1016/ j.compchemeng.2018.09.027. 

- Bender, Emily M., Timnit Gebru, Angelina McMillan-Major, and Shmargaret Shmitchell. 2021. “On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?” In _Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency, FAccT ’21_ , 610–623. New York, NY: Association for Computing Machinery. https://doi.org/10.1145/3442188.3445922. 

- Bode, Christoph, Stephan M. Wagner, Kenneth J. Petersen, and Lisa M. Ellram. 2011. “Understanding Responses to Supply Chain Disruptions: Insights from Information Processing and Resource Dependence Perspectives.” _Academy of Management Journal_ 54 (4): 833–856. https://doi.org/10.5465/ amj.2011.64870145. 

- Boussioux, Leonard, Hongyu Chen, Ming Fan, and Apurva Jain. 2024. “Socratic Iterative Prompt Engineering: Enhancing Large Language Model Decision-Making and Reasoning in the Beer Game Supply Chain.” _Available at SSRN_ . 

- Brintrup, Alexandra, Anna Ledwoch, and Jose Barros. 2016. “Topological Robustness of the Global Automotive Industry.” _Logistics Research_ 9 (1): 1. https://doi.org/10.1007/s121 59-015-0128-1. 

- Brintrup, Alexandra, Duncan McFarlane, Damith Ranasinghe, Tomás Sánchez López, and Kenneth Owens. 2011. “Will Intelligent Assets Take Off? Toward Self-Serving Aircraft.” _IEEE Intelligent Systems_ 26 (03): 66–75. https://doi.org/10. 1109/MIS.2009.89. 

- Brintrup, Alexandra, Yu Wang, and Ashutosh Tiwari. 2015. “Supply Networks as Complex Systems: A Network-ScienceBased Characterization.” _IEEE Systems Journal_ 11 (4): 2170–2181. https://doi.org/10.1109/JSYST.2015.2425137. 

- Bu, Lingjie. 2024. “Logistic Resource Allocation Based on Multi-Agent Supply Chain Scheduling Using Meta-Heuristic Optimization Algorithms.” _Applied Artificial Intelligence_ 38 (1):2362516. https://doi.org/10.1080/08839514.2024.236 2516. 

- Campbell, Murray, A. Joseph Hoane Jr., and Feng-hsiung Hsu. 2002. “Deep Blue.” _Artificial Intelligence_ 134 (1-2): 57–83. https://doi.org/10.1016/S0004-3702(01)00129-1. 

- Carlini, Nicholas, Florian Tramèr, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, et al. 2021. “Extracting Training Data from Large Language Models.” In _30th USENIX Security Symposium (USENIX_ 

_Security 21), August_ , 2633–2650. USENIX Association. https://www.usenix.org/conference/usenixsecurity21/pres entation/carlini-extracting. 

- Carter, Craig R., Dale S. Rogers, and Thomas Y. Choi. 2015. “Toward the Theory of the Supply Chain.” _Journal of Supply Chain Management_ 51 (2): 89–97. https://doi.org/10.1111/ jscm.2015.51.issue-2. 

- Chen, Frank, Zvi Drezner, Jennifer K. Ryan, and David SimchiLevi. 2000. “Quantifying the Bullwhip Effect in a Simple Supply Chain: The Impact of Forecasting, Lead Times, and Information.” _Management Science_ 46 (3): 436–443. https://doi.org/10.1287/mnsc.46.3.436.12069. 

- Choi, Thomas Y., Kevin J. Dooley, and Manus Rungtusanatham. 2001. “Supply Networks and Complex Adaptive Systems: Control Versus Emergence.” _Journal of Operations Management_ 19 (3): 351–366. https://doi.org/10.1016/S02 72-6963(00)00068-1. 

- Choi, Thomas Y., Torbjørn H. Netland, Nada Sanders, ManMohan S. Sodhi, and Stephan M. Wagner. 2023. “Just-inTime for Supply Chains in Turbulent Times.” _Production and Operations Management_ 32 (7): 2331–2340. https://doi. org/10.1111/poms.13979. 

- Coehoorn, Robert M., and Nicholas R. Jennings. 2004. “Learning on Opponent’s Preferences to Make Effective Multi-Issue Negotiation Trade-Offs.” In _Proceedings of the 6th International Conference on Electronic Commerce_ , 59–68. Delft, The Netherlands: Association for Computing Machinery. 

- Dangelmaier, Wilhelm, Jens Heidenreich, and Ulrich Pape. 2005. “Supply Chain Management: A Multi-Agent System for Collaborative Production Planning.” In _2005 IEEE International Conference on e-Technology, e-Commerce and e- Service_ , 309–314. Hong Kong, China: IEEE. 

- Dash, Rupa, Mark McMurtrey, Carl Rebman, and Upendra K. Kar. 2019. “Application of Artificial Intelligence in Automation of Supply Chain Management.” _Journal of Strategic Innovation and Sustainability_ 14 (3): 43–53. 

- Dejonckheere, Jeroen, Stephen M. Disney, Marc R. Lambrecht, and Denis R. Towill. 2004. “The Impact of Information Enrichment on the Bullwhip Effect in Supply Chains: A Control Engineering Perspective.” _European Journal of Operational Research_ 153 (3): 727–750. https://doi.org/10.1016/S0 377-2217(02)00808-1. 

- Disney, Stephen M., Ingrid Farasyn, Marc Lambrecht, Denis R. Towill, and Wim Van de Velde. 2005. “Smooth Is Smart: Bullwhip, Inventory, Fill-Rates and the Golden Ratio.” _Tijdschrift Voor Economie En Management_ L (2): 167– 185. 

- Disney, Stephen M., and Denis R. Towill. 2003. “On the Bullwhip and Inventory Variance Produced by an Ordering Policy.” _Omega_ 31 (3): 157–167. https://doi.org/10.1016/S03050483(03)00028-8. 

- Dong, Qingxiu, Lei Li, Damai Dai, Ce Zheng, Jingyuan Ma, Rui Li, Heming Xia, et al. 2022. “A Survey on In-Context Learning.” _arXiv preprint arXiv:2301.00234_ . 

- Dorri, Ali, Salil S. Kanhere, and Raja Jurdak. 2018. “MultiAgent Systems: A Survey.” _IEEE Access_ 6:28573–28593. https://doi.org/10.1109/ACCESS.2018.2831228. 

- Dragoni, Mauro, Ivan Donadello, and Claudio Eccher. 2020. “Explainable AI Meets Persuasiveness: Translating Reasoning Results into Behavioral Change Advice.” _Artificial Intelligence in Medicine_ 105:101840. https://doi.org/10.1016/j.art med.2020.101840. 

24 V. JANNELLI ET AL. 

Fatima, Shaheen, Sarit Kraus, and Michael Wooldridge. 2015. _Principles of Automated Negotiation_ . Cambridge, UK: Cambridge University Press. 

- Flynn, Barbara B., Baofeng Huo, and Xiande Zhao. 2010. “The Impact of Supply Chain Integration on Performance: A Contingency and Configuration Approach.” _Journal of Operations Management_ 28 (1): 58–71. https://doi.org/10.1016/j. jom.2009.06.001. 

- Fransoo, Jan C., and Marc J. F. Wouters. 2000. “Measuring the Bullwhip Effect in the Supply Chain.” _Supply Chain Management: An International Journal_ 5 (2): 78–89. https://doi. org/10.1108/13598540010319993. 

- Frohlich, Markham T., and Roy Westbrook. 2001. “Arcs of Integration: An International Study of Supply Chain Strategies.” _Journal of Operations Management_ 19 (2): 185–200. https://doi.org/10.1016/S0272-6963(00)00055-3. 

- Fung, Richard Y. K., and Tsiushuang Chen. 2005. “A Multiagent Supply Chain Planning and Coordination Architecture.” _The International Journal of Advanced Manufacturing Technology_ 25 (7–8): 811–819. https://doi.org/10.1007/s00170-003-19 00-y. 

- Gartenberg, Chaim. 2024. “What Is a Long Context Window?” Accessed November 5th, 2024. https://blog.google/techno logy/ai/long-context-window-ai-models/. 

- Gemini Team. 2024. “Gemini Models.” Accessed November 6, 2024. https://ai.google.dev/gemini-api/docs/models/gem ini. 

- Giannoccaro, Ilaria, Anand Nair, and Thomas Choi. 2018. “The Impact of Control and Complexity on Supply Network Performance: An Empirically Informed Investigation Using NK Simulation Analysis.” _Decision Sciences_ 49 (4): 625–659. https://doi.org/10.1111/deci.2018.49.issue-4. 

- Godfrey, Toby, William Hunt, and Mohammad D. Soorati. 2025. “MARLIN: Multi-Agent Reinforcement Learning Guided by Language-Based Inter-Robot Negotiation.” https://arxiv.org/abs/2410.14383. 

- Grigonis, Hillary K. 2024. “Gemini 1.5 Pro Vs Gemini 1.5 Flash: What’s the Best Google AI?” Accessed November 6, 2024. https://www.pocket-lint.com/gemini-15-pro-vs-gemini15-flash/. 

- Hendler, James. 2007. “Where Are All the Intelligent Agents?” _IEEE Intelligent Systems_ 22 (3): 2–3. https://doi.org/10.1109/ MIS.2007.62. 

- Hendriksen, Christian. 2023. “Artificial Intelligence for Supply Chain Management: Disruptive Innovation or Innovative Disruption?” _Journal of Supply Chain Management_ 59 (3): 65–76. https://doi.org/10.1111/jscm.v59.3. 

- Ivanov, Dmitry. 2023. “The Industry 5.0 Framework: ViabilityBased Integration of the Resilience, Sustainability, and Human-Centricity Perspectives.” _International Journal of Production Research_ 61 (5): 1683–1695. https://doi.org/10. 1080/00207543.2022.2118892. 

- Ivanov, Dmitry. 2024a. “Conceptualisation of a 7-Element Digital Twin Framework in Supply Chain and Operations Management.” _International Journal of Production Research_ 62 (6): 2220–2232. https://doi.org/10.1080/00207543.2023.22 17291. 

- Ivanov, Dmitry. 2024b. “Two Views of Supply Chain Resilience.” _International Journal of Production Research_ 62 (11): 4031– 4045. https://doi.org/10.1080/00207543.2023.2253328. 

- Ivanov, Dmitry, and Alexandre Dolgui. 2020. “Viability of Intertwined Supply Networks: Extending the Supply 

Chain Resilience Angles towards Survivability. A Position Paper Motivated by COVID-19 Outbreak.” _International Journal of Production Research_ 58 (10): 2904–2915. https://doi.org/10.1080/00207543.2020.1750727. 

- Ivanov, Dmitry, Alexandre Dolgui, Jennifer V. Blackhurst, and Tsan-Ming Choi. 2023. “Toward Supply Chain Viability Theory: From Lessons Learned through COVID-19 Pandemic to Viable Ecosystems.” _International Journal of Production Research_ 61 (8): 2402–2415. https://doi.org/10.1080/002075 43.2023.2177049. 

- Jackson, Ilya, Dmitry Ivanov, Alexandre Dolgui, and Jafar Namdar. 2024. “Generative Artificial Intelligence in Supply Chain and Operations Management: A CapabilityBased Framework for Analysis and Implementation.” _International Journal of Production Research_ 62 (17): 1–26. https://doi.org/10.1080/00207543.2024.2309309. 

- Jackson, Ilya, Maria Jesus Saenz, and Dmitry Ivanov. 2024. “From Natural Language to Simulations: Applying AI to Automate Simulation Modelling of Logistics Systems.” _International Journal of Production Research_ 62 (4): 1434–1457. https://doi.org/10.1080/00207543.2023.2276811. 

- Jennings, Nicholas R., Peyman Faratin, Alessio R. Lomuscio, Simon Parsons, Carles Sierra, and Michael Wooldridge. 2001. “Automated Negotiation: Prospects, Methods and Challenges.” _International Journal of Group Decision and Negotiation_ 10 (2): 199–215. https://doi.org/10.1023/A:100 8746126376. 

- Ji, Ziwei, Nayeon Lee, Rita Frieske, Tiezheng Yu, Dan Su, Yan Xu, Etsuko Ishii, Ye Jin Bang, Andrea Madotto, and Pascale Fung. 2023. “Survey of Hallucination in Natural Language Generation.” _ACM Computing Surveys_ 55 (12): 1–38. https://doi.org/10.1145/3571730. 

- Jiao, Jianxin (Roger), Xiao You, and Arun Kumar. 2006. “An Agent-Based Framework for Collaborative Negotiation in the Global Manufacturing Supply Chain Network.” _Robotics and Computer-Integrated Manufacturing_ 22 (3): 239–255. https://doi.org/10.1016/j.rcim.2005.04.003. 

- Julka, Nirupam, I. Karimi, and Rajagopalan Srinivasan. 2002. “Agent-Based Supply Chain Management – 2: A Refinery Application.” _Computers & Chemical Engineering_ 26 (12): 1771–1781. https://doi.org/10.1016/S0098-1354(02)0015 

1-5. 

- Kaplan, Jared, Sam McCandlish, Tom Henighan, Tom B. Brown, Benjamin Chess, Rewon Child, Scott Gray, Alec Radford, Jeffrey Wu, and Dario Amodei. 2020. “Scaling Laws for Neural Language Models.” _https://arxiv.org/abs/2001.08 361_ . 

- Khattab, Omar, Arnav Singhvi, Paridhi Maheshwari, Zhiyuan Zhang, Keshav Santhanam, Sri Vardhamanan, Saiful Haq, et al. 2023. “DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines.” _arXiv preprint arXiv: 2310.03714_ . 

- Kojima, Takeshi, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. 2022. “Large Language Models are Zero-Shot Reasoners.” _Advances in Neural Information Processing Systems_ 35:22199–22213. 

- Kudiabor, Helena. 2024. “AI Tool Helps People with Opposing Views Find Common Ground.” _Nature_ . https://doi.org/10. 1038/d41586-024-03424-z. 

- Kuncova, Martina. 2002. “Optimization Methods and Bullwhip Effect.” _Quantitative Methods in Economics (Multiple Criteria Decision Making XI)_ , 144. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 25 

- LangChain AI. 2024. “LangGraph Documentation.” Accessed October 22, 2024. https://langchain-ai.github.io/langgraph/ reference/graphs/. 

- Lee, Hau L., V. Padmanabhan, and Seungjin Whang. 1997b. “The Bullwhip Effect in Supply Chains.” _MIT Sloan Management Review_ 38 (3): 1763–1893. 

- Lee, Hau L., Venkata Padmanabhan, and Seungjin Whang. 1997a. “Information Distortion in a Supply Chain: The Bullwhip Effect.” _Management Science_ 43 (4): 546–558. https://doi.org/10.1287/mnsc.43.4.546. 

- Leitao, Paulo, and Stamatis Karnouskos. 2015. “A Survey on Factors That Impact Industrial Agent Acceptance.” In _Industrial Agents_ , 401–429. Amsterdam, The Netherlands: Elsevier. 

- Li, Beibin, Konstantina Mellou, Bo Zhang, Jeevan Pathuri, and Ishai Menache. 2023. “Large Language Models for Supply Chain Optimization.” _arXiv preprint arXiv:2307.03875_ . 

- Lim, Ming K., Kim Tan, and Stephen C. H. Leung. 2013. “Using a Multi-Agent System to Optimise Resource Utilisation in Multi-Site Manufacturing Facilities.” _International Journal of Production Research_ 51 (9): 2620–2638. https://doi.org/10.1080/00207543.2012.737953. 

- Liu, Xiaotian, Ming Hu, Yijie Peng, and Yaodong Yang. 2022. “Multi-Agent Deep Reinforcement Learning for MultiEchelon Inventory Management.” Rotman School of Management Working Paper (4262186). 

- Long, Yunbo, Sebastian Kroeger, Michael F. Zaeh, and Alexandra Brintrup. 2025. “Leveraging Synthetic Data to Tackle Machine Learning Challenges in Supply Chains: Challenges, Methods, Applications, and Research Opportunities.” _International Journal of Production Research_ 1–22. https://doi.org/10.1080/00207543.2024.2447927. 

- López, Tomás Sánchez, Alexandra Brintrup, Marc-André Isenberg, and Jeanette Mansfeld. 2011. “Resource Management in the Internet of Things: Clustering, Synchronisation and Software Agents.” In _Architecting the Internet of Things_ , 159–193. London: Springer. 

- Löwhagen, Nils, Philippe Schwendener, and Torbjørn Netland. 2025. “Can a Troubleshooting AI Assistant Improve Task Performance in Industrial Contexts?” _International Journal of Production Research_ 1–22. https://doi.org/10.1080/0020 7543.2025.2527368. 

- Ma, Ke, Rudrajeet Pal, and Eva Gustafsson. 2019. “What Modelling Research on Supply Chain Collaboration Informs Us? Identifying Key Themes and Future Directions through a Literature Review.” _International Journal of Production Research_ 57 (7): 2203–2225. https://doi.org/10.1080/002075 43.2018.1535204. 

- Mak, Stephen, Liming Xu, Tim Pearce, Michael Ostroumov, and Alexandra Brintrup. 2023. “Fair Collaborative Vehicle Routing: A Deep Multi-Agent Reinforcement Learning Approach.” _Transportation Research Part C: Emerging Technologies_ 157:104376. https://doi.org/10.1016/j.trc.2023.10 4376. 

- Marik, Vladimir, and Duncan McFarlane. 2005. “Industrial Adoption of Agent-Based Technologies.” _IEEE Intelligent Systems_ 20 (1): 27–35. https://doi.org/10.1109/MIS.2005.11. 

- Marty, Justine, and Salomée Ruel. 2024. “Why Is “supply Chain Collaboration” Still a Hot Topic? A Review of Decades of Research and a Comprehensive Framework Proposal.” _International Journal of Production Economics_ 273:109259. https://doi.org/10.1016/j.ijpe.2024.109259. 

- Mukobi, Gabriel, Hannah Erlebach, Niklas Lauffer, Lewis Hammond, Alan Chan, and Jesse Clifton. 2023. “Welfare Diplomacy: Benchmarking Language Model Cooperation.” _arXiv preprint arXiv:2310.08901_ . 

- Nair, Anand, Ram Narasimhan, and Thomas Y. Choi. 2009. “Supply Networks as a Complex Adaptive System: Toward Simulation-Based Theory Building on Evolutionary Decision Making.” _Decision Sciences_ 40 (4): 783–815. https://doi. org/10.1111/deci.2009.40.issue-4. 

- Nair, Anand, and Felix Reed-Tsochas. 2019. “Revisiting the Complex Adaptive Systems Paradigm: Leading Perspectives for Researching Operations and Supply Chain Management Issues”. 

- Neef, Dale. 2001. _E-Procurement: From Strategy to Implementation_ . New Jersey: Upper Saddle River. 

- Olan, Femi, Emmanuel Ogiemwonyi Arakpogun, Uchitha Jayawickrama, Jana Suklan, and Shaofeng Liu. 2022. “Sustainable Supply Chain Finance and Supply Networks: The Role of Artificial Intelligence.” _IEEE Transactions on Engineering Management_ 71: 13296–13311. 

- Ouyang, Shuyin, Jie M. Zhang, Mark Harman, and Meng Wang. 2024. “An Empirical Study of the Non-determinism of ChatGPT in Code Generation.” _ACM Transactions on Software Engineering and Methodology_ 42: 1–28. 

- Pan, A., S. Y. S. Leung, K. L. Moon, and K. W. Yeung. 2009. “Optimal Reorder Decision-Making in the AgentBased Apparel Supply Chain.” _Expert Systems with Applications_ 36 (4): 8571–8581. https://doi.org/10.1016/j.eswa.2008. 10.081. 

- Pan, Shan L., Gary Pan, and Dorothy E. Leidner. 2012. “Crisis Response Information Networks.” _Journal of Association of Information Systems_ 13 (1): 32–56. https://doi.org/10.17705/ 1jais. 

- Park, Joon Sung, Joseph C. O’Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. 2023. “Generative Agents: Interactive Simulacra of Human Behavior.” _https://arxiv.org/abs/2304.03442_ . 

- Quan, Yinzhu, and Zefang Liu. 2024. “InvAgent: A Large Language Model Based Multi-agent System for Inventory Management in Supply Chains.” _arXiv Preprint ArXiv:2407.11 384_ . 

- Renze, Matthew, and Erhan Guven. 2024. “Self-Reflection in LLM Agents: Effects on Problem-Solving Performance.” _arXiv preprint arXiv:2405.06682_ . 

- Rolf, Benjamin, Ilya Jackson, Marcel Müller, Sebastian Lang, Tobias Reggelin, and Dmitry Ivanov. 2023. “A Review on Reinforcement Learning Algorithms and Applications in Supply Chain Management.” _International Journal of Production Research_ 61 (20): 7151–7179. https://doi.org/10. 1080/00207543.2022.2140221. 

- Samuel, Cherian, and Biswajit Mahanty. 2003. “Shortage Gaming and Supply Chain Performance.” _International Journal of Manufacturing Technology and Management_ 5 (5–6): 536–548. https://doi.org/10.1504/IJMTM.2003.003708. 

- Schöpf, Stefan, Jack Foster, and Alexandra Brintrup. 2024. “Identifying Contributors to Supply Chain Outcomes in a Multi-Echelon Setting: A Decentralised Approach.” _IEEE Transactions on Industrial Informatics_ 20 (12): 1–9. 

- Senna, Pedro P., Ana C. Barros, Jaime Bonnin Roca, and Américo Azevedo. 2023. “Development of a Digital Maturity Model for Industry 4.0 Based on the TechnologyOrganization-Environment Framework.” _Computers &_ 

26 V. JANNELLI ET AL. 

_Industrial Engineering_ 185:109645. https://doi.org/10.1016/ j.cie.2023.109645. 

Shang, Kevin H. 2011. “Simple Heuristics for Optimal Inventory Policies in Supply Chains.” In _Tutorials in Operations Research_ , 106–128. Charlotte, NC: INFORMS. 

- Skjoett-Larsen, Tage. 2000. “European Logistics Beyond 2000.” _International Journal of Physical Distribution & Logistics Management_ 30 (5): 377–387. https://doi.org/10.1108/0960 0030010336144. 

- Smyth, Conn, Denis Dennehy, Samuel Fosso Wamba, Murray Scott, and Antoine Harfouche. 2024. “Artificial Intelligence and Prescriptive Analytics for Supply Chain Resilience: A Systematic Literature Review and Research Agenda.” _International Journal of Production Research_ 62 (23): 8537–8561. https://doi.org/10.1080/00207543.2024.2341415. 

- Song, Lei, Chuheng Zhang, Li Zhao, and Jiang Bian. 2023. “PreTrained Large Language Models for Industrial Control.” _arXiv preprint arXiv:2308.03028_ . 

- Sterman, John D., and Gokhan Dogan. 2015. ““I’m Not Hoarding, I’m Just Stocking up before the Hoarders Get Here.”: Behavioral Causes of Phantom Ordering in Supply Chains.” _Journal of Operations Management_ 39:6–22. https://doi.org/10.1016/j.jom.2015.07.002. 

- Surana, Amit, Soundar Kumara∗, Mark Greaves, and Usha Nandini Raghavan. 2005. “Supply-Chain Networks: A Complex Adaptive Systems Perspective.” _International Journal of Production Research_ 43 (20): 4235–4265. https://doi.org/10. 1080/00207540500142274. 

- Tessler, Michael Henry, Michiel A. Bakker, Daniel Jarrett, Hannah Sheahan, Martin J. Chadwick, Raphael Koster, Georgina Evans, et al. 2024. “AI Can Help Humans Find Common Ground in Democratic Deliberation.” _Science (New York, N.Y.)_ 386 (6719): eadq2852. https://doi.org/10.1126/science. adq2852. 

- Vanpoucke, Evelyne, Ann Vereecke, and Steve Muylle. 2017. “Leveraging the Impact of Supply Chain Integration through Information Technology.” _International Journal of Operations & Production Management_ 37 (4): 510–530. https://doi. org/10.1108/IJOPM-07-2015-0441. 

- Villena, Verónica H., Thomas Y. Choi, and Elena Revilla. 2021. “Mitigating Mechanisms for the Dark Side of Collaborative Buyer–Supplier Relationships: A Mixed-Method Study.” _Journal of Supply Chain Management_ 57 (4): 86–116. https://doi.org/10.1111/jscm.v57.4. 

- Visentin, Andrea, Steven Prestwich, Roberto Rossi, and S. Armagan Tarim. 2021. “Computing Optimal (R, S, S) Policy Parameters by a Hybrid of Branch-and-Bound and Stochastic Dynamic Programming.” _European Journal of Operational Research_ 294 (1): 91–99. https://doi.org/10.1016/j.ejor. 2021.01.012. 

- Viswanadham, Nukala. 2002. “The Past, Present, and Future of Supply-Chain Automation.” _IEEE Robotics & Automation Magazine_ 9 (2): 48–56. https://doi.org/10.1109/MRA.2002. 1019490. 

- Wang, Gang, Angappa Gunasekaran, Eric W. T. Ngai, and Thanos Papadopoulos. 2016. “Big Data Analytics in Logistics and Supply Chain Management: Certain Investigations for Research and Applications.” _International Journal of Production Economics_ 176:98–110. https://doi.org/10.1016/j.ijp e.2016.03.014. 

- Wang, Li, Xi Chen, XiangWen Deng, Hao Wen, MingKe You, WeiZhi Liu, Qi Li, and Jian Li. 2024. “Prompt Engineering 

in Consistency and Reliability with the Evidence-Based Guideline for LLMs.” _npj Digital Medicine_ 7 (1): 41–50. https://doi.org/10.1038/s41746-024-01029-4. 

- Wang, Xun, and Stephen M. Disney. 2016. “The Bullwhip Effect: Progress, Trends and Directions.” _European Journal of Operational Research_ 250 (3): 691–701. https://doi.org/10. 1016/j.ejor.2015.07.022. 

- Wei, Jason, Yi Tay, Rishi Bommasani, Colin Raffel, Barret Zoph, Sebastian Borgeaud, Dani Yogatama, et al. 2022. “Emergent Abilities of Large Language Models.” _arXiv preprint arXiv:2206.07682_ . 

- Wei, Jason, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi, Quoc Le, and Denny Zhou. 2022. “Chainof-Thought Prompting Elicits Reasoning in Large Language Models.” _Advances in Neural Information Processing Systems_ 35:24824–24837. 

- Westermann, Hannes, Jaromir Savelka, and Karim Benyekhlef. 2023. “Llmediator: Gpt-4 Assisted Online Dispute Resolution.” _arXiv preprint arXiv:2307.16732_ . 

- Wieder, Bernhard, Peter Booth, Zoltan P. Matolcsy, and Maria-Luise Ossimitz. 2006. “The Impact of ERP Systems on Firm and Business Process Performance.” _Journal of Enterprise Information Management_ 19 (1): 13–29. https://doi.org/10.1108/17410390610636850. 

- Wong, T. N., and Fang Fang. 2010. “A Multi-Agent Protocol for Multilateral Negotiations in Supply Chain Management.” _International Journal of Production Research_ 48 (1): 271–299. https://doi.org/10.1080/00207540802425393. 

- Wooldridge, Michael, and Nicholas R. Jennings. 1995a. “Agent Theories, Architectures, and Languages: A Survey.” In _Intelligent Agents: ECAI-94 Workshop on Agent Theories, Architectures, and Languages Amsterdam, The Netherlands August 8–9, 1994 Proceedings 1_ , 1–39. Berlin, Germany: Springer. 

- Wooldridge, Michael, and Nicholas R. Jennings. 1995b. “Intelligent Agents: Theory and Practice.” _The Knowledge Engineering Review_ 10 (2): 115–152. https://doi.org/10.1017/S02698 88900008122. 

- Wooldridge, Michael, Nicholas R. Jennings, and David Kinny. 2000. “The Gaia Methodology for Agent-Oriented Analysis and Design.” _Autonomous Agents and Multi-Agent Systems_ 3:285–312. https://doi.org/10.1023/A:1010071910869. 

- Wu, Qingyun, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang. 2023. “AutoGen: Enabling Next-Gen LLM Applications Via Multi-Agent Conversation.” _arXiv preprint arXiv:2308.08155_ . 

- Wycisk, Christine, Bill McKelvey, and Michael Hülsmann. 2008. ““Smart Parts” Supply Networks as Complex Adaptive Systems: Analysis and Implications.” _International Journal of Physical Distribution & Logistics Management_ 38 (2): 108–125. https://doi.org/10.1108/096000308108 61198. 

- Xu, Liming, Stephen Mak, and Alexandra Brintrup. 2021. “Will Bots Take over the Supply Chain? Revisiting Agent-Based Supply Chain Automation.” _International Journal of Production Economics_ 241:108279. https://doi.org/10.1016/j.ijpe. 2021.108279. 

- Xu, Liming, Stephen Mak, Maria Minaricova, and Alexandra Brintrup. 2024. “On Implementing Autonomous Supply Chains: A Multi-Agent System Approach.” _Computers in Industry_ 161:104120. https://doi.org/10.1016/j.compind. 2024.104120. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 27 

- Xu, Liming, Stephen Mak, Yaniv Proselkov, and Alexandra Brintrup. 2024. “Towards Autonomous Supply Chains: Definition, Characteristics, Conceptual Framework, and Autonomy Levels.” _Journal of Industrial Information Integration_ 42: 100698. 

- Xue, Xiaolong, Xiaodong Li, Qiping Shen, and Yaowu Wang. 2005. “An Agent-Based Framework for Supply Chain Coordination in Construction.” _Automation in Construction_ 14 (3): 413–430. https://doi.org/10.1016/j.autcon.2004.08. 010. 

- Yang, Xianliang, Zhihao Liu, Wei Jiang, Chuheng Zhang, Li Zhao, Lei Song, and Jiang Bian. 2023. “A Versatile MultiAgent Reinforcement Learning Benchmark for Inventory Management.” _arXiv preprint arXiv:2306.07542_ . 

- Yuan, Lei, Ziqian Zhang, Lihe Li, Cong Guan, and Yang Yu. 2023. “A Survey of Progress on Cooperative MultiAgent Reinforcement Learning in Open Environment.” _arXiv preprint arXiv:2312.01058_ . 

- Zamfirescu-Pereira, J. D., Richmond Y. Wong, Bjoern Hartmann, and Qian Yang. 2023. “Why Johnny Can’t Prompt: How Non-AI Experts Try (and Fail) to Design LLM Prompts.” In _Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems_ , 1–21. Hamburg, Germany: Association of Computing Machinery. 

- Zhang, Hongxin, Weihua Du, Jiaming Shan, Qinhong Zhou, Yilun Du, Joshua B. Tenenbaum, Tianmin Shu, and Chuang Gan. 2023. “Building Cooperative Embodied Agents Modularly with Large Language Models.” _arXiv preprint arXiv:2307.02485_ . 

- Zhao, Qinlin, Jindong Wang, Yixuan Zhang, Yiqiao Jin, Kaijie Zhu, Hao Chen, and Xing Xie. 2024. “CompeteAI: Understanding the Competition Dynamics of Large Language Model-Based Agents.” In _Proceedings of Machine Learning Research_ , 61092–61107. Vol. 235. Vienna, Austria: PMLR. 

- Zheng, Ge, and Alexandra Brintrup. 2025. “Enhancing Supply Chain Visibility with Generative AI: An Exploratory Case Study on Relationship Prediction in Knowledge Graphs.” _International Journal of Production Research_ 1–23. https://doi.org/10.1080/00207543.2025.254 3964. 

- Zhu, Anding, Yunyan Han, and Hong Liu. 2024. “Effects of Adaptive Cooperation among Heterogeneous Manufacturers on Supply Chain Viability under Fluctuating Demand in post-COVID-19 Era: An Agent-Based Simulation.” _International Journal of Production Research_ 62 (4): 1162–1188. https://doi.org/10.1080/00207543.2023.217 8370. 

### **Appendices** 

### **Appendix 1. Inspiration for communication frameworks** 



<!-- Start of picture text -->
Memory: Communication<br>Perception module Action memo eee dia eagles Execution module<br>P ry communication & Summarization for<br>State memory Tera<br>Benchmark<br><!-- End of picture text -->

**Figure 12.** Framework for cognitive-inspired embodied-agent decision-making. 

28 V. JANNELLI ET AL. 

### **Appendix 2. Detailed prompt for standalone LLM agents** 



<!-- Start of picture text -->
Prompt Standalone Agent with Too!<br>1: This is simulation of a sequential supply chain. Your'<br>‘overall goal is to minimize the global costs for the whole!<br>supply chain, not just your local costs. So dont act too!<br>lsHolding e lfishly.vels foexcessAtmeettheinventorydemandsame time, iswhile veryyou costly.minimizingmustTherebalanceholding are penaltiesinventory}costs.{| 4. P1:<br>Randomfor backlog,demandsimulatingfluctuationslost salesare.orincludedunhappy to.customers.simulatoi| | chain[Sequential<br>‘market changes, requiring adaptive inventory and strategies. |<br>| Highsigec en ificantrieieetieienetsenenennenenennsnenennsneneresedholding financialcosts losses.for excess inventory can lead to}H<br>i} + BacklogP2:the+ Holding total cost,Consider cost:cost:whereisinventory thebackiog objectivethe level totallevel costs * * (1)function(1) the sumto achieve:of: Minimize 1HVLi] (~ objective2:<br>{+ Ordering cost: order qua nti ty * (1) A] | this case<br>| beeen  + Fixed cost: a fixed cost (= 1) iff order quantity > 0. [J forcost<br>5"} facagent:torsTo to consider:make this Heredecision, are thethere current iceeeeeememecect are observationsalso some variable for this |1H<br>inventory level: 20 i<br>| Backiog 0 |<br>} Latest order: 3 H<br>inventory level is the amount that the agent has in stock, HW" Obs<br>whereas in transit orders are the orders that are on their way Hl)<br>tothethe14, 3upstream agent(higher-number)inthe nex steps. agentIntranitin the orders next coming2 time steps: fom 4]){|| Varableke<br>Total cost for this agentso far: 937 ])lastorder,<br>_ "<br>Cont i nues on top right. incoming<br><!-- End of picture text -->



<!-- Start of picture text -->
Prompt Standalone Agent with Tool (continued)<br>{Pa : Here are the variable observations for the last 10 time steps: ¢<br>t a . i. H<br>{ourrent _i nventory'13,"curren t_b acklog"0, “ates t order’: 7} }<br>{reurren{{Ceurren tt_ ~inventory":inventory"11,"curren12, “curren tt_ nbabacklog":cklog"0,"atest0, "ates _ort de.order':8)r''8} |H|<br>|!{curren t uinventory"11,"currene et_ backlog"0,eee  "ates te order's}S ATL} pa:<br>{freurrent_inventory’+12,"current_backlog’.0, Yates t  order"7} +) P* prev<br>{current t inventory’:14,"curren t_ backlog’.0,"late st_ order’6} {||1] | andinventory, ord<br>{feurrent_inventory’:16,"current_backlog’:0, "atest order’5} $1) retrieve<br>ieiircurrenrcuren et t inventory'17,inventory"18, .  "curren‘current t "backlog’,backiog",packiog'a  "ates lates t_o tYatest order's5}rder'4}externa {| | memory<br>Fcurren t inventory” 20, "curre nt _backiog’ 0,"ate st _order"3)_}<br>| Fo=n-nos5-nnnonicceconananainacesscnancncesonoraioccad<br>J<br>I-55)HiThe10,  action9,Lasi(...) 307,(amount steps6, §, 5, showed ordered)4, 3, 3] from your awil demand ave down in of 2[9,8 stream time stops.10, neighbor. 10, 6,9, 70.1TL1iJ demandPs:info<br>a ee<br>FP8: The (Demand Forecasting with Linear Regression] too! has |<br>been activated. The result obtained from this too! is: [3}. Please i] | pg:<br>ft i] FF tne<br>|| 9¥@ @ lot of weight fo this forecast in your decision-making i] |" the<br>| process. J the<br>| |pr:peesWhateesshouldeenneennnnnnonnnennnonnnannnannnanbe the next amount of inventory to order?H eroor<br>'Please provide only a number in the form of an integer value |) P7:<br>nen dipapiiabebiaes 4] Pm ang<br>{wherenumericalineger answer  value  within is @  triple  number  brackets, om 0 for example: to 100. Endose [2].  youri i }] || frmdata at<br><!-- End of picture text -->

**Figure 13.** _Detailed breakdown of prompt for standalone agent with tool_ . As illustrated in this prompt, conflicting global and local agent objectives coexist in the prompts that will direct agentic decision-making. 

### **Appendix 3. Introducing tool usage** 



<!-- Start of picture text -->
Introducing Tool for Gemini Flash: Introducing Tool for Gemini Pro:<br>(.) (-)<br>{The [Demand Forecasting with Linear Regression] tool has been {The [Demand Forecasting with Linear Regression] toolhas been 4<br>{ activated. The result obtained from this tool is: [3]. Please givea | { activated. The result obtained from this tool is: [3]. Please givea +<br>Hi H Hi H<br>i lot of weight to this forecast in your decision-making process. q Hi lot of weight to this forecast in your decision-making process. {<br>H H } Use it as an upper bound for the final output. H<br>| en<br>(4) a)<br><!-- End of picture text -->

**Figure 14.** _ManualpromptoptimisationbetweenGeminiFlashandGeminiPro_ . Gemini Pro required more insistence in the prompt to steer the decision-making closer to the tool output. This is likely because Gemini Pro is designed to handle nuanced tasks, which leads it to weigh multiple factors: without clear instructions emphasising the importance of specific tools, Gemini Pro may not prioritise them as intended. In contrast, Gemini Flash, optimised for speed, tends to follow direct instructions more closely (Grigonis 2024). Without these prompt tweaks, the Gemini Pro runs that included tool usage consistently underperformed the Gemini Flash runs. 

INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 29 

### **Appendix 4. Detailed results tables** 

**Table 1.** Cumulative global costs for sequential SC – experiments with different agentic setups. 

|Setup: 3 echelons, temperature = 0.1, lead_ti|me = 2, tool = demand pred., prev|obs = 30|
|---|---|---|
|Soft Baseline Agent with (S,s) = (100, 60) policy<sup>a</sup>|159’094 (bw = 65.77168)|159’094 (bw = 65.77168)|
|Hard Baseline Agent with Demand Prediction tool<sup>a</sup>|16’645 (bw = 1.01291)|16’645 (bw = 1.01291)|
|LLM Agent Architecture|model = gemini-1.5-pro-latest|model = gemini-1.5-flash|
|Solo LLM Agent|172’624 (bw = 4.1756)|221’532 (bw = 3.40989)|
|Solo LLM Agent with Tool (Demand Pred.)|16’645 (bw = 1.01291)|15’967 (bw = 1.00138)|
|LLM Agents with Information Sharing|116’508 (bw = 2.71284)|80’822 (bw = 0.36064)|
|LLM Agents with Information Sharing & Tool (Demand Pred.)<br>|13’431 (bw = 1.02958)|25’947 (bw = 0.82897)|
|Agent negotiation with Tool (Demand Pred.) (num_iter = 3)<sup>b</sup>|15’393 (bw = 1.0229)|12’790 (bw = 1.02481)|



Note:<sup>a</sup> This agent is not powered by a foundation model. 

> bnum_iter = 3 means that each agent pair has 3 back-and-forth passes before moving to the agreement stage. 

### **Appendix 5. Detailed communication framework examples** 



<!-- Start of picture text -->
“Let's have @ conversation about how much to order to minimize the<br>Conversation Intro: overall bullwhip effect of the sequential supply chain. Let's use the<br>=n Economic Order Quantities (EOQs) shared by each agent as upper and<br>lower bound for the negotiation.”<br>NenelhiyFi | EOQ Leeee is of 4:1 eenam wiling EOE to negotiate 3 aacveeeceeeeenenncncseeeeeeeeeecnccc==syh how mach to order in order to} [iy{ minimizeE0Q theis  bullwhipeffect”9:1 am wilingto negotiate howmuchtoorderin order to;1<br>Second Loop of negotiationstage; SagarMV currentaaa  backlogaaa  isbe veryaan  highcad wllce oder 9 j<br>FOk, [will order 4.” i — ~ — ~<br>cuiitd Loop of negotiation stage:cenceennneneeennvnernveny | “Great! Let's avoid large fluctuations in our orders.” H<br>F’Sounds good! / agree that consistency 1S key fo minimizing the Dullwhip} W--nm-nmmenmmnnnnnneenn nent<br>H ‘System: “What is your final answer?” ‘System: “What is your final answer?” [ali taepril H<br>{ Agent n+1: 4 Agentn: 9 exchanges H<br> Gemini-pro (C5)<br>=a) Agentn+1 Gemini-pro — Agentn<br><!-- End of picture text -->

**Figure 15.** Example of disagreement between neighbouring agents in negotiation stage. These prompts highlight the goal of minimising the overall bullwhip effect in the sequential supply chain, while preserving the agents’ local objectives. 

30 V. JANNELLI ET AL. 



<!-- Start of picture text -->
“Let's have a conversation about how much to order to minimize the<br>Conversation intro: _} Overall bullwhip effect of the sequential supply chain. Let's use the<br>Started by downstream ™) Economic Order Quantities (EOQs) shared by each agent as upper and<br>agent lower bound for the negotiation.<br>First, Loop of negotiation stage: H{My EOQ is 6; | am willing to negotiate how much to order in order tol;<br>pereeretnmnsnentenentonsnentensnnncnenecreneeeeetococcceeecececeeeeenyli'My EQQ is 4; | am willing to negotiate how much to order in order [Oh minimizenennnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnncnnnennnnnnnnnnnnnnnnnnnnnythe DullWhip FOC ened<br>minimize<br>the bullwhip effect” {Given that my EOQ is 8 and yours is 4, how about we settle on ordering}<br>Second ‘ati {16 units each? This way, we stay close to our optimal order quantities andi<br>"That soundsLooplike of negotiation@ goodcompromisestage: to mel Ordering | minimize the bullwhip effect." H<br>both close to our EOQs and should help minimize the6b u nitsllwhip keepseffect.us}——~—~—~S~CSC*~<CS<br>{Let's do itt” Dan<br>Leecsenseneasensonussnsaensaneasansaearanensansonanscnsasenecneascmcasened [AO KP H<br>Third Loop of negotiation stage: oseneannnnennnnnacnnnnnsanaan<br>LOM secccosssssssseeeeseesconssvererererseecoonssvsseeeeesseseonsscssseed<br>|i system: What is your final answer? ‘System: What is your final answer? Finalage: Agreement}takes place |<br>i| Agent n+1: 6 Agent n: 6 attertheexchangesnegotiation |<br>=a) Agentn+1 Gemini-pro — AgentnGemini-pro (=<br><!-- End of picture text -->

**Figure 16.** Example of agreement without motivation between neighbouring agents in negotiation stage. 

### **Appendix 6. Experimental values for reproducibility** 

**Table 2.** Summary of parameters used in our experiments. 

|Parameter|Value|
|---|---|
|number of agents|3|
|<br>rounds of communication|3|
|number observations in agent|10|
|memory||
|max oder amount|100|
|lead time|2|
|temperature|0.1|
|max token count output|90|
|inventory cost|1|
|backlog cost|1|
|ordering cost|1|
|<br>fixed ordering cost|1|
|i<br>previous obs demand forecast tool|30|
|customer demand|Merton Jump Diffusion (run number 13)|



INTERNATIONAL JOURNAL OF PRODUCTION RESEARCH 31 



<!-- Start of picture text -->
‘ MA she"<br><!-- End of picture text -->

**Figure 17.** Customer Demand is simulated with Merton Jump Diffusion Model and exhibits a spike to exacerbate the bullwhip effect. 

