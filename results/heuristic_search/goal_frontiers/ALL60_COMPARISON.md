# Hybrid versus saved greedy: all 60 solved presentations

This comparison uses all 60 uncensored greedy solutions from
`benchmark/subsets/benchmark_subset_60.json` (`nodes_1M`, `path_1M`) and all 60
hybrid certificates in `matched_10k/runs.jsonl`. No new searches were run.
The hybrid's paths and charged counts also match its saved 1k run exactly.

The greedy records have a 1,000,000-node ceiling and relator cap 24, documented
in `benchmark/subsets/ARMS.md`. The hybrid uses ordinary search cap 48 and
rewrite cap 256; its largest observed canonical relator is 131. These are
recorded costs under different move sets/caps, not a controlled estimate of
the effect of changing only the priority function.

| Metric, all 60 | Saved greedy | Hybrid |
|---|---:|---:|
| Solved | 60/60 | 60/60 |
| Explored/charged nodes: total | 2,714,651.00 | 6,286.00 |
| Explored/charged nodes: mean | 45,244.18 | 104.77 |
| Explored/charged nodes: median | 1,310.50 | 57.00 |
| Explored/charged nodes: maximum | 574,959.00 | 404.00 |
| Certificate path length: total | 8,557.00 | 3,650.00 |
| Certificate path length: mean | 142.62 | 60.83 |
| Certificate path length: median | 46.50 | 25.00 |
| Certificate path length: maximum | 708.00 | 260.00 |

Hybrid node charges are lower on 51 rows, equal on 2, and higher on 7.
Hybrid certificate paths are shorter on 49 rows, equal on 5, and longer on 6.
The 7 higher-work cases are easy greedy inputs requiring only 3-12 pops.

## What the counters mean

- Greedy nodes count popped states, including the solution pop. Its path
  length counts stored substitution transitions, excluding the initial state.
- Hybrid nodes add accepted initial basis transforms, one rewrite root plus
  every explicit rewrite, and all fallback heap pops. Failed attempts and
  restarts remain charged. Alternative basis-image evaluations are recorded
  separately and timed; neither method's node count counts every generated
  child as a separate node.
- Hybrid path length is `len(steps) = len(states)-1` for the successful
  certificate only. Its 3,650 steps comprise 3,361 substitutions and 289
  basis transforms. Discarded branch work is absent from the final path but
  present in the charged node count.
- Both paths use the solver's cyclic/inverse/relator-order canonicalization
  convention. A basis transform is one stored transition. These counts are
  not lengths in a common expanded alphabet of elementary AC moves and
  neither solver claims a shortest path.

All 60 hybrid certificates carry both recorded replay-verification flags.
The 40 greedy solutions available in the fresh cap-48, 10k matched run agree
with the saved cap-24 greedy records in both node count and path length.
The other 20 are taken from the uncensored saved data, not extrapolated.
No matched all-60 greedy runtime was measured; node counts do not establish
an all-60 wall-time speedup. This remains an in-sample benchmark result.

## Procedure

1. Canonically reduce the input. Repeatedly choose the most length-decreasing
   of four Nielsen maps, and then choose the least signed generator
   permutation. This strict descent does not enumerate length-preserving
   automorphism plateaus; do not call it a full Aut-canonical representative.
2. Recognize a signed/rotated/inverted relator `b^-1 a b a^-2` with a companion
   of b-exponent sum ±1. Orient that companion to exponent sum -1.
3. Use the donor to perform explicit replacements `b^-1 s -> s s b^-1` and
   `b s s -> s b`, for `s = a` or `a^-1`. The deterministic cyclic scan prefers
   `b a^(2k) b^-1` pinches, then `b^-1 a^k b` pinches. Each elementary replacement
   is converted to an actual rotated donor substitution and verified.
4. If the companion reduces to `b^-1 a^q`, use it to eliminate b from
   `b^-1 a b a^-2`, leaving `a^-1`. Use this generator relator to erase the
   remaining a letters in the companion, leaving `b^-1`.
5. If this branch fails, restart the original input with `L+40S` and the four
   generator-change neighbors for at most 500 pops. Plain `S20_MK2` receives
   any remaining global budget. The rewrite allowance is at most 1,000;
   all components share one total budget. No benchmark ID or stored path
   is consulted by the solver. W is not used in this final hybrid.

The four maps applied to both relators are `x -> xy`, `x -> xY`,
`y -> yx`, and `y -> yX`, leaving the other generator fixed. The S40 phase
queues these alongside the ordinary substitution neighbors, orders by
`(L+40S, depth, canonical key)`, and suppresses previously seen states.

Here 21 inputs finish through rewriting and 39 through S40 with generator
moves; none reaches S20. The full algorithm and budget details are in
`CASCADE.md`, with code in `experiments/search/cascade_heuristics.py` and
`experiments/search/bs_collapse.py`.

## Every presentation

