Constraints (2025) 30:35–61 https://doi.org/10.1007/s10601-025-09381-2 

**<mark>APPLICATION PAPER</mark>** 

# **Solutions and minimal conflict search for product configuration: a case study** 



<!-- Start of picture text -->
&<br><!-- End of picture text -->

### **Sebastian Velten**<sup>**1**</sup> to) **· Christopher Hamkins**<sup>**2**</sup> 

Received: 7 April 2025 / Accepted: 8 October 2025 / Published online: 29 October 2025 © The Author(s) 2025, modified publication 2026 

### **Abstract** 

We consider a product configuration problem for high-performance pumps and valves, where feasible configurations are defined by restriction tables. For this problem we propose a _Constraint Programming_ based model to find preferred solutions and to detect conflicts. We introduce an algorithm for enumerating minimal conflicts and their resolutions. The paper highlights two primary use cases: assisting sales personnel to resolve conflicts that arise during product configuration when not all the customer requirements can be met simultaneously and aiding product modelers in structuring and validating product models by finding the source of unexpected conflicts. The study also explores model preprocessing techniques to improve the solver performance. The algorithm is shown to be well suited for both real-time decision support and in-depth product model analysis in the cases at hand; the computational results demonstrate the practical applicability of the approach. 

**Keywords** Constraint programming · Product configuration · Minimal conflicts · Conflict resolution 

Christopher Hamkins contributed equally to this work. 

The project _Development of new methods, algorithms and software for configuration and selection of complex product systems_ would not have been possible without the grant from the European Union European Fund for Regional Development (EFRE file no. 84004994). 

> Sebastian Velten sebastian.velten@itwm.fraunhofer.de Christopher Hamkins christopher.hamkins@alum.mit.edu 

> 1 Fraunhofer Institute for Industrial Mathematics ITWM, Fraunhofer-Platz 1, 67663 Kaiserslautern, Germany 

> 2 KSB SE & Co. KGaA, Johann-Klein-Str. 9, 67227 Frankenthal, Germany 

```
1 3
```

Constraints (2025) 30:35–61 

36 

## **1 Introduction** 

Pumps and valves are ubiquitous in modern life ranging from small components in appliances such as washing machines or household heating systems, larger components in processes such as chemical production or machine cooling up to the largest units for example in municipal water supply or power plant boiler feed systems. The settings are quite diverse with the smallest pumps having a rated power of only a few watts but ranging up to tens of megawatts for pumps used in thermal energy production systems. 

High performance industrial pumps and valves are often produced to order for an exact customer specification in relatively low quantities; a typical order might have only four line items of a few pieces each. The customer requirements are quite diverse, hardly any two orders are exactly the same, even from the same customer. The challenge is to be able to fulfill the diverse requirements but still be able to deliver quickly and economically. This can be accomplished with an “assemble to order” paradigm: The products are assembled for each customer order from a standardized set of parts kept in stock or able to be directly manufactured from parts in stock. Many different possible components, suited to disparate pump uses and pressures, are combined into a single, finished product. The production is quick because only the final assembly step needs to be done, but the inventory cost is also minimized because only generic components are kept in stock. The variability to meet the customer specification comes from the possibility to combine parts in numerous ways. Many combinations of parts are theoretically possible, but some combinations are not feasible due to physical, engineering or even business constraints. 

During the sales process, it is necessary to solve the so-called product configuration problem: given customer specifications, select a generic product and an appropriate combination of parts by assigning values to features such that the customer specifications are best fulfilled and the combination is indeed possible to manufacture. Solving this problem in practice requires a dedicated decision support system, as the number of possible different combinations and complexity of the constraints is far larger than what can be efficiently handled manually. In addition, sometimes the choices needed to satisfy the customer specification conflict with each other. Due to the complexity of the product model, it is practically impossible for the user to resolve these conflicts manually. Even simply finding a consistent initial configuration is a challenge. Therefore, automated assistance for solution and conflict resolution is needed. 

In this paper, we describe the models and algorithms that are used to run such a decision support system as part of a product configuration software used by sales people who configure and quote the product in response to customer inquiries. After the product is configured, the output of the software is a customer quotation document with prices, standard delivery times and technical data sheets, all submitted to the customer as an offer. When an order is placed, the software is used to automatically generate the bill of materials (BOM), the work plans and the routings needed in the factory. The results of the configuration are transmitted to and persisted in the company’s enterprise resourse planning (ERP) system. Therefore, the configuration software is an integral and frequently needed business component which is designed to ensure that the complex rules are respected with regard to how the product can be assembled to all technical, pricing, lead time and business limits. Moreover, the component must also be ergonomic and easy to use. 

```
1 3
```

Constraints (2025) 30:35–61 

37 

The configuration software is also needed to assist the product modeling, i.e. the structuring of the possible pumps and valves into products by employees (product modelers) of the manufacturer. When configuring a particular pump or valve, the product is always selected first. After that, the specification is made based on the requirements of the customer. Product modeling defines the constraints in the model and specifies which combinations of different features of the product are allowed and which are not. During the development of the model constraints, it must be continuously checked whether feasible realizations of the product exist or if desired realizations (test cases) are feasible. The result of the process is a product model. 

Both during configuration of products by sales people (use of the model) and during development of the product model constraints (creation of the model), the decision support system is expected to find a feasible solution if one exists. If not, it should find a conflict resolution respecting as many requirements as possible and be able to explain the infeasibility by reporting which constraints do not fit together. 

Product configuration problems have been studied in the literature over the last decades. A comprehensive review of this work can be found in [1]. Different aspects of the problem have been investigated, in particular the establishment and maintenance of appropriate expert systems (see e.g. [2] and [3]), the design and resolution of product models (see e.g. [4, 5] and [6]), and the determination (see e.g. [7] and [8]) and resolution of conflicts (see e.g. [9, 10] and [11]) that may arise during the configuration process. 

In this paper we introduce a Constraint Programming (CP) based formulation for the product model with which feasible configurations for the given product configuration problem can be found or infeasibility can be detected. Moreover, for the second case, we describe two algorithms for determining minimal conflicts: an adaption of the QUICKXPLAIN algorithm of [12], which was previously used in the decision support system, and an algorithm for enumerating all minimal conflicts which uses a bottom up approach combined with a binary search for finding a single conflict (MinC_BBS). The latter explores the power set of the constraints of the CP formulation and is a refinement of the MARCO framework presented in Liffiton et. al. (see [13]). MARCO in turn is based on the hitting set duality between the set of all minimal conflicts and the set of all minimal conflict resolutions reported in [9] and [14]: a minimal conflict resolution (i.e. a set of constraints, which when relaxed, result in a satisfiable model) is a hitting set for the set of minimal conflicts, and the minimal conflicts are hitting sets for the set of minimal conflict resolutions. Therefore, this property is crucial for MinC_BBS as well. 

This paper is an extension of previous work of the authors with others reported in [15], which contains a short overview of the MinC_BBS algorithm and presents some initial results. Here, we give a detailed description of the context in which the model and the algorithms are applied, provide proofs of the correctness and present a more extensive computational study. 

The remainder of this paper is organized as follows. We first describe the product configuration system and various use cases ranging from finding valid solutions for sales quotations to providing analysis assistance for the product modelers. The elements used in the product model and their translation to a constraint programming formulation are then described. After that we proceed with the algorithms to find and resolve conflicts that can arise in a product model or in a product model extended by user decisions. We then describe how the CP model can be realized and optimized in the decision support system. Finally, we provide 

```
1 3
```

Constraints (2025) 30:35–61 

38 

computational results for finding solutions, analyzing and resolving conflicts, explaining decisions and show that the approach is very well suited for the use cases in actual practice. 

## **2 Use cases** 

The use cases of the decision support system mentioned in the introduction are described here in more detail. Similar use cases are also mentioned in [11] and pertain to specific roles. The **end- user** is the sales person using the product configuration software to make customer offers. The **product modeler** is a designer who is developing the initial product model so that it can be used in the product configuration by the end- user. 

