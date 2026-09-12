#!/usr/bin/env python3
"""C42: one YYXXXyxx row with y ≡ C^{-1} in abelianization (L1=1), then k=3 ncl.

Listed shared-donor D = YYXXXyxx, exponent (−1,−1), cyclic length 8.
Only aca_38 has C_ab=(0,-1). On that listed row, y and {Xyx, xyX} have
unique combination (0,-1) in abelianization, so L1=1 and y ≡ C^{-1}
abelianly. This is not free equality, not every companion of D, not a
six-row YYXXXyxx census, and not lumped with C40, C41, aca_56, or aca_57.

The companion is consecutive BS(4,5). That is classification, not a
C15/C31 rerun.

Even k is abelian-impossible. k=1 is blocked by |C|=11. k=3 is the
C23/C25 nine signed-type configs with R^+ = C^{-1} and S = D (C31
orientation; not C35, not C40).

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
import c35_yxxx_family as c35  # noqa: E402
import c40_yyxxxyxx_x_eq_c as c40  # noqa: E402
from u124_census import bs_mm1_shape  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c42_yyxxxyxx_y_eq_cinv.json"

DONOR = "YYXXXyxx"
ALPHABET = "xXyY"
POSITIVE_Y = c29.POSITIVE_Y
ORIENTATION = c35.C31_ORIENTATION
if ORIENTATION != c35.C31_ORIENTATION:
    raise RuntimeError("C42 must use C31 orientation")
if ORIENTATION == c35.C35_ORIENTATION or ORIENTATION == c40.C40_ORIENTATION:
    raise RuntimeError("C42 must not use C35 or C40 orientation")
ROW_IDS = ("aca_38",)
EXPECTED_COMPANIONS = {
    "aca_38": "YYYYYXyyyyx",
}
EXPECTED_C_EXP = {
    "aca_38": (0, -1),
}
EXPECTED_C_CYC_LEN = {
    "aca_38": 11,
}
EXPECTED_COUNTS = {
    "aca_38": (26, 26, 29, 29),
}
EXPECTED_TYPED = {
    "aca_38": 183924,
}
EXPECTED_TYPED_TOTAL = 183924
EXPECTED_BS_M = 4


def y_combo_from_listed_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique y combo against D_ab=(-1,-1) when C_ab=(0,-1).

    Not a claim about every companion of this donor.
    """
    if (p, q) != (0, -1):
        raise ValueError("C42 combo (0,-1) is for listed C_ab=(0,-1) companion")
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
    if name not in ROW_IDS:
        raise ValueError(f"{name} is not a listed C42 row")
    if companion != EXPECTED_COMPANIONS[name]:
        raise ValueError(f"{name}: companion {companion} != {EXPECTED_COMPANIONS[name]}")
    donor = DONOR
    ed, ec = c22.exp_on(donor, "xy"), c22.exp_on(companion, "xy")
    if tuple(ed) != (-1, -1):
        raise ValueError(f"{name}: D_exp {ed} != (-1,-1)")
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
    x = rows["x"]
    if x["combo"].get("a") != -1 or x["combo"].get("b") != 1 or x["L1"] != 2:
        raise ValueError(f"{name}: leftover x combo mismatch {x['combo']}")
    pair_det = ed[0] * ec[1] - ed[1] * ec[0]
    if pair_det != 1:
        raise ValueError(f"{name}: pair_det {pair_det} != 1")
    c_cyc = len(cyc_reduce(companion))
    if c_cyc != EXPECTED_C_CYC_LEN[name]:
        raise ValueError(f"{name}: C_cyc_len {c_cyc} != {EXPECTED_C_CYC_LEN[name]}")
    bs, m = bs_mm1_shape(companion)
    if not bs or m != EXPECTED_BS_M:
        raise ValueError(f"{name}: companion is not consecutive BS({EXPECTED_BS_M},{EXPECTED_BS_M + 1})")
    return {
        "id": name,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "C_exp": list(ec),
        "pair_det": pair_det,
        "pair_exponent_matrix_unimodular": abs(pair_det) == 1,
        "D_cyc_len": len(cyc_reduce(donor)),
        "C_cyc_len": c_cyc,
        "y_combo": y["combo"],
        "y_L1": y["L1"],
        "y_equiv_Cinv_in_abelianization": True,
        "not_free_equality_y_equals_Cinv": True,
        "Xyx_same_as_y": rows["Xyx"]["combo"] == y["combo"],
        "xyX_same_as_y": rows["xyX"]["combo"] == y["combo"],
        "x_combo": x["combo"],
        "x_L1": x["L1"],
        "x_exact_l1_not_part_of_c42": True,
        "k1_len_obstruction": c_cyc >= 9,
        "k1_blocked_by_C_cyc_len_11": c_cyc == 11,
        "even_k_forbidden": y["L1"] == 1,
        "companion_bs_mm1": bs,
        "companion_bs_m": m,
        "bs_is_classification_not_a_c15_or_c31_rerun": True,
        "combo_restricted_to_listed_C_ab": True,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    if name not in ROW_IDS:
        raise ValueError(f"{name} is not a listed C42 row")
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
    if rec["orientation"] != c35.C31_ORIENTATION:
        raise RuntimeError(f"{name}: scanner lost C31 orientation {rec['orientation']}")
    if rec["orientation"] in (c35.C35_ORIENTATION, c40.C40_ORIENTATION):
        raise RuntimeError(f"{name}: scanner used C35 or C40 orientation")
    counts = (rec["n_Rplus"], rec["n_Rminus"], rec["n_Splus"], rec["n_Sminus"])
    if counts != EXPECTED_COUNTS[name]:
        raise RuntimeError(f"{name}: counts {counts} != {EXPECTED_COUNTS[name]}")
    typed = c29.typed_nine_size(*counts)
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
            "R+": inv(companion),
            "R-": companion,
            "S+": DONOR,
            "S-": inv(DONOR),
        }
        rec["hit_replay_outside_scanner"] = c35.reconstruct_hit(rec["hit"], bases)
        if not rec["hit_replay_outside_scanner"]["ok"]:
            raise RuntimeError(f"{name}: hit replay failed")
        if rec["hit"]["word"] not in set(POSITIVE_Y):
            raise RuntimeError(f"{name}: hit word not a target")
    else:
        rec["hit_replay_outside_scanner"] = None
    return rec


