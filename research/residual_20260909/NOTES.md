# Working notes (chronological, 2026-09-09)

1. Panels built (`panels/`): dev/val/test 102/102/101 rows, 9 clusters; regression60
   (all `incumbent_restart` solves with >= 900 units). Only 19/727 residual rows have a
   consecutive-BS donor (18 stalled, 1 preflight-accept); 293/727 roots have a 4-block
   relator; zero residual roots pass the two-block or one-occurrence gates.
2. Harness (`harness.py`, `policies.py`, `compare.py`) reproduces the census records
   exactly (smoke 12/12 and regression60 60/60 with identical node counts).
3. Dev screens (`screens/DEV_SCREENS.md`): frozen 0/102 at 1,000 but 87 at 2,000 and 98
   at 5,000+; the incumbent stage ALONE at 1,000 solves 87/102 and `aut_edges_s20` 86/102;
   the frozen 250+872 prefix starves the incumbent. Regression60 is 60/60 under every
   alternative with far fewer nodes.
4. Theorem audit (`THEOREMS_PROOFS_AND_FREQUENCY.md`): ordinary terminal 60.2 % of
   solves, consecutive BS 34.7 % (98.5 % of those are m=1, i.e. BS(1,2)), primitive
   one-occurrence 5.0 %, two-block 0.14 %, everything else 0; the incumbent's 612 solves
   all end in a macro (BS 518, two-block 94). Ten prose-vs-code gaps listed there.
5. Backward table ("ball") discovery: the exact set of canonical pairs from which an
   engine-move path to (x,y) exists within relator cap c has 317 / 6,069 / 101,885 states
   for c = 6 / 8 / 10 (closing at depth 8 / 16 / 33). Saved census paths enter the cap-8
   ball 7-13 steps before their terminal. Using membership as a terminal at every generated
   state: generator-edge S20 search + cap-8 table solves 82/102 dev rows at 1,000 units
   (all decoded and independently replayed); cap 10 gives the same 82 with 10 % fewer nodes;
   automorphism-closed cap-8 table (7,613 states) lifts the ORDINARY arm from 7 to 25.
   Deeper-first tie-break: 83/102 dev and 56/60 on regression60 for the bare generator arm.
6. Budget-starved BS-accept row ac19_109: the certified collapse needs 256 rewrites; stage 1
   has 246 -> certified-overrun rule (let an accepted collapse draw on the shared remainder).
7. Dev rows unsolved by every 1,000-unit single policy include the two `bs_stalled_hi`
   rows (T=6) which no arm solves even at 10,000 units.

## Pre-registered candidate cascades and selection rule (written before opening val.csv)

All candidates share the 1,000-unit heterogeneous allowance, `cap=None`, the frozen
orderings (`L + 20 S + 2 MK`, W = 1.5 on the generator arm, 4 T on the ordinary escape arm)
and add the backward-table terminal (membership lookup at the root and at every newly
generated state, uncharged but counted) with the cap-10 table (automorphism-closed if
built). "Overrun" = a preflight-accepted consecutive-BS collapse may draw on the shared
remainder instead of the 250-unit stage cap. "SP" = stable-power gate enabled.

| id | stage 1 (strict donor) | stage 2 (plain S20) | stage 3 (incumbent) |
|---|---|---|---|
| K0 | frozen 250 | frozen 872 | rest, routed | (reference: the published census policy)
| K1 | 250 + table | 872 + table | rest, routed + table | dominates K0 by construction
| K2 | K1 + overrun | K1 | K1 + SP |
| K3 | 250 + table + overrun | 300 + table | rest, routed + table + SP |
| K4 | 250 + table + overrun | none | rest, routed + table + SP |
| K5 | 250 + table + overrun | none | rest, forced generator arm + table + SP |

