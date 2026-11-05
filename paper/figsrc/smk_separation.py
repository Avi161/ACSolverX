"""Appendix E: how well S and MK separate the MS1190 presentations LENGTH solves from those it does not.

Three populations, all built from data/ in this repository:
  cells    the 1190 starting presentations of MS1190: 640 in data/ms640_solved.txt, the other 550 unsolved;
  orbits   each cell replaced by its Aut(F2)-minimal form, duplicates removed: 113 solved, 159 unsolved;
  classes  the 113 solved orbits against the 124 unsolved ACA classes (data/ms_unsolved_reps/aca_124_initial.csv),
           the population of the summer clustering study (experiments/clustering on the heuristic branches).
S, MK and lambda are acx.core.priority.features, the definitions the search uses. AUROC is the probability that an
unsolved presentation has the larger value, ties counting one half; the 95% interval is a stratified bootstrap.

    python3 paper/figsrc/smk_separation.py        # writes figures/smk_distributions.png, figures/smk_roc.png
"""
import collections
import csv
import os
import sys

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, ROOT)
from acx.aut.whitehead import aut_canon          # noqa: E402
from acx.core.priority import features, s20_mk2  # noqa: E402
from acx.data import rows                        # noqa: E402

FIG = os.path.join(HERE, "..", "figures")
INK = "#0b0b0b"; INK2 = "#52514e"; GRID = "#e4e3df"; GREY = "#8a8984"; BLUE = "#2a78d6"; ORANGE = "#eb6834"
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "mathtext.fontset": "cm"})


def _parse(word):
    return tuple((1 if c in "xX" else 2) * (-1 if c.isupper() else 1) for c in word)


def populations():
    """``{name: (list of relator tuples, labels)}``, label 1 for unsolved."""
    cells = rows("1190ms")
    solved = {r.pres.rels for r in rows("ms640")}
    lab = [0 if r.pres.rels in solved else 1 for r in cells]
    assert collections.Counter(lab) == {0: 640, 1: 550}
    orbit = {}
    for r, y in zip(cells, lab):
        rep = aut_canon(r.pres).rep.rels
        assert orbit.setdefault(rep, y) == y, "an orbit cannot be both solved and unsolved"
    assert collections.Counter(orbit.values()) == {0: 113, 1: 159}
    sol = [k for k, y in orbit.items() if y == 0]
    with open(os.path.join(ROOT, "data/ms_unsolved_reps/aca_124_initial.csv")) as f:
        aca = [(_parse(r["r1"]), _parse(r["r2"])) for r in csv.DictReader(f)]
    assert len(aca) == 124
    return {"cells": ([r.pres.rels for r in cells], lab),
            "orbits": (list(orbit), list(orbit.values())),
            "classes": (sol + aca, [0] * len(sol) + [1] * len(aca))}


def table(rels):
    """Columns lambda, S, MK, pi_SMK."""
    f = np.array([features(r) for r in rels], float)           # (L, MK, S)
    return {"lambda": f[:, 0], "S": f[:, 2], "MK": f[:, 1], "pi": np.array([s20_mk2(r) for r in rels])}


def auroc(v, y):
    """Mann-Whitney AUROC with average ranks for ties."""
    _, inv, cnt = np.unique(v, return_inverse=True, return_counts=True)
    rank = (np.cumsum(cnt) - (cnt - 1) / 2)[inv]
    n1 = y.sum(); n0 = len(y) - n1
    return (rank[y == 1].sum() - n1 * (n1 + 1) / 2) / (n0 * n1)


