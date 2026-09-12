"""Classify companions of the most common U124 best-table donors.

This is an inventory, not a theorem. It groups the second relator of each
row that contains a shared donor, up to rotation and inversion of that
companion, so a later theorem can target one shape at a time.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from experiments.equivalence_classes.lib.words import canon_rel, exp_sums  # noqa: E402
from u124_census import bs_mm1_shape, syllables  # noqa: E402

DATA = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

DONORS = (
    "YXXyxYx",
    "YXXXyxYx",
    "YXyXYxx",
    "YYXXyxx",
    "YXXXyxx",
    "YYXXXyxx",
    "YXXyXYxxx",
    "YXXYxxyx",
    "YXXXyxYxx",
    "YXXYxxyX",
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    families = []
    covered = set()
    for donor in DONORS:
        members = []
        for row in rows:
            if row["r1"] == donor:
                companion, side = row["r2"], "r1_is_donor"
            elif row["r2"] == donor:
                companion, side = row["r1"], "r2_is_donor"
            else:
                continue
            covered.add(row["name"])
            bs, m = bs_mm1_shape(companion)
            members.append(
                {
                    "id": row["name"],
                    "side": side,
                    "companion": companion,
                    "companion_canon": canon_rel(companion),
                    "companion_len": len(companion),
                    "companion_exp": list(exp_sums(companion)),
                    "companion_syllables": syllables(companion),
                    "companion_bs_mm1": bs,
                    "companion_bs_m": m,
                    "pair_len": len(row["r1"]) + len(row["r2"]),
                }
            )
        by_canon: dict[str, list[str]] = defaultdict(list)
        for member in members:
            by_canon[member["companion_canon"]].append(member["id"])
        families.append(
            {
                "donor": donor,
                "donor_len": len(donor),
                "donor_exp": list(exp_sums(donor)),
                "n_rows": len(members),
                "distinct_companion_canons": len(by_canon),
                "companion_canon_groups": [
                    {"canon": key, "ids": ids, "n": len(ids)}
                    for key, ids in sorted(
                        by_canon.items(), key=lambda kv: (-len(kv[1]), kv[0])
                    )
                ],
                "members": members,
            }
        )
    uncovered = [row["name"] for row in rows if row["name"] not in covered]
    summary = {
        "n_listed_donors": len(DONORS),
        "n_rows_covered": len(covered),
        "n_rows_uncovered": len(uncovered),
        "uncovered": uncovered,
        "families": families,
        "status": "inventory_not_a_solve",
    }
    path = OUT / "shared_donor_families.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "n_rows_covered": len(covered),
                "n_rows_uncovered": len(uncovered),
                "families": [
                    {
                        "donor": f["donor"],
                        "n_rows": f["n_rows"],
                        "distinct_companion_canons": f["distinct_companion_canons"],
                    }
                    for f in families
                ],
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
