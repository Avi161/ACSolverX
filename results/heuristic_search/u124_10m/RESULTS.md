# u124: 124 unsolved Miller-Schupp AC classes at 10M nodes (cap 64)

**Campaign complete, 2026-09-06.** The 124 rows of
`results/stable_ac/fable/aca_124.csv` under the `s20_mk2` arm
(priority = L + 20·S + 2·MK) at a 10,000,000-node budget, max relator
length 64, engine hcompact. **124/124 rows ran the full budget; 0 solved.**
Run on AWS Spot boxes (r6a.16xlarge 493 GiB, then r8ib.24xlarge 743 GB),
one row per lane, lanes admitted by the RAM governor.

## Files

- `u124_10m_s20_mk2_b10000000_mrl64.jsonl` — the final campaign file, 137
  records for 124 distinct rows: 124 finished records and 13
  reservation-exhaustion deaths that were retried and completed later
  (readers dedupe by name preferring finished records, as `classify_5m`
  does). Every earlier snapshot published here is a strict prefix of it.
- `aca_124_reduced_again.csv` — a companion reduction study of the same
  124 presentations, **not produced by this search**; see below.
- `run_log_u124.log` — the campaign run.log for 2026-08-31 (rows aca_0
  through aca_8 and the first exhaustion deaths). It is the early
  fragment, not the whole campaign: the box was rebuilt twice after it.

## Final tally

| quantity | value |
|---|---|
| rows | 124/124 complete, 0 errors outstanding |
| solved at 10,000,000 nodes | **0** |
| rows that ran the full budget | 124 |
| rows that lowered their presentation total | 14 (list below) |
| finished row time | 186.6 h (median 3,638 s, range 989–14,498 s) |
| row time lost to exhaustion deaths | 27.1 h across 13 deaths |
| peak RSS | 65.7–286.4 GB (the extremes are different engine generations; see below) |
| widest expansion reached | totals of 37–65 against the per-relator cap of 64 |

`min_relator_length` is the shortest **total** (|r1| + |r2|) any state in
the search reached; the per-relator cap of 64 bounds each relator, not the
total, so a recorded 65 is a legitimate two-relator total.

## What the search established

No presentation in this set is AC-trivialized by s20_mk2 within 10M nodes
at cap 64. Fourteen rows did reach a shorter total than they started at
(the rest are rigid at this budget — `min_relator_length` equals the
starting total and `min_relator` is the starting pair):

| row | start → min total | row | start → min total |
|---|---|---|---|
| `aca_36` | 18 → 17 | `aca_105` | 25 → 24 |
| `aca_55` | 19 → 18 | `aca_106` | 25 → 24 |
| `aca_78` | 21 → 19 | `aca_107` | 25 → 22 |
| `aca_88` | 23 → 21 | `aca_109` | 25 → 23 |
| `aca_99` | 25 → 22 | `aca_110` | 25 → 22 |
| `aca_100` | 25 → 22 | `aca_111` | 25 → 23 |
| | | `aca_113` | 25 → 23 |
| | | `aca_114` | 25 → 23 |

Every row is recorded with empty `path`/`path_moves`: no row solved, and
from engine_mem_gen 4 on this campaign runs with `track_path=False`
anyway. Had a row solved, its certificate would be recovered by re-running
that one row with paths on at its recorded node count — the search is
deterministic, so the re-run pops the identical sequence:

    python -m experiments.search.rerun_row --row aca_N --campaign u124 \
        --arm s20_mk2 --budget <nodes_explored> \
        --reserve-states 2140016900 --out-dir <dir>

then replaying `path_moves` through `greedy_baseline.moves_to_states`, as
the AC19 solves were certified. That the running build still finds solves
at all is checked by the positive control in
`experiments/heuristic_search/core/perf_lab/RUNBOOK.md` section 7.

## The reduction study (`aca_124_reduced_again.csv`)

A separate line of work on the same 124 presentations, archived here
because it is the other half of what became of this set. Its provenance is
in its own `source` column and it is **not** output of this search:

| `reduce_kind` | rows | `source` |
|---|---:|---|
| `mu_floor` | 35 | `mu_ladder_r256_b64` |
| `length_only` | 3 | `external_len_table` |
| `auto_cov_plus_complete_cov` | 1 | a wandb export of 2026-08-10 |
| none | 85 | — |

39 of the 124 carry a shorter (or equal-length, for `length_only`)
presentation in `new_r1`/`new_r2`, with `mu_in`/`mu_out` the totals before
and after and `n_hops` the ladder length. Checked against the campaign
here: the `name`, `r1`, `r2`, `n_members` and `members` columns match
`results/stable_ac/fable/aca_124.csv` row for row; `mu_in` equals the
starting total and `mu_out` equals `|new_r1| + |new_r2|` on every reduced
row; and the 14 rows the search itself shortened are a **subset** of the
39, with the study's `mu_out` never longer than the total the search
reached (equal on 8, shorter on 6). The two lines of work agree where they
overlap. A shorter presentation is not a solve: none of these rows is
AC-trivialized by either result.