def interval(v, y, reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    i0, i1 = np.flatnonzero(y == 0), np.flatnonzero(y == 1)
    a = [auroc(v[idx], y[idx]) for idx in
         (np.concatenate([rng.choice(i0, len(i0)), rng.choice(i1, len(i1))]) for _ in range(reps))]
    return np.percentile(a, [2.5, 97.5])


def length_removed(v, lam):
    A = np.column_stack([np.ones(len(lam)), lam])
    return v - A @ np.linalg.lstsq(A, v, rcond=None)[0]


def roc(v, y):
    t = np.unique(v)[::-1]
    tpr = [0.0] + [((v >= s) & (y == 1)).sum() / y.sum() for s in t]
    fpr = [0.0] + [((v >= s) & (y == 0)).sum() / (y == 0).sum() for s in t]
    return fpr, tpr


def _label(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def bars(ax, v, y, name, width=None):
    """Share of each group per value; with ``width``, per bin of that width centred on a multiple of it."""
    if width:
        k = np.round(v / width).astype(int)
        cen = np.arange(k.min(), k.max() + 1); pos = cen * width; w = width * 0.42
    else:
        k = v; cen = np.unique(v); pos = np.arange(len(cen)); w = 0.38
    for j, (cls, c, nm) in enumerate(((0, BLUE, "solved"), (1, ORANGE, "unsolved"))):
        share = [((k == u) & (y == cls)).sum() / (y == cls).sum() for u in cen]
        ax.bar(pos + (j - 0.5) * w, share, w * 0.92, color=c, label=f"{nm} ({(y == cls).sum()})")
    if not width:
        ax.set_xticks(pos, [_label(u) for u in cen])
    ax.set_xlabel(name); ax.set_ylabel("share of the group")
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)


def main():
    pops = populations()
    title = {"cells": "MS1190 cells", "orbits": "Aut-minimal orbits", "classes": "orbits and ACA classes"}
    print(f"{'population':10s} {'n0':>4s} {'n1':>4s}  " + "  ".join(f"{c:>22s}" for c in ("lambda", "S", "MK", "pi")))
    res = {}
    for p, (rels, lab) in pops.items():
        y = np.array(lab); t = table(rels); res[p] = (t, y)
        cols = []
        for c in ("lambda", "S", "MK", "pi"):
            lo, hi = interval(t[c], y)
            lr = "  -  " if c == "lambda" else f"{auroc(length_removed(t[c], t['lambda']), y):.3f}"
            cols.append(f"{auroc(t[c], y):.3f} [{lo:.3f},{hi:.3f}] {lr}")
        print(f"{p:10s} {(y == 0).sum():4d} {(y == 1).sum():4d}  " + "  ".join(f"{c:>22s}" for c in cols))
        for c in ("S", "MK"):
            print(f"    mean {c}: solved {t[c][y == 0].mean():.3f}, unsolved {t[c][y == 1].mean():.3f}")
        s = t["S"]
        tp = ((s > 1.25) & (y == 1)).sum(); tn = ((s <= 1.25) & (y == 0)).sum()
        print(f"    rule S > 1.25: balanced accuracy {0.5 * (tp / y.sum() + tn / (y == 0).sum()):.3f}")

    shown = ("cells", "classes")
    f, axs = plt.subplots(2, 2, figsize=(6.8, 4.6))
    for i, p in enumerate(shown):
        t, y = res[p]
        for j, c in enumerate(("S", "MK")):
            ax = axs[i, j]
            bars(ax, t[c], y, "$S$ (bins of width $0.05$)" if c == "S" else r"$\mathrm{MK}$", 0.05 if c == "S" else None)
            ax.set_title(f"{title[p]}: AUROC {auroc(t[c], y):.3f}", fontsize=8)
            if j == 0:
                ax.legend(frameon=True, framealpha=0.95, edgecolor=GRID, fontsize=7, loc="upper right")
    f.tight_layout(); f.savefig(os.path.join(FIG, "smk_distributions.png"), dpi=300); plt.close(f)

    f, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))
    style = {"lambda": (GREY, "--", r"$\lambda$"), "S": (BLUE, "-", "$S$"), "MK": (ORANGE, "-", r"$\mathrm{MK}$"),
             "pi": (INK, ":", r"$\pi_{\mathrm{S20\_MK2}}$")}
    for ax, p in zip(axs, shown):
        t, y = res[p]
        ax.plot([0, 1], [0, 1], color=GRID, lw=0.8)
        for c, (col, ls, nm) in style.items():
            fpr, tpr = roc(t[c], y)
            ax.plot(fpr, tpr, color=col, ls=ls, lw=1.4, label=f"{nm}  {auroc(t[c], y):.3f}")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1.005); ax.set_aspect("equal")
        ax.set_xlabel("false positive rate (solved flagged)"); ax.set_ylabel("true positive rate (unsolved flagged)")
        ax.set_title(f"{title[p]} ({(y == 0).sum()} solved, {(y == 1).sum()} unsolved)", fontsize=8)
        ax.legend(title="feature, AUROC", title_fontsize=7, frameon=True, framealpha=0.95, edgecolor=GRID,
                  fontsize=7, loc="lower right")
    f.tight_layout(); f.savefig(os.path.join(FIG, "smk_roc.png"), dpi=300); plt.close(f)


if __name__ == "__main__":
    main()
