# Campaign runbook: the configuration the next campaign starts from

Operational companion to `REPORT.md` (which holds the measurements, the
identity arguments and the verification commands; nothing there is
repeated here). Written 2026-09-05 after the u124 campaign rolled the
promoted build; u124 itself finished 2026-09-06 (124/124 rows at the full
10M budget, 0 solved -- `results/heuristic_search/u124_10m/RESULTS.md`),
and section 2 now records what its floor ladder ended at.

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
the largest measured peak). Rows at the rate measured when this was
written, 186 states per node, peak near 104 GiB physical, so that extra
lane is safe for the measured population; `--workers N` (or `WORKERS=N`
for the job) pins the count when zero OOM exposure is preferred.

**How the ladder ended.** Five more rows beat the 214 floor late in the
campaign (aca_63, aca_64, aca_65, aca_71, aca_72, at 218.51 to 222.83
states per node, all dying past 9.6M of their 10M pops), and a second pass
at `STATES_PER_NODE=236` with `RETRY_EXHAUSTED` naming them completed all
five: 144.1 GiB a lane without paths, five lanes on the 743 GB box,
because 236 doubles the hash table to 32 GiB. Campaign maximum:
**222.83 states per popped node**. The rule this leaves behind is in the
row-hygiene section: a discovery rate measured over the first half of a
budget understates the rate at the end, so a floor chosen from early
evidence is a first pass, not a guarantee -- plan the second pass rather
than paying for the extra lane up front.

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
| 10M-row wall time | 12,320 to 13,428 s (aca_47, 50, 49, 48) at 96.7 to 101.1 GB peak | 2,350 to 2,839 s (aca_54, 58, 57, 56) at 90.0 to 100.4 GB peak: 4.4x to 5.2x per row, peak RSS unchanged | first four completed rows on each build, same box, six lanes |
| box aggregate | ~3,600 nodes/s on `5d047da5`, ~5,400 on `3093592d` | ~23,000 nodes/s across six lanes | campaign box |

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
- A row's discovery rate is not flat in pops: u124 rows that cleared 168
  states per node for 9.5M pops died at 175 to 180, and rows that cleared
  214 for 9.6M pops died at 218 to 223. Expect a floor set from early or
  half-budget evidence to lose a few rows at ~96% of budget, and budget one
  second pass for them instead of over-reserving every lane.
- A solved u124 row has empty `path` fields by design; recover the
  certificate with `rerun_row` at the recorded node count and the
  campaign's reservation, then replay the moves (RESULTS.md).

## 7. Positive control: prove the running build still solves

Every u124 row is unsolved by construction, so a build that silently
stopped solving would look identical to a healthy one. `ac19_15866`
(`r1 = YXXXyXYx`, `r2 = YXyxxxyxx`, in
`results/heuristic_search/ac19_autmin_screen/unsolved_10k_s20_mk2.csv`)
is solved by s20_mk2 at 17,369 nodes with a 96-move path, and greedy
leaves it unsolved at 1M (cap 48) and 5M (cap 64). Its widest expanded
total is 35, so caps 48 and 64 give the identical search. Run it from the
checkout on an idle core; it never touches a campaign jsonl and needs no
environment (`STATES_PER_NODE` applies only to campaigns with a floor):

    nice -n 10 taskset -c <idle core> env PYTHONPATH=. python3 -m experiments.search.rerun_row \
      --row ac19_15866 --campaign ac19 --arm s20_mk2 \
      --csv results/heuristic_search/ac19_autmin_screen/unsolved_10k_s20_mk2.csv \
      --budget 1000000 --mrl 64 --out-dir <dir>

Expected record: solved true, nodes_explored 17369, path_length 96, path
of 97 states ending `["Y","X"]`, 96 path_moves, min_relator_length 2,
max_relator_length_expanded 35. Capture is on by default in `rerun_row`
and does not alter the search, so the record is the certificate; replay
it with `greedy_baseline.moves_to_states` over `str_to_move` of the moves
and check it equals the recorded path. Any other node count means the
search is not the one that produced the archive: stop the campaign and
find out why before reading any result.

