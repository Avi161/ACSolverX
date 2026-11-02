# ACSolverES Dual / Triple GS at 10,000 nodes

Elliot Steffen's greedy searches ([ElliotSteffen/ACSolverES](https://github.com/ElliotSteffen/ACSolverES), commit
`2a458e4`), run with their compact C++ engines on MS640, bench60 and ladder100 (`benchmark/ladder/ladder_default.csv`,
the paper's ladder100). Runner: `benchmark/elliot/run_elliot.py`; table: `benchmark/elliot/summarize.py`.

```bash
python benchmark/elliot/run_elliot.py --budget 10000 --out results/elliot_10k --workers 4
python benchmark/elliot/summarize.py results/elliot_10k --md results/elliot_10k/SUMMARY_TABLE.md
```

## Methods

| name here | ACSolverES name | queues | certificate |
|---|---|---|---|
| Dual (sub + single CoV) | `single_auto_cov_dual` | S-moves; single CoV (z := prefix w of a relator rotation, eliminate the generator left once) | `ac_path` via Aut(F2): every single CoV is an automorphism of F2 |
| Dual (sub + auto CoV) | `auto_dual` | S-moves; the 24 maps x -> xy^k, y -> yx^k, 1 <= abs(k) <= 6 | `ac_path` via Aut(F2) |
| Triple (sub + auto + complete CoV) | `auto_nonauto_cov_triple` | S-moves; the 24 maps; complete CoV (k >= 2 copies of w replaced by z) | `stable_cert` when a complete CoV is on the path (it is never an automorphism), else `ac_path` |

Parameters: those of ACSolverES `results/ms640_final_paper_v1/config.json` (thresholds 2, gap 0, seeding on, tie
`deepest`), except `max_len = 65` and `max_live_frontier_states = None`.

- `max_len` is a strict bound on the total length |r1|+|r2|. 65 is the largest value the compact engine stores (64
  letters a relator). The sub queue is ordered by length, so a longer state could be popped only after every shorter one;
  the peak total length on every solution path here is 25, and the bound did not change any popped state on the rows
  checked.
- No frontier pruning: `frontier_prune_count` is 0 on every row. ACSolverES's own config prunes at 5M live states,
  which drops the longest half of the queue.

## Units

A node is one pop from any queue (sub, auto, complete), as ACSolverES counts it. Not charged:

- the CoV children of the start state (seeding);
- the work of generating CoV candidates;
- triple pops of the complete queue that yield nothing new.

## Fields (`<bench>__<algo>.jsonl`)

| field | meaning |
|---|---|
| `nodes` | nodes used (the whole budget on a failure) |
| `path_length` | number of moves: `sub_moves` + `cov_moves`. Each CoV counts 1, so a map x -> xy^6 is one move. |
| `move_kinds` | moves of each type on the path |
| `max_relator_len`, `max_total_len` | longest relator, and longest total, on the solution path |
| `frontier_peak` | the largest number of states in the frontier at one time |
| `path`, `moves` | the solution |

## Checks

Both checks passed:

- Every MS640 row that ACSolverES's committed 10^6 run solves within 10,000 nodes has the same nodes, path length and
  path here (all three methods); every other MS640 row is unsolved here.
- bench60 rows equal their MS640 rows.

`VERIFY.json` has the independent replay of every solved path.
