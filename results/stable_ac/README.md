# `results/stable_ac/`

The evidence area for the stable-AC escape push: two search branches over the 2-generator greedy (Branch A "no change of variables" in `nocov/`, Branch B "one-shot change of variables" in `cov/`), plus everything built on top of Branch B once it became the productive direction — the CoV-vs-baseline analysis, the AK(3) universal-CoV experiment, the orbit-floor μ-ladder, the budget escalation on the eight CoV-resistant benchmark rows, and the theory notes that came out of reading the ladder's output. The top-level [`results/README.md`](../README.md) has one summary row per subdirectory here; this file expands each of them. The code-side map is [`experiments/stable_ac/README.md`](../../experiments/stable_ac/README.md) (`cov/` subpackage map: [`experiments/stable_ac/cov/README.md`](../../experiments/stable_ac/cov/README.md)). What this branch kept vs pruned from the prior `research/stable-ac-escape` push is [`PRUNED.md`](../../PRUNED.md).

| path | what it holds | produced by |
|---|---|---|
| **`nocov/`** | Branch-A sweep jsonl (resume key in the filename, see `results/README.md`); `old_benchmark/` archives every nocov run made against the pre-automorphism-minimisation benchmark (12 files, 6 jsonl + 6 `*_paths.jsonl`, archived 2026-07-16) | `experiments/stable_ac/nocov/run_nocov.py` |
| **`cov/` (top-level files)** | Branch-B sweep jsonl at 5 `(budget, subset)` points — `covsweep_100_11_*` (an 11-row pipeline check), `covsweep_100_66_*`, `covsweep_1000_66_*`, `covsweep_10000_66_*` (the 66-row benchmark at increasing budget), `covsweep_50000_124_*` (the 124 unsolved ACA classes); plus `greedy_vs_bestcov_subset60_b10000.csv` and `STABLE_ORBIT_LINKS.md` | `experiments/stable_ac/cov/run/run_cov.py`; `STABLE_ORBIT_LINKS.md` by `cov/ladder/orbit_links.py` |
| **`cov/graphs/`** | CoV-vs-baseline node-reduction analysis at three budgets | `experiments/stable_ac/cov/figures/{cov_summary,make_figs}.py` |
| **`cov/allcov_escape/`** | the eight CoV-resistant benchmark rows, re-run at budget 20,000 | `experiments/stable_ac/cov/escape/{allcov_escalate,allcov_escape_report}.py`, figure by `experiments/stable_ac/cov/figures/make_escape_fig.py` |
| **`mitm/`** | Aut-quotient meet-in-the-middle vs `TRIVIAL`, one jsonl per length ceiling (26, 28, 30) | `experiments/stable_ac/cov/run/run_mitm_aut.py` |
| **`mu_scan/`** | the orbit-floor μ toolchain's raw output and its findings write-up | `experiments/stable_ac/cov/ladder/{mu_descent_scan,mu_ladder,mu_ladder_big,mu_ladder_big_report}.py` |
| **`orbit_greedy/`** | pilot: run the baseline greedy from μ-ladder orbits instead of the original start | `experiments/stable_ac/cov/run/orbit_greedy.py` |
| **`ak3/`** | the AK(3) universal-CoV experiment — two certificates, the 390-search sweep, `RESULTS.md` | `experiments/stable_ac/cov/ak3/{sweep,census,analyze,certify,certify_classical,ball}.py` |
| **`theory/`** | five proved/refuted theory notes from the escape push | written by hand, ac-advisor reviewed |
| **`IDEA_BENCH_RESULTS.md`** | the 16-strategy start-transform race on `combined_22`; evidence kept, producer pruned | ⚠ `experiments/stable_ac/idea_bench/`, removed — see [`PRUNED.md`](../../PRUNED.md) |

---

## `nocov/`

Branch-A sweep results — one jsonl per `(benchmark, family, budget)`, filename = resume key (date not part of it, same rule as `greedy_baseline/`). Full walkthrough of the method and every knob: [`experiments/stable_ac/nocov/PIPELINE.md`](../../experiments/stable_ac/nocov/PIPELINE.md).

`old_benchmark/` holds every nocov run produced against the benchmark as it existed before automorphism minimisation. Those rows are still valid certificates — the verifier still replays them — but their `pres_id`s index the old CSVs, so never compare them against a run over the current benchmark. Fresh runs write to `nocov/` itself.

## `cov/`

