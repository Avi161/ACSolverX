# Ryan Zang's CoV-gate search, full table to 1,000,000 nodes (no length cap)

`results/ryan_1e5` (all 4,440 searches at 10^5) merged with `results/ryan_1e6` (the 171 searches unsolved at 10^5,
rerun at 10^6) by `benchmark/ryan/merge.py`. Rows solved at 10^5 are carried (`carried_from`): the search is
deterministic and nothing is pruned, so they give the same result at any larger budget.

```bash
python benchmark/ryan/run_all.py --out results/ryan_1e6 --max-nodes 1000000 --only-unsolved-from results/ryan_1e5 --workers 20
python benchmark/ryan/merge.py results/ryan_1e5 results/ryan_1e6 results/ryan_full_1e6
python benchmark/ryan/summarize.py results/ryan_full_1e6 --md results/ryan_full_1e6/SUMMARY_TABLE.md
```

## Result (`SUMMARY_TABLE.md`)

- **Five gates solve every row of MS640, bench60 and ladder100 within 10^6:** `no_short_sub`, `unbalanced`,
  `long_presentation`, `plateau100` and `periodic10`.
- **`short_relator` does not.** It solves 640 / 60 / 60 rows. That gate opens CoV only when a relator has at most 3
  letters, so it rarely uses CoV and behaves almost like LENGTH.
- **Path checks:** every path is verified, in `../ryan_1e5/VERIFY.json` and `../ryan_1e6/VERIFY.json` (all pass).
  Every CoV step stays in the Aut(F2) orbit, so the solves are AC paths.
- **Search size:** a 10^6 search holds up to about 17M states, or 146M for `short_relator` on ladder100. The longest
  relator generated is 84 letters, beyond Ryan's cap of 24.
