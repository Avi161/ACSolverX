# AC19 1M leftovers at a 5,000,000-node budget — two notebooks, two machines

One notebook per machine. The greedy arm's 88 rows run combined in a single
notebook (this **replaced the four `c{1..4}of4` stride-shard notebooks**; MAIN
absorbs any rows those shards already finished, from their Drive dirs, so
nothing paid for is re-run), and the s20_mk2 arm's 14 run as the other.

| notebook | arm | rows |
|---|---|---:|
| [`ac19_leftovers_5m_greedy.ipynb`](ac19_leftovers_5m_greedy.ipynb) | `greedy` — total length | 88 |
| [`ac19_leftovers_5m_s20_mk2.ipynb`](ac19_leftovers_5m_s20_mk2.ipynb) | `s20_mk2` — `L + 20·S + 2·MK` | 14 |

Cell contract: **CONFIG → SETUP → SMOKE → MAIN.** SMOKE always runs (2 rows,
2,000 nodes, ~a minute, into a separate `_smoke` dir) and **gates** the long
job: if anything in it raises, Run All stops and MAIN never starts. `ENGINE`
and `HIGH_SPEEDUP` live in SETUP, which refuses to proceed without the
packed-arena engine — `ENGINE=hcompact` is required for `HIGH_SPEEDUP`, and the
Python solvers in `experiments/search/` are the test oracle and fallback, not
the fast path.

Runs on **Colab or a plain GCE VM's Jupyter**: SETUP clones the branch wherever
no checkout is found, mounts Drive only where Drive exists, and MAIN says so
when there is no mirror (copy the jsonl off the VM yourself in that case).

## The machine

Any CPU machine type. One search runs at a time — it is a memory event
(~25–30 GB touched for a full-budget row at cap 48), not a compute one, so core
count buys nothing here; **the requirement is ≥ 32 GB of RAM**, whatever shape
provides it. Under that, a full-budget row will OOM hours in — SETUP prints a
loud warning when free RAM is below ~28 GB. `N_WORKERS="auto"` sizes by free
RAM via the engine's own arena formula and resolves 1 at this budget on any
box; a machine with much more RAM simply fits more workers automatically.

## The row lists

```
results/heuristic_search/ac19_autmin_screen/unsolved_1m_baseline.csv   88 rows
results/heuristic_search/ac19_autmin_screen/unsolved_1m_s20_mk2.csv    14 rows
```

`solved == false` read off the 1M jsonl; the 14 are a strict subset of the 88.
`tests/test_leftovers_5m.py` re-derives both, and SETUP re-derives its own list
again before anything searches.

## Expect days, and expect to resume

At ~500–800 nodes/s single-worker, a full-budget row takes ~2–3 h: the greedy
list is on the order of a week on one machine, s20_mk2 about a day and a half.
The jsonl appends locally and mirrors whole-file to Drive when mounted;
`RESUME` skips every finished row, a wiped machine reseeds from the mirror, and
re-running the notebook never repeats finished work.

The 1M floor self-check carries over: at cap 48 a row solving at or below
1,000,000 nodes is impossible for these lists and the report says so loudly; at
any other cap it is labelled legitimate instead — a different corridor is a
different search.

Regenerate the notebooks after editing the template:

```bash
PYTHONPATH=. python3 -m experiments.search.make_leftover_5m_notebooks
```
