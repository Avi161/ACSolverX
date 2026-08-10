"""Abelianized-magnitude top-K CoV selection vs the best-CoV oracle, at budget 1,000.

The budget-1,000 replication of ``abel_topk_cov_b10k.py``. Same key, same arms, same
subset-60, one tenth of the node budget. **Zero search nodes** — this runner re-ranks the
frozen ``covsweep_1000_66_*.jsonl``; it never calls the solver, so it is trivially inside
the repo's 1,000-node local cap.

## The question

At budget 10,000 the abelianized-magnitude key recovered the best-CoV oracle exactly
(52/60, 0 misses). That is one budget. This asks the same question at 1,000, where the
oracle itself is weaker (45/60, not 52) and the untransformed greedy control is 29/60 —
i.e. where there is more room for a ranking key to fail.

```text
abel(r1, r2) = |sigma_x(r1)| + |sigma_y(r1)| + |sigma_x(r2)| + |sigma_y(r2)|
```

Identical to ``restart_planner.abel_magnitude`` / ``IDEAS.md`` idea 1, read off the start
strings here so this file stays stdlib-only and importable without numba.

## Arms

Each arm ranks a presentation's CoV candidates, takes the top K, and counts the
presentation solved if **any** of those K solved inside its own 1,000-node budget.

| arm | rank on |
|---|---|
| ``abel`` | ``abel`` — **the headline**, pre-committed before looking at 1k |
| ``abel_len_lex`` | ``(abel, start_total_length, longest_relator)`` — the 10k headline key, reported secondary |
| ``len_only`` | ``start_total_length`` — "smallest length top 3", the control |
| ``random`` | uniform K of the candidates — the null, exact expectation + simulation |

**The headline is bare ``abel``, not ``abel_len_lex``.** The two extra tie-break fields were
chosen at budget 10,000; promoting whichever arm looks better at 1,000 would be exactly the
post-hoc selection this replication exists to rule out. ``abel_len_lex`` is reported as a
secondary row with that provenance stated.

## Gates (all fatal — the run refuses to write)

The shipped ``greedy_vs_bestcov_subset60_b10000.csv`` covers 10,000 only, so gate 1 of the
10k runner is replaced by a stronger one. Greedy search at budget ``B`` is the first ``B``
pops of any longer search, so the 1k sweep must be the 10k sweep truncated:

1. **truncation** — on all 6,788 rows, ``solved@1k == (solved@10k and nodes@10k <= 1000)``,
   with equal ``nodes_explored``, ``path_length`` and ``max_relator_length_cap`` whenever
   both solved. This validates the 1k file against an independently-run 10k file.
2. **anti-leak** — ``len(r1) + len(r2) == start_total_length_cov`` on every row, proof that
   ``r1``/``r2`` is the *start* and not a search-derived state, so no key can read the
   search. ``min_relator``/``max_relator`` are search-derived and are never read here.
3. **budget** — every row carries ``node_budget == 1000`` and ``nodes_explored <= 1000``.
4. **coverage** — subset-60 contributes exactly 60 presentations, each with >= 1 CoV
   candidate row and exactly one ``n_cov == 0`` control row.
5. **cross-implementation** — ``abel_len_lex`` top-3 must equal ``LIVE_HOP1_TOPK``, the
   ``hop1_topk`` arm of ``abel_double_cov_b1k.py``, which reached the same number by running
   live searches rather than re-reading the sweep. Two independent code paths, one number.
6. **selection honesty** — the headline's solved set is a subset of the oracle's.

    python3 -m experiments.heuristic_search.runners.abel_topk_cov_b1k
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

BUDGET = 1_000
KS = (1, 2, 3, 4, 5, 10)
HEADLINE_K = 3
N_RANDOM = 2_000
RANDOM_SEED = 20260810

# hop1_topk of results/comparison/ABEL_DOUBLE_COV_B1K.md, produced by live searches at
# budget 1000 under the same (abel, start_len, longest, z, iso_gen, iso_index) key.
LIVE_HOP1_TOPK = 41

SWEEP = ("results/stable_ac/cov/"
         "covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
SWEEP_10K = ("results/stable_ac/cov/"
             "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
SUBSET60 = "benchmark/subsets/benchmark_subset_60.csv"
OUT_CSV = "results/comparison/abel_topk_cov_b1k_subset60.csv"
OUT_MD = "results/comparison/ABEL_TOPK_COV_B1K.md"


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


# --------------------------------------------------------------------------- key

def exponent_sums(rel):
    """(sigma_x, sigma_y) of one relator string: lowercase +1, uppercase -1."""
    return (rel.count("x") - rel.count("X"), rel.count("y") - rel.count("Y"))


def abel_magnitude(r1, r2):
    """|sigma_x| + |sigma_y| over both relators — ``restart_planner.abel_magnitude``.

    A solution-DEPTH proxy (``IDEAS.md`` idea 1): strong on shallow instances, weak on the
    hard residual, blind on near-identity-abelianization presentations. A prior, never a
    guarantee.
    """
    ax, ay = exponent_sums(r1)
    bx, by = exponent_sums(r2)
    return abs(ax) + abs(ay) + abs(bx) + abs(by)


def _ident(d):
    """Deterministic, search-free identity tie-break: the CoV's own name."""
    return (d["z_word"] or "", d["iso_gen"] or "",
            d["iso_index"] if d["iso_index"] is not None else -1, d["r1"], d["r2"])


def _start_len(d):
    return len(d["r1"]) + len(d["r2"])


def _longest(d):
    return max(len(d["r1"]), len(d["r2"]))


