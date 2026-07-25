# EXP-15 — does the best knot weight depend on how hard the presentation is?

The direct form of the user's intuition. EXP-13 varied the knot weight by the length of a state *inside* a search; this varies it across **presentations**, scoring each weight separately within each difficulty stratum and asking whether the argmax moves. Ordering is the phased winner's shape: pure length below 16, `L + k·knots` above it, with only `k` varying.

Difficulty is the baseline's grading, so this says "the weight depends on baseline-difficulty" — which is still what a caller can condition on, since they know it before the search starts.

## Budget 500

| stratum | n | k=0.5 | k=1 | k=2 | k=3 | k=4 | k=6 | k=8 | k=12 | k=16 | k=24 | k=32 | best k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| easy (bins 0-3) | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 15 | **0.5** _(saturated — every weight solves it; no argmax)_ |
| mid (bins 4-5) | 8 | 3 | 2 | 4 | 3 | 3 | 5 | 7 | 7 | 7 | 6 | 6 | **8** _(threshold k≥8)_ |
| hard (bins 6-7) | 8 | 0 | 0 | 0 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | **4** _(threshold k≥4)_ |
| unreachable (bins 8-9) | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0.5** _(flat — no dynamic range)_ |

## Budget 1000

| stratum | n | k=0.5 | k=1 | k=2 | k=3 | k=4 | k=6 | k=8 | k=12 | k=16 | k=24 | k=32 | best k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| easy (bins 0-3) | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 15 | **0.5** _(saturated — every weight solves it; no argmax)_ |
| mid (bins 4-5) | 8 | 5 | 4 | 4 | 5 | 5 | 6 | 8 | 8 | 8 | 7 | 7 | **8** _(threshold k≥8)_ |
| hard (bins 6-7) | 8 | 0 | 0 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | **3** _(threshold k≥3)_ |
| unreachable (bins 8-9) | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0.5** _(flat — no dynamic range)_ |

## Verdict

- budget 500: mid needs **k≥8** (solves 3→7 of 8); hard needs **k≥4** (solves 0→2 of 8)
- budget 1000: mid needs **k≥8** (solves 5→8 of 8); hard needs **k≥3** (solves 0→3 of 8)

### What the numbers actually say

The interesting structure is not where the optimum sits — past a point the magnitude stops mattering — but that **the hard strata solve nothing at all until the knot term is heavy enough**, while the easy stratum solves everything at every weight:

- budget 500, hard (bins 6-7): **0 solved** below k=4, 2/8 at and above it.
- budget 1000, hard (bins 6-7): **0 solved** below k=3, 3/8 at and above it.

So the user's intuition is **supported in the form that matters, and not in the form it was posed**. Knots are not merely *worth more* on hard presentations — on the hard stratum they are the difference between solving several and solving **none**, whereas on the easy stratum the knot weight is irrelevant. What does *not* hold is the smooth version: the optimal magnitude does not keep climbing with difficulty. It is a threshold to clear, not a dial to turn up.

Practical consequence: there is nothing to gain from tuning the knot weight per presentation. Pick one comfortably above the threshold — the phased winner's 8 to 9 sits there — and it serves every stratum at once.

