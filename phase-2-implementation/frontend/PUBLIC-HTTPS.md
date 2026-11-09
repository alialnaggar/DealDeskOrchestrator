# Supervisor demo public HTTPS (synthetic, offline-scripted only)

Approved exception to the former loopback-only **browser access** policy: `https://dealdeskdemo.duckdns.org` serves the login page through the existing n8n/Odoo Caddy container. No browser reaches Python, PostgreSQL or Next.js directly. The operator login, strict DTOs, exact-Origin/Host CSRF check and human-only authority are unchanged. Frontend cookies are `Secure` for this HTTPS origin.

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
- `/etc/systemd/system/dealdesk-supervisor.service` runs as `ubuntu`, with the same `npm run start` loopback argument and existing owner-only `/tmp/opencode/d6-{token,password,session}` files. `DEALDESK_UI_ORIGIN` is exactly `https://dealdeskdemo.duckdns.org`. No secret contents appear in the service unit or in Git. Frontend, relay socket and narrow firewall units are enabled at boot.

**Reboot limitation:** The current Python API and disposable PostgreSQL test cluster were already launched outside systemd. Caddy, frontend and bridge relay restart automatically, but a **full VM reboot has not been tested and the backend/fixture may need the existing D3/D6 runbook to be restarted** before assessments work. Do not claim an unattended end-to-end reboot recovery until that is separately verified. Avoid modifying shared databases or the existing n8n/Odoo services for this demo.

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

The public login page is intentionally reachable without an IP allowlist. The operator password is still required to create/read assessments. This is not hardened production authentication: there is no login rate limiter, remote identity provider or server-side session revocation store. Rotate the password and session key after the demonstration, and do not put real customer data or credentials into the synthetic demo.
