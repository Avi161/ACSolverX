# The 124 unsolved Miller-Schupp ACA classes at 10,000 units

Probe of the round-2 census algorithm on `data/ms_unsolved_reps/aca_124_best.csv`
(the 124 Aut(F2)-minimal representatives of the unsolved ACA classes, CLAUDE.md
section 4), at ten times the census budget. Question asked: does the new cascade
solve any of them, or reach a shorter presentation?

**Answer: no solve, no shorter presentation, on any of the 124, by any of the
five probes below; every claimed state was replayed.**

| probe (10,000 units per row, both relators uncapped) | solved | rows with a shorter total length | notes |
|---|---:|---:|---|
| `K3p_c14aut` (round-2 cascade, cap-14 table terminal) | 0 / 124 | 0 | 165 M table lookups, all missed; 14.8 s per row |
| frozen published policy (baseline) | 0 / 124 | 0 | identical per-row outcome; 13.2 s per row |
| certified reduction search, ordinary moves (`reduce_search.py --arms s20`) | 0 / 124 | 0 | path to the shortest state kept and replayed |
| same, ordinary moves + 4 Nielsen automorphisms (`--arms aut_edges`) | 0 / 124 | 0 | 3 rows reach an equal-length pair with a shorter longest relator: aca_5 (12 to 11), aca_29 (10 to 9), aca_80 (13 to 11) |
| mu-probe: search + Whitehead minimisation of every visited state (`mu_probe.py`, both arms) | 0 / 124 | 0 rows below the Aut-orbit floor | 1.75 M `aut_min` evaluations |

Files: `aca124_<policy>_10000.jsonl` (harness screens), `aca124_reduce_10000.jsonl`
(certified best states with their paths), `aca124_mu_10000.jsonl` (best-mu states
with paths), `*.summary.json`, `*.log`; `analyze.py` prints the per-row table.

## Why the 36 mu-ladder reductions are not reproduced

`aca_124_reduced.csv` records 36 classes whose length dropped (2,446 to 2,356
letters in total) under the mu-ladder, in 2-9 "hops". Starting the certified
search from those 36 *initial* pairs (`aca36_initial_reduce_10000.jsonl`) recovers
none of the reductions with ordinary moves and 5 of 36 with Nielsen edges (2 of
them reaching the ladder's floor). An exhaustive depth-2 enumeration of the full
Definition 2.1 move set, with or without Nielsen automorphisms and conjugate
multiplication by words of length <= 3, finds no reduction at all on the fourteen
"2-hop" rows. The reason is in the ladder's source (branch `experiments/ppo`,
`experiments/stable_ac/cov/ladder/`): a hop is a *subword change of variables*
(introduce z = w(x, y), substitute, isolate and remove a generator, relabel), and
its length is the Aut(F2)-orbit minimum computed by Whitehead reduction
(`autcanon_fast.aut_min`, copied here verbatim for the mu-probe). Those hops are
Tietze-type transformations outside the AC move set, so the 36 entries are not
AC reductions and were never expected to be reachable by an AC-move search.
The 124 best-known pairs are confirmed Aut-minimal by `aut_min` (all 124 agree
with their stored totals).

## Reading

The census algorithm's strength is an exact table of short paths to (x, y) and a
budget allocation that lets the search reach it. On these 124 classes no visited
state is within 14 letters of (x, y) on any relator, no recogniser fires, and the
orbit floor is not lowered, so the round-2 gains on AC19 do not transfer. This is
consistent with the classes' history (bounded AC searches at relator caps 30-36
found no descent) and with several of them being candidate counterexamples.
