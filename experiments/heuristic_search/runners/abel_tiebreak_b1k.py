"""Which tie-break does the abelianized-magnitude key want second — length, or the shorter relator?

**Zero search nodes.** Every number here is a re-ranking of the frozen
``covsweep_1000_66_*.jsonl`` (and, as a free robustness check, its 10,000-node twin) through
``abel_topk_cov_b1k``'s own gated loader, so the candidate set, the anti-leak gate and the
truncation gate are the ones that already carry the incumbent numbers. No solver is called;
nothing here can exceed the local budget cap.

## The question

``abel`` alone is a filter, not a ranking: it leaves a median of 6 candidates tied at its
minimum on subset-60 and collapses to a unique pick on only 7 of 60. Something has to break
that tie, and two orderings are on the table:

| arm | key |
|---|---|
| ``abel_min_len`` | ``(abel, min(|r1|,|r2|), |r1|+|r2|)`` — shorter relator first |
| ``abel_len_min`` | ``(abel, |r1|+|r2|, min(|r1|,|r2|))`` — total length first |

Both then fall through to ``_ident`` (the CoV's own name) for determinism, which is the only
key left: with two relators ``max = total - min``, so once ``abel``, ``min`` and ``total``
are fixed there is no further length information to spend.

## "Mean relator length" is total length

The proposal as first worded was ``(abel, mean relator length, total)`` against
``(abel, total, mean relator length)``. Every candidate here is a **two**-relator pair, so
``mean = total / 2`` — a strictly monotone function of total length, hence the identical
ordering. Those two arms are one arm, and ``assert_mean_is_length`` proves it on all 60
presentations rather than arguing it. The substantive contrast is the one above, on
``min(|r1|, |r2|)``, which is not a function of the total.

## min-relator here is a start feature, not the search's progress signal

``min_relator_length`` earned its reputation as a *progress* signal read off a running
search. This key reads ``min(len(r1), len(r2))`` off the **start** pair, before a node is
popped — the anti-leak gate in ``abel_topk_cov_b1k.load`` exists precisely so no key can
reach the search-derived ``min_relator``/``min_relator_length`` columns. Same word, a
different object; a win here would not be evidence for the other one.

## What is measured

Every arm ranks a presentation's CoV candidates, takes the top 3, and runs them in rank
order at the sweep's budget. Two costs, as in the ms640 census:

- ``first_solve`` — nodes over ranks 1..r, r = the first rank that solves. The deployed cost,
  and the one the paired comparison uses.
- ``deployed`` — ``first_solve`` where the presentation solves, otherwise the full 3 searches.
  The total bill of running the policy over all 60.

Arms are compared **on their both-solved intersection**, never by their own means over their
own solved sets: each arm's solved set is its own denominator.

## Why two budgets, and why the held-out 124 is absent

Subset-60 at budget 1,000 has an oracle of 45 and puts every ``abel``-first arm on the same
41 — a 1–2 row band in which to separate two keys. Re-scoring the 10,000-node sweep costs
nothing (the file is already open for gate 1) and is the only cheap way to ask whether a
1,000-node margin is a property of the key or of the budget. The genuinely held-out set,
``covsweep_50000_124_*`` over the unsolved 124, is **not** usable: no candidate in the whole
enumerated CoV family solves any of the 124 at budget 50,000, so its oracle is 0 and every
arm ties at zero. A control with no dynamic range measures nothing.

    python3 -m experiments.heuristic_search.runners.abel_tiebreak_b1k
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))

from experiments.heuristic_search.runners import abel_topk_cov_b1k as R  # noqa: E402

ROOT = R.ROOT
K = 3
KS = (1, 2, 3)
HELDOUT = ("results/stable_ac/cov/"
           "covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl")
OUT_CSV = "results/comparison/abel_tiebreak_b1k_subset60.csv"
OUT_MD = "results/comparison/ABEL_TIEBREAK_B1K.md"


# --------------------------------------------------------------------------- keys

def _minrel(d):
    """The shorter of the two START relators. Never the row's search-derived min_relator."""
    return min(len(d["r1"]), len(d["r2"]))


