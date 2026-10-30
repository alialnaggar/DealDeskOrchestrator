# Fresh Phase 1C PostgreSQL verification — 30 October 2026

Technical verification only. Source branch `phase1c-candidate-contract`, starting
at `cef6c4fc61e390c98a490cf6b7df206f44bcd128` (remote independently
queried before work). Phase 2 at `fe250fd132a149bef7ccebad0148147cf60f6c29`
has uncommitted Gemma files; the Phase 1C work used a separate worktree and
did not switch, edit, merge or re-pin Phase 2. PR #1 remains draft.

## Isolation and reproducible commands

Local image `postgres:16`, started as a dedicated ephemeral container with a
tmpfs data directory, bound to `127.0.0.1:55431`. Client `psql` 16 and a
temporary Python virtualenv with `psycopg[binary]` 3.3.6 and PyYAML 6.0.3.
Four newly created databases, all with zero deals before the test, were used:
`phase1c_original_20261030`, `phase1c_config_20261030`,
`phase1c_credit_20261030`, `phase1c_reader_20261030`. No existing databases,
assessment IDs or checkpoint records were reused. The 36, configuration and
control test cases each run in individually rolled-back transactions; compiled
masters remain local to their disposable database. Sensitive local connection
credentials are intentionally omitted here. Exported packets/logs live only
under `/tmp/opencode/phase1c_*` on the verification VM, not in Git.

From `phase-1c-data/implementation`, with the temporary venv's Python and
`PGHOST=127.0.0.1 PGPORT=55431 PGUSER=postgres` and a local `PGPASSWORD`:

```sh
python compile_phase1c_policy.py --output /tmp/opencode/phase1c_compiled_rules.sql
createdb phase1c_original_20261030
psql -X -v ON_ERROR_STOP=1 -d phase1c_original_20261030 -f schema.sql -f /tmp/opencode/phase1c_compiled_rules.sql
EVALUATION_DATABASE_URL=postgresql://postgres@127.0.0.1:55431/phase1c_original_20261030 PHASE1C_EVALUATION_PACKETS=/tmp/opencode/phase1c_original_packets PHASE1C_EVALUATION_PACKETS_V1=/tmp/opencode/phase1c_archive_packets python -m unittest -v test_phase1c_evaluation_cases
createdb phase1c_config_20261030
psql -X -v ON_ERROR_STOP=1 -d phase1c_config_20261030 -f schema.sql -f /tmp/opencode/phase1c_compiled_rules.sql
EVALUATION_DATABASE_URL=postgresql://postgres@127.0.0.1:55431/phase1c_config_20261030 PHASE1C_CONFIGURATION_PACKETS=/tmp/opencode/phase1c_configuration_packets python -m unittest -v test_phase1c_configuration_extension test_phase1c_configuration_review_scope
createdb phase1c_credit_20261030
psql -X -v ON_ERROR_STOP=1 -d phase1c_credit_20261030 -f schema.sql -f /tmp/opencode/phase1c_compiled_rules.sql
PYTHONPATH=../evaluation EVALUATION_DATABASE_URL=postgresql://postgres@127.0.0.1:55431/phase1c_credit_20261030 PHASE1C_CREDIT_PACKETS=/tmp/opencode/phase1c_credit_packets python -m unittest -v test_phase1c_credit_controls
createdb phase1c_reader_20261030
psql -X -v ON_ERROR_STOP=1 -d phase1c_reader_20261030 -f schema.sql
PGDATABASE=phase1c_reader_20261030 DATABASE_URL=postgresql://postgres@127.0.0.1:55431/phase1c_reader_20261030 python -m unittest -v test_phase1c_reader
```

The reference reader test loads its own SQL fixture into the *separate* reader
database. Run the source-only checks from `phase-1c-data/evaluation`:

```sh
python build_credit_v3.py --check
python build_v3_technical_matrix.py --packets /tmp/opencode/phase1c_original_packets --check
python -m unittest -v test_build_credit_v3 test_credit_evidence_gate
```

Configuration scope and saved draft validation from `implementation/`:

```sh
python phase1c_configuration_review_scope.py --packet-directory /tmp/opencode/phase1c_configuration_packets --candidate-index-output /tmp/opencode/phase1c_config_candidate.json --blank-review-output /tmp/opencode/phase1c_config_blank.json
python phase1c_evaluation_review.py --index /tmp/opencode/phase1c_config_candidate.json --review-file ../evaluation/configuration-extension/v1/reviews/model_assisted_039_draft.json --packet-directory /tmp/opencode/phase1c_configuration_packets
```

