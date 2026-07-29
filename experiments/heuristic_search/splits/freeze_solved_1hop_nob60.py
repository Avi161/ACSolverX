"""Freeze solved-side unique Aut orbits (1-hop CoV), excluding prior-eval Auts.

Pool: ``data/cov/unique_aut_orbits_1hop/unique_aut_orbits_1hop.csv`` with
``source_side == solved`` (113 seeds + 410 moved_cov = 523).

Exclude Aut(F2) overlap with:
  - ``benchmark/subsets/benchmark_subset_60.json`` (and full bench66)
  - ``results/heuristic_search/splits/splits_ac1m_hard_aut.json`` (arm-selection)

Write-once. Refusing to overwrite.

    python3 -m experiments.heuristic_search.splits.freeze_solved_1hop_nob60
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hlab import bench66  # noqa: E402
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

ROOT = _d
SRC = os.path.join(ROOT, "data", "cov", "unique_aut_orbits_1hop",
                   "unique_aut_orbits_1hop.csv")
BENCH60 = os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.json")
AC1M_SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                          "splits_ac1m_hard_aut.json")
OUT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                   "solved_1hop_nob60.json")


def _rep(r1, r2):
    _, rep = aut_min((r1, r2))
    return rep


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"refusing to overwrite existing freeze: {OUT}")

    warm()
    exclude = set()
    for r in json.load(open(BENCH60))["subset"]:
        exclude.add(_rep(r["r1"], r["r2"]))
    n_b60 = len(exclude)
    for r in bench66():
        exclude.add(_rep(r["r1"], r["r2"]))
    n_b66 = len(exclude)
    sp = json.load(open(AC1M_SPLIT))
    for side in ("train_rows", "holdout_rows"):
        for r in sp[side]:
            exclude.add(_rep(r["r1"], r["r2"]))
    n_all = len(exclude)

    rows_in = [r for r in csv.DictReader(open(SRC))
               if r["source_side"] == "solved"]
    kept = []
    seen = set()
    for r in rows_in:
        rep = _rep(r["rep_r1"], r["rep_r2"])
        if rep in exclude or rep in seen:
            continue
        seen.add(rep)
        kept.append({
            "name": r["orbit_id"],
            "r1": r["rep_r1"],
            "r2": r["rep_r2"],
            "kind": r["kind"],
            "source_side": r["source_side"],
            "mu": int(r["mu"]),
            "aut_rep_r1": rep[0],
            "aut_rep_r2": rep[1],
        })
    kept.sort(key=lambda r: (r["kind"] != "seed", r["mu"], r["name"]))

    n_seed = sum(1 for r in kept if r["kind"] == "seed")
    n_moved = sum(1 for r in kept if r["kind"] == "moved_cov")
    out = {
        "kind": "solved_1hop_nob60",
        "created": datetime.now(timezone.utc).isoformat(),
        "source_csv": "data/cov/unique_aut_orbits_1hop/unique_aut_orbits_1hop.csv",
        "n_solved_side_in": len(rows_in),
        "n_kept": len(kept),
        "n_seed": n_seed,
        "n_moved_cov": n_moved,
        "excluded_aut": {
            "bench60": n_b60,
            "bench66_union": n_b66,
            "plus_ac1m_hard_aut": n_all,
            "removed_from_pool": len(rows_in) - len(kept),
        },
        "selected_on": "skmk_aut_tune train (AC1M-hard Aut) + prior S-grid scouts",
        "evaluated_on": "solved_1hop_nob60 (this freeze)",
        "note": ("Presents trivial group via stable CoV from solved MS seeds; "
                 "unstable trivializability is what the search tests. "
                 "Stratify seed vs moved_cov when reporting."),
        "rows": kept,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"[freeze] wrote {OUT}: kept={len(kept)} "
          f"(seed={n_seed} moved={n_moved}); "
          f"excluded_aut_union={n_all}; removed={len(rows_in)-len(kept)}",
          flush=True)


if __name__ == "__main__":
    main()
