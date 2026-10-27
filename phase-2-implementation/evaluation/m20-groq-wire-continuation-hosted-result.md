# B05-only corrected Groq continuation — completed, human review required

**27 October 2026.** Ali explicitly approved the single fresh B05 identity
`M20-WIRE-CONTINUATION-B05-6c63a9e3-fec9-4d97-8c80-2cb1c9dcf476` from
manifest SHA-256
`9fcd2fd14fde3ba00b497f404ea3716dc88ca79f58a635c9d39ee762517f7822`
at commit `ad78ae120a60ea3561c7049f128f465e7a5adff7`; the Groq account
was confirmed Free/billing disabled. No old assessment or reservation was
replayed, and no B01 or other case was sent.

## Gates and observed hosted behavior

Before the first POST, the canonical manifest hash, pinned Phase 1C checkout
`90c0bc8e285ee69262c7db826b786096a77ad004`, fresh synthetic source
bundle and source-input digests, all six original fixed findings, eligibility,
empty isolated checkpoint, empty owner-only receipt directory, credential
ownership/mode/shape and authenticated model-metadata GET (200) passed.
The fresh local PostgreSQL suite for the wire fix had passed **233 tests:
226 passed and seven unrelated skips**; GitHub CI remains unverified.

| Stage | HTTP/model outcome | Serialized request bytes | Reported prompt + completion tokens | Model latency |
| --- | --- | ---: | ---: | ---: |
| First decision | Returned a native `inspect_fulfillment_paths` call; trusted inspection completed | 4,810 | 1,178 + 337 = 1,515 | 1,293 ms |
| Corrected follow-up | **Accepted by Groq**, with `system → user → assistant(tool_calls) → tool(tool_call_id)` and one returned submission intent | 7,252 | 1,825 + 494 = 2,319 | 1,877 ms |
| Separate structured final | Returned a parsed binding proposal | 6,430 | 1,863 + 1,017 = 2,880 | 2,608 ms |

**Exactly three sequential POSTs**, all returned; each was at most 8,192
bytes. Configured output ceilings were 512 + 512 + 1,024 = **2,048 tokens**.
Actual reported usage was **4,866 prompt + 1,848 completion = 6,714 total**,
below the 8,000 reported-total-token post-send stop. Model-call latency was
5,778 ms combined; it is not overall wall-clock assessment time. Cost was
not reported; Free-tier/billing-disabled status is the account owner's
confirmation, not an independently measured invoice. Three reserved and
returned private receipts, checkpoint and raw responses remain in owner-only
`/tmp/opencode/dealdesk-m20-wire-approved-*` directories; raw content and
credentials are not in Git.

## Evidence, AI, fixed verification and business outcome

The trusted prefetch inspected original supply and the model selected one
scoped `inspect_fulfillment_paths` read. Both tool calls completed; the
model-selected read returned two evidence references. The final AI output
proposed a **two-slice partial delivery** for 18 units: 11 on 2 September
from inventory and seven on 11 September citing dated inbound supply and
inventory. It did not abstain. Three submitted source references were
accessible from returned tools; exact per-slice support was **decided by the
pinned deterministic verifier**, not by counting citations or accepting model
text. No validation rejection occurred.

The verifier marked **one isolated candidate** `fixed_checked`, with supply
`supply_supported_unreserved`; all six candidate responsibility mappings
completed. The immutable original still needs revision; the candidate also
remains `needs_revision` with approval routing withheld. The reviewer package
records customer acceptance of the revised schedule as **pending** and
requires human review. Nothing was approved, reserved, booked or promised;
this is an evidence-supported alternative, **not a delivery commitment**.

This one-case result demonstrates that Groq accepted the corrected second
decision wire and structured final in this run. It does not establish measured
accuracy across cases, authorize B01 hosted use, or activate ordinary hybrid
assessments. The bounded authorization is spent; further inference requires
new scope and approval. Week 3 planning remains separate.
