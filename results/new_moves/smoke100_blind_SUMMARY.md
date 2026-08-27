# New moves on subset-60 at tiny budgets

One 100-node run per arm per presentation (`solved_at` gives every smaller budget); cap 24, cyclic reduction on. Solve counts include ONLY independently verified paths (`certify.verify_solution` for macro arms, `moves_to_states` replay for plain arms); unverified solves are listed separately and count as failures.

| arm | moves | ordering | @100 | median nodes | median path | donor-edge solves | wall s | nodes/s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| greedy | sub | L | 17 | 13 | 9 | - | 18.0 | 266 |
| s20_mk2 | sub | s20_mk2 | 21 | 16 | 11 | - | 14.1 | 318 |
| recommended | sub | RECOMMENDED | 20 | 13.5 | 11.5 | - | 14.7 | 321 |
| macro_L | sub+donor | L | 17 | 13 | 9 | 0 | 46.2 | 103 |
| macro_s20_mk2 | sub+donor | s20_mk2 | 21 | 16 | 11 | 0 | 41.0 | 110 |
| macro_recommended | sub+donor | RECOMMENDED | 20 | 13.5 | 11.5 | 0 | 44.4 | 106 |

Total wall time for the whole grid: 47 s. Node budgets are pop counts; the macro arms pay more wall time per pop (see nodes/s), so read the table twice — once at equal nodes, once at equal time via the nodes/s column.

Regenerate: `python -m experiments.search.bench_new_moves --budget 100 --goal-smax 0 --subw 3 4` (pre-dates the goal proposer; at the time this family was the default).