Run on the campaign box on `edfa8c68` (2026-09-05, core 95, nice 10,
campaign untouched): both the u124 configuration (cap 64, 1M budget,
1.97 s, 1.31 GB peak) and the archived configuration (cap 48, 200k
budget) returned 17,369 / 96 / 2 / 35 exactly, and the replay ended at
the trivial pair.

## 8. ac19_10m: the AC19 residue at 10M, per arm

The 10M stage of AC19 is shaped exactly like its 1M and 5M stages: each
arm runs its own unsolved-at-5M rows against its own CSV, into its own
jsonl. Nothing crosses arms. `CAMPAIGNS["ac19_10m"]` in
`experiments/search/run_leftovers_5m.py`, `SPEC_10M` beside it.

| arm | rows | list (in `results/heuristic_search/ac19_autmin_screen/`) | out file |
|---|---:|---|---|
| greedy | 31 | `unsolved_5m_baseline.csv` | `$OUT/ac19_10m_greedy_b10000000_mrl64.jsonl` |
| s20_mk2 | 9 | `unsolved_5m_s20_mk2.csv` | `$OUT/ac19_10m_s20_mk2_b10000000_mrl64.jsonl` |

Both lists are written by `experiments/search/make_ac19_10m_lists.py`
from the two 5M jsonls (never by hand), with `UNSOLVED_AFTER_5M.md`
beside them naming the rung at which s20_mk2 solved each of the 22
greedy failures that are not on its own list (3 at 5M, 9 at 1M, 4 at
100k, 6 at the 10k screen). `python3 -m experiments.search.make_ac19_10m_lists
--check` reports drift; `tests/test_leftovers_5m.py` re-derives the lists.
The 9 are a subset of the 31 as presentations, so the two arms meet
head-to-head on those 9 at equal budget.

Profile on the campaign box (743 GB, 96 threads), both arms identical:

