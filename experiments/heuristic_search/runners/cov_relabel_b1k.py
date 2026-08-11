"""Relabel-dedup + the final ordering slot (`S`, vs `MK`), on both arms, at budget 1,000 and 10,000.

**Zero search nodes.** Every number is a re-ranking of the frozen subset-60
sweeps through ``abel_topk_cov_b1k``'s gated loader — the same loader, the same
truncation gate, the same 60 presentations. Nothing here calls the solver, so
the 1,000-node local cap is not in play.

Why this set can be measured at all
-----------------------------------

The ms640 top-3 run searched only the three picks each rule chose, so a dedup
there can be *counted* but not *priced*: the replacement candidate it promotes
was never searched. The subset-60 sweep searched the **entire enumerated CoV
family** of every row at both budgets, so promoting a candidate from rank 7 to
rank 3 costs nothing to score. This file is therefore the only place the dedup's
real effect — not its slot count — can be read.

The three variants, per base key
--------------------------------

```text
plain  rank by the arm's key, ties by _ident (the shipped behaviour)
rd     the same ranking, then drop any candidate whose relabel class already
       appeared, pulling deeper to refill the top k
rd_s   rank by the arm's key + S, then the same dedup    <- the intended rule
rd_mk  rank by the arm's key + MK, then the same dedup   (comparison only)
```

``S`` is ``hlab.FEATURES``' smaller mean block — the mean run length of the
thinner generator, and the heaviest-weighted term of the project's one
sanctioned heuristic ``L + 20*S + 2*MK``. It is the intended third term:
**abel -> length -> S**. ``MK`` (max knots) is carried beside it only so the two
can be compared; it is not the recommendation. Either enters as the last key
*before* ``_ident``, so it decides only what ``_ident`` would otherwise have
decided by name — it can never outvote abel or length.

Three base keys are carried, because the user's question is about both arms:

```text
abel       (abel,)                 the shipped ms640 arm
abel_len   (abel, total length)    the validated b1k ranking
len        (total length,)         the shipped "top length" arm
```

Read the cost columns, not the solve column: subset-60's oracle at budget 1,000
is 45/60 and every abel-first arm reaches the same top-3 count, so solves
saturate by construction. The repo's own
[control-with-no-dynamic-range](../../lessons/control-with-no-dynamic-range.md)
and [gap-metric](../../lessons/gap-metric-saturates-when-the-treatment-wins.md)
lessons both apply: a one-row margin on 60 rows is not a property of the key.

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_relabel_b1k
"""

import csv
import json
import os
import statistics

from experiments.equivalence_classes.lib.words import relabel_key
from experiments.heuristic_search.runners import abel_topk_cov_b1k as R
from experiments.heuristic_search.runners import abel_tiebreak_b1k as T

K = T.K
KS = T.KS
ROOT = R.ROOT

OUT_CSV = "results/comparison/cov_relabel_b1k_subset60.csv"
OUT_MD = "results/comparison/COV_RELABEL_B1K.md"
OUT_FIG = "results/comparison/cov_relabel_b1k.png"

# base key name -> (label, key function). The key is imported, never restated.
BASES = {
    "abel": ("(abel)", R.KEYS["abel"]),
    "abel_len": ("(abel, total)", R.KEYS["abel_len"]),
    "len": ("(total)", R.KEYS["len_only"]),
}
VARIANTS = ("plain", "rd", "rd_s", "rd_mk")

# third ordering term per variant; None = the name tie-break decides alone.
_THIRD = {"plain": None, "rd": None, "rd_s": T._S, "rd_mk": T._MK}


def relabel_class(d):
    """The repo's canonical form under the 8 signed permutations of {x, y}.

    ``words.relabel_key`` — the same function ``cov_top3_relabel`` gates the
    ms640 manifests with, so the study and the shipped rule cannot drift apart
    about what "the same start renamed" means.
    """
    return relabel_key((d["r1"], d["r2"]))


