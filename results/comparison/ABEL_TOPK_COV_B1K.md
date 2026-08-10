# Abelianized-magnitude top-K CoV selection @ budget 1,000 (subset-60)

**No search.** Every number is a row of the frozen [`covsweep_1000_66_*.jsonl`](../stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl) selected by a key computed from the two *start* strings. This runner explores 0 nodes.

This is the budget-1,000 replication of [`ABEL_TOPK_COV_B10K.md`](ABEL_TOPK_COV_B10K.md), run to test whether that file's headline was a property of the key or of the budget it was measured at.

## Headline

| arm @ budget 1,000 | solved /60 | orbits /45 |
|---|---:|---:|
| plain greedy, untransformed start (`n_cov = 0` control row) | **29/60** | 29/45 |
| **abel top-3, bare `abel` key** (pre-committed headline) | **41/60** | 39/45 |
| abel top-3, `(abel, start_len, longest)` — the 10k key | 41/60 | 39/45 |
| length-only top-3 ("smallest length"), the control | 39/60 | 37/45 |
| random top-3, exact expectation | 36.1/60 | — |
| random top-3, 2,000-trial mean (min–max) | 36.1/60 (31–41) | — |
| best CoV — **oracle** over all ~103 candidates | **45/60** | 41/45 |

Against the untransformed greedy baseline of **29/60**, abel top-3 is **+12** presentations for at most 3 searches of <= 1,000 nodes each. Against the oracle's 45/60 it gives up **4**, so it recovers **91%** of the oracle from 3 tries out of ~103 — a ~34x cut in the portfolio.

**The 10k result does not replicate exactly, and that is the finding.** At 10,000 the key matched the oracle with 0 misses (52/52). At 1,000 it misses 4 of 45: 581, 586, 634, 635. The key is a real signal — it beats every control at every K below — but "recovers the oracle exactly" is a statement about budget 10,000, not about the key.

**The misses are needles, and abel still finds them faster than chance.** Each of those 4 presentations has exactly **one** solving candidate in its whole family:

| pres | candidates | solvers | abel rank of the solver | expected rank if abel were noise |
|---|---:|---:|---:|---:|
| 581 | 109 | 1 | **5** | 55 |
| 586 | 109 | 1 | **9** | 55 |
| 634 | 138 | 1 | **30** | 70 |
| 635 | 134 | 1 | **36** | 68 |

A top-3 arm cannot be expected to hit a 1-in-109 needle — random top-3 finds it 2.8% of the time. On 2 of the 4 the key still puts the unique solver in the top 10 of 109+. The gap to the oracle here is a budget-K limit, not the key failing.

## Is it beating the controls, or beating nothing?

| comparison | abel top-3 | control | gap |
|---|---:|---:|---:|
| vs random (null, exact) | 41 | 36.1 | **+4.9** |
| vs random (null, 2,000 trials) | 41 | 36.1 | one-sided p = **0.0010** (2/2,000 trials reached it) |
| vs length-only (is abel a length proxy?) | 41 | 39 | **+2** |
| length-only vs random | 39 | 36.1 | one-sided p = 0.0650 |

The length-only control is the load-bearing one: shorter relators are easier, so any key correlated with length gets credit it did not earn. Abel beats it by 2 at K=3, and at every K in the table below.

**Effect size in the only band that is measurable here.** Random already reaches 36.1/60 and the oracle caps at 45/60, so the whole discriminable range is 8.9 presentations wide. Abel closes **55%** of that random-to-oracle band; length-only closes 33%. Quoting "41/60" without the 36.1/60 floor overstates what the ranking is doing.

### The paired tests (a difference of totals is not evidence)

Two arms scored on the same 60 presentations are paired, so only rows where exactly one arm solves carry information. Exact McNemar on the discordant rows:

| pair | solved only by A | solved only by B | two-sided exact p |
|---|---|---|---:|
| **A = abel top-3**, B = length-only top-3 | 2 (602, 632) | 0 (none) | **0.500** |
| **A = abel top-3**, B = greedy control | 12 | 0 | 4.88e-04 |

Abel over the untransformed greedy baseline is decisive. **Abel over the length control is not** — at p = 0.500 on 2 discordant rows, the +2 is directionally consistent at every K but individually underpowered on 60 presentations. It should be reported as a consistent direction, not a demonstrated separation.

And the two rows are not abel finding a needle — they are the length key picking *worse than chance*:

| pres | candidates | of which solve | P(random top-3 solves) | abel top-3 | length top-3 |
|---|---:|---:|---:|:--:|:--:|
| 602 | 134 | 38 | 0.64 | yes | **no** |
| 632 | 169 | 68 | 0.79 | yes | **no** |

A uniform draw would have solved both more often than the length key did. So the honest reading of abel-over-length at this budget is: abel is not worse than random anywhere, and length is worse than random somewhere.

### Where does abel's lead actually come from? Rank by length first, let abel break ties

If abel merely re-expressed length, forcing length to lead and abel to follow would reproduce abel's score. If abel added signal *within* a length stratum, `len_then_abel` would pull clear of the other length keys. It never approaches abel's 41:

