"""Rank-3/4/5 starts against the 2-generator control, drawn like the CoV figure.

Same picture as ``cov/run/plot_cov_all_control_vs_cov.py`` (colours, bins and
panels are taken from it): one point of mass per (presentation, start), x the
control's ``nodes_explored``, y the start's. Above y = x the start needs more
nodes than ``<x, y | r1, r2>``, below it fewer; a search that did not solve
within the budget sits in the "unsolved" row / column.

A start is ``<x, y, z | r1, r2, Z.w>`` for one word w (``--rank3``) or
``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>`` for one multiset of words
(``--rankn``). Every presentation has the same number of starts and carries the
same total weight, so the picture is the outcome of drawing one presentation,
then one start, uniformly at random. With ``--rank3`` the starts are all words
of the chosen lengths, so two thirds of them have the largest length; the
markdown file gives the same table per length.

``--noise`` (default 0.17, the 90th percentile of the node gap between a
presentation and its y <-> Y mirror image, PLAN.md §11 item 10) adds two
columns: starts that beat, or lose to, the control by more than that fraction.
A smaller difference is what relabeling the generators already produces.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.rank3.plot_rankn_vs_control \
        --rank3 results/stable_ac/rank3_bf --budget 1000 [--lengths 1-10]
    python3 -m experiments.stable_ac.rank3.plot_rankn_vs_control \
        --rankn results/stable_ac/rank3_bf/rankn_bf_ms640_b1000_cap24_r4.npz
writes ``<stem>_control_vs_start[_L<a>-<b>].png`` and ``.md`` next to the data.
"""

import argparse
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm

from experiments.stable_ac.cov.run.plot_cov_all_control_vs_cov import (
    AXIS, BLUES, INK, INK2, MUTED, OUTCOMES, PER_DECADE, SURFACE, fmt,
)
from experiments.stable_ac.rank3.run_rank3_bf import CAP, stem

KEYS = [k for k, _, _ in OUTCOMES]


def load_rank3(d, source, budget, cap, lengths):
    """-> control solved [P], control nodes [P], {length: (nodes [P, K], solved [P, K])}"""
    base = os.path.join(d, stem(source, budget, cap))
    ctrl = {}
    with open(base + "_control.jsonl") as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                ctrl[r["pres_id"]] = r
    blocks, ids = {}, None
    for n in lengths:
        path = f"{base}_L{n}.npz"
        if not os.path.exists(path):
            continue
        with np.load(path) as z:
            p = [int(x) for x in z["pres_ids"]]
            assert ids is None or p == ids, f"{path}: presentation order differs"
            ids = p
            blocks[n] = (z["nodes"].astype(np.int32), z["path_len"] >= 0)
    assert blocks, f"no {base}_L*.npz for lengths {lengths}"
    return (np.array([bool(ctrl[p]["solved"]) for p in ids]),
            np.array([int(ctrl[p]["nodes_explored"]) for p in ids]), blocks)


def load_rankn(path):
    with np.load(path) as z:
        meta = json.loads(str(z["meta"]))
        base = z["base"]
        return (meta, base[:, 0] == 1, base[:, 1].astype(np.int64),
                {0: (z["nodes"].astype(np.int32), z["path_len"] >= 0)})


def fractions(c_solved, c_nodes, nodes, solved, noise):
    """Per presentation: share of its starts in each outcome (same rule as the
    CoV figure: a start that solves an unsolved control counts as cheaper)."""
    cs, cn = c_solved[:, None], c_nodes[:, None]
    out = {"cheaper": solved & (~cs | (nodes < cn)),
           "equal": solved & cs & (nodes == cn),
           "dearer": solved & cs & (nodes > cn),
           "fail": ~solved,
           "cheaper_clear": solved & (~cs | (nodes < cn * (1 - noise))),
           "dearer_clear": solved & cs & (nodes > cn * (1 + noise))}
    return {k: v.mean(axis=1) for k, v in out.items()}


