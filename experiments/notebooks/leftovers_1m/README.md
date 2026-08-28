# AC19 100k leftovers at a 1,000,000-node budget

Two Colab notebooks, one per arm, that take what the AC19 aut-min screen still
had unsolved after a 100,000-node budget and give it 1,000,000 instead.

| notebook | arm | rows | question |
|---|---|---:|---|
| [`ac19_leftovers_1m_greedy.ipynb`](ac19_leftovers_1m_greedy.ipynb) | `greedy` — total length | **222** | how many of the greedy arm's 100k leftovers does 1M solve? |
| [`ac19_leftovers_1m_s20_mk2.ipynb`](ac19_leftovers_1m_s20_mk2.ipynb) | `s20_mk2` — `L + 20·S + 2·MK` | **39** | how many of the heuristic's 100k leftovers does 1M solve? |

Runtime: **CPU, High-RAM**. Nothing here touches a GPU. Open a notebook,
Runtime → Run All. Both ship with `SMOKE_RUN = True`; read the smoke table, then
set it `False`. The two are independent and are meant to run as two parallel
Colab sessions with separate Drive directories — which is how every earlier wave
of this screen was run.

## The row lists

Shipped beside the notebooks, presentations inline, no join needed:

```
results/heuristic_search/ac19_autmin_screen/unsolved_100k_baseline.csv   222 rows
results/heuristic_search/ac19_autmin_screen/unsolved_100k_s20_mk2.csv     39 rows
                                            + matching .txt name lists
```

Schema (the one `run_ac19_hard_residual_100k.load_hard_rows` already reads):

```
name,r1,r2,n_members,members,nodes_explored,min_relator_length
ac19_7284,YYXXXyXX,YXyxYXXXyxx,3,8769 16286 101025,100000,17
```

`r1`/`r2` are the relators (upper = generator, lower = inverse);
`min_relator_length` is the shortest relator the 100k search reached, i.e. how
close it got. Rows are **`Aut(F₂)`-minimal representatives** — difficulty is not
orbit-invariant, so a failure is a failure *for this representative*.

Both CSVs are `solved == false` read straight off the 100k jsonl, which ships too:

```
results/heuristic_search/hsearch_ac19_hard100k/
  ac19_unsolved10k_baseline_b100000_mrl48.jsonl   831 rows, 609 solved, 222 not
  ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl    259 rows, 220 solved,  39 not
```

`tests/test_leftovers_1m.py` **re-derives both CSVs from that jsonl** rather than
trusting them, and checks the solved counts against `RESULTS.md`. The 39 are a
strict subset of the 222: `s20_mk2` recovers 182 of length's failures and loses
none the other way, so all 39 are rows both orderings fail.

Full provenance, including the 1k → 10k → 100k chain:
[`../../../results/heuristic_search/ac19_autmin_screen/UNSOLVED_AFTER_100k.md`](../../../results/heuristic_search/ac19_autmin_screen/UNSOLVED_AFTER_100k.md).

### 221 or 222?

Both, and they do not conflict. `RESULTS.md` scores over the **70,723 orbits both
arms searched at 10k** (`baseline` 71,556, `s20_mk2` 71,582 — the sets differ).
Exactly one greedy failure, `ac19_33435`, sits outside that intersection because
`s20_mk2` never searched it. So **222** = orbits the greedy arm actually failed,
**221** = the common denominator. The notebooks ship all 222; set
`COMMON_DENOMINATOR = True` to drop that one row and quote 221. Either is fine as
long as it says which.

## What comes out

`results/heuristic_search/leftovers_1m/`, mirrored to Drive as the run goes:

```
leftovers_1m_<arm>_b1000000_mrl48.jsonl   one row per presentation
solved_at_1m_<arm>.txt                    what the extra budget bought
still_unsolved_1m_<arm>.txt               what survives even 1,000,000 nodes
```

The jsonl is appended locally and mirrored **whole-file** to Drive, never appended
to a mount — appending to a mount is what silently truncates a jsonl when a Colab
session drops. `RESUME` reads it back, so Restart → Run All continues rather than
restarting.

The REPORT cell also prints the **anytime curve** at 250k and 500k. That costs
nothing: `solved_at` is a prefix property — a search at budget *B* is exactly the
first *B* pops of any longer search — so one run at 1M already answers every
budget below it. For the same reason the 100,000 column is a **self-check, not a
result**: every row here failed at 100,000 in the run that built the list, so a
row coming back solved at or below 100,000 nodes means the search being run is
not that search, and the report says so loudly.

## Which search runs

