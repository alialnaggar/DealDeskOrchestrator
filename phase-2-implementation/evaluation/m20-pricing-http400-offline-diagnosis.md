# Stopped B01 Pricing HTTP 400 — offline structural diagnosis

**27 October 2026.** The B01 assessment and its fourth attempted Groq POST
are permanently stopped. This diagnosis reads the existing private PostgreSQL
checkpoint **locally**; it does not send anything, print provider responses,
expose credentials, or interpret an unread error body. The [sanitized run
result](m20-configuration-pricing-hosted-result.md) identifies the four
attempts, three returned usage reports and fixed-review containment.

The Configuration and Pricing second-turn bodies were independently rebuilt
from each specialist's exact checkpointed input, returned native call
descriptor and **completed** permission-ledger result, using the same
`request_body` serializer. Each rebuilt SHA-256 matched its pre-send
`m20_model_attempts` reservation. No model text, line values or private body
was copied into this document.

| Checked property | Configuration follow-up (accepted) | Pricing follow-up (HTTP 400) |
| --- | --- | --- |
| UTF-8 canonical body | 3,339 bytes | 3,377 bytes |
| Model / token setting | `openai/gpt-oss-120b` / 512 | Same |
| Top-level fields | `model`, `temperature`, `max_completion_tokens`, `parallel_tool_calls`, `tool_choice`, `tools`, `messages` | Same |
| Tool names | Own `inspect_configuration_line`, `submit_finding`, `abstain` | Own `inspect_pricing_line`, `submit_finding`, `abstain` |
| Tool schema / control | Domain-specific line ID; shared final/abstain schemas; `tool_choice=required`, `parallel_tool_calls=false` | Same, except own inspection name |
| Role sequence | system → user → assistant → tool | Same |
| Assistant call / tool result | `content=null`, one function call, native 39-character ID paired with `tool_call_id`, same function name, valid original line ID; tool content equals completed ledger result | Same checks pass |
| Request reservation | Rebuilt request hash equals reserved hash | Same |

The Pricing tool result contains the selected pricing-line fields rather than
Configuration's selected product fields, as authorized. That data and the
inspect function name are the meaningful differences; an HTTP 400 alone
does not establish which difference mattered. Groq's error body was **not
read**, and there is no provider contract rejection detail. Neither the
paired-message implementation, IDs, serialization nor budget can currently
be identified as the demonstrated root cause. Classify as **unresolved
provider rejection**; do not change the adapter or claim that Groq rejects
Pricing's schema based on this one response.

Offline regression adds both specialists' shared wire-shape/ID checks and a
mocked four-turn Configuration-success/Pricing-HTTP400 flow: the original
fixed results and human review remain intact, Pricing contributes no validated
finding, and reopening the PostgreSQL checkpoint causes **zero replay sends**.
Further diagnosis must use safe local fixtures or separately authorized
provider-contract documentation/probes. A fresh hosted assessment and budget
would require Ali's new explicit authorization; B01 may not be resumed.
