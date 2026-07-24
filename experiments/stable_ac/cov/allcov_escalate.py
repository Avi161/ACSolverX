"""Escalate the node budget on the CoV starts the b10k sweep left unsolved.

The subword family is a *pure function of the presentation* (PIPELINE.md §2) —
``enumerate_cov`` already returned every member at b10k, so "all possible CoV"
is exhausted and the only knob left is the budget. This runner re-runs that same
family at a higher budget and records, per presentation, the cheapest CoV start
that solves (or proves none does at this budget).

Deduplication is by **output pair**, not by presentation: the search depends only
on ``(r1, r2, cap, budget)``, and 909 of the 1366 starts across the eight rows are
distinct. It is deliberately NOT by Aut-orbit — 91% of the family is a relabel of
the input orbit, and a relabel is not a no-op to a solver that reads strings.

Resume is keyed on ``(r1, r2, budget)`` — the pair is what was searched. The
``(pres_id, z_word, iso_gen, iso_index)`` provenance of every pair that produced
it is carried in the row so a result maps back to each presentation that owns it.

    .venv/bin/python3 -m experiments.stable_ac.cov.allcov_escalate \
        --budget 100000 --workers 5 --seconds 0
"""

import argparse
import json
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

CSV = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
OUT_DIR = "results/stable_ac/cov/allcov_escape"
CAP_HEADROOM = 16
DEFAULT_CAP = 24


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()


def build_tasks():
    """(r1, r2, cap) -> provenance list, over every CoV start of the unsolved rows."""
    import csv as _csv
    from experiments.stable_ac.cov import cov
    from experiments.greedy_tests.spec.words import str_to_word, word_to_str

    rows = list(_csv.DictReader(open(os.path.join(ROOT, CSV))))
    unsolved = [r for r in rows if r["cov_solved"] != "True"]
    tasks = {}
    for r in unsolved:
        pid = int(r["pres_id"])
        for res in cov.enumerate_cov(str_to_word(r["r1"]), str_to_word(r["r2"])):
            a, b, cap = word_to_str(res.r1), word_to_str(res.r2), res.cap
            prov = {"pres_id": pid, "z_word": word_to_str(res.z_word),
                    "iso_gen": res.iso_gen, "iso_index": res.iso_index}
            tasks.setdefault((a, b, cap), []).append(prov)
    return [(a, b, cap, prov) for (a, b, cap), prov in tasks.items()], unsolved


def _search(job):
    a, b, cap, budget = job
    from experiments import run_baseline as rb
    t = time.time()
    out = rb.greedy_search(a, b, budget, max_relator_length=cap,
                           cyclic_reduce=True, high_speedup=True)
    row = {"r1": a, "r2": b, "cap": cap, "node_budget": budget,
           "solved": bool(out["solved"]), "nodes_explored": int(out["nodes_explored"]),
           "min_relator_length": int(out["min_relator_length"]),
           "seconds": round(time.time() - t, 2)}
    if out["solved"]:
        # the compact solver returns no path; the normal one does (run_baseline's pattern)
        slow = rb.greedy_search(a, b, budget, max_relator_length=cap,
                                cyclic_reduce=True, high_speedup=False)
        row["path_length"] = int(slow["path_length"])
        row["path_moves"] = slow.get("path_moves")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--seconds", type=int, default=0, help="0 = run to completion")
    args = ap.parse_args()

    out_dir = os.path.join(ROOT, OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"allcov_b{args.budget}_8rows_subnc2pxysb.jsonl")

    tasks, unsolved = build_tasks()
    done = set()
    if os.path.exists(path):
        with open(path) as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    d = json.loads(ln)
                except json.JSONDecodeError:
                    break  # torn trailing line: everything after it is unreadable
                done.add((d["r1"], d["r2"]))
    todo = [(a, b, cap, prov) for (a, b, cap, prov) in tasks if (a, b) not in done]
    print(f"[allcov] budget={args.budget} pairs={len(tasks)} done={len(done)} todo={len(todo)} "
          f"workers={args.workers} presentations={len(unsolved)}", flush=True)
    if not todo:
        print("[allcov] nothing to do", flush=True)
        return

    prov_of = {(a, b): prov for (a, b, cap, prov) in tasks}
    t0 = time.time()
    n = 0
    ctx = multiprocessing.get_context("spawn")
    with open(path, "a") as fh, ProcessPoolExecutor(max_workers=args.workers,
                                                    mp_context=ctx) as pool:
        futs = {pool.submit(_search, (a, b, cap, args.budget)): (a, b)
                for (a, b, cap, prov) in todo}
        for fut in as_completed(futs):
            row = fut.result()
            row["provenance"] = prov_of[(row["r1"], row["r2"])]
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            n += 1
            if row["solved"] or n % 25 == 0:
                el = time.time() - t0
                print(f"[allcov] {n}/{len(todo)}  {el:7.0f}s  "
                      f"{'SOLVED ' if row['solved'] else '       '}"
                      f"nodes={row['nodes_explored']} minlen={row['min_relator_length']} "
                      f"eta={el / max(n, 1) * (len(todo) - n) / 60:.0f}min", flush=True)
            if args.seconds and time.time() - t0 > args.seconds:
                print("[allcov] time budget hit — stopping (resume-safe)", flush=True)
                for f in futs:
                    f.cancel()
                break
    print(f"[allcov] wrote {n} rows to {path} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