| arm | K=1 | K=2 | K=3 | K=4 | K=5 | K=10 |
|---|---:|---:|---:|---:|---:|---:|
| `len_only` — length, then the CoV's own name | 37 | 39 | 39 | 39 | 39 | 40 |
| `len_lex` — length, then longest relator | 36 | 39 | 39 | 39 | 39 | 40 |
| `len_then_abel` — length, then **abel** | 37 | 39 | 39 | 39 | 39 | 40 |
| `abel` — **abel leading** | 38 | 41 | 41 | 41 | 42 | 43 |

**This is a null result and it is informative.** At the headline K=3, `len_then_abel` wins 0 rows against `len_lex` and loses 0 (exact p = 1.000). Across the sweep it is identical to `len_lex` at every K except K=1 (36 → 37, one row, exact p = 1.000) — so the most abel buys at *fixed* start length anywhere on this set is one presentation, at the one K nobody is quoting, and at K=3 it buys nothing. Abel's whole +2 comes instead from the rows where it **overrides** length — picking a longer candidate with a smaller abelianized magnitude and being right.

That rules out the simple "abel is a length proxy" story, since a proxy cannot beat the thing it proxies. It does not establish an independent length-residual signal at this sample size: the effect lives in 2 presentations, and the stratified probe that would confirm it moves by at most a single row (and by none at K=3). Idea 1's length-residualized AUC of 0.92 was measured on a per-candidate ranking over the whole 66-set; this is a 60-presentation top-3 reach test, a far coarser instrument, and it does not reproduce that here.

## Every arm, every K (deterministic `(z, iso_gen, iso_index)` tie-break)

| arm | K=1 | K=2 | K=3 | K=4 | K=5 | K=10 |
|---|---:|---:|---:|---:|---:|---:|
| `abel` | 38 | 41 | 41 | 41 | 42 | 43 |
| `abel_len` | 40 | 41 | 41 | 41 | 41 | 43 |
| `abel_len_lex` | 39 | 41 | 41 | 41 | 41 | 43 |
| `len_only` | 37 | 39 | 39 | 39 | 39 | 40 |
| `len_lex` | 36 | 39 | 39 | 39 | 39 | 40 |
| `len_then_abel` | 37 | 39 | 39 | 39 | 39 | 40 |
| `random` exact expectation | 29.9 | 34.1 | 36.1 | 37.3 | 38.2 | 40.2 |
| `random` mean of 2,000 | 29.9 | 34.1 | 36.1 | 37.4 | 38.2 | 40.2 |
| **oracle (all ~103)** | 45 | 45 | 45 | 45 | 45 | 45 |

## Ties, and why the claim is stated at K=3

A median of **6** candidates (max 21) tie at the abel minimum, so under the bare key K=1 measures the tie-break as much as the key. Resolving every tie *against* the arm and *for* it brackets the truth:

| arm | K=1 | K=2 | K=3 | K=4 | K=5 | K=10 |
|---|---:|---:|---:|---:|---:|---:|
| `abel` adversarial (worst tie-break) | 22 | 38 | 39 | 41 | 41 | 43 |
| `abel` + random tie-break, min of 2,000 | 29 | 39 | 40 | 41 | 41 | 43 |
| `abel` + random tie-break, median | 36 | 41 | 41 | 41 | 41 | 43 |
| `abel` optimistic (best tie-break) | 40 | 41 | 41 | 43 | 43 | 43 |
| `len_only` adversarial | 36 | 38 | 38 | 38 | 38 | 39 |
| `len_only` + random tie-break, median | 36 | 38 | 38 | 38 | 39 | 40 |
| `len_only` optimistic | 37 | 39 | 39 | 39 | 39 | 40 |

At K=1 the bare key's bracket is **22–40** with a random-tie-break median of 36; at K=3 it is **39–41** with a median of 41. The adversarial row is the floor an enemy tie-break cannot push below; the length control's own adversarial floor is 38, so the two arms are compared at the same standard.

## Orbit level, not row level

subset-60's 60 rows are only **45 distinct Aut classes** — 38 singletons, 4 pairs, 2 triples, and one class of 8. A /60 count therefore weights one orbit up to 8x. Counting a class solved only when **every** member is solved:

| arm | rows /60 | orbits /45 | classes split (some members solved, some not) |
|---|---:|---:|---|
| greedy control | 29 | 29 | none |
| abel top-3 | 41 | 39 | none |
| length-only top-3 | 39 | 37 | none |
| oracle | 45 | 41 | none |

The ordering survives the orbit view, so the headline is not one big Aut class carrying the count.

## The cap confound, measured

A CoV lengthens relators and the sweep sizes each row's cap to `max(24, longest + 16)`, so a transformed row can run at a larger cap than the untransformed control's fixed 24. That is a confound, not a result — [a control with no dynamic range is not a comparison](../../experiments/lessons/control-with-no-dynamic-range.md).

| picks | median cap | max cap | share at cap 24 |
|---|---:|---:|---:|
| abel top-3 | 31 | 41 | 6% |
| length-only top-3 | 27 | 33 | 22% |
| untransformed control | 24 | 24 | 100% |

