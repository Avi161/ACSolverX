# CoV sweep summary: `cov_all_suballpxyb8_ms640_b100.jsonl`

Budget 100 nodes; 640 presentations, 114,042 CoV starts + 640 controls; 1.086 CPU-hours of search (sum of `time_seconds`).

Every statistic is computed per presentation, then aggregated across presentations. Oracle arms presume knowing the best start. CoV path lengths are in transformed coordinates (stable AC, not an AC path of the original).

Total nodes over all CoV starts per presentation (the oracle's real cost): mean 5,328.4, median 1,371.5, max 173,997.

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

