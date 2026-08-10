# Two CoV top-3 rules on all 640 ms640 presentations, at budget 100,000

A full census of what a one-shot change of variables buys over plain greedy, on every presentation in the dataset rather than on the 60-row subset. For each presentation, take the top 3 CoV candidates under a search-free ranking rule and search **all three** at budget 100,000 each, in rank order, including the ranks below one that already solved. Every presentation therefore costs exactly 3 searches (worst case 300,000 nodes).

Running the ranks below a solve is the design, not waste. It is what makes the per-rank means comparable: every rank is then measured on the same 640 presentations, so "does rank 1 solve more often and more cheaply than rank 3" is a question the file can answer — and that question is the only direct evidence that the ranking rule orders the CoV family by quality at all. Stop at the first solve and ranks 2–3 exist only where rank 1 failed, i.e. on a harder, self-selected subset; their means would then be worse than rank 1's *by construction*, and the comparison would be circular. Nothing is lost by running them, because the ranks run in order and every row carries its running `cum_nodes`, so the early-exit cost is recovered exactly, per presentation, as `first_solve_nodes`.

That gives every presentation **two costs, and they are not interchangeable**:

| field | what it is | use it for |
|---|---|---|
| `first_solve_nodes` | nodes over ranks 1..r, r = the first rank that solved | the head-to-head against plain greedy — this is what the rule costs *deployed as a solver* |
| `cum_nodes` | nodes over all 3 ranks | what the census itself spent |