Both arms run **`hcompact`** — the packed-arena engine (nibble arena, int32 binary
heap, open-addressing table, all in numba) that the 100k wave itself used, ported
onto this branch with its chain (`greedy_compact`, `hlab`, `hfast`, `hsolve`). The
heap ordering is the only thing that differs:

| arm | config | priority |
|---|---|---|
| `greedy` | `LENGTH_ONLY` | `L` |
| `s20_mk2` | `S20_MK2` | `L + 20·S + 2·MK` |

`S20_MK2` is `{"L": 1.0, "S": 20.0, "MK": 2.0}`. The former `RECOMMENDED` vector
(`L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb`) was withdrawn as overfit and is
refused by name by `run_leftovers_1m.resolve_arm`.

**Why not the Python solvers.** `heuristics.greedy_search_h` keeps `visited`
(state → parent), `move_in` and `new_seen` keyed by tuples of Python strings so it
can rebuild certificates; measured on `ac19_1007` at cap 48 it holds **1.64 GB by
12,288 popped nodes**, past 100 GB at 1M. A memory-lean rewrite
(`LeanHeuristicSolver`) got that to 46 GB and 290 nodes/s — still only one worker
on a 51 GB runtime. `hcompact` holds ~76–84 B/state against those solvers' ~390.

They both remain in the tree, and they are still exercised: they are the fallback
where the engine is absent, and they are the **oracle** the tests check the engine
against, field for field, on real rows from these lists. Swapping an engine under
an experiment that already has published numbers is only legitimate if it is the
same search.

**Node counts are comparable with the 100k run**, because this is the engine that
run used. An earlier revision of these notebooks used the Python solvers and
warned that `nodes_explored` was not interchangeable across engines; that caveat
no longer applies.

## Cost, and why the runtime must be High-RAM

Measured on `ac19_7284` from this row list, budget 60,000, cap 48:

| engine | rate | RAM at 1M | workers on 51 GB |
|---|---:|---:|---:|
| `LeanHeuristicSolver` (Python) | 290 n/s | 46 GB | 1 |
| **`hcompact`** | **802 n/s** | **7.6 GB** | **6** |

Memory grows with what the search **discovers**, not what it pops — a best-first
search queues far more than it expands.

`N_WORKERS = "auto"` sizes the pool by **free RAM, not core count**, using the
engine's *own* arena reservation formula — so the number the pool is sized by and
the number the search allocates are one quantity rather than two that can drift.
It also scales with the budget, so a 2,000-node smoke does not reserve the 1M
footprint. Workers run `maxtasksperchild=1`, so one row's peak cannot become the
next row's floor.

SETUP prints what it resolved. You want to see:

```
  engine  : hcompact (packed arena, numba)
  workers : 6 (~7.6 GB/search reserved)
```

`python fallback` there means the clone did not pick up the engine files — re-run
SETUP rather than letting it run ~10× slower.

**Expect to resume.** Colab will disconnect before 222 rows finish. That is
planned for: reopen, Run All, and nothing already recorded is recomputed; a wiped
`/content` reseeds from the Drive mirror.

## Tests

`tests/test_leftovers_1m.py`. **Nothing in the suite runs a 1M search** — the
budgets are small enough that the whole file is under a minute.

What it holds:

- **The row lists are derived, not trusted** — both CSVs re-read from the 100k
  jsonl, the solved counts checked against `RESULTS.md`, 39 ⊂ 222, and the
  221/222 denominator.
- **The notebooks are what the generator writes**, `BRANCH` names the branch the
  code is actually on, and each notebook is **executed end-to-end** on its smoke
  path — the only thing that catches a CONFIG name the RUN cell does not define.
- **The engine is the same search.** `hcompact` agrees field-for-field with the
  Python solver on real rows from these lists, the greedy arm still reproduces
  the length baseline exactly, and the arms genuinely *call* the engine rather
  than silently falling back — a quiet fallback would cost ~10× and look fine.
- **The run survives.** Progress from pool workers reaches the parent, a wiped
  local jsonl reseeds from the Drive mirror, and a local jsonl ahead of the
  mirror is not clobbered.
- **The docs match the code.** This file must name the engine that is actually
  importable and must not claim it is absent while the code calls it, and its
  cost table must quote `est_gb` and the worker count `resolve_workers` returns.

A count of checks is deliberately not stated here: it is a number no test can
verify, and it went stale three times while the code around it changed. The
current count is in the PR description, which is a snapshot; this file, which
lives with the code, only claims things the suite itself enforces.

Regenerate the notebooks after editing the template:

```bash
PYTHONPATH=. python3 -m experiments.search.make_leftover_notebooks
```
