"""Which tie-break does the abelianized-magnitude key want second — length, or ``S``?

**Zero search nodes.** Every number here is a re-ranking of the frozen
``covsweep_1000_66_*.jsonl`` (and, as a free robustness check, its 10,000-node twin) through
``abel_topk_cov_b1k``'s own gated loader, so the candidate set, the anti-leak gate and the
truncation gate are the ones that already carry the incumbent numbers. No solver is called;
nothing here can exceed the local budget cap.

## The question

``abel`` alone is a filter, not a ranking: it leaves a median of 6 candidates tied at its
minimum on subset-60 and collapses to a unique pick on only 7 of 60. Something has to break
that tie, and the ordering the tuned heuristic already trusts most is ``S`` — the
**smallest mean block**, ``hlab.FEATURES[7]``, the mean run length of the thinner generator
read cyclically over both relators. It carries the largest weight in
``hsolve.RECOMMENDED`` (8.458, against ``L``'s 1.0), which is the reason to try it here.

| arm | key |
|---|---|
| ``abel_S_len`` | ``(abel, S, |r1|+|r2|)`` — smallest mean block first |
| ``abel_len_S`` | ``(abel, |r1|+|r2|, S)`` — total length first |

Both then fall through to ``_ident`` (the CoV's own name) for determinism.

## Three keys that are not ``S``, kept because they were asked for first

- **Mean relator length is total length.** Every candidate here is a **two**-relator pair, so
  ``mean = total / 2`` — a strictly monotone function of the total, hence the identical
  ordering. ``assert_mean_is_length`` proves it on all 60 rather than arguing it.
- **``Lmin``** = ``min(|r1|, |r2|)``, ``hlab.FEATURES[1]`` — the shorter *relator*, which is
  what "min of min relator length" reads as if ``S`` is not meant. It is genuinely not a
  function of the total, so it is measured, and it comes out a dead heat with the total.
- **``max = total - Lmin``**, so once ``abel``, ``Lmin`` and the total are fixed there is no
  further *length* information to spend. That is why the sweep below leaves length behind and
  ranges over the whole 17-feature vocabulary.

## These are start features, not the search's progress signals

``S`` and ``Lmin`` earn their weights inside ``hsolve``/``hfast`` as **climb** features,
re-evaluated at every node of a running search, where they measure progress. Here they are
read off the **start** pair, before a node is popped — the anti-leak gate in
``abel_topk_cov_b1k.load`` exists precisely so no key can reach the search-derived
``min_relator``/``min_relator_length`` columns. Same features, a different object: a result
here is evidence about *start ranking*, and neither confirms nor refutes the heap ordering.

## The second-key sweep

Since a key costs nothing to evaluate, ``second_key_sweep`` scores **every** one of the 17
features in both positions — ``(abel, f, total)`` and ``(abel, total, f)`` — plus ``reco``,
the full ``RECOMMENDED`` linear score used as a single key. That is the empirical answer to
"if it is a tie, use something else": the something else is enumerated, not argued.

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
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    canonical_pair_nj, reduce_relator_nj, str_to_arr,
)

ROOT = R.ROOT
K = 3
KS = (1, 2, 3)
HELDOUT = ("results/stable_ac/cov/"
           "covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl")
OUT_CSV = "results/comparison/abel_tiebreak_b1k_subset60.csv"
OUT_MD = "results/comparison/ABEL_TIEBREAK_B1K.md"


# --------------------------------------------------------------------------- keys

_FIDX = {f: i for i, f in enumerate(FEATURES)}
_RECO_W = RECOMMENDED["segments"][0]["w"]


def _feat(name):
    """A ranking key that reads one ``hlab`` feature off the START pair. ``phi`` caches."""
    i = _FIDX[name]
    return lambda d: phi(d["r1"], d["r2"])[i]


def _reco(d):
    """``hsolve.RECOMMENDED``'s own linear score, as a single ranking key."""
    v = phi(d["r1"], d["r2"])
    return sum(w * v[_FIDX[k]] for k, w in _RECO_W.items())


_S = _feat("S")          # smallest mean block — the heuristic's heaviest weight
_LMIN = _feat("Lmin")    # length of the shorter relator
_MK = _feat("MK")        # max knots over the two relators


def _s20mk2(d):
    """``L + 20*S + 2*MK`` — the ``s20_mk2`` heap ordering, used here as a START key.

    The arm that ran the ac19 hard-100k A/B (``results/heuristic_search/hsearch_ac19_hard100k``)
    and the one the ``S`` grid in ``results/comparison/S_B1K.md`` peaks near. Scored here
    because it is the composite that was actually named, not a feature of it.
    """
    v = phi(d["r1"], d["r2"])
    return v[_FIDX["L"]] + 20.0 * v[_FIDX["S"]] + 2.0 * v[_FIDX["MK"]]


