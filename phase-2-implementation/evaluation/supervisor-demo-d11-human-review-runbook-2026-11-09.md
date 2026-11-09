# D11 — private human first pass and restricted post-freeze comparison

**Working workflow, not a reviewed answer set.** D9's [blinded source-only index](supervisor-demo-d9-source-index-2026-11-09.md), [unchanged blank pilot](supervisor-demo-d9-pilot-blank.json) and [handbook](supervisor-demo-d9-review-handbook-2026-11-09.md) govern case inspection. The D10 [restricted handoff](supervisor-demo-d10-private-handoff-2026-11-09.md) and [non-answer integrity manifest](supervisor-demo-d10-private-manifest-2026-11-09.json) govern the *separate* AI proposals. Do **not** hand the D10 handoff, this runbook's post-freeze section, prior case-choice records, model drafts, or AI proposals to the blind reviewer before their own first pass. This script does not accept any answers and cannot establish independence, authority or semantic correctness.

## D10 preservation remains an owner action

**D11 historical state:** the original dossier at `/tmp/opencode/d10_private_pilot_2026-11-09/dossier.md` was mode `0600` under a `0700` owner-only directory. **D12 update:** an owner-authorized, hash-verified on-VM copy now exists at `/home/ubuntu/dealdesk-private/evaluation/d10/dossier.md`, outside Git; this is not disaster recovery against boot-volume loss. Recheck its hash against the D10 committed manifest before any separately authorized post-freeze comparison. The commands below document the earlier owner backup procedure, not a claim of an additional off-VM copy. Never send the dossier to an external service without explicit authorization.

```sh
export OWNER_PRIVATE_DIR=/owner-approved-durable-volume/dealdesk-restricted
test -d "$(dirname "$OWNER_PRIVATE_DIR")" || exit 1
install -d -m 700 "$OWNER_PRIVATE_DIR"
{ test ! -e "$OWNER_PRIVATE_DIR/d10-pilot.md" && test ! -L "$OWNER_PRIVATE_DIR/d10-pilot.md"; } || { echo 'Backup target already exists; do not overwrite'; exit 1; }
install -m 600 /tmp/opencode/d10_private_pilot_2026-11-09/dossier.md "$OWNER_PRIVATE_DIR/d10-pilot.md"
python3 - "$OWNER_PRIVATE_DIR/d10-pilot.md" <<'PY'
import hashlib, json, pathlib, sys
manifest = json.loads(pathlib.Path('phase-2-implementation/evaluation/supervisor-demo-d10-private-manifest-2026-11-09.json').read_text())
copied = pathlib.Path(sys.argv[1]); source = pathlib.Path('/tmp/opencode/d10_private_pilot_2026-11-09/dossier.md')
expected = manifest['private_dossier_sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, 'source changed'
assert hashlib.sha256(copied.read_bytes()).hexdigest() == expected, 'backup changed'
assert copied.stat().st_mode & 0o077 == 0, 'backup permissions too open'
assert copied.parent.stat().st_mode & 0o077 == 0, 'directory permissions too open'
print('Verified owner-only copy against Git manifest:', expected)
PY
```

Owner must confirm volume durability, physical/encrypted-at-rest protection and authorized reviewer access by the storage provider; Unix file permissions alone are **not** encryption. Keep the original, test recovery from the backup, and do not publish backup paths/keys. This example does **not** write to cloud, issue tracker, Git or a model prompt.

## 1. Prepare, inspect and hand off source-only private workspace

The operator must authenticate the selected human reviewer **out of band**, verify their lack of prior answer access (or explicitly record exposure), and place the source-only workspace on a reviewer-controlled, restricted system. `/tmp/opencode` is merely local staging on this VM, **not** a guarantee that a human reviewer has independent access or that the files will survive a reboot. The six-case copy created by D11 is staged at `/tmp/opencode/d11_human_staging/first_pass_workspace` with `0700` directories/`0600` files, and the owner must deliver it safely. It contains only the six matching packet/provider exports, one separately hash-verified v3 Credit row per case, and `first_pass.json` with blank fields. Never place a filled form back into Git or into model inputs.

