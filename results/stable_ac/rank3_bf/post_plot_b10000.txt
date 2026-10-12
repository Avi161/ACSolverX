# Control vs a random 3-generator start: `rank3_bf_ms640_b10000_cap24_control_vs_start_L1-6`

Budget 10,000; 640 presentations, 728 starts each (<x,y,z | r1, r2, Z·w> for every word w of lengths 1 to 6; 465,920 searches); every presentation weighted equally. A start with an unsolved control counts as having fewer nodes when it solves. Control solved: 606 of 640.

| control's nodes | presentations | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 to 9 | 295 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 98.5% |
| 10 to 99 | 159 | 1.7% | 0.1% | 97.5% | 0.7% | 1.1% | 96.2% |
| 100 to 999 | 100 | 1.8% | 0.0% | 60.2% | 38.0% | 1.4% | 59.6% |
| 1,000 to 9,999 | 52 | 2.1% | 0.0% | 4.9% | 93.0% | 1.7% | 4.4% |
| unsolved | 34 | 1.1% | 0.0% | 0.0% | 98.9% | 1.1% | 0.0% |
| all | 640 | 0.9% | 0.0% | 80.1% | 18.9% | 0.7% | 79.0% |

## Per word length

The `all` row of the table above, for the starts of one word length at a time.

| word length | starts | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 0.0% | 0.0% | 71.5% | 28.5% | 0.0% | 42.3% |
| 2 | 6 | 1.1% | 0.1% | 79.0% | 19.8% | 0.8% | 75.1% |
| 3 | 18 | 0.6% | 0.0% | 80.1% | 19.3% | 0.3% | 77.4% |
| 4 | 54 | 1.3% | 0.0% | 80.5% | 18.2% | 1.0% | 79.2% |
| 5 | 162 | 1.1% | 0.0% | 80.3% | 18.6% | 0.8% | 78.1% |
| 6 | 486 | 0.9% | 0.0% | 80.0% | 19.0% | 0.6% | 79.5% |
