# `experiments/analysis/`

Builds the **stable-AC benchmark**: which presentations to test a new technique on, and what bar it
has to clear. Read-only over `results/greedy_baseline/`; writes `results/benchmark/`.

Run them in this order — each consumes the previous one's output:

```bash
.venv/bin/python3 -m experiments.analysis.difficulty_bins      # -> results/benchmark/difficulty_bins.csv
.venv/bin/python3 -m experiments.analysis.benchmark_subsets    # -> results/benchmark/subsets/
.venv/bin/python3 -m experiments.analysis.reach_tier           # -> results/benchmark/reach/
.venv/bin/python3 -m experiments.analysis.combined_benchmark   # -> results/benchmark/combined/
```

**Use `-m`.** Running them by path (`python3 experiments/analysis/difficulty_bins.py`) fails with
`ModuleNotFoundError: No module named 'experiments'`.

| module | what it does |
|---|---|
| `whitehead.py` | **library.** Whitehead's algorithm for F₂ — the `Aut(F₂)` canonical form. Also serves as the *independent* cross-check for `equivalence_classes/lib/autcanon.py`: same theory, separately written, and it computes no witness, so agreement between the two is real evidence rather than a tautology. |
| `difficulty_bins.py` | labels all 640 ms640 presentations with a difficulty bin + Aut class |
| `benchmark_subsets.py` | the **efficiency ladder** — subsets of 10/20/40/60 |
| `reach_tier.py` | the **reach tier** — 1/2/4/6 genuinely-unsolved problems |
| `combined_benchmark.py` | **ladder + reach in one file** — `benchmark_combined_{11,22,44,66}` (subset_10+reach_1 … subset_60+reach_6); what a technique sweep consumes via `load_combined` |

---

## The two tiers ask different questions, so they count differently

| tier | asks | scored on | deduped by Aut class? |
|---|---|---|---|
| **ladder** (`benchmark_subsets`) | is the technique more **efficient**? | node-speedup, path-speedup, Pareto | **Minimally automorphic** (2026-07-15) |
| **reach** (`reach_tier`) | does it get **further**? | `solved`, and `progress` | **Yes** |

On the **reach** tier the unit is a *problem cracked*. Running the same problem in eight coordinate
systems and cracking it once is one result, not eight. So there `aut_class` is a hard dedup key.

The **ladder** is *minimally automorphic* (policy change 2026-07-15; before that `aut_class` was a
column only). Two Aut-equivalent presentations are one problem in two coordinate systems — the same
lesson the 261 unsolved reps taught when they collapsed to ~125 classes — so a subset that repeats a
class over-samples that orbit. Selection now guarantees, in priority order: (1) no two picks share an
`aut_class` wherever the bins allow it, (2) forced duplicates are spread evenly across the available
classes, (3) within those constraints the old path-length even-spread rule decides. Every subset is
verified against the true optimum (bipartite matching, `_distinct_bound`): **10/10, 19/20, 33/40,
45/60** distinct classes. The residue is forced by the hard bins — bins 8+9 hold 12 presentations in
only **3** classes (106 ×8, 97 ×2, 108 ×2) and bin 7 holds 14 in 4 — and is flagged per row in the
JSON and as black-edged diamonds in `subset_coverage.png`.

The forced duplicates are still genuinely different *search instances*: cost is not an orbit
invariant (623 and 636 are Aut-equivalent yet cost 59,710 vs 213,882 nodes, 3.6× — precisely the gap
a change-of-variables technique exploits). They are informative; they are just no longer chosen when
a distinct class was available.

## Why the bins are log-width, not deciles

Difficulty is multiplicative: 10 → 20 nodes doubles the work, 500,000 → 500,010 is nothing. Ten equal
slices of `log10(nodes)` make each bin **×3.37** the one below it. Deciles would put *five of the ten
levels* inside `nodes ≤ 11`, because half of ms640 solves that fast.

## Why the within-bin pick is by `path_length`

The bin already pins `nodes` to a ×3.37 window — there is nothing left to spread on there. `path`
inside one bin runs to **×11**. Sorting by path puts the node/path off-diagonal on every rung of the
ladder for free; sorting by nodes would hand back a set sitting on the diagonal, and the path graph
would be a rescaled copy of the nodes graph. Since 2026-07-15 the path spread is the *tie-break
under* the Aut-class constraint above, not the primary criterion — in practice the rich bins (0–6
hold 8–58 classes each) still get near-exact even spacing, because a class collision only ever
shifts a pick by a rank or two.

## `progress`, not `min_relator_length`

`progress = min_relator_length − (|r1| + |r2|)` — how far *below its own starting length* the search
got. Raw `min_relator_length` is degenerate: 247 of the 261 sit exactly at their start even after 1M
nodes. `progress` discriminates — ms640's hard-but-solvable bins 8–9 reach −5 to −8, the genuinely
walled 261 sit at 0.

**Read `progress` as effort, never as promise.** Only 7 of the 126 classes have `progress < 0`, and
they are the *longest* presentations — so it ranks slack to shed, not likelihood of success.
