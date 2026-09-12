#!/usr/bin/env python3
"""C35: YXXXyxx family — x ≡ D^{-1} (L1=1), then k=3 nine-config products.

Last unused length-7 donor in the listed shared-donor inventory.
D = YXXXyxx abelianizes to (−1, 0). For a companion C_ab=(p,q) the pair
exponent matrix has det(D,C)=−q; if that matrix is unimodular then q=±1
and a D_ab + b C_ab = (1,0) uniquely (a,b)=(−1,0). Same combo for the
one-letter class {x, Yxy, yxY}. Even k is abelian-impossible. k=1 is
blocked by |D|=7. k=3 is the C23/C25 nine signed-type configs with
R^+ = D^{-1} and S = C.

This word already appears in C22.6 as the free identity
YXXXyxYx · (x^{-1} y x) = YXXXyxx = P_{m,+1} row 1. That identity is not
an AC2 and is not this census.

A hit is a normal-closure candidate, not a C12 primitive. If a hit
occurs, the ordered signed types, three factor words, and conjugators
are persisted and the product is replayed.

Not a heap search. Not a U124 solve unless a witness is found and given
an explicit AC1–AC5 path.
"""
from __future__ import annotations

import csv
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
import c24_even_k as c24  # noqa: E402
import c29_yxx_family as c29  # noqa: E402
import c30_x_exact_l1 as c30  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c35_yxxx_family.json"

DONOR = "YXXXyxx"
ALPHABET = "xXyY"
POSITIVE_X = c30.POSITIVE_X
ROW_IDS = (
    "aca_9",
    "aca_10",
    "aca_11",
    "aca_12",
    "aca_116",
    "aca_117",
)
HIT_WITNESS_KEYS = (
    "word",
    "len",
    "signed_types",
    "shape",
    "factors",
    "conjugators",
    "replay_free_reduce_equals_target",
)


def x_combo_from_c_exp(p: int, q: int) -> tuple[int, int, int]:
    """Unique x combo against D_ab=(-1,0) when the pair matrix is unimodular."""
    det = -q
    if abs(det) != 1:
        raise ValueError("pair (D,C) exponent matrix is not unimodular")
    return -1, 0, 1


def conjugator_map(donor: str, conjugators: list[str]) -> dict[str, str]:
    first: dict[str, str] = {}
    for g in conjugators:
        word = c22.conjugate(donor, g)
        if word and word not in first:
            first[word] = g
    return first


def labeled_three_factor_configs(
    r_plus: list[str],
    r_minus: list[str],
    s_plus: list[str],
    s_minus: list[str],
) -> list[tuple[list[str], str, list[list[str]]]]:
    labeled: list[tuple[list[str], str, list[list[str]]]] = []
    for pos in range(3):
        types = ["R+", "R+", "R+"]
        types[pos] = "R-"
        lists = [r_plus, r_plus, r_plus]
        lists[pos] = r_minus
        labeled.append((types, "A", lists))
    for pos in range(3):
        others = [i for i in range(3) if i != pos]
        for order_types, order_lists in (
            (("S+", "S-"), (s_plus, s_minus)),
            (("S-", "S+"), (s_minus, s_plus)),
        ):
            types = ["R+", "R+", "R+"]
            types[others[0]], types[others[1]] = order_types
            lists = [r_plus, r_plus, r_plus]
            lists[others[0]], lists[others[1]] = order_lists
            labeled.append((types, "B", lists))
    return labeled


C35_ORIENTATION = {
    "Rplus": "D^{-1}",
    "Rminus": "D",
    "Splus": "C",
    "Sminus": "C^{-1}",
}
C31_ORIENTATION = {
    "Rplus": "C^{-1}",
    "Rminus": "C",
    "Splus": "D",
    "Sminus": "D^{-1}",
}


def reconstruct_hit(hit: dict, bases: dict[str, str]) -> dict:
    """Replay a hit outside the scanner loop: rebuild each conjugate, then the product."""
    rebuilt = []
    consistent = True
    for typ, factor, g in zip(hit["signed_types"], hit["factors"], hit["conjugators"]):
        word = c22.conjugate(bases[typ], g)
        rebuilt.append(word)
        if word != factor:
            consistent = False
    replay = free_reduce("".join(rebuilt))
    return {
        "rebuilt_factors": rebuilt,
        "factor_conjugator_consistent": consistent,
        "replay_outside_scanner": replay,
        "replay_equals_hit_word": replay == hit["word"],
        "ok": consistent and replay == hit["word"],
        "independent_checker": False,
    }


