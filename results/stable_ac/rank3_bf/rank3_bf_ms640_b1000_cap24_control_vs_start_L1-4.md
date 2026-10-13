# Control vs a random 3-generator start: `rank3_bf_ms640_b1000_cap24_control_vs_start_L1-4`

Budget 1,000; 640 presentations, 80 starts each (<x,y,z | r1, r2, Z·w> for every word w of lengths 1 to 4; 51,200 searches); every presentation weighted equally. A start with an unsolved control counts as having fewer nodes when it solves. Control solved: 554 of 640.

| control's nodes | presentations | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 to 9 | 295 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 95.7% |
| 10 to 99 | 159 | 2.3% | 0.1% | 79.2% | 18.5% | 1.6% | 77.5% |
| 100 to 999 | 100 | 2.4% | 0.0% | 12.1% | 85.5% | 1.8% | 11.3% |
| unsolved | 86 | 0.1% | 0.0% | 0.0% | 99.9% | 0.1% | 0.0% |
| all | 640 | 1.0% | 0.0% | 67.6% | 31.4% | 0.7% | 65.2% |

## Per word length

The `all` row of the table above, for the starts of one word length at a time.

| word length | starts | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 0.0% | 0.0% | 60.1% | 39.9% | 0.0% | 30.9% |
| 2 | 6 | 1.1% | 0.1% | 67.2% | 31.6% | 0.8% | 63.3% |
| 3 | 18 | 0.6% | 0.0% | 69.2% | 30.2% | 0.3% | 66.6% |
| 4 | 54 | 1.1% | 0.0% | 67.4% | 31.4% | 0.8% | 66.2% |
