# Control vs a random 3-generator start: `rank3_bf_ms640_b10000_cap24_control_vs_start_L1-7`

Budget 10,000; 640 presentations, 2,186 starts each (<x,y,z | r1, r2, Z·w> for every word w of lengths 1 to 7; 1,399,040 searches); every presentation weighted equally. A start with an unsolved control counts as having fewer nodes when it solves. Control solved: 606 of 640.

| control's nodes | presentations | fewer nodes than the control | same nodes | more nodes than the control | start not solved within the budget | fewer by more than 17% | more by more than 17% |
|---|---|---|---|---|---|---|---|
| 1 to 9 | 295 | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% | 98.9% |
| 10 to 99 | 159 | 1.6% | 0.1% | 97.6% | 0.7% | 1.0% | 96.2% |
| 100 to 999 | 100 | 1.6% | 0.0% | 59.2% | 39.1% | 1.2% | 58.6% |
| 1,000 to 9,999 | 52 | 1.9% | 0.0% | 4.7% | 93.4% | 1.6% | 4.2% |
| unsolved | 34 | 0.9% | 0.0% | 0.0% | 99.1% | 0.9% | 0.0% |
| all | 640 | 0.9% | 0.0% | 80.0% | 19.1% | 0.6% | 79.0% |

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
| 7 | 1,458 | 0.8% | 0.0% | 79.9% | 19.3% | 0.6% | 79.0% |
