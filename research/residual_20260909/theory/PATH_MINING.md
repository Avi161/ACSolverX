# Path mining of the AC19 census certificates

Scope: `results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl`, read
only.  Analysis code: [`path_mining.py`](path_mining.py); per-row output:
[`path_mining_rows.jsonl`](path_mining_rows.jsonl) (1,496 records).  Every
number below is reproducible with

```bash
PYTHONPATH=. python3 research/residual_20260909/theory/path_mining.py
```

The miner re-replays the saved substitution steps with
`experiments/equivalence_classes/lib/words.replay_move`; 60 sampled paths were
replayed step by step with 0 mismatches, so the saved `states`/`steps` are
internally consistent.

## 0. The first result is a correction to the brief

The task assumed the residual is dominated by pairs `(R, W)` with `R` a
consecutive Baumslag-Solitar relator.  Scanning the whole census for a literal
consecutive-BS relator (`bs_preflight.donor_orientations`, which already
enumerates all eight signed generator permutations and all rotations/inverses):

| root shape | strict_donor | plain_s20 | incumbent_restart | total |
|---|---|---|---|---|
| no BS relator at all | 8,818 solved | 42,821 solved / 0 unsolved | 612 solved / **708 unsolved** | 52,959 |
| BS core, preflight **accept** | 19,217 solved | 0 solved / 1 unsolved | 0 | 19,218 |
| BS core, preflight **reject** (stalled) | 0 | **584 solved** / 0 unsolved | 0 solved / **18 unsolved** | 602 |

So of the 727 unsolved rows only **18** carry a stalled consecutive-BS root;
the other 709 do not carry a BS relator at all (708 `incumbent_restart` plus
the single unsolved `plain_s20` row, whose root is a *pinchable* BS pair the
budget ran out on).

The consequence for Task A is that the two mandated groups are the wrong place
to look for the stalled-BS family:

* of the 612 solved `incumbent_restart` rows, **0** have a BS root;
* of the 300 largest-`nodes_explored` solved `plain_s20` rows, **0** have a BS root.

The miner therefore analyses a third group as well - **every solved row whose
root is a stalled consecutive-BS pair (584 rows)** - and that is where all the
structure lives.  All three groups are in `path_mining_rows.jsonl`, tagged by
`group`.

## 1. Group profiles

| | incumbent_restart (612) | plain_s20 top-300 (300) | stalled-BS root (584) |
|---|---|---|---|
| route | `incumbent_restart` | `plain_s20` | `plain_s20` (all 584) |
| nodes_explored, median / max | 949 / 999 | 737 / 889 | **58 / 541** |
| mixed steps, median / max | 24 / 76 | 35 / 100 | 21 / 76 |
| automorphism steps, median / max | 6 / 14 | 0 / 0 | 0 / 0 |
| paths containing an automorphism | 612 / 612 | 0 | 0 |
| total length `L0`, median / max | 19 / 30 | 19 / 29 | 19 / 25 |
| peak total length, median / max | 23 / 67 | 24 / 33 | **19 / 28** |
| decoded elementary moves, median / max | 913 / 11,413 | 1,069 / 3,522 | 546 / 2,485 |
| first certified state, median index | 13 | 28 | 16 |
| first certified class | 516 BS-accept, 96 one-occurrence | 105 BS-accept, 195 one-occurrence | 220 BS-accept, 364 one-occurrence |
| last mixed state | 518 `(x,y)`, 94 two-block det ±1 | 300 `(x,y)` | 584 `(x,y)` |
| `bs_escape_feature` T at the root | 0 (all) | 0 (all) | `s_red - 1` in {2,4,6} |

"First certified state" is the first state on the saved path at which one of
the census's four terminal recognisers would fire: a pair of distinct
generators; `cheap_gates.canonical_two_block_gate`; a general BS gate whose
`bs_preflight` **accepts**; or a one-occurrence relator with unimodular
abelianisation.

Two observations about the mandated groups:

