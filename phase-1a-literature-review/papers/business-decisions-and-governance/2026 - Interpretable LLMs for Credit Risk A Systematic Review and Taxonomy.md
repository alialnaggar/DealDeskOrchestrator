Expert Systems With Applications 306 (2026) 130941 



Contents lists available at ScienceDirect 

# Expert Systems With Applications 

journal homepage: www.elsevier.com/locate/eswa 



#### Review 

## Interpretable LLMs for credit risk: A systematic review and taxonomy 



### Muhammed Golec a,∗, Maha Alabduljalil b 

a _Department of Computer Engineering, Bo˘gaziçi University, 34342, Istanbul, Türkiye_ b _College of Science Computer Science Department, Kuwait University, Kuwait_ 

|a r t i c l e i n f o|a b s t r a c t|
|---|---|
|_Keywords:_<br>|Large Language Models (LLM), which have developed in recent years, enable credit risk assessment through|
|Large language models (LLMs)<br>Credit risk assessment explainable<br>Artificial intelligence (XAI)<br>Financial text analysis<br>Interpretable transformers<br>Natural language processing (NLP)<br>Taxonomy|the analysis of financial texts such as analyst reports and corporate disclosures. To the best of our knowledge,<br>this paper presents the first systematic review and taxonomy focusing on LLM-based approaches in credit risk<br>estimation. We determined the basic model architectures by selecting 60 relevant papers published between<br>2020–2025 with the PRISMA research strategy. And we examined the data used for scenarios such as credit<br>default prediction and risk analysis. Since the main focus of the paper is interpretability, we classify concepts<br>such as explainability mechanisms, chain of thought prompts and natural language justifications for LLM-based<br>credit models.<br>The taxonomy organizes the literature under four main headings: model architectures, data types, explainabil-<br>ity mechanisms and application areas. Based on this analysis, we highlight the main future trends and research<br>gaps for LLM-based credit scoring systems. This paper aims to be a reference paper for artificial intelligence and<br>financial researchers.|



##### **1. Introduction** 

Credit risk assessment is one of the important components in financial decision making, such as making investment decisions and determining whether to grant credit to an individual or institution (Nana et al., 2022). While traditional methods rely on structured data such as financial ratios and past payment information when assessing credit risk, in reality important information about the credit may not be available in an organized manner (Roeder et al., 2022). An example of this is that executive comments, economic news and analyst reports are generally in free text (unstructured). Previous approaches to financial text, from traditional classifiers (SVM, RF) to static embeddings (Word2Vec/GloVe), struggle to capture concepts such as context, negation, and hedging for analyst reports. George (2024). While RNN/LSTM models (sequence models) reduce sparsity, they have limitations such as (i) long document length limitations, (ii) intertemporal domain drift, and (iii) intensive feature engineering (Wang et al., 2018). These gaps can be overcome by using context-aware, domain-adaptive representations. 

Transformer-based large language models address these limitations of RNN/LSTM models by using contextual token representations and long-range dependency modeling to improve signal extraction from un- 

structured text (Choi et al., 2025). Advanced LLM models such as GPT and FinBERT have great potential in financial applications with their high performance in extracting meaning from free text (Golec et al., 2025; Kang & Choi, 2025). They can produce interpretable outputs by making sense of complex financial data and thus facilitate decisionmaking processes (Shobayo et al., 2024). With its high potential, this research area, LLM-Driven Credit Risk Assessment, where Natural Language Processing (NLP), financial analysis and Explainable Artificial Intelligence (XAI) intersect, has begun to attract the attention of researchers. However, the applications of LLMs in the field of credit risk analysis have not yet been systematically examined. Existing AI and LLM-based surveys only cover broad foundations such as generative AI and financial NLP in banking, while few address credit risk, and even fewer position interpretability as central to credit analysis. General surveys in the field, however, do not focus on the specifics of credit risk, instead emphasizing more general criteria and tasks. Conversely, credit risk surveys focus on traditional ML techniques outside of LLM. Consequently, a new synthesis is needed that evaluates the entire field across model architectures, data formats, interpretability mechanisms, and application areas, focusing on LLM-focused credit risk modeling. 

> ∗ Corresponding author. 

> _E-mail addresses:_ muhammed.golec@bogazici.edu.tr (M. Golec), maha.jalil@ku.edu.kw, maha@cs.ku.edu.kw (M. Alabduljalil). 

https://doi.org/10.1016/j.eswa.2025.130941 Received 10 June 2025; Received in revised form 18 November 2025; Accepted 20 December 2025 Available online 24 December 2025 

0957-4174/© 2025 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies. 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

##### _1.1. Objectives and contributions_ 

This paper systematically reviews LLM-based approaches in credit risk assessment and presents a detailed taxonomy study. The main contributions of this paper are as follows: 

- **Reproducible credit-risk synthesis** : 60 studies (2020–2025) that explicitly apply LLMs to credit risk problems are analyzed using the PRISMA methodology. This narrows the scope, unlike the established literature, from broad financial-NLP/GenAI to credit risk tasks. 

- **Four-pillar taxonomy for credit risk** : A structured taxonomy is provided, encompassing model architectures, data formats, interpretability mechanisms, and application domains. The taxonomy focuses on the credit task and includes interpretability considerations such as quick-level justifications. 

- **Evidence-based positioning vs. prior surveys** : A comparison with the literature is provided using criteria such as task-level credit focus, LLM specificity, depth of interpretability, and structured taxonomy (Table 1). This positioning of the paper’s scope relative to the broader field of FinLLM/financial-NLP and non-LLM credit risk surveys. 

- **Gap analysis and future agenda** : Research gaps specific to LLMs for credit are summarized and concrete aspects such as cost difference adjustment and increased confidence interval reporting are identified. 

To the best of our knowledge, there is no LLM-specific and interpretability-aware taxonomy study in the literature that offers an evidence-based comparison with existing surveys, excludes credit risk. The term “LLM-Specific” is used throughout this paper to indicate whether the study focuses entirely on large language models (LLMs) or whether there is no separate analysis/experiment/section devoted to LLMs within the general AI/ML context. 

##### _1.2. Paper structure_ 

Fig. 1 shows the organization of the paper. Section 2 examines the current survey studies in the field related finance and LLM , examining their focus and limitations. Then, a comparison analysis is performed by comparing this paper and the literature. Section 3 explains the research questions and article collection strategy. Section 4 provides a taxonomy by classifying LLM-oriented credit risk assessment systems in four main aspects: model architecture, data modality, interpretability mechanism and application area. Section 5 synthesizes the main emphases obtained throughout the paper and highlights the literature gaps. Section 6 concludes the paper by discussing the implications for researchers and finance practitioners in the field. 

##### **2. Related surveys** 

Although there has been increasing interest in LLM and artificial intelligence (AI)-based financial studies in recent years, there is still no comprehensive classification in terms of focus, depth and relevance to credit risk, and discussions about interpretability, a key component in credit assessment scenarios, are lacking. Surveys found in the literature are examined in three clusters: (A) domain-general finance/LLM overviews, (B) financial-NLP/FinLLM surveys, and (C) credit risk/ML surveys. All of these are evaluated based on their credit risk targeting, LLM specificity, and interpretability. 

##### _2.1. Domain-general finance / LLM overviews_ 

**Scope & Focus** : The papers reviewed under this subsection include comprehensive surveys such as generative AI overviews and inclusiveness/policy analyses. These surveys address GenAI-based applications in banking and risk mitigation, as well as LLM-based programs such as FinGPT/BloombergGPT. While all these surveys describe LLM programs and their promise in finance, they are not credit-focused and do 

not delve deeply into interpretability requirements and credit-specific modeling options. 

Staegemann et al. (2025) highlight the potential of LLMs for risk reduction and customer experience in their literature review on generative AI applications in banking. However, the article does not include techniques for credit risk modeling or interpretability, and there is no taxonomy of model types. In Lee (2024), models such as FinGPT and BloombergGPT are discussed, LLMs address financial inclusion and policy implications, and ethical concerns, but ignore credit risk applications. Chen et al. (2024) highlight the risks of using LLMs in highrisk sectors in their study of finance, law, and healthcare. However, the financial discussion is superficial, and credit scoring methods are not addressed. In Jayanthakumaran et al. (2025), sentiment analysis techniques used in banking are reviewed, and the focus is on examining the impact on investor confidence. However, credit risk tasks are only superficially examined. In Nie et al. study’s the research on generative AI and LLMs focused on risk modeling and deployment architectures (Nie et al., 2024). The paper discusses areas such as data engineering, credit scoring modules, etc. but lacks a comparative taxonomy and interpretability mechanisms for LLM types. Alonso et al. (2024) provide an overview of LLMs in areas such as asset management and risk reporting, but is insufficient for credit risk. Krause (2023) presents a survey discussing the sustainability of LLM models such as ChatGPT. The survey is mostly on ethical and governance concerns and is superficial in terms of credit scoring, model breakdowns, and datasets. In Xu (2024), the robustness of LLMs in financial tasks is assessed and benchmarks are made on summarization and event detection. However, the study does not include credit-related tasks and explainability is weak. Lakkaraju et al. (2023b) evaluate LLM performance through a fairness lens, focuses on bias reduction strategies such as improving user trust, but credit risk assessments and explainability are very superficial. 

**Takeaway** : Consequently, the surveys classified under this subsection lay the groundwork for LLMs in finance, but they do not establish a credit-focused, interpretability-aware taxonomy. 

##### _2.2. Financial NLP / FinLLM surveys_ 

**Scope & Focus** : The surveys reviewed under this subsection address financial NLP tasks and domain-specific financial LLMs such as FinLLM. Some of these surveys compare LLMs in multilingual finance (Kong et al., 2024), use GenAI agents in financial tasks (Joshi, 2025c), and summarize financial datasets and FinLLM-specific challenges (Li et al., 2023), Lee et al. (2025). Other studies emphasize sentiment analysis or financial security scenarios (Omoseebi et al., 2024) and highlight the concepts of fairness and reproducibility (Junyan Wang & Xiaoqi Wang, 2025). These papers focus on financial datasets rather than domaingeneral datasets and are NLP-focused rather than credit-specific. 

Kong et al. (2024) presented a study that benchmarked LLM-based financial tasks for three different languages (Chinese, Japanese, English). However, the model types are not classified and also the explainability is not analyzed for credit risk domains. Joshi (2025c) provides a detailed architectural review on LLM-based applications for credit scoring and macroeconomic simulations. However, the paper lacks empirical comparison and also lacks a classification for interpretability. In Li et al. (2023), LLMs are studied for financial applications such as credit analysis and fraud detection. However, they are very superficial in interpretability and credit-specific modeling. Lee et al. (2025) review domain-specific financial applications based on LLM, but categorizes flow tasks and datasets, but does not focus on credit risk subdomains. Omoseebi et al. (2024) investigates the financial security side of LLMs such as fraud detection, but does not perform detailed credit risk modeling and taxonomy studies. In Junyan Wang and Xiaoqi Wang (2025), democratization of financial datasets and open data models of LLMs are discussed, but no empirical comparison is included for credit or risk analytics. 

2 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 



**Fig. 1.** The organization of the paper. 



**Fig. 2.** PRISMA flow diagram for the selection of studies on LLM-based credit risk assessment. 

size traditional ML and statistical-based methods for financial forecasting, but do not address large language models or explainable AI methods. In Joshi et al. study’s research on AI frameworks in credit risk and trading applications, but does not focus on LLM-specific taxonomy or performance benchmarking (Joshi, 2025a). In Khan et al. (2025) investigates AI-based methods in financial scenarios such as fraud detection and portfolio management, but does not provide a detailed review of model interpretability and LLM for credit scoring. In Karami and Igbokwe study examines AI-based risk assessment and limitations of traditional credit methods, but does not provide a classification of LLM (Karami & Igbokwe, 2025). 

**Takeaway** : While this group directly addresses credit risk, it is tied to pre-LLM paradigms and lacks integration with converter-based architectures, multimodal data, or advanced interpretability. Therefore, gaps inherent to LLM are not addressed, demonstrating the need for a four-pillar classification. 

**Takeaway** : While the surveys examined under this subsection describe FinLLM criteria, datasets, and multilingual capabilities, they lack classifications of credit risk subtasks. Consequently, while these surveys address general NLP and finance topics, they lack an interpretable synthesis focused on credit. 

##### _2.3. Credit risk / ML surveys_ 

**Scope & Focus** :The surveys reviewed under this subsection generally fall outside the context of LLM, but consist of studies examining credit risk and ML/AI methods. Some of the surveys (Zavitsanos et al., 2025) classify ML methods used in financial risk detection, while others examine AI and credit risk in modern banking and trading frameworks (Joshi, 2025a). While the surveys reviewed under this subsection examine credit scoring tasks, datasets, and ML methods, they generally do not include LLM-based architectures and systematic interpretability. 

