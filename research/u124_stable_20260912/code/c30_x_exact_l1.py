#!/usr/bin/env python3
"""C30: exact-L1 typed products for defining word x on the YXXyxYx family.

C29 left defining word x: against (D, C) the unique combination always has
|b|=1, so exact-L1 products are |a| conjugates of D^{sign(a)} and one
conjugate of C^{sign(b)}, in some order. L1 ranges from 2 (aca_120) to 7
(aca_36). Even k is abelian-legal on even-L1 rows; there is no C24-style
even-k block.

Prefix/one-letter conjugators, unique conjugates per signed type. Counts
are typed Cartesian sizes k|A|^{k-1}|B|, not |F|^k. Cartesian enumeration
only when that size is ≤ 500,000; otherwise existence MITM on unique
freely reduced folds (same code as C26). A hit is a normal-closure
candidate, not a C12 primitive.

Targets are the exponent-(1,0) one-letter class {x, Yxy, yxY}. The inverse
class {X, YXy, yXY} follows by reversing and inverting factors.

Not a heap search. Not a U124 solve unless a witness is found and given an
explicit AC1–AC5 path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    cyc_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c22_gate_witness as c22  # noqa: E402
import c23_three_factor as c23  # noqa: E402
import c26_y_exact_l1 as c26  # noqa: E402
import c29_yxx_family as c29  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
JSON_PATH = OUT / "c30_x_exact_l1.json"
ALPHABET = "xXyY"
POSITIVE_X = ("x", "Yxy", "yxY")
CARTESIAN_MAX_TUPLES = c26.CARTESIAN_MAX_TUPLES


def x_class_exponents() -> dict:
    rows = {word: list(c22.exp_on(word, "xy")) for word in POSITIVE_X}
    return {
        "positive": rows,
        "all_exp_one_zero": all(tuple(exp) == (1, 0) for exp in rows.values()),
        "inverse_class": ["X", "YXy", "yXY"],
        "inverse_all_exp_minus_one_zero": all(
            c22.exp_on(word, "xy") == (-1, 0) for word in ("X", "YXy", "yXY")
        ),
        "Yxy_is_C22_xi": POSITIVE_X[1] == "Yxy",
    }


def scan_row(name: str, companion: str, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_X)
    donor = c29.DONOR
    ab = c29.abelian_row(name, companion)
    combo = ab["x_combo"]
    a, b = combo["a"], combo["b"]
    if abs(b) != 1:
        raise ValueError(f"{name}: x combination must have |b|=1, got {combo}")
    conjugators = c22.short_conjugators([donor, companion], ALPHABET, 1)
    a_word = donor if a >= 0 else inv(donor)
    b_word = companion if b >= 0 else inv(companion)
    a_factors = c23.unique_conjugates(a_word, conjugators)
    b_factors = c23.unique_conjugates(b_word, conjugators)
    m = abs(a)
    k = m + abs(b)
    n_typed = k * (len(a_factors) ** m) * len(b_factors) if k else 0
    if n_typed <= CARTESIAN_MAX_TUPLES:
        rec = c26.cartesian_m_plus_one(a_factors, b_factors, m, targets)
    else:
        rec = c26.mitm_m_plus_one(a_factors, b_factors, m, targets)
    rec.update(
        {
            "id": name,
            "companion": companion,
            "combo_a": a,
            "combo_b": b,
            "L1": ab["x_L1"],
            "k": k,
            "m_D": m,
            "n_conjugators": len(conjugators),
            "n_A": len(a_factors),
            "n_B": len(b_factors),
            "n_typed_tuples": n_typed,
            "n_products_equals_typed": (
                rec["n_products"] == n_typed if rec["n_products"] is not None else None
            ),
            "counts_are_typed_cartesian": True,
            "not_F_to_the_k": True,
            "D_cyc_len": len(cyc_reduce(donor)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "is_p_floor_companion": name in c29.P_FLOOR_IDS,
            "targets": sorted(targets),
            "negative_targets_via_inversion": True,
        }
    )
    return rec


def inversion_closure() -> dict:
    return {
        "map": "(f1,...,fk) -> (fk^{-1}, ..., f1^{-1})",
        "enumerated_class": "(1,0); checks x, Yxy, yxY; inverse class follows",
        "negative_targets_hit_iff_positive_inverse_factors": True,
        "xi_is_in_positive_class": True,
    }


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("cartesian_min_lens") or []
    observed = summary.get("cartesian_observed_min_len")
    return [
        "Exact L1 for x on the YXXyxYx family is |a| copies of D^{sign(a)} and one C^{sign(b)}.",
        "Every row has |b|=1. L1 ranges from 2 to 7. No even-k abelian block.",
        (
            f"All-row typed size {summary['n_typed_tuples_total']} is "
            "k|A|^{k-1}|B| summed over eleven rows, not |F|^k."
        ),
        (
            f"Cartesian cells enumerate {summary['n_cartesian_products_enumerated']} "
            f"products (observed min lengths {mins}, all ≥{observed})."
        ),
        (
            f"MITM cells have typed search-space size {summary['n_typed_tuples_mitm']} "
            "and do not enumerate that many products."
        ),
        "A hit would be a normal-closure candidate, not a C12 primitive. Five companions are C7 Aut-minimal P floors; that is not a solve.",
        "JSON is same-code deterministic replay plus C26 planted controls. No U124 row is solved.",
    ]


def summarize(scans: list[dict], controls: dict, xclass: dict) -> dict:
    cart = [row for row in scans if row["method"] == "typed_cartesian"]
    mitm = [row for row in scans if row["method"] == "typed_mitm_unique_folds"]
    cart_mins = [row["min_len"] for row in cart if row["min_len"] is not None]
    return {
        "n_rows": len(scans),
        "all_abs_b_1": all(abs(row["combo_b"]) == 1 for row in scans),
        "all_k_equals_L1": all(row["k"] == row["L1"] for row in scans),
        "L1_values": sorted({row["L1"] for row in scans}),
        "any_hit": any(row["found"] for row in scans),
        "n_typed_tuples_total": sum(row["n_typed_tuples"] for row in scans),
        "n_typed_tuples_cartesian": sum(row["n_typed_tuples"] for row in cart),
        "n_typed_tuples_mitm": sum(row["n_typed_tuples"] for row in mitm),
        "n_cartesian_products_enumerated": sum(row["n_products"] or 0 for row in cart),
        "n_cartesian_cells": len(cart),
        "n_mitm_cells": len(mitm),
        "cartesian_ids": [row["id"] for row in cart],
        "mitm_ids": [row["id"] for row in mitm],
        "cartesian_min_lens": cart_mins,
        "cartesian_observed_min_len": min(cart_mins) if cart_mins else None,
        "cartesian_all_min_len_ge_7": all(m >= 7 for m in cart_mins) if cart_mins else True,
        "cartesian_products_equal_typed": all(
            row["n_products_equals_typed"] for row in cart
        ),
        "n_p_floor_companions": sum(1 for row in scans if row["is_p_floor_companion"]),
        "x_class_all_exp_one_zero": xclass["all_exp_one_zero"],
        "inverse_class_ok": xclass["inverse_all_exp_minus_one_zero"],
        "controls_ok": controls["ok"],
        "counts_are_typed_cartesian": True,
        "mitm_counts_are_search_space_not_enumerated_products": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    c26._FOLD_CACHE.clear()
    best = c29.load_best()
    xclass = x_class_exponents()
    scans = []
    for name in c29.ROW_IDS:
        row = best[name]
        _donor, companion = c29.split_pair(row["r1"], row["r2"])
        rec = scan_row(name, companion)
        scans.append(rec)
        print(
            f"c30 {name} L1={rec['L1']} method={rec['method']} "
            f"typed={rec['n_typed_tuples']} found={rec['found']} "
            f"min_len={rec['min_len']}",
            flush=True,
        )
    controls = c26.planted_controls()
    summary = summarize(scans, controls, xclass)
    report = {
        "summary": summary,
        "x_class": xclass,
        "scans": scans,
        "controls": controls,
        "inversion_closure": inversion_closure(),
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c30 exact-L1 x on YXXyxYx")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    c26._FOLD_CACHE.clear()
    controls = c26.planted_controls()
    xclass = x_class_exponents()
    summary = summarize(report["scans"], controls, xclass)
    report["summary"] = summary
    report["x_class"] = xclass
    report["controls"] = controls
    report["inversion_closure"] = inversion_closure()
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c30 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
