# ac19_cascade_screen: the 501-node cascade over all 72,779 AC19 orbits

Status: **both 501-node arms COMPLETE**, budget ladder in progress.
Carries a correction dated 2026-09-07 -- read it before quoting any
number in this file.
Branch `claude/ac19-leftover-solver-notebook-6yan6d`. Not merged to main.

## What was run

Every `Aut(F2)` orbit of `data/AC19_extended.txt` -- 72,779 of them,
156,762 dataset presentations -- through
`experiments/search/cascade_heuristics.py` at a 501-node budget and cap
255. That is the same prefix `experiments/search/hybrid_10m.py` runs
before its S20 restart, minus the three-row signature pin. The row list
is `ac19_autmin_screen/ac19_autmin_orbits.csv`, rebuilt by
`experiments/search/make_ac19_autmin_screen.py` and cross-checked
row-for-row against all 865 shipped residue rows.

    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen run \
        --arm cascade501 --workers 3

## Cost

| quantity | value |
|---|---:|
| rows | 72,779 |
| wall clock, 3 workers on 4 cores | 11.0 min |
| CPU | 0.55 core-hours (0.027 s/row) |
| peak RSS per worker | 0.18 GB |
| errors, reservation failures | 0 |

For contrast, the same cap 255 at the 10M budget plans a
2,140,262,144-state reservation -- **319.0 GiB per lane**. On the 15 GB
box this ran on, `plan_memory` clips that reservation by a factor of
about 170, to roughly 58,000 of the 10,000,000 nodes. The screen is the
cheap pass; the 10M hybrid is not, and no amount of arranging makes it so.

## What came back

| outcome | rows | share |
|---|---:|---:|
| **AC-certified** (substitution-only, replayed to a terminal pair) | 27,164 | 37.32% |
| aut-assisted only (solved, but the path changes basis) | 43,485 | 59.75% |
| neither, at 501 nodes | 2,130 | 2.93% |
| certificates that failed replay | 0 | -- |

AC-certified, by which component won:

| winner | rows | what it is |
|---|---:|---|
| `rewrite` | 18,839 | `bs_collapse`: the relator is a signed form of `b^-1 a b a^-2`, rewritten by a bounded proof-carrying substitution path |
| `s40_gen` | 8,324 | the L + 40*S beam happened to reach a terminal pair without using any of the Nielsen images in its heap |
| `terminal` | 1 | `ac19_347` is the trivial pair itself (89 dataset members land on it) |

Median nodes to an AC solve: 12. Maximum: 257. Nothing about this pass
is expensive on the rows it settles.

## CORRECTION (2026-09-07): `aut_assisted` rows ARE AC-solved

Everything below that treats an automorphism-assisted path as "not an AC
solve" is **wrong**, and the two arms' headline comparison inverts once it
is fixed. Recorded in place rather than edited away, because the wrong
version was quoted.

AC moves are equivariant under `Aut(F2)`: apply `phi^-1` to every word of
`r_i -> r_i r_j`, `r_i -> r_i^-1` or `r_i -> w r_i w^-1` and the result is
the same move on the images. So push the accumulated basis change back
through a mixed path and every automorphism step collapses to a no-op,
leaving a pure AC path from the input to SOME basis of `F2`. Nielsen's
theorem finishes it: any basis reaches `(x, y)` by tuple Nielsen moves
(swap, invert, multiply), and those are themselves AC moves.

Measured on MS640 aut-assisted solves: 26 of 30 push back to a genuine AC
step sequence directly, and the other 4 are not failures -- the path
passes through a terminal before its recorded end. The pure-AC prefix
lands on bases 1 to 5 letters long (`('Y','Yx')`, `('Y','YYX')`,
`('Y','X')`), so the tail is a handful of moves.

So the corrected comparison at 501 nodes over all 72,779 orbits:

| arm | AC-solved once decoded |
|---|---:|
| cascade501 | 27,164 + 43,485 = **70,649 (97.07%)** |
| ac501 (no Nielsen images in the heap) | 64,541 (88.68%) |

The Nielsen moves are a net **gain of about 6,100 rows**, not the loss of
38,658 claimed below. Same for MS640: 640/640 is an AC result, not
146/640.

What is true is narrower and is a code fact, not a mathematical one:
`hybrid_10m` refuses these solves because nothing in the repo decodes
them, and writing an Aut move into a move-string field would be a format
bug. The decoder is the missing piece, not the proof.

## The distinction the numbers turn on

`cascade_heuristics`' `s40_gen` arm pushes Nielsen images into the same
heap as AC substitutions. A path that uses one proves AC-triviality of an
**automorphic image** of the presentation, not of the presentation. So
`solved` here counts only substitution-only paths, each replayed move by
move through `moves_to_states` and required to end on a terminal pair;
anything reached through a basis change is recorded as `aut_assisted` and
never certified.

