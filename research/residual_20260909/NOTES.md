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

## Validation run (val.csv, 102 hidden rows, opened once; cap-12 automorphism-closed table)

| candidate | solved | verified | units | search wall (s) | smoke |
|---|---:|---:|---:|---:|---:|
| K1 | 90 | 90 | 14,258 | 5.7 | 12/12 |
| K2' | 90 | 90 | 14,258 | 6.0 | 12/12 |
| K3' | 94 | 94 | 11,585 | 8.9 | 12/12 |
| K4' | 94 | 94 | 11,868 | 12.2 | 12/12 |
| K5' | 93 | 93 | 12,058 | 11.3 | 12/12 |

Selected by the pre-registered rule (solves, then units, then wall): K3' on the cap-12
automorphism-closed table, registered as `K3p_c12aut`: BS-DEMOTE root stage; strict donor
250 with certified overrun; plain S20 300; incumbent with the rest, routed; the table
terminal at every generated state in every stage. Regression60 60/60 with no row over its
census cost; smoke 12/12.

## Frozen test run (test.csv, 101 hidden rows, opened once, after the candidate was fixed)

K3' on the cap-12 automorphism-closed table: **97/101 solved and verified**, 0 errors,
9,407 units, 6.8 s search wall, 0.43 s certificate wall. Unsolved: ac19_99 (the row the
BS theory agent had touched once), ac19_6554, ac19_50262, ac19_58570.

## Full census, round 1 (policy K3p_c12aut, 1,000 units, 4 workers)

**72,738 / 72,779 solved and verified (99.944 %); 41 unsolved; 0 errors.** Against the
published census: 692 gained, 6 lost (all six were plain_s20 solves needing more than the
300-unit plain stage). Charged units 2,829,457 (published: 6,621,411). Search wall 172.4 s
(published 389.2 s); certificate wall 203.1 s (published 109.4 s; the table tails add decode
work); total compute 375 s vs 499 s. Routes: ball_root 24,708 (a third of the census is
inside the cap-12 automorphism-closed ball), strict_donor 24,415, plain_s20 23,424,
incumbent_restart 148 solved / 41 unsolved, bs_demote 43. Results in
results/heuristic_search/ac19_ball_cascade_full_1k/ (SUMMARY.json, RESULTS.md,
COMPARISON.md, unsolved.csv, 73 shards, manifests).

## Diagnosis of the six census losses (round 1)

All six are rows the frozen plain stage solved at 491-638 plain units; with the cap-12
automorphism-closed table the ordinary arm needs 413-569 units, i.e. more than K3''s
300-unit plain stage, and the incumbent stage does not reach them within its ~692 units.
Two families: r1 = YYXyxYXXyx (4 rows) and r1 = YXyXYXyxx (2 rows); the same first
relators recur among the 41 unsolved rows. Of the 41 unsolved roots, 34 have both relators
of length <= 14, so a cap-14 automorphism-closed table could resolve them at the root if a
cap-14 path exists (24,708 census roots already lie in the cap-12 ball).
Of the 692 gains, 460 were roots that lie INSIDE the cap-12 automorphism-closed ball
(route ball_root, one lookup), 164 plain_s20, 57 incumbent, 7 strict_donor, 4 bs_demote.

## Ball membership of the round-1 remaining roots (SUPERSEDED, see the correction below)

CORRECTION (round 2): the six round-1 losses are among the 41 round-1 unsolved rows, so
the residual after round 1 is 41 roots, not 47; the list below double-counted them. The
forward-component counts below also disagree with the exact table lookup made once the
cap-14 automorphism-closed table existed: exactly 26 of the 41 roots are in the cap-14
ball (0 in the cap-12 ball); the remaining 15 (largest relator 17 letters) are solved by
the plain stage in 9-201 units on the way into the ball. The table below is kept only as
the record of what was believed when the cap-14 build was ordered.


| cap | in the ball | provably outside | undecided |
|---|---:|---:|---:|
| 14 | 35 | 12 | 0 |
| 15 | 46 | 1 (ac19_66543) | 0 |
| 16 | 47 | 0 | 0 |

The forward components under these caps are small (tens to a few thousand states), i.e.
the roots sit in "pockets" whose exits pass through a length-15/16 relator. A cap-14
automorphism-closed table would resolve 35 of the 47 at the root; the rest need the search
to find a short path (depth 3-15) through a longer state before meeting the table.

## Round 2: compact cap-14 automorphism-closed table (tables/ball_cap14_aut.npz)

Built by `python -m research.residual_20260909.backward_table --cap 14 --aut-edges
--compact` (BACKWARD_TABLE.md section 10): 12,803,449 states (2,269,806 automorphism
edges), max depth 100, 1,612 s single-thread build, 1.95 GB peak build RSS, 281.7 MB
`.npz` (sha256 c2bbbf3e...13f94, recorded in tables/ball_cap14_aut.npz.manifest.json),
1.27 s load, 0.37 GB process RSS, 1.2-2.7 M lookups/s. Replay check: every entry of depth
<= 3 plus a random sample, 150,050 edges re-derived in pure Python, 0 failures. The
compact builder reproduces the dict tables key-for-key and depth-for-depth at caps 8, 10
and 12 (plain and automorphism-closed). The 269 MiB file is gitignored; only its manifest
is committed.

