# Campaign 12h RESULTS — anti-overfit heuristic evaluation

Updated: `2026-07-29T02:44:59.763806+00:00`

## Advisor gate

`ac-advisor` **BLOCK**ed fitting on the ~1100 automorphic/CoV pool (1043 unsolved-descended; EXP-27/10 already ties; no dynamic range on unsolved @1000).
This campaign follows the **approved evaluation-only** re-scope on never-read AC1M (MS pairs excluded), budget **1000**, cap **48**.

## Screen (length-only denominator)

- Screened: **13971**
- Easy (<100 nodes): 8944
- Mid (100–999): 2617
- Hard (unsolved @1000): 2410
- Solve rate: 11561/13971 (82.7%)

## Go / no-go

**GO for evaluation.** AC1M has real mid/hard mass. Mid solve-rate cannot separate arms (length solves mid by construction). Read **hard recoveries** and **mid speed**.

## Hard-band recoveries (490 complete idxs)

| arm | recovered | rate |
|---|---:|---:|
| `length` | **0/490** | 0.0% |
| `recommended` | **93/490** | 19.0% |
| `mk8` | **70/490** | 14.3% |
| `k8` | **39/490** | 8.0% |
| `kms5` | **84/490** | 17.1% |
| `s24` | **174/490** | 35.5% |

- Any non-length recovery: **215/490** (43.9%)
- `s24` ∩ `recommended`: 59
- `s24` not recovered by recommended: 115

## Mid-band speed (1065 complete idxs)

| arm | still solved | mean nodes | med nodes | faster than length | slower/fail |
|---|---:|---:|---:|---:|---:|
| `length` | 1065/1065 | 170.1 | 146 | 0 | 0 |
| `recommended` | 1041/1065 | 255.8 | 184 | 393 | 670 |
| `mk8` | 992/1065 | 324.4 | 237 | 281 | 784 |
| `k8` | 602/1065 | 150.8 | 94 | 419 | 645 |
| `kms5` | 1047/1065 | 203.4 | 145 | 470 | 588 |
| `s24` | 1058/1065 | 131.3 | 96 | 816 | 242 |

## Verdict

1. **Best pre-registered arm on never-read AC1M hard band: `L + 24·S`** — largest recovery rate and often faster on mid.
2. **Full RECOMMENDED helps hard somewhat but is slower / loses mid solves** vs length — not a free upgrade off the Miller–Schupp distribution.
3. **Knot-heavy one-features (`k8`, `mk8`) transfer poorly** here (many mid failures; weaker hard recoveries).
4. **No new weights were fit.** These are frozen arms from prior subset-60 / shipped configs, scored once on a held-out-style never-read pool.
5. Unsolved ACA presentations were **not** used for selection (none occurred).

## Files

- [`PLAN.md`](PLAN.md) — advisor re-scope
- [`FEATURE_CENSUS.md`](FEATURE_CENSUS.md)
- `screen_length_ac1m.jsonl`, `arms_on_band.jsonl`, `arms_hard_full.jsonl`

