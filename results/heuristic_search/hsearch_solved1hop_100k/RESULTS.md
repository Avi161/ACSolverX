# solved_1hop_autclean @ 100k — results

Tip `9279591` Colab chunks, reorganized from misnamed `hsearch_solved1hop_1m/`
(actual budget **100,000**, not 1M). No zips in the push — already jsonl.

| | |
|---|---|
| dataset | `solved_1hop_autclean` (432 Aut-orbits) |
| budget / cap | **100,000** / 48 |
| arms | baseline, s12, s28, s20_mk2, s24_k1_mk2 |
| rows | **2160** = 432 × 5 (all complete) |
| certificates | **2020/2020** solved paths replay (pure-Python spec) |
| selected_on | AC1M-hard tune + campaign S-grid/arms + scale10k |
| evaluated_on | solved_1hop_autclean |

Layout:
```
results/heuristic_search/hsearch_solved1hop_100k/
  chunks/c{1..5}of5_…_b100000_mrl48.{jsonl,md}
  merged_solved_1hop_autclean_b100000_mrl48.jsonl
  RESULTS.md  SHIP.md  residual_unsolved_100k.json
```

## Anytime solve counts (complete rows)

| arm | 1,000 | 5,000 | 10,000 | 25,000 | 50,000 | 100,000 |
|---|---|---|---|---|---|---|
| baseline | 304/432 | 345/432 | 363/432 | 381/432 | 385/432 | 389/432 |
| s12 | 331/432 | 371/432 | 381/432 | 389/432 | 395/432 | 399/432 |
| s28 | 329/432 | 361/432 | 373/432 | 380/432 | 396/432 | 401/432 |
| s20_mk2 | 334/432 | 375/432 | 392/432 | 403/432 | 412/432 | 416/432 |
| s24_k1_mk2 | 333/432 | 373/432 | 385/432 | 399/432 | 411/432 | 415/432 |

## Δ vs length baseline

| arm | 1,000 | 5,000 | 10,000 | 25,000 | 50,000 | 100,000 |
|---|---|---|---|---|---|---|
| s12 | +27 | +26 | +18 | +8 | +10 | +10 |
| s28 | +25 | +16 | +10 | -1 | +11 | +12 |
| s20_mk2 | +30 | +30 | +29 | +22 | +27 | +27 |
| s24_k1_mk2 | +29 | +28 | +22 | +18 | +26 | +26 |

Gap verdict suppressed in spirit of the saturation trap: several arms are near-ceiling;
read the table row-level / stratified below.

## Stratified at 100k

| stratum | n | baseline | s12 | s28 | s20_mk2 | s24_k1_mk2 |
|---|---:|---:|---:|---:|---:|---:|
| all | 432 | 389/432 | 399/432 | 401/432 | 416/432 | 415/432 |
| seed | 58 | 58/58 | 58/58 | 58/58 | 58/58 | 58/58 |
| moved_cov | 374 | 331/374 | 341/374 | 343/374 | 358/374 | 357/374 |
| short_relator | 38 | 38/38 | 38/38 | 38/38 | 38/38 | 38/38 |
| non-short moved_cov | 339 | 296/339 | 306/339 | 308/339 | 323/339 | 322/339 |

## Node efficiency vs baseline (both solved)

| arm | geo-mean nodes ratio | n paired | med solved_at |
|---|---:|---:|---:|
| baseline | — | — | 54 |
| s12 | 0.645 | 389 | 38 |
| s28 | 0.780 | 388 | 53 |
| s20_mk2 | 0.674 | 389 | 62 |
| s24_k1_mk2 | 0.706 | 389 | 59 |

## Difficulty bins (benchmark log-edges, length-baseline @100k)

Same `[lo, hi)` node edges as `benchmark/difficulty_bins.csv` (ms640 greedy @1M). Ruler here = this run's **length baseline** `solved_at` (unsolved censored at 100k → bin 8).

| bin | nodes range | n | baseline | s12 | s28 | s20_mk2 | s24_k1_mk2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | [3, 10) | 100 | 100/100 | 100/100 | 100/100 | 100/100 | 100/100 |
| 1 | [10, 34) | 72 | 72/72 | 72/72 | 72/72 | 72/72 | 72/72 |
| 2 | [34, 115) | 56 | 56/56 | 56/56 | 56/56 | 56/56 | 56/56 |
| 3 | [115, 389) | 48 | 48/48 | 48/48 | 48/48 | 48/48 | 48/48 |
| 4 | [389, 1313) | 38 | 38/38 | 38/38 | 38/38 | 38/38 | 38/38 |
| 5 | [1313, 4432) | 26 | 26/26 | 26/26 | 26/26 | 26/26 | 26/26 |
| 6 | [4432, 14958) | 33 | 33/33 | 33/33 | 32/33 | 33/33 | 33/33 |
| 7 | [14958, 50482) | 12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| 8 | [50482, 170367) | 47 | 4/47 | 14/47 | 17/47 | 31/47 | 30/47 |
| 9 | [170367, 574959] | 0 | — | — | — | — | — |

Baseline-censored (unsolved @100k): **43** presentations (placed in bin by nodes=100000).

### Figures

- `solved1hop_100k_mean_median.png`
- `solved1hop_100k_nodes_explored.png`
- `solved1hop_100k_path_length.png`
- `solved1hop_100k_difficulty_bins.png`

Per-row table: `difficulty_bins_solved1hop_100k.csv`.
