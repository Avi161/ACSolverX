# AC19 100k residuals at a 1,000,000-node budget — results

Run 2026-08-28, two parallel Colab sessions (CPU high-RAM), engine `hcompact`,
cap 48, budget 1,000,000. Inputs are the 100k residual lists
(`../ac19_autmin_screen/unsolved_100k_{baseline,s20_mk2}.csv`); provenance for
those is [`UNSOLVED_AFTER_100k.md`](../ac19_autmin_screen/UNSOLVED_AFTER_100k.md).

| | |
|---|---|
| rows | `greedy` 222 (all its 100k failures), `s20_mk2` 39 |
| budget / cap | **1,000,000** / 48 |
| engine | `hcompact` — the engine the 100k wave used, so node counts splice |
| completeness | 222/222 and 39/39, no resume holes |

**Integrity check passed.** Every row here failed at 100,000 in the run that built
the list, so no row may come back solved at or below 100,000 nodes. None did
(`<= 100,000: 0` on both arms), and every unsolved row exhausted the budget
exactly. The search that ran is the search that built the list.

## Headline

| arm | solved at 1M | still unsolved |
|---|---:|---:|
| `greedy` (total length) | **134/222** (60.4%) | 88 |
| `s20_mk2` (`L + 20·S + 2·MK`) | **25/39** (64.1%) | 14 |

On the common denominator (dropping `ac19_33435`, the one orbit outside the
70,723 both arms searched at 10k): `greedy` 134/221, 87 unsolved.

### Anytime, free by the prefix property

A row solved after *N* pops was solved at every budget above *N*, so one run
answers all of them with no second search.

| arm | ≤100k | ≤250k | ≤500k | ≤1M |
|---|---:|---:|---:|---:|
| `greedy` | 0 | 61 | 107 | 134 |
| `s20_mk2` | 0 | 19 | 21 | 25 |

## Head-to-head on the 39 rows both arms ran

These 39 are the genuinely hard tail — the orbits **both** orderings failed at
100,000 — and they are a strict subset of the greedy arm's 222, so this is a
paired comparison on a common denominator.

| | |
|---|---:|
| `greedy` solves | **0/39** |
| `s20_mk2` solves | **25/39** |
| `s20_mk2`-only | 25 |
| `greedy`-only | 0 |
| both | 0 |
| neither | 14 |

**McNemar 25–0, Δ +25.** A strict superset once again: `s20_mk2` recovers 25
orbits the length ordering does not reach at ten times the budget, and loses
nothing the other way. The same shape the 1k → 10k → 100k waves showed, now at
the point where the length ordering has stopped making progress on this tail
altogether.

## Nodes and path length

**The subset solved by both arms is empty (n = 0)** — `greedy` solved none of the
39 rows the two arms share. There is therefore no joint denominator, and no
fair paired cost comparison can be computed from this run. That absence is the
result, not a gap in the analysis.

Each arm over everything it solved:

| arm | n | mean nodes | median nodes | mean path | median path |
|---|---:|---:|---:|---:|---:|
| `greedy` | 134 | 335,054 | 254,160 | 68.3 | 67 |
| `s20_mk2` | 25 | 279,651 | 169,589 | 90.1 | 77 |

**These two rows are not comparable.** They are disjoint populations of different
difficulty: every one of the greedy arm's 134 solves comes from the 183 orbits
`s20_mk2` never had to run (it had already solved them by 100k), while all 25 of
the `s20_mk2` solves come from the 39 that beat both arms at 100k. Solved-only
means are biased in the usual direction too — an arm that reaches further picks
up harder residuals and inflates its own mean.

Longer paths on `s20_mk2` (median 77 vs 67) are consistent with every earlier
wave: the gain is node efficiency, never shorter certificates. Do not read it as
a cost, and do not claim shorter proofs.

Including censored rows, over every row each arm ran:

| arm | n | mean nodes | median nodes | censored at 1M |
|---|---:|---:|---:|---:|
| `greedy` | 222 | 598,636 | 527,710 | 88 |
| `s20_mk2` | 39 | 538,238 | 259,825 | 14 |

## Census-wide: the 70,636 orbits both arms solve

The sections above cover only the hard tail this run escalated. Splicing all
three waves — 10k census, 100k residual, 1M residual — gives the per-arm
`solved_at` for every orbit, and a fair paired cost comparison over the whole
screen. All three ran `hcompact` at cap 48, so node counts splice without
adjustment.

| | |
|---|---:|
| joint denominator (a row for **both** arms) | **70,723** |
| `greedy` solves | 70,636 — 87 unsolved |
| `s20_mk2` solves | 70,709 — 14 unsolved |
| **solved by both** | **70,636** (99.88%) |

`s20_mk2`'s 14 unsolved are a strict subset of `greedy`'s 87. Nothing the length
ordering solves is lost.

### Nodes and path on the 70,636 solved by both

