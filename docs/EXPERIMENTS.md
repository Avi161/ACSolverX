# Running a reproducible experiment

Use this workflow for a new comparison. [USAGE.md](USAGE.md) is the flag and output reference;
[METHODS.md](METHODS.md) explains the algorithms, and [ARCHITECTURE.md](ARCHITECTURE.md) maps the implementation.

## 1. Check the environment and a small input

From a checkout, install with Python 3.12 and run the smoke configuration into a new folder:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
export NUMBA_NUM_THREADS=1
export OMP_NUM_THREADS=1
python run.py --config configs/smoke.toml --set name=demo_smoke
```

The first search loads/compiles Numba kernels. The runner warms each worker before timing its rows. Check that
`summary.json` has `errors = 0`; an unsolved row spent its search budget or exhausted its frontier, while an error
row did not complete a valid search. The runner retains error rows on resume, so correct the cause and use a new
run name to retry them.

To use your own data, start with `--input examples/presentations.csv` or `--pres "xxYYY, xyxYXY"`. The supported file
formats and identifier rules are in [USAGE.md](USAGE.md#inputs). `--rows 0:20` selects positions, while a
TOML list such as `rows = ["0:1", "one,two"]` selects those exact identifiers.

## 2. Compare one setting at a time

These commands use the same input, slice, cap, budget and backend; only the priority changes:

```bash
python run.py --config configs/greedy_fast.toml --set name=demo_length --set benchmark=bench60 --rows 0:20 --set search.budget=1000 --set path=false
python run.py --config configs/greedy_fast.toml --set name=demo_s20 --set benchmark=bench60 --rows 0:20 --set search.budget=1000 --set search.priority=s20_mk2 --set path=false
python compare.py results/demo_length results/demo_s20 --html demo_comparison.html
```

`path=false` records unverified search outcomes and depths. It omits certificate construction/replay where the
method permits, so compare timings with the same capture setting. Different methods count different work: hybrid
units and policy evaluations cannot be compared directly to greedy pops. Use solve rate plus CPU time, and read the
cap counters before interpreting a miss as a budget limit.

Without `--common`, cost/path means cover each run's own solves; those sets can differ. `--common` restricts those
means and CPU columns to rows every run solved. It is useful for matched comparisons, but excludes hard rows solved
by only one method. Always retain the overall solve counts too.

## 3. Extend or resume without mixing settings

Rerun an unchanged command to resume. To add rows to the same experiment, extend `--rows`; completed rows are skipped.
You may change `workers` between invocations. With process workers, keep the thread limits above at one to avoid
oversubscribing the machine.

Every new run writes `provenance.json`: a SHA-256 identity of the package/entry-point source, Python and relevant
dependency versions, plus each invocation's git revision/dirty status, host, thread settings, worker count and row
selection. RL also hashes its checkpoint. Resume refuses changed source or runtime identity; use a new name after
changing the code or dependencies. A documentation-only commit can resume because git revision itself is not the
guard. Files containing code comments/docstrings do count as source changes.

Older folders lacking this manifest can resume, but `prior_results_untracked: true` explicitly marks their missing
history. This does not establish the provenance of old records. Input identity is held by each record's `pres` or
the sweep row's `ident`; archive your input alongside the run. The manifest is an execution record, not a dependency
lockfile or a guarantee of identical timing on another machine.

Use one writer per run directory. `workers` manages concurrency within that writer; separate jobs should use
separate names. `--fresh` discards the named run's earlier results. Never apply it to shipped published folders.

## 4. Capture certificates for results you will report

Rerun the solved rows with the same solver settings and path capture enabled:

```bash
python run.py --config configs/greedy_fast.toml --set name=demo_length_paths --set benchmark=bench60 --set search.budget=1000 --solved-from results/demo_length --set path=true
```

This creates a separate certified run. Its row count is the number solved by `demo_length`, so it is not a new
solve-rate experiment on all 20 rows. `--solved-from` checks presentation identity, including custom ids containing
commas or slice-like text. Replay shares word/move definitions with the Python implementation; see the verification
trust boundary in [METHODS.md](METHODS.md#14-verification).

Keep the following evidence together:

| artifact | purpose |
|---|---|
| input file and its dataset source | establishes which mathematical objects were searched |
| `config.json`, `provenance.json` | settings, source/runtime identity and invocation history |
| `paths.jsonl` | per-row outcomes, errors, timings and captured certificates |
| `summary.json` | aggregate counts; insufficient by itself to replay the experiment |

For timing claims, run several warmed repetitions under **different names**, alternate settings, and report the
distribution and machine load. Repeating a completed name measures resume, not search. Preserve whether timings
include replay/decoding. Historical tables in [PERFORMANCE.md](PERFORMANCE.md) retain their original environments;
they are not automatically updated when the code changes.

## Rank-n studies and policy training

Rank-n sweeps use `rows/<encoded-id>.npz` instead of `paths.jsonl`; follow [RANK3.md](RANK3.md) for commands and
`python -m acx.ngen.sweep ... --verify N` to replay saved paths and recheck `N` sampled cells on both backends.
The sweep generates combinations lazily and captures only selected paths. Per-start result arrays and the word
pool still grow with the experiment, and a row is checkpointed only when that entire row finishes. Begin with a
small `rankn.max_len` and a few rows. An oracle's best start is a different research quantity from a solver that
must discover that start within a budget.

For a small CPU PPO training smoke test after `pip install -e '.[rl]'`:

```python
from acx import data
from acx.rl.ppo import encode_rows, train

states = encode_rows(data.load("ms640", ids=range(12)))
model = train(states, updates=2, envs=8, steps=6, minibatches=2, micro=16, seed=142)
```

Training rejects unknown settings and invalid shapes/ranges before optimization. Minibatches partition every
rollout sample exactly once per epoch; `micro` changes gradient accumulation, not the sample set. Singleton
minibatches skip advantage normalization. Save the resulting `model.state_dict()`, the complete training settings
and the input/source environment yourself: the `run.py` manifest covers solver runs, not direct calls to `train`.
