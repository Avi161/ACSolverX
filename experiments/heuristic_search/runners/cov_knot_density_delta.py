"""Length-normalized knot densities: original vs best-CoV starts.

Raw ``K`` / ``MK`` scale with length, so a lengthening CoV can look worse on
knots even when knot *density* falls. This diagnostic drops ``xyimb`` and
compares:

```text
K_den  = (k1 + k2) / L
MK_den = max(k1/|r1|, k2/|r2|)
```

on all 60 raw pairs, plus Aut-min forms for the 17 moved best-CoVs.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_knot_density_delta
"""
from __future__ import annotations

import csv
import os
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _repo_root(start=None):
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (experiments/ + data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.heuristic_search.core.hlab import word_stats  # noqa: E402

SOURCE = os.path.join(ROOT, "results/comparison/cov_heur_b1k_subset60.csv")
OUT_DIR = os.path.join(ROOT, "results/comparison")
FIG_DIR = os.path.join(OUT_DIR, "figures")
CSV_OUT = os.path.join(OUT_DIR, "cov_knot_density_delta_subset60.csv")
MD_OUT = os.path.join(OUT_DIR, "COV_KNOT_DENSITY.md")
FIG_OUT = os.path.join(FIG_DIR, "cov_knot_density_simple.png")

METRICS = ("L", "K", "MK", "K_den", "MK_den", "S")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
IMPROVED = "#2a78d6"
WORSENED = "#eb6834"
UNCHANGED = "#898781"

FIELDS = [
    "pres_id", "bin", "aut_class", "cov_class", "cov_z",
    "r1", "r2", "cov_r1", "cov_r2",
]
for m in METRICS:
    FIELDS.extend([f"{m}_orig", f"{m}_cov", f"d_{m}"])
FIELDS.extend([
    "mu_orig", "mu_cov", "same_aut_orbit",
])
for m in METRICS:
    FIELDS.extend([f"{m}_orig_autmin", f"{m}_cov_autmin", f"d_{m}_autmin"])


def _knot_feats(r1, r2):
    """L, K, MK, K_den, MK_den, S from the same knot definition as ``phi``."""
    n1, x1, y1, xr1, yr1, _nx1 = word_stats(r1)
    n2, x2, y2, xr2, yr2, _nx2 = word_stats(r2)
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)
    L = n1 + n2
    K = k1 + k2
    MK = max(k1, k2)
    K_den = (K / L) if L else 0.0
    dens = []
    if n1:
        dens.append(k1 / n1)
    if n2:
        dens.append(k2 / n2)
    MK_den = max(dens) if dens else 0.0

    xs, ys = xr1 + xr2, yr1 + yr2
    mx = sum(xs) / len(xs) if xs else 0.0
    my = sum(ys) / len(ys) if ys else 0.0
    if not xs or not ys:
        S = mx or my
    else:
        S = min(mx, my)

    return {
        "L": float(L),
        "K": float(K),
        "MK": float(MK),
        "K_den": float(K_den),
        "MK_den": float(MK_den),
        "S": float(S),
    }


def _style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#c3c2b7")
        spine.set_linewidth(0.8)
    ax.grid(True, color=GRID, linewidth=0.7, alpha=0.75)
    ax.set_axisbelow(True)


