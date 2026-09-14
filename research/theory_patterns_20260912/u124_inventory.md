# U124 structural inventory and tiny panel

This is a finite word inventory of the current 124 best-known representatives. No heap search was run and no new solve or theorem is claimed. The 124 are retained components from bounded AC moves modulo Aut(F2), an upper bound on distinct unresolved problems. They are not 124 proved distinct AC classes.

## Inputs and verification

- `data/ms_unsolved_reps/aca_124_initial.csv`: 124 rows; SHA-256 `614bce2d3250a1acca81ec9de0fc0deb097eb74c4d56e6a9718985a150bb1d2c`.
- `data/ms_unsolved_reps/aca_124_reduced.csv`: 124 rows; SHA-256 `5be80a918b2b970e9bba7557a168908d8225ee8f781cc884cf0df6a845bbb72a`.
- `data/ms_unsolved_reps/aca_124_best.csv`: 124 rows; SHA-256 `8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3`.

Initial/best columns: `name,r1,r2,n_members,members`.
Ledger columns: `name,r1,r2,n_members,members,reduced,reduce_kind,mu_in,mu_out,new_r1,new_r2,n_hops,source,ext_label`.

The IDs are exactly `aca_0` through `aca_123`, once each and in that order. `n_members` sums to 261 A-equivalence representatives; it does not count the 550 raw MS cells. All three files join exactly by name. All 36 changes reconstruct from the ledger, are strict length reductions, and lower aggregate length 2,446 to 2,356; the other 88 pairs are unchanged. All 248 words are cyclically freely reduced, and every exponent matrix has determinant ±1. These properties were independently asserted during generation.

The README contains one stale sentence claiming `source` is `none` on every row; the actual ledger has `mu_ladder_r256_b64` on the 36 strict reductions and `none` on 88 rows. This inventory follows the CSV bytes.

## Lengths

| Total length | Rows |
|---:|---:|
| 13 | 1 |
| 14 | 2 |
| 15 | 10 |
| 16 | 7 |
| 17 | 22 |
| 18 | 10 |
| 19 | 27 |
| 20 | 8 |
| 21 | 15 |
| 22 | 6 |
| 23 | 9 |
| 24 | 3 |
| 25 | 4 |

Mean total length 19.000000; median 19.0; range 13–25. Ordered length-pair frequencies are exact in JSON.

Shortest representatives (all rows of total length at most 15):

| ID | r1 | r2 | Lengths | Exponent rows |
|---|---|---|---|---|
| aca_115 | `YXYxyx` | `YYYYxxx` | [6, 7] | ((1, -1), (3, -4)) |
| aca_116 | `YYYXyyX` | `YXXXyxx` | [7, 7] | ((-2, -1), (-1, 0)) |
| aca_117 | `YYYXyyx` | `YXXXyxx` | [7, 7] | ((0, -1), (-1, 0)) |
| aca_1 | `YYXXyxx` | `YYYxyXyX` | [7, 8] | ((0, -1), (-1, -1)) |
| aca_8 | `YXyXYxx` | `YYXYXyyx` | [7, 8] | ((0, -1), (-1, -1)) |
| aca_9 | `YXXXyxx` | `YYYXXyyX` | [7, 8] | ((-1, 0), (-3, -1)) |
| aca_10 | `YXXXyxx` | `YYXYXyyX` | [7, 8] | ((-1, 0), (-3, -1)) |
| aca_11 | `YXXXyxx` | `YYYXyxyx` | [7, 8] | ((-1, 0), (1, -1)) |
| aca_12 | `YXXXyxx` | `YYXYxyyX` | [7, 8] | ((-1, 0), (-1, -1)) |
| aca_14 | `YXXyXyx` | `YYYXyyxx` | [7, 8] | ((-2, 1), (1, -1)) |
| aca_118 | `YXXyxYx` | `YYYYXyxx` | [7, 8] | ((0, -1), (1, -3)) |
| aca_120 | `YXXyxYx` | `YYYXyyxx` | [7, 8] | ((0, -1), (1, -1)) |
| aca_121 | `YXyXYxx` | `YYYXXYYx` | [7, 8] | ((0, -1), (-1, -5)) |

