"""Render the EXP-29 L/K/MK ablation in the style of the PR-8 benchmark figure.

    .venv/bin/python3 -m experiments.heuristic_search.figures.make_lkmk_comparison_fig
"""
import csv
import os
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, part)) for part in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hlab import LOGS  # noqa: E402

SOURCE = os.path.join(LOGS, "EXP29_lkmk_ablation.csv")
DEST = os.path.join(LOGS, "EXP29_lkmk_ablation.png")
BUDGET = 1_000
ARMS = ("baseline", "lkmk", "recommended")
STYLE = {
    "baseline": {"label": "Greedy baseline", "color": "#898781", "marker": "o", "ls": "-"},
    "lkmk": {"label": "L + 2.53K + 6.418MK", "color": "#2a78d6", "marker": "s", "ls": "--"},
    "recommended": {"label": "Full RECOMMENDED", "color": "#eb6834", "marker": "D", "ls": "-"},
}
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"


def _bool(value):
    return value.lower() == "true"


def load_rows():
    with open(SOURCE) as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["order"] = int(r["order"])
        r["pres_id"] = int(r["pres_id"])
        r["bin"] = int(r["bin"])
        r["solved"] = _bool(r["solved"])
        r["nodes_explored"] = int(r["nodes_explored"])
        r["path_length"] = int(r["path_length"]) if r["path_length"] else None
        r["in_all_three_solved"] = _bool(r["in_all_three_solved"])
    return rows


def _matched_stats(rows, arm, field):
    vals = [r[field] for r in rows
            if r["arm"] == arm and r["in_all_three_solved"]]
    return statistics.fmean(vals), statistics.median(vals)


def _fmt(value):
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.1f}"


def _style_axis(ax, log_x=False):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#c3c2b7")
        spine.set_linewidth(0.8)
    ax.grid(True, axis="x", which="both" if log_x else "major", color=GRID,
            linewidth=0.7, alpha=0.75)
    ax.grid(False, axis="y")


def _draw_summary(ax, rows, field, title, log_x):
    means, medians = [], []
    for arm in ARMS:
        mean, median = _matched_stats(rows, arm, field)
        means.append(mean)
        medians.append(median)

    y = np.arange(len(ARMS))
    h = 0.27
    for i, arm in enumerate(ARMS):
        st = STYLE[arm]
        ax.barh(y[i] - h / 2, means[i], height=h, color=st["color"], alpha=0.95)
        ax.barh(y[i] + h / 2, medians[i], height=h, facecolor=st["color"], alpha=0.36,
                hatch="//", edgecolor=INK, linewidth=0.0)
    ax.set_yticks(y, [STYLE[a]["label"] for a in ARMS])
    ax.invert_yaxis()
    values = means + medians
    if log_x:
        ax.set_xscale("log")
        ax.set_xlim(min(values) * 0.82, max(values) * 1.55)
    else:
        ax.set_xlim(0, max(values) * 1.22)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    ax.set_xlabel(field.replace("_", " "), color=SECONDARY)
    _style_axis(ax, log_x=log_x)

    xmin, xmax = ax.get_xlim()
    for i in range(len(ARMS)):
        for value, yy, kind in ((means[i], y[i] - h / 2, "mean"),
                                (medians[i], y[i] + h / 2, "median")):
            offset = value * 1.06 if log_x else value + 0.018 * (xmax - xmin)
            ax.text(offset, yy, f"{_fmt(value)}  {kind}", va="center", ha="left",
                    color=INK, fontsize=9)


