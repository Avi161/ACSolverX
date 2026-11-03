# Branch context: ryan-replication

This branch replicates Ryan Zang's CoV-gate best-first search (ryanzang04/Stable-ACSolver) on MS640, bench60 and
ladder100, with a numba CPU port (no JAX) and no relator-length cap. It was cut from `elliot-replication`, so it also
carries the Elliot Steffen work.

**Read [docs/RYAN_REPLICATION.md](docs/RYAN_REPLICATION.md) first**, then [docs/ELLIOT_REPLICATION.md](docs/ELLIOT_REPLICATION.md)
for the Elliot side and the user's working preferences.

Quick facts:

- **Code:** `benchmark/ryan/` (Python port, numba kernel, equivalence checks, driver, summary, verifier) and
  `benchmark/elliot/`.
- **Results:** `results/ryan_1e5/`, `results/ryan_1e6/` (when present); Elliot: `results/elliot_*`.
- **AWS:** `ops/aws/` scripts. `ops/aws/ledger.md` records every box and its cost. Terminate boxes when done and run
  the all-regions audit. Spot only, cheapest.
- **No PR, no CI:** commit and push to the branch only; do not open PRs or watch CI.
- **Ask first:** ask before expensive runs or deletions, and keep replies short.
