# Why fixed-rank, fixed-dictionary triangle search cannot shadow the known rank-2 solutions

Companion to `../RESULTS.md` (triangular expansion + fixed-rank ordinary AC search:
0/4 solves on the hard panel, 5/12 on the easy control panel).  Nothing here is a
new search; it is a measurement of the *known* rank-2 certificates, lifted into
the triangle picture with the exact `high_rank_triangles.triangulate` and
`high_rank_ac_search` code the failed experiment used.

## Hypothesis under test

> A fixed-rank, fixed-dictionary triangle search is a search over rank-2
> presentations restricted to those whose compressed encoding under the INITIAL
> dictionary stays within a tiny cap.  The known rank-2 paths require the
> dictionary and the rank to change continually, and they pass through rank-2
> relators of length 33-35, so no fixed-rank triangle path with cap <= 6 can
> shadow them.  At the triangle level every all-triangle state has total length
> 3r, so the length gradient that drives rank-2 search is flat.

**Verdict: supported on all three counts, with one scope limit (see Caveats).**

## Method

For every state of every saved certificate (both arms for each hard row: the
8.2M/1.5M-node greedy path and the S20_MK2 path; the plain S20 path for the easy
controls) we ran `triangulate` and recorded

* the rank-2 total length `L` and maximum relator length,
* the triangle rank `r_t` (always `2 + #definitions`), the number of triangles,
* every defining compression **fully expanded to a word in x, y**, canonical up
  to inversion — this is "the dictionary at that state",
* the cost of writing that rank-2 state using the **initial** dictionary only.
  Both a greedy longest-match tokenization and an exact dynamic program that
  minimises over *all* tokenizations and all rotations are computed; the
  reported cap uses the exact minimum, so it is a genuine lower bound on the
  relator cap a fixed-dictionary search would need.

## 1-2. Dictionary drift and rank drift

#### Hard panel (4 rows x 2 saved certificates)

| row | arm | states | rank-2 L max | rank-2 maxrel | rank_t min..max (mean) | rank_t at step 0 | rank changes | dict drift | longest stable run | distinct defs | mean shared w/ init |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| ac19_15866 | greedy | 66 | 33 | 18 | 2..13 (8.17) | 8 | 0.600 | 0.954 | 3 | 170 | 1.27 |
| ac19_15866 | s20_mk2 | 97 | 35 | 19 | 2..11 (8.18) | 8 | 0.615 | 0.979 | 3 | 253 | 0.78 |
| ac19_25244 | greedy | 70 | 33 | 17 | 2..12 (7.77) | 8 | 0.522 | 0.942 | 3 | 168 | 0.93 |
| ac19_25244 | s20_mk2 | 61 | 35 | 19 | 2..12 (7.82) | 8 | 0.617 | 0.933 | 3 | 132 | 1.03 |
| ac19_44158 | greedy | 72 | 35 | 19 | 2..14 (8.76) | 9 | 0.732 | 0.958 | 3 | 215 | 1.31 |
| ac19_44158 | s20_mk2 | 64 | 35 | 19 | 2..14 (8.73) | 9 | 0.714 | 0.968 | 3 | 196 | 1.42 |
| ac19_66724 | greedy | 97 | 37 | 22 | 2..12 (7.81) | 7 | 0.448 | 0.979 | 3 | 213 | 0.67 |
| ac19_66724 | s20_mk2 | 81 | 39 | 22 | 2..14 (8.19) | 7 | 0.675 | 0.950 | 3 | 223 | 0.22 |

#### Easy control panel (3 longest solved paths)

| row | arm | states | rank-2 L max | rank-2 maxrel | rank_t min..max (mean) | rank_t at step 0 | rank changes | dict drift | longest stable run | distinct defs | mean shared w/ init |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| ac19_51 | easy_plain_s20 | 19 | 16 | 9 | 2..8 (5.37) | 7 | 0.556 | 0.889 | 3 | 29 | 1.11 |
| ac19_54 | easy_plain_s20 | 13 | 15 | 8 | 2..7 (4.77) | 7 | 0.417 | 0.833 | 3 | 20 | 1.08 |
| ac19_50 | easy_plain_s20 | 12 | 15 | 8 | 2..7 (4.58) | 6 | 0.455 | 0.818 | 3 | 20 | 0.67 |

* The fully expanded definition set changes at **93.3%-97.9%** of hard-path
  steps (81.8%-88.9% on the easy controls).  The longest run of consecutive
  steps with an unchanged dictionary is **3** on every single path, hard and easy.
