"""Greedy @ B from nonsym-ladder Aut-min best_rep (bench60).

Reuses climb rows from ``covbeam_nonsym_b1kfull_subset60.jsonl`` (no re-climb).
Designed for Colab at B=10_000; locally hard-capped at 1_000.

    # Colab / production:
    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_covbeam_greedy_from_climb \\
        --budget 10000 --ids 596,605,610,622,623,624,625,636,637,638,639

    # Local smoke (≤1000 only):
    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_covbeam_greedy_from_climb \\
        --budget 1000 --ids 0,496
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.search.greedy_baseline import greedy_search  # noqa: E402

ROOT = _d
CLIMB_JSONL = os.path.join(
    ROOT, "results", "comparison", "covbeam_nonsym_b1kfull_subset60.jsonl")
OUT_DIR = os.path.join(ROOT, "results", "comparison")
LOCAL_CAP = 1000
ORIG_CAP = 24


def search_cap(r1, r2, base=ORIG_CAP, headroom=16):
    return max(base, max(len(r1), len(r2)) + headroom)


def load_climb(path=CLIMB_JSONL):
    out = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            out[str(r["pres_id"])] = r
    return out


def run(budget, ids=None, climb_path=CLIMB_JSONL, out_stem=None,
        allow_over_local_cap=False):
    if budget > LOCAL_CAP and not allow_over_local_cap:
        # Colab sets --allow-over-local-cap. Never default-on.
        raise SystemExit(
            f"budget={budget} > local cap {LOCAL_CAP}. "
            f"Pass --allow-over-local-cap only on Colab/production hosts.")
    climb = load_climb(climb_path)
    if ids is None:
        todo = sorted(climb, key=lambda x: (len(x), x))
    else:
        todo = [str(i) for i in ids]
        missing = [i for i in todo if i not in climb]
        if missing:
            raise SystemExit(f"ids not in climb jsonl: {missing}")

    stem = out_stem or f"covbeam_nonsym_g{budget}_from_climb_subset60"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_jsonl = os.path.join(OUT_DIR, f"{stem}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{stem}.csv")

    done = set()
    if os.path.exists(out_jsonl):
        with open(out_jsonl) as f:
            for line in f:
                if line.strip():
                    done.add(str(json.loads(line)["pres_id"]))
        print(f"resume: {len(done)} rows already in {out_jsonl}")

    results = []
    t0 = time.perf_counter()
    with open(out_jsonl, "a") as jf:
        for i, pid in enumerate(todo):
            if pid in done:
                continue
            c = climb[pid]
            br = c["best_rep"]
            if isinstance(br, str):
                br = json.loads(br)
            r1, r2 = br[0], br[1]
            cap = int(c.get("treat_cap") or search_cap(r1, r2))
            g = greedy_search(r1, r2, budget, max_relator_length=cap)
            row = {
                "pres_id": pid,
                "budget": budget,
                "treat_cap": cap,
                "best_rep": list(br),
                "mu_in": c["mu_in"],
                "best_mu": c["best_mu"],
                "solved": bool(g["solved"]),
                "nodes_explored": int(g["nodes_explored"]),
                "path_length": g.get("path_length"),
                "min_relator_length": g.get("min_relator_length"),
                "source_climb": climb_path,
            }
            jf.write(json.dumps(row) + "\n")
            jf.flush()
            results.append(row)
            print(
                f"  [{i+1:02d}/{len(todo)}] ms{pid}: "
                f"solved={row['solved']} nodes={row['nodes_explored']} "
                f"cap={cap}",
                flush=True)

    # Rewrite CSV from full jsonl (resume-safe).
    all_rows = []
    with open(out_jsonl) as f:
        for line in f:
            if line.strip():
                all_rows.append(json.loads(line))
    if all_rows:
        fields = list(all_rows[0].keys())
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in all_rows:
                flat = dict(r)
                flat["best_rep"] = json.dumps(r["best_rep"])
                w.writerow(flat)
    n_sol = sum(1 for r in all_rows if r["solved"])
    print(f"done: {n_sol}/{len(all_rows)} solved @ budget {budget}; "
          f"wall {time.perf_counter()-t0:.1f}s")
    print(f"wrote {out_jsonl}")
    return out_jsonl, out_csv


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--ids", type=str, default=None,
                    help="comma-separated pres_ids; default=all 60")
    ap.add_argument("--climb", type=str, default=CLIMB_JSONL)
    ap.add_argument("--out-stem", type=str, default=None)
    ap.add_argument("--allow-over-local-cap", action="store_true",
                    help="required for budget > 1000 (Colab only)")
    args = ap.parse_args()
    ids = None
    if args.ids:
        ids = [s.strip() for s in args.ids.split(",") if s.strip()]
    run(args.budget, ids=ids, climb_path=args.climb, out_stem=args.out_stem,
        allow_over_local_cap=args.allow_over_local_cap)


if __name__ == "__main__":
    main()
