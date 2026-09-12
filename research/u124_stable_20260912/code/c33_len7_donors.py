#!/usr/bin/env python3
"""C33: remaining length-7 donors with D_ab=(0,−1): y ≡ D^{-1}, then k=3 ncl.

C29 treated compact donor YXXyxYx. Two unused best-table donors have the
same abelian type and cyclic length 7:

- YXyXYxx (six rows)
- YYXXyxx (six rows, Family A floor companions)

On every unimodular companion the unique combination of y (and of
{Xyx, xyX}) against (D, C) is (−1, 0), so L1=1. Even k is impossible.
k=1 is blocked by |D|=7. k=3 is the C23/C25 nine signed-type configs
with R^+ = D^{-1} and S = C.

A hit is a normal-closure candidate, not a C12 primitive. This is not a
re-run of C29's YXXyxYx census.

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
import c24_even_k as c24  # noqa: E402
import c25_alt_words as c25  # noqa: E402
import c29_yxx_family as c29  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c33_len7_donors.json"
ALPHABET = "xXyY"
POSITIVE_Y = c29.POSITIVE_Y
FAMILIES = (
    {
        "donor": "YXyXYxx",
        "ids": ("aca_8", "aca_85", "aca_98", "aca_121", "aca_122", "aca_123"),
    },
    {
        "donor": "YYXXyxx",
        "ids": ("aca_1", "aca_7", "aca_31", "aca_43", "aca_72", "aca_99"),
    },
)


def load_best() -> dict[str, dict]:
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        return {row["name"]: row for row in csv.DictReader(handle)}


def split_pair(donor: str, r1: str, r2: str) -> tuple[str, str]:
    for displayed, companion in ((r1, r2), (r2, r1)):
        if displayed == donor:
            return displayed, companion
    raise ValueError(f"donor {donor} not a displayed relator")


def abelian_row(name: str, donor: str, companion: str) -> dict:
    ed, ec = c22.exp_on(donor, "xy"), c22.exp_on(companion, "xy")
    rows = {}
    for word in ("y", "Xyx", "xyX", "x"):
        target = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], ec[0], ed[1], ec[1], target[0], target[1])
        rows[word] = {"exp": list(target), "combo": sol, "L1": c24.l1_combo(sol)}
    y = rows["y"]
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
        "k1_len_obstruction": len(cyc_reduce(donor)) > 1,
        "even_k_forbidden": y["L1"] == 1,
        "targets": rows,
    }


def three_factor_row(name: str, donor: str, companion: str) -> dict:
    conjugators = c22.short_conjugators([donor, companion], ALPHABET, 1)
    rec = c25.scan_three_against(
        inv(donor),
        donor,
        companion,
        inv(companion),
        conjugators,
        set(POSITIVE_Y),
    )
    typed = c29.typed_nine_size(
        rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"]
    )
    rec.update(
        {
            "id": name,
            "donor": donor,
            "companion": companion,
            "n_typed_tuples": typed,
            "n_products_equals_typed": rec["n_products"] == typed,
            "D_cyc_len": len(cyc_reduce(donor)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "targets": list(POSITIVE_Y),
        }
    )
    return rec


def summarize(abelian: list[dict], three: list[dict], ctrl: dict) -> dict:
    return {
        "n_rows": len(abelian),
        "n_donors": len({row["donor"] for row in abelian}),
        "all_D_exp_zero_minus_one": all(row["D_exp"] == [0, -1] for row in abelian),
        "all_D_cyc_len_7": all(row["D_cyc_len"] == 7 for row in abelian),
        "all_y_L1_1": all(row["y_L1"] == 1 for row in abelian),
        "all_y_combo_minus_one_zero": all(
            row["y_combo"].get("a") == -1 and row["y_combo"].get("b") == 0
            for row in abelian
        ),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_k1_len_block": all(row["k1_len_obstruction"] for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": sum(row["n_products"] for row in three),
        "three_n_typed_tuples": sum(row["n_typed_tuples"] for row in three),
        "three_products_equal_typed": all(row["n_products_equals_typed"] for row in three),
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in three),
        "not_a_c29_rerun": True,
        "counts_are_nine_config_cartesian": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "Donors YXyXYxx and YYXXyxx have exponent (0,−1) and cyclic length 7, the same abelian type as C29's YXXyxYx.",
        "On every listed unimodular companion, y has unique combination (−1, 0), L1=1.",
        "Even k is abelian-impossible. k=1 is blocked by |D|=7. k=3 is the nine signed-type configs of C23/C25.",
        "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^3.",
        "This is not a re-run of C29. A hit would be a normal-closure candidate, not a C12 primitive.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = c29.planted()
    print("c33 planted", ctrl["ok"], flush=True)
    abelian = []
    three = []
    for family in FAMILIES:
        donor = family["donor"]
        for name in family["ids"]:
            row = best[name]
            _d, companion = split_pair(donor, row["r1"], row["r2"])
            ab = abelian_row(name, donor, companion)
            abelian.append(ab)
            rec = three_factor_row(name, donor, companion)
            three.append(rec)
            print(
                f"c33 {name} donor={donor} products={rec['n_products']} "
                f"min_len={rec['min_len']} found={rec['found']}",
                flush=True,
            )
    summary = summarize(abelian, three, ctrl)
    report = {
        "summary": summary,
        "planted": ctrl,
        "abelian": abelian,
        "three_factor": three,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c33 remaining length-7 D_ab=(0,-1) donors")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = c29.planted()
    summary = summarize(report["abelian"], report["three_factor"], ctrl)
    report["summary"] = summary
    report["planted"] = ctrl
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c33 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
