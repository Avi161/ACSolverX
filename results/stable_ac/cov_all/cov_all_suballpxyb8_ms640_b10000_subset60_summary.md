# CoV sweep summary: `cov_all_suballpxyb8_ms640_b10000_subset60.jsonl`

Budget 10,000 nodes; 60 presentations, 9,105 CoV starts + 60 controls; 19.751 CPU-hours of search (sum of `time_seconds`).

Every statistic is computed per presentation, then aggregated across presentations. Oracle arms presume knowing the best start. CoV path lengths are in transformed coordinates (stable AC, not an AC path of the original).

Total nodes over all CoV starts per presentation (the oracle's real cost): mean 705,835.3, median 146,384.0, max 7,847,894.

## Budget 100

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 17 | 28.47 / 13 | 10.94 / 9 | 28.47 / 13 | 10.94 / 9 |
| oracle_all | 34 | 16.12 / 12.5 | 10.12 / 9.5 | 7.88 / 8 | 5.88 / 7 |
| oracle_one | 34 | 16.15 / 12.5 | 10.15 / 9.5 | 7.94 / 8 | 5.94 / 7 |

Shared solved set: 17 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 13.5%, equal 2.1%, dearer 12.4%, fails 72.0%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 1.

## Budget 1,000

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 29 | 175.52 / 61 | 19.21 / 16 | 175.52 / 61 | 19.21 / 16 |
| oracle_all | 45 | 103.62 / 17 | 23.2 / 12 | 13.97 / 10 | 8.69 / 8 |
| oracle_one | 45 | 103.64 / 17 | 23.22 / 12 | 14 / 10 | 8.72 / 8 |

Shared solved set: 29 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 25.5%, equal 2.2%, dearer 18.4%, fails 53.9%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 1.

## Budget 10,000

| arm | solved | nodes mean / median (own) | path mean / median (own) | nodes mean / median (shared) | path mean / median (shared) |
|---|---|---|---|---|---|
| control | 40 | 1205.67 / 197.0 | 36.88 / 24.0 | 1205.67 / 197.0 | 36.88 / 24.0 |
| oracle_all | 52 | 543.35 / 25.0 | 36.5 / 14.5 | 72.17 / 14.0 | 19.32 / 11.0 |
| oracle_one | 52 | 543.37 / 25.0 | 36.52 / 14.5 | 72.2 / 14.0 | 19.35 / 11.0 |

Shared solved set: 40 presentations.
A single random CoV start vs the control (mean over presentations): cheaper 34.0%, equal 2.2%, dearer 26.8%, fails 37.1%.
Solved only through a start that is NOT one-pattern (control and one-pattern oracle both fail): 0.
Presentations where the full family's oracle beats the one-pattern oracle (solves it or uses fewer nodes): 1.

