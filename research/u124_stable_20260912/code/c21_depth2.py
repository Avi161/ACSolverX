#!/usr/bin/env python3
"""C21: depth-2 ordinary AC2 from C20's ten no-pinch children.

C20 left, for each n=2..7, exactly ten canon_pair-unique depth-1 children
that keep D and lengthen B, with no valid BS(n,n+1) pinch. This script:

1. Serializes those ten B-words as a function of n (family probe).
2. Enumerates their unique depth-1 AC2 children (one extra multiply) and
   classifies length drops below the C19 base 2n+10, one-occurrence,
   two-block-both, and associated-subgroup pinches that do not rewrite
   to cyclic D/D^{-1}/B/B^{-1}/empty.

Not a heap search. A miss is not an obstruction to depth ≥ 3.
Incoming C16 remains two Lemma-11 uses. Not a U124 solve.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    cyc_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c16_escape_scan as esc  # noqa: E402
import c20_roundtrip as c20  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children, flags  # noqa: E402
from u124_census import bs_mm1_shape  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

D = c20.D
ALLOWED = {"cyclic_D", "cyclic_Dinv", "cyclic_B", "cyclic_Binv", "empty"}


def c19_base(n: int) -> tuple[str, str, int]:
    rec = esc.c19_identity(n)
    r1, r2 = rec["donor"], rec["product"]
    return r1, r2, rec["out_len"]


def no_pinch_children(n: int) -> list[dict]:
    depth = c20.depth1_pinch_roundtrips(n)
    kids = depth["no_pinch_children"]
    if len(kids) != 10:
        raise AssertionError(f"n={n}: expected 10 no-pinch children, got {len(kids)}")
    if not all(row["keeps_D"] for row in kids):
        raise AssertionError(f"n={n}: a no-pinch child moved D")
    return kids


def classify_pair(a: str, b: str, n: int, base_len: int) -> dict:
    feat = flags(a, b)
    new_len = feat["length"]
    pinch_hits = []
    other_after = []
    for word, slot in ((a, "r1"), (b, "r2")):
        for rec in c20.apply_all_valid_pinches(word, n):
            klass = rec.get("class", "pinch_failed")
            if klass == "empty" and slot == "r1":
                pinch_hits.append({"slot": slot, "class": "empty_on_D", "k": rec.get("k")})
            elif klass == "other":
                after = rec.get("after_cyc") or ""
                other_after.append(
                    {
                        "slot": slot,
                        "k": rec.get("k"),
                        "after_cyc": after,
                        "after_len": len(after),
                    }
                )
                pinch_hits.append(
                    {
                        "slot": slot,
                        "class": "other",
                        "k": rec.get("k"),
                        "after_len": len(after),
                    }
                )
            elif klass not in ALLOWED:
                pinch_hits.append({"slot": slot, "class": klass, "k": rec.get("k")})
    return {
        "new_r1": a,
        "new_r2": b,
        "new_len": new_len,
        "drop_vs_c19": base_len - new_len,
        "one_occurrence": feat["one_occurrence"],
        "two_block_both": feat["two_block_both"],
        "bs_mm1_either": feat["bs_mm1_either"],
        "bs_m": feat["bs_m"],
        "n_disallowed_pinches": len(pinch_hits),
        "n_other_after": len(other_after),
        "min_other_after_len": min((row["after_len"] for row in other_after), default=None),
        "other_after": other_after[:4],
        "pinch_hits": pinch_hits[:4],
    }


def interesting(rec: dict, parent_len: int, d_len: int = 7) -> bool:
    rec["drop_vs_parent"] = parent_len - rec["new_len"]
    shorter_other = (
        rec["min_other_after_len"] is not None and rec["min_other_after_len"] < d_len
    )
    return bool(
        rec["drop_vs_c19"] > 0
        or rec["drop_vs_parent"] > 0
        or rec["one_occurrence"]
        or rec["two_block_both"]
        or shorter_other
    )


def scan_n(n: int) -> dict:
    r1, r2, base_len = c19_base(n)
    kids = no_pinch_children(n)
    family = []
    hits = []
    n_grand = 0
    n_unique = 0
    n_other = 0
    n_return_c19 = 0
    n_return_db_edges = 0
    n_parent_drop = 0
    n_parent_drop_edges = 0
    min_other = None
    shortest_others = []
    seen_global = set()
    db_key = canon_pair(r1, r2)
    for kid in kids:
        parent = (kid["r1"], kid["r2"])
        parent_len = kid["len"]
        family.append(
            {
                "B": kid["r2"],
                "B_len": kid["r2_len"],
                "len": parent_len,
                "move": kid["move"],
                "B_cyc": cyc_reduce(kid["r2"]),
                "bs_mm1": bs_mm1_shape(kid["r2"])[0],
            }
        )
        seen = set()
        for a, b, move in children(*parent):
            n_grand += 1
            key = canon_pair(a, b)
            if key in seen:
                continue
            seen.add(key)
            rec = classify_pair(a, b, n, base_len)
            rec["drop_vs_parent"] = parent_len - rec["new_len"]
            if rec["drop_vs_parent"] > 0:
                n_parent_drop_edges += 1
            if key == db_key:
                n_return_db_edges += 1
            if key in seen_global:
                continue
            seen_global.add(key)
            n_unique += 1
            rec["move"] = move
            rec["parent_B"] = kid["r2"]
            rec["parent_len"] = parent_len
            if rec["n_other_after"]:
                n_other += 1
                mol = rec["min_other_after_len"]
                if mol is not None and (min_other is None or mol < min_other):
                    min_other = mol
                    shortest_others = rec["other_after"][:2]
            if rec["drop_vs_parent"] > 0:
                n_parent_drop += 1
            if rec["new_len"] == base_len and rec["drop_vs_parent"] > 0:
                n_return_c19 += 1
            if interesting(rec, parent_len):
                hits.append(rec)
    lens = Counter(row["B_len"] for row in family)
    return {
        "n": n,
        "c19_base_len": base_len,
        "n_no_pinch": len(kids),
        "B_len_histogram": dict(sorted(lens.items())),
        "family": family,
        "n_grandchildren_raw": n_grand,
        "n_grandchildren_unique": n_unique,
        "n_interesting": len(hits),
        "n_other_pinch_children": n_other,
        "n_parent_drop": n_parent_drop,
        "n_parent_drop_edges": n_parent_drop_edges,
        "n_return_to_c19_length": n_return_c19,
        "n_return_to_DB_edges": n_return_db_edges,
        "min_other_after_len": min_other,
        "shortest_other_after": shortest_others,
        "interesting": hits[:24],
        "any_drop_vs_c19": any(h["drop_vs_c19"] > 0 for h in hits),
        "any_drop_vs_parent": n_parent_drop > 0,
        "any_one_occ": any(h["one_occurrence"] for h in hits),
        "any_two_block": any(h["two_block_both"] for h in hits),
        "any_other_shorter_than_D": bool(min_other is not None and min_other < 7),
    }


def family_alignment(scans: list[dict]) -> dict:
    """Compare the ten B-words across n after stripping the n-dependent x-run."""
    by_move = {}
    for rec in scans:
        n = rec["n"]
        for i, row in enumerate(rec["family"]):
            key = (row["move"]["target"], row["move"]["jsign"], row["move"]["k1"], row["move"]["k2"])
            by_move.setdefault(i, []).append(
                {
                    "n": n,
                    "B": row["B"],
                    "B_len": row["B_len"],
                    "move": row["move"],
                    "len_minus_n": row["B_len"] - n,
                }
            )
    # Moves are not necessarily in a stable order. Compare length offsets.
    offset_sets = []
    for rec in scans:
            offset_sets.append(tuple(sorted(row["B_len"] - 2 * rec["n"] for row in rec["family"])))
    return {
        "B_len_minus_n_sorted": offset_sets,
        "uniform_offset_multiset": len(set(offset_sets)) == 1,
        "n_family_slots": 10,
    }


def gate2_destab_probe() -> dict:
    """Can I_S = u^p x^c y^{-1} be rotated to a generator without C0?

    After the C16 substitutions one has I_S = e Y with e = u^p x^c.
    Cyclic rotations of eY are listed; none is y or Y unless e is empty.
    """
    rows = []
    for n in range(2, 8):
        for delta in (-1, 1):
            p, c = 2, n * delta
            e = tw.pw("u", p) + tw.pw("x", c)
            isol = cyc_reduce(e + "Y")
            letters = {isol[i:] + isol[:i] for i in range(len(isol))}
            letters |= {inv(w) for w in list(letters)}
            rows.append(
                {
                    "n": n,
                    "delta": delta,
                    "isolator": isol,
                    "is_generator": isol in ("y", "Y"),
                    "any_orientation_generator": any(w in ("y", "Y") for w in letters),
                    "e_len": len(cyc_reduce(e)),
                }
            )
    return {
        "n_checked": len(rows),
        "any_bare_ac5": any(r["any_orientation_generator"] for r in rows),
        "rows": rows,
        "note": (
            "Bare AC5 needs a relator that is the generator y. "
            "I_S = u^2 x^{nδ} y^{-1} is never that generator for n=2..7."
        ),
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    scans = [scan_n(n) for n in range(2, 8)]
    destab = gate2_destab_probe()
    align = family_alignment(scans)
    summary = {
        "n_checked": len(scans),
        "uniform_B_len_minus_2n": align["uniform_offset_multiset"],
        "B_len_minus_2n_sorted": align["B_len_minus_n_sorted"],
        "any_drop_vs_c19": any(s["any_drop_vs_c19"] for s in scans),
        "any_drop_vs_parent": any(s["any_drop_vs_parent"] for s in scans),
        "any_one_occ": any(s["any_one_occ"] for s in scans),
        "any_two_block": any(s["any_two_block"] for s in scans),
        "any_other_shorter_than_D": any(s["any_other_shorter_than_D"] for s in scans),
        "min_other_after_len": {s["n"]: s["min_other_after_len"] for s in scans},
        "n_return_to_c19_length": {s["n"]: s["n_return_to_c19_length"] for s in scans},
        "n_return_to_DB_edges": {s["n"]: s["n_return_to_DB_edges"] for s in scans},
        "n_parent_drop": {s["n"]: s["n_parent_drop"] for s in scans},
        "n_parent_drop_edges": {s["n"]: s["n_parent_drop_edges"] for s in scans},
        "interesting_counts": {s["n"]: s["n_interesting"] for s in scans},
        "grandchild_unique": {s["n"]: s["n_grandchildren_unique"] for s in scans},
        "gate2_bare_ac5": destab["any_bare_ac5"],
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "alignment": align,
        "gate2_destab": destab,
        "scans": scans,
        "notes": [
            "Depth-2 is one extra AC2 from each of the ten C20 no-pinch children.",
            "Uniqueness is canon_pair. A miss is not an obstruction to depth ≥ 3.",
            "Bare AC5 of I_S is a negative for making C16 Gate 2 elementary.",
            "Incoming C16 still has two Lemma-11 uses. Not a U124 solve.",
        ],
    }
    path = OUT / "c21_depth2.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c21 depth-2")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
