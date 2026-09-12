"""Depth-1 ordinary AC2 feature scan on the U124 best table.

Enumerates cyclic AC2 children of each pair (invert the donor, all rotations)
and records two-block, one-occurrence, and strict cyclic-length drops.

This is a complete depth-1 neighbourhood, not a heap search. It does not
apply automorphisms. A miss is not an obstruction.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    cyc_reduce,
    inv,
    rot,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
from u124_census import (  # noqa: E402
    bs_mm1_shape,
    one_occurrence_cyclic,
    two_block_shape,
)

DATA = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
OUT = ROOT / "research" / "u124_stable_20260912" / "tables"


def children(r1: str, r2: str) -> list[tuple[str, str, dict[str, int]]]:
    out: list[tuple[str, str, dict[str, int]]] = []
    for target in (1, 2):
        ri, rj = (r1, r2) if target == 1 else (r2, r1)
        if not ri or not rj:
            continue
        for jsign, oj in ((1, rj), (-1, inv(rj))):
            for k1 in range(len(ri)):
                for k2 in range(len(oj)):
                    piece = cyc_reduce(rot(ri, k1) + rot(oj, k2))
                    if not piece:
                        continue
                    if target == 1:
                        pair = (piece, r2)
                    else:
                        pair = (r1, piece)
                    move = {
                        "target": target,
                        "jsign": jsign,
                        "k1": k1,
                        "k2": k2,
                        "new_len": len(pair[0]) + len(pair[1]),
                    }
                    out.append((pair[0], pair[1], move))
    return out


def flags(r1: str, r2: str) -> dict[str, bool | int | None]:
    bs1, m1 = bs_mm1_shape(r1)
    bs2, m2 = bs_mm1_shape(r2)
    return {
        "one_occurrence": one_occurrence_cyclic(r1) or one_occurrence_cyclic(r2),
        "two_block_both": two_block_shape(r1) and two_block_shape(r2),
        "two_block_either": two_block_shape(r1) or two_block_shape(r2),
        "bs_mm1_either": bs1 or bs2,
        "bs_m": m1 or m2,
        "length": len(cyc_reduce(r1)) + len(cyc_reduce(r2)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    reports = []
    n_children = 0
    n_len_drop = 0
    n_one = 0
    n_two_both = 0
    hits = []
    for row in rows:
        r1, r2 = row["r1"], row["r2"]
        base = flags(r1, r2)
        best_len = base["length"]
        row_hits = []
        kids = children(r1, r2)
        n_children += len(kids)
        seen = set()
        for a, b, move in kids:
            key = (a, b)
            if key in seen:
                continue
            seen.add(key)
            feat = flags(a, b)
            dropped = feat["length"] < base["length"]
            interesting = (
                dropped
                or (feat["one_occurrence"] and not base["one_occurrence"])
                or (feat["two_block_both"] and not base["two_block_both"])
            )
            if not interesting:
                continue
            rec = {
                "new_r1": a,
                "new_r2": b,
                "move": move,
                **feat,
                "length_drop": dropped,
            }
            row_hits.append(rec)
            if dropped:
                n_len_drop += 1
                if feat["length"] < best_len:
                    best_len = feat["length"]
            if feat["one_occurrence"] and not base["one_occurrence"]:
                n_one += 1
            if feat["two_block_both"] and not base["two_block_both"]:
                n_two_both += 1
        reports.append(
            {
                "id": row["name"],
                "input_length": base["length"],
                "n_children": len(kids),
                "n_interesting": len(row_hits),
                "best_child_length": best_len,
                "strict_drop": best_len < base["length"],
                "hits": row_hits[:20],
            }
        )
        if row_hits:
            hits.append(row["name"])

    elapsed = time.perf_counter() - started
    summary = {
        "n_rows": len(rows),
        "n_children_enumerated": n_children,
        "rows_with_interesting_child": len(hits),
        "interesting_ids": hits,
        "n_strict_length_drop_children": n_len_drop,
        "n_new_one_occurrence_children": n_one,
        "n_new_two_block_both_children": n_two_both,
        "rows_with_strict_drop": sum(1 for r in reports if r["strict_drop"]),
        "elapsed_seconds": round(elapsed, 3),
        "status": "depth1_neighbourhood_not_a_solve",
        "rows": reports,
    }
    path = OUT / "elementary_ac2_scan.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: summary[k] for k in (
                "n_rows",
                "n_children_enumerated",
                "rows_with_interesting_child",
                "n_strict_length_drop_children",
                "n_new_one_occurrence_children",
                "n_new_two_block_both_children",
                "rows_with_strict_drop",
                "elapsed_seconds",
                "status",
            )},
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
