# Miller–Schupp 640 (the solved set), 1,000 charged units, policy `K3p_c14aut`

640 / 640 solved and verified; 0 unsolved; 0 errors. Maximum per-row charge
**267**; the whole panel costs **13,082** charged units.

**Read the units with the table in mind.** `K3p_c14aut` looks every generated
state up in a precomputed 12.8M-state backward ball whose lookups are *not*
charged; 550 of these 640 roots are already inside it and cost 0 units. The
"≤ 267 units" is the forward search on top of that ball, not the whole
computation. The no-table controls are in the comparison section below.

- Input: `research/residual_20260909/panels/ms640.csv`, SHA-256
  `5ca1f7911cdfc76c643b0722369f51f61270f67e11633bd522c4bda21a907667`, built by
  `panels/build_ms640.py` from `data/ms640_solved.txt` (SHA-256 `fbf976f7…32a43`)
  — the 640 Miller–Schupp presentations the greedy baseline solved at a
  1,000,000-node budget, in source order (`ms_000` … `ms_639`).
- Policy: `K3p_c14aut` (`policies.py:408`) — 250-unit certified-overrun strict
  donor stage, 300-unit plain S20_MK2 stage, incumbent restart, BS-DEMOTE, with
  the cap-14 automorphism-closed backward table `tables/ball_cap14_aut.npz` as
  terminal at the root and at every generated state.
- Timing, one core, warm caches: the 640 rows take 4.1 s (search 1.9 s +
  certificate decode/replay 2.2 s); process wall 11 s, of which table load
  1.7 s, numba cache load 2.3 s, provenance hashing of `tables/` ~2 s.
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

## Same panel, same 1,000-unit budget, four policies

| policy | table | solved | units | max charge | rows at 0 units |
|---|---|---|---|---|---|
| `cascade_heuristics` (`experiments/search`, the MS-640 cascade: BS rewrite → L+40S with generator moves, cap 48 → S20_MK2) | none | **640** / 640 | 22,075 | 404 | 0 |
| `K3p_c14aut` (this bundle) | cap-14 ball | **640** / 640 | 13,082 | 267 | 550 |
| `K3p_notable` (same cascade, `table=None`) | none | 627 / 640 | 71,136 | 1,000 (exhausted on 13) | 0 |
| `frozen` (`final_policy`, 98f719e2) | none | 602 / 640 | 87,531 | 1,000 (exhausted on 38) | 0 |

- The MS-640 cascade solves everything without any table; re-run on this
  container (`ms640_cascade_heuristics_1k_rerun/`) it reproduces the saved
  record in `goal_frontiers/MS640_RESULTS.md` exactly (22,075 units, max 404,
  rewrite 254 / s40_gen 386 / fallback 0). Search wall 6.2 s on one core here
  (2.36 s on the machine of record).
- Against `frozen`, `K3p_notable` gains 26 and loses 1 (net +25); the table
  adds the last 13. Those 13 (`ms_527`, `ms_529`, `ms_568`, `ms_570`,
  `ms_573`, `ms_577`, `ms_578`, `ms_583`, `ms_584`, `ms_587`, `ms_602`,
  `ms_607`, `ms_615`) are all `Y^n X y^(n-1) x` against a 7–8-letter
  companion; the MS-640 cascade's `s40_gen` arm takes them in 41–331 units,
  and the 24 rows `K3p_c14aut` closes by BS-DEMOTE at 250–267 units cost it
  10–46. On this panel the MS-640 cascade is the better no-table policy; the
  AC19 cascade's gains are on AC19.
- On the 602 rows both `K3p_c14aut` and `frozen` solve, `K3p_c14aut` is
  cheaper on every one — but 550 of those are table hits. Per-row detail in
  `comparison.json`; the frozen and no-table runs are in
  `results/heuristic_search/ms640_frozen_1k` and `ms640_K3p_notable_1k`.

`frozen` missing 38 of these is not a contradiction of the MS census: MS-640
is "solved" at a 1,000,000-node greedy budget, not at 1,000 units.

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
