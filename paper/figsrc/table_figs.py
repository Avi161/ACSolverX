"""Figures that draw the tables of Section 2 from the per-row records in results/benchmark_rows/.

    scores_budget.png  presentations solved against the budget, all seven methods (tab:cov_search_solved)
    maxrel_summary.png mean and largest total relator length on the path, all seven methods (tab:maxrel)

    python paper/figsrc/table_figs.py
"""
import json
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/figures"
METHODS = ["LENGTH", "S20_MK2", "hybrid", "CoV gate", "dual, single CoV", "dual, auto CoV", "triple"]
COLORS = dict(zip(METHODS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]))
INK, MUTED, GRID = "#1f1f1e", "#5f5e58", "#e4e3dc"
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 11})


def load():
    ms = [json.loads(x) for x in (ROOT / "results/benchmark_rows/ms640.jsonl").read_text().splitlines()]
    la = [json.loads(x) for x in (ROOT / "results/benchmark_rows/ladder100.jsonl").read_text().splitlines()]
    return {"MS640": ms, "bench60": [r for r in ms if r.get("bench60")], "ladder100": la}


def style(ax):
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def scores_budget(B):
    # dual, auto CoV is left out: it never solves more than dual, single CoV (Table 3)
    SHOWN = [m for m in METHODS if m != "dual, auto CoV"]
    budgets = [10 ** (3 + j / 4) for j in range(17)]      # four budgets per decade, each counted exactly from the rows
    decades = [10 ** k for k in range(3, 8)]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6))
    for ax, (name, rows) in zip(axes, B.items()):
        for m in SHOWN:
            if m == "hybrid":
                # the hybrid of Section 1 (the paper's numbers): every row within 10^3 units except ladder100's
                # ac19_70845, which takes 2,267; the per-row records hold a later hybrid version
                units = [2267 if r["id"] == "ac19_70845" else 1000 for r in rows]
                ys = [100 * sum(1 for u in units if u <= b) / len(rows) for b in budgets]
            else:
                ys = [100 * sum(1 for r in rows if r["methods"][m]["solved"] and r["methods"][m]["units"] <= b)
                      / len(rows) for b in budgets]
            ax.plot(budgets, ys, color=COLORS[m], lw=1.8, marker="o", markersize=3.6,
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3 if m == "hybrid" else 2)
        ax.set_xscale("log")
        ax.set_xticks(decades)
        ax.set_title(f"{name} (of {len(rows)})")
        ax.set_xlabel("budget (units)")
        ax.set_ylim(0, 103)
        style(ax)
    axes[0].set_ylabel("% of presentations solved")
    fig.legend([Line2D([], [], color=COLORS[m], lw=1.8, marker="o", markersize=4.5) for m in SHOWN], SHOWN,
               loc="upper center", ncol=6, frameon=False, fontsize=8.5, handlelength=1.6, columnspacing=1.2)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT / "scores_budget.png", dpi=200)


def maxrel_summary(B):
    T = [json.loads(x) for x in (ROOT / "results/benchmark_rows/max_total.jsonl").read_text().splitlines()]
    sets = {"MS640": [x for x in T if x["benchmark"] == "ms640"], "bench60": [x for x in T if x["bench60"]],
            "ladder100": [x for x in T if x["benchmark"] == "ladder100"]}
    keys = ["start_total", "LENGTH", "S20_MK2", "hybrid, search states", "hybrid, AC path", "CoV gate",
            "dual, single CoV", "dual, auto CoV", "triple"]
    labels = ["starting presentation"] + keys[1:]
    colors = [MUTED, COLORS["LENGTH"], COLORS["S20_MK2"], COLORS["hybrid"], COLORS["hybrid"]] + \
        [COLORS[m] for m in METHODS[3:]]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.9), sharey=True)
    for ax, (name, rows) in zip(axes, sets.items()):
        start = mean(x["start_total"] for x in rows)
        ax.axvline(start, color=MUTED, lw=0.9, ls="--", zorder=0)
        for y, (k, c) in enumerate(zip(keys, colors)):
            v = [x[k] for x in rows if k in x]
            mu, mx = mean(v), max(v)
            ax.plot([mu, mx], [y, y], color=c, lw=1.2, zorder=1)
            ax.scatter([mu], [y], s=34, color=c, zorder=3, edgecolor="white", linewidth=0.8)
            ax.scatter([mx], [y], s=34, facecolor="white", edgecolor=c, linewidth=1.4, zorder=3)
            ax.annotate(f"{mx:,}", (mx, y), xytext=(6, -3), textcoords="offset points", fontsize=7.5, color=INK)
        ax.set_xscale("log")
        ax.set_xlim(6, 4000)
        ax.set_title(name)
        ax.set_xlabel("largest total relator length")
        style(ax)
    axes[0].set_yticks(range(len(labels)))
    axes[0].set_yticklabels(labels, fontsize=8.5)
    axes[0].invert_yaxis()
    fig.legend([Line2D([], [], ls="", marker="o", color=INK, markersize=6),
                Line2D([], [], ls="", marker="o", markerfacecolor="white", markeredgecolor=INK, markersize=6),
                Line2D([], [], ls="--", color=MUTED, lw=0.9)],
               ["mean", "largest", "mean at the start"], loc="upper center", ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "maxrel_summary.png", dpi=200)


def main():
    B = load()
    scores_budget(B)
    maxrel_summary(B)


if __name__ == "__main__":
    main()
