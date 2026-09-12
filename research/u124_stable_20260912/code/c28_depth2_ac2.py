#!/usr/bin/env python3
"""C28: depth-2 ordinary AC2 neighbourhood of archival and parametric pairs.

C13/C27.1 scanned depth-1: one AC2, with cyclic orientations of both factors
as AC3 by a prefix. This census applies that neighbourhood twice. Unique
depth-1 children are expanded once each; unique grandchildren are scored
against the original pair.

A miss is not an AC obstruction to depth ≥ 3, stable moves, or Aut with C1.
Not a heap search. Not a U124 solve unless a witness is found and given an
explicit AC1–AC5 path.
"""
from __future__ import annotations

import csv
import json
import sys
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

import family_a_identities as fam  # noqa: E402
import ms_template_identities as ms  # noqa: E402
import q_peel  # noqa: E402
from elementary_ac2_scan import children  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_INITIAL = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c28_depth2_ac2.json"


def concat_cyc(a: str, b: str) -> str:
    """Cyclic reduction of a freely reduced concatenation at the junction.

    Equivalent to ``cyc_reduce(a + b)`` when ``a`` and ``b`` are freely reduced.
    """
    i = 0
    la, lb = len(a), len(b)
    while i < la and i < lb and a[la - 1 - i] == b[i].swapcase():
        i += 1
    s = a[: la - i] + b[i:]
    while len(s) >= 2 and s[0] == s[-1].swapcase():
        s = s[1:-1]
    return s


def children_fast(r1: str, r2: str) -> list[tuple[str, str, dict[str, int]]]:
    """Same pairs and move triples as ``elementary_ac2_scan.children``."""
    out: list[tuple[str, str, dict[str, int]]] = []
    for target in (1, 2):
        ri, rj = (r1, r2) if target == 1 else (r2, r1)
        if not ri or not rj:
            continue
        n = len(ri)
        ri2 = ri + ri
        for jsign, oj in ((1, rj), (-1, inv(rj))):
            m = len(oj)
            oj2 = oj + oj
            for k1 in range(n):
                a = ri2[n - k1 : 2 * n - k1] if k1 else ri
                for k2 in range(m):
                    b = oj2[m - k2 : 2 * m - k2] if k2 else oj
                    piece = concat_cyc(a, b)
                    if not piece:
                        continue
                    pair = (piece, r2) if target == 1 else (r1, piece)
                    move = {
                        "target": target,
                        "jsign": jsign,
                        "k1": k1,
                        "k2": k2,
                        "new_len": len(pair[0]) + len(pair[1]),
                    }
                    out.append((pair[0], pair[1], move))
    return out


def children_agree(r1: str, r2: str) -> bool:
    slow = [
        (a, b, m["target"], m["jsign"], m["k1"], m["k2"])
        for a, b, m in children(r1, r2)
    ]
    fast = [
        (a, b, m["target"], m["jsign"], m["k1"], m["k2"])
        for a, b, m in children_fast(r1, r2)
    ]
    return slow == fast


def one_occ_reduced(word: str) -> bool:
    """Equivalent to ``one_occurrence_cyclic`` on an already cyclically reduced word."""
    if not word:
        return False
    nx = ny = 0
    for char in word:
        if char in "xX":
            nx += 1
        elif char in "yY":
            ny += 1
    return nx == 1 or ny == 1


def two_block_reduced(word: str) -> bool:
    """Equivalent to ``two_block_shape`` on an already cyclically reduced word."""
    if not word:
        return False
    gens = [char.lower() for char in word]
    if len(set(gens)) != 2:
        return False
    return sum(gens[i] != gens[i - 1] for i in range(len(gens))) == 2


def unique_children(
    r1: str, r2: str
) -> list[tuple[str, str, dict[str, int]]]:
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str, dict[str, int]]] = []
    for a, b, move in children_fast(r1, r2):
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b, move))
    return out