* `incumbent_restart` is entirely the router's `s20_generator` branch.  Because
  the root BS feature is 0 for all 612 rows, the router adds the four ambient
  Nielsen neighbours and drops the `4*T` term; every one of the 612 paths
  actually uses at least one of them.  The four images are used almost
  uniformly: `x->xY` 1,006, `x->xy` 994, `y->yx` 825, `y->yX` 809.
* 94 of the 612 `incumbent_restart` certificates stop at a **two-block pair**
  and hand off to `two_block.solve` (their last mixed state is a two-block pair
  with determinant ±1, not `(x,y)`); the other 518 run all the way down.
  In the two `plain_s20` groups the mixed path always reaches `(x,y)`, because
  `plain_search_fast` has no terminal macros at all.

Neither mandated group shows a repeatable macro: with no BS core the step
signatures degenerate to "substitution on relator 1 or 2", and the most common
5-step prefix in `incumbent_restart` occurs 7 times out of 612.  All of the
structure below is from the stalled-BS group.

## 2. The stalled-BS group: what the root looks like

584 solved rows, all through `plain_s20` and all cheap (median 58 units).
`(m, s_red)` is the BS parameter and the Britton-**reduced** stable-letter count
of the companion (the raw count can be larger; the reduced count is what
`bs_preflight` reports on rejection):

| `m` | solved, `s_red = 3` | solved, `s_red = 5` | solved, `s_red = 7` | solved total | unsolved |
|---|---|---|---|---|---|
| 2 | 404 | 121 | 0 | 525 | 7 (all `s_red = 7`) |
| 3 | 28 | 0 | 0 | 28 | 0 |
| 4 | 18 | 0 | 0 | 18 | 0 |
| 5 | 6 | 0 | 0 | 6 | 10 |
| 6 | 5 | 0 | 0 | 5 | 0 |
| 7 | 2 | 0 | 0 | 2 | 1 |

Root stable exponent: +1 in 491 rows, -1 in 93.

## 3. The one hard invariant: the stall never lifts while `R` is untouched

The single most useful empirical fact is a *non*-event.  For each solved
stalled path, walk forward while the root BS relator `R0` is still one of the
two relators and the gate still selects `R0` as the donor, and record
`bs_preflight`'s verdict:

* 7,558 such states across the 584 paths;
* `bs_preflight` accepted at **0** of them;
* `preflight`'s reported `stable_letters` is **constant** along that whole
  stretch in 584 / 584 rows (value 3 in 463 rows, value 5 in 121 rows).

This is exactly what Britton's lemma predicts, and it is proved in
[`STALLED_BS_THEORY.md`](STALLED_BS_THEORY.md) §2: a move on the companion
multiplies it by a conjugate of `R^{±1}`, which does not move it in
`BS(m,m+1)`, and the reduced stable-letter count of a cyclic word is a
conjugacy invariant there.

Charged cost of that provably-doomed recognition, on the 584 *solved* paths
alone: 7,558 `bs_preflight` calls and 59,414 scans.  On the 18 unsolved rows
the same recogniser is called at essentially every W-only descendant for the
whole 1,000-unit budget.

Consequences visible in the mined paths:

* every one of the 584 paths eventually modifies `R0`, and the first move that
  does so is a substitution whose target is `R0`: 584 / 584;
* it happens **exactly once** in 580 rows and twice in 4 rows - `n_sub_on_R0`
  is 1 or 2 for every single row;
* the position of that move is highly variable (median step index 10, mean 12,
  max 43), and everything before it is a run of `W <- rot(W) . rot(R^{±1})`
  moves that provably cannot certify anything (§3).

## 4. Macro patterns

Writing `S[W±]` for a substitution whose target is *not* `R0` (donor `R0`,
sign ±) and `S[R0±]` for one whose target *is* `R0`, the saved paths fall into
two macros.

### M1. Demote-and-swap (48 / 584 rows certify without ever touching `R0`)

A run of `S[W-]/S[W+]` moves turns the companion into a **BS(1,2) relator**,
i.e. a five-letter word such as `YYXyx` or `YYxyX`; the recogniser then reads
the pair the other way round - the (former) companion is the donor, `R0` is the
companion - and `bs_preflight` **accepts**.  In all 48 rows the new donor has
`m' = 1` and the old `m` was 2 (40 rows) or 3 (8 rows).

