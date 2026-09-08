#!/usr/bin/env python3
"""Week-9 figures: the AC19 cascade, binned by difficulty.

    PYTHONPATH=. python3 presentations/week_9/figures/make_figures.py

Every number is read off the frozen campaign jsonl in results/heuristic_search/.
Nothing here runs a search, and nothing in content.js is typed by hand -- the deck
interpolates this script's stats.js.

TWO POPULATIONS, AND THEY ARE NOT THE SAME EXPERIMENT
-----------------------------------------------------
  AC19 extended : all 156,762 raw presentations, cascade at budget 1,000 ONLY.
  AC19 aut-min  : the 72,779 Aut(F2) orbit representatives, cascade over the full
                  501 / 1,000 / 100,000 ladder.

So the extended set has no 1k-10k or >=10k bin -- not because it has no hard rows,
but because its run stopped at 1,000. Its tail is the 3,208 unsolved, not an empty
bin. Only the three head bins compare across populations, and the figures say so.

BANDS ARE THE CASCADE'S OWN COST
--------------------------------
Week 8 banded on the CONTROL's cost, for a good reason quoted there: a band defined
by the treatment selects for rows the treatment is good at. Here the cascade is the
only arm with a per-row cost on every row, so it has to define the bands; the honest
move is to say so rather than to pretend the bands are arm-neutral. BANDS and their
labels are byte-identical to week 8's so the two decks can be read together.

WHY greedy AND s20_mk2 ARE BOUNDS, NOT NUMBERS
----------------------------------------------
Their per-row cost was only ever stored for rows that FAILED the 10,000-node screen
(831 and 259 rows). For the other ~72k the archive keeps a failure list and nothing
else, so all that is known is "solved at <= 10,000". Re-running them is barred by the
standing archive rule, so this script substitutes:

    <= 10,000       for a row the arm solved at or below the 10k screen
    exact           where a later rung recorded it
    >= 10,000,000   for a row that exhausted the 10M budget

Those two substitutions push in OPPOSITE directions, so a single mean is not a bound
in either direction. Means are therefore emitted as a [lo, hi] bracket and medians as
a bound string. The cascade column is exact throughout and is the only one quoted bare.

Emits presentations/assets/week_9/{*.svg, stats.js} and week_9/standalone.html.
"""
from __future__ import annotations

import csv
import json
import os
import statistics as st
import sys

import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# svg.fonttype="none" leaves the font unresolved in the SVG, so the BROWSER picks
# Helvetica Neue exactly as the deck's CSS does. matplotlib still warns that it
# cannot find the family locally while measuring text; that warning is noise here.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = os.path.dirname(HERE)
PRES = os.path.dirname(WEEK)
ROOT = os.path.dirname(PRES)
OUT = os.path.join(PRES, "assets", "week_9")
RES = os.path.join(ROOT, "results", "heuristic_search")
sys.path.insert(0, ROOT)

N_EXT, N_AUT = 156_762, 72_779
SCREEN_BUDGET, TEN_M = 10_000, 10_000_000

# Week 8's bands, unchanged, so the two decks read together.
BANDS = [(0, 10), (10, 100), (100, 1_000), (1_000, 10_000), (10_000, 10 ** 12)]
BAND_LABELS = ["< 10", "10–100", "100–1k", "1k–10k", "≥ 10k"]

# Week 8's palette. INK is the baseline arm and BLUE the treatment, which is this
# series' established language; ORANGE is its third slot and is chosen over any
# green for the reason week 8 states in its own source -- never red/green.
INK, GRAY, MUTED, BLUE, FAINT = "#16181d", "#b9bec9", "#9aa1b0", "#4864e8", "#e8eaf0"
ORANGE, LIGHT = "#e69f00", "#d8dce4"
ARM_COLOR = {"greedy": INK, "s20_mk2": ORANGE, "cascade": BLUE}

plt.rcParams.update({
    "font.family": "Helvetica Neue, Helvetica, Arial, sans-serif",
    "font.size": 12, "axes.edgecolor": "#d7dae2", "axes.linewidth": 0.8,
    "axes.titlesize": 13, "axes.titleweight": "medium", "xtick.color": "#6b7280",
    "ytick.color": "#6b7280", "axes.labelcolor": "#3c4250",
    "figure.facecolor": "white", "axes.facecolor": "white", "svg.fonttype": "none",
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name + ".svg"))
    plt.close(fig)
    print("  wrote", name + ".svg")


