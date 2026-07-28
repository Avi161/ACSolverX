"""Score Aut-minimal forms of original vs moved best-CoV starts (60-row set).

For every shipped best-CoV that is **not** an Aut-relabel (``cov_class=moved``),
bring both the original pair and the CoV pair to their Whitehead / ``aut_canon``
representatives, then score both with the RECOMMENDED feature vector.

Relabels are skipped: after Aut-min they are the same orbit by construction.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_autmin_feature_delta
"""
from __future__ import annotations

import csv
import os
import shutil
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
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402

SOURCE = os.path.join(ROOT, "results/comparison/cov_heur_b1k_subset60.csv")
OUT_DIR = os.path.join(ROOT, "results/comparison")
FIG_DIR = os.path.join(OUT_DIR, "figures")
CSV_OUT = os.path.join(OUT_DIR, "cov_autmin_feature_delta_moved.csv")
MD_OUT = os.path.join(OUT_DIR, "COV_AUTMIN_FEATURE_DELTA.md")
FIG_OUT = os.path.join(FIG_DIR, "cov_autmin_feature_simple.png")

DIMS = ("L", "K", "MK", "S", "xyimb")
WEIGHTS = RECOMMENDED["segments"][0]["w"]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
IMPROVED = "#2a78d6"
WORSENED = "#eb6834"
UNCHANGED = "#898781"

FIELDS = [
    "pres_id", "bin", "aut_class", "cov_z", "cov_iso_gen", "cov_iso_index",
    "r1", "r2", "cov_r1", "cov_r2",
    "mu_orig", "autmin_r1", "autmin_r2",
    "mu_cov", "autmin_cov_r1", "autmin_cov_r2",
    "same_aut_orbit",
]
for d in DIMS:
    FIELDS.extend([f"{d}_orig_raw", f"{d}_cov_raw", f"d_{d}_raw",
                   f"{d}_orig_autmin", f"{d}_cov_autmin", f"d_{d}_autmin"])
FIELDS.extend([
    "prio_orig_raw", "prio_cov_raw", "d_prio_raw",
    "prio_orig_autmin", "prio_cov_autmin", "d_prio_autmin",
])


def _feats(r1, r2):
    v = phi(r1, r2)
    idx = {f: i for i, f in enumerate(FEATURES)}
    return {d: float(v[idx[d]]) for d in DIMS}


