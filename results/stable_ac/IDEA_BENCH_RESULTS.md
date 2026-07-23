# idea_bench RESULTS — start-transform strategies vs the greedy baseline (combined_22, budgets 500 & 1000)

## Question

At a small node budget (500–1000), does any pre-search *idea* — a change of variables, a relabel, a restart re-seed — let the numba greedy solve a presentation it **cannot** solve at that same budget (coverage), or solve a commonly-solved one in **fewer nodes** (efficiency)? Sixteen strategies raced the plain greedy on the repo's canonical `benchmark_combined_22` (ladder + reach, 22 presentations). **Every number is a delta vs the greedy baseline run at the SAME budget**, per presentation — nothing is compared across budgets, and the baseline is itself a strategy (candidates = the original pair only), so "baseline @ B" is literally `run_baseline.greedy_search`.

## Method (why it is trustworthy)

- **CSV gate passed.** Baseline @ 1000 reproduces every known count in the benchmark to the node (ms0→3, ms455→10, … ms537→579), so the encoding / cap / cyclic-reduce all match ground truth — deltas are real.
- **A strategy runs no search.** It is a pure `candidates(r1,r2,cap)` returning candidate *starting* presentations in try-order; the harness searches each with the trusted greedy and stops at the first solve. So a buggy strategy can only pick bad starts and underperform — it can never corrupt a measurement. This is what made the 10-agent fan-out safe.
- **Ranking headline = coverage, then honest `total_nodes`.** `total_nodes` = cumulative nodes across every candidate searched until the first solve (rewards a well-ordered portfolio). `winning_nodes` (the solving search alone) is color only — a big portfolio always has one lucky fast start. A per-search budget across a portfolio is legitimate for *coverage* because it parallelizes across coordinate systems. **`total_nodes` excludes the (cheap, non-search) CoV enumeration cost** — noted, not hidden.
- **Path wins count only within-coordinate.** A CoV changes coordinates, so its path length excludes the (unbounded, Lemma-11) change-of-variables prefix and is NOT comparable to baseline — hence `pathWIN` is 0 for every coordinate-changing strategy by construction.

## Headline (budget 1000; baseline solves 10/22)

Ranked by coverage wins then efficiency wins (both vs baseline @ 1000):

| strategy | solved | covWIN | effWIN | covLOSS | note |
|---|---|---|---|---|---|
| **cov_abel_len_lex** | **16** | **6** | **9** | 0 | best overall — abel magnitude, ties broken by length |
| cov_abel | 16 | 6 | 7 | 0 | CoV ranked by abelianized magnitude |
| cov_nsubs_escape | 16 | 6 | 6 | 0 | orbit-escaping (n_subs≥2) CoVs first |
| cov_deep_z | 16 | 6 | 5 | 0 | longer (len 3–6) z-words |
| cov_defining_iso | 15 | 5 | **9** | 0 | defining-relator isolation (Thm-2 family) |
| cov_universe | 15 | 5 | 7 | 0 | every reduced z-word len 2–4 |
| cov_plus_relabel | 15 | 5 | 7 | 0 | CoV × its 8 relabels |
| cov_restart_2hop | 15 | 5 | 5 | 0 | depth-2 iterated-CoV restart tree |
| cov_balanced | 15 | 5 | 4 | 0 | most length-balanced relators first |
| cov_len / cov_min_maxrelator | 14 | 4 | 8 | 0 | shortest total / shortest longest-relator |
| cov_common_subword_z | 13 | 3 | 6 | 0 | z = most frequent subwords |
| restart_tree | 13 | 3 | 5 | 0 | depth-1 orbit-deduped restart tree |
| cov_orbit_spread | 14 | 4 | 2 | 0 | farthest-orbit-first (weak ordering) |
| **relabel8** *(control)* | 10 | **0** | 6 | 0 | pure signed relabels — 0 coverage |
| **rotation_seed** *(control)* | 10 | **0** | 0 | 0 | re-seed same pair — 0 coverage, 0 efficiency |
| baseline *(anchor)* | 10 | – | – | – | greedy @ 1000 |

At budget 500 (baseline 9/22) the picture is the same, cov_defining_iso and cov_abel_len_lex leading (5 cov, 8 eff, 0 loss).

## What the controls prove (the load-bearing result)

- **rotation_seed** (re-seed the *same* presentation under every rotation/inversion — same group, same Aut-orbit, only the start string differs): **0 coverage, 0 efficiency, everything `changed_coords=False`.** So the CoV wins are NOT just the greedy being string-seed lucky.
- **relabel8** (the 8 signed-permutation relabels): **0 coverage**, but 6 efficiency wins. So a relabel is a real *speed* lever (a better string-seed lets the greedy solve a solvable case in fewer nodes) but never a *coverage* lever — it cannot crack a new presentation.
- **Only genuine substitution (CoV) buys coverage.** Every strategy that reached new coverage does an actual change of variables; the two that only re-seed reach none. That is the clean scientific separation.

