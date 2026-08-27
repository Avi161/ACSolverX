"""Figures for the CoV-quality finding, into results/stable_ac/cov/ml/.

    .venv/bin/python3 experiments/stable_ac/cov/ml/cov_figures.py

Palette is blue / orange with a second non-colour channel on every series (marker shape, dash,
hatch) — the deck's reader is red-green colourblind, so colour never carries meaning alone.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cov_features import load_dataset, cost, default_path  # noqa: E402
from cov_rank import spearman, geo_mean  # noqa: E402

INK = "#16181d"
GRAY = "#b9bec9"
MUTED = "#9aa1b0"
BLUE = "#4864e8"
ORANGE = "#e8814a"
FAINT = "#e8eaf0"

plt.rcParams.update({
    "font.family": "Helvetica Neue, Helvetica, Arial, sans-serif",
    "font.size": 12,
    "axes.edgecolor": "#d7dae2", "axes.linewidth": 0.8,
    "axes.titlesize": 13, "axes.titleweight": "medium",
    "xtick.color": "#6b7280", "ytick.color": "#6b7280",
    "axes.labelcolor": "#3c4250",
    "figure.facecolor": "white", "axes.facecolor": "white",
})

OUT = None


def strip(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=FAINT, lw=0.8, zorder=0)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=170)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- figures

def fig_simpson(ds, am, tot, c):
    """The whole methodological point: pooled says length, per-presentation says abelian mass."""
    logc = np.log10(np.maximum(c, 1.0))
    P = sorted(set(ds.pres.tolist()))
    rho_am = np.array([spearman(am[ds.pres == p], c[ds.pres == p]) for p in P], dtype=float)
    rho_len = np.array([spearman(tot[ds.pres == p], c[ds.pres == p]) for p in P], dtype=float)
    keep = ~np.isnan(rho_am) & ~np.isnan(rho_len)

    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.4))

    ax = axes[0]
    ax.scatter(am, logc, s=6, color=BLUE, alpha=0.16, lw=0, zorder=3)
    ax.set_xlabel("abelian mass of the transformed pair")
    ax.set_ylabel("log₁₀ cost  (nodes, or budget if unsolved)")
    ax.set_title(f"pooled over all {len(ds):,} CoV rows  ·  r = "
                 f"{np.corrcoef(logc, am)[0, 1]:+.2f}", loc="left")
    strip(ax)

    ax = axes[1]
    order = np.argsort(rho_am[keep])
    y = np.arange(keep.sum())
    ax.scatter(rho_am[keep][order], y, s=30, color=BLUE, marker="o",
               label="abelian mass", zorder=4)
    ax.scatter(rho_len[keep][order], y, s=34, facecolors="none", edgecolors=ORANGE,
               marker="s", linewidths=1.3, label="total relator length", zorder=3)
    ax.axvline(0, color=MUTED, lw=1, ls=(0, (4, 4)), zorder=1)
    ax.set_xlim(-0.6, 1.02)
    ax.set_yticks([])
    ax.set_xlabel("Spearman ρ against cost, within one presentation")
    ax.set_ylabel(f"the {keep.sum()} presentations some CoV solves  →")
    ax.set_title("per presentation  ·  median ρ  "
                 f"{np.median(rho_am[keep]):+.2f}  vs  {np.median(rho_len[keep]):+.2f}",
                 loc="left")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="x", color=FAINT, lw=0.8, zorder=0)
    ax.legend(frameon=False, loc="upper left", fontsize=11)
    save(fig, "simpson.png")


def fig_picker(res):
    """What one pick costs, per picker — the deployable comparison."""
    order = ["random", "heuristic · shortest result", "heuristic · moved only",
             "heuristic · abelian mass", "ridge · centred", "GBT · centred"]
    by = {(s["picker"], s["k"]): s for s in res["summary"]}
    ks = [1, 3, 5]
    # Arithmetic mean on the COMMON subset — the presentations every picker solves. Scoring each
    # picker on its own solved set would let the weak ones drop exactly the presentations they
    # failed, which are the expensive ones.
    val = lambda p, k: by[(p, k)]["mean_nodes_common"]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4),
                             gridspec_kw={"width_ratios": [1.25, 1]})

    # Dots, not bars: on a log axis a bar's length is measured from the axis minimum, which is
    # an arbitrary number, so bar length would encode nothing.
    ax = axes[0]
    y = np.arange(len(order))
    marks = [("o", 9, BLUE, "full"), ("D", 8, BLUE, "half"), ("s", 8, BLUE, "none")]
    for j, k in enumerate(ks):
        vals = [val(p, k) for p in order]
        mk, ms, col, fill = marks[j]
        ax.plot(vals, y + (j - 1) * 0.17, mk, ms=ms, color=col,
                mfc=col if fill == "full" else ("white" if fill == "none" else col),
                alpha=1.0 if fill != "half" else 0.45, mew=1.4,
                ls="none", label=f"best of first {k}", zorder=4)
    for i in y:
        lo = min(val(order[i], k) for k in ks)
        hi = max(val(order[i], k) for k in ks)
        ax.plot([lo, hi], [i, i], color=GRAY, lw=1.2, zorder=2)

    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.set_ylim(-0.6, len(order) - 0.3)
    ax.set_xscale("log")
    ax.set_xlim(min(val(p, 5) for p in order) * 0.6, max(val(p, 1) for p in order) * 1.35)
    ax.set_xlabel("mean nodes of the chosen start, on the presentations all pickers solve")
    ax.set_title(f"budget {res['budget']:,}  ·  scored on the "
                 f"{by[(order[0], 1)]['n_common']} presentations every picker solves", loc="left")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.grid(axis="x", color=FAINT, lw=0.8, zorder=0)
    ax.legend(frameon=False, fontsize=10.5, loc="lower right", numpoints=1)

    ax = axes[1]
    for p, marker, color in [("GBT · centred", "o", BLUE),
                             ("heuristic · abelian mass", "D", BLUE),
                             ("heuristic · shortest result", "s", ORANGE),
                             ("random", "^", GRAY)]:
        ax.plot(ks, [by[(p, k)]["n_solved"] for k in ks], marker=marker,
                color=color, lw=1.8, ms=8,
                mfc="white" if marker in ("D", "s") else color, label=p, zorder=3)
    orc = res["oracle_solve_rate"] * res["n_pres"]
    ax.axhline(orc, color=ORANGE, lw=1.6, ls=(0, (5, 3)), zorder=2)
    ax.text(ks[-1], orc + 0.25, "oracle — every CoV tried",
            color=ORANGE, fontsize=10.5, ha="right")
    ax.set_xticks(ks)
    ax.set_xlabel("how many starts you are willing to run")
    ax.set_ylabel(f"presentations solved, of {res['n_pres']}")
    strip(ax)
    ax.legend(frameon=False, fontsize=10.5, loc="lower right")
    save(fig, "picker.png")


def fig_mass_curve(ds, am, c):
    """Solve rate and cost against abelian mass, per presentation then averaged — the shape
    behind the ranking. Pooled counts would show the Simpson-flattened version instead."""
    P = sorted(set(ds.pres.tolist()))
    bins = [(2, 2), (3, 3), (4, 4), (5, 5), (6, 7), (8, 9), (10, 31)]
    labels = ["2", "3", "4", "5", "6–7", "8–9", "10+"]
    solve, costs, n = [], [], []
    for lo, hi in bins:
        # per presentation first: each presentation contributes one solve-rate and one geo-cost,
        # so a presentation with 170 candidates cannot outvote one with 11
        s_p, c_p = [], []
        for p in P:
            m = (ds.pres == p) & (am >= lo) & (am <= hi)
            if not m.any():
                continue
            s_p.append(ds.solved[m].mean())
            c_p.append(geo_mean(c[m]))
        solve.append(np.mean(s_p))
        costs.append(geo_mean(c_p))
        n.append(len(s_p))

    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    x = np.arange(len(bins))
    ax.bar(x, solve, width=0.55, color=BLUE, alpha=0.85, zorder=3, label="solve rate")
    for i, (v, k) in enumerate(zip(solve, n)):
        ax.text(i, v + 0.012, f"{100 * v:.0f}%", ha="center", fontsize=11, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("abelian mass of the transformed pair  (2 = abelianisation already trivial)")
    ax.set_ylabel("solve rate within a presentation")
    ax.set_ylim(0, max(solve) * 1.22)
    strip(ax)

    ax2 = ax.twinx()
    ax2.plot(x, costs, marker="D", ms=9, mfc="white", color=ORANGE, lw=2.0,
             ls=(0, (5, 2)), zorder=4, label="geo-mean cost")
    ax2.set_yscale("log")
    ax2.set_ylabel("geometric-mean cost (nodes, log)", color=ORANGE)
    ax2.tick_params(axis="y", colors=ORANGE)
    for s_ in ("top",):
        ax2.spines[s_].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, loc="upper center", fontsize=11, ncol=2)
    ax.set_title(f"budget {ds.budget:,}  ·  averaged per presentation, "
                 f"not pooled over rows", loc="left")
    save(fig, "abelian_mass.png")


def main():
    global OUT
    path = default_path()
    here = os.path.dirname(os.path.abspath(path))
    OUT = os.path.join(here, "ml")
    os.makedirs(OUT, exist_ok=True)

    ds = load_dataset(path)
    c = cost(ds)
    am = ds.X[:, ds.names.index("cov_r1_exp_l1")] + ds.X[:, ds.names.index("cov_r2_exp_l1")]
    tot = ds.X[:, ds.names.index("cov_total_len")]

    fig_simpson(ds, am, tot, c)
    fig_mass_curve(ds, am, c)
    with open(os.path.join(OUT, "rank_b10000.json")) as f:
        fig_picker(json.load(f))


if __name__ == "__main__":
    main()
