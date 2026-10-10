# Exhaustive CoV sweep (`suballpxyb8`) on MS640

The baseline greedy (`run_baseline.greedy_search`, unchanged) is run from the untransformed
presentation (control, cap 24) and from every distinct change-of-variables class of
`experiments/stable_ac/cov/cov_all.py` (cap `res.cap`), one row per start, for all 640 rows of
`data/ms640_solved.txt` (`pres_id` = 0-based line; subset 60's `pres_id`s are the same rows).

| file | what |
|---|---|
| `cov_all_suballpxyb8_ms640_b100.jsonl.gz` | budget 100 smoke: 114,682 rows (640 controls + 114,042 CoV), every solved path stored as `path_moves` |
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