def jsonl(rel):
    path = os.path.join(RES, rel)
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def names(rel):
    with open(os.path.join(RES, rel), newline="") as fh:
        return {r["name"] for r in csv.DictReader(fh)}


def band_of(n):
    for i, (lo, hi) in enumerate(BANDS):
        if lo <= n < hi:
            return i
    return len(BANDS) - 1


def describe(values):
    v = sorted(values)
    return {"n": len(v), "mean": round(st.mean(v), 1) if v else None,
            "median": int(st.median(v)) if v else None,
            "min": v[0] if v else None, "max": v[-1] if v else None,
            "total": sum(v)}


# ------------------------------------------------------------------ the cascade

# Job B: the 8 aut-min representatives the cascade left open, re-run at a 10,000,000
# ceiling. TRANSCRIBED FROM THE RUN LOG -- the jsonl has not landed in the repo, so
# these are flagged provisional and the deck says so. Every one is standalone
# s20_mk2's own 1M cost plus exactly 501, the cascade's fixed stage-1..3 prefix.
JOB_B = {"ac19_20270": 229_666, "ac19_39288": 156_174, "ac19_43611": 157_125,
         "ac19_49095": 152_246, "ac19_54616": 149_962, "ac19_54765": 150_293,
         "ac19_57992": 230_345, "ac19_65206": 229_099}
JOB_B_PROVISIONAL = True

CASCADE_LADDER = [
    "ac19_cascade_screen/ac19_cascade_screen_cascade501_b501_mrl255.jsonl",
    "ac19_residue_unstarved/ac19_cascade_screen_cascade501_b1000_mrl255_sb1000.jsonl",
    "ac19_residue_unstarved/ac19_cascade_screen_cascade501_b100000_mrl255_sb10000.jsonl",
]


def cascade_autmin():
    """name -> nodes, over the 72,779, taking each row at the rung that settled it."""
    cost = {}
    for rel in CASCADE_LADDER:
        for r in jsonl(rel):
            if (r.get("solved") or r.get("aut_assisted")) and r["name"] not in cost:
                cost[r["name"]] = r["nodes_explored"]
    cost.update(JOB_B)
    return cost


def cascade_extended():
    rows = jsonl("ac19_extended_screen/ac19_cascade_screen_cascade501_b1000_mrl255.jsonl")
    solved = {r["name"]: r["nodes_explored"] for r in rows
              if r.get("solved") or r.get("aut_assisted")}
    ac = sum(1 for r in rows if r.get("solved"))
    return solved, len(rows) - len(solved), ac, len(solved) - ac


def bin_table(cost, population=None):
    """Per-band n / mean / median, plus the pooled total.

    Two shares, because they answer different questions and mixing them is how
    the extended and aut-min columns stopped being comparable: `share` is of the
    rows that HAVE a cost (the table's own denominator), `share_pop` is of the
    whole population including rows that never solved.
    """
    out = []
    pop = population or len(cost)
    for i, label in enumerate(BAND_LABELS):
        vals = [v for v in cost.values() if band_of(v) == i]
        d = describe(vals) if vals else {"n": 0, "mean": None, "median": None}
        out.append({"band": label, "share": round(100 * d["n"] / len(cost), 2),
                    "share_pop": round(100 * d["n"] / pop, 2), **d})
    total = describe(list(cost.values()))
    return out, total


# ------------------------------------------------------- greedy / s20_mk2 bounds

ARM_RUNGS = {
    "greedy": ["hsearch_ac19_hard100k/ac19_unsolved10k_baseline_b100000_mrl48.jsonl",
               "leftovers_1m/leftovers_1m_greedy_b1000000_mrl48.jsonl",
               "leftovers_5m/leftovers_5m_greedy_b5000000_mrl64.jsonl",
               "ac19_10m/ac19_10m_greedy_b10000000_mrl64.jsonl"],
    "s20_mk2": ["hsearch_ac19_hard100k/ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl",
                "leftovers_1m/leftovers_1m_s20_mk2_b1000000_mrl48.jsonl",
                "leftovers_5m/leftovers_5m_s20_mk2_b5000000_mrl64.jsonl",
                "ac19_10m/ac19_10m_s20_mk2_b10000000_mrl64.jsonl"],
}
ARM_10K_LIST = {"greedy": "ac19_autmin_screen/unsolved_10k_baseline.csv",
                "s20_mk2": "ac19_autmin_screen/unsolved_10k_s20_mk2.csv"}


