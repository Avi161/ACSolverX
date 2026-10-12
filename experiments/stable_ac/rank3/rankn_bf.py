"""Rank-4 and rank-5 brute-force arms of the stable-AC baseline (AWS only).

Start ``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>`` for EVERY multiset
{w1..wk} of folded reduced words (``words.words_of_length``):

* rank 4: k = 2, |w| <= 3 (26 words, 351 multisets)
* rank 5: k = 3, |w| <= 2 (8 words, 120 multisets)

Same search (``search_n_fast``), cap 24 and budget 1,000 as the rank-3 sweep.
Per presentation the 2-generator control and the null stabilization
``Z1, .., Zk`` are searched too; they must agree node for node.
The cap counters of every search (``run_rank3_bf.CAP_DOC``) are stored beside
the node counts: ``cap_dropped``, ``cap_dropped_min_total``, ``cap_first_bind``
indexed ``[presentation, multiset]``, and ``base_cap`` / ``null_cap`` for the
control and the null stabilization (-1 = none).

    python3 rankn_bf.py <out_dir> <workers>
"""
import hashlib
import itertools
import json
import os
import sys
import time
from multiprocessing import get_context

import numpy as np

from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.rank3.run_rank3_bf import CAP_DOC, CAP_FIELDS, load_ms640
from experiments.stable_ac.solvern import Pres, word_to_str
from experiments.stable_ac.solvern_fast import search_n_fast

BUDGET, CAP = 1000, 24
ARMS = {4: (2, 3), 5: (3, 2)}        # rank: (extra generators, max word length)
SAMPLE = 0.02                         # fraction of solved rows whose path is kept
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"


def word_list(max_len):
    return [w for n in range(1, max_len + 1) for w in W.words_of_length(n)]


def combos(rank):
    k, max_len = ARMS[rank]
    ws = word_list(max_len)
    return ws, list(itertools.combinations_with_replacement(range(len(ws)), k))


def start(r1, r2, ws):
    return Pres(2 + len(ws), (tuple(r1), tuple(r2))
                + tuple((-(3 + i),) + tuple(w) for i, w in enumerate(ws)))


def triple(res):
    return (int(bool(res["solved"])), int(res["nodes_explored"]),
            int(res["path_length"]) if res["solved"] else -1)


def counters(res):
    return tuple(-1 if res[k] is None else int(res[k]) for k in CAP_FIELDS)


