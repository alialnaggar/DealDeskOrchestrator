"""Read-only structural/provenance check of a PRIVATE proposed-answer dossier.

Never copy the dossier into this repo or print its contents. Citation resolution
does not prove that a cited source entails the author's business conclusion.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

import d9_review_prep as d9

SPECIALISTS = ("Configuration", "Pricing", "Availability", "Credit", "Policy", "Approval")
SECTION = re.compile(r"^### (EVAL-PREP-\d{3})\b", re.M)
POINTER = re.compile(r"\b(packet|provider|scope):(/[^\s`,;)*]+)")
RULE = re.compile(r"\b(?:AP|PO|PR)-BASE-[A-Z0-9-]+\b")


def follow(value, pointer):
    """RFC 6901 pointer; must resolve, including selected empty collections."""
    if not pointer.startswith("/"):
        raise ValueError("Citation requires absolute JSON pointer")
    for token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", token):
            raise ValueError("Invalid JSON pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict):
            value = value[token]
        elif isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", token):
                raise ValueError("Invalid array index")
            value = value[int(token)]
        else:
            raise ValueError("Pointer traverses scalar")
    return value


def validate(dossier, manifest, source_root, packets):
    from d8_readiness import PIN

    if (manifest.get("status") != "private_ai_draft_not_accepted" or
            manifest.get("accepted_cases") != 0 or manifest.get("v2_index_sha256") != PIN or
            manifest.get("case_ids") != [f"EVAL-PREP-{n:03d}" for n in d9.PILOT]):
        raise ValueError("Safe manifest status/case pins differ")
    index, scope_pins, state, _ = d9.load_sources(source_root, packets)
    if any(not state[cid].startswith("verified:") for cid in manifest["case_ids"]):
        raise ValueError("Missing/unverified pilot packet or provider")
    scope_rows = {r["case_id"]: r for r in json.loads(
        (source_root / "phase-1c-data/evaluation/credit-evidence-v3/credit_scope_v3.json").read_text())["cases"]}
    rows = {r["case_id"]: r for r in index["cases"]}
    for cid in manifest["case_ids"]:
        pin = manifest["sources"].get(cid)
        if (pin is None or pin != {"packet_payload_sha256": rows[cid]["packet_sha256"],
                                   "provider_file_sha256": rows[cid]["provider_file_sha256"],
                                   "credit_scope_row_sha256": scope_pins[cid]["scope_sha256"]}):
            raise ValueError(f"{cid}: source pin differs")
    if set(manifest["sources"]) != set(manifest["case_ids"]):
        raise ValueError("Unexpected source IDs")
    if hashlib.sha256(dossier.read_bytes()).hexdigest() != manifest["private_dossier_sha256"]:
        raise ValueError("Private dossier digest differs from manifest")
    text = dossier.read_text()
    if ("AI-generated" not in text or "NOT a blind human review" not in text or
            "0/36 accepted" not in text):
        raise ValueError("Assistance/status disclaimer missing")
    matches = list(SECTION.finditer(text))
    if [m.group(1) for m in matches] != manifest["case_ids"]:
        raise ValueError("Dossier missing/duplicating/reordering pilot cases")
    counts = {"cases": len(matches), "citation_pointers_resolved": 0, "rule_identifiers_resolved": 0,
              "source_export_pairs_verified": len(matches), "acceptances_created": 0}
    for i, match in enumerate(matches):
        cid = match.group(1)
        part = text[match.end():matches[i + 1].start() if i + 1 < len(matches) else text.index("## Required accountable review", match.end())]
        packet = json.loads((packets / f"{cid}.json").read_text())["payload"]
        provider = json.loads((packets / f"{cid}-provider.json").read_text())
        sources = {"packet": packet, "provider": provider, "scope": scope_rows[cid]}
        for name in SPECIALISTS:
            if len(re.findall(r"^\* \*\*" + name + r" — ", part, re.M)) != 1:
                raise ValueError(f"{cid}: missing/duplicate {name} finding")
        if "**Overall:**" not in part:
            raise ValueError(f"{cid}: missing overall rationale")
        refs = POINTER.findall(part)
        if len(refs) < len(SPECIALISTS):
            raise ValueError(f"{cid}: insufficient source citations")
        for document, pointer in refs:
            try:
                follow(sources[document], pointer.rstrip("."))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise ValueError(f"{cid}: unresolved {document} citation {pointer}") from exc
            counts["citation_pointers_resolved"] += 1
        rules = {r.get("pricing_rule_id", r.get("policy_rule_id", r.get("approval_rule_id")))
                 for group in packet["source_rows"]["rules"].values() for r in group}
        used = RULE.findall(part)
        if not used:
            raise ValueError(f"{cid}: missing business rule IDs")
        for rule in used:
            if rule not in rules:
                raise ValueError(f"{cid}: unknown rule ID {rule}")
            counts["rule_identifiers_resolved"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--review-root", required=True, type=Path)
    parser.add_argument("--packet-directory", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.dossier, json.loads(args.manifest.read_text()),
                                  args.review_root, args.packet_directory), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"D10 private draft check refused: {exc}\n")


if __name__ == "__main__":
    main()
