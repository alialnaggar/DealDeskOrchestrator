# Guarded six-specialist Groq follow-up (29 October 2026)

Eight **new** B01/B05 synthetic assessments used the same authorized
free-tier account, fresh business/checkpoint databases, guarded runner and
cross-process Groq coordinator. No terminal assessment was replayed. A
read-only models request returned HTTP 200 but no quota headers; subsequent
inference responses gave remaining-request/token headers and no new HTTP 429.
The historical 429 still has no retained reset metadata, so its quota type
cannot be identified. No paid OpenAI call was made.

| Outcome category | Assessments | Result |
| --- | ---: | --- |
| Local runner owner-directory collision | 1 | Fixed; regression reproduces the real CLI's pre-created directory. |
| Configuration final rejected | 2 | One `claim_value_json`, one `terminal_semantics_or_evidence`; versioned JSON-scalar guidance added, no validator change. |
| Fulfillment native tool HTTP 400 / unseen path citation | 3 | Binding path inspection is now a fixed read prerequisite; after it completes, the existing no-tools strict final follows without extra native-tool decisions. Rejected attempts remain terminal. |
| Fulfillment completed, candidate fixed-checked | 2 | B01 and B05: isolated candidate passed fixed checks, but M2.1 did not start. |

**No complete six-specialist real-Groq assessment yet.** The explicit M2.1
contract requires `candidate_status=not_started`; a fixed-checked candidate
cannot be silently ignored, reset, or attributed to the original. The runner
now reports `candidate_requires_separate_review` separately from an incomplete
Fulfillment result. Completing a six-specialist run after a verified candidate
requires a reviewed candidate-aware continuation design (which state is being
assessed, prerequisite identity, reruns, routing and final package), not a
validator relaxation or another retry of these terminal assessments.

For B01, the original submitted shortfall remained `needs_revision`: Groq
inspected pinned product, pricing, stock, confirmed inbound and shipping-lane
evidence; Fulfillment proposed a two-slice schedule with customer-acceptance
tradeoff. Phase 1C marked the isolated candidate's supply
`supply_supported_unreserved` while its fixed business status remained
`needs_revision`; AI neither approved the deal nor promised delivery. Credit,
Policy and Routing remain
unrun on those same live assessments. Offline regression: 71 focused tests
passed (7 skipped for optional fixture environments), including a fresh
PostgreSQL six-stage LangGraph run with model doubles and no candidate.
No comparative reliability or accuracy claim follows from eight cases.
