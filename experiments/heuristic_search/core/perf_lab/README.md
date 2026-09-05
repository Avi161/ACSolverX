# perf_lab

A performance lab for `hcompact.py` (`HCompactSolver` / `greedy_search_hcompact`): a
frozen reference engine to compare against, an A/B throughput bench, and a set of
equivalence gates a candidate change must pass before it is trusted for speed
numbers at all.

Everything here assumes the repo root as `cwd` and `PYTHONPATH=.` (every module in
this repo, this one included, walks up from its own `__file__` to find the root and
inserts it into `sys.path` itself, so this also works if you invoke a script by
absolute path from somewhere else).

## Layout

- `hcompact_baseline.py` -- a verbatim copy of `hcompact.py` as it stood at commit
  `5d047da5`, plus one comment line at the top. **Never edit this file.** It is the
  fixed yardstick every candidate is measured against; if it moves, "faster than
  baseline" stops meaning anything.
- `bench.py` -- times the frozen baseline against a candidate engine (by default,
  the live `experiments/heuristic_search/core/hcompact.py`) and reports pops/second,
  peak RSS, and per-state memory.
- `gates.py` -- proves the candidate's search is bit-identical to the oracle and to
  the baseline before any speed number from `bench.py` is meaningful.
- `frozen/` -- `hcompact_frozen.py` (the text of `hcompact_baseline.py`) importing
  verbatim copies of `experiments/search/greedy_baseline.py` and
  `experiments/heuristic_search/core/hfast.py` as they stood at `9b98e313`.
  **Never edit these either.** `hcompact_baseline.py` imports the *live*
  kernels, so a change to `greedy_baseline.py` or `hfast.py` moves the baseline
  and the candidate together: `bench.py` would report a ratio of ~1.0 for a real
  speedup and `gates.py --twin` would pass on a changed search. For kernel work
  the yardstick is `--engines frozen,candidate` and `gates.py --frozen`.
- `phase_split.py` / `PHASE_SPLIT.md` -- the per-pop phase split by replay (see
  the file header) and its measured result on this box.

## numba's on-disk cache and why both scripts purge it

Every hot function is `@njit(cache=True)`. numba keys a cached function on its
*own* source file's stamp and bytecode (`numba/core/caching.py`,
`get_source_stamp` / `_index_key`); callees compiled into it from *other* files
are not tracked. After an edit to `greedy_baseline.py` or `hfast.py`, every
cached caller in an unchanged file -- `_run_chunk_h` in `hcompact.py`, the
frozen engines, the replay kernels in `phase_split.py`, any test that reaches
the kernel through the engine -- reloads machine code with the **old** kernel
linked in, and a gate or a bench then exercises code that is not in the working
tree. (This lab hit exactly that: a kernel edit measured at 0.47x in isolation
showed no change through the engine until the cache was cleared.) `bench.py`
and `gates.py` therefore delete `*.nbi`/`*.nbc` under `experiments/` before
doing anything (`purge_numba_cache`), at the cost of one recompilation per
process, which the bench's warm-up call already keeps out of the timed run.
Run the same purge by hand before `pytest` after a kernel edit.

## Running the bench

```
PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/bench.py \
    --rows aca_0,aca_1,aca_3,aca_4,aca_5,aca_8 \
    --budget 200000 --reps 3 --mrl 64 --cpu 1 \
    --out /tmp/bench.json
```

For each row, for each rep, each engine is run once in a **fresh subprocess**:
pin to `--cpu`, do a throwaway 2,000-node warm-up call (so numba's first-call
compilation is not charged to the timed run), then time exactly one
`greedy_search_hcompact` call with `time.perf_counter`. Engines alternate
A,B,A,B,... within a row (not "all of A's reps, then all of B's") so that any
drift over the run's wall-clock span -- another job landing on the box, thermal
throttling -- lands on both engines equally rather than favouring whichever one
happens to run first or last.

Each run also builds a second, unsolved `HCompactSolver` with identical
arguments purely to read `bytes_per_state()` and `bytes_reserved()`, and computes
a sha256 "record fingerprint" of the full returned dict (JSON, sorted keys). The
aggregate table reports, per row per engine, median/min/max pops/second and peak
RSS (`VmHWM`, from `/proc/self/status`), plus the
`candidate / baseline` ratio of median pops/second -- and it loudly flags any row
where the two engines' fingerprints disagree, because in that case the timing
comparison is meaningless (the engines searched different things).

Useful flags: `--engines baseline,candidate` (comma list; order sets the
alternation; `frozen` is the fully-frozen engine for kernel work, and the
reported ratio is candidate over whichever of `baseline`/`frozen` is present),
`--rows` (comma list of names from `results/stable_ac/fable/aca_124.csv`),
`--reps`, `--budget`, `--mrl`, `--cpu`, `--out`.

A smoke-sized run (`--rows aca_0,aca_1 --budget 20000 --reps 2`) takes on the
order of two minutes on this box; the default (6 rows x 3 reps x 2 engines at
200,000 nodes) is a much longer campaign -- budget accordingly.

## Running the gates

```
PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/gates.py --all
```

`--frozen` switches the baseline in `--oracle` and `--twin` to `frozen/hcompact_frozen.py`
(frozen kernels too); it is the only way either gate can see a change to
`greedy_baseline.py` or `hfast.py`, and is required to certify one.

`--all` runs the three gates below in order and **stops at the first failure**
(no reason to spend the twin or suite gate's time once the oracle gate has
already found a divergence). Each gate can also be run alone; every mismatch is
printed with the concrete values on both sides, not just "differs".

