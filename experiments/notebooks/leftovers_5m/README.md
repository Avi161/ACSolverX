# AC19 1M leftovers at a 5,000,000-node budget — five notebooks, five machines

Four greedy stride shards plus s20_mk2, one notebook per machine. The greedy
arm's 88 rows split `CHUNKS=4, CHUNK_INDEX=k → rows[k-1::4]` — interleaved so
difficulty spreads evenly; disjoint, union = 88 — and the s20_mk2 arm's 14 run
as the fifth. (A combined single-machine greedy notebook is **not** the job.)

| notebook | arm | rows |
|---|---|---:|
| [`ac19_leftovers_5m_greedy_c1of4.ipynb`](ac19_leftovers_5m_greedy_c1of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c2of4.ipynb`](ac19_leftovers_5m_greedy_c2of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c3of4.ipynb`](ac19_leftovers_5m_greedy_c3of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c4of4.ipynb`](ac19_leftovers_5m_greedy_c4of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_s20_mk2.ipynb`](ac19_leftovers_5m_s20_mk2.ipynb) | `s20_mk2` | 14 |

Cell contract: **CONFIG → SETUP → SMOKE → MAIN.** SMOKE always runs (2 rows,
2,000 nodes, fresh each time) and **gates** the long job — any failure stops Run
All before MAIN. Runs on Colab or a plain VM's Jupyter; Drive mounts where
Drive exists, and each notebook has its own Drive dir.

## ENGINE=hcompact / HIGH_SPEEDUP, with no silent fallback

`ENGINE="hcompact"` and `HIGH_SPEEDUP=True` live in SETUP, asserted
(`ENGINE=hcompact required for HIGH_SPEEDUP`). SETUP refuses to proceed if the
packed-arena engine is missing **and** verifies the arm actually *calls*
`greedy_search_hcompact` — importable is not enough; a silent Python fallback at
5M is a ~hundreds-of-GB wrong code path, not an optimization problem. The
Python solvers stay as the test oracle only.

## The Edge Compact crash guards

The first 5M sessions died outright: the search ran in the driver process, and
`hcompact`'s `_grow` doubles its arrays with a copy — old and new coexist, and
that transient is what the OOM killer shoots, kernel and all. The fix reuses
the repo's own guards, no new engine:

- **One row, one process** (`run_ab`'s `__error__`-row pattern): if a row's
  child is OOM-killed, CPU-limit-killed, times out (`ROW_TIMEOUT_SECS`), or
  raises, the parent records an `error` row and moves to the next
  presentation. The session never dies with a row.
- **The engine's own `reserve_states` knob**: `plan_memory()` clips the
  reservation to this machine's free RAM, and the child's address space is
  capped (RLIMIT_AS) just under it — a `_grow` that would have summoned the
  OOM killer instead raises MemoryError *inside the child*, caught and
  recorded. A kill becomes a diagnosis.
- **Error rows never satisfy resume** (`_done_ok`), so a failed row is retried
  on the next invocation — same machine or a bigger one. The report dedupes
  retries and lists what errored.

`N_WORKERS="auto"` stays: it sizes by free RAM via the engine's arena formula,
whatever the machine type — nothing here assumes one. A full-budget 5M row
touches roughly 40 GB and up; SETUP prints free RAM and warns when a machine is
too small for the long job (the smoke still passes there).

## The row lists

```
results/heuristic_search/ac19_autmin_screen/unsolved_1m_baseline.csv   88 rows
results/heuristic_search/ac19_autmin_screen/unsolved_1m_s20_mk2.csv    14 rows
```

`solved == false` off the 1M jsonl; the 14 are a strict subset of the 88.
Tests re-derive both, and SETUP re-derives its own list again before anything
searches. The 1M floor self-check carries over at cap 48 and stands down, with
a note, at any other cap.

## Resume

The jsonl appends locally and mirrors whole-file to Drive when mounted;
`RESUME` skips every finished row, a wiped machine reseeds from the mirror, and
re-running a notebook never repeats finished work.

Regenerate after editing the template:

```bash
PYTHONPATH=. python3 -m experiments.search.make_leftover_5m_notebooks
```

## Running this on a rented high-RAM box instead

The five notebooks above stay as they are — they are the Colab/five-machine
path. This section is an **additional** path for one big rented CPU box
(vast.ai, Hetzner, bare metal), which is the better shape once the campaign
runs many more presentations at 5M and beyond.

The constraint Colab ran into is RAM *per row*, not CPU. `hcompact` discovers
~62 states per node popped, so at 5M nodes one row reserves **~34.7 GB on one
core**. Cloud sells 4–8 GB/core, so on a 51 GB runtime you rent 8 cores and
use 1. Buying RAM is what buys workers:

| box | workers at 5M | all 102 rows, worst case |
|---|---:|---:|
| 64 GB / 8 core | 1 | ~196 h |
| 128 GB / 16 core | 3 | ~65 h |
| 256 GB / 32 core | 7 | ~28 h |
| 512 GB / 64 core | **14** | **~14 h** |

(Worst case = every row runs the full budget. Rows that solve stop early.)
The five-shard Colab plan is ~204 machine-hours for the same work.

`experiments/search/run_remote.sh` is the whole path:

```bash
PLAN_GB=512 PLAN_CORES=64 ./experiments/search/run_remote.sh plan   # price an offer FIRST
./experiments/search/run_remote.sh plan     # what the box you rented will do
./experiments/search/run_remote.sh smoke    # 2 rows x 2,000 nodes; gates the long job
./experiments/search/run_remote.sh run      # detached -- survives an SSH drop
./experiments/search/run_remote.sh tail     # follow it
./experiments/search/run_remote.sh report   # safe mid-flight
```

`plan` runs before you pay: it prints the engine status, GB/row, the workers
`auto` will resolve, the wall-clock estimate, and whether the box is too small
for a full `reserve_states`. It refuses a box where `hcompact` is missing,
because the Python fallback at 5M is a hundreds-of-GB *wrong code path*, not a
slow one. It also fails loudly on a stale clone.

`run` uses `setsid nohup` — the connection to a rented box will drop and the
job must not care. **The instance is ephemeral: `rsync` the jsonl off the box
before you destroy it** (the `run` output prints the command). Resume then
works normally against whatever you pulled back.

Overrides: `BUDGET MRL WORKERS ARMS OUT BRANCH REPO`. Note `--mrl` is now a
real CLI flag feeding *both* the run and the report — the cap is in the jsonl
filename, so a run at one cap and a report at another silently read a file
that does not exist. That bug hit this campaign twice; one flag closes it.

### On Google Cloud specifically

The job is RAM-bound, so cost is nearly flat across high-memory SKUs — the
machine only changes how long you wait. Workers come from
`resolve_workers`; hours assume every row runs the full 5M budget.

| machine | vCPU / GB | GB per vCPU | workers | hours | ~Spot cost |
|---|---|---:|---:|---:|---:|
| `n2-highmem-32` | 32 / 256 | 8 | 7 | 28 | ~$18 |
| `n2-highmem-64` | 64 / 512 | 8 | 14 | 14 | ~$18 |
| `m1-ultramem-40` | 40 / 961 | 24 | 27 | 7 | ~$14 |
| `m1-megamem-96` | 96 / 1433 | 15 | 41 | 5 | ~$15 |

`m1-ultramem` wins on $/row-hour because 24 GB/vCPU is closest to the 34.7 GB
one row actually needs — the `highmem` families sell 8 GB/vCPU, so three
quarters of the cores you pay for sit idle. But **quota, not price, is the
real constraint**: a personal project has neither 64-vCPU N2 nor any M1 quota
by default, and M1 requests are granted less readily. Take whichever you can
get; they all cost about the same.

Use **Spot** (60–91% off) with `--instance-termination-action=STOP`, so a
preemption stops the VM with its disk intact instead of deleting it, and
`install-service` restarts the campaign on the next boot. Resume then skips
every finished row, so a preemption costs only the rows in flight.

### Dynamic worker allocation

`N_WORKERS="auto"` no longer means "decide once at startup". `RamGovernor`
re-decides before every launch, from the cores and free RAM of whatever
machine it lands on, and from what finished rows actually peaked at
(children report `VmHWM` in their record).

Why the old static number was so conservative: it assumed every row would run
the full budget and reserved `est_gb(budget)` for each. Most rows solve long
before that, and the arena is `np.empty` — address space up front, physical
pages only on first touch — so a fixed N sized off the worst case leaves most
of a big machine idle.

Two things keep it honest rather than merely optimistic:

- Memory a live row has **reserved but not yet touched** is subtracted before
  admitting the next one. A row that just started has touched almost nothing,
  so free RAM looks enormous; admitting on that number invites a crowd that
  then grows into each other.
- A prediction never drops below what a row **in flight has already
  demonstrated**, and never exceeds the worst case. Every row on these lists
  failed at 1M, so plenty will run the full budget and peak near the reserve —
  three cheap early rows must not widen the gate just before those arrive.

If it does overreach, the existing guards still apply: the row is
crash-isolated, `RLIMIT_AS` turns a `_grow` into a MemoryError inside the
child, and the row is recorded as an error and retried next run. The old
fixed Pool had no per-row isolation at all — on a wide box one OOM took every
row in flight with it — so `run_rows_dynamic` replaces both paths.

An explicit `N_WORKERS` is a **ceiling**, never a target; RAM still has the
last word.