def sampled(key):
    h = hashlib.md5(key.encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64 < SAMPLE


def shard_path(rank, p):
    return os.path.join(OUT, "shards", f"r{rank}_p{p}.npz")


def task(args):
    rank, p, r1, r2 = args
    path = shard_path(rank, p)
    if os.path.exists(path):
        return rank, p, 0.0
    t0 = time.time()
    ws, cs = combos(rank)
    k = ARMS[rank][0]
    res2 = search_n_fast(Pres(2, (tuple(r1), tuple(r2))), BUDGET, cap=CAP, cyclic=True)
    res0 = search_n_fast(start(r1, r2, [()] * k), BUDGET, cap=CAP, cyclic=True)
    base, null = triple(res2), triple(res0)
    nodes = np.zeros(len(cs), dtype=np.uint16)
    plen = np.full(len(cs), -1, dtype=np.int16)
    caps = np.full((len(cs), 3), -1, dtype=np.int64)
    paths = []
    for i, c in enumerate(cs):
        res = search_n_fast(start(r1, r2, [ws[j] for j in c]), BUDGET, cap=CAP, cyclic=True)
        nodes[i] = res["nodes_explored"]
        caps[i] = counters(res)
        if res["solved"]:
            plen[i] = res["path_length"]
            if sampled(f"{rank}|{p}|{i}"):
                paths.append({"rank": rank, "pres_id": p, "index": i,
                              "z_words": [word_to_str(ws[j]) for j in c],
                              "nodes_explored": int(nodes[i]),
                              "path_moves": list(res["path_moves"])})
    secs = time.time() - t0
    tmp = path + f".tmp{os.getpid()}.npz"
    np.savez(tmp, nodes=nodes, path_len=plen, base=np.array(base), null=np.array(null),
             cap_counts=caps, base_cap=np.array(counters(res2)),
             null_cap=np.array(counters(res0)),
             seconds=np.float32(secs), paths=np.array(json.dumps(paths)))
    os.replace(tmp, path)
    return rank, p, secs


def merge(rank, rows):
    ws, cs = combos(rank)
    ids = [p for p, _, _ in rows]
    nodes = np.zeros((len(ids), len(cs)), dtype=np.uint16)
    plen = np.full((len(ids), len(cs)), -1, dtype=np.int16)
    base = np.zeros((len(ids), 3), dtype=np.int32)
    null = np.zeros((len(ids), 3), dtype=np.int32)
    caps = np.full((len(ids), len(cs), 3), -1, dtype=np.int64)
    base_cap = np.zeros((len(ids), 3), dtype=np.int64)
    null_cap = np.zeros((len(ids), 3), dtype=np.int64)
    secs, paths = 0.0, []
    for i, p in enumerate(ids):
        with np.load(shard_path(rank, p)) as z:
            nodes[i], plen[i], base[i], null[i] = z["nodes"], z["path_len"], z["base"], z["null"]
            caps[i], base_cap[i], null_cap[i] = z["cap_counts"], z["base_cap"], z["null_cap"]
            secs += float(z["seconds"])
            paths += json.loads(str(z["paths"]))
    meta = {"rank": rank, "node_budget": BUDGET, "max_relator_length_cap": CAP,
            "solver": "solvern_fast.search_n_fast", "source": "ms640",
            "extra_generators": ARMS[rank][0], "max_word_len": ARMS[rank][1],
            "words": [word_to_str(w) for w in ws], "core_seconds": secs,
            "cap_fields": CAP_DOC, "base_cap_null_cap_order": list(CAP_FIELDS)}
    stem = os.path.join(OUT, f"rankn_bf_ms640_b{BUDGET}_cap{CAP}_r{rank}")
    np.savez_compressed(stem + ".tmp.npz", pres_ids=np.array(ids), nodes=nodes, path_len=plen,
                        base=base, null=null, combos=np.array(cs, dtype=np.int16),
                        cap_dropped=np.minimum(caps[:, :, 0], 2 ** 32 - 1).astype(np.uint32),
                        cap_dropped_min_total=caps[:, :, 1].astype(np.int16),
                        cap_first_bind=caps[:, :, 2].astype(np.int32),
                        base_cap=base_cap, null_cap=null_cap,
                        meta=np.array(json.dumps(meta)))
    os.replace(stem + ".tmp.npz", stem + ".npz")
    with open(stem + "_sample_paths.jsonl", "w") as f:
        for row in paths:
            f.write(json.dumps(row) + "\n")

    bad = [ids[i] for i in range(len(ids)) if tuple(base[i]) != tuple(null[i])]
    # no Z_i shares a letter with r1, r2 or another Z_j: the null stabilization
    # drops the children the control drops, each k letters longer in total
    k = ARMS[rank][0]
    cap_bad = [ids[i] for i in range(len(ids)) if tuple(null_cap[i]) != (
        base_cap[i, 0], base_cap[i, 1] + (k if base_cap[i, 1] >= 0 else 0), base_cap[i, 2])]
    cs_ok = base[:, 0] == 1
    S = plen >= 0
    faster = S & (nodes < base[:, 1][:, None]) & cs_ok[:, None]
    out = {
        "rank": rank, "combos_per_presentation": len(cs), "searches": int(S.size),
        "core_seconds": round(secs), "ms_per_search": round(1000 * secs / S.size, 1),
        "null_mismatch_pres_ids": bad,
        "null_cap_counter_mismatch_pres_ids": cap_bad,
        "searches_where_the_cap_dropped_a_child": int((caps[:, :, 0] > 0).sum()),
        "searches_where_the_cap_could_bind": int((caps[:, :, 2] >= 0).sum()),
        "solved_searches_where_the_cap_could_bind": int(((caps[:, :, 2] >= 0) & (plen >= 0)).sum()),
        "control_solved": int(cs_ok.sum()),
        "mean_solve_rate_per_presentation": round(float(S.mean(axis=1).mean()), 4),
        "mean_solve_rate_on_control_solved": round(float(S[cs_ok].mean()), 4),
        "mean_solve_rate_on_control_unsolved": round(float(S[~cs_ok].mean()), 4) if (~cs_ok).any() else None,
        "solved_by_some_combo": int(S.any(axis=1).sum()),
        "gained_presentations": [ids[i] for i in np.where(S.any(axis=1) & ~cs_ok)[0]],
        "lost_by_every_combo": int((cs_ok & ~S.any(axis=1)).sum()),
        "share_of_solved_combos_faster_than_control": round(float(faster.sum() / max(1, (S & cs_ok[:, None]).sum())), 4),
        "presentations_where_some_combo_is_faster": int(faster.any(axis=1).sum()),
        "best_single_combo_solved": int(S.sum(axis=0).max()),
        "best_single_combo": [word_to_str(ws[j]) for j in cs[int(S.sum(axis=0).argmax())]],
    }
    with open(stem + "_summary.json", "w") as f:
        json.dump(out, f, indent=1)
    print(time.strftime("%FT%TZ", time.gmtime()), "SUMMARY", json.dumps(out), flush=True)
    return bad


def main():
    workers = int(sys.argv[2])
    os.makedirs(os.path.join(OUT, "shards"), exist_ok=True)
    rows = load_ms640("data/ms640_solved.txt")
    if len(sys.argv) > 3:                       # preflight: a few presentations
        keep = {int(x) for x in sys.argv[3].split(",")}
        rows = [r for r in rows if r[0] in keep]
    failed = False
    with get_context("fork").Pool(workers) as pool:
        for rank in sorted(ARMS):
            t0, done = time.time(), 0
            jobs = [(rank, p, r1, r2) for p, r1, r2 in rows]
            for _ in pool.imap_unordered(task, jobs, chunksize=1):
                done += 1
                if done % 40 == 0 or done == len(jobs):
                    print(time.strftime("%FT%TZ", time.gmtime()),
                          f"rank {rank}: {done}/{len(jobs)} presentations, elapsed {time.time() - t0:.0f}s", flush=True)
            bad = merge(rank, rows)
            if bad:
                failed = True
                print(f"FAIL rank {rank}: null stabilization != control on {bad[:20]}", flush=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
