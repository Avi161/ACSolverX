# Per-row results on MS640 and ladder100, every method

One record per presentation of MS640 (640 rows; the 60 of bench60 are marked) and ladder100
(`benchmark/ladder/ladder_default.csv`, 100 rows), with the result of each of the seven methods of the paper, so the
per-row numbers never have to be gathered or rerun again. Built by `benchmark/relen/build_rows.py` (on branch
`paper`, where the Elliot and CoV-gate result folders live); every stored path is replayed and checked against its
record by `benchmark/relen/verify_rows.py` (5,151 paths, 0 mismatches), which runs on main.

Every LENGTH and S20_MK2 rerun reproduces the recorded pop count of its row, and the units and path lengths agree with
the paper's Section 1 table (LENGTH ladder100: 975,165 / 101,770.5 / 8,204,360 units, paths 130.8 / 69 / 706). The
per-row rerun records, with their S-move paths, are in `results/relen/`.

## Files

| file | holds |
|---|---|
| `ms640.jsonl`, `ladder100.jsonl` | per row: `id`, `pres`, `start_max_rel`, `bench60` (MS640) or `level` (ladder100), and `methods` |
| `paths/ms640.jsonl.gz`, `paths/ladder100.jsonl.gz` | per row: the solution path of every method that solved it |
| `SUMMARY.md` | mean / median / max over the solved rows, per benchmark and method |

The hybrid entry also holds `max_rel_search`: the longest relator over the hybrid's own search states (the
presentations after each S-move or Nielsen map), before its certificate is rewritten as AC moves.

Each `methods` entry: `solved`, `units`, `path_length`, `max_rel` (the longest relator on the solution path).

## Methods, units and sources

| method | units | path length | source |
|---|---|---|---|
| LENGTH | pops | S-moves | MS640: rerun at budget 10^6, cap 24. ladder100: rerun at each row's recorded cap with budget = its recorded pops (`greedy_nodes`; every rerun reproduces the count exactly); the 17 rows above 1.5 million pops from the paths stored by the 5M and 10M runs (branch `claude/ac19-leftover-solver-notebook-6yan6d`, node counts equal to `greedy_nodes`) |
| S20_MK2 | pops | S-moves | MS640: rerun at budget 10^5, cap 24. ladder100: as LENGTH, with `s20_nodes` (caps 48, 64, 24 tried until the count matches); the 4 hardest rows from the stored 5M run |
| hybrid | S-moves and Nielsen maps | S-moves and Nielsen maps | `configs/hybrid.toml` at budget 10^3 (this repo's hybrid; the paper's Section 1 hybrid numbers came from an earlier version) |
| CoV gate | pops plus gate openings | S-moves and CoV moves | `results/ryan_cov_full_1e5` and `_1e6` (branch `paper`) |
| dual, single CoV / dual, auto CoV / triple | pops of any queue | S-moves and CoV moves | `results/elliot_fullcov` (branch `paper`) |

**Longest relator.** LENGTH, S20_MK2: the S-move path replayed on the cyclically reduced start (`acx.verify.replay`).
Hybrid: the certificate rewritten as elementary AC moves on the original presentation, each relator cyclically
reduced. CoV searches: the states on the path (the CoV images, not the intermediate states with three generators).

## Path formats (`paths/*.jsonl.gz`)

| `format` | fields | replay |
|---|---|---|
| `smoves` | `path`: S-moves `[i, j, s, k1, k2]` (`acx.core.moves.Move`), `cap` | `replay(pres, [Move(*m) for m in path], cyclic=True, cap=cap)` |
| `states` | `path`: every state `[r1, r2]` from start to the trivial presentation, `cap`, `source` | consecutive states differ by one S-move |
| `hybrid` | `certificate`: Nielsen maps `{"aut": k}` and S-moves; `elementary`: packed AC moves (`acx.verify.pack`) | `replay(pres, unpack(elementary), cyclic=False, normalize=False)` |
| `cov_gate` | `path`: states with the S-move or CoV step that reached each; `kind` (`ac_path` or `stable_cert`) | `benchmark/ryan/verify_full.py` (branch `paper`) |
| `elliot` | `path`: states; `cov_used`: each CoV step; `moves`; `kind` | `benchmark/elliot/fullcov` (branch `paper`) |
