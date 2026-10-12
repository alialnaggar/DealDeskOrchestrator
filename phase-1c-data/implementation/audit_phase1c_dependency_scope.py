"""Audit the scope of a proposed catalogue-wide product dependency.

The checked-in SQL is deterministically rendered and separately checked in CI.
This audit reads submitted deal lines only; it does not infer expected decisions.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

from render_phase1c_dependency_pilot import SOURCE, TARGET

HERE = Path(__file__).resolve().parent
INPUTS = (
    *(f"phase1c_historical_inputs_{n:02d}.sql" for n in range(1, 9)),
    "phase1c_vertical_pilot.sql",
    "phase1c_conflict_pilot.sql",
    "phase1c_stress_pilot.sql",
)
LINE = re.compile(
    r"^INSERT INTO deal_lines \([^)]*\) VALUES "
    r"\('[^']+', '([^']+)', '[^']+', '([^']+)',"
)


def audit(base_dir=HERE):
    deals = defaultdict(set)
    line_count = 0
    for filename in INPUTS:
        for line in (base_dir / filename).read_text().splitlines():
            if not line.startswith("INSERT INTO deal_lines "):
                continue
            match = LINE.match(line)
            if not match:
                raise ValueError(f"cannot parse generated deal line in {filename}")
            deal_id, product_id = match.groups()
            deals[deal_id].add(product_id)
            line_count += 1
    historical = sorted(d for d in deals if d.startswith("HIST-DEAL-"))
    pilot = sorted(d for d in deals if not d.startswith("HIST-DEAL-"))
    if len(historical) != 400 or len(pilot) != 36:
        raise ValueError("expected 400 historical and 36 pilot deals")
    affected = sorted(d for d, products in deals.items()
                      if SOURCE in products and TARGET not in products)
    present = sorted(d for d, products in deals.items()
                     if SOURCE in products and TARGET in products)
    # A requires_product rule is safe for prior deals only when its target
    # occurs in every existing submission that contains the source.
    product_ids = set().union(*deals.values())
    safe_pairs = []
    for source in sorted(product_ids):
        source_deals = [products for products in deals.values() if source in products]
        common = set.intersection(*source_deals) - {source}
        safe_pairs.extend((source, target) for target in sorted(common))
    return {
        "existing_safe_requires_pairs": len(safe_pairs),
        "source_product_id": SOURCE,
        "target_product_id": TARGET,
        "historical_deals": len(historical),
        "pilot_deals": len(pilot),
        "line_rows": line_count,
        "source_without_target": {
            "historical": [d for d in affected if d.startswith("HIST-DEAL-")],
            "pilot": [d for d in affected if not d.startswith("HIST-DEAL-")],
        },
        "source_with_target": {
            "historical": [d for d in present if d.startswith("HIST-DEAL-")],
            "pilot": [d for d in present if not d.startswith("HIST-DEAL-")],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(report)
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
