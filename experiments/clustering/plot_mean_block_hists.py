"""Solved/unsolved histograms: min vs max mean block on population A (113+124).

Rebuilds the classic ``smaller mean block`` (thinner generator) histogram and
the same plot for ``larger mean block`` (``max(mean_x, mean_y)``) on the same
states, so the two can be compared side by side.

    python3 -m experiments.clustering.plot_mean_block_hists
"""
from __future__ import annotations

import csv
import json
import os
import sys

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

from experiments.clustering.rank_signals import (  # noqa: E402
    _auc, best_threshold, candidates,
)
from experiments.clustering.run_cluster_237 import pop_tables  # noqa: E402

FIG_DIR = os.path.join(ROOT, "results/comparison/figures")
FIG_OUT = os.path.join(FIG_DIR, "mean_block_min_vs_max_hists.png")
MD_OUT = os.path.join(ROOT, "results/comparison/MEAN_BLOCK_MIN_VS_MAX.md")
JSON_OUT = os.path.join(ROOT, "results/comparison/mean_block_min_vs_max.json")

SOLVED_COLOR = "#4C72B0"
UNSOLVED_COLOR = "#DD8452"


def _vals(rows, key):
    solved, unsolved = [], []
    for _name, lab, r1, r2 in rows:
        v = candidates(r1, r2)[key]
        (unsolved if lab == 1 else solved).append(v)
    return np.asarray(solved, float), np.asarray(unsolved, float)


def _hist_axis(ax, solved, unsolved, title, xlabel, cut=None):
    lo = min(solved.min(), unsolved.min())
    hi = max(solved.max(), unsolved.max())
    # Match the classic thinner-generator figure's bin feel.
    bins = np.arange(np.floor(lo * 20) / 20, np.ceil(hi * 20) / 20 + 1e-9, 0.05)
    ax.hist(solved, bins=bins, alpha=0.75, color=SOLVED_COLOR,
            label=f"solved ({len(solved)})", edgecolor="white", linewidth=0.4)
    ax.hist(unsolved, bins=bins, alpha=0.65, color=UNSOLVED_COLOR,
            label=f"unsolved ({len(unsolved)})", edgecolor="white", linewidth=0.4)
    if cut is not None:
        ax.axvline(cut, color="black", ls="--", lw=1.2,
                   label=f"cut at {cut:g}")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("presentations")
    ax.legend(frameon=False, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def run():
    rows = pop_tables()
    s_min, u_min = _vals(rows, "smaller mean block")
    s_max, u_max = _vals(rows, "larger mean block")

    y = np.array([r[1] for r in rows])
    v_min = np.concatenate([s_min, u_min])
    v_max = np.concatenate([s_max, u_max])
    # pop_tables order is all solved then all unsolved — rebuild aligned vectors
    v_min = np.array([candidates(r1, r2)["smaller mean block"]
                      for _, _, r1, r2 in rows])
    v_max = np.array([candidates(r1, r2)["larger mean block"]
                      for _, _, r1, r2 in rows])

    rule_min = best_threshold(v_min, y)
    rule_max = best_threshold(v_max, y)
    auc_min = _auc(v_min, y)
    auc_max = _auc(v_max, y)

    os.makedirs(FIG_DIR, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
    _hist_axis(
        axes[0], s_min, u_min,
        title="solvable = the thin generator sits as single letters",
        xlabel="mean run length of the thinner generator",
        cut=1.25,
    )
    _hist_axis(
        axes[1], s_max, u_max,
        title="thicker generator — does NOT separate",
        xlabel="mean run length of the thicker generator",
        cut=rule_max["threshold"],
    )
    fig.suptitle(
        "Population A (113 solved Aut-orbit reps + 124 unsolved ACA reps)",
        fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_OUT, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {FIG_OUT}")

    summary = {
        "n_solved": int(len(s_min)),
        "n_unsolved": int(len(u_min)),
        "smaller_mean_block": {
            "auc": float(auc_min),
            "solved_mean": float(s_min.mean()),
            "unsolved_mean": float(u_min.mean()),
            "solved_median": float(np.median(s_min)),
            "unsolved_median": float(np.median(u_min)),
            "rule": rule_min,
        },
        "larger_mean_block": {
            "auc": float(auc_max),
            "solved_mean": float(s_max.mean()),
            "unsolved_mean": float(u_max.mean()),
            "solved_median": float(np.median(s_max)),
            "unsolved_median": float(np.median(u_max)),
            "rule": rule_max,
        },
    }
    with open(JSON_OUT, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"wrote {JSON_OUT}")

    lines = [
        "# Mean block histograms: min vs max (population A)",
        "",
        "Same 237 states as the classic thinner-generator figure "
        "(113 solved Aut-orbit reps + 124 unsolved ACA-class reps).",
        "",
        f"![min vs max mean block](figures/{os.path.basename(FIG_OUT)})",
        "",
        "| feature | AUC | solved mean | unsolved mean | best cut | bal. acc |",
        "|---|---:|---:|---:|---:|---:|",
        (
            f"| `min(mean_x, mean_y)` (thinner) | "
            f"**{auc_min:.3f}** | {s_min.mean():.3f} | {u_min.mean():.3f} | "
            f"{rule_min['threshold']:g} | {rule_min['bal_acc']:.3f} |"
        ),
        (
            f"| `max(mean_x, mean_y)` (thicker) | "
            f"{auc_max:.3f} | {s_max.mean():.3f} | {u_max.mean():.3f} | "
            f"{rule_max['threshold']:g} | {rule_max['bal_acc']:.3f} |"
        ),
        "",
        "## Verdict",
        "",
        "- **Thinner (`min`)** separates cleanly — solved pile near 1.0–1.25, "
        "unsolved sit higher; the published cut at 1.25 still works.",
        "- **Thicker (`max`) is not similar** — the two colors heavily overlap, "
        f"AUC {auc_max:.3f} (near chance / slightly inverted vs thinner's "
        f"{auc_min:.3f}). Solved mean ({s_max.mean():.2f}) is even a bit "
        f"*higher* than unsolved ({u_max.mean():.2f}).",
        "",
        "## Source",
        "",
        "- Runner: `experiments/clustering/plot_mean_block_hists.py`",
        f"- Figure: [`figures/{os.path.basename(FIG_OUT)}`]"
        f"(figures/{os.path.basename(FIG_OUT)})",
        f"- Numbers: [`{os.path.basename(JSON_OUT)}`]({os.path.basename(JSON_OUT)})",
        "",
    ]
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {MD_OUT}")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    run()


if __name__ == "__main__":
    main()