| arm | mean nodes | median | mean path | median path |
|---|---:|---:|---:|---:|
| `greedy` | **1,197.8** | **14** | 23.58 | 10 |
| `s20_mk2` | **284.2** | **14** | 26.64 | 11 |

Node geo-mean ratio `s20_mk2`/`greedy`: **0.800**. Total node-work across the set:
84,611,237 against 20,076,547 — a **4.2×** reduction in aggregate search.

The identical medians and the 4.2× mean gap are the same fact seen twice: most of
the census is trivial (p50 is 14 nodes for both arms), and the entire saving lives
in the tail.

| arm | p50 | p75 | p90 | p99 | p99.9 | max |
|---|---:|---:|---:|---:|---:|---:|
| `greedy` nodes | 14 | 100 | 786 | 10,771 | 253,986 | 948,266 |
| `s20_mk2` nodes | 14 | 61 | 372 | 4,165 | 32,914 | 95,944 |
| `greedy` path | 10 | 22 | 55 | 191 | — | 502 |
| `s20_mk2` path | 11 | 23 | 57 | 248 | — | 783 |

### The ratio is monotone in difficulty

Binned by how hard the row was for the **length baseline**, so the strata are
defined without reference to the arm being judged:

| `greedy` nodes | n | `greedy` mean | med | `s20_mk2` mean | med | geo ratio | `g` path | `s` path |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [0, 10) | 23,537 | 7 | 7 | 8 | 7 | **1.092** | 6 | 6 |
| [10, 100) | 29,431 | 29 | 19 | 27 | 16 | 0.890 | 11 | 12 |
| [100, 1,000) | 11,165 | 331 | 268 | 267 | 126 | 0.542 | 38 | 37 |
| [1,000, 10,000) | 5,761 | 3,005 | 2,833 | 1,714 | 1,211 | 0.364 | 101 | 121 |
| [10,000, 100,000) | 608 | 29,082 | 22,524 | 7,762 | 3,200 | 0.166 | 68 | 66 |
| [100,000, +) | 134 | 335,054 | 254,160 | 11,356 | 3,118 | **0.012** | 67 | 61 |

`s20_mk2` is **slightly worse than length on the trivial rows** (ratio 1.09 on the
23,537 that finish inside ten nodes — the structural terms buy nothing there and
cost a little), and the advantage grows monotonically with difficulty to ~80×
fewer nodes on the hardest bin. A single headline ratio averages those two
regimes together and describes neither.

**Path length is still not improved.** Across the joint set `s20_mk2` is shorter
on 16,306 rows, longer on 23,855, tied on 30,475 — it loses that comparison, as it
has in every wave. The gain is node efficiency. Do not claim shorter proofs.

### Which wave cracked each row

| arm | ≤10,000 | ≤100,000 | ≤1,000,000 |
|---|---:|---:|---:|
| `greedy` | 69,894 | 608 | 134 |
| `s20_mk2` | 70,440 | 196 | 0 |

`s20_mk2` contributes 0 at the 1M column *of the joint set* by construction: its 25
solves there are all rows `greedy` never solved, so they cannot be in a
both-solved denominator.

## The residual: 14 orbits survive both orderings at 1,000,000

Unsolved by `greedy` **and** `s20_mk2` at a million nodes, cap 48:

```
ac19_7284   ac19_12445  ac19_16286  ac19_27254  ac19_27683  ac19_28131
ac19_28930  ac19_31298  ac19_44381  ac19_50841  ac19_51034  ac19_54835
ac19_59576  ac19_65753
```

These are `Aut(F₂)`-**minimal representatives**, so a failure is a failure for
this representative — difficulty is not orbit-invariant and another member of the
orbit may be easier.

## Cost

| arm | total | median row | slowest row |
|---|---:|---:|---:|
| `greedy` | 60.9 core-h | 12.5 min | 53.3 min |
| `s20_mk2` | 6.8 core-h | 6.0 min | 25.0 min |

## Caveat: these solves are not certificate-backed

`hcompact` reports `path_length` — the solved node's depth — but keeps no path,
so the jsonl carries no `path_moves` and nothing here has been replayed. Earlier
waves of this screen did replay their certificates. To get them, re-run the solved
rows through `heuristics.greedy_search_h`, which is affordable for the 25
`s20_mk2` solves and expensive for the greedy arm's 134.

Until that is done, read the solved counts as what the search reported, not as
verified proofs.

## Files

```
leftovers_1m_greedy_b1000000_mrl48.jsonl    222 rows
leftovers_1m_s20_mk2_b1000000_mrl48.jsonl    39 rows
solved_at_1m_{arm}.txt                       what the extra budget bought
still_unsolved_1m_{arm}.txt                  what survives 1,000,000 nodes
```

Regenerate the tables from the jsonl:

```bash
PYTHONPATH=. python3 -c "
from experiments.search.run_leftovers_1m import report
for a in ('greedy','s20_mk2'): report(a, 'results/heuristic_search/leftovers_1m')"
```
