Teaching Case 





# Implementing configure, price, quote in the supply chain: The case of Essemtec AG 

## Ariane Blumentritt<sup>1</sup> , Joachim Ehrenthal<sup>1</sup> , Benjamin Haueter<sup>1</sup> , Nadine Hitz<sup>1</sup> and Muhammad Sufian<sup>1</sup> 

Journal of Information Technology Teaching Cases 2023, Vol. 13(2) 246–254 © Association for Information Technology Trust 2022 

Article reuse guidelines: sagepub.com/journals-permissions DOI: 10.1177/20438869221139596 journals.sagepub.com/home/jittc 

### Abstract 

Essemtec AG develops, manufactures, and sells machinery and equipment to the electronics industry. This teaching case presents Essemtec AG’s experience with implementing a configure, price, quote (CPQ) system in its supply chain from the perspective of Tim, the Product Manager, who led the implementation project. This case helps students understand the value and organizational impact of a CPQ system on companies like Essemtec AG. 

### Keywords 

Configure, price, quote system, sales, mass customization, electronics industry, product management, disintermediation 

## Introduction to the case 

In June 2016, Tim, the Product Manager of Essemtec AG, a Swiss manufacturer of industrial automation equipment in Aesch, Lucerne, started a project to introduce new software that would help configure, price, and quote products for the B2B market. 

At that time, Essemtec AG had already been using varied information technology (IT) solutions for its different functional units. For production, manufacturing, accounting, supply chain management, and distribution, they used an enterprise resource planning (ERP) system. For sales and marketing purposes, a customer relationship management (CRM) system had been in place since 2015 to streamline all processes, from lead generation to offering a quote. However, software to replace the spreadsheet-based solution with which Essemtec AG’s internal sales department and its international distributors configured the machines to create quotes was still missing. 

Essemtec AG specializes in multivariant products. Its machines’ flexibility and modular expandability make it stand out among competitors; however, the machines’ configuration remained highly complex. The spreadsheetbased solution, which was in place, made the configuration and the entire process of creating a quote for potential customers a time-consuming and error-prone activity. Usually, the sales team depends on the product management department to configure complex machines correctly. 

To increase efficiency within the sales process and make it appear more modern to its sales intermediaries, Essemtec 

AG’s management team replaced the spreadsheet-based solution with a new configure, price, quote (CPQ) system. In the second quarter of 2016, they acquired a CPQ system from their existing CRM software supplier and entasked Tim, the Product Manager, with leading the implementation of this new system. 

## Essemtec AG at a glance 

Essemtec AG, founded in 1991, is a privately held company with a development and production site in Switzerland. The technology-oriented company’s core business is manufacturing technologically advanced and highly flexible automation equipment for the electronics manufacturing industry. 

Essemtec AG has approximately 90 employees in Aesch, Lucerne. It has direct operations in Switzerland, Germany, France, and the United States. Essemtec AG serves these markets directly. To capture additional international market share, it joined forces with around 30 distributors and sales agents worldwide. 

> 1School of Business, University of Applied Sciences and Arts Northwestern Switzerland, Windisch, Switzerland 

#### Corresponding author: 

> Joachim Ehrenthal, School of Business, University of Applied Sciences and Arts Northwestern Switzerland, Bahnhofstrasse 6, Windisch 5210, Switzerland. 

Email: joachim.ehrenthal@fhnw.ch 

247 

Blumentritt et al. 

Essemtec AG’s varied equipment is designed for small engineering offices and multinational companies. Its product portfolio comprises production equipment for electronic assemblies. Its high-tech solutions can be quickly adjusted to meet wide-ranging requirements. Thus, it can respond to customer requests from all over the world. It sells approximately 100 machines per year, of which, approximately 90% are sold abroad (Figures 1 and 2). 

Due to competition and pricing pressure, Essemtec AG had to reinvent itself repeatedly over the past decade, creating a unique selling proposition (USP), which was the flexibility and modular expandability of the machines. Consequently, the products became increasingly complex. 

## The current spreadsheet-based solution— problems preprogrammed? 

When Tim was assigned to this implementation project, he began by going through the sales process at that time and collected all the pain points of the spreadsheet-based solution in use. As the Product Manager, he was already in charge of managing Essemtec AG’s product line on a daily 



Figure 1. Headquarter of Essemtec AG in Aesch, Lucerne (Source: Essemtec, 2021). 



Figure 2. Essemtec pick-and-place machine during picking of a component (Essemtec AG, 2021). 

