## Solved ladder (60 rows), solves by difficulty bin and pop budget (max 2000)

Cell = rows solved within that many heap pops (best-first is deterministic, so one run at the largest budget gives every smaller budget).


### arm `ctrl`

| bin | rows | <= 100 pops | <= 300 pops | <= 1000 pops | <= 2000 pops | unsolved | verified | mean states (solved) | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 168 | 0.1 |
| 1 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 1,018 | 0.4 |
| 2 | 6 | 5 | 6 | 6 | 6 | 0 | 6 | 6,330 | 2.3 |
| 3 | 6 | 2 | 6 | 6 | 6 | 0 | 6 | 18,475 | 7.4 |
| 4 | 6 | 0 | 1 | 5 | 6 | 0 | 6 | 78,775 | 43.5 |
| 5 | 6 | 0 | 0 | 0 | 4 | 2 | 4 | 219,156 | 148.0 |
| 6 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 256.2 |
| 7 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 228.0 |
| 8 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 217.7 |
| 9 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 228.3 |
| **all** | 60 | 19 | 25 | 29 | 34 | 26 | 34 | | 1,131.9 |

### arm `dyn`

| bin | rows | <= 100 pops | <= 300 pops | <= 1000 pops | <= 2000 pops | unsolved | verified | mean states (solved) | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 52 | 0.1 |
| 1 | 6 | 5 | 5 | 6 | 6 | 0 | 6 | 6,246 | 5.9 |
| 2 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 1,235 | 1.0 |
| 3 | 6 | 2 | 3 | 5 | 6 | 0 | 6 | 35,088 | 35.1 |
| 4 | 6 | 3 | 4 | 6 | 6 | 0 | 6 | 20,701 | 18.8 |
| 5 | 6 | 0 | 0 | 2 | 2 | 4 | 2 | 42,786 | 152.6 |
| 6 | 6 | 0 | 0 | 3 | 3 | 3 | 3 | 62,863 | 139.8 |
| 7 | 6 | 0 | 0 | 4 | 5 | 1 | 5 | 94,619 | 151.2 |
| 8 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 280.5 |
| 9 | 6 | 0 | 0 | 2 | 2 | 4 | 2 | 71,150 | 181.9 |
| **all** | 60 | 22 | 24 | 40 | 42 | 18 | 42 | | 966.8 |

### arm `dyn_c10s12`

| bin | rows | <= 100 pops | <= 300 pops | <= 1000 pops | <= 2000 pops | unsolved | verified | mean states (solved) | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 74 | 0.1 |
| 1 | 6 | 5 | 5 | 6 | 6 | 0 | 6 | 13,590 | 11.3 |
| 2 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 2,242 | 1.7 |
| 3 | 6 | 4 | 5 | 6 | 6 | 0 | 6 | 25,844 | 23.4 |
| 4 | 6 | 3 | 5 | 6 | 6 | 0 | 6 | 21,822 | 19.3 |
| 5 | 6 | 0 | 0 | 1 | 3 | 3 | 3 | 165,516 | 255.0 |
| 6 | 6 | 1 | 1 | 3 | 3 | 3 | 3 | 70,183 | 247.2 |
| 7 | 6 | 0 | 0 | 3 | 4 | 2 | 4 | 172,827 | 228.7 |
| 8 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 481.9 |
| 9 | 6 | 0 | 0 | 2 | 2 | 4 | 2 | 144,934 | 373.7 |
| **all** | 60 | 25 | 28 | 39 | 42 | 18 | 42 | | 1,642.1 |

### arm `dyn_norelabel`

| bin | rows | <= 100 pops | <= 300 pops | <= 1000 pops | <= 2000 pops | unsolved | verified | mean states (solved) | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 52 | 0.0 |
| 1 | 6 | 5 | 5 | 5 | 6 | 0 | 6 | 16,576 | 7.0 |
| 2 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 1,354 | 0.5 |
| 3 | 6 | 2 | 2 | 5 | 5 | 1 | 5 | 35,548 | 29.2 |
| 4 | 6 | 2 | 4 | 5 | 6 | 0 | 6 | 43,507 | 15.0 |
| 5 | 6 | 0 | 0 | 0 | 2 | 4 | 2 | 143,569 | 85.3 |
| 6 | 6 | 0 | 0 | 1 | 2 | 4 | 2 | 101,608 | 78.1 |
| 7 | 6 | 0 | 0 | 0 | 4 | 2 | 4 | 164,783 | 79.7 |
| 8 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 132.4 |
| 9 | 6 | 0 | 0 | 0 | 2 | 4 | 2 | 189,683 | 107.2 |
| **all** | 60 | 21 | 23 | 28 | 39 | 21 | 39 | | 534.3 |

### arm `tri`

