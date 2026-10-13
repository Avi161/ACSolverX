# CoV sweep summary: `cov_all_suballpxyb8_ms640_b10000.jsonl`

Budget 10,000 nodes; 640 presentations, 114,042 CoV starts + 640 controls; 49.767 CPU-hours of search (sum of `time_seconds`).

Every statistic is computed per presentation, then aggregated across presentations. Oracle arms presume knowing the best start. CoV path lengths are in transformed coordinates (stable AC, not an AC path of the original).

Total nodes over all CoV starts per presentation (the oracle's real cost): mean 164,758.7, median 2,001.5, max 7,847,894.

## Budget 100

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 455 | 15.76 / 8 | 7.62 / 7 | 15.76 / 8 | 7.62 / 7 |
| oracle_all | 555 | 9.63 / 5 | 6.22 / 4 | 5.71 / 4 | 4.3 / 3 |
| oracle_one | 555 | 9.66 / 5 | 6.26 / 4 | 5.76 / 4 | 4.35 / 3 |

Shared solved set: 455 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 26.2%, equal 9.5%, dearer 31.6%, fails 32.7%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 19.

## Budget 1,000

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 554 | 65.36 / 9.0 | 12.09 / 8.0 | 65.36 / 9.0 | 12.09 / 8.0 |
| oracle_all | 604 | 35.47 / 6.0 | 10.5 / 5.0 | 13.68 / 5.0 | 6.96 / 4.0 |
| oracle_one | 604 | 35.5 / 6.5 | 10.53 / 5.5 | 13.72 / 5.0 | 6.99 / 4.0 |

Shared solved set: 554 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 30.9%, equal 9.6%, dearer 41.8%, fails 17.7%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 19.

## Budget 10,000

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 606 | 389.53 / 10.0 | 19.97 / 8.0 | 389.53 / 10.0 | 19.97 / 8.0 |
| oracle_all | 626 | 152.22 / 7.0 | 15.72 / 6.0 | 85.99 / 6.0 | 12.84 / 5.0 |
| oracle_one | 626 | 152.26 / 7.0 | 15.76 / 6.0 | 86.02 / 7.0 | 12.87 / 6.0 |

Shared solved set: 606 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 33.0%, equal 9.6%, dearer 48.2%, fails 9.2%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 19.

