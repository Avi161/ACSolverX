# MS640: length ordering vs L + 20·S + 2·MK at 10^6 nodes

Both arms run `greedy_search_hcompact` (the engine of the AC19 escalation waves) on all 640 solved Miller–Schupp presentations, node budget 1,000,000 heap pops, per-relator cap 24 (the Two-Hump baseline setting). Only the heap ordering differs: `LENGTH_ONLY` (priority L) vs `S20_MK2` (priority L + 20S + 2MK). Presentations: `r1,r2` columns of the paper's `data/06_ms640_greedy_vs_hybrid.csv`.

| arm | solved | mean nodes | median | max | total nodes | mean path |
|---|---|---|---|---|---|---|
| greedy (L) | 640 | 4,963.0 | 11 | 574,959 | 3,176,297 | 36.77 |
| L+20S+2MK | 640 | 994.8 | 11 | 34,438 | 636,670 | 42.88 |

Greedy arm reproduces the paper's `greedy_nodes` column exactly on all 640 rows (0 mismatches), so the engine and cap match the published baseline. On the 14 presentations that need more than 10,000 nodes under both orderings: mean 96,150 (greedy) vs 28,139 (L+20S+2MK).

Run: `PYTHONPATH=. .venv/bin/python3 results/heuristic_search/ms640_s20_mk2_1m/run_ms640.py <csv> {greedy|s20_mk2} 24` (6 workers, ~2 min per arm on an M-series laptop).