| bin | rows | <= 100 pops | <= 300 pops | <= 1000 pops | <= 2000 pops | unsolved | verified | mean states (solved) | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 6 | 6 | 6 | 6 | 6 | 0 | 6 | 1,286 | 1.2 |
| 1 | 6 | 5 | 6 | 6 | 6 | 0 | 6 | 2,609 | 2.7 |
| 2 | 6 | 2 | 6 | 6 | 6 | 0 | 6 | 5,700 | 6.2 |
| 3 | 6 | 1 | 2 | 4 | 6 | 0 | 6 | 20,194 | 32.4 |
| 4 | 6 | 0 | 0 | 1 | 1 | 5 | 1 | 34,197 | 100.8 |
| 5 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 137.8 |
| 6 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 156.1 |
| 7 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 154.9 |
| 8 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 181.0 |
| 9 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | - | 154.3 |
| **all** | 60 | 14 | 20 | 23 | 25 | 35 | 25 | | 927.4 |

### Per row (pops to solve; `-` = unsolved at the budget)

| row | bin | r1, r2 | L | greedy nodes (1M budget) | ctrl | dyn | dyn_c10s12 | dyn_norelabel | tri | dyn min L | dyn path (defs/elims/prods, max rank) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 0 | `YYXyx`, `Yx` | 7 | 3 | 3 | 2 | 2 | 2 | 4 | 0 | 2 (0/2/0, 2) |
| 228 | 0 | `YYYXyyx`, `YYXXYYx` | 14 | 9 | 6 | 5 | 5 | 5 | 5 | 0 | 5 (1/3/1, 3) |
| 323 | 0 | `YYYYYx`, `YYYYXyyyx` | 15 | 7 | 4 | 2 | 2 | 2 | 6 | 0 | 2 (0/2/0, 2) |
| 455 | 0 | `YYYYYXyyyyx`, `YYYYxYXX` | 19 | 10 | 9 | 3 | 3 | 3 | 8 | 0 | 3 (0/2/1, 2) |
| 496 | 0 | `YYYYYYYXyyyyyyx`, `YYX` | 18 | 4 | 4 | 2 | 2 | 2 | 8 | 0 | 2 (0/2/0, 2) |
| 521 | 0 | `YYYYYYYYXyyyyyyyx`, `YYYx` | 21 | 5 | 4 | 2 | 2 | 2 | 8 | 0 | 2 (0/2/0, 2) |
| 43 | 1 | `YYXyx`, `YYxYxYX` | 12 | 13 | 9 | 10 | 10 | 8 | 8 | 0 | 7 (2/4/1, 3) |
| 48 | 1 | `YYYxxYX`, `YYXyx` | 12 | 18 | 16 | 10 | 10 | 8 | 22 | 0 | 7 (2/4/1, 3) |
| 77 | 1 | `YYXyx`, `YXyXXyxx` | 13 | 11 | 10 | 9 | 9 | 9 | 9 | 0 | 7 (1/3/3, 3) |
| 141 | 1 | `YYXyx`, `YXyXyxxx` | 13 | 12 | 11 | 10 | 10 | 10 | 9 | 0 | 7 (1/3/3, 3) |
| 155 | 1 | `YYYYxyXX`, `YYXyx` | 13 | 18 | 16 | 17 | 17 | 17 | 18 | 0 | 8 (2/4/2, 3) |
| 505 | 1 | `YYYYYYYXyyyyyyx`, `YYXyyxx` | 22 | 34 | 34 | 463 | 458 | 1197 | 115 | 0 | 30 (7/9/14, 4) |
| 201 | 2 | `YYYXyyx`, `YYXYxYx` | 14 | 61 | 56 | 17 | 17 | 21 | 293 | 0 | 10 (3/5/2, 3) |
| 217 | 2 | `YYYXyyx`, `YYYxxyX` | 14 | 57 | 49 | 15 | 15 | 18 | 136 | 0 | 9 (2/4/3, 3) |
| 247 | 2 | `YYYXyyx`, `YYXyyXyx` | 15 | 46 | 33 | 17 | 17 | 17 | 98 | 0 | 10 (2/4/4, 3) |
| 288 | 2 | `YYYYXXYx`, `YYYXyyx` | 15 | 106 | 100 | 25 | 25 | 26 | 183 | 0 | 14 (4/6/4, 3) |
| 331 | 2 | `YYYYXyyyx`, `YYXYxYx` | 16 | 93 | 105 | 14 | 14 | 15 | 161 | 0 | 12 (4/6/2, 4) |
| 367 | 2 | `YYYYXyyyx`, `YYXYYxYx` | 17 | 83 | 86 | 32 | 32 | 32 | 78 | 0 | 18 (5/7/6, 4) |
| 203 | 3 | `YYYXyyx`, `YYxYXYx` | 14 | 116 | 98 | 22 | 22 | 21 | 79 | 0 | 13 (4/6/3, 3) |
| 265 | 3 | `YYYXyyx`, `YYYxYxYX` | 15 | 121 | 100 | 25 | 25 | 22 | 836 | 0 | 15 (5/7/3, 4) |
| 327 | 3 | `YYYYXyyyx`, `YYxYXX` | 15 | 273 | 204 | 210 | 210 | 421 | 467 | 0 | 18 (5/7/6, 4) |
| 333 | 3 | `YYYYXyyyx`, `YYxyXYx` | 16 | 313 | 215 | 488 | 56 | 895 | 275 | 0 | 22 (6/8/8, 4) |
| 380 | 3 | `YYYYXyyyx`, `YYYYxxyX` | 17 | 381 | 239 | 507 | 87 | 963 | 1977 | 0 | 24 (8/10/6, 4) |
| 579 | 3 | `YYYYYYXyyyyyx`, `YYYXYYxx` | 21 | 366 | 135 | 1013 | 586 | - | 1328 | 0 | 21 (7/9/5, 5) |
| 533 | 4 | `YYYYXyyyx`, `YYYXYxYx` | 17 | 438 | 239 | 515 | 94 | 934 | - | 0 | 25 (8/10/7, 4) |
| 546 | 4 | `YYYYYXyyyyx`, `YYXYYxYx` | 19 | 398 | 370 | 158 | 158 | 298 | - | 0 | 20 (5/7/8, 4) |
| 548 | 4 | `YYYYYXyyyyx`, `YYxYYxyX` | 19 | 661 | 478 | 31 | 31 | 35 | - | 0 | 13 (4/6/3, 4) |
| 580 | 4 | `YYYYYYXyyyyyx`, `YYYxxYYX` | 21 | 875 | 560 | 45 | 45 | 48 | 904 | 0 | 26 (8/10/8, 4) |
| 589 | 4 | `YYYYYYXyyyyyx`, `YYYXYXYx` | 21 | 558 | 342 | 100 | 103 | 104 | - | 0 | 35 (10/12/13, 5) |
| 609 | 4 | `YYYYYYYXyyyyyyx`, `YYYxYxyX` | 23 | 1217 | 1149 | 635 | 486 | 1170 | - | 0 | 51 (18/20/13, 5) |
| 538 | 5 | `YYYYYXyyyyx`, `YYxYxYX` | 18 | 2261 | - | 434 | 434 | 1948 | - | 0 | 18 (5/7/6, 4) |
| 543 | 5 | `YYYYYXyyyyx`, `YYYYXYxx` | 19 | 1813 | 1445 | - | - | - | - | 15 |  |
| 544 | 5 | `YYYYYXyyyyx`, `YYYxyXYx` | 19 | 1569 | 1441 | - | 1144 | - | - | 15 |  |
| 549 | 5 | `YYYYYXyyyyx`, `YYYxYxYX` | 19 | 1411 | 1013 | - | - | - | - | 15 |  |
| 565 | 5 | `YYYYYYXyyyyyx`, `YYxyXYx` | 20 | 1404 | 1299 | - | - | - | - | 16 |  |
| 606 | 5 | `YYYYYYYXyyyyyyx`, `YYYxxYYX` | 23 | 2023 | - | 548 | 1544 | 1380 | - | 0 | 48 (13/15/20, 5) |
| 573 | 6 | `YYYYYYXyyyyyx`, `YYYYXYxx` | 21 | 13393 | - | 616 | 616 | 1101 | - | 0 | 36 (14/16/6, 4) |
| 575 | 6 | `YYYYYYXyyyyyx`, `YYYxyXYx` | 21 | 14383 | - | - | - | - | - | 16 |  |
| 581 | 6 | `YYYYYYXyyyyyx`, `YYYYxxYX` | 21 | 9567 | - | - | - | - | - | 16 |  |
| 586 | 6 | `YYYYYYXyyyyyx`, `YYYYxYXX` | 21 | 9162 | - | - | - | - | - | 16 |  |
| 602 | 6 | `YYYYYYYXyyyyyyx`, `YYYxYXX` | 22 | 6285 | - | 949 | 682 | - | - | 0 | 54 (19/21/14, 5) |
| 632 | 6 | `YYYYYYYYXyyyyyyyx`, `YYYYXXYx` | 25 | 6425 | - | 463 | 73 | 578 | - | 0 | 46 (14/16/16, 4) |
| 568 | 7 | `YYYYYYXyyyyyx`, `YYXYXyx` | 20 | 15814 | - | 607 | 607 | 1097 | - | 0 | 37 (14/16/7, 4) |
| 578 | 7 | `YYYYYYXyyyyyx`, `YYXYYXyx` | 21 | 15873 | - | 619 | 635 | 1235 | - | 0 | 44 (17/19/8, 4) |
| 583 | 7 | `YYYYYYXyyyyyx`, `YYXyxYYx` | 21 | 16111 | - | 541 | 541 | 1087 | - | 0 | 32 (12/14/6, 4) |
| 596 | 7 | `YYYYYYYXyyyyyyx`, `YYxyXYx` | 22 | 16168 | - | - | - | - | - | 16 |  |
| 628 | 7 | `YYYYYYYYXyyyyyyyx`, `YYXyXyyx` | 25 | 26774 | - | 799 | 1362 | 1521 | - | 0 | 76 (22/24/30, 5) |
| 633 | 7 | `YYYYYYYYXyyyyyyyx`, `YYXyyxyx` | 25 | 26838 | - | 1557 | - | - | - | 0 | 101 (26/28/47, 5) |
| 605 | 8 | `YYYYYYYXyyyyyyx`, `YYYXyxYX` | 23 | 60593 | - | - | - | - | - | 17 |  |
| 610 | 8 | `YYYYYYYXyyyyyyx`, `YYYxYXyx` | 23 | 61366 | - | - | - | - | - | 16 |  |
| 622 | 8 | `YYYYYYYYXyyyyyyyx`, `YYxyXYx` | 24 | 78774 | - | - | - | - | - | 17 |  |
| 623 | 8 | `YYYYYYYYXyyyyyyyx`, `YYXyxYX` | 24 | 59710 | - | - | - | - | - | 17 |  |
| 624 | 8 | `YYYYYYYYXyyyyyyyx`, `YYxYXyx` | 24 | 59971 | - | - | - | - | - | 17 |  |
| 625 | 8 | `YYYYYYYYXyyyyyyyx`, `YYXYxyX` | 24 | 78770 | - | - | - | - | - | 17 |  |
| 634 | 9 | `YYYYYYYXyyyyyyx`, `YYYXyyxx` | 23 | 574348 | - | 650 | 608 | 1604 | - | 0 | 69 (20/22/27, 5) |
| 635 | 9 | `YYYYYYYXyyyyyyx`, `YYYXXyyx` | 23 | 574959 | - | 612 | 628 | 1244 | - | 0 | 63 (17/19/27, 4) |
| 636 | 9 | `YYYYYYYYXyyyyyyyx`, `YYYXYxyX` | 25 | 213882 | - | - | - | - | - | 17 |  |
| 637 | 9 | `YYYYYYYYXyyyyyyyx`, `YYYXyxYX` | 25 | 271866 | - | - | - | - | - | 17 |  |
| 638 | 9 | `YYYYYYYYXyyyyyyyx`, `YYYxyXYx` | 25 | 213878 | - | - | - | - | - | 17 |  |
| 639 | 9 | `YYYYYYYYXyyyyyyyx`, `YYYxYXyx` | 25 | 272953 | - | - | - | - | - | 17 |  |