## Exponent classes

There are 53 exact ordered exponent matrices and 18 classes after only row/column signed permutations. This is an elementary feature quotient, not an AC or Aut(F2) classification. Lowercase letters contribute +1; uppercase letters contribute −1. Full frequencies and the exact member IDs of every class are in JSON.

| Exact matrix, rows (r1,r2), columns (x,y) | Count | IDs |
|---|---:|---|
| `((-1, -1), (0, -1))` | 18 | aca_18, aca_20, aca_21, aca_25, aca_38, aca_40, aca_42, aca_47, aca_50, aca_63, aca_65, aca_69, aca_73, aca_91, aca_93, aca_96, aca_102, aca_104 |
| `((1, -1), (0, -1))` | 12 | aca_19, aca_22, aca_23, aca_41, aca_46, aca_49, aca_64, aca_68, aca_70, aca_89, aca_92, aca_103 |
| `((-1, -3), (0, -1))` | 6 | aca_17, aca_37, aca_39, aca_62, aca_94, aca_101 |
| `((-1, 1), (0, -1))` | 4 | aca_15, aca_27, aca_52, aca_74 |
| `((0, -1), (-1, -7))` | 4 | aca_75, aca_77, aca_109, aca_123 |
| `((0, -1), (-1, -6))` | 4 | aca_7, aca_36, aca_61, aca_122 |
| `((0, -1), (-1, 0))` | 4 | aca_43, aca_66, aca_90, aca_117 |
| `((0, -1), (1, -4))` | 4 | aca_60, aca_81, aca_111, aca_119 |
| `((0, -1), (1, -3))` | 4 | aca_3, aca_48, aca_58, aca_118 |
| `((-2, -1), (-1, 0))` | 3 | aca_4, aca_100, aca_116 |
| `((0, -1), (-1, -8))` | 3 | aca_84, aca_85, aca_107 |
| `((0, -1), (1, -6))` | 3 | aca_83, aca_110, aca_112 |
| `((1, -3), (0, -1))` | 3 | aca_26, aca_28, aca_51 |
| `((-6, -1), (1, 0))` | 2 | aca_86, aca_87 |
| `((-2, 1), (1, -1))` | 2 | aca_14, aca_78 |
| `((-1, -4), (0, -1))` | 2 | aca_13, aca_44 |
| `((-1, -1), (-2, -3))` | 2 | aca_30, aca_56 |
| `((-1, -1), (-1, 0))` | 2 | aca_71, aca_105 |
| `((-1, -1), (1, 0))` | 2 | aca_16, aca_95 |
| `((-1, 0), (-3, -1))` | 2 | aca_9, aca_10 |
| `((-1, 0), (-1, -1))` | 2 | aca_12, aca_79 |
| `((0, -1), (-1, -9))` | 2 | aca_98, aca_113 |
| `((0, -1), (-1, -5))` | 2 | aca_45, aca_121 |
| `((0, -1), (-1, -1))` | 2 | aca_1, aca_8 |
| `((0, -1), (1, -5))` | 2 | aca_76, aca_97 |
| `((-7, -1), (-1, 0))` | 1 | aca_106 |
| `((-6, -1), (-1, 0))` | 1 | aca_67 |
| `((-5, -1), (1, 0))` | 1 | aca_88 |
| `((-4, -1), (1, 0))` | 1 | aca_82 |
| `((-4, -1), (3, 1))` | 1 | aca_5 |
| `((-2, -1), (-3, -1))` | 1 | aca_54 |
| `((-2, -1), (1, 0))` | 1 | aca_35 |
| `((-2, -1), (1, 1))` | 1 | aca_29 |
| `((-2, 1), (1, 0))` | 1 | aca_2 |
| `((-1, -3), (-2, -5))` | 1 | aca_24 |
| `((-1, -1), (-4, -3))` | 1 | aca_57 |
| `((-1, -1), (-3, -4))` | 1 | aca_80 |
| `((-1, -1), (0, 1))` | 1 | aca_33 |
| `((-1, 0), (-2, -1))` | 1 | aca_55 |
| `((-1, 0), (1, -1))` | 1 | aca_11 |
| `((0, -1), (-1, -4))` | 1 | aca_0 |
| `((0, -1), (-1, -3))` | 1 | aca_31 |
| `((0, -1), (-1, 1))` | 1 | aca_99 |
| `((0, -1), (-1, 2))` | 1 | aca_72 |
| `((0, -1), (1, -10))` | 1 | aca_108 |
| `((0, -1), (1, -7))` | 1 | aca_114 |
| `((0, -1), (1, -2))` | 1 | aca_34 |
| `((0, -1), (1, -1))` | 1 | aca_120 |
| `((0, -1), (1, 2))` | 1 | aca_53 |
| `((1, -1), (1, -2))` | 1 | aca_32 |
| `((1, -1), (3, -4))` | 1 | aca_115 |
| `((1, 0), (-3, -1))` | 1 | aca_6 |
| `((2, -1), (7, -4))` | 1 | aca_59 |

