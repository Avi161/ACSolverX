# [2026-10-13] A spot box needs an automatic relaunch from the minute it starts; several small boxes in different zones beat one big one [TRAP]

On 12 Oct 2026 the rank-3 counted rerun lost a spot box 8 times. Each relaunch waited for a person or an agent to notice. The worst case: a `c8g.48xlarge` spot helper (us-east-1c) was reclaimed at 23:50:04 UTC, 16 minutes after it started work, and its replacements only ran at 00:40 UTC. For those 50 minutes the on-demand main box worked alone, 96 cores instead of 288. Six minutes before that reclaim, a `c8g.16xlarge` spot helper that had been stable for three hours had been terminated to make room for the bigger box, in a zone that had already reclaimed two ARM spot boxes that day.

Two helpers cannot simply run side by side: with the same task order (`run_rank3_bf.py --reverse`) the second one picks the tasks the first has in flight, and a finished shard takes up to 165 s to be visible on the other box (push every 120 s, pull every 45 s).

**What replaced it** (00:40 UTC, 13 Oct):

- Three `c8g.16xlarge` spot helpers in three zones (us-east-1d, 1a, 1f), each on its own third of the presentations: `aws_rank3_split_helpers.py` writes the three user-data files from `aws_rank3_arm_helper_box.sh`, adding `--pres <ids>` and `--path-sample-target 675` (or 650). The target is scaled by k/640 so the sample fraction target / (words x k) stays exactly 2000 / (words x 640); `tests/stable_ac/test_rank3_split_helpers.py` checks the partition and the fraction. A reclaim now costs 64 running tasks, not 192.
- `aws_rank3_supervise.zsh`, started with the boxes: every 60 s it reads each box's state; on `Server.SpotInstanceTermination` it saves the log and starts the same user-data in the next zone, at most 3 times per helper. It restarts the on-demand main box if that disappears without `== DONE` or `FAIL`. It exits, which wakes the session, on `merged L10`, a `FAIL` line, a box gone for another reason, or no capacity.

Not used: a persistent spot request relaunches by itself, but this IAM user cannot call `CancelSpotInstanceRequests`, so it could never be stopped; Auto Scaling groups and EC2 Fleet need `CreateLaunchTemplate`, also denied.

**Rule:** launch no spot box without the relaunch loop already written and started in the same step. Do not replace a spot box that has run for hours with a larger one in a zone that reclaimed that day. To add spot cores, add small boxes in other zones, each on a disjoint part of the work.
