#!/usr/bin/env python3
"""Independent L>24 test: can lifting the per-relator cap trivialize AK(3)?

Everything writes under experiments/test_cap/ ONLY. We never edit the global gn.L=24
(the flat-format / RL-env padding width); the lifted cap is passed as the ``max_len``
PARAMETER to NRelatorSolver, whose byte keys are variable-width, so max_len is a pure
prune threshold with no IO-format impact.

Arms (run in sequence; RAM-heavy arms never overlap):
  gate     positive control — a stabilized trivial MS presentation still solves+verifies
  search   stabilized 3-gen greedy on <x,y,z | r1,r2,z.w^-1> at max_len in {24, 48},
           forms textbook+rep, hero words. Does letting relators exceed 24 in the SEARCH
           trivialize AK(3)? Records solved / floor(min_total_len) / visited.
  harvest  plateau_elim.py harvest+merge with the QUOTIENT caps lifted (l_cap 48,
           harvest_tl_cap 40, merge_tl_cap 40) -> eliminated 2-gen quotients of total
           length 25-40 the L=24 pipeline never produced. (solve is solve_stratified.py)

Resumable append-only JSONL. Runner: .venv/bin/python3 (numba). Sized for a 16 GB Mac.
"""
import argparse
import json
import os
import resource
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
PROOF = os.path.join(ROOT, "experiments", "stable_ac", "ak3_stable_proof")
for p in (PROOF, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

# Redirect all plateau_elim output into test_cap; the real results/.../laneD is untouched.
OUT = os.environ.get("ACX_TESTCAP_DIR") or HERE
LANE_D = os.path.join(OUT, "laneD")
CERTS = os.path.join(OUT, "certs")
os.environ["ACX_LANED_DIR"] = LANE_D
os.environ["ACX_CERTS_DIR"] = CERTS

import greedy_nrel as gn  # noqa: E402
import ak3_words as aw  # noqa: E402

HERO = ["xyx", "yxy", "xxx", "yyyy", "Xyxy", "YXyxy", "x", "y"]


def _rss_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6)


def gate():
    """Positive control: stabilize a known-trivial MS presentation (idx 0) with z=x and
    confirm the 3-gen greedy solves AND the path verifies. Proves the solver + stabilize
    + verify chain is live in this folder before we trust any negative."""
    labels = json.load(open(os.path.join(ROOT, "results", "labels_1190.json")))
    p0 = next(r for r in labels if r["idx"] == 0)["presentation"]
    p0_stab = aw.stabilize_with_word(p0, aw.parse("x"))
    res, _ = gn.solve_one(p0_stab, n_gen=3, max_len=24, max_nodes=50000)
    ok = bool(res["solved"] and res["path_verified"])
    print(f"[gate] positive control (stabilized MS idx0, z=x): solved={res['solved']} "
          f"verified={res['path_verified']} nodes={res['nodes_explored']} -> "
          f"{'OK' if ok else '*** GATE FAILED ***'}", flush=True)
    return ok


def run_stab(form, w, budget, max_len):
    """Real production search: stabilized 3-gen greedy with max_len passed as a PARAMETER.
    Mirrors plateau_elim.run_stabilized exactly except max_len is not pinned to gn.L."""
    sflat = aw.stabilize_with_word(aw.FORMS[form], w)
    rels = gn.flat_to_relators(sflat, 3)
    blocked = [gn.null_revert_state(sflat, 3)]
    solver = gn.NRelatorSolver(rels, 3, max_nodes=budget, max_len=max_len,
                               blocked_states=blocked)
    t0 = time.time()
    path, nodes, _ = solver.solve()
    rec = dict(solved=path is not None, min_total_len=int(solver.min_total_len),
               nodes=int(nodes), visited=len(solver.visited),
               wall_s=round(time.time() - t0, 1), rss_mb=_rss_mb())
    if path is not None:
        rec["path_verified"] = bool(gn.verify_path(path["states"], 3))
        rec["path_states"] = [[[int(a) for a in r] for r in st] for st in path["states"]]
    return rec


