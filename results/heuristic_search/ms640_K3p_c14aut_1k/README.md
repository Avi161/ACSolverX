# Miller–Schupp 640 (the solved set), 1,000 charged units, policy `K3p_c14aut`

640 / 640 solved and verified; 0 unsolved; 0 errors. Maximum per-row charge
**267**; the whole panel costs **13,082** charged units.

- Input: `research/residual_20260909/panels/ms640.csv`, SHA-256
  `5ca1f7911cdfc76c643b0722369f51f61270f67e11633bd522c4bda21a907667`, built by
  `panels/build_ms640.py` from `data/ms640_solved.txt` (SHA-256 `fbf976f7…32a43`)
  — the 640 Miller–Schupp presentations the greedy baseline solved at a
  1,000,000-node budget, in source order (`ms_000` … `ms_639`).
- Policy: `K3p_c14aut` (`policies.py:408`) — 250-unit certified-overrun strict
  donor stage, 300-unit plain S20_MK2 stage, incumbent restart, BS-DEMOTE, with
  the cap-14 automorphism-closed backward table `tables/ball_cap14_aut.npz` as
  terminal at the root and at every generated state.
- Files: 8 shards `rows_*.jsonl` (one record per input row, in input order,
  carrying the mixed path `states`/`steps`), `SUMMARY.json`, `RESULTS.md`,
  `unsolved.csv` (empty), `replay_check.json`, `budget_sweep.json`,
  `comparison.json`, `census_run.log`.

## Where the units go

| route | rows | note |
|---|---|---|
| `ball_root` | 550 | the root itself is in the cap-14 ball — 0 charged units |
| `plain_s20` | 62 | |
| `bs_demote` | 24 | |
| `strict_donor` | 4 | |

Charge distribution: 550 rows at 0, 12 at 1–9, 22 at 10–49, 14 at 100–249,
42 at 250–267. Median 0, mean 20.4.

## Budget threshold

`budget_sweep.json` records the same panel at 1000 / 300 / 267 / 266 / 200 /
100 / 50. **267 is exact**: at 267 all 640 solve, at 266 four rows
(`ms_636`…`ms_639`, all of the form `YYYYYYYYXyyyyyyyx` against an 8-letter
second relator) miss. At 200: 626; at 100 and at 50: 612.

## Against the frozen policy, same panel, same budget

| | solved | units | max charge |
|---|---|---|---|
| `K3p_c14aut` | **640** / 640 | 13,082 | 267 |
| `frozen` (`final_policy`, 98f719e2) | 602 / 640 | 87,531 | 1,000 (exhausted) |

38 rows gained, 0 lost; on all 602 rows both solve, `K3p_c14aut` is strictly
cheaper (602 cheaper, 0 equal, 0 dearer). Per-row detail in `comparison.json`;
the frozen run is in `results/heuristic_search/ms640_frozen_1k`.

That the frozen policy misses 38 of these is not a contradiction of the census:
MS-640 is "solved" at a 1,000,000-node greedy budget, not at 1,000 units.

Reproduce and check:

```bash
PYTHONPATH=. python3 -m research.residual_20260909.panels.build_ms640
PYTHONPATH=. python3 -m research.residual_20260909.census_run \
    --input research/residual_20260909/panels/ms640.csv --policy K3p_c14aut \
    --budget 1000 --out results/heuristic_search/ms640_K3p_c14aut_1k \
    --shard-size 80 --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.census_summarize \
    --input research/residual_20260909/panels/ms640.csv \
    --result-dir results/heuristic_search/ms640_K3p_c14aut_1k
PYTHONPATH=. python3 -m research.residual_20260909.replay_census \
    --result-dir results/heuristic_search/ms640_K3p_c14aut_1k --workers 4
PYTHONPATH=. python3 -m research.residual_20260909.verify_bundle \
    --result-dir results/heuristic_search/ms640_K3p_c14aut_1k \
    --input research/residual_20260909/panels/ms640.csv \
    --expect-sha256 5ca1f7911cdfc76c643b0722369f51f61270f67e11633bd522c4bda21a907667 \
    --expect-rows 640
```

`verify_bundle` PASSes on this directory; `replay_check.json` records 640 / 640
certificates re-decoded and replayed to `['x', 'y']` in fresh processes, 0
failures. Clocks (4 workers, this container): search wall 1.6 s, certificate
decode + replay wall 2.0 s, census wall 5.6 s.
