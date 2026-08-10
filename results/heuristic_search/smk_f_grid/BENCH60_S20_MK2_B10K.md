# bench60 @ budget 10,000 — `s20_mk2` vs greedy

**No new search.** `s20_mk2` rescored from existing `hsearch_bench60_1m` runs (budget 1M, mrl 48): a search at B is the first B pops.
Greedy column = frozen `m10k_greedy_*` in `benchmark/subsets/benchmark_subset_60_arms.json` (no re-run).

## Headline

| arm | solved @10k |
|---|---:|
| greedy (length) | **40/60** |
| `s20_mk2` (L+20S+2MK) | **52/60** |
| Δ | **+12** |

McNemar: s20-only=12, greedy-only=0, both=40.

## Per-bin

| bin | greedy | s20_mk2 | Δ |
|---:|---:|---:|---:|
| 0 | 6/6 | 6/6 | +0 |
| 1 | 6/6 | 6/6 | +0 |
| 2 | 6/6 | 6/6 | +0 |
| 3 | 6/6 | 6/6 | +0 |
| 4 | 6/6 | 6/6 | +0 |
| 5 | 6/6 | 6/6 | +0 |
| 6 | 4/6 | 6/6 | +2 |
| 7 | 0/6 | 6/6 | +6 |
| 8 | 0/6 | 2/6 | +2 |
| 9 | 0/6 | 2/6 | +2 |

## Cost (joint solved @10k, n=40)

| arm | median nodes | mean nodes |
|---|---:|---:|
| greedy | 197 | 1205.7 |
| s20_mk2 | 86 | 280.1 |

## Cap note

- `s20_mk2` 1M Colab used **mrl=48**.
- Frozen greedy `m10k_*` is the length-greedy @10k column in the arms freeze (historically often mrl 24 on this ladder — treat Δ solves as primary; node ratios are indicative).

Row table: `bench60_s20_mk2_b10k_vs_greedy.csv`.