## Donor syntax frequencies

All 248 relators are counted separately. Neither the label “donor” nor a pattern match asserts a theorem. Maximal cyclic blocks retain x/y labels and signed powers. Canonical block patterns identify rotation and relator inversion only. For a nominated stable generator t, the stable sequence records `(sign of t, intervening exponent of the other generator)` once per stable-letter occurrence, including zero between adjacent t letters. Both choices t=x and t=y are inventoried independently.

| Cyclic block count | Relators |
|---:|---:|
| 2 | 2 |
| 4 | 115 |
| 6 | 102 |
| 8 | 10 |
| 10 | 19 |

Signed stable occurrence counts, written `(positive, negative)`:

| Stable generator | Occurrence pair : number of relators |
|---|---|
| x | (0, 2): 1; (0, 3): 2; (0, 4): 1; (0, 5): 1; (0, 6): 3; (0, 7): 1; (1, 1): 44; (1, 2): 16; (1, 3): 9; (1, 4): 1; (1, 5): 2; (2, 1): 16; (2, 2): 24; (2, 3): 62; (2, 4): 3; (2, 5): 2; (3, 0): 1; (3, 2): 33; (3, 3): 21; (3, 4): 1; (4, 1): 1; (4, 2): 1; (4, 5): 1; (7, 0): 1 |
| y | (0, 3): 10; (0, 4): 4; (0, 5): 3; (0, 6): 4; (0, 7): 4; (0, 8): 3; (0, 9): 2; (0, 10): 1; (1, 1): 6; (1, 2): 94; (1, 4): 4; (1, 5): 2; (1, 6): 1; (1, 7): 2; (1, 8): 1; (2, 1): 7; (2, 2): 4; (2, 3): 18; (2, 4): 2; (2, 5): 4; (2, 6): 3; (2, 7): 1; (2, 8): 1; (3, 2): 2; (3, 3): 16; (3, 4): 13; (3, 7): 1; (4, 2): 2; (4, 3): 2; (4, 5): 12; (5, 6): 9; (6, 7): 6; (7, 8): 4 |

There are 119 distinct canonical cyclic block patterns among 248 relators. The most frequent 16 are below; all patterns, their occurrences, and all stable sequences are in JSON.

