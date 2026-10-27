# Hosted transport reliability / replacement proposal (offline)

**27 October 2026.** This is an engineering and preparation record, **not a
new inference authorization**. The historical B01 receipt, checkpoints,
aggregate journal and report are immutable; see
[stopped result](hybrid-groq-campaign-stopped-result.md). No hosted POST was
made during this milestone. The Phase 1C pin and fixed rules are unchanged.

## Incident: proof versus hypotheses

- B01's original six fixed results were `needs_revision`. One counted
  line-supply prefetch yielded three scoped references. The checkpoint has a
  pending decision at ordinal zero, no returned model response, and no
  candidate. The `0600` receipt has only `reserved`. The 4,807-byte reconstructed
  wire exactly matches the checkpointed SHA-256; the decision completion cap
  was 512. The campaign journal says only `ProviderError`. No HTTP status,
  provider body, timing or usage was captured; a metadata GET succeeded before
  the attempt but does not prove that the POST was accepted.
- `live_models._post` previously classified HTTP status but grouped several
  network/protocol failures, used unbounded `json.load`, and discarded provider
  error subtypes before the campaign journal. The private launcher printed
  exception *class*, not the code. It is **impossible to assign a historical
  root cause**: HTTP rejection, connection failure, timeout or response
  failure remain possible. Nothing in the saved artifacts establishes a 512
  cap rejection, rate limit, invalid schema or provider-token total.