def _counts(rows, key):
    vals = [r[key] for r in rows]
    return (
        sum(1 for v in vals if v > 0),
        sum(1 for v in vals if v == 0),
        sum(1 for v in vals if v < 0),
        statistics.fmean(vals) if vals else 0.0,
    )


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60 rows, got {len(src)}")

    rows = []
    for s in src:
        fo = _knot_feats(s["r1"], s["r2"])
        fc = _knot_feats(s["cov_r1"], s["cov_r2"])
        row = {
            "pres_id": s["pres_id"],
            "bin": s["bin"],
            "aut_class": s["aut_class"],
            "cov_class": s["cov_class"],
            "cov_z": s["cov_z"],
            "r1": s["r1"],
            "r2": s["r2"],
            "cov_r1": s["cov_r1"],
            "cov_r2": s["cov_r2"],
            "mu_orig": "",
            "mu_cov": "",
            "same_aut_orbit": "",
        }
        for m in METRICS:
            row[f"{m}_orig"] = fo[m]
            row[f"{m}_cov"] = fc[m]
            row[f"d_{m}"] = fc[m] - fo[m]
            row[f"{m}_orig_autmin"] = ""
            row[f"{m}_cov_autmin"] = ""
            row[f"d_{m}_autmin"] = ""

        if s["cov_class"] == "moved":
            mu0, rep0, _ = aut_canon((s["r1"], s["r2"]))
            mu1, rep1, _ = aut_canon((s["cov_r1"], s["cov_r2"]))
            if rep0 == rep1:
                raise RuntimeError(
                    f"ms{s['pres_id']} marked moved but Aut-reps coincide")
            fa = _knot_feats(rep0[0], rep0[1])
            fb = _knot_feats(rep1[0], rep1[1])
            row["mu_orig"] = mu0
            row["mu_cov"] = mu1
            row["same_aut_orbit"] = False
            for m in METRICS:
                row[f"{m}_orig_autmin"] = fa[m]
                row[f"{m}_cov_autmin"] = fb[m]
                row[f"d_{m}_autmin"] = fb[m] - fa[m]

        rows.append(row)

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            out = dict(r)
            if out["same_aut_orbit"] is False:
                out["same_aut_orbit"] = "false"
            w.writerow({k: out[k] for k in FIELDS})
    print(f"wrote {CSV_OUT}")

    write_figure(rows)
    write_md(rows)
    return rows