Zavitsanos et al. (2025) examine ML approaches in financial risk detection, examining features, data labels, evaluation techniques, and ML methods. Although this is a useful taxonomy, it is more focused on ML than LLM. In Aziz and Andriansyah (2023), the authors mainly empha- 

##### _2.4. Comparison of surveys_ 

Table 1 provides a comparison of the surveys examined in this section. While interest in the financial domain applications of LLMs is increasing day by day, existing studies focus on broad themes such as generative AI (Staegemann et al., 2025), inclusiveness frameworks (Lee, 2024) and financial NLP (Lee et al., 2025; Li et al., 2023). Only a limited number of studies directly focus on credit risk tasks, and none of them provide a taxonomy by examining LLM architectures, data formats, interpretability techniques and domain-specific applications. 

Furthermore, most studies do not provide interpretability for highrisk decisions such as credit scoring, and the studies that do provide interpretability are very superficial (Alonso et al., 2024; Junyan Wang & Xiaoqi Wang, 2025). Some of the surveys include studies such as sentiment analysis or fraud detection (Samson & Rout, 2024), but they do not address the concept of credit risk modeling. Some of the reviewed studies focus only on traditional machine learning (ML) (Karami & Igbokwe, 2025; Zavitsanos et al., 2025) and only propose conceptual frameworks without model comparison (Joshi, 2025b,c). 

3 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 1** 

Comparison of related survey studies with this work _LLM-Specific is to indicate studies that focus solely on LLMs or devote a separate analysis section to LLMs_ . 

|Work|Main Aim|Credit Risk (task-|LLM-Specific<br>(exclu-|XAI/Interpretability|Taxonomy (structured classifica-|
|---|---|---|---|---|---|
|||level focus)|sive/section-level)|(depth)|tion)|
|Staegemann et al.|GenAI in Banking|||||
|(2025)||||||
|Lee (2024)<br>|LLMs for Financial<br>Regulation<br>|||||
|Joshi (2025b)|Agentic GenAI for<br>Risk Mgmt|||||
|Chen et al. (2024)|LLMs<br>in<br>Fi-<br>nance/Health-<br>care/Law|||||
|Jayanthakumaran|Sentiment in Banking|||||
|et al. (2025)|Headlines|||||
|Nie et al. (2024)|LLMs in Financial<br>Applications|||||
|Zavitsanos<br>et<br>al.<br>|ML for Financial Risk|||||
|(2025)|Reports|||||
|Aziz and Andrian-|AI in Modern Bank-|||||
|syah (2023)|ing|||||
|Joshi (2025a)|GenAI Agents in Fi-<br>nance|||||
|Kong et al. (2024)|LLMs in Investment<br>Mgmt|||||
|Joshi (2025c)|GenAI for Financial<br>Risk|||||
|Lee et al. (2025)|Survey of FinLLMs|||||
|Khan et al. (2025)|Explainable AI in Fi-|||||
||nance|||||
|Karami and Igbokwe|Big Data in Credit|||||
|(2025)|Risk|||||
|Alonso et al. (2024)|LLMs for Financial<br>Reasoning|||||
|Li et al. (2023)|LLMs in Financial AI|||||
|Lakkaraju<br>et<br>al.|LLMs as Finance Ad-|||||
|(2023b)|visors|||||
|Samson and Rout|LLMs for Sentiment|||||
|(2024)|Analysis|||||
|Omoseebi<br>et<br>al.|LLMs for Financial|||||
|(2024)|Security|||||
|Junyan Wang and Xi-<br>aoqi Wang (2025)|Consistency of LLMs|||||
|Krause (2023)|LLMs<br>in<br>Finance<br>(ChatGPT/Bard)|||||
|Xu (2024)|LLM Strategy in FIs|||||
|**This** **Work**|LLMs for Credit Risk<br>Assessment|||||



Although some of the studies discuss domain-specific LLMs (such as FinBERT, FinGPT, and InvestLM), they do not systematically model architecture or risk. The term “LLM-specific” used throughout this paper indicates whether the study focuses entirely on large language models (LLMs) or whether there is no separate analysis/experiment/section dedicated to LLMs within the general AI/ML context. None of the existing studies provide a classification of LLM applications that addresses both modeling and regulatory requirements (e.g., explainability, data provenance, or fairness). **This study is the first to fill this gap based on four main pillars: model architecture, data modality, interpretability mechanism, and application domain.** 

##### **3. Systematic review protocol** 

This section describes the methodology used in the systematic review of LLM-based credit risk assessment. 

##### _3.1. Paper collection and selection protocol_ 

For the paper collection, refereed journals, high-ranking conferences, book chapters covering the years 2020–2025 were collected by scanning libraries such as IEEE Xplore, Elsevier, ACM Digital Library, SpringerLink, Scopus and arXiv. Previous fundamental studies such as FinBERT 

2019 were therefore excluded from the inclusion framework. Although major digital libraries are covered, some finance-focused repositories (such as SSRN and NBER) are not included, and it is acknowledged that this may limit the scope of the working papers. All searches were provided independently by both authors. To provide PRISMA recommendations, search strings are provided in Table 2 along with execution dates. The initial searches were conducted in January 2025 and completed in May 2025. Disagreements were resolved through discussion, and no blinding was experienced due to the limited author pool. The following keywords were used while scanning the paper: 

1. `("LLM" OR "Large Language Model" OR "Transformer" OR "FinLLM" OR "FinGPT" OR "FinBERT") AND ("Credit Scoring" OR "Credit Risk Assessment" OR "Credit Default" OR "Loan Approval" OR "Underwriting" OR "PD/LGD/EAD" OR "Counterparty Risk" OR "Basel")` 

2. `("LLM" OR "Transformer") AND ("Explainability" OR "XAI") AND ("Financial NLP" OR "Financial Text Analysis")` 

3. `("Credit Risk") AND ("Multimodal Data" OR "Unstructured Text" OR "Behavioral Data")` 

4. `("LLM" OR "FinLLM" OR "GPT-3/4" OR "ChatGPT" OR "FinBERT") AND ("Evaluation" OR "Benchmark")` 

4 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 2** 

Final database-specific search strings and execution dates for reproducibility. 

|Database|Search String (Final Syntax)|Date of Search|
|---|---|---|
|**IEEE** **Xplore**|((“LLM” OR “Large Language Model” OR “Transformer” OR<br>“FinLLM” OR “FinGPT” OR “FinBERT”)) AND (“Credit Scor-<br>ing” OR “Credit Risk Assessment” OR “Credit Default” OR<br>“Loan Approval” OR “Underwriting” OR “PD” OR “LGD” OR<br>“EAD” OR “Counterparty Risk” OR “Basel”)|12 Jan 2025|
|**Scopus**|TITLE-ABS-KEY((“LLM” OR “Large Language Model” OR<br>“Transformer” OR “FinLLM” OR “FinGPT” OR “FinBERT”))<br>AND TITLE-ABS-KEY((“Credit Scoring” OR “Credit Risk As-<br>sessment” OR “Credit Default” OR “Loan Approval” OR “Un-<br>derwriting” OR “PD” OR “LGD” OR “EAD” OR “Counter-<br>party Risk” OR “Basel”))|12 Jan 2025|
|**ACM** **DL**|Abstract:(“LLM” OR “Transformer” OR “FinLLM” OR “Fin-<br>GPT” OR “FinBERT”) AND Abstract:(“Credit Risk” OR<br>“Credit Default” OR “Loan Approval” OR “Underwriting”<br>OR “PD” OR “LGD” OR “EAD”)|18 Jan 2025|
|**Elsevier**|(“LLM” OR “Large Language Model” OR “Transformer” OR<br>“FinLLM” OR “FinGPT” OR “FinBERT”) AND (“Credit Risk”<br>OR “Credit Scoring” OR “Credit Default” OR “Loan Ap-<br>proval” OR “Underwriting” OR “Basel”)|25 Jan 2025|
|**SpringerLink**|(“Large Language Model” OR “LLM” OR “FinBERT” OR “Fin-<br>GPT”) AND (“Credit Risk” OR “Credit Scoring” OR “Loan<br>Approval”)|25 Jan 2025|
|**arXiv**|(“LLM” OR “Large Language Model” OR “FinBERT” OR “Fin-<br>GPT” OR “ChatGPT” OR “GPT-4”) AND (“Credit Risk” OR<br>“Credit Default” OR “Loan Approval” OR “Underwriting”)|20 May 2025|



5. `("Fairness" OR "Bias" OR "Hallucination" OR "Reproducibility") AND ("LLM" OR "Credit Risk")` 

Fig. 2 summarizes the strategy followed for paper collection in this survey. Following the PRISMA guidelines, 182 papers were first collected as the initial body as a result of the relevant keys. After removing duplicates and papers that were not related to the research area, 120 papers were obtained. With the joint efforts of both authors in this survey (according to the inclusion criteria), 51 articles were obtained for the final analysis and this number was increased to 60 papers with the snowball method. The inclusion criteria can be summarized as follows: (i) preprint in peer-reviewed publications, (ii) focus on LLM or transformer-based models, (iii) focus on credit risk tasks, and (iv) be fully available in English. Excluded at eligibility: Not credit risk (n=28), Not LLM (n=21), No interpretability (n=6), No full text (n=4). A classification of all these papers is shown in Table 3. In addition to listing selected works, Table 4 & 5 presents some evaluation metrics to provide a comparison of performance levels. Studies are first grouped by model category: encoder-only, decoder-only, hybrid channels, domain-specific FinLLMs, and parameter-efficient LLMs. The datasets, metrics, and results used are then examined. The advantages and disadvantages of all these studies are categorized. 

##### _3.2. Quality and risk-of-bias assessment_ 

For the PRISMA-based selection protocol, a specific quality and risk of bias assessment was performed on the credit risk modeling studies investigated for this paper. A binary (Yes/No) list of items covering dataset transparency, reproducibility, interpretability mechanisms, neutrality issues, robustness testing, and publication type for the studies (60 papers) is shown in Table 6. 

##### _3.3. Research questions_ 

In this paper, the systematic review is structured around five research questions. Table 7 shows the research questions, motivation, and relevant section information for this paper. For transparency in the taxonomy, the research questions are defined according to the following criteria: 

- **RQ1 (Model architectures)** : Categories are created using transformative design families. This is to distinguish between architectures used when processing textual and financial signals. 

- **RQ2 (Data modalities)** : Data are grouped using the source structure (structured table, unstructured text, etc.). This is to capture heterogeneity in the inputs used to ensure generalizability and fairness. 

- **RQ3 (Interpretability mechanisms)** : Explainability is adjusted based on the type of strategy. This is to reflect whether transparency is internally focused. 

- **RQ4 (Application domains)** : Categories are created following financial scenarios such as retail/SME credit scoring. This is to highlight practical application contexts. 

- **RQ5 (Challenges & gaps)** : Fairness/bias, robustness, reproducibility, and cost/efficiency constraints were derived inductively. The purpose of this is to identify unresolved issues in LLM-based credit risk. 

##### **4. Taxonomy of LLM-based credit risk assessment** 

After reviewing the LLM-based credit risk literature, recurring design families, input structures, and transparency strategies were generated, while categorizing the models according to their architectures, data formats, and interpretability mechanisms. Methodological consistency was ensured with RQ1–RQ3. The papers collected in this section are classified around four main categories: model architectures, data formats, interpretability mechanisms and application areas, and answers are sought to RQ1, RQ2, RQ3, and RQ4. 

##### _4.1. Model architectures (RQ1)_ 

Recent research on LLM-based credit risk has spanned a variety of domains, from transformer-based architectures to hybrid pipelines and domain-specific fine-tuning to efficient learning. This subsection surveys model architectures for credit risk prediction found in the literature to answer RQ1. Fig. 3 shows a taxonomy of these models. 

- **Encoder-Only Architectures** : Encoder-only models (RoBERT, DistilBERT, FinBERT) are widely used in textual analysis-based financial classification. Sanz-Guerrero and Arroyo (2024a) integrates Fin- 

5 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 3** 

Overview of 60 selected studies. 

