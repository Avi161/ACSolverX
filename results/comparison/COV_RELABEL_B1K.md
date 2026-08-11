# Relabel-dedup, and `MK` at the last slot — both arms, budget 1,000 and 10,000

**Zero search nodes.** A re-ranking of the frozen `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` and its 10,000-node twin through `abel_topk_cov_b1k`'s gated loader, subset-60, top 3. The sweep searched every candidate of every row, so unlike the ms640 top-3 census a promoted candidate costs nothing to score — this is the only place the dedup can be priced rather than merely counted.

## Budget 1,000

| arm | k=1 | k=3 | median nodes | mean nodes | deployed | wasted slots |
|---|---:|---:|---:|---:|---:|---:|
| `(abel)` | 38 | 41 | 18 | 165.6 | 63,790 | 72 |
| `(abel)` + relabel-dedup | 38 | 41 | 18 | 165.6 | 63,790 | 0 |
| `(abel)` + relabel-dedup + MK | 40 | 41 | 18 | 110.7 | 61,540 | 0 |
| `(abel, total)` | 40 | 41 | 18 | 112.9 | 61,627 | 83 |
| `(abel, total)` + relabel-dedup | 40 | 41 | 18 | 112.9 | 61,627 | 0 |
| `(abel, total)` + relabel-dedup + MK | 40 | 41 | 18 | 112.8 | 61,625 | 0 |
| `(total)` | 37 | 39 | 60 | 244.8 | 72,549 | 49 |
| `(total)` + relabel-dedup | 37 | 39 | 60 | 244.8 | 72,549 | 0 |
| `(total)` + relabel-dedup + MK | 37 | 39 | 60 | 270.5 | 73,549 | 0 |

## Budget 10,000

| arm | k=1 | k=3 | median nodes | mean nodes | deployed | wasted slots |
|---|---:|---:|---:|---:|---:|---:|
| `(abel)` | 52 | 52 | 35 | 1,103.3 | 297,372 | 72 |
| `(abel)` + relabel-dedup | 52 | 52 | 35 | 1,103.3 | 297,372 | 0 |
| `(abel)` + relabel-dedup + MK | 50 | 52 | 32 | 1,650.6 | 325,829 | 0 |
| `(abel, total)` | 51 | 52 | 32 | 1,231.3 | 304,030 | 83 |
| `(abel, total)` + relabel-dedup | 51 | 52 | 32 | 1,231.3 | 304,030 | 0 |
| `(abel, total)` + relabel-dedup + MK | 52 | 52 | 32 | 1,039.0 | 294,028 | 0 |
| `(total)` | 47 | 49 | 270 | 1,797.8 | 418,090 | 49 |
| `(total)` + relabel-dedup | 47 | 50 | 271 | 2,319.3 | 415,965 | 0 |
| `(total)` + relabel-dedup + MK | 47 | 50 | 271 | 2,319.3 | 415,965 | 0 |

## Paired, on the rows both arms solve

| base key | comparison | budget | win / tie / loss |
|---|---|---:|---|
| `(abel)` | dedup vs shipped | 1,000 | 0 / 41 / 0 |
| `(abel)` | dedup vs shipped | 10,000 | 0 / 52 / 0 |
| `(abel)` | MK vs name, after dedup | 1,000 | 7 / 34 / 0 |
| `(abel)` | MK vs name, after dedup | 10,000 | 8 / 39 / 5 |
| `(abel)` | both vs shipped | 1,000 | 7 / 34 / 0 |
| `(abel)` | both vs shipped | 10,000 | 8 / 39 / 5 |
| `(abel, total)` | dedup vs shipped | 1,000 | 0 / 41 / 0 |
| `(abel, total)` | dedup vs shipped | 10,000 | 0 / 52 / 0 |
| `(abel, total)` | MK vs name, after dedup | 1,000 | 1 / 40 / 0 |
| `(abel, total)` | MK vs name, after dedup | 10,000 | 2 / 50 / 0 |
| `(abel, total)` | both vs shipped | 1,000 | 1 / 40 / 0 |
| `(abel, total)` | both vs shipped | 10,000 | 2 / 50 / 0 |
| `(total)` | dedup vs shipped | 1,000 | 0 / 39 / 0 |
| `(total)` | dedup vs shipped | 10,000 | 0 / 49 / 0 |
| `(total)` | MK vs name, after dedup | 1,000 | 0 / 38 / 1 |
| `(total)` | MK vs name, after dedup | 10,000 | 0 / 50 / 0 |
| `(total)` | both vs shipped | 1,000 | 0 / 38 / 1 |
| `(total)` | both vs shipped | 10,000 | 0 / 49 / 0 |

Reference points at budget 1,000: best-CoV **oracle 45/60**, plain greedy on the untransformed pair **29/60**. The solve column saturates against that oracle, so read the cost columns.

![arms](cov_relabel_b1k.png)

