# Proposed fresh B01 Week 2 Configuration/Pricing validation — NO authorization

**Status update:** Ali explicitly authorized the exact manifest and bounds.
The [first preflight stopped without any request](week2-closure-hosted-preflight-blocked.md)
because `GROQ_API_KEY` was unavailable in the execution environment. The
immutable manifest below retains its original `proposal_not_authorized`
status as part of the approved digest; this text records the later approval
and stop without rewriting that identity. **Do not infer that a run occurred.**

**Not executed.** This is a request for Ali's explicit, separate approval,
not a continuation of the [permanently stopped B01 assessment](m20-configuration-pricing-hosted-result.md).
Do not run it, reuse the old identity, read private provider responses, or
send inference based on this document. [Canonical JSON manifest](week2-closure-hosted-proposal.json)
has SHA-256 `5bbf5e79f7fe6d77014d4f40f4f66c446b029b6e54bbcc0e5353b82b58a14143`
using the repository's sorted-key `_canonical` serializer. Its proposed
assessment ID is `M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7`.
Do not substitute a different manifest, prompt or source identity without
new preflight and approval.

| Gate | Proposed bound / required evidence |
| --- | --- |
| Provider and authority | Existing opt-in Groq Free `openai/gpt-oss-120b`; confirm project access, billing disabled and free-tier status again with Ali. No paid OpenAI, fallback, retries, or provider replacement. |
| Source/subject | Synthetic B01 only; Phase 1C pin `90c0bc8e285ee69262c7db826b786096a77ad004`; complete fixture bundle `720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`; source fingerprint `64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`. Preflight exact frozen original, run, deal, sealed pool and fixed findings; abort before a POST on mismatch. |
| Prompt and order | Commit-pinned new `m20-config-pricing-system-v2` system instructions; Configuration then Pricing, one original subject only. Do not apply this version to the old B01 checkpoint. |
| Budget | Maximum **six** sequential POSTs total; **512** configured completion tokens each (**3,072** combined ceiling), **8,192** serialized request bytes each, **24,000** *reported total tokens* post-send stop; no retry of a failed/uncertain request. These ceilings are not authorization. |
| Execution isolation | Fresh disposable business/checkpoint DB, owner-only empty reservation directory, single worker, credential shape/mode and source-pin checks, clean fresh local regression; do not touch other host services or post private payloads. Reconcile branch/commit, staged manifest and prompt version before any separate approval-gated run. |
| Stop and report | Stop on provider HTTP error (including HTTP 400), malformed/tool-pair/identity error, budget overrun, missing/changed evidence, contested citation, mismatch or uncertain reservation. Record sanitized request sizes/hashes, attempt IDs, tokens/latency if returned and no-replay status; retain fixed original and human review. No payload/credential leak or speculation about error cause. |
| Narrow acceptance | Configuration **and** Pricing each complete their own authorized inspection and return grounded, validated observation(s), with fixed result/reviewer invariance and no candidate/approval. An abstention or HTTP error is safe containment, **not** live Pricing completion. One synthetic success does not establish independent accuracy, full Week 2 hierarchy, or production readiness. |

Offline source-first preflight of the *proposal* matched the above B01 bundle
and fingerprint, the original `needs_revision` finding and withheld route.
With the proposed prompt, first-turn bodies were **3,006 / 2,964 bytes** and
illustrative paired follow-ups **3,711 / 3,730 bytes** (Configuration /
Pricing); all are under the proposed byte ceiling. Illustrative follow-ups
are not predictions of a live model's calls or evidence that Groq accepts
them. The Pricing HTTP 400 is still **unclassified**; no adapter defect has
been demonstrated by the offline structural comparison. A separate
provider-contract diagnostic or revised wire might be needed if another
fresh authorized test fails, but must not be guessed in advance.

**Decision requested later:** approve or decline *this exact manifest and
limits* after reviewing the [closure audit](week2-closure-audit.md). Until
explicitly approved, no hosted POSTs. Full Week 2 acceptance still needs a
separate resolution of the older Fulfillment prompt-hierarchy/integration
scope if those are required as written in the blueprint.