1. _Solution:_ The **end- user** must find a valid product configuration that fulfills the customer requirements. He or she makes decisions for certain values of features as specified by the customer. The other features should be assigned their consistent preferred values. If no such solution is possible it should be reported that the decisions lead to a conflict. Normally the user proceeds feature by feature with the system responding after each choice, so a fast response is very important for this use case. 

2. _Resolution:_ The **end- user** makes decisions that lead to a conflict. He or she needs to be informed which of the decisions cause conflicts with the product model and be given suggestions for changing them to get a valid configuration. This is the same as the use case described in [12]. The feasibility constraints of the product model form the _background_ in this use case and may not be changed. The conflict resolution is found by relaxing one or more of the user decisions. Again, a fast response time is required, since this use case, like the one before, is based on direct interaction with the end- user. 

3. _Analysis:_ During the preparation of the product model, the **product modeler** tests it by assigning values intended to be a valid configuration but finds that no solution is possible. In this case, the product modeler needs to know which of the constraints in the model prevent the assignments to check their formulation for errors. In this use case the response time is of minor importance. The analysis is only done during the development of the product model after tests have failed. Manual analysis of the conflict often takes days, so if the system can automatically deliver a complete analysis in less time it is a great benefit. 

4. _Explanation:_ The **product modeler** discovers that a different value is chosen by the solver for an unconstrained feature than is expected or preferred. In fact, the value chosen will have been the most preferred one available and consistent with the user decisions and the solver’s prior decisions for the more important features. To explain the choice, the prior decisions and constraints which prevent the expected value can be found and reported. This use case usually arises only during testing and has more of an analysis character so run-time performance is not so important as well. With the analysis, the product modeler can change the prioritization of the features to result in the expected value being chosen. 

```
1 3
```

Constraints (2025) 30:35–61 

39 

## **3 Product configuration** 

For product configuration the rules for a given product are defined in a formal product model by product modelers. A product encompasses a large number of specific variants built from a defined set of parts, but similar enough to be described in a single product model. The complete portfolio of the company is composed of a large number of separate products each with its own product model and design rules. The product models are formally described in a variant configuration language using the company’s enterprise resource planning (ERP) system. To be used for decision support in the product configuration software the product model is interpreted and transformed into a CP based formulation. In the following the components of the product model are defined and explained. After that, in Section 4, a CP based formulation for a product model is introduced. 

### **3.1 Bill of materials** 

The product model can be considered as a tree-like maximal bill of materials (BOM). The nodes in the maximal BOM can themselves all have sub-nodes, but loops are not allowed and the depth is finite. The leaf nodes represent the specific parts to be taken from stock for the order. In general, the nodes in the maximal BOM are optional and each node may or may not be selected in a particular configuration via a selection condition that depends on feature evaluations (see also [4]). The constraints defined in the model for the parent nodes need to ensure that only consistent selection conditions for the child nodes can be true, as there may be some components that cannot be selected together. Defining the correct constraints in the parent node is an important job of the product modelers. 

A particular combination of parts fulfilling the requirements of a customer order (i.e. a solution of a product configuration process) is specified by an order-specific BOM. The order-specific BOM describes exactly what parts should be taken from stock to assemble the pump or valve, and what documentation such as material certificates or performance tests need to be supplied. To avoid errors and reduce effort, the order-specific BOM is automatically generated by the product configuration system and used in the ERP system. Figure 1 shows an example of a part of a maximal BOM (all nodes) and a specific BOM (without grayed out nodes), respectively. 

### **3.2 Feature domains and constraints** 

Formally, the product model includes a set of features _F_ describing the product properties. For each feature _f ∈F_ a domain _Df_ is given, comprising a finite set of possible values for _f_ . The domain of the product model is given by: 



In addition, the product model contains a set of constraints _CP_ that restrict the assignment of values to the features. This set of constraints remains the same for each end-user request (the _background_ ). The main constraints in _CP_ are restriction tables, conditional assignments and plant availability constraints. 

```
1 3
```

Constraints (2025) 30:35–61 

40 



<!-- Start of picture text -->
Product Model Pump<br>Top level nodes My screnasCasing Rotor= ‘AcceptanceTests ‘Seal‘Shaft ei cco<br>I<br>‘Subnodes, Casing cover shat Mechanical = Gland<br>‘Subsubnodes... a) Group ‘Seal Packing<br>= LL a Lo —,<br>Leaf nodes<br>Parts to Assemble= came Botut coo<br><!-- End of picture text -->

**Fig. 1** This example shows schematically a part of a tree-like maximal BOM. The graying-out of the Impeller Group node indicates that its selection condition is false; in this case all the children of the node are also not present in the final order-specific BOM. 

|**Table 1**Restriction table for two<br>|CNNCTN_EXCTN|CNNCTN_SIZE|
|---|---|---|
|features.|’WO’|’WO’|
||’PLUGGED’|’M8’|
||’PLUGGED’|’M10’|



A _restriction table_ lists all allowed combinations of values for a set of features; see Table 1 for an example. A combination of values not corresponding to a line in the table is not allowed. The restriction tables are assigned to nodes and are only active if their node exists. This can lead to nodes being rejected in a solution if the tables they contain cannot be fulfilled due to other constraints. 

**Remark 1** In CP literature, restriction tables are usually referred to as (positive) table constraints. We use the term restriction table as this is the name for these conditions in the underlying ERP-System. 

A _conditional assignment_ is an implication that a feature takes on a certain value if a condition holds. These conditions are modeled as Boolean expressions the terms of which are comparisons of features to certain values. In most cases conditional assignments refer to node existences. For example, node `U10` (dependencies for material testing) exists if `MTRLS_TSTNG == ’1’` and node `K10` (electric motor) exists if `(MTR == ’1’ || MTR_CNSTRNT_FK == ’0’) && (CMBSTN_ENGN == ’0’)` . 

In principle, the Boolean expressions used in conditional assignment could be arbitrarily complex combinations of boolean and comparison operators, but in the cases investigated they usually contained at most five or six terms. 

A further special case of conditional assignments are the _reference_ constraints which apply to features that become irrelevant for the configuration when a set of nodes does not exist. Such features are enforced to a value that indicates _intentional non-evaluation_ . An example is the acceptance test standard when no acceptance test was selected. This is simi- 

```
1 3
```

Constraints (2025) 30:35–61 

41 

lar to the concept of _active_ variables proposed by Mittal in [16], where all the constraints in which such variables participate are fulfilled by definition. In our case, the nodal existence controls whether constraints are active, and variables not participating in any active constraints are assigned the value for _intentional non-evaluation_ . 

The _plant availability constraints_ specify that depending on the selected plant of production certain values are not available for some features. These constraints are designed to reflect the fact that not all plants are able to produce all the variants. 

Furthermore, depending on the use case (see Section 2) an additional set of constraints _CU_ has to be respected. _CU_ does not belong to the product model but represents the customer requirements for a specific order. It contains direct choices of a value for features _f ∈F_ , limitations of allowed values to a specified set, or _node existence_ constraints. 

### **3.3 Preferred solutions** 

In the first use case _Solution_ (see Section 2)) the decision support system has the job to find the best solution that fulfills all the constraints. The preferred values for the _best_ solution are defined via a lexicographical priority. The features are ranked in order from most to least important; for each feature, the values are also ordered by decreasing preference. The preferred solution is one in which no feature has a more preferred feasible unassigned value that is consistent with the values assigned to the more important features. 

This definition of the preferred solution naturally lends itself to a solution search using decisions and backtracking– at each stage of the search, a decision is made to assign the most highly ranked, still unassigned feature its most preferred remaining value. The constraints are propagated, which possibly results in other lower ranked features being forced to some value, after which the next most highly ranked unassigned feature is determined. Backtracking and retraction of the decisions can occur when it is found that one is infeasible; then the next most preferable value is selected. As long as the most highly ranked unassigned feature is always decided at each step, there will be no more highly ranked feature that could have been given a more preferred value. Therefore, no further optimization of an objective is required during the search to find the preferred solution. 

