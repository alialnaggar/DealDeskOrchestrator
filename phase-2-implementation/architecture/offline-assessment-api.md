# D3 — authenticated offline assessment API (demo-only)

This is a loopback-only, **scripted offline** integration runner, not a hosted-model endpoint or an approval system. The production execution path imports no test doubles, monkeypatches or HTTP model clients: `assessment_service.py` supplies explicit `offline_double` actions through the existing M2.0, Fulfillment and M2.1 model protocols. The B01 proposal is a predefined synthetic *hypothesis* constrained to B01/RC01; the Fulfillment tool must return its sources, the existing Phase 1C candidate verifier must check it, and the D2 projector must validate the checkpoint before the API serves it. The N01/UC02 script abstains without a candidate. AI-origin labels denote the existing specialist slot, **not a fresh hosted inference**; every API response labels execution `offline_scripted`. This workflow does not create V2, call a provider, modify source evidence, reserve stock, accept terms or authorize a deal.

## Installation, fixture setup and startup

From the repository root, with the pre-existing **local disposable** PostgreSQL cluster on `/tmp/opencode` port 55539 and an exact pinned Phase 1C checkout at commit `90c0bc8e285ee69262c7db826b786096a77ad004`:

```sh
/tmp/opencode/dealdesk-test-venv/bin/python -m pip install -r phase-2-implementation/backend/requirements-m1.1.lock
PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests \
  /tmp/opencode/dealdesk-test-venv/bin/python phase-2-implementation/backend/tests/setup_assessment_api.py \
  --cluster-dsn 'host=/tmp/opencode port=55539 user=ubuntu dbname=postgres' \
  --phase1c /tmp/opencode/dealdesk-phase1c-pinned \
  --pg-bin /tmp/opencode/dealdesk-pg16/root/usr/lib/postgresql/16/bin \
  --pg-lib /tmp/opencode/dealdesk-pg16/root/usr/lib/aarch64-linux-gnu \
  --env-file /tmp/opencode/dealdesk-api-local.env
source /tmp/opencode/dealdesk-api-local.env
export DEALDESK_DEMO_OWNER=operator
export DEALDESK_DEMO_TOKEN="$(/tmp/opencode/dealdesk-test-venv/bin/python -c 'import secrets;print(secrets.token_hex(32))')"
PYTHONPATH=phase-2-implementation/backend \
  /tmp/opencode/dealdesk-test-venv/bin/python -m dealdesk_phase2.assessment_api
```

The setup script writes a new business database containing the existing **synthetic** Phase 1C reference, M1.8 B01/N01 cases and RC01/UC02 overlays; a separate new checkpoint database receives `backend/migrations/001_demo_assessment_registry.sql`. Both are created on the explicitly checked disposable cluster; the API never provisions or writes business data, and its business connections set `default_transaction_read_only=on`. The script creates `/tmp/opencode/dealdesk-api-local.env` as `0600` and refuses to overwrite it. No database cleanup or shared-service changes are automatic. The three environment variables in the file are `DEALDESK_DEMO_BUSINESS_DSN`, `DEALDESK_DEMO_CHECKPOINT_DSN`, and `DEALDESK_PHASE1C_CHECKOUT`. The two additional required variables are `DEALDESK_DEMO_OWNER` and a secret `DEALDESK_DEMO_TOKEN` (at least 32 characters). Do not commit, print or forward the token. No Groq/OpenAI key is loaded. Startup refuses non-disposable, remote, shared or identical business/checkpoint databases; the Python entry point binds only `127.0.0.1:8765`, disables access logs, and runs a single API owner per registry (PostgreSQL advisory lock). Do not run it through an externally bound ASGI server or public tunnel; no remote user authentication/TLS design is claimed.

## HTTP contract

All four routes require `Authorization: Bearer <configured local token>` and owner-scoped lookup; unauthorized returns 401, other owners' IDs return 404. Requests are restricted to 512 bytes; POST requires `Idempotency-Key` (8–128 allowed characters) and JSON with exactly one field: `scenario` = `B01/RC01` or `N01/UC02`. Status/events are versioned by the API service (`demo-api-v1` implementation); no CORS or introspection endpoints are enabled.

```sh
curl -sS -X POST http://127.0.0.1:8765/demo/assessments \
  -H "Authorization: Bearer $DEALDESK_DEMO_TOKEN" \
  -H 'Content-Type: application/json' -H 'Idempotency-Key: demo-b01-001' \
  --data '{"scenario":"B01/RC01"}'
curl -sS http://127.0.0.1:8765/demo/assessments/ASSESSMENT_ID \
  -H "Authorization: Bearer $DEALDESK_DEMO_TOKEN"
curl -sS 'http://127.0.0.1:8765/demo/assessments/ASSESSMENT_ID/events?after=0' \
  -H "Authorization: Bearer $DEALDESK_DEMO_TOKEN"
curl -sS http://127.0.0.1:8765/demo/assessments/ASSESSMENT_ID/review \
  -H "Authorization: Bearer $DEALDESK_DEMO_TOKEN"
```

