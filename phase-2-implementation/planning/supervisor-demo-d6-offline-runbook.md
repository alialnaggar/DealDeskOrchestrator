# D6 — supervisor live demonstration (local, scripted, 7–10 minutes)

**Scope:** `feature/supervisor-live-demo`, D2 source-grounded review + D3 authenticated Python API + D4/D6 Next.js UI. This is a **synthetic offline model-double demonstration**. No paid inference, production credit decision, approval, stock reservation, customer acceptance or measured model accuracy. Use this runbook with the [D5 QA record](../evaluation/supervisor-demo-d5-quality-assurance-2026-11-08.md) and [D6 rehearsal record](../evaluation/supervisor-demo-d6-rehearsal-2026-11-08.md). The older D0 plan's hosted-development proposal was **not** authorized for this rehearsal.

## Before the meeting: exact local setup

Use a terminal in the repository root. Prerequisites are the **previously approved** `/tmp/opencode/dealdesk-test-venv` with `backend/requirements-m1.1.lock`, PostgreSQL 16 tools/cluster at `/tmp/opencode` (Unix socket port `55539`), the exact Phase 1C checkout at `90c0bc8e285ee69262c7db826b786096a77ad004`, Node 22/npm 10 and installed Playwright Chromium for optional checks. Do not restart an already running cluster, touch other services or point the setup at shared data. The cluster is Unix-socket-only (`listen_addresses=`). If it is stopped and **you own this disposable cluster**, start it via:

```sh
PG_BIN=/tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin
PG_LIB=/tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu
LD_LIBRARY_PATH="$PG_LIB" "$PG_BIN/pg_ctl" -D /tmp/opencode/dealdesk-remediation-pgdata status
# Only if status reports stopped; never restart another owner's running process:
LD_LIBRARY_PATH="$PG_LIB" "$PG_BIN/pg_ctl" -D /tmp/opencode/dealdesk-remediation-pgdata -o '-k /tmp/opencode -p 55539 -c listen_addresses=' -l /tmp/opencode/dealdesk-pg-demo.log start
```

Verify branch, clean tree, pin and local socket, then provision a **new** disposable pair and new owner-only credentials. The setup command refuses an existing environment file: choose a fresh `/tmp/opencode/d6-demo-<date>.env` filename rather than overwriting it. Do not paste credentials into chat, screenshots or a commit.

```sh
git fetch origin feature/supervisor-live-demo
git status --short --branch
git -C /tmp/opencode/dealdesk-phase1c-pinned rev-parse HEAD
PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests \
  /tmp/opencode/dealdesk-test-venv/bin/python phase-2-implementation/backend/tests/setup_assessment_api.py \
  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --env-file /tmp/opencode/d6-demo-2026-11-08.env
umask 077
for name in token password session; do
  /tmp/opencode/dealdesk-test-venv/bin/python -c 'import secrets; print(secrets.token_hex(32))' > "/tmp/opencode/d6-demo-$name"
done
```

**Terminal A**, repository root (use the actual new environment file name):

```sh
source /tmp/opencode/d6-demo-2026-11-08.env
export DEALDESK_DEMO_OWNER=operator
export DEALDESK_DEMO_TOKEN="$(cat /tmp/opencode/d6-demo-token)"
PYTHONPATH=phase-2-implementation/backend \
  /tmp/opencode/dealdesk-test-venv/bin/python -m dealdesk_phase2.assessment_api
```

**Terminal B**, repository root:

```sh
cd phase-2-implementation/frontend
npm ci                     # once before the meeting; lockfile is authoritative
export DEALDESK_DEMO_TOKEN="$(cat /tmp/opencode/d6-demo-token)"
export DEALDESK_UI_PASSWORD="$(cat /tmp/opencode/d6-demo-password)"
export DEALDESK_UI_SESSION_SECRET="$(cat /tmp/opencode/d6-demo-session)"
export NEXT_TELEMETRY_DISABLED=1
npm run build
npm run start
```

Open **http://127.0.0.1:3000** in a local browser. Both listeners must remain `127.0.0.1` only; do not use a proxy, public IP or tunnel. Type the local operator password in the browser. Keep no provider credentials in these terminals. The UI passes a server-side bearer token to Python; the browser gets only an HttpOnly session cookie and validated DTOs. Complete provisioning, `npm ci` and build before going offline; the **assessment itself** requires no network/model provider.

## 7–10 minute narrated path