def main():
    rows = load_rows()
    by_arm = {arm: sorted([r for r in rows if r["arm"] == arm], key=lambda r: r["order"])
              for arm in ARMS}
    names = [r["name"] for r in by_arm["baseline"]]
    if any([r["name"] for r in by_arm[a]] != names for a in ARMS):
        raise SystemExit("arm rows do not share one frozen presentation order")
    shared_n = sum(r["in_all_three_solved"] for r in by_arm["baseline"])
    solved_counts = {a: sum(r["solved"] for r in by_arm[a]) for a in ARMS}

    fig = plt.figure(figsize=(18, 11), facecolor=SURFACE)
    grid = fig.add_gridspec(2, 2, height_ratios=(2.2, 1.0), hspace=0.34, wspace=0.28)
    ax = fig.add_subplot(grid[0, :])
    ax_nodes = fig.add_subplot(grid[1, 0])
    ax_path = fig.add_subplot(grid[1, 1])

    x = np.arange(len(names))
    for b in range(10):
        lo, hi = 6 * b - 0.5, 6 * (b + 1) - 0.5
        if b % 2 == 0:
            ax.axvspan(lo, hi, color="#f0efec", zorder=0)
        ax.text((lo + hi) / 2, 1.33 * BUDGET, f"bin {b}", ha="center", va="bottom",
                color=MUTED, fontsize=9)

    for arm in ARMS:
        st = STYLE[arm]
        data = by_arm[arm]
        y = [r["nodes_explored"] if r["solved"] else BUDGET for r in data]
        ax.plot(x, y, color=st["color"], linestyle=st["ls"], linewidth=2.0, alpha=0.88,
                marker=st["marker"], markersize=5.5, markeredgecolor=SURFACE,
                markeredgewidth=1.1, zorder=2)
        missed = [i for i, r in enumerate(data) if not r["solved"]]
        if missed:
            ax.scatter(missed, [BUDGET] * len(missed), marker="x", s=52, linewidths=1.7,
                       color=st["color"], zorder=4)

    ax.axhline(BUDGET, color=MUTED, linewidth=0.9, linestyle=":", zorder=1)
    ax.text(len(names) - 0.5, BUDGET * 1.045, "unsolved at the 1,000-node ceiling",
            ha="right", va="bottom", color=SECONDARY, fontsize=9)
    ax.set_yscale("log")
    ax.set_xlim(-0.75, len(names) - 0.25)
    ax.set_ylim(1.8, 1_550)
    ax.set_xticks(x, [r["name"].removeprefix("ms") for r in by_arm["baseline"]],
                  rotation=90, fontsize=7)
    ax.set_ylabel("nodes explored (log)", color=SECONDARY)
    ax.set_xlabel("presentation (frozen 60-row benchmark, easy → hard)", color=SECONDARY)
    ax.set_title("L/K/MK ablation at a matched 1,000-node budget and cap 48", loc="left",
                 fontsize=17, color=INK, pad=35)
    ax.text(0.0, 1.015,
            "Unsolved rows are × at the ceiling; solve counts: "
            + " · ".join(f"{STYLE[a]['label']} {solved_counts[a]}/60" for a in ARMS),
            transform=ax.transAxes, color=SECONDARY, fontsize=10, va="bottom")
    ax.grid(True, axis="y", which="both", color=GRID, linewidth=0.7, alpha=0.8)
    ax.grid(False, axis="x")
    ax.set_facecolor(SURFACE)
    for spine in ax.spines.values():
        spine.set_color("#c3c2b7")
        spine.set_linewidth(0.8)
    ax.tick_params(colors=SECONDARY)
    ax.legend(handles=[Line2D([0], [0], color=STYLE[a]["color"], linestyle=STYLE[a]["ls"],
                                  marker=STYLE[a]["marker"], markersize=7,
                                  markeredgecolor=SURFACE, markeredgewidth=1.1,
                                  label=STYLE[a]["label"])
                       for a in ARMS],
              loc="upper left", bbox_to_anchor=(0, 1.18), ncol=3, frameon=False, fontsize=10)

    _draw_summary(ax_nodes, rows, "nodes_explored",
                  f"Mean and median nodes — all three solve (n={shared_n})", log_x=True)
    _draw_summary(ax_path, rows, "path_length",
                  f"Mean and median path length — same rows (n={shared_n})", log_x=False)

    fig.text(0.01, 0.012,
             "Matched-cost panels use the all-three-solved intersection. Own-solved statistics and "
             "all row values are in EXP29_lkmk_ablation.md/.csv.",
             ha="left", color=SECONDARY, fontsize=9)
    fig.savefig(DEST, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {DEST}")


if __name__ == "__main__":
    main()