The shortest instance is one move (`ac19_11046`, 8 mixed steps, 17 units):

```
 0 ['YXXXyxx', 'YYXyxxYXXXyx']
 1 ['YYXyx',   'YXXXyxx']       2_-1_0_6   W    <- pair now BS(1,2)-donor, preflight ACCEPT
 2 ['YYXyx',   'YYxxyX']        2_-1_1_0   R0
 3 ['YYXyx',   'YYxyXYx']       2_1_3_3    W
 4 ['YYYx',    'YYXyx']         2_1_0_3    W
 5 ['YYx',     'YYYx']          2_-1_0_0   W
 6 ['Y',       'YYx']           2_-1_0_0   W
 7 ['Y',       'Yx']            2_-1_1_0   W
 8 ['Y',       'X']             2_-1_1_0   W
```

(`plain_s20` has no terminal macros, so the search keeps going by hand after
step 1; a gated policy would have stopped there.)

This macro is the empirical shadow of **Rule BS-DEMOTE**, which
[`STALLED_BS_THEORY.md`](STALLED_BS_THEORY.md) §4 proves, compiles and
verifies: it applies to exactly one congruence class per `m`, covers **427 of
the 602** stalled census rows (including 4 of the 18 unsolved ones), and its
certificates were machine-replayed to `['x','y']` for all 427.

### M2. One `R0` move, then run down to a small terminal (536 / 584 rows)

The remaining rows do a run of `S[W±]` moves, then a single `S[R0±]`, and then
another run of `S[W±]` down to a terminal.  Example `ac19_42`, class `(2,1,1)`,
8 steps / 18 units:

```
 0 ['YYXXyx',  'YXXXyxx']
 1 ['YXyxxyX', 'YXXXyxx']  1_-1_2_3  W
 2 ['YXyXyx',  'YXyxxyX']  2_1_0_1   R0   <- the single move on R
 3 ['YXYxx',   'YXyXyx']   2_1_0_1   W
 4 ['YYXyx',   'YXyXyx']   1_1_1_3   W    <- CERT bs_preflight_accept (donor m'=1)
 5..8 -> ['Y','X']
```

Distribution of the gap between the `R0` move and certification
(`first_certified - (i_R + 1)`): 48 rows certify *before* the `R0` move (macro
M1), then 82 at +2, 127 at +3, 151 at +4, 66 at +5, and a long tail; 59 rows sit
at +19.  So M2 is really "one `R0` move plus a 2-5 move tail", with the search
cost concentrated in *finding* the right `R0` move.

### The terminals are only two

| closing terminal | count | shape |
|---|---|---|
| `bs_preflight` accept | 220 | donor is a BS(1,2) relator (158) or BS(2,3) (62); never the original `R0` (0 / 220) |
| one-occurrence, det ±1 | 364 | pair lengths `(3,5)` with a 3-letter donor (190) or `(4,7)` with a 4-letter donor (174) |

No stalled-root path reaches a two-block pair before it reaches one of these
two (other than the trivial terminal itself, which is vacuously two-block).
Both facts are explained in the theory note: while `R` is fixed the companion
can be neither two-block nor one-occurrence, so those terminals only become
available after `R` has been modified, and the BS terminal is only ever reached
with a *new* donor.

### Path convergence (hub states)

The 584 paths funnel through a very small set of states - strong evidence that
the family is a handful of AC classes, not 584 problems:

| state | paths through it |
|---|---|
| `('Y','X')` | 584 (100%) |
| `('Y','YX')` | 213 (36%) |
| `('YYX','YYXYX')` / `('YX','YYX')` | 150 (26%) |
| `('YXXYx','YXYXyx')` / `('YYXYX','YXYXyx')` | 129 (22%) |
| `('YXYXyx','YXYxxyX')` | 120 (21%) |
| `('YXYxxyX','YXXXyxx')` | 114 (20%) |