def _meanrel(d):
    """Mean START relator length. With two relators this is exactly total / 2."""
    return (len(d["r1"]) + len(d["r2"])) / 2.0


def _abel(d):
    return R.abel_magnitude(d["r1"], d["r2"])


ARMS = {
    # the incumbents, for reference
    "abel":          lambda d: (_abel(d),),
    "abel_len_lex":  lambda d: (_abel(d), R._start_len(d), R._longest(d)),
    "len_only":      lambda d: (R._start_len(d),),
    # the proposal, as literally worded (mean == total / 2, so these two are one arm)
    "abel_mean_len": lambda d: (_abel(d), _meanrel(d), R._start_len(d)),
    "abel_len_mean": lambda d: (_abel(d), R._start_len(d), _meanrel(d)),
    # the substantive contrast
    "abel_min_len":  lambda d: (_abel(d), _minrel(d), R._start_len(d)),
    "abel_len_min":  lambda d: (_abel(d), R._start_len(d), _minrel(d)),
    # min alone, to see what it does with no length behind it
    "abel_min":      lambda d: (_abel(d), _minrel(d)),
}

HEADLINE = ("abel_min_len", "abel_len_min")

# the key chains, for the discrimination table: how much of the tie each one actually breaks
CHAINS = {
    "abel":               lambda d: (_abel(d),),
    "abel + min":         lambda d: (_abel(d), _minrel(d)),
    "abel + total":       lambda d: (_abel(d), R._start_len(d)),
    "abel + min + total": lambda d: (_abel(d), _minrel(d), R._start_len(d)),
    "abel + total + longest": lambda d: (_abel(d), R._start_len(d), R._longest(d)),
}


# ------------------------------------------------------------------------- costs

def first_solve_nodes(cands, k=K):
    """Nodes over ranks 1..r, r the first rank that solves. None if none of the k solve."""
    return R.cumulative_nodes(cands, k)


def deployed_nodes(cands, k=K):
    """first_solve where it solves, else the full k searches — what the policy actually bills."""
    n = first_solve_nodes(cands, k)
    return sum(d["nodes_explored"] for d in cands[:k]) if n is None else n


def ident_decided(cands, k=K):
    """True if the top-k SET is decided by ``_ident`` — a candidate at rank > k carries the
    same key tuple as the one at rank k, so the ordered keys alone do not choose."""
    return len(cands) > k and cands[k - 1]["_key"] == cands[k]["_key"]


def rank1_tied(cands):
    """True if rank 1 is decided by ``_ident`` — rank 2 carries the same key tuple."""
    return len(cands) > 1 and cands[0]["_key"] == cands[1]["_key"]


def rank_arm(cov, key):
    """Sorted candidates per presentation, each row stamped with its own key tuple."""
    out = {}
    for p, v in cov.items():
        for d in v:
            d["_key"] = key(d)
        out[p] = sorted(v, key=lambda d: d["_key"] + R._ident(d))
    return out


def _id(d):
    return (d["z_word"], d["iso_gen"], d["iso_index"], d["r1"], d["r2"])


# ------------------------------------------------------------------------- gates

def assert_mean_is_length(cov):
    """Gate — mean relator length and total length induce the SAME top-3, on every row.

    Not an argument, a check: with two relators mean = total / 2, so the proposal's two
    orderings are one ordering. If a three-relator row ever enters this sweep, this fires.
    """
    a = rank_arm(cov, ARMS["abel_mean_len"])
    b = rank_arm(cov, ARMS["abel_len_mean"])
    c = rank_arm(cov, ARMS["abel_len_lex"])
    diff = [p for p in cov if [_id(d) for d in a[p][:K]] != [_id(d) for d in b[p][:K]]]
    assert not diff, f"mean-first and length-first differ on {diff} — check n_relators"
    same_as_lex = sum(1 for p in cov
                      if [_id(d) for d in a[p][:K]] == [_id(d) for d in c[p][:K]])
    return len(cov), same_as_lex