KEYS = {
    "abel": lambda d: (abel_magnitude(d["r1"], d["r2"]),),
    "abel_len": lambda d: (abel_magnitude(d["r1"], d["r2"]), _start_len(d)),
    "abel_len_lex": lambda d: (abel_magnitude(d["r1"], d["r2"]), _start_len(d), _longest(d)),
    "len_only": lambda d: (_start_len(d),),
    "len_lex": lambda d: (_start_len(d), _longest(d)),
    # length FIRST, abel only as the tie-break: isolates what abel adds at fixed length.
    "len_then_abel": lambda d: (_start_len(d), abel_magnitude(d["r1"], d["r2"])),
}


def rank(cands, key, tie="ident"):
    """Sort ``cands`` by ``key``. ``tie`` resolves exact key ties:

    ``ident``       — the CoV's own (z, iso_gen, iso_index, r1, r2), reproducible;
    ``adversarial`` — unsolved candidates first (the arm's worst case);
    ``optimistic``  — solved candidates first (the arm's best case).
    """
    if tie == "ident":
        return sorted(cands, key=lambda d: key(d) + _ident(d))
    flag = 0 if tie == "optimistic" else 1
    return sorted(cands, key=lambda d: key(d) + (flag if d["solved"] else 1 - flag,) + _ident(d))


def solves_within(cands, k):
    return any(d["solved"] for d in cands[:k])


def cumulative_nodes(cands, k):
    """Nodes a sequential top-k trial burns before its first solve (None if none solve)."""
    total = 0
    for d in cands[:k]:
        total += d["nodes_explored"]
        if d["solved"]:
            return total
    return None


# -------------------------------------------------------------------------- load

def _split(rows, keep):
    cov, control = defaultdict(list), {}
    for d in rows:
        if d["pres_id"] not in keep:
            continue
        if d.get("n_cov", 0) == 0:
            assert d["pres_id"] not in control, f"two control rows for {d['pres_id']}"
            control[d["pres_id"]] = d
        else:
            cov[d["pres_id"]].append(d)
    return dict(cov), control


def _rowkey(d):
    return (d["pres_id"], d["r1"], d["r2"], d.get("z_word"), d.get("iso_gen"),
            d.get("iso_index"), d.get("n_cov"))


def gate_truncation():
    """Gate 1 — the 1k sweep is the 10k sweep truncated at 1,000 pops, exactly.

    Greedy search is deterministic and a budget-B run is the first B pops of any longer
    run, so this is an identity, not a correlation. It validates the 1k file against an
    independently-executed 10k file: any row where the two disagree is a bug in one of them.
    """
    a = {_rowkey(d): d for d in map(json.loads, open(os.path.join(ROOT, SWEEP)))}
    b = {_rowkey(d): d for d in map(json.loads, open(os.path.join(ROOT, SWEEP_10K)))}
    assert len(a) == len(b) and set(a) == set(b), (
        f"candidate sets differ: {len(a)} rows @1k vs {len(b)} @10k, "
        f"{len(set(a) ^ set(b))} keys unmatched")
    bad_flag = bad_nodes = bad_path = bad_cap = 0
    for k, d in a.items():
        e = b[k]
        if d["solved"] != (e["solved"] and e["nodes_explored"] <= BUDGET):
            bad_flag += 1
        if d["solved"] and e["solved"]:
            bad_nodes += d["nodes_explored"] != e["nodes_explored"]
            bad_path += d["path_length"] != e["path_length"]
        bad_cap += d["max_relator_length_cap"] != e["max_relator_length_cap"]
    assert bad_flag == 0, f"{bad_flag} rows where solved@1k != (solved@10k and nodes <= {BUDGET})"
    assert bad_nodes == 0, f"{bad_nodes} rows disagree on nodes_explored"
    assert bad_path == 0, f"{bad_path} rows disagree on path_length"
    assert bad_cap == 0, f"{bad_cap} rows disagree on max_relator_length_cap"
    return len(a)


def load():
    ids60, bins, auts = [], {}, {}
    with open(os.path.join(ROOT, SUBSET60)) as fh:
        for row in csv.DictReader(fh):
            p = int(row["pres_id"])
            ids60.append(p)
            bins[p] = int(row["bin"])
            auts[p] = int(row["aut_class"])

    keep = set(ids60)
    rows, leaks, over, wrong_budget = [], 0, 0, 0
    with open(os.path.join(ROOT, SWEEP)) as fh:
        for line in fh:
            d = json.loads(line)
            rows.append(d)
            if d["pres_id"] not in keep:
                continue
            if len(d["r1"]) + len(d["r2"]) != d["start_total_length_cov"]:
                leaks += 1
            if d["nodes_explored"] > d["node_budget"]:
                over += 1
            if d["node_budget"] != BUDGET:
                wrong_budget += 1

    # gate 2 — r1/r2 is the start, so every key is search-free
    assert leaks == 0, (f"{leaks} rows where len(r1)+len(r2) != start_total_length_cov: "
                        "r1/r2 is not the start, the ranking keys would read the search")
    # gate 3
    assert over == 0, f"{over} rows exceed their own node_budget"
    assert wrong_budget == 0, f"{wrong_budget} rows are not at node_budget {BUDGET}"

    cov, control = _split(rows, keep)
    # gate 4
    assert len(ids60) == 60, f"subset-60 has {len(ids60)} rows"
    missing = [p for p in ids60 if not cov.get(p)]
    assert not missing, f"no CoV candidate rows for {missing}"
    missing_ctl = [p for p in ids60 if p not in control]
    assert not missing_ctl, f"no untransformed control row for {missing_ctl}"

    return ids60, bins, auts, cov, control


def oracle_set(cov):
    """The best-CoV @1,000 set: any CoV row that solved. n_cov == 0 is excluded."""
    return {p for p, v in cov.items() if any(d["solved"] for d in v)}


