# Phase 1B — Agent architecture

The authoritative Phase 1B design is [Agent architecture and deal flow](agent-architecture-and-deal-flow.md). The [workflow diagram](assets/six-agent-workflow.png) illustrates the same execution order and dependencies; the written specification governs if they differ.

The system has six specialists coordinated by one orchestrator: Configuration Validator; Pricing & Margin; Availability, Production & Fulfillment; Credit & Risk; Policy & Compliance; and Approval Routing. Credit and Policy remain independent for domain-specific decisions and error attribution. Mandatory checks run in deterministic tools; LLM reasoning is bounded by those results and human escalation.

**Scope and related work:** Phase 1A contains the literature review and is unchanged. The 24-table Phase 1C data strategy and its implementation live separately; this folder defines agent behavior and the incoming-deal handoff, not the database schema. Design status and implementation evidence are distinguished in the specification.
