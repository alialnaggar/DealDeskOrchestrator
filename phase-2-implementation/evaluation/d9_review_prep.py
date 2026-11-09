"""Build/verify source-only D9 references; never copy held-out data or fill a review.

Output is a reference index and a SUBSET of the authoritative blank v2 form,
not a new answer registry. Exported packets stay in the private review area.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path

import d8_readiness as d8

PILOT = (1, 5, 9, 20, 23, 31)
SCOPE_SHA256 = "7655c6f82dcbe8679f8d6369748c3a81e777b186e7c2b69ba9fe4b41076d711a"
THEMES = ("finished stock and dispatch", "allocated inventory", "inventory recency",
          "confirmed inbound and shipping", "supplier offers", "cancelled inbound and offers",
          "BOM and workshop", "component inbound and offers", "capacity recency",
          "competing inbound, offer and workshop", "digital term and provider proof",
          "digital proof availability", "digital proof term", "service region and slot",
          "service region and slot", "credit and commercial rules", "pricing floor and policy",
          "commercial policy and routing")
GATES = ("case_020_gate_and_route", "credit_v3_scope_and_intake",
         "reviewer_independence_and_assistance", "ambiguity_and_abstention",
         "denominators_and_exclusions")
FORBIDDEN_BLIND_MARKERS = ("model_review_v2_draft", "v2_author_amendments",
                           "v3_six_responsibility_technical_matrix", "case_020_business_choice",
                           "gate_for_review", "selected_interpretation", "second_model_review/")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sources(root, packets=None):
    check_index, _, _, _, digest = d8.load_contract(root)
    from phase1c_evaluation_review import build_review_workspace
    source = root / "phase-1c-data/evaluation"
    index = json.loads((source / "provisional_packet_index.json").read_text())
    check_index(index)
    if digest(index) != d8.PIN or len(index["cases"]) != 36:
        raise ValueError("Pinned v2 index differs")
    scope_file = source / "credit-evidence-v3/credit_scope_v3.json"
    scope_index = json.loads((source / "credit-evidence-v3/index.json").read_text())
    scope = json.loads(scope_file.read_text())
    if (scope_index.get("base_v2_index_sha256") != d8.PIN or
            scope.get("base_v2_index_sha256") != d8.PIN or
            scope_index.get("credit_scope_sha256") != SCOPE_SHA256 or
            sha(scope_file) != SCOPE_SHA256):
        raise ValueError("Credit v3 source pin differs")
    by_scope = {x["case_id"]: x for x in scope["cases"]}
    by_scope_pin = {x["case_id"]: x for x in scope_index["cases"]}
    ids = {x["case_id"] for x in index["cases"]}
    if len(by_scope) != 36 or len(by_scope_pin) != 36 or set(by_scope) != ids or set(by_scope_pin) != ids:
        raise ValueError("Credit scope membership differs")
    state = {}
    for row in index["cases"]:
        cid = row["case_id"]
        c = by_scope[cid]; pin = by_scope_pin[cid]
        if (pin["base_packet_sha256"] != row["packet_sha256"] or
                c["base_packet_sha256"] != row["packet_sha256"] or
                c["base_provider_file_sha256"] != row["provider_file_sha256"] or
                digest(c) != pin["scope_sha256"]):
            raise ValueError(f"{cid}: Credit scope/source pin differs")
        if packets is None:
            state[cid] = "not_checked: export path not supplied"
            continue
        packet_path = packets / f"{cid}.json"
        provider_path = packets / f"{cid}-provider.json"
        if not packet_path.is_file() or not provider_path.is_file():
            state[cid] = "missing: packet or provider export"
            continue
        try:
            payload = json.loads(packet_path.read_text())
            if (set(payload) != {"payload", "sha256"} or
                    payload["sha256"] != row["packet_sha256"] or
                    digest(payload["payload"]) != row["packet_sha256"] or
                    sha(provider_path) != row["provider_file_sha256"]):
                raise ValueError("hash mismatch")
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"{cid}: packet/provider source differs from pinned index") from exc
        state[cid] = "verified: packet payload + provider bytes + Credit v3 scope pin"
    return index, by_scope_pin, state, build_review_workspace(index)


def render_index(index, scopes, state, *, source_version, retrieval):
    lines = ["# D9 — source-only index for 36 provisional held-out cases",
             "", "**Not an answer key, reviewed packet or accepted-case list.** Each row names only a case, source theme and expected hashes. No source contents, authoring intents, model predictions, findings or evaluation outputs are copied here. Phase 1C's pinned index and v3 Credit scope remain authoritative.",
             "", f"**Source version:** `{source_version}`; canonical v2 index `{d8.PIN}`; Credit v3 is a separate source overlay, not part of the v2 packet. **Retrieval:** {retrieval} For each `CASE_ID` read the private export `CASE_ID.json` (self-hashed payload) and `CASE_ID-provider.json` (hashed raw bytes); the v3 scope row is in the separate Phase 1C `credit-evidence-v3/credit_scope_v3.json` and indexed in `credit-evidence-v3/index.json`. Verify hashes again in the reviewer's private environment; a D9 check does not freeze files outside Git.",
             "", "**Every case requires:** original submitted deal/lines and run cutoff, Configuration/product/BOM/compatibility, Pricing/cost and compiled rules, Availability/inventory/inbound/offers/capacity/digital/service/shipping, Credit profile/AR/payments **plus separately bound v3 completeness scope**, Policy rules, Approval routing rules, and separate provider records. A category can be empty or not applicable; inspect the actual selected packet rather than inferring its contents from this theme. Evidence flags: exports are not individually in Git; Credit v3 is a fictional complete-zero declaration, not real-world financial verification, and its intake binding/methodological adoption remain open for **all 36**. Do not read the model-assisted matrix or drafts in the blind pass.",
             "", "**Per-case reviewer checklist:** [ ] Verify v2 index/self/provider hashes and v3 Credit row hash/customer/run/cutoff; [ ] read source rows, separate provider file and business contract; [ ] independently calculate six findings and overall precedence/action; [ ] cite exact permitted JSON pointers including counterevidence; [ ] explain missing/unknown/abstention and assumptions; [ ] record identity, timezone-aware time, method and assistance; [ ] freeze first-pass draft before comparing others; [ ] record unresolved disagreements in the private form. **Disposition:** use only Phase 1C's existing `pending → draft_complete` source-first form, then its separate `reviewed_pending_disposition → accepted/rejected` intake; never set these from this index.",
             "", "| Case | Source theme (not an expected finding) | v2 packet payload SHA-256 | Provider-file bytes SHA-256 | Credit v3 row SHA-256 | Local export check |",
             "| --- | --- | --- | --- | --- | --- |"]
    for n, row in enumerate(index["cases"], start=1):
        cid = row["case_id"]
        if cid != f"EVAL-PREP-{n:03d}":
            raise ValueError("Unexpected v2 case sequence")
        lines.append(f"| `{cid}` | {THEMES[(n-1)//2]} | `{row['packet_sha256']}` | `{row['provider_file_sha256']}` | `{scopes[cid]['scope_sha256']}` | {state[cid]} |")
    lines.extend(["", "**Scope:** 039–041 are separate controls, not part of this index or pilot denominator. If exports are unavailable, affected rows are incomplete and review must wait for a reproducible hash-matched export.", ""])
    return "\n".join(lines)


def blank_pilot(index, workspace):
    cases = {row["case_id"]: row for row in workspace["cases"]}
    chosen = [f"EVAL-PREP-{n:03d}" for n in PILOT]
    if len(set(chosen)) != 6 or not set(chosen) <= set(cases):
        raise ValueError("Pilot membership differs from authoritative index")
    return {"schema_version": 1, "status": "blank_pilot_subset_not_answer_key",
            "input_index_sha256": d8.PIN, "cases": [copy.deepcopy(cases[cid]) for cid in chosen]}


def validate_pilot(pilot, index, workspace, packets, state, gates):
    """Structural subset checks only. No case can be promoted by this function."""
    serialized = json.dumps(pilot).lower()
    if any(marker in serialized for marker in FORBIDDEN_BLIND_MARKERS):
        raise ValueError("Draft/model-assisted decision marker exposed in blind pilot")
    expected = blank_pilot(index, workspace)
    if not isinstance(pilot, dict) or set(pilot) != set(expected) or any(pilot[k] != expected[k] for k in ("schema_version", "status", "input_index_sha256")):
        raise ValueError("Pilot header/acceptance claim invalid")
    by_id = {row["case_id"]: row for row in expected["cases"]}
    if (not isinstance(pilot["cases"], list) or len(pilot["cases"]) != 6 or
            [row.get("case_id") for row in pilot["cases"] if isinstance(row, dict)] != list(by_id)):
        raise ValueError("Pilot missing/duplicate/reordered cases")
    for row in pilot["cases"]:
        blank = by_id[row["case_id"]]
        if set(row) != set(blank) or any(row[k] != blank[k] for k in ("case_id", "packet_sha256", "provider_file_sha256")):
            raise ValueError("Pilot source pin/fields differ")
        if row["review_status"] not in ("pending", "draft_complete"):
            raise ValueError("Unsupported acceptance or reviewed claim in pilot")
        if state[row["case_id"]].startswith("verified:") is False and row["review_status"] != "pending":
            raise ValueError("Pilot decisions need verified packet and provider exports")
    if not isinstance(gates, dict) or set(gates) != set(GATES) or any(v != "decision_pending" for v in gates.values()):
        raise ValueError("Methodology gate changed/approved without an authoritative decision")
    # Apply only to a throwaway copy of the authoritative 36-case blank form.
    full = copy.deepcopy(workspace)
    lookup = {row["case_id"]: row for row in pilot["cases"]}
    full["cases"] = [lookup.get(row["case_id"], row) for row in full["cases"]]
    return full


def check_pilot(pilot, index, workspace, packets, state, gates, check_workspace):
    full = validate_pilot(pilot, index, workspace, packets, state, gates)
    results = check_workspace(full, index, packet_directory=packets)
    if results["errors"]:
        raise ValueError("Authoritative source-review check: " + "; ".join(results["errors"]))
    return {"pilot_cases": [row["case_id"] for row in pilot["cases"]],
            "complete_drafts_not_accepted": results["complete_draft_cases"],
            "missing_pilot_decisions": 6 - results["complete_draft_cases"],
            "unresolved_methodology_gates": list(GATES), "acceptances_created": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--packet-directory", type=Path)
    parser.add_argument("--pilot-file", type=Path, help="reviewer-only filled subset for read-only check; never commit it")
    parser.add_argument("--output-index", type=Path, help="write source-only Markdown index")
    parser.add_argument("--output-blank-pilot", type=Path, help="write blank subset form only")
    args = parser.parse_args()
    try:
        root = args.review_root.resolve(strict=True)
        index, scopes, state, workspace = load_sources(root, args.packet_directory)
        _, _, _, check_workspace, _ = d8.load_contract(root)
        gates = {key: "decision_pending" for key in GATES}
        # Decision gate status is a recommendation; no acceptance from check output.
        pilot = json.loads(args.pilot_file.read_text()) if args.pilot_file else blank_pilot(index, workspace)
        results = check_pilot(pilot, index, workspace, args.packet_directory, state, gates, check_workspace)
        results["verified_exports"] = sum(x.startswith("verified:") for x in state.values())
        results["missing_or_unchecked_exports"] = 36 - results["verified_exports"]
        if args.output_index:
            text = render_index(index, scopes, state, source_version="v2 packets + separate Credit v3 scope",
                                retrieval="the dated Phase 1C PostgreSQL verification export (see D9 handbook); no source file is embedded here.")
            if any(marker in text.lower() for marker in FORBIDDEN_BLIND_MARKERS):
                raise ValueError("Draft/model-assisted decision marker exposed in blind index")
            args.output_index.write_text(text)
        if args.output_blank_pilot:
            args.output_blank_pilot.write_text(json.dumps(blank_pilot(index, workspace), indent=2, sort_keys=True) + "\n")
        print(json.dumps(results, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"D9 source-first preparation refused: {exc}\n")


if __name__ == "__main__":
    main()
