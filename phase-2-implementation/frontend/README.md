# D4 — supervisor console (offline-scripted; optional HTTPS demo access)

The approved synthetic supervisor demo is also available at `https://dealdeskdemo.duckdns.org` through the VM's existing Caddy proxy. In its explicitly opted-in public mode, the architecture overview and **two allowlisted synthetic scenarios** are accessible without a password; no unrestricted deal entry or backend API is exposed. The backend, database, Next.js listener and model execution remain private/offline. See [public HTTPS deployment](./PUBLIC-HTTPS.md) before changing the VM configuration. The local password-protected setup below remains the default for isolated development.

The guided public journey opens `/scenarios/rc01` or `/scenarios/uc02` **before** issuing a POST. Its structured pre-run record is an explicitly labeled copy of the disposable fixture definitions (`backend/tests/m18_case_setup.py` and `m21_integrated_credit_setup.py`), not a live API read or legally executed agreement. The assessment API has no pre-run deal-record endpoint: fields copied from the reference rows but not explicitly declared in these fixture definitions are deliberately omitted. The public review DTO likewise does not expose raw specialist tool transcripts or credit ledgers; the guided replay can display only event-level boundaries and validated review fields, with findings gated on supporting events. Extending pre-run records to live deals would require a separately authorized, allowlisted read-only source projection with schema/identity/source-drift validation, not frontend inference from a completed review. The candidate record shows only `proposed_delivery_slices` as changed; it does not assert customer acceptance, stock reservation or approval.

For the refined supervisor-facing sequence, exact clean-start commands, timed narration and fallback, see the [D6 offline demonstration runbook](../planning/supervisor-demo-d6-offline-runbook.md). [D6 rehearsal and residual advisories](../evaluation/supervisor-demo-d6-rehearsal-2026-11-08.md) document the desktop/mobile evidence. The completed assessment now shows a source-validated decision brief first; the keyboard-operable technical trace remains available through “Inspect technical trace.”

Two routes: `/` launches the two allowlisted **synthetic** assessments; `/assessments/[id]` recovers ordered PostgreSQL events and displays the source-validated review. Python is called **only from Next.js route handlers**. No browser token, direct Python request, approval, acceptance, reservation, source writer, model prose or raw checkpoint is included. D3 remains the authority for owner-scoped lookups and source validation; the browser URL is **not** authorization.

## Prerequisites

- Node 22 and npm 10; `npm ci` in `phase-2-implementation/frontend/` (exact `package-lock.json`).
- The already approved **disposable** PostgreSQL 16 cluster at `/tmp/opencode` port `55539`, `/tmp/opencode/dealdesk-test-venv`, and the **exact** Phase 1C pin at `/tmp/opencode/dealdesk-phase1c-pinned`. See [D3 setup/security contract](../architecture/offline-assessment-api.md). Do not point this API at shared, remote or non-disposable databases.
- No model-provider key or hosted access is required. Both servers remain bound to `127.0.0.1`; only the Caddy HTTPS virtual host is public. Never publish ports 3000 or 8765 directly.

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

For local development open **http://127.0.0.1:3000** and enter the password from the owner-only file; never paste it into an issue or chat. `npm run dev` can replace `build` + `start` for development. Both commands hardcode loopback binding; the server-side backend base is fixed to `http://127.0.0.1:8765`. For this HTTPS deployment, set `DEALDESK_UI_ORIGIN=https://dealdeskdemo.duckdns.org` and `DEALDESK_PUBLIC_SYNTHETIC_DEMO=1` in the frontend service; otherwise leave the flag unset and use the local password flow. The API token and UI secret are never part of `NEXT_PUBLIC_*` variables. In public mode the operator password is not loaded into the frontend process. Logs must not include secrets.

The UI session is an HMAC-authenticated, HttpOnly, SameSite=Strict, eight-hour cookie; POSTs require a session-bound CSRF token and an exact configured Origin and Host. Local password login uses a separately signed, expiring CSRF cookie; explicitly opted-in public synthetic mode instead issues a session without a password and disables the password endpoint. Neither token is one-time-use: there is no server-side nonce store. Cookies set `Secure` when the configured origin is HTTPS. Logout clears the browser cookie, but sessions have no server-side revocation store; rotate the session secret to invalidate all sessions. Public synthetic launches have a process-local cap, **not** production-grade DDoS protection or remote identity management. Never expose the Next.js or Python listener directly on a public interface.

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

For public HTTPS verification, set `DEALDESK_E2E_BASE_URL=https://dealdeskdemo.duckdns.org` for `playwright test e2e/supervisor.spec.ts`. The server-side API token still comes from an owner-only file and must never be printed. Homepage screenshots are written to `/tmp/opencode/dealdesk-home-{desktop,tablet,mobile}.png`; assessment screenshots use `/tmp/opencode/d6-{rc01,uc02}-{desktop,mobile}.png`. Reviewed copies are collected at `/tmp/opencode/dealdesk-architecture-public-20261109/` on this VM.

Playwright creates new RC01 and UC02 assessments, checks 21/20 ordered events, original versus candidate semantics, refresh recovery, CSRF rejection, operator cookie, logout, secrets, keyboard navigation and 390/768/1440px viewports. Screenshots land in `/tmp/opencode/d5-rc01.png` and `/tmp/opencode/d5-uc02.png`; no private artifacts are committed. The opt-in `e2e/fault-injection.spec.ts` additionally requires `D5_DISPOSABLE_ENV_FILE=/tmp/opencode/<fresh-owner-only-fixture>.env` and a **stopped** Python API. It starts its own Python process, kills/restarts only that process, and mutates **only the validated matching disposable databases** for source drift, checkpoint tampering and connection refusal; run it separately from the normal browser suite, never against shared data. On this minimal VM, browser libraries and fonts were **downloaded and extracted only under `/tmp/opencode/d4-browser-libs`** and Playwright was run with `LD_LIBRARY_PATH=/tmp/opencode/d4-browser-libs/extracted/usr/lib/aarch64-linux-gnu` and `FONTCONFIG_FILE=/tmp/opencode/d4-browser-libs/extracted/fonts.conf`. No system packages were installed. On a standard workstation these overrides are unnecessary.

Source references, pin, sealed bundle/source digests, event timestamps and human-only recommendations are deliberately displayed; credit invoice/payment identities, customer ledger rows, provider receipts, credentials and raw LangGraph checkpoint values are not. This is a synthetic, offline-scripted supervisor explanation, **not** a hosted-model reliability result or an executable deal decision.