## **4 The CP model** 

We model the product configuration problem using a _Constraint Programming_ (CP) approach (see, e.g., [17] for similar approaches). The CP formulation is the basis for finding feasible configurations (using a backtracking search based on feature and evaluation priorities, see Section 3.3) and for determining conflicts and resolutions. In the following we introduce the general formulation of the model. For some constraints we show how they can be formulated using Google’s OR-Tools CP library (see [18]). 

For each feature _f ∈F_ we define an integer decision variable _xf_ with domain _Df_ = _{−_ 1 _,_ 0 _, . . . , |f | −_ 1 _}}_ , where | _f_ | is the number of possible values for _f_ . The value _−_ 1 is used to represent _intentional non-evaluation_ of a feature. Furthermore, let _N_ be the node set of the tree-like maximal BOM. For each _n ∈N_ we define a binary decision variable _yn_ which is equal to 1 if node _n_ is selected in the solution and 0 otherwise. 

```
1 3
```

Constraints (2025) 30:35–61 

42 

The most important constraints are those for the table restrictions. For each node _n ∈N_ let _Tn_ be the set of its restriction tables. The set of all restriction tables is denoted by _T_ =<sup>∪</sup> _n∈N_<sup>_Tn_. A restriction table</sup><sup>_r∈T_constrains the possible combinations of values</sup> for a vector of _pr_ features ( _f_ 1 _, . . . , fpr_ ). The possible combinations of values of restriction table _r_ are given by a set _Ar_ of _qr_ integer vectors, each of length _pr_ . As the nodes are optional and for _n ∈N_ the restriction tables in _Tn_ need only to be satisfied if _n_ exists, we introduce a _local feature variable x_<sup>_n_</sup> _f_<sup>for each feature</sup><sup>_f∈Fn_, where</sup> _Fn_ is the set of features referenced in at least one restriction table in _Tn_ . Each of these local variables _x_<sup>_n_</sup> _f_<sup>has the same domain as</sup><sup>_xf_and we add the constraint</sup> 



to the CP formulation. Using [18] this _if-then_ constraint can be formulated as 



In (2), the expression `( ).Var()` defines a clause which is equal to 1 (i.e. `true` ) if and only if the inner constraint (in this case _xf_ = _x_<sup>_n_</sup> _f_<sup>) is satisfied. Thus, (2) enforces that</sup><sup>_xf_and</sup> _x_<sup>_n_</sup> _f_<sup>are equal if</sup><sup>_yn_= 1 and node</sup><sup>_n_exists.</sup> Given the local feature variables, the restriction tables are then included in the CP model by the following set of constraints 



Using [18] these constraints can be modeled applying the predefined constraint 

AllowedAssignment<sup>((</sup> _x_<sup>_n_</sup> _f_ 1<sup>_, . . . , xn_</sup> _fpr_ ) _, Ar_ ) _,_ (4) which ensures the vector of values assigned to ( _x_<sup>_n_</sup> _f_ 1<sup>_, . . . , xn_</sup> _fpr_ ) is an element of _Ar_ . In combination with (2) these constraints ensure that the restriction tables are respected if node _n_ exists. 

**Remark 2** Note that the usage of the local feature variables is necessary as the clause `( ).Var()` is not available for `AllowedAssignment()` (see [18]). 

As explained in Section 3.2 the conditional assignment constraints of a product model consist of a Boolean expression and depending on the evaluation of this expression a feature or node existence variable has to assume a particular value. In the CP model this is reflected by conjunctions and disjunctions of value assignments to feature and/or node existence variables and by using again the clause `( ).Var()` . Examples for conditional assignments of node existence variables are 



```
1 3
```

Constraints (2025) 30:35–61 

43 

and 



In this way, more complex conditional assignments for feature and node existence variables can be formulated as well. 

The remaining constraints of the product model (i.e. of the constraint set _Cp_ ) are the plant availability constraints. These constraints are formulated similar to (6). Let _x_ OPRTN_PLNTS be the feature variable modeling the operation plant and _f ∈F_ be a feature which must not take a certain set of values _Vf_<sup>_t_if</sup><sup>_x_OPRTN_PLNTS is set to a certain value</sup><sup>_t_. The correspond-</sup> ing plant availability constraint is then given by 



Depending on the use case (see Section 2) the final constraints of the CP model are the explicit user requirements _CU_ . The requests can lead to an assignment of a certain value _v ∈Df_ to a feature _f ∈F_ , i.e. 



the decision on the existence of a node _n ∈N_ , i.e. 



or further domain restrictions for a feature variable _f ∈F_ , i.e. 



## **5 Conflict determination and resolution** 

Especially in early stages of product modeling (use case _Analysis_ in Section 2) or when users specify many feature requirements (use case _Resolution_ in Section 2), the resulting CP model (i.e. _CP_ combined with _CU_ ) may be infeasible. In these cases, the automatic determination of conflicting constraint sets which are subset minimal ( _minimal conflicts_ , see definition in the following section) is crucial. They describe the core of the infeasibility and thus form the basis for resolutions that fulfill the specifications as far as possible. Depending on the use case, different subsets of _CP ∪ CU_ are explored for minimal conflicts. On the one hand, in the _Analysis_ use case, the goal is to obtain a set _CP_ without conflicts. Hence, minimal conflicts within _CP_ or subsets of _CP_ are desired. In the _Resolution_ use case, on the other hand, _CP_ is known to be conflict free and only conflicts within _CU_ are determined. 

```
1 3
```

Constraints (2025) 30:35–61 

44 

Note that, instead of an approach that can be used to directly determine conflict resolutions (see e.g. [9] and [11]), we decided to find the set of all minimal conflicts. The reason for this is that at least in the analysis use case the minimal conflicts are needed to better understand the reasons for infeasibility (see [19]). Moreover, we do not apply a network based approach for determining conflicts in product configuration like in [7] or [8] as these approaches require the explicit enumeration of all feasible solutions which is not practical in our case. 

In the following we first state some basic definitions and then describe an approach for finding individual conflict resolutions. This approach has initially been used in practice, but has two main drawbacks: it only finds a limited number of minimal conflicts, and thus resolutions, and it is not applicable to the analysis use case. Therefore, after that, we introduce an algorithm for enumerating all minimal conflicts which uses a bottom up approach combined with a binary search for finding a single conflict. Apart from being faster this approach can be applied to the analysis use case as well. 

### **5.1 Basic definitions** 

Let _C_ be a set of constraints. _C_ is a conflict if not all constraints in _C_ can be fulfilled at the same time. _C_ is minimal if no proper subset of _C_ is a conflict. Furthermore, if _C_ is a conflict, _R ⊂C_ is called a conflict resolution if _C\R_ is satisfiable and _R_ is minimal if no proper subset of _R_ is a conflict resolution. 

Moreover, let `S` be a set of sets. Then _H_ is a hitting set of `S` if _S_<sup>_′_</sup> _∩H̸_ = _∅_ for all _S_<sup>_′_</sup> _∈_ `S` . _H_ is minimal if no proper subset of _H_ is a hitting set. 

Let `MinC` be the set of all minimal conflicts and `MinR` be the set of all minimal conflict resolutions of a conflict _C_ . Then there exists a hitting set duality between these two sets of sets: any element of `MinC` is a hitting set of `MinR` and any element of `MinR` is a hitting set of `MinC` (see [9] and [14]). This property is essential for the algorithm presented in Section 5.3. 

### **5.2 Junker’s QUICKXPLAIN algorithm** 

In the conflict resolution use case the end-user would like to be informed which of the customer requests cause conflicts with the product model. Since this is the same use case as described in [12] a variant of the QUICKXPLAIN algorithm presented there was implemented first and applied in practice. In the following it is used as a baseline for comparison. 

