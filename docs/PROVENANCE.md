# Provenance

Where every part of this branch comes from: component -> source branch -> path -> the commit that last touched that path
(`git log -1 --format=%h origin/<branch> -- <path>`, read 11 Oct 2026; the rows of `rank3/brute-force-baseline` and
`cov/all-subsets-sweep`, 13 Oct 2026). The origin is the public repository `Avi161/ACSolverX`. Code was ported file by
file into `acx/` (rewritten on the `acx` word and move types, then checked against the source: the tests named in each
row). Nothing was copied as a whole tree.

## Code (`acx/`)

| acx module | component | source branch | source path | commit | checked by |
|---|---|---|---|---|---|
| `core/words.py`, `core/moves.py`, `verify/replay.py` | words, presentations, general n-relator S-move, AC4/AC5, `abs det` invariant | `test/greedy-test-suite` | `experiments/greedy_tests/spec/` | `bed10350` | `test_core`, `test_replay` |
| `search/spec.py` | slow baseline: length-only greedy, reduction tail, `(priority, depth, key)` order, legacy moves | `main` | `experiments/search/greedy_baseline.py` | `cdc5d319` | `test_spec` (golden) |
| `tests/data/greedy_golden.json` | baseline golden file | `test/greedy-test-suite` | `experiments/greedy_tests/golden/greedy_golden.json` | `1623ed42` | `test_spec` |
| `core/priority.py` | S20_MK2 (`L + 20 S + 2 MK`) | `claude/heuristic-search-benchmark-e1f9l8` | `experiments/search/heuristics.py` | `df0ddeae` | `test_core` |
| `core/priority.py` | float accumulation order of the fast scorer | `codex/ac-elementary-decoder` | `experiments/heuristic_search/core/hfast.py` | `bddce971` | `test_fast` |
| `search/fast/kernels/` | expansion kernel, cut-shift skip, enumeration order, canonical form on packed words (`kernels/words.py`; the source's two-generator 2-bit form, here any symbol width) | `codex/ac-elementary-decoder` | `experiments/heuristic_search/core/hexpand.py` (blob `f005093d`) | `a8a6b3a4` | `test_fast` |
| `search/fast/best_first.py`, `search/fast/arrays.py`, `search/fast/packing.py`, `search/fast/heap.py`, `search/fast/dedup.py` | arena, packed rows (the source's 2 bits a symbol; here 1, 2, 4 or 8 by generator count), int32 heap, dedup table, grow/widen, path capture | `codex/ac-elementary-decoder` | `experiments/heuristic_search/core/hcompact.py` (blob `046a6003`) | `d01a315f` | `test_fast` |
| `verify/decode.py`, `verify/pack.py` | elementary decoder and the packed `I/S/C/M` form | `codex/ac-elementary-decoder` | `experiments/search/ac_decode.py`, `decode_ac_jsonl.py` | `ea0b3e16` | `test_decode` |
| `aut/whitehead.py`, `aut/autos.py` | Whitehead canonical form with witness; `AUTOS` | `main` | `experiments/equivalence_classes/lib/autcanon.py`, `experiments/analysis/whitehead.py` | `6bf981b6` | `test_aut` |
| `aut/fast.py` | numba Aut-min (`autcanon_fast`) | `research/w5/stable-ac-escape` | `experiments/stable_ac/cov/ladder/autcanon_fast.py` | `584f8809` | `test_aut` (parity with pure) |
| `aut/transport.py`, `aut/emitter.py` | certificate transport (equivariance) | `claude/ac19-leftover-solver-notebook-6yan6d` | `experiments/search/transport_ac19_orig.py` | `24178792` | `test_aut` |
| `aut/equivalence.py` | checker for the equivalence certificates (new; data from `codex/proofs`) | new | | | `test_data` |
| `cov/images.py`, `cov/substitution.py`, `cov/family.py`, `cov/certificate.py` | CoV transform and family `subnc2pxysb` (acx reads the relators cyclically reduced first; every shipped row already is) | `cov/all-subsets-sweep` (same blob on `research/w5/stable-ac-escape`) | `experiments/stable_ac/cov/cov.py` | `4f63f976` | `test_cov` (17,313 images equal to the source) |
| `cov/run.py` | per-image cap `max(24, longest + 16)` | `cov/all-subsets-sweep` | `experiments/stable_ac/cov/run/run_cov.py` | `584f8809` | `test_cov` |
| `cov/` family `suballpxyb8` (`family.proper_subwords`, `substitution.patterns`, `images.class_key`) | exhaustive CoV family | `cov/all-subsets-sweep` | `experiments/stable_ac/cov/cov_all.py` | `58b34b9f` | `test_cov` (the sweep's 114,042 MS640 starts, sha256) |
| `hybrid/solver.py`, `hybrid/search.py`, `hybrid/frontier.py`, `hybrid/steps.py` (the steps' JSON form) | hybrid search and solve | `claude/vigilant-babbage-nnbuj0` | `research/ac_hashfree_cascade_20260914/hfhybrid.py` | `62108ade` | `test_hybrid` (MS640 per row) |
| `hybrid/cascade.py`, `hybrid/steps.py`, `hybrid/pinch.py` | stages A-C, the step types and the `Run` that applies them, and the finishing gates | `claude/vigilant-babbage-nnbuj0` | `research/ac_hashfree_cascade_20260914/hfcascade.py` | `62108ade` | `test_hybrid` |
| `hybrid/dynrank.py` | define, eliminate, products; transvections | `claude/vigilant-babbage-nnbuj0` | `research/ac_dynamic_rank_20260913/dynrank.py`; `research/ac_hashfree_cascade_20260914/hfunified.py` | `61bc4ebc` | `test_hybrid` |
| `hybrid/kernels.py` | rank-two expansion and Nielsen/permutation transforms | `codex/ac-elementary-decoder` | `experiments/search/basis_moves.py` (on the fast kernels) | `d01a315f` | `test_hybrid` (spec = fast) |
| `hybrid/elementary.py`, `hybrid/frame.py` | certificate to elementary/stable moves (replaces `verify_hybrid`) | `claude/vigilant-babbage-nnbuj0` | `research/ac_hashfree_cascade_20260914/hfhybrid.py`, `research/ac_dynamic_rank_20260913/verify.py` | `62108ade`, `61bc4ebc` | `test_hybrid` |
| `ngen/sac.py`, `core/digrams.py` | `triangulate`, `define` (the SAC transform to relators of length <= 3); the digram helpers `digram_counts`, `tokenize` (shared with `hybrid/dynrank.py`) | `claude/vigilant-babbage-nnbuj0` | `research/ac_dynamic_rank_20260913/dynrank.py` (blob `901efc11`) | `61bc4ebc` | `test_ngen` (equal on 142,365 rows) |
| `ngen/solver.py` | n-generator search (replaces `solvern`, `solvern_fast` by `acx.search`) | `worktree-hsearch-hyper` | `experiments/stable_ac/solvern.py`, `solvern_fast.py` | `eff4b4c7`, `a4024828` | `test_ngen` |
| `ngen/lifting.py` | lift of a root solve to a stable path (new, on `aut.emitter.Emitter`) | new | | | `test_ngen` |
| `ngen/sweep/` | rank-n brute-force sweep: word pool, stabilised starts, per-row sweep with control and null stabilisation, summary tables, verifier. The search is `acx.search`; `solvern` and `solvern_fast` are not ported | `rank3/brute-force-baseline` (tip `f2d53ced`; ported at `068ea77`, after which only `run_rank3_bf.py` changed, in its cloud options `--reverse` and `--no-merge`) | `experiments/stable_ac/rank3/words.py`, `run_rank3_bf.py`, `rankn_bf.py`, `verify_rank3_bf.py`, `summarize_rank3_bf.py` | `6fd59c2b`, `faa88318`, `ec5dde8e`, `878d939a`, `d6d6513a` | `test_rankn_sweep` (every cell of the stored MS640 results equal: control, rank 3 lengths 1-4, rank 4 and 5 slices) |
| `core/capcount/` and the six counter fields in every search | the relator-cap counters (`docs/CAP.md`). **Origin:** the rank-3 baseline's `cap_dropped`, `cap_dropped_min_total` and `cap_first_bind` in `solvern.py` / `solvern_fast.py`, and the analyses `cap_compare.py` and `cap_exhaustion.py`. acx rewrote them as one heuristic-blind module that compares full heap keys, and added `cap_would_pop` and `cap_needed` (new) | `rank3/brute-force-baseline` (tip `f2d53ced`) | `experiments/stable_ac/solvern.py`, `solvern_fast.py`, `rank3/cap_compare.py`, `rank3/cap_exhaustion.py` | `ec5dde8e` | `test_capcount`, `test_cap_invariant` (same search at any larger cap when the count is 0); `cap_dropped` equals the earlier per-move rejected count on every MS640 row |
| `hybrid/capwatch.py` | counters of the hybrid's three limits (new, on `core/capcount/`) | new | | | `test_hybrid` |
| `rl/moves.py`, `rl/policy.py` | batched S-move; Dual-Ring actor-critic | `experiments/ppo` | `experiments/ppo/acs_moves.py`, `policy.py` | `fde45378` | `test_rl` (JAX reference) |
| `rl/beam.py` (its chunked forward pass is `rl/policy.forward`) | beam search | `experiments/ppo` | `experiments/ppo/beam.py` | `5326550d` | `test_rl` |
| `rl/env.py`, `rl/ppo.py` | training environment and PPO | `experiments/ppo` | `experiments/ppo/acs_env.py`, `ppo.py` | `42302b0a`, `91c74c0b` | `test_rl` (smoke) |
| `rl/convert.py` | orbax -> torch weights | `experiments/ppo` | `experiments/ppo/transplant.py` | `6359ea90` | `test_rl` |
| `rl/checkpoint/610model_1000.pt` | the step-1000 weights (converted) | `main` | `ppo_checkpoints/610model/1000/params` | `aa0371c7` | `test_rl` |
| `data.py` (`MS`, `AK`) | the Miller-Schupp and Akbulut-Kirby families | `main` | `greedy_search.ipynb` | `aa0371c7` | `test_data` |
| `runner/` (with `runner/rundir.py`, the run folder), `run.py`, `configs/`, `examples/` | the one CLI and its inputs (new) | new | | | `test_runner`, `test_cli` |
| `report/` (`load`, `table`, `charts`, `page`), `compare.py` | the comparison table and charts (new) | new | | | `test_report` |

## Data (`data/`, `benchmark/`)

| file | source branch | source path | commit |
|---|---|---|---|
| `data/*.txt[.gz]` (`1190MS.txt`, `AC19.txt`, `AC19_extended.txt`, `AC1M.txt.gz`, `ms640_solved.txt`), `data/ms_unsolved_reps/ms_*` (the same blobs as on `main`) | `main` | `data/` | `317f9c1d` (`ms640_solved.txt`) |
| `benchmark/subsets/` | `main` | `benchmark/subsets/` | `e7fef21a` |
| `benchmark/ladder/` (panels, pairs, `unsolved_124.csv`, `LADDER.md`) | `claude/ac19-theorem-strength-8v1wp6` | `benchmark/ladder/` | `1fc160c8` (built from `dab82a84` on `claude/ac19-leftover-solver-notebook-6yan6d`, `9033f13e` on `claude/summer-results-docs-scoring-u6klsb` and the MS-640 greedy blob `525050dd`, hashed in `ladder_manifest.json`; the build and tester scripts, `runs/`, `sources/` and `ladder_all.csv` stay there) |
| `benchmark/splits/splits_ac1m_hard_aut.json` | `cursor/heur-12h-anti-overfit-a42e` | `results/heuristic_search/splits/splits_ac1m_hard_aut.json` | `3643a8da` |
| `data/AC19_extended_aut_min.csv` | `cursor/heur-12h-anti-overfit-a42e` | `data/AC19_extended_aut_min.csv` | `eb9b6143` |
| `data/AC1M_aut_min.csv.gz` | `claude/vigilant-babbage-nnbuj0` | `research/ac1m_autmin_20260914/records/AC1M_aut_min.csv.gz` | `5390ca42` |
| `data/ms_unsolved_reps/aca_124_*` | `cursor/u124-stable-ac-1b54` | `data/ms_unsolved_reps/` | `33eb4147` |
| `data/equivalence_classes/certificates.json` | `codex/proofs` | `results/equivalence_classes/certificates.json` | `d89d3dde` |
| `benchmark/difficulty_bins.csv` | `claude/summer-results-docs-scoring-u6klsb` | `benchmark/difficulty_bins.csv` | `9033f13e` |

Every copied file matches its source blob (`git hash-object`), except `LADDER.md` and `README_aca_124.md` (a provenance
note added; `LADDER.md` also points to `run.py` instead of the source's tester, and its source refs moved here).

## Stored studies (`results/stable_ac/`)

Two studies run on their own branches, carried as their compact files (summaries, tables, logs, graphs) byte for byte,
plus a README edited for this checkout and a new `MANIFEST.json` that lists every raw file of the source folder with its
size and sha256 ([results/README.md](../results/README.md#studies)).

| folder or file | what | source branch | source path | commit |
|---|---|---|---|---|
| `results/stable_ac/rank3_bf/` | the rank-3/4/5 brute force on MS640: the 91 files of the source folder that are not raw data; its raw `.npz`/`.jsonl` files (102, 70.5 MB) listed in the manifest | `rank3/brute-force-baseline` | `results/stable_ac/rank3_bf/` | `f14945df` (tip `f2d53ced`) |
| `results/stable_ac/cov_all/` | the exhaustive CoV sweep on MS640 at budgets 100, 10,000 and 100,000: summaries, the per-presentation csv, logs, graphs, and the budget 100,000 `.jsonl.gz` (4.1 MB, the transform of every start); the other raw files (5, 280 MB) listed in the manifest; the source's day logs are not carried, their facts are in the README | `cov/all-subsets-sweep` | `results/stable_ac/cov_all/` | `f8d5dce7` (tip `fb84a588`) |
| `tests/test_rank3_study.py` | the manifest, no raw file committed, a fetched raw file against its size and sha256, the stored numbers the docs quote, `results/rank3_bf/` against the stored tables (new) | new | | |
| `tests/test_cov_all_study.py` | the manifest, the stored numbers the docs quote, the stored certificates and paths replayed with `acx.cov` and `acx.verify`; slow: every transform rebuilt, 100 rows searched again, the six control failures at cap 64 and uncapped (new) | new | | |

## Evidence (numbers quoted in RESULTS.md)

| component | source branch | source path | commit |
|---|---|---|---|
| evidence: MS640 length vs S20_MK2 at 1M | `results/ms640-s20-mk2-1m` | `results/heuristic_search/ms640_s20_mk2_1m/RESULTS.md` | `dbbf22b9` |
| evidence: AC19 hard tail at 100k | `results/ms640-s20-mk2-1m` | `results/heuristic_search/hsearch_ac19_hard100k/RESULTS.md` | `4fe83008` |
| evidence: AC19 Aut-min 10k, complete run | `claude/ac19-leftover-solver-notebook-6yan6d` | `results/heuristic_search/ac19_autmin_10k/RESULTS.md` | `a2ea9786` |
| evidence: AC19 originals at 10M and transport | `claude/ac19-leftover-solver-notebook-6yan6d` | `results/heuristic_search/ac19_orig_10m/RESULTS.md` | `9f50ff3a` |
| evidence: MS640 elementary decode | `codex/ac-elementary-decoder` | `results/heuristic_search/ms640_elementary_ac/RESULTS.md` | `0ed6d9d3` |
| evidence: S20_MK2 selection tables | `claude/heuristic-search-benchmark-e1f9l8` | `experiments/search/HEURISTICS.md` | `df0ddeae` |
| evidence: abel top-3 on MS640 | `research/w5/stable-ac-escape` | `results/stable_ac/cov/cov_top3/RESULTS.md` | `605db83d` |
| evidence: one-shot CoV sweep 10k | `research/w5/stable-ac-escape` | `results/stable_ac/cov/graphs/SUMMARY_b10000.md` | `bab3e40f` |
| evidence: three-way cost | `research/w5/stable-ac-escape` | `results/comparison/THREE_WAY_COST.md` | `0f4eefc1` |
| evidence: rank-3/4/5 brute force and its cap-counter tables (final at cap 24, 13 Oct 2026; stored in `results/stable_ac/rank3_bf/`) | `rank3/brute-force-baseline` | `results/stable_ac/rank3_bf/README.md` | `f14945df`; the study's commits: `6fd59c2b` (plan and code), `13c6e536` (interim results), `7c9ab33b` (final at cap 24), `ec5dde8e` (cap counters), `a416bad9` (the counted rerun), `f14945df` (README) |
| evidence: nonsym K=4 beam | `cursor/heur-u124-s20mk2-a42e` | `results/comparison/COVBEAM_K4_B1K_ADVISOR_REVISE.md` | `83116e0f` |
| evidence: u124 s20_mk2 1M census (runner only) | `cursor/heur-u124-s20mk2-a42e` | `results/heuristic_search/u124_s20mk2_1m/README.md` | `17e19950` |
| evidence: mu-ladder findings | `cursor/cloud-agent-1785265366483-2x3ne` | `results/stable_ac/mu_scan/MU_SCAN_FINDINGS.md` | `584f8809` |
| evidence: covmeet audit | `experiments/ppo` | `results/stable_ac/covmeet/AUDIT_2026-08-16.md` | `51b3dfbd` |
| evidence: z=w stabilisation arms (negative) | `test/stable-ac-moves` | `experiments/stable_ac/ak3_stable_proof/RESULTS.md` | `2278437b` |
| evidence: S x MK x F holdout read | `experiments/ppo` | `results/heuristic_search/smk_f_grid/HOLDOUT.md` | `f5842134` |
| evidence: S-family arms on never-read AC1M | `cursor/heur-12h-anti-overfit-a42e` | `results/heuristic_search/campaign_12h/RESULTS.md` | `8ba73131` |
| evidence: depth term (EXP-11) | `cursor/heur-depth-tie-a42e` | `results/heuristic_search/runs/EXP11_depth.md` | `69146acb` |
| evidence: cut-shift and packed canonicalisation | `codex/ac-elementary-decoder` | `experiments/heuristic_search/core/perf_lab/EXPAND_SPLIT.md` | `d4b222b7` |
| evidence: 10M-node row timings | `codex/ac-elementary-decoder` | `results/heuristic_search/u124_10m/RESULTS.md` | `153aecfe` |
| evidence: solvern_fast speed and parity | `research/w5/stable-ac-escape` | `experiments/stable_ac/nocov/PIPELINE.md` | `b736f001` |
| evidence: 501-node cascade screen | `codex/ac-elementary-decoder` | `results/heuristic_search/ac19_cascade_screen/RESULTS.md` | `8be0c041` |
| evidence: cascade_bs probe | `claude/ac19-leftover-solver-notebook-6yan6d` | `results/heuristic_search/ac19_bs_probe/RESULTS.md` | `dab82a84` |
| evidence: final_policy census at 1,000 units | `claude/results-collection-org-wmvpxu` | `results/heuristic_search/ac19_final_policy_full_1k/README.md` | `98f719e2` |
| evidence: cascade with the cap-14 backward table | `claude/ac19-theorem-strength-8v1wp6` | `research/residual_20260909/CAMPAIGN_REPORT.md` | `460904f9` |
| evidence: U124 probes at 10,000 (incl. orbit search) | `claude/ac19-theorem-strength-8v1wp6` | `research/residual_20260909/u124/README.md` | `7f6bcdb4` |
| evidence: orbit-image atlas (autchoice) | `claude/ac19-theorem-strength-8v1wp6` | `research/autchoice_20260910/ATLAS.md` | `7fa813ae` |
| evidence: CoV escape at 20,000 | `research/w5/stable-ac-escape` | `results/stable_ac/cov/allcov_escape/ESCAPE.md` | `81078f47` |
| evidence: certificate standing count | `research/w5/stable-ac-escape` | `results/README.md` | `9e748f60` |
| evidence: abelian-mass ranking | `research/w5/stable-ac-escape` | `experiments/IDEAS.md` | `81078f47` |
| evidence: bench60 arms tables | `claude/abelianized-exponents-verify-1i6muh` | `benchmark/subsets/ARMS.md` | `cd913649` |
| evidence: abel top-3 at 1,000 nodes | `claude/abelianized-exponents-verify-1i6muh` | `logs/05-08-2026.md` | `90461e9c` |
| evidence: same-cap Aut-min control (36/60) | `cursor/heur-u124-s20mk2-a42e` | `results/comparison/covbeam_nonsym_b1kfull_subset60.md` | `06672c5d` |
| evidence: z=w arms on MS640 at 500k | `test/stable-ac-moves` | `results/stable_ac/3_generators_w_choices/README.md` | `3d181532` |
| evidence: stabilisation that only rebookkeeps is inert | `claude/stable-ac-conjecture-stabilization-rwo9as` | `experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md` | `2c053e63` |
| evidence: dynamic-rank search and triangulated roots | `claude/vigilant-babbage-nnbuj0` | `research/ac_dynamic_rank_20260913/RESULTS.md` | `3e8aa893` |
| evidence: triangular expansion on hard AC19 rows | `claude/vigilant-babbage-nnbuj0` | `research/ac19_triangle_expansion_20260912/RESULTS.md` | `9eb31975` |
| evidence: macros and the Whitehead portal | `new_moves` | `experiments/search/NEW_MOVES.md` | `ddb4f874` |
| evidence: PyTorch port plan and parity | `experiments/ppo` | `experiments/ppo/PLAN.md` | `5c567a36` |
| evidence: A100 smoke (530/530) | `experiments/ppo` | `logs/10-08-2026.md` | `7d38f5fa` |
| evidence: hybrid at 10M (code only, open) | `codex/ac19-hybrid-10m` | `experiments/search/hybrid_10m.py` | `0e77ffce` |
| evidence: exhaustive CoV sweep, MS640 at 100 (stored in `results/stable_ac/cov_all/`, as are the next three) | `cov/all-subsets-sweep` | `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100_summary.md` | `58b34b9f` |
| evidence: exhaustive CoV sweep, MS640 at 10,000 | `cov/all-subsets-sweep` | `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000_summary.md` | `9b496d5f` |
| evidence: exhaustive CoV sweep, MS640 at 100,000 | `cov/all-subsets-sweep` | `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000_summary.md`, `..._b100000.jsonl.gz` | `22b7e37c` |
| evidence: the sweep's per-presentation csv and its box script | `cov/all-subsets-sweep` | `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000_per_presentation.csv` | `f8d5dce7` (tip `fb84a588`) |
| reference reruns of the original code (not in git) | `main` e7fef21a, `claude/vigilant-babbage-nnbuj0` 5ae1bd8e | `work/reference/` of the consolidation run | |
| checks of this branch: test runs, the fast/spec speed print (not in git) | this branch | `work/verify/` of the consolidation run (`NUMBERS.md`, `logs/`) | |

## Where several copies exist, and the one chosen

- **`hcompact.py`** exists in five drifted versions. Chosen: blob `046a6003` (979 lines, `codex/ac-elementary-decoder`
  tip, also on `claude/ac19-leftover-solver-notebook-6yan6d`), the newest generation: it stores cut positions unsigned,
  so path capture is correct for caps above 128. Not chosen: `647f8d02` (971 lines, the results-collection / vigilant /
  theory line; refuses path capture above cap 128), `3fea8f49` (423 lines, heur-u124 / abel / ppo line), `c393e4db`
  (418 lines, the **oldest** port, cloud-agent / heur-12h / w5 line), and `worktree-hsearch-hyper:experiments/heuristic_search/hcompact.py`
  (`9e401a90`, at a different path). `hexpand.py` is blob `f005093d` (551 lines).
- **`cov.py`** is blob `81fb41e3` on `research/w5/stable-ac-escape`, `cov/all-subsets-sweep` and
  `claude/abelianized-exponents-verify-1i6muh`: one file, three branches. The family tag `subnc2pxysb` and the earlier
  `zf3` (`NAIVE_Z_FAMILY`) are both inside it.
- **`heuristics.py`** (S20_MK2) is on `claude/heuristic-search-benchmark-e1f9l8` (`df0ddeae`), and a later copy on
  `codex/ac-elementary-decoder` (`d01a315f`). The arms used for selection live on `cursor/heur-12h-anti-overfit-a42e`.
  `RECOMMENDED` is not shipped (RESULTS.md, Tried).
- **`beam/beam_search.py`** on `main` fails to restore the 610 checkpoint as committed (fixes on `test/eda` and
  `test/stable-ac-moves`). Not ported: `acx.rl` uses the PyTorch port of `experiments/ppo` and a converted `.pt`.
- **The decoder and transport** share a vocabulary: `ac_decode.py` (`codex/ac-elementary-decoder`) is imported by
  `transport_ac19_orig.py` (`claude/ac19-leftover-solver-notebook-6yan6d`); in `acx` they share only the move schema.

## Branch coverage

Every public branch is accounted for. A "covered" branch contributes nothing new beyond the branch named.

| branch | tip | role |
|---|---|---|
| `main` | `e7fef21a` | baseline `greedy_baseline.py`, Whitehead (pure), words, RL code and checkpoint, data, benchmark subsets |
| `claude/finalized-research-run-t1xh3u` | | this branch; not a source |
| `ci/tests-main` | `9435fcbb` | covered: squash-merged into `main` as PR #6 |
| `feat/heuristic-greedy` | `88a3ef02` | covered: squash-merged into `main` as PR #7 |
| `feat/benchmark-subsets` | `e18df6ae` | covered: squash-merged into `main` as PR #9 |
| `feat/heuristic-docs` | `cc88335a` | covered: stale |
| `test/greedy-test-suite` | `1623ed42` | specification, golden file, parity harness |
| `claude/heuristic-search-benchmark-e1f9l8` | `5be0421f` | S20_MK2 and its feature table |
| `claude/greedy-s20mk2-benchmark-6pybub` | `ab8b9e73` | evidence only: duplicate length vs S20_MK2 A/B runs |
| `cursor/greedy-vs-s20mk2-subset20-5c17` | `6fb45062` | evidence only: duplicate A/B on subset 20 |
| `claude/auto-cov-algorithm-progress-mko887` | `ef337c4b` | covered: only withdraws `RECOMMENDED` |
| `cursor/heur-12h-anti-overfit-a42e` | `cb85bee5` | S-family arms, splits, AC19 Aut-min CSV |
| `cursor/heur-depth-tie-a42e` | `cb85bee5` | covered: same tip as `cursor/heur-12h-anti-overfit-a42e` (depth-term experiments) |
| `cursor/setup-dev-environment-69da` | `17d5bf8c` | no component kept |
| `worktree-hsearch-hyper` | `3cd9789f` | ancestor of the kept engine and CoV code; superseded first copies not carried |
| `codex/ac-elementary-decoder` | `0ed6d9d3` | fast engine, performance lab, decoder, cascade stages |
| `codex/ac19-hybrid-10m` | `0e77ffce` | covered by the hybrid and cascade lines; the 10M run is an open experiment |
| `claude/ac19-leftover-solver-notebook-6yan6d` | `9f50ff3a` | certificate transport, complete AC19 10k run, `cascade_bs` |
| `claude/ac19-theorem-strength-8v1wp6` | `dd06d784` | difficulty ladder, backward-ball table builder (evidence only) |
| `claude/vigilant-babbage-nnbuj0` | `5ae1bd8e` | hybrid solver, dynamic-rank moves, AC1M Aut-min census |
| `codex/theory-patterns-3h` | `5ae1bd8e` | covered: same tip as `claude/vigilant-babbage-nnbuj0` |
| `claude/results-collection-org-wmvpxu` | `98f719e2` | `BRANCH_MAP.md`, `final_policy` evidence; its PyTorch and CoV copies are not sources |
| `claude/summer-results-docs-scoring-u6klsb` | `9033f13e` | MS640 reference run and difficulty bins |
| `results/ms640-s20-mk2-1m` | `dbbf22b9` | numbers only (MS640 1M, AC19 100k); not copied wholesale |
| `research/w5/stable-ac-escape` | `525050dd` | one-shot CoV, n-generator solver, numba Whitehead, certificate verifier |
| `cov/all-subsets-sweep` | `fb84a588` | family `suballpxyb8` (`[cov] family`); the sweep's compact files in `results/stable_ac/cov_all/`, evidence that it adds no solve; reach tier |
| `claude/abelianized-exponents-verify-1i6muh` | `90461e9c` | evidence: abel top-3 |
| `cursor/heur-u124-s20mk2-a42e` | `8de34cb5` | evidence: nonsymmetric beam; U124 census runner (no results) |
| `cursor/cloud-agent-1785265366483-2x3ne` | `c9aff6b8` | evidence: mu-ladder |
| `rank3/brute-force-baseline` | `f2d53ced` | rank-n brute-force sweep and the cap counters it introduced (`acx/ngen/sweep/`, `acx/core/capcount/`); its study folder in `results/stable_ac/rank3_bf/`, compact files only (the raw `.npz`/`.jsonl` files and the cloud scripts are not carried) |
| `experiments/ppo` | `c73b11f2` | PyTorch PPO and beam port, splits, covmeet audit |
| `test/eda` | `0f4149a1` | beam restore fix; path datasets not carried |
| `test/stable-ac-moves` | `2278437b` | stable moves, z = w negative results, beam fix, AK(3) attempts |
| `new_moves` | `ddb4f874` | evidence: macros, Whitehead CoV portal |
| `claude/ac-stable-ac-conjecture-ijfzgz` | `b6333caf` | negative results (Neuwirth thickenability) |
| `claude/stable-ac-conjecture-stabilization-rwo9as` | `670c4f41` | negative results (stabilisation, length-3 SPLIT) |
| `codex/proofs`, `fable/proofs`, `cursor/u124-stable-ac-1b54`, `cursor/q-residue-scan-9163` | `62b10c94`, `7d8e999b`, `7d518aef`, `529c5756` | AK(3) and U124 theory: linked, not shipped; `cursor/q-residue-scan-9163` (`529c5756`) is subsumed |

## Not carried

- A 71 MB Regina `.so` and an `ocx` binary on `results/ms640-s20-mk2-1m`; third-party paper PDFs
  (`.scratch/papers`, `tmp/pdfs`, about 10 MB) on the same branch; 154 MB of `.scratch` output there.
- The 287 duplicate files with " 2" in their names on `claude/results-collection-org-wmvpxu` and
  `claude/ac19-theorem-strength-8v1wp6` (no pinned source comes from those trees).
- Raw 1k/10k AC19 chunk runs (about 380 MB); the backward-ball `.npz` (282 MB, rebuilt in about 27 minutes); the 610
  checkpoint's steps 900 and 950 (step 1000 only, converted to a 0.6 MB `.pt`); the JAX training stack (`ppo_ac_s.py`,
  `network.py`, `envs/`, `wrappers.py`, `beam/`), removed from this branch's tree.
- The website and paper on `test/stable-ac-moves`; the `dot_archive_v2` dataset and `merged_best_paths.jsonl` on `test/eda`.
- On `rank3/brute-force-baseline`: the per-row `.npz`/`.jsonl` result files (102 files, 70.5 MB, listed in
  `results/stable_ac/rank3_bf/MANIFEST.json`), the cloud run scripts, the 2,187-word block shards, the relator-subword
  arm, the code of the shortlex, cross-validation and class-view analyses (`class_view.py`, `indep/`, `rankn_checks.py`,
  `word_families.py`; their outputs are in the study folder), and `PLAN.md`.
- On `cov/all-subsets-sweep`: the sweep's `.jsonl` files and the `.jsonl.gz` of budgets 100 and 10,000 (listed in
  `results/stable_ac/cov_all/MANIFEST.json`), the sweep's runner, checker, summary, table and plot scripts and its box
  script (`experiments/stable_ac/cov/run/`, `verify/`; the enumerator `cov_all.py` is ported as `[cov] family`), and
  the source's day logs.
- Nothing outside the branches of the public repository.

## Environment of the original runs

| run | host and versions |
|---|---|
| hybrid solver (`ac_hashfree_cascade_20260914`) | 4-core container, CPython 3.11, numba 0.63; MS640 timings on one core with `NUMBA_NUM_THREADS=1` |
| fast engine lab (`perf_lab`) | 4 cores, 15 GB, Xeon 2.8 GHz nominal; the 4.49x was measured on a Xeon 6975P-C cloud machine |
| MS640 1M A/B | M-series laptop, 6 workers, about 2 minutes an arm |
| main CI (`.github/workflows/tests.yml`) | Python 3.10, numpy 2.1.3, numba 0.63.1 |
| the Aut-minimal census | CPython 3.14.3, numba 0.66.0 [survey] |
| reference reruns (`work/reference/`) | shared 4-core Xeon 2.80 GHz VM, Python 3.12.3, numba 0.63.1, numpy 2.1.3, one single-threaded process per run; sources `main` e7fef21a and `claude/vigilant-babbage-nnbuj0` 5ae1bd8e |
| this branch (`acx`) | shared 4-core Xeon 2.80 GHz VM, Python 3.12, numba 0.63.1, numpy 2.1.3, `NUMBA_NUM_THREADS=1` |
