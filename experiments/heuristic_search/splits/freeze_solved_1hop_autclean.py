"""Freeze solved-side 1-hop Aut orbits, excluding the FULL selection Aut union.

Supersedes ``solved_1hop_nob60.json`` (kept write-once; do not overwrite it).
This freeze additionally excludes campaign_12h / scale10k selection surfaces
that chose the S / S+K+MK arms (advisor REVISE 2026-07-29).

Pool: ``data/cov/unique_aut_orbits_1hop/unique_aut_orbits_1hop.csv`` with
``source_side == solved``.

    python3 -m experiments.heuristic_search.splits.freeze_solved_1hop_autclean
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
CAMP = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h")
SCALE = os.path.join(ROOT, "results", "heuristic_search", "scale10k")
OUT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                   "solved_1hop_autclean.json")

# Selection surfaces that chose / ranked the arms we will evaluate.
JSONL_EXCLUDE = [
    os.path.join(CAMP, "s_grid_hard.jsonl"),
    os.path.join(CAMP, "arms_on_band.jsonl"),
    os.path.join(CAMP, "arms_hard_full.jsonl"),
    os.path.join(CAMP, "aut_disjoint_null.jsonl"),
]
JSON_EXCLUDE = [
    os.path.join(SCALE, "slice_fresh_hard.json"),
    os.path.join(SCALE, "slice_l_stratified.json"),
]


def _rep(r1, r2):
    _, rep = aut_min((r1, r2))
    return rep


def _add_jsonl(exclude, path, counts):
    n0 = len(exclude)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            exclude.add(_rep(r["r1"], r["r2"]))
    counts[os.path.basename(path)] = len(exclude) - n0


def _add_json_rows(exclude, path, counts):
    n0 = len(exclude)
    data = json.load(open(path))
    for r in data["rows"]:
        exclude.add(_rep(r["r1"], r["r2"]))
    counts[os.path.basename(path)] = len(exclude) - n0


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"refusing to overwrite existing freeze: {OUT}")

    warm()
    exclude = set()
    counts = {}

    for r in json.load(open(BENCH60))["subset"]:
        exclude.add(_rep(r["r1"], r["r2"]))
    counts["bench60"] = len(exclude)

    n0 = len(exclude)
    for r in bench66():
        exclude.add(_rep(r["r1"], r["r2"]))
    counts["bench66_new"] = len(exclude) - n0

    n0 = len(exclude)
    sp = json.load(open(AC1M_SPLIT))
    for side in ("train_rows", "holdout_rows"):
        for r in sp[side]:
            exclude.add(_rep(r["r1"], r["r2"]))
    counts["splits_ac1m_hard_aut"] = len(exclude) - n0

    for path in JSONL_EXCLUDE:
        _add_jsonl(exclude, path, counts)
    for path in JSON_EXCLUDE:
        _add_json_rows(exclude, path, counts)

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
            "short_relator": min(len(r["rep_r1"]), len(r["rep_r2"])) <= 2,
        })
    kept.sort(key=lambda r: (r["kind"] != "seed", r["mu"], r["name"]))

    n_seed = sum(1 for r in kept if r["kind"] == "seed")
    n_moved = sum(1 for r in kept if r["kind"] == "moved_cov")
    n_short = sum(1 for r in kept if r["short_relator"])
    out = {
        "kind": "solved_1hop_autclean",
        "created": datetime.now(timezone.utc).isoformat(),
        "supersedes": "results/heuristic_search/splits/solved_1hop_nob60.json",
        "source_csv": "data/cov/unique_aut_orbits_1hop/unique_aut_orbits_1hop.csv",
        "n_solved_side_in": len(rows_in),
        "n_kept": len(kept),
        "n_seed": n_seed,
        "n_moved_cov": n_moved,
        "n_short_relator": n_short,
        "excluded_aut": {
            "union_size": len(exclude),
            "removed_from_pool": len(rows_in) - len(kept),
            "by_source_new_reps": counts,
        },
        "selected_on": (
            "skmk_aut_tune train (AC1M-hard Aut) + campaign_12h S-grid/arms bands "
            "+ scale10k slices"
        ),
        "evaluated_on": "solved_1hop_autclean (this freeze)",
        "note": (
            "Presents trivial group via stable CoV from solved MS seeds; "
            "unstable trivializability is what the search tests. "
            "Stratify seed vs moved_cov and short_relator when reporting. "
            "Eval searches the aut_min representative."
        ),
        "rows": kept,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"[freeze] wrote {OUT}: kept={len(kept)} "
          f"(seed={n_seed} moved={n_moved} short={n_short}); "
          f"exclude_union={len(exclude)}; removed={len(rows_in)-len(kept)}",
          flush=True)
    print(f"[freeze] new-reps by source: {counts}", flush=True)


if __name__ == "__main__":
    main()
