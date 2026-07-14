"""Build the combined solved+unsolved benchmark for the Branch-A (No-CoV) sweep.

Merges the efficiency ladder (``benchmark_subsets.py``) with the reach tier
(``reach_tier.py``): solved presentations to measure speedup on, and
genuinely-unsolved ones to measure reach on, in one file per rung.

    PAIRING = {11: (10, 1), 22: (20, 2), 44: (40, 4), 66: (60, 6)}   # combined_id: (ladder, reach)

Ladder rows and reach rows carry different fields (a ladder row has no
``bar_to_beat``; a reach row has no ``baseline_solved_at_50k``), so every row
gets five common keys (``name``, ``source``, ``r1``, ``r2``,
``base_total_length``) plus whichever family-specific extras its source row
carried. ``source`` here is ``"ladder"`` / ``"reach"`` -- not to be confused
with the reach tier's own ``source`` column (``"AK(3)"`` / ``"ms_reps_unsolved
/ ACA class"``), which is deliberately dropped rather than carried through,
since it would collide.

Writes ``results/benchmark/combined/``::

    .venv/bin/python3 -m experiments.analysis.combined_benchmark
"""

import csv
import json
import os

REPO = os.path.abspath(__file__)
while not (os.path.isdir(os.path.join(REPO, "experiments"))
           and os.path.isdir(os.path.join(REPO, "data"))):
    REPO = os.path.dirname(REPO)

SUBSETS_DIR = os.path.join(REPO, "results", "benchmark", "subsets")
REACH_DIR = os.path.join(REPO, "results", "benchmark", "reach")
OUT_DIR = os.path.join(REPO, "results", "benchmark", "combined")

PAIRING = {11: (10, 1), 22: (20, 2), 44: (40, 4), 66: (60, 6)}
COMPARE_BUDGET = 50_000

PURPOSE = ("ladder rows measure efficiency vs a solved baseline; reach rows measure reach "
           "on genuinely-unsolved problems (no speedup ratio exists for them)")

LADDER_EXTRAS = ("pres_id", "bin", "aut_class", "nodes_1M", "path_1M", "start_length",
                  "baseline_solved_at_50k", "baseline_nodes_at_50k", "baseline_path_at_50k",
                  "baseline_min_relator_length_at_50k", "baseline_progress_at_50k")
REACH_EXTRAS = ("slot", "aca_class_id", "n_members", "baseline_start_length",
                 "baseline_min_relator_length", "baseline_progress", "baseline_solved",
                 "bar_to_beat", "aut_min_rep_r1", "aut_min_rep_r2",
                 "aut_min_rep_total_length", "note", "members")


def _ladder_row(r):
    row = {
        "name": f"ms{r['pres_id']}",
        "source": "ladder",
        "r1": r["r1"],
        "r2": r["r2"],
        "base_total_length": len(r["r1"]) + len(r["r2"]),
    }
    for k in LADDER_EXTRAS:
        row[k] = r[k]
    return row


def _reach_row(r):
    row = {
        "name": r["name"],
        "source": "reach",
        "r1": r["r1"],
        "r2": r["r2"],
        "base_total_length": len(r["r1"]) + len(r["r2"]),
    }
    for k in REACH_EXTRAS:
        if k in r:                  # "note"/"members" are only on some reach rows
            row[k] = r[k]
    return row


def build_combined(combined_id, out_dir=None):
    if combined_id not in PAIRING:
        raise ValueError(f"unknown combined_id: {combined_id!r} (must be one of {list(PAIRING)})")
    n_ladder, n_reach = PAIRING[combined_id]
    out_dir = out_dir or OUT_DIR

    subset_name = f"benchmark_subset_{n_ladder}.json"
    reach_name = f"reach_tier_{n_reach}.json"
    with open(os.path.join(SUBSETS_DIR, subset_name)) as f:
        subset_doc = json.load(f)
    with open(os.path.join(REACH_DIR, reach_name)) as f:
        reach_doc = json.load(f)

    rows = ([_ladder_row(r) for r in subset_doc["subset"]]
            + [_reach_row(r) for r in reach_doc["tier"]])

    doc = {
        "combined_id": combined_id,
        "size": len(rows),
        "n_ladder": len(subset_doc["subset"]),
        "n_reach": len(reach_doc["tier"]),
        "ladder_source": subset_name,
        "reach_source": reach_name,
        "comparison_budget": COMPARE_BUDGET,
        "pairing": list(PAIRING[combined_id]),
        "purpose": PURPOSE,
        "rows": rows,
    }

    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, f"benchmark_combined_{combined_id}.json")
    csv_path = os.path.join(out_dir, f"benchmark_combined_{combined_id}.csv")
    with open(json_path, "w") as f:
        json.dump(doc, f, indent=2)

    fieldnames = list(dict.fromkeys(
        ["name", "source", "r1", "r2", "base_total_length"]
        + list(LADDER_EXTRAS) + list(REACH_EXTRAS)))
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(rows)

    return json_path, csv_path, doc


def load_combined(combined_id, out_dir=None):
    out_dir = out_dir or OUT_DIR
    with open(os.path.join(out_dir, f"benchmark_combined_{combined_id}.json")) as f:
        return json.load(f)


def main():
    for combined_id, (n_ladder, n_reach) in PAIRING.items():
        json_path, csv_path, doc = build_combined(combined_id)
        assert (doc["n_ladder"], doc["n_reach"]) == (n_ladder, n_reach), (
            f"combined_{combined_id}: expected {n_ladder}+{n_reach}, "
            f"got {doc['n_ladder']}+{doc['n_reach']}")
        for r in doc["rows"]:
            assert r["r1"] and r["r2"], f"combined_{combined_id}: row {r['name']} missing r1/r2"
        print(f"combined_{combined_id:<2} {doc['n_ladder']:>2} ladder + {doc['n_reach']} reach "
              f"= {doc['size']:>2} rows -> {os.path.relpath(json_path, REPO)}")


if __name__ == "__main__":
    main()
