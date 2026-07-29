"""Figures + difficulty bins for solved_1hop_autclean @ 100k.

Uses the **same log-width bin edges** as ``benchmark/difficulty_bins.csv``
(ms640 length-greedy @1M), applied to this run's length-``baseline`` cost at
budget 100k. Unsolved baseline rows are censored at 100,000 nodes (land in
bin 8 of the frozen edges; bin 9 is unreachable at this budget).

    .venv/bin/python3 -m experiments.heuristic_search.figures.make_solved1hop_100k_figs
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
ROOT = _d

MERGED = os.path.join(
    ROOT, "results", "heuristic_search", "hsearch_solved1hop_100k",
    "merged_solved_1hop_autclean_b100000_mrl48.jsonl")
FREEZE = os.path.join(
    ROOT, "results", "heuristic_search", "splits", "solved_1hop_autclean.json")
BENCH_BINS = os.path.join(ROOT, "benchmark", "difficulty_bins.csv")
OUT_DIR = os.path.join(
    ROOT, "results", "heuristic_search", "hsearch_solved1hop_100k")

ARMS = ["baseline", "s12", "s28", "s20_mk2", "s24_k1_mk2"]
COLORS = {
    "baseline": "#4a4a4a",
    "s12": "#1f77b4",
    "s28": "#2ca02c",
    "s20_mk2": "#d62728",
    "s24_k1_mk2": "#ff7f0e",
}
BUDGET = 100_000


def _load_bin_edges():
    """Frozen (lo, hi) per bin from ms640 difficulty_bins.csv."""
    edges = {}
    with open(BENCH_BINS) as f:
        for r in csv.DictReader(f):
            b = int(r["bin"])
            edges[b] = (int(r["bin_lo_nodes"]), int(r["bin_hi_nodes"]))
    return edges


def _bin_of(nodes, edges):
    """Half-open [lo, hi) for bins 0..8; bin 9 is [lo, hi]."""
    bs = sorted(edges)
    for b in bs:
        lo, hi = edges[b]
        if b == bs[-1]:
            if nodes >= lo:
                return b
        elif lo <= nodes < hi:
            return b
    return bs[0]


def load():
    rows = [json.loads(l) for l in open(MERGED) if l.strip()]
    by = defaultdict(dict)
    for r in rows:
        by[r["name"]][r["arm"]] = r
    meta = {r["name"]: r for r in json.load(open(FREEZE))["rows"]}
    return by, meta


def assign_bins(by, meta, edges):
    out = []
    for name in sorted(by, key=lambda n: (
            meta[n]["kind"] != "seed", meta[n]["mu"], n)):
        base = by[name]["baseline"]
        # Difficulty ruler = length-baseline cost (same role as greedy nodes_1M).
        if base.get("solved") and base.get("solved_at") is not None:
            nodes = int(base["solved_at"])
            censored = False
        else:
            nodes = BUDGET
            censored = True
        b = _bin_of(nodes, edges)
        lo, hi = edges[b]
        row = {
            "name": name,
            "kind": meta[name]["kind"],
            "mu": meta[name]["mu"],
            "short_relator": bool(meta[name].get("short_relator")),
            "bin": b,
            "bin_lo_nodes": lo,
            "bin_hi_nodes": hi,
            "baseline_nodes": nodes,
            "baseline_solved": bool(base.get("solved")),
            "baseline_censored_at_100k": censored,
            "baseline_path": (base.get("path_length")
                              if base.get("solved") else None),
        }
        for a in ARMS:
            r = by[name][a]
            row[f"{a}_solved"] = bool(r.get("solved"))
            row[f"{a}_nodes"] = (int(r["solved_at"]) if r.get("solved")
                                 and r.get("solved_at") is not None
                                 else BUDGET)
            row[f"{a}_path"] = (r.get("path_length") if r.get("solved")
                                else None)
        out.append(row)
    # sort like the ladder: by bin, then baseline nodes, then name
    out.sort(key=lambda r: (r["bin"], r["baseline_nodes"], r["name"]))
    for i, r in enumerate(out):
        r["difficulty_rank"] = i
    return out


def write_csv(assigned, path):
    fields = list(assigned[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in assigned:
            w.writerow(r)


def fig_mean_median(assigned, path):
    """Bar chart: mean/median on the all-five-solved intersection (unbiased)."""
    all5 = [r for r in assigned if all(r[f"{a}_solved"] for a in ARMS)]
    n = len(all5)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    x = np.arange(len(ARMS))
    width = 0.36

    means_n, meds_n, means_p, meds_p = [], [], [], []
    for a in ARMS:
        nodes = [r[f"{a}_nodes"] for r in all5]
        paths = [r[f"{a}_path"] for r in all5]
        means_n.append(float(np.mean(nodes)))
        meds_n.append(float(np.median(nodes)))
        means_p.append(float(np.mean(paths)))
        meds_p.append(float(np.median(paths)))

    ax = axes[0]
    ax.bar(x - width / 2, means_n, width, label="mean", color="#5b7c99")
    ax.bar(x + width / 2, meds_n, width, label="median", color="#c4a35a")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(ARMS, fontsize=8)
    ax.set_ylabel("nodes to solve")
    ax.set_title("Nodes explored — mean / median")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1]
    ax.bar(x - width / 2, means_p, width, label="mean", color="#5b7c99")
    ax.bar(x + width / 2, meds_p, width, label="median", color="#c4a35a")
    ax.set_xticks(x)
    ax.set_xticklabels(ARMS, fontsize=8)
    ax.set_ylabel("path length")
    ax.set_title("Path length — mean / median")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.3)

    fig.suptitle(
        f"solved_1hop_autclean @ 100k  (all 5 arms solved, n={n}/{len(assigned)})",
        fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def fig_nodes_by_rank(assigned, path):
    """Per-presentation nodes, x = difficulty rank (baseline bin order)."""
    fig, ax = plt.subplots(figsize=(12, 4.8))
    xs = [r["difficulty_rank"] for r in assigned]
    for a in ARMS:
        ys = [r[f"{a}_nodes"] for r in assigned]
        ok = [r[f"{a}_solved"] for r in assigned]
        ax.plot(xs, ys, color=COLORS[a], alpha=0.35, linewidth=0.8, zorder=1)
        ax.scatter([x for x, s in zip(xs, ok) if s],
                   [y for y, s in zip(ys, ok) if s],
                   s=10, color=COLORS[a], label=a, zorder=2)
        ax.scatter([x for x, s in zip(xs, ok) if not s],
                   [y for y, s in zip(ys, ok) if not s],
                   s=18, color=COLORS[a],
                   marker="x", linewidths=0.9, zorder=3)
    # bin boundaries
    edges_x = []
    prev = None
    for r in assigned:
        if r["bin"] != prev:
            edges_x.append(r["difficulty_rank"])
            prev = r["bin"]
    for x in edges_x[1:]:
        ax.axvline(x - 0.5, color="#bbbbbb", linewidth=0.6)
    # bin labels at top
    from itertools import groupby
    for b, grp in groupby(assigned, key=lambda r: r["bin"]):
        g = list(grp)
        mid = 0.5 * (g[0]["difficulty_rank"] + g[-1]["difficulty_rank"])
        ax.text(mid, BUDGET * 1.35, f"b{b}", ha="center", va="bottom",
                fontsize=7, color="#666666")

    ax.set_yscale("log")
    ax.set_ylim(2, BUDGET * 2.2)
    ax.axhline(BUDGET, color="#999999", linestyle="--", linewidth=0.7)
    ax.set_xlabel("presentations sorted by length-baseline difficulty "
                  "(benchmark log-bins)")
    ax.set_ylabel("nodes explored (✗ = unsolved @100k)")
    ax.set_title("Nodes explored by difficulty rank")
    ax.legend(ncol=5, frameon=False, fontsize=8, loc="upper left")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def fig_path_by_rank(assigned, path):
    fig, ax = plt.subplots(figsize=(12, 4.8))
    xs = [r["difficulty_rank"] for r in assigned]
    for a in ARMS:
        ys = [r[f"{a}_path"] if r[f"{a}_solved"] else None for r in assigned]
        ok_x = [x for x, y in zip(xs, ys) if y is not None]
        ok_y = [y for y in ys if y is not None]
        ax.scatter(ok_x, ok_y, s=10, color=COLORS[a], label=a, alpha=0.85)
    ax.set_xlabel("presentations sorted by length-baseline difficulty")
    ax.set_ylabel("path length (solved only)")
    ax.set_title("Path length by difficulty rank")
    ax.legend(ncol=5, frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def fig_bin_distribution(assigned, path):
    """How many presentations land in each benchmark difficulty bin."""
    edges = _load_bin_edges()
    counts = Counter(r["bin"] for r in assigned)
    cens = Counter(r["bin"] for r in assigned if r["baseline_censored_at_100k"])
    bins = list(range(10))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))

    ax = axes[0]
    vals = [counts.get(b, 0) for b in bins]
    cens_vals = [cens.get(b, 0) for b in bins]
    solved_vals = [v - c for v, c in zip(vals, cens_vals)]
    ax.bar(bins, solved_vals, color="#5b7c99", label="baseline solved")
    ax.bar(bins, cens_vals, bottom=solved_vals, color="#c45c5c",
           label="baseline unsolved (censored @100k)")
    ax.set_xticks(bins)
    ax.set_xticklabels(
        [f"{b}\n[{edges[b][0]},{edges[b][1]})" if b < 9
         else f"{b}\n[{edges[b][0]},{edges[b][1]}]"
         for b in bins],
        fontsize=7)
    ax.set_xlabel("difficulty bin (same edges as benchmark/difficulty_bins.csv)")
    ax.set_ylabel("# presentations")
    ax.set_title("Difficulty distribution (length-baseline cost)")
    ax.legend(frameon=False, fontsize=8)
    for b, v in zip(bins, vals):
        if v:
            ax.text(b, v + 1, str(v), ha="center", va="bottom", fontsize=8)

    ax = axes[1]
    # solve rate per bin per arm
    width = 0.15
    x = np.arange(10)
    for i, a in enumerate(ARMS):
        rates = []
        for b in bins:
            sub = [r for r in assigned if r["bin"] == b]
            if not sub:
                rates.append(float("nan"))
            else:
                rates.append(sum(1 for r in sub if r[f"{a}_solved"]) / len(sub))
        ax.bar(x + (i - 2) * width, rates, width, label=a, color=COLORS[a])
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels([str(b) for b in bins])
    ax.set_xlabel("difficulty bin")
    ax.set_ylabel("solve rate @100k")
    ax.set_title("Solve rate by difficulty bin")
    ax.legend(ncol=3, frameon=False, fontsize=7)
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def write_bin_table(assigned, path_md_fragment):
    edges = _load_bin_edges()
    lines = [
        "## Difficulty bins (benchmark log-edges, length-baseline @100k)",
        "",
        "Same `[lo, hi)` node edges as `benchmark/difficulty_bins.csv` "
        "(ms640 greedy @1M). Ruler here = this run's **length baseline** "
        "`solved_at` (unsolved censored at 100k → bin 8).",
        "",
        "| bin | nodes range | n | baseline | s12 | s28 | s20_mk2 | s24_k1_mk2 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for b in range(10):
        sub = [r for r in assigned if r["bin"] == b]
        lo, hi = edges[b]
        rng = f"[{lo}, {hi})" if b < 9 else f"[{lo}, {hi}]"
        if not sub:
            lines.append(f"| {b} | {rng} | 0 | — | — | — | — | — |")
            continue
        cells = [str(len(sub))]
        for a in ARMS:
            s = sum(1 for r in sub if r[f"{a}_solved"])
            cells.append(f"{s}/{len(sub)}")
        lines.append(f"| {b} | {rng} | " + " | ".join(cells) + " |")
    n_c = sum(1 for r in assigned if r["baseline_censored_at_100k"])
    lines += [
        "",
        f"Baseline-censored (unsolved @100k): **{n_c}** presentations "
        f"(placed in bin by nodes={BUDGET}).",
        "",
        "### Figures",
        "",
        "- `solved1hop_100k_mean_median.png`",
        "- `solved1hop_100k_nodes_explored.png`",
        "- `solved1hop_100k_path_length.png`",
        "- `solved1hop_100k_difficulty_bins.png`",
        "",
        "Per-row table: `difficulty_bins_solved1hop_100k.csv`.",
        "",
    ]
    with open(path_md_fragment, "w") as f:
        f.write("\n".join(lines))
    return "\n".join(lines)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    edges = _load_bin_edges()
    by, meta = load()
    assigned = assign_bins(by, meta, edges)
    assert len(assigned) == 432

    csv_path = os.path.join(OUT_DIR, "difficulty_bins_solved1hop_100k.csv")
    write_csv(assigned, csv_path)
    fig_mean_median(assigned, os.path.join(
        OUT_DIR, "solved1hop_100k_mean_median.png"))
    fig_nodes_by_rank(assigned, os.path.join(
        OUT_DIR, "solved1hop_100k_nodes_explored.png"))
    fig_path_by_rank(assigned, os.path.join(
        OUT_DIR, "solved1hop_100k_path_length.png"))
    fig_bin_distribution(assigned, os.path.join(
        OUT_DIR, "solved1hop_100k_difficulty_bins.png"))
    frag = write_bin_table(assigned, os.path.join(
        OUT_DIR, "_bins_fragment.md"))

    # splice into RESULTS.md: replace/append bins section
    results = os.path.join(OUT_DIR, "RESULTS.md")
    text = open(results).read()
    marker = "## Difficulty bins"
    if marker in text:
        text = text.split(marker)[0].rstrip() + "\n\n" + frag
    else:
        # insert before Residual section if present
        if "## Residual" in text:
            pre, post = text.split("## Residual", 1)
            text = pre.rstrip() + "\n\n" + frag + "## Residual" + post
        else:
            text = text.rstrip() + "\n\n" + frag
    open(results, "w").write(text)
    os.remove(os.path.join(OUT_DIR, "_bins_fragment.md"))

    counts = Counter(r["bin"] for r in assigned)
    print("bin counts:", dict(sorted(counts.items())))
    print("wrote figures +", csv_path)


if __name__ == "__main__":
    main()