Selection: run K1..K5 once each on val.csv at 1,000 units; choose the candidate with the
most verified solves; ties by fewer total charged units, then lower search wall. Hard
constraints: 60/60 on regression60 and 12/12 on the smoke panel. The chosen candidate
runs once on test.csv, then on the full 72,779-row census (its allocation differs from
the frozen policy, so the old per-row outcomes are not logically reusable); gains and
losses against the published census are reported per route. If the chosen candidate
loses any census row, the loss is reported and K1 (zero-loss by construction) is the
fallback recommendation.

## Protocol exposures (recorded honestly)

- The stalled-BS theory agent ran one 1,000-unit `root_router` search on `ac19_99`, which
  belongs to the hidden TEST panel (it learned that the incumbent alone solves it in 896
  units, consistent with the dev stage-isolation screen). No rule or constant was tuned on
  that row; the candidate cascades were pre-registered before this. Recorded so that the
  single test-panel run is read with this caveat.
- Cheap recognizers (BS gate, stable-power gate, BS-DEMOTE label) were evaluated on all
  727 residual roots for AGGREGATE counts only; no search was run on val/test/rest rows.

## Stalled-BS theory (theory/STALLED_BS_THEORY.md, theory/PATH_MINING.md)

- Proved: while the BS relator R is the untouched donor, the companion's reduced
  stable-letter count is a conjugacy invariant of BS(m,m+1), so the preflight can never
  accept and no census terminal is reachable; the 4T/preflight work spent at such states
  is provably wasted (59,414 scans on solved census rows).
- Proved rule BS-DEMOTE: a carry-lattice label (m, alpha, beta) classifies stalled
  s=3 pairs; label (m,1,m-1) admits a deterministic compiler (carry W onto a BS(1,2)
  relator, then every pinch is legal). Certified 427/602 stalled census rows including 4
  previously unsolved residual rows (all in `rest`), each replayed to (x,y).
- Refuted: demotion to m' >= 2; BS-DEMOTE for s = 5, 7 (sign-necklace invariant);
  the naive y = A^-1 B^-1 substitution into R; the second relator as a BS donor after one
  multiplication (bounded enumeration).
- Note: 0 of the 612 incumbent-route census solves have a stalled-BS root; the family
  lives in 584 plain_s20 solves (median 58 units) and 18 residual rows.

## Table results with the prototype search on dev at 1,000 units

| table | states | ordinary arm | generator arm (w=1.5) |
|---|---:|---:|---:|
| cap 8 | 6,069 | 6 | 82 |
| cap 10 | 101,885 | 7 | 82 |
| cap 8, automorphism-closed | 7,613 | 25 | 82 |
| cap 10, automorphism-closed | 127,873 | 72 | 86 |
| cap 12 | 1,165,797 | 28 | 87 |

Rows no arm reaches within 3,000 units with the cap-10 automorphism-closed table: 7
(1 fixed by certified overrun, 2 BS T=6 rows which the incumbent's gates solve at full
budget, 4 which only the ordinary arm solves and only at 3,000-5,400 units).

## Negative result: score-guided backward table

A best-first backward expansion from (x,y) under the S20_MK2 score (cap 16,
automorphism-closed, stopped at 1,500,007 states after 36,422 pops, 108 s) is WORSE as a
terminal than the uniform automorphism-closed cap-10 ball (127,873 states): on dev at
1,000 units the generator arm solves 83 (vs 86) and the ordinary arm 26 (vs 72). The
score-guided set is wide and shallow around a few low-score states; the uniform ball is
the right object. Not shipped.

## Census runner validated

`census_run.py` / `census_summarize.py`: 300-row slice under the frozen policy matches the
published shards row for row (0 mismatches; workers=1 and workers=3 identical). Full census
estimate: 26-32 min at one worker, 7-10 min at four.

## Timing facts (dev panel, 102 rows, one thread, warm JIT)

