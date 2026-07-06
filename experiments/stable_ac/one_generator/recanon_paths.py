#!/usr/bin/env python3
"""Re-express the stored canonical representatives in results/ path streams under the CURRENT
canonicalization (greedy_nrel), after the canonical letter-order was aligned to the paper (Y<y<X<x).

Each ``paths_*.jsonl`` record stores a solved path as ``states`` (canonical presentations) + ``moves``
(splice indices relative to each state's stored rotation). When the canonical representative changes,
every state's chosen rotation/inversion can change, so:
  * each ``states[t]`` is re-canonicalized with the current ``canonical_tuple``;
  * ``moves`` are recomputed to connect the new representatives (any valid connecting move — the path
    is the same sequence of AC-classes, just relabelled);
  * the whole path is re-checked with ``verify_path`` (independent replay) — a HARD gate per record.
This is sound because ``get_neighbors`` enumerates all rotations, so neighbour-classes are
representation-independent: a path valid under the old order is valid under the new one.

Only ``states``/``moves`` change; every other field is preserved. Runs/calibration streams hold no
canonical representatives (metrics only) and are left untouched, as is anything under website/.

    python recanon_paths.py            # DRY RUN: migrate in memory, verify all, report (no writes)
    python recanon_paths.py --write    # back up each file to <f>.precanon.bak, then rewrite it
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import greedy_nrel as gn

# every results/ paths stream (NOT website/, NOT the empty ak_3_test paths, NOT runs/ metrics)
TARGETS = [
    "results/baseline_greedy/paths/paths_baseline.jsonl",
    "results/solved640/paths/paths_baseline.jsonl",
    "results/solved640/paths/paths_r1.jsonl",
    "results/solved640/paths/paths_r2.jsonl",
    "results/stable_ac/3_generators_w_choices/ms640/paths/paths_r1.jsonl",
    "results/stable_ac/3_generators_w_choices/ms640/paths/paths_r2.jsonl",
    "results/stable_ac/3_generators_w_choices/ms640/paths/paths_x.jsonl",
    "results/stable_ac/3_generators_w_choices/ms640/paths/paths_y.jsonl",
]


def _to_arrays(state):
    return tuple(np.array(r, dtype=gn.INT_DTYPE) for r in state)


def _to_lists(state):
    return [[int(x) for x in r] for r in state]


def recanon_record(rec):
    """Return (new_rec, n_states_changed). Raises if a path fails to re-verify."""
    n_gen = rec["n_gen"]
    old_states = rec["states"]
    new_states = [gn.canonical_tuple(_to_arrays(st)) for st in old_states]   # current-order canonical

    # recompute moves to connect the new representatives
    moves = [None]
    for t in range(1, len(new_states)):
        target = gn.canonical_key(new_states[t])
        mv = None
        for nbr, m in gn.get_neighbors(new_states[t - 1], n_gen):
            if any(len(r) == 0 for r in nbr):
                continue
            if gn.canonical_key(nbr) == target:
                mv = list(int(x) for x in m)
                break
        if mv is None:
            raise RuntimeError(f"{rec.get('name')}: no move connects step {t} after recanon")
        moves.append(mv)

    if not gn.verify_path(new_states, n_gen):
        raise RuntimeError(f"{rec.get('name')}: verify_path FAILED after recanon")

    new_lists = [_to_lists(st) for st in new_states]
    changed = sum(1 for a, b in zip(old_states, new_lists) if a != b)
    rec = dict(rec)
    rec["states"] = new_lists
    rec["moves"] = moves
    return rec, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="rewrite files (default: dry run)")
    args = ap.parse_args()

    # warm numba
    gn.canonical_tuple((np.array([1, 2], dtype=gn.INT_DTYPE), np.array([2], dtype=gn.INT_DTYPE)))

    grand_recs = grand_changed = grand_files = 0
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print(f"  SKIP (missing): {rel}")
            continue
        recs = [json.loads(l) for l in open(path) if l.strip()]
        out, changed_states, changed_recs = [], 0, 0
        for rec in recs:
            new_rec, ch = recanon_record(rec)
            out.append(new_rec)
            changed_states += ch
            changed_recs += (ch > 0)
        verified = sum(1 for r in out if gn.verify_path(
            [ _to_arrays(s) for s in r["states"] ], r["n_gen"]))
        assert verified == len(out), f"{rel}: only {verified}/{len(out)} verify!"
        grand_recs += len(out); grand_changed += changed_recs; grand_files += 1
        tag = "WROTE" if args.write else "dry-run OK"
        print(f"  [{tag}] {rel}: {len(out)} paths, {verified} verify_path=True, "
              f"{changed_recs} records had >=1 restated relator ({changed_states} states)")
        if args.write:
            shutil.copy2(path, path + ".precanon.bak")
            with open(path, "w") as f:
                for r in out:
                    f.write(json.dumps(r) + "\n")
                f.flush(); os.fsync(f.fileno())

    mode = "WROTE" if args.write else "DRY RUN (no files changed)"
    print(f"\n{mode}: {grand_files} files, {grand_recs} paths total, {grand_changed} records restated; "
          f"ALL re-verified with verify_path under the current canonical order.")
    if not args.write:
        print("Re-run with --write to apply (backs up each file to <f>.precanon.bak first).")


if __name__ == "__main__":
    main()