### `--oracle` (default 60 rows, budget 1,000, `mrl=64`, `config=S20_MK2`)

For `aca_0 .. aca_{N-1}`: the candidate's `greedy_search_hcompact` (called with
`track_path=False`) is compared field for field against the pure-Python oracle,
`hsolve.greedy_search_h(..., keep_path=False)`, on exactly the fields
`tests/test_leftovers_5m.py`'s
`test_the_engine_path_matches_the_python_oracle_field_for_field` compares
(`solved`, `nodes_explored`, `path_length`, `min_relator_length`,
`max_relator_length`, `max_relator_length_expanded`, `path`, `path_moves`); AND
the candidate's full returned dict is compared against the frozen baseline
engine's, key for key.

**What it proves:** the candidate reproduces the reference search's semantics
(not just "a plausible search") across many different presentations, cheaply
enough to run on every change. It does **not**, on its own, prove bit-identical
internals -- a budget of 1,000 rarely reaches interesting arena-widening or
capacity-growth code paths. That is what `--twin` is for.

### `--twin` (default 12 rows, budget 100,000, `mrl=64`, `config=S20_MK2`, `track_path=True`)

For `aca_0 .. aca_{N-1}`: an `HCompactSolver` is constructed from the candidate
module and from `hcompact_baseline` with **identical** arguments, both are
solved, and compared exactly:

- the `(solved, nodes)` tuple `solve()` returns;
- every scalar the solver tracks: `n_discovered`, `min_id`/`min_total`,
  `max_id`/`max_total`, `max_expanded_id`/`max_expanded_total`, `solved_depth`,
  `solved_id`, and the `widened` counter;
- with `numpy.array_equal`, the `[:n_discovered]` prefixes of `len1`, `len2`,
  `depth`, `seg`, `score`, `parent`, `pmove` -- this is the layout check, and
  it is why a *candidate that stores rows differently* would fail here even if
  its answers were right;
- every decoded relator string, `solver.relators(sid)`, for
  `sid` in `0 .. min(n_discovered, --decode-max) - 1` -- this is deliberately
  a check on **decoded strings**, not on raw arena bytes, so a candidate that
  changes the byte layout (different width, different packing) but preserves
  what each state actually *means* still passes;
- the exact `"rows widen ..."` lines each engine prints while solving. With
  `--widen-lines states` only the `at N states` figure of each line (and the
  number of lines) must match: that figure is the pop at which the rows
  widened, i.e. part of the search's fingerprint, whereas the `aB -> bB`
  widths describe the row layout -- a candidate that packs symbols in fewer
  bits prints different widths at the very same pops. The default stays
  `exact`; a report that used `states` should say so.

**Capturing the print lines:** the two prints in `hcompact.py`
(`_grow`/`_grow_width`) are plain Python `print()` calls, but the gate captures
them by redirecting the real OS file descriptor 1 (`os.dup2`) around each
`solve()` call, not via `contextlib.redirect_stdout` -- `redirect_stdout` only
patches `sys.stdout`, which would miss output from a numba-compiled kernel or
any other code that writes straight to fd 1. The gate cross-checks that the
captured line count for each engine equals that engine's own `solver.widened`
counter before trusting the line-by-line comparison, so a silently-broken
capture shows up as its own failure rather than a false pass.

**What it proves:** the candidate is bit-identical to the frozen baseline on
real, long-enough searches that they exercise capacity growth and (at `mrl=64`
with the adaptive-width engine) row widening -- the parts of the engine a
1,000-node oracle sweep is too short to reach.

### `--suite`

Runs `python -m pytest tests/test_leftovers_5m.py -q` in the worktree and
reports pass/fail. This is the project's own existing test suite; the gate
exists so "the harness's gates pass" and "the suite the rest of the repo
trusts passes" are checked from the same command.

## Promotion criteria

A candidate is promotable when **all three gates pass bit-identically**
(`--all` exits 0), **and** at least one of:

- median pops/second improves by **>= +10%** across the default bench rows
  (`aca_0,aca_1,aca_3,aca_4,aca_5,aca_8`), with `bytes_per_state` within **+1%**
  of the baseline (i.e. the speedup did not come from spending materially more
  memory per state); or
- `bytes_per_state` improves by **<= -15%** (a 15%+ reduction), with median
  pops/second within **-3%** of the baseline (i.e. the memory saving did not
  cost meaningful speed).

Bit-identical gates are the gate on trustworthiness; the pops/second and
bytes_per_state thresholds are the gate on whether the change is worth taking.
Neither substitutes for the other -- a 20% speedup on a search that is not
actually the same search is not a result, and a bit-identical change that is
neither faster nor smaller is not a promotion candidate.

## About this box, and reading the numbers with that in mind

This box has **4 cores and 15 GB RAM**, and other agents may be running
concurrently on it. A 100k-pop run of a real `u124`-class row uses roughly
1-2 GB, so keep `--budget` modest for exploratory bench runs -- the defaults
here (200,000 nodes, 3 reps, 6 rows) are already a real campaign, not a smoke
test (`bench.py --rows aca_0,aca_1 --budget 20000 --reps 2` is closer to a
smoke test, and is what this lab's own setup was verified with).

Because the box is shared, a single measurement is not a result -- that is the
entire reason `bench.py` runs multiple reps, alternates engines within each
row instead of block-scheduling them, and reports median (not mean, which one
stalled subprocess can drag arbitrarily far) alongside min/max so a suspiciously
wide spread is visible rather than hidden inside an average. If the
`candidate/baseline` ratio for a row looks off, check whether that row's min
and max are close together (a tight, believable measurement) or far apart (this
box was busy; re-run rather than trust it).
