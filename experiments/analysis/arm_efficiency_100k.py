"""How much cheaper is s20_mk2 than greedy, and does that depend on difficulty?

THE ONLY PLACE THE TWO ARMS MEET
--------------------------------
The AC19 ladder gives each arm its own residual list, so at 1M, 5M and 10M the
two arms are mostly searching different rows and no honest per-row comparison
exists. The 100k stage is the exception: greedy ran the 831 rows the 10k screen
left it and s20_mk2 ran its own 259, and **225 rows appear on both lists at the
same budget and the same cap** (100,000 nodes, mrl 48). Those 225 are the paired
sample -- every row both arms actually searched under identical conditions.

WHY "BOTH SOLVED" IS NOT THE WHOLE STORY
----------------------------------------
Of the 225, both arms solve 133; s20_mk2 alone solves 53; greedy alone solves 0.
A speedup ratio only exists for the 133. Restricting to them therefore throws
away exactly the cases where s20_mk2 won by the largest margin -- the ratio is
right-censored at the budget wall, and the censoring is one-sided. This module
reports the ratio *and* the censored cells, because the ratio alone understates
the difference and the composition alone hides the per-row cost.

WHY THE DIFFICULTY AXIS IS PRESENTATION LENGTH, NOT NODE COUNT
--------------------------------------------------------------
Binning a ratio g/s on g is a trap: the top bin selects for rows where g ran
long, so the ratio rises with the bin even under pure noise. Measured here, the
correlation between log speedup and log difficulty is +0.55 when difficulty is
greedy's own node count and +0.08 when it is the geometric mean of the two node
counts, which is the arm-neutral coordinate orthogonal to the log ratio. The
apparent "s20_mk2 pulls ahead on hard rows" in the first framing is mostly
regression to the mean.

Starting total length is structural, independent of either arm, and -- unlike a
node count -- defined for the rows *neither* arm solved, so the same bins carry
the composition and the ratio. Among these rows shorter means harder (rank
correlation between total length and a greedy solve is +0.49): every row here
already survived a 10,000-node screen, and a short presentation that survives
one is rigid, while a long one merely needed room to reduce.

    PYTHONPATH=. python3 -m experiments.analysis.arm_efficiency_100k
    PYTHONPATH=. python3 -m experiments.analysis.arm_efficiency_100k --json out.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics as st

HS = os.path.join("results", "heuristic_search")
STAGE = os.path.join(HS, "hsearch_ac19_hard100k")
SCREEN = os.path.join(HS, "ac19_autmin_screen")

GREEDY_JSONL = os.path.join(STAGE, "ac19_unsolved10k_baseline_b100000_mrl48.jsonl")
S20_JSONL = os.path.join(STAGE, "ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl")
SCREEN_CSVS = (os.path.join(SCREEN, "unsolved_10k_baseline.csv"),
               os.path.join(SCREEN, "unsolved_10k_s20_mk2.csv"))

BUDGET = 100_000
MRL = 48

# (low, high) on total starting length; high is exclusive, None = open.
# Ordered hardest first -- shorter is harder among screen survivors.
BINS = ((0, 18, "hardest"), (18, 20, "middle"), (20, None, "easiest"))


def load(path):
    """One record per name, preferring a finished record and the deeper search."""
    best = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("error") or rec.get("name") is None:
                continue
            prev = best.get(rec["name"])
            if prev is None or rec.get("nodes_explored", 0) >= prev.get("nodes_explored", 0):
                best[rec["name"]] = rec
    return best


def presentations():
    out = {}
    for path in SCREEN_CSVS:
        with open(path) as fh:
            for row in csv.DictReader(fh):
                out[row["name"]] = (row["r1"], row["r2"])
    return out


def bin_of(total):
    for lo, hi, label in BINS:
        if lo <= total and (hi is None or total < hi):
            return label
    raise ValueError(total)


def bin_title(lo, hi):
    return f"L {lo}-{hi - 1}" if hi is not None else f"L {lo}+"


def rank_corr(xs, ys):
    def ranked(vs):
        order = sorted(range(len(vs)), key=lambda i: vs[i])
        out = [0] * len(vs)
        for pos, idx in enumerate(order):
            out[idx] = pos
        return out
    rx, ry = ranked(xs), ranked(ys)
    return pearson(rx, ry)


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    vx = sum((a - mx) ** 2 for a in xs)
    vy = sum((b - my) ** 2 for b in ys)
    return cov / math.sqrt(vx * vy) if vx and vy else float("nan")


def quartiles(vals):
    s = sorted(vals)
    return s[len(s) // 4], s[(3 * len(s)) // 4]


def collect():
    greedy, s20, pres = load(GREEDY_JSONL), load(S20_JSONL), presentations()
    shared = sorted(set(greedy) & set(s20))
    if not shared:
        raise SystemExit("no shared rows -- are the 100k jsonls present?")

    settings = {(greedy[n]["budget"], greedy[n]["mrl"]) for n in shared}
    settings |= {(s20[n]["budget"], s20[n]["mrl"]) for n in shared}
    if settings != {(BUDGET, MRL)}:
        raise SystemExit(f"arms did not meet at one budget/cap: {sorted(settings)}")

    rows = []
    for name in shared:
        r1, r2 = pres[name]
        rows.append({
            "name": name, "r1": r1, "r2": r2, "total_length": len(r1) + len(r2),
            "greedy_solved": bool(greedy[name]["solved"]),
            "s20_solved": bool(s20[name]["solved"]),
            "greedy_nodes": greedy[name]["nodes_explored"],
            "s20_nodes": s20[name]["nodes_explored"],
        })
    for r in rows:
        r["bin"] = bin_of(r["total_length"])
        r["speedup"] = (r["greedy_nodes"] / r["s20_nodes"]
                        if r["greedy_solved"] and r["s20_solved"] else None)
        # s20 solved, greedy hit the wall: the ratio is only a lower bound.
        r["speedup_lower_bound"] = (BUDGET / r["s20_nodes"]
                                    if r["s20_solved"] and not r["greedy_solved"] else None)
    return rows


def summarise(rows):
    paired = [r for r in rows if r["speedup"] is not None]
    cells = {
        "both": sum(1 for r in rows if r["greedy_solved"] and r["s20_solved"]),
        "s20_only": sum(1 for r in rows if r["s20_solved"] and not r["greedy_solved"]),
        "greedy_only": sum(1 for r in rows if r["greedy_solved"] and not r["s20_solved"]),
        "neither": sum(1 for r in rows if not r["greedy_solved"] and not r["s20_solved"]),
    }
    ratios = [r["speedup"] for r in paired]
    overall = {
        "n_shared": len(rows), "cells": cells,
        "median": st.median(ratios), "geomean": st.geometric_mean(ratios),
        "s20_cheaper_pct": 100 * sum(1 for v in ratios if v > 1) / len(ratios),
        "aggregate": (sum(r["greedy_nodes"] for r in paired)
                      / sum(r["s20_nodes"] for r in paired)),
        # the two binning axes, to show the trap rather than assert it
        "corr_logspeedup_vs_log_greedy_nodes": pearson(
            [math.log(r["greedy_nodes"]) for r in paired],
            [math.log(r["speedup"]) for r in paired]),
        "corr_logspeedup_vs_log_geomean_nodes": pearson(
            [math.log(math.sqrt(r["greedy_nodes"] * r["s20_nodes"])) for r in paired],
            [math.log(r["speedup"]) for r in paired]),
        "rank_corr_length_vs_greedy_solved": rank_corr(
            [r["total_length"] for r in rows],
            [1.0 if r["greedy_solved"] else 0.0 for r in rows]),
    }

    per_bin = []
    for lo, hi, label in BINS:
        got = [r for r in rows if r["bin"] == label]
        if not got:
            continue
        pair = [r for r in got if r["speedup"] is not None]
        cens = [r["speedup_lower_bound"] for r in got if r["speedup_lower_bound"] is not None]
        entry = {
            "bin": label, "title": bin_title(lo, hi), "n": len(got),
            "both": sum(1 for r in got if r["greedy_solved"] and r["s20_solved"]),
            "s20_only": sum(1 for r in got if r["s20_solved"] and not r["greedy_solved"]),
            "greedy_only": sum(1 for r in got if r["greedy_solved"] and not r["s20_solved"]),
            "neither": sum(1 for r in got if not r["greedy_solved"] and not r["s20_solved"]),
            "greedy_solve_rate": 100 * sum(1 for r in got if r["greedy_solved"]) / len(got),
            "s20_solve_rate": 100 * sum(1 for r in got if r["s20_solved"]) / len(got),
            "n_paired": len(pair),
        }
        if pair:
            vals = [r["speedup"] for r in pair]
            entry["median"] = st.median(vals)
            entry["geomean"] = st.geometric_mean(vals)
            entry["q1"], entry["q3"] = quartiles(vals)
            entry["s20_cheaper_pct"] = 100 * sum(1 for v in vals if v > 1) / len(vals)
        if cens:
            entry["censored_median_lower_bound"] = st.median(cens)
        per_bin.append(entry)
    return {"overall": overall, "bins": per_bin}


def report(summary):
    o = summary["overall"]
    c = o["cells"]
    print(f"AC19 100k stage -- {o['n_shared']} rows both arms searched at "
          f"budget {BUDGET:,}, cap {MRL}\n")
    print(f"  both solved       {c['both']:>4}")
    print(f"  s20_mk2 only      {c['s20_only']:>4}")
    print(f"  greedy only       {c['greedy_only']:>4}   <- s20_mk2 never lost a row greedy won")
    print(f"  neither           {c['neither']:>4}\n")
    print(f"  speedup on the {c['both']} paired rows: median {o['median']:.2f}x, "
          f"geomean {o['geomean']:.2f}x, aggregate {o['aggregate']:.2f}x")
    print(f"  s20_mk2 cheaper on {o['s20_cheaper_pct']:.0f}% of them\n")
    print(f"  corr(log speedup, log difficulty): {o['corr_logspeedup_vs_log_greedy_nodes']:+.3f} "
          f"binning on greedy nodes (biased), "
          f"{o['corr_logspeedup_vs_log_geomean_nodes']:+.3f} arm-neutral")
    print(f"  rank corr(total length, greedy solved): "
          f"{o['rank_corr_length_vs_greedy_solved']:+.3f} -> shorter is harder here\n")
    head = f"  {'bin':<8} {'n':>4} {'both':>5} {'s20only':>8} {'neither':>8} " \
           f"{'greedy%':>8} {'s20%':>7} {'median':>8} {'IQR':>13}"
    print(head)
    print("  " + "-" * (len(head) - 2))
    for b in summary["bins"]:
        iqr = f"{b['q1']:.2f}-{b['q3']:.2f}" if "q1" in b else "--"
        med = f"{b['median']:.2f}x" if "median" in b else "--"
        print(f"  {b['title']:<8} {b['n']:>4} {b['both']:>5} {b['s20_only']:>8} "
              f"{b['neither']:>8} {b['greedy_solve_rate']:>7.0f}% {b['s20_solve_rate']:>6.0f}% "
              f"{med:>8} {iqr:>13}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", metavar="PATH", help="also write the summary and rows as JSON")
    args = ap.parse_args(argv)

    rows = collect()
    summary = summarise(rows)
    report(summary)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"summary": summary, "rows": rows}, fh, indent=2)
        print(f"\nwrote {args.json}")
    return summary


if __name__ == "__main__":
    main()