basis and various tasks at all stages of a product’s lifecycle, that is, from product development to marketing, including product pricing. Hence, Tim had the required knowledge and competency to implement the new CPQ software. 

## The multivariant product challenge 

Offering multivariant products is not only a great challenge for Essemtec AG’s development team but also its employees involved in the sales process. Sales staff must know the products that they want to sell. However, this is easier said than done, especially when dealing with highly complex machines. This can be well illustrated by the placement machine “Puma.” The basic machine can be extended with over a hundred different options. However, the issue is that certain options cannot be offered with others because they either make no sense or are technically not feasible. Moreover, there are options whose preconditions are the other options. This requires the fundamental technical expertise of each salesperson to ensure correct machine configuration. 

For simplicity, Tim used the example of a car to explain a multivariant product. This helped new employees understand the principles of a multivariant product: “If a customer wants to configure a car with an optional sport brake system, the wheels must also be larger; otherwise, the larger brake discs will no longer fit on the standard wheels. Larger wheels also require different tire dimensions, which in turn require different chassis. This implies that one option can have an impact on several other options.” 

## Overview of the sales process 

The sales process at Essemtec AG is divided into the following subprocesses: 

- Lead management process. 

- Opportunity management process, including quote creation. 

The goal is to convert each contact into a contactable lead, and eventually, into a customer. These two subprocesses are supported by CRM system. The lead management process contains the first touch point with potential customers. Since Essemtec AG is in the B2B market, the contact persons are usually the engineers of the corresponding companies using machines of the kind Essemtec AG produces. Leads are generated in different ways, such as at exhibitions, through social media platforms like LinkedIn, or through their website. Once a lead is generated, it is nurtured using various measures, such as newsletters and personalized e-mails containing information that might be interesting to potential customers. During this process, the potential customer requests a quote. In this case, the 

248 

<u>Journal</u> of Information Technology Teaching Cases 13(2) 

opportunity management process begins, and the lead transforms into an opportunity. The sales team then configures the machine according to the specific requirements of potential customers and creates a quote. The quote is then sent to a potential customer via e-mail. If the customer agrees with the quote, it is confirmed by means of a purchase order. The purchase order is then converted into a factory order, which also triggers the production process. 

After each stage of the manufacturing process, the products must pass a predefined quality test. A final quality check is performed after completion and before delivery. 

## Machine configuration and quote creation in detail 

To create quotes, Essemtec AG used a spreadsheet-based solution (see Figure 3) developed by an external company. The spreadsheet included all available sales items, which were the core data for the machine configuration. This means that the sales team could fill in the number of machine components needed to fulfill the requirements of the potential customer. 

For Essemtec AG’s highly configurable, multivariant products, the sales team witnessed a rapid increase in quote 

complexity. Thus, users of the spreadsheet-based solution needed to know all dependencies of all machine components and how they can be configured in combination with each other. The sales team felt increasingly overwhelmed by their superficial technical knowledge and high complexity. In the past, this led to machine configurations being offered to the customer that were technically not feasible at all or at a price that was too low because options were missing that would have been necessary as a precondition for the options offered. Consequently, in most cases, a proper configuration could only be achieved by consulting the product management staff, who had to rectify all problems and issues. In such cases, Tim sat with the sales team and reviewed the faulty configuration statement to identify the mistakes. Normally, this took a couple of hours, but occasionally, he had to spend half-a-day to check a configuration statement. Consequently, the workload for the product management department increased in addition to their usual tasks. In general, configuring the quote in the spreadsheet is very time-consuming for both the sales and product management staff. For a single-machine sale, both departments need to work closely and communicate with each other. Failing to do so increases the risk of misconfiguration, ultimately leading to failure costs. 