| ID | Greedy nodes | Hybrid charges | Greedy path | Hybrid path | Substitutions + basis transforms | Winner | Peak relator |
|---|---:|---:|---:|---:|---:|---|---:|
| ms0 | 3 | 4 | 2 | 3 | 2 + 1 | rewrite | 5 |
| ms496 | 4 | 7 | 3 | 3 | 2 + 1 | s40_gen | 15 |
| ms521 | 5 | 9 | 4 | 4 | 4 + 0 | s40_gen | 17 |
| ms323 | 7 | 13 | 6 | 6 | 6 + 0 | s40_gen | 9 |
| ms228 | 9 | 10 | 7 | 7 | 7 + 0 | s40_gen | 7 |
| ms455 | 10 | 11 | 9 | 8 | 8 + 0 | s40_gen | 11 |
| ms77 | 11 | 11 | 8 | 10 | 9 + 1 | rewrite | 8 |
| ms43 | 13 | 12 | 9 | 11 | 9 + 2 | rewrite | 7 |
| ms141 | 12 | 13 | 10 | 12 | 11 + 1 | rewrite | 9 |
| ms48 | 18 | 14 | 11 | 13 | 12 + 1 | rewrite | 9 |
| ms155 | 18 | 15 | 12 | 14 | 13 + 1 | rewrite | 11 |
| ms505 | 34 | 34 | 23 | 18 | 16 + 2 | s40_gen | 15 |
| ms247 | 46 | 15 | 9 | 8 | 7 + 1 | s40_gen | 8 |
| ms217 | 57 | 18 | 13 | 12 | 9 + 3 | s40_gen | 8 |
| ms201 | 61 | 21 | 15 | 12 | 9 + 3 | s40_gen | 8 |
| ms288 | 106 | 43 | 17 | 13 | 10 + 3 | s40_gen | 9 |
| ms367 | 83 | 38 | 21 | 15 | 11 + 4 | s40_gen | 11 |
| ms331 | 93 | 26 | 24 | 11 | 8 + 3 | s40_gen | 10 |
| ms203 | 116 | 45 | 16 | 12 | 9 + 3 | s40_gen | 9 |
| ms265 | 121 | 46 | 21 | 15 | 11 + 4 | s40_gen | 9 |
| ms579 | 366 | 22 | 26 | 16 | 12 + 4 | s40_gen | 13 |
| ms327 | 273 | 31 | 29 | 18 | 13 + 5 | s40_gen | 9 |
| ms333 | 313 | 19 | 35 | 18 | 16 + 2 | rewrite | 11 |
| ms380 | 381 | 36 | 39 | 21 | 15 + 6 | s40_gen | 11 |
| ms546 | 398 | 129 | 24 | 17 | 13 + 4 | s40_gen | 13 |
| ms548 | 661 | 83 | 28 | 27 | 20 + 7 | s40_gen | 11 |
| ms533 | 438 | 37 | 43 | 21 | 15 + 6 | s40_gen | 11 |
| ms589 | 558 | 47 | 46 | 21 | 15 + 6 | s40_gen | 13 |
| ms580 | 875 | 30 | 47 | 24 | 18 + 6 | s40_gen | 13 |
| ms609 | 1,217 | 79 | 56 | 27 | 20 + 7 | s40_gen | 15 |
| ms538 | 2,261 | 114 | 25 | 25 | 19 + 6 | s40_gen | 12 |
| ms606 | 2,023 | 30 | 39 | 20 | 14 + 6 | s40_gen | 15 |
| ms544 | 1,569 | 36 | 75 | 35 | 32 + 3 | rewrite | 19 |
| ms549 | 1,411 | 119 | 79 | 40 | 29 + 11 | s40_gen | 13 |
| ms543 | 1,813 | 104 | 81 | 38 | 28 + 10 | s40_gen | 13 |
| ms565 | 1,404 | 67 | 145 | 66 | 64 + 2 | rewrite | 35 |
| ms602 | 6,285 | 41 | 56 | 25 | 18 + 7 | s40_gen | 15 |
| ms632 | 6,425 | 83 | 56 | 34 | 26 + 8 | s40_gen | 17 |
| ms573 | 13,393 | 144 | 63 | 38 | 22 + 16 | s40_gen | 13 |
| ms586 | 9,162 | 382 | 153 | 71 | 53 + 18 | s40_gen | 17 |
| ms581 | 9,567 | 404 | 153 | 71 | 49 + 22 | s40_gen | 17 |
| ms575 | 14,383 | 68 | 156 | 67 | 64 + 3 | rewrite | 35 |
| ms568 | 15,814 | 225 | 48 | 35 | 25 + 10 | s40_gen | 13 |
| ms578 | 15,873 | 226 | 50 | 34 | 25 + 9 | s40_gen | 13 |
| ms583 | 16,111 | 228 | 52 | 33 | 24 + 9 | s40_gen | 13 |
| ms628 | 26,774 | 151 | 81 | 34 | 27 + 7 | s40_gen | 17 |
| ms633 | 26,838 | 151 | 83 | 34 | 27 + 7 | s40_gen | 17 |
| ms596 | 16,168 | 131 | 337 | 130 | 128 + 2 | rewrite | 67 |
| ms605 | 60,593 | 132 | 307 | 131 | 128 + 3 | rewrite | 67 |
| ms610 | 61,366 | 133 | 309 | 132 | 128 + 4 | rewrite | 67 |
| ms625 | 78,770 | 260 | 665 | 259 | 256 + 3 | rewrite | 131 |
| ms622 | 78,774 | 259 | 671 | 258 | 256 + 2 | rewrite | 131 |
| ms624 | 59,971 | 260 | 706 | 259 | 256 + 3 | rewrite | 131 |
| ms623 | 59,710 | 259 | 708 | 258 | 256 + 2 | rewrite | 131 |
| ms634 | 574,348 | 158 | 80 | 34 | 27 + 7 | s40_gen | 15 |
| ms635 | 574,959 | 161 | 80 | 34 | 26 + 8 | s40_gen | 15 |
| ms637 | 271,866 | 260 | 667 | 259 | 256 + 3 | rewrite | 131 |
| ms639 | 272,953 | 261 | 669 | 260 | 256 + 4 | rewrite | 131 |
| ms638 | 213,878 | 260 | 672 | 259 | 256 + 3 | rewrite | 131 |
| ms636 | 213,882 | 261 | 678 | 260 | 256 + 4 | rewrite | 131 |
