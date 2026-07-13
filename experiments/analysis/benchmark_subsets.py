"""Freeze the stable-AC benchmark subsets: 10 / 20 / 40 / 60 presentations.

Reads ``results/benchmark/difficulty_bins.csv`` (see ``difficulty_bins.py``) and
picks ``k = size // 10`` presentations from each of the 10 log-width difficulty
bins.

**Within a bin, members are ordered by ``path_length``, not by nodes.** The bin
already pins ``nodes_explored`` to a x3.37 window -- that is the bin width -- so
there is almost nothing left to spread on there. ``path_length`` inside one bin
runs up to x11 (bin 6: 44 -> 489). Path is also the second axis the comparison
table reports, and the one the bin does *not* control. Ordering by it puts the
node/path off-diagonal on every rung of the ladder for free; ordering by nodes
would hand back 20 presentations sitting on the diagonal, and the path graph
would be a rescaled copy of the nodes graph.

Picks are spaced evenly over the bin's path range, endpoints included, so the
path-cheapest and path-deepest member at that node cost are both on the ladder.
Where a bin holds no more members than are asked for (bins 8 and 9 have exactly
6), every member is taken; ``k=6`` is therefore the ceiling and there is no
subset-80.

The four sizes are **not nested** (50% is not one of {33%, 66%}). That is by
design: screen word families on subset-10, then validate the winner on 40/60 and
have that be a genuine held-out check rather than a re-scoring of the set the
words were tuned on.

Writes ``results/benchmark/subsets/``. Read-only over the baseline jsonl.
"""

import csv
import json
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BINS_CSV = os.path.join(REPO, "results", "benchmark", "difficulty_bins.csv")
OUT_DIR = os.path.join(REPO, "results", "benchmark", "subsets")

SIZES = (10, 20, 40, 60)
N_BINS = 10
COMPARE_BUDGET = 50_000

INT_COLS = ("pres_id", "difficulty_rank", "bin", "bin_lo_nodes", "bin_hi_nodes",
            "nodes_explored", "path_length", "nodes_at_50k", "aut_class",
            "aut_min_total", "aut_orbit_size", "start_length",
            "min_relator_length_at_50k", "progress_at_50k")


def _load_bins():
    with open(BINS_CSV) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for c in INT_COLS:
            r[c] = int(r[c])
        r["log10_nodes"] = float(r["log10_nodes"])
        r["solved_at_50k"] = r["solved_at_50k"] == "True"
        r["path_at_50k"] = int(r["path_at_50k"]) if r["path_at_50k"] not in ("", "None") else None
    if len(rows) != 640:
        raise SystemExit(f"{BINS_CSV}: expected 640 rows, found {len(rows)}")
    return rows


