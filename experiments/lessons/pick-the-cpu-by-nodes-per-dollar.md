# [2026-10-12] Pick the AWS machine by measured nodes per second per dollar; ARM Graviton4 spot won [WORKS]

The rank-3 counted rerun (`experiments/stable_ac/rank3/aws_rank3_counted_box.sh`) ran on one `c7a.48xlarge` spot box (192 AMD Zen 4 cores) because that was the machine of the first run. On 12 Oct 2026 AWS reclaimed it four times: after 3 h 11 min (us-east-1d), 15 min (1d), 6 min (1a), and a `c7a.32xlarge` after 14 min (1a). Every relaunch repeats about 8 minutes of setup and checks, and the 124 tasks left at budget 10,000 need about an hour each without interruption, so the short-lived boxes finished nothing. The fallback, a `c7a.24xlarge` on demand, cannot be reclaimed but costs $4.93/h for 96 cores. The CPU had never been chosen: it was a habit.

**Measured** (`aws_rank3_bench_box.sh`, commit `64b41ff`, one `.large` spot box per CPU, a few cents each): 8 fixed tasks = 3,888 searches (presentations 0, 91, 182, 273, 364, 455, 546, 639 x the 486 words of length 6, budget 1,000, cap 24), 2 processes on 2 real cores.

| | AMD Zen 4 `c7a` | ARM Graviton4 `c8g` |
|---|---|---|
| core-seconds for the 3,888 searches | 461.9 | 534.4 |
| nodes per second per core (presentation 639: 486 unsolved searches = 486,000 nodes) | 2,320 | 2,045 |
| sha256 of nodes, path length, min total and the three cap counters | `4269bdf4eddd545a` | `4269bdf4eddd545a` |
| solver tests (`test_solvern_fast`, `test_solvern`, `test_rank3_bf`, `test_rankn_class_view`, `test_run_nocov`) | pass | pass (76, 35, 29, 9, 17) |
| rest of `tests/stable_ac` at that commit | 319 pass, 1 fail, 1 skip | 319 pass, 1 fail, 1 skip |

The one failure is the same test on both (`test_verify_results::test_main_verifies_everything_committed_including_invariance`: the control rows committed at that commit had no `path_moves`; fixed at `ef770ba`). A Graviton4 core is 12% slower and gives the same result bit for bit.

**Priced** (us-east-1, 18:30 UTC, spot = cheapest zone):

| machine | cores | $/h | nodes/s | million nodes per $ |
|---|---|---|---|---|
| `c7a.24xlarge` on demand (list price; the pricing API is denied to this IAM user) | 96 | 4.93 | 222,720 | 163 |
| `c7a.48xlarge` spot (reclaimed 3 times that day) | 192 | 3.14 | 445,440 | 511 |
| `c8g.48xlarge` spot | 192 | 1.89 | 392,640 | 747 |

ARM spot is 1.8 times faster than the on-demand box and gives 4.6 times more nodes per dollar. Not benchmarked: `c8a` (Zen 5; `c8a.24xlarge` spot $1.13/h), `c7g`, `c8i`. The ARM image is the arm64 build of the same AL2023 release (`al2023-ami-2023.12.20260817.0-kernel-6.18-arm64`, `ami-0cded71ff6ab7f608` in us-east-1); the box scripts run on it unchanged (python 3.12.13, numpy 2.1.3, numba 0.63.1 from wheels).

**The process, for any sweep:**

1. List spot prices across families and zones: `aws ec2 describe-spot-price-history --instance-types ... --product-descriptions Linux/UNIX --start-time now`. A deep discount off on demand suggests a less contended pool; that is an inference, the IAM user cannot call `GetSpotPlacementScores`.
2. Benchmark each candidate family on a `.large` spot box with `aws_rank3_bench_box.sh`: same tasks, core-seconds, sha256 of the results.
3. Require the identical digest and the same test outcomes. Then rank by cores x nodes/s per core / $ per hour.
4. Match the purchase to the task length: a task that needs an hour or more uninterrupted goes on demand; short tasks that resume from shards go on spot. A whole-host size (`48xlarge`) is reclaimed first; after a reclaim try a smaller size or another family before paying on demand.
5. Whatever CPU computed a result, compare it search for search with a run on the reference CPU (`cap_compare --must-match`) before it enters a table.

**Rule:** never inherit the instance type from the previous run. Before a sweep that costs more than a few dollars, spend a few cents on the benchmark, and take the machine with the most nodes per dollar whose digest matches. As of this entry that is Graviton4 spot.