The procedure as implemented is shown in Algorithm 1. It is a binary search which switches between attempting to retain as many user decisions (in order of priority) as possible, and relaxing as few as necessary, after which attempt is made to retain as many of those remaining as possible, etc. Algorithm 1 treats the CP solver (with the model introduced in Section 4) as a black box which simply reports if a solution can be found or if there is an infeasibility. 

```
1 3
```

Constraints (2025) 30:35–61 

45 



#### **Algorithm 1** QUICKXPLAIN (from [12]) as implemented here. 

Algorithm 1 requires that the constraints (in our case the user decisions) be prioritized. As an a priori ordering was not available, the decisions were prioritized based on the order in which they were made. Because of the step-by-step feature evaluation procedure executed by the end-user in practice, after the first conflict Algorithm 1 therefore reports “relax your last decision” as the resolution. This is sometimes unsatisfying for the end-user who would like to know what other decisions lead to the conflict. In this use case the product model is known to be feasible without user decision constraints and each feature value can occur in at least one solution. This is guaranteed by testing each value for each feature during product modeling. Hence, there are always at least two possible conflict resolutions. A single user decision of the form `FEATURE = VALUE` can never be in conflict with the model. Algorithm 1 was therefore applied again to find another relaxation of user decisions different than “relax your last decision” by giving the last decision the highest instead of lowest priority in the second application. 

In actual use, it was discovered that relaxations of single user decisions often lead to solutions, so it was attempted to first relax each decision individually to try to resolve the conflict. Only if fewer than two conflict resolutions were discovered was the full Algorithm 1 applied. 

### **5.3 Minimal conflict enumeration using a bottom up binary search approach** 

In this section we present an algorithm for enumerating all minimal conflicts using a bottom up binary search approach for determining a single conflict (MinC_BBS). Moreover, 

```
1 3
```

Constraints (2025) 30:35–61 

46 

it provides the set of all minimal conflict resolutions as a by-product. We use a bottom up approach since the minimal conflicts in our case are usually rather small (meaning the number of constraints in a minimal conflict is small compared to the total number of constraints in the model). 

The algorithm explores the power set of the set of constraints and is similar in most respects to the MARCO framework reported by Liffiton et. al. in [13]. In the following we first describe the components of our algorithm and prove its correctness and completeness. We then explain how the approach fits into the MARCO framework. 

### **5.3.1 The MinC_BBS algorithm** 

The MinC_BBS algorithm enumerates all minimal conflicts of a conflict _C_ by iteratively executing the following steps: 

- Determine an unexplored conflict _C_<sup>_′_</sup> _⊂C_ . 

   - Find one minimal conflict _C_<sup>_∗_</sup> _⊆C_<sup>_′_</sup> . 

- 

For the second step we propose a bottom up approach combined with a binary search which is detailed in Algorithm 2. The following lemma shows that Algorithm 2 is valid. 



**Algorithm 2** Bottom up binary search (BBS): determination of _one_ minimal conflict. 

**Lemma 1** Algorithm 2 terminates and returns a minimal conflict. 

```
1 3
```

Constraints (2025) 30:35–61 

47 

**_Proof_** First we show, that the initial execution of the while-loop 6-17 ends in line 10. During this execution the set of constraints _{c_ 1 _, . . . , cn_ max _}_ is always a conflict as _C_<sup>_∗_</sup> = _∅_ and either _n_ max = _N_ (and _C_<sup>_′_</sup> is a conflict) or _C_<sup>˜</sup> has been tested to be a conflict before executing Line 12. Moreover, the difference between _n_ min and _n_ max is continuously reduced until _⌈_ ( _n_ max _− n_ min) _/_ 2 _⌉_ is equal to 1, _n_<sup>_∗_</sup> = _n_ max and _C_<sup>˜</sup> = _{c_ 1 _, . . . , cn_ max _}_ , which has already been tested to be a conflict in the previous iteration. 

itself is a minimal conflict (and Algorithm 2 stops in line 19) or it is element of all minimal Let _n_<sup>_∗_</sup> 1<sup>be the final</sup><sup>_n∗_of the initial execution of the while-loop 6-17. Then, either</sup><sup>_cn∗_</sup> 1 conflicts of { _c_ 1 _, . . . , cn_<sup>_∗_</sup> 1 }. In the latter case, with the same arguments as above, the second execution of the while-loop 6-17 stops in Line 10 with a second constraint _cn_<sup>_∗_</sup> 2<sup>(</sup><sup>_n_</sup> 2<sup>_∗< n∗_</sup> 1<sup>)</sup> and so on. 

Algorithm 2 always stops in line 19 because if _n_ max = 1 (which will eventually be the case if _C_<sup>_∗_</sup> has not been a conflict in a preceding iteration) _C_<sup>˜</sup> = _C_<sup>_∗_</sup> _∪{c_ 1 _}_ , which has been tested to be a conflict in the previous iteration, becomes the new _C_<sup>_∗_</sup> . 

The final _C_<sup>_∗_</sup> is also a minimal conflict because either _|C_<sup>_∗_</sup> _|_ = 1 or for each execution _i_ of the while-loop 6-17 the superset 

_{c_ 1 _, . . . , cn∗−_ 1 _} ∪Ci_<sup>_∗_</sup> _−_ 1 



of _C_<sup>_∗_</sup> _\{cn_<sup>_∗_</sup> _i_<sup>_}_has been tested to be no conflict in the second last iteration of this execution. In</sup> expression (11), _cn_<sup>_∗_</sup> _i_<sup>is the constraint selected in</sup><sup>_i_and</sup><sup>_C_</sup> _i_<sup>_∗_</sup> _−_ 1<sup>the conflict set after the execu-</sup> tion _i_ -1. □ 

**Remark 3** In Algorithm 1 and 2 it may happen that a candidate constraint set has already been tested by the solver in a previous step. In the implementation of the respective algorithm, the results of the solution attempts are therefore cached to avoid redundant attempts. If a more tightly constrained attempt (i.e. one containing a superset of the constraints in the candidate) had a solution, then the candidate is feasible; if a more relaxed attempt (i.e. one for which the candidate contains a subset of its constraints) is infeasible, then so is the candidate. 

The caching was implemented using bitmaps to represent the constraints enforced in the candidates: the bit at position _n_ is 1 if the constraint _n_ is enforced and 0 if not. After each solution attempt the bitmap and its result were noted. Before a call to solve for a new candidate was done, we looped over the previous results, and for each, checked if the candidate 1 with bitmap _b_ 1 is a subset of a known feasible set 2 with bitmap _b_ 2 (if _b_ 1 _∧ b_ 2 = _b_ 1), and therefore feasible, or a superset of a known conflict 3 with bitmap _b_ 3 (if _b_ 1 _∨ b_ 3 = _b_ 3), and therefore a conflict. In the expressions, _∨_ and _∧_ are applied bitwise on the bitmap. 

Although the algorithms do not guarantee that all candidates proposed are “unexplored” in the sense of the MARCO framework’s Map in [13], checking candidates against the cache prevents redundant calls to solve for them, without the need to solve a CP problem to find an unexplored candidate. 

Based on Algorithm 2, the overall MinC_BBS approach is described in Algorithm 3. In each iteration of the while loop of this algorithm a minimal conflict for an unexplored conflict _C_<sup>_′_</sup> _⊆C_ is calculated. For the first iteration _C_<sup>_′_</sup> is set to the whole set _C_ . In later iterations _C_<sup>_′_</sup> 

```
1 3
```

Constraints (2025) 30:35–61 

48 

is always a conflict since in step 20, where _C_<sup>_′_</sup> is set, `H` only contains elements _H_ for which _C\H_ is a conflict. Furthermore, because of steps 9 and 14, an element of `H` can only be selected once in step 20, and, hence, _C_<sup>_′_</sup> is always unexplored. The following lemma and corollary show that the approach is complete (i.e. all minimal conflicts and minimal conflict resolutions are found). 



