#!/usr/bin/env python3
"""C27: archival depth-1 AC2, and k=L1+2 for y on the unique L1=2 Q' cell.

C13 scanned the best table. Thirty-six μ-floor rows have a different
archival initial spelling; this census repeats the depth-1 ordinary AC2
neighbourhood on aca_124_initial.csv and on the parametric P/Q/Family A
families. A miss is not an AC obstruction.

C26 left k=L1+2t. The unique Q'_{n,δ} with L1(y)=2 is (n,δ)=(3,-1),
combination (1,-1). Then k=4 is the first extra cancelling pair: either
two R^+, one R^-, one S^-, or one R^+, one S^+, two S^-. Prefix/one-letter
typed Cartesian products; a hit is a normal-closure candidate, not C12.

Not a heap search. Not a U124 solve unless a witness is found and given an
explicit AC1–AC5 path.
"""
from __future__ import annotations

import csv
import json
import sys
from itertools import permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    cyc_reduce,
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c22_gate_witness as c22  # noqa: E402
import c23_three_factor as c23  # noqa: E402
import c26_y_exact_l1 as c26  # noqa: E402
import family_a_identities as fam  # noqa: E402
import ms_template_identities as ms  # noqa: E402
import q_peel  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children, flags  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_INITIAL = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
ALPHABET = "xXyY"
POSITIVE_Y = c26.POSITIVE_Y
K4_CONFIGS = (
    {"Rp": 2, "Rm": 1, "Sm": 1},
    {"Rp": 1, "Sp": 1, "Sm": 2},
)


def type_sequences(counts: dict[str, int]) -> list[tuple[str, ...]]:
    letters: list[str] = []
    for name, n in counts.items():
        letters.extend([name] * n)
    return sorted(set(permutations(letters)))


def typed_size(counts: dict[str, int], pools: dict[str, list[str]]) -> int:
    n_seq = len(type_sequences(counts))
    local = 1
    for key, m in counts.items():
        local *= len(pools[key]) ** m
    return n_seq * local


def scan_ac2_pair(tag: str, r1: str, r2: str) -> dict:
    base = flags(r1, r2)
    n_drop = n_eq = n_up = n_one = n_tb = 0
    best_len = base["length"]
    hit = None
    seen: set[tuple[str, str]] = set()
    n_kids = 0
    for a, b, move in children(r1, r2):
        n_kids += 1
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        feat = flags(a, b)
        if feat["length"] < base["length"]:
            n_drop += 1
            if feat["length"] < best_len:
                best_len = feat["length"]
            if hit is None:
                hit = {
                    "new_r1": a,
                    "new_r2": b,
                    "len": feat["length"],
                    "drop": base["length"] - feat["length"],
                    "move": move,
                    "one_occurrence": feat["one_occurrence"],
                    "two_block_both": feat["two_block_both"],
                }
        elif feat["length"] == base["length"]:
            n_eq += 1
        else:
            n_up += 1
        if feat["one_occurrence"] and not base["one_occurrence"]:
            n_one += 1
        if feat["two_block_both"] and not base["two_block_both"]:
            n_tb += 1
    return {
        "tag": tag,
        "in_len": base["length"],
        "best_child_len": best_len,
        "drop": base["length"] - best_len,
        "n_kids": n_kids,
        "n_unique": len(seen),
        "n_drop_unique": n_drop,
        "n_eq_unique": n_eq,
        "n_up_unique": n_up,
        "n_new_one_occ": n_one,
        "n_new_two_block": n_tb,
        "hit": hit,
        "found": hit is not None or n_one > 0 or n_tb > 0,
    }


def ac2_planted() -> dict:
    rec = scan_ac2_pair("planted_x_xy", "x", "xy")
    miss = scan_ac2_pair("planted_x_y", "x", "y")
    return {
        "hit_found": rec["found"] and rec["drop"] > 0,
        "miss_found": miss["found"],
        "ok": rec["found"] and rec["drop"] > 0 and not miss["found"],
        "independent_checker": False,
        "same_code_as_census": True,
        "hit": rec["hit"],
    }


def scan_parametric() -> list[dict]:
    rows = []
    for n in range(2, 8):
        for delta in (-1, 1):
            p = ms.parametric_p(n, delta)
            rows.append(scan_ac2_pair(f"P[{n},{delta}]", p[0], p[1]))
            q = q_peel.q_pair(n, delta)
            rows.append(scan_ac2_pair(f"Q[{n},{delta}]", q[0], q[1]))
        fp = fam.parametric_p(n)
        rows.append(scan_ac2_pair(f"FA_P[{n}]", fp[0], fp[1]))
        fq = q_peel.family_a_q(n)
        rows.append(scan_ac2_pair(f"FA_Q[{n}]", fq[0], fq[1]))
    return rows


def scan_initial_table() -> dict:
    with DATA_INITIAL.open(newline="", encoding="utf-8") as handle:
        initial = list(csv.DictReader(handle))
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        best = {row["name"]: row for row in csv.DictReader(handle)}
    interesting = []
    n_changed = 0
    n_kids = 0
    n_drop = 0
    n_eq = 0
    for row in initial:
        name = row["name"]
        b = best[name]
        changed = (row["r1"], row["r2"]) != (b["r1"], b["r2"])
        if changed:
            n_changed += 1
        rec = scan_ac2_pair(name, row["r1"], row["r2"])
        rec["id"] = name
        rec["changed_from_best"] = changed
        n_kids += rec["n_kids"]
        n_drop += rec["n_drop_unique"]
        n_eq += rec["n_eq_unique"]
        if rec["found"]:
            interesting.append(rec)
    return {
        "n_rows": len(initial),
        "n_changed_from_best": n_changed,
        "n_interesting_rows": len(interesting),
        "n_kids": n_kids,
        "n_drop_unique_total": n_drop,
        "n_eq_unique_total": n_eq,
        "interesting": interesting,
    }