* Only **one** state per path (step 0, by construction) carries exactly the
  initial dictionary.  On average a hard-path state shares
  0.22-1.42 of its 5-12 definitions with the initial dictionary.
* **132-253 distinct definitions** appear along a hard path, against an initial
  dictionary of 5-7.  The easy controls use 20-29.
* The triangle rank is not fixed and not monotone: hard paths reach
  **r_t = 11-14** while the fixed-rank search is pinned at the root rank 7-9,
  and they also drop below it (the rank changes at 45%-73% of steps).
  Easy paths stay at **r_t <= 8** and spend most of their steps *below* the root
  rank — they descend to rank 2 almost immediately.

## 3. The cap a fixed-dictionary search would need

#### Hard panel

| row | arm | cap to follow path | interior min | steps needing cap>6 | fraction | first step past cap 4 | past cap 5 | past cap 6 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ac19_15866 | greedy | **11** | 3 | 34/66 | 0.515 | 1 | 2 | 3 |
| ac19_15866 | s20_mk2 | **13** | 3 | 78/97 | 0.804 | 1 | 2 | 2 |
| ac19_25244 | greedy | **12** | 3 | 37/70 | 0.529 | 2 | 2 | 3 |
| ac19_25244 | s20_mk2 | **12** | 3 | 44/61 | 0.721 | 2 | 2 | 3 |
| ac19_44158 | greedy | **11** | 3 | 43/72 | 0.597 | 1 | 2 | 2 |
| ac19_44158 | s20_mk2 | **11** | 2 | 35/64 | 0.547 | 1 | 2 | 2 |
| ac19_66724 | greedy | **14** | 2 | 63/97 | 0.649 | 1 | 2 | 2 |
| ac19_66724 | s20_mk2 | **22** | 3 | 60/81 | 0.741 | 1 | 2 | 2 |

#### Easy control panel

| row | arm | cap to follow path | interior min | steps needing cap>6 | fraction | first step past cap 4 | past cap 5 | past cap 6 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ac19_51 | easy_plain_s20 | **7** | 3 | 2/19 | 0.105 | 1 | 1 | 2 |
| ac19_54 | easy_plain_s20 | **6** | 2 | 0/13 | 0.000 | 1 | 6 | None |
| ac19_50 | easy_plain_s20 | **7** | 3 | 1/12 | 0.083 | 1 | 2 | 5 |

"cap to follow path" is the maximum over path steps of the minimum, over all
tokenizations under the initial dictionary, of the longest encoded relator.
"interior min" excludes the trivial endgame (states of rank-2 total length <= 6),
where the answer collapses to 1-2 for every path.

* Hard paths need cap **11-22**; the experiment ran cap 4 (macro), cap 5 and
  cap 6 (deep).  **51.5%-80.4%** of hard-path states are outside cap 6 entirely.
* A cap-6 fixed-dictionary search leaves every hard path at **step 2 or 3** of
  61-97 — it can shadow at most the first two moves.
* Easy paths need cap **6-7**; 3 of their 44 states sit outside cap 6
  (0.0%-10.5% per row, versus 51.5%+ for every hard path).

Worked example (`ac19_66724`, S20_MK2 arm, step 18, the worst state on any path):
the rank-2 pair is `YYYxYxYYYxyXYYxYx`, `YYYxYYYxYxYYYxYxYYXyyx` (L = 39,
max relator 22).  Its own triangulation needs 12 fresh definitions
(r_t = 14), **none of which is in the initial dictionary**.  Under the initial
dictionary `{XX, xxY, Yxx, yyXX, XXyX}` no tokenization writes the two relators
in fewer than **22** and **17** letters respectively.

## 4. Gradient flatness at the triangle roots

`high_rank_ac_search.generate(words, relator_cap=4)` at each root, scored with the
engine's own `structural_score`:

| row | panel | rank | neighbours | distinct scores | tie fraction | best-score ties | better | equal | worse | all-triangle children | constant components |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ac19_15866 | hard | 8 | 54 | 5 | 0.907 | 6 | 0 | 0 | 54 | 0 | 9/11 |
| ac19_25244 | hard | 8 | 48 | 5 | 0.896 | 10 | 0 | 0 | 48 | 0 | 9/11 |
| ac19_44158 | hard | 9 | 62 | 4 | 0.935 | 6 | 0 | 0 | 62 | 0 | 9/11 |
| ac19_66724 | hard | 7 | 40 | 6 | 0.850 | 4 | 0 | 0 | 40 | 0 | 9/11 |
| ac19_51 | easy | 7 | 44 | 5 | 0.886 | 8 | 0 | 0 | 44 | 0 | 9/11 |
| ac19_54 | easy | 7 | 42 | 9 | 0.786 | 1 | 0 | 0 | 42 | 0 | 8/11 |
| ac19_50 | easy | 6 | 36 | 5 | 0.861 | 8 | 0 | 0 | 36 | 0 | 9/11 |