def tenk_arms(ids60):
    """The same arms re-ranked on the frozen 10,000-node sweep — PR #14's own budget.

    PR #14 reports abel top-3 = 52 against a length-only control of 49 but never pairs them,
    so the margin's significance is unstated there. It is the identical paired structure as
    the 1k comparison, so it costs one pass over a file this module already opens for gate 1
    and it turns "the caveat probably transfers" into a measured claim.
    """
    keep = set(ids60)
    rows = []
    with open(os.path.join(ROOT, SWEEP_10K)) as fh:
        for line in fh:
            rows.append(json.loads(line))
    cov, control = _split(rows, keep)
    hits = {n: arm_hits(cov, KEYS[n], "ident", HEADLINE_K) for n in KEYS}
    greedy = {p for p, c in control.items() if c["solved"]}
    return cov, greedy, oracle_set(cov), hits, random_exact(cov)[HEADLINE_K]


# ------------------------------------------------------------------------- arms

def arm_hits(cov, key, tie, k):
    return {p for p, v in cov.items() if solves_within(rank(v, key, tie), k)}


def arm_counts(cov, key, tie):
    return {k: len(arm_hits(cov, key, tie, k)) for k in KS}


def random_exact(cov):
    """Exact expected solve count of a uniform top-K draw — no simulation noise.

    For a presentation with n candidates of which s solve, P(K uniform draws miss all of
    them) = C(n - s, K) / C(n, K), so the expectation over subset-60 is the sum of the
    complements. This is the null the abel arm has to beat.
    """
    out = {}
    for k in KS:
        tot = 0.0
        for v in cov.values():
            n = len(v)
            s = sum(1 for d in v if d["solved"])
            kk = min(k, n)
            tot += 1.0 - math.comb(n - s, kk) / math.comb(n, kk) if n - s >= kk else 1.0
        out[k] = tot
    return out


def random_arm(cov, seed=RANDOM_SEED, trials=N_RANDOM):
    """The null's distribution, plus the abel key's random-tie-break distribution.

    Two independent streams so the arms cannot correlate through a shared draw order.
    """
    r_plain = random.Random(seed)
    r_tie = random.Random(seed + 1)
    plain = {k: [] for k in KS}
    abel_tie = {k: [] for k in KS}
    len_tie = {k: [] for k in KS}
    vals = list(cov.values())
    for _ in range(trials):
        for k in KS:
            plain[k].append(sum(1 for v in vals
                                if any(d["solved"] for d in r_plain.sample(v, min(k, len(v))))))
        shuffled = [sorted(v, key=lambda d: r_tie.random()) for v in vals]
        for k in KS:
            abel_tie[k].append(sum(
                1 for v in shuffled
                if any(d["solved"] for d in
                       sorted(v, key=lambda d: abel_magnitude(d["r1"], d["r2"]))[:k])))
            len_tie[k].append(sum(
                1 for v in shuffled
                if any(d["solved"] for d in sorted(v, key=_start_len)[:k])))
    return plain, abel_tie, len_tie


def p_value(null_counts, observed):
    """One-sided: fraction of null trials that match or beat the arm."""
    return sum(1 for c in null_counts if c >= observed) / len(null_counts)


def mcnemar(hits_a, hits_b):
    """Exact paired test on the *discordant* presentations only.

    Two arms scored on the same 60 presentations are paired, so a difference of totals is
    not evidence by itself: 41 vs 39 could be 2 wins and 0 losses, or 7 and 5. Only the rows
    where exactly one arm solves carry information. Under the null "each discordant row is a
    coin flip", the two-sided exact p is 2 * P(X >= max(b, c)) for X ~ Binom(b + c, 1/2).
    """
    only_a = sorted(hits_a - hits_b)
    only_b = sorted(hits_b - hits_a)
    b, c = len(only_a), len(only_b)
    n = b + c
    if n == 0:
        return only_a, only_b, 1.0
    hi = max(b, c)
    tail = sum(math.comb(n, i) for i in range(hi, n + 1)) / 2 ** n
    return only_a, only_b, min(1.0, 2 * tail)


def orbit_view(auts, hits, ids60):
    """Per-Aut-class verdict. subset-60's 60 rows are only 45 distinct Aut classes, so a
    /60 count double-counts: one class of size 8 alone can move it by 7. ``full`` = classes
    where every member is solved, ``split`` = classes whose members disagree (a real signal
    that an arm is picking on presentation, not on orbit).
    """
    by = defaultdict(list)
    for p in ids60:
        by[auts[p]].append(p)
    full = sum(1 for members in by.values() if all(p in hits for p in members))
    split = [c for c, members in by.items()
             if any(p in hits for p in members) and not all(p in hits for p in members)]
    return len(by), full, sorted(split)