`('YXYxxyX','YXXXyxx')` is the m=2 bottleneck: 112 rows sit on exactly that
state immediately before their single `R0` move, and 77 more on `YXyxxyx`,
67 on `YXXyxYx`, 59 on `YXyxYxx` - all seven letters long, all class `(2,1,1)`.

## 5. Congruence classes: 602 rows are 18 problems

§3 of the theory note shows that for a stalled companion with reduced
stable-letter count 3 the whole AC problem is determined by an integer label
`(m, alpha, beta)` computable in `O(|W|)`, invariant under rotation, inversion
of either relator, relator swap, all eight signed generator permutations, and
every move that uses `R` as the donor.  Labelling the 602 stalled census roots:

| label | rows | census outcome |
|---|---|---|
| `(2,1,1)` | 404 | all solved |
| `s_red = 5`, `m = 2` (3 sign necklaces) | 121 | all solved |
| `(3,1,2)` / `(3,2,1)` | 15 / 13 | all solved |
| `(4,1,2)` / `(4,1,3)` / `(4,2,2)` | 8 / 4 / 6 | all solved |
| `(5,2,3)` / `(5,3,1)` / `(5,3,2)` | 2 / 2 / 2 | all solved |
| `(6,1,3)` / `(6,2,3)` / `(6,2,4)` | 2 / 2 / 1 | all solved |
| `(7,4,1)` | 2 | all solved |
| **`(5,1,4)`** | 4 | **all unsolved** |
| **`(5,2,4)`** | 6 | **all unsolved** |
| **`(7,2,5)`** | 1 | **all unsolved** |
| **`s_red = 7`, `m = 2`, necklace `(+,+,-,+,-,+,-)`** | 7 | **all unsolved** |

No label is both solved and unsolved - as it must be, since same label means
explicitly AC-equivalent.  The 727-row residual therefore contains exactly
**four** distinct stalled-BS problems, and 602 census rows are 18 problems.

## 6. Why those 18 failed: budget allocation, not difficulty

All 18 unsolved stalled rows have the identical charge split
`(prepass 8, plain_s20 872, incumbent 120)`.  The stalled-BS feature is only
consulted in Stage 3, which therefore never got more than 120 units on any of
them, while the 584 solved siblings needed a median of 58 and up to 541 units.

On the four rows the brief permits searching, giving Stage 3 its full 1,000
units solves two of them outright (verified by
`verify_stalled_bs_examples.py`, section G, decoded and replayed to `['x','y']`):

| row | class | `root_router(budget=1000)` | gated `mid_search(budget=2000)` |
|---|---|---|---|
| ac19_99 | `(7,2,5)` | **solved, 896 units** | not solved at 2,000 |
| ac19_102 | `(5,2,4)` | **solved, 608 units** | solved, 1,638 units |
| ac19_103 | `(5,2,4)` | not solved at 1,000 | solved, 1,743 units |
| ac19_105 | `(5,1,4)` | not solved at 1,000 | solved, 1,191 units |

and Rule BS-DEMOTE certifies ac19_105 (and its whole class) with **no search at
all**: 17 carry moves plus 64 pinch rewrites, decoded to 1,515 elementary moves
and replayed to `['x','y']`.

## 7. What the mining says to implement

1. **Stop charging for provably doomed recognition.**  Once the root is a
   stalled BS pair, cache `R0`; at any descendant that still contains `R0` as
   the gate donor, skip `bs_preflight` entirely (§3 - it cannot accept).  That
   is 59,414 scans of pure waste on the solved rows alone and roughly the whole
   Stage-3 budget on the unsolved ones.
2. **Normalise before searching.**  Compute the label, carry the companion onto
   its class normal form, and search that.  602 census rows collapse to 18
   searches.
3. **Run Rule BS-DEMOTE first.**  It is `O(|W|)` to decide and covers 427 / 602
   rows with a deterministic certificate.
4. **Give Stage 3 the budget on stalled roots.**  `plain_search_fast` has no
   BS/two-block gates, so its 872 units on a stalled root can only ever *find*
   the terminal by accident; the router's `4*T` ordering with the gates on is
   what actually solves these rows.
