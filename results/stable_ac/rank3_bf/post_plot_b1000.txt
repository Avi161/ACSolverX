# Control vs a random 3-generator start: `rank3_bf_ms640_b1000_cap24_control_vs_start_L1-10`

Budget 1,000; 640 presentations, 59,048 starts each (<x,y,z | r1, r2, Z·w> for every word w of lengths 1 to 10; 37,790,720 searches); every presentation weighted equally. A start with an unsolved control counts as having fewer nodes when it solves. Control solved: 554 of 640.

| control's nodes | presentations | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 to 9 | 295 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 99.9% |
| 10 to 99 | 159 | 1.3% | 0.1% | 71.4% | 27.3% | 0.7% | 70.5% |
| 100 to 999 | 100 | 1.3% | 0.0% | 9.2% | 89.5% | 0.9% | 8.6% |
| unsolved | 86 | 0.1% | 0.0% | 0.0% | 99.9% | 0.1% | 0.0% |
| all | 640 | 0.5% | 0.0% | 65.3% | 34.2% | 0.3% | 64.9% |

## Per word length

The `all` row of the table above, for the starts of one word length at a time.

| word length | starts | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 0.0% | 0.0% | 60.1% | 39.9% | 0.0% | 30.9% |
| 2 | 6 | 1.1% | 0.1% | 67.2% | 31.6% | 0.8% | 63.3% |
| 3 | 18 | 0.6% | 0.0% | 69.2% | 30.2% | 0.3% | 66.6% |
| 4 | 54 | 1.1% | 0.0% | 67.4% | 31.4% | 0.8% | 66.2% |
| 5 | 162 | 0.9% | 0.0% | 66.5% | 32.7% | 0.6% | 64.3% |
| 6 | 486 | 0.7% | 0.0% | 66.1% | 33.2% | 0.4% | 65.6% |
| 7 | 1,458 | 0.6% | 0.0% | 65.9% | 33.5% | 0.4% | 64.9% |
| 8 | 4,374 | 0.6% | 0.0% | 65.6% | 33.8% | 0.4% | 65.2% |
| 9 | 13,122 | 0.5% | 0.0% | 65.3% | 34.1% | 0.3% | 64.9% |
| 10 | 39,366 | 0.5% | 0.0% | 65.2% | 34.3% | 0.3% | 64.9% |
