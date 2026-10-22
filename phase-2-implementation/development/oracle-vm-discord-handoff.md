# Oracle VM, OpenCode 2 and Kimaki/Discord — setup and handoff plan

**Status:** Prepared 22 October 2026; **not deployed or verified on the VM**. This guide is a proposed procedure requiring Ali's approval before changing the host, Discord server or authentication. It does not assert that Python, Node, OpenCode 2, GitHub access, PostgreSQL isolation, Discord or a service already work. Odoo and n8n are unrelated and must remain untouched. GitHub remains the only repository source of truth. Runtime AI provider is provisional Groq; coding-assistant subscription access is a separate authentication surface.

**Official references checked 22 October 2026:** [Kimaki agent setup](https://kimaki.dev/docs/guides/agent-machine-setup), [Kimaki subscriptions](https://kimaki.dev/docs/getting-started/subscriptions), [Kimaki access control](https://kimaki.dev/docs/configuration/access-control), [Kimaki tool permissions](https://kimaki.dev/docs/configuration/permissions), [Kimaki advanced setup](https://kimaki.dev/docs/guides/advanced-setup), [OpenCode 2 installation](https://opencode.ai/v2/docs), [OpenCode providers](https://opencode.ai/docs/providers/) and [GitHub deploy-key guidance](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys). Review these again during deployment; installation flags and provider availability can change. Kimaki's **published CLI** uses OpenCode 2 on the same machine, with a gateway bot; it does not control the Codex IDE extension. Kimaki advises `npx -y kimaki@latest --gateway` and explicitly says not to clone its repo to run the bot. Its published setup requires Node 20+ and Git. If OpenCode 1 is installed, stop before replacing it; do not assume an upgrade is harmless.

## 1. Mental model and boundaries

A private Discord channel maps to a single project directory on the Oracle VM; a Discord thread maps to an OpenCode session. Kimaki bridges Discord to the OpenCode 2 service on the VM. OpenCode uses a coding model you explicitly authenticate. The code it edits is a Git working copy; no Discord message is an accepted architecture decision until reviewed and committed to GitHub. Runtime Groq calls in thesis code use `GROQ_API_KEY` only in separately approved experiments and do not come from Kimaki's coding-model login.

Keep a dedicated Unix identity and directory for this thesis if permitted by the VM administrator. This is the simplest enforceable boundary from unrelated Odoo/n8n services. Avoid giving the coding agent `sudo`, Docker socket access, system service control or broad `/home/ubuntu` and database superuser rights. Do not attach the existing n8n or Odoo Docker networks, containers or PostgreSQL volumes. If a new OS user is not allowed, use a dedicated directory and explicit file/database permissions and record the weaker isolation before proceeding. No deployment action in this guide has been performed.

## 2. Ordered preflight (read-only; report before changing anything)

Ali or the authorized VM operator signs in using the established secure SSH method. Run only read-only checks first, preferably as the proposed thesis user. Do not print secrets, database connection strings or auth files:

```bash
whoami
pwd
uname -m
lsb_release -ds
command -v git
command -v python3.12
python3.12 --version
command -v node
node --version
command -v npx
command -v opencode
opencode --version
command -v psql
psql --version
```

Record which checks are missing and whether the host is ARM64/aarch64; confirm published installers and locked Python wheels support that architecture before running an installer. Inspect disk/memory/headroom and known allocated ports with the VM operator. **Do not infer safety from the presence of a GitHub clone or a running PostgreSQL service.** Check the current thesis checkout's branch and dirtiness before touching it:

```bash
git -C /ABS/PATH/TO/DEALDESK status --short --branch
git -C /ABS/PATH/TO/DEALDESK remote -v
git -C /ABS/PATH/TO/DEALDESK rev-parse HEAD
```

Replace placeholders with approved paths; never paste credential-bearing remote URLs into Discord. If an existing checkout is dirty or divergent, preserve it and use a new dedicated clone instead of resetting it. Host-wide installation (`apt`, Node upgrade, `loginctl`, PostgreSQL cluster or systemd changes) requires an explicit setup review, especially because Odoo/n8n share the VM.

## 3. Dedicated checkout and minimum GitHub access

Prefer a **read-only repository deploy key** for the first clone, limited to `alialnaggar/DealDeskOrchestrator`. Ali adds the public half through GitHub repository settings; the private half stays in the thesis Unix user's `~/.ssh` with restricted permissions. A read-only key cannot push; that is useful while validating the bot. Later, if Ali approves VM pushes, use a separately reviewed repository-scoped fine-grained credential or a dedicated write deploy key, and keep branch protections/CI review. Do not reuse a personal all-repository token or copy the current workstation's private SSH key. The VM agent must not be allowed to modify the Phase 1C draft PR by default. GitHub Actions already checks out the private pinned SHA with read permission.

After auth is confirmed, clone to a dedicated path such as `/home/dealdesk/projects/DealDeskOrchestrator`; pin the Phase 1C source in a **separate** checkout, never copying its module files into Phase 2. Example commands for an authorized operator:

```bash
mkdir -p /home/dealdesk/projects
cd /home/dealdesk/projects
git clone git@github.com:alialnaggar/DealDeskOrchestrator.git DealDeskOrchestrator
cd DealDeskOrchestrator
git fetch origin
git switch phase2-agent-implementation
git status --short --branch
git worktree add ../dealdesk-m20 -b m20-config-pricing origin/phase2-agent-implementation
git worktree add --detach ../phase1c-pinned 90c0bc8e285ee69262c7db826b786096a77ad004
git -C ../phase1c-pinned rev-parse HEAD
```

Only create the feature branch when M2.0 is separately approved; this is an example, not an instruction to begin it now. Keep the original Phase 2 checkout a clean integration reference. Register **one feature worktree** as a Kimaki project channel; separate tasks can use separate reviewed worktrees/branches. Do not bind one channel to the repository parent directory, which would expose other projects. A `git worktree --detach` Phase 1C source is read-only by convention; filesystem permissions and code review must enforce the no-modification boundary.

## 4. Python and PostgreSQL for local verification

Python 3.12 is the tested runtime. In the approved Phase 2 worktree, create a local virtual environment and install only the existing lock:

```bash
cd /home/dealdesk/projects/dealdesk-m20
python3.12 -m venv .venv
.venv/bin/python -m pip install -r phase-2-implementation/backend/requirements-m1.1.lock
.venv/bin/python -m pip check
```

The repo ignores the virtual environment. Do not `sudo pip install`, rewrite the lock, or introduce a package merely to make setup convenient. If the VM does not have Python 3.12 or `venv`, propose the exact user-space or package installation first and check impact on other services.

Use a **separate thesis PostgreSQL role and disposable databases** for Phase 1C fixtures and LangGraph checkpoints. Prefer the existing PostgreSQL installation only if the operator can create those isolated resources without changing cluster configuration, ports, user permissions or Odoo/n8n databases. If isolation is unavailable, pause and propose an alternative for approval; do not silently start a new Docker Postgres container. The role should own only its thesis databases, not be a superuser. Set local connection environment variables through a user-owned file outside Git (`chmod 600`) or a reviewed secret store; avoid printing them. CI provides its own disposable service and separate checkpoint database.

To reproduce the existing CI, follow `.github/workflows/phase2-m1-contracts.yml` exactly: verify `DEALDESK_PHASE1C_CHECKOUT` resolves to the pinned SHA, load only disposable pinned schema/reference rows and compiled rules, then run `python -m unittest discover -s phase-2-implementation/backend/tests -p 'test_*.py' -v` with `PYTHONPATH=phase-2-implementation/backend` and the CI-matching database variables. Never aim fixture loads at a shared database. Run offline checks before database checks; do not invoke any `--live` runner without new explicit authorization.

## 5. OpenCode 2 and subscription login

After the preflight and setup approval, install OpenCode 2 for the thesis user using its **current official installer** and check `opencode --version`. The Kimaki agent-setup page currently documents `curl -fsSL https://opencode.ai/v2/install | bash`; inspect the installation script or select an official package method in the setup review before execution. Do not install over an existing OpenCode 1 without consent. Confirm supported models via OpenCode, rather than assuming a model listed in `AGENTS.md` remains free or available.

OpenCode supports its own `/connect` or `opencode auth login` flow. Kimaki offers `/login` in a project channel; its documentation says ChatGPT Plus/Pro OAuth is built into OpenCode, while credentials are stored by OpenCode and shared between the OpenCode TUI and Kimaki. Only the Discord server owner or Administrator may run `/login`. Ali completes the browser/device-code authorization manually. Do not paste an OAuth code or API key into a project thread. Confirm a small **read-only** coding task works before enabling edits. This authenticates OpenCode coding sessions; it does not import a Codex IDE extension session or grant runtime Groq API credit. Model selection `/model` is an explicit coding-model choice, subject to existing cost policy.

## 6. Kimaki gateway, Discord and permissions

For the first test, run the official published CLI **in the foreground** as the thesis user, after ensuring Node 20+ and Git:

```bash
npx -y kimaki@latest --gateway
```

Kimaki may install OpenCode 2 if missing, so install/verify it deliberately first. The gateway emits a short-lived `install_url` containing a client secret. Ali opens that URL privately in a logged-in Discord browser, selects a **new private server** and presses Authorize. Never post the URL in Discord or a public log. Kimaki then creates its own machine category, channel and onboarding thread; do not create a custom Discord application unless self-hosted mode is separately chosen. Map only the approved Phase 2 worktree from another shell after authorization:

```bash
npx -y kimaki@latest project add /home/dealdesk/projects/dealdesk-m20
npx -y kimaki@latest status
npx -y kimaki@latest project list
```

These commands are the published gateway/project flow; verify `running` and `connected:true`. Kimaki's access control processes messages from the server owner, administrators, Manage Server users and holders of a role named `Kimaki`. Use a private server, grant that role only to explicitly trusted participants, restrict channel visibility, avoid other admin/Manage Server assignments, and do not grant it to other bots. Test that an unauthorized account cannot trigger a session. Note that a project channel ordinarily treats each message as a session request; mention mode is available for busier channels. Configure OpenCode tool permissions to require approval for shell commands or access outside the project; in particular, deny external paths, deployment, arbitrary `sudo`, `docker`, database write tools, force pushes and secret reads. Discord authorization controls **who may ask**, and OpenCode permissions control **what the agent may do**; both are needed. Review actual permissions with a harmless test before leaving the gateway unattended.

## 7. Long-running operation, secrets and rollback

After the foreground proof succeeds, choose one persistent method during deployment review. Kimaki's official VPS guide favors its Docker setup, but using that on this shared Odoo/n8n VM would introduce host/container changes; propose it separately if desired. A user-scoped systemd service is a plausible simpler alternative **only after** verifying `npx`'s absolute path, user service availability and the installed Kimaki version. Example *template*, not an applied unit:

```ini
[Unit]
Description=Thesis Kimaki gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/dealdesk/projects/DealDeskOrchestrator
ExecStart=/ABS/PATH/TO/npx -y kimaki@REVIEWED_VERSION --gateway
Restart=on-failure
RestartSec=10
UMask=0077

[Install]
WantedBy=default.target
```

For the example user service, install under `~/.config/systemd/user/` as the thesis account and verify the user-specific `HOME`/PATH; a system service instead needs an explicit `User=dealdesk` and a separate review. Keep gateway state under the thesis user's private directory and never put login tokens or the install URL in `Environment=` or a committed unit. Decide whether user linger is needed only after the foreground test, with administrator approval. Check restart, logs, session resumption and resource impact before relying on it; stop/disable the thesis service to roll back, leaving Odoo/n8n untouched. Do not bind OpenCode's local server publicly or create an inbound VM firewall rule merely for Discord gateway mode.

## 8. Daily development and safe handoff

1. In a **new** Discord thread, ask OpenCode to read `AGENTS.md`, the [master blueprint](../planning/master-implementation-blueprint.md), the exact current branch and CI. Confirm the checkout path and branch before edits. Ask for a narrow diff and test plan. Keep source-first evaluation answer keys out of model-visible prompts.
2. Work only on the approved Phase 2 feature branch/worktree. Inspect `git status --short --branch`, `git fetch origin`, diff and tracking divergence; use `git pull --ff-only` only on a clean compatible checkout. Never reset, force-push or merge the Phase 1C draft PR silently.
3. Run offline tests and disposable PostgreSQL integration. Confirm no live Groq call occurred. Have an independent review for business/identity changes. Before push, inspect the actual diff, secret scan and current branch, then commit one bounded change. A human reviews the commit/PR and GitHub Actions. Failed CI is corrected, not hidden.
4. At handoff, write the branch/SHA, exact Phase 1C pin, tests and CI links, limitations, open decisions and next safe step into the Phase 2 roadmap or progress record. GitHub is the shared memory between Codex, OpenCode and any later Claude Code session.

### Ali's manual steps at the deployment approval gate

- Approve the specific VM account/isolation and system package plan after the read-only preflight; grant only the minimum GitHub repository access and confirm no Odoo/n8n database or container is touched.
- Create or select the private Discord server and authorize Kimaki through the private install URL; grant the `Kimaki` role only to trusted members.
- Complete OpenCode's ChatGPT subscription OAuth personally if supported for the desired model. Confirm any pricing or usage limits before enabling another coding provider.
- Review the first agent permissions, feature branch and service persistence plan. Approve host installation/service changes separately. Review commits and CI before merging or activating a new runtime provider.

**Stop condition:** a missing preflight dependency, OpenCode 1 conflict, dirty checkout, database isolation gap, unsupported ARM64 package, failed login or overly broad Discord/Git access pauses setup. This document alone authorizes no VM or Discord change.
