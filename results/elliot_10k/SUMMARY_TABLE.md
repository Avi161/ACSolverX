| benchmark | method | rows | solved @1e3 | solved @1e4 | stable_cert | nodes mean / median / max (solved) | nodes total (fail = budget) | path mean / median / max | S-moves mean | CoV moves mean / max | max relator len mean / max | max total len max | pruned | errors |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ms640 | Dual (sub + single CoV) | 640 | 604 | 627 | 0 | 205.1 / 10 / 8,602 | 258,619 | 25.6 / 9 / 825 | 24.0 | 1.61 / 10 | 9.9 / 19 | 25 | 0 | 0 |
| ms640 | Dual (sub + auto CoV) | 640 | 618 | 634 | 0 | 170.8 / 10 / 7,537 | 168,283 | 35.6 / 9 / 939 | 34.3 | 1.24 / 10 | 10.0 / 19 | 25 | 0 | 0 |
| ms640 | Triple (sub + auto + complete CoV) | 640 | 618 | 634 | 54 | 171.1 / 10 / 7,548 | 168,486 | 35.6 / 9 / 939 | 34.3 | 1.29 / 10 | 10.0 / 19 | 25 | 0 | 0 |
| bench60 | Dual (sub + single CoV) | 60 | 46 | 52 | 0 | 565.4 / 156 / 4,340 | 109,400 | 52.3 / 38 / 280 | 49.0 | 3.29 / 10 | 11.9 / 17 | 25 | 0 | 0 |
| bench60 | Dual (sub + auto CoV) | 60 | 51 | 56 | 0 | 609.0 / 155 / 5,571 | 74,106 | 106.3 / 37 / 778 | 103.8 | 2.55 / 9 | 12.4 / 19 | 25 | 0 | 0 |
| bench60 | Triple (sub + auto + complete CoV) | 60 | 51 | 56 | 7 | 606.7 / 156 / 5,579 | 73,977 | 106.2 / 36 / 778 | 103.6 | 2.61 / 8 | 12.4 / 19 | 25 | 0 | 0 |
| ladder100 | Dual (sub + single CoV) | 100 | 64 | 92 | 0 | 1,142.6 / 508 / 6,292 | 185,119 | 65.2 / 55 / 308 | 58.9 | 6.33 / 22 | 13.2 / 19 | 25 | 0 | 0 |
| ladder100 | Dual (sub + auto CoV) | 100 | 80 | 97 | 0 | 819.7 / 277 / 5,972 | 109,511 | 97.0 / 55 / 778 | 91.3 | 5.66 / 18 | 13.4 / 19 | 25 | 0 | 0 |
| ladder100 | Triple (sub + auto + complete CoV) | 100 | 86 | 97 | 17 | 660.8 / 266 / 5,579 | 94,099 | 95.9 / 52 / 778 | 90.3 | 5.59 / 19 | 13.4 / 19 | 25 | 0 | 0 |