Panels at 1,000 units with the same cascade as round 1 (K3' = 250-unit certified-overrun
donor stage, 300-unit plain S20 stage, incumbent restart, BS-DEMOTE), now `K3p_c14aut`:

| panel | rows | solved | verified | units | search wall (s) |
|---|---:|---:|---:|---:|---:|
| smoke (already solved) | 12 | 12 | 12 | 480 | 0.03 |
| regression60 (near-limit frozen solves) | 60 | 60 | 60 | 0 | 0.02 |
| dev | 102 | 102 | 102 | 754 | 0.3 |
| val (hidden, opened once in round 1) | 102 | 102 | 102 | 740 | 0.3 |
| test (frozen, opened once in round 1) | 101 | 101 | 101 | 1,504 | 1.0 |
| round-1 residual (panels/residual_round1.csv) | 41 | 41 | 41 | 691 | 0.28 |

No regression row costs more than in the census (all 60 resolve at the root for 0
units). `K1_c14aut` (frozen allocation, no overrun, no BS-DEMOTE) solves 101/102 dev; the
one miss is ac19_109, the 256-rewrite certified-overrun row. Round 2 changed the terminal
table only; no constant was re-tuned on val or test.

## Full census, round 2 (policy K3p_c14aut, 1,000 units, 4 workers, commit 4a4500af)

**72,779 / 72,779 solved and verified (100 %); 0 unsolved; 0 errors; 727 gained, 0 lost
against the published census.** Charged units 949,521 (published 6,621,411; round 1
2,829,457); maximum 699 (ac19_32603, incumbent route), median 0, 99th percentile 251;
66,151 roots (90.9 %) resolve inside the cap-14 automorphism-closed ball for 0 charged
units. No row is charged more than the published policy charged it. Routes: ball_root
66,151, strict_donor 4,508, plain_s20 2,113, incumbent_restart 7 (all solved); bs_demote
0 (every BS-DEMOTE row of round 1 is now inside the ball).

Time (all rows, this container, 4 workers): search wall 46.7 s (published 389.2 s; round
1 172.4 s), certificate decode + replay wall 186.2 s (published 109.4 s; round 1 203.1 s),
compute 233 s against 499 s; census wall 70 s from manifest creation to the last shard
(round 1: 108 s; the published serial run took 1,976 s elapsed including 1,471 s of
recorded cooldown). Worst single row: 0.456 s search wall (published 0.454 s), 0.063 s
certificate wall (published 0.042 s).

Certificates: 42,304,643 elementary moves in total, median 243 per row (published 248),
longest 26,002 (published 17,485; ac19 rows whose ball tail is long). On the 72,052 rows
both censuses solve, the elementary paths total 40.97 M moves against 39.39 M (+4.0 %);
37,645 rows are longer now and 28,696 shorter.

Verification, independent of the census process:

- `verify_bundle.py --result-dir results/heuristic_search/ac19_ball14_cascade_full_1k`:
  PASS. Input hash 7e220253...4ae2; 73 shards tile [0, 72779) once; names unique and equal
  to the input names in order; 0 errors; max charge 699 <= 1000; solved == verified ==
  72,779; SUMMARY.json totals and clocks recomputed from the rows; the manifest's 42 source
  hashes and 8 table hashes match the tree at 4a4500af.
- `replay_census.py --result-dir ... --workers 4`: every one of the 72,779 stored mixed
  paths decoded again with `certificate_decoder_compact_moves.decode_elementary` and
  replayed with `certificate_decoder.replay_elementary` in fresh processes, all ending at
  (x, y) with the recorded move count; 0 failures; 46.5 s wall (replay_check.json).
- `pytest research/residual_20260909/tests`: 341 passed.

Results: results/heuristic_search/ac19_ball14_cascade_full_1k/ (73 shards with the mixed
paths, manifest, SUMMARY.json, RESULTS.md, COMPARISON.md, comparison.json, unsolved.csv
(empty), replay_check.json, census_run.log, summarize.log).

## Family theory for the 41 round-1 roots (theory/FAMILY_THEORY.md, FAMILY_DATA.md)

Written before the cap-14 result and kept as the explanation of why those rows were hard:
the conjugacy class of the companion in <x, y | R> is a complete invariant of the moves
that preserve R (Theorems W2-W4, algebra machine-checked on all 2,346 R-preserving
children of the 41 roots); Rule W-TRANSPORT certifies 20 of the 41 with 1-8 charged
R-preserving moves onto a solved census row (each certificate decoded and independently
replayed); 17 of the roots have both relators <= 12 yet lie outside the cap-12 ball, so
every path from them must first pass a longer relator, which is exactly what the cap-14
table supplies. Negative results are recorded as bounded refutations (W5, W6). One
family (r1 = YYXXYxYXX: ac19_11753, ac19_38222) is solved by the table but still has no
structural explanation. `FAMILY_verify.py` passes; its search sections are opt-in.

