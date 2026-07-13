# `experiments/analysis/`

Builds the **stable-AC benchmark**: which presentations to test a new technique on, and what bar it
has to clear. Read-only over `results/greedy_baseline/`; writes `results/benchmark/`.

Run them in this order — each consumes the previous one's output:

```bash
.venv/bin/python3 -m experiments.analysis.difficulty_bins      # -> results/benchmark/difficulty_bins.csv
.venv/bin/python3 -m experiments.analysis.benchmark_subsets    # -> results/benchmark/subsets/
.venv/bin/python3 -m experiments.analysis.reach_tier           # -> results/benchmark/reach/
```

**Use `-m`.** Running them by path (`python3 experiments/analysis/difficulty_bins.py`) fails with
`ModuleNotFoundError: No module named 'experiments'`.

| module | what it does |
|---|---|
| `whitehead.py` | **library.** Whitehead's algorithm for F₂ — the `Aut(F₂)` canonical form. Also serves as the *independent* cross-check for `equivalence_classes/lib/autcanon.py`: same theory, separately written, and it computes no witness, so agreement between the two is real evidence rather than a tautology. |
| `difficulty_bins.py` | labels all 640 ms640 presentations with a difficulty bin + Aut class |
| `benchmark_subsets.py` | the **efficiency ladder** — subsets of 10/20/40/60 |
| `reach_tier.py` | the **reach tier** — 1/2/4/6 genuinely-unsolved problems |

---

## The two tiers ask different questions, so they count differently

| tier | asks | scored on | deduped by Aut class? |
|---|---|---|---|
| **ladder** (`benchmark_subsets`) | is the technique more **efficient**? | node-speedup, path-speedup, Pareto | **No** |
| **reach** (`reach_tier`) | does it get **further**? | `solved`, and `progress` | **Yes** |

Opposite calls, for opposite reasons — and neither is an oversight.

On the **ladder** the unit is a *search instance*. Search cost is **not** an `Aut(F₂)` orbit
invariant: presentations 623 and 636 are provably Aut-equivalent yet cost 59,710 vs 213,882 nodes
(3.6×). Two coordinate systems on one problem are two genuinely different tests — and that gap is
precisely what a change-of-variables technique sets out to exploit. If cost *were* an orbit
invariant, CoV could never gain anything. So `aut_class` is a **column, not a dedup key**.

On the **reach** tier the unit is a *problem cracked*. Running the same problem in eight coordinate
systems and cracking it once is one result, not eight. So there it *is* a dedup key.

## Why the bins are log-width, not deciles

Difficulty is multiplicative: 10 → 20 nodes doubles the work, 500,000 → 500,010 is nothing. Ten equal
slices of `log10(nodes)` make each bin **×3.37** the one below it. Deciles would put *five of the ten
levels* inside `nodes ≤ 11`, because half of ms640 solves that fast.

## Why the within-bin pick is by `path_length`

The bin already pins `nodes` to a ×3.37 window — there is nothing left to spread on there. `path`
inside one bin runs to **×11**. Sorting by path puts the node/path off-diagonal on every rung of the
ladder for free; sorting by nodes would hand back a set sitting on the diagonal, and the path graph
would be a rescaled copy of the nodes graph.

## `progress`, not `min_relator_length`

`progress = min_relator_length − (|r1| + |r2|)` — how far *below its own starting length* the search
got. Raw `min_relator_length` is degenerate: 247 of the 261 sit exactly at their start even after 1M
nodes. `progress` discriminates — ms640's hard-but-solvable bins 8–9 reach −5 to −8, the genuinely
walled 261 sit at 0.

**Read `progress` as effort, never as promise.** Only 7 of the 126 classes have `progress < 0`, and
they are the *longest* presentations — so it ranks slack to shed, not likelihood of success.
