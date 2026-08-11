# The four CoV top-3 arms at budget 100,000, all 640 ms640 presentations

Zero search nodes — a regrouping of four frozen result files in this directory, from [`cov_top3_arm_compare.py`](../../../../experiments/stable_ac/cov/run/cov_top3_arm_compare.py). The `_s` arms ran on Colab on 2026-08-11; `abel` and `len` shipped on 08-10. All four cover the same 640 presentations at `k = 3`, `max_relator_length 24`, cyclic reduction on, and all four embed the **same** baseline column (asserted, not assumed).

Three accountings are kept apart because they point in opposite directions. **rank1** is the first pick alone; **deployed** is cumulative nodes up to and including the first *solving* rank — what a deployment stopping on success would spend; **as-run** is all three ranks, which is what these runs actually burned. The recorded runs do **not** early-stop: all three candidates execute even after rank 1 solves, so `stop3` in the filenames does not mean early-stop in the data.

| arm | rank 1 | top 3 | rank-1 nodes | deployed | as-run | median path | unsolved |
|---|---:|---:|---:|---:|---:|---:|---|
| `abel` | 640 / 640 | **640 / 640** | 458,688 | 458,688 | 2,541,652 | 7 | — |
| `abel_len_rd_s` | 640 / 640 | **640 / 640** | 420,426 | 420,426 | 8,447,944 | 7 | — |
| `len` | 633 / 640 | **638 / 640** | 1,306,940 | 1,721,736 | 3,143,988 | 7 | 634, 635 |
| `len_rd_s` | 633 / 640 | **639 / 640** | 1,325,916 | 1,648,391 | 3,710,106 | 7 | 634 |
| *baseline, untransformed* | — | 640 / 640 | — | 3,176,297 | — | 9 | — |

**On the abel arm `S` buys no solves at all, and that was predicted.** Shipped `abel` already solves 640/640 at rank 1 at this budget, so there is no solve headroom for any abel-first arm to take — `RESULTS.md` said so before this run. What `S` does move is cost: the rank-1 bill falls **458,688 → 420,426 nodes (-8.3%)**, and it gets there by changing the rank-1 pick on **357 of 640** presentations. Over half the picks change and the solve set does not move — the same 640, not merely the same count.

**On the length arm `S` buys exactly one row.** Rank 1 is unchanged at 633/640, but top-3 goes **638 → 639**, recovering presentation 635. Only 634 remains unsolved on that arm. The rank-1 bill goes the wrong way (+1.5%) while deployed improves (-4.3%).

**Priced as it was actually run, `abel_len_rd_s` is much the dearest arm**: 8,447,944 nodes against `abel`'s 2,541,652 (+232.4%), 3.6 h of wall clock against 1.2 h. This is the budget-1,000 finding at scale: `S` fills slots 2 and 3 with near-copies of the rank-1 pick, and on the rows where rank 1 already solved, those near-copies still run and still cost. The arm is cheaper only if the deployment actually stops on success, and these runs did not.

**No escapes.** The untransformed baseline solves 640/640 at its own 1,000,000-node budget, so nothing here is a solvability win over the baseline; the win is cost and path length. Note the budgets are not matched — the baseline had 1,000,000 per presentation, each CoV candidate 100,000 — so the honest comparison is nodes actually spent, which is the column above: `abel_len_rd_s` reaches the same 640/640 for 420,426 deployed nodes against the baseline's 3,176,297, and with a shorter median path (7 vs 9).

Reproduce: `.venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_arm_compare`