|No|Paper|Venue/Platform|Year|
|---|---|---|---|
|1|Sanz-Guerrero and Arroyo (2024a)|Inteligencia Artificial (IBERAMIA)|2025|
|2|Dogra et al. (2022)|MDPI Systems|2022|
|3|Dolphin et al. (2024)|arXiv / Polygon.io|2024|
|4|Cai (2024)|IEEE ICEDCS|2024|
|5|Govindaraj et al. (2023)|World Journal of Advanced Research Reviews|2023|
|6|Xie et al. (2023a)|Proceedings of the 37th International Conference on Neural Information Processing Systems|2023|
|7|Babaei and Giudici (2024a)|Machine Learning with Applications (Elsevier)|2024|
|8|Loukas et al. (2023)|ACM ICAIF ’23 (International Conference on AI in Finance)|2023|
|9|Liu et al. (2024a)|ACM DEBAI 2024 (Digital Economy, Blockchain & AI)|2024|
|10|Chen et al. (2023)|International Journal of Computer Science & Info Systems|2024|
|11|Luca (2024)|ResearchGate (Preprint)|2024|
|12<br> 13|Inserte et al. (2024)<br>Yang et al. (2020)|arXiv<br> arXiv|2024<br> 2020|
|14|Rao and Zhang (2025)|International Journal of Multidisciplinary Research and Growth Evaluation|2025|
|15|Yoon(2023)|InternationalJournalofAdvancedSmartConvergence|2023|
|<br> 16|<br>Feng et al. (2023)|<br> ACM (Conference acronym ’XX)|<br> 2024|
|17|JOEL (A.)|ResearchGate|2023|
|18|Walia et al. (2025)|arXiv (arXiv:2502.17011v1)|2025|
|19|Tan and Kok (2024)|ICIS (AIS Electronic Library)|2023|
|20<br>|Idbenjra et al. (2024)<br>|Elsevier – Decision Support Systems<br>|2024<br>|
|21|Zhang et al. (2023a)|arXiv|2023|
|22|Malaysha et al. (2024)|arXiv|2024|
|23|Wu et al. (2023)|CRC Working Papers|2024|
|24|Sideras et al. (2024)|ACM (ICAIF ’24)|2024|
|25<br> 26|Fatemi et al. (2024)<br>Kalluri (2024)|arXiv<br> IJNRD|2024<br> 2024|
|27|Lin et al. (2025b)|ACM ICAIF|2024|
|28|Lei et al. (2025)|arXiv|2025|
|29|Lakkaraju et al. (2023a)|ACM ICAIF|2023|
|30|Liu et al. (2023)|NeurIPS Workshop|2023|
|31|Lopez-Lira et al. (2025)|arXiv|2025|
|32|Xie et al. (2023b)|NeurIPS (Datasets & Benchmarks Track)|2023|
|33<br>|Huang et al. (2025)<br>|MDPI Applied Sciences<br>|2025<br>|
|34|de S. et al. (2024)|WebMedia (Brazilian Symposium on Multimedia and the Web)|2024|
|35|Huang et al. (2024)|MDPI Applied Sciences|2025|
|36|Seshakagarietal.(2025)|Int.Jr.ofHumComp.&Int.|2025|
|<br> 37|<br>Babaei and Giudici (2024b)|<br> Machine Learning with Applications|<br> 2024|
|38|Wang et al. (2025)|IEEE Transactions on Engineering Management|2025|
|39|Lin et al. (2025a)|Journal of Data, Information and Management|2025|
|40|Hartomo et al. (2025)|IEEE Access|2025|
|41|Yan et al. (2024)|IEEE RAAI (Robotics, Automation, and AI Conference)|2024|
|42|Gupta et al. (2024)|JPMorgan Chase (Internal ML Research)|2024|
|43|Suresh et al. (2024)|Educational Administration: Theory and Practice (Kuey)|2024|
|44|Ni et al. (2024)|IEEE DOCS (Data-driven Optimization of Complex Systems)|2024|
|45|Bond et al. (2023)|Working Paper / Preprint (University of Queensland)|2024|
|46|Sun et al. (2024)|IEEE Access|2024|
|47|Sabuncuoglu and Maple (2025)|IEEE Symposium on Computational Intelligence for Financial Engineering and Economics (CIFEr)|2025|
|48|Xie et al. (2024)|NeurIPS (Track on Datasets and Benchmarks)|2024|
|49|Liu et al. (2024b)|IEEE 4th International Conference on Computer Communication and Artificial Intelligence (CCAI)|2024|
|50|Liu et al. (2025)|_Finance_ _Research_ _Letters_ _(Elsevier)_|2025|
|51|ChandaandPrabhu(2023)|_IEEEICICCSConferenceProceedins_|2023|
|<br> 52|<br>Papasotiriou et al. (2024)|_g_<br> _ACM_ _ICAIF_ _’24_ _(AI_ _in_ _Finance_ _Conference)_|<br> 2024|
|3|iikil2024|_IEEEA_|2024|
|5<br> 54|Rzns et a. ()<br>Talha et al. (2023)|_ccess_<br> _ICON_|<br> 2024|
|55|Yu et al. (2023)|SSRN|2024|
|56|Kim et al. (2023)|ACM ICAIF|2023|
|57|Sanz-Guerrero and Arroyo (2024b)|SSRN|2024|
|58|Guo et al. (2023)|The 2023 Conference on Empirical Methods in Natural Language Processing|2023|
|59|Fallahgoul (2025)|SSRN (Preprint)|2025|
|60|Zhang et al. (2023b)|ACM ICAIF|2023|



BERT and XGBoost using the LendingClub dataset and reports improvements in AUC performance compared to tree-based models. It also shows that text descriptions improve under bias risks. In another study, Dogra et al. (2022), Random Forests-based DistilBERT was applied to stock reaction analysis, achieving 94% accuracy. However, the approach is limited to narrow event windows, and therefore, while encoder-only models perform well in structured text classification, they face tradeoffs in interpretability and generalizability. FinBERT is robust at classifying sentiment on financial datasets. For example, Seshakagari et al. (2025) reported that F1=90.8% for news sentiment, achieving performance close to 

GPT-4. This demonstrates FinBERT’s reliability as a baseline for the field. Guo et al. (2023) showed that encoder models outperform decoder models in FinLMEval for low-resource environments. This demonstrates the value of encoders. Luca (2024) applied BERT to default detection and achieved 92.5% accuracy. However, despite this high accuracy, they encountered the problem of data scarcity. Similarly, Kim et al. (2023) reduced the “buy bias” in Korean analyst reports with KR-FinBERT. In conclusion, all these studies demonstrate that encoder-only architectures, while balancing accuracy and interpretability, have limitations in computational efficiency. 

6 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 4** 

Comparative overview of 60 selected studies (Part I: Studies 1–30). 

|No|Study (Author, Year)<br>|Model Category<br>|Dataset / Task<br>|Evaluation Metric(s)<br>|Reported Result(s)<br>|Notes (Strengths / Limitations)<br>|
|---|---|---|---|---|---|---|
|1|Sanz-Guerrero and<br>Arroyo (2024a)|Encoder-only (BERT +<br>XGBoost)|LendingClub P2P<br>loans (119,101 with<br>descriptions)|Balanced Accuracy,<br>AUC|Improved Acc &<br>AUC vs baseline<br>(XGBoost only)|Text features add predictive<br>power; opacity/bias issues|
|2|Dogra et al. (2022)|Encoder-only<br>(DistilBERT + RF)|Indian bank stocks<br>reaction to 7 major<br>news events|Accuracy|Acc = 94%<br>(DistilBERT+RF,<br>with SMOTE)|Strong event-study; limited in<br>scope|
|3|Dolphin et al. (2024)|Decoder-only (GPT-4 +<br>validation framework)|Financial news<br>(5,530 articles,<br>Google News)|Coverage, Sentiment<br>accuracy|90% ticker coverage,<br>+22% extra tickers<br>vs providers|First per-company sentiment API;<br>hallucination risk|
|4|Cai (2024)|LLM-assisted (FinGPT +<br>ML models)|Australian & German<br>Credit datasets<br>(synthetic<br>augmentation)|Accuracy, Recall,<br>Precision, F1|RF Acc ↑ to 0.89 (vs<br>0.86); F1 ↑ to 0.87|Synthetic data boosts<br>performance; useful for<br>small/imbalanced samples|
|5|Govindaraj et al.<br>(2023)|Encoder-only<br>(Explainable<br>Transformer)|Multi-modal<br>financial data<br>(prices, volumes,<br>macro, sentiment)|MAE, RMSE, MAPE,<br>Interpretability|Outperforms<br>LSTM/GRU; +1.5%<br>MAE vs vanilla<br>transformer|Accuracy-transparency balance;<br>slight accuracy trade-off|
|6|Xie et al. (2023a)|Decoder-only (FinMA =<br>LLaMA fine-tuned)|FLARE benchmark<br>(FPB, FiQA-SA, NER,<br>QA, stock, credit<br>scoring)|Accuracy, F1, MCC,<br>EM Acc.|FinMA beats GPT-<br>4/BloombergGPT on<br>SA/headline; weaker<br>on QA/NER|First open-source fin. LLM;<br>limited numeric reasoning|
|7|Babaei and Giudici<br>(2024a)|Decoder-only (GPT,<br>Informed GPT)|LendingClub P2P<br>loans (accepted vs<br>rejected)|AUC|GPT ≈ 0.61;<br>Informed GPT ≈<br>0.67; LR ≈ 0.75|In-context examples help; LR still<br>stronger; API cost/latency|
|8|Loukas et al. (2023)|Encoder + Decoder<br>(MPNet, GPT-3.5/4)|Banking77 (intent<br>classification,<br>few-shot & cost)|Micro-F1, Macro-F1,<br>Cost|GPT-4 (3-shot)<br>_𝜇_-F1=83.1; MPNet<br>(20-shot) _𝜇_-F1=91.2|Few-shot LLMs competitive; RAG<br>improves affordability|
|9|Liu et al. (2024a)|LLM + XAI (ChatGPT,<br>GPT-4o)|HELOC (binary<br>credit risk)|Accuracy,<br>Explainability|GPT-4o integrates<br>SHAP+LIME<br>prompts; clearer<br>outputs|Transparency boost; role-based<br>prompting helps stakeholders|
|10|Chen et al. (2023)|Reliability discriminator<br>(RelD)|RelQA dataset<br>(1.37M QA pairs)|Accuracy, F1,<br>Reliability|RelD detects<br>hallucinations across<br>LLMs|Faithfulness improved; adds<br>deeper metrics|
|11|Luca (2024)|Encoder+Decoder<br>(BERT, GPT)|Credit unions<br>(default, fraud,<br>scoring)|Accuracy, Precision,<br>Recall, F1, AUC|BERT Acc=92.5%;<br>Fraud Prec=89.3%|LLMs _>_ trad. models; but small<br>data, interpretability issues|
|12|Inserte et al. (2024)|Decoder-only (OPT,<br>Pythia)|FLARE (FPB,<br>FiQA-SA, Headlines,<br>NER)|Accuracy, F1|F1 up to 0.97<br>(Headlines), 0.83<br>(FiQA-SA)|Small LLMs rival larger; synthetic<br>instruction helps|
|13|Yang et al. (2020)|Transformer + XAI|M&A Rumor dataset<br>(2007–2019)|MCC, Accuracy, F1|Acc=0.89,<br>F1=0.888,<br>MCC=0.780|Adversarial training +<br>counterfactuals boost trust|
|14|Rao and Zhang<br>(2025)|Hybrid (LSTM+Trans-<br>former+CNN)|AI vs human text<br>(1378 samples)|Accuracy, Precision,<br>Recall, F1|Acc=99%,<br>Prec=0.99,<br>Rec=1.0, F1=0.99|Strong AI-text detection; finance<br>transfer unclear|
|15|Yoon (2023)|Decoder-only (GPT<br>chatbot)|SME credit<br>evaluation dataset|Accuracy, RMSE,<br>MAE|Competitive vs trad.<br>eval; faster|Automates SME eval; dataset<br>small, domain limits|
|16|Feng et al. (2023)|Decoder-only (LLaMA2<br>fine-tuned, CALM)|9 datasets (German,<br>Australia,<br>LendingClub etc.)|Accuracy, F1, MCC,<br>Bias|CALM ≈ SOTA;<br>GPT-4 close; bias<br>issues observed|Generalist framework; fairness<br>concerns|
|17|JOEL (A.)|Encoder+Decoder<br>(BERT, GPT)|Credit unions<br>(default, fraud,<br>scoring)|Accuracy, Precision,<br>Recall, F1, AUC|BERT Acc=92.5%,<br>GPT Acc=90.7%|Outperform LR/DT; compute<br>cost; adaptation needed|
|18|Walia et al. (2025)|Hybrid<br>(GANs+RL+LLM)|Bond yield<br>forecasting (AAA,<br>BAA, US10Y, Junk)|MAE, Profit Rate,<br>Eval|MAE=0.103;<br>Profit=60%|GAN+RL improves; complex<br>pipeline|
|19|Tan and Kok (2024)|Encoder-only<br>(FinBERT-XRC)|SEC 10-K filings<br>(2008–2013)|F1, Accuracy,<br>Explainability|F1 ↑; interpretable at<br>multiple levels|Scalable; heavier than stats<br>models|
|20|Idbenjra et al.<br>(2024)|Hybrid (Logit Leaf<br>Model)|French consumer<br>credit (65k)|AUC, Top-decile Lift|LLM competitive vs<br>SOTA; best on TDL|Accuracy vs interpretability<br>trade-off|
|21|Zhang et al. (2023a)|Decoder-only<br>(Instruct-FinGPT)|Twitter, FiQA, FPB|Accuracy, F1|Twitter Acc=0.88,<br>F1=0.84|Beats FinBERT/ChatGPT; latency<br>issues|



