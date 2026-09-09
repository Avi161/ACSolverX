# AC19 Aut-minimal census: final policy at 1,000 charged units

**72,052 / 72,779 solved (99.001%); 727 unsolved.** Every solve was decoded
and independently replayed to `(x,y)`. No errors or budget violations occurred.

- [Results and timings](RESULTS.md)
- [Algorithm, sufficient completion rules, and reproduction commands](../../../research/supermoves_20260908/AC19_FULL_CENSUS_ALGORITHM.md)
- [Machine-readable summary](SUMMARY.json)
- [Exact 727-row continuation list](unsolved.csv)
- [Exact input census](../../../data/AC19_extended_aut_min.csv)
- [Publication file hashes](PUBLICATION_MANIFEST.json)

The 74 `rows_*.jsonl` shards contain all 72,779 input outcomes and the mixed
certificate for every solve. Expanded elementary arrays are reconstructed from
those saved paths; another search is unnecessary. Interval manifests pin the
executed input and 44 runtime files. `rows_*.summary.json` are cumulative within
each invocation and must not be added together; use `SUMMARY.json`.

This is a research-branch experiment with no ordinary relator-length cap.
The 1,000-unit allowance includes several kinds of work; consult the recorded
wall and CPU times when comparing compute costs.
