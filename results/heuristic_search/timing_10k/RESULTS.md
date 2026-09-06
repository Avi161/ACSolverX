# Matched subset 60 timings at 10,000 pops

Fresh single-pass measurements, budget 10,000 per presentation, relator cap 48, **no timeout**. All four methods use the same engine and path-capture settings. Searches ran sequentially with one numerical-library thread and cooldowns.

**S20_MK2 has the highest coverage at 10k. L+40S with generator moves is
fastest on the presentations both solve.** Both generator candidates solve
the same 49 rows; S20 solves those and three more (ms596, ms605 and ms610).
The 1k coverage advantage of the new candidates does not persist at 10k.

## Coverage and total workload

These totals include all 60 searches, including unsolved rows. They are not the shared-solve timing comparison.

| Method | Solved /60 | Total search wall (s) | Total search CPU (s) | Total pops |
|---|---:|---:|---:|---:|
| Greedy | 40 | 44.940204 | 42.888042 | 248,227 |
| S20_MK2 | 52 | 23.371998 | 23.284816 | 141,776 |
| L+40S + generator moves | 49 | 29.957705 | 29.532629 | 114,318 |
| L+20S+1.5W + generator moves | 49 | 37.099650 | 36.954880 | 118,508 |

## Pairwise means on presentations both solve

For each row below, both means use exactly the same solved-ID intersection. Each mean is the arithmetic mean per presentation; it excludes failed searches. Different pairs may use different subsets, so do not compare means across rows as though the input set were fixed.

| Method A | Method B | Shared solves | A mean wall (ms) | B mean wall (ms) | A mean CPU (ms) | B mean CPU (ms) |
|---|---|---:|---:|---:|---:|---:|
| Greedy | S20_MK2 | 40 | 209.494 | 35.130 | 181.455 | 35.047 |
| Greedy | L+40S + generator moves | 40 | 209.494 | 15.172 | 181.455 | 15.081 |
| Greedy | L+20S+1.5W + generator moves | 40 | 209.494 | 27.722 | 181.455 | 27.658 |
| S20_MK2 | L+40S + generator moves | 49 | 130.608 | 21.028 | 130.075 | 20.710 |
| S20_MK2 | L+20S+1.5W + generator moves | 49 | 130.608 | 39.477 | 130.075 | 39.228 |
| L+40S + generator moves | L+20S+1.5W + generator moves | 49 | 21.028 | 39.477 | 20.710 | 39.228 |

## Fixed subset solved by all four: 40 presentations

| Method | Mean search wall (ms) | Mean search CPU (ms) | Mean pops |
|---|---:|---:|---:|
| Greedy | 209.494 | 181.455 | 1205.675 |
| S20_MK2 | 35.130 | 35.047 | 280.100 |
| L+40S + generator moves | 15.172 | 15.081 | 63.875 |
| L+20S+1.5W + generator moves | 27.722 | 27.658 | 127.875 |

## Solved-set differences

- Greedy versus S20_MK2: A-only: none. B-only: ms568, ms573, ms575, ms578, ms583, ms596, ms605, ms610, ms628, ms633, ms634, ms635.
- Greedy versus L+40S + generator moves: A-only: none. B-only: ms568, ms573, ms575, ms578, ms583, ms628, ms633, ms634, ms635.
- Greedy versus L+20S+1.5W + generator moves: A-only: none. B-only: ms568, ms573, ms575, ms578, ms583, ms628, ms633, ms634, ms635.
- S20_MK2 versus L+40S + generator moves: A-only: ms596, ms605, ms610. B-only: none.
- S20_MK2 versus L+20S+1.5W + generator moves: A-only: ms596, ms605, ms610. B-only: none.
- L+40S + generator moves versus L+20S+1.5W + generator moves: A-only: none. B-only: none.

## Verification, timing scope and limits

All 190 solved records passed move-by-move certificate replay. All 163 previous 1k solved records retained exactly the same pop count, state path, move path and generator-evaluation count. The input and source hashes were unchanged throughout the run.

Times surround the full search call, including initialization, successful path reconstruction and local search-object cleanup. They exclude warm-up, explicit pre-search garbage collection, replay, historical checks, output and cooldown.

Warm-up: 0.696s. Batch elapsed including cooldowns: 365.654s. Total certificate replay: 0.095s. Longest individual search: 3.413s.

Execution: arm64, macOS-26.5.2-arm64-arm-64bit-Mach-O; priority adjustment denied; inherited priority retained. One worker and numerical-library thread; the OS chooses the physical CPU core. This is one matched timing pass, not a repeated-run estimate of measurement noise.

The largest wall/CPU discrepancy on a shared solve is greedy on ms602:
2.482 s wall versus 1.400 s CPU. The 40-row greedy mean is consequently
209.494 ms wall versus 181.455 ms CPU. Both clocks are preserved; the
reported wall means are not corrected or replaced by CPU measurements.

The two generator methods use mixed Aut/substitution paths. The controls use substitution-only paths. The same subset selected the new methods at 1k, so this 10k budget extension is exploratory, not an independent validation. Production defaults remain S20_MK2.

## Evidence

- `runs.jsonl`: 240 per-presentation records with clocks, paths and verification flags.
- `summary.json`: exact IDs, totals, arithmetic means and all six intersections.
- `manifest.json`: settings, source/input hashes, environment and timing protocol.
- `PROTOCOL.md`: predeclared design and reproduction command.
- `AUDIT.md`: independent read-only review.
