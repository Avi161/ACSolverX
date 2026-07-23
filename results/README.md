# `results/`

Every artifact any experiment has produced. Each directory has a different job.

| directory | what it holds | produced by |
|---|---|---|
| **`greedy_baseline/`** | the raw baseline runs — 10 `.jsonl`, one per (budget, dataset) | `experiments/run_baseline.py`, on Colab |
| **`benchmark/`** | the stable-AC benchmark: difficulty ladder + reach tier + `combined/` | `experiments/analysis/*.py` |
| **`stable_ac/nocov/`** | Branch-A (No-CoV) sweep jsonl, one per `(benchmark, family, budget)` | `experiments/stable_ac/nocov/run_nocov.py` |
| **`stable_ac/cov/`** | Branch-B (one-shot CoV) jsonl, one per budget, `cov` + `covbase` modes | `experiments/stable_ac/cov/run_cov.py` |
| **`stable_ac/mu_scan/`** | the orbit-floor μ-ladder: depth-2 descent map, the rung ladders, `MU_SCAN_FINDINGS.md` | `experiments/stable_ac/cov/{mu_descent_scan,mu_ladder}.py` |
| **`stable_ac/mitm/`** | Aut-quotient meet-in-the-middle vs TRIVIAL, one jsonl per length ceiling | `experiments/stable_ac/cov/run_mitm_aut.py` |
| **`stable_ac/theory/`** | proved/refuted notes from the escape push (μ criterion, MS template, orbit floors) | written by hand, ac-advisor reviewed |
| **`stable_ac/IDEA_BENCH_RESULTS.md`** | the 16-strategy start-transform race on combined_22 — evidence kept, [producer pruned](../PRUNED.md) | ⚠ `experiments/stable_ac/idea_bench/`, removed |
| **`equivalence_classes/`** | the 261 unsolved reps are really **126 distinct problems** — and the proof | `experiments/equivalence_classes/` |
| **`graphs/`** | two baseline curves + the difficulty ranking | ⚠ no producer script in the repo |

---

## `greedy_baseline/` — do not rename anything in here

This is a **live pipeline contract**, not just a folder of data.

`run_baseline.py` hardcodes `LOCAL_OUT_DIR = "results/greedy_baseline"` and *globs* the directory to
find a run to resume (`_resolve_paths`). `experiments/analysis/difficulty_bins.py` does a
non-recursive `os.listdir` on it. **Moving a `.jsonl` into a subfolder does not raise** — resume
silently concludes no prior run exists and starts a fresh one. The 1M-budget run over the 261 reps
alone is days of compute.

Filenames are the resume key:
`greedy_<budget>_<n_pres>_mrl<cap>_<cyc|noncyc>_<subset>_<mm_dd_yy>.jsonl`. The date is deliberately
**not** part of the key (see `experiments/lessons/date-in-filename-broke-resume.md`), which is why the
nine 640-runs carry three different dates.

All ten files are live. A budget-`B` run is exactly the first `B` pops of any longer run, so the small
budgets are not superseded drafts of the big one — each is a distinct point on the anytime
solve-rate curve. `greedy_1000000_640_…` is the one `difficulty_bins.py` treats as ground truth: all
640 solve there, so nothing is censored.

> ⚠ **No `*_paths.jsonl` companions are present**, although `run_baseline.py` defaults to writing them
> (`use_path`, `PATH_IN_SEPARATE_FILE`). They may exist only on Drive. Unresolved.

## `benchmark/`

`difficulty_bins.csv` labels all 640 presentations with a log-width difficulty bin. `subsets/` holds
the efficiency ladder (10/20/40/60), `reach/` the unsolved tier (1/2/4/6). All three regenerate from
the baseline jsonl and the class table — and are checked by regenerating them and requiring a zero
diff.

`combined/` merges the two into what a technique actually runs on: `benchmark_combined_{11,22,44,66}`
= subset_10+reach_1 … subset_60+reach_6. Ladder rows (solved, `source: "ladder"`) score speedup
ratios; reach rows (unsolved, `source: "reach"`) score `solved`/`bar_to_beat` and never enter a
ratio. Produced by `experiments/analysis/combined_benchmark.py`.

> **Certificates:** every `solved: true` row in `stable_ac/` is a claim whose proof is its move
> path. `.venv/bin/python3 -m experiments.stable_ac.verify_results` replays all of them through the
> pure-Python spec (independent of every solver) and checks budget invariance across files.
> Standing count: **ALL 399 SOLVED-ROW CERTIFICATES VERIFY** (2,680 rows, 8 files, 2026-07-13).
> Rows carry `git_commit` — the code that produced them. Run the verifier before believing any run.

## `stable_ac/nocov/`

Branch-A sweep results. Filename = the resume key:
`nocov_<benchmark>_<family>_<budget>_mrl<cap>_<cyc|noncyc>_<mm_dd_yy>.jsonl` (date not part of the
key, same rule as `greedy_baseline/`). One row per `(presentation, z_word)`; solved paths go to the
`*_paths.jsonl` sibling as replayable move strings. Budget-100/1000 files are local pipeline
verification, not production data.

`old_benchmark/` holds every nocov run produced against the pre-automorphism-minimisation benchmark
(archived 2026-07-16). Those rows are still valid certificates and the verifier still replays them,
but their `pres_id`s index the old CSVs — never compare them against a new-benchmark run. Fresh runs
write to `nocov/` itself, so resume never reaches back into the archive.

## `stable_ac/cov/`

Branch-B (one-shot change of variables) results. Filename = the resume key:
`cov_<budget>_<n_rows>_<zfam>_mrl<cap>_<cyc|noncyc>_<datasets>_<mm_dd_yy>.jsonl` (`covbase_…` = the
identity-transform comparison runs; date not part of the key). Produced by
`experiments/stable_ac/cov/run_cov.py`.

## `equivalence_classes/`

The shipped result and every piece of evidence behind it. See its own `README.md`.

## `graphs/`

⚠ **No script in the repo produces these.** They were made ad hoc. `difficulty_ranking.csv` (the 640
sorted by `(nodes_explored, path_length, pres_id)`) is superseded by `benchmark/difficulty_bins.csv`,
which carries the same ranking as its `difficulty_rank` column, plus the bin, the Aut class, and the
50k columns. Prefer the latter.