- Groq [chat API](https://console.groq.com/docs/api-reference#chat-create),
  [reasoning](https://console.groq.com/docs/reasoning),
  [tool use](https://console.groq.com/docs/tool-use) and
  [structured output](https://console.groq.com/docs/structured-outputs)
  describe the chat `messages`, named local function tools, required tool
  selection, `parallel_tool_calls`, `max_completion_tokens` and strict
  `json_schema` response-format mechanisms used by the decision and separate
  final wires. GPT-OSS 120B supports these mechanisms. The decision has tools
  and no `response_format`; the final has strict schema and no tools. The
  schema's objects include required properties and disallow additional
  properties. The offline reconstructed decision includes no proposal before
  binding-path inspection. A 512 cap **includes reasoning tokens**, potentially
  starving the visible tool call; this is a quality/truncation risk, not proof
  of HTTP rejection. A larger cap would change the frozen campaign budget and
  needs an explicitly approved replacement scope. Offline document checking
  cannot prove acceptance by the live account/API; no schema probe was sent.

## Changes and safety decision

- The opt-in no-redirect hybrid transport reads at most 16,385 response bytes and
  rejects >16,384, malformed JSON and non-object top-level data. It emits
  bounded sanitized HTTP status or separate timeout, connection lost/refused,
  protocol, network and malformed-response codes. Error bodies, URL, headers,
  credential, exception text and raw error payload are never journaled.
- After an fsynced reservation, a caught send failure appends and fsyncs one
  `failed` marker with an allowlisted code and monotonic elapsed milliseconds.
  A returned response retains the existing `returned` marker and raw-response
  checkpoint path. A crash before the failure marker still leaves a reserved
  receipt. A `failed` or reserved-only receipt **never grants replay**; legacy
  reserved/returned receipts still parse. Cancellation is caught at this
  boundary; process kill and power loss cannot be caught, hence remain
  uncertain. Socket timeout is per blocking operation, **not a guaranteed
  wall-clock deadline**; the configured hosted timeout remains 30 seconds.
  A crash between `returned` and checkpoint persistence can leave a returned
  marker without raw data; the no-replay contract intentionally stops rather
  than recovering by retransmission. No new persistence service or retry path
  was added.
- Campaign journal now saves allowlisted `ProviderError` and known malformed
  Groq response codes instead of their uninformative class, while still stopping globally.
  Unrecognized exceptions use a generic code. **Global stop stays
  in force.** Proceeding to unrelated cases after an uncertain send would
  require new campaign authorization accounting for unknown provider usage,
  new per-case stop/reconciliation semantics and tests; silently continuing
  under the old 21-send / 60,000-reported-token threshold is not justified.
  The existing one-shot journal also blocks second workers and restart reuse.

## Offline verification

Fault injection exercises HTTP error bodies never read, redirect rejection,
timeout, connection reset/refusal, truncated protocol read, malformed and
oversized responses, cancellation, durable sanitized failure receipt, forged
receipt fields, duplicate workers and restart/no-replay. The historical B01
reserved-only receipt was verified **read-only** against the revised parser:
it remains non-replayable. A newly initialized isolated PostgreSQL 16 cluster
on port 55483 loaded the unchanged pinned schema, two independently loaded
fixtures, compiled rules and an empty checkpoint database. The full offline
suite ran **211 tests, 204 passed and seven unrelated Gemma diagnostics
skipped**. A second run against the already used first disposable database
failed due to duplicate fixture rows and old checkpoints; it was not a fresh
regression. After an additional malformed-response journal test, the final
passing run used another **newly initialized isolated cluster** on port 55485
with fresh databases and independently loaded source fixtures. No provider key
or inference POST was used. GitHub CI has not been observed; this local result
is not a CI pass. The disposable clusters are
separate from the preserved historical B01 cluster.

## Replacement proposal — not executable or authorized

**Superseded for authorization by the separately frozen
[replacement proposal](hybrid-groq-replacement-authorization.md).** The
historical investigation above and first preparation sketch remain intact;
use the newer manifest/digest and tested case-local policy for any approval.

Keep the ten ordered cases **B01–B05, N01, R03, N02–N04** on separate fresh
synthetic, reference and checkpoint databases. The frozen source hashes in
[`hybrid-groq-campaign-identities.json`](hybrid-groq-campaign-identities.json)
were independently re-read for all ten during the stopped campaign's
preflight (R03 from the reference database). Revalidate each source fingerprint
again before any replacement send; no historical checkpoint or journal may be
mounted in that run. Fresh proposed assessment identities (not Phase 1C run
IDs; the current runner generates identities at execution time, so a revised
runner/manifest would have to pin these before authorization):

| Case | Proposed fresh assessment identity |
| --- | --- |
| B01 | `HYBRID-REPLACEMENT-B01-4cf91223-e301-4aaa-b94f-f7988298f9bd` |
| B02 | `HYBRID-REPLACEMENT-B02-70f527d9-4167-48c9-92d3-ad2331c8e7e3` |
| B03 | `HYBRID-REPLACEMENT-B03-ea0ac6e3-0b87-44d4-8b91-d43f178c0b9d` |
| B04 | `HYBRID-REPLACEMENT-B04-6fe305a1-136d-483c-ac57-95d3198eb389` |
| B05 | `HYBRID-REPLACEMENT-B05-61dc5bc6-635a-4a76-a1f8-1380dc0a8f3f` |
| N01 | `HYBRID-REPLACEMENT-N01-24e4474a-6c49-4d3f-a6c8-f2948f3cd47f` |
| R03 | `HYBRID-REPLACEMENT-R03-f1a2e564-0e58-4bc1-8658-d4b9cbc1b62c` |
| N02 | `HYBRID-REPLACEMENT-N02-c75a39a8-630f-4fae-8f5a-2a549de65099` |
| N03 | `HYBRID-REPLACEMENT-N03-818c7e1a-f48f-43b7-8592-e4079e9da5dc` |
| N04 | `HYBRID-REPLACEMENT-N04-c08dcd30-87f3-42bf-a1da-3a02841b22bc` |

Proposed conservative budget **unchanged until separately approved**: at
most 21 sequential sends, 14,336 configured completion tokens total, 8,192
bytes per request; per eligible case at most two 512-token decisions and one
1,024-token final (2,048 configured total); no revision, retry, fallback or
concurrent worker. Stop on any uncertain send, identity/source mismatch,
missing usage, critical verification error, >60,000 *reported* total tokens
after a case, or two contained errors. This reported-usage threshold does not
cap input tokens. Before approval, decide explicitly whether to enlarge the
512 decision cap and reduce requests/cases or obtain a separately bounded
output allocation; do not claim the current cap is adequate for reasoning.
Review R03's provisional expected finding source-first outside agent inputs.
The new manifest digest, runtime binding for fresh identities, database
isolation and full offline rehearsal must be frozen and reviewed before asking
for hosted authorization. Nothing here invokes the existing executable
campaign, whose digest remains its historical identity.
