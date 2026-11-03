| benchmark | method | nodes | CoV pops | CPU s | CoV callback share of CPU | t_pop (us) | seed cost (pops) | CoV pop cost (pops) | cost units | cost / nodes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ms640 | Dual, single CoV | 328,688 | 4,504 | 97.7 | 30% | 209.5 | 23 | 28 | 466,359 | 1.42 |
| ms640 | Dual, auto CoV | 216,023 | 951 | 47.1 | 3% | 211.0 | 4 | 6 | 223,080 | 1.03 |
| ms640 | Triple | 216,292 | 1,191 | 51.5 | 10% | 213.9 | 6 | 11 | 240,554 | 1.11 |
| bench60 | Dual, single CoV | 155,682 | 1,972 | 46.7 | 26% | 221.8 | 34 | 28 | 210,540 | 1.35 |
| bench60 | Dual, auto CoV | 105,926 | 390 | 26.2 | 2% | 243.6 | 4 | 5 | 107,718 | 1.02 |
| bench60 | Triple | 105,841 | 490 | 26.7 | 6% | 236.9 | 6 | 10 | 112,738 | 1.07 |
| ladder100 | Dual, single CoV | 232,073 | 9,507 | 92.0 | 50% | 197.7 | 31 | 25 | 465,436 | 2.01 |
| ladder100 | Dual, auto CoV | 133,376 | 4,043 | 31.5 | 12% | 206.7 | 5 | 6 | 152,295 | 1.14 |
| ladder100 | Triple | 117,997 | 2,177 | 27.8 | 14% | 202.1 | 6 | 7 | 137,335 | 1.16 |

Solved within a budget B, counted in nodes and in cost units (CoV work included):

| benchmark | method | nodes <= 1e3 / 1e4 / 1e5 | cost <= 1e3 / 1e4 / 1e5 | cost median | cost max |
|---|---|---|---|---:|---:|
| ms640 | Dual, single CoV | 604 / 627 / 640 | 593 / 621 / 640 | 31 | 25,854 |
| ms640 | Dual, auto CoV | 618 / 634 / 640 | 614 / 634 / 640 | 14 | 18,110 |
| ms640 | Triple | 618 / 634 / 640 | 612 / 634 / 640 | 22 | 18,745 |
| bench60 | Dual, single CoV | 46 / 52 / 60 | 43 / 52 / 60 | 326 | 25,582 |
| bench60 | Dual, auto CoV | 51 / 56 / 60 | 51 / 56 / 60 | 192 | 18,079 |
| bench60 | Triple | 51 / 56 / 60 | 49 / 56 / 60 | 198 | 18,637 |
| ladder100 | Dual, single CoV | 64 / 92 / 100 | 56 / 82 / 100 | 796 | 61,821 |
| ladder100 | Dual, auto CoV | 80 / 97 / 100 | 77 / 96 / 100 | 315 | 18,113 |
| ladder100 | Triple | 86 / 97 / 100 | 81 / 97 / 100 | 314 | 18,680 |
