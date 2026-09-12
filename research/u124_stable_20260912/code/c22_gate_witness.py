#!/usr/bin/env python3
"""C22: bounded C0 witnesses for C16 gates, C16-as-C6, and a C15 bridge.

Three exact, restore-preserving questions:

1. Gate 1 with u-free conjugators is the word problem ``ξ ∈ ncl(R,S)`` in
   F(x,y). After AC4 the third relator is the letter u; one restore-preserving
   AC2 against a u-free donor cannot produce D = u⁻¹ξ (length). A bounded
   conjugacy-product search for ξ is the honest Lemma-11 witness.
2. Gate 2 with y-free conjugators is ``e = u^p x^c ∈ ncl(Â, B̂)`` in F(x,u).
3. The C16 isolator template is a Theorem 3.1 corridor with |w|=3, which the
   |w|≤2 census could not see. That classifies C16 as C6; it does not expand
   either C0 use.

Also checks whether any depth-1 ordinary AC2 of a C15 row is the MS pair
P_{m,±1} (a same-length structural hit C13 did not report).

Not a heap search. Not a U124 solve unless a witness is found and replayed.
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    cyc_reduce,
    free_reduce,
    inv,
)
from experiments.stable_ac.rank3_compression.corridors import (  # noqa: E402
    corridor_output,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c15_divisibility_scan as c15  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children  # noqa: E402
from ms_template_identities import parametric_p  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

XI = tw.XI  # Yxy
D_ROW = free_reduce("U" + XI)  # u⁻¹ ξ
MAX_STATES = 800
MAX_FACTORS = 4
MAX_CONJ_LEN = 2


def exp_on(word: str, gens: str) -> tuple[int, ...]:
    counts = []
    for gen in gens:
        counts.append(
            sum(1 if ch == gen else -1 if ch == gen.swapcase() else 0 for ch in word)
        )
    return tuple(counts)


def l1(vec: tuple[int, ...]) -> int:
    return sum(abs(v) for v in vec)


def reduced_conjugators(alphabet: str, max_len: int) -> list[str]:
    out = [""]
    stack = [""]
    letters = list(alphabet)
    for _ in range(max_len):
        nxt = []
        for prefix in stack:
            for letter in letters:
                if prefix and prefix[-1] == letter.swapcase():
                    continue
                word = prefix + letter
                nxt.append(word)
                out.append(word)
        stack = nxt
    return out


def prefixes(word: str) -> list[str]:
    return [word[:i] for i in range(len(word) + 1)]


def donor_list(relators: list[str]) -> list[str]:
    donors = []
    for rel in relators:
        for spelling in (rel, inv(rel)):
            spelling = free_reduce(spelling)
            if spelling and spelling not in donors:
                donors.append(spelling)
    return donors


def short_conjugators(relators: list[str], alphabet: str, max_len: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for word in reduced_conjugators(alphabet, max_len):
        if word not in seen:
            seen.add(word)
            out.append(word)
    for rel in relators:
        for spelling in (rel, inv(rel)):
            for prefix in prefixes(spelling):
                reduced = free_reduce(prefix)
                if reduced not in seen:
                    seen.add(reduced)
                    out.append(reduced)
    return out


def conjugate(word: str, g: str) -> str:
    if not g:
        return free_reduce(word)
    return free_reduce(inv(g) + word + g)


def factor_list(relators: list[str], alphabet: str, max_conj_len: int) -> list[str]:
    donors = donor_list(relators)
    conjugators = short_conjugators(relators, alphabet, max_conj_len)
    seen: set[str] = set()
    out: list[str] = []
    for donor in donors:
        for g in conjugators:
            factor = conjugate(donor, g)
            if factor and factor not in seen:
                seen.add(factor)
                out.append(factor)
    return out


def search_ncl(
    relators: list[str],
    target: str,
    alphabet: str,
    *,
    exhaustive_factors: int = 2,
    exhaustive_conj_len: int = 1,
    extra_factors: int = MAX_FACTORS,
    extra_conj_len: int = MAX_CONJ_LEN,
    extra_states: int = MAX_STATES,
    max_len: int = 48,
) -> dict:
    """Restore-preserving conjugacy-product search for ``target``.

    The depth-``exhaustive_factors`` layer with generator/prefix conjugators of
    length ``≤ exhaustive_conj_len`` is fully enumerated. Extra factors use
    best-first expansion capped at ``extra_states`` and are not exhaustive.
    """
    target_free = free_reduce(target)
    target_inv = inv(target_free)
    gens = "".join(dict.fromkeys(ch.lower() for ch in alphabet))
    want_exp = exp_on(target_free, gens)
    factors = factor_list(relators, alphabet, exhaustive_conj_len)
    hit = None
    products: dict[str, int] = {"": 0}
    min_l1 = l1(want_exp)
    min_len_gap0: int | None = None
    enumerated = 0

    def consider(word: str, depth: int) -> bool:
        nonlocal hit, min_l1, min_len_gap0, enumerated
        enumerated += 1
        if word in (target_free, target_inv):
            hit = {"word": word, "factors": depth, "inverted": word == target_inv}
            return True
        gap = l1(tuple(a - b for a, b in zip(exp_on(word, gens), want_exp)))
        if gap < min_l1:
            min_l1 = gap
        if gap == 0 and (min_len_gap0 is None or len(word) < min_len_gap0):
            min_len_gap0 = len(word)
        return False

    layer = [""]
    for depth in range(1, exhaustive_factors + 1):
        nxt_layer = []
        nxt_seen = set()
        for word in layer:
            for factor in factors:
                cand = free_reduce(word + factor)
                if len(cand) > max_len or cand in products:
                    continue
                products[cand] = depth
                if consider(cand, depth):
                    break
                if cand not in nxt_seen:
                    nxt_seen.add(cand)
                    nxt_layer.append(cand)
            if hit is not None:
                break
        if hit is not None:
            break
        layer = nxt_layer

    extra_visited = 0
    extra_unique = 0
    if hit is None and extra_factors > exhaustive_factors:
        extra_factors_list = factor_list(relators, alphabet, extra_conj_len)
        donor_l1 = max((l1(exp_on(f, gens)) for f in extra_factors_list), default=0)
        ranked = sorted(
            products.items(),
            key=lambda item: (
                l1(tuple(a - b for a, b in zip(exp_on(item[0], gens), want_exp))),
                len(item[0]),
                item[1],
            ),
        )
        queue: deque[tuple[str, int]] = deque(ranked)
        seen_extra = set(products)
        while queue and extra_visited < extra_states and hit is None:
            word, depth = queue.popleft()
            extra_visited += 1
            if depth >= extra_factors:
                continue
            remaining = extra_factors - depth
            if l1(tuple(a - b for a, b in zip(exp_on(word, gens), want_exp))) > remaining * donor_l1:
                continue
            for factor in extra_factors_list:
                cand = free_reduce(word + factor)
                if len(cand) > max_len or cand in seen_extra:
                    continue
                seen_extra.add(cand)
                extra_unique += 1
                products[cand] = depth + 1
                if consider(cand, depth + 1):
                    break
                queue.append((cand, depth + 1))
                if extra_unique >= extra_states:
                    queue.clear()
                    break

    return {
        "target": target,
        "target_len": len(target_free),
        "target_exp": list(want_exp),
        "gens": gens,
        "n_exhaustive_factors": len(factors),
        "exhaustive_factor_bound": exhaustive_factors,
        "exhaustive_conj_len": exhaustive_conj_len,
        "enumerated_exhaustive_products": enumerated,
        "n_products": len(products),
        "extra_visited": extra_visited,
        "extra_unique": extra_unique,
        "hit": hit,
        "found": hit is not None,
        "min_l1_to_target": min_l1,
        "min_len_abelian_match": min_len_gap0,
        "exhaustive_layer_complete": True,
    }


def solve_2x2(m00: int, m01: int, m10: int, m11: int, b0: int, b1: int) -> dict:
    det = m00 * m11 - m01 * m10
    rec = {"det": det, "ok": False, "a": None, "b": None}
    if det not in (1, -1):
        rec["reason"] = "not_unimodular"
        return rec
    a = det * (m11 * b0 - m01 * b1)
    b = det * (-m10 * b0 + m00 * b1)
    rec.update({"ok": True, "a": a, "b": b})
    return rec


def gate1_abelian(n: int, delta: int) -> dict:
    r, s = tw.q_prime(n, delta)
    xi = XI
    gens = "xy"
    er, es, exi = exp_on(r, gens), exp_on(s, gens), exp_on(xi, gens)
    sol = solve_2x2(er[0], es[0], er[1], es[1], exi[0], exi[1])
    return {
        "n": n,
        "delta": delta,
        "R": r,
        "S": s,
        "R_len": len(cyc_reduce(r)),
        "S_len": len(cyc_reduce(s)),
        "R_exp": list(er),
        "S_exp": list(es),
        "xi_exp": list(exi),
        "combo": sol,
        "xi_cyclic_of_R": tw.same_cyclic(xi, r),
        "xi_cyclic_of_S": tw.same_cyclic(xi, s),
        "D": D_ROW,
        "D_len": len(cyc_reduce(D_ROW)),
        "depth1_restore_len_R": 1 + len(cyc_reduce(r)),
        "depth1_restore_len_S": 1 + len(cyc_reduce(s)),
    }


def gate1_depth1_impossible(rows: list[dict]) -> bool:
    return all(
        rec["D_len"] != rec["depth1_restore_len_R"]
        and rec["D_len"] != rec["depth1_restore_len_S"]
        for rec in rows
    )


def gate2_abelian(n: int, delta: int) -> dict:
    a_hat, b_hat = tw.s_pair(n, delta, tag="u")
    p, c = 2, n * delta
    e = free_reduce(tw.pw("u", p) + tw.pw("x", c))
    gens = "xu"
    ea, eb, ee = exp_on(a_hat, gens), exp_on(b_hat, gens), exp_on(e, gens)
    sol = solve_2x2(ea[0], eb[0], ea[1], eb[1], ee[0], ee[1])

    def power(word: str, k: int) -> str:
        if k == 0:
            return ""
        if k > 0:
            return free_reduce(word * k)
        return free_reduce(inv(word) * (-k))

    literal = (
        free_reduce(power(a_hat, sol["a"] or 0) + power(b_hat, sol["b"] or 0))
        if sol["ok"]
        else ""
    )
    return {
        "n": n,
        "delta": delta,
        "Ahat": a_hat,
        "Bhat": b_hat,
        "e": e,
        "A_exp": list(ea),
        "B_exp": list(eb),
        "e_exp": list(ee),
        "combo": sol,
        "literal_product": literal,
        "literal_equals_e": literal == e,
        "literal_cyclic_e": tw.same_cyclic(literal, e) if literal else False,
        "I_S": free_reduce(e + "Y"),
    }


def c16_as_c6(n: int, delta: int) -> dict:
    pair = tw.q_prime(n, delta)
    w = XI
    template = "zz" + tw.pw("x", n * delta) + "Y"
    try:
        output = corridor_output(pair, 1, w, template, "y")
        ok = True
        error = None
    except ValueError as exc:
        output = ("", "")
        ok = False
        error = str(exc)
    claimed = tw.s_pair(n, delta, tag="y")
    match = ok and canon_pair(*output) == canon_pair(*claimed)
    return {
        "n": n,
        "delta": delta,
        "template": template,
        "word": w,
        "hypotheses_ok": ok,
        "error": error,
        "output": list(output),
        "claimed_S_tag_y": list(claimed),
        "canon_match_S": match,
        "out_cyc_total": len(cyc_reduce(output[0])) + len(cyc_reduce(output[1])) if ok else None,
        "claimed_cyc_total": len(cyc_reduce(claimed[0])) + len(cyc_reduce(claimed[1])),
    }


def c15_bridge_identities() -> dict:
    donor = c15.DONOR
    conjugator = "Xyx"  # x⁻¹ y x
    p1_plus = parametric_p(3, 1)[0]
    product = free_reduce(donor + conjugator)
    inverse_step = free_reduce(p1_plus + inv(conjugator))
    return {
        "donor": donor,
        "conjugator": conjugator,
        "P1_plus": p1_plus,
        "donor_times_Xyx_equals_P1": product == p1_plus,
        "P1_times_xyX_equals_donor": inverse_step == donor,
        "note": "Xyx is conjugate of y, not an AC donor unless y is already a relator.",
    }


def c15_depth1_to_p() -> dict:
    hits = []
    n_children = 0
    n_unique = 0
    for name, companion, m in c15.ROWS:
        r1, r2 = c15.DONOR, companion
        targets = {
            "P_plus": canon_pair(*parametric_p(m, 1)),
            "P_minus": canon_pair(*parametric_p(m, -1)),
        }
        seen = set()
        row_hits = []
        for a, b, move in children(r1, r2):
            n_children += 1
            key = canon_pair(a, b)
            if key in seen:
                continue
            seen.add(key)
            n_unique += 1
            for label, target in targets.items():
                if key == target:
                    row_hits.append({"target": label, "move": move, "pair": [a, b]})
        hits.append(
            {
                "id": name,
                "m": m,
                "companion": companion,
                "n_unique": len(seen),
                "hits": row_hits,
            }
        )
    return {
        "n_rows": len(c15.ROWS),
        "n_children_raw": n_children,
        "n_unique": n_unique,
        "any_hit": any(row["hits"] for row in hits),
        "rows": hits,
    }


def stored_gate2_abelian() -> list[dict]:
    from c16_escape_scan import STORED_HITS, endpoint_from_params  # local

    rows = []
    gens = "xu"
    for name, a_u, b_u, p, b, c in STORED_HITS:
        a_hat, b_hat = endpoint_from_params(a_u, b_u, p, b, c)
        e = free_reduce(tw.pw("u", p) + tw.pw("x", c))
        ea, eb, ee = exp_on(a_hat, gens), exp_on(b_hat, gens), exp_on(e, gens)
        sol = solve_2x2(ea[0], eb[0], ea[1], eb[1], ee[0], ee[1])
        rows.append(
            {
                "id": name,
                "p": p,
                "c": c,
                "e": e,
                "A_exp": list(ea),
                "B_exp": list(eb),
                "e_exp": list(ee),
                "combo": sol,
            }
        )
    return rows


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    g1_ab = [gate1_abelian(n, d) for d in (-1, 1) for n in range(2, 8)]
    g2_ab = [gate2_abelian(n, d) for d in (-1, 1) for n in range(2, 8)]
    c6 = [c16_as_c6(n, d) for d in (-1, 1) for n in range(2, 8)]
    bridge = c15_bridge_identities()
    c15_p = c15_depth1_to_p()
    stored = stored_gate2_abelian()

    # Bounded witnesses: smallest Q' and the matching Gate 2, plus one stored hit.
    g1_search = []
    for n, delta in ((2, -1), (2, 1), (3, -1), (3, 1)):
        r, s = tw.q_prime(n, delta)
        g1_search.append(
            {
                "n": n,
                "delta": delta,
                **search_ncl([r, s], XI, "xXyY"),
            }
        )
    g2_search = []
    for n, delta in ((2, -1), (2, 1), (3, -1), (3, 1)):
        a_hat, b_hat = tw.s_pair(n, delta, tag="u")
        e = free_reduce(tw.pw("u", 2) + tw.pw("x", n * delta))
        g2_search.append(
            {
                "n": n,
                "delta": delta,
                **search_ncl([a_hat, b_hat], e, "xXuU"),
            }
        )
    stored_search = []
    from c16_escape_scan import STORED_HITS, endpoint_from_params

    for name, a_u, b_u, p, b, c in STORED_HITS[:2]:
        a_hat, b_hat = endpoint_from_params(a_u, b_u, p, b, c)
        e = free_reduce(tw.pw("u", p) + tw.pw("x", c))
        stored_search.append(
            {
                "id": name,
                **search_ncl([a_hat, b_hat], e, "xXuU"),
            }
        )

    summary = {
        "c16_as_c6_hypotheses": all(row["hypotheses_ok"] for row in c6),
        "c16_as_c6_same_as_c16": any(row["canon_match_S"] for row in c6),
        "c16_as_c6_n_checked": len(c6),
        "gate1_S_coeff_always_0": all(row["combo"]["ok"] and row["combo"]["b"] == 0 for row in g1_ab),
        "gate1_R_coeff_equals_delta": all(row["combo"]["ok"] and row["combo"]["a"] == row["delta"] for row in g1_ab),
        "gate1_depth1_restore_impossible": gate1_depth1_impossible(g1_ab),
        "gate1_search_any_hit": any(row["found"] for row in g1_search),
        "gate2_search_any_hit": any(row["found"] for row in g2_search),
        "stored_search_any_hit": any(row["found"] for row in stored_search),
        "gate2_literal_power_equals_e": any(row["literal_equals_e"] for row in g2_ab),
        "c15_bridge_identity": bridge["donor_times_Xyx_equals_P1"] and bridge["P1_times_xyX_equals_donor"],
        "c15_depth1_reaches_P": c15_p["any_hit"],
        "stored_gate2_unimodular": all(row["combo"]["ok"] for row in stored),
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "c16_as_c6": c6,
        "gate1_abelian": g1_ab,
        "gate2_abelian": g2_ab,
        "gate1_search": g1_search,
        "gate2_search": g2_search,
        "stored_gate2_abelian": stored,
        "stored_gate2_search": stored_search,
        "c15_bridge": bridge,
        "c15_depth1_to_P": c15_p,
        "notes": [
            "A missed bounded ncl search is not an obstruction to a longer witness.",
            "C6 hypotheses hold for the C16 isolator template; the output is not C16 because C6 letter-substitutes y in the companion.",
            "C15 donor times x^{-1} y x equals P1_{δ=+1}; that conjugator is not an AC donor.",
            "No U124 row is solved.",
        ],
    }
    path = OUT / "c22_gate_witness.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c22 gate witness")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
