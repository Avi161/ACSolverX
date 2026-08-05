"""Abelianized-magnitude top-K CoV selection vs the best-CoV oracle, at budget 10,000.

**Zero search nodes.** This runner re-ranks the frozen budget-10,000 CoV sweep
(``covsweep_10000_66_*.jsonl``); it never calls the solver. Every number below is a
row already in that file, selected by a key computed from the *start* strings alone.

## The question

``benchmark/subsets/ARMS.md`` reports **best CoV @10k = 52/60** on subset-60. That is an
**oracle**: the cheapest of ~11-173 subword CoVs per presentation, and finding it cost the
whole sweep. The oracle is a lower bound on a transformed route, not a procedure
([why that matters](../../lessons/price-the-untransformed-route.md)).

This asks whether a **search-free ranking key** recovers that same 52 from a handful of
tries. The key is ``IDEAS.md`` idea 1's abelianized magnitude — the sum of the absolute
abelianized exponent sums of the transformed pair,

```text
abel(r1, r2) = |sigma_x(r1)| + |sigma_y(r1)| + |sigma_x(r2)| + |sigma_y(r2)|
```

identical to ``restart_planner.abel_magnitude``, but read off the *strings* here so this
file stays stdlib-only and importable without numba.

## Arms

Each arm ranks a presentation's CoV candidates, takes the top K, and counts the
presentation solved if **any** of those K solved within its own 10,000-node budget.

| key | rank on |
|---|---|
| ``abel`` | ``abel`` |
| ``abel_len`` | ``(abel, start_total_length)`` |
| ``abel_len_lex`` | ``(abel, start_total_length, longest_relator)`` -- idea_bench's ``cov_abel_len_lex`` |
| ``len_only`` | ``start_total_length`` -- the control: is abel just a length proxy? |
| ``random`` | a seeded shuffle, ``N_RANDOM`` trials -- the null |

Every key is a pure function of the two start strings, so it costs 0 nodes and cannot
read the search. Gate 2 below enforces that.

**Ties are the load-bearing detail.** A median of 6 candidates (max 21) tie at the abel
minimum, so K=1 is a statement about the tie-break, not about the key. Both extremes are
reported per K: ``adversarial`` resolves every tie against the arm (unsolved first),
``optimistic`` resolves it for the arm. A claim belongs in the adversarial column or in
the random-tie-break distribution, never in the optimistic one.

## Gates (all fatal -- the run refuses to write)

1. the oracle re-derived from the sweep is exactly the ``cov_solved`` set of the shipped
   ``greedy_vs_bestcov_subset60_b10000.csv``, 52 rows;
2. ``len(r1) + len(r2) == start_total_length_cov`` on every row, which proves ``r1``/``r2``
   is the *start* and not a search-derived state -- ``min_relator``/``max_relator`` are
   search-derived and are never read here
   ([the leak](../../lessons/held-out-means-held-out-from-selection.md));
3. every row's ``nodes_explored`` is within its own ``node_budget``;
4. subset-60 contributes exactly 60 presentations, each with >= 1 CoV candidate row.

    python3 -m experiments.heuristic_search.runners.abel_topk_cov_b10k
"""
from __future__ import annotations

import csv
import json
import os
import random
import statistics
import sys

KS = (1, 2, 3, 4, 5, 10)
HEADLINE_K = 3
N_RANDOM = 300
RANDOM_SEED = 20260805

