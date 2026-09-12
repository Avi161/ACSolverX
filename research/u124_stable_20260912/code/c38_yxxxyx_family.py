#!/usr/bin/env python3
"""C38: YXXXyxYxx family — y ≡ D^{-1} (L1=1) on seven listed rows, then k=3 ncl.

Unused listed shared-donor D = YXXXyxYxx, exponent (0,−1), cyclic length 9.
Seven best-table rows, all with |p|=1 so det(D,C)=p=±1. On those listed
rows, y and {Xyx, xyX} have unique combination (−1,0), so L1=1 and
y ≡ D^{-1}. This is not a claim about every companion of D.

Even k is abelian-impossible. k=1 is blocked by |D|=9. k=3 is the
C23/C25 nine signed-type configs with R^+ = D^{-1} and S = C (C29/C35
orientation). Parallel to C29/C33; disjoint donor/row presentation
pairs, not a disjoint companion-word pool. Not the last unused listed
donor.

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
import c26_y_exact_l1 as c26  # noqa: E402
import c29_yxx_family as c29  # noqa: E402
import c30_x_exact_l1 as c30  # noqa: E402
import c35_yxxx_family as c35  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c38_yxxxyx_family.json"

DONOR = "YXXXyxYxx"
ALPHABET = "xXyY"
POSITIVE_Y = c29.POSITIVE_Y
ORIENTATION = c35.C35_ORIENTATION
ROW_IDS = (
    "aca_48",
    "aca_60",
    "aca_75",
    "aca_76",
    "aca_84",
    "aca_110",
    "aca_113",
)
EXPECTED_COMPANIONS = {
    "aca_48": "YYYYXXyxxx",
    "aca_60": "YYYYYXXyxxx",
    "aca_75": "YYYYYYXXXYxx",
    "aca_76": "YYYYYYXXyxxx",
    "aca_84": "YYYYYYYXXXYxx",
    "aca_110": "YYYYYYYXXyxxx",
    "aca_113": "YYYYYYYYXXXYxx",
}
EXPECTED_C_EXP = {
    "aca_48": (1, -3),
    "aca_60": (1, -4),
    "aca_75": (-1, -7),
    "aca_76": (1, -5),
    "aca_84": (-1, -8),
    "aca_110": (1, -6),
    "aca_113": (-1, -9),
}
EXPECTED_TYPED = {
    "aca_48": 188328,
    "aca_60": 222120,
    "aca_75": 235197,
    "aca_76": 259776,
    "aca_84": 274329,
    "aca_110": 301512,
    "aca_113": 317625,
}
EXPECTED_TYPED_TOTAL = 1_798_887
OVERLAPPING_COMPANIONS = {
    "YYYYYYXXXYxx": ("aca_75", "aca_77"),
    "YYYYYYYXXXYxx": ("aca_84", "aca_107"),
}


def y_combo_from_listed_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique y combo against D_ab=(0,-1) when |p|=1.

    Not a claim about every companion of this donor, nor about p=0.
    """
    if abs(p) != 1:
        raise ValueError("C38 combo (-1,0) is for listed unimodular C_ab with |p|=1")
    return -1, 0, 1


def load_best() -> dict[str, dict]:
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        return {row["name"]: row for row in csv.DictReader(handle)}


def split_pair(r1: str, r2: str) -> tuple[str, str]:
    for donor, companion in ((r1, r2), (r2, r1)):
        if donor == DONOR:
            return donor, companion
    raise ValueError(f"donor {DONOR} not a displayed relator")