For a fresh owner-controlled staging directory, from this repo root:

```sh
install -d -m 700 /tmp/opencode/my-private-human-staging
python3 phase-2-implementation/evaluation/d11_human_review.py prepare \
  --review-root /home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c \
  --packet-directory /tmp/opencode/phase1c_original_packets \
  --destination /tmp/opencode/my-private-human-staging/first-pass
python3 phase-2-implementation/evaluation/d11_human_review.py check \
  --review-root /home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c \
  --workspace /tmp/opencode/my-private-human-staging/first-pass \
  --form /tmp/opencode/my-private-human-staging/first-pass/first_pass.json
```

`prepare` refuses a preexisting destination (no overwrite), a public parent or a development-tree destination. It verifies actual packet payload/self-hash, provider bytes, v3 scope row and D9 blank-form SHA before copying, then rechecks copied sources. `check` returns 0 completed, 6 remaining for the blank form. The workspace must be copied/re-verified **on the reviewer's own controlled system** before use; staged material on this VM is not independent review.

**Human reviewer fields:** edit a private copy of `first_pass.json`, setting each `review_state` to `draft_complete` only after the actual author decision. Record a real identity/role, source-first attestation, explicit booleans for prior AI-answer exposure and AI assistance, details/limitations (write `none declared` if truly none). For `schema_version: 2`, use either a real timezone-aware `reviewed_at` with null `review_date`/`review_timezone`, **or**, where no clock time was recorded, `reviewed_at: null` with exact `YYYY-MM-DD` `review_date` and IANA `review_timezone`; never infer a time from the date or record-entry timestamp. Legacy version-1 forms still require timezone-aware `reviewed_at`. [D13 provenance limits](supervisor-demo-d13-date-only-review-provenance-2026-11-09.md) explain why the authoritative Phase 1C v2 intake cannot silently consume date-only D11 records. If the reviewer saw prior answers, report that; do not claim blind independence. Every case requires six codes from the existing Phase 1C set, each with nonempty calculations, rationale, uncertainty, exact `{ "document": "packet"|"provider"|"scope", "pointer": "/..." }` citations and applicable **case-local** rule IDs; Configuration/Availability may have an empty rule list when no case-local rule ID applies, not an invented ID. `scope` citations point to the copied *full* v3 row, with explicit `credit_scope.use` as `conditional`, `not_adopted`, or `unresolved` (the latter two do not establish complete AR). Selecting a scope in this workspace is an analytical assumption, **not** adoption by Phase 1C intake. `overall.status` may be `proposed` with one of the existing five exception gates or `deferred` with `gate: null`; do not invent a clean-case `approved` gate. Both require rationale, arithmetic, uncertainty, sources, rule IDs, human actions and a methodology question. Case 020 requires at least **two** distinct assumption-bound, source-cited `conditional_interpretations`—do not silently pick one as an adopted policy. Keep the form pending if evidence cannot support required fields rather than forging completeness.

## 2. Freeze only a real first pass

On the reviewer's controlled system and only **after** all six first-pass decisions are complete, use a new private output path (never reuse a frozen directory). The tool does not authenticate `--reviewer-name`: the owner must independently check identity and assistance disclosure. It rejects incomplete forms, missing/duplicated cases, stale source hashes, invalid JSON pointers or rule IDs, a missing Credit scope citation, an unresolved/undisclosed case-020 alternative, and any accepted-answer status. It copies the **exact input bytes** to `first_pass.json` and creates a SHA-256/timestamp/identity-*claim* receipt. The receipt is not a signature, independent-review certificate or accepted intake. The source form and immutable copy must be preserved out of band; the validator will detect content changed without updating the receipt, but a person with write access to both files could forge a replacement. For stronger tamper resistance, the owner should independently timestamp/sign the receipt in their approved record system.

