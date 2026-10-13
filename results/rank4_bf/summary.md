# rank 4 brute force: 223 rows, budget 1000, cap 24

Control solves 219 of 223. 78,273 searches (351 starts per row), words of length 1 to 3.

| bucket | starts | solved | on control-solved | on control-unsolved | fewer | same | more | lost | solved by some | gained | lost by every | some faster |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 351 | 83.2% | 84.7% | 0.0% | 0.1% | 0.0% | 84.7% | 15.3% | 216 | 0 | 3 | 9 |

`solved` is a share of all presentations; `fewer`, `same`, `more` (pops against the control's) and `lost` are shares of the control-solved presentations and add up to 100%; the last four columns count presentations.

Best single start: `yxY,Yxy` solves 208 rows.

Cap counters (cap_dropped, cap_dropped_min_total, cap_would_pop, cap_first_bind, cap_needed): the cap dropped a child in 0 of 78,273 searches; could bind in 0 (0 solved); 0 unsolved searches stopped below the budget.
