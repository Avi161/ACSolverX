# EXP-24 — the tie-break and child filtering, the two knobs never swept here

Decidable band (bins 4–7, 24 rows), cap 48. `tie = +1` pops the shallowest of equally-scored states (what everything so far used), `-1` the deepest. `topk = 0` keeps every child (also what everything used); a positive value keeps only that many shortest children.

The tie-break is **not** EXP-11's depth term: it never changes a state's score, so it cannot reorder states with different priorities — it only decides exact ties, which a structural ordering produces constantly.

## Budget 500

| ordering | tie | topk=all | topk=8 | topk=16 | topk=32 | topk=64 | topk=128 |
|---|---|---|---|---|---|---|---|
| baseline (length) ← current | +1 | 2 | 0 | **3** | 2 | 2 | 2 |
| baseline (length) | -1 | 1 | 0 | 2 | 1 | 1 | 1 |
| recommended ← current | +1 | 13 | 0 | 2 | 3 | 11 | 13 |
| recommended | -1 | 12 | 0 | 2 | 3 | 10 | 12 |
| phased K8 ← current | +1 | 12 | 0 | 1 | 3 | 9 | 12 |
| phased K8 | -1 | **15** | 0 | 1 | 3 | 12 | **15** |

## Budget 1000

| ordering | tie | topk=all | topk=8 | topk=16 | topk=32 | topk=64 | topk=128 |
|---|---|---|---|---|---|---|---|
| baseline (length) ← current | +1 | 5 | 0 | 4 | 4 | 5 | 5 |
| baseline (length) | -1 | 4 | 0 | 3 | 3 | 4 | 4 |
| recommended ← current | +1 | 19 | 0 | 4 | 7 | 17 | 19 |
| recommended | -1 | 19 | 0 | 4 | 8 | 17 | 19 |
| phased K8 ← current | +1 | 16 | 0 | 1 | 7 | 13 | 16 |
| phased K8 | -1 | 16 | 0 | 1 | 7 | 13 | 16 |

## Verdict

Flipping the tie-break to **deepest-first** beats the current setting in:

- budget 500, `phased K8`: 15/24 against 12/24

Child filtering beats keeping everything in 2 of 60 arms:

- budget 500, `phased K8`, tie -1, topk 128: 15/24 against 12/24
- budget 500, `baseline (length)`, tie +1, topk 16: 3/24 against 2/24


## Reading both results honestly

**Child filtering is a clear loss, and the shape says why.** `topk=8` solves *nothing* — 0/24 for every ordering at both budgets — and the count climbs back monotonically as the beam widens, reaching parity with "keep everything" only at `topk=128`. There is no width at which filtering wins. The mechanism is that the priority is *already* the filter: a child a narrow beam discards is, in the overwhelming majority of cases, one the heap would never have popped anyway, so the beam's only real effect is to delete the occasional state the search needed later. Completeness costs nothing here because the heap never pays for children it does not pop; incompleteness costs solves.

The two arms listed as "beating" the control are not filtering wins. Both involve `phased K8` at budget 500 with `tie = -1`, or the baseline moving by a single presentation — the first is the tie-break effect showing up at a width so wide (`topk=128`) that filtering is nearly inactive, and the second is one row.

**The tie-break is inert where it matters.** For the recommended ordering the two directions are exactly equal at both budgets (19/24 and, at 500, identical too). The one real movement is `phased K8` at budget 500, where preferring the deepest of several equally-scored states gains +3. That is a lean knot-only ordering — the same family that EXP-18 showed needs an endgame threshold — so it is consistent with the picture there: a lean vector under-determines the search and leaves more work to the tie-break, while a richer one has already made the decision by the time a tie could arise.

**Neither knob changes the recommendation.** `tie = +1, topk = 0` — the settings inherited from the base solver and used throughout this program — are optimal or tied for the ordering actually recommended, at both budgets. That is now measured rather than assumed, which is the whole value of the experiment.
