# Groq standing development authorization (29 October 2026)

Ali authorizes **free-tier Groq** inference for synthetic Phase 2 development,
debugging and evaluation without a separate owner approval for every assessment.
This supersedes the earlier *per-experiment* owner-approval step for **new**
Groq development cases, not prior terminal receipts. It does not authorize
paid billing, another provider, production deployment, human deal approval,
customer data, or the future paid OpenAI API. `HOSTED_ACTIVATION=False` remains
the separate production/legacy gate; no OpenAI API adapter or credential is
configured by this change.

Run only in the isolated `/tmp/opencode` synthetic PostgreSQL test cluster.
Each invocation of `backend/tests/run_groq_development.py` provisions a fresh
business database and a **dedicated empty checkpoint database**, loads the pinned
Phase 1C fixture, starts a new assessment, writes a private `0600` manifest
and per-assessment standing-authorization audit record, then enters the existing
receipt, lock, source-revalidation and fixed-rule verification path. The
record binds the case and free-tier account claim; it is **not** a request
for another human signature. Do not commit these records. The process must
opt in with `DEALDESK_GROQ_DEV_ENABLE=1`; only the explicitly selected
secondary Groq key from the existing private `.env` is used. No credentials
are written to output. A completed case can be read from its checkpoint;
an uncertain/failed reservation is terminal and **must not be resent**. To
test a fix, create a new assessment with new databases and audit path.

Example (adjust the local cluster port and package locations to the isolated
test installation; never use production DBs):

```sh
DEALDESK_GROQ_DEV_ENABLE=1 \
PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests \
/tmp/opencode/dealdesk-test-venv/bin/python \
  phase-2-implementation/backend/tests/run_groq_development.py \
  --cluster-dsn 'host=/tmp/opencode port=55492 dbname=postgres user=ubuntu' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --account-id org_01m5d82zneee6b2vzsz8d2014b \
  --case B05 --specialist pricing
```

The CLI prints only bounded/sanitized outcome fields and the private output
directory. **One CLI invocation = one assessment**, at most four POSTs and
2,560 configured completion tokens for Pricing (Configuration first), or two
POSTs/1,536 configured tokens for Credit. Check the account's actual rate
limits (Groq's public table is not an account-specific entitlement). Send
sequentially; on HTTP 429 or quota exhaustion **stop**, report the limit and
do not rotate credentials/accounts or replay the case to evade it. A new
assessment is for a changed test or an independently justified follow-up,
not a retry of an uncertain send. Do not expose raw provider bodies or
private approval/receipt paths in public reports.

Policy and Routing currently use separate M2.1 hosted contracts; Fulfillment
uses its own older live path. This first streamlined entry covers the
Configuration → Pricing typed-final and Credit cases only; it does **not**
claim the other specialists have passed real-model tests. Extend their
development harnesses with the same scoped/frozen evidence and receipt
invariants, never by bypassing their original gates.