def _minrel(d):
    """The shorter of the two START relators. Never the row's search-derived min_relator.

    Identical to ``_LMIN`` by construction; kept as its own definition because the arms named
    ``*_min*`` predate the sweep and ``assert_lmin_is_minrel`` pins the two against each other.
    """
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
    # the heuristic's own heaviest feature, in both positions and alone
    "abel_S_len":    lambda d: (_abel(d), _S(d), R._start_len(d)),
    "abel_len_S":    lambda d: (_abel(d), R._start_len(d), _S(d)),
    "abel_S":        lambda d: (_abel(d), _S(d)),
    "S_only":        lambda d: (_S(d),),
    # the composite the S weight actually ships inside: L + 20*S + 2*MK
    "abel_s20mk2":   lambda d: (_abel(d), _s20mk2(d)),
    "abel_len_s20mk2": lambda d: (_abel(d), R._start_len(d), _s20mk2(d)),
    "s20mk2_only":   lambda d: (_s20mk2(d),),
}

HEADLINE = ("abel_S_len", "abel_len_S")

# the key chains, for the discrimination table: how much of the tie each one actually breaks
CHAINS = {
    "abel":               lambda d: (_abel(d),),
    "abel + min":         lambda d: (_abel(d), _minrel(d)),
    "abel + total":       lambda d: (_abel(d), R._start_len(d)),
    "abel + min + total": lambda d: (_abel(d), _minrel(d), R._start_len(d)),
    "abel + total + longest": lambda d: (_abel(d), R._start_len(d), R._longest(d)),
    "abel + S": lambda d: (_abel(d), _S(d)),
    "abel + S + total": lambda d: (_abel(d), _S(d), R._start_len(d)),
    "abel + reco": lambda d: (_abel(d), _reco(d)),
    "abel + s20mk2": lambda d: (_abel(d), _s20mk2(d)),
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


def assert_lmin_is_minrel(cov):
    """Gate — the ``*_min*`` arms rank on exactly ``hlab``'s ``Lmin``, not a lookalike.

    Two definitions of "the shorter relator" are in play (this file's ``_minrel`` and the
    feature table's index 1); if they ever diverge, the sweep row labelled ``Lmin`` and the
    arms labelled ``min`` would silently be measuring different keys.
    """
    bad = [(p, d["r1"], d["r2"]) for p, v in cov.items() for d in v
           if float(_minrel(d)) != _LMIN(d)]
    assert not bad, f"_minrel != FEATURES['Lmin'] on {len(bad)} rows, e.g. {bad[0]}"
    return True


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


def canon_pair(d):
    """The pair the SOLVER would start from — Booth lex-min, order-normalised.

    Two candidates with the same value here are not similar, they are the same search: same
    pops, same ``nodes_explored``, same outcome. This is the equivalence a top-k list wastes a
    slot on when it takes both.
    """
    a = reduce_relator_nj(str_to_arr(d["r1"]), True)
    b = reduce_relator_nj(str_to_arr(d["r2"]), True)
    c1, c2 = canonical_pair_nj(a, b)
    return c1.tobytes(), c2.tobytes()


def tie_residue(cov, key):
    """What is actually left in the tie at ``key``'s minimum, and whether the pick can matter.

    ``homog`` splits the tied sets by outcome: a set where every member solves, or none does,
    cannot be improved by any tie-break — the choice is between identical outcomes. Only a
    ``mixed`` set is a decision.
    """
    tied, n_cand, n_canon, collapse = [], 0, 0, 0
    homog_all, homog_none, mixed = 0, 0, []
    for p, v in cov.items():
        m = min(key(d) for d in v)
        t = [d for d in v if key(d) == m]
        if len(t) == 1:
            continue
        tied.append(p)
        n_cand += len(t)
        n_canon += len({canon_pair(d) for d in t})
        collapse += len({canon_pair(d) for d in t}) == 1
        ns = sum(1 for d in t if d["solved"])
        if ns == len(t):
            homog_all += 1
        elif ns == 0:
            homog_none += 1
        else:
            mixed.append((p, len(t), ns, min(d["nodes_explored"] for d in t),
                          max(d["nodes_explored"] for d in t)))
    return {"n_tied": len(tied), "n_cand": n_cand, "n_canon": n_canon, "collapse": collapse,
            "homog_all": homog_all, "homog_none": homog_none, "mixed": mixed}


def dedup_rank(cov, key):
    """Rank by ``key``, then drop every candidate whose canonical pair already appeared.

    The top k is then k *distinct searches*. This is the intervention the ms640 write-up
    proposed for the residue; ``main`` prices it rather than assuming it helps.
    """
    out = {}
    for p, v in cov.items():
        for d in v:
            d["_key"] = key(d)
        seen, keep = set(), []
        for d in sorted(v, key=lambda d: d["_key"] + R._ident(d)):
            c = canon_pair(d)
            if c in seen:
                continue
            seen.add(c)
            keep.append(d)
        out[p] = keep
    return out


def score_ranked(ranked, cov):
    """``score`` for an already-ranked dict (``dedup_rank``'s output)."""
    hits = {p for p in cov if R.solves_within(ranked[p], K)}
    return {"ranked": ranked, "hits": hits,
            "hits_at": {k: {p for p in cov if R.solves_within(ranked[p], k)} for k in KS},
            "at_k": {k: len({p for p in cov if R.solves_within(ranked[p], k)}) for k in KS},
            "first_solve": {p: first_solve_nodes(ranked[p]) for p in hits},
            "deployed": {p: deployed_nodes(ranked[p]) for p in cov},
            "deployed_total": sum(deployed_nodes(ranked[p]) for p in cov),
            "k1_first_solve": {p: first_solve_nodes(ranked[p], 1) for p in cov
                               if first_solve_nodes(ranked[p], 1) is not None},
            "ident_topk": 0, "ident_rank1": 0}


def slot_waste(ranked, cov):
    """Top-k slots spent re-running a search an earlier rank already ran."""
    lists = sum(1 for p in cov
                if len({canon_pair(d) for d in ranked[p][:K]}) < min(K, len(ranked[p])))
    slots = sum(min(K, len(ranked[p])) - len({canon_pair(d) for d in ranked[p][:K]})
                for p in cov)
    return lists, slots


def solve_rank_curve(ranked, cov):
    """Rank of the first solving candidate — how large k would have to be, and for whom."""
    ranks = {}
    for p in cov:
        i = next((i + 1 for i, d in enumerate(ranked[p]) if d["solved"]), None)
        if i:
            ranks[p] = i
    curve = {k: sum(1 for r in ranks.values() if r <= k) for k in (1, 2, 3, 5, 10, 25, 50)}
    beyond = sorted((p, r, ranked[p][r - 1]["nodes_explored"], len(ranked[p]))
                    for p, r in ranks.items() if r > K)
    return ranks, curve, beyond


def abel_offset(cov):
    """For each solvable presentation, abel(first solving candidate) - min abel over the family.

    0 means the abelian filter's own minimum shell contains a solving start; 1 means the
    solving start is one step above it and the primary key ranks it below every member of a
    shell that never solves.
    """
    out = {}
    for p, v in cov.items():
        sol = [d for d in v if d["solved"]]
        if not sol:
            continue
        m = min(_abel(d) for d in v)
        w = min(sol, key=lambda d: (_abel(d), R._start_len(d)) + R._ident(d))
        out[p] = _abel(w) - m
    return out


def class_quota(cov, quota):
    """Take ``quota[i]`` candidates from the i-th lowest abel shell, shortest first.

    A diversification control for the offset finding: if the misses are a shell problem,
    reserving a slot for the next shell should recover them.
    """
    out = {}
    for p, v in cov.items():
        shells = defaultdict(list)
        for d in v:
            shells[_abel(d)].append(d)
        pick = []
        for i, a in enumerate(sorted(shells)):
            n = quota[i] if i < len(quota) else 0
            pick += sorted(shells[a], key=lambda d: (R._start_len(d),) + R._ident(d))[:n]
        out[p] = pick
    return out


def second_key_sweep(cov):
    """Every feature as the second key, in both positions. Zero search nodes, so exhaustive.

    ``before`` is ``(abel, f, total)`` — f overrides length. ``after`` is ``(abel, total, f)``
    — f only breaks what length left tied. ``uniq`` is how often ``(abel, f)`` alone reaches a
    single candidate, i.e. how much of the abel tie f can break on its own.
    """
    out = []
    for name in list(FEATURES) + ["reco", "s20_mk2"]:
        f = {"reco": _reco, "s20_mk2": _s20mk2}.get(name) or _feat(name)
        before = score(cov, lambda d, f=f: (_abel(d), f(d), R._start_len(d)))
        after = score(cov, lambda d, f=f: (_abel(d), R._start_len(d), f(d)))
        uniq = 0
        for v in cov.values():
            ks = [(_abel(d), f(d)) for d in v]
            m = min(ks)
            uniq += sum(1 for k in ks if k == m) == 1
        out.append((name, before, after, uniq))
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
    assert_lmin_is_minrel(cov)

    S = {name: score(cov, key) for name, key in ARMS.items()}
    A, B = HEADLINE
    pr = paired(S[A], S[B])
    only_a, only_b, p_mc = R.mcnemar(S[A]["hits"], S[B]["hits"])
    vs_inc = {n: paired(S[n], S["abel_len_lex"]) for n in ARMS}
    vs_abel = {n: paired(S[n], S["abel"]) for n in ARMS}
    disc = discrimination(cov)
    sweep = second_key_sweep(cov)

    # what is left in the tie after (abel, total), and whether anything can be done with it
    AT = ARMS["abel_mean_len"]              # (abel, total, mean) == (abel, total)
    TOTKEY = lambda d: (_abel(d), R._start_len(d))          # noqa: E731
    resid = tie_residue(cov, TOTKEY)
    dd = score_ranked(dedup_rank(cov, TOTKEY), cov)
    waste_lists, waste_slots = slot_waste(S["abel_mean_len"]["ranked"], cov)
    pr_dd = paired(dd, S["abel_mean_len"])
    _, curve, beyond = solve_rank_curve(S["abel_mean_len"]["ranked"], cov)
    offs = abel_offset(cov)
    off_hist = {o: sum(1 for x in offs.values() if x == o) for o in sorted(set(offs.values()))}
    QUOTAS = ((K,), (K - 1, 1), (1, 1, 1))
    quota_res = [(q, score_ranked(class_quota(cov, q), cov)) for q in QUOTAS]

    # free robustness check: the same arms on the 10,000-node twin of this sweep
    cov10, ctl10 = load_sweep(R.SWEEP_10K, set(ids60))
    S10 = {name: score(cov10, key) for name, key in ARMS.items()}
    oracle10 = R.oracle_set(cov10)
    greedy10 = {p for p, c in ctl10.items() if c["solved"]}
    pr10 = paired(S10[A], S10[B])
    dd10 = score_ranked(dedup_rank(cov10, TOTKEY), cov10)
    pr_dd10 = paired(dd10, S10["abel_mean_len"])

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
    winner = A if pr["a_mean"] < pr["b_mean"] else B
    verdict = "**a dead heat**" if dead_heat else f"a win for **`{winner}`**"
    sweep_tbl = "\n".join(
        f"| `{n}` | {b['at_k'][1]} | {_stat(b)[1]:,.1f} | {b['deployed_total']:,} | "
        f"{a['at_k'][1]} | {_stat(a)[1]:,.1f} | {a['deployed_total']:,} | {u}/{n_pres} |"
        for n, b, a, u in sweep)
    ref_k1 = S["abel_mean_len"]["at_k"][1]      # (abel, total) — what a second key must beat
    ref_dep = S["abel_mean_len"]["deployed_total"]
    hurt = [n for n, b, _, _ in sweep if b["at_k"][1] < ref_k1]
    wreck = [n for n, b, _, _ in sweep if b["at_k"][1] <= ref_k1 - 10]
    # after length: split by whether the arm still matches (abel, total) on the rank-1 count
    aft_same = [n for n, _, a, _ in sweep if a["at_k"][1] == ref_k1]
    aft_worse = [n for n, _, a, _ in sweep if a["at_k"][1] < ref_k1]
    aft_same_span = max(abs(a["deployed_total"] - ref_dep)
                        for n, _, a, _ in sweep if a["at_k"][1] == ref_k1)
    aft_worse_cost = (min(a["deployed_total"] for n, _, a, _ in sweep
                          if a["at_k"][1] < ref_k1) - ref_dep) if aft_worse else 0
    after_span = (min(a["deployed_total"] for _, _, a, _ in sweep),
                  max(a["deployed_total"] for _, _, a, _ in sweep))

    md = f"""# The abel tie-break at budget 1,000: total length, or `S`?

**Zero search nodes.** A re-ranking of the frozen `{R.SWEEP}` through `abel_topk_cov_b1k`'s gated loader ({n_rows:,} rows checked by its truncation gate), subset-60, top {K}, budget 1,000 — plus the same arms on the 10,000-node twin of that sweep, which costs nothing because gate 1 already opens it.

## Verdict

**Total length first.** `{B}` solves **{S[B]['at_k'][1]}/60 at rank 1** against `{A}`'s {S[A]['at_k'][1]}, at a mean of **{pr['b_mean']:,.1f} nodes against {pr['a_mean']:,.1f}** paired over the {pr['n']} presentations both solve — {pr['loss']} rows dearer for `{A}`, {pr['win']} cheaper, {pr['tie']} tied. The head-to-head is {verdict}. Putting `S` *ahead* of length costs {abs(pr['a_total'] - pr['b_total']):,} nodes out of {pr['b_total']:,} ({abs(pr['a_total'] - pr['b_total']) / pr['b_total'] * 100:.0f}% more), and two of the five losses are a rank-1 pick that burns the entire budget.

`S` **behind** length is free and inert: `{B}` and the plain `(abel, total)` differ by {abs(S['abel_len_S']['deployed_total'] - S['abel_mean_len']['deployed_total'])} nodes in {S['abel_mean_len']['deployed_total']:,} on the whole bill. By the time length has been applied, `S` has almost nothing left to break — which is the finding, not a caveat.

`S` is the right feature to have suspected: it carries the heaviest weight in `hsolve.RECOMMENDED` ({_RECO_W['S']} against `L`'s {_RECO_W['L']}) and it is the `S` in `L + 20·S + 2·MK`, the ordering that ran the ac19 hard-100k A/B. But it has never been used the way a lexicographic tie-break uses it — **`s20_mk2` and `RECOMMENDED` both keep `L` inside the same expression, where it can outvote `S`**; a lexicographic first key cannot be outvoted by anything. Score the composite itself and it holds up: `(abel, L + 20·S + 2·MK)` is the joint-cheapest arm in this file at {S['abel_s20mk2']['deployed_total']:,} nodes, {S['abel_s20mk2']['at_k'][1]}/60 at rank 1, against `(abel, total)`'s {S['abel_mean_len']['deployed_total']:,} and {S['abel_mean_len']['at_k'][1]}/60 — a {abs(S['abel_s20mk2']['deployed_total'] - S['abel_mean_len']['deployed_total'])}-node difference, i.e. no difference. So the honest reading is not "`S` fails" but **"`S` adds nothing to a start ranking that already has `abel` and length, and actively hurts if given priority over length"**. Whether it earns its weight as a *climb* feature is a separate question this file cannot touch.

## Every feature as the second key, both positions

Since a key costs nothing to evaluate, every one of the 17 `hlab` features was scored in both positions, plus two composites used as one key each: `reco`, the full `RECOMMENDED` score (`{", ".join(f"{k}={v}" for k, v in _RECO_W.items())}`), and `s20_mk2` = `L + 20·S + 2·MK`, the ordering that ran the ac19 hard-100k A/B. `uniq` is how often `(abel, f)` alone reaches a single candidate.

| f | (abel, **f**, total): k=1 | mean | deployed | (abel, total, **f**): k=1 | mean | deployed | uniq |
|---|---:|---:|---:|---:|---:|---:|---:|
{sweep_tbl}

Read the two halves separately, because they say different things.

**Placed before length, not one feature beats it.** {len(hurt)} of the {len(sweep)} lose rank-1 solves against `(abel, total)`'s {ref_k1}/60 — `{"`, `".join(hurt)}` — and {len(wreck)} of those are a collapse rather than a slip: `{"`, `".join(wreck)}` fall to {min(b['at_k'][1] for _, b, _, _ in sweep)}/60 and take the bill from {ref_dep:,} to {max(b['deployed_total'] for _, b, _, _ in sweep):,} nodes. Those four are exactly the features with the *highest* `uniq` (55–58 of 60 decided outright). A key that discriminates more is not a better key; it is a key that overrides length more often, and length is the one that pays. The remaining {len(sweep) - len(hurt)} keep the full {ref_k1}/60 — and the best of them beats `(abel, total)` by {ref_dep - min(b['deployed_total'] for _, b, _, _ in sweep):,} nodes in {ref_dep:,}, which is not a result. Note *which* ones they are: the two composites (`reco`, `s20_mk2`) and the pure counts (`K`, `MK`, `mK`, `nb`, `B1`, `Bmin`). Both composites contain `L`, so putting them "ahead of length" does not actually demote length — see the section above. The counts are integers on a coarse scale that rarely separates two candidates length would have ordered differently.

**Placed after length, no feature helps and most do nothing at all.** {len(aft_same)} of {len(sweep)} keep the full {ref_k1}/60 at rank 1 and land within {aft_same_span} nodes of `(abel, total)`'s {ref_dep:,} — a spread smaller than one search on one presentation. The other {len(aft_worse)} (`{"`, `".join(aft_worse)}`) give a rank-1 solve back and cost about {aft_worse_cost:,} nodes, which is the same single presentation the incumbent's `longest` third key loses. Nothing in this vocabulary, the tuned linear score included, improves on `(abel, total length)` by a measurable amount.

One apparent exception is worth pricing, because the 10,000-node table below makes it look like a win: `abel_len_S` posts the lowest bill of any arm there ({S10['abel_len_S']['deployed_total']:,} against `(abel, total)`'s {S10['abel_mean_len']['deployed_total']:,}) and is the only length-keyed arm to reach {S10['abel_len_S']['at_k'][1]}/60 at rank 1. Paired, that is **win/tie/loss {paired(S10['abel_len_S'], S10['abel_mean_len'])['win']}/{paired(S10['abel_len_S'], S10['abel_mean_len'])['tie']}/{paired(S10['abel_len_S'], S10['abel_mean_len'])['loss']}** — one presentation (634) where `S` happens to break the tie toward a rank 1 that solves, worth the whole 10,000-node budget, against one it loses by 6 nodes. At budget 1,000 the same pair is {paired(S['abel_len_S'], S['abel_mean_len'])['win']}/{paired(S['abel_len_S'], S['abel_mean_len'])['tie']}/{paired(S['abel_len_S'], S['abel_mean_len'])['loss']}, the other way. A margin carried by one row on a 60-row set is the repo's own [gap-metric](../../experiments/lessons/gap-metric-saturates-when-the-treatment-wins.md) shape, not a reason to add a key.

## Lexicographic is not weighted — which is why `s20_mk2` survives and bare `S` does not

`S` never ships on its own. It ships inside `L + 20·S + 2·MK` (`s20_mk2`, the arm that ran the ac19 hard-100k A/B) and inside `RECOMMENDED`'s weighted sum — **always with `L` in the same expression, always able to be outvoted by it**. A lexicographic key is the opposite: whatever comes first has absolute priority, and every later key only sees the ties it left.

Scored three ways on the same 60 presentations, at budget 1,000:

| how `S` is used | rank-1 solves | deployed |
|---|---:|---:|
| lexicographic, **ahead** of length — `(abel, S, total)` | {S['abel_S_len']['at_k'][1]}/60 | {S['abel_S_len']['deployed_total']:,} |
| lexicographic, alone after `abel` — `(abel, S)` | {S['abel_S']['at_k'][1]}/60 | {S['abel_S']['deployed_total']:,} |
| lexicographic, **behind** length — `(abel, total, S)` | {S['abel_len_S']['at_k'][1]}/60 | {S['abel_len_S']['deployed_total']:,} |
| **weighted, with `L` in the sum** — `(abel, L + 20·S + 2·MK)` | {S['abel_s20mk2']['at_k'][1]}/60 | {S['abel_s20mk2']['deployed_total']:,} |
| reference — `(abel, total)` | {S['abel_mean_len']['at_k'][1]}/60 | {S['abel_mean_len']['deployed_total']:,} |

The composite is the joint-best arm in the whole file ({S['abel_s20mk2']['deployed_total']:,} nodes, {paired(S['abel_s20mk2'], S['abel_mean_len'])['win']}/{paired(S['abel_s20mk2'], S['abel_mean_len'])['tie']}/{paired(S['abel_s20mk2'], S['abel_mean_len'])['loss']} against `(abel, total)`), and the *same feature* used lexicographically ahead of length is one of the worst. That is the finding this file is actually good for: **the "before length" column below is not evidence that these features are bad, it is evidence that lexicographic priority is the wrong way to spend them.** No arm in `hsearch`/`hsolve` has ever used one that way.

The magnitudes say why. Over all {sum(len(v) for v in cov.values()):,} candidates, `L` runs {min(phi(d['r1'], d['r2'])[_FIDX['L']] for v in cov.values() for d in v):.0f}–{max(phi(d['r1'], d['r2'])[_FIDX['L']] for v in cov.values() for d in v):.0f} while the `20·S + 2·MK` term stays in a band of standard deviation {statistics.pstdev([20 * phi(d['r1'], d['r2'])[_FIDX['S']] + 2 * phi(d['r1'], d['r2'])[_FIDX['MK']] for v in cov.values() for d in v]):.1f} — big enough to reorder candidates of similar length, never big enough to put a long pair ahead of a short one. Lexicographic `S` does exactly that, on every tie.

Two honest limits on the composite. Its own 10,000-node edge over `(abel, total)` is **{paired(S10['abel_len_s20mk2'], S10['abel_mean_len'])['win']}/{paired(S10['abel_len_s20mk2'], S10['abel_mean_len'])['tie']}/{paired(S10['abel_len_s20mk2'], S10['abel_mean_len'])['loss']}** and comes from the same single presentation (634) that carries `abel_len_S`'s — one row, not a distribution. And with `abel` dropped entirely, `s20_mk2` alone ranks *worse* than length alone ({S['s20mk2_only']['at_k'][3]}/60 against {S['len_only']['at_k'][3]} at 1,000, {S10['s20mk2_only']['at_k'][3]}/60 against {S10['len_only']['at_k'][3]} at 10,000), so nothing here promotes it above the abelian filter.

## `Lmin` and "mean relator length", the two keys asked for first

Mean relator length is **not a distinct key**: every candidate is a *two*-relator pair, so mean = total / 2, a strictly monotone function of the total and therefore the identical ordering. `(abel, mean, total)` and `(abel, total, mean)` produce the same top {K} on all {n_pres} presentations — checked by `assert_mean_is_length`, not argued — and both coincide with the incumbent `(abel, total, longest)` on {mean_eq_lex}/{n_pres}.

`Lmin` = `min(|r1|, |r2|)` (`hlab.FEATURES[1]`, pinned equal to this file's `_minrel` by `assert_lmin_is_minrel`) genuinely is not a function of the total, and against it the total is **a dead heat**: `abel_min_len` and `abel_len_min` both solve {S['abel_min_len']['at_k'][3]}/60 at top {K} and {S['abel_min_len']['at_k'][1]}/60 at rank 1, differing on {paired(S['abel_min_len'], S['abel_len_min'])['win'] + paired(S['abel_min_len'], S['abel_len_min'])['loss']} of {paired(S['abel_min_len'], S['abel_len_min'])['n']} both-solved rows by {abs(paired(S['abel_min_len'], S['abel_len_min'])['a_total'] - paired(S['abel_min_len'], S['abel_len_min'])['b_total'])} nodes. `Lmin` also discriminates strictly less on its own than the total ({disc['abel + min'][2]}/60 unique against {disc['abel + total'][2]}/60). With two relators `max = total − Lmin`, so once `abel`, `Lmin` and the total are fixed there is no further *length* information anywhere — which is why the sweep above ranges over shape features instead.

## Every arm at top {K}, budget 1,000

| arm | k=1 | k=2 | **k=3** | median | mean | max | deployed total | rank-1 ties | top-3 ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{arms1k}

Median/mean/max are `first_solve_nodes` over that arm's own solved set, so they are **not** comparable across arms in general — and the last two rows are exactly where that bites: `len_only` and `S_only` drop `abel` entirely and solve {S['len_only']['at_k'][3]} and {S['S_only']['at_k'][3]} of 60, so their means are over smaller, easier sets. Among the `abel`-first arms the means happen to be comparable, because every one of them solves the **same** {S['abel']['at_k'][3]} presentations at k={K}. That is a measured coincidence, not a guarantee — the arms disagree on the top-{K} *set* on up to {sum(1 for p in cov if {_id(d) for d in S['abel_min_len']['ranked'][p][:K]} != {_id(d) for d in S['abel_len_lex']['ranked'][p][:K]})} of 60 presentations, and a different set could have reached a different presentation. The paired sections below are the comparison that does not rely on it. `deployed total` is the whole bill over all 60 (a presentation no rank solves costs the full {K} × 1,000). The last two columns count presentations where the ordered keys run out and `_ident` picks.

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
        for n in ("abel", "abel_mean_len", "abel_min_len", "abel_len_min", "abel_min",
                  "abel_S_len", "abel_len_S", "abel_S")) + f"""

The {abs(vs_inc['abel_mean_len']['a_total'] - vs_inc['abel_mean_len']['b_total']):,}-node gap over the incumbent is **one presentation**, not a distribution: the win/tie/loss column is {vs_inc['abel_mean_len']['win']}/{vs_inc['abel_mean_len']['tie']}/{vs_inc['abel_mean_len']['loss']}. `longest` as the third key sends one rank-1 pick into a search that burns the whole budget; `total` and `min` both avoid it.

## How much tie is left for each key to break

| key chain | median candidates tied at the minimum | mean | collapses to one pick | worst |
|---|---:|---:|---:|---:|
{disc_tbl}

**This column is not a scoreboard — read it against the one above.** `abel` alone decides a unique pick on {disc['abel'][2]}/{n_pres}; total length as the second key takes it to {disc['abel + total'][2]}/{n_pres}, `Lmin` to only {disc['abel + min'][2]}/{n_pres}, and `S` to {disc['abel + S'][2]}/{n_pres}. But `abel + S + total` decides **{disc['abel + S + total'][2]}/{n_pres}** — the most of any chain here, more than `abel + total + Lmin`'s {disc['abel + min + total'][2]} — and it is the arm that *loses* {S['abel_mean_len']['at_k'][1] - S['abel_S_len']['at_k'][1]} rank-1 solves and {S['abel_S_len']['deployed_total'] - S['abel_mean_len']['deployed_total']:,} nodes. `abel + reco` decides {disc['abel + reco'][2]}/{n_pres} and buys nothing. Breaking more ties is not the objective; breaking them *toward the shorter pair* is.

After `abel` and the total, **{resid['n_tied']} of 60 presentations are still tied** and — since `max = total − Lmin` — no length feature remains to supply another key. The next section asks what to do about that, and the answer is nothing.

## What to do when the tie survives: nothing

Three measurements, in the order that settles the question.

**1. Half the tie is not a tie.** The {resid['n_cand']} candidates tied at `(abel, total)`'s minimum across those {resid['n_tied']} presentations reduce to **{resid['n_canon']} distinct Booth-canonical pairs** ({100 * (1 - resid['n_canon'] / resid['n_cand']):.0f}% duplicates), and on {resid['collapse']} of the {resid['n_tied']} the whole tied set is **one** start listed several times. Two candidates with the same canonical pair are not similar starts, they are the same search: same pops, same `nodes_explored`, same outcome. Choosing between them is not a decision.

**2. Where the tie is real, it is almost always inconsequential.** Split the {resid['n_tied']} tied sets by outcome: **{resid['homog_all']}** where every member solves, **{resid['homog_none']}** where none does, and **{len(resid['mixed'])}** mixed. A homogeneous set cannot be improved by any tie-break — every choice returns the same verdict. Exactly {len(resid['mixed'])} presentation is a genuine decision: `{resid['mixed'][0][0]}`, where the tied pair splits {resid['mixed'][0][3]:,} nodes against {resid['mixed'][0][4]:,}. That is the same row that has driven every margin in this file.

**3. Deduplicating before the top {K} is free and buys nothing.** It is a real intervention, not a no-op — **{waste_lists} of 60** top-{K} lists currently spend at least one slot on a search an earlier rank already ran ({waste_slots} slots in total), and dropping the duplicates changes the top-{K} *set* on those {waste_lists} rows. The result is identical anyway:

| | k=1 | k=2 | k=3 | median | mean | deployed |
|---|---:|---:|---:|---:|---:|---:|
| `(abel, total)` top {K} | {S['abel_mean_len']['at_k'][1]} | {S['abel_mean_len']['at_k'][2]} | {S['abel_mean_len']['at_k'][3]} | {_stat(S['abel_mean_len'])[2]:,.0f} | {_stat(S['abel_mean_len'])[1]:,.1f} | {S['abel_mean_len']['deployed_total']:,} |
| + canonical dedup | {dd['at_k'][1]} | {dd['at_k'][2]} | {dd['at_k'][3]} | {_stat(dd)[2]:,.0f} | {_stat(dd)[1]:,.1f} | {dd['deployed_total']:,} |

Paired: win/tie/loss **{pr_dd['win']}/{pr_dd['tie']}/{pr_dd['loss']}** at budget 1,000 and **{pr_dd10['win']}/{pr_dd10['tie']}/{pr_dd10['loss']}** at 10,000 — not one node moves at either budget. The promoted candidates never solve where the old top {K} failed.

This is **not** a refutation of the dedup recommendation in [`cov_top3/RESULTS.md`](../stable_ac/cov/cov_top3/RESULTS.md); it is the abel-arm half of it, measured. That census found the waste is overwhelmingly a `len`-arm problem — `len` spent **325,963 nodes, 10% of its census, on 126 repeated searches**, while **abel spent 707 nodes on 38** — and it flagged its own re-score as a lower bound because it could only reorder picks already searched. This file removes that limitation (it re-ranks the whole enumerated family, so the dedup really does pull in candidates that were never in the top {K}) and finds the abel arm's gain is not merely small but **exactly zero** on all 60 rows at both budgets. So: keep the dedup, because {waste_lists}/60 lists really do waste a slot and `k` should mean *k distinct searches* — but for an `abel`-ranked arm it is hygiene, not headroom, and it must never be reported as a gain. The correction is to the first version of *this* file, which offered it as the answer to the residue on the strength of the {100 * (1 - resid['n_canon'] / resid['n_cand']):.0f}% duplicate count alone.

## Where the headroom actually is

The tie is exhausted, so the {len(oracle) - S['abel_mean_len']['at_k'][3]} rows between this arm's {S['abel_mean_len']['at_k'][3]}/60 and the oracle's {len(oracle)}/60 have to come from somewhere else. Rank of the first *solving* candidate under `(abel, total)`, over the {len(oracle)} solvable presentations:

| k | 1 | 2 | 3 | 5 | 10 | 25 | 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| solved within k | {curve[1]} | {curve[2]} | {curve[3]} | {curve[5]} | {curve[10]} | {curve[25]} | {curve[50]} |

Widening k is not the answer either: k={K} to k=5 buys **{curve[5] - curve[3]}**, and the four rows beyond k={K} sit at ranks {", ".join(str(r) for _, r, _, _ in beyond)} out of {", ".join(str(n) for *_, n in beyond)} candidates. Their solving searches cost {min(n for _, _, n, _ in beyond)}–{max(n for _, _, n, _ in beyond)} nodes — they are **cheap solves ranked far down**, so this is a primary-ranking failure, not a budget or a tie-break failure.

All four share one cause: the solving candidate sits **one abel step above the minimum** (abel 3 against the rank-1 pick's abel 2), and on two of them it is also much longer (41 and 37 against 24). Both keys point away from it. Over all {len(oracle)} solvable rows, `abel(first solving candidate) − min abel` is {" and ".join(f"**{v}** at offset {o}" for o, v in off_hist.items())} — so the abelian filter's own minimum shell is right {off_hist.get(0, 0)} times out of {len(offs)} and wrong {sum(v for o, v in off_hist.items() if o)}. The open question this file leaves is therefore **when to skip abel's minimum shell**, which is not a tie-break question.

Reserving a slot for the next shell does not answer it. Three class-quota policies, scored the same way:

| policy | k=1 | k=2 | k=3 | deployed |
|---|---:|---:|---:|---:|
""" + "\n".join(
        f"| {lbl} | {sc['at_k'][1]} | {sc['at_k'][2]} | {sc['at_k'][3]} | {sc['deployed_total']:,} |"
        for lbl, (_, sc) in zip(("all 3 from the minimum shell",
                                 "2 from the minimum + 1 from the next",
                                 "1 from each of the 3 lowest"), quota_res)) + f"""
| `(abel, total)` top {K}, for reference | {S['abel_mean_len']['at_k'][1]} | {S['abel_mean_len']['at_k'][2]} | {S['abel_mean_len']['at_k'][3]} | {S['abel_mean_len']['deployed_total']:,} |

Not one recovers a row, and the pure-shell policy *loses* one. The reason is that `(abel, total)` already spills into the next shell whenever the minimum shell holds fewer than {K} candidates, so an explicit quota is mostly a no-op — and where it is not, it displaces a rank that was solving. Whatever promotes these four is a signal not yet in the vocabulary.

## Rank 1 alone, and why the 1,000-node margin does not survive a budget change

| arm | k=1 solved @1,000 | k=1 mean nodes @1,000 | k=1 solved @10,000 | k=1 mean nodes @10,000 |
|---|---:|---:|---:|---:|
{k1_tbl}

Each mean is over that arm's **own** k=1 solved set, so an arm that solves more rows can carry a higher mean by picking up expensive ones — bare `abel`'s {statistics.mean(S['abel']['k1_first_solve'].values()):,.1f} at 1,000 is over {S['abel']['at_k'][1]} rows against the length-keyed arms' {S['abel_mean_len']['at_k'][1]}. At budget 1,000 any length-bearing second key is worth **+{S['abel_mean_len']['at_k'][1] - S['abel']['at_k'][1]} presentations at rank 1** over bare `abel` ({S['abel']['at_k'][1]} → {S['abel_mean_len']['at_k'][1]}) and cuts the top-3 mean from {_stat(S['abel'])[1]:,.1f} to {_stat(S['abel_mean_len'])[1]:,.1f} nodes. At budget 10,000 it goes the other way: bare `abel` reaches {S10['abel']['at_k'][1]}/60 at rank 1 while `(abel, total)` reaches {S10['abel_mean_len']['at_k'][1]}, with a *higher* top-3 mean ({_stat(S10['abel_mean_len'])[1]:,.1f} against {_stat(S10['abel'])[1]:,.1f}). The one length-keyed arm that still reaches {S10['abel_len_S']['at_k'][1]} there is `abel_len_S`, on the single presentation priced two sections above.

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