| Minute | Action / expected screen | What to say (and not say) |
| --- | --- | --- |
| 0–1 | Login; landing page offers B01/RC01 and N01/UC02 synthetic scenarios. Launch RC01 once. | “These are allowlisted synthetic cases and explicitly scripted model observations. No hosted inference is running.” |
| 1–2 | Watch the persisted events count, then the **decision brief**. Original V0: 10 units by **4 Sep 2026**, only 8 supported by the requested date. Outcome `needs_revision`; the banner says checks complete, **not approved**. | “The original date cannot be met unchanged; event completion is not business clearance.” |
| 2–4 | Six original-subject specialist rows: fixed finding on the left, scripted observation on the right. | Configuration checks product/line validity; Pricing & margin calculates within fixed interface limits; Fulfillment identifies the delivery shortfall; Credit checks selected credit evidence (not a full ledger guarantee); Policy retains the late-delivery rule; Approval Routing withholds roles while the revised request is unresolved. A scripted `completed` means a checkpointed stage, **not** a positive finding. Cite visible refs/rule IDs as examples, not hidden records. |
| 4–5 | Delivery comparison. Fulfillment's **offline-scripted hypothesis** is 8 units **3 Sep** + 2 units **8 Sep**. Six V1 fixed checks follow it; supply is `supply_supported_unreserved`, status still `needs_revision`, acceptance `pending`, routing roles `null`/withheld. | “The deterministic verifier confirmed this *proposed* schedule's source-backed supply, not a reservation or customer acceptance. No candidate-specific AI reruns occurred; a human must obtain agreement to the later date.” |
| 5–6 | Human authority panel and recommendations. Then expand **Inspect technical trace** with keyboard Enter or click to show ordered events, pin, source/bundle digests and run ID. | “The source-grounded D2 projection and D3 API revalidate evidence before display. There is no approve/reserve/accept button or raw checkpoint in the browser.” |
| 6–8 | Navigate back; launch UC02. Brief prioritizes **fixed Credit unknown**; no verified candidate; stale/unavailable evidence is visible. | “A completed original scripted Credit observation is **not** credit clearance or a fixed abstention. Missing/old evidence requires a person to review it.” |
| 8–9 | Refresh UC02, optionally return to RC01 via browser history/direct URL, inspect 20/21 persisted events. | “PostgreSQL stores events and LangGraph checkpoints. The URL is not authorization; session and owner checks still apply.” |
| 9–10 | Summarize limits and next steps. | “This illustrates attributable checks, a bounded proposal and fail-closed review, not deployed deal automation or evaluation accuracy.” |

## Technical explanation and recovery

1. Next.js exposes the two local **UI pages** and a restricted authenticated server-side API proxy; a signed, expiring HttpOnly cookie plus CSRF and exact Origin guard browser POSTs. Python bearer tokens never reach browser JavaScript.
2. Python's single-owner API registers an idempotent assessment and schedules the LangGraph offline workflow. Separate disposable PostgreSQL databases isolate synthetic business source from checkpoints/append-only events; the pinned Phase 1C adapter supplies evidence and deterministic checks. Six original-subject specialist slots use offline-scripted model doubles, not Groq/OpenAI calls. Fulfillment supplies one bounded hypothesis, and six **fixed** candidate checks run on V1. The D2 projector accepts a complete, bound checkpoint only; D3 rereads source and rejects drift before serving review.
3. **Temporary API outage:** show that the old decision disappears and the safe error says “review withheld.” Restart Terminal A with the same environment file, then click **Retry now** or wait for polling. Do not invent progress. A completed review and event history can reappear only after revalidation.
4. **Source drift or invalid checkpoint:** HTTP 409 withholds completed status/review. Do **not** edit pinned or real data to unblock it; use a new disposable fixture or inspect the controlled test fixture. **Killed in-flight run:** `uncertain` remains `uncertain` across restart; repeating the same key does not replay the send. A new run requires human inspection and a new launch/key.
5. **Expired login:** return to login and reauthenticate. **No backend/DB:** keep UI decision withheld; do not show a stale screenshot as if live. Check `127.0.0.1:8765`, local PostgreSQL socket and environment file permissions; only restart your own services, never delete a shared DB. **Port conflict:** stop only your known demo PID; do not rebind publicly.

## Offline fallback if live launch fails

First attempt the safe service restart above using the **same** disposable DB pair. If new runs are unavailable but the two completed runs still validate, navigate to their known assessment URLs under the authenticated session and say “historical completed **offline-scripted** assessments, not fresh execution.” Confirm statuses/reviews/events before showing them. If DB or review is invalid/unavailable, stop presenting the UI as a live result. Use the D2/D3 sanitized example and this walkthrough as a **static architecture explanation**, or clearly label locally saved D6 screenshots as prior-run evidence. Never fabricate event progression, switch to hosted AI, edit source records, or bypass `409`/`uncertain`.

**Do not claim:** six candidate AI reruns, fresh hosted reasoning, verified credit clearance for UC02, a fully negotiated V2, reservation, customer acceptance, approval/required approvers when roles are null, production-readiness, formal accuracy or reproducibility from one historical development result. Known Starlette and developer-tool advisories are recorded separately in D6 rehearsal evidence; do not expose this loopback demo to untrusted networks.