def phase_search(args):
    out_path = os.path.join(OUT, "search_L.jsonl")
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                pass
    forms = args.forms.split(",")
    words = args.words.split(",") if args.words else HERO
    maxlens = [int(x) for x in args.maxlens.split(",")]
    tasks = [(f, w, ml) for f in forms for w in words for ml in maxlens]
    print(f"[search] {len(tasks)} runs (forms={forms} words={words} maxlens={maxlens} "
          f"budget={args.budget}); {len(done)} already done", flush=True)
    with open(out_path, "a") as f:
        for i, (form, word, ml) in enumerate(tasks):
            key = f"{form}|{word}|{ml}|{args.budget}"
            if key in done:
                continue
            w = aw.parse(word)
            rec = run_stab(form, w, args.budget, ml)
            rec.update(key=key, form=form, word=word, max_len=ml, budget=args.budget)
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
            flag = "  *** SOLVED ***" if rec["solved"] else ""
            print(f"  [{i + 1}/{len(tasks)}] {form}/{word} L={ml}: "
                  f"solved={rec['solved']} floor={rec['min_total_len']} "
                  f"visited={rec['visited']:,} nodes={rec['nodes']:,} "
                  f"{rec['wall_s']}s rss={rec['rss_mb']}MB{flag}", flush=True)
    print("[search] done", flush=True)


def phase_harvest_merge(args):
    """Shell plateau_elim.py for harvest+merge with the QUOTIENT caps lifted. Output is
    redirected into test_cap via the env vars set at import time."""
    os.makedirs(LANE_D, exist_ok=True)
    words = args.words.split(",") if args.words else HERO
    env = dict(os.environ)
    base = [sys.executable, "-u", os.path.join(PROOF, "plateau_elim.py")]
    common = ["--forms", args.forms, "--words", ",".join(words),
              "--budget", str(args.harvest_budget), "--l_cap", str(args.l_cap),
              "--harvest_tl_cap", str(args.htl), "--merge_tl_cap", str(args.mtl),
              "--workers", str(args.workers), "--merge_workers", str(args.workers)]
    print(f"[harvest] l_cap={args.l_cap} htl={args.htl} mtl={args.mtl} "
          f"budget={args.harvest_budget} workers={args.workers}", flush=True)
    subprocess.run(base + ["--phase", "harvest"] + common, env=env, check=True)
    subprocess.run(base + ["--phase", "merge"] + common, env=env, check=True)
    merged = os.path.join(LANE_D, "merged.jsonl")
    n = sum(1 for _ in open(merged)) if os.path.exists(merged) else 0
    print(f"[harvest] merged.jsonl: {n} unique candidates", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--forms", default="textbook,rep")
    ap.add_argument("--words", default=None)  # default: HERO
    ap.add_argument("--maxlens", default="24,48")
    ap.add_argument("--budget", type=int, default=100_000)       # arm 2 search
    ap.add_argument("--harvest_budget", type=int, default=100_000)  # arm 3 harvest
    ap.add_argument("--l_cap", type=int, default=48)
    ap.add_argument("--htl", type=int, default=40)
    ap.add_argument("--mtl", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--skip_search", action="store_true")
    ap.add_argument("--skip_harvest", action="store_true")
    args = ap.parse_args()
    if args.quick:
        args.budget = 4_000
        args.harvest_budget = 4_000
        args.words = ",".join(HERO[:2])
    os.makedirs(OUT, exist_ok=True)

    if not gate():
        print("ABORT: positive control failed — pipeline is broken, trust no negative.",
              flush=True)
        sys.exit(1)
    if not args.skip_search:
        phase_search(args)
    if not args.skip_harvest:
        phase_harvest_merge(args)
    print(f"run_captest done. Next: solve_stratified.py (out={OUT})", flush=True)


if __name__ == "__main__":
    main()