def table_rows(c_solved, c_nodes, frac, decades):
    """-> [(name, n presentations, {outcome: mean share})] by the control's nodes."""
    g = np.where(c_solved,
                 np.minimum(np.floor(np.log10(np.maximum(c_nodes, 1)) + 1e-9), decades - 1),
                 decades).astype(int)
    names = [f"{fmt(10 ** d)} to {fmt(10 ** (d + 1) - 1)}" for d in range(decades)] + ["unsolved"]
    rows = []
    for i, name in enumerate(names):
        m = g == i
        rows.append((name, int(m.sum()),
                     {k: float(v[m].mean()) if m.any() else 0.0 for k, v in frac.items()}))
    rows.append(("all", len(g), {k: float(v.mean()) for k, v in frac.items()}))
    return rows


def md_table(rows, noise):
    head = ["control's nodes", "presentations"] + [l for _, l, _ in OUTCOMES] + [
        f"fewer by more than {noise:.0%}", f"more by more than {noise:.0%}"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for name, n, f in rows:
        out.append(f"| {name} | {n} | " + " | ".join(
            f"{f[k]:.1%}" for k in KEYS + ["cheaper_clear", "dearer_clear"]) + " |")
    return out


def draw(out_png, c_solved, c_nodes, nodes, solved, budget, rows, title, sub, ylabel, start_name):
    decades = round(math.log10(budget))
    nb = decades * PER_DECADE
    P, K = nodes.shape

    # bin index along one axis; index nb + 1 is the unsolved rail, nb is a gap
    def idx(v, ok):
        b = np.minimum(np.floor(np.log10(np.maximum(v, 1)) * PER_DECADE + 1e-9), nb - 1)
        return np.where(ok, b, nb + 1).astype(np.int64)

    ix = np.broadcast_to(idx(c_nodes, c_solved)[:, None], nodes.shape)
    H = np.bincount((idx(nodes, solved) * (nb + 2) + ix).ravel(),
                    minlength=(nb + 2) ** 2).reshape(nb + 2, nb + 2) / (P * K)

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
    ax.set_ylabel(ylabel)
    ax.text(0.9, nb - 0.5, f"above the line: the {start_name} needs more nodes",
            color=INK2, rotation=90, ha="center", va="top", fontsize=9.5)
    ax.text(nb - 0.5, 0.6, f"below the line:\nthe {start_name} needs fewer nodes",
            color=INK2, ha="right", va="bottom", fontsize=9.5)
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, labelsize=8.5)
    cb.set_label("share of random (presentation, start) draws in the cell",
                 color=INK2, fontsize=9)

    fig.text(0.17, 0.975, title, color=INK, fontsize=14, fontweight="bold", ha="left", va="top")
    fig.text(0.17, 0.95, sub, color=INK2, fontsize=9.5, ha="left", va="top", linespacing=1.45)

    groups = rows[:-1]
    left = np.zeros(len(groups))
    for key, label, color in OUTCOMES:
        vals = np.array([f[key] for _, _, f in groups])
        bx.barh(range(len(groups)), vals, left=left, color=color, height=0.72,
                edgecolor=SURFACE, linewidth=1.5, label=label)
        for i, (v, l) in enumerate(zip(vals, left)):
            if v >= 0.07:
                bx.text(l + v / 2, i, f"{v:.0%}", ha="center", va="center", fontsize=8.5,
                        color="#ffffff" if key in ("cheaper", "fail") else INK)
        left += vals
    bx.set_yticks(range(len(groups)), [name for name, _, _ in groups])
    for i, (_, n, _) in enumerate(groups):
        bx.text(1.012, i, f"n = {n}", ha="left", va="center", fontsize=8.5, color=INK2)
    bx.invert_yaxis()
    bx.set_xlim(0, 1)
    bx.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
    bx.tick_params(length=0)
    bx.spines["left"].set_visible(False)
    bx.set_xlabel("share of a presentation's starts, mean over the group's presentations")
    bx.set_title("Does a random start beat the control? Grouped by the control's nodes "
                 "(n = presentations)", color=INK, fontsize=10.5, loc="left", x=-0.2, pad=40)
    bx.legend(loc="lower left", bbox_to_anchor=(-0.21, 1.0), ncol=2, frameon=False,
              fontsize=8.5, handlelength=1.1, columnspacing=1.6, labelcolor=INK2,
              borderaxespad=0.2)
    fig.savefig(out_png, dpi=170, facecolor=SURFACE)
    plt.close(fig)


