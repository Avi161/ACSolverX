"""Minimal solving cap per rank-2 row, with closure records below it.

For every row of a CSV (columns ``name, r1, r2`` by default) run ``capbfs.bfs``
at every cap from the row's floor (its longest cyclically reduced relator) up
to ``--max-cap``, stopping at the first cap that SOLVES or that exhausts the
state budget.  Every run is written as one JSON line, so a row's record is a
ladder of CLOSED-unsolved results followed by either a SOLVED result (whose
cap is then the row's minimal solving cap, and whose path is a replayable
certificate) or a budget-exhausted result (minimal cap unknown beyond the
last closed cap).

    python run_min_cap.py --csv rows.csv --max-cap 14 --out out.jsonl
    python run_min_cap.py --csv rows.csv --min-cap 15 --max-cap 16 \
        --skip-from out.jsonl --out out2.jsonl      # continue a ladder

``--shard i --nshards n`` takes every n-th row starting at i, for running
several processes side by side.  ``--skip-from`` skips rows that a previous
output already SOLVED or exhausted.  ``verify_path.py`` replays the solved
rows of the output.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capbfs  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", required=True)
    ap.add_argument("--name-col", default="name")
    ap.add_argument("--r1-col", default="r1")
    ap.add_argument("--r2-col", default="r2")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--min-cap", type=int, default=1)
    ap.add_argument("--max-cap", type=int, default=14)
    ap.add_argument("--max-states", type=int, default=5_000_000)
    ap.add_argument("--skip-from", action="append", default=[],
                    help="jsonl of earlier runs; rows already solved or "
                         "budget-exhausted there are skipped")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    done = set()
    for path in args.skip_from:
        with open(path) as fh:
            for line in fh:
                if line.strip():
                    rec = json.loads(line)
                    if rec.get("solved") or rec.get("budget_exhausted"):
                        done.add(rec["name"])

    with open(args.csv, newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows = rows[args.shard::args.nshards]

    t_all = time.perf_counter()
    n_runs = 0
    with open(args.out, "a") as out:
        for row in rows:
            name = row[args.name_col]
            r1, r2 = row[args.r1_col], row[args.r2_col]
            if name in done:
                continue
            floor = max(len(capbfs._cyc_reduce_str(r1)),
                        len(capbfs._cyc_reduce_str(r2)))
            for cap in range(max(floor, args.min_cap), args.max_cap + 1):
                res = capbfs.json_ready(
                    capbfs.bfs(r1, r2, cap, args.max_states, True))
                res.update(name=name, r1=r1, r2=r2)
                for extra in ("bin", "aut_class", "n_members"):
                    if extra in row:
                        res[extra] = row[extra]
                out.write(json.dumps(res) + "\n")
                out.flush()
                n_runs += 1
                sys.stderr.write("%s cap=%d states=%d %s %.1fs\n" % (
                    name, cap, res["states"],
                    "SOLVED" if res["solved"] else
                    "BUDGET" if res["budget_exhausted"] else "closed",
                    res["seconds"]))
                if res["solved"] or res["budget_exhausted"]:
                    break
    sys.stderr.write("%d runs, %.0f s\n" % (n_runs, time.perf_counter() - t_all))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
