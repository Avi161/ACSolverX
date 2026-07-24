# [2026-07-24] A "decidable subset" is defined by the configs in the file — never compare two runs' counts across it [TRAP]

The heuristic program scores orderings on the **decidable subset**: the rows that some config solves and some does not, at that budget. It is the right denominator — it strips the saturated easy rows (every ordering solves them) and the unreachable ones (nothing does), leaving only rows that can separate two orderings. But it is computed *from the configs present in the file*, so it is a property of the run, not of the benchmark.

EXP-10 (a 400-config refinement round) compared its best against the standing best from an earlier run, and reported:

```
standing best on aut_train @1000 (from the finalists):  10/24 decidable
round-two best:                                         20/24 decidable
=> "Round two found a better config."
```

That was false. The prior's `10` was computed on the **finalists' own 11-row** decidable set; the `24` in the denominator came from **EXP-10's** decidable set. Two different row sets, one printed as though it were the other. Scored on the same 24 rows, the finalist knot climb, the finalist block climb, and round-two's winner all reach **20/24** — a dead tie. Round two gained nothing.

The failure is quiet in the worst way: both numbers are individually correct, the ratio looks plausible, and the conclusion ("a breakthrough on the second round") is exactly what a tuning loop is hoping to find, so nothing about it invites suspicion.

## The second guard, which caught the same claim independently

The run also measured its own selection optimism by half-splitting the slice: **1.23 presentations** for a best-of-400 pick, across **7 distinct half-split winners** — against EXP-04's 0.20 with a single winner taking 100% of splits. A margin has to exceed that optimism before it means anything. The verdict is now gated on it:

```python
margin = dsolved(best) - prior[0]
if margin > opt["optimism"]:   # a real candidate
elif margin > 0:               # inside the noise -- recommendation stands
else:                          # a tie
```

Had the denominators matched but the margin been a genuine +1, the optimism gate would still have refused to call it a finding.

## Rule

**Two counts are comparable only when they are counts over the same rows.** When a metric's denominator is derived from the data in a file — a decidable subset, a both-solved set, a discordant-pair count — recompute it once, over a fixed row set, and score every arm against that. Never take a stored score from one run and print it against another run's denominator.

And when a refinement round says it beat the thing it was seeded from, **assume the comparison is broken until the denominators are shown to match** — then check the margin against the measured selection optimism. Best-of-N against a small row set reaches the ceiling by chance; that is what the optimism figure is for, and it should gate the verdict in code, not in the reader's head. Related: [a good ordering feature is not a good progress proxy](knot-progress-is-not-a-solve-predictor.md).
