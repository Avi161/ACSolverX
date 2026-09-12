#!/usr/bin/env python3
"""C44: certified cyclic pair-length descent on listed U124 BEST pairs.

C44.1. Depth ≤ 2 in the C13 neighbourhood on the 36 μ-floor BEST pairs
(C28 scanned archival INITIAL, not these shorter spellings). Unique
exact-spelling children and grandchildren. Depth counts AC2 macro-steps,
not elementary moves.

C44.2. Restricted depth-3 corridor on the 47-row union of those 36 and
the 13 shortest BEST pairs (total ≤ 15). Completeness: all row-local
exact-spelling depth-2 states of cyclic total equal to the input total
are expanded once. Not full depth-3.

C43 is the leftover aca_43 ncl scanner; this file is not that census.

A length drop is a BEST-relative witness. Independent replay uses
greedy_tests.spec apply_move, not children_fast. Ledger: ordinary field
only if BEST=INITIAL; a μ-floor row is not an ordinary archival
certificate. aca_115 μ ≤ 12 is an AK(3) tripwire, not a solve.

Not a heap search. Not leftover 10M. Not ncl product-word length 11.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    cyc_reduce,
)
from experiments.greedy_tests.spec.moves import (  # noqa: E402
    apply_move,
    legacy_to_move,
)
from experiments.greedy_tests.spec.words import (  # noqa: E402
    reduce_word,
    str_to_word,
    word_to_str,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c28_depth2_ac2 as c28  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
DATA_INITIAL = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
JSON_PATH = OUT / "c44_best_length_descent.json"

BEST_SHA256 = (
    "8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3"
)
INITIAL_SHA256 = (
    "614bce2d3250a1acca81ec9de0fc0deb097eb74c4d56e6a9718985a150bb1d2c"
)

SHORT_IDS = (
    "aca_1",
    "aca_8",
    "aca_9",
    "aca_10",
    "aca_11",
    "aca_12",
    "aca_14",
    "aca_115",
    "aca_116",
    "aca_117",
    "aca_118",
    "aca_120",
    "aca_121",
)
FLOOR_IDS = (
    "aca_34",
    "aca_36",
    "aca_43",
    "aca_44",
    "aca_55",
    "aca_58",
    "aca_66",
    "aca_67",
    "aca_71",
    "aca_72",
    "aca_78",
    "aca_80",
    "aca_81",
    "aca_85",
    "aca_87",
    "aca_88",
    "aca_90",
    "aca_95",
    "aca_97",
    "aca_98",
    "aca_99",
    "aca_100",
    "aca_105",
    "aca_106",
    "aca_107",
    "aca_108",
    "aca_109",
    "aca_110",
    "aca_111",
    "aca_112",
    "aca_113",
    "aca_114",
    "aca_120",
    "aca_121",
    "aca_122",
    "aca_123",
)
LISTED_IDS = tuple(
    sorted(set(SHORT_IDS) | set(FLOOR_IDS), key=lambda s: int(s.split("_")[1]))
)
SHORT_LEN_MAX = 15
CORRIDOR_POS = ("xxy", "xYxY")
BUDGET_SECONDS = 50.0


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_macro_spec(r1: str, r2: str, move: dict) -> tuple[str, str]:
    """One AC2 macro-step via greedy_tests.spec, not children_fast."""
    rels = (str_to_word(r1), str_to_word(r2))
    mv = legacy_to_move(
        int(move["target"]),
        int(move["jsign"]),
        int(move["k1"]),
        int(move["k2"]),
    )
    raw = apply_move(rels, mv)
    return word_to_str(reduce_word(raw[0], True)), word_to_str(
        reduce_word(raw[1], True)
    )


def replay_macros_spec(
    r1: str, r2: str, moves: list[dict]
) -> dict:
    cur = (r1, r2)
    for move in moves:
        cur = apply_macro_spec(cur[0], cur[1], move)
        if not cur[0] or not cur[1]:
            return {
                "ok": False,
                "end_r1": cur[0],
                "end_r2": cur[1],
                "end_len": len(cur[0]) + len(cur[1]),
                "empty_relator": True,
                "canon": None,
            }
    return {
        "ok": True,
        "end_r1": cur[0],
        "end_r2": cur[1],
        "end_len": len(cyc_reduce(cur[0])) + len(cyc_reduce(cur[1])),
        "empty_relator": False,
        "canon": list(canon_pair(cur[0], cur[1])),
    }


def certify_drop(
    start: tuple[str, str],
    scanner_end: tuple[str, str],
    moves: list[dict],
) -> dict:
    replay = replay_macros_spec(start[0], start[1], moves)
    scanner_len = len(scanner_end[0]) + len(scanner_end[1])
    scanner_canon = list(canon_pair(*scanner_end))
    canon_ok = replay["canon"] == scanner_canon
    len_ok = replay["end_len"] == scanner_len
    start_len = len(start[0]) + len(start[1])
    dropped = scanner_len < start_len
    return {
        "independent_replay_ok": bool(
            replay["ok"] and canon_ok and len_ok and dropped
        ),
        "scanner_end_len": scanner_len,
        "spec_end_len": replay["end_len"],
        "canon_match": canon_ok,
        "spec_end": [replay["end_r1"], replay["end_r2"]],
        "n_ac2_macro_steps": len(moves),
        "not_three_elementary_moves": True,
    }


def load_tables() -> tuple[dict[str, dict], dict[str, dict]]:
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        best = {row["name"]: row for row in csv.DictReader(handle)}
    with DATA_INITIAL.open(newline="", encoding="utf-8") as handle:
        initial = {row["name"]: row for row in csv.DictReader(handle)}
    return best, initial


def provenance_of(name: str, best: dict, initial: dict) -> dict:
    b1, b2 = best[name]["r1"], best[name]["r2"]
    i1, i2 = initial[name]["r1"], initial[name]["r2"]
    same = (b1, b2) == (i1, i2)
    return {
        "best_equals_initial": same,
        "provenance": (
            "ordinary_displayed_initial" if same else "mu_floor_best_relative"
        ),
        "in_c44_1": name in FLOOR_IDS,
        "in_c44_2": name in LISTED_IDS,
        "in_short": name in SHORT_IDS,
    }


def scan_row(name: str, r1: str, r2: str, meta: dict) -> dict:
    r1 = cyc_reduce(r1)
    r2 = cyc_reduce(r2)
    base_len = len(r1) + len(r2)
    base_one = c28.one_occ_reduced(r1) or c28.one_occ_reduced(r2)
    base_tb = c28.two_block_reduced(r1) and c28.two_block_reduced(r2)
    d1 = c28.unique_children(r1, r2)
    n_d1_drop = n_d1_eq = n_d1_up = 0
    n_one = n_tb = 0
    hits: list[dict] = []
    best_child_len = base_len

    def consider(
        a: str,
        b: str,
        depth: int,
        moves: list[dict],
    ) -> None:
        nonlocal best_child_len, n_one, n_tb
        length = len(a) + len(b)
        dropped = length < base_len
        if dropped and length < best_child_len:
            best_child_len = length
        new_one = (not base_one) and (
            c28.one_occ_reduced(a) or c28.one_occ_reduced(b)
        )
        new_tb = (not base_tb) and (
            c28.two_block_reduced(a) and c28.two_block_reduced(b)
        )
        if new_one:
            n_one += 1
        if new_tb:
            n_tb += 1
        if not dropped:
            return
        cert = certify_drop((r1, r2), (a, b), moves)
        rec = {
            "depth_ac2_macro_steps": depth,
            "new_r1": a,
            "new_r2": b,
            "len": length,
            "drop": base_len - length,
            "moves": moves,
            "one_occurrence": c28.one_occ_reduced(a) or c28.one_occ_reduced(b),
            "two_block_both": c28.two_block_reduced(a)
            and c28.two_block_reduced(b),
            "leq_12": length <= 12,
            "ak3_tripwire": name == "aca_115" and length <= 12,
            "provenance": meta["provenance"],
            "best_equals_initial": meta["best_equals_initial"],
            "may_update_best_known": cert["independent_replay_ok"],
            "may_update_ordinary_certified": (
                cert["independent_replay_ok"] and meta["best_equals_initial"]
            ),
            "may_update_stable_certified": False,
            "independent_replay": cert,
        }
        hits.append(rec)

    for a, b, move1 in d1:
        length = len(a) + len(b)
        if length < base_len:
            n_d1_drop += 1
        elif length == base_len:
            n_d1_eq += 1
        else:
            n_d1_up += 1
        consider(a, b, 1, [move1])

    seen_d2: set[tuple[str, str]] = set()
    eq_d2: list[tuple[str, str, dict, dict]] = []
    n_d2_raw = n_d2_drop = n_d2_eq = n_d2_up = 0
    for a, b, move1 in d1:
        for c, d, move2 in c28.children_fast(a, b):
            n_d2_raw += 1
            key = (c, d)
            if key in seen_d2:
                continue
            seen_d2.add(key)
            length = len(c) + len(d)
            if length < base_len:
                n_d2_drop += 1
            elif length == base_len:
                n_d2_eq += 1
                eq_d2.append((c, d, move1, move2))
            else:
                n_d2_up += 1
            consider(c, d, 2, [move1, move2])

    seen_d3: set[tuple[str, str]] = set()
    n_d3_raw = n_d3_drop = n_d3_eq = n_d3_up = 0
    for c, d, move1, move2 in eq_d2:
        for e, f, move3 in c28.children_fast(c, d):
            n_d3_raw += 1
            key = (e, f)
            if key in seen_d3:
                continue
            seen_d3.add(key)
            length = len(e) + len(f)
            if length < base_len:
                n_d3_drop += 1
            elif length == base_len:
                n_d3_eq += 1
            else:
                n_d3_up += 1
            consider(e, f, 3, [move1, move2, move3])

    length_hits = [h for h in hits if h["independent_replay"]["independent_replay_ok"]]
    min_end = min((h["len"] for h in length_hits), default=base_len)
    return {
        "id": name,
        "tag": name,
        "in_len": base_len,
        "best_equals_initial": meta["best_equals_initial"],
        "provenance": meta["provenance"],
        "in_c44_1": meta["in_c44_1"],
        "in_c44_2": meta["in_c44_2"],
        "in_short": meta["in_short"],
        "n_d1_unique": len(d1),
        "n_d1_drop_unique": n_d1_drop,
        "n_d1_eq_unique": n_d1_eq,
        "n_d1_up_unique": n_d1_up,
        "n_d2_raw": n_d2_raw,
        "n_d2_unique": len(seen_d2),
        "n_d2_drop_unique": n_d2_drop,
        "n_d2_eq_unique": n_d2_eq,
        "n_d2_up_unique": n_d2_up,
        "n_d3_raw_from_eq": n_d3_raw,
        "n_d3_unique_from_eq": len(seen_d3),
        "n_d3_drop_unique": n_d3_drop,
        "n_d3_eq_unique": n_d3_eq,
        "n_d3_up_unique": n_d3_up,
        "n_new_one_occ": n_one,
        "n_new_two_block": n_tb,
        "best_child_len": best_child_len,
        "drop": base_len - best_child_len,
        "n_length_hits_replayed": len(length_hits),
        "min_replayed_len": min_end,
        "found_length_drop": bool(length_hits),
        "leq_12_hit": any(h["leq_12"] for h in length_hits),
        "ak3_tripwire": any(h["ak3_tripwire"] for h in length_hits),
        "hits": length_hits[:8],
        "corridor_completeness": (
            "All row-local exact-spelling depth-2 states of cyclic total "
            "equal to the input total were expanded once."
        ),
        "depth_counts_ac2_macro_steps": True,
        "not_full_depth_3": True,
    }


def planted() -> dict:
    hit = c28.scan_depth2("planted_x_xy", "x", "xy")
    miss = c28.scan_depth2("planted_x_y", "x", "y")
    agree = (
        c28.children_agree("x", "xy")
        and c28.children_agree("x", "y")
        and c28.children_agree(*CORRIDOR_POS)
    )
    pos_meta = {
        "best_equals_initial": True,
        "provenance": "ordinary_displayed_initial",
        "in_c44_1": False,
        "in_c44_2": True,
        "in_short": True,
    }
    pos = scan_row("planted_corridor", CORRIDOR_POS[0], CORRIDOR_POS[1], pos_meta)
    spec_ok = True
    for r1, r2 in (("x", "xy"), CORRIDOR_POS, ("YXXXYxx", "YYYYXyyyx")):
        for a, b, move in c28.unique_children(r1, r2)[:40]:
            sa, sb = apply_macro_spec(r1, r2, move)
            if canon_pair(sa, sb) != canon_pair(a, b):
                spec_ok = False
                break
        if not spec_ok:
            break
    pos_hits = pos["hits"]
    pos_ok = (
        pos["n_d1_drop_unique"] == 0
        and pos["n_d2_drop_unique"] == 0
        and pos["n_d3_drop_unique"] > 0
        and pos["found_length_drop"]
        and pos_hits
        and pos_hits[0]["independent_replay"]["independent_replay_ok"]
        and pos_hits[0]["depth_ac2_macro_steps"] == 3
        and pos["drop"] > 0
    )
    return {
        "hit_found": hit["drop"] > 0,
        "hit_depth": None if hit["hit"] is None else hit["hit"]["depth"],
        "miss_drop": miss["drop"],
        "children_fast_agrees": agree,
        "spec_replay_agrees_on_sample": spec_ok,
        "corridor_pos_ok": pos_ok,
        "corridor_pos_drop": pos["drop"],
        "corridor_pos_d3_drop": pos["n_d3_drop_unique"],
        "ok": (
            hit["drop"] > 0
            and miss["drop"] == 0
            and agree
            and spec_ok
            and pos_ok
        ),
        "independent_checker": False,
        "same_code_as_census": True,
        "positive_witness_uses_spec_replay": True,
        "note": (
            "Depth counts AC2 macro-steps. Corridor positive is "
            "⟨xxy, xYxY⟩. Spec apply_move is the independent drop replay."
        ),
    }


def aggregate(rows: list[dict | None]) -> dict:
    done = [row for row in rows if row is not None]
    floor_done = [row for row in done if row["in_c44_1"]]
    listed_done = [row for row in done if row["in_c44_2"]]
    drops = [row for row in done if row["found_length_drop"]]
    return {
        "n_listed": len(LISTED_IDS),
        "n_short": len(SHORT_IDS),
        "n_floor": len(FLOOR_IDS),
        "n_done": len(done),
        "n_floor_done": len(floor_done),
        "n_listed_done": len(listed_done),
        "c44_1_complete": len(floor_done) == len(FLOOR_IDS),
        "c44_2_complete": len(listed_done) == len(LISTED_IDS),
        "n_rows_with_replayed_drop": len(drops),
        "n_d1_drop_total": sum(row["n_d1_drop_unique"] for row in done),
        "n_d2_drop_total": sum(row["n_d2_drop_unique"] for row in done),
        "n_d3_drop_total": sum(row["n_d3_drop_unique"] for row in done),
        "n_d2_eq_total": sum(row["n_d2_eq_unique"] for row in done),
        "n_d2_unique_sum": sum(row["n_d2_unique"] for row in done),
        "n_d3_unique_from_eq_sum": sum(row["n_d3_unique_from_eq"] for row in done),
        "any_leq_12": any(row["leq_12_hit"] for row in done),
        "any_ak3_tripwire": any(row["ak3_tripwire"] for row in done),
        "drop_ids": [row["id"] for row in drops],
        "rows": rows,
    }


def summarize(ctrl: dict, agg: dict) -> dict:
    complete = bool(agg["c44_1_complete"] and agg["c44_2_complete"])
    return {
        "planted_ok": ctrl["ok"],
        "children_fast_agrees": ctrl["children_fast_agrees"],
        "spec_replay_agrees_on_sample": ctrl["spec_replay_agrees_on_sample"],
        "listed_ids": list(LISTED_IDS),
        "short_ids": list(SHORT_IDS),
        "floor_ids": list(FLOOR_IDS),
        "n_listed": len(LISTED_IDS),
        "best_sha256": BEST_SHA256,
        "initial_sha256": INITIAL_SHA256,
        "c44_1_complete": agg["c44_1_complete"],
        "c44_2_complete": agg["c44_2_complete"],
        "census_complete": complete,
        "n_done": agg["n_done"],
        "n_rows_with_replayed_drop": agg["n_rows_with_replayed_drop"],
        "n_d1_drop_total": agg["n_d1_drop_total"],
        "n_d2_drop_total": agg["n_d2_drop_total"],
        "n_d3_drop_total": agg["n_d3_drop_total"],
        "n_d2_eq_total": agg["n_d2_eq_total"],
        "n_d2_unique_sum": agg["n_d2_unique_sum"],
        "n_d3_unique_from_eq_sum": agg["n_d3_unique_from_eq_sum"],
        "any_leq_12": agg["any_leq_12"],
        "any_ak3_tripwire": agg["any_ak3_tripwire"],
        "drop_ids": agg["drop_ids"],
        "d2_counts_are_row_local_exact_spellings": True,
        "corridor_is_equal_length_d2_states": True,
        "not_full_depth_3": True,
        "depth_counts_ac2_macro_steps": True,
        "independent_checker": False,
        "positive_witness_independent_of_children_fast": True,
        "solved_u124": 0,
        "c10_finish": False,
        "not_ncl_product_length": True,
        "not_leftover_10m": True,
        "c43_is_aca43_ncl_not_this_census": True,
        "replay_kind": "single_resumed_census_plus_spec_replay_of_drops",
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "C44.1 is depth ≤ 2 on the 36 μ-floor BEST pairs. C28 used archival INITIAL.",
        "C44.2 expands each unique exact-spelling depth-2 state of cyclic total equal to the input total once. Not full depth-3.",
        "Depth counts AC2 macro-steps, not elementary moves.",
        "Length-drop witnesses are replayed with greedy_tests.spec apply_move, not children_fast.",
        "BEST=INITIAL drops may update ordinary certified length after replay. μ-floor drops are BEST-relative only.",
        "aca_115 μ ≤ 12 is an AK(3) tripwire. μ = 13 is never a removal. Order-120 is an integrity check, not a C10 exception.",
        "C43 is the leftover aca_43 ncl scanner. This file is C44.",
        "JSON is a resumed deterministic census. independent_checker=false for the negative. No U124 row is solved unless a non-tripwire μ ≤ 12 endpoint is replayed.",
    ]


def empty_report() -> dict:
    rows: list[dict | None] = [None] * len(LISTED_IDS)
    agg = aggregate(rows)
    ctrl = {
        "ok": False,
        "children_fast_agrees": False,
        "spec_replay_agrees_on_sample": False,
        "independent_checker": False,
    }
    return {
        "summary": summarize(ctrl, agg),
        "planted": ctrl,
        "listed": agg,
        "notes": [],
    }


def load_report() -> dict:
    if not JSON_PATH.exists():
        return empty_report()
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    rows = list((report.get("listed") or {}).get("rows") or [])
    while len(rows) < len(LISTED_IDS):
        rows.append(None)
    report["listed"] = aggregate(rows[: len(LISTED_IDS)])
    return report


def write_report(report: dict) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def assert_inputs() -> None:
    got_best = file_sha256(DATA_BEST)
    got_init = file_sha256(DATA_INITIAL)
    if got_best != BEST_SHA256:
        raise RuntimeError(f"best sha256 mismatch: {got_best}")
    if got_init != INITIAL_SHA256:
        raise RuntimeError(f"initial sha256 mismatch: {got_init}")
    if len(LISTED_IDS) != 47:
        raise RuntimeError("listed id count")
    if len(SHORT_IDS) != 13 or len(FLOOR_IDS) != 36:
        raise RuntimeError("short/floor id counts")
    if set(SHORT_IDS) | set(FLOOR_IDS) != set(LISTED_IDS):
        raise RuntimeError("listed ids are not the union")


def main(budget: float = BUDGET_SECONDS) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    assert_inputs()
    deadline = time.perf_counter() + budget
    best, initial = load_tables()
    for name in SHORT_IDS:
        if len(best[name]["r1"]) + len(best[name]["r2"]) > SHORT_LEN_MAX:
            raise RuntimeError(f"{name} exceeds short length cap")
    report = load_report()
    ctrl = planted()
    report["planted"] = ctrl
    print("c44 planted", ctrl["ok"], flush=True)

    rows = report["listed"]["rows"]
    paused = False
    for i, name in enumerate(LISTED_IDS):
        if rows[i] is not None:
            continue
        if time.perf_counter() >= deadline:
            paused = True
            break
        meta = provenance_of(name, best, initial)
        rec = scan_row(name, best[name]["r1"], best[name]["r2"], meta)
        rows[i] = rec
        print(
            f"c44 {rec['id']} prov={rec['provenance']} in_len={rec['in_len']} "
            f"d1={rec['n_d1_unique']} d2u={rec['n_d2_unique']} "
            f"d2eq={rec['n_d2_eq_unique']} d3u={rec['n_d3_unique_from_eq']} "
            f"d1drop={rec['n_d1_drop_unique']} d2drop={rec['n_d2_drop_unique']} "
            f"d3drop={rec['n_d3_drop_unique']} found={rec['found_length_drop']}",
            flush=True,
        )
        report["listed"] = aggregate(rows)
        report["summary"] = summarize(ctrl, report["listed"])
        write_report(report)

    report["listed"] = aggregate(rows)
    report["summary"] = summarize(ctrl, report["listed"])
    report["notes"] = notes_from_summary(report["summary"])
    write_report(report)
    status = "complete" if report["summary"]["census_complete"] else "paused"
    print("c44 best-pair length descent", status)
    print(json.dumps(report["summary"], indent=2))
    print(f"wrote {JSON_PATH}")
    if paused:
        print("paused: re-run until census_complete")
    return report


def annotate_existing() -> dict:
    assert_inputs()
    report = load_report()
    ctrl = planted()
    report["planted"] = ctrl
    report["listed"] = aggregate(report["listed"]["rows"])
    report["summary"] = summarize(ctrl, report["listed"])
    report["notes"] = notes_from_summary(report["summary"])
    write_report(report)
    print("c44 annotate-existing")
    print(json.dumps(report["summary"], indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
