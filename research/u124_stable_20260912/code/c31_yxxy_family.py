#!/usr/bin/env python3
"""C31: YXXYxxyx family — y ≡ C^{-1} (L1=1) then k=3 ncl; aca_32 exact L1=2.

The next unused shared-donor block is eight best-table rows with donor
D = YXXYxxyx, exponent (1,−1), cyclic length 8. Seven companions are
consecutive BS(m,m+1) (m=3..6) with exponent (0,−1); on those rows y and
{Xyx, xyX} have unique combination (0,−1) against (D, C), so L1=1 and
y ≡ C^{-1}. Even k is abelian-impossible. k=1 is blocked by |C|≥9.
k=3 is the C23/C25 nine signed-type configs with R^+ = C^{-1} and S = D.

The remaining row aca_32 is not BS: y has combination (1,−1), L1=2, so
exact-L1 is one D^+ and one C^{-1} (two-factor Cartesian).

A hit is a normal-closure candidate, not a C12 primitive.

Not a heap search. Not a U124 solve unless a witness is found and given
an explicit AC1–AC5 path.
"""
from __future__ import annotations

import csv
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
import c24_even_k as c24  # noqa: E402
import c25_alt_words as c25  # noqa: E402
import c26_y_exact_l1 as c26  # noqa: E402
import c29_yxx_family as c29  # noqa: E402
from u124_census import bs_mm1_shape  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c31_yxxy_family.json"

DONOR = "YXXYxxyx"
ALPHABET = "xXyY"
POSITIVE_Y = c29.POSITIVE_Y
ROW_IDS = (
    "aca_22",
    "aca_23",
    "aca_32",
    "aca_46",
    "aca_49",
    "aca_68",
    "aca_70",
    "aca_89",
)
L1_1_IDS = (
    "aca_22",
    "aca_23",
    "aca_46",
    "aca_49",
    "aca_68",
    "aca_70",
    "aca_89",
)
EXCEPTIONAL_ID = "aca_32"


def load_best() -> dict[str, dict]:
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        return {row["name"]: row for row in csv.DictReader(handle)}


def split_pair(r1: str, r2: str) -> tuple[str, str]:
    for donor, companion in ((r1, r2), (r2, r1)):
        if donor == DONOR:
            return donor, companion
    raise ValueError(f"donor {DONOR} not a displayed relator")


