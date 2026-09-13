# Retained-rank triangular expansion on hard AC19 rows: what can expose a short relator?

Continuation of `research/ac19_triangle_expansion_20260912` (question: does
expanding a rank-two pair to an all-triangle system of rank 7–9 and then
searching with ordinary AC moves at fixed rank make hard-but-solved AC19 rows
easier?) and of its `lift/` sub-study (the saved rank-two certificates cannot be
shadowed at fixed rank and fixed dictionary).

This directory adds the rank-preserving *theory* of what a single substitution
can do at an all-triangle state, a search ordering built from it, and a small
counted benchmark on the frozen hard panel and easy controls.

| file | what |
|---|---|
| `THEORY.md` | Lemma 1 (parity), Lemma 2 (a shared cyclic digram is necessary for a one-move bigon), digram-disjointness, the coupling ordering |
| `theory.py` | the primitives (`cyclic_digrams`, `inv2`, `shared_digram_pairs`, `coupling`, `one_step_products`) and the machine checks of both lemmas |
| `coupling_search.py` | rank-preserving best-first search; every edge is a `normal_product_substitution` event of the frozen engine, so paths replay under `research/u124_rank_3h_20260912/verify.py`; `coupling` vs `structural` orderings |
| `run_panel.py` | the benchmark: triangulate (counted as preprocessing), then both orderings at each cap; all work counted |
| `verify.py` | independent replayer: re-derives the lemma checks and replays every arm's path with separate word code |
| `make_results.py` | renders the tables in `RESULTS.md` from the JSON records |
| `bench_cap45_p60.json`, `bench_cap6_p60.json` | the records |
| `RESULTS.md` | the numbers and the conclusion |

Reproduce (from the repository root):

```sh
cd research/ac19_triangle_theory_20260913
python3 run_panel.py --caps 4,5 --pops 60 --beam 48 --out bench_cap45_p60.json
python3 run_panel.py --caps 6   --pops 60 --beam 48 --out bench_cap6_p60.json
python3 verify.py bench_cap45_p60.json bench_cap6_p60.json
python3 make_results.py bench_cap45_p60.json bench_cap6_p60.json
```

Scope: fixed rank, fixed declared basis, ordinary AC normal-product
substitutions only. Triangulation is preprocessing, never a solve. Nothing here
concerns stable moves or AC-triviality.
