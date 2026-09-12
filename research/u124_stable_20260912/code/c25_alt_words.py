#!/usr/bin/env python3
"""C25: alternative defining words on Q', and the C15 conjugator class.

C24 left two conjugator-independent leftovers that are abelian identities:

- On Q', the generator x has the same exponent vector as ξ, so C24.1 applies
  verbatim. C23 checked 3-factor products against ξ, not against x.
- On the C15 family, both y and the C22.6 conjugator x^{-1} y x abelianize to
  B^{-1} (L1=1). k=1 is a length obstruction (|B|=2m+3 ≥ 9). Even k is
  impossible. The next value is k=3.

Not a heap search. Not a U124 solve unless a witness is found and replayed.
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

import c15_divisibility_scan as c15  # noqa: E402
import c22_gate_witness as c22  # noqa: E402
import c23_three_factor as c23  # noqa: E402
import c24_even_k as c24  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

ALPHABET = "xXyY"
Y_CLASS = ("y", "Y", "Xyx", "XYx", "xyX", "xYX")


def l1_of(sol: dict) -> int | None:
    return c24.l1_combo(sol)


def y_l1_closed(n: int, delta: int) -> int:
    return abs(n + 2 * delta) + 1


def scan_three_against(
    r_plus_word: str,
    r_minus_word: str,
    s_plus_word: str,
    s_minus_word: str,
    conjugators: list[str],
    targets: set[str],
) -> dict:
    r_plus = c23.unique_conjugates(r_plus_word, conjugators)
    r_minus = c23.unique_conjugates(r_minus_word, conjugators)
    s_plus = c23.unique_conjugates(s_plus_word, conjugators)
    s_minus = c23.unique_conjugates(s_minus_word, conjugators)
    hit = None
    min_len = None
    n_products = 0
    n_len_le_3 = 0
    for lists in c23.three_factor_configs(r_plus, r_minus, s_plus, s_minus):
        for a, b, c in product(*lists):
            word = free_reduce(a + b + c)
            n_products += 1
            length = len(word)
            if min_len is None or length < min_len:
                min_len = length
            if length <= 3:
                n_len_le_3 += 1
            if word in targets:
                hit = {"word": word, "len": length}
    return {
        "n_conjugators": len(conjugators),
        "n_Rplus": len(r_plus),
        "n_Rminus": len(r_minus),
        "n_Splus": len(s_plus),
        "n_Sminus": len(s_minus),
        "n_products": n_products,
        "min_len": min_len,
        "n_len_le_3": n_len_le_3,
        "hit": hit,
        "found": hit is not None,
        "pool": "globally_deduplicated_per_type_then_configs",
    }


def q_prime_x_l1(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    er, es, ex = c22.exp_on(r, "xy"), c22.exp_on(s, "xy"), c22.exp_on("x", "xy")
    sol = c22.solve_2x2(er[0], es[0], er[1], es[1], ex[0], ex[1])
    xi_sol = c22.solve_2x2(er[0], es[0], er[1], es[1], 1, 0)
    return {
        "n": n,
        "delta": delta,
        "x_exp": list(ex),
        "xi_exp": [1, 0],
        "combo": sol,
        "xi_combo": xi_sol,
        "same_abelian_class_as_xi": sol.get("a") == xi_sol.get("a")
        and sol.get("b") == xi_sol.get("b"),
        "L1": l1_of(sol),
        "R_cyc_len": len(cyc_reduce(r)),
        "k1_len_obstruction": len(cyc_reduce(r)) > 1,
    }


def q_prime_y_l1(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    er, es, ey = c22.exp_on(r, "xy"), c22.exp_on(s, "xy"), c22.exp_on("y", "xy")
    sol = c22.solve_2x2(er[0], es[0], er[1], es[1], ey[0], ey[1])
    closed = y_l1_closed(n, delta)
    l1 = l1_of(sol)
    return {
        "n": n,
        "delta": delta,
        "combo": sol,
        "L1": l1,
        "expected_L1": closed,
        "matches_closed": l1 == closed
        and sol.get("a") == n + 2 * delta
        and sol.get("b") == -1,
        "S_cyc_len": len(cyc_reduce(s)),
        "k1_len_obstruction": len(cyc_reduce(s)) > 1,
        "odd_k_forbidden": l1 is not None and l1 % 2 == 0,
        "even_k_forbidden": l1 is not None and l1 % 2 == 1,
        "min_k": l1,
    }


def q_prime_x_three_factor(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    r_delta = r if delta == 1 else inv(r)
    conjugators = c22.short_conjugators([r, s], ALPHABET, 1)
    rec = scan_three_against(r_delta, inv(r_delta), s, inv(s), conjugators, {"x", "X"})
    rec.update({"n": n, "delta": delta, "targets": ["x", "X"]})
    return rec


def c15_row_abelian(name: str, companion: str, m: int) -> dict:
    donor = c15.DONOR
    ed, eb = c22.exp_on(donor, "xy"), c22.exp_on(companion, "xy")
    rows = {}
    for word in ("y", "Xyx", "x", tw.XI):
        ew = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], eb[0], ed[1], eb[1], ew[0], ew[1])
        rows[word] = {
            "exp": list(ew),
            "combo": sol,
            "L1": l1_of(sol),
        }
    b_len = len(cyc_reduce(companion))
    return {
        "id": name,
        "m": m,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "B_exp": list(eb),
        "B_cyc_len": b_len,
        "B_len_is_2m3": b_len == 2 * m + 3,
        "y_L1": rows["y"]["L1"],
        "Xyx_L1": rows["Xyx"]["L1"],
        "y_combo": rows["y"]["combo"],
        "Xyx_combo": rows["Xyx"]["combo"],
        "y_same_class_as_Xyx": rows["y"]["combo"].get("a") == rows["Xyx"]["combo"].get("a")
        and rows["y"]["combo"].get("b") == rows["Xyx"]["combo"].get("b"),
        "k1_len_obstruction": b_len > 3,
        "targets": rows,
    }


def c15_three_factor(name: str, companion: str, m: int) -> dict:
    donor = c15.DONOR
    conjugators = c22.short_conjugators([donor, companion], ALPHABET, 1)
    # Target class (0,1) ≡ B^{-1}; r_plus is B^{-1}.
    rec = scan_three_against(
        inv(companion),
        companion,
        donor,
        inv(donor),
        conjugators,
        set(Y_CLASS),
    )
    rec.update(
        {
            "id": name,
            "m": m,
            "targets": list(Y_CLASS),
            "B_cyc_len": len(cyc_reduce(companion)),
            "D_cyc_len": len(cyc_reduce(donor)),
        }
    )
    return rec


def y_class_free_targets() -> dict:
    words = []
    for g in ("", "x", "X", "y", "Y"):
        words.append(free_reduce(inv(g) + "y" + g))
        words.append(free_reduce(inv(g) + "Y" + g))
    reduced = sorted(set(words))
    return {
        "one_letter_conjugates_of_y": reduced,
        "stated_class": list(Y_CLASS),
        "class_covers_one_letter": set(Y_CLASS) == set(reduced),
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    x_l1 = [q_prime_x_l1(n, d) for d in (-1, 1) for n in range(2, 8)]
    y_l1 = [q_prime_y_l1(n, d) for d in (-1, 1) for n in range(2, 21)]
    y_l1_u124 = [row for row in y_l1 if row["n"] <= 7]
    x_three = [q_prime_x_three_factor(n, d) for d in (-1, 1) for n in range(2, 8)]
    c15_ab = [c15_row_abelian(name, companion, m) for name, companion, m in c15.ROWS]
    c15_three = [c15_three_factor(name, companion, m) for name, companion, m in c15.ROWS]
    yclass = y_class_free_targets()
    summary = {
        "x_same_class_as_xi_all_Q": all(row["same_abelian_class_as_xi"] for row in x_l1),
        "x_L1_always_1": all(row["L1"] == 1 for row in x_l1),
        "x_three_any_hit": any(row["found"] for row in x_three),
        "x_three_n_checked": len(x_three),
        "x_three_n_products": sum(row["n_products"] for row in x_three),
        "x_three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in x_three),
        "y_L1_closed_n_le_20": all(row["matches_closed"] for row in y_l1),
        "y_L1_formula": "|n+2δ|+1",
        "c15_n_rows": len(c15_ab),
        "c15_B_len_always_2m3": all(row["B_len_is_2m3"] for row in c15_ab),
        "c15_y_Xyx_same_class": all(row["y_same_class_as_Xyx"] for row in c15_ab),
        "c15_y_L1_always_1": all(row["y_L1"] == 1 for row in c15_ab),
        "c15_Xyx_L1_always_1": all(row["Xyx_L1"] == 1 for row in c15_ab),
        "c15_k1_len_all": all(row["k1_len_obstruction"] for row in c15_ab),
        "c15_three_any_hit": any(row["found"] for row in c15_three),
        "c15_three_n_checked": len(c15_three),
        "c15_three_n_products": sum(row["n_products"] for row in c15_three),
        "c15_three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in c15_three),
        "y_class_covers_one_letter": yclass["class_covers_one_letter"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "q_prime_x_l1": x_l1,
        "q_prime_y_l1": y_l1_u124,
        "q_prime_x_three_factor": x_three,
        "c15_abelian": c15_ab,
        "c15_three_factor": c15_three,
        "y_class": yclass,
        "notes": [
            "x ≡ ξ in abelianization on every Q'_{n,δ}; C24.1 even-k obstruction applies.",
            "C23 3-factor A/B products are the abelian-legal 3-factor set for x as well; this scan checks x^{±1}.",
            "y on Q' has L1=|n+2δ|+1 for all n≥2; k=1 is |S|≥7>1. Not enumerated here except the identity.",
            "C15: y and Xyx both ≡ B^{-1}, L1=1, |B|=2m+3≥9. Three-factor prefix/one-letter on all 10 rows.",
            "Y_CLASS is the one-letter conjugacy class of y^{±1}. A hit would be a C12 or C22.6 route.",
            "JSON is same-code deterministic replay. No U124 row is solved.",
        ],
    }
    path = OUT / "c25_alt_words.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c25 alt defining words / C15 conjugator")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
