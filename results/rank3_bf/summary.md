# rank 3 brute force: 640 rows, budget 1000, cap 24

Control solves 554 of 640. 51,200 searches (80 starts per row), words of length 1 to 4.

| bucket | starts | solved | on control-solved | on control-unsolved | fewer | same | more | lost | solved by some | gained | lost by every | some faster |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 2 | 60.1% | 69.4% | 0.0% | 0.0% | 0.0% | 69.4% | 30.6% | 403 | 0 | 151 | 0 |
| L2 | 6 | 68.4% | 79.0% | 0.0% | 1.3% | 0.1% | 77.7% | 21.0% | 472 | 0 | 82 | 35 |
| L3 | 18 | 69.8% | 80.6% | 0.0% | 0.7% | 0.0% | 80.0% | 19.4% | 516 | 0 | 38 | 60 |
| L4 | 54 | 68.6% | 79.2% | 0.2% | 1.2% | 0.0% | 77.9% | 20.8% | 540 | 4 | 18 | 130 |

`solved` is a share of all presentations; `fewer`, `same`, `more` (pops against the control's) and `lost` are shares of the control-solved presentations and add up to 100%; the last four columns count presentations.

Best single start: `yXYx` solves 506 rows.

Cap counters (cap_dropped, cap_dropped_min_total, cap_would_pop, cap_first_bind, cap_needed): the cap dropped a child in 8 of 51,200 searches; could bind in 0 (0 solved); 0 unsolved searches stopped below the budget.
