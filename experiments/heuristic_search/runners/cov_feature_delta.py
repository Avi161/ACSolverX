"""Score original vs best-CoV starts on RECOMMENDED features (no search).

For each of the 60 subset rows, compute ``phi`` on ``(r1, r2)`` and on
``(cov_r1, cov_r2)``, emit per-feature before/after/Δ for the five RECOMMENDED
axes, the weighted min-heap priority, four diagnostic PNGs, and a short note.

Lower priority is better (min-heap). Every RECOMMENDED weight is positive, so
Δ < 0 on a feature is an improvement for the heuristic.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_feature_delta
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

from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402

SOURCE = os.path.join(ROOT, "results/comparison/cov_heur_b1k_subset60.csv")
OUT_DIR = os.path.join(ROOT, "results/comparison")
FIG_DIR = os.path.join(OUT_DIR, "figures")
CSV_OUT = os.path.join(OUT_DIR, "cov_feature_delta_subset60.csv")
MD_OUT = os.path.join(OUT_DIR, "COV_FEATURE_DELTA.md")

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
GAIN = "#2a78d6"
ALREADY = "#898781"
STILL = "#eb6834"

ROW_FIELDS = [
    "pres_id", "bin", "aut_class", "start_length",
    "r1", "r2", "cov_r1", "cov_r2", "cov_z",
    "b1k_greedy_solved", "b1k_covgreedy_solved", "cov_helped_b1k", "outcome",
]
for d in DIMS:
    ROW_FIELDS.extend([f"{d}_orig", f"{d}_cov", f"d_{d}"])
ROW_FIELDS.extend(["prio_orig", "prio_cov", "d_prio"])


def _bool(v):
    return str(v).strip().lower() in ("1", "true", "yes")


def _feat_map(r1, r2):
    v = phi(r1, r2)
    idx = {f: i for i, f in enumerate(FEATURES)}
    return {d: float(v[idx[d]]) for d in DIMS}


def _prio(feats):
    return sum(WEIGHTS[d] * feats[d] for d in DIMS)


def _outcome(greedy_solved, cov_solved):
    if cov_solved and not greedy_solved:
        return "gain"
    if greedy_solved:
        return "already_solved"
    return "still_unsolved"


def load_and_score():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60 rows, got {len(src)}")

    rows = []
    for r in src:
        fo = _feat_map(r["r1"], r["r2"])
        fc = _feat_map(r["cov_r1"], r["cov_r2"])
        g_sol = _bool(r["b1k_greedy_solved"])
        c_sol = _bool(r["b1k_covgreedy_solved"])
        helped = c_sol and not g_sol
        po, pc = _prio(fo), _prio(fc)
        out = {
            "pres_id": r["pres_id"],
            "bin": r["bin"],
            "aut_class": r["aut_class"],
            "start_length": r["start_length"],
            "r1": r["r1"],
            "r2": r["r2"],
            "cov_r1": r["cov_r1"],
            "cov_r2": r["cov_r2"],
            "cov_z": r["cov_z"],
            "b1k_greedy_solved": g_sol,
            "b1k_covgreedy_solved": c_sol,
            "cov_helped_b1k": helped,
            "outcome": _outcome(g_sol, c_sol),
            "prio_orig": po,
            "prio_cov": pc,
            "d_prio": pc - po,
        }
        for d in DIMS:
            out[f"{d}_orig"] = fo[d]
            out[f"{d}_cov"] = fc[d]
            out[f"d_{d}"] = fc[d] - fo[d]
        rows.append(out)
    return rows


def _delta_stats(rows, key):
    vals = [r[key] for r in rows]
    n = len(vals)
    n_imp = sum(1 for v in vals if v < 0)
    n_same = sum(1 for v in vals if v == 0)
    n_wors = sum(1 for v in vals if v > 0)
    return {
        "n": n,
        "n_improved": n_imp,
        "n_unchanged": n_same,
        "n_worsened": n_wors,
        "frac_improved": n_imp / n,
        "mean": statistics.fmean(vals),
        "median": statistics.median(vals),
    }


def summarize(rows):
    summary = {d: _delta_stats(rows, f"d_{d}") for d in DIMS}
    summary["prio"] = _delta_stats(rows, "d_prio")
    helped = [r for r in rows if r["cov_helped_b1k"]]
    other = [r for r in rows if not r["cov_helped_b1k"]]
    summary["n_helped"] = len(helped)
    summary["n_other"] = len(other)
    summary["helped"] = {d: _delta_stats(helped, f"d_{d}") for d in DIMS} if helped else {}
    summary["other"] = {d: _delta_stats(other, f"d_{d}") for d in DIMS} if other else {}
    if helped:
        summary["helped"]["prio"] = _delta_stats(helped, "d_prio")
    if other:
        summary["other"]["prio"] = _delta_stats(other, "d_prio")
    # Does lower Δprio associate with CoV unlocks?
    prio_drop = [r for r in rows if r["d_prio"] < 0]
    prio_rise = [r for r in rows if r["d_prio"] > 0]
    summary["among_prio_drop_helped"] = (
        sum(1 for r in prio_drop if r["cov_helped_b1k"]) / len(prio_drop)
        if prio_drop else None)
    summary["among_prio_rise_helped"] = (
        sum(1 for r in prio_rise if r["cov_helped_b1k"]) / len(prio_rise)
        if prio_rise else None)
    summary["n_prio_drop"] = len(prio_drop)
    summary["n_prio_rise"] = len(prio_rise)
    summary["n_prio_same"] = sum(1 for r in rows if r["d_prio"] == 0)
    return summary


def write_csv(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ROW_FIELDS)
        w.writeheader()
        for r in rows:
            row = dict(r)
            for k in ("b1k_greedy_solved", "b1k_covgreedy_solved", "cov_helped_b1k"):
                row[k] = "true" if r[k] else "false"
            w.writerow({k: row[k] for k in ROW_FIELDS})
    print(f"wrote {CSV_OUT}")


def _style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=SECONDARY, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#c3c2b7")
        spine.set_linewidth(0.8)
    ax.grid(True, color=GRID, linewidth=0.7, alpha=0.75)
    ax.set_axisbelow(True)


def fig_before_after(rows):
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 8.2), facecolor=SURFACE)
    axes = axes.ravel()
    for i, d in enumerate(DIMS):
        ax = axes[i]
        xo = [r[f"{d}_orig"] for r in rows]
        yc = [r[f"{d}_cov"] for r in rows]
        n_imp = sum(1 for a, b in zip(xo, yc) if b < a)
        lo = min(min(xo), min(yc))
        hi = max(max(xo), max(yc))
        pad = (hi - lo) * 0.08 if hi > lo else 0.5
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color=MUTED,
                linewidth=1.0, linestyle="--", zorder=1)
        colors = [IMPROVED if b < a else (UNCHANGED if b == a else WORSENED)
                  for a, b in zip(xo, yc)]
        ax.scatter(xo, yc, c=colors, s=36, alpha=0.88, edgecolors=SURFACE,
                   linewidths=0.8, zorder=2)
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(f"{d} original", color=SECONDARY)
        ax.set_ylabel(f"{d} after CoV", color=SECONDARY)
        ax.set_title(f"{d}: {n_imp}/60 improved (Δ<0)", loc="left",
                     fontsize=11, color=INK, pad=8)
        _style_axis(ax)
    axes[5].axis("off")
    axes[5].text(
        0.05, 0.55,
        "Below the diagonal = lower after CoV\n"
        "(better for RECOMMENDED min-heap).\n\n"
        f"Blue = improved   Grey = same\nOrange = worsened",
        transform=axes[5].transAxes, color=SECONDARY, fontsize=11,
        va="center")
    fig.suptitle("Original vs best-CoV feature values (RECOMMENDED axes)",
                 x=0.01, ha="left", fontsize=15, color=INK, y=0.98)
    fig.tight_layout(rect=(0, 0.02, 1, 0.94))
    path = os.path.join(FIG_DIR, "cov_feature_before_after.png")
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def fig_delta_bars(rows, summary):
    fig, ax = plt.subplots(figsize=(9.5, 5.2), facecolor=SURFACE)
    labels = list(DIMS) + ["prio"]
    imp = [summary[d if d != "prio" else "prio"]["n_improved"] for d in labels]
    same = [summary[d if d != "prio" else "prio"]["n_unchanged"] for d in labels]
    wors = [summary[d if d != "prio" else "prio"]["n_worsened"] for d in labels]
    x = np.arange(len(labels))
    ax.bar(x, imp, color=IMPROVED, label="improved (Δ<0)", width=0.65)
    ax.bar(x, same, bottom=imp, color=UNCHANGED, label="unchanged", width=0.65)
    ax.bar(x, wors, bottom=np.array(imp) + np.array(same), color=WORSENED,
           label="worsened (Δ>0)", width=0.65)
    for i, (a, b, c) in enumerate(zip(imp, same, wors)):
        total = a + b + c
        if a:
            ax.text(i, a / 2, str(a), ha="center", va="center", color="white",
                    fontsize=10, fontweight="bold")
        if c:
            ax.text(i, a + b + c / 2, str(c), ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
        ax.text(i, total + 1.2, f"{a}/60", ha="center", va="bottom",
                color=SECONDARY, fontsize=9)
    ax.set_xticks(x, [d if d != "prio" else "weighted\npriority" for d in labels])
    ax.set_ylim(0, 68)
    ax.set_ylabel("presentations (of 60)", color=SECONDARY)
    ax.set_title("Does best-CoV move each RECOMMENDED axis the right way?",
                 loc="left", fontsize=14, color=INK, pad=12)
    ax.legend(frameon=False, loc="upper right")
    _style_axis(ax)
    ax.grid(False, axis="x")
    path = os.path.join(FIG_DIR, "cov_feature_delta_bars.png")
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def fig_priority_scatter(rows):
    fig, ax = plt.subplots(figsize=(8.2, 7.0), facecolor=SURFACE)
    style = {
        "gain": {"c": GAIN, "label": "CoV unlock at b1k (greedy missed)", "z": 3},
        "already_solved": {"c": ALREADY, "label": "greedy already solved at b1k", "z": 2},
        "still_unsolved": {"c": STILL, "label": "still unsolved under CoV at b1k", "z": 3},
    }
    xo = [r["prio_orig"] for r in rows]
    yc = [r["prio_cov"] for r in rows]
    lo = min(min(xo), min(yc))
    hi = max(max(xo), max(yc))
    pad = (hi - lo) * 0.06
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color=MUTED,
            linewidth=1.1, linestyle="--", zorder=1)
    for outcome, st in style.items():
        pts = [r for r in rows if r["outcome"] == outcome]
        if not pts:
            continue
        ax.scatter([r["prio_orig"] for r in pts],
                   [r["prio_cov"] for r in pts],
                   c=st["c"], s=48, alpha=0.9, edgecolors=SURFACE,
                   linewidths=0.9, label=f"{st['label']} (n={len(pts)})",
                   zorder=st["z"])
    n_drop = sum(1 for r in rows if r["d_prio"] < 0)
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("RECOMMENDED priority — original", color=SECONDARY)
    ax.set_ylabel("RECOMMENDED priority — after best CoV", color=SECONDARY)
    ax.set_title(
        f"Weighted priority before vs after CoV  ({n_drop}/60 lower after = better)",
        loc="left", fontsize=13, color=INK, pad=10)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    _style_axis(ax)
    path = os.path.join(FIG_DIR, "cov_priority_scatter.png")
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def fig_simple_higher_and_means(rows):
    """Simple view: how many of 60 got higher after CoV, and mean orig vs mean CoV."""
    feat_labels = list(DIMS)
    all_labels = feat_labels + ["prio"]

    def series(d):
        if d == "prio":
            okey, ckey = "prio_orig", "prio_cov"
        else:
            okey, ckey = f"{d}_orig", f"{d}_cov"
        orig = [float(r[okey]) for r in rows]
        covv = [float(r[ckey]) for r in rows]
        return orig, covv

    n_higher, n_lower, n_same = [], [], []
    mean_orig_f, mean_cov_f = [], []
    for d in all_labels:
        orig, covv = series(d)
        n_higher.append(sum(1 for a, b in zip(orig, covv) if b > a))
        n_lower.append(sum(1 for a, b in zip(orig, covv) if b < a))
        n_same.append(sum(1 for a, b in zip(orig, covv) if b == a))
    for d in feat_labels:
        orig, covv = series(d)
        mean_orig_f.append(statistics.fmean(orig))
        mean_cov_f.append(statistics.fmean(covv))
    po, pc = series("prio")
    mean_prio_orig = statistics.fmean(po)
    mean_prio_cov = statistics.fmean(pc)

    fig = plt.figure(figsize=(13.2, 8.0), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=(1.05, 1.0), hspace=0.42, wspace=0.28)
    ax0 = fig.add_subplot(gs[0, :])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])

    # --- top: how many higher after CoV ---
    x_all = np.arange(len(all_labels))
    disp_all = [d if d != "prio" else "weighted priority" for d in all_labels]
    ax0.bar(x_all, n_higher, color=WORSENED, width=0.62)
    ax0.axhline(30, color=MUTED, linewidth=0.9, linestyle=":", zorder=1)
    for i, (hi, lo, sm) in enumerate(zip(n_higher, n_lower, n_same)):
        ax0.text(i, hi + 1.0, f"{hi}/60", ha="center", va="bottom",
                 color=INK, fontsize=11, fontweight="bold")
        ax0.text(i, -0.8, f"lower {lo} · same {sm}", ha="center", va="top",
                 color=SECONDARY, fontsize=8)
    ax0.set_ylim(-8, 68)
    ax0.set_xticks(x_all, disp_all)
    ax0.set_ylabel("presentations (of 60)", color=SECONDARY)
    ax0.set_title(
        "Of the 60 presentations, how many had a HIGHER score after best CoV?",
        loc="left", fontsize=14, color=INK, pad=8)
    ax0.text(
        0.0, 1.02,
        "All RECOMMENDED weights are positive → higher score = worse for the heuristic (min-heap)",
        transform=ax0.transAxes, color=SECONDARY, fontsize=10, va="bottom")
    _style_axis(ax0)
    ax0.grid(False, axis="x")

    # --- bottom left: mean feature values ---
    x_f = np.arange(len(feat_labels))
    w = 0.36
    ax1.bar(x_f - w / 2, mean_orig_f, width=w, color=MUTED, label="original")
    ax1.bar(x_f + w / 2, mean_cov_f, width=w, color=WORSENED, label="best CoV")
    for i, (mo, mc) in enumerate(zip(mean_orig_f, mean_cov_f)):
        ax1.text(i - w / 2, mo, f"{mo:.2f}", ha="center", va="bottom",
                 color=SECONDARY, fontsize=8)
        ax1.text(i + w / 2, mc, f"{mc:.2f}", ha="center", va="bottom",
                 color=INK, fontsize=8)
    ax1.set_xticks(x_f, feat_labels)
    ax1.set_ylabel("mean feature value", color=SECONDARY)
    ax1.set_title("Mean feature: original vs best-CoV",
                  loc="left", fontsize=13, color=INK, pad=8)
    ax1.legend(frameon=False, loc="upper right")
    _style_axis(ax1)
    ax1.grid(False, axis="x")

    # --- bottom right: mean weighted priority alone ---
    ax2.bar([-0.2], [mean_prio_orig], width=0.35, color=MUTED, label="original")
    ax2.bar([0.2], [mean_prio_cov], width=0.35, color=WORSENED, label="best CoV")
    ax2.text(-0.2, mean_prio_orig, f"{mean_prio_orig:.1f}", ha="center",
             va="bottom", color=SECONDARY, fontsize=12, fontweight="bold")
    ax2.text(0.2, mean_prio_cov, f"{mean_prio_cov:.1f}", ha="center",
             va="bottom", color=INK, fontsize=12, fontweight="bold")
    ax2.set_xticks([-0.2, 0.2], ["original", "best CoV"])
    ax2.set_xlim(-0.7, 0.7)
    ax2.set_ylabel("mean weighted priority", color=SECONDARY)
    ax2.set_title("Mean RECOMMENDED score (prio)",
                  loc="left", fontsize=13, color=INK, pad=8)
    ax2.text(
        0.5, 0.92,
        f"original {mean_prio_orig:.1f}  →  CoV {mean_prio_cov:.1f}"
        f"  (Δ {mean_prio_cov - mean_prio_orig:+.1f})",
        transform=ax2.transAxes, ha="center", va="top",
        color=SECONDARY, fontsize=10)
    _style_axis(ax2)
    ax2.grid(False, axis="x")

    fig.suptitle(
        "Original presentation vs best-CoV presentation — 60 benchmark rows",
        x=0.01, ha="left", fontsize=15, color=INK, y=0.995)
    path = os.path.join(FIG_DIR, "cov_feature_simple.png")
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")
    # Replace the old confusing outcome graph with this simple one
    path2 = os.path.join(FIG_DIR, "cov_delta_by_outcome.png")
    shutil.copyfile(path, path2)
    print(f"wrote {path2} (same simple figure)")


def write_figures(rows, summary):
    os.makedirs(FIG_DIR, exist_ok=True)
    fig_simple_higher_and_means(rows)
    fig_before_after(rows)
    fig_delta_bars(rows, summary)
    fig_priority_scatter(rows)


def _pct(frac):
    return f"{100 * frac:.0f}%"


def _line_stats(name, st):
    return (f"- **{name}**: {_pct(st['frac_improved'])} improved "
            f"({st['n_improved']}/60), unchanged {st['n_unchanged']}, "
            f"worsened {st['n_worsened']}; "
            f"mean Δ = {st['mean']:+.3f}, median Δ = {st['median']:+.3f}")


def write_md(rows, summary):
    n_helped = summary["n_helped"]
    prio = summary["prio"]
    lines = [
        "# CoV vs RECOMMENDED feature alignment",
        "",
        "Diagnostic only: for each of the 60 benchmark presentations, score the "
        "original pair and its oracle best-CoV transform with the five features in "
        "`RECOMMENDED`, then ask whether CoV moves those features the way the "
        "heuristic prefers. **No search** — only `phi` on the two starts.",
        "",
        "## Interpretation",
        "",
        "`RECOMMENDED` is a min-heap priority",
        "",
        "```text",
        "prio = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb",
        "```",
        "",
        "Lower is better. Every weight is positive, so **Δ < 0** on a feature "
        "(or on `prio`) is an improvement for the heuristic.",
        "",
        "Caveat: the oracle `z` was selected by **length-only** cost at ≤20,000 "
        "nodes, not by RECOMMENDED. This checks feature *alignment*, not CoV "
        "selection under the tuned ordering.",
        "",
        "## Headline",
        "",
    ]
    for d in DIMS:
        lines.append(_line_stats(d, summary[d]))
    lines.append(_line_stats("weighted priority", prio))
    lines.extend([
        "",
        f"At budget 1,000 with length-only ordering, best-CoV unlocks "
        f"**{n_helped}** presentations that plain greedy misses "
        f"(`b1k_covgreedy` vs `b1k_greedy`).",
        "",
        f"Priority drops on **{summary['n_prio_drop']}/60** rows and rises on "
        f"**{summary['n_prio_rise']}/60**"
        + (f" (same on {summary['n_prio_same']})"
           if summary["n_prio_same"] else "")
        + ".",
        "",
    ])
    if summary["among_prio_drop_helped"] is not None:
        lines.append(
            f"Among rows where priority **falls**, "
            f"{_pct(summary['among_prio_drop_helped'])} are CoV unlocks "
            f"({sum(1 for r in rows if r['d_prio'] < 0 and r['cov_helped_b1k'])}"
            f"/{summary['n_prio_drop']}).")
    if summary["among_prio_rise_helped"] is not None:
        lines.append(
            f"Among rows where priority **rises**, "
            f"{_pct(summary['among_prio_rise_helped'])} are CoV unlocks "
            f"({sum(1 for r in rows if r['d_prio'] > 0 and r['cov_helped_b1k'])}"
            f"/{summary['n_prio_rise']}).")
    lines.extend([
        "",
        "## Simple picture",
        "",
        "For each RECOMMENDED axis (and the weighted priority), count how many of "
        "the 60 presentations got a **higher** score after best CoV, and compare "
        "the **mean on the original** vs the **mean on the best-CoV** start. "
        "Higher = worse for the heuristic (all weights positive, min-heap).",
        "",
        "![Simple: higher counts + means](figures/cov_feature_simple.png)",
        "",
        "## Verdict",
        "",
        "**Best CoV does not win by improving the RECOMMENDED feature axes.** "
        "L rises on 47/60 rows; K and MK usually stay put or rise; xyimb worsens "
        "on 42/60; the weighted priority rises on 45/60 (mean Δprio ≈ +12.7). "
        "Only S tilts the helpful way more often than not (19 improved vs 7 worsened), "
        "and the effect is tiny.",
        "",
        "Δprio also does **not** track CoV’s solve advantage: unlock rate is almost "
        "identical when priority falls (29%) and when it rises (27%). On the 16 rows "
        "CoV actually unlocks at b1k, mean Δprio is **worse** (+30) than on the rest "
        "(+6) — CoV helps despite looking worse to RECOMMENDED, not because of it.",
        "",
        "## More figures",
        "",
        "![Before vs after](figures/cov_feature_before_after.png)",
        "",
        "![Delta direction bars](figures/cov_feature_delta_bars.png)",
        "",
        "![Priority scatter](figures/cov_priority_scatter.png)",
        "",
        "## Stratified means (CoV unlock vs not)",
        "",
        "| feature | mean Δ when CoV helped | mean Δ otherwise |",
        "|---|---:|---:|",
    ])
    for d in list(DIMS) + ["prio"]:
        h = summary["helped"].get(d, {})
        o = summary["other"].get(d, {})
        hm = f"{h['mean']:+.3f}" if h else "—"
        om = f"{o['mean']:+.3f}" if o else "—"
        lines.append(f"| {d} | {hm} | {om} |")
    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`cov_feature_delta_subset60.csv`](cov_feature_delta_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/cov_feature_delta.py`",
        "",
    ])
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {MD_OUT}")


def print_console(summary):
    print("\n=== CoV vs RECOMMENDED feature Δ ===")
    for d in DIMS:
        st = summary[d]
        print(f"  {d:6s}  improved {st['n_improved']:2d}/60  "
              f"same {st['n_unchanged']:2d}  worse {st['n_worsened']:2d}  "
              f"mean {st['mean']:+.3f}  med {st['median']:+.3f}")
    st = summary["prio"]
    print(f"  {'prio':6s}  improved {st['n_improved']:2d}/60  "
          f"same {st['n_unchanged']:2d}  worse {st['n_worsened']:2d}  "
          f"mean {st['mean']:+.3f}  med {st['median']:+.3f}")
    print(f"  CoV unlocks at b1k: {summary['n_helped']}")
    if summary["among_prio_drop_helped"] is not None:
        print(f"  P(unlock | Δprio<0) = {summary['among_prio_drop_helped']:.2f}  "
              f"P(unlock | Δprio>0) = {summary['among_prio_rise_helped']}")


def main():
    rows = load_and_score()
    summary = summarize(rows)
    write_csv(rows)
    write_figures(rows, summary)
    write_md(rows, summary)
    print_console(summary)
    return summary


if __name__ == "__main__":
    main()