def arm_costs(arm):
    """(exact, censored, failed_10k) for one arm over the aut-min population."""
    exact, censored = {}, set()
    for rel in ARM_RUNGS[arm]:
        for r in jsonl(rel):
            if r.get("solved") and r["name"] not in exact:
                exact[r["name"]] = r["nodes_explored"]
    for r in jsonl(ARM_RUNGS[arm][-1]):
        if not r.get("solved"):
            censored.add(r["name"])
    return exact, censored, names(ARM_10K_LIST[arm])


def arm_on_bands(arm, cascade_cost):
    """Per cascade band, the arm's cost bracket. See the module docstring."""
    exact, censored, failed = arm_costs(arm)
    # The low end of an unknown-easy row's bracket is 1, NOT min(exact): `exact`
    # holds only rows that FAILED the 10k screen, so its minimum is above 10,000
    # (10,008 greedy, 10,131 s20_mk2) and pairing it with a 10,000 ceiling
    # inverted every bracket -- mean_lo > mean_hi on all five bands, and the
    # figure then drew both arms as flat lines pinned to the ceiling.
    floor = 1
    rows = []
    for i, label in enumerate(BAND_LABELS):
        lo_vals, hi_vals, kinds = [], [], {"exact": 0, "bounded": 0, "censored": 0}
        for name, c in cascade_cost.items():
            if band_of(c) != i:
                continue
            if name in censored:
                lo_vals.append(TEN_M); hi_vals.append(TEN_M); kinds["censored"] += 1
            elif name in exact:
                lo_vals.append(exact[name]); hi_vals.append(exact[name]); kinds["exact"] += 1
            elif name in failed:
                # failed the 10k screen but no later rung recorded it: should not
                # happen, and if it does the row is dropped rather than guessed.
                continue
            else:
                lo_vals.append(floor); hi_vals.append(SCREEN_BUDGET); kinds["bounded"] += 1
        if not hi_vals:
            rows.append({"band": label, "n": 0}); continue
        rows.append({
            "band": label, "n": len(hi_vals),
            "mean_lo": round(st.mean(lo_vals), 1), "mean_hi": round(st.mean(hi_vals), 1),
            "median_lo": int(st.median(lo_vals)), "median_hi": int(st.median(hi_vals)),
            **kinds,
        })
    return rows, len(exact), len(censored), len(failed)


# ------------------------------------------------------------------ other blocks

def stage_block():
    from experiments.search.stage_attribution import attribute, final_rows
    rows = final_rows()
    counts, split = attribute(rows)
    ac = sum(1 for r in rows.values() if r["solved"])
    aut = sum(1 for r in rows.values() if r["aut_assisted"] and not r["solved"])
    return {"counts": dict(counts),
            "split": {k: {"ac": v[0], "aut": v[1]} for k, v in split.items()},
            "n": len(rows), "ac": ac, "aut": aut,
            "open": sorted(n for n, r in rows.items()
                           if not (r["solved"] or r["aut_assisted"]))}


def rewrite_block():
    """What the recognised pattern is, measured rather than asserted."""
    rows = [r for r in jsonl(CASCADE_LADDER[0])
            if r["winner"] == "rewrite" and (r["solved"] or r["aut_assisted"])]
    other = [r for r in jsonl(CASCADE_LADDER[0])
             if r["winner"] != "rewrite" and (r["solved"] or r["aut_assisted"])]
    moves = sorted(r["certificate_moves"] for r in rows)
    has5 = sum(1 for r in rows if 5 in (len(r["r1"]), len(r["r2"])))
    return {"n": len(rows), "has5": has5, "other_n": len(other),
            "other_has5": sum(1 for r in other if 5 in (len(r["r1"]), len(r["r2"]))),
            "moves_min": moves[0], "moves_med": int(st.median(moves)),
            "moves_p99": moves[int(len(moves) * 0.99)], "moves_max": moves[-1]}