```sh
python3 phase-2-implementation/evaluation/d11_human_review.py freeze \
  --review-root /home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c \
  --workspace /private/first-pass --form /private/first-pass/first_pass.json \
  --freeze-dir /private/frozen-first-pass --reviewer-name 'ACTUAL REVIEWER NAME'
python3 phase-2-implementation/evaluation/d11_human_review.py verify-freeze \
  --review-root /home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c \
  --workspace /private/first-pass --freeze-dir /private/frozen-first-pass
```

## 3. Owner-authorized *after-freeze* comparison and proposed adjudication

The owner must **first verify a genuinely human-completed freeze** and confirm permission to share the D10 restricted dossier with that specific reviewer. The tool checks the frozen content/digest and reviewer claim **before reading any D10 bytes**, validates the committed D10 digest and all sources again, then copies D10 only into a **new separate** private comparison directory; it never puts AI text into the blind workspace. The owner release switch is an explicit acknowledgement, **not** cryptographic authorization. Do not run this step for synthetic test fixtures or prior-exposed reviewers without recording the methodological limitation. Use the verified on-VM private copy; if it disappears, STOP and recover only from an authorized hash-matched source.

```sh
python3 phase-2-implementation/evaluation/d11_human_review.py unlock \
  --review-root /home/ubuntu/coding-agent/projects/DealDeskOrchestrator-phase1c \
  --workspace /private/first-pass --freeze-dir /private/frozen-first-pass \
  --packet-directory /tmp/opencode/phase1c_original_packets \
  --dossier /home/ubuntu/dealdesk-private/evaluation/d10/dossier.md \
  --manifest phase-2-implementation/evaluation/supervisor-demo-d10-private-manifest-2026-11-09.json \
  --destination /private/restricted-comparison --reviewer-name 'ACTUAL REVIEWER NAME' \
  --owner-release-after-human-freeze
```

In `/private/restricted-comparison/comparison_blank.json`, the accountable reviewer records, per case, text entries for `agreements`, `disagreements`, `corrections`, `open_questions` and optionally `proposed_adjudication: {"rationale": "...", "open_authority_question": "..."}`. Keep the original frozen bytes. Check the edited comparison using `check-comparison --review-root ... --workspace ... --freeze-dir ... --manifest ... --comparison /private/restricted-comparison/comparison_blank.json`. The form permits **only** comparison-blank or comparison-proposed statuses and `acceptances_created: 0`; it cannot change the authoritative Phase 1C acceptance register or certify reference correctness. Submit disagreements and recommended policy to the actual authorized Phase 1C/supervisor process, not this file.

## Decisions the owner/supervisor must record outside this workflow

| Gate | Explicit choices; no option silently adopted here |
| --- | --- |
| 020 route | Require committed modal path; require full max-lead coverage; or defer route choice until sourcing/production evidence improves. Preserve first-pass alternatives before seeing any prior interpretation. |
| Credit v3 | Adopt the exact per-case fictional complete-zero declaration with a **new scope-bound intake**; treat completeness as unknown; or commission newly versioned evidence. No old v2 form can bind v3 automatically. |
| Independence | Obtain genuinely independent human and disclosure; or use explicitly author-led/AI-assisted labels with thesis limitation. Source-first is a procedure, not a certificate of independence. |
| Ambiguity | Evidence-needed with verifiable gaps where possible, or defer and seek versioned abstention policy; do not force one of five exception gates for an unsupported/clean case. |
| Acceptance authority | Specify case-level reviewer/approver, signed evidence scope, disagreements and authoritative Phase 1C transition before any accepted answer or scoring. D8 reports **0/36 accepted** until genuine authorized intake occurs. |

**No hosted/paid AI integration, answer-key export, human judgment or supervisor approval was performed in D11.**
