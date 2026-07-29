# `tests/` — every suite in the repo

One root, nested by area. A bare `pytest` collects all of them (`pytest.ini` sets `testpaths = tests`), and `conftest.py` sits here at the top because every suite needs the same two things: the repo root on `sys.path`, and the `numba_warm` session fixture that pays the ~30–60 s JIT compile once instead of inside whichever test happens to run first.

| suite | files / tests | covers |
|---|---|---|
| [`greedy/`](greedy/) | 23 / 1015 | the greedy pipeline — `experiments/search/{greedy_baseline,greedy_compact}.py`, `experiments/run_baseline.py`, and the `experiments/greedy_tests/` spec/fixtures support code |
| [`stable_ac/`](stable_ac/) | 12 / 312 | `experiments/stable_ac/` — the general-`n` solvers (`solvern`, `solvern_fast`), CoV, the μ-ladder, AK(3), the certificate verifier, `word_families` |
| [`heuristic_search/`](heuristic_search/) | 6 / 70 | `experiments/heuristic_search/` — the heap orderings and the solver variants they run on |
| [`clustering/`](clustering/) | 3 / 25 | `experiments/clustering/` — features, signed knots, holdout evaluation |
| [`analysis/`](analysis/) | 1 / 11 | `experiments/analysis/` — the combined ladder+reach benchmark builder |
| [`equivalence_classes/`](equivalence_classes/) | 1 / 35 | `experiments/equivalence_classes/` — the 261-reps collapse |
| [`wandb_tracking/`](wandb_tracking/) | 2 / — | `experiments/wandb_tracking.py`. **Not pytest** — run these two as scripts (below) |

A test file belongs to the suite matching **what it imports**, not what its name suggests. `greedy/test_stable_ac.py` is in the greedy suite on purpose: it imports only `experiments/greedy_tests/{spec,adapters,fixtures}`, so it is the greedy harness's own forward-compat coverage for stable AC moves at `n_gen ≥ 3`, not a test of `experiments/stable_ac/`.

## Running them

```bash
.venv/bin/python3 -m pytest -q                                             # everything
.venv/bin/python3 -m pytest tests/greedy tests/stable_ac tests/analysis -q # the mandatory pipeline gate
.venv/bin/python3 -m pytest tests/greedy tests/stable_ac tests/analysis -q --runslow   # before any push
.venv/bin/python3 -m pytest tests/equivalence_classes -q                   # after any change to that package
```

The two `wandb_tracking` files are plain scripts, not pytest modules — no wandb server is needed for either:

```bash
.venv/bin/python3 tests/wandb_tracking/wandb_tracking_test.py
.venv/bin/python3 tests/wandb_tracking/wandb_offline_integration.py <phase>   # cum_nodes identity fresh panels resume_full resume_partial heavy
```

## The rules that make these numbers mean something

- **The default tier proves nothing about what it skipped.** `--runslow` is what carries the multiprocessing path, the golden regressions, and the deep parity matrix. Check the skip count; never push behind a green default tier alone. [`../experiments/lessons/slow-tier-caught-broken-path-test.md`](../experiments/lessons/slow-tier-caught-broken-path-test.md)
- **No test may use a node budget above `MAX_BUDGET = 1_000`.** A search at budget `B` is exactly the first `B` pops of any longer search, so a bigger budget buys a slower test, never different behaviour. Want a deeper anchor? Find a presentation that solves in *fewer* nodes. [`../experiments/lessons/test-budget-ceiling.md`](../experiments/lessons/test-budget-ceiling.md)
- **The budget ceiling caps the search, not the machinery.** Any structural threshold the ceiling cannot reach (chunk size, reservation floor, resize trigger) gets a test that drags the threshold *below* the ceiling — monkeypatch the constant, never raise the budget. [`../experiments/lessons/budget-capped-tests-miss-structural-thresholds.md`](../experiments/lessons/budget-capped-tests-miss-structural-thresholds.md)
- **A golden failure is a result change, not a stale fixture.** The search is deterministic, so a moved number means something altered it. Diagnose first; only then `python3 -m experiments.greedy_tests.tools.regen_golden`, and say why in the commit message.
- **Never assert `min_relator` / `max_relator` strings** — both are tie-broken over a `set`, so they follow `PYTHONHASHSEED`. Their lengths are deterministic; the *first-seen* strings pin discovery order.
- Markers: `slow`, `mp` (spawns real worker processes), `wandb` (needs the package), `stable` (forward-compat at `n_gen ≥ 3`). Temp files go under `.pytest_tmp/` in the repo — agent sandboxes deny `/tmp`.

## Where the support code lives

The fixtures, the executable spec, the golden corpus and the solver adapters are **not** here — they are at [`../experiments/greedy_tests/`](../experiments/greedy_tests/README.md), because production modules import them too. Do not move them under `tests/`.

Adding a stable-AC solver? Implement a `SolverAdapter` in `experiments/greedy_tests/adapters.py` and append it to `ALL_ADAPTERS`; the contract, abelianization-invariant and packed-key suites then run against it at `n_gen = 3` with no test rewriting.
