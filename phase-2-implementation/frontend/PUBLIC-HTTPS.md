# Supervisor demo public HTTPS (synthetic, offline-scripted only)

Approved exception to the former loopback-only **browser access** policy: `https://dealdeskdemo.duckdns.org` serves the synthetic demo through the existing n8n/Odoo Caddy container. No browser reaches Python, PostgreSQL or Next.js directly. Strict DTOs, exact-Origin/Host CSRF checks and human-only authority remain in force. Frontend cookies are `Secure` for this HTTPS origin.

**Public demo mode:** The frontend service sets `DEALDESK_PUBLIC_SYNTHETIC_DEMO=1` alongside the *exact* HTTPS `DEALDESK_UI_ORIGIN`. Only this combination allows the `/api/auth/csrf` route to issue a signed demo session without an operator password. The password endpoint is disabled in that mode; without the opt-in, local password authentication remains the default. Session-bound CSRF, the two-code POST allowlist, random assessment IDs, validated DTOs and Python's loopback bearer token remain. A process-local global/per-session rate limit throttles scenario **creation** (8 new runs/minute, 40/hour globally; 4/minute and 12/hour per session). Idempotent retries retain their key; accepted requests are capped at 30/minute, 120/hour globally. This is not comprehensive DDoS protection or production identity management.

## VM wiring (2026-11-09)

- DuckDNS `dealdeskdemo.duckdns.org` resolves to the VM public IPv4. The existing Caddy container `n8n-caddy-1` owns ports 80/443, has a persistent `/data` volume and `unless-stopped` restart policy. It obtains and automatically renews its publicly trusted Let's Encrypt certificate. Existing `rofo-n8n.duckdns.org` and `rofo-odoo.duckdns.org` virtual hosts remain intact.
- The host file `/home/ubuntu/n8n/Caddyfile` was backed up to `/home/ubuntu/n8n/Caddyfile.pre-dealdesk-20261109` before editing. Its additional block is:

  ```caddyfile
  dealdeskdemo.duckdns.org {
      reverse_proxy 172.18.0.1:13000
  }
  ```

- The Docker bridge `n8n_default` has host gateway `172.18.0.1`. Systemd's **socket** `/etc/systemd/system/dealdesk-supervisor-relay.socket` binds only `172.18.0.1:13000`, activating `/etc/systemd/system/dealdesk-supervisor-relay.service` (`systemd-socket-proxyd 127.0.0.1:3000`). The original Next.js listener remains `127.0.0.1:3000`; FastAPI remains `127.0.0.1:8765`.
- `/etc/systemd/system/dealdesk-supervisor-relay-firewall.service` persists one INPUT rule permitting TCP 13000 only from `172.18.0.0/16` on `br-3c1a844e060c` to the gateway address. The public IP has no listener on 13000, 3000 or 8765. The Docker bridge identifier and gateway must be rechecked if the n8n Docker network is recreated. Do not broaden the rule to public interfaces.
- `/etc/systemd/system/dealdesk-supervisor.service` runs as `ubuntu`, with the same `npm run start` loopback argument and existing owner-only token and session-secret files under `/tmp/opencode/`. `DEALDESK_UI_ORIGIN` is exactly `https://dealdeskdemo.duckdns.org`; `DEALDESK_PUBLIC_SYNTHETIC_DEMO=1` is the opt-in. The unused operator password is **not loaded into the public frontend process** (the owner-only file remains for local-mode rollback). No secret contents appear in the service unit or in Git. Frontend, relay socket and narrow firewall units are enabled at boot.

**Reboot limitation:** The current Python API and disposable PostgreSQL test cluster were already launched outside systemd. Caddy, frontend and bridge relay restart automatically, but a **full VM reboot has not been tested and the backend/fixture may need the existing D3/D6 runbook to be restarted** before assessments work. Do not claim an unattended end-to-end reboot recovery until that is separately verified. Avoid modifying shared databases or the existing n8n/Odoo services for this demo.

**Final audit recovery check (2026-11-09):** Restarted only `dealdesk-supervisor.service`; the passwordless HTTPS homepage and persisted assessments remained readable afterwards, and Caddy, n8n and Odoo continued responding. Inspected the API process and the disposable PostgreSQL cluster: the API runs from a manually started shell, and the demo database is a manually started Unix-socket-only PostgreSQL process with data under `/tmp/opencode/dealdesk-remediation-pgdata`. Neither has a dedicated enabled boot unit. This is *not* evidence of unattended backend or database recovery after a process failure or full VM reboot. No database, API, shared container or VM restart was attempted during the audit.

## Verification and safe rollback

```sh
systemctl status dealdesk-supervisor.service dealdesk-supervisor-relay.socket dealdesk-supervisor-relay-firewall.service
sudo docker exec n8n-caddy-1 caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
curl -I https://dealdeskdemo.duckdns.org/
curl -I https://rofo-n8n.duckdns.org/
curl -I https://rofo-odoo.duckdns.org/
ss -lnt '( sport = :3000 or sport = :8765 or sport = :13000 )'
```

To remove *only* the Deal Desk exposure in an emergency, restore the backed-up Caddyfile after checking it still matches the two preexisting hosts, validate it with the `caddy validate` command above, then gracefully reload using `sudo docker exec n8n-caddy-1 caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile`. Do not restart the shared container. The relay can then be disabled with `sudo systemctl disable --now dealdesk-supervisor-relay.socket dealdesk-supervisor-relay-firewall.service`; the firewall unit's stop removes only its own rule. The frontend can remain loopback-only, but local HTTP login requires restoring its local `DEALDESK_UI_ORIGIN` and restarting it. Never copy or commit the owner-only credential files.

The public homepage is intentionally reachable without an IP allowlist or password. Anyone can run and inspect the **two** allowlisted synthetic assessments, but no other scenario or unrestricted Python API. There is no remote identity provider or server-side session revocation store, and the in-memory creation cap resets on frontend restart. The current password secret remains stored for local-mode rollback; rotate it and the session key after the demonstration. Do not put real customer data or credentials into this demo.
