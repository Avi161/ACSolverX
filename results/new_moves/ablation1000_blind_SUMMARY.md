# New moves on subset-60 at tiny budgets

One 1,000-node run per arm per presentation (`solved_at` gives every smaller budget); cap 24, cyclic reduction on. Solve counts include ONLY independently verified paths (`certify.verify_solution` for macro arms, `moves_to_states` replay for plain arms); unverified solves are listed separately and count as failures.

| arm | moves | ordering | @100 | @250 | @500 | @1000 | median nodes | median path | donor-edge solves | wall s | nodes/s |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| greedy | sub | L | 17 | 20 | 26 | 29 | 61 | 16 | - | 65.2 | 554 |
| s20_mk2 | sub | s20_mk2 | 21 | 28 | 35 | 37 | 52 | 22 | - | 80.7 | 355 |
| recommended | sub | RECOMMENDED | 20 | 31 | 37 | 43 | 106 | 25 | - | 74.7 | 351 |
| macro_L | sub+donor | L | 17 | 20 | 26 | 29 | 61 | 16 | 0 | 369.5 | 98 |
| macro_s20_mk2 | sub+donor | s20_mk2 | 21 | 28 | 35 | 37 | 52 | 22 | 0 | 298.5 | 96 |
| macro_recommended | sub+donor | RECOMMENDED | 20 | 31 | 37 | 43 | 106 | 25 | 0 | 261.1 | 100 |

Total wall time for the whole grid: 385 s. Node budgets are pop counts; the macro arms pay more wall time per pop (see nodes/s), so read the table twice — once at equal nodes, once at equal time via the nodes/s column.

Regenerate: `python -m experiments.search.bench_new_moves --goal-smax 0 --subw 3 4`.
