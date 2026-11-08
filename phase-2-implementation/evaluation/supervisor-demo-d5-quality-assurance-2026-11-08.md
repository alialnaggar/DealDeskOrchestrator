# D5 — offline supervisor demo quality-assurance record (8 November 2026)

**Scope and authority.** GitHub `alialnaggar/DealDeskOrchestrator`, `feature/supervisor-live-demo`, starting at `f7657e553cda1d3da9aeea50f62114b3c7d53685`. Checked the D0 demo plan, D2 source-grounded review contract, D3 offline API contract, D4 frontend README, implementation and tests. No hosted-model request, provider configuration, real evidence change, Phase 1C verifier edit, or held-out case edit is part of D5. All execution was `offline_scripted` on loopback; fault mutations were confined to freshly created `demo_api_*` databases under the disposable `/tmp/opencode` PostgreSQL cluster. This record describes **tested behavior, not a production security certification**.

## Inventory, boundaries and QA coverage matrix

The browser offers operator login/logout, two allowlisted scenario launch buttons, direct assessment URLs, durable status/timeline, six original-subject specialists, optional checked candidate comparison and human-only review. Next.js routes: `GET /api/auth/csrf`, `POST /api/auth/login`, `POST /api/auth/logout`, `POST /api/assessments`, `GET /api/assessments/[id]/{status,events,review}`. Next.js alone calls the bearer-authenticated Python `POST /demo/assessments`, `GET /demo/assessments/{id}`, `/events`, `/review`; there is no approval, reservation, acceptance, source-write or hosted-execution route. The checkpoint database holds the registry, append-only events and LangGraph state; the separate business database holds synthetic source evidence. The registry proceeds from accepted to running, then completed, stopped or uncertain; on restart in-flight work becomes uncertain and is **not replayed**. A completed status is served only while its checkpoint and current source verify. `409` withholds mismatched/incomplete evidence; `404` does not reveal another owner's assessment.

| Requirement / error boundary | Evidence (D5 unless noted) | Remaining gap |
| --- | --- | --- |
| Login, signed session, logout, expiry, CSRF and exact Origin | `frontend/tests/security.test.ts`, `e2e/offline.spec.ts` (cookie, rejected CSRF and Origin, logout, expired-cookie injection) | No remote identity, per-user rate limit or revocation store; intended loopback operator only. |
| Scenario allowlist; rapid clicks, lost response, retry key, concurrent same-key, conflict and per-owner isolation | `frontend/tests/launch.test.tsx`, `backend/tests/test_assessment_api.py`, `e2e/fault-injection.spec.ts` | Lost-response/retry is simulated in component tests; real concurrent posts tested; no browser-kill during a POST was injected. |
| Input sizes, IDs, query bounds, request-body rejection and safe errors | API integration tests, `frontend/tests/proxy.test.ts`, `frontend/tests/states.test.tsx` | No broad fuzz campaign or volumetric DoS test. |
| Owner isolation, bearer-only backend and browser proxy restrictions | API integration owner tests, server-proxy tests, `frontend/lib/security.ts`, `frontend/lib/backend.ts`; loopback socket inspection | No untrusted-network exposure or multi-operator load test. |
| Persisted accepted/running, six fixed and six scripted stages, ordered unique events, review-ready and refresh | Backend integration/full suite, real RC01/UC02 Playwright, fresh restart retrieval below | Screenshot timeline scroll area shows the first portion; API/test assertions cover all 21/20 events. |
| Stopped/uncertain, reserved-send interruption, no replay after worker kill | API integration tests, full backend suite, real in-flight SIGKILL/duplicate retry | Other precise mid-stage kill timings covered by simulation, not every graph instruction by real SIGKILL. |
| Database failure and recovery, API unavailable, interrupted polling | `test_assessment_api.py`, real checkpoint-database connection refusal/recovery and Python kill/restart, browser 503 injection | Does not simulate corrupt WAL or whole-cluster power loss. |
| Source drift, stale/incomplete evidence, checkpoint corruption and review withholding | API integration tests, real disposable source edit and checkpoint tamper in fault suite; post-restart `409` | One representative drift and corruption injection; not exhaustive malformed-checkpoint fuzzing. |
| Deterministic candidate lineage, original vs candidate subjects, candidate-only fixed checks | D2/backend projector tests, strict `frontend/lib/contracts.ts`, frontend contract/component tests, real RC01 DTO | No candidate-specific AI rerun by architecture. |
| Missing/null/unknown/abstained Credit; withheld routing vs no roles; long/empty refs | Frontend component/contract tests, UC02 real DTO + screenshot | Screen-reader behavior reviewed semantically, not independently audited with assistive technology. |
| Direct URL, refresh, history back/forward, 401/403/404/409/502/503 and invalid DTO | Playwright refresh/history/expired session/503/malformed status; component error tests; backend/proxy tests | Live browser 403/404 are covered at API/component level, not all via dedicated screenshots. |
| 390/768/1440px, keyboard focus, labels and no horizontal page overflow | Playwright viewport checks, screenshots, labeled buttons, focusable ordered timeline | Full mobile/tablet **workspace** screenshots and automated WCAG/contrast audit remain for D6. |
| No secret or raw checkpoint in browser, local-only, SQL/path safety | Restricted Next proxy, typed SQL/parameterized store paths, no-store/nosniff and Host checks, browser token assertion, sanitized error regression | Local logs and installed development tools require normal host access controls; no external penetration test. |

