#!/usr/bin/env python3
"""C37: exact-L1 typed products for defining word x on the C36 rows.

C36 left defining word x. On the seven listed YXXYxxyX companions with
C_ab=(0,−1), the unique x-combination is (a,b)=(−1,1), so L1=2. Exact-L1
products are one conjugate of D^{-1} and one conjugate of C, in either
order. This is not a claim about every unimodular companion of D.

Prefix/one-letter conjugators, unique conjugates per signed type. Counts
are typed Cartesian sizes 2|A||B|, not |F|^k. All seven cells are within
the Cartesian cap.

Targets are the exponent-(1,0) one-letter class {x, Yxy, yxY}. A hit is a
normal-closure candidate, not a C12 primitive. Hits persist signed types,
factors, conjugators, and an outside-scanner replay.

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
import c26_y_exact_l1 as c26  # noqa: E402
import c30_x_exact_l1 as c30  # noqa: E402
import c35_yxxx_family as c35  # noqa: E402
import c36_yxxyx_family as c36  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
JSON_PATH = OUT / "c37_x_exact_l1.json"
ALPHABET = "xXyY"
POSITIVE_X = c30.POSITIVE_X
DONOR = c36.DONOR
ROW_IDS = c36.ROW_IDS
EXPECTED_TYPED = {
    "aca_21": 1200,
    "aca_25": 1300,
    "aca_47": 1508,
    "aca_50": 1620,
    "aca_69": 1848,
    "aca_73": 1972,
    "aca_96": 2356,
}
EXPECTED_TYPED_TOTAL = 11804


def x_combo_from_listed_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique x combo against D_ab=(-1,-1) when C_ab=(0,-1).

    Not a claim about every unimodular companion of this donor.
    """
    if (p, q) != (0, -1):
        raise ValueError("C37 combo (-1,1) is for listed C_ab=(0,-1) companions")
    return -1, 1, 2


def cartesian_two_witness(
    a_word: str,
    b_word: str,
    conjugators: list[str],
    targets: set[str],
) -> dict:
    a_factors = c23.unique_conjugates(a_word, conjugators)
    b_factors = c23.unique_conjugates(b_word, conjugators)
    g_a = c35.conjugator_map(a_word, conjugators)
    g_b = c35.conjugator_map(b_word, conjugators)
    type_a, type_b = "D-", "C+"
    hit = None
    min_len = None
    n_products = 0
    n_len_le_3 = 0
    n_hits = 0
    for pos in range(2):
        types = [type_a, type_a]
        types[pos] = type_b
        lists = [a_factors, a_factors]
        lists[pos] = b_factors
        gmaps = [g_a, g_a]
        gmaps[pos] = g_b
        for factors in product(*lists):
            word = free_reduce("".join(factors))
            n_products += 1
            length = len(word)
            if min_len is None or length < min_len:
                min_len = length
            if length <= 3:
                n_len_le_3 += 1
            if word in targets:
                n_hits += 1
                if hit is None:
                    conjugators_used = [gmaps[i][factors[i]] for i in range(2)]
                    hit = {
                        "word": word,
                        "len": length,
                        "pos": pos,
                        "signed_types": list(types),
                        "factors": list(factors),
                        "conjugators": conjugators_used,
                        "replay_free_reduce_equals_target": (
                            free_reduce("".join(factors)) == word
                        ),
                    }
    n_typed = 2 * len(a_factors) * len(b_factors)
    return {
        "method": "typed_cartesian",
        "n_products": n_products,
        "n_typed_tuples": n_typed,
        "n_products_equals_typed": n_products == n_typed,
        "min_len": min_len,
        "n_len_le_3": n_len_le_3,
        "n_hits": n_hits,
        "hit": hit,
        "found": hit is not None,
        "n_A": len(a_factors),
        "n_B": len(b_factors),
        "k": 2,
    }


