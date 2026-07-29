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

## Residual for 1M escalation

- **140** unsolved cells (presentation, arm)
- **44** presentations with any unsolved arm
- **15** unsolved by all five arms
- Listed in `residual_unsolved_100k.json` — escalate every cell, not a subsample.

## Notes

- Seed stratum: **58/58** for every arm at ≤100k.
- short_relator (38): free solves for every arm (aut_min reintroduces ≤2-letter relators).
- Discrimination is almost entirely in non-short `moved_cov`.
- Best reach at 100k: **s20_mk2 416/432**, then s24_k1_mk2 415; length baseline 389.
- A solve is about the `aut_min` representative searched, not the Aut orbit.
- Unsolved = unsolved within budget 100k, not a counterexample.
