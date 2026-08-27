# New moves on subset-60 at tiny budgets

One 1,000-node run per arm per presentation (`solved_at` gives every smaller budget); cap 24, cyclic reduction on. Solve counts include ONLY independently verified paths (`certify.verify_solution` for macro arms, `moves_to_states` replay for plain arms); unverified solves are listed separately and count as failures.

| arm | moves | ordering | @100 | @250 | @500 | @1000 | median nodes | median path | donor-edge solves | wall s | nodes/s |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| greedy | sub | L | 17 | 20 | 26 | 29 | 61 | 16 | - | 40.2 | 899 |
| s20_mk2 | sub | s20_mk2 | 21 | 28 | 35 | 37 | 52 | 22 | - | 56.1 | 511 |
| macro_L | sub+donor | L | 17 | 20 | 26 | 29 | 61 | 16 | 0 | 114.3 | 316 |
| macro_s20_mk2 | sub+donor | s20_mk2 | 21 | 28 | 35 | 37 | 52 | 22 | 0 | 77.2 | 371 |

Total wall time for the whole grid: 97 s. Node budgets are pop counts; the macro arms pay more wall time per pop (see nodes/s), so read the table twice — once at equal nodes, once at equal time via the nodes/s column.

Regenerate: `python -m experiments.search.bench_new_moves --budget 1000`.