def scan_row(name: str, companion: str, targets: set[str] | None = None) -> dict:
    if targets is None:
        targets = set(POSITIVE_X)
    p, q = c22.exp_on(companion, "xy")
    a, b, l1 = x_combo_from_listed_c_exp(p, q)
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    a_word = inv(DONOR)
    b_word = companion
    rec = cartesian_two_witness(a_word, b_word, conjugators, targets)
    if rec["n_typed_tuples"] > c26.CARTESIAN_MAX_TUPLES:
        raise RuntimeError(f"{name}: unexpected MITM cell {rec['n_typed_tuples']}")
    rec.update(
        {
            "id": name,
            "donor": DONOR,
            "companion": companion,
            "combo_a": a,
            "combo_b": b,
            "L1": l1,
            "n_conjugators": len(conjugators),
            "D_cyc_len": len(cyc_reduce(DONOR)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "targets": sorted(targets),
            "equality_is_free_reduce_literal": True,
            "combo_restricted_to_listed_C_ab": True,
            "counts_are_typed_cartesian": True,
            "not_F_to_the_k": True,
        }
    )
    if rec["hit"] is not None:
        rec["hit_replay_outside_scanner"] = c35.reconstruct_hit(
            rec["hit"], {"D-": a_word, "C+": b_word}
        )
    else:
        rec["hit_replay_outside_scanner"] = None
    expected = EXPECTED_TYPED[name]
    rec["matches_c36_predicted_typed"] = rec["n_typed_tuples"] == expected
    if rec["n_products"] != rec["n_typed_tuples"]:
        raise RuntimeError(
            f"{name}: n_products {rec['n_products']} != "
            f"n_typed_tuples {rec['n_typed_tuples']}"
        )
    if rec["n_typed_tuples"] != expected:
        raise RuntimeError(
            f"{name}: typed {rec['n_typed_tuples']} != C36 prediction {expected}"
        )
    return rec


def planted() -> dict:
    rec = cartesian_two_witness("xx", "X", [""], {"x"})
    miss = cartesian_two_witness("xx", "X", [""], {"u"})
    witness = rec["hit"]
    outside = None
    if witness is not None:
        outside = c35.reconstruct_hit(witness, {"D-": "xx", "C+": "X"})
    ok = (
        rec["found"]
        and not miss["found"]
        and rec["n_products"] == 2
        and rec["n_products_equals_typed"]
        and witness is not None
        and witness["word"] == "x"
        and outside is not None
        and outside["ok"]
        and free_reduce("".join(witness["factors"])) == "x"
    )
    return {
        "n_products_hit": rec["n_products"],
        "hit": witness,
        "hit_replay_outside_scanner": outside,
        "miss_found": miss["found"],
        "ok": ok,
        "independent_checker": False,
        "same_code_as_census": True,
    }


def summarize(scans: list[dict], controls: dict, xclass: dict) -> dict:
    mins = [row["min_len"] for row in scans]
    n_typed = sum(row["n_typed_tuples"] for row in scans)
    n_products = sum(row["n_products"] for row in scans)
    if n_typed != EXPECTED_TYPED_TOTAL or n_products != EXPECTED_TYPED_TOTAL:
        raise RuntimeError(
            f"C37 typed/product totals {n_typed}/{n_products} != {EXPECTED_TYPED_TOTAL}"
        )
    if not all(row["n_products_equals_typed"] for row in scans):
        raise RuntimeError("C37 per-row n_products != n_typed_tuples")
    return {
        "n_rows": len(scans),
        "all_combo_minus_one_one": all(
            row["combo_a"] == -1 and row["combo_b"] == 1 for row in scans
        ),
        "all_L1_2": all(row["L1"] == 2 for row in scans),
        "all_k_equals_L1": all(row["k"] == row["L1"] for row in scans),
        "combo_restricted_to_listed_C_ab": True,
        "any_hit": any(row["found"] for row in scans),
        "n_typed_tuples_total": n_typed,
        "n_cartesian_products_enumerated": n_products,
        "n_cartesian_cells": len(scans),
        "n_mitm_cells": 0,
        "cartesian_ids": [row["id"] for row in scans],
        "cartesian_min_lens": mins,
        "cartesian_observed_min_len": min(mins) if mins else None,
        "cartesian_products_equal_typed": True,
        "matches_c36_predicted_typed": all(row["matches_c36_predicted_typed"] for row in scans),
        "equality_is_free_reduce_literal": True,
        "one_letter_class_complete": xclass["one_letter_class_complete"],
        "hit_witness_records_factors_and_conjugators": True,
        "hit_replay_outside_scanner": True,
        "controls_ok": controls["ok"],
        "counts_are_typed_cartesian": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("cartesian_min_lens") or []
    observed = summary.get("cartesian_observed_min_len")
    return [
        "Exact L1 for x on the seven listed YXXYxxyX rows is one D^{-1} conjugate and one C conjugate, both orders.",
        "Combo (−1,1) and L1=2 are those listed C_ab=(0,−1) rows, not every unimodular companion of D.",
        f"Typed Cartesian total {summary['n_typed_tuples_total']} is 2|A||B| summed over seven rows, not |F|^k.",
        f"Enumerated {summary['n_cartesian_products_enumerated']} tuple evaluations (observed min lengths {mins}, census min {observed}).",
        "Equality is free-reduce literal against {x, Yxy, yxY}. A hit would be a normal-closure candidate, not C12.",
        "Hit witnesses persist signed types, factors, conjugators, and an outside-scanner replay.",
        "JSON is same-code replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = c36.load_best()
    xclass = c30.x_class_exponents()
    controls = planted()
    print("c37 planted", controls["ok"], flush=True)
    scans = []
    for name in ROW_IDS:
        _donor, companion = c36.split_pair(best[name]["r1"], best[name]["r2"])
        rec = scan_row(name, companion)
        scans.append(rec)
        print(
            f"c37 {name} typed={rec['n_typed_tuples']} min_len={rec['min_len']} "
            f"found={rec['found']}",
            flush=True,
        )
    summary = summarize(scans, controls, xclass)
    report = {
        "summary": summary,
        "x_class": xclass,
        "scans": scans,
        "controls": controls,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c37 exact-L1 x on C36 rows")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    controls = planted()
    xclass = c30.x_class_exponents()
    summary = summarize(report["scans"], controls, xclass)
    report["summary"] = summary
    report["x_class"] = xclass
    report["controls"] = controls
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c37 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
