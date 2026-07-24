# EXP-18 — is 16 still the right endgame boundary?

The phase boundary was fixed at 16 by EXP-03, which swept it **at budget 500 for the simple `L + 8K` ordering**. The recommendation has since moved to a richer climb at budget 1,000 and the boundary was carried along untouched. This re-sweeps it for every climb still in play, on the decidable band (bins 4–7, 24 rows).

`T = 0` means no endgame segment at all — the climb runs everywhere — so it is the control on whether the two-phase shape is doing anything.

## Budget 500

| climb | T=0 | T=8 | T=12 | T=14 | T=16 | T=18 | T=20 | T=24 | T=28 | T=34 | best |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K8 | 9 | 9 | 9 | 9 | **12** | **12** | 8 | 5 | 2 | 2 | 12/24 at T=16,18 |
| K+xyimb | 12 | 12 | 12 | 12 | **16** | 12 | 9 | 5 | 2 | 2 | 16/24 at T=16 |
| richer | 13 | 13 | 13 | 12 | **14** | 11 | 6 | 4 | 2 | 2 | 14/24 at T=16 |
| blocks | **11** | **11** | **11** | **11** | **11** | 10 | 5 | 3 | 2 | 2 | 11/24 at T=0,8,12,14,16 |

## Budget 1000

| climb | T=0 | T=8 | T=12 | T=14 | T=16 | T=18 | T=20 | T=24 | T=28 | T=34 | best |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K8 | 13 | 13 | 13 | 13 | **16** | **16** | 12 | 8 | 5 | 5 | 16/24 at T=16,18 |
| K+xyimb | 12 | 12 | 12 | 12 | 16 | 16 | **17** | 8 | 5 | 5 | 17/24 at T=20 |
| richer | **19** | **19** | **19** | **19** | **19** | **19** | 13 | 8 | 5 | 5 | 19/24 at T=0,8,12,14,16,18 |
| blocks | **19** | **19** | **19** | **19** | **19** | **19** | 17 | 8 | 5 | 5 | 19/24 at T=0,8,12,14,16,18 |

## Does 16 still hold?

- budget 500, `K+xyimb`: yes — 16 is among the optima (16/24).
- budget 500, `K8`: yes — 16 is among the optima (12/24).
- budget 500, `blocks`: yes — 16 is among the optima (11/24).
- budget 500, `richer`: yes — 16 is among the optima (14/24).
- budget 1000, `K8`: yes — 16 is among the optima (16/24).
- budget 1000, `blocks`: yes — 16 is among the optima (19/24).
- budget 1000, `richer`: yes — 16 is among the optima (19/24).
- budget 1000, `K+xyimb`: **no** — best is T=20 at 17/24, against 16/24 at 16 (**+1**).

## Is the endgame phase load-bearing?

`T = 0` removes it entirely. If that matched the best threshold, the two-phase story would be decoration.

| budget | climb | T=0 | best T | difference |
|---|---|---|---|---|
| 500 | K+xyimb | 12/24 | 16/24 (T=16) | **+4** |
| 500 | K8 | 9/24 | 12/24 (T=16) | **+3** |
| 500 | blocks | 11/24 | 11/24 (T=0) | **+0** |
| 500 | richer | 13/24 | 14/24 (T=16) | **+1** |
| 1000 | K+xyimb | 12/24 | 17/24 (T=20) | **+5** |
| 1000 | K8 | 13/24 | 16/24 (T=16) | **+3** |
| 1000 | blocks | 19/24 | 19/24 (T=0) | **+0** |
| 1000 | richer | 19/24 | 19/24 (T=0) | **+0** |

## The finding: the endgame phase is load-bearing only for the LEAN climbs

The pattern across both budgets is sharp and mechanistic, not a tuning artifact:

| climb | terms | endgame worth (500 / 1000) |
|---|---|---|
| `K8` | length + knots | **+3 / +3** |
| `K+xyimb` | length + knots + generator imbalance | **+4 / +5** |
| `richer` | length + knots + max-knots + smaller-block + imbalance | +1 / **+0** |
| `blocks` | length + block extremes | +0 / **+0** |

A climb carrying only a knot term needs the phase switch, and for a reason that is easy to state: near the trivial state there is nothing structural left to buy, so an ordering that keeps paying for knots wanders instead of cancelling. The endgame segment forces it to stop.

The multi-feature climbs do not need it, because they already contain the terms that make them behave near the end. `S` (the smaller mean block) and `MK` both fall as a pair approaches the trivial state, so the climb self-regulates and a hard phase boundary has nothing left to fix.

**Practical consequence, and it simplifies the recommendation.** If you use the recommended richer climb, the threshold is optional — a single weight vector with no segments scores the same 19/24 at budget 1,000. If you use a lean knot-only ordering, the threshold is not optional and 16 is the right value.

`T = 16` remains a safe default everywhere: it is among the optima in 7 of the 8 (budget, climb) cells, and the one exception (`K+xyimb` at 1,000, best T=20) is worth a single presentation.
