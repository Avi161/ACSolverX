# The eight CoV-resistant presentations escape at budget 20,000 — and the escape is mostly a relabel

`ms622`–`ms625` and `ms636`–`ms639` are the eight rows of the 60-presentation benchmark that neither the greedy nor **any** change of variables solves at 10,000 nodes ([the b10k table](../greedy_vs_bestcov_subset60_b10000.csv), [the three-way comparison](../../../comparison/three_way_b10k_subset60.csv)). They are not eight problems: all eight share `aut_class 106`, sit in **one** Aut(F₂) orbit, and share the relator `YYYYYYYYXyyyyyyyx`. This run re-ran their entire subword-CoV family at **budget 20,000** and nothing else changed.

**All eight escape.** Every one of them has a change of variables that trivialises within 20,000 nodes.

| | tried | solved | best CoV, nodes | path | blind restart, E[nodes] | greedy @1M | blind vs greedy | tuned heuristic @100k |
|---|---|---|---|---|---|---|---|---|
| `ms622` | 169 | 50 | 14,469 | 489 | 62,749 | 78,774 | 1.26× | 62,530 |
| `ms623` | 169 | 50 | 14,352 | 488 | 62,524 | 59,710 | 0.95× | 62,528 |
| `ms624` | 169 | 50 | 14,385 | 488 | 62,817 | 59,971 | 0.95× | 62,509 |
| `ms625` | 169 | 50 | 14,447 | 489 | 63,029 | 78,770 | 1.25× | 62,511 |
| `ms636` | 172 | 39 | 14,447 | 489 | 82,975 | 213,882 | 2.58× | 62,515 |
| `ms637` | 173 | 40 | 14,413 | 489 | 80,943 | 271,866 | 3.36× | 62,528 |
| `ms638` | 173 | 40 | 14,469 | 489 | 81,099 | 213,878 | 2.64× | 62,534 |
| `ms639` | 172 | 40 | 14,444 | 489 | 80,803 | 272,953 | 3.38× | 62,509 |

Per-row provenance (`best_z`, `iso_gen`, `iso_index`, the transformed pair, and whether it left the input orbit) is in [`escape_b20000_summary.csv`](escape_b20000_summary.csv); every search is a row in [`allcov_b20000_8rows_subnc2pxysb.jsonl`](allcov_b20000_8rows_subnc2pxysb.jsonl). The same table as a figure: [`escape_b20000_cost.svg`](escape_b20000_cost.svg) (producer `experiments/stable_ac/cov/figures/make_escape_fig.py`).

Downstream artifacts now carry the escape: `results/comparison/nodes_comparison_subset60.csv` has `nodes_bestcov_b20k` / `solved_bestcov_b20k` (60/60) beside its untouched b10k columns, `nodes_comparison_subset60.png` is regenerated with these eight ringed instead of drawn as hollow ✗, and [`greedy_vs_bestcov_subset60_nodes_path.csv`](../../../comparison/greedy_vs_bestcov_subset60_nodes_path.csv) is the two-arm nodes-and-path table over all 60. One artifact still reads `never` and is correct to: `graphs/per_presentation_b10000.csv`'s `klass` column is a record of the 10,000-node run, and its meaning is pinned in [`SUMMARY_b10000.md`](../graphs/SUMMARY_b10000.md).

## Read the last three columns before the fourth

**Best CoV is an oracle, not a solver.** 14.4k nodes is the *cheapest* of ~170 searches; finding it cost 909 searches and 17,313,543 nodes for the eight together, ~2.2M per presentation. Against the plain greedy's 59.7k–273.0k on the untransformed pair, the oracle is 4.2×–18.9× — and 10× more expensive than simply running the greedy longer.

**Blind restart is the runnable version, and it is a wash on four of the eight.** 221 of the 909 pairs solve (24.3%), so drawing this presentation's CoV starts in random order and stopping at the first that trivialises has its first success at expected position `(n+1)/(k+1)`; every earlier draw costs the full 20,000. That expectation beats the greedy by 2.58×–3.38× on the four bin-9 rows and by 0.95×–1.26× — i.e. not at all — on the four bin-8 rows. **The tuned heuristic ordering is cheaper than both on every one of the eight**, at ~62.5k nodes with a single search and no restarts.

**Those two ratios are a best case over the collection budget, not a floor.** `B = 20,000` was fixed before any of this data existed, and both the number of solving starts `k(B)` and their mean cost move with it, so the ratio is a property of `(method, B)` and not of the method. A search at budget `B` is exactly the first `B` pops of a longer one, so every row re-scores at any smaller `B` with no new search — and the ratio is **not monotone**: it drops each time failed draws get more expensive and jumps down whenever a cluster of solves comes into range (`k` goes 12→35 between 15k and 16k on `ms622`, and 26→40 between 18k and 19k on `ms637`).

