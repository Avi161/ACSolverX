"""Census of greedy floor states across the Lane D quotient pool: for every merged
candidate with total_len <= --tl_cap, run gn greedy @--budget tracking min_total_state;
tally the distinct canonical floor classes (mod signed relabeling). Streams to
laneD/floor_census.jsonl (resumable by mkey). The floor set = the hardest core of the
stable class; each member is a candidate start form for deeper attacks."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import greedy_nrel as gn
from mitm import symmetry_keys

LANE_D = os.environ.get("ACX_LANED_DIR") or os.path.join(
    ROOT, "results", "stable_ac", "ak3_stable_proof", "laneD")


def probe_floor(task):
    rec, budget = task
    rels = [np.array(r, dtype=gn.INT_DTYPE) for r in rec["relators"]]
    solver = gn.NRelatorSolver(rels, 2, max_nodes=budget, max_len=gn.L)
    path, nodes, _ = solver.solve()
    st = [[int(a) for a in r] for r in gn.key_to_state(solver.min_total_state)]
    return {"mkey": rec["mkey"], "total_len": rec["total_len"], "budget": budget,
            "solved": path is not None,
            "min_total_len": int(solver.min_total_len),
            "floor_mkey": min(symmetry_keys(st)).hex(),
            "floor_state": st}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=25_000)
    ap.add_argument("--tl_cap", type=int, default=18)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    out = os.path.join(LANE_D, "floor_census.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add(json.loads(line)["mkey"])
            except Exception:
                pass
    cands = []
    for line in open(os.path.join(LANE_D, "merged.jsonl")):
        rec = json.loads(line)
        if rec["total_len"] <= args.tl_cap and rec["mkey"] not in done:
            cands.append(rec)
    print(f"census: {len(cands)} candidates pending ({len(done)} done)", flush=True)
    if not cands:
        report(out)
        return
    import ak3_words as aw
    gn.solve_one(aw.FORMS["textbook"], n_gen=2, max_nodes=8)  # warm numba pre-fork
    from multiprocessing import Pool
    with Pool(processes=args.workers, maxtasksperchild=32) as pool, open(out, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(
                probe_floor, [(c, args.budget) for c in cands])):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
            if (i + 1) % 100 == 0:
                print(f"  [{i + 1}/{len(cands)}]", flush=True)
    report(out)


def report(out):
    from collections import Counter
    floors = Counter()
    examples = {}
    for line in open(out):
        r = json.loads(line)
        floors[r["floor_mkey"]] += 1
        examples.setdefault(r["floor_mkey"], (r["floor_state"], r["min_total_len"]))
    print(f"\n{sum(floors.values())} probes -> {len(floors)} distinct floor classes:")
    for fk, n in floors.most_common(15):
        st, mtl = examples[fk]
        print(f"  {n:5d}x  mtl={mtl:2d}  {st}")


if __name__ == "__main__":
    main()