7 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 4** Continued 

|No|Study (Author, Year)|Model Category|Dataset / Task|Evaluation Metric(s)|Reported Result(s)|Notes (Strengths / Limitations)|
|---|---|---|---|---|---|---|
|22|Malaysha et al.<br>(2024)|Encoder-only (Arabic<br>BERTs)|AraFinNLP Shared<br>Task (39k queries)|Micro-F1, BLEU|Best<br>Micro-F1=0.8773;<br>BLEU=1.667|First Arabic FinNLP shared task;<br>dialect imbalance|
|23|Wu et al. (2023)|LLM+DL<br>(ChatGPT+DL)|Chinese bank SME<br>loans|Accuracy, F1,<br>Explainability|ChatGPT-texts _>_<br>human-texts for<br>default prediction|First to use LLM texts for credit<br>scoring|
|24|Sideras et al. (2024)|Hybrid<br>(LLM+VAE+TF-IDF)|Bankruptcy<br>prediction<br>(ECL+MD&A)|AUC, F1,<br>Precision/Recall|Outperforms<br>baselines; LLM<br>zero-shot variable|Auditor’s opinion strong;<br>imbalance mitigated|
|25|Fatemi et al. (2024)|Instruction fine-tuned<br>LLMs|Multi-task (FPB,<br>FiQA-SA, FinRED)|Accuracy, F1|Small LLMs<br>competitive w/<br>GPT-4|Efficient; avoids forgetting;<br>compute cost|
|26|Kalluri (2024)|Param-efficient LLM<br>tuning|Credit unions (inq.,<br>compliance)|Accuracy,<br>Compliance, Bias|+27% inquiry Acc;<br>+35% compliance|Efficient; retains 95% general<br>ability|
|27|Lin et al. (2025b)|Benchmark (FinLLM<br>Leaderboard)|42 datasets (IE, TA,<br>QA, RM, etc.)|Accuracy, F1, MCC,<br>ROUGE, etc.|GPT-4, LLaMA3,<br>Gemini ranked|Open benchmark; hallucination<br>risk|
|28|Lei et al. (2025)|Decoder-only (ZiGong<br>1.0)|Credit scoring,<br>fraud, insurance|Accuracy, F1, KS|Outperforms<br>baselines<br>(Acc=0.779 AU)|Data pruning ↑ reliability;<br>deployed in service|
|29|Lakkaraju et al.<br>(2023a)|LLM vs Rule-based|Personal finance<br>advisement|ISIP, ISA|LLMs fluent but<br>biased; rule-based<br>safer|Fairness issues in LLMs|
|30|Liu et al. (2023)|Data-centric LLM<br>(FinGPT)|Internet-scale fin.<br>data (34+ sources)|Accuracy, Efficiency,<br>Cost|Fine-tuning cost<br>_<_300 via<br>RLSP+LoRA|Democratizes FinLLM; data<br>noisy/time-sensitive|



- **Decoder-Only Architectures** : Decoder-only architectures (such as GPT-3.5, GPT-4) are becoming more frequently used in credit and financial prediction. Loukas et al. (2023) used GPT-3.5 and GPT-4 for banking intent classification and showed that GPT-4 achieved a Macro-F1 of 83.1 with a small sample size, while smaller encoders (MPNet) outperformed this figure (F1=91.2) with a larger sample size. These results demonstrate that decoder architectures, while performing well with small samples, are not always cost-effective. Babaei and Giudici (2024a,b) showed that GPT achieved an AUC of 0.61 for LendingClub loan approvals, and increased it to 0.67 with domain knowledge manipulation. This value was 0.75 with logistic regression. In-context examples are important for increasing transparency, but they have drawbacks such as API cost and inference latency. Lin et al. (2025a) reported that ChatGPT-3.5 is successful in providing reliable ratings and fraud detection in multi-source credit rating tasks, but it raises concerns about small dataset size and bias. All these results demonstrate that while decoding models are successful in generating adaptive and explanation information, they are inconsistent in their predictive performance and face challenges such as latency, cost, and bias. 

- **Hybrid and Augmented Pipelines** : In hybrid and enriched data pipelines, accuracy and interpretability are balanced by integrating LLMs with classical machine learning or data ingestion strategies. Combining BERT with XGBoost achieved higher accuracy and AUC compared to tree-based baselines. Their results showed that while textual credit descriptions provide complementary risk signals, they suffer from opacity and potential bias limitations. In their experiments analyzing financial news using GPT-4, they achieved 22% higher news text coverage compared to commercial providers. However, they carry the risk of hallucinatory output, which is a concern for high-risk financial applications. In their experiments, they present a retrieval-augmented generation (RAG) framework for sentiment analysis using financial news and tweets. The results indicate that the models show gains of 15–48% over baselines, but the computational burden is not trivial. In conclusion, all these studies show that hybrid pipelines increase predictive power and inter- 

pretability, but they also introduce complexity, cost, and monitoring challenges. 

- **Domain-Specific Financial LLMs (FinLLMs)** : Several domainspecific LLMs have been proposed to perform better in the context of financial language and risk. Liu et al. (2023) proposes FinGPT, a LoRA-based model using reinforcement learning. The tuning costs are under $300, and the accuracy is competitive, but the noisy and time-sensitive data are a challenge. Xie et al. (2023b) evaluates FinMA, a fine-tuned LLaMA variant, using the FLARE benchmark on credit scoring and different NLP tasks. While FinMA outperforms GPT-4 and BloombergGPT in sentiment and headline classification, it is weak in numerical reasoning. Lei et al. (2025) proposes ZiGong 1.0, which introduces pruning strategies (TracSeq) to improve reliability in credit scoring and fraud detection. Although it provides AUROC gains, the preprocessing overhead is high. Huang et al. (2024) proposes FinLLaMA/FinLLaVA, which integrates textual, tabular, and visual signals to extend LLMs. The results report that while it offers higher accuracy than GPT-4 and BloombergGPT, it is computationally intensive. Another study, Lin et al. (2025b), demonstrates performance variance and hallucination risks with the Open FinLLM Leaderboard. Guo et al. (2023), in their study FinLMEval, reports that fine-tuned encoder models perform well in data-scarce scenarios. Finally, while domain-specific FinLLMs demonstrate improvements in financial sensitivity, credit risk scoring, and multimodal integration, they also face challenges such as high computational costs and limited robustness to numerical reasoning tasks. 

- **Parameter-Efficient LLMs and Training Techniques** : It is aimed to reduce computational costs in LLM applications using parameterefficient training techniques in credit risk scenarios. A novel finetuning method is presented, targeting efficient parameter utilization in credit union applications (inquiry management and compliance checks). The results show a 27% increase in classification accuracy and a 35% gain in compliance prediction, while maintaining 95% of the model’s overall capabilities. Another study proposes adapting QLoRA-based tuning to LLaMA-3 models in Ni et al. (2024). The results show lower resource consumption and higher F1 and 

8 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 5** 

Comparative overview of 60 selected studies (Part II: Studies 31–60). 

|No Study<br>(Author,<br>Year)|Model Category|Dataset / Task|Evaluation Metric(s)|Reported Result(s)|Notes (Strengths / Limitations)|
|---|---|---|---|---|---|
|31 Lopez-Lira et al.<br>(2025)|Survey (LLM method-<br>ologies)|Broad finance apps (trading, risk,<br>ESG, QA)|Accuracy, F1, EM,<br>ROUGE, BLEU|Surveys SOTA; LLMs enhance fi-<br>nance tasks|i<br>Bridges<br>CS/Finance;<br>inter-<br>pretability challenges|
|32 Xie et al. (2023b)|Decoder-only (FinMA)|FLARE benchmark|Accuracy, F1, MCC|Outperforms<br>GPT-<br>4/BloombergGPT<br>(SA/head-<br>line)|Strong NLP; weak numeric rea-<br>soning|
|33 Huang et al. (2025)|LLM-assisted<br>(prompt/fine-tune)|Chinese SMEs (1972 firms)|Accuracy, F1|LLM<br>Acc=82.1%;<br>XG-<br>Boost=81.4%|Novel use; robust but limited<br>scope|
|34 de S. et al. (2024)|LLM+Taxonomy|Retail bank transactions (50k<br>businesses)|Coherence, F1|Coherence >90%; Gemini Pro-<br>F1=89%|First unsupervised taxonomy;<br>scalable|
|35 Huang et al. (2024)|Decoder-only+Multi-<br>modal|30 datasets (text, tabular, charts)|Accuracy, F1, ROUGE,<br>Sharpe|Outperforms<br>GPT-4,<br>BloombergGPT|Multimodal LLM suite; compute<br>intensive|
|36 Seshakagari et al.<br>(2025)|Encoder+Decoder<br>(FinBERT, GPT-4, T5)|Financial SA (5,322 news)|Precision, Recall, F1|GPT-4 F1=93.1%; FinBERT<br>F1=90.8%|GPT-4 best; FinBERT reliable;<br>T5 recall weaker|
|37 Babaei and Giudici<br>(2024b)|Decoder-only<br>(GPT,<br>Informed GPT)|LendingClub P2P loans|AUC|GPT=0.61;<br>Informed<br>GPT=0.67; LR >|LR baseline stronger|
|38 Wang et al. (2025)|LLM-assisted text min-<br>ing|Supply chain finance (China bus<br>sector)|Efficiency, Practicality|Outperforms trad. text mining|Democratizes analytics; de-<br>pends on web data|
|39 Lin et al. (2025a)|Decoder-only<br>(ChatGPT-3.5)|Credit rating (multi-source)|Accuracy, Predictabil-<br>ity|Reliable ratings; fraud detection|First ChatGPT rating; small test;<br>bias concerns|
|40 Hartomo<br>et<br>al.<br>(2025)|TabTransformer+XAI|BISAID & German Credit|Accuracy, AUC, PR,<br>XAI|Acc ↑ (86→89%; 93→95%)|Tackles<br>imbalance;<br>inter-<br>pretable SHAP|
|41 Yan et al. (2024)|Encoder+De-<br>coder<br>(BERT,<br>GPT-3,<br>RoBERTa,<br>BloombergGPT)|AML (simulated SBI)|Accuracy, Efficiency|LLMs<br>-><br>rule-based;<br>BloombergGPT best|Privacy/security concerns; sim-<br>ulated data|
|42 Gupta et al. (2024)|Long-context<br>LLMs<br>(GPT-4o)|Financial news (128k ctx)|Recall, F1|F1=0.99 (4k) → 0.40 (128k)|Shows brittleness; small test|
|43 Suresh et al. (2024)|Classical NLP pipeline|Banking (reviews, chats, feed-<br>back)|Accuracy, F1|Reveals preferences; tailored<br>services|Applied; classical NLP; India-<br>only|
|44 Ni et al. (2024)|LLM (QLoRA Llama3)|Earnings reports (501 S&P500)|Accuracy, F1, MCC|Outperforms GPT-4 baseline|Robust; limited horizon|
|45 Bond et al. (2023)|Decoder-only<br>(Chat-<br>GPT, Bard) vs Trans-<br>formers|Reuters news (2000–2020)|R<sup>2</sup>, MSPE, CER|LLMs _>_ FinBERT; correlated<br>with returns|Novel; risk of lookahead bias|
|46 Sun et al. (2024)|Actuarial Transformer|Auto insurance dataset (CAS)|Accuracy,<br>Inter-<br>pretability|Beats GLM, XGB, RF, NN; SHAP<br>transparency|First<br>actuarial<br>transformer;<br>domain-limited|
|47 Sabuncuoglu<br>and<br>Maple (2025)|Bias eval framework<br>(FinBERT)|Financial SA (GN/GS, Indian<br>news)|Accuracy,<br>Fairness,<br>XAI|Unbiased in GN/GS; drop in In-<br>dian news|Fairness issues revealed|
|48 Xie et al. (2024)|Benchmark (FinBen)|42 datasets, 24 tasks, 21 LLMs|F1, Acc, ROUGE, etc.|GPT-4 strong; Gemini better in<br>TG|Reveals reasoning/forecasting<br>gaps|
|49 Liu et al. (2024b)|Interpretability meth-<br>ods|FinTech (credit, risk, QA)|Interp. metrics, viz.|Graph/DFS/D-sep improve XAI|Conceptual; lacks large-scale<br>benchmarks|
|50 Liu et al. (2025)|Multimodal LLM (AT-<br>FinGPT)|Risk prediction (news, filings, au-<br>dio)|MSE, VaR|Outperforms FinGPT, GPT-3.5,<br>LSTM|First audio-text LLM; compute-<br>intensive|
|51 Chanda and Prabhu<br>(2023)|Secure Chatbot Frame-<br>work|Banking chatbots (expert inter-<br>views)|Security, Efficiency|Improved trust/security|Conceptual; no large-scale eval|
|52 Papasotiriou et al.<br>(2024)|Decoder-only (GPT-4,<br>CoT)|S&P500 equity ratings (2022–24)|Acc, Prec, Rec|GPT-4 > analysts/trad models|Rigorous JPM study; limited<br>horizon|
|53 Rizinski<br>et<br>al.<br>(2024)|Transformer+SHAP<br>(XLex)|FPB+SemEval vs LM lexicon|Accuracy, Coverage,<br>Efficiency|XLex<br>><br>LM<br>(+0.431);<br>XLex+LM +0.450|Transparent;<br>benchmark-<br>limited|
|54 Talha et al. (2023)|GPT-3.5/4<br>fairness<br>eval|German Credit; ML Fairness Gym|Rejection%, Profit, Re-<br>call|GPT-3.5<br>rej.+37%,<br>GPT-<br>4+49%|Shows fragility; fairness lens|
|55 Yu et al. (2023)|GPT+LightGBM<br>(GPT-LGBM)|LendingClub (loan texts + traits)|Accuracy, AUC, Recall|GPT-LGBM<br>><br>baselines;<br>RoBERTa distil helps|Improves<br>interpretability;<br>preprint|
|56 Kim et al. (2023)|Encoder (KoBERT, KR-<br>FinBERT) + Decoder<br>(GPT-3.5)|Korean analyst reports (16k)|Sentiment, Returns|KR-FinBERT > KoBERT; GPT-<br>3.5 competitive|Tackles “buy bias”; simulated<br>portfolios|
|57 Sanz-Guerrero and<br>Arroyo (2024b)|Encoder-only<br>(BERT<br>fine-tuned)|LendingClub (119k)|Accuracy, AUC, KS|Risk score improves discrimina-<br>tion|No manual annotation; opacity<br>issues|



