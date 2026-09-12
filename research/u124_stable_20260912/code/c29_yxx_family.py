#!/usr/bin/env python3
"""C29: YXXyxYx family — y ≡ D^{-1} (L1=1), then k=3 nine-config products.

The largest unused shared-donor block on the best table is eleven rows
with compact donor D = YXXyxYx, exponent (0,−1). For every unimodular
companion, y and the exponent-(0,1) one-letter class {y, Xyx, xyX} have
the unique combination (−1, 0) against (D, C), so L1=1. Even k is
abelian-impossible. k=1 is a length block (|D|=7). k=3 is the first
extra cancelling pair: the C23/C25 nine signed-type configs with
R^+ = D^{-1} and S = C.

A hit is a normal-closure candidate, not a C12 primitive. The free
identity D · (x^{-1} y x) = YXXyxx is not an AC2: Xyx is not a donor.

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
import c25_alt_words as c25  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c29_yxx_family.json"

DONOR = "YXXyxYx"
ALPHABET = "xXyY"
POSITIVE_Y = ("y", "Xyx", "xyX")
ROW_IDS = (
    "aca_0",
    "aca_3",
    "aca_34",
    "aca_36",
    "aca_53",
    "aca_58",
    "aca_81",
    "aca_97",
    "aca_118",
    "aca_119",
    "aca_120",
)
P_FLOOR_IDS = ("aca_120", "aca_34", "aca_58", "aca_81", "aca_97")


def typed_nine_size(n_rp: int, n_rm: int, n_sp: int, n_sm: int) -> int:
    type_a = 3 * (n_rp ** 2) * n_rm
    type_b = 6 * n_rp * n_sp * n_sm
    return type_a + type_b


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
        "is_p_floor_companion": name in P_FLOOR_IDS,
        "targets": rows,
    }


def three_factor_row(name: str, companion: str) -> dict:
    conjugators = c22.short_conjugators([DONOR, companion], ALPHABET, 1)
    rec = c25.scan_three_against(
        inv(DONOR),
        DONOR,
        companion,
        inv(companion),
        conjugators,
        set(POSITIVE_Y),
    )
    typed = typed_nine_size(
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


def free_bridge() -> dict:
    product = free_reduce(DONOR + "Xyx")
    return {
        "identity": "YXXyxYx · Xyx = YXXyxx",
        "product": product,
        "product_is_YXXyxx": product == "YXXyxx",
        "Xyx_is_not_a_relator": True,
        "not_an_ac2": True,
        "note": (
            "Same caveat as C22.6: the conjugator x^{-1}yx is not an AC donor, "
            "so this free identity is not a depth-1 AC2."
        ),
    }


def planted() -> dict:
    pools = {"Rp": ["y"], "Rm": ["Y"], "Sp": ["x"], "Sm": ["X"]}
    lists_hit = c23.three_factor_configs(["y"], ["Y"], ["x"], ["X"])
    hit = None
    miss = None
    n = 0
    for lists in lists_hit:
        for parts in product(*lists):
            word = free_reduce("".join(parts))
            n += 1
            if word == "y" and hit is None:
                hit = {"word": word, "parts": list(parts)}
            if word == "u":
                miss = word
    expected = typed_nine_size(1, 1, 1, 1)
    return {
        "n_products": n,
        "n_typed": expected,
        "hit": hit,
        "miss": miss,
        "ok": hit is not None and miss is None and n == expected,
        "independent_checker": False,
        "same_code_as_census": True,
    }


def summarize(abelian: list[dict], three: list[dict], ctrl: dict, bridge: dict) -> dict:
    return {
        "n_rows": len(abelian),
        "all_y_L1_1": all(row["y_L1"] == 1 for row in abelian),
        "all_y_combo_minus_one_zero": all(
            row["y_combo"].get("a") == -1 and row["y_combo"].get("b") == 0
            for row in abelian
        ),
        "all_Xyx_same_as_y": all(row["Xyx_same_as_y"] for row in abelian),
        "all_xyX_same_as_y": all(row["xyX_same_as_y"] for row in abelian),
        "all_k1_len_block": all(row["k1_len_obstruction"] for row in abelian),
        "all_even_k_forbidden": all(row["even_k_forbidden"] for row in abelian),
        "n_p_floor_companions": sum(1 for row in abelian if row["is_p_floor_companion"]),
        "three_any_hit": any(row["found"] for row in three),
        "three_n_products": sum(row["n_products"] for row in three),
        "three_n_typed_tuples": sum(row["n_typed_tuples"] for row in three),
        "three_products_equal_typed": all(row["n_products_equals_typed"] for row in three),
        "three_min_len": min((row["min_len"] or 0) for row in three) if three else None,
        "three_all_min_len_ge_7": all((row["min_len"] or 0) >= 7 for row in three),
        "counts_are_nine_config_cartesian": True,
        "bridge_ok": bridge["product_is_YXXyxx"] and bridge["not_an_ac2"],
        "planted_ok": ctrl["ok"],
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "D = YXXyxYx has exponent (0,-1). On every unimodular companion, y has unique combination (−1, 0), L1=1.",
        "Even k is abelian-impossible. k=1 is blocked by |D|=7. k=3 is the nine signed-type configs of C23/C25.",
        "Counts are typed Cartesian sizes after per-type unique conjugates, not |F|^3.",
        "A hit would be a normal-closure candidate, not a C12 primitive. Five companions are C7 Aut-minimal P floors; that is not a solve.",
        "D · Xyx = YXXyxx is a free identity, not an AC2.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
    ]


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    best = load_best()
    ctrl = planted()
    print("c29 planted", ctrl["ok"], flush=True)
    bridge = free_bridge()
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
            f"c29 {name} products={rec['n_products']} min_len={rec['min_len']} "
            f"found={rec['found']}",
            flush=True,
        )
    summary = summarize(abelian, three, ctrl, bridge)
    report = {
        "summary": summary,
        "planted": ctrl,
        "free_bridge": bridge,
        "abelian": abelian,
        "three_factor": three,
        "notes": notes_from_summary(summary),
    }
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c29 YXXyxYx family")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    ctrl = planted()
    bridge = free_bridge()
    summary = summarize(report["abelian"], report["three_factor"], ctrl, bridge)
    report["summary"] = summary
    report["planted"] = ctrl
    report["free_bridge"] = bridge
    report["notes"] = notes_from_summary(summary)
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c29 annotate-existing")
    print(json.dumps(summary, indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