def tenm_block(cascade_cost):
    """The rows NO arm settled at 10,000,000, and what the cascade did with them."""
    g = {r["name"] for r in jsonl(ARM_RUNGS["greedy"][-1]) if not r["solved"]}
    s = {r["name"] for r in jsonl(ARM_RUNGS["s20_mk2"][-1]) if not r["solved"]}
    mutual = sorted(g & s)
    # The rung that SETTLED the row, not the first rung it appears in. Every row
    # appears in the 501 screen (it is the whole population), so keying on first
    # appearance reported budget=501 for all nine and made the slide claim 9/9
    # settled inside the prefix when the true figure is 6.
    by_name = {}
    for rel in CASCADE_LADDER:
        for r in jsonl(rel):
            if r["name"] in mutual and (r["solved"] or r["aut_assisted"]) \
                    and r["name"] not in by_name:
                by_name[r["name"]] = r
    return {"greedy_open": len(g), "s20_open": len(s), "mutual": mutual,
            "rows": [{"name": n, "nodes": cascade_cost[n],
                      "budget": by_name[n]["budget"],
                      "ac": bool(by_name[n]["solved"])} for n in mutual],
            "in_prefix": sum(1 for n in mutual if by_name[n]["budget"] == 501),
            "ac_certified": sum(1 for n in mutual if by_name[n]["solved"])}


def originals_block():
    """Job A: the pre-aut-min originals of the orbits greedy exhausted at 10M."""
    rows = jsonl("ac19_orig_10m/ac19_orig_10m_greedy_b10000000_mrl64.jsonl")
    if not rows:
        return {}
    solved = [r for r in rows if r["solved"]]
    n = sorted(r["nodes_explored"] for r in solved)
    ctl = [r for r in jsonl(ARM_RUNGS["greedy"][-1]) if not r["solved"]]
    casc = jsonl("ac19_orig_cascade/ac19_cascade_screen_cascade501_b100000_mrl255_sb10000.jsonl")
    return {"n": len(rows), "solved": len(solved), "orbits": len(ctl),
            "min": n[0], "median": int(st.median(n)), "max": n[-1], "total": sum(n),
            "ctl_nodes": TEN_M,
            "casc_n": len(casc), "casc_solved": sum(1 for r in casc if r["solved"]),
            "casc_min": min((r["nodes_explored"] for r in casc), default=None),
            "casc_max": max((r["nodes_explored"] for r in casc), default=None)}


def u124_block():
    # Count DISTINCT rows, not lines: the 10M jsonl has 137 lines for 124 rows
    # (a resumed lane re-appends), and len() made the slide say "0 / 137" beside
    # a foot saying "0 of 124".
    s20 = jsonl("u124_10m/u124_10m_s20_mk2_b10000000_mrl64.jsonl")
    s40 = [r for r in jsonl("u124_s40_gen/u124_s40_gen_starter10000.jsonl")
           if not r.get("error")]
    s20_solved = {r["name"] for r in s20 if r.get("solved")}
    s40_solved = {r["name"] for r in s40 if r.get("solved")}
    return {"s20_n": len({r["name"] for r in s20}), "s20_solved": len(s20_solved),
            "s20_budget": TEN_M, "s20_lines": len(s20),
            "s40_n": len({r["name"] for r in s40}), "s40_solved": len(s40_solved),
            "s40_budget": 10_000}


# ----------------------------------------------------------------------- figures