<!-- Start of picture text -->
a ee roe et ra oa veal oer oe<br>2. | mee se “He BE (sues? teal 2<br>rate DCm = . -%9 ea pam Inset Dette Format<br>1) Fox2)| [Customer name essemicc..”<br>P>__EUR [_tistprce rakraly ecepie ce<br>i Price<br>- to be added. it any:<br>RENS<br>‘ & Mise oe aEA<br>i3 rowerssBase Machine franceSoftware Option§ SpareiNOZz6S!See : der Options caaseese 2 SN [somGeneral Dispensing Optionsi _] Packin.<br>fs Forapposa weno ocr Ferenc comesve peoce sr Nava<br> Fowene ewase se essen pomsccuia — Gmieieve —PCeRATFn2 Navaan sx sn<br>eae Bietrs come perms Ilerorrsm —— westD<br>f' pemaro-wePe econcconssa | econ eeetetSacsien ee rereare swecas|e coservioPei — |fercasthepaneast<br>(re - sos eussien a rere en BA Nero<br>Pao corr esos ec Gee Prez New Soerven<br>3 corre = eassrteo canet perruase ear gece |=<br>oes Prose senor oanan carers Recereee — |[scrunas Geercae [feiss<br>3 pace woes. steps pea canert recrrreec — |[scevnae Seervae feiss<br>2 prowcour fa ecsieoss came Gavare, Perens cea Geena [fics<br>3aen eva Beard Feswesa | [eines Reema |fscessce Seevnee [ase<br>* owen eves ecsiene Pessrews | leunses moro —|[scorm coservrs 7<br>2 viet Sve reseoom | pessecome — |Ictnase tere eevee  oserverre<br>3 page sys Jrcsevore | pessreomr [faust nas ceovene server<br>spose rome lecseons | pcssremn — |Icunsor Peco fosvervsorn<br>sn |pcsup-coo [FXBAR20F |Pc-SLED-0016 PC-SSPEOO1T Jumvss6 PCCLMSB! VVHP02<br>» poses ces Jcsevow | rcssreane — |faanser ae rarer<br>— Se a ree stn aan<br>ovo! EN SED ELIE KIKI I ——_<br><!-- End of picture text -->

Figure 3. Spreadsheet quote solution (source: internal document). 

249 

Blumentritt et al. 

Furthermore, the configuration of the quote using the spreadsheet-based solution was error-prone. If there was just one type of logic error in the spreadsheet, the external company that developed the spreadsheet solution had to be involved, and the product management team had to ensure that all spreadsheets were replaced worldwide. This is because all distributors worked with the spreadsheet. Since the change process was tedious, the spreadsheet was updated only on an annual basis. This also led to Essemtec AG knowing that many configurations were incorrect and that each configuration had to be double-checked by the product management team. In case of misconfiguration, the salesperson, or even the customer, had to be informed to set it right. 

## Characteristics of international sales 

Essemtec AG partners with approximately 30 distributors and sales agents and serves indirect markets. Thus, approximately 40% of sales revenue is generated through sales intermediaries and 60% through direct sales. Nobody who works in an international environment has not heard of the following: “International sales are not comparable to local sales.” Tim wanted to know what this meant and asked Michael, the Director of Sales, to explain it to him in more detail. Tim usually works very closely with Michael and had already accomplished several projects with him. Michael had more than two decades of experience in industry and international sales. He agreed that international sales differed significantly from local sales. The main difference lay in the physical distance as well as differences in language and culture, which should not be underestimated. Michael believed that the language barrier makes it more difficult to get in touch with potential customers because either the 

communication is hindered or a certain foundation of trust always seemed missing. Selling a product and capital goods is always a matter of trust. To bridge this gap, Essemtec AG relied on local sales intermediaries that are closer to customers. A sales intermediary usually sells not only products from one supplier but also from various other suppliers. This means that its products are in direct competition with those of its competitors. Besides lucrative commissions, sales intermediaries also expected a convenient method in terms of quote creation. The simpler this process, the more frequently Essemtec AG’s products would be considered for new sales projects. 

## New CPQ software—helper in need? 

In June 2016, Essemtec AG’s management team accepted the offer of an existing CRM solution provider to introduce professional CPQ software. Tim and Michael were part of the management team led by the CEO. The goal of the new system was to resolve all the problems Essemtec AG had with the spreadsheet-based solution in creating a quote and to ensure a more modern appearance, especially for their distributors. Finally, the new system had to work flawlessly with the existing CRM and ERP systems. Figure 4 shows how the new CPQ system was integrated into Essemtec AG’s IT system. 

The management also knew that among their competitors, only some big players were already using CPQ software, and that they would be clearly ahead of companies of their size in this regard. 

## CPQ explained 

Tim remembered how the CRM supplier introduced Essemtec AG’s management team into the CPQ system. 



<!-- Start of picture text -->
s 9 Fd<br>Ooa 1S) lu<br>= Opportunity Products & Components - Sales Order<br>Orders:Sales a |<br><!-- End of picture text -->

Figure 4. System integration (own depiction). 

250 

<u>Journal</u> of Information Technology Teaching Cases 13(2) 

Configuration, price, quote (CPQ) software is a term used in the B2B industry to describe software systems that help sellers quote complex and configurable products. CPQ is a web-based application in which system modelers enter a set of rules under which they are allowed to configure the product. The software configures a product (often with visualization capability) and transfers the configuration data to e-commerce systems. Most CPQ system providers have significantly developed over the years. Modern CPQ systems can partially remedy the media disruption between sales and production, as relevant information from the configuration flows directly into the production process. 

The product configurator within the CPQ software closes the gap between sales and technical production. Sales configuration and product determination are not built up in bills of materials or individual components, but these are designed or translated in such a way that they can be understood by sales and the customer. The product configurator automatically converts the product configuration into a technically feature-driven configuration suitable for immediate production. The CPQ software is ideal for multivariant products. It is often used to implement mass customization. 

Mass customization is the capability of manufacturers to produce a high volume of different products for a relatively large market. Furthermore, it can adjust products and process design quickly to suit customer demands without the interchange of high costs, incorrect delivery, and reduction of quality. Customization has four dimensions: high-volume customization, customization of cost efficiency, customization responsiveness, and customization of quality. These capabilities allow manufacturers to offer tailor-made products efficiently. Furthermore, it has widely been acknowledged that mass customization and product innovation can improve operational performance and customer satisfaction (Qi et al., 2020). 

## Implementing CPQ at Essemtec AG 

July 27, 2016—a day that Tim still remembers vividly. This was the day when the project kick-off for the new CPQ software took place. The project team included the owner of the CRM system, owner of the ERP system, two representatives of the external software supplier, a representative of the sales team, and Tim as the project leader and project owner. A review team was also included, and it consisted mainly of management team members, including the CEO and Michael, as the Director of Sales. Figure 5 shows the chart of the project organization. 

The project duration was estimated to be 6 months. Since this kind of software was completely new to the company, there were many unknown challenges at this stage of the project. Furthermore, CPQ software needs to be integrated into the existing Information and Communications 

Technology (ICT) landscape to ensure a single point of truth regarding the database. Within the project, one had to deal with various stakeholders, such as sales, ICT, and product management departments. The sales department was the socalled internal customer; therefore, they had certain requirements to be covered by the project. The product management department had knowledge of the products that had to be mapped using the software. The ICT department was responsible for providing suitable infrastructure to ensure proper operation of the software. 

## Concerns and expectations of functional units 

During the roll-out phase of the software, Tim consulted all internal and external stakeholders and collected their expectations. To ensure employee engagement, all involved departmental representatives could contribute with their ideas at each project stage. Before the CPQ software was implemented, various concerns had to be resolved. 

The product management team was open to a better solution because it had bad experiences working with the spreadsheet. Employees who were directly involved in the process welcomed this solution. However, there were also some critical voices of employees who were not directly involved in the process. According to their understanding, they wondered why such expensive software had to be implemented because this would not lead to higher sales. 

Essemtec AG’s distributors and agents praised the new initiative because it would increase the efficiency of the sales process. 

## Challenges 

The first challenge for Tim was to retrieve core data, such as article master data and customer master data, from the existing ERP system. During the implementation project of the CRM system in 2015, a bidirectional interface was created between the ERP and CRM systems. Since the CRM system and the evaluated CPQ software came from the same software vendor, there was already a standardized interface available. This interface was slightly adapted according to specific requirements. 

The second challenge was to gather all related product know-how distributed throughout the company. This knowledge had to be centralized in the CPQ software by a visual model that included all the rules and conditions of the multivariant products. This visual model was called a set of rules and had to be created for each product and product option. Figure 6 shows a set of rules for a simple aluminum box that is offered as an option for a fully automated storage system. 

The third challenge was the user interface, particularly the manner in which a machine could be configured. During the project, the project team decided to implement it in a 

251 

Blumentritt et al. 



<!-- Start of picture text -->
| nn<br>Project Leader<br>"Tim"<br>Owner CRM- Software Vendor Salle : Owner ERP-System<br>System (External) representatives<br><!-- End of picture text -->

Figure 5. Chart of project organization (own depiction). 



<!-- Start of picture text -->
.<br>F Tray Boxes: Yes 4 if ~ ~<br>.<br>*<br>le Ge, a Seat}<br>Sid rt<br>_ .<br>+<br>Round of Trteger = Integer<br>pmo |e O° “=F |<br>=e<br><!-- End of picture text -->