* Every all-triangle root of rank r has total length exactly **3r**, and every
  cap-4 child has total length exactly **3r + 1** — a product of two length-3
  cyclic words has even cyclically reduced length, so no child is all-triangle
  (0 across all 326 children generated here).  The length
  signal is therefore constant across the entire declared neighbourhood.
* **8 to 9 of the 11 score components are literally constant** over the whole
  neighbourhood, including all seven leading components
  (`has_excess, excess, max_length, n_long, -#units, -#bigons, -shared_digrams`) at
  6 of the 7 roots.  Only `repeated` (3-4 values), `min_degree` (2-3 values) and
  occasionally `shared_digrams` (2 values) move at all.
* 4-9 distinct score tuples are spread over 36-62 neighbours: a tie
  fraction of **78.6%-93.5%**.  The best-scoring class alone holds
  1-10 states.
* At every root, **0 children are better than or equal to the parent**; all
  326 are strictly worse.  Each root is a strict local minimum of the
  engine's score, and the frontier beyond it is nearly score-blind.  This is the
  mechanism behind the "one-state component" observation in `../RESULTS.md`.

## 5. Positive control

The three longest solved easy-control paths were lifted identically.  Their
dictionaries drift almost as often (82%-89% of steps), so drift by itself is not
what separates easy from hard.  What separates them is **scale**: peak triangle
rank 8 vs 14, 20-29 distinct definitions vs 132-253, encoding cap
6-7 vs 11-22, and 3/44 vs 394/608 states outside cap 6.  An easy path stays
essentially inside the initial dictionary's reach; a hard path does not.  This
matches the outcome of the original experiment (5/12 easy solved, 0/4 hard).

## Conclusion

The evidence supports the hypothesis.

1. **The dictionary is not fixed along the known solutions.** It changes at
   93%+ of steps, never stays put for more than 3 consecutive steps, and a hard
   path visits 132-253 distinct definitions against an initial dictionary of 5-7.
2. **The rank is not fixed either.** Hard paths run from r_t = 2 to r_t = 14
   while the experiment held rank at 7-9, changing rank at roughly half of all steps.
3. **The cap is the binding constraint.** Following a hard path with the initial
   dictionary requires a relator cap of 11-22, not 4-6.  A cap-6 search falls off
   every hard path by step 3.  This alone explains 0/4 without appealing to
   search budget: the paths are not in the searched set.
4. **The score cannot compensate.** At the roots, the declared cap-4
   neighbourhood is one flat shell: constant total length 3r+1, 8-9 of 11 score
   components constant, 79%+ ties, and no non-worsening child.

A definition-aware search (one that may introduce, retire, and rewrite
definitions, and whose score reads the dependency graph rather than the relator
lengths) is the indicated next step, exactly as `../RESULTS.md` suspected.

## Caveats

* This shows the fixed-rank, fixed-dictionary search cannot **shadow these
  specific certificates**.  It is not a proof that no cap-6 fixed-rank path to a
  solution exists — a fixed-rank search may also rewrite the definition rows
  themselves and take a completely different route.  The gradient result says
  only that its score gives it no help in finding one.
* "The dictionary at a state" means the set produced by the deterministic greedy
  `triangulate`; a different triangulation policy would give different sets.  The
  encoding cap in section 3 does not depend on that choice — it is computed
  against the initial dictionary by exact minimisation.
* Definitions are compared as words up to inversion after full expansion to x, y,
  not up to conjugacy; conjugate definitions count as distinct.
* The panel is small and frozen: 8 hard certificates (4 rows x 2 saved arms)
  and 3 easy-control paths.  These are measurements of saved certificates, not a
  sample of all solutions.

## Reproduce

```bash
cd /home/user/ACSolverX/research/ac19_triangle_expansion_20260912/lift
python3 run_lift.py        # writes lift_hard.json, lift_easy.json, gradient.json, tables/
python3 make_results.py    # regenerates this file from those JSONs
python3 verify.py          # re-derives every headline number from the saved JSON
```

Per-step markdown tables for each row and arm are in `tables/`.
Inputs are pinned by SHA-256 in the `inputs_sha256` block of each JSON.
