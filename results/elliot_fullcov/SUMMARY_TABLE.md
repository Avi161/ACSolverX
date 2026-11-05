## Solved by budget (units)

| benchmark | method | 10^3 | 10^4 | 10^5 | 10^6 | 10^7 |
|---|---|---:|---:|---:|---:|---:|
| MS640 (of 640) | dual, single CoV | 612 | 634 | 640 | 640 | 640 |
| MS640 (of 640) | dual, auto CoV | 612 | 627 | 640 | 640 | 640 |
| MS640 (of 640) | triple | 612 | 637 | 640 | 640 | 640 |
| bench60 (of 60) | dual, single CoV | 49 | 57 | 60 | 60 | 60 |
| bench60 (of 60) | dual, auto CoV | 49 | 53 | 60 | 60 | 60 |
| bench60 (of 60) | triple | 49 | 58 | 60 | 60 | 60 |
| ladder100 (of 100) | dual, single CoV | 73 | 98 | 100 | 100 | 100 |
| ladder100 (of 100) | dual, auto CoV | 72 | 94 | 100 | 100 | 100 |
| ladder100 (of 100) | triple | 73 | 97 | 100 | 100 | 100 |

## Solves

| benchmark | method | solved | AC path | stable cert | units mean | median | max | path mean | median | max | longest relator | CoV moves (aut / stable / 24-map) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| MS640 | dual, single CoV | 640 | 465 | 175 | 305 | 9 | 19,544 | 41.2 | 9 | 963 | 19 | 845 / 277 / 0 |
| MS640 | dual, auto CoV | 640 | 477 | 163 | 579 | 8 | 31,332 | 40.2 | 8 | 907 | 20 | 552 / 269 / 303 |
| MS640 | triple | 640 | 484 | 156 | 312 | 8 | 18,528 | 39.2 | 8 | 842 | 20 | 501 / 276 / 458 |
| bench60 | dual, single CoV | 60 | 26 | 34 | 1,576 | 106 | 19,544 | 162.5 | 25.5 | 963 | 19 | 194 / 84 / 0 |
| bench60 | dual, auto CoV | 60 | 28 | 32 | 3,055 | 120 | 31,016 | 152.6 | 25.5 | 907 | 20 | 92 / 84 / 100 |
| bench60 | triple | 60 | 31 | 29 | 1,657 | 114 | 18,528 | 145.8 | 32.5 | 842 | 20 | 72 / 88 / 171 |
| ladder100 | dual, single CoV | 100 | 47 | 53 | 1,146 | 290 | 10,372 | 118.0 | 46 | 941 | 19 | 511 / 122 / 0 |
| ladder100 | dual, auto CoV | 100 | 55 | 45 | 2,059 | 426 | 31,016 | 116.3 | 48 | 907 | 20 | 225 / 108 / 382 |
| ladder100 | triple | 100 | 60 | 40 | 1,444 | 403 | 18,528 | 113.2 | 52 | 842 | 20 | 198 / 102 / 539 |

## Full-CoV moves on the solution paths (all rows, all methods)

|w| (automorphism / stable): 2: 1577 / 1274, 3: 902 / 75, 4: 400 / 18, 5: 204 / 40, 6: 96 / 3, 7: 10 / 0, 9: 1 / 0

occurrences substituted (automorphism / stable): 1: 992 / 0, 2: 1798 / 69, 3: 307 / 1089, 4: 54 / 68, 5: 30 / 42, 6: 9 / 54, 7: 0 / 40, 8: 0 / 27, 9: 0 / 21