**Algorithm 3** MinC_BBS: Find _all_ minimal conflicts (and conflict resolutions) of a conflict. 

**Lemma 2** After the execution of Algorithm 3, `MinC` contains all minimal conflicts of _C_ . 

**_Proof_** Let H<sup>˜</sup> be the set of all hitting sets of `MinC` and assume that _C\H_ is feasible for all _H ∈_ H<sup>˜</sup> . In addition, assume toward contradiction that there exists a minimal conflict _C_<sup>ˆ</sup> _⊂C_ which is not contained in `MinC` . 

Then, on the one hand, as _C\H_ is feasible for all _H ∈_ H<sup>˜</sup> , _C ∩H̸_<sup>ˆ</sup> = _∅_ for all _H ∈_ H<sup>˜</sup> . On the other hand, as _C_<sup>ˆ</sup> is minimal, no element of _C_<sup>_∗_</sup> of `MinC` can be a subset of _C_<sup>ˆ</sup> and 



is a hitting set of `MinC` with _H ∩_<sup>ˆ</sup> _C_<sup>ˆ</sup> = _∅_ , which is a contradiction to the previous argument. Thus, a minimal conflict _C_<sup>ˆ</sup> _⊂C_ which is not contained in `MinC` cannot exist. 

Finally note that the argument still holds if only minimal hitting sets are considered and hitting sets for which _C\H_ is feasible are removed from `H` as 



```
1 3
```

Constraints (2025) 30:35–61 

49 

if _H ⊂H_<sup>_′_</sup> . □ 

**Corollary 1** After the execution of Algorithm 3, `MinR` contains all minimal conflict resolutions of _C_ . 

**_Proof_** Follows directly from `MinC` being complete and the hitting set duality of `MinC` and `MinR` (see Section 5.1). □ 

**Remark 4** Algorithms 2 and 3 benefit from a constraint _C_<sup>˜</sup> which is known to be part of all minimal conflicts. This situation may occur in Use Case 1 _Solution_ (see Section 2). In Algorithm 2 this information can be used to reduce the number of iterations by one by initializing _C_<sup>_∗_</sup> with _C_<sup>˜</sup> in Step 4. In Algorithm 3 checks for satisfiablity in Step 13 my be skipped if _C\H_ does not contain _C_<sup>˜</sup> . However, this improvement has not been implemented in the productive system as tracking this condition increases the complexity of implementation and the response times are perfectly satisfactory even without this extension. 

### **5.3.2 Integration in the MARCO framework** 

The MARCO framework presented in [13] enumerates the minimal conflicts of a set of constraints _C_ in the following way: 

- Solve the Unexplored Subset Problem (USP) to obtain an unexplored subset of _C_ . 

- If the unexplored subset is satisfiable, use a Grow method to extend it to a Maximal Satisfiable Subset (MSS) and add a BlockDown constraint to the USP to mark the MSS as explored. 

- If the unexplored subset is unsatisfiable, use a Shrink method to reduce it to a Minimal Unsatisfiable Subset (MUS), i.e. a minimal conflict, and add a BlockUp constraint to the USP to mark the MUS as explored. 

These steps are repeated until the USP is infeasible. An optimized version (also presented in [13]) uses a Maximal Unexplored Subset Problem (MaxUSP), which is an optimization problem and returns an unexplored subset of maximal cardinality. In this version the Grow method becomes obsolete and unsatisfiable subsets are found with a higher probability. The authors of [13] show that the approach is superior to previous approaches for determining all minimal conflicts. 

The algorithm proposed in Section 5.3.1 is a variation of optimized MARCO in which the solution of the MaxUSP is replaced by exploring _C\H, H ∈_ `H` . As these sets are complements of minimal hitting sets of the current set of minimal conflicts, they are always a solution to the MaxUSP. In addition, Algorithm 2 is a concrete implementation of the Shrink method considered in [13]. 

### **5.4 Resolution** 

Each _R ∈_ `MinR` , being a minimal hitting set of the set of minimal conflicts `MinC` , leads to a possible resolution which fulfills the original requirements as well as possible in the sense that all constraints of _R_ must be relaxed to obtain a feasible solution. After the relaxation 

```
1 3
```

Constraints (2025) 30:35–61 

50 

of _R_ the resolution is found by applying the prioritized backtracking search described in Section 3.3. Note that, depending on the size of the set of minimal conflicts `MinC` , there can be very many possible conflict resolutions. Therefore, at most a given number of resolutions is presented to the end-user and hitting sets containing constraints with low priority are considered first. 

## **6 Model preprocessing** 

The CP model and the algorithms for conflict determination presented in the previous sections are integrated in the product configurator described in the introduction. The configurator delegates requests for a consistent, preferred product configuration to product-specific solver model libraries. As there are only a manageable number of different products (several dozen new products per year) and the end user has no influence on the feasibility constraints _UP_ (and therefore on the main part of the concrete CP model), it makes sense to consider product-specific model optimizations and to build product-specific solver libraries. Together with preparing and caching solver objects during idle times this can achieve faster response times for end-user queries. 

### **6.1 Model preprocessing cycle** 

The product model can be retrieved from the ERP repository by a suitable software which interprets it and automatically generates the code needed to use the constraint solver library, which is subsequently compiled to a product-specific library. At the time of the model extraction and code generation, there are no particular run-time requirements. It would be perfectly acceptable to take hours or days for the process, if doing so results in better runtime performance of the final generated code to process user requests. In fact, it has been discovered that certain types of model preprocessing after the initial extraction do improve the final performance. 

This is the same situation as in [20], whose authors describe the use of _Binary Decision Diagrams (BDDs)_ to encode the complete set of solutions in a form that allows them to be found without backtracking in the final application. They report that BDDs are “particularly efficient” to encode the solutions and allow their retrieval in guaranteed polynomial time, although producing the BDD itself is a “hard” problem. The solution size of our models is hundreds of orders of magnitude larger than the example in [20] and the strong linking of the features would negatively impact the size of the result. Since the CP model solution was working satisfactorily and problems of this size will continue to be typical for the product models in the author’s company, the BDD approach was not investigated further. 

The model preprocessing is done using a preliminary, non-optimized code which simply exactly represents the formal model definition. With this code, the model can be investigated and potential for improvements be discovered. The findings are used to generate a second, equivalent but faster code: 

1. Read the model, generate and compile code that represents it exactly. 

2. Use the generated code to discover potential for improvement. 

```
1 3
```

Constraints (2025) 30:35–61 

51 

3. Use the discovered potential for improvement to generate a new, equivalent but better performing code. 

As is the case during constraint propagation, an initial model preprocessing can lead to additional knowledge that allows even more improvement. The preprocessing is therefore repeated with the improved model until no further optimization possibilities are discovered. 

In the following subsections the attempted improvements are described and evaluated. 

### **6.1.1 Domain reduction** 

If for the CP model for a specific product it turns out that a value in a variable’s domain can never be present in a feasible solution, then the value can simply be removed from its initially defined domain. The solver does not need to discover this type of dependency anew for each user request. The optimized model is generated with a reduced domain for the variable. 

In the extreme, this can lead to a variable’s domain being reduced to a single value.<sup>1</sup> In such a case, the variable can be removed and all of its usages in other expressions can be replaced by a constant Boolean “true” or “false” expression. 

We looked for such infeasible values with a decision procedure during the search to choose a variable that has not yet had all of its values appear in a solution (or be confirmed infeasible), and make a decision for one of the untried values. If a feasible solution is found, we note all the values that appeared in the solution as being feasible. If the decision was the first one made and leads to infeasibility, note the value as being infeasible. Continue until there are no more untried values. 

