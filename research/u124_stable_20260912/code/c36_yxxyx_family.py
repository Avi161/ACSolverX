#!/usr/bin/env python3
"""C36: YXXYxxyX family — y ≡ C^{-1} (L1=1) on seven BS companions, then k=3 ncl.

Unused listed shared-donor D = YXXYxxyX, exponent (−1,−1), cyclic length 8.
Seven best-table rows, all companions consecutive BS(m,m+1) (m=3..6) with
C_ab=(0,−1). On those listed companions, y and {Xyx, xyX} have unique
combination (0,−1), so L1=1 and y ≡ C^{-1}. This is not a claim about
every unimodular companion of D.

Even k is abelian-impossible. k=1 is blocked by |C|≥9. k=3 is the
C23/C25 nine signed-type configs with R^+ = C^{-1} and S = D (C31
orientation). Parallel to C31’s YXXYxxyx block; disjoint donor/row
presentation pairs, not a disjoint companion-word pool. No exceptional
row.

A hit is a normal-closure candidate, not a C12 primitive. If a hit
occurs, signed types, factors, and conjugators are persisted and then
replayed outside the scanner loop.

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
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c22_gate_witness as c22  # noqa: E402
import c24_even_k as c24  # noqa: E402
import c29_yxx_family as c29  # noqa: E402
import c35_yxxx_family as c35  # noqa: E402
from u124_census import bs_mm1_shape  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c36_yxxyx_family.json"

DONOR = "YXXYxxyX"
ALPHABET = "xXyY"
POSITIVE_Y = c29.POSITIVE_Y
ORIENTATION = c35.C31_ORIENTATION
ROW_IDS = (
    "aca_21",
    "aca_25",
    "aca_47",
    "aca_50",
    "aca_69",
    "aca_73",
    "aca_96",
)


def y_combo_from_listed_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique y combo against D_ab=(-1,-1) when C_ab=(0,-1).

    Not a claim about every unimodular companion of this donor.
    """
    if (p, q) != (0, -1):
        raise ValueError("C36 combo (0,-1) is for listed C_ab=(0,-1) companions")
    return 0, -1, 1


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
    a, b, l1 = y_combo_from_listed_c_exp(ec[0], ec[1])
    rows = {}
    for word in ("y", "Xyx", "xyX", "x"):
        target = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], ec[0], ed[1], ec[1], target[0], target[1])
        rows[word] = {"exp": list(target), "combo": sol, "L1": c24.l1_combo(sol)}
    y = rows["y"]
    if y["combo"].get("a") != a or y["combo"].get("b") != b or y["L1"] != l1:
        raise ValueError(f"{name}: combo mismatch {y['combo']} vs {(a, b)}")
    bs, m = bs_mm1_shape(companion)
    x = rows["x"]
    return {
        "id": name,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "C_exp": list(ec),
        "pair_det": ed[0] * ec[1] - ed[1] * ec[0],
        "D_cyc_len": len(cyc_reduce(donor)),
        "C_cyc_len": len(cyc_reduce(companion)),
        "y_combo": y["combo"],
        "y_L1": y["L1"],
        "Xyx_same_as_y": rows["Xyx"]["combo"] == y["combo"],
        "xyX_same_as_y": rows["xyX"]["combo"] == y["combo"],
        "x_combo": x["combo"],
        "x_L1": x["L1"],
        "k1_len_obstruction": len(cyc_reduce(companion)) >= 9,
        "even_k_forbidden": y["L1"] == 1,
        "companion_bs_mm1": bs,
        "companion_bs_m": m,
        "combo_restricted_to_listed_C_ab": True,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    rec = c35.scan_three_against_witness(
        inv(companion),
        companion,
        DONOR,
        inv(DONOR),
        conjugators,
        set(POSITIVE_Y),
        orientation=ORIENTATION,
    )
    if rec["orientation"] != ORIENTATION:
        raise RuntimeError(f"{name}: scanner kept C35 orientation {rec['orientation']}")
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
    if rec["hit"] is not None:
        bases = {
            "R+": inv(companion),
            "R-": companion,
            "S+": DONOR,
            "S-": inv(DONOR),
        }
        rec["hit_replay_outside_scanner"] = c35.reconstruct_hit(rec["hit"], bases)
    else:
        rec["hit_replay_outside_scanner"] = None
    return rec


def planted() -> dict:
    rec = c35.scan_three_against_witness(
        "y", "Y", "x", "X", [""], {"y"}, orientation=ORIENTATION
    )
    if rec["orientation"] != ORIENTATION:
        raise RuntimeError("planted kept C35 orientation")
    expected = c29.typed_nine_size(1, 1, 1, 1)
    miss = c35.scan_three_against_witness(
        "y", "Y", "x", "X", [""], {"u"}, orientation=ORIENTATION
    )
    witness = rec["hit"]
    outside = None
    if witness is not None:
        outside = c35.reconstruct_hit(
            witness, {"R+": "y", "R-": "Y", "S+": "x", "S-": "X"}
        )
    witness_ok = (
        witness is not None
        and witness["word"] == "y"
        and outside is not None
        and outside["ok"]
        and free_reduce("".join(witness["factors"])) == "y"
    )
    return {
        "n_products_hit": rec["n_products"],
        "n_typed": expected,
        "hit": witness,
        "hit_replay_outside_scanner": outside,
        "miss_found": miss["found"],
        "orientation": rec["orientation"],
        "witness_ok": witness_ok,
        "ok": (
            rec["found"]
            and not miss["found"]
            and rec["n_products"] == expected
            and miss["n_products"] == expected
            and witness_ok
            and rec["orientation"] == ORIENTATION
        ),
        "independent_checker": False,
        "same_code_as_census": True,
    }


def summarize(abelian: list[dict], three: list[dict], ctrl: dict) -> dict:
    return {
        "n_rows": len(abelian),
        "donor": DONOR,
        "all_D_exp_minus_one_minus_one": all(row["D_exp"] == [-1, -1] for row in abelian),
        "all_C_exp_zero_minus_one": all(row["C_exp"] == [0, -1] for row in abelian),
        "all_companion_bs_mm1": all(row["companion_bs_mm1"] for row in abelian),
        "n_exceptional_rows": 0,
        "all_y_L1_1": all(row["y_L1"] == 1 for row in abelian),
        "all_y_combo_zero_minus_one": all(
            row["y_combo"].get("a") == 0 and row["y_combo"].get("b") == -1
            for row in abelian
        ),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_x_combo_minus_one_one": all(
            row["x_combo"].get("a") == -1 and row["x_combo"].get("b") == 1
            for row in abelian
        ),
        "all_x_L1_2": all(row["x_L1"] == 2 for row in abelian),
        "all_k1_len_block": all(row["k1_len_obstruction"] for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "combo_restricted_to_listed_C_ab": True,
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": sum(row["n_products"] for row in three),
        "three_n_typed_tuples": sum(row["n_typed_tuples"] for row in three),
        "three_products_equal_typed": all(row["n_products_equals_typed"] for row in three),
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_all_orientation_c31": all(row["orientation"] == ORIENTATION for row in three),
        "counts_are_nine_config_cartesian": True,
        "disjoint_donor_row_presentation_pairs": True,
        "not_disjoint_companion_word_set": True,
        "not_a_c31_rerun": True,
        "c28_touched_rows_under_different_predicate": True,
        "hit_witness_records_factors_and_conjugators": True,
        "hit_replay_outside_scanner": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "D = YXXYxxyX has exponent (−1,−1). On the seven listed C_ab=(0,−1) BS companions, y has unique combination (0,−1), L1=1.",
        "That combo is not claimed for every unimodular companion of D.",
        "Even k is abelian-impossible. k=1 is blocked by |C|≥9. k=3 uses C31 orientation R^+=C^{-1}, S=D.",
        "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^3.",
        "Disjoint donor/row presentation pairs from C31, not a disjoint companion-word pool. No exceptional row.",
        "A hit would be a normal-closure candidate, not a C12 primitive. Hit witnesses persist factors and are replayed outside the scanner.",
        "Observed minimum length is a C36 census statistic, not a theorem and not a comparison with C31.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = planted()
    print("c36 planted", ctrl["ok"], flush=True)
    abelian = []
    three = []
    for name in ROW_IDS:
        row = best[name]
        _donor, companion = split_pair(row["r1"], row["r2"])
        ab = abelian_row(name, companion)
        abelian.append(ab)
        rec = three_factor_row(name, companion)
        three.append(rec)
        print(
            f"c36 {name} products={rec['n_products']} min_len={rec['min_len']} "
            f"found={rec['found']}",
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
    print("c36 YXXYxxyX family")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = planted()
    summary = summarize(report["abelian"], report["three_factor"], ctrl)
    report["summary"] = summary
    report["planted"] = ctrl
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c36 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
