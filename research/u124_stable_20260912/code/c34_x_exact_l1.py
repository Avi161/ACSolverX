#!/usr/bin/env python3
"""C34: exact-L1 typed products for defining word x on the C33 rows.

C33 left defining word x. Both remaining length-7 donors abelianize to
(0,−1), so C30's formula applies: unimodular C_ab=(p,q) has p=±1 and the
unique x-combination is (a,b)=(pq,p). On the twelve listed rows L1 runs
from 1 (aca_43) to 10. Exact-L1 products are |a| conjugates of D^{sign(a)}
and one conjugate of C^{sign(b)}.

Window: 2≤L1≤7 on those twelve rows. L1=1 is aca_43 (k=1 blocked by
lengths; even k impossible). L1≥8 is open (aca_123, 85, 98).

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
import c33_len7_donors as c33  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
JSON_PATH = OUT / "c34_x_exact_l1.json"
ALPHABET = "xXyY"
POSITIVE_X = c30.POSITIVE_X
CARTESIAN_MAX_TUPLES = c26.CARTESIAN_MAX_TUPLES
WINDOW_MIN, WINDOW_MAX = 2, 7


def window_rows(abelian: list[dict] | None = None) -> list[dict]:
    if abelian is None:
        report = json.loads(
            (OUT / "c33_len7_donors.json").read_text(encoding="utf-8")
        )
        abelian = report["abelian"]
    return [row for row in abelian if WINDOW_MIN <= row["x_L1"] <= WINDOW_MAX]


def skipped(abelian: list[dict]) -> dict:
    l1_1 = [row for row in abelian if row["x_L1"] == 1]
    ge8 = [row for row in abelian if row["x_L1"] >= 8]
    return {
        "l1_1": [
            {"id": row["id"], "donor": row["donor"], "L1": row["x_L1"]}
            for row in l1_1
        ],
        "l1_ge_8": [
            {"id": row["id"], "donor": row["donor"], "L1": row["x_L1"]}
            for row in ge8
        ],
    }


def scan_row(name: str, donor: str, companion: str, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_X)
    p, q = c22.exp_on(companion, "xy")
    a, b, l1 = c30.x_combo_from_c_exp(p, q)
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
            "donor": donor,
            "companion": companion,
            "combo_a": a,
            "combo_b": b,
            "L1": l1,
            "k": k,
            "n_A": len(a_factors),
            "n_B": len(b_factors),
            "n_typed_tuples": n_typed,
            "n_products_equals_typed": (
                rec["n_products"] == n_typed if rec["n_products"] is not None else None
            ),
            "D_cyc_len": len(cyc_reduce(donor)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "targets": sorted(targets),
            "equality_is_free_reduce_literal": True,
        }
    )
    return rec


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("cartesian_min_lens") or []
    observed = summary.get("cartesian_observed_min_len")
    return [
        "Exact L1 for x on C33 donors is |a| copies of D^{sign(a)} and one C^{sign(b)}.",
        "Both donors have D_ab=(0,-1), so C30's (a,b)=(pq,p) applies. L1 in {2,…,7} is the listed window rows.",
        (
            f"All-window typed size {summary['n_typed_tuples_total']} is "
            "k|A|^{k-1}|B|, not |F|^k."
        ),
        (
            f"Cartesian cells enumerate {summary['n_cartesian_products_enumerated']} "
            f"products (observed min lengths {mins}, all ≥{observed})."
        ),
        (
            f"MITM cells have typed search-space size {summary['n_typed_tuples_mitm']} "
            "and do not enumerate that many products."
        ),
        "Equality is free-reduce literal against {x, Yxy, yxY}. A hit would be a normal-closure candidate, not C12.",
        "JSON is same-code replay plus C26 planted controls. No U124 row is solved.",
    ]


def summarize(scans: list[dict], controls: dict, xclass: dict, skip: dict) -> dict:
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
        "cartesian_products_equal_typed": all(
            row["n_products_equals_typed"] for row in cart
        ),
        "skipped_l1_1": skip["l1_1"],
        "skipped_l1_ge_8": skip["l1_ge_8"],
        "uses_c30_combo_formula": True,
        "l1_range_is_window_rows": True,
        "equality_is_free_reduce_literal": True,
        "one_letter_class_complete": xclass["one_letter_class_complete"],
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
    c33_report = json.loads((OUT / "c33_len7_donors.json").read_text(encoding="utf-8"))
    abelian = c33_report["abelian"]
    skip = skipped(abelian)
    xclass = c30.x_class_exponents()
    scans = []
    for row in window_rows(abelian):
        rec = scan_row(row["id"], row["donor"], row["companion"])
        scans.append(rec)
        print(
            f"c34 {row['id']} L1={rec['L1']} method={rec['method']} "
            f"typed={rec['n_typed_tuples']} found={rec['found']} "
            f"min_len={rec['min_len']}",
            flush=True,
        )
    controls = c26.planted_controls()
    summary = summarize(scans, controls, xclass, skip)
    report = {
        "summary": summary,
        "x_class": xclass,
        "scans": scans,
        "skipped": skip,
        "controls": controls,
        "inversion_closure": c30.inversion_closure(),
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c34 exact-L1 x on C33 rows")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    c26._FOLD_CACHE.clear()
    controls = c26.planted_controls()
    xclass = c30.x_class_exponents()
    c33_report = json.loads((OUT / "c33_len7_donors.json").read_text(encoding="utf-8"))
    skip = skipped(c33_report["abelian"])
    summary = summarize(report["scans"], controls, xclass, skip)
    report["summary"] = summary
    report["x_class"] = xclass
    report["skipped"] = skip
    report["controls"] = controls
    report["inversion_closure"] = c30.inversion_closure()
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c34 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