def scan_depth2(
    tag: str,
    r1: str,
    r2: str,
    best: tuple[str, str] | None = None,
) -> dict:
    r1 = cyc_reduce(r1)
    r2 = cyc_reduce(r2)
    base_len = len(r1) + len(r2)
    base_one = one_occ_reduced(r1) or one_occ_reduced(r2)
    base_tb = two_block_reduced(r1) and two_block_reduced(r2)
    best_key = canon_pair(*best) if best is not None else None
    best_len = (
        len(cyc_reduce(best[0])) + len(cyc_reduce(best[1]))
        if best is not None
        else None
    )
    d1 = unique_children(r1, r2)
    n_raw = 0
    n_drop_d1 = n_eq_d1 = n_up_d1 = n_one_d1 = n_tb_d1 = 0
    n_drop = n_eq = n_up = n_one = n_tb = 0
    n_hit_best = 0
    best_child_len = base_len
    hit = None

    def consider(
        a: str,
        b: str,
        length: int,
        depth: int,
        move1: dict[str, int],
        move2: dict[str, int] | None,
    ) -> None:
        nonlocal best_child_len, hit, n_hit_best
        dropped = length < base_len
        new_one = (not base_one) and (one_occ_reduced(a) or one_occ_reduced(b))
        new_tb = (not base_tb) and two_block_reduced(a) and two_block_reduced(b)
        if dropped and length < best_child_len:
            best_child_len = length
        interesting = dropped or new_one or new_tb
        if interesting:
            rec = {
                "depth": depth,
                "new_r1": a,
                "new_r2": b,
                "len": length,
                "drop": max(0, base_len - length),
                "move1": move1,
                "move2": move2,
                "one_occurrence": one_occ_reduced(a) or one_occ_reduced(b),
                "two_block_both": two_block_reduced(a) and two_block_reduced(b),
            }
            if hit is None:
                hit = rec
            elif dropped and hit["drop"] == 0:
                hit = rec
        if (
            best_key is not None
            and best_len is not None
            and length <= best_len
            and canon_pair(a, b) == best_key
        ):
            n_hit_best += 1

    for a, b, move1 in d1:
        length = len(a) + len(b)
        if length < base_len:
            n_drop_d1 += 1
        elif length == base_len:
            n_eq_d1 += 1
        else:
            n_up_d1 += 1
        if not base_one and (one_occ_reduced(a) or one_occ_reduced(b)):
            n_one_d1 += 1
        if not base_tb and two_block_reduced(a) and two_block_reduced(b):
            n_tb_d1 += 1
        consider(a, b, length, 1, move1, None)

    seen: set[tuple[str, str]] = set()
    for a, b, move1 in d1:
        for c, d, move2 in children_fast(a, b):
            n_raw += 1
            key = (c, d)
            if key in seen:
                continue
            seen.add(key)
            length = len(c) + len(d)
            if length < base_len:
                n_drop += 1
            elif length == base_len:
                n_eq += 1
            else:
                n_up += 1
            if not base_one and (one_occ_reduced(c) or one_occ_reduced(d)):
                n_one += 1
            if not base_tb and two_block_reduced(c) and two_block_reduced(d):
                n_tb += 1
            consider(c, d, length, 2, move1, move2)
    return {
        "tag": tag,
        "in_len": base_len,
        "best_table_len": best_len,
        "best_child_len": best_child_len,
        "drop": base_len - best_child_len,
        "n_d1_unique": len(d1),
        "n_d1_drop_unique": n_drop_d1,
        "n_d1_eq_unique": n_eq_d1,
        "n_d1_up_unique": n_up_d1,
        "n_d1_new_one_occ": n_one_d1,
        "n_d1_new_two_block": n_tb_d1,
        "n_d2_raw": n_raw,
        "n_d2_unique": len(seen),
        "n_drop_unique": n_drop,
        "n_eq_unique": n_eq,
        "n_up_unique": n_up,
        "n_new_one_occ": n_one,
        "n_new_two_block": n_tb,
        "n_hit_best": n_hit_best,
        "hit": hit,
        "found": hit is not None,
    }


def planted() -> dict:
    hit = scan_depth2("planted_x_xy", "x", "xy")
    miss = scan_depth2("planted_x_y", "x", "y")
    agree = (
        children_agree("x", "xy")
        and children_agree("x", "y")
        and children_agree(*ms.parametric_p(2, -1))
    )
    return {
        "hit_found": hit["drop"] > 0,
        "hit_drop": hit["drop"],
        "hit_depth": None if hit["hit"] is None else hit["hit"]["depth"],
        "miss_drop": miss["drop"],
        "miss_d1_drop": miss["n_d1_drop_unique"],
        "miss_d2_drop": miss["n_drop_unique"],
        "children_fast_agrees": agree,
        "ok": hit["drop"] > 0 and miss["drop"] == 0 and agree,
        "independent_checker": False,
        "same_code_as_census": True,
        "hit": hit["hit"],
        "note": (
            "Miss control is no length drop on ⟨x,y⟩; lengthening "
            "two-block grandchildren of ⟨x,y⟩ are expected at depth 2."
        ),
    }


def parametric_pairs() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for n in range(2, 8):
        for delta in (-1, 1):
            p = ms.parametric_p(n, delta)
            rows.append((f"P[{n},{delta}]", p[0], p[1]))
            q = q_peel.q_pair(n, delta)
            rows.append((f"Q[{n},{delta}]", q[0], q[1]))
        fp = fam.parametric_p(n)
        rows.append((f"FA_P[{n}]", fp[0], fp[1]))
        fq = q_peel.family_a_q(n)
        rows.append((f"FA_Q[{n}]", fq[0], fq[1]))
    return rows


def scan_parametric() -> list[dict]:
    return [scan_depth2(tag, r1, r2) for tag, r1, r2 in parametric_pairs()]