def _pick(members, k):
    """k members evenly spaced over the bin's path_length range, endpoints included.

    Interior ``(i+1)/(k+1)`` positions were tried first and are wrong here. They
    avoid a bin's extremes, which is sensible in a 317-member bin and collapses
    to the middle in a 6-member one: bins 8 and 9 hold 6 members each, so the
    33rd and 66th percentiles are *adjacent* indices, and k=2 returned two near
    clones (625/622: nodes 78,770 vs 78,774, path 665 vs 671). Those are the two
    most valuable rungs on the ladder. Spanning the full range instead yields the
    path-cheapest and path-deepest member at that node cost -- the node/path
    off-diagonal, which is the whole reason the two axes are reported separately.
    """
    ordered = sorted(members, key=lambda r: (r["path_length"], r["nodes_explored"],
                                             r["pres_id"]))
    m = len(ordered)
    if m <= k:                      # bins 8/9 at k=6 -- take everything
        return ordered
    if k == 1:
        return [ordered[(m - 1) // 2]]
    idxs = []
    for i in range(k):
        j = round(i * (m - 1) / (k - 1))
        while j in idxs:            # only reachable when m is barely above k
            j += 1
        idxs.append(j)
    return [ordered[j] for j in sorted(idxs)]


def build(rows, size):
    k = size // N_BINS
    out = []
    for b in range(N_BINS):
        members = [r for r in rows if r["bin"] == b]
        for r in _pick(members, k):
            out.append({
                "pres_id": r["pres_id"],
                "bin": b,
                "r1": r["r1"],
                "r2": r["r2"],
                "nodes_1M": r["nodes_explored"],
                "path_1M": r["path_length"],
                "aut_class": r["aut_class"],
                "start_length": r["start_length"],
                "baseline_solved_at_50k": r["solved_at_50k"],
                "baseline_nodes_at_50k": r["nodes_at_50k"],
                "baseline_path_at_50k": r["path_at_50k"],
                # only meaningful on an unsolved row (bins 8-9); the same key the reach
                # tier scores on, so both tiers are read the same way
                "baseline_min_relator_length_at_50k": r["min_relator_length_at_50k"],
                "baseline_progress_at_50k": r["progress_at_50k"],
            })
    return k, out


def main():
    rows = _load_bins()
    os.makedirs(OUT_DIR, exist_ok=True)
    edges = sorted({(r["bin"], r["bin_lo_nodes"], r["bin_hi_nodes"]) for r in rows})
    built = {}

    for size in SIZES:
        k, subset = build(rows, size)
        built[size] = subset
        doc = {
            "size": len(subset),
            "requested_size": size,
            "per_bin": k,
            "n_bins": N_BINS,
            "comparison_budget": COMPARE_BUDGET,
            "difficulty_variable": "log10(nodes_explored) at the 1M budget (uncensored)",
            "binning": "10 equal-width slices of log10(nodes); each bin is x3.37 the one below",
            "within_bin_selection": ("sort by (path_length, nodes_explored, pres_id); "
                                     "take k evenly spaced positions over the full range, "
                                     "endpoints included (median if k=1). Nodes are already "
                                     "fixed to a x3.37 window by the bin, so path is what "
                                     "is left to spread on."),
            "nested": False,
            "aut_class_note": ("aut_class is the exact Aut(F2)/change-of-variables orbit "
                               "(the 640 are 113 classes). It is a COLUMN, not a dedup key: "
                               "search cost is not an orbit invariant (623 and 636 are "
                               "Aut-equivalent yet cost 59,710 vs 213,882 nodes), and that "
                               "gap is what Branch B exploits. Use it to (a) spot that a "
                               "canonicalising technique collapses same-class rows to "
                               "identical runs, and (b) see the sampling weight -- the four "
                               "hardest picks of subset_20 span only three classes."),
            "aut_classes_in_subset": len({r["aut_class"] for r in subset}),
            "bins": [{"bin": b, "lo_nodes": lo, "hi_nodes": hi} for b, lo, hi in edges],
            "subset": subset,
        }
        with open(os.path.join(OUT_DIR, f"benchmark_subset_{size}.json"), "w") as f:
            json.dump(doc, f, indent=2)
        with open(os.path.join(OUT_DIR, f"benchmark_subset_{size}.csv"), "w",
                  newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(subset[0]))
            w.writeheader()
            w.writerows(subset)

        n_unsolved = sum(not r["baseline_solved_at_50k"] for r in subset)
        hard = [r for r in subset if r["bin"] >= 8]
        print(f"subset_{size:<2} k={k}/bin  {len(subset):>2} presentations  "
              f"| nodes {min(r['nodes_1M'] for r in subset):>5}-"
              f"{max(r['nodes_1M'] for r in subset):<6} "
              f"| path {min(r['path_1M'] for r in subset):>3}-"
              f"{max(r['path_1M'] for r in subset):<3} "
              f"| unsolved@50k: {n_unsolved:>2} "
              f"| Aut classes: {len({r['aut_class'] for r in subset}):>2}/{len(subset):<2} "
              f"(bins 8-9: {len({r['aut_class'] for r in hard})}/{len(hard)})")

    # ---- the 20 in full, since it is the working default -------------------
    print("\nbenchmark_subset_20:")
    print(f"  {'bin':>3} {'pres_id':>7} {'nodes':>7} {'path':>5} {'aut':>4}  {'@50k':>5}")
    seen = Counter(r["aut_class"] for r in built[20])
    for r in built[20]:
        dup = "  <- shares an Aut class" if seen[r["aut_class"]] > 1 else ""
        print(f"  {r['bin']:>3} {r['pres_id']:>7} {r['nodes_1M']:>7} "
              f"{r['path_1M']:>5} {r['aut_class']:>4}  "
              f"{'ok' if r['baseline_solved_at_50k'] else 'UNSOLVED':>8}{dup}")

    # ---- coverage plot ------------------------------------------------------
    order = sorted(rows, key=lambda r: r["difficulty_rank"])
    x = [r["difficulty_rank"] for r in order]
    rank = {r["pres_id"]: r["difficulty_rank"] for r in rows}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, key, lab in ((axes[0], "nodes_explored", "nodes_explored"),
                         (axes[1], "path_length", "path_length")):
        ax.scatter(x, [r[key] for r in order], s=6, c="#d0d0d0", label="all 640")
        for size, colour in zip(SIZES, ("#c0392b", "#e67e22", "#2980b9", "#27ae60")):
            sub = built[size]
            k = "nodes_1M" if key == "nodes_explored" else "path_1M"
            ax.scatter([rank[r["pres_id"]] for r in sub], [r[k] for r in sub],
                       s=90 - SIZES.index(size) * 18, alpha=.85, c=colour,
                       edgecolors="white", linewidths=.5, label=f"subset {size}")
        ax.set_yscale("log")
        ax.set_xlabel("presentations, sorted by baseline difficulty")
        ax.set_ylabel(lab)
        ax.set_title(f"benchmark subset coverage — {lab}")
        ax.grid(alpha=.25, which="both")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    png = os.path.join(OUT_DIR, "subset_coverage.png")
    fig.savefig(png, dpi=140)
    print(f"\n-> {os.path.relpath(OUT_DIR, REPO)}/  "
          f"({len(SIZES)} json + {len(SIZES)} csv + subset_coverage.png)")


if __name__ == "__main__":
    main()
