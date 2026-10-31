# Coding-agent model selection and escalation guide

Status: Working guidance (25 October 2026). This is a developer workflow guide, not an approved change to the six specialist runtime contracts.

## Separate the two model layers

1. **Coding assistant**: Slack → OpenCode/OpenACP → coding model. This model reads and changes the repository, runs tests, and prepares pull requests.
2. **Thesis runtime**: The six Deal Desk specialists invoke an LLM through controlled, provider-independent interfaces. Their business decisions remain subject to deterministic verification and human approval.

Changing the coding assistant's model does **not** change the thesis runtime provider. Do not conflate OpenCode/Codex usage with paid OpenAI API calls made by the thesis.

## Current coding-model recommendations

Available models reported by the operator on 25 October 2026. These are provisional choices, **not independently benchmarked quality rankings**.

| Work | Select | Reason / constraint |
| --- | --- | --- |
| Correctness-sensitive implementation, LangGraph/checkpoints, specialist contracts | `openai/gpt-5.5` | Conservative default for the next bounded Fulfillment correction increment |
| Difficult independent review / second opinion | `openai/gpt-6-astra` | Different model for reviewing sensitive changes; validate output independently |
| Straightforward tests and small edits | `opencode/glm-5.3-flash-free` | Save paid usage when the task is bounded and easy to verify |
| Repository reading, formatting, simple documentation | `opencode/beam-free` | Lower-cost default for low-risk work |

The `openai/` prefix alone does not verify which paid account, subscription, or API billing path OpenCode uses. Check the actual provider connection, availability, and usage before initiating expensive work. If the recommended model is unavailable or its billing route is unclear, stop and ask rather than silently switching to a costly model.

## ChatGPT versus Slack/OpenCode

**ChatGPT: architecture, scope, governance, acceptance criteria, independent review.** Consult at milestone start; when the coding agent proposes changing contracts, permission boundaries, provider/runtime strategy, evaluation methodology, pinned Phase 1C data, checkpoint semantics, budgets, or scope; when blocked; and at PR completion.

**Slack/OpenCode: implementation within approved scope.** Continue autonomously for repository inspection, code changes, focused and regression tests, ordinary bug fixes, docs, commits, and PR preparation. Do not require a ChatGPT round-trip for every coding message or minor failure.

At a milestone end, send ChatGPT the branch, commit SHA, PR link, changed files, tests and CI links, remaining failures, and deviations. ChatGPT should verify repository evidence rather than accept the coding agent's self-report.

## Slack conversation handling

For a new milestone, start a **fresh OpenCode/OpenACP conversation/session** through the Slack integration's supported session/new-chat control. Do not assume that posting in a new Slack thread necessarily creates a fresh underlying OpenCode session. Verify the session identifier or reset confirmation. Do not invent an unverified Slack command. Select the coding model for that new session and provide the full scoped task with repository/branch, constraints, and acceptance tests.

## Next bounded work

1. Implement the approved **same-specialist Fulfillment correction prototype** using offline model doubles, checkpoint-safe attempt accounting, bounded feedback, full revalidation, and disposable PostgreSQL tests.
2. Continue bounded Groq free-tier reliability tests and offline M2.1 Credit contract work. Gemma 4 is permanently discontinued; the future paid OpenAI production strategy requires separate approval for model, adapter, cost and security. Preserve provider-independent specialist boundaries.
3. Continue M2.0/M2.1 specialist implementation under their current approved gates; do not couple it to a discontinued provider migration.

## Safety and source-of-truth rules

- GitHub repository is authoritative; inspect current branch head and approved Phase 2 blueprint before coding.
- Preserve pinned Phase 1C reader SHA unless explicitly approved otherwise.
- Deterministic rules/tools remain authoritative; models do not approve deals or bypass human review.
- Use live Groq only under its approved free-tier development gates; do not use paid runtime APIs without explicit approval and budget. No Gemma calls.
- Keep unrelated Phase 1C and Odoo/n8n infrastructure untouched.
- Prefer a coherent, testable increment over many tiny PRs; stop for material architectural changes.