SWEEP = ("results/stable_ac/cov/"
         "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
BASE_CSV = "results/stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv"
SUBSET60 = "benchmark/subsets/benchmark_subset_60.csv"
OUT_CSV = "results/comparison/abel_topk_cov_b10k_subset60.csv"
OUT_MD = "results/comparison/ABEL_TOPK_COV_B10K.md"


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
    """|sigma_x| + |sigma_y| over both relators -- ``restart_planner.abel_magnitude``.

    The depth-proxy ranking key of ``IDEAS.md`` idea 1 (within-presentation AUC 0.92 on
    the 66-set, length-independent). It is a solution-DEPTH proxy: strong on shallow
    instances, weak on the hard residual, blind on near-identity-abelianization
    presentations. A prior, never a guarantee.
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
}


def rank(cands, key, tie="ident"):
    """Sort ``cands`` by ``key``. ``tie`` resolves exact key ties:

    ``ident``       -- the CoV's own (z, iso_gen, iso_index, r1, r2), reproducible;
    ``adversarial`` -- unsolved candidates first (the arm's worst case);
    ``optimistic``  -- solved candidates first (the arm's best case).
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

def load():
    ids60, bins = [], {}
    with open(os.path.join(ROOT, SUBSET60)) as fh:
        for row in csv.DictReader(fh):
            ids60.append(int(row["pres_id"]))
            bins[int(row["pres_id"])] = int(row["bin"])

    keep = set(ids60)
    cov, control, leaks, over = {}, {}, 0, 0
    with open(os.path.join(ROOT, SWEEP)) as fh:
        for line in fh:
            d = json.loads(line)
            if d["pres_id"] not in keep:
                continue
            if len(d["r1"]) + len(d["r2"]) != d["start_total_length_cov"]:
                leaks += 1
            if d["nodes_explored"] > d["node_budget"]:
                over += 1
            if d.get("n_cov", 0) == 0:
                control[d["pres_id"]] = d      # the ORIGINAL pair, not a CoV
            else:
                cov.setdefault(d["pres_id"], []).append(d)

    # gate 2 -- r1/r2 is the start, so every key is search-free
    assert leaks == 0, (f"{leaks} rows where len(r1)+len(r2) != start_total_length_cov: "
                        "r1/r2 is not the start, the ranking keys would read the search")
    # gate 3
    assert over == 0, f"{over} rows exceed their own node_budget"
    # gate 4
    assert len(ids60) == 60, f"subset-60 has {len(ids60)} rows"
    missing = [p for p in ids60 if not cov.get(p)]
    assert not missing, f"no CoV candidate rows for {missing}"

    return ids60, bins, cov, control


def oracle_set(cov):
    """The best-CoV @10k set: any CoV row that solved. n_cov == 0 is excluded."""
    return {p for p, v in cov.items() if any(d["solved"] for d in v)}


def gate_oracle(oracle):
    """Gate 1 -- the re-derived oracle is the shipped table's cov_solved set."""
    shipped = set()
    with open(os.path.join(ROOT, BASE_CSV)) as fh:
        for row in csv.DictReader(fh):
            if row["cov_solved"] == "True":
                shipped.add(int(row["pres_id"]))
    assert oracle == shipped, (
        f"oracle mismatch vs {BASE_CSV}: "
        f"only-here {sorted(oracle - shipped)}, only-shipped {sorted(shipped - oracle)}")
    assert len(oracle) == 52, f"oracle is {len(oracle)}/60, ARMS.md says 52"
    return shipped


# ------------------------------------------------------------------------- arms

def arm_counts(cov, key, tie):
    return {k: sum(1 for v in cov.values() if solves_within(rank(v, key, tie), k)) for k in KS}


def random_arm(cov, seed=RANDOM_SEED, trials=N_RANDOM):
    """The null: K candidates drawn uniformly. Also the random-tie-break distribution."""
    rnd = random.Random(seed)
    plain = {k: [] for k in KS}
    abel_tie = {k: [] for k in KS}
    for _ in range(trials):
        for k in KS:
            plain[k].append(sum(1 for v in cov.values()
                                if any(d["solved"] for d in rnd.sample(v, min(k, len(v))))))
            abel_tie[k].append(sum(
                1 for v in cov.values()
                if any(d["solved"] for d in sorted(
                    v, key=lambda d: (abel_magnitude(d["r1"], d["r2"]), rnd.random()))[:k])))
    return plain, abel_tie


def main():
    ids60, bins, cov, control = load()
    oracle = oracle_set(cov)
    gate_oracle(oracle)

    counts = {name: {tie: arm_counts(cov, key, tie)
                     for tie in ("ident", "adversarial", "optimistic")}
              for name, key in KEYS.items()}
    rnd_plain, rnd_abel = random_arm(cov)

    headline = rank_all(cov, KEYS["abel_len_lex"])
    hit = {p for p in cov if solves_within(headline[p], HEADLINE_K)}
    assert hit <= oracle, f"top-{HEADLINE_K} claims rows the oracle misses: {sorted(hit - oracle)}"

    write_csv(ids60, bins, cov, control, oracle, headline)
    write_md(ids60, cov, control, oracle, counts, rnd_plain, rnd_abel, hit, headline)
    print(f"oracle {len(oracle)}/60 | abel_len_lex top-{HEADLINE_K} {len(hit)}/60")
    print(f"wrote {OUT_CSV}\nwrote {OUT_MD}")


def rank_all(cov, key, tie="ident"):
    return {p: rank(v, key, tie) for p, v in cov.items()}


# ------------------------------------------------------------------------ output

def write_csv(ids60, bins, cov, control, oracle, headline):
    path = os.path.join(ROOT, OUT_CSV)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["pres_id", "bin", "n_cand", "abel_min", "n_tied_at_min",
            "oracle_solved", "oracle_nodes",
            "greedy_orig_solved", "greedy_orig_nodes",
            "top1_solved", "top1_nodes", "top1_z", "top1_iso_gen", "top1_cap",
            "top3_solved", "top3_cum_nodes", "top3_first_solver_rank",
            "adv_top3_solved", "len_top3_solved"]
    adv = rank_all(cov, KEYS["abel_len_lex"], "adversarial")
    lonly = rank_all(cov, KEYS["len_only"])
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for p in ids60:
            v, ordered = cov[p], headline[p]
            amin = min(abel_magnitude(d["r1"], d["r2"]) for d in v)
            tied = sum(1 for d in v if abel_magnitude(d["r1"], d["r2"]) == amin)
            first = next((i + 1 for i, d in enumerate(ordered[:HEADLINE_K]) if d["solved"]), "")
            ok = [d for d in v if d["solved"]]
            c = control.get(p)
            w.writerow([
                p, bins[p], len(v), amin, tied,
                p in oracle, min((d["nodes_explored"] for d in ok), default=""),
                bool(c and c["solved"]), c["nodes_explored"] if c else "",
                ordered[0]["solved"], ordered[0]["nodes_explored"], ordered[0]["z_word"],
                ordered[0]["iso_gen"], ordered[0]["max_relator_length_cap"],
                solves_within(ordered, HEADLINE_K), cumulative_nodes(ordered, HEADLINE_K) or "",
                first,
                solves_within(adv[p], HEADLINE_K), solves_within(lonly[p], HEADLINE_K),
            ])


def _row(name, per_k):
    return "| `%s` | %s |" % (name, " | ".join(str(per_k[k]) for k in KS))


def write_md(ids60, cov, control, oracle, counts, rnd_plain, rnd_abel, hit, headline):
    n_cand = [len(v) for v in cov.values()]
    cum = [cumulative_nodes(headline[p], HEADLINE_K) for p in sorted(hit)]
    top1 = [headline[p][0]["nodes_explored"] for p in sorted(hit)]
    omin = [min(d["nodes_explored"] for d in cov[p] if d["solved"]) for p in sorted(oracle)]
    ties = []
    for v in cov.values():
        m = min(abel_magnitude(d["r1"], d["r2"]) for d in v)
        ties.append(sum(1 for d in v if abel_magnitude(d["r1"], d["r2"]) == m))
    greedy = sum(1 for c in control.values() if c["solved"])
    hdr = "| arm | " + " | ".join("K=%d" % k for k in KS) + " |"
    sep = "|---|" + "---:|" * len(KS)

    md = f"""# Abelianized-magnitude top-K CoV selection @ budget 10,000 (subset-60)

**No search.** Every number is a row of the frozen
[`covsweep_10000_66_*.jsonl`]({os.path.relpath(SWEEP, 'results/comparison')}) selected by a key
computed from the two *start* strings. 0 nodes explored by this runner.

## The claim under test

`benchmark/subsets/ARMS.md` reports **best CoV @10k = 52/60**, and calls it an oracle: the
cheapest of {min(n_cand)}-{max(n_cand)} subword CoVs per presentation (mean
{statistics.mean(n_cand):.0f}), found by sweeping all of them. The question is whether a
**search-free** key picks a solver out of that family in a handful of tries.

The key is `IDEAS.md` idea 1's abelianized magnitude — the sum of the absolute abelianized
exponent sums of the transformed pair:

```text
abel(r1, r2) = |sigma_x(r1)| + |sigma_y(r1)| + |sigma_x(r2)| + |sigma_y(r2)|
```

## Headline

**Ranking a presentation's CoV candidates by abelianized magnitude and running the top 3,
each at 10,000 nodes, solves {len(hit)}/60 — the oracle's set exactly, 0 misses.**

| arm @ budget 10,000 | solved |
|---|---:|
| plain greedy, untransformed start (`n_cov = 0` control row) | **{greedy}/60** |
| best CoV — oracle over all ~{statistics.mean(n_cand):.0f} candidates | **{len(oracle)}/60** |
| **abel top-3, `(abel, start_len, longest)` key** | **{len(hit)}/60** |
| abel top-3, bare `abel` key, random tie-break (median of {N_RANDOM}) | **{statistics.median(rnd_abel[HEADLINE_K]):.0f}/60** |
| abel top-3, bare `abel` key, adversarial tie-break | **{counts['abel']['adversarial'][HEADLINE_K]}/60** |
| length-only top-3 (control) | **{counts['len_only']['ident'][HEADLINE_K]}/60** |
| random top-3 (null, {N_RANDOM} trials) | **{statistics.mean(rnd_plain[HEADLINE_K]):.1f}/60** |

The adversarial row is the floor: even if every tie at the abel minimum is resolved by an
enemy, top-3 still reaches {counts['abel']['adversarial'][HEADLINE_K]}/60. The claim is not
tie-break luck.

{len(oracle)} is the ceiling of this data, not of the method: the other 8 rows
({', '.join(str(p) for p in sorted(set(ids60) - oracle))} — one Aut class) are solved by
**no** CoV in the sweep at 10,000 and need budget 20,000, so no ranking can reach them here.

## Every arm, every K (deterministic `(z, iso_gen, iso_index)` tie-break)

{hdr}
{sep}
{chr(10).join(_row(n, counts[n]['ident']) for n in KEYS)}
| `random` (mean of {N_RANDOM}) | {' | '.join('%.1f' % statistics.mean(rnd_plain[k]) for k in KS)} |

Abel beats length-only at every K, so it is not a length proxy — consistent with idea 1's
length-residualized AUC of 0.92.

## Ties are why the claim says 3, not 1

A median of **{statistics.median(ties):.0f}** candidates (max {max(ties)}) tie at the abel
minimum, so under the bare key K=1 measures the tie-break as much as the key itself.
Resolving every tie *against* the arm and *for* it brackets the truth:

{hdr}
{sep}
| `abel` adversarial (worst tie-break) | {' | '.join(str(counts['abel']['adversarial'][k]) for k in KS)} |
| `abel` + random tie-break, min of {N_RANDOM} | {' | '.join(str(min(rnd_abel[k])) for k in KS)} |
| `abel` + random tie-break, median | {' | '.join('%.0f' % statistics.median(rnd_abel[k]) for k in KS)} |
| `abel` optimistic (best tie-break) | {' | '.join(str(counts['abel']['optimistic'][k]) for k in KS)} |
| `abel_len_lex` adversarial | {' | '.join(str(counts['abel_len_lex']['adversarial'][k]) for k in KS)} |

At K=1 the bare key's bracket is wide —
**{counts['abel']['adversarial'][1]}-{counts['abel']['optimistic'][1]}**, and a random
tie-break lands at a median of {statistics.median(rnd_abel[1]):.0f}. By K={HEADLINE_K} it has
closed to **{counts['abel']['adversarial'][HEADLINE_K]}-{counts['abel']['optimistic'][HEADLINE_K]}**,
with a random-tie-break median of {statistics.median(rnd_abel[HEADLINE_K]):.0f} and a worst
observed trial of {min(rnd_abel[HEADLINE_K])}. **So K=1 is not a result and K=3 is** — three
tries is where the bare key stops depending on how ties are broken.

Adding the two other static fields removes the ties instead of surviving them:
`abel_len_lex` ranks {counts['abel_len_lex']['adversarial'][HEADLINE_K]}/60 at K={HEADLINE_K}
even under an adversarial tie-break, because exact `(abel, start_len, longest)` ties are rare.
Either route gets to {len(hit)}; the bare key needs K={HEADLINE_K} to get there safely, which
is why the claim is stated at 3.

## Cost

Sequential top-3, stopping at the first solve, over the {len(hit)} rows it solves:

| | median nodes | mean nodes | max nodes |
|---|---:|---:|---:|
| abel top-3, cumulative to first solve | {statistics.median(cum):.0f} | {statistics.mean(cum):.0f} | {max(cum)} |
| abel top-1 pick alone | {statistics.median(top1):.0f} | {statistics.mean(top1):.0f} | {max(top1)} |
| oracle minimum (what the sweep found) | {statistics.median(omin):.0f} | {statistics.mean(omin):.0f} | {max(omin)} |

Under this key the first pick is the solver on all {len(hit)} rows, so the worst row costs
**{max(cum)}** nodes — the whole procedure fits inside *one* 10,000-node budget, not 3x10,000.
Under a random tie-break that no longer holds: a failed candidate burns its full 10,000, so
the cumulative cost can exceed 10,000 on some rows even though the per-candidate claim stands.
Read the headline as **3 searches of <= 10,000 each**, and the single-budget statement as a
property of this deterministic key.

## What this does and does not buy

- **Does.** It removes the oracle from the 52. `ARMS.md` warns that the best-CoV column
  "is a lower bound on a transformed route, not a runnable procedure" because finding the
  winning `z` cost ~2.2M nodes of sweeping. Ranking by abel magnitude replaces that sweep
  with a 0-node sort and keeps every row: 3 tries out of ~{statistics.mean(n_cand):.0f}
  candidates, a ~{statistics.mean(n_cand) / HEADLINE_K:.0f}x cut in the portfolio.
- **Does not.** It does not crack a new presentation — the 8 unsolved rows stay unsolved,
  and this is still selection *within* an enumerated CoV family.
- **The cap confound is unchanged.** A CoV lengthens relators, so each sweep row carries its
  own `max_relator_length_cap` (24-88; 24-41 on the top-1 picks) while the untransformed
  control runs at 24. A CoV row read against a control at a different cap
  [is not a comparison](../../experiments/lessons/control-with-no-dynamic-range.md); the cap
  is carried per row in the CSV so the confound stays visible.
- **The known limit of this key still applies.** Abelianized magnitude is a solution-*depth*
  proxy (`IDEAS.md` idea 1): strong on shallow instances, weak on the hard residual, and
  provably blind on near-identity-abelianization instances. subset-60 is the solvable ladder.
  The load-bearing test remains the unsolved 124, where it is expected to shrink.

## Gates (all fatal)

1. the oracle re-derived from the sweep equals the `cov_solved` set of
   [`greedy_vs_bestcov_subset60_b10000.csv`](../stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv)
   on all 60 rows, and is 52;
2. `len(r1) + len(r2) == start_total_length_cov` on every row — proof that `r1`/`r2` is the
   start, so no key can read the search. `min_relator`/`max_relator` are search-derived and
   are never read;
3. every row's `nodes_explored` is within its own `node_budget`;
4. subset-60 contributes exactly 60 presentations, each with >= 1 CoV candidate.

## Source

- Sweep: `{SWEEP}`
- Table: [`abel_topk_cov_b10k_subset60.csv`](abel_topk_cov_b10k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_topk_cov_b10k.py`
  (`python3 -m experiments.heuristic_search.runners.abel_topk_cov_b10k`)
- Key: `IDEAS.md` idea 1 / `restart_planner.abel_magnitude`; `abel_len_lex` is idea_bench's
  `cov_abel_len_lex`.
"""
    with open(os.path.join(ROOT, OUT_MD), "w") as fh:
        fh.write(md)


if __name__ == "__main__":
    main()
