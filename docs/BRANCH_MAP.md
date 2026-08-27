# Branch map — what lives where, and how to get it back

## How to retrieve anything

```bash
git fetch origin <branch>
git show origin/<branch>:<path>            # read one file
git checkout origin/<branch> -- <path>     # copy one file into the working tree
```

**Never merge a research branch.** The big ones carry ~480 MB of run artifacts and
1,600+ automated log commits (`git rev-list --count main..origin/experiments/ppo` = 1,731).
Everything worth keeping was cherry-picked or copied file-by-file onto this branch;
everything else is findable below.

## The branches

| branch | what it was | status | what came here / where recorded |
|---|---|---|---|
| `claude/heuristic-search-benchmark-e1f9l8` | the distilled `S20_MK2` port (PR #17) | **folded in** (both commits cherry-picked) | `experiments/search/`, tests, `CLAUDE.md` |
| `cursor/heur-u124-s20mk2-a42e` | tip of the heuristic research line; the grid, holdouts, bench60 rescore, CoV beam | mined | [`results/heuristic-search.md`](results/heuristic-search.md), [`results/speedups.md`](results/speedups.md) |
| `cursor/heur-12h-anti-overfit-a42e` | its direct ancestor (identical content to `cursor/heur-depth-tie-a42e` — duplicate ref) | superseded by `heur-u124` | same |
| `cursor/cloud-agent-1785265366483-2x3ne` | the reorg into `core/`/`runners/` + CoV-at-1k comparison (PR #10) | superseded by `heur-u124` | heuristic-search doc |
| `worktree-hsearch-hyper` | pre-reorg heuristic engine work: `hcompact`, `N_WORKERS`, EXP-01…29 | superseded (results mined) | [`results/speedups.md`](results/speedups.md) |
| `experiments/ppo` | the PyTorch PPO port + shaped-reward A/B; later commits are covmeet | **module + tests ported** | [`results/ppo-pytorch.md`](results/ppo-pytorch.md), [`results/stable-ac-learnings.md`](results/stable-ac-learnings.md) |
| `cursor/setup-dev-environment-69da` | a July fork carrying one depth-tie-break experiment + a Cursor env note (PR #12) | dormant | depth tie-break: `results/heuristic_search/depth_tie_bench60/` there |
| `claude/abelianized-exponents-verify-1i6muh` | AC19 aut-min pipeline + abel top-3 CoV (PR #14) | docs-only by decision | [`results/benchmarks.md`](results/benchmarks.md) has the retrieval table |
| `claude/summer-results-docs-scoring-u6klsb` | 640-row GS-Sub baseline doc + per-row CSV (PR #15) | numbers recorded; CSV excluded by the md-only rule | [`results/benchmarks.md`](results/benchmarks.md) |
| `claude/auto-cov-algorithm-progress-mko887` | withdraw-`RECOMMENDED`-only (PR #16) | superseded by e1f9l8 (withdraw **and** replace) | — |
| `claude/ac-stable-ac-conjecture-ijfzgz` | AK(3) sphere-decision / spike-calculus program | closed with a refutation | [`results/stable-ac-learnings.md`](results/stable-ac-learnings.md) |
| `claude/stable-ac-conjecture-stabilization-rwo9as` | the S-line; S24 AC2-from-γ₁ null | closed, uninformative null | same |
| `research/w5/stable-ac-escape` | CoV-pool economy; abelianized ranking key | mined | same |
| `codex/proofs` | ongoing crossed-derivative periodicity reduction | active; **no proofs ported** | same |
| `test/stable-ac-moves` | ICML paper source; AK(3) stable-proof attempt; form F | dormant | same |
| `test/eda` | d-o-t regressor data engineering (38,384-row split) | dormant | same |
| `test/greedy-test-suite` | 8k-line greedy test suite against a pre-main solver | stale (older `greedy_baseline.py`); would need rebasing | — |
| `feat/heuristic-greedy`, `feat/heuristic-docs`, `feat/benchmark-subsets` | PRs #7–#9 | **fully merged to main**; `feat/benchmark-subsets` tree is byte-identical to main | — |
| `ci/tests-main` | PR #6 | fully merged; tree identical to main | — |

## Colab notebooks not collected

The ~25 `experiments/heuristic_search/hsearch_colab_*.ipynb` on
`origin/claude/abelianized-exponents-verify-1i6muh` (e.g.
`hsearch_colab_ac19_autmin_1k_c{1..5}.ipynb`) drive `experiments/heuristic_search/`,
which is not ported, and hard-code Drive paths and `git reset --hard`. The
deduplication rule applied throughout this collection: **when several notebooks are one
template under different configs, keep one** — for PPO that is
`experiments/notebooks/ppo/ppo_baseline.ipynb` plus the generator
(`python3 -m experiments.ppo.make_arm_notebooks`) for the two arm variants.

## Merge-to-main checklist

- [ ] Flip `BRANCH` to `"main"` in **both** `experiments/notebooks/ppo/ppo_baseline.ipynb`
      (the CONFIG cell) and `experiments/ppo/make_arm_notebooks.py` —
      `tests/ppo/test_notebook.py::test_the_branch_matches_the_branch_this_code_is_on`
      enforces it on any push to a named branch.
- [ ] Enable `tests-ppo` as a required status check alongside `tests`.
- [ ] Decide the two deferred fold-ins: `benchmark/BASELINE.md` + `difficulty_bins.csv`
      (PR #15's branch), and the aut-min pipeline (see
      [`results/benchmarks.md`](results/benchmarks.md)).
