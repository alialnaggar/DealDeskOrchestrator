# Reviewed, project-local guidance for the supervisor demo

Only Markdown guidance was copied; no installers, hooks, packages, binaries or remote code were run. The upstream versions are pinned below. The local copies are intentionally smaller than the upstream bundles.

| Local skill | Source | Pinned revision | Local changes |
| --- | --- | --- | --- |
| `vercel-react-best-practices` | [Vercel React Best Practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices) (MIT per skill metadata) | `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` | Only three reviewed rule files copied; `SKILL.md` notes the subset. |
| `frontend-ui-engineering` | [Addy Osmani UI engineering](https://github.com/addyosmani/agent-skills/tree/main/skills/frontend-ui-engineering) and its [accessibility checklist](https://github.com/addyosmani/agent-skills/blob/main/references/accessibility-checklist.md) (MIT repository) | `301b02b12bff98e4688e6984af6556802322bbde` | Checklist moved alongside the skill; link changed to `./references/accessibility-checklist.md`. |

[OpenCode V2 documents `.agents/skills/` discovery](https://opencode.ai/v2/docs/skills). OpenACP is installed on this host, but its end-to-end skill discovery was not independently confirmed; the reviewed advice was applied directly to this frontend. This directory is not a dependency of the running application.