# ------------------------------------------------------------------------ scoring

def score(cov, key):
    ranked = rank_arm(cov, key)
    hits = {p for p in cov if R.solves_within(ranked[p], K)}
    return {
        "ranked": ranked,
        "hits": hits,
        "hits_at": {k: {p for p in cov if R.solves_within(ranked[p], k)} for k in KS},
        "at_k": {k: len({p for p in cov if R.solves_within(ranked[p], k)}) for k in KS},
        "first_solve": {p: first_solve_nodes(ranked[p]) for p in hits},
        "deployed": {p: deployed_nodes(ranked[p]) for p in cov},
        "deployed_total": sum(deployed_nodes(ranked[p]) for p in cov),
        "k1_first_solve": {p: first_solve_nodes(ranked[p], 1) for p in cov
                           if first_solve_nodes(ranked[p], 1) is not None},
        "ident_topk": sum(1 for p in cov if ident_decided(ranked[p])),
        "ident_rank1": sum(1 for p in cov if rank1_tied(ranked[p])),
    }


def paired(a, b):
    """Paired cost comparison on the presentations BOTH arms solve — the only fair set."""
    both = sorted(a["hits"] & b["hits"])
    da = [a["first_solve"][p] for p in both]
    db = [b["first_solve"][p] for p in both]
    win = sum(1 for x, y in zip(da, db) if x < y)
    loss = sum(1 for x, y in zip(da, db) if x > y)
    return {
        "n": len(both),
        "a_mean": statistics.mean(da) if da else 0.0,
        "b_mean": statistics.mean(db) if db else 0.0,
        "a_median": statistics.median(da) if da else 0.0,
        "b_median": statistics.median(db) if db else 0.0,
        "a_total": sum(da), "b_total": sum(db),
        "win": win, "tie": len(both) - win - loss, "loss": loss,
        "diff": [(p, a["first_solve"][p] - b["first_solve"][p]) for p in both
                 if a["first_solve"][p] != b["first_solve"][p]],
    }


def _stat(s, field="first_solve"):
    v = sorted(s[field].values())
    if not v:
        return 0, 0.0, 0.0, 0
    return len(v), statistics.mean(v), statistics.median(v), max(v)


def discrimination(cov):
    """How many candidates survive each key chain tied at its minimum — the tie the next key
    has to break. A key that leaves a median of 1 has nothing left to give."""
    out = {}
    for name, keyf in CHAINS.items():
        counts = []
        for v in cov.values():
            ks = [keyf(d) for d in v]
            m = min(ks)
            counts.append(sum(1 for k in ks if k == m))
        out[name] = (statistics.median(counts), statistics.mean(counts),
                     sum(1 for c in counts if c == 1), max(counts))
    return out


# -------------------------------------------------------------------------- load

def load_sweep(path, keep=None):
    """Candidate rows per presentation from any covsweep jsonl, controls split out."""
    cov, ctl = defaultdict(list), {}
    with open(os.path.join(ROOT, path)) as fh:
        for line in fh:
            d = json.loads(line)
            if keep is not None and d["pres_id"] not in keep:
                continue
            if d.get("n_cov", 0) == 0:
                ctl[d["pres_id"]] = d
            else:
                cov[d["pres_id"]].append(d)
    leaks = sum(1 for v in cov.values() for d in v
                if len(d["r1"]) + len(d["r2"]) != d["start_total_length_cov"])
    assert leaks == 0, f"{leaks} rows in {path} where r1/r2 is not the start"
    return dict(cov), ctl


