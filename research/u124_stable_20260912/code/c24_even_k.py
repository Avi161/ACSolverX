#!/usr/bin/env python3
"""C24: abelian factor-parity for C16 gates, and the next odd/even searches.

C22/C23 ruled out 1- and 3-factor prefix/one-letter products for ξ. Abelianization
gives a uniform parity law: if w ≡ U^α V^β is the unique integer combination,
every conjugate product equal to w has k ≥ |α|+|β| and k ≡ |α|+|β| (mod 2).

Consequences used here:

- Gate 1, target ξ: (α,β)=(δ,0), L1=1. Even k is impossible. Next k is 5.
- Gate 2 on Q'/S_{n,δ}: L1 is even and ≥ 2. Odd k is impossible. k=4 is
  legal only when L1 ≤ 4 (δ=−1 and n∈{2,3,4,5}).

Meet-in-the-middle enumerates the remaining small-k prefix/one-letter products.
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

import c22_gate_witness as c22  # noqa: E402
import c23_three_factor as c23  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

XI = tw.XI
G1_ALPHABET = "xXyY"
G2_ALPHABET = "xXuU"


def l1_combo(sol: dict) -> int | None:
    if not sol.get("ok") or sol.get("a") is None or sol.get("b") is None:
        return None
    return abs(sol["a"]) + abs(sol["b"])


def rotations(word: str) -> list[str]:
    word = free_reduce(word)
    return [word[i:] + word[:i] for i in range(len(word) or 1)]


def donor_factors(relators: list[str], alphabet: str) -> list[str]:
    conjugators = c22.short_conjugators(relators, alphabet, 1)
    seen: set[str] = set()
    out: list[str] = []
    for rel in relators:
        for donor in (rel, inv(rel)):
            for word in c23.unique_conjugates(donor, conjugators):
                if word and word not in seen:
                    seen.add(word)
                    out.append(word)
    return out


def signed_type_legal_count(k: int, er: tuple[int, ...], es: tuple[int, ...], want: tuple[int, int]) -> int:
    n_legal = 0
    for signs in product((-1, 1), repeat=k):
        for types in product("RS", repeat=k):
            vec = [0, 0]
            for sign, typ in zip(signs, types):
                src = er if typ == "R" else es
                vec[0] += sign * src[0]
                vec[1] += sign * src[1]
            if tuple(vec) == want:
                n_legal += 1
    return n_legal


def gate1_hypotheses(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    er, es, exi = c22.exp_on(r, "xy"), c22.exp_on(s, "xy"), c22.exp_on(XI, "xy")
    sol = c22.solve_2x2(er[0], es[0], er[1], es[1], exi[0], exi[1])
    r0, _ = tw.q_prime(2, delta)
    return {
        "n": n,
        "delta": delta,
        "R": r,
        "S": s,
        "R_independent_of_n": r == r0,
        "R_cyc_len": len(cyc_reduce(r)),
        "S_cyc_len": len(cyc_reduce(s)),
        "R_exp": list(er),
        "S_exp": list(es),
        "xi_exp": list(exi),
        "combo": sol,
        "L1": l1_combo(sol),
        "R_exp_is_delta_0": er == (delta, 0),
        "S_y_exp_is_minus_1": es[1] == -1,
        "xi_exp_is_1_0": exi == (1, 0),
        "unimodular": sol.get("det") in (1, -1) and sol.get("ok"),
        "combo_is_delta_0": sol.get("a") == delta and sol.get("b") == 0,
    }


def abelian_k_table(max_k: int = 6) -> dict:
    rows = []
    uniform = True
    for delta in (-1, 1):
        for n in range(2, 8):
            r, s = tw.q_prime(n, delta)
            er, es = c22.exp_on(r, "xy"), c22.exp_on(s, "xy")
            counts = {
                str(k): signed_type_legal_count(k, er, es, (1, 0)) for k in range(1, max_k + 1)
            }
            even_zero = all(counts[str(k)] == 0 for k in range(2, max_k + 1, 2))
            odd_pos = all(counts[str(k)] > 0 for k in range(1, max_k + 1, 2))
            rec = {
                "n": n,
                "delta": delta,
                "counts": counts,
                "even_k_zero": even_zero,
                "odd_k_positive": odd_pos,
                "k1": counts["1"],
                "k3": counts["3"],
                "k5": counts["5"],
            }
            rows.append(rec)
            if not (even_zero and odd_pos and counts["1"] == 1 and counts["3"] == 9 and counts["5"] == 100):
                uniform = False
    return {
        "uniform_gate1_counts": uniform,
        "even_k_all_zero": all(row["even_k_zero"] for row in rows),
        "k1_always_1": all(row["k1"] == 1 for row in rows),
        "k3_always_9": all(row["k3"] == 9 for row in rows),
        "k5_always_100": all(row["k5"] == 100 for row in rows),
        "rows": rows,
    }


def mitm_product(
    factors: list[str],
    primary_targets: list[str],
    left_arity: int,
    right_arity: int,
    extra_targets: list[str] | None = None,
) -> dict:
    """All concatenations of left_arity then right_arity factors; free equality."""
    primary_set = {free_reduce(t) for t in primary_targets}
    extra_set = {free_reduce(t) for t in (extra_targets or [])} - primary_set
    right: set[str] = set()
    n_right = 0
    for parts in product(factors, repeat=right_arity):
        word = free_reduce("".join(parts))
        n_right += 1
        right.add(word)
    hit = None
    extra_hit = None
    n_left = 0
    n_primary_hits = 0
    n_extra_hits = 0
    for parts in product(factors, repeat=left_arity):
        left = free_reduce("".join(parts))
        n_left += 1
        for tgt in primary_set:
            need = free_reduce(inv(left) + tgt)
            if need in right:
                n_primary_hits += 1
                if hit is None:
                    hit = {"left": left, "need": need, "target": tgt}
        for tgt in extra_set:
            need = free_reduce(inv(left) + tgt)
            if need in right:
                n_extra_hits += 1
                if extra_hit is None:
                    extra_hit = {"left": left, "need": need, "target": tgt}
    n_factors = len(factors)
    return {
        "n_factors": n_factors,
        "left_arity": left_arity,
        "right_arity": right_arity,
        "n_left_tuples": n_left,
        "n_right_tuples": n_right,
        "n_right_unique": len(right),
        "n_k_tuples": n_factors ** (left_arity + right_arity) if n_factors else 0,
        "n_target_hits": n_primary_hits,
        "hit": hit,
        "found": hit is not None,
        "rotation_n_target_hits": n_extra_hits,
        "rotation_hit": extra_hit,
        "rotation_found": extra_hit is not None,
    }


def gate1_five_factor(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    factors = donor_factors([r, s], G1_ALPHABET)
    primary = [XI, inv(XI)]
    extra = []
    seen = set(primary)
    for word in primary:
        for rot in rotations(word):
            if rot not in seen:
                seen.add(rot)
                extra.append(rot)
    rec = mitm_product(factors, primary, 2, 3, extra_targets=extra)
    return {
        "n": n,
        "delta": delta,
        "xi": XI,
        "xi_len": len(XI),
        "n_conjugators": len(c22.short_conjugators([r, s], G1_ALPHABET, 1)),
        **rec,
    }


def gate2_parity_row(n: int, delta: int) -> dict:
    rec = c22.gate2_abelian(n, delta)
    l1 = l1_combo(rec["combo"])
    e_len = len(free_reduce(rec["e"]))
    a_len = len(cyc_reduce(rec["Ahat"]))
    b_len = len(cyc_reduce(rec["Bhat"]))
    if delta == 1:
        expected_l1 = 2 * n + 2
        expected_a, expected_b = n + 2, n
    else:
        expected_a, expected_b = n - 2, n - 4
        expected_l1 = abs(expected_a) + abs(expected_b)
    combo_ok = rec["combo"].get("a") == expected_a and rec["combo"].get("b") == expected_b
    return {
        "n": n,
        "delta": delta,
        "combo": rec["combo"],
        "L1": l1,
        "expected_L1": expected_l1,
        "expected_combo": {"a": expected_a, "b": expected_b},
        "combo_matches_closed_form": combo_ok and l1 == expected_l1,
        "e": rec["e"],
        "e_len": e_len,
        "A_cyc_len": a_len,
        "B_cyc_len": b_len,
        "odd_k_forbidden": l1 is not None and l1 % 2 == 0,
        "even_k_forbidden": l1 is not None and l1 % 2 == 1,
        "k4_abelian_legal": l1 is not None and l1 <= 4 and l1 % 2 == 0,
        "min_k": l1,
    }


def gate2_four_factor(n: int, delta: int) -> dict:
    a_hat, b_hat = tw.s_pair(n, delta, tag="u")
    p, c = 2, n * delta
    e = free_reduce(tw.pw("u", p) + tw.pw("x", c))
    factors = donor_factors([a_hat, b_hat], G2_ALPHABET)
    rec = mitm_product(factors, [e, inv(e)], 2, 2)
    return {
        "n": n,
        "delta": delta,
        "e": e,
        "e_len": len(e),
        "n_conjugators": len(c22.short_conjugators([a_hat, b_hat], G2_ALPHABET, 1)),
        **rec,
    }


def stored_small_k_search() -> list[dict]:
    from c16_escape_scan import STORED_HITS, endpoint_from_params

    splits = {1: None, 2: (1, 1), 3: (1, 2), 4: (2, 2), 5: (2, 3)}
    out = []
    for name, a_u, b_u, p, b, c in STORED_HITS:
        a_hat, b_hat = endpoint_from_params(a_u, b_u, p, b, c)
        e = free_reduce(tw.pw("u", p) + tw.pw("x", c))
        gens = "xu"
        ea, eb, ee = c22.exp_on(a_hat, gens), c22.exp_on(b_hat, gens), c22.exp_on(e, gens)
        sol = c22.solve_2x2(ea[0], eb[0], ea[1], eb[1], ee[0], ee[1])
        l1 = l1_combo(sol)
        rec = {
            "id": name,
            "L1": l1,
            "e": e,
            "e_len": len(e),
            "combo": sol,
            "searched": False,
            "k": None,
            "found": False,
            "hit": None,
        }
        if l1 is None:
            out.append(rec)
            continue
        if l1 % 2 == 0 and l1 <= 4:
            k = 4
        elif l1 % 2 == 1 and l1 <= 5:
            k = l1
        else:
            out.append(rec)
            continue
        factors = donor_factors([a_hat, b_hat], G2_ALPHABET)
        if k == 1:
            hit = next((w for w in factors if w in (e, inv(e))), None)
            rec.update(
                {
                    "searched": True,
                    "k": 1,
                    "n_factors": len(factors),
                    "n_k_tuples": len(factors),
                    "found": hit is not None,
                    "hit": {"target": hit} if hit else None,
                }
            )
        else:
            left_arity, right_arity = splits[k]
            search = mitm_product(factors, [e, inv(e)], left_arity, right_arity)
            rec.update(
                {
                    "searched": True,
                    "k": k,
                    "n_factors": search["n_factors"],
                    "n_k_tuples": search["n_k_tuples"],
                    "found": search["found"],
                    "hit": search["hit"],
                }
            )
        out.append(rec)
    return out


def stored_gate2_parity() -> list[dict]:
    rows = []
    for rec in c22.stored_gate2_abelian():
        l1 = l1_combo(rec["combo"])
        rows.append(
            {
                "id": rec["id"],
                "p": rec["p"],
                "c": rec["c"],
                "combo": rec["combo"],
                "L1": l1,
                "e": rec["e"],
                "e_len": len(rec["e"]),
                "odd_k_forbidden": l1 is not None and l1 % 2 == 0,
                "even_k_forbidden": l1 is not None and l1 % 2 == 1,
                "min_k": l1,
            }
        )
    return rows


def infinite_family_check(n_max: int = 20) -> dict:
    g1_ok = True
    g2_even = True
    r_by_delta = {}
    rows = []
    for delta in (-1, 1):
        for n in range(2, n_max + 1):
            g1 = gate1_hypotheses(n, delta)
            g2 = gate2_parity_row(n, delta)
            if delta not in r_by_delta:
                r_by_delta[delta] = g1["R"]
            ok = all(
                [
                    g1["R_independent_of_n"],
                    g1["R_exp_is_delta_0"],
                    g1["S_y_exp_is_minus_1"],
                    g1["xi_exp_is_1_0"],
                    g1["unimodular"],
                    g1["combo_is_delta_0"],
                    g1["L1"] == 1,
                    g1["R"] == r_by_delta[delta],
                    g2["L1"] is not None and g2["L1"] % 2 == 0,
                    g2["odd_k_forbidden"],
                    g2["combo_matches_closed_form"],
                ]
            )
            g1_ok = g1_ok and ok
            g2_even = g2_even and bool(g2["odd_k_forbidden"])
            if n <= 7:
                rows.append(
                    {
                        "n": n,
                        "delta": delta,
                        "g1_L1": g1["L1"],
                        "g2_L1": g2["L1"],
                        "g2_combo_a": g2["combo"]["a"],
                        "g2_combo_b": g2["combo"]["b"],
                        "ok": ok,
                    }
                )
    return {
        "n_max": n_max,
        "gate1_hypotheses_hold": g1_ok,
        "gate2_L1_always_even": g2_even,
        "rows_n_le_7": rows,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    family = infinite_family_check(20)
    ktable = abelian_k_table(6)
    five = [gate1_five_factor(n, d) for d in (-1, 1) for n in range(2, 8)]
    g2_parity = [gate2_parity_row(n, d) for d in (-1, 1) for n in range(2, 8)]
    g2_four = [
        gate2_four_factor(row["n"], row["delta"])
        for row in g2_parity
        if row["k4_abelian_legal"]
    ]
    stored = stored_gate2_parity()
    stored_search = stored_small_k_search()
    summary = {
        "gate1_hypotheses_n_le_20": family["gate1_hypotheses_hold"],
        "gate2_L1_always_even_n_le_20": family["gate2_L1_always_even"],
        "even_k_all_zero": ktable["even_k_all_zero"],
        "uniform_gate1_counts": ktable["uniform_gate1_counts"],
        "k5_always_100": ktable["k5_always_100"],
        "five_factor_any_hit": any(row["found"] for row in five),
        "five_factor_rotation_any_hit": any(row["rotation_found"] for row in five),
        "five_factor_n_checked": len(five),
        "five_factor_n_k_tuples": sum(row["n_k_tuples"] for row in five),
        "gate2_odd_k_all_forbidden": all(row["odd_k_forbidden"] for row in g2_parity),
        "gate2_four_n_checked": len(g2_four),
        "gate2_four_any_hit": any(row["found"] for row in g2_four),
        "stored_n": len(stored),
        "stored_small_k_n_searched": sum(1 for row in stored_search if row["searched"]),
        "stored_small_k_any_hit": any(row["found"] for row in stored_search),
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "family": family,
        "abelian_k": ktable,
        "gate1_five_factor": five,
        "gate2_parity": g2_parity,
        "gate2_four_factor": g2_four,
        "stored_gate2_parity": stored,
        "stored_small_k": stored_search,
        "notes": [
            "Even k is an abelian obstruction for Gate 1, independent of conjugators.",
            "Five-factor conjugators are prefix/one-letter, same set as C22.3/C23.2.",
            "Meet-in-the-middle split is 2+3, covering every 5-tuple of that factor pool.",
            "Rotation targets are recorded separately; they are not extra factors in the pool.",
            "Gate 2 odd k is abelian-impossible on every Q'_{n,δ} with n=2..20.",
            "Four-factor Gate 2 is searched only where L1 ≤ 4 (δ=−1, n=2..5).",
            "Stored C16 endpoints: k=4 on L1≤4 even, k=L1 on odd L1≤5; L1>5 unsearched.",
            "No U124 row is solved.",
        ],
    }
    path = OUT / "c24_even_k.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c24 even-k / five-factor")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
