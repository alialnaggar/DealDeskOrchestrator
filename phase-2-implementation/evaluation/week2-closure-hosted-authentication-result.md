# Authorized Week 2 B01 validation — metadata authentication gate stopped inference

**Outcome: NO INFERENCE.** Ali supplied a development credential for the
previously approved B01-only assessment
`M20-WEEK2-CLOSURE-B01-7947a47b-ee53-48b0-9a92-2c3dd64c32a7` and
confirmed Groq Free with billing disabled. The local key is stored only in
`phase-2-implementation/backend/.env` (owner-only `0600`, ignored by the
existing root `.gitignore`); its value, provider error body, HTTP headers and
private checkpoints are **not** published. The actual child process loaded
the key and passed the local credential-shape check. That check does **not**
prove provider authentication.

Before contacting Groq, the exact [manifest](week2-closure-hosted-proposal.json)
matched approved canonical SHA-256
`5bbf5e79f7fe6d77014d4f40f4f66c446b029b6e54bbcc0e5353b82b58a14143`.
Tracked M2.0 runtime code was unchanged from reviewed `a6ee726`; the
execution branch was `534e616`. The pinned Phase 1C checkout was at
`90c0bc8e285ee69262c7db826b786096a77ad004`. Fresh isolated PostgreSQL
business and checkpoint databases were created; the business database held
the complete nine-case synthetic fixture and pinned compiled rules. A
source-first **read-only** original assessment matched B01's sealed bundle
`720f3b16d9be58a83ece05881387ea0b074bc1552e1b301b933c00eb17128526`
and source digest
`64aca7dd89012213a130b542ebc37c15707342a7763d6ecdeda0c5765821ffe4`.
All six original fixed responsibilities matched the previous B01 baseline:
Configuration `confirmed`, Pricing `calculated`, Fulfillment `needs_revision`,
Credit `calculated`, Policy `evaluated_with_interface_limits`, and Approval
Routing `withheld`. The original review remained `needs_revision`, routing
withheld and the candidate `not_started`. The checkpoint database was empty
before that fixed original was checkpointed. The single-worker owner and
private directories were fresh, owner-only `0700` and empty.

**Stopping gate:** Exactly one approved, bounded **metadata GET** to the
Groq model endpoint returned HTTP **401**, categorized locally as
`authentication_failed`; the response body was not read or logged. The run
stopped before invoking `run_m20_evaluation` or sending any inference POST.
No metadata retry, provider fallback, paid call or old B01 replay followed.
The newly created checkpoint holds only the six fixed original results and
sealed source; the owner directory still has **zero send reservations**.

| Sanitized measure | Value |
| --- | --- |
| Metadata requests | 1 GET, HTTP 401; no response usage |
| Configuration/Pricing generation POSTs | **0** of 6 allowed |
| Configured output / reported inference tokens | **0** / none |
| Inference request bytes / latency | None / not measured |
| Validated hosted Pricing finding or justified abstention | **Neither: Pricing never ran** |
| Fixed results, candidate, human approval | Unchanged; no candidate or approval |

This is a specific **authentication failure**, not Pricing's previously
unclassified HTTP 400. The provided key must authenticate successfully in
the authorized environment before another metadata preflight or any POST.
Do not retry the same known-401 credential or infer that local shape proves
access. A fresh offline regression with the local loader available passed
**251 tests, seven skips** on seven newly isolated PostgreSQL databases;
private GitHub CI remains unverified. The [closure matrix](week2-closure-audit.md)
remains partial.