## U124 rows

arm `dyn`: 124 rows, solved 0, pops budget 2000, total CPU 5,229 s

| row | r1, r2 | L | arm | pops | states | min total length | max rank | CPU s |
|---|---|---:|---|---:|---:|---:|---:|---:|
| aca_0 | `YXXyxYx`, `YYYYYYXyxyX` | 18 | dyn | 2000 | 272,227 | 18 | 6 | 47.3 |
| aca_1 | `YYXXyxx`, `YYYxyXyX` | 15 | dyn | 2000 | 213,431 | 15 | 5 | 34.8 |
| aca_2 | `YXXyXyx`, `YYYXyyyxx` | 16 | dyn | 2000 | 190,516 | 16 | 5 | 33.9 |
| aca_3 | `YXXyxYx`, `YYYYYxyxyX` | 17 | dyn | 2000 | 136,495 | 17 | 5 | 26.7 |
| aca_4 | `YYXXXyx`, `YYxyxyXyXYX` | 18 | dyn | 2000 | 207,717 | 17 | 5 | 37.9 |
| aca_5 | `YYXXXyX`, `YYYxyXyxyxyx` | 19 | dyn | 2000 | 181,317 | 16 | 5 | 32.1 |
| aca_6 | `YYXXyxxyx`, `YXXXXXyxYx` | 19 | dyn | 2000 | 179,955 | 16 | 6 | 32.0 |
| aca_7 | `YYXXyxx`, `YYYYxYXYX` | 16 | dyn | 2000 | 187,187 | 15 | 5 | 32.1 |
| aca_8 | `YXyXYxx`, `YYXYXyyx` | 15 | dyn | 2000 | 306,698 | 14 | 5 | 44.1 |
| aca_9 | `YXXXyxx`, `YYYXXyyX` | 15 | dyn | 2000 | 163,816 | 15 | 5 | 26.6 |
| aca_10 | `YXXXyxx`, `YYXYXyyX` | 15 | dyn | 2000 | 169,300 | 15 | 5 | 27.2 |
| aca_11 | `YXXXyxx`, `YYYXyxyx` | 15 | dyn | 2000 | 212,018 | 15 | 5 | 33.9 |
| aca_12 | `YXXXyxx`, `YYXYxyyX` | 15 | dyn | 2000 | 161,477 | 15 | 5 | 26.7 |
| aca_13 | `YYXXYYx`, `YXXXyxxYx` | 16 | dyn | 2000 | 276,537 | 15 | 5 | 41.7 |
| aca_14 | `YXXyXyx`, `YYYXyyxx` | 15 | dyn | 2000 | 213,592 | 15 | 5 | 32.8 |
| aca_15 | `YXXyXyxx`, `YYYYxyyyX` | 17 | dyn | 2000 | 215,209 | 16 | 5 | 36.8 |
| aca_16 | `YYXXXyxx`, `YXyxxyXYx` | 17 | dyn | 2000 | 277,668 | 15 | 5 | 42.6 |
| aca_17 | `YXXXYxYx`, `YYYYXyyyx` | 17 | dyn | 2000 | 201,483 | 17 | 5 | 36.5 |
| aca_18 | `YXXXyxYx`, `YYYYxyyyX` | 17 | dyn | 2000 | 182,074 | 17 | 5 | 33.8 |
| aca_19 | `YXyXYxxx`, `YYYYXyyyx` | 17 | dyn | 2000 | 242,941 | 17 | 5 | 41.8 |
| aca_20 | `YXXXyxYx`, `YYYYXyyyx` | 17 | dyn | 2000 | 164,477 | 17 | 5 | 30.3 |
| aca_21 | `YXXYxxyX`, `YYYYxyyyX` | 17 | dyn | 2000 | 318,437 | 17 | 6 | 53.8 |
| aca_22 | `YXXYxxyx`, `YYYYxyyyX` | 17 | dyn | 2000 | 310,301 | 17 | 6 | 52.0 |
| aca_23 | `YXXYxxyx`, `YYYYXyyyx` | 17 | dyn | 2000 | 260,830 | 17 | 5 | 45.2 |
| aca_24 | `YYXXXYxx`, `YYYXXYXYx` | 17 | dyn | 2000 | 279,251 | 15 | 5 | 43.4 |
| aca_25 | `YXXYxxyX`, `YYYYXyyyx` | 17 | dyn | 2000 | 286,582 | 16 | 6 | 46.3 |
| aca_26 | `YXXYxYxx`, `YYYYxyyyX` | 17 | dyn | 2000 | 185,066 | 16 | 5 | 32.8 |
| aca_27 | `YXXyXyxx`, `YYYYXyyyx` | 17 | dyn | 2000 | 229,341 | 17 | 5 | 38.4 |
| aca_28 | `YXXYxYxx`, `YYYYXyyyx` | 17 | dyn | 2000 | 182,827 | 16 | 5 | 32.1 |
| aca_29 | `YYXXXyx`, `YYxxyxyXyX` | 17 | dyn | 2000 | 227,904 | 15 | 5 | 35.1 |
| aca_30 | `YYXXyx`, `YYYYYxyXXyX` | 17 | dyn | 2000 | 184,023 | 15 | 5 | 29.7 |
| aca_31 | `YYXXyxx`, `YYYYYXyXyx` | 17 | dyn | 2000 | 146,275 | 15 | 5 | 25.9 |
| aca_32 | `YXXYxxyx`, `YYYYXyxyx` | 17 | dyn | 2000 | 167,527 | 16 | 5 | 30.3 |
| aca_33 | `YXXXyxYx`, `YYXyXyxyx` | 17 | dyn | 2000 | 161,467 | 16 | 5 | 29.5 |
| aca_34 | `YXXyxYx`, `YYYYXyyxx` | 16 | dyn | 2000 | 167,425 | 16 | 5 | 29.6 |
| aca_35 | `YYXXXyx`, `YYYxxyxyXyX` | 18 | dyn | 2000 | 315,444 | 17 | 5 | 52.0 |
| aca_36 | `YXXyxYx`, `YYYxYYXYX` | 16 | dyn | 2000 | 228,444 | 15 | 5 | 34.7 |
| aca_37 | `YYXXXYxx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 119,315 | 17 | 5 | 25.7 |
| aca_38 | `YYXXXyxx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 119,316 | 17 | 5 | 26.3 |
| aca_39 | `YXXXYxYx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 191,290 | 18 | 6 | 35.2 |
| aca_40 | `YXXXyxYx`, `YYYYYxyyyyX` | 19 | dyn | 2000 | 188,498 | 18 | 6 | 35.9 |
| aca_41 | `YXyXYxxx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 196,799 | 18 | 6 | 36.8 |
| aca_42 | `YXXXyxYx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 148,937 | 18 | 6 | 28.8 |
| aca_43 | `YYXXyxx`, `YYxyXYxyXyX` | 18 | dyn | 2000 | 291,478 | 16 | 5 | 45.4 |
| aca_44 | `YYXXYYx`, `YXyXYxxYXyx` | 18 | dyn | 2000 | 186,131 | 16 | 5 | 32.0 |
| aca_45 | `YXXyXYxxx`, `YYYYXXXYxx` | 19 | dyn | 2000 | 239,318 | 17 | 6 | 40.6 |
| aca_46 | `YXXYxxyx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 198,801 | 18 | 6 | 35.0 |
| aca_47 | `YXXYxxyX`, `YYYYYxyyyyX` | 19 | dyn | 2000 | 261,666 | 18 | 6 | 46.2 |
| aca_48 | `YXXXyxYxx`, `YYYYXXyxxx` | 19 | dyn | 2000 | 253,175 | 17 | 6 | 42.9 |
| aca_49 | `YXXYxxyx`, `YYYYYxyyyyX` | 19 | dyn | 2000 | 260,557 | 18 | 6 | 46.1 |
| aca_50 | `YXXYxxyX`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 198,793 | 18 | 6 | 36.1 |
| aca_51 | `YXXYxYxx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 206,051 | 18 | 6 | 38.6 |
| aca_52 | `YXXyXyxx`, `YYYYYXyyyyx` | 19 | dyn | 2000 | 213,234 | 18 | 6 | 39.4 |
| aca_53 | `YXXyxYx`, `YYXyyXyxyxx` | 18 | dyn | 2000 | 176,636 | 16 | 5 | 31.4 |
| aca_54 | `YYXXXXyxx`, `YYxxyXXXXX` | 19 | dyn | 2000 | 362,730 | 16 | 5 | 57.9 |
| aca_55 | `YYXXXyxyx`, `YYxYXXyyX` | 18 | dyn | 2000 | 307,771 | 17 | 6 | 52.6 |
| aca_56 | `YYXXXyxx`, `YYXYYxxyXXX` | 19 | dyn | 2000 | 424,432 | 17 | 6 | 68.4 |
| aca_57 | `YYXXXyxx`, `YYXYYxyXXXX` | 19 | dyn | 2000 | 246,879 | 17 | 6 | 42.3 |
| aca_58 | `YXXyxYx`, `YYYYYXyyxx` | 17 | dyn | 2000 | 204,276 | 17 | 5 | 36.6 |
| aca_59 | `YXXYxxyxx`, `YYYYxxxxxxx` | 20 | dyn | 2000 | 263,504 | 17 | 6 | 44.9 |
| aca_60 | `YXXXyxYxx`, `YYYYYXXyxxx` | 20 | dyn | 2000 | 213,355 | 18 | 6 | 39.9 |
| aca_61 | `YXXyXYxxx`, `YYYYYXXXYxx` | 20 | dyn | 2000 | 217,320 | 18 | 6 | 40.8 |
| aca_62 | `YXXXYxYx`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 217,141 | 19 | 6 | 42.0 |
| aca_63 | `YXXXyxYx`, `YYYYYYxyyyyyX` | 21 | dyn | 2000 | 311,667 | 19 | 6 | 57.0 |
| aca_64 | `YXyXYxxx`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 260,855 | 19 | 6 | 48.6 |
| aca_65 | `YXXXyxYx`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 274,357 | 19 | 6 | 51.8 |
| aca_66 | `YYXXXyxxx`, `YYXyXyxYXyx` | 20 | dyn | 2000 | 268,394 | 17 | 5 | 46.4 |
| aca_67 | `YYXXXyXXX`, `YYXyxYXyxyX` | 20 | dyn | 2000 | 219,603 | 18 | 6 | 39.5 |
| aca_68 | `YXXYxxyx`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 308,246 | 19 | 6 | 58.5 |
| aca_69 | `YXXYxxyX`, `YYYYYYxyyyyyX` | 21 | dyn | 2000 | 292,573 | 19 | 6 | 53.3 |
| aca_70 | `YXXYxxyx`, `YYYYYYxyyyyyX` | 21 | dyn | 2000 | 292,565 | 19 | 6 | 53.8 |
| aca_71 | `YYXXXyxx`, `YYXyxyXYxyX` | 19 | dyn | 2000 | 249,022 | 17 | 6 | 42.5 |
| aca_72 | `YYXXyxx`, `YYxyXyxyXyX` | 18 | dyn | 2000 | 193,295 | 16 | 5 | 34.4 |
| aca_73 | `YXXYxxyX`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 311,741 | 19 | 6 | 57.4 |
| aca_74 | `YXXyXyxx`, `YYYYYYXyyyyyx` | 21 | dyn | 2000 | 258,716 | 19 | 6 | 49.5 |
| aca_75 | `YXXXyxYxx`, `YYYYYYXXXYxx` | 21 | dyn | 2000 | 224,590 | 19 | 6 | 41.5 |
| aca_76 | `YXXXyxYxx`, `YYYYYYXXyxxx` | 21 | dyn | 2000 | 373,050 | 19 | 6 | 66.6 |
| aca_77 | `YXXyXYxxx`, `YYYYYYXXXYxx` | 21 | dyn | 2000 | 395,183 | 19 | 6 | 69.0 |
| aca_78 | `YXXyXyx`, `YYYXYXyxyyxx` | 19 | dyn | 2000 | 218,287 | 18 | 6 | 38.2 |
| aca_79 | `YYXXXyyxx`, `YXXXXXyxxYxx` | 21 | dyn | 2000 | 365,825 | 17 | 6 | 59.0 |
| aca_80 | `YYXXyx`, `YYYXyXYYYxyXX` | 19 | dyn | 2000 | 278,734 | 16 | 6 | 45.6 |
| aca_81 | `YXXyxYx`, `YYYYYYXyyxx` | 18 | dyn | 2000 | 159,978 | 17 | 5 | 31.0 |
| aca_82 | `YYYXXXXXyyx`, `YYXyxxyyxYX` | 22 | dyn | 2000 | 234,608 | 19 | 6 | 45.8 |
| aca_83 | `YXXyXYxxx`, `YYYYYYYXXyxxx` | 22 | dyn | 2000 | 279,196 | 19 | 6 | 52.9 |
| aca_84 | `YXXXyxYxx`, `YYYYYYYXXXYxx` | 22 | dyn | 2000 | 302,990 | 19 | 6 | 57.2 |
| aca_85 | `YXyXYxx`, `YYYYYYXXYYx` | 18 | dyn | 2000 | 165,008 | 17 | 5 | 30.8 |
| aca_86 | `YYYXXXXXyyX`, `YYXyxxyyXYx` | 22 | dyn | 2000 | 218,933 | 19 | 6 | 43.9 |
| aca_87 | `YYXXXyXXX`, `YYXyxYXyxyx` | 20 | dyn | 2000 | 213,451 | 18 | 6 | 41.8 |
| aca_88 | `YYXXXyXX`, `YYxyXyxYXyx` | 19 | dyn | 2000 | 140,247 | 17 | 5 | 28.3 |
| aca_89 | `YXXYxxyx`, `YYYYYYYXyyyyyyx` | 23 | dyn | 2000 | 387,465 | 19 | 6 | 69.8 |
| aca_90 | `YYXXXyxxx`, `YYXyxYXyxyX` | 20 | dyn | 2000 | 184,318 | 18 | 6 | 36.4 |
| aca_91 | `YXXXyxYx`, `YYYYYYYXyyyyyyx` | 23 | dyn | 2000 | 340,114 | 20 | 6 | 62.4 |
| aca_92 | `YXyXYxxx`, `YYYYYYYXyyyyyyx` | 23 | dyn | 2000 | 394,592 | 20 | 6 | 74.3 |
| aca_93 | `YXXXyxYx`, `YYYYYYYxyyyyyyX` | 23 | dyn | 2000 | 276,834 | 19 | 6 | 54.9 |
| aca_94 | `YXXXYxYx`, `YYYYYYYXyyyyyyx` | 23 | dyn | 2000 | 345,920 | 20 | 6 | 64.7 |
| aca_95 | `YYXXXyxx`, `YYxyxyXYxyX` | 19 | dyn | 2000 | 241,662 | 17 | 5 | 41.9 |
| aca_96 | `YXXYxxyX`, `YYYYYYYXyyyyyyx` | 23 | dyn | 2000 | 389,122 | 19 | 6 | 69.2 |
| aca_97 | `YXXyxYx`, `YYYYYYYXyyxx` | 19 | dyn | 2000 | 154,190 | 18 | 5 | 32.2 |
| aca_98 | `YXyXYxx`, `YYYYYYYXXYYx` | 19 | dyn | 2000 | 149,984 | 18 | 6 | 31.4 |
| aca_99 | `YYXXyxx`, `YYYxyXyxyXyX` | 19 | dyn | 2000 | 238,975 | 17 | 6 | 43.6 |
| aca_100 | `YYXXXXyxx`, `YYXyxyXYxyX` | 20 | dyn | 2000 | 210,274 | 18 | 6 | 39.0 |
| aca_101 | `YXXXYxYx`, `YYYYYYYYXyyyyyyyx` | 25 | dyn | 2000 | 315,007 | 20 | 6 | 59.9 |
| aca_102 | `YXXXyxYx`, `YYYYYYYYxyyyyyyyX` | 25 | dyn | 2000 | 255,200 | 20 | 6 | 52.1 |
| aca_103 | `YXyXYxxx`, `YYYYYYYYXyyyyyyyx` | 25 | dyn | 2000 | 224,715 | 20 | 6 | 47.9 |
| aca_104 | `YXXXyxYx`, `YYYYYYYYXyyyyyyyx` | 25 | dyn | 2000 | 256,703 | 20 | 6 | 52.8 |
| aca_105 | `YYXXXXyxxx`, `YYXyXyxYXyx` | 21 | dyn | 2000 | 244,406 | 19 | 6 | 46.8 |
| aca_106 | `YYXXXXyXXX`, `YYXyxyXYxyX` | 21 | dyn | 2000 | 216,253 | 20 | 6 | 44.7 |
| aca_107 | `YXXyXYxxx`, `YYYYYYYXXXYxx` | 22 | dyn | 2000 | 267,251 | 20 | 6 | 53.4 |
| aca_108 | `YXYXyxyXYxx`, `YYYYYYYxYYXYx` | 24 | dyn | 2000 | 177,431 | 21 | 6 | 40.5 |
| aca_109 | `YYXXyxYxxyX`, `YYYYYYXXXYxx` | 23 | dyn | 2000 | 214,890 | 20 | 6 | 44.5 |
| aca_110 | `YXXXyxYxx`, `YYYYYYYXXyxxx` | 22 | dyn | 2000 | 274,563 | 20 | 6 | 52.8 |
| aca_111 | `YXYXYxxyXyx`, `YYYYYYYxyXyyx` | 24 | dyn | 2000 | 178,104 | 21 | 6 | 41.6 |
| aca_112 | `YXYxxyXYXyx`, `YYYYYYYxyyXYx` | 24 | dyn | 2000 | 171,587 | 21 | 6 | 39.8 |
| aca_113 | `YXXXyxYxx`, `YYYYYYYYXXXYxx` | 23 | dyn | 2000 | 271,659 | 20 | 6 | 50.8 |
| aca_114 | `YXXyXYxxx`, `YYYYYYYYXXyxxx` | 23 | dyn | 2000 | 270,803 | 20 | 6 | 52.1 |
| aca_115 | `YXYxyx`, `YYYYxxx` | 13 | dyn | 2000 | 290,792 | 13 | 5 | 39.8 |
| aca_116 | `YYYXyyX`, `YXXXyxx` | 14 | dyn | 2000 | 136,577 | 14 | 5 | 23.5 |
| aca_117 | `YYYXyyx`, `YXXXyxx` | 14 | dyn | 2000 | 195,202 | 14 | 5 | 31.6 |
| aca_118 | `YXXyxYx`, `YYYYXyxx` | 15 | dyn | 2000 | 222,182 | 15 | 5 | 32.4 |
| aca_119 | `YXXyxYx`, `YYYYYXyxx` | 16 | dyn | 2000 | 159,742 | 16 | 5 | 26.8 |
| aca_120 | `YXXyxYx`, `YYYXyyxx` | 15 | dyn | 2000 | 218,253 | 15 | 5 | 34.5 |
| aca_121 | `YXyXYxx`, `YYYXXYYx` | 15 | dyn | 2000 | 216,742 | 15 | 5 | 33.9 |
| aca_122 | `YXyXYxx`, `YYYYXXYYx` | 16 | dyn | 2000 | 219,719 | 16 | 5 | 37.7 |
| aca_123 | `YXyXYxx`, `YYYYYXXYYx` | 17 | dyn | 2000 | 185,644 | 17 | 5 | 35.2 |

## Separation: U124 vs solved ladder rows under the same arm and budget

AUC = probability that a U124 row scores above a solved row (0.5 = no separation).

| arm | feature | AUC vs all solved | AUC vs solved bins 6-9 | mean U124 | mean solved | mean solved 6-9 |
|---|---|---:|---:|---:|---:|---:|
| dyn | unsolved at budget (1/0) | 0.8500 | 0.7083 | 1.00 | 0.30 | 0.58 |
| dyn | pops used | 0.8500 | 0.7083 | 2000.00 | 813.32 | 1475.54 |
| dyn | min total length / L | 0.9997 | 1.0000 | 0.92 | 0.22 | 0.42 |
| dyn | min total length | 0.9060 | 0.7878 | 17.37 | 4.90 | 9.71 |
| dyn | states | 0.8300 | 0.6405 | 235666.70 | 98063.08 | 190713.08 |
| dyn | max rank | 0.7151 | 0.4866 | 5.56 | 4.87 | 5.58 |
| dyn | root length L | 0.4501 | 0.1136 | 19.00 | 19.32 | 23.04 |

### Threshold on `min total length / L` (arm `dyn`)

| threshold t | solved rows with ratio < t (of 60) | solved bins 6-9 with ratio < t (of 24) | U124 rows with ratio < t (of 124) |
|---:|---:|---:|---:|
| 0.70 | 47 | 15 | 0 |
| 0.75 | 53 | 21 | 0 |
| 0.78 | 56 | 24 | 0 |
| 0.80 | 59 | 24 | 0 |
| 0.81 | 60 | 24 | 5 |
| 0.85 | 60 | 24 | 12 |
| 0.90 | 60 | 24 | 46 |
| 1.00 | 60 | 24 | 96 |

U124 ratio range: 0.800 .. 1.000; solved-ladder ratio range: 0.000 .. 0.800 (unsolved solved-ladder rows only: 0.680 .. 0.800).

U124 shortening `L - min total length` histogram: 0: 28, 1: 29, 2: 40, 3: 19, 4: 4, 5: 4
