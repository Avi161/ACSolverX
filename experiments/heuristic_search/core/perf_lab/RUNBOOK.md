# Campaign runbook: the configuration the next campaign starts from

Operational companion to `REPORT.md` (which holds the measurements, the
identity arguments and the verification commands; nothing there is
repeated here). Written 2026-09-05 after the u124 campaign rolled the
promoted build.

## 1. The build to pin

| | |
|---|---|
| campaign default build | `edfa8c68` on `claude/ac19-leftover-solver-notebook-6yan6d` |
| engine-identical through | `41a59ea1` (every commit after `edfa8c68` is docs and result JSONs under `perf_lab/`) |
| what it is | 2-bit rows, in-place widen, no path capture for u124, allocation-free expansion kernel, cut-shift skip, packed-word canonicalisation |
| memory generation | `ENGINE_MEM_GEN = 5` (unchanged from `3093592d`; peaks recorded under 5 seed the governor, older ones do not) |

The box-side boot script (operator's `boot4.sh` in S3, not in this repo)
checks out that SHA, restores the campaign jsonl from S3 when S3 has more
rows, and exports `STATES_PER_NODE=214` and `RETRY_EXHAUSTED=aca_38`. On
this build both exports are optional: 214 equals the campaign constant,
and the named `RETRY_EXHAUSTED` re-admits exactly the rows it names, so it
is safe to leave in an unattended unit.

## 2. The u124 profile, and where each number lives in the checkout

| setting | value | where |
|---|---|---|
| reservation floor | 214 states per popped node | `CAMPAIGNS["u124"]["states_per_node"]` in `experiments/search/run_leftovers_5m.py` |
| path capture | off | `CAMPAIGNS["u124"]["track_path"]` (certificates by deterministic re-run: `results/heuristic_search/u124_10m/RESULTS.md`) |
| reservation | 2,140,016,900 states (214 x 10M + 4 x 65^2) | `plan_memory` |
| bytes per reserved state | 51 (32 B row at cap 64 + 19 B metadata) | `_per_state_bytes` via `hcompact.row_width_h` |
| allocation-backed worst per lane | 117.6 GiB (51 B x 2.14B + 16 GiB table) | `_reserved_worst_gb`, printed by `run_remote.sh plan` |
| per-child RLIMIT_AS under the floor | allocation + 10 GiB = 127.6 GiB | `plan_memory` (the rate-floor cap: an over-floor row dies a clean recorded MemoryError, never an OOM kill, on every box size) |
| lanes | floor((MemAvailable - 4 GiB) / 117.6 GiB) | `RamGovernor.capacity` |
| second pass over rows that died at exhaustion | `STATES_PER_NODE=<higher>` in the environment, `RETRY_EXHAUSTED=1` or `RETRY_EXHAUSTED=aca_38,aca_40` | baked into the job by `write_job` when set |

Lanes by box class, as `run_remote.sh plan` prints them today from the
checkout alone (no environment):

| box | admissible RAM | lanes |
|---|---|---|
| r8ib.24xlarge, 743 GB | 739 | 6 |
| 512 GiB class (r6a/r5a.16xlarge) | 489 | 4 |
| 256 GiB class (8xlarge) | 246 | 2 |
| 1.5 TiB | 1532 | 12 |

The governor can seat one more lane than the allocation arithmetic after
three completed rows report peaks well under the worst (it predicts 1.25x
the largest measured peak). Rows at the measured maximum rate, 186 states
per node, peak near 104 GiB physical, so that extra lane is safe for the
measured population; `--workers N` (or `WORKERS=N` for the job) pins the
count when zero OOM exposure is preferred.

## 3. A fresh box from the checkout alone

`run_remote.sh` clones `BRANCH` (default: the campaign branch) at depth 1,
installs numba and numpy if missing, and derives everything from the
checkout: the campaign's budget, cap, floor, path setting and memory
generation come from `run_leftovers_5m.py`, the job pins BLAS/OMP/numba
threads to 1 and runs unbuffered, and the systemd unit restarts the job
after a reboot or a preemption. Confirmed 2026-09-05: `plan` prints the
figures in section 2 with no environment set.

    # price a box before renting it (no engine, no rows)
    CAMPAIGN=u124 PLAN_GB=743 PLAN_CORES=96 bash experiments/search/run_remote.sh plan
    # on the box: prove the pipeline, then install the unit
    CAMPAIGN=u124 bash experiments/search/run_remote.sh smoke
    CAMPAIGN=u124 bash experiments/search/run_remote.sh install-service
    CAMPAIGN=u124 bash experiments/search/run_remote.sh verify     # read-only gate list

What is NOT in the checkout and must be re-created per account: the boot
script that pins the SHA and syncs the jsonl to S3, the spend backstop
(an AWS Budgets action or a wall-clock shutdown), and the box choice.
The cost reasoning that led to on-demand over spot for this workload is
in the session record, not the repo: with restart-from-zero rows of
several hours, spot only wins when the mean instance lifetime exceeds a
few times the row length.

## 4. Measured campaign-regime numbers (details in REPORT.md 7 and 8)

| what | before | after | measured how |
|---|---|---|---|
| per-lane rate from the expansion-kernel rewrite alone (`3093592d`) | 1.0x | ~1.0x at campaign length (1.74x in the lab at 50k pops did not transfer) | campaign box, rows aca_47..51 vs the previous row family |
| peak RSS per row from 2-bit rows | 155 to 156 GB | 96.7 to 101.1 GB (1.55x to 1.60x lower) | first four `3093592d` rows |
| lanes on the 743 GB box | 4 | 6 | governor |
| per-pop time, `3093592d` -> `edfa8c68` | 941.6 us | 209.8 us (4.49x) | `phase_split.py --rows aca_47 --budget 300000` on the campaign box, identical search statistics (44,077,944 states, 331.7 candidates per pop, 146.9 inserts per pop) |
| live per-lane rate at six lanes, `edfa8c68` | 1,000 to 1,300 pops/s | 3,875 to 6,203 pops/s | four minutes after the roll |
| 10M-row wall time | 12,300 to 13,800 s | expected 2,500 to 4,000 s (fill in from the first completed rows) | campaign records |

## 5. Rules learned, stated as rules

1. A lab bench at 50k to 100k pops on short rows does not transfer to
   campaign length. Every speed claim is measured at 300,000 pops on a
   real campaign row (`aca_47`) against a frozen copy of the build the
   campaign is running, on a box whose regime matches (compute-bound here:
   the lab box reproduces it at that budget in about 5 GB).
2. Diagnose before choosing a target: `phase_split.py` (and `--sub` for
   the inside of the expansion kernel) at 300k pops, plus `perf stat` IPC
   and dTLB misses on a live worker. The first round of this lab optimised
   the hash table on the strength of a memo; the split showed the table
   was 8% of a pop.
3. Right-sized runs: gates at 60 rows x 1,000 and 6 rows x 30,000; one
   300k run as the decision bench; the full suite once at the end; never
   re-run a gate that passed on the same code.
4. The frozen reference moves with every promotion: after a roll, re-copy
   the running build's engine files (now `hcompact.py`, `hexpand.py`,
   `greedy_baseline.py`, `hfast.py`) into a new `perf_lab/frozen<N>/` the
   way `frozen2/` was built, so the next round measures against what the
   campaign actually runs.
5. Known tooling caveat on builds with the cut-shift skip: the phase
   split's `expand` timer replays the unskipped reference kernel, so it
   over-counts (the operator saw expand 408 us inside a 209.8 us pop with a
   negative residual). The plain per-pop total is right; a replay through
   `expand_and_score_h(skip=True)` is the pending fix.
6. Skipping a bit-identity gate to save time is never a saving. Every
   change in this lab was proved identical by construction and then
   checked by the oracle and the frozen twin before it was benched.

## 6. Row hygiene

- A row that dies at reservation exhaustion is deferred, not retried at
  the same sizing (`_deferred_exhausted`); the death record carries the
  measured states-per-node. Re-admit with a higher `STATES_PER_NODE` or
  `RETRY_EXHAUSTED=<names>`.
- Rows recorded under earlier memory generations are valid results (the
  search is identical across every generation); only their peaks are
  ignored for governor seeding.
- A solved u124 row has empty `path` fields by design; recover the
  certificate with `rerun_row` at the recorded node count and the
  campaign's reservation, then replay the moves (RESULTS.md).
