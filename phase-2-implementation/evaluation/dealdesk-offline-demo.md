# Offline release-candidate demonstration

**Engineering demonstration only:** pinned synthetic evidence and scripted offline model substitutes; no real LLM reasoning, approval or delivery promise. The six fixed mappings are not six AI findings.

| Deal | Fixed original | Fulfillment AI | Configuration | Pricing | Credit | Policy | Routing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M18-D-B01 | needs_revision | completed / abstention | completed | completed | completed | completed | completed |
| M18-D-B05 | needs_revision | completed / abstention | completed | completed | error | abstained | completed |
| M18-D-N03 | needs_evidence | skipped / None | completed | completed | completed | error | completed |

## Follow B01 end to end

- **Submitted deal and evidence:** `M18-D-B01`, pinned Phase 1C run `00000000-0000-4000-8000-000000018001`, frozen bundle `720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`. Read-only dated evidence and source digests are in the JSON.
- **Fixed rules:** original `needs_revision`; all six deterministic specialist mappings completed. The approval route is withheld; no salesperson promise is authorized.
- **Scripted AI:** all six investigations completed; Fulfillment *abstained* rather than proposing a candidate in this original-only workflow. The five other specialists each recorded an evidence-checked citation. See `offline_ai` and `trace` in the JSON for exact references and order.
- **Final handoff:** `Human review required; no approval, reservation or delivery promise`.

B05 injects an unsupported Credit citation (rejected) and a Policy abstention; N03 has insufficient/stale Fulfillment evidence and a Policy error. Neither is reported as a validated AI finding. Other fixed specialist results remain isolated.

## Separate supported alternative

A **different assessment thread** on the same frozen B01 deal uses a predeclared scripted two-slice Fulfillment hypothesis. It is not a six-AI candidate continuation. The pinned verifier rechecked all six fixed candidate responsibilities: `supply_supported_unreserved` supply, `needs_revision` business outcome, customer acceptance `pending`. Source citations were returned by an authorized tool. The schedule matches deterministic-only discovery, so no AI advantage is shown.

## Reproduce and operator checks

1. Follow the [Week 4 one-command setup and evaluation](week4-offline-development.md#run) from this repository's root with the locked Python environment and already-running `/tmp/opencode` test PostgreSQL. It writes fresh evaluation JSON/Markdown and `dealdesk-offline-demo.json`/`.md` beside the JSON path; it never connects to Groq or a non-disposable DB.
2. Check `phase1c_pin`, bundle and source hashes, and `evaluation_stable_sha256`; the B01 original and candidate must have different assessment IDs but the same bundle and source digest.
3. Check B05 rejected/abstained and N03 skipped/error outcomes, candidate `fixed_rechecks` (six), pending customer acceptance and the human-only reviewer action. A rerun on one thread tests replay, not a new sample.
4. If any source or fixed result differs, stop rather than treating this sample report as an answer key. No 36-case independent answers have been accepted. Hosted-model compatibility, semantic utility and private CI remain unverified.