def main():
    n_rows = gate_truncation()
    ids60, bins, auts, cov, control = load()
    oracle = oracle_set(cov)
    greedy_hits = {p for p, c in control.items() if c["solved"]}

    counts = {name: {tie: arm_counts(cov, key, tie)
                     for tie in ("ident", "adversarial", "optimistic")}
              for name, key in KEYS.items()}
    rnd_plain, rnd_abel, rnd_len = random_arm(cov)
    rnd_exact = random_exact(cov)

    headline = rank_all(cov, KEYS["abel"])                       # bare abel, pre-committed
    hit = {p for p in cov if solves_within(headline[p], HEADLINE_K)}
    lex = rank_all(cov, KEYS["abel_len_lex"])
    hit_lex = {p for p in cov if solves_within(lex[p], HEADLINE_K)}
    lonly = rank_all(cov, KEYS["len_only"])
    hit_len = {p for p in cov if solves_within(lonly[p], HEADLINE_K)}

    # gate 5 — an independent live-search implementation reached the same number
    assert len(hit_lex) == LIVE_HOP1_TOPK, (
        f"abel_len_lex top-{HEADLINE_K} is {len(hit_lex)}/60, but the live-search hop1_topk "
        f"arm of abel_double_cov_b1k reports {LIVE_HOP1_TOPK}/60 — the two paths disagree")
    # gate 6
    assert hit <= oracle, f"top-{HEADLINE_K} claims rows the oracle misses: {sorted(hit - oracle)}"
    assert hit_lex <= oracle and hit_len <= oracle, "an arm claims rows outside the oracle"

    tenk = tenk_arms(ids60)

    write_csv(ids60, bins, auts, cov, control, oracle, headline, lex, lonly)
    write_md(ids60, bins, auts, cov, control, oracle, greedy_hits, counts,
             rnd_plain, rnd_abel, rnd_len, rnd_exact, hit, hit_lex, hit_len, headline, n_rows,
             tenk)
    n_orb, orb_hit, _ = orbit_view(auts, hit, ids60)
    print(f"gates ok on {n_rows} rows | greedy {len(greedy_hits)}/60 | oracle {len(oracle)}/60 "
          f"| abel top-{HEADLINE_K} {len(hit)}/60 ({orb_hit}/{n_orb} orbits) "
          f"| len-only {len(hit_len)}/60 | random exact {rnd_exact[HEADLINE_K]:.1f}/60")
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}")


def rank_all(cov, key, tie="ident"):
    return {p: rank(v, key, tie) for p, v in cov.items()}


# ------------------------------------------------------------------------ output

def write_csv(ids60, bins, auts, cov, control, oracle, headline, lex, lonly):
    path = os.path.join(ROOT, OUT_CSV)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["pres_id", "bin", "aut_class", "n_cand", "n_solving_cand",
            "abel_min", "n_tied_at_min",
            "oracle_solved", "oracle_nodes", "greedy_orig_solved", "greedy_orig_nodes",
            "abel_top1_solved", "abel_top1_nodes", "abel_top1_z", "abel_top1_iso_gen",
            "abel_top1_cap", "abel_top3_solved", "abel_top3_cum_nodes",
            "abel_top3_first_solver_rank", "abel_top3_max_cap",
            "adv_abel_top3_solved", "lex_top3_solved", "len_top3_solved", "len_top3_max_cap",
            "p_random_top3"]
    adv = rank_all(cov, KEYS["abel"], "adversarial")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for p in ids60:
            v, ordered = cov[p], headline[p]
            amin = min(abel_magnitude(d["r1"], d["r2"]) for d in v)
            tied = sum(1 for d in v if abel_magnitude(d["r1"], d["r2"]) == amin)
            first = next((i + 1 for i, d in enumerate(ordered[:HEADLINE_K]) if d["solved"]), "")
            ok = [d for d in v if d["solved"]]
            n, s = len(v), len(ok)
            kk = min(HEADLINE_K, n)
            pr = 1.0 - math.comb(n - s, kk) / math.comb(n, kk) if n - s >= kk else 1.0
            c = control[p]
            w.writerow([
                p, bins[p], auts[p], n, s, amin, tied,
                p in oracle, min((d["nodes_explored"] for d in ok), default=""),
                bool(c["solved"]), c["nodes_explored"],
                ordered[0]["solved"], ordered[0]["nodes_explored"], ordered[0]["z_word"],
                ordered[0]["iso_gen"], ordered[0]["max_relator_length_cap"],
                solves_within(ordered, HEADLINE_K), cumulative_nodes(ordered, HEADLINE_K) or "",
                first, max(d["max_relator_length_cap"] for d in ordered[:HEADLINE_K]),
                solves_within(adv[p], HEADLINE_K),
                solves_within(lex[p], HEADLINE_K),
                solves_within(lonly[p], HEADLINE_K),
                max(d["max_relator_length_cap"] for d in lonly[p][:HEADLINE_K]),
                round(pr, 4),
            ])


def _row(name, per_k):
    return "| `%s` | %s |" % (name, " | ".join(str(per_k[k]) for k in KS))


def _caps(ordered, k):
    return [d["max_relator_length_cap"] for d in ordered[:k]]


