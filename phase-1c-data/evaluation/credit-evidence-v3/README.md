# Provisional Credit evidence input version 3

This is a **versioned source overlay**, not a released answer key or a replacement
for the pinned 36 v2 PostgreSQL packets. The unchanged v2 source definition and
packet index are bound by exact SHA-256 values in `index.json`. A v3 original
input consists of that exact v2 packet/provider pair **plus** its matching
`credit_scope_v3.json` row. A consumer must verify both identities and expose
the credit scope as a trusted source fact before interpreting an empty list.
The existing Phase 2 pin and reader do not consume this overlay.

## Case-by-case source review

`../credit_intent_review_v3.json` records all 36 case IDs, source archetypes,
customer/cutoff, quote amount, credit limit, commitments, zero authored AR and
payment rows, and the explicit fictional complete-zero authoring choice.
`../build_credit_v3.py` refuses missing or inconsistent individual records,
wrong original source/index hashes, a changed archetype or credit-limit pair,
stale commitment observations, wrong customer/run identity, and any unexpected
AR/payment row. The review was performed by Codex using pinned source facts
and Ali's approved methodology; it is **not independent human adjudication**.
The declaration concerns only the complete fictional population for each
isolated synthetic customer at its run cutoff. It is not a real-world
zero-balance certification or evidence of favorable payment behavior.

The original v2 packets and model drafts remain intact, including their
unaccepted "complete snapshot" wording. The v3 overlay cannot silently
rewrite them. If a case's source or meaning changes, create another version,
recompute all affected hashes and redo source-first review.

## Separate provisional controls

`control_cases_v1.json` derives two distinct-customer cases from v2 001.
Case 040 has one EUR 1,000 invoice, EUR 300 paid before its due date, and
EUR 700 outstanding past due at the 1 September cutoff. Its scope is explicitly
complete within the fictional fixture. Case 041 has no selected AR/payment
rows and an **explicitly incomplete/unknown** scope. The two controls are
not included in the original 36, the 039 Configuration extension, or accepted
answers. Their IDs and row content are hashed separately in `index.json`.

The source-only `../credit_evidence_gate.py` checks the control document's
exact bytes against the index and each case's canonical hash, source/customer/
run identity, declared population and accounting/cutoff facts. It reports
`unknown_incomplete` for 041, a null overdue amount and
`credit_clearance_allowed=false`, even though its selected sets are empty.
It also withholds clearance from 040 until selected PostgreSQL rows and a
trusted exported packet have been verified. Agent-provided text cannot serve
as the trusted source declaration. Five focused mutation/identity tests pass.

The existing Phase 1C nonhistorical reader will still sum zero selected AR
for case 041. This source gate is **not integrated into the reader or Phase 2**;
041 remains a pending end-to-end missing-evidence control. A future explicit
consumer must bind the selected reader packet and this trusted scope before
turning source completeness into a specialist finding. An empty selected set
alone never establishes complete-zero exposure or credit clearance.
No six-responsibility expected findings for either control are accepted.

## Verification and remaining gate

Run `python build_credit_v3.py --check` and
`python -m unittest -v test_build_credit_v3 test_credit_evidence_gate` from `phase-1c-data/evaluation`.
The source-only local tests check pin drift, per-case review mutations,
case separation, and control source shape. They do not replace a fresh
PostgreSQL import/reader replay. Before release, import each control in an
isolated clean database, check typed rows and exact selected AR/payment
records, implement/verify the trusted completeness projection without
altering the Phase 2 pin, generate and hash v3 packets, and obtain accountable
source-first six-finding reviews for the chosen original and supplemental
cases. Keep reviewer-only answers away from agent-visible input.

Current accepted answers remain original **0/36**, Credit controls **0/2**,
and Configuration case 039 **0/1**. `ready_for_generation=false`;
PR #1 remains draft.
