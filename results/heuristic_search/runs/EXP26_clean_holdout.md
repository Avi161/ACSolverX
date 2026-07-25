# EXP-26 — the honest evaluation, on 580 never-seen presentations

`data/ms640_solved.txt` holds 640 solved Miller-Schupp presentations; the benchmark's 60 ladder rows are drawn from it. The other 580 were never in any slice, sweep, shortlist or report in this program. Restricted to the decidable band (bins 4-7, graded by the baseline's own 10^6-node run) that leaves **75 presentations**, and nothing here was selected on any of them — both orderings were fixed before this file existed.

| budget | arm | solved |
|---|---|---|
| 500 | baseline (length) | **11**/75 |
| 500 | recommended | **38**/75 |
| 500 | lean (500 rec) | **39**/75 |
| 1000 | baseline (length) | **20**/75 |
| 1000 | recommended | **50**/75 |
| 1000 | lean (500 rec) | **39**/75 |

## Against the contaminated figure

- budget **500**: baseline **11/75** → `lean (500 rec)` **39/75** (**+28**, 52% against 15%)
- budget **1000**: baseline **20/75** → `recommended` **50/75** (**+30**, 67% against 27%)

This replaces the three-class figure the audit left standing, and it is the number to quote: same decidable band, same caps, same orderings — on presentations that could not have leaked into the tuning, because they were never in any file this program read.

## Per bin

| budget | arm | bin 4 | bin 5 | bin 6 | bin 7 |
|---|---|---|---|---|---|
| 500 | baseline (length) | 11/25 | 0/20 | 0/22 | 0/8 |
| 500 | recommended | 21/25 | 12/20 | 5/22 | 0/8 |
| 500 | lean (500 rec) | 18/25 | 16/20 | 5/22 | 0/8 |
| 1000 | baseline (length) | 20/25 | 0/20 | 0/22 | 0/8 |
| 1000 | recommended | 25/25 | 16/20 | 9/22 | 0/8 |
| 1000 | lean (500 rec) | 18/25 | 16/20 | 5/22 | 0/8 |

## Does it ever lose?

At budget 1000 the recommended ordering solves **30** presentations the baseline does not, and the baseline solves **0** it does not. A strict superset — it never trades a solve away.

