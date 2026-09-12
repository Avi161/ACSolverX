#!/usr/bin/env python3
"""C28: depth-2 ordinary AC2 neighbourhood of archival and parametric pairs.

C13/C27.1 scanned depth-1: one AC2, with cyclic orientations of both factors
as AC3 by a prefix. This census applies that neighbourhood twice. Unique
depth-1 children are expanded once each; unique grandchildren are scored
against the original pair.

A miss is not an AC obstruction to depth ≥ 3, stable moves, or Aut with C1.
Not a heap search. Not a U124 solve unless a witness is found and given an
explicit AC1–AC5 path.
"""
from __future__ import annotations

import csv
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
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import family_a_identities as fam  # noqa: E402
import ms_template_identities as ms  # noqa: E402
import q_peel  # noqa: E402
from elementary_ac2_scan import children  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA_INITIAL = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
DATA_BEST = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
JSON_PATH = OUT / "c28_depth2_ac2.json"


def concat_cyc(a: str, b: str) -> str:
    """Cyclic reduction of a freely reduced concatenation at the junction.

    Equivalent to ``cyc_reduce(a + b)`` when ``a`` and ``b`` are freely reduced.
    """
    i = 0
    la, lb = len(a), len(b)
    while i < la and i < lb and a[la - 1 - i] == b[i].swapcase():
        i += 1
    s = a[: la - i] + b[i:]
    while len(s) >= 2 and s[0] == s[-1].swapcase():
        s = s[1:-1]
    return s


def children_fast(r1: str, r2: str) -> list[tuple[str, str, dict[str, int]]]:
    """Same pairs and move triples as ``elementary_ac2_scan.children``."""
    out: list[tuple[str, str, dict[str, int]]] = []
    for target in (1, 2):
        ri, rj = (r1, r2) if target == 1 else (r2, r1)
        if not ri or not rj:
            continue
        n = len(ri)
        ri2 = ri + ri
        for jsign, oj in ((1, rj), (-1, inv(rj))):
            m = len(oj)
            oj2 = oj + oj
            for k1 in range(n):
                a = ri2[n - k1 : 2 * n - k1] if k1 else ri
                for k2 in range(m):
                    b = oj2[m - k2 : 2 * m - k2] if k2 else oj
                    piece = concat_cyc(a, b)
                    if not piece:
                        continue
                    pair = (piece, r2) if target == 1 else (r1, piece)
                    move = {
                        "target": target,
                        "jsign": jsign,
                        "k1": k1,
                        "k2": k2,
                        "new_len": len(pair[0]) + len(pair[1]),
                    }
                    out.append((pair[0], pair[1], move))
    return out


def children_agree(r1: str, r2: str) -> bool:
    slow = [
        (a, b, m["target"], m["jsign"], m["k1"], m["k2"])
        for a, b, m in children(r1, r2)
    ]
    fast = [
        (a, b, m["target"], m["jsign"], m["k1"], m["k2"])
        for a, b, m in children_fast(r1, r2)
    ]
    return slow == fast


def one_occ_reduced(word: str) -> bool:
    """Equivalent to ``one_occurrence_cyclic`` on an already cyclically reduced word."""
    if not word:
        return False
    nx = ny = 0
    for char in word:
        if char in "xX":
            nx += 1
        elif char in "yY":
            ny += 1
    return nx == 1 or ny == 1


def two_block_reduced(word: str) -> bool:
    """Equivalent to ``two_block_shape`` on an already cyclically reduced word."""
    if not word:
        return False
    gens = [char.lower() for char in word]
    if len(set(gens)) != 2:
        return False
    return sum(gens[i] != gens[i - 1] for i in range(len(gens))) == 2


def unique_children(
    r1: str, r2: str
) -> list[tuple[str, str, dict[str, int]]]:
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str, dict[str, int]]] = []
    for a, b, move in children_fast(r1, r2):
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        out.append((a, b, move))
    return out