## MS-640 (the solved Miller–Schupp set) under K3p_c14aut at 1,000 units

Panel `panels/ms640.csv` (SHA-256 `5ca1f791…a7667`), built by `panels/build_ms640.py`
from `data/ms640_solved.txt` (SHA-256 `fbf976f7…32a43`): the 640 presentations the
greedy baseline solved at a 1,000,000-node budget, decoded from the padded integer rows
with {1: x, -1: X, 2: y, -2: Y} and kept in source order. Total lengths 7-25 (median 15).

- 640 / 640 solved and verified, 0 errors; 13,082 charged units, max 267, median 0,
  mean 20.4. Routes: ball_root 550 (0 units — the root is already in the cap-14 ball),
  plain_s20 62, bs_demote 24, strict_donor 4.
- Budget threshold is exact at **267** (`budget_sweep.json`): 267 -> 640, 266 -> 636.
  The four rows that need the last unit are ms_636..ms_639, all
  r1 = YYYYYYYYXyyyyyyyx against an 8-letter companion. 200 -> 626, 100 -> 612, 50 -> 612.
- Frozen policy on the same panel at the same budget: 602 / 640, 87,531 units, 38 rows
  exhaust the 1,000. 38 gained, 0 lost, and on every one of the 602 rows both solve
  K3p_c14aut is strictly cheaper. (No contradiction with the MS census: these rows are
  "solved" at 10^6 greedy nodes, not at 1,000 units.)
- Independent replay: 640 / 640 certificates re-decoded and replayed to (x, y) in fresh
  processes, 0 failures. `verify_bundle` PASSes.

`verify_bundle.py` gained `--expect-sha256` / `--expect-rows` so the input-identity checks
can name a panel; both default to the settled AC19 census hash and 72,779, so the AC19
bundle is certified by exactly the same two checks as before (re-verified PASS).

Results: results/heuristic_search/ms640_K3p_c14aut_1k/ and ms640_frozen_1k/.

## What the table does, stated plainly (no-table controls)

The cap-14 backward ball is precomputed search: BFS outward from the trivial pair over
every AC move (and 4 Nielsen edges) that keeps both relators <= 14 letters — 12,803,449
states, max depth 100, 1,612 s to build once, no census input (`backward_table.py` reads
no census file). Its lookups are uncharged, so "<= 1,000 units" under `K3p_c14aut` is the
forward search on top of the ball, not the whole computation. The honest split, from the
new no-table control `K3p_notable` (same cascade, `table=None`):

| panel | frozen | K3p_notable (rules, no table) | K3p_c14aut (rules + table) | rows inside the ball |
|---|---|---|---|---|
| AC19, 72,779 rows | 72,052 | **72,562** (+567 / -57) | **72,779** | 66,151 (91%) |
| MS-640 | 602 | **627** (+26 / -1) | **640** | 550 (86%) |

So on AC19 the new rules are worth +510 net and the table exactly the last 217; on
MS-640 the rules +25 and the table the last 13. The table's cap is a resource knob
(cap 12 left 41 unsolved, cap 14 left 0). Every table hit still yields a genuine AC path
(the stored tail), and every certificate in both bundles is independently replayed.

MS-640 has an older no-table policy that solves all 640 at 1,000 units: the MS-640
cascade `experiments/search/cascade_heuristics.search` (BS rewrite -> L+40S with
generator moves, cap 48 -> S20_MK2 fallback), re-run here in
`results/heuristic_search/ms640_cascade_heuristics_1k_rerun/` and matching
`goal_frontiers/MS640_RESULTS.md` exactly: 22,075 units, max 404, rewrite 254 / s40_gen
386 / fallback 0; search wall 6.2 s on one core in this container (2.36 s on the machine
of record). The 13 rows `K3p_notable` misses are all `Y^n X y^(n-1) x` with a 7-8 letter
companion; that cascade's s40_gen arm takes them in 41-331 units, and the 24 rows
`K3p_c14aut` closes by BS-DEMOTE at 250-267 units cost it 10-46.

Timing of `K3p_c14aut` on MS-640, one core, warm: 4.1 s for the 640 rows (search 1.9 s,
certificate decode + replay 2.2 s). The S20 kernel is numba; the BS-DEMOTE and
consecutive-BS collapse compilers are pure Python (`words.canon_pair` / `replay_move` /
`cyc_reduce`) and account for 1.25 s of the 1.9 s on 24 rows. Fixed process startup is
~7 s (table load + sha256 1.7 s, numba cache load 2.3 s, provenance hashing of
`tables/` ~2 s). Results: results/heuristic_search/ac19_K3p_notable_full_1k/,
ms640_K3p_notable_1k/, ms640_cascade_heuristics_1k_rerun/.
