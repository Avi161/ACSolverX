#!/usr/bin/env python3
"""C23: three-factor Gate 1 ncl, and F3 conjugators after AC4.

C22 ruled out one- and two-factor conjugate products for ξ. Abelianization
forces every three-factor product equal to ξ to be one of two shapes:

A. two conjugates of R^δ and one of R^{-δ} (any order)
B. one conjugate of R^δ and a pair of opposite-sign S conjugates (any order)

This script enumerates those shapes with the C22 prefix/one-letter conjugator
set for n=2..7 and both signs, and enumerates restore-preserving depth ≤ 2
on the AC4 third relator with conjugators in F(x,y,u).

Not a heap search. Not a U124 solve.
"""
from __future__ import annotations

import json
import sys
from itertools import product
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
import theory_wave1_replay as tw  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

XI = tw.XI
D_ROW = c22.D_ROW  # UYxy, length 4


def unique_conjugates(donor: str, conjugators: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for g in conjugators:
        word = c22.conjugate(donor, g)
        if word and word not in seen:
            seen.add(word)
            out.append(word)
    return out


def three_factor_configs(
    r_plus: list[str],
    r_minus: list[str],
    s_plus: list[str],
    s_minus: list[str],
) -> list[list[list[str]]]:
    configs: list[list[list[str]]] = []
    for pos in range(3):
        lists = [r_plus, r_plus, r_plus]
        lists[pos] = r_minus
        configs.append(lists)
    for pos in range(3):
        others = [i for i in range(3) if i != pos]
        for order in ((s_plus, s_minus), (s_minus, s_plus)):
            lists = [r_plus, r_plus, r_plus]
            lists[pos] = r_plus
            lists[others[0]], lists[others[1]] = order
            configs.append(lists)
    return configs


def scan_three_factor(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    r_delta = r if delta == 1 else inv(r)
    conjugators = c22.short_conjugators([r, s], "xXyY", 1)
    r_plus = unique_conjugates(r_delta, conjugators)
    r_minus = unique_conjugates(inv(r_delta), conjugators)
    s_plus = unique_conjugates(s, conjugators)
    s_minus = unique_conjugates(inv(s), conjugators)
    target = {XI, inv(XI)}
    min_len = None
    hit = None
    n_products = 0
    n_len7 = 0
    for lists in three_factor_configs(r_plus, r_minus, s_plus, s_minus):
        for a, b, c in product(*lists):
            word = free_reduce(a + b + c)
            n_products += 1
            length = len(word)
            if min_len is None or length < min_len:
                min_len = length
            if length == 7:
                n_len7 += 1
            if word in target:
                hit = {"word": word, "inverted": word == inv(XI), "len": length}
    return {
        "n": n,
        "delta": delta,
        "n_conjugators": len(conjugators),
        "n_Rdelta": len(r_plus),
        "n_Rinv": len(r_minus),
        "n_S": len(s_plus),
        "n_Sinv": len(s_minus),
        "n_products": n_products,
        "min_len": min_len,
        "n_len7": n_len7,
        "hit": hit,
        "found": hit is not None,
        "R_len": len(cyc_reduce(r)),
        "S_len": len(cyc_reduce(s)),
        "xi_len": len(XI),
        "W": free_reduce(inv(r_delta) + XI),
        "W_len": len(free_reduce(inv(r_delta) + XI)),
    }


def f3_depth2(n: int, delta: int) -> dict:
    """Restore-preserving depth ≤ 2 on the AC4 third relator, F3 conjugators."""
    r, s = tw.q_prime(n, delta)
    conjugators = c22.short_conjugators([r, s], "xXyYuU", 2)
    donors = [r, s, inv(r), inv(s)]
    factors = []
    seen: set[str] = set()
    for donor in donors:
        for g in conjugators:
            word = c22.conjugate(donor, g)
            if word and word not in seen:
                seen.add(word)
                factors.append(word)
    d_free = free_reduce(D_ROW)
    d_inv = inv(d_free)
    d_cyc = cyc_reduce(d_free)
    d_inv_cyc = cyc_reduce(d_inv)

    def is_d(cand: str) -> bool:
        reduced = cyc_reduce(cand)
        return (
            cand in (d_free, d_inv)
            or reduced in (d_cyc, d_inv_cyc)
            or tw.same_cyclic(cand, d_free)
            or tw.same_cyclic(cand, d_inv)
        )
    hit = None
    n_products = 0
    min_len_non_gen = None
    n_return_to_u = 0
    for start in ("u", "U"):
        layer = [start]
        for depth in range(1, 3):
            nxt = []
            nxt_seen: set[str] = set()
            for word in layer:
                for factor in factors:
                    cand = free_reduce(word + factor)
                    n_products += 1
                    if cand in ("u", "U"):
                        n_return_to_u += 1
                    elif min_len_non_gen is None or len(cand) < min_len_non_gen:
                        min_len_non_gen = len(cand)
                    if is_d(cand):
                        hit = {
                            "start": start,
                            "depth": depth,
                            "word": cand,
                            "free_D": cand in (d_free, d_inv),
                            "cyclic_D": tw.same_cyclic(cand, d_free)
                            or tw.same_cyclic(cand, d_inv),
                        }
                        return {
                            "n": n,
                            "delta": delta,
                            "n_conjugators": len(conjugators),
                            "n_factors": len(factors),
                            "n_products": n_products,
                            "min_len_non_generator": min_len_non_gen,
                            "n_return_to_u": n_return_to_u,
                            "hit": hit,
                            "found": True,
                            "D": d_free,
                            "D_len": len(d_free),
                        }
                    if depth < 2 and cand not in nxt_seen:
                        nxt_seen.add(cand)
                        nxt.append(cand)
            layer = nxt
    return {
        "n": n,
        "delta": delta,
        "n_conjugators": len(conjugators),
        "n_factors": len(factors),
        "n_products": n_products,
        "min_len_non_generator": min_len_non_gen,
        "n_return_to_u": n_return_to_u,
        "hit": None,
        "found": False,
        "D": d_free,
        "D_len": len(d_free),
    }


def abelian_three_factor_shapes() -> dict:
    """Sanity: the only 3-factor exponent combinations giving (1,0)."""
    rows = []
    for delta in (-1, 1):
        for n in range(2, 8):
            r, s = tw.q_prime(n, delta)
            er = c22.exp_on(r, "xy")
            es = c22.exp_on(s, "xy")
            want = (1, 0)
            legal = []
            for signs in product((-1, 1), repeat=3):
                for types in product("RS", repeat=3):
                    vec = [0, 0]
                    for sign, typ in zip(signs, types):
                        src = er if typ == "R" else es
                        vec[0] += sign * src[0]
                        vec[1] += sign * src[1]
                    if tuple(vec) == want:
                        legal.append({"signs": list(signs), "types": "".join(types)})
            n_r = sum(1 for rec in legal if rec["types"].count("S") == 0)
            n_s = sum(1 for rec in legal if rec["types"].count("S") == 2)
            n_other = len(legal) - n_r - n_s
            rows.append(
                {
                    "n": n,
                    "delta": delta,
                    "n_legal_signed_typed": len(legal),
                    "n_all_R": n_r,
                    "n_one_R_two_S": n_s,
                    "n_other": n_other,
                }
            )
    return {
        "all_only_A_or_B": all(row["n_other"] == 0 for row in rows),
        "rows": rows,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    shapes = abelian_three_factor_shapes()
    three = [scan_three_factor(n, d) for d in (-1, 1) for n in range(2, 8)]
    f3 = [f3_depth2(n, d) for d in (-1, 1) for n in range(2, 8)]
    summary = {
        "abelian_only_shapes_A_and_B": shapes["all_only_A_or_B"],
        "three_factor_any_hit": any(row["found"] for row in three),
        "three_factor_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in three),
        "three_factor_n_checked": len(three),
        "three_factor_n_products": sum(row["n_products"] for row in three),
        "W_len_always_10": all(row["W_len"] == 10 for row in three),
        "f3_any_hit": any(row["found"] for row in f3),
        "f3_n_checked": len(f3),
        "f3_n_products": sum(row["n_products"] for row in f3),
        "f3_all_min_len_non_gen_ge_8": all(
            (row["min_len_non_generator"] or 0) >= 8 for row in f3
        ),
        "D_len": len(D_ROW),
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "abelian_shapes": shapes,
        "three_factor": three,
        "f3_depth2": f3,
        "notes": [
            "Three-factor conjugators are prefix/one-letter, same set as C22.3.",
            "F3 depth-2 conjugators are reduced length ≤ 2 in {x,y,u} plus prefixes.",
            "A miss is not an obstruction to four factors or to longer conjugators.",
            "No U124 row is solved.",
        ],
    }
    path = OUT / "c23_three_factor.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c23 three-factor")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