def fig_bins(table, total, title, name, unsolved=None, truncated_from=None):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.2),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    labels = [b["band"] for b in table]
    ns = [b["n"] for b in table]
    live = [i for i, v in enumerate(ns) if v]
    bars = ax.bar(range(len(labels)), ns, color=BLUE, width=.66)
    for i in live:
        ax.text(i, ns[i], f"{ns[i]:,}\n{table[i]['share']}%", ha="center", va="bottom",
                fontsize=10.5, color=INK, linespacing=1.25)
    if truncated_from is not None:
        # Grey ONLY the bands the budget makes unreachable and that are genuinely
        # empty. The extended run stops at 1,000, so its "1k-10k" band can hold
        # exactly one attainable value -- a row solving on its very last node --
        # and one row does. Painting "not run" over a real bar would be a lie.
        for i in range(truncated_from, len(labels)):
            if ns[i]:
                ax.text(i, ns[i], "  ← the budget's\n  last node",
                        ha="left", va="bottom", fontsize=9, color=MUTED, linespacing=1.3)
                continue
            ax.bar([i], [max(ns) * .02], color=LIGHT, width=.66)
            ax.text(i, max(ns) * .04, "not run\nat this\nbudget", ha="center", va="bottom",
                    fontsize=9, color=MUTED, linespacing=1.3)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
    ax.set_ylabel("presentations"); ax.set_ylim(0, max(ns) * 1.34)
    ax.set_title(title, loc="left", color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    med = [table[i]["median"] for i in live]
    mean = [table[i]["mean"] for i in live]
    x = range(len(live))
    ax2.plot(x, med, "o-", color=BLUE, lw=2, ms=7, label="median")
    ax2.plot(x, mean, "s--", color=ORANGE, lw=1.8, ms=6, label="mean")
    # BELOW the marker: the mean line runs above the median everywhere on this
    # data, so a label offset upward lands on it.
    for j, i in enumerate(live):
        ax2.annotate(f"{med[j]:,}", (j, med[j]), textcoords="offset points",
                     xytext=(0, -17), ha="center", fontsize=10, color=BLUE)
    ax2.set_yscale("log"); ax2.set_xticks(list(x))
    ax2.set_xticklabels([labels[i] for i in live])
    ax2.set_ylabel("nodes explored (log)")
    ax2.set_title(f"mean {total['mean']:,}  ·  median {total['median']:,}  "
                  f"over all {total['n']:,}", loc="left", color=INK)
    ax2.legend(frameon=False, fontsize=10.5, loc="upper left")
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    if unsolved:
        ax.text(.99, .97, f"+{unsolved:,} unsolved\nat the ceiling", transform=ax.transAxes,
                ha="right", va="top", fontsize=10, color=MUTED, linespacing=1.35)
    save(fig, name)


def fig_compare(aut, ext):
    fig, ax = plt.subplots(figsize=(9.4, 4.0))
    idx = [0, 1, 2]
    w = .38
    # share_pop, not share: the legend names the FULL populations, so the bars
    # have to be over those too. Dividing the extended side by the 153,554 it
    # solved while labelling it 156,762 inflated every extended bar.
    a = [aut[i]["share_pop"] for i in idx]
    e = [ext[i]["share_pop"] for i in idx]
    ax.bar([i - w / 2 for i in idx], e, w, color=GRAY, label=f"AC19 extended · {N_EXT:,}")
    ax.bar([i + w / 2 for i in idx], a, w, color=BLUE, label=f"aut-min · {N_AUT:,}")
    for i in idx:
        ax.text(i - w / 2, e[i], f"{e[i]}%", ha="center", va="bottom", fontsize=10.5, color=MUTED)
        ax.text(i + w / 2, a[i], f"{a[i]}%", ha="center", va="bottom", fontsize=10.5, color=BLUE)
    ax.set_xticks(idx); ax.set_xticklabels([BAND_LABELS[i] for i in idx])
    ax.set_ylabel("share of the population (%)")
    ax.set_title("The three bands both populations actually ran", loc="left", color=INK)
    ax.legend(frameon=False, fontsize=11)
    ax.set_ylim(0, max(a + e) * 1.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "bins_compare")


def fig_arms(cas_tbl, g_rows, s_rows):
    """What is actually KNOWN per band, per arm -- not a fabricated comparison.

    An earlier version drew greedy and s20_mk2 as node-count brackets beside the
    cascade's median. With the bracket stated honestly (1 to 10,000) both arms
    became one full-height block covering the whole plot: truthful and useless.
    The informative quantity is not their cost -- it is how much of each band
    they have any cost for at all, which is almost none until the hard tail.
    """
    idx = [i for i, b in enumerate(cas_tbl) if b["n"]]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.3),
                                  gridspec_kw={"width_ratios": [1, 1.25]})
    x = list(range(len(idx)))

    ax.plot(x, [cas_tbl[i]["median"] for i in idx], "o-", color=BLUE, lw=2.4, ms=8)
    for j, i in enumerate(idx):
        ax.annotate(f"{cas_tbl[i]['median']:,}", (j, cas_tbl[i]["median"]),
                    textcoords="offset points", xytext=(0, -17), ha="center",
                    fontsize=10, color=BLUE)
    ax.set_yscale("log"); ax.set_xticks(x)
    ax.set_xticklabels([BAND_LABELS[i] for i in idx])
    ax.set_ylabel("median nodes (log)")
    ax.set_title("cascade — exact on every row", loc="left", color=BLUE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    w = .38
    for off, (arm, rows, col) in zip((-w / 2, w / 2),
                                     (("greedy", g_rows, INK),
                                      ("s20_mk2", s_rows, ORANGE))):
        known = [100 * (rows[i].get("exact", 0) + rows[i].get("censored", 0))
                 / max(rows[i]["n"], 1) for i in idx]
        ax2.bar([j + off for j in x], known, w, color=col, label=arm)
        for j, v in zip(x, known):
            ax2.text(j + off, v + 1.5, f"{v:.0f}%" if v >= 1 else "<1%",
                     ha="center", fontsize=9.5,
                     color=col if v >= 1 else MUTED)
    ax2.set_xticks(x); ax2.set_xticklabels([BAND_LABELS[i] for i in idx])
    ax2.set_ylabel("% of the band with a stored cost")
    ax2.set_ylim(0, 118)
    ax2.set_title("greedy and s20_mk2 — how much is even known",
                  loc="left", color=INK)
    ax2.legend(frameon=False, fontsize=10.5, loc="upper left")
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    save(fig, "arms_on_bins")


def fig_stages(sb):
    fig, ax = plt.subplots(figsize=(9.6, 3.0))
    order = ["rewrite (BS collapse)", "s40_gen", "s20_mk2", "terminal", "unsolved"]
    cols = {"rewrite (BS collapse)": BLUE, "s40_gen": ORANGE, "s20_mk2": INK,
            "terminal": GRAY, "unsolved": "#c0392b"}
    left = 0
    for k in order:
        v = sb["counts"].get(k, 0)
        if not v:
            continue
        ax.barh([0], [v], left=left, color=cols[k], height=.5)
        if v / sb["n"] > .02:
            ax.text(left + v / 2, 0, f"{k}\n{v:,}", ha="center", va="center",
                    color="white", fontsize=11, linespacing=1.3)
        left += v
    ax.set_xlim(0, sb["n"]); ax.set_yticks([]); ax.set_xlabel("orbits")
    ax.set_title(f"Which stage returned the certificate · all {sb['n']:,}",
                 loc="left", color=INK)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    save(fig, "stage_attribution")


def fig_tenm(tb):
    fig, ax = plt.subplots(figsize=(9.6, 4.0))
    rows = sorted(tb["rows"], key=lambda r: r["nodes"])
    y = range(len(rows))
    ax.barh(list(y), [r["nodes"] for r in rows], color=BLUE, height=.62)
    ax.axvline(TEN_M, color=INK, ls="--", lw=1.4)
    ax.text(TEN_M, len(rows) - .3, "  greedy and s20_mk2\n  both stopped here",
            va="top", fontsize=10.5, color=INK, linespacing=1.35)
    for i, r in enumerate(rows):
        ax.text(r["nodes"] * 1.15, i, f"{r['nodes']:,}", va="center",
                fontsize=10.5, color=INK)
    ax.set_yticks(list(y)); ax.set_yticklabels([r["name"] for r in rows], fontsize=10)
    ax.set_xscale("log"); ax.set_xlim(50, TEN_M * 3.2)
    ax.set_xlabel("nodes explored (log)")
    ax.set_title("The 9 rows no arm settled at 10,000,000 — cascade cost",
                 loc="left", color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "tenm_residue")


def fig_originals(ob):
    if not ob:
        return
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    ax.hist([1], bins=1, alpha=0)  # keep axes even if the block is thin
    ax.bar([0], [ob["ctl_nodes"]], color=INK, width=.5,
           label=f"aut-min representative · {ob['orbits']} orbits, none solved")
    ax.bar([1], [ob["median"]], color=BLUE, width=.5,
           label=f"its raw original · {ob['solved']}/{ob['n']} solved")
    ax.set_yscale("log")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["minimised", "original"])
    ax.set_ylabel("nodes (log)")
    for i, v in ((0, ob["ctl_nodes"]), (1, ob["median"])):
        ax.text(i, v * 1.25, f"{v:,}", ha="center", fontsize=11.5, color=INK)
    ax.set_title("Same arm, same budget, same cap — only the input word differs",
                 loc="left", color=INK)
    ax.legend(frameon=False, fontsize=10.5, loc="upper center")
    ax.set_ylim(1, ob["ctl_nodes"] * 12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "autmin_harder")