def write_md(ids60, bins, auts, cov, control, oracle, greedy_hits, counts,
             rnd_plain, rnd_abel, rnd_len, rnd_exact, hit, hit_lex, hit_len, headline, n_rows,
             tenk):
    n_cand = [len(v) for v in cov.values()]
    cum = [cumulative_nodes(headline[p], HEADLINE_K) for p in sorted(hit)]
    top1 = [headline[p][0]["nodes_explored"] for p in sorted(hit)]
    omin = [min(d["nodes_explored"] for d in cov[p] if d["solved"]) for p in sorted(oracle)]
    ties = []
    for v in cov.values():
        m = min(abel_magnitude(d["r1"], d["r2"]) for d in v)
        ties.append(sum(1 for d in v if abel_magnitude(d["r1"], d["r2"]) == m))
    lonly = rank_all(cov, KEYS["len_only"])
    abel_caps = [c for p in ids60 for c in _caps(headline[p], HEADLINE_K)]
    len_caps = [c for p in ids60 for c in _caps(lonly[p], HEADLINE_K)]
    n_orb, orb_abel, split_abel = orbit_view(auts, hit, ids60)
    _, orb_len, split_len = orbit_view(auts, hit_len, ids60)
    _, orb_oracle, split_oracle = orbit_view(auts, oracle, ids60)
    _, orb_greedy, split_greedy = orbit_view(auts, greedy_hits, ids60)
    _, orb_lex, split_lex = orbit_view(auts, hit_lex, ids60)
    t_cov, t_greedy, t_oracle, t_hits, t_rnd = tenk
    t_only_a, t_only_l, t_p = mcnemar(t_hits["abel"], t_hits["len_only"])
    p_abel = p_value(rnd_plain[HEADLINE_K], len(hit))
    p_len = p_value(rnd_plain[HEADLINE_K], len(hit_len))
    only_abel, only_len, p_pair = mcnemar(hit, hit_len)
    only_abel_g, only_greedy, p_pair_g = mcnemar(hit, greedy_hits)
    strat = {n: arm_hits(cov, KEYS[n], "ident", HEADLINE_K)
             for n in ("len_only", "len_lex", "len_then_abel")}
    only_strat, only_lex_ctl, p_strat = mcnemar(strat["len_then_abel"], strat["len_lex"])
    strat_k = {n: counts[n]["ident"] for n in ("len_only", "len_lex", "len_then_abel")}
    # exactly which K the stratified probe moves at — "identical everywhere" would be a stronger
    # claim than the data supports, and the report must not round a single-row win down to zero.
    strat_moves = sorted(k for k in KS
                         if strat_k["len_then_abel"][k] != strat_k["len_lex"][k])
    strat_where = ("identical to `len_lex` at every K" if not strat_moves else
                   "identical to `len_lex` at every K except "
                   + ", ".join(f"K={k} ({strat_k['len_lex'][k]} → "
                               f"{strat_k['len_then_abel'][k]}, one row, exact p = "
                               f"{mcnemar(arm_hits(cov, KEYS['len_then_abel'], 'ident', k), arm_hits(cov, KEYS['len_lex'], 'ident', k))[2]:.3f})"
                               for k in strat_moves))
    # what the key does on the rows top-K misses: where the solver actually ranks, against
    # the (n + 1) / (s + 1) mean rank of the best solver under a uniformly random order.
    miss_rows = []
    for p in sorted(oracle - hit):
        ordered = headline[p]
        n = len(ordered)
        ranks = [i + 1 for i, d in enumerate(ordered) if d["solved"]]
        miss_rows.append((p, n, len(ranks), ranks[0], (n + 1) / (len(ranks) + 1)))
    # the rows abel wins over length: how likely a uniform draw would have taken them too
    disc_rows = []
    for p in only_abel:
        v = cov[p]
        n = len(v)
        s = sum(1 for d in v if d["solved"])
        kk = min(HEADLINE_K, n)
        pr = 1.0 - math.comb(n - s, kk) / math.comb(n, kk) if n - s >= kk else 1.0
        disc_rows.append((p, n, s, pr))
    band = len(oracle) - rnd_exact[HEADLINE_K]
    closed_abel = 100 * (len(hit) - rnd_exact[HEADLINE_K]) / band
    closed_len = 100 * (len(hit_len) - rnd_exact[HEADLINE_K]) / band
    hdr = "| arm | " + " | ".join("K=%d" % k for k in KS) + " |"
    sep = "|---|" + "---:|" * len(KS)
    unsolved = sorted(set(ids60) - oracle)
    sizes = Counter(Counter(auts[p] for p in ids60).values())

    md = f"""# Abelianized-magnitude top-K CoV selection @ budget 1,000 (subset-60)

**No search.** Every number is a row of the frozen [`covsweep_1000_66_*.jsonl`]({os.path.relpath(SWEEP, 'results/comparison')}) selected by a key computed from the two *start* strings. This runner explores 0 nodes.

This is the budget-1,000 replication of [`ABEL_TOPK_COV_B10K.md`](ABEL_TOPK_COV_B10K.md), run to test whether that file's headline was a property of the key or of the budget it was measured at.

## Headline

| arm @ budget {BUDGET:,} | solved /60 | orbits /{n_orb} |
|---|---:|---:|
| plain greedy, untransformed start (`n_cov = 0` control row) | **{len(greedy_hits)}/60** | {orb_greedy}/{n_orb} |
| **abel top-{HEADLINE_K}, bare `abel` key** (pre-committed headline) | **{len(hit)}/60** | {orb_abel}/{n_orb} |
| abel top-{HEADLINE_K}, `(abel, start_len, longest)` — the 10k key | {len(hit_lex)}/60 | {orb_lex}/{n_orb} |
| length-only top-{HEADLINE_K} ("smallest length"), the control | {len(hit_len)}/60 | {orb_len}/{n_orb} |
| random top-{HEADLINE_K}, exact expectation | {rnd_exact[HEADLINE_K]:.1f}/60 | — |
| random top-{HEADLINE_K}, {N_RANDOM:,}-trial mean (min–max) | {statistics.mean(rnd_plain[HEADLINE_K]):.1f}/60 ({min(rnd_plain[HEADLINE_K])}–{max(rnd_plain[HEADLINE_K])}) | — |
| best CoV — **oracle** over all ~{statistics.mean(n_cand):.0f} candidates | **{len(oracle)}/60** | {orb_oracle}/{n_orb} |

Against the untransformed greedy baseline of **{len(greedy_hits)}/60**, abel top-{HEADLINE_K} is **+{len(hit) - len(greedy_hits)}** presentations for at most {HEADLINE_K} searches of <= {BUDGET:,} nodes each. Against the oracle's {len(oracle)}/60 it gives up **{len(oracle) - len(hit)}**, so it recovers **{100 * len(hit) / len(oracle):.0f}%** of the oracle from {HEADLINE_K} tries out of ~{statistics.mean(n_cand):.0f} — a ~{statistics.mean(n_cand) / HEADLINE_K:.0f}x cut in the portfolio.

**The 10k result does not replicate exactly, and that is the finding.** At 10,000 the key matched the oracle with 0 misses (52/52). At 1,000 it misses {len(oracle) - len(hit)} of {len(oracle)}: {', '.join(str(p) for p in sorted(oracle - hit))}. The key is a real signal — it beats every control at every K below — but "recovers the oracle exactly" is a statement about budget 10,000, not about the key.

**The misses are needles, and abel still finds them faster than chance.** Each of those {len(oracle) - len(hit)} presentations has exactly **one** solving candidate in its whole family:

| pres | candidates | solvers | abel rank of the solver | expected rank if abel were noise |
|---|---:|---:|---:|---:|
{chr(10).join('| %d | %d | %d | **%d** | %.0f |' % m for m in miss_rows)}

A top-3 arm cannot be expected to hit a 1-in-{miss_rows[0][1]} needle — random top-3 finds it {100 * HEADLINE_K / miss_rows[0][1]:.1f}% of the time. On {sum(1 for m in miss_rows if m[3] <= 10)} of the {len(miss_rows)} the key still puts the unique solver in the top 10 of {miss_rows[0][1]}+. The gap to the oracle here is a budget-K limit, not the key failing.

## Is it beating the controls, or beating nothing?

| comparison | abel top-{HEADLINE_K} | control | gap |
|---|---:|---:|---:|
| vs random (null, exact) | {len(hit)} | {rnd_exact[HEADLINE_K]:.1f} | **+{len(hit) - rnd_exact[HEADLINE_K]:.1f}** |
| vs random (null, {N_RANDOM:,} trials) | {len(hit)} | {statistics.mean(rnd_plain[HEADLINE_K]):.1f} | one-sided p = **{p_abel:.4f}** ({sum(1 for c in rnd_plain[HEADLINE_K] if c >= len(hit))}/{N_RANDOM:,} trials reached it) |
| vs length-only (is abel a length proxy?) | {len(hit)} | {len(hit_len)} | **+{len(hit) - len(hit_len)}** |
| length-only vs random | {len(hit_len)} | {statistics.mean(rnd_plain[HEADLINE_K]):.1f} | one-sided p = {p_len:.4f} |

The length-only control is the load-bearing one: shorter relators are easier, so any key correlated with length gets credit it did not earn. Abel beats it by {len(hit) - len(hit_len)} at K={HEADLINE_K}, and at every K in the table below.

**Effect size in the only band that is measurable here.** Random already reaches {rnd_exact[HEADLINE_K]:.1f}/60 and the oracle caps at {len(oracle)}/60, so the whole discriminable range is {band:.1f} presentations wide. Abel closes **{closed_abel:.0f}%** of that random-to-oracle band; length-only closes {closed_len:.0f}%. Quoting "{len(hit)}/60" without the {rnd_exact[HEADLINE_K]:.1f}/60 floor overstates what the ranking is doing.

### The paired tests (a difference of totals is not evidence)

Two arms scored on the same 60 presentations are paired, so only rows where exactly one arm solves carry information. Exact McNemar on the discordant rows:

| pair | solved only by A | solved only by B | two-sided exact p |
|---|---|---|---:|
| **A = abel top-{HEADLINE_K}**, B = length-only top-{HEADLINE_K} | {len(only_abel)} ({', '.join(map(str, only_abel)) or 'none'}) | {len(only_len)} ({', '.join(map(str, only_len)) or 'none'}) | **{p_pair:.3f}** |
| **A = abel top-{HEADLINE_K}**, B = greedy control | {len(only_abel_g)} | {len(only_greedy)} | {p_pair_g:.2e} |

Abel over the untransformed greedy baseline is decisive. **Abel over the length control is not** — at p = {p_pair:.3f} on {len(only_abel) + len(only_len)} discordant rows, the +{len(hit) - len(hit_len)} is directionally consistent at every K but individually underpowered on 60 presentations. It should be reported as a consistent direction, not a demonstrated separation.

And the two rows are not abel finding a needle — they are the length key picking *worse than chance*:

| pres | candidates | of which solve | P(random top-{HEADLINE_K} solves) | abel top-{HEADLINE_K} | length top-{HEADLINE_K} |
|---|---:|---:|---:|:--:|:--:|
{chr(10).join('| %d | %d | %d | %.2f | yes | **no** |' % d for d in disc_rows)}

A uniform draw would have solved both more often than the length key did. So the honest reading of abel-over-length at this budget is: abel is not worse than random anywhere, and length is worse than random somewhere.

### Where does abel's lead actually come from? Rank by length first, let abel break ties

If abel merely re-expressed length, forcing length to lead and abel to follow would reproduce abel's score. If abel added signal *within* a length stratum, `len_then_abel` would pull clear of the other length keys. It never approaches abel's {counts['abel']['ident'][HEADLINE_K]}:

{hdr}
{sep}
| `len_only` — length, then the CoV's own name | {' | '.join(str(strat_k['len_only'][k]) for k in KS)} |
| `len_lex` — length, then longest relator | {' | '.join(str(strat_k['len_lex'][k]) for k in KS)} |
| `len_then_abel` — length, then **abel** | {' | '.join(str(strat_k['len_then_abel'][k]) for k in KS)} |
| `abel` — **abel leading** | {' | '.join(str(counts['abel']['ident'][k]) for k in KS)} |

**This is a null result and it is informative.** At the headline K={HEADLINE_K}, `len_then_abel` wins {len(only_strat)} rows against `len_lex` and loses {len(only_lex_ctl)} (exact p = {p_strat:.3f}). Across the sweep it is {strat_where} — so the most abel buys at *fixed* start length anywhere on this set is one presentation, at the one K nobody is quoting, and at K={HEADLINE_K} it buys nothing. Abel's whole +{len(hit) - len(hit_len)} comes instead from the rows where it **overrides** length — picking a longer candidate with a smaller abelianized magnitude and being right.

That rules out the simple "abel is a length proxy" story, since a proxy cannot beat the thing it proxies. It does not establish an independent length-residual signal at this sample size: the effect lives in {len(only_abel)} presentations, and the stratified probe that would confirm it moves by at most a single row (and by none at K={HEADLINE_K}). Idea 1's length-residualized AUC of 0.92 was measured on a per-candidate ranking over the whole 66-set; this is a 60-presentation top-{HEADLINE_K} reach test, a far coarser instrument, and it does not reproduce that here.

## Every arm, every K (deterministic `(z, iso_gen, iso_index)` tie-break)

{hdr}
{sep}
{chr(10).join(_row(n, counts[n]['ident']) for n in KEYS)}
| `random` exact expectation | {' | '.join('%.1f' % rnd_exact[k] for k in KS)} |
| `random` mean of {N_RANDOM:,} | {' | '.join('%.1f' % statistics.mean(rnd_plain[k]) for k in KS)} |
| **oracle (all ~{statistics.mean(n_cand):.0f})** | {' | '.join(str(len(oracle)) for k in KS)} |

## Ties, and why the claim is stated at K={HEADLINE_K}

A median of **{statistics.median(ties):.0f}** candidates (max {max(ties)}) tie at the abel minimum, so under the bare key K=1 measures the tie-break as much as the key. Resolving every tie *against* the arm and *for* it brackets the truth:

{hdr}
{sep}
| `abel` adversarial (worst tie-break) | {' | '.join(str(counts['abel']['adversarial'][k]) for k in KS)} |
| `abel` + random tie-break, min of {N_RANDOM:,} | {' | '.join(str(min(rnd_abel[k])) for k in KS)} |
| `abel` + random tie-break, median | {' | '.join('%.0f' % statistics.median(rnd_abel[k]) for k in KS)} |
| `abel` optimistic (best tie-break) | {' | '.join(str(counts['abel']['optimistic'][k]) for k in KS)} |
| `len_only` adversarial | {' | '.join(str(counts['len_only']['adversarial'][k]) for k in KS)} |
| `len_only` + random tie-break, median | {' | '.join('%.0f' % statistics.median(rnd_len[k]) for k in KS)} |
| `len_only` optimistic | {' | '.join(str(counts['len_only']['optimistic'][k]) for k in KS)} |

At K=1 the bare key's bracket is **{counts['abel']['adversarial'][1]}–{counts['abel']['optimistic'][1]}** with a random-tie-break median of {statistics.median(rnd_abel[1]):.0f}; at K={HEADLINE_K} it is **{counts['abel']['adversarial'][HEADLINE_K]}–{counts['abel']['optimistic'][HEADLINE_K]}** with a median of {statistics.median(rnd_abel[HEADLINE_K]):.0f}. The adversarial row is the floor an enemy tie-break cannot push below; the length control's own adversarial floor is {counts['len_only']['adversarial'][HEADLINE_K]}, so the two arms are compared at the same standard.

## Orbit level, not row level

subset-60's 60 rows are only **{n_orb} distinct Aut classes** — {sizes[1]} singletons, {sizes.get(2, 0)} pairs, {sizes.get(3, 0)} triples, and one class of {max(Counter(auts[p] for p in ids60).values())}. A /60 count therefore weights one orbit up to {max(Counter(auts[p] for p in ids60).values())}x. Counting a class solved only when **every** member is solved:

| arm | rows /60 | orbits /{n_orb} | classes split (some members solved, some not) |
|---|---:|---:|---|
| greedy control | {len(greedy_hits)} | {orb_greedy} | {', '.join(map(str, split_greedy)) or 'none'} |
| abel top-{HEADLINE_K} | {len(hit)} | {orb_abel} | {', '.join(map(str, split_abel)) or 'none'} |
| length-only top-{HEADLINE_K} | {len(hit_len)} | {orb_len} | {', '.join(map(str, split_len)) or 'none'} |
| oracle | {len(oracle)} | {orb_oracle} | {', '.join(map(str, split_oracle)) or 'none'} |

The ordering survives the orbit view, so the headline is not one big Aut class carrying the count.

## The cap confound, measured

A CoV lengthens relators and the sweep sizes each row's cap to `max(24, longest + 16)`, so a transformed row can run at a larger cap than the untransformed control's fixed 24. That is a confound, not a result — [a control with no dynamic range is not a comparison](../../experiments/lessons/control-with-no-dynamic-range.md).

| picks | median cap | max cap | share at cap 24 |
|---|---:|---:|---:|
| abel top-{HEADLINE_K} | {statistics.median(abel_caps):.0f} | {max(abel_caps)} | {100 * sum(1 for c in abel_caps if c == 24) / len(abel_caps):.0f}% |
| length-only top-{HEADLINE_K} | {statistics.median(len_caps):.0f} | {max(len_caps)} | {100 * sum(1 for c in len_caps if c == 24) / len(len_caps):.0f}% |
| untransformed control | 24 | 24 | 100% |

Both arms draw from the same candidate pool with the same caps, so the abel-vs-length and abel-vs-random comparisons are cap-fair by construction. Only the comparison against the untransformed greedy control carries the confound; the per-pick cap is in the CSV so it stays visible.

## Cost

Sequential top-{HEADLINE_K}, stopping at the first solve, over the {len(hit)} rows it solves:

| | median nodes | mean nodes | max nodes |
|---|---:|---:|---:|
| abel top-{HEADLINE_K}, cumulative to first solve | {statistics.median(cum):.0f} | {statistics.mean(cum):.0f} | {max(cum)} |
| abel top-1 pick alone | {statistics.median(top1):.0f} | {statistics.mean(top1):.0f} | {max(top1)} |
| oracle minimum (what the sweep found) | {statistics.median(omin):.0f} | {statistics.mean(omin):.0f} | {max(omin)} |

Read the headline as **{HEADLINE_K} searches of <= {BUDGET:,} nodes each**, worst case {HEADLINE_K * BUDGET:,} nodes, against the control's one search of <= {BUDGET:,}.

## Back-applying the same test to PR #14's own budget

PR #14 reports abel top-{HEADLINE_K} = {len(t_hits['abel_len_lex'])}/60 against a length-only control of {len(t_hits['len_only'])}/60 and never pairs them. Re-ranking the 10,000-node sweep with these keys and running the same exact McNemar:

| budget | abel top-{HEADLINE_K} | length top-{HEADLINE_K} | discordant | exact p | random floor | oracle ceiling |
|---|---:|---:|:--:|---:|---:|---:|
| 1,000 | {len(hit)} | {len(hit_len)} | {len(only_abel)}–{len(only_len)} | {p_pair:.3f} | {rnd_exact[HEADLINE_K]:.1f} | {len(oracle)} |
| 10,000 | {len(t_hits['abel'])} | {len(t_hits['len_only'])} | {len(t_only_a)}–{len(t_only_l)} | {t_p:.3f} | {t_rnd:.1f} | {len(t_oracle)} |

Same direction, same shape, same verdict at both budgets: abel never loses a row to the length control, and the win is never statistically separated — {len(only_abel) + len(only_len)} discordant rows at 1,000 and {len(t_only_a) + len(t_only_l)} at 10,000 are not enough to reject a coin flip. **The abel-beats-length claim is undemonstrated at 10,000 too, not just here.** What *is* decisive at both budgets is abel against the greedy baseline and against random.

Note also how much narrower the discriminable band is at 10,000: random top-{HEADLINE_K} already reaches {t_rnd:.1f}/60 against an oracle of {len(t_oracle)}/60, so "recovers the oracle exactly" is a {len(t_oracle) - t_rnd:.1f}-presentation effect over chance there, versus {len(oracle) - rnd_exact[HEADLINE_K]:.1f} at 1,000. The tighter budget is the *more* discriminating test of the key, and it is the one where the length control is left behind by the wider margin.

## What this replication does and does not establish

- **Does.** The key is not an artefact of budget 10,000. At one tenth the budget it still beats random by {len(hit) - rnd_exact[HEADLINE_K]:.1f} presentations (p = {p_abel:.4f}), closing {closed_abel:.0f}% of the random-to-oracle band, and it survives an adversarial tie-break.
- **Does not — separate abel from length at this sample size.** Abel leads the length control at every K, but the paired test on {len(only_abel) + len(only_len)} discordant rows gives p = {p_pair:.3f} and the length-stratified probe (`len_then_abel`) adds nothing at K={HEADLINE_K} and one row at K=1. 60 presentations cannot settle a {len(hit) - len(hit_len)}-row gap; the direction is consistent, the separation is not demonstrated. The one thing that *is* ruled out is abel being a pure length proxy — it wins by overriding length, not by tracking it.
- **Does.** The pipeline is cross-validated two ways: gate 1 checks the 1k sweep is the 10k sweep truncated on all {n_rows:,} rows, and gate 5 checks this re-ranking reproduces the {LIVE_HOP1_TOPK}/60 that `abel_double_cov_b1k.py` reached by running live searches.
- **Does not — this is not independent data.** The 1k and 10k sweeps enumerate the *same* candidate set, and the key reads only the start strings, so the abel *ranking* is bit-identical at both budgets; only the solved flags move. This is a budget-robustness check on one frozen sweep, not a second experiment.
- **Does not — subset-60 is in-sample.** Idea 1's abelianized magnitude was developed on the 66-set, of which subset-60 is a part, at every budget. The genuinely held-out test remains the unsolved 124.
- **Does not — it does not crack a new presentation.** The {len(unsolved)} rows no CoV solves here ({', '.join(str(p) for p in unsolved)}) stay unsolved; this is selection *within* an enumerated CoV family.
- **The known limit of the key applies.** Abelianized magnitude is a solution-*depth* proxy: strong on shallow instances, weak on the hard residual, provably blind on near-identity-abelianization instances. That it misses {len(oracle) - len(hit)} rows here and 0 at 10,000 is consistent with a depth proxy degrading as the budget tightens.

## Gates (all fatal)

1. **truncation** — `solved@1k == (solved@10k and nodes@10k <= {BUDGET})` on all {n_rows:,} rows, with equal nodes, path and cap when both solved;
2. **anti-leak** — `len(r1) + len(r2) == start_total_length_cov` on every row, so `r1`/`r2` is the start and no key can read the search (`min_relator`/`max_relator` are search-derived and never read);
3. **budget** — every row is at `node_budget == {BUDGET}` with `nodes_explored <= {BUDGET}`;
4. **coverage** — 60 presentations, each with >= 1 CoV candidate and exactly one untransformed control row;
5. **cross-implementation** — `abel_len_lex` top-{HEADLINE_K} equals the {LIVE_HOP1_TOPK}/60 that `abel_double_cov_b1k.py`'s `hop1_topk` reached via live search;
6. **selection honesty** — every arm's solved set is a subset of the oracle's.

## Source

- Sweep: `{SWEEP}`
- Cross-checked against: `{SWEEP_10K}`
- Table: [`abel_topk_cov_b1k_subset60.csv`](abel_topk_cov_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_topk_cov_b1k.py` (`python3 -m experiments.heuristic_search.runners.abel_topk_cov_b1k`)
- Key: `IDEAS.md` idea 1 / `restart_planner.abel_magnitude`.
"""
    with open(os.path.join(ROOT, OUT_MD), "w") as fh:
        fh.write(md)


if __name__ == "__main__":
    main()
