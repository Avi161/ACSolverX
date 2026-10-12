"""Re-run stored results with the REFERENCE solver ``solvern.search_n`` (AWS only).

Three job kinds, all at budget 1,000, cap 24:

* ``r3``    random (presentation, word) cells of the deployed rank-3 npz files
* ``flip``  both sides of mirror-twin pairs (y <-> Y) whose solved flags differ
* ``r4``/``r5`` random cells of the rank-4/5 npz files

Each job compares (solved, nodes, path_len) from the fast solver's file with a
fresh reference search. Time-boxed: stops after <minutes> and reports how many
jobs were compared.

    python3 rankn_checks.py <rank3_dir> <rankn_dir> <out_json> <workers> <minutes>
"""
import glob
import json
import os
import random
import re
import sys
import time
from multiprocessing import get_context

import numpy as np

from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.rank3.run_rank3_bf import load_ms640
from experiments.stable_ac.solvern import Pres, search_n

BUDGET, CAP = 1000, 24


def canon_word(w):
    inv = tuple(-g for g in reversed(w))
    return min(c[i:] + c[:i] for c in (tuple(w), inv) for i in range(len(c)))


def key(r1, r2):
    return tuple(sorted((canon_word(r1), canon_word(r2))))


def mir(w):
    return tuple(-g if abs(g) == 2 else g for g in w)


def job(args):
    kind, label, rels, exp = args
    res = search_n(Pres(len(rels), rels), BUDGET, cap=CAP, cyclic=True)
    got = (int(bool(res["solved"])), int(res["nodes_explored"]),
           int(res["path_length"]) if res["solved"] else -1)
    return kind, label, list(exp), list(got)