`hybrid_10m.run_hybrid_10m` enforces the same line by refusing a prefix
solve outright -- "so an Aut move is never serialized as an ordinary AC
substitution certificate". That refusal is correct for its three pinned
rows. On a screen it is not usable: the prefix settles 97% of the list,
so the refusal would fire on nearly every row.

**`aut_assisted` does not mean "no AC path exists".** It means the
cheapest path this heap reached used a basis change -- and per the
correction above, such a path decodes to an AC certificate. The control
below is still worth having: it says what the search reaches with the
Nielsen door shut. It is not, as first written, the arbiter of which
solves are real.

## The control, and what it says about the Nielsen moves

`ac501` is `s40_gen` with one door shut: same priority (L + 40*S), same
501 nodes, same cap 255, no Nielsen image ever entering the heap. Same
72,779 rows, 1.22 core-hours.

| outcome | cascade501 | ac501 (control) |
|---|---:|---:|
| AC-certified | 27,164 (37.32%) | **64,541 (88.68%)** |
| aut-assisted only | 43,485 (59.75%) | 0 |
| neither | 2,130 (2.93%) | 8,238 (11.32%) |
| rejected certificates | 0 | 0 |

Paired over all 72,779:

| | rows |
|---|---:|
| AC-solved by the control only | 38,658 |
| AC-solved by both | 25,883 |
| AC-solved by the cascade only | 1,281 |
| AC-solved by neither | 6,957 |

Of the 43,485 rows the cascade could only reach by changing basis, the
control AC-solves **38,512 (88.6%)** at the same budget. Only 4,973 are
out of AC reach at 501 nodes.

**Superseded by the correction at the top of this file.** The paired
counts here are counts of rows whose recorded certificate was already
substitution-only. They are not counts of AC-solvable rows: a decoded
aut-assisted path is an AC certificate too, and with decoding the cascade
reaches 70,649 against the control's 64,541.

What the cascade does add is `bs_collapse`. Its 1,281 exclusive solves
are the rows the beam cannot reach and the pattern can, including all 22
below. The arm worth building next is the obvious one and nobody has run
it: `bs_collapse` first, then the AC-only beam, no Nielsen edges at all.

## Against the shipped hard lists

| list | rows | AC-solved by the cascade at 501 nodes |
|---|---:|---:|
| `unsolved_10k_s20_mk2.csv` | 259 | **22** |
| `unsolved_100k_s20_mk2.csv` | 39 | 0 |
| `unsolved_1m_s20_mk2.csv` | 14 | 0 |
| `unsolved_5m_s20_mk2.csv` | 9 | 0 |

The 22 are real and they are one family: every one of them has
`r1 = YXXyx`, the shape `bs_collapse` recognizes. `bs_collapse` settles
each in 106 to 257 nodes with a 105-to-256-move substitution path that
replays to a terminal pair.

**It is a speed win, not a coverage win.** Given 100,000 nodes instead of
10,000, s20_mk2 solves all 22 itself, at 10,131 to 33,768 nodes (median
10,249). Against the cascade's median 112 nodes that is a **92x median
speedup** -- worth having, and not new mathematics. It is also a pattern
recognizer's win rather than a better ordering's: on the 39, 14 and 9
rows of the harder lists the same recognizer fires zero times, and the
AC-only control solves 0 of the 259.

## What is actually still open

Every orbit absent from `unsolved_10k_s20_mk2.csv` was AC-solved by
s20_mk2 within 10,000 nodes. So of the 8,238-row control residue, only
**259** are rows anyone still owes a proof for, and the open set is the
one the earlier ladder already found:

| list | rows | still unsolved by `ac501` at 501 nodes |
|---|---:|---:|
| `unsolved_100k_s20_mk2.csv` | 39 | 39 |
| `unsolved_1m_s20_mk2.csv` | 14 | 14 |
| `unsolved_5m_s20_mk2.csv` | 9 | 9 |

Neither 501-node arm touched any of them. Nothing in this pass changes
what is open; it changes how cheaply the settled part can be re-settled.

One gap the repo cannot close: 2,056 of the 72,779 orbits sit outside the
70,723-orbit intersection that `run_leftovers_1m.py` documents, and
nothing records which. A ladder survivor that is not on a shipped list is
therefore either a row this arm is weak on or a row nobody ever searched,
and only an s20_mk2 re-run at 10,000 nodes tells them apart.

## Files

| file | what |
|---|---|
| `unsolved_cascade501_b501.csv` | the 2,130 the cascade did not settle at all |
| `aut_assisted_cascade501_b501.csv` | the 43,485 reached only through a basis change |
| `ac19_cascade_screen_cascade501_b501_mrl255.jsonl` | the run itself, 57 MB, git-ignored |
| `*_certificates.jsonl` | regenerated on demand by `certify`, digest-checked against the run |

The run jsonl is not committed, in line with `ac19_autmin_screen/`, which
ships residues rather than the screen. Every solved row carries
`certificate_sha256`; `certify` re-runs the search, replays the moves and
refuses to write anything whose digest has moved.
