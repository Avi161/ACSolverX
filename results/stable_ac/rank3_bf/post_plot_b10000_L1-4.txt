# Control vs a random 3-generator start: `rank3_bf_ms640_b10000_cap24_control_vs_start_L1-4`

Budget 10,000; 640 presentations, 80 starts each (<x,y,z | r1, r2, Z·w> for every word w of lengths 1 to 4; 51,200 searches); every presentation weighted equally. A start with an unsolved control counts as having fewer nodes when it solves. Control solved: 606 of 640.

| control's nodes | presentations | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 to 9 | 295 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 95.7% |
| 10 to 99 | 159 | 2.3% | 0.1% | 97.2% | 0.4% | 1.6% | 95.6% |
| 100 to 999 | 100 | 2.4% | 0.0% | 60.0% | 37.5% | 1.8% | 59.3% |
| 1,000 to 9,999 | 52 | 1.5% | 0.0% | 5.1% | 93.3% | 1.2% | 5.0% |
| unsolved | 34 | 0.7% | 0.0% | 0.0% | 99.3% | 0.7% | 0.0% |
| all | 640 | 1.1% | 0.0% | 80.1% | 18.8% | 0.8% | 77.6% |

## Per word length

The `all` row of the table above, for the starts of one word length at a time.

| word length | starts | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 0.0% | 0.0% | 71.5% | 28.5% | 0.0% | 42.3% |
| 2 | 6 | 1.1% | 0.1% | 79.0% | 19.8% | 0.8% | 75.1% |
| 3 | 18 | 0.6% | 0.0% | 80.1% | 19.3% | 0.3% | 77.4% |
| 4 | 54 | 1.3% | 0.0% | 80.5% | 18.2% | 1.0% | 79.2% |