9 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

**Table 5** 

Continued 

|No Study<br>Year)|(Autho|r,<br>Model Category|Dataset / Task|Evaluation Metric(s)|Reported Result(s)|Notes (Strengths / Limitations)|
|---|---|---|---|---|---|---|
|58 Guo et a|l. (2023)|Benchmark<br>(FinLMEval)|Nine financial NLP datasets|Micro-F1, Acc|Encoders > decoders (zero-shot<br>weaker)|Task-specific tuning still critical|
|59 Fallahgo|ul (2025)|Theory (Interp. Trans-<br>former AIPMs)|Asset Pricing (simulations)|Interp. metric, Proofs|Defines attention-based interp.;<br>universal approx|Theoretical; not dataset-driven|
|60 Zhang e<br>Zhang et|t al. (2023<br> al. (2023b|)<br>)<br>Retrieval-Augmented<br>LLM|Fin. SA (news, tweets + retriev|al) Accuracy, F1|+15–48% gains vs baselines|First RAG+instruction LLM;<br>high compute cost|
||**T**<br>Q|**able** **6**<br>uality and risk-of-bias|assessment questions.||||
|||Question|||Y|es<br> No|
|||Q1) Does the article exp<br> Q2) Is the dataset clearly<br> Q3) Are reproducibility <br> Q4) Does the article incl<br> Q5) Are bias/fairness co<br> Q6) Does the study asses<br> Q7) What is the publicat|licitly apply LLMs (or transforme<br> described (source, size, preproc<br> elements provided (code, hyperp<br>ude interpretability or explainab<br>nsiderations or demographic risk<br>s robustness (e.g., hallucination <br>ion type and venue (journal/con|r-based models) to credit ri<br>essing)?<br>arameters, evaluation proto<br>ility mechanisms (e.g., SHA<br> audits reported?<br> checks, adversarial testing)<br>ference, peer-reviewed, pre|sk tasks?<br> –<br> –<br>col)?<br> –<br>P, CoT, intrinsic models)?<br> –<br> –<br>?<br> –<br>print)?<br> –|–<br> –<br> –<br> –<br> –<br> –<br> –|



**Table 7** 

The research questions of the survey. 

|Research Question|Motivation|Section|
|---|---|---|
|Which LLMs are applied for credit risk assessment and how<br>are they categorized?|The purpose is to understand LLM architectures used for<br>credit risk applications and identify performance bottle-<br>necks and suitability for domain-specific tasks.|4.1|
|What types of data sources are used in LLM-based credit risk<br>applications?|The purpose is to evaluate how comprehensive mapping of<br>data sources provides model generalization and fairness.|4.2|
|How are explainability and interpretability addressed for<br>credit modeling in LLM-based credit risk applications?|The purpose is to evaluate how model transparency and ac-<br>countability are addressed in existing studies.|4.3|
|In which credit risk scenarios are LLMs most commonly ap-<br>plied and what are the assessment metrics?|The purpose is to identify common use cases of existing stud-<br>ies and thus provide insight into practical relevance, dataset<br>diversity, and reproducibility.|4.4|
|What are the challenges and research gaps in applying LLMs|The purpose is to guide future research by highlighting chal-|5|
|for credit risk assessment?|lenges and open questions.||



MCC performance compared to GPT-4. However, due to the limited evaluation horizon, robustness still needs to be verified. Consequently, while parameter-efficient approaches like LoRA and QLoRA offer cost-effective solutions, their robustness still needs to be investigated. 

- **Benchmarking and Evaluation Tools** : These initiatives are crucial for evaluating LLMs in financial tasks. The Open FinLLM Leaderboard presents a leaderboard that evaluates tasks such as information extraction, sentiment analysis, and quality assurance. The results show that GPT-4, LLaMA, and Gemini exhibit high performance, but exhibit hallucinations and reasoning deficits in credit tasks. This table, while not providing a repeatable testing environment, also demonstrates the fragility of LLM outputs. The benchmark suite FinLMEval is presented. In this study, the authors emphasize that encoder-based models outperform decoder models in credit tasks. Another study compares ChatGPT and Bard for fairness assessment. The authors report that LLMs, despite fluent responses, contain bias and inconsistencies in interpretability. Rule-based methods, despite their lower flexibility, provide more reliable results. All these benchmark studies emphasize the need for performance transparency and fairness auditing. 

##### _4.2. Data modalities (RQ2)_ 

Recent developments have also witnessed major improvements in the data processed for LLM-focused credit risk assessment. While traditional credit modeling was done with structured tabular data, various data modalities have now emerged, such as unstructured financial text, 

time series behaviors, multimodal data pipelines, and integration of synthetic data. Fig. 4 shows the taxonomy of data modalities. 

- **Structured Data** : Income levels, credit history, and financial ratios are important factors for credit risk assessment. A new framework, GPT-LGBM, integrates structured features into textual borrower narratives. Experiments on the LendingClub dataset show that GPTLGBM has higher accuracy and AUC compared to baselines and also contributes directly interpretable features. Similar studies, such as the FLARE benchmark (Xie et al., 2023b) and the Open-FinLLMs package (Huang et al., 2024), show strong predictive signals. However, two studies caution that the models may overlook borrower reliability and qualitative aspects. All these results suggest that structured data contributes to transparency and reproducibility. 

- **Unstructured Financial Text** : Loan narratives, analyst reports, and regulatory documents are frequently used data in credit risk modeling. [1a] reports that adding loan narratives in addition to structured data yields higher accuracy and AUC compared to structured feature models alone, but introduces opacity and bias. [23a] A study on SME loan applications in China also shows that borrower narratives generated using ChatGPT outperform human-written text. The results demonstrate the positive impact of unstructured text in capturing subtle risk cues. [24a] uses narrative narratives from auditors and managers for bankruptcy prediction. The hybrid LLM + VAE + TF-IDF frameworks outperform baselines and have strong predictive power. While all these studies highlight the importance of unstructured text in providing risk signals and in credit scoring systems, they 

10 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 



**Fig. 3.** Taxonomy of transformer-based model architectures for llm-driven credit risk assessment. 

also present new challenges regarding bias, interpretability, and data 

imbalance. 

- **Time-Series and Behavioral Data** : Another data type that is increasingly important in LLM-based credit scoring is time series and behavioral data. They introduce a pruning strategy called TracSeq. TracSeq filters temporal sequences in ZiGong 1.0 models and aims to increase reliability in credit scoring tasks. The results show that prediction accuracy increases compared to baseline values, but it incurs preprocessing overhead. They use behavioral and price-based time series data with the FinGPT framework in their study. The results highlight the potential for long-term stability reduction due to noisy and variable data sources while preserving fine-tuning costs. All these studies demonstrate that temporal information provides important clues in traditional credit scoring, but robust filtering is needed for interpretability and reliability. 



**Fig. 4.** Taxonomy of data modalities utilized in llm-based credit risk systems. 

- **Multimodal and Hybrid Inputs** : Credit risk scoring is expected to improve when numerical and behavioral features are combined. Huang et al. (2025) applies a multimodal LLM approach combining financial indicators and textual claim data. While this approach provides higher accuracy compared to single-mode baselines, it requires intensive computational resources. Yu et al. (2023) uses GPT-LGBM frameworks by combining borrower personality traits with structured financial variables. This hybrid approach makes the extracted features directly observable, increasing accuracy and interpretability. Zhang et al. (2023b) proposes a sentiment analysis system combining context-weak financial news and external information. Results show a 15–48% increase compared to baselines, demonstrating increased reliability by reducing hallucinations. All these findings demonstrate that multimodal integration improves performance at the expense of scalability. 

- **Synthetic and Augmented Data** : The primary goal of synthetic and enriched data strategies is to compensate for class imbalance and data scarcity. Cai (2024) generates synthetic data on Australian and German credit datasets using FinGPT. The results show that accuracy improves from 0.86 to 0.89 and F1 score improves from 0.84 to 0.87. These results demonstrate that models can be robust to small or imbalanced datasets with data enrichment. Inserte et al. (2024) fits synthetic Reuters headlines and SEC filings to LLMs for crosstask model generalization. The results show that synthetic fitting improves stability, but data realism concerns remain. In another study, Feng et al. (2023) presents a fine-tuned LLaMA2 framework, CALM, on nine datasets. While CALM demonstrates high performance, it also introduces persistent bias issues and harbors fairness concerns stemming from synthetic data. Consequently, synthetic and enriched data reduce imbalance by improving robustness. However, it also brings challenges such as financial representation and ethical use. 

##### _4.3. Interpretability mechanisms (RQ3)_ 

Interpretability is an important concept in LLM-based credit risk assessment due to its fairness and reliability. Recent studies aim to increase transparency with methods such as post-hoc methods, internal model designs, instruction setting and model checking strategies. Fig. 5 shows the taxonomy of interpretability mechanisms. 

- **Post-Hoc Explainability** : Govindaraj et al. (2023) apply SHAP and attention heatmaps to financial data to visualize local and global feature contributions. Their model achieved transparency and improved accuracy, outperforming standard transformers in MAE and RMSE. In Liu et al. (2024a) experiments on the HELOC dataset, they integrated ChatGPT commands with SHAP and LIME annotations, and 

11 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

produced clear outputs. This suggests that post-hoc integration of XAI with LLM could facilitate human agent interpretability of technical outputs. Wu et al. (2023) show that using LIME annotations and ChatGPT increases confidence in SME credit scoring. However, they also highlight limitations, such as imbalanced datasets. In another study, they show that combining TabTransformer with SHAP for the BISAID and German Credit datasets can increase AUC and accuracy, address class imbalance, and improve predictive explainability (Hartomo et al., 2025). In conclusion, these studies confirm the effectiveness of post-hoc tools in visualization and explanation, but their intrinsic interpretability remains more limited compared to the methods. 

- **Chain-of-Thought and Prompt-Level Explanations** : In this approach, interpretability is tailored to the chain of thought (CoT) stimulation or inference process. Dolphin et al. (2024) report a 22% improvement in emotion classification with CoT stimulation in GPT-4, but at the risk of hallucination. Loukas et al. (2023) show that CoT explanations perform close to/better than encoder-based baselines but have a high inference cost. Fatemi et al. (2024) confirm that models with smaller instructions can achieve competitive prediction accuracy and produce consistent results. Consequently, CoT explanations are more faithful than later-generation tools, but have higher costs and lower reliability. 