def scan_k4(n: int = 3, delta: int = -1, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_Y)
    a, b, l1 = c26.y_combo(n, delta)
    if (a, b, l1) != (1, -1, 2):
        raise ValueError("k=4 extra-pair census is for the unique L1=2 cell")
    r, s = tw.q_prime(n, delta)
    conjugators = c22.short_conjugators([r, s], ALPHABET, 1)
    pools = {
        "Rp": c23.unique_conjugates(r, conjugators),
        "Rm": c23.unique_conjugates(inv(r), conjugators),
        "Sp": c23.unique_conjugates(s, conjugators),
        "Sm": c23.unique_conjugates(inv(s), conjugators),
    }
    hit = None
    min_len = None
    n_products = 0
    n_hits = 0
    n_len_le_3 = 0
    n_typed = 0
    config_rows = []
    for counts in K4_CONFIGS:
        seqs = type_sequences(counts)
        size = typed_size(counts, pools)
        n_typed += size
        for seq in seqs:
            factor_lists = [pools[label] for label in seq]
            for parts in product(*factor_lists):
                word = free_reduce("".join(parts))
                n_products += 1
                length = len(word)
                if min_len is None or length < min_len:
                    min_len = length
                if length <= 3:
                    n_len_le_3 += 1
                if word in targets:
                    n_hits += 1
                    if hit is None:
                        hit = {"word": word, "seq": list(seq), "len": length}
        config_rows.append(
            {
                "counts": counts,
                "n_sequences": len(seqs),
                "pool_sizes": {k: len(pools[k]) for k in counts},
                "n_typed_tuples": size,
            }
        )
    return {
        "n": n,
        "delta": delta,
        "combo_a": a,
        "combo_b": b,
        "L1": l1,
        "k": 4,
        "n_conjugators": len(conjugators),
        "pool_sizes": {k: len(v) for k, v in pools.items()},
        "n_typed_tuples": n_typed,
        "n_products": n_products,
        "n_products_equals_typed": n_products == n_typed,
        "min_len": min_len,
        "n_len_le_3": n_len_le_3,
        "n_hits": n_hits,
        "hit": hit,
        "found": hit is not None,
        "targets": sorted(targets),
        "configs": config_rows,
        "counts_are_typed_cartesian": True,
        "not_F_to_the_k": True,
        "negative_targets_via_inversion": True,
        "R_cyc_len": len(cyc_reduce(r)),
        "S_cyc_len": len(cyc_reduce(s)),
    }


def k4_planted() -> dict:
    """Same-code typed Cartesian hit/miss, not the Q' census."""
    pools = {"Rp": ["x"], "Rm": ["X"], "Sp": ["y"], "Sm": ["Y"]}
    counts = {"Rp": 2, "Rm": 1, "Sm": 1}
    hit = None
    miss = None
    n = 0
    for seq in type_sequences(counts):
        for parts in product(*[pools[label] for label in seq]):
            word = free_reduce("".join(parts))
            n += 1
            if word == "xY":
                hit = {"word": word, "seq": list(seq)}
            if word == "u":
                miss = word
    expected = typed_size(counts, pools)
    return {
        "n_products": n,
        "n_typed": expected,
        "hit": hit,
        "miss": miss,
        "ok": hit is not None and miss is None and n == expected,
        "independent_checker": False,
        "same_code_as_census": True,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    ac2_ctrl = ac2_planted()
    print("c27 ac2 planted", ac2_ctrl["ok"], flush=True)
    parametric = scan_parametric()
    print(
        f"c27 parametric n={len(parametric)} any={any(r['found'] for r in parametric)}",
        flush=True,
    )
    initial = scan_initial_table()
    print(
        f"c27 initial rows={initial['n_rows']} changed={initial['n_changed_from_best']} "
        f"interesting={initial['n_interesting_rows']}",
        flush=True,
    )
    k4 = scan_k4()
    print(
        f"c27 k4 typed={k4['n_typed_tuples']} min_len={k4['min_len']} found={k4['found']}",
        flush=True,
    )
    k4_ctrl = k4_planted()
    summary = {
        "ac2_planted_ok": ac2_ctrl["ok"],
        "parametric_n": len(parametric),
        "parametric_any_hit": any(row["found"] for row in parametric),
        "parametric_any_drop": any(row["drop"] > 0 for row in parametric),
        "initial_n_rows": initial["n_rows"],
        "initial_n_changed_from_best": initial["n_changed_from_best"],
        "initial_any_hit": initial["n_interesting_rows"] > 0,
        "initial_n_drop_unique_total": initial["n_drop_unique_total"],
        "k4_found": k4["found"],
        "k4_n_typed_tuples": k4["n_typed_tuples"],
        "k4_n_products": k4["n_products"],
        "k4_min_len": k4["min_len"],
        "k4_products_equal_typed": k4["n_products_equals_typed"],
        "counts_are_typed_cartesian": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "ac2_planted": ac2_ctrl,
        "k4_planted": k4_ctrl,
        "parametric": parametric,
        "initial": initial,
        "k4": k4,
        "notes": [
            "C13 scanned the best table; C27.1 scans archival initial spellings and parametric P/Q/Family A.",
            "C27.2 is k=L1+2=4 on the unique L1(y)=2 cell Q'_{3,-1}; two extra-pair type configs.",
            "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^k.",
            "A k=4 hit would be a normal-closure candidate, not a C12 path.",
            "JSON is same-code deterministic replay. No U124 row is solved.",
        ],
    }
    path = OUT / "c27_archival_k4.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c27 archival AC2 / k=4 y")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