Branch-B (one-shot change of variables) results. The method, worked examples and family-tag rules: [`experiments/stable_ac/cov/PIPELINE.md`](../../experiments/stable_ac/cov/PIPELINE.md). Filename = the resume key: `covsweep_<budget>_<n_rows>_subnc2pxysb_mrl<cap>_<cyc|noncyc>_<subset>_<mm_dd_yy>.jsonl`.

`greedy_vs_bestcov_subset60_b10000.csv` is a foundational join — greedy baseline vs best CoV at budget 10,000, per presentation, with `n_cov_tried`/`n_cov_solved`/`best_z`/`best_iso_gen`/`cov_min_path`/`flip` columns. It is read as an input by five downstream scripts (`experiments/stable_ac/cov/figures/rebuild_comparison_tables.py`, `experiments/stable_ac/cov/escape/allcov_escalate.py`, `experiments/stable_ac/cov/escape/allcov_escape_report.py`, `experiments/heuristic_search/runners/cov_heur_b1k.py`, `experiments/heuristic_search/runners/three_way_b10k.py`), but no script in this repo writes it — treat its origin as ad hoc, the same caveat `nodes_comparison_subset60.csv` carries below.

`STABLE_ORBIT_LINKS.md` unions the two large sweeps (`covsweep_50000_124_*`, `covsweep_10000_66_*`) by Aut(F₂)-orbit to look for **stable** equivalences among the 124 still-unsolved classes: none found among the 124 themselves, but the method has detection power — it collapses 15 of the 60 benchmark presentations into one stable component and confirms the eight budget-20,000-escape rows are a single problem in eight disguises.

## `cov/graphs/`

Three summaries of the same question — does a change of variables consistently reduce `nodes_explored` vs the untransformed baseline? — at three budgets, all generated from their matching `covsweep_*_66_*` jsonl: [`SUMMARY_b100.md`](cov/graphs/SUMMARY_b100.md), [`SUMMARY_b1000.md`](cov/graphs/SUMMARY_b1000.md), [`SUMMARY_b10000.md`](cov/graphs/SUMMARY_b10000.md) (`cov_summary.py`, also writing the matching `per_presentation_b*.csv`). [`RESULTS.md`](cov/graphs/RESULTS.md) is the deeper write-up at budget 100 — solve landscape, the fewer/equal/more/unsolved split over every CoV variant, and the Spearman correlations showing CoV tracks difficulty rather than erasing it — with its two figures (`fig1_composition.png`, `fig2_distribution_correlation.png`) and `solved_cov_points.csv`, all from `make_figs.py`. The three budgets are not directly comparable to each other — each is its own closed sweep over the same 66 presentations, not points on a shared curve with the other files here.

## `cov/allcov_escape/`

[`ESCAPE.md`](cov/allcov_escape/ESCAPE.md): the eight rows that resist every change of variables at 10,000 nodes (`ms622`–`ms625`, `ms636`–`ms639`, all one Aut class) all escape once the same subword-CoV family is re-run at budget 20,000 — but read the oracle-cost and collection-budget caveats in the write-up before citing a speedup number from it. `allcov_b20000_8rows_subnc2pxysb.jsonl` and `allcov_b100000_8rows_subnc2pxysb.jsonl` are the search rows (deduplicated by output pair, not by presentation — see the resume-key note in `results/README.md`); `escape_b20000_summary.csv` is the per-row provenance (`best_z`, `iso_gen`, `iso_index`, transformed pair, whether it left the input orbit); `escape_b20000_cost.svg` is the same table as a figure.

## `mitm/`

`mitm_aut_ceil{26,28,30}_nps1000.jsonl` — the Aut-quotient meet-in-the-middle search against `TRIVIAL`, one file per length ceiling, `nps1000` = 1,000 states expanded per side per step (dual-stack merge, verified). No accompanying write-up in this directory; consult `experiments/stable_ac/README.md`'s escape-additions table for what the runner does.

## `mu_scan/`

