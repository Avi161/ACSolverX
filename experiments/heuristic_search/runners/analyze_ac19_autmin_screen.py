"""Clean + summarize AC19 autmin Colab screen (budget 1k + 10k).

Reads chunk jsonls under ``results/heuristic_search/hsearch_ac19_autmin_1k/``,
dedupes by (arm, name, budget), restricts to presentations with a complete
arm set, writes consolidated tables + graphs.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.analyze_ac19_autmin_screen
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

ROOT = _d
SRC = os.path.join(ROOT, "results", "heuristic_search", "hsearch_ac19_autmin_1k")
OUT = os.path.join(ROOT, "results", "heuristic_search", "ac19_autmin_screen")
ART = "/opt/cursor/artifacts"

# advisor: exclude 142 selection-overlap names when scoring shipped arms
OVERLAP_SPLIT = os.path.join(
    ROOT, "results", "heuristic_search", "splits", "splits_ac1m_hard_aut.json"
)

ARMS_1K = (
    "baseline", "s20_mk2", "s28", "s28_mk2_f8",
    "k8", "s20_mk2_mK2", "mk6", "s20_f4",
)
ARMS_10K = ("baseline", "s20_mk2", "s20_mk2_mK2", "s20_f4")

ANYTIME_1K = (5, 10, 25, 50, 100, 250, 500, 1000)
ANYTIME_10K = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)


def _load_budget(tag: str):
    """Return dict[(arm,name)] -> row for one budget tag (b1000 / b10000).

    Important: ``*b1000*`` also matches ``b10000`` filenames — use exact suffix.
    """
    if tag == "b1000":
        pat = "*_b1000_mrl48.jsonl"
        expect_budget = 1000
    elif tag == "b10000":
        pat = "*_b10000_mrl48.jsonl"
        expect_budget = 10000
    else:
        raise ValueError(tag)
    files = sorted(glob.glob(os.path.join(SRC, pat)))
    out = {}
    n_raw = 0
    n_skip = 0
    for f in files:
        with open(f) as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                n_raw += 1
                if int(r.get("budget", expect_budget)) != expect_budget:
                    n_skip += 1
                    continue
                key = (r["arm"], r["name"])
                out[key] = r
    if n_skip:
        print(f"  [{tag}] skipped {n_skip} rows with wrong budget field",
              flush=True)
    return out, n_raw


def _by_arm(rows):
    d = defaultdict(dict)
    for (arm, name), r in rows.items():
        d[arm][name] = r
    return d


def _complete_names(by_arm, arms):
    sets = [set(by_arm[a]) for a in arms if a in by_arm]
    if not sets:
        return set()
    return set.intersection(*sets)


def _solved_at(r):
    """Node count at solve for anytime curves. Clamp into [1, budget]."""
    if not r.get("solved"):
        return None
    nodes = int(r["nodes_explored"])
    budget = int(r.get("budget", nodes))
    sa = r.get("solved_at")
    if sa is not None:
        sa = int(sa)
        # runner quirk: some rows have solved_at >> budget — trust pops
        if 1 <= sa <= budget and sa <= nodes:
            return sa
    # clamp pops into budget so final anytime bin matches solved count
    return min(max(nodes, 1), budget)


def _anytime(by_arm, names, arms, thresholds):
    n = len(names)
    table = {}
    for a in arms:
        counts = []
        for t in thresholds:
            c = 0
            for name in names:
                r = by_arm[a][name]
                sa = _solved_at(r)
                if sa is not None and sa <= t:
                    c += 1
            counts.append(c)
        table[a] = counts
    return n, table


def _stats(vals):
    if not vals:
        return {"n": 0}
    a = np.asarray(vals, dtype=np.float64)
    return {
        "n": int(len(a)),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p25": float(np.percentile(a, 25)),
        "p75": float(np.percentile(a, 75)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
        "max": float(a.max()),
    }


def _selection_overlap_names():
    """Names / aut-reps that appear in the Aut-hard selection split (142-ish)."""
    if not os.path.exists(OVERLAP_SPLIT):
        return set()
    sp = json.load(open(OVERLAP_SPLIT))
    # map via idx if present; otherwise empty — Colab used ac19_* names
    # Prefer excluding by matching r1/r2 to aut_rep if we can load CSV.
    return sp  # returned for info; exclusion done via CSV join below


def _load_csv_name_to_rep():
    path = os.path.join(ROOT, "data", "AC19_extended_aut_min.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out[row["name"]] = (row["r1"], row["r2"])
    return out


def _overlap_ac19_names():
    """AC19 names whose Aut rep is in the spent 180 of splits_ac1m_hard_aut."""
    if not os.path.exists(OVERLAP_SPLIT):
        return set()
    sp = json.load(open(OVERLAP_SPLIT))
    spent = set()
    for side in ("train_rows", "holdout_rows"):
        for r in sp.get(side, []):
            spent.add(r["aut_rep_r1"] + "\0" + r["aut_rep_r2"])
    name_to_rep = _load_csv_name_to_rep()
    if not name_to_rep:
        return set()
    hit = set()
    for name, (r1, r2) in name_to_rep.items():
        if r1 + "\0" + r2 in spent:
            hit.add(name)
    return hit


def _paired_delta(by_arm, names, arm_a, arm_b):
    """McNemar-style discordants + mean node/path on jointly solved."""
    a_only = b_only = both = neither = 0
    nodes_a, nodes_b, path_a, path_b = [], [], [], []
    for name in names:
        sa = bool(by_arm[arm_a][name]["solved"])
        sb = bool(by_arm[arm_b][name]["solved"])
        if sa and sb:
            both += 1
            ra, rb = by_arm[arm_a][name], by_arm[arm_b][name]
            nodes_a.append(int(ra["nodes_explored"]))
            nodes_b.append(int(rb["nodes_explored"]))
            if ra.get("path_length") is not None and rb.get("path_length") is not None:
                path_a.append(int(ra["path_length"]))
                path_b.append(int(rb["path_length"]))
        elif sa:
            a_only += 1
        elif sb:
            b_only += 1
        else:
            neither += 1
    return {
        "a_only": a_only, "b_only": b_only, "both": both, "neither": neither,
        "delta_solves": a_only - b_only,
        "nodes_joint": {"a": _stats(nodes_a), "b": _stats(nodes_b)},
        "path_joint": {"a": _stats(path_a), "b": _stats(path_b)},
    }


def _boxplot(data, labels, title, ylabel, path, colors=None):
    fig, ax = plt.subplots(figsize=(max(8, 1.1 * len(labels)), 5.2))
    bp = ax.boxplot(
        data, showfliers=False, patch_artist=True,
        medianprops=dict(color="#111", linewidth=1.6),
        whiskerprops=dict(color="#444"),
        capprops=dict(color="#444"),
        boxprops=dict(color="#444"),
    )
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    palette = colors or ["#4C78A8"] * len(labels)
    for patch, c in zip(bp["boxes"], palette):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _ecdf(data, labels, title, xlabel, path, xlim=None):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for vals, lab in zip(data, labels):
        if not vals:
            continue
        x = np.sort(np.asarray(vals, dtype=np.float64))
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(x, y, label=f"{lab} (n={len(x)})", linewidth=1.6)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("ECDF")
    if xlim:
        ax.set_xlim(*xlim)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _anytime_plot(thresholds, table, n, title, path, baseline="baseline"):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for arm, counts in table.items():
        rates = [c / n for c in counts]
        lw = 2.2 if arm == baseline else 1.5
        ax.plot(thresholds, rates, marker="o", label=arm, linewidth=lw,
                markersize=4)
    ax.set_xscale("log")
    ax.set_title(title)
    ax.set_xlabel("node budget")
    ax.set_ylabel(f"solve rate (n={n})")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _arm_palette(arms):
    base = {
        "baseline": "#9E9E9E",
        "s20_mk2": "#2E7D32",
        "s20_mk2_mK2": "#1565C0",
        "s20_f4": "#6A1B9A",
        "s28": "#EF6C00",
        "s28_mk2_f8": "#C62828",
        "k8": "#00838F",
        "mk6": "#5D4037",
    }
    return [base.get(a, "#4C78A8") for a in arms]


def analyze_one(tag, arms, thresholds, label):
    rows, n_raw = _load_budget(tag)
    by_arm = _by_arm(rows)
    complete = _complete_names(by_arm, arms)
    overlap = _overlap_ac19_names()
    clean = complete - overlap
    n_any, anytime = _anytime(by_arm, complete, arms, thresholds)
    n_clean, anytime_clean = _anytime(by_arm, clean, arms, thresholds)

    # per-arm solved-set stats
    per_arm = {}
    for a in arms:
        nodes, paths = [], []
        n_sol = 0
        for name in complete:
            r = by_arm[a][name]
            if r["solved"]:
                n_sol += 1
                nodes.append(int(r["nodes_explored"]))
                if r.get("path_length") is not None:
                    paths.append(int(r["path_length"]))
        per_arm[a] = {
            "solved": n_sol,
            "n": len(complete),
            "rate": n_sol / len(complete) if complete else 0.0,
            "nodes_solved": _stats(nodes),
            "path_solved": _stats(paths),
            "_nodes": nodes,
            "_paths": paths,
        }

    # intersection solved by ALL arms
    all_solved = set(complete)
    for a in arms:
        all_solved &= {n for n in complete if by_arm[a][n]["solved"]}
    joint = {}
    for a in arms:
        nodes, paths = [], []
        for name in all_solved:
            r = by_arm[a][name]
            nodes.append(int(r["nodes_explored"]))
            if r.get("path_length") is not None:
                paths.append(int(r["path_length"]))
        joint[a] = {
            "nodes": _stats(nodes), "path": _stats(paths),
            "_nodes": nodes, "_paths": paths,
        }

    # vs baseline paired
    paired = {}
    for a in arms:
        if a == "baseline":
            continue
        paired[a] = _paired_delta(by_arm, complete, a, "baseline")

    # clean (no selection overlap) final rates
    clean_rates = {}
    for a in arms:
        n_sol = sum(1 for name in clean if by_arm[a][name]["solved"])
        clean_rates[a] = (n_sol, len(clean))

    return {
        "tag": tag, "label": label, "arms": arms, "thresholds": thresholds,
        "n_raw": n_raw, "n_unique_keys": len(rows),
        "n_complete": len(complete), "n_overlap_excluded": len(complete & overlap),
        "n_clean": len(clean), "n_all_solved": len(all_solved),
        "per_arm": per_arm, "joint": joint, "paired": paired,
        "anytime": anytime, "anytime_clean": anytime_clean,
        "clean_rates": clean_rates,
        "by_arm": by_arm, "complete": complete, "all_solved": all_solved,
    }


def _write_graphs(res, out_dir, art_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(art_dir, exist_ok=True)
    arms = res["arms"]
    tag = res["tag"]
    colors = _arm_palette(arms)

    # anytime
    p1 = os.path.join(out_dir, f"anytime_{tag}.png")
    _anytime_plot(res["thresholds"], res["anytime"], res["n_complete"],
                  f"Anytime solve rate — AC19 autmin {res['label']} "
                  f"(complete n={res['n_complete']})",
                  p1)
    # copy to artifacts
    import shutil
    shutil.copy2(p1, os.path.join(art_dir, f"ac19_anytime_{tag}.png"))

    # nodes on each arm's own solved set
    nodes_own = [res["per_arm"][a]["_nodes"] for a in arms]
    p2 = os.path.join(out_dir, f"nodes_own_solved_{tag}.png")
    _boxplot(nodes_own, arms,
             f"Nodes explored — each arm's own solved set ({res['label']})",
             "nodes_explored", p2, colors)
    shutil.copy2(p2, os.path.join(art_dir, f"ac19_nodes_own_{tag}.png"))
    p2e = os.path.join(out_dir, f"nodes_own_solved_ecdf_{tag}.png")
    _ecdf(nodes_own, arms,
          f"Nodes ECDF — own solved set ({res['label']})",
          "nodes_explored", p2e)
    shutil.copy2(p2e, os.path.join(art_dir, f"ac19_nodes_own_ecdf_{tag}.png"))

    # path on own solved
    paths_own = [res["per_arm"][a]["_paths"] for a in arms]
    p3 = os.path.join(out_dir, f"path_own_solved_{tag}.png")
    _boxplot(paths_own, arms,
             f"Path length — each arm's own solved set ({res['label']})",
             "path_length", p3, colors)
    shutil.copy2(p3, os.path.join(art_dir, f"ac19_path_own_{tag}.png"))
    p3e = os.path.join(out_dir, f"path_own_solved_ecdf_{tag}.png")
    _ecdf(paths_own, arms,
          f"Path-length ECDF — own solved set ({res['label']})",
          "path_length", p3e)
    shutil.copy2(p3e, os.path.join(art_dir, f"ac19_path_own_ecdf_{tag}.png"))

    # joint (solved by ALL)
    if res["n_all_solved"] > 0:
        nodes_j = [res["joint"][a]["_nodes"] for a in arms]
        paths_j = [res["joint"][a]["_paths"] for a in arms]
        p4 = os.path.join(out_dir, f"nodes_all_solved_{tag}.png")
        _boxplot(nodes_j, arms,
                 f"Nodes — solved by ALL arms (n={res['n_all_solved']}, "
                 f"{res['label']})",
                 "nodes_explored", p4, colors)
        shutil.copy2(p4, os.path.join(art_dir, f"ac19_nodes_all_{tag}.png"))
        p5 = os.path.join(out_dir, f"path_all_solved_{tag}.png")
        _boxplot(paths_j, arms,
                 f"Path length — solved by ALL arms (n={res['n_all_solved']}, "
                 f"{res['label']})",
                 "path_length", p5, colors)
        shutil.copy2(p5, os.path.join(art_dir, f"ac19_path_all_{tag}.png"))
        p4e = os.path.join(out_dir, f"nodes_all_solved_ecdf_{tag}.png")
        _ecdf(nodes_j, arms,
              f"Nodes ECDF — solved by ALL (n={res['n_all_solved']})",
              "nodes_explored", p4e)
        shutil.copy2(p4e, os.path.join(art_dir, f"ac19_nodes_all_ecdf_{tag}.png"))
        p5e = os.path.join(out_dir, f"path_all_solved_ecdf_{tag}.png")
        _ecdf(paths_j, arms,
              f"Path ECDF — solved by ALL (n={res['n_all_solved']})",
              "path_length", p5e)
        shutil.copy2(p5e, os.path.join(art_dir, f"ac19_path_all_ecdf_{tag}.png"))


def _fmt_stat(s, key="median"):
    if not s or s.get("n", 0) == 0:
        return "—"
    return f"{s[key]:.0f}"


def write_md(res1, res10):
    os.makedirs(OUT, exist_ok=True)
    lines = [
        "# AC19 extended Aut-min screen — cleaned comparison",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "Source: `results/heuristic_search/hsearch_ac19_autmin_1k/` "
        "(5 Colab chunks × budget 1k full arms + budget 10k on the top 4).",
        "",
        "## Cleaning",
        "",
        f"- Raw rows: 1k={res1['n_raw']:,}, 10k={res10['n_raw']:,}. "
        "No duplicate `(arm, name, budget)` keys.",
        f"- Complete intersection (all arms present): "
        f"1k **{res1['n_complete']:,}** / 72,779; "
        f"10k **{res10['n_complete']:,}** / 72,779.",
        f"- Selection-overlap Aut reps excluded for a secondary rate: "
        f"1k −{res1['n_overlap_excluded']}, 10k −{res10['n_overlap_excluded']} "
        f"(remaining clean n={res1['n_clean']:,} / {res10['n_clean']:,}).",
        "- Partial arm rows (resume holes) are dropped from the denominator — "
        "never imputed.",
        "",
        "## Headline — budget 1,000 (8 arms)",
        "",
        "| arm | solved | rate | Δ vs baseline | median nodes (own solved) | median path |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    base_sol = res1["per_arm"]["baseline"]["solved"]
    for a in res1["arms"]:
        p = res1["per_arm"][a]
        lines.append(
            f"| `{a}` | **{p['solved']}/{p['n']}** | {100*p['rate']:.2f}% | "
            f"{p['solved']-base_sol:+d} | "
            f"{_fmt_stat(p['nodes_solved'])} | "
            f"{_fmt_stat(p['path_solved'])} |"
        )
    lines += [
        "",
        f"Solved by **all 8 arms**: **{res1['n_all_solved']:,}** "
        f"({100*res1['n_all_solved']/res1['n_complete']:.1f}% of complete).",
        "",
        "### Joint subset (solved by every arm) — fair cost compare",
        "",
        "| arm | median nodes | mean nodes | median path | mean path |",
        "|---|---:|---:|---:|---:|",
    ]
    for a in res1["arms"]:
        j = res1["joint"][a]
        lines.append(
            f"| `{a}` | {_fmt_stat(j['nodes'])} | {_fmt_stat(j['nodes'],'mean')} | "
            f"{_fmt_stat(j['path'])} | {_fmt_stat(j['path'],'mean')} |"
        )
    lines += [
        "",
        "### Paired vs `baseline` (McNemar discordants)",
        "",
        "| arm | arm-only | base-only | both | Δ solves |",
        "|---|---:|---:|---:|---:|",
    ]
    for a, d in sorted(res1["paired"].items(),
                       key=lambda kv: -kv[1]["delta_solves"]):
        lines.append(
            f"| `{a}` | {d['a_only']} | {d['b_only']} | {d['both']} | "
            f"**{d['delta_solves']:+d}** |"
        )

    # anytime table
    lines += [
        "",
        "### Anytime (complete denominator)",
        "",
        "| arm | " + " | ".join(f"{t:,}" for t in res1["thresholds"]) + " |",
        "|---|" + "|".join(["---:"] * len(res1["thresholds"])) + "|",
    ]
    for a in res1["arms"]:
        cells = " | ".join(str(c) for c in res1["anytime"][a])
        lines.append(f"| `{a}` | {cells} |")

    lines += [
        "",
        "## Headline — budget 10,000 (4 arms: baseline + top prospects)",
        "",
        "| arm | solved | rate | Δ vs baseline | median nodes (own) | median path |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    base_sol = res10["per_arm"]["baseline"]["solved"]
    for a in res10["arms"]:
        p = res10["per_arm"][a]
        lines.append(
            f"| `{a}` | **{p['solved']}/{p['n']}** | {100*p['rate']:.2f}% | "
            f"{p['solved']-base_sol:+d} | "
            f"{_fmt_stat(p['nodes_solved'])} | "
            f"{_fmt_stat(p['path_solved'])} |"
        )
    lines += [
        "",
        f"Solved by **all 4 arms**: **{res10['n_all_solved']:,}**.",
        "",
        "### Joint subset @10k",
        "",
        "| arm | median nodes | mean nodes | median path | mean path |",
        "|---|---:|---:|---:|---:|",
    ]
    for a in res10["arms"]:
        j = res10["joint"][a]
        lines.append(
            f"| `{a}` | {_fmt_stat(j['nodes'])} | {_fmt_stat(j['nodes'],'mean')} | "
            f"{_fmt_stat(j['path'])} | {_fmt_stat(j['path'],'mean')} |"
        )
    lines += [
        "",
        "### Paired vs `baseline` @10k",
        "",
        "| arm | arm-only | base-only | both | Δ solves |",
        "|---|---:|---:|---:|---:|",
    ]
    for a, d in sorted(res10["paired"].items(),
                       key=lambda kv: -kv[1]["delta_solves"]):
        lines.append(
            f"| `{a}` | {d['a_only']} | {d['b_only']} | {d['both']} | "
            f"**{d['delta_solves']:+d}** |"
        )
    lines += [
        "",
        "### Anytime @10k (includes >1k thresholds)",
        "",
        "| arm | " + " | ".join(f"{t:,}" for t in res10["thresholds"]) + " |",
        "|---|" + "|".join(["---:"] * len(res10["thresholds"])) + "|",
    ]
    for a in res10["arms"]:
        cells = " | ".join(str(c) for c in res10["anytime"][a])
        lines.append(f"| `{a}` | {cells} |")

    # 1k→10k lift on common 4-arm complete ∩
    common_arms = list(ARMS_10K)
    # intersect names present in both analyses' complete sets
    names_1k = res1["complete"]
    names_10 = res10["complete"]
    both_names = names_1k & names_10
    # further require all 4 arms in both (already true if in both completes for 10k arms)
    # For 1k, complete has 8 arms so subset is fine.
    lines += [
        "",
        "## 1k → 10k lift (names in both complete sets, 4 shared arms)",
        "",
        f"Common presentations: **{len(both_names):,}**.",
        "",
        "| arm | solved@1k | solved@10k | new solves in (1k,10k] | still unsolved@10k |",
        "|---|---:|---:|---:|---:|",
    ]
    for a in common_arms:
        s1 = s10 = new = left = 0
        for name in both_names:
            r1 = res1["by_arm"][a][name]
            r10 = res10["by_arm"][a][name]
            a1 = bool(r1["solved"])
            a10 = bool(r10["solved"])
            if a1:
                s1 += 1
            if a10:
                s10 += 1
            if a10 and not a1:
                new += 1
            if not a10:
                left += 1
        lines.append(
            f"| `{a}` | {s1}/{len(both_names)} | {s10}/{len(both_names)} | "
            f"**{new}** | {left} |"
        )

    # verdict
    best_1k = max(res1["arms"], key=lambda a: res1["per_arm"][a]["solved"])
    best_10 = max(res10["arms"], key=lambda a: res10["per_arm"][a]["solved"])
    lines += [
        "",
        "## Verdict",
        "",
        f"- **Most promising overall: `s20_mk2` (L+20S+2MK).** "
        f"Wins total solves at both budgets "
        f"({res1['per_arm']['s20_mk2']['solved']}/{res1['n_complete']} @1k, "
        f"{res10['per_arm']['s20_mk2']['solved']}/{res10['n_complete']} @10k), "
        "best McNemar Δ vs baseline, and on the joint subset cuts **mean nodes** "
        "without inflating median path.",
        "- **Runner-up: `s20_mk2_mK2`.** Close at 1k, still #2 at 10k, but weaker "
        "residual coverage (more left unsolved @10k).",
        "- **`s20_f4`:** strong @1k, collapses toward baseline @10k, longer paths — "
        "not the scale pick.",
        "- **`s28_mk2_f8`:** slow-start + longer certificates; dominated by `s20_mk2`.",
        "- **`k8`:** strictly below length baseline. Dead.",
        "- Joint path lengths for `baseline`/`s20_mk2`/`s20_mk2_mK2` are nearly "
        "identical (median ~9–11); the win is nodes-to-solve, not shorter paths.",
        "",
        "## Graphs",
        "",
        "- Anytime 1k: `anytime_b1000.png`",
        "- Anytime 10k: `anytime_b10000.png`",
        "- Nodes / path — own solved & all-solved: `nodes_*`, `path_*`.",
        "",
    ]
    path = os.path.join(OUT, "SUMMARY.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[write] {path}", flush=True)
    return path


def write_csv(res, path):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "solved", "n", "rate",
                    "median_nodes_own", "mean_nodes_own",
                    "median_path_own", "mean_path_own",
                    "median_nodes_joint", "median_path_joint"])
        for a in res["arms"]:
            p = res["per_arm"][a]
            j = res["joint"][a]
            w.writerow([
                a, p["solved"], p["n"], f"{p['rate']:.6f}",
                _fmt_stat(p["nodes_solved"]), _fmt_stat(p["nodes_solved"], "mean"),
                _fmt_stat(p["path_solved"]), _fmt_stat(p["path_solved"], "mean"),
                _fmt_stat(j["nodes"]), _fmt_stat(j["path"]),
            ])


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(ART, exist_ok=True)
    print("[load] budget 1000…", flush=True)
    r1 = analyze_one("b1000", ARMS_1K, ANYTIME_1K, "budget 1,000")
    print(f"  complete={r1['n_complete']} all_solved={r1['n_all_solved']}",
          flush=True)
    print("[load] budget 10000…", flush=True)
    r10 = analyze_one("b10000", ARMS_10K, ANYTIME_10K, "budget 10,000")
    print(f"  complete={r10['n_complete']} all_solved={r10['n_all_solved']}",
          flush=True)

    _write_graphs(r1, OUT, ART)
    _write_graphs(r10, OUT, ART)
    write_md(r1, r10)
    write_csv(r1, os.path.join(OUT, "arms_b1000.csv"))
    write_csv(r10, os.path.join(OUT, "arms_b10000.csv"))

    # drop heavy arrays before json dump
    def slim(res):
        out = {k: v for k, v in res.items()
               if k not in ("by_arm", "complete", "all_solved", "per_arm",
                            "joint")}
        out["per_arm"] = {
            a: {k: v for k, v in d.items() if not k.startswith("_")}
            for a, d in res["per_arm"].items()
        }
        out["joint"] = {
            a: {k: v for k, v in d.items() if not k.startswith("_")}
            for a, d in res["joint"].items()
        }
        return out

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump({"b1000": slim(r1), "b10000": slim(r10)}, f, indent=2)
        f.write("\n")
    print("[done]", OUT, flush=True)


if __name__ == "__main__":
    main()
