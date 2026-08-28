# AC19 1M leftovers at a 5,000,000-node budget

Five Colab notebooks that take what survived the 1,000,000-node pass
([`../../../results/heuristic_search/leftovers_1m/RESULTS.md`](../../../results/heuristic_search/leftovers_1m/RESULTS.md))
and give it 5,000,000. The greedy arm's 88 rows are **stride-chunked** across
four notebooks — `CHUNKS=4, CHUNK_INDEX=k` takes rows `[k-1::4]`, the u124
campaign's split, interleaved so difficulty spreads evenly — and the s20_mk2
arm's 14 run as one.

| notebook | arm | rows |
|---|---|---:|
| [`ac19_leftovers_5m_greedy_c1of4.ipynb`](ac19_leftovers_5m_greedy_c1of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c2of4.ipynb`](ac19_leftovers_5m_greedy_c2of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c3of4.ipynb`](ac19_leftovers_5m_greedy_c3of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_greedy_c4of4.ipynb`](ac19_leftovers_5m_greedy_c4of4.ipynb) | `greedy` | 22 |
| [`ac19_leftovers_5m_s20_mk2.ipynb`](ac19_leftovers_5m_s20_mk2.ipynb) | `s20_mk2` | 14 |

Runtime: **CPU, High-RAM**, one session per notebook, separate Drive dirs (each
CONFIG carries its own). All ship `SMOKE_RUN = True`; read the smoke table, set
it `False`, Run All.

## The row lists

```
results/heuristic_search/ac19_autmin_screen/unsolved_1m_baseline.csv   88 rows
results/heuristic_search/ac19_autmin_screen/unsolved_1m_s20_mk2.csv    14 rows
                                            + matching .txt name lists
```

`solved == false` read off the 1M jsonl, orbit membership joined back from the
100k lists so the schema stays the one every wave has used. The 14 are a strict
subset of the 88. `tests/test_leftovers_5m.py` re-derives both from the jsonl,
and each notebook's SETUP re-derives its own list again before searching
anything.

## Memory at 5M, and why one worker per session

The engine's arena formula reserves **~35 GB per search** at this budget, and the
hard tail discovers ~100 states per pop (measured: a 6,053,728-state grow by
60,000 pops on `ac19_7284`), so a full-budget row can genuinely touch ~40 GB.
`N_WORKERS="auto"` resolves **1** on a 51 GB runtime — correct, not a bug. The
parallelism is the four sessions, which is the whole reason the greedy arm is
chunked.

The dedup **is already the memory trick**: FNV-hashed nibble-packed rows in an
open-addressing int32 table at ~79 B/state (`experiments/search/greedy_compact.py`)
— the same machinery the u124 CoV-mining campaign ran on. The remaining lever
would be fingerprint-only visited sets, which make the search probabilistic (a
hash collision silently skips a state, possibly a solution); nothing in this
screen's chain of results is probabilistic, so it is not done here.

## Expect days, and expect to resume

At ~500–800 nodes/s single-worker, a row that exhausts the budget takes ~2–3 h:
roughly two Colab-days per greedy chunk and one and a half for the s20_mk2 list,
less whatever solves early. Colab will disconnect first — reopen, Run All, and
`RESUME` continues from the Drive-mirrored jsonl; a wiped `/content` reseeds from
Drive. Nothing already recorded is recomputed.

## The self-check moves to 1,000,000

Same engine, same cap, same config, so a search at budget *B* is the first *B*
pops of any longer one: a row that failed at 1,000,000 cannot come back solved at
or below 1,000,000 now. The REPORT cell flags any such row loudly — it means the
wrong search ran. The REPORT cell also prints the merged view across whatever
chunks have rows so far; the merged table is the experiment's answer, a single
chunk's is progress.

Regenerate the notebooks after editing the template:

```bash
PYTHONPATH=. python3 -m experiments.search.make_leftover_5m_notebooks
```