Figure 6. Set of rules of a simple aluminum box for a fully automated storage system (source: screenshot from internal system). 

252 

<u>Journal</u> of Information Technology Teaching Cases 13(2) 

question-based form. This implies that the user would be guided through the configuration process using the predetermined questions. By answering these questions, the set of rules would apply its logic and compile the bill of materials in the background. 

## User acceptance test 

Once the user interface was created, the configurator was ready for testing. Selected Essemtec AG employees were invited to test and provide feedback. Figure 7 shows the final user interface of the CPQ system. Tim remembers this day when a design review was held to discuss the feedback. In general, the feedback was satisfactory, but there were also fundamental discussions about the question-based logic in which the end user had to configure a product. These fundamental differences in expectations led to considerable project delays. Not only were personal differences blamed for the delays but also the technical difficulties regarding the sophisticated set of rules and the previously underestimated integration of the software into the existing ICT landscape also significantly affected the project duration. The go-live took place in June 2018, one and a half years after the initial estimation. 

## Reactions post-implementation 

When the sales team started using the new CPQ software, they were slightly anxious. First, it seemed to be more time-consuming 

than the spreadsheet-based solution because they were used to the old process. However, with time, the sales team became accustomed to it and started to like the new CPQ software. They also noticed that for newly hired salespeople, it was more convenienttofamiliarizethemselveswiththenewCPQsoftwarethan with the old solution process. One reason for this was that the software user was guided by the configuration process based on various questions. 

