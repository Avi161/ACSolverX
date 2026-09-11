# AC19 Aut-minimal census, 1,000 charged units, policy `K3p_c14aut`

72,779 / 72,779 solved and verified; 0 unsolved; 0 errors; 727 gained and 0 lost
against `results/heuristic_search/ac19_final_policy_full_1k` (72,052).

- Input: `data/AC19_extended_aut_min.csv`, SHA-256
  `7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`.
- Code: commit `4a4500af` of `research/residual_20260909` (source hashes in
  `manifest_00000_72779.json`); policy `K3p_c14aut` = `final_policy_ball.search`
  with the cap-14 automorphism-closed backward table
  (`tables/ball_cap14_aut.npz`, SHA-256 `c2bbbf3e...13f94`, rebuilt with
  `python -m research.residual_20260909.backward_table --cap 14 --aut-edges --compact`),
  250-unit certified-overrun donor stage, 300-unit plain S20 stage, incumbent
  restart, BS-DEMOTE.
- Files: 73 shards `rows_*.jsonl` (one record per input row, in input order,
  including the mixed path `states`/`steps` so any certificate can be re-decoded),
  `SUMMARY.json`, `RESULTS.md`, `COMPARISON.md` / `comparison.json` (against the
  published census), `unsolved.csv` (empty), `replay_check.json`,
  `census_run.log`, `summarize.log`.
- Charged units 949,521 (max 699, median 0); 66,151 roots resolve inside the
  table for 0 units; no row costs more than it did under the published policy.
- Clocks (4 workers, this container): search wall 46.7 s, certificate decode +
  replay wall 186.2 s, census wall 70 s.

Reproduce and check:

```bash
PYTHONPATH=. python3 -m research.residual_20260909.census_run \
    --input data/AC19_extended_aut_min.csv --policy K3p_c14aut --budget 1000 \
    --out results/heuristic_search/ac19_ball14_cascade_full_1k \
    --offset 0 --limit 72779 --shard-size 1000 --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.census_summarize \
    --input data/AC19_extended_aut_min.csv \
    --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k \
    --baseline results/heuristic_search/ac19_final_policy_full_1k
PYTHONPATH=. python3 -m research.residual_20260909.verify_bundle \
    --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k
PYTHONPATH=. python3 -m research.residual_20260909.replay_census \
    --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k --workers 4
```