| Canonical cyclic block sequence | Frequency | Example |
|---|---:|---|
| `(('x', -3), ('y', 1), ('x', 1), ('y', -1), ('x', 1), ('y', -1))` | 11 | aca_18:r1 |
| `(('x', -2), ('y', 1), ('x', 1), ('y', -1), ('x', 1), ('y', -1))` | 11 | aca_0:r1 |
| `(('x', -1), ('y', -4), ('x', 1), ('y', 5))` | 9 | aca_37:r2 |
| `(('x', -2), ('y', -1), ('x', 2), ('y', 1), ('x', 1), ('y', -1))` | 8 | aca_22:r1 |
| `(('x', -3), ('y', 1), ('x', 1), ('y', -1), ('x', 2), ('y', -1))` | 7 | aca_48:r1 |
| `(('x', -2), ('y', -1), ('x', 2), ('y', 1), ('x', -1), ('y', -1))` | 7 | aca_21:r1 |
| `(('x', -1), ('y', -3), ('x', 1), ('y', 4))` | 7 | aca_17:r2 |
| `(('x', -3), ('y', 1), ('x', 1), ('y', -1), ('x', 2), ('y', 1))` | 6 | aca_45:r1 |
| `(('x', -3), ('y', 1), ('x', 2), ('y', -2))` | 6 | aca_16:r1 |
| `(('x', -3), ('y', 1), ('x', 2), ('y', -1))` | 6 | aca_9:r1 |
| `(('x', -2), ('y', -1), ('x', 2), ('y', 2))` | 6 | aca_1:r1 |
| `(('x', -2), ('y', 1), ('x', 1), ('y', -1), ('x', 1), ('y', 1))` | 6 | aca_8:r1 |
| `(('x', -1), ('y', -5), ('x', 1), ('y', 6))` | 6 | aca_62:r2 |
| `(('x', -3), ('y', -1), ('x', 1), ('y', -1), ('x', 1), ('y', -1))` | 5 | aca_17:r1 |
| `(('x', -3), ('y', 1), ('x', 1), ('y', -1), ('x', 1), ('y', 1))` | 5 | aca_19:r1 |
| `(('x', -1), ('y', -6), ('x', 1), ('y', 7))` | 5 | aca_89:r2 |

Exactly two opposite-sign stable-letter occurrences appear in 50 relator/generator choices. Their literal base-power magnitudes are tabulated below. A same-sign base-power pair is retained as such; it is not silently treated as a BS(m,n) completion.

| Stable generator | Absolute base powers | Opposite base signs? | Count |
|---|---|---|---:|
| x | 3, 4 | True | 12 |
| x | 4, 5 | True | 12 |
| x | 5, 6 | True | 9 |
| x | 6, 7 | True | 6 |
| y | 2, 3 | True | 6 |
| x | 7, 8 | True | 4 |
| x | 2, 3 | True | 1 |

## A priori 20-row diagnostic panel

A priori for future tests: cover every observed total length 13 through 25, then add same-versus-opposite stable signs, larger/equal powers, maximal signed exponents, and balanced long relators. Selection uses raw structural features and initial-to-best provenance only, never a future recognizer outcome. This is a development diagnostic panel, not a representative statistical sample or validation set.