After the initial familiarization phase, the product management department noticed that they received practically no more inquiries from the sales department regarding the product configuration. There were also noticeable improvements in the production process. During the project, they discovered unexpected possibilities for more customization of both customer- and country-related requirements. Another advantage of the CPQ system that quickly became apparent was that Essemtec AG could now make real-time changes in configuration and prices worldwide. 

Moreover, Tim received positive feedback from Essemtec AG’s distributors and external sales agents, who mainly admired the new modern appearance and improved user friendliness. This was important to the management because it strengthened their position as distributors who also sell competitors’ products. With the CPQ software, they could get ahead of same-sized competitors. With the new configurator, distributors were able to create a quote for their potential customers. This also helped the onboarding of new distributors. 

In general, the entire sales process was much more efficient than before. Thus, Essemtec AG could reduce 



<!-- Start of picture text -->
ll Cockpit #% Catalog Quote EQRMenen Pina oY<br>- 2 « rN ete<br><>.i7*<br>7*<br>em ee Mees ; : - 9<br>a em and al ~ e<br><!-- End of picture text -->

Figure 7. User interface of the CPQ software implemented at Essemtec (source: Essemtec, 2021). 

253 

Blumentritt et al. 



<!-- Start of picture text -->
Goods flow<br>tow igh Informationcomplexity<br><!-- End of picture text -->

Figure 8. Danger of disintermediation (building on Clement and Schreiber 2016: 101). 

Table 1. Goals of configure, price, quote software. 

||Advantage/gain/<br>opportunity|Disadvantage/<br>pain/risk|
|---|---|---|
|Sales department|||
|Product management<br>department|||
|Distributors and external<br>sales agents|||
|Company as a whole/<br>others|||



failure costs. Additionally, customer satisfaction increased. However, Essemtec AG also faced some disadvantages. One is that the CPQ system cannot fully cover all customer requests. Approximately 30% of the cases are special requests that still require manual action. Moreover, special training is required to maintain the software, and the sales team must be trained to use it. Another disadvantage is project intensity. Its integration into Essemtec AG’s IT landscape created dependencies within the company. 

## What the future holds 

With the CPQ system now successfully in place, and thus some processes of the supply chain being more digitalized, Tim thought about further potential for Essemtec AG. One was disintermediation, that is, selling directly to customers and thus making the work of external salespeople obsolete. If the engineers of the B2B customers could use the configuration tool themselves, Essemtec AG’s internal sales department would act as sales consultants only. Tim immediately scheduled a meeting with Michael to discuss this. Before the meeting, Tim refreshed his knowledge about disintermediation. 

