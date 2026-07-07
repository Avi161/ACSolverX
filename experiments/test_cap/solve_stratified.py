#!/usr/bin/env python3
"""Stratified solve of the escalated (l_cap=48) Lane-D quotients.

plateau_elim's own solve phase is shortest-first, so within any bounded budget it never
reaches the never-before-searched total-length 25-40 region — it re-confirms floor-13 on
the short candidates and stops. This driver instead SAMPLES candidates across every length
bucket (esp. 25-40) and greedy-solves each with max_len=60 passed as a PARAMETER (gn.L
stays 24). Resumable append-only JSONL. On any solve: verify_path replay AND the full
certificate chain (plateau_elim.build_chain_cert -> verify_certificate).
"""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict

# macOS: force fork for the solve Pool so forked children inherit the parent's warmed
# numba. Under spawn (macOS default) each child re-imports greedy_nrel and deadlocks on
# the numba compile cache (CLAUDE.md lesson 2026-07-02). Set before any heavy import.
os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
PROOF = os.path.join(ROOT, "experiments", "stable_ac", "ak3_stable_proof")
for p in (PROOF, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

OUT = os.environ.get("ACX_TESTCAP_DIR") or HERE
os.environ["ACX_LANED_DIR"] = os.path.join(OUT, "laneD")
os.environ["ACX_CERTS_DIR"] = os.path.join(OUT, "certs")

import greedy_nrel as gn  # noqa: E402
import ak3_words as aw  # noqa: E402
import plateau_elim as pe  # noqa: E402  (reuse build_chain_cert — the tested cert path)

INT = gn.INT_DTYPE


def _solve_task(task):
    """Worker: plain 2-gen greedy on one candidate at max_len (parameter, may exceed gn.L)."""
    rec, budget, max_len = task
    rels = [np.array(r, dtype=INT) for r in rec["relators"]]
    t0 = time.time()
    solver = gn.NRelatorSolver(rels, 2, max_nodes=budget, max_len=max_len)
    path, nodes, _ = solver.solve()
    out = {"mkey": rec["mkey"], "total_len": rec["total_len"], "budget": budget,
           "max_len": max_len, "solved": path is not None, "nodes": int(nodes),
           "min_total_len": int(solver.min_total_len), "wall_s": round(time.time() - t0, 1),
           "form": rec["form"], "word": rec["word"], "gen": rec["gen"], "ri": rec["ri"],
           "src": rec["src"], "relators": rec["relators"]}
    if path is not None:
        out["path_states"] = [[[int(a) for a in r] for r in st] for st in path["states"]]
        out["path_verified"] = bool(gn.verify_path(path["states"], 2))
    return out


def select(merged_path, k_long, k_ctrl, long_lo, long_hi):
    """merged.jsonl is sorted by (total_len, mkey), so first-K per bucket is a deterministic
    sample. Control = shortest k_ctrl with total_len < long_lo (reproduce floor-13).
    Long = up to k_long per bucket for long_lo..long_hi (the untested region)."""
    buckets = defaultdict(list)
    with open(merged_path) as f:
        for line in f:
            rec = json.loads(line)
            buckets[rec["total_len"]].append(rec)
    coverage = {L: len(v) for L, v in sorted(buckets.items())}
    chosen, ctrl = [], []
    for L in sorted(buckets):
        if L < long_lo:
            ctrl += buckets[L]
        elif L <= long_hi:
            chosen += buckets[L][:k_long]
    chosen = ctrl[:k_ctrl] + chosen
    return chosen, coverage


def main():
    import multiprocessing as mp
    try:
        mp.set_start_method("fork", force=True)
    except RuntimeError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--budget2", type=int, default=80_000)
    ap.add_argument("--max_len", type=int, default=60)
    ap.add_argument("--k_long", type=int, default=100)   # per length bucket, 25..hi
    ap.add_argument("--k_ctrl", type=int, default=200)   # total, lengths < 25
    ap.add_argument("--long_lo", type=int, default=25)
    ap.add_argument("--long_hi", type=int, default=40)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if args.quick:
        args.budget2, args.k_long, args.k_ctrl = 2_000, 5, 5

    merged = os.path.join(OUT, "laneD", "merged.jsonl")
    if not os.path.exists(merged):
        print(f"no merged.jsonl at {merged} — run run_captest.py first", flush=True)
        sys.exit(1)
    chosen, coverage = select(merged, args.k_long, args.k_ctrl, args.long_lo, args.long_hi)
    print(f"[stratified] merged bucket coverage (total_len: n_candidates): {coverage}",
          flush=True)
    print(f"[stratified] sampled {len(chosen)} candidates "
          f"(k_ctrl={args.k_ctrl} for <{args.long_lo}, k_long={args.k_long}/bucket for "
          f"{args.long_lo}-{args.long_hi}); budget2={args.budget2} max_len={args.max_len}",
          flush=True)

    out_path = os.path.join(OUT, "solve_stratified.jsonl")
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                r = json.loads(line)
                if r["budget"] >= args.budget2:
                    done.add(r["mkey"])
            except Exception:
                pass
    todo = [c for c in chosen if c["mkey"] not in done]
    print(f"[stratified] {len(todo)} to solve ({len(done)} already done)", flush=True)
    if not todo:
        _summarize(out_path)
        return

    gn.solve_one(aw.FORMS["textbook"], n_gen=2, max_nodes=8)  # warm numba pre-fork
    from multiprocessing import Pool
    n_solved = 0
    t0 = time.time()
    tasks = [(rec, args.budget2, args.max_len) for rec in todo]
    with Pool(processes=args.workers, maxtasksperchild=16) as pool, open(out_path, "a") as f:
        for i, res in enumerate(pool.imap_unordered(_solve_task, tasks)):
            if res["solved"]:
                n_solved += 1
                print(f"*** SOLVED *** mkey={res['mkey'][:12]} tl={res['total_len']} "
                      f"({res['form']},{res['word']}) nodes={res['nodes']} "
                      f"path_verified={res.get('path_verified')}", flush=True)
                try:
                    ok, errs, cpath = pe.build_chain_cert(res, args.budget2)
                    res["cert_verified"] = bool(ok)
                    res["cert_path"] = cpath
                    res["cert_errors"] = errs[:5]
                    print(f"*** CERT {'VERIFIED' if ok else 'FAILED'} *** {cpath}", flush=True)
                except Exception as e:
                    import traceback
                    res["cert_verified"] = False
                    res["cert_exc"] = repr(e)
                    print(f"cert build EXC: {e}\n{traceback.format_exc()[-1200:]}", flush=True)
            f.write(json.dumps(res) + "\n")
            f.flush()
            os.fsync(f.fileno())
            if (i + 1) % 100 == 0:
                el = time.time() - t0
                rate = (i + 1) / el if el else 0
                eta = (len(todo) - i - 1) / rate if rate else 0
                print(f"  [{i + 1}/{len(todo)}] solved={n_solved} "
                      f"({rate:.1f}/s ETA {eta / 60:.0f}m)", flush=True)
    print(f"[stratified] done: {n_solved} solved / {len(todo)} attempted", flush=True)
    _summarize(out_path)


def _summarize(out_path):
    by_len_floor = defaultdict(Counter)
    solved = []
    for line in open(out_path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        by_len_floor[r["total_len"]][r["min_total_len"]] += 1
        if r["solved"]:
            solved.append(r)
    print("\n[summary] floor(min_total_len) distribution per candidate length bucket:")
    for L in sorted(by_len_floor):
        print(f"  total_len={L:>3}: {dict(sorted(by_len_floor[L].items()))}")
    print(f"[summary] SOLVED: {len(solved)}"
          + (" — " + ", ".join(f"{s['mkey'][:10]}(tl={s['total_len']},"
             f"cert={s.get('cert_verified')})" for s in solved) if solved else ""))


if __name__ == "__main__":
    main()
