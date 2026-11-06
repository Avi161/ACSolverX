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
    names = ["LENGTH", "S20_MK2", "hybrid", "CoV gate", "dual, single CoV", "dual, auto CoV", "triple"]
    plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED})
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1, 1]})
    data = {m: series(pres, m, r["paths"][m]) for m in names}
    # the hybrid is drawn along its AC path: every Nielsen map rewritten as elementary AC moves
    st = replay(pres, unpack(r["paths"]["hybrid"]["elementary"]), cyclic=False, normalize=False)
    hy = [total(s.rels) for s in st]
    others = [m for m in names if m != "hybrid"]
    # (a) all seven methods on one scale
    for c, m in zip(COLORS, names):
        ys = hy if m == "hybrid" else data[m][0]
        a.plot(range(len(ys)), ys, color=c, lw=1.4, label=m, zorder=3 if m == "hybrid" else 2)
    mx = max(range(len(hy)), key=hy.__getitem__)
    a.annotate(f"hybrid: total length {hy[mx]}, longest relator "
               f"{max(len(reduce(tuple(w))) for w in st[mx].rels)}", (mx, hy[mx]), xytext=(-6, -2),
               textcoords="offset points", ha="right", fontsize=7.5, color=INK)
    a.set_xlabel("moves along the path (elementary AC moves for the hybrid)")
    a.set_ylabel("total relator length")
    a.set_title("(a) all seven methods", loc="left", fontsize=9, color=INK)
    a.legend(frameon=False, fontsize=7.5, loc="upper left")
    # (b) the six other methods, enlarged, with the CoV moves marked
    top = 0
    for c, m in zip(COLORS, names):
        if m == "hybrid":
            continue
        ys, special = data[m]
        top = max(top, max(ys))
        b.plot(range(len(ys)), ys, color=c, lw=1.2, zorder=2)
        if special:
            b.scatter(special, [ys[i] for i in special], s=7, marker="o", color=INK, linewidth=0, zorder=3)
    b.legend([Line2D([], [], ls="", marker="o", color=INK, markersize=3.5)], ["CoV move"],
             frameon=False, fontsize=7.5, loc="upper right")
    b.set_ylim(0, top * 1.25)
    b.set_xlabel("moves along the path (S-moves and CoV moves)")
    b.set_title("(b) the six other methods, enlarged", loc="left", fontsize=9, color=INK)
    for ax in (a, b):
        ax.grid(True, color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    out = ROOT / "paper/figures/maxrel_example.png"
    fig.savefig(out, dpi=300)
    print(out)


if __name__ == "__main__":
    main()