def write_figure(rows):
    moved = [r for r in rows if r["cov_class"] == "moved"]
    # Two-row figure: raw-60 densities vs raw K/MK; Aut-min moved densities
    fig = plt.figure(figsize=(13.0, 10.2), facecolor=SURFACE)
    gs = fig.add_gridspec(
        3, 2, height_ratios=(1.2, 1.0, 1.0), hspace=0.55, wspace=0.30,
        top=0.90, bottom=0.06, left=0.08, right=0.98)
    ax0 = fig.add_subplot(gs[0, :])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])
    ax3 = fig.add_subplot(gs[2, 0])
    ax4 = fig.add_subplot(gs[2, 1])

    fig.suptitle(
        "Knot density vs raw knots — original vs best CoV (no xyimb)",
        x=0.08, ha="left", fontsize=15, color=INK, y=0.97)
    fig.text(
        0.08, 0.935,
        "K_den = (k1+k2)/L · MK_den = max(k_i/|ri|) · higher = denser = worse. "
        "Density removes length bias.",
        ha="left", color=SECONDARY, fontsize=10)

    # --- top: raw-60 higher/same/lower for K, MK, K_den, MK_den ---
    labels = ("K", "MK", "K_den", "MK_den")
    hi, sm, lo = [], [], []
    for m in labels:
        h, s, l, _ = _counts(rows, f"d_{m}")
        hi.append(h); sm.append(s); lo.append(l)
    x = np.arange(len(labels))
    hi_a, sm_a, lo_a = np.array(hi), np.array(sm), np.array(lo)
    ax0.bar(x, hi_a, color=WORSENED, width=0.62, label="higher after CoV (worse)")
    ax0.bar(x, sm_a, bottom=hi_a, color=UNCHANGED, width=0.62, label="same")
    ax0.bar(x, lo_a, bottom=hi_a + sm_a, color=IMPROVED, width=0.62,
            label="lower after CoV (better)")
    for i, (h, s, l) in enumerate(zip(hi, sm, lo)):
        ax0.text(i, 61.5, f"↑{h}", ha="center", va="bottom",
                 color=WORSENED, fontsize=10, fontweight="bold")
        ax0.text(i, 66.0, f"={s}  ↓{l}", ha="center", va="bottom",
                 color=SECONDARY, fontsize=9)
    ax0.set_ylim(0, 74)
    ax0.set_yticks([0, 20, 40, 60])
    ax0.set_xticks(x, labels)
    ax0.set_ylabel("count (of 60)", color=SECONDARY)
    ax0.set_title("Raw strings — score after best CoV vs original",
                  loc="left", fontsize=13, color=INK, pad=10)
    ax0.legend(frameon=False, loc="lower right", ncol=3, fontsize=9,
               bbox_to_anchor=(1.0, -0.28))
    _style_axis(ax0)
    ax0.grid(False, axis="x")

    def _mean_pair(ax, metrics, prefix_o, prefix_c, title, ylabel):
        xo = [statistics.fmean(r[f"{m}{prefix_o}"] for r in rows
                               if r[f"{m}{prefix_o}"] != "") for m in metrics]
        xc = [statistics.fmean(r[f"{m}{prefix_c}"] for r in rows
                               if r[f"{m}{prefix_c}"] != "") for m in metrics]
        # for autmin, only moved rows have values
        if prefix_o == "_orig_autmin":
            src = moved
            xo = [statistics.fmean(r[f"{m}_orig_autmin"] for r in src) for m in metrics]
            xc = [statistics.fmean(r[f"{m}_cov_autmin"] for r in src) for m in metrics]
        xx = np.arange(len(metrics))
        w = 0.36
        ax.bar(xx - w / 2, xo, width=w, color=MUTED, label="original")
        ax.bar(xx + w / 2, xc, width=w, color=WORSENED, label="best CoV")
        ymax = max(max(xo), max(xc), 1e-9)
        ax.set_ylim(0, ymax * 1.28)
        for i, (a, b) in enumerate(zip(xo, xc)):
            fmt = "{:.3f}" if ymax < 2 else "{:.2f}"
            ax.text(i - w / 2, a + 0.02 * ymax, fmt.format(a), ha="center",
                    va="bottom", color=SECONDARY, fontsize=8)
            ax.text(i + w / 2, b + 0.02 * ymax, fmt.format(b), ha="center",
                    va="bottom", color=INK, fontsize=8)
        ax.set_xticks(xx, metrics)
        ax.set_ylabel(ylabel, color=SECONDARY)
        ax.set_title(title, loc="left", fontsize=12, color=INK, pad=8)
        ax.legend(frameon=False, loc="upper right", fontsize=9)
        _style_axis(ax)
        ax.grid(False, axis="x")

    _mean_pair(ax1, ("K", "MK"), "_orig", "_cov",
               "Mean raw knots (length-biased)", "mean count")
    _mean_pair(ax2, ("K_den", "MK_den"), "_orig", "_cov",
               "Mean knot density (length-normalized)", "mean density")

    # Aut-min moved: counts + means for densities
    labels_m = ("K", "MK", "K_den", "MK_den")
    hi, sm, lo = [], [], []
    for m in labels_m:
        h, s, l, _ = _counts(moved, f"d_{m}_autmin")
        hi.append(h); sm.append(s); lo.append(l)
    x = np.arange(len(labels_m))
    n = len(moved)
    ax3.bar(x, hi, color=WORSENED, width=0.62, label="higher (worse)")
    ax3.bar(x, sm, bottom=hi, color=UNCHANGED, width=0.62, label="same")
    ax3.bar(x, lo, bottom=np.array(hi) + np.array(sm), color=IMPROVED,
            width=0.62, label="lower (better)")
    for i, (h, s, l) in enumerate(zip(hi, sm, lo)):
        ax3.text(i, n + 0.6, f"↑{h}", ha="center", va="bottom",
                 color=WORSENED, fontsize=10, fontweight="bold")
        ax3.text(i, n + 2.0, f"={s}  ↓{l}", ha="center", va="bottom",
                 color=SECONDARY, fontsize=9)
    ax3.set_ylim(0, n + 5)
    ax3.set_xticks(x, labels_m)
    ax3.set_ylabel(f"count (of {n} moved)", color=SECONDARY)
    ax3.set_title("Moved only — Aut-min score after CoV vs Aut-min original",
                  loc="left", fontsize=12, color=INK, pad=8)
    ax3.legend(frameon=False, loc="upper right", fontsize=8)
    _style_axis(ax3)
    ax3.grid(False, axis="x")

    _mean_pair(ax4, ("K_den", "MK_den"), "_orig_autmin", "_cov_autmin",
               f"Mean Aut-min density (moved n={n})", "mean density")

    fig.savefig(FIG_OUT, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {FIG_OUT}")


def write_md(rows):
    moved = [r for r in rows if r["cov_class"] == "moved"]
    n_moved = len(moved)
    lines = [
        "# Knot density vs best CoV (length-normalized, no xyimb)",
        "",
        "Raw `K` / `MK` grow with length, so a lengthening CoV can look worse "
        "on knots even when knots are *sparser*. This check drops `xyimb` and "
        "compares densities:",
        "",
        "```text",
        "K_den  = (k1 + k2) / L",
        "MK_den = max(k1/|r1|, k2/|r2|)",
        "```",
        "",
        "Higher density = denser knots = worse. "
        "`K` / `MK` are kept for contrast.",
        "",
        "![Knot density](figures/cov_knot_density_simple.png)",
        "",
        "## Raw strings (all 60)",
        "",
        "| metric | higher (worse) | same | lower (better) | mean orig | mean CoV | mean Δ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for m in ("K", "MK", "K_den", "MK_den", "L", "S"):
        h, s, l, mean_d = _counts(rows, f"d_{m}")
        mo = statistics.fmean(r[f"{m}_orig"] for r in rows)
        mc = statistics.fmean(r[f"{m}_cov"] for r in rows)
        lines.append(
            f"| {m} | {h} | {s} | {l} | {mo:.4g} | {mc:.4g} | {mean_d:+.4g} |"
        )

    lines.extend([
        "",
        "## Aut-min (moved only, "
        f"n={n_moved})",
        "",
        "| metric | higher (worse) | same | lower (better) | mean orig | mean CoV | mean Δ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for m in ("K", "MK", "K_den", "MK_den", "L", "S"):
        h, s, l, mean_d = _counts(moved, f"d_{m}_autmin")
        mo = statistics.fmean(r[f"{m}_orig_autmin"] for r in moved)
        mc = statistics.fmean(r[f"{m}_cov_autmin"] for r in moved)
        lines.append(
            f"| {m} | {h} | {s} | {l} | {mo:.4g} | {mc:.4g} | {mean_d:+.4g} |"
        )

    # Verdict hints
    raw_kden = _counts(rows, "d_K_den")
    am_kden = _counts(moved, "d_K_den_autmin")
    lines.extend([
        "",
        "## Verdict",
        "",
        f"On **raw** strings, `K_den` is higher (worse) on "
        f"**{raw_kden[0]}/60** and lower on **{raw_kden[2]}/60** "
        f"(mean Δ {raw_kden[3]:+.4f}). "
        f"Raw `K` mean Δ was "
        f"{_counts(rows, 'd_K')[3]:+.3f} — density removes most of that length inflation.",
        "",
        f"On **Aut-min moved** rows, `K_den` is higher on "
        f"**{am_kden[0]}/{n_moved}** and lower on **{am_kden[2]}/{n_moved}** "
        f"(mean Δ {am_kden[3]:+.4f}).",
        "",
        "## Source",
        "",
        "- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        "- Table: [`cov_knot_density_delta_subset60.csv`](cov_knot_density_delta_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/cov_knot_density_delta.py`",
        "",
    ])
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {MD_OUT}")


def main():
    run()


if __name__ == "__main__":
    main()