| ID | r1 | r2 | L | Rationale |
|---|---|---|---:|---|
| aca_115 | `YXYxyx` | `YYYYxxx` | 13 | Shortest total length (13); one of the two literal two-block relators, with powers 3 and -4. |
| aca_116 | `YYYXyyX` | `YXXXyxx` | 14 | Total length 14; balanced lengths 7/7; r1 has two x-stable occurrences of the same sign. |
| aca_1 | `YYXXyxx` | `YYYxyXyX` | 15 | Total length 15; recurring r1 YYXXyxx, contrasting equal-magnitude x powers across unequal y powers. |
| aca_13 | `YYXXYYx` | `YXXXyxxYx` | 16 | Total length 16; r1 has two negative y blocks of size 2, separated by unequal signed x blocks. |
| aca_30 | `YYXXyx` | `YYYYYxyXXyX` | 17 | Total length 17; one of only three rows with a length-6 relator, with an 11-letter companion. |
| aca_55 | `YYXXXyxyx` | `YYxYXXyyX` | 18 | Total length 18; unique 9/9 length pair and neither relator has only four cyclic blocks. |
| aca_80 | `YYXXyx` | `YYYXyXYYYxyXX` | 19 | Total length 19; same length-6 donor as aca_30, now with a 13-letter companion and a recorded strict reduction. |
| aca_59 | `YXXYxxyxx` | `YYYYxxxxxxx` | 20 | Total length 20; the other literal two-block relator, powers 7 and -4, paired with exponent vector (2,-1). |
| aca_79 | `YYXXXyyxx` | `YXXXXXyxxYxx` | 21 | Total length 21; r1 has y-block magnitudes 2 and 2 with opposite signs, and unequal x-block magnitudes 3 and 2. |
| aca_82 | `YYYXXXXXyyx` | `YYXyxxyyxYX` | 22 | Total length 22; a longest shortest-relator length of 11, with r1 x exponent -4. |
| aca_109 | `YYXXyxYxxyX` | `YYYYYYXXXYxx` | 23 | Total length 23; length pair 11/12, unique in the table, after a recorded strict reduction. |
| aca_108 | `YXYXyxyXYxx` | `YYYYYYYxYYXYx` | 24 | Total length 24; a maximal 10-block r1 and the most negative r2 y exponent (-10). |
| aca_101 | `YXXXYxYx` | `YYYYYYYYXyyyyyyyx` | 25 | Total length 25; maximum total length and maximum individual length (17), with opposite x-stable occurrences in r2. |
| aca_117 | `YYYXyyx` | `YXXXyxx` | 14 | Controlled structural contrast with aca_116 at 7/7: r1 now has opposite x-stable signs and zero x exponent. |
| aca_9 | `YXXXyxx` | `YYYXXyyX` | 15 | A shortest occurrence of a two-opposite-y-stable-letter donor with base powers of magnitudes 2 and 3. |
| aca_67 | `YYXXXyXXX` | `YYXyxYXyxyX` | 20 | r1 has x exponent -6 and same-sign x blocks of magnitude 3; contrasts with the exponent-zero equal-power pattern. |
| aca_86 | `YYYXXXXXyyX` | `YYXyxxyyXYx` | 22 | Pairs with aca_82 at 11/11 while changing r1 x exponent from -4 to -6 and the companion exponent accordingly. |
| aca_106 | `YYXXXXyXXX` | `YYXyxyXYxyX` | 21 | r1 has x exponent -7, the largest absolute r1 x exponent in the table; length pair 10/11. |
| aca_54 | `YYXXXXyxx` | `YYxxyXXXXX` | 19 | Consecutive comparisons of larger powers: r1 has opposite signed x blocks of magnitudes 4 and 2; r2 2 and 5. |
| aca_5 | `YYXXXyX` | `YYYxyXyxyxyx` | 19 | r2 has 10 cyclic blocks at length 12; adds a complicated companion to a length-7 first relator. |

## Existing U124 results to respect

- `results/heuristic_search/goal_frontiers/U124_UNCAPPED_10K.md` (Exact current best table; manifest input hash independently matched): 0/124 solves and 0/124 strict total-length reductions at 10,000 shared charged units per row, ordinary and rewrite caps absent. No new searches run here.
- `results/heuristic_search/goal_frontiers/U124_UNCAPPED_10K.md` (Saved root recognition of current best and older initial tables): Zero strict Nielsen reductions and zero special b^-1 a b a^-2 rewrite hits on either table. Do not rescreen those unchanged recognizers as a new idea.
- `results/heuristic_search/goal_frontiers/U124_UNCAPPED_10K.md` (Historical ordinary S20 result, older initial table, cited by saved report rather than re-run here): 0/124 solves at 10 million pops and cap 64; 14 rows found shorter total length. Different inputs/budget from current best study.
- `research/supermoves_20260908/NEXT_THEORY_AFTER_FRINGE.md` (Later AC19 theory records): Explicitly states no U124 scan. AC19 hard-panel donor/primitive/fringe negatives are not automatically U124 negatives.

The saved current-best cascade manifest contains the same input SHA-256 as this inventory. Its ten equal-total rebalances are aca_5, aca_29, aca_30, aca_31, aca_69, aca_70, aca_74, aca_79, aca_80, and aca_89; these are not strict progress. Later supermove theory often targets AC19 panels and explicitly disclaims U124 coverage. Absence of a U124 record in that work is not evidence that its recognizers fail here.

