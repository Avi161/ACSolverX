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

Nothing about the search is re-implemented. The greedy arm calls
`greedy_baseline.greedy_search(..., high_speedup=True)` — the shipped memory-lean
solver that exists for exactly this budget.

The heuristic arm **cannot** call `heuristics.greedy_search_h`. That solver keeps
`visited` (state → parent), `move_in` and `new_seen`, all keyed by tuples of
Python strings, so it can rebuild certificates; measured on `ac19_1007` from this
screen at cap 48 it holds **1.64 GB by 12,288 popped nodes**, which extrapolates
past 100 GB at 1M. That is not a slow run, it is an OOM. So
`run_leftovers_1m.LeanHeuristicSolver` subclasses the same lean solver the greedy
arm uses and swaps only the heap's priority expression — the numba expansion, the
reduction, the canonicalisation, the cap, the visited set and the
`(priority, depth, key)` push shape are all inherited, exactly as
`heuristics.HeuristicSolver` inherits from `GreedyBaselineSolver`. The tests pin
it against `greedy_search_h` **pop for pop** on synthetic and real rows, and pin
that its baseline config reproduces the greedy arm exactly.

`S20_MK2` is `{"L": 1.0, "S": 20.0, "MK": 2.0}`. The former `RECOMMENDED` vector
(`L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb`) was withdrawn as overfit and is
refused by name by `run_leftovers_1m.resolve_arm`.

**Engine note.** The 100k pass ran on the research branches' `hcompact` engine,
which is not on this branch. These are the `experiments/search/` solvers that ship
with main and that `tests/test_greedy_heuristic.py` pins. They search the same
space, so `solved` is comparable across the two runs — but node counts are not
interchangeable between engines, so read `nodes_explored` only within this run.

## Cost, and why the runtime must be High-RAM

Measured single-core at cap 48 on rows from these lists, extrapolated linearly to
1,000,000 nodes:

| arm | row | measured | rate | → 1M nodes |
|---|---|---|---:|---|
| `greedy` | `ac19_420` | 2.71 GB at 200,000 pops | ~1050 n/s | **~16 GB**, ~16 min/row |
| `s20_mk2` | `ac19_7284` | 1.17 GB at 25,600 pops | ~330 n/s | **~46 GB**, ~50 min/row |

Memory grows with what the search **discovers**, not what it pops — a best-first
search queues far more than it expands. The arms differ because the orderings go
different places: `s20_mk2` prefers thicker blocks, so it queues longer relators
and a wider frontier.

`N_WORKERS = "auto"` therefore sizes the pool by **free RAM, not core count**: on
a 51 GB high-RAM runtime that is **3 workers for `greedy`, 1 for `s20_mk2`**. A
standard (non-high-RAM) runtime has ~13 GB and cannot run the `s20_mk2` arm at 1M
at all — SETUP prints the worker count it resolved, so check that line before
walking away. Oversubscribing does not make a slow run, it makes an OOM that loses
the session. Workers also run with `maxtasksperchild=1`, so one row's peak cannot
become the next row's floor.

`s20_mk2` reaching 1M at all depends on one detail: a single-segment config scores
to a **bare float** rather than `make_priority`'s `(segment_index, score)` tuple.
That tuple is allocated once per discovered state and lives in the heap until the
state is popped; dropping it took this arm from ~63 GB projected to ~46 GB and
from ~200 to ~330 nodes/s. It is order-identical — every state is in segment 0, so
comparing `(0, a)` with `(0, b)` is comparing `a` with `b` — and the tests pin that
against `greedy_search_h`.

**Expect to resume.** 39 rows is a small job; 222 at 2 workers is on the order of
a day, and Colab will disconnect first. That is planned for — reopen, Run All,
and nothing is recomputed.

## Tests

`tests/test_leftovers_1m.py` (58 checks): notebook shape, that `BRANCH` names the
branch the code is actually on, that the committed notebooks are what the
generator writes, the CSVs re-derived from the 100k jsonl, the 39 ⊂ 222 relation,
the 221/222 denominator, the RAM-bound worker maths, the lean-solver equivalence,
and an end-to-end smoke (run → resume → report) at a budget that measures nothing.
Nothing in the suite runs a 1M search.

Regenerate the notebooks after editing the template:

```bash
PYTHONPATH=. python3 -m experiments.search.make_leftover_notebooks
```