def scan_depth2(
    tag: str,
    r1: str,
    r2: str,
    best: tuple[str, str] | None = None,
) -> dict:
    r1 = cyc_reduce(r1)
    r2 = cyc_reduce(r2)
    base_len = len(r1) + len(r2)
    base_one = one_occ_reduced(r1) or one_occ_reduced(r2)
    base_tb = two_block_reduced(r1) and two_block_reduced(r2)
    best_key = canon_pair(*best) if best is not None else None
    best_len = (
        len(cyc_reduce(best[0])) + len(cyc_reduce(best[1]))
        if best is not None
        else None
    )
    d1 = unique_children(r1, r2)
    n_raw = 0
    n_drop_d1 = n_eq_d1 = n_up_d1 = n_one_d1 = n_tb_d1 = 0
    n_drop = n_eq = n_up = n_one = n_tb = 0
    n_hit_best = 0
    best_child_len = base_len
    hit = None

    def consider(
        a: str,
        b: str,
        length: int,
        depth: int,
        move1: dict[str, int],
        move2: dict[str, int] | None,
    ) -> None:
        nonlocal best_child_len, hit, n_hit_best
        dropped = length < base_len
        new_one = (not base_one) and (one_occ_reduced(a) or one_occ_reduced(b))
        new_tb = (not base_tb) and two_block_reduced(a) and two_block_reduced(b)
        if dropped and length < best_child_len:
            best_child_len = length
        interesting = dropped or new_one or new_tb
        if interesting:
            rec = {
                "depth": depth,
                "new_r1": a,
                "new_r2": b,
                "len": length,
                "drop": max(0, base_len - length),
                "move1": move1,
                "move2": move2,
                "one_occurrence": one_occ_reduced(a) or one_occ_reduced(b),
                "two_block_both": two_block_reduced(a) and two_block_reduced(b),
            }
            if hit is None:
                hit = rec
            elif dropped and hit["drop"] == 0:
                hit = rec
        if (
            best_key is not None
            and best_len is not None
            and length <= best_len
            and canon_pair(a, b) == best_key
        ):
            n_hit_best += 1

    for a, b, move1 in d1:
        length = len(a) + len(b)
        if length < base_len:
            n_drop_d1 += 1
        elif length == base_len:
            n_eq_d1 += 1
        else:
            n_up_d1 += 1
        if not base_one and (one_occ_reduced(a) or one_occ_reduced(b)):
            n_one_d1 += 1
        if not base_tb and two_block_reduced(a) and two_block_reduced(b):
            n_tb_d1 += 1
        consider(a, b, length, 1, move1, None)

    seen: set[tuple[str, str]] = set()
    for a, b, move1 in d1:
        for c, d, move2 in children_fast(a, b):
            n_raw += 1
            key = (c, d)
            if key in seen:
                continue
            seen.add(key)
            length = len(c) + len(d)
            if length < base_len:
                n_drop += 1
            elif length == base_len:
                n_eq += 1
            else:
                n_up += 1
            if not base_one and (one_occ_reduced(c) or one_occ_reduced(d)):
                n_one += 1
            if not base_tb and two_block_reduced(c) and two_block_reduced(d):
                n_tb += 1
            consider(c, d, length, 2, move1, move2)
    return {
        "tag": tag,
        "in_len": base_len,
        "best_table_len": best_len,
        "best_child_len": best_child_len,
        "drop": base_len - best_child_len,
        "n_d1_unique": len(d1),
        "n_d1_drop_unique": n_drop_d1,
        "n_d1_eq_unique": n_eq_d1,
        "n_d1_up_unique": n_up_d1,
        "n_d1_new_one_occ": n_one_d1,
        "n_d1_new_two_block": n_tb_d1,
        "n_d2_raw": n_raw,
        "n_d2_unique": len(seen),
        "n_drop_unique": n_drop,
        "n_eq_unique": n_eq,
        "n_up_unique": n_up,
        "n_new_one_occ": n_one,
        "n_new_two_block": n_tb,
        "n_hit_best": n_hit_best,
        "hit": hit,
        "found": hit is not None,
    }


def planted() -> dict:
    hit = scan_depth2("planted_x_xy", "x", "xy")
    miss = scan_depth2("planted_x_y", "x", "y")
    agree = (
        children_agree("x", "xy")
        and children_agree("x", "y")
        and children_agree(*ms.parametric_p(2, -1))
    )
    return {
        "hit_found": hit["drop"] > 0,
        "hit_drop": hit["drop"],
        "hit_depth": None if hit["hit"] is None else hit["hit"]["depth"],
        "miss_drop": miss["drop"],
        "miss_d1_drop": miss["n_d1_drop_unique"],
        "miss_d2_drop": miss["n_drop_unique"],
        "children_fast_agrees": agree,
        "ok": hit["drop"] > 0 and miss["drop"] == 0 and agree,
        "independent_checker": False,
        "same_code_as_census": True,
        "hit": hit["hit"],
        "note": (
            "Miss control is no length drop on ⟨x,y⟩; lengthening "
            "two-block grandchildren of ⟨x,y⟩ are expected at depth 2."
        ),
    }


