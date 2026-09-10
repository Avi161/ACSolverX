# AC19 Aut-minimal census, 1,000 charged units, policy `K3p_notable` (no table)

The no-table control for `K3p_c14aut`: the same cascade with `table=None`, so
every charged unit is forward search and nothing is looked up. 72,562 / 72,779
solved and verified; 217 unsolved; 0 errors; 5,871,522 charged units.

| policy | table | solved | units | max | rows at 0 units |
|---|---|---|---|---|---|
| `frozen` (`final_policy`, 98f719e2) | none | 72,052 | 6,621,411 | 1,000 | 0 |
| `K3p_notable` (this bundle) | none | **72,562** | 5,871,522 | 1,000 | 0 |
| `K3p_c14aut` (`ac19_ball14_cascade_full_1k`) | cap-14 ball | **72,779** | 949,521 | 699 | 66,151 |

- Against `frozen`: 567 gained, 57 lost (net +510). On the 71,995 rows both
  solve: 26,435 cheaper, 45,219 equal, 341 dearer.
- The cap-14 table accounts for exactly the remaining **217** rows (every row
  `K3p_c14aut` solves that this run does not), and for the drop from 5.87M to
  0.95M units — 66,151 roots (91%) lie inside the ball and cost 0 under the
  tabled policy.
- Routes: plain_s20 41,644, strict_donor 28,036, incumbent_restart 2,672,
  bs_demote 427.
- Input `data/AC19_extended_aut_min.csv`, SHA-256 `7e220253…4ae2`. Code:
  commit `a717f043` plus the `K3p_notable` registration (`policies.py`,
  `make_notable_policy`).
- Clocks (4 workers, this container): search wall 840 s, certificate decode +
  replay 213 s, census wall 279 s.
- `replay_check.json`: 72,562 / 72,562 certificates re-decoded and replayed to
  (x, y) in fresh processes, 0 failures. `verify_bundle` PASS.

Reproduce and check:

```bash
PYTHONPATH=. python3 -m research.residual_20260909.census_run \
    --input data/AC19_extended_aut_min.csv --policy K3p_notable --budget 1000 \
    --out results/heuristic_search/ac19_K3p_notable_full_1k --shard-size 1000 --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.census_summarize \
    --input data/AC19_extended_aut_min.csv \
    --result-dir results/heuristic_search/ac19_K3p_notable_full_1k \
    --baseline results/heuristic_search/ac19_final_policy_full_1k
PYTHONPATH=. python3 -m research.residual_20260909.replay_census \
    --result-dir results/heuristic_search/ac19_K3p_notable_full_1k --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.verify_bundle \
    --result-dir results/heuristic_search/ac19_K3p_notable_full_1k
```