## Source results and boundaries

- **Original 36:** eight evaluation tests pass, including fresh import and
  two independent export passes of all 36 v2 cases, retained v1 archive
  replay, exact pinned packet/provider hashes and no reused development or
  historical operational IDs. `build_credit_v3.py --check` reproduces 36
  explicit fictional complete-zero scopes, per-case v2 packet/provider pins,
  customer/run/cutoff and intent-ledger hashes. The matrix regenerates exactly
  from the exported sources: 36 cases / 216 *model-assisted technical*
  recommendations, zero accepted answers. The generator reads packets and
  scope, not historical diagnostics or saved model drafts; its authored
  recommendation templates/gate proposals are *not* independent derivations
  or accepted outcomes. No v2 source or
  Phase 2 dataset pin changed.
- **039:** two-connection replay and exact `83f65e17...` packet and
  `6f217c34...` provider hashes match the separate configuration index.
  Reader selects only the active V2 whole-deal `requires_product` rule
  `EVALCFG-003-REQUIRES-ADDON`, with absent target 005-V2 and `fail` status.
  Removing the rule in a rolled-back mutation removes that fact and changes
  the packet hash; it does not invent a dependency failure. 037/038 remain
  preflight diagnostics, not candidates. The one 039 model-assisted draft
  validates structurally, still 0/1 accepted. V2 dependency release field
  scope is not closed by this test alone.
- **040:** typed import selects one overdue AR invoice EUR 1,000 originally,
  one EUR 300 payment and EUR 700 outstanding. Complete fictional source
  declaration, cutoff, source/index and pinned packet/provider hashes are
  bound. Output state `declared_complete_nonempty`; clearance false. A
  recomputed packet from mutated database AR EUR 650 fails the pin/selection.
- **041:** typed import selects empty AR/payment sets, but the trusted source
  declares `explicitly_incomplete_unknown`; packet projection returns null
  overdue, no clearance. Rehashed injected selected rows, swapped source
  identity, changed provider, altered pin and upgraded completeness all fail.
  Empty sets alone are not a complete-zero assertion. Both controls are
  provisional, 0/2 accepted.
- **Regressions:** 15 fresh PostgreSQL reference-reader tests pass; four
  configuration scope/replay tests pass; eleven Credit source/gate tests pass.
  Additional 35 source/reader/compatibility tests passed with 16 skipped
  because that secondary command intentionally omitted `DATABASE_URL` or
  packet directory; the reader tests were rerun and passed with their own
  fresh database. No observed failures in the final verification. Full
  historical/100-case runtime campaigns and genuine specialist runtime
  outputs were not rerun; older CI cannot verify this commit.

## Phase 2 adoption handoff (separate branch and decision)

The existing nonhistorical `read_run` selects AR and payments but carries **no
population completeness proof**. The new control-v1 evaluation projection
`classify_selected_packet` requires trusted source/index, pinned control
packet/provider and verified reader selections; it does not modify the v2
packet or current Phase 2 pin. Before Phase 2 adopts any v3 dataset, introduce
an explicit versioned trusted credit-scope input/API field, bind it to the
same customer/run/cutoff and exact source/packet/provider hashes, and project
it into the Credit specialist's evidence state. Missing/untrusted scope must
fail closed. For declared complete-zero, selected AR/payment rows must be
empty and the *trusted declaration* must match; do not infer payment history
or real-world verification. For complete/nonempty, reconcile invoice,
payments, dates and overdue amount and withhold clearance on overdue debt.
For incomplete/unknown, even if selected sets are empty, exposure/overdue
cannot be asserted as zero and Credit must request evidence. Test all three
states plus missing scope, wrong customer/run/cutoff, row mutation, provider
and hash mismatch, with 040/041 isolated PostgreSQL fixtures. Preserve the
older Phase 2 pin until that branch makes an explicit versioned adoption.

## Remaining release gates

No independent human case adjudication: original 0/36, supplemental 039
0/1, Credit controls 0/2. The 216 recommendations and 039 draft are not
accepted answers. Accountable six-responsibility source-first review, exact
Configuration field-scope disposition, genuine specialist runtime-output
evidence, calibration/field reviews and final release audit remain open.
`ready_for_generation=false`; PR #1 remains draft. The packet projection is
evaluation-only; a production reader/runtime completeness contract remains
an explicit downstream task, not an implied release.