Note that after applying this procedure the resulting CP model is arc consistent. However, as we guarantee that each remaining domain value of each variable can be extended to a feasible solution, in general our procedure results in a stronger domain filtering than, for example, the AC4 algorithm (see [21]). 

### **6.1.2 Node elimination** 

It is sometimes the case that a nodal existence expression will never be true due to restrictions imposed by other constraints in the model.<sup>2</sup> Nodes may also never be present because they contain a restriction table that is infeasible together with other constraints outside the node. In both cases, the node and its restriction tables as well as its sub-nodes and their tables can be dropped from the model. Only the conditional assignment expressions need to be kept. This results in an equivalent but smaller model that runs faster because the unused tables cannot strengthen the propagation but still need memory and administration by the solver. 

To find infeasible nodes, the procedure to test the feature values is used in parallel; nodes appearing in solutions are noted as feasible. After all the feature values have been investi- 

> 1 If the domain were reduced to zero values it would mean that the model itself is infeasible even without user decisions, indicating an error in the product modeling. 

> 2 Nodes and their tables and sub-nodes are often reused in the ERP system product models by several different products to save modeling effort even when a particular product does not need the entire scope represented in the full model. 

```
1 3
```

Constraints (2025) 30:35–61 

52 

gated, any nodes not yet having appeared in a solution are individually constrained to be present and another solution attempt is made. Depending on the result (feasible or infeasible) the status of the node is learned. 

When a node is infeasible, its child nodes do not need to be investigated. They too can never be present in a solution since the existence of their parent node is a prerequisite for their own existence. 

### **6.1.3 Table line elimination** 

Lines in restriction tables that never appear in a feasible solution do not strengthen the propagation because they cannot eliminate more values from the variable domains. Removing them in advance can strengthen the propagation and can reduce the run-time needed to process the table and the administrative as well as memory overhead for the solver. 

During the preprocessing, the complete feasible permutations of the features in each table are therefore determined and compared with the restriction table itself. Since the table is active and restricts the feasible solutions, there cannot be more feasible permutations of the table’s features than the number of lines in the table. The permutation is therefore not problematic to determine in practice. If the table contains lines that do not appear in any solution, they can be removed from the table. 

When a value is eliminated from a variable’s domain during the preprocessing, all the lines in tables which reference the value can also be eliminated. 

A straightforward propagation of the dependencies in a table can lead to a need for backtracking during a solution search. By “straightforward propagation” we mean one in which the lines are removed from consideration which contain a value that is no longer in the domain of one the corresponding variables. After removing the lines, the remaining values in the table for the other variables are examined, and values no longer present are removed from their domains. The process repeats until no further reduction of a domain was found. This propagation method can require backtracking to discover dependencies. 

The following small example shows how table line elimination can help to eliminate this backtracking. Consider three variables _A_ , _B_ and _C_ which each have a domain consisting of the values 1, 2, and 3 and which are controlled by the table constraints shown in Table 2. Each of the tables pairs two variables and each column contains all the values in its variable’s domain. 

On the first pass of the propagation, no values are removed from any of the variable’s domains since each column contains all the values and no lines could be rejected. The initial propagation ends without having reduced any domains. 

It is easy to see in this example that the only possible solution is _A_ = 1, _B_ = 2, and _C_ = 3. If a trial decision _A_ = 1 is made, the propagation immediately leads to _B_ = 2 by Table AB, and then to _C_ = 3 by Table BC. Table AC has two lines rejected but the assignment fulfills the remaining line, so we have a solution. 

|**Table 2**Example table con-<br>|Table AB|Table BC|Table AC|
|---|---|---|---|
|straints requiring decisions and|_A_<br>_B_|_B_<br>_C_|_A_<br>_C_|
|backtrackin||||
|g.|1<br>2|1<br>2|1<br>3|
||2<br>1|2<br>3|2<br>1|
||3<br>3|3<br>1|3<br>2|



```
1 3
```

Constraints (2025) 30:35–61 

53 

A trial decision for either _A_ = 2 or _A_ = 3 on the other hand leads to _B_ = 1 respective _B_ = 3 by Table AB, and to _C_ = 2 respective _C_ = 1 by Table BC, but the propagation of Table AC leads to failure since all its lines are rejected and backtracking is needed to retract the decision. 

The table line elimination step would remove two lines from each table in this example and allow the dependency to be discovered without any backtracking. (In this case, the domain reduction step described above would also reduce the domains of these variables to the single actually allowed value, after which the tables would no longer be needed at all.) 

### **6.1.4 Feature equalities** 

In many of the real product models it happens that there are pairs of features with a 1:1 correspondence of their value assignments, either via a direct equality or a bijective mapping. In these cases we do not need to burden the solver with finding values for both of them. One of the variables can be used as a proxy for the other, whose value is determined in a preor postprocessing step outside the solver. All the uses of the second variable in constraint expressions or restriction tables need to be replaced by the proxy and its mapped values. The savings slightly reduce the overhead for the solver. 

### **6.2 Preparing and caching solver objects** 

To process a request, a solver object is created and all the constraints are added by calling the appropriate methods of the object. Since in Google’s OR-Tools CP library (see [18]) used here it is not possible to change or remove constraints after they have been added, the object is consumed to process the request and must be discarded afterwards and a new object created for the next request. Because of the separation of the constraints into an unchanging ”background” which is always the same, i.e. the basic product model, and the specific details of the user request, i.e. the user decisions, it is possible to prepare the solver object with the basic product model in advance of any user request. This is done asynchronously in a separate thread so that there is always a pool of prepared product models available when a user solution request arrives. The prepared product model is then supplemented by adding constraints with the details of the user decisions and the solution process is started. This typically saves 30 percent of the time otherwise required to process the request. 

## **7 Computational results** 

### **7.1 Test environment** 

The implementation used Google’s OR-Tools CP library version 6.7.4973 with the .NET API for C# and were run under the Windows 10 operating system. The computers used for the tests were one with an Intel<sup>®</sup> Core™i7-8850H CPU at 2.60GHz and another with an i7-13850HX CPU running at 2.10 GHz, each with 32 GB of RAM. 

The tests were done with 21 different product models whose size range is summarized in Table 3. 

```
1 3
```

Constraints (2025) 30:35–61 

54 

**Table 3** Size of the product models for tests. 

||Min|Average|Max|
|---|---|---|---|
|Features|35|227|442|
|Values|393|1260|2352|
|Nodes|13|84|177|
|Tables|41|295|663|
|Table lines|578|31726|126235|
|Table columns|93|761|1806|
|Table cells|1803|182155|708444|



**Fig. 2** Typical response times for solution use case 



<!-- Start of picture text -->
200 -<br>4<br>'<br>p<br>= =Conflict 1<br>150<br>_é Solution fi<br>E<br>=5 100 ae7<br>50 cee”<br>D<br>5<br>0% 20% 40% 60% 80% 100%<br>Fraction of fest Cases<br><!-- End of picture text -->

### **7.2 Solution** 

The solution relies on the specific search, constraint propagation and backtracking mechanisms of the solver package but is guided by providing decisions as required. A _decision_ in this context means the selection of a feature (or features) and assignment of a specific value (or range of values) for them. The solver continues the constraint propagation, possibly requesting new decisions and eventually either finds a solution or determines that there is none. 

In the present case, the decision mechanism selects the single most important unassigned feature and assigns its most preferred remaining value. This procedure guarantees that the lexicographical priority of preferences as described in Section 3.3 is enforced. 

When a solution is found, the response to the request is prepared and transmitted back to the sales configurator. 

The distribution of typical response times to answer a solution request are shown in Fig. 2. In the “conflict” case in this diagram, the response only reported that the request was infeasible but did not provide conflict resolutions. The vertical axis is the response time to answer the request, the horizontal axis shows the fraction of the test cases at or below the response time on the curve. The diagram is based on 2250 test cases taken from real user interactions on a variety of product models. 431 of the test cases were infeasible (conflicts) and 1819 admitted solutions. 

