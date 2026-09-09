# ac19_extended_screen: the hybrid at 1,000 nodes over all 156,762 AC19 presentations

Branch `claude/ac19-leftover-solver-notebook-6yan6d`. Not merged to main.

Every presentation in `data/AC19_extended.txt` -- the raw dataset, not the
72,779 `Aut(F2)`-orbit representatives -- through
`experiments/search/cascade_heuristics.py` at a 1,000-node budget,
search cap 255, rewrite intermediate cap unbounded.

    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen run \
        --arm cascade501 --budget 1000 --rows-csv <dataset csv> \
        --out-dir results/heuristic_search/ac19_extended_screen --workers 3

## Result

| outcome | rows | share |
|---|---:|---:|
| **solved** (reached a terminal pair) | **153,554** | **97.95%** |
| ... AC-certified as recorded | 29,371 | 18.74% |
| ... AC-solved, certificate still needs decoding | 124,183 | 79.22% |
| unsolved at 1,000 nodes | 3,208 | 2.05% |
| certificates that failed replay | 0 | -- |

By which component won: `s40_gen` 113,754, `rewrite` 39,017, `s20_mk2` 783.

Charged nodes on the solved rows: total 5,589,544, mean 36.40, median 16,
max 1,000. Cost: **32.3 minutes wall on 3 workers, 1.61 core-hours,
0.037 s per presentation**, 0.18 GB peak RSS per worker.

## The two solved lines are one number, not two

A path that changes basis is still an AC solve. AC moves are equivariant
under `Aut(F2)`, so pushing the accumulated basis change back through the
path collapses every automorphism step and leaves a pure AC path to some
basis of `F2`; Nielsen's theorem then carries that basis to `(x, y)` by
tuple moves that are themselves AC moves. Measured on MS640, the basis
tail costs about **2 AC moves** on average.

So 97.95% is the honest solve rate. The split is a statement about the
certificate FORMAT, not about which rows are settled: nothing in the repo
performs the push-back yet, so those 124,183 rows are recorded rather
than certified. Building that decoder is the open task.

## Charging, and what it is not comparable to

`nodes_explored` here is the cascade's own charge: accepted basis
changes, rewrite steps plus the root, and fallback pops including
abandoned attempts. A greedy `nodes_explored` counts heap pops. The two
are different units and must not be put in one column without saying so.

## Files

| file | rows |
|---|---:|
| `unsolved_cascade501_b1000.csv` | 3,208 |
| `aut_assisted_cascade501_b1000.csv` | 124,183 |
| `ac19_cascade_screen_cascade501_b1000_mrl255.jsonl` | 156,762 (122 MB, git-ignored) |

## Relation to the orbit screen

`results/heuristic_search/ac19_cascade_screen/` runs the same search over
the 72,779 `Aut(F2)`-orbit representatives instead. The dataset here has
156,762 rows because Aut-duplicates are not removed; a presentation and
its automorphic images all appear. Solve rates are not comparable between
the two -- the orbit list is one row per class, this is every member.