## Defect register

| ID | Severity | Discovery and disposition |
| --- | --- | --- |
| D5-01 | High | Rapid launch/lost-response retry could allocate a second key and duplicate a run. Fixed synchronous single-flight guard and per-scenario session-tab retry key; component and concurrent API/fault tests. |
| D5-02 | High | A previous completed banner/outcome could remain visible after polling/review failure. Commit status/events/review together; clear stale data and sanitize errors until validation succeeds again. Unit and real fault/browser tests. |
| D5-03 | Medium | Database exception could expose internal connection text or yield an unsanitized 500. Generic Python 503 plus regression for DSN-like exception and recovery; no-store and nosniff headers. |
| D5-04 | Medium | The frontend accepted inconsistent candidate lineage/quantities and could confuse routing withheld (`null`) with no required roles (`[]`). Strict review validation and explicit labels; contract/component tests. |
| D5-05 | Medium | Credit wording implied a completed original observation even for null or abstained execution. Render according to the verified execution state; regression tests and UC02 rehearsal. |
| D5-06 | Low | API Host header was not checked; focus/long-ref/narrow-screen presentation lacked safeguards. Exact local Host check, focusable trace, accessible scenario labels, wrapping CSS and viewport tests. |
| D5-07 | Low | README called the login CSRF cookie “one-time” although it is signed/expiring but not consumed. Corrected documentation; no false security claim. |

**Open defects:** none confirmed in the tested local workflow. This does not mean defect-free; incomplete coverage and the residual dependency risk below are explicitly retained.

## Security and dependency audit

- `npm audit --omit=dev`: **0** production advisories. Full lockfile `npm audit`: **8 moderate** dev-dependency findings in `eslint-config-next` / `typescript-eslint` / `minimatch` dependency paths, no high/critical. `npm audit fix --dry-run` proposed an `eslint-config-next` major/downgrade path; no breaking change was applied just to suppress counts. Do not run development tooling on untrusted repositories.
- `pip-audit -r backend/requirements-m1.1.lock`: **14 records** for `starlette==0.46.2`, **7 distinct advisory IDs** (some duplicated in feed). `fastapi==0.115.12` constrains `starlette<0.47.0`; fixes start at 0.47.2 and extend to 1.x. This is **residual known dependency risk**, not claimed fixed. The demo exposes no multipart/upload/static/FileResponse endpoint, disables interactive docs, binds only to `127.0.0.1`, checks Host and bounded POSTs; these mitigate known surfaces but are not a universal remedy. Re-evaluate compatible, fully tested framework upgrades before any network deployment.
- Auth is a long local bearer token between servers and an HMAC-signed HttpOnly SameSite=Strict operator session in browser; state-changing browser routes require signed CSRF plus exact loopback Origin. Cookies are not `Secure` because this is local HTTP, and sessions are not server-revocable except by secret rotation. The Next proxy rejects non-exact loopback API URL, constructs server paths from validated IDs, and validates upstream DTOs. SQL uses fixed schema queries and parameters; source identity and Phase 1C checkout are pinned; no user-supplied filesystem path is accepted by the HTTP API. Validation/DB errors are generic. Browser checks found no backend bearer token in HTML or review. This is **not** suitable for public binding, tunneling or proxy exposure.