`summarize()` uses `first_solve_nodes` for the paired comparison (plain greedy's number is one search that stopped when it solved, so charging the CoV arm for ranks a user would never run would compare a census against a solver) and reports the census total separately.

Two rules, one Colab session each, both over all 640:

| rule | key | file stem |
|---|---|---|
| `abel` | `abel(r1,r2) = \|σx(r1)\|+\|σy(r1)\|+\|σx(r2)\|+\|σy(r2)\|` | `abeltop3_100000_640_…` |
| `len` | `len(r1) + len(r2)` of the **transformed** pair (the shortest CoV) | `lentop3_100000_640_…` |

Both keys and the `_ident` tie-break are imported from `abel_topk_cov_b1k` (`KEYS["abel"]`, `KEYS["len_only"]`), the runner the subset-60 numbers came from — one key, one implementation. The rules are not two names for one thing: they pick the same top-3 **set** on only 5 of the 640 presentations.

Two stages, because the selection must be frozen before any search runs.

| stage | file | cost |
|---|---|---|
| A — rank and freeze the top 3, per rule | [`cov_top3_manifest.py`](cov_top3_manifest.py) → `results/stable_ac/cov/cov_top3/manifest_ms640_{rule}_top3.jsonl` | **0 nodes**, ~3 s, committed |
| B — search the frozen starts | [`cov_top3_run.py`](cov_top3_run.py) | the experiment |

## Running it

Two Colab sessions, one notebook each. `RULE` is the only knob that differs.

- [`experiments/notebooks/stable_ac/cov_top3_ms640_abel.ipynb`](../../../notebooks/stable_ac/cov_top3_ms640_abel.ipynb)
- [`experiments/notebooks/stable_ac/cov_top3_ms640_len.ipynb`](../../../notebooks/stable_ac/cov_top3_ms640_len.ipynb)

CONFIG / SETUP / RUN, plus a fourth optional cell: `MERGE` (only if you split one arm across more machines with `CHUNKS > 1` — stride sharding, `j % N`, never blocks, because ms640 is difficulty-ordered) and the **head-to-head**, which needs the other arm's file and so runs once both have finished and mirrored to Drive. Restart → Run All continues a run; hotfixes mid-run must be pushed as `.py` files, since a pushed `.ipynb` never reaches an already-open Colab notebook. `HIGH_SPEEDUP` is on: the compact solver has the same pop order and the same stats, and a solved fast search is re-solved by the normal solver to recover its path, so every written row is identical to a slow-mode row and the files resume across the two modes.

Cost is dominated by the ranks that never solve and burn the full 100,000 — and since every rank now runs, that includes the non-solving ranks of presentations an earlier rank already solved. Budget several core-hours per arm rather than one, and note that the census cost is *not* the number to quote as the method's price; `first_solve_nodes` is. A search holds ~1.4 GB at this budget, so one search per session is comfortable on any Colab runtime.

A restart is safe and, more to the point, *complete*: a presentation counts as finished only when all 3 ranks have a row. A solved rank 1 does not finish it — otherwise Restart → Run All would skip exactly the presentations rank 1 solved, the file would end up looking complete, and ranks 2–3 would have been measured only on the complement of the easy rows. `tests/stable_ac/test_cov_top3.py::test_restart_fills_in_the_ranks_after_a_solve` pins this by truncating a finished file to its rank-1 rows and requiring the resume to fill the rest in.

**The rule↔manifest binding is enforced, not documented.** The manifest path is derived from the rule (never passed beside it), every manifest row carries its `rule`, the loader refuses a manifest ranked by a different rule, and the rule is the first field of the results filename — so the two arms can never resume into each other, and no run can search one rule's picks under the other's name.

## What lands in the jsonl

One row per **search** (not per presentation), keyed `(pres_id, rank)`, carrying:

- the search — `solved`, `nodes_explored`, `path_length`, `path_moves` (the Definition 2.1 tuples `verify_results` replays), `min_relator`/`max_relator` and their lengths, `time_seconds`;
- the pick — `rule`, `rank`, `k`, `n_cand`, `abel`, `z_word`, `iso_gen`, `iso_index`, `n_subs`, `max_relator_length_cap`, `r1_orig`/`r2_orig`, `start_total_length_orig`/`_cov`, `family_tag`, `git_commit`;
- the presentation's running `cum_nodes` — every rank it has run so far. Because the ranks are written in order, the row of the *first solving* rank carries that presentation's `first_solve_nodes`, which is why the deployed cost survives running the whole census;
- **the plain-greedy reference for the same presentation** — `base_solved`, `base_nodes_explored`, `base_path_length`, read once from the frozen 1,000,000-node baseline. The nodes/path comparison is therefore answerable from this one file, with no join.

## What it is compared against

**Plain greedy on the untransformed presentation**, and it costs zero new search: a greedy search at budget `B` is exactly the first `B` pops of any longer search, so every control below is a read of the frozen `results/greedy_baseline/greedy_1000000_640_*.jsonl`. `summarize()` does those reads; never re-run them.

| plain greedy, by truncation | solved | unsolved |
|---|---:|---|
| 100,000 (one search) | 634/640 | 634, 635, 636, 637, 638, 639 |
| 200,000 | 634/640 | the same six |
| **300,000 (node-matched to 3 × 100,000)** | **638/640** | **634, 635** |
| 1,000,000 | 640/640 | — |

## Read the cost, not the solve count

Plain greedy already solves 634 of 640 at a single 100,000-node search, so there are at most six rows in which either arm can move on the count, and the node-matched control takes four of them. That is the repo's own [control-with-no-dynamic-range](../../../lessons/control-with-no-dynamic-range.md) and [gap-metric-saturates-when-the-treatment-wins](../../../lessons/gap-metric-saturates-when-the-treatment-wins.md) shape: a solve-count headline on ms640 at this budget is a metric with almost no room left in it.

Three of the six are already settled by the frozen 10,000-node subset-60 sweep, at zero cost:

| pres | abel top-3 at 10,000 | plain greedy at 300,000 |
|---|---|---|
| 634 | **solves at rank 1 in 7,840 nodes** | unsolved |
| 635 | **solves at rank 1 in 7,875 nodes** | unsolved |
| 636–639 | no candidate in the whole CoV family solves | 636–639 solved |

So the two rows the node-matched control cannot reach are exactly the two the abel rule already takes, for under 8,000 nodes each, and 636–639 are the only genuinely open headline rows. **The dimensions with real dynamic range are cost and path length**, which is what `summarize()` leads on: median/mean/max `first_solve_nodes` and `path_length` against plain greedy's own, paired over the presentations *both* arms solved, with a win/tie/loss count on each. A 20-presentation dry run at budget 1,000 (stride-sampled, `CHUNKS=32`) already shows the shape — abel mean 66 nodes and mean path 16.9 against plain greedy's 547 and 24.9 on the same rows.

Beside that, and only available because every rank runs, is the **per-rank block**: solve count, median/mean nodes and median/mean path length for rank 1, rank 2 and rank 3 *over the same presentations*. That is the internal question — is the rule's ordering real? — and it also prices the top-3 policy itself, by reporting how many presentations rank 1 solves alone against how many the union of all three solves.

A CoV path certifies the **transformed** pair: it proves the original is *stably* AC-trivial, and its `path_length` is not a certificate for the original. The comparison is legitimate as a cost/complexity measurement, not as two lengths of the same object.

## Gates

- **Selection.** Stage A builds its candidate families from `data/ms640_solved.txt` and ranks them itself; the validated budget-1,000 result ranked rows read out of a frozen sweep jsonl. `tests/stable_ac/test_cov_top3.py` pins that the two paths agree on all 60 subset-60 selections **for both rules** *and* on the full enumerated family.
- **Cap.** Each pick is searched under its own `max(24, longest + 16)` cap, not the base 24 — a CoV lengthens relators, and a comparison at a different cap is not a comparison.
- **Budget-agnostic.** Both arms' picks on the 60 subset-60 rows were already searched by the frozen 10,000-node sweep. `verify_overlap()` requires every one of them to reproduce it exactly: a start that solved at 10,000 must solve here with the same `nodes_explored` and `path_length`, and a start solving here in ≤ 10,000 must have solved there. `summarize()` runs it and prints the verdict.
- **Denominator.** Every count is scored over the presentations the file actually searched, never over all 640, and the paired statistics only over the presentations both arms solved. `compare_rules()` scores the two arms on their intersection, since two sessions finish at different times.
- **Merge.** `merge_chunks()` refuses while a chunk file is absent or any presentation is unfinished: the merged file claims the canonical name every later unchunked run resumes from.
- **Certificates.** `verify_results` was run against this format after the all-ranks change, on a file whose rows include ranks searched below an already-solved one (5 presentations per rule at budget 1,000 → 15 rows each, 10 of them post-solve): **30/30 verify, exit 0**. The command below is a checked instruction, not an assumed one.
- **Unfinished work is reported.** `summarize()`'s `partial` list is `n_searches < k` — a solve does **not** remove a presentation from it. Otherwise a mid-run summary would report nothing outstanding while the per-rank block below it printed over unequal sets.

## Afterwards

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov/cov_top3
```
