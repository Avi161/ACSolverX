# `results/`

Every artifact any experiment has produced. Each directory has a different job.

> The frozen evaluation set moved out of here to [`benchmark/`](../benchmark/README.md) at the repo root. It is *derived* from `greedy_baseline/` but *consumed* as an input by roughly two dozen files, and living under `results/` hid that.

| directory | what it holds | produced by |
|---|---|---|
| **`greedy_baseline/`** | the raw baseline runs — 10 `.jsonl`, one per (budget, dataset) | `experiments/run_baseline.py`, on Colab |
| **`stable_ac/nocov/`** | Branch-A (No-CoV) sweep jsonl, one per `(benchmark, family, budget)` | `experiments/stable_ac/nocov/run_nocov.py` |
| **`stable_ac/cov/`** | Branch-B (one-shot CoV) jsonl, one per budget, `cov` + `covbase` modes | `experiments/stable_ac/cov/run/run_cov.py` |
| **`stable_ac/cov/graphs/`** | CoV-vs-baseline node comparison: `RESULTS.md`, `SUMMARY_b*.md`, `per_presentation*.csv`, `fig1_composition.png`, `fig2_distribution_correlation.png` | `experiments/stable_ac/cov/figures/{cov_summary,make_figs}.py` |
| **`stable_ac/mu_scan/`** | the orbit-floor μ-ladder: depth-2 descent map, the rung ladders, `MU_SCAN_FINDINGS.md` | `experiments/stable_ac/cov/ladder/{mu_descent_scan,mu_ladder}.py` |
| **`stable_ac/mitm/`** | Aut-quotient meet-in-the-middle vs TRIVIAL, one jsonl per length ceiling | `experiments/stable_ac/cov/run/run_mitm_aut.py` |
| **`stable_ac/cov/allcov_escape/`** | the whole subword-CoV family of the eight b10k-resistant rows, re-run at a higher budget; keyed by output pair, not presentation | `experiments/stable_ac/cov/escape/allcov_escalate.py` |
| **`comparison/`** | cross-arm tables: greedy vs best-CoV vs tuned heuristic at a matched budget | `experiments/heuristic_search/runners/three_way_b10k.py` |
| **`stable_ac/theory/`** | proved/refuted notes from the escape push (μ criterion, MS template, orbit floors) | written by hand, ac-advisor reviewed |
| **`stable_ac/IDEA_BENCH_RESULTS.md`** | the 16-strategy start-transform race on combined_22 — evidence kept, [producer pruned](../PRUNED.md) | ⚠ `experiments/stable_ac/idea_bench/`, removed |
| **`stable_ac/ak3/`** | the AK(3) universal test: two certificates, the sweep jsonl, `RESULTS.md` | `experiments/stable_ac/cov/ak3/` |
| **`equivalence_classes/`** | the 261 unsolved reps are really **124 distinct problems** — and the proof (`verify_proofs.py` asserts that exact count; 125/126/168 answer different questions — see [`data/README.md`](../data/README.md)) | `experiments/equivalence_classes/` |
| **`superseded/`** | artifacts kept for provenance only, never cited — see `superseded/README.md` | — |

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

> **Certificates:** every `solved: true` row in `stable_ac/` is a claim whose proof is its move
> path. `.venv/bin/python3 -m experiments.stable_ac.verify_results` replays all of them through the
> pure-Python spec (independent of every solver) and checks budget invariance across files.
> Standing count: **ALL 9,836 SOLVED-ROW CERTIFICATES VERIFY** (41,793 rows, 12 files, 2026-07-24), plus budget-invariance across 6,608 jobs seen at more than one budget, 0 violations.
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
`experiments/stable_ac/cov/run/run_cov.py`.

`allcov_escape/` is a different shape and a different key: one jsonl per budget over the whole subword-CoV family of the eight benchmark rows that resist every CoV at 10,000 nodes, **deduplicated by output pair** rather than by presentation (909 distinct pairs from 1,366 starts), so the resume key is `(r1, r2)` and the owning presentations ride along in each row's `provenance`. All eight escape at budget 20,000 — [`ESCAPE.md`](stable_ac/cov/allcov_escape/ESCAPE.md) has the table and the gates behind it. Produced by `experiments/stable_ac/cov/escape/allcov_escalate.py`, analysed by `allcov_escape_report.py`.