Raw output of the orbit-floor μ-descent toolchain, all keyed to the 124 unsolved ACA classes and their orbit-minimal total length (`aut_canon`, "μ"): `mu_scan_aca124_d2_k10_mrl{24,48}.jsonl` (depth-2 scan, two caps), `mu_scan_mu_descents_d2_d2_k10_mrl24.jsonl` (depth-4, re-scanning the depth-2 descended starts), `mu_ladder_aca124_r{4,8}_b{8,12,24}_mrl24.jsonl` and `mu_ladder_ak3_only_r{8,20}_b{12,32}_mrl24.jsonl` (the beam ladder at increasing rungs/beam), `mu_ladder_mu_floors_r8_r10_b32_mrl24.jsonl` (re-scan from the r8 floor exports), and the definitive `mu_ladder_big_aca124_r256_b64_mrl24.jsonl` + its `_report.json` (256 rungs, beam 64, all 124 classes, 5.58M orbits — the 1.6 GB per-orbit provenance stays out of git, see the report script's own note). [`MU_SCAN_FINDINGS.md`](mu_scan/MU_SCAN_FINDINGS.md) walks through all of it in the order it was run, ending in the census: 36/124 classes strictly descend their orbit floor, 88 robustly walled, with three null collision scans (vs the 640 solved presentations' orbits, cross-class, and against AK(3)'s orbit) over the full 5.58M.

## `orbit_greedy/`

[`ORBIT_GREEDY_PILOT.md`](orbit_greedy/ORBIT_GREEDY_PILOT.md): runs the baseline greedy starting from concrete μ-ladder orbits (free alternative starts, produced at zero search cost) instead of the original presentation, on 6 of the 124 unsolved classes. `orbit_greedy_b1000_cap96_spread60_rl8_n6.jsonl` is the one search run behind it. Result: 0 solves, 0 flips — but the pilot's own reading is that its control has no dynamic range at this budget (every control run reduces by exactly zero), so it cannot separate "the transformed start doesn't help" from "nothing shows progress here at 1,000 nodes"; the write-up flags the real test as a Colab-budget question. A companion finding inside the same run — instrumenting one class showed the ladder's rung-local beam abandoning the low shell in favour of a global best-first heap — is in the write-up and in `experiments/lessons/rung-local-beam-abandons-the-low-shell.md`.

## `ak3/`

The AK(3) universal-CoV sweep. [`RESULTS.md`](ak3/RESULTS.md) has its own file-by-file producer table at the bottom — `sweep_results.jsonl` (390 rows, resume-keyed by canonical start), `ORBIT2_CERTIFICATE.json` (the universal-move certificate) and `AC17_CERTIFICATE.json` (the classical closure certificate), both independently replay-verified. Headline: no universal CoV reaches below total length 13 from AK(3), but the sweep surfaces a second Aut(F₂)-orbit at that same floor, not a change of variables of AK(3), joined to it only at ceiling 17.

## `theory/`

Hand-written notes from the escape push, ac-advisor reviewed where the file itself says so: [`MU_CRITERION.md`](theory/MU_CRITERION.md) (the μ-descent solve criterion, revised per the ac-advisor gate), [`MS_TEMPLATE_PROPOSITION.md`](theory/MS_TEMPLATE_PROPOSITION.md) (the two-hop descent template proven for all `n`, machine-checked), [`LISITSA_TRANSFER.md`](theory/LISITSA_TRANSFER.md) (identifies the template families as Miller–Schupp presentations), [`OBSTRUCTION_BARRIER.md`](theory/OBSTRUCTION_BARRIER.md) (why abelian/quotient invariants cannot separate stable-AC classes), and [`THEORY_NIGHT_2026_07_21.md`](theory/THEORY_NIGHT_2026_07_21.md) (a committed summary of two results whose full proofs live in the gitignored `literature/proofs/` — see `experiments/lessons/literature-dir-is-gitignored.md`).

## `IDEA_BENCH_RESULTS.md`

Sixteen start-transform strategies raced against the plain greedy on the 22-row ladder+reach benchmark at budgets 500 and 1000 — coverage and efficiency deltas, all vs the same-budget baseline. The producer package (`experiments/stable_ac/idea_bench/`) was removed in the branch restart; this file is the evidence kept from it per [`PRUNED.md`](../../PRUNED.md). Do not expect to reproduce it without recovering that package first.

## Verifying anything here

Every `solved: true` row under this directory is a certificate whose proof is its move path. Before citing a number, replay it:

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results          # everything under results/stable_ac
.venv/bin/python3 -m experiments.stable_ac.verify_results <files>  # specific jsonl(s)
```

It runs no search (seconds, safe anywhere) and checks move legality, the per-relator cap at every step, a genuinely trivial endpoint, `abs_det` preservation, and cross-file budget invariance. `results/README.md` records the current standing count.
