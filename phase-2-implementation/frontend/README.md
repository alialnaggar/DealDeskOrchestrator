# D4 — supervisor console (offline, local only)

For the refined supervisor-facing sequence, exact clean-start commands, timed narration and fallback, see the [D6 offline demonstration runbook](../planning/supervisor-demo-d6-offline-runbook.md). [D6 rehearsal and residual advisories](../evaluation/supervisor-demo-d6-rehearsal-2026-11-08.md) document the desktop/mobile evidence. The completed assessment now shows a source-validated decision brief first; the keyboard-operable technical trace remains available through “Inspect technical trace.”

Two routes: `/` launches the two allowlisted **synthetic** assessments; `/assessments/[id]` recovers ordered PostgreSQL events and displays the source-validated review. Python is called **only from Next.js route handlers**. No browser token, direct Python request, approval, acceptance, reservation, source writer, model prose or raw checkpoint is included. D3 remains the authority for owner-scoped lookups and source validation; the browser URL is **not** authorization.

## Prerequisites

- Node 22 and npm 10; `npm ci` in `phase-2-implementation/frontend/` (exact `package-lock.json`).
- The already approved **disposable** PostgreSQL 16 cluster at `/tmp/opencode` port `55539`, `/tmp/opencode/dealdesk-test-venv`, and the **exact** Phase 1C pin at `/tmp/opencode/dealdesk-phase1c-pinned`. See [D3 setup/security contract](../architecture/offline-assessment-api.md). Do not point this API at shared, remote or non-disposable databases.
- No model-provider key or hosted access is required. Both servers must remain bound to `127.0.0.1`; do not publish ports or tunnel this demo.

From the **repository root**, prepare a fresh fixture and owner-only secrets (file names must be new on each setup; do not commit or print secrets):

```sh
PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests \
  /tmp/opencode/dealdesk-test-venv/bin/python phase-2-implementation/backend/tests/setup_assessment_api.py \
  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --env-file /tmp/opencode/dealdesk-d4-local.env
umask 077
for name in token password session; do
  /tmp/opencode/dealdesk-test-venv/bin/python -c 'import secrets; print(secrets.token_hex(32))' > "/tmp/opencode/dealdesk-d4-$name"
done
```

**Terminal A** (Python):

```sh
source /tmp/opencode/dealdesk-d4-local.env
export DEALDESK_DEMO_OWNER=operator
export DEALDESK_DEMO_TOKEN="$(cat /tmp/opencode/dealdesk-d4-token)"
PYTHONPATH=phase-2-implementation/backend \
  /tmp/opencode/dealdesk-test-venv/bin/python -m dealdesk_phase2.assessment_api
```

**Terminal B** (Next.js, from the repository root):

```sh
cd phase-2-implementation/frontend
npm ci
export DEALDESK_DEMO_TOKEN="$(cat /tmp/opencode/dealdesk-d4-token)"
export DEALDESK_UI_PASSWORD="$(cat /tmp/opencode/dealdesk-d4-password)"
export DEALDESK_UI_SESSION_SECRET="$(cat /tmp/opencode/dealdesk-d4-session)"
export NEXT_TELEMETRY_DISABLED=1
npm run build
npm run start
```

Open **http://127.0.0.1:3000** and enter the password from the owner-only file locally; never paste it into an issue or chat. `npm run dev` can replace `build` + `start` for development. Both commands hardcode loopback binding; the server-side backend base is fixed to `http://127.0.0.1:8765`. The optional `DEALDESK_UI_ORIGIN` must be left at its default `http://127.0.0.1:3000`. The API token and UI secret are never part of `NEXT_PUBLIC_*` variables. Use distinct values for operator password, API token and session key. Logs must not include them.

The UI session is an HMAC-authenticated, HttpOnly, SameSite=Strict, eight-hour cookie; POSTs require a session-bound CSRF token and exact loopback Origin. Login requires a separately signed, expiring CSRF cookie. It is **not** one-time-use: there is no server-side nonce store. Cookies use `Secure=false` **only** because this application is HTTP on loopback; this is not a remote/TLS deployment design. Logout clears the browser cookie, but sessions have no server-side revocation store; rotate the session secret to invalidate all sessions. No login throttling or remote identity provider is claimed. Never expose this listener through a proxy or public tunnel.

The synthetic fixture preview is intentionally static. All in-workspace facts come from the authenticated D3 API and pass strict Zod contracts. `ai_completed` denotes checkpointed original-subject execution, not clearance; review-confirmed abstentions and gaps appear only after the validated D2 package is available. The candidate panel shows **six deterministic** checks, not six candidate AI runs. The UI polls the exclusive persisted event cursor, recovers from zero on refresh, and refuses source drift (HTTP 409), missing rows, schema drift and identity mismatches.

The supervisor presentation uses a single light theme and separates customer request, six original-subject findings, validated evidence, conditional V0/V1 comparison, human-only action and the collapsed technical trace. The project-local, pinned Markdown-only UI skills and discovery limits are recorded in [`.agents/skills/README.md`](../../.agents/skills/README.md); they are not runtime dependencies.

## Verification

```sh
cd phase-2-implementation/frontend
npm run lint
npm run typecheck
npm run build
npm test
npx playwright install chromium     # once; host needs browser libraries/fonts
npm run test:e2e                  # with both local servers and the three secrets exported
```

To test an updated build without stopping a previous loopback-only UI on port 3000, start a second local Next.js process with `DEALDESK_UI_ORIGIN=http://127.0.0.1:3001` on port 3001 and set `DEALDESK_E2E_BASE_URL=http://127.0.0.1:3001` for `playwright test e2e/supervisor.spec.ts`. Never expose either listener remotely. Supervisor screenshots are written to `/tmp/opencode/dealdesk-launcher-{login,scenarios}.png` and `/tmp/opencode/d6-{rc01,uc02}-{desktop,mobile}.png`.

Playwright creates new RC01 and UC02 assessments, checks 21/20 ordered events, original versus candidate semantics, refresh recovery, CSRF rejection, operator cookie, logout, secrets, keyboard navigation and 390/768/1440px viewports. Screenshots land in `/tmp/opencode/d5-rc01.png` and `/tmp/opencode/d5-uc02.png`; no private artifacts are committed. The opt-in `e2e/fault-injection.spec.ts` additionally requires `D5_DISPOSABLE_ENV_FILE=/tmp/opencode/<fresh-owner-only-fixture>.env` and a **stopped** Python API. It starts its own Python process, kills/restarts only that process, and mutates **only the validated matching disposable databases** for source drift, checkpoint tampering and connection refusal; run it separately from the normal browser suite, never against shared data. On this minimal VM, browser libraries and fonts were **downloaded and extracted only under `/tmp/opencode/d4-browser-libs`** and Playwright was run with `LD_LIBRARY_PATH=/tmp/opencode/d4-browser-libs/extracted/usr/lib/aarch64-linux-gnu` and `FONTCONFIG_FILE=/tmp/opencode/d4-browser-libs/extracted/fonts.conf`. No system packages were installed. On a standard workstation these overrides are unnecessary.

Source references, pin, sealed bundle/source digests, event timestamps and human-only recommendations are deliberately displayed; credit invoice/payment identities, customer ledger rows, provider receipts, credentials and raw LangGraph checkpoint values are not. This is a local supervisor explanation, **not** a hosted-model reliability result or an executable deal decision.