```
1 3
```

Constraints (2025) 30:35–61 

55 

The times reported in the diagram include the savings of using a prepared model pool (roughly 30%) and the model preprocessing described in Section 6 (roughly 10%). 

The response times are suitable for the _Solution_ use case where a new solution needs to be provided after each user feature selection. 

It is generally faster for the solver to determine that a request is infeasible than to provide a full solution for it, especially for complex models. In the diagram we can see that the response time curve for infeasible requests (conflicts) lies below the curve for providing solutions. 

Although the vast majority of the requests are answered quickly, at the far right of the diagram we see a sharp increase for certain specific requests where the solver only discovers the dependencies after significant backtracking. 

### **7.3 Benefits of the preprocessing** 

The benefits of the model preprocessing were tested by comparing response times to get solutions from the original and preprocessed models. 24,000 test cases were available based on genuine user interaction with the system. 

Since the response time for a specific request has a certain amount of scatter due to system operations such as memory allocation or file access for logging, each test was repeated five times with both the original and preprocessed model and the results summarized in a histogram of the solution time ratios; see Fig. 3. The preprocessing resulted in a solution time improvement of about 10% on average, but there is also considerable scatter with some requests taking longer than without the preprocessing. 

The benefits of the preprocessing depend on the quality of the original model. If the model did not have any of the problems described such as infeasible values, then the preprocessing would not change it. In practice, the modelers used the results of the preprocessing 



<!-- Start of picture text -->
Histogram of Solution Time Ratios<br>1400<br>1200<br>g 1000<br>s<br>% 900<br>x}<br>5 600<br>3<br>€<br>5<br>2 400<br>200<br>o-— —paamaltl Mijaensns._ I<br>0,4 06 0,8 1 12 14 16<br>Solution Time Ratio Preprocessed / Normal<br><!-- End of picture text -->

**Fig. 3** Histogram of solution time ratios. The bins have width of 2%. 24,000 test cases were used and each was repeated 5 times. 

```
1 3
```

Constraints (2025) 30:35–61 

56 

to improve subsequent versions of their model, after which further preprocessing would not provide additional benefits. 

### **7.4 Conflict resolution and analysis** 

In the following we demonstrate the performance of the MinC_BBS algorithm for the use cases _Resolution_ and _Analysis_ explained in Section 2. 

### **7.4.1 Finding minimal conflicts** 

An important part of the MinC_BBS algorithm is the binary search (Algorithm 2) which is a concrete implementation of Shrink from the MARCO framework. As a binary search, one would expect it to have an O(log(n)) performance in the number of solver calls, and an evaluation of its behavior confirms that this is the case, as seen in Fig. 4 here. The solid line is simply _y_ = 18 _· log_ ( _x_ ), the symbols show results for each minimal conflict found in the test cases. The symbols group around certain values on the x-axis since the initial conflict includes all the constraints in the model, and there were 21 different models with different specific sizes. 

Even when the initial conflict had over 800 constraints, it could usually be reduced to a minimal conflict with fewer than 50 solver calls. For these models, a solver call during the minimal conflict search took on average 13.5 ms; the 95<sup>th</sup> percentile is 54 ms, but as is typical for this type of problem, there is a large variation and some cases took much longer, up to 3 s per solver call. 



<!-- Start of picture text -->
x<br>3 100 -<br>=5 90 5<br>°<br>= 80 iedx “%-<br>E<br>=70 % xx<br>5 60 «x oo<br>EBE 50 erexx ee 5 eeeT<br>2 40 ae ae td me &<br>af6xax; i<br>g30 Xk va : z<br>S20 | fs :. J<br>= 10 gad x BF ae<br>5 ce © 3<br>2 ie ee<br>=<br>0 200 400 600 800 1000<br>Number of Constraints In Initial Conflict,<br><!-- End of picture text -->

**Fig. 4** Number of solver calls to find each minimal conflict as a function of the size of the initial conflict. 

```
1 3
```

Constraints (2025) 30:35–61 

57 

### **7.4.2 Resolution: comparison with modified QUICKXPLAIN** 

Figure 5 shows a comparison of the solution times for the MinC_BBS algorithm with the modified QUICKXPLAIN algorithm as a baseline for about 6000 test cases taken from actual conflicting end-user interactions in which the user decisions were in conflict with the product model. It can be seen that the MinC_BBS algorithm usually completes in 25% of the time that the baseline required. Further, in general it reports a larger number of possible conflict resolutions (potentially one for each minimal hitting set). At the far right of the figure we see that there are a few cases in which both algorithms required substantially more time, reminding us that the problem at hand remains NP-complete. 

Figure 6 shows the distribution of the number of conflict resolutions reported by the two approaches. Where the baseline algorithm typically found one or two resolutions, the new approach typically found two to five. Note that the new approach in general reports _all_ the possible resolutions. However, at most five are presented to the user. 

### **7.4.3 Analysis** 

The _Analysis_ use case has modelers trying to find which constraints in the model prevent what should be valid solutions. This is done at model design time as quality check on the model. 

The performance of the MinC_BBS algorithm for conflict analysis was demonstrated on 3700 test cases with conflicts, also taken from product modeler interactions. Figure 7 shows the processing time required vs. the number of minimal conflicts discovered. The solution time of up to a few minutes is perfectly acceptable for practical use in this case. 

The large number of minimal conflicts appears surprising at first but can be explained due to (necessary) redundancies in the table constraints. Every pair of features that appear together in more than one table will necessarily have all the same combinations in both tables, since otherwise the combinations appearing in only one table would be disallowed 



<!-- Start of picture text -->
8<br>7= = Modified QUICKXPLAIN<br>Ze —New BBS Algorithm aa<br>—<br>=< 5 =<br>gs oe -°<br>Fa3 on" ai<br>ze 3 a4<br>& eee<br>5 2 aa<br>3“<br>1ain<br>CY)<br>0% = ~—«'10% == 20% += 30% = 40% © 50% = GOK = 70% += 80% © 90% © 100%<br>Fraction of test cases<br><!-- End of picture text -->

**Fig. 5** Solution time for conflict resolution use case compared to ref. [12]. 

```
1 3
```

Constraints (2025) 30:35–61 

58 



<!-- Start of picture text -->
70%<br>Bed Modified QUICKXPLAIN<br>g Hea<br>3 bes lm New BBS Algorithm<br>8 40% He<br>2 eee<br>0 1 2 3 4 s 6 7 8 °<br>Number of conflict resolutionsreported<br><!-- End of picture text -->

**Fig. 6** Number of resolutions found for conflict resolution use case. 



<!-- Start of picture text -->
160<br>Ban a<br>140 00 0 cartaeetmntann| i?° 0<br>120 oo<br>8<br>100 2 6<br>= Be<br>Fa © 9 0 °<br>5 80 a<br>P=12§ 60 of2 28ofogobe 86© °°<br>”5 40| © og SooF805<br>SE o<br>20 gato o<br>0<br>0 100 200 300 400 500 600<br>Number of Minimal Conflicts Found<br><!-- End of picture text -->

**Fig. 7** Running time for conflict analysis use case with the MinC_BBS algorithm. 

by the other one, even though each table constrains a different set of overall features. The number of minimal conflicts grows exponentially with the number of such feature pairs involved. 

For the tests, a time limit of roughly 150 _s_ was enforced. When the time limit was reached, the MinC_BBS algorithm had always reported some minimal conflicts. Since every single minimal conflict needs to be addressed to resolve the overall conflict, reporting even one minimal conflict is a help for the product modelers. Moreover, the analysis can be executed 

```
1 3
```

Constraints (2025) 30:35–61 

59 

**Fig. 8** Rate of minimal conflict discovery with the MinC_BBS algorithm. 