def planted() -> dict:
    rec = c35.scan_three_against_witness(
        "y", "Y", "x", "X", [""], {"y"}, orientation=ORIENTATION
    )
    if rec["orientation"] != c35.C31_ORIENTATION:
        raise RuntimeError("planted lost C31 orientation")
    if rec["orientation"] in (c35.C35_ORIENTATION, c40.C40_ORIENTATION):
        raise RuntimeError("planted used C35 or C40 orientation")
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
            and rec["orientation"] == c35.C31_ORIENTATION
        ),
        "independent_checker": False,
        "same_code_as_census": True,
    }


def summarize(abelian: list[dict], three: list[dict], ctrl: dict) -> dict:
    n_typed = sum(row["n_typed_tuples"] for row in three)
    n_products = sum(row["n_products"] for row in three)
    if n_typed != EXPECTED_TYPED_TOTAL or n_products != EXPECTED_TYPED_TOTAL:
        raise RuntimeError(
            f"C42 typed/product totals {n_typed}/{n_products} != {EXPECTED_TYPED_TOTAL}"
        )
    if not all(row["n_products_equals_typed"] for row in three):
        raise RuntimeError("C42 per-row n_products != n_typed_tuples")
    ids = [row["id"] for row in abelian]
    if tuple(ids) != ROW_IDS:
        raise RuntimeError(f"C42 row ids {ids} != {ROW_IDS}")
    return {
        "n_rows": len(abelian),
        "donor": DONOR,
        "all_D_exp_minus_one_minus_one": all(row["D_exp"] == [-1, -1] for row in abelian),
        "all_C_exp_zero_minus_one": all(row["C_exp"] == [0, -1] for row in abelian),
        "all_pair_det_one": all(row["pair_det"] == 1 for row in abelian),
        "all_pair_exponent_matrix_unimodular": all(
            row["pair_exponent_matrix_unimodular"] for row in abelian
        ),
        "C_cyc_lens": [row["C_cyc_len"] for row in abelian],
        "all_k1_blocked_by_C_cyc_len_11": all(
            row["k1_blocked_by_C_cyc_len_11"] for row in abelian
        ),
        "all_k1_blocked_by_C_cyc_len_ge_9": all(row["k1_len_obstruction"] for row in abelian),
        "all_y_L1_1": all(row["y_L1"] == 1 for row in abelian),
        "all_y_combo_zero_minus_one": all(
            row["y_combo"].get("a") == 0 and row["y_combo"].get("b") == -1
            for row in abelian
        ),
        "all_y_equiv_Cinv_in_abelianization": all(
            row["y_equiv_Cinv_in_abelianization"] for row in abelian
        ),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_x_L1_2": all(row["x_L1"] == 2 for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "all_companion_bs_mm1_m4": all(
            row["companion_bs_mm1"] and row["companion_bs_m"] == EXPECTED_BS_M
            for row in abelian
        ),
        "bs_is_classification_not_a_c15_or_c31_rerun": True,
        "combo_restricted_to_listed_C_ab": True,
        "not_six_row_yyxxxyxx_census": True,
        "not_lumped_with_c40_or_c41": True,
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": n_products,
        "three_n_typed_tuples": n_typed,
        "three_products_equal_typed": True,
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_min_lens": [row["min_len"] for row in three],
        "three_all_orientation_c31": all(
            row["orientation"] == c35.C31_ORIENTATION for row in three
        ),
        "three_none_orientation_c35_or_c40": all(
            row["orientation"] not in (c35.C35_ORIENTATION, c40.C40_ORIENTATION)
            for row in three
        ),
        "counts_are_nine_config_cartesian": True,
        "completeness_is_all_typed_tuples_in_this_bounded_pool": True,
        "cartesian_cap_is_per_cell": True,
        "disjointness_relative_to_prior_typed_donor_family_censuses": True,
        "c28_touched_rows_under_different_predicate": True,
        "equal_typed_sizes_do_not_identify_censuses": True,
        "x_exact_l1_not_part_of_c42": True,
        "hit_witness_records_factors_and_conjugators": True,
        "hit_replay_outside_scanner_capability": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    mins = summary.get("three_min_lens") or []
    observed = summary.get("three_min_len")
    return [
        "D = YYXXXyxx has exponent (−1,−1). On listed C_ab=(0,-1) row aca_38, y has unique combination (0,-1), L1=1, and y ≡ C^{-1} in abelianization.",
        "That is not free equality y=C^{-1}, not every companion of D, not a six-row YYXXXyxx census, and not lumped with C40 or C41.",
        "Companion is consecutive BS(4,5); that is classification, not a C15/C31 rerun.",
        "Even k is abelian-impossible. k=1 is blocked by |C|=11. k=3 uses C31 orientation R^+=C^{-1}, S=D.",
        f"Typed Cartesian total {summary['three_n_typed_tuples']} is nine-config 3|R+|²|R−|+6|R+||S+||S−|, not |F|^3.",
        f"Enumerated {summary['three_n_products']} tuple evaluations (observed min lengths {mins}, census min {observed}).",
        "Completeness is all 183,924 typed tuples in this bounded pool.",
        "Disjointness is relative to prior typed donor-family censuses. C28 touched this row under a different predicate.",
        "Equal typed size 183,924 does not identify C40 aca_95.",
        "A hit would be a normal-closure candidate, not a C12 primitive. Hit witnesses persist factors and are replayed outside the scanner.",
        "JSON hit_replay_outside_scanner_capability is capability, not a census hit.",
        "Observed minimum length is a C42 census statistic, not a theorem and not a comparison with C31/C36/C40/C41.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = planted()
    print("c42 planted", ctrl["ok"], flush=True)
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
            f"c42 {name} products={rec['n_products']} min_len={rec['min_len']} "
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
    print("c42 YYXXXyxx y ≡ C^{-1} in abelianization")
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
    print("c42 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