## `comparison/`

Cross-arm tables that no single runner produces. `three_way_b10k_subset60.csv` is greedy vs best-CoV vs the tuned heuristic at a matched budget (10,000) and matched cap (24) over the 60-row benchmark, written by `experiments/heuristic_search/runners/three_way_b10k.py` — which refuses to write unless its length-only control reproduces the greedy column pop for pop on all 60 rows. `nodes_comparison_subset60.csv` joins the 1M-budget greedy and 100k heuristic runs to the b10k CoV table; its trailing rows are aggregates, not presentations, so filter on a numeric `pres_id`.

`cov_heur_b1k_subset60.csv` is the 2×2 of **transform × ordering** at budget 1,000, written by `experiments/heuristic_search/runners/cov_heur_b1k.py`: `{length-only, recommended}` × `{original pair, best-CoV pair}`, where the CoV is the winning `z` from the ≤20,000 sweep and its own per-row cap. It carries the transformed pair (`cov_r1`/`cov_r2`) and the full winner identity (`cov_z`, `cov_iso_gen`, `cov_iso_index`), so any row replays. Four gates, all fatal: the re-derived winner must equal the shipped best-CoV columns, both length-only arms must reproduce `covsweep_1000_66_*.jsonl` pop for pop — which is what proves the right winner row was identified — and no search may exceed the budget. Result on the controlled contrast (same transformed start, same cap, ordering the only difference): **43/60 for the combination against 45/60 for length-only** — 0 rows gained, 2 lost. The untransformed arms (29/60, 43/60) run at cap 24 against the CoV arms' 24–46 and are a reference, not a matched cell.

`greedy_vs_bestcov_subset60_nodes_path.csv` + [`GREEDY_VS_BESTCOV.md`](comparison/GREEDY_VS_BESTCOV.md) is the two-arm table on **both** axes — greedy at 1M against best CoV at ≤20,000, nodes *and* path length, 60/60 on each side. Best CoV is defined for all 60 without a new sweep because a search at budget `B` is the first `B` pops of a longer one, so a row that solved at 10,000 keeps its exact value; the builder asserts that on all 52 before writing.

**`nodes_comparison_subset60.png` was regenerated, and its producer is now committed** (`experiments/stable_ac/cov/figures/make_nodes_comparison_fig.py`). It is a **re-creation, not the original script** — the original was made ad hoc on Colab and was never in the repo, so fonts and tick placement differ from the superseded image. What changed in the data is one arm: best CoV used to draw `ms622`–`ms625` / `ms636`–`ms639` as hollow ✗ at the 10,000-node budget, and now solves 60/60 with those eight ringed at their real cost. Every other arm reproduces its previous mean and median exactly (greedy 45,244/1,310 · stdcov 26,130/70 · dualcov 9,754/438 · h-search base 10,977/610 · h-search reco 10,244/226), which is what makes the re-creation checkable. The eight on their own: [`escape_b20000_cost.svg`](stable_ac/cov/allcov_escape/escape_b20000_cost.svg).

## `equivalence_classes/`

The shipped result and every piece of evidence behind it. See its own `README.md`.

## `superseded/`

Artifacts kept for provenance, never for citation. `superseded/graphs/` (formerly a top-level
directory directly under `results/`) holds two baseline curves + `difficulty_ranking.csv`. ⚠ **No script in the repo produces these.** They
were made ad hoc. `difficulty_ranking.csv` (the 640 sorted by `(nodes_explored, path_length, pres_id)`)
is superseded by `benchmark/difficulty_bins.csv`, which carries the same ranking as its
`difficulty_rank` column, plus the bin, the Aut class, and the 50k columns. Prefer the latter. See
[`superseded/README.md`](superseded/README.md).