def parametric_pairs() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for n in range(2, 8):
        for delta in (-1, 1):
            p = ms.parametric_p(n, delta)
            rows.append((f"P[{n},{delta}]", p[0], p[1]))
            q = q_peel.q_pair(n, delta)
            rows.append((f"Q[{n},{delta}]", q[0], q[1]))
        fp = fam.parametric_p(n)
        rows.append((f"FA_P[{n}]", fp[0], fp[1]))
        fq = q_peel.family_a_q(n)
        rows.append((f"FA_Q[{n}]", fq[0], fq[1]))
    return rows


BUDGET_SECONDS = 50.0


def load_initial_csv() -> tuple[list[dict], dict[str, dict]]:
    with DATA_INITIAL.open(newline="", encoding="utf-8") as handle:
        initial = list(csv.DictReader(handle))
    with DATA_BEST.open(newline="", encoding="utf-8") as handle:
        best = {row["name"]: row for row in csv.DictReader(handle)}
    return initial, best


def scan_one_initial(row: dict, best_row: dict) -> dict:
    changed = (row["r1"], row["r2"]) != (best_row["r1"], best_row["r2"])
    rec = scan_depth2(
        row["name"],
        row["r1"],
        row["r2"],
        best=(best_row["r1"], best_row["r2"]) if changed else None,
    )
    rec["id"] = row["name"]
    rec["changed_from_best"] = changed
    return rec


def aggregate_initial(rows: list[dict | None], n_expected: int) -> dict:
    done = [row for row in rows if row is not None]
    interesting = [row for row in done if row["found"] or row["n_hit_best"]]
    return {
        "n_rows": n_expected,
        "n_done": len(done),
        "n_changed_from_best": sum(1 for row in done if row["changed_from_best"]),
        "n_interesting_rows": len(interesting),
        "n_d2_raw": sum(row["n_d2_raw"] for row in done),
        "n_d2_unique_sum": sum(row["n_d2_unique"] for row in done),
        "n_d1_drop_unique_total": sum(row["n_d1_drop_unique"] for row in done),
        "n_drop_unique_total": sum(row["n_drop_unique"] for row in done),
        "n_new_one_occ_total": sum(row["n_new_one_occ"] for row in done),
        "n_new_two_block_total": sum(row["n_new_two_block"] for row in done),
        "n_hit_best_total": sum(row["n_hit_best"] for row in done),
        "complete": len(done) == n_expected and all(row is not None for row in rows),
        "interesting": interesting,
        "rows": rows,
    }


def summarize(ctrl: dict, parametric: list[dict | None], initial: dict) -> dict:
    para_done = [row for row in parametric if row is not None]
    return {
        "planted_ok": ctrl["ok"],
        "children_fast_agrees": ctrl["children_fast_agrees"],
        "parametric_n": len(parametric),
        "parametric_n_done": len(para_done),
        "parametric_complete": len(para_done) == len(parametric) and bool(para_done),
        "parametric_any_hit": any(row["found"] for row in para_done),
        "parametric_any_drop": any(row["drop"] > 0 for row in para_done),
        "parametric_any_d1_drop": any(row["n_d1_drop_unique"] > 0 for row in para_done),
        "parametric_n_d2_raw": sum(row["n_d2_raw"] for row in para_done),
        "parametric_n_d2_unique_sum": sum(row["n_d2_unique"] for row in para_done),
        "initial_n_rows": initial["n_rows"],
        "initial_n_done": initial["n_done"],
        "initial_complete": initial["complete"],
        "initial_n_changed_from_best": initial["n_changed_from_best"],
        "initial_any_hit": initial["n_interesting_rows"] > 0,
        "initial_any_length_drop": (
            initial["n_d1_drop_unique_total"] > 0
            or initial["n_drop_unique_total"] > 0
        ),
        "initial_n_d1_drop_unique_total": initial["n_d1_drop_unique_total"],
        "initial_n_drop_unique_total": initial["n_drop_unique_total"],
        "initial_n_new_one_occ_total": initial["n_new_one_occ_total"],
        "initial_n_new_two_block_total": initial["n_new_two_block_total"],
        "initial_n_hit_best_total": initial["n_hit_best_total"],
        "initial_n_d2_raw": initial["n_d2_raw"],
        "initial_n_d2_unique_sum": initial["n_d2_unique_sum"],
        "census_complete": bool(
            initial["complete"]
            and len(para_done) == len(parametric)
            and para_done
        ),
        "d2_counts_are_unique_presentations": True,
        "d2_raw_is_enumerated_edges": True,
        "same_code_replay": True,
        "independent_checker": False,
        "solved_u124": 0,
    }