- **Intrinsically Interpretable Model Designs** : In these mechanisms, explainability is integrated into the model’s structure. Idbenjra et al. (2024) introduces the Logit Leaf Model, which generates controllable decision paths by combining segmentation trees and LLM estimations. The results show high AUC performance on a French consumer credit dataset. Tan and Kok (2024) proposes FinBERT-XRC, which emphasizes risk signals at the word and sentence level. The results are compelling, but the computational cost is high. Yu et al. (2023) designs GPT-LGBM, which combines borrower variables and personality traits, outperforming baselines. This internal design has higher complexity and efficiency than later-developed tools, while overcoming the “loyalty gap.” 

- **Robustness and Hallucination Mitigation** : Robustness mechanisms aim to stabilize annotations and reduce hallucinations to improve interpretability. Lei et al. (2025) propose a ZiGong framework using TracSeq pruning. This framework filters temporal sequences for consistent output in credit scoring. While the results demonstrate improvements in AUROC and annotation stability, there is a preprocessing overhead. Consequently, such approaches can improve interpretability by ensuring transparency and cross-run consistency. 

- **Fairness, Auditing, and Reproducibility** : Fairness and moderation mechanisms are used to assess the consistency and impartiality of LLM explanations. Lakkaraju et al. (2023a) reports that in a study comparing ChatGPT and Bard in fairness-sensitive applications, the output is fluid and user-friendly, but contains systemic biases and provides inconsistent recommendations. Gupta et al. (2024) analyzed GPT-4o behavior, revealing reproducibility issues and a decrease in F1 from 0.99 to 0.40 as sequence length increases. This suggests that even when models produce interpretable explanations, their reliability decreases. Finally, Lin et al. (2025b) reports that interpretability is fragmented and lacks cross-task metrics in the FinLLM Leaderboard. All these studies confirm that interpretability, fairness, and reproducibility are intertwined, and that biased or unstable explanations can undermine trust. 

- **Ethical, Regulatory, and Theoretical Dimensions** : In addition to enhancing performance, technical mechanisms must also comply with issues such as interpretability, ethical, and regulatory requirements. Studies in Yan et al. (2024) summarize the dimensions of accuracy, fairness, confidentiality, robustness, security, and sub-ethical compliance. This study emphasizes that even if a prediction performance is highly accurate, if it fails to en- 



**Fig. 5.** Taxonomy of interpretability mechanisms for llm-based credit models. 

sure confidentiality or fairness, it undermines trust and, therefore, makes acceptance difficult. Fallahgoul (2025) LLM connects the attention mechanism with the Markowitz optimization paradigm and integrates financial theory with interpretability. All these perspectives demonstrate that interpretability is related to transparency, as well as compliance with ethical principles and regulatory obligations. Future research should integrate ethical safeguards and theoretical frameworks to ensure credibility and institutional acceptance. 

##### _4.4. Application domains (RQ4)_ 

LLMs have recently been applied in a wide range of areas, including traditional credit scoring, fraud detection, sentiment prediction, roboadvisory, etc. Fig. 6 shows the Taxonomy of Application Domains for LLMs in Credit Risk Assessment. 

- **Retail and SME Credit Scoring** : When the literature is examined, it is seen that LLMs are used in various financial application areas such as peer-to-peer (P2P) lending and SME financing decisions. In their studies, Sanz-Guerrero and Arroyo (2024a) and Babaei and Giudici (2024a) use credit disclosures for borrower creditworthiness classification. In Yoon (2023), SME technology loans are evaluated with a GPT-based credit assessment mechanism. In another study, Huang et al. (2025), claims-based assessments are applied to nonfinancial data for SME default prediction. In Hartomo et al. (2025), the SHAP-TabTransformer model is applied to SME credit classification. Yu et al. (2023) combine structured financial data with extracted personality traits for credit assessment in their proposed GPTLGBM framework. In conclusion, studies show that LLM-based models outperform SME and individual loan applications compared to classical statistical methods. These findings suggest that LLMs can not only improve credit prediction performance but also enhance transparency for SMEs. 

- **Financial News, Sentiment, and Market Signals** : LLMs performed well in extracting market sentiment and event triggers even on unstructured financial data. Dolphin et al. (2024) and Dogra et al. (2022) used LLMs to predict risk from headlines with event triggers. In Bond et al. (2023) daily S&P 500 sentiment scores were generated using GPT-3.5, while in another study (Kim et al., 2023) analyst 

12 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 



**Fig. 6.** Taxonomy of application domains for llms in credit risk assessment. 



**Fig. 7.** Taxonomy of research gaps and future directions in llm-driven credit risk research. . 

tone was measured. Seshakagari et al. (2025) used GPT-4 to classify financial sentiment in a changing macroeconomic environment. All these studies indicate that LLM models outperform dictionary-based models by 15–48%. FinBERT and GPT-4 have expanded the scope of company coverage for news feeds, capturing investor sentiment more accurately. All these results highlight the potential for extracting early warning signals using market risks, while also highlighting the need to consider challenges such as hallucination risk and bias. 

- **Customer Service and Banking Operations** : Some studies in the literature focus on intent recognition and service personalization with LLMs. Loukas et al. (2023) performed service request classification with the Banking77 dataset, while in Suresh et al. (2024) customer sentiment analysis was used to support banking service personalization and credit decisions. LLM-based chatbots and support systems have achieved significant success (over 80%) in intent classification and complaint resolution. While studies have shown increased service efficiency in these systems, they also highlight issues such as security and data privacy concerns. 

- **Fraud Detection and Anti-Money Laundering (AML)** : FinGPT and ZiGong are two models used in fraud detection in credit and banking transactions (Cai, 2024; Lei et al., 2025). In JOEL (A.) credit unions predict fraud and default, while Yan et al. (2024) examine the performance of GPT/BERT-based models on AML, sanctions screening, and suspicious activity. For AML scenarios, LLM models are more effective at detecting suspicious transaction patterns than rulebased systems. Finance-focused models like BloombergGPT demonstrate this success for large-scale AML scenarios. However, all these systems remain limited in transparency and require explainability mechanisms. 

- **Investment, Trading, and Asset Management** : Walia et al. (2025) apply LLMs to bond yield prediction and extend the use of LLMs in finance. In Lin et al. (2025b) LLMs are used for SEC filing interpretation and sentiment-based trading, while Liu et al. (2023) evaluate the performance of FinGPT in robo-advisory and algorithmic trading bots. Other studies test the capabilities of LLMs using Open-FinLLMs in multimodal investment reasoning (Huang et al., 2024). Ni et al. (2024) report that QLoRA outperforms GPT-4 in stock prediction. LLMs, used in interpreting financial news and analyst reports, outperform traditional models in extracting sentiment signals. Studies highlight the potential of LLM models to increase profit margins in portfolio management while also emphasizing the importance of caution in the risk of hallucination and bias. All of this demonstrates the confidence-boosting potential of LLMs for investors. 

- **Taxonomy Building and Transaction Analysis** : In (de S. et al., 2024), LLMs are used to create financial taxonomy and explain transaction data to perform credit analyses, thus strengthening banking behaviors in credit and KYC (Know Your Customer) scenarios. LLMbased classifiers have demonstrated high performance in retail transactions and bank transactions. The success of models like Gemini Pro-in analyzing banking data is particularly noteworthy because they establish scalable taxonomy systems. All these findings demonstrate the potential for reducing classification costs with LLM-based systems, while indicating the need for operational optimization to reduce computational costs. 

- **Supply Chain and Sector-Specific Credit Evaluation** : In (Wang et al., 2025), LLMs use bid data and operational descriptions to evaluate China’s green transportation sector SME loans, helping non-specialist analysts understand feasible financing targets and strengthening the accessibility of LLMs. The reviewed studies indicate that LLM-based text mining performs well in assessing credit risk in supply chain finance. This is because these models analyze company reports and industry data. While these models yield more accurate results compared to traditional statistical methods, they also face challenges such as data dependency, sustainability, and reliability. 

- **Early Warning Systems and Multidimensional Risk Ratings** : ChatGPT was used for credit risk estimation scenarios where data is incomplete, such as start-ups (Lin et al., 2025a). This provides early warning and adaptive credit scoring capabilities for variable domains and applications. LLM-based early warning systems outperform traditional models because they utilize multidimensional indicators. Studies have shown that while these approaches offer the advantage of proactive risk management, they also face challenges such as bias and overconfidence in small datasets. 

13 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

##### **5. Research gaps and future directions (RQ5)** 

Although significant advances have been made in LLM-based financial applications (credit risk estimation, etc.), there are still research gaps and limitations that need to be investigated. Fig. 7 illustrates these limitations. This section examines research gaps in two subsections: Methodological Gaps and Application-Oriented Gaps. 

**Gap Derivation Process** : In this paper, to identify research gaps, each of the 60 studies examined was examined according to five evaluation dimensions: (i) model architectures, (ii) data formats, (iii) interpretability mechanisms, (iv) application domains, and (v) evaluation/benchmarking practices. Taking into account the previously described Table 6, we recorded whether each study explicitly reported robustness checks, fairness checks, efficiency measures, or interpretability mechanisms. Using all these indicators, we identified underrepresented areas. For example, 9 of the 60 studies included robustness tests, while 12 adopted fairness checks. 

##### _5.1. Methodological gaps_ 

- **Interpretability Gaps** : In the financial domain, LLMs largely remain black boxes because they rely on post hoc methods, such as SHAP and attention maps, for explainability (Govindaraj et al., 2023; Liu et al., 2024a). Causal or counterfactual reasoning is rarely encountered in the literature; explicitly counterfactual or closely related causal techniques were adopted in only three of the sixty reviewed studies (e.g., Yang et al., 2020). As a result, it is difficult to understand the true decision-making mechanism of the model in credit scenarios, and automatic taxonomy generation remains limited for taxonomy studies. 

- **Reproducibility and Robustness Limitations** : Only 9 of the reviewed studies report robustness tests (such as adversarial or stress tests), while 12 include a fairness/bias check. Furthermore, 7 studies report efficiency (for binary imputation and more details, please see Tables 4 & 5). Most of the experiments use small datasets (Loukas et al., 2023; Xie et al., 2023a), which limits their external validity. Furthermore, a few studies do not include standardized splits (e.g., Hartomo et al., 2025; Sideras et al., 2024; Wu et al., 2023), while some present standardized frameworks (such as FinLLM Lin et al., 2025b and FinLMEval Guo et al., 2023). Furthermore, there are studies that continue to show model fragility under reasoning style caveats. One example is Xie et al. (2023b) FinMA, where it is clear that instruction following can be fragile in long contexts. 

- **Bias, Fairness, and Hallucination Risks** : The literature reports that LLMs are prone to bias against demographic characteristics such as race, gender, and age (Lakkaraju et al., 2023a; Liu et al., 2024a). Furthermore, LLMs can produce false information, hallucinations, that are very close to the truth, and these remain a major threat to credit risk estimation (Chen et al., 2023). Few frameworks in the literature target fairness and hallucination reduction (Yan et al., 2024). 

- **Efficiency and Model Scaling** : While some studies address cost or latency, most do not provide systematic measurements. For example, Babaei and Giudici (2024a) reports that GPT models require less data to achieve the performance of logistic regression in credit scoring scenarios, but does not address API cost or inference latency. Another example is Liu et al. (2023), which reports that the cost of fine-tuning LoRA/QLoRA can be reduced to less than $300. However, only seven papers (out of a total of 60 papers) address quantitative runtime and energy consumption metrics. This demonstrates that efficiency over interpretability has not been investigated. Therefore, future studies should measure throughput (samples/s), latency (ms), and energy (Joules) for credit risk modeling, especially in resource-constrained edge deployments. 

- **Evaluation Benchmark Deficiencies** : Due to the diversity of datasets and scenarios, it is difficult to directly compare the performance of LLMs, a shortcoming noted in some literature studies (such as the assessment of the trade-off between interpretability and com- 

plexity) (Fallahgoul, 2025; Lin et al., 2025b). Tables 4 and 5 provide a detailed overview of the 60 studies reviewed in this paper. As can be seen, benchmark adoption remains fragmented. Studies such as Wu et al. (2023), Sideras et al. (2024), and Hartomo et al. (2025) do not include standardized distinctions or replicable criteria, while Lin et al. (2025b) and Guo et al. (2023) provide standardized assessments. 

##### _5.2. Application-oriented gaps_ 

- **Integration of Behavioral and External Signals** : Signals from unstructured data (news, social media content, etc.) can be incorporated into credit scoring models and used for forecasting purposes. Although theoretically potential, behavioral and external signals have not yet been widely integrated. 

##### _5.3. Future directions_ 

