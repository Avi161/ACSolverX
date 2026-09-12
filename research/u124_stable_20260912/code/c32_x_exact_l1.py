#!/usr/bin/env python3
"""C32: exact-L1 typed products for defining word x on the YXXYxxyx family.

C31 left defining word x. Donor D abelianizes to (1,−1). For a unimodular
companion C_ab=(p,q) one has |p+q|=1, and the unique x-combination is
b=p+q, a=(p+q)q. On the eight listed rows that is L1=2 on the seven BS
companions and L1=3 on aca_32 — not a claim about every conceivable
unimodular companion. Exact-L1 products are |a| conjugates of D^{sign(a)}
and one conjugate of C^{sign(b)}. All eight cells are within the Cartesian
cap.

Targets are the exponent-(1,0) one-letter class {x, Yxy, yxY}. A hit is a
normal-closure candidate, not a C12 primitive.

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
import c30_x_exact_l1 as c30  # noqa: E402
import c31_yxxy_family as c31  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
JSON_PATH = OUT / "c32_x_exact_l1.json"
ALPHABET = "xXyY"
POSITIVE_X = c30.POSITIVE_X
CARTESIAN_MAX_TUPLES = c26.CARTESIAN_MAX_TUPLES


def x_combo_from_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique x combo against D_ab=(1,-1) and unimodular C_ab=(p,q)."""
    if abs(p + q) != 1:
        raise ValueError("companion must be unimodular with D=(1,-1)")
    b = p + q
    a = b * q
    return a, b, abs(a) + abs(b)


def scan_row(name: str, companion: str, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_X)
    donor = c31.DONOR
    p, q = c22.exp_on(companion, "xy")
    a, b, l1 = x_combo_from_c_exp(p, q)
    ab = c31.abelian_row(name, companion)
    if ab["x_combo"]["a"] != a or ab["x_combo"]["b"] != b:
        raise ValueError(f"{name}: combo mismatch {ab['x_combo']} vs {(a, b)}")
    conjugators = c22.short_conjugators([donor, companion], ALPHABET, 1)
    a_word = donor if a >= 0 else inv(donor)
    b_word = companion if b >= 0 else inv(companion)
    a_factors = c23.unique_conjugates(a_word, conjugators)
    b_factors = c23.unique_conjugates(b_word, conjugators)
    m = abs(a)
    k = m + abs(b)
    n_typed = k * (len(a_factors) ** m) * len(b_factors) if k else 0
    if n_typed > CARTESIAN_MAX_TUPLES:
        rec = c26.mitm_m_plus_one(a_factors, b_factors, m, targets)
    else:
        rec = c26.cartesian_m_plus_one(a_factors, b_factors, m, targets)
    rec.update(
        {
            "id": name,
            "companion": companion,
            "combo_a": a,
            "combo_b": b,
            "L1": l1,
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
            "companion_bs_mm1": ab["companion_bs_mm1"],
            "targets": sorted(targets),
            "negative_targets_via_inversion": True,
            "equality_is_free_reduce_literal": True,
        }
    )
    return rec


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("cartesian_min_lens") or []
    observed = summary.get("cartesian_observed_min_len")
    return [
        "Exact L1 for x on the YXXYxxyx family is |a| copies of D^{sign(a)} and one C^{sign(b)}.",
        "On the eight listed rows, L1 is 2 (seven BS companions) or 3 (aca_32). |b|=1 from unimodularity with D=(1,-1).",
        (
            f"All-row typed size {summary['n_typed_tuples_total']} is "
            "k|A|^{k-1}|B| summed over eight rows, not |F|^k."
        ),
        (
            f"Cartesian cells enumerate {summary['n_cartesian_products_enumerated']} "
            f"products (observed min lengths {mins}, all ≥{observed})."
        ),
        "A hit would be a normal-closure candidate, not a C12 primitive.",
        "Equality is free-reduce literal match against {x, Yxy, yxY}. JSON is same-code replay. No U124 row is solved.",
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
        "n_bs_l1_2": sum(1 for row in scans if row["companion_bs_mm1"] and row["L1"] == 2),
        "n_aca_32_l1_3": sum(1 for row in scans if row["id"] == "aca_32" and row["L1"] == 3),
        "any_hit": any(row["found"] for row in scans),
        "n_typed_tuples_total": sum(row["n_typed_tuples"] for row in scans),
        "n_typed_tuples_cartesian": sum(row["n_typed_tuples"] for row in cart),
        "n_typed_tuples_mitm": sum(row["n_typed_tuples"] for row in mitm),
        "n_cartesian_products_enumerated": sum(row["n_products"] or 0 for row in cart),
        "n_cartesian_cells": len(cart),
        "n_mitm_cells": len(mitm),
        "cartesian_ids": [row["id"] for row in cart],
        "cartesian_min_lens": cart_mins,
        "cartesian_observed_min_len": min(cart_mins) if cart_mins else None,
        "cartesian_products_equal_typed": all(
            row["n_products_equals_typed"] for row in cart
        ),
        "x_class_all_exp_one_zero": xclass["all_exp_one_zero"],
        "one_letter_class_complete": xclass["one_letter_class_complete"],
        "abs_b_1_from_unimodularity": True,
        "l1_range_is_eight_listed_rows": True,
        "equality_is_free_reduce_literal": True,
        "controls_ok": controls["ok"],
        "counts_are_typed_cartesian": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    c26._FOLD_CACHE.clear()
    best = c31.load_best()
    xclass = c30.x_class_exponents()
    scans = []
    for name in c31.ROW_IDS:
        row = best[name]
        _donor, companion = c31.split_pair(row["r1"], row["r2"])
        rec = scan_row(name, companion)
        scans.append(rec)
        print(
            f"c32 {name} L1={rec['L1']} method={rec['method']} "
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
        "inversion_closure": c30.inversion_closure(),
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c32 exact-L1 x on YXXYxxyx")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    c26._FOLD_CACHE.clear()
    controls = c26.planted_controls()
    xclass = c30.x_class_exponents()
    summary = summarize(report["scans"], controls, xclass)
    report["summary"] = summary
    report["x_class"] = xclass
    report["controls"] = controls
    report["inversion_closure"] = c30.inversion_closure()
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c32 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