<!-- Start of picture text -->
= 400<br>3<br>2H 350 7<br>& “a<br>E 300 “<br>3 250 Zl Fa<br>8 200 Yoo A<br>E 150 ——————a<br>= 100 eT __E ZB:<br>S ) POE Ez<br>3e50 WA g aa<br>&o<br>: " 100 150<br>Running Time [s]<br><!-- End of picture text -->

iteratively. Therefore, finding at least one minimal conflict (if there is any) in each iteration is sufficient. 

Moreover, the MinC_BBS algorithm has the desired property that it starts to report minimal conflicts directly and continues to find them at a relatively steady rate until either all are found or the time limit is reached. This can be seen in Fig. 8, in which the curves show the number of minimal conflicts found vs the running time for a number of test cases. The slope of the curve is the rate of minimal conflict production. The rate does vary with the complexity of the product model, but all of them show the behavior of steadily producing minimal conflicts. 

## **8 Conclusion** 

In this case study it has been demonstrated that modeling the practical configuration problem at hand using a _Constraint Programming_ (CP) approach is successful not only to find consistent solutions but also to analyze conflicts and propose resolutions for them. Apart from the software library, which provided all the necessary constraints and generic components for implementing the algorithms, a major advantage over other approaches, such as integer programming, was the possibility to formulate existing product models directly as CP models in an application-oriented manner and without significant overhead. 

The MinC_BBS algorithm for enumerating all minimal conflicts and all minimal resolutions of a set of constraints works well in practice not only to resolve conflicts in the user decisions but also to analyze the product models to find possible errors in them. For the _Resolution_ use case, it therefore replaces the modified QUICKXPLAIN approach that was used previously. Moreover, the MinC_BBS algorithm is a valuable tool for the product modelers in the _Analysis_ use case, for which there had not been adequate system support. 

One key reason why the algorithm performs so satisfactorily in this particular application is that the minimal conflicts usually have a rather small cardinality (less than 10 elements). The bottom up approach in Algorithm 2, which determines the elements of the minimal conflict step by step, therefore typically requires relatively few iterations. In addition, due to the problem structure (mainly restriction tables) and model preprocessing, the response times 

```
1 3
```

Constraints (2025) 30:35–61 

60 

of the solver are almost always very short. For applications with minimal conflicts of higher cardinality and/or more complex problem structures, the approach may be less suitable and Algorithm 2 should be replaced and/or Algorithm 3 adapted. 

However, at the author’s company, both the end users looking for conflict resolutions involving their decisions and the product modelers looking for problematic constraints that cause their test cases to fail use the tool so often that they have come to take its assistance for granted. 

**Author Contributions** Both authors contributed equally to this work. 

**Funding** Christopher Hamkins received partial financial support from the European Union European Fund for Regional Development (EFRE file no. 84004994). Open Access funding enabled and organized by Projekt DEAL. 

**Data Availability** The data supporting the findings of this study are confidential and cannot be made available. 

**Code Availability** The source code is confidential and cannot be made available. 

**Materials Availability** Not applicable. 

### **Declarations** 

**Competing interests** The authors have no relevant financial or non-financial interests to disclose. 

**Ethics approval and consent to participate** Not applicable. 

**Consent for publication** Not applicable. 

**Open Access** This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the material. If material is not included in the article’s Creative Commons licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/. 

## **References** 

1. Zhang, L. L. (2014). Product configuration: A review of the state-of-the-art and future research. _International Journal of Production Research, 52_ (21), 6381–6398.  h t t p s : / / d o i . o r g / 1 0 . 1 0 8 0 / 0 0 2 0 7 5 4 3 . 2 0 1 4 . 9 4 2 0 1 2 

2. Reinfrank, F., Ninaus, G., Wotawa, F., & Felfernig, A. (2015). Maintaining constraint-based conguration systems: Challenges ahead. In _CEUR workshop proceedings_ (Vol. 1453, pp. 39–46). RWTH Aachen. 

3. Felfernig, A., Zehentner, C., & Blazek, P. (2021). Corediag: Eliminating redundancy in constraint sets. arXiv:2102.12151 

4. Wang, L., Ng, W. K., & Song, B. (2011). Extended dcsp approach on product configuration with cost estimation. _Concurrent Engineering, 19_ (2), 123–138. https://doi.org/10.1177/1063293X11406750 

5. Benavides, D., Felfernig, A., Galindo, J. A., & Reinfrank, F. (2013). Automated analysis in feature modelling and product configuration. In J. Favaro & M. Morisio (Eds.), _Safe and secure software reuse_ (pp. 160–175). Berlin, Heidelberg: Springer. 

```
1 3
```

Constraints (2025) 30:35–61 

61 

6. Xie, H., Henderson, P., & Kernahan, M. (2005). Modelling and solving engineering product configuration problems by constraint satisfaction. _International Journal of Production Research, 43_ (20), 4455– 4469. https://doi.org/10.1080/00207540500142381 

7. Schubert, M., Felfernig, A., & Mandl, M. (2009). Solving over-constrained problems using network analysis. In _2009 international conference on adaptive and intelligent systems_ (pp. 9–14). IEEE. 

8. Schubert, M., Felfernig, A., & Mandl, M. (2010). Fastxplain: Conflict detection for constraint-based recommendation problems. In _International conference on industrial, engineering and other applications of applied intelligent systems_ (pp. 621–630). Springer. 

9. Reiter, R. (1987). A theory of diagnosis from first principles. _Artificial Intelligence, 32_ (1), 57–95. https://doi.org/10.1016/0004-3702(87)90062-2 

10. Felfernig, A., & Schubert, M. (2011). Personalized diagnoses for inconsistent user requirements. _AI EDAM, 25_ (2), 175–183. 

11. Felfernig, A., Schubert, M., & Zehentner, C. (2012). An efficient diagnosis algorithm for inconsistent constraint sets. _Artificial Intelligence for Engineering Design, Analysis and Manufacturing, 26_ (1), 53–62. https://doi.org/10.1017/S0890060411000011 

12. Junker, U. (2004). Quickxplain: Preferred explanations and relaxations for over-constrained problems. In _Proceedings of the 19th national conference on artifical intelligence_ (pp. 167–172). 

13. Liffiton, M. H., Previti, A., Malik, A., & Marques-Silva, J. (2016). Fast, flexible MUS enumeration. _Constraints - An International Journal, 21_ (2), 223–250. https://doi.org/10.1007/S10601-015-9183-0 

14. Stern, R., Kalech, M., Feldman, A., & Provan, G. (2012). Exploring the duality in conflict-directed model-based diagnosis. In _Proceedings of the AAAI conference on artificial intelligence_ (Vol. 26, pp. 828–834). 

15. Fischer, T., Hamkins, C., Velten, S., & Wortel, P. (2022). Determining and resolving conflicts in the configuration of high-performance pumps. In N. Trautmann & M. Gnägi (Eds.), _Operations research proceedings 2021_ (pp. 87–92). Cham: Springer. 

16. Mittal, S., & Falkenhainer, B. (1990). Dynamic constraint satisfaction. In _Proceedings eighth national conference on artificial intelligence_ (pp. 25–32). 

17. Falkner, A. A., Haselböck, A., Schenner, G., & Schreiner, H. (2011). Modeling and solving technical product configuration problems. _Artificial Intelligence for Engineering Design, Analysis and Manufacturing, 25_ , 115–129. 

18. Google (2020). Google’s or-tools. https://developers.google.com/optimization/ 19. Wotawa, F., Stettinger, M., Reinfrank, F., Ninaus, G., & Felfernig, A. (2015). Conflict management for constraint-based recommendation. In _CPCR+ ITWP@ IJCAI_ . 

20. Hadzic, T., Subbarayan, S., Jensen, R., Andersen, H., Møller, J., & Hulgaard, H. (2009). Fast backtrackfree product configuration using a precompiled solution space representation. _PETO_ . 

21. Mohr, R., & Henderson, T. C. (1986). Arc and path consistency revisited. _Artificial Intelligence, 28_ (2), 225–233. 

```
1 3
```

