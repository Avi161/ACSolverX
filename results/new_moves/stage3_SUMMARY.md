# New moves on subset-60 at tiny budgets — stage 2

One 10,000-node run per arm per presentation (`solved_at` gives every smaller budget); cap 24, cyclic reduction on. Solve counts include ONLY independently verified paths (`certify.verify_solution` for certificate arms, `moves_to_states` replay for plain arms — for cov arms the verified object is the Whitehead image's path; the portal supplies the rest of the claim); unverified solves are listed separately and count as failures. The `claim` column is load-bearing: an `AC_TRIVIAL_IFF` solve proves the original presentation AC-trivial without materialising a path for it, and must never be pooled with `AC_EQ path` counts as if it were one.

| arm | moves | ordering | claim | @100 | @250 | @500 | @1000 | @2500 | @5000 | @10000 | median nodes | median path | macro-edge solves | wall s | nodes/s |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| greedy | sub | L | AC_EQ path | 17 | 20 | 26 | 29 | 36 | 36 | 40 | 197.0 | 24.0 | - | 230.1 | 1,079 |
| ncrw_L | sub+goal+ncrw | L | AC_EQ path | 17 | 20 | 26 | 29 | 36 | 36 | 40 | 196.0 | 23.0 | 39 | 596.3 | 416 |
| cov_L | Whitehead reduce, then sub | L | AC_TRIVIAL_IFF portal | 20 | 24 | 32 | 36 | 39 | 42 | 49 | 273 | 25 | - | 302.4 | 609 |
| covncrw_L | Whitehead reduce, then sub+goal+ncrw | L | AC_TRIVIAL_IFF portal | 20 | 24 | 32 | 36 | 39 | 42 | 49 | 272 | 24 | - | 464.8 | 396 |

Total wall time for the whole grid: 1594 s. Node budgets are pop counts; the macro arms pay more wall time per pop (see nodes/s), so read the table twice — once at equal nodes, once at equal time via the nodes/s column.

Regenerate: `python -m experiments.search.bench_new_moves --budget 10000 --stage3 (two rows re-run solo after worker OOM; see stage3 notes in NEW_MOVES.md)`.
