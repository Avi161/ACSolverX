"""Freeze the stable-AC benchmark subsets: 10 / 20 / 40 / 60 presentations.

Reads ``results/benchmark/difficulty_bins.csv`` (see ``difficulty_bins.py``) and
picks ``k = size // 10`` presentations from each of the 10 log-width difficulty
bins.

**Subsets are minimally automorphic (policy change, 2026-07-15).** Two
Aut(F2)-equivalent presentations are one problem in two coordinate systems --
the same lesson the 261 unsolved reps taught (they collapsed to ~125 classes).
Selection is therefore constrained, in priority order:

1. no two picks in the subset share an ``aut_class`` wherever the bins allow it
   (subset_10 achieves 10/10 distinct classes, subset_20 19/20);
2. where duplicates are forced -- bins 8+9 hold 12 presentations in only 3
   classes (106 x8, 97 x2, 108 x2), bin 7 holds 14 in 4 -- they are spread as
   evenly as possible across the available classes, minimising the number of
   Aut-equivalent pairs;
3. subject to 1-2, the old rule: **within a bin, members are ordered by
   ``path_length``, not by nodes.** The bin already pins ``nodes_explored`` to a
   x3.37 window -- that is the bin width -- so there is almost nothing left to
   spread on there. ``path_length`` inside one bin runs up to x11. Picks sit as
   close as possible to k evenly spaced positions over the bin's path-sorted
   order, endpoints included, so the path-cheapest and path-deepest member at
   that node cost stay on the ladder.

Bins are processed scarcest-first (fewest classes first), so the bins with no
room to dodge claim their classes before the rich bins, which can always pick
elsewhere. ``build`` fails loudly if the result misses the true optimum number
of distinct classes (computed by bipartite matching).

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
import itertools
import json
import math
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


# exact enumeration up to this many candidate sets per bin; covers every bin
# where forced duplicates can occur (bins 4-9 at every k). Bins 0-3 have >= 20
# classes each, so the greedy path always finds a zero-cost pick there.
_BRUTE_LIMIT = 1_000_000


def _pick(members, k, used):
    """k members of one bin, adding as few Aut(F2)-equivalent pairs as possible.

    ``used`` counts the aut classes already picked into this subset by other
    bins. The cost of a member is the number of new equivalent pairs it creates:
    the number of picks of its class already in the subset, this bin included.
    Zero-cost picks (a class nobody has yet) always win; forced duplicates are
    waterfilled across classes, never concentrated in one.

    Subject to that, picks sit as close as possible to k evenly spaced positions
    over the bin's path-sorted order, endpoints included (median if k=1) -- the
    old spread rule, now a tie-break. Interior ``(i+1)/(k+1)`` positions were
    tried before endpoints and are wrong here: in a 6-member bin the 33rd and
    66th percentiles are adjacent indices, and k=2 returned two near clones
    (625/622: nodes 78,770 vs 78,774). Spanning the full range keeps the
    path-cheapest and path-deepest member at that node cost on the ladder.

    Bins with ``C(m, k) <= _BRUTE_LIMIT`` are solved exactly by enumeration;
    larger bins greedily, one target at a time with endpoints claimed first, so
    a forced duplicate lands on an interior target, never on an endpoint.
    """
    ordered = sorted(members, key=lambda r: (r["path_length"], r["nodes_explored"],
                                             r["pres_id"]))
    m = len(ordered)
    if m <= k:                      # bins 8/9 at k=6 -- take everything
        for r in ordered:
            used[r["aut_class"]] += 1
        return ordered
    targets = [(m - 1) // 2] if k == 1 else [round(i * (m - 1) / (k - 1))
                                             for i in range(k)]
    cls = [r["aut_class"] for r in ordered]

    if math.comb(m, k) <= _BRUTE_LIMIT:
        best = None
        for idxs in itertools.combinations(range(m), k):
            cnt = {}
            pairs = 0
            for j in idxs:
                c = cls[j]
                n = cnt.get(c, 0)
                pairs += used[c] + n
                cnt[c] = n + 1
            if best is not None and pairs > best[0]:
                continue
            dev = sum(abs(j - t) for j, t in zip(idxs, targets))
            key = (pairs, dev, idxs)
            if best is None or key < best:
                best = key
        chosen = list(best[2])
    else:
        order = [0, k - 1] + list(range(1, k - 1)) if k > 1 else [0]
        cnt = Counter()
        free = set(range(m))
        by_target = {}
        for t in order:
            j = min(free, key=lambda i: (used[cls[i]] + cnt[cls[i]],
                                         abs(i - targets[t]), i))
            by_target[t] = j
            free.discard(j)
            cnt[cls[j]] += 1
        chosen = sorted(by_target.values())

    picked = [ordered[j] for j in chosen]
    for r in picked:
        used[r["aut_class"]] += 1
    return picked


def _distinct_bound(by_bin, k):
    """Max distinct aut classes any pick can achieve: bipartite b-matching
    between bins (capacity = their quota) and classes (capacity 1)."""
    bin_classes = {b: sorted({r["aut_class"] for r in mem})
                   for b, mem in by_bin.items()}
    owner = {}                                     # class -> bin holding it
    def _augment(b, taken):
        for c in bin_classes[b]:
            if c in taken:
                continue
            taken.add(c)
            if c not in owner or _augment(owner[c], taken):
                owner[c] = b
                return True
        return False
    total = 0
    for b in sorted(by_bin):
        for _ in range(min(k, len(by_bin[b]))):
            if _augment(b, set()):
                total += 1
    return total


def build(rows, size):
    k = size // N_BINS
    by_bin = {b: [r for r in rows if r["bin"] == b] for b in range(N_BINS)}
    # scarcest bins first: they have the fewest classes to dodge into, so they
    # claim theirs before the rich bins, which can always pick elsewhere
    scarcity = sorted(range(N_BINS),
                      key=lambda b: (len({r["aut_class"] for r in by_bin[b]}), -b))
    used = Counter()
    picks = {}
    for b in scarcity:
        picks[b] = _pick(by_bin[b], k, used)

    distinct = len(used)
    bound = _distinct_bound(by_bin, k)
    if distinct != bound:
        raise SystemExit(f"subset_{size}: reached {distinct} distinct Aut classes "
                         f"but {bound} is achievable -- selection regressed")

    out = []
    for b in range(N_BINS):
        for r in picks[b]:
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
            "within_bin_selection": ("minimise Aut(F2)-equivalent pairs across the whole "
                                     "subset first (no two picks share an aut_class wherever "
                                     "the bins allow; forced duplicates -- bins 7-9 -- are "
                                     "spread evenly across classes); subject to that, sort by "
                                     "(path_length, nodes_explored, pres_id) and take k evenly "
                                     "spaced positions over the full range, endpoints included "
                                     "(median if k=1). Nodes are already fixed to a x3.37 "
                                     "window by the bin, so path is what is left to spread on."),
            "nested": False,
            "aut_class_note": ("aut_class is the exact Aut(F2)/change-of-variables orbit "
                               "(the 640 are 113 classes). Since 2026-07-15 the subsets are "
                               "MINIMALLY AUTOMORPHIC: two Aut-equivalent presentations are "
                               "one problem in two coordinate systems (the 261 unsolved reps "
                               "collapsed the same way), so picks avoid sharing a class "
                               "wherever the bins allow. aut_distinct_optimum is the proven "
                               "ceiling (bipartite matching); the residual duplicates are "
                               "forced by bins 8+9 (12 presentations, 3 classes: 106 x8, "
                               "97 x2, 108 x2) and bin 7 (14 in 4). Search cost is still not "
                               "an orbit invariant (623 vs 636: 59,710 vs 213,882 nodes), so "
                               "the forced duplicates remain genuinely different search "
                               "instances -- but they are no longer over-sampled."),
            "aut_classes_in_subset": len({r["aut_class"] for r in subset}),
            "aut_distinct_optimum": _distinct_bound(
                {b: [r for r in rows if r["bin"] == b] for b in range(N_BINS)}, k),
            "aut_pairs_in_subset": sum(n * (n - 1) // 2 for n in
                                       Counter(r["aut_class"] for r in subset).values()),
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
              f"= optimum, {doc['aut_pairs_in_subset']:>2} equivalent pairs "
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

    # ---- coverage plot: one row per subset, so no subset ever hides another --
    order = sorted(rows, key=lambda r: r["difficulty_rank"])
    x = [r["difficulty_rank"] for r in order]
    rank = {r["pres_id"]: r["difficulty_rank"] for r in rows}
    fig, axes = plt.subplots(len(SIZES), 2, figsize=(14, 3.6 * len(SIZES)))
    for row_i, (size, colour) in enumerate(
            zip(SIZES, ("#c0392b", "#e67e22", "#2980b9", "#27ae60"))):
        sub = built[size]
        cls_count = Counter(r["aut_class"] for r in sub)
        uniq = [r for r in sub if cls_count[r["aut_class"]] == 1]
        dup = [r for r in sub if cls_count[r["aut_class"]] > 1]
        for col_i, (key, subkey) in enumerate((("nodes_explored", "nodes_1M"),
                                               ("path_length", "path_1M"))):
            ax = axes[row_i][col_i]
            ax.scatter(x, [r[key] for r in order], s=6, c="#d0d0d0", label="all 640")
            ax.scatter([rank[r["pres_id"]] for r in uniq], [r[subkey] for r in uniq],
                       s=55, c=colour, edgecolors="white", linewidths=.5,
                       label="unique Aut class")
            if dup:
                ax.scatter([rank[r["pres_id"]] for r in dup], [r[subkey] for r in dup],
                           s=55, c=colour, marker="D", edgecolors="black",
                           linewidths=1.1, label="shares an Aut class (forced)")
            ax.set_yscale("log")
            ax.set_ylabel(key)
            ax.set_title(f"subset {size} — {key}  "
                         f"({len(cls_count)}/{len(sub)} distinct Aut classes, "
                         f"{sum(n * (n - 1) // 2 for n in cls_count.values())} "
                         f"equivalent pairs)", fontsize=10)
            ax.grid(alpha=.25, which="both")
            if row_i == len(SIZES) - 1:
                ax.set_xlabel("presentations, sorted by baseline difficulty")
        axes[row_i][0].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    png = os.path.join(OUT_DIR, "subset_coverage.png")
    fig.savefig(png, dpi=140)
    print(f"\n-> {os.path.relpath(OUT_DIR, REPO)}/  "
          f"({len(SIZES)} json + {len(SIZES)} csv + subset_coverage.png)")


if __name__ == "__main__":
    main()