## Final test evidence and browser rehearsal

| Check | Result |
| --- | --- |
| Backend full regression, eight fresh disposable databases | **372/372 passed**, 311.877 s (`/tmp/opencode/d5-backend-full.log`). Focused API regression also passed after hardening. |
| Frontend ESLint, TypeScript, Next.js production build | All passed. |
| Vitest unit/component/security/proxy tests | **26/26**, six files passed. |
| Real failure-injection Playwright (separate disposable fixture) | **1/1 passed**: API SIGKILL/restart, source drift/recovery, checkpoint tampering, checkpoint-DB refusal/recovery, concurrent duplicate requests, killed run `uncertain` after restart/no replay (`/tmp/opencode/d5-e2e-faults.log`). |
| Final real offline FastAPI + Next.js Playwright (fresh fixture) | **2/2 passed** (`/tmp/opencode/d5-final-browser.log`): login/logout/CSRF, refresh/history, 390/768/1440px, 503 and malformed response recovery, expiry and safe errors. |
| Final API restart after browser rehearsal | RC01 and UC02 still `completed`, validated reviews retrieved, event sequences exactly `1..21` and `1..20`; API remains `offline_scripted`. |

**RC01/B01** assessment `8a992af6456a4f849709c7c1e1ae81bf` (21 events): requested 10 units by **4 Sep 2026**; candidate 8 by **3 Sep** and 2 by **8 Sep**. Supply `supply_supported_unreserved`, reservation `not_reserved`, acceptance `pending`; original requested date remains unmet, candidate status `needs_revision`, routing roles withheld (`null`), and all candidate AI execution fields `null`. Full-page browser screenshot `/tmp/opencode/d5-rc01.png` was visually inspected: source-grounded comparison, human-only authority and separate fixed/scripted specialist columns are present. The screenshot shows a scrollable subset of the timeline; all events were checked via the API.

**UC02/N01** assessment `72d04ae5116948acaffaec1adeabd16c` (20 events): no candidate; fixed Credit `unknown`, evidence gaps `stale` and `unavailable`, original offline-scripted Credit stage `completed` **without credit clearance**. Screenshot `/tmp/opencode/d5-uc02.png` was visually inspected: no candidate or approval is implied. Screenshots/logs are disposable local evidence, not committed artifacts; exact run IDs are fixture-specific and not guaranteed on another installation.

## Remaining risks and readiness

**Known residual security issue:** Starlette advisories in the pinned FastAPI stack, plus dev-only npm advisories (above). **Deliberate architectural limits, not D5 defects:** scripted rather than hosted model behavior; synthetic allowlisted cases, no candidate-specific AI, no multi-candidate revision loop, no stock reservation/customer acceptance/approval, local single-operator HTTP with no remote auth or revocation, and unsafe-to-replay interrupted sends intentionally remaining `uncertain`. **Coverage gaps:** fuzzing, power-loss/load/DoS testing, independent screen-reader/contrast audit, exhaustive stage-by-stage process kills and full workspace responsive screenshots. Do not present this as production-ready.

**Readiness:** suitable to enter D6 UI refinement and a supervised **local offline** rehearsal with the documented limitations and a disposable fixture. Re-run the checks above after any D6 contract, framework or authorization change. No paid/hosted AI calls were made in this D5 execution; dependency advisory queries and package audit metadata are not model-provider calls.