def abelian_row(name: str, companion: str) -> dict:
    donor = DONOR
    ed, ec = c22.exp_on(donor, "xy"), c22.exp_on(companion, "xy")
    rows = {}
    for word in ("y", "Xyx", "xyX", "x"):
        target = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], ec[0], ed[1], ec[1], target[0], target[1])
        rows[word] = {"exp": list(target), "combo": sol, "L1": c24.l1_combo(sol)}
    y = rows["y"]
    bs, m = bs_mm1_shape(companion)
    return {
        "id": name,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "C_exp": list(ec),
        "D_cyc_len": len(cyc_reduce(donor)),
        "C_cyc_len": len(cyc_reduce(companion)),
        "y_combo": y["combo"],
        "y_L1": y["L1"],
        "Xyx_same_as_y": rows["Xyx"]["combo"] == y["combo"],
        "xyX_same_as_y": rows["xyX"]["combo"] == y["combo"],
        "x_combo": rows["x"]["combo"],
        "x_L1": rows["x"]["L1"],
        "k1_len_obstruction": len(cyc_reduce(companion)) > 1 if y["L1"] == 1 else None,
        "even_k_forbidden": y["L1"] == 1,
        "companion_bs_mm1": bs,
        "companion_bs_m": m,
        "is_l1_1": name in L1_1_IDS,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    rec = c25.scan_three_against(
        inv(companion),
        companion,
        DONOR,
        inv(DONOR),
        conjugators,
        set(POSITIVE_Y),
    )
    typed = c29.typed_nine_size(
        rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"]
    )
    rec.update(
        {
            "id": name,
            "companion": companion,
            "n_typed_tuples": typed,
            "n_products_equals_typed": rec["n_products"] == typed,
            "D_cyc_len": len(cyc_reduce(DONOR)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "targets": list(POSITIVE_Y),
        }
    )
    return rec


def exact_l1_row(name: str, companion: str, combo_a: int, combo_b: int) -> dict:
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    a_word = DONOR if combo_a >= 0 else inv(DONOR)
    b_word = companion if combo_b >= 0 else inv(companion)
    a_factors = c23.unique_conjugates(a_word, conjugators)
    b_factors = c23.unique_conjugates(b_word, conjugators)
    m = abs(combo_a)
    k = m + abs(combo_b)
    n_typed = k * (len(a_factors) ** m) * len(b_factors) if k else 0
    rec = c26.cartesian_m_plus_one(a_factors, b_factors, m, set(POSITIVE_Y))
    rec.update(
        {
            "id": name,
            "companion": companion,
            "combo_a": combo_a,
            "combo_b": combo_b,
            "L1": abs(combo_a) + abs(combo_b),
            "k": k,
            "n_A": len(a_factors),
            "n_B": len(b_factors),
            "n_typed_tuples": n_typed,
            "n_products_equals_typed": rec["n_products"] == n_typed,
            "targets": list(POSITIVE_Y),
        }
    )
    return rec


def summarize(
    abelian: list[dict], three: list[dict], exact: dict, ctrl: dict
) -> dict:
    l1_1 = [row for row in abelian if row["is_l1_1"]]
    return {
        "n_rows": len(abelian),
        "n_l1_1": len(l1_1),
        "all_l1_1_combo_zero_minus_one": all(
            row["y_combo"].get("a") == 0 and row["y_combo"].get("b") == -1
            for row in l1_1
        ),
        "all_l1_1_bs_mm1": all(row["companion_bs_mm1"] for row in l1_1),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_l1_1_k1_len_block": all(row["k1_len_obstruction"] for row in l1_1),
        "all_l1_1_even_k_forbidden": all(row["even_k_forbidden"] for row in l1_1),
        "exceptional_id": EXCEPTIONAL_ID,
        "exceptional_y_L1": next(
            row["y_L1"] for row in abelian if row["id"] == EXCEPTIONAL_ID
        ),
        "exceptional_not_bs": not next(
            row["companion_bs_mm1"] for row in abelian if row["id"] == EXCEPTIONAL_ID
        ),
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": sum(row["n_products"] for row in three),
        "three_n_typed_tuples": sum(row["n_typed_tuples"] for row in three),
        "three_products_equal_typed": all(row["n_products_equals_typed"] for row in three),
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in three),
        "exact_found": exact["found"],
        "exact_n_products": exact["n_products"],
        "exact_n_typed": exact["n_typed_tuples"],
        "exact_min_len": exact["min_len"],
        "counts_are_nine_config_cartesian": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "D = YXXYxxyx has exponent (1,−1). Seven companions are consecutive BS(m,m+1) with y ≡ C^{-1}, L1=1.",
        "Even k is abelian-impossible on those seven. k=1 is blocked by |C|≥9. k=3 is the nine signed-type configs of C23/C25.",
        "aca_32 is not BS: y has L1=2, exact-L1 two-factor Cartesian.",
        "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^k.",
        "A hit would be a normal-closure candidate, not a C12 primitive.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = c29.planted()
    print("c31 planted", ctrl["ok"], flush=True)
    abelian = []
    three = []
    exact = None
    for name in ROW_IDS:
        row = best[name]
        _donor, companion = split_pair(row["r1"], row["r2"])
        ab = abelian_row(name, companion)
        abelian.append(ab)
        if name in L1_1_IDS:
            rec = three_factor_row(name, companion)
            three.append(rec)
            print(
                f"c31 {name} products={rec['n_products']} min_len={rec['min_len']} "
                f"found={rec['found']}",
                flush=True,
            )
        else:
            combo = ab["y_combo"]
            exact = exact_l1_row(name, companion, combo["a"], combo["b"])
            print(
                f"c31 {name} exact L1={exact['L1']} products={exact['n_products']} "
                f"min_len={exact['min_len']} found={exact['found']}",
                flush=True,
            )
    if exact is None:
        raise RuntimeError("missing aca_32 exact-L1 scan")
    summary = summarize(abelian, three, exact, ctrl)
    report = {
        "summary": summary,
        "planted": ctrl,
        "abelian": abelian,
        "three_factor": three,
        "exact_l1_aca_32": exact,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c31 YXXYxxyx family")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = c29.planted()
    summary = summarize(
        report["abelian"], report["three_factor"], report["exact_l1_aca_32"], ctrl
    )
    report["summary"] = summary
    report["planted"] = ctrl
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c31 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