| run | solved | units | search wall (s) | ms / unit |
|---|---:|---:|---:|---:|
| frozen @1000 | 0 | 102,000 | 34.7 | 0.34 |
| incumbent alone @1000 | 87 | 39,336 | 28.5 | 0.73 |
| aut_edges_s20 alone @1000 | 86 | 39,788 | 29.9 | 0.75 |
| aut_edges + cap-10 table @1000 | 86 | 34,441 | 29.0 | 0.84 |
| frozen + cap-10 table @1000 | 24 | 100,071 | 38.5 | 0.38 |

The generator arm costs about twice as much wall per charged unit as the ordinary arm
(Nielsen children, gate checks, W). Table lookups are negligible. The goal requires a
census wall time comparable to the frozen census (389 s search + 109 s certificate), so
the candidate is judged on wall time as well as solves; per-node cost of the generator
arm is an optimization target once the design is fixed.

## Frozen cascade + tables (dominance-preserving allocation 250/872/rest), dev and reg60 at 1,000

| table | dev solved | dev units | dev wall (s) | reg60 solved | reg60 units | reg60 wall (s) |
|---|---:|---:|---:|---:|---:|---:|
| none (frozen) | 0 | 102,000 | 34.7 | 60 | 57,166 | 16.8 |
| cap 8 | 6 | | | 60 | | |
| cap 10 | 24 | 100,071 | 38.5 | 60 | 54,044 | 16.4 |
| cap 10 automorphism-closed | 78 | 34,872 | 14.6 | 60 | 22,176 | 7.1 |
| cap 12 | 71 | 71,085 | 27.3 | 60 | 26,607 | 9.8 |
| cap 12 automorphism-closed (1,488,649 states, 625 s build) | 91 | 15,221 | 7.2 | 60 | 6,733 | 2.4 |

The automorphism-closed cap-12 table raises coverage AND cuts wall time (fewer units per
row), which is what the goal's time constraint needs.
Table load cost (cap 12 automorphism-closed): 68.7 MB pickle, 1.85 s to load, 507 MB RSS
per process; acceptable for a four-worker census run (about 2 GB).

## Candidate screens with the cap-10 automorphism-closed table (dev / reg60 at 1,000)

| candidate | dev solved | dev units | dev wall (s) | reg60 | reg60 units |
|---|---:|---:|---:|---:|---:|
| K1 (frozen allocation + table) | 78 | 34,872 | 14.3 | 60 | 22,176 |
| K2 (K1 + overrun + stable-power) | 80 | 34,044 | 14.5 | 59 (lost ac19_28267) | 22,145 |
| K3 (250 / 300 / rest + table + SP) | 92 | 26,132 | 18.0 | 60 | 9,524 |
| K4 (250 / none / rest + table + SP) | pending | | | 60 | 2,022 |

Dominance break found: the stable-power gate charges its failed attempts, and on
ac19_28267 (frozen solve at exactly 973 units) those charges pushed K2 past 1,000. SP is
dropped from all candidates. The overrun rule fires only on preflight-accepted BS states;
it CAN in principle cost a row (a collapse needing more than the whole remaining budget
burns it, where the frozen cascade would have moved on to stages 2-3), so its zero-loss
claim is checked on the census comparison, not asserted.

## Four-block theory (theory/FOURBLOCK_THEORY.md, FOURBLOCK_PATHS.md)

- 44,039 census roots have a four-block relator (60.7 % of solves; 293 residual).
- Proved: F1 (four-block primitive merge, with sharp converse; 2,725 census rows, a cost
  rule), F3 (twin four-block row reduction), L1 (forced consecutivity and forced companion
  exponent). Proved negative N1: widening the BS donor pattern to stable runs s >= 2
  recognizes 71 residual donors and closes none (|det| = 1 forces the companion exponent
  to be 1, never divisible by s). The relator is consumed as a donor in 99 % of census
  paths; Nielsen maps never lower its block count outside the merge family.
- Consistent check: the disabled `stable_square` rule (the b = 2 instance of the
  Britton-over-zero-exponent-generator idea, donor YYXXyxx) stalls on all 8 dev rows that
  carry its donor. Zero residual reach from these rules; their value is cost and theory.