def fig_u124(ub):
    fig, ax = plt.subplots(figsize=(9.0, 3.0))
    ax.barh([1], [ub["s20_budget"]], color=INK, height=.5)
    ax.barh([0], [ub["s40_budget"]], color=ORANGE, height=.5)
    ax.set_xscale("log"); ax.set_yticks([0, 1])
    ax.set_yticklabels([f"s40_gen · {ub['s40_solved']}/{ub['s40_n']}",
                        f"s20_mk2 · {ub['s20_solved']}/{ub['s20_n']}"])
    for y, v in ((1, ub["s20_budget"]), (0, ub["s40_budget"])):
        ax.text(v * 1.3, y, f"{v:,} nodes", va="center", fontsize=11, color=INK)
    ax.set_xlim(1e3, ub["s20_budget"] * 30)
    ax.set_title("u124 carries two zeros, a thousand-fold apart", loc="left", color=INK)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "u124_two_zeros")


def fig_funnel():
    fig, ax = plt.subplots(figsize=(9.0, 2.5))
    ax.barh([1], [N_EXT], color=GRAY, height=.52)
    ax.barh([0], [N_AUT], color=BLUE, height=.52)
    ax.text(N_EXT * 1.02, 1, f"{N_EXT:,} raw presentations", va="center", fontsize=11.5, color=INK)
    ax.text(N_AUT * 1.02, 0, f"{N_AUT:,} Aut(F₂) orbits", va="center", fontsize=11.5, color=BLUE)
    ax.set_yticks([]); ax.set_xlim(0, N_EXT * 1.5); ax.set_xticks([])
    ax.set_title("AC19_extended, and the orbit representatives it collapses to",
                 loc="left", color=INK)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    save(fig, "populations")


