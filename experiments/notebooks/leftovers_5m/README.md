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