## Full current-row structural index

Lengths, exponent matrices and cyclic block counts are shown below; JSON additionally preserves exact words, members, letter counts, canonical patterns and both stable-letter sequence decompositions for every row.

| ID | Lengths | L | Exponent matrix | Cyclic block counts | Changed from initial |
|---|---|---:|---|---|---|
| aca_0 | [7, 11] | 18 | `((0, -1), (-1, -4))` | [6, 6] | False |
| aca_1 | [7, 8] | 15 | `((0, -1), (-1, -1))` | [4, 6] | False |
| aca_2 | [7, 9] | 16 | `((-2, 1), (1, 0))` | [6, 4] | False |
| aca_3 | [7, 10] | 17 | `((0, -1), (1, -3))` | [6, 6] | False |
| aca_4 | [7, 11] | 18 | `((-2, -1), (-1, 0))` | [4, 10] | False |
| aca_5 | [7, 12] | 19 | `((-4, -1), (3, 1))` | [4, 10] | False |
| aca_6 | [9, 10] | 19 | `((1, 0), (-3, -1))` | [6, 6] | False |
| aca_7 | [7, 9] | 16 | `((0, -1), (-1, -6))` | [4, 6] | False |
| aca_8 | [7, 8] | 15 | `((0, -1), (-1, -1))` | [6, 6] | False |
| aca_9 | [7, 8] | 15 | `((-1, 0), (-3, -1))` | [4, 4] | False |
| aca_10 | [7, 8] | 15 | `((-1, 0), (-3, -1))` | [4, 6] | False |
| aca_11 | [7, 8] | 15 | `((-1, 0), (1, -1))` | [4, 6] | False |
| aca_12 | [7, 8] | 15 | `((-1, 0), (-1, -1))` | [4, 6] | False |
| aca_13 | [7, 9] | 16 | `((-1, -4), (0, -1))` | [4, 6] | False |
| aca_14 | [7, 8] | 15 | `((-2, 1), (1, -1))` | [6, 4] | False |
| aca_15 | [8, 9] | 17 | `((-1, 1), (0, -1))` | [6, 4] | False |
| aca_16 | [8, 9] | 17 | `((-1, -1), (1, 0))` | [4, 8] | False |
| aca_17 | [8, 9] | 17 | `((-1, -3), (0, -1))` | [6, 4] | False |
| aca_18 | [8, 9] | 17 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_19 | [8, 9] | 17 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_20 | [8, 9] | 17 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_21 | [8, 9] | 17 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_22 | [8, 9] | 17 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_23 | [8, 9] | 17 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_24 | [8, 9] | 17 | `((-1, -3), (-2, -5))` | [4, 6] | False |
| aca_25 | [8, 9] | 17 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_26 | [8, 9] | 17 | `((1, -3), (0, -1))` | [6, 4] | False |
| aca_27 | [8, 9] | 17 | `((-1, 1), (0, -1))` | [6, 4] | False |
| aca_28 | [8, 9] | 17 | `((1, -3), (0, -1))` | [6, 4] | False |
| aca_29 | [7, 10] | 17 | `((-2, -1), (1, 1))` | [4, 8] | False |
| aca_30 | [6, 11] | 17 | `((-1, -1), (-2, -3))` | [4, 6] | False |
| aca_31 | [7, 10] | 17 | `((0, -1), (-1, -3))` | [4, 6] | False |
| aca_32 | [8, 9] | 17 | `((1, -1), (1, -2))` | [6, 6] | False |
| aca_33 | [8, 9] | 17 | `((-1, -1), (0, 1))` | [6, 8] | False |
| aca_34 | [7, 9] | 16 | `((0, -1), (1, -2))` | [6, 4] | True |
| aca_35 | [7, 11] | 18 | `((-2, -1), (1, 0))` | [4, 8] | False |
| aca_36 | [7, 9] | 16 | `((0, -1), (-1, -6))` | [6, 6] | True |
| aca_37 | [8, 11] | 19 | `((-1, -3), (0, -1))` | [4, 4] | False |
| aca_38 | [8, 11] | 19 | `((-1, -1), (0, -1))` | [4, 4] | False |
| aca_39 | [8, 11] | 19 | `((-1, -3), (0, -1))` | [6, 4] | False |
| aca_40 | [8, 11] | 19 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_41 | [8, 11] | 19 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_42 | [8, 11] | 19 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_43 | [7, 11] | 18 | `((0, -1), (-1, 0))` | [4, 10] | True |
| aca_44 | [7, 11] | 18 | `((-1, -4), (0, -1))` | [4, 10] | True |
| aca_45 | [9, 10] | 19 | `((0, -1), (-1, -5))` | [6, 4] | False |
| aca_46 | [8, 11] | 19 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_47 | [8, 11] | 19 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_48 | [9, 10] | 19 | `((0, -1), (1, -3))` | [6, 4] | False |
| aca_49 | [8, 11] | 19 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_50 | [8, 11] | 19 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_51 | [8, 11] | 19 | `((1, -3), (0, -1))` | [6, 4] | False |
| aca_52 | [8, 11] | 19 | `((-1, 1), (0, -1))` | [6, 4] | False |
| aca_53 | [7, 11] | 18 | `((0, -1), (1, 2))` | [6, 8] | False |
| aca_54 | [9, 10] | 19 | `((-2, -1), (-3, -1))` | [4, 4] | False |
| aca_55 | [9, 9] | 18 | `((-1, 0), (-2, -1))` | [6, 6] | True |
| aca_56 | [8, 11] | 19 | `((-1, -1), (-2, -3))` | [4, 6] | False |
| aca_57 | [8, 11] | 19 | `((-1, -1), (-4, -3))` | [4, 6] | False |
| aca_58 | [7, 10] | 17 | `((0, -1), (1, -3))` | [6, 4] | True |
| aca_59 | [9, 11] | 20 | `((2, -1), (7, -4))` | [6, 2] | False |
| aca_60 | [9, 11] | 20 | `((0, -1), (1, -4))` | [6, 4] | False |
| aca_61 | [9, 11] | 20 | `((0, -1), (-1, -6))` | [6, 4] | False |
| aca_62 | [8, 13] | 21 | `((-1, -3), (0, -1))` | [6, 4] | False |
| aca_63 | [8, 13] | 21 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_64 | [8, 13] | 21 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_65 | [8, 13] | 21 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_66 | [9, 11] | 20 | `((0, -1), (-1, 0))` | [4, 10] | True |
| aca_67 | [9, 11] | 20 | `((-6, -1), (-1, 0))` | [4, 10] | True |
| aca_68 | [8, 13] | 21 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_69 | [8, 13] | 21 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_70 | [8, 13] | 21 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_71 | [8, 11] | 19 | `((-1, -1), (-1, 0))` | [4, 10] | True |
| aca_72 | [7, 11] | 18 | `((0, -1), (-1, 2))` | [4, 10] | True |
| aca_73 | [8, 13] | 21 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_74 | [8, 13] | 21 | `((-1, 1), (0, -1))` | [6, 4] | False |
| aca_75 | [9, 12] | 21 | `((0, -1), (-1, -7))` | [6, 4] | False |
| aca_76 | [9, 12] | 21 | `((0, -1), (1, -5))` | [6, 4] | False |
| aca_77 | [9, 12] | 21 | `((0, -1), (-1, -7))` | [6, 4] | False |
| aca_78 | [7, 12] | 19 | `((-2, 1), (1, -1))` | [6, 8] | True |
| aca_79 | [9, 12] | 21 | `((-1, 0), (-1, -1))` | [4, 6] | False |
| aca_80 | [6, 13] | 19 | `((-1, -1), (-3, -4))` | [4, 8] | True |
| aca_81 | [7, 11] | 18 | `((0, -1), (1, -4))` | [6, 4] | True |
| aca_82 | [11, 11] | 22 | `((-4, -1), (1, 0))` | [4, 8] | False |
| aca_83 | [9, 13] | 22 | `((0, -1), (1, -6))` | [6, 4] | False |
| aca_84 | [9, 13] | 22 | `((0, -1), (-1, -8))` | [6, 4] | False |
| aca_85 | [7, 11] | 18 | `((0, -1), (-1, -8))` | [6, 4] | True |
| aca_86 | [11, 11] | 22 | `((-6, -1), (1, 0))` | [4, 8] | False |
| aca_87 | [9, 11] | 20 | `((-6, -1), (1, 0))` | [4, 10] | True |
| aca_88 | [8, 11] | 19 | `((-5, -1), (1, 0))` | [4, 10] | True |
| aca_89 | [8, 15] | 23 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_90 | [9, 11] | 20 | `((0, -1), (-1, 0))` | [4, 10] | True |
| aca_91 | [8, 15] | 23 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_92 | [8, 15] | 23 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_93 | [8, 15] | 23 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_94 | [8, 15] | 23 | `((-1, -3), (0, -1))` | [6, 4] | False |
| aca_95 | [8, 11] | 19 | `((-1, -1), (1, 0))` | [4, 10] | True |
| aca_96 | [8, 15] | 23 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_97 | [7, 12] | 19 | `((0, -1), (1, -5))` | [6, 4] | True |
| aca_98 | [7, 12] | 19 | `((0, -1), (-1, -9))` | [6, 4] | True |
| aca_99 | [7, 12] | 19 | `((0, -1), (-1, 1))` | [4, 10] | True |
| aca_100 | [9, 11] | 20 | `((-2, -1), (-1, 0))` | [4, 10] | True |
| aca_101 | [8, 17] | 25 | `((-1, -3), (0, -1))` | [6, 4] | False |
| aca_102 | [8, 17] | 25 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_103 | [8, 17] | 25 | `((1, -1), (0, -1))` | [6, 4] | False |
| aca_104 | [8, 17] | 25 | `((-1, -1), (0, -1))` | [6, 4] | False |
| aca_105 | [10, 11] | 21 | `((-1, -1), (-1, 0))` | [4, 10] | True |
| aca_106 | [10, 11] | 21 | `((-7, -1), (-1, 0))` | [4, 10] | True |
| aca_107 | [9, 13] | 22 | `((0, -1), (-1, -8))` | [6, 4] | True |
| aca_108 | [11, 13] | 24 | `((0, -1), (1, -10))` | [10, 6] | True |
| aca_109 | [11, 12] | 23 | `((0, -1), (-1, -7))` | [8, 4] | True |
| aca_110 | [9, 13] | 22 | `((0, -1), (1, -6))` | [6, 4] | True |
| aca_111 | [11, 13] | 24 | `((0, -1), (1, -4))` | [10, 6] | True |
| aca_112 | [11, 13] | 24 | `((0, -1), (1, -6))` | [10, 6] | True |
| aca_113 | [9, 14] | 23 | `((0, -1), (-1, -9))` | [6, 4] | True |
| aca_114 | [9, 14] | 23 | `((0, -1), (1, -7))` | [6, 4] | True |
| aca_115 | [6, 7] | 13 | `((1, -1), (3, -4))` | [6, 2] | False |
| aca_116 | [7, 7] | 14 | `((-2, -1), (-1, 0))` | [4, 4] | False |
| aca_117 | [7, 7] | 14 | `((0, -1), (-1, 0))` | [4, 4] | False |
| aca_118 | [7, 8] | 15 | `((0, -1), (1, -3))` | [6, 4] | False |
| aca_119 | [7, 9] | 16 | `((0, -1), (1, -4))` | [6, 4] | False |
| aca_120 | [7, 8] | 15 | `((0, -1), (1, -1))` | [6, 4] | True |
| aca_121 | [7, 8] | 15 | `((0, -1), (-1, -5))` | [6, 4] | True |
| aca_122 | [7, 9] | 16 | `((0, -1), (-1, -6))` | [6, 4] | True |
| aca_123 | [7, 10] | 17 | `((0, -1), (-1, -7))` | [6, 4] | True |
