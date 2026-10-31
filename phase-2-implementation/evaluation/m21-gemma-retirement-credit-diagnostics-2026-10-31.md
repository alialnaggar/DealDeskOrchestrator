# Gemma retirement and Credit-contract diagnosis — 31 October 2026

**Current decision:** Ali permanently discontinued Gemma. The experimental
untracked adapter/runner/diagnostic modules, three Gemma test modules, three
Gemma-only design/trial reports, eight ignored local saved-result/audit files,
nine Gemma-only bytecode files and fifty explicitly named local trial-log
files were removed. Historical reports that mention past work retain their
original dates and counts; the decision log and active architecture/roadmap
supersede any former provider-selection advice. Shared Groq transport,
LangGraph checkpoints, pinned Phase 1C evidence, fixed rules, Credit fixtures
and future separately approved OpenAI production direction were not removed.
Gemma-named PostgreSQL server logs and historical databases were **not**
deleted: they may belong to the running shared test cluster; credentials and
unrelated services were not inspected.

## Full local verification

After removal, **the complete discoverable Phase 2 backend suite passed:
331 run, 331 passed, 0 failed, 0 skipped** (`python -m unittest discover -s
phase-2-implementation/backend/tests -p 'test_*.py' -q`). Five fresh isolated
business databases (original reference, primary, M2.0, E2E and Credit
development) and three separate fresh checkpoint
databases used the exact Phase 1C pin
`90c0bc8e285ee69262c7db826b786096a77ad004`, pinned schema/reference
fixture and compiled rules. The Credit suite now provisions its own nine M18
baseline and three M21CD rows; CI's workflow provisions that separate database
so these tests no longer rely on an environment-only skip. This is **local**
verification, not a claim that GitHub Actions passed; Actions results must be
checked separately after push.

## CR01 and CR03, source-first interpretation

Example CR01: a submitted synthetic deal has a 100.00 receivable, a 40.00
payment and 60.00 outstanding. The pinned reader selected the correct
original-subject profile/AR/payment; fixed Credit calculated exposure 9160.00.
The real model's inspection turn returned and the authorized tool completed;
the terminal HTTP exchange returned, but the strict final parser rejected it
as `terminal_semantics_or_evidence`. No finding was validated. This category
can represent more than one issue (e.g., an aliased AR field/value mismatch
or an unreturned reference); the raw response is intentionally not retained.
CR03's first HTTP exchange returned an allowed function with parseable JSON
arguments, but the parser classified `action_arguments` and did **not** execute
the inspection. Offline reproductions show both a wrong aliased subject and
an extra argument produce that category; it does not identify which occurred
in CR03. The receipts do not establish a tool failure, Groq HTTP 400, a
specific schema incompatibility or a prompt root cause. Neither assessment
may be replayed to improve the outcome. No validation rule or prompt was
weakened; offline tests reproduce the distinct failure shapes and preserve
exact original-only claims, abstention and no-replay protections.

CR02 alone completed with dated profile citations including stale
`fixed_commitments_fresh=false`; its fixed Credit status remains `unknown`.
It is **not** a real-model abstention or proof that all receivables are absent.
Credit v2 still lacks a validated hosted reconciled-transaction result and a
validated hosted profile-plus-AR result. Fulfillment HTTP 400 remains
unexplained; no unnecessary hosted calls were made for this retirement task.
M2.1 reliability requires fresh, diagnostically justified trials with safe
rejection categories or another separately authorized observation mechanism,
continued original/candidate and human-approval isolation, and eventual
independently accepted Phase 1C answers for formal quality evaluation.