| B | `ms622` | `ms623` | `ms624` | `ms625` | `ms636` | `ms637` | `ms638` | `ms639` |
|---|---|---|---|---|---|---|---|---|
| 15,000 | 0.40 | 0.56 | 0.57 | 0.40 | 0.91 | 1.78 | 0.90 | 1.79 |
| 16,000 | 1.06 | 0.80 | 0.81 | 1.06 | 2.11 | 2.67 | 2.09 | 2.69 |
| 17,000 | 1.01 | 0.76 | 0.77 | 1.01 | 2.00 | 2.53 | 1.99 | 2.56 |
| 18,000 | 0.96 | 0.73 | 0.73 | 0.96 | 1.90 | 2.41 | 1.89 | 2.43 |
| 19,000 | **1.30** | **0.99** | 0.70 | 0.92 | 1.82 | **3.50** | **2.75** | 2.32 |
| 20,000 | 1.26 | 0.95 | **0.95** | **1.25** | **2.58** | 3.36 | 2.64 | **3.38** |

20,000 is the *most favourable* B on four of the eight and within 5% of it on the other four. Read the published ratios as an optimistic bound: at 15,000 the blind restart loses to the greedy on six of the eight. What survives the sweep is the **direction** — bin 8 never clears 1.3 at any B, bin 9 clears 1.8 at every B ≥ 16,000.

**And the bin-9 "win" is the denominator moving, not the transform improving.** Blind restart costs 62.5k–83.0k across all eight — nearly flat. The greedy costs 59.7k–78.8k on bin 8 and 213.9k–273.0k on bin 9. CoV does nothing special on the harder rows; the greedy simply gets much worse there while the restart portfolio does not.

**The escape is mostly a rename.** The 1,366 CoV starts reduce to 909 distinct pairs reaching 23 distinct Aut orbits; 803 of the 909 pairs (88.3%) — 1,244 of the 1,366 starts (91.1%) — are the input orbit under a different name. Of the 221 solving pairs, **187 (84.6%) never left the input orbit**, and the solvers occupy only 9 of the 23 orbits. This is [the relabel finding](../AUTOMORPHISMS_COV.md) again, at a larger budget: the solver reads strings, so a rename is a different search even when the group-theoretic content is identical.

## Scope

All 60 rows come from `data/ms640_solved.txt` and are **known-trivial by construction**. "Escape" here means *trivialised inside a budget that previously could not reach it* — a search-cost result, not new mathematics, and it says nothing about the hard tier (all 124 unsolved AC-classes remain at 0 solves in 3,920 searches). The certificates prove the *transformed* pair is AC-trivial; `path_length` from a transformed start is not a certificate for the original.

The eight are one Aut class, so this is really **one** presentation escaping, measured eight ways. The near-identical numbers down every column are that fact showing through, not eight independent confirmations.

## What was checked before any number above was counted

- **Provenance key does not collide.** `build_tasks` returns 909 `(r1, r2, cap)` tasks over 909 *distinct* `(r1, r2)`. The runner's resume set and `prov_of` both key on `(r1, r2)` alone, so this equality is what makes the per-presentation attribution safe. Asserted, not assumed.
- **Budget is the only thing that changed.** Every one of the 909 pairs is joined back to its own row in the b10k sweep jsonl and asserted to carry an identical `max_relator_length_cap` and `cyclic_reduce`, and to be unsolved at *exactly* 10,000 nodes. The escalation runner passes `res.cap` (31–49 here, never the base 24), and so did the sweep — there is no cap confound.
- **The cheapest solve is 14,352 nodes**, 1.44× the old budget. Nothing solved just past 10,000, so 10,000 was not marginally short; and nothing needed the full 20,000 either (median 15,386, max 19,358).
- **Budget truncates and nothing else.** An abandoned budget-100,000 run of the same family covered 10 pairs before it was superseded; the 6 it solved appear in the b20000 file with *identical* `nodes_explored`, and the 4 it did not differ only in having explored their respective budgets.
- **221 of 221 certificates replay.** Every solved row's `path_moves` is re-walked through `experiments/greedy_tests/spec` — never a solver — and must end at the trivial presentation with `abs_det` preserved.

## Reproduce

```bash
.venv/bin/python3 -m experiments.stable_ac.cov.escape.allcov_escalate --budget 20000 --workers 6 --seconds 0
.venv/bin/python3 -m experiments.stable_ac.cov.escape.allcov_escape_report --budget 20000
```

The runner is resume-safe on `(r1, r2)` and the report is pure analysis — re-running it recomputes every number above and re-asserts every gate. Total cost of the sweep: 909 searches, 17.3M nodes, 2.31 CPU-hours across 6 workers (~34 min wall).