def abelian_row(name: str, companion: str) -> dict:
    if name not in ROW_IDS:
        raise ValueError(f"{name} is not a listed C38 row")
    if companion != EXPECTED_COMPANIONS[name]:
        raise ValueError(f"{name}: companion {companion} != {EXPECTED_COMPANIONS[name]}")
    donor = DONOR
    ed, ec = c22.exp_on(donor, "xy"), c22.exp_on(companion, "xy")
    if tuple(ed) != (0, -1):
        raise ValueError(f"{name}: D_exp {ed} != (0,-1)")
    if tuple(ec) != EXPECTED_C_EXP[name]:
        raise ValueError(f"{name}: C_exp {ec} != {EXPECTED_C_EXP[name]}")
    a, b, l1 = y_combo_from_listed_c_exp(ec[0], ec[1])
    rows = {}
    for word in ("y", "Xyx", "xyX", "x"):
        target = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], ec[0], ed[1], ec[1], target[0], target[1])
        rows[word] = {"exp": list(target), "combo": sol, "L1": c24.l1_combo(sol)}
    y = rows["y"]
    if y["combo"].get("a") != a or y["combo"].get("b") != b or y["L1"] != l1:
        raise ValueError(f"{name}: combo mismatch {y['combo']} vs {(a, b)}")
    xa, xb, xl1 = c30.x_combo_from_c_exp(ec[0], ec[1])
    x = rows["x"]
    if x["combo"].get("a") != xa or x["combo"].get("b") != xb or x["L1"] != xl1:
        raise ValueError(f"{name}: leftover x combo mismatch {x['combo']} vs {(xa, xb)}")
    pair_det = ed[0] * ec[1] - ed[1] * ec[0]
    return {
        "id": name,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "C_exp": list(ec),
        "pair_det": pair_det,
        "pair_det_equals_C_x": pair_det == ec[0],
        "pair_exponent_matrix_unimodular": abs(pair_det) == 1,
        "D_cyc_len": len(cyc_reduce(donor)),
        "C_cyc_len": len(cyc_reduce(companion)),
        "y_combo": y["combo"],
        "y_L1": y["L1"],
        "Xyx_same_as_y": rows["Xyx"]["combo"] == y["combo"],
        "xyX_same_as_y": rows["xyX"]["combo"] == y["combo"],
        "x_combo": x["combo"],
        "x_L1": x["L1"],
        "x_combo_is_c30_leftover_not_censused": True,
        "k1_len_obstruction": len(cyc_reduce(donor)) >= 9,
        "even_k_forbidden": y["L1"] == 1,
        "combo_restricted_to_listed_rows": True,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    if name not in ROW_IDS:
        raise ValueError(f"{name} is not a listed C38 row")
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    rec = c35.scan_three_against_witness(
        inv(DONOR),
        DONOR,
        companion,
        inv(companion),
        conjugators,
        set(POSITIVE_Y),
        orientation=ORIENTATION,
    )
    if rec["orientation"] != ORIENTATION:
        raise RuntimeError(f"{name}: scanner lost C35 orientation {rec['orientation']}")
    if rec["orientation"] == c35.C31_ORIENTATION:
        raise RuntimeError(f"{name}: scanner used C31 orientation")
    typed = c29.typed_nine_size(
        rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"]
    )
    expected = EXPECTED_TYPED[name]
    rec.update(
        {
            "id": name,
            "companion": companion,
            "n_typed_tuples": typed,
            "n_products_equals_typed": rec["n_products"] == typed,
            "matches_predicted_typed": typed == expected,
            "D_cyc_len": len(cyc_reduce(DONOR)),
            "C_cyc_len": len(cyc_reduce(companion)),
            "targets": list(POSITIVE_Y),
        }
    )
    if typed > c26.CARTESIAN_MAX_TUPLES:
        raise RuntimeError(f"{name}: unexpected MITM cell {typed}")
    if rec["n_products"] != typed:
        raise RuntimeError(
            f"{name}: n_products {rec['n_products']} != n_typed_tuples {typed}"
        )
    if typed != expected:
        raise RuntimeError(f"{name}: typed {typed} != predicted {expected}")
    if rec["hit"] is not None:
        bases = {
            "R+": inv(DONOR),
            "R-": DONOR,
            "S+": companion,
            "S-": inv(companion),
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
        raise RuntimeError("planted lost C35 orientation")
    if rec["orientation"] == c35.C31_ORIENTATION:
        raise RuntimeError("planted used C31 orientation")
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
    n_typed = sum(row["n_typed_tuples"] for row in three)
    n_products = sum(row["n_products"] for row in three)
    if n_typed != EXPECTED_TYPED_TOTAL or n_products != EXPECTED_TYPED_TOTAL:
        raise RuntimeError(
            f"C38 typed/product totals {n_typed}/{n_products} != {EXPECTED_TYPED_TOTAL}"
        )
    if not all(row["n_products_equals_typed"] for row in three):
        raise RuntimeError("C38 per-row n_products != n_typed_tuples")
    ids = [row["id"] for row in abelian]
    if tuple(ids) != ROW_IDS:
        raise RuntimeError(f"C38 row ids {ids} != {ROW_IDS}")
    return {
        "n_rows": len(abelian),
        "donor": DONOR,
        "all_D_exp_zero_minus_one": all(row["D_exp"] == [0, -1] for row in abelian),
        "all_D_cyc_len_9": all(row["D_cyc_len"] == 9 for row in abelian),
        "all_pair_exponent_matrix_unimodular": all(
            row["pair_exponent_matrix_unimodular"] for row in abelian
        ),
        "all_C_x_exp_abs_one": all(abs(row["C_exp"][0]) == 1 for row in abelian),
        "all_y_L1_1": all(row["y_L1"] == 1 for row in abelian),
        "all_y_combo_minus_one_zero": all(
            row["y_combo"].get("a") == -1 and row["y_combo"].get("b") == 0
            for row in abelian
        ),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_k1_len_block": all(row["k1_len_obstruction"] for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "combo_restricted_to_listed_rows": True,
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": n_products,
        "three_n_typed_tuples": n_typed,
        "three_products_equal_typed": True,
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_min_lens": [row["min_len"] for row in three],
        "three_all_orientation_c35": all(row["orientation"] == ORIENTATION for row in three),
        "three_none_orientation_c31": all(
            row["orientation"] != c35.C31_ORIENTATION for row in three
        ),
        "counts_are_nine_config_cartesian": True,
        "cartesian_cap_is_per_cell": True,
        "disjoint_donor_row_presentation_pairs": True,
        "not_disjoint_companion_word_set": True,
        "overlapping_companions": {
            word: list(ids) for word, ids in OVERLAPPING_COMPANIONS.items()
        },
        "not_last_unused_listed_donor": True,
        "not_a_c29_or_c33_rerun": True,
        "c28_touched_rows_under_different_predicate": True,
        "x_exact_l1_not_part_of_c38": True,
        "hit_witness_records_factors_and_conjugators": True,
        "hit_replay_outside_scanner": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("three_min_lens") or []
    observed = summary.get("three_min_len")
    return [
        "D = YXXXyxYxx has exponent (0,−1). On the seven listed |p|=1 rows, y has unique combination (−1,0), L1=1.",
        "That combo is not claimed for every companion of D, nor for p=0.",
        "Even k is abelian-impossible. k=1 is blocked by |D|=9. k=3 uses C35 orientation R^+=D^{-1}, S=C.",
        f"Typed Cartesian total {summary['three_n_typed_tuples']} is nine-config 3|R+|²|R−|+6|R+||S+||S−|, not |F|^3.",
        f"Enumerated {summary['three_n_products']} tuple evaluations (observed min lengths {mins}, census min {observed}).",
        "Disjoint donor/row presentation pairs from C29/C33. Companion words overlap YXXyXYxxx. Not the last unused listed donor.",
        "A hit would be a normal-closure candidate, not a C12 primitive. Hit witnesses persist factors and are replayed outside the scanner.",
        "Observed minimum length is a C38 census statistic, not a theorem and not a comparison with C29/C33.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = planted()
    print("c38 planted", ctrl["ok"], flush=True)
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
            f"c38 {name} products={rec['n_products']} min_len={rec['min_len']} "
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
    print("c38 YXXXyxYxx family")
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
    print("c38 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
