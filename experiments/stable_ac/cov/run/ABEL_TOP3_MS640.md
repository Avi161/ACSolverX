# Abelian-mass top-3 CoV on ms640 at budget 100,000

The subset-60 result scaled to the whole dataset. For each of the 640 ms640 presentations, take the top 3 change-of-variables candidates by abelianized magnitude, search them in rank order at budget 100,000 each, and **stop at the first solve** — so a presentation costs at most 3 × 100,000 = 300,000 nodes.

```text
abel(r1, r2) = |σ_x(r1)| + |σ_y(r1)| + |σ_x(r2)| + |σ_y(r2)|
```

Two stages, because the selection must be frozen before any search runs — otherwise two parallel sessions could disagree about what they are searching.

| stage | file | cost |
|---|---|---|
| A — rank and freeze the top 3 | [`abel_top3_manifest.py`](abel_top3_manifest.py) → `results/stable_ac/cov/abel_top3/manifest_ms640_top3.jsonl` | **0 nodes**, ~2 s, committed |
| B — search the frozen starts | [`abel_top3_run.py`](abel_top3_run.py) | the experiment |

## Running it

Two Colab sessions, one notebook each. They take presentation `j` iff `j % 2 == shard - 1`, write separate jsonls, and never touch each other's file. Nothing differs between the two notebooks but `CHUNK_INDEX`.

- [`experiments/notebooks/stable_ac/abel_top3_ms640_c1of2.ipynb`](../../../notebooks/stable_ac/abel_top3_ms640_c1of2.ipynb)
- [`experiments/notebooks/stable_ac/abel_top3_ms640_c2of2.ipynb`](../../../notebooks/stable_ac/abel_top3_ms640_c2of2.ipynb)

CONFIG / SETUP / RUN, plus a fourth MERGE cell that only runs once **both** shards have finished and mirrored to Drive. Restart → Run All continues a run; hotfixes mid-run must be pushed as `.py` files, since a pushed `.ipynb` never reaches an already-open Colab notebook. `HIGH_SPEEDUP` is on: the compact solver has the same pop order and the same stats, and a solved fast search is re-solved by the normal solver to recover its path, so every written row is identical to a slow-mode row and the files resume across the two modes.

Roughly 1–3 core-hours per shard — dominated entirely by the presentations where no pick solves, which burn the full 3 × 100,000. A search holds ~1.4 GB at this budget (more at a raised cap), so one search per session is comfortable on any Colab runtime.

## What it is compared against

**Plain greedy at 3 × 100,000 = 300,000 nodes**, the node-matched control, and it costs zero new search: a greedy search at budget `B` is exactly the first `B` pops of any longer search, so the control is the frozen `results/greedy_baseline/greedy_1000000_640_*.jsonl` read with `solved and nodes_explored <= 300000`. `summarize()` does that read; never re-run it.

| plain greedy, by truncation | solved | unsolved |
|---|---:|---|
| 100,000 (one search) | 634/640 | 634, 635, 636, 637, 638, 639 |
| 200,000 | 634/640 | the same six |
| **300,000 (node-matched)** | **638/640** | **634, 635** |
| 1,000,000 | 640/640 | — |

## Read the cost, not the solve count — the dataset is nearly saturated

Plain greedy already solves 634 of 640 at a single 100,000-node search, so there are at most six rows in which either arm can move, and the node-matched control takes four of them. This is the repo's own [control-with-no-dynamic-range](../../../lessons/control-with-no-dynamic-range.md) and [gap-metric-saturates-when-the-treatment-wins](../../../lessons/gap-metric-saturates-when-the-treatment-wins.md) shape: a solve-count headline on ms640 at this budget is a metric with almost no room left in it.

Three of the six are already settled by the frozen 10,000-node subset-60 sweep, at zero cost:

| pres | abel top-3 at 10,000 | plain greedy at 300,000 |
|---|---|---|
| 634 | **solves at rank 1 in 7,840 nodes** | unsolved |
| 635 | **solves at rank 1 in 7,875 nodes** | unsolved |
| 636–639 | no candidate in the whole CoV family solves | 636–639 solved |

So the two rows the node-matched control cannot reach are exactly the two this rule already takes, for under 8,000 nodes each — a ~38× cost win on the hardest rows in the set — and 636–639 are the only genuinely open headline rows in the run. Expect the two arms to swap rows rather than separate on the count. **The dimension with real dynamic range here is cost**, which is why every row carries `cum_nodes` (the presentation's cumulative nodes to its first solve) and why `summarize()` prints its median, mean and max against the baseline's own per-row nodes.

## Gates

- **Selection.** Stage A builds its candidate families from `data/ms640_solved.txt` and ranks them itself; the validated budget-1,000 result ranked rows read out of a frozen sweep jsonl. `tests/stable_ac/test_abel_top3.py` pins that the two paths agree on all 60 subset-60 selections *and* on the full enumerated family, so the ms640 run measures the same rule the subset-60 deck reports. The key and the tie-break are imported from `abel_topk_cov_b1k`, never re-implemented.
- **Cap.** Each pick is searched under its own `max(24, longest + 16)` cap, not the base 24 — a CoV lengthens relators, and a comparison at a different cap is not a comparison.
- **Budget-agnostic.** ~180 of this run's searches are subset-60 rows whose whole families the frozen 10,000-node sweep already searched. `verify_overlap()` requires every one of them to reproduce it exactly: a start that solved at 10,000 must solve here with the same `nodes_explored` and `path_length`, and a start solving here in ≤ 10,000 must have solved there. `summarize()` runs it and prints the verdict.
- **Denominator.** Every count is scored over the presentations the file actually searched, never over all 640 — a partial run scored against a complete control reads as a collapse that is really unfinished work.
- **Merge.** `merge_chunks()` refuses while a chunk file is absent or any presentation is unfinished: the merged file claims the canonical name every later unchunked run resumes from.

## Afterwards

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov/abel_top3
```

A solve from a transformed start proves the original is **stably** AC-trivial, never AC-trivial, and `path_length` from a transformed start is not a certificate for the original.