## Engine generations in this file

The search is bit-identical across all four generations (oracle and
frozen-engine gates in `experiments/heuristic_search/core/perf_lab/`);
only memory profile and speed changed, which is why `engine_mem_gen` is
recorded per row and why the governor seeds learned peaks only from rows
of the generation running now.

| gen | rows | seconds (min–max, median) | peak RSS | what changed |
|---|---:|---|---|---|
| 2 | 38 | 4,111–13,695 (7,094) | 79.8–286.4 GB | adaptive width, reservations honored as-is |
| 3 | 5 | 11,864–14,498 (13,863) | 144.2–175.8 GB | the rate-floor RLIMIT cap in `plan_memory` |
| 4 | 4 | 11,202–13,775 (13,175) | 130.5–156.1 GB | one full-width arena, widen in place, no path capture |
| 5 | 77 | 989–13,758 (3,328) | 65.7–144.0 GB | 2-bit rows, allocation-free expansion, then the cut-shift skip and packed canonicalisation of `edfa8c68` |

The gen-2 286.4 GB peak (aca_37, which completed through a grow doubling
on the 493 GiB box) and aca_1's 158.0 GB repack are transients that no gen-4 or gen-5 row can produce. The
speed step inside gen 5 is the `edfa8c68` roll on 2026-09-05 with 53 of
124 rows complete: rows before it took 12,320–13,428 s, rows after it
2,350–2,839 s (4.4× to 5.2× per row, 4.49× measured per pop with identical
search statistics). Method, measurements and verification commands:
`perf_lab/REPORT.md`; operations: `perf_lab/RUNBOOK.md`.

## The reservation-floor ladder, and how it ended

The floor is the campaign's memory model: states reserved per popped node.
Each rung was set by rows that beat the previous one, and a row that
outgrows a rate-floored reservation dies with a clean, recorded
`MemoryError` naming its measured rate — never an OOM kill — and waits for
the next pass.

| floor | reserve | rows it lost | measured rate of the deaths |
|---:|---:|---|---|
| 110 | 1,100,016,900 | aca_0, aca_1 | records from before the field existed |
| 150 | 1,500,016,900 | none | — |
| 168 | 1,680,016,900 | aca_38 (×3), aca_39, aca_40, aca_41 | 175.83, 178.57, 180.34 |
| 214 | 2,140,016,900 | aca_63, aca_64, aca_65, aca_71, aca_72 | 218.51, 221.89, 222.16, 222.33, 222.83 |
| 236 | 2,360,016,900 | none | — |

All thirteen deaths were completed by a later pass; the final measured
maximum over the whole campaign is **222.83 states per popped node**
(aca_71). The lesson for any 10M campaign: a discovery rate measured over
the first half of a budget understates the rate at the end, so a floor set
from early evidence should be paired with a planned second pass
(`STATES_PER_NODE` raised, `RETRY_EXHAUSTED` naming the rows) rather than
trusted to cover everything. 214 is the last floor at which the hash table
stays 16 GiB; 236 doubles it to 32 GiB and costs a lane on a 743 GB box.

## Verification

Nothing here needs to be trusted. Against this file and the shipped row
list, a verifier can re-derive:

- **completeness and identity** — 124 distinct names, exactly those of
  `results/stable_ac/fable/aca_124.csv`, with `r1`/`r2` matching row for
  row, every finished record at `nodes_explored == 10,000,000`, no name
  whose only record is an error. Pinned by
  `tests/test_leftovers_5m.py::test_the_archived_u124_result_is_complete_and_consistent`.
- **the reduction study's arithmetic and its agreement with the search** —
  pinned by the test beside it.
- **the search itself** — the production CLI re-run on another machine
  reproduces the run bit for bit; widen points are content-determined and
  fingerprint the search (the 2026-09-01 check below), and the pure-Python
  reference `greedy_search_h` with the S20_MK2 config agrees with the
  engine on every shared field.

Earlier verification, unchanged and still valid: the production CLI
(`--campaign u124 --arm s20_mk2`, budget 1,000, cap 64) was re-run twice on
rows aca_0..aca_59 on a different machine (4-core x86 container vs the
campaign's 64-vCPU EPYC). The two runs are bit-identical; all ten
12B→24B widen points in `run_log_u124.log` (aca_0..aca_9: 523 / 2,415 /
423 / 348 / 837 / 816 / 378 / 2,127 / 13,999 / 10,641 states) reproduce to
the digit. The 24B→32B widens (113M–1.1B states) are correctly absent at a
1k budget. On the 2-bit engine the widen lines print half those widths
("6B → 12B"); the "at N states" figures are unchanged, which is the point.