POST returns **202** with an accepted ID, even if the worker finishes before the client polls; repeating a key with identical scenario returns the same ID with `created:false`, while changing the scenario returns 409. GET review returns 409 until completion or when the source/checkpoint differs. Event pages contain up to 100 persisted, timestamped rows, monotonic per assessment; `after` is exclusive. `accepted`, `running`, `preflight_ok`, `checkpoint`, `fixed_completed`, `ai_completed`, `review_ready`, `stopped`, and `uncertain` are durable *observations*. A fixed or AI completion event is emitted only after the relevant checkpoint has been read and its execution status checked. The six original fixed and six original AI observations are not candidate AI reruns. A candidate checkpoint event means deterministic candidate checks completed, not authorization.

Sanitized excerpt from an **actual offline HTTP integration execution** (dynamic IDs/hashes shortened, not a hosted receipt):

```json
{"version":"demo-api-v1","assessment_id":"725e…","scenario":"B01/RC01","mode":"offline_scripted","status":"completed","last_sequence":21}
{"version":"demo-api-v1","assessment_id":"725e…","events":[{"sequence":1,"kind":"accepted","stage":null},
 {"sequence":3,"kind":"preflight_ok","stage":"original"},
 {"sequence":15,"kind":"ai_completed","stage":"fulfillment"},
 {"sequence":16,"kind":"checkpoint","stage":"candidate"},
 {"sequence":21,"kind":"review_ready","stage":"review"}]}
{"version":"source-grounded-review-v1","authorization":"human_only_not_granted",
 "original":{"requested_delivery_date":"2026-09-04","lines":[{"quantity":10}],
   "availability":[{"quantity_by_requested_date":"8.000"}]},
 "candidate":{"business_status":"needs_revision","required_roles":null},
 "candidate_comparison":{"proposed_slices":[{"quantity":8,"delivery_date":"2026-09-03"},
   {"quantity":2,"delivery_date":"2026-09-08"}],
   "fixed_supply_status":"supply_supported_unreserved","reservation_status":"not_reserved",
   "customer_acceptance":"pending","unmet_customer_constraints":["original_requested_delivery_date"]}}
```

The actual event entries also include `assessment_id` and `occurred_at`, and the full review is the D2 typed allowlist—not these abbreviated examples. In particular, no raw checkpoint, model output, private invoice, provider receipt or secret is returned. `GET review` reopens a separate checkpoint connection, checks owner, source digest, sealed identity and pending graph state, rereads the source to reject drift, then invokes `project_source_grounded_review` exclusively. It does **not** claim receipt verification. The registry schema enforces append-only event rows; a lost running/queued worker is marked `uncertain` on server restart and is never resumed automatically. Retrying an idempotency key cannot restart it: request a *new* assessment after human review of the stopped state.

**Limits / frontend gate:** Polling returns persisted boundaries, not individual token/tool streaming. The scripted RC01 hypothesis is a demonstration of validation, not a model accuracy or speed measurement. Single operator per configured server and loopback binding are suitable for local demo only; external access would require separately reviewed TLS, multi-user identity, deployment/secret management and field-level permissions. D4 may consume only these allowlisted status/event/review endpoints **from a local server-side component**; the operator token must never be sent to the browser. D4 must label offline execution and preserve human-only approval/acceptance semantics. No permissive CORS or public listener is present.

## Offline verification

`PYTHONPATH=phase-2-implementation/backend:phase-2-implementation/backend/tests` with a pinned checkout and a disposable PostgreSQL fixture: `python -m unittest -v test_assessment_api` passed **6/6 in 16.691 s** on the final focused code. The `setup_assessment_api.py` CLI separately provisioned a fresh database pair, and an authenticated `TestClient` invocation against `create_app_from_env()` produced one completed 21-event RC01 assessment and the verified candidate comparison excerpt above. An earlier full-suite run reported **one setup error** because the new test tried to overlay cases before installing M1.8 fixture rows; the test now installs missing synthetic rows only into its own fresh clone. The final `python -m unittest discover -s phase-2-implementation/backend/tests -p 'test_*.py' -v` passed **370/370 in 305.049 s**, zero errors/failures/skips, using eight freshly provisioned disposable PostgreSQL databases and the exact committed code. No hosted inference POST was made.
