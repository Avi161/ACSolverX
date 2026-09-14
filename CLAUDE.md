# AC-SolverX — what a session needs to know before touching the search

Four settled facts. The code on this branch reflects the first two; the third
is about modules that live on other branches. Read this file before trusting a
docstring found elsewhere.

## 1. The best heuristic is `S20_MK2`

```
priority(r1, r2) = L + 20*S + 2*MK
```

`S` = smaller mean block (mean run length of the thinner generator), `MK` = max
knots over the two relators, `L` = total length. Lower pops first. `S20_MK2` is
the **recommended** heap ordering — where a default is needed, this is it.

Provenance, stated as a pair — a number without both halves is not readable:
*selected on* the ac1m_hard_aut train 120 (54/120, against the length control's
0/120); *evaluated on* an automorphism-disjoint fresh holdout (27/60, against
the length control's 0/60). On the 60-row ladder at budget 10,000 it solves
52/60 against the plain greedy's 40/60 — McNemar 12-0, a strict superset, gains
concentrated in bins 6-9. Cap caveat: those runs used `mrl=48` while the frozen
greedy column is `mrl=24`, so read the delta in solves as primary and the node
ratios as indicative.

Note the tuning grid's own top scorer, `S28_MK2_F8` (57/120), is **not** the
keeper: it falls to 22/60 on that fresh holdout. Taking the training-set maximum
would repeat the mistake described next.

## 2. `RECOMMENDED` is overfit and is NOT production

```
L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb        <- do not use as default
```

It was selected on a slice containing fourteen of the twenty rows it was then
validated against, and its 60-row campaign used subset-60 as its own row list.
So every margin ever published for it -- 10/20 -> 15/20, the 60-row cost tables
-- is largely in-sample: a statement about the tuner, not about the ordering.

This branch ships `S20_MK2` instead. Both the name `RECOMMENDED` and the
withdrawn weight map are guarded against returning by
`tests/test_greedy_heuristic.py::test_module_ships_no_overfit_weight_vector`.

The runs `RECOMMENDED` produced are real and should be kept as the record of
what that campaign cost (the `heur_*` columns of the arms tables); it is the
recommendation that is withdrawn, not the data.

## 3. The μ-ladder is NOT production

It does not appear on this branch at all. On the research branches
(`research/w5/*`, `cursor/*`, `experiments/ppo`) `CLAUDE.md` describes it as the
active line — that framing is stale. Its modules and results stay as records.

## 4. The census

| step | count |
|---|---|
| Miller–Schupp presentations | **1,190** |
| solved | **640** |
| unsolved | **550** |
| A-equivalent reps among the 550 | **261** |
| after automorphisms and AC moves | **124** |

State it once, from here. Two precisions worth carrying: 124 is an **upper
bound** from a bounded AC-move search (caps 30–36, unanimous across five arms,
not proven converged), and the exact `Aut(F₂)` step between 261 and 124 is
**168** — no change of variables does better than 168. Derivation and the
machine-checked merges are in `results/equivalence_classes/EQUIVALENCE_FINDING.md`
on the research branches; `docs/BRANCH_MAP.md` says which branch holds what.

### [2026-09-13] At an all-triangle root a unit is parity-forbidden and a bigon needs a shared digram
[MECHANISM] Products of two length-3 cyclic words have even length, so a fixed-rank
search from a triangulated root cannot make a unit in one move; a length-2 relator
needs two relators sharing a cyclic digram modulo (u,v)->(v^-1,u^-1); every one of
the 255 all-triangle roots in a 400-row AC19 sample is digram-disjoint, as are all four
hard rows (the other 145 roots already carry a length<=2 relator from preprocessing).
Score by digram coupling, not total length (constant 3r), and never read an empty
cap-3/cap-4 neighbourhood as a budget problem. See
`research/ac19_triangle_theory_20260913/THEORY.md`.

### [2026-09-13] Cap-bounded exhaustive closure separates U124 from solved rows better than any structural feature, but not perfectly
[MECHANISM] `research/ac_cap_closure_20260912/capbfs.py` enumerates the whole rank-2 AC
component under a per-relator length cap (exact to cap 16 only: the int64 accumulator holds
32 letters, so never trust a cap above 16). Every one of the 120 U124 rows whose relators fit
is CLOSED and unsolved at every cap <= 16 (329 CPU-s in total, AK(3) is 190 s of it); of the
48 solved-ladder rows that fit, 45 solve within cap 16 with a replayable certificate and their
minimal cap rises with the difficulty bin (bin 0: 5-11, bin 6: 14-15, bin 9: 15), while 3 hard
rows (bins 7-8) close at 16 exactly like U124. MS(n, w) with n >= 7 has a relator of length
2n+3 >= 17 and is out of reach in this spelling (4 U124 rows, 12 solved rows). Minimal caps
are far below the mrl=48 the heuristic certificates use. Records and tables in
`research/ac_cap_closure_20260912/records/separator/`.

### [2026-09-13] Definitions and eliminations as search moves beat fixed-rank search, and the reachable compression separates U124 from every solved row
[MECHANISM] `research/ac_dynamic_rank_20260913/dynrank.py` searches presentations of any rank
with three moves: ordinary rotation products, `define` (new generator for a repeated digram,
rank+1) and `eliminate` (a generator occurring once in some relator is substituted away,
rank-1); the solve condition is the empty presentation, and define/eliminate are stable AC
composites (Lemma 11 of arXiv:2408.15332), so a certificate proves *stable* AC-triviality
with those steps unexpanded. At 2,000 pops the dynamic arm solves 42/60 ladder rows against
34/60 for the same engine held at rank two (12 rows in bins 5-9 only the dynamic arm solves,
including two bin-9 rows that plain greedy needs 574k nodes for; 4 bin-5 rows only the
control solves) and 25/60 for a search from the all-triangle root with a fixed dictionary:
triangulating and then searching hurts, letting the dictionary change throughout helps.
No U124 row solves (0/124). The feature `min total length reached / L` is a near-perfect
separator: every U124 row stays at >= 0.80 of its length (the same floor the 3-hour
shortening campaign hit on the same four rows), every solved row drops to <= 0.80 (59/60
strictly below, hard bins 6-9 all <= 0.762) within the same 2,000 pops. Empirical, not a
proof: the exhaustive dynamic-rank closure explodes (>100k states at zero slack for bin 4).

### [2026-09-14] Nielsen maps as search edges, a sorted-array closed set and define/eliminate in one frontier solve the whole AC19 Aut-minimal census at 1,000 units
[MECHANISM] `research/ac_hashfree_cascade_20260914/hfhybrid.py`: best-first on total length with
no hash table (block-sorted closed set, bisection) and no pattern table (primitive relators
finished by substitution, conjugation-shaped relators `g^a h^p g^-a h^q` pinched from a parsed
form). The four Nielsen maps as search edges are the decisive ingredient: on the census
policy's 727 leftovers the same engine goes from 31/180 to 673/727, and seven of the nine rows
unsolved by every fixed-basis arm at 10M nodes solve in 137-318 units, because the Aut-minimal
spelling sits at the bottom of a length well. Signed-permutation canonicalisation adds 23;
define/eliminate moves (stable-AC composites, Lemma 11) in a second frontier served at most
half as often as the rank-two one add the last 31, all of which need 1,100-10,080 rank-two
units. Final: 72,779/72,779 rows verified at 1,000 units (policy: 72,052; 188 stable certificates), 727/727
leftovers, MS-640 640/640 in 3.6 s of single-core search, 3.9 s with verification (cascade
2.4 s / 6.3 s). Memoryless
search (parent-chain cycle check, frontier-only dedup, beams) solves 1.5% of the leftovers:
visited-state memory is indispensable, hashing is not.
[TRAP] A dynamic-rank state that is skipped for a budget-share rule must be deferred (second
heap), never dropped: dropping it lost 6 of the 41 hard rows.