def rank_variant(cov, base, variant):
    """{pres_id: [candidate, ...]} under one (base key, variant) pair."""
    _, key = BASES[base]
    third = _THIRD[variant]
    out = {}
    for p, cands in cov.items():
        if third is not None:
            order = sorted(cands, key=lambda d: tuple(key(d)) + (third(d),) + R._ident(d))
        else:
            order = sorted(cands, key=lambda d: tuple(key(d)) + R._ident(d))
        if variant == "plain":
            out[p] = order
            continue
        seen, keep = set(), []
        for d in order:
            c = relabel_class(d)
            if c in seen:
                continue
            seen.add(c)
            keep.append(d)
        out[p] = keep
    return out


def relabel_waste(ranked, cov):
    """Top-k slots holding a start an earlier rank already searched, up to renaming."""
    lists = sum(1 for p in cov
                if len({relabel_class(d) for d in ranked[p][:K]})
                < min(K, len(ranked[p])))
    slots = sum(min(K, len(ranked[p])) - len({relabel_class(d) for d in ranked[p][:K]})
                for p in cov)
    return lists, slots


def promoted(ranked_plain, ranked_rd, cov):
    """Presentations whose top-k membership the dedup actually changed."""
    return {p for p in cov
            if [T._id(d) for d in ranked_plain[p][:K]]
            != [T._id(d) for d in ranked_rd[p][:K]]}


def score_all(cov):
    s = {}
    for base in BASES:
        for v in VARIANTS:
            ranked = rank_variant(cov, base, v)
            sc = T.score_ranked(ranked, cov)
            sc["waste"] = relabel_waste(ranked, cov)
            s[f"{base}__{v}"] = sc
    return s


def _row(name, sc):
    fs = sc["first_solve"]
    return {
        "arm": name,
        "k1": sc["at_k"][1], "k2": sc["at_k"][2], "k3": sc["at_k"][3],
        "deployed_total": sc["deployed_total"],
        "median_first_solve": statistics.median(fs.values()) if fs else None,
        "mean_first_solve": round(statistics.mean(fs.values()), 1) if fs else None,
        "waste_lists": sc["waste"][0], "waste_slots": sc["waste"][1],
    }


def table(s, budget):
    lines = [f"| arm | k=1 | k=3 | median nodes | mean nodes | deployed | "
             f"wasted slots |", "|---|---:|---:|---:|---:|---:|---:|"]
    for base, (lab, _) in BASES.items():
        for v in VARIANTS:
            r = _row(f"{base}__{v}", s[f"{base}__{v}"])
            suffix = {"plain": "", "rd": " + relabel-dedup",
                      "rd_s": " + relabel-dedup + S",
                      "rd_mk": " + relabel-dedup + MK"}[v]
            lines.append(
                f"| `{lab}`{suffix} | {r['k1']} | {r['k3']} | "
                f"{r['median_first_solve']:,.0f} | {r['mean_first_solve']:,.1f} | "
                f"{r['deployed_total']:,} | {r['waste_slots']} |")
    return "\n".join(lines)


