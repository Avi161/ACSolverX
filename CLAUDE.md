# Branch context: elliot-replication

This branch benchmarks Elliot Steffen's ACSolverES Dual / Triple greedy searches on MS640, bench60 and ladder100.

**Read [docs/ELLIOT_REPLICATION.md](docs/ELLIOT_REPLICATION.md) first.** It has the goal, setup, review findings,
results, open items and the user's working preferences.

For the rest of the repository, see README.md and docs/.

Quick facts:

- **Code:** `benchmark/elliot/` (run, summarize, verify).
- **Results:** `results/elliot_10k/`, `results/elliot_100k/`.
- **Status:** done at 10^4 and 10^5 nodes, every row solved, all paths verified.
- **Next:** a time-weighted cost study, waiting on the user's choice of unit.
- **No PR, no CI:** this branch has no pull request and none should be opened. Commit and push to
  `elliot-replication` only, and do not watch, run or fix CI (draft PR #38 was closed on request).
- **Ask first:** ask before expensive runs or deletions, and keep replies short.