According to Clement and Schreiber (2016: 80), intermediaries can ensure a decrease in transaction costs between different market actors. They function as central points that bring together supply and demand, and their presence in the market increases transparency and prevents opportunistic behavior. Due to the better availability of information, market actors can save different types of transaction costs—starting with efforts to search for offers and compare products, over costs for negotiating with the other party, and monitoring the actual implementation. From an economic perspective, disintermediation (i.e., forgoing intermediaries) makes sense as soon as the costs of direct transactions between suppliers and customers become lower than the cumulative costs of transactions between suppliers and intermediaries, intermediaries, and customers, and the trading margin of the intermediary. This is mainly the case in electronic markets where the Internet and digitalization help suppliers and customers reduce their transaction costs. To assess disintermediation, Clement and Schreiber (2016: 101) suggested that two dimensions be considered, as shown by the matrix in Figure 8. On the one hand, the volume of goods flows, and on the other, information complexity. 

- The risk of disintermediation is rather low for companies that handle high flows of goods and, at the same time, process complex information. 

- The more specialized a company’s services are in the supply chain, the lower the risk of disintermediation by an upstream or downstream business partner. 

## Conclusion 

Apparently, the implementation of a new CPQ system was successful for the project team and departments that were directly or indirectly involved in the quote creation process. The implementation, especially the integration of CPQ software, is not a project that can be done in addition to daily work. Motivated and skilled employees are required to lead such a project to success. 

The initial pain points with the spreadsheet were successfully resolved, and the quote creation process became more convenient. This is especially important for sales intermediaries, who expect a simple and efficient solution from manufacturers. Furthermore, the different departments, such as sales and product management, were satisfied because they gained time to focus on their daily tasks. 

CPQ software suits a company that offers highly configurable products, and these products are configured according to customer requirements. A company must know that CPQ software not only solves issues but also creates new challenges that must be overcome. 

254 

<u>Journal</u> of Information Technology Teaching Cases 13(2) 

## Assignment questions 

1. Goals of CPQ software: What are the advantages and disadvantages of implementing new CPQ software? Use Table 1 as a guide. 

2. Mass customization: Following Qui et al. (2020), does Essemtec AG fulfill the prerequisites for mass customization? 

3. Disintermediation: Put yourself in the shoes of Tim, who wants to prepare himself to discuss the idea of disintermediation with Michael, the Director of Sales. With the help of Clement and Schreiber’s matrix (2016), assess the danger of disintermediation and eventually recommend the introduction of direct sales to customers’ engineers. 

## Additional questions 

4. Depending on your assessment, provide a recommendation to the management team on how to proceed with mass customization. 

5. Think of any situation in a company you worked for, or are currently working for, that is comparable to Essemtec AG’s case. If a CPQ system was also implemented in your case, what was its goal, and did you experience similar advantages and disadvantages observed in Essemtec AG? If not, what are the reasons for this? 

## Abbreviations 

- CPQ Configure, price, quote 

- CRM Customer relationship management ERP Enterprise resource planning B2B Business-to-business B2C Business-to-customer ICT Information and communications technology IT Information technology 

- USP Unique selling proposition. 

### Declaration of conflicting interests 

The author(s) declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article. 

### Funding 

The author(s) received no financial support for the research, authorship, and/or publication of this article. 

### ORCID iD 

Joachim Ehrenthal  https://orcid.org/0000-0003-2195-1465 

### References 

- Clement R and Schreiber D (2016). Direkte beziehungen zwischen anbieter und nachfrager. In R Clement and D Schreiber (Eds), Internet- Okonomie:<sup>¨</sup> Grundlagen und Fallbeispiele der vernetzten Wirtschaft (pp. 79–106). Springer. DOI: 10.1007/9783-662-49047-1_4 

- Essemtec AG (2021). Produkte—SMTequipment aus der schweiz, viewed in December 2021. https://essemtec.com/produkte/ 

- Qi Y, Mao Z, Zhang M, et al. (2020). Manufacturing practices and servitization: The role of mass customization and product innovation capabilities. International Journal of Production Economics 228: 107747. DOI: 10.1016/j.ijpe.2020.107747 

### Author biographies 

Joachim Ehrenthal is Professor for Business Information Systems at the University of Applied Sciences and Arts Northwestern Switzerland FHNW, specializing in supply chain tech. 

Ariane Blumentritt is MSc. students in Business Information Systems at the University of Applied Sciences and Arts Northwestern Switzerland FHNW. 

Benjamin Haueter is MSc. students in Business Information Systems at the University of Applied Sciences and Arts Northwestern Switzerland FHNW. 

Nadine Hitz is MSc. students in Business Information Systems at the University of Applied Sciences and Arts Northwestern Switzerland FHNW. 

Muhammad Sufian is MSc. students in Business Information Systems at the University of Applied Sciences and Arts Northwestern Switzerland FHNW. 

