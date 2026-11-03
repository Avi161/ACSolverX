# Replicating ACSolverES Dual / Triple GS

State of the `elliot-replication` branch, written so that someone (or an agent) starting here has the context.

**Goal.** Benchmark Elliot Steffen's greedy searches from
[ElliotSteffen/ACSolverES](https://github.com/ElliotSteffen/ACSolverES) (commit `2a458e4`, the only commit) on our
three benchmarks, and record for each row:

- nodes explored;
- CoV moves used;
- path length, i.e. S-moves plus CoV moves;
- the longest relator reached.

The searches benchmarked are the "dual" and "triple" methods. The user's constraint: a relator-length bound must
never be the reason a state is left out of the queue. The results are meant for the paper (Section 1, AC algorithms,
and Section 2, stable AC); the LaTeX source is not in this repository.

**Status.**

| step | state |
|---|---|
| Review of the friend's code | done |
| Runs at 10^4 and 10^5 nodes | done |
| Independent replay of every solved path | done |
| Time-weighted cost | done (`results/elliot_cost/`) |

**No PR, no CI.** This branch has no pull request and none should be opened. Commit and push to
`elliot-replication` only, and do not watch, run or fix CI. The draft PR #38 opened earlier was closed at the user's
request.

## Files on this branch

| path | what |
|---|---|
| `benchmark/elliot/run_elliot.py` | runner: the three methods on `ms640`, `bench60`, `ladder100`; resumable; `--from` carries solved rows from a smaller budget |
| `benchmark/elliot/summarize.py` | the summary table of a results folder (`SUMMARY_TABLE.md`) |
| `benchmark/elliot/verify_paths.py` | independent replay of every solved path in one results file |
| `results/elliot_10k/` | all 2,400 rows (800 rows x 3 methods) at 10^4 nodes; `README.md` (settings, fields), `SUMMARY_TABLE.md`, `VERIFY.json` |
| `benchmark/elliot/time_cost.py` | time-weighted cost: CPU time of the CoV callbacks, converted to substitution-pop units |
| `results/elliot_cost/` | per-row CPU time and cost units for all 2,400 rows; `README.md`, `COST_TABLE.md` |
| `results/elliot_100k/` | the same at 10^5 nodes: 2,345 rows carried from 10^4 (`carried_from`), 55 rows searched (26 distinct presentations) |

## Setup (the container is ephemeral; redo this)

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/ElliotSteffen/acsolveres /home/user/elliotsteffen/acsolveres
python3 -m venv /tmp/elliot-venv
/tmp/elliot-venv/bin/pip install -e "/home/user/elliotsteffen/acsolveres[test]"   # builds two C++17 pybind11 modules
```

- **What the install writes:** the editable install puts `native_compact_{dual,triple}_gs*.so` into the clone's
  `src/ac_final_paper/solvers/`. They are gitignored there.
- **Numba:** that venv also has numba, so `benchmark/elliot/verify_paths.py` can import `acx` from it. Set
  `NUMBA_CACHE_DIR` to a scratch folder and use `python -B`, so no cache is written into `acx/`.
- **Their tests:** `python -m pytest` fails at collection in their repo, because two `test_pipeline.py` files clash.
  Use `python -m pytest --import-mode=importlib` instead: 10/10 pass. `scripts/verify_repository.py` passes.

Run (`--workers` = cores; peak memory about 1 GB per worker at 10^5):

```bash
PY=/tmp/elliot-venv/bin/python
$PY benchmark/elliot/run_elliot.py --budget 10000 --out results/elliot_10k --workers 4
$PY benchmark/elliot/run_elliot.py --budget 100000 --from results/elliot_10k --out results/elliot_100k --workers 3
$PY benchmark/elliot/summarize.py results/elliot_100k --md results/elliot_100k/SUMMARY_TABLE.md
NUMBA_CACHE_DIR=/tmp/nc $PY -B benchmark/elliot/verify_paths.py results/elliot_10k/ms640__auto_dual.jsonl /tmp/v.json
```

## The three methods

All three use ACSolverES's `algorithm_adapters.run_algorithm` with the compact C++ engine
(`native/native_standard_successors.cpp`). The CoV children come from Python callbacks.

| our label | ACSolverES name | second / third queue | certificate |
|---|---|---|---|
| Dual, single CoV | `single_auto_cov_dual` | single CoV | `ac_path` via Aut(F2) |
| Dual, auto CoV | `auto_dual` | 24 maps x -> x y^k, y -> y x^k, 1 <= abs(k) <= 6 (`MAX_RIGHT_POWER`) | `ac_path` via Aut(F2) |
| Triple | `auto_nonauto_cov_triple` | the 24 maps, plus complete CoV | `stable_cert` if a complete CoV is on the path |

### Queue policy (native engine)

- **The sub queue.** Every new state goes into the sub queue, whatever move made it. The sub queue is ordered by
  (total length, -depth, insertion), so ties go to the deepest state, first in first.
- **CoV queues.** A state enters a CoV queue only after it is popped from the sub queue, and only if
  `standard_gap >= min_standard_moves_between_*`. The gap counts standard moves since the last CoV.
- **Dual pop rule.** The dual pops the CoV queue when `sub_head_len - cov_head_len >= threshold + 1`, which with
  threshold 2 means the CoV head is at least 3 shorter. Otherwise it pops the sub queue.
- **Triple pop rule.** The triple pops the minimum of sub+0, auto+t_a and complete+t_c, with ties going
  sub < auto < complete.
- **Seeding.** With `seed_initial_*`, the start state is CoV-expanded once before the loop, and that is not charged.
- **Duplicates.** One global `seen` map covers all queues; it compares full keys, so hash collisions cannot merge
  states. The canonical form is up to rotation, inversion and swap of the relators, not up to automorphisms.
- **Solve.** A row is solved when a state with both relators of length 1 is popped from the sub queue. The path is
  the chain of parents; `path_length` counts each CoV as one move.

### Parameters

The parameters are those of `results/ms640_final_paper_v1/config.json` in ACSolverES:

- preference thresholds 2;
- `min_standard_moves_between_*` = 0 (the function defaults are 10; the paper config uses 0);
- seeding on;
- tie `deepest`;
- `cov_min_subword_len` 2.

**We change two things:**

- **`max_len = 65`** (theirs was 50).
  - It is a strict bound on the TOTAL length |r1|+|r2|, applied to every child: standard, auto, single and complete
    CoV, and seeds.
  - 65 is the engine maximum: `PackedWord` stores each relator as 2 bits a letter in 128 bits, so at most 64 letters.
  - It is not binding. The sub queue is ordered by length, so a longer state would be popped only after every
    shorter one. Solution paths peak at total length 25, and max_len 50 vs 65 gave identical pops on every row
    checked.
  - Lifting the cap is a mechanical change, about 50 lines in the C++ (`std::array<uint64_t, W>`).
  - The pure-Python engines (`run_dual_single_cov_gs`, `run_dual_auto_cov_gs`, `run_triple_gs`) have no cap and gave
    identical results on the rows tested. They are 4 to 43 times slower.
- **`max_live_frontier_states = None`** (theirs was 5,000,000).
  - When their cap is hit, the engine silently keeps only the shortest half of the frontier: a length-based drop,
    which the user does not allow.
  - Worse, in the TRIPLE engine the dropped states stay in `seen` and are never re-enqueued (`cpp:2108-2117`; the
    dual erases them correctly). That is a bug.
  - With no cap, `frontier_prune_count` is 0 on every row here. The frontier grows by about 74 states a pop, about
    740k states at 10^4 nodes. Every row is solved by 21k nodes, so memory was never a problem.

## Review findings

### CoV soundness (all steps replayed; see VERIFY.json)

- **Auto CoV** is an automorphism of F2 applied to both relators.
- **Single CoV is always an automorphism**, even though it is built as define/eliminate.
  - Let w be a prefix of a rotation of the source relator R, with R = w u. Let t be the generator to eliminate and s
    the other one.
  - The code requires t to occur once in u, so u = s^p t^e s^q. Define z := w and solve z u for t:
    t = s^-p z^-e s^-q.
  - Let psi be s -> s, t -> s^-p z^-e s^-q. Then psi(u) = z^-1, the new pair is (psi(Q), psi(R)^-1), and
    {s, s^-p z^-e s^-q} is a basis of F2.
  - Hence the single-CoV dual gives AC paths via Aut transport. The name "Single-Auto-COV" is accurate.
- **The triple's complete CoV is never an automorphism.**
  - k >= 2 copies of w in the rotation are replaced by z, and the other relator is rewritten greedily
    (w -> z, w^-1 -> Z).
  - The eliminated generator's image has z-exponent sum of absolute value k >= 2, so psi is not onto H1.
  - It is a valid Tietze move: add z with Z w, rewrite, eliminate t. So it proves stable AC-triviality only.
  - It is flagged in our records as `kind: "stable_cert"`.
  - Their "non-automorphic" filter only quotients by signed letter permutations plus rotation, inversion and swap, not
    by full Aut(F2). Harmless, but the name overstates it.
- **Logging.** Single-CoV moves are logged as `move_type: "complete_cov"` with `cov_variant: "single_cov"`. The
  runner relabels them `single_cov`; do not filter on `move_type` alone.
- **S-moves.** Every logged standard move is a genuine seam-cancelling S-move. No unsound step was found anywhere.

### Engine and accounting (severity)

- **High: triple frontier pruning blacklists states** (above). Avoided with `max_live_frontier_states=None`.
- **Medium: pruning changes results silently.** It is recorded only as `frontier_prune_count`; our runs record it per
  row, and it is 0 on every row.
- **Medium: empty complete-CoV pops are free in the triple** (`cpp:2366-2369`), so `max_len` can change the triple's
  node count.
- **Medium: the Python dual reference engine re-expands the seeded start state** (`dual_single_cov_gs.py:674`). It
  differs from the native engine by at most one node without pruning.
- **Low:**
  - the dual's `best_id` can point at a pruned record (an `out_of_range` at path reconstruction), only with pruning;
  - a budget off-by-one when the trivial state appears on the last pop;
  - the C++ dual does not validate its inputs;
  - unreachable undefined behaviour on an empty relator.
- **Deterministic.** The search is deterministic and the budget only stops it. So solved at budget B is the same as
  nodes <= B, and a row solved at a smaller budget is solved identically at a larger one. That is what `--from` relies
  on.

### Node accounting: NOT time-weighted

`nodes` counts one per pop from any queue, sub or CoV, at equal weight. It does not charge:

- seeding, i.e. CoV-expanding the start state;
- generating CoV candidates, which happens in Python;
- empty complete-CoV pops.

CoV pops are a small share of the nodes, from ACSolverES's committed MS640 run (identical to ours row for row):

| method | nodes | sub pops | CoV pops |
|---|---|---|---|
| Dual, single CoV | 328,688 | 324,184 | 4,504 single (1.4%) |
| Dual, auto CoV | 216,023 | 215,072 | 951 auto (0.4%) |
| Triple | 216,292 | 215,101 | 941 auto + 250 complete (0.6%) |

Wall time per counted node over the 10^5 run, which includes the uncharged work:

| method | MS640 | ladder100 |
|---|---|---|
| Dual, single CoV | 0.23 ms | 0.30 ms |
| Dual, auto CoV | 0.17 ms | 0.19 ms |
| Triple | 0.18 ms | 0.18 ms |

These ran with 3–4 parallel workers, so treat them as ±20%. They are C++ engine times, so they cannot be compared with
the paper's pure-Python ms-per-pop table.

## Benchmarks (loaded by `run_elliot.load_bench`)

- **`ms640`** = `data/ms640_solved.txt`; the row id is the line index.
  - ACSolverES's `data/gssub_baseline_ms640.csv` has the same 640 presentations in the same order.
  - Its nodes equal our GS-SUB g in `benchmark/difficulty_bins.csv`.
- **`bench60`** = `benchmark/subsets/benchmark_subset_60.csv`; its ids are MS640 line numbers.
- **`ladder100`** = `benchmark/ladder/ladder_default.csv`, the paper's ladder100.
  - It reproduces the paper's LENGTH (11/20/40/60/80) and S20_MK2 (23/53/69/87/91) counts.
  - Do not use `acx`'s `benchmark=ladder100`: it loads `ladder_100.csv`, which has 99 rows and is not the paper's set.
  - Its `ms_*` rows are MS640 rows.
- **Starting lengths:** at most 25 total and at most 19 per relator on every benchmark.

## Results

Solved at 10^3 / 10^4 / 10^5 nodes. LENGTH and S20_MK2 are the paper's numbers; the hybrid is 640/640, 60/60 and
99/100 / 100 at 10^3 / 10^4.

| benchmark | Dual, single CoV | Dual, auto CoV | Triple (stable_cert rows) |
|---|---|---|---|
| MS640 | 604 / 627 / 640 | 618 / 634 / 640 | 618 / 634 / 640 (54) |
| bench60 | 46 / 52 / 60 | 51 / 56 / 60 | 51 / 56 / 60 (7) |
| ladder100 | 64 / 92 / 100 | 80 / 97 / 100 | 86 / 97 / 100 (17) |

- **Every row is solved within 20,819 nodes**, so a budget of 10^6 or 10^7 gives the same table.
- **Hardest rows:** for all three methods, MS640 rows 616–625 and 636–639, plus `ac19_70845` for the single-CoV dual.
  Ladder levels 7–10, which LENGTH fails at 10^7, are all solved at 10^4.
- **Full per-benchmark metrics** are in `results/elliot_100k/SUMMARY_TABLE.md`: nodes mean, median and max; path;
  S-moves; CoV moves; longest relator.
- **Path climb:** the longest relator on any solution path is 19, and the longest total 25. A path climbs at most 6
  letters above its start.
- **Compared with the hybrid** on ladder100: about 10 times more nodes (mean about 1,330 against 127 units) and
  paths about 2.4 times longer (121 against 49.7).
- **Recommendation for the paper:**
  - The auto dual is the cleanest AC method of the three.
  - The triple matches it but adds stable-only certificates. It belongs in Section 2, or needs its 54 / 7 / 17 rows
    flagged.
  - The complete-CoV queue adds almost nothing: 86 against 80 ladder rows at 10^3, the same counts from 10^4 up.

### Checks done

- **Exact match with ACSolverES:** all 640 MS640 rows equal its committed 10^6 run
  (`results/ms640_final_paper_v1/*.csv`) in nodes and path, for all three methods.
- **bench60:** its rows equal their MS640 rows.
- **Replay:** `VERIFY.json` in both results folders has `all_pass: true`. Every step of every solved path was replayed
  (S-move, Aut orbit, CoV rebuilt or regenerated), and the count of non-orbit rows equals the `stable_cert` count.

## Time-weighted cost (`results/elliot_cost/`, done)

`benchmark/elliot/time_cost.py` wraps the CoV callbacks that the C++ engine calls with a CPU timer, without changing
ACSolverES or the results. It converts the callback time into substitution-pop units:

    cost = nodes + callback_s / t_pop,    t_pop = engine time / nodes,  about 0.2 ms

A substitution pop does the work of one LENGTH expansion, so these are LENGTH-expansion units algorithmically.

**Cost of one CoV step, in substitution pops:** single CoV about 25; auto CoV about 5–6; the triple 7–11 (empty
complete-CoV pops included). Seeding the start state costs about 23–34 for single CoV and 4–6 for auto.

**cost / nodes:**

| method | MS640 | bench60 | ladder100 |
|---|---:|---:|---:|
| Dual, single CoV | 1.42 | 1.35 | 2.01 |
| Dual, auto CoV | 1.03 | 1.02 | 1.14 |
| Triple | 1.11 | 1.07 | 1.16 |

**Solved within a budget in cost units (10^3 / 10^4 / 10^5):**

| method | MS640 | bench60 | ladder100 |
|---|---|---|---|
| Dual, single CoV | 593 / 621 / 640 | 43 / 52 / 60 | 56 / 82 / 100 |
| Dual, auto CoV | 614 / 634 / 640 | 51 / 56 / 60 | 77 / 96 / 100 |
| Triple | 612 / 634 / 640 | 49 / 56 / 60 | 81 / 97 / 100 |

All rows are still solved within 10^5 cost units; the max is 61,821, single CoV on `ac19_70845`. Details and caveats
(timing ±10%, 2 workers on 4 cores) are in `results/elliot_cost/README.md`.

## Open items

1. **The paper text.** Nothing is written into the LaTeX yet: no tables or paragraphs for Sections 1 and 2, and no
   citation of ACSolverES (it has a `CITATION.cff`). The `.tex` file is not in this repository; ask the user for it,
   or draft the text for them to paste.
2. **The Python-layer review.** The review of ACSolverES's Python policy layer started, but its report never came
   back. The C++ review, the build tests and the exact reproduction cover most of its scope.
3. **Optional:** lift the 65 cap in the C++ (mechanical) if a benchmark with longer paths is ever run.

## How the user works

- Read context first.
- Ask clarifying questions and show a short plan before running anything expensive.
- Never delete files without approval.
- Keep replies short, outcome first.