def scan_three_against_witness(
    r_plus_word: str,
    r_minus_word: str,
    s_plus_word: str,
    s_minus_word: str,
    conjugators: list[str],
    targets: set[str],
    orientation: dict[str, str] | None = None,
) -> dict:
    r_plus = c23.unique_conjugates(r_plus_word, conjugators)
    r_minus = c23.unique_conjugates(r_minus_word, conjugators)
    s_plus = c23.unique_conjugates(s_plus_word, conjugators)
    s_minus = c23.unique_conjugates(s_minus_word, conjugators)
    unlabeled = c23.three_factor_configs(r_plus, r_minus, s_plus, s_minus)
    labeled = labeled_three_factor_configs(r_plus, r_minus, s_plus, s_minus)
    if [lists for _types, _shape, lists in labeled] != unlabeled:
        raise RuntimeError("C35 config order diverged from C23.three_factor_configs")
    gmap = {
        "R+": conjugator_map(r_plus_word, conjugators),
        "R-": conjugator_map(r_minus_word, conjugators),
        "S+": conjugator_map(s_plus_word, conjugators),
        "S-": conjugator_map(s_minus_word, conjugators),
    }
    hit = None
    min_len = None
    n_products = 0
    n_len_le_3 = 0
    for types, shape, lists in labeled:
        for factors in product(*lists):
            word = free_reduce("".join(factors))
            n_products += 1
            length = len(word)
            if min_len is None or length < min_len:
                min_len = length
            if length <= 3:
                n_len_le_3 += 1
            if word in targets and hit is None:
                conjugators_used = [gmap[types[i]][factors[i]] for i in range(3)]
                replay = free_reduce("".join(factors))
                hit = {
                    "word": word,
                    "len": length,
                    "signed_types": types,
                    "shape": shape,
                    "factors": list(factors),
                    "conjugators": conjugators_used,
                    "replay_free_reduce_equals_target": replay == word,
                }
    return {
        "n_conjugators": len(conjugators),
        "n_Rplus": len(r_plus),
        "n_Rminus": len(r_minus),
        "n_Splus": len(s_plus),
        "n_Sminus": len(s_minus),
        "n_products": n_products,
        "min_len": min_len,
        "n_len_le_3": n_len_le_3,
        "hit": hit,
        "found": hit is not None,
        "pool": "nine_signed_type_configs_per_type_dedup",
        "n_configs": 9,
        "negative_targets_via_inversion": True,
        "hit_witness_keys": list(HIT_WITNESS_KEYS),
        "orientation": dict(orientation or C35_ORIENTATION),
    }


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
    p, q = ec
    pair_det = ed[0] * ec[1] - ed[1] * ec[0]
    a, b, l1 = x_combo_from_c_exp(p, q)
    rows = {}
    for word in ("x", "Yxy", "yxY", "y"):
        target = c22.exp_on(word, "xy")
        sol = c22.solve_2x2(ed[0], ec[0], ed[1], ec[1], target[0], target[1])
        rows[word] = {"exp": list(target), "combo": sol, "L1": c24.l1_combo(sol)}
    x = rows["x"]
    if x["combo"].get("a") != a or x["combo"].get("b") != b or x["L1"] != l1:
        raise ValueError(f"{name}: combo mismatch {x['combo']} vs {(a, b)}")
    return {
        "id": name,
        "donor": donor,
        "companion": companion,
        "D_exp": list(ed),
        "C_exp": list(ec),
        "pair_det": pair_det,
        "pair_det_equals_minus_C_y": pair_det == -q,
        "pair_exponent_matrix_unimodular": abs(pair_det) == 1,
        "D_cyc_len": len(cyc_reduce(donor)),
        "C_cyc_len": len(cyc_reduce(companion)),
        "x_combo": x["combo"],
        "x_L1": x["L1"],
        "Yxy_same_as_x": rows["Yxy"]["combo"] == x["combo"],
        "yxY_same_as_x": rows["yxY"]["combo"] == x["combo"],
        "y_combo": rows["y"]["combo"],
        "y_L1": rows["y"]["L1"],
        "k1_len_obstruction": len(cyc_reduce(donor)) > 1,
        "even_k_forbidden": x["L1"] == 1,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    rec = scan_three_against_witness(
        inv(DONOR),
        DONOR,
        companion,
        inv(companion),
        conjugators,
        set(POSITIVE_X),
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
            "targets": list(POSITIVE_X),
        }
    )
    return rec