# -------------------------------------------------------------------------- main

def main():
    os.makedirs(OUT, exist_ok=True)
    print("reading the frozen campaign files (no search is run)")

    cas_aut = cascade_autmin()
    assert len(cas_aut) == N_AUT, f"aut-min cascade coverage {len(cas_aut):,}"
    aut_tbl, aut_tot = bin_table(cas_aut, N_AUT)

    cas_ext, ext_unsolved, ext_ac, ext_aut = cascade_extended()
    ext_tbl, ext_tot = bin_table(cas_ext, N_EXT)
    # Job B's 8 reconstructed rows are a tenth of the aut-min node mass, so the
    # deck has to be able to say how much of the total rests on them.
    job_b_mass = sum(JOB_B.values())

    g_rows, g_exact, g_cens, g_failed = arm_on_bands("greedy", cas_aut)
    s_rows, s_exact, s_cens, s_failed = arm_on_bands("s20_mk2", cas_aut)

    sb, rb = stage_block(), rewrite_block()
    tb, ob, ub = tenm_block(cas_aut), originals_block(), u124_block()

    W = {
        "n_ext": N_EXT, "n_aut": N_AUT, "screen_budget": SCREEN_BUDGET, "ten_m": TEN_M,
        "bands": BAND_LABELS,
        "aut": {"bins": aut_tbl, "total": aut_tot, "n": len(cas_aut),
                "job_b_n": len(JOB_B), "job_b_mass": job_b_mass,
                "job_b_pct": round(100 * job_b_mass / aut_tot["total"], 1)},
        "ext": {"bins": ext_tbl, "total": ext_tot, "n": len(cas_ext),
                "unsolved": ext_unsolved, "budget": 1000,
                "ac": ext_ac, "aut_assisted": ext_aut,
                "live_bands": sum(1 for b in ext_tbl if b["n"])},
        "arms": {
            "greedy": {"bins": g_rows, "exact": g_exact, "censored": g_cens,
                       "bounded": N_AUT - g_failed, "failed_10k": g_failed},
            "s20_mk2": {"bins": s_rows, "exact": s_exact, "censored": s_cens,
                        "bounded": N_AUT - s_failed, "failed_10k": s_failed},
        },
        "stages": sb, "rewrite": rb, "tenm": tb, "orig": ob, "u124": ub,
        "job_b_provisional": JOB_B_PROVISIONAL,
    }

    with open(os.path.join(OUT, "stats.js"), "w") as fh:
        fh.write("// generated by presentations/week_9/figures/make_figures.py — do not edit\n")
        fh.write("window.W9 = " + json.dumps(W) + ";\n")
    print("  wrote stats.js")

    fig_funnel()
    fig_bins(aut_tbl, aut_tot, f"AC19 aut-min · {N_AUT:,} orbits · full ladder",
             "bins_autmin")
    fig_bins(ext_tbl, ext_tot, f"AC19 extended · {N_EXT:,} · budget 1,000 only",
             "bins_extended", unsolved=ext_unsolved, truncated_from=3)
    fig_compare(aut_tbl, ext_tbl)
    fig_arms(aut_tbl, g_rows, s_rows)
    fig_stages(sb)
    fig_tenm(tb)
    fig_originals(ob)
    fig_u124(ub)

    print()
    print(f"aut-min  bins: " + "  ".join(
        f"{b['band']}={b['n']:,}(med {b['median']})" for b in aut_tbl if b["n"]))
    print(f"  total {aut_tot['n']:,}  mean {aut_tot['mean']:,}  median {aut_tot['median']:,}")
    print(f"extended bins: " + "  ".join(
        f"{b['band']}={b['n']:,}(med {b['median']})" for b in ext_tbl if b["n"]))
    print(f"  total {ext_tot['n']:,}  mean {ext_tot['mean']:,}  median {ext_tot['median']:,}"
          f"  +{ext_unsolved:,} unsolved")
    print(f"arm coverage: greedy exact {g_exact:,} censored {g_cens} · "
          f"s20_mk2 exact {s_exact:,} censored {s_cens}")
    build_standalone()
    return 0