Based on the research gaps described above, the following areas of 

priority for future research are as follows: 

- **Low-Cost and Edge-Ready Credit Models** : Lightweight architectures can be developed and fine-tuned to ensure the most costoptimized deployment of LLM models in resource-constrained financial institutions. Furthermore, considering throughput (samples/sec), latency (ms), and energy consumption (Joules) in addition to accuracy when evaluating LLM models will accelerate the adoption of these models for real-world credit assessment scenarios. 

- **Sentiment-Driven and Behavioral Credit Signals** : While recent research has generally focused on textual and structured data, future researchers could also consider using behavioral signals such as repayment patterns, taking into account sentiment indicators such as analyst tone. This is important for assessing forecast robustness across different borrower groups. 

- **Domain-Specific Personalization** : Existing models provide uniform predictions, but credit scoring systems that can adapt to sectoral or regional differences are needed. This requires research into domain adaptation, transfer learning, and market-specific multilingual credit scoring systems. 

- **Evaluation Frameworks Beyond Accuracy** : Standard interpretability and reproducibility metrics are needed for systematic comparison. Future studies could develop methodologies such as fairness audits and hallucination stress tests for credit scoring tasks, taking these metrics into account. 

- **Regulatory Alignment and Ethical Protocols** : Because financial regulations prioritize transparency, future studies should develop model outputs that take into account regulations such as the Basel Accords and the EU Artificial Intelligence Act. This will ensure ethical and bias checks, thereby fostering public trust. 

##### **6. Conclusions** 

This paper presents one of the first systematic review and taxonomy of Large Language Model (LLM) based credit risk assessment approaches. The most relevant 60 peer-reviewed studies published between 2020 and 2025 are analyzed using the PRISMA methodology and a structured taxonomy is presented along four main dimensions: model architectures, data formats, interpretability mechanisms, and application domains. The findings confirm that although only coding and domain-specific FinLLMs are frequently used in this field, recent trends in hybrid pipelines, parameter-efficient tuning (e.g. QLoRA), and multimodal data integration are also used in credit scoring. Although SHAP and LIMA (post-hoc) are prevalent interpretability techniques, there is increasing interest in intrinsic and demand-based explanations. Apart from all these developments, there is still a need for further research in the areas of reproducibility, fairness control, robustness to hallucinations, and standardized assessment. We hope that this systematic review 

14 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

and taxonomy study will be a reference paper for researchers in transparent, reliable and field-compatible LLM-based financial risk modeling. 

##### **CRediT authorship contribution statement** 

**Muhammed Golec:** Conceptualization, Literature survey, Writing – original draft, Formal analysis, Visualization. **Maha Alabduljalil:** Supervision, Literature survey, Writing – review & editing, Methodology. 

Huang, H., Li, J., Zheng, C., Chen, S., Wang, X., & Chen, X. (2025). Advanced default risk prediction in small and medum-sized enterprises using large language models. _Applied Sciences_ , _15_ (5), 2733. 

- Huang, J., Xiao, M., Li, D., Jiang, Z., Yang, Y., Zhang, Y., Qian, L., Wang, Y., Peng, X., Ren, Y. et al. (2024). Open-finllms: Open multimodal large language models for financial applications. arXiv:2408.11878. 

Idbenjra, K., Coussement, K., & De Caigny, A. (2024). Investigating the beneficial impact of segmentation-based modelling for credit scoring. _Decision Support Systems_ , _179_ , 114170. 

- Inserte, P. R., Nakhlé, M., Qader, R., Caillaut, G., & Liu, J. (2024). Large language model adaptation for financial sentiment analysis. arXiv:2401.14777. 

Jayanthakumaran, M., Shukla, N., Pradhan, B., & Beydoun, G. (2025). A systematic review 

##### **Data availability** 

No data was used for the research described in the article. 

##### **Declaration of competing interest** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

##### **References** 

- Alonso, N. I. et al. (2024). Large language models in finance: Reasoning. _Large Language Models in Finance: Reasoning (December 08, 2024)_ . https://doi.org/10.2139/ssrn. 5048316. 

- Aziz, L. A.-R., & Andriansyah, Y. (2023). The role artificial intelligence in modern banking: an exploration of AI-driven approaches for enhanced fraud prevention, risk management, and regulatory compliance. _Reviews of Contemporary Business Analytics_ , _6_ (1), 110–132. 

- Babaei, G., & Giudici, P. (2024a). Gpt classifications, with application to credit lending. _Machine Learning with Applications_ , _16_ , 100534. 

- Babaei, G., & Giudici, P. (2024b). Gpt classifications, with application to credit lending. _Machine Learning with Applications_ , _16_ , 100534. 

- Bond, S. A., Klok, H., & Zhu, M. (2023). Large language models and financial market sentiment. _Available at SSRN 4584928_ . 

- Cai, Y. (2024). Overcoming data limitations in credit risk assessment with finGPTgenerated synthetic data. In _2024 International conference on electronics and devices, computational science (ICEDCS)_ (pp. 137–141). IEEE. 

- Chanda, R., & Prabhu, S. (2023). Secured framework for banking chatbots using AI, ML and NLP. In _2023 7th international conference on intelligent computing and control systems (ICICCS)_ (pp. 60–65). IEEE. 

- Chen, Y., Fu, Q., Yuan, Y., Wen, Z., Fan, G., Liu, D., Zhang, D., Li, Z., & Xiao, Y. (2023). Hallucination detection: Robustly discerning reliable answers in large language models. In _Proceedings of the 32nd ACM international conference on information and knowledge management_ (pp. 245–255). 

- Chen, Z. Z., Ma, J., Zhang, X., Hao, N., Yan, A., Nourbakhsh, A., Yang, X., McAuley, J., Petzold, L., & Wang, W. Y. (2024). A survey on large language models for critical societal domains: Finance, healthcare, and law. arXiv:2405.01769. 

- Choi, P. M. S., Huang, S. H., & Wang, Q. (2025). Large language models in finance: An overview.Choi, P. M. S., Huang(Eds.), S. H. _Finance and Large Language Models, Springer, Singapore._ (pp. 1–26). https://doi.org/10.1007/978-981-96-5833-6_1. 

- Dogra, V., Alharithi, F. S., Álvarez, R. M., Singh, A., & Qahtani, A. M. (2022). Nlp-based application for analyzing private and public banks stocks reaction to news events in the indian stock exchange. _Systems_ , _10_ (6), 233. 

- Dolphin, R., Dursun, J., Chow, J., Blankenship, J., Adams, K., & Pike, Q. (2024). Extracting structured insights from financial news: an augmented llm driven approach. arXiv:2407.15788. 

- Fallahgoul, H. (2025). Beyond black-box AI: A theory of interpretable transformers for asset pricing. _Available at SSRN_ . https://doi.org/10.2139/ssrn.5161644. 

- Fatemi, S., Hu, Y., & Mousavi, M. (2024). A comparative analysis of instruction fine-tuning LLMs for financial text classification. arXiv:2411.02476. 

- Feng, D., Dai, Y., Huang, J., Zhang, Y., Xie, Q., Han, W., Chen, Z., Lopez-Lira, A., & Wang, H. (2023). Empowering many, biasing a few: Generalist credit scoring through large language models. arXiv preprint arXiv:2310.00566. 

- George, M. (2024). Improving sentiment analysis of financial news headlines using hybrid word2vec-TFIDF feature extraction technique. _Procedia Computer Science_ , _244_ , 1–8. 

- Golec, M., Khamayseh, Y., Melhem, S. B., & Alwarafy, A. (2025). Llm-driven apt detection for 6g wireless networks: A systematic review and taxonomy. _IEEE Access_ , _13_ , 145271–145288. https://doi.org/10.1109/ACCESS.2025.3595665 

- Govindaraj, V., Jaganathan, H. V., & Prakash, P. (2023). Explainable transformers in financial forecasting. _philpapers_ . 

- Guo, Y., Xu, Z., & Yang, Y. (2023). Is chatGPT a financial expert? evaluating language models on financial natural language processing. In _The 2023 conference on empirical methods in natural language processing_ . 

- Gupta, L., Sharma, S., & Zhao, Y. (2024). Systematic evaluation of long-context LLMs on financial concepts. In _Proceedings of the 2024 conference on empirical methods in natural language processing: Industry track_ (pp. 1163–1175). 

- Hartomo, K. D., Arthur, C., & Nataliani, Y. (2025). A novel weighted loss tabtransformer integrating explainable AI for imbalanced credit risk datasets. _IEEE Access_ , _13_ , 31045–31056. 

of sentiment analytics in banking headlines. _Decision Analytics Journal_ , (p. 100584). JOEL, A. Optimizing large language models for financial risk assessment in credit unions. _researchgate_ . 

- Joshi, S. (2025a). A comprehensive review of gen AI agents: applications and frameworks in finance, investments and risk domains. _International Journal of Innovative Science and Research Technology_ , (pp. 1339–1355). https://doi.org/10.2139/ssrn.5133316. 

- Joshi, S. (2025b). Gen AI for market risk and credit risk learn agentically powered gen AI; gen AI agentic framework for financial risk management. _Gen AI Agentic Framework for Financial Risk Management (January 15, 2025)_ , _11_ (1), 709–723. 

Joshi, S. (2025c). Review of gen AI models for financial risk management: Architectural frameworks and implementation strategies. _Available at SSRN 5239190_ . 

- Junyan Wang, J., & Xiaoqi Wang, V. (2025). Assessing consistency and reproducibility in the outputs of large language models: Evidence across diverse finance and accounting tasks, arXiv e-prints, arXiv–2503. 

- Kalluri, K. (2024). Scalable fine-tunning strategies for llms in finance domain-specific application for credit union. 

- Kang, J.-W., & Choi, S.-Y. (2025). Comparative investigation of GPT and finBERT’s sentiment analysis performance in news across different sectors. _Electronics_ , _14_ (6), 1090. 

- Karami, A., & Igbokwe, C. (2025). The impact of big data characteristics on credit risk assessment. _International Journal of Data Science and Analytics_ , _20_ (pp. 4239–4259). 

- Khan, F. S., Mazhar, S. S., Mazhar, K., Dhoha, A. A., & Mazhar, A. (2025). Model-agnostic explainable artificial intelligence methods in finance: A systematic review, recent developments, limitations, challenges and future directions. _Artificial Intelligence Review_ , _58_ (8), 232. 

- Kim, S., Kim, S., Kim, Y., Park, J., Kim, S., Kim, M., Sung, C. H., Hong, J., & Lee, Y. (2023). Llms analyzing the analysts: Do bert and gpt extract more value from financial analyst reports? In _Proceedings of the fourth ACM international conference on AI in finance_ (pp. 383–391). 

- Kong, Y., Nie, Y., Dong, X., Mulvey, J. M., Poor, H. V., Wen, Q., & Zohren, S. (2024). Large language models for financial and investment management: Applications and benchmarks. _Journal of Portfolio Management_ , _51_ (2). 

- Krause, D. (2023). Large language models and generative AI in finance: an analysis of chatGPT, bard, and bing AI. _Bard, and Bing AI (July 15, 2023)_ , https://ssrn.com/abstract=4511540. 

- Lakkaraju, K., Jones, S. E., Vuruma, S. K. R., Pallagani, V., Muppasani, B. C., & Srivastava, B. (2023a). Llms for financial advisement: A fairness and efficacy study in personal decision making. In _Proceedings of the fourth ACM international conference on AI in finance_ (pp. 100–107). 

- Lakkaraju, K., Vuruma, S. K. R., Pallagani, V., Muppasani, B., & Srivastava, B. (2023b). Can llms be good financial advisors?: An initial study in personal decision making for optimized outcomes. arXiv:2307.07422. 

- Lee, J., Stevens, N., & Han, S. C. (2025). Large language models in finance (finLLMs). _Neural Computing and Applications_ , (pp. 1–15). https://doi.org/10.48550/arXiv.2404. 11898. 

- Lee, L. (2024). Enhancing financial inclusion and regulatory challenges: A critical analysis of digital banks and alternative lenders through digital platforms, machine learning, and large language models integration. arXiv:2404.11898. 

- Lei, Y., Wang, Z., Liu, C., & Wang, T. (2025). Zigong 1.0: A large language model for financial credit. arXiv:2502.16159. 

- Li, Y., Wang, S., Ding, H., & Chen, H. (2023). Large language models in finance: A survey. In _Proceedings of the fourth ACM international conference on AI in finance_ (pp. 374–382). 

- Lin, J., Lai, S., Yu, H., Liang, R., & Yen, J. (2025a). ChatGPT based credit rating and default forecasting. _Journal of Data, Information and Management_ , (pp. 1–24) arXiv:2501.10963. 

