#!/usr/bin/env python3
"""Merge greedy + beam(PPO) solutions into one best-path-per-presentation dataset.

For every presentation in the greedy CSV (all 17,635 rows -- solved AND unsolved),
pick the **shortest known solving path** across the two sources and emit one record
whose path is stored in a SINGLE uniform format: the state trajectory
[r1_0, r2_0, r1_1, r2_1, ... , r1_N, r2_N] as xXyY strings (N = best_path_length).

Why states (not packed actions): the d-o-t model trains on STATES, so storing the
state trajectory lets every downstream step (canonicalize -> label -> featurize)
read it directly with zero env replay, and int8 encoding for the DRT is a trivial
load-time call (canon.strs_to_presentation_literal). Packed actions cannot be the
common format (greedy is not stored as actions).

Sources:
  greedy CSV (`all_presentations_len_8_to_19_GS_solved_copy2.csv`): already a state
      trajectory; Path Length = -1 means greedy did not solve it.
  beam JSONL (`pilot_results.jsonl`): stored as PACKED ACTION ints. We expand a
      beam-won path to states with `scripts/s_move_np.py` -- a pure-numpy port of
      the env S-move, so NO jax/Colab is needed (runs in the py3.9 venv). Only
      beam-WON paths (the shorter ones) are replayed. The replay doubles as
      replay-validation: it asserts each path trivializes in exactly
      beam_path_length steps, catching any spurious solve.

Selection: among the sources that solved a presentation, take the minimum path
length; tie -> greedy (already states, no replay). Unsolved-by-both rows keep
best_source="none", best_path_length=-1, best_path=[] (right-censored).

Outputs (in data/):
  merged_best_paths.jsonl        one record per presentation, WITH the state path
  merged_best_paths_index.csv    slim scan table (lengths/sources, NO path)

Stdlib + numpy only (no jax). Run from the repo root with the venv python:
    ../.venv/bin/python scripts/build_merged_paths.py --limit 50   # smoke test
    ../.venv/bin/python scripts/build_merged_paths.py              # full
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # scripts/
import canon       # noqa: E402  (scripts/canon.py)
import s_move_np   # noqa: E402  (scripts/s_move_np.py -- pure-numpy beam replay)

CSV = "data/all_presentations_len_8_to_19_GS_solved_copy2.csv"
JSONL = "data/derived/paths/pilot_results.jsonl"
OUT_JSONL = "data/derived/paths/merged_best_paths.jsonl"
OUT_INDEX = "data/derived/paths/merged_best_paths_index.csv"

csv.field_size_limit(10 ** 7)  # greedy paths can be hundreds of tokens wide


def load_beam(jsonl_path):
    """beam JSONL -> {idx: record} (last record wins, matching resume dedup)."""
    out = {}
    if not os.path.exists(jsonl_path):
        return out
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # tolerate a truncated final line
            out[rec["idx"]] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--jsonl", default=JSONL)
    ap.add_argument("--out_jsonl", default=OUT_JSONL)
    ap.add_argument("--out_index", default=OUT_INDEX)
    ap.add_argument("--max_length", type=int, default=24)
    ap.add_argument("--limit", type=int, default=None,
                    help="expand only the first N beam-won paths (smoke test)")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit(f"required input not found: {args.csv} (run from repo root?)")
    beam = load_beam(args.jsonl)
    if not beam:
        print(f"note: no beam JSONL at {args.jsonl}; merge will be greedy-only")

    L = args.max_length
    records = []          # final records (path filled for greedy/none now, beam later)
    beam_todo = []        # (record_index, idx, packed_path, beam_len) to expand
    src_count = {"greedy": 0, "beam": 0, "none": 0}
    n_solved = n_new_solve = 0

    with open(args.csv, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[:5] != ["r1", "r2", "Nodes Visited", "Path Length", "Path"]:
            raise SystemExit(f"unexpected CSV header: {header[:5]}")
        for tok in reader:
            if not tok or all(c.strip() == "" for c in tok):
                continue
            idx = len(records)
            r1, r2 = tok[0].strip(), tok[1].strip()
            g_len = int(tok[3])
            g_solved = g_len >= 0
            g_path = [t.strip() for t in tok[4:] if t.strip() != ""] if g_solved else []
            if g_solved and len(g_path) != 2 * (g_len + 1):
                raise SystemExit(
                    f"row {idx}: greedy path {len(g_path)} tokens != {2 * (g_len + 1)}")

            brec = beam.get(idx)
            b_solved = bool(brec and brec.get("beam_solved"))
            b_len = int(brec["beam_path_length"]) if b_solved else -1

            # choose shortest; tie -> greedy (replay-free state trajectory)
            use_beam = b_solved and (not g_solved or b_len < g_len)
            if g_solved or b_solved:
                n_solved += 1
                if not g_solved and b_solved:
                    n_new_solve += 1
            best_src = "beam" if use_beam else ("greedy" if g_solved else "none")
            best_len = b_len if use_beam else (g_len if g_solved else -1)
            src_count[best_src] += 1

            rec = {
                "idx": idx, "r1": r1, "r2": r2,
                "greedy_solved": g_solved, "greedy_path_length": g_len,
                "beam_solved": b_solved, "beam_path_length": b_len,
                "solved": g_solved or b_solved,
                "best_source": best_src, "best_path_length": best_len,
                "best_path": g_path if best_src == "greedy" else [],
            }
            records.append(rec)
            if best_src == "beam":
                beam_todo.append((idx, idx, list(brec.get("packed_path") or []), b_len))

    # ---- expand beam-won paths to states (pure numpy, no jax) ----
    if beam_todo:
        todo = beam_todo[:args.limit] if args.limit else beam_todo
        print(f"expanding {len(todo)} beam-won paths to states "
              f"(pure-numpy S-move replay)...")
        for rec_i, idx, packed, blen in todo:
            r1, r2 = records[rec_i]["r1"], records[rec_i]["r2"]
            flat, terminated, nsteps = s_move_np.replay_to_states(r1, r2, packed, L)
            if not (terminated and nsteps == blen):
                raise AssertionError(
                    f"idx {idx}: replay terminated={terminated} steps={nsteps} "
                    f"!= beam_path_length={blen} (s_move_np port bug or spurious solve)")
            records[rec_i]["best_path"] = flat
        if args.limit:
            print(f"--limit {args.limit}: smoke test only, NOT writing partial output")
            print(f"OK: {len(todo)} beam paths replayed -> states, all trivialize")
            return

    # ---- write ----
    os.makedirs(os.path.dirname(args.out_jsonl) or ".", exist_ok=True)
    with open(args.out_jsonl, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    with open(args.out_index, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "r1", "r2", "greedy_solved", "greedy_path_length",
                    "beam_solved", "beam_path_length", "solved",
                    "best_source", "best_path_length"])
        for r in records:
            w.writerow([r["idx"], r["r1"], r["r2"], r["greedy_solved"],
                        r["greedy_path_length"], r["beam_solved"],
                        r["beam_path_length"], r["solved"],
                        r["best_source"], r["best_path_length"]])

    # ---- validation gate ----
    n = len(records)
    fail = []
    if n != 17635:
        fail.append(f"record count {n} != 17635")
    for r in records:
        bp, src, blen = r["best_path"], r["best_source"], r["best_path_length"]
        if src == "none":
            if bp or blen != -1:
                fail.append(f"idx {r['idx']}: unsolved row not empty"); break
        else:
            if len(bp) != 2 * (blen + 1):
                fail.append(f"idx {r['idx']}: path {len(bp)} tokens != {2*(blen+1)}"); break
            if len(bp[-2]) != 1 or len(bp[-1]) != 1:
                fail.append(f"idx {r['idx']}: final state not trivial: {bp[-2:]}"); break

    n_beam_shorter = sum(1 for r in records if r["best_source"] == "beam")
    total_best = sum(r["best_path_length"] for r in records if r["solved"])
    total_greedy = sum(r["greedy_path_length"] for r in records if r["greedy_solved"])
    print(f"\nwrote {args.out_jsonl} and {args.out_index}")
    print(f"presentations            : {n}")
    print(f"  solved (greedy or beam): {n_solved}   unsolved: {n - n_solved}")
    print(f"  new solves (beam only) : {n_new_solve}")
    print(f"best path source         : greedy {src_count['greedy']}  "
          f"beam {src_count['beam']}  none {src_count['none']}")
    print(f"sum of best path lengths : {total_best}  "
          f"(greedy-only would be {total_greedy}; saved {total_greedy - total_best})")
    if fail:
        for m in fail:
            print("  VALIDATION FAIL:", m)
        raise SystemExit("merge validation FAILED")
    print("OK: 17,635 records, single state-trajectory format, every path ends "
          "trivial; beam paths replay-validated")


if __name__ == "__main__":
    main()
