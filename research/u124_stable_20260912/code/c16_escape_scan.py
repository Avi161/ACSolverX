"""Bounded structural probes of C16 escape endpoints.

Covers the δ=−1 Q' corridor endpoint and the five stored best-table C16
hits. Depth-1 ordinary AC2 only, plus free-group factorizations and a
swapped-letter Magnus scan. Not a U124 solve.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    cyc_reduce,
    exp_sums,
    free_reduce,
    inv,
    rot,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children, flags  # noqa: E402
from u124_census import bs_mm1_shape, syllables  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

# Best-table C16 hits, parameters from the independent replay.
STORED_HITS = (
    ("aca_16", "Uxx", "x", -3, -1, 2),
    ("aca_43", "uXuX", "", -2, -1, 2),
    ("aca_67", "UxUx", "", -3, -1, -3),
    ("aca_87", "UxUx", "", -3, 1, -3),
    ("aca_90", "UxUx", "", -3, -1, 3),
)


def endpoint_from_params(a_u: str, b_u: str, p: int, b: int, c: int) -> tuple[str, str]:
    a_hat = free_reduce(a_u + tw.pw("u", p) + tw.pw("x", b) + tw.pw("u", -p) + b_u)
    b_hat = free_reduce("U" + tw.pw("x", -c) + tw.pw("u", -p) + "x" + tw.pw("u", p) + tw.pw("x", c))
    return a_hat, b_hat


def bs_mn_shape(word: str) -> dict | None:
    """HNN/BS donor x^{±1} u^M x^{∓1} u^{±N} up to rotation/inversion, any M,N≠0."""
    reduced = cyc_reduce(word)
    if not reduced:
        return None
    for spelling in (reduced, inv(reduced)):
        for offset in range(len(spelling)):
            runs = syllables(spelling[offset:] + spelling[:offset])
            if len(runs) != 4:
                continue
            (g0, e0), (g1, e1), (g2, e2), (g3, e3) = runs
            if g0 == g2 and g1 == g3 and g0 != g1 and abs(e0) == 1 and abs(e2) == 1 and e0 == -e2:
                if e1 * e3 < 0:
                    return {
                        "stable": g0,
                        "M": abs(e1),
                        "N": abs(e3),
                        "consecutive": abs(abs(e1) - abs(e3)) == 1,
                    }
    return None


def magnus_as(word: str, height_letter: str, content_letter: str) -> tuple[list[tuple[int, int]], int]:
    renamed = tw.subst(word, {height_letter: "y", content_letter: "x"})
    return tw.magnus(renamed)


def pair_c16_shape(r1: str, r2: str, height: str, content: str) -> dict:
    info = {"height": height, "content": content, "H2": False, "H3": False, "fires": False}
    for spelling in tw.rotations_and_inverses(r1) + tw.rotations_and_inverses(r2):
        blocks, h = magnus_as(spelling, height, content)
        if tw.h2_isolator(blocks, h):
            info["H2"] = True
        if tw.h3_companion(blocks, h):
            info["H3"] = True
    info["fires"] = info["H2"] and info["H3"]
    return info


def britton_pinch(word: str, stable: str = "u") -> bool:
    """True if some orientation has a pinch u^{±1} x^k u^{∓1} with |u|=1."""
    reduced = cyc_reduce(word)
    for spelling in (reduced, inv(reduced)):
        for offset in range(len(spelling) or 1):
            runs = syllables(spelling[offset:] + spelling[:offset] if spelling else "")
            for i in range(len(runs) - 2):
                (g0, e0), (g1, e1), (g2, e2) = runs[i : i + 3]
                if (
                    g0 == g2 == stable
                    and g1 != stable
                    and abs(e0) == 1
                    and abs(e2) == 1
                    and e0 == -e2
                ):
                    return True
    return False


def split_stable_pinches(word: str, stable: str = "u") -> list[dict]:
    """Opposite-sign stable letters with only x-letters between, including
    pinches obtained by splitting a longer stable run."""
    reduced = cyc_reduce(word)
    n = len(reduced)
    doubled = reduced + reduced
    out = []
    seen = set()
    for i in range(n):
        left = doubled[i]
        if left.lower() != stable:
            continue
        xexp = 0
        only_x = True
        for step in range(1, n):
            right = doubled[i + step]
            if right.lower() == stable:
                if only_x and right == left.swapcase():
                    key = (i, xexp, left, right)
                    if key not in seen:
                        seen.add(key)
                        out.append({"k": xexp, "left": left, "right": right})
                break
            if right.lower() == "x":
                xexp += 1 if right == "x" else -1
            else:
                only_x = False
                break
    return out


def associated_bs_pinch(k: int, left: str, right: str, n: int) -> bool:
    """u^{-1} x^{q n} u or u x^{q(n+1)} u^{-1} for integer q ≠ 0."""
    if n < 1:
        return False
    if left == "U" and right == "u":
        return k != 0 and k % n == 0
    if left == "u" and right == "U":
        return k != 0 and k % (n + 1) == 0
    return False


def c19_identity(n: int) -> dict:
    """Elementary AC2 on S_{n,-1}: companion becomes consecutive BS(n,n+1)."""
    donor, companion = tw.s_pair(n, -1)
    piece = cyc_reduce(rot(companion, n) + rot(donor, 2))
    claimed = tw.pw("x", -n) + "U" + tw.pw("x", n) + "uX"
    claimed = free_reduce(claimed)
    bs, m = bs_mm1_shape(piece)
    rotated_bs = cyc_reduce("U" + tw.pw("x", n) + "u" + tw.pw("x", -(n + 1)))
    return {
        "n": n,
        "donor": donor,
        "companion": companion,
        "product": piece,
        "equals_claimed": piece == claimed,
        "claimed": claimed,
        "bs_mm1": bs,
        "bs_m": m,
        "cyclically_bs_n_n1": tw.same_cyclic(piece, rotated_bs),
        "in_len": len(cyc_reduce(donor)) + len(cyc_reduce(companion)),
        "out_len": len(cyc_reduce(donor)) + len(cyc_reduce(piece)),
        "drop": (len(cyc_reduce(donor)) + len(cyc_reduce(companion)))
        - (len(cyc_reduce(donor)) + len(cyc_reduce(piece))),
        "donor_u_exp": tw.exp_sums(tw.subst(donor, {"u": "y"}))[1],
        "donor_maximal_run_pinch": britton_pinch(donor, "u"),
        "product_maximal_run_pinch": britton_pinch(piece, "u"),
        "donor_split_pinches": split_stable_pinches(donor, "u"),
        "donor_valid_bs_pinch": any(
            associated_bs_pinch(p["k"], p["left"], p["right"], n)
            for p in split_stable_pinches(donor, "u")
        ),
    }


def factorization_identities() -> dict:
    d = tw.s_pair(2, -1)[0]
    inner = free_reduce("Xuuux")  # x^{-1} u^3 x
    xinv2 = free_reduce("XXUU")  # x^{-2} u^{-2}
    conjugate = free_reduce("xuuuX")  # x u^3 x^{-1}
    return {
        "D": d,
        "equals_inner_xinv2": d == free_reduce(inner + xinv2),
        "equals_xinv2_conjugate": d == free_reduce("XX" + conjugate + "UU"),
        "inner_conjugate": inner,
        "xinv2_upow": xinv2,
        "missing_bs32_inner": conjugate != "uu",
    }


def one_occ(word: str, gens: str = "xu") -> bool:
    reduced = cyc_reduce(word)
    for spelling in (reduced, inv(reduced)):
        for offset in range(len(spelling) or 1):
            rotated = spelling[offset:] + spelling[:offset] if spelling else ""
            for gen in gens:
                if rotated.lower().count(gen) == 1:
                    return True
    return False


def pair_flags(r1: str, r2: str) -> dict:
    feat = flags(r1, r2)
    feat["one_occurrence"] = one_occ(r1) or one_occ(r2)
    return feat


def interesting_child(
    base: dict, feat: dict, pair: tuple[str, str], p_relabel: tuple[str, str] | None
) -> dict | None:
    dropped = feat["length"] < base["length"]
    new_one = feat["one_occurrence"] and not base["one_occurrence"]
    new_two = feat["two_block_both"] and not base["two_block_both"]
    new_bs = feat["bs_mm1_either"] and not base["bs_mm1_either"]
    bs_mn = bs_mn_shape(pair[0]) or bs_mn_shape(pair[1])
    matches_p = False
    if p_relabel is not None:
        matches_p = canon_pair(*pair) == canon_pair(*p_relabel)
    swapped = pair_c16_shape(pair[0], pair[1], "u", "x")
    if not (dropped or new_one or new_two or new_bs or matches_p or swapped["fires"]):
        return None
    return {
        "length_drop": dropped,
        "new_one_occurrence": new_one,
        "new_two_block_both": new_two,
        "new_bs_mm1": new_bs,
        "bs_mn": bs_mn,
        "matches_relabeled_P": matches_p,
        "swapped_c16_fires": swapped["fires"],
        "new_r1": pair[0],
        "new_r2": pair[1],
        "new_length": feat["length"],
    }


def scan_pair(tag: str, r1: str, r2: str, n: int | None, delta: int | None) -> dict:
    base_flags = pair_flags(r1, r2)
    p_relabel = None
    if n is not None and delta == 1:
        p_relabel = (
            tw.subst(tw.p_pair(n, 1)[0], {"x": "u", "y": "x"}),
            tw.subst(tw.p_pair(n, 1)[1], {"x": "u", "y": "x"}),
        )
    hits = []
    n_children = 0
    seen = set()
    for a, b, move in children(r1, r2):
        n_children += 1
        key = canon_pair(a, b)
        if key in seen:
            continue
        seen.add(key)
        feat = pair_flags(a, b)
        rec = interesting_child(base_flags, feat, (a, b), p_relabel)
        if rec is not None:
            rec["move"] = move
            hits.append(rec)
    return {
        "tag": tag,
        "pair": [r1, r2],
        "n": n,
        "delta": delta,
        "cyc_total": len(cyc_reduce(r1)) + len(cyc_reduce(r2)),
        "row1_x_exp": exp_sums(r1)[0],
        "row1_bs_mn": bs_mn_shape(r1),
        "row1_bs_mm1": bs_mm1_shape(r1)[0],
        "swapped_magnus_ux": pair_c16_shape(r1, r2, "u", "x"),
        "native_magnus_yx": pair_c16_shape(r1, r2, "y", "x"),
        "n_children_raw": n_children,
        "n_unique_children": len(seen),
        "n_interesting": len(hits),
        "interesting": hits[:12],
        "base_one_occurrence": base_flags["one_occurrence"],
        "base_two_block_both": base_flags["two_block_both"],
        "base_bs_mm1": base_flags["bs_mm1_either"],
    }


def tag_family_depth1(n: int, delta: int) -> dict:
    """Depth-1 AC2 with the MS relator held as a donor, other row the tag."""
    ms, p_comp = tw.p_pair(n, delta)
    s_y = tw.s_pair(n, delta, tag="y")
    # Aut-canonical second row claimed in C16: y^{-n} x^{-2} y^{-1} x^2 y^n x^δ
    s_comp = free_reduce(tw.pw("y", -n) + "XXYxx" + tw.pw("y", n) + tw.pw("x", delta))
    # Multiply the tag row by rotations of the MS relator (and inverse).
    reached_p = False
    reached_s = False
    n_moves = 0
    for donor in (ms, inv(ms)):
        for k in range(len(donor)):
            n_moves += 1
            prod_p = cyc_reduce(p_comp + rot(donor, k))
            prod_s = cyc_reduce(s_comp + rot(donor, k))
            if tw.same_cyclic(prod_p, s_comp) or tw.same_cyclic(prod_s, p_comp):
                if tw.same_cyclic(prod_p, s_comp):
                    reached_s = True
                if tw.same_cyclic(prod_s, p_comp):
                    reached_p = True
    return {
        "n": n,
        "delta": delta,
        "ms": ms,
        "P_companion": p_comp,
        "claimed_S_companion": s_comp,
        "raw_S_pair": list(s_y),
        "n_donor_rotations": n_moves,
        "P_tag_to_S_tag_depth1": reached_s,
        "S_tag_to_P_tag_depth1": reached_p,
        "same_cyclic_already": tw.same_cyclic(p_comp, s_comp),
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    factors = factorization_identities()
    c19 = [c19_identity(n) for n in range(2, 8)]
    s_scans = []
    for delta in (-1, 1):
        for n in range(2, 8):
            r1, r2 = tw.s_pair(n, delta)
            s_scans.append(scan_pair(f"S_{n}_{delta:+d}", r1, r2, n, delta))
    stored = []
    for name, a_u, b_u, p, b, c in STORED_HITS:
        r1, r2 = endpoint_from_params(a_u, b_u, p, b, c)
        rec = scan_pair(name, r1, r2, None, None)
        rec["params"] = {"A_u": a_u, "B_u": b_u, "p": p, "b": b, "c": c}
        stored.append(rec)
    tags = [tag_family_depth1(n, d) for d in (-1, 1) for n in range(2, 8)]
    plus = [r for r in s_scans if r["delta"] == 1]
    minus = [r for r in s_scans if r["delta"] == -1]
    summary = {
        "factorizations_hold": factors["equals_inner_xinv2"] and factors["equals_xinv2_conjugate"],
        "c19_all_equal": all(r["equals_claimed"] and r["cyclically_bs_n_n1"] and r["drop"] == 3 for r in c19),
        "c19_bs_m": [r["bs_m"] for r in c19],
        "c19_donor_u_exp": sorted({r["donor_u_exp"] for r in c19}),
        "c19_maximal_run_pinch_on_D": any(r["donor_maximal_run_pinch"] for r in c19),
        "c19_split_pinch_exponents_on_D": sorted(
            {p["k"] for r in c19 for p in r["donor_split_pinches"]}
        ),
        "c19_valid_bs_pinch_on_D": any(r["donor_valid_bs_pinch"] for r in c19),
        "S_minus_row1_x_exp": sorted({r["row1_x_exp"] for r in minus}),
        "S_plus_row1_bs_mn": all(r["row1_bs_mn"] is not None for r in plus),
        "S_minus_row1_not_bs": all(r["row1_bs_mn"] is None for r in minus),
        "S_swapped_c16_fires": any(r["swapped_magnus_ux"]["fires"] for r in s_scans),
        "S_interesting_total": sum(r["n_interesting"] for r in s_scans),
        "S_minus_interesting": sum(r["n_interesting"] for r in minus),
        "S_plus_interesting": sum(r["n_interesting"] for r in plus),
        "S_plus_matches_P": any(
            any(h["matches_relabeled_P"] for h in r["interesting"]) for r in plus
        ),
        "stored_row1_x_exps": {r["tag"]: r["row1_x_exp"] for r in stored},
        "stored_bs_mn": {r["tag"]: r["row1_bs_mn"] for r in stored},
        "stored_swapped_c16": {r["tag"]: r["swapped_magnus_ux"]["fires"] for r in stored},
        "stored_interesting_total": sum(r["n_interesting"] for r in stored),
        "tag_family_P_to_S": any(t["P_tag_to_S_tag_depth1"] for t in tags),
        "tag_family_S_to_P": any(t["S_tag_to_P_tag_depth1"] for t in tags),
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "factorizations": factors,
        "c19": c19,
        "S_scans": s_scans,
        "stored_hits": stored,
        "tag_family": tags,
        "notes": [
            "Depth-1 AC2 only; a miss is not an obstruction.",
            "Swapped Magnus treats u as the conjugating letter.",
            "Tag-family check holds the MS relator fixed and multiplies the tag.",
            "No U124 row is solved.",
        ],
    }
    path = OUT / "c16_escape_scan.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c16 escape scan")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