- Lin, S. C., Tian, F., Wang, K., Zhao, X., Huang, J., Xie, Q., Borella, L., White, M., Wang, C. D., Xiao, K. et al. (2025b). Open finLLM leaderboard: Towards financial ai readiness. arXiv:2501.10963. 

- Liu, X.-Y., Wang, G., Yang, H., & Zha, D. (2023). Data-centric fingpt: Democratizing internet-scale data for financial large language models. In _NeurIPS workshop on instruction tuning and instruction following_ . 

- Liu, Y., Bu, N., Li, Z., Zhang, Y., & Zhao, Z. (2025). At-fingpt: Financial risk prediction via an audio-text large language model. _Finance Research Letters_ , _77_ , 106967. 

- Liu, Z., He, H., Zhang, L., & Peng, C. (2024a). Leveraging XAI in prompt-based chatGPT for financial decision support. In _Proceedings of the international conference on digital economy, blockchain and artificial intelligence_ (pp. 255–259). 

- Liu, Z., Zhang, K., Zheng, Y., & Sun, Z. (2024b). Research on the application methods of large language model interpretability in fintech scenarios. In _2024 4th international conference on computer communication and artificial intelligence (CCAI)_ (pp. 526–531). IEEE. 

- Lopez-Lira, A., Kwon, J., Yoon, S., Sohn, J.-y., & Choi, C. (2025). Bridging language models and financial analysis. arXiv:2503.22693. 

- Loukas, L., Stogiannidis, I., Diamantopoulos, O., Malakasiotis, P., & Vassos, S. (2023). Making llms worth every penny: Resource-limited text classification in banking. In _Proceedings of the fourth ACM international conference on AI in finance_ (pp. 392–400). 

15 

_Expert Systems With Applications 306 (2026) 130941_ 

_M. Golec and M. Alabduljalil_ 

Luca, C. (2024). Optimizing large language models for financial risk assessment in credit unions. _researchgate_ https://www.researchgate.net/publication/388060268_ OPTIMIZING_LARGE_LANGUAGE_MODELS_FOR_FINANCIAL_RISK_ASSESSMENT_IN_ CREDIT_UNIONS. 

- Malaysha, S., El-Haj, M., Ezzini, S., Khalilia, M., Jarrar, M., Almujaiwel, S., Berrada, I., & Bouamor, H. (2024). Arafinnlp 2024: The first arabic financial nlp shared task. arXiv:2407.09818. 

- Nana, Z., Xiujian, W., & Zhongqiu, Z. (2022). Game theory analysis on credit risk assessment in e-commerce. _Information Processing & Management_ , _59_ (1), 102763. 

- Ni, H., Meng, S., Chen, X., Zhao, Z., Chen, A., Li, P., Zhang, S., Yin, Q., Wang, Y., & Chan, Y. (2024). Harnessing earnings reports for stock predictions: A qlora-enhanced llm approach. In _2024 6th international conference on data-driven optimization of complex systems (DOCS)_ (pp. 909–915). IEEE. 

- Nie, Y., Kong, Y., Dong, X., Mulvey, J. M., Poor, H. V., Wen, Q., & Zohren, S. (2024). A survey of large language models for financial applications: Progress, prospects and challenges. arXiv:2406.11903. 

- Omoseebi, A., Jhon, A., & Olabiyi, W. (2024). Large language models (LLMs) for financial security. _researchgate_ https://www.researchgate.net/publication/389354395_Large_ Language_Models_LLMs_for_Financial_Security/links/67bf4cd4f5cb8f70d5c08244/ Large-Language-Models-LLMs-for-Financial-Security.pdf. 

- Papasotiriou, K., Sood, S., Reynolds, S., & Balch, T. (2024). Ai in investment analysis: Llms for equity stock ratings. In _Proceedings of the 5th ACM international conference on AI in finance_ (pp. 419–427). 

- Rao, J., & Zhang, Q. (2025). Deep learning with LLM: A new paradigm for financial market prediction and analysis. _allmultidisciplinaryjournal_ . 

- Rizinski, M., Peshov, H., Mishev, K., Jovanovik, M., & Trajanov, D. (2024). Sentiment analysis in finance: From transformers back to explainable lexicons (xlex). _IEEE Access_ , _12_ , 7170–7198. 

- Roeder, J., Palmer, M., & Muntermann, J. (2022). Data-driven decision-making in credit risk management: The information value of analyst reports. _Decision Support Systems_ , _158_ , 113770. 

- Moraes, D.d.S., da Costa, P. B., Santos, P. T. C., de J. P. Pinto, I., Colcher, S., Busson, A. J. G., Pinto, M. A. S., Rocha, R. H., Gaio, R., Tourinho, G. et al. (2024). Tagging enriched bank transactions using LLM-generated topic taxonomies. In _Brazilian symposium on multimedia and the web (webmedia)_ (pp. 267–274). SBC. 

- Sabuncuoglu, A., & Maple, C. (2025). Identifying representation bias in large language models used in financial sentiment analysis. In _2025 IEEE Symposium on computational intelligence for financial engineering and economics (cifer)_ (pp. 1–7). IEEE. 

- Samson, S., & Rout, J. (2024). Comparative analysis of large language models adaptability to detect sentiments in financial domain. _Authorea Preprints_ . https://doi.org/10. 22541/au.172498784.43599501. 

- Sanz-Guerrero, M., & Arroyo, J. (2024a). Credit risk meets large language models: Building a risk indicator from loan descriptions in p2p lending. arXiv:2401.16458. 

- Sanz-Guerrero, M., & Arroyo, J. (2024b). Credit risk meets large language models: Building a risk indicator from loan descriptions in p2p lending. arXiv:2401.16458. 

- Seshakagari, H. R. B., Umashankar, A., Harikala, T., Jayasree, L., & Severance, J. (2025). Dynamic financial sentiment analysis and market forecasting through large language models. _International Journal of Human Computations & Intelligence_ , _4_ (1), 397–410. 

- Shobayo, O., Adeyemi-Longe, S., Popoola, O., & Ogunleye, B. (2024). Innovative sentiment analysis and prediction of stock price using finBERT, GPT-4 and logistic regression: A data-driven approach. _Big Data and Cognitive Computing_ , _8_ (11), 143. 

- Sideras, A., Bougiatiotis, K., Zavitsanos, E., Paliouras, G., & Vouros, G. (2024). Bankruptcy prediction: Data augmentation, LLMs and the need for auditor’s opinion. In _Proceedings of the 5th ACM international conference on AI in finance_ (pp. 453–460). 

- Staegemann, D., Haertel, C., Daase, C., Pohl, M., Abdallah, M., & Turowski, K. (2025). A review on large language models and generative AI in banking. In _Proceedings of the 7th international conference on finance, economics, management and IT business (FEMIB 2025)_ (pp. 267–278). SCITEPRESS. https://doi.org/10.5220/0013472600003956 

- Sun, T., Yang, J., Li, J., Chen, J., Liu, M., Fan, L., & Wang, X. (2024). Enhancing auto insurance risk evaluation with transformer and SHAP. _IEEE Access 12_ , 116546–116557. 

- Suresh, D. M., Vincent, G., Vijai, C., Rajendhiran, M., Com, M., Vidhyalakshmi, A. H., & Natarajan, S. (2024). Analyse customer behaviour and sentiment using natural language processing (NLP) techniques to improve customer service and personalize banking experiences. _Educational Administration: Theory And Practice_ , _30_ (5), 8802–8813. 

- Talha, C., Aafiya, H., & In, C. C. (2023). Understanding behaviour of large language models for short-term and long-term fairness scenarios. (pp. 52–61). 

- Tan, X. W., & Kok, S. (2024). Explainable risk classification in financial reports. arXiv:2405.01881. 

- Walia, J. S., Sinha, A., Srinivasan, S., & Unnikrishnan, S. (2025). Predicting liquidity-aware bond yields using causal GANs and deep reinforcement learning with LLM evaluation. arXiv:2502.17011. 

- Wang, D., Fan, J., Fu, H., & Zhang, B. (2018). Research on optimization of big data construction engineering quality management based on RNN-LSTM. _Complexity_ , _2018_ (1), 9691868. 

- Wu, Z., Dong, Y., Li, Y., & Shi, B. (2023). Unleashing the power of text for credit default prediction: Comparing human-generated and AI-generated texts. _4601317_ . _SSRN Electronic Journal. https://doi.org/10.2139/ssrn_ 

- Xie, Q., Han, W., Chen, Z., Xiang, R., Zhang, X., He, Y., Xiao, M., Li, D., Dai, Y., Feng, D. et al. (2024). Finben: A holistic financial benchmark for large language models. _Advances in Neural Information Processing Systems_ , _37_ , 95716–95743. 

- Xie, Q., Han, W., Zhang, X., Lai, Y., Peng, M., Lopez-Lira, A., & Huang, J. (2023a). Pixiu: A large language model, instruction data and evaluation benchmark for finance. In _Proceedings of the 37th international conference on neural information processing systems_ (pp. 33469–33484). 

- Xie, Q., Han, W., Zhang, X., Lai, Y., Peng, M., Lopez-Lira, A., & Huang, J. (2023b). Pixiu: A large language model, instruction data and evaluation benchmark for finance. In _Proceedings of the 37th international conference on neural information processing systems_ (pp. 33469–33484). 

- Xu, J. (2024). GenAI and LLM for financial institutions: A corporate strategic survey. _Available at SSRN 4988118_ . 

- Yan, Y., Hu, T., & Zhu, W. (2024). Leveraging large language models for enhancing financial compliance: A focus on anti-money laundering applications. In _2024 4th international conference on robotics, automation and artificial intelligence (RAAI)_ (pp. 260–273). IEEE. 

- Yang, L., Kenny, E. M., Ng, T. L. J., Yang, Y., Smyth, B., & Dong, R. (2020). Generating plausible counterfactual explanations for deep transformers in financial text classification. arXiv:2010.12512. 

- Yoon, S. (2023). Design and implementation of an LLM system to improve response time for SMEs technology credit evaluation. _International journal of advanced smart convergence_ , _12_ (3), 51–60. 

- Yu, L., Bai, X., & Chen, Z. (2023). Gpt-lgbm: A chatgpt-based integrated framework for credit scoring with textual and structured data. _Available at SSRN 4671511_ . _67_ , 12547–12578 

- Zavitsanos, E., Spyropoulou, E., Giannakopoulos, G., & Paliouras, G. (2025). Machine learning for identifying risk in financial statements: A survey. _ACM Computing Surveys_ , _57_ (9), 1–37. 

- Zhang, B., Yang, H., & Liu, X.-Y. (2023a). Instruct-fingpt: Financial sentiment analysis by instruction tuning of general-purpose large language models. arXiv:2306.12659. 

- Zhang, B., Yang, H., Zhou, T., Ali Babar, M., & Liu, X.-Y. (2023b). Enhancing financial sentiment analysis via retrieval augmented large language models. In _Proceedings of the fourth ACM international conference on AI in finance_ (pp. 349–356). 

**Muhammed Golec** is an Assistant Professor in the Department of Computer Engineering at Bo˘gaziçi University. He received his MSc and PhD in Computer Science from Queen Mary University of London under the prestigious Turkish Ministry of National Education Scholarship. During his postgraduate studies, he authored more than 40 peer-reviewed publications in high-impact journals and leading international conferences, including IEEE Transactions on Industrial Informatics, IEEE Internet of Things Journal, IEEE Transactions on Sustainable Computing, IEEE Journal of Biomedical and Health Informatics, ACM Computing Surveys, IEEE Transactions on Cognitive and Neural Networks (TCNN), and IEEE CCGrid. He gained industry experience by participating in Industry 4.0 projects as an Electrical and Electronic Maintenance Engineer at Sisecam, a global glass manufacturing company that combines theoretical knowledge with applied industrial expertise. He has also received multiple awards in recognition of his research and reviewing contributions: _Demonstrator of the Year_ (2024 Queen Mary University of London), _Reviewer Awards_ (2025 Wiley TETT, 2024 Elsevier IoT, 2023 Wiley TETT ), _Top Cited Article_ (2022–2023 Wiley SPJ). His research interests include Artificial Intelligence, Cloud Computing, and Security & Privacy. 



**Maha AlabdulJalil** is an Assistant Professor at Kuwait University since 2014. Her research interests primarily focus on similarity search applications, including duplicate detection and clustering. In addition to her research, she teaches courses in Parallel and Distributed Systems, drawing from her hands-on experience with the MapReduce framework, which was central to her thesis work. 

- Wang, J., Liu, G., Cheng, Y., Xu, X., & Li, Z. (2025). Leveraging internet-sourced text data for financial analytics in supply chain finance: A large language model-enhanced text mining workflow. _IEEE Transactions on Engineering Management_ . 

16 

