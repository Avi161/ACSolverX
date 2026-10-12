"""Plot a ``run_cov_all`` jsonl: nodes from a CoV start against nodes from the control.

One point of mass per (presentation, CoV start): x is the control's
``nodes_explored``, y is the start's. Above y = x the start needs more nodes than
the untransformed presentation, below it fewer. A search that did not solve
within the file's budget sits in the "unsolved" row / column past the axis end.

Every presentation carries the same total weight (a start weighs 1 / number of
starts of its presentation), so the picture is the outcome of drawing one
presentation, then one of its CoV starts, uniformly at random; unweighted, rows
531/532 alone would be a fifth of it.

Lower panel: the same starts grouped by the control's cost, split into cheaper /
equal / dearer / unsolved, each bar the mean over that group's presentations.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.cov.run.plot_cov_all_control_vs_cov FILE.jsonl
writes FILE_control_vs_cov.png and FILE_control_vs_cov.md next to it.
"""

import argparse
import json
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm

SURFACE, INK, INK2, MUTED, GRID, AXIS = (
    "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7")
BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
OUTCOMES = [("cheaper", "fewer nodes than the control", "#2a78d6"),
            ("equal", "same nodes", "#c3c2b7"),
            ("dearer", "more nodes than the control", "#eb6834"),
            ("fail", "start not solved within the budget", "#9c1f24")]
PER_DECADE = 5


def load(path):
    by = defaultdict(list)
    with open(path) as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                by[r["pres_id"]].append(r)
    return by


def outcome(ctrl, row):
    if not row["solved"]:
        return "fail"
    if not ctrl["solved"] or row["nodes_explored"] < ctrl["nodes_explored"]:
        return "cheaper"
    return "equal" if row["nodes_explored"] == ctrl["nodes_explored"] else "dearer"


def collect(by):
    budget = next(iter(by.values()))[0]["node_budget"]
    decades = round(math.log10(budget))
    xs, ys, ws = [], [], []
    groups = defaultdict(list)   # control-cost group -> per-presentation fractions
    overall = []
    for rows in by.values():
        ctrl = next(r for r in rows if r["is_control"])
        cov = [r for r in rows if not r["is_control"]]
        if not cov:
            continue
        frac = dict.fromkeys((k for k, _, _ in OUTCOMES), 0.0)
        for r in cov:
            frac[outcome(ctrl, r)] += 1 / len(cov)
            xs.append(ctrl["nodes_explored"] if ctrl["solved"] else None)
            ys.append(r["nodes_explored"] if r["solved"] else None)
            ws.append(1 / len(cov))
        g = min(int(math.log10(ctrl["nodes_explored"])), decades - 1) if ctrl["solved"] else decades
        groups[g].append(frac)
        overall.append(frac)
    return budget, decades, xs, ys, np.array(ws) / len(overall), groups, overall


def mean_frac(fracs):
    return {k: sum(f[k] for f in fracs) / len(fracs) for k, _, _ in OUTCOMES}


def fmt(n):
    return f"{n:,}"


