"""Read-only, two-process Phase 1C contract comparison on a disposable database.

The normal Phase 2 adapter remains pinned. This diagnostic imports each
Phase 1C checkout in a separate subprocess to prevent Python module mixing.
It never invokes the Phase 1C writing development runtime.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID


PIN = "90c0bc8e285ee69262c7db826b786096a77ad004"
REFERENCE = tuple(f"00000000-0000-4000-8000-000000{x:02d}0001" for x in range(1, 15))
CASE_IDS = ("B01", "B05")


def _sha(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _decision_digest(decision):
    """Compare actual six-domain values, not only shape and aggregate gate."""
    return sha256(json.dumps(decision["specialists"], default=str,
                             sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _shape(value):
    if isinstance(value, dict):
        return {str(key): _shape(item) for key, item in sorted(value.items(),
                                                               key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        return [_shape(value[0])] if value else []
    return type(value).__name__


def _worker(checkout):
    import psycopg
    from phase1c_reader import read_run
    from phase1c_candidate import reader_input_digest, verify_run_correlation
    from phase1c_deal_decision import assemble_deal_decision
    from phase1c_partial_discovery import discover_partial_delivery

    root = Path(checkout).resolve()
    if not Path(read_run.__code__.co_filename).resolve().is_relative_to(root):
        raise RuntimeError("Reader imported outside selected Phase 1C checkout")
    rows = {}
    for label, run_id in [(f"R{x:02d}", UUID(ref)) for x, ref in enumerate(REFERENCE, 1)]:
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                bundle = read_run(conn, run_id, commercial_rule_mode="compiled")
                decision = assemble_deal_decision(bundle)
                row = {"reader_shape": _shape({key: bundle[key] for key in
                         ("run", "deal", "lines", "facts", "rules", "supplier_offers")}),
                       "source_digest": reader_input_digest(bundle),
                       "business_status": decision["status"],
                       "specialist_digest": _decision_digest(decision),
                       "specialist_shape": _shape(decision["specialists"]),
                       "availability": [x["status"] for x in decision["specialists"]["availability"]],
                       "approval": decision["specialists"]["approval_routing"],
                       "offer_estimates": bundle["facts"]["lines"][0].get("supplier_offer_estimates", [])}
                rows[label] = row
    for label in CASE_IDS:
        run_id = UUID(f"00000000-0000-4000-8000-{18000 + int(label[-2:]):012d}")
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                original = read_run(conn, run_id, commercial_rule_mode="compiled")
                candidate, reason = discover_partial_delivery(original)
                if candidate is None:
                    raise AssertionError(f"{label}: existing binding candidate disappeared: {reason}")
                checked = read_run(conn, run_id, commercial_rule_mode="compiled", candidate=candidate)
                verify_run_correlation(candidate, original, checked)
                decision = assemble_deal_decision(checked)
                trace = checked["candidate_trace"]
                original_decision = assemble_deal_decision(original)
                rows[label] = {"source_digest": reader_input_digest(original),
                               "original_status": original_decision["status"],
                               "original_specialist_digest": _decision_digest(original_decision),
                               "candidate_supply_status": trace["assessment"]["status"],
                               "candidate_business_status": decision["status"],
                               "candidate_specialist_digest": _decision_digest(decision),
                               "candidate_source_digest": trace["source_input_digest"],
                               "candidate_input_digest": trace["candidate_input_digest"],
                               "candidate_slices": [(str(s.quantity), s.arrival_date.isoformat(),
                                                      list(s.evidence_ids)) for s in candidate.delivery_slices]}
                if (trace["source_input_digest"] != rows[label]["source_digest"] or
                        trace["assessment"]["status"] != "supply_supported_unreserved" or
                        decision["status"] != "needs_revision"):
                    raise AssertionError(f"{label}: binding or human-acceptance boundary changed")
    # An offer may be indicative, never a binding receipt or candidate source.
    if rows["R03"]["availability"] != ["conditional"] or any(
            x.get("binding") for x in rows["R03"]["offer_estimates"]):
        raise AssertionError("Conditional supplier offer incorrectly treated as confirmed")
    return rows


def _capture(checkout):
    checkout = Path(checkout).resolve(strict=True)
    implementation = checkout / "phase-1c-data" / "implementation"
    env = {**os.environ, "PYTHONPATH": str(implementation)}
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker",
                             str(checkout)], env=env, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def compare(pinned, development):
    pinned, development = Path(pinned), Path(development)
    if subprocess.check_output(["git", "-C", str(pinned), "rev-parse", "HEAD"], text=True).strip() != PIN:
        raise ValueError("Pinned checkout differs from approved Phase 1C SHA")
    development_sha = subprocess.check_output(["git", "-C", str(development), "rev-parse", "HEAD"], text=True).strip()
    files = ("schema.sql", "phase1c_reader.py", "phase1c_candidate.py",
             "phase1c_deal_decision.py", "phase1c_policy_decision.py",
             "phase1c_partial_discovery.py", "phase1c_row_fixtures.sql")
    hashes = {name: {label: _sha(checkout / "phase-1c-data" / "implementation" / name)
                     for label, checkout in (("pinned", pinned), ("development", development))}
              for name in files}
    old, new = _capture(pinned), _capture(development)
    diffs = {}
    for case in old:
        diffs[case] = {key: {"pinned": old[case][key], "development": new[case][key]}
                       for key in old[case] if old[case][key] != new[case][key]}
    return {"version": "m1.9-contract-comparison-v1", "pinned_sha": PIN,
            "development_sha": development_sha, "file_sha256": hashes,
            "source_and_contract_differences": diffs,
            "observed_cases": list(old), "results": {"pinned": old, "development": new},
            "scope": "14 reference runs and two disposable binding cases; read-only comparison, no pin upgrade"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pinned", type=Path)
    parser.add_argument("--development", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(_worker(args.worker), default=str, sort_keys=True))
    else:
        if not all((args.pinned, args.development, args.output)):
            parser.error("Pinned/development checkouts and an output path are required")
        result = compare(args.pinned, args.development)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"pinned_sha": result["pinned_sha"],
                          "development_sha": result["development_sha"],
                          "cases": len(result["observed_cases"]),
                          "different_cases": [k for k, v in result["source_and_contract_differences"].items() if v],
                          "changed_files": [k for k, v in result["file_sha256"].items()
                                            if v["pinned"] != v["development"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