def figure(s1k, s10k, path):
    """Each variant's cost **relative to its own shipped ranking**, both budgets.

    Plotted as a delta, not as absolute totals, for a specific reason: the arms differ by
    ~3%, so on a zero-based axis of ~65,000 nodes every bar is the same height and the two
    findings — that the dedup changes *nothing* and that MK changes sign — are both
    invisible. Against a zero baseline the dedup's exact inertness is a bar of literally no
    height, which is the honest picture of it.

    Down is cheaper. Solve changes are annotated where they are nonzero, because a cost
    delta means nothing without them: an arm can look cheap purely by giving up a row.

    Colour never carries a distinction alone (the reader is red-green colourblind): blue vs
    orange, and each series also has its own hatch.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    BLUE, ORANGE = "#3b6ea5", "#e08214"
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.4), dpi=200, sharey=False)
    x = np.arange(len(BASES))
    w = 0.26
    SERIES = (("rd", "+ relabel-dedup", BLUE, ""),
              ("rd_s", "+ relabel-dedup + S  (the rule)", ORANGE, "///"),
              ("rd_mk", "+ relabel-dedup + MK  (comparison)", "#7f7f7f", "..."))
    OFF = {"rd": -w, "rd_s": 0.0, "rd_mk": w}

    for ax, (s, budget) in zip(axes, ((s1k, 1000), (s10k, 10000))):
        series = []
        for v, lab, c, h in SERIES:
            d = [s[f"{b}__{v}"]["deployed_total"] - s[f"{b}__plain"]["deployed_total"]
                 for b in BASES]
            series.append((v, d))
            off = OFF[v]
            ax.bar(x + off, d, w, label=lab, color=c, edgecolor="black",
                   linewidth=.6, hatch=h, zorder=3)
        span = max((abs(v) for _, d in series for v in d), default=1) or 1
        for v, d in series:
            off = OFF[v]
            for i, (b, dv) in enumerate(zip(BASES, d)):
                dk1 = s[f"{b}__{v}"]["at_k"][1] - s[f"{b}__plain"]["at_k"][1]
                dk3 = s[f"{b}__{v}"]["at_k"][3] - s[f"{b}__plain"]["at_k"][3]
                note = f"{dv:+,}" if dv else "0"
                if dk1 or dk3:
                    note += f"\nk1 {dk1:+d}" if dk1 else ""
                    note += f"\nk3 {dk3:+d}" if dk3 else ""
                up = dv >= 0
                ax.text(i + off, dv + (0.03 if up else -0.03) * span, note,
                        ha="center", va="bottom" if up else "top", fontsize=7,
                        linespacing=1.35, zorder=4)
        ax.axhline(0, color="black", lw=1.1, zorder=2)
        ax.set_ylim(-1.45 * span, 1.45 * span)
        ax.set_xticks(x)
        ax.set_xticklabels([lab for lab, _ in BASES.values()], fontsize=9)
        ax.set_title(f"budget {budget:,}", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", color="#e8eaf0", lw=0.8, zorder=0)
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:+,.0f}".replace("+0", "0"))

    axes[0].set_ylabel("nodes vs the same arm's shipped ranking\n(down = cheaper)",
                       fontsize=9)
    # three series no longer fit inside a panel without covering a bar, so the
    # legend goes under the axes where it can never collide with data
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=8, frameon=False, ncol=3,
               loc="lower center", bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Relabel-dedup is inert; S and MK are indistinguishable on 60 rows · "
                 "top-3, subset-60", fontsize=11)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    ap = path if os.path.isabs(path) else os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    fig.savefig(ap, bbox_inches="tight")
    plt.close(fig)
    return ap


def main():
    ids60, bins, auts, cov, control = R.load()
    cov10, ctl10 = T.load_sweep(R.SWEEP_10K, set(ids60))
    s1k, s10k = score_all(cov), score_all(cov10)

    ap = os.path.join(ROOT, OUT_CSV)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    with open(ap, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(_row("x", s1k["abel__plain"])) + ["budget"])
        w.writeheader()
        for budget, s in ((1000, s1k), (10000, s10k)):
            for name in s:
                w.writerow({**_row(name, s[name]), "budget": budget})

    oracle = R.oracle_set(cov)
    greedy_hits = {p for p, c in control.items() if c['solved']}
    fig_path = figure(s1k, s10k, OUT_FIG)

    def pair(base, a, b, s):
        return T.paired(s[f"{base}__{a}"], s[f"{base}__{b}"])

    md = [
        "# Relabel-dedup, and `MK` at the last slot — both arms, budget 1,000 and 10,000",
        "",
        f"**Zero search nodes.** A re-ranking of the frozen `{R.SWEEP}` and its 10,000-node twin through `abel_topk_cov_b1k`'s gated loader, subset-60, top {K}. The sweep searched every candidate of every row, so unlike the ms640 top-3 census a promoted candidate costs nothing to score — this is the only place the dedup can be priced rather than merely counted.",
        "",
        "## Budget 1,000",
        "",
        table(s1k, 1000),
        "",
        "## Budget 10,000",
        "",
        table(s10k, 10000),
        "",
        "## Paired, on the rows both arms solve",
        "",
        "| base key | comparison | budget | win / tie / loss |",
        "|---|---|---:|---|",
    ]
    for base, (lab, _) in BASES.items():
        for a, b, what in (("rd", "plain", "dedup vs shipped"),
                           ("rd_s", "rd", "S vs name, after dedup"),
                           ("rd_mk", "rd", "MK vs name, after dedup"),
                           ("rd_s", "plain", "dedup + S vs shipped"),
                           ("rd_mk", "plain", "dedup + MK vs shipped")):
            for budget, s in ((1000, s1k), (10000, s10k)):
                pr = pair(base, a, b, s)
                md.append(f"| `{lab}` | {what} | {budget:,} | "
                          f"{pr['win']} / {pr['tie']} / {pr['loss']} |")
    short = sum(1 for p in cov for d in cov[p]
                if not d["solved"] and d["nodes_explored"] < d["node_budget"])
    n_searches = sum(len(cov[p]) for p in cov)
    md += [
        "",
        "## What the paired column can actually see",
        "",
        f"A win/tie/loss of 0/N/0 is only evidence if the metric had room to move. Two measurements say it mostly did not. **Every unsolved search burns the whole budget** — {short} of {n_searches} unsolved searches stop short of it — and the dedup **never changes rank 1** (it keeps the first-ranked member of each relabel class, so rank 1 is identical by construction). The deployed bill therefore cannot move on any row whose rank 1 already solves, which is nearly all of them. `promoted` below counts the rows whose top-{K} *membership* the change actually rewrites; `sensitive` counts the rows where that rewrite could reach the bill at all.",
        "",
        "| base key | budget | dedup rewrites top-3 | S rewrites top-3 | MK rewrites top-3 | rows the bill can see |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for budget, c in ((1000, cov), (10000, cov10)):
        for base in BASES:
            plain = rank_variant(c, base, "plain")
            rd = rank_variant(c, base, "rd")
            rds = rank_variant(c, base, "rd_s")
            rdmk = rank_variant(c, base, "rd_mk")
            sens = sum(1 for p in c if not plain[p][0]["solved"]
                       and any(d["solved"] or d["nodes_explored"] < d["node_budget"]
                               for d in plain[p][1:K]))
            md.append(f"| `{BASES[base][0]}` | {budget:,} | {len(promoted(plain, rd, c))}/{len(c)} "
                      f"| {len(promoted(rd, rds, c))}/{len(c)} "
                      f"| {len(promoted(rd, rdmk, c))}/{len(c)} | {sens}/{len(c)} |")
    md += [
        "",
        "So the dedup's 0/N/0 is not \"the dedup does nothing\" — it rewrites five-sixths of the top-3 lists. It is \"the bill cannot see ranks 2-3 except on a handful of rows.\" On `(abel)` at 10,000 that handful is **empty**, which makes the null there mathematically forced rather than measured, exactly the shape of [control-with-no-dynamic-range](../../experiments/lessons/control-with-no-dynamic-range.md). And `MK`'s support is thinner than its win column suggests: it rewrites the top-3 on 22/60 rows of `(abel)`, the arm where it *hurts* at 10,000, but only 3/60 of `(abel, total)`, the arm whose 1-2 wins are the whole case for keeping it.",
        "",
        "## Which presentations, not how many",
        "",
        "A count that does not move can still be a different set, and a figure keyed on the shipped arm would then depict a different `k` rows than the text describes. Set membership of the recommended `(abel, total)` + dedup + `S` against the shipped `(abel)`:",
        "",
        "| budget | k | shipped | recommended | identical set | gained | lost |",
        "|---:|---:|---:|---:|---|---|---|",
    ]
    for budget, s in ((1000, s1k), (10000, s10k)):
        for k in (1, K):
            a = s["abel__plain"]["hits_at"][k]
            b = s["abel_len__rd_s"]["hits_at"][k]
            gained = ", ".join(str(p) for p in sorted(b - a)) or "—"
            lost = ", ".join(str(p) for p in sorted(a - b)) or "—"
            md.append(f"| {budget:,} | {k} | {len(a)} | {len(b)} | "
                      f"{'yes' if a == b else 'no'} | {gained} | {lost} |")
    md += [
        "",
        f"Reference points at budget 1,000: best-CoV **oracle {len(oracle)}/60**, plain greedy on the untransformed pair **{len(greedy_hits)}/60**. The solve column saturates against that oracle, so read the cost columns.",
        "",
        f"![arms]({os.path.basename(OUT_FIG)})",
        "",
    ]
    mp = os.path.join(ROOT, OUT_MD)
    with open(mp, "w") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}\nwrote {OUT_FIG}")
    for budget, s in ((1000, s1k), (10000, s10k)):
        print(f"\n=== budget {budget:,} ===")
        print(table(s, budget))
    return s1k, s10k


if __name__ == "__main__":
    main()