def main():
    r3dir, rndir, out, workers, minutes = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
    rng = random.Random(20261012)
    ms = {p: (r1, r2) for p, r1, r2 in load_ms640("data/ms640_solved.txt")}
    by_key = {}
    for p, (r1, r2) in ms.items():
        by_key.setdefault(key(r1, r2), []).append(p)
    twin = {}
    for p, (r1, r2) in ms.items():
        q = [x for x in by_key.get(key(mir(r1), mir(r2)), []) if x != p]
        if len(q) == 1:
            twin[p] = q[0]
    print("mirror twins:", len(twin), flush=True)

    r3_jobs, flip_jobs, rn_jobs = [], [], []
    for f in sorted(glob.glob(os.path.join(r3dir, "*_L*.npz"))):
        m = re.search(r"_b1000_cap24_L(\d+)\.npz$", f)
        if not m:
            continue
        n = int(m.group(1))
        with np.load(f) as z:
            N, pl, ids = z["nodes"].astype(np.int64), z["path_len"].astype(np.int64), [int(p) for p in z["pres_ids"]]
        ws = W.words_of_length(n)
        row = {p: i for i, p in enumerate(ids)}

        def cell(p, k):
            r1, r2 = ms[p]
            i = row[p]
            return ((tuple(r1), tuple(r2), (-3,) + tuple(ws[k])),
                    (int(pl[i, k] >= 0), int(N[i, k]), int(pl[i, k])))

        for _ in range(min(400, 60 * n)):
            p, k = rng.choice(ids), rng.randrange(len(ws))
            r3_jobs.append(("r3", f"L{n}|p{p}|w{k}") + cell(p, k))
        if n >= 3:
            idx = {w: k for k, w in enumerate(ws)}
            flips = [(p, k) for p in ids if p in twin and p < twin[p] for k in range(len(ws))
                     if (pl[row[p], k] >= 0) != (pl[row[twin[p]], idx[W.fold(mir(ws[k]))]] >= 0)]
            print(f"L{n}: {len(flips)} mirror-twin flips", flush=True)
            for p, k in rng.sample(flips, min(15, len(flips))):
                k2 = idx[W.fold(mir(ws[k]))]
                flip_jobs.append(("flip", f"L{n}|p{p}|w{k}|a") + cell(p, k))
                flip_jobs.append(("flip", f"L{n}|p{p}|w{k}|b") + cell(twin[p], k2))

    for f in sorted(glob.glob(os.path.join(rndir, "rankn_bf_*_r[45].npz"))):
        with np.load(f) as z:
            N, pl, ids, cs = z["nodes"].astype(np.int64), z["path_len"].astype(np.int64), [int(p) for p in z["pres_ids"]], z["combos"]
            meta = json.loads(str(z["meta"]))
            base, null = z["base"], z["null"]
        from experiments.stable_ac.solvern import str_to_word
        ws = [tuple(str_to_word(s)) for s in meta["words"]]
        rank = meta["rank"]
        for _ in range(300):
            i, c = rng.randrange(len(ids)), rng.randrange(len(cs))
            r1, r2 = ms[ids[i]]
            rels = (tuple(r1), tuple(r2)) + tuple((-(3 + j),) + ws[int(a)] for j, a in enumerate(cs[c]))
            rn_jobs.append((f"r{rank}", f"p{ids[i]}|c{c}", rels,
                            (int(pl[i, c] >= 0), int(N[i, c]), int(pl[i, c]))))
        for i in rng.sample(range(len(ids)), min(40, len(ids))):
            r1, r2 = ms[ids[i]]
            rels = (tuple(r1), tuple(r2)) + tuple((-(3 + j),) for j in range(rank - 2))
            rn_jobs.append((f"r{rank}null", f"p{ids[i]}", rels, tuple(int(v) for v in null[i])))
            rn_jobs.append(("r2", f"p{ids[i]}", (tuple(r1), tuple(r2)), tuple(int(v) for v in base[i])))

    rng.shuffle(r3_jobs)
    rng.shuffle(rn_jobs)
    rest = [j for pair in zip(r3_jobs, rn_jobs) for j in pair] + r3_jobs[len(rn_jobs):] + rn_jobs[len(r3_jobs):]
    jobs = flip_jobs + rest
    print(f"jobs: flip {len(flip_jobs)}, rank3 {len(r3_jobs)}, rank4/5 {len(rn_jobs)}", flush=True)

    t0 = time.time()
    stats, bad, flips_seen = {}, [], {}
    pool = get_context("fork").Pool(workers)
    for kind, label, exp, got in pool.imap(job, jobs, chunksize=1):
        s = stats.setdefault(kind, {"compared": 0, "equal": 0})
        s["compared"] += 1
        if exp == got:
            s["equal"] += 1
        else:
            bad.append({"kind": kind, "label": label, "file": exp, "reference": got})
        if kind == "flip":
            flips_seen[label] = got[0]
        if sum(v["compared"] for v in stats.values()) % 100 == 0:
            print(time.strftime("%FT%TZ", time.gmtime()), json.dumps(stats), f"elapsed {time.time() - t0:.0f}s", flush=True)
        if time.time() - t0 > 60 * minutes:
            break
    pool.terminate()
    pairs = {lab[:-2] for lab in flips_seen if lab[:-2] + "|a" in flips_seen and lab[:-2] + "|b" in flips_seen}
    repro = sum(flips_seen[p + "|a"] != flips_seen[p + "|b"] for p in pairs)
    res = {"budget": BUDGET, "cap": CAP, "reference": "solvern.search_n", "jobs_planned": len(jobs),
           "seconds": round(time.time() - t0), "stats": stats,
           "flip_pairs_rerun": len(pairs), "flip_pairs_reproduced_by_reference": repro,
           "mismatches": len(bad), "first_mismatches": bad[:200]}
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print(time.strftime("%FT%TZ", time.gmtime()), "CHECKS", json.dumps({k: v for k, v in res.items() if k != "first_mismatches"}), flush=True)
    sys.exit(3 if bad else 0)      # 3 = a real fast-vs-reference mismatch


if __name__ == "__main__":
    main()
