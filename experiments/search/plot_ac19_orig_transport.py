"""One panel per original: total relator length along the path, both starting points.

The claim the picture makes, and the reason the picture is the argument: the two
curves are THE SAME SEQUENCE OF AC MOVES. The blue curve starts at the raw
dataset presentation, the orange one starts at its ``Aut(F2)``-minimal
representative, and move ``k`` of one is move ``k`` of the other with its
conjugator word carried through ``phi`` (``transport_ac19_orig``). They run in
lockstep to the blue curve's terminal, and then the orange one needs a short
dashed tail -- 1 to 4 Nielsen moves -- because ``phi`` of a terminal pair is a
basis of F2 rather than two single letters.

So the panels show three things at once: the moves really are shared, the
aut-min pair has to climb much higher in relator length along the identical
route, and the extra cost at the end is tiny.

    PYTHONPATH=. python3 -m experiments.search.plot_ac19_orig_transport
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.equivalence_classes.lib.words import apply_hom, canon_pair
from experiments.search.ac_decode import reduce_basis
from experiments.search.greedy_baseline import moves_to_states
from experiments.search import make_ac19_orig_10m_lists as mk
from experiments.search.run_leftovers_1m import read_rows

OUT_DIR = os.path.join(mk.RESULTS_DIR, "ac19_orig_10m")
JSONL = "ac19_orig_10m_greedy_b10000000_mrl64.jsonl"
STEM = "ac19_orig_10m_transport_profiles"

# Categorical slots 1 and 2 of the validated default palette. The pair passes
# every check under --pairs all (CVD dE 24.7, normal-vision 33.6, both >= 3:1
# on the surface), which is the gate small multiples have to clear.
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e6e3"

plt.rcParams.update({
    # Liberation Sans is metric-compatible with Arial and is what this box has;
    # naming absent families only produces a findfont warning per text object.
    "font.family": "Liberation Sans, DejaVu Sans, sans-serif",
    "font.size": 8, "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "axes.titlesize": 8.5, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.labelcolor": MUTED, "figure.facecolor": "white",
    "axes.facecolor": "white", "svg.fonttype": "none",
})


def profiles(rec):
    """``(original lengths, aut-min lengths, tail length)`` for one record.

    Both lists are indexed by AC move number and share their first
    ``len(path_moves) + 1`` entries' move sequence; the aut-min list then
    carries its Nielsen tail.
    """
    orig = (rec["r1"], rec["r2"])
    _, rep, phi = aut_canon(orig)
    a = [len(s[0]) + len(s[1]) for s in rec["path"]]
    moved = [canon_pair(apply_hom(s[0], phi), apply_hom(s[1], phi))
             for s in rec["path"]]
    b = [len(p[0]) + len(p[1]) for p in moved]
    basis = moved[-1]
    tail = reduce_basis(basis) or []
    for state in moves_to_states(basis[0], basis[1], tail)[1:]:
        b.append(len(state[0]) + len(state[1]))
    return a, b, len(tail), rep


def build(rows, orbit_of):
    n = len(rows)
    cols = 5
    rowsn = (n + cols - 1) // cols
    fig, axes = plt.subplots(rowsn, cols, figsize=(15.5, 2.35 * rowsn))
    axes = axes.ravel()
    for ax in axes[n:]:
        ax.axis("off")

    for ax, rec in zip(axes, rows):
        a, b, tail, rep = profiles(rec)
        split = len(a) - 1                      # last shared move index
        ax.plot(range(len(a)), a, color=BLUE, lw=1.5, zorder=3)
        ax.plot(range(split + 1), b[:split + 1], color=ORANGE, lw=1.5, zorder=4)
        # the tail, dashed: identity is never carried by colour alone
        ax.plot(range(split, len(b)), b[split:], color=ORANGE, lw=1.5,
                ls=(0, (2.2, 1.6)), zorder=4)
        ax.plot([len(a) - 1], [a[-1]], "o", ms=3.4, color=BLUE,
                mec="white", mew=0.8, zorder=5)
        ax.plot([len(b) - 1], [b[-1]], "o", ms=3.4, color=ORANGE,
                mec="white", mew=0.8, zorder=5)
        ax.set_title(f'{orbit_of[rec["name"]]}  ·  {rec["name"]}',
                     color=INK, pad=4, loc="left")
        ax.text(0.985, 0.93, f"+{tail}", transform=ax.transAxes, ha="right",
                va="top", fontsize=8, color=ORANGE, fontweight="bold")
        ax.text(0.985, 0.76, f'{rec["nodes_explored"]:,} nodes',
                transform=ax.transAxes, ha="right", va="top", fontsize=7,
                color=MUTED)
        ax.grid(True, color=GRID, lw=0.6, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.margins(x=0.03, y=0.14)
        ax.set_ylim(bottom=0)

    handles = [Line2D([], [], color=BLUE, lw=1.8,
                      label="from the ORIGINAL dataset presentation"),
               Line2D([], [], color=ORANGE, lw=1.8,
                      label="from its AUT-MIN representative, identical moves"),
               Line2D([], [], color=ORANGE, lw=1.8, ls=(0, (2.2, 1.6)),
                      label="the aut-min pair's extra Nielsen tail (+1 to +4)")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.006, 0.998),
               frameon=False, ncol=3, fontsize=9.5, handlelength=2.4,
               labelcolor=INK)
    fig.suptitle("The same AC moves, seen from both starting points  ·  "
                 "x: AC move number   y: total relator length",
                 x=0.006, y=0.978, ha="left", fontsize=11.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.962))
    return fig


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args(argv)
    orbit_of = {r["name"]: r["orbit"] for r in mk.build()["greedy"]}
    rows = read_rows(os.path.join(OUT_DIR, JSONL))
    if len(rows) != 40:
        raise RuntimeError(f"expected 40 greedy originals, found {len(rows)}")
    rows.sort(key=lambda r: (int(orbit_of[r["name"]].split("_")[1]),
                             int(r["name"].split("_")[1])))
    fig = build(rows, orbit_of)
    for ext in ("svg", "png"):
        path = os.path.join(args.out_dir, f"{STEM}.{ext}")
        fig.savefig(path, dpi=170)
        print(f"  wrote {os.path.relpath(path)} ({os.path.getsize(path):,} B)")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
