# Exhaustive CoV sweep (`suballpxyb8`) on MS640

The baseline greedy (`run_baseline.greedy_search`, unchanged) is run from the untransformed
presentation (control, cap 24) and from every distinct change-of-variables class of
`experiments/stable_ac/cov/cov_all.py` (cap `res.cap`), one row per start, for all 640 rows of
`data/ms640_solved.txt` (`pres_id` = 0-based line; subset 60's `pres_id`s are the same rows).

| file | what |
|---|---|
| `cov_all_suballpxyb8_ms640_b100.jsonl.gz` | budget 100 smoke: 114,682 rows (640 controls + 114,042 CoV), every solved path stored as `path_moves` |
| `cov_all_suballpxyb8_ms640_b10000.jsonl.gz` | budget 10,000: the same 114,682 rows; `path_moves` kept on a 2% hash sample of solved rows (`--path-sample 0.02`), every other row keeps `path_length` and `nodes_explored` only |
| `cov_all_suballpxyb8_ms640_b10000_subset60_summary.*` | the budget 10,000 statistics restricted to subset 60's 60 `pres_id`s (their rows are in the b10000 file) |
| `*_summary.md` / `*_summary.json` | per-presentation statistics aggregated across presentations (`summarize_cov_all`) |
| `*.log` | runner log: start, enumeration, progress, wall time |

Each row records how its start was made from the original: `z_word`, `pattern` (chosen
occurrences `[start, ±1]` of w / w⁻¹ in the cyclically reduced r1 and r2), the substituted pair
(`r1_substituted`, `r2_substituted`, generator 3 = z), `defining_relator` (Z·w), `iso_gen`
(eliminated generator), `iso_index` (0 = solved from r1′, 1 = from r2′) and `iso_expr`.
Path lengths of CoV rows are in transformed coordinates: a solve certifies stable AC-triviality.

Reproduce / check (repo root, `PYTHONPATH=.`, gunzip first):

    python3 -m experiments.stable_ac.cov.run.run_cov_all --budget 100 --workers N --path-sample 1
    python3 -m experiments.stable_ac.cov.verify.verify_cov_all FILE.jsonl --counts --dataset data/ms640_solved.txt --path-sample 1
    python3 -m experiments.stable_ac.cov.run.summarize_cov_all FILE.jsonl

Budget 100 check: 114,682 rows, 14,051 one-pattern, 90,234 solved, 90,234 paths replayed through
`greedy_tests/spec` to the trivial presentation, 0 failures.

Budget 10,000 check (64 workers on a c7a.16xlarge, code at `99968da`): 114,682 rows, 14,051
one-pattern, 106,843 solved, 2,147 sampled paths replayed to the trivial presentation, 0 failures,
on the box and again on the downloaded file (`--counts --dataset data/ms640_solved.txt
--path-sample 0.02`). Every row solved within 100 nodes has the same `nodes_explored` and
`path_length` as in the budget 100 file. Search wall time 47.5 min (19.0 for subset 60 first,
28.5 for the other 580 presentations), 49.8 CPU-hours.

Presentations solved (of 640; subset 60 in brackets), oracle = best start of the family:

| budget | control | oracle, all starts | oracle, one-pattern starts |
|---|---|---|---|
| 100 | 455 (17) | 555 (34) | 555 (34) |
| 1,000 | 554 (29) | 604 (45) | 604 (45) |
| 10,000 | 606 (40) | 626 (52) | 626 (52) |

No presentation changes outcome because of a start outside the one-pattern set, at any budget; on
19 presentations the best such start is 1 or 2 nodes cheaper than the best one-pattern start. At
10,000 the 20 presentations solved only from a CoV start are `pres_id` 568, 570, 573, 575, 578,
583, 584, 588, 596, 603, 604, 605, 610, 613, 628, 629, 630, 633, 634, 635, and the 14 no start
solves are 616-625 and 636-639. Subset 60 is `pres_id` 0, 43, 48, 77, 141, 155, 201, 203, 217,
228, 247, 265, 288, 323, 327, 331, 333, 367, 380, 455, 496, 505, 521, 533, 538, 543, 544, 546,
548, 549, 565, 568, 573, 575, 578-581, 583, 586, 589, 596, 602, 605, 606, 609, 610, 622-625, 628,
632-639.