Both arms draw from the same candidate pool with the same caps, so the abel-vs-length and abel-vs-random comparisons are cap-fair by construction. Only the comparison against the untransformed greedy control carries the confound; the per-pick cap is in the CSV so it stays visible.

## Cost

Sequential top-3, stopping at the first solve, over the 41 rows it solves:

| | median nodes | mean nodes | max nodes |
|---|---:|---:|---:|
| abel top-3, cumulative to first solve | 18 | 166 | 1626 |
| abel top-1 pick alone | 18 | 134 | 1000 |
| oracle minimum (what the sweep found) | 17 | 103 | 632 |

Read the headline as **3 searches of <= 1,000 nodes each**, worst case 3,000 nodes, against the control's one search of <= 1,000.

## Back-applying the same test to PR #14's own budget

PR #14 reports abel top-3 = 52/60 against a length-only control of 49/60 and never pairs them. Re-ranking the 10,000-node sweep with these keys and running the same exact McNemar:

| budget | abel top-3 | length top-3 | discordant | exact p | random floor | oracle ceiling |
|---|---:|---:|:--:|---:|---:|---:|
| 1,000 | 41 | 39 | 2–0 | 0.500 | 36.1 | 45 |
| 10,000 | 52 | 49 | 3–0 | 0.250 | 48.6 | 52 |

Same direction, same shape, same verdict at both budgets: abel never loses a row to the length control, and the win is never statistically separated — 2 discordant rows at 1,000 and 3 at 10,000 are not enough to reject a coin flip. **The abel-beats-length claim is undemonstrated at 10,000 too, not just here.** What *is* decisive at both budgets is abel against the greedy baseline and against random.

Note also how much narrower the discriminable band is at 10,000: random top-3 already reaches 48.6/60 against an oracle of 52/60, so "recovers the oracle exactly" is a 3.4-presentation effect over chance there, versus 8.9 at 1,000. The tighter budget is the *more* discriminating test of the key, and it is the one where the length control is left behind by the wider margin.

## What this replication does and does not establish

- **Does.** The key is not an artefact of budget 10,000. At one tenth the budget it still beats random by 4.9 presentations (p = 0.0010), closing 55% of the random-to-oracle band, and it survives an adversarial tie-break.
- **Does not — separate abel from length at this sample size.** Abel leads the length control at every K, but the paired test on 2 discordant rows gives p = 0.500 and the length-stratified probe (`len_then_abel`) adds nothing at K=3 and one row at K=1. 60 presentations cannot settle a 2-row gap; the direction is consistent, the separation is not demonstrated. The one thing that *is* ruled out is abel being a pure length proxy — it wins by overriding length, not by tracking it.
- **Does.** The pipeline is cross-validated two ways: gate 1 checks the 1k sweep is the 10k sweep truncated on all 6,788 rows, and gate 5 checks this re-ranking reproduces the 41/60 that `abel_double_cov_b1k.py` reached by running live searches.
- **Does not — this is not independent data.** The 1k and 10k sweeps enumerate the *same* candidate set, and the key reads only the start strings, so the abel *ranking* is bit-identical at both budgets; only the solved flags move. This is a budget-robustness check on one frozen sweep, not a second experiment.
- **Does not — subset-60 is in-sample.** Idea 1's abelianized magnitude was developed on the 66-set, of which subset-60 is a part, at every budget. The genuinely held-out test remains the unsolved 124.
- **Does not — it does not crack a new presentation.** The 15 rows no CoV solves here (568, 573, 578, 583, 596, 605, 610, 622, 623, 624, 625, 636, 637, 638, 639) stay unsolved; this is selection *within* an enumerated CoV family.
- **The known limit of the key applies.** Abelianized magnitude is a solution-*depth* proxy: strong on shallow instances, weak on the hard residual, provably blind on near-identity-abelianization instances. That it misses 4 rows here and 0 at 10,000 is consistent with a depth proxy degrading as the budget tightens.

## Gates (all fatal)

1. **truncation** — `solved@1k == (solved@10k and nodes@10k <= 1000)` on all 6,788 rows, with equal nodes, path and cap when both solved;
2. **anti-leak** — `len(r1) + len(r2) == start_total_length_cov` on every row, so `r1`/`r2` is the start and no key can read the search (`min_relator`/`max_relator` are search-derived and never read);
3. **budget** — every row is at `node_budget == 1000` with `nodes_explored <= 1000`;
4. **coverage** — 60 presentations, each with >= 1 CoV candidate and exactly one untransformed control row;
5. **cross-implementation** — `abel_len_lex` top-3 equals the 41/60 that `abel_double_cov_b1k.py`'s `hop1_topk` reached via live search;
6. **selection honesty** — every arm's solved set is a subset of the oracle's.

## Source

- Sweep: `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl`
- Cross-checked against: `results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl`
- Table: [`abel_topk_cov_b1k_subset60.csv`](abel_topk_cov_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_topk_cov_b1k.py` (`python3 -m experiments.heuristic_search.runners.abel_topk_cov_b1k`)
- Key: `IDEAS.md` idea 1 / `restart_planner.abel_magnitude`.
