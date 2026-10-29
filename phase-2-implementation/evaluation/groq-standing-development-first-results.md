# First standing-authorization Groq development results — 29 October 2026

Free-tier, synthetic-only, seven fresh assessments with separate disposable
business/checkpoint DBs and private owner receipts. No old B05 request was
replayed. All runs used Groq `openai/gpt-oss-120b`; the future paid OpenAI API
was not used. The provider-facing schema, receipt, source and fixed-rule gates
remained in force. Per-case private manifests, receipts and sanitized results
live under `/tmp/opencode/dealdesk-groq-dev-*` (not in Git).

| Fresh assessment prefix | Specialist path | Result |
| --- | --- | --- |
| `8ce3e32b` | Configuration → Pricing | Both inspections returned, Configuration completed; Pricing final failed local validation (`malformed_output`, old prompt). |
| `68c20814` | Configuration → Pricing | Configuration inspection returned, second native-tool POST HTTP 400; stopped before Pricing. |
| `388c86f5` | Configuration → Pricing | Same second-POST HTTP 400; allowlisted error diagnostic empty, exact cause unknown. |
| `5fc8e705` | Credit | Inspection **and** strict-schema final completed; three exact credit-profile fields validated. |
| `8b0ac664` | Configuration → Pricing, B01 | Second native-tool response rejected (`action_arguments`); stopped before Pricing. |
| `4f43dfc1` | Configuration → Pricing, B05 | New no-tools Configuration final completed, Pricing inspected its line; Pricing final rejected (`terminal_semantics_or_evidence`, old final prompt). |
| `198e6101` | Configuration → Pricing, B05 | New no-tools Configuration final completed; Pricing strict-schema final completed with six exact validated pricing fields. |

The final successful B05 run read `product:M18-P-B05` and
`pricing_line:M18-L-B05`. Configuration cited only the product's active and
sellable flags; **these do not establish all configuration validity**. Pricing
cited EUR, fixed discount `10`, fixed margin
`22.22222222222222222222222222`, list price `1000.00`, quantity `18` and
quoted unit price `900.00`, all copied from the authorized inspection and
checked against its ledger. Groq did **not** calculate or authorize the
margin or reprice/approve a deal. Fixed B05 review stayed `needs_revision`.
That run used four returned POSTs and 2,560 **configured** completion tokens;
checkpointed usage totals 2,743 prompt and 1,164 completion tokens. Across
other stopped cases, uncheckpointed returned usage is unknown; do not infer
actual consumption from configured ceilings. No observed 429 or rate-limit
evasion. A success on one synthetic assessment is not a reliability estimate.

Development-only Configuration now uses a verified inspection followed by a
separate no-tools strict-schema terminal response. Pricing/Credit development
uses a versioned terminal prompt spelling out exact JSON-encoded scalar
citations. The previous legacy manifest/prompt hash and disabled production
gate remain intact. The historical HTTP 400 is not conclusively attributed to
`tool_use_failed`; a bounded provider diagnostic yielded no allowlisted code.

**Remaining:** repeated real-model trials on fresh cases, terminal failure
categories, Credit on broader evidence, and development harnesses for Policy,
Routing and Fulfillment. Human review and fixed rules remain authoritative;
the six-specialist real-model journey is **not** yet complete.
