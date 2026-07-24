"""The three-way cost table: standard greedy vs best CoV vs the tuned heuristic.

Every arm at the **same** node budget (10,000) and the **same** per-relator cap (24),
on the same 60 benchmark presentations, reporting both axes — nodes explored and
path length. The existing comparison CSVs carry nodes at three different budgets
(10k / 100k / 1M) and path length for only two of the arms, so a matched table has
to be computed rather than joined.

* **greedy** and **best CoV** come from ``greedy_vs_bestcov_subset60_b10000.csv``
  (``greedy_nodes``/``greedy_path``; ``cov_nodes``/``cov_path`` = the cheapest of the
  ~170 subword-CoV starts for that presentation).
* **heuristic** is run here: ``hsolve.greedy_search_h`` with ``RECOMMENDED``.
* **control** is ``greedy_search_h(config=None)`` — length-only ordering. It must
  reproduce the greedy column pop for pop; the run refuses to write if it does not.

Cap 24 for the heuristic, not the recommended 48: the arms must share a cap for the
comparison to be about the ordering (caps 24 and 48 solve identically at this budget).

    .venv/bin/python3 -m experiments.heuristic_search.three_way_b10k
"""

import csv
import json
import os
import time

from experiments.heuristic_search.hsolve import RECOMMENDED, greedy_search_h

SRC = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
OUT = "results/comparison/three_way_b10k_subset60.csv"
BUDGET = 10_000
CAP = 24


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


def main():
    root = _repo_root()
    rows = list(csv.DictReader(open(os.path.join(root, SRC))))
    out, drift = [], []
    t0 = time.time()
    for i, r in enumerate(rows):
        ctrl = greedy_search_h(r["r1"], r["r2"], BUDGET, max_relator_length=CAP, config=None)
        heur = greedy_search_h(r["r1"], r["r2"], BUDGET, max_relator_length=CAP, config=RECOMMENDED)
        if int(ctrl["nodes_explored"]) != int(r["greedy_nodes"]) or \
                bool(ctrl["solved"]) != (r["greedy_solved"] == "True"):
            drift.append((r["pres_id"], r["greedy_nodes"], ctrl["nodes_explored"]))
        out.append({
            "pres_id": int(r["pres_id"]), "bin": int(r["bin"]), "aut_class": int(r["aut_class"]),
            "start_length": int(r["start_length"]), "r1": r["r1"], "r2": r["r2"],
            "greedy_solved": r["greedy_solved"] == "True",
            "greedy_nodes": int(r["greedy_nodes"]),
            "greedy_path": r["greedy_path"] or "",
            "bestcov_solved": r["cov_solved"] == "True",
            "bestcov_nodes": int(r["cov_nodes"]) if r["cov_nodes"] else "",
            "bestcov_path": r["cov_path"] or "",
            "bestcov_z": r["best_z"], "bestcov_class": r["best_class"],
            "n_cov_tried": int(r["n_cov_tried"]),
            "heur_solved": bool(heur["solved"]),
            "heur_nodes": int(heur["nodes_explored"]),
            "heur_path": int(heur["path_length"]) if heur["solved"] else "",
        })
        if (i + 1) % 10 == 0:
            print(f"[3way] {i+1}/{len(rows)}  {time.time()-t0:.0f}s", flush=True)

    if drift:
        raise SystemExit(f"control gate FAILED — length-only ordering does not reproduce "
                         f"the greedy column on {len(drift)} rows: {drift[:5]}")
    dest = os.path.join(root, OUT)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"[3way] control gate PASSED on all {len(rows)} rows")
    print(f"[3way] wrote {dest} in {time.time()-t0:.0f}s")
    print(json.dumps({
        "solved_greedy": sum(r["greedy_solved"] for r in out),
        "solved_bestcov": sum(r["bestcov_solved"] for r in out),
        "solved_heur": sum(r["heur_solved"] for r in out),
    }, indent=2))


if __name__ == "__main__":
    main()
