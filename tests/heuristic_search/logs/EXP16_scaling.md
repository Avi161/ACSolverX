# EXP-16 — how the advantage scales with budget

A search at budget B is exactly the first B pops of any longer search, so each curve below comes from one 1000-node run per (ordering, presentation): the node count at which it solved is the budget from which it is solved. No extra searching.

## The decidable band (bins 4–7, 24 rows)

| ordering | 50 | 100 | 200 | 300 | 500 | 700 | 1000 |
|---|---|---|---|---|---|---|---|
| baseline (length) | 0 | 0 | 0 | 0 | 2 | 4 | 5 |
| phased K8 | 0 | 4 | 8 | 11 | 12 | 16 | 16 |
| phased K+xyimb | 0 | 4 | 9 | 12 | 16 | 16 | 16 |
| richer knot climb | 0 | 0 | 5 | 8 | 14 | 15 | 19 |

### The gap against the baseline

| ordering | 50 | 100 | 200 | 300 | 500 | 700 | 1000 | shape |
|---|---|---|---|---|---|---|---|---|
| phased K8 | +0 | +4 | +8 | +11 | +10 | +12 | +11 | widening / tail flat (±1) |
| phased K+xyimb | +0 | +4 | +9 | +12 | +14 | +12 | +11 | widening / tail **turning over** |
| richer knot climb | +0 | +0 | +5 | +8 | +12 | +11 | +14 | widening / tail **still growing** |

## What this implies for a Colab-scale run

Over the whole range every finalist widens its gap — which it must, since the baseline solves nothing below 500. The question that bears on a 10^5–10^6 run is the **tail**: is the gap still growing where the budget runs out, or has it already turned over?

Change in the gap from budget 500 to 1,000, which is the only part of these curves that speaks to a larger run. One solve on 24 rows is inside the jitter, so a tail is only called a trend at ±2 or more.

| ordering | gap @500 | gap @1000 | change | reading |
|---|---|---|---|---|
| phased K8 | +10 | +11 | +1 | flat (±1) |
| phased K+xyimb | +14 | +11 | -3 | **turning over** |
| richer knot climb | +12 | +14 | +2 | **still growing** |

Only **`richer knot climb`** is still converting budget into new solves where the local ceiling cuts the curve off. The leaner orderings peak in the middle of the range and hold or give ground back: they find their solutions early and then stop finding new ones. That is the same crossover EXP-06 found by a completely different route — the richer climb gained 25→29 with budget while the lean winner plateaued 27→27. **Two independent measurements agreeing on which ordering keeps scaling is the strongest evidence in this program for what to run at 10^5–10^6 nodes.**

## Where each ordering's solves land in time

Median solving budget on the rows each one solves — a low median with a high final count means it finds its solutions early and keeps finding more.

| ordering | rows solved by 1000 | median solving budget | max |
|---|---|---|---|
| baseline (length) | 5/24 | 558 | 875 |
| phased K8 | 16/24 | 202 | 597 |
| phased K+xyimb | 16/24 | 180 | 408 |
| richer knot climb | 19/24 | 388 | 773 |
