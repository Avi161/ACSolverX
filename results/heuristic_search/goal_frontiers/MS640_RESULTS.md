# Certified cascade on all 640 solved Miller–Schupp presentations

The fixed cascade solves **640/640** at a budget of 1,000 charged units per
presentation. It uses 22,075 charged units in total, at most 404 on one row.
Search calls took 2.356716 seconds wall and 2.324334 seconds CPU. The complete
batch took 6.321895 seconds including certificate verification through two
decoders, serialization, progress output and twelve 0.25-second cooldowns.

The run was serial with one Numba/OpenMP/OpenBLAS thread. Compilation warm-up
was performed before timing. Every successful certificate was replayed by the
word-level verifier and the separate compiled substitution decoder.

| Metric | Saved greedy | Cascade |
|---|---:|---:|
| solved | 640/640 | 640/640 |
| budget per row | 1,000,000 | 1,000 |
| total nodes / charged units | 3,176,297 | 22,075 |
| mean | 4,962.96 | 34.49 |
| median | 11 | 13 |
| maximum | 574,959 | 404 |
| total path transitions | 23,533 | 13,686 |
| mean path | 36.77 | 21.38 |
| median path | 9 | 10 |
| maximum path | 708 | 260 |

The aggregate work reduction is 143.89-fold, and the aggregate recorded-path
reduction is 1.72-fold. The distribution matters: the cascade spends fewer
units on 291 rows, ties on 6 and spends more on 343. Its paths are shorter on
242 rows, equal on 186 and longer on 212. Greedy is already extremely cheap
on most of MS-640; the cascade's aggregate advantage comes from eliminating
the expensive tail rather than improving the median row.

The cascade produces 12,214 substitution transitions and 1,472 basis-change
transitions. The structural rewrite solves 254 rows and the `L+40S` search with
generator moves solves 386. No row reaches the S20_MK2 fallback. Twenty-eight
certificates exceed relator length 48; the largest observed canonical relator
is 131 under the explicit rewrite cap 256.

The saved greedy run used cap 24 and contains uncensored results for every row.
Its historical `time_seconds` totals 2,554.674 seconds (42 minutes 34.674
seconds), with median 0.00455 seconds and maximum 375.2362 seconds. That timing
came from an older campaign whose hardware/environment metadata is absent, so
it is not a same-machine speed ratio. No greedy search was rerun here.

The new measured search time is:

- total wall: 2.356716 seconds;
- total CPU: 2.324334 seconds;
- mean wall per row: 0.003682 seconds;
- median wall per row: 0.000700 seconds;
- maximum wall for one row: 0.072191 seconds.

`nodes_explored` is not exactly the same unit between methods. Greedy counts
heap pops, including the root and terminal. Cascade charges accepted basis
transforms, each rewrite root and elementary rewrite, and every fallback heap
pop, including failed branches and restarts. Alternative basis-image
evaluations are timed but counted separately. Likewise, greedy paths contain
substitution transitions, while cascade paths mix substitutions and basis
transforms. The comparison is therefore a measured cost comparison between
the complete methods, not an equal-cap priority-function ablation.

The input is the current `data/ms640_solved.txt`, byte-identical to the copy at
commit `525050dd9ed9b9e1ee06cde2d739ad05940c8172`. Saved greedy results come from
`results/greedy_baseline/greedy_1000000_640_mrl24_cyc_all_07_11_26.jsonl` at
that commit. All IDs, decoded relators and settings were checked before search.

Machine-readable artifacts are in `ms640_1k/`: `manifest.json`, `summary.json`
and the complete certificate-bearing `runs.jsonl`. The fixed runner is
`experiments/search/run_cascade_ms640.py`.
