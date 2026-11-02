# ACSolverES Dual / Triple GS at 100,000 nodes

The same runs as [`../elliot_10k`](../elliot_10k/README.md): same settings (`max_len` 65, no frontier pruning), now with
a budget of 100,000 nodes.

```bash
python benchmark/elliot/run_elliot.py --budget 100000 --from results/elliot_10k --out results/elliot_100k --workers 3
python benchmark/elliot/summarize.py results/elliot_100k --md results/elliot_100k/SUMMARY_TABLE.md
```

## Which rows were searched

`--from` copies the rows solved at 10,000 (marked `carried_from`). The search is deterministic and nothing is
pruned, so a larger budget gives them the same result. Only the rows unsolved at 10,000 were searched.

- That is 55 rows, or 26 distinct searches, because bench60 and the ladder's `ms_*` rows are MS640 rows.
- All 26 searches are solved. The hardest needs 20,819 nodes.
- **Every row of MS640, bench60 and ladder100 is solved within 100,000 nodes, by all three methods**, so a budget of 10^6
  or 10^7 gives the same table.

## Checks

- All 640 MS640 rows equal ACSolverES's committed 10^6 run (`results/ms640_final_paper_v1`) in nodes and path, for all
  three methods.
- `VERIFY.json` is the independent replay of the 55 newly searched rows, and all of them pass. The carried rows were
  verified in `../elliot_10k/VERIFY.json`.