def main():
    n_rows = R.gate_truncation()
    ids60, bins, auts, cov, control = R.load()
    oracle = R.oracle_set(cov)
    greedy_hits = {p for p, c in control.items() if c["solved"]}
    n_pres, mean_eq_lex = assert_mean_is_length(cov)

    S = {name: score(cov, key) for name, key in ARMS.items()}
    A, B = HEADLINE
    pr = paired(S[A], S[B])
    only_a, only_b, p_mc = R.mcnemar(S[A]["hits"], S[B]["hits"])
    vs_inc = {n: paired(S[n], S["abel_len_lex"]) for n in ARMS}
    vs_abel = {n: paired(S[n], S["abel"]) for n in ARMS}
    disc = discrimination(cov)

    # free robustness check: the same arms on the 10,000-node twin of this sweep
    cov10, ctl10 = load_sweep(R.SWEEP_10K, set(ids60))
    S10 = {name: score(cov10, key) for name, key in ARMS.items()}
    oracle10 = R.oracle_set(cov10)
    greedy10 = {p for p, c in ctl10.items() if c["solved"]}
    pr10 = paired(S10[A], S10[B])

    # the held-out 124 — reported as untestable, with the number that makes it so
    cov124, _ = load_sweep(HELDOUT)
    oracle124 = R.oracle_set(cov124)

    rows = []
    for p in ids60:
        row = {"pres_id": p, "bin": bins[p], "aut_class": auts[p], "n_cand": len(cov[p]),
               "n_solving_cand": sum(1 for d in cov[p] if d["solved"]),
               "oracle": int(p in oracle), "greedy_b1k": int(p in greedy_hits)}
        for name in ARMS:
            s = S[name]
            row[f"{name}_solved"] = int(p in s["hits"])
            row[f"{name}_first_solve"] = s["first_solve"].get(p, "")
            row[f"{name}_deployed"] = s["deployed"][p]
        rows.append(row)
    with open(os.path.join(ROOT, OUT_CSV), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def line(name, sc):
        s = sc[name]
        _, mean, med, mx = _stat(s)
        return (f"| `{name}` | {s['at_k'][1]} | {s['at_k'][2]} | **{s['at_k'][3]}** | "
                f"{med:,.0f} | {mean:,.1f} | {mx:,} | {s['deployed_total']:,} | "
                f"{s['ident_rank1']} | {s['ident_topk']} |")

    arms1k = "\n".join(line(n, S) for n in ARMS)
    arms10k = "\n".join(line(n, S10) for n in ARMS)
    disc_tbl = "\n".join(
        f"| `{n}` | {v[0]:,.0f} | {v[1]:.2f} | {v[2]}/{n_pres} | {v[3]} |"
        for n, v in disc.items())
    k1_tbl = "\n".join(
        f"| `{n}` | {S[n]['at_k'][1]} | {statistics.mean(S[n]['k1_first_solve'].values()):,.1f} "
        f"| {S10[n]['at_k'][1]} | {statistics.mean(S10[n]['k1_first_solve'].values()):,.1f} |"
        for n in ARMS)

    dead_heat = (pr["win"] + pr["loss"] <= 1 and len(only_a) == len(only_b) == 0)
    verdict = ("**a dead heat**" if dead_heat else
               f"**`{A if pr['a_mean'] < pr['b_mean'] else B}`**")

    md = f"""# The abel tie-break at budget 1,000: shorter relator, or shorter total?

**Zero search nodes.** A re-ranking of the frozen `{R.SWEEP}` through `abel_topk_cov_b1k`'s gated loader ({n_rows:,} rows checked by its truncation gate), subset-60, top {K}, budget 1,000 — plus the same arms on the 10,000-node twin of that sweep, which costs nothing because gate 1 already opens it.

## Verdict

**Neither ordering outperforms.** `{A}` and `{B}` solve the same {S[A]['at_k'][3]}/60 at top {K}, the same {S[A]['at_k'][1]}/60 at rank 1, and differ on **{pr['win'] + pr['loss']} of the {pr['n']} presentations both solve, by {abs(pr['a_total'] - pr['b_total'])} nodes out of {pr['a_total']:,}** ({abs(pr['a_total'] - pr['b_total']) / pr['a_total'] * 100:.2f}%). Exact paired p on discordant solves = {p_mc:.3f}. At budget 10,000 the same two arms differ on {pr10['win'] + pr10['loss']} of {pr10['n']} rows and {abs(pr10['a_total'] - pr10['b_total'])} nodes. The head-to-head is {verdict}.

What the run *does* separate is whether `min(|r1|,|r2|)` carries signal the total length does not — and at fixed `abel`, **it does not**. As a sole second key it discriminates strictly less than the total (a unique pick on {disc['abel + min'][2]}/60 against {disc['abel + total'][2]}/60), and adding min anywhere in the chain — before the total or after it — moves the whole bill by at most {max(abs(S['abel_min_len']['deployed_total'] - S['abel_mean_len']['deployed_total']), abs(S['abel_len_min']['deployed_total'] - S['abel_mean_len']['deployed_total']))} nodes in {S['abel_mean_len']['deployed_total']:,}. The recommendation stays `(abel, total length)`; min does not earn a slot.

## The proposal as worded is one arm, not two

Every candidate in this sweep is a **two**-relator pair, so mean relator length = total / 2 — a strictly monotone function of total length and therefore the identical ordering. `(abel, mean, total)` and `(abel, total, mean)` produce **the same top {K} on all {n_pres} presentations** (checked, not argued: `assert_mean_is_length`), and both coincide with the incumbent `(abel, total, longest)` on {mean_eq_lex}/{n_pres}. So the substantive contrast is `min(|r1|, |r2|)`, which is not a function of the total.

That intuition was earned by `min_relator_length` as a **search progress** signal. The key here reads `min(len(r1), len(r2))` off the **start** pair, before a node is popped; the anti-leak gate exists so no key can reach the search-derived column. Same word, different object.

## Every arm at top {K}, budget 1,000

| arm | k=1 | k=2 | **k=3** | median | mean | max | deployed total | rank-1 ties | top-3 ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{arms1k}

Median/mean/max are `first_solve_nodes` over that arm's own solved set, so in general they are not comparable across arms; here they happen to be, because every `abel`-first arm turns out to solve the **same** {S['abel']['at_k'][3]} presentations at k={K}. That is a measured coincidence, not a guarantee — the arms disagree on the top-{K} *set* on up to {sum(1 for p in cov if {_id(d) for d in S['abel_min_len']['ranked'][p][:K]} != {_id(d) for d in S['abel_len_lex']['ranked'][p][:K]})} of 60 presentations, and a different set could have reached a different presentation. The paired sections below are the comparison that does not rely on it. `deployed total` is the whole bill over all 60 (a presentation no rank solves costs the full {K} × 1,000). The last two columns count presentations where the ordered keys run out and `_ident` picks.

Reference points at this budget: the best-CoV **oracle is {len(oracle)}/60**, plain greedy on the untransformed pair is **{len(greedy_hits)}/60**, and the incumbent `abel_len_lex` is {S['abel_len_lex']['at_k'][3]}/60. The solve column has {len(oracle) - S['abel']['at_k'][3]} rows of headroom above bare `abel` and none above the oracle, so it is saturated by construction — read the cost columns.

## The head-to-head

`{A}` against `{B}`, paired on the {pr['n']} presentations both solve:

| | `{A}` | `{B}` |
|---|---:|---:|
| solved / 60 at k=3 | {S[A]['at_k'][3]} | {S[B]['at_k'][3]} |
| solved / 60 at k=1 | {S[A]['at_k'][1]} | {S[B]['at_k'][1]} |
| median nodes | {pr['a_median']:,.0f} | {pr['b_median']:,.0f} |
| mean nodes | {pr['a_mean']:,.1f} | {pr['b_mean']:,.1f} |
| total nodes | {pr['a_total']:,} | {pr['b_total']:,} |

Cheaper on {pr['win']}, tied on {pr['tie']}, dearer on {pr['loss']}; solve-count discordance {len(only_a)}–{len(only_b)}, exact p = {p_mc:.3f}. The differing rows are `{pr['diff']}` (pres_id, `{A}` − `{B}`).

Each arm against the incumbent `abel_len_lex`, same paired rule:

| arm | n both | arm mean | `abel_len_lex` mean | arm total | incumbent total | cheaper / tied / dearer |
|---|---:|---:|---:|---:|---:|---|
""" + "\n".join(
        f"| `{n}` | {vs_inc[n]['n']} | {vs_inc[n]['a_mean']:,.1f} | {vs_inc[n]['b_mean']:,.1f} | "
        f"{vs_inc[n]['a_total']:,} | {vs_inc[n]['b_total']:,} | "
        f"{vs_inc[n]['win']} / {vs_inc[n]['tie']} / {vs_inc[n]['loss']} |"
        for n in ("abel", "abel_mean_len", "abel_min_len", "abel_len_min", "abel_min")) + f"""

The {abs(vs_inc['abel_mean_len']['a_total'] - vs_inc['abel_mean_len']['b_total']):,}-node gap over the incumbent is **one presentation**, not a distribution: the win/tie/loss column is {vs_inc['abel_mean_len']['win']}/{vs_inc['abel_mean_len']['tie']}/{vs_inc['abel_mean_len']['loss']}. `longest` as the third key sends one rank-1 pick into a search that burns the whole budget; `total` and `min` both avoid it.

## How much tie is left for each key to break

| key chain | median candidates tied at the minimum | mean | collapses to one pick | worst |
|---|---:|---:|---:|---:|
{disc_tbl}

`abel` alone decides a unique pick on {disc['abel'][2]}/{n_pres}. Total length is the stronger second key ({disc['abel + total'][2]}/{n_pres} unique against min's {disc['abel + min'][2]}/{n_pres}), and the two together reach {disc['abel + min + total'][2]}/{n_pres} — so **{n_pres - disc['abel + min + total'][2]} of 60 presentations still need a further key after all three**, and with two relators `max = total − min` means no length feature is left. That residue is what `_ident` decides today, and the ms640 census already says what it should be spent on instead: a **Booth-canonical dedup of the candidate list before the top {K} is taken**, not a fourth sort key — canonically identical candidates carry equal keys, sort adjacent, and both enter the top {K} either way. No dedup is applied here, deliberately, so these numbers stay comparable to the incumbent {S['abel_len_lex']['at_k'][3]}/60.

## Rank 1 alone, and why the 1,000-node margin does not survive a budget change

| arm | k=1 solved @1,000 | k=1 mean nodes @1,000 | k=1 solved @10,000 | k=1 mean nodes @10,000 |
|---|---:|---:|---:|---:|
{k1_tbl}

Each mean is over that arm's **own** k=1 solved set, so an arm that solves more rows can carry a higher mean by picking up expensive ones — bare `abel`'s {statistics.mean(S['abel']['k1_first_solve'].values()):,.1f} at 1,000 is over {S['abel']['at_k'][1]} rows against the length-keyed arms' {S['abel_mean_len']['at_k'][1]}. At budget 1,000 any length-bearing second key is worth **+{S['abel_mean_len']['at_k'][1] - S['abel']['at_k'][1]} presentations at rank 1** over bare `abel` ({S['abel']['at_k'][1]} → {S['abel_mean_len']['at_k'][1]}) and cuts the top-3 mean from {_stat(S['abel'])[1]:,.1f} to {_stat(S['abel_mean_len'])[1]:,.1f} nodes. At budget 10,000 it goes the other way: bare `abel` reaches {S10['abel']['at_k'][1]}/60 at rank 1 and every length-keyed arm reaches {S10['abel_mean_len']['at_k'][1]}, with a *higher* top-3 mean ({_stat(S10['abel_mean_len'])[1]:,.1f} against {_stat(S10['abel'])[1]:,.1f}).

| arm | k=1 | k=2 | **k=3** | median | mean | max | deployed total | rank-1 ties | top-3 ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{arms10k}

Oracle {len(oracle10)}/60, plain greedy {len(greedy10)}/60 at 10,000. Both budgets are the same 60 presentations and the same {sum(len(v) for v in cov.values()):,} candidates — only the solved flags move — so this is a budget-robustness check on one frozen sweep, not a second experiment. What it establishes is negative and worth stating: **a one-or-two-row margin on subset-60 is not a property of the key.** The powered evidence for `(abel, total)` is the ms640 census — 640 presentations at budget 100,000, where re-scoring the searched top 3 under `(abel, length, lex)` came to 420,419 nodes against `_ident`'s 458,688 — not this file.

## The held-out set cannot test this

`{HELDOUT}` covers the 124 unsolved representatives at budget 50,000, and **{len(oracle124)} of its {len(cov124)} presentations have any solving CoV candidate at all**. Every arm scores zero, so it separates nothing. That is the repo's own [control-with-no-dynamic-range](../../experiments/lessons/control-with-no-dynamic-range.md) shape, and it is why the honest scope of this comparison is subset-60.

## Source

- Sweep: `{R.SWEEP}` (cross-checked against `{R.SWEEP_10K}` by gate 1)
- Table: [`abel_tiebreak_b1k_subset60.csv`](abel_tiebreak_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_tiebreak_b1k.py` (`python3 -m experiments.heuristic_search.runners.abel_tiebreak_b1k`)
- Incumbent numbers it is read against: [`ABEL_TOPK_COV_B1K.md`](ABEL_TOPK_COV_B1K.md)
"""
    with open(os.path.join(ROOT, OUT_MD), "w") as fh:
        fh.write(md)

    print(f"rows gated {n_rows:,} | pres {n_pres} | oracle@1k {len(oracle)} "
          f"| greedy@1k {len(greedy_hits)} | oracle@10k {len(oracle10)} "
          f"| held-out 124 oracle {len(oracle124)}")
    print(f"mean-first == length-first on all {n_pres}: OK "
          f"(== abel_len_lex on {mean_eq_lex}/{n_pres})")
    hdr = (f"{'arm':<15}{'k1':>4}{'k2':>4}{'k3':>4}{'median':>8}{'mean':>10}{'max':>8}"
           f"{'deployed':>11}{'tie1':>6}{'tie3':>6}")
    for label, sc in (("budget 1,000", S), ("budget 10,000", S10)):
        print(f"\n--- {label} ---\n{hdr}")
        for name in ARMS:
            s = sc[name]
            _, mean, med, mx = _stat(s)
            print(f"{name:<15}{s['at_k'][1]:>4}{s['at_k'][2]:>4}{s['at_k'][3]:>4}"
                  f"{med:>8,.0f}{mean:>10,.1f}{mx:>8,}{s['deployed_total']:>11,}"
                  f"{s['ident_rank1']:>6}{s['ident_topk']:>6}")
    for label, q in (("@1k", pr), ("@10k", pr10)):
        print(f"\npaired {A} vs {B} {label}: n={q['n']} mean {q['a_mean']:,.1f} vs "
              f"{q['b_mean']:,.1f} | median {q['a_median']:,.0f} vs {q['b_median']:,.0f} | "
              f"total {q['a_total']:,} vs {q['b_total']:,} | w/t/l "
              f"{q['win']}/{q['tie']}/{q['loss']} | diff {q['diff']}")
    print(f"\ndiscrimination: " + " | ".join(
        f"{n} med {v[0]:.0f} uniq {v[2]}/{n_pres}" for n, v in disc.items()))
    print(f"\nwrote {OUT_MD} and {OUT_CSV}")


if __name__ == "__main__":
    main()
