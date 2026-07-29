# Campaign 12h RESULTS — anti-overfit heuristic evaluation

Advisor **BLOCK**ed fitting weights on the CoV/automorphic unsolved-descended pool.
This campaign is **evaluation-only**: never-read AC1M rows (MS string pairs excluded),
budget **1000**, cap **48**. Negatives = unsolved within budget 1000.

## Screen (length-only, pre-registered denominator)

- Screened: **3500**
- Easy (solved <100 nodes): 2228
- Mid (solved 100–999): 682
- Hard (unsolved @1000): 590
- Solve rate: 2910/3500 (83.1%)

## Go / no-go

**Dynamic range exists** on AC1M (unlike the advisor’s 20-row probe): hundreds of mid and hard rows.
But mid-band **solve rate cannot separate arms** — length solves 100% of mid by construction.
Separation must be read as (1) **hard-band recoveries** and (2) **mid-band speed**.

## Mid-band speed (500 complete rows)

| arm | solved (always ~all) | mean nodes | med nodes | faster than length | slower / failed |
|---|---:|---:|---:|---:|---:|
| `length` | 500/500 | 203.9 | 194 | 0 | 0 |
| `recommended` | 486/500 | 287.2 | 212 | 194 | 306 |
| `mk8` | 453/500 | 355.3 | 245 | 143 | 357 |
| `k8` | 265/500 | 170.9 | 96 | 190 | 310 |
| `kms5` | 487/500 | 227.7 | 168 | 232 | 265 |
| `s24` | 493/500 | 150.8 | 106 | 380 | 118 |

## Hard-band recoveries (47 complete rows)

| arm | solved |
|---|---:|
| `length` | **0/47** |
| `recommended` | **5/47** |
| `mk8` | **2/47** |
| `k8` | **1/47** |
| `kms5` | **6/47** |
| `s24` | **13/47** |

Any non-length arm recovers: **15/47**.

## Verdict (so far)

- On never-read AC1M mid-band, **length-only is hard to beat on solve count** (definitionally).
- Knot-heavy arms (`k8`, `mk8`) are **slower / lose mid solves** vs length — matches EXP-15 “easy stratum: knots irrelevant” and the advisor’s AC-19 probe direction.
- `s24` is closest to length on mid (few failures, often faster nodes).
- Hard-band recoveries are the only place a structural arm can prove value at budget 1000; see table above.
- **Do not fit new weights on this pool without a pre-registered speed or hard-recovery objective** — solve-rate on mid is contaminated by the screen.

## Also

- Feature census: [`FEATURE_CENSUS.md`](FEATURE_CENSUS.md) (S barely differs mid vs hard on AC1M).
- Plan / advisor re-scope: [`PLAN.md`](PLAN.md).

