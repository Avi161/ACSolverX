# rank 5 brute force: 32 rows, budget 1000, cap 24

Control solves 28 of 32. 3,840 searches (120 starts per row), words of length 1 to 2.

| bucket | starts | solved | on control-solved | on control-unsolved | fewer | same | more | lost | solved by some | gained | lost by every | some faster |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 120 | 57.5% | 65.7% | 0.0% | 0.2% | 0.0% | 65.5% | 34.3% | 21 | 0 | 7 | 1 |

`solved` is a share of all presentations; `fewer`, `same`, `more` (pops against the control's) and `lost` are shares of the control-solved presentations and add up to 100%; the last four columns count presentations.

Best single start: `xx,xy,yx` solves 20 rows.

Cap counters (cap_dropped, cap_dropped_min_total, cap_would_pop, cap_first_bind, cap_needed): the cap dropped a child in 0 of 3,840 searches; could bind in 0 (0 solved); 0 unsolved searches stopped below the budget.