def _prio(feats):
    return sum(WEIGHTS[d] * feats[d] for d in DIMS)


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    moved = [r for r in src if r["cov_class"] == "moved"]
    if not moved:
        raise RuntimeError("no moved best-CoV rows")

    rows = []
    for i, s in enumerate(moved):
        fo_raw = _feats(s["r1"], s["r2"])
        fc_raw = _feats(s["cov_r1"], s["cov_r2"])
        mu0, rep0, _ = aut_canon((s["r1"], s["r2"]))
        mu1, rep1, _ = aut_canon((s["cov_r1"], s["cov_r2"]))
        if rep0 == rep1:
            raise RuntimeError(
                f"ms{s['pres_id']} marked moved but Aut-reps coincide: {rep0}")
        fo = _feats(rep0[0], rep0[1])
        fc = _feats(rep1[0], rep1[1])
        po_raw, pc_raw = _prio(fo_raw), _prio(fc_raw)
        po, pc = _prio(fo), _prio(fc)
        row = {
            "pres_id": s["pres_id"],
            "bin": s["bin"],
            "aut_class": s["aut_class"],
            "cov_z": s["cov_z"],
            "cov_iso_gen": s["cov_iso_gen"],
            "cov_iso_index": s["cov_iso_index"],
            "r1": s["r1"],
            "r2": s["r2"],
            "cov_r1": s["cov_r1"],
            "cov_r2": s["cov_r2"],
            "mu_orig": mu0,
            "autmin_r1": rep0[0],
            "autmin_r2": rep0[1],
            "mu_cov": mu1,
            "autmin_cov_r1": rep1[0],
            "autmin_cov_r2": rep1[1],
            "same_aut_orbit": False,
            "prio_orig_raw": po_raw,
            "prio_cov_raw": pc_raw,
            "d_prio_raw": pc_raw - po_raw,
            "prio_orig_autmin": po,
            "prio_cov_autmin": pc,
            "d_prio_autmin": pc - po,
        }
        for d in DIMS:
            row[f"{d}_orig_raw"] = fo_raw[d]
            row[f"{d}_cov_raw"] = fc_raw[d]
            row[f"d_{d}_raw"] = fc_raw[d] - fo_raw[d]
            row[f"{d}_orig_autmin"] = fo[d]
            row[f"{d}_cov_autmin"] = fc[d]
            row[f"d_{d}_autmin"] = fc[d] - fo[d]
        rows.append(row)
        print(f"  [{i+1}/{len(moved)}] ms{s['pres_id']}: "
              f"μ {mu0}→{mu1}  Δprio_raw={row['d_prio_raw']:+.1f}  "
              f"Δprio_autmin={row['d_prio_autmin']:+.1f}", flush=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {CSV_OUT}")

    write_figure(rows)
    write_md(rows)
    return rows


def _counts(rows, key):
    vals = [r[key] for r in rows]
    return (
        sum(1 for v in vals if v > 0),
        sum(1 for v in vals if v == 0),
        sum(1 for v in vals if v < 0),
        statistics.fmean(vals),
    )


def write_figure(rows):
    n = len(rows)
    labels = list(DIMS) + ["prio"]
    keys = [f"d_{d}_autmin" for d in DIMS] + ["d_prio_autmin"]
    mean_o_keys = [f"{d}_orig_autmin" for d in DIMS] + ["prio_orig_autmin"]
    mean_c_keys = [f"{d}_cov_autmin" for d in DIMS] + ["prio_cov_autmin"]

    hi, sm, lo = [], [], []
    mean_o, mean_c = [], []
    for k, ko, kc in zip(keys, mean_o_keys, mean_c_keys):
        h, s, l, _ = _counts(rows, k)
        hi.append(h); sm.append(s); lo.append(l)
        mean_o.append(statistics.fmean(r[ko] for r in rows))
        mean_c.append(statistics.fmean(r[kc] for r in rows))

    fig = plt.figure(figsize=(12.8, 8.6), facecolor=SURFACE)
    gs = fig.add_gridspec(
        2, 2, height_ratios=(1.15, 1.0), hspace=0.55, wspace=0.30,
        top=0.88, bottom=0.08, left=0.08, right=0.98)
    ax0 = fig.add_subplot(gs[0, :])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])

    fig.suptitle(
        f"Moved best-CoV only (n={n}) — scored on Aut-minimal representatives",
        x=0.08, ha="left", fontsize=15, color=INK, y=0.97)
    fig.text(
        0.08, 0.925,
        "Both original and CoV brought to Whitehead / aut_canon min. "
        "Higher score = worse for RECOMMENDED (min-heap).",
        ha="left", color=SECONDARY, fontsize=10)

    x = np.arange(len(labels))
    disp = [d if d != "prio" else "weighted\npriority" for d in labels]
    hi_a, sm_a, lo_a = np.array(hi), np.array(sm), np.array(lo)
    ax0.bar(x, hi_a, color=WORSENED, width=0.62, label="higher after CoV (worse)")
    ax0.bar(x, sm_a, bottom=hi_a, color=UNCHANGED, width=0.62, label="same")
    ax0.bar(x, lo_a, bottom=hi_a + sm_a, color=IMPROVED, width=0.62,
            label="lower after CoV (better)")
    for i, (h, s, l) in enumerate(zip(hi, sm, lo)):
        ax0.text(i, n + 1.2, f"↑{h}", ha="center", va="bottom",
                 color=WORSENED, fontsize=10, fontweight="bold")
        ax0.text(i, n + 3.8, f"={s}  ↓{l}", ha="center", va="bottom",
                 color=SECONDARY, fontsize=9)
    ax0.set_ylim(0, n + 8)
    ax0.set_yticks(list(range(0, n + 1, max(1, n // 4))))
    ax0.set_xticks(x, disp)
    ax0.set_ylabel(f"count (of {n})", color=SECONDARY)
    ax0.set_title("Aut-min score after moved best CoV vs Aut-min original",
                  loc="left", fontsize=13, color=INK, pad=10)
    ax0.legend(frameon=False, loc="lower right", ncol=3, fontsize=9,
               bbox_to_anchor=(1.0, -0.22))
    ax0.set_facecolor(SURFACE)
    ax0.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax0.spines.values():
        spine.set_color("#c3c2b7"); spine.set_linewidth(0.8)
    ax0.grid(True, color=GRID, linewidth=0.7, alpha=0.75); ax0.set_axisbelow(True)
    ax0.grid(False, axis="x")

    # means for features only on left; prio on right
    xf = np.arange(len(DIMS))
    w = 0.36
    mo = mean_o[:-1]; mc = mean_c[:-1]
    ax1.bar(xf - w / 2, mo, width=w, color=MUTED, label="orig Aut-min")
    ax1.bar(xf + w / 2, mc, width=w, color=WORSENED, label="CoV Aut-min")
    ymax = max(max(mo), max(mc), 1e-9)
    ax1.set_ylim(0, ymax * 1.25)
    for i, (a, b) in enumerate(zip(mo, mc)):
        ax1.text(i - w / 2, a + 0.02 * ymax, f"{a:.2f}", ha="center",
                 va="bottom", color=SECONDARY, fontsize=8)
        ax1.text(i + w / 2, b + 0.02 * ymax, f"{b:.2f}", ha="center",
                 va="bottom", color=INK, fontsize=8)
    ax1.set_xticks(xf, list(DIMS))
    ax1.set_ylabel("mean feature value", color=SECONDARY)
    ax1.set_title("Mean Aut-min features", loc="left", fontsize=13, color=INK, pad=10)
    ax1.legend(frameon=False, loc="upper right")
    ax1.set_facecolor(SURFACE)
    ax1.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#c3c2b7"); spine.set_linewidth(0.8)
    ax1.grid(True, color=GRID, linewidth=0.7, alpha=0.75)
    ax1.set_axisbelow(True)
    ax1.grid(False, axis="x")

    po, pc = mean_o[-1], mean_c[-1]
    ax2.bar([-0.22], [po], width=0.38, color=MUTED)
    ax2.bar([0.22], [pc], width=0.38, color=WORSENED)
    pmax = max(po, pc, 1e-9)
    ax2.set_ylim(0, pmax * 1.28)
    ax2.text(-0.22, po + 0.02 * pmax, f"{po:.1f}", ha="center", va="bottom",
             color=SECONDARY, fontsize=12, fontweight="bold")
    ax2.text(0.22, pc + 0.02 * pmax, f"{pc:.1f}", ha="center", va="bottom",
             color=INK, fontsize=12, fontweight="bold")
    ax2.set_xticks([-0.22, 0.22], ["orig Aut-min", "CoV Aut-min"])
    ax2.set_xlim(-0.75, 0.75)
    ax2.set_ylabel("mean weighted priority", color=SECONDARY)
    ax2.set_title(f"Mean RECOMMENDED score on Aut-min   (Δ {pc - po:+.1f})",
                  loc="left", fontsize=13, color=INK, pad=10)
    ax2.set_facecolor(SURFACE)
    ax2.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#c3c2b7"); spine.set_linewidth(0.8)
    ax2.grid(True, color=GRID, linewidth=0.7, alpha=0.75)
    ax2.set_axisbelow(True); ax2.grid(False, axis="x")

    fig.savefig(FIG_OUT, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {FIG_OUT}")


def write_md(rows):
    n = len(rows)
    lines = [
        "# Moved best-CoV scored on Aut-minimal representatives",
        "",
        f"Of the 60 shipped best-CoV starts, **{n} are moved** "
        f"(not Aut-relabels). For each, both the original and the CoV pair are "
        "reduced with Whitehead / `aut_canon`, then scored with RECOMMENDED "
        "features. Relabels are omitted — after Aut-min they are the same orbit.",
        "",
        "```text",
        "prio = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb   # lower better",
        "```",
        "",
        f"![Aut-min feature view](figures/cov_autmin_feature_simple.png)",
        "",
        "## Counts on Aut-min (of "
        f"{n})",
        "",
        "| feature | higher (worse) | same | lower (better) | mean Δ |",
        "|---|---:|---:|---:|---:|",
    ]
    for d in list(DIMS) + ["prio"]:
        key = f"d_{d}_autmin" if d != "prio" else "d_prio_autmin"
        h, s, l, mean = _counts(rows, key)
        lines.append(f"| {d} | {h} | {s} | {l} | {mean:+.3f} |")

    # raw vs autmin contrast for prio
    raw_h, _, raw_l, raw_m = _counts(rows, "d_prio_raw")
    am_h, _, am_l, am_m = _counts(rows, "d_prio_autmin")
    lines.extend([
        "",
        "## Raw strings vs Aut-min (weighted priority)",
        "",
        f"| view | higher (worse) | lower (better) | mean Δprio |",
        f"|---|---:|---:|---:|",
        f"| raw CoV string vs raw original | {raw_h}/{n} | {raw_l}/{n} | {raw_m:+.2f} |",
        f"| Aut-min CoV vs Aut-min original | {am_h}/{n} | {am_l}/{n} | {am_m:+.2f} |",
        "",
        "## Per-row Aut-min snapshot",
        "",
        "| pres | μ_orig | μ_cov | ΔL | ΔK | ΔMK | Δprio_raw | Δprio_autmin |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for r in sorted(rows, key=lambda x: int(x["pres_id"])):
        lines.append(
            f"| ms{r['pres_id']} | {r['mu_orig']} | {r['mu_cov']} | "
            f"{r['d_L_autmin']:+.0f} | {r['d_K_autmin']:+.0f} | "
            f"{r['d_MK_autmin']:+.0f} | {r['d_prio_raw']:+.1f} | "
            f"{r['d_prio_autmin']:+.1f} |"
        )
    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv) "
        f"(moved rows only)",
        f"- Table: [`cov_autmin_feature_delta_moved.csv`]"
        f"(cov_autmin_feature_delta_moved.csv)",
        "- Runner: `experiments/heuristic_search/runners/cov_autmin_feature_delta.py`",
        "",
    ])
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {MD_OUT}")


def main():
    run()


if __name__ == "__main__":
    main()
