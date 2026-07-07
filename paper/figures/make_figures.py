#!/usr/bin/env python
"""Figure generation for the stable-AC NeurIPS preprint.

Usage
-----
    python make_figures.py --all
    python make_figures.py arms_bar ak3_plateau ...

Each figure is a function ``fig_<name>()`` that
  (a) writes ``paper/figures/out/<name>.pdf`` and ``.png`` (300 dpi, vector text),
  (b) returns a dict of every number it plotted.

After the selected figures run, the merged dict of all returned numbers is
written to ``paper/figures/out/figure_digest.json``. Each figure block also
records ``expected`` values and a per-key ``checks`` map (computed-vs-expected)
so the digest self-documents agreement; any genuine disagreement is recorded
under a top-level ``discrepancies`` list and the computed truth is plotted.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import _data as D

# --------------------------------------------------------------------------
# style
# --------------------------------------------------------------------------
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colorblind-safe palette
OI = {
    "black": "#000000",
    "orange": "#E69F00",
    "skyblue": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "grey": "#999999",
}

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.constrained_layout.use": True,
        # keep all text as vector glyphs in the PDF (never rasterize text)
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

# single-column NeurIPS text width ~5.5in
FULL_W = 5.5
HALF_W = 2.7

# collects {figure_name: {...numbers...}}
DIGEST = {}
DISCREPANCIES = []


def _save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def _check(block, key, computed, expected):
    """Record a computed vs expected comparison; log any mismatch globally."""
    ok = computed == expected
    block.setdefault("checks", {})[key] = {
        "computed": computed,
        "expected": expected,
        "match": ok,
    }
    if not ok:
        DISCREPANCIES.append(
            {"figure": block["_figure"], "key": key,
             "computed": computed, "expected": expected}
        )
    return computed


def _solved_set(rows):
    return {r["idx"] for r in rows if r.get("solved")}


# --------------------------------------------------------------------------
# fig_arms_bar
# --------------------------------------------------------------------------
def fig_arms_bar():
    name = "arms_bar"
    block = {"_figure": name}

    base_rows = D.baseline_solved_rows()
    base_set = _solved_set(base_rows)
    arm_sets = {a: _solved_set(D.arm_solved_rows(a)) for a in D.ARM_NAMES}
    union = set().union(*arm_sets.values())

    dataset_size = 640
    counts = {
        "baseline": len(base_set),
        "r1": len(arm_sets["r1"]),
        "r2": len(arm_sets["r2"]),
        "x": len(arm_sets["x"]),
        "y": len(arm_sets["y"]),
        "union": len(union),
    }

    _check(block, "baseline", counts["baseline"], 634)
    _check(block, "r1", counts["r1"], 619)
    _check(block, "r2", counts["r2"], 602)
    _check(block, "x", counts["x"], 540)
    _check(block, "y", counts["y"], 523)
    _check(block, "union", counts["union"], 620)
    _check(block, "n_rows_baseline", len(base_rows), 640)

    order = ["baseline", "r1", "r2", "x", "y", "union"]
    labels = ["baseline\n(2-gen)", "$z{=}r_1$", "$z{=}r_2$", "$z{=}x$", "$z{=}y$",
              "union\nof arms"]
    colors = [OI["black"], OI["blue"], OI["skyblue"], OI["green"],
              OI["orange"], OI["vermillion"]]

    fig, ax = plt.subplots(figsize=(FULL_W, 2.9))
    xs = range(len(order))
    vals = [counts[k] for k in order]
    ax.bar(xs, vals, color=colors, width=0.7, edgecolor="black", linewidth=0.4)
    ax.axhline(dataset_size, ls="--", lw=1.0, color=OI["grey"])
    ax.text(len(order) - 0.5, dataset_size + 6, f"dataset size = {dataset_size}",
            ha="right", va="bottom", fontsize=8, color=OI["grey"])

    for xi, v in zip(xs, vals):
        ax.text(xi, v + 6, str(v), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels)
    ax.set_ylabel("presentations solved")
    ax.set_ylim(0, dataset_size + 55)
    ax.set_title("Stabilized $z{=}w$ arms solve a strict subset of the 2-gen baseline")
    _save(fig, name)

    block.update({k: counts[k] for k in order})
    block["dataset_size"] = dataset_size
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_arms_subset
# --------------------------------------------------------------------------
def fig_arms_subset():
    name = "arms_subset"
    block = {"_figure": name}

    base_set = _solved_set(D.baseline_solved_rows())
    arm_sets = {a: _solved_set(D.arm_solved_rows(a)) for a in D.ARM_NAMES}
    base_n = len(base_set)

    per_arm = {}
    for a in D.ARM_NAMES:
        s = arm_sets[a]
        in_base = len(s & base_set)
        not_in_base = len(s - base_set)
        remainder = base_n - in_base  # baseline-only (solved by baseline, not arm)
        per_arm[a] = {
            "in_baseline": in_base,
            "not_in_baseline": not_in_base,
            "baseline_only_remainder": remainder,
        }
        _check(block, f"{a}_minus_baseline", not_in_base, 0)

    inter_all = arm_sets["r1"] & arm_sets["r2"] & arm_sets["x"] & arm_sets["y"]
    _check(block, "intersection_all_arms", len(inter_all), 523)
    _check(block, "baseline_size", base_n, 634)

    fig, ax = plt.subplots(figsize=(FULL_W, 2.9))
    arms = D.ARM_NAMES
    xs = range(len(arms))
    in_base = [per_arm[a]["in_baseline"] for a in arms]
    not_base = [per_arm[a]["not_in_baseline"] for a in arms]
    rem = [per_arm[a]["baseline_only_remainder"] for a in arms]

    b1 = ax.bar(xs, in_base, color=OI["green"], width=0.62, edgecolor="black",
                linewidth=0.4, label="arm-solved, in baseline")
    b2 = ax.bar(xs, not_base, bottom=in_base, color=OI["vermillion"], width=0.62,
                edgecolor="black", linewidth=0.4,
                label="arm-solved, NOT in baseline (0)")
    b3 = ax.bar(xs, rem, bottom=[i + n for i, n in zip(in_base, not_base)],
                color=OI["grey"], width=0.62, edgecolor="black", linewidth=0.4,
                alpha=0.55, label="baseline-only remainder")

    for xi, v in zip(xs, in_base):
        ax.text(xi, v / 2, str(v), ha="center", va="center", fontsize=8,
                color="white")
    for xi, base_top in zip(xs, in_base):
        ax.text(xi, base_n + 6, f"+{base_n - base_top}", ha="center", va="bottom",
                fontsize=7, color=OI["grey"])

    ax.axhline(base_n, ls="--", lw=1.0, color="black")
    ax.text(len(arms) - 0.5, base_n + 24, f"baseline = {base_n}", ha="right",
            va="bottom", fontsize=8)

    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"$z{{=}}{a}$" if a in ("x", "y") else f"$z{{=}}r_{a[-1]}$"
                        for a in arms])
    ax.set_ylabel("presentations")
    ax.set_ylim(0, base_n + 55)
    ax.set_title("Every arm's solved set is contained in the baseline "
                 r"($|\mathrm{arm}\setminus\mathrm{baseline}|=0$)")
    ax.legend(loc="lower center", frameon=False, ncol=1, fontsize=7,
              bbox_to_anchor=(0.5, -0.02))
    _save(fig, name)

    block["per_arm"] = per_arm
    block["intersection_all_arms"] = len(inter_all)
    block["baseline_size"] = base_n
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_ak3_plateau
# --------------------------------------------------------------------------
def fig_ak3_plateau():
    name = "ak3_plateau"
    block = {"_figure": name}

    expected = {
        ("rep", "100000"): {13: 79, 14: 11, 15: 7},
        ("rep", "1000000"): {13: 88, 14: 2, 15: 7},
        ("textbook", "100000"): {13: 77, 14: 11, 15: 9},
        ("textbook", "1000000"): {13: 86, 14: 2, 15: 9},
    }
    hists = {}
    solved_counts = {}
    for form in D.AK3_FORMS:
        for budget in D.AK3_BUDGETS:
            rows = D.ak3_rows(form, budget)
            unsolved = [r for r in rows if not r.get("solved")]
            h = collections.Counter(r["min_total_len"] for r in unsolved)
            hists[(form, budget)] = dict(sorted(h.items()))
            solved_counts[(form, budget)] = sum(1 for r in rows if r.get("solved"))
            _check(block, f"{form}_{budget}_hist",
                   {int(k): v for k, v in hists[(form, budget)].items()},
                   expected[(form, budget)])
            _check(block, f"{form}_{budget}_solved", solved_counts[(form, budget)], 0)
            _check(block, f"{form}_{budget}_nrows", len(rows), 97)

    fig, axes = plt.subplots(2, 2, figsize=(FULL_W, 4.2), sharex=True, sharey=True)
    trivial = 3
    col_titles = {"100000": "budget 100k", "1000000": "budget 1M"}
    row_labels = {"rep": "rep form", "textbook": "textbook form"}
    bins = list(range(13, 16))
    for i, form in enumerate(D.AK3_FORMS):
        for j, budget in enumerate(D.AK3_BUDGETS):
            ax = axes[i][j]
            h = hists[(form, budget)]
            vals = [h.get(b, 0) for b in bins]
            ax.bar(bins, vals, color=OI["blue"], width=0.72, edgecolor="black",
                   linewidth=0.4)
            for b, v in zip(bins, vals):
                if v:
                    ax.text(b, v + 1.2, str(v), ha="center", va="bottom", fontsize=7)
            ax.axvline(trivial, ls="--", lw=1.1, color=OI["vermillion"])
            ax.set_xlim(1.5, 16.5)
            ax.set_ylim(0, 100)
            if i == 0:
                ax.set_title(col_titles[budget])
            if j == 0:
                ax.set_ylabel(f"{row_labels[form]}\n# unsolved words")
            if i == 1:
                ax.set_xlabel("min. total length reached")
            ax.set_xticks([trivial] + bins)
    # label the trivial line once (top-left panel)
    axes[0][0].text(trivial + 0.4, 92, "trivial", rotation=90, va="top",
                    ha="left", fontsize=7, color=OI["vermillion"])
    fig.suptitle("AK(3) greedy plateaus at total length 13 — never reaches "
                 "trivial (3)", fontsize=10)
    _save(fig, name)

    block["hists"] = {f"{f}_{b}": hists[(f, b)] for (f, b) in hists}
    block["solved"] = {f"{f}_{b}": solved_counts[(f, b)] for (f, b) in solved_counts}
    block["trivial_length"] = trivial
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_hard_ties
# --------------------------------------------------------------------------
def fig_hard_ties():
    name = "hard_ties"
    block = {"_figure": name}

    expected_hist = {
        625: {17: 2, 18: 16, 19: 41, 20: 20, 21: 7, 22: 6, 25: 2},
        610: {16: 2, 17: 21, 18: 12, 19: 34, 20: 10, 21: 14, 23: 4},
    }
    expected_solvers = {
        625: {"r1": 77395, "XYYYYYYYxyyyyyyyy": 77395, "xYXyxyy": 80111, "r2": 80111},
        610: {"XYYYYYYxyyyyyyy": 61082, "r1": 61082},
    }

    data = {}
    for idx in (625, 610):
        rows = D.hard_rows(idx)
        unsolved = [r for r in rows if not r.get("solved")]
        solved = [r for r in rows if r.get("solved")]
        h = dict(sorted(collections.Counter(r["min_total_len"] for r in unsolved).items()))
        solvers = {r["word_name"]: r["nodes_explored"] for r in solved}
        data[idx] = {"hist": h, "solvers": solvers, "n_rows": len(rows),
                     "n_solved": len(solved)}
        _check(block, f"ms{idx}_hist", {int(k): v for k, v in h.items()},
               expected_hist[idx])
        _check(block, f"ms{idx}_solvers", solvers, expected_solvers[idx])

    fig, axes = plt.subplots(1, 2, figsize=(FULL_W, 3.0), sharey=False)
    for ax, idx in zip(axes, (625, 610)):
        h = data[idx]["hist"]
        bins = list(range(min(h), max(h) + 1))
        vals = [h.get(b, 0) for b in bins]
        ax.bar(bins, vals, color=OI["skyblue"], width=0.85, edgecolor="black",
               linewidth=0.3)
        ax.set_ylim(0, max(vals) * 1.32)
        ax.set_xlabel("min. total length (unsolved)")
        ax.set_title(f"MS idx {idx}  ({data[idx]['n_solved']}/{data[idx]['n_rows']} "
                     "words solve)")
        # solver annotation: group ties by node count
        ties = collections.defaultdict(list)
        for w, n in data[idx]["solvers"].items():
            ties[n].append(w)
        lines = ["solving words (nodes):"]
        for n in sorted(ties):
            ws = ", ".join(sorted(ties[n], key=len))
            lines.append(f"  {n:,}: {ws}")
        ax.text(0.97, 0.97, "\n".join(lines), transform=ax.transAxes, ha="right",
                va="top", fontsize=5.6, family="monospace",
                bbox=dict(boxstyle="round,pad=0.35", fc=OI["yellow"], ec="black",
                          lw=0.4, alpha=0.85))
    axes[0].set_ylabel("# words")
    fig.suptitle("Only relator-derived $z$ solve, and they tie the "
                 "$z{=}r_1$ control's node count", fontsize=9.5)
    _save(fig, name)

    block["ms625"] = data[625]
    block["ms610"] = data[610]
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_campaign_floor
# --------------------------------------------------------------------------
def fig_campaign_floor():
    name = "campaign_floor"
    block = {"_figure": name}

    trials = D.campaign_trials()
    n_trials = len(trials)
    n_solved = sum(1 for r in trials if r.get("solved"))
    floor_hist = dict(sorted(collections.Counter(r["min_total_len"]
                                                  for r in trials).items()))
    _check(block, "n_trials", n_trials, 16870)
    _check(block, "solved", n_solved, 0)
    _check(block, "floor_hist", {int(k): v for k, v in floor_hist.items()},
           {13: 16844, 19: 23, 20: 3})

    # Lane-C trivial-z floors by n_gen (parse n_gen from probe id "..._n<k>@...")
    probes = D.campaign_grid_probes()
    lanec = [r for r in probes if r.get("kind") == "laneC"]
    lanec_by_ngen = {}
    for r in lanec:
        pid = r["id"]  # e.g. "rep_n3@1500000"
        ng = int(pid.split("_n")[1].split("@")[0])
        lanec_by_ngen.setdefault(ng, []).append(r["min_total_len"])
    lanec_floor = {ng: max(set(v), key=v.count) for ng, v in lanec_by_ngen.items()}
    lanec_floor = dict(sorted(lanec_floor.items()))
    _check(block, "laneC_floor_by_ngen",
           {int(k): v for k, v in lanec_floor.items()},
           {3: 14, 4: 15, 5: 16})

    # trivial-z 3-gen runs (2 rows @200k, floor 14)
    tz = D.lane_c_trivial_z()
    tz_floors = sorted({r["min_total_len"] for r in tz})
    _check(block, "lane_c_trivial_z_floors", tz_floors, [14])
    _check(block, "lane_c_trivial_z_nrows", len(tz), 2)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.0),
                                  gridspec_kw={"width_ratios": [2.2, 1.0]})
    # main: log-y floor histogram over all trials
    bins = sorted(floor_hist)
    vals = [floor_hist[b] for b in bins]
    ax.bar(bins, vals, color=OI["purple"], width=0.75, edgecolor="black",
           linewidth=0.4, log=True)
    for b, v in zip(bins, vals):
        ax.text(b, v * 1.25, f"{v:,}", ha="center", va="bottom", fontsize=7)
    ax.axvline(3, ls="--", lw=1.1, color=OI["vermillion"])
    ax.text(3.3, ax.get_ylim()[1] * 0.4, "trivial (3)", rotation=90, va="top",
            ha="left", fontsize=7, color=OI["vermillion"])
    ax.set_xlabel("min. total length reached")
    ax.set_ylabel("# trials (log)")
    ax.set_xlim(1.5, 21.5)
    ax.set_ylim(0.6, n_trials * 3)
    ax.set_title(f"Lane-D campaign: {n_trials:,} trials, 0 solved")

    # side: Lane-C trivial-z floor vs n_gen
    ngs = list(lanec_floor)
    fl = [lanec_floor[k] for k in ngs]
    ax2.bar([str(n) for n in ngs], fl, color=OI["green"], width=0.6,
            edgecolor="black", linewidth=0.4)
    for i, (n, v) in enumerate(zip(ngs, fl)):
        ax2.text(i, v + 0.15, str(v), ha="center", va="bottom", fontsize=7)
    # trivial reference = n_gen
    ax2.plot(range(len(ngs)), ngs, "o--", color=OI["vermillion"], lw=1.0, ms=3,
             label="trivial = $n$")
    ax2.set_xlabel("# generators $n$")
    ax2.set_ylabel("Lane-C floor")
    ax2.set_ylim(0, 18)
    ax2.set_title("trivial-$z$ floor")
    ax2.legend(frameon=False, fontsize=7, loc="lower right")
    _save(fig, name)

    block["n_trials"] = n_trials
    block["solved"] = n_solved
    block["floor_hist"] = {int(k): v for k, v in floor_hist.items()}
    block["laneC_floor_by_ngen"] = {int(k): v for k, v in lanec_floor.items()}
    block["lane_c_trivial_z_floors"] = tz_floors
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_rl_gap
# --------------------------------------------------------------------------
def _truthy(v):
    return str(v).strip().lower() == "true"


def fig_rl_gap():
    name = "rl_gap"
    block = {"_figure": name}

    rows = D.beam_laneD_floor()
    n = len(rows)
    train_solved = sum(1 for r in rows if _truthy(r["train_solved"]))
    eval_solved = sum(1 for r in rows if _truthy(r["solved"]))
    tpl = [int(r["train_path_length"]) for r in rows]
    tpl_hist = dict(sorted(collections.Counter(tpl).items()))

    _check(block, "n", n, 155)
    _check(block, "train_solved", train_solved, 155)
    _check(block, "eval_solved", eval_solved, 0)
    _check(block, "tpl_min", min(tpl), 2)
    _check(block, "tpl_max", max(tpl), 16)

    w2 = D.beam_laneD_floor_w2048()
    w2_n = len(w2)
    w2_eval = sum(1 for r in w2 if _truthy(r["solved"]))
    _check(block, "w2048_n", w2_n, 30)
    _check(block, "w2048_eval_solved", w2_eval, 0)

    mean_tpl = statistics.mean(tpl)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(FULL_W, 3.0),
                                  gridspec_kw={"width_ratios": [1.0, 1.5]})
    # left: paired solve rate bars
    bars = ax.bar([0, 1], [train_solved, eval_solved],
                  color=[OI["green"], OI["vermillion"]], width=0.6,
                  edgecolor="black", linewidth=0.4)
    for xi, v in zip([0, 1], [train_solved, eval_solved]):
        ax.text(xi, v + 3, f"{v}/{n}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["train\npresentations", "eval\n(floor set)"])
    ax.set_ylabel("beam-solved")
    ax.set_ylim(0, n + 20)
    ax.set_title("RL train vs. floor eval")

    # right: histogram of train path length
    bins = list(range(min(tpl), max(tpl) + 1))
    vals = [tpl_hist.get(b, 0) for b in bins]
    ax2.bar(bins, vals, color=OI["blue"], width=0.85, edgecolor="black",
            linewidth=0.3)
    ax2.axvline(mean_tpl, ls="--", lw=1.1, color=OI["orange"])
    ax2.text(mean_tpl + 0.3, max(vals) * 0.9, f"mean {mean_tpl:.1f}", fontsize=7,
             color=OI["orange"])
    ax2.set_xlabel("train solve path length")
    ax2.set_ylabel("# presentations")
    ax2.set_title("Train paths short (min 2, max 16)")
    ax2.annotate(f"width=2048 escalation:\n{w2_eval}/{w2_n} floor solved",
                 xy=(0.97, 0.97), xycoords="axes fraction", ha="right", va="top",
                 fontsize=7,
                 bbox=dict(boxstyle="round,pad=0.3", fc=OI["yellow"], ec="black",
                           lw=0.4, alpha=0.85))
    fig.suptitle("Agent solves all training presentations but 0 of the "
                 "155-floor eval set", fontsize=9.5)
    _save(fig, name)

    block.update({
        "n": n, "train_solved": train_solved, "eval_solved": eval_solved,
        "tpl_min": min(tpl), "tpl_max": max(tpl), "tpl_mean": round(mean_tpl, 3),
        "tpl_hist": tpl_hist, "w2048_n": w2_n, "w2048_eval_solved": w2_eval,
    })
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_cap_hump
# --------------------------------------------------------------------------
def fig_cap_hump():
    name = "cap_hump"
    block = {"_figure": name}

    rows = D.cap_solve_stratified()
    n = len(rows)
    n_solved = sum(1 for r in rows if r.get("solved"))
    xs = [r["total_len"] for r in rows]
    ys = [r["min_total_len"] for r in rows]
    _check(block, "n_rows", n, 1800)
    _check(block, "solved", n_solved, 0)
    _check(block, "min_total_len_min", min(ys), 13)
    _check(block, "min_total_len_max", max(ys), 13)

    per_bucket = collections.Counter(xs)
    trivial = 3

    fig, ax = plt.subplots(figsize=(FULL_W, 3.0))
    # deterministic x-jitter per point so identical (x,y) stacks are visible
    import random
    rng = random.Random(0)
    jx = [x + rng.uniform(-0.32, 0.32) for x in xs]
    ax.scatter(jx, ys, s=7, color=OI["blue"], alpha=0.35, edgecolors="none",
               label="1,800 candidates")
    # emphasize the exact plateau
    ax.axhline(13, ls="-", lw=1.2, color=OI["vermillion"], alpha=0.9)
    ax.text(40.3, 13, "plateau floor = 13", ha="right", va="bottom", fontsize=8,
            color=OI["vermillion"])
    ax.axhline(trivial, ls="--", lw=1.1, color=OI["green"])
    ax.axhspan(0, trivial + 0.5, color=OI["green"], alpha=0.10)
    ax.text(13, trivial - 0.6, "solved region (trivial = 3)", ha="left", va="top",
            fontsize=8, color=OI["green"])
    ax.set_xlabel("candidate total length (starting)")
    ax.set_ylabel("min. total length reached")
    ax.set_ylim(0, 16)
    ax.set_xlim(11, 41)
    ax.set_title("Every candidate — from length 13 to 40 — collapses to exactly 13")
    _save(fig, name)

    block.update({
        "n_rows": n, "solved": n_solved,
        "min_total_len_min": min(ys), "min_total_len_max": max(ys),
        "total_len_buckets": dict(sorted(per_bucket.items())),
        "trivial_length": trivial,
    })
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# fig_two_floors  (hero)
# --------------------------------------------------------------------------
# floor_mkey class prefixes (verified against the F->AK3 certificate)
F_PREFIX = "030305040606"
AK3_PREFIX = "030503060406"


def fig_two_floors():
    name = "two_floors"
    block = {"_figure": name}

    census = D.floor_census()
    n = len(census)
    fm = collections.Counter(r["floor_mkey"] for r in census)
    _check(block, "n_rows", n, 1006)
    _check(block, "n_distinct_floors", len(fm), 2)

    # classify the two floor mkeys
    classes = {}
    for mkey, cnt in fm.items():
        if mkey.startswith(F_PREFIX):
            classes["F"] = {"mkey": mkey, "count": cnt}
        elif mkey.startswith(AK3_PREFIX):
            classes["AK3"] = {"mkey": mkey, "count": cnt}
        else:
            classes[mkey] = {"mkey": mkey, "count": cnt}
    f_count = classes["F"]["count"]
    ak3_count = classes["AK3"]["count"]
    _check(block, "F_count", f_count, 712)
    _check(block, "AK3_count", ak3_count, 294)

    # certificate: confirm 21 steps and the two endpoints
    cert = D.cert_laneF()
    n_steps = len(cert["steps"])
    _check(block, "cert_steps", n_steps, 21)

    def w2s(r):
        m = {1: "x", 2: "y", -1: "X", -2: "Y", 3: "z", -3: "Z"}
        return "".join(m[i] for i in r)

    start_words = [w2s(r) for r in cert["start"]["relators"]]
    end_words = [w2s(r) for r in cert["end"]["relators"]]
    block["cert_start_words"] = start_words
    block["cert_end_words"] = end_words

    fig, ax = plt.subplots(figsize=(FULL_W, 3.4))
    xs = [0, 1]
    vals = [f_count, ak3_count]
    cols = [OI["blue"], OI["vermillion"]]
    ax.bar(xs, vals, color=cols, width=0.5, edgecolor="black", linewidth=0.6)
    for xi, v in zip(xs, vals):
        ax.text(xi, v + 12, f"{v}", ha="center", va="bottom", fontsize=11,
                fontweight="bold")

    ax.set_xticks(xs)
    ax.set_xticklabels([
        "floor class $F$",
        "floor class AK(3)",
    ], fontsize=10)
    # presentation subtitles under the tick labels
    ax.text(0, -95, r"$\langle x,y \mid y^{-2}xyx^{-2},\ y^{-3}x^{-2}yx\rangle$",
            ha="center", va="top", fontsize=8)
    ax.text(1, -95, r"AK(3) floor:  $\langle x,y \mid YXYxyx,\ YYYYxxx\rangle$",
            ha="center", va="top", fontsize=8)

    ax.set_ylabel("# elimination floors (of 1,006)")
    ax.set_ylim(0, max(vals) + 130)
    ax.set_title("Two-floor census: all 1,006 Lane-D floors fall in two AC classes",
                 fontsize=9.5)

    # arrow annotating the certified path between the two bars
    ymid = max(vals) + 55
    ax.annotate("", xy=(1, ymid), xytext=(0, ymid),
                arrowprops=dict(arrowstyle="-|>", color=OI["green"], lw=1.8,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(0.5, ymid + 34, f"certified {n_steps}-move AC path  $F \\to$ AK(3)",
            ha="center", va="bottom", fontsize=9, color=OI["green"],
            fontweight="bold")

    ax.margins(x=0.25)
    # give room for the presentation labels below the axis
    ax.set_xlim(-0.7, 1.7)
    _save(fig, name)

    block.update({
        "n_rows": n,
        "F": classes["F"],
        "AK3": classes["AK3"],
        "cert_steps": n_steps,
    })
    DIGEST[name] = block
    return {name: block}


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------
FIGURES = {
    "arms_bar": fig_arms_bar,
    "arms_subset": fig_arms_subset,
    "ak3_plateau": fig_ak3_plateau,
    "hard_ties": fig_hard_ties,
    "campaign_floor": fig_campaign_floor,
    "rl_gap": fig_rl_gap,
    "cap_hump": fig_cap_hump,
    "two_floors": fig_two_floors,
}


def main():
    ap = argparse.ArgumentParser(description="Generate stable-AC paper figures.")
    ap.add_argument("--all", action="store_true", help="render every figure")
    ap.add_argument("names", nargs="*", help="figure names to render")
    args = ap.parse_args()

    if args.all or not args.names:
        todo = list(FIGURES)
    else:
        todo = args.names
        unknown = [n for n in todo if n not in FIGURES]
        if unknown:
            ap.error(f"unknown figures: {unknown}; known: {list(FIGURES)}")

    for n in todo:
        print(f"[fig] {n} ...", flush=True)
        FIGURES[n]()

    digest = dict(DIGEST)
    if DISCREPANCIES:
        digest["discrepancies"] = DISCREPANCIES
    else:
        digest["discrepancies"] = []
    with open(OUT / "figure_digest.json", "w") as f:
        json.dump(digest, f, indent=2, sort_keys=True)
    print(f"[digest] wrote {OUT / 'figure_digest.json'} "
          f"({len(DISCREPANCIES)} discrepancies)")


if __name__ == "__main__":
    main()
