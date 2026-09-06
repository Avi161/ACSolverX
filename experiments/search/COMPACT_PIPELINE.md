# Compact substitution search

The campaign engine is ported file by file from
`claude/ac19-leftover-solver-notebook-6yan6d`, commit
`153aecfed6615d7859692a68c230dae7106db5e2`. The existing
`heuristics.greedy_search_h` remains the readable reference. Large searches use
`experiments.heuristic_search.core.hcompact.greedy_search_hcompact`, and both
arms in `run_leftovers_1m` / `run_leftovers_5m` require that engine.

```python
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
from experiments.search.heuristics import S20_MK2, BASELINE_CONFIG

stats = greedy_search_hcompact(
    "YXyxYx", "YYYYxxx", node_budget=1000,
    max_relator_length=64, config=S20_MK2, track_path=True,
)
```

Use `BASELINE_CONFIG` for the length control. `config=None` retains the
reference API's length ordering; pass `S20_MK2` for the recommended ordering.
The result has the same eleven fields. Equal-length min/max witnesses are
first-discovered states; the older public wrapper chooses from a Python set,
so those tied witness strings can differ even when the searches agree.

The engine expects the project's two-generator AC-trivial/unimodular input
corpus, using `xXyY`. It does not establish triviality of arbitrary groups:
its inherited terminal predicate assumes two singleton relators generate both
generators. Input Aut-minimization is a separate preprocessing operation; the
engine's cyclic canonicalization does not compute an Aut-minimal presentation.

## What is optimized

- Two-bit, most-significant-first storage. The heap compares actual relator
  lengths and masks a partial final byte, preserving the old string-key order.
- One full-cap-width arena reservation, with narrower live rows widened
  backward in place through scratch storage. No second arena during widening.
- Optional parent/move capture, saving 8 bytes per reserved state when disabled.
- Cut-shift skipping only for children equal to an earlier child from the same
  pop; the predecessor-emission bitmap preserves discovery order.
- Packed least-rotation canonicalization through length 64, with the reference
  fallback for longer words. Scratch buffers remove per-child allocation.
- Exact full-width state allocation plus the power-of-two visited table for
  admission, and same-generation-only measured peaks for the governor.

The source branch measured 941.6 to 209.8 microseconds/pop on `aca_47` at 300k
pops. That is historical evidence, not a claim about this machine. Its report
is `experiments/heuristic_search/core/perf_lab/REPORT.md` at the source SHA.
The frozen engines and raw source benchmark records are retained under
`core/perf_lab/` for identity and throughput comparisons.

## Capture and limits

`track_path=True` returns a replayable certificate. With capture off, a solve
returns its pop count and depth but empty `path` / `path_moves`. Re-run that
same pair with the same cap/config/cyclic setting, at `nodes_explored`, with
capture enabled, then replay its moves. A pathless solve alone is not a stored
certificate. AC19 campaigns capture; the u124 campaign disables capture.

Port fixes: explicit reservations are honored exactly; a second per-pop
allowance must not cross a hash-table size boundary behind the planner's back.
Memory generation is now **6**. Plans and allocations enforce the signed int32
capacity ceiling, **2,147,483,647 states**. Capture requires cap at most **128**
because rotation cuts are int8; without capture the storage cap is at most 255.
Reduced roots longer than the cap are rejected before storage.

The campaign governor targets Linux `/proc` and `RLIMIT_AS`. If a requested
address-space limit cannot be installed, the worker records an error and never
starts the search. The core engine and identity tests run on macOS, but the
Linux governor must not silently promise OOM protection there. Memory estimates
remain conditional on the reserved discovered-state count: a row exceeding its
reservation can fail and require a larger supported reservation.

## Verification and benchmarking

Local CPU policy: only minimal checks, presentation budgets strictly below
10,000, and no concurrent heavy validation. The user runs larger work in the
cloud. The example above uses 1,000 nodes. No further local performance runs
are authorized.

The following full verification and performance commands are for the user's
cloud machine, from the project root with NumPy, Numba, and pytest installed:

```sh
python -m pytest tests/test_compact_pipeline.py tests/test_expand_kernel.py tests/test_hcompact_kernels.py tests/test_hexpand.py tests/test_greedy_heuristic.py -q
python -m experiments.heuristic_search.core.perf_lab.gates --oracle --twin --frozen --twin-rows 6 --twin-budget 30000 --widen-lines states
python -m experiments.heuristic_search.core.perf_lab.bench --rows aca_47 --budget 300000 --reps 1 --engines frozen,candidate --out .scratch/pipeline-review/local-bench.json
```

The benchmark warms each engine before timing, alternates fresh processes, and
compares result fingerprints. Its Linux CPU affinity is unavailable on macOS;
peak RSS uses `getrusage` there. Purge Numba caches after kernel changes because
cached callers do not track source changes in other modules. The gate and
benchmark commands purge automatically. Run benchmarks without competing tests.
Subset-60 evaluation and new heuristic experiments await the user's protocol.

## Local port validation (2026-09-06)

Historical completed checks below preceded the user's local heat restriction;
they are a record, not permission to repeat these workloads locally.

- 81 focused tests passed: 27 integration/memory/capture tests and 54 existing
  heuristic plus imported expansion/hash/canonicalization tests.
- Oracle gate: 60 u124 rows at 1,000 pops, cap 64, S20_MK2, passed against the
  Python reference and the fully frozen engine.
- Twin gate: 6 u124 rows at 30,000 pops, cap 64, passed for discovered-state
  arrays, scores, parents, decoded words and widening events. These are u124
  correctness rows, not the held-back subset-60 benchmark.
- `aca_47`, 300,000 pops, cap 64, one warmed run per engine: frozen 150.112 s
  versus compact 43.534 s, **3.448x throughput**. Peak process RSS was 2.567
  versus 2.112 GiB. Full result fingerprints agree. This is a local macOS
  single-row measurement, without Linux CPU pinning or `perf stat`; no claim
  of a universal speed ratio or large-box lane count follows from it.
- Final AC19 residue-list regeneration check passed. All 62 stored 5M solve
  certificates replayed, covering 4,743 moves.

Raw local timing evidence:
`experiments/heuristic_search/core/perf_lab/results/port_macos_aca47_300k_2026-09-06.json`.
No additional optimization was selected from this timing run.