def scan_initial_table() -> dict:
    with DATA_INITIAL.open(newline="", encoding="utf-8") as handle:
        initial = list(csv.DictReader(handle))
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        best = {row["name"]: row for row in csv.DictReader(handle)}
    rows = []
    n_changed = 0
    n_drop_d1 = 0
    n_drop = 0
    n_one = 0
    n_tb = 0
    n_hit_best = 0
    n_d2_raw = 0
    n_d2_unique = 0
    interesting = []
    for row in initial:
        name = row["name"]
        b = best[name]
        changed = (row["r1"], row["r2"]) != (b["r1"], b["r2"])
        if changed:
            n_changed += 1
        rec = scan_depth2(
            name,
            row["r1"],
            row["r2"],
            best=(b["r1"], b["r2"]) if changed else None,
        )
        rec["id"] = name
        rec["changed_from_best"] = changed
        n_drop_d1 += rec["n_d1_drop_unique"]
        n_drop += rec["n_drop_unique"]
        n_one += rec["n_new_one_occ"]
        n_tb += rec["n_new_two_block"]
        n_hit_best += rec["n_hit_best"]
        n_d2_raw += rec["n_d2_raw"]
        n_d2_unique += rec["n_d2_unique"]
        rows.append(rec)
        if rec["found"] or rec["n_hit_best"]:
            interesting.append(rec)
        print(
            f"c28 {name} d1={rec['n_d1_unique']} d2u={rec['n_d2_unique']} "
            f"d1drop={rec['n_d1_drop_unique']} d2drop={rec['n_drop_unique']} "
            f"found={rec['found']}",
            flush=True,
        )
    return {
        "n_rows": len(initial),
        "n_changed_from_best": n_changed,
        "n_interesting_rows": len(interesting),
        "n_d2_raw": n_d2_raw,
        "n_d2_unique_sum": n_d2_unique,
        "n_d1_drop_unique_total": n_drop_d1,
        "n_drop_unique_total": n_drop,
        "n_new_one_occ_total": n_one,
        "n_new_two_block_total": n_tb,
        "n_hit_best_total": n_hit_best,
        "interesting": interesting,
        "rows": rows,
    }


def summarize(ctrl: dict, parametric: list[dict], initial: dict) -> dict:
    return {
        "planted_ok": ctrl["ok"],
        "children_fast_agrees": ctrl["children_fast_agrees"],
        "parametric_n": len(parametric),
        "parametric_any_hit": any(row["found"] for row in parametric),
        "parametric_any_drop": any(row["drop"] > 0 for row in parametric),
        "parametric_any_d1_drop": any(row["n_d1_drop_unique"] > 0 for row in parametric),
        "initial_n_rows": initial["n_rows"],
        "initial_n_changed_from_best": initial["n_changed_from_best"],
        "initial_any_hit": initial["n_interesting_rows"] > 0,
        "initial_any_length_drop": (
            initial["n_d1_drop_unique_total"] > 0
            or initial["n_drop_unique_total"] > 0
        ),
        "initial_n_d1_drop_unique_total": initial["n_d1_drop_unique_total"],
        "initial_n_drop_unique_total": initial["n_drop_unique_total"],
        "initial_n_new_one_occ_total": initial["n_new_one_occ_total"],
        "initial_n_new_two_block_total": initial["n_new_two_block_total"],
        "initial_n_hit_best_total": initial["n_hit_best_total"],
        "initial_n_d2_raw": initial["n_d2_raw"],
        "d2_counts_are_unique_presentations": True,
        "d2_raw_is_enumerated_edges": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "Depth ≤ 2: unique depth-1 children are scored against the input, then each is expanded once. Depth-2 is a second C13/C27.1 neighbourhood, not a longer AC3–AC2 composite.",
        "children_fast is junction cyclic reduction; tested equal to elementary_ac2_scan.children including move triples.",
        "Unique depth-1 parents are expanded once. Unique grandchildren are (r1, r2) spellings, not canon_pair classes.",
        "Raw grandchild counts include (k1, k2) multiplicity and are not the unique-presentation counts.",
        "A length drop would be an ordinary AC1–AC3 path of two AC2 steps (rotations as AC3). No Aut, no C0.",
        "Matching the stored best table is checked only on changed rows, and only when grandchild length is at most the best length.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    ctrl = planted()
    print("c28 planted", ctrl["ok"], flush=True)
    parametric = scan_parametric()
    print(
        f"c28 parametric n={len(parametric)} any={any(r['found'] for r in parametric)}",
        flush=True,
    )
    initial = scan_initial_table()
    print(
        f"c28 initial rows={initial['n_rows']} changed={initial['n_changed_from_best']} "
        f"interesting={initial['n_interesting_rows']}",
        flush=True,
    )
    summary = summarize(ctrl, parametric, initial)
    report = {
        "summary": summary,
        "planted": ctrl,
        "parametric": parametric,
        "initial": initial,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c28 depth-2 archival AC2")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = planted()
    summary = summarize(ctrl, report["parametric"], report["initial"])
    report["summary"] = summary
    report["planted"] = ctrl
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c28 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
