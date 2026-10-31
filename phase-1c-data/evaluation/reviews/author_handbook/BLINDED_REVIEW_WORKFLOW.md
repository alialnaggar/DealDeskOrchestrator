# Phase 1C author source-first adjudication — versioned method proposal

Source basis: `alialnaggar/DealDeskOrchestrator`, `phase1c-candidate-contract`,
`c80460492def9b32771089997bfccff7c4732288` for the packet and technical
matrix inputs. The preparation scripts are later documentation commits.

## First pass — author decision before AI recommendation

1. Open **Blinded_Source_First_Handbook.pdf** and
   **Blinded_Initial_Decision_Register.xlsx** only. Do not open the 212-page
   technical reference, 216-recommendation matrix, original model drafts, or
   proposed answers yet. The source-first handbook does show approved business
   rules and their deterministic consequences, since those are necessary to
   decide a case. Its compilation and explanations used AI assistance; it is
   not independent of AI authorship in that sense.
2. Review an initial batch (suggested: 001–006), or start with difficult 020,
   029–030 if the business interpretation is clearer to you. For each case,
   write the six finding codes and narratives, source pointers, exact rule IDs and calculations,
   original-deal gate/actions, uncertainties, alternatives, rationale, name,
   timezone-aware decision time and assistance disclosure. Do not enter
   `Accepted` in the first-pass workbook; `Draft` or `Unresolved` describes the
   preliminary author record.
3. Freeze a completed batch before seeing technical recommendations:

   ```sh
   python3 freeze_initial_review.py \
     --workbook outputs/Blinded_Initial_Decision_Register.xlsx \
     --cases 001 002 003 004 005 006 \
     --output outputs/initial_001_006.json
   ```

   The script requires all six detailed findings and case-level fields for
   selected cases, checks pinned hashes and timezone-aware timestamps, writes
   an immutable JSON file and companion `.sha256`, and refuses overwrite.
   Save or commit this exact snapshot before comparison. Structural validation
   does not certify business correctness or accept any answer.

## Second pass — compare and finalize

4. Only after preserving the first-pass snapshot, run the bounded comparison:

   ```sh
   python3 compare_frozen_review.py \
     --snapshot outputs/initial_001_006.json \
     --output outputs/exceptions_001_006.json
   ```

   It checks the frozen snapshot hash and source pins, then flags code/gate
   disagreements, abstentions, missing pointer syntax and high-risk cases.
   Narrative claims and pointer support still need human source checking.
   The output never changes the initial snapshot or accepts a label.
5. Open the separate
   **Author_Adjudication_Handbook.pdf** and technical matrix. Compare each
   finding, gate, source pointer, calculation and action. Record agreements,
   disagreements, unsupported claims and missing evidence without rewriting
   the first-pass snapshot. A second-model review, if available, is additional
   quality assurance, not a substitute for Ali's decision.
6. Enter a distinct final author decision with identity, timestamp, rationale,
   corrections, evidence and assistance disclosure in a versioned final
   register/intake. Never convert an AI agreement into automatic acceptance.
   Maintain the original 36 separate from supplemental 039–041; adjudicate
   those through their own intake.

## Release criterion and academic limitation

Ali has directed that he is the sole accountable human dataset owner and will
conduct the source-first decisions. This proposed criterion replaces the
checklist's mandatory blinded second-model pass with (a) a source-first author
snapshot before technical recommendations, (b) deterministic and source-bound
comparison, (c) explicit final author acceptance, and (d) an optional second
model quality assurance pass. It is **author-conducted blinded source-first
adjudication**, not independent external expert validation. The blinding is
limited to the prior recommendations; the source booklet itself was compiled
with AI assistance, which must be disclosed.

The existing final release checklist still states a mandatory second-model
gate. Do not count answers accepted or release the evaluation set until this
replacement is explicitly adopted in the methodology/release record and any
applicable academic requirement is checked with the supervisor or academic
authority. If the thesis's formal evaluation requires independent expert
labels or a second-model pass, this method does not satisfy that requirement
without an authorized change. Runtime output evidence and final audit remain
separate gates. `ready_for_generation=false` and draft PR #1 remain unchanged.
