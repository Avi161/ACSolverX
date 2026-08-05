# Abelianized-magnitude top-K CoV selection @ budget 10,000 (subset-60)

**No search.** Every number is a row of the frozen
[`covsweep_10000_66_*.jsonl`](../stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl) selected by a key
computed from the two *start* strings. 0 nodes explored by this runner.

## The claim under test

`benchmark/subsets/ARMS.md` reports **best CoV @10k = 52/60**, and calls it an oracle: the
cheapest of 11-173 subword CoVs per presentation (mean
103), found by sweeping all of them. The question is whether a
**search-free** key picks a solver out of that family in a handful of tries.

The key is `IDEAS.md` idea 1's abelianized magnitude — the sum of the absolute abelianized
exponent sums of the transformed pair:

```text
abel(r1, r2) = |sigma_x(r1)| + |sigma_y(r1)| + |sigma_x(r2)| + |sigma_y(r2)|
```

## Headline

**Ranking a presentation's CoV candidates by abelianized magnitude and running the top 3,
each at 10,000 nodes, solves 52/60 — the oracle's set exactly, 0 misses.**

| arm @ budget 10,000 | solved |
|---|---:|
| plain greedy, untransformed start (`n_cov = 0` control row) | **40/60** |
| best CoV — oracle over all ~103 candidates | **52/60** |
| **abel top-3, `(abel, start_len, longest)` key** | **52/60** |
| abel top-3, bare `abel` key, random tie-break (median of 300) | **52/60** |
| abel top-3, bare `abel` key, adversarial tie-break | **50/60** |
| length-only top-3 (control) | **49/60** |
| random top-3 (null, 300 trials) | **48.5/60** |

The adversarial row is the floor: even if every tie at the abel minimum is resolved by an
enemy, top-3 still reaches 50/60. The claim is not
tie-break luck.

52 is the ceiling of this data, not of the method: the other 8 rows
(622, 623, 624, 625, 636, 637, 638, 639 — one Aut class) are solved by
**no** CoV in the sweep at 10,000 and need budget 20,000, so no ranking can reach them here.

## Every arm, every K (deterministic `(z, iso_gen, iso_index)` tie-break)

| arm | K=1 | K=2 | K=3 | K=4 | K=5 | K=10 |
|---|---:|---:|---:|---:|---:|---:|
| `abel` | 52 | 52 | 52 | 52 | 52 | 52 |
| `abel_len` | 51 | 52 | 52 | 52 | 52 | 52 |
| `abel_len_lex` | 52 | 52 | 52 | 52 | 52 | 52 |
| `len_only` | 47 | 48 | 49 | 49 | 51 | 51 |
| `random` (mean of 300) | 41.8 | 46.6 | 48.5 | 49.7 | 50.6 | 51.7 |

Abel beats length-only at every K, so it is not a length proxy — consistent with idea 1's
length-residualized AUC of 0.92.

## Ties are why the claim says 3, not 1

A median of **6** candidates (max 21) tie at the abel
minimum, so under the bare key K=1 measures the tie-break as much as the key itself.
Resolving every tie *against* the arm and *for* it brackets the truth:

| arm | K=1 | K=2 | K=3 | K=4 | K=5 | K=10 |
|---|---:|---:|---:|---:|---:|---:|
| `abel` adversarial (worst tie-break) | 27 | 48 | 50 | 50 | 51 | 52 |
| `abel` + random tie-break, min of 300 | 42 | 50 | 51 | 51 | 52 | 52 |
| `abel` + random tie-break, median | 48 | 52 | 52 | 52 | 52 | 52 |
| `abel` optimistic (best tie-break) | 52 | 52 | 52 | 52 | 52 | 52 |
| `abel_len_lex` adversarial | 52 | 52 | 52 | 52 | 52 | 52 |

At K=1 the bare key's bracket is wide —
**27-52**, and a random
tie-break lands at a median of 48. By K=3 it has
closed to **50-52**,
with a random-tie-break median of 52 and a worst
observed trial of 51. **So K=1 is not a result and K=3 is** — three
tries is where the bare key stops depending on how ties are broken.

Adding the two other static fields removes the ties instead of surviving them:
`abel_len_lex` ranks 52/60 at K=3
even under an adversarial tie-break, because exact `(abel, start_len, longest)` ties are rare.
Either route gets to 52; the bare key needs K=3 to get there safely, which
is why the claim is stated at 3.

## Cost

Sequential top-3, stopping at the first solve, over the 52 rows it solves:

| | median nodes | mean nodes | max nodes |
|---|---:|---:|---:|
| abel top-3, cumulative to first solve | 35 | 1080 | 7875 |
| abel top-1 pick alone | 35 | 1080 | 7875 |
| oracle minimum (what the sweep found) | 24 | 530 | 3359 |

Under this key the first pick is the solver on all 52 rows, so the worst row costs
**7875** nodes — the whole procedure fits inside *one* 10,000-node budget, not 3x10,000.
Under a random tie-break that no longer holds: a failed candidate burns its full 10,000, so
the cumulative cost can exceed 10,000 on some rows even though the per-candidate claim stands.
Read the headline as **3 searches of <= 10,000 each**, and the single-budget statement as a
property of this deterministic key.

## What this does and does not buy

- **Does.** It removes the oracle from the 52. `ARMS.md` warns that the best-CoV column
  "is a lower bound on a transformed route, not a runnable procedure" because finding the
  winning `z` cost ~2.2M nodes of sweeping. Ranking by abel magnitude replaces that sweep
  with a 0-node sort and keeps every row: 3 tries out of ~103
  candidates, a ~34x cut in the portfolio.
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

- Sweep: `results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl`
- Table: [`abel_topk_cov_b10k_subset60.csv`](abel_topk_cov_b10k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_topk_cov_b10k.py`
  (`python3 -m experiments.heuristic_search.runners.abel_topk_cov_b10k`)
- Key: `IDEAS.md` idea 1 / `restart_planner.abel_magnitude`; `abel_len_lex` is idea_bench's
  `cov_abel_len_lex`.