| quantity | value | where |
|---|---|---|
| budget, cap | 10,000,000 nodes, 64 | `CAMPAIGNS["ac19_10m"]` |
| reservation floor | 214 states per popped node (u124's) | same |
| paths | captured, 8 B/state (AC19 convention: every solve carries its moves) | same |
| reserve_states | 2,140,016,900 | `plan` prints it |
| allocation-backed worst per lane | 133.6 GiB (59 B/state + 16 GiB table) | `plan` prints it |
| child RLIMIT_AS | 143.6 GiB (allocation + 10 GiB margin) | `plan_memory` |
| lanes | 5 (743 - 4) // 133.6; 6 without paths | governor arithmetic |
| wrong-search alarm | any solve at or below 5,000,000 nodes at cap 64 | `report` |

Why a floor and not the est curve: est-based sizing at 10M reserves
915,490,520 states (91.5 per popped node) and admits 8 lanes at 88.4 GB.
At 5M the est curve reserved 463.8M, and the 5M records say most rows on
both lists outgrew it -- all 9 s20_mk2 rows peak at the same 86.7 GB and
24 of the 31 greedy rows at the same 72.9 GB, the gen-2 grow transient,
one `reservation exceeded at 463,821,9xx states` line each in
`results/heuristic_search/leftovers_5m/run_log_ac19.log` -- and none
doubled twice, so those rows discover between 92.8 and 185.5 states per
popped node. At 10M every one of them would blow through 915M and, with
no rate floor, take an ungated grow doubling to 1.83B states (~117 GiB
steady, ~175 GiB during the copy) on lanes admitted at 88 GB: the 5M
stage's crash loop again. 214 covers the whole interval with 15% over
its top at the last value that keeps the table at 16 GiB. A row above
214 dies at reservation exhaustion with its rate recorded and waits for
the second pass, as on u124 (section 6).

Expect that second pass to have work: the (92.8, 185.5) interval is what
these rows demonstrated over their first 5M pops, and u124's history says
the rate climbs with pops (its rows died at 218 to 223 after clearing 214
for 9.6M). Raising the floor to 236 up front would cost a lane -- 161.7
GiB with paths at 10M, four lanes instead of five -- so the cheaper plan is
five lanes at 214 and one pass at `STATES_PER_NODE=236` over whatever
dies, which is what the boot table below is written for.

Preview, from the checkout on the box (prints the table above):

    cd ~/ACSolverX && CAMPAIGN=ac19_10m OUT=$HOME/ac19_10m ./experiments/search/run_remote.sh plan

Boot env for the service (`install-service` reads these at write time):

| variable | first pass | second pass (rows that died at exhaustion) |
|---|---|---|
| `CAMPAIGN` | `ac19_10m` | `ac19_10m` |
| `OUT` | `$HOME/ac19_10m` (its own dir; the same dir as u124 is also safe, the prefixes differ) | same |
| `ARMS` | unset = `greedy s20_mk2`, run in that order by one job; `ARMS=s20_mk2` runs one arm | same |
| `STATES_PER_NODE` | unset (the campaign carries 214; `=214` is a no-op) | `236` |
| `RETRY_EXHAUSTED` | unset (nothing to retry) | the names, comma-separated, never `1` in an unattended unit |
| `BUDGET`, `MRL` | unset (10,000,000 and 64 follow from the campaign) | same |

The job runs greedy's 31 to completion, then s20_mk2's 9, each with its
own governor; resume skips finished rows per file, and a preemption
restarts wherever it was. Cost, at one full-budget row per 2,800 to
3,300 s per lane (3,000 to 3,600 pops/s on edfa8c68, measured on u124
rows, which are longer than these): greedy 31 rows on 5 lanes is 5.7 h
worst case, s20_mk2 9 rows is 1.7 h, 7.4 box-hours if no row solves
early -- about $15 on the $1.98/h spot box, with each second-pass row
adding one row-time. `plan` prints these hours.

When it lands: copy both jsonls and `run.log` to
`results/heuristic_search/ac19_10m/`, run the generator's `--check`
(the lists must still derive), replay-certify every solve as in
`results/heuristic_search/leftovers_5m/RESULTS.md`, and write the
ladder line there: greedy 222 -> 134 solved at 1M -> 57 at 5M -> N at
10M; s20_mk2 39 -> 25 -> 5 -> N.

### What it actually did (2026-09-06, COMPLETE)

Ladder line: greedy 222 -> 134 -> 57 -> **3**; s20_mk2 39 -> 25 -> 5 ->
**0**. Archive and certificates in
`results/heuristic_search/ac19_10m/RESULTS.md`. No `run.log` was
delivered with the jsonls.

**The 214 floor was enough and the second pass never happened.** All 40
row-runs reached their full 10,000,000 pops; no error records, no
reservation exhaustion, so nothing was left for `STATES_PER_NODE=236`.
Peak RSS over all 40 rows was 108.15 GB (greedy 49.4-92.3, s20_mk2
90.6-108.2) against the 133.6 GiB allocation-backed worst per lane --
about 75% of it, five lanes together peaking near 541 GB of 743 GB. The
prediction above that the rate would climb past 214 with pops, as it did
on u124, did not hold for these rows: they are shorter than u124's, and
none of them exceeded the floor over the full 10M. Read that as a fact
about this row set, not a licence to drop the floor elsewhere -- u124
still died at 218 to 223.

Cost came in under the estimate: 22.18 core-hours of row time (greedy
16.14, s20_mk2 6.04) against the 7.4 box-hour worst case, which is about
4.4 h of box wall-clock at five lanes with perfect packing.

The wrong-search alarm (any solve at or below 5,000,000 nodes at cap 64)
did not fire: the three solves came in at 5.31M, 8.01M and 8.20M pops.

Scientifically the stage was a null. All three greedy solves are rows
s20_mk2 had already solved at 100k, 100k and 1M -- 472x, 334x and 29x
fewer nodes -- so no presentation changed AC-status and the mutual
residue is the same 9 rows it was after 5M. On those 9 the arms tied on
`min_relator_length` row for row while s20_mk2 spent 1.14x the wall and
1.27x the memory to explore words 11 to 16 letters longer. Before
provisioning a 20M stage, note that the 28 exhausted greedy rows collapse
onto only 18 distinct minimal presentations (three of the groups landing
on the start of another row in the same list), so the residue is a
smaller problem than its row count suggests and a budget doubling is not
what is binding on it.

## 9. ac19_cascade_screen: the whole screen, on a small box

Every other campaign in this runbook is sized by RAM. This one is not,
and that is the only reason it exists as a separate stage: it sweeps all
72,779 AC19 Aut-min orbits at a 501-node budget, touches hcompact only
for an import, and reserves nothing. It is the one campaign here that a
cheap two-to-four-core VM runs well.

| quantity | value | where |
|---|---|---|
| rows | 72,779 orbits (all of them) | `ac19_autmin_screen/ac19_autmin_orbits.csv` |
| budget, cap | 501 nodes, cap 255 | `hybrid_10m.PREFIX_BUDGET`, `SEARCH_CAP` |
| search | `cascade_heuristics.search`: basis normalization, then the BS rewrite, then `s40_gen` | `experiments/search/cascade_heuristics.py` |
| peak RSS | 0.18 GB per worker, measured | `plan` prints it |
| worker RLIMIT_AS | 2.0 GB (an order of magnitude of headroom) | `run_ac19_cascade_screen.WORKER_RLIMIT_GB` |
| sizing rule | `2 GB x workers + 1 GB`; 8 workers fit in 17 GB | `plan` prints it |

    CAMPAIGN=ac19_cascade_screen ./experiments/search/run_remote.sh plan
    CAMPAIGN=ac19_cascade_screen ./experiments/search/run_remote.sh smoke
    CAMPAIGN=ac19_cascade_screen ./experiments/search/run_remote.sh run

`SCREEN=1` is set by the campaign case and routes `plan`, `smoke`, `run`
and `report` past the big-RAM planner -- which would otherwise price a
reservation this stage never makes. Resume, chunking and the detached
job work exactly as they do for the other campaigns.

### The row list has to be rebuilt before the first run

The screen list itself was never committed; only its residues were. Build
it once, from the dataset, and let it cross-check itself against every
shipped residue CSV before you trust it:

    PYTHONPATH=. python3 -m experiments.search.make_ac19_autmin_screen --write

That prints `agreement : exact on every shipped row` or dies. It is about
6 minutes on two cores.

### What comes back, and the one column that matters

`cascade_heuristics`' `s40_gen` arm pushes Nielsen images into the same
heap as AC substitutions. A path that uses one proves AC-triviality of an
automorphic image, not of the presentation, so the runner splits them and
`solved` counts only the first kind:

| column | meaning |
|---|---|
| `solved` | AC-trivialized. Substitution-only, replayed through `moves_to_states`, lands on a terminal pair. |
| `aut_assisted` | Solved only by also changing basis. Recorded, never counted as solved, never certified. |
| `certificate_sha256` | Digest of the move sequence. The run jsonl does not carry paths (57 MB even so); `certify` regenerates and re-verifies them. |

This is the same distinction `hybrid_10m.run_hybrid_10m` enforces by
refusing a prefix solve outright. That refusal is right for its three
pinned rows and wrong for a screen, where the prefix settles most of the
list; here the split replaces the refusal.

### The ladder, and where this stage hands off

Almost every orbit falls at 501 nodes; a thin tail wants more. Rather
than re-running the whole screen at each budget, `ladder` runs rung N+1
over rung N's `unsolved_*` CSV. That is sound because a search at budget
B is exactly the first B pops of any longer search, so a row solved at
501 stays solved at 100,000 and never needs re-running.

    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen         ladder --arm ac501 --workers 3

Rungs are 501 -> 1,000 -> 10,000 -> 100,000. It stops at 100,000 because
`cascade_heuristics.search` refuses more and because past that point this
stage is no longer the cheap one: what survives 100,000 nodes is the
short list for the big-RAM campaigns (`ac19` at 1M/5M, `ac19_10m`,
`ac19_hybrid_10m`), which are sized by reservation, not by wall clock.

### What gets committed

The raw run jsonl is git-ignored. What ships is what the next stage
reads: `unsolved_cascade501.csv`, `aut_assisted_cascade501.csv`, the
certificates file, and `RESULTS.md`. `run` writes the residues itself;
`certify` writes the certificates on demand.

## 10. Cap 255 buys nothing on the AC19 rows -- do not provision for it

`ac19_hybrid_10m` runs at cap 255 and, since `0e77ffce`, captures paths.
That plans a 2,140,262,144-state reservation: **325.0 GiB
allocation-backed per lane, 335.0 GiB RLIMIT**, against cap 64 with paths
at 133.6 / 143.6. On a 768 GB box that is 2 lanes instead of 5. (Path
capture itself is cheap here -- 309.0 GiB without it, so 2 lanes either
way; the cap is what costs the other three.) Before paying for it, two
measurements say the wider cap explores the same states.

**From the finished archive.** Across all 40 completed `ac19_10m`
row-runs at cap 64 -- 400 million popped nodes -- the longest relator any
expansion ever produced is **39 letters**. Zero rows of 40 reached the
cap. (`max_relator_length` in those records is the configured cap echoed
back; `max_relator_expanded` is what the search actually made.)

**Directly, on the nine rows that are still open.** s20_mk2, 400,000
nodes, cap 64 against cap 255:

| row | cap 64 states | cap 255 states | longest relator |
|---|---:|---:|---:|
| ac19_16286 | 55,790,334 | 55,790,334 | 29 |
| ac19_27254 | 51,061,320 | 51,061,320 | 24 |
| ac19_28131 | 55,788,484 | 55,788,484 | 29 |
| ac19_44381 | 58,706,251 | 58,706,251 | 23 |
| ac19_50841 | 48,565,359 | 48,565,359 | 25 |
| ac19_51034 | 49,963,796 | 49,963,796 | 31 |
| ac19_59576 | 55,790,114 | 55,790,114 | 29 |
| ac19_65753 | 50,023,522 | 50,023,522 | 31 |
| ac19_7284  | 54,610,254 | 54,610,254 | 31 |

Nine of nine identical, state for state. The cap never binds, so cap 255
costs 2.3x the memory and 3 of 5 lanes for the same search.

### Two different caps -- clamp the wrong one and the rewrite breaks

`cascade_heuristics.search` carries two caps and only one of them costs
memory. Astra's development note on the 60-row subset gives both ("hybrid
search uses 48, with rewrite cap 256 and observed maximum 131"), and the
72,779-row screen confirms the number exactly:

| cap | what it bounds | measured need | costs |
|---|---|---:|---|
| `cap` (search) | children `mixed_search`/hcompact will keep | **max 31** on the 9 open rows at 400k nodes; **max 39** across 40 rows at 10M | the reservation -- 133.6 GiB/lane at 64, 325.0 at 255, both with paths |
| `intermediate_cap` (rewrite) | `bs_collapse`'s intermediate relators | **max 131**, p99 41, median 13 over 72,779 rows | nothing -- pure Python, no arena |

Across the whole screen, 23 rows of 72,779 produced a relator longer than
64. **All 23 are the rewrite's intermediates; zero come from the search.**
Zero rows exceed 131, so Astra's 256 has ample headroom.

So the two settings pull in opposite directions and both are right:
keep `intermediate_cap` at 256 or `None`, and drop the hcompact search
cap to 64. `hybrid_10m` currently sets `SEARCH_CAP = 255` for both, which
buys the rewrite nothing it does not already have and costs the search
2.4x its memory -- and, on a 768 GB box, three of its five lanes.

Two more consequences worth stating as rules:

- **A cap is a pruning parameter, not a capacity parameter.** Raising it
  changes results only if the search was hitting it. Check
  `max_relator_expanded` on a finished run before widening one.
- **The discovery rate here is 139.5 states per popped node** (55.8M
  states / 400k nodes), well under the 214 floor the campaigns reserve
  against. The floor is conservative on AC19 rows, which is why no 10M
  row died at reservation exhaustion.

### And 10M is the engine ceiling, not a choice

State ids are signed int32, so the reservation cannot exceed 2,147,483,647
states -- **10,034,970 nodes at the 214 floor**. The 10M stage already
sits at 99.65% of that. `plan_memory` clips a 15M or 20M request back to
the int32 maximum, and rows then die at reservation exhaustion rather
than finishing short. Going past 10M needs int64 state ids in
`hcompact.py`, which is an engine change and goes through the full
promotion recipe in `perf_lab/README.md` -- oracle and twin gates first,
then one 300k decision bench.