def plot(path, out_png):
    by = load(path)
    budget, decades, xs, ys, ws, groups, overall = collect(by)
    nb = decades * PER_DECADE
    # bin index along one axis; index nb + 1 is the unsolved rail, nb is a gap
    def idx(v):
        return nb + 1 if v is None else min(int(math.log10(v) * PER_DECADE + 1e-9), nb - 1)
    H = np.zeros((nb + 2, nb + 2))
    for x, y, w in zip(xs, ys, ws):
        H[idx(y), idx(x)] += w

    plt.rcParams.update({"font.family": "sans-serif", "font.size": 10,
                         "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                         "xtick.color": MUTED, "ytick.color": MUTED,
                         "xtick.labelcolor": INK2, "ytick.labelcolor": INK2})
    fig = plt.figure(figsize=(7.8, 10.8), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[3.1, 1], width_ratios=[1, 0.03],
                          hspace=0.36, wspace=0.04,
                          left=0.17, right=0.89, top=0.875, bottom=0.065)
    ax, cax, bx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0])
    for a in (ax, bx):
        a.set_facecolor(SURFACE)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)

    cmap = LinearSegmentedColormap.from_list("blues", BLUES)
    cmap.set_bad(SURFACE)
    Hm = np.ma.masked_where(H <= 0, H)
    im = ax.pcolormesh(np.arange(nb + 3), np.arange(nb + 3), Hm, cmap=cmap,
                       norm=LogNorm(vmin=max(H[H > 0].min(), 1e-5), vmax=H.max()),
                       edgecolors=SURFACE, linewidth=0.4)
    ax.plot([0, nb], [0, nb], color=INK, lw=1.4, zorder=3)
    ax.text(nb * 0.55, nb * 0.55 + 0.5, "y = x", color=INK, rotation=45,
            rotation_mode="anchor", ha="center", va="bottom", fontsize=9.5)
    for v in (nb, nb + 1):
        ax.axhline(v, color=AXIS, lw=0.8, zorder=2)
        ax.axvline(v, color=AXIS, lw=0.8, zorder=2)
    ticks = [d * PER_DECADE for d in range(decades + 1)] + [nb + 1.5]
    labels = [fmt(10 ** d) for d in range(decades + 1)]
    ax.set_xticks(ticks, labels + ["\nunsolved"])
    ax.set_yticks(ticks, labels + ["unsolved"])
    ax.set_xlim(0, nb + 2)
    ax.set_ylim(0, nb + 2)
    ax.set_aspect("equal")
    ax.tick_params(length=3)
    ax.set_xlabel("nodes explored from the original presentation (control)")
    ax.set_ylabel("nodes explored from a CoV start")
    ax.text(0.9, nb - 0.5, "above the line: the CoV start needs more nodes",
            color=INK2, rotation=90, ha="center", va="top", fontsize=9.5)
    ax.text(nb - 0.5, 0.6, "below the line:\nthe CoV start needs fewer nodes",
            color=INK2, ha="right", va="bottom", fontsize=9.5)
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, labelsize=8.5)
    cb.set_label("share of random (presentation, start) draws in the cell",
                 color=INK2, fontsize=9)

    o = mean_frac(overall)
    n_starts = len(xs)
    fig.text(0.17, 0.975, "A random CoV start against the original presentation",
             color=INK, fontsize=14, fontweight="bold", ha="left", va="top")
    fig.text(0.17, 0.95,
             f"MS640, baseline greedy, budget {fmt(budget)} nodes; {len(overall)} presentations, "
             f"{fmt(n_starts)} suballpxyb8 starts,\neach presentation weighted equally. "
             f"A random start needs fewer nodes {o['cheaper']:.0%} of the time,\n"
             f"the same {o['equal']:.0%}, more {o['dearer']:.0%}, and is unsolved "
             f"{o['fail']:.0%}. CoV solves certify stable AC-triviality.",
             color=INK2, fontsize=9.5, ha="left", va="top", linespacing=1.45)

    order = list(range(decades)) + [decades]
    names = [f"{fmt(10 ** d)} to {fmt(10 ** (d + 1) - 1)}" for d in range(decades)] + ["unsolved"]
    left = np.zeros(len(order))
    table = []
    for key, label, color in OUTCOMES:
        vals = np.array([mean_frac(groups[g])[key] if groups.get(g) else 0 for g in order])
        bx.barh(range(len(order)), vals, left=left, color=color, height=0.72,
                edgecolor=SURFACE, linewidth=1.5, label=label)
        for i, (v, l) in enumerate(zip(vals, left)):
            if v >= 0.07:
                bx.text(l + v / 2, i, f"{v:.0%}", ha="center", va="center", fontsize=8.5,
                        color="#ffffff" if key in ("cheaper", "fail") else INK)
        left += vals
        table.append((label, vals))
    bx.set_yticks(range(len(order)), names)
    for i, g in enumerate(order):
        bx.text(1.012, i, f"n = {len(groups.get(g, []))}", ha="left", va="center",
                fontsize=8.5, color=INK2)
    bx.invert_yaxis()
    bx.set_xlim(0, 1)
    bx.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    bx.tick_params(length=0)
    bx.spines["left"].set_visible(False)
    bx.set_xlabel("share of a presentation's CoV starts, mean over the group's presentations")
    bx.set_title("Does a random start beat the control? Grouped by the control's nodes "
                 "(n = presentations)", color=INK, fontsize=10.5, loc="left", x=-0.2, pad=40)
    bx.legend(loc="lower left", bbox_to_anchor=(-0.21, 1.0), ncol=2, frameon=False,
              fontsize=8.5, handlelength=1.1, columnspacing=1.6, labelcolor=INK2,
              borderaxespad=0.2)
    fig.savefig(out_png, dpi=170, facecolor=SURFACE)
    plt.close(fig)

    md = [f"# Control vs a random CoV start: `{os.path.basename(path)}`", "",
          f"Budget {fmt(budget)}; {len(overall)} presentations, {fmt(n_starts)} CoV starts; every "
          "presentation weighted equally. A start with an unsolved control counts as cheaper "
          "when it solves.", "",
          "| control's nodes | presentations | " + " | ".join(l for l, _ in table) + " |",
          "|---|---|" + "---|" * len(table)]
    for i, (n, g) in enumerate(zip(names, order)):
        md.append(f"| {n} | {len(groups.get(g, []))} | "
                  + " | ".join(f"{v[i]:.1%}" for _, v in table) + " |")
    md.append(f"| all | {len(overall)} | "
              + " | ".join(f"{o[k]:.1%}" for k, _, _ in OUTCOMES) + " |")
    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    a = ap.parse_args()
    base = os.path.splitext(a.file)[0] + "_control_vs_cov"
    md = plot(a.file, base + ".png")
    with open(base + ".md", "w") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
