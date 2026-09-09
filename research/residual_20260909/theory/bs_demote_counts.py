"""Counts for research/residual_20260909/bs_demote_gate.py.

* dev panel (102 rows): per-row recognition / certification, with work and the
  decoded elementary move count.
* full 727-row residual: AGGREGATE counts only - val/test/rest are hidden, so
  no row identity is printed for anything outside dev.
* the 584 solved stalled-BS census paths: how many bs_preflight calls
  ``is_doomed_bs_state`` would have skipped.

Usage: PYTHONPATH=. python3 research/residual_20260909/theory/bs_demote_counts.py
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter

from experiments.equivalence_classes.lib.words import canon_pair, canon_rel
from research.residual_20260909.bs_demote_gate import (
    complete, demotable, is_doomed_bs_state, recognize,
)
from research.supermoves_20260908.bs_preflight import preflight
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary
from research.supermoves_20260908.cheap_gates import bs_gate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV = os.path.join(ROOT, "panels", "dev.csv")
RESIDUAL = "results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv"
MINED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "path_mining_rows.jsonl")
BUDGET = 1000


def rows(path):
    with open(path) as handle:
        for row in csv.DictReader(handle):
            yield row["name"], (row["r1"], row["r2"])


def dev_report():
    print(f"== dev panel ({DEV}) ==")
    recognised = certified = 0
    total = 0
    for name, pair in rows(DEV):
        total += 1
        label = recognize(pair)
        if label is None:
            continue
        recognised += 1
        result = complete(pair, budget=BUDGET)
        if not result["solved"]:
            print(f"  {name:<12} label={label} recognised, NOT certified "
                  f"(work={result['work']}, {result['reason']})")
            continue
        moves = decode_elementary(list(pair), result["states"], result["steps"],
                                  result["elementary_tail"])
        assert replay_elementary(list(pair), moves) == ["x", "y"]
        certified += 1
        print(f"  {name:<12} label={label} CERTIFIED work={result['work']} "
              f"(pinch {result['pinch_carries']} + transport "
              f"{result['transport_carries']} + collapse "
              f"{result['collapse_rewrites']}), {len(moves)} elementary moves")
    print(f"  dev rows {total}: recognised {recognised}, certified {certified}")


def residual_report():
    print(f"== full residual ({RESIDUAL}) - aggregate only ==")
    total = recognised = certified = 0
    labels = Counter()
    work = []
    for _name, pair in rows(RESIDUAL):
        total += 1
        label = recognize(pair)
        if label is None:
            continue
        recognised += 1
        labels[("demotable" if demotable(label) else "other")] += 1
        result = complete(pair, budget=BUDGET)
        if result["solved"]:
            moves = decode_elementary(list(pair), result["states"], result["steps"],
                                      result["elementary_tail"])
            assert replay_elementary(list(pair), moves) == ["x", "y"]
            certified += 1
            work.append((result["work"], len(moves)))
    print(f"  rows {total}: recognised {recognised}, certified {certified}")
    print(f"  recognised split: {dict(labels)}")
    if work:
        print(f"  certified work {min(w for w, _ in work)}..{max(w for w, _ in work)}, "
              f"elementary moves {min(e for _, e in work)}..{max(e for _, e in work)}")


def doomed_report():
    print("== is_doomed_bs_state on the 584 solved stalled-BS census paths ==")
    if not os.path.exists(MINED):
        print("  path_mining_rows.jsonl missing; run theory/path_mining.py first")
        return
    paths = skipped = states = scans = accepts = 0
    with open(MINED) as handle:
        for line in handle:
            record = json.loads(line)
            if "stalled_bs_root" not in record["group"]:
                continue
            paths += 1
            root = tuple(record["pair"])
            R0 = record["root_R"]
            for state in record["states"]:
                state = tuple(state)
                if R0 not in state:
                    break            # the first move on R0 ends the W-only prefix
                states += 1
                if not is_doomed_bs_state(root, state):
                    continue
                skipped += 1
                check = preflight(state)
                scans += check["scans"]
                accepts += check["status"] == "accept"
    print(f"  {paths} paths, {states} states on the W-only prefix")
    print(f"  is_doomed_bs_state True at {skipped} of them -> {skipped} bs_preflight "
          f"calls and {scans} scans skipped")
    print(f"  soundness check: preflight accepted at {accepts} of the skipped states "
          f"(must be 0)")
    assert accepts == 0


def main():
    dev_report()
    print()
    residual_report()
    print()
    doomed_report()


if __name__ == "__main__":
    main()