def build_standalone():
    """One self-contained file: the same renderer, stats and content, SVG inlined.

    GitHub Pages serves the multi-file deck directly, so this exists for the cases
    that cannot fetch siblings -- an Artifact, an email attachment, a USB stick.
    It is GENERATED, never edited: the deck and this file cannot drift.
    """
    renderer = open(os.path.join(WEEK, "week9_presentation.html")).read()
    stats = open(os.path.join(OUT, "stats.js")).read()
    content = open(os.path.join(WEEK, "content.js")).read()

    # Inline every figure the content references, as an <svg> string keyed by filename.
    figs = {}
    for name in sorted(os.listdir(OUT)):
        if name.endswith(".svg"):
            svg = open(os.path.join(OUT, name)).read()
            svg = svg[svg.index("<svg"):]          # drop the XML prolog and DOCTYPE
            figs[name] = svg

    inject = ("<script>window.__FIGS__ = " + json.dumps(figs) + ";</script>\n"
              "<script>" + stats + "</script>\n"
              "<script>" + content.replace("const A = '../assets/week_9/';",
                                           "const A = '';") + "</script>\n")
    html = renderer.replace(
        '<script src="../assets/week_9/stats.js"></script>\n<script src="content.js"></script>',
        inject)
    # Swap the <img> for the inlined markup at render time -- one line, in the same
    # place the renderer builds a figure, so its layout rules still apply.
    html = html.replace(
        "'<img src=\"'+f.img+'\" alt=\"\" loading=\"eager\">'",
        "(window.__FIGS__ && window.__FIGS__[f.img] ? window.__FIGS__[f.img] "
        ": '<img src=\"'+f.img+'\" alt=\"\" loading=\"eager\">')")
    path = os.path.join(WEEK, "standalone.html")
    with open(path, "w") as fh:
        fh.write(html)
    print(f"  wrote standalone.html ({len(html) // 1024} KB, {len(figs)} figures inlined)")


if __name__ == "__main__":
    raise SystemExit(main())
