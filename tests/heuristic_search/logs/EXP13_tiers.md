# EXP-13 — three tiers, and a knot weight that rises with length

Endgame boundary fixed at 16 (every two-tier winner agreed on it); the second boundary and the two knot coefficients vary. **rising** = a larger knot coefficient on the longer tier, the user's "knots matter more when it is harder" made state-pure through length. **falling** = the same ladder inverted, which is the control: if it does as well, the ladder is adding parameters rather than encoding the idea.

## Budget 500 — decidable subset (8 rows)

Baseline **0/8**. Best two-tier incumbent **8/8**.

| mid boundary | rising (k_mid → k_long) | falling |
|---|---|---|
| 24 | **5** (6→16), **4** (4→12), **4** (2.5→9) | **6** (16→6), **6** (12→4), **4** (9→2.5) |
| 28 | **4** (6→16), **2** (4→12), **2** (2.5→9) | **5** (16→6), **5** (12→4), **5** (9→2.5) |
| 32 | **4** (6→16), **2** (4→12), **2** (2.5→9) | **6** (16→6), **6** (12→4), **6** (9→2.5) |
| 40 | **6** (6→16), **4** (4→12), **2** (2.5→9) | **8** (16→6), **8** (12→4), **8** (9→2.5) |

A third tier **matches** the two-tier incumbent (8) and costs two more parameters — prefer two tiers. Falling beats rising (8 vs 6) — the opposite of the intuition, and worth not over-reading at this sample size.

## Budget 1000 — decidable subset (9 rows)

Baseline **2/9**. Best two-tier incumbent **9/9**.

| mid boundary | rising (k_mid → k_long) | falling |
|---|---|---|
| 24 | **5** (6→16), **4** (4→12), **4** (2.5→9) | **6** (16→6), **6** (12→4), **4** (9→2.5) |
| 28 | **5** (6→16), **4** (4→12), **3** (2.5→9) | **6** (16→6), **6** (12→4), **6** (9→2.5) |
| 32 | **5** (6→16), **4** (4→12), **4** (2.5→9) | **7** (16→6), **7** (12→4), **7** (9→2.5) |
| 40 | **7** (6→16), **6** (4→12), **4** (2.5→9) | **9** (16→6), **9** (12→4), **9** (9→2.5) |

A third tier **matches** the two-tier incumbent (9) and costs two more parameters — prefer two tiers. Falling beats rising (9 vs 7) — the opposite of the intuition, and worth not over-reading at this sample size.


## What this does and does not test

The long tier is genuinely occupied, so the ladder was really exercised: under the phased knot ordering on bins 4-7 at budget 1000, **88.1%** of discovered states have total length > 24, 55.9% exceed 32, and 19.4% exceed 40. A "falling" arm is therefore not just the two-tier incumbent in disguise.

So the measurement stands: the knot coefficient wants to be **larger on the middle tier and smaller on the longest one**. Read mechanically that is sensible — once a pair is very long the thing blocking progress is length itself, and an ordering that keeps paying for knots up there wanders instead of coming back down.

**But this is not the user's claim.** The intuition was that reducing a knot is worth more on a *hard presentation* than an easy one. This experiment varies the knot weight by the **length of a state inside one search**, which is a different quantity: a hard presentation can start short, and every search passes through long states regardless of how hard its presentation is. Length is a within-trajectory coordinate, not a per-problem difficulty. The direct test of the user's claim is whether the best knot weight differs between easy and hard *presentations* — EXP-15.