def sentence(o):
    return (f"A random start needs fewer nodes {o['cheaper']:.0%} of the time, the same "
            f"{o['equal']:.0%}, more {o['dearer']:.0%},\nand is unsolved {o['fail']:.0%}. "
            "A solve from any start certifies stable AC-triviality.")


def run(c_solved, c_nodes, blocks, budget, noise, out_base, title, what, ylabel, start_name,
        block_name):
    decades = round(math.log10(budget))
    nodes = np.concatenate([blocks[k][0] for k in sorted(blocks)], axis=1)
    solved = np.concatenate([blocks[k][1] for k in sorted(blocks)], axis=1)
    rows = table_rows(c_solved, c_nodes, fractions(c_solved, c_nodes, nodes, solved, noise), decades)
    P, K = nodes.shape
    sub = (f"MS640, baseline greedy, budget {fmt(budget)} nodes; {P} presentations, each "
           f"weighted equally.\n{fmt(K)} starts each: {what}.\n" + sentence(rows[-1][2]))
    draw(out_base + ".png", c_solved, c_nodes, nodes, solved, budget, rows, title, sub, ylabel,
         start_name)
    md = [f"# Control vs a random {start_name}: `{os.path.basename(out_base)}`", "",
          f"Budget {fmt(budget)}; {P} presentations, {fmt(K)} starts each ({what}; "
          f"{fmt(P * K)} searches); every presentation weighted equally. A start with an "
          "unsolved control counts as "
          f"having fewer nodes when it solves. Control solved: {int(c_solved.sum())} of {P}.", ""]
    md += md_table(rows, noise)
    if len(blocks) > 1:
        md += ["", f"## Per {block_name}", "",
               f"The `all` row of the table above, for the starts of one {block_name} at a time.", "",
               f"| {block_name} | starts | " + " | ".join(l for _, l, _ in OUTCOMES)
               + f" | fewer by more than {noise:.0%} | more by more than {noise:.0%} |",
               "|---|---|" + "---|" * (len(OUTCOMES) + 2)]
        for k in sorted(blocks):
            f = {a: float(b.mean()) for a, b in
                 fractions(c_solved, c_nodes, blocks[k][0], blocks[k][1], noise).items()}
            md.append(f"| {k} | {fmt(blocks[k][0].shape[1])} | " + " | ".join(
                f"{f[a]:.1%}" for a in KEYS + ["cheaper_clear", "dearer_clear"]) + " |")
    with open(out_base + ".md", "w") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


def parse_lengths(s):
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank3", default=None, help="results directory of run_rank3_bf")
    ap.add_argument("--rankn", default=None, help="one rankn_bf_*_r<rank>.npz")
    ap.add_argument("--source", default="ms640")
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--lengths", default="1-99", help="word lengths for --rank3, e.g. 1-10 or 4")
    ap.add_argument("--noise", type=float, default=0.17)
    a = ap.parse_args(argv)
    assert (a.rank3 is None) != (a.rankn is None), "give exactly one of --rank3, --rankn"
    if a.rank3:
        c_solved, c_nodes, blocks = load_rank3(a.rank3, a.source, a.budget, a.cap,
                                               parse_lengths(a.lengths))
        lo, hi = min(blocks), max(blocks)
        span = f"length {lo}" if lo == hi else f"lengths {lo} to {hi}"
        run(c_solved, c_nodes, blocks, a.budget, a.noise,
            os.path.join(a.rank3, stem(a.source, a.budget, a.cap)) + f"_control_vs_start_L{lo}-{hi}",
            "A random 3-generator start against the 2-generator control",
            f"<x,y,z | r1, r2, Z·w> for every word w of {span}",
            "nodes explored from a 3-generator start", "3-generator start", "word length")
    else:
        meta, c_solved, c_nodes, blocks = load_rankn(a.rankn)
        r, k, m = meta["rank"], meta["extra_generators"], meta["max_word_len"]
        run(c_solved, c_nodes, blocks, meta["node_budget"], a.noise,
            os.path.splitext(a.rankn)[0] + "_control_vs_start",
            f"A random {r}-generator start against the 2-generator control",
            f"{k} new generators z_i, relators Z_i·w_i, every {k} words of length at most {m}",
            f"nodes explored from a {r}-generator start", f"{r}-generator start", "block")


if __name__ == "__main__":
    main()
