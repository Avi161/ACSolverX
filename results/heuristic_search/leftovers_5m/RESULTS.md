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
  (priority = L + 20·S + 2·MK), PARTIAL snapshot of 2026-08-31: 5 of 14
  rows solved (`ac19_27683`, `ac19_12445`, `ac19_28930`, `ac19_31298`,
  `ac19_54835`), each with the full AC-trivialization path and moves.
  The 4 duplicate `ac19_50841` error records are the OOM crash-loop
  incident (9 lanes admitted off thin early peaks; fixed operationally
  with `--workers 3`); the row is retried by resume and the readers
  (`classify_5m`) dedupe by name preferring finished records.

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