## Coverage: what CoV cracked, and the wall it hit

- **Cracked at budget 1000** (baseline unsolved → CoV solved at ≤1000): **ms538 (2261), ms565 (1404), ms602 (6285), ms581 (9567), ms633 (26838), ms634 (574348)** — six presentations, including two whose *baseline* optimum needs 27k and **574k** nodes, solved after a change of variables in tens of nodes.
- **The wall (unsolved by every strategy at ≤1000):** ms568 (15814), ms605 (60593), ms623 (59710), ms636 (213882), and the two reach cases **AK(3)** and **19_40**. So CoV coverage is strong but NOT universal on the deep tail, and the marquee open cases stay open — the honest ceiling.
- **Baseline difficulty does not predict CoV difficulty.** ms634 (574k baseline nodes) is cracked while ms605 (60k) is not — a good CoV exists for one and not the other within the portfolio. Coordinate choice, not baseline depth, is what matters.

## Mechanism (mixed — verified by spot-check)

CoV coverage wins come by two distinct routes, both legitimate stable-AC-equivalent presentations:
- **Orbit escape** (`n_subs ≥ 2`): a genuinely new Aut(F₂)-orbit. Spot-checked earlier on pres 609 — winning candidate in a *different* Aut-canonical class, solved in 37 nodes.
- **Same-orbit automorphic re-seed** (`n_subs = 1`): an automorphic image in the *same* orbit that nonetheless gives the greedy a solve-enabling string the simple relabels/rotations never reach. Spot-checked on **ms634** — winning candidate `xxxxYxxxxxYXyXXXXXXXX | YxxxxxxxyXXXXXXXX` (lens 21/17, not collapsed) has the *identical* Aut-canonical form as ms634, yet greedy solves it in 39 nodes vs baseline's >1000.

So the honest statement is: CoV substitution reaches solve-enabling representations of the same stable class that rotations and the 8 relabels miss — sometimes by escaping the orbit, sometimes by finding a far better representative *within* it. The controls prove the reach is real; the ms634 case proves it is partly a search-representation effect, not always a deep escape.

## Most promising (the answer)

**`cov_abel_len_lex`** — rank CoV candidates by abelianized magnitude with length tie-breaks. Top coverage (6/6 of the crackable band) and top-tier efficiency (9), zero regressions, at both budgets. It is a subagent's refinement of `cov_abel` and genuinely beats it (9 vs 7 efficiency wins) — the fan-out earned its keep. Close behind: `cov_abel`, `cov_nsubs_escape`, `cov_deep_z` (all 6 coverage), and `cov_defining_iso` (9 efficiency). **`cov_universe` / `cov_plus_relabel` / `cov_restart_2hop`** are the next tier. The scale-up test (per your "increase budget once promising"): re-run `cov_abel_len_lex` and `cov_nsubs_escape` on the wall cases (ms605, ms623, ms636, ms568) and AK(3)/19_40 at production budget on Colab.

## Caveats (do not over-read)

- Coverage uses a per-search budget across a candidate portfolio; the honest cumulative cost is in `total_nodes` (excludes the cheap enumeration). Winning-search nodes are color.
- The cracked presentations are KNOWN-AC-trivial ladder cases — CoV finds a *faster route*, it does not prove new triviality. The genuinely open cases (AK(3), 19_40) are exactly the ones nothing cracked.
- Results are on `combined_22` at ≤1000 nodes. `MAX_CANDIDATES=60` portfolio cap. Same-budget baseline is the only anchor.

## Reproduce

```
# full parallel sweep (resume-safe; foreground, bounded — the background wall kills long jobs)
.venv/bin/python3 -m experiments.stable_ac.idea_bench.run_sweep --bench combined_22 --budgets 500 1000 --jobs 8 --out idea_bench_combined_22_final.jsonl
# lean/minimal (small benchmark, single low budget — scale the budget only once a strategy looks promising)
.venv/bin/python3 -m experiments.stable_ac.idea_bench.run_sweep --bench combined_11 --budgets 500 --jobs 8
# summarize any jsonl
.venv/bin/python3 -m experiments.stable_ac.idea_bench.harness --summarize <jsonl>
```

*Data: `results/stable_ac/idea_bench/idea_bench_combined_22_final.jsonl` (748 cells = 17 strategies × 22 presentations × 2 budgets). Strategies: 6 hand-written + 10 from a parallel subagent fan-out (each a pure candidate-generator, blocked-ideas list enforced), all measured in one process for comparability. July 2026.*
