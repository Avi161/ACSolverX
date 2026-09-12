#!/usr/bin/env python3
"""C26: exact-L1 typed conjugate products for defining word y on Q'.

C25.2: the unique combination of y against (R,S) is (a,b)=(n+2δ,-1), so
L1=|n+2δ|+1. Exact-L1 products (t_R=t_S=0) are |a| conjugates of
R^{sign(a)} and one conjugate of S^{-1}, in some order.

This census uses the C22 prefix/one-letter conjugator set, with unique
conjugates per signed type. Counts are typed Cartesian sizes, not |F|^k.
A hit would be a normal-closure candidate, not a C12 primitive.

Window: every Q'_{n,δ} with n=2..7 and 2≤L1≤7. L1=1 is C25.2's exceptional
length block. L1≥8 (δ=+1, n≥5) is not searched.

Not a heap search. Not a U124 solve unless a witness is found and given an
explicit AC1–AC5 path.
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
import c25_alt_words as c25  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

ALPHABET = "xXyY"
POSITIVE_Y = ("y", "Xyx", "xyX")
MATERIALIZE_MAX_ARITY = 3
MATERIALIZE_MAX_TUPLES = 1_000_000
CARTESIAN_MAX_TUPLES = 500_000

_FOLD_CACHE: dict[tuple[tuple[str, ...], int], set[str]] = {}


def y_combo(n: int, delta: int) -> tuple[int, int, int]:
    a = n + 2 * delta
    b = -1
    return a, b, abs(a) + abs(b)


def window(max_n: int = 7, max_l1: int = 7) -> list[tuple[int, int, int]]:
    rows = []
    for delta in (-1, 1):
        for n in range(2, max_n + 1):
            l1 = c25.y_l1_closed(n, delta)
            if 2 <= l1 <= max_l1:
                rows.append((n, delta, l1))
    return rows


def fold_set(factors: tuple[str, ...], arity: int) -> set[str]:
    if arity < 0:
        raise ValueError("arity")
    if arity == 0:
        return {""}
    if arity > MATERIALIZE_MAX_ARITY:
        raise ValueError(f"refusing to materialize arity {arity}")
    n_tuples = len(factors) ** arity if factors else 0
    if n_tuples > MATERIALIZE_MAX_TUPLES:
        raise ValueError(f"fold too large: {n_tuples}")
    key = (factors, arity)
    cached = _FOLD_CACHE.get(key)
    if cached is not None:
        return cached
    out = {free_reduce("".join(parts)) for parts in product(factors, repeat=arity)}
    _FOLD_CACHE[key] = out
    return out


def is_fold(factors: tuple[str, ...], arity: int, word: str) -> bool:
    """Whether word is a freely reduced product of `arity` factors."""
    if arity < 0:
        raise ValueError("arity")
    if arity <= MATERIALIZE_MAX_ARITY:
        return word in fold_set(factors, arity)
    if arity == 4:
        key = (factors, 4)
        cached = _FOLD_CACHE.get(key)
        if cached is None:
            lefts = fold_set(factors, 2)
            rights = fold_set(factors, 2)
            cached = {free_reduce(a + b) for a in lefts for b in rights}
            _FOLD_CACHE[key] = cached
        return word in cached
    if arity == 5:
        lefts = fold_set(factors, 2)
        rights = fold_set(factors, 3)
        return any(free_reduce(inv(left) + word) in rights for left in lefts)
    if arity == 6:
        lefts = fold_set(factors, 3)
        rights = fold_set(factors, 3)
        return any(free_reduce(inv(left) + word) in rights for left in lefts)
    raise ValueError(f"is_fold arity {arity} not implemented")


def cartesian_m_plus_one(
    a_factors: list[str],
    b_factors: list[str],
    m: int,
    targets: set[str],
) -> dict:
    k = m + 1
    hit = None
    min_len = None
    n_products = 0
    n_len_le_3 = 0
    n_hits = 0
    for pos in range(k):
        lists = [a_factors] * k
        lists[pos] = b_factors
        for parts in product(*lists):
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
                    hit = {"word": word, "pos": pos, "len": length}
    return {
        "method": "typed_cartesian",
        "n_products": n_products,
        "min_len": min_len,
        "n_len_le_3": n_len_le_3,
        "n_hits": n_hits,
        "hit": hit,
        "found": hit is not None,
    }


def contains_mid(
    factors: tuple[str, ...],
    left_arity: int,
    mid: str,
    right_arity: int,
    tgt: str,
) -> bool:
    """Whether tgt freely equals A^{left} * mid * A^{right}."""
    if left_arity == 0 and right_arity == 0:
        return tgt == free_reduce(mid)
    if left_arity == 0:
        return is_fold(factors, right_arity, free_reduce(inv(mid) + tgt))
    if right_arity == 0:
        return is_fold(factors, left_arity, free_reduce(tgt + inv(mid)))
    if left_arity <= 2 and left_arity <= right_arity:
        for left in fold_set(factors, left_arity):
            need = free_reduce(inv(left + mid) + tgt)
            if is_fold(factors, right_arity, need):
                return True
        return False
    if right_arity <= 2:
        for right in fold_set(factors, right_arity):
            need = free_reduce(tgt + inv(mid + right))
            if is_fold(factors, left_arity, need):
                return True
        return False
    for left2 in fold_set(factors, 2):
        need = free_reduce(inv(left2) + tgt)
        if contains_mid(factors, left_arity - 2, mid, right_arity, need):
            return True
    return False


def mitm_m_plus_one(
    a_factors: list[str],
    b_factors: list[str],
    m: int,
    targets: set[str],
) -> dict:
    """Existence MITM: A^L * B * A^R against targets, no large fold iteration."""
    a_t = tuple(a_factors)
    k = m + 1
    hit = None
    n_hits = 0
    for pos in range(k):
        left_arity = pos
        right_arity = m - pos
        for b_word in b_factors:
            for tgt in targets:
                if contains_mid(a_t, left_arity, b_word, right_arity, tgt):
                    n_hits += 1
                    if hit is None:
                        hit = {
                            "target": tgt,
                            "pos": pos,
                            "b": b_word,
                        }
    return {
        "method": "typed_mitm_unique_folds",
        "n_products": None,
        "min_len": None,
        "n_len_le_3": None,
        "n_hits": n_hits,
        "hit": hit,
        "found": hit is not None,
    }


def scan_exact_l1(n: int, delta: int, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_Y)
    a, b, l1 = y_combo(n, delta)
    if abs(b) != 1:
        raise ValueError("y combination must have |b|=1")
    r, s = tw.q_prime(n, delta)
    conjugators = c22.short_conjugators([r, s], ALPHABET, 1)
    r_signed = r if a >= 0 else inv(r)
    s_signed = s if b >= 0 else inv(s)
    a_factors = c23.unique_conjugates(r_signed, conjugators)
    b_factors = c23.unique_conjugates(s_signed, conjugators)
    m = abs(a)
    k = m + abs(b)
    n_typed = k * (len(a_factors) ** m) * len(b_factors) if k else 0
    if n_typed <= CARTESIAN_MAX_TUPLES:
        rec = cartesian_m_plus_one(a_factors, b_factors, m, targets)
    else:
        rec = mitm_m_plus_one(a_factors, b_factors, m, targets)
    rec.update(
        {
            "n": n,
            "delta": delta,
            "combo_a": a,
            "combo_b": b,
            "L1": l1,
            "k": k,
            "m_R": m,
            "n_conjugators": len(conjugators),
            "n_A": len(a_factors),
            "n_B": len(b_factors),
            "n_typed_tuples": n_typed,
            "counts_are_typed_cartesian": True,
            "not_F_to_the_k": True,
            "R_cyc_len": len(cyc_reduce(r)),
            "S_cyc_len": len(cyc_reduce(s)),
            "targets": sorted(targets),
            "negative_targets_via_inversion": True,
        }
    )
    return rec


def planted_controls() -> dict:
    """Same-code positive/negative controls, not the Q' census.

    Branches covered: Cartesian k=2; MITM arity 4 (cached 2+2); arity 5
    (2+3); arity 6 end-slot (3+3); recursive mid-slot L=3,R=3; a
    cancellation-heavy empty 5-fold; Cartesian/MITM agreement on a tiny
    pool. Not a second implementation.
    """
    a_factors = ["x", "xx"]
    b_factors = ["y", "Y"]
    hit = cartesian_m_plus_one(a_factors, b_factors, 1, {"xy"})
    miss = cartesian_m_plus_one(a_factors, b_factors, 1, {"u"})
    mitm4_hit = mitm_m_plus_one(["x"], ["y"], 4, {"xxxxy"})
    mitm4_miss = mitm_m_plus_one(["x"], ["y"], 4, {"u"})
    mitm5_hit = mitm_m_plus_one(["x"], ["y"], 5, {"xxxxxy"})
    mitm5_miss = mitm_m_plus_one(["x"], ["y"], 5, {"u"})
    mitm6_end = mitm_m_plus_one(["x"], ["y"], 6, {"xxxxxxy"})
    mitm6_mid = mitm_m_plus_one(["x"], ["y"], 6, {"xxxyxxx"})
    mitm6_miss = mitm_m_plus_one(["x"], ["y"], 6, {"u"})
    cancel_hit = mitm_m_plus_one(["Xx"], ["y"], 5, {"y"})
    cancel_miss = mitm_m_plus_one(["Xx"], ["y"], 5, {"u"})
    tiny_a, tiny_b = ["x", "xx"], ["y"]
    tiny_targets = {"xxy", "xyx", "yxx"}
    cart_tiny = cartesian_m_plus_one(tiny_a, tiny_b, 2, tiny_targets)
    mitm_tiny = mitm_m_plus_one(tiny_a, tiny_b, 2, tiny_targets)
    agree = cart_tiny["found"] is True and mitm_tiny["found"] is True
    ok = (
        hit["found"]
        and not miss["found"]
        and mitm4_hit["found"]
        and not mitm4_miss["found"]
        and mitm5_hit["found"]
        and not mitm5_miss["found"]
        and mitm6_end["found"]
        and mitm6_mid["found"]
        and not mitm6_miss["found"]
        and cancel_hit["found"]
        and not cancel_miss["found"]
        and agree
    )
    return {
        "cartesian_hit_found": hit["found"],
        "cartesian_miss_found": miss["found"],
        "mitm4_hit_found": mitm4_hit["found"],
        "mitm4_miss_found": mitm4_miss["found"],
        "mitm5_hit_found": mitm5_hit["found"],
        "mitm5_miss_found": mitm5_miss["found"],
        "mitm6_end_hit_found": mitm6_end["found"],
        "mitm6_mid_hit_found": mitm6_mid["found"],
        "mitm6_miss_found": mitm6_miss["found"],
        "cancel_empty_fold_hit_found": cancel_hit["found"],
        "cancel_empty_fold_miss_found": cancel_miss["found"],
        "cartesian_mitm_agree_tiny_m2": agree,
        "branches_exercised": [
            "cartesian_k2",
            "mitm_arity4_2plus2",
            "mitm_arity5_2plus3",
            "mitm_arity6_3plus3_end",
            "mitm_recursive_L3_R3",
            "mitm_cancel_empty_5fold",
            "cartesian_vs_mitm_m2",
        ],
        "ok": ok,
        "independent_checker": False,
        "same_code_as_census": True,
    }


def inversion_closure() -> dict:
    return {
        "map": "(f1,...,fk) -> (fk^{-1}, ..., f1^{-1})",
        "enumerated_class": "(0,1); checks y, Xyx, xyX; Y-class follows",
        "negative_targets_hit_iff_positive_inverse_factors": True,
    }


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("cartesian_min_lens") or []
    observed = summary.get("cartesian_observed_min_len")
    return [
        "Exact L1 for y on Q' is |a| copies of R^{sign(a)} and one S^{-1}.",
        (
            f"All-cell typed size {summary['n_typed_tuples_total']} is "
            "k|A|^{k-1}|B| summed over eight cells, not |F|^k."
        ),
        (
            f"Cartesian cells enumerate {summary['n_cartesian_products_enumerated']} "
            f"products (observed min lengths {mins}, all ≥{observed})."
        ),
        (
            f"MITM cells have typed search-space size {summary['n_typed_tuples_mitm']} "
            "and do not enumerate that many products."
        ),
        "A hit would be a normal-closure candidate, not a C12/C22.6 path.",
        "Window is n=2..7 with 2≤L1≤7. L1=1 is C25.2; L1≥8 is open.",
        "JSON is same-code deterministic replay plus branch-complete planted controls. No U124 row is solved.",
    ]


def summarize(scans: list[dict], controls: dict) -> dict:
    cart = [row for row in scans if row["method"] == "typed_cartesian"]
    mitm = [row for row in scans if row["method"] == "typed_mitm_unique_folds"]
    cart_mins = [row["min_len"] for row in cart if row["min_len"] is not None]
    skipped_l1_ge_8 = [
        {"n": n, "delta": 1, "L1": c25.y_l1_closed(n, 1)}
        for n in range(5, 8)
    ]
    return {
        "n_cells": len(scans),
        "window": [{"n": row["n"], "delta": row["delta"], "L1": row["L1"]} for row in scans],
        "any_hit": any(row["found"] for row in scans),
        "n_typed_tuples_total": sum(row["n_typed_tuples"] for row in scans),
        "n_typed_tuples_cartesian": sum(row["n_typed_tuples"] for row in cart),
        "n_typed_tuples_mitm": sum(row["n_typed_tuples"] for row in mitm),
        "n_cartesian_products_enumerated": sum(row["n_products"] or 0 for row in cart),
        "n_cartesian_cells": len(cart),
        "n_mitm_cells": len(mitm),
        "cartesian_min_lens": cart_mins,
        "cartesian_observed_min_len": min(cart_mins) if cart_mins else None,
        "cartesian_all_min_len_ge_11": all(m >= 11 for m in cart_mins),
        "cartesian_all_min_len_ge_7": all(m >= 7 for m in cart_mins),
        "controls_ok": controls["ok"],
        "skipped_l1_1": {"n": 2, "delta": -1, "L1": 1, "reason": "C25.2 length block |S|=7"},
        "skipped_l1_ge_8": skipped_l1_ge_8,
        "counts_are_typed_cartesian": True,
        "mitm_counts_are_search_space_not_enumerated_products": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    _FOLD_CACHE.clear()
    cells = window()
    scans = []
    for n, delta, l1 in cells:
        rec = scan_exact_l1(n, delta)
        scans.append(rec)
        print(
            f"c26 n={n} delta={delta} L1={l1} method={rec['method']} "
            f"typed={rec['n_typed_tuples']} found={rec['found']}",
            flush=True,
        )
    controls = planted_controls()
    summary = summarize(scans, controls)
    report = {
        "summary": summary,
        "scans": scans,
        "controls": controls,
        "inversion_closure": inversion_closure(),
        "notes": notes_from_summary(summary),
    }
    path = OUT / "c26_y_exact_l1.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c26 exact-L1 y on Q'")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


def annotate_existing() -> dict:
    """Refresh summary, notes, and planted controls without re-running the window."""
    path = OUT / "c26_y_exact_l1.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    _FOLD_CACHE.clear()
    controls = planted_controls()
    summary = summarize(report["scans"], controls)
    report["summary"] = summary
    report["controls"] = controls
    report["inversion_closure"] = inversion_closure()
    report["notes"] = notes_from_summary(summary)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c26 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