def planted() -> dict:
    hit = scan_three_against_witness("x", "X", "y", "Y", [""], {"x"})
    miss = scan_three_against_witness("x", "X", "y", "Y", [""], {"u"})
    expected = c29.typed_nine_size(1, 1, 1, 1)
    witness = hit["hit"]
    witness_ok = (
        witness is not None
        and witness["word"] == "x"
        and witness["replay_free_reduce_equals_target"]
        and len(witness["factors"]) == 3
        and len(witness["conjugators"]) == 3
        and free_reduce("".join(witness["factors"])) == "x"
        and set(witness.keys()) >= set(HIT_WITNESS_KEYS)
    )
    return {
        "n_products_hit": hit["n_products"],
        "n_typed": expected,
        "hit": witness,
        "miss_found": miss["found"],
        "witness_ok": witness_ok,
        "ok": (
            hit["found"]
            and not miss["found"]
            and hit["n_products"] == expected
            and miss["n_products"] == expected
            and witness_ok
        ),
        "independent_checker": False,
        "same_code_as_census": True,
    }


def c22_6_note() -> dict:
    product = free_reduce("YXXXyxYx" + "Xyx")
    return {
        "identity": "YXXXyxYx · Xyx = YXXXyxx = P_{m,+1} row 1",
        "product": product,
        "product_is_donor": product == DONOR,
        "Xyx_is_not_a_relator": True,
        "not_an_ac2": True,
        "c35_donor_is_that_word": True,
        "note": (
            "C22.6 is a free-group identity on the C15 donor. C35 treats the "
            "same spelling as a stored best-table donor on six other rows."
        ),
    }


def summarize(abelian: list[dict], three: list[dict], ctrl: dict, bridge: dict) -> dict:
    return {
        "n_rows": len(abelian),
        "donor": DONOR,
        "all_D_exp_minus_one_zero": all(row["D_exp"] == [-1, 0] for row in abelian),
        "all_D_cyc_len_7": all(row["D_cyc_len"] == 7 for row in abelian),
        "all_pair_exponent_matrix_unimodular": all(
            row["pair_exponent_matrix_unimodular"] for row in abelian
        ),
        "all_pair_det_equals_minus_C_y": all(
            row["pair_det_equals_minus_C_y"] for row in abelian
        ),
        "all_C_y_exp_minus_one": all(row["C_exp"][1] == -1 for row in abelian),
        "all_x_L1_1": all(row["x_L1"] == 1 for row in abelian),
        "all_x_combo_minus_one_zero": all(
            row["x_combo"].get("a") == -1 and row["x_combo"].get("b") == 0
            for row in abelian
        ),
        "all_Yxy_same_as_x": all(row["Yxy_same_as_x"] for row in abelian),
        "all_yxY_same_as_x": all(row["yxY_same_as_x"] for row in abelian),
        "all_k1_len_block": all(row["k1_len_obstruction"] for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": sum(row["n_products"] for row in three),
        "three_n_typed_tuples": sum(row["n_typed_tuples"] for row in three),
        "three_products_equal_typed": all(row["n_products_equals_typed"] for row in three),
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in three),
        "counts_are_nine_config_cartesian": True,
        "last_unused_len7_in_listed_shared_donor_inventory": True,
        "yxxx_appears_in_c22_6": True,
        "c22_6_is_free_identity_not_ac2": bridge["not_an_ac2"] and bridge["product_is_donor"],
        "not_a_c29_or_c33_rerun": True,
        "not_a_c30_or_c34_rerun": True,
        "pair_unimodularity_is_of_DC_matrix": True,
        "hit_witness_records_factors_and_conjugators": True,
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "D = YXXXyxx has exponent (−1,0). Pair det(D,C)=−q; unimodular pair matrix forces q=±1 and unique x-combo (−1, 0), L1=1.",
        "Even k is abelian-impossible. k=1 is blocked by |D|=7. k=3 is the nine signed-type configs of C23/C25 with R^+=D^{-1}, S=C.",
        "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^3.",
        "Last unused length-7 donor in the listed shared-donor inventory. The spelling already appears in C22.6; that free identity is not an AC2.",
        "A hit would be a normal-closure candidate, not a C12 primitive. Hit witnesses persist signed types, factors, conjugators, and a free-reduce replay.",
        "Observed minimum length is a C35 census statistic, not a theorem and not a comparison with C29/C33/C34.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = planted()
    print("c35 planted", ctrl["ok"], flush=True)
    bridge = c22_6_note()
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
            f"c35 {name} products={rec['n_products']} min_len={rec['min_len']} "
            f"found={rec['found']}",
            flush=True,
        )
    summary = summarize(abelian, three, ctrl, bridge)
    report = {
        "summary": summary,
        "planted": ctrl,
        "c22_6": bridge,
        "abelian": abelian,
        "three_factor": three,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c35 YXXXyxx family")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = planted()
    bridge = c22_6_note()
    summary = summarize(report["abelian"], report["three_factor"], ctrl, bridge)
    report["summary"] = summary
    report["planted"] = ctrl
    report["c22_6"] = bridge
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c35 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
