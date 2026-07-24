"""Re-create `results/comparison/nodes_comparison_subset60.png` from its CSV.

**This is a re-creation, not the original producer.** The original figure was made
ad hoc (on Colab; no script for it was ever committed and matplotlib is not a
repo dependency), so cosmetic details — fonts, tick placement, exact marker
sizes — will differ from the superseded PNG. Every arm's *data* comes from
`nodes_comparison_subset60.csv` unchanged, and the row order in that file is the
figure's x-axis (bins 0→9, already sorted).

What actually changed: the best-CoV arm used to draw `ms622`–`ms625` and
`ms636`–`ms639` as hollow ✗ at the 10,000-node budget, and the lower-left panel
was captioned "only the 52 it solves". All eight solve at budget 20,000, so best
CoV is now 60/60 and those points are drawn ringed, at their real cost.

    .venv/bin/python3 -m experiments.stable_ac.cov.make_nodes_comparison_fig
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.lines import Line2D      # noqa: E402

CSV = "results/comparison/nodes_comparison_subset60.csv"
OUT = "results/comparison/nodes_comparison_subset60.png"
ESCAPED = {622, 623, 624, 625, 636, 637, 638, 639}

# (nodes column, solved column, label, colour, budget drawn at when unsolved)
ARMS = [
    ("nodes_bestcov_b20k", "solved_bestcov_b20k",
     "Best CoV (oracle z)  (≤20k, per-CoV cap)", "#8256d0", 20_000),
    ("nodes_greedy_b1M", "solved_greedy_b1M",
     "Greedy baseline  (1M, mrl24)", "#8a8a8a", 1_000_000),
    ("nodes_stdcov_b1M", "solved_stdcov_b1M",
     "Standard single-CoV GS  (1M)", "#1f77b4", 1_000_000),
    ("nodes_dualcov_b1M", "solved_dualcov_b1M",
     "Dual single-CoV gap10 covpref2  (1M)", "#2ca02c", 1_000_000),
    ("nodes_hsearch_base_b100k", "solved_hsearch_base_b100k",
     "H-search baseline arm  (100k, mrl48)", "#ff7f0e", 100_000),
    ("nodes_hsearch_reco_b100k", "solved_hsearch_reco_b100k",
     "H-search recommended arm  (100k, mrl48)", "#d62728", 100_000),
]
REF = 0  # best CoV is the reference arm for panel B


def _repo_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()


def load():
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, CSV)))
            if r["pres_id"].isdigit()]
    series = []
    for nk, sk, label, colour, budget in ARMS:
        vals, solved = [], []
        for r in rows:
            ok = r[sk] == "True" and r[nk]
            solved.append(bool(ok))
            vals.append(int(r[nk]) if ok else budget)
        series.append({"label": label, "colour": colour, "v": vals,
                       "ok": solved, "budget": budget})
    return rows, series


def main():
    rows, series = load()
    n = len(rows)
    x = list(range(n))
    ids = [int(r["pres_id"]) for r in rows]
    bins = [int(r["bin"]) for r in rows]

    fig = plt.figure(figsize=(20.5, 15.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.42, 1], hspace=0.30, wspace=0.34)
    ax = fig.add_subplot(gs[0, :])

    # bin bands
    for b in range(10):
        idx = [i for i, v in enumerate(bins) if v == b]
        if not idx:
            continue
        lo, hi = min(idx) - 0.5, max(idx) + 0.5
        if b % 2 == 0:
            ax.axvspan(lo, hi, color="#000000", alpha=0.035, lw=0)
        ax.text((lo + hi) / 2, 0.965, f"bin {b}", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=11, color="#8a8a8a")

    for k, s in enumerate(series):
        style = dict(color=s["colour"], lw=2.0)
        if k == REF:
            style.update(ls="--", lw=2.6)
        ax.plot(x, s["v"], **style, zorder=3 if k == REF else 2)
        sx = [i for i in x if s["ok"][i]]
        ax.plot(sx, [s["v"][i] for i in sx], ".", color=s["colour"], ms=9, zorder=4)
        ux = [i for i in x if not s["ok"][i]]
        if ux:
            ax.plot(ux, [s["v"][i] for i in ux], "x", color=s["colour"],
                    ms=11, mew=2.4, ls="none", zorder=4)
        # the eight the escalation moved out of the ✗ state
        if k == REF:
            ex = [i for i in x if ids[i] in ESCAPED]
            ax.plot(ex, [s["v"][i] for i in ex], "o", mfc="none", mec=s["colour"],
                    ms=17, mew=2.4, ls="none", zorder=5)

    ax.set_yscale("log")
    ax.set_ylabel("nodes explored  (log)", fontsize=13)
    ax.set_xlabel("presentation  (60-subset, ordered easy → hard by difficulty bin)", fontsize=13)
    ax.set_xticks(x[::2])
    ax.set_xticklabels([str(ids[i]) for i in x[::2]], rotation=90, fontsize=9)
    ax.set_xlim(-0.6, n - 0.4)
    ax.grid(axis="y", which="both", color="#e6e6e6", lw=0.7)
    ax.set_axisbelow(True)
    ax.set_title("Nodes explored per presentation — benchmark_subset_60   "
                 "(reference: best CoV, dashed purple)", fontsize=17, loc="left", pad=54)
    ax.legend([Line2D([], [], color=s["colour"], lw=2.4,
                      ls="--" if i == REF else "-") for i, s in enumerate(series)],
              [s["label"] for s in series], loc="lower left",
              bbox_to_anchor=(0, 1.012), ncol=3, frameon=False, fontsize=11.5)
    ax.text(0.995, 0.02, "hollow ✗ = did not solve, drawn at that run's node budget\n"
                         "ringed ○ = solved only once the CoV budget reached 20,000",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=11,
            bbox=dict(fc="white", ec="#cccccc", boxstyle="round,pad=0.42"))

    # ---- panel B: cost relative to best CoV --------------------------------
    axb = fig.add_subplot(gs[1, 0])
    ref = series[REF]
    both = [i for i in x if ref["ok"][i]]
    axb.axhline(1.0, color=ref["colour"], ls="--", lw=2)
    for k, s in enumerate(series):
        if k == REF:
            continue
        px = [i for i in both if s["ok"][i]]
        axb.plot(px, [s["v"][i] / ref["v"][i] for i in px], ".-",
                 color=s["colour"], lw=1.4, ms=8, label=s["label"])
    axb.set_yscale("log")
    axb.set_xlabel("presentation (easy → hard)", fontsize=12)
    axb.set_ylabel("nodes ÷ best-CoV nodes  (log)", fontsize=12)
    axb.set_title(f"Cost relative to best CoV   (all {len(both)} — the CoV arm now "
                  f"solves every row)", fontsize=15, loc="left")
    axb.grid(color="#ececec", lw=0.7)
    axb.set_axisbelow(True)
    axb.legend(fontsize=9.5, ncol=1, frameon=True, loc="upper left")
    axb.text(0.985, 0.045, "best CoV = 1", transform=axb.transAxes, ha="right",
             color=ref["colour"], fontsize=11)

    # ---- panel C: mean / median -------------------------------------------
    axc = fig.add_subplot(gs[1, 1])
    labels, means, medians, colours = [], [], [], []
    for s in series:
        sv = sorted(s["v"][i] for i in x if s["ok"][i])
        if not sv:
            continue
        labels.append(s["label"].replace("  (", "\n("))
        means.append(sum(sv) / len(sv))
        medians.append(sv[len(sv) // 2] if len(sv) % 2 else (sv[len(sv) // 2 - 1] + sv[len(sv) // 2]) / 2)
        colours.append(s["colour"])
    y = list(range(len(labels)))[::-1]
    axc.barh([v + 0.19 for v in y], means, height=0.36, color=colours)
    axc.barh([v - 0.19 for v in y], medians, height=0.36, color=colours,
             alpha=0.45, hatch="//", edgecolor="black")
    for v, m, md in zip(y, means, medians):
        axc.text(m * 1.06, v + 0.19, f"{m:,.0f}", va="center", fontsize=10.5)
        axc.text(md * 1.06, v - 0.19, f"{md:,.0f}", va="center", fontsize=10.5)
    axc.set_yticks(y)
    axc.set_yticklabels(labels, fontsize=10)
    axc.set_xscale("log")
    axc.set_xlim(4, 3e6)
    axc.set_xlabel("nodes explored (log) — solved presentations only", fontsize=12)
    axc.set_title("Mean / median nodes explored", fontsize=15, loc="left")
    axc.grid(axis="x", which="both", color="#ececec", lw=0.7)
    axc.set_axisbelow(True)
    axc.legend([Line2D([], [], color="#777", lw=9),
                Line2D([], [], color="#777", lw=9, alpha=0.45)],
               ["mean", "median"], loc="lower right", fontsize=10.5)

    dest = os.path.join(ROOT, OUT)
    fig.savefig(dest, dpi=100, bbox_inches="tight", facecolor="white")
    print(f"[fig] wrote {dest}")
    for s in series:
        print(f"       {s['label']:<46s} solved {sum(s['ok'])}/{n}")


if __name__ == "__main__":
    main()
