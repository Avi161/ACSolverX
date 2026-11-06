"""Figure maxrel_example.png: total relator length along each method's solution path of MS640 row 636, the row on
which the hybrid's AC path reaches its longest relator (509). Data: results/benchmark_rows/paths/ms640.jsonl.gz.

    python paper/figsrc/maxrel_example.py
"""
import gzip
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from acx.core.moves import Move  # noqa: E402
from acx.core.words import canonical_rels, parse, reduce  # noqa: E402
from acx.data import parse_presentation  # noqa: E402
from acx.hybrid.steps import aut_child, move_child  # noqa: E402
from acx.verify.pack import unpack  # noqa: E402
from acx.verify.replay import replay  # noqa: E402

ROW = "636"
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]   # categorical slots 1-7
INK, MUTED, GRID = "#1f1f1e", "#5f5e58", "#e4e3dc"


def total(rels):
    return sum(len(reduce(tuple(w))) for w in rels)


def series(pres, m, p):
    """(totals along the path, indices of the CoV moves or Nielsen maps)"""
    f = p["format"]
    if f == "smoves":
        st = replay(pres, [Move(*x) for x in p["path"]], cyclic=True, cap=int(p["cap"]))
        return [total(s.rels) for s in st], []
    if f == "hybrid":
        cur = canonical_rels(tuple(reduce(r) for r in pres.rels))
        ys, special = [total(cur)], []
        for i, s in enumerate(p["certificate"], 1):
            if isinstance(s, dict):
                cur = aut_child(cur, s["aut"])
                special.append(i)
            else:
                cur = move_child(cur, Move(*s))
            ys.append(total(cur))
        return ys, special
    if f == "cov_gate":
        ys = [total([parse(w) for w in s["state"]["relators_text"]]) for s in p["path"]]
        return ys, [i for i, s in enumerate(p["path"]) if s.get("kind") == "img"]
    if f == "elliot":
        ys = [total(parse(w) for w in s) for s in p["path"]]
        return ys, [i + 1 for i, k in enumerate(p["moves"]) if k != "standard_substitution"]
    raise ValueError(f)


def main():
    rows = {r["id"]: r for r in map(json.loads, (ROOT / "results/benchmark_rows/ms640.jsonl").read_text().splitlines())}
    for line in gzip.open(ROOT / "results/benchmark_rows/paths/ms640.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["id"] == ROW:
            break
    pres = parse_presentation(", ".join(rows[ROW]["pres"]))
    names = ["LENGTH", "S20_MK2", "hybrid", "CoV gate", "triple"]     # triple: the best of the dual and triple searches
    colors = {"LENGTH": COLORS[0], "S20_MK2": COLORS[1], "hybrid": COLORS[2], "CoV gate": COLORS[3], "triple": COLORS[6]}
    plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED})
    data = {m: series(pres, m, r["paths"][m]) for m in names}
    start = data["LENGTH"][0][0]
    xmax = max(len(ys) for ys, _ in data.values())
    fig, axes = plt.subplots(len(names), 1, figsize=(7.5, 7.2), sharex=True, sharey=True)
    for ax, m in zip(axes, names):
        ys, special = data[m]
        ax.axhline(start, color=MUTED, lw=0.8, ls="--", zorder=1)
        ax.plot(range(len(ys)), ys, color=colors[m], lw=1.1, zorder=2)
        if m != "hybrid" and special:
            ax.scatter(special, [ys[i] for i in special], s=8, marker="o", color=INK, linewidth=0, zorder=3)
        ax.text(0.995, 0.92, f"{m}: {len(ys) - 1} steps, largest total length {max(ys)}", transform=ax.transAxes,
                ha="right", va="top", fontsize=8.5, color=INK,
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none"))
        ax.set_yscale("log")
        ax.set_ylim(1.6, 400)
        ax.set_yticks([2, 10, 25, 100])
        ax.set_yticklabels(["2", "10", "25", "100"])
        ax.minorticks_off()
        ax.set_xlim(-10, xmax + 10)
        ax.grid(True, color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[-1].set_xlabel("steps along the path (S-moves, CoV moves and Nielsen maps)")
    fig.supylabel("total relator length", fontsize=9, color=INK)
    fig.suptitle(r"MS640 presentation $\langle x,y \mid y^{-8}x^{-1}y^{7}x,\ y^{-3}x^{-1}y^{-1}xyx^{-1}\rangle$",
                 fontsize=10, color=INK)
    axes[0].legend([Line2D([], [], ls="--", color=MUTED, lw=0.8),
                    Line2D([], [], ls="", marker="o", color=INK, markersize=3.5)],
                   [f"starting total length ({start})", "CoV move"], frameon=False, fontsize=8, loc="upper left",
                   ncol=2, bbox_to_anchor=(0, 1.32))
    fig.tight_layout(h_pad=0.6)
    out = ROOT / "paper/figures/maxrel_example.png"
    fig.savefig(out, dpi=300)
    print(out)


if __name__ == "__main__":
    main()