def notes_from_summary(summary: dict) -> list[str]:
    return [
        "Depth ≤ 2: unique depth-1 children are scored against the input, then each is expanded once. Depth-2 is a second C13/C27.1 neighbourhood, not a longer AC3–AC2 composite.",
        "children_fast is junction cyclic reduction; tested equal to elementary_ac2_scan.children including move triples.",
        "Unique depth-1 parents are expanded once. Unique grandchildren are (r1, r2) spellings, not canon_pair classes.",
        "Raw grandchild counts include (k1, k2) multiplicity and are not the unique-presentation counts.",
        "A length drop would be an ordinary AC1–AC3 path of two AC2 steps (rotations as AC3). No Aut, no C0.",
        "Matching the stored best table is checked only on changed rows, and only when grandchild length is at most the best length.",
        "JSON is same-code deterministic replay. No U124 row is solved.",
        "The full census exceeds one 60s guard; main() resumes for BUDGET_SECONDS and must be re-run until census_complete.",
    ]


def write_report(report: dict) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def empty_report(n_param: int, n_initial: int) -> dict:
    parametric: list[dict | None] = [None] * n_param
    rows: list[dict | None] = [None] * n_initial
    initial = aggregate_initial(rows, n_initial)
    ctrl = {
        "ok": False,
        "children_fast_agrees": False,
        "independent_checker": False,
    }
    return {
        "summary": summarize(ctrl, parametric, initial),
        "planted": ctrl,
        "parametric": parametric,
        "initial": initial,
        "notes": [],
    }


def load_report(n_param: int, n_initial: int) -> dict:
    if not JSON_PATH.exists():
        return empty_report(n_param, n_initial)
    report = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    parametric = list(report.get("parametric") or [])
    while len(parametric) < n_param:
        parametric.append(None)
    rows = list((report.get("initial") or {}).get("rows") or [])
    while len(rows) < n_initial:
        rows.append(None)
    report["parametric"] = parametric[:n_param]
    report["initial"] = aggregate_initial(rows[:n_initial], n_initial)
    return report


def main(budget: float = BUDGET_SECONDS) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    deadline = time.perf_counter() + budget
    pairs = parametric_pairs()
    csv_rows, best = load_initial_csv()
    report = load_report(len(pairs), len(csv_rows))
    ctrl = planted()
    report["planted"] = ctrl
    print("c28 planted", ctrl["ok"], flush=True)

    paused = False
    for i, (tag, r1, r2) in enumerate(pairs):
        if report["parametric"][i] is not None:
            continue
        if time.perf_counter() >= deadline:
            paused = True
            break
        rec = scan_depth2(tag, r1, r2)
        report["parametric"][i] = rec
        print(
            f"c28 parametric {tag} d1={rec['n_d1_unique']} "
            f"d2u={rec['n_d2_unique']} drop={rec['drop']} found={rec['found']}",
            flush=True,
        )
        report["initial"] = aggregate_initial(report["initial"]["rows"], len(csv_rows))
        report["summary"] = summarize(ctrl, report["parametric"], report["initial"])
        write_report(report)

    if not paused:
        rows = report["initial"]["rows"]
        for i, row in enumerate(csv_rows):
            if rows[i] is not None:
                continue
            if time.perf_counter() >= deadline:
                paused = True
                break
            rec = scan_one_initial(row, best[row["name"]])
            rows[i] = rec
            print(
                f"c28 {rec['id']} d1={rec['n_d1_unique']} d2u={rec['n_d2_unique']} "
                f"d1drop={rec['n_d1_drop_unique']} d2drop={rec['n_drop_unique']} "
                f"found={rec['found']}",
                flush=True,
            )
            report["initial"] = aggregate_initial(rows, len(csv_rows))
            report["summary"] = summarize(ctrl, report["parametric"], report["initial"])
            write_report(report)

    report["initial"] = aggregate_initial(report["initial"]["rows"], len(csv_rows))
    report["summary"] = summarize(ctrl, report["parametric"], report["initial"])
    report["notes"] = notes_from_summary(report["summary"])
    write_report(report)
    print("c28 depth-2 archival AC2", "complete" if report["summary"]["census_complete"] else "paused")
    print(json.dumps(report["summary"], indent=2))
    print(f"wrote {JSON_PATH}")
    return report


def annotate_existing() -> dict:
    pairs = parametric_pairs()
    csv_rows, _best = load_initial_csv()
    report = load_report(len(pairs), len(csv_rows))
    ctrl = planted()
    report["planted"] = ctrl
    report["initial"] = aggregate_initial(report["initial"]["rows"], len(csv_rows))
    report["summary"] = summarize(ctrl, report["parametric"], report["initial"])
    report["notes"] = notes_from_summary(report["summary"])
    write_report(report)
    print("c28 annotate-existing")
    print(json.dumps(report["summary"], indent=2))
    print(f"wrote {JSON_PATH}")
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--annotate-existing"]:
        annotate_existing()
    else:
        main()
