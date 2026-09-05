# AC19 leftovers at 5M nodes (cap 64)

The 102 rows that survived the 1M screen (88 greedy-arm + 14 s20_mk2-arm),
re-run at a 5,000,000-node budget with max relator length 64 (the 1M stage
ran at cap 48). Produced on the GCP campaign box (n2-highmem class,
251 GB), single chunk (`--chunks 1`), engine hcompact, engine_mem_gen 2.

## Files

- `leftovers_5m_greedy_b5000000_mrl64.jsonl` — the greedy arm, COMPLETE:
  88/88 rows, **57 solved / 31 unsolved** at 5M. This is the final file;
  earlier partial uploads (5-, 41-row snapshots) are strict prefixes of it.
- `leftovers_5m_s20_mk2_b5000000_mrl64.jsonl` — the s20_mk2 arm
  (priority = L + 20·S + 2·MK), COMPLETE: all 14 rows settled, **5 solved
  / 9 exhausted**, no outstanding errors. The solved rows (`ac19_27683`,
  `ac19_12445`, `ac19_28930`, `ac19_31298`, `ac19_54835`) each carry the
  full AC-trivialization path and moves. The 6 interleaved error records
  (5× `ac19_50841`, 1× `ac19_28131`) are the OOM crash-loop incident
  (9 lanes admitted off thin early peaks; fixed operationally with
  `--workers 3`); both rows were retried by resume and completed —
  readers (`classify_5m`) dedupe by name preferring finished records.
- `run_log_ac19.log` — the campaign run.log: the crash-loop restarts,
  the `--workers 3` cap taking effect, and every per-row landing line.

## Final tally (campaign complete, 102/102 rows, 2026-09-01)

Of the 88 rows that survived greedy's 1M screen: 57 solved by greedy at
5M; of the 31 greedy-exhausted, 19 were already solved by s20_mk2 at
≤1M (they are absent from its 1M-failure list by construction) and 3
more fell to s20_mk2 at 5M. **The residue unsolved by any arm at any
budget is 9 rows**: `ac19_16286`, `ac19_27254`, `ac19_28131`,
`ac19_44381`, `ac19_50841`, `ac19_51034`, `ac19_59576`, `ac19_65753`,
`ac19_7284`. Four of the nine reduced their presentation totals without
solving (16286: 19→17, 59576: 19→17, 65753: 20→17, 7284: 19→17); the
other five are rigid at this budget. Exhausted-row peaks sit at
~86.7-86.8 GB.

## Verification (2026-09-01)

All five solved s20_mk2 rows are replay-certified: their `path_moves`
were replayed from the starting presentation through
`greedy_baseline.moves_to_states` (which applies only legal Definition
2.1 moves via `replay_move_nj`), the replayed state sequence equals the
recorded `path` step for step, and every path terminates at the trivial
pair `['Y', 'X']`. The solves are certificates, independent of the
search that produced them.

## Notable

`ac19_12445` and `ac19_31298` were in the mutual hard core (unsolved by
BOTH arms at every earlier stage) and fell to s20_mk2 at ~1.3M nodes under
cap 64. The remaining hard core — `ac19_16286`, `ac19_27254`,
`ac19_28131` — is unsolved by greedy at 5M and pending in the s20 arm.
`ac19_27683` and `ac19_28930` (nearly identical presentations) solved at
the identical node count 1,383,279 — the search is deterministic and the
pair's corridors coincide.

## Next: the 10M stage (`CAMPAIGN=ac19_10m`), per arm

Both arms go to the same 10M budget on the same underlying orbit set,
each against its own residual list, so the baseline comparison stays at
equal budget. The lists are derived from the two jsonls above by
`experiments/search/make_ac19_10m_lists.py` (accounting in
`../ac19_autmin_screen/UNSOLVED_AFTER_5M.md`), runbook in
`experiments/heuristic_search/core/perf_lab/RUNBOOK.md` section 8.

| arm | 100k residue | solved at 1M (cap 48) | solved at 5M (cap 64) | to 10M | list |
|---|---:|---:|---:|---:|---|
| greedy | 222 | 134 | 57 | 31 | `unsolved_5m_baseline.csv` |
| s20_mk2 | 39 | 25 | 5 | 9 | `unsolved_5m_s20_mk2.csv` |

Of greedy's 31, the 22 not on the s20_mk2 list are rows s20_mk2 already
solved: 3 at 5M (`ac19_12445`, `ac19_31298`, `ac19_54835`), 9 at 1M, 4 at
100k and 6 at the 10k screen -- the "19 solved at <= 1M" above, split by
rung. The 9 are a subset of the 31 as presentations, so the two arms meet
head-to-head on them. 40 row-runs; the 10M column of this table is filled
in when the campaign lands.
