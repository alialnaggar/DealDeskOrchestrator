# Original-only M2.1 continuation with fixed candidate — live development

**29 October 2026.** One fresh B01 and three further fresh B05/B01/B05 assessments
used the authorized free-tier Groq account, separate disposable PostgreSQL
business/checkpoint databases, opt-in rate coordinator and no replay. No
new HTTP 429 or paid OpenAI request occurred. The historical 429's specific
quota remains unknown.

| Case | Observed outcome |
| --- | --- |
| B01 `GROQ-DEV-1e91a2ee2c7a4063b2675526aefa10e6` | All six AI responsibilities were invoked on **the original**. Configuration, Pricing, Fulfillment, Policy and Routing completed; Credit inspected evidence and validly abstained with `model_uncertainty`. Fulfillment's isolated candidate was fixed-checked with `supply_supported_unreserved` but `needs_revision`; both original and candidate Routing stayed withheld, customer acceptance pending. The original AI review was added without overwriting the candidate comparison. |
| B05 `GROQ-DEV-8de78c6314b94acd97c764313957283d` | Configuration and Pricing completed; Fulfillment stopped on HTTP 400 at the no-tools final. No candidate or later AI continuation; no resend. |
| B01 `GROQ-DEV-f6f8432870cd46b683b0716591107f02` | Configuration and Pricing completed; Fulfillment again stopped on HTTP 400 at the final. No candidate or later AI continuation; no resend. |
| B05 `GROQ-DEV-015d6fae7ba449c287eebdb113a52354` | Configuration and Pricing completed; Fulfillment again stopped on HTTP 400 at the final. The opt-in allowlisted diagnostic yielded no usable provider category. No candidate or later AI continuation; no resend. |

The four attempts are preliminary troubleshooting evidence, **not** an
accuracy estimate. The B01 run demonstrates full original-subject graph
traversal, but not six favorable AI findings: Credit abstained. The three
terminal HTTP 400s have no usable safe provider error category, so their
specific causes cannot be inferred from the status alone. A future fresh
attempt may capture only the existing allowlisted type/code/param diagnostic;
the latest returned none. Provider text is never stored. Fixed business rules
remain authoritative. Further B05 attempts should first investigate provider
contract compatibility offline rather than replaying any terminal assessment.

Offline regression used a fresh PostgreSQL checkpoint: 83 tests passed,
2 skipped, including a mocked complete candidate + original-only AI LangGraph
assessment, original-subject tool/model isolation, candidate tamper rejection,
restart without extra model sends and the unchanged no-candidate path.
